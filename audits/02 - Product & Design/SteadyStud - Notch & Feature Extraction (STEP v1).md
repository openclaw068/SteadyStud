# SteadyStud — Notch & feature extraction (STEP v1) (draft)

## Source
- `00 - Intake & Notes/Magnetic Stud Finer v1.step`
- Units: inches

## Global solid extents (shell-derived)
When restricting to faces in the solid’s CLOSED_SHELL, the model’s solid extents resolve to:
- X: 0.0 → 5.0
- Y: 0.0 → 2.0
- Z: 0.0 → 0.25

This differs from the raw point-set extents (which included Y down to -0.35 and Z up to 0.35). Conclusion: the STEP file includes some auxiliary geometry/points not part of the main solid body; for manufacturing we should use the **solid shell extents**.

Source: `MANIFOLD_SOLID_BREP('Body2',#2399)` with `CLOSED_SHELL` faces; face-point traversal.

## Primary slab thickness
- Solid bottom: Z=0.0
- Solid top: Z=0.25
→ nominal body thickness: **0.25"**

## Recess / relief strip features (not magnets)
There are 19 down-facing planar faces at Z=0.20. Extracted boundaries show each is a narrow rectangle:
- width in X: **0.025"**
- length in Y: varies per strip (0.25 / 0.35 / 0.5)
- depth: 0.25 - 0.20 = **0.05"**

These are far too small to be magnet pockets. They appear to be relief/texture/slot geometry.

## Candidate marking-notch geometry (inferred from repeated sloped faces)
There are **21 sloped planar faces** with normal approximately (0, -0.707107, 0.707107), i.e. a 45° plane in Y/Z.

Most of these are located in a band:
- Y: 0.0 → 0.05
- Z: 0.20 → 0.25
spanning much of the X range.

Interpretation: a **45° chamfer** (or V-profile) near the Y=0 edge, consistent with a pro tool that slides smoothly and/or guides marking.

We still need to isolate the actual “notch” boundaries (likely the local discontinuity where the edge is open/indented) by identifying loops with missing material (internal boundary loops) rather than external chamfers.

## Next extraction steps
1) Detect internal loops / holes in the shell faces to find actual cutouts (candidate notch and magnet pockets).
2) For each internal loop, compute bounding boxes and approximate dimensions.
3) Summarize: notch width/depth, edge distance, and machinability (2D vs CNC).
