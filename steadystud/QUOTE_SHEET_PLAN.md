# SteadyStud — Quote spreadsheet plan (AgentMail magstud@agentmail.to)

## Where the current CSVs are
Drive folder: `SteadyStud - Business Project/RFQs/agentmail/quotes/`
- `extracted_quotes.csv` — 34 quote-ish messages (triage)
- `online_submission_list.csv` — 3 items flagged as “requires online submission” (currently these are our outbound RFQ copies; we’ll refine)

## Next step: turn this into an actual Google Sheet
Because our Google OAuth refresh token is currently failing (`invalid_grant`), the fastest reliable path is:
1. Upload/maintain CSV in Drive (done)
2. Convert CSV → Google Sheet either:
   - manually once (Drive UI: open CSV → File → Save as Google Sheets), or
   - via Apps Script, once OAuth is fixed

## Proposed columns for the Sheet
- Vendor / Company
- Vendor contact name
- Vendor email
- Quote / RFQ reference #
- Part description / scope
- Qty
- Unit price
- NRE / setup
- Tooling
- Lead time
- Shipping / Incoterms
- Valid until
- Notes
- Requires online submission? (Y/N)
- Online submission URL / portal
- Source message_id
- Thread_id
- Received date

## Refinement needed
Most of the 34 rows are not actual pricing lines; several vendors send quotes as PDFs/attachments.
Next iteration should:
- fetch + download attachments
- run text extraction on PDFs
- parse structured fields (MOQ, lead time, unit price)

I can proceed with attachment harvesting next.
