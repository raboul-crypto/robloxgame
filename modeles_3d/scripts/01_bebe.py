# Dragon classique - stade BEBE (+ mise en place de la scene : camera, lumieres, sol, materiaux de base).
# A lancer en premier dans une scene Blender vide. Les scripts de l'ado reutilisent ses materiaux et ses ailes.
import bpy, math
from mathutils import Vector as V, Matrix, Euler

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def lin(c): return tuple(x ** 2.2 for x in c)
def sstep(a, b, x):
    t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)
def sel(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

# ---------------- scene ----------------
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 70
def light(name, loc, energy, size, color=(1, 1, 1)):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = color; L.size = size
    o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (V((0, 0, 0.7)) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
light("Key", (3, -4, 5), 405, 4); light("Fill", (-4, -2, 2.5), 112, 5, (0.85, 0.9, 1)); light("Rim", (-1, 4, 3.5), 225, 3)
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = (0.78, 0.84, 0.92, 1); bg.inputs[1].default_value = 0.6
bpy.ops.mesh.primitive_plane_add(size=30); g = bpy.context.object; g.name = "Ground"
gm = bpy.data.materials.new("Ground"); gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1)
g.data.materials.append(gm)
r = sc.render; r.engine = 'BLENDER_EEVEE'; r.resolution_x = 1200; r.resolution_y = 750
sc.view_settings.view_transform = 'AgX'

# ---------------- corps (metaballs fondues en un seul maillage) ----------------
K = 1.74
mb = bpy.data.metaballs.new("BodyMB"); mb.resolution = 0.03; mb.render_resolution = 0.03; mb.threshold = 0.6
def ell(co, rr, size=(1, 1, 1), st=2.0):
    e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = rr * K; e.size_x, e.size_y, e.size_z = size; e.stiffness = st
ell((0, 0.08, 0.56), 0.5, (0.95, 1.08, 0.92)); ell((0, -0.12, 0.45), 0.4, (0.9, 0.9, 0.95))
ell((0, -0.42, 1.3), 0.56, (1.08, 0.95, 0.9)); ell((0, -0.82, 1.13), 0.3, (1.05, 0.95, 0.72)); ell((0, -0.3, 1.0), 0.3)
for s in (-1, 1):
    ell((s * 0.3, -0.3, 0.3), 0.2, (0.85, 0.9, 1.15)); ell((s * 0.3, -0.38, 0.09), 0.16, (0.95, 1.25, 0.6))
    ell((s * 0.35, 0.3, 0.32), 0.28, (0.8, 0.95, 0.9)); ell((s * 0.37, 0.18, 0.09), 0.18, (0.95, 1.3, 0.6))
for x, y, z, rr in [(0, 0.6, 0.38, 0.22), (0.05, 0.8, 0.3, 0.18), (0.13, 0.98, 0.27, 0.14), (0.23, 1.13, 0.3, 0.11), (0.31, 1.25, 0.37, 0.085), (0.36, 1.33, 0.45, 0.065)]:
    ell((x, y, z), rr)
mo = bpy.data.objects.new("BodyMB", mb); sc.collection.objects.link(mo)
sel([mo]); bpy.context.view_layer.update(); bpy.ops.object.convert(target='MESH')
body = bpy.context.view_layer.objects.active; body.name = "Body"
for p in body.data.polygons: p.use_smooth = True
me = body.data

# couleurs (attribut "Col") + masque d'ecailles (attribut "Mask")
SKIN = V(lin((0.93, 0.33, 0.22))); BELLY = V(lin((1.0, 0.86, 0.6))); BLUSH = V(lin((1.0, 0.5, 0.55)))
cheeks = [V((s * 0.43, -0.86, 1.12)) for s in (-1, 1)]
col = me.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT'); mask = me.color_attributes.new("Mask", 'FLOAT_COLOR', 'POINT')
for v in me.vertices:
    p = v.co; n = v.normal
    bel = sstep(0.15, 0.55, -n.y * 0.75 - n.z * 0.55) * (1 - sstep(0.22, 0.42, abs(p.x)))
    bel *= (1 - sstep(0.95, 1.05, p.z)) if p.y > -0.7 else sstep(0.2, 0.6, -n.z)
    if p.z < 0.14: bel = 0
    c = SKIN.lerp(BELLY, bel)
    for ch in cheeks: c = c.lerp(BLUSH, 0.75 * (1 - sstep(0.06, 0.16, (p - ch).length)))
    col.data[v.index].color = (*c, 1)
    face = sstep(0.0, 0.15, -(p.y + 0.6)) * sstep(0.9, 1.0, p.z)
    m = max(0, 1 - bel) * (1 - 0.85 * face); mask.data[v.index].color = (m, m, m, 1)

# materiau "DragonSkin" (couleurs + ecailles en relief) - base reutilisee par l'ado
m = bpy.data.materials.new("DragonSkin"); nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
ca = N.new("ShaderNodeVertexColor"); ca.layer_name = "Col"
b.inputs["Roughness"].default_value = 0.42; b.inputs["Subsurface Weight"].default_value = 0.15
tc = N.new("ShaderNodeTexCoord"); vor = N.new("ShaderNodeTexVoronoi"); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs["Scale"].default_value = 11
L.new(tc.outputs["Object"], vor.inputs["Vector"])
rmp = N.new("ShaderNodeMapRange"); rmp.inputs["From Max"].default_value = 0.08; L.new(vor.outputs["Distance"], rmp.inputs["Value"])
mk = N.new("ShaderNodeVertexColor"); mk.layer_name = "Mask"
inv = N.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(rmp.outputs["Result"], inv.inputs[1])
mul = N.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; L.new(inv.outputs[0], mul.inputs[0]); L.new(mk.outputs["Color"], mul.inputs[1])
fl = N.new("ShaderNodeMath"); fl.operation = 'MULTIPLY'; fl.inputs[1].default_value = -1; L.new(mul.outputs[0], fl.inputs[0])
bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.18; bump.inputs["Distance"].default_value = 0.02
L.new(fl.outputs[0], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs["B"].default_value = (0.8, 0.7, 0.7, 1)
L.new(mul.outputs[0], mix.inputs["Factor"]); L.new(ca.outputs["Color"], mix.inputs["A"]); L.new(mix.outputs["Result"], b.inputs["Base Color"])
me.materials.append(m)

def mat(name, c, rough=0.4, emit=0):
    mm = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    bb = mm.node_tree.nodes["Principled BSDF"]; bb.inputs["Base Color"].default_value = (*lin(c), 1); bb.inputs["Roughness"].default_value = rough
    if emit: bb.inputs["Emission Color"].default_value = (1, 1, 1, 1); bb.inputs["Emission Strength"].default_value = emit
    return mm
EYE = mat("Eye", (0.06, 0.04, 0.05), 0.05); IRIS = mat("Iris", (0.55, 0.28, 0.12), 0.08); HL = mat("Highlight", (1, 1, 1), 0.2, 2.0)
HORN = mat("Horn", (1, 0.93, 0.78), 0.35); SPIKE = mat("Spike", (1, 0.78, 0.4), 0.4); WING = mat("WingMembrane", (1, 0.66, 0.32), 0.5)
def sphere(name, loc, scl, mm, q=None, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scl; o.data.materials.append(mm)
    if q is not None: o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = q
    for p in o.data.polygons: p.use_smooth = True
    return o
def tube(name, pts, radii, mm):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 12
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 6; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p, rr in zip(sp.bezier_points, pts, radii): bp.co = V(p); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = rr
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); cu.materials.append(mm); return o
def hit(origin, d):
    d = V(d).normalized(); h, l, n, _ = body.ray_cast(V(origin) + d * 3, -d); return l, n

# ---------------- yeux (encastres, grands et brillants) ----------------
hc = V((0, -0.42, 1.3))
for s in (-1, 1):
    l, n = hit(hc, (s * 0.33, -0.94, 0.06)); q = n.to_track_quat('-Y', 'Z')
    sphere(f"Eye_{s}", l - n * 0.035, (0.12, 0.05, 0.155), EYE, q)
    sphere(f"EyeIris_{s}", l + q @ V((0, -0.012, -0.045)), (0.085, 0.012, 0.09), IRIS, q)
    sphere(f"EyeHL1_{s}", l + q @ V((-0.035, -0.02, 0.055)), (0.04, 0.008, 0.045), HL, q)
    sphere(f"EyeHL2_{s}", l + q @ V((0.035, -0.02, -0.06)), (0.018, 0.006, 0.018), HL, q)
    l2, n2 = hit((0, -0.82, 1.13), (s * 0.12, -1, -0.15))
    sphere(f"EyeNostril_{s}", l2 - n2 * 0.01, (0.025, 0.025, 0.02), EYE, n2.to_track_quat('-Y', 'Z'), 12)
# ---------------- cornes, pics, griffes ----------------
for s in (-1, 1):
    l, n = hit(hc, (s * 0.45, 0.25, 0.85)); b_ = l - n * 0.04
    tube(f"Horn_{s}", [b_, b_ + V((s * 0.05, 0.1, 0.13)), b_ + V((s * 0.08, 0.24, 0.18))], [0.07, 0.05, 0.008], HORN)
for i, (x, y, z) in enumerate([(0, -0.05, 1.0), (0, 0.15, 0.98), (0, 0.35, 0.88), (0, 0.58, 0.62), (0.1, 0.98, 0.42)]):
    l, n = hit((x, y, 0.5), (0, 0, 1)) if i < 4 else hit((x, y, 0.27), (0, 0.2, 1))
    hh = 0.13 if i in (1, 2) else 0.09
    tube(f"Spike_{i}", [l - n * 0.03, l + n * hh * 0.6 + V((0, 0.02, 0)), l + n * hh + V((0, 0.05, 0))], [0.07, 0.04, 0.006], SPIKE)
for s in (-1, 1):
    for fx, fy in ((0.3, -0.38), (0.37, 0.18)):
        for k in (-1, 0, 1):
            h, l, n, _ = body.ray_cast(V((s * fx, fy, 0.06)), V((k * 0.45, -1, -0.05)).normalized())
            sphere(f"Claw_{s}_{fy}_{k}", l + V((0, -0.012, -0.01)), (0.032, 0.05, 0.026), HORN, V((k * 0.3, -1, -0.25)).normalized().to_track_quat('Y', 'Z'), 16)
# ---------------- ailes (contour lisse rempli, orientees vers l'arriere) ----------------
W2 = [(0, 0), (0.18, 0.2), (0.42, 0.36), (0.62, 0.42), (0.52, 0.24), (0.58, 0.08), (0.42, 0.1), (0.4, -0.06), (0.22, 0.0), (0.05, -0.04)]
for s in (-1, 1):
    cu = bpy.data.curves.new(f"Wing_{s}", 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = 0.012; cu.bevel_depth = 0.012; cu.bevel_resolution = 4; cu.resolution_u = 10
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(W2) - 1); sp.use_cyclic_u = True
    for bp, (x, y) in zip(sp.bezier_points, W2): bp.co = (x, y, 0); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    for i in (3, 5, 7): sp.bezier_points[i].handle_left_type = sp.bezier_points[i].handle_right_type = 'VECTOR'
    o = bpy.data.objects.new(f"Wing_{s}", cu); sc.collection.objects.link(o); cu.materials.append(WING)
    u = V((s * 0.8, 0.5, 0.32)).normalized(); up = V((0, 0.45, 1.0)); v = (up - u * up.dot(u)).normalized(); ww = u.cross(v)
    R = Matrix((u, v, ww)).transposed()
    l, n = hit(V((s * 0.18, 0.1, 0.75)), (s * 0.45, 0.1, 1))
    o.matrix_world = Matrix.Translation(l - n * 0.06) @ R.to_4x4() @ Matrix.Diagonal((1.75, 1.75, 0.7, 1))
print("bebe OK")
