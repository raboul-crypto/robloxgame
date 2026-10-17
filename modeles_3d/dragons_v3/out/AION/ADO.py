import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Aïon · Ado
#  Mythe · Ténèbres · Oriental · monde 5
#  - Corps long en S, tête plus fine, crocs, cornes ramifiées dorées à mi-taille, couronne d'or
#  - Motifs dorés plus nombreux, constellations émissives sur les flancs, crinière en deux rangées
#  - Halo cosmique plus grand, deux anneaux runiques, FX d'étoiles et de sabliers
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(5005)            # même dragon à chaque exécution
TAG = "AION_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
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
# RÉGLAGES DU STADE (seul bloc qui change entre Bébé, Ado et Adulte)
#  Unités de construction : tête d'environ 1.5 m de large ; finalize() remet ensuite le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
BODY_K, RK, SEG_STEP = 0.78, 0.92, 0.6
SNOUT_L, GEM_K, BABY_EYES, BROW_ANGLE, FANGS = 1.3, 1.1, False, 11, 2
CROWN, EAR_K, EAR_RAYS = 1, 0.85, 4
ANTLER_K, ANTLER_TINES, WHISKER_K, BEARD_N = 0.8, 4, 0.85, 5
MANE_RINGS, MANE_COUNT, MANE_K, NECK_MANE_S = 3, 17, 0.9, 0.35
MOTIF_RANGE, MOTIF_EVERY, FLANK_BANDS = (0.1, 0.94), 5, True
CONST_EVERY, CONST_RANGE, BAND_EVERY, SPIKE_ROWS, CREST_H = 5, (0.1, 0.92), 9, True, 0.6
CHEST, PAULD, LEG_K, LEG_RUNES = True, 1, 1.0, True
TAIL_K, TAIL_FAN_N, TAIL_FAN_L, TAIL_PETALS, TAIL_RING = 0.85, 7, 2.2, 5, True
HALO_N, HALO_R, HALO_RINGS = 14, 2.8, 3
ORBIT_S, ORBIT_TICKS = [0.3, 0.55], 8
FX_COUNT, FX_RINGS, FX_HOUR, FX_K = 12, 3, 2, 1.5

# Colonne vertébrale en S (points de contrôle Catmull-Rom, taille adulte) ; BODY_K la raccourcit pour Bébé et Ado
CTRL_ADULT = [
    (0.0, -0.3, 9.0),   # sous le crâne
    (0.0,  0.3, 8.2),
    (0.2,  1.0, 7.0),   # cou
    (0.5,  1.7, 5.6),
    (0.3,  2.8, 4.3),   # poitrail
    (-0.1, 4.4, 3.4),
    (-0.6, 6.2, 3.3),
    (-0.7, 8.0, 4.4),   # dos qui monte
    (-0.2, 9.8, 5.2),
    (0.4, 11.4, 4.4),
    (0.8, 12.8, 3.1),   # creux
    (0.5, 14.2, 2.6),
    (-0.1, 15.5, 3.4),  # la queue remonte
    (-0.6, 16.8, 4.9),
    (-0.5, 17.8, 6.4),  # bout de queue qui se redresse
]
CTRL = [(x * BODY_K, y * BODY_K, z * BODY_K) for x, y, z in CTRL_ADULT]
HEAD_POS = Vector(CTRL[0]) + Vector((0, -0.1, 0.2))      # base du crâne (HEAD_ROOT)
HEAD_TILT = 5                         # inclinaison de la tête vers l'avant (degrés)
RADIUS_KEYS = [(0.0, 0.62 * RK), (0.06, 0.72 * RK), (0.2, 0.86 * RK), (0.35, 1.0 * RK), (0.55, 0.92 * RK),
               (0.75, 0.62 * RK), (0.9, 0.38 * RK), (1.0, 0.24 * RK)]
SEG_BEVEL  = 0.06                     # biseau des segments
TAIL_START = 0.62                     # à partir de s = 0.62, les segments vont dans TAIL_ROOT

# ----------------------------------------------------------
# 7. PALETTE (identique aux 3 stades) : violet nuit, or ancien métallique, étoiles et runes émissives
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      "#4A2B8C", 0.42)                     # corps, crâne, pattes
M_DARK   = get_mat("ScaleDark", "#2A1660", 0.45)                     # écailles du dos, narines, bouche
M_LIGHT  = get_mat("ScaleLight","#7448C8", 0.40)                     # arête du museau, bandes des flancs
M_BELLY  = get_mat("Belly",     "#9467E8", 0.50)                     # plaques du ventre, menton
M_GOLD   = get_mat("Gold",      "#E8C35A", 0.26, 0.95)               # cornes, couronne, plastron, motifs anciens
M_GOLD2  = get_mat("GoldBright","#FFD45A", 0.22, 0.95)               # pointes, accents
M_MANE_V = get_mat("ManeViolet","#8A4DFF", 0.40)                     # crinière violette
M_MANE_D = get_mat("ManeDeep",  "#5A2FBF", 0.40)                     # crinière violet profond
M_GLOW   = get_mat("Glow",      "#FFD45A", 0.15, 0.0, emission="#FFD45A", strength=3.5)    # yeux, runes dorées lumineuses
M_VGLOW  = get_mat("VioletGlow","#B07CFF", 0.15, 0.0, emission="#A56BFF", strength=4.0)    # halo, gemmes, anneaux
M_STAR   = get_mat("Star",      "#F4EAFF", 0.10, 0.0, emission="#EBDDFF", strength=6.0)    # étoiles des constellations
M_LINE   = get_mat("StarLine",  "#9A6BFF", 0.20, 0.0, emission="#8D5CFF", strength=3.0)    # traits des constellations
M_WHITE  = get_mat("EyeWhite",  "#F2F2F2", 0.30)                     # yeux, crocs
M_BLACK  = get_mat("Black",     "#0A0612", 0.20)                     # pupilles, narines
M_CLAW   = get_mat("Claw",      "#F2E6B8", 0.30, 0.8)                # griffes or pâle

def mane_mat():
    """Éclats de crinière : violet vif, violet profond et or."""
    return pick([M_MANE_V, M_MANE_D, M_GOLD], [4, 3, 3])

GLYPHS = [
    [((0, -1), (0, 1)), ((0, 0.1), (0.8, 0.7))],
    [((-0.7, -0.9), (0.7, -0.9)), ((0, -0.9), (0, 1))],
    [((-0.6, 1), (0, -1)), ((0, -1), (0.6, 1))],
    [((-0.7, 0), (0.7, 0)), ((0, -0.8), (0, 0.8)), ((-0.5, -0.5), (0.5, 0.5))],
]

def rune(name, c, t, d, nrm, size, parent, kind, mat=None, th=0.075):
    """Rune ancienne : 2 ou 3 traits posés sur une surface."""
    mat = mat or M_GOLD
    for k, (a, b) in enumerate(GLYPHS[kind % len(GLYPHS)]):
        pa = c + t * a[0] * size + d * a[1] * size
        pb = c + t * b[0] * size + d * b[1] * size
        link(f"{name}_{k}", pa, pb, th, mat, parent, up=tuple(nrm), extra=th * 0.6, bevel=0)

def hourglass(name, c, t, d, nrm, size, parent, mat=None):
    """Sablier doré : deux triangles pointe contre pointe, barres en haut et en bas."""
    mat = mat or M_GOLD
    w, h = size * 0.7, size
    p = lambda x, y: c + t * x + d * y
    plate(f"{name}_Top", [p(-w, h), p(w, h), p(0, 0)], 0.07, mat, parent)
    plate(f"{name}_Bot", [p(0, 0), p(w, -h), p(-w, -h)], 0.07, mat, parent)
    link(f"{name}_BarT", p(-w * 1.15, h), p(w * 1.15, h), 0.09, mat, parent, up=tuple(nrm), extra=0.04, bevel=0)
    link(f"{name}_BarB", p(-w * 1.15, -h), p(w * 1.15, -h), 0.09, mat, parent, up=tuple(nrm), extra=0.04, bevel=0)

# ----------------------------------------------------------
# 8. HIÉRARCHIE
# ----------------------------------------------------------
master     = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root  = empty("BODY_ROOT", master)
legs_root  = empty("LEGS_ROOT", master)
tail_root  = empty("TAIL_ROOT", master)
head_root  = empty("HEAD_ROOT", master,
                   Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_TILT), 0, 0)).to_matrix().to_4x4())
H = head_root

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT)
# ----------------------------------------------------------
sk = SNOUT_L / 1.55
wedge("Head_Skull",     (1.5, 1.55, 1.35), (0, 0, 0), mat=M_BODY, parent=H, top_x=0.86, top_y=0.92, bevel=0.07)
box("Head_Snout",       (1.1, SNOUT_L, 0.72), (0, -0.62 - SNOUT_L / 2, -0.15), mat=M_BODY, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.78, 1.2 * sk, 0.2), (0, -0.65 - 0.6 * sk, 0.28), rot=(-6, 0, 0), mat=M_LIGHT, parent=H, bevel=0)
box("Head_NosePad",     (1.15, 0.3, 0.55), (0, -0.55 - SNOUT_L, -0.12), mat=M_BODY, parent=H, bevel=0)
box("Head_Jaw",         (1.0, 1.45 * sk, 0.32), (0, -0.53 - 0.72 * sk, -0.68), mat=M_BELLY, parent=H, bevel=0)
box("Head_MouthLine",   (1.04, 1.4 * sk, 0.06), (0, -0.58 - 0.7 * sk, -0.52), mat=M_DARK, parent=H, bevel=0)
# Bande dorée sur l'arête du museau (motif ancien)
box("Head_SnoutGold",   (0.2, 0.9 * sk, 0.06), (0, -0.62 - 0.55 * sk, 0.4), rot=(-6, 0, 0), mat=M_GOLD, parent=H, bevel=0)

# Joyau frontal violet dans un cadre d'or, et couronne (Ado : petite, Adulte : complète)
box("Head_GemSocket", (0.62, 0.45, 0.16), (0, -0.6, 0.66), rot=(-20, 0, 0), mat=M_GOLD, parent=H, bevel=0)
crystal("Head_Gem", 0.2 * GEM_K, 0.14, 0.24 * GEM_K, (0, -0.76, 0.68), (0, -0.45, 1), mat=M_VGLOW, parent=H)
if CROWN >= 1:
    box("Head_CrownBand", (1.25, 0.2, 0.14), (0, -0.2, 0.7), rot=(-8, 0, 0), mat=M_GOLD, parent=H, bevel=0)
    shard("Head_CrownSpike_C", 0.34, 0.1, 0.5 + 0.5 * CROWN, (0, -0.35, 0.72), (0, 0.15, 1), mat=M_GOLD2, parent=H)
for sgn in (-1, 1):
    if CROWN >= 1:
        shard(f"Head_CrownSpike_{sgn}", 0.28, 0.1, 0.4 + 0.35 * CROWN, (sgn * 0.38, -0.3, 0.7), (sgn * 0.35, 0.25, 1), mat=M_GOLD, parent=H)
        shard(f"Head_CrownWing_{sgn}", 0.24, 0.1, 0.35 + 0.25 * CROWN, (sgn * 0.66, -0.15, 0.66), (sgn * 1, 0.3, 0.55), mat=M_GOLD, parent=H)
    if CROWN >= 2:
        shard(f"Head_CrownSpike2_{sgn}", 0.24, 0.1, 1.1, (sgn * 0.2, -0.3, 0.72), (sgn * 0.12, 0.2, 1), mat=M_GOLD2, parent=H)
        shard(f"Head_CrownWing2_{sgn}", 0.2, 0.1, 0.7, (sgn * 0.82, -0.05, 0.55), (sgn * 1, 0.35, 0.3), mat=M_GOLD2, parent=H)
        crystal(f"Head_CrownGem_{sgn}", 0.09, 0.08, 0.13, (sgn * 0.52, -0.38, 0.8), (0, -0.3, 1), mat=M_VGLOW, parent=H)

for sgn in (-1, 1):
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -0.72 - SNOUT_L, 0.0), mat=M_BLACK, parent=H, bevel=0)
    if BABY_EYES:
        # Très grands yeux : blanc, grand iris or lumineux, pupille ronde, petit reflet blanc
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.62, 0.58), (sgn * 0.76, -0.3, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.44, 0.48), (sgn * 0.80, -0.33, 0.1), mat=M_GLOW, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.26, 0.32), (sgn * 0.83, -0.35, 0.08), mat=M_BLACK, parent=H, bevel=0)
        box(f"Head_Shine_{sgn}",    (0.04, 0.1, 0.1), (sgn * 0.855, -0.42, 0.18), mat=M_WHITE, parent=H, bevel=0)
    else:
        # Œil en amande : blanc, iris or lumineux, pupille fendue
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.45, 0.36), (sgn * 0.76, -0.35, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.28, 0.30), (sgn * 0.80, -0.38, 0.12), mat=M_GLOW, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.07, 0.26), (sgn * 0.83, -0.38, 0.12), mat=M_BLACK, parent=H, bevel=0)
    box(f"Head_Brow_{sgn}", (0.33, 0.7, 0.2), (sgn * 0.72, -0.4, 0.44 + (0.08 if BABY_EYES else 0)),
        rot=(BROW_ANGLE, 0, sgn * -8), mat=M_GOLD, parent=H, bevel=0)

    # Crocs
    for j in range(FANGS):
        fy = -0.8 - SNOUT_L * (0.18 + 0.27 * j)
        shard(f"Head_Fang_{sgn}_{j}", 0.13, 0.1, 0.42 - 0.07 * j, (sgn * 0.5, fy, -0.5), (0, 0, -1), mat=M_WHITE, parent=H, up=(0, 1, 0))

    # Oreilles : éventail d'éclats violets bordés d'or
    ek = EAR_K
    for j in range(EAR_RAYS):
        a = math.radians(-20 + j * 150 / max(1, EAR_RAYS - 1))
        dv = Vector((sgn * math.cos(a) * 0.8, 0.55, math.sin(a)))
        shard(f"Head_Ear_{sgn}_{j}", 0.3 * ek, 0.07, (1.2 + 0.5 * math.sin(a * 1.5)) * ek,
              (sgn * 0.7, 0.3, 0.2), dv, mat=M_MANE_V if j % 2 == 0 else M_GOLD, parent=H, up=(0, 1, 0))
    # Pointes de joue
    for j in range(2):
        shard(f"Head_Cheek_{sgn}_{j}", 0.26, 0.08, (0.9 - 0.2 * j) * ek, (sgn * 0.7, -0.35 + j * 0.4, -0.4),
              (sgn * 1, 0.7 + j * 0.4, -0.6), mat=M_GOLD if j == 0 else M_MANE_D, parent=H, up=(0, 1, 0))

    # Cornes dorées ramifiées
    a0 = Vector((sgn * 0.45, 0.35, 0.65))
    def ap(x, y, z):
        return a0 + (Vector((sgn * x, y, z)) - a0) * ANTLER_K
    a1, a2, a3 = ap(0.9, 0.9, 1.8), ap(1.3, 1.7, 2.9), ap(1.3, 2.5, 3.8)
    th = 0.32 * max(0.8, ANTLER_K)
    chain(f"Head_Antler_{sgn}", [a0, a1, a2, a3], th, th * 0.55, M_GOLD, H, bevel=0.02)
    tines = [(a1, ap(1.3, 0.3, 2.9), 0.18), (a2, ap(2.0, 1.4, 3.8), 0.17), (a2.lerp(a3, 0.4), ap(0.9, 2.2, 4.2), 0.15),
             (a3, ap(1.8, 3.1, 4.4), 0.13), (a1.lerp(a2, 0.5), ap(0.4, 1.8, 3.3), 0.13), (a3, ap(1.0, 3.2, 4.9), 0.12)]
    for k, (p, q, tk) in enumerate(tines[:ANTLER_TINES]):
        link(f"Head_AntlerTine{k + 1}_{sgn}", p, q, tk * max(0.8, ANTLER_K), M_GOLD2 if k % 2 else M_GOLD, H, bevel=0)

    # Longues moustaches dorées qui flottent vers l'arrière
    wb = Vector((sgn * 0.58, -0.4 - SNOUT_L, -0.05))
    wpts = [wb] + [wb + (Vector(p) - Vector((sgn * 0.58, -1.95, -0.05))) * WHISKER_K
                   for p in [(sgn * 1.3, -1.6, -0.45), (sgn * 2.0, -0.8, -0.9), (sgn * 2.5, 0.2, -1.1), (sgn * 3.0, 1.2, -0.8)]]
    chain(f"Head_Whisker_{sgn}", wpts, 0.10, 0.07, M_GOLD, H, bevel=0)

# Barbe d'éclats sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, (0.7 + random.random() * 0.3) * MANE_K,
          (x, -0.3 - 0.6 * sk + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=M_MANE_V if k % 2 == 0 else M_GOLD, parent=H)

# Crinière immense violette et dorée en éventail derrière la tête
for rg in range(MANE_RINGS):
    for k in range(MANE_COUNT):
        ang = math.radians(-165 + k * (330 / (MANE_COUNT - 1)) + rg * 8)
        radial = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (radial.x * 0.6, 0.4 + rg * 0.3, radial.z * 0.55 - 0.05)
        jitter = Vector((random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.2), random.uniform(-0.2, 0.2)))
        direction = radial * (1.1 - rg * 0.2) + Vector((0, 1.0, 0)) + jitter
        shard(f"Head_Mane_{rg}_{k}", (1.0 - rg * 0.08) * max(0.8, MANE_K), 0.16,
              (1.3 + rg * 0.35 + random.random() * 0.6) * MANE_K,
              loc, direction, mat=mane_mat(), parent=H, up=tuple(radial.cross(Vector((0, 1, 0)))))

# ----------------------------------------------------------
# 10. CORPS EN S : segments, ventre, flancs, motifs dorés, constellations, crête
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

# Motif de constellation : 5 étoiles reliées (coordonnées 2D dans le plan tangente / dos du flanc)
CONST_PATTERNS = [
    [(-0.8, 0.2), (-0.3, 0.7), (0.2, 0.25), (0.7, 0.65), (0.55, -0.3)],
    [(-0.7, -0.4), (-0.2, 0.1), (0.3, -0.2), (0.75, 0.35), (0.1, 0.7)],
    [(-0.6, 0.5), (0.0, 0.65), (0.5, 0.2), (0.15, -0.35), (-0.55, -0.2)],
]

def constellation(name, c, t, d, nrm, size, parent, pat, rot):
    ca, sa = math.cos(rot), math.sin(rot)
    pts = [c + t * (x * ca - y * sa) * size + d * (x * sa + y * ca) * size for x, y in pat]
    for k in range(len(pts) - 1):
        link(f"{name}_L{k}", pts[k], pts[k + 1], 0.045, M_LINE, parent, up=tuple(nrm), extra=0.03, bevel=0)
    for k, p in enumerate(pts):
        crystal(f"{name}_S{k}", 0.07 + 0.03 * (k % 2), 0.08, 0.11 + 0.03 * (k % 2), p + nrm * 0.03, nrm, mat=M_STAR, parent=parent)

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

    # Plaques de ventre violettes (bien séparées) + bandes claires sur les flancs
    if s < 0.9:
        box(f"{tag}_Belly_{i}", (2 * r * 0.84, L * 0.85, 0.2), mid - d * (r * 0.95), R, M_BELLY, parent, bevel=0)
    if s < 0.88 and FLANK_BANDS:
        for sgn in (-1, 1):
            box(f"{tag}_Flank_{i}_{sgn}", (0.08, L * 0.9, r * 0.45), mid + side * sgn * r - d * r * 0.6,
                R, M_LIGHT, parent, bevel=0)

    # Écaille dorsale sombre légèrement inclinée
    Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
    box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.18), mid + d * (r * 0.95), Rtilt, M_DARK, parent, bevel=0)

    # Motifs dorés anciens (runes et sabliers) sur les flancs, en alternance
    if MOTIF_RANGE[0] < s < MOTIF_RANGE[1]:
        for sgn in (-1, 1):
            c = mid + side * sgn * (r + 0.03) - d * r * 0.1
            sz = min(r * 0.42, 0.5)
            if i % MOTIF_EVERY == 0:
                hourglass(f"{tag}_Hour_{i}_{sgn}", c, t, d, side * sgn, sz, parent)
            elif i % MOTIF_EVERY == MOTIF_EVERY // 2:
                rune(f"{tag}_Rune_{i}_{sgn}", c, t, d, side * sgn, sz, parent, i + (sgn > 0))

    # Constellations émissives sur le haut des flancs
    if CONST_EVERY and CONST_RANGE[0] < s < CONST_RANGE[1] and i % CONST_EVERY == CONST_EVERY // 2:
        for sgn in (-1, 1):
            c = mid + side * sgn * (r + 0.04) + d * r * 0.45
            constellation(f"{tag}_Const_{i}_{sgn}", c, t, d, side * sgn, min(r * 0.55, 0.6), parent,
                          CONST_PATTERNS[(i + (sgn > 0)) % 3], random.uniform(-0.5, 0.5))

    # Bandes d'or autour du corps
    if BAND_EVERY and i % BAND_EVERY == BAND_EVERY // 2 and 0.08 < s < 0.9:
        ring(f"{tag}_Band_{i}", r * 1.06, 0.16, 0.3, mid, t, M_GOLD, parent, sides=8, up=tuple(d))

    # Double rangée de pics dorés sur le dos
    if SPIKE_ROWS and i % 2 == 0 and 0.08 < s < 0.94:
        for sgn in (-1, 1):
            shard(f"{tag}_Spike_{i}_{sgn}", 0.2 + 0.1 * r, 0.1, 0.35 + r * 0.55,
                  mid + d * r * 0.9 + side * sgn * r * 0.4, d + side * sgn * 0.5 + t * 0.4, mat=M_GOLD2, parent=parent)

    # Crête de losanges violets et or tout le long du dos
    if CREST_H and 0.02 < s < 0.97:
        h = CREST_H * (0.5 + r)
        b = mid + d * r * 0.9
        plate(f"{tag}_Crest_{i}", [b - t * L * 0.55, b + t * L * 0.1 + d * h, b + t * L * 0.55 - d * 0.0 + d * h * 0.35, b + t * L * 0.55],
              0.06, M_MANE_V if i % 2 == 0 else M_MANE_D, parent)

# Crinière du cou : grands éclats violets et or le long de la nuque
for i in range(N):
    s = (i + 0.5) / N
    if s > NECK_MANE_S:
        break
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = frame(SPINE[i + 1] - SPINE[i])
    r = radius(s)
    for sgn in (-1, 1):
        for row in range(2):
            shard(f"Neck_Mane_{i}_{sgn}_{row}", 0.7, 0.1, (1.5 - 0.5 * row - 0.9 * s) * MANE_K,
                  mid + d * r * 0.8 + side * sgn * r * (0.25 + 0.35 * row),
                  d * 0.8 + side * sgn * (0.5 + 0.4 * row) + t * 0.7, mat=mane_mat(), parent=body_root, up=tuple(side))

# ----------------------------------------------------------
# 11. PATTES : épaule en bloc, avant-bras, bracelet doré, pied à 3 griffes
# ----------------------------------------------------------
LEG_FRONT = dict(s=0.2, upper=(0, -0.55, -0.75), lower=(0, -0.75, -0.25), th_up=0.48, th_low=0.38, push=0.35)
LEG_BACK  = dict(s=0.5, upper=(0, -0.7, -0.45),  lower=(0, 0.35, -0.8),   th_up=0.6,  th_low=0.42, push=0.30)

def paw(name, center):
    k_ = LEG_K
    box(f"{name}_Paw", (0.55 * k_, 0.55 * k_, 0.3 * k_), center, mat=M_BODY, parent=legs_root, bevel=0.04)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0)) * k_
        end = center + Vector((k * 0.24, -0.55, -0.2)) * k_
        link(f"{name}_Toe_{k}", base, end, 0.14 * k_, M_BODY, legs_root, bevel=0)
        shard(f"{name}_Claw_{k}", 0.12 * k_, 0.12 * k_, 0.28 * k_, end, (k * 0.2, -1, -0.9), mat=M_CLAW, parent=legs_root)

def leg(name, cfg):
    mid, t, d, side, r = frame_at(cfg["s"])
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.85 - d * 0.15
        joint = root + Vector((sgn * cfg["push"], 0, 0)) + Vector(cfg["upper"]) * LEG_K
        wrist = joint + Vector((sgn * 0.05, 0, 0)) + Vector(cfg["lower"]) * LEG_K
        wedge(f"{n}_Shoulder", (0.75 * LEG_K, 0.8 * LEG_K, 0.7 * LEG_K), root, mat=M_BODY, parent=legs_root,
              top_x=0.8, top_y=0.75, bevel=0.05)
        link(f"{n}_Upper", root, joint, cfg["th_up"] * LEG_K, M_BODY, legs_root, up=(1, 0, 0), bevel=0.04)
        link(f"{n}_Lower", joint, wrist, cfg["th_low"] * LEG_K, M_BODY, legs_root, up=(1, 0, 0), bevel=0)
        link(f"{n}_Cuff", joint.lerp(wrist, 0.62), wrist, (cfg["th_low"] + 0.14) * LEG_K, M_GOLD, legs_root, up=(1, 0, 0), bevel=0)
        if LEG_RUNES:
            link(f"{n}_CuffGem", joint.lerp(wrist, 0.3), joint.lerp(wrist, 0.4), (cfg["th_low"] + 0.1) * LEG_K, M_GOLD2, legs_root, up=(1, 0, 0), bevel=0)
            shard(f"{n}_ElbowSpike", 0.2 * LEG_K, 0.08, 0.7 * LEG_K, joint, (sgn * 0.8, 0.9, 0.2), mat=M_MANE_V, parent=legs_root)
        paw(n, wrist + Vector((0, -0.2, -0.12)) * LEG_K)

leg("Legs_Front", LEG_FRONT)
leg("Legs_Back", LEG_BACK)

# ----------------------------------------------------------
# 12. AILES : pas d'ailes (oriental). Les épaulières et la crinière tiennent lieu d'ornements (sections 10 et 14).
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : collier d'or, grand cristal, plumes violettes et dorées, anneau runique final
# ----------------------------------------------------------
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
box("Tail_TipCollar", (0.5 * TAIL_K, 0.4, 0.5 * TAIL_K), tip, seg_matrix(tt, td, tside), M_GOLD, tail_root, bevel=0)
crystal("Tail_TipCrystal", 0.24 * TAIL_K, 0.5 * TAIL_K, 0.6 * TAIL_K, tip + tt * 0.15, tt, mat=M_VGLOW, parent=tail_root, up=tuple(td))
for k in range(TAIL_FAN_N):
    a = math.radians(-80 + k * 160 / max(1, TAIL_FAN_N - 1))
    dv = tt * math.cos(a) + td * math.sin(a)
    Lk = TAIL_FAN_L * (1.0 - 0.35 * abs(a) / math.radians(80)) * (1.0 + 0.15 * random.random())
    shard(f"Tail_Feather_{k}", 0.55 * TAIL_K, 0.08, Lk, tip + tt * 0.1, dv,
          mat=M_MANE_V if k % 2 == 0 else M_GOLD, parent=tail_root, up=tuple(tside))
for k in range(TAIL_PETALS):
    a = k / TAIL_PETALS * 2 * math.pi
    sp = tside * math.cos(a) + td * math.sin(a)
    shard(f"Tail_Petal_{k}", 0.3 * TAIL_K, 0.1, 0.9 * TAIL_K, tip - tt * 0.05, tt + sp * 0.55, mat=M_GOLD2, parent=tail_root)
if TAIL_RING:
    ring("Tail_Ring", 1.0 * TAIL_K, 0.14, 0.08, tip + tt * 0.9 * TAIL_K, tt, M_VGLOW, tail_root, sides=12, up=tuple(td))
    hourglass("Tail_Hour", tip + tt * 0.9 * TAIL_K, tside, td, tt, 0.35 * TAIL_K, tail_root, M_GLOW)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (Mythe) : plastron, épaulières, halo cosmique, anneaux runiques, FX
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(0.2)
CR = seg_matrix(ct, cd, cside)
if CHEST:
    wedge("Body_ChestPlate", (2 * cr * 1.05, 1.5, 0.3), cmid - cd * (cr + 0.05), CR, M_GOLD, body_root, top_x=0.8, top_y=0.85, bevel=0)
    box("Body_ChestInner", (2 * cr * 0.65, 1.0, 0.14), cmid - cd * (cr + 0.22), CR, M_DARK, body_root, bevel=0)
    crystal("Body_ChestGem", 0.32, 0.22, 0.32, cmid - cd * (cr + 0.28), -cd, mat=M_VGLOW, parent=body_root, up=tuple(ct))
    hourglass("Body_ChestHour", cmid - cd * (cr + 0.26) - ct * 0.0, cside, ct, -cd, 0.35, body_root, M_GOLD2)
for sgn in (-1, 1):
    if CHEST:
        shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.8, cmid - cd * (cr + 0.25) + cside * sgn * 0.4,
              cside * sgn * 0.6 - ct * 1.0, mat=M_GOLD, parent=body_root)
    if PAULD:
        wedge(f"Body_Pauldron_{sgn}", (0.85, 1.0, 0.45), cmid + cside * sgn * (cr + 0.1) + cd * 0.35, CR @ Euler((0, math.radians(sgn * 25), 0)).to_matrix(),
              M_GOLD, body_root, top_x=0.75, top_y=0.8, bevel=0)
        for k in range(PAULD):
            shard(f"Body_PauldronSpike_{sgn}_{k}", 0.22, 0.1, 0.8 - 0.15 * k, cmid + cside * sgn * (cr + 0.3) + cd * (0.6 - 0.25 * k) + ct * 0.2 * k,
                  cside * sgn * 0.7 + cd * (0.8 - 0.4 * k) + ct * 0.5 * k, mat=M_GOLD2, parent=body_root)

# Halo cosmique derrière la tête : anneaux violet / or, pointes, étoiles, runes
if HALO_N:
    ac = (0, 2.3, 0.15)
    ring("Head_HaloRing", HALO_R, 0.32, 0.12, ac, (0, 1, 0), M_VGLOW, H, sides=18)
    ring("Head_HaloGold", HALO_R * 0.8, 0.14, 0.1, (0, 2.1, 0.15), (0, 1, 0), M_GOLD, H, sides=18)
    if HALO_RINGS >= 3:
        ring("Head_HaloOuter", HALO_R * 1.22, 0.07, 0.06, (0, 2.5, 0.15), (0, 1, 0), M_STAR, H, sides=18)
        ring("Head_HaloCore", HALO_R * 0.58, 0.07, 0.06, (0, 1.9, 0.15), (0, 1, 0), M_GLOW, H, sides=14)
    for k in range(HALO_N):
        a = k / HALO_N * 2 * math.pi
        rad = Vector((math.sin(a), 0, math.cos(a)))
        long_ = (k % 2 == 0)
        shard(f"Head_HaloShard_{k}", 0.3, 0.1, (1.1 if long_ else 0.6) * HALO_R / 2.6,
              Vector(ac) + rad * (HALO_R + 0.05), rad, mat=M_VGLOW if long_ else M_GOLD, parent=H, up=(0, 1, 0))
        if HALO_RINGS >= 3 and k % 2 == 1:
            crystal(f"Head_HaloStar_{k}", 0.1, 0.1, 0.14, Vector(ac) + rad * HALO_R * 1.22 + Vector((0, 0.1, 0)), (0, -1, 0), mat=M_STAR, parent=H)
    for k in range(HALO_N // 2):
        a = (k + 0.5) / (HALO_N // 2) * 2 * math.pi
        rad = Vector((math.sin(a), 0, math.cos(a)))
        rune(f"Head_HaloRune_{k}", Vector(ac) + rad * HALO_R * 0.9 + Vector((0, -0.08, 0)), rad.cross(Vector((0, 1, 0))), rad, (0, -1, 0), 0.14, H, k, mat=M_GLOW, th=0.05)

# Anneaux runiques flottants autour du corps (cerceaux inclinés avec runes en relief)
for k, s_ in enumerate(ORBIT_S):
    omid, ot, od, oside, orad = frame_at(s_)
    R_ = orad * 1.9 + 0.5
    tilt = Vector((0.18 * (-1) ** k, 0, 0.12))
    axis = (ot + tilt).normalized()
    ring(f"Orbit_Ring_{k}", R_, 0.26, 0.14, omid + od * 0.0, axis, M_GOLD if k % 2 == 0 else M_VGLOW, master, sides=18, up=tuple(od))
    ring(f"Orbit_Inner_{k}", R_ * 0.9, 0.08, 0.07, omid, axis, M_STAR, master, sides=14, up=tuple(od))
    ax_x = axis.cross(Vector((0, 0, 1))).normalized()
    ax_y = axis.cross(ax_x).normalized()
    for j in range(ORBIT_TICKS):
        a = j / ORBIT_TICKS * 2 * math.pi
        rad = ax_x * math.cos(a) + ax_y * math.sin(a)
        if j % 2 == 0:
            rune(f"Orbit_Rune_{k}_{j}", omid + rad * (R_ + 0.12), axis, rad, rad.cross(axis), 0.2, master, k + j, mat=M_GLOW, th=0.06)
        else:
            crystal(f"Orbit_Star_{k}_{j}", 0.1, 0.1, 0.16, omid + rad * (R_ + 0.1), rad, mat=M_STAR, parent=master)

if ADD_FLOATING_FX:
    lo = Vector([min(p[j] for p in CTRL) for j in range(3)])
    hi = Vector([max(p[j] for p in CTRL) for j in range(3)])
    for k in range(FX_COUNT):
        p = Vector((random.uniform(-3.5 * BODY_K - 1, 3.5 * BODY_K + 1), random.uniform(lo.y - 2.0, hi.y + 1.0),
                    random.uniform(max(1.0, lo.z - 0.5), HEAD_POS.z + 2.0)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        m = [M_STAR, M_VGLOW, M_GLOW][k % 3]
        crystal(f"FX_Star_{k}", 0.08 * FX_K, 0.12 * FX_K, 0.18 * FX_K, p, dirv, mat=m, parent=master)
    for k in range(FX_RINGS):
        p = Vector((random.uniform(-2.5, 2.5), random.uniform(lo.y - 1.0, hi.y), random.uniform(max(1.5, lo.z), HEAD_POS.z + 1.0)))
        ring(f"FX_Ring_{k}", random.uniform(0.35, 0.55) * FX_K, 0.07, 0.05, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
             M_VGLOW if k % 2 == 0 else M_GOLD, master, sides=8)
    for k in range(FX_HOUR):
        p = Vector((random.uniform(-3, 3), random.uniform(lo.y, hi.y), random.uniform(max(1.5, lo.z), HEAD_POS.z + 1.5)))
        hourglass(f"FX_Hour_{k}", p, Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), 0.3 * FX_K, master, M_GLOW)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
