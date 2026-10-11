#!/bin/bash
set -euo pipefail
ROOT='gdrive:SteadyStud - Business Project'
ARCH="$ROOT/_archive/2026-03-30/root-loose"

# Move loose root files (docs/xlsx/pptx/md) into archive, leaving the main folders.
files=(
  "36mo_model.xlsx"
  "assumptions.xlsx"
  "Business Plan.docx" "Business Plan.md"
  "Competitive Analysis.docx" "Competitive Analysis.md"
  "Executive Summary.docx" "Executive Summary.md"
  "Growth Strategy Analysis.docx" "Growth Strategy Analysis.md"
  "Manufacturing & Finish Recommendation.docx"
  "Market Research.docx" "Market Research.md"
  "Marketing Plan.docx" "Marketing Plan.md"
  "One-Pager.docx" "One-Pager.md"
  "Pitch Deck.md" "Pitch Deck.pptx"
  "Product Development Roadmap.docx" "Product Development Roadmap.md"
  "Product Requirements Document (PRD).docx" "Product Requirements Document (PRD).md"
  "SteadyStud u2014 Sources & fact-check notes.md"
  "SteadyStud — Sources & fact-check notes.docx"
)

~/bin/rclone mkdir "$ARCH" >/dev/null

for f in "${files[@]}"; do
  # move if exists
  if ~/bin/rclone lsf "$ROOT" --include "$f" | grep -qx "$f"; then
    echo "Moving $f -> $ARCH"
    ~/bin/rclone moveto "$ROOT/$f" "$ARCH/$f"
  fi
done
