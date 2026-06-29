---
name: latex
description: Compile a very formal, official technical document (interface control document / specification / RFC / 技术规范 / 正式技术文档) to a print-grade PDF via LaTeX (pandoc → xelatex/xeCJK), with full CJK (中文) support. Use when the user wants a serious, no-flourish, no-decoration formal document as a shareable PDF — specs, ICDs, standards, 规范/标准/正式文档. NOT for marketing/sales one-pagers (use apple-sales-doc) and NOT for viewable HTML artifacts (use /check or /open).
---

# latex — formal Markdown → PDF (LaTeX)

Produce a **serious, official technical document** as a PDF compiled with `xelatex`. Dry, normative
register; **zero decoration**. Full CJK. The deliverable is a print-grade `.pdf` plus its `.md` source.

## When to use
- Interface control documents (ICDs), specifications, RFC-style normative docs, 技术规范 / 标准 /
  正式技术文档 that must be a polished, shareable, print-grade PDF.
- **NOT** marketing/pitch one-pagers → use `apple-sales-doc`. **NOT** a viewable web artifact →
  use `/check` (HTML) or `/open`.

## Hard rules
- **Compile with the bundled script** `~/.claude/skills/latex/build_pdf.sh` (pandoc → xelatex +
  xeCJK). Do not hand-roll LaTeX unless the document genuinely needs custom macros.
- **Formal register**: numbered sections, a table of contents, **RFC 2119** keywords
  (MUST / SHOULD / MAY) where statements are normative, and **no emoji, no marketing language, no
  flourish**. Restrained and factual.
- **Start with a document-control block** at the top of the markdown: Doc ID · Version · Status ·
  Classification · Date (a small table or definition list).
- **CJK**: Songti (宋体) serif as the main CJK face (formal), Menlo monospace for code. The script
  auto-picks an installed font; override with `CJK_FONT` / `MONO_FONT` env vars if needed.
- **Compile-safety (avoid page overflow / xelatex errors):**
  - Write comparison operators in ASCII — `<=`, `>=`, `->` — **not** `≤` `≥` `→` (glyphs may be
    missing from the mono/CJK font and break or render as tofu).
  - Keep tables to **≤ 4 columns**; move long prose out of cells.
  - **Long monospace tokens (paths, dedup keys, URLs) go in fenced code blocks, NOT table cells** —
    code blocks line-wrap (fvextra), table cells do not, so a long token overflows the page.
  - Backtick or escape LaTeX-special characters in inline code.

## Procedure
1. **Write / refine the content as Markdown** (the document body). Pick a Doc ID and Version.
   Use `## `/`### ` headings (they become numbered sections + the TOC).
2. **Compile:**
   ```bash
   bash ~/.claude/skills/latex/build_pdf.sh <in.md> <out.pdf> "<Title>" "<Subtitle>" "<DocID>" "<Version>"
   ```
   (Title/Subtitle/DocID/Version are optional but recommended; they fill the title block + header.)
3. **VERIFY before delivering (self-check).** Render the PDF to PNG and **Read the image** to confirm
   there is no table/code overflow and the formatting is clean — check page 1 **and** a dense
   table/code page:
   ```bash
   pdftoppm -png -f 1 -l 1 -r 90 <out.pdf> /tmp/lpg && # then Read /tmp/lpg-1.png
   ```
   If anything overflows: narrow the table, move long tokens into a code block, ASCII-ize `≤`/`→`,
   then recompile. Iterate until clean.
4. **Deliver** the `.pdf` path. Keep the `.md` source beside it so the doc can be revised + recompiled.

## Dependencies (check first; instruct the user if missing — do not silently fail)
- **pandoc** — `brew install pandoc`
- **TinyTeX (xelatex)** — install from https://yihui.org/tinytex/ , then add the needed packages:
  `tlmgr install fvextra fancyhdr sectsty lineno footnotehyper xurl`
- **poppler** (for the verify step's `pdftoppm`) — `brew install poppler`

## Notes
- `build_pdf.sh` auto-locates a TinyTeX install, picks a CJK serif (Songti SC → Noto Serif CJK
  fallback) and mono (Menlo → DejaVu Sans Mono), emits a numbered TOC, A4 with 2.4 cm margins, a
  header (Doc ID + page) and a footer (status, default "Draft" — override via `FOOTER` env), and
  monochrome code highlighting. It is stdlib-of-the-shell only — no Python, no extra deps.
- **Pairs with `/check`**: use `/latex` when the deliverable must be a formal **PDF**; use `/check`
  when it's a viewable **HTML** artifact in WaveTerm.
