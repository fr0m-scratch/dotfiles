# Trainable Agent Runtime: Arrow Corrections

This is a compact correction reference for the three accepted raster figures.
It records semantic constraints that must survive any redraw or image edit.
It is not a full edge ledger and does not prescribe layout.

## Reading convention

- Write every connector as `source — verb / payload → target`.
- Draw request and response as separate one-way arrows.
- A container, caption, boundary, or color band is not an endpoint.
- Every fork, join, rejection, retry, rollback, and terminal state needs an explicit target.
- Red means control or learning, blue means execution or serving, green means assurance or governance, and purple means optimization; color never substitutes for direction.

## 1. Dynamic Workflow Runtime

### Fatal wrong arrows

- Do not leave `Task` disconnected from `Contract` and `Task Profiler`.
- Do not draw `Topology Policy`, `Scheduler`, `Budget Controller`, and `Recovery Controller` as a compiler's serial post-processing stages; policy and budget constrain compilation and scheduling, while recovery feeds graph actions back to the compiler.
- Do not leave `Scheduler` disconnected from the execution fork.
- Do not derive `Counter-evidence` from `Reader A`; it must be an independently scheduled branch, otherwise it repeats the generating branch's context and bias.
- Do not let `Writer` certify itself or reach a commit path without a candidate-artifact edge and independent verification.
- Never draw `FAIL → Human Gate → Commit`; failure goes to recovery, replan, rollback, escalation, or stop, and a human is not a verifier-failure override.
- Never draw `Versioned Policy → Assurance`, `Versioned Policy → Commit`, or any learning-plane edge that writes a live effect.
- Do not let a searched policy update the online graph before offline evaluation, canary, and release.
- Do not leave the Artifact Bus, Event Log, sandboxed tools, snapshot, or budget ledger as decorative disconnected rails.

### Canonical boundary invariants

- The Control Plane chooses topology, binding, budget, checkpoint, and recovery actions; it does not generate or approve the final artifact.
- The Execution Plane produces typed candidate artifacts; actors can propose completion but cannot sign it.
- The Assurance Plane is independent of the generating branch and owns acceptance plus commit authorization.
- `PASS + reversible` may proceed through the Commit Gate.
- `PASS + irreversible` must stop at the Human Gate before commit.
- `FAIL` must return to Recovery or Stop.
- Human reject or timeout must return to Recovery or Stop, never fall through to Commit.
- The Learning Plane is offline: it may produce a versioned policy, but only a released policy may return to the Graph Compiler.
- Branch width is justified by independently useful, independently verifiable evidence, not agent count.
- Artifacts cross branches by `ArtifactRef`; full transcripts do not become the default bus.
- Graph changes, tool calls, verifier receipts, human decisions, and commits append to a durable event log.

### Compact canonical patterns

- `Task + Contract — provide objective, constraints, acceptance contract → Task Profiler`
- `Task Profiler — emit task profile → Graph Compiler`
- `Topology Policy — constrain allowed graph rewrites → Graph Compiler`
- `Budget Controller — set execution and verification envelope → Graph Compiler`
- `Graph Compiler — emit versioned ExecutionPlan → Scheduler`
- `Scheduler — fork independent work → Reader A`
- `Scheduler — fork independent work → Reader B`
- `Scheduler — fork independent challenge → Counter-evidence`
- `Scheduler — bind work and tools → Coder / Specialist`
- `Readers / Coder / Specialist — publish typed ArtifactRef → Artifact Bus`
- `Artifact Bus — deliver least-context inputs → Writer`
- `Writer — submit Candidate Artifact → Independent Verification`
- `Independent Verification — PASS, reversible → Commit Gate`
- `Commit Gate — commit accepted artifact → Commit`
- `Independent Verification — PASS, irreversible → Human Gate`
- `Human Gate — approve → Commit`
- `Human Gate — reject or timeout → Recovery Controller`
- `Independent Verification — FAIL with receipts → Recovery Controller`
- `Recovery Controller — retry / replan / rollback / stop → Graph Compiler`
- `Execution / tools / verifier / human / commit — append events → Append-only Event Log`
- `Append-only Event Log + outcomes — form trajectory and failure labels → Trajectory Store`
- `Trajectory Store — diagnose and assign credit → Workflow Search`
- `Workflow Search — propose candidate policy → Offline Eval`
- `Offline Eval — accepted candidate → Canary`
- `Canary — promote signed version → Versioned Policy`
- `Canary — regression → Previous Policy / Rollback`
- `Versioned Policy — supply released policy only → Graph Compiler`

## 2. Organization Context Lake

### Fatal wrong arrows

- P0 forbidden: `ContextPacket → External Systems`; a packet returns to agent reasoning and never grants effect authority.
- P0 forbidden: `Context Compiler → Capability Broker / Effect Executor`; a read path cannot originate a real-world action.
- P0 forbidden: `Governance re-authorization → ContextPacket` when labeled “before effects”; effect re-authorization belongs at the Capability Broker or Effect Executor.
- Do not send `TaskEnvelope` to the Context Gateway; it delegates from the Edge Agent to a Vertical Agent.
- Do not let a Vertical Agent bypass the Edge Agent's final user-facing gate on its way to the broker.
- Do not draw `Raw Pool → ContextPacket`, `Raw Pool → Agent`, or `Promotion → Gateway / prompt output`.
- Do not draw `Memory Foundry → Promotion` while skipping independent offline evaluation or external verification.
- Do not let the Foundry generate and certify the same MemoryCandidate.
- Do not point the pre-retrieval authorization arrow at only one materialized view.
- Do not send an admitted query directly into the views while bypassing compiler authorization and routing.
- Do not return external results directly to promoted memory.
- A backward edge into the Raw Pool is legal only when explicitly labeled as an append-only decision or audit receipt; rollback never rewrites raw evidence.

### Canonical boundary invariants

- The Edge Coding Agent owns current human intent and local working state; it is not the universal trust root.
- Vertical Agents receive scoped `TaskEnvelope`s and return proposals, artifacts, evidence, and action requests; they hold no ambient credentials.
- The Context Gateway enforces identity, tenant, scope, consent, and budget before retrieval.
- The read path is fast and read-only: governed views compile into the minimum authorized `ContextPacket` for one principal, purpose, model, and harness.
- The learning path is slow and gated: an agent may submit a trace or `MemoryCandidate`, but cannot write an organizational fact.
- Raw evidence is append-only source of truth; summaries, facts, procedures, evals, and indexes are rebuildable materialized views.
- Foundry output requires independent eval, promotion scope, canary, versioning, and rollback.
- Governance spans ingestion, storage, retrieval, promotion, deletion, and effect re-authorization.
- Policy, permission, and revocation fail closed; revocation propagates through lineage to indexes, derived views, future packets, and outstanding capabilities.
- The `ContextPacket` returns only to the requesting agent reasoning loop.
- Proposed effects follow a separate capability path.
- Effect results return as new typed observations to raw traces, never directly to promoted memory.
- Credentials remain inside the broker / executor boundary.

### Compact canonical patterns

- `Human Session — provide intent and approval → Edge Coding Agent`
- `Edge Coding Agent — delegate scoped TaskEnvelope → Vertical Agent`
- `Vertical Agent — return proposal / ArtifactRef / evidence / ActionRequest → Edge Coding Agent`
- `Agent — submit ContextRequest → Context Gateway`
- `Context Gateway — request pre-retrieval authorization → Governance Spine`
- `Governance Spine — return policy decision, scope, filters, expiry → Context Gateway`
- `Context Gateway — send admitted query → Authorize`
- `Authorize — route authorized query → Route`
- `Route — issue RetrievalPlan → Retrieve`
- `Governed Views / Index — return eligible records with lineage and time → Retrieve`
- `Retrieve — preserve and reconcile contradictions → Reconcile`
- `Reconcile — send candidates for ordering → Rerank`
- `Rerank — order authorized evidence → Compress / Cite / Budget`
- `Compress / Cite / Budget — compile typed bounded result → ContextPacket`
- `ContextPacket — return authorized context → Requesting Agent`
- `Agent / Effect Executor — submit typed trace, artifact, outcome, receipt → Context Gateway`
- `Context Gateway — admit policy-labelled event → Typed Traces + Outcomes`
- `Typed Traces + Outcomes — append evidence → Immutable Raw Pool`
- `Immutable Raw Pool — supply lineage-preserving evidence → Memory Foundry`
- `Memory Foundry — propose MemoryCandidate → Offline Eval / External Verify`
- `Offline Eval / External Verify — issue independent receipt → Promotion Gate`
- `Promotion Gate — release scoped candidate → Canary`
- `Canary — activate accepted version → Governed Materialized View`
- `Canary — reject regression → Rollback / Previous View Version`
- `Edge Coding Agent — propose ToolIntent / EffectProposal → Capability Broker`
- `Capability Broker — request fresh effect authorization → Governance Spine`
- `Governance Spine — issue scoped short-lived capability → Capability Broker`
- `Capability Broker — pass approved action and handle → Effect Executor`
- `Effect Executor — execute scoped idempotent action → External Systems`
- `External Systems — return observation and receipt → Effect Executor`
- `Effect Executor — append result / outcome → Typed Traces + Outcomes`
- `Revocation Event — identify invalid lineage and scope → Lineage Recompute`
- `Lineage Recompute — invalidate or rebuild → Views / Index`
- `Revocation Event — update fail-closed filter → Authorize`
- `Revocation Event — revoke outstanding handle → Capability Broker`

## 3. Core Code: Stable Kernel, Evolvable Harness

### Fatal wrong arrows

- Never draw `Observe → Vertical Profile` or any optimizer feedback that bypasses evaluate, hard gate, signed release, and registry.
- Never draw `Model ↔ Tool / Environment` directly; every effect request and response crosses typed adapters, the Effect Kernel, capability checks, and event commit.
- Never draw `Re-Ablate Runtime → Vertical Profile` directly; a new model/runtime pairing must repeat conformance tests, runtime evaluation, release, and registry publication.
- Do not leave safety, permission, regression, cost, latency, or tail-risk constraints isolated from Evaluate and the hard release gate.
- Do not make the Event Plane look like a peer that freely commands the kernel: primary direction is `Kernel → Event Plane` append; `Event Plane → Kernel` exists only for explicit replay or recovery.
- Do not let an evolvable module, profile, model adapter, optimizer, or post-training branch bypass the Effect Kernel.
- Do not let a learned component modify its own evaluator, release gate, authority boundary, or rollback target.
- Do not release a new model merely because post-training completed; training is optional, conformance and evaluation are mandatory.

### Canonical boundary invariants

- Stable Semantic ABI and Effect Kernel are different layers.
- Evolvable profiles and service modules may predict, route, retrieve, verify, and propose; they do not own real-world authority.
- The Effect Kernel is small, stable, and reviewable: identity, capability check, event commit, effect commit, version pin, kill, and rollback remain outside learned search.
- All models are replaceable and pass the same action, trace, safety, and recovery conformance suite through model-specific adapters.
- Tool and environment credentials remain behind controlled adapters and sandboxes.
- Every request and response is typed and separately logged.
- Event history is append-only; replay is explicit, version-pinned, and cannot masquerade as a new live event.
- The optimizer follows `Observe → Diagnose → Propose → Evaluate → Hard Gate → Release`.
- Evaluation failure returns to Diagnose; it does not drift into Release.
- A released regression follows `Rollback → Previous Runtime Version`.
- Releases are signed tuples that pin model, runtime, adapter, context snapshot, policy, and eval suite.
- Post-training and runtime adaptation share gates but remain distinct optimization modes.

### Compact canonical patterns

- `Vertical Profile — compile versioned configuration → Evolvable Service Modules`
- `Evolvable Module — emit typed ABI request or proposal → Stable Semantic ABI`
- `Model — speak provider protocol → Model-specific Adapter`
- `Model-specific Adapter — lower request to ToolIntent / EffectProposal → Stable Semantic ABI`
- `Execution IR — submit versioned probabilistic intent → Effect Kernel`
- `ToolIntent / EffectProposal — request capability and commit → Effect Kernel`
- `Effect Kernel — append event envelope and decision → Append-only Event Plane`
- `Append-only Event Plane — replay version-pinned event only → Effect Kernel`
- `Effect Kernel — send authorized constrained call → Tool / Environment Adapter`
- `Tool / Environment Adapter — execute inside scoped sandbox → Environment`
- `Environment — return typed result / receipt → Tool / Environment Adapter`
- `Tool / Environment Adapter — return result for commit and logging → Effect Kernel`
- `Effect Kernel — return constrained result → Requesting Runtime / Model Adapter`
- `Append-only Event Plane + outcomes — provide traces, cost, latency, risk → Observe`
- `Observe — send measured behavior → Diagnose`
- `Diagnose — emit failure taxonomy and node / edge credit → Propose`
- `Propose — emit typed module, policy, routing, adapter, or topology diff → Evaluate`
- `Evaluate — run replay, held-out, OOD, security, shadow, and canary → Hard Release Gate`
- `Evaluate — return failed candidate and reasons → Diagnose`
- `Constraints — enforce safety, permission, regression, cost, latency, tail risk → Hard Release Gate`
- `Hard Release Gate — sign accepted release tuple → Registry`
- `Registry — activate signed version → Profiles / Evolvable Modules`
- `Runtime Monitor — report released regression → Rollback Controller`
- `Rollback Controller — restore signed rollback target → Previous Runtime Version`
- `Stable Residual Errors — admit curated training data → Post-training`
- `Post-training — produce candidate model version → Conformance Tests`
- `Conformance Tests — pass compatible model / adapter pair → Runtime Eval`
- `Runtime Eval — pass hard gates → Registry / Release`
- `Runtime Eval — fail with residuals → Diagnose or further training`

## Cross-figure invariants

- Proposal is never authority: actor output, memory candidate, optimizer patch, and model intent cannot commit themselves.
- No learning, serving, model, or optimizer edge may directly produce an external effect.
- Independent verification, current authorization, effect commit, audit, and rollback stay outside learned search.
- Authorization occurs before retrieval and again immediately before effects.
- Human approval is an additional gate for an already verified irreversible action, not a route from failure to commit.
- Raw evidence and event history are append-only; rollback changes active versions, not history.
- Every promoted memory, workflow policy, module, adapter, model, and runtime has a version, evidence, eval receipt, canary scope, and rollback target.
- New observations return to typed traces or event logs before they can influence learning.
- Credentials never live in an agent, model, prompt, memory packet, or learned module.
- Request and response are separate directed edges with different payloads.
- Every generated arrow has one visible source, one visible target, and an action label; no double-headed shortcuts, dangling arrowheads, or arrows into captions.
- Failure paths end in retry, repair, replan, rollback, escalation, or stop; only accepted paths can reach commit.
- Released policies and models may re-enter execution only through their compiler, conformance, registry, and version-pin boundaries.
