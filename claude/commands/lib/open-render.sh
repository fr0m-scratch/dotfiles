#!/usr/bin/env bash
# Portable file-preview dispatcher for the /open and /check slash commands.
# Renders a .md / .html file in the best surface the current terminal offers:
#   Wave  ($WAVETERM_JWT + wsh) -> wsh view <md> | wsh web open file://<html>  (native block)
#   otty  ($TERM_PROGRAM=otty)  -> otty view --right <file>  (SAME tab, split pane; renders md+html)
#   plain (anything else)       -> open <html> (browser) | glow <md> (stdout)  (fallback)
#
# Usage: open-render.sh <file-path>
# The file's extension decides md-vs-html; the terminal decides the backend.
set -euo pipefail

f="${1:-}"
[ -n "$f" ]  || { echo "open-render: no file given" >&2; exit 2; }
[ -e "$f" ]  || { echo "open-render: no such file: $f" >&2; exit 2; }

# Absolutize (backends want a real path; otty/plain reject file:// for local files).
case "$f" in
  /*) ;;
  *)  f="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")" ;;
esac

ext="$(printf '%s' "${f##*.}" | tr '[:upper:]' '[:lower:]')"
is_html=0
case "$ext" in html|htm) is_html=1 ;; esac

if   [ -n "${WAVETERM_JWT:-}" ] && command -v wsh  >/dev/null 2>&1; then host=wave
elif [ "${TERM_PROGRAM:-}" = otty ] && command -v otty >/dev/null 2>&1; then host=otty
else host=plain
fi

case "$host" in
  wave)
    if [ "$is_html" = 1 ]; then wsh web open "file://$f"; else wsh view "$f"; fi
    ;;
  otty)
    # otty view renders md+html in a read-only pane, but it can ONLY split the *focused* pane, and it
    # has no --pane flag. In a multi-session fleet the GUI-focused pane is usually NOT this session's
    # pane, so a plain `otty view --right` lands the preview in the wrong tab. Fix: target THIS
    # session's pane explicitly. The caller pane id comes from $OTTY_OPEN_PANE (Claude sets it after
    # correlating `otty pane list` against its own session) or positional $2.
    # We focus the caller, split-right to render there, then restore the user's prior focus so a
    # background /open never yanks them off the tab they're working in (set OTTY_OPEN_KEEP_FOCUS=1 to
    # stay on the preview instead). No caller id -> best-effort focused pane (legacy behavior).
    caller="${OTTY_OPEN_PANE:-${2:-}}"
    # Fall back to this Claude session's cached pane id (written once by /open|/check on first use;
    # keyed by the session id so concurrent sessions don't clobber each other).
    if [ -z "$caller" ]; then
      skey="${CODEX_COMPANION_SESSION_ID:-${CLAUDE_SESSION_ID:-}}"
      [ -n "$skey" ] && [ -f "$HOME/.cache/otty-open/$skey" ] && caller="$(cat "$HOME/.cache/otty-open/$skey" 2>/dev/null || true)"
    fi
    if [ -n "$caller" ]; then
      prev="$(otty pane show --json 2>/dev/null | grep -oE '"id"[^,]*' | head -1 | grep -oE 'p_[a-z0-9_]+' || true)"
      otty pane focus "$caller" >/dev/null 2>&1 || true
      otty view --right "$f" >/dev/null
      if [ "${OTTY_OPEN_KEEP_FOCUS:-0}" != 1 ] && [ -n "$prev" ] && [ "$prev" != "$caller" ]; then
        otty pane focus "$prev" >/dev/null 2>&1 || true
      fi
      if [ "${OTTY_OPEN_KEEP_FOCUS:-0}" = 1 ]; then _fmsg="kept on preview"; else _fmsg="restored to ${prev:-caller}"; fi
      echo "  (otty: rendered into caller pane $caller; focus $_fmsg)" >&2
    else
      otty view --right "$f" >/dev/null   # no caller id -> best-effort focused pane
    fi
    ;;
  plain)
    if [ "$is_html" = 1 ]; then
      if command -v open >/dev/null 2>&1; then open "$f"
      else echo "open manually (no GUI opener): $f" >&2; fi
    elif command -v glow >/dev/null 2>&1; then
      glow "$f"                 # non-tty -> renders markdown to stdout
    elif command -v open >/dev/null 2>&1; then
      open "$f"
    else
      cat "$f"
    fi
    ;;
esac

echo "rendered $f  (surface: $host)"
