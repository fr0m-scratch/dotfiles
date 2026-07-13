---
name: pptx
description: Create, inspect, edit, or validate PowerPoint presentations and .pptx files using ordinary open tooling and visual QA. Use whenever the user mentions a deck, slides, presentation, template, speaker notes, or a .pptx input/output.
---

# PowerPoint workflow

This is a clean-room portable workflow. It intentionally contains no copied Claude/Anthropic PPTX skill materials.

## Inspect an existing deck

1. Preserve the original and work on a copy unless the user explicitly requests in-place editing.
2. Extract text and metadata with an available local tool such as `python -m markitdown`, `python-pptx`, or direct OOXML inspection via `unzip`.
3. Render the deck to PDF with LibreOffice, then render PDF pages to images with Poppler.
4. Inspect every slide image for clipping, overlap, weak contrast, inconsistent alignment, missing assets, and stale placeholders.
5. Inventory layouts, theme fonts/colors, masters, image relationships, notes, and external links before changing structure.

## Edit

- Prefer the deck's original source generator when one exists.
- For ordinary edits, use `python-pptx` or a carefully scoped OOXML change. For generated decks, use a source-controlled generator such as PptxGenJS.
- Preserve masters, theme, slide dimensions, notes, accessibility text, and relationship targets unless the task explicitly changes them.
- Do not rasterize editable text/charts merely to make an edit easier.
- Set author metadata to the user or issuing organization, never an AI system.

## Create

1. Agree on audience, decision goal, slide count, language, brand constraints, and evidence sources.
2. Write a slide-by-slide narrative before layout: one claim per slide, supporting evidence, and the visual that proves it.
3. Use a consistent 16:9 master unless another format is required. Define theme fonts, palette, margins, grid, title hierarchy, and footer once.
4. Use diagrams, charts, real product images, or structured comparison visuals. Avoid decorative filler and unsupported numbers.
5. Keep editable source code/data beside the generated `.pptx` so future edits are reproducible.

## Required QA loop

1. Validate the ZIP container with `unzip -t` and open/convert it with LibreOffice.
2. Extract text to catch omissions, ordering errors, and placeholders.
3. Render all slides to images and visually inspect them at normal size.
4. Fix every material issue, rerender affected slides, and repeat until a complete pass finds no new problem.
5. Report dependencies that were unavailable rather than claiming unperformed validation.

Typical dependencies are Python 3.10+, `python-pptx`, optional `markitdown[pptx]`, LibreOffice, Poppler, and optionally PptxGenJS. Do not install them without the authorization appropriate to the parent task.
