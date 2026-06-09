---
name: new-skill
description: Scaffold a new reusable Claude Code skill from a description. Use when the user wants to create / author / write / register a new skill (slash command), capture a workflow or style as a reusable skill, or "make this a skill". Writes a well-formed SKILL.md (global by default, so every Claude Code on the machine can use it) with a strong trigger description and concrete instructions.
---

# new-skill — author a new Claude Code skill

The user wants to turn a capability, workflow, or style into a **reusable skill**.
`$ARGUMENTS` is their description of what the skill should do. Produce one well-formed
`SKILL.md` and confirm it's registered.

## What a skill is (the mental model)
A skill = a folder with a `SKILL.md`. Its **frontmatter `description` is the trigger** — the model
reads it to decide when to load the skill — and the **body is instructions to the model** (imperative,
concrete steps), not prose for a human. Users also invoke it explicitly as `/<name>`.

## Where it lives (scope)
- **Global / whole machine (DEFAULT):** `~/.claude/skills/<name>/SKILL.md` — available in every project, every cwd.
- **Project-only:** `<project>/.claude/skills/<name>/SKILL.md` — only inside that repo.
Default to **global** unless the user says "just this project". (Personal slash commands instead go in
`~/.claude/commands/<name>.md`, but skills are the richer mechanism — prefer a skill.)

## Steps
1. **Understand the ask.** From `$ARGUMENTS`, identify: what the skill DOES, and crucially WHEN it should
   fire (the trigger phrases / situations). If either is unclear, ask 1–2 short questions before writing —
   a vague trigger makes a skill that never activates or fires at the wrong time.
2. **Pick a name.** Short, kebab-case, verb-or-noun, distinctive (e.g. `apple-frontend`, `release-notes`,
   `pdf-redact`). Check for collision: `ls ~/.claude/skills/`. Don't shadow an existing skill.
3. **Write the `description` (most important line).** Third person, one or two sentences:
   *what it does* + *explicit "Use when …" triggers* (the words/situations a user would say). This is what
   the model matches on — be concrete about triggers, not just capability. Bad: "Helps with frontends."
   Good: "Build an Apple-HIG-style web UI… Use when the user wants a product UI that looks like Apple and NOT AI-style."
4. **Write the body.** Imperative instructions the model will follow: the rules/constraints, a step-by-step
   procedure, concrete examples or templates, and any verification step. Reference `$ARGUMENTS` if the skill
   takes input. Keep it self-sufficient (inline the key tokens/snippets) so it works without external lookups.
   Put long references or assets as sibling files in the skill folder and point to them.
5. **Optional frontmatter:**
   - `disable-model-invocation: true` → user-only (pure `/slash` command, never auto-triggers). Use for
     destructive or explicitly-manual actions.
   - (no flag) → model may also auto-load it when the description matches. Default for helpers/styles.
6. **Create it:** `mkdir -p ~/.claude/skills/<name>` then write `SKILL.md` (frontmatter + body).
7. **Confirm registration.** A global skill is picked up by all Claude Code sessions automatically (no
   restart of the harness file needed; new sessions see it, and the running session lists it shortly).
   Tell the user the name, the path, the scope (whole-machine), and how to invoke: `/<name>`.

## SKILL.md template
```markdown
---
name: <kebab-name>
description: <what it does> + Use when <explicit trigger situations / phrases>.
# disable-model-invocation: true   # uncomment for user-only slash command
---

# <name> — <one-line purpose>

<Imperative context: the user invoked this (optionally with $ARGUMENTS). State the goal.>

## Rules / constraints
- <hard rules; what must always/never happen>

## Steps
1. <do this>
2. <then this>

## Example / template
<concrete snippet the model can adapt>
```

## Quality bar
- The `description` names real trigger words — test it mentally: "would this fire when the user says X?"
- The body is actionable on its own. No "figure it out" hand-waves.
- Prefer one focused skill over a kitchen-sink one. If the ask spans two distinct triggers, make two skills.
- After writing, restate the trigger back to the user so they can confirm it'll fire when they expect.
