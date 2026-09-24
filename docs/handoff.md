# Durable task packet

`babel.py` stores each task in `.babel/tasks/TASK_ID.json`. These files are the durable handoff record. The command-line output is a readable view of the same state. Keep task IDs short and descriptive.

## Start

```text
python babel.py new task-id --objective "..." --kind routine-code --scope src/module.py --acceptance "..." --constraint "..." --reference docs/spec.md
python babel.py route --kind routine-code
python babel.py claim task-id --model deepseek
python babel.py brief task-id
```

`--kind` is one of `architecture`, `complex-debug`, `routine-code`, `long-context`, `visual-tool`, `research`, or `docs`. Add `--high-judgment` or `--unverifiable` when appropriate. A path scope is relative to this repository; `.` claims the whole tree. Parallel claims with overlapping scopes fail. A model ID is `gpt`, `deepseek`, or `mimo`.

## Work and transfer

```text
python babel.py note task-id --model deepseek --summary "What changed and why" --changed src/module.py --evidence "pytest tests/test_module.py: 4 passed" --next "Check edge case X"
python babel.py handoff task-id --model deepseek --to gpt --summary "Current result" --why "Needs cross-module decision" --evidence "Failure details" --next "Choose API boundary"
python babel.py escalate task-id --model mimo --summary "Current result" --why "Tool returned ambiguous error" --evidence "Tool name and error" --next "Decide recovery"
python babel.py claim task-id --model gpt
python babel.py complete task-id --model gpt --summary "Delivered result" --evidence "Verification command and result"
```

Every transfer needs a summary, reason, evidence, and next action. A packet also carries the objective, constraints, acceptance checks, references, owned paths, events, and current target. The sender records failed approaches and unresolved uncertainty in `note` or transfer evidence. The receiver checks files and reruns the relevant verification if it modifies the result. `brief` is a pointer, not a replacement for reading actual files.

The `handoff` command only transfers ownership. It does **not** start another model session or send a message. Give the receiving session the task ID and this repository path through the host's supported mechanism. The receiving model claims the packet before editing. `escalate` is a one-way transfer to GPT. The transfer limit prevents bouncing the same task indefinitely.

If a process crashes while holding `.babel/.lock`, inspect the PID stored there and remove the lock only after confirming that process has ended. Packet files are replaced atomically so a reader sees a complete old or new version.
