#!/usr/bin/env python3
"""Codex PreToolUse guard for durable fr0m invariants.

Codex currently cannot implement Claude's permissionDecision=ask. Existing
Principal.md files are therefore hard-blocked for agent writes; the user can
edit them manually or explicitly disable/trust-adjust this hook for that edit.
Hooks are guardrails, not a complete security boundary; Git/CI must enforce
repository policy independently.
"""

import json
import os
import re
import sys


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    raise SystemExit(0)


def governed(cwd: str) -> bool:
    path = os.path.abspath(cwd)
    while True:
        if os.path.isfile(os.path.join(path, "Principal.md")):
            return True
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def targets_existing_governance_file(patch: str, basename: str) -> bool:
    header = re.compile(r"^\*\*\* (?:Update|Delete) File: (.+)$", re.MULTILINE)
    return any(os.path.basename(path.strip()) == basename for path in header.findall(patch))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    cwd = data.get("cwd") or os.getcwd()
    if not governed(cwd):
        return

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command", "") or ""
    low = command.lower()

    if tool == "Bash":
        if "git commit" in low and (
            re.search(r"co-authored-by:\s*\S*\s*(claude|codex|openai)", low)
            or re.search(r"generated with.*(claude|codex|openai)", low)
            or "claude code" in low
            or "🤖" in command
        ):
            deny("AI co-authorship and generated-by commit trailers are not allowed.")

        if "aol.md" in low:
            rewrite = (
                re.search(r"(^|[^>])>\s*[^>|]*aol\.md", low)
                or re.search(r"\bsed\b.*-i", low)
                or re.search(r"\btruncate\b", low)
                or re.search(r"\b(dd|cp|mv|install)\b.*aol\.md", low)
                or (re.search(r"\btee\b", low) and not re.search(r"tee\s+(-a|--append)", low))
            )
            if rewrite:
                deny("AOL.md is append-only. Append one new milestone entry; never rewrite history.")

        if "principal.md" in low and (
            re.search(r">\s*(?:[^;&|]*[/\\])?principal\.md\b", low)
            or re.search(r"\bsed\b.*-i.*principal\.md", low)
            or re.search(r"\btruncate\b.*principal\.md", low)
            or re.search(r"\b(?:cp|mv|install)\b.*principal\.md", low)
            or (re.search(r"\btee\b.*principal\.md", low) and not re.search(r"tee\s+(-a|--append)", low))
        ):
            deny("Existing Principal.md is user-owned and cannot be changed by this hook-enabled agent.")
        return

    if tool == "apply_patch":
        if targets_existing_governance_file(command, "AOL.md"):
            deny("AOL.md is append-only. Use ~/.codex/hooks/aol-append.sh rather than apply_patch.")
        if targets_existing_governance_file(command, "Principal.md"):
            deny("Existing Principal.md is user-owned and cannot be changed by this hook-enabled agent.")


if __name__ == "__main__":
    main()
