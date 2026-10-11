# SteadyStud — Manufacturing plan (premium / pro-speed) v0.3

## Your constraint
- v1 design is preferred, but we must avoid an unnecessarily expensive process if the geometry forces full CNC.

## Decision: is full CNC actually required?
We’ll decide this by extracting from STEP v1:
- Are there 3D pockets/cavities that require milling (depth features), or is the part mostly a 2D profile + simple edge finishing?

### If the geometry is mostly 2D (best case for cost)
**Process candidates (cheaper than full CNC):**
1) **Waterjet or laser cut** from aluminum plate
2) Deburr + tumble
3) Add magnets (adhesive)
4) **Laser mark** logo

This supports a pro-speed SKU with good feel at lower cost.

### If the geometry has real 3D pockets (likely)
**Hybrid approach:**
- 2D cut blank (laser/waterjet)
- CNC secondary op only where needed (pockets/notch precision)

### If the geometry is fully 3D (worst case for cost)
- Full CNC billet machining + finishing
- This can still work for premium pricing, but we must ensure margin survives Amazon fees/fulfillment.

## Magnets + retention
For a pro tool, avoid magnets coming loose:
- Prefer **captured pocket** + epoxy, or press-fit if tolerance holds.

## Finish
- Deburr + edge radius for wall-safety
- Optional anodize (black/orange) for durability + brand

## Prototype plan
1) Prototype A: 3D print with test magnets (validate behavior + notch usability)
2) Prototype B: laser-cut aluminum blank + simple finishing
3) If needed: Prototype C: hybrid CNC pocket

## Outputs we will produce
- Cost model at 100 / 1k / 10k units per process route
- A “production-intent drawing” with critical dimensions and tolerances
