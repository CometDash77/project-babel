# Project Babel agent rules

This directory is the shared workspace for GPT, DeepSeek V4.1 Flash, and MiMo V2.6 Pro RL. The user's current request and the host's system/developer instructions always take precedence over this file.

1. Before work, read `docs/model-policy.md` and the relevant task packet with `python babel.py brief TASK_ID`. Read the files named in the packet and inspect the current workspace; a conversation summary is never the sole source of task state.
2. Claim the task before editing: `python babel.py claim TASK_ID --model MODEL`. Edit only the claimed `scope`. Coordinate another scope through a separate task. Never treat an advisory scope as permission to override user or host restrictions.
3. Keep the packet current after meaningful changes with `note`. Record what changed, why, file paths, verification results, and remaining work. Preserve uncertainty and failed attempts. Do not compress away an unresolved constraint or failure.
4. Use only tools actually exposed by the current host. Follow each tool's exact schema and inspect its result or error before the next dependent step. Do not paste a tool call as plain text and assume it ran. An unsupported or malformed tool call is a failure to report, not permission to guess.
5. Do not assume context windows, tool schemas, system prompts, Skills, or AGENTS loading are identical across providers. At a model switch, give the receiver the task ID, packet, relevant files, constraints, prior decisions, current state, and next action. The receiver must re-read the packet and local rules.
6. Delegate bounded, verifiable work to a secondary model. GPT owns ambiguous architecture, cross-module tradeoffs, sensitive changes, final integration, and uncertain or conflicting results. A secondary model escalates to GPT with evidence when it cannot verify a result, encounters a capability/tool boundary, or needs a material judgment. Do not repeatedly transfer the same task between models.
7. Before completion, verify the requested behavior with the smallest meaningful check and report the command/result or direct observation. A passing test does not alone prove scope, quality, or absence of unintended changes. Mark a task complete only after recording remaining limitations.

Use the same delivery shape across models: result, changed files, verification evidence, and unresolved limits. Say explicitly when a result is inferred or a real model/tool run was unavailable.

See `docs/handoff.md` for the packet and transition contract. This repository does not contain model API credentials or a provider tool adapter; the current host executes model and tool calls.
