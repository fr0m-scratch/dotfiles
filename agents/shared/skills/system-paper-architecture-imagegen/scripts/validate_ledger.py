#!/usr/bin/env python3
"""Validate a directed-edge ledger for an ImageGen architecture figure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ALLOWED_TONES = {"ink", "red", "blue", "green", "purple"}
ALLOWED_EDGE_STYLES = {"solid", "dashed"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "title",
    "purpose",
    "caption",
    "canvas",
    "style",
    "zones",
    "nodes",
    "edges",
    "forbidden_edges",
    "layout_notes",
    "required_text",
)
ALLOWED_FIELDS = {
    "canvas": {"aspect", "background"},
    "style": {"medium", "palette"},
    "zone": {"id", "label", "tone"},
    "node": {"id", "label", "zone", "kind"},
    "edge": {"id", "from", "to", "label", "tone", "style"},
    "forbidden_edge": {"from", "to", "reason"},
}
FORBIDDEN_DIRECTION_SYMBOLS = ("<->", "↔", "⇄", "⇆", "⇔", "⟷", "⟺")
FORBIDDEN_DIRECTION_WORDS = re.compile(
    r"\b(?:bi[- ]?directional(?:ly)?|double[- ]?headed|both directions|both ways|two[- ]?way)\b",
    re.IGNORECASE,
)
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")


class DuplicateJsonKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_fields(
    item: dict[str, Any], required: tuple[str, ...], location: str, errors: list[str]
) -> None:
    missing = [field for field in required if field not in item]
    if missing:
        errors.append(f"{location}: missing required fields: {', '.join(missing)}")


def _reject_unknown_fields(
    item: dict[str, Any], allowed: set[str], location: str, errors: list[str]
) -> None:
    unknown = sorted(set(item) - allowed)
    if unknown:
        errors.append(f"{location}: unknown fields: {', '.join(unknown)}")


def _validate_string_list(value: Any, location: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{location} must be an array of non-empty strings")
        return
    for index, item in enumerate(value):
        if not _is_non_empty_string(item):
            errors.append(f"{location}[{index}] must be a non-empty string")


def _contains_bidirectional_notation(label: str) -> bool:
    return bool(FORBIDDEN_DIRECTION_WORDS.search(label)) or any(
        symbol in label for symbol in FORBIDDEN_DIRECTION_SYMBOLS
    )


def validate(data: dict[str, Any], source: str = "<ledger>") -> tuple[list[str], list[str]]:
    """Return validation errors and non-fatal warnings for one parsed ledger."""

    del source  # Kept in the public signature for callers that track source paths.
    errors: list[str] = []
    warnings: list[str] = []

    missing_top_level = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in data]
    if missing_top_level:
        errors.append(f"missing top-level fields: {', '.join(missing_top_level)}")
    _reject_unknown_fields(data, set(REQUIRED_TOP_LEVEL_FIELDS), "top level", errors)

    for field in ("title", "purpose", "caption"):
        if field in data and not _is_non_empty_string(data[field]):
            errors.append(f"{field} must be a non-empty string")

    canvas = data.get("canvas")
    if canvas is not None:
        if not isinstance(canvas, dict):
            errors.append("canvas must be an object")
        else:
            _require_fields(canvas, ("aspect", "background"), "canvas", errors)
            _reject_unknown_fields(canvas, ALLOWED_FIELDS["canvas"], "canvas", errors)
            for field in ("aspect", "background"):
                if field in canvas and not _is_non_empty_string(canvas[field]):
                    errors.append(f"canvas.{field} must be a non-empty string")

    style = data.get("style")
    if style is not None:
        if not isinstance(style, dict):
            errors.append("style must be an object")
        else:
            _require_fields(style, ("medium", "palette"), "style", errors)
            _reject_unknown_fields(style, ALLOWED_FIELDS["style"], "style", errors)
            for field in ("medium", "palette"):
                if field in style and not _is_non_empty_string(style[field]):
                    errors.append(f"style.{field} must be a non-empty string")

    global_ids: dict[str, str] = {}

    def register_id(value: Any, location: str) -> str | None:
        if not _is_non_empty_string(value):
            errors.append(f"{location}.id must be a non-empty string")
            return None
        identifier = value.strip()
        if identifier != value:
            errors.append(f"{location}.id must not have leading or trailing whitespace")
        if not ID_PATTERN.fullmatch(identifier):
            errors.append(
                f"{location}.id must use only letters, digits, dot, underscore, colon, slash, or hyphen"
            )
        previous = global_ids.get(identifier)
        if previous is not None:
            errors.append(f"duplicate id {identifier!r}: {previous} and {location}")
        else:
            global_ids[identifier] = location
        return identifier

    zones = data.get("zones", [])
    known_zones: set[str] = set()
    if not isinstance(zones, list):
        errors.append("zones must be an array")
        zones = []
    elif not zones:
        errors.append("zones must contain at least one zone")
    for index, zone in enumerate(zones):
        location = f"zones[{index}]"
        if not isinstance(zone, dict):
            errors.append(f"{location} must be an object")
            continue
        _require_fields(zone, ("id", "label", "tone"), location, errors)
        _reject_unknown_fields(zone, ALLOWED_FIELDS["zone"], location, errors)
        zone_id = register_id(zone.get("id"), location)
        if zone_id is not None:
            known_zones.add(zone_id)
        if "label" in zone and not _is_non_empty_string(zone["label"]):
            errors.append(f"{location}.label must be a non-empty string")
        tone = zone.get("tone")
        if tone not in ALLOWED_TONES:
            errors.append(
                f"{location}.tone must be one of {', '.join(sorted(ALLOWED_TONES))}; got {tone!r}"
            )

    nodes = data.get("nodes", [])
    known_nodes: set[str] = set()
    if not isinstance(nodes, list):
        errors.append("nodes must be an array")
        nodes = []
    elif not nodes:
        errors.append("nodes must contain at least one node")
    for index, node in enumerate(nodes):
        location = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{location} must be an object")
            continue
        _require_fields(node, ("id", "label", "zone"), location, errors)
        _reject_unknown_fields(node, ALLOWED_FIELDS["node"], location, errors)
        node_id = register_id(node.get("id"), location)
        if node_id is not None:
            known_nodes.add(node_id)
        if "label" in node and not _is_non_empty_string(node["label"]):
            errors.append(f"{location}.label must be a non-empty string")
        zone_id = node.get("zone")
        if not _is_non_empty_string(zone_id):
            errors.append(f"{location}.zone must be a non-empty string")
        else:
            if zone_id != zone_id.strip():
                errors.append(f"{location}.zone must not have leading or trailing whitespace")
            if zone_id.strip() not in known_zones:
                errors.append(f"{location}.zone references unknown zone {zone_id!r}")
        if "kind" in node and not _is_non_empty_string(node["kind"]):
            errors.append(f"{location}.kind must be a non-empty string when provided")

    edges = data.get("edges", [])
    actual_pairs: set[tuple[str, str]] = set()
    edge_signatures: dict[tuple[str, str, str], str] = {}
    if not isinstance(edges, list):
        errors.append("edges must be an array")
        edges = []
    elif not edges:
        errors.append("edges must contain at least one directed edge")
    for index, edge in enumerate(edges):
        location = f"edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{location} must be an object")
            continue
        _require_fields(edge, ("id", "from", "to", "label", "tone"), location, errors)
        _reject_unknown_fields(edge, ALLOWED_FIELDS["edge"], location, errors)
        edge_id = register_id(edge.get("id"), location)

        source_id = edge.get("from")
        target_id = edge.get("to")
        valid_source = _is_non_empty_string(source_id)
        valid_target = _is_non_empty_string(target_id)
        if not valid_source:
            errors.append(f"{location}.from must be a non-empty string")
        else:
            if source_id != source_id.strip():
                errors.append(f"{location}.from must not have leading or trailing whitespace")
            if source_id.strip() not in known_nodes:
                errors.append(f"{location}.from references unknown node {source_id!r}")
        if not valid_target:
            errors.append(f"{location}.to must be a non-empty string")
        else:
            if target_id != target_id.strip():
                errors.append(f"{location}.to must not have leading or trailing whitespace")
            if target_id.strip() not in known_nodes:
                errors.append(f"{location}.to references unknown node {target_id!r}")
        if valid_source and valid_target:
            source_id = source_id.strip()
            target_id = target_id.strip()
            if source_id == target_id:
                errors.append(f"{location}: from and to must differ")
            actual_pairs.add((source_id, target_id))

        label = edge.get("label")
        if not _is_non_empty_string(label):
            errors.append(f"{location}.label must be a non-empty action or payload")
        else:
            label = label.strip()
            if _contains_bidirectional_notation(label):
                errors.append(
                    f"{location}.label contains forbidden bidirectional/double-headed notation"
                )
            if valid_source and valid_target:
                signature = (source_id.strip(), target_id.strip(), label)
                previous = edge_signatures.get(signature)
                if previous is not None:
                    errors.append(
                        f"{location}: duplicate directed edge from/to/label; first declared by {previous}"
                    )
                else:
                    edge_signatures[signature] = edge_id or location

        tone = edge.get("tone")
        if tone not in ALLOWED_TONES:
            errors.append(
                f"{location}.tone must be one of {', '.join(sorted(ALLOWED_TONES))}; got {tone!r}"
            )
        edge_style = edge.get("style", "solid")
        if edge_style not in ALLOWED_EDGE_STYLES:
            errors.append(
                f"{location}.style must be one of {', '.join(sorted(ALLOWED_EDGE_STYLES))}; "
                f"got {edge_style!r}"
            )

    forbidden_edges = data.get("forbidden_edges", [])
    forbidden_pairs: set[tuple[str, str]] = set()
    if not isinstance(forbidden_edges, list):
        errors.append("forbidden_edges must be an array")
        forbidden_edges = []
    for index, forbidden in enumerate(forbidden_edges):
        location = f"forbidden_edges[{index}]"
        if not isinstance(forbidden, dict):
            errors.append(f"{location} must be an object")
            continue
        _require_fields(forbidden, ("from", "to", "reason"), location, errors)
        _reject_unknown_fields(
            forbidden, ALLOWED_FIELDS["forbidden_edge"], location, errors
        )
        source_id = forbidden.get("from")
        target_id = forbidden.get("to")
        if not _is_non_empty_string(source_id):
            errors.append(f"{location}.from must be a non-empty string")
        else:
            if source_id != source_id.strip():
                errors.append(f"{location}.from must not have leading or trailing whitespace")
            if source_id.strip() not in known_nodes:
                errors.append(f"{location}.from references unknown node {source_id!r}")
        if not _is_non_empty_string(target_id):
            errors.append(f"{location}.to must be a non-empty string")
        else:
            if target_id != target_id.strip():
                errors.append(f"{location}.to must not have leading or trailing whitespace")
            if target_id.strip() not in known_nodes:
                errors.append(f"{location}.to references unknown node {target_id!r}")
        if not _is_non_empty_string(forbidden.get("reason")):
            errors.append(f"{location}.reason must be a non-empty string")
        if _is_non_empty_string(source_id) and _is_non_empty_string(target_id):
            pair = (source_id.strip(), target_id.strip())
            if pair in forbidden_pairs:
                errors.append(
                    f"{location}: duplicate forbidden edge {pair[0]!r} -> {pair[1]!r}"
                )
            forbidden_pairs.add(pair)

    for source_id, target_id in sorted(actual_pairs & forbidden_pairs):
        errors.append(f"edge {source_id!r} -> {target_id!r} matches forbidden_edges")

    if "layout_notes" in data:
        _validate_string_list(data["layout_notes"], "layout_notes", errors)
    if "required_text" in data:
        _validate_string_list(data["required_text"], "required_text", errors)

    if len(edges) > 36:
        warnings.append(
            f"{len(edges)} visible edges may be too dense for reliable ImageGen routing"
        )

    return errors, warnings


def load_and_validate(path: Path) -> tuple[list[str], list[str], dict[str, Any] | None]:
    """Load one JSON ledger and return errors, warnings, and parsed data."""

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except OSError as exc:
        return [f"cannot read ledger: {exc}"], [], None
    except UnicodeDecodeError as exc:
        return [f"ledger is not valid UTF-8: {exc}"], [], None
    except (json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        return [f"invalid JSON: {exc}"], [], None
    if not isinstance(data, dict):
        return [f"{path}: top-level JSON must be an object"], [], None
    errors, warnings = validate(data, str(path))
    return errors, warnings, data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an ImageGen architecture edge-ledger JSON file."
    )
    parser.add_argument("ledger", type=Path, help="Path to the ledger JSON file")
    args = parser.parse_args(argv)

    errors, warnings, data = load_and_validate(args.ledger)
    for warning in warnings:
        print(f"WARNING: {args.ledger}: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {args.ledger}: {error}", file=sys.stderr)
        return 1

    assert data is not None
    print(
        f"OK: {args.ledger} "
        f"({len(data['zones'])} zones, {len(data['nodes'])} nodes, "
        f"{len(data['edges'])} directed edges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
