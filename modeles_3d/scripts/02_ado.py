# Dragon classique - stade ADO. A executer dans Blender (scene avec le bebe deja presente).
import bpy, math
from mathutils import Vector as V, Matrix
sc = bpy.context.scene; P = "Ado_"
for o in [o for o in bpy.data.objects if o.name.startswith(P)]: bpy.data.objects.remove(o, do_unlink=True)
coll = bpy.data.collections.get("Ado") or bpy.data.collections.new("Ado")
if coll.name not in sc.collection.children: sc.collection.children.link(coll)
S = Matrix.Translation((5.0, 0, 0)) @ Matrix.Scale(1.15, 4)
def lin(c): return tuple(x ** 2.2 for x in c)
def sstep(a, b, x):
    t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def put(o, local=None):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)
    o.matrix_world = S @ (local if local is not None else o.matrix_world); return o

# ---------------- corps (metaballs) ----------------
K = 1.74
mb = bpy.data.metaballs.new("AdoMB"); mb.resolution = 0.03; mb.render_resolution = 0.03; mb.threshold = 0.6
def ell(co, r, size=(1, 1, 1), st=2.4):
    e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r * K
    e.size_x, e.size_y, e.size_z = size; e.stiffness = st
HO = V((0, -0.35, 0.61))                       # decalage de la tete (corps plus grand)
HC = V((0, -0.9, 2.05)) + HO; SN = V((0, -1.35, 1.9)) + HO
# --- tete (inchangee, juste deplacee) ---
ell(HC, 0.38, (0.92, 1.15, 0.74), 2.6)
ell(SN, 0.26, (0.82, 1.55, 0.6), 2.8)
for s in (-1, 1): ell(V((s * 0.075, -1.66, 1.88)) + HO, 0.12, (1, 1, 0.75), 3.0)
ell(V((0, -1.17, 1.74)) + HO, 0.21, (0.88, 1.45, 0.5), 2.8)
# --- tronc athletique (sureleve, taille fine) ---
ell((0, -0.25, 1.53), 0.47, (0.74, 0.98, 1.05), 2.8)     # poitrail en carene
ell((0, -0.55, 1.4), 0.3, (0.95, 0.7, 1.1), 2.4)        # torse avant plat
ell((0, 0.25, 1.5), 0.47, (0.7, 1.1, 0.85), 2.8)         # cotes
ell((0, 0.75, 1.42), 0.33, (0.6, 1.0, 0.72), 2.8)        # taille rentree
ell((0, 1.15, 1.45), 0.37, (0.72, 0.95, 0.82), 2.8)      # hanches serrees
NECK = [(0, -0.55, 1.83, 0.27), (0, -0.72, 2.08, 0.24), (0, -0.88, 2.32, 0.215), (0, -1.02, 2.5, 0.2), (0, -1.12, 2.61, 0.195)]
for x, y, z, r in NECK: ell((x, y, z), r, (1, 1, 1), 2.0)
CLAWS = []
def toe_chain(pts, rads, st=2.2, n=6):
    for i in range(len(pts) - 1):
        for k in range(n):
            t = k / n; ell(pts[i].lerp(pts[i + 1], t), (rads[i] + (rads[i + 1] - rads[i]) * t), (1, 1, 1), st)
    ell(pts[-1], rads[-1], (1, 1, 1), st)
def foot(cx, cy, s, size=1.0):
    """cheville -> metatarse -> petite paume -> 3 doigts separes + ergot."""
    c = V((cx, cy, 0.0)); z0 = 0.055 * size
    ell(c + V((0, -0.01, z0)), 0.085 * size, (1.25, 0.95, 0.55), 2.6)                 # paume
    for ang in (-34, 0, 34):
        a = math.radians(ang * s)
        d = V((math.sin(a), -math.cos(a), 0))
        b = c + d * 0.07 * size + V((0, 0, z0))
        pts = [b, b + d * 0.09 * size + V((0, 0, -0.012 * size)), b + d * 0.17 * size + V((0, 0, -0.024 * size)), b + d * 0.23 * size + V((0, 0, -0.028 * size))]
        toe_chain(pts, [0.046 * size, 0.04 * size, 0.035 * size, 0.03 * size], 2.6)
        for j in (1, 2): ell(pts[j], 0.046 * size, (1, 1, 0.85), 3.0)                # jointures
        CLAWS.append((pts[-1] + d * 0.015 * size, d, size))
    d = V((0.4 * s, 1, 0)).normalized()                                               # ergot
    p0 = c + d * 0.05 * size + V((0, 0, 0.09 * size))
    toe_chain([p0, p0 + d * 0.07 * size + V((0, 0, -0.02 * size))], [0.032 * size, 0.026 * size], 2.6, 4)
    CLAWS.append((p0 + d * 0.085 * size + V((0, 0, -0.02 * size)), d, size * 0.7))
for s in (-1, 1):
    ell((s * 0.28, -0.22, 1.86), 0.19, (0.8, 1.25, 0.6), 3.0)     # omoplates
    # membres continus : chaines interpolees (pas de perles)
    FRONT = [(s * 0.3, -0.3, 1.5, 0.24), (s * 0.38, -0.16, 1.2, 0.2), (s * 0.42, -0.02, 0.95, 0.14), (s * 0.43, -0.24, 0.62, 0.125), (s * 0.43, -0.46, 0.3, 0.095), (s * 0.43, -0.53, 0.2, 0.075), (s * 0.43, -0.6, 0.08, 0.07)]
    BACK = [(s * 0.3, 1.18, 1.38, 0.3), (s * 0.38, 0.95, 1.08, 0.23), (s * 0.43, 0.7, 0.8, 0.14), (s * 0.44, 1.0, 0.6, 0.115), (s * 0.44, 1.22, 0.42, 0.1), (s * 0.44, 1.12, 0.24, 0.08), (s * 0.44, 0.98, 0.09, 0.072)]
    for chain in (FRONT, BACK):
        for i in range(len(chain) - 1):
            A, B = chain[i], chain[i + 1]
            for k in range(5):
                t = k / 5; ell(tuple(A[j] + (B[j] - A[j]) * t for j in range(3)), (A[3] + (B[3] - A[3]) * t) * 0.95, (1, 1, 1), 2.0)
    ell((s * 0.38, -0.2, 1.24), 0.15, (0.8, 0.9, 1.3), 2.2)       # biceps
    ell((s * 0.43, -0.12, 0.8), 0.13, (0.85, 0.95, 1.5), 2.2)     # mollet avant
    ell((s * 0.36, 1.12, 1.12), 0.2, (0.7, 1.0, 1.2), 2.2)        # ischio (leger)
    foot(s * 0.43, -0.64, s, 1.0)                                  # patte avant
    foot(s * 0.44, 0.94, s, 1.08)                                   # patte arriere
FEET = [(0.43, -0.63), (0.44, 0.92)]
TAILC = [(0, 1.5, 1.36, 0.27), (0.05, 2.0, 1.0, 0.2), (0.2, 2.55, 0.7, 0.15), (0.42, 3.05, 0.55, 0.105), (0.64, 3.5, 0.55, 0.075), (0.78, 3.82, 0.62, 0.055)]
def lerp(a, b, t): return a + (b - a) * t
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
SKIN = V(lin((0.86, 0.22, 0.15))); BELLY = V(lin((1.0, 0.82, 0.52)))
col = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT'); msk = me.color_attributes.new("Mask", 'FLOAT_COLOR', 'POINT')
for v in me.vertices:
    p = v.co; n = v.normal
    bb = sstep(0.15, 0.55, -n.y * 0.7 - n.z * 0.6) * (1 - sstep(0.18, 0.34, abs(p.x)))
    bh = sstep(0.25, 0.65, -n.z) * (1 - sstep(0.12, 0.26, abs(p.x)))
    hw = 1 - sstep(0.5, 0.85, min((p - HC).length, (p - SN).length + 0.05))
    bel = bb * (1 - hw) + bh * hw
    if p.z < 0.12: bel = 0
    c = SKIN.lerp(BELLY, bel); col.data[v.index].color = (*c, 1)
    m = (1 - bel) * (1 - 0.6 * (1 - sstep(0.25, 0.45, (p - SN).length)))
    msk.data[v.index].color = (m, m, m, 1)
base_m = bpy.data.materials["DragonSkin"]
am = bpy.data.materials.get("DragonSkinAdo")
if am: bpy.data.materials.remove(am)
am = base_m.copy(); am.name = "DragonSkinAdo"
an = am.node_tree.nodes; al = am.node_tree.links
bump = [x for x in an if x.type == 'BUMP'][0]
mk = [x for x in an if x.type == 'VERTEX_COLOR' and x.layer_name == "Mask"][0]
tco = an.new("ShaderNodeTexCoord")
wav = an.new("ShaderNodeTexWave"); wav.wave_type = 'BANDS'; wav.bands_direction = 'Z'; wav.wave_profile = 'SAW'
wav.inputs["Scale"].default_value = 3.2; wav.inputs["Distortion"].default_value = 0.0
al.new(tco.outputs["Object"], wav.inputs["Vector"])
inv = an.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
al.new(mk.outputs["Color"], inv.inputs[1])
pl = an.new("ShaderNodeMath"); pl.operation = 'MULTIPLY'
al.new(wav.outputs["Fac"], pl.inputs[0]); al.new(inv.outputs[0], pl.inputs[1])
old = bump.inputs["Height"].links[0].from_socket
addh = an.new("ShaderNodeMath"); addh.operation = 'MULTIPLY_ADD'; addh.inputs[1].default_value = 0.6
al.new(pl.outputs[0], addh.inputs[0]); al.new(old, addh.inputs[2]); al.new(addh.outputs[0], bump.inputs["Height"])
me.materials.append(am)
def hit(origin, d):
    d = V(d).normalized(); h, l, n, _ = body.ray_cast(V(origin) + d * 4, -d); return l, n
put(body, body.matrix_world.copy())

HORN = bpy.data.materials["Horn"]; SPIKE = bpy.data.materials["Spike"]; PUP = bpy.data.materials["Eye"]; HL = bpy.data.materials["Highlight"]
def tube(name, pts, radii, mm):
    cu = bpy.data.curves.new(P + name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 12
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 5; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, pp, r in zip(sp.bezier_points, pts, radii):
        bp.co = V(pp); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r
    o = bpy.data.objects.new(P + name, cu); cu.materials.append(mm); sc.collection.objects.link(o); return put(o, Matrix())

# ---------------- iris lumineux : degrade radial dans le plan de l'oeil ----------------
iris = bpy.data.materials.get("AdoIrisGlow") or bpy.data.materials.new("AdoIrisGlow")
nt = iris.node_tree; N = nt.nodes; L = nt.links
for x in list(N):
    if x.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL'): N.remove(x)
bs = N["Principled BSDF"]; bs.inputs["Roughness"].default_value = 0.05
tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
cmb = N.new("ShaderNodeCombineXYZ"); L.new(sep.outputs["X"], cmb.inputs["X"]); L.new(sep.outputs["Z"], cmb.inputs["Y"])
ln = N.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'; L.new(cmb.outputs[0], ln.inputs[0])
cr = N.new("ShaderNodeValToRGB"); L.new(ln.outputs["Value"], cr.inputs["Fac"])
e = cr.color_ramp.elements
e[0].position = 0.0; e[0].color = (*lin((1.0, 0.97, 0.45)), 1)
e[1].position = 0.95; e[1].color = (*lin((0.45, 0.04, 0.0)), 1)
m = e.new(0.45); m.color = (*lin((1.0, 0.62, 0.05)), 1)
m2 = e.new(0.78); m2.color = (*lin((0.9, 0.25, 0.02)), 1)
L.new(cr.outputs["Color"], bs.inputs["Base Color"]); L.new(cr.outputs["Color"], bs.inputs["Emission Color"])
bs.inputs["Emission Strength"].default_value = 0.9
brow = bpy.data.materials.get("AdoLid") or bpy.data.materials.new("AdoLid")
brow.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin((0.8, 0.19, 0.13)), 1)

def lemon(name, loc, q, w, h, dep, mm, sharp=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1)
    o = bpy.context.object; o.name = P + name; o.data.materials.append(mm)
    for v in o.data.vertices:
        x = v.co.x; v.co.z *= max(0.0, 1 - x * x) ** (0.5 * sharp)
    for pp in o.data.polygons: pp.use_smooth = True
    return put(o, Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((w, dep, h, 1)))

def face_quat(n, tilt_deg, s):
    """axe -Y local = normale, X local = horizontal vers l'exterieur, puis inclinaison."""
    up = V((0, 0, 1)); z = (up - n * up.dot(n)).normalized()
    y = -n; x = y.cross(z)
    q = Matrix((x, y, z)).transposed().to_quaternion()
    return q @ Matrix.Rotation(math.radians(tilt_deg * s), 4, 'Y').to_quaternion()

for s in (-1, 1):
    d = V((s * 0.5, -0.82, 0.12)).normalized(); l, n = hit(HC, d)
    q = face_quat(n, -16, s)          # coin exterieur releve
    lemon(f"Eye_{s}", l - n * 0.035, q, 0.15, 0.085, 0.06, iris, 1.2)
    lemon(f"EyePupil_{s}", l + n * 0.02, q, 0.016, 0.075, 0.01, PUP, 1.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1); o = bpy.context.object; o.name = P + f"EyeHL_{s}"; o.data.materials.append(HL)
    for pp in o.data.polygons: pp.use_smooth = True
    put(o, Matrix.Translation(l + n * 0.024 + q @ V((-0.05, 0, 0.025))) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((0.016, 0.006, 0.016, 1)))
    qb = face_quat(n, -24, s)         # arcade qui descend vers le museau
    lemon(f"EyeBrow_{s}", l - n * 0.035 + qb @ V((0.0, 0, 0.08)), qb, 0.18, 0.04, 0.045, brow, 1.6)
    l2, n2 = hit(V((s * 0.075, -1.66, 1.88)) + HO, V((s * 0.3, -1, 0.35)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1); o = bpy.context.object; o.name = P + f"Nostril_{s}"; o.data.materials.append(PUP)
    put(o, Matrix.Translation(l2 - n2 * 0.012) @ n2.to_track_quat('-Y', 'Z').to_matrix().to_4x4() @ Matrix.Diagonal((0.035, 0.02, 0.016, 1)))


# ---------------- bouche : ligne en rictus + crocs ----------------
lipm = bpy.data.materials.get("AdoLip") or bpy.data.materials.new("AdoLip")
lipm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin((0.18, 0.02, 0.03)), 1)
for s in (-1, 1):
    pts = []
    ys = [-1.76, -1.66, -1.5, -1.34, -1.18, -1.04, -0.96]
    zs = [1.78, 1.77, 1.775, 1.785, 1.8, 1.84, 1.9]
    for y, z in zip(ys, zs):
        h_, l, n, _ = body.ray_cast(V((s * 1.5, y, z)) + HO, V((-s, 0, 0)))
        if not h_:
            h_, l, n, _ = body.ray_cast(V((0, -2.5, z)) + HO, V((0, 1, 0)))
        pts.append((l - n * 0.006, n))
    tube(f"Mouth_{s}", [p for p, _ in pts], [0.012, 0.018, 0.02, 0.02, 0.019, 0.016, 0.006], lipm)
    for i, (dz, ln) in ((1, (-1, 0.1)), (3, (-1, 0.075)), (2, (1, 0.07))):
        p, n = pts[i]
        b = p + V((0, 0, -0.01 if dz < 0 else 0.01)) - n * 0.01
        tube(f"Fang_{s}_{i}", [b, b + V((0, -0.01, dz * ln * 0.5)) + n * 0.012, b + V((0, -0.02, dz * ln))], [0.022, 0.014, 0.002], HORN)

for s in (-1, 1):
    l, n = hit(HC, (s * 0.4, 0.4, 0.8)); b = l - n * 0.05
    tube(f"Horn_{s}", [b, b + V((s * 0.05, 0.28, 0.12)), b + V((s * 0.08, 0.6, 0.16)), b + V((s * 0.09, 0.86, 0.26))], [0.08, 0.06, 0.03, 0.004], HORN)
    for k, (dz, lg) in enumerate(((0.05, 0.32), (-0.1, 0.24))):
        l, n = hit(V((0, -0.95, 1.82)) + HO, (s * 1, 0.35, dz)); b = l - n * 0.03
        tube(f"Cheek_{s}_{k}", [b, b + V((s * 0.1, lg * 0.5, 0.0)), b + V((s * 0.13, lg, 0.04))], [0.045, 0.025, 0.003], HORN)
SPY = [-1.0, -0.8, -0.58, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.55, 1.95, 2.35, 2.75, 3.15, 3.5]
for i, y in enumerate(SPY):
    l, n = hit((tail_x(y), y, 0.5), (0, 0, 1)); h = 0.22 if 3 <= i <= 9 else 0.14
    tube(f"Spike_{i}", [l - n * 0.04, l + n * h * 0.5 + V((0, 0.05, 0)), l + n * h + V((0, 0.13, 0))], [0.065, 0.032, 0.002], SPIKE)
e2 = V(TAILC[-1][:3]); dd = (e2 - V(TAILC[-2][:3])).normalized()
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.15, radius2=0, depth=0.32)
o = bpy.context.object; o.name = P + "TailTip"; o.data.materials.append(SPIKE)
put(o, Matrix.Translation(e2 + dd * 0.12) @ dd.to_track_quat('Z', 'Y').to_matrix().to_4x4() @ Matrix.Diagonal((1, 0.3, 1, 1)))
for i, (tip, d, sz) in enumerate(CLAWS):
    tube(f"Claw_{i}", [tip - d * 0.025 * sz, tip + d * 0.045 * sz + V((0, 0, 0.004)), tip + d * 0.09 * sz + V((0, 0, -0.03 * sz))], [0.028 * sz, 0.017 * sz, 0.002], HORN)
for s in (-1, 1):
    src = bpy.data.objects[f"Wing_{s}"]; o = src.copy(); o.data = src.data.copy(); o.name = P + f"Wing_{s}"; sc.collection.objects.link(o)
    u = V((s * 0.8, 0.55, 0.35)).normalized(); up = V((0, 0.45, 1.0)); v = (up - u * up.dot(u)).normalized(); w = u.cross(v)
    R = Matrix((u, v, w)).transposed()
    l, n = hit(V((s * 0.25, -0.15, 1.8)), (s * 0.45, 0.1, 1))
    put(o, Matrix.Translation(l - n * 0.07) @ R.to_4x4() @ Matrix.Diagonal((3.0, 3.0, 0.75, 1)))

# ---------------- rendus ----------------
cam = sc.camera; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
TAG = globals().get("TAG", "ado")
def shot(name, tgt, d, dist):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
hw = S @ HC
shot(TAG + "_tete", hw + V((0, -0.3, -0.1)), (0.55, -1, 0.12), 6.5)
shot(TAG + "_profil", (5.0, 1.4, 1.9), (1, -0.15, 0.12), 15)
shot(TAG + "_pattes", (5.0 + 0.45 * 1.15, -0.6 * 1.15, 0.3), (0.8, -1, 0.45), 3.2)
shot(TAG, (2.6, 0.8, 1.5), (0.6, -1, 0.3), 23)
