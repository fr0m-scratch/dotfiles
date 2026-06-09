---
name: fr0m
description: Initialize or refresh a project's governance docs (Principal.md, Plan.md, AOL.md, Errors.md), put the folder under git, and turn on the working rules. The user runs this (/fr0m) as the FIRST thing before any implementation, and again whenever they restate the project's goal or restrictions.
disable-model-invocation: true
---

# fr0m — project governance bootstrap

The user typed `/fr0m`, usually followed by a paragraph stating this project's **goal**
and **restrictions** (`$ARGUMENTS`). This is the **first thing that happens before any
real implementation**. Your job: set up (or reconcile) the four governing docs, ensure
git, run a clarifying Q&A if anything is unclear, and produce an agreed **Plan.md** —
*then* implementation may begin.

Do the steps below in order. Do not start writing feature code during a `/fr0m` run; the
output of this skill is the docs + an agreed plan.

## The four docs (created in the current working directory)

| File | Purpose | Who edits it |
|------|---------|--------------|
| **Principal.md** | End Goal + Key Restrictions (+ scope/non-goals). The constitution. | You author it at first init. After that it is **user-owned** — only edit when the user explicitly tells you to (the guard hook will ask the user to confirm any edit). |
| **Plan.md** | Detailed plan + TODO. The **single source of truth** and most important doc. | You — keep it current at **all** times; every new requirement or change the user states must be reflected here immediately. |
| **AOL.md** | Append-Only Log of everything you do/modify (skip pure side/btw questions). | You — **append only**, via the helper. Never edit past entries. |
| **Errors.md** | Every error encountered and how it was resolved. | You — append as errors happen. |

## Procedure

1. **Ensure git.** If the dir is not a git repo (`git rev-parse --is-inside-work-tree`
   fails), run `git init`. Never configure or add Claude as a commit co-author — and never
   add `Co-Authored-By: Claude`, "Generated with Claude", "Claude Code", or a robot emoji
   to any commit message (the guard hook blocks these).

2. **Read what already exists.** If any of the four docs already exist, read them — you are
   **reconciling**, not clobbering. Preserve prior content; merge the new goal/restrictions in.

3. **Clarify first (Q&A → Plan).** If the goal, restrictions, scope, success criteria, or
   any new requirement in `$ARGUMENTS` is unclear or underspecified, ask the user focused
   questions and wait for answers **before** generating/updating Plan.md. A clear, agreed
   plan precedes implementation — always.

4. **Write / reconcile the docs** using the templates below.
   - First init: create Principal.md (allowed), Plan.md, Errors.md; create AOL.md via the
     helper (step 6) or the template.
   - Re-run with new restrictions: editing Principal.md is an edit to a user-owned file, so
     the guard will **ask the user to confirm** — this is expected, not a failure. Once
     confirmed, merge the change; then reflect it in Plan.md and log it in AOL.md.

5. **State the standing rules** back to the user (they are also injected every turn while
   this dir is governed):
   - Plan.md stays the source of truth and the most up-to-date doc.
   - Append an AOL entry after each substantive action/modification.
   - Log errors + resolutions to Errors.md.
   - Don't edit Principal.md unless told; keep the folder under git; no Claude co-author.

6. **Record the init/refresh in AOL** (the one sanctioned write path — `<dir>` is the cwd):

   ```
   bash ~/.claude/hooks/aol-append.sh "<dir>" "fr0m init: created/reconciled governance docs; plan agreed"
   ```

## Templates

**Principal.md**
```markdown
# Principal

> Owner: the user. Authored by Claude at init; thereafter only the user edits this
> (Claude edits only when explicitly told — the guard hook asks the user to confirm).

## End Goal
<one or two sentences>

## Key Restrictions
- <restriction>

## Scope / Non-goals
- <out of scope>
```

**Plan.md**
```markdown
# Plan

_Source of truth. Keep this the most up-to-date document at all times._
_Last updated: <YYYY-MM-DD>_

## Current Objective
<what we are doing right now>

## TODO
- [ ] <task>

## In Progress
- [ ] <task>

## Done
- [x] <task>

## Open Questions / Decisions
- <question or decision + outcome>

## Requirement Change Log
- <YYYY-MM-DD>: <new requirement / modification the user asked for>
```

**Errors.md**
```markdown
# Errors

> Log every error encountered and how it was resolved.

## <YYYY-MM-DD HH:MM> — <short title>
- **Error:** <message / symptom>
- **Cause:** <root cause>
- **Resolution:** <fix>
```

**AOL.md** (prefer creating it with the helper, which writes this header automatically)
```markdown
# Append-Only Log (AOL)

> Append-only. Never edit or delete past entries.
> Add entries only via `bash ~/.claude/hooks/aol-append.sh "<dir>" "<message>"`.

- [<timestamp>] fr0m init: governance docs created.
```

## Enforcement (handled by hooks, FYI)
- **Guard** (`fr0m-guard.py`, PreToolUse): denies AOL.md edits/rewrites, denies Claude
  co-author commits, and asks the user to confirm any Principal.md edit.
- **Rules** (`fr0m-rules.py`, UserPromptSubmit): injects the standing rules every turn while
  the dir contains Principal.md, so governance survives past this skill's run.
- **Helper** (`aol-append.sh`): the only sanctioned way to write AOL.md.
