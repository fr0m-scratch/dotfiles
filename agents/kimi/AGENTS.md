# Global Kimi Code routing contract

Treat `$HOME` as a machine boundary, not as a project. Work from an explicit
repository root; default to read-only when the task genuinely spans the whole
machine. Personal work belongs under `~/theOne`; company work belongs under
`~/plantcore`; archives are reference-only unless the user names one.

- Read the nearest repository `AGENTS.md`; narrower instructions take priority.
- Preserve unrelated dirty work. Inspect the nearest Git root before editing.
- Never print, parse, copy, or commit credential values. Credentials live in
  macOS Keychain and are exposed only to the process that needs them.
- Do not read `~/.ssh`, Keychains, agent auth files, or quarantine directories
  unless the user explicitly requests a security operation.
- Do not claim that a local commit, APFS snapshot, or same-disk archive is a
  backup. A verified remote or external destination is required.
- Do not create personal remotes for company repositories or move company
  content into public dotfiles, personal projects, public services, or chats.
- Avoid broad parent-repository staging. Stage exact files only after reviewing
  status and diffs; never add nested repositories as gitlinks.
- `Principal.md` is user-owned. `AOL.md` is append-only through
  `~/.kimi-code/hooks/aol-append.sh`. Never add AI co-author/generated-by trailers.
- Use immutable, source-controlled skills and hook scripts. Keep sessions,
  auth, caches, databases, logs, plugin downloads, and mutable app
  state out of dotfiles.
- Verify changed configuration syntactically and exercise the behavior it
  controls. Report any external-account or physical-device step that remains.

Portable agent source is `~/theOne/dotfiles/agents`. Machine-private inventory
and drift checks are in `~/theOne/machine-private`. Do not edit generated doctor
state by hand.
