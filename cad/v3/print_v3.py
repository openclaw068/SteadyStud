"""3D-print versions of SteadyStud v3 with the ruler and logo ENGRAVED.

The production part gets its ruler/logo by laser marking, which a print can't do,
so these models cut them into the front face instead:
  SteadyStud_v3<V>_PRINT_mm.stl   true-size mm mesh for slicers / print services
  SteadyStud_v3<V>_PRINT.step     same model, STEP in INCH

Model units are inches (like steadystud_v3.py). Run after steadystud_v3.py.
"""
import os
import cadquery as cq
import steadystud_v3 as P

ENGRAVE = 0.020          # engrave depth, in (~0.5 mm): visible, doesn't weaken the plate
TICK_W = 0.025           # printed tick width, in (~0.64 mm) — >= one 0.4 mm FDM line
TEXT = "STEADYSTUD"
TEXT_H = 0.29            # nominal font size, in; auto-shrinks to fit the 2.0 in logo zone


def print_body(mag_len):
    body, s = P.build_body(mag_len)
    top = P.THK
    # ruler ticks
    for x0, y0, x1, y1 in P.ticks():
        tick = (cq.Workplane("XY", origin=(0, 0, top - ENGRAVE))
                .center(x0, (y0 + y1) / 2).rect(TICK_W, y1 - y0).extrude(ENGRAVE))
        body = body.cut(tick)
    # logo text, centered in the logo zone, cut into the top face
    lx0, ly0, lx1, ly1 = P.LOGO_BOX
    txt = (cq.Workplane("XY", origin=((lx0 + lx1) / 2, (ly0 + ly1) / 2, top))
           .text(TEXT, TEXT_H, -ENGRAVE, kind="bold", halign="center", valign="center",
                 combine=False))
    tb = txt.val().BoundingBox()
    max_w = (lx1 - lx0) * 0.95
    if tb.xlen > max_w:                      # shrink to fit the zone if needed
        k = max_w / tb.xlen
        txt = (cq.Workplane("XY", origin=((lx0 + lx1) / 2, (ly0 + ly1) / 2, top))
               .text(TEXT, TEXT_H * k, -ENGRAVE, kind="bold", halign="center",
                     valign="center", combine=False))
    body = body.cut(txt)
    return body, txt.val().BoundingBox()


def main():
    out = {}
    for v, ml in P.VARIANTS.items():
        body, tb = print_body(ml)
        base = os.path.join(P.OUT, f"SteadyStud_v3{v}_PRINT")
        cq.exporters.export(cq.Workplane().add(body.val().scale(25.4)),
                            base + "_mm.stl", tolerance=0.01, angularTolerance=0.15)
        P.export_step_inch([body], base + ".step")
        out[v] = dict(valid=body.val().isValid(), vol=body.val().Volume(),
                      text_w=tb.xlen, text_h=tb.ylen)
    return out


if __name__ == "__main__":
    for k, r in main().items():
        print(k, r)
