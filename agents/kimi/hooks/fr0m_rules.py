#!/usr/bin/env python3
"""Inject a compact reminder when the current tree is governed by fr0m.

Kimi Code appends a UserPromptSubmit hook's stdout to the context when the
hook exits 0, so this prints plain text rather than a JSON envelope. Silent
outside governed trees (no Principal.md upward from cwd).
"""

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

print(
    f"fr0m governance is active at {root}. Follow the nearest AGENTS.md. "
    "Principal.md is user-owned; Plan.md holds current intent. Preserve unrelated dirty work. "
    "AOL.md is append-only: add one concise entry per completed material change via "
    "bash ~/.kimi-code/hooks/aol-append.sh \"<dir>\" \"<message>\". "
    "Do not add AI co-authorship to commits, print secrets, or mistake a local commit for a backup."
)
