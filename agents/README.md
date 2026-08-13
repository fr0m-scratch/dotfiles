# Agent configuration source

This tree is authored configuration, not application state.

- `shared/skills/*` is the portable skill source intended for `$HOME/.agents/skills/*`.
- Skill discovery differs per runtime and `$HOME/.agents/skills/` is **not** universal (verified 2026-08-13): Claude Code reads `$HOME/.claude/skills/`, Kimi Code reads `$HOME/.kimi-code/skills/` then `$HOME/.agents/skills/` (brand dir wins on name collision), and Codex 0.147.0 reads **only** `$CODEX_HOME/skills` (`$HOME/.codex/skills`) — its binary contains no reference to `agents/skills`. Consequence: everything currently under `$HOME/.agents/skills/` is invisible to Codex unless it is also linked into `$HOME/.codex/skills/`.
- `codex/skills/*` and `kimi/skills/*` hold runtime-dialect skills — same doctrine, different fan-out primitive — for cases where one portable file would have to give a runtime contradictory instructions. Keep a skill in `shared/skills/` whenever it is genuinely runtime-neutral.
- `codex/config.toml` is a safe base layer. Merge it with live config; never overwrite auth, project trust, hook trust hashes, state, or user-selected model settings.
- `codex/hooks.json` must be merged by event/handler identity because Otty and other app-owned handlers may already exist. A non-empty target is not evidence that these hooks were migrated.
- `codex/hooks/*` is intended for `$HOME/.codex/hooks/`; `codex/rules/*` for `$HOME/.codex/rules/` after explicit review.
- `kimi/AGENTS.md` is intended for `$HOME/.kimi-code/AGENTS.md` (global Kimi-specific instructions); `kimi/hooks/*` for `$HOME/.kimi-code/hooks/`.
- `kimi/config.toml` is a safe base layer published as `$HOME/.kimi-code/config.base.toml`. Merge its `[[hooks]]` entries and `default_permission_mode` into the live config; never overwrite providers, models, or OAuth state. Kimi Code reads `$HOME/.agents/skills/` natively, so the shared skills need no Kimi-specific copy.
- Company skills, agents, and MCP definitions remain project-scoped under `~/plantcore/.agents/` and `~/plantcore/.codex/`.

Deploy immutable skills and hook scripts as symlinks when practical. Generate mutable config from reviewed fragments and a private machine overlay. Never import or commit sessions, transcripts, memories, credentials, tokens, account files, databases, logs, caches, plugin downloads, trust decisions, or local permission history.

Run every skill through `skill-creator/scripts/quick_validate.py`, parse TOML/JSON strictly, syntax-check bundled scripts, then test hook decisions with fixtures before touching live configuration.
