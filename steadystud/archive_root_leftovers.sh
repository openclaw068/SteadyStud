#!/bin/bash
set -euo pipefail
ROOT='gdrive:SteadyStud - Business Project'
ARCH="$ROOT/_archive/2026-03-30/root-loose"

~/bin/rclone mkdir "$ARCH" >/dev/null

left=(
  "Executive Summary.docx"
  "Manufacturing & Finish Recommendation.docx"
  "SteadyStud — Sources & fact-check notes.docx"
)

for f in "${left[@]}"; do
  if ~/bin/rclone lsf "$ROOT" --include "$f" | grep -qx "$f"; then
    echo "Moving $f -> $ARCH"
    ~/bin/rclone moveto "$ROOT/$f" "$ARCH/$f"
  fi
done
