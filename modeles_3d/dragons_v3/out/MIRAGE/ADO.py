import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Mirage · Ado
#  Épique · Terre · Oriental · monde 2
#  - Même corps de script que l'Adulte Mirage v3, réglé pour l'ado : debout sur ses 4 pattes,
#    poitrail droit et long corps en S qui part vers l'arrière, queue qui remonte
#  - Crinière en éclats à mi-taille (2 rangées) qui coule sur le cou, bois courts à 2 pointes, moustaches
#  - Joyau cyan dans sa couronne dorée, sourcils, pupilles fendues, ventre en plaques crème
#  - Rendu Épique à mi-puissance : grappes de cristaux cyan sur le dos, petit plastron à gemme,
#    2 éclats d'aile par épaule, 10 cristaux flottants
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1115)            # même dragon à chaque exécution
TAG = "MIRAGE_ADO"        # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7           # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 8500           # budget de triangles de ce stade et de cette rareté
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
# RÉGLAGES DU STADE (seul bloc qui change entre Bébé, Ado et Adulte)
#  Unités de construction : celles du v3 (tête d'environ 1.5 m de large) ;
#  finalize() remet ensuite le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
HEAD_POS   = Vector((0, -0.4, 6.4))   # base du crâne (HEAD_ROOT)
HEAD_TILT  = 5                        # inclinaison de la tête vers l'avant (degrés)
SNOUT_L    = 1.35                     # longueur du museau
BABY_EYES  = False                    # True = grands yeux ronds avec reflet (bébé)
BROW_ANGLE = 9                        # sourcils : plus l'angle est grand, plus le regard est sévère
ANTLER_K   = 0.6                      # taille des bois (1 = pleine taille)
ANTLER_TINES = 2                      # nombre de ramifications par bois (0 à 3)
WHISKER_K  = 0.75                     # longueur des moustaches
BEARD_N    = 3                        # éclats de barbe
MANE_RINGS, MANE_COUNT, MANE_K = 2, 12, 0.8   # crinière : rangées, éclats par rangée, taille
NECK_MANE_END = 0.18                  # la crinière descend le long du cou jusqu'à s = 0.18

# Colonne vertébrale en S : points de contrôle (Catmull-Rom) et rayon le long du corps (s de 0 à 1)
# L'ado se tient debout : poitrail droit, ventre à l'horizontale, queue qui remonte derrière.
CTRL = [
    (0.0, -0.2, 6.2),   # sous le crâne
    (0.0,  0.2, 5.5),
    (0.0,  0.5, 4.5),   # cou
    (0.0,  0.3, 3.5),   # poitrail
    (0.0,  0.5, 2.6),
    (0.0,  1.3, 2.1),
    (0.0,  2.5, 2.0),   # ventre
    (0.0,  3.7, 2.2),
    (0.0,  4.8, 2.5),   # hanches
    (0.2,  5.9, 2.9),
    (0.5,  6.9, 3.6),   # queue qui remonte
    (0.7,  7.6, 4.5),
    (0.8,  7.8, 5.3),   # bout de queue
]
RADIUS_KEYS = [(0.0, 0.5), (0.1, 0.6), (0.25, 0.8), (0.35, 0.85), (0.5, 0.78),
               (0.65, 0.6), (0.85, 0.35), (1.0, 0.18)]
SEG_STEP   = 0.56                     # longueur d'un segment du corps
TAIL_START = 0.62                     # à partir de s = 0.62, les segments vont dans TAIL_ROOT
CRYSTAL_RANGE = (0.3, 0.8)            # zone du dos qui porte des grappes de cristaux
CRYSTAL_EVERY = 2                     # une grappe tous les N segments
TUFT_N, TUFT_L = 5, 0.8               # touffe de queue : nombre d'éclats, longueur

# Rendu de rareté (Épique, mi-puissance)
CHEST_PLATE = True                    # plastron doré avec gemme cyan
CHEST_S = 0.22                        # position du plastron et des ailes d'épaule sur le corps
SHOULDER_WINGS = 2                    # éclats d'aile grise par épaule (0 = aucun)
FX_COUNT = 10                         # petits cristaux flottants

# Pattes : position sur le corps (s), vecteurs haut et bas de patte, épaisseurs, écart sur le côté.
# GROUNDED = True : les pieds descendent jusqu'au sol (Bébé, Ado). False : pattes pendantes (Adulte qui flotte).
GROUNDED = True
LEG_FRONT = dict(s=0.3,  upper=(0, -0.3, -0.6), lower=(0, -0.1, 0), th_up=0.44, th_low=0.36, push=0.3)
LEG_BACK  = dict(s=0.6,  upper=(0, -0.4, -0.5), lower=(0, 0.15, 0), th_up=0.52, th_low=0.38, push=0.3)
LEG_K = 0.95                          # taille des épaules, pieds et griffes

# ----------------------------------------------------------
# 7. PALETTE (identique aux 3 stades) : or saturé, crème, brun, os, cyan émissif
# ----------------------------------------------------------
M_GOLD   = get_mat("Gold",      "#E7AD38", 0.35, 0.15)   # corps, crâne, pattes
M_LGOLD  = get_mat("LightGold", "#F9CE61", 0.40, 0.10)   # arête du museau, mâchoire, flancs, oreilles
M_DGOLD  = get_mat("DarkGold",  "#B37C30", 0.35, 0.20)   # écailles du dos, bracelets, plastron, sourcils
M_BROWN  = get_mat("Brown",     "#895927", 0.60)         # éclats sombres de la crinière
M_CREAM  = get_mat("Cream",     "#EDDAAA", 0.50)         # plaques du ventre
M_WING   = get_mat("WingGrey",  "#C4BCAA", 0.55)         # petites ailes d'épaule
M_ANTLER = get_mat("Antler",    "#B3A286", 0.60)         # bois de cerf
M_CYAN   = get_mat("Cyan",      "#3FEDE7", 0.10, 0.0, emission="#3FF9ED", strength=3.0)  # cristaux, joyaux
M_WHITE  = get_mat("EyeWhite",  "#F6F6F1", 0.30)
M_IRIS   = get_mat("Iris",      "#FDE561", 0.20)
M_BLACK  = get_mat("Black",     "#302727", 0.20)         # pupilles, narines
M_CLAW   = get_mat("Claw",      "#F9F7EF", 0.30)         # griffes

def mane_mat():
    """Éclats de crinière : mélange or / or clair / brun / or foncé."""
    return pick([M_GOLD, M_LGOLD, M_BROWN, M_DGOLD], [4, 3, 2, 2])

# ----------------------------------------------------------
# 8. HIÉRARCHIE
# ----------------------------------------------------------
master    = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_TILT), 0, 0)).to_matrix().to_4x4())
H = head_root

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT)
# ----------------------------------------------------------
sk = SNOUT_L / 1.55                  # facteur de longueur du museau
box("Head_Skull",       (1.5, 1.55, 1.35), (0, 0, 0), mat=M_GOLD, parent=H, bevel=0.07)
box("Head_Snout",       (1.15, SNOUT_L, 0.72), (0, -0.62 - SNOUT_L / 2, -0.15), mat=M_GOLD, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.8, 1.2 * sk, 0.2), (0, -0.65 - 0.6 * sk, 0.28), rot=(-6, 0, 0), mat=M_LGOLD, parent=H, bevel=0.03)
box("Head_NosePad",     (1.2, 0.3, 0.55), (0, -0.55 - SNOUT_L, -0.12), mat=M_GOLD, parent=H, bevel=0)
box("Head_Jaw",         (1.05, 1.45 * sk, 0.32), (0, -0.53 - 0.72 * sk, -0.68), mat=M_LGOLD, parent=H, bevel=0)
box("Head_MouthLine",   (1.08, 1.4 * sk, 0.06), (0, -0.58 - 0.7 * sk, -0.52), mat=M_DGOLD, parent=H, bevel=0)

# Joyau frontal + couronne dorée
box("Head_GemSocket", (0.7, 0.5, 0.16), (0, -0.62, 0.66), rot=(-20, 0, 0), mat=M_DGOLD, parent=H, bevel=0.03)
crystal("Head_Gem", 0.22, 0.15, 0.22, (0, -0.78, 0.68), (0, -0.45, 1), mat=M_CYAN, parent=H)

for sgn in (-1, 1):
    # Narines
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -0.72 - SNOUT_L, 0.0), mat=M_BLACK, parent=H, bevel=0)
    if BABY_EYES:
        # Grands yeux de bébé : blanc, grand iris, pupille ronde, petit reflet blanc
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.62, 0.58), (sgn * 0.76, -0.3, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.44, 0.48), (sgn * 0.80, -0.33, 0.1), mat=M_IRIS, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.26, 0.32), (sgn * 0.83, -0.35, 0.08), mat=M_BLACK, parent=H, bevel=0)
        box(f"Head_Shine_{sgn}",    (0.04, 0.1, 0.1), (sgn * 0.855, -0.42, 0.18), mat=M_WHITE, parent=H, bevel=0)
    else:
        # Œil : blanc, iris jaune, pupille fendue
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.45, 0.36), (sgn * 0.76, -0.35, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.26, 0.30), (sgn * 0.80, -0.38, 0.12), mat=M_IRIS, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.07, 0.26), (sgn * 0.83, -0.38, 0.12), mat=M_BLACK, parent=H, bevel=0)
    box(f"Head_Brow_{sgn}", (0.35, 0.7, 0.22), (sgn * 0.72, -0.4, 0.44 + (0.08 if BABY_EYES else 0)),
        rot=(BROW_ANGLE, 0, sgn * -8), mat=M_DGOLD, parent=H, bevel=0.03)

    # Couronne autour du joyau
    shard(f"Head_GemFrame_{sgn}", 0.25, 0.12, 0.6, (sgn * 0.3, -0.65, 0.7), (sgn * 0.5, 0.1, 1), mat=M_LGOLD, parent=H)
    shard(f"Head_Crown_{sgn}", 0.32, 0.12, 0.85, (sgn * 0.45, -0.1, 0.7), (sgn * 0.4, 0.6, 1), mat=M_GOLD, parent=H)

    # Oreilles / nageoires et pointes de joues
    shard(f"Head_Ear_{sgn}", 0.42, 0.1, 1.0, (sgn * 0.75, 0.3, 0.35), (sgn * 0.8, 1, 0.4), mat=M_LGOLD, parent=H)
    shard(f"Head_Cheek1_{sgn}", 0.3, 0.1, 0.8, (sgn * 0.6, -0.6, -0.55), (sgn * 0.9, 0.8, -0.3), mat=M_LGOLD, parent=H)
    shard(f"Head_Cheek2_{sgn}", 0.3, 0.1, 0.9, (sgn * 0.55, -0.2, -0.6), (sgn * 0.7, 1, -0.6), mat=M_GOLD, parent=H)

    # Bois de cerf ramifiés (ANTLER_K les raccourcit pour le bébé et l'ado)
    a0 = Vector((sgn * 0.45, 0.35, 0.65))
    def ap(x, y, z):
        return a0 + (Vector((sgn * x, y, z)) - a0) * ANTLER_K
    a1, a2, a3 = ap(0.9, 0.9, 1.8), ap(1.2, 1.6, 2.9), ap(1.25, 2.3, 3.6)
    th = 0.32 * max(0.8, ANTLER_K)
    chain(f"Head_Antler_{sgn}", [a0, a1, a2, a3], th, th * 0.56, M_ANTLER, H, bevel=0.03)
    tines = [(a1, ap(1.1, 0.3, 2.7), 0.18), (a2, ap(1.8, 1.3, 3.6), 0.16), (a2.lerp(a3, 0.4), ap(0.85, 2.0, 3.9), 0.14)]
    for k, (p, q, tk) in enumerate(tines[:ANTLER_TINES]):
        link(f"Head_AntlerTine{k + 1}_{sgn}", p, q, tk * max(0.8, ANTLER_K), M_ANTLER, H, bevel=0)

    # Longues moustaches qui tombent vers l'arrière
    wb = Vector((sgn * 0.58, -0.4 - SNOUT_L, -0.05))
    wpts = [wb] + [wb + (Vector(p) - Vector((sgn * 0.58, -1.95, -0.05))) * WHISKER_K
                   for p in [(sgn * 1.3, -1.6, -0.45), (sgn * 1.8, -0.8, -1.0), (sgn * 2.0, 0.2, -1.8), (sgn * 1.9, 0.8, -2.6)]]
    chain(f"Head_Whisker_{sgn}", wpts, 0.10, 0.07, M_LGOLD, H, bevel=0)

# Barbe sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, (0.7 + random.random() * 0.3) * MANE_K,
          (x, -0.3 - 0.6 * sk + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=mane_mat(), parent=H)

# Crinière en éventail derrière la tête (éclats larges, pas des piques)
for rg in range(MANE_RINGS):
    for k in range(MANE_COUNT):
        ang = math.radians(-155 + k * (310 / (MANE_COUNT - 1)) + rg * 8)
        radial = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (radial.x * 0.6, 0.4 + rg * 0.3, radial.z * 0.55 - 0.05)
        jitter = Vector((random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.2), random.uniform(-0.2, 0.2)))
        direction = radial * (1.1 - rg * 0.3) + Vector((0, 1.0, 0)) + jitter
        shard(f"Head_Mane_{rg}_{k}", (0.65 - rg * 0.08) * max(0.8, MANE_K), 0.14,
              (1.4 + rg * 0.3 + random.random() * 0.5) * MANE_K,
              loc, direction, mat=mane_mat(), parent=H, up=tuple(radial.cross(Vector((0, 1, 0)))))

# ----------------------------------------------------------
# 10. CORPS EN S : segments, ventre, flancs, écailles du dos, cristaux, crinière du cou
# ----------------------------------------------------------
SPINE = resample(sample_curve(CTRL), SEG_STEP)
N = len(SPINE) - 1

def radius(s):
    return keyed(RADIUS_KEYS, s)

def frame_at(s):
    """Milieu, tangente, dos, côté et rayon du segment situé à la fraction s du corps."""
    i = min(N - 1, max(0, int(s * N)))
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = frame(SPINE[i + 1] - SPINE[i])
    return mid, t, d, side, radius(s)

for i in range(N):
    p1, p2 = SPINE[i], SPINE[i + 1]
    L = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / N
    r = radius(s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    parent = body_root if s < TAIL_START else tail_root
    tag = "Body" if s < TAIL_START else "Tail"

    # Segment principal (gros bloc biseauté)
    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R, M_GOLD, parent, bevel=0.06)

    # Plaques de ventre crème (segmentées) + bandes claires sur les flancs
    if s < 0.85:
        box(f"{tag}_Belly_{i}", (2 * r * 0.86, L * 0.85, 0.22), mid - d * (r * 0.95), R, M_CREAM, parent, bevel=0.03)
        for sgn in (-1, 1):
            box(f"{tag}_Flank_{i}_{sgn}", (0.1, L * 0.9, r * 1.1), mid + side * sgn * r - d * r * 0.2,
                R, M_LGOLD, parent, bevel=0.02)

    # Écaille dorsale légèrement inclinée
    Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
    box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.2), mid + d * (r * 0.95), Rtilt, M_DGOLD, parent, bevel=0.03)

    # Grappes de 1 à 3 cristaux cyan sur le dos
    if CRYSTAL_RANGE[0] < s < CRYSTAL_RANGE[1] and i % CRYSTAL_EVERY == 0:
        n_cr = 1 + (random.random() < 0.6) + (random.random() < 0.35)
        for c in range(n_cr):
            off = 0.0 if c == 0 else random.choice((-1, 1)) * random.uniform(0.25, 0.45) * r
            direction = d + t * 0.55 + side * (off * 0.8) + Vector([random.uniform(-0.1, 0.1) for _ in range(3)])
            sc = r * (1.0 if c == 0 else random.uniform(0.55, 0.75))
            crystal(f"{tag}_Crystal_{i}_{c}", 0.3 * sc, 0.7 * sc, 0.45 * sc,
                    mid + d * (r * 0.85) + side * off + t * random.uniform(-0.1, 0.1),
                    direction, mat=M_CYAN, parent=parent)

    # Petites nageoires dorsales sur la fin de la queue
    if s >= 0.82:
        shard(f"Tail_Fin_{i}", 0.35 * r + 0.1, 0.08, 0.5 + r * 0.6, mid + d * r * 0.9, d + t * 0.8,
              mat=M_LGOLD, parent=tail_root)

    # Crinière qui coule le long du cou
    if s < NECK_MANE_END:
        fade = 1.0 - s / NECK_MANE_END
        for k, amt in enumerate((-1.5, -0.5, 0.5, 1.5)):
            amt = amt * 0.35 + random.uniform(-0.1, 0.1)
            shard(f"Body_NeckMane_{i}_{k}", 0.6 * max(0.8, MANE_K), 0.12, (1.0 + 0.9 * fade + random.random() * 0.4) * MANE_K,
                  mid + d * r * 0.8 + side * amt * r * 0.5, d + t * 0.9 + side * amt,
                  mat=mane_mat(), parent=body_root)
        for sgn in (-1, 1):
            shard(f"Body_NeckSide_{i}_{sgn}", 0.32, 0.1, (0.7 + 0.5 * fade) * MANE_K,
                  mid + side * sgn * r * 0.85, side * sgn + t * 0.8 + d * 0.3,
                  mat=mane_mat(), parent=body_root)

# ----------------------------------------------------------
# 11. PATTES AVEC BRACELETS ET GRIFFES
# ----------------------------------------------------------
def paw(name, center):
    k_ = LEG_K
    box(f"{name}_Paw", (0.55 * k_, 0.55 * k_, 0.3 * k_), center, mat=M_GOLD, parent=legs_root, bevel=0.04)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0)) * k_
        end = center + Vector((k * 0.24, -0.55, -0.08 if GROUNDED else -0.2)) * k_
        link(f"{name}_Toe_{k}", base, end, 0.14 * k_, M_GOLD, legs_root, bevel=0)
        shard(f"{name}_Claw_{k}", 0.12 * k_, 0.12 * k_, 0.28 * k_, end,
              (k * 0.2, -1, -0.4 if GROUNDED else -0.9), mat=M_CLAW, parent=legs_root)

def leg(name, cfg):
    mid, t, d, side, r = frame_at(cfg["s"])
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.85 - d * 0.15
        joint = root + Vector((sgn * cfg["push"], 0, 0)) + Vector(cfg["upper"])
        if GROUNDED:
            # le poignet descend jusqu'au sol : le pied se pose à Z = 0
            low = Vector(cfg["lower"])
            wrist = Vector((joint.x + sgn * 0.05 + low.x, joint.y + low.y, 0.27 * LEG_K))
        else:
            wrist = joint + Vector((sgn * 0.05, 0, 0)) + Vector(cfg["lower"])
        box(f"{n}_Shoulder", (0.62 * LEG_K,) * 3, root, mat=M_GOLD, parent=legs_root, bevel=0.06)
        link(f"{n}_Upper", root, joint, cfg["th_up"], M_GOLD, legs_root, up=(1, 0, 0), bevel=0.05)
        link(f"{n}_Lower", joint, wrist, cfg["th_low"], M_GOLD, legs_root, up=(1, 0, 0), bevel=0.04)
        link(f"{n}_Cuff", joint.lerp(wrist, 0.6), wrist, cfg["th_low"] + 0.14, M_DGOLD, legs_root, up=(1, 0, 0), bevel=0.03)
        shard(f"{n}_ElbowSpike", 0.25 * LEG_K, 0.08, 0.6 * LEG_K, joint, (sgn * 0.4, 0.8, 0.2), mat=M_LGOLD, parent=legs_root)
        paw(n, wrist + Vector((0, -0.2, -0.12)) * LEG_K)

leg("Legs_Front", LEG_FRONT)
leg("Legs_Back", LEG_BACK)

# ----------------------------------------------------------
# 12. AILES : pas de grandes ailes (oriental) -> petites ailes d'épaule, voir section 14
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : collier, touffe d'éclats dorés et cristal au bout
# ----------------------------------------------------------
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
box("Tail_TipCollar", (0.5, 0.4, 0.5), tip, seg_matrix(tt, td, tside), M_DGOLD, tail_root, bevel=0.03)
for k in range(TUFT_N):
    a = k / TUFT_N * 2 * math.pi
    spread = tside * math.cos(a) + td * math.sin(a)
    shard(f"Tail_Tuft_{k}", 0.35, 0.1, TUFT_L + random.random() * 0.5 * TUFT_L, tip, tt + spread * 0.6,
          mat=random.choice([M_LGOLD, M_GOLD]), parent=tail_root)
crystal("Tail_TipCrystal", 0.18, 0.4, 0.35, tip + tt * 0.2, tt, mat=M_CYAN, parent=tail_root)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (Épique) : plastron à gemme, ailes d'épaule, cristaux flottants
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(CHEST_S)
CR = seg_matrix(ct, cd, cside)
if CHEST_PLATE:
    box("Body_ChestPlate", (2 * cr * 1.05, 1.4, 0.25), cmid - cd * (cr + 0.05), CR, M_DGOLD, body_root, bevel=0.05)
    box("Body_ChestInner", (2 * cr * 0.7, 1.0, 0.12), cmid - cd * (cr + 0.2), CR, M_GOLD, body_root, bevel=0.03)
    crystal("Body_ChestGem", 0.3, 0.2, 0.28, cmid - cd * (cr + 0.2), -cd, mat=M_CYAN, parent=body_root, up=tuple(ct))
for sgn in (-1, 1):
    if CHEST_PLATE:
        shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.7, cmid - cd * (cr + 0.25) + cside * sgn * 0.35,
              cside * sgn * 0.6 - ct * 1.0, mat=M_LGOLD, parent=body_root)
    for k in range(SHOULDER_WINGS):
        shard(f"Body_Wing_{sgn}_{k}", 0.5 - k * 0.08, 0.08, 1.3 - k * 0.2,
              cmid + cside * sgn * (cr + 0.1) + cd * (0.35 - k * 0.15) - ct * (0.3 - k * 0.25),
              ct * 0.6 + cd * 0.8 + cside * sgn * 0.6, mat=M_WING, parent=body_root)

if ADD_FLOATING_FX:
    lo = Vector([min(p[j] for p in CTRL) for j in range(3)])
    hi = Vector([max(p[j] for p in CTRL) for j in range(3)])
    for k in range(FX_COUNT):
        p = Vector((random.uniform(-2.5, 2.5), random.uniform(lo.y - 2.0, hi.y + 0.6),
                    random.uniform(max(1.5, lo.z), HEAD_POS.z + 1.8)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        crystal(f"FX_Crystal_{k}", 0.08, 0.12, 0.12, p, dirv, mat=M_CYAN, parent=master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
