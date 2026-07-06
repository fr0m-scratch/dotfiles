---
description: Open a Markdown or HTML file in THIS terminal. Portable — auto-detects Wave (native Markdown/web block), otty (`otty view` pane), or a plain terminal (browser / `glow`). Markdown renders natively (no HTML conversion); pass `html` to force the pandoc→self-contained-HTML export.
model: haiku
argument-hint: <path to a .md or .html file — empty = most recent in cwd> [html]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), Bash(cat:*), Bash(pandoc:*), Bash(realpath:*), Bash(basename:*), Bash(bash ~/.claude/commands/lib/open-render.sh:*), Bash(otty pane list:*), Bash(otty view:*), Bash(wsh view:*), Bash(wsh web open:*), Bash(open:*), Bash(glow:*)
---

The user invoked `/open`. Render the target file **in the current terminal**, using whatever preview
surface it offers. You do NOT branch on the terminal yourself — the dispatcher
`~/.claude/commands/lib/open-render.sh` does that (Wave → `wsh view`/`wsh web open`; otty → `otty view`;
plain terminal → `open` in the browser for HTML, `glow` for Markdown). Your job is to pick the right
**target file** and hand it to the dispatcher.

Target: **$ARGUMENTS**
(`$ARGUMENTS` may end with the literal word `html` as a flag — strip it off first; what remains is the path.
If the path part is empty, pick the most recently modified `.md`/`.markdown`/`.html`/`.htm` in cwd:
`ls -t *.md *.markdown *.html *.htm 2>/dev/null | head -1`. If still nothing, tell the user and stop.)

Steps:
0. **(otty only) Resolve this session's pane** so the preview lands in THIS tab — never the GUI-focused
   one (in a multi-session fleet the focused pane is usually a *different* session). Skip on Wave/plain.
   - `SESSION="${CODEX_COMPANION_SESSION_ID:-$CLAUDE_SESSION_ID}"`; cache file = `~/.cache/otty-open/$SESSION`.
   - If that cache file already exists, do nothing — the dispatcher reads it automatically.
   - Else identify your OWN pane: `otty pane list --json`, pick the pane whose `process` field reflects
     THIS session's current task, `mkdir -p ~/.cache/otty-open` and write just that pane id (e.g.
     `p_19f3697312d_8`) to the cache file. One-time per session — otty gives a background process no way
     to self-identify, so it needs your judgment once; after that every `/open` + `/check` here is pinned.
1. Parse args: detect a trailing `html` flag (→ `FORCE_HTML=1`); the rest is the path. Resolve it to an
   **absolute path** (`realpath`). If it doesn't exist, say so and stop.
2. Decide the **target file** to render:
   - **`.md` / `.markdown`** (default) → target = the Markdown file itself. No conversion, no temp files —
     each surface renders Markdown natively (Wave's Markdown renderer / `otty view` / `glow`).
   - **`.md` / `.markdown` WITH the `html` flag** → the legacy export path: convert to a **self-contained**
     HTML first, then that HTML is the target:
     - `mkdir -p .open`
     - Write the style header below to `./.open/_style.html` (once; reuse if present).
     - `pandoc "<abs-md>" -f gfm -t html5 --standalone --embed-resources \
         --include-in-header ./.open/_style.html --metadata title="<basename>" \
         -o "./.open/<slug>.html"`  (slug = kebab of the filename); target = `./.open/<slug>.html`.
   - **`.html` / `.htm`** → target = the HTML file itself.
   - Any other extension → tell the user `/open` handles `.md` and `.html` only, and stop.
3. Render it: `bash ~/.claude/commands/lib/open-render.sh "<abs-target>"`.
   The dispatcher prints `rendered <file>  (surface: wave|otty|plain)`.
4. Confirm to the user which file was rendered and on which surface (echo the dispatcher's `surface:` line).
   On follow-up edits: for a natively-rendered Markdown file just re-run the dispatcher on the same path;
   for the `html` export path, re-run pandoc on the same output file, then re-run the dispatcher.

Rules:
- Default Markdown render path is **native** (no HTML). Only convert to HTML when the user passes `html`.
- Never pass a `file://` URL — the dispatcher takes a plain absolute path.
- The `html` export must stay self-contained (inline `<style>`, `--embed-resources`, no network/CDN).
- Keep any generated HTML under `./.open/`. Never modify the user's source `.md`/`.html`.
- The preview always opens in the **SAME tab as this session** — never a new tab, never the GUI-focused
  tab. On otty the dispatcher focuses this session's pane (from the cache in Step 0), splits it `--right`,
  renders, then restores the user's prior focus (so a background `/open` doesn't yank them off their
  current tab; set `OTTY_OPEN_KEEP_FOCUS=1` to stay on the preview instead). On Wave it's a block in the
  current tab. If the dispatcher reports `surface: plain` and there's no `open`/`glow`, it prints the path.

`./.open/_style.html` (only needed for the `html` export path — GitHub-ish, light+dark, print-friendly — write verbatim):
```html
<style>
:root{color-scheme:light dark}
body{max-width:860px;margin:40px auto;padding:0 20px;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#1f2328;background:#fff}
@media(prefers-color-scheme:dark){body{color:#e6edf3;background:#0d1117}a{color:#4493f8}code,pre{background:#161b22}hr{border-color:#30363d}blockquote{color:#9198a1;border-color:#30363d}table td,table th{border-color:#30363d}}
h1,h2{border-bottom:1px solid #d1d9e0;padding-bottom:.3em}
a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}
code{background:#eff1f3;padding:.2em .4em;border-radius:6px;font:.9em ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:#eff1f3;padding:16px;border-radius:8px;overflow:auto}pre code{background:none;padding:0}
blockquote{margin:0;padding:0 1em;color:#59636e;border-left:.25em solid #d1d9e0}
table{border-collapse:collapse}table td,table th{border:1px solid #d1d9e0;padding:6px 13px}
img{max-width:100%}
</style>
```
