# Claude Code to Codex source map

This map records semantic ownership. It is not proof that live deployment or authentication is complete.

## Commands

| Claude command | Codex skill | Decision |
|---|---|---|
| `check` | `check-artifact` | Rewritten as a portable skill with a bundled preview dispatcher. |
| `fr0m` | `fr0m` | Thin command removed; governance lives in the skill and AGENTS files. |
| `kickback` | `kickback` | Explicit-only diagnostic for the Claude sidecar; not a Codex earning feature. |
| `latex` | `latex` | Build path moved from `~/.claude` to canonical `.agents/skills`. |
| `open` | `open-artifact` | Rewritten as a portable skill; Codex companion environment dependency removed. |
| `share` | `share-lan` | Rewritten as a skill with a bundled, traversal-safe proxy and mandatory LAN verification. |

## Skills

| Claude skill/surface | Source destination | Decision |
|---|---|---|
| `apple-frontend` | `agents/shared/skills/` | Portable copy. |
| `apple-sales-doc` | `agents/shared/skills/` | Portable copy. |
| `fr0m` | `agents/shared/skills/` | Semantic rewrite for Codex hooks and compact governance. |
| `hlf-modern` | `agents/shared/skills/` | Portable copy with valid concise metadata. |
| `kickback` | `agents/shared/skills/` | Preserved as explicit-only Claude maintenance. |
| `latex` | `agents/shared/skills/` | Portable copy using an installed-skill-relative build path. |
| `pptx` | `agents/shared/skills/` | Clean-room portable workflow. Anthropic's proprietary skill files were not retained because their license forbids copying outside the service. |
| `system-blueprint` | `agents/shared/skills/` | Rewritten generically; confidential RBC exemplar intentionally excluded. |
| `data-platform-solution` | `plantcore/.agents/skills/` | Company-only; personal-tree exemplars removed. |
| `fetch-ctx` | `plantcore/.agents/skills/` | Thin registration wrapper; Context Lake project remains canonical. |
| `fetch-tencent-meeting` | `plantcore/.agents/skills/` | Company-only source with bundled capture/assembly scripts. |
| `new-skill` | none | Replaced by Codex's maintained `skill-creator`; copying it would duplicate platform logic. |
| `shiye-*` (9) | deferred | Nine unmanaged copies were not duplicated. Establish one private canonical upstream first, then expose selected thin registrations. |
| `frontend-design` plugin skill | none | Leave plugin-owned; do not vendor its cache. Evaluate a Codex plugin separately. |

## Agents, hooks, MCP, plugins, state

| Surface | Decision |
|---|---|
| Notion/Lark agents | Rewritten as read-only Plantcore custom agents. |
| Notion/Lark MCP | Plantcore-only project config, Keychain-backed, package versions pinned. |
| fr0m guard/rules | Codex-native source hooks; `apply_patch` input is handled. Principal edits are denied because Codex hooks do not support Claude's `ask` decision. |
| IP/geofence hooks | Not copied. They are provider-specific and require a private country policy; port only after defining OpenAI-specific behavior. |
| Otty hooks | Not copied into this source file; they are app-owned live integration and must be merged during deployment. |
| agent telemetry hooks | Not globalized; keep them project-scoped until their event schema and retention policy are defined. |
| Claude HUD | Not migrated; Codex TUI status line is configured instead. |
| Codex companion plugin | Excluded; it is a transition bridge, not target architecture. |
| sessions, memory, auth, trust, caches, plugin downloads | Excluded. Promote selected durable facts into governed docs; never bulk-copy state. |
