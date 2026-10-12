"""Dimensioned PDF drawing for each SteadyStud v3 variant.

Geometry is read back from the exported laser DXF (so the drawing shows
exactly what a shop will cut) plus the parameters in steadystud_v3.py.
Run after steadystud_v3.py:  python3 draw_v3.py
"""
import math
import os

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, Polygon

import steadystud_v3 as P

OUT = P.OUT
INK = "#111111"
MARK = "#1f5fbf"
LOGO = "#2a8f3a"
DIM = "#444444"
HID = "#888888"
MAG = "#b9bcc4"


def draw_dxf(ax, path, ox=0, oy=0, s=1.0, layers=None, lw=1.2):
    doc = ezdxf.readfile(path)
    for e in doc.modelspace():
        lay = e.dxf.layer
        if layers and lay not in layers:
            continue
        col = {"CUT": INK, "PAD_CUT": INK, "MARK": MARK, "LOGO_ZONE": LOGO}.get(lay, INK)
        ls = "--" if lay == "LOGO_ZONE" else "-"
        w = 0.8 if lay != "CUT" else lw
        t = e.dxftype()
        if t == "LINE":
            a, b = e.dxf.start, e.dxf.end
            ax.plot([ox + s * a.x, ox + s * b.x], [oy + s * a.y, oy + s * b.y],
                    color=col, lw=w, ls=ls, solid_capstyle="butt")
        elif t == "ARC":
            c = e.dxf.center
            ax.add_patch(Arc((ox + s * c.x, oy + s * c.y), 2 * s * e.dxf.radius,
                             2 * s * e.dxf.radius, theta1=e.dxf.start_angle,
                             theta2=e.dxf.end_angle, color=col, lw=w))
        elif t == "LWPOLYLINE":
            pts = [(ox + s * x, oy + s * y) for x, y, *_ in e.get_points()]
            pts.append(pts[0])
            ax.plot(*zip(*pts), color=col, lw=w, ls=ls)


def hdim(ax, x0, x1, y, text, ext_from=None, fs=7.5, above=True):
    ax.annotate("", (x0, y), (x1, y),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7,
                                shrinkA=0, shrinkB=0))
    if ext_from is not None:
        for x in (x0, x1):
            ax.plot([x, x], [ext_from, y + (0.04 if y > ext_from else -0.04)],
                    color=DIM, lw=0.4)
    ax.text((x0 + x1) / 2, y + (0.035 if above else -0.035), text, ha="center",
            va="bottom" if above else "top", fontsize=fs, color=DIM)


def vdim(ax, y0, y1, x, text, ext_from=None, fs=7.5, left=True):
    ax.annotate("", (x, y0), (x, y1),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=0.7,
                                shrinkA=0, shrinkB=0))
    if ext_from is not None:
        for y in (y0, y1):
            ax.plot([ext_from, x + (-0.04 if x < ext_from else 0.04)], [y, y],
                    color=DIM, lw=0.4)
    ax.text(x + (-0.04 if left else 0.04), (y0 + y1) / 2, text,
            ha="right" if left else "left", va="center", fontsize=fs,
            color=DIM, rotation=90 if not left else 90)


def leader(ax, xy, xytext, text, fs=7):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=DIM,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=DIM, lw=0.5))


def sheet(variant, mag_len):
    s = P.slot_geometry(mag_len)
    fig = plt.figure(figsize=(11, 8.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # border + title
    ax.add_patch(Rectangle((0.3, 0.3), 10.4, 7.9, fill=False, lw=1.2, color=INK))
    ax.text(0.5, 7.95, f"STEADYSTUD v3{variant} — 2D-CUT ALUMINUM BODY, "
            f"{mag_len:g}\" BAR MAGNET", fontsize=13, weight="bold", color=INK)
    ax.text(0.5, 7.72, "Laser/waterjet profile from 0.250\" plate. No machining. "
            "Dimensions in inches. Drawing generated from the laser DXF.",
            fontsize=8.5, color=DIM)

    # ---------------- top view (scale 1:1) ----------------
    ox, oy, sc = 1.0, 4.75, 1.0
    draw_dxf(ax, os.path.join(OUT, f"SteadyStud_v3{variant}_laser.dxf"), ox, oy, sc)
    ax.text(ox, oy + 2.55, "FRONT FACE (marked side) — 1:1 when PDF printed at 100%",
            fontsize=8, weight="bold", color=INK)
    # overall
    hdim(ax, ox, ox + 5, oy - 0.55, "5.000", ext_from=oy)
    vdim(ax, oy, oy + 2, ox - 0.45, "2.000", ext_from=ox)
    # slot location + size
    hdim(ax, ox, ox + s["x0"], oy + 2.3, f"{s['x0']:.3f}", ext_from=oy + 2, fs=7)
    hdim(ax, ox + s["x0"], ox + s["x1"], oy + 2.3, f"{s['len']:.3f} SLOT", fs=7)
    vdim(ax, oy + s["y0"], oy + s["y1"], ox + 5.35, f"{s['w']:.3f}",
         ext_from=ox + s["x1"], fs=7, left=False)
    leader(ax, (ox + s["x1"], oy + s["y1"]), (ox + 5.55, oy + 1.75),
           f"4X Ø{P.RELIEF_D:.3f} CORNER RELIEF, CENTERED ON\nSLOT CORNERS (shop may reduce to its min hole)")
    leader(ax, (ox + 2.6, oy + P.CL_Y), (ox + 5.55, oy + 1.05),
           f"SLOT ON CENTERLINE (y = {P.CL_Y:.3f})\nCOMMON WITH NOTCH APEX")
    leader(ax, (ox + 5 - 0.04, oy + 2 - 0.04), (ox + 5.55, oy + 2.35),
           f"4X R{P.CORNER_R:.3f} OUTER CORNERS")
    leader(ax, (ox + 2.0, oy + 0.3), (ox + 5.55, oy + 0.35),
           "RULER: 19 LASER-MARK TICKS @ 0.250 PITCH\n"
           "LENGTHS .25 / .35 (HALF) / .50 (INCH)  — MARK, NOT CUT")
    leader(ax, (ox + P.LOGO_BOX[2], oy + P.LOGO_BOX[3]),
           (ox + 5.55, oy + 2.65 - 0.05),
           "LOGO ZONE 2.00 x 0.40 (laser mark) — moved from v1")

    # ---------------- notch detail (4:1) ----------------
    nx, ny, ns = 1.0, 0.75, 2.5
    # local geometry around notch: x 0..0.45, y 0.55..1.45
    y_lo, y_hi = P.CL_Y - P.NOTCH_HALF_MOUTH, P.CL_Y + P.NOTCH_HALF_MOUTH
    pts = [(0, 0.55), (0, y_lo), (P.NOTCH_STRAIGHT, y_lo), (P.NOTCH_APEX_X, P.CL_Y),
           (P.NOTCH_STRAIGHT, y_hi), (0, y_hi), (0, 1.45)]
    T = lambda x, y: (nx + ns * x, ny + ns * (y - 0.55))
    ax.plot(*zip(*[T(*p) for p in pts]), color=INK, lw=1.4)
    ax.plot(*zip(T(0, 0.55), T(0.5, 0.55)), color=INK, lw=0.6, ls=(0, (6, 3)))
    ax.plot(*zip(T(0, 1.45), T(0.5, 1.45)), color=INK, lw=0.6, ls=(0, (6, 3)))
    ax.plot(*zip(T(-0.05, P.CL_Y), T(0.6, P.CL_Y)), color=HID, lw=0.5,
            ls=(0, (8, 3, 2, 3)))
    ax.text(nx, ny + ns * 0.95 + 0.25, "DETAIL A — END NOTCH (2.5:1)\n"
            "unchanged from v1 STEP", fontsize=8, weight="bold", color=INK)
    x0, y0 = T(0, y_lo); x1, y1 = T(0, y_hi)
    vdim(ax, y0, y1, x0 - 0.25, f"{2 * P.NOTCH_HALF_MOUTH:.3f}", ext_from=x0)
    a0 = T(0, y_hi); a1 = T(P.NOTCH_STRAIGHT, y_hi)
    hdim(ax, a0[0], a1[0], a0[1] + 0.35, f"{P.NOTCH_STRAIGHT:.3f}",
         ext_from=a0[1], fs=7)
    b0 = T(0, P.CL_Y); b1 = T(P.NOTCH_APEX_X, P.CL_Y)
    hdim(ax, b0[0], b1[0], ny - 0.15, f"{P.NOTCH_APEX_X:.3f} TO APEX",
         ext_from=b0[1], fs=7, above=False)
    ax.text(T(0.27, 1.1)[0], T(0.27, 1.1)[1], "60° INCLUDED V", fontsize=7,
            color=DIM)
    ax.text(T(0.62, P.CL_Y)[0], T(0.62, P.CL_Y)[1], "℄", fontsize=9, color=HID,
            va="center")

    # ---------------- edge view / assembly section (2:1) ----------------
    ex, ey, es = 3.1, 3.0, 1.0
    # section through centerline, length direction, scale 1:1 x, 2:1 z for clarity
    zs = 2.0
    ax.text(ex, ey + 0.95, "SECTION B — THROUGH CENTERLINE (thickness shown 2:1)",
            fontsize=8, weight="bold", color=INK)
    # body pieces either side of slot (notch end starts at apex x=0.25 on CL)
    ax.add_patch(Rectangle((ex + P.NOTCH_APEX_X, ey), s["x0"] - P.NOTCH_APEX_X,
                           P.THK * zs, facecolor="#d9d9d9", edgecolor=INK, lw=1,
                           hatch="////"))
    ax.add_patch(Rectangle((ex + s["x1"], ey), 5 - s["x1"], P.THK * zs,
                           facecolor="#d9d9d9", edgecolor=INK, lw=1, hatch="////"))
    mx = ex + (s["x0"] + s["x1"]) / 2 - mag_len / 2
    ax.add_patch(Rectangle((mx, ey), mag_len, P.MAG_T * zs, facecolor=MAG,
                           edgecolor=INK, lw=0.8))
    ax.text(mx + mag_len / 2, ey + P.MAG_T * zs / 2,
            f"MAGNET {mag_len:g} x {P.MAG_W:g} x {P.MAG_T:g}  (N42, magnetized "
            "through thickness)", ha="center", va="center", fontsize=6.5)
    # pad under
    ax.add_patch(Rectangle((ex + 0.02, ey - 0.06), 4.96, 0.04, facecolor="#555555",
                           edgecolor="none"))
    leader(ax, (ex + 4.6, ey - 0.04), (ex + 5.2, ey - 0.3),
           "BACK PAD (wall side) — see note 7")
    vdim(ax, ey, ey + P.THK * zs, ex + 5.25, ".250", ext_from=ex + 5, left=False)
    hdim(ax, ex + s["x0"], ex + s["x1"], ey + P.THK * zs + 0.25,
         f"SLOT {s['len']:.3f} / MAGNET {mag_len:.3f}", ext_from=ey + P.THK * zs,
         fs=7)
    ax.text(ex, ey - 0.45, "Magnet bonded FLUSH TO BACK (wall) face. Any thickness "
            "mismatch is taken on the front face.", fontsize=7, color=DIM)

    # ---------------- notes ----------------
    notes = [
        "1. MATERIAL: 6061-T6 aluminum plate, 0.250\" nominal.",
        "2. PROCESS: through-cut profile only (fiber laser or waterjet). No milling, no chamfers.",
        "3. TOLERANCES: profile ±0.005; slot +0.005/-0.000 vs nominal shown; thickness per mill plate.",
        "4. EDGES: tumble/vibratory deburr. Break all edges .010–.020. No sharp edges (wall-safe).",
        "5. FINISH: Type II anodize, black (alt: clear). Quote as-cut + tumbled as alternate.",
        "6. MARKING: laser mark after anodize — layer MARK (ruler) and LOGO_ZONE. Not engraved.",
        "7. BACK PAD: adhesive-backed PET felt or UHMW tape ≤0.5 mm, die-cut to",
        "   SteadyStud_v3_back_pad.dxf (outline inset 0.020). Covers magnet; wall-contact face.",
        f"8. MAGNET: {mag_len:g} x 1/2 x 1/4 NdFeB N42, Ni-Cu-Ni, magnetized through thickness.",
        ("   Stock ref: K&J Magnetics BZ084. " if mag_len == 3.0 else
         "   Not a US catalog stock size — custom order. ") +
        "Bond with 2-part epoxy; polarity uniform across lot.",
        "9. USE: hold notch UP (long axis vertical). Mark at notch apex = fastener column = stud line.",
    ]
    import textwrap
    nb_x, y = 3.1, 2.3
    ax.text(nb_x, y + 0.08, "NOTES", fontsize=8.5, weight="bold", color=INK)
    y -= 0.08
    for n in notes:
        for j, line in enumerate(textwrap.wrap(n, 96)):
            ax.text(nb_x + (0.12 if j else 0), y, line, fontsize=6.3, color=INK,
                    va="top")
            y -= 0.135

    # title block
    tb = [("PART", f"SteadyStud body v3{variant}"),
          ("MAGNET", f"{mag_len:g}\" bar"),
          ("SOURCE", "cad/v3/steadystud_v3.py"),
          ("SUPERSEDES", "Stud Finer v1 (for quoting)"),
          ("UNITS", "inch"),
          ("DATE", "2026-10-10"),
          ("STATUS", "PROTOTYPE / RFQ — NOT RELEASED")]
    bx, by = 7.75, 0.45
    ax.add_patch(Rectangle((bx - 0.08, by - 0.05), 2.95, 0.2 * len(tb) + 0.08,
                           fill=False, lw=0.8, color=INK))
    for i, (k, v) in enumerate(reversed(tb)):
        ax.text(bx, by + i * 0.2 + 0.05, k, fontsize=6.5, weight="bold", color=INK)
        ax.text(bx + 0.85, by + i * 0.2 + 0.05, v, fontsize=6.5, color=INK)

    path = os.path.join(OUT, f"SteadyStud_v3{variant}_drawing.pdf")
    fig.savefig(path)
    fig.savefig(path.replace(".pdf", ".png"), dpi=110)
    plt.close(fig)
    return path


if __name__ == "__main__":
    for v, m in P.VARIANTS.items():
        print(sheet(v, m))
