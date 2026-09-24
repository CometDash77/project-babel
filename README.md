# Project Babel

An initial shared workspace for GPT, DeepSeek V4.1 Flash, and MiMo V2.6 Pro RL. Start with [AGENTS.md](AGENTS.md), then [model policy](docs/model-policy.md) and [task handoff](docs/handoff.md).

The repository was empty at setup. It provides task routing, durable state, scoped ownership, handoff, and escalation; model execution and tool calls remain with the host running each model. No API keys or provider adapters are assumed.

Run `python -m unittest discover -s tests` to verify the local coordination contract.
See [initial validation](docs/validation.md) for the tested flows and the limits of this host.
