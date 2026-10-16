import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Tempête · Bébé
#  Épique · Vol · Wyvern · Brute · monde 4
#  - Bébé : petite wyvern trapue debout sur 2 pattes courtes et épaisses, grosse tête (~35 %), museau court
#  - Très grands yeux bleu glacier lumineux (blanc + iris + pupille ronde + 2 reflets), pas de crocs, petites cornes anthracite
#  - Signes distinctifs en petit : crinière de nuage blanc et gris, ailes-bras à bord effiloché en nuages, spirale de vent claire
#  - Ventre gris clair en plaques, queue terminée par une touffe de nuage
#  - Épique (touche) : iris et spirales de vent lumineux, quelques nuages et éclats flottants
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4417)            # même dragon à chaque exécution
TAG = "TEMPETE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 4       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 5000          # budget de triangles de ce stade et de cette rareté
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
#    Vol : gris orage bleuté + blanc nuage + bleu glacier lumineux. Épique : émission 2 à 2,5 (iris, vents, éclats), or discret.
#    Pas d'éclairs : la Foudre est un élément futur du jeu.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#6B80A2", 0.50)   # corps principal, gris orage bleuté
M_BODY2  = get_mat("BodyScale",  "#4D5F80", 0.55)   # écailles, dessus des pattes, orteils
M_DARK   = get_mat("BodyDark",   "#2C3650", 0.55)   # sourcils, bouche, ombres, genoux
M_CREAM  = get_mat("Belly",      "#EAF0F8", 0.55)   # ventre en plaques, plastron, menton
M_CLOUD  = get_mat("Cloud",      "#F6FAFF", 0.80)   # nuage blanc (crinière, bords d'ailes)
M_CLOUD2 = get_mat("CloudGrey",  "#B3C1D6", 0.80)   # nuage gris clair
M_CLOUD3 = get_mat("CloudDark",  "#8E9CB8", 0.80)   # nuage d'orage sombre
M_HORN   = get_mat("Horn",       "#2D3342", 0.45)   # cornes anthracite
M_WING   = get_mat("Membrane",   "#8EA3C6", 0.55)   # membrane des ailes (gris orage)
M_WING2  = get_mat("MembraneBand", "#B4C6E0", 0.55) # bandes claires de la membrane
M_BONE   = get_mat("WingBone",   "#5A6A8A", 0.55)   # os des ailes
M_CLAW   = get_mat("Claw",       "#2D3342", 0.35)   # griffes, crocs anthracite
M_FANG   = get_mat("Fang",       "#EEF2F8", 0.35)   # crocs
M_WHITE  = get_mat("EyeWhite",   "#F2F6FC", 0.30)
M_IRIS   = get_mat("Iris",       "#7FC8F0", 0.25, emission="#7FC8F0", strength=2.4)   # yeux bleu glacier
M_BLACK  = get_mat("Black",      "#0A0D14", 0.30)
M_GLOW   = get_mat("WindGlow",   "#CBE9FF", 0.35, emission="#8FD2FF", strength=2.2)   # spirales de vent lumineuses
M_GOLD   = get_mat("Gold",       "#D8B050", 0.30, metallic=0.85)                       # ornements dorés (Épique)
CLOUDS = [M_CLOUD, M_CLOUD, M_CLOUD2, M_CLOUD3]
CLOUDW = [5, 4, 4, 2]


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
NECK_PUFFS = False       # nuages sur les côtés du cou
HEAD_SCALE = 1.75        # taille de la tête
SNOUT_K = 0.6            # longueur du museau
FANGS = 0                # crocs par côté
CHEEK_N = 1              # nuages de joue
MANE_RINGS = 1           # anneaux de la crinière de nuage
MANE_N = 8               # nuages par anneau
WIND_EYE = 0              # éclats de vent lumineux au coin de chaque oeil
CROWN_N = 3              # éclats sur le crâne
GOLD = False              # ornements dorés
BELLY_N = 4              # plaques de ventre
FLANK_ROWS = 2
FLANK_COLS = 3
CREST_N = 4              # nuages et éclats du dos
CREST_SIDE = False
SHOULDER_PUFFS = 1
SWIRL_FLANK = 1          # spirales de vent par flanc
SWIRL_N = 6                # barres par spirale
LEG_TH_K = 0.56           # épaisseur des pattes (fraction de BW)
THIGH_PUFFS = 1
SWIRL_LEG = False
WING_SPAN = 4.4
WING_ELBOW = (0.42, 0.3, 0.34)
WING_WRIST = (0.3, -0.12, 0.55)   # x, y en fraction d'envergure ; z = hauteur du poignet en fraction de LEG_H
WING_TIPS = [(0.45, 0.3, 0.8), (0.42, 0.65, 0.58), (0.28, 0.9, 0.28)]
WING_BONE = 0.3
WING_MEMB_T = 0.1
FRAY_N = 2                # nuages par côté du bord effiloché
SWIRL_WING = 0            # spirales sur chaque membrane
TAIL_L = 4.4
TAIL_STEP = 0.75
TAIL_BEV_N = 6
TAIL_SCALES = False
SWIRL_TAIL_AT = [2]    # segments de queue qui portent une spirale
TAIL_TUFT = 1.3            # taille de la touffe de nuage au bout
FX_N = 6
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
    """Suite de barres qui s'affinent (cornes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def puff(name, c, r, mat, parent):
    """Bloc de nuage : cube tourné au hasard (reproductible), sans biseau."""
    rot = (random.uniform(0, 90), random.uniform(0, 90), random.uniform(0, 90))
    return box(name, (r * random.uniform(0.85, 1.25), r * random.uniform(0.85, 1.25), r * random.uniform(0.8, 1.15)),
               c, rot, mat, parent, 0.0)

def cloud(name, c, r, parent, n=2, spread=0.55, mats=None):
    """Petit nuage facetté : n blocs qui se chevauchent, blanc / gris / orage."""
    c = Vector(c)
    for i in range(n):
        off = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.6, 1))) * r * spread * (0 if i == 0 else 1)
        m = (mats[i % len(mats)] if mats else pick(CLOUDS, CLOUDW))
        puff(f"{name}_{i}", c + off, r * (1.0 - 0.18 * i), m, parent)

def swirl(name, c, u, v, r, turns, th, parent, nrm, n=7):
    """Spirale de vent lumineuse : petites barres émissives posées en spirale sur la peau
    (c = centre, u et v = axes du plan, nrm = normale de la surface)."""
    c, u, v = Vector(c), Vector(u).normalized(), Vector(v).normalized()
    pts = []
    for i in range(n + 1):
        a = i / n * turns * 2 * math.pi
        rr = r * (0.2 + 0.8 * i / n)
        pts.append(c + u * math.cos(a) * rr + v * math.sin(a) * rr)
    for i in range(n):
        link(f"{name}_{i}", pts[i], pts[i + 1], th, M_GLOW, parent, up=tuple(nrm), extra=th * 0.5, bevel=0, depth=th * 0.7)

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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1), depth=None):
    bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up, None if depth is None else depth * HS)

def hcloud(name, loc, r, n=2, mats=None, spread=0.55):
    cloud("Head_" + name, hv(loc), r * HS, H, n, spread, mats)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODY2)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K
SF = SNOUT_FRONT
# Dessus du museau : petite crête de nuage blanc qui court de l'arête vers le front
hbox("SnoutCap", (0.9, 0.8 * SNOUT_K, 0.16), (0, SF + 0.6 * SNOUT_K + 0.1, 0.24), mat=M_CLOUD)
# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris bleu glacier lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.16), (sgn * 0.97, ey - 0.02, ez + 0.6), rot=(8, 0, 0), mat=M_CLOUD)
    else:
        # sourcils sévères blancs, inclinés vers le museau + un éclat de nuage gris dessus
        hbox(f"Brow_{sgn}", (0.2, 1.0, 0.26), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(16, 0, 0), mat=M_CLOUD, bevel=0.02)
        hbox(f"BrowCloud_{sgn}", (0.24, 0.6, 0.18), (sgn * 0.99, ey - 0.35, ez + 0.72), rot=(16, 0, 0), mat=M_CLOUD2)
    # Éclats de vent bleu glacier au coin de l'oeil (lueur)
    for k in range(WIND_EYE):
        hshard(f"EyeWind_{sgn}_{k}", 0.16, 0.06, 0.5 + 0.1 * k, (sgn * 0.95, ey + 0.55 + 0.28 * k, ez - 0.05 - 0.12 * k),
               (sgn * 0.5, 0.9, -0.15 * k), M_GLOW, up=(1, 0, 0))

# Crocs (bébé : aucun ; ado : 2 par côté ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_FANG, up=(1, 0, 0))

# Oreilles en éclat + joues de nuage
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.15 if not IS_BEBE else 0.8, (sgn * 0.85, 0.5, 0.2), (sgn * 1, 0.6, 0.3), M_BODY2)
    for k in range(CHEEK_N):
        hcloud(f"Cheek_{sgn}_{k}", (sgn * (0.95 + 0.05 * k), -0.05 + k * 0.4, -0.35 - k * 0.1), 0.42 - 0.04 * k, 2,
               [M_CLOUD, M_CLOUD2])

# Crinière de nuage : anneaux de blocs de nuage + éclats facettés, derrière le crâne et sur la nuque
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * (0.8 + 0.3 * ring_i), 0.65 + ring_i * 0.45, rad.z * (0.75 + 0.3 * ring_i))
        rr = (0.62 - 0.05 * ring_i) + random.random() * 0.12
        m = [M_CLOUD, M_CLOUD2, M_CLOUD3][(k + ring_i) % 3] if ring_i else pick([M_CLOUD, M_CLOUD, M_CLOUD2])
        hcloud(f"Mane_{ring_i}_{k}", loc, rr * 1.35, 2, [m, pick([M_CLOUD, M_CLOUD2])], 0.7)
        if k % 2:
            continue
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.2) + Vector((0, 1.0, 0)) + jit
        hshard(f"ManeShard_{ring_i}_{k}", 0.7 - ring_i * 0.05, 0.3, 1.1 + ring_i * 0.35 + random.random() * 0.3,
               (loc[0] * 1.1, loc[1] + 0.1, loc[2] * 1.1), direction, pick([M_CLOUD, M_CLOUD2], [3, 2]), up=tuple(rad))

# Cornes anthracite : bébé = 2 petits cônes, ado = recourbées + 1 pointe, adulte = longues, 2 pointes + corne basse
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.2), (sgn * 0.7, 0.9, 1.6)], 0.34, 0.13, M_HORN)
    elif IS_ADO:
        a0, a1 = Vector((sgn * 0.6, 0.25, 0.78)), Vector((sgn * 0.85, 0.5, 1.45))
        a2, a3 = Vector((sgn * 1.0, 1.1, 2.1)), Vector((sgn * 0.85, 1.85, 2.5))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.38, 0.14, M_HORN)
        hbar(f"HornTine_{sgn}", a1, (sgn * 1.4, 0.0, 2.15), 0.2, M_HORN)
    else:
        a0, a1 = Vector((sgn * 0.6, 0.3, 0.78)), Vector((sgn * 0.95, 0.6, 1.6))
        a2, a3 = Vector((sgn * 1.2, 1.4, 2.3)), Vector((sgn * 1.05, 2.4, 2.8))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.46, 0.15, M_HORN)
        hbar(f"HornTine1_{sgn}", a1, (sgn * 1.5, 0.25, 2.1), 0.22, M_HORN)
        hbar(f"HornTine2_{sgn}", a2, (sgn * 1.65, 1.0, 2.9), 0.2, M_HORN)
        hchain(f"HornLow_{sgn}", [(sgn * 0.85, 0.6, 0.35), (sgn * 1.35, 1.2, 0.6), (sgn * 1.6, 1.95, 0.75)], 0.3, 0.12, M_HORN)
    if GOLD:
        a0 = Vector((sgn * 0.6, 0.3, 0.78)) if not IS_ADO else Vector((sgn * 0.6, 0.25, 0.78))
        a1 = Vector((sgn * 0.95, 0.6, 1.6)) if IS_ADULTE else Vector((sgn * 0.85, 0.5, 1.45))
        hbox(f"HornRing_{sgn}", (0.62, 0.5, 0.2), a0.lerp(a1, 0.5), rot=(0, sgn * 10, 0), mat=M_GOLD)

# Crête du crâne : éclats de nuage en rangée centrale + blocs de nuage de chaque côté
for k in range(CROWN_N):
    hshard(f"Crown_{k}", 0.55, 0.3, 1.1 + 0.15 * CROWN_N * 0.4 - 0.12 * abs(k - CROWN_N / 2),
           (0, 0.55 + 0.38 * k, 0.8 + 0.02 * k), (0, 0.55, 1), pick([M_CLOUD, M_CLOUD2]), up=(1, 0, 0))
    if not IS_BEBE:
        for sgn in (-1, 1):
            hcloud(f"CrownCloud_{sgn}_{k}", (sgn * 0.42, 0.6 + 0.38 * k, 0.78), 0.36, 1, [pick(CLOUDS, CLOUDW)])

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs penchés, cou en plaques, ventre, flancs, nuages sur le dos, spirales de vent
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.1, TL * 0.46, BH * 1.06), CHEST - F * (0.02 * TL), RT, M_BODY, body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.44, BH * 0.96), C, RT, M_BODY, body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 1.0, TL * 0.46, BH * 1.0), PELVIS, RT, M_BODY, body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)
HALF_W = BW * 0.5

# Plastron clair + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), CHEST + F * (TL * 0.22) - UPT * (BH * 0.08),
    RT, M_CREAM, body_root, bevel=0.05 * SC)
if GOLD:
    # plastron doré : plaque en wedge + gemme bleu glacier lumineuse au centre
    wedge("Body_GoldPlate", (BW * 0.5, 0.18 * SC, BH * 0.34), CHEST + F * (TL * 0.235) + UPT * (BH * 0.0), RT, M_GOLD, body_root,
          top_x=0.7, top_y=1.0, bevel=0.03 * SC)
    crystal("Body_ChestGem", 0.13 * SC, 0.26 * SC, 0.16 * SC, CHEST + F * (TL * 0.245) + UPT * (BH * 0.0), F, M_IRIS, body_root, up=tuple(UPT), sides=4)
for i in range(BELLY_N):
    s = -0.4 + 0.8 * (i + 0.5) / BELLY_N
    pl = (TL * 0.8) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), tpos(s, -BH / 2 + 0.03), RT, M_CREAM, body_root)
    for sgn in (-1, 1):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), tpos(s, -BH * 0.3, sgn * (HALF_W - 0.01)),
          RT, M_CREAM, body_root)

# Écailles en quinconce sur les flancs (pointe vers l'arrière), grises et bleutées
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            s = -0.36 + 0.74 * (c + 0.5 * (r % 2)) / FLANK_COLS
            up = BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, tpos(s, up, sgn * (HALF_W - 0.03 * SC)),
                  -F + SIDEV * sgn * 0.3 - UPT * 0.1, pick([M_BODY2, M_BODY2, M_CLOUD3]), body_root, up=(sgn, 0, 0))

# Spirales de vent claires sur les flancs (signe distinctif, lueur)
for sgn in (-1, 1):
    for j in range(SWIRL_FLANK):
        s0 = -0.2 + 0.42 * j
        swirl(f"Body_Swirl_{sgn}_{j}", tpos(s0, BH * 0.08, sgn * (HALF_W + 0.05)), F, UPT, BH * 0.3, 1.25, 0.1 * SC, body_root,
              SIDEV * sgn, n=SWIRL_N)

# Cou : courbe lissée du torse vers la tête, un segment gris + une plaque claire par maillon
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
    # nuque : bloc de nuage + éclat blanc
    cloud(f"Body_NeckCloud_{i}", mid + dz * r * 0.9, 0.55 * SC, body_root, 1, mats=[pick(CLOUDS, CLOUDW)])
    shard(f"Body_NeckShard_{i}", 0.6 * SC, 0.3 * SC, (1.0 - 0.3 * s) * SC * 1.2, mid + dz * r * 0.95,
          dz + (p2 - p1).normalized() * (-0.5), M_CLOUD, body_root, up=tuple(sd))
    if NECK_PUFFS:
        for sgn in (-1, 1):
            cloud(f"Body_NeckSide_{i}_{sgn}", mid + dz * r * 0.6 + sd * sgn * r * 0.95, 0.4 * SC, body_root, 1, mats=[M_CLOUD2])

# Dos : rangée de nuages blancs et d'éclats, comme une crête d'orage
for k in range(CREST_N):
    s = -0.38 + 0.78 * k / max(1, CREST_N - 1)
    cloud(f"Body_CrestCloud_{k}", tpos(s, BH / 2 - 0.02), (0.6 - 0.04 * abs(k - CREST_N / 2)) * SC, body_root, 2, 0.5, [M_CLOUD, M_CLOUD2])
    shard(f"Body_Crest_{k}", 0.8 * SC, 0.3 * SC, (1.2 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          tpos(s, BH / 2 + 0.1), -F * 0.45 + UPT, pick([M_CLOUD, M_CLOUD2], [3, 2]), body_root, up=(1, 0, 0))
    if CREST_SIDE:
        for sgn in (-1, 1):
            shard(f"Body_CrestSide_{k}_{sgn}", 0.5 * SC, 0.12 * SC, 0.7 * SC, tpos(s + 0.03, BH * 0.4, sgn * BW * 0.28),
                  -F * 0.5 + UPT * 0.8 + SIDEV * sgn * 0.5, M_CLOUD2, body_root, up=(1, 0, 0))

# Épaules : touffe de nuage sur chaque épaule + plaque d'épaule sombre
for sgn in (-1, 1):
    sh = CHEST + SIDEV * sgn * BW * 0.5 + UPT * BH * 0.42 - F * 0.05 * TL
    wedge(f"Body_ShoulderPad_{sgn}", (BW * 0.5, TL * 0.3, 0.3 * SC + 0.2), sh, RT @ Euler((0, math.radians(sgn * 22), 0)).to_matrix(),
          M_BODY2, body_root, top_x=0.85, top_y=0.85, bevel=0.05 * SC)
    for k in range(SHOULDER_PUFFS):
        cloud(f"Body_ShoulderCloud_{sgn}_{k}", sh + SIDEV * sgn * (0.1 * BW + 0.2 * k * SC) + UPT * (0.2 + 0.15 * k * SC) + F * (-0.3 + 0.3 * k) * SC,
              (0.75 - 0.08 * k) * SC, body_root, 2, 0.5, [M_CLOUD, M_CLOUD2])

# ----------------------------------------------------------
# 11. PATTES ARRIÈRE (wyvern : 2 pattes) : hanche, cuisse, tibia, genouillère, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.16)
LEG_TH = BW * LEG_TH_K
HIP_Y = PELVIS.y - 0.05 * TL
for sgn in (-1, 1):
    x = sgn * (BW * 0.5 - LEG_TH * 0.2)
    hip = Vector((x, HIP_Y, HIP_Z + BH * 0.05))
    knee = Vector((x + sgn * 0.04 * LEG_TH, HIP_Y - LEG_H * 0.28, LEG_H * 0.5))
    ank = Vector((x, HIP_Y + LEG_H * 0.16, FOOT_H + LEG_H * 0.12))
    wedge(f"Legs_Haunch_{sgn}", (LEG_TH * 1.35, LEG_TH * 1.9, LEG_H * 0.46 + BH * 0.3), hip - Vector((0, -0.05, LEG_H * 0.12)),
          None, M_BODY, legs_root, top_x=0.8, top_y=0.85, shift_y=LEG_TH * 0.1, bevel=0.1 * SC)
    link(f"Legs_Thigh_{sgn}", hip - Vector((0, 0, LEG_H * 0.1)), knee, LEG_TH * 1.2, M_BODY, legs_root, extra=0.2,
         bevel=0.08 * SC, depth=LEG_TH * 1.45)
    link(f"Legs_Shin_{sgn}", knee, ank, LEG_TH * 0.95, M_BODY2, legs_root, extra=0.15, bevel=0.05 * SC, depth=LEG_TH * 1.0)
    B(f"Legs_Knee_{sgn}", (LEG_TH * 1.15, LEG_TH * 0.7, LEG_TH * 0.9), knee + Vector((0, -LEG_TH * 0.15, 0)), None, M_DARK, legs_root)
    # genouillère : nuage gris clair sur le genou
    cloud(f"Legs_KneeCloud_{sgn}", knee + Vector((sgn * LEG_TH * 0.55, -LEG_TH * 0.2, 0.1)), LEG_TH * 0.55, legs_root, 2, 0.5, [M_CLOUD2, M_CLOUD])
    # bande claire sur le tibia (+ anneau doré si Épique en place)
    g0, g1 = knee.lerp(ank, 0.3), knee.lerp(ank, 0.8)
    link(f"Legs_Greave_{sgn}", g0, g1, LEG_TH * 1.1, M_CREAM, legs_root, extra=0.05, bevel=0.03 * SC, depth=LEG_TH * 1.12)
    if GOLD:
        ring(f"Legs_Anklet_{sgn}", LEG_TH * 0.62, LEG_TH * 0.28, LEG_TH * 0.24, knee.lerp(ank, 0.9), direction=(ank - knee), mat=M_GOLD,
             parent=legs_root, sides=6)
    B(f"Legs_Heel_{sgn}", (LEG_TH * 0.9, LEG_TH * 0.9, FOOT_H * 1.4), Vector((x, ank.y + LEG_TH * 0.1, FOOT_H * 0.9)), None, M_BODY2, legs_root)
    fy = ank.y - LEG_TH * 0.75
    box(f"Legs_Foot_{sgn}", (LEG_TH * 1.2, LEG_TH * 2.1, FOOT_H), (x, fy, FOOT_H / 2), None, M_BODY, legs_root, bevel=0.06 * SC)
    toe_y = fy - LEG_TH * 1.05 - LEG_TH * 0.1
    for k in (-1, 0, 1):
        B(f"Legs_Toe_{sgn}_{k}", (LEG_TH * 0.3, LEG_TH * 0.5, FOOT_H * 0.72), (x + k * LEG_TH * 0.36, toe_y, FOOT_H * 0.36), None, M_BODY2, legs_root)
        shard(f"Legs_Claw_{sgn}_{k}", LEG_TH * 0.22, LEG_TH * 0.18, LEG_TH * 0.62, (x + k * LEG_TH * 0.36, toe_y - LEG_TH * 0.18, FOOT_H * 0.34),
              (k * 0.12, -1, -0.05), M_CLAW, legs_root)
    # nuages et spirale de vent sur la cuisse
    for k in range(THIGH_PUFFS):
        cloud(f"Legs_ThighCloud_{sgn}_{k}", hip.lerp(knee, 0.2 + 0.32 * k) + Vector((sgn * LEG_TH * 0.75, 0.1, 0.0)), 0.5 * SC, legs_root, 2, 0.5, [M_CLOUD2, M_CLOUD])
    if SWIRL_LEG:
        swirl(f"Legs_Swirl_{sgn}", hip.lerp(knee, 0.45) + Vector((sgn * (LEG_TH * 0.7 + 0.03), 0.05, 0)), (0, 1, 0), (0, 0, 1),
              LEG_TH * 0.7, 1.25, 0.09 * SC, legs_root, (sgn, 0, 0), n=SWIRL_N)

# ----------------------------------------------------------
# 12. AILES-BRAS (wyvern) : épaule, coude vers l'arrière, poignet posé devant, griffe + bracelet,
#     3 doigts qui montent vers l'arrière, membrane d'orage dont le bord s'effiloche en nuages
# ----------------------------------------------------------
SP = WING_SPAN
CLAW_L = 0.18 * SP
WRIST_Z = LEG_H * WING_WRIST[2] + CLAW_L * 0.2
for sgn in (-1, 1):
    S = CHEST + SIDEV * sgn * BW * 0.48 + UPT * BH * 0.36 - F * 0.02 * TL
    E = S + Vector((sgn * WING_ELBOW[0] * SP, WING_ELBOW[1] * SP, WING_ELBOW[2] * SP))
    W = Vector((sgn * (BW * 0.5 + WING_WRIST[0] * SP), CHEST.y + WING_WRIST[1] * SP, WRIST_Z))
    tips = [W + Vector((sgn * a * SP, b * SP, c * SP)) for (a, b, c) in WING_TIPS]
    Hpt = Vector((sgn * BW * 0.45, PELVIS.y + 0.12 * TL, PELVIS.z + 0.15 * BH))   # bord de fuite accroché au haut de la hanche
    bn = WING_BONE
    link(f"Wings_{sgn}_Arm", S, E, bn * 1.3, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.3)
    link(f"Wings_{sgn}_Fore", E, W, bn * 1.1, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.1)
    wedge(f"Wings_{sgn}_Shoulder", (bn * 2.2, bn * 2.2, bn * 2.2), S, None, M_BODY2, wings_root, bevel=0.06 * SC)
    for k, tp in enumerate(tips):
        link(f"Wings_{sgn}_Finger_{k}", W, tp, bn * (0.85 - 0.12 * k), M_BONE, wings_root, up=(0, 1, 0), extra=0.1, bevel=0, depth=bn * 0.85)
        shard(f"Wings_{sgn}_Spike_{k}", bn * 1.7, bn * 1.2, SP * 0.12, tp, tp - W, M_CLAW, wings_root)
    # membrane : triangles en éventail autour du poignet + bandes claires dessus
    edge = tips + [Hpt]
    for k in range(len(edge) - 1):
        plate(f"Wings_{sgn}_Memb_{k}", [W, edge[k], edge[k + 1]], WING_MEMB_T, M_WING, wings_root)
        a, b = edge[k], edge[k + 1]
        plate(f"Wings_{sgn}_Band_{k}", [W + (a - W) * 0.5, W + (a - W) * 0.92, W + (b - W) * 0.92, W + (b - W) * 0.5],
              WING_MEMB_T * 1.5, M_WING2, wings_root)
    plate(f"Wings_{sgn}_Memb_A", [W, Hpt, S], WING_MEMB_T, M_WING, wings_root)
    plate(f"Wings_{sgn}_Memb_B", [W, S, E], WING_MEMB_T, M_WING, wings_root)
    # bord effiloché en nuage : blocs de nuage + lambeaux qui pendent le long du bord de fuite
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        for j in range(FRAY_N):
            t = (j + 0.5) / FRAY_N
            p = a.lerp(b, t)
            out = (p - W).normalized()
            puff(f"Wings_{sgn}_Fray_{k}_{j}", p + out * SP * 0.015, SP * random.uniform(0.06, 0.1),
                 pick([M_CLOUD, M_CLOUD2, M_CLOUD3], [4, 3, 2]), wings_root)
            if j % 2 == 0:
                shard(f"Wings_{sgn}_Tatter_{k}_{j}", SP * 0.07, SP * 0.04, SP * random.uniform(0.1, 0.17), p + out * SP * 0.03,
                      out * 0.9 + Vector((0, 0.2, -0.5)), pick([M_CLOUD, M_CLOUD2]), wings_root)
    # spirales de vent sur la membrane
    for j in range(SWIRL_WING):
        a, b = edge[j % (len(edge) - 1)], edge[(j + 1) % (len(edge) - 1)]
        cen = (W + a + b) / 3 + (W - a) * 0.0
        nrm = (a - W).cross(b - W).normalized()
        if nrm.x * sgn < 0:
            nrm = -nrm
        swirl(f"Wings_{sgn}_Swirl_{j}", cen + nrm * (WING_MEMB_T * 0.9), (a - W), (b - W), SP * 0.11, 1.25, 0.06 * SP * 0.5, wings_root, nrm, n=SWIRL_N)
    # poignet : bloc, bracelet doré (Épique), grande griffe + 2 petites griffes anthracite
    wedge(f"Wings_{sgn}_WristBlock", (bn * 2.2, bn * 2.4, bn * 2.0), W, None, M_BODY2, wings_root, bevel=0.0)
    cloud(f"Wings_{sgn}_WristCloud", W + Vector((sgn * bn * 0.6, 0.0, bn * 0.9)), bn * 1.3, wings_root, 2, 0.6, [M_CLOUD, M_CLOUD2])
    if GOLD:
        ring(f"Wings_{sgn}_Bracelet", bn * 1.45, bn * 0.7, bn * 0.55, E.lerp(W, 0.85), direction=(W - E), mat=M_GOLD, parent=wings_root, sides=6)
    fd = Vector((sgn * 0.12, -1, -0.75))
    shard(f"Wings_{sgn}_ThumbClaw", bn * 1.2, bn * 1.0, CLAW_L, W + Vector((0, -0.1, -0.05)), fd, M_CLAW, wings_root)
    for k in (-1, 1):
        shard(f"Wings_{sgn}_Claw_{k}", bn * 0.8, bn * 0.7, CLAW_L * 0.7, W + Vector((k * bn * 0.9, -0.1, -0.02)), (k * 0.25, -1, -0.75), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, nuages sur le dos, spirales de vent, touffe de nuage au bout
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
    if i % 2 == 0 and s < 0.9:
        cloud(f"Tail_Cloud_{i}", mid + dz * (r * 0.9), 0.5 * SC + r * 0.35, tail_root, 2, 0.5, [pick([M_CLOUD, M_CLOUD2]), M_CLOUD2])
    else:
        shard(f"Tail_Crest_{i}", 0.8 * r + 0.2, 0.25 * SC, 0.6 * SC + r * 0.8, mid + dz * r * 0.85, dz + t_ * 0.7, M_CLOUD, tail_root, up=tuple(sd))
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + sd * sgn * (r - 0.03), sd * sgn * 0.3 + t_,
                  pick([M_BODY2, M_CLOUD3]), tail_root, up=(sgn, 0, 0))
for j in SWIRL_TAIL_AT:
    if j < TN - 1:
        a, b = TAIL_SPINE[j], TAIL_SPINE[j + 1]
        R = basis(b - a); dz = R.col[2]; sd = R.col[0]
        r = keyed(TAIL_R, j / TN)
        for sgn in (-1, 1):
            swirl(f"Tail_Swirl_{j}_{sgn}", (a + b) / 2 + sd * sgn * (r + 0.03), (b - a), dz, r * 0.95, 1.25, 0.08 * SC, tail_root, sd * sgn, n=SWIRL_N)
tip = TAIL_SPINE[-1]
tt_ = (TAIL_SPINE[-1] - TAIL_SPINE[-2]).normalized()
RT_TIP = basis(tt_)
tdz, tsd = RT_TIP.col[2], RT_TIP.col[0]
B("Tail_TipBlock", (BW * 0.3, 0.6 * SC, BW * 0.3), tip, RT_TIP, M_BODY2, tail_root)
if GOLD:
    ring("Tail_TipRing", BW * 0.2, BW * 0.12, 0.3 * SC, tip - tt_ * 0.3 * SC, direction=tt_, mat=M_GOLD, parent=tail_root, sides=6)
# touffe de nuage au bout de la queue : gros nuage + éclats qui s'échappent en arrière
TUFT = TAIL_TUFT
cloud("Tail_Tuft", tip + tt_ * TUFT * 0.5, TUFT * 0.8, tail_root, 4 + (1 if not IS_BEBE else 0), 0.55, [M_CLOUD, M_CLOUD2, M_CLOUD, M_CLOUD3])
for k in range(5 if IS_ADULTE else 4):
    ang = k / 5 * 2 * math.pi
    d = tt_ + tsd * math.cos(ang) * 0.8 + tdz * math.sin(ang) * 0.8
    shard(f"Tail_TuftShard_{k}", TUFT * 0.5, TUFT * 0.3, TUFT * (1.0 + 0.2 * (k % 2)), tip + tt_ * TUFT * 0.5, d, pick([M_CLOUD, M_CLOUD2]), tail_root, up=tuple(tdz))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Épique : crinière de nuage, ailes aux bords effilochés, iris et spirales de vent lumineux (2,2 à 2,4),
#     ornements dorés (cornes, bracelets, chevilles, plastron, queue), éclats et nuages flottants.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (SP * 0.6 + BW), random.uniform(-TL * 0.9 - NECK_FWD, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.8, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 3 == 2:
            crystal(f"FX_Wind_{k}", FX_SIZE * 0.12, FX_SIZE * 0.22, FX_SIZE * 0.16, p, dirv, M_GLOW, master, sides=4)
        else:
            puff(f"FX_Cloud_{k}", p, FX_SIZE * random.uniform(0.3, 0.5), pick([M_CLOUD, M_CLOUD2]), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
