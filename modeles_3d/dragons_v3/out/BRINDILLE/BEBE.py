import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Brindille · Bébé
#  Commun · Plante · Amphiptère · monde 1
#  - Bébé serpent tan enroulé au sol, tête énorme et carrée, très grands yeux verts, museau court
#  - Signe distinctif : bois de brindilles brunes avec bourgeons, pousse de 2 feuilles, liane brune en spirale
#  - Ventre crème en plaques, ailes en forme de petites feuilles nervurées, queue terminée par des feuilles
#  - Commun : aucune émission, 3 familles de couleurs (bois, crème, vert)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1103)            # même dragon à chaque exécution
TAG = "BRINDILLE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
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
#    Bois tan (corps), crème (ventre), brun écorce (liane, plaques), vert feuille (feuilles, ailes).
#    Commun : aucune émission, couleurs mates. Seul l'iris des yeux a une très légère lueur.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#C99A5B", 0.62)   # corps principal : bois tan
M_BODY2 = get_mat("BodyDark",  "#B08044", 0.65)   # segments alternés, dessus du museau
M_BODYL = get_mat("BodyLight", "#E2BE82", 0.55)   # arête du museau, éclats clairs
M_BARK  = get_mat("Bark",      "#7A4E26", 0.75)   # liane, plaques d'écorce, sourcils
M_BARK2 = get_mat("BarkDark",  "#4F3017", 0.80)   # écorce sombre, bouche, narines
M_CREAM = get_mat("Belly",     "#F1E6BC", 0.55)   # ventre en plaques, mâchoire, plastron
M_HORN  = get_mat("Horn",      "#D9B880", 0.55)   # bois (brindilles) beige-tan
M_LEAF1 = get_mat("LeafLight", "#A9DC45", 0.45)   # feuilles claires
M_LEAF2 = get_mat("LeafMid",   "#5DB82C", 0.45)   # feuilles moyennes
M_LEAF3 = get_mat("LeafDark",  "#2F8A2A", 0.50)   # feuilles sombres
M_BUD   = get_mat("Bud",       "#8BE03A", 0.40)   # bourgeons au bout des bois
M_WING  = get_mat("Membrane",  "#86C640", 0.55)   # membrane des ailes-feuilles
M_BONE  = get_mat("WingBone",  "#3C8426", 0.55)   # bord et nervure centrale des ailes
M_VEIN  = get_mat("WingVein",  "#5FAA30", 0.55)   # nervures secondaires
M_CLAW  = get_mat("Claw",      "#F6EEDA", 0.35)   # crocs, pointes d'aile
M_WHITE = get_mat("EyeWhite",  "#F4F4EA", 0.30)
M_IRIS  = get_mat("Iris",      "#6EDB35", 0.25, 0.0, "#6EDB35", 0.8)   # iris vert, très faible lueur
M_BLACK = get_mat("Black",     "#0B0F08", 0.30)
LEAFS = [M_LEAF1, M_LEAF2, M_LEAF3]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
ZB = 2.3
NECK_H = 3.4
COIL_R = 1.8
TAIL_UP = 0.7
RK = 0.95
BODY_STEP = 0.9
HEAD_SCALE = 1.75
SNOUT_K = 0.5
FANGS = 0
CHEEK_N = 2
BEARD_N = 2
MANE_RINGS = 1
MANE_N = 7
ANT_K = 0.5
ANT_BEAM = 3
ANT_TINES = 1
SPROUT_N = 2
LEAF_K = 0.8
LEAF_FROM = 0.1
LEAF_TO = 0.7
BIB_N = 3
SHOULDER_LEAVES = 2
VINE = True
VINE_TURN = 0.9
VINE_END = 0.85
VINE_T = 0.2
GROUND_TUFTS = 4
WING_L = 4.2
WING_W = 1.9
WING_EL = 50
WING_BACK = 0.25
WING_VEINS = 2
WING_BONE_T = 0.16
SPIKES = False
GRAIN_EVERY = 0        # veines de bois sur les flancs : 1 = chaque segment, 2 = un sur deux, 0 = aucune
JOINT_BANDS = True     # anneaux d'écorce sombre entre les segments (effet planches de bois)
ANT_TWIGS = False      # petits rameaux secondaires sur les bois
TAIL_LEAF = 1.8
FX_N = 5
FX_SIZE = 0.7

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
HS = HEAD_SCALE
LK = LEAF_K                                      # taille des feuilles / petits détails

# Points de contrôle de la colonne (Catmull-Rom) : cou dressé en S, descente, anneaux au sol, queue qui remonte
def build_ctrl():
    pts = []
    for f, y in ((1.0, -0.30), (0.86, 0.10), (0.62, 0.50), (0.38, 0.45), (0.15, -0.10), (0.0, -0.55)):
        pts.append(Vector((0, y, ZB + NECK_H * f)))
    pts.append(Vector((0, -0.60, ZB * 0.55 + 0.9)))        # descente du poitrail vers le sol
    pts.append(Vector((0, -0.25, 1.6)))
    pts.append(Vector((0.05, 0.75, 0.3)))                  # le corps se couche vers l'arrière
    cy = 0.8 + COIL_R * 1.55                               # centre de l'anneau
    # anneau : R diminue de COIL_R à 0.55*COIL_R sur 320 degrés, puis la queue se dresse au centre
    for k in range(1, 7):
        th = math.radians(55 * k)
        R = COIL_R * (1.0 - 0.45 * (k / 6.0))
        pts.append(Vector((R * math.sin(th) * 1.05, cy - R * math.cos(th), 0.3)))
    pts.append(Vector((-0.25 * COIL_R, cy - 0.25 * COIL_R, 0.9)))
    pts.append(Vector((0.05 * COIL_R, cy + 0.05 * COIL_R, 2.0 * TAIL_UP)))
    pts.append(Vector((0.25 * COIL_R, cy + 0.15 * COIL_R, 3.6 * TAIL_UP)))
    return pts
CTRL = build_ctrl()

RADIUS_KEYS = [(0.0, 0.62), (0.04, 0.74), (0.18, 0.86), (0.30, 1.08), (0.42, 1.12), (0.60, 0.98),
               (0.78, 0.62), (0.90, 0.38), (1.0, 0.16)]
RADIUS_KEYS = [(s, v * RK) for s, v in RADIUS_KEYS]
S_TAIL = 0.64                                     # au-delà : pièces parentées à TAIL_ROOT
S_WING = 0.17                                     # position des épaules (ailes) le long de la colonne

SPINE = resample(sample_curve(CTRL), BODY_STEP)
N = len(SPINE) - 1
# le corps repose sur le sol : on remonte les points trop bas selon leur rayon
for i in range(len(SPINE)):
    s_ = i / N
    SPINE[i].z = max(SPINE[i].z, keyed(RADIUS_KEYS, s_) * 0.96)

# Repère par segment par transport parallèle : dos = +Y dans le cou, +Z à plat au sol
FR = []
_d = Vector((0, 1, 0))
for i in range(N):
    t = (SPINE[i + 1] - SPINE[i]).normalized()
    _d = (_d - t * _d.dot(t)).normalized()
    FR.append((t, _d.copy(), t.cross(_d).normalized()))

def radius(s):
    return keyed(RADIUS_KEYS, s)

def frame_at(s):
    i = min(N - 1, max(0, int(s * N)))
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = FR[i]
    return mid, t, d, side, radius(s)

HEAD_POS = SPINE[0] + Vector((0, -0.25 * HS, 0.60 * HS))
HEAD_PITCH = 6                                    # degrés : la tête regarde un peu vers le bas

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)           # pas de pattes (amphiptère) : sert aux touffes posées au sol
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (bois, branches)."""
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

def hbar(name, p1, p2, th, mat):
    return bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H)

# Crâne carré, museau long en bloc, arête claire, mâchoire crème distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.5, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.04, bevel=0.08)
hbox("SnoutBridge", (0.95, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODYL)
hbox("SnoutTop", (1.25, 0.7 * SNOUT_K + 0.3, 0.1), (0, -0.2, 0.86), mat=M_BODY2)     # plaque de bois sur le front
hbox("Jaw", (1.3, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.53, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_BARK2)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.22, 0.06), (sgn * 0.38, SNOUT_FRONT + 0.25, 0.2), mat=M_BARK2)

# Yeux : blanc, iris vert, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.92, 1.0, 0.72, 0.84, 0.42, 0.6
else:
    EW, EH, IW, IH, PW, PH = 0.72, 0.74, 0.54, 0.62, 0.11, 0.54
for sgn in (-1, 1):
    ey, ez = -0.28, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.93, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 0.98, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.02, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.05, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.05, ey + 0.13, ez - 0.22), mat=M_WHITE)
    else:
        # sourcils sévères en écorce, inclinés vers le museau
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.22), (sgn * 0.95, ey - 0.05, ez + 0.55), rot=(14, 0, 0),
             mat=M_BARK, bevel=0.02)

# Crocs (ado : 2 petits par côté ; adulte : 3 par côté)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.28 + 0.1 * FANGS / 3, (sgn * 0.68, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles en feuille, feuilles de joue et barbe de feuilles sous le menton
for sgn in (-1, 1):
    hleaf(f"Ear_{sgn}", 0.7, 1.2, (sgn * 0.85, 0.5, 0.3), (sgn * 1, 0.6, 0.5), M_LEAF1, up=(0, 0, 1))
    for k in range(CHEEK_N):
        hleaf(f"Cheek_{sgn}_{k}", 0.5, 0.9 - 0.1 * k, (sgn * 0.9, -0.3 + k * 0.32, -0.4 - k * 0.12),
              (sgn * 0.8, 0.9, -0.5), pick(LEAFS, [3, 4, 2]), up=(sgn, 0, 0))
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.32
    hleaf(f"Beard_{k}", 0.42, 0.95 - 0.1 * abs(x), (x, SNOUT_FRONT * 0.45, -0.88), (x * 0.3, 0.35, -1),
          pick([M_LEAF2, M_LEAF3, M_LEAF1]), up=(1, 0, 0))

# Collerette de feuilles derrière le crâne (se prolonge le long du cou)
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / max(1, cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hleaf(f"Mane_{ring_i}_{k}", 0.75 - ring_i * 0.1, 1.15 + ring_i * 0.2 + random.random() * 0.3,
              loc, direction, pick(LEAFS, [4, 3, 2]), up=tuple(rad))

# SIGNE DISTINCTIF : bois de brindilles brunes avec bourgeons verts
#   bébé : 1 branche courte + 1 bourgeon ; ado : branches ramifiées ; adulte : grands bois à 3 branches
AK = ANT_K
for sgn in (-1, 1):
    a0 = Vector((sgn * 0.55, 0.25, 0.78))
    a1 = Vector((sgn * 0.85, 0.55, 0.78 + 1.0 * AK))
    a2 = Vector((sgn * 1.10, 1.05, 0.78 + 1.9 * AK))
    a3 = Vector((sgn * 1.00, 1.70, 0.78 + 2.7 * AK))
    tchain(f"Head_Antler_{sgn}", [hv(a0), hv(a1), hv(a2), hv(a3)][:ANT_BEAM], 0.34 * HS, 0.15 * HS, M_HORN, H)
    ends = [a3 if ANT_BEAM == 4 else a2]
    tines = [(0.5, (sgn * 1.55, 0.15, 0.55)), (0.8, (sgn * 1.75, 0.95, 0.5)), (0.35, (sgn * 0.45, 0.05, 0.9))][:ANT_TINES]
    for k, (f, off) in enumerate(tines):
        base = a1.lerp(a3 if ANT_BEAM == 4 else a2, f)
        tip = base + Vector(off) * AK * 0.9 + Vector((0, 0, 0.55 * AK))
        hbar(f"Antler_{sgn}_Tine{k}", base, tip, 0.2 - 0.03 * k, M_HORN)
        ends.append(tip)
        if ANT_TWIGS:                     # petit rameau qui part du milieu de chaque branche
            mid_t = base.lerp(tip, 0.55)
            twig = mid_t + Vector((sgn * 0.35, 0.3, 0.35)) * AK
            hbar(f"Antler_{sgn}_Twig{k}", mid_t, twig, 0.11, M_HORN)
            ends.append(twig)
    for k, e in enumerate(ends):          # bourgeons verts au bout des brindilles
        hleaf(f"AntlerBud_{sgn}_{k}", 0.34, 0.55 * max(0.7, AK), e - Vector((0, 0, 0.05)), (sgn * 0.5, -0.2, 1),
              M_BUD if k % 2 == 0 else M_LEAF1, up=(0, 1, 0), t=0.06)
    # petit rameau de bois sur le front
    if ANT_BEAM == 4:
        hbar(f"Brow_Twig_{sgn}", (sgn * 0.5, -0.5, 0.82), (sgn * 0.6, -1.0, 1.2), 0.12, M_HORN)

# Pousse centrale sur le front (2 feuilles chez le bébé, 3 chez l'ado, 5 chez l'adulte)
hbar("Sprout", (0, -0.05, 0.8), (0, -0.05, 1.05 + 0.25 * AK), 0.14, M_BARK)
for k in range(SPROUT_N):
    a = math.radians(-70 + k * (140 / max(1, SPROUT_N - 1))) if SPROUT_N > 1 else 0
    hleaf(f"Sprout_{k}", 0.5, 0.95, (0, -0.05, 1.0 + 0.25 * AK), (math.sin(a) * 0.9, -0.1, 0.65),
          LEAFS[k % 3], up=(0, 1, 0), t=0.07)

# ----------------------------------------------------------
# 10. CORPS : segments en bois, ventre en plaques, plaques d'écorce, feuilles, liane en spirale
# ----------------------------------------------------------
def leaf_dir(t, d, side, sgn, k=0.5):
    return t * 0.9 + side * sgn * k - d * 0.1

for i in range(N):
    p1, p2 = SPINE[i], SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / N
    r = radius(s)
    t, d, side = FR[i]
    R = seg_matrix(t, d, side)
    parent = body_root if s < S_TAIL else tail_root
    tag = "Body" if s < S_TAIL else "Tail"

    # Segment principal (couleurs de bois alternées), biseau seulement sur les gros blocs
    box(f"{tag}_Seg_{i}", (2 * r, Ln * 1.30, 1.9 * r), mid, R, M_BODY if i % 2 == 0 else M_BODY2, parent,
        bevel=(0.08 * r if s < 0.42 else 0.0))
    # Anneau d'écorce sombre à la jointure (effet planches de bois du concept)
    if JOINT_BANDS and 0.02 < s < 0.86:
        B(f"{tag}_Joint_{i}", (2.06 * r, 0.12, 1.96 * r), p1, R, M_BARK2, parent)
    # Veines de bois sur les flancs (une rainure claire et une sombre par côté)
    if GRAIN_EVERY and s < 0.8 and i % GRAIN_EVERY == 0:
        for sgn in (-1, 1):
            B(f"{tag}_Grain_{i}_{sgn}", (0.08, Ln * 0.9, 0.11 * r), mid + side * sgn * r * 0.99 + d * (0.38 * r), R,
              M_BODYL, parent)
            B(f"{tag}_GrainD_{i}_{sgn}", (0.08, Ln * 0.6, 0.09 * r), mid + side * sgn * r * 0.99 - d * (0.18 * r) + t * (Ln * 0.15), R,
              M_BARK, parent)
    # Plaques de ventre crème bien séparées
    if s < 0.84:
        B(f"{tag}_Belly_{i}", (1.55 * r, Ln * 0.80, 0.26 * r + 0.06), mid - d * (r * 0.93), R, M_CREAM, parent)
    # Plaques d'écorce sur le dos
    if 0.1 < s < 0.78 and i % 2 == 1:
        B(f"{tag}_Bark_{i}", (1.3 * r, Ln * 0.85, 0.2 * r + 0.05), mid + d * (r * 0.92), R @ Euler((math.radians(-6), 0, 0)).to_matrix(),
          M_BARK if (i // 2) % 2 == 0 else M_BARK2, parent)
    # Feuilles sur les flancs (pointe vers la queue), plus nombreuses sur la poitrine et les épaules
    if LEAF_FROM < s < LEAF_TO:
        dense = 1.0 if (s < 0.34) else 0.55
        for sgn in (-1, 1):
            if random.random() < dense:
                leaf_plate(f"{tag}_FlankLeaf_{i}_{sgn}", mid + side * sgn * r * 0.9 - d * 0.15 * r,
                           leaf_dir(t, d, side, sgn, 0.55), (1.15 + 0.5 * dense) * LK * (0.8 + 0.5 * r),
                           0.78 * LK, pick(LEAFS, [3, 4, 2]), parent, up=tuple(side * sgn + d * 0.3), t=0.09 * LK)
    # Crête de feuilles le long du dos
    if i % 2 == 0 and 0.03 < s < 0.9:
        leaf_plate(f"{tag}_Crest_{i}", mid + d * r * 0.9, d * 0.9 + t * 0.8, (0.9 + 0.5 * r) * LK, 0.7 * LK,
                   pick(LEAFS, [3, 4, 2]), parent, up=tuple(side), t=0.09 * LK)

# Plastron crème large et bavoir de feuilles sur la poitrine
cmid, ct, cd, cside, cr = frame_at(S_WING + 0.05)
CR = seg_matrix(ct, cd, cside)
B("Body_Plastron", (1.7 * cr, 1.5, 0.3), cmid - cd * (cr + 0.04), CR, M_CREAM, body_root)
for k in range(BIB_N):
    amt = (k - (BIB_N - 1) / 2) * 0.55
    leaf_plate(f"Body_Bib_{k}", cmid - cd * cr * 0.9 + cside * amt * cr * 0.8 + ct * 0.4, -cd * 0.5 + ct * 0.7 - Vector((0, 0, 0.5)),
               (1.3 - 0.15 * abs(amt)) * LK * 1.1, 0.8 * LK, pick(LEAFS, [3, 4, 2]), body_root, up=tuple(-cd), t=0.1 * LK)

# Épaulières de feuilles + plaque d'écorce à la base de chaque aile
for sgn in (-1, 1):
    for k in range(SHOULDER_LEAVES):
        leaf_plate(f"Body_ShoulderLeaf_{sgn}_{k}", cmid + cside * sgn * cr * 0.9 + cd * (0.3 - 0.2 * k) * cr + ct * (-0.4 + 0.3 * k),
                   cside * sgn * (0.9 + 0.1 * k) + ct * (0.5 + 0.3 * k) + cd * (0.3 - 0.3 * k), (1.2 - 0.12 * k) * LK, 0.75 * LK,
                   pick(LEAFS, [3, 4, 2]), body_root, up=tuple(cd), t=0.1 * LK)
    wedge(f"Body_ShoulderBark_{sgn}", (0.9 * cr, 1.5, 0.45), cmid + cside * sgn * cr * 0.55 + cd * cr * 0.85, seg_matrix(ct, cd, cside),
          M_BARK, body_root, top_x=0.8, top_y=0.8, bevel=0.05)

# Liane brune enroulée en spirale autour du corps (signe distinctif), avec de petites feuilles
if VINE:
    vp = []
    for i in range(N):
        s = (i + 0.5) / N
        if s < 0.03 or s > VINE_END:
            continue
        mid = (SPINE[i] + SPINE[i + 1]) / 2
        t, d, side = FR[i]
        r = radius(s)
        a = i * VINE_TURN
        vp.append((i, mid + (side * math.cos(a) + d * math.sin(a)) * (r * 1.02 + 0.05), side * math.cos(a) + d * math.sin(a)))
    for j in range(len(vp) - 1):
        i, p, n_ = vp[j]
        s = (i + 0.5) / N
        bar(f"{'Body' if s < S_TAIL else 'Tail'}_Vine_{j}", p, vp[j + 1][1], VINE_T, M_BARK2 if j % 2 else M_BARK,
            body_root if s < S_TAIL else tail_root, up=tuple(n_))
        if j % 4 == 2:
            leaf_plate(f"Body_VineLeaf_{j}", p, n_ + FR[min(i, N - 1)][0] * 0.6, 0.85 * LK, 0.55 * LK,
                       pick([M_LEAF1, M_LEAF2]), body_root if s < S_TAIL else tail_root, up=tuple(n_), t=0.07 * LK)

# Touffes de feuilles posées au sol autour des anneaux (parentées à LEGS_ROOT)
for k in range(GROUND_TUFTS):
    a = k * 2 * math.pi / GROUND_TUFTS + 0.4
    base = Vector((math.sin(a) * COIL_R * 1.0, 0.8 + COIL_R * 1.55 - math.cos(a) * COIL_R * 1.0, 0.1))
    base += Vector((math.sin(a), -math.cos(a), 0)) * RK * 0.9
    for j in range(2):
        leaf_plate(f"Legs_Tuft_{k}_{j}", base, Vector((math.sin(a) * (0.6 + j * 0.5), -math.cos(a) * (0.6 + j * 0.5), 0.7 + 0.3 * j)),
                   0.9 * LK, 0.5 * LK, LEAFS[(k + j) % 3], legs_root, up=(0, 0, 1), t=0.07 * LK)

# ----------------------------------------------------------
# 11. PATTES : aucune (amphiptère, corps de serpent). LEGS_ROOT ne porte que les touffes posées au sol (section 10).
# ----------------------------------------------------------

# ----------------------------------------------------------
# 12. AILES-FEUILLES (bord + nervure centrale + nervures, membrane verte)
# ----------------------------------------------------------
OUTLINE = [(0.0, 0.0), (0.28, 0.72), (0.60, 1.0), (1.0, 0.0), (0.60, -1.0), (0.28, -0.72)]

def edge_w(u):
    """Demi-largeur du bord de la feuille (en proportion) à la position u le long de la nervure."""
    if u <= 0.28:
        return 0.72 * u / 0.28
    if u <= 0.60:
        return 0.72 + 0.28 * (u - 0.28) / 0.32
    return max(0.0, 1.0 * (1.0 - u) / 0.40)

def leaf_wing(sgn, root):
    el = math.radians(WING_EL)
    a = Vector((sgn * math.cos(el), WING_BACK, math.sin(el))).normalized()
    p = Vector((a.z, 0, -a.x))
    if p.z < 0:
        p = -p
    p.normalize()
    def P(u, w):
        return root + a * (u * WING_L) + p * (w * WING_W)
    pts = [P(u, w) for (u, w) in OUTLINE]
    plate(f"Wings_{sgn}_Membrane", pts, WING_BONE_T * 0.5, M_WING, wings_root)
    for k in range(len(pts)):                                  # bord de la feuille
        k2 = (k + 1) % len(pts)
        if k == 0 or k2 == 0:
            continue
        link(f"Wings_{sgn}_Edge_{k}", pts[k], pts[k2], WING_BONE_T, M_BONE, wings_root, up=tuple(a.cross(p)), extra=WING_BONE_T * 0.5,
             bevel=0, depth=WING_BONE_T * 0.8)
    link(f"Wings_{sgn}_Rib", pts[0], P(1.0, 0.0), WING_BONE_T * 1.2, M_BONE, wings_root, up=tuple(a.cross(p)), extra=0.2,
         bevel=0, depth=WING_BONE_T)
    link(f"Wings_{sgn}_EdgeUp", pts[0], pts[1], WING_BONE_T, M_BONE, wings_root, up=tuple(a.cross(p)), extra=0.1, bevel=0,
         depth=WING_BONE_T * 0.8)
    link(f"Wings_{sgn}_EdgeLo", pts[0], pts[5], WING_BONE_T, M_BONE, wings_root, up=tuple(a.cross(p)), extra=0.1, bevel=0,
         depth=WING_BONE_T * 0.8)
    for k in range(WING_VEINS):                                # nervures secondaires, penchées vers la pointe
        u = 0.18 + 0.52 * k / max(1, WING_VEINS - 1) if WING_VEINS > 1 else 0.4
        u2 = min(0.92, u + 0.2)
        for side_w in (1, -1):
            link(f"Wings_{sgn}_Vein_{k}_{side_w}", P(u, 0), P(u2, side_w * edge_w(u2) * 0.93), WING_BONE_T * 0.5, M_VEIN,
                 wings_root, up=tuple(a.cross(p)), extra=0.05, bevel=0, depth=WING_BONE_T * 0.5)
    # pointes crème au sommet de la feuille et au bord (comme sur le concept)
    shard(f"Wings_{sgn}_TipSpike", WING_BONE_T * 1.5, WING_BONE_T, WING_L * 0.12, P(1.0, 0.0), a, M_CLAW, wings_root)
    if SPIKES:
        shard(f"Wings_{sgn}_SpikeUp", WING_BONE_T * 1.4, WING_BONE_T, WING_L * 0.1, P(0.6, 1.0), p, M_CLAW, wings_root)
    # articulation en bois à la base
    B(f"Wings_{sgn}_Joint", (WING_BONE_T * 2.2, WING_BONE_T * 2.2, WING_BONE_T * 2.2), P(0.02, 0), None,
      M_BARK, wings_root)

wmid, wt, wd, wside, wr = frame_at(S_WING)
for sgn in (-1, 1):
    leaf_wing(sgn, wmid + wd * wr * 0.8 + wside * sgn * wr * 0.55)

# ----------------------------------------------------------
# 13. QUEUE : fait partie de la même courbe (s > S_TAIL) ; bout = anneau d'écorce + feuilles croisées
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = FR[-1]
B("Tail_TipRing", (0.55 * RK, 0.32, 0.55 * RK), tip, seg_matrix(tt_, td_, ts_), M_BARK, tail_root)
leaf_plate("Tail_TipLeaf_A", tip, tt_ + td_ * 0.15, TAIL_LEAF, TAIL_LEAF * 0.5, M_LEAF1, tail_root, up=tuple(ts_), t=0.12 * LK)
leaf_plate("Tail_TipLeaf_B", tip, tt_ + td_ * 0.15, TAIL_LEAF * 0.82, TAIL_LEAF * 0.42, M_LEAF2, tail_root, up=tuple(td_), t=0.12 * LK)
leaf_plate("Tail_TipLeaf_C", tip, tt_ + ts_ * 0.5, TAIL_LEAF * 0.6, TAIL_LEAF * 0.32, M_LEAF3, tail_root, up=tuple(td_), t=0.1 * LK)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, 3 familles de couleurs (bois, crème, vert), AUCUNE émission
#     (hors léger éclat des iris). Un signe fort : bois + liane. Feuilles qui flottent autour.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 3.2
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_L * 0.6 + 2.0), random.uniform(-2.5, 3.0 + COIL_R * 2.5),
                    random.uniform(1.0, top_z)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55, pick([M_LEAF1, M_LEAF2, M_BUD]),
                   master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
