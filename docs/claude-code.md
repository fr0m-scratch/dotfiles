# Claude Code Personalization

这份文档讲清楚本仓库对 **Claude Code** 做的所有个性化：界面/行为设置、五个自定义 skill、`fr0m` 项目治理系统、IP 地理围栏，以及三个自定义命令。每一项都说明 **它是什么 / 怎么配置的 / 怎么用**。

All the Claude Code customization in this repo lives under `claude/` and is symlinked into `~/.claude/` by `./install.sh`. Nothing here requires editing Claude Code's own source — everything is driven by `settings.json`, skill folders, hooks, and slash commands.

---

## 0. Install (TL;DR)

设置通过 `./install.sh` 安装，两种 profile 都会装 Claude Code 部分。

```bash
./install.sh --claude-only   # only the Claude Code setup (config, skills, hooks, CLI, bun)
./install.sh                 # interactive TUI — pick "Claude Code only" or "full"
./install.sh --yes --claude-only   # non-interactive
```

What the installer does for Claude Code (`link_claude` + `collect_claude_deps`):

- Installs the **`claude` CLI** if missing (`curl -fsSL https://claude.ai/install.sh | bash`).
- Installs dependencies via Homebrew: **`bun`** (for the statusline), **`node`**, **`jq`**, and warns if **`python3`** is missing (needed by the guard/IP hooks — `xcode-select --install`).
- Symlinks every piece into `~/.claude/`:
  - `claude/settings.json` → `~/.claude/settings.json`
  - `claude/skills/*/` → `~/.claude/skills/*/`
  - `claude/hooks/*` → `~/.claude/hooks/*`
  - `claude/scripts/*` → `~/.claude/scripts/*` (the `*.example.sh` files are **skipped** — they are templates only)
  - `claude/commands/*` → `~/.claude/commands/*`
  - `claude/output-styles/*` → `~/.claude/output-styles/*`
  - `claude/themes/*` → `~/.claude/themes/*`
- **Plugins** (`claude-hud`, `frontend-design`) are *not* downloaded by the installer — they are declared in `settings.json` and fetched from their marketplaces on the first `claude` launch (see §1).
- **Information intake — Lark + Notion** (`link_sources` + `register_sources_mcp`, both profiles): symlinks the two source subagents (`@notion-agent`, `@lark-agent`) into `~/.claude/agents/` and the Notion local-cache reader into `~/bin/notion-extract`, then registers the Notion + Lark MCP servers at **user scope** so they load in every session. See §6 and [`sources.md`](sources.md).

---

## 1. Settings overview

文件：`claude/settings.json` → `~/.claude/settings.json`。这是整个个性化的中枢，连接了主题、输出风格、努力等级、顾问模型、TUI 模式、状态栏和插件。

| Setting | Value | What it does |
|---|---|---|
| `theme` | `custom:blocks` | Loads the custom theme defined in `claude/themes/blocks.json`. |
| `tui` | `fullscreen` | Runs the Claude Code TUI in fullscreen (alternate-screen) mode. |
| `effortLevel` | `high` | Default reasoning effort for the model. |
| `advisorModel` | `opus` | Model used by the `advisor` tool (the "stronger reviewer" consulted mid-task). |
| `skipDangerousModePermissionPrompt` | `true` | Suppresses the dangerous-mode permission prompt. |
| `skipWorkflowUsageWarning` | `true` | Suppresses the workflow usage warning. |
| `statusLine` | command | Renders the bottom status line via **claude-hud** (run with `bun`). |
| `enabledPlugins` | claude-hud, frontend-design | Plugins auto-installed from marketplaces. |
| `permissions.allow` | (list) | Pre-approved tool calls so they don't prompt (pytest, pip3, `python3 -m json.tool`, `grep`, a few NVIDIA `WebFetch` domains, etc.). |

### Theme — `custom:blocks`

`claude/themes/blocks.json` is a thin override on the built-in `dark` base — it only re-colors the user-message bubble so your prompts stand out as distinct blocks:

```json
{
  "name": "Blocks",
  "base": "dark",
  "overrides": {
    "userMessageBackground": "#24283b",
    "userMessageBackgroundHover": "#2f3449"
  }
}
```

### Output style — "Blocks" (the trailing `---` rule)

`claude/output-styles/blocks.md` is a **formatting-only** output style (`keep-coding-instructions: true`, so it does not change how Claude scopes/codes/verifies). Its single job: end **every** reply with a markdown horizontal rule on its own line, so each turn reads as a visually-separated block:

```
---
```

The rule must appear only at the very end of the message, nowhere else. To activate it, run `/output-style Blocks` (or pick it in `/config`). Combined with the Blocks theme, every exchange becomes a clearly-bounded block in the transcript.

### Statusline — claude-hud via bun

`statusLine` is a `command` type. The one-liner:

1. Reads the real terminal width with `stty size` and exports a slightly-narrowed `COLUMNS` so the HUD fits.
2. Finds the **highest installed version** of the `claude-hud` plugin under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/*/claude-hud/*/` (sorts the semver dirs and takes the latest).
3. Executes that version's `src/index.ts` with **`bun`** (`$HOME/.bun/bin/bun --env-file /dev/null`).

So the statusline is a TypeScript program shipped by the claude-hud plugin, run by the Bun runtime the installer puts in place. You can configure what it shows with the `/claude-hud:setup` and `/claude-hud:configure` skills.

### Plugins & marketplaces (how they auto-install)

```json
"enabledPlugins": {
  "claude-hud@claude-hud": true,
  "frontend-design@claude-plugins-official": true
},
"extraKnownMarketplaces": {
  "claude-plugins-official": { "source": { "source": "github", "repo": "anthropics/claude-plugins-official" } },
  "claude-hud":              { "source": { "source": "github", "repo": "jarrodwatts/claude-hud" } }
}
```

`extraKnownMarketplaces` registers two GitHub marketplaces; `enabledPlugins` flags two plugins (`claude-hud` for the statusline, `frontend-design` for UI work) as enabled. On the **first `claude` launch** after install, Claude Code resolves these from their marketplaces and downloads them into `~/.claude/plugins/cache/`. You can also manage them manually with `/plugin`. The installer deliberately does **not** vendor the plugins — only the declaration is in this repo.

---

## 2. Skills

五个自定义 skill 放在 `claude/skills/<name>/SKILL.md`，安装后是全局的（每个项目都能用）。一个 skill = 一个带 `SKILL.md` 的文件夹；frontmatter 的 `description` 是触发器，正文是给模型的指令。用 `/<name>` 显式调用，或在描述匹配时由模型自动加载（除非禁用了自动调用）。

| Skill | What it does | How to invoke |
|---|---|---|
| **apple-frontend** | Builds a clean Apple-HIG-style web frontend — light, system-font, hairline borders, single accent, master-detail app shell, restrained data display, explicitly **NO AI-slop** (no gradients/glow/neon/purple-gold/emoji). Ships verbatim design tokens, a canonical app-shell structure, a11y rules, and a headless-Chrome self-verify step. | `/apple-frontend`, or auto-loads when you ask for an "Apple-style / not AI-style" product UI. |
| **apple-sales-doc** | Generates a polished, Apple-clean **one-page sales/pitch document** as a single self-contained HTML file with real product screenshots embedded as base64 (print-to-PDF friendly). Pairs with apple-frontend (screenshot that UI into this doc). | `/apple-sales-doc`, or auto-loads on "sales doc / pitch / one-pager / 销售文档". |
| **fr0m** | Initializes/refreshes a project's **governance docs** (Principal/Plan/AOL/Errors.md), ensures git, runs a clarifying Q&A, and produces an agreed Plan.md. See §3. | `/fr0m <goal + restrictions>` — **user-only** (`disable-model-invocation: true`; never auto-fires). |
| **new-skill** | Scaffolds a new reusable skill from a description — picks a kebab name, writes a strong trigger `description` + imperative body, creates `~/.claude/skills/<name>/SKILL.md`, and confirms registration. | `/new-skill <description>`, or auto-loads on "make this a skill / write a new skill". |
| **latex** | Compiles a **very formal / official technical document** (ICD, specification, RFC, 技术规范) to a **print-grade PDF via LaTeX** (pandoc → xelatex/xeCJK, full 中文) — numbered sections + TOC + RFC-2119, Songti 宋体 serif + Menlo mono, **zero decoration**. Bundles `build_pdf.sh`; self-verifies the render (PDF → PNG → Read). Pairs with `/check` — use `/latex` when the deliverable must be a formal **PDF**. | `/latex <topic / source>`, or auto-loads on "formal PDF / spec / ICD / 正式文档". |

> The two `apple-*` skills share the same anti-AI-slop design tokens and the same "screenshot the real UI with headless Chrome, then Read the PNG to self-verify" workflow — apple-frontend builds the UI, apple-sales-doc embeds screenshots of it into a pitch.

---

## 3. The `fr0m` governance system

`fr0m` 是一套**项目治理**机制：每个项目先用 `/fr0m` 建立四份文档 + git + 常驻规则，之后由两个 hook 机械地强制执行。SKILL.md 只在 `/fr0m` 运行的那一回合生效；真正让治理"活下去"的是 hook。

### The four docs (created in the project's cwd)

| File | Purpose | Who edits it |
|---|---|---|
| **Principal.md** | End Goal + Key Restrictions (+ scope/non-goals). The constitution. | Claude authors it at first init; thereafter **user-owned** — Claude only edits when explicitly told (the guard hook asks the user to confirm any edit). |
| **Plan.md** | Detailed plan + TODO. The **single source of truth**, kept current at all times. | Claude — every new requirement must be folded in immediately. |
| **AOL.md** | Append-Only Log of everything done/modified. | Claude — **append only**, via the helper. Never edit past entries. |
| **Errors.md** | Every error encountered and how it was resolved. | Claude — append as errors happen. |

### The guard hook — `claude/hooks/fr0m-guard.py` (PreToolUse)

Wired on `matcher: "Bash|Edit|Write|MultiEdit"`. It runs on **every** such tool call in **every** project (it is fast and **fail-open** — any parse problem just defers to normal flow). It enforces three things mechanically:

1. **No Claude co-author commits → `deny`.** If a `git commit` command contains `Co-Authored-By: …claude`, `Generated with …Claude`, `Claude Code`, or the robot emoji (🤖), the commit is denied with a message to remove those lines and retry.
2. **AOL.md is append-only → `deny`.** Blocks Bash truncation/rewrite of `AOL.md` (`> AOL.md`, `sed -i`, `truncate`, `dd/cp/mv/install`, `tee` without `-a`) and blocks `Edit`/`Write`/`MultiEdit` on an **existing** `AOL.md`. First-time creation is allowed; appending via the helper (or `>>`) is allowed.
3. **Principal.md is user-owned → `ask`.** Any `Edit`/`Write`/`MultiEdit` on an **existing** `Principal.md` triggers a confirmation prompt to the user (initial creation by `/fr0m` is fine).

### The rules hook — `claude/hooks/fr0m-rules.py` (UserPromptSubmit)

Fires on every prompt, but is **silent unless the cwd contains `Principal.md`** (i.e. the directory is governed). When active, it injects standing rules as `additionalContext` so governance survives long after the `/fr0m` turn:

- Plan.md is the single source of truth — re-read before acting; fold every new requirement in immediately.
- After each substantive action, append one timestamped AOL entry via the helper.
- Log every error + resolution to Errors.md.
- Don't edit Principal.md unless told (guard will ask to confirm).
- Never add Claude as a git co-author; keep the folder under git.
- If a new requirement is unclear, ask first, then reflect the answer in Plan.md before implementing.

### The AOL helper — `claude/hooks/aol-append.sh`

The **only sanctioned write path** for `AOL.md`. It creates the file with a header if absent, then appends a timestamped entry:

```bash
bash ~/.claude/hooks/aol-append.sh "<dir-containing-AOL.md>" "<message>"
```

### How to bootstrap a project

```text
/fr0m Build a CLI that does X. Restrictions: no network, Python 3.11 only, must stay under 500 LOC.
```

`/fr0m` will: ensure git (`git init` if needed) → read any existing docs (reconcile, don't clobber) → ask clarifying questions if anything is underspecified → write/reconcile the four docs → state the standing rules back → record the init in AOL via the helper. Re-run `/fr0m` whenever you restate the goal or change restrictions (editing Principal.md will trigger the guard's confirm prompt — expected, not a failure).

---

## 4. The IP geofence (`claude-ip-guard`)

一个**可选**的地理围栏：在会话启动和每次发消息前检查你的公网 IP 与归属国家。本仓库默认**关闭**（黑名单为空 `BLOCKED_COUNTRIES=()`）—— 此时它只**记录**位置、提醒新 IP，**从不**因为地区而拦截。

### Wiring

Two hooks in `settings.json`, both sourcing the shared library `claude/scripts/ip-guard-lib.sh`:

| Hook | Script | When | Strategy |
|---|---|---|---|
| `SessionStart` (`startup\|resume`) | `check-ip-on-start.sh` (timeout 15s) | New/resumed session | Full check on every session start. |
| `UserPromptSubmit` | `check-ip-on-prompt.sh` (timeout 15s) | Every prompt you send | Cheap: if IP unchanged and cache fresh (`RECHECK_INTERVAL=600s`), pass; otherwise full re-check. |

### What it checks (in `ip-guard-lib.sh`)

1. **Native connection only.** If `ANTHROPIC_BASE_URL` is set to a non-official URL (a third-party proxy), it skips all checks. It only runs for direct connections to `https://api.anthropic.com`.
2. **Direct reachability test** against the real Anthropic endpoint (no key needed) — distinguishes "network unreachable" from "reachable but region-blocked" (a `403` is a hard region block; `000`/timeout is unknown).
3. **Geo lookup** of your public IP — `ipinfo.io` primary, `ip-api.com` fallback — yielding country/region/city/org.
4. **Blocklist check** — `is_blocked` against `BLOCKED_COUNTRIES`. If your country is in the list (and the link is genuinely blocked), it **hard-blocks** (`exit 2`) with an "access restricted" message.
5. **New-IP history** — keeps a 30-day dedup history (`~/.cache/claude-ip-guard/ip_history.jsonl`). A brand-new IP triggers a tiered warning (`[提示]/[注意]/[警告]/[严重警告]` by how many distinct IPs appeared in 30 days) and a soft-block (`exit 2`) — re-send your message to continue. Known IPs just refresh the cache and pass.

Everything is **fail-safe**: any lookup failure passes you through. Caches/logs live under `~/.cache/claude-ip-guard/` (`ip_cache`, `ip_history.jsonl`, dated `ip-guard-*.log`).

### OFF by default — and how to enable it

The blocklist in this repo is empty, so the guard never blocks on geography — it only logs and warns on new IPs. The real country list is intentionally **not** in version control (privacy/政治敏感). To turn on geofencing, create a per-machine file:

```bash
mkdir -p ~/.config/claude-ip-guard
cp claude/scripts/blocked-countries.example.sh \
   ~/.config/claude-ip-guard/blocked-countries.sh
# then edit it, e.g.:
#   BLOCKED_COUNTRIES=("KP" "IR")
```

The library sources `${CLAUDE_IP_GUARD_COUNTRIES:-$HOME/.config/claude-ip-guard/blocked-countries.sh}` if it exists. Use ISO-3166 alpha-2 country codes. (The installer **skips** linking `*.example.sh`, so you create the real file yourself.)

---

## 5. Custom commands

自定义 slash 命令放在 `claude/commands/<name>.md`，安装后是全局命令。

### `/check` — render anything as HTML in WaveTerm

`claude/commands/check.md`. Renders the requested content (or, if no argument, the latest result in the conversation) as **one self-contained HTML file** and opens it in the current WaveTerm tab. The deliverable is **always HTML** — never markdown/plaintext.

```text
/check the benchmark table from above
```

It writes `./.check/<slug>.html` (inline `<style>`, UTF-8, no network/CDN deps, responsive, print-friendly) then opens it with `wsh web open "file://$(pwd)/.check/<slug>.html"`. Requires WaveTerm (`wsh`); on follow-up tweaks it edits the same file and re-opens. Allowed tools are restricted to `Write, Edit, Read, Bash(mkdir:*), Bash(wsh web open:*), Bash(wsh view:*)`.

### `/fr0m` — initialize/refresh project governance

`claude/commands/fr0m.md`. A thin entry point: it tells Claude to read `~/.claude/skills/fr0m/SKILL.md` and follow it exactly, passing your goal + restrictions as `$ARGUMENTS`. Run it **first, before any implementation**. See §3 for the full flow.

```text
/fr0m <project goal and key restrictions>
```

### `/latex` — compile a formal document to a print-grade PDF

`claude/commands/latex.md`. A thin entry point that tells Claude to read `~/.claude/skills/latex/SKILL.md` and follow it: write/refine the content as Markdown, compile it to a **formal PDF** with the bundled `build_pdf.sh` (pandoc → xelatex + xeCJK — numbered sections, TOC, RFC-2119 where normative, Songti 宋体 + Menlo, A4, header/footer, **no emoji / no flourish**, full 中文), then **verify the render** (PDF → PNG → Read) before delivering. For ICDs / specifications / 技术规范 / 正式文档. Pairs with `/check`: `/latex` when the deliverable must be a formal **PDF**, `/check` when it's a viewable **HTML** artifact. Needs `pandoc` + TinyTeX (`xelatex`) + `poppler` (the skill prints the install commands if a tool is missing).

```text
/latex the daemon ingestion ICD from above
```

---

## 6. Information intake — Lark / 飞书 + Notion

`sources/` 把「Claude 怎么读飞书 / Notion」整理成一套可复现的能力：两个子代理、一份 Keychain 自取钥匙的 MCP 配置、以及一个 Notion 本地缓存提取器。凭据只在 macOS Keychain 里（`api_keys`），仓库里**零密钥**。完整说明 + 排错见 [`sources.md`](sources.md)。

What the installer wires (`link_sources` + `register_sources_mcp`, run in **both** profiles):

- **Global MCP (always-on).** `sources/mcp.json` defines the Notion + Lark servers; each launch command self-runs `eval "$(api_keys export)"` to pull credentials from the Keychain, then execs the real MCP server (`@notionhq/notion-mcp-server`, `@larksuiteoapi/lark-mcp`). The installer registers both at **user scope** (`claude mcp add-json … -s user`), so `mcp__notion__*` / `mcp__lark__*` load in every session — verify with `claude mcp list` (both should report ✔ Connected). No secret is ever written to disk; the registration lands in machine-local `~/.claude.json`, which is **not** committed.
- **Subagents.** `sources/{notion,lark}/agent.md` → `~/.claude/agents/` as `@notion-agent` / `@lark-agent`. Each is read-first, normalizes content to Markdown, attaches provenance frontmatter, and writes **reference-only** output. They declare `disallowedTools: [Edit, NotebookEdit]` so they still **inherit** the `mcp__*` tools — a bare `tools:` allowlist would exclude every MCP tool and break them.
- **Notion local-cache reader.** `sources/notion/extract_local.py` → `~/bin/notion-extract`. Reads the desktop app's `notion.db` SQLite cache (read-only, via a `.backup` snapshot) — **no API, no page-sharing** needed. This is the primary Notion path on this machine; the Notion API only sees pages explicitly shared with the integration. (Lark's desktop cache is encrypted — Lark is API/MCP only.)

| Read path | Tool | When |
|---|---|---|
| Notion / Lark MCP | `mcp__notion__*` / `mcp__lark__*` | Default — global, always-on |
| Notion local cache | `notion-extract "<needles>" <out-dir>` | Pages not shared with the integration |
| Direct REST | `eval "$(api_keys export)"` + curl | Ad-hoc probes (`api_keys test`) |

**Credentials:** `api_keys set` stores `NOTION_API_KEY` / `LARK_APP_ID` / `LARK_APP_SECRET` in the Keychain; `api_keys test` smoke-tests both against live endpoints. Emitted Markdown is **reference-only** (provenance-stamped) — never treated as ground truth.

---
