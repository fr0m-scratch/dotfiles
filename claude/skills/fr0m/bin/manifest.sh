#!/usr/bin/env bash
# shellcheck disable=SC2016 # Markdown backticks are intentional literals.
# Re-derive a repository registry from disk without mutating repositories.
set -euo pipefail

ROOT="${1:-.}"
[ -d "$ROOT" ] || { echo "no such dir: $ROOT" >&2; exit 1; }
ROOT="$(cd "$ROOT" && pwd)"
NAME="$(basename "$ROOT")"

short_remote() {
  local u="${1%.git}" repo rest org
  u="${u%/}"
  repo="${u##*/}"
  rest="${u%/*}"
  org="${rest##*[:/]}"
  printf '%s/%s' "$org" "$repo"
}

printf '# Repo Manifest — %s\n\n' "$NAME"
printf '> **Generated from disk — do not hand-edit.** Regenerate with:\n'
printf '> `bash ~/.claude/skills/fr0m/bin/manifest.sh %s > MANIFEST.md`\n>\n' "$ROOT"
printf '> Every repo below is independent (own `.git`, own governance), gitignored by its\n'
printf '> parent so it stays independent (repo-of-repos; **no git submodules**).\n'
printf '> `Backup` is ✅ only when a remote exists and HEAD is not ahead of it.\n\n'
printf '| Path | Commits | Remote | Backup | Dirty | Tracked | Size |\n'
printf '|------|--------:|--------|:------:|------:|--------:|-----:|\n'

find "$ROOT" -name .git -not -path '*/node_modules/*' -not -path '*/.venv*/*' 2>/dev/null \
  | sed 's#/\.git$##' | LC_ALL=C sort | while IFS= read -r repo; do
  rel="${repo#"$ROOT"}"
  rel="${rel#/}"
  [ -n "$rel" ] || rel='.'
  commits=$(git -C "$repo" rev-list --count HEAD 2>/dev/null || echo 0)
  remote_raw=$(git -C "$repo" remote get-url origin 2>/dev/null || true)
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  tracked=$(git -C "$repo" ls-files 2>/dev/null | wc -l | tr -d ' ')
  size=$(du -sh "$repo" 2>/dev/null | cut -f1 | tr -d ' ')
  if [ -n "$remote_raw" ]; then
    remote="\`$(short_remote "$remote_raw")\`"
    ahead=$(git -C "$repo" rev-list --count '@{u}..HEAD' 2>/dev/null || echo '?')
    case "$ahead" in
      0) backup='✅' ;;
      '?') backup='⚠️ 无 upstream' ;;
      *) backup="⚠️ 领先 ${ahead}" ;;
    esac
  else
    remote='—'
    backup='❌ 仅本地'
  fi
  [ "$commits" = 0 ] && backup='❌ 零提交'
  printf '| `%s` | %s | %s | %s | %s | %s | %s |\n' \
    "$rel" "$commits" "$remote" "$backup" "$dirty" "$tracked" "$size"
done

printf '\n_Generated: %s_\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
