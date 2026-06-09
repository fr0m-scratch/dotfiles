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
