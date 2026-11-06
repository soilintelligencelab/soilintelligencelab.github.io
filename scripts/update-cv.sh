#!/bin/bash
# Copies Feng's CV from the CV-Latex repository into the site (assets/pdf/cv-fengtao.pdf), the file the
# People page links to. Run it before every build or push; the CV-Latex copy is always the source.
set -euo pipefail
SRC="${CV_SOURCE:-$HOME/GitHub/CV-Latex/cv-fengtao.pdf}"
DST="$(cd "$(dirname "$0")/.." && pwd)/assets/pdf/cv-fengtao.pdf"
[ -f "$SRC" ] || { echo "CV not found: $SRC" >&2; exit 1; }
mkdir -p "$(dirname "$DST")"
if [ -f "$DST" ] && cmp -s "$SRC" "$DST"; then
  echo "CV already up to date ($(date -r "$SRC" '+%Y-%m-%d %H:%M'))"
else
  cp "$SRC" "$DST"
  echo "CV updated from $SRC ($(date -r "$SRC" '+%Y-%m-%d %H:%M'))"
fi
