---
description: Render the requested content as a self-contained HTML file and open it in THIS WaveTerm tab (wave web). Output MUST be HTML.
argument-hint: <what to render / topic — empty = the latest result in this conversation>
allowed-tools: Write, Edit, Read, Bash(mkdir:*), Bash(wsh web open:*), Bash(wsh view:*)
---

The user invoked `/check`. The deliverable is **ALWAYS a single self-contained HTML file opened
in the current WaveTerm tab** — never reply with markdown/plaintext as the deliverable. Must be HTML.

Content to render: **$ARGUMENTS**
(If `$ARGUMENTS` is empty, render the most relevant current artifact/result from this conversation.)

Steps:
1. Decide what to render from `$ARGUMENTS` + current context.
2. Write ONE **self-contained** `.html` file — inline `<style>`, UTF-8, no external/CDN deps
   (no network fonts/CSS/JS), responsive, print-friendly — to an absolute path under `./.check/`:
   - `mkdir -p .check`
   - filename: `.check/<short-kebab-slug>.html`
3. Open it in THIS tab (absolute path, `file://` URL):
   - `wsh web open "file://$(pwd)/.check/<short-kebab-slug>.html"`
4. Confirm the web block was created and state the file path. On follow-up tweaks, edit the same
   HTML and re-open — keep everything in HTML.

Rules:
- HTML is mandatory; the render path is `wsh web open` (WaveTerm). If `wsh` is missing, say so —
  this command requires WaveTerm.
- Single self-contained file (no external assets that need the network).
- Use a clear, readable design unless the user asks for a specific style.
