#!/usr/bin/env python3
"""fr0m project-governance PreToolUse guard.

Enforces (hard, mechanically):
  - No Claude co-authorship in git commits          -> deny
  - AOL.md is append-only (Edit/Write/Bash rewrite) -> deny
  - Principal.md is user-owned (edits after init)   -> ask the user to confirm

Fail-open: any parse problem or unmatched case -> exit 0 (defer to normal flow).
Keep this fast: it runs on every Bash/Edit/Write/MultiEdit call in every project.
"""
import sys, json, os, re


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return  # fail-open

    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}

    # ---------- Bash branch ----------
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        low = cmd.lower()

        # 1) Never let Claude co-author a commit.
        if "git commit" in low and (
            re.search(r"co-authored-by:\s*\S*\s*claude", low)
            or re.search(r"generated with.*claude", low)
            or "claude code" in low
            or "\U0001f916" in cmd  # robot emoji
        ):
            decide("deny",
                   "No Claude co-authorship allowed. Remove any 'Co-Authored-By: Claude...', "
                   "'Generated with Claude', 'Claude Code', or robot-emoji lines from the commit "
                   "message, then retry.")

        # 2) AOL.md is append-only — block Bash truncation/rewrite, allow '>>' and the helper.
        if "aol.md" in low:
            bad = (
                re.search(r"(^|[^>])>\s*[^>|]*aol\.md", low)            # > AOL.md (truncate)
                or re.search(r"\bsed\b.*-i", low)                        # sed -i ... AOL.md
                or re.search(r"\btruncate\b", low)                       # truncate ... AOL.md
                or re.search(r"\b(dd|cp|mv|install)\b.*aol\.md", low)    # overwrite copies
                or (re.search(r"\btee\b", low)
                    and not re.search(r"tee\s+(-a|--append)", low))      # tee w/o append
            )
            if bad:
                decide("deny",
                       "AOL.md is append-only — do not truncate or rewrite it. Append a new "
                       "entry with:  bash ~/.claude/hooks/aol-append.sh \"<dir-with-AOL.md>\" "
                       "\"<message>\"   (or use a '>>' redirect).")
        return

    # ---------- Edit / Write / MultiEdit branch ----------
    if tool in ("Edit", "MultiEdit", "Write"):
        fp = ti.get("file_path") or ti.get("filePath") or ""
        if not fp:
            return
        base = os.path.basename(fp)
        exists = os.path.exists(fp)

        if base == "AOL.md":
            if exists:  # editing/overwriting an existing log
                d = os.path.dirname(os.path.abspath(fp))
                decide("deny",
                       "AOL.md is append-only — never edit or overwrite past entries. Append "
                       "with:  bash ~/.claude/hooks/aol-append.sh \"%s\" \"<message>\"" % d)
            return  # first-time creation is fine

        if base == "Principal.md":
            if exists:  # only the user changes the governing doc after init
                decide("ask",
                       "Principal.md is user-owned (End Goal + Key Restrictions). Only edit it "
                       "when the user explicitly asked for this change. Confirm to proceed.")
            return  # initial creation by /fr0m is fine
    return


if __name__ == "__main__":
    main()
