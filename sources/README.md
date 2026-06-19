# sources — read Lark / 飞书 + Notion

The **information-intake** layer: how this machine reads from Lark/飞书 and Notion, processes
the content into clean Markdown, and hands it to whatever project needs it. Consolidated here
from `plantcore/sources/` so it travels with the dotfiles and reproduces on a fresh machine.

> Full prose walkthrough + troubleshooting: [`../docs/sources.md`](../docs/sources.md).

## The one rule: credentials live in the Keychain

Nothing here stores a secret. All three creds live in the macOS Keychain (service
`codex-api-keys`), managed by the bundled [`api_keys`](../bin/api_keys) tool:

| Key | Used by |
|-----|---------|
| `NOTION_API_KEY` | Notion MCP / REST |
| `LARK_APP_ID`    | Lark MCP / REST |
| `LARK_APP_SECRET`| Lark MCP / REST |

```bash
api_keys set      # store them (prompts; saved to Keychain)
api_keys test     # verify Notion + Lark auth against live endpoints
api_keys export   # print shell `export …` lines (used by the MCP wiring below)
```

## Three read paths

### 1. MCP tools — `mcp__notion__*` / `mcp__lark__*` (global, always-on)
[`mcp.json`](./mcp.json) defines two stdio servers whose launch command **self-runs
`api_keys export`** to pull the creds from the Keychain, then execs the real MCP server
(`@notionhq/notion-mcp-server`, `@larksuiteoapi/lark-mcp`). No secret is ever written to disk.

`install.sh` registers both at **user scope** (`claude mcp add-json -s user`), so they load in
**every** Claude Code session — no per-repo setup. (`mcp.json` is also a valid drop-in project
`.mcp.json`: copy it into a repo and approve via `enabledMcpjsonServers` if you ever want
repo-scoped instead of global.)

### 2. Notion local-cache extractor — `notion-extract` (primary on this machine)
[`notion/extract_local.py`](./notion/extract_local.py) (symlinked to `~/bin/notion-extract`)
reads the running Notion desktop app's local SQLite cache
(`~/Library/Application Support/Notion/notion.db`). **No API, no integration-sharing** — if a
page is visible in your Notion app, it's reachable. Read-only (snapshots the DB via `.backup`
first), filters trashed/archived, two-sweep (full subtree of each matching page + a
`_mentions-elsewhere.md` for scattered hits), and stamps every file as **reference-only**.

```bash
notion-extract "伊芙丽,YFL" /path/to/<project>/intake/notion
```

Why it exists: the Notion **API** only sees pages **shared with the integration**; the local
cache sees everything in your desktop app. Lark's desktop cache is encrypted, so there is **no
local-cache path for Lark** — Lark is API/MCP only.

### 3. Direct REST — `eval "$(api_keys export)"` + curl
For ad-hoc probes without the MCP layer: export the creds into the env and hit the Notion /
Lark REST APIs directly. `api_keys test` already does exactly this for an auth smoke-test.

## Subagents

Two Claude Code subagents (symlinked to `~/.claude/agents/`) wrap ACCESS → PROCESS → EMIT:

- [`notion/agent.md`](./notion/agent.md) — `@notion-agent`
- [`lark/agent.md`](./lark/agent.md) — `@lark-agent`

Both use `disallowedTools: [Edit, NotebookEdit]` so they **inherit the MCP tools** (a bare
`tools:` allowlist would exclude all `mcp__*` tools and break them). They read-only by default,
normalize to Markdown, attach provenance frontmatter, and write **reference-only** output to
the path the task names.

## Provenance — every emitted file is stamped

```yaml
---
source: notion | lark
notion_url / notion_block_id / lark_ref: <id-or-url>
title: <title>
fetched_at: <YYYY-MM-DD>
status: reference-only
---
> ⚠️ Reference only — NOT ground truth.
```

Intake is **reference-only**: agent-written, may be stale/contradictory. Ground truth is
user-written and lives wherever the consuming project keeps it; agents may read it, never write
it.

## Layout

```
sources/
├── README.md            # this file
├── mcp.json             # notion + lark server defs (Keychain self-fetch; drop-in .mcp.json too)
├── notion/
│   ├── agent.md         # @notion-agent  → ~/.claude/agents/notion-agent.md
│   └── extract_local.py # local-cache extractor → ~/bin/notion-extract
└── lark/
    └── agent.md         # @lark-agent    → ~/.claude/agents/lark-agent.md
```
