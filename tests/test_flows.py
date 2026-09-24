"""Exercise the ledger transitions without pretending to invoke remote models."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "babel.py"


class TaskFlows(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)

    def run_cli(self, *arguments, success=True):
        env = dict(os.environ, BABEL_HOME=str(self.root))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments], env=env,
            text=True, encoding="utf-8", capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def create(self, task_id, kind="routine-code", scope="src/example.py", *flags):
        self.run_cli(
            "new", task_id, "--objective", "Implement the specified example",
            "--kind", kind, "--scope", scope,
            "--acceptance", "The example behaves as specified", *flags,
        )

    def packet(self, task_id):
        return json.loads(self.run_cli("brief", task_id).stdout)

    def test_gpt_independent_high_judgment(self):
        self.create("gpt-solo", "architecture", "docs/design.md", "--high-judgment")
        self.run_cli("claim", "gpt-solo", "--model", "deepseek", success=False)
        self.run_cli("claim", "gpt-solo", "--model", "gpt")
        (self.root / "docs").mkdir()
        (self.root / "docs/design.md").write_text("Decision and rationale", encoding="utf-8")
        self.run_cli("note", "gpt-solo", "--model", "gpt", "--summary", "Selected boundary",
                     "--changed", "docs/design.md", "--evidence", "Inspected output")
        self.run_cli("complete", "gpt-solo", "--model", "gpt",
                     "--summary", "Decision recorded", "--evidence", "File exists and was read")
        self.assertEqual(self.packet("gpt-solo")["status"], "done")

    def test_secondary_independent_work(self):
        self.create("secondary-solo")
        self.assertEqual(json.loads(self.run_cli("route", "--kind", "routine-code").stdout)["model"], "deepseek")
        self.run_cli("claim", "secondary-solo", "--model", "deepseek")
        (self.root / "src").mkdir()
        (self.root / "src/example.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.run_cli("note", "secondary-solo", "--model", "deepseek", "--summary", "Added value",
                     "--changed", "src/example.py", "--evidence", "Read file: VALUE = 1")
        self.run_cli("complete", "secondary-solo", "--model", "deepseek",
                     "--summary", "Example complete", "--evidence", "Read file: VALUE = 1")
        self.assertEqual(self.packet("secondary-solo")["status"], "done")

    def test_gpt_delegates_then_resumes_same_file(self):
        self.create("shared-edit", "visual-tool")
        self.assertEqual(json.loads(self.run_cli("route", "--kind", "visual-tool").stdout)["model"], "mimo")
        self.run_cli("claim", "shared-edit", "--model", "gpt")
        (self.root / "src").mkdir()
        file = self.root / "src/example.py"
        file.write_text("# GPT specification\n", encoding="utf-8")
        self.run_cli("note", "shared-edit", "--model", "gpt", "--summary", "Defined interface",
                     "--changed", "src/example.py", "--evidence", "File inspected", "--next", "Add implementation")
        self.run_cli("handoff", "shared-edit", "--model", "gpt", "--to", "mimo",
                     "--summary", "Interface exists", "--why", "Bounded implementation",
                     "--evidence", "src/example.py contains interface", "--next", "Add implementation")
        self.run_cli("claim", "shared-edit", "--model", "mimo")
        file.write_text(file.read_text(encoding="utf-8") + "VALUE = 1\n", encoding="utf-8")
        self.run_cli("note", "shared-edit", "--model", "mimo", "--summary", "Implemented value",
                     "--changed", "src/example.py", "--evidence", "File contains VALUE = 1")
        self.run_cli("handoff", "shared-edit", "--model", "mimo", "--to", "gpt",
                     "--summary", "Implementation ready", "--why", "Integration review",
                     "--evidence", "File contains VALUE = 1", "--next", "Review and close")
        self.run_cli("claim", "shared-edit", "--model", "gpt")
        self.assertIn("GPT specification\nVALUE = 1", file.read_text(encoding="utf-8"))
        self.run_cli("complete", "shared-edit", "--model", "gpt",
                     "--summary", "Integrated", "--evidence", "Read both file changes")
        packet = self.packet("shared-edit")
        self.assertEqual(packet["transfers"], 2)
        self.assertEqual([e["action"] for e in packet["events"]].count("handoff"), 2)

    def test_secondary_escalates_to_gpt_with_evidence(self):
        self.create("needs-judgment")
        self.run_cli("claim", "needs-judgment", "--model", "deepseek")
        self.run_cli("escalate", "needs-judgment", "--model", "deepseek",
                     "--summary", "Two valid designs conflict", "--why", "Needs API decision",
                     "--evidence", "Both options pass local check", "--next", "Choose public behavior")
        self.run_cli("claim", "needs-judgment", "--model", "mimo", success=False)
        self.run_cli("claim", "needs-judgment", "--model", "gpt")
        self.assertEqual(self.packet("needs-judgment")["events"][-2]["why"], "Needs API decision")

    def test_parallel_scope_conflict_and_transfer_limit(self):
        self.create("first-task", scope="src")
        self.create("second-task", scope="src/example.py")
        self.run_cli("claim", "first-task", "--model", "deepseek")
        self.run_cli("claim", "second-task", "--model", "mimo", success=False)
        self.run_cli("escalate", "first-task", "--model", "deepseek",
                     "--summary", "Needs review", "--why", "Uncertain result",
                     "--evidence", "Check inconclusive", "--next", "Review")
        self.run_cli("claim", "second-task", "--model", "mimo", success=False)
        self.run_cli("claim", "first-task", "--model", "gpt")
        self.run_cli("handoff", "first-task", "--model", "gpt", "--to", "mimo",
                     "--summary", "Narrow follow-up", "--why", "Implementation",
                     "--evidence", "Decision recorded", "--next", "Implement", success=False)
        self.run_cli("complete", "first-task", "--model", "gpt",
                     "--summary", "Resolved", "--evidence", "Reviewed scope")
        self.run_cli("claim", "second-task", "--model", "mimo")

    def test_delegated_task_requires_gpt_completion(self):
        self.create("delegated-task")
        self.run_cli("claim", "delegated-task", "--model", "gpt")
        self.run_cli("handoff", "delegated-task", "--model", "gpt", "--to", "deepseek",
                     "--summary", "Ready", "--why", "Bounded work",
                     "--evidence", "Acceptance defined", "--next", "Implement")
        self.run_cli("claim", "delegated-task", "--model", "deepseek")
        self.run_cli("complete", "delegated-task", "--model", "deepseek",
                     "--summary", "Implemented", "--evidence", "Checked", success=False)
        self.run_cli("handoff", "delegated-task", "--model", "deepseek", "--to", "gpt",
                     "--summary", "Ready", "--why", "Integration review",
                     "--evidence", "Checked", "--next", "Review")
        self.run_cli("claim", "delegated-task", "--model", "gpt")
        self.run_cli("handoff", "delegated-task", "--model", "gpt", "--to", "mimo",
                     "--summary", "Try again", "--why", "More work",
                     "--evidence", "Check", "--next", "Retry", success=False)

    @unittest.skipUnless(os.name == "nt", "Windows path alias rule")
    def test_windows_case_aliases_conflict(self):
        self.create("case-one", scope="src/Example.py")
        self.create("case-two", scope="src/example.py")
        self.run_cli("claim", "case-one", "--model", "deepseek")
        self.run_cli("note", "case-one", "--model", "deepseek", "--summary", "Changed file",
                     "--changed", "src/example.py", "--evidence", "File inspected")
        self.run_cli("claim", "case-two", "--model", "mimo", success=False)


if __name__ == "__main__":
    unittest.main()
