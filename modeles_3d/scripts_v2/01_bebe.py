# Dragon classique v2 (style Roblox) - stade BEBE + mise en place de la scene.
# A lancer dans une scene Blender vide.
# Style : formes rondes, couleurs unies et vives, gros yeux, pas de textures d'ecailles, peu de details.
# Identite commune aux 3 stades (a garder dans l'ado et l'adulte) :
#   rouge vif + ventre creme, marque en flamme jaune sur le front, cornes creme recourbees vers l'arriere,
#   crete orange, yeux ambre, ailes orange.
import bpy, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v2")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())

sc = bpy.context.scene; P = "Bebe_"
for o in [o for o in bpy.data.objects if o.name.startswith(P) or o.name in ("Cam", "Key", "Fill", "Rim", "Ground")]:
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------- scene ----------------
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 70
def light(name, loc, energy, size, color=(1, 1, 1)):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = color; L.size = size
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (V((0, 0, 0.7)) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
light("Key", (3, -4, 5), 405, 4); light("Fill", (-4, -2, 2.5), 140, 5, (0.85, 0.9, 1)); light("Rim", (-1, 4, 3.5), 260, 3)
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = (0.78, 0.84, 0.92, 1); bg.inputs[1].default_value = 0.7
bpy.ops.mesh.primitive_plane_add(size=80); g = bpy.context.object; g.name = "Ground"
gm = bpy.data.materials.get("Ground") or bpy.data.materials.new("Ground")
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1); g.data.materials.append(gm)
r = sc.render; r.engine = 'BLENDER_EEVEE'; r.resolution_x = 1200; r.resolution_y = 750
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Punchy'
except Exception: pass
coll = bpy.data.collections.get("Bebe") or bpy.data.collections.new("Bebe")
if coll.name not in sc.collection.children: sc.collection.children.link(coll)
def own(o):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); return o

# ---------------- corps (metaballs, meme silhouette que la v1) ----------------
K = 1.74
mb = bpy.data.metaballs.new("BebeMB"); mb.resolution = 0.03; mb.render_resolution = 0.03; mb.threshold = 0.6
def ell(co, rr, size=(1, 1, 1), st=2.0):
    e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = rr * K; e.size_x, e.size_y, e.size_z = size; e.stiffness = st
ell((0, 0.08, 0.56), 0.5, (0.95, 1.08, 0.92)); ell((0, -0.12, 0.45), 0.4, (0.9, 0.9, 0.95))
ell((0, -0.42, 1.3), 0.58, (1.1, 0.96, 0.92)); ell((0, -0.82, 1.13), 0.3, (1.05, 0.95, 0.72)); ell((0, -0.3, 1.0), 0.3)
for s in (-1, 1):
    ell((s * 0.3, -0.3, 0.3), 0.2, (0.85, 0.9, 1.15)); ell((s * 0.3, -0.38, 0.09), 0.17, (0.95, 1.25, 0.6))
    ell((s * 0.35, 0.3, 0.32), 0.28, (0.8, 0.95, 0.9)); ell((s * 0.37, 0.18, 0.09), 0.19, (0.95, 1.3, 0.6))
for x, y, z, rr in [(0, 0.6, 0.38, 0.22), (0.05, 0.8, 0.3, 0.18), (0.13, 0.98, 0.27, 0.15), (0.23, 1.13, 0.3, 0.12), (0.31, 1.25, 0.37, 0.1), (0.36, 1.33, 0.45, 0.085)]:
    ell((x, y, z), rr)
mo = bpy.data.objects.new("BebeMB", mb); sc.collection.objects.link(mo)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = mo; mo.select_set(True); bpy.context.view_layer.update()
bpy.ops.object.convert(target='MESH')
body = own(bpy.context.view_layer.objects.active); body.name = P + "Body"
for p in body.data.polygons: p.use_smooth = True
me = body.data

# ---------------- peau : zones de couleur calculees dans le materiau (bords nets a toute distance) ----------------
# Ventre, flamme du front et bout de queue sont calcules a partir de la position et de la normale.
# Pour Roblox, ce materiau sera cuit en texture image sur le modele allege.
HC = V((0, -0.42, 1.3))
# flamme en (longitude, latitude) autour du centre de la tete : 0,0 = face ; les yeux sont vers (+-0.35, 0.06)
# chaque langue : base ronde en a, pointe en b, rayon max
FLAMES = [((0, 0.36), (0, 1.35), 0.17), ((0.1, 0.42), (0.42, 1.05), 0.1), ((-0.1, 0.42), (-0.42, 1.05), 0.1)]

skin = new_mat("BebeSkin"); X = Nodes(skin)
tc = X.N.new("ShaderNodeTexCoord"); geo = X.N.new("ShaderNodeNewGeometry")
px, py, pz = X.sep(tc.outputs["Object"])[:3]
nx, ny, nz = X.sep(geo.outputs["Normal"])[:3]
# dos legerement plus fonce
c = X.mix(X.m('MULTIPLY', X.sstep(0.3, 1.0, nz), 0.3), rgba(PAL["RED"]), rgba(PAL["RED_DARK"]))
# ventre : face avant/dessous, bande centrale ; sous le museau : seulement le dessous
e = X.m('MULTIPLY_ADD', ny, -0.75, X.m('MULTIPLY', nz, -0.55))
bel = X.m('MULTIPLY', X.sstep(0.33, 0.38, e), X.inv(X.sstep(0.26, 0.285, X.m('ABSOLUTE', px))))
chest = X.inv(X.sstep(0.95, 1.03, pz)); under = X.sstep(0.38, 0.43, X.m('MULTIPLY', nz, -1.0))
wy = X.sstep(-0.75, -0.65, py)
bel = X.m('MULTIPLY', bel, X.m('ADD', X.m('MULTIPLY', chest, wy), X.m('MULTIPLY', under, X.inv(wy))))
bel = X.m('MULTIPLY', bel, X.sstep(0.26, 0.3, X.m('MULTIPLY_ADD', X.m('MULTIPLY', px, px), -3.0, pz)))   # bas du plastron en U
c = X.mix(bel, c, rgba(PAL["BELLY"]))
# flamme du front
c = X.mix(flamme(X, tc.outputs["Object"], HC, FLAMES, 1.0, HC.z - 0.15), c, rgba(PAL["FLAME"]))
# bout de queue
c = X.mix(X.sstep(1.12, 1.2, py), c, rgba(PAL["FLAME"]))
X.L.new(c, X.N["Principled BSDF"].inputs["Base Color"])
me.materials.append(skin)

def hit(origin, d):
    d = V(d).normalized(); h, l, n, _ = body.ray_cast(V(origin) + d * 3, -d); return l, n
def sphere(name, loc, scl, mm, q=None, seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = own(bpy.context.object); o.name = P + name; o.scale = scl; o.data.materials.append(mm)
    if q is not None: o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = q
    for pp in o.data.polygons: pp.use_smooth = True
    return o
def tube(name, pts, radii, mm, res=4):
    cu = bpy.data.curves.new(P + name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = res
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, pp, rr in zip(sp.bezier_points, pts, radii):
        bp.co = V(pp); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = rr
    o = bpy.data.objects.new(P + name, cu); coll.objects.link(o); cu.materials.append(mm)
    return o

# ---------------- yeux : gros, ambre, pupille ronde, deux reflets ----------------
DARK = mat("BebeDark", PAL["DARK"], 0.1); IRIS = mat("BebeIris", PAL["IRIS"], 0.1, emit=0.25)
HL = mat("BebeHL", (1, 1, 1), 0.2, emit=2.0, coat=0); LID = mat("BebeLid", PAL["RED"], 0.45)
for s in (-1, 1):
    l, n = hit(HC, (s * 0.34, -0.94, 0.06)); q = n.to_track_quat('-Y', 'Z')
    sphere(f"Eye_{s}", l - n * 0.03, (0.13, 0.05, 0.165), DARK, q, 24)                    # contour sombre fin
    sphere(f"EyeIris_{s}", l + q @ V((0, -0.014, -0.01)), (0.118, 0.014, 0.152), IRIS, q, 24)
    sphere(f"EyePupil_{s}", l + q @ V((0, -0.024, -0.012)), (0.05, 0.01, 0.085), DARK, q)
    sphere(f"EyeHL1_{s}", l + q @ V((-0.035, -0.032, 0.05)), (0.036, 0.008, 0.042), HL, q, 12)
    sphere(f"EyeHL2_{s}", l + q @ V((0.04, -0.032, -0.065)), (0.016, 0.006, 0.016), HL, q, 10)
    # paupiere : demi-sphere couleur peau qui couvre le haut de l'oeil, inclinee vers le nez
    lid = sphere(f"EyeLid_{s}", l + q @ V((0, 0.01, 0.135)) - n * 0.03, (0.165, 0.07, 0.08), LID, q, 20)
    lid.rotation_quaternion = q @ Matrix.Rotation(math.radians(-22 * s), 4, 'Y').to_quaternion()
    l2, n2 = hit((0, -0.82, 1.13), (s * 0.12, -1, -0.15))
    sphere(f"Nostril_{s}", l2 - n2 * 0.01, (0.024, 0.024, 0.018), DARK, n2.to_track_quat('-Y', 'Z'), 10)

# ---------------- bouche + petit croc (un seul, pour l'attitude) ----------------
mouth = []
for k in range(7):
    x = -0.17 + k * 0.34 / 6
    h_, l, n, _ = body.ray_cast(V((x, -2.0, 1.0 + 1.2 * x * x + 0.12 * max(0.0, x))), V((0, 1, 0)))
    if h_: mouth.append((l - n * 0.004, n))
tube("Mouth", [p for p, _ in mouth], [0.006, 0.011, 0.013, 0.013, 0.013, 0.011, 0.006][:len(mouth)], DARK)
HORN = mat("BebeHorn", PAL["HORN"], 0.35)
if len(mouth) >= 6:
    p, n = mouth[5]
    tube("Fang", [p + V((0, 0, 0.006)), p + V((0, -0.008, -0.03)), p + V((0, -0.01, -0.055))], [0.022, 0.014, 0.002], HORN)

# ---------------- cornes (meme forme que l'adulte, en petit), crete ----------------
for s in (-1, 1):
    l, n = hit(HC, (s * 0.45, 0.25, 0.85)); b = l - n * 0.04
    tube(f"Horn_{s}", [b, b + V((s * 0.04, 0.1, 0.12)), b + V((s * 0.07, 0.24, 0.15)), b + V((s * 0.07, 0.33, 0.22))], [0.08, 0.058, 0.032, 0.006], HORN)
SPIKE = mat("BebeSpike", PAL["SPIKE"], 0.4)
for i, (x, y, z) in enumerate([(0, -0.05, 1.0), (0, 0.15, 0.98), (0, 0.35, 0.88), (0, 0.58, 0.62), (0.1, 0.98, 0.42)]):
    l, n = hit((x, y, 0.5), (0, 0, 1)) if i < 4 else hit((x, y, 0.27), (0, 0.2, 1))
    hh = 0.14 if i in (1, 2) else 0.1
    tube(f"Spike_{i}", [l - n * 0.03, l + n * hh * 0.6 + V((0, 0.02, 0)), l + n * hh + V((0, 0.06, 0))], [0.075, 0.042, 0.006], SPIKE)

# ---------------- ailes : membrane orange + os rouges ----------------
WING = mat("BebeWing", PAL["WING"], 0.5); WBONE = mat("BebeWingBone", PAL["RED"], 0.45)
W2 = [(0, 0), (0.18, 0.2), (0.42, 0.36), (0.62, 0.42), (0.52, 0.24), (0.58, 0.08), (0.42, 0.1), (0.4, -0.06), (0.22, 0.0), (0.05, -0.04)]
for s in (-1, 1):
    cu = bpy.data.curves.new(P + f"Wing_{s}", 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = 0.012; cu.bevel_depth = 0.012; cu.bevel_resolution = 2; cu.resolution_u = 6
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(W2) - 1); sp.use_cyclic_u = True
    for bp, (x, y) in zip(sp.bezier_points, W2): bp.co = (x, y, 0); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    for i in (3, 5, 7): sp.bezier_points[i].handle_left_type = sp.bezier_points[i].handle_right_type = 'VECTOR'
    o = bpy.data.objects.new(P + f"Wing_{s}", cu); coll.objects.link(o); cu.materials.append(WING)
    u = V((s * 0.8, 0.5, 0.32)).normalized(); up = V((0, 0.45, 1.0)); v = (up - u * up.dot(u)).normalized(); ww = u.cross(v)
    R = Matrix((u, v, ww)).transposed()
    l, n = hit(V((s * 0.18, 0.1, 0.75)), (s * 0.45, 0.1, 1))
    M = Matrix.Translation(l - n * 0.06) @ R.to_4x4() @ Matrix.Diagonal((1.75, 1.75, 0.7, 1))
    o.matrix_world = M
    # os de l'aile : bord d'attaque + 2 doigts
    bo = tube(f"WingBone_{s}", [(0.0, 0.0, 0.0), (0.18, 0.2, 0.0), (0.42, 0.36, 0.0), (0.62, 0.42, 0.0)], [0.035, 0.03, 0.022, 0.006], WBONE)
    bo.matrix_world = M

# ---------------- bilan triangles (hors corps metaball, qui sera decime a l'export) ----------------
dg = bpy.context.evaluated_depsgraph_get(); TRIS = 0
for o in coll.objects:
    if o == body or o.type not in ('MESH', 'CURVE'): continue
    m = o.evaluated_get(dg).to_mesh(); m.calc_loop_triangles(); TRIS += len(m.loop_triangles); o.evaluated_get(dg).to_mesh_clear()
print("bebe v2 OK, triangles hors corps :", TRIS)

# ---------------- rendus ----------------
base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
TAG = globals().get("TAG", "v2_bebe")
def shot(name, tgt, d, dist, res=(1200, 750)):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    r.resolution_x, r.resolution_y = res
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
if globals().get("RENDER", True):
    shot(TAG, (0, -0.15, 0.8), (0.6, -1, 0.32), 7.5)
    shot(TAG + "_face", (0, -0.4, 1.0), (0.05, -1, 0.15), 6.5)
    r.resolution_x, r.resolution_y = 1200, 750
