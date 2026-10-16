import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Sillon · Bébé
#  Rare · Terre · Wyvern · Brute · monde 1
#  - Bébé : petite wyvern trapue debout sur 2 pattes courtes et épaisses, grosse tête (~35 %), museau court
#  - Très grands yeux ambre (blanc + iris + pupille ronde + 2 reflets), pas de crocs, petites cornes beige
#  - Signes distinctifs en petit : corne-SOC grise sur le museau, épines brunes et feuilles d'automne sur crâne et dos
#  - Ailes-bras repliées avec petite griffe en PELLE de pierre, ventre caramel en plaques, queue à plaques de pierre
#  - Rare (touche) : éclats ambre lumineux autour des yeux, iris lumineux, quelques feuilles flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1107)            # même dragon à chaque exécution
TAG = "SILLON_BEBE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 4       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 4000          # budget de triangles de ce stade et de cette rareté
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
#    Terre : brun terracotta + caramel + pierre grise + mousse + feuilles d'automne (ambre, orange, ocre, olive).
#    Rare : un seul accent lumineux discret (veines/fissures ambre, yeux, éclats du masque), strength <= 1.5.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#C98A4C", 0.50)   # corps principal (caramel terracotta, comme le concept)
M_BODY2  = get_mat("BodyScale",  "#A8642F", 0.55)   # écailles, dessus des pattes, orteils
M_DARK   = get_mat("BodyDark",   "#4A2A16", 0.55)   # sourcils, bouche, ombres
M_CREAM  = get_mat("Belly",      "#F2C987", 0.55)   # ventre en plaques, plastron, menton
M_HORN   = get_mat("Horn",       "#E9D4A8", 0.50)   # cornes beige
M_STONE  = get_mat("Stone",      "#9A9486", 0.65)   # corne-soc du museau, plaques de pierre
M_STONE2 = get_mat("StoneDark",  "#6E6B5C", 0.70)   # pierre sombre
M_GREAVE = get_mat("Greave",     "#80905A", 0.70)   # protège-tibias gris-vert moussu
M_GREAVE2 = get_mat("GreaveDark", "#58643C", 0.75)  # bords des protège-tibias
M_CREST  = get_mat("Crest",      "#8A4A22", 0.55)   # épines brunes de la crinière et du dos
M_AMB    = get_mat("LeafAmber",  "#F6B73C", 0.45)   # feuilles ambre
M_ORA    = get_mat("LeafOrange", "#E0761F", 0.45)   # feuilles orange
M_OCH    = get_mat("LeafOchre",  "#C48A2A", 0.50)   # feuilles ocre
M_OLV    = get_mat("LeafOlive",  "#8C9238", 0.50)   # feuilles olive
M_WING   = get_mat("Membrane",   "#A65A33", 0.55)   # membrane des ailes
M_WING2  = get_mat("MembraneSpot", "#7E4127", 0.60) # taches de la membrane
M_BONE   = get_mat("WingBone",   "#6A3B22", 0.55)   # os des ailes
M_CLAW   = get_mat("Claw",       "#F4EAD2", 0.35)   # griffes, crocs, pointes d'aile
M_WHITE  = get_mat("EyeWhite",   "#F6F0DE", 0.30)
M_IRIS   = get_mat("Iris",       "#F7A81C", 0.25, emission="#FFA81C", strength=1.2)   # yeux ambre
M_BLACK  = get_mat("Black",      "#120A06", 0.30)
M_GLOW   = get_mat("Glow",       "#FFB02E", 0.40, emission="#FF9A1A", strength=1.4)   # veines et fissures ambre
LEAFS = [M_AMB, M_ORA, M_OCH, M_OLV]
LEAFW = [4, 4, 3, 2]


# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
BW = 2.7                 # largeur du torse
BH = 2.6                 # hauteur du torse
LEG_H = 2.1              # hauteur des pattes (hanche -> sol)
TL = 3.6                 # longueur du torse
PITCH = 10               # inclinaison du torse vers l'avant (degrés)
NECK_L = 1.1             # hauteur du cou
NECK_FWD = 0.45          # avancée du cou
NECK_N = 2               # nombre de maillons du cou
NECK_R = (1.15, 1.0)     # rayon du cou (base, haut)
NECK_LEAF = False        # feuilles sur la nuque
HEAD_SCALE = 1.75        # taille de la tête
SNOUT_K = 0.6            # longueur du museau
FANGS = 0                # crocs par côté
CHEEK_N = 1              # éclats de joue
MANE_RINGS = 1           # rangées de la collerette de feuilles
MANE_N = 7               # feuilles par rangée
MASK_N = 2               # éclats ambre autour de chaque œil
CROWN_N = 3              # épines sur le crâne
BELLY_N = 4              # plaques de ventre
FLANK_ROWS = 2
FLANK_COLS = 3
CREST_N = 4              # épines du dos
SHOULDER_LEAVES = 2
CHEST_LEAVES = 1
CRACKS_BODY = 0          # fissures lumineuses par flanc
CRACK_NECK = False
LEG_TH_K = 0.56          # épaisseur des pattes (fraction de BW)
THIGH_LEAVES = 1
CRACKS_LEG = 0
WING_SPAN = 4.4
WING_ELBOW = (0.42, 0.3, 0.34)
WING_WRIST = (0.3, -0.12, 0.55)   # x, y en fraction d'envergure ; z = hauteur du poignet en fraction de LEG_H
WING_TIPS = [(0.45, 0.3, 0.8), (0.42, 0.65, 0.58), (0.28, 0.9, 0.28)]
WING_BONE = 0.3
WING_MEMB_T = 0.1
WING_SPOTS = 2
CRACKS_WING = False
TAIL_L = 4.4
TAIL_STEP = 0.75
TAIL_BEV_N = 6
TAIL_SCALES = False
CRACK_TAIL = False
TAIL_BLADE = 1.3
TAIL_GLOW = False
FX_N = 5
FX_SIZE = 0.6

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
#    Wyvern : 2 pattes arrière, tronc penché vers l'avant, les ailes servent de bras (poignet posé devant).
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.2                                    # échelle des petits détails
HS = HEAD_SCALE
P = math.radians(PITCH)
F = Vector((0, -math.cos(P), -math.sin(P)))      # axe du torse, vers l'avant (penché)
SIDEV = Vector((1, 0, 0))
UPT = F.cross(SIDEV)                             # "haut" du torse (perpendiculaire à F)
RT = basis(F)                                    # rotation des blocs du torse
HIP_Z = LEG_H                                    # hauteur de la hanche
ZC = HIP_Z + BH * 0.3 - 0.3 * TL * math.sin(P)   # centre du torse
C = Vector((0, 0, ZC))
PELVIS = C - F * (0.3 * TL)
CHEST = C + F * (0.3 * TL)
NECK_BASE = CHEST + F * (0.17 * TL) + UPT * (BH * 0.28)
NECK_TOP = NECK_BASE + Vector((0, -NECK_FWD, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.25 * HS, 0.35 * HS))
HEAD_PITCH = 12                                  # degrés : la tête regarde un peu vers le bas
TAIL_START = PELVIS + Vector((0, 0.2 * TL, 0.0))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def tpos(s, up=0.0, side=0.0):
    """Point du torse : s = position le long de l'axe (en fraction de TL, + vers l'avant)."""
    return C + F * (s * TL) + UPT * up + SIDEV * side

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, soc, bois)."""
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

def zigzag(p0, p1, jit, n, amp):
    """Ligne brisée de p0 à p1 (fissure) : décalage alterné 'jit' * amp."""
    p0, p1, jit = Vector(p0), Vector(p1), Vector(jit)
    pts = [p0]
    for i in range(1, n):
        pts.append(p0.lerp(p1, i / n) + jit * amp * (1 if i % 2 else -1) * random.uniform(0.6, 1.2))
    pts.append(p1)
    return pts

def crack(name, pts, th, parent, up=(0, 0, 1)):
    """Fissure lumineuse ambre : petites barres émissives, posées sur la surface."""
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        link(f"{name}_{i}", pts[i], pts[i + 1], th, M_GLOW, parent, up, extra=th * 0.5, bevel=0, depth=th * 0.7)

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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1), depth=None):
    bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up, None if depth is None else depth * HS)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODY2)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Signe distinctif : la corne-SOC de charrue sur le museau (large lame plate qui se recourbe vers l'avant et le haut)
SF = SNOUT_FRONT
hbox("SocBase", (0.95, 0.75, 0.3), (0, SF + 0.55, 0.3), mat=M_STONE, bevel=0.04)
SOC_N = 3 if not IS_BEBE else 2
soc_pts = [(0, SF + 0.6, 0.38), (0, SF + 0.05, 0.62), (0, SF - 0.35, 1.0), (0, SF - 0.5, 1.4)]
if IS_BEBE:
    soc_pts = [(0, SF + 0.55, 0.38), (0, SF + 0.1, 0.6), (0, SF - 0.1, 0.95)]
widths = [0.95, 0.7, 0.42] if not IS_BEBE else [0.8, 0.5]
for i in range(len(soc_pts) - 1):
    hbar(f"Soc_{i}", soc_pts[i], soc_pts[i + 1], widths[i], M_STONE, up=(1, 0, 0), depth=0.26 - 0.05 * i)
hshard("SocTip", 0.4, 0.14, 0.45, soc_pts[-1], (0, -0.35, 1), M_STONE2, up=(1, 0, 0))
if not IS_BEBE:
    hbox("SocBand", (1.0, 0.16, 0.34), (0, SF + 0.25, 0.46), rot=(-25, 0, 0), mat=M_STONE2)

# Yeux : blanc, iris, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
        hbox(f"Brow_{sgn}", (0.12, 0.8, 0.14), (sgn * 0.97, ey - 0.02, ez + 0.6), rot=(8, 0, 0), mat=M_DARK)
    else:
        # sourcils sévères en pierre, inclinés vers le museau
        hbox(f"Brow_{sgn}", (0.2, 1.0, 0.26), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(16, 0, 0),
             mat=M_DARK, bevel=0.02)
        hbox(f"BrowStone_{sgn}", (0.24, 0.6, 0.18), (sgn * 0.99, ey - 0.35, ez + 0.72), rot=(16, 0, 0), mat=M_STONE2)
    # Masque d'éclats ambre autour de l'œil (lueur discrète)
    for k in range(MASK_N):
        ang = math.radians(200 + k * 140 / max(1, MASK_N - 1) if MASK_N > 1 else 270)
        off = Vector((0, math.sin(ang), math.cos(ang))) * (0.5 if not IS_BEBE else 0.7)
        hshard(f"Mask_{sgn}_{k}", 0.2, 0.06, 0.45, (sgn * 0.95, ey + off.y, ez + off.z),
               (sgn * 0.6, off.y * 1.3, off.z * 1.3), M_GLOW if k % 2 == 0 else M_AMB, up=(1, 0, 0))

# Crocs (bébé : aucun ; ado : 2 par côté ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles en éclat + feuilles de joue (caramel / ocre)
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.15 if not IS_BEBE else 0.8, (sgn * 0.85, 0.5, 0.2), (sgn * 1, 0.6, 0.3), M_BODY2)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.45, 0.08, 0.85 - 0.1 * k, (sgn * 0.88, -0.1 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick([M_OCH, M_ORA, M_AMB], [3, 3, 2]))

# Collerette de feuilles d'automne derrière le crâne
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hleaf(f"Mane_{ring_i}_{k}", 0.75 - ring_i * 0.1, 1.2 + ring_i * 0.2 + random.random() * 0.3,
              loc, direction, pick(LEAFS, LEAFW), up=tuple(rad))

# Cornes beige : bébé = 2 petits cônes, ado = recourbées + 1 pointe, adulte = longues, recourbées, 2 pointes (rare)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.2), (sgn * 0.7, 0.9, 1.6)],
               0.34, 0.13, M_HORN)
    elif IS_ADO:
        a0, a1 = Vector((sgn * 0.6, 0.25, 0.78)), Vector((sgn * 0.85, 0.5, 1.45))
        a2, a3 = Vector((sgn * 1.0, 1.1, 2.1)), Vector((sgn * 0.85, 1.85, 2.5))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.38, 0.14, M_HORN)
        hbar(f"HornTine_{sgn}", a1, (sgn * 1.4, 0.0, 2.15), 0.2, M_HORN)
    else:
        a0, a1 = Vector((sgn * 0.6, 0.3, 0.78)), Vector((sgn * 0.95, 0.6, 1.6))
        a2, a3 = Vector((sgn * 1.2, 1.4, 2.3)), Vector((sgn * 1.05, 2.3, 2.7))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.44, 0.15, M_HORN)
        # 2e pointe courte vers l'avant (rare) + petite corne basse vers l'arrière (comme le concept)
        hbar(f"HornTine1_{sgn}", a1, (sgn * 1.45, 0.25, 2.05), 0.22, M_HORN)
        hchain(f"HornLow_{sgn}", [(sgn * 0.85, 0.6, 0.35), (sgn * 1.35, 1.2, 0.6), (sgn * 1.6, 1.95, 0.75)], 0.3, 0.12, M_HORN)
        hbox(f"HornRing_{sgn}", (0.62, 0.5, 0.2), a0.lerp(a1, 0.5), rot=(0, sgn * 10, 0), mat=M_STONE2)

# Crête double sur le crâne : rangée centrale d'éclats bruns + feuilles ambre/orange de chaque côté
for k in range(CROWN_N):
    z = 0.8 + 0.02 * k
    hshard(f"Crown_{k}", 0.5, 0.1, (1.0 + 0.2 * CROWN_N * 0.5 - 0.15 * abs(k - CROWN_N / 2)) * 0.9,
           (0, 0.55 + 0.38 * k, z), (0, 0.55, 1), M_CREST, up=(1, 0, 0))
    if not IS_BEBE:
        for sgn in (-1, 1):
            hshard(f"CrownLeaf_{sgn}_{k}", 0.42, 0.08, 0.8, (sgn * 0.35, 0.6 + 0.38 * k, 0.76),
                   (sgn * 0.5, 0.5, 1), pick([M_ORA, M_AMB, M_OCH], [3, 3, 2]), up=(1, 0, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs penchés, cou en plaques, ventre, flancs, crête double, épaulières de pierre
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.1, TL * 0.46, BH * 1.06), CHEST - F * (0.02 * TL), RT, M_BODY, body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.44, BH * 0.96), C, RT, M_BODY, body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 1.0, TL * 0.46, BH * 1.0), PELVIS, RT, M_BODY, body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)
HALF_W = BW * 0.5

# Plastron caramel + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), CHEST + F * (TL * 0.22) - UPT * (BH * 0.08),
    RT, M_CREAM, body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    s = -0.4 + 0.8 * (i + 0.5) / BELLY_N
    pl = (TL * 0.8) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), tpos(s, -BH / 2 + 0.03), RT, M_CREAM, body_root)
    for sgn in (-1, 1):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), tpos(s, -BH * 0.3, sgn * (HALF_W - 0.01)),
          RT, M_CREAM, body_root)

# Écailles-feuilles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            s = -0.36 + 0.74 * (c + 0.5 * (r % 2)) / FLANK_COLS
            up = BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, tpos(s, up, sgn * (HALF_W - 0.03 * SC)),
                  -F + SIDEV * sgn * 0.3 - UPT * 0.1, pick([M_BODY2, M_BODY2, M_OCH]), body_root, up=(sgn, 0, 0))

# Cou : courbe lissée du torse vers la tête, un segment brun + une plaque caramel par maillon
NECK_CTRL = []
for tt in (0.0, 0.33, 0.66, 1.0):
    sm = tt * tt * (3 - 2 * tt)
    NECK_CTRL.append(NECK_BASE + Vector((0, -NECK_FWD * sm, NECK_L * tt)))
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_L * 1.05) / NECK_N)
NN = len(NECK_SPINE) - 1
neck_frames = []
for i in range(NN):
    p1, p2 = NECK_SPINE[i], NECK_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / NN
    r = keyed([(0, NECK_R[0]), (1, NECK_R[1])], s)
    R = basis(p2 - p1)
    dz, sd = R.col[2], R.col[0]               # dz = arrière du cou (dos), sd = côté
    neck_frames.append((mid, r, dz, sd, R, s))
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.25, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - dz * (r * 0.95), R, M_CREAM, body_root)
    # crête de la nuque : épine brune centrale + 2 feuilles
    shard(f"Body_NeckSpine_{i}", 0.5 * SC, 0.1 * SC, (0.95 - 0.35 * s) * SC * 1.2, mid + dz * r * 0.9, dz + (p2 - p1).normalized() * (-0.5),
          M_CREST, body_root, up=tuple(sd))
    if NECK_LEAF:
        for sgn in (-1, 1):
            leaf_plate(f"Body_NeckLeaf_{i}_{sgn}", mid + dz * r * 0.75 + sd * sgn * r * 0.55,
                       dz + sd * sgn * 0.7 - (p2 - p1).normalized() * 0.3, (0.9 + 0.3 * (1 - s)) * SC, 0.7 * SC,
                       pick(LEAFS, LEAFW), body_root, up=tuple(dz), t=0.09 * SC)

# Crête double sur le dos : rangée centrale d'épines brunes + 2 rangées basses de feuilles
for k in range(CREST_N):
    s = -0.38 + 0.78 * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.8 * SC, 0.12 * SC, (1.15 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          tpos(s, BH / 2 - 0.05), -F * 0.45 + UPT, M_CREST, body_root, up=(1, 0, 0))
    for sgn in (-1, 1):
        shard(f"Body_CrestSide_{k}_{sgn}", 0.5 * SC, 0.1 * SC, 0.7 * SC, tpos(s + 0.03, BH * 0.4, sgn * BW * 0.28),
              -F * 0.5 + UPT * 0.8 + SIDEV * sgn * 0.5, pick([M_OCH, M_AMB, M_ORA]), body_root, up=(1, 0, 0))

# Épaulières : dalle de pierre moussue + grappe de feuilles d'automne sur chaque épaule
for sgn in (-1, 1):
    sh = CHEST + SIDEV * sgn * BW * 0.5 + UPT * BH * 0.42 - F * 0.05 * TL
    wedge(f"Body_ShoulderStone_{sgn}", (BW * 0.5, TL * 0.3, 0.3 * SC + 0.2), sh, RT @ Euler((0, math.radians(sgn * 22), 0)).to_matrix(),
          M_GREAVE, body_root, top_x=0.85, top_y=0.85, bevel=0.05 * SC)
    B(f"Body_ShoulderStone2_{sgn}", (BW * 0.34, TL * 0.17, 0.24 * SC + 0.1), sh + F * 0.2 * TL + SIDEV * sgn * 0.08 * BW + UPT * 0.1,
      RT @ Euler((0, math.radians(sgn * 18), 0)).to_matrix(), M_GREAVE2, body_root)
    for k in range(SHOULDER_LEAVES):
        shard(f"Body_ShoulderLeaf_{sgn}_{k}", 0.55 * SC, 0.09 * SC, (1.05 - 0.1 * k) * SC,
              sh + SIDEV * sgn * (0.12 * BW + 0.08 * k * SC) + UPT * (0.1 + 0.1 * k * SC) + F * (-0.35 + 0.2 * k * SC) * SC,
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.35 * k), pick(LEAFS, LEAFW), body_root)
    # feuilles de poitrail (plastron)
    for k in range(CHEST_LEAVES):
        leaf_plate(f"Body_ChestLeaf_{sgn}_{k}", CHEST + F * (TL * 0.24) + SIDEV * sgn * BW * (0.12 + 0.1 * k) + UPT * (BH * (0.2 - 0.14 * k)),
                   -UPT * 0.5 + F + SIDEV * sgn * 0.4, (0.95 - 0.1 * k) * SC, 0.7 * SC, pick(LEAFS, LEAFW), body_root,
                   up=tuple(SIDEV * sgn), t=0.09 * SC)

# Fissures ambre (motif secondaire, lueur discrète) : flancs, cou, épaules
for sgn in (-1, 1):
    for j in range(CRACKS_BODY):
        s0 = -0.25 + 0.4 * j
        pts = zigzag(tpos(s0 + 0.1, BH * 0.42, sgn * (HALF_W + 0.04)), tpos(s0 - 0.08, -BH * 0.3, sgn * (HALF_W + 0.04)),
                     F, 3, 0.18 * SC)
        crack(f"Body_Crack_{sgn}_{j}", pts, 0.07 * SC, body_root, up=(sgn, 0, 0))
    if CRACK_NECK:
        pts = [Vector(neck_frames[i][0]) + neck_frames[i][3] * sgn * (neck_frames[i][1] + 0.03) + neck_frames[i][2] * 0.18 * (1 if i % 2 else -1)
               for i in range(1, NN)]
        crack(f"Body_NeckCrack_{sgn}", pts, 0.07 * SC, body_root, up=(sgn, 0, 0))

# ----------------------------------------------------------
# 11. PATTES ARRIÈRE (wyvern : 2 pattes) : hanche, cuisse, tibia, protège-tibia de pierre moussue, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.16)
LEG_TH = BW * LEG_TH_K
HIP_Y = PELVIS.y - 0.05 * TL
for sgn in (-1, 1):
    x = sgn * (BW * 0.5 - LEG_TH * 0.2)
    hip = Vector((x, HIP_Y, HIP_Z + BH * 0.05))
    knee = Vector((x + sgn * 0.04 * LEG_TH, HIP_Y - LEG_H * 0.28, LEG_H * 0.5))
    ank = Vector((x, HIP_Y + LEG_H * 0.16, FOOT_H + LEG_H * 0.12))
    # hanche + cuisse musclée (wedge + barre épaisse)
    wedge(f"Legs_Haunch_{sgn}", (LEG_TH * 1.35, LEG_TH * 1.9, LEG_H * 0.46 + BH * 0.3), hip - Vector((0, -0.05, LEG_H * 0.12)),
          None, M_BODY, legs_root, top_x=0.8, top_y=0.85, shift_y=LEG_TH * 0.1, bevel=0.1 * SC)
    link(f"Legs_Thigh_{sgn}", hip - Vector((0, 0, LEG_H * 0.1)), knee, LEG_TH * 1.2, M_BODY, legs_root, extra=0.2,
         bevel=0.08 * SC, depth=LEG_TH * 1.45)
    link(f"Legs_Shin_{sgn}", knee, ank, LEG_TH * 0.95, M_BODY2, legs_root, extra=0.15, bevel=0.05 * SC, depth=LEG_TH * 1.0)
    B(f"Legs_Knee_{sgn}", (LEG_TH * 1.15, LEG_TH * 0.7, LEG_TH * 0.9), knee + Vector((0, -LEG_TH * 0.15, 0)), None, M_BODY2, legs_root)
    # protège-tibia moussu avec liseré sombre
    g0, g1 = knee.lerp(ank, 0.22), knee.lerp(ank, 0.85)
    link(f"Legs_Greave_{sgn}", g0, g1, LEG_TH * 1.18, M_GREAVE, legs_root, extra=0.05, bevel=0.04 * SC, depth=LEG_TH * 1.2)
    link(f"Legs_GreaveTop_{sgn}", g0 + (g0 - g1) * 0.02, g0 + (g1 - g0) * 0.12, LEG_TH * 1.28, M_GREAVE2, legs_root, extra=0.03,
         bevel=0, depth=LEG_TH * 1.3)
    link(f"Legs_GreaveBot_{sgn}", g1 - (g1 - g0) * 0.1, g1, LEG_TH * 1.26, M_GREAVE2, legs_root, extra=0.03, bevel=0, depth=LEG_TH * 1.28)
    # cheville + pied plat + 3 doigts + 3 griffes
    B(f"Legs_Heel_{sgn}", (LEG_TH * 0.9, LEG_TH * 0.9, FOOT_H * 1.4), Vector((x, ank.y + LEG_TH * 0.1, FOOT_H * 0.9)), None, M_BODY2, legs_root)
    fy = ank.y - LEG_TH * 0.75
    box(f"Legs_Foot_{sgn}", (LEG_TH * 1.2, LEG_TH * 2.1, FOOT_H), (x, fy, FOOT_H / 2), None, M_BODY, legs_root, bevel=0.06 * SC)
    toe_y = fy - LEG_TH * 1.05 - LEG_TH * 0.1
    for k in (-1, 0, 1):
        B(f"Legs_Toe_{sgn}_{k}", (LEG_TH * 0.3, LEG_TH * 0.5, FOOT_H * 0.72), (x + k * LEG_TH * 0.36, toe_y, FOOT_H * 0.36), None, M_BODY2, legs_root)
        shard(f"Legs_Claw_{sgn}_{k}", LEG_TH * 0.22, LEG_TH * 0.18, LEG_TH * 0.62, (x + k * LEG_TH * 0.36, toe_y - LEG_TH * 0.18, FOOT_H * 0.34),
              (k * 0.12, -1, -0.05), M_CLAW, legs_root)
    # feuilles sur la cuisse
    for k in range(THIGH_LEAVES):
        shard(f"Legs_Leaf_{sgn}_{k}", 0.42 * SC, 0.07 * SC, (0.85 - 0.12 * k) * SC,
              hip.lerp(knee, 0.25 + 0.3 * k) + Vector((sgn * LEG_TH * 0.7, 0, 0)), (sgn * 0.8, 0.4, -0.6), pick(LEAFS, LEAFW), legs_root)
    # fissures ambre : cuisse (côté) et protège-tibia
    for j in range(CRACKS_LEG):
        a = hip.lerp(knee, 0.2 + 0.3 * j) + Vector((sgn * (LEG_TH * 0.68 + 0.04), 0, 0.1))
        b = a + Vector((0, 0.5 * LEG_TH, -LEG_H * 0.2))
        crack(f"Legs_Crack_{sgn}_{j}", zigzag(a, b, (0, 1, 0), 3, 0.16 * SC), 0.07 * SC, legs_root, up=(sgn, 0, 0))
    if CRACKS_LEG:
        a = g0 + Vector((sgn * (LEG_TH * 0.62), 0.0, 0.0))
        b = g1 + Vector((sgn * (LEG_TH * 0.62), 0.0, 0.0))
        crack(f"Legs_GreaveCrack_{sgn}", zigzag(a, b, (0, 1, 0), 4, 0.17 * SC), 0.07 * SC, legs_root, up=(sgn, 0, 0))

# ----------------------------------------------------------
# 12. AILES-BRAS (wyvern) : épaule, coude vers l'arrière, poignet posé devant avec griffe en PELLE,
#     3 doigts qui montent vers l'arrière, grande membrane brune tachetée
# ----------------------------------------------------------
SP = WING_SPAN
SPADE_L = 0.27 * SP
WRIST_Z = LEG_H * WING_WRIST[2] + SPADE_L * 0.2     # poignet replié devant, à mi-hauteur de patte
for sgn in (-1, 1):
    S = CHEST + SIDEV * sgn * BW * 0.48 + UPT * BH * 0.36 - F * 0.02 * TL
    E = S + Vector((sgn * WING_ELBOW[0] * SP, WING_ELBOW[1] * SP, WING_ELBOW[2] * SP))
    W = Vector((sgn * (BW * 0.5 + WING_WRIST[0] * SP), CHEST.y + WING_WRIST[1] * SP, WRIST_Z))
    tips = [W + Vector((sgn * a * SP, b * SP, c * SP)) for (a, b, c) in WING_TIPS]
    Hpt = Vector((sgn * BW * 0.45, PELVIS.y + 0.12 * TL, PELVIS.z + 0.15 * BH))   # bord de fuite accroché au haut de la hanche
    bn = WING_BONE
    link(f"Wings_{sgn}_Arm", S, E, bn * 1.3, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.3)
    link(f"Wings_{sgn}_Fore", E, W, bn * 1.1, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.1)
    wing_shoulder = wedge(f"Wings_{sgn}_Shoulder", (bn * 2.2, bn * 2.2, bn * 2.2), S, None, M_BODY2, wings_root, bevel=0.06 * SC)
    for k, tp in enumerate(tips):
        link(f"Wings_{sgn}_Finger_{k}", W, tp, bn * (0.85 - 0.12 * k), M_BONE, wings_root, up=(0, 1, 0), extra=0.1, bevel=0, depth=bn * 0.85)
        shard(f"Wings_{sgn}_Spike_{k}", bn * 1.7, bn * 1.2, SP * 0.12, tp, tp - W, M_HORN, wings_root)
    # membrane : triangles en éventail autour du poignet
    edge = tips + [Hpt]
    for k in range(len(edge) - 1):
        plate(f"Wings_{sgn}_Memb_{k}", [W, edge[k], edge[k + 1]], WING_MEMB_T, M_WING, wings_root)
    plate(f"Wings_{sgn}_Memb_A", [W, Hpt, S], WING_MEMB_T, M_WING, wings_root)
    plate(f"Wings_{sgn}_Memb_B", [W, S, E], WING_MEMB_T, M_WING, wings_root)
    # taches de membrane (petites plaques plus sombres, posées sur la membrane)
    for k in range(WING_SPOTS):
        i = random.randrange(0, len(tips) - 1)
        c = (W + tips[i] + tips[i + 1]) / 3 + (W - tips[i]) * random.uniform(-0.05, 0.1)
        sz = SP * random.uniform(0.04, 0.07)
        plate(f"Wings_{sgn}_Spot_{k}", [c + Vector((0, sz, 0)), c + Vector((sz * 0.9, 0, sz * 0.4)), c + Vector((0, -sz, 0)), c + Vector((-sz * 0.9, 0, -sz * 0.4))],
              WING_MEMB_T * 1.6, M_WING2, wings_root)
    # poignet : griffe en pelle (plaque pentagonale posée devant) + 2 petites griffes
    fd = Vector((sgn * 0.12, -1, -0.75)).normalized()   # la pelle pointe vers l'avant et le bas
    lat = Vector((1, 0, 0))
    nrm = fd.cross(lat).normalized()                     # dessus de la pelle
    w_ = 0.2 * SP
    base = W + Vector((0, 0, -0.02))
    sp = [base - lat * w_ * 0.45 + fd * SPADE_L * 0.05, base + lat * w_ * 0.45 + fd * SPADE_L * 0.05,
          base + lat * w_ * 0.6 + fd * SPADE_L * 0.55, base + fd * SPADE_L, base - lat * w_ * 0.6 + fd * SPADE_L * 0.55]
    plate(f"Wings_{sgn}_Spade", sp, 0.2 * SC + 0.05, M_STONE, wings_root)
    plate(f"Wings_{sgn}_SpadeRim", [base + (sp[0] - base) * 0.0 + fd * SPADE_L * 0.1 + nrm * (0.14 * SC),
                                    base + lat * w_ * 0.3 + fd * SPADE_L * 0.6 + nrm * (0.14 * SC),
                                    base + fd * SPADE_L * 0.9 + nrm * (0.14 * SC),
                                    base - lat * w_ * 0.3 + fd * SPADE_L * 0.6 + nrm * (0.14 * SC)], 0.05 * SC, M_STONE2, wings_root)
    B(f"Wings_{sgn}_WristBlock", (bn * 2.0, bn * 2.2, bn * 1.8), W, None, M_STONE, wings_root)
    for k in (-1, 1):
        shard(f"Wings_{sgn}_Claw_{k}", 0.22 * SC, 0.16 * SC, SPADE_L * 0.55, W + Vector((k * bn * 0.9, -0.1, -0.02)), (k * 0.25, -1, -0.75), M_CLAW, wings_root)
    # fissure ambre sur l'avant-bras
    if CRACKS_WING:
        a = E.lerp(W, 0.25) + Vector((0, 0, 0.0))
        b = E.lerp(W, 0.85)
        crack(f"Wings_{sgn}_Crack", zigzag(a, b, (1, 0, 0), 3, 0.14 * SC), 0.07 * SC, wings_root, up=(0, 1, 0))

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques de pierre sur le dos, crête, pointe en soc
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.15, 0.0), (0.45, -0.28, 0.25), (0.7, -0.22, 0.1), (0.9, 0.02, -0.2), (1.0, 0.2, -0.3)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * TAIL_L * 0.35)))
TAIL_R = [(0.0, BW * 0.40), (0.3, BW * 0.34), (0.6, BW * 0.25), (0.85, BW * 0.17), (1.0, BW * 0.12)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_R, s)
    R = basis(p2 - p1)
    dz, sd = R.col[2], R.col[0]
    t_ = (p2 - p1).normalized()
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.3, 2 * r * 0.95), mid, R, M_BODY, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - dz * (r * 0.95), R, M_CREAM, tail_root)
    # plaques de pierre sur le dos (une sur deux) + épine brune sinon
    if i % 2 == 0 and s < 0.88:
        wedge(f"Tail_Plate_{i}", (2 * r * 0.9, Ln * 1.05, 0.26 * SC + r * 0.25), mid + dz * (r * 0.92), R, M_STONE, tail_root,
              top_x=0.75, top_y=0.85, bevel=0)
    else:
        shard(f"Tail_Crest_{i}", 0.8 * r + 0.2, 0.1 * SC, 0.5 * SC + r * 0.8, mid + dz * r * 0.85, dz + t_ * 0.7, M_CREST, tail_root, up=tuple(sd))
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + sd * sgn * (r - 0.03), sd * sgn * 0.3 + t_,
                  pick([M_BODY2, M_OCH]), tail_root, up=(sgn, 0, 0))
if CRACK_TAIL:
    for j in (1, 3):
        if j < TN - 2:
            a = TAIL_SPINE[j]; b = TAIL_SPINE[j + 1]
            R = basis(b - a); dz = R.col[2]; sd = R.col[0]
            r = keyed(TAIL_R, j / TN)
            pts = zigzag(a + dz * (r + 0.03) - sd * r * 0.7, a + dz * (r + 0.03) + sd * r * 0.7, (b - a).normalized(), 4, 0.25 * SC)
            crack(f"Tail_Crack_{j}", pts, 0.07 * SC, tail_root, up=(0, 0, 1))
tip = TAIL_SPINE[-1]
tt_ = (TAIL_SPINE[-1] - TAIL_SPINE[-2]).normalized()
RT_TIP = basis(tt_)
B("Tail_TipBlock", (BW * 0.3, 0.6 * SC, BW * 0.3), tip, RT_TIP, M_STONE2, tail_root)
# pointe en soc : lame de pierre pentagonale + 2 feuilles
tdz, tsd = RT_TIP.col[2], RT_TIP.col[0]
Lb = TAIL_BLADE
blade = [tip + tsd * Lb * 0.12, tip - tsd * Lb * 0.12, tip - tsd * Lb * 0.3 + tt_ * Lb * 0.5, tip + tt_ * Lb * 1.05, tip + tsd * Lb * 0.3 + tt_ * Lb * 0.5]
plate("Tail_Blade", blade, 0.22 * SC, M_STONE, tail_root)
plate("Tail_BladeInner", [tip + tsd * Lb * 0.06 + tdz * 0.05, tip - tsd * Lb * 0.06 + tdz * 0.05, tip + tt_ * Lb * 0.8 + tdz * 0.05], 0.3 * SC, M_GLOW if TAIL_GLOW else M_STONE2, tail_root)
leaf_plate("Tail_TipLeaf_A", tip, tt_ * 0.5 + tsd, TAIL_BLADE * 0.6, TAIL_BLADE * 0.35, M_ORA, tail_root, up=tuple(tdz), t=0.1 * SC)
leaf_plate("Tail_TipLeaf_B", tip, tt_ * 0.5 - tsd, TAIL_BLADE * 0.6, TAIL_BLADE * 0.35, M_AMB, tail_root, up=tuple(tdz), t=0.1 * SC)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (fissures ambre, taches de membrane), cornes à 2 pointes, crête double,
#     lueur discrète (yeux, fissures, éclats du masque, <= 1.5). FX : feuilles d'automne et quelques braises.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (SP * 0.6 + BW), random.uniform(-TL * 0.9 - NECK_FWD, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.8, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 4 == 3:
            crystal(f"FX_Ember_{k}", FX_SIZE * 0.12, FX_SIZE * 0.2, FX_SIZE * 0.14, p, dirv, M_GLOW, master, sides=4)
        else:
            leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55, pick(LEAFS, LEAFW),
                       master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
