---
name: open-artifact
description: Open or preview a local Markdown or HTML artifact in the best available Wave, Otty, terminal, or browser surface; optionally export Markdown to self-contained HTML. Use when the user says open, preview, show, 打开, or names a local .md, .markdown, .html, or .htm file.
---

# Open artifact

1. Resolve the requested path. If absent, choose the most recently modified Markdown or HTML file in the current directory. Stop with a clear message if none exists.
2. Accept only `.md`, `.markdown`, `.html`, or `.htm`.
3. By default, preview Markdown natively. If the user explicitly requests HTML export, use Pandoc to create a standalone, embedded-resource file under `.open/`; never modify the Markdown source.
4. Invoke the bundled dispatcher:

   ```bash
   SKILL_DIR="${OPEN_ARTIFACT_SKILL_DIR:-$HOME/.agents/skills/open-artifact}"
   bash "$SKILL_DIR/scripts/open-render.sh" "$(realpath <target>)"
   ```

5. Report the resolved file and the dispatcher's `surface:` value. On follow-up edits, reopen the same artifact.

Use plain absolute paths, not `file://` URLs. Do not open a different session's Otty pane; if `OTTY_OPEN_PANE` is available the dispatcher will target it, otherwise it uses a best-effort local preview.
