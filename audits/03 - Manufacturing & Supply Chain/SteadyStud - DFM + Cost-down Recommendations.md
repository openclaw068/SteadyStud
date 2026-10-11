# SteadyStud — DFM + Cost-down recommendations (STEP v1, pro-speed) v0.2

## Decisions (confirmed)
- Units: inches
- Overall length: 5.00"
- Premium pro-speed SKU
- Feel: stiff/solid
- Thickness target: 0.25" nominal
- Preferred manufacturing route: **Hybrid** (2D cut + limited CNC)

## CAD-derived extraction (no-render, STEP topology signals)
Source file: `00 - Intake & Notes/Magnetic Stud Finer v1.step`

### 1) Primary slab thickness appears to be 0.25"
Evidence:
- There is an **up-facing plane** at **Z = 0.25** (top surface)
- There is an **up-facing plane** at **Z = 0.0** (bottom surface)

Interpretation: a main body thickness of **0.25"** (good for stiffness and matches our target).

### 2) There are repeated shallow recessed **strips** at Z = 0.20 (depth ≈ 0.05")
We see **19 down-facing planar faces** at **Z = 0.20**.

When I traverse the STEP topology for these faces, each one resolves to a **very narrow rectangle** (example face 2282):
- x: 0.2375 → 0.2625 (**width 0.025"**)
- y: 0.0 → 0.25 (varies across faces)
- z: 0.2 (constant)

So these are not “pocket floors for magnets” (0.025" is far too small for any practical magnet seat). They are more consistent with a series of shallow relief grooves / slot features.

Depth inference (still valid): if the main slab top is Z=0.25, then these Z=0.20 faces correspond to a **0.05" recess depth**.

What remains unknown (pending more STEP parsing): how these strips connect to surrounding faces (i.e., whether they form part of a notch, a texture/anti-slip feature, or a retention pattern).

## Manufacturing route recommendation (Hybrid, optimized)
### Base blank (cheap)
- Start from **0.25" aluminum plate**.
- **Waterjet or laser** the outer profile.

### Limited CNC ops (fast)
Because the recess depth is shallow (~0.05"), you can keep CNC time low:
- Face/spotface these recesses in one setup with a single tool + depth.
- Machine the marking-notch feature if it is not achievable in the 2D cut.

### Finishing
- Aggressive deburr + tumble
- Edge radius (paint-safe) — critical for “pro-speed” slide along wall
- Laser mark logo

## Cost-down changes that preserve stiffness
1) Keep the body at **0.25"** across most of the part.
2) Keep recesses shallow (≈0.05") and standardized to one depth.
3) Avoid large deep pockets (introduce flex + add CNC time).
4) If any raised ridge goes above the slab (Z>0.25 up to 0.35), remove it unless functionally required.

## Open items (still pending from pure STEP parsing)
- Exact **notch geometry** (width/depth and whether it is 2D-cuttable)
- Exact **magnet cavity geometry** (we have strong evidence of repeated recess floors; next step is to identify their boundary loops to recover diameters/rect dims)

## Next extraction step (continuing pure STEP)
- Identify boundary loops for the Z=0.20 floor planes to derive each recess shape and size (diameter/width).
