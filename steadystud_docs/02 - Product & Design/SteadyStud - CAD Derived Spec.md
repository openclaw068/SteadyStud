# SteadyStud — CAD-derived spec (STEP v1) (draft v0.2)

## Source of truth
- File: `00 - Intake & Notes/Magnetic Stud Finer v1.step`
- Units: inches (confirmed)

## IMPORTANT: solid shell vs raw point extents
The STEP file contains some points that are not part of the main solid body.

- **Solid shell extents** (from `MANIFOLD_SOLID_BREP('Body2',#2399)` faces):
  - X: 0.0 → 5.0
  - Y: 0.0 → 2.0
  - Z: 0.0 → 0.25

- **Raw point extents** (all CARTESIAN_POINT in file) show larger ranges (Y down to -0.35 and Z up to 0.35). These appear to be auxiliary/reference geometry.

For manufacturing/DFM we will use the **solid shell extents**.

## Overall envelope (solid shell)
- **Length:** 5.00"
- **Height:** 2.00"
- **Thickness (nominal):** 0.25"

## Edge/feature pattern on the top face (evidence of repeated slots)
Top face (ADVANCED_FACE id 2384, Z=0.25) has boundary vertices along the min-Y edge (y=0.05) at repeated x positions:
- x positions include pairs like: (0.2375, 0.2625), (0.4875, 0.5125), … up to (4.7375, 4.7625)

These pairs correspond to the **0.025" wide** recessed strips previously extracted at Z=0.20.

Interpretation: the model likely includes a repeating slot/relief/texture pattern along one long edge.

## Working manufacturing stance
- Hybrid approach remains recommended (2D cut from 0.25" plate + limited CNC where required).
- Next step is to determine if there is an actual *marking notch cutout* (a void) vs just chamfers/slots.

## Next extraction steps
1) Identify if any true cutouts exist (internal boundary loops or through-features). (So far: none detected as multi-bound faces.)
2) If no cutouts: the “notch” may be represented as an edge contour formed by multiple faces rather than a hole; we’ll extract it by locating the local edge discontinuity on the perimeter.
