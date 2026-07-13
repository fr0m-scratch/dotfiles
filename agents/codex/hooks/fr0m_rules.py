#!/usr/bin/env python3
"""Inject a compact reminder when the current tree is governed by fr0m."""

import json
import os
import sys
from typing import Optional


def governance_root(cwd: str) -> Optional[str]:
    path = os.path.abspath(cwd)
    while True:
        if os.path.isfile(os.path.join(path, "Principal.md")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


try:
    payload = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)

root = governance_root(payload.get("cwd") or os.getcwd())
if not root:
    raise SystemExit(0)

context = (
    f"fr0m governance is active at {root}. Follow the nearest AGENTS.md. "
    "Principal.md is user-owned; Plan.md holds current intent. Preserve unrelated dirty work. "
    "AOL.md is append-only: add one concise entry for each completed material change, not every command. "
    "Do not add AI co-authorship to commits, print secrets, or mistake a local commit for a backup."
)
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": context,
}}))
