# Principal

> Owner: the user. Authored by Claude at init; thereafter only the user edits this
> (Claude edits only when explicitly told — the guard hook asks the user to confirm).

## End Goal
A reusable, public **dotfiles** repo that reproduces this Mac's personalization on a
fresh machine with one TUI command: Claude Code (config + skills + hooks + CLI),
window management (yabai/skhd/Karabiner), terminals (WaveTerm + iTerm2), shell
(zsh + Powerlevel10k), keybindings, and the `~/bin` tools (`api_keys`, `wave_focus`,
`wm_*`). `install.sh` downloads what's missing (parallel), configures it, and guides
the user through the macOS grants that cannot be scripted.

## Key Restrictions
- **Public repo → no secrets, ever.** Real email, the IP-guard country list, and any
  machine-specific paths are templatized to placeholders filled at install time.
- API keys stay in the macOS Keychain (managed by `api_keys`); never committed.
- Do **not** ship: the WaveTerm `widgets.json` / `wave-status.sh` status bar; the
  `claude --dangerously-skip-permissions` alias; `~/.local/bin` tools; `.claude.json`;
  `settings.local.json`.
- Installer is idempotent, backs up anything it overwrites, and never claims to
  automate SIP / Accessibility / Karabiner-driver grants — it detects and instructs.
- No Claude co-author trailer on any commit (enforced by the fr0m guard hook).

## Scope / Non-goals
- Not a general cross-distro dotfiles framework; macOS (Apple Silicon) only.
- Does not migrate Keychain secrets, browser state, or app data — config only.
