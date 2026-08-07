#!/usr/bin/env python3
"""Core PreToolUse guard for durable fr0m invariants (R5 hook contract).

Ported from the Codex guard (agents/codex/hooks/fr0m_guard.py) to Core's
hook contract, which differs from Claude/Codex:

- stdin JSON keys are `event` / `tool` / `input` (not tool_name/tool_input);
  there is no `cwd` field, so the guard resolves the governance root from its
  own process cwd (Core inherits the launch directory).
- DENY = exit code **2** with the reason on **stderr**; any other exit is
  fail-open ("no opinion"). Timeout is 30s.
- Only `bash` and `edit` mutate in this build (no apply_patch / write_file).

Core cannot implement Claude's permissionDecision=ask either, so existing
Principal.md files are hard-blocked for agent writes, exactly like Codex; the
operator can edit them manually or temporarily remove this hook from
~/.core/config.json. Hooks are guardrails, not a complete security boundary;
Git/CI must enforce repository policy independently.
"""

import json
import os
import re
import sys


def deny(reason: str) -> None:
    # Core surfaces the bounded stderr of the first exit-2 hook as the deny reason.
    print(reason, file=sys.stderr)
    sys.exit(2)


def governed(cwd: str) -> bool:
    path = os.path.abspath(cwd)
    while True:
        if os.path.isfile(os.path.join(path, "Principal.md")):
            return True
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    cwd = data.get("cwd") or os.getcwd()
    if not governed(cwd):
        return

    tool = (data.get("tool") or "").lower()
    tool_input = data.get("input") or {}

    if tool == "bash":
        command = tool_input.get("command", "") or ""
        low = command.lower()

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

    if tool == "edit":
        path = tool_input.get("path", "") or ""
        basename = os.path.basename(path)
        if basename == "AOL.md":
            deny("AOL.md is append-only. Use theOne's aol-append.sh rather than edit.")
        if basename == "Principal.md":
            deny("Existing Principal.md is user-owned and cannot be changed by this hook-enabled agent.")


if __name__ == "__main__":
    main()
