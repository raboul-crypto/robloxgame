import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Aurore · Adulte
#  Épique · Plante · Oriental · monde 1
#  - Adulte majestueux en S qui flotte : cou dressé, tête haute, corps bas, queue qui remonte et s'enroule vers l'avant
#  - Signe distinctif : grands bois beige ramifiés (pointes dorées), crinière en feuilles vertes, lime lumineuses et dorées, moustaches dorées en boucle, pousse lumineuse
#  - Plastron brun et or avec gemme verte, épaulières brunes à franges dorées, ventre crème en plaques, crête de feuilles, bracelets dorés
#  - Rendu Épique complet : feuilles émissives, nervures lime, bois en fleurs de cerisier, aura rose, anneau doré et touffe lumineuse au bout de la queue, 14 FX flottants
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1108)            # même dragon à chaque exécution
TAG = "AURORE_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 13000          # budget de triangles de ce stade et de cette rareté
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
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
DORSAL, TAIL_BANDS, VINES, ANT_LEAVES = True, True, True, 4
CTRL = [(0.0, -0.2, 9.0), (0.0, 0.3, 8.3), (0.0, 0.9, 7.1), (0.0, 0.9, 5.8), (0.0, 0.3, 4.6), (0.0, 0.1, 3.3),
        (0.3, 0.9, 2.2), (0.6, 2.4, 1.7), (0.6, 3.9, 2.2), (0.4, 5.2, 3.0), (0.1, 6.4, 4.1), (-0.3, 7.2, 5.4),
        (-0.6, 7.4, 6.6), (-0.9, 6.9, 7.5), (-1.0, 6.1, 7.7)]   # colonne en S (comme le Mirage)
RADIUS_KEYS = [(0.0, 0.6), (0.08, 0.72), (0.2, 0.92), (0.3, 0.98), (0.45, 0.92), (0.6, 0.75), (0.8, 0.45), (1.0, 0.2)]
RK = 1.0
STEP = 0.5
NECK_S = 0.2
BODY_S = 0.62
FRONT_S, BACK_S = 0.24, 0.55
HS = 1.3
SW = 1.5
SNOUT_K = 1.0
FANGS = 3
CHEEK_N, CROWN_N, BEARD_N = 3, 3, 5
MANE_RINGS, MANE_N, AURA_N = 4, 17, 15
SPROUT = 0.8
GLOW_K = 0.7
GOLD = True
CREST, CREST_STEP = True, 1
SCALES, FLANKS, NECK_SIDE = True, True, True
NECK_LEAF_X = (-0.7, -0.25, 0.25, 0.7)
CHEST, PADS, PADK, PAD_FEATHERS = True, True, 1.0, 3
LS = 1.0
FOOT_Z, LEG_DROP = None, 2.3
LEG_TH = (0.55, 0.4)
FRONT_BEND, BACK_BEND = 0.5, -0.6
LEG_GOLD = True
TIP_LEAVES, TIP_L = 5, 2.0
FX_N, FX_SIZE, FX_W = 14, 0.7, 3.0
SCALE_STEP = 1        # 1 = une rangée d'écailles par segment, 2 = un segment sur deux
VEINS = True          # nervures lumineuses lime sur les flancs (rendu Épique)
BLOSSOMS = 2          # fleurs de cerisier roses par bois (+ sur la liane)
MANE_FLOWERS = 6      # fleurs roses lumineuses piquées dans la crinière

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Vert feuille (corps), crème (ventre), beige (bois), or (ornements), brun (épaulières),
#    lueurs : lime (feuilles, pousse, gemme) et rose (aura, étincelles).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#6CC02E", 0.50)   # corps principal
M_BODY2 = get_mat("BodyScale", "#4FA524", 0.50)   # écailles, dessus des pattes
M_DARK  = get_mat("BodyDark",  "#2C7A1E", 0.55)   # sourcils, bouche, ombres
M_LEAF1 = get_mat("LeafLight", "#A8E64A", 0.45)   # feuilles claires (crinière, crête)
M_LEAF2 = get_mat("LeafMid",   "#5DBB2C", 0.45)   # feuilles moyennes
M_LEAF3 = get_mat("LeafDark",  "#2F8A24", 0.50)   # feuilles sombres
M_CREAM = get_mat("Belly",     "#E6D49A", 0.55)   # ventre en plaques, mâchoire
M_HORN  = get_mat("Horn",      "#D9BF8A", 0.55)   # bois et cornes beige
M_GOLD  = get_mat("Gold",      "#F0B72E", 0.30, 0.55)          # ornements dorés, moustaches
M_DGOLD = get_mat("DarkGold",  "#B87A16", 0.35, 0.50)          # ombres de l'or
M_BROWN = get_mat("Brown",     "#7B4A22", 0.65)   # épaulières, plastron
M_CLAW  = get_mat("Claw",      "#F6EEDA", 0.35)   # griffes, crocs
M_WHITE = get_mat("EyeWhite",  "#F4F4EA", 0.30)
M_IRIS  = get_mat("Iris",      "#9BE03C", 0.25, 0.0, "#B8FF50", 1.2)   # iris vert vif, lueur faible
M_BLACK = get_mat("Black",     "#0B0F08", 0.30)
M_GLOW  = get_mat("LeafGlow",  "#6EE23A", 0.30, 0.0, "#58FF3C", 2.4)   # feuilles lumineuses
M_PINK  = get_mat("PinkGlow",  "#FF8EBE", 0.30, 0.0, "#FF7FB4", 2.2)   # aura rose, étincelles
M_GEM   = get_mat("Gem",       "#74FF5A", 0.12, 0.0, "#5CFF48", 3.0)   # gemme du plastron
M_SPARK = get_mat("Spark",     "#FFD25A", 0.20, 0.0, "#FFC83C", 2.8)   # étincelles dorées
LEAFS = [M_LEAF1, M_LEAF2, M_LEAF3]

# ----------------------------------------------------------
# 8. HIÉRARCHIE ET OUTILS
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
CTRL = [Vector(p) for p in CTRL]
HEAD_POS = CTRL[0] + Vector((0, -0.32 * HS, 0.22 * HS))
HEAD_PITCH = 5

master    = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (bois, moustaches, tige)."""
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

def blossom(name, center, normal, size, parent, petal_mat=None):
    """Fleur de cerisier : 5 pétales en éclats plats autour d'un coeur doré lumineux."""
    center, normal = Vector(center), Vector(normal).normalized()
    ref = Vector((0, 0, 1)) if abs(normal.z) < 0.9 else Vector((1, 0, 0))
    u = normal.cross(ref).normalized()
    v = normal.cross(u).normalized()
    for k in range(5):
        a = k / 5 * 2 * math.pi
        dirv = u * math.cos(a) + v * math.sin(a) + normal * 0.35
        shard(f"{name}_Petal_{k}", size * 0.75, size * 0.12, size, center, dirv, petal_mat or M_PINK, parent,
              up=tuple(normal))
    crystal(f"{name}_Heart", size * 0.28, size * 0.15, size * 0.2, center + normal * size * 0.05, normal, M_SPARK,
            parent, sides=5)

def leaf_mat(glow=0.25):
    """Feuille : surtout vertes, parfois lumineuses (rendu Épique)."""
    if random.random() < glow * GLOW_K:
        return M_GLOW
    return pick(LEAFS, [4, 3, 2])

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HS)
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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

SK = SNOUT_K
SNF = -0.7 - 1.6 * SK                      # avant du museau
hwedge("Skull", (SW, 1.55, 1.4), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.08)
hwedge("Snout", (SW * 0.78, 1.7 * SK, 0.76), (0, -0.7 - 0.85 * SK, -0.14), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.04, bevel=0.06)
hbox("SnoutBridge", (SW * 0.5, 1.3 * SK, 0.14), (0, -0.7 - 0.75 * SK, 0.27), rot=(-5, 0, 0), mat=M_LEAF1)
hbox("Jaw", (SW * 0.7, 1.55 * SK, 0.3), (0, -0.62 - 0.8 * SK, -0.66), mat=M_CREAM)
hbox("MouthLine", (SW * 0.78 + 0.02, 1.5 * SK, 0.06), (0, -0.7 - 0.85 * SK, -0.5), mat=M_DARK)
hbox("NosePad", (SW * 0.78, 0.18, 0.6), (0, SNF - 0.02, -0.14), mat=M_BODY2)

# Yeux : blanc, iris, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.72, 0.78, 0.56, 0.64, 0.34, 0.46
else:
    EW, EH, IW, IH, PW, PH = 0.46, 0.4, 0.3, 0.34, 0.07, 0.3
EX = SW / 2 + 0.01
for sgn in (-1, 1):
    ey, ez = -0.28, 0.1
    hbox(f"Nostril_{sgn}", (0.2, 0.06, 0.16), (sgn * 0.26, SNF - 0.1, 0.12), mat=M_BLACK)
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * EX, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * (EX + 0.04), ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * (EX + 0.08), ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.2), (sgn * (EX + 0.11), ey - 0.14, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * (EX + 0.11), ey + 0.1, ez - 0.18), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.16, 0.8, 0.2), (sgn * (EX - 0.02), ey - 0.06, ez + 0.4), rot=(12, 0, 0),
             mat=M_DARK, bevel=0.02)

# Crocs (ado : 2 petits ; adulte : 3 par côté)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNF + 0.4 + k * 0.38
        hshard(f"Fang_{sgn}_{k}", 0.17, 0.17, 0.26 + 0.05 * FANGS, (sgn * SW * 0.37, fy, -0.5), (0, 0.05, -1),
               M_CLAW, up=(1, 0, 0))

# Oreilles-feuilles, feuilles de joue, couronne dorée au-dessus des sourcils
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.5, 0.1, 1.0 * (1 if not IS_BEBE else 0.7), (sgn * SW * 0.5, 0.3, 0.3), (sgn * 0.9, 1, 0.35), M_LEAF1)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.34, 0.08, 0.85 - 0.12 * k, (sgn * SW * 0.4, -0.5 + k * 0.32, -0.5 - k * 0.1),
               (sgn * 0.9, 0.9, -0.45), pick(LEAFS, [3, 4, 2]))
    for k in range(CROWN_N):
        hshard(f"Crown_{sgn}_{k}", 0.3 - 0.03 * k, 0.1, 0.8 - 0.14 * k, (sgn * (SW * 0.3 + 0.12 * k), -0.45 + 0.28 * k, 0.62),
               (sgn * (0.5 + 0.2 * k), 0.25 + 0.25 * k, 1), M_GOLD if k % 2 == 0 else M_DGOLD)

# Barbe de feuilles sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.2
    hshard(f"Beard_{k}", 0.24, 0.08, 0.6 + random.random() * 0.3,
           (x, -0.9 - 0.5 * SK + abs(x) * 0.5, -0.8), (x * 0.4, 0.4, -1), pick(LEAFS, [3, 4, 2]))

# Collerette de feuilles derrière le crâne (vertes, quelques-unes lumineuses ou dorées)
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-155 + k * (310 / (cnt - 1)) + ring_i * 8)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.6 * SW / 1.5, 0.45 + ring_i * 0.28, rad.z * 0.58)
        jit = Vector((random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.2), random.uniform(-0.2, 0.2)))
        direction = rad * (1.0 - ring_i * 0.28) + Vector((0, 1.0, 0)) + jit
        r = random.random()
        mat = M_GOLD if (ring_i == 0 and k % 5 == 2 and GOLD) else leaf_mat(0.3)
        hleaf(f"Mane_{ring_i}_{k}", 0.62 - ring_i * 0.08, 1.35 + ring_i * 0.3 + random.random() * 0.4,
              loc, direction, mat, up=tuple(rad))

# Aura rose : grandes feuilles lumineuses qui rayonnent derrière la crinière
for k in range(AURA_N):
    ang = math.radians(-135 + k * (270 / max(1, AURA_N - 1)))
    rad = Vector((math.sin(ang), 0, math.cos(ang)))
    hleaf(f"Aura_{k}", 0.5, 2.0 + 0.5 * math.cos(ang * 2), (rad.x * 0.8, 1.2, rad.z * 0.75),
          rad * 1.0 + Vector((0, 1.1, 0)), M_PINK, up=tuple(rad), t=0.05)

ANT_TIPS = []   # bouts des bois (coord. locales de la tête) qui reçoivent des fleurs
# Bois beige : bébé = 2 petites cornes ; ado = bois à 2 pointes ; adulte = grands bois ramifiés
for sgn in (-1, 1):
    a0 = Vector((sgn * 0.5, 0.35, 0.65))
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [a0, (sgn * 0.75, 0.55, 1.1), (sgn * 0.7, 0.95, 1.5)], 0.3, 0.14, M_HORN)
        ANT_TIPS.append(((sgn * 0.72, 0.85, 1.42), (sgn * 0.6, 0.2, 1)))
    elif IS_ADO:
        a1, a2, a3 = Vector((sgn * 0.8, 0.7, 1.5)), Vector((sgn * 1.0, 1.2, 2.3)), Vector((sgn * 1.0, 1.7, 2.9))
        hchain(f"Antler_{sgn}", [a0, a1, a2, a3], 0.32, 0.15, M_HORN)
        bar(f"Head_AntlerTine1_{sgn}", hv(a1), hv((sgn * 1.45, 0.4, 2.2)), 0.17 * HS, M_HORN, H)
        bar(f"Head_AntlerTine2_{sgn}", hv(a2), hv((sgn * 1.6, 1.0, 2.9)), 0.15 * HS, M_HORN, H)
        ANT_TIPS += [((sgn * 1.45, 0.4, 2.2), (sgn * 0.8, -0.4, 0.6)), ((sgn * 1.0, 1.7, 2.9), (sgn * 0.2, 0.3, 1)),
                     ((sgn * 1.6, 1.0, 2.9), (sgn * 0.8, 0, 0.6))]
    else:
        a1, a2, a3 = Vector((sgn * 0.9, 0.9, 1.8)), Vector((sgn * 1.2, 1.6, 2.9)), Vector((sgn * 1.25, 2.3, 3.6))
        hchain(f"Antler_{sgn}", [a0, a1, a2, a3], 0.34, 0.16, M_HORN)
        bar(f"Head_AntlerTine1_{sgn}", hv(a1), hv((sgn * 1.7, 0.4, 2.6)), 0.19 * HS, M_HORN, H)
        bar(f"Head_AntlerTine2_{sgn}", hv(a2), hv((sgn * 1.9, 1.3, 3.7)), 0.17 * HS, M_HORN, H)
        bar(f"Head_AntlerTine3_{sgn}", hv(a2.lerp(a3, 0.4)), hv((sgn * 0.8, 2.0, 3.9)), 0.15 * HS, M_HORN, H)
        bar(f"Head_AntlerTine4_{sgn}", hv(a1.lerp(a2, 0.5)), hv((sgn * 0.55, 0.5, 2.9)), 0.14 * HS, M_HORN, H)
        shard(f"Head_AntlerTip_{sgn}", 0.2 * HS, 0.12 * HS, 0.5 * HS, hv(a3), hv((sgn * 0.1, 0.6, 1)), M_GOLD, H)
        ANT_TIPS += [((sgn * 1.7, 0.4, 2.6), (sgn * 0.8, -0.5, 0.4)), ((sgn * 1.9, 1.3, 3.7), (sgn * 0.8, 0, 0.6)),
                     ((sgn * 0.8, 2.0, 3.9), (0, 0.2, 1)), ((sgn * 0.55, 0.5, 2.9), (sgn * 0.2, -0.6, 0.7))]

# Feuilles lumineuses qui poussent sur les bois
for sgn in (-1, 1):
    for k in range(ANT_LEAVES):
        yy = 0.8 + 0.5 * k
        hleaf(f"AntlerLeaf_{sgn}_{k}", 0.4, 0.9, (sgn * (0.85 + 0.1 * k), yy, 1.6 + 0.55 * k), (sgn * 0.6, 0.3, 1), leaf_mat(0.6), up=(0, 1, 0), t=0.05)

# Fleurs de cerisier au bout des bois (signe distinctif : bois de cerisier en fleur)
per_side = max(1, len(ANT_TIPS) // 2)
for idx, (loc, nrm) in enumerate(ANT_TIPS):
    if (idx % per_side) < BLOSSOMS:
        blossom(f"Head_AntBlossom_{idx}", hv(loc), nrm, 0.32 * HS, H)

# Fleurs roses lumineuses piquées dans la crinière
for k in range(MANE_FLOWERS):
    ang = math.radians(-120 + k * (240 / max(1, MANE_FLOWERS - 1)))
    rad = Vector((math.sin(ang), 0, math.cos(ang)))
    blossom(f"Head_ManeFlower_{k}", hv((rad.x * 1.05, 0.75, rad.z * 1.0)), rad * 0.6 + Vector((0, -1, 0)), 0.3 * HS, H)

# Moustaches dorées (bébé : courtes ; ado : moyennes ; adulte : longues, relevées en boucle)
for sgn in (-1, 1):
    if IS_BEBE:
        pts = [(sgn * 0.5, SNF + 0.2, 0.0), (sgn * 1.1, SNF + 0.5, -0.15), (sgn * 1.5, SNF + 1.4, 0.15)]
    elif IS_ADO:
        pts = [(sgn * 0.55, SNF + 0.2, 0.0), (sgn * 1.3, SNF + 0.3, -0.15), (sgn * 1.9, SNF + 1.1, 0.2),
               (sgn * 2.0, SNF + 2.0, 0.9)]
    else:
        pts = [(sgn * 0.6, SNF + 0.2, 0.0), (sgn * 1.4, SNF + 0.2, -0.2), (sgn * 2.1, SNF + 0.9, 0.1),
               (sgn * 2.3, SNF + 1.9, 0.9), (sgn * 2.0, SNF + 2.7, 1.7), (sgn * 1.6, SNF + 3.0, 1.5)]
    hchain(f"Whisker_{sgn}", pts, 0.13, 0.08, M_GOLD)

# Signe distinctif : la pousse lumineuse entre les bois (bébé : grande, 2 feuilles ; adulte : plus fine)
SPR = SPROUT
hchain("SproutStem", [(0, 0.2, 0.7), (0, 0.15, 0.7 + 0.5 * SPR), (0, 0.1, 0.7 + 0.95 * SPR)], 0.16, 0.1, M_LEAF3)
for sgn in (-1, 1):
    hshard(f"SproutLeaf_{sgn}", 0.7 * SPR, 0.07, 1.4 * SPR, (0, 0.1, 0.7 + 0.9 * SPR), (sgn * 0.85, -0.1, 0.6), M_GLOW, up=(0, 1, 0))
hshard("SproutBud", 0.5 * SPR, 0.07, 1.0 * SPR, (0, 0.1, 0.7 + 0.95 * SPR), (0, -0.1, 1), M_LEAF1, up=(1, 0, 0))

# ----------------------------------------------------------
# 10. CORPS : spine en S, segments, ventre en plaques, flancs, crête, plastron, épaulières
# ----------------------------------------------------------
SPINE = resample(sample_curve(CTRL), STEP)
N = len(SPINE) - 1

def radius(s):
    return keyed(RADIUS_KEYS, s) * RK

def frame_at(s):
    i = min(N - 1, max(0, int(s * N)))
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = frame(SPINE[i + 1] - SPINE[i])
    return mid, t, d, side, radius(s)

BVL = 0.06 * RK
for i in range(N):
    p1, p2 = SPINE[i], SPINE[i + 1]
    L = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / N
    r = radius(s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    is_body = s < BODY_S
    parent = body_root if is_body else tail_root
    tag = "Body" if is_body else "Tail"

    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R, M_BODY, parent, bevel=BVL)

    if s < 0.86:
        B(f"{tag}_Belly_{i}", (2 * r * 0.86, L * 0.84, 0.2 * RK), mid - d * (r * 0.95), R, M_CREAM, parent)
        if FLANKS and is_body:
            for sgn in (-1, 1):
                B(f"{tag}_Flank_{i}_{sgn}", (0.1 * RK, L * 0.86, r * 0.9), mid + side * sgn * r - d * r * 0.3,
                  R, M_LEAF1 if i % 2 == 0 else M_BODY2, parent)
    # Nervures lumineuses (rendu Épique) : un trait lime émissif sur chaque flanc
    if VEINS and s < 0.85:
        for sgn in (-1, 1):
            B(f"{tag}_Vein_{i}_{sgn}", (0.06 * RK, L * 0.9, 0.09 * RK), mid + side * sgn * (r * 1.02 + 0.03) - d * r * 0.05,
              R @ Euler((math.radians(18 * math.sin(i * 0.8)), 0, 0)).to_matrix(), M_GLOW, parent)
    # Écailles-feuilles sur les flancs (pointe vers l'arrière)
    if SCALES and i % SCALE_STEP == SCALE_STEP - 1 and s < 0.9:
        for sgn in (-1, 1):
            shard(f"{tag}_Scale_{i}_{sgn}", r * 0.7, 0.07 * RK, r * 0.95, mid + side * sgn * (r - 0.03) + d * r * 0.25,
                  t * 1.0 + side * sgn * 0.3, M_BODY2, parent, up=tuple(side * sgn))

    # Plaque dorsale sombre + bandes dorées sur la queue
    if DORSAL and s < 0.9:
        B(f"{tag}_Dorsal_{i}", (2 * r * 0.7, L * 0.8, 0.14 * RK), mid + d * (r * 0.97), R @ Euler((math.radians(-8), 0, 0)).to_matrix(), M_DARK, parent)
    if TAIL_BANDS and not is_body and i % 3 == 0 and s < 0.93:
        B(f"{tag}_Band_{i}", (2 * r * 1.08, 0.2 * RK, 2 * r * 1.02), mid, R, M_GOLD, parent)

    # Crête dorsale : feuilles plates en losange, parfois lumineuses
    if CREST and (i % CREST_STEP == 0) and 0.05 < s < 0.92:
        fade = 1.0 if s < 0.7 else (0.92 - s) / 0.22
        base = mid + d * r * 0.85
        mat = leaf_mat(0.28)
        leaf_plate(f"{tag}_Crest_{i}", base, d + t * 0.75, (0.95 * r + 0.4) * RK * fade + 0.2, (0.85 * r + 0.15), mat, parent,
                   up=tuple(side), t=0.1 * RK)
        if GOLD and i % 4 == 0 and s < 0.7:
            shard(f"{tag}_CrestGold_{i}", 0.3 * r, 0.08 * RK, 0.7 * RK, base - t * 0.2, d + t * 0.5, M_GOLD, parent, up=tuple(side))

    # Crinière qui coule le long du cou
    if s < NECK_S:
        fade = 1.0 - s / NECK_S
        for k, amt in enumerate(NECK_LEAF_X):
            leaf_plate(f"Body_NeckLeaf_{i}_{k}", mid + d * r * 0.8 + side * amt * r, d + t * 0.9 + side * amt * 0.5,
                       (0.9 + 0.8 * fade) * RK + random.random() * 0.3, 0.7 * RK + 0.1, leaf_mat(0.3), body_root,
                       up=tuple(d), t=0.1 * RK)
        if NECK_SIDE:
            for sgn in (-1, 1):
                shard(f"Body_NeckSide_{i}_{sgn}", 0.45 * RK, 0.09, (0.6 + 0.4 * fade) * RK,
                      mid + side * sgn * r * 0.85, side * sgn + t * 0.8 + d * 0.3, pick(LEAFS, [3, 4, 2]), body_root)


# Liane fleurie qui serpente le long du corps (un côté), avec petites feuilles et fleurs roses
if VINES:
    vp = []
    for i in range(0, N + 1):
        s = i / N
        if s > 0.9:
            break
        t, d, side = frame(SPINE[min(N, i + 1)] - SPINE[max(0, i - 1)])
        r = radius(s)
        w = math.sin(i * 0.9)
        vp.append(SPINE[i] + side * r * (0.98 + 0.05 * w) + d * r * 0.35 * w)
    for i in range(len(vp) - 1):
        bar(f"Body_Vine_{i}", vp[i], vp[i + 1], 0.1 * RK, M_LEAF3, body_root)
        if i % 3 == 1:
            t, d, side = frame(vp[i + 1] - vp[i])
            leaf_plate(f"Body_VineLeaf_{i}", vp[i], side + t * 0.6 + d * 0.3, 0.7 * RK, 0.4 * RK, leaf_mat(0.4), body_root, up=tuple(d), t=0.05 * RK)
        if i % 4 == 2:
            t, d, side = frame(vp[i + 1] - vp[i])
            blossom(f"Body_VineFlower_{i}", vp[i] + side * 0.08, side + d * 0.2, 0.26 * RK, body_root)

# Plastron d'armure + épaulières brunes à franges dorées
cmid, ct, cd, cside, cr = frame_at(FRONT_S)
CR = seg_matrix(ct, cd, cside)
if CHEST:
    B("Body_ChestPlate", (2 * cr * 1.0, 1.3 * RK, 0.22 * RK), cmid - cd * (cr + 0.04), CR, M_BROWN, body_root, bevel=0.04 * RK)
    B("Body_ChestGold", (2 * cr * 0.62, 0.9 * RK, 0.12 * RK), cmid - cd * (cr + 0.16 * RK), CR, M_GOLD, body_root, bevel=0.03 * RK)
    crystal("Body_ChestGem", 0.24 * RK, 0.14 * RK, 0.22 * RK, cmid - cd * (cr + 0.2 * RK), -cd, M_GEM, body_root, up=tuple(ct))
    for sgn in (-1, 1):
        shard(f"Body_ChestFrame_{sgn}", 0.26 * RK, 0.09, 0.6 * RK, cmid - cd * (cr + 0.22 * RK) + cside * sgn * 0.3 * RK,
              cside * sgn * 0.6 - ct * 1.0, M_GOLD, body_root)
if PADS:
    for sgn in (-1, 1):
        wedge(f"Body_Pad_{sgn}", (cr * 0.95 * PADK, 1.2 * RK * PADK, 0.34 * RK), cmid + cside * sgn * (cr + 0.1 * RK) + cd * 0.25 * RK,
              basis(cside * sgn * 0.7 + ct * 0.1 - cd * 0.5, tuple(cd)), M_BROWN, body_root, top_x=0.8, top_y=0.8, bevel=0.04 * RK)
        for k in range(PAD_FEATHERS):
            shard(f"Body_PadFeather_{sgn}_{k}", 0.36 * RK, 0.07, (0.9 - 0.12 * k) * RK,
                  cmid + cside * sgn * (cr + 0.35 * RK) + cd * (0.25 - 0.15 * k) * RK + ct * (0.4 - 0.4 * k) * RK,
                  cside * sgn * 0.5 + ct * 0.7 + cd * (0.1 - 0.3 * k), M_GOLD if k % 2 == 0 else M_DGOLD, body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, 2 os, bracelet doré, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = 0.28 * LS

def leg(name, s, fwd, bend, th_up, th_lo, hind):
    mid, t, d, side, r = frame_at(s)
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.8 - d * 0.12 * LS
        fz = (FOOT_Z if FOOT_Z is not None else root.z - LEG_DROP)
        wrist = Vector((root.x + sgn * 0.3 * LS, root.y + fwd, fz + FOOT_H + 0.1 * LS))
        knee = root.lerp(wrist, 0.5) + Vector((sgn * 0.22 * LS, bend, 0.0))
        wedge(f"{n}_Shoulder", (th_up * 1.5, th_up * (1.9 if hind else 1.6), th_up * 1.5), root, mat=M_BODY, parent=legs_root,
              top_x=0.85, top_y=0.8, shift_y=0.0, bevel=0.06 * LS)
        bar(f"{n}_Upper", root, knee, th_up, M_BODY, legs_root, up=(1, 0, 0))
        bar(f"{n}_Lower", knee, wrist, th_lo, M_BODY2, legs_root, up=(1, 0, 0))
        if LEG_GOLD:
            bar(f"{n}_Cuff", knee.lerp(wrist, 0.45), knee.lerp(wrist, 0.85), th_lo * 1.4, M_GOLD, legs_root, up=(1, 0, 0))
            B(f"{n}_CuffTop", (th_lo * 1.55, th_lo * 1.55, 0.09 * LS), knee.lerp(wrist, 0.47), None, M_DGOLD, legs_root)
        shard(f"{n}_ElbowLeaf", 0.28 * LS, 0.07, 0.65 * LS, knee, (sgn * 0.5, 0.9 if not hind else 1.0, 0.3), M_LEAF1, legs_root)
        # pied : plat + 3 doigts + 3 griffes
        fc = Vector((wrist.x, wrist.y - 0.12 * LS, fz + FOOT_H / 2))
        box(f"{n}_Paw", (th_lo * 1.7, th_lo * 2.0, FOOT_H), fc, mat=M_BODY, parent=legs_root, bevel=0.04 * LS)
        for k in (-1, 0, 1):
            tp = Vector((fc.x + k * th_lo * 0.52, fc.y - th_lo * 1.05, fz + FOOT_H * 0.34))
            B(f"{n}_Toe_{k}", (th_lo * 0.5, th_lo * 0.55, FOOT_H * 0.7), tp, None, M_BODY2, legs_root)
            shard(f"{n}_Claw_{k}", th_lo * 0.36, th_lo * 0.3, th_lo * 0.95, tp - Vector((0, th_lo * 0.2, 0)),
                  (k * 0.22, -1, -0.2), M_CLAW, legs_root)

leg("Legs_Front", FRONT_S, -0.25 * LS, FRONT_BEND * LS, LEG_TH[0], LEG_TH[1], False)
leg("Legs_Back", BACK_S, 0.15 * LS, BACK_BEND * LS, LEG_TH[0] * 1.12, LEG_TH[1] * 1.05, True)

# ----------------------------------------------------------
# 12. (pas d'ailes : dragon oriental) — les épaulières et la crinière tiennent ce rôle
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : bout de queue avec anneau doré et touffe de feuilles
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = frame(SPINE[-1] - SPINE[-2])
rt = radius(1.0)
B("Tail_TipRing", (rt * 3.2, 0.34 * RK, rt * 3.2), tip, seg_matrix(tt_, td_, ts_), M_GOLD if GOLD else M_BROWN, tail_root)
for k in range(TIP_LEAVES):
    a = k / TIP_LEAVES * 2 * math.pi
    spread = ts_ * math.cos(a) + td_ * math.sin(a)
    leaf_plate(f"Tail_TipLeaf_{k}", tip, tt_ + spread * 0.55, TIP_L * (0.85 + 0.3 * random.random()), TIP_L * 0.42,
               M_GLOW if k % 3 == 0 else pick(LEAFS, [4, 3, 2]), tail_root, up=tuple(spread.cross(tt_)), t=0.1 * RK)
leaf_plate("Tail_TipMain", tip, tt_, TIP_L * 1.3, TIP_L * 0.5, M_GLOW, tail_root, up=tuple(td_), t=0.12 * RK)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Feuilles et pousse lumineuses, aura rose, ornements dorés, plastron avec gemme verte,
#     feuilles / étincelles flottantes.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    zmax = HEAD_POS.z + HS * 3.0
    ys = [p.y for p in SPINE]
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (FX_W), random.uniform(min(ys) - 0.5, max(ys) + 0.3),
                    random.uniform(0.3 * zmax, zmax)))
        kind = k % 4
        if kind in (0, 1):
            dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
            leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55,
                       M_GLOW if kind == 0 else M_LEAF1, master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * RK)
        elif kind == 2:
            crystal(f"FX_Spark_{k}", FX_SIZE * 0.1, FX_SIZE * 0.12, FX_SIZE * 0.18, p, (random.uniform(-1, 1), random.uniform(-1, 1), 1), M_SPARK, master, sides=4)
        else:
            crystal(f"FX_Star_{k}", FX_SIZE * 0.11, FX_SIZE * 0.1, FX_SIZE * 0.2, p, (random.uniform(-1, 1), random.uniform(-1, 1), 1), M_PINK, master, sides=4)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
