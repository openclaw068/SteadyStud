#!/usr/bin/env python3
"""Send RFQ emails to portal-first targets using email fallback.

We already sent to the email-friendly 4 targets.
This script sends to:
- Empire Group USA
- All Metals Fabricating
- Dynamic Design & Manufacturing
- JLCCNC

Requires:
  export AGENTMAIL_API_KEY=...
"""

import os, json, base64, urllib.request

BASE = "https://api.agentmail.to/v0"
INBOX_ID = "magstud@agentmail.to"
SHIP_TO = "55117, USA"
QTY_LADDER = "50 / 100 / 500 / 1000"

TO_LIST = [
    {"company": "Empire Group USA", "to": ["info@empirepd.com"], "portal": "https://info.empiregroupusa.com/request-a-quote"},
    {"company": "All Metals Fabricating", "to": ["info@ametals.com"], "portal": "https://www.ametals.com/request-for-quote"},
    {"company": "Dynamic Design & Manufacturing", "to": ["rfq@dycoinc.com"], "portal": "https://www.dycoinc.com/request-a-quote.html"},
    {"company": "JLCCNC", "to": ["support@jlcpcb.com"], "portal": "https://jlccnc.com/help/contact"},
]

ATTACH_PATHS = [
    "/home/node/.openclaw/workspace/steadystud/rfq_files/Magnetic Stud Finer v1.step",
    "/home/node/.openclaw/workspace/steadystud/rfq_files/Magnetic Stud Finer v1 v2.dxf",
    "/home/node/.openclaw/workspace/steadystud/rfq_files/2026-03-17__037f37b3-56c0-4062-bf5f-1efe351ddcb5__SteadyStud_2D_Top_View_APPROVED.pdf",
    "/home/node/.openclaw/workspace/steadystud/rfq_files/2026-03-14__0c21ed18-1775-480b-9f7f-7311841da8c3__Magnetic_Stud_Finder_RFQ_Spec.pdf",
]


def guess_mime(path: str) -> str:
    p = path.lower()
    if p.endswith('.pdf'):
        return 'application/pdf'
    if p.endswith('.dxf'):
        return 'application/dxf'
    if p.endswith('.step') or p.endswith('.stp'):
        return 'model/step'
    return 'application/octet-stream'


def load_attachments():
    out = []
    for p in ATTACH_PATHS:
        if not os.path.exists(p):
            raise SystemExit(f"Missing attachment: {p}")
        data = open(p, 'rb').read()
        out.append({
            "filename": os.path.basename(p),
            "content": base64.b64encode(data).decode('ascii'),
            "content_type": guess_mime(p),
        })
    return out


def send(to_emails, subject, text, attachments):
    key = os.getenv('AGENTMAIL_API_KEY')
    if not key:
        raise SystemExit('AGENTMAIL_API_KEY not set')

    url = f"{BASE}/inboxes/{INBOX_ID}/messages/send"
    payload = {
        "to": to_emails,
        "subject": subject,
        "text": text,
        "attachments": attachments,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def build_body(company: str, portal: str) -> str:
    return f"""Hi {company} team,\n\nWe’re requesting an RFQ for a small metal product component for our project “SteadyStud.” We want one supplier who can do BOTH fabrication and laser logo marking (logo only).\n\nShip-to: {SHIP_TO}\nQuantities: {QTY_LADDER}\n\nPlease quote BOTH manufacturing approaches (as two line items / alternatives):\nA) CNC machined option (e.g., 6061 aluminum or stainless; raw finish is fine)\nB) Sheet metal option (laser cut/punch + bend as needed; recommend alloy + thickness; raw finish is fine)\n\nMarking requirement (both options):\n- Laser logo marking on metal (logo only; no serial numbers)\n- Please include any one-time setup/marking-programming fee + per-part marking cost\n- Please confirm laser type used for marking on metal (fiber preferred) and expected contrast on raw aluminum/stainless\n\nPlease include in your quote:\n1) Unit price at each quantity + any NRE/setup/tooling fees\n2) Lead time for first article/prototype and production\n3) Material recommendation + any DFM notes\n4) Shipping cost (or assumptions) to {SHIP_TO}\n\nCAD files are attached (STEP + DXF) along with a 2D top view and RFQ spec PDF.\n\nIf you prefer we submit via your online portal, we can do that as well: {portal}\n\nThanks,\nGrayson\nSteadyStud\n"""


def main():
    attachments = load_attachments()
    results = []
    for entry in TO_LIST:
        company = entry['company']
        subject = f"RFQ — SteadyStud — metal part + laser logo marking — Qty {QTY_LADDER}"
        body = build_body(company, entry['portal'])
        res = send(entry['to'], subject, body, attachments)
        results.append({"company": company, "to": entry['to'], "portal": entry['portal'], "result": res})
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
