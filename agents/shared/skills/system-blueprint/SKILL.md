---
name: system-blueprint
description: Produce a self-contained HTML architecture blueprint with precise hand-laid SVG diagrams, named interfaces, sequence flows, deployment topology, decision tables, and implementation steps. Use for architecture diagrams, system designs, reference architectures, swimlanes, deployment diagrams, 系统架构, 时序图, 系统蓝图, or 部署图.
---

# System blueprint

Create one standalone HTML file with inline CSS and SVG, zero external assets, and no runtime JavaScript. The document must explain a system, not merely decorate boxes.

## Evidence first

1. Identify actors, trust zones, components, data stores, interfaces, deployment units, and unresolved decisions from source material.
2. Mark facts, design choices, assumptions, and open questions distinctly. Never promote an assumption into an implemented fact.
3. Define a finite vocabulary of named actions such as `commit`, `compile`, `fetch`, `dispatch`, and `render`. Reuse each name consistently across diagrams and tables.

## Required document

- Header: system name, one-sentence purpose, scope/status disclaimer.
- Context: current pain, desired outcome, and governing principles.
- Figure A: zone/container architecture.
- Figure B: end-to-end swimlane sequence.
- Figure C: runtime/deployment topology and trust boundaries.
- Interface matrix: name, caller, callee, contract, authentication, failure behavior, maturity.
- Decision-space table: fixed choice, open choice, trade-off, evidence needed, owner.
- Implementation plan: dependency-ordered steps tied back to interfaces.

## Drawing grammar

- Use an SVG `viewBox` around 1300 pixels wide and fixed hand-laid coordinates; do not use Mermaid, Graphviz, or auto-layout.
- Give every trust zone a quiet tinted container. Reserve clear corridors for cross-zone arrows.
- Map one restrained color family to each domain. Color encodes ownership or action semantics, never decoration.
- Draw one straight cross-zone arrow per named action at a unique coordinate. Avoid bends and crossings; docking points must reveal topology.
- Put the action number/name and `caller -> callee` contract beside the arrow. Repeat the same vocabulary in the legend, sequence, matrix, and plan.
- Use hierarchy through scale, weight, and whitespace. Keep labels readable at 100% zoom and in print.
- Include `role="img"` and meaningful `aria-label` on diagrams.

## Visual baseline

Use system fonts, white panels on a cool neutral canvas, hairline borders, 8px spacing increments, 12–20px radii, and restrained shadows. Avoid neon, decorative gradients, glow, glassmorphism, emoji-as-icons, and arbitrary color. Bilingual documents may use Chinese narrative with stable English technical terms.

## Verification

1. Validate HTML/SVG syntax and check for external URLs.
2. Render a full-page screenshot plus close crops of each diagram.
3. Inspect for clipped labels, overlapping arrows, illegible text, inconsistent action names, and unsupported claims.
4. Verify print layout and that every component/action in prose appears in at least one diagram or table.
5. Iterate until a fresh review finds no material problem.
