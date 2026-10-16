import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Neptyr · Adulte
#  Légendaire · Eau · Oriental · monde 3
#  - Long dragon oriental d'eau qui flotte en vague : corps bleu nuit, ventre turquoise en plaques, bandes claires
#  - Bois dorés ramifiés (métal), diadème doré, crinière et nageoires bleu ciel translucides, moustaches lumineuses
#  - Spirales et runes cyan émissives sur les flancs, nageoire dorsale continue, bandes d'or, double rangée de pics dorés
#  - Rendu Légendaire : plastron et épaulières dorés, aura (anneaux et pointes) derrière la tête, FX riches
#  - Queue en grande nageoire plumeuse translucide avec ornement final (cristal, pétales d'or, anneau runique)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3303)            # même dragon à chaque exécution
TAG = "NEPTYR_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 15000          # budget de triangles de ce stade et de cette rareté
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
#  Unités de construction : tête d'environ 1.5 m de large ; finalize() remet ensuite le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
HEAD_POS   = Vector((0, -0.4, 9.2))   # base du crâne (HEAD_ROOT)
HEAD_TILT  = 5                        # inclinaison de la tête vers l'avant (degrés)
SNOUT_L    = 1.55                     # longueur du museau
BABY_EYES  = False                    # True = grands yeux ronds avec reflet (bébé)
BROW_ANGLE = 14                       # sourcils : plus l'angle est grand, plus le regard est sévère
FANGS      = 3                        # crocs par côté
CROWN      = True                     # diadème doré sur le front
GEM_K      = 1.2                      # taille du joyau frontal
EAR_K, EAR_RAYS = 1.0, 4              # nageoires-oreilles : taille et nombre de rayons
ANTLER_K   = 1.0                      # taille des bois (1 = pleine taille)
ANTLER_TINES = 4                      # nombre de ramifications par bois (0 à 4)
WHISKER_K  = 1.0                      # longueur des moustaches
BEARD_N    = 5                        # éclats de barbe
MANE_RINGS, MANE_COUNT, MANE_K = 3, 18, 1.0   # crinière : rangées, éclats par rangée, taille

# Colonne vertébrale en vague : points de contrôle (Catmull-Rom) et rayon le long du corps (s de 0 à 1)
CTRL = [
    (0.0, -0.3, 9.0),   # sous le crâne
    (0.0,  0.3, 8.2),
    (0.2,  1.0, 7.0),   # cou
    (0.4,  1.6, 5.6),
    (0.3,  2.6, 4.3),   # poitrail
    (0.0,  4.2, 3.4),
    (-0.4, 6.0, 3.4),
    (-0.6, 7.8, 4.4),   # dos qui monte
    (-0.3, 9.6, 4.9),
    (0.3, 11.4, 4.0),
    (0.7, 13.0, 2.9),   # creux
    (0.5, 14.6, 2.5),
    (0.0, 16.0, 3.4),   # queue qui remonte
    (-0.5, 17.4, 4.8),
    (-0.7, 18.6, 6.2),  # bout de queue
]
RADIUS_KEYS = [(0.0, 0.6), (0.06, 0.7), (0.2, 0.82), (0.35, 0.95), (0.55, 0.9), (0.75, 0.6), (0.9, 0.36), (1.0, 0.22)]
SEG_STEP   = 0.6                      # longueur d'un segment du corps
SEG_BEVEL  = 0.06                     # biseau des segments
TAIL_START = 0.62                     # à partir de s = 0.62, les segments vont dans TAIL_ROOT
SWIRL_RANGE, SWIRL_EVERY = (0.12, 0.92), 6   # spirales (et runes entre elles) tous les N segments
BAND_EVERY = 8                        # bandes d'or autour du corps (0 = aucune)
SPIKE_ROWS = True                     # double rangée de pics dorés sur le dos
FIN_RANGE, FIN_H, FIN_RAY_EVERY = (0.04, 0.99), 0.75, 2   # nageoire dorsale : zone, hauteur, rayons
TAIL_K = 1.0                          # taille de l'ornement de queue
TAIL_FAN_N, TAIL_FAN_L, TAIL_PETALS, TAIL_RING = 9, 2.6, 6, True   # plumes, longueur, pétales d'or, anneau

# Rendu de rareté (Légendaire)
CHEST_PLATE = True                    # plastron doré avec gemme cyan
CHEST_S = 0.2                         # position du plastron et des épaulières sur le corps
PAULDRONS = True                      # épaulières dorées
SHOULDER_FINS = 2                     # éclats d'aileron translucide par épaule
AURA_N, AURA_R = 16, 2.7              # aura derrière la tête : pointes et rayon (0 = aucune)
FX_COUNT, FX_RINGS, FX_K = 16, 4, 1.5  # FX flottants : cristaux et gouttes, anneaux, taille

# Pattes
GROUNDED = False
LEG_WEDGE = True                      # True = épaule en bloc biseauté (adulte)
LEG_FIN_RAYS = 3                      # rayons de l'aileron de coude
LEG_FRONT = dict(s=0.2, upper=(0, -0.55, -0.75), lower=(0, -0.75, -0.25), th_up=0.48, th_low=0.38, push=0.35)
LEG_BACK  = dict(s=0.5, upper=(0, -0.7, -0.45),  lower=(0, 0.35, -0.8),   th_up=0.6,  th_low=0.42, push=0.30)
LEG_K = 1.0                           # taille des épaules, pieds et griffes

# ----------------------------------------------------------
# 7. PALETTE (identique aux 3 stades) : bleu profond, turquoise, or métallique, cyan émissif, nageoires translucides
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#1F4FA3", 0.40)         # corps, crâne, pattes
M_DARK   = get_mat("ScaleDark",  "#143570", 0.45)         # écailles du dos, mâchoire, narines claires
M_LIGHT  = get_mat("ScaleLight", "#4A86D0", 0.40)         # arête du museau, bandes des flancs
M_BELLY  = get_mat("Belly",      "#8ED6D0", 0.50)         # plaques du ventre, menton
M_GOLD   = get_mat("Gold",       "#E8B93C", 0.28, 0.9)    # bois, diadème, plastron, bracelets (métal)
M_FIN    = get_mat("Fin",        "#9FDDF5", 0.25, 0.0, alpha=0.55)   # crinière, nageoires (translucide)
M_FIN2   = get_mat("Fin2",       "#7FD8D8", 0.30, 0.0, alpha=0.70)   # nageoires turquoise (translucide)
M_RAY    = get_mat("FinRay",     "#6EC1EC", 0.35)         # rayons des nageoires, sourcils
M_GLOW   = get_mat("Glow",       "#3FE0FF", 0.10, 0.0, emission="#3FE0FF", strength=3.0)   # runes, spirales, yeux, gemmes
M_WHISK  = get_mat("Whisker",    "#9FE8FF", 0.20, 0.0, emission="#7FEBFF", strength=2.0)   # moustaches lumineuses
M_WHITE  = get_mat("EyeWhite",   "#F2F2F2", 0.30)         # yeux, crocs
M_BLACK  = get_mat("Black",      "#0A0F1E", 0.20)         # pupilles, narines
M_CLAW   = get_mat("Claw",       "#F4DC8A", 0.30, 0.8)    # griffes dorées claires

def mane_mat():
    """Éclats de crinière : bleu ciel et turquoise translucides, quelques éclats dorés."""
    return pick([M_FIN, M_FIN2, M_GOLD], [5, 3, 1])

def fin_fan(name, root, tips, parent, mat_ray=M_RAY, mat_memb=M_FIN, ray_t=0.07, memb_t=0.04):
    """Nageoire en éventail : rayons qui partent de 'root' et membrane translucide entre eux."""
    root = Vector(root)
    for k, tp in enumerate(tips):
        link(f"{name}_Ray{k}", root, tp, ray_t, mat_ray, parent, extra=0.04, bevel=0)
    for k in range(len(tips) - 1):
        plate(f"{name}_Memb{k}", [root, Vector(tips[k]), Vector(tips[k + 1])], memb_t, mat_memb, parent)

# ----------------------------------------------------------
# 8. HIÉRARCHIE
# ----------------------------------------------------------
master     = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root  = empty("BODY_ROOT", master)
legs_root  = empty("LEGS_ROOT", master)
tail_root  = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)      # nageoires : dorsale et ailerons des pattes
head_root  = empty("HEAD_ROOT", master,
                   Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_TILT), 0, 0)).to_matrix().to_4x4())
H = head_root

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT)
# ----------------------------------------------------------
sk = SNOUT_L / 1.55                  # facteur de longueur du museau
wedge("Head_Skull",     (1.5, 1.55, 1.35), (0, 0, 0), mat=M_BODY, parent=H, top_x=0.86, top_y=0.92, bevel=0.07)
box("Head_Snout",       (1.1, SNOUT_L, 0.72), (0, -0.62 - SNOUT_L / 2, -0.15), mat=M_BODY, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.78, 1.2 * sk, 0.2), (0, -0.65 - 0.6 * sk, 0.28), rot=(-6, 0, 0), mat=M_LIGHT, parent=H, bevel=0)
box("Head_NosePad",     (1.15, 0.3, 0.55), (0, -0.55 - SNOUT_L, -0.12), mat=M_BODY, parent=H, bevel=0)
box("Head_Jaw",         (1.0, 1.45 * sk, 0.32), (0, -0.53 - 0.72 * sk, -0.68), mat=M_BELLY, parent=H, bevel=0)
box("Head_MouthLine",   (1.04, 1.4 * sk, 0.06), (0, -0.58 - 0.7 * sk, -0.52), mat=M_DARK, parent=H, bevel=0)

# Diadème doré sur le front (Ado et Adulte) ou simple joyau (Bébé)
box("Head_GemSocket", (0.62, 0.45, 0.16), (0, -0.6, 0.66), rot=(-20, 0, 0), mat=M_GOLD, parent=H, bevel=0)
crystal("Head_Gem", 0.2 * GEM_K, 0.14, 0.2 * GEM_K, (0, -0.76, 0.68), (0, -0.45, 1), mat=M_GLOW, parent=H)
if CROWN:
    box("Head_DiademBand", (1.25, 0.2, 0.14), (0, -0.2, 0.7), rot=(-8, 0, 0), mat=M_GOLD, parent=H, bevel=0)
    shard("Head_DiademSpike_C", 0.32, 0.1, 0.95, (0, -0.35, 0.72), (0, 0.15, 1), mat=M_GOLD, parent=H)
for sgn in (-1, 1):
    if CROWN:
        shard(f"Head_DiademSpike_{sgn}", 0.26, 0.1, 0.7, (sgn * 0.38, -0.3, 0.7), (sgn * 0.35, 0.25, 1), mat=M_GOLD, parent=H)
        shard(f"Head_DiademWing_{sgn}", 0.22, 0.1, 0.55, (sgn * 0.66, -0.15, 0.66), (sgn * 1, 0.3, 0.55), mat=M_GOLD, parent=H)

for sgn in (-1, 1):
    # Narines
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -0.72 - SNOUT_L, 0.0), mat=M_BLACK, parent=H, bevel=0)
    if BABY_EYES:
        # Grands yeux de bébé : blanc, grand iris cyan lumineux, pupille ronde, petit reflet blanc
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.62, 0.58), (sgn * 0.76, -0.3, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.44, 0.48), (sgn * 0.80, -0.33, 0.1), mat=M_GLOW, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.26, 0.32), (sgn * 0.83, -0.35, 0.08), mat=M_BLACK, parent=H, bevel=0)
        box(f"Head_Shine_{sgn}",    (0.04, 0.1, 0.1), (sgn * 0.855, -0.42, 0.18), mat=M_WHITE, parent=H, bevel=0)
    else:
        # Œil en amande : blanc, iris cyan lumineux, pupille fendue
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.45, 0.36), (sgn * 0.76, -0.35, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.28, 0.30), (sgn * 0.80, -0.38, 0.12), mat=M_GLOW, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.07, 0.26), (sgn * 0.83, -0.38, 0.12), mat=M_BLACK, parent=H, bevel=0)
    box(f"Head_Brow_{sgn}", (0.33, 0.7, 0.2), (sgn * 0.72, -0.4, 0.44 + (0.08 if BABY_EYES else 0)),
        rot=(BROW_ANGLE, 0, sgn * -8), mat=M_RAY, parent=H, bevel=0)

    # Crocs (Ado : petits ; Adulte : 3 par côté)
    for j in range(FANGS):
        fy = -0.8 - SNOUT_L * (0.18 + 0.27 * j)
        shard(f"Head_Fang_{sgn}_{j}", 0.13, 0.1, 0.42 - 0.07 * j, (sgn * 0.5, fy, -0.5), (0, 0, -1), mat=M_WHITE, parent=H, up=(0, 1, 0))

    # Oreilles-nageoires translucides (rayons + membrane) et nageoires de joue
    ek = EAR_K
    fin_fan(f"Head_Ear_{sgn}", (sgn * 0.7, 0.3, 0.3),
            [(sgn * 1.3 * ek, 0.9 * ek, 1.2 * ek), (sgn * 1.9 * ek, 1.2 * ek, 0.7 * ek),
             (sgn * 2.0 * ek, 1.2 * ek, 0.0), (sgn * 1.7 * ek, 1.0 * ek, -0.6 * ek)][:EAR_RAYS], H)
    fin_fan(f"Head_Cheek_{sgn}", (sgn * 0.7, -0.45, -0.45),
            [(sgn * 1.5 * ek, -0.1, -0.7 * ek), (sgn * 1.6 * ek, 0.5 * ek, -1.0 * ek), (sgn * 1.3 * ek, 0.9 * ek, -1.4 * ek)][:max(2, EAR_RAYS - 1)], H,
            mat_memb=M_FIN2)

    # Bois dorés ramifiés (ANTLER_K les raccourcit pour le bébé et l'ado)
    a0 = Vector((sgn * 0.45, 0.35, 0.65))
    def ap(x, y, z):
        return a0 + (Vector((sgn * x, y, z)) - a0) * ANTLER_K
    a1, a2, a3 = ap(0.9, 0.9, 1.8), ap(1.3, 1.7, 2.9), ap(1.3, 2.5, 3.7)
    th = 0.30 * max(0.8, ANTLER_K)
    chain(f"Head_Antler_{sgn}", [a0, a1, a2, a3], th, th * 0.55, M_GOLD, H, bevel=0.02)
    tines = [(a1, ap(1.2, 0.3, 2.8), 0.17), (a2, ap(1.9, 1.4, 3.7), 0.16), (a2.lerp(a3, 0.4), ap(0.9, 2.2, 4.0), 0.14),
             (a3, ap(1.7, 3.0, 4.2), 0.12)]
    for k, (p, q, tk) in enumerate(tines[:ANTLER_TINES]):
        link(f"Head_AntlerTine{k + 1}_{sgn}", p, q, tk * max(0.8, ANTLER_K), M_GOLD, H, bevel=0)

    # Longues moustaches lumineuses qui flottent vers l'arrière
    wb = Vector((sgn * 0.58, -0.4 - SNOUT_L, -0.05))
    wpts = [wb] + [wb + (Vector(p) - Vector((sgn * 0.58, -1.95, -0.05))) * WHISKER_K
                   for p in [(sgn * 1.3, -1.6, -0.45), (sgn * 2.0, -0.8, -0.9), (sgn * 2.5, 0.2, -1.1), (sgn * 3.0, 1.2, -0.8)]]
    chain(f"Head_Whisker_{sgn}", wpts, 0.10, 0.07, M_WHISK, H, bevel=0)

# Barbe translucide sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, (0.7 + random.random() * 0.3) * MANE_K,
          (x, -0.3 - 0.6 * sk + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=M_FIN2, parent=H)

# Crinière bleu ciel translucide en éventail derrière la tête
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
# 10. CORPS EN S : segments, ventre, flancs, nageoire dorsale, spirales et runes
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

# Repère lissé à chaque point de la colonne (pour une nageoire dorsale continue)
PF = [frame(SPINE[min(N, k + 1)] - SPINE[max(0, k - 1)]) for k in range(N + 1)]
PR = [radius(k / N) for k in range(N + 1)]

def swirl(name, c, t, d, nrm, rho, parent, sgn, turns=1.4, n=6, th=0.075):
    """Spirale cyan lumineuse posée sur le flanc (suite de petites barres)."""
    pts = []
    for k in range(n + 1):
        f = k / n
        a = sgn * f * turns * 2 * math.pi
        rr = rho * (0.2 + 0.8 * f)
        pts.append(c + t * math.cos(a) * rr + d * math.sin(a) * rr)
    for k in range(n):
        link(f"{name}_{k}", pts[k], pts[k + 1], th, M_GLOW, parent, up=tuple(nrm), extra=th * 0.6, bevel=0)

GLYPHS = [
    [((0, -1), (0, 1)), ((0, 0.1), (0.8, 0.7))],
    [((-0.7, -0.9), (0.7, -0.9)), ((0, -0.9), (0, 1))],
    [((-0.6, 1), (0, -1)), ((0, -1), (0.6, 1))],
]

def rune(name, c, t, d, nrm, size, parent, kind, th=0.075):
    """Rune cyan lumineuse : 2 ou 3 traits posés sur le flanc."""
    for k, (a, b) in enumerate(GLYPHS[kind % len(GLYPHS)]):
        pa = c + t * a[0] * size + d * a[1] * size
        pb = c + t * b[0] * size + d * b[1] * size
        link(f"{name}_{k}", pa, pb, th, M_GLOW, parent, up=tuple(nrm), extra=th * 0.6, bevel=0)

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
    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R, M_BODY, parent, bevel=SEG_BEVEL)

    # Plaques de ventre turquoise (segmentées) + bandes claires sur les flancs
    if s < 0.88:
        box(f"{tag}_Belly_{i}", (2 * r * 0.84, L * 0.85, 0.2), mid - d * (r * 0.95), R, M_BELLY, parent, bevel=0)
        for sgn in (-1, 1):
            box(f"{tag}_Flank_{i}_{sgn}", (0.08, L * 0.9, r * 0.5), mid + side * sgn * r - d * r * 0.55,
                R, M_LIGHT, parent, bevel=0)

    # Écaille dorsale sombre légèrement inclinée
    Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
    box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.18), mid + d * (r * 0.95), Rtilt, M_DARK, parent, bevel=0)

    # Spirales et runes cyan lumineuses sur les flancs (alternées)
    if SWIRL_RANGE[0] < s < SWIRL_RANGE[1]:
        for sgn in (-1, 1):
            c = mid + side * sgn * (r + 0.03) + d * r * 0.1
            rho = min(r * 0.5, 0.5)
            if i % SWIRL_EVERY == 0:
                swirl(f"{tag}_Swirl_{i}_{sgn}", c, t, d, side * sgn, rho, parent, sgn)
            elif i % SWIRL_EVERY == SWIRL_EVERY // 2:
                rune(f"{tag}_Rune_{i}_{sgn}", c, t, d, side * sgn, rho * 0.8, parent, i + (sgn > 0))

    # Bandes d'or autour du corps (Légendaire)
    if BAND_EVERY and i % BAND_EVERY == BAND_EVERY // 2 and 0.08 < s < 0.9:
        ring(f"{tag}_Band_{i}", r * 1.06, 0.16, 0.3, mid, t, M_GOLD, parent, sides=8, up=tuple(d))

    # Double rangée de pics dorés sur le dos
    if SPIKE_ROWS and i % 2 == 0 and 0.1 < s < 0.92:
        for sgn in (-1, 1):
            shard(f"{tag}_Spike_{i}_{sgn}", 0.2 + 0.1 * r, 0.1, 0.35 + r * 0.5,
                  mid + d * r * 0.9 + side * sgn * r * 0.4, d + side * sgn * 0.5 + t * 0.4, mat=M_GOLD, parent=parent)

# Nageoire dorsale continue : membrane translucide entre les points du dos + rayons
for i in range(N):
    s = (i + 0.5) / N
    if not (FIN_RANGE[0] <= s <= FIN_RANGE[1]):
        continue
    parent = wings_root
    t0, d0, _ = PF[i]
    t1, d1, _ = PF[i + 1]
    h0 = FIN_H * (0.45 + PR[i] * 1.0) * (1.0 + 0.5 * (s > 0.9))
    h1 = FIN_H * (0.45 + PR[i + 1] * 1.0) * (1.0 + 0.5 * (s > 0.9))
    b0 = SPINE[i] + d0 * PR[i] * 0.9
    b1 = SPINE[i + 1] + d1 * PR[i + 1] * 0.9
    plate(f"Fin_Memb_{i}", [b0, b0 + d0 * h0 - t0 * 0.3, b1 + d1 * h1 - t1 * 0.3, b1], 0.05, M_FIN if i % 2 == 0 else M_FIN2, parent)
    if i % FIN_RAY_EVERY == 0:
        link(f"Fin_Ray_{i}", b0, b0 + d0 * (h0 + 0.1) - t0 * 0.3, 0.07, M_RAY, parent, up=tuple(PF[i][2]), extra=0.03, bevel=0)

# ----------------------------------------------------------
# 11. PATTES : épaule, avant-bras, bracelet doré, ailerons, pied à 3 griffes
# ----------------------------------------------------------
def paw(name, center):
    k_ = LEG_K
    box(f"{name}_Paw", (0.55 * k_, 0.55 * k_, 0.3 * k_), center, mat=M_BODY, parent=legs_root, bevel=0.04 if LEG_K >= 1 else 0.03)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0)) * k_
        end = center + Vector((k * 0.24, -0.55, -0.08 if GROUNDED else -0.2)) * k_
        link(f"{name}_Toe_{k}", base, end, 0.14 * k_, M_BODY, legs_root, bevel=0)
        shard(f"{name}_Claw_{k}", 0.12 * k_, 0.12 * k_, 0.28 * k_, end,
              (k * 0.2, -1, -0.4 if GROUNDED else -0.9), mat=M_CLAW, parent=legs_root)

def leg(name, cfg):
    mid, t, d, side, r = frame_at(cfg["s"])
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.85 - d * 0.15
        joint = root + Vector((sgn * cfg["push"], 0, 0)) + Vector(cfg["upper"])
        if GROUNDED:
            low = Vector(cfg["lower"])
            wrist = Vector((joint.x + sgn * 0.05 + low.x, joint.y + low.y, 0.27 * LEG_K))
        else:
            wrist = joint + Vector((sgn * 0.05, 0, 0)) + Vector(cfg["lower"])
        if LEG_WEDGE:
            wedge(f"{n}_Shoulder", (0.75 * LEG_K, 0.8 * LEG_K, 0.7 * LEG_K), root, mat=M_BODY, parent=legs_root,
                  top_x=0.8, top_y=0.75, bevel=0.05)
        else:
            box(f"{n}_Shoulder", (0.6 * LEG_K,) * 3, root, mat=M_BODY, parent=legs_root, bevel=0.05)
        link(f"{n}_Upper", root, joint, cfg["th_up"], M_BODY, legs_root, up=(1, 0, 0), bevel=0.04)
        link(f"{n}_Lower", joint, wrist, cfg["th_low"], M_BODY, legs_root, up=(1, 0, 0), bevel=0)
        link(f"{n}_Cuff", joint.lerp(wrist, 0.62), wrist, cfg["th_low"] + 0.14, M_GOLD, legs_root, up=(1, 0, 0), bevel=0)
        # Ailerons translucides au coude
        fin_fan(f"{n}_ElbowFin", joint, [joint + Vector((sgn * 0.5, 0.5, 0.35)) * LEG_K,
                                         joint + Vector((sgn * 0.6, 0.9, -0.05)) * LEG_K,
                                         joint + Vector((sgn * 0.45, 1.1, -0.5)) * LEG_K][:LEG_FIN_RAYS], wings_root, ray_t=0.06)
        paw(n, wrist + Vector((0, -0.2, -0.12)) * LEG_K)

leg("Legs_Front", LEG_FRONT)
leg("Legs_Back", LEG_BACK)

# ----------------------------------------------------------
# 12. NAGEOIRES : pas d'ailes (oriental). Dorsale continue en section 10, nageoires-oreilles en section 9,
#     ailerons de coude en section 11, grande nageoire de queue en section 13.
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : collier d'or, cristal, pétales dorés et grande nageoire plumeuse
# ----------------------------------------------------------
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
box("Tail_TipCollar", (0.5, 0.4, 0.5), tip, seg_matrix(tt, td, tside), M_GOLD, tail_root, bevel=0)
crystal("Tail_TipCrystal", 0.2 * TAIL_K, 0.4 * TAIL_K, 0.45 * TAIL_K, tip + tt * 0.15, tt, mat=M_GLOW, parent=tail_root, up=tuple(td))
# Grande nageoire plumeuse : plumes translucides en éventail dans le plan tangente / dos
for k in range(TAIL_FAN_N):
    a = math.radians(-80 + k * 160 / max(1, TAIL_FAN_N - 1))
    dv = tt * math.cos(a) + td * math.sin(a)
    Lk = TAIL_FAN_L * (1.0 - 0.35 * abs(a) / math.radians(80)) * (1.0 + 0.15 * random.random())
    shard(f"Tail_Feather_{k}", 0.55 * TAIL_K, 0.07, Lk, tip + tt * 0.1, dv,
          mat=M_FIN if k % 2 == 0 else M_FIN2, parent=tail_root, up=tuple(tside))
# Ornement final : petales d'or autour du cristal
for k in range(TAIL_PETALS):
    a = k / TAIL_PETALS * 2 * math.pi
    sp = tside * math.cos(a) + td * math.sin(a)
    shard(f"Tail_Petal_{k}", 0.3 * TAIL_K, 0.1, 0.9 * TAIL_K, tip - tt * 0.05, tt + sp * 0.55, mat=M_GOLD, parent=tail_root)
if TAIL_RING:
    ring("Tail_Ring", 0.95 * TAIL_K, 0.12, 0.08, tip + tt * 0.9 * TAIL_K, tt, M_GLOW, tail_root, sides=12, up=tuple(td))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (Légendaire) : plastron et épaulières dorés, aura derrière la tête, FX riches
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(CHEST_S)
CR = seg_matrix(ct, cd, cside)
if CHEST_PLATE:
    wedge("Body_ChestPlate", (2 * cr * 1.05, 1.5, 0.3), cmid - cd * (cr + 0.05), CR, M_GOLD, body_root, top_x=0.8, top_y=0.85, bevel=0)
    box("Body_ChestInner", (2 * cr * 0.65, 1.0, 0.14), cmid - cd * (cr + 0.22), CR, M_DARK, body_root, bevel=0)
    crystal("Body_ChestGem", 0.3, 0.2, 0.3, cmid - cd * (cr + 0.28), -cd, mat=M_GLOW, parent=body_root, up=tuple(ct))
for sgn in (-1, 1):
    if CHEST_PLATE:
        shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.8, cmid - cd * (cr + 0.25) + cside * sgn * 0.4,
              cside * sgn * 0.6 - ct * 1.0, mat=M_GOLD, parent=body_root)
    if PAULDRONS:
        wedge(f"Body_Pauldron_{sgn}", (0.85, 1.0, 0.45), cmid + cside * sgn * (cr + 0.1) + cd * 0.35, CR @ Euler((0, math.radians(sgn * 25), 0)).to_matrix(),
              M_GOLD, body_root, top_x=0.75, top_y=0.8, bevel=0)
        shard(f"Body_PauldronSpike_{sgn}", 0.22, 0.1, 0.7, cmid + cside * sgn * (cr + 0.3) + cd * 0.6,
              cside * sgn * 0.7 + cd * 0.8, mat=M_GOLD, parent=body_root)
    for k in range(SHOULDER_FINS):
        shard(f"Body_ShoulderFin_{sgn}_{k}", 0.4 - k * 0.06, 0.06, 1.3 - k * 0.25,
              cmid + cside * sgn * (cr + 0.1) + cd * (0.1 - k * 0.1), cside * sgn * 0.7 + ct * 0.9 + cd * 0.4,
              mat=M_FIN if k % 2 == 0 else M_FIN2, parent=wings_root)

# Aura derrière la tête : double anneau cyan, pointes en couronne, petites runes
if AURA_N:
    ac = (0, 2.2, 0.15)
    ring("Head_AuraRing", AURA_R, 0.2, 0.1, ac, (0, 1, 0), M_GLOW, H, sides=16)
    ring("Head_AuraInner", AURA_R * 0.78, 0.07, 0.06, (0, 2.0, 0.15), (0, 1, 0), M_GOLD, H, sides=16)
    for k in range(AURA_N):
        a = k / AURA_N * 2 * math.pi
        rad = Vector((math.sin(a), 0, math.cos(a)))
        long_ = (k % 2 == 0)
        shard(f"Head_AuraShard_{k}", 0.3, 0.1, (0.95 if long_ else 0.55) * AURA_R / 2.6,
              Vector(ac) + rad * (AURA_R + 0.05), rad, mat=M_GLOW if long_ else M_GOLD, parent=H, up=(0, 1, 0))
    for k in range(AURA_N // 2):
        a = (k + 0.5) / (AURA_N // 2) * 2 * math.pi
        rad = Vector((math.sin(a), 0, math.cos(a)))
        rune(f"Head_AuraRune_{k}", Vector(ac) + rad * AURA_R * 0.89 + Vector((0, -0.07, 0)), rad.cross(Vector((0, 1, 0))), rad, (0, -1, 0), 0.13, H, k, th=0.05)

if ADD_FLOATING_FX:
    lo = Vector([min(p[j] for p in CTRL) for j in range(3)])
    hi = Vector([max(p[j] for p in CTRL) for j in range(3)])
    for k in range(FX_COUNT):
        p = Vector((random.uniform(-3.0, 3.0), random.uniform(lo.y - 2.0, hi.y + 1.0),
                    random.uniform(max(1.0, lo.z - 0.5), HEAD_POS.z + 1.8)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 3 == 0:
            crystal(f"FX_Drop_{k}", 0.09 * FX_K, 0.14 * FX_K, 0.16 * FX_K, p, dirv, mat=M_FIN, parent=master)
        else:
            crystal(f"FX_Crystal_{k}", 0.08 * FX_K, 0.12 * FX_K, 0.14 * FX_K, p, dirv, mat=M_GLOW, parent=master)
    for k in range(FX_RINGS):
        p = Vector((random.uniform(-2.5, 2.5), random.uniform(lo.y - 1.0, hi.y), random.uniform(max(1.5, lo.z), HEAD_POS.z + 1.0)))
        ring(f"FX_Ring_{k}", random.uniform(0.35, 0.55) * FX_K, 0.07, 0.05, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
             M_GLOW if k % 2 == 0 else M_GOLD, master, sides=8)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
