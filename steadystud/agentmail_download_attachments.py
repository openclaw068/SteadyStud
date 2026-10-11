#!/usr/bin/env python3
"""Download all attachments from an AgentMail inbox and save locally.

- Lists messages
- Fetches full message
- For each attachment, fetches metadata to get download_url
- Downloads file bytes

Requires:
  export AGENTMAIL_API_KEY=...
"""

import os, json, urllib.request, urllib.parse, pathlib

BASE = "https://api.agentmail.to/v0"
INBOX_ID = "magstud@agentmail.to"
OUT_DIR = pathlib.Path("/home/node/.openclaw/workspace/steadystud/attachments")


def req_json(url: str) -> dict:
    key = os.getenv("AGENTMAIL_API_KEY")
    if not key:
        raise SystemExit("AGENTMAIL_API_KEY not set")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def req_bytes(url: str) -> tuple[bytes, str]:
    key = os.getenv("AGENTMAIL_API_KEY")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req) as resp:
        return resp.read(), resp.headers.get("Content-Type") or "application/octet-stream"


def list_messages(limit=50, max_pages=500):
    page_token = None
    pages = 0
    while pages < max_pages:
        params = {"limit": limit}
        if page_token:
            params["page_token"] = page_token
        url = f"{BASE}/inboxes/{INBOX_ID}/messages?" + urllib.parse.urlencode(params)
        data = req_json(url)
        msgs = data.get("messages") or []
        if not msgs:
            return
        for m in msgs:
            yield m
        page_token = data.get("next_page_token")
        pages += 1
        if not page_token:
            return


def get_message(mid: str) -> dict:
    midq = urllib.parse.quote(mid, safe="")
    return req_json(f"{BASE}/inboxes/{INBOX_ID}/messages/{midq}")


def get_attachment(mid: str, aid: str) -> dict:
    midq = urllib.parse.quote(mid, safe="")
    return req_json(f"{BASE}/inboxes/{INBOX_ID}/messages/{midq}/attachments/{aid}")


def safe_filename(s: str) -> str:
    s = s.replace("/", "_").replace("\\", "_")
    return s


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT_DIR / "manifest.jsonl"
    count_files = 0
    count_msgs = 0

    with manifest_path.open("w", encoding="utf-8") as mf:
        for meta in list_messages():
            mid = meta.get("message_id")
            if not mid:
                continue
            full = get_message(mid)
            atts = full.get("attachments") or []
            if not atts:
                continue
            count_msgs += 1

            for a in atts:
                aid = a.get("attachment_id")
                if not aid:
                    continue
                info = get_attachment(mid, aid)
                url = info.get("download_url")
                fname = safe_filename(info.get("filename") or f"attachment_{aid}")

                # prefix with date + short message id hash to avoid collisions
                created = (full.get("created_at") or "").replace(":", "-")
                prefix = created[:10] if created else "unknown-date"
                outname = f"{prefix}__{aid}__{fname}"
                outpath = OUT_DIR / outname

                if url:
                    data, ctype = req_bytes(url)
                    outpath.write_bytes(data)
                    count_files += 1
                    mf.write(json.dumps({
                        "message_id": mid,
                        "thread_id": full.get("thread_id"),
                        "created_at": full.get("created_at"),
                        "from": full.get("from"),
                        "subject": full.get("subject"),
                        "attachment_id": aid,
                        "filename": fname,
                        "saved_as": outname,
                        "content_type": info.get("content_type") or ctype,
                        "size": info.get("size"),
                    }, ensure_ascii=False) + "\n")

    print(f"Downloaded {count_files} attachments from {count_msgs} messages to {OUT_DIR}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
