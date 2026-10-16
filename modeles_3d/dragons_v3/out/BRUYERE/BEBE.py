import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Bruyère · Bébé
#  Rare · Terre · Drake · monde 1
#  - Bébé trapu et mignon : très grosse tête carrée, museau court, très grands yeux ambre brillants, pattes courtes et épaisses
#  - Signes distinctifs : plaques de roche or-ocre sur le dos, touffes de bruyère violet-rose entre les plaques, ventre crème
#  - Rare : bandes de roche sur les flancs, petites cornes brunes, cristaux ambre et lianes dorées lumineuses (discrets)
#  - Pas de crocs, petites épines ; mêmes couleurs que l'adulte
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1106)            # même dragon à chaque exécution
TAG = "BRUYERE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
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
#    Brun ocre (corps), or-ocre (plaques de roche), crème (ventre), violet-rose (bruyère).
#    Rare : accent lumineux discret (yeux, cristaux ambre, lianes dorées), strength <= 1.5.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#A96D34", 0.55)   # corps principal brun ocre
M_BODY2 = get_mat("BodyScale", "#8C5628", 0.58)   # dessus des pattes, mâchoire, écailles
M_DARK  = get_mat("BodyDark",  "#4E301A", 0.65)   # sourcils, bouche, taches, ombres
M_ROCK1 = get_mat("Rock1",     "#D9993A", 0.50)   # plaques de roche or-ocre
M_ROCK2 = get_mat("Rock2",     "#BF7E2C", 0.55)   # plaques de roche plus foncées
M_GOLD  = get_mat("RockGold",  "#F2BE4A", 0.38)   # grands éclats de roche dorée
M_CREAM = get_mat("Belly",     "#F2D8A0", 0.55)   # ventre en plaques, plastron, menton
M_HORN  = get_mat("Horn",      "#5E3F24", 0.55)   # cornes / bois brun foncé
M_HORN2 = get_mat("HornTip",   "#A57B46", 0.50)   # pointes des cornes, branches claires
M_CLAW  = get_mat("Claw",      "#F4E6C4", 0.35)   # griffes, crocs
M_PUR1  = get_mat("HeatherA",  "#B042A6", 0.50)   # bruyère violet-rose
M_PUR2  = get_mat("HeatherB",  "#DD77CF", 0.50)   # bruyère rose clair
M_PUR3  = get_mat("HeatherC",  "#7C2C86", 0.55)   # bruyère violet foncé
M_STEM  = get_mat("Stem",      "#4F8E32", 0.55)   # tiges et petites feuilles vertes
M_WHITE = get_mat("EyeWhite",  "#F6F0DC", 0.30)
M_IRIS  = get_mat("Iris",      "#FFAE1F", 0.25, emission="#FFA811", strength=1.3)  # yeux ambre (accent Rare)
M_BLACK = get_mat("Black",     "#120B06", 0.30)
M_GLOW  = get_mat("AmberCrystal", "#FFC247", 0.15, emission="#FFB01F", strength=1.5)  # cristaux ambre
M_VINE  = get_mat("GoldVine",  "#F7C040", 0.30, emission="#FFAA1A", strength=1.1)    # lianes dorées lumineuses
M_PINK  = get_mat("PinkGlow",  "#F06BD8", 0.20, emission="#E04CC8", strength=1.2)    # petit cristal rose
PURPS = [M_PUR1, M_PUR2, M_PUR3]
ROCKS = [M_ROCK1, M_ROCK2, M_GOLD]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
BW = 2.7
BH = 2.2
LEG_H = 1.5
TORSO_L = 3.3
NECK_L = 1.0
NECK_LEAN = 0.3
NECK_N = 2
NECK_R = (1.05, 1.15)
HEAD_SCALE = 1.8
SNOUT_K = 0.62
FANGS = 0
CHEEK_N = 2
HEAD_STRATA = 2
HEAD_SHARDS = 3
HEAD_TUFTS = 1
HEATHER_HEAD = 0.9
BELLY_N = 4
BELLY_SIDES = False
FLANK_ROWS = 2
FLANK_COLS = 4
FLANK_BANDS = 2
SPOTS = 3
CREST_N = 4
STRATA_N = 2
SPINE_DOUBLE = False
SHOULDER_N = 2
SHOULDER_SPIKES = 1
GLOW_SPOTS = [(0.1, 0.0)]
PINK_GLOW = False
TUFTS = 3
BRACER_K = 0.5
LEG_GLOW = False
LEG_HEATHER = False
TAIL_L = 3.0
TAIL_STEP = 0.75
TAIL_BEV_N = 2
TAIL_SCALES = False
TAIL_TUFT_AT = [1]
TAIL_TIP_N = 2
FX_N = 3
FX_SIZE = 0.6

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.2                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_BASE = Vector((0, -TL * 0.38, ZC + BH * 0.15))
NECK_TOP = NECK_BASE + Vector((0, -NECK_LEAN, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.2 * HEAD_SCALE, 0.35 * HEAD_SCALE))
HEAD_PITCH = 8                                   # degrés : la tête regarde un peu vers le bas
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
    """Suite de barres qui s'affinent (cornes, bois, branches)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def bud_mesh(r, L):
    """Bouton de fleur : double pyramide à 4 côtés (8 triangles), axe +Y."""
    e = [(r, L * 0.4, 0), (0, L * 0.4, r), (-r, L * 0.4, 0), (0, L * 0.4, -r)]
    v = [(0, 0, 0)] + e + [(0, L, 0)]
    f = [(0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4), (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)]
    return mesh_from("bud", v, f)

def heather(name, base, direction, size, parent, up=(0, 0, 1), n=5, leaves=True):
    """Touffe de bruyère : tige fine + n boutons violet-rose en épi + une petite feuille verte."""
    base = Vector(base)
    d = Vector(direction).normalized()
    m = basis(d, up)
    fx = m.col[0]
    bar(f"{name}_Stem", base - d * size * 0.1, base + d * size * 0.95, size * 0.1, M_STEM, parent, up)
    for j in range(n):
        t = 0.38 + 0.62 * j / max(1, n - 1)
        off = fx * (0.1 * size * (1 if j % 2 == 0 else -1)) * (1.1 - 0.5 * t)
        pos = base + d * size * t + off
        r = size * (0.17 - 0.06 * j / max(1, n - 1))
        place(f"{name}_Bud_{j}", bud_mesh(r, r * 2.8), PURPS[(j + 1) % 3] if j < n - 1 else M_PUR2, pos,
              basis(d + off * 3, up), parent)
    if leaves:
        shard(f"{name}_Leaf", size * 0.16, size * 0.05, size * 0.5, base + d * size * 0.2, d + fx * 1.2, M_STEM, parent, up)

def glow_cluster(name, base, direction, k, parent, n=3, up=(0, 0, 1)):
    """Grappe de cristaux ambre émissifs (accent lumineux Rare)."""
    d = Vector(direction).normalized()
    m = basis(d, up)
    for i in range(n):
        a = i * 2.4
        sp = (m.col[0] * math.cos(a) + m.col[2] * math.sin(a)) * (0.55 if i else 0.0)
        crystal(f"{name}_{i}", 0.2 * k * (1 - 0.18 * i), 0.55 * k * (1 - 0.25 * i), 0.3 * k * (1 - 0.2 * i),
                Vector(base) + sp * 0.2 * k, d + sp, M_GLOW, parent, up, sides=5)

def strata(name, center, w, l, t, n, parent, rot=(0, 0, 0), top=0.86, taper=0.16, mats=None):
    """Pile de dalles de roche feuilletées, de plus en plus petites vers le haut."""
    mats = mats or [M_ROCK2, M_ROCK1, M_GOLD]
    for i in range(n):
        s = 1 - taper * i
        wedge(f"{name}_{i}", (w * s, l * (1 - 0.1 * i), t), (center[0] + 0.03 * i * w, center[1], center[2] + i * t * 0.78),
              (rot[0], rot[1], rot[2] + 9 * i * (1 if i % 2 else -1)), mats[i % len(mats)], parent,
              top_x=top, top_y=top, bevel=0)

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

def hcrystal(name, r, h, tip, loc, direction, mat, up=(0, 0, 1), sides=5):
    return crystal("Head_" + name, r * HS, h * HS, tip * HS, hv(loc), direction, mat, H, up, sides)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

def hheather(name, base, direction, size, n=5, up=(0, 0, 1)):
    heather("Head_" + name, hv(base), direction, size * HS, H, up, n)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (2.0, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.65, 2.1 * SNOUT_K, 1.0), (0, -0.6 - 1.05 * SNOUT_K, -0.26), mat=M_BODY, top_x=0.94, top_y=0.96,
       shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.1, 1.7 * SNOUT_K, 0.14), (0, -0.6 - 0.95 * SNOUT_K, 0.26), mat=M_ROCK1)
hbox("Jaw", (1.45, 1.95 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BODY2, bevel=0.03)
hbox("Chin", (0.9, 1.2 * SNOUT_K, 0.12), (0, -0.7 - 1.0 * SNOUT_K, -0.97), mat=M_CREAM)
hbox("MouthLine", (1.68, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.7), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines et bout du museau
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.24, 0.07), (sgn * 0.42, SNOUT_FRONT + 0.25, 0.28), mat=M_BLACK)
    hbox(f"SnoutSide_{sgn}", (0.1, 1.0 * SNOUT_K, 0.35), (sgn * 0.85, SNOUT_FRONT + 0.7, -0.15), mat=M_BODY2)

# Yeux : blanc, iris ambre lumineux, pupille (ronde + reflets bébé, fendue ado / adulte), sourcils
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.9, 0.98, 0.72, 0.84, 0.42, 0.6
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.64, 0.42, 0.54, 0.1, 0.5
for sgn in (-1, 1):
    ey, ez = -0.32, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 1.0, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.04, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.08, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.11, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.11, ey + 0.12, ez - 0.22), mat=M_WHITE)
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.14), (sgn * 1.0, ey - 0.02, ez + 0.62), mat=M_ROCK2)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.24), (sgn * 1.01, ey - 0.05, ez + 0.54), rot=(14, 0, 0), mat=M_DARK, bevel=0.02)
        hbox(f"BrowRock_{sgn}", (0.2, 0.8, 0.14), (sgn * 1.02, ey - 0.02, ez + 0.74), rot=(14, 0, 0), mat=M_ROCK2)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.74, fy, -0.74), (0, 0.05, -1), M_CLAW,
                   up=(1, 0, 0))

# Plaques de roche sur le crâne : dalles feuilletées + grands éclats dorés + éclats de joue
strata("Head_SkullRock", hv((0, 0.15, 0.82)), 1.5 * HS, 1.4 * HS, 0.2 * HS, HEAD_STRATA, H)
strata("Head_SnoutRock", hv((0, -1.35 * SNOUT_K - 0.2, 0.36)), 0.95 * HS, 1.1 * SNOUT_K * HS, 0.12 * HS, 2, H,
       mats=[M_ROCK2, M_ROCK1])
for k in range(HEAD_SHARDS):
    f = (k + 0.5) / HEAD_SHARDS - 0.5
    hcrystal(f"CrownGold_{k}", 0.26 - 0.06 * abs(f), 0.5 - 0.1 * abs(f), 0.5 - 0.1 * abs(f),
             (f * 1.5, 0.45 - 0.2 * abs(f), 0.95 + 0.08 * HEAD_STRATA), (f * 0.8, 0.5, 1), M_GOLD, up=(1, 0, 0))
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.5, 0.12, 0.95 - 0.12 * k, (sgn * 0.92, -0.2 + k * 0.32, -0.38 - k * 0.14),
               (sgn * 0.8, 0.9, -0.5), pick(ROCKS, [3, 2, 3]))
    hshard(f"Ear_{sgn}", 0.4, 0.14, 0.9, (sgn * 0.86, 0.6, 0.3), (sgn * 1, 0.7, 0.5), M_BODY2)

# Cornes brunes : bébé = petites cornes recourbées ; ado = cornes + 1 branche ; adulte = bois ramifiés (3 branches)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.6, 0.2, 0.75), (sgn * 0.85, 0.35, 1.2), (sgn * 0.85, 0.8, 1.55)], 0.36, 0.15, M_HORN)
    elif IS_ADO:
        a0, a1, a2 = Vector((sgn * 0.62, 0.25, 0.78)), Vector((sgn * 0.95, 0.5, 1.5)), Vector((sgn * 1.15, 1.05, 2.1))
        hchain(f"Horn_{sgn}", [a0, a1, a2, (sgn * 1.0, 1.7, 2.35)], 0.38, 0.15, M_HORN)
        bar(f"Head_HornTine_{sgn}", hv(a1), hv((sgn * 1.45, 0.3, 2.2)), 0.2 * HS, M_HORN2, H)
    else:
        a0, a1 = Vector((sgn * 0.62, 0.3, 0.8)), Vector((sgn * 1.0, 0.6, 1.7))
        a2, a3 = Vector((sgn * 1.3, 1.25, 2.5)), Vector((sgn * 1.2, 2.0, 3.0))
        hchain(f"Antler_{sgn}", [a0, a1, a2, a3], 0.44, 0.16, M_HORN)
        bar(f"Head_AntlerTine1_{sgn}", hv(a1), hv((sgn * 1.7, 0.3, 2.4)), 0.22 * HS, M_HORN2, H)
        bar(f"Head_AntlerTine2_{sgn}", hv(a2), hv((sgn * 2.0, 1.0, 3.2)), 0.2 * HS, M_HORN2, H)
        bar(f"Head_AntlerTine3_{sgn}", hv(a1.lerp(a2, 0.5)), hv((sgn * 0.85, 0.1, 2.9)), 0.17 * HS, M_HORN2, H)
        bar(f"Head_AntlerTine4_{sgn}", hv(a3), hv((sgn * 1.7, 2.7, 3.5)), 0.14 * HS, M_HORN2, H)
        hheather(f"HeatherTine_{sgn}", (sgn * 2.0, 1.0, 3.2), (sgn * 0.5, 0.2, 1), 0.85, 4)

# Bruyère sur le crâne (signe distinctif) : entre les cornes
hheather("HeatherTop", (0, 0.3, 1.05 + 0.08 * HEAD_STRATA), (0, 0.15, 1), HEATHER_HEAD, 6)
if HEAD_TUFTS > 1:
    hheather("HeatherL", (-0.5, 0.6, 1.0 + 0.08 * HEAD_STRATA), (-0.5, 0.3, 1), HEATHER_HEAD * 0.75, 5)
    hheather("HeatherR", (0.5, 0.45, 1.0 + 0.08 * HEAD_STRATA), (0.5, 0.2, 1), HEATHER_HEAD * 0.7, 5)
if HEAD_TUFTS > 3:
    hheather("HeatherC1", (-0.25, -0.2, 1.0 + 0.08 * HEAD_STRATA), (-0.2, -0.3, 1), HEATHER_HEAD * 0.55, 4)
    hheather("HeatherC2", (0.3, -0.25, 1.0 + 0.08 * HEAD_STRATA), (0.25, -0.3, 1), HEATHER_HEAD * 0.5, 4)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou, ventre en plaques, flancs, armure de roche, bruyère
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

# Plastron crème + plaques de ventre séparées + bandes crème sur le bas des flancs
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
              mat=M_CREAM, parent=body_root)

# Motif secondaire (Rare) : bandes de roche feuilletée sur les flancs + taches brunes
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.34 + (TL * 0.74) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.22 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.1 * SC, BH * 0.32, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_ROCK2, M_BODY2]), body_root, up=(sgn, 0, 0))
    for b in range(FLANK_BANDS):
        y = -TL * 0.3 + b * (TL * 0.6) / max(1, FLANK_BANDS - 1)
        B(f"Body_FlankBand_{sgn}_{b}", (0.08 * SC, TL * 0.17, BH * 0.1), (sgn * (half_w(y) + 0.01), y, ZC - BH * 0.02),
          mat=M_ROCK1, parent=body_root)
for k in range(SPOTS):
    y = random.uniform(-TL * 0.4, TL * 0.45)
    sgn = random.choice((-1, 1))
    B(f"Body_Spot_{k}", (0.06, random.uniform(0.35, 0.55) * SC, random.uniform(0.3, 0.45) * SC),
      (sgn * (half_w(y) + 0.0), y, ZC + BH * random.uniform(-0.2, 0.28)), mat=M_DARK, parent=body_root)

# Cou court et épais : courbe lissée, un segment brun + une plaque crème + des dalles de roche par maillon
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):
    p = NECK_BASE.lerp(NECK_TOP, tt)
    p.y -= 0.25 * NECK_LEAN * math.sin(math.pi * tt)
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
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.25, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_CREAM, body_root)
    wedge(f"Body_NeckRock_{i}", (2 * r * 0.85, Ln * 1.0, 0.24 * SC), mid + d * (r * 0.97), R, pick([M_ROCK1, M_ROCK2]), body_root,
          top_x=0.85, top_y=0.9, bevel=0)
    crystal(f"Body_NeckGold_{i}", 0.24 * SC * (1.1 - 0.3 * s), 0.45 * SC, 0.5 * SC, mid + d * (r * 1.0),
            d + t * 0.8, M_GOLD, body_root, up=side)
    if IS_ADULTE and i % 2 == 0:
        for sgn in (-1, 1):
            shard(f"Body_NeckSide_{i}_{sgn}", 0.6 * SC, 0.12 * SC, 0.7 * SC, mid + side * sgn * r * 0.9,
                  side * sgn + t * 0.8 + d * 0.3, pick(ROCKS), body_root)

# Armure de roche dorsale : dalles feuilletées + éclats dorés sur la ligne du dos (double rangée)
TOPZ = ZC + BH / 2
for k in range(CREST_N):
    f = k / max(1, CREST_N - 1)
    y = -TL * 0.36 + (TL * 0.78) * f
    w = BW * (0.78 - 0.12 * f)
    strata(f"Body_Strata_{k}", (0, y, TOPZ - 0.02), w, TL * 0.74 / CREST_N, 0.2 * SC, STRATA_N, body_root, rot=(0, 0, 0))
    crystal(f"Body_Spine_{k}", 0.3 * SC * (1.15 - 0.4 * abs(f - 0.35)), 0.5 * SC, (0.75 - 0.25 * abs(f - 0.35)) * SC,
            (0, y, TOPZ + 0.2 * SC * STRATA_N * 0.6), (0, 0.4, 1), M_GOLD if k % 2 == 0 else M_ROCK1, body_root, up=(1, 0, 0))
    for sgn in (-1, 1):
        if k % 2 == (0 if sgn == -1 else 1) or SPINE_DOUBLE:
            crystal(f"Body_SpineSide_{k}_{sgn}", 0.2 * SC, 0.4 * SC, 0.5 * SC, (sgn * w * 0.33, y + 0.2, TOPZ + 0.12 * SC),
                    (sgn * 0.5, 0.5, 1), pick(ROCKS), body_root, up=(1, 0, 0))

# Cape de roche sur les épaules (dalles qui retombent sur les flancs) + éclats dorés
for sgn in (-1, 1):
    for k in range(SHOULDER_N):
        wedge(f"Body_Cape_{sgn}_{k}", (BW * 0.5 * (1 - 0.08 * k), TL * 0.2 * (1 + 0.05 * k), 0.24 * SC),
              (sgn * BW * (0.34 + 0.05 * k), -TL * 0.22 + 0.12 * k * SC * 2, TOPZ - BH * 0.1 * k),
              (0, sgn * (16 + 12 * k), 0), ROCKS[k % 3], body_root, top_x=0.85, top_y=0.85, bevel=0)
    for k in range(SHOULDER_SPIKES):
        crystal(f"Body_ShoulderGold_{sgn}_{k}", 0.3 * SC, 0.55 * SC, 0.7 * SC,
                (sgn * BW * (0.4 + 0.03 * k), -TL * 0.2 + 0.4 * k * SC, TOPZ + 0.1 * SC),
                (sgn * (0.9 + 0.2 * k), 0.4, 0.8), M_GOLD, body_root, up=(0, 1, 0))

# Cristaux ambre lumineux en grappes dans l'armure (accent Rare)
for k, (yf, xf) in enumerate(GLOW_SPOTS):
    glow_cluster(f"Body_Glow_{k}", (xf * BW * 0.5, TL * yf, TOPZ + 0.25 * SC * STRATA_N * 0.6), (xf * 0.6, 0.2, 1),
                 SC * 0.9, body_root, n=3, up=(1, 0, 0))
if PINK_GLOW:
    crystal("Body_PinkGem", 0.3 * SC, 0.55 * SC, 0.7 * SC, (BW * 0.18, -TL * 0.18, TOPZ + 0.3 * SC), (0.3, 0.2, 1),
            M_PINK, body_root, up=(1, 0, 0), sides=5)
    crystal("Body_PinkGem2", 0.2 * SC, 0.4 * SC, 0.5 * SC, (BW * 0.1, -TL * 0.1, TOPZ + 0.2 * SC), (0.1, -0.1, 1),
            M_PINK, body_root, up=(1, 0, 0), sides=5)

# Touffes de bruyère entre les plaques (signe distinctif)
for k in range(TUFTS):
    f = (k + 0.5) / TUFTS
    sgn = -1 if k % 2 == 0 else 1
    y = -TL * 0.4 + TL * 0.82 * f
    heather(f"Body_Heather_{k}", (sgn * BW * random.uniform(0.18, 0.36), y, TOPZ + 0.08 * SC * STRATA_N),
            (sgn * 0.3, random.uniform(-0.2, 0.2), 1), SC * random.uniform(0.95, 1.4), body_root, up=(1, 0, 0), n=5)

# ----------------------------------------------------------
# 11. PATTES : cuisse en wedge, genouillère de roche, jambe, bracelet doré + lianes lumineuses, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    # genouillère / épaulière de roche sur la cuisse
    # deux dalles de roche qui se chevauchent en écaille sur le haut de la cuisse (pas de « tiroir »)
    for j in range(2):
        wedge(f"{name}_KneeRock_{j}", (th * 0.3, th * (1.15 - 0.25 * j), th * (0.75 - 0.15 * j)),
              (x + sgn * th * (0.6 + 0.06 * j), y + th * 0.08 * j, FOOT_H + SHIN_H + thigh_h * (0.5 + 0.2 * j)),
              (-12, sgn * (24 + 10 * j), 0), (M_ROCK2, M_ROCK1)[j] if hind else (M_ROCK1, M_GOLD)[j], legs_root,
              top_x=0.7, top_y=0.6, bevel=0)
    crystal(f"{name}_KneeGold", 0.2 * th, 0.3 * th, 0.55 * th, (x + sgn * th * 0.7, y + th * 0.1, FOOT_H + SHIN_H + thigh_h * 0.85),
            (sgn * 0.7, 0.35, 1), M_GOLD, legs_root, up=(0, 1, 0))
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=0.05 * SC)
    # Bracelet doré + lianes lumineuses en spirale + grappe de cristaux ambre
    bh_ = SHIN_H * BRACER_K
    zc_ = FOOT_H + SHIN_H * 0.5
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, y + yo, zc_), mat=M_ROCK1, parent=legs_root, bevel=0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.14, th * 1.18, 0.1 * SC), (x, y + yo, zc_ + bh_ / 2), mat=M_ROCK2, parent=legs_root)
    B(f"{name}_BracerLow", (th * 1.14, th * 1.18, 0.08 * SC), (x, y + yo, zc_ - bh_ / 2), mat=M_ROCK2, parent=legs_root)
    for k in (-1, 1):
        B(f"{name}_VineF_{k}", (th * 0.98, 0.08 * SC, 0.1 * SC), (x, y + yo - th * 0.57, zc_ + k * bh_ * 0.15),
          rot=(0, k * 38, 0), mat=M_VINE, parent=legs_root)
        B(f"{name}_VineS_{k}", (0.08 * SC, th * 0.98, 0.1 * SC), (x + sgn * th * 0.55, y + yo, zc_ - k * bh_ * 0.15),
          rot=(0, 0, 0), mat=M_VINE, parent=legs_root)
    if LEG_GLOW:
        glow_cluster(f"{name}_Glow", (x + sgn * th * 0.58, y + yo - th * 0.2, zc_ + bh_ * 0.1), (sgn, -0.2, 0.5), th * 0.75, legs_root,
                     n=2, up=(0, 1, 0))
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2), mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.3, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2, parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    # Petite touffe de bruyère à l'arrière de la cuisse
    if LEG_HEATHER:
        heather(f"{name}_Heather", (x + sgn * th * 0.3, y + th * 0.5, FOOT_H + SHIN_H + thigh_h * 0.95),
                (sgn * 0.3, 0.1, 1), th * 0.7, legs_root, up=(1, 0, 0), n=4)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : aucune (morphologie Drake)
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques crème, roche dorée, bruyère, grappe finale
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.3, 0.0), (0.45, -0.55, 0.3), (0.7, -0.5, 0.2), (0.9, -0.2, -0.2), (1.0, 0.2, -0.3)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.42), (0.3, BW * 0.36), (0.6, BW * 0.27), (0.85, BW * 0.19), (1.0, BW * 0.13)]
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
    wedge(f"Tail_Rock_{i}", (2 * r * 0.8, Ln * 1.0, 0.2 * SC), mid + d * (r * 0.97), R, ROCKS[i % 3], tail_root,
          top_x=0.85, top_y=0.9, bevel=0)
    if i % 2 == 0:
        crystal(f"Tail_Gold_{i}", 0.7 * r * 0.6 + 0.08, 0.3 * SC + r * 0.5, 0.3 * SC + r * 0.6, mid + d * r * 1.0,
                d + t * 0.6, M_GOLD if i % 4 == 0 else M_ROCK1, tail_root, up=side)
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.07 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_ROCK2]), tail_root, up=(sgn, 0, 0))
    if i in TAIL_TUFT_AT:
        sg = 1 if TAIL_TUFT_AT.index(i) % 2 == 0 else -1
        heather(f"Tail_Heather_{i}", mid + d * r * 0.9 + side * sg * r * 0.3, d + side * sg * 0.3, SC * 1.1, tail_root, up=tuple(side), n=4)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipBlock", (BW * 0.3, 0.5 * SC, BW * 0.3), tip, seg_matrix(tt_, td_, ts_), M_ROCK2, tail_root)
for k in range(TAIL_TIP_N):
    a = (k - (TAIL_TIP_N - 1) / 2) * 0.55
    crystal(f"Tail_TipGold_{k}", 0.3 * SC, 0.9 * SC, 0.9 * SC, tip + ts_ * a * 0.25, tt_ + td_ * 0.5 + ts_ * a, M_GOLD if k % 2 == 0 else M_ROCK1,
            tail_root, up=td_)
glow_cluster("Tail_TipGlow", tip + td_ * 0.1, tt_ * 0.5 + td_, SC * 1.1, tail_root, n=3, up=ts_)
if TAIL_TUFT_AT:
    heather("Tail_TipHeather", tip + td_ * 0.2, td_ + tt_ * 0.3, SC * 1.5, tail_root, up=tuple(ts_), n=5)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (bandes de roche, taches), cornes ramifiées, double rangée de pics,
#     accent lumineux discret (yeux ambre, cristaux ambre, lianes dorées ; strength <= 1.5).
#     FX : quelques éclats de roche qui tombent, braises ambre et pétales de bruyère.
# ----------------------------------------------------------
def petal(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.05):
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2), base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.2 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.5), random.uniform(-TL * 0.8, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.8, top_z * 0.97)))
        kind = k % 3
        if kind == 0:
            petal(f"FX_Shard_{k}", p, Vector([random.uniform(-1, 1) for _ in range(3)]), FX_SIZE * random.uniform(0.8, 1.2), FX_SIZE * 0.5,
                  M_ROCK1, master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * SC)
        elif kind == 1:
            place(f"FX_Ember_{k}", bud_mesh(FX_SIZE * 0.12, FX_SIZE * 0.4), M_GLOW, p,
                  basis(Vector([random.uniform(-1, 1) for _ in range(3)])), master)
        else:
            petal(f"FX_Petal_{k}", p, Vector([random.uniform(-1, 1) for _ in range(3)]), FX_SIZE * 0.7, FX_SIZE * 0.4,
                  pick([M_PUR1, M_PUR2]), master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.03 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
