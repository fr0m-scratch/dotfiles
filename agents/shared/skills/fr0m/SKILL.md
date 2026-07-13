---
name: fr0m
description: Initialize or reconcile lightweight project governance with Principal.md, Plan.md, AOL.md, Errors.md, Git, and a compact AGENTS.md. Use when starting a project, when the user invokes fr0m, or when goals, restrictions, or repository boundaries materially change.
---

# fr0m governance bootstrap

Set up governance before feature implementation. Reconcile existing files; never clobber them.

1. Inspect the current repository and read any existing `Principal.md`, `Plan.md`, `AOL.md`, `Errors.md`, `AGENTS.md`, and provider-specific instruction files.
2. If the directory is not inside Git, initialize Git. Do not stage or create the first commit unless explicitly requested.
3. Resolve ambiguity in goal, scope, success criteria, ownership, data classification, and backup/remote policy before writing the plan.
4. On first initialization, create:
   - `Principal.md`: stable end goal, non-negotiable restrictions, scope/non-goals. After creation it is user-owned.
   - `Plan.md`: current objective, acceptance criteria, active tasks, decisions, and a short requirement-change log.
   - `AOL.md`: append-only milestone log. One entry per completed material change, not every command.
   - `Errors.md`: resolved incidents with symptom, cause, resolution, and optional prevention.
   - `AGENTS.md`: compact operational routing; keep it comfortably below 32 KiB.
5. On refresh, preserve history. Change `Principal.md` only when the user explicitly requests the constitutional change. Update `Plan.md` rather than creating another governance document.
6. Append the completed init/refresh with `scripts/aol_append.sh <root> <message>`.
7. Review the resulting files and Git status. State what remains uncommitted or unbacked; a local commit is not a backup.

## Standing invariants

- Never rewrite old AOL entries.
- Never add AI co-author or generated-by metadata to commits.
- Preserve unrelated dirty work.
- Keep secrets out of files and logs.
- In a repo-of-repos, ignore a new child repository in the parent in the same change and never use parent-level `git add -A`.
- Use Git hooks/CI for hard repository enforcement; agent hooks are only guardrails.
