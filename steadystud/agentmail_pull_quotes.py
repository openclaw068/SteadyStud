#!/usr/bin/env python3
"""Pull messages from AgentMail inbox and extract quote-ish info to CSV.

Outputs:
- extracted_quotes.csv
- online_submission_list.csv
- raw_messages.jsonl (for audit)

Requires:
  export AGENTMAIL_API_KEY=...

Notes:
- Uses AgentMail REST API directly (no SDK dependency).
- Fetches message list, then fetches full message bodies for quote extraction.
"""

import os
import re
import csv
import json
import urllib.request
import urllib.parse

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
]

ONLINE_PATTERNS = [
    r"submit (an? )?rfq",
    r"submit (a )?quote",
    r"online (form|portal)",
    r"request a quote",
    r"rfq form",
    r"fill out",
    r"portal",
]

MONEY_RE = re.compile(
    r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|usd)\b",
)


def api_get(url: str) -> dict:
    key = os.getenv("AGENTMAIL_API_KEY")
    if not key:
        raise SystemExit("AGENTMAIL_API_KEY not set")

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_list_messages(limit_per_page=50, max_pages=500):
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


def normalize_email(addr) -> str:
    if not addr:
        return ""
    if isinstance(addr, dict):
        return addr.get("email") or ""
    return str(addr)


def get_text(m: dict) -> str:
    # prefer extracted_text if present
    return m.get("extracted_text") or m.get("text") or m.get("body") or m.get("preview") or ""


def summarize_quote(m: dict) -> dict:
    text = get_text(m)
    lower = text.lower()

    lines = []
    for line in text.splitlines():
        ll = line.lower()
        if MONEY_RE.search(line) or any(k in ll for k in ["moq", "lead", "unit", "price", "setup", "tooling", "shipping"]):
            s = line.strip()
            if s:
                lines.append(s)

    snippet = " | ".join(lines)[:700]

    money_mentions = []
    for s in MONEY_RE.finditer(text):
        money_mentions.append(s.group(0))
    seen = set()
    money_mentions = [x for x in money_mentions if not (x in seen or seen.add(x))]

    requires_online = any(re.search(p, lower) for p in ONLINE_PATTERNS)

    return {
        "requires_online_submission": "yes" if requires_online else "no",
        "money_mentions": ", ".join(money_mentions)[:200],
        "quote_snippet": snippet,
    }


def main():
    os.makedirs("/home/node/.openclaw/workspace/steadystud", exist_ok=True)

    out_quotes = "/home/node/.openclaw/workspace/steadystud/extracted_quotes.csv"
    out_online = "/home/node/.openclaw/workspace/steadystud/online_submission_list.csv"
    out_raw = "/home/node/.openclaw/workspace/steadystud/raw_messages.jsonl"

    quotes_rows = []
    online_rows = []

    with open(out_raw, "w", encoding="utf-8") as rawf:
        for meta in api_list_messages():
            mid = meta.get("message_id") or meta.get("id")
            if not mid:
                continue

            full = api_get_message(mid)
            rawf.write(json.dumps(full, ensure_ascii=False) + "\n")

            subject = full.get("subject") or ""
            text = get_text(full)
            hay = (subject + "\n" + text).lower()

            if not any(re.search(p, hay) for p in QUOTE_PATTERNS) and not MONEY_RE.search(text):
                continue

            frm = ""
            from_field = full.get("from")
            if isinstance(from_field, list) and from_field:
                frm = normalize_email(from_field[0])
            else:
                frm = normalize_email(from_field)

            summary = summarize_quote(full)

            row = {
                "message_id": full.get("message_id") or "",
                "thread_id": full.get("thread_id") or "",
                "date": full.get("created_at") or full.get("date") or "",
                "from": frm,
                "subject": subject,
                "requires_online_submission": summary["requires_online_submission"],
                "money_mentions": summary["money_mentions"],
                "quote_snippet": summary["quote_snippet"],
            }
            quotes_rows.append(row)
            if row["requires_online_submission"] == "yes":
                online_rows.append(row)

    fieldnames = [
        "message_id",
        "thread_id",
        "date",
        "from",
        "subject",
        "requires_online_submission",
        "money_mentions",
        "quote_snippet",
    ]

    with open(out_quotes, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(quotes_rows)

    with open(out_online, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(online_rows)

    print(f"Wrote {len(quotes_rows)} quote-ish rows to {out_quotes}")
    print(f"Wrote {len(online_rows)} online-submission rows to {out_online}")
    print(f"Raw messages saved to {out_raw}")


if __name__ == "__main__":
    main()
