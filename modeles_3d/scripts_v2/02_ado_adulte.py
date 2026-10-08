# Dragon classique v2 (style Roblox) - ADO et ADULTE. A lancer apres 01_bebe.py.
# Reprend la geometrie de la v1 (blend/Dragon_classique.blend, collections "Ado" et "Adulte")
# et la restyle : couleurs unies, plastron net, flamme du front (comme le bebe), flammes sur les flancs
# et la queue (qui brillent chez l'adulte), nouveaux yeux (meme recette que le bebe, en amande).
import bpy, bmesh, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v2")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())
sc = bpy.context.scene
SRC = os.path.join(os.path.dirname(DIR), "blend", "Dragon_classique.blend")

# ---------------- 1) importer la geometrie v1 ----------------
for name in ("Ado", "Adulte"):
    old = bpy.data.collections.get(name)
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.collections = ["Ado", "Adulte"]
for c in dst.collections: sc.collection.children.link(c)
bpy.context.view_layer.update()                     # sinon matrix_world des objets importes vaut encore l'identite

# ---------------- 2) reglages par stade ----------------
# HC / SN : centre de la tete et du museau dans les coordonnees locales du corps (voir scripts/02_ado.py et 06_adulte.py)
FLAMES_TETE = [((0, 0.42), (0, 1.5), 0.2), ((0.13, 0.48), (0.6, 1.15), 0.12), ((-0.13, 0.48), (-0.6, 1.15), 0.12)]
STAGES = {
    "Ado": dict(P="Ado_", HC=V((0, -1.25, 2.66)), SN=V((0, -1.7, 2.51)), dos=0.3, plaques=6.5,
                flammes=dict(freq=3.2, hw=0.3, pente=0.35, y0=-0.35, z_torse=1.15), glow=0.0,
                oeil=dict(w=0.17, h=0.1, tilt=-14, lid_tilt=-24)),
    "Adulte": dict(P="Adulte_", HC=V((0, -1.52, 2.97)), SN=V((0, -1.97, 2.82)), dos=0.45, plaques=5.5,
                   flammes=dict(freq=2.8, hw=0.34, pente=0.35, y0=-0.4, z_torse=1.15), glow=1.2,
                   oeil=dict(w=0.16, h=0.088, tilt=-16, lid_tilt=-28)),
}

HORN = mat("V2Horn", PAL["HORN"], 0.35); SPIKE = mat("V2Spike", PAL["SPIKE"], 0.4)
WING = mat("V2Wing", PAL["WING"], 0.5, coat=0.0); BONE = mat("V2WingBone", PAL["RED"], 0.45)
def corne(name, c_base, c_tip):
    """keratine bicolore : base claire -> pointe foncee (le long de la corne : coordonnees Generated Y+Z)."""
    m = new_mat(name, 0.35); X = Nodes(m); tc = X.N.new("ShaderNodeTexCoord"); g = X.sep(tc.outputs["Generated"])
    t = X.sstep(0.55, 0.95, X.mul(X.m('ADD', g[1], g[2]), 0.5))
    X.L.new(X.mix(t, rgba(c_base), rgba(c_tip)), X.N["Principled BSDF"].inputs["Base Color"]); return m
HORN2 = corne("V2Horn2", PAL["HORN"], (0.3, 0.12, 0.1))
DARK = mat("V2Dark", PAL["DARK"], 0.1); IRIS = mat("V2Iris", PAL["IRIS"], 0.1, emit=0.35)
HL = mat("V2HL", (1, 1, 1), 0.2, emit=2.0, coat=0); LID = mat("V2Lid", PAL["RED"], 0.45)

def peau(name, body, st):
    """peau unie : rouge (dos plus fonce), plastron creme a plaques, flamme du front, flammes des flancs."""
    me = body.data
    # plastron : on reprend la zone "ventre" de la v1 (canal vert de l'attribut Col, normalise 0..1)
    cola = me.color_attributes["Col"]; g = [cola.data[i].color[1] for i in range(len(me.vertices))]
    g0, g1 = min(g), max(g); val = [(gv - g0) / (g1 - g0) for gv in g]
    nb = [[] for _ in val]                                  # lissage du champ (bord du plastron sans dents de scie)
    for e in me.edges:
        i, j = e.vertices; nb[i].append(j); nb[j].append(i)
    for _ in range(6):
        val = [0.5 * val[i] + 0.5 * sum(val[j] for j in nb[i]) / len(nb[i]) if nb[i] else val[i] for i in range(len(val))]
    att = me.attributes.get("Ventre") or me.attributes.new("Ventre", 'FLOAT', 'POINT')
    for i, x in enumerate(val): att.data[i].value = x
    m = new_mat(name); X = Nodes(m)
    tc = X.N.new("ShaderNodeTexCoord"); geo = X.N.new("ShaderNodeNewGeometry")
    at = X.N.new("ShaderNodeAttribute"); at.attribute_name = "Ventre"
    pos = tc.outputs["Object"]; px, py, pz = X.sep(pos)[:3]; nz = X.sep(geo.outputs["Normal"])[2]
    c = X.mix(X.mul(X.sstep(0.3, 1.0, nz), st["dos"]), rgba(PAL["RED"]), rgba(PAL["RED_DARK"]))
    # flammes des flancs : langues qui partent du ventre et montent vers le dos, longues/courtes en alternance
    f = st["flammes"]
    s_ = X.m('MULTIPLY_ADD', py, f["freq"], X.m('MULTIPLY', nz, f["pente"]))
    u = X.m('FRACT', s_); k = X.m('FLOORED_MODULO', X.m('FLOOR', s_), 2.0)
    top = X.m('MULTIPLY_ADD', k, -0.3, 0.75)
    w = X.m('MULTIPLY', X.inv(X.sstep(-0.3, top, nz)), f["hw"])
    tongue = X.sstep(-0.012, 0.012, X.m('SUBTRACT', w, X.m('ABSOLUTE', X.m('SUBTRACT', u, 0.5))))
    torse = X.mul(X.sstep(f["y0"], f["y0"] + 0.1, py), X.inv(X.sstep(1.4, 1.5, py)), X.sstep(f["z_torse"], f["z_torse"] + 0.08, pz))
    zone = X.m('MAXIMUM', torse, X.sstep(1.4, 1.5, py))
    marks = X.m('MAXIMUM', X.mul(tongue, zone), flamme(X, pos, st["HC"], FLAMES_TETE, 0.85, st["HC"].z - 0.1))
    c = X.mix(marks, c, rgba(PAL["FLAME"]))
    # plastron (par-dessus) + lignes de plaques
    bel = X.sstep(0.45, 0.55, at.outputs["Fac"])
    ligne = X.inv(X.sstep(0.035, 0.06, X.m('ABSOLUTE', X.m('SUBTRACT', X.m('FRACT', X.m('MULTIPLY', pz, st["plaques"])), 0.5))))
    c = X.mix(bel, c, X.mix(X.mul(ligne, 0.85), rgba(PAL["BELLY"]), rgba(PAL["BELLY_DARK"])))
    B = X.N["Principled BSDF"]; X.L.new(c, B.inputs["Base Color"])
    if st["glow"]:
        X.L.new(X.mix(X.mul(marks, X.inv(bel)), (0, 0, 0, 1), rgba(PAL["FLAME"])), B.inputs["Emission Color"])
        B.inputs["Emission Strength"].default_value = st["glow"]
    me.materials.clear(); me.materials.append(m)

def lemon(name, S, loc, q, w, h, dep, mm, sharp=1.0, coll=None):
    """amande : sphere aplatie en pointe sur les cotes (axe X = largeur, -Y = vers l'exterieur, Z = hauteur)."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1)
    for v in bm.verts: v.co.z *= max(0.0, 1 - v.co.x ** 2) ** (0.5 * sharp)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); coll.objects.link(o); me.materials.append(mm)
    o.matrix_world = S @ Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((w, dep, h, 1)); return o
def face_quat(n, tilt_deg, s):
    """axe -Y local = normale, X local = horizontal vers l'exterieur, puis inclinaison."""
    up = V((0, 0, 1)); z = (up - n * up.dot(n)).normalized()
    y = -n; x = y.cross(z)
    q = Matrix((x, y, z)).transposed().to_quaternion()
    return q @ Matrix.Rotation(math.radians(tilt_deg * s), 4, 'Y').to_quaternion()

def yeux(body, st, coll):
    """meme recette que le bebe : contour sombre, iris ambre, pupille fendue epaisse, reflets, paupiere lourde."""
    P = st["P"]; S = body.matrix_basis.copy(); e = st["oeil"]
    for s in (-1, 1):
        d = V((s * 0.5, -0.82, 0.12)).normalized()
        h_, l, n, _ = body.ray_cast(st["HC"] + d * 3, -d)
        q = face_quat(n, e["tilt"], s); w, h = e["w"], e["h"]
        lemon(P + f"Eye_{s}", S, l - n * 0.035, q, w, h, 0.06, DARK, 1.2, coll)                       # contour
        lemon(P + f"EyeIris_{s}", S, l + n * 0.02, q, w * 0.86, h * 0.84, 0.012, IRIS, 1.2, coll)
        lemon(P + f"EyePupil_{s}", S, l + n * 0.028, q, 0.026, h * 0.72, 0.008, DARK, 0.0, coll)     # fente epaisse
        lemon(P + f"EyeHL1_{s}", S, l + n * 0.034 + q @ V((-0.045, 0, 0.025)), q, 0.024, 0.022, 0.005, HL, 0.0, coll)
        lemon(P + f"EyeHL2_{s}", S, l + n * 0.034 + q @ V((0.05, 0, -0.03)), q, 0.011, 0.011, 0.004, HL, 0.0, coll)
        ql = face_quat(n, e["lid_tilt"], s)                                                             # paupiere vers le nez
        lemon(P + f"EyeLid_{s}", S, l - n * 0.045 + ql @ V((0, 0, h * 0.9)), ql, w * 1.2, h * 0.6, 0.07, LID, 1.6, coll)

# ---------------- 3) restyle ----------------
for cname, st in STAGES.items():
    coll = bpy.data.collections[cname]; P = st["P"]
    body = bpy.data.objects[P + "Body"]
    for o in [o for o in coll.objects if o.name[len(P):].startswith(("Eye", "EyeBrow"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    peau(f"V2Peau{cname}", body, st)
    for o in coll.objects:
        nm = o.name[len(P):]
        if o.type not in ('MESH', 'CURVE') or nm == "Body": continue
        if nm.startswith(("Horn", "Cheek", "NoseHorn")): mm = HORN2
        elif nm.startswith(("Fang", "Claw", "WingBone_thumb")): mm = HORN
        elif nm.startswith(("Spike", "TailTip")): mm = SPIKE
        elif nm.startswith("WingBone"): mm = BONE
        elif nm.startswith("Wing"): mm = WING
        elif nm.startswith(("Mouth", "Nostril")): mm = DARK
        else: print("non restyle :", o.name); continue
        o.data.materials.clear(); o.data.materials.append(mm)
    yeux(body, st, coll)
bpy.data.orphans_purge(do_recursive=True)
print("ado + adulte v2 OK")

# ---------------- rendus ----------------
cam = sc.camera; r = sc.render; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
def shot(name, tgt, d, dist):
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    r.resolution_x, r.resolution_y = 1200, 750
    r.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
if globals().get("RENDER", True):
    for cname, dist_t in (("Ado", 6.0), ("Adulte", 8.0)):
        st = STAGES[cname]; S = bpy.data.objects[st["P"] + "Body"].matrix_world
        shot(f"v2_{cname.lower()}_tete", S @ st["HC"] + V((0, -0.3, -0.1)), (0.55, -1, 0.12), dist_t)
    shot("v2_ado", (5.0, 0.8, 1.6), (0.6, -1, 0.3), 16)
    shot("v2_adulte", (11.5, 1.0, 2.4), (0.6, -1, 0.3), 26)
    shot("v2_bebe_ado_adulte", (7.0, 0.6, 2.2), (0.25, -1, 0.28), 35)
