# Model routing and boundaries

The routing unit is a *task*, not an entire conversation. `python babel.py route --kind KIND [--high-judgment] [--unverifiable]` provides a starting recommendation. A capable human or GPT can override it after recording why. The `claim` command enforces the non-negotiable boundary: high-judgment or unverifiable tasks cannot be claimed by a secondary model.

| Task signal | Initial owner | Reason and boundary |
| --- | --- | --- |
| Ambiguous architecture, competing requirements, security or migration judgment, cross-module integration, disputed evidence | GPT (`gpt-6-astra`) | Strongest judgment and long-context recovery. Keep final integration here. |
| Large repository reading, long input, bounded code or terminal work with executable checks | DeepSeek V4.1 Flash | 1M context, efficient input-heavy serving, strong coding-agent results. Recheck exact cited files and tests at handoff; long-context retrieval still has edge cases. |
| Bounded tool-rich workflow, visual inspection, UI implementation against a concrete target, ordinary code with clear acceptance checks | MiMo V2.6 Pro RL | Agent training across heterogeneous tools, code, visual and professional tasks. Verify tool responses and rendered outcomes; do not infer success from a tool call alone. |
| No clear verifier, unknown scope, or a secondary model's failed/contradictory attempt | GPT | Decide the next experiment or narrow the task before delegating. |

Secondary models may complete their own low-risk, verifiable tasks. GPT need not review every small change. For a GPT-delegated task, GPT reviews the packet, diff, and evidence before integration. For parallel work, give each agent a distinct path scope; overlapping active scopes are rejected by `babel.py`. Shared files require sequential ownership or separate worktrees managed by the host.

## Context and prompt order

Use the host's actual instruction hierarchy. Treat this file and `AGENTS.md` as repository guidance, never as a replacement for system/developer instructions. On every fresh session or model switch, read `AGENTS.md`, the task packet, and relevant local files. Load a Skill only when available and applicable in that host. Record Skill constraints that affect the task in the packet; do not assume another model has the same Skill installed. Preserve source paths, test output, decisions, failed attempts, and unresolved questions in packet events. Native context caching, compaction, and the advertised 1M context are optimizations, not durable cross-provider state.

## Tool contract

The host owns tool schemas and execution. Use the exact exposed name and argument structure; never invent a common JSON tool format. For each meaningful call, distinguish success, tool error, and uncertain result. Read returned values before dependent calls. Retry a transient error at most once with the same intended operation; do not blindly retry mutations. If a tool is unavailable, switch to an equivalent exposed tool only when semantics are clear, otherwise record the blocker and escalate. In handoffs, record *what* the tool established and where the evidence is, not raw unbounded transcripts or secrets.

## Effort and fallback

DeepSeek's report exposes `low`, `high`, and `max` reasoning effort (50/75/100); use `low` for simple checks, `high` for normal agent work, and `max` only for difficult bounded tasks. MiMo's report does not establish the same portable effort control, so do not send DeepSeek-specific effort parameters to MiMo. GPT effort is host-specific. If a provider/model is unavailable, keep the task unclaimed or return it to GPT; do not silently substitute a different model or spin through fallbacks. GPT may delegate once and receive the result once. If a secondary model starts independently and escalates, GPT finishes that task; any further delegation needs a newly scoped task. Further decomposition starts a new task with a new objective and scope.

## Source basis and limits

- [GPT-6 Astra](https://openai.com/index/gpt-6-astra/): complex software/professional judgment, task steering, context notes and retrieval in Codex. The latter is host-specific and cannot be assumed for another provider.
- [GPT-6 Sol and Luna](https://openai.com/index/introducing-gpt-6-sol-and-luna/): lower cost and improved coding/agent performance; the article also says Astra remains the strongest. This setup chooses Astra for the GPT judgment role; Sol/Luna are not silent substitutes.
- [DeepSeek V4.1 Flash technical report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf), §§1, 5.3.4–5.3.5, 6: efficient 1M input, strong code agents across harnesses, preliminary multi-agent gains, and acknowledged difficult-task/long-context retrieval limits.
- [MiMo V2.6 technical report](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Pro-RL/blob/main/MiMo_V2_6_technical_report.pdf), §§4.2–4.3, 5.3, 6: multi-harness agent training, code/visual/tool tasks, quality beyond binary tests, and trajectory/tool-error handling. The reported benchmark settings are not guarantees in this host.
