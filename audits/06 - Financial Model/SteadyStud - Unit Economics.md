# SteadyStud — Unit economics (template v0.2)

## Known external price anchor (to validate)
A major magnetic stud finder (StudBuddy) appears listed at **$10.97** at Home Depot (per public listing snippet).

Source: https://www.homedepot.com/p/The-StudBuddy-Magnetic-Stud-Finder-000107/205554450 (price seen in search snippet; confirm via additional sources)

## Pricing hypotheses (starting point)
- Value SKU (plastic): $9.99–$14.99
- Premium SKU (aluminum): $14.99–$24.99

(We’ll refine after competitor price mapping and COGS estimates.)

## Estimated COGS (v2 placeholder — replace with supplier quotes)
Below is a *directional* unit-level COGS estimate for the premium aluminum SKU. It is meant to (1) stress-test margin at plausible price points and (2) define the exact quote line-items to request from suppliers.

> **Important:** These are not quotes. Treat this as a model to be overwritten by real RFQ responses.

### Estimated COGS per unit (Best / Base / Worst)
| Line item | Best | Base | Worst |
|---|---:|---:|---:|
| Raw material (6061 plate) | $0.90 | $1.25 | $1.80 |
| Machining / laser-cut / CNC | $1.50 | $2.50 | $4.00 |
| Magnets (NdFeB + coating) | $0.80 | $1.20 | $2.00 |
| Finishing (anodize/coat) | $0.80 | $1.20 | $2.00 |
| Packaging (box + insert + label) | $0.40 | $0.75 | $1.25 |
| Assembly labor | $0.35 | $0.60 | $1.00 |
| QA / inspection | $0.15 | $0.25 | $0.45 |
| Scrap allowance | $0.20 | $0.45 | $1.20 |
| Inbound freight | $0.20 | $0.40 | $0.80 |
| Payment fees (DTC placeholder) | $0.70 | $0.88 | $1.05 |
| Returns allowance (placeholder) | $0.20 | $0.40 | $0.80 |
| **TOTAL COGS / unit** | **$6.20** | **$9.88** | **$16.35** |

### What this implies at MSRP $19.99 (COGS-only gross margin)
- **Best:** 69.0% gross margin (COGS $6.20)
- **Base:** 50.6% gross margin (COGS $9.88)
- **Worst:** 18.2% gross margin (COGS $16.35)

### Channel fees note (why Amazon can be tight)
If selling on Amazon with a typical fee stack (illustrative):
- Referral fee: ~15% of price
- Fulfillment: ~$4.00/unit
- Inbound-to-FBA: ~$0.50/unit

At **$19.99**, that’s about **$7.50/unit** before ads. With **Base COGS $9.88**, contribution is roughly **$2.61/unit** before PPC.

## Inputs to collect (to replace estimates)
### COGS
- Magnets (unit cost, grade/coating, count per unit)
- Body: cut method + any CNC secondary ops
- Finishing: anodize cost + laser mark cost
- Packaging BOM + assembly labor standards
- Scrap rates and rework assumptions

### Channel costs
- Amazon: referral, fulfillment, inbound, PPC (TACOS target)
- DTC: payment processing, shipping, returns

### Marketing
- CAC assumptions by channel

## Outputs
- Gross margin % by channel
- Break-even CAC
- Contribution margin per unit
- Sensitivity table (price vs COGS vs ad spend)
