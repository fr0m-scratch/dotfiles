# Information intake — read Lark / 飞书 + Notion

How this machine reads from **Lark/飞书** and **Notion**, turns the content into clean
Markdown, and hands it to whatever project needs it. The reusable pieces live in
[`sources/`](../sources/) (agents, the canonical MCP defs, the Notion local-cache extractor);
credentials live in the macOS Keychain via [`bin/api_keys`](../bin/api_keys). Nothing here
stores a secret.

> Quick map of the `sources/` directory: [`sources/README.md`](../sources/README.md).

---

## 1. The model

```
  Notion app ─┐                        ┌── @notion-agent ─┐
 (desktop+API) ├─ Keychain (api_keys) ─┤   notion-extract  ├─▶ clean Markdown (reference-only)
   Lark app  ─┘   NOTION_API_KEY        └── @lark-agent ───┘     → the consuming project
 (Open Platform)  LARK_APP_ID/SECRET
```

- **Credentials** never touch the repo. They live in the macOS Keychain (service
  `codex-api-keys`), managed by `api_keys`.
- **Access** happens three ways (below): MCP tools, the Notion local-cache extractor, or
  direct REST.
- **Output** is always **reference-only** Markdown with provenance frontmatter — never treated
  as ground truth.

---

## 2. Credentials (do this once)

```bash
api_keys set      # prompts; stores keys in the macOS Keychain
api_keys test     # smoke-tests Notion + Lark auth against live endpoints
api_keys list     # show which keys are saved (names only)
```

| Key | What it is | Where to get it |
|-----|-----------|-----------------|
| `NOTION_API_KEY`  | Notion internal-integration secret (`ntn_…`) | <https://www.notion.so/my-integrations> → New integration |
| `LARK_APP_ID`     | Lark self-built app ID     | Lark Developer Console → your app → Credentials |
| `LARK_APP_SECRET` | Lark self-built app secret | same page |

For Lark, the app must be **published** and granted the read scopes you need
(`im:message:readonly`, `docx:document:readonly`, `wiki:wiki:readonly`,
`drive:drive:readonly`, `bitable:app:readonly`, …). For the Notion **API**, each page/database
must be **shared with the integration** — which is exactly why the local-cache extractor
(below) is the primary Notion path on this machine.

---

## 3. Three read paths

### Path 1 — MCP tools (`mcp__notion__*` / `mcp__lark__*`), global & always-on

[`sources/mcp.json`](../sources/mcp.json) defines two stdio servers. Their launch command
**self-runs `api_keys export`** to pull creds from the Keychain, then execs the real MCP
server:

```jsonc
"notion": { "command": "bash", "args": ["-c",
  "eval \"$(\"$HOME/bin/api_keys\" export)\" && export NOTION_TOKEN=\"$NOTION_API_KEY\" && exec npx -y @notionhq/notion-mcp-server"] }
"lark":   { "command": "bash", "args": ["-c",
  "eval \"$(\"$HOME/bin/api_keys\" export)\" && exec npx -y @larksuiteoapi/lark-mcp mcp -a \"$LARK_APP_ID\" -s \"$LARK_APP_SECRET\" -d https://open.larksuite.com"] }
```

`install.sh` registers both at **user scope**, so they load in **every** Claude Code session —
no per-repo setup:

```bash
claude mcp add-json notion "$(jq -c .mcpServers.notion sources/mcp.json)" -s user
claude mcp add-json lark   "$(jq -c .mcpServers.lark   sources/mcp.json)" -s user
claude mcp list     # both should report ✔ Connected
```

This writes to `~/.claude.json`'s top-level `mcpServers` (machine-local, **not** committed —
the repo ships only the secret-free definition + the install step).

> Repo-scoped alternative: `sources/mcp.json` is also a valid drop-in project `.mcp.json` —
> copy it into a repo and approve via `.claude/settings.json` `"enabledMcpjsonServers":
> ["notion","lark"]` if you ever want it scoped to one repo instead of global.

### Path 2 — Notion local-cache extractor (`notion-extract`), primary on this machine

[`sources/notion/extract_local.py`](../sources/notion/extract_local.py) (symlinked to
`~/bin/notion-extract`) reads the running Notion desktop app's local SQLite cache
(`~/Library/Application Support/Notion/notion.db`). **No API, no integration-sharing** — if a
page is visible in your Notion app, it's reachable.

```bash
notion-extract "伊芙丽,YFL" /path/to/<project>/intake/notion
```

- **Read-only:** snapshots the DB via `.backup` first; filters trashed/archived.
- **Two sweeps (deduped):** the full subtree of each matching page, plus a
  `_mentions-elsewhere.md` collecting scattered hits inside other pages.
- **Stamped:** every file gets provenance frontmatter + a "NOT ground truth" banner.

Lark's desktop cache is **encrypted**, so there is no local-cache path for Lark — Lark is
API/MCP only.

### Path 3 — direct REST (`eval "$(api_keys export)"` + curl)

For ad-hoc probes without the MCP layer, export the creds and hit the REST APIs directly.
`api_keys test` already does this for an auth smoke-test (Notion `/v1/users/me`, Lark
`tenant_access_token`).

---

## 4. Subagents

Two Claude Code subagents (symlinked to `~/.claude/agents/`, so `@notion-agent` / `@lark-agent`
work in every session) wrap **ACCESS → PROCESS → EMIT**:

- [`sources/notion/agent.md`](../sources/notion/agent.md)
- [`sources/lark/agent.md`](../sources/lark/agent.md)

Both declare `disallowedTools: [Edit, NotebookEdit]` so they **inherit the MCP tools** — a bare
`tools:` allowlist would exclude every `mcp__*` tool and break them. They are read-only by
default, normalize content to Markdown, attach provenance, and write the result to the path the
task names (one object → one file).

---

## 5. Provenance — every emitted file is stamped

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

**Intake is reference-only:** agent-written, possibly stale/contradictory. Ground truth is
user-written and lives wherever the consuming project keeps it; agents may *read* it, never
*write* it.

---

## 6. Reproduce on a fresh machine

`./install.sh` (either profile) does it automatically:

1. links `@notion-agent` / `@lark-agent` into `~/.claude/agents/`,
2. links `notion-extract` onto `~/bin`,
3. registers the Notion + Lark MCP servers at user scope (`claude mcp add-json … -s user`).

Then the only manual step is the secrets: `api_keys set` → `api_keys test`.

---

## 7. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `claude mcp list` shows notion/lark **not connected** | Run `api_keys test`. If a key is missing, `api_keys set`. The server self-fetches at launch, so a fresh session picks up new keys. |
| Notion MCP returns nothing for a page you can see | The API only sees pages **shared with the integration**. Either share the page, or use `notion-extract` (local cache, no sharing). |
| Lark calls denied (non-zero `code`) | The app lacks the scope or its version isn't **published**. Add the read scope in the Developer Console and release a version. |
| `notion-extract` finds nothing | The Notion **desktop app** must have synced the pages locally; open them once in the app, then re-run. |
| Wrong Lark host | International = `open.larksuite.com`; China/Feishu = `open.feishu.cn`. Edit the `-d` host in `sources/mcp.json`. |

---

## 8. Security

- **No secrets in the repo, ever.** Creds live only in the Keychain; the MCP wiring fetches
  them at launch. Emitted Markdown must never contain a token.
- **Read-first.** Write-back *to* Notion/Lark is opt-in and must be explicitly requested.
- `~/.claude.json` (where the global MCP registration lands) is machine-local and intentionally
  **not** committed — the repo carries only the reproducible definition + install step.
