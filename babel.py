"""Small, provider-neutral task ledger for model handoffs in this repository."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
import uuid


ROOT = Path(os.environ.get("BABEL_HOME", Path(__file__).resolve().parent)).resolve()
STORE = ROOT / ".babel"
TASKS = STORE / "tasks"
MODELS = ("gpt", "deepseek", "mimo")
KINDS = (
    "architecture", "complex-debug", "routine-code", "long-context",
    "visual-tool", "research", "docs",
)


def fail(message: str) -> None:
    raise ValueError(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def task_path(task_id: str) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", task_id):
        fail("Task ID must be 2–64 lowercase letters, digits, or hyphens, starting with a letter")
    return TASKS / f"{task_id}.json"


def scope_path(value: str) -> str:
    value = value.replace("\\", "/").rstrip("/") or "."
    if value == ".":
        return value
    parts = value.split("/")
    if (value.startswith("/") or ":" in parts[0] or
            any(part in ("", ".", "..") or any(char in part for char in "*?[]")
                for part in parts) or
            parts[0] in (".babel", ".git")):
        fail(f"Invalid repository-relative scope: {value}")
    return "/".join(parts)


def overlaps(left: str, right: str) -> bool:
    if os.name == "nt":
        left, right = left.casefold(), right.casefold()
    return (left == "." or right == "." or left == right or
            left.startswith(right + "/") or right.startswith(left + "/"))


def within(path: str, scope: str) -> bool:
    if os.name == "nt":
        path, scope = path.casefold(), scope.casefold()
    return scope == "." or path == scope or path.startswith(scope + "/")


@contextmanager
def locked():
    STORE.mkdir(parents=True, exist_ok=True)
    lock = STORE / ".lock"
    deadline = time.monotonic() + 5
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                fail("Task ledger is locked; inspect .babel/.lock before retrying")
            time.sleep(0.05)
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def read(task_id: str) -> dict:
    path = task_path(task_id)
    if not path.exists():
        fail(f"Task not found: {task_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def write(task: dict) -> None:
    TASKS.mkdir(parents=True, exist_ok=True)
    path = task_path(task["id"])
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def event(task: dict, action: str, model: str, summary: str, **details: object) -> None:
    task["events"].append({
        "at": now(), "action": action, "model": model, "summary": summary, **details,
    })


def recommendation(kind: str, high_judgment: bool, verifiable: bool) -> tuple[str, str]:
    if high_judgment or not verifiable or kind in ("architecture", "complex-debug"):
        return "gpt", "Needs difficult judgment, or lacks a reliable verifier"
    if kind == "visual-tool":
        return "mimo", "Bounded visual or tool-rich work with an observable result"
    return "deepseek", "Bounded, verifiable work suited to efficient long-input/code execution"


def ensure_owner(task: dict, model: str) -> None:
    if task["status"] != "active" or task["owner"] != model:
        fail(f"Task is not actively owned by {model}")


def new(args: argparse.Namespace) -> None:
    scopes = list(dict.fromkeys(scope_path(item) for item in args.scope))
    if not args.objective.strip() or not args.acceptance:
        fail("Objective and at least one acceptance check are required")
    path = task_path(args.task_id)
    with locked():
        if path.exists():
            fail(f"Task already exists: {args.task_id}")
        task = {
            "version": 1, "id": args.task_id, "objective": args.objective,
            "kind": args.kind, "high_judgment": args.high_judgment,
            "verifiable": not args.unverifiable, "scope": scopes,
            "constraints": args.constraint, "acceptance": args.acceptance,
            "references": args.reference, "status": "ready", "owner": None,
            "target": None, "transfers": 0, "delegated": False, "events": [],
        }
        event(task, "new", "user", "Task packet created")
        write(task)
    model, why = recommendation(task["kind"], task["high_judgment"], task["verifiable"])
    print(f"Created {args.task_id}; recommended owner: {model} ({why})")


def route(args: argparse.Namespace) -> None:
    model, why = recommendation(args.kind, args.high_judgment, not args.unverifiable)
    print(json.dumps({"model": model, "reason": why}, ensure_ascii=False))


def claim(args: argparse.Namespace) -> None:
    with locked():
        task = read(args.task_id)
        if task["status"] not in ("ready", "awaiting"):
            fail(f"Task cannot be claimed from status {task['status']}")
        if task["target"] and task["target"] != args.model:
            fail(f"Task is awaiting {task['target']}")
        if args.model != "gpt" and (task["high_judgment"] or not task["verifiable"] or
                                    task["kind"] in ("architecture", "complex-debug")):
            fail("This task requires GPT judgment; narrow it into a new verifiable task first")
        for path in TASKS.glob("*.json") if TASKS.exists() else []:
            if path.stem == task["id"]:
                continue
            other = json.loads(path.read_text(encoding="utf-8"))
            if other["status"] in ("active", "awaiting") and any(
                overlaps(a, b) for a in task["scope"] for b in other["scope"]
            ):
                fail(f"Scope conflicts with active task {other['id']}")
        task.update(status="active", owner=args.model, target=None)
        event(task, "claim", args.model, "Ownership claimed")
        write(task)
    print(f"{args.model} claimed {args.task_id}")


def note(args: argparse.Namespace) -> None:
    with locked():
        task = read(args.task_id)
        ensure_owner(task, args.model)
        changed = [scope_path(value) for value in args.changed]
        if any(not any(within(path, scope) for scope in task["scope"]) for path in changed):
            fail("Changed file is outside claimed scope")
        event(task, "note", args.model, args.summary, changed=changed,
              evidence=args.evidence, next=args.next)
        write(task)
    print(f"Recorded progress on {args.task_id}")


def transfer(args: argparse.Namespace, escalation: bool = False) -> None:
    target = "gpt" if escalation else args.to
    if not all(value.strip() for value in (args.summary, args.why, args.evidence, args.next)):
        fail("Transfer needs a nonempty summary, reason, evidence, and next action")
    with locked():
        task = read(args.task_id)
        ensure_owner(task, args.model)
        if target == args.model:
            fail("Transfer target must differ from current owner")
        if args.model != "gpt" and target != "gpt":
            fail("Secondary models transfer only to GPT")
        if task["transfers"] >= 2:
            fail("Transfer limit reached; GPT must complete or create a new scoped task")
        if args.model == "gpt" and target != "gpt":
            if task["transfers"]:
                fail("GPT received this task from another model; finish it or create a new scoped task")
            if task["delegated"]:
                fail("Task has already been delegated; create a new scoped task")
            if task["high_judgment"] or not task["verifiable"] or task["kind"] in ("architecture", "complex-debug"):
                fail("Narrow this judgment task into a new verifiable task before delegation")
            task["delegated"] = True
        task.update(status="awaiting", owner=None, target=target,
                    transfers=task["transfers"] + 1)
        event(task, "escalate" if escalation else "handoff", args.model, args.summary,
              to=target, why=args.why, evidence=args.evidence, next=args.next)
        write(task)
    print(f"{args.task_id} awaits {target}")


def complete(args: argparse.Namespace) -> None:
    if not args.summary.strip() or not args.evidence.strip():
        fail("Completion needs a nonempty summary and verification evidence")
    with locked():
        task = read(args.task_id)
        ensure_owner(task, args.model)
        if task["delegated"] and args.model != "gpt":
            fail("GPT must review and complete a GPT-delegated task")
        task.update(status="done", owner=None, target=None)
        event(task, "complete", args.model, args.summary, evidence=args.evidence)
        write(task)
    print(f"Completed {args.task_id}")


def brief(args: argparse.Namespace) -> None:
    print(json.dumps(read(args.task_id), ensure_ascii=False, indent=2))


def list_tasks(_args: argparse.Namespace) -> None:
    rows = []
    for path in sorted(TASKS.glob("*.json")) if TASKS.exists() else []:
        task = json.loads(path.read_text(encoding="utf-8"))
        rows.append({key: task[key] for key in ("id", "status", "owner", "target", "scope")})
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    n = commands.add_parser("new")
    n.add_argument("task_id")
    n.add_argument("--objective", required=True)
    n.add_argument("--kind", choices=KINDS, required=True)
    n.add_argument("--scope", action="append", required=True)
    n.add_argument("--acceptance", action="append", required=True)
    n.add_argument("--constraint", action="append", default=[])
    n.add_argument("--reference", action="append", default=[])
    n.add_argument("--high-judgment", action="store_true")
    n.add_argument("--unverifiable", action="store_true")
    n.set_defaults(func=new)
    r = commands.add_parser("route")
    r.add_argument("--kind", choices=KINDS, required=True)
    r.add_argument("--high-judgment", action="store_true")
    r.add_argument("--unverifiable", action="store_true")
    r.set_defaults(func=route)
    c = commands.add_parser("claim")
    c.add_argument("task_id")
    c.add_argument("--model", choices=MODELS, required=True)
    c.set_defaults(func=claim)
    no = commands.add_parser("note")
    no.add_argument("task_id")
    no.add_argument("--model", choices=MODELS, required=True)
    no.add_argument("--summary", required=True)
    no.add_argument("--changed", action="append", default=[])
    no.add_argument("--evidence", action="append", default=[])
    no.add_argument("--next", action="append", default=[])
    no.set_defaults(func=note)
    for name in ("handoff", "escalate"):
        h = commands.add_parser(name)
        h.add_argument("task_id")
        h.add_argument("--model", choices=MODELS, required=True)
        if name == "handoff":
            h.add_argument("--to", choices=MODELS, required=True)
        h.add_argument("--summary", required=True)
        h.add_argument("--why", required=True)
        h.add_argument("--evidence", required=True)
        h.add_argument("--next", required=True)
        h.set_defaults(func=(lambda args, esc=name == "escalate": transfer(args, esc)))
    done = commands.add_parser("complete")
    done.add_argument("task_id")
    done.add_argument("--model", choices=MODELS, required=True)
    done.add_argument("--summary", required=True)
    done.add_argument("--evidence", required=True)
    done.set_defaults(func=complete)
    b = commands.add_parser("brief")
    b.add_argument("task_id")
    b.set_defaults(func=brief)
    commands.add_parser("list").set_defaults(func=list_tasks)
    return p


def main() -> int:
    try:
        args = parser().parse_args()
        args.func(args)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
