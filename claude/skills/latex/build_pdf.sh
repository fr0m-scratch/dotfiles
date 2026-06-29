#!/usr/bin/env bash
# Formal Markdown -> PDF via pandoc + xelatex (xeCJK). Part of the /latex skill.
#
# Usage:
#   build_pdf.sh <input.md> <output.pdf> ["Title"] ["Subtitle"] ["DocID"] ["Version"]
#
# Produces a dry, print-grade, formal document: numbered sections, TOC, A4,
# header(DocID)/footer(page+status), Songti (宋体) serif for CJK, Menlo mono for
# code, fvextra line-wrapping so code never overflows the page, monochrome
# syntax highlighting. Override fonts/footer via env: CJK_FONT, CJK_SANS,
# MONO_FONT, FOOTER.
set -euo pipefail

MD="${1:?input markdown required}"
OUT="${2:?output pdf required}"
TITLE="${3:-}"; SUB="${4:-}"; DOCID="${5:-}"; VER="${6:-}"
FOOTER="${FOOTER:-Draft}"

# --- locate xelatex (TinyTeX install or system PATH) ----------------------
for p in \
  "$HOME/Library/TinyTeX/bin/universal-darwin" \
  "$HOME/Library/TinyTeX/bin/x86_64-darwin" \
  "$HOME/Library/TinyTeX/bin/aarch64-darwin" \
  "$HOME/.TinyTeX/bin/universal-linux" \
  "$HOME/.TinyTeX/bin/x86_64-linux" \
  "$HOME/bin"; do
  [ -x "$p/xelatex" ] && PATH="$p:$PATH"
done

command -v pandoc  >/dev/null || { echo "build_pdf: pandoc not found — install: brew install pandoc" >&2; exit 1; }
command -v xelatex >/dev/null || { echo "build_pdf: xelatex not found — install TinyTeX (https://yihui.org/tinytex/) then: tlmgr install fvextra fancyhdr sectsty lineno footnotehyper xurl" >&2; exit 1; }

# --- fonts: pick the first installed candidate (override via env) ----------
pick_font(){ for f in "$@"; do if fc-list 2>/dev/null | grep -qi "$f"; then echo "$f"; return; fi; done; echo "$1"; }
CJK_FONT="${CJK_FONT:-$(pick_font "Songti SC" "Noto Serif CJK SC" "Source Han Serif SC" "STSong")}"
CJK_SANS="${CJK_SANS:-$(pick_font "PingFang SC" "Noto Sans CJK SC" "Heiti SC")}"
MONO_FONT="${MONO_FONT:-$(pick_font "Menlo" "DejaVu Sans Mono" "Consolas")}"

WORK="$(mktemp -d)"; HDR="$WORK/hdr.tex"; DOC="$WORK/doc.md"
trap 'rm -rf "$WORK"' EXIT

cat > "$HDR" <<EOF
\\usepackage{fontspec}
\\usepackage{xeCJK}
\\setCJKmainfont{$CJK_FONT}
\\setCJKsansfont{$CJK_SANS}
\\setCJKmonofont{$CJK_SANS}
\\setmonofont{$MONO_FONT}[Scale=0.85]
\\usepackage{fvextra}
\\fvset{breaklines=true,breakanywhere=true,fontsize=\\footnotesize}
\\usepackage{etoolbox}
\\AtBeginEnvironment{longtable}{\\footnotesize}
\\usepackage{fancyhdr}
\\pagestyle{fancy}
\\fancyhf{}
\\fancyhead[L]{\\footnotesize\\sffamily ${DOCID}}
\\fancyhead[R]{\\footnotesize\\sffamily \\thepage}
\\fancyfoot[C]{\\footnotesize\\sffamily ${FOOTER}}
\\renewcommand{\\headrulewidth}{0.4pt}
\\renewcommand{\\footrulewidth}{0.2pt}
\\usepackage{sectsty}
\\sectionfont{\\large}
\\subsectionfont{\\normalsize}
\\setlength{\\parskip}{0.45em}
\\setlength{\\parindent}{0pt}
EOF

# Build a YAML metadata header (title/subtitle/date) then the body.
DATELINE=""
[ -n "$DOCID" ] && DATELINE="$DOCID"
[ -n "$VER" ] && DATELINE="${DATELINE:+$DATELINE · }$VER"
{
  echo "---"
  [ -n "$TITLE" ] && echo "title: \"$TITLE\""
  [ -n "$SUB" ]   && echo "subtitle: \"$SUB\""
  [ -n "$DATELINE" ] && echo "date: \"$DATELINE\""
  echo "---"
  echo
  cat "$MD"
} > "$DOC"

pandoc "$DOC" -o "$OUT" --pdf-engine=xelatex \
  -V geometry:a4paper,margin=2.4cm \
  -V fontsize=11pt -V colorlinks=false -V linkcolor=black -V urlcolor=black \
  --toc --toc-depth=2 --number-sections \
  --highlight-style=monochrome \
  -H "$HDR"

echo "build_pdf: wrote $OUT  (cjk=$CJK_FONT mono=$MONO_FONT)"
