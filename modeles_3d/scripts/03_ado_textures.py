# Textures realistes pour l'ADO (a lancer apres ado_v9.py)
import bpy, math
from mathutils import Vector as V, Matrix
sc = bpy.context.scene; P = "Ado_"
coll = bpy.data.collections["Ado"]
def lin(c): return tuple(x ** 2.2 for x in c)
def newmat(name):
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ('BSDF_PRINCIPLED', 'OUTPUT_MATERIAL'): nt.nodes.remove(n)
    return m, nt.nodes, nt.links, nt.nodes["Principled BSDF"]
def math_node(N, L, op, a=None, b=None, va=None, vb=None):
    n = N.new("ShaderNodeMath"); n.operation = op
    if a is not None: L.new(a, n.inputs[0])
    elif va is not None: n.inputs[0].default_value = va
    if b is not None: L.new(b, n.inputs[1])
    elif vb is not None: n.inputs[1].default_value = vb
    return n.outputs[0]
def maprange(N, L, x, fmin, fmax, tmin=0.0, tmax=1.0):
    n = N.new("ShaderNodeMapRange"); L.new(x, n.inputs["Value"])
    n.inputs["From Min"].default_value = fmin; n.inputs["From Max"].default_value = fmax
    n.inputs["To Min"].default_value = tmin; n.inputs["To Max"].default_value = tmax
    return n.outputs["Result"]
def mixrgb(N, L, fac, a, b, mode='MIX'):
    n = N.new("ShaderNodeMix"); n.data_type = 'RGBA'; n.blend_type = mode
    if isinstance(fac, float): n.inputs["Factor"].default_value = fac
    else: L.new(fac, n.inputs["Factor"])
    for sock, v in (("A", a), ("B", b)):
        if isinstance(v, tuple): n.inputs[sock].default_value = v
        else: L.new(v, n.inputs[sock])
    return n.outputs["Result"]

# ================= PEAU =================
m, N, L, B = newmat("AdoSkinReal")
col = N.new("ShaderNodeVertexColor"); col.layer_name = "Col"
msk = N.new("ShaderNodeVertexColor"); msk.layer_name = "Mask"
mk = N.new("ShaderNodeSeparateColor"); L.new(msk.outputs["Color"], mk.inputs[0]); mask = mk.outputs[0]
tc = N.new("ShaderNodeTexCoord")
vor = N.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 15; vor.inputs["Randomness"].default_value = 0.85
L.new(tc.outputs["Object"], vor.inputs["Vector"])
ved = N.new("ShaderNodeTexVoronoi"); ved.feature = 'DISTANCE_TO_EDGE'; ved.inputs["Scale"].default_value = 15; ved.inputs["Randomness"].default_value = 0.85
L.new(tc.outputs["Object"], ved.inputs["Vector"])
edge = maprange(N, L, ved.outputs["Distance"], 0.0, 0.09)                   # 0 au bord, 1 au centre de l'ecaille
dome = math_node(N, L, 'POWER', edge, vb=0.5)
# variation de teinte par ecaille
cs = N.new("ShaderNodeSeparateColor"); L.new(vor.outputs["Color"], cs.inputs[0])
var = maprange(N, L, cs.outputs[0], 0, 1, 0.78, 1.12)
vcol = N.new("ShaderNodeCombineColor"); L.new(var, vcol.inputs[0]); L.new(var, vcol.inputs[1]); L.new(var, vcol.inputs[2])
base = mixrgb(N, L, mask, col.outputs["Color"], col.outputs["Color"])
c1 = mixrgb(N, L, mask, base, mixrgb(N, L, 1.0, base, vcol.outputs[0], 'MULTIPLY'))
# creux sombres entre les ecailles
crev = math_node(N, L, 'MULTIPLY', math_node(N, L, 'SUBTRACT', va=1.0, b=dome), mask)
c2 = mixrgb(N, L, crev, c1, mixrgb(N, L, 1.0, c1, (0.3, 0.12, 0.1, 1), 'MULTIPLY'))
# dos plus fonce
geo = N.new("ShaderNodeNewGeometry"); gs = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], gs.inputs[0])
top = math_node(N, L, 'MULTIPLY', maprange(N, L, gs.outputs["Z"], 0.2, 1.0, 0, 0.45), mask)
c3 = mixrgb(N, L, top, c2, mixrgb(N, L, 1.0, c2, (0.45, 0.2, 0.2, 1), 'MULTIPLY'))
# plaques ventrales (sillons)
wav = N.new("ShaderNodeTexWave"); wav.wave_type = 'BANDS'; wav.bands_direction = 'Z'; wav.wave_profile = 'SIN'
wav.inputs["Scale"].default_value = 3.0; wav.inputs["Distortion"].default_value = 0.0
L.new(tc.outputs["Object"], wav.inputs["Vector"])
groove = maprange(N, L, wav.outputs["Fac"], 0.0, 0.25, 1.0, 0.0)
belly = math_node(N, L, 'SUBTRACT', va=1.0, b=mask)
gb = math_node(N, L, 'MULTIPLY', groove, belly)
c4 = mixrgb(N, L, gb, c3, mixrgb(N, L, 1.0, c3, (0.55, 0.4, 0.3, 1), 'MULTIPLY'))
L.new(c4, B.inputs["Base Color"])
# relief
h = math_node(N, L, 'ADD', math_node(N, L, 'MULTIPLY', dome, mask), math_node(N, L, 'MULTIPLY', math_node(N, L, 'SUBTRACT', va=1.0, b=groove), belly))
bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.45; bump.inputs["Distance"].default_value = 0.03
L.new(h, bump.inputs["Height"]); L.new(bump.outputs["Normal"], B.inputs["Normal"])
L.new(maprange(N, L, dome, 0, 1, 0.65, 0.32), B.inputs["Roughness"])
B.inputs["Coat Weight"].default_value = 0.15; B.inputs["Coat Roughness"].default_value = 0.25
body = bpy.data.objects[P + "Body"]; body.data.materials.clear(); body.data.materials.append(m)

# ================= KERATINE (cornes, pics, griffes) =================
def keratin(name, c_base, c_mid, c_tip):
    m, N, L, B = newmat(name)
    tc = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sp.inputs[0])
    t = math_node(N, L, 'MULTIPLY', math_node(N, L, 'ADD', sp.outputs["Y"], sp.outputs["Z"]), vb=0.5)
    cr = N.new("ShaderNodeValToRGB"); L.new(t, cr.inputs["Fac"])
    e = cr.color_ramp.elements; e[0].position = 0.15; e[0].color = (*lin(c_base), 1); e[1].position = 0.95; e[1].color = (*lin(c_tip), 1)
    mm = e.new(0.55); mm.color = (*lin(c_mid), 1)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40; nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    streak = maprange(N, L, nz.outputs["Fac"], 0.3, 0.7, 0.85, 1.05)
    sc_ = N.new("ShaderNodeCombineColor"); [L.new(streak, sc_.inputs[i]) for i in range(3)]
    L.new(mixrgb(N, L, 1.0, cr.outputs["Color"], sc_.outputs[0], 'MULTIPLY'), B.inputs["Base Color"])
    rings = N.new("ShaderNodeMath"); rings.operation = 'SINE'
    L.new(math_node(N, L, 'MULTIPLY', t, vb=60.0), rings.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.01
    L.new(rings.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], B.inputs["Normal"])
    B.inputs["Roughness"].default_value = 0.38; B.inputs["Coat Weight"].default_value = 0.3
    return m
HORNR = keratin("AdoHornReal", (0.25, 0.17, 0.13), (0.62, 0.52, 0.4), (0.96, 0.92, 0.8))
SPIKER = keratin("AdoSpikeReal", (0.4, 0.1, 0.06), (0.75, 0.45, 0.2), (0.96, 0.85, 0.6))
CLAWR = keratin("AdoClawReal", (0.12, 0.09, 0.08), (0.3, 0.25, 0.22), (0.75, 0.7, 0.62))
for o in coll.objects:
    if o.type not in ('MESH', 'CURVE'): continue
    nm = o.name[len(P):]
    tgt = None
    if nm.startswith(("Horn", "Cheek", "Fang")): tgt = HORNR
    elif nm.startswith(("Spike", "TailTip")): tgt = SPIKER
    elif nm.startswith("Claw"): tgt = CLAWR
    if tgt:
        o.data.materials.clear(); o.data.materials.append(tgt)

# ================= YEUX =================
iris = bpy.data.materials["AdoIrisGlow"]; N = iris.node_tree.nodes; L = iris.node_tree.links; B = N["Principled BSDF"]
cr = [n for n in N if n.type == 'VALTORGB'][0]; ln = [n for n in N if n.type == 'VECT_MATH'][0]
sep = [n for n in N if n.type == 'SEPXYZ'][0]
ang = N.new("ShaderNodeMath"); ang.operation = 'ARCTAN2'; L.new(sep.outputs["Z"], ang.inputs[0]); L.new(sep.outputs["X"], ang.inputs[1])
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = '2D'; nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 4
cmb = N.new("ShaderNodeCombineXYZ"); L.new(math_node(N, L, 'MULTIPLY', ang.outputs[0], vb=6.0), cmb.inputs["X"]); L.new(ln.outputs["Value"], cmb.inputs["Y"])
L.new(cmb.outputs[0], nz.inputs["Vector"])
streak = maprange(N, L, nz.outputs["Fac"], 0.3, 0.7, 0.55, 1.15)
scc = N.new("ShaderNodeCombineColor"); [L.new(streak, scc.inputs[i]) for i in range(3)]
limb = maprange(N, L, ln.outputs["Value"], 0.78, 0.98, 0.0, 1.0)
ci = mixrgb(N, L, 1.0, cr.outputs["Color"], scc.outputs[0], 'MULTIPLY')
ci = mixrgb(N, L, limb, ci, (0.02, 0.005, 0.0, 1))
L.new(ci, B.inputs["Base Color"]); L.new(ci, B.inputs["Emission Color"])
B.inputs["Emission Strength"].default_value = 0.45
B.inputs["Coat Weight"].default_value = 1.0; B.inputs["Coat Roughness"].default_value = 0.02; B.inputs["Coat IOR"].default_value = 1.45

# ================= AILES =================
m, N, L, B = newmat("AdoWingReal")
tc = N.new("ShaderNodeTexCoord")
vn = N.new("ShaderNodeTexVoronoi"); vn.feature = 'DISTANCE_TO_EDGE'; vn.inputs["Scale"].default_value = 7; vn.inputs["Randomness"].default_value = 1.0
mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 2.2, 1.0)
L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], vn.inputs["Vector"])
vein = maprange(N, L, vn.outputs["Distance"], 0.0, 0.03, 1.0, 0.0)
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 12; L.new(tc.outputs["Object"], nz.inputs["Vector"])
mott = maprange(N, L, nz.outputs["Fac"], 0.3, 0.7, 0.8, 1.1)
mc = N.new("ShaderNodeCombineColor"); [L.new(mott, mc.inputs[i]) for i in range(3)]
memb = mixrgb(N, L, 1.0, (*lin((0.72, 0.2, 0.1)), 1), mc.outputs[0], 'MULTIPLY')
wc = mixrgb(N, L, vein, memb, (*lin((0.35, 0.06, 0.04)), 1))
L.new(wc, B.inputs["Base Color"])
B.inputs["Roughness"].default_value = 0.5
B.inputs["Subsurface Weight"].default_value = 0.4; B.inputs["Subsurface Radius"].default_value = (0.5, 0.15, 0.05)
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; L.new(vein, bp.inputs["Height"]); L.new(bp.outputs["Normal"], B.inputs["Normal"])
tr = N.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (*lin((1.0, 0.42, 0.12)), 1)
mix = N.new("ShaderNodeMixShader"); mix.inputs["Fac"].default_value = 0.3
out = N["Material Output"]
L.new(B.outputs[0], mix.inputs[1]); L.new(tr.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs["Surface"])
bone = bpy.data.materials.get("AdoBone") or bpy.data.materials.new("AdoBone")
bb = bone.node_tree.nodes["Principled BSDF"]; bb.inputs["Base Color"].default_value = (*lin((0.55, 0.12, 0.08)), 1); bb.inputs["Roughness"].default_value = 0.4
for o in [o for o in bpy.data.objects if o.name.startswith(P + "WingBone")]: bpy.data.objects.remove(o, do_unlink=True)
def btube(name, pts, radii, mw):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 12
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bpn, pp, r in zip(sp.bezier_points, pts, radii):
        bpn.co = V(pp); bpn.handle_left_type = bpn.handle_right_type = 'AUTO'; bpn.radius = r
    o = bpy.data.objects.new(name, cu); cu.materials.append(bone); coll.objects.link(o); o.matrix_world = mw; return o
for s in (-1, 1):
    w = bpy.data.objects[P + f"Wing_{s}"]
    w.data.materials.clear(); w.data.materials.append(m)
    mw = w.matrix_world.copy()
    root, wrist = (0, 0, 0), (0.3, 0.29, 0.012)
    btube(P + f"WingBone_arm_{s}", [root, (0.15, 0.17, 0.012), wrist], [0.035, 0.028, 0.022], mw)
    for k, tip in enumerate(((0.62, 0.42, 0.012), (0.58, 0.08, 0.012), (0.4, -0.06, 0.012))):
        mid = tuple((a + b) / 2 for a, b in zip(wrist, tip))
        btube(P + f"WingBone_f{k}_{s}", [wrist, mid, tip], [0.02, 0.013, 0.004], mw)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.02, radius2=0, depth=0.07)
    o = bpy.context.object; o.name = P + f"WingBone_claw_{s}"; o.data.materials.append(CLAWR)
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)
    o.matrix_world = mw @ Matrix.Translation((0.31, 0.33, 0.012)) @ Matrix.Rotation(math.radians(-60), 4, 'X')

sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
cam = sc.camera; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
TAG = globals().get("TAG", "tex")
def shot(name, tgt, d, dist):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
Smat = Matrix.Translation((5.0, 0, 0)) @ Matrix.Scale(1.15, 4)
HCw = Smat @ (V((0, -0.9, 2.05)) + V((0, -0.35, 0.61)))
shot(TAG + "_tete", HCw + V((0, -0.3, -0.1)), (0.55, -1, 0.12), 5.0)
shot(TAG + "_profil", (5.0, 1.4, 1.9), (1, -0.15, 0.12), 15)
shot(TAG + "_aile", (5.6, 0.6, 3.0), (0.4, 0.6, 0.6), 9)
