#!/usr/bin/env bash
set -euo pipefail
cd /home/node/.openclaw/workspace

# Run quote tracker
/home/node/.openclaw/workspace/.venv/bin/python steadystud/update_quote_tracker.py > steadystud/morning_summary.txt

# Upload outputs to Drive
~/bin/rclone copyto steadystud/quote_tracker_master.csv "gdrive:SteadyStud - Business Project/_current/02-RFQs/RFQs/SteadyStud - Quote Tracker.csv"
~/bin/rclone copyto steadystud/morning_summary.txt "gdrive:SteadyStud - Business Project/_current/02-RFQs/RFQs/morning_quote_summary.txt"

echo "OK"
