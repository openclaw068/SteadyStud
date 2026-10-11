#!/usr/bin/env python3
"""SteadyStud Quote Tracker

Goal:
- Pull new quote-ish messages from AgentMail (magstud@agentmail.to)
- Update the master comparison sheet CSV in Drive
- Emit a concise morning summary

Design notes:
- We keep state in memory/agentmail-magstud-seen.json (message_id -> processedAt)
- We do *light* extraction from email body (money mentions + key lines)
- Attachments: AgentMail API attachment download is not implemented here yet.
  For now we link/mention known attachments if they exist in the Drive quotes/attachments folder.

Outputs (local workspace):
- steadystud/quote_tracker_master.csv
- steadystud/morning_summary.txt

Then the caller uploads to Drive path:
SteadyStud - Business Project/_current/02-RFQs/RFQs/SteadyStud - Quote Tracker.csv
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.agentmail.to/v0"
INBOX_ID = "magstud@agentmail.to"

QUOTE_PATTERNS = [
    r"\bquote\b",
    r"\bquotation\b",
    r"\bpricing\b",
    r"\bprice\b",
    r"\bunit price\b",
    r"\bmoq\b",
    r"\blead time\b",
    r"\btooling\b",
    r"\bnre\b",
]

MONEY_RE = re.compile(
    r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|usd)\b"
)

KEYLINE_WORDS = [
    "moq",
    "lead",
    "turnaround",
    "unit",
    "price",
    "setup",
    "nre",
    "tooling",
    "shipping",
    "qty",
]

STATE_PATH = Path("/home/node/.openclaw/workspace/memory/agentmail-magstud-seen.json")
WORKDIR = Path("/home/node/.openclaw/workspace")
ATTACH_DIR = WORKDIR / "steadystud" / "attachments"

DRIVE_QUOTES_ATTACH_DIR = "gdrive:SteadyStud - Business Project/_current/02-RFQs/RFQs/agentmail/quotes/attachments"


def _load_env_if_needed() -> None:
    """Load AGENTMAIL_API_KEY from workspace .secrets/agentmail.env if not already set."""
    if os.getenv("AGENTMAIL_API_KEY"):
        return
    env_path = Path("/home/node/.openclaw/workspace/.secrets/agentmail.env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v and not os.getenv(k):
            os.environ[k] = v


def api_get(url: str) -> dict:
    _load_env_if_needed()
    key = os.getenv("AGENTMAIL_API_KEY")
    if not key:
        raise SystemExit("AGENTMAIL_API_KEY not set (missing env and .secrets/agentmail.env)")

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_list_messages(limit_per_page=50, max_pages=200):
    page_token = None
    pages = 0
    while pages < max_pages:
        params = {"limit": limit_per_page}
        if page_token:
            params["page_token"] = page_token
        url = f"{BASE}/inboxes/{INBOX_ID}/messages?" + urllib.parse.urlencode(params)
        data = api_get(url)
        msgs = data.get("messages") or data.get("items") or []
        if not msgs:
            return
        for m in msgs:
            yield m
        page_token = data.get("next_page_token")
        pages += 1
        if not page_token:
            return


def api_get_message(message_id: str) -> dict:
    mid = urllib.parse.quote(message_id, safe="")
    url = f"{BASE}/inboxes/{INBOX_ID}/messages/{mid}"
    return api_get(url)


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def get_text(m: dict) -> str:
    return m.get("extracted_text") or m.get("text") or m.get("body") or m.get("preview") or ""


def norm_from(m: dict) -> str:
    f = m.get("from")
    if isinstance(f, list) and f:
        f = f[0]
    if isinstance(f, dict):
        # sometimes {email,name}
        email = f.get("email") or ""
        name = f.get("name") or ""
        return f"{name} <{email}>".strip()
    return str(f or "")


def looks_quoteish(subject: str, text: str) -> bool:
    hay = (subject + "\n" + text).lower()
    if MONEY_RE.search(text):
        return True
    return any(re.search(p, hay) for p in QUOTE_PATTERNS)


def extract_keylines(text: str, max_lines=6) -> str:
    out = []
    for line in text.splitlines():
        ll = line.lower().strip()
        if not ll:
            continue
        if MONEY_RE.search(line) or any(w in ll for w in KEYLINE_WORDS):
            s = re.sub(r"\s+", " ", line.strip())
            if s and s not in out:
                out.append(s)
        if len(out) >= max_lines:
            break
    return " | ".join(out)[:700]


def money_mentions(text: str) -> str:
    found = []
    for m in MONEY_RE.finditer(text):
        found.append(m.group(0))
    seen = set()
    uniq = [x for x in found if not (x in seen or seen.add(x))]
    return ", ".join(uniq)[:200]


def sync_drive_attachments() -> None:
    """Best-effort: mirror Drive attachments into local steadystud/attachments."""
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [str(Path.home() / "bin" / "rclone"), "copy", DRIVE_QUOTES_ATTACH_DIR, str(ATTACH_DIR), "--ignore-existing"]
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def list_local_attachments() -> set[str]:
    if not ATTACH_DIR.exists():
        return set()
    return {p.name for p in ATTACH_DIR.iterdir() if p.is_file()}


def build_tracker_rows(messages: list[dict], attachments: set[str]) -> list[dict]:
    rows = []
    for m in messages:
        subject = m.get("subject") or ""
        text = get_text(m)
        frm = norm_from(m)
        created = m.get("created_at") or m.get("date") or ""
        mid = m.get("message_id") or m.get("id") or ""
        tid = m.get("thread_id") or ""

        rows.append(
            {
                "vendor": frm,
                "email_subject": subject,
                "received_at": created,
                "status": "new" if mid else "",
                "money_mentions": money_mentions(text),
                "key_lines": extract_keylines(text),
                "message_id": mid,
                "thread_id": tid,
                "attachments_found": "",  # filled below
                "unit_100": "",
                "unit_200": "",
                "unit_500": "",
                "unit_1000": "",
                "setup_nre": "",
                "lead_time": "",
                "shipping": "",
                "notes": "",
            }
        )

    # crude attachment association: if quote PDF exists, just list all quote PDFs for now
    quote_like = sorted([a for a in attachments if a.lower().endswith((".pdf", ".xlsx", ".csv", ".docx"))])
    for r in rows:
        # Keep small; we mostly care if *any* attachments exist.
        r["attachments_found"] = "; ".join(quote_like[:6])
        if len(quote_like) > 6:
            r["attachments_found"] += f"; (+{len(quote_like)-6} more)"
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    """Default mode: incremental update.

    FULL_REBUILD=1 will ignore state and rebuild the tracker from all quote-ish messages.
    """

    full_rebuild = os.getenv("FULL_REBUILD") in ("1", "true", "yes")

    state = load_state() if not full_rebuild else {}
    processed = set(state.keys())

    sync_drive_attachments()
    attachments = list_local_attachments()

    new_msgs = []
    total_seen = 0

    for meta in api_list_messages():
        mid = meta.get("message_id") or meta.get("id")
        if not mid:
            continue
        total_seen += 1

        if (not full_rebuild) and (mid in processed):
            continue

        full = api_get_message(mid)
        subject = full.get("subject") or ""
        text = get_text(full)

        if not looks_quoteish(subject, text):
            if not full_rebuild:
                state[mid] = {"skippedAt": int(dt.datetime.now(dt.UTC).timestamp() * 1000)}
            continue

        new_msgs.append(full)
        if not full_rebuild:
            state[mid] = {"processedAt": int(dt.datetime.now(dt.UTC).timestamp() * 1000)}

    if not full_rebuild:
        save_state(state)

    rows = build_tracker_rows(new_msgs, attachments)

    out_csv = WORKDIR / "steadystud" / "quote_tracker_master.csv"
    out_txt = WORKDIR / "steadystud" / "morning_summary.txt"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "vendor",
        "email_subject",
        "received_at",
        "status",
        "money_mentions",
        "key_lines",
        "message_id",
        "thread_id",
        "attachments_found",
        "unit_100",
        "unit_200",
        "unit_500",
        "unit_1000",
        "setup_nre",
        "lead_time",
        "shipping",
        "notes",
    ]

    if full_rebuild:
        # overwrite from scratch
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in rows:
                w.writerow(r)
    else:
        # Ensure file exists w/ headers
        if not out_csv.exists():
            with out_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(headers)
        # Append new rows
        if rows:
            with out_csv.open("a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=headers)
                for r in rows:
                    w.writerow(r)

    # summary
    lines = []
    lines.append(f"SteadyStud quote tracker — {dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"New quote-ish emails since last run: {len(new_msgs)}")
    if rows:
        lines.append("")
        for r in rows[:10]:
            lines.append(f"- {r['received_at'][:10]} | {r['vendor']} | {r['email_subject']} | {r['money_mentions']}")
        if len(rows) > 10:
            lines.append(f"(+{len(rows)-10} more)")
    else:
        lines.append("No new quote-ish emails found.")
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out_txt.read_text(encoding='utf-8'))


if __name__ == "__main__":
    main()
