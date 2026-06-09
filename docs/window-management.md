# Window Management

> 中文导读:这套窗口管理把 macOS 变成一个**自动平铺 + 一键工作区**的环境。三个工具配合:`yabai` 负责自动把窗口铺满屏幕(BSP 平铺),`skhd` 负责窗口操作快捷键(切焦点、移动、缩放、换布局),`karabiner` 负责按键重映射和"一键打开/聚焦某个 App 的工作区"。本指南按 stack → spaces 模型 → wm_* 脚本 → skhd 快捷键 → 关键系统授权(SIP / sudoers / Accessibility)的顺序展开。最后一节是**必读**的:不做那几步,`yabai` 的核心功能(跨 Space 移动窗口、网格排布)无法工作。

This guide documents the tiling window-management layer of the dotfiles: how windows auto-arrange, how the 7 labeled spaces route apps, what every hotkey does, and the one-time macOS security setup that the installer can only *print* but cannot perform for you.

All config files live under `wm/`:

| File | Tool | Installed to |
| --- | --- | --- |
| `wm/yabairc` | yabai | `~/.config/yabai/yabairc` (or `~/.yabairc`) |
| `wm/skhdrc` | skhd | `~/.config/skhd/skhdrc` (or `~/.skhdrc`) |
| `wm/karabiner.json` | Karabiner-Elements | `~/.config/karabiner/karabiner.json` |
| `bin/wm_*`, `bin/wave_focus` | helper scripts | `~/bin/` (must be on `PATH`) |

These are part of the **`full`** install profile. The `claude` profile (Claude Code only) does not touch window management.

---

## 1. The stack — yabai + skhd + Karabiner

中文:三件套各管一摊,互不重叠,组合起来才是完整体验。

### yabai — the tiling engine

[yabai](https://github.com/koekeishiya/yabai) is a tiling window manager. Whenever you open a window it automatically splits the screen so windows never overlap, using a **BSP (Binary Space Partitioning)** layout. From `wm/yabairc`:

```sh
yabai -m config layout bsp
yabai -m config window_placement second_child
yabai -m config auto_balance off
yabai -m config split_ratio 0.5
yabai -m config split_type auto
```

Other notable settings in `wm/yabairc`:

| Setting | Value | Meaning |
| --- | --- | --- |
| `window_gap` | `6` | 6px gap between tiled windows |
| `top/bottom/left/right_padding` | `6` | 6px padding from the screen edge |
| `mouse_follows_focus` | `on` | focusing a window warps the cursor to it |
| `focus_follows_mouse` | `off` | hovering does **not** steal focus |
| `mouse_modifier` | `alt` | hold `Alt` + drag to move/resize with the mouse |
| `mouse_action1` / `mouse_action2` | `move` / `resize` | left-drag moves, right-drag resizes |
| `mouse_drop_action` | `swap` | dropping a dragged window swaps it with the one underneath |
| `window_shadow` | `on` | keep macOS window shadows |
| `window_animation_duration` | `0.0` | instant, no resize animation |
| `window_opacity` | `off` | no transparency on unfocused windows |
| `external_bar` | `all:0:0` | no reserved space for an external status bar |

**Window rules (exclusions)** — some apps should *not* be tiled and are left floating:

```sh
yabai -m rule --add app="^yabai_config$" manage=off
yabai -m rule --add app="^System Preferences$" manage=off
yabai -m rule --add app="^System Settings$" manage=off
yabai -m rule --add app="^Calculator$" manage=off
yabai -m rule --add app="^Archive Utility$" manage=off
yabai -m rule --add app="^Finder$" title="(Copy|Move|Trash)" manage=off
```

### skhd — the hotkey daemon

[skhd](https://github.com/koekeishiya/skhd) is a keyboard hotkey daemon. `wm/skhdrc` binds key combos to `yabai -m ...` commands: focus a neighbor window, swap windows, resize, switch layouts, and move focus across displays. These are the **window-level** controls (see section 4).

### Karabiner-Elements — key remaps & workspace launchers

[Karabiner-Elements](https://karabiner-elements.pqrs.org/) does low-level key remapping. `wm/karabiner.json` defines three groups of "complex modifications":

1. **Caps Lock → Wave Terminal** — tapping Caps Lock runs `~/bin/wave_focus` (opens/focuses [Wave Terminal](https://www.waveterm.dev/)).
2. **Option + number → macOS Desktop** — `Option+1..9` is remapped to `Control+1..9`, which is macOS's native "switch to Desktop N" shortcut. This is why `Option+N` jumps between native Spaces/Desktops.
3. **Option app-workspace actions** — `Option+W/N/L/F/M/R` each run a `wm_*` helper script (see section 3).

> Note: paths in `karabiner.json` use the `__HOME__` placeholder (e.g. `__HOME__/bin/wm_chat`); the installer substitutes your real home directory at install time.

**Why Karabiner and not skhd for the app launchers?** `wm/skhdrc` itself notes: *"Apps / Spaces are handled by Karabiner: alt+1..9, alt+w, alt+l, alt+m, alt+r."* Karabiner can both inject a native macOS Desktop-switch keystroke **and** run a shell command from a single keypress (visible in the `Option+F` rule, which sends `Control+5` then runs `wm_firefox`), which skhd cannot do as cleanly.

---

## 2. The Spaces model

中文:这里区分两个概念。`yabai` 的 **label** 是给显示器(display)和 Space 起的名字,脚本用名字而不是序号来定位,序号会变名字不变。下面 7 个标签把固定 App 固定到固定 Space。

`wm/yabairc` labels two displays and several spaces, then pins specific apps to specific spaces.

### Display labels

```sh
yabai -m display 1 --label main
yabai -m display 2 --label side
```

### Space labels

| Space index | Label | Purpose |
| --- | --- | --- |
| 2 | `chat` | WeChat (and WeChat2) |
| 3 | `notion` | Notion |
| 4 | `lark` | Lark / LarkSuite |
| 5 | `firefox` | Firefox |
| 7 | `side_space` | a secondary/overflow space |

> The `wm_*` scripts target spaces **by label** (`yabai -m space --focus chat`), so the label is the stable contract — re-ordering spaces in Mission Control won't break the shortcuts as long as the labels stay attached.

### App → space routing rules

These yabai rules send an app's windows to its dedicated space automatically whenever the app opens:

```sh
yabai -m rule --add label="app-wechat"  app="^WeChat$"  space=chat
yabai -m rule --add label="app-notion"  app="^Notion$"  space=notion
yabai -m rule --add label="app-lark"    app="^Lark$"    space=lark
yabai -m rule --add label="app-firefox" app="^Firefox$" space=firefox
```

So the model is: **one app, one home space.** Open WeChat → it lands on `chat`. Open Notion → it lands on `notion`. The `Option+letter` shortcuts (section 3) then *jump you to that space and make sure the app is open and un-minimized*.

---

## 3. The `wm_*` scripts (Option-key workspace launchers)

中文:这是日常最常用的一组快捷键。每个 `Option+字母` 都对应一个脚本,做三件事:**聚焦目标 Space → 打开/去最小化 App → (聊天专用)按网格排版**。脚本都很防御性:每步失败都 `|| true`,不会因为某个 App 没装就报错。

Karabiner maps each of these keys to a script in `~/bin/`:

| Shortcut | Script | What it does |
| --- | --- | --- |
| `Option+W` | `wm_chat` | Focus `chat` space; `open -a WeChat` and `WeChat2`; de-minimize any minimized WeChat windows; then call `wm_arrange_chat` to tile them. |
| (internal) | `wm_arrange_chat` | Tiles WeChat windows on `chat`: 1 window → full screen (`--grid 1:1:0:0:1:1`); 2+ windows → side-by-side halves (`1:2:0:0` and `1:2:1:0`). |
| `Option+N` | `wm_notion` | Focus `notion` space; `open -a Notion`; de-minimize minimized Notion windows. |
| `Option+L` | `wm_lark` | Focus `lark` space; `open -a LarkSuite`; de-minimize minimized Lark windows. (No longer forces fullscreen — Lark tiles normally with yabai.) |
| `Option+F` | `wm_firefox` | Karabiner first sends `Control+5` (native switch to Desktop 5), then runs the script: focus `firefox` space; `open -a Firefox`; de-minimize minimized Firefox windows. |
| `Option+M` | `wm_space_minimize` | Minimize **all** currently-visible windows on the *current* space, recording their IDs to a state file so they can be restored exactly. |
| `Option+R` | `wm_space_restore` | De-minimize the windows recorded by the last `Option+M` on this space (or, if no state file exists, de-minimize whatever is currently minimized here). |

> `Option+1..9` is **not** a `wm_*` script — Karabiner remaps it to `Control+1..9` so it switches macOS native Desktops directly.

### How the launchers work (shared pattern)

Each launcher (`wm_chat`, `wm_notion`, `wm_lark`, `wm_firefox`) follows the same defensive recipe:

```sh
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"  # so yabai/jq/open resolve under Karabiner
sleep 0.2                                  # let the keystroke settle
# append a timestamped line to ~/.local/share/wm_app_shortcuts.log
yabai -m space --focus <label> 2>/dev/null || true   # jump to the home space
open -a <App> || true                      # launch or foreground the app
# de-minimize the app's minimized windows on that space (via yabai query + jq)
```

The `PATH` export matters: Karabiner runs commands with a minimal environment, so the scripts hardcode the Homebrew/system paths to find `yabai`, `jq`, and `open`. Every step is `|| true`, so a missing app never aborts the script. Launches are also logged to `~/.local/share/wm_app_shortcuts.log` for debugging.

### Minimize / restore a whole space

`wm_space_minimize` and `wm_space_restore` give you a "stash the whole workspace and bring it back" toggle, scoped per-space:

- **Minimize** (`Option+M`): queries the current space for windows that are visible and not minimized, writes their IDs to `${XDG_CACHE_HOME:-~/.cache}/wm-spaces/minimized-space-<index>`, then minimizes each one.
- **Restore** (`Option+R`): reads that state file and de-minimizes exactly those windows; if the state file is empty/missing it falls back to de-minimizing whatever is currently minimized on the space. The state file is deleted after a successful restore.

### `wave_focus` (Caps Lock)

Tapping **Caps Lock** runs `~/bin/wave_focus`, which is simply:

```bash
open -a "Wave"
```

`open -a` launches Wave Terminal if it isn't running, or brings it to the front if it is. (This replaced an older iTerm "new tab + focus" script.)

---

## 4. skhd window controls

中文:这一组是纯窗口操作,全部在 `wm/skhdrc` 里。键码 `0x7B/0x7C/0x7D/0x7E` 分别是左/右/下/上方向键。`Alt` = Option。

Key codes in `skhdrc`: `0x7B`=←, `0x7C`=→, `0x7D`=↓, `0x7E`=↑. `alt` is the Option key.

### Focus a neighboring window

| Shortcut | Action |
| --- | --- |
| `Alt+←` | Focus window to the **west** |
| `Alt+→` | Focus window to the **east** |
| `Alt+↑` | Focus window to the **north** |
| `Alt+↓` | Focus window to the **south** |

### Move / swap windows

| Shortcut | Action |
| --- | --- |
| `Shift+Alt+←` | Swap with window to the west |
| `Shift+Alt+→` | Swap with window to the east |
| `Shift+Alt+↑` | Swap with window to the north |
| `Shift+Alt+↓` | Swap with window to the south |

### Resize the focused window

| Shortcut | Action |
| --- | --- |
| `Ctrl+Alt+←` | Resize left edge by `-20` (`--resize left:-20:0`) |
| `Ctrl+Alt+→` | Resize right edge by `+20` (`--resize right:20:0`) |
| `Ctrl+Alt+↑` | Resize top edge by `-20` (`--resize top:0:-20`) |
| `Ctrl+Alt+↓` | Resize bottom edge by `+20` (`--resize bottom:0:20`) |

### Change the layout

| Shortcut | Action |
| --- | --- |
| `Alt+E` | Set current space layout to **BSP** tiling (`space --layout bsp`) |
| `Alt+S` | Set current space layout to **stack** (`space --layout stack`) |
| `Alt+F` | Toggle **fullscreen zoom** on the focused window (`window --toggle zoom-fullscreen`) |
| `Alt+T` | Toggle **float** for the focused window (`window --toggle float`) |

### Displays (multi-monitor)

| Shortcut | Action |
| --- | --- |
| `Alt+D` | Focus the **next display** (`display --focus next`) |
| `Shift+Alt+D` | Move the focused window to the **next display** and follow it (`window --display next --focus`) |

### Other bindings present in `skhdrc`

| Shortcut | Action |
| --- | --- |
| `Alt+2` (`0x32`, the backtick/§ key area) | Toggle the `cockpit` tmux popup (`tmux display-popup -E -t cockpit`), falling back to opening iTerm |
| `Cmd+Alt+C` | Open iTerm |

> Moving windows between *spaces* (not just displays) requires the yabai **scripting addition** — see section 5. Without it, `Shift+Alt+arrows` and the `wm_arrange_chat` grid commands may silently do nothing.

---

## 5. THE CRITICAL SETUP (read this — the installer cannot do it for you)

中文:**最关键、也最容易漏的一步。** `yabai` 的高级功能(跨 Space 移动窗口、`--grid` 网格排版、`--load-sa`)依赖一个叫 *scripting addition* 的内核注入,而 macOS 默认的 SIP(系统完整性保护)会阻止它。你必须:(1) 进 Recovery 部分关闭 SIP;(2) 加一条免密 sudoers 让 `yabai --load-sa` 不用每次输密码;(3) 在系统设置里授予 Accessibility 和 Input Monitoring 权限。`install.sh` 会**打印**这些步骤并尝试帮你打开设置面板,但**无法自动完成**——它们需要重启进 Recovery、`sudo` 和系统弹窗点击。

`wm/yabairc` begins with:

```sh
yabai -m signal --add event=dock_did_restart action="sudo yabai --load-sa"
sudo yabai --load-sa
```

This loads the **scripting addition**, which is what powers cross-space window moves, the `--grid` placement used by `wm_arrange_chat`, and other privileged operations. For this to work you need three one-time grants.

### Step A — Partially disable SIP (in Recovery)

The scripting addition injects into Dock, which SIP forbids by default. Reboot into Recovery and relax SIP:

1. Shut down. **Reboot into Recovery** (Apple Silicon: hold the power button until "Loading startup options"; Intel: hold `Cmd+R` at boot).
2. Open **Utilities → Terminal** and run:

   ```sh
   csrutil enable --without-fs --without-debug --without-nvram
   ```

   (Or, more bluntly, `csrutil disable`.)
3. Reboot back into macOS.

After rebooting you can confirm with `csrutil status`. If it still says *"System Integrity Protection status: enabled"* (fully), `yabai --load-sa` in `yabairc` will fail — the installer warns about exactly this.

### Step B — Passwordless `yabai --load-sa` (sudoers)

`yabairc` calls `sudo yabai --load-sa` on every load and on every Dock restart. Without a passwordless rule this would prompt for your password (and break on the `dock_did_restart` signal). Add a dedicated sudoers file:

```sh
echo "$(whoami) ALL=(root) NOPASSWD: $(which yabai) --load-sa" | sudo tee /etc/sudoers.d/yabai
```

This grants *only* the `yabai --load-sa` command passwordless — nothing else.

> Tip: the path baked into the sudoers entry is wherever `which yabai` resolved at the time you ran it (e.g. `/opt/homebrew/bin/yabai`). If you later move or reinstall yabai to a different path, regenerate this file or `--load-sa` will start prompting again.

### Step C — Accessibility + Input Monitoring grants

In **System Settings → Privacy & Security**:

1. **Accessibility** — add and enable **yabai**, **skhd**, and **Karabiner-Elements**. All three need it to observe/control windows and keys.
2. **Input Monitoring** — Karabiner installs a virtual keyboard driver (`Karabiner-VirtualHIDDevice`). Approve the driver and grant **Input Monitoring** to Karabiner. macOS may prompt you to allow the system extension the first time.

The installer (`install.sh`) prints all of the above and offers to open the Accessibility settings pane:

```
open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
```

…but it **cannot** click the toggles, type your password for sudoers, or reboot into Recovery for you. These are deliberately manual, security-gated steps.

### Verifying it worked

After all three steps and a fresh login:

```sh
yabai --start-service    # or: brew services start yabai
skhd --start-service     # or: brew services start skhd
csrutil status           # should NOT say fully "enabled"
yabai -m query --spaces  # should print your spaces with labels
```

If `Shift+Alt+arrows` (move between displays) works but `wm_arrange_chat`'s grid layout or cross-space moves do nothing, the scripting addition is not loaded — re-check steps A and B.

---

## Troubleshooting quick reference

| Symptom | Likely cause |
| --- | --- |
| Hotkeys do nothing at all | skhd not running, or Accessibility not granted to skhd |
| `Option+W/N/L/F` does nothing | Karabiner not running / Input Monitoring not granted; or script not on `PATH` in `~/bin` |
| Grid layout / cross-space moves silently fail | Scripting addition not loaded (SIP fully enabled, or sudoers entry missing/wrong path) |
| `sudo` password prompt on every login | `/etc/sudoers.d/yabai` missing or `yabai` path changed |
| App opens but doesn't go to its space | yabai `rule` not applied — check the app's exact name matches `^WeChat$` etc. |
| Caps Lock doesn't open Wave | Karabiner not running, or `~/bin/wave_focus` not present/executable |

Logs: the app launchers append to `~/.local/share/wm_app_shortcuts.log`; tail it to see whether a keypress actually fired its script.
