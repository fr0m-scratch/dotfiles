# Plan

_Source of truth. Keep this the most up-to-date document at all times._
_Last updated: 2026-06-09_

## Current Objective
Ship the reusable dotfiles repo (public, name `dotfiles`) and push to the user's GitHub.

## TODO
- [ ] Push to GitHub (`gh repo create dotfiles --public`) — needs user to run `gh auth login` first.

## In Progress
- [ ] Final commit, then push.

## Done
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
