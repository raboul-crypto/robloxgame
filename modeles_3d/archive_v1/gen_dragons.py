"""Generateur de dragons chibi pour Dragon Pets Simulator.
7 types x 3 stades (Bebe, Ado, Adulte). Pieces separees nommees, export FBX par modele.
Usage : python3 gen_dragons.py <dossier_sortie>
"""
import bpy, bmesh, math, sys, os, addon_utils
from mathutils import Vector as V, Euler

OUT = os.path.abspath(sys.argv[-1])
os.makedirs(OUT + "/fbx", exist_ok=True)
os.makedirs(OUT + "/render", exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    addon_utils.enable("io_scene_fbx", default_set=True)
except Exception as e:
    print("fbx addon:", e)

# Couleurs de demo (sRGB). En jeu, chaque espece recolore les pieces par leur nom.
PAL = {
    "Classique":  dict(Skin=(0.86, 0.24, 0.18), Belly=(1, 0.84, 0.58), Wing=(1, 0.58, 0.32), Horn=(1, 0.94, 0.8), Spike=(1, 0.62, 0.26)),
    "Wyvern":     dict(Skin=(0.52, 0.34, 0.84), Belly=(0.92, 0.85, 1), Wing=(0.8, 0.64, 1), Horn=(0.98, 0.95, 1), Spike=(0.96, 0.78, 1)),
    "Drake":      dict(Skin=(0.58, 0.42, 0.28), Belly=(0.93, 0.84, 0.64), Wing=(0.5, 0.8, 0.45), Horn=(0.96, 0.92, 0.82), Spike=(0.46, 0.78, 0.42)),
    "Hydre":      dict(Skin=(0.32, 0.72, 0.34), Belly=(0.93, 0.96, 0.62), Wing=(0.6, 0.9, 0.5), Horn=(0.98, 0.95, 0.82), Spike=(0.96, 0.8, 0.3)),
    "Oriental":   dict(Skin=(0.98, 0.76, 0.22), Belly=(1, 0.95, 0.74), Wing=(1, 0.5, 0.3), Horn=(1, 0.97, 0.86), Spike=(0.9, 0.26, 0.22)),
    "Amphiptere": dict(Skin=(0.36, 0.66, 0.96), Belly=(0.95, 0.97, 1), Wing=(0.66, 0.88, 1), Horn=(1, 1, 0.9), Spike=(1, 0.86, 0.42)),
    "Aquatique":  dict(Skin=(0.16, 0.6, 0.66), Belly=(0.76, 0.97, 0.9), Wing=(0.36, 0.88, 0.92), Horn=(0.9, 1, 0.97), Spike=(0.36, 0.88, 0.92)),
}
FIXED = {"Eye": (1, 1, 1), "Pupil": (0.07, 0.06, 0.09)}
MATROLE = {"Claw": "Horn", "Bone": "Skin"}
SUFFIX = {"Skin": "", "Belly": "Belly", "Horn": "Horns", "Claw": "Claws", "Spike": "Spikes",
          "Eye": "Eyes", "Pupil": "Pupils", "Bone": "Bones"}
STAGES = ["Bebe", "Ado", "Adulte"]

CUR = {"typ": None}
P = []      # (obj, groupe, role)
PIV = {}    # groupe -> pivot (articulation)
MATS = {}


def mat(role):
    typ = CUR["typ"]
    role = MATROLE.get(role, role)
    k = (typ, role)
    if k in MATS:
        return MATS[k]
    c = FIXED.get(role) or PAL[typ][role]
    lin = tuple(x ** 2.2 for x in c)
    m = bpy.data.materials.new(f"{typ}_{role}")
    try:
        m.use_nodes = True
    except Exception:
        pass
    m.diffuse_color = (*lin, 1)
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Base Color"].default_value = (*lin, 1)
                n.inputs["Roughness"].default_value = 0.2 if role in ("Eye", "Pupil") else 0.5
    MATS[k] = m
    return m


def sel(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def reg(o, g, r, sm=True):
    if sm:
        smooth(o)
    o.data.materials.append(mat(r))
    P.append((o, g, r))
    return o


def sph(loc, sc, g, r, rot=(0, 0, 0)):
    if isinstance(sc, (int, float)):
        sc = (sc, sc, sc)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1, location=V(loc), rotation=rot, scale=sc)
    return reg(bpy.context.object, g, r)


def cone(a, b, r, g, role, flat=(1, 1, 1)):
    a, b = V(a), V(b)
    d = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=r, radius2=0, depth=d.length, location=a + d / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = V((0, 0, 1)).rotation_difference(d.normalized())
    o.scale = flat
    return reg(o, g, role)


def tube(pts, radii, g, role):
    cu = bpy.data.curves.new("t", "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 6
    cu.bevel_mode = "ROUND"
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 2
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p, r in zip(sp.bezier_points, pts, radii):
        bp.co = V(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r
    o = bpy.data.objects.new("t", cu)
    bpy.context.collection.objects.link(o)
    sel([o])
    bpy.ops.object.convert(target="MESH")
    return reg(bpy.context.view_layer.objects.active, g, role)


def membrane(pts, g, role, thick):
    me = bpy.data.meshes.new("m")
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    c = bm.verts.new(sum(pts, V()) / len(pts))
    for i in range(len(vs)):
        bm.faces.new((c, vs[i], vs[(i + 1) % len(vs)]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("m", me)
    bpy.context.collection.objects.link(o)
    sel([o])
    mod = o.modifiers.new("s", "SOLIDIFY")
    mod.thickness = thick
    mod.offset = 0
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return reg(o, g, role, sm=False)


# ---------- pieces ----------
WING = [(0, -0.12), (0.55, -0.18), (1.05, 0.0), (0.8, 0.25), (0.95, 0.5), (0.65, 0.48), (0.6, 0.8), (0.0, 0.4)]
FIN = [(0, 0), (0.12, 0.5), (0.3, 0.38), (0.45, 0.8), (0.62, 0.55), (0.85, 0.95), (0.95, 0.45), (0.75, 0)]


def wing(root, span, sx, g, up=0.9):
    root = V(root)
    ca, sa = math.cos(up), math.sin(up)
    pts = [root + V((sx * a * ca, b, a * sa)) * span for a, b in WING]
    membrane(pts, g, "Wing", max(0.03, 0.04 * span))
    tube([root, pts[1], pts[2]], [0.05 * span, 0.035 * span, 0.01 * span], g, "Bone")
    tube([pts[1], pts[4]], [0.03 * span, 0.008 * span], g, "Bone")
    tube([pts[1], pts[6]], [0.03 * span, 0.008 * span], g, "Bone")
    sph(pts[1], 0.045 * span, g, "Claw")
    PIV[g] = root


def fin(root, u, v, size, g):
    root, u, v = V(root), V(u).normalized(), V(v).normalized()
    membrane([root + (u * x + v * y) * size for x, y in FIN], g, "Wing", max(0.025, 0.04 * size))


def horn(b, d, hl, r0, g):
    b, d = V(b), V(d).normalized()
    tube([b, b + d * 0.5 * hl + V((0, 0, 0.15 * hl)), b + d * hl], [r0, r0 * 0.55, 0.01], g, "Horn")


def head(hc, hr, t, g="Head", kind="classic"):
    hc = V(hc)
    PIV[g] = hc
    sph(hc, (hr * 1.06, hr, hr * 0.92), g, "Skin")
    sph(hc + V((0, -0.7 * hr, -0.34 * hr)), (0.62 * hr, 0.56 * hr, 0.42 * hr), g, "Skin")
    sph(hc + V((0, -0.72 * hr, -0.52 * hr)), (0.5 * hr, 0.44 * hr, 0.22 * hr), g, "Belly")
    er = hr * (0.42 - 0.12 * t)
    for s in (-1, 1):
        ep = hc + V((s * 0.46 * hr, -0.68 * hr, 0.14 * hr))
        d = (ep - hc).normalized()
        sph(ep, (er * 0.92, er * 0.75, er), g, "Eye")
        pp = ep + d * er * 0.42
        sph(pp, (er * 0.66, er * 0.45, er * 0.76), g, "Pupil")
        sph(pp + d * er * 0.33 + V((-0.22 * er, 0, 0.28 * er)), er * 0.24, g, "Eye")
        sph(hc + V((s * 0.2 * hr, -1.2 * hr, -0.22 * hr)), 0.06 * hr, g, "Pupil")
    hl = hr * (0.32 + 0.7 * t)
    if kind in ("classic", "hydra", "amph", "wyvern", "drake"):
        L = hl * (1.35 if kind == "wyvern" else 1.0)
        for s in (-1, 1):
            horn(hc + V((s * 0.42 * hr, 0.22 * hr, 0.6 * hr)), (s * 0.3, 0.8, 0.55), L, 0.15 * hr, g)
    if kind == "drake":
        for s in (-1, 1):
            horn(hc + V((s * 0.72 * hr, 0.1 * hr, 0.05 * hr)), (s * 0.6, 0.8, 0.1), hl * 0.6, 0.11 * hr, g)
        cone(hc + V((0, -1.0 * hr, 0.0)), hc + V((0, -1.12 * hr, (0.3 + 0.3 * t) * hr)), 0.1 * hr, g, "Horn")
    if kind == "oriental":
        for s in (-1, 1):
            b = hc + V((s * 0.38 * hr, 0.15 * hr, 0.65 * hr))
            m = b + V((s * 0.15 * hl, 0.35 * hl, 0.7 * hl))
            tube([b, m, m + V((s * 0.1 * hl, 0.45 * hl, 0.35 * hl))], [0.11 * hr, 0.08 * hr, 0.02 * hr], g, "Horn")
            tube([m, m + V((s * 0.3 * hl, -0.05 * hl, 0.35 * hl))], [0.06 * hr, 0.015 * hr], g, "Horn")
            w = hc + V((s * 0.42 * hr, -1.05 * hr, -0.3 * hr))
            tube([w, w + V((s * 0.5 * hr, 0.1 * hr, -0.05 * hr)), w + V((s * 0.85 * hr, 0.5 * hr, -0.35 * hr))],
                 [0.05 * hr, 0.035 * hr, 0.01 * hr], g, "Spike")
            for i in range(3):
                bb = hc + V((s * 0.3 * hr, 0.72 * hr, (0.45 - 0.32 * i) * hr))
                cone(bb, bb + V((s * 0.15 * hr, 0.5 * hr, 0.12 * hr)), 0.16 * hr, g, "Spike")
    if kind == "aqua":
        for s in (-1, 1):
            fin(hc + V((s * 0.8 * hr, 0.15 * hr, 0.1 * hr)), (s, 0.7, 0.35), (0, 0.4, 1), hr * (0.7 + 0.3 * t), g)


def torso(bc, bw, bl, bh, rot=0.0):
    PIV["Body"] = bc
    sph(bc, (bw, bl, bh), "Body", "Skin", rot=(rot, 0, 0))
    off = V((0, -0.38 * bl, -0.14 * bh))
    off.rotate(Euler((rot, 0, 0)))
    sph(bc + off, (0.8 * bw, 0.72 * bl, 0.84 * bh), "Body", "Belly", rot=(rot, 0, 0))


def legs(bc, bw, bl, bh, ys, th):
    PIV["Legs"] = bc
    tr, fr = 0.26 * th, 0.17 * th
    for sy in ys:
        for sx in (-1, 1):
            hip = bc + V((sx * 0.68 * bw, sy * bl, -0.3 * bh))
            ft = V((hip.x * 1.05, hip.y - 0.06, fr * 0.8))
            sph(hip, (tr, tr * 1.1, tr), "Legs", "Skin")
            tube([hip, ft + V((0, 0, fr * 0.5))], [tr * 0.75, fr * 0.9], "Legs", "Skin")
            sph(ft, (fr, fr * 1.3, fr * 0.8), "Legs", "Skin")
            for cx in (-1, 0, 1):
                sph(ft + V((cx * fr * 0.55, -fr * 1.15, -fr * 0.35)), fr * 0.28, "Legs", "Claw")


def spine(bc, bl, bh, n, h, r, ys=(-0.55, 0.65), rot=0.0):
    for i in range(n):
        u = i / max(n - 1, 1)
        y = bl * (ys[0] + (ys[1] - ys[0]) * u)
        p = V((0, y, bh * math.sqrt(max(0, 1 - (y / bl) ** 2))))
        p.rotate(Euler((rot, 0, 0)))
        p += bc
        hh = h * (1 - 0.6 * abs(u - 0.45))
        cone(p - V((0, 0, 0.05)), p + V((0, 0.05, hh)), r, "Body", "Spike", flat=(0.45, 1, 1))


def neckhead(base, hc, hr, t, rad, g="Head", kind="classic"):
    base, hc = V(base), V(hc)
    mid = (base + hc) / 2 + V((0, -0.05, 0.08))
    tube([base, mid, hc + V((0, 0.2 * hr, -0.3 * hr))], [rad, rad * 0.9, rad * 0.85], "Body", "Skin")
    head(hc, hr, t, g, kind)


def tail(start, L, r0, t, end=None, curl=1):
    s = V(start)
    PIV["Tail"] = s
    pts = [s, s + V((0.05 * L * curl, 0.38 * L, -0.12)), s + V((0.18 * L * curl, 0.75 * L, 0.02)),
           s + V((0.32 * L * curl, 1.0 * L, 0.125 * L))]
    rad = [r0, r0 * 0.7, r0 * 0.4, r0 * 0.12]
    tube(pts, rad, "Tail", "Skin")
    if t > 0:
        for p, r in zip(pts[1:3], rad[1:3]):
            cone(p + V((0, 0, r * 0.5)), p + V((0, 0.05, r + 0.06 + 0.1 * t)), 0.05 + 0.04 * t, "Tail", "Spike", flat=(0.45, 1, 1))
    d = (pts[3] - pts[2]).normalized()
    if end == "spade" and t > 0:
        cone(pts[3] - d * 0.03, pts[3] + d * (0.14 + 0.1 * t), 0.08 + 0.04 * t, "Tail", "Spike", flat=(1, 0.3, 1))
    if end == "club" and t > 0:
        sph(pts[3], 0.12 + 0.1 * t, "Tail", "Spike")
        for s in (-1, 1):
            cone(pts[3], pts[3] + V((s * (0.2 + 0.12 * t), 0, 0.05)), 0.05 + 0.03 * t, "Tail", "Horn")


# ---------- types ----------
def classique(t):
    bw, bl, bh, zb = 0.55 + 0.05 * t, 0.6 + 0.35 * t, 0.5 + 0.05 * t, 0.62 + 0.2 * t
    bc = V((0, 0, zb))
    torso(bc, bw, bl, bh)
    legs(bc, bw, bl, bh, (-0.55, 0.55), 1 + 0.15 * t)
    spine(bc, bl, bh, round(3 + 3 * t), 0.1 + 0.18 * t, 0.07 + 0.05 * t)
    hr = 0.58 - 0.18 * t
    neckhead(bc + V((0, -0.55 * bl, 0.45 * bh)), (0, -(0.55 + 0.6 * t), zb + 0.62 + 0.45 * t), hr, t, 0.24 - 0.03 * t)
    for sx, g in ((1, "WingL"), (-1, "WingR")):
        wing(bc + V((sx * 0.32 * bw, -0.2 * bl, 0.8 * bh)), 0.7 + 0.9 * t, sx, g)
    tail(bc + V((0, 0.8 * bl, -0.15 * bh)), 0.8 + 1.1 * t, 0.24 + 0.04 * t, t, "spade")


def wyvern(t):
    bw, bl, bh, zb, rot = 0.5 + 0.05 * t, 0.55 + 0.3 * t, 0.55 + 0.1 * t, 0.78 + 0.32 * t, -0.45
    bc = V((0, 0.1, zb))
    torso(bc, bw, bl, bh, rot)
    legs(bc, bw, bl, bh, (0.35,), 1.3 + 0.2 * t)
    spine(bc, bl, bh, round(3 + 2 * t), 0.1 + 0.15 * t, 0.07 + 0.04 * t, rot=rot)
    nb = V((0, -0.6 * bl, 0.4 * bh))
    nb.rotate(Euler((rot, 0, 0)))
    hr = 0.56 - 0.17 * t
    neckhead(bc + nb, (0, -(0.45 + 0.45 * t), zb + 0.75 + 0.6 * t), hr, t, 0.22 - 0.03 * t, kind="wyvern")
    for sx, g in ((1, "WingL"), (-1, "WingR")):
        wing(bc + V((sx * 0.35 * bw, -0.25 * bl, 0.75 * bh)), 0.95 + 1.15 * t, sx, g, up=0.75)
    tail(bc + V((0, 0.7 * bl, -0.45 * bh)), 1.0 + 1.3 * t, 0.24 + 0.03 * t, t, "spade", curl=-1)


def drake(t):
    bw, bl, bh, zb = 0.68 + 0.08 * t, 0.68 + 0.35 * t, 0.5 + 0.07 * t, 0.58 + 0.17 * t
    bc = V((0, 0, zb))
    torso(bc, bw, bl, bh)
    legs(bc, bw, bl, bh, (-0.55, 0.55), 1.25 + 0.25 * t)
    spine(bc, bl, bh, round(4 + 3 * t), 0.14 + 0.26 * t, 0.1 + 0.07 * t)
    hr = 0.56 - 0.15 * t
    neckhead(bc + V((0, -0.55 * bl, 0.4 * bh)), (0, -(0.6 + 0.6 * t), zb + 0.5 + 0.32 * t), hr, t, 0.27 - 0.02 * t, kind="drake")
    tail(bc + V((0, 0.8 * bl, -0.1 * bh)), 0.75 + 1.0 * t, 0.28 + 0.06 * t, t, "club")


def hydre(t):
    bw, bl, bh, zb = 0.6 + 0.06 * t, 0.62 + 0.3 * t, 0.5 + 0.06 * t, 0.6 + 0.18 * t
    bc = V((0, 0, zb))
    torso(bc, bw, bl, bh)
    legs(bc, bw, bl, bh, (-0.55, 0.55), 1.1 + 0.15 * t)
    spine(bc, bl, bh, round(2 + 2 * t), 0.1 + 0.12 * t, 0.07 + 0.04 * t, ys=(-0.2, 0.65))
    hr, spread = 0.42 - 0.12 * t, 0.6 + 0.3 * t
    for k, ax in enumerate((-1, 0, 1)):
        hc = (ax * spread, -(0.5 + 0.45 * t) + abs(ax) * 0.15, zb + 0.72 + 0.6 * t - abs(ax) * (0.18 - 0.14 * t))
        neckhead(bc + V((ax * 0.25 * bw, -0.55 * bl, 0.4 * bh)), hc, hr, t, 0.17 - 0.02 * t, g=f"Head{k + 1}", kind="hydra")
    tail(bc + V((0, 0.8 * bl, -0.15 * bh)), 0.8 + 1.0 * t, 0.24 + 0.04 * t, t)


def serpent_body(pts, rad):
    PIV["Body"] = pts[len(pts) // 2].copy()
    tube(pts, rad, "Body", "Skin")


def oriental(t):
    N, L, A, z0, R = 10, 2.2 + 1.8 * t, 0.55 + 0.3 * t, 0.75 + 0.35 * t, 0.24 + 0.05 * t
    pts, rad = [], []
    for i in range(N):
        u = i / (N - 1)
        pts.append(V((A * math.sin(u * 5.0), -0.45 * L + u * L, z0 + 0.3 * (1 + t) * math.sin(u * 5.0 + 1.3))))
        rad.append(R * (0.85 if i == 0 else (1 - 0.82 * u ** 1.3)))
    serpent_body(pts, rad)
    for i in range(1, N - 1):
        p = pts[i]
        cone(p + V((0, 0, rad[i] * 0.6)), p + V((0, 0.06, rad[i] + 0.1 + 0.08 * t)), 0.07 + 0.03 * t, "Body", "Spike", flat=(0.45, 1, 1))
    PIV["Legs"] = pts[3].copy()
    for i in (2, 5):
        p, r = pts[i], rad[i]
        for sx in (-1, 1):
            hip = p + V((sx * r * 0.75, 0, -r * 0.45))
            ft = hip + V((sx * 0.12, -0.08, -(0.28 + 0.15 * t)))
            fr = 0.1 + 0.03 * t
            sph(hip, fr * 1.2, "Legs", "Skin")
            tube([hip, ft], [fr * 0.8, fr * 0.7], "Legs", "Skin")
            sph(ft, (fr, fr * 1.2, fr * 0.8), "Legs", "Skin")
            for cx in (-1, 0, 1):
                sph(ft + V((cx * fr * 0.55, -fr * 1.1, -fr * 0.3)), fr * 0.3, "Legs", "Claw")
    e = pts[-1]
    for off in ((0, 0.08, 0.06), (0.07, 0.02, -0.05), (-0.07, 0.02, -0.05)):
        sph(e + V(off) * (1 + t), 0.12 + 0.06 * t, "Body", "Spike")
    hr = 0.5 - 0.14 * t
    head(pts[0] + V((0, -0.45 * hr, 0.55 * hr)), hr, t, kind="oriental")


def path(C, sy=1.0, sc=1.0):
    return [V((x * sc, y * sy * sc, z * sc)) for x, y, z in C]


def amphiptere(t):
    k = 1 + 0.35 * t
    C = [(1.0, 0.75, 0.06), (0.35, 0.95, 0.16), (-0.4, 0.75, 0.22), (-0.75, 0.1, 0.24), (-0.45, -0.5, 0.26),
         (0.2, -0.55, 0.28), (0.55, -0.1, 0.34), (0.35, 0.25, 0.68), (0.08, 0.1, 1.08), (0, -0.25, 1.4)]
    pts = path(C, sc=k)
    rad = [r * (1 + 0.25 * t) for r in (0.04, 0.12, 0.19, 0.23, 0.25, 0.25, 0.25, 0.23, 0.2, 0.18)]
    for p, r in zip(pts, rad):
        p.z = max(p.z, r)
    serpent_body(pts, rad)
    root = (pts[7] + pts[8]) / 2
    for sx, g in ((1, "WingL"), (-1, "WingR")):
        wing(root + V((sx * 0.12, 0, 0.05)), 0.7 + 0.9 * t, sx, g)
    for i in (2, 3, 4, 5):
        p = pts[i]
        cone(p + V((0, 0, rad[i] * 0.6)), p + V((0, 0, rad[i] + 0.08 + 0.08 * t)), 0.06 + 0.03 * t, "Body", "Spike", flat=(0.45, 1, 1))
    hr = 0.5 - 0.14 * t
    head(pts[-1] + V((0, -0.3 * hr, 0.4 * hr)), hr, t, kind="amph")


def aquatique(t):
    C = [(0, -0.35, 1.08), (0, -0.12, 0.62), (0.12, 0.3, 0.27), (0, 0.78, 0.5), (-0.25, 1.2, 0.26),
         (-0.12, 1.6, 0.42), (0.2, 1.95, 0.22)]
    pts = path(C, sy=1 + 0.45 * t, sc=1 + 0.2 * t)
    rad = [r * (1 + 0.2 * t) for r in (0.2, 0.24, 0.26, 0.25, 0.22, 0.15, 0.06)]
    for p, r in zip(pts, rad):
        p.z = max(p.z, r)
    serpent_body(pts, rad)
    PIV["Fins"] = pts[2].copy()
    for i, size in ((2, 0.45 + 0.4 * t), (4, 0.32 + 0.3 * t)):
        p, r = pts[i], rad[i]
        for sx in (-1, 1):
            fin(p + V((sx * r * 0.8, -0.05, -r * 0.2)), (sx, 0.3, -0.3), (0, 1, 0), size, "Fins")
    for i in (3, 5):
        p, r = pts[i], rad[i]
        s = 0.35 + 0.3 * t
        fin(p + V((0, -0.45 * s, r * 0.6)), (0, 1, 0), (0, 0, 1), s, "Fins")
    for sx in (-1, 1):
        fin(pts[-1], (sx, 0.5, 0), (0, 1, 0), 0.4 + 0.35 * t, "Fins")
    hr = 0.52 - 0.15 * t
    head(pts[0] + V((0, -0.35 * hr, 0.35 * hr)), hr, t, kind="aqua")


TYPES = [("Classique", classique), ("Wyvern", wyvern), ("Drake", drake), ("Hydre", hydre),
         ("Oriental", oriental), ("Amphiptere", amphiptere), ("Aquatique", aquatique)]


def build(typ, fn, stage):
    t, S = (0, 0.5, 1)[stage], (1.0, 1.45, 2.0)[stage]
    CUR["typ"] = typ
    P.clear()
    PIV.clear()
    fn(t)
    sel([p[0] for p in P])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    groups = {}
    for o, g, r in P:
        groups.setdefault((g, r), []).append(o)
    out = []
    for (g, r), objs in groups.items():
        sel(objs)
        if len(objs) > 1:
            bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active
        name = g if (r == "Wing" and g.startswith("Wing")) else (g + ("Fins" if r == "Wing" and g != "Fins" else ("" if r == "Wing" else SUFFIX[r])))
        o.name = o.data.name = name
        bpy.context.scene.cursor.location = PIV.get(g, PIV.get("Body", V()))
        sel([o])
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        out.append(o)
    tot = sum(len(p.vertices) - 2 for o in out for p in o.data.polygons)
    ratio = min(1.0, 6000 / tot)
    if ratio < 1:
        for o in out:
            sel([o])
            m = o.modifiers.new("d", "DECIMATE")
            m.ratio = ratio
            bpy.ops.object.modifier_apply(modifier=m.name)
    for o in out:
        o.location = o.location * S
        o.scale = (S, S, S)
    sel(out)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    model = f"{typ}_{STAGES[stage]}"
    bpy.ops.export_scene.fbx(filepath=f"{OUT}/fbx/{model}.fbx", use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                             mesh_smooth_type="FACE", add_leaf_bones=False)
    tris = 0
    for o in out:
        o.name = f"{model}_{o.name}"
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print(f"{model}: {len(out)} pieces, {tris} triangles")
    return out


# ---------- scene de rendu ----------
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.view_settings.view_transform = 'Standard'
try:
    scene.cycles.use_denoising = True
except Exception:
    pass
scene.render.resolution_x, scene.render.resolution_y = 1200, 540
world = bpy.data.worlds.new("w")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.75, 0.8, 0.88, 1)
bg.inputs[1].default_value = 0.55
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
sun.data.energy = 2.2
sun.rotation_euler = (math.radians(45), math.radians(10), math.radians(30))
scene.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
ground = bpy.context.object
gm = bpy.data.materials.new("Ground")
try:
    gm.use_nodes = True
except Exception:
    pass
for n in gm.node_tree.nodes:
    if n.type == "BSDF_PRINCIPLED":
        n.inputs["Base Color"].default_value = (0.8, 0.8, 0.76, 1)
ground.data.materials.append(gm)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 13.5
scene.collection.objects.link(cam)
scene.camera = cam

OFFX = (-5.6, -2.2, 3.4)
allmodels = []
for ti, (typ, fn) in enumerate(TYPES):
    coll = bpy.data.collections.new(typ)
    scene.collection.children.link(coll)
    objs_type = []
    for st in range(3):
        objs = build(typ, fn, st)
        for o in objs:
            for c in o.users_collection:
                c.objects.unlink(o)
            coll.objects.link(o)
            o.location += V((OFFX[st], ti * 25, 0))
        objs_type += objs
    allmodels.append(objs_type)

dirv = V((0.7, -1, 0.5)).normalized()
for ti, (typ, fn) in enumerate(TYPES):
    for k, objs in enumerate(allmodels):
        for o in objs:
            o.hide_render = k != ti
    target = V((0, ti * 25, 1.6))
    cam.location = target + dirv * 40
    cam.rotation_euler = (-dirv).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{OUT}/render/{typ}.png"
    bpy.ops.render.render(write_still=True)
    print("render", typ)
for objs in allmodels:
    for o in objs:
        o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/Dragons_base.blend")
print("OK")
