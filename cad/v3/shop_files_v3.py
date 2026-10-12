"""Shop-ready files for SteadyStud v3, all in INCHES (run after steadystud_v3.py).

  SteadyStud_v3<V>_CUT_ONLY_inch.dxf        through-cut outline only (no marks)
  SteadyStud_v3<V>_laser_marking_inch.dxf   OUTLINE_REF (reference) + MARK layer:
                                            ruler ticks + "STEADYSTUD" as closed outlines
  SteadyStud_v3<V>_laser_marking_drawing.pdf  1:1 marking drawing, inch dimensions
"""
import os
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import steadystud_v3 as P

OUT = P.OUT
TICK_W = 0.014            # marked line width, inches
TEXT = "STEADYSTUD"


def cut_only(v):
    d = ezdxf.readfile(os.path.join(OUT, f"SteadyStud_v3{v}_laser.dxf"))
    msp = d.modelspace()
    for e in [e for e in msp if e.dxf.layer != "CUT"]:
        msp.delete_entity(e)
    d.header["$INSUNITS"] = 1
    d.header["$MEASUREMENT"] = 0
    d.saveas(os.path.join(OUT, f"SteadyStud_v3{v}_CUT_ONLY_inch.dxf"))


def marking(v):
    src = ezdxf.readfile(os.path.join(OUT, f"SteadyStud_v3{v}_laser.dxf"))
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1
    doc.header["$MEASUREMENT"] = 0
    doc.layers.add("OUTLINE_REF", color=8)
    doc.layers.add("MARK", color=7)
    msp = doc.modelspace()
    for e in src.modelspace():
        if e.dxf.layer == "CUT":
            c = e.copy()
            c.dxf.layer = "OUTLINE_REF"
            msp.add_entity(c)
    w = TICK_W / 2
    for x0, y0, x1, y1 in P.ticks():
        msp.add_lwpolyline([(x0 - w, y0), (x0 + w, y0), (x0 + w, y1), (x0 - w, y1)],
                           close=True, dxfattribs={"layer": "MARK"})
    lx0, ly0, lx1, ly1 = P.LOGO_BOX
    polys = TextPath((0, 0), TEXT, size=10,
                     prop=FontProperties(family="DejaVu Sans", weight="bold")).to_polygons()
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    tw, th = max(xs) - min(xs), max(ys) - min(ys)
    s = min((lx1 - lx0) * 0.9 / tw, (ly1 - ly0) * 0.8 / th)
    cx, cy = (lx0 + lx1) / 2, (ly0 + ly1) / 2
    for poly in polys:
        msp.add_lwpolyline([(cx + (x - min(xs) - tw / 2) * s, cy + (y - min(ys) - th / 2) * s)
                            for x, y in poly], close=True, dxfattribs={"layer": "MARK"})
    path = os.path.join(OUT, f"SteadyStud_v3{v}_laser_marking_inch.dxf")
    doc.saveas(path)
    return path, tw * s, th * s


def marking_drawing(v, dxf_path, tw, th):
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ox, oy = 3.0, 3.4
    for e in ezdxf.readfile(dxf_path).modelspace():
        t = e.dxftype()
        if e.dxf.layer == "OUTLINE_REF":
            if t == "LINE":
                a, b = e.dxf.start, e.dxf.end
                ax.plot([ox + a.x, ox + b.x], [oy + a.y, oy + b.y], color="#999", lw=0.8)
            elif t == "ARC":
                c = e.dxf.center
                ax.add_patch(Arc((ox + c.x, oy + c.y), 2 * e.dxf.radius, 2 * e.dxf.radius,
                                 theta1=e.dxf.start_angle, theta2=e.dxf.end_angle,
                                 color="#999", lw=0.8))
        elif t == "LWPOLYLINE":
            pts = [(ox + x, oy + y) for x, y, *_ in e.get_points()]
            pts.append(pts[0])
            ax.plot(*zip(*pts), color="black", lw=0.9)
    lx0, ly0, lx1, ly1 = P.LOGO_BOX
    ax.text(0.6, 7.9, f"STEADYSTUD v3{v} — LASER MARKING DRAWING (INCHES)",
            fontsize=15, weight="bold")
    ax.text(0.6, 7.6, "Grey = cut outline (reference only). BLACK = laser mark on the "
            "FRONT face. All dimensions in inches.", fontsize=10)
    notes = [
        "MARK 1 — RULER: 19 lines along the bottom long edge, 0.250 pitch, first line "
        "0.250 from the notched end.",
        "   Line lengths: 0.250 at quarter-inch, 0.350 at half-inch, 0.500 at whole-inch "
        f"positions. Line width ≈ {TICK_W:.3f}.",
        f"   Lines start {P.TICK_EDGE_INSET:.3f} in from the edge. Positions measured from "
        "the notched end of the part.",
        f"MARK 2 — TEXT: \"{TEXT}\", about {tw:.2f} × {th:.2f}, centered in a "
        f"{lx1 - lx0:.3f} × {ly1 - ly0:.3f} zone; zone center {(lx0 + lx1) / 2:.3f} from "
        f"the notched end, {(ly0 + ly1) / 2:.3f} from the ruler edge.",
        "FACE: front face only (notch on the LEFT, ruler along the BOTTOM edge). "
        "Do not mark the back.",
        "Marks only — NOT cut or engraved through. Fill all closed BLACK shapes. "
        "1:1 when printed at 100% on letter paper.",
        f"Matching file: {os.path.basename(dxf_path)} (units: inch).",
    ]
    y = 2.6
    for n in notes:
        ax.text(0.6, y, n, fontsize=9.5)
        y -= 0.3
    fig.savefig(os.path.join(OUT, f"SteadyStud_v3{v}_laser_marking_drawing.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    for v in P.VARIANTS:
        cut_only(v)
        path, tw, th = marking(v)
        marking_drawing(v, path, tw, th)
        print(v, "ok")
