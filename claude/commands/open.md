---
description: Open a Markdown or HTML file in THIS WaveTerm tab. Markdown opens in WaveTerm's native Markdown renderer by default (no HTML conversion); HTML opens as-is. Pass `html` to force the old pandoc→self-contained-HTML export.
model: haiku
argument-hint: <path to a .md or .html file — empty = most recent in cwd> [html]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), Bash(pandoc:*), Bash(wsh view:*), Bash(wsh web open:*), Bash(realpath:*), Bash(basename:*)
---

The user invoked `/open`. Render the target file **in the current WaveTerm tab**.
For Markdown the default render path is **WaveTerm's native Markdown renderer** (`wsh view`) — NOT an HTML
conversion. HTML files open directly as a web block.

Target: **$ARGUMENTS**
(`$ARGUMENTS` may end with the literal word `html` as a flag — strip it off first; what remains is the path.
If the path part is empty, pick the most recently modified `.md`/`.markdown`/`.html`/`.htm` in cwd:
`ls -t *.md *.markdown *.html *.htm 2>/dev/null | head -1`. If still nothing, tell the user and stop.)

Steps:
1. Parse args: detect a trailing `html` flag (→ `FORCE_HTML=1`), the rest is the path. Resolve the path to
   an **absolute path** (`realpath`). If it doesn't exist, say so and stop.
2. Branch on the extension:
   - **`.md` / `.markdown`** (default) → open in the native Markdown renderer, no conversion, no temp files:
     `wsh view "<abs-md>"`
     (WaveTerm renders the Markdown itself, with a rendered/source toggle; relative links to sibling
     `.md` files stay navigable. Add `-m` for a magnified block if the user asks for a bigger view.)
   - **`.md` / `.markdown` WITH the `html` flag** → the legacy export path: convert to a **self-contained**
     HTML via pandoc, then open it as a web block:
     - `mkdir -p .open`
     - Write the style header below to `./.open/_style.html` (once; reuse if present).
     - `pandoc "<abs-md>" -f gfm -t html5 --standalone --embed-resources \
         --include-in-header ./.open/_style.html --metadata title="<basename>" \
         -o "./.open/<slug>.html"`  (slug = kebab of the filename)
     - `wsh web open "file://$(pwd)/.open/<slug>.html"`
   - **`.html` / `.htm`** → open directly as a web block, no conversion:
     `wsh web open "file://<abs-path>"`
   - Any other extension → tell the user `/open` handles `.md` and `.html` only.
3. Confirm the block opened and print which file was rendered and via which path (native Markdown renderer
   vs HTML export vs web). On follow-up edits to a Markdown source opened with the native renderer, just
   re-run `wsh view`; for the `html` export path, re-run pandoc on the same output and re-open.

Rules:
- Default Markdown render path is the **native WaveTerm Markdown renderer** (`wsh view`). Only convert to
  HTML when the user explicitly passes `html`. If `wsh` is missing, say so — this command needs WaveTerm.
- The `html` export must stay self-contained (inline `<style>`, `--embed-resources`, no network/CDN).
- Keep any generated HTML under `./.open/`. Never modify the user's source `.md`/`.html`.

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
