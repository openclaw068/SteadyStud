# SteadyStud — Intake (updated)

## Scale / units (confirmed)
- **Target physical length:** **5.0 inches** (confirmed by you).

## What you provided (intake folder)
- CAD: STEP/DWG/DXF/IPT/F3D/FBX (v1 + v2)
- Media: MOV + MP4
- Receipt: PDF (image-based scan; needs OCR)

## CAD unit reconciliation (no guessing)
### STEP v1 (`Magnetic Stud Finer v1.step`)
- Extracted bounding extents from STEP point set:
  - X: 0.0 → 5.0
  - Y: -0.35 → 2.35
  - Z: 0.0 → 0.3500000039
- This matches a **5-inch** overall length when interpreted as inches.

Source: `Magnetic Stud Finer v1.step` (CARTESIAN_POINT extents)

### DXF v1 (`Magnetic Stud Finer v1.DXF`)
- DXF header reports `INSUNITS = 1` (inches), but entity extents are:
  - X: 0.0 → 12.7
  - Y: 0.0 → 5.08
- **12.7 and 5.08 are exactly 5.0" and 2.0" expressed in centimeters.**

Conclusion: DXF appears to be **inch design exported/scaled in cm-like numeric units** (despite INSUNITS flag). We will use STEP v1 as the authoritative inch-scale reference.

Source: `Magnetic Stud Finer v1.DXF` header + LINE entity endpoints; and your confirmation that the product should be 5 inches long.

### FBX v2 (`Magnetic Stud Finer v2.fbx`)
- FBX contains `UnitScaleFactor = 2.54` and `OriginalUnitScaleFactor = 1.0`, consistent with inch↔cm conversion in export.

Source: `Magnetic Stud Finer v2.fbx` (UnitScaleFactor fields).

## Manufacturing reality (premium / pro-speed)
- v1 geometry may be manufacturable without full CNC depending on how pockets/features are designed.
- We’ll evaluate two production routes:
  1) **Aluminum (premium):** CNC OR 2.5D processes (laser/waterjet + secondary ops) depending on 3D features.
  2) **Polymer (lower cost):** injection molding later; for now 3D print for iteration.

## Next actions
1) Finish feature-level extraction from STEP v1 (notch geometry, any pockets/cavities, thickness zones).
2) Produce a DFM recommendation: "CNC required" vs "laser-cut feasible" vs "hybrid".
3) Update channel + pricing strategy for **pro-speed** positioning.
