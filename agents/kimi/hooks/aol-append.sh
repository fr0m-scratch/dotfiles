#!/usr/bin/env bash
# shellcheck disable=SC2016 # Markdown backticks are intentional literals.
# The sanctioned write path for append-only AOL.md logs.
# Usage: aol-append.sh <dir-containing-AOL.md> "<message>"
set -euo pipefail

dir="${1:?usage: aol-append.sh <dir> \"<message>\"}"
shift
msg="$*"
[[ -n "$msg" ]] || { echo "aol-append: empty message" >&2; exit 1; }

file="$dir/AOL.md"
if [[ ! -f "$file" ]]; then
  {
    printf '# Append-Only Log (AOL)\n\n'
    printf '> Append-only. Never edit or delete past entries. Add entries only via\n'
    printf '> `bash ~/.kimi-code/hooks/aol-append.sh "%s" "<message>"`.\n' "$dir"
  } >> "$file"
fi

ts="$(date '+%Y-%m-%d %H:%M:%S %z')"
printf -- '- [%s] %s\n' "$ts" "$msg" >> "$file"
printf 'AOL <- %s\n' "$msg"
