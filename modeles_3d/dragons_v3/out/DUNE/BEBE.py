import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Dune · Bébé
#  Commun · Terre · Drake · monde 2
#  - Bébé trapu : énorme tête carrée brun orangé, museau court, très grands yeux brillants, pattes courtes et épaisses
#  - Signes distincts : rayures de dune brunes ondulées sur les flancs, collerette de plaques facettées, deux cornes beige, crête de roche
#  - Ventre crème en plaques, dalles dorées sur les flancs, menton en plaques, 3 doigts + 3 griffes crème par patte, pas de crocs
#  - Pas d'ailes (Drake), queue courte terminée par une petite massue de pierre
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1111)            # même dragon à chaque exécution
TAG = "DUNE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 4       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 3000          # budget de triangles de ce stade et de cette rareté
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
#    Or sable (corps), plaques de roche dorées claires, brun dune (rayures, museau), crème (ventre, cornes).
#    Commun : aucune émission, couleurs mates (seuls les iris ont une lueur ambre très faible).
# ----------------------------------------------------------
M_GOLD  = get_mat("Body",      "#E0A63A", 0.55)   # corps principal, or sable
M_GOLD2 = get_mat("BodyScale", "#C98A2C", 0.60)   # écailles, dessus des pattes, dessous des plaques
M_HEAD  = get_mat("Head",      "#C97A2E", 0.55)   # crâne et museau, brun orangé
M_BROWN = get_mat("Dune",      "#97551F", 0.65)   # rayures de dune, nez, joues
M_DARK  = get_mat("BodyDark",  "#5C3519", 0.70)   # dalles sombres du dos, bouche, sourcils
M_PL1   = get_mat("PlateLight", "#F3CB5C", 0.50)  # plaques de roche claires
M_PL2   = get_mat("PlateMid",  "#DDA23B", 0.55)   # plaques de roche moyennes
M_CREAM = get_mat("Belly",     "#F4DDA0", 0.55)   # ventre en plaques, plastron
M_HORN  = get_mat("Horn",      "#EBD0A0", 0.45)   # cornes beige
M_CLAW  = get_mat("Claw",      "#F8EDCF", 0.35)   # griffes, crocs
M_WHITE = get_mat("EyeWhite",  "#F6F0DC", 0.30)
M_IRIS  = get_mat("Iris",      "#E08A14", 0.25, emission="#E08A14", strength=1.0)
M_BLACK = get_mat("Black",     "#120A05", 0.30)
M_DUST  = get_mat("Dust",      "#DDB86E", 0.80)   # poussière et éclats de sable flottants
PLATES = [M_PL1, M_PL2, M_GOLD]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
BW = 2.7
BH = 2.0
LEG_H = 1.55
TORSO_L = 3.3
NECK_L = 0.55
NECK_LEAN = 0.15
NECK_N = 1
NECK_R = (0.95, 1.05)
HEAD_SCALE = 1.2
SNOUT_K = 0.6
FANGS = 0
CHEEK_N = 1
JAW_PLATES = 2
CREST_HEAD_N = 3
COLLAR_RINGS = 1
COLLAR_N = 8
BELLY_N = 4
BELLY_SIDES = False
SLAB_ROWS = 1
SLAB_COLS = 3
STRIPES = 2
STRIPE_SEGS = 8
BACK_SLABS = 1
SHOULDER_SLABS = 1
RIDGE_N = 3
BRACER_K = 0.35
LEG_BEV = 0
THIGH_PLATES = 0
CLAW_L = 0.45
TAIL_L = 2.4
TAIL_STEP = 0.6
TAIL_BEV_N = 1
TAIL_STRIPES = False
TAIL_SPIKES = 2
FX_N = 3
DUST_N = 1
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
HEAD_PITCH = 6                                   # degrés : la tête regarde un peu vers le bas
TAIL_START = Vector((0, TL * 0.42, ZC - 0.1 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
H = head_root

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def leaf_plate(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Éclat plat en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne brun orangé, long museau carré, plaques dorées sur le dessus, menton en plaques dentelées.
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

SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K
# Crâne, museau, dessus clair du museau, nez, mâchoire, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_HEAD, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.65, 2.1 * SNOUT_K, 1.12), (0, -0.6 - 1.05 * SNOUT_K, -0.22), mat=M_HEAD,
       top_x=0.95, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.1, 1.7 * SNOUT_K, 0.14), (0, -0.6 - 0.95 * SNOUT_K, 0.38), mat=M_PL2)
hbox("Nose", (1.72, 0.55, 1.0), (0, SNOUT_FRONT + 0.1, -0.18), mat=M_BROWN, bevel=0.06)
hbox("Jaw", (1.45, 1.95 * SNOUT_K, 0.32), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BROWN)
hbox("MouthLine", (1.7, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.66), mat=M_DARK)

# Menton : plaques dentelées empilées sous la mâchoire
for k in range(JAW_PLATES):
    f = k / max(1, JAW_PLATES - 1)
    hbox(f"Chin_{k}", (1.25 - 0.45 * f, 0.55 + 0.1 * (k % 2), 0.28 + 0.06 * k),
         (0.12 * (-1) ** k, SNOUT_FRONT + 0.7 + 0.6 * k * SNOUT_K, -1.0 - 0.1 * k),
         rot=(8 * (-1) ** k, 12 * (-1) ** k, 0), mat=PLATES[k % 2])

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.24, 0.07), (sgn * 0.4, SNOUT_FRONT - 0.15, 0.34), mat=M_BLACK)

# Yeux : blanc, iris ambre, pupille (ronde + reflets pour bébé, fendue pour ado / adulte), sourcils
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
        hbox(f"Brow_{sgn}", (0.14, 0.7, 0.14), (sgn * 0.97, ey - 0.02, ez + 0.58), rot=(10, 0, 0), mat=M_DARK)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.24), (sgn * 0.97, ey - 0.05, ez + 0.5), rot=(14, 0, 0), mat=M_DARK, bevel=0.02)

# Crocs (ado : 2 petits par côté ; adulte : 3 plus longs)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.6 + k * 0.5
        hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.72, fy, -0.7), (0, 0.05, -1),
               M_CLAW, up=(1, 0, 0))

# Joues : pointes brunes de roche + petite plaque dorée
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.5, 0.2, 0.9 - 0.12 * k, (sgn * 0.88, -0.2 + k * 0.38, -0.4 - k * 0.14),
               (sgn * 0.9, 0.7, -0.35), M_BROWN if k % 2 == 0 else M_PL2)

# Plaques dorées sur le dessus du crâne (crête de tête, de plus en plus grandes vers l'arrière)
for k in range(CREST_HEAD_N):
    f = k / max(1, CREST_HEAD_N - 1)
    hshard(f"HeadCrest_{k}", 0.75 + 0.2 * f, 0.3, 0.85 + 0.55 * f, (((-1) ** k) * 0.28 * (1 - f * 0.6), -0.4 + 0.3 * k, 0.78),
           (0, 0.45 + 0.35 * f, 1), PLATES[k % 3], up=(1, 0, 0))

# Collerette : anneaux de plaques facettées autour de l'arrière du crâne
for ring_i in range(COLLAR_RINGS):
    cnt = COLLAR_N - ring_i * 3
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 11)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.8, 0.7 + ring_i * 0.28, rad.z * 0.75)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hshard(f"Collar_{ring_i}_{k}", 0.9 - ring_i * 0.12, 0.26, 1.2 + ring_i * 0.2 + random.random() * 0.3,
               loc, direction, PLATES[(k + ring_i) % 3], up=tuple(rad))

# Cornes beige recourbées vers l'arrière (bébé : courtes ; ado : moyennes ; adulte : grandes + pointe avant)
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.75, 0.75, 0.5), (sgn * 0.62, 0.3, 0.78), mat=M_DARK, bevel=0.05)
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.3, 0.9), (sgn * 0.85, 0.55, 1.3), (sgn * 0.8, 1.05, 1.65)], 0.36, 0.14, M_HORN)
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.65, 0.3, 0.95), (sgn * 0.95, 0.55, 1.5), (sgn * 1.0, 1.1, 2.0),
                               (sgn * 0.8, 1.7, 2.25)], 0.42, 0.15, M_HORN)
    else:
        h0, h1 = Vector((sgn * 0.65, 0.3, 0.95)), Vector((sgn * 1.0, 0.65, 1.55))
        h2, h3, h4 = Vector((sgn * 1.2, 1.2, 2.0)), Vector((sgn * 1.15, 1.85, 2.3)), Vector((sgn * 0.95, 2.4, 2.35))
        hchain(f"Horn_{sgn}", [h0, h1, h2, h3, h4], 0.5, 0.16, M_HORN)
        hshard(f"HornSpur_{sgn}", 0.4, 0.3, 1.0, h1 + Vector((sgn * 0.1, 0, 0)), (sgn * 0.7, -0.3, 0.8), M_HORN, up=(0, 1, 0))
        hshard(f"HornSpur2_{sgn}", 0.35, 0.26, 0.9, h2, (sgn * 0.9, 0.2, 0.7), M_HORN, up=(0, 1, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre, rayures de dune, dalles de roche, crête
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_GOLD, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_GOLD, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_GOLD, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les plaques sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron crème sur le poitrail + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.26), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.34),
              mat=M_CREAM, parent=body_root)

# Dalles de roche facettées sur le haut des flancs (le haut du corps est fait de plaques dorées)
for sgn in (-1, 1):
    for r in range(SLAB_ROWS):
        for c in range(SLAB_COLS):
            y = -TL * 0.38 + (TL * 0.8) * (c + 0.5 + 0.35 * (r % 2) + random.uniform(-0.12, 0.12)) / SLAB_COLS
            z = ZC + BH * (0.27 - 0.2 * r) + random.uniform(-0.04, 0.04) * BH
            wy = (TL * 0.8) / SLAB_COLS * random.uniform(0.85, 1.15)
            wz = BH * random.uniform(0.24, 0.32)
            wedge(f"Body_Slab_{sgn}_{r}_{c}", (0.2 * SC, wy, wz), (sgn * (half_w(y) + 0.02 * SC), y, z),
                  (random.uniform(-9, 9), 0, random.uniform(-8, 8)), pick(PLATES, [4, 3, 2]), body_root,
                  top_x=0.8, top_y=0.82, bevel=0)

# Rayures de dune : lignes brunes ondulées sur les flancs (signe distinctif)
def dune_stripe(name, sgn, z0, amp, lam, y0, y1, segs, th, parent, xfun):
    pts = []
    for s in range(segs + 1):
        y = y0 + (y1 - y0) * s / segs
        pts.append((y, z0 + amp * math.sin(2 * math.pi * (y - y0) / lam)))
    for s in range(segs):
        (ya, za), (yb, zb) = pts[s], pts[s + 1]
        ln = math.hypot(yb - ya, zb - za)
        ang = math.degrees(math.atan2(zb - za, yb - ya))
        ym = (ya + yb) / 2
        B(f"{name}_{s}", (0.1 * SC, ln * 1.15, th), (sgn * xfun(ym), ym, (za + zb) / 2), rot=(ang, 0, 0),
          mat=M_BROWN, parent=parent)

for sgn in (-1, 1):
    for k in range(STRIPES):
        dune_stripe(f"Body_Dune_{sgn}_{k}", sgn, ZC - BH * (0.02 + 0.17 * k) - BH * 0.02, BH * 0.07,
                    TL * 0.3, -TL * 0.4, TL * 0.46, STRIPE_SEGS, 0.17 * SC, body_root, lambda y: half_w(y) + 0.09 * SC)

# Dalles sombres sur le dos (comme les plaques brunes du concept)
for sgn in (-1, 1):
    for k in range(BACK_SLABS):
        wedge(f"Body_BackSlab_{sgn}_{k}", (BW * 0.34, TL * (0.2 - 0.03 * k), 0.26 * SC),
              (sgn * BW * 0.22, -TL * 0.12 + TL * 0.27 * k, ZC + BH / 2 + 0.03), (0, sgn * 7, sgn * (6 - 5 * k)),
              M_DARK, body_root, top_x=0.85, top_y=0.85, bevel=0.03 * SC)

# Épaulières : grosses dalles dorées empilées sur chaque épaule
for sgn in (-1, 1):
    for k in range(SHOULDER_SLABS):
        wedge(f"Body_Shoulder_{sgn}_{k}", (0.5 * SC + 0.15 * (SHOULDER_SLABS - k), BH * (0.42 - 0.06 * k), BH * (0.4 - 0.05 * k)),
              (sgn * (BW * 0.52 + 0.03 * k), -TL * 0.24 + 0.22 * k * SC, ZC + BH * (0.12 + 0.17 * k)),
              (0, sgn * (10 + 6 * k), sgn * 8 * k), PLATES[k % 3], body_root, top_x=0.8, top_y=0.8, bevel=0.03 * SC)

# Cou : courbe lissée de la tête vers le torse, un bloc doré + une plaque crème + une dalle de roche par maillon
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
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.22, 2 * r * 0.95), mid, R, M_GOLD, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_CREAM, body_root)
    # dalle de roche sur la nuque
    shard(f"Body_NeckRidge_{i}", 1.0 * r, 0.26 * SC, (0.8 + 0.4 * (1 - s)) * SC + r * 0.4, mid + d * r * 0.85, d + t * 0.8,
          PLATES[i % 3], body_root, up=tuple(side))
    for sgn in (-1, 1):
        if i % 2 == 0 or IS_ADULTE:
            wedge(f"Body_NeckSlab_{i}_{sgn}", (0.2 * SC, Ln * 0.95, r * 1.1), mid + side * sgn * (r + 0.02),
                  R, PLATES[(i + (sgn > 0)) % 3], body_root, top_x=0.8, top_y=0.85, bevel=0)

# Crête dorsale : plaques de roche pointues sur le torse
for k in range(RIDGE_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, RIDGE_N - 1)
    shard(f"Body_Ridge_{k}", 1.0 * SC, 0.3 * SC, (1.05 - 0.25 * abs(k / max(1, RIDGE_N - 1) - 0.4)) * SC * 1.1,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), PLATES[k % 3], body_root, up=(1, 0, 0))

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, genouillère en dalle, bracelet de sable, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = 0.42 * SC                                # pied bas et plat (comme sur le concept)
SHIN_H = LEG_H * 0.55                            # jambe bien visible sous le torse

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    off = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.3 if hind else 1.15), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_GOLD, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.95, th * 1.0, SHIN_H + 0.1), (x, y + off, FOOT_H + SHIN_H / 2),
        mat=M_GOLD2, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    # Bracelet de sable brun + dessus sombre
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.08, th * 1.12, bh_), (x, y + off, FOOT_H + SHIN_H * 0.5),
        mat=M_BROWN, parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.14, th * 1.18, 0.1 * SC), (x, y + off, FOOT_H + SHIN_H * 0.5 + bh_ / 2),
      mat=M_DARK, parent=legs_root)
    # Genouillère : dalle de roche claire devant la cuisse
    wedge(f"{name}_Knee", (th * 0.95, 0.22 * SC, thigh_h * 0.5), (x, y - th * 0.72, FOOT_H + SHIN_H + thigh_h * 0.32),
          (-8, 0, 0), PLATES[(int(y * 10) + (sgn > 0)) % 2], legs_root, top_x=0.8, top_y=0.8, bevel=0)
    for k in range(THIGH_PLATES):
        wedge(f"{name}_ThighSlab_{k}", (0.2 * SC, th * 0.85, thigh_h * 0.35),
              (x + sgn * th * 0.62, y + (k - 0.5) * th * 0.5, FOOT_H + SHIN_H + thigh_h * (0.62 - 0.25 * k)),
              (0, 0, 6 * (k - 0.5)), PLATES[(k + 1) % 3], legs_root, top_x=0.8, top_y=0.8, bevel=0)
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.2, th * 1.9, FOOT_H), (x, fy + off, FOOT_H / 2),
        mat=M_BROWN, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + off - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_GOLD2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * CLAW_L, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.46
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.35, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.33, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : aucune (Drake). La silhouette est massive, large et basse.
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques crème, crête de roche, rayures, massue de pierre au bout
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.3, 0.0), (0.45, -0.55, 0.3), (0.7, -0.5, 0.15), (0.9, -0.3, -0.25), (1.0, -0.15, -0.35)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.44), (0.3, BW * 0.37), (0.6, BW * 0.27), (0.85, BW * 0.2), (1.0, BW * 0.15)]
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
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.3, 2 * r * 0.95), mid, R, M_GOLD, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    shard(f"Tail_Crest_{i}", 1.0 * r + 0.2, 0.26 * SC, 0.5 * SC + r * 0.9, mid + d * r * 0.85, d + t * 0.7,
          PLATES[i % 3], tail_root, up=(1, 0, 0))
    if i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            wedge(f"Tail_Slab_{i}_{sgn}", (0.16 * SC, Ln * 1.5, r * 1.0), mid + side * sgn * (r - 0.02), R,
                  PLATES[(i // 2 + (sgn > 0)) % 3], tail_root, top_x=0.8, top_y=0.85, bevel=0)
    elif TAIL_STRIPES and s < 0.85:
        for sgn in (-1, 1):
            B(f"Tail_Dune_{i}_{sgn}", (0.1 * SC, Ln * 1.3, r * 0.4), mid + side * sgn * (r + 0.01) - d * r * 0.2, R, M_BROWN, tail_root)
# Massue de pierre : anneau brun, bloc doré et grappe de pointes
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
RT = seg_matrix(tt_, td_, ts_)
B("Tail_TipRing", (BW * 0.34, 0.3 * SC, BW * 0.34), tip, RT, M_BROWN, tail_root)
box("Tail_Club", (BW * 0.4, BW * 0.5, BW * 0.4), tip + tt_ * BW * 0.22, RT, M_PL2, tail_root, bevel=0.05 * SC)
for k in range(TAIL_SPIKES):
    a = 2 * math.pi * k / TAIL_SPIKES
    dirv = td_ * math.cos(a) + ts_ * math.sin(a)
    shard(f"Tail_Spike_{k}", BW * 0.22, BW * 0.16, BW * 0.55, tip + tt_ * BW * 0.3 + dirv * BW * 0.12, dirv * 1.0 + tt_ * 0.5,
          M_PL1 if k % 2 == 0 else M_HORN, tail_root, up=tuple(tt_))
shard("Tail_SpikeEnd", BW * 0.26, BW * 0.2, BW * 0.7, tip + tt_ * BW * 0.4, tt_, M_HORN, tail_root, up=tuple(td_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, aucune émission (sauf la lueur ambre des iris). Signe fort = rayures de dune
#     + collerette de roche. Détails = dalles, ventre en plaques, griffes, crête.
#     Éléments flottants : éclats de sable en losange et petits nuages de poussière autour des pieds.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.6), random.uniform(-TL * 0.8, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        leaf_plate(f"FX_Shard_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55, pick([M_DUST, M_PL2, M_HORN]),
                   master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.05 * SC)
    for k in range(DUST_N):
        base = Vector((random.choice((-1, 1)) * BW * random.uniform(0.7, 1.3), random.uniform(-TL * 0.5, TL * 0.6), FOOT_H * 0.4))
        for j in range(2):
            sz = FX_SIZE * random.uniform(0.35, 0.6)
            B(f"FX_Dust_{k}_{j}", (sz, sz, sz), base + Vector((random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), j * sz * 0.9)),
              rot=(random.uniform(0, 60), random.uniform(0, 60), random.uniform(0, 60)), mat=M_DUST, parent=master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
