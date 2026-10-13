"""Photo-style renders of SteadyStud v3 (run after steadystud_v3.py)."""
import os
import numpy as np
import pyvista as pv
import cadquery as cq
import steadystud_v3 as P

pv.OFF_SCREEN = True
OUT = P.OUT
BODY = "#26272b"      # black anodize
MAGNET = "#9ea2aa"    # Ni-Cu-Ni
MARKC = "#d8dbe0"     # laser mark on black anodize
PADC = "#5b5f66"      # grey felt


def mesh(shape, tol=0.002):
    vs, tris = shape.val().tessellate(tol, 0.1)
    pts = np.array([(v.x, v.y, v.z) for v in vs])
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces).compute_normals(split_vertices=True,
                                                    feature_angle=30)


def marks():
    z = P.THK + 0.0008
    parts = []
    for x0, y0, x1, y1 in P.ticks():
        parts.append(pv.Box(bounds=(x0 - 0.007, x0 + 0.007, y0, y1, z - 0.0005, z)))
    lx0, ly0, lx1, ly1 = P.LOGO_BOX
    txt = pv.Text3D("STEADYSTUD", depth=0.001)
    b = txt.bounds
    s = (lx1 - lx0) * 0.92 / (b[1] - b[0])
    txt.scale([s, s, 1], inplace=True)
    b = txt.bounds
    txt.translate([(lx0 + lx1) / 2 - (b[0] + b[1]) / 2,
                   (ly0 + ly1) / 2 - (b[2] + b[3]) / 2, z - b[4]], inplace=True)
    parts.append(txt)
    return parts


def pad_mesh():
    face = P.profile_solid(0.02).faces("<Z").val()
    inset = face.outerWire().offset2D(-P.PAD_INSET, "arc")[0]
    return mesh(cq.Workplane("XY").add(inset).toPending().extrude(0.02))


def scene(pl, m, explode=0.0, dx=0.0, dy=0.0):
    body, s = P.build_body(m)
    mag = P.build_magnet(m, s)
    off = np.array([dx, dy, 0.0])
    pl.add_mesh(mesh(body).translate(off), color=BODY, smooth_shading=True,
                specular=0.35, specular_power=18, ambient=0.18, diffuse=0.8)
    for m in marks():
        pl.add_mesh(m.translate(off), color=MARKC, ambient=0.6)
    # magnet installs from the back (wall) side, so explode it downward
    for one in mag.vals():                         # each bar separately so seams show
        mm_ = mesh(cq.Workplane().add(one)).translate(off + [0, 0, -explode])
        pl.add_mesh(mm_, color=MAGNET, smooth_shading=True, specular=0.5,
                    specular_power=30, ambient=0.08, diffuse=0.75)
        if explode:
            pl.add_mesh(mm_.extract_feature_edges(30), color="#3a3c40", line_width=1.5)
    pl.add_mesh(pad_mesh().translate(off + [0, 0, -0.022 - 2 * explode]), color=PADC,
                ambient=0.25, specular=0.0)


def shoot(fname, build, cam, size=(1600, 1000)):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("#f4f4f2", top="#ffffff")
    build(pl)
    pl.camera_position = cam
    pl.enable_anti_aliasing("ssaa")
    pl.add_light(pv.Light(position=(-6, -8, 12), focal_point=(2.5, 1, 0),
                          intensity=0.55))
    pl.screenshot(os.path.join(OUT, fname))
    pl.close()


if __name__ == "__main__":
    c = (2.5, 1.0, 0.1)
    hero = [(c[0] - 3.2, c[1] - 5.4, 4.6), c, (0, 0, 1)]
    for v, ml in P.VARIANTS.items():
        shoot(f"SteadyStud_v3{v}_render.png", lambda pl, ml=ml: scene(pl, ml), hero)
    for v in ("B", "C"):
        shoot(f"SteadyStud_v3{v}_exploded.png",
              lambda pl, v=v: scene(pl, P.VARIANTS[v], explode=0.75),
              [(c[0] - 4.0, c[1] - 7.6, 1.2), (2.5, 1.0, -0.7), (0, 0, 1)])
    print("done")
