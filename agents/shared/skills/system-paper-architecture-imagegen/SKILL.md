---
name: system-paper-architecture-imagegen
description: Generate presentation-ready raster systems-paper architecture figures with the built-in ImageGen tool, using a canonical directed-edge ledger and connector-by-connector visual audit. Use for ImageGen, bitmap, or PNG architecture diagrams; technical-talk schematics; trust-boundary, data-flow, learning-loop, or deployment figures; and any raster figure whose arrow sources, targets, failure paths, rollback paths, or authority boundaries must be correct. Use system-paper-architecture for deterministic SVG; do not use SVG artifacts as references for this skill.
---

# System paper architecture ImageGen

Generate raster architecture figures from semantics, not from decorative connector guesses. Keep a machine-checked ledger beside every image and treat the final PNG as a presentation layer over that ledger.

## Start from evidence

1. Read the system description, source notes, and any original raster figure.
2. Treat an existing image with suspect arrows as a component/style reference only. Do not inherit its connectors.
3. Identify actors, processes, stores, authority boundaries, lifecycle gates, and recovery targets.
4. Give each visible component a stable ID. Use a zone, band, brace, or annotation for containment; do not invent an arrow for ownership.
5. Record each visible relationship as `source — action or payload → receiver` in a JSON ledger.
6. Record forbidden bypasses explicitly. Split request and response into separately labeled, separately routed edges.

For the three Trainable Agent Runtime exemplars, read [references/trainable-agent-runtime-corrections.md](references/trainable-agent-runtime-corrections.md) and start from `assets/examples/*.json`. Use only the original PNG files under `assets/references/` as visual references. Never inspect or use SVG versions of these figures.

## Validate and compile the prompt

Run both scripts before generation:

```bash
python3 <skill-dir>/scripts/validate_ledger.py figure.json
python3 <skill-dir>/scripts/build_prompt.py figure.json
```

`validate_ledger.py` rejects unknown endpoints, duplicate IDs, self-loops, forbidden edges, unlabeled arrows, ambiguous reverse pairs, ambiguous same-direction parallel lanes, orphan nodes, and unsupported bidirectional notation. Keep warnings about figure density visible; simplify node interiors before deleting a required edge.

`build_prompt.py` emits an ImageGen-ready prompt containing the exact node inventory, arrow ledger, forbidden bypasses, semantic rules, and visual language. Pass the prompt verbatim unless the user changes the content.

## Generate with ImageGen

- Use the built-in `image_gen` tool in `infographic-diagram` mode.
- Generate one distinct figure per call.
- When a local PNG is a reference, inspect it first with `view_image`, then pass its path as a reference image. State that it supplies visual language and component inventory only; the JSON ledger owns topology and direction.
- Use 16:9 landscape, near-white paper, thin marker-like linework, flat boxes, and restrained semantic colors.
- Use red for control or learning, blue for execution or serving, green for assurance or governance, and purple for offline optimization.
- Draw every ledger edge exactly once and draw no unlisted connector. Put one conventional arrowhead only at the receiver.
- Route opposite-direction request/response edges in visibly separate lanes. Never use double-headed arrows, shared trunks, decorative arrows, dangling lines, or endpoints on zone borders.
- Keep labels beside clear segments, never beneath an arrowhead or across a node label.
- Save project-bound outputs in the project or the skill's `assets/examples/`; do not leave them only in the generated-images cache.

## Audit every arrow

Inspect the final raster at original resolution and in close crops. For every visible connector:

1. Find its ledger ID.
2. Read it aloud as `source — label → receiver`.
3. Confirm the tail leaves the source and the arrowhead touches the receiver.
4. Confirm the line does not terminate in whitespace, on a boundary, or on another edge.
5. Confirm request/response, append/replay, and effect/result pairs occupy separate lanes.
6. Confirm failure reaches recovery, rollback, quarantine, prior version, or stop—never commit.
7. Confirm context read paths never become effect write paths.
8. Confirm learned components never bypass an authority, policy, evaluation, conformance, or release gate.
9. Confirm rollback names a known-good target.
10. Confirm no extra arrow exists outside the ledger.

If any connector fails, use ImageGen edit mode for one targeted correction and restate every invariant that must remain unchanged. Reinspect the entire figure after the edit. If edits drift or the graph stays ambiguous, regenerate from a simpler layout; never repair the bitmap manually.

## Non-negotiable semantics

- Generators propose; independent assurance accepts or rejects.
- A failed check cannot advance toward commit or release.
- Raw evidence is append-only; derived views and policies are versioned and rebuildable.
- A ContextPacket is read context, never effect authority.
- Models and learned modules emit intents or proposals; an effect kernel or capability broker owns authorization and commit.
- Optimizers consume governed evidence and publish only through evaluation, constraints, canary, signed release, and rollback.
- The primary event direction is producer/authority to append-only log. Replay is a separate, labeled reverse edge.

## Deliver

Deliver the final PNG, its JSON ledger, the exact compiled prompt, and a short statement of any assumptions. Do not claim arrow integrity until the ledger validator passes and the raster has been audited edge by edge.
