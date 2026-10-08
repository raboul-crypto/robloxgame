# Dragon classique - stade ADULTE. A executer apres 01 a 05 (reutilise les materiaux de l'ado).
# Meme construction que l'ado, mais : plus massif, cou plus long, tete plus petite par rapport au corps,
# grandes cornes recourbees, crete plus haute, rouge plus sombre, ailes plus grandes.
import bpy, bmesh, math
from mathutils import Vector as V, Matrix
sc = bpy.context.scene; P = "Adulte_"
for o in [o for o in bpy.data.objects if o.name.startswith(P)]: bpy.data.objects.remove(o, do_unlink=True)
coll = bpy.data.collections.get("Adulte") or bpy.data.collections.new("Adulte")
if coll.name not in sc.collection.children: sc.collection.children.link(coll)
S = Matrix.Translation((11.5, 0, 0)) @ Matrix.Scale(1.6, 4)
gr = bpy.data.objects.get("Ground")
if gr: gr.scale = (80 / 30, 80 / 30, 1)       # sol 80 x 80 pour faire tenir l'adulte
def lin(c): return tuple(x ** 2.2 for x in c)
def sstep(a, b, x):
    t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def put(o, local=None):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)
    o.matrix_world = S @ (local if local is not None else o.matrix_world); return o

# ---------------- corps (metaballs) ----------------
K = 1.74
mb = bpy.data.metaballs.new("AdulteMB"); mb.resolution = 0.03; mb.render_resolution = 0.03; mb.threshold = 0.6
def ell(co, r, size=(1, 1, 1), st=2.4):
    e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r * K
    e.size_x, e.size_y, e.size_z = size; e.stiffness = st
def chain(pts, n=5, f=0.95, st=2.0):
    for i in range(len(pts) - 1):
        A, B = pts[i], pts[i + 1]
        for k in range(n):
            t = k / n; ell(tuple(lerp(A[j], B[j], t) for j in range(3)), lerp(A[3], B[3], t) * f, (1, 1, 1), st)
    ell(pts[-1][:3], pts[-1][3] * f, (1, 1, 1), st)
HO = V((0, -0.62, 0.92))                       # tete portee plus haut et plus loin (long cou)
HC = V((0, -0.9, 2.05)) + HO; SN = V((0, -1.35, 1.9)) + HO
# --- tete : meme base que l'ado, machoire et arcades plus marquees ---
ell(HC, 0.38, (0.95, 1.15, 0.72), 2.6)
ell(SN, 0.27, (0.84, 1.6, 0.6), 2.8)
for s in (-1, 1): ell(V((s * 0.08, -1.68, 1.88)) + HO, 0.12, (1, 1, 0.72), 3.0)
ell(V((0, -1.15, 1.72)) + HO, 0.235, (0.95, 1.5, 0.52), 2.8)              # machoire plus forte
for s in (-1, 1): ell(V((s * 0.17, -0.98, 1.78)) + HO, 0.16, (0.8, 1.2, 0.8), 3.0)   # joues / masseters
# --- tronc massif ---
ell((0, -0.25, 1.5), 0.55, (0.8, 1.0, 1.08), 2.8)        # poitrail profond
ell((0, -0.58, 1.36), 0.34, (1.0, 0.7, 1.15), 2.4)       # torse avant
ell((0, 0.25, 1.5), 0.53, (0.76, 1.12, 0.9), 2.8)        # cotes
ell((0, 0.78, 1.45), 0.4, (0.68, 1.0, 0.8), 2.8)         # taille (moins rentree que l'ado)
ell((0, 1.18, 1.48), 0.43, (0.78, 0.95, 0.86), 2.8)      # hanches
NECK = [(0, -0.58, 1.88, 0.33), (0, -0.78, 2.18, 0.3), (0, -0.96, 2.48, 0.27), (0, -1.1, 2.75, 0.25), (0, -1.22, 2.92, 0.235), (0, -1.3, 3.0, 0.22)]
chain(NECK, 4, 1.0)
CLAWS = []
def toe_chain(pts, rads, st=2.2, n=6):
    for i in range(len(pts) - 1):
        for k in range(n):
            t = k / n; ell(pts[i].lerp(pts[i + 1], t), (rads[i] + (rads[i + 1] - rads[i]) * t), (1, 1, 1), st)
    ell(pts[-1], rads[-1], (1, 1, 1), st)
def foot(cx, cy, s, size=1.0):
    """cheville -> metatarse -> paume -> 3 doigts separes + ergot."""
    c = V((cx, cy, 0.0)); z0 = 0.055 * size
    ell(c + V((0, -0.01, z0)), 0.09 * size, (1.25, 0.95, 0.55), 2.6)
    for ang in (-34, 0, 34):
        a = math.radians(ang * s)
        d = V((math.sin(a), -math.cos(a), 0))
        b = c + d * 0.07 * size + V((0, 0, z0))
        pts = [b, b + d * 0.09 * size + V((0, 0, -0.012 * size)), b + d * 0.17 * size + V((0, 0, -0.024 * size)), b + d * 0.23 * size + V((0, 0, -0.028 * size))]
        toe_chain(pts, [0.048 * size, 0.042 * size, 0.037 * size, 0.031 * size], 2.6)
        for j in (1, 2): ell(pts[j], 0.048 * size, (1, 1, 0.85), 3.0)
        CLAWS.append((pts[-1] + d * 0.015 * size, d, size))
    d = V((0.4 * s, 1, 0)).normalized()
    p0 = c + d * 0.05 * size + V((0, 0, 0.09 * size))
    toe_chain([p0, p0 + d * 0.07 * size + V((0, 0, -0.02 * size))], [0.034 * size, 0.028 * size], 2.6, 4)
    CLAWS.append((p0 + d * 0.085 * size + V((0, 0, -0.02 * size)), d, size * 0.75))
for s in (-1, 1):
    ell((s * 0.32, -0.22, 1.9), 0.22, (0.8, 1.25, 0.6), 3.0)      # omoplates
    FRONT = [(s * 0.33, -0.3, 1.5, 0.29), (s * 0.42, -0.16, 1.2, 0.24), (s * 0.47, -0.02, 0.95, 0.17), (s * 0.48, -0.24, 0.62, 0.15), (s * 0.48, -0.46, 0.3, 0.115), (s * 0.48, -0.53, 0.2, 0.09), (s * 0.48, -0.6, 0.08, 0.082)]
    BACK = [(s * 0.34, 1.18, 1.4, 0.36), (s * 0.42, 0.95, 1.08, 0.28), (s * 0.48, 0.7, 0.8, 0.17), (s * 0.49, 1.0, 0.6, 0.14), (s * 0.49, 1.22, 0.42, 0.12), (s * 0.49, 1.12, 0.24, 0.095), (s * 0.49, 0.98, 0.09, 0.085)]
    chain(FRONT); chain(BACK)
    ell((s * 0.42, -0.2, 1.24), 0.19, (0.8, 0.9, 1.3), 2.2)       # biceps
    ell((s * 0.48, -0.12, 0.8), 0.16, (0.85, 0.95, 1.5), 2.2)     # avant-bras
    ell((s * 0.4, 1.1, 1.12), 0.25, (0.7, 1.0, 1.2), 2.2)         # cuisse
    foot(s * 0.48, -0.64, s, 1.2)
    foot(s * 0.49, 0.94, s, 1.28)
TAILC = [(0, 1.5, 1.4, 0.33), (0.05, 2.05, 1.05, 0.25), (0.22, 2.65, 0.72, 0.19), (0.45, 3.2, 0.55, 0.14), (0.7, 3.72, 0.5, 0.1), (0.9, 4.18, 0.55, 0.075), (1.02, 4.55, 0.65, 0.056)]
TAIL = []
for i in range(len(TAILC) - 1):
    a, b = TAILC[i], TAILC[i + 1]
    for k in range(4):
        t = k / 4; TAIL.append(tuple(lerp(a[j], b[j], t) for j in range(4)))
TAIL.append(TAILC[-1])
for x, y, z, r in TAIL: ell((x, y, z), r * 0.92, (1, 1, 1), 2.0)
def tail_x(y):
    if y <= TAILC[0][1]: return 0.0
    for a, b in zip(TAILC, TAILC[1:]):
        if a[1] <= y <= b[1]: return lerp(a[0], b[0], (y - a[1]) / (b[1] - a[1]))
    return TAILC[-1][0]
mo = bpy.data.objects.new(P + "MB", mb); sc.collection.objects.link(mo)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = mo; mo.select_set(True); bpy.context.view_layer.update()
bpy.ops.object.convert(target='MESH')
body = bpy.context.view_layer.objects.active; body.name = P + "Body"
for p in body.data.polygons: p.use_smooth = True
me = body.data
SKIN = V(lin((0.54, 0.07, 0.055))); BELLY = V(lin((0.9, 0.62, 0.36)))
col = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT'); msk = me.color_attributes.new("Mask", 'FLOAT_COLOR', 'POINT')
for v in me.vertices:
    p = v.co; n = v.normal
    bb = sstep(0.15, 0.55, -n.y * 0.7 - n.z * 0.6) * (1 - sstep(0.2, 0.38, abs(p.x)))
    bh = sstep(0.25, 0.65, -n.z) * (1 - sstep(0.12, 0.26, abs(p.x)))
    hw = 1 - sstep(0.5, 0.85, min((p - HC).length, (p - SN).length + 0.05))
    bel = bb * (1 - hw) + bh * hw
    if p.z < 0.14: bel = 0
    c = SKIN.lerp(BELLY, bel); col.data[v.index].color = (*c, 1)
    m = (1 - bel) * (1 - 0.6 * (1 - sstep(0.25, 0.45, (p - SN).length)))
    msk.data[v.index].color = (m, m, m, 1)
skin = bpy.data.materials.get("AdulteSkinReal")
if skin: bpy.data.materials.remove(skin)
skin = bpy.data.materials["AdoSkinReal"].copy(); skin.name = "AdulteSkinReal"
for n in skin.node_tree.nodes:
    if n.type == 'BUMP': n.inputs["Strength"].default_value = 0.55       # ecailles plus marquees
me.materials.append(skin)
def hit(origin, d):
    d = V(d).normalized(); h, l, n, _ = body.ray_cast(V(origin) + d * 6, -d); return l, n
put(body, body.matrix_world.copy())

HORN = bpy.data.materials["AdoHornReal"]; SPIKE = bpy.data.materials["AdoSpikeReal"]; CLAW = bpy.data.materials["AdoClawReal"]
PUP = bpy.data.materials["Eye"]; HL = bpy.data.materials["Highlight"]; IRIS = bpy.data.materials["AdoIrisGlow"]
def tube(name, pts, radii, mm, res=12):
    cu = bpy.data.curves.new(P + name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = res
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 5; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, pp, r in zip(sp.bezier_points, pts, radii):
        bp.co = V(pp); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r
    o = bpy.data.objects.new(P + name, cu); cu.materials.append(mm); sc.collection.objects.link(o); return put(o, Matrix())

# ---------------- yeux (plus etroits : regard adulte) ----------------
brow = bpy.data.materials.get("AdulteLid") or bpy.data.materials.new("AdulteLid")
brow.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin((0.55, 0.09, 0.07)), 1)
def lemon(name, loc, q, w, h, dep, mm, sharp=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1)
    o = bpy.context.object; o.name = P + name; o.data.materials.append(mm)
    for v in o.data.vertices:
        x = v.co.x; v.co.z *= max(0.0, 1 - x * x) ** (0.5 * sharp)
    for pp in o.data.polygons: pp.use_smooth = True
    return put(o, Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((w, dep, h, 1)))
def face_quat(n, tilt_deg, s):
    up = V((0, 0, 1)); z = (up - n * up.dot(n)).normalized()
    y = -n; x = y.cross(z)
    q = Matrix((x, y, z)).transposed().to_quaternion()
    return q @ Matrix.Rotation(math.radians(tilt_deg * s), 4, 'Y').to_quaternion()
for s in (-1, 1):
    d = V((s * 0.5, -0.82, 0.12)).normalized(); l, n = hit(HC, d)
    q = face_quat(n, -18, s)
    lemon(f"Eye_{s}", l - n * 0.035, q, 0.135, 0.062, 0.06, IRIS, 1.3)
    lemon(f"EyePupil_{s}", l + n * 0.02, q, 0.013, 0.056, 0.01, PUP, 1.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1); o = bpy.context.object; o.name = P + f"EyeHL_{s}"; o.data.materials.append(HL)
    for pp in o.data.polygons: pp.use_smooth = True
    put(o, Matrix.Translation(l + n * 0.024 + q @ V((-0.045, 0, 0.018))) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((0.013, 0.005, 0.013, 1)))
    qb = face_quat(n, -26, s)                                   # arcade lourde, plus basse
    lemon(f"EyeBrow_{s}", l - n * 0.025 + qb @ V((0.0, 0, 0.062)), qb, 0.2, 0.05, 0.06, brow, 1.6)
    l2, n2 = hit(V((s * 0.08, -1.68, 1.88)) + HO, V((s * 0.3, -1, 0.35)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1); o = bpy.context.object; o.name = P + f"Nostril_{s}"; o.data.materials.append(PUP)
    put(o, Matrix.Translation(l2 - n2 * 0.012) @ n2.to_track_quat('-Y', 'Z').to_matrix().to_4x4() @ Matrix.Diagonal((0.038, 0.022, 0.017, 1)))

# ---------------- bouche + crocs ----------------
lipm = bpy.data.materials["AdoLip"]
for s in (-1, 1):
    pts = []
    ys = [-1.78, -1.68, -1.52, -1.36, -1.2, -1.06, -0.97]
    zs = [1.77, 1.76, 1.765, 1.775, 1.79, 1.83, 1.89]
    for y, z in zip(ys, zs):
        h_, l, n, _ = body.ray_cast(V((s * 1.5, y, z)) + HO, V((-s, 0, 0)))
        if not h_:
            h_, l, n, _ = body.ray_cast(V((0, -2.5, z)) + HO, V((0, 1, 0)))
        pts.append((l - n * 0.006, n))
    tube(f"Mouth_{s}", [p for p, _ in pts], [0.012, 0.018, 0.021, 0.021, 0.02, 0.017, 0.006], lipm)
    for i, (dz, ln) in ((1, (-1, 0.12)), (3, (-1, 0.09)), (2, (1, 0.08)), (4, (-1, 0.06))):
        p, n = pts[i]
        b = p + V((0, 0, -0.01 if dz < 0 else 0.01)) - n * 0.01
        tube(f"Fang_{s}_{i}", [b, b + V((0, -0.01, dz * ln * 0.5)) + n * 0.012, b + V((0, -0.02, dz * ln))], [0.024, 0.015, 0.002], HORN)

# ---------------- cornes : grande paire recourbee + petite paire + corne nasale ----------------
for s in (-1, 1):
    l, n = hit(HC, (s * 0.4, 0.4, 0.8)); b = l - n * 0.06
    tube(f"Horn_{s}", [b, b + V((s * 0.08, 0.3, 0.1)), b + V((s * 0.14, 0.68, 0.08)), b + V((s * 0.18, 1.02, 0.2)), b + V((s * 0.16, 1.22, 0.42))],
         [0.1, 0.08, 0.055, 0.03, 0.004], HORN, 16)
    l, n = hit(HC, (s * 0.7, 0.55, 0.45)); b = l - n * 0.04
    tube(f"Horn2_{s}", [b, b + V((s * 0.12, 0.22, 0.02)), b + V((s * 0.2, 0.42, 0.08))], [0.055, 0.032, 0.003], HORN)
    for k, (dz, lg) in enumerate(((0.08, 0.4), (-0.08, 0.32), (-0.24, 0.22))):
        l, n = hit(V((0, -0.95, 1.82)) + HO, (s * 1, 0.35, dz)); b = l - n * 0.03
        tube(f"Cheek_{s}_{k}", [b, b + V((s * 0.12, lg * 0.5, 0.0)), b + V((s * 0.16, lg, 0.05))], [0.05, 0.028, 0.003], HORN)
l, n = hit(SN + V((0, -0.2, 0)), (0, -0.25, 1)); b = l - n * 0.02
tube("NoseHorn", [b, b + V((0, -0.02, 0.07)), b + V((0, 0.04, 0.13))], [0.04, 0.022, 0.003], HORN)

# ---------------- crete dorsale (plus haute) + bout de queue ----------------
SPY = [-1.2, -1.02, -0.8, -0.58, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.55, 1.95, 2.35, 2.75, 3.15, 3.55, 3.95, 4.3]
for i, y in enumerate(SPY):
    l, n = hit((tail_x(y), y, 0.5), (0, 0, 1))
    h = 0.32 if 4 <= i <= 11 else (0.2 if i < 4 else max(0.12, 0.26 - 0.03 * (i - 11)))
    tube(f"Spike_{i}", [l - n * 0.05, l + n * h * 0.5 + V((0, 0.06, 0)), l + n * h + V((0, 0.17, 0))], [0.08, 0.04, 0.002], SPIKE)
e2 = V(TAILC[-1][:3]); dd = (e2 - V(TAILC[-2][:3])).normalized()
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, radius2=0, depth=0.42)
o = bpy.context.object; o.name = P + "TailTip"; o.data.materials.append(SPIKE)
put(o, Matrix.Translation(e2 + dd * 0.15) @ dd.to_track_quat('Z', 'Y').to_matrix().to_4x4() @ Matrix.Diagonal((1, 0.3, 1, 1)))
for i, (tip, d, sz) in enumerate(CLAWS):
    tube(f"Claw_{i}", [tip - d * 0.025 * sz, tip + d * 0.05 * sz + V((0, 0, 0.004)), tip + d * 0.1 * sz + V((0, 0, -0.035 * sz))], [0.03 * sz, 0.018 * sz, 0.002], CLAW)

# ---------------- ailes (meme methode que 04_ado_ailes.py, plus grandes) ----------------
wm = bpy.data.materials.get("AdulteWingReal")
if wm: bpy.data.materials.remove(wm)
wm = bpy.data.materials["AdoWingReal"].copy(); wm.name = "AdulteWingReal"
ramp = [n for n in wm.node_tree.nodes if n.type == 'VALTORGB'][0].color_ramp.elements
ramp[0].color = (0.2, 0.016, 0.012, 1); ramp[1].color = (0.45, 0.045, 0.025, 1)
BONE = bpy.data.materials["AdoBone"]
def resample(poly, n):
    poly = [V(p) for p in poly]
    seg = [(poly[i + 1] - poly[i]).length for i in range(len(poly) - 1)]
    tot = sum(seg); out = []
    for k in range(n):
        d = tot * k / (n - 1); i = 0
        while i < len(seg) - 1 and d > seg[i]: d -= seg[i]; i += 1
        out.append(poly[i].lerp(poly[i + 1], min(1.0, d / seg[i] if seg[i] else 0)))
    return out
def smooth_poly(poly, it=2):
    pts = [V(p) for p in poly]
    for _ in range(it):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]): new += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        new.append(pts[-1]); pts = new
    return pts
KW = 2.2
R = V((0, 0, 0)); E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))],
     [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))],
     [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))],
     [W, V((0.62, 0.64, 0.0)), V((0.52, 1.06, -0.3))]]
BODY_REAR = V((0.02, 0.8, -0.22))
SAG = V((0, 0.25, -1)).normalized()
for s in (-1, 1):
    d = V((s * 0.45, 0.1, 1)).normalized()
    h, sh, n, _ = body.ray_cast(V((s * 0.28, -0.15, 1.85)) + d * 6, -d)
    root = sh - n * 0.06
    def W2L(p): return root + V((s * p.x, p.y, p.z)) * KW
    nt, nv = 16, 9
    bm = bmesh.new()
    def panel(A, Bc, scallop, sag):
        A = resample(smooth_poly(A), nt); Bc = resample(smooth_poly(Bc), nt)
        grid = []
        for i in range(nt):
            t = i / (nt - 1); row = []
            for j in range(nv):
                v = j / (nv - 1)
                p = A[i].lerp(Bc[i], v)
                w = math.sin(math.pi * v)
                p = p + SAG * (sag * w * math.sin(math.pi * t) ** 0.7)
                p = p.lerp(W, scallop * w * t ** 3)
                row.append(bm.verts.new(W2L(p)))
            grid.append(row)
        for i in range(nt - 1):
            for j in range(nv - 1):
                bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    for a, b in zip(F, F[1:]): panel(a, b, 0.22, 0.07)
    panel([W, E, R], F[3] + [BODY_REAR], 0.0, 0.06)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    wme = bpy.data.meshes.new(P + f"Wing_{s}"); bm.to_mesh(wme); bm.free()
    o = bpy.data.objects.new(P + f"Wing_{s}", wme); coll.objects.link(o); o.matrix_world = S
    wme.materials.append(wm)
    m1 = o.modifiers.new("sol", 'SOLIDIFY'); m1.thickness = 0.01; m1.offset = 0
    m2 = o.modifiers.new("sub", 'SUBSURF'); m2.levels = 1; m2.render_levels = 2
    for p in wme.polygons: p.use_smooth = True
    tube(f"WingBone_arm_{s}", [W2L(R), W2L(E), W2L(W)], [0.055 * KW, 0.044 * KW, 0.036 * KW], BONE)
    for k, f in enumerate(F):
        tube(f"WingBone_f{k}_{s}", [W2L(p) for p in f], [0.026 * KW, 0.017 * KW, 0.004], BONE)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.024 * KW, radius2=0, depth=0.1 * KW)
    c = bpy.context.object; c.name = P + f"WingBone_thumb_{s}"; c.data.materials.append(CLAW)
    dirw = V((s * 0.3, -1, 0.4)).normalized()
    put(c, Matrix.Translation(W2L(W) + dirw * 0.045 * KW) @ dirw.to_track_quat('Z', 'Y').to_matrix().to_4x4())

# ---------------- rendus ----------------
cam = sc.camera; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
TAG = globals().get("TAG", "adulte")
def shot(name, tgt, d, dist):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
if globals().get("RENDER", True):
    hw = S @ HC
    shot(TAG + "_tete", hw + V((0, -0.4, -0.15)), (0.55, -1, 0.12), 8.5)
    shot(TAG + "_profil", (11.5, 2.0, 2.6), (1, -0.15, 0.12), 22)
    shot(TAG, (11.5, 1.0, 2.4), (0.6, -1, 0.3), 26)
