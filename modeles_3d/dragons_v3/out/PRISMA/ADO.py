import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Prisma · Ado
#  Exclusif · Vol · Classique · monde exclusif (payant)
#  - Ado nacré plus musclé : cou de 5 maillons colorés, petits crocs, yeux sérieux, cornes à pointes de cristal
#  - Bandes d'arc-en-ciel sur le dos, la queue et le cou : une couleur différente par segment ; écailles prismatiques sur les flancs
#  - Ailes irisées en anneaux de couleurs, traînée arc-en-ciel derrière les bouts d'aile, halo de 7 éclats
#  - Rendu Exclusif à mi-puissance : tout ce qui est coloré est émissif, 28 cristaux flottants
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(7707)            # même dragon à chaque exécution
TAG = "PRISMA_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 11000          # budget de triangles de ce stade et de cette rareté
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
#    Base nacrée blanc / lilas + 8 couleurs d'arc-en-ciel émissives qui défilent segment par segment.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",     "#EEEAF8", 0.40, 0.05)   # corps nacré
M_BODY2 = get_mat("BodyScale","#CFC6EC", 0.40, 0.10)   # dessus des pattes, plaques de dos
M_DARK  = get_mat("BodyDark", "#7F76B4", 0.50)         # sourcils, bouche, narines
M_CREAM = get_mat("Belly",    "#FFFFFF", 0.45)         # ventre en plaques, menton
M_HORN  = get_mat("Horn",     "#F8F6FF", 0.35, 0.10)   # base des cornes
M_CLAW  = get_mat("Claw",     "#FFFFFF", 0.30)         # griffes, crocs
M_BONE  = get_mat("WingBone", "#F4F1FF", 0.40, 0.10)   # os des ailes
M_WHITE = get_mat("EyeWhite", "#F4F4F8", 0.30)
M_IRIS  = get_mat("Iris",     "#5AB8FF", 0.15, 0.0, emission="#5AB8FF", strength=3.0)   # iris lumineux
M_BLACK = get_mat("Black",    "#0A0A12", 0.30)
M_GEM   = get_mat("Gem",      "#FFFFFF", 0.10, 0.0, emission="#FFFFFF", strength=3.5)   # gemmes blanches
RB_HEX = ["#FF4D5E", "#FF9A3C", "#FFE14A", "#4DE07A", "#3FD8FF", "#5A7BFF", "#B070FF", "#FF5FD0"]
RB   = [get_mat(f"Rb{i}",  h, 0.25, 0.10, emission=h, strength=1.6) for i, h in enumerate(RB_HEX)]    # écailles, crêtes
RBG  = [get_mat(f"RbG{i}", h, 0.12, 0.0,  emission=h, strength=3.2) for i, h in enumerate(RB_HEX)]    # cristaux vifs
RBW  = [get_mat(f"RbW{i}", h, 0.30, 0.0,  emission=h, strength=1.1, alpha=0.8) for i, h in enumerate(RB_HEX)]  # membranes
def rb(i):  return RB[int(i) % 8]
def rbg(i): return RBG[int(i) % 8]
def rbw(i): return RBW[int(i) % 8]

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
CHEEK_N = 2
MANE_RINGS = 2
MANE_N = 12
BELLY_N = 5
FLANK_ROWS = 3
FLANK_COLS = 5
STRIPES = 11
CREST_N = 6
SHOULDER_N = 4
BRACER_K = 0.55
LEG_BEV = 1
TAIL_SCALES = True
TAIL_BEV_N = 3
BELLY_SIDES = True
HALO_N = 7
WING_SPAN = 5.6
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.26
WING_FINGERS = 3
WING_BANDS = 4
TRAIL_L = 3.4
TAIL_L = 5.0
TAIL_STEP = 0.65
TAIL_FAN = 7
FX_N = 34
FX_SIZE = 0.55
HORN_STYLE = 1
CREST_K = 0.85         # taille de la crinière et du halo de cristaux (bébé plus petit)

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

SMALL_BEV = 0.04     # petit biseau sur les plaques (0 = aucun, économise des triangles)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=None):
    return box(name, size, loc, rot, mat, parent, SMALL_BEV * SC if bevel is None else bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, branches)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

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

def hcrystal(name, r, h, tip, loc, direction, mat, up=(0, 0, 1)):
    return crystal("Head_" + name, r * HS, h * HS, tip * HS, hv(loc), direction, mat, H, up)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne, museau, arête du museau (bande prismatique), mâchoire, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
BR_N = 4 if not IS_BEBE else 3
for k in range(BR_N):   # arête du museau : bandes de couleurs différentes
    sl = 1.7 * SNOUT_K / BR_N
    hbox(f"SnoutBridge_{k}", (0.9, sl * 0.96, 0.12), (0, -0.6 - 0.1 - sl * (k + 0.5), 0.22 - 0.02 * k), mat=rb(k + 3))
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_DARK)

# Yeux : blanc, iris bleu lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
             mat=rb(5 if sgn < 0 else 6), bevel=0.02)

# Crocs
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles prismatiques et pointes de joue (une couleur par pointe)
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.25, (sgn * 0.8, 0.5, 0.3), (sgn * 1, 0.6, 0.5), rbw(2 + sgn))
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.45, 0.08, 0.85 - 0.1 * k, (sgn * 0.85, -0.35 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), rb(k * 2 + (0 if sgn < 0 else 1)))

# Gemme frontale (signe du Prisma) dans un petit support nacré
hbox("GemSocket", (0.55, 0.45, 0.14), (0, -0.62, 0.7), rot=(-20, 0, 0), mat=M_HORN, bevel=0.03)
hcrystal("Gem", 0.2, 0.14, 0.22, (0, -0.74, 0.74), (0, -0.4, 1), M_GEM)

# Crinière de cristaux : éventail de 2 rangées derrière le crâne, une couleur d'arc-en-ciel par éclat
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hshard(f"Mane_{ring_i}_{k}", (0.7 - ring_i * 0.1) * max(0.7, CREST_K), 0.12, (1.3 + ring_i * 0.2 + random.random() * 0.3) * CREST_K,
               loc, direction, rb(k + ring_i * 3), up=tuple(rad))

# Cornes nacrées à pointes prismatiques (bébé : courtes ; ado : longues ; adulte : ramifiées)
for sgn in (-1, 1):
    if IS_BEBE:
        pts = [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.2), (sgn * 0.7, 0.9, 1.6)]
        hchain(f"Horn_{sgn}", pts, 0.32, 0.13, M_HORN)
        hcrystal(f"HornTip_{sgn}", 0.14, 0.16, 0.3, pts[-1], (0, 0.5, 1), rbg(3 + sgn))
    elif IS_ADO:
        pts = [(sgn * 0.6, 0.25, 0.78), (sgn * 0.85, 0.45, 1.4), (sgn * 0.85, 0.95, 1.95), (sgn * 0.65, 1.55, 2.2)]
        hchain(f"Horn_{sgn}", pts, 0.36, 0.14, M_HORN)
        hcrystal(f"HornTip_{sgn}", 0.16, 0.2, 0.4, pts[-1], (0, 1, 0.3), rbg(3 + sgn))
        hcrystal(f"HornMid_{sgn}", 0.11, 0.14, 0.26, pts[1], (sgn * 1, 0.2, 0.6), rbg(1 + sgn))
    else:
        a0, a1 = Vector((sgn * 0.6, 0.3, 0.78)), Vector((sgn * 0.95, 0.8, 1.45))
        a2, a3 = Vector((sgn * 1.2, 1.7, 1.95)), Vector((sgn * 1.15, 2.6, 2.05))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.4, 0.16, M_HORN)
        t1 = Vector((sgn * 1.5, 0.55, 2.2))
        t2 = Vector((sgn * 1.7, 1.5, 2.8))
        t3 = Vector((sgn * 0.85, 1.2, 2.55))
        bar(f"Head_HornTine1_{sgn}", hv(a1), hv(t1), 0.2 * HS, M_HORN, H)
        bar(f"Head_HornTine2_{sgn}", hv(a2), hv(t2), 0.18 * HS, M_HORN, H)
        bar(f"Head_HornTine3_{sgn}", hv(a1.lerp(a2, 0.5)), hv(t3), 0.16 * HS, M_HORN, H)
        hcrystal(f"HornTip_{sgn}", 0.2, 0.3, 0.6, a3, (0, 1, 0.5), rbg(0 if sgn < 0 else 6))
        hcrystal(f"HornTipA_{sgn}", 0.14, 0.2, 0.4, t1, (sgn * 1, 0, 0.6), rbg(2 + sgn))
        hcrystal(f"HornTipB_{sgn}", 0.14, 0.2, 0.4, t2, (sgn * 1, 0.6, 0.5), rbg(4 + sgn))
        hcrystal(f"HornTipC_{sgn}", 0.12, 0.18, 0.36, t3, (-sgn * 0.3, 0, 1), rbg(5 + sgn))

# Halo de cristaux derrière la tête (adulte et ado) : couronne d'éclats arc-en-ciel
for k in range(HALO_N):
    a = math.radians(-100 + k * 200 / max(1, HALO_N - 1))
    hshard(f"Halo_{k}", 0.4 * max(0.7, CREST_K), 0.1, (1.6 + 0.3 * math.cos(a * 1.5)) * CREST_K, (math.sin(a) * 2.1, 1.7, math.cos(a) * 1.7 + 0.2),
           (math.sin(a) * 0.9, 0.9, math.cos(a) * 0.9), rbg(k), up=(0, 1, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en maillons, ventre, flancs, bandes d'arc-en-ciel, crête
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

# Plastron nacré + gemme, plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
crystal("Body_ChestGem", 0.2 * SC, 0.14 * SC, 0.22 * SC, (0, -TL * 0.5 - 0.1, ZC - BH * 0.08), (0, -1, 0), M_GEM, body_root, up=(0, 0, 1))
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Écailles prismatiques en quinconce sur les flancs : la couleur défile le long du corps
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), rb(c + r), body_root, up=(sgn, 0, 0))

# Bandes d'arc-en-ciel sur le dos : une couleur différente par tranche
for k in range(STRIPES):
    sl = (TL * 0.86) / STRIPES
    y = -TL * 0.43 + sl * (k + 0.5)
    B(f"Body_Stripe_{k}", (BW * 0.62, sl * 0.9, 0.12 * SC), (0, y, ZC + BH / 2 + 0.01), mat=rb(k), parent=body_root)

for k in range(STRIPES // 2):
    y = -TL * 0.43 + (TL * 0.86) * (k * 2 + 1.0) / STRIPES
    for sgn in (-1, 1):
        crystal(f"Body_BackGem_{k}_{sgn}", 0.14 * SC, 0.28 * SC, 0.26 * SC, (sgn * BW * 0.36, y, ZC + BH / 2 + 0.03),
                (sgn * 0.35, 0.4, 1), rbg(k * 2 + 3 + sgn), body_root, up=(1, 0, 0))

# Cou : un maillon nacré + une plaque crème + une plaque de dos colorée par maillon
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
    B(f"Body_NeckBand_{i}", (2 * r * 0.7, Ln * 0.86, 0.16 * SC), mid + d * (r * 0.97), R, rb(NN - i), body_root)
    crystal(f"Body_NeckCrystal_{i}", 0.2 * SC + 0.1 * r, 0.5 * SC + 0.2 * r, 0.4 * SC, mid + d * r * 0.95,
            d + t * 0.8, rbg(NN - i + 2), body_root, up=tuple(side))
    for sgn in (-1, 1):
        if IS_ADULTE:
            crystal(f"Body_NeckCrystalB_{i}_{sgn}", 0.12 * SC, 0.3 * SC, 0.26 * SC, mid + d * r * 0.85 + side * sgn * r * 0.45,
                    d + t * 0.8 + side * sgn * 0.5, rbg(NN - i + 5 + sgn), body_root, up=tuple(side))
        if i % 2 == 0 or IS_ADULTE:
            shard(f"Body_NeckSide_{i}_{sgn}", 0.5 * SC, 0.1 * SC, 0.7 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, rb(NN - i + sgn), body_root)

# Crête dorsale de cristaux sur le torse : une couleur par cristal
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    crystal(f"Body_Crest_{k}", 0.3 * SC, 0.6 * SC, 0.5 * SC, (0, y, ZC + BH / 2 + 0.02),
            (0, 0.45, 1), rbg(k + 3), body_root, up=(1, 0, 0))

# Épaulières : grappe d'éclats prismatiques sur chaque épaule, plaque nacrée à l'adulte
for sgn in (-1, 1):
    for k in range(SHOULDER_N):
        shard(f"Body_ShoulderShard_{sgn}_{k}", 0.45 * SC, 0.08 * SC, (1.0 - 0.1 * k) * SC,
              (sgn * BW * (0.42 + 0.03 * k), -TL * 0.2 + 0.2 * k * SC, ZC + BH * (0.4 - 0.12 * k)),
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.5 * k), rb(k * 2 + sgn), body_root)
    if IS_ADULTE:
        wedge(f"Body_BackPlate_{sgn}", (BW * 0.5, TL * 0.3, 0.28), (sgn * BW * 0.3, -TL * 0.1, ZC + BH / 2 + 0.02),
              (0, sgn * 8, 0), M_BODY2, body_root, top_x=0.85, top_y=0.85, bevel=0.04)
        wedge(f"Body_BackPlateB_{sgn}", (BW * 0.4, TL * 0.22, 0.24), (sgn * BW * 0.3, TL * 0.17, ZC + BH / 2 - 0.02),
              (0, sgn * 6, 0), M_BODY2, body_root, top_x=0.85, top_y=0.85, bevel=0.03)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, bracelet prismatique, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind, idx):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    # Bracelet : deux bagues de couleurs différentes
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.5),
        mat=rb(idx), parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.12, th * 1.16, 0.12 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.5 + bh_ / 2),
      mat=rb(idx + 4), parent=legs_root)
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    if IS_ADULTE:
        for k in range(2):
            shard(f"{name}_ThighShard_{k}", 0.4 * SC, 0.07 * SC, (0.8 - 0.12 * k) * SC,
                  (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
                  (sgn * 0.8, 0.5, -0.6), rb(idx + k * 3), legs_root)
    if hind:
        crystal(f"{name}_Gem", 0.16 * SC, 0.12 * SC, 0.16 * SC, (x + sgn * th * 0.56, fy + th * 0.2, FOOT_H * 0.55),
                (sgn, 0, 0), rbg(idx + 2), legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False, 0 if sgn < 0 else 1)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True, 2 if sgn < 0 else 3)

# ----------------------------------------------------------
# 12. AILES irisées : os nacrés, membranes en anneaux de couleurs, pointes de cristal, traînée arc-en-ciel
# ----------------------------------------------------------
def prism_wing(name, root, sgn, span, lift, sweep, fingers, bone, droop, bands):
    """Comme wing() du kit, mais chaque bande de membrane a sa couleur d'arc-en-ciel."""
    root = Vector(root)
    elbow = root + Vector((sgn * span * 0.38, span * sweep * 0.25, span * lift * 0.9))
    wrist = root + Vector((sgn * span * 0.62, span * sweep * 0.45, span * lift))
    link(f"{name}_Arm", root, elbow, bone * 1.25, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    link(f"{name}_Fore", elbow, wrist, bone, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    tips = []
    for k in range(fingers):
        f = k / max(1, fingers - 1)
        tip = wrist + Vector((sgn * span * (0.38 - 0.18 * f), span * (0.15 + 0.55 * f), -span * (0.05 + droop * f)))
        link(f"{name}_Finger_{k}", wrist, tip, bone * (0.8 - 0.15 * f), M_BONE, wings_root, up=(0, 1, 0), bevel=0)
        crystal(f"{name}_Tip_{k}", bone * 0.7, bone * 1.2, bone * 1.8, tip, tip - wrist, rbg(k * 2 + 1 + (sgn > 0)), wings_root)
        tips.append(tip)
        for b_ in range(3):
            pb = wrist.lerp(tip, 0.25 + 0.25 * b_)
            B(f"{name}_Bead_{k}_{b_}", (bone * 1.5, bone * 1.5, bone * 1.5), pb, None, rb(k * 3 + b_ + 2), wings_root)
    edge = [elbow.lerp(wrist, 0.5)] + tips + [root + Vector((sgn * span * 0.05, span * 0.45, -span * 0.12))]
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        for j in range(bands):
            t0, t1 = j / bands, (j + 1) / bands
            m = rbw(k * 2 + j + (0 if sgn < 0 else 1))
            if j == 0:
                plate(f"{name}_Memb_{k}_{j}", [wrist, wrist.lerp(a, t1), wrist.lerp(b, t1)], bone * 0.4, m, wings_root)
            else:
                plate(f"{name}_Memb_{k}_{j}", [wrist.lerp(a, t0), wrist.lerp(a, t1), wrist.lerp(b, t1), wrist.lerp(b, t0)],
                      bone * 0.4, m, wings_root)
    plate(f"{name}_Memb_Root", [root, elbow, wrist, edge[-1]], bone * 0.4, rbw(5 if sgn < 0 else 6), wings_root)
    return wrist, tips

for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist, tips = prism_wing(f"Wings_{sgn}", root, sgn, WING_SPAN, WING_LIFT, WING_SWEEP, WING_FINGERS, WING_BONE, 0.55, WING_BANDS)
    shard(f"Wings_{sgn}_WristSpike", WING_BONE * 1.8, WING_BONE * 1.3, WING_SPAN * 0.15, wrist, (sgn * 0.5, 0.2, 1), M_CLAW, wings_root)
    # Traînée arc-en-ciel : 8 rubans de couleurs qui partent du dernier bout de doigt, vers l'arrière
    base = tips[-1]
    dirv = Vector((sgn * 0.2, 1.0, 0.1)).normalized() * TRAIL_L
    spread = Vector((sgn * 0.6, 0.0, 0.8)) * (WING_BONE * 0.9)
    for c in range(8):
        a0 = base + spread * (c - 3.5)
        a1 = a0 + spread
        plate(f"Wings_{sgn}_Trail_{c}", [a0, a1, a1 + dirv * (1.0 - 0.04 * c) + Vector((0, 0, -0.1)),
                                         a0 + dirv * (1.0 - 0.04 * c) + Vector((0, 0, -0.1))], 0.05, rbw(c), wings_root)

# ----------------------------------------------------------
# 13. QUEUE : segments nacrés, une bande colorée + un cristal par segment, éventail arc-en-ciel au bout
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
    B(f"Tail_Band_{i}", (2 * r * 0.8, Ln * 0.9, 0.14 * SC), mid + d * (r * 0.97), R, rb(i + 2), tail_root)
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    crystal(f"Tail_Crystal_{i}", 0.12 * SC + 0.25 * r, 0.3 * SC + r * 0.7, 0.3 * SC, mid + d * r * 0.9,
            d + t * 0.7, rbg(i + 4), tail_root, up=tuple(side))
    if TAIL_SCALES and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  rb(i + 1 + sgn), tail_root, up=(sgn, 0, 0))
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_BODY2, tail_root)
for k in range(TAIL_FAN):
    a = math.radians(-70 + k * 140 / max(1, TAIL_FAN - 1))
    dirv = tt_ * 1.0 + ts_ * math.sin(a) * 1.1 + td_ * (math.cos(a) * 0.5 + 0.1)
    shard(f"Tail_Fan_{k}", 0.55, 0.1, 1.5 * (1 - 0.25 * abs(math.sin(a))) * (BW / 2.5) + 0.6, tip, dirv, rbg(k), tail_root, up=tuple(td_))
crystal("Tail_TipGem", 0.2, 0.3, 0.45, tip + tt_ * 0.2, tt_, M_GEM, tail_root)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (EXCLUSIF) + FX
#     Émission sur tous les motifs prismatiques, halo, traînée d'ailes. FX : cristaux arc-en-ciel qui flottent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        crystal(f"FX_Crystal_{k}", FX_SIZE * 0.2, FX_SIZE * 0.35, FX_SIZE * 0.35, p, dirv, rbg(k), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
