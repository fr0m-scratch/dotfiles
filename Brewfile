# Brewfile — every dependency these dotfiles touch.
# Install all at once:  brew bundle --file=Brewfile
# (install.sh fetches these in parallel and only the missing ones.)

# taps
tap "koekeishiya/formulae"

# ── core / Claude Code ───────────────────────────────────────────
brew "bun"          # runs the claude-hud statusline (settings.json)
brew "node"         # general JS tooling
brew "jq"           # used by the `wave` shell function & scripts
brew "git"
brew "pandoc"       # /latex skill: Markdown → formal PDF (needs TinyTeX/xelatex)
brew "poppler"      # /latex verify step (pdftoppm) + PDF page rendering

# ── window management (full profile) ─────────────────────────────
brew "koekeishiya/formulae/yabai"   # tiling WM  (needs SIP partial-disable for scripting addition)
brew "koekeishiya/formulae/skhd"    # hotkey daemon

# ── apps (full profile) ──────────────────────────────────────────
cask "wave"                 # Wave Terminal (primary)
cask "iterm2"               # iTerm2
cask "karabiner-elements"   # key remapping (Caps Lock → Wave, Option workspaces)
cask "font-meslo-lg-nerd-font"  # glyphs for Powerlevel10k

# NOTE: Claude Code CLI is not on Homebrew — install.sh fetches it from
#   https://claude.ai/install.sh  (or see docs.claude.com/en/docs/claude-code/setup)
# NOTE: Powerlevel10k is cloned to ~/powerlevel10k by install.sh (not brew).
