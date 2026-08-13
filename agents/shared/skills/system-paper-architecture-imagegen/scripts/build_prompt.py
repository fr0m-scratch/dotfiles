#!/usr/bin/env python3
"""Build a structured English ImageGen prompt from a validated edge ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .validate_ledger import load_and_validate
else:
    from validate_ledger import load_and_validate


def _quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def compile_prompt(data: dict[str, Any]) -> str:
    """Compile a validated ledger into an ImageGen-ready English prompt."""

    node_labels = {node["id"]: node["label"] for node in data["nodes"]}
    lines = [
        "Create a presentation-ready systems-paper architecture figure.",
        "",
        "PURPOSE",
        f"- Title, verbatim: {_quoted(data['title'])}",
        f"- Intended message: {_quoted(data['purpose'])}",
        "",
        "CANVAS",
        f"- Aspect ratio: {_quoted(data['canvas']['aspect'])}",
        f"- Background: {_quoted(data['canvas']['background'])}",
        "",
        "VISUAL STYLE",
        f"- Medium: {_quoted(data['style']['medium'])}",
        f"- Palette: {_quoted(data['style']['palette'])}",
        "",
        "SEMANTIC ZONES — draw each zone exactly once as containment, never as an arrow endpoint:",
    ]

    for zone in data["zones"]:
        lines.append(
            f"- {zone['id']}: {_quoted(zone['label'])}; semantic tone: {zone['tone']}"
        )

    lines.extend(
        [
            "",
            "NODE INVENTORY — draw each node exactly once; kind is semantic guidance only "
            "and must not be rendered:",
        ]
    )
    for node in data["nodes"]:
        kind = (
            f"; semantic kind, do not render: {_quoted(node['kind'])}"
            if node.get("kind")
            else ""
        )
        lines.append(
            f"- {node['id']}: {_quoted(node['label'])}; zone: {node['zone']}{kind}"
        )

    lines.extend(
        [
            "",
            "ONLY ALLOWED SINGLE-HEADED ARROW LEDGER — draw every listed edge exactly once "
            "and no unlisted connector:",
        ]
    )
    for edge in data["edges"]:
        edge_style = edge.get("style", "solid")
        lines.append(
            f"- {edge['id']}: {_quoted(node_labels[edge['from']])} ({edge['from']}) "
            f"— {_quoted(edge['label'])} → {_quoted(node_labels[edge['to']])} ({edge['to']}); "
            f"tone: {edge['tone']}; style: {edge_style}; place the sole arrowhead at "
            f"the receiver {edge['to']}"
        )

    lines.extend(["", "FORBIDDEN EDGES — never draw these source/receiver pairs:"])
    if data["forbidden_edges"]:
        for forbidden in data["forbidden_edges"]:
            lines.append(
                f"- {_quoted(node_labels[forbidden['from']])} ({forbidden['from']}) → "
                f"{_quoted(node_labels[forbidden['to']])} ({forbidden['to']}): "
                f"{_quoted(forbidden['reason'])}"
            )
    else:
        lines.append("- None beyond the rule that every unlisted connector is forbidden.")

    lines.extend(["", "LAYOUT REQUIREMENTS:"])
    if data["layout_notes"]:
        lines.extend(f"- {_quoted(note)}" for note in data["layout_notes"])
    else:
        lines.append("- Preserve clear routing corridors between all nodes and zones.")

    lines.extend(["", "REQUIRED TEXT — render each string verbatim:"])
    if data["required_text"]:
        lines.extend(f"- {_quoted(text)}" for text in data["required_text"])
    else:
        lines.append("- No additional required text beyond the title, labels, and caption.")

    lines.extend(
        [
            "",
            "CAPTION",
            f"- Bottom caption, verbatim: {_quoted(data['caption'])}",
            "",
            "CONNECTOR INTEGRITY — mandatory:",
            "- Every connector must correspond to exactly one ledger edge above.",
            "- Treat zone, node, and edge IDs as internal references; do not render the IDs.",
            "- Render every zone label, node label, edge label, required-text string, title, and "
            "caption verbatim.",
            "- Draw one conventional single-headed arrow per edge, with its arrowhead at the "
            "receiver and its tail visibly leaving the source.",
            "- Draw no extra connectors, no dangling connectors, no double-headed arrows, and "
            "no shared-trunk connectors.",
            "- Never terminate an arrow in whitespace, on a zone boundary, on a node that is not "
            "its receiver, or on another connector.",
            "- Route opposite-direction edges in visibly separate lanes; never merge them into a "
            "single two-way line.",
            "- Keep edge labels beside unobstructed line segments and keep arrowheads clear of all text.",
            "- If routing becomes crowded, increase whitespace or simplify node interiors; never "
            "reverse, merge, omit, duplicate, or invent an edge.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an edge ledger and compile it into an English ImageGen prompt."
    )
    parser.add_argument("ledger", type=Path, help="Path to the ledger JSON file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write the compiled prompt to this file instead of standard output",
    )
    args = parser.parse_args(argv)

    errors, warnings, data = load_and_validate(args.ledger)
    for warning in warnings:
        print(f"WARNING: {args.ledger}: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {args.ledger}: {error}", file=sys.stderr)
        return 1

    assert data is not None
    prompt = compile_prompt(data)
    if args.output is None:
        print(prompt)
        return 0

    try:
        if args.output.resolve() == args.ledger.resolve():
            print("ERROR: --output must not overwrite the input ledger", file=sys.stderr)
            return 1
        args.output.write_text(prompt + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot write {args.output}: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote ImageGen prompt to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
