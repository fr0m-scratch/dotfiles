---
description: Render the requested content as a self-contained HTML file and open it in THIS terminal tab. Portable — auto-detects Wave (web block), otty (`otty view` split pane, same tab), or a plain terminal (browser). Output MUST be HTML.
argument-hint: <what to render / topic — empty = the latest result in this conversation>
allowed-tools: Write, Edit, Read, Bash(mkdir:*), Bash(cat:*), Bash(bash ~/.claude/commands/lib/open-render.sh:*), Bash(otty pane list:*), Bash(otty view:*), Bash(wsh web open:*), Bash(wsh view:*), Bash(open:*)
---

The user invoked `/check`. The deliverable is **ALWAYS a single self-contained HTML file opened
in the current terminal tab** — never reply with markdown/plaintext as the deliverable. Must be HTML.
You do NOT branch on the terminal yourself — the dispatcher `~/.claude/commands/lib/open-render.sh` picks
the surface (Wave → `wsh web open`; otty → `otty view` split pane in the SAME tab; plain → browser).

Content to render: **$ARGUMENTS**
(If `$ARGUMENTS` is empty, render the most relevant current artifact/result from this conversation.)

Steps:
0. **(otty only) Resolve this session's pane** so the preview lands in THIS tab, not the GUI-focused one
   (skip on Wave/plain): `SESSION="${CODEX_COMPANION_SESSION_ID:-$CLAUDE_SESSION_ID}"`; if
   `~/.cache/otty-open/$SESSION` is absent, run `otty pane list --json`, pick the pane whose `process`
   reflects THIS session, `mkdir -p ~/.cache/otty-open` and write that pane id to the cache file. One-time
   per session; the dispatcher reads it automatically thereafter.
1. Decide what to render from `$ARGUMENTS` + current context.
2. Write ONE **self-contained** `.html` file — inline `<style>`, UTF-8, no external/CDN deps
   (no network fonts/CSS/JS), responsive, print-friendly — to an absolute path under `./.check/`:
   - `mkdir -p .check`
   - filename: `.check/<short-kebab-slug>.html`
3. Open it in THIS tab: `bash ~/.claude/commands/lib/open-render.sh "$(pwd)/.check/<short-kebab-slug>.html"`.
   The dispatcher prints `rendered <file>  (surface: wave|otty|plain)`.
4. Confirm the preview opened and state the file path + surface. On follow-up tweaks, edit the same
   HTML and re-run the dispatcher — keep everything in HTML.

Rules:
- HTML is mandatory. Single self-contained file (no external assets that need the network).
- Pass a **plain absolute path** to the dispatcher — never a `file://` URL.
- The preview opens in the **SAME tab as this session** (otty → focuses this session's pane, splits right,
  restores prior focus; never a new tab and never a different session's focused tab; Wave → web block).
- Use a clear, readable design unless the user asks for a specific style.
