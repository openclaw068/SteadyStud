"""SteadyStud v3 — 2D-cut aluminum body with a long bar-magnet through-slot.

Parametric model. Run:  python3 steadystud_v3.py
Outputs (per variant) into ./out/:
  SteadyStud_v3<variant>_body.step       body only (what a shop quotes), units INCH
  SteadyStud_v3<variant>_assembly.step   body + magnet, for fit check
  SteadyStud_v3<variant>_body_mm.stl     true-size mesh in mm (STL has no units)
  SteadyStud_v3<variant>_laser.dxf       layer CUT = through-cut profile,
                                         layer MARK = laser-mark ruler ticks,
                                         layer LOGO_ZONE = logo placement box
  SteadyStud_v3_back_pad.dxf             die-cut back pad outline (shared)

Units: inches. Origin: lower-left of the body, notch on the x=0 end,
ruler along the y=0 edge, front (marked) face at z=THK, back (wall) face at z=0.

Carried over unchanged from v1 STEP: 5.000 x 2.000 x 0.250 envelope, the
end notch (0.433 wide mouth, 0.125 straight, 60 deg V to 0.250 deep, centered
on y=1.000), ruler tick positions and lengths.
Changed from v1: no chamfers (tumble deburr instead), 45-deg corner chamfers
-> R0.125 corner radii, ruler engraved grooves -> laser mark, added magnet
through-slot on the centerline, logo zone moved above the slot.
"""
import os
import cadquery as cq
import ezdxf

# ---------------- parameters ----------------
L, W, THK = 5.000, 2.000, 0.250
CORNER_R = 0.125

# notch (from v1 STEP, unchanged)
NOTCH_HALF_MOUTH = 0.2165          # mouth y = 1.0 +/- 0.2165  -> 0.433 wide
NOTCH_STRAIGHT = 0.125             # straight-walled entry depth
NOTCH_APEX_X = 0.250               # V apex depth from end
CL_Y = W / 2                       # centerline (notch + magnet)

# magnet slot
MAG_W, MAG_T = 0.500, 0.250        # magnet cross-section (width, thickness)
CLEAR = 0.010                      # per side, for epoxy + laser/magnet tolerance
RELIEF_D = 0.125                   # dog-bone relief at slot corners (~50% of thk; shop may reduce to its min hole)

VARIANTS = {
    # name: magnet length.  "A" = K&J BZ084 stock (3 x 1/2 x 1/4, N42).
    #                        "B" = 4 x 1/2 x 1/4 custom bar (no US stock found).
    "A": 3.000,
    "B": 4.000,
}

# ruler (laser mark), same positions/lengths as v1 grooves
TICK_STEP = 0.25
TICK_LEN = {"quarter": 0.25, "half": 0.35, "inch": 0.50}
TICK_EDGE_INSET = 0.030            # start a hair in from the edge (edge break)

# logo zone (moved: v1 box overlapped the new magnet slot)
LOGO_BOX = (1.500, 1.400, 3.500, 1.800)   # x0, y0, x1, y1

# back pad (die-cut PET felt / UHMW tape, adhesive-backed)
PAD_INSET = 0.020

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def slot_geometry(mag_len):
    """Slot centered between notch apex and far end, on the centerline."""
    slot_len = mag_len + 2 * CLEAR
    slot_w = MAG_W + 2 * CLEAR
    avail = L - NOTCH_APEX_X
    gap = (avail - slot_len) / 2
    x0 = NOTCH_APEX_X + gap
    return dict(x0=x0, x1=x0 + slot_len, y0=CL_Y - slot_w / 2,
                y1=CL_Y + slot_w / 2, len=slot_len, w=slot_w, web=gap)


def outline_pts():
    y_lo, y_hi = CL_Y - NOTCH_HALF_MOUTH, CL_Y + NOTCH_HALF_MOUTH
    return [(0, 0), (L, 0), (L, W), (0, W),
            (0, y_hi), (NOTCH_STRAIGHT, y_hi), (NOTCH_APEX_X, CL_Y),
            (NOTCH_STRAIGHT, y_lo), (0, y_lo)]


def outer_corner_selector(edge):
    c = edge.Center()
    return (abs(c.x) < 1e-6 or abs(c.x - L) < 1e-6) and \
           (abs(c.y) < 1e-6 or abs(c.y - W) < 1e-6)


def profile_solid(thk):
    body = cq.Workplane("XY").polyline(outline_pts()).close().extrude(thk)
    corners = [e for e in body.edges("|Z").vals() if outer_corner_selector(e)]
    assert len(corners) == 4, len(corners)
    return body.newObject(corners).fillet(CORNER_R)


def build_body(mag_len):
    s = slot_geometry(mag_len)
    body = profile_solid(THK)
    slot = (cq.Workplane("XY").center((s["x0"] + s["x1"]) / 2, CL_Y)
            .rect(s["len"], s["w"]).extrude(THK))
    reliefs = (cq.Workplane("XY")
               .pushPoints([(s["x0"], s["y0"]), (s["x1"], s["y0"]),
                            (s["x0"], s["y1"]), (s["x1"], s["y1"])])
               .circle(RELIEF_D / 2).extrude(THK))
    return body.cut(slot).cut(reliefs), s


def build_magnet(mag_len, s):
    cx = (s["x0"] + s["x1"]) / 2
    return (cq.Workplane("XY").center(cx, CL_Y)
            .rect(mag_len, MAG_W).extrude(MAG_T))   # flush to back face z=0


def ticks():
    out = []
    n = int(round(L / TICK_STEP))
    for i in range(1, n):
        x = i * TICK_STEP
        if i % 4 == 0:
            ln = TICK_LEN["inch"]
        elif i % 2 == 0:
            ln = TICK_LEN["half"]
        else:
            ln = TICK_LEN["quarter"]
        out.append((x, TICK_EDGE_INSET, x, ln))
    return out


def flatten(msp):
    """Section export carries the cut height as Z; laser CAM wants Z=0."""
    for e in msp:
        t = e.dxftype()
        if t == "LINE":
            e.dxf.start = (e.dxf.start.x, e.dxf.start.y, 0)
            e.dxf.end = (e.dxf.end.x, e.dxf.end.y, 0)
        elif t in ("ARC", "CIRCLE"):
            c = e.dxf.center
            e.dxf.center = (c.x, c.y, 0)
        elif t == "LWPOLYLINE":
            e.dxf.elevation = 0


def export_dxf(body, path):
    tmp = path + ".tmp.dxf"
    cq.exporters.export(body.section(THK / 2), tmp, exportType="DXF")
    doc = ezdxf.readfile(tmp)
    os.remove(tmp)
    doc.header["$INSUNITS"] = 1  # inches (v1 DXF had this flag wrong)
    msp = doc.modelspace()
    flatten(msp)
    for name, color in (("CUT", 1), ("MARK", 5), ("LOGO_ZONE", 3)):
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    for e in msp:
        e.dxf.layer = "CUT"
    for x0, y0, x1, y1 in ticks():
        msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": "MARK"})
    lx0, ly0, lx1, ly1 = LOGO_BOX
    msp.add_lwpolyline([(lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)],
                       close=True, dxfattribs={"layer": "LOGO_ZONE"})
    doc.saveas(path)


def export_pad(path):
    face = profile_solid(0.02).faces("<Z").val()
    inset = face.outerWire().offset2D(-PAD_INSET, "arc")[0]
    pad = cq.Workplane("XY").add(inset).toPending().extrude(0.02)
    tmp = path + ".tmp.dxf"
    cq.exporters.export(pad.section(0.01), tmp, exportType="DXF")
    doc = ezdxf.readfile(tmp)
    os.remove(tmp)
    doc.header["$INSUNITS"] = 1
    if "PAD_CUT" not in doc.layers:
        doc.layers.add("PAD_CUT", color=4)
    flatten(doc.modelspace())
    for e in doc.modelspace():
        e.dxf.layer = "PAD_CUT"
    doc.saveas(path)


def export_step_inch(shapes, path):
    """Write STEP with the file's length unit declared as INCH.

    Model numbers are inches. OCCT works internally in mm, so scale by 25.4
    and tell the writer to emit inches: the file then reads 5.0 x 2.0 x 0.25
    INCH, which every CAD/CAM tool imports at true size.
    """
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.Interface import Interface_Static
    from OCP.IFSelect import IFSelect_RetDone
    w = STEPControl_Writer()          # create first: loading the STEP module resets statics
    Interface_Static.SetCVal_s("xstep.cascade.unit", "MM")
    Interface_Static.SetCVal_s("write.step.unit", "INCH")
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS")
    for sh in shapes:
        w.Transfer(sh.val().scale(25.4).wrapped, STEPControl_AsIs)
    assert w.Write(path) == IFSelect_RetDone, path


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {}
    for name, mag_len in VARIANTS.items():
        body, s = build_body(mag_len)
        mag = build_magnet(mag_len, s)
        base = os.path.join(OUT, f"SteadyStud_v3{name}")
        export_step_inch([body], base + "_body.step")
        export_step_inch([body, mag], base + "_assembly.step")
        # STL has no units; slicers/print services read it as mm, so write true-size mm
        cq.exporters.export(cq.Workplane().add(body.val().scale(25.4)),
                            base + "_body_mm.stl", tolerance=0.02, angularTolerance=0.2)
        export_dxf(body, base + "_laser.dxf")
        vol = body.val().Volume()
        report[name] = dict(mag_len=mag_len, slot=s, volume_in3=vol,
                            mass_g=vol * 16.387 * 2.70,
                            valid=body.val().isValid())
    export_pad(os.path.join(OUT, "SteadyStud_v3_back_pad.dxf"))
    return report


if __name__ == "__main__":
    import json
    print(json.dumps(main(), indent=2, default=float))
