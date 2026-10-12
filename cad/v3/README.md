# SteadyStud v3 — 2D-cut aluminum body, long bar magnet

Cost-down redesign of `audits/Magnetic Stud Finer v1.step`. Every feature is a
through-cut profile, so the body is laser- or waterjet-cut from 1/4" plate with
no milling.

**All design files are in INCHES** (STEP declares INCH; DXFs have `$INSUNITS = 1`).
The only exception is the STL, which has no unit field and is written true-size
in mm because slicers and print services assume mm.

Regenerate everything:

    ./build_all.sh        # needs: cadquery, ezdxf, matplotlib, pyvista

| Variant | Magnet | Source | Slot |
|---|---|---|---|
| v3A | 3 × ½ × ¼ in N42 bar (60% of length) | K&J Magnetics BZ084, stock | 3.020 × 0.520 |
| v3B | 4 × ½ × ¼ in bar (80% of length) | custom order (no US stock found) | 4.020 × 0.520 |

Kept from v1: 5.000 × 2.000 × 0.250 envelope, end V-notch (unchanged), ruler tick layout.
Changed: chamfers removed (tumble deburr), 45° corners → R0.125, engraved ruler →
laser mark, magnet through-slot on the notch centerline, logo zone moved above the
slot, adhesive back pad covers the magnet and is the wall-contact face.

## What to send a shop (`out/`)

| Job | File |
|---|---|
| Laser/waterjet/sheet-metal quote | `SteadyStud_v3A_body.step` (or `_CUT_ONLY_inch.dxf`) |
| Laser marking artwork | `SteadyStud_v3A_laser_marking_inch.dxf` + `_laser_marking_drawing.pdf` |
| Full drawing for review | `SteadyStud_v3A_drawing.pdf` |
| Back pad die-cut | `SteadyStud_v3_back_pad.dxf` |
| 3D print (ruler + logo engraved 0.020 deep) | `SteadyStud_v3A_PRINT_mm.stl` / `SteadyStud_v3B_PRINT_mm.stl` |

Other outputs: `_assembly.step` (body + magnet), `_laser.dxf` (CUT / MARK /
LOGO_ZONE layers together), `_body_mm.stl` (plain body, no marks), `_PRINT.step`
(engraved print model, inch), renders (`.png`).

## Scripts

- `steadystud_v3.py` — parametric model; STEP, combined laser DXF, STL, back pad
- `draw_v3.py` — dimensioned drawing PDFs
- `shop_files_v3.py` — cut-only DXF, marking DXF, marking drawing (inch)
- `print_v3.py` — 3D-print models with ruler and logo engraved
- `render_v3.py` — product renders
