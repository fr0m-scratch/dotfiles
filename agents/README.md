# Agent configuration source

This tree is authored configuration, not application state.

- `shared/skills/*` is the portable skill source intended for `$HOME/.agents/skills/*`.
- `codex/config.toml` is a safe base layer. Merge it with live config; never overwrite auth, project trust, hook trust hashes, state, or user-selected model settings.
- `codex/hooks.json` must be merged by event/handler identity because Otty and other app-owned handlers may already exist. A non-empty target is not evidence that these hooks were migrated.
- `codex/hooks/*` is intended for `$HOME/.codex/hooks/`; `codex/rules/*` for `$HOME/.codex/rules/` after explicit review.
- Company skills, agents, and MCP definitions remain project-scoped under `~/plantcore/.agents/` and `~/plantcore/.codex/`.

Deploy immutable skills and hook scripts as symlinks when practical. Generate mutable config from reviewed fragments and a private machine overlay. Never import or commit sessions, transcripts, memories, credentials, tokens, account files, databases, logs, caches, plugin downloads, trust decisions, or local permission history.

Run every skill through `skill-creator/scripts/quick_validate.py`, parse TOML/JSON strictly, syntax-check bundled scripts, then test hook decisions with fixtures before touching live configuration.
