#!/usr/bin/env bash
# ============================================================================
#  dotfiles installer  ·  one TUI to download + configure a Mac
# ----------------------------------------------------------------------------
#  Two profiles:
#    claude  — just the Claude Code setup (config, skills, hooks, CLI, bun)
#    full    — everything: Claude + window mgmt + terminals + shell + bin
#
#  Usage:
#    ./install.sh                 # interactive TUI menu
#    ./install.sh --full          # install everything, prompt only for grants
#    ./install.sh --claude-only   # Claude Code bits only
#    ./install.sh --dry-run       # print every action, change nothing
#    ./install.sh --yes           # assume yes (non-interactive); pair w/ a profile
#
#  Safe by design: idempotent, backs up anything it would overwrite, and never
#  pretends to automate the macOS grants it cannot (SIP / Accessibility /
#  Karabiner driver) — it detects, instructs, and blocks on them.
# ============================================================================
set -uo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$HOME/.dotfiles-backup/$TS"

# ---- flags -----------------------------------------------------------------
DRY=0; PROFILE=""; ASSUME_YES=0
for a in "$@"; do case "$a" in
  --dry-run)      DRY=1 ;;
  --full)         PROFILE="full" ;;
  --claude-only)  PROFILE="claude" ;;
  --yes|-y)       ASSUME_YES=1 ;;
  --help|-h)      sed -n '2,22p' "$0"; exit 0 ;;
  *) echo "unknown flag: $a"; exit 2 ;;
esac; done

# ---- pretty ----------------------------------------------------------------
if [[ -t 1 ]]; then
  B=$'\e[1m'; DIM=$'\e[2m'; R=$'\e[0m'; ACC=$'\e[38;5;209m'
  GRN=$'\e[32m'; YEL=$'\e[33m'; RED=$'\e[31m'; BLU=$'\e[34m'
else B=""; DIM=""; R=""; ACC=""; GRN=""; YEL=""; RED=""; BLU=""; fi
step(){ printf '\n%s▸ %s%s\n' "$B$ACC" "$*" "$R"; }
ok(){   printf '  %s✓%s %s\n' "$GRN" "$R" "$*"; }
info(){ printf '  %s·%s %s\n' "$DIM" "$R" "$*"; }
warn(){ printf '  %s!%s %s\n' "$YEL" "$R" "$*"; }
err(){  printf '  %s✗%s %s\n' "$RED" "$R" "$*" >&2; }
run(){  if (( DRY )); then printf '  %s[dry]%s %s\n' "$DIM" "$R" "$*"; else eval "$*"; fi; }
ask(){  # ask "question" -> 0 yes / 1 no
  (( ASSUME_YES )) && return 0
  local r; printf '  %s? %s [y/N] %s' "$BLU" "$1" "$R"; read -r r </dev/tty || true
  [[ "$r" == [yY]* ]]; }

# ============================================================================
#  symlink / render helpers  (always back up, never clobber blindly)
# ============================================================================
backup(){ # backup a path if it exists and is not already our symlink
  local t="$1"
  [[ -e "$t" || -L "$t" ]] || return 0
  if [[ -L "$t" && "$(readlink "$t")" == "$DOTFILES"/* ]]; then return 0; fi
  run "mkdir -p '$BACKUP_DIR$(dirname "${t#$HOME}")'"
  run "mv '$t' '$BACKUP_DIR${t#$HOME}'"
  warn "backed up existing $t → $BACKUP_DIR${t#$HOME}"
}
link(){ # link SRC(relative to repo) TARGET(abs)
  local src="$DOTFILES/$1" dst="$2"
  [[ -e "$src" ]] || { err "missing in repo: $1"; return 1; }
  if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then ok "linked $dst"; return 0; fi
  backup "$dst"; run "mkdir -p '$(dirname "$dst")'"; run "ln -snf '$src' '$dst'"; ok "linked $dst → $1"
}
render(){ # render SRC TARGET  (substitutes __HOME__ etc, COPIES not links)
  local src="$DOTFILES/$1" dst="$2"
  backup "$dst"; run "mkdir -p '$(dirname "$dst")'"
  if (( DRY )); then info "[dry] render $1 → $dst (sub __HOME__,__GIT_NAME__,__GIT_EMAIL__)"; return; fi
  sed -e "s|__HOME__|$HOME|g" \
      -e "s|__GIT_NAME__|${GIT_NAME:-}|g" \
      -e "s|__GIT_EMAIL__|${GIT_EMAIL:-}|g" "$src" > "$dst"
  ok "rendered $dst ← $1"
}

# ============================================================================
#  dependency layer  (Homebrew + parallel prefetch)
# ============================================================================
have(){ command -v "$1" >/dev/null 2>&1; }

ensure_brew(){
  if have brew; then ok "Homebrew present"; return; fi
  step "Installing Homebrew"
  run '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  [[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
}

# brew_need <type> <name> <test-cmd> → echoes name to the right queue if missing
FORMULAE=(); CASKS=()
need_formula(){ have "$2" || FORMULAE+=("$1"); }                 # need_formula <pkg> <bin>
need_cask(){ [[ -d "$3" ]] || CASKS+=("$1"); }                  # need_cask <cask> <_> <app-path>

install_brew_queue(){
  local nf=${#FORMULAE[@]} nc=${#CASKS[@]}
  (( nf + nc )) || { ok "all Homebrew packages already present"; return; }
  export HOMEBREW_DOWNLOAD_CONCURRENCY=auto HOMEBREW_NO_AUTO_UPDATE=1
  step "Pre-fetching $((nf+nc)) package(s) in parallel"
  # kick off concurrent downloads, then install (install reuses cached bottles)
  if (( DRY )); then info "[dry] brew fetch ${FORMULAE[*]:-} ${CASKS[*]:-}"; else
    ( for p in ${FORMULAE[@]+"${FORMULAE[@]}"}; do brew fetch "$p" >/dev/null 2>&1 & done
      for c in ${CASKS[@]+"${CASKS[@]}"};       do brew fetch --cask "$c" >/dev/null 2>&1 & done
      wait ) & local fpid=$!
    spin "$fpid" "downloading bottles"
  fi
  (( nf )) && { step "brew install ${FORMULAE[*]}"; run "brew install ${FORMULAE[*]}"; }
  (( nc )) && { step "brew install --cask ${CASKS[*]}"; run "brew install --cask ${CASKS[*]}"; }
}
spin(){ local pid=$1 msg=$2 c='|/-\\' i=0
  while kill -0 "$pid" 2>/dev/null; do printf '\r  %s%s%s %s' "$DIM" "${c:i++%4:1}" "$R" "$msg"; sleep 0.2; done
  printf '\r  %s✓%s %s\n' "$GRN" "$R" "$msg"; }

# ============================================================================
#  profile pieces
# ============================================================================
collect_claude_deps(){
  need_formula bun bun
  have node || need_formula node node
  have jq   || need_formula jq jq
  have python3 || warn "python3 missing — install Xcode CLT (xcode-select --install)"
}
collect_full_deps(){
  collect_claude_deps
  need_formula koekeishiya/formulae/yabai yabai
  need_formula koekeishiya/formulae/skhd  skhd
  need_cask karabiner-elements _ "/Applications/Karabiner-Elements.app"
  need_cask wave              _ "/Applications/Wave.app"
  need_cask iterm2            _ "/Applications/iTerm.app"
  need_cask font-meslo-lg-nerd-font _ "$HOME/Library/Fonts/MesloLGSNerdFont-Regular.ttf"
}

ensure_claude_cli(){
  if have claude; then ok "Claude Code CLI present"; return; fi
  step "Installing Claude Code CLI"
  if (( DRY )); then info "[dry] curl -fsSL https://claude.ai/install.sh | bash"; return; fi
  if curl -fsSL https://claude.ai/install.sh 2>/dev/null | bash; then ok "claude installed"
  else warn "auto-install failed — install manually: https://docs.claude.com/en/docs/claude-code/setup"; fi
}
ensure_p10k(){
  if [[ -d "$HOME/powerlevel10k" ]]; then ok "powerlevel10k present"; return; fi
  step "Cloning Powerlevel10k"
  run "git clone --depth=1 https://github.com/romkatv/powerlevel10k.git '$HOME/powerlevel10k'"
}

link_claude(){
  step "Linking Claude Code config"
  link claude/settings.json     "$HOME/.claude/settings.json"
  for d in "$DOTFILES"/claude/skills/*/;        do link "claude/skills/$(basename "$d")"        "$HOME/.claude/skills/$(basename "$d")"; done
  for f in "$DOTFILES"/claude/hooks/*;           do link "claude/hooks/$(basename "$f")"          "$HOME/.claude/hooks/$(basename "$f")"; done
  for f in "$DOTFILES"/claude/scripts/*;         do [[ "$f" == *.example.sh ]] && continue; link "claude/scripts/$(basename "$f")" "$HOME/.claude/scripts/$(basename "$f")"; done
  for f in "$DOTFILES"/claude/commands/*;        do link "claude/commands/$(basename "$f")"       "$HOME/.claude/commands/$(basename "$f")"; done
  for f in "$DOTFILES"/claude/output-styles/*;   do link "claude/output-styles/$(basename "$f")"  "$HOME/.claude/output-styles/$(basename "$f")"; done
  for f in "$DOTFILES"/claude/themes/*;          do link "claude/themes/$(basename "$f")"         "$HOME/.claude/themes/$(basename "$f")"; done
  info "plugins (claude-hud, frontend-design) are declared in settings.json and"
  info "fetch from their marketplaces on first \`claude\` launch (or via /plugin)."
}
link_bin(){
  step "Linking ~/bin scripts"
  for f in "$DOTFILES"/bin/*; do link "bin/$(basename "$f")" "$HOME/bin/$(basename "$f")"; done
}
link_shell(){
  step "Linking shell config"
  link shell/zshrc    "$HOME/.zshrc"
  link shell/p10k.zsh "$HOME/.p10k.zsh"
  if [[ ! -e "$HOME/.gitconfig" ]] || ask "overwrite ~/.gitconfig (backed up) from template?"; then
    : "${GIT_NAME:=$(git config --global user.name  2>/dev/null || true)}"
    : "${GIT_EMAIL:=$(git config --global user.email 2>/dev/null || true)}"
    if (( ! ASSUME_YES )); then
      printf '  %s? git user.name  [%s]: %s' "$BLU" "${GIT_NAME:-}" "$R"; read -r x </dev/tty || true; [[ -n "$x" ]] && GIT_NAME="$x"
      printf '  %s? git user.email [%s]: %s' "$BLU" "${GIT_EMAIL:-}" "$R"; read -r x </dev/tty || true; [[ -n "$x" ]] && GIT_EMAIL="$x"
    fi
    render shell/gitconfig.template "$HOME/.gitconfig"
  fi
}
link_wm(){
  step "Linking window-management config"
  link wm/yabairc "$HOME/.yabairc"
  link wm/skhdrc  "$HOME/.skhdrc"
  render wm/karabiner.json "$HOME/.config/karabiner/karabiner.json"
}
link_terminals(){
  step "Linking terminal config"
  link terminal/waveterm/settings.json   "$HOME/.config/waveterm/settings.json"
  link terminal/waveterm/termthemes.json "$HOME/.config/waveterm/termthemes.json"
  link terminal/iterm2/DynamicProfiles/tokyo-night.json \
       "$HOME/Library/Application Support/iTerm2/DynamicProfiles/tokyo-night.json"
  info "In iTerm2: Settings → Profiles → select 'Tokyo Night (dotfiles)' → Other Actions → Set as Default."
}

start_services(){
  step "Starting yabai + skhd"
  run "yabai --start-service"
  run "skhd  --start-service"
}

# ============================================================================
#  the grants this installer CANNOT script — detect, instruct, block
# ============================================================================
grants_guide(){
  step "Manual macOS grants (cannot be automated — do these now)"
  cat <<EOF
  ${B}1. Accessibility${R}  (yabai + skhd + Karabiner need it)
       System Settings → Privacy & Security → Accessibility →
       enable: yabai, skhd, Karabiner-Elements, your terminal.

  ${B}2. Karabiner driver${R}
       First launch of Karabiner-Elements asks to allow a system extension &
       Input Monitoring. Approve in System Settings → Privacy & Security.

  ${B}3. yabai scripting addition  (needed by this .yabairc)${R}
       a) Partly disable SIP: reboot holding power → Recovery →
          Utilities → Terminal → ${ACC}csrutil enable --without-fs --without-debug --without-nvram${R}
          (or simply ${ACC}csrutil disable${R}) → reboot.
       b) Passwordless load-sa. Add a sudoers entry:
          ${ACC}echo "\$(whoami) ALL=(root) NOPASSWD: \$(which yabai) --load-sa" | sudo tee /etc/sudoers.d/yabai${R}
       Docs: https://github.com/koekeishiya/yabai/wiki
EOF
  if [[ "$PROFILE" == "full" ]]; then
    if csrutil status 2>/dev/null | grep -qi "enabled"; then
      warn "SIP is fully enabled — yabai --load-sa in .yabairc will fail until you do step 3."
    fi
    ask "Open System Settings → Accessibility now?" && run "open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'"
  fi
}

# ============================================================================
#  TUI
# ============================================================================
menu(){
  cat <<EOF
${B}${ACC}
  ┌────────────────────────────────────────────┐
  │   dotfiles · one-shot Mac setup              │
  └────────────────────────────────────────────┘${R}
  Pick what to install:

    ${B}1${R}) Claude Code only   — config, skills, hooks, CLI, bun
    ${B}2${R}) Full setup         — Claude + window mgmt + terminals + shell + bin
    ${B}3${R}) Dry run (full)     — show every action, change nothing
    ${B}q${R}) quit
EOF
  local c; printf '\n  %sChoose [1/2/3/q]: %s' "$BLU" "$R"; read -r c </dev/tty || true
  case "$c" in
    1) PROFILE="claude" ;;
    2) PROFILE="full" ;;
    3) PROFILE="full"; DRY=1 ;;
    *) echo "  bye."; exit 0 ;;
  esac
}

# ============================================================================
#  main
# ============================================================================
main(){
  [[ "$(uname)" == "Darwin" ]] || { err "macOS only."; exit 1; }
  [[ -z "$PROFILE" ]] && menu
  (( DRY )) && warn "DRY RUN — no changes will be made."
  step "Profile: $PROFILE   ·   repo: $DOTFILES"

  ensure_brew
  if [[ "$PROFILE" == "claude" ]]; then collect_claude_deps; else collect_full_deps; fi
  install_brew_queue
  ensure_claude_cli

  link_claude
  link_bin               # api_keys + wave_focus + wm_* are useful in both profiles

  if [[ "$PROFILE" == "full" ]]; then
    ensure_p10k
    link_shell
    link_wm
    link_terminals
    start_services
    grants_guide
  fi

  step "Done"
  ok "Backups (if any): $BACKUP_DIR"
  cat <<EOF
  Next:
    • Open a new terminal (or: ${ACC}exec zsh${R}) to load the shell config.
    • Manage API keys:  ${ACC}api_keys help${R}   (stored in macOS Keychain).
    • IP geofence is OFF by default. To enable, copy
      claude/scripts/blocked-countries.example.sh →
      ~/.config/claude-ip-guard/blocked-countries.sh
    • Read docs/ and open cheatsheet.html for shortcuts & usage.
EOF
}
main
