#!/usr/bin/env bash
# Regenerate every SteadyStud v3 output into ./out (inch-based).
set -euo pipefail
cd "$(dirname "$0")"
rm -rf out && mkdir out
python3 steadystud_v3.py
python3 draw_v3.py
python3 shop_files_v3.py
python3 print_v3.py
python3 render_v3.py
