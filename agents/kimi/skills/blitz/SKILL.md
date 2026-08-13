---
name: blitz
description: Finish an entire already-decided backlog in the least WALL-CLOCK time — fan out file-disjoint lanes in ONE AgentSwarm call, one full compile at the very end, minimum tests, one local branch and one commit, never push, and decide open questions yourself instead of blocking on the user. Use when the user pastes a list of remaining items / TODOs / 未完成清单 and says 全部完成 / finish everything / do it all / as fast as possible / 尽可能少的全量 compile / 不要过度 test / 这些做成一个 PR 即可 / 不要 push / 在本地全部完成 / "if you have any question you decide yourself" — i.e. asks for maximum-parallel implementation optimized for time-to-done rather than for tokens, review polish, or commit hygiene.
---

# blitz — clear the whole backlog, optimized for wall-clock (Kimi Code dialect)

`$ARGUMENTS` is a backlog of **already-decided** work (usually pasted, often 5–30 items).
The user wants all of it done, locally, now. Design is settled; this is execution.

## The objective function

**The only metric is elapsed time until every item is actually done.** Token spend, agent count,
duplicated reading, and re-derived context are **free** — spend them freely. What is expensive is
anything **serialized**: full builds, full test suites, commit-per-item, and above all a **question
back to the user** (that one costs however long until they next look at the screen — usually the
single largest term in the whole run).

**Fast never means partial.** Dropping scope is a failure, not an optimization. The deal is: you
skip verification breadth, and in exchange you finish *everything* and state plainly what you did
not verify.

## Standing contract (assume these unless the user says otherwise)

| Rule | Meaning |
|---|---|
| Fewest full compiles | Ideally **exactly one**, at the end. Never one per lane. |
| Fewest tests | Narrowest selector that proves the change, run **once**. No full suite unless asked. |
| One PR's worth | One branch, **one commit**. Do not split work across many branches/PRs. |
| Never push | Stop at the local commit. Print the push command; let the user run it. |
| You decide | Ambiguity → pick the option most consistent with the stated goal, record it, keep moving. Ask only if a wrong choice is unsafe or would invalidate the work. |
| Complete means complete | Every item done, or explicitly reported as not done with the reason. |

## Phase 0 — cut the work (main agent, never delegated)

1. **Turn the paste into a numbered checklist.** Restate it — that list is the contract and the
   final report's skeleton. Skip `TodoList` ceremony; the checklist in your reply is enough.
2. **One cheap discovery pass.** Use `Grep`/`Glob` yourself, or one `Agent` with
   `subagent_type: "explore"` if the repo is unfamiliar, to get `file:line` for every item's target
   **before** the swarm. A lane that must find its own target spends most of its life reading, and
   every lane pays that cost again.
3. **Build the conflict graph — partition by WRITE-SET, not by topic.** Two lanes writing the same
   file will clobber each other. Items touching a common file go into the **same lane item** as a
   serial queue.
4. **Choose lane count: 4–8.** One lane = one entry in the swarm's `items` array.

## Phase 1 — one swarm, all lanes

`AgentSwarm` is the fan-out primitive, and it has two hard rules that shape this phase:

- **It must be the ONLY tool call in that response.** No `Read`, no `Bash` alongside it.
- **Swarms do not overlap.** A second `AgentSwarm` may only be issued after the first returns.

So there is exactly **one** swarm per blitz: every lane goes into a single `items` array. Splitting
6 lanes into three swarms of two turns your parallel run back into a serial one.

Call shape:

- `prompt_template` — the **shared** rules, containing the `{{item}}` placeholder.
- `items` — one entry per lane, each carrying that lane's items, paths, and acceptance criteria.
  Everything lane-specific must live here, because the template is identical for all lanes.
- `subagent_type` — omit for the default coder profile (it has `Read`/`Write`/`Edit`/`Bash`).
  Never use `explore` or `plan` for lanes; both are read-only and will silently do nothing.

```
prompt_template:
  You own one lane of a parallel implementation. Do ONLY what this lane lists, in order:

  {{item}}

  Rules:
  - NO full build, NO test suite, NO benchmark. Cheapest per-target check only:
    `cargo check -p <crate>` / `tsc --noEmit` / `node --check <f>` / `python -c 'import m'` / `go build ./pkg/...`.
    A full build here is the single worst thing you can do to this run.
  - NO git commands at all — no add/commit/stash/checkout/branch. The main agent owns the index.
  - Edit ONLY the files this lane lists. If another file must change, report it instead of editing it.
  - Blocked or ambiguous? Take the smallest reasonable decision and note it. Never stop, never ask.
  - Your final message IS the deliverable — the main agent sees nothing else from your run. Make it
    complete in ONE message: per item done|partial|blocked, every file path you touched, what you
    changed and why, the check command you ran and its result, anything left undone. A one- or
    two-sentence summary is rejected as too brief and sent back to you, costing an extra turn.

items[i]:
  1. <item> — file: <path:line>. Acceptance: <observable criterion>.
  2. <item> — file: <path:line>. Acceptance: <observable criterion>.
  <paste the relevant existing code/config snippets so no re-discovery is needed>
```

Prefer **more, smaller, fully-specified lane items** over a few compound ones: an under-specified
lane comes back partial, and a re-issued lane costs a whole extra swarm.

## Phase 2 — the single compile (main agent)

The swarm returns all lanes together. Then run **one** full build. A 6-lane blitz typically yields
under ~20 errors and they are mechanical (imports, renamed fields, changed signatures):

- **Fix them yourself.** A second swarm costs more than the fixes do.
- **Fix ALL of them, then recompile once.** Recompiling after each individual fix is the second
  biggest wall-clock leak in this procedure.
- Issue a second swarm only if errors are numerous (~25+) **and** land in disjoint files.

## Phase 3 — the minimum test

Narrowest selector that covers what changed, once:
`cargo test -p <crate> <filter>` · `pytest path/to/test_x.py::test_y` · `vitest run <file>` · `go test ./pkg/x`.

If the suite takes minutes and the change is mechanical or type-checked, **skip it and say so**.
Never run the full suite "to be safe" — the contract is that you name what went unverified.

## Phase 4 — land it locally

One branch, one `git add -A`, one commit, **no push**, no AI co-author line. Then print the exact
commands the user would run to push and open the PR — and stop there.

## Report format

```
✅ 1. <item>   ✅ 2. <item>   ⚠️ 7. <item> — done, but <caveat>
Decisions I took: <ambiguity → choice, one line each>
NOT verified: <suite skipped / manual path untested / compile-only>
To push:  git push -u origin <branch>  &&  gh pr create ...
```

## Wall-clock anti-patterns (each is real minutes)

- ❌ **Per-lane full build.** N × the slowest thing in the repo. Worse for Rust: cargo takes an
  exclusive lock on `target/`, so parallel builds *serialize anyway* ("Blocking waiting for file
  lock") while thrashing the disk.
- ❌ **Several small swarms instead of one wide one** — they cannot overlap, so that is serial work
  wearing a parallel costume.
- ❌ **Lanes that discover their own files.** Hand them `file:line` and the snippet.
- ❌ **Thin lane receipts** — Kimi bounces a too-short final message back to the lane, costing a
  turn you cannot get back. Demand the full receipt in the template.
- ❌ **Asking the user mid-run.** Decide, flag it in the report, keep going.
- ❌ **Recompiling after every single fix.**
- ❌ **Commit per item**, or a branch per item.
- ❌ **"Let me refactor this first."** Blitz is scope-fixed. Note the smell, don't chase it.

## Runtime notes (Kimi Code specific)

- Invoke as `/blitz` or `/skill:blitz`.
- Run the session in an unattended permission mode (`kimi --auto`, or `--yolo` if you want it to
  still be able to ask). Under the default mode a lane's first `Write` can sit waiting for an
  approval that no one is watching — that single stall can cost more than the whole fan-out saved.
- Lanes share **one working tree**. Disjoint write-sets are what makes this safe — there is no
  per-lane isolation to fall back on.

## In a fr0m-governed directory

If the cwd has `Plan.md`/`AOL.md`: fold the checklist into `Plan.md` **once** at the start, append
**one** entry at the end via `~/.kimi-code/hooks/aol-append.sh` (not one per item — the per-item
appends are pure wall-clock), and log genuine failures to `Errors.md`. `Principal.md` edits are
hard-denied by the guard hook; never attempt one mid-blitz.

## When NOT to blitz

- **Design is not settled** — parallel lanes just produce wrong work in parallel. Decide first.
- **≤ 2 files** — swarming costs more than doing it.
- **Anything that pushes, deploys, or touches prod.**
- **Ordered migrations** where item N+1 consumes N's output — that is one lane, not many.
