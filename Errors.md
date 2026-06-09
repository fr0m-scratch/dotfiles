# Errors

> Log every error encountered and how it was resolved.

## 2026-06-09 — install.sh: FORMULAE[@] unbound variable
- **Error:** `FORMULAE[@]: unbound variable` on both dry-runs.
- **Cause:** macOS `/bin/bash` is 3.2; under `set -u`, expanding an empty array is an error there.
- **Resolution:** length-gate first and use the `${arr[@]+"${arr[@]}"}` safe-expansion idiom. Re-ran clean.

## 2026-06-09 — shellcheck SC2294 in run()
- **Error:** `eval "$@"` flagged (eval negates array benefit).
- **Cause:** dry-run helper builds command strings deliberately.
- **Resolution:** switched to `eval "$*"`; intentional string-eval, warning cleared.

## 2026-06-09 — git push failed: exit status 128 (SSH)
- **Error:** `gh repo create dotfiles --source=. --remote=origin --push` created the GitHub repo and added an SSH `origin` (`git@github.com:...`), but the push failed: "make sure you have the correct access rights ... exit status 128". Retries with other names hit "Name already exists".
- **Cause:** No SSH key registered with GitHub; `origin` was set to the SSH URL. The repo already existed from the first (partial) attempt, so re-creating collided.
- **Resolution:** `gh auth setup-git` (HTTPS credential helper) → `git remote set-url origin https://github.com/fr0m-scratch/dotfiles.git` → `git push -u origin main`. Succeeded.
