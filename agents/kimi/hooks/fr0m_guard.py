#!/usr/bin/env python3
"""Kimi Code PreToolUse guard for durable fr0m invariants.

Kimi Code documents only allow/deny hook decisions (exit code 2, or a stdout
JSON object with hookSpecificOutput.permissionDecision); there is no
documented "ask" decision. Existing Principal.md files are therefore
hard-blocked for agent writes; the user edits them manually. Hooks are
guardrails, not a complete security boundary; Git/CI must enforce repository
policy independently.

Fail-open: any parse problem or unmatched case -> exit 0.
"""

import json
import os
import re
import sys


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
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


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    cwd = data.get("cwd") or os.getcwd()
    if not governed(cwd):
        return

    tool = data.get("tool_name") or data.get("toolName") or ""
    tool_input = data.get("tool_input") or data.get("toolInput") or {}

    if tool == "Bash":
        command = tool_input.get("command", "") or ""
        low = command.lower()

        # 1) No AI co-authorship in git commits.
        if "git commit" in low and (
            re.search(r"co-authored-by:\s*\S*\s*(claude|codex|openai|kimi|moonshot)", low)
            or re.search(r"generated with.*(claude|codex|openai|kimi|moonshot)", low)
            or "claude code" in low
            or "kimi code" in low
            or "\U0001f916" in command  # robot emoji
        ):
            deny("AI co-authorship and generated-by commit trailers are not allowed.")

        # 2) AOL.md is append-only — block Bash truncation/rewrite, allow '>>' and the helper.
        if "aol.md" in low:
            rewrite = (
                re.search(r"(^|[^>])>\s*[^>|]*aol\.md", low)          # > AOL.md (truncate)
                or re.search(r"\bsed\b.*-i", low)                     # sed -i ... AOL.md
                or re.search(r"\btruncate\b", low)                    # truncate ... AOL.md
                or re.search(r"\b(dd|cp|mv|install)\b.*aol\.md", low) # overwrite copies
                or (re.search(r"\btee\b", low)
                    and not re.search(r"tee\s+(-a|--append)", low))   # tee w/o append
            )
            if rewrite:
                deny("AOL.md is append-only. Append with:  "
                     "bash ~/.kimi-code/hooks/aol-append.sh \"<dir-with-AOL.md>\" \"<message>\"  "
                     "(or a '>>' redirect).")

        # 3) Principal.md is user-owned — block Bash rewrites of an existing file.
        if "principal.md" in low and (
            re.search(r">\s*(?:[^;&|]*[/\\])?principal\.md\b", low)
            or re.search(r"\bsed\b.*-i.*principal\.md", low)
            or re.search(r"\btruncate\b.*principal\.md", low)
            or re.search(r"\b(?:cp|mv|install)\b.*principal\.md", low)
            or (re.search(r"\btee\b.*principal\.md", low)
                and not re.search(r"tee\s+(-a|--append)", low))
        ):
            deny("Existing Principal.md is user-owned and cannot be changed by this hook-enabled agent.")
        return

    # ---------- Edit / Write branch ----------
    if tool in ("Edit", "Write"):
        fp = (tool_input.get("path") or tool_input.get("file_path")
              or tool_input.get("filePath") or "")
        if not fp:
            return
        base = os.path.basename(fp)
        if not os.path.exists(fp):
            return  # first-time creation is fine

        if base == "AOL.md":
            d = os.path.dirname(os.path.abspath(fp))
            deny("AOL.md is append-only — never edit or overwrite past entries. Append with:  "
                 "bash ~/.kimi-code/hooks/aol-append.sh \"%s\" \"<message>\"" % d)

        if base == "Principal.md":
            deny("Existing Principal.md is user-owned and cannot be changed by this hook-enabled agent.")


if __name__ == "__main__":
    main()
