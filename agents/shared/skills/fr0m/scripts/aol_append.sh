#!/usr/bin/env bash
set -euo pipefail

dir="${1:?usage: aol_append.sh <dir> <message>}"
shift
message="$*"
[ -n "$message" ] || { echo "aol_append: empty message" >&2; exit 2; }
file="$dir/AOL.md"
if [ ! -f "$file" ]; then
  printf '# Append-Only Log (AOL)\n\n> Append-only milestone log. Never edit or delete prior entries.\n\n' >> "$file"
fi
printf -- '- [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$message" >> "$file"
