---
name: blitz
description: Finish an entire already-decided backlog in the least WALL-CLOCK time — fan out file-disjoint subagent lanes in parallel, one full compile at the very end, minimum tests, one local branch and one commit, never push, and decide open questions yourself instead of blocking on the user. Use when the user pastes a list of remaining items / TODOs / 未完成清单 and says 全部完成 / finish everything / do it all / as fast as possible / 尽可能少的全量 compile / 不要过度 test / 这些做成一个 PR 即可 / 不要 push / 在本地全部完成 / "if you have any question you decide yourself" — i.e. asks for maximum-parallel implementation optimized for time-to-done rather than for tokens, review polish, or commit hygiene.
---

# blitz — clear the whole backlog, optimized for wall-clock

`$ARGUMENTS` is a backlog of **already-decided** work (usually pasted, often 5–30 items).
The user wants all of it done, locally, now. Design is settled; this is execution.

## The objective function

**The only metric is elapsed time until every item is actually done.** Token spend, agent
count, duplicated reading, and re-derived context are **free** — spend them freely. What is
expensive is anything **serialized**: full builds, full test suites, commit-per-item, and above
all a **question back to the user** (that one costs however long until they next look at the
screen — usually the single largest term in the whole run).

**Fast never means partial.** Dropping scope is a failure, not an optimization. The deal is:
you skip verification breadth, and in exchange you finish *everything* and state plainly what
you did not verify.

## Standing contract (assume these unless the user says otherwise)

| Rule | Meaning |
|---|---|
| Fewest full compiles | Ideally **exactly one**, at the end. Never one per lane. |
| Fewest tests | Narrowest selector that proves the change, run **once**. No full suite unless asked. |
| One PR's worth | One branch, **one commit**. Do not split work across many branches/PRs. |
| Never push | Stop at the local commit. Print the push command; let the user run it. |
| You decide | Ambiguity → pick the option most consistent with the stated goal, record it, keep moving. Ask only if a wrong choice is unsafe or would invalidate the work. |
| Complete means complete | Every item done, or explicitly reported as not done with the reason. |

## Phase 0 — cut the work (inline, in the main thread, never delegate)

1. **Turn the paste into a numbered checklist.** Restate it back — that list is the contract
   and the final report's skeleton. If the paste is long, this is the one place to be precise.
2. **One cheap discovery pass.** Fire all the Grep/Glob calls you need **in a single message**
   (or one `Explore` agent if the repo is unfamiliar) to get `file:line` for every item's target.
   Do this *before* spawning implementers: an agent that must find its own target spends most of
   its life reading, and every lane pays that cost again.
3. **Build the conflict graph — partition by WRITE-SET, not by topic.** Two agents writing the
   same file will clobber each other. Items that touch a common file go into the **same lane** as
   a serial queue. Everything else parallelizes.
4. **Choose lane count.** 4–8 is the practical band (this machine has 14 cores). More lanes only
   when the write-sets are genuinely disjoint; a lane is one agent holding a serial list of items.
   Shared-file items concentrate in one lane rather than serializing the whole run.

## Phase 1 — fan out (all `Agent` calls in ONE message)

Send every lane in a single assistant message so they start together. Do not design lane 2
after lane 1 returns — that is a barrier you chose to build.

Lane prompt template — inline everything the agent would otherwise have to discover:

```
You own lane <N> of a parallel implementation. Do ONLY these items, in this order:

1. <item> — file: <path:line>. Acceptance: <observable criterion>.
2. <item> — file: <path:line>. Acceptance: <observable criterion>.

<paste the relevant existing code/config snippets here so no re-discovery is needed>

Rules:
- NO full build, NO test suite, NO benchmark. Cheapest per-target check only:
  `cargo check -p <crate>` / `tsc --noEmit` / `node --check <f>` / `python -c 'import m'` / `go build ./pkg/...`.
  A full build here is the single worst thing you can do to this run.
- NO git commands at all — no add/commit/stash/checkout/branch. The main thread owns the index.
- Touch ONLY the files listed. If you believe another file must change, say so in the receipt
  instead of editing it.
- Blocked or ambiguous? Take the smallest reasonable decision and note it. Never stop, never ask.
- Return a compact receipt, no prose: per item → done|partial|blocked, files+lines touched,
  decisions taken, anything left for the main thread.
```

Use `isolation: "worktree"` **only** when lanes must build or run the code (they contend on the
same `target/`/`node_modules`). Plain edits to disjoint files need no worktree — it costs setup
time and disk for nothing.

**While lanes run**, the main thread does conflict-free prep: read the build config, work out the
narrowest test selector, draft the commit message. Do not poll with `sleep` — completions notify you.

## Phase 2 — the single compile (main thread)

After the last lane returns, run **one** full build. A 6-lane blitz typically yields under ~20
errors and they are mechanical (imports, renamed fields, changed signatures):

- **Fix them inline.** A round-trip to a fresh agent costs more than the fix itself.
- **Fix ALL of them, then recompile once.** Recompiling after each individual fix is the second
  biggest wall-clock leak in this whole procedure.
- Fan out fix-agents only if errors are numerous (~25+) **and** land in disjoint files.

## Phase 3 — the minimum test

Run the narrowest selector that covers what changed, once:
`cargo test -p <crate> <filter>` · `pytest path/to/test_x.py::test_y` · `vitest run <file>` · `go test ./pkg/x`.

If the suite takes minutes and the change is mechanical or type-checked, **skip it and say so**.
Never run the full suite "to be safe" — the contract is that you name what went unverified.

## Phase 4 — land it locally

One branch, one `git add -A`, one commit, **no push**, no Claude co-author. Then print the exact
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
- ❌ **A barrier where a pipeline would do** — waiting for all of stage 1 when each item could
  already be moving through stage 2.
- ❌ **Agents that discover their own files.** Hand them `file:line` and the snippet.
- ❌ **Asking the user mid-run.** Decide, flag it in the report, keep going.
- ❌ **Recompiling after every single fix.**
- ❌ **Commit per item**, or a branch per item.
- ❌ **`sleep`/poll loops** waiting on background work.
- ❌ **"Let me refactor this first."** Blitz is scope-fixed. Note the smell, don't chase it.
- ❌ **Serial handoff** — main thread doing item 1 itself while 7 lanes could have been running.

## Workflow vs. plain fan-out

Plain `Agent` fan-out is the default: it starts instantly and the main thread keeps control of the
compile and the commit. Reach for `Workflow` only at **≥8 items with a real per-item multi-stage
shape** (implement → verify), and then use `pipeline()`, **not** `parallel()`, so each item flows
to its next stage without waiting for its cohort. Keep the final compile and commit in the main thread.

## In a fr0m-governed directory

If the cwd has `Plan.md`/`AOL.md`: fold the checklist into `Plan.md` **once** at the start, append
**one** `AOL.md` entry at the end (not one per item — the per-item appends are pure wall-clock),
and log genuine failures to `Errors.md`.

## When NOT to blitz

- **Design is not settled** — parallel lanes just produce wrong work in parallel. Decide first.
- **≤ 2 files** — spawning costs more than doing it.
- **Anything that pushes, deploys, or touches prod.**
- **Ordered migrations** where item N+1 consumes N's output — that is one lane, not many.
