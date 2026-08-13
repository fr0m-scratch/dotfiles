---
name: blitz
description: Finish an entire already-decided backlog in the least WALL-CLOCK time. This skill explicitly authorizes and requires multi-agent delegation - fan out file-disjoint sub-agent lanes with spawn_agent, one full compile at the very end, minimum tests, one local branch and one commit, never push, and decide open questions yourself instead of blocking on the user. Use when the user pastes a list of remaining items / TODOs / 未完成清单 and says 全部完成 / finish everything / do it all / as fast as possible / 尽可能少的全量 compile / 不要过度 test / 这些做成一个 PR 即可 / 不要 push / 在本地全部完成 / "if you have any question you decide yourself" - i.e. asks for maximum-parallel implementation optimized for time-to-done rather than for tokens, review polish, or commit hygiene.
---

# blitz — clear the whole backlog, optimized for wall-clock (Codex dialect)

`$ARGUMENTS` is a backlog of **already-decided** work (usually pasted, often 5–30 items).
The user wants all of it done, locally, now. Design is settled; this is execution.

> **Delegation is authorized here.** Codex's default posture is *do not spawn sub-agents unless
> the user or a skill explicitly asks for it*. This skill is that explicit instruction: when the
> backlog has ≥3 items touching disjoint files, **you must fan out** rather than work serially.

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

## Phase 0 — cut the work (root agent, never delegated)

1. **Turn the paste into a numbered checklist.** Restate it — that list is the contract and the
   final report's skeleton.
2. **One cheap discovery pass.** Run the `rg`/`fd` calls you need to get `file:line` for every
   item's target *before* spawning anyone. A lane that must find its own target spends most of its
   life reading, and every lane pays that cost again.
3. **Build the conflict graph — partition by WRITE-SET, not by topic.** Two lanes writing the same
   file will clobber each other (they share one working tree; `apply_patch` has no merge). Items
   touching a common file go into the **same lane** as a serial queue.
4. **Choose lane count: 4–6.** Codex caps concurrent threads per session
   (`features.multi_agent_v2.max_concurrent_threads_per_session`, keep it under 8) and each live
   sub-agent burns quota. More lanes than that queue anyway — you buy nothing.

## Phase 1 — spawn the lanes

Issue **all `spawn_agent` calls before any `wait_agent`.** Spawning lane 2 only after lane 1
returns is a barrier you built by hand.

- `task_name`: `lane_1`, `lane_2`, … (canonical path becomes `/root/lane_1`).
- **Do not set `model`.** Sub-agents inherit yours; overriding it is a slower cold path and the
  tool explicitly says not to unless asked.
- **Keep `fork_turns` minimal.** Do not fork your whole transcript into six lanes — a fat inherited
  context is slower to first token *and* pulls in irrelevant instructions. Put everything the lane
  needs in its prompt instead.
- **Forbid nested spawning.** Sub-agents can spawn their own sub-agents; in a blitz that is a
  quota fire with no wall-clock gain. Say so in the prompt.

Lane prompt template — inline everything the lane would otherwise have to discover:

```
You own lane <N> of a parallel implementation. Do ONLY these items, in this order:

1. <item> — file: <path:line>. Acceptance: <observable criterion>.
2. <item> — file: <path:line>. Acceptance: <observable criterion>.

<paste the relevant existing code/config snippets here so no re-discovery is needed>

Rules:
- NO full build, NO test suite, NO benchmark, NO `codex review`. Cheapest per-target check only:
  `cargo check -p <crate>` / `tsc --noEmit` / `node --check <f>` / `python -c 'import m'` / `go build ./pkg/...`.
  A full build here is the single worst thing you can do to this run.
- Do NOT spawn your own sub-agents.
- NO git commands at all — no add/commit/stash/checkout/branch. The root agent owns the index.
- Edit ONLY the files listed. If another file must change, say so in your receipt instead of editing it.
- Blocked or ambiguous? Take the smallest reasonable decision and note it. Never stop, never ask.
- Final message = the whole receipt: per item done|partial|blocked, files+lines touched,
  decisions taken, anything left. The root agent sees nothing else from your run.
```

Then **one `wait_agent` over all lane ids** — not a wait per lane, and never a poll loop. While
waiting you may do conflict-free prep in your own turn: read the build config, work out the test
selector, draft the commit message. `close_agent` each lane once its receipt is in.

## Phase 2 — the single compile (root agent)

After the last receipt, run **one** full build. A 6-lane blitz typically yields under ~20 errors
and they are mechanical (imports, renamed fields, changed signatures):

- **Fix them yourself with `apply_patch`.** A round-trip to a fresh lane costs more than the fix.
- **Fix ALL of them, then recompile once.** Recompiling after each individual fix is the second
  biggest wall-clock leak in this procedure.
- Re-spawn fixer lanes only if errors are numerous (~25+) **and** land in disjoint files.

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
- ❌ **Spawn → wait → spawn → wait.** Spawn the whole fleet, then wait once.
- ❌ **Fat `fork_turns`** into every lane.
- ❌ **Lanes that discover their own files.** Hand them `file:line` and the snippet.
- ❌ **Asking the user mid-run.** Decide, flag it in the report, keep going.
- ❌ **Recompiling after every single fix.**
- ❌ **Commit per item**, or a branch per item.
- ❌ **`codex review`** during a blitz — it is a second full pass over the diff, not a build check.
- ❌ **"Let me refactor this first."** Blitz is scope-fixed. Note the smell, don't chase it.

## Runtime notes (Codex-specific)

- Requires the `multi_agent` feature (stable, on by default). If `spawn_agent` is missing, run
  `codex features enable multi_agent`; if it is still unavailable, fall back to serial execution
  with the same compile/test/commit discipline and say the fan-out was unavailable.
- This machine runs `approval_policy = "never"`, so lanes will not stall on approvals. If a
  sandbox denial does appear in a receipt, fix it in the root agent rather than re-spawning.
- Lanes share **one working tree**. Disjoint write-sets are what makes this safe — there is no
  per-lane isolation to fall back on.

## In a fr0m-governed directory

If the cwd has `Plan.md`/`AOL.md`: fold the checklist into `Plan.md` **once** at the start, append
**one** entry at the end via `~/.codex/hooks/aol-append.sh` (not one per item — the per-item
appends are pure wall-clock), and log genuine failures to `Errors.md`. `Principal.md` edits are
hard-denied by the guard hook; never attempt one mid-blitz.

## When NOT to blitz

- **Design is not settled** — parallel lanes just produce wrong work in parallel. Decide first.
- **≤ 2 files** — spawning costs more than doing it.
- **Anything that pushes, deploys, or touches prod.**
- **Ordered migrations** where item N+1 consumes N's output — that is one lane, not many.
