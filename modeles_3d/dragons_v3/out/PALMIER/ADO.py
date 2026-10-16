import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Palmier · Ado
#  Commun · Plante · Classique · monde 3
#  - Ado élancé : cou de 5 plaques annelées, crocs, sourcils, cornes brunes recourbées
#  - Signe distinctif : crinière de 6 longues palmes + petites palmes devant
#  - Ventre en tronc (plaques beige + bandes brunes), bracelets annelés aux pattes, queue annelée
#  - Ailes faites de 4 palmes à folioles, queue terminée par 2 noix de coco et une petite touffe de palmes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3101)            # même dragon à chaque exécution
TAG = "PALMIER_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
#    Vert vif (corps + palmes), beige (ventre, anneaux de tronc), brun (bandes, noix de coco, cornes).
#    Commun : aucune émission, couleurs mates.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#5FB02E", 0.50)   # corps principal
M_BODY2 = get_mat("BodyScale", "#4A9526", 0.50)   # écailles, dessus des pattes
M_DARK  = get_mat("BodyDark",  "#2F5A1A", 0.55)   # sourcils, bouche, narines
M_LEAF1 = get_mat("FrondLight","#86D03F", 0.45)   # palmes claires
M_LEAF2 = get_mat("FrondMid",  "#5FB02E", 0.45)   # palmes moyennes
M_LEAF3 = get_mat("FrondDark", "#3F8326", 0.50)   # palmes sombres
M_CREAM = get_mat("Belly",     "#E3C593", 0.55)   # ventre en plaques, anneaux de tronc, menton
M_RING  = get_mat("TrunkRing", "#8A5E30", 0.70)   # bandes brunes de tronc de palmier
M_HORN  = get_mat("Horn",      "#7A4A28", 0.55)   # cornes brunes
M_NUT   = get_mat("Coconut",   "#6B4226", 0.65)   # noix de coco
M_NUT2  = get_mat("CoconutCap","#47291A", 0.80)   # calotte fibreuse de la noix
M_CLAW  = get_mat("Claw",      "#F4ECD8", 0.35)   # griffes, crocs, pointes de corne
M_BONE  = get_mat("WingBone",  "#4A7F2E", 0.55)   # bras d'aile et nervures des palmes
M_WHITE = get_mat("EyeWhite",  "#F4F4EA", 0.30)
M_IRIS  = get_mat("Iris",      "#D8902C", 0.25)   # iris ambre
M_BLACK = get_mat("Black",     "#0B0F08", 0.30)
LEAFS = [M_LEAF1, M_LEAF2, M_LEAF3]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
BW = 1.9
BH = 1.8
LEG_H = 1.7
TORSO_L = 3.6
NECK_L = 2.6
NECK_LEAN = 0.45
NECK_N = 5
NECK_R = (0.7, 0.9)
HEAD_SCALE = 0.98
SNOUT_K = 1.0
FANGS = 2
CHEEK_N = 1
MANE_FRONDS = 6
MANE_LEN = 2.6
MANE_DROOP = 0.5
MANE_LEAFLETS = 3
MANE_LEAFLEN = 0.7
MANE_SMALL = 0
BELLY_N = 5
PLASTRON_BANDS = 2
BACK_BANDS = 4
FLANK_ROWS = 2
FLANK_COLS = 4
NECK_BANDS = True
CREST_N = 5
SHOULDER_LEAVES = 3
SHOULDER_FROND = False
BRACER_K = 0.55
LEG_RINGS = 1
LEG_BEV = 1
TAIL_BEV_N = 3
BELLY_SIDES = False
THIGH_LEAVES = 1
WING_SPAN = 5.4
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.26
WING_FRONDS = 3
WING_LEAFLETS = 4
WING_LEAFLEN = 0.9
WING_DROOP = 0.35
TAIL_L = 5.0
TAIL_STEP = 0.7
COCONUTS = 2
TAIL_TUFT = 3
TAIL_TUFT_L = 1.5
FX_N = 3
FX_SIZE = 0.6


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
    """Suite de barres qui s'affinent (cornes, nervures)."""
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

def frond(name, base, direction, length, droop, n, leaf_len, parent, rib_mat=None, mats=None, rib_t=0.12,
          side_ref=(0, 0, 1), t=0.05):
    """PALME : nervure centrale en 2 barres qui retombe en arc, + n paires de folioles
    (plaques triangulaires) de chaque côté. 'droop' = affaissement (fraction de la longueur)."""
    base = Vector(base)
    d = Vector(direction).normalized()
    down = Vector((0, 0, -1))
    rib_mat = rib_mat or M_BONE
    mats = mats or [M_LEAF1, M_LEAF2]
    def P(u):
        return base + d * (length * u) + down * (droop * length * u * u)
    bar(f"{name}_RibA", P(0), P(0.5), rib_t, rib_mat, parent)
    bar(f"{name}_RibB", P(0.5), P(1.0), rib_t * 0.65, rib_mat, parent)
    side = d.cross(Vector(side_ref))
    if side.length < 1e-3:
        side = d.cross(Vector((0, 1, 0)))
    side.normalized()
    side = side.normalized()
    for k in range(n):
        u = 0.22 + 0.74 * k / max(1, n - 1)
        rp = P(u)
        tan = (P(min(1.0, u + 0.05)) - P(max(0.0, u - 0.05))).normalized()
        ll = leaf_len * (1.0 - 0.45 * u)
        for sg in (-1, 1):
            tip = rp + side * (sg * ll) + tan * (ll * 0.55) + down * (ll * 0.30)
            plate(f"{name}_Leaflet_{k}_{sg}", [rp - tan * ll * 0.22, tip, rp + tan * ll * 0.35], t,
                  mats[(k + (sg > 0)) % len(mats)], parent)

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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_LEAF1)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
# Petite bande de tronc brune sur le museau (écho des anneaux du ventre)
hbox("SnoutBand", (1.0, 0.16, 0.14), (0, -0.6 - 0.55 * SNOUT_K, 0.24), mat=M_RING)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris ambre, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
        hbox(f"Brow_{sgn}", (0.14, 0.95, 0.22), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0),
             mat=M_DARK, bevel=0.02)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles en folioles et petites feuilles de joue
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.6, 0.1, 1.1, (sgn * 0.8, 0.5, 0.3), (sgn * 1, 0.6, 0.5), M_LEAF1)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.4, 0.08, 0.8 - 0.1 * k, (sgn * 0.85, -0.35 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick(LEAFS, [3, 4, 2]))

# Cornes brunes recourbées vers l'arrière, pointes beige (ado / adulte : plus longues)
for sgn in (-1, 1):
    if IS_BEBE:
        pts = [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.15), (sgn * 0.72, 0.85, 1.45)]
        hchain(f"Horn_{sgn}", pts, 0.34, 0.14, M_HORN)
    elif IS_ADO:
        pts = [(sgn * 0.6, 0.25, 0.78), (sgn * 0.85, 0.45, 1.4), (sgn * 0.85, 0.95, 1.9), (sgn * 0.68, 1.5, 2.1)]
        hchain(f"Horn_{sgn}", pts, 0.36, 0.14, M_HORN)
        hshard(f"HornTip_{sgn}", 0.2, 0.2, 0.45, pts[-1], (0, 0.6, 0.3), M_CLAW)
    else:
        pts = [(sgn * 0.6, 0.3, 0.78), (sgn * 0.95, 0.55, 1.6), (sgn * 1.1, 1.1, 2.35), (sgn * 0.95, 1.8, 2.7)]
        hchain(f"Horn_{sgn}", pts, 0.42, 0.16, M_HORN)
        hshard(f"HornTip_{sgn}", 0.24, 0.24, 0.6, pts[-1], (0, 0.7, 0.3), M_CLAW)

# SIGNE DISTINCTIF : la CRINIÈRE DE PALMES (éventail de palmes qui retombent derrière le crâne)
for k in range(MANE_FRONDS):
    f = k / max(1, MANE_FRONDS - 1)
    a = math.radians(-78 + 156 * f)
    dirv = Vector((math.sin(a) * 0.9, 0.35 + 0.2 * (1 - abs(2 * f - 1)), math.cos(a) * 0.8 + 0.5))
    ln = (MANE_LEN * (1.0 if 0.2 < f < 0.8 else 0.8)) * HS
    frond(f"Head_Mane_{k}", hv((math.sin(a) * 0.5, 0.45, 0.55 + 0.1 * math.cos(a))), dirv, ln, MANE_DROOP,
          MANE_LEAFLETS, MANE_LEAFLEN * HS, H, side_ref=(0, 1, 0) if abs(math.sin(a)) < 0.3 else (0, 0, 1),
          rib_t=0.16 * HS, mats=[M_LEAF1, M_LEAF2] if k % 2 else [M_LEAF2, M_LEAF1])
# Petit bouquet de palmes courtes devant la crinière (adulte / ado)
for k in range(MANE_SMALL):
    sgn = -1 if k % 2 == 0 else 1
    hshard(f"Mane_Small_{k}", 0.55, 0.08, 1.2 - 0.1 * (k // 2), (sgn * 0.45, 0.1 + 0.1 * (k // 2), 0.8),
           (sgn * 0.5, 0.45, 1.0), pick(LEAFS, [4, 3, 2]), up=(0, 1, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques annelées, ventre en tronc, flancs, crête, épaulières
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

# Plastron beige annelé de 2 bandes brunes
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for j in range(PLASTRON_BANDS):
    B(f"Body_PlastronBand_{j}", (BW * 0.86, 0.38 * SC, 0.09 * SC),
      (0, -TL * 0.5 + 0.04, ZC - BH * 0.1 + BH * (0.2 - 0.2 * j)), mat=M_RING, parent=body_root)
# Ventre en TRONC DE PALMIER : plaques beige séparées par des bandes brunes
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.80
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    yb = y + (TL * 0.86) / BELLY_N * 0.5
    if i < BELLY_N - 1:
        B(f"Body_BellyBand_{i}", (BW * 0.84, 0.14 * SC, 0.22 * SC), (0, yb, ZC - BH / 2 + 0.03), mat=M_RING, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Bandes brunes en travers du dos (anneaux de tronc)
for k in range(BACK_BANDS):
    y = -TL * 0.38 + (TL * 0.8) * (k + 0.5) / BACK_BANDS
    B(f"Body_BackBand_{k}", (BW * 0.62, 0.16 * SC, 0.06), (0, y, ZC + BH / 2 - 0.005), mat=M_RING, parent=body_root)

# Écailles-feuilles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_LEAF2, M_BODY2]), body_root, up=(sgn, 0, 0))

# Cou : courbe lissée, un segment vert + une plaque beige + une bande brune par maillon
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
    if NECK_BANDS:
        B(f"Body_NeckBand_{i}", (2 * r * 0.84, Ln * 0.12, 0.25 * SC), p1 - d * (r * 0.95), R, M_RING, body_root)
    for sgn in (-1, 1):
        if i % 2 == 0:
            shard(f"Body_NeckSide_{i}_{sgn}", 0.5 * SC, 0.1 * SC, 0.7 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, pick(LEAFS, [3, 4, 2]), body_root)

# Crête dorsale en palmes (éclats verts)
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.8 * SC, 0.12 * SC, (1.0 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.5, 1), pick(LEAFS, [3, 4, 2]), body_root, up=(1, 0, 0))

# Épaulières : petites palmes sur chaque épaule
for sgn in (-1, 1):
    for k in range(SHOULDER_LEAVES):
        shard(f"Body_ShoulderLeaf_{sgn}_{k}", 0.45 * SC, 0.08 * SC, (0.95 - 0.1 * k) * SC,
              (sgn * BW * (0.42 + 0.03 * k), -TL * 0.2 + 0.2 * k * SC, ZC + BH * (0.4 - 0.12 * k)),
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.5 * k), pick(LEAFS, [3, 4, 2]), body_root)
    if SHOULDER_FROND:
        frond(f"Body_ShoulderFrond_{sgn}", (sgn * BW * 0.4, -TL * 0.2, ZC + BH * 0.46), (sgn * 0.7, 0.35, 0.8),
              2.1 * SC, 0.5, 3, 0.55 * SC, body_root, rib_t=0.1 * SC, side_ref=(0, 1, 0))

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, bracelet-anneau de tronc, pied, 3 doigts + 3 griffes
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
    # Bracelet : anneaux de tronc beige et brun
    bh_ = SHIN_H * BRACER_K
    yy = y + (th * 0.15 if hind else 0)
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, yy, FOOT_H + SHIN_H * 0.5),
        mat=M_CREAM, parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    for j in range(LEG_RINGS):
        zz = FOOT_H + SHIN_H * 0.5 + bh_ * (0.5 - (j + 0.5) / LEG_RINGS) * 0.9 + bh_ * 0.03
        B(f"{name}_BracerRing_{j}", (th * 1.12, th * 1.16, 0.09 * SC), (x, yy, zz), mat=M_RING, parent=legs_root)
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
    # Palmes sur la cuisse
    for k in range(THIGH_LEAVES):
        shard(f"{name}_Leaf_{k}", 0.4 * SC, 0.07 * SC, (0.8 - 0.12 * k) * SC,
              (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
              (sgn * 0.8, 0.5, -0.6), pick(LEAFS, [3, 4, 2]), legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES FAITES DE PALMES : bras + avant-bras, puis un éventail de palmes à folioles
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    elbow = root + Vector((sgn * WING_SPAN * 0.36, WING_SPAN * WING_SWEEP * 0.25, WING_SPAN * WING_LIFT * 0.9 * 0.55))
    wrist = root + Vector((sgn * WING_SPAN * 0.58, WING_SPAN * WING_SWEEP * 0.45, WING_SPAN * WING_LIFT * 0.55))
    link(f"Wings_{sgn}_Arm", root, elbow, WING_BONE * 1.3, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    link(f"Wings_{sgn}_Fore", elbow, wrist, WING_BONE, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    # membrane de raccord entre l'épaule et le flanc
    plate(f"Wings_{sgn}_Root", [root, elbow, wrist, root + Vector((sgn * 0.1, TL * 0.3, -BH * 0.25))],
          WING_BONE * 0.4, M_LEAF2, wings_root)
    for k in range(WING_FRONDS):
        f = k / max(1, WING_FRONDS - 1)
        ang = math.radians(52 - 70 * f)                       # de la palme du haut à celle du bas
        dirv = Vector((sgn * math.cos(ang) * 0.85, 0.2 + 0.75 * f, math.sin(ang)))
        frond(f"Wings_{sgn}_Frond_{k}", wrist, dirv, WING_SPAN * (0.78 - 0.1 * abs(f - 0.4)), WING_DROOP,
              WING_LEAFLETS, WING_LEAFLEN, wings_root, rib_t=WING_BONE * 0.8,
              mats=[M_LEAF1, M_LEAF2, M_LEAF1, M_LEAF3][(k % 2):][:2] if k % 2 else [M_LEAF2, M_LEAF1], t=WING_BONE * 0.25)
    shard(f"Wings_{sgn}_WristClaw", WING_BONE * 1.6, WING_BONE * 1.2, WING_SPAN * 0.14, wrist, (sgn * 0.5, 0.2, 1), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments beige annelés de brun, bande dorsale verte, noix de coco + touffe
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
    # segment beige (tronc), bande brune au joint, bande dorsale verte
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.25, 2 * r * 0.95), mid, R, M_CREAM, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    B(f"Tail_Ring_{i}", (2 * r * 1.07, Ln * 0.2, 2 * r * 1.02), p1, R, M_RING, tail_root)
    B(f"Tail_Stripe_{i}", (2 * r * 0.62, Ln * 1.15, 0.14 * SC), mid + d * (r * 0.93), R, M_BODY, tail_root)
    if i % 2 == 0 and s < 0.85:
        shard(f"Tail_Crest_{i}", 0.8 * r + 0.2, 0.1 * SC, 0.5 * SC + r * 0.8, mid + d * r * 0.95, d + t * 0.7,
              pick(LEAFS, [3, 4, 2]), tail_root, up=(1, 0, 0))
# Bout de queue : noix de coco brunes (calotte fibreuse) + touffe de palmes
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_RING, tail_root)
NR = BW * 0.2
for k in range(COCONUTS):
    a = math.radians(k * 360 / max(1, COCONUTS) + 20)
    off = (ts_ * math.cos(a) + td_ * math.sin(a)) * (NR * 0.7 if COCONUTS > 1 else 0)
    c = tip + tt_ * NR * 1.1 + off
    prism(f"Tail_Coconut_{k}", NR, NR * 2.0, c, tt_, M_NUT, tail_root, sides=8, top=0.82)
    if not IS_BEBE:
      prism(f"Tail_CoconutCap_{k}", NR * 0.8, NR * 0.5, c + tt_ * NR * 0.95, tt_, M_NUT2, tail_root, sides=8, top=0.5)
for k in range(TAIL_TUFT):
    a = math.radians(k * 360 / TAIL_TUFT + 15)
    dv = tt_ * 0.5 + td_ * (math.sin(a) * 0.8 + 0.35) + ts_ * math.cos(a) * 0.8
    frond(f"Tail_Tuft_{k}", tip + tt_ * NR * 1.4, dv, TAIL_TUFT_L, 0.7, 2, TAIL_TUFT_L * 0.3,
          tail_root, rib_t=0.1 * SC, side_ref=tuple(td_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, aucune émission. Détails = ventre-tronc en plaques, écailles, crête, griffes.
#     Seuls éléments flottants : quelques palmes qui tombent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.45, pick([M_LEAF1, M_LEAF2]),
                   master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
