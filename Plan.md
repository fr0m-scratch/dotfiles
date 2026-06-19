# Plan

_Source of truth. Keep this the most up-to-date document at all times._
_Last updated: 2026-06-19_

## Current Objective
Maintain the reusable dotfiles repo (public, `dotfiles`). Latest: consolidated the
Lark/飞书 + Notion read setup from `plantcore/sources` into `sources/`.

## TODO
- (none)

## In Progress
- (none)

## Done
- [x] **Information intake (`sources/`)** — captured how this machine reads Lark + Notion:
      canonical `sources/mcp.json` (Keychain self-fetch, secret-free), `@notion-agent` +
      `@lark-agent` subagents, the Notion local-cache extractor (`notion-extract`), plus
      `docs/sources.md`. `install.sh` links the agents/extractor and registers Notion + Lark
      MCP at **user scope** (global, always-on); verified ✔ Connected via `claude mcp list`.
- [x] Pushed to GitHub: https://github.com/fr0m-scratch/dotfiles (public, main, 46 files). Switched origin SSH→HTTPS after an SSH key was missing.
- [x] Added README "How I actually work (the philosophy)" section (later moved out — see below).

## Requirement Change Log (continued)
- 2026-06-09: Revert the inline README philosophy section; instead create a standalone "说明"
  in TWO versions (English `docs/how-i-work.md` + 中文 `docs/how-i-work.zh.md`), link both from
  the README, and give `cheatsheet.html` a clear entry/link in the main README. — DONE: README
  restored to the reference version + a "Start here · 从这里开始" table linking both 说明 versions
  and the cheatsheet; both docs cross-link each other + the cheatsheet.
- [x] Generate docs (keybindings / window-management / claude-code / shell-terminal) + README via a 5-agent workflow; all 205-315 lines, verified accurate, no leakage.
- [x] `cheatsheet.html` via generate→critique→refine workflow; self-contained, one-accent-per-card, balanced HTML, no horizontal scroll.
- [x] Converted cheatsheet from HLF **Bold** (dark) to HLF **Print** (warm paper #f3ede1 / near-black ink / oxblood #b81c1c accent) per user correction — token swap only, tokens-pure, footer relabeled.
- [x] Excluded AOL.md from the public repo (.gitignore) — personal build log embeds local username path.
- [x] Inventory the machine's personalization (10-agent sweep).
- [x] Lock package manifest; copy + sanitize 35 config files into `dotfiles/`.
- [x] Templatize sensitive data: email (`gitconfig.template`), IP-guard country list
      (externalized to `~/.config/claude-ip-guard/blocked-countries.sh`, empty default),
      home paths (`$HOME` / `__HOME__`).
- [x] Strip the dangerous `claude` alias; guard the `wave()` quota pane behind `$WAVE_STATUS_CMD`.
- [x] Generate iTerm2 Tokyo Night Dynamic Profile from the WaveTerm palette.
- [x] Write `install.sh` (TUI; claude-only/full profiles; parallel brew prefetch;
      backup+symlink; render templates; SIP/Accessibility/Karabiner guidance). Verified
      via `bash -n`, `shellcheck`, and dry-runs of both profiles.
- [x] `.gitignore`, `Brewfile`, governance docs.

## Open Questions / Decisions
- Repo visibility: **Public** (user choice 2026-06-09) → all sensitive data templatized.
- Repo name: **dotfiles**. Lives at `~/theOne/dotfiles` (gitignored from the theOne repo).
- Install method: **symlink + backup** for shell-expandable files; **render (copy+sed)** for
  Karabiner (`__HOME__`) and `.gitconfig` (name/email). Decided for reproducibility.

## Requirement Change Log
- 2026-06-09: Initial requirement — package the machine's personalization into a reusable,
  self-installing public dotfiles repo with a TUI installer, detailed docs, and an
  HTML cheatsheet; build via multiple workflows; push to GitHub.
- 2026-06-09: Correction — the cheatsheet must be HLF **Print** style (not Bold); keep only Print.
- 2026-06-19: New requirement — read how Lark/飞书 + Notion are accessed in `plantcore/sources`
  and consolidate it ALL into dotfiles; then update every relevant doc, commit, and push.
  User chose **global, always-on** MCP scope (vs per-repo template). — DONE: added `sources/`
  (mcp.json + agents + extractor), wired `install.sh` (link_sources + register_sources_mcp via
  `claude mcp add-json -s user`), registered + health-checked both servers live (✔ Connected),
  and updated README + `docs/sources.md` + cheatsheet (new card 07) + Plan. No secrets committed.
- 2026-06-19: Follow-up — surface the Lark + Notion intake in the two reader-facing docs:
  `docs/claude-code.md` (new §6 + install bullet) and `docs/how-i-work.md` + `.zh.md` (a
  parallel "Claude reads from where my work lives / 直接读我工作真正所在的地方" section).
  Then push.
