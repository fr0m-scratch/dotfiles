# Keyboard Shortcuts Reference / 键盘快捷键参考

> **中文导读：** 这份文档是本 dotfiles 的**完整键盘快捷键参考**。所有快捷键来自三个层级，从下到上分别是：
> Karabiner（系统级、把按键重映射成其他按键或脚本）、skhd（配合 yabai 做平铺窗口管理）、以及 zsh shell 的别名/函数。
> 每个快捷键都列出了**组合键 / 动作 / 用途**三栏。下面的设计前提请务必记住。

## Design premise — read this first / 先读这里

This setup is built around two deliberate remappings. Everything else depends on them:

1. **Caps Lock is no longer a modifier.** It does **not** act as Caps Lock, Control, Hyper, or anything modifier-like. Karabiner intercepts a tap of Caps Lock and runs a shell command that opens/focuses **Wave Terminal**. So the largest, easiest-to-hit key on the keyboard becomes "jump to my terminal."
   - 中文：`Caps Lock` 已经被彻底改造，不再是任何修饰键，按一下 = 直接聚焦 Wave 终端。

2. **Option (⌥) is the primary window-manager modifier.** Almost all window/space movement is `Option + …`. macOS normally uses Option for special characters, but here Karabiner and skhd claim the Option combos listed below. (Plain typing of accented characters still works for keys not listed here.)
   - 中文：`Option (⌥)` 是窗口管理的主修饰键，下面绝大多数操作都是 `Option + 某键`。

The three sources, by layer:

| Source | File | Layer / Responsibility |
| --- | --- | --- |
| Karabiner-Elements | `wm/karabiner.json` | System-wide key remapping: Caps Lock, Option+number → desktop switch, Option+letter → app/workspace scripts |
| skhd | `wm/skhdrc` | Hotkey daemon driving **yabai** tiling window manager: focus / move / resize / layout |
| zsh | `shell/zshrc` | Shell aliases & functions (typed at the prompt, not chords) |

> `__HOME__` in `wm/karabiner.json` is a template placeholder; `install.sh` rewrites it to your real `$HOME` so the `shell_command` paths point at `~/bin/...`.

---

## 1. Karabiner — system-wide (`wm/karabiner.json`)

中文：Karabiner 在系统层面拦截按键。这一层负责"切桌面 / 切 App / 启动脚本"，在任何前台程序里都生效。

### 1.1 Caps Lock

| Chord | Action | Why / When |
| --- | --- | --- |
| `Caps Lock` | Run `~/bin/wave_focus` — open or focus **Wave Terminal** | One-key jump to your terminal from anywhere; Caps Lock is no longer a modifier |

### 1.2 Option + number → switch macOS Desktop / Space

Each `Option + N` is remapped to `Control + N`, which is the macOS default shortcut for "switch to Desktop N" (enable it in **System Settings → Keyboard → Keyboard Shortcuts → Mission Control**). This lets you change Spaces with Option instead of Control, keeping the Option modifier consistent with window management.

| Chord | Action | Why / When |
| --- | --- | --- |
| `Option + 1` | Sends `Control + 1` → switch to Desktop/Space 1 | Jump straight to Space 1 |
| `Option + 2` | Sends `Control + 2` → Space 2 | Jump to Space 2 |
| `Option + 3` | Sends `Control + 3` → Space 3 | Jump to Space 3 |
| `Option + 4` | Sends `Control + 4` → Space 4 | Jump to Space 4 |
| `Option + 5` | Sends `Control + 5` → Space 5 | Jump to Space 5 |
| `Option + 6` | Sends `Control + 6` → Space 6 | Jump to Space 6 |
| `Option + 7` | Sends `Control + 7` → Space 7 | Jump to Space 7 |
| `Option + 8` | Sends `Control + 8` → Space 8 | Jump to Space 8 |
| `Option + 9` | Sends `Control + 9` → Space 9 | Jump to Space 9 |

### 1.3 Option + letter → app / workspace actions

These run helper scripts in `~/bin` that bring up a specific app or run a workspace action. The scripts are personal automations (focus a window on a chosen Space, etc.).

| Chord | Action | Why / When |
| --- | --- | --- |
| `Option + W` | Run `~/bin/wm_chat` | Open/focus your chat ("W" = WeChat/chat workspace) |
| `Option + N` | Run `~/bin/wm_notion` | Open/focus **Notion** |
| `Option + L` | Run `~/bin/wm_lark` | Open/focus **Lark / 飞书** |
| `Option + F` | Send `Control + 5` (switch to Space 5) **then** run `~/bin/wm_firefox` | Jump to the browser Space and focus **Firefox** in one chord |
| `Option + M` | Run `~/bin/wm_space_minimize` | Minimize / tuck away the current Space's windows |
| `Option + R` | Run `~/bin/wm_space_restore` | Restore the windows previously minimized by `Option + M` |

> `Option + M` and `Option + R` are a pair: minimize stows the layout, restore brings it back.

---

## 2. skhd — yabai window management (`wm/skhdrc`)

中文：skhd 是热键守护进程，把按键转成 `yabai` 命令，实现平铺式窗口管理（聚焦、交换、缩放、布局）。
注意：`alt` 在 skhd 里就是 `Option`。`0x7B/0x7C/0x7D/0x7E` 是方向键的硬件键码（← → ↓ ↑）。

> Key-code legend: `0x7B = ←` (left), `0x7C = →` (right), `0x7D = ↓` (down), `0x7E = ↑` (up).

### 2.1 Focus window

| Chord | Action | Why / When |
| --- | --- | --- |
| `Option + ←` | `yabai window --focus west` | Move focus to the window on the left |
| `Option + ↓` | `yabai window --focus south` | Focus the window below |
| `Option + ↑` | `yabai window --focus north` | Focus the window above |
| `Option + →` | `yabai window --focus east` | Focus the window on the right |

### 2.2 Move / swap window

| Chord | Action | Why / When |
| --- | --- | --- |
| `Shift + Option + ←` | `yabai window --swap west` | Swap current window with the one to its left |
| `Shift + Option + ↓` | `yabai window --swap south` | Swap with the window below |
| `Shift + Option + ↑` | `yabai window --swap north` | Swap with the window above |
| `Shift + Option + →` | `yabai window --swap east` | Swap with the window to its right |

### 2.3 Resize window (20 px steps)

| Chord | Action | Why / When |
| --- | --- | --- |
| `Ctrl + Option + ←` | `yabai window --resize left:-20:0` | Pull the left edge in by 20 px |
| `Ctrl + Option + ↓` | `yabai window --resize bottom:0:20` | Push the bottom edge down by 20 px |
| `Ctrl + Option + ↑` | `yabai window --resize top:0:-20` | Pull the top edge up by 20 px |
| `Ctrl + Option + →` | `yabai window --resize right:20:0` | Push the right edge out by 20 px |

### 2.4 Layout & window state

| Chord | Action | Why / When |
| --- | --- | --- |
| `Option + E` | `yabai space --layout bsp` | Switch the Space to **bsp** tiling (auto split — the normal working layout) |
| `Option + S` | `yabai space --layout stack` | Switch to **stack** layout (windows stacked, one visible at a time) |
| `Option + F` | `yabai window --toggle zoom-fullscreen` | Zoom the focused window to fill the Space (toggle) |
| `Option + T` | `yabai window --toggle float` | Toggle the focused window between tiled and floating |

### 2.5 Displays / monitors

| Chord | Action | Why / When |
| --- | --- | --- |
| `Option + D` | `yabai display --focus next` | Move focus to the next display |
| `Shift + Option + D` | `yabai window --display next --focus` | Send the current window to the next display and follow it |

### 2.6 Terminal popups (cockpit)

| Chord | Action | Why / When |
| --- | --- | --- |
| `` Option + ` `` | `tmux display-popup -E -t cockpit` (falls back to `open -a iTerm` if tmux/popup unavailable) | Quick floating popup of your `cockpit` tmux session over whatever you're doing |
| `Cmd + Option + C` | `open -a iTerm` | Open / focus a full **iTerm** window |

> `` ` `` is key-code `0x32`. The popup targets a tmux session named `cockpit`; if it isn't running, it just opens iTerm.

---

## 3. zsh — shell aliases & functions (`shell/zshrc`)

中文：这些不是组合键，而是在 shell 提示符里**输入的命令**。它们围绕 Wave Terminal 的 `wsh` 工具，把项目摊开成"VS Code 风格"的多面板布局，或在 Wave 里预览文件 / 网页。

### 3.1 Quick aliases

| Command | Expands to | Why / When |
| --- | --- | --- |
| `v <file/dir>` | `wsh view` | Open a **preview block** in Wave (files, images, directories) |
| `e <file>` | `wsh edit` | Open an **editor block** in Wave for a file |
| `cl` | `clear` | Clear the terminal screen |
| `check <pattern>` | `history 0 \| grep <pattern>` | Search your full shell history for a command |

### 3.2 `wave [dir]` — lay out the current Wave tab like an IDE

`wave` rearranges the **current Wave tab** into a VS Code–style coding layout:
**left** = the shell you ran it in (session slot) · **middle** = a `claude` agent block + a `codex` agent block · **right** = a file-tree view of the directory.

```bash
wave            # use the current directory ($PWD)
wave ~/proj     # lay out that project directory
wave .          # same as no argument (current dir)

WAVE_AI_PANEL=1 wave .          # also open Wave's built-in AI side panel
WAVE_STATUS_CMD='my-status.sh' wave .   # add a bottom status/quota pane running your script
```

| Aspect | Detail |
| --- | --- |
| Argument | Optional `dir` (defaults to `$PWD`; `~` and `.` are expanded/resolved) |
| Requirement | Must be run **inside a Wave terminal pane** (`$WAVETERM_TABID` must be set — press `Cmd + T` for a fresh tab first) |
| `WAVE_AI_PANEL=1` | Also opens the Wave AI side panel (width 560) |
| `WAVE_STATUS_CMD=…` | If set, adds a bottom pane running that command (e.g. a quota/status script). Not shipped with these dotfiles |
| Note | Wave can't size panes from the CLI — drag the dividers afterward to resize |

> Why/when: instant "`code .`"-style workspace inside Wave with Claude + Codex agents and a file tree, without manually spawning each pane.

### 3.3 `wavep [-m] <path>` — preview a file/image/dir in Wave

```bash
wavep report.pdf            # preview a file in a Wave preview block
wavep ./screenshots         # preview a directory
wavep -m diagram.png        # -m = magnified preview
wavep https://example.com   # http/https/file URLs are passed through as-is
```

| Aspect | Detail |
| --- | --- |
| `-m` / `--magnified` | Open the preview magnified |
| `<path>` | Defaults to `.`; local paths are resolved to an absolute, symlink-resolved path and checked to exist |
| URLs | `http://`, `https://`, `file://` are passed straight to `wsh view` |

> Why/when: quickly eyeball a file, image, or directory in a Wave block without leaving the shell.

### 3.4 `waveweb [-m] <file|url>` — open HTML/web in a Wave browser block

```bash
waveweb index.html              # open a local HTML artifact in a Wave web block
waveweb -m dashboard.html       # -m = magnified
waveweb http://localhost:3000   # open a localhost dev server
waveweb https://example.com     # open any URL
```

| Aspect | Detail |
| --- | --- |
| `-m` / `--magnified` | Open the web block magnified |
| `<file\|url>` | **Required.** `http://`, `https://`, `file://` open directly; a local path is converted to an absolute `file://` URL (spaces are percent-encoded) |

> Why/when: preview generated HTML artifacts or a running localhost dev server in an embedded Wave browser, instead of switching to a separate browser app.

---

## Quick mental model / 速记

- **Caps Lock** → terminal. **Option** → windows & spaces. **Option+letter** → apps.
- Arrows under **Option** focus; add **Shift** to move; add **Ctrl** to resize.
- `Option+1..9` change Space; `Option+D` / `Shift+Option+D` deal with displays.
- At the shell: `v`/`e` open Wave blocks, `wave` lays out an IDE, `wavep`/`waveweb` preview files & web.
