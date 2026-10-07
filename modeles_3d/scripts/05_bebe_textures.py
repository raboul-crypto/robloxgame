# Textures realistes "douces" pour le BEBE
import bpy, math
from mathutils import Vector as V, Matrix
sc = bpy.context.scene
def lin(c): return tuple(x ** 2.2 for x in c)
def newmat(name):
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name); nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL'): nt.nodes.remove(n)
    return m, nt.nodes, nt.links, nt.nodes["Principled BSDF"]
def mnode(N, L, op, a=None, b=None, va=None, vb=None):
    n = N.new("ShaderNodeMath"); n.operation = op
    if a is not None: L.new(a, n.inputs[0])
    elif va is not None: n.inputs[0].default_value = va
    if b is not None: L.new(b, n.inputs[1])
    elif vb is not None: n.inputs[1].default_value = vb
    return n.outputs[0]
def mr(N, L, x, a, b, c=0.0, d=1.0):
    n = N.new("ShaderNodeMapRange"); L.new(x, n.inputs["Value"])
    n.inputs["From Min"].default_value = a; n.inputs["From Max"].default_value = b
    n.inputs["To Min"].default_value = c; n.inputs["To Max"].default_value = d; return n.outputs["Result"]
def mix(N, L, f, a, b, mode='MIX'):
    n = N.new("ShaderNodeMix"); n.data_type = 'RGBA'; n.blend_type = mode
    if isinstance(f, float): n.inputs["Factor"].default_value = f
    else: L.new(f, n.inputs["Factor"])
    for s_, v in (("A", a), ("B", b)):
        if isinstance(v, tuple): n.inputs[s_].default_value = v
        else: L.new(v, n.inputs[s_])
    return n.outputs["Result"]

# ---------- peau ----------
m, N, L, B = newmat("BebeSkinReal")
col = N.new("ShaderNodeVertexColor"); col.layer_name = "Col"
mk_ = N.new("ShaderNodeVertexColor"); mk_.layer_name = "Mask"
sp = N.new("ShaderNodeSeparateColor"); L.new(mk_.outputs["Color"], sp.inputs[0]); mask = sp.outputs[0]
tc = N.new("ShaderNodeTexCoord")
v1 = N.new("ShaderNodeTexVoronoi"); v1.inputs["Scale"].default_value = 13; L.new(tc.outputs["Object"], v1.inputs["Vector"])
v2 = N.new("ShaderNodeTexVoronoi"); v2.feature = 'DISTANCE_TO_EDGE'; v2.inputs["Scale"].default_value = 13; L.new(tc.outputs["Object"], v2.inputs["Vector"])
edge = mr(N, L, v2.outputs["Distance"], 0.0, 0.12); dome = mnode(N, L, 'POWER', edge, vb=0.6)
cs = N.new("ShaderNodeSeparateColor"); L.new(v1.outputs["Color"], cs.inputs[0])
var = mr(N, L, cs.outputs[0], 0, 1, 0.88, 1.08)
vc = N.new("ShaderNodeCombineColor"); [L.new(var, vc.inputs[i]) for i in range(3)]
c1 = mix(N, L, mask, col.outputs["Color"], mix(N, L, 1.0, col.outputs["Color"], vc.outputs[0], 'MULTIPLY'))
crev = mnode(N, L, 'MULTIPLY', mnode(N, L, 'SUBTRACT', va=1.0, b=dome), mask)
c2 = mix(N, L, mnode(N, L, 'MULTIPLY', crev, vb=0.6), c1, mix(N, L, 1.0, c1, (0.45, 0.22, 0.2, 1), 'MULTIPLY'))
wav = N.new("ShaderNodeTexWave"); wav.wave_type = 'BANDS'; wav.bands_direction = 'Z'; wav.inputs["Scale"].default_value = 4.5; wav.inputs["Distortion"].default_value = 0
L.new(tc.outputs["Object"], wav.inputs["Vector"])
groove = mr(N, L, wav.outputs["Fac"], 0.0, 0.2, 1.0, 0.0)
cc = N.new("ShaderNodeSeparateColor"); L.new(col.outputs["Color"], cc.inputs[0])
belly = mr(N, L, cc.outputs[1], 0.3, 0.6)            # zone creme uniquement (vert eleve, exclut les joues roses)
gb = mnode(N, L, 'MULTIPLY', mnode(N, L, 'MULTIPLY', groove, belly), vb=0.5)
c3 = mix(N, L, gb, c2, mix(N, L, 1.0, c2, (0.7, 0.55, 0.45, 1), 'MULTIPLY'))
L.new(c3, B.inputs["Base Color"])
h = mnode(N, L, 'ADD', mnode(N, L, 'MULTIPLY', dome, mask), mnode(N, L, 'MULTIPLY', mnode(N, L, 'SUBTRACT', va=1.0, b=groove), belly))
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.28; bp.inputs["Distance"].default_value = 0.02
L.new(h, bp.inputs["Height"]); L.new(bp.outputs["Normal"], B.inputs["Normal"])
L.new(mr(N, L, dome, 0, 1, 0.6, 0.38), B.inputs["Roughness"])
B.inputs["Subsurface Weight"].default_value = 0.15; B.inputs["Subsurface Radius"].default_value = (0.3, 0.1, 0.05)
B.inputs["Coat Weight"].default_value = 0.1
body = bpy.data.objects["Body"]; body.data.materials.clear(); body.data.materials.append(m)

# ---------- keratine claire ----------
def keratin(name, c0, c1_, c2_):
    m, N, L, B = newmat(name)
    tc = N.new("ShaderNodeTexCoord"); s = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], s.inputs[0])
    t = mnode(N, L, 'MULTIPLY', mnode(N, L, 'ADD', s.outputs["Y"], s.outputs["Z"]), vb=0.5)
    cr = N.new("ShaderNodeValToRGB"); L.new(t, cr.inputs["Fac"]); e = cr.color_ramp.elements
    e[0].position = 0.1; e[0].color = (*lin(c0), 1); e[1].position = 0.95; e[1].color = (*lin(c2_), 1); x = e.new(0.5); x.color = (*lin(c1_), 1)
    L.new(cr.outputs["Color"], B.inputs["Base Color"])
    rg = N.new("ShaderNodeMath"); rg.operation = 'SINE'; L.new(mnode(N, L, 'MULTIPLY', t, vb=40.0), rg.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; L.new(rg.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], B.inputs["Normal"])
    B.inputs["Roughness"].default_value = 0.35; B.inputs["Coat Weight"].default_value = 0.35
    return m
HB = keratin("BebeHorn", (0.78, 0.62, 0.46), (0.93, 0.85, 0.7), (1.0, 0.97, 0.9))
SB = keratin("BebeSpike", (0.85, 0.35, 0.15), (1.0, 0.62, 0.3), (1.0, 0.86, 0.55))
CB = keratin("BebeClaw", (0.8, 0.68, 0.55), (0.9, 0.84, 0.74), (0.98, 0.95, 0.88))
for o in bpy.data.objects:
    if o.name.startswith("Ado_") or o.type not in ('MESH', 'CURVE'): continue
    t = None
    if o.name.startswith("Horn"): t = HB
    elif o.name.startswith("Spike"): t = SB
    elif o.name.startswith("Claw"): t = CB
    if t: o.data.materials.clear(); o.data.materials.append(t)

# ---------- yeux (iris brun strie + reflet humide) ----------
ir = bpy.data.materials["Iris"]; N = ir.node_tree.nodes; L = ir.node_tree.links; B = N["Principled BSDF"]
for x in list(N):
    if x.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL'): N.remove(x)
tc = N.new("ShaderNodeTexCoord"); se = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], se.inputs[0])
ang = mnode(N, L, 'ARCTAN2', se.outputs["Z"], se.outputs["X"])
cb = N.new("ShaderNodeCombineXYZ"); L.new(se.outputs["X"], cb.inputs["X"]); L.new(se.outputs["Z"], cb.inputs["Y"])
ln = N.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'; L.new(cb.outputs[0], ln.inputs[0])
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = '2D'; nz.inputs["Scale"].default_value = 3
cv = N.new("ShaderNodeCombineXYZ"); L.new(mnode(N, L, 'MULTIPLY', ang, vb=6.0), cv.inputs["X"]); L.new(ln.outputs["Value"], cv.inputs["Y"]); L.new(cv.outputs[0], nz.inputs["Vector"])
cr = N.new("ShaderNodeValToRGB"); L.new(ln.outputs["Value"], cr.inputs["Fac"]); e = cr.color_ramp.elements
e[0].position = 0.0; e[0].color = (*lin((0.95, 0.68, 0.3)), 1); e[1].position = 0.95; e[1].color = (*lin((0.2, 0.08, 0.03)), 1)
x = e.new(0.55); x.color = (*lin((0.6, 0.28, 0.1)), 1)
st = mr(N, L, nz.outputs["Fac"], 0.3, 0.7, 0.7, 1.15); sc_ = N.new("ShaderNodeCombineColor"); [L.new(st, sc_.inputs[i]) for i in range(3)]
L.new(mix(N, L, 1.0, cr.outputs["Color"], sc_.outputs[0], 'MULTIPLY'), B.inputs["Base Color"])
B.inputs["Roughness"].default_value = 0.2; B.inputs["Coat Weight"].default_value = 1.0; B.inputs["Coat Roughness"].default_value = 0.02
eye = bpy.data.materials["Eye"].node_tree.nodes["Principled BSDF"]; eye.inputs["Coat Weight"].default_value = 1.0; eye.inputs["Coat Roughness"].default_value = 0.02

# ---------- ailes ----------
m, N, L, B = newmat("BebeWingReal")
tc = N.new("ShaderNodeTexCoord")
vn = N.new("ShaderNodeTexVoronoi"); vn.feature = 'DISTANCE_TO_EDGE'; vn.inputs["Scale"].default_value = 6
mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 2.2, 1.0); L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], vn.inputs["Vector"])
vein = mr(N, L, vn.outputs["Distance"], 0.0, 0.025, 1.0, 0.0)
wc = mix(N, L, mnode(N, L, 'MULTIPLY', vein, vb=0.7), (*lin((1.0, 0.55, 0.28)), 1), (*lin((0.8, 0.28, 0.14)), 1))
L.new(wc, B.inputs["Base Color"]); B.inputs["Roughness"].default_value = 0.5
B.inputs["Subsurface Weight"].default_value = 0.4; B.inputs["Subsurface Radius"].default_value = (0.5, 0.2, 0.08)
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.2; L.new(vein, bp.inputs["Height"]); L.new(bp.outputs["Normal"], B.inputs["Normal"])
tr = N.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (*lin((1.0, 0.6, 0.25)), 1)
mx = N.new("ShaderNodeMixShader"); mx.inputs["Fac"].default_value = 0.3
L.new(B.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
bone = bpy.data.materials.get("BebeBone") or bpy.data.materials.new("BebeBone")
bb = bone.node_tree.nodes["Principled BSDF"]; bb.inputs["Base Color"].default_value = (*lin((0.9, 0.32, 0.2)), 1); bb.inputs["Roughness"].default_value = 0.45
for o in [o for o in bpy.data.objects if o.name.startswith("BebeWingBone")]: bpy.data.objects.remove(o, do_unlink=True)
def btube(name, pts, radii, mw):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 12
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 4; cu.use_fill_caps = True
    s_ = cu.splines.new('BEZIER'); s_.bezier_points.add(len(pts) - 1)
    for bpn, pp, r in zip(s_.bezier_points, pts, radii):
        bpn.co = V(pp); bpn.handle_left_type = bpn.handle_right_type = 'AUTO'; bpn.radius = r
    o = bpy.data.objects.new(name, cu); cu.materials.append(bone); sc.collection.objects.link(o); o.matrix_world = mw; return o
for s in (-1, 1):
    w = bpy.data.objects[f"Wing_{s}"]; w.data.materials.clear(); w.data.materials.append(m)
    mw = w.matrix_world.copy(); wrist = (0.3, 0.29, 0.012)
    btube(f"BebeWingBone_arm_{s}", [(0, 0, 0), (0.15, 0.17, 0.012), wrist], [0.04, 0.032, 0.026], mw)
    for k, tip in enumerate(((0.62, 0.42, 0.012), (0.58, 0.08, 0.012), (0.4, -0.06, 0.012))):
        mid = tuple((a + b) / 2 for a, b in zip(wrist, tip))
        btube(f"BebeWingBone_f{k}_{s}", [wrist, mid, tip], [0.024, 0.015, 0.005], mw)

cam = sc.camera; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
def shot(name, tgt, d, dist):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
shot("bebe_tex", (0, -0.1, 0.8), (0.75, -1, 0.35), 7.5)
shot("bebe_tex_dos", (0, 0.1, 0.8), (-0.9, 0.8, 0.55), 7.5)
shot("bebe_tex_ado", (2.6, 0.6, 1.4), (0.6, -1, 0.3), 21)
