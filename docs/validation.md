# Initial deployment check — 2026-09-24

The target directory was confirmed by the user as the intended project and was empty. There was no Git repository, AGENTS.md, model route, prompt, tool adapter, task state, or existing multi-agent mechanism to preserve. The four requested primary sources were read before the setup was designed. Both downloaded PDFs matched the SHA-256 digests shown on their Hugging Face file pages.

## Local flows

Run `python -m unittest discover -s tests -v` from the repository root. The checks create disposable workspaces and use the actual `babel.py` commands to exercise:

1. GPT claims and completes a high-judgment task; a secondary claim is rejected.
2. DeepSeek claims and completes a bounded task independently.
3. GPT records a file decision, hands the same task/file to MiMo, and receives it back for integration.
4. A secondary model escalates uncertainty with evidence; only GPT can claim the result.
5. Parallel claims to overlapping paths are rejected, including Windows case aliases and a packet awaiting transfer.
6. A GPT-delegated task requires GPT completion; repeated transfer is rejected.

These are **ledger and file-workflow checks using model labels**, not live inference by DeepSeek or MiMo. This host had no configured DeepSeek/MiMo credential or local executable at deployment time. GPT work in the current Codex session supplied the initial design and implementation. A live cross-provider run still requires a host that exposes those models and its native tool schemas. Do not report the simulated flows as model-quality evidence.

The ledger enforces path claims only for users of this repository and this checkout. It cannot authenticate a model identity, enforce filesystem permissions, guarantee another host loads AGENTS.md/Skills, or prevent edits from a client that bypasses it. Provider-specific context caches and tool semantics remain host responsibilities. For separate worktrees, use Git review/merge to detect conflicts before integration.
