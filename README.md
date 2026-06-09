# dotfiles · one-shot Mac setup

A **public, reusable macOS dotfiles repo** that reproduces the author's Mac
personalization on a fresh machine with **one TUI command**. It installs and wires up
Claude Code (config, skills, hooks, CLI), a tiling window manager
(yabai / skhd / Karabiner-Elements), terminals (WaveTerm + iTerm2), the shell
(zsh + Powerlevel10k), keybindings, and a handful of `~/bin` helper tools — downloading
whatever is missing in parallel, backing up anything it would overwrite, and walking you
through the macOS security grants that *cannot* be scripted.

> 中文：这是一个公开、可复用的 macOS dotfiles 仓库。一条命令 `./install.sh` 打开终端菜单，
> 即可在新 Mac 上重建作者的全套环境。仓库里**不含任何密钥**，敏感信息（邮箱、IP 地区名单、
> 路径）都已模板化，安装时再填入。Apple Silicon / macOS only。

---

## Quick start

```bash
git clone <repo-url> dotfiles
cd dotfiles
./install.sh
```

Running with no arguments opens the interactive TUI menu:

```
  ┌────────────────────────────────────────────┐
  │   dotfiles · one-shot Mac setup              │
  └────────────────────────────────────────────┘
    1) Claude Code only   — config, skills, hooks, CLI, bun
    2) Full setup         — Claude + window mgmt + terminals + shell + bin
    3) Dry run (full)     — show every action, change nothing
    q) quit
```

You can also skip the menu with flags:

| Flag | Effect |
|------|--------|
| `--full` | Install everything; prompt only for the manual macOS grants. |
| `--claude-only` | Install the Claude Code bits only. |
| `--dry-run` | Print every action, change nothing (safe to inspect first). |
| `--yes`, `-y` | Assume "yes" to prompts (non-interactive). **Pair with a profile flag** — `--yes` alone still shows the menu. |
| `--help`, `-h` | Print usage and exit. |

```bash
./install.sh --full --yes        # unattended full install
./install.sh --claude-only       # just Claude Code
./install.sh --dry-run           # preview the full install
```

The installer is **macOS-only** (it exits on anything else) and **idempotent** — re-running
it re-uses existing symlinks and skips packages that are already present.

---

## What's included

> 中文：下表按领域列出仓库内容，并链接到 `docs/` 下的详细说明与可在浏览器打开的速查表。

| Area | What it is | Docs |
|------|-----------|------|
| **Claude Code** | `claude/settings.json`, bundled skills (`apple-frontend`, `apple-sales-doc`, `fr0m`, `new-skill`), hooks (`fr0m-guard.py`, `fr0m-rules.py`, `aol-append.sh`), slash commands (`/check`, `/fr0m`), the `blocks` output-style + theme, an IP-geofence guard, plus auto-install of the Claude Code CLI and `bun` (runs the statusline). | [`docs/claude-code.md`](docs/claude-code.md) |
| **Window management** | yabai tiling WM (`wm/yabairc`) + skhd hotkey daemon (`wm/skhdrc`) + Karabiner-Elements key remaps (`wm/karabiner.json`, e.g. Caps Lock → Wave, Option-based workspace switching). | [`docs/window-management.md`](docs/window-management.md) |
| **Terminals** | WaveTerm settings + term themes (`terminal/waveterm/`) and an iTerm2 Tokyo Night dynamic profile (`terminal/iterm2/DynamicProfiles/`). | [`docs/shell-and-terminal.md`](docs/shell-and-terminal.md) |
| **Shell** | zsh config (`shell/zshrc`), Powerlevel10k prompt (`shell/p10k.zsh`, cloned to `~/powerlevel10k`), and a templatized `~/.gitconfig`. | [`docs/shell-and-terminal.md`](docs/shell-and-terminal.md) |
| **Keybindings** | The full hotkey map across skhd, Karabiner, and the terminals. | [`docs/keybindings.md`](docs/keybindings.md) |
| **`~/bin` tools** | `api_keys` (Keychain key manager), `wave_focus`, and the `wm_*` window helpers (`wm_chat`, `wm_firefox`, `wm_lark`, `wm_notion`, `wm_arrange_chat`, `wm_space_minimize`, `wm_space_restore`). Linked in **both** profiles. | [`docs/window-management.md`](docs/window-management.md) |

A printable, browser-openable shortcut & command reference lives at
[`cheatsheet.html`](cheatsheet.html).

> **Skills vs plugins.** The four skills above are *bundled* (symlinked from this repo into
> `~/.claude/skills/`). `claude-hud` and `frontend-design` are *plugins* declared in
> `settings.json`; they fetch from their marketplaces on first `claude` launch (or via
> `/plugin`) and are not stored in this repo.

---

## What's deliberately excluded (and why)

> 中文：以下内容**故意不放进仓库**——要么涉及隐私/机器特定状态，要么有危险性。

| Excluded | Why |
|----------|-----|
| WaveTerm `widgets.json` / `wave-status.sh` status bar | Highly machine-specific IDE layout; not portable. |
| The `claude --dangerously-skip-permissions` alias | Dangerous to ship as a default — users should opt in knowingly. |
| `~/.local/bin` tools | Personal, machine-specific scripts outside this repo's scope. |
| `.claude.json` | Holds session/account state, not reusable config. |
| `settings.local.json` | Per-machine local overrides (git-ignored). |

Secrets, the real IP-guard country list, and `.dotfiles-backup/` are also git-ignored
(see `.gitignore`).

---

## How the install works

> 中文：安装器的核心是「软链接 + 备份 + 模板渲染」，全程可干跑预览。

- **Symlink, with backup.** Config files are symlinked from the repo into place
  (e.g. `claude/settings.json → ~/.claude/settings.json`). Before overwriting anything,
  the existing file is moved into a **timestamped backup** at
  `~/.dotfiles-backup/<YYYYMMDD-HHMMSS>/`. A path that's already our symlink is left alone.
- **Template rendering.** A few files are *copied* (not linked) with placeholders
  substituted: `__HOME__` → your home dir, `__GIT_NAME__` and `__GIT_EMAIL__` →
  your git identity. This covers `shell/gitconfig.template` and `wm/karabiner.json`.
  For the gitconfig, the installer pre-fills from your existing global git config and
  lets you confirm/override the name and email interactively.
- **Parallel brew prefetch.** Only *missing* dependencies are queued; the installer then
  fires off concurrent `brew fetch` downloads (a spinner shows progress) before running
  the actual `brew install`, which reuses the cached bottles. Homebrew itself is installed
  if absent. The Claude Code CLI (not on Homebrew) is fetched from `https://claude.ai/install.sh`,
  and Powerlevel10k is `git clone`d to `~/powerlevel10k`.
- **Idempotent.** Re-running detects existing symlinks, present binaries/apps, and an
  existing `~/powerlevel10k`, and skips them.
- **Dry-run.** `--dry-run` (menu option 3) prints every action — links, renders, brew
  commands — and changes nothing, so you can audit it first.

See [`Brewfile`](Brewfile) for the exact dependency list
(`bun`, `node`, `jq`, `git`, `yabai`, `skhd`, plus the casks `wave`, `iterm2`,
`karabiner-elements`, `font-meslo-lg-nerd-font`).

---

## Security & privacy

> 中文：仓库公开，所以**绝不含密钥**；API key 全部放在 macOS 钥匙串里。

- **No secrets in the repo, ever.** API keys live in the **macOS Keychain**, managed by the
  bundled `api_keys` tool (`api_keys help`). Nothing key-related is committed.
- **IP geofence is OFF by default.** The Claude IP-guard scripts ship without a country list.
  The real list is externalized; to enable it, copy the example into place:
  ```bash
  cp claude/scripts/blocked-countries.example.sh \
     ~/.config/claude-ip-guard/blocked-countries.sh
  ```
  The repo git-ignores the live `claude/scripts/blocked-countries.sh`.
- **Templatized identity & paths.** Email, git name, and home-relative paths are placeholders
  filled in at install time (`__HOME__`, `__GIT_NAME__`, `__GIT_EMAIL__`).

---

## Manual macOS grants you must do

> 中文：以下授权 macOS 不允许脚本代办，安装器只能检测并提示，你需手动完成。

The full profile starts yabai + skhd and then prints a guide. Three things require your hands:

1. **Accessibility** — System Settings → Privacy & Security → Accessibility → enable
   `yabai`, `skhd`, `Karabiner-Elements`, and your terminal.
2. **Karabiner driver** — on first launch, approve its system extension and Input Monitoring
   under Privacy & Security.
3. **yabai scripting addition** — partially disable SIP from Recovery
   (`csrutil enable --without-fs --without-debug --without-nvram`, or `csrutil disable`) and
   add a passwordless `sudoers` entry for `yabai --load-sa`.

The installer detects when SIP is still fully enabled and warns you. Full step-by-step
instructions are in [`docs/window-management.md`](docs/window-management.md).

---

## Repo layout

```
dotfiles/
├── install.sh                  # the TUI installer
├── Brewfile                    # all Homebrew dependencies
├── cheatsheet.html             # printable shortcuts & commands reference
├── README.md
├── Principal.md  Plan.md  AOL.md  Errors.md   # fr0m governance
├── .gitignore
├── bin/                        # ~/bin tools (linked in both profiles)
│   ├── api_keys                # Keychain API-key manager
│   ├── wave_focus
│   └── wm_*                    # window helpers (chat/firefox/lark/notion/space_*)
├── claude/                     # Claude Code config → ~/.claude/
│   ├── settings.json
│   ├── skills/                 # apple-frontend, apple-sales-doc, fr0m, new-skill
│   ├── hooks/                  # fr0m-guard.py, fr0m-rules.py, aol-append.sh
│   ├── scripts/                # IP-guard lib + blocked-countries.example.sh
│   ├── commands/               # /check, /fr0m
│   ├── output-styles/blocks.md
│   └── themes/blocks.json
├── shell/                      # zshrc, p10k.zsh, gitconfig.template
├── terminal/
│   ├── waveterm/               # settings.json, termthemes.json
│   └── iterm2/DynamicProfiles/ # tokyo-night.json
├── wm/                         # yabairc, skhdrc, karabiner.json
└── docs/
    ├── claude-code.md
    ├── window-management.md
    ├── keybindings.md
    └── shell-and-terminal.md
```

---

## Governance

This repo is governed under **fr0m**: see [`Principal.md`](Principal.md) (end goal &
restrictions), [`Plan.md`](Plan.md), [`AOL.md`](AOL.md) (append-only log), and
[`Errors.md`](Errors.md). Per the Principal, the public repo carries no secrets and commits
include no Claude co-author trailer.
