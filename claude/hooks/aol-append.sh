#!/usr/bin/env bash
# The one sanctioned write path for AOL.md (append-only log).
# Usage: aol-append.sh <dir-containing-AOL.md> "<message>"
# Creates AOL.md with a header if it does not exist, then appends a timestamped entry.
set -euo pipefail

dir="${1:?usage: aol-append.sh <dir> \"<message>\"}"
shift
msg="$*"
[ -n "$msg" ] || { echo "aol-append: empty message" >&2; exit 1; }

file="$dir/AOL.md"
if [ ! -f "$file" ]; then
  {
    printf '# Append-Only Log (AOL)\n\n'
    printf '> Append-only. Never edit or delete past entries. Add entries only via\n'
    printf '> `bash ~/.claude/hooks/aol-append.sh "%s" "<message>"`.\n' "$dir"
  } >> "$file"
fi

ts="$(date '+%Y-%m-%d %H:%M:%S %z')"
printf -- '- [%s] %s\n' "$ts" "$msg" >> "$file"
echo "AOL <- $msg"
