---
description: Compile a very formal / official technical document (ICD, specification, RFC, 规范, 正式技术文档) to a print-grade PDF via LaTeX (pandoc → xelatex, full CJK, zero decoration).
argument-hint: <topic / source content — empty = the latest spec/result in this conversation>
---

Read `~/.claude/skills/latex/SKILL.md` and follow its procedure exactly to produce a **formal,
LaTeX-compiled PDF**. The deliverable is a print-grade `.pdf` (formal register: numbered sections, a
table of contents, RFC-2119 keywords where normative, full CJK, **no emoji / no flourish / no
decoration**) plus its `.md` source. Compile with the bundled `build_pdf.sh`, then **verify the render**
(PDF → PNG → Read the image) to confirm no table/code overflow before delivering.

Content / topic for this document:

$ARGUMENTS

(If `$ARGUMENTS` is empty, compile the most relevant current spec/artifact from this conversation.)
