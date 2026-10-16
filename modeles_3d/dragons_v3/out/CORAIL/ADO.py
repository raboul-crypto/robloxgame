import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Corail · Ado
#  Commun · Eau · Drake · monde 3
#  - Ado drake qui s'allonge : cou de 3 blocs, petits crocs, sourcils corail, pattes avec plaques d'armure bleues
#  - Signes distinctifs : bois de corail ramifiés, coraux sur le dos, le cou et la queue, coquilles en épaulettes, nageoires-oreilles
#  - Commun : silhouette propre, pas d'émission (sauf les yeux), quelques bulles flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3301)            # même dragon à chaque exécution
TAG = "CORAIL_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 4500          # budget de triangles de ce stade et de cette rareté
ADD_FLOATING_FX = True         # éléments flottants autour du dragon (cristaux, braises...)
COLL_NAME = TAG

# ----------------------------------------------------------
# 0. NETTOYAGE (ne touche qu'à ce dragon et à ce stade)
# ----------------------------------------------------------
coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)

def belongs_to_tag(obj):
    """Vrai si l'objet est un root de ce dragon ou un de ses enfants. Les autres stades ne sont jamais touchés."""
    o = obj
    while o is not None:
        if o.name.startswith(TAG + "_"):
            return True
        o = o.parent
    return False

to_delete = [o for o in bpy.data.objects
             if coll in o.users_collection or belongs_to_tag(o)
             or (o.name == "Cube" and o.type == 'MESH' and len(o.data.vertices) == 8)]
for obj in to_delete:
    bpy.data.objects.remove(obj, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)

# @@KIT@@

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Bleu azur (corps), bleu clair (taches, ailerons), crème (ventre), corail saumon (bois, crête), beige rosé (coquilles).
#    Commun : 5 familles de couleurs, aucune émission sauf la lueur douce des yeux.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#2670B8", 0.50)   # corps principal, bleu azur
M_BODY2 = get_mat("BodyLight", "#4A9BDD", 0.50)   # dessus du museau, écailles claires
M_DARK  = get_mat("BodyDark",  "#17426F", 0.60)   # bouche, narines, genoux, plaques sombres
M_MARK  = get_mat("Mark",      "#7CC2EA", 0.45)   # taches bleu clair, nageoires-oreilles
M_BELLY = get_mat("Belly",     "#EDE6D6", 0.55)   # ventre en plaques, plastron, mâchoire
M_CORAL = get_mat("Coral",     "#FF917D", 0.50)   # bois de corail, crête, sourcils
M_CORAL2= get_mat("CoralDark", "#E8625A", 0.55)   # corail plus sombre (branches du bas, bases)
M_SHELL = get_mat("Shell",     "#E8CDB8", 0.50)   # coquilles beige rosé (épaulettes)
M_SHELL2= get_mat("ShellDark", "#D3A58F", 0.55)   # nervures de coquille
M_CLAW  = get_mat("Claw",      "#E9ECEF", 0.35)   # griffes et crocs
M_WHITE = get_mat("EyeWhite",  "#F4F7FA", 0.30)
M_IRIS  = get_mat("Iris",      "#2AA0EE", 0.25, emission="#2AA0EE", strength=1.0)   # iris bleu lumineux
M_BLACK = get_mat("Black",     "#0A1018", 0.30)   # pupilles, narines
M_BUBBLE= get_mat("Bubble",    "#BFE6F7", 0.20)   # bulles flottantes

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADO"
BW = 3.0
BH = 2.2
LEG_H = 1.8
TORSO_L = 4.2
NECK_L = 1.7
NECK_LEAN = 0.3
NECK_N = 3
NECK_R = (0.9, 1.1)
HEAD_SCALE = 1.1
SNOUT_K = 0.85
FANGS = 2
HEAD_SPOTS = 2
EAR_N = 3
EAR_K = 1.0
ANTLER_K = 0.85
ANTLER_DEPTH = 2
CHEEK_CORAL = False
BELLY_N = 5
BELLY_SIDES = True
SCALE_ROWS = 2
SCALE_COLS = 4
CORAL_N = 5
CORAL_K = 0.85
CORAL_DEPTH = 1
PLATE_N = 3
SHELL_N = 1
SHELL_K = 1.35
SHELL_RIBS = 6
NECK_CORAL = True
ARMOR = True
LEG_SPOTS = 1
KNEE = False
TAIL_L = 4.6
TAIL_STEP = 0.75
TAIL_BEV_N = 3
TAIL_CORAL_EVERY = 2
CLUB_SIZE = 1.0
TAIL_TIP_N = 3
TAIL_FIN = 2
FX_N = 6
FX_SIZE = 0.5

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 1.9                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_BASE = Vector((0, -TL * 0.36, ZC + BH * 0.2))
NECK_TOP = NECK_BASE + Vector((0, -NECK_LEAN, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.1 * HEAD_SCALE, 0.45 * HEAD_SCALE))
HEAD_PITCH = 8                                   # degrés : la tête regarde un peu vers le bas
TAIL_START = Vector((0, TL * 0.42, ZC - 0.12 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def rock(name, size, loc, mat, parent, rot=None, jit=10, tx=0.72, ty=0.78, bevel=0.0):
    """Plaque taillée : bloc dont le dessus est rétréci, légèrement tourné au hasard (seed fixe)."""
    if rot is None:
        rot = (random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit * 2, jit * 2))
    return wedge(name, size, loc, rot, mat, parent, top_x=tx, top_y=ty,
                 shift_y=random.uniform(-0.12, 0.12) * size[1], bevel=bevel)

def spot(name, loc, normal, r, mat, parent, h=0.07, sides=6):
    """Tache plate posée sur la peau (prisme dont l'axe = normale de la surface)."""
    return prism(name, r, h, loc, normal, mat, parent, sides=sides, up=(0, 0, 1))

def coral(name, base, direction, length, thick, depth, parent, side=1, spread=40, mats=None):
    """Branche de corail : une barre, une branche latérale au 55 % et la suite du tronc au bout.
    depth = nombre de ramifications (0 = simple pointe). Récursif, seed fixe."""
    mats = mats or (M_CORAL, M_CORAL2)
    base, d = Vector(base), Vector(direction).normalized()
    tip = base + d * length
    mat = mats[depth % 2]
    link(name, base, tip, thick, mat, parent, up=(0, 0, 1), extra=thick * 0.6, bevel=0, depth=thick)
    if depth <= 0:
        shard(name + "_T", thick * 1.5, thick * 1.2, length * 0.55, tip - d * thick * 0.3, d, mats[0], parent, up=(1, 0, 0))
        return
    ax = d.cross(Vector((0, 1, 0)) if depth % 2 else Vector((1, 0, 0)))
    if ax.length < 1e-3:
        ax = Vector((1, 0, 0))
    ax.normalize()
    d2 = Matrix.Rotation(math.radians(side * (spread + random.uniform(-8, 8))), 3, ax) @ d
    coral(name + "s", base + d * length * 0.55, d2, length * 0.62, thick * 0.72, depth - 1, parent, -side, spread, mats)
    d3 = Matrix.Rotation(math.radians(-side * random.uniform(8, 16)), 3, ax) @ d
    coral(name + "t", tip - d * thick * 0.2, d3, length * 0.78, thick * 0.8, depth - 1, parent, side, spread, mats)

def scallop_mesh(R, ribs, h, arc=150):
    """Coquille Saint-Jacques : éventail de nervures en toit (une par tranche) qui part de la charnière (0,0,0)
    vers +Y, bombé vers +Z. Chaque nervure : base plate + arête qui monte vers le bord."""
    verts, faces = [], []
    a_start = math.radians(90 - arc / 2)
    da = math.radians(arc) / ribs
    for i in range(ribs):
        a0, a1 = a_start + i * da, a_start + (i + 1) * da
        am = (a0 + a1) / 2
        hh = h * (1.0 if i % 2 else 0.8)
        n = len(verts)
        verts += [(0, 0, 0), (R * math.cos(a0), R * math.sin(a0), 0), (R * math.cos(a1), R * math.sin(a1), 0),
                  (R * 0.97 * math.cos(am), R * 0.97 * math.sin(am), hh), (0, 0, h * 0.4)]
        faces += [(n, n + 2, n + 1), (n, n + 1, n + 3, n + 4), (n + 2, n, n + 4, n + 3), (n + 1, n + 2, n + 3)]
    return mesh_from("scallop", verts, faces)

def scallop(name, hinge, direction, outward, R, ribs, parent, mats=None):
    """Pose une coquille : charnière en 'hinge', éventail vers 'direction', bombée vers 'outward'.
    Les nervures alternent deux teintes (une pièce par teinte)."""
    mats = mats or (M_SHELL, M_SHELL2)
    me = scallop_mesh(R, ribs, R * 0.32)
    place(name, me, mats[0], hinge, basis(direction, outward), parent)
    # base de la charnière (petit bloc sombre) et arête centrale
    B(name + "_Hinge", (R * 0.32, R * 0.32, R * 0.22), Vector(hinge), None, mats[1], parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne carré bleu, museau, mâchoire crème, nageoires-oreilles bleu clair, sourcils corail,
#    deux grands bois de corail ramifiés (signe distinctif).
# ----------------------------------------------------------
HS = HEAD_SCALE
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.75, 2.1 * SNOUT_K, 1.0), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.06, bevel=0.08)
hbox("SnoutTop", (1.5, 1.9 * SNOUT_K, 0.16), (0, -0.6 - 1.0 * SNOUT_K, 0.27), mat=M_BODY2, bevel=0.03)
hbox("Jaw", (1.55, 1.95 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY, bevel=0.04)
hbox("Chin", (1.7, 0.4, 0.4), (0, -0.55 - 2.0 * SNOUT_K - 0.08, -0.74), mat=M_BELLY, bevel=0.04)
hbox("MouthLine", (1.8, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.26, 0.24, 0.07), (sgn * 0.45, SNOUT_FRONT + 0.25, 0.36), mat=M_BLACK)

# Taches bleu clair sur le crâne et le museau
for sgn in (-1, 1):
    for k in range(HEAD_SPOTS):
        p = (sgn * 0.9, 0.0 + 0.32 * k, 0.62 - 0.1 * (k % 2))
        spot(f"Head_Spot_{sgn}_{k}", hv(p), (sgn, 0, 0), 0.17 * HS * (1.0 - 0.1 * k), M_MARK, H)

# Yeux : blanc, iris, pupille (ronde + reflets pour bébé, fendue pour ado / adulte) + sourcils
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.9, 0.98, 0.7, 0.82, 0.42, 0.58
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.64, 0.42, 0.54, 0.1, 0.5
for sgn in (-1, 1):
    ey, ez = -0.3, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.07, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.11, 0.11), (sgn * 1.07, ey + 0.13, ez - 0.22), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.22, 1.0, 0.26), (sgn * 0.97, ey - 0.05, ez + 0.54), rot=(14, 0, 0),
             mat=M_CORAL2, bevel=0.02)

# Crocs : ado 2 par côté (petits), adulte 3 par côté (plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.72, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Nageoires-oreilles : éventail de rayons bleu clair sur une base, de chaque côté du crâne
for sgn in (-1, 1):
    hbox(f"EarBase_{sgn}", (0.34, 0.5, 0.55), (sgn * 0.98, 0.5, 0.0), mat=M_BODY2)
    for k in range(EAR_N):
        f = k / max(1, EAR_N - 1)
        dv = (sgn * (0.75 + 0.1 * f), 0.5 + 0.7 * (1 - f), 0.55 - 0.95 * f)
        hshard(f"Ear_{sgn}_{k}", 0.5 - 0.06 * f, 0.1, (1.3 - 0.25 * f) * EAR_K, (sgn * 1.02, 0.5, 0.05 - 0.05 * f), dv,
               M_MARK if k % 2 == 0 else M_BODY2, up=(sgn, 0, 0))

# Bois de corail (signe distinctif) : deux ramures ramifiées sur le dessus du crâne
for sgn in (-1, 1):
    hbox(f"AntlerBase_{sgn}", (0.6, 0.6, 0.35), (sgn * 0.5, 0.25, 0.82), mat=M_CORAL2, bevel=0.03)
    coral("Head_Antler_%d" % sgn, hv((sgn * 0.5, 0.25, 0.9)), (sgn * 0.45, 0.25, 1.0), 1.5 * ANTLER_K * HS,
          0.36 * HS * ANTLER_K ** 0.5, ANTLER_DEPTH, H, side=sgn)
    if CHEEK_CORAL:
        coral("Head_CheekCoral_%d" % sgn, hv((sgn * 0.9, 0.35, -0.3)), (sgn * 0.9, 0.75, -0.25), 0.9 * HS * ANTLER_K,
              0.24 * HS, max(0, ANTLER_DEPTH - 1), H, side=sgn)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, plastron crème, ventre en plaques, taches, coraux dorsaux, coquilles, cou
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron crème + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_BELLY, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_BELLY, parent=body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.32),
              mat=M_BELLY, parent=body_root)

# Écailles en quinconce sur les flancs : losanges sombres/clairs + taches bleu clair
for sgn in (-1, 1):
    for r in range(SCALE_ROWS):
        for c in range(SCALE_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / SCALE_COLS
            z = ZC + BH * (0.24 - 0.2 * r)
            x = sgn * (half_w(y) + 0.03 * SC)
            if (r + c) % 3 == 1:
                spot(f"Body_Spot_{sgn}_{r}_{c}", (x, y, z), (sgn, 0, 0), BH * 0.075, M_MARK, body_root)
            else:
                sz = BH * 0.12
                plate(f"Body_Scale_{sgn}_{r}_{c}", [(x, y - sz, z), (x, y, z + sz * 0.8), (x, y + sz, z), (x, y, z - sz * 0.8)],
                      0.07 * SC, M_DARK if (r + c) % 2 else M_BODY2, body_root)

# Coraux dorsaux : une branche de corail par vertèbre le long de l'échine
for k in range(CORAL_N):
    f = k / max(1, CORAL_N - 1)
    y = -TL * 0.38 + (TL * 0.82) * f
    L_ = (1.15 - 0.3 * f) * SC * CORAL_K
    rock(f"Body_CoralBase_{k}", (BW * 0.42, TL * 0.8 / CORAL_N, 0.3 * SC), (0, y, ZC + BH / 2 + 0.02 * BH), M_CORAL2, body_root,
         rot=(0, 0, 0), tx=0.7, ty=0.8)
    coral(f"Body_Coral_{k}", (0, y, ZC + BH / 2 + 0.1 * BH), (0.05 * (-1) ** k, 0.25 + 0.1 * f, 1.0), L_, 0.3 * SC * CORAL_K,
          CORAL_DEPTH, body_root, side=1 if k % 2 else -1, spread=52)
# Plaques d'armure bleues entre les coraux (ado / adulte)
for k in range(PLATE_N):
    f = (k + 0.5) / PLATE_N
    y = -TL * 0.38 + (TL * 0.82) * f
    for sgn in (-1, 1):
        rock(f"Body_Plate_{sgn}_{k}", (BW * 0.28, TL * 0.7 / PLATE_N, 0.36 * SC),
             (sgn * BW * 0.3, y, ZC + BH / 2 - 0.04 * BH), M_DARK if k % 2 else M_BODY2, body_root,
             rot=(0, sgn * 10, random.uniform(-5, 5)), tx=0.7, ty=0.85, bevel=0.0)

# Coquilles Saint-Jacques en épaulettes (signe distinctif)
for sgn in (-1, 1):
    for k in range(SHELL_N):
        R_ = BW * (0.44 - 0.08 * k) * SHELL_K
        hinge = (sgn * BW * 0.47, -TL * 0.2 + k * TL * 0.42, ZC + BH * (0.4 - 0.06 * k))
        scallop(f"Body_Shell_{sgn}_{k}", hinge, (sgn * 0.12, 0.0, -1.0), (sgn * 1.0, 0, 0.15), R_, SHELL_RIBS, body_root)

# Cou : courbe lissée de la tête vers le torse, bloc bleu + plaque crème devant par maillon, corail sur la nuque
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):
    p = NECK_BASE.lerp(NECK_TOP, tt)
    p.y -= 0.3 * NECK_LEAN * math.sin(math.pi * tt)
    NECK_CTRL.append(p)
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_L * 1.04) / NECK_N)
NN = len(NECK_SPINE) - 1
for i in range(NN):
    p1, p2 = NECK_SPINE[i], NECK_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / NN
    r = keyed([(0, NECK_R[0]), (1, NECK_R[1])], s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.22, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_BELLY, body_root)
    if NECK_CORAL and i < NN - 1:
        coral(f"Body_NapeCoral_{i}", mid + d * r * 0.8, d * 1.0 + t * 0.35, r * 1.1 * CORAL_K, r * 0.28, max(0, CORAL_DEPTH - 1),
              body_root, side=1 if i % 2 else -1)

# ----------------------------------------------------------
# 11. PATTES : cuisse en wedge, jambe, plaque d'armure, genouillère, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.26)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.92, th * 0.97, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_BODY2 if ARMOR else M_BODY, parent=legs_root, bevel=0.05 * SC if ARMOR else 0)
    if ARMOR:
        rock(f"{name}_Bracer", (th * 1.1, th * 1.14, SHIN_H * 0.45), (x, y + yo, FOOT_H + SHIN_H * 0.62), M_DARK, legs_root,
             rot=(0, 0, random.uniform(-6, 6)), tx=0.92, ty=0.92)
        B(f"{name}_BracerTop", (th * 1.0, th * 1.04, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.62 + SHIN_H * 0.23),
          mat=M_CORAL, parent=legs_root)
    for k in range(LEG_SPOTS):
        spot(f"{name}_Spot_{k}", (x + sgn * th * 0.66, y + yo + th * (-0.25 + 0.4 * k), FOOT_H + SHIN_H + thigh_h * (0.7 - 0.25 * k)),
             (sgn, 0, 0), th * 0.1, M_MARK, legs_root)
    if KNEE:
        scallop(f"{name}_KneeShell", (x, y + yo - th * 0.55, FOOT_H + SHIN_H + 0.12 * thigh_h), (0, -0.3, 1.0), (0, -1, 0.2),
                th * 0.4, 5, legs_root)
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments bleus, plaques crème dessous, coraux dessus, taches sur les côtés,
#     bout de queue en bouquet de corail avec petit aileron bleu clair (ornement final).
#     Pas de section 12 : le Drake n'a pas d'ailes.
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.25, -0.35, 0.0), (0.5, -0.55, 0.25), (0.75, -0.4, 0.1), (1.0, -0.1, -0.2)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.42), (0.3, BW * 0.35), (0.6, BW * 0.26), (0.85, BW * 0.2), (1.0, BW * 0.17)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_R, s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.3, 2 * r * 0.95), mid, R, M_BODY, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_BELLY, tail_root)
    if i % TAIL_CORAL_EVERY == 0 and s < 0.9:
        coral(f"Tail_Coral_{i}", mid + d * r * 0.8, d * 1.0 + t * 0.3, (1.0 - 0.4 * s) * SC * CORAL_K * 1.0, r * 0.4,
              max(0, CORAL_DEPTH - 1), tail_root, side=1 if i % 2 else -1)
    if i % 2 == 1 and s < 0.85 and not IS_BEBE:
        for sgn in (-1, 1):
            spot(f"Tail_Spot_{i}_{sgn}", mid + side * sgn * (r * 0.99), (sgn, 0, 0), r * 0.34, M_MARK, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
CL = CLUB_SIZE
core = tip + tt_ * CL * 0.3
rock("Tail_TipCore", (CL * 1.1, CL * 1.2, CL * 0.9), core, M_CORAL2, tail_root, rot=(0, 0, 0), tx=0.85, ty=0.85)
for k in range(TAIL_TIP_N):
    a = (k - (TAIL_TIP_N - 1) / 2) * 0.5
    coral(f"Tail_TipCoral_{k}", core + Vector((0, 0, CL * 0.3)), (math.sin(a), 0.45, 1.0), CL * 1.3, CL * 0.3,
          max(0, CORAL_DEPTH - 1), tail_root, side=1 if k % 2 else -1)
if TAIL_FIN:
    for k in range(TAIL_FIN):
        a = (k - (TAIL_FIN - 1) / 2) * 0.55
        shard(f"Tail_Fin_{k}", CL * 0.7, 0.1 * SC, CL * 1.9, core + Vector((0, tt_.y * CL * 0.3, -CL * 0.1)),
              (math.sin(a) * 0.3, 1.0, 0.5 * math.cos(a) - 0.2), M_MARK if k % 2 == 0 else M_BODY2, tail_root, up=(1, 0, 0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, 1 signe fort (bois de corail), pas d'émission sauf la lueur douce des yeux.
#     Seuls éléments flottants : quelques bulles (petits prismes bleu clair) qui montent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.0 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.3 + 1.0), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        prism(f"FX_Bubble_{k}", FX_SIZE * random.uniform(0.6, 1.0), FX_SIZE * 0.3, p, (random.uniform(-1, 1), random.uniform(-1, 1), 1.0),
              M_BUBBLE, master, sides=6)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
