# SteadyStud

**SteadyStud** is a no-battery magnetic stud finder with a built-in marking notch — find a fastener, mark immediately without swapping tools. Target customer: everyday DIYers who want confidence, not a contractor-grade tool.

---

## What Makes It Different

Most magnetic stud finders are commodity hardware. SteadyStud's edge is a **dedicated marking notch** that lets you mark your spot the moment you feel the snap — no finger-hold, no reaching for a pencil with your other hand.

Core pitch: *"Slide → Snap → Mark → Hang — right the first time."*

---

## Product

| Attribute | Detail |
|-----------|--------|
| Form factor | 5.0-inch flat aluminum body |
| Power | None — pure permanent magnets |
| Key feature | Built-in marking notch for pens/Sharpies |
| Materials | 6061-T6 aluminum (target), plastic prototype exists |
| Finish | Anodized Type II (per received quote) |
| Logo | Laser-etched |
| Prototype status | 3D-printed plastic — works; needs metal production unit |

**Honest claim constraint:** Magnetic stud finders detect **metal fasteners** (nails, screws), not wood directly. Do not imply wire detection or guaranteed stud center without confirmation steps.

---

## Stage

**Mid-diligence / pre-production.** Manufacturing RFQs have been sent and one quote has been received. The biggest open questions are manufacturing cost, supplier selection, and go-to-market execution.

---

## Project Structure

```
steadystud/                  ← Active RFQ tracking, email drafts, vendor attachments, scripts
steadystud_docs/             ← Full business research (all markdown)
steadystud_financials/       ← 36-month financial model + assumptions
audits/                      ← Raw CAD files (STEP/DXF/DWG), vendor RFQ docs, supplier quote sheets
memory-projects-steadystud/  ← Orchestrator pipeline state + quotes tracker
```

### Key docs to read first

- `steadystud_docs/00 - Intake & Notes/SteadyStud - Intake.md` — how the project started, what was provided
- `steadystud_docs/02 - Product & Design/SteadyStud - Product Spec.md` — product definition and constraints
- `steadystud_docs/04 - Branding & Positioning/SteadyStud - Positioning.md` — brand voice, positioning statement, truth-in-advertising guardrails
- `steadystud_docs/05 - Go-To-Market & Channels/SteadyStud - Channels Strategy.md` — DTC-first, Amazon-avoid, independent hardware phase 2
- `steadystud_docs/06 - Financial Model/SteadyStud - Unit Economics.md` — pricing anchors ($16.99–$19.99 DTC MSRP)
- `memory-projects-steadystud/quotes-tracker.json` — live RFQ status

---

## Manufacturing

### RFQ Status (as of April 2026)

| Supplier | Status | Notes |
|----------|--------|-------|
| Pittsburgh Laser Cutting | ✅ Quote received | $153–$425/unit (50–1000 qty), 6061-T6 alum, anodized Type II. **Quote expired 3/31 — needs reconfirmation** |
| Approved Sheet Metal | ⏳ May reconsider | Contact: Shane Van Heerden, 603-288-5371 |
| JLCPCB / JLCCNC | ⏳ Needs upload | Portal: jlccnc.com/sheet-metal-quote |
| Decimal | ❌ Declined | — |
| Dyco Inc | ❌ Email bounced | — |
| Fictiv | ⚠️ Marketing only | Consider uploading specs at fictiv.com |

### Contact: Shane Van Heerden — Approved Sheet Metal
- **Phone:** 603-288-5371
- **Email:** svheerden@approvedsheetmetal.com
- May reconsider with adjusted specs. **This is the highest-priority re-engagement.**

### CAD Files (authoritative)
- `audits/Magnetic Stud Finer v1.step` — primary reference for all dimensions
- `audits/Magnetic Stud Finer v1 v2.dxf` — 2D export
- `audits/SteadyStud_2D_Top_View_APPROVED.pdf` — approved 2D drawing

---

## Open Questions (Priority Order)

1. **Reconfirm Pittsburgh Laser Cutting quote** — expired 3/31. Contact Jason: jason@pittsburghlasercutting.com, +1 412-204-6293
2. **Call Shane @ Approved Sheet Metal** (603-288-5371) — highest-leverage re-engagement
3. **Upload to JLCPCB portal** — jlccnc.com/sheet-metal-quote
4. **Decide on finish + marking method** — anodize + laser etch is the default path; is there a cheaper route that still looks premium?
5. **Tighten target BOM + margin requirements** — what does the financial model need to be healthy?
6. **Decide on design patent timing** — prior art scan before broad launch?
7. **Validate magnet + glide feel** — prototype testing for snap strength and wall safety

---

## Positioning

**Statement:** SteadyStud helps everyday DIYers hang things right the first time — no batteries, no calibration, just slide and snap.

**Channels:** DTC-first → independent hardware (ACE, True Value) → big-box if velocity proves out

**Avoid:** Amazon (fees + race to bottom on a commodity category)

**DTC price target:** $16.99–$19.99

---

## Financials

See `steadystud_financials/`:
- `assumptions.csv` / `assumptions.xlsx` — cost and pricing assumptions
- `36mo_model.csv` / `36mo_model.xlsx` — three-year projection
- `retail_unit_economics_notes.md` — DTC vs wholesale unit economics

**Key anchors:** Commodity competitors (e.g., StudBuddy) sit ~$10–$14. SteadyStud needs to justify $16.99+ through the notch UX and brand clarity.

---

## Experiments Planned

1. **DIY usability test** — 10–15 participants, measure time-to-confident-mark and error rate
2. **Packaging comprehension test** — can someone understand it in 10 seconds from the box?
3. **Magnet + glide tuning** — 2–4 configs, balance snap feel vs wall safety
4. **Price + offer test (DTC)** — $14.99 vs $16.99 vs $19.99; standalone vs Hang Kit bundle

---

## Brand Guardrails

- Magnetic finders detect **fasteners**, not wood directly
- Do not claim: wire detection, guaranteed stud center, deep scanning
- OK to claim: find fasteners, no batteries, no calibration, built-in mark, wall-safe glide

---

## Owner

Grayson McCormick — primary contact for this project.
