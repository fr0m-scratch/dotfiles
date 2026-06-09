#!/usr/bin/env python3
"""fr0m UserPromptSubmit injector.

SKILL.md content only lives for the turn /fr0m runs. These standing rules are what
keeps the governance alive every turn afterward. Fires ONLY in a governed dir
(one that contains Principal.md), so it is silent in every other project.
"""
import sys, json, os

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cwd = data.get("cwd") or os.getcwd()
if not os.path.isfile(os.path.join(cwd, "Principal.md")):
    sys.exit(0)

rules = (
    "[fr0m governance is ACTIVE in this directory — follow these standing rules]\n"
    "- Plan.md is the single source of truth. Re-read it before acting. Fold EVERY new "
    "requirement or change the user states into it immediately and keep it the most up-to-date doc.\n"
    "- After each substantive action or modification (skip pure side/btw questions), append ONE "
    "timestamped entry to AOL.md via:  bash ~/.claude/hooks/aol-append.sh \"" + cwd + "\" \"<what you did>\"\n"
    "- Log every error encountered and how it was resolved to Errors.md.\n"
    "- Principal.md (End Goal + Key Restrictions) is user-owned: do NOT edit it unless the user "
    "explicitly tells you to (the guard will ask the user to confirm any edit).\n"
    "- Never add Claude as a git co-author. Keep this folder under git.\n"
    "- If a new requirement is unclear, ask the user first, then reflect the answer in Plan.md "
    "before implementing."
)

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": rules,
}}))
