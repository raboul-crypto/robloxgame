import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Pousse · Adulte
#  Commun · Plante · Classique · monde 1
#  - Adulte puissant et droit : cou de 5 plaques crème, épaules et cuisses en blocs, 3 crocs par côté
#  - Signe distinctif : un PETIT ARBRE (tronc brun, cime en cubes de feuilles) pousse entre deux bois beige ramifiés
#  - Crinière et épaulières en feuilles, plaques d'écorce sur le dos, bracelets d'écorce + lianes, pierre verte au pied
#  - Grandes ailes lime à os verts et pointes crème, queue longue terminée par une grande feuille
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1101)            # même dragon à chaque exécution
TAG = "POUSSE_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 6000          # budget de triangles de ce stade et de cette rareté
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
#    Vert lime (corps + feuilles), crème (ventre, mâchoire), brun écorce (tronc, bracelets).
#    Commun : aucune émission, couleurs mates.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#78BE3C", 0.50)   # corps principal
M_BODY2 = get_mat("BodyScale", "#5FA832", 0.50)   # écailles, dessus des pattes
M_DARK  = get_mat("BodyDark",  "#2F6E22", 0.55)   # sourcils, bouche, ombres, taches
M_LEAF1 = get_mat("LeafLight", "#A6E05A", 0.45)   # feuilles claires (pousse, crinière)
M_LEAF2 = get_mat("LeafMid",   "#68B534", 0.45)   # feuilles moyennes
M_LEAF3 = get_mat("LeafDark",  "#3B8A28", 0.50)   # feuilles sombres
M_CREAM = get_mat("Belly",     "#EFE3B6", 0.55)   # ventre en plaques, menton
M_HORN  = get_mat("Horn",      "#DDC79A", 0.50)   # cornes / bois
M_BARK  = get_mat("Bark",      "#7E5430", 0.75)   # tronc, bracelets d'écorce
M_BARK2 = get_mat("BarkDark",  "#51351D", 0.80)   # écorce sombre
M_CLAW  = get_mat("Claw",      "#F6EEDA", 0.35)   # griffes, crocs, pointes d'aile
M_WING  = get_mat("Membrane",  "#8DC947", 0.55)   # membrane des ailes
M_BONE  = get_mat("WingBone",  "#3F8626", 0.55)   # os des ailes
M_WHITE = get_mat("EyeWhite",  "#F4F4EA", 0.30)
M_IRIS  = get_mat("Iris",      "#7FE03A", 0.25)
M_BLACK = get_mat("Black",     "#0B0F08", 0.30)
M_GEM   = get_mat("Gem",       "#B6F06E", 0.12)   # petite pierre verte (non émissive)
LEAFS = [M_LEAF1, M_LEAF2, M_LEAF3]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
BW = 2.5
BH = 2.3
LEG_H = 2.1
TORSO_L = 4.3
NECK_L = 3.6
NECK_LEAN = 0.55
NECK_N = 6
NECK_R = (0.85, 1.15)
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
CHEEK_N = 3
MANE_RINGS = 2
MANE_N = 12
BELLY_N = 6
FLANK_ROWS = 3
FLANK_COLS = 5
SPOTS = 9
NECK_LEAF_X = (-0.5, 0.0, 0.5)
CREST_N = 6
SHOULDER_LEAVES = 4
BRACER_K = 0.62
LEG_BEV = 1
TAIL_SCALES = True
TAIL_BEV_N = 4
BELLY_SIDES = True
VINES = True
THIGH_LEAVES = 2
GEM = True
WING_SPAN = 6.6
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.32
WING_FINGERS = 3
TAIL_L = 6.5
TAIL_STEP = 0.8
TAIL_LEAF = 2.2
FX_N = 12
FX_SIZE = 0.7


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
HEAD_PITCH = 7                                   # degrés : la tête regarde un peu vers le bas
TAIL_START = Vector((0, TL * 0.42, ZC - 0.12 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, bois, tronc, branches)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def leaf_plate(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Feuille en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
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

def hleaf(name, w, Ln, loc, direction, mat, up=(0, 0, 1), t=0.08):
    return leaf_plate("Head_" + name, hv(loc), direction, Ln * HS, w * HS, mat, H, up, t * HS)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_LEAF1)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris, pupille (ronde + reflet pour bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.88, 0.95, 0.68, 0.8, 0.4, 0.56
else:
    EW, EH, IW, IH, PW, PH = 0.55, 0.62, 0.4, 0.52, 0.1, 0.48
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.22), (sgn * 1.07, ey - 0.15, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, ey + 0.12, ez - 0.2), mat=M_WHITE)
    else:
        # sourcils sévères, inclinés vers le museau
        hbox(f"Brow_{sgn}", (0.14, 0.95, 0.22), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0),
             mat=M_DARK, bevel=0.02)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles en feuille et feuilles de joue
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.25, (sgn * 0.8, 0.5, 0.3), (sgn * 1, 0.6, 0.5), M_LEAF1)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.45, 0.08, 0.85 - 0.1 * k, (sgn * 0.85, -0.35 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick(LEAFS, [3, 4, 2]))

# Collerette de feuilles autour de l'arrière du crâne
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hleaf(f"Mane_{ring_i}_{k}", 0.75 - ring_i * 0.1, 1.2 + ring_i * 0.2 + random.random() * 0.3,
              loc, direction, pick(LEAFS, [4, 3, 2]), up=tuple(rad))

# Cornes beige recourbées vers l'arrière (bébé : courtes ; ado : longues ; adulte : bois ramifiés)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.2), (sgn * 0.7, 0.9, 1.6)],
               0.32, 0.13, M_HORN)
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.6, 0.25, 0.78), (sgn * 0.85, 0.45, 1.4), (sgn * 0.85, 0.95, 1.95),
                               (sgn * 0.65, 1.55, 2.2)], 0.36, 0.14, M_HORN)
    else:
        a0, a1 = Vector((sgn * 0.6, 0.3, 0.78)), Vector((sgn * 0.95, 0.65, 1.7))
        a2, a3 = Vector((sgn * 1.25, 1.25, 2.45)), Vector((sgn * 1.3, 1.95, 3.0))
        hchain(f"Antler_{sgn}", [a0, a1, a2, a3], 0.4, 0.16, M_HORN)
        bar(f"Head_AntlerTine1_{sgn}", hv(a1), hv((sgn * 1.55, 0.25, 2.35)), 0.2 * HS, M_HORN, H)
        bar(f"Head_AntlerTine2_{sgn}", hv(a2), hv((sgn * 1.95, 1.0, 3.1)), 0.18 * HS, M_HORN, H)
        bar(f"Head_AntlerTine3_{sgn}", hv(a1.lerp(a2, 0.5)), hv((sgn * 0.8, 0.1, 2.75)), 0.16 * HS, M_HORN, H)

# Signe distinctif : la POUSSE sur le crâne (bébé : 2 feuilles ; ado : tige + 3 feuilles ; adulte : petit arbre)
if IS_BEBE:
    hchain("SproutStem", [(0, 0.2, 0.7), (0, 0.2, 1.3)], 0.15, 0.12, M_BARK)
    for sgn in (-1, 1):
        hshard(f"SproutLeaf_{sgn}", 0.6, 0.06, 1.0, (0, 0.2, 1.25), (sgn * 0.8, 0.0, 0.65), M_LEAF1, up=(0, 1, 0))
elif IS_ADO:
    hchain("SproutStem", [(0, 0.2, 0.7), (0.05, 0.15, 1.3), (0.05, 0.1, 1.75)], 0.18, 0.12, M_BARK)
    for sgn in (-1, 1):
        hshard(f"SproutLeaf_{sgn}", 0.8, 0.07, 1.5, (0.05, 0.1, 1.7), (sgn * 0.75, -0.1, 0.7), M_LEAF1, up=(0, 1, 0))
        hshard(f"SproutLow_{sgn}", 0.5, 0.06, 0.9, (0.03, 0.15, 1.25), (sgn * 0.9, 0.1, 0.4), M_LEAF2, up=(0, 1, 0))
    hshard("SproutBud", 0.45, 0.06, 0.85, (0.05, 0.1, 1.75), (0, 0, 1), M_LEAF2, up=(0, 1, 0))
else:
    hchain("Trunk", [(0, 0.25, 0.7), (0.05, 0.18, 1.6), (-0.08, 0.25, 2.4), (0, 0.2, 3.0)], 0.32, 0.16, M_BARK)
    hchain("BranchR", [(0.02, 0.2, 1.7), (0.55, 0.15, 2.1), (1.0, 0.1, 2.5)], 0.14, 0.09, M_BARK)
    hchain("BranchL", [(-0.05, 0.25, 2.1), (-0.5, 0.3, 2.5), (-0.8, 0.3, 2.8)], 0.12, 0.08, M_BARK)
    hbox("BranchLeafR", (0.6, 0.6, 0.45), (1.08, 0.1, 2.65), rot=(0, 15, 25), mat=M_LEAF1)
    hbox("BranchLeafL", (0.5, 0.5, 0.4), (-0.85, 0.3, 2.95), rot=(0, -15, -20), mat=M_LEAF2)
    hbox("Canopy_0", (1.35, 1.3, 1.1), (0, 0.2, 3.3), mat=M_LEAF2, bevel=0.08)
    hbox("Canopy_1", (0.95, 0.95, 0.9), (0.8, 0.1, 3.15), rot=(0, 0, 20), mat=M_LEAF1)
    hbox("Canopy_2", (0.95, 0.95, 0.9), (-0.75, 0.3, 3.1), rot=(0, 0, -15), mat=M_LEAF3)
    hbox("Canopy_3", (0.85, 0.85, 0.8), (0.1, -0.6, 3.15), rot=(0, 10, 30), mat=M_LEAF1)
    hbox("Canopy_4", (0.85, 0.85, 0.8), (0.0, 0.85, 3.2), rot=(0, 0, 12), mat=M_LEAF2)
    hbox("Canopy_5", (0.95, 0.95, 0.85), (0.15, 0.1, 4.0), rot=(0, 20, 15), mat=M_LEAF1)
    hbox("Canopy_6", (0.65, 0.65, 0.6), (-0.45, -0.2, 3.8), rot=(15, 0, 35), mat=M_LEAF3)
    hbox("Canopy_7", (0.65, 0.65, 0.6), (0.55, 0.45, 3.85), rot=(0, 15, -20), mat=M_LEAF2)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre, flancs, crête, épaulières
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les écailles sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron crème sur le poitrail + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Écailles-feuilles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_LEAF2, M_BODY2]), body_root, up=(sgn, 0, 0))

# Taches vert foncé sur le dos et les flancs
for k in range(SPOTS):
    y = random.uniform(-TL * 0.4, TL * 0.45)
    if k % 2 == 0:
        B(f"Body_Spot_{k}", (random.uniform(0.3, 0.5) * SC, random.uniform(0.3, 0.5) * SC, 0.06),
          (random.uniform(-0.3, 0.3) * BW, y, ZC + BH / 2 - 0.01), mat=M_DARK, parent=body_root)
    else:
        sgn = random.choice((-1, 1))
        B(f"Body_Spot_{k}", (0.06, random.uniform(0.35, 0.55) * SC, random.uniform(0.3, 0.45) * SC),
          (sgn * (half_w(y) + 0.0), y, ZC + BH * random.uniform(-0.05, 0.3)), mat=M_DARK, parent=body_root)

# Cou : courbe lissée de la tête vers le torse, un segment vert + une plaque crème par maillon
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
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_CREAM, body_root)
    # crête de feuilles sur la nuque
    for k, amt in enumerate(NECK_LEAF_X):
        leaf_plate(f"Body_NeckLeaf_{i}_{k}", mid + d * r * 0.8 + side * amt * r, d + t * 0.9 + side * amt * 0.5,
                   (1.0 + 0.5 * (1 - s)) * SC + random.random() * 0.3, 0.8 * SC,
                   pick(LEAFS, [3, 4, 2]), body_root, up=tuple(d), t=0.1 * SC)
    for sgn in (-1, 1):
        if i % 2 == 0 or IS_ADULTE:
            shard(f"Body_NeckSide_{i}_{sgn}", 0.6 * SC, 0.1 * SC, 0.75 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, pick(LEAFS, [3, 4, 2]), body_root)

# Crête dorsale en feuilles sur le torse
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.85 * SC, 0.12 * SC, (1.05 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), pick(LEAFS, [3, 4, 2]), body_root, up=(1, 0, 0))

# Épaulières : grappe de feuilles sur chaque épaule (+ plaques d'écorce chez l'adulte)
for sgn in (-1, 1):
    for k in range(SHOULDER_LEAVES):
        shard(f"Body_ShoulderLeaf_{sgn}_{k}", 0.45 * SC, 0.08 * SC, (0.95 - 0.1 * k) * SC,
              (sgn * BW * (0.42 + 0.03 * k), -TL * 0.2 + 0.2 * k * SC, ZC + BH * (0.4 - 0.12 * k)),
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.5 * k), pick(LEAFS, [3, 4, 2]), body_root)
    if IS_ADULTE:
        wedge(f"Body_BarkPlate_{sgn}", (BW * 0.5, TL * 0.3, 0.28), (sgn * BW * 0.3, -TL * 0.1, ZC + BH / 2 + 0.02),
              (0, sgn * 8, 0), M_BARK, body_root, top_x=0.85, top_y=0.85, bevel=0.04)
        B(f"Body_BarkPlateB_{sgn}", (BW * 0.34, TL * 0.2, 0.22), (sgn * BW * 0.32, TL * 0.13, ZC + BH / 2 - 0.02),
          (0, sgn * 6, 0), M_BARK2, body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, bracelet d'écorce, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, y + (th * 0.15 if hind else 0), FOOT_H + SHIN_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    # Bracelet d'écorce + lianes
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, y + (th * 0.15 if hind else 0), FOOT_H + SHIN_H * 0.5),
        mat=M_BARK, parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.12, th * 1.16, 0.1 * SC), (x, y + (th * 0.15 if hind else 0), FOOT_H + SHIN_H * 0.5 + bh_ / 2),
      mat=M_BARK2, parent=legs_root)
    if VINES:
        for k in (-1, 1):
            B(f"{name}_Vine_{k}", (th * 0.95, 0.08 * SC, 0.1 * SC),
              (x, y + (th * 0.15 if hind else 0) - th * 0.56, FOOT_H + SHIN_H * 0.5 + k * bh_ * 0.15),
              rot=(0, k * 35, 0), mat=M_LEAF3, parent=legs_root)
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + (th * 0.15 if hind else 0), FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + (th * 0.15 if hind else 0) - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    # Feuilles sur la cuisse
    for k in range(THIGH_LEAVES):
        shard(f"{name}_Leaf_{k}", 0.4 * SC, 0.07 * SC, (0.8 - 0.12 * k) * SC,
              (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
              (sgn * 0.8, 0.5, -0.6), pick(LEAFS, [3, 4, 2]), legs_root)
    if hind and GEM and sgn == 1:
        crystal(f"{name}_Gem", 0.16 * SC, 0.12 * SC, 0.16 * SC, (x + sgn * th * 0.56, fy + th * 0.2, FOOT_H * 0.55),
                (sgn, 0, 0), M_GEM, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES membraneuses (os verts, membrane lime, pointes crème)
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_BONE, M_WING, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.55, memb_t=WING_BONE * 0.45, claw_mat=M_CLAW)
    # pointes crème au bout de chaque doigt (mêmes formules que wing())
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tip = wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                              -WING_SPAN * (0.05 + 0.55 * f)))
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.7, WING_BONE * 1.2, WING_SPAN * 0.13, tip, tip - wrist, M_CLAW, wings_root)
    shard(f"Wings_{sgn}_WristSpike", WING_BONE * 1.8, WING_BONE * 1.3, WING_SPAN * 0.15, wrist, (sgn * 0.5, 0.2, 1), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques crème, crête de feuilles, feuille finale
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.35, 0.0), (0.45, -0.7, 0.3), (0.7, -0.62, 0.15), (0.9, -0.15, -0.25), (1.0, 0.45, -0.4)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.42), (0.3, BW * 0.36), (0.6, BW * 0.26), (0.85, BW * 0.17), (1.0, BW * 0.11)]
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    shard(f"Tail_Crest_{i}", 0.9 * r + 0.2, 0.1 * SC, 0.5 * SC + r * 0.8, mid + d * r * 0.85, d + t * 0.7,
          pick(LEAFS, [3, 4, 2]), tail_root, up=(1, 0, 0))
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t, 
                  pick([M_BODY2, M_LEAF2]), tail_root, up=(sgn, 0, 0))
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_BARK, tail_root)
leaf_plate("Tail_TipLeaf_A", tip, tt_ + td_ * 0.25, TAIL_LEAF, TAIL_LEAF * 0.55, M_LEAF1, tail_root, up=tuple(ts_), t=0.12 * SC)
leaf_plate("Tail_TipLeaf_B", tip, tt_ + td_ * 0.25, TAIL_LEAF * 0.85, TAIL_LEAF * 0.45, M_LEAF2, tail_root, up=tuple(td_), t=0.12 * SC)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, aucune émission. Détails = écailles, plaques, crête, griffes.
#     Seuls éléments flottants : quelques feuilles qui tombent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55, pick([M_LEAF1, M_LEAF2]),
                   master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
