#!/usr/bin/env python3
"""Global delivery rule and fr0m UserPromptSubmit injector.

SKILL.md content only lives for the turn /fr0m runs. These standing rules are what
keep the governance alive every turn afterward. The Finder-visible artifact rule
is global; project governance is added only in a governed directory.
"""
import sys, json, os

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cwd = data.get("cwd") or os.getcwd()

delivery_rule = (
    "[global artifact delivery rule]\n"
    "- For every final file artifact, copy a verified deliverable into "
    "~/Desktop/Deliverables/ unless the user names another Finder-visible "
    "folder, reveal it with `open -R`, and report that Finder-visible path. A repository "
    "or hidden-directory path alone is not delivery."
)

if not os.path.isfile(os.path.join(cwd, "Principal.md")):
    rules = delivery_rule
else:
    rules = delivery_rule + "\n" + (
        "[fr0m governance is ACTIVE in this directory — follow these standing rules]\n"
        "- Plan.md is the single source of truth. Re-read it before acting. Fold EVERY new "
        "requirement or change the user states into it immediately and keep it the most up-to-date doc.\n"
        "- After each substantive action or modification (skip pure side/btw questions), append ONE "
        "timestamped entry to AOL.md via:  bash ~/.claude/hooks/aol-append.sh \"" + cwd + "\" \"<what you did>\"\n"
        "- Log every error encountered and how it was resolved to Errors.md.\n"
        "- Principal.md (End Goal + Key Restrictions) is user-owned: do NOT edit it unless the user "
        "explicitly tells you to (the guard will ask the user to confirm any edit).\n"
        "- Never add Claude as a git co-author. Keep this folder under git.\n"
        "- STORAGE: this machine runs at 95% full. Large, append-only or cold artifacts (traces, "
        "captures, datasets, recordings, exports) default to the 1 TiB volume at ~/nas, not the "
        "local disk; register new large sources in ~/.agent-trace-ship/config.json. Regenerable "
        "output (target/, node_modules/, .venv/, build/, caches) is DELETED, never archived. The "
        "link to ~/nas is 3-4 MiB/s, so it is an archive, not a working disk: never put active "
        "source trees, live databases or runtime-loaded weights there. See ~/.claude/CLAUDE.md.\n"
        "- If a new requirement is unclear, ask the user first, then reflect the answer in Plan.md "
        "before implementing."
    )

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": rules,
}}))
