import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Galet · Ado
#  Commun · Terre · Drake · monde 1 · Brute
#  - Ado drake plus long et musclé : casque de galets, sourcils de pierre, 2 crocs par côté, griffes claires
#  - Signes distinctifs à mi-taille : crête d'éclats de pierre, épaules en rochers, genouillères et coudières de galets
#  - Ventre en plaques ocre, plastron, blocs ocre sur les flancs, cornes de pierre claire moyennes
#  - Commun : aucune émission (sauf les yeux), galets qui flottent
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1104)            # même dragon à chaque exécution
TAG = "GALET_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
#    Pierre gris-brun (corps + galets), ocre doré (ventre, plastron, mâchoire), corne claire.
#    Commun : aucune émission, sauf les yeux ambre (très léger).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",     "#A39078", 0.80)   # corps principal, pierre gris-beige
M_BODY2 = get_mat("Pebble",   "#CDBB9C", 0.75)   # galets clairs, écailles claires
M_STONE = get_mat("StoneDark", "#74665A", 0.85)  # galets sombres, genouillères
M_DARK  = get_mat("BodyDark", "#45362A", 0.85)   # sourcils, bouche, taches, narines
M_OCHRE = get_mat("Ochre",    "#F2AE24", 0.60)   # ventre en plaques, plastron, mâchoire
M_OCHRE2 = get_mat("OchreDark", "#D08A14", 0.65) # veines et bords ocre foncé
M_HORN  = get_mat("Horn",     "#E9D7AA", 0.55)   # cornes
M_HORN2 = get_mat("HornBase", "#B09A72", 0.65)   # base des cornes
M_CLAW  = get_mat("Claw",     "#EFE6D0", 0.40)   # griffes, crocs
M_WHITE = get_mat("EyeWhite", "#F4EFE2", 0.30)
M_IRIS  = get_mat("Iris",     "#F28A12", 0.25, emission="#FF9A1F", strength=1.2)   # yeux ambre
M_BLACK = get_mat("Black",    "#0E0B08", 0.30)
PEBBLES = [M_BODY2, M_STONE, M_BODY2, M_BODY]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
BW = 2.4
BH = 2.1
LEG_H = 2.0
TORSO_L = 4.4
NECK_FWD = 1.1
NECK_UP = 1.9
NECK_N = 3
HEAD_SCALE = 1.25
SNOUT_K = 0.85
FANGS = 2
LOWER_FANGS = 1
CHEEK_N = 2
BELLY_N = 5
FLANK_ROWS = 3
FLANK_COLS = 4
SPOTS = 7
CREST_N = 6
BACK_PEBBLES = 9
HEAD_PEBBLES = 5
HEAD_SPIKES = 5
HORN_L = 2.0
SIDE_HORNS = False
SHOULDER_SPIKES = 3
KNEE_ROCK = True
TAIL_L = 4.6
TAIL_STEP = 0.8
TAIL_BEV_N = 3
TAIL_SCALES = True
TAIL_TIP_K = 0.9
FX_N = 9
FX_SIZE = 0.6

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.2                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_BASE = Vector((0, -TL * 0.36, ZC + BH * 0.18))
NECK_TOP = NECK_BASE + Vector((0, -NECK_FWD, NECK_UP))
HEAD_POS = NECK_TOP + Vector((0, -0.25 * HEAD_SCALE, 0.2 * HEAD_SCALE))
HEAD_PITCH = 9                                   # degrés : la tête regarde un peu vers le bas
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

def rock_mesh(rx, rz, h, sides=6, top=0.75, jit=0.16):
    """Galet de pierre : prisme irrégulier (rayons qui varient), axe Y = épaisseur."""
    v = []
    rr = [random.uniform(1 - jit, 1 + jit) for _ in range(sides)]
    ph = random.uniform(0, math.pi / sides)
    for k in range(sides):
        a = ph + k * 2 * math.pi / sides
        v.append((rx * rr[k] * math.cos(a), -h / 2, rz * rr[k] * math.sin(a)))
    for k in range(sides):
        a = ph + k * 2 * math.pi / sides
        j = random.uniform(0.88, 1.08)
        v.append((rx * top * rr[k] * j * math.cos(a) + random.uniform(-0.05, 0.05) * rx, h / 2,
                  rz * top * rr[k] * j * math.sin(a) + random.uniform(-0.05, 0.05) * rz))
    f = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
    for k in range(sides):
        n = (k + 1) % sides
        f.append((k, n, sides + n, sides + k))
    return mesh_from("rock", v, f)

def rock(name, rx, rz, h, loc, normal, mat, parent, sides=6, top=0.75, spin=None):
    """Galet posé sur une surface : 'normal' = direction de l'épaisseur (vers l'extérieur)."""
    up = spin if spin is not None else (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
    return place(name, rock_mesh(rx, rz, h, sides, top), mat, loc, basis(normal, up), parent)

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

def hrock(name, rx, rz, h, loc, normal, mat, sides=6, top=0.75, spin=None):
    return rock("Head_" + name, rx * HS, rz * HS, h * HS, hv(loc), normal, mat, H, sides, top, spin)

# Crâne carré, museau court et large, arête (galet) sur le museau, mâchoire ocre, ligne de bouche
SK = SNOUT_K
hwedge("Skull", (2.0, 1.9, 1.75), (0, 0, 0), mat=M_BODY, top_x=0.93, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.8, 1.9 * SK, 1.05), (0, -0.55 - 0.95 * SK, -0.26), mat=M_BODY,
       top_x=0.95, top_y=0.96, shift_y=-0.04, bevel=0.08)
hrock("SnoutBridge", 0.62, 0.8 * SK, 0.26, (0, -0.6 - 0.9 * SK, 0.3), (0, 0, 1), M_BODY2, spin=(0, -1, 0))
hbox("Jaw", (1.6, 1.85 * SK + 0.1, 0.34), (0, -0.55 - 0.95 * SK, -0.8), mat=M_OCHRE, bevel=0.04)
hbox("MouthLine", (1.84, 1.82 * SK, 0.05), (0, -0.55 - 0.95 * SK, -0.7), mat=M_DARK)
SNOUT_FRONT = -0.55 - 1.9 * SK

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.24, 0.24, 0.07), (sgn * 0.45, SNOUT_FRONT + 0.25, 0.26), mat=M_BLACK)

# Yeux : blanc, iris ambre, pupille (ronde + reflets pour bébé, étroite pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.95, 1.02, 0.74, 0.86, 0.44, 0.6
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.62, 0.44, 0.5, 0.14, 0.44
EY, EZ = -0.42, 0.12
for sgn in (-1, 1):
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, EY, EZ), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, EY - 0.02, EZ - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, EY - 0.03, EZ - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.07, EY - 0.16, EZ + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, EY + 0.14, EZ - 0.22), mat=M_WHITE)
        # petit sourcil de galet plat, doux
        hbox(f"Brow_{sgn}", (0.14, 1.0, 0.2), (sgn * 0.97, EY - 0.02, EZ + 0.64), rot=(4, 0, 0), mat=M_STONE, bevel=0.02)
    else:
        # sourcils sévères en galet plat, inclinés vers le museau
        hbox(f"Brow_{sgn}", (0.2, 1.1, 0.3), (sgn * 0.97, EY - 0.05, EZ + 0.5), rot=(16, 0, 0), mat=M_STONE, bevel=0.03)
        hrock(f"BrowStone_{sgn}", 0.4, 0.55, 0.22, (sgn * 0.94, EY - 0.1, EZ + 0.72), (sgn * 0.4, -0.3, 1), M_BODY2)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs) + dents du bas (ado 1, adulte 2)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.74, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))
        for k in range(LOWER_FANGS):
            hshard(f"LowFang_{sgn}_{k}", 0.22, 0.2, 0.55 + 0.1 * k, (sgn * (0.55 - 0.3 * k), SNOUT_FRONT + 0.3, -0.7),
                   (sgn * 0.05, -0.2, 1), M_CLAW, up=(1, 0, 0))

# Joues : éclats de pierre qui partent vers l'arrière de la mâchoire
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.5, 0.22, 0.95 - 0.12 * k, (sgn * 0.9, -0.1 + k * 0.32, -0.45 - k * 0.1),
               (sgn * 0.8, 0.9, -0.3 - 0.2 * k), pick([M_BODY2, M_STONE, M_HORN]))

# Casque de galets sur le crâne et crête d'éclats vers l'arrière
for k in range(HEAD_PEBBLES):
    x = (-0.6, 0.55, 0.0, -0.3, 0.35, 0.65, -0.7, 0.0)[k % 8]
    y = (-0.35, -0.25, 0.1, 0.5, 0.45, 0.1, 0.15, -0.55)[k % 8]
    hrock(f"SkullPebble_{k}", 0.5 + 0.08 * (k % 3), 0.5, 0.3, (x, y, 0.82 + 0.03 * (k % 3)), (x * 0.3, 0.1 * y, 1),
          PEBBLES[k % 4], sides=6 + (k % 2))
for k in range(HEAD_SPIKES):
    x = (-0.55, 0.55, 0.0, -0.8, 0.8, -0.28, 0.28, 0.0)[k % 8]
    row = k // 5
    hshard(f"SkullSpike_{k}", 0.55, 0.3, (0.9 + 0.35 * (k % 3)) * (1.0 + 0.15 * row), (x, 0.7 + 0.25 * row, 0.7 - 0.15 * row),
           (x * 0.4, 0.75, 1), pick([M_BODY2, M_STONE, M_HORN], [4, 3, 2]), up=(1, 0, 0))

# Cornes de pierre claire (bébé : courtes ; ado : moyennes ; adulte : grandes + petites cornes latérales)
for sgn in (-1, 1):
    HW = min(0.95, 0.3 + 0.27 * HORN_L)          # largeur de la corne, proportionnelle à sa longueur
    hshard(f"Horn_{sgn}", HW, HW * 0.75, HORN_L, (sgn * 0.62, 0.35, 0.78), (sgn * 0.3, 0.5, 1), M_HORN, up=(0, 1, 0))
    hbox(f"HornBase_{sgn}", (0.62, 0.62, 0.32), (sgn * 0.62, 0.35, 0.8), mat=M_HORN2, bevel=0.03)
    if SIDE_HORNS:
        hshard(f"HornSide_{sgn}", 0.55, 0.45, HORN_L * 0.45, (sgn * 0.95, 0.55, 0.3), (sgn * 1, 0.5, 0.45), M_HORN, up=(0, 1, 0))
        hshard(f"HornJaw_{sgn}", 0.45, 0.4, HORN_L * 0.3, (sgn * 0.96, 0.1, -0.5), (sgn * 1, 0.2, -0.5), M_HORN, up=(0, 1, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre ocre, flancs, crête, épaules en rochers
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les pièces sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron ocre sur le poitrail + plaques de ventre séparées + gros blocs ocre sur le bas des flancs
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_OCHRE, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.22 * SC), (0, y, ZC - BH / 2 + 0.03), mat=pick([M_OCHRE, M_OCHRE, M_OCHRE2]), parent=body_root)
    for sgn in (-1, 1):
        B(f"Body_BellySide_{i}_{sgn}", (0.2 * SC, pl, BH * 0.4), (sgn * (half_w(y) + 0.02), y, ZC - BH * 0.27),
          mat=M_OCHRE if i % 2 == 0 else M_OCHRE2, parent=body_root)

# Écailles de pierre en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.36 - 0.12 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.1 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_STONE, M_BODY2]), body_root, up=(sgn, 0, 0))

# Taches brun foncé sur le dos et les flancs
for k in range(SPOTS):
    y = random.uniform(-TL * 0.4, TL * 0.45)
    if k % 2 == 0:
        B(f"Body_Spot_{k}", (random.uniform(0.3, 0.5) * SC, random.uniform(0.3, 0.5) * SC, 0.06),
          (random.uniform(-0.3, 0.3) * BW, y, ZC + BH / 2 - 0.01), mat=M_DARK, parent=body_root)
    else:
        sgn = random.choice((-1, 1))
        B(f"Body_Spot_{k}", (0.06, random.uniform(0.35, 0.55) * SC, random.uniform(0.3, 0.45) * SC),
          (sgn * (half_w(y) + 0.0), y, ZC + BH * random.uniform(0.0, 0.3)), mat=M_DARK, parent=body_root)

# Cou court et massif : courbe lissée de la tête vers le torse, un bloc + une plaque ocre par maillon
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):
    p = NECK_BASE.lerp(NECK_TOP, tt)
    p.y -= 0.12 * NECK_FWD * math.sin(math.pi * tt)
    NECK_CTRL.append(p)
NECK_LEN = (NECK_TOP - NECK_BASE).length
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_LEN * 1.05) / NECK_N)
NN = len(NECK_SPINE) - 1
for i in range(NN):
    p1, p2 = NECK_SPINE[i], NECK_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / NN
    r = keyed([(0, BW * 0.36), (1, BW * 0.43)], s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.25, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.84, 0.22 * SC), mid - d * (r * 0.95), R, M_OCHRE, body_root)
    shard(f"Body_NeckCrest_{i}", 0.8 * SC, 0.2 * SC, (0.9 + 0.5 * (1 - s)) * SC, mid + d * r * 0.85, d + t * 0.9,
          pick([M_BODY2, M_STONE]), body_root, up=tuple(side))
    for sgn in (-1, 1):
        if i % 2 == 0 or IS_ADULTE:
            shard(f"Body_NeckSide_{i}_{sgn}", 0.6 * SC, 0.2 * SC, 0.75 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, pick(PEBBLES), body_root)

# Crête dorsale d'éclats de pierre, et galets plats sur le dos
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.9 * SC, 0.3 * SC, (1.15 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC * 1.1,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), pick([M_BODY2, M_STONE, M_HORN], [4, 3, 1]), body_root, up=(1, 0, 0))
for k in range(BACK_PEBBLES):
    y = -TL * 0.4 + (TL * 0.82) * ((k * 0.618) % 1.0)
    x = (-1 if k % 2 else 1) * BW * (0.12 + 0.2 * ((k * 0.37) % 1.0))
    rock(f"Body_BackPebble_{k}", 0.5 * SC, 0.42 * SC, 0.2 * SC, (x, y, ZC + BH / 2 - 0.02), (x * 0.15, 0, 1),
         PEBBLES[k % 4], body_root, sides=6 + (k % 2), spin=(0, 1, 0.3 * (k % 3)))

# Épaules en gros rochers (+ éclats), hanches plus petites chez l'ado et l'adulte
for sgn in (-1, 1):
    rock(f"Body_ShoulderRock_{sgn}", BH * 0.42, BH * 0.4, BH * 0.5, (sgn * BW * 0.5, -TL * 0.3, ZC + BH * 0.18),
         (sgn * 1, -0.1, 0.5), M_BODY2, body_root, sides=7, top=0.5)
    for k in range(SHOULDER_SPIKES):
        shard(f"Body_ShoulderSpike_{sgn}_{k}", 0.5 * SC, 0.3 * SC, (1.1 - 0.15 * k) * SC,
              (sgn * BW * (0.46 + 0.04 * k), -TL * 0.3 + 0.35 * k * SC - 0.3 * SC, ZC + BH * (0.36 - 0.05 * k)),
              (sgn * (0.7 + 0.2 * k), 0.3 * k - 0.2, 0.9 - 0.15 * k), pick([M_BODY2, M_STONE, M_HORN], [3, 3, 1]), body_root)
    if KNEE_ROCK:
        rock(f"Body_HipRock_{sgn}", BH * 0.34, BH * 0.32, BH * 0.4, (sgn * BW * 0.48, TL * 0.3, ZC + BH * 0.2),
             (sgn * 1, 0.1, 0.5), M_STONE, body_root, sides=7, top=0.5)
        for k in range(2):
            shard(f"Body_HipSpike_{sgn}_{k}", 0.45 * SC, 0.28 * SC, (0.9 - 0.15 * k) * SC,
                  (sgn * BW * (0.46 + 0.04 * k), TL * 0.3 + 0.3 * k * SC, ZC + BH * (0.34 - 0.04 * k)),
                  (sgn * 0.8, 0.5 + 0.2 * k, 0.9), pick([M_BODY2, M_STONE]), body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, tibia, genouillère de pierre, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.32   # la cuisse remonte au tiers du flanc
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.2), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    # plaque ocre sur le devant de la cuisse (comme le plastron)
    depth = th * (1.7 if hind else 1.5)
    B(f"{name}_ThighPlate", (th * 0.8, 0.14 * SC, thigh_h * 0.5),
      (x + sgn * 0.05 * th, y - depth * 0.44, FOOT_H + SHIN_H + thigh_h * 0.4), mat=M_OCHRE, parent=legs_root)
    box(f"{name}_Shin", (th * 0.95, th * 1.0, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.04 * SC)
    # Manchette de pierre sombre + galets sur la jambe
    B(f"{name}_Cuff", (th * 1.08, th * 1.12, SHIN_H * 0.32), (x, y + yo, FOOT_H + SHIN_H * 0.42), mat=M_STONE, parent=legs_root)
    if KNEE_ROCK:
        # genouillère (devant) et coudière (derrière) : gros galets de pierre
        rock(f"{name}_Knee", th * 0.55, th * 0.5, th * 0.5, (x, y + yo - th * 0.52, FOOT_H + SHIN_H + 0.05),
             (sgn * 0.2, -1, 0.3), M_BODY2, legs_root, sides=7, top=0.7)
        rock(f"{name}_Elbow", th * 0.4, th * 0.4, th * 0.4, (x + sgn * th * 0.3, y + yo + th * 0.48, FOOT_H + SHIN_H + 0.1),
             (sgn * 0.5, 1, 0.3), M_STONE, legs_root, sides=6, top=0.7)
        shard(f"{name}_KneeSpike", 0.3 * SC, 0.25 * SC, 0.8 * SC, (x + sgn * th * 0.45, y + yo - th * 0.2, FOOT_H + SHIN_H + 0.3),
              (sgn * 1, -0.2, 0.5), M_BODY2, legs_root)
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2), mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : aucune (morphologie Drake : massif, large, bas sur pattes)
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques ocre, crête de galets, pointe de pierre
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.25, -0.3, 0.0), (0.5, -0.55, 0.15), (0.75, -0.45, 0.1), (1.0, -0.05, -0.1)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.46), (0.3, BW * 0.39), (0.6, BW * 0.29), (0.85, BW * 0.17), (1.0, BW * 0.12)]
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.2 * SC), mid - d * (r * 0.95), R, M_OCHRE, tail_root)
    shard(f"Tail_Crest_{i}", 0.9 * r + 0.25, 0.3 * SC, 0.5 * SC + r * 0.9, mid + d * r * 0.85, d + t * 0.7,
          pick([M_BODY2, M_STONE, M_BODY2]), tail_root, up=(1, 0, 0))
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.1 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_STONE]), tail_root, up=(sgn, 0, 0))
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
rock("Tail_TipRock", BW * 0.2, BW * 0.2, BW * 0.2, tip + tt_ * 0.1, tt_, M_BODY2, tail_root, sides=7, top=0.8)
for k, (ax, az, ln) in enumerate(((0, 1, 1.0), (1, 0.3, 0.8), (-1, 0.3, 0.8), (0, 0, 1.3))):
    shard(f"Tail_TipSpike_{k}", BW * 0.16, BW * 0.12, BW * 0.5 * ln * TAIL_TIP_K, tip + tt_ * 0.1,
          tt_ + ts_ * ax * 0.5 + td_ * az * 0.5, pick([M_BODY2, M_HORN]), tail_root)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, aucune émission (sauf les yeux). Détails = écailles de pierre,
#     ventre ocre en plaques, griffes, crête de galets. Éléments flottants : galets en lévitation.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.8), random.uniform(-TL * 0.8, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        if k % 3 == 2:
            leaf_plate(f"FX_Chip_{k}", p, Vector([random.uniform(-1, 1) for _ in range(3)]), FX_SIZE * random.uniform(0.8, 1.3),
                       FX_SIZE * 0.55, M_OCHRE2, master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.05 * SC)
        else:
            rock(f"FX_Pebble_{k}", FX_SIZE * random.uniform(0.35, 0.6), FX_SIZE * random.uniform(0.3, 0.5), FX_SIZE * 0.3, p,
                 (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)), pick([M_BODY2, M_STONE]), master,
                 sides=6)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
