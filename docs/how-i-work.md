# How I actually work — the philosophy

*A non-technical companion to this repo. It explains **why** the setup is shaped the way it is:
how I use Claude, how the keyboard drives the machine, and what `fr0m` and the hooks are really for.*

🌏 中文版 → [`how-i-work.zh.md`](how-i-work.zh.md) · 🗺️ Shortcut card → [`../cheatsheet.html`](../cheatsheet.html)

This isn't just a pile of configs — it's a way of working. Two ideas hold it together:
**govern the AI before you trust it**, and **drive the machine from the keyboard, not the mouse.**

---

## fr0m is the core of everything

I treat Claude as a brilliant but forgetful collaborator. Brilliant, so I give it real work.
Forgetful, so I never let intent live only in a chat history that scrolls away. **Every project
starts with `/fr0m`**, which lays down four documents that *are* the project's memory and law:

| Doc | What it is | The role it plays |
|-----|-----------|-------------------|
| **Principal.md** | The constitution — the end goal and the hard restrictions. | *Mine.* Claude may not quietly rewrite it; changing it is a deliberate act. |
| **Plan.md** | The single source of truth — always the most current picture of the work. | Re-read before acting; every new decision folds in here immediately. |
| **AOL.md** | Append-only log — a timestamped trail of everything that was done. | The durable memory. Never edited, only appended, so history can't be quietly rewritten. |
| **Errors.md** | Every error and how it was resolved. | So the same wall isn't hit twice. |

The philosophy in one line: **externalize intent into durable, append-only documents, and the
work becomes governed, auditable, and resumable** — by me, by Claude, by anyone who clones it.
A chat is a conversation; fr0m turns it into a project with a constitution and a paper trail.
That's why this very repo is itself governed by fr0m — look at its `Principal/Plan/Errors`.

---

## The hooks make the discipline automatic

Rules nobody enforces are wishes. So the discipline is wired into hooks that run on every turn —
I don't have to remember it, and Claude can't drift from it:

- **`fr0m-guard`** quietly refuses the things that would break the system: rewriting the
  append-only log, editing the constitution behind my back, or signing commits as a Claude
  co-author. It fails *open* on anything it doesn't understand, so it guards without getting in the way.
- **`fr0m-rules`** re-injects the standing rules at the start of every turn *whenever a project is
  governed*, so the worldview above is always in front of Claude — never "forgotten" three messages later.
- **`ip-guard`** is a personal safety rail (off by default in this repo). The point isn't the
  specific check; it's that a guard rail you set once keeps protecting you without attention.

---

## `/check` — "show me," not "tell me"

I think visually, so I rarely want a wall of explanatory text. **`/check` renders whatever Claude
produced into a self-contained HTML page and pops it open in Wave instantly.** Output becomes a
*viewable artifact* — a table, a diagram, a dashboard, this repo's own `cheatsheet.html` — not
paragraphs I have to imagine. (The `blocks` output style does the small-scale version of this:
every reply ends with a rule so turns read as clean, scannable blocks.)

---

## How Claude sits in the day

`wave .` lays out a coding cockpit in one command: my shell on the left, **Claude and Codex side
by side** in the middle, a file tree on the right. I run agents in parallel and keep the settings
tuned for serious work — `effort: high`, `advisor: opus` for a second opinion on hard calls, a
custom theme so the panes are easy on the eyes. Claude is a teammate with a desk in my workspace,
not a website I visit.

---

## Claude reads from where my work lives

My real context doesn't live in the repo — it lives in **Lark/飞书 and Notion**. So I let Claude
read it directly instead of copy-pasting: the Notion and Lark tools are wired into **every**
session, and a local-cache reader pulls Notion pages straight out of the desktop app — no API
hoops, no "share this page first." Two small source agents do the fetching — they pull read-only,
clean the content into Markdown, and stamp it **reference-only**, so material I *gathered* never
gets confused with what I *decided*. The keys for all this never touch the repo; they sit in the
macOS Keychain and the tooling fetches them at launch. The point is the same as everywhere else:
let Claude work with my actual material, but keep the boundary sharp and the secrets put.

---

## The keyboard is the command surface

The desktop is arranged so I never hunt for a window — **one key, one place, muscle memory:**

- **Caps Lock → Wave**, from anywhere. The most useless key on the keyboard now jumps straight to
  where the agents live. That's the home key of my whole setup.
- **Option + a number** flips between desktops; **Option + a letter** summons an entire app
  *workspace* in one stroke — `⌥W` WeChat, `⌥N` Notion, `⌥L` Lark, `⌥F` Firefox — each on its own
  labeled space, opened and arranged for me. `⌥M` / `⌥R` minimize and restore a whole space at once.
- **yabai tiles every window automatically** (no dragging, no overlap), and **skhd moves focus by
  direction** — `⌥`+arrows to move attention, `⇧⌥`+arrows to rearrange. The mouse is the fallback,
  not the default.

The throughline: set the rules once, wire them so they hold themselves, and spend your attention
on the work — not on remembering where things are or what you decided last week.

---

*Deeper, more technical detail lives in [`claude-code.md`](claude-code.md),
[`window-management.md`](window-management.md), [`keybindings.md`](keybindings.md), and
[`shell-and-terminal.md`](shell-and-terminal.md).*
