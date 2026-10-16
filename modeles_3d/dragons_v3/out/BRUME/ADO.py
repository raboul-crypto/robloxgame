import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Brume · Ado
#  Légendaire · Ténèbres · Oriental · monde 4
#  - Ado oriental de brume qui flotte en S : violet sombre, ventre lilas en plaques, veines lavande lumineuses sur les flancs
#  - Crinière, moustaches et queue en brume violette translucide (alpha) ; la queue commence à se dissoudre
#  - Cornes noires droites aux arêtes vives (2 anneaux d'argent), yeux lavande lumineux en amande, petits crocs
#  - Rendu Légendaire à mi-puissance : lune d'argent sur le front, petit plastron, épaulières, collier d'argent, une rangée de pics noirs
#  - Petit croissant d'aura derrière la tête, ornement d'argent au bout de la queue, FX de brume
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4417)            # même dragon à chaque exécution
TAG = "BRUME_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 10000          # budget de triangles de ce stade et de cette rareté
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
HEAD_POS   = Vector((0, -0.4, 4.9))   # base du crâne (HEAD_ROOT)
HEAD_TILT  = 4                        # inclinaison de la tête vers l'avant (degrés)
HEAD_S     = 1.15                     # taille de la tête (1 = 1.5 m de large)
SNOUT_L    = 1.3                      # longueur du museau
BABY_EYES  = False                    # True = grands yeux ronds avec reflet (bébé)
BROW_ANGLE = 8                        # sourcils : plus l'angle est grand, plus le regard est sévère
BROW_SILVER = False                   # sourcils d'argent (sinon brume)
FANGS      = 1                        # crocs fins par côté
CIRCLET, CIRCLET_K = True, 0.8        # lune d'argent sur le front : présence, taille
EAR_K, EAR_FAN = 0.8, False            # oreilles : taille, nageoire de brume
HORN_K     = 0.7                      # taille des cornes noires (1 = pleine taille)
HORN_RINGS = 2                        # anneaux d'argent sur chaque corne (0 à 3)
HORN2      = False                    # petite corne basse
WHISKER_K  = 0.7                      # longueur des moustaches de brume
BEARD_N    = 3                        # brins de barbe
MANE_RINGS, MANE_COUNT, MANE_K, MANE_LINK = 2, 9, 0.8, 3   # crinière de tête : rangées, brins par rangée, taille, éclats par brin

# Colonne vertébrale en S : points de contrôle (Catmull-Rom) et rayon le long du corps (s de 0 à 1)
CTRL = [
    (0.0, -0.3, 4.8),   # sous le crâne
    (0.0,  0.4, 4.5),
    (0.2,  1.2, 3.8),   # cou
    (0.3,  2.2, 3.1),
    (0.1,  3.4, 2.9),   # poitrail
    (-0.2, 4.6, 3.4),
    (-0.3, 5.8, 3.8),   # dos qui monte
    (0.0,  7.0, 3.4),
    (0.4,  8.2, 2.7),   # creux
    (0.5,  9.4, 2.6),
    (0.2, 10.6, 3.1),   # queue qui remonte
    (-0.3, 11.8, 3.8),
    (-0.4, 12.8, 4.0),  # bout de queue
]
RADIUS_KEYS = [(0.0, 0.5), (0.06, 0.58), (0.2, 0.7), (0.35, 0.82), (0.55, 0.72), (0.75, 0.46), (0.9, 0.26), (1.0, 0.14)]
SEG_STEP   = 0.5                      # longueur d'un segment du corps
SEG_BEVEL  = 0.06                     # biseau des segments
TAIL_START = 0.6                      # à partir de s = 0.6, les segments vont dans TAIL_ROOT
MIST_START = 0.8                      # à partir de s = 0.74, la queue devient brume translucide
GLOW_VEINS = True                     # veines lavande lumineuses sur les flancs
SPIKE_ROWS = 1                        # pics noirs sur le dos : 0 = aucun, 1 = une rangée, 2 = double rangée
BAND_EVERY = 0                        # anneaux d'argent autour du corps (0 = aucun)
RIBBON_EVERY, RIBBON_RANGE = 3, (0.03, 0.6)   # brins de crinière le long du dos : un tous les N segments, zone
TAIL_PLUME_N, TAIL_K, TAIL_ORNAMENT = 5, 0.8, True   # panache de queue : brins, taille, ornement d'argent

# Rendu de rareté (Légendaire)
CHEST_PLATE = True                    # plastron d'argent avec gemme lavande
CHEST_S = 0.2                         # position du plastron et des épaulières sur le corps
PAULDRONS = True                      # épaulières d'argent
COLLAR, COLLAR_S = True, 0.07         # collier d'argent au cou : présence, position
SHOULDER_FINS = 1                     # éclats de brume par épaule
AURA_N, AURA_R = 9, 1.9              # croissant d'aura : pointes et rayon (0 = aucune)
FX_COUNT, FX_RINGS, FX_K = 10, 2, 1.2 # FX flottants : brins/cristaux, anneaux, taille

# Pattes
GROUNDED = False
LEG_WEDGE = True                      # True = épaule en bloc biseauté
LEG_FIN_RAYS = 2                      # rayons de l'aileron de coude (0 = aucun)
LEG_FRONT = dict(s=0.2, upper=(0, -0.45, -0.6), lower=(0, -0.6, -0.2), th_up=0.42, th_low=0.34, push=0.3)
LEG_BACK  = dict(s=0.5, upper=(0, -0.55, -0.4),  lower=(0, 0.3, -0.65),   th_up=0.5,  th_low=0.36, push=0.28)
LEG_K = 0.85                          # taille des épaules, pieds et griffes
PAL = dict(body="#432D75", scaleA="#31215A", scaleB="#634AA0", nostril="#171024")   # violets du stade

# ----------------------------------------------------------
# 7. PALETTE (mêmes teintes aux 3 stades, le violet s'assombrit un peu avec l'âge)
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      PAL["body"],  0.45)              # corps, crâne, pattes
M_SCALEA = get_mat("ScaleA",    PAL["scaleA"], 0.50)             # écailles du dos, narines claires
M_SCALEB = get_mat("ScaleB",    PAL["scaleB"], 0.45)             # arête du museau, flancs
M_NOSTRIL= get_mat("Nostril",   PAL["nostril"], 0.30)            # narines, ligne de bouche
M_BELLY  = get_mat("Belly",     "#B8A2D6", 0.50)                 # plaques du ventre, menton
M_HORN   = get_mat("Horn",      "#1A1622", 0.25)                 # cornes, pics, griffes (noir)
M_SILVER = get_mat("Silver",    "#D6DAEA", 0.22, 0.9)            # ornements d'argent (métal)
M_MIST   = get_mat("Mist",      "#8F6FC8", 0.40, 0.0, alpha=0.55)   # brume violette translucide
M_MIST2  = get_mat("MistLight", "#B8A2D6", 0.40, 0.0, alpha=0.50)   # brume claire translucide
M_MISTD  = get_mat("MistDark",  "#5E4496", 0.40, 0.0, alpha=0.62)   # brume sombre translucide
M_EYE    = get_mat("Eye",       "#CDB3FF", 0.15, 0.0, emission="#CDB3FF", strength=3.0)   # yeux, gemmes
M_GLOW   = get_mat("Glow",      "#A98BFF", 0.15, 0.0, emission="#A98BFF", strength=2.5)   # veines, cristaux, FX
M_WHITE  = get_mat("White",     "#F2F2F2", 0.30)                 # dents, yeux de bébé
M_BLACK  = get_mat("Black",     "#0A0A0A", 0.20)                 # pupilles

def mane_mat():
    """Brins de crinière : trois violets translucides."""
    return pick([M_MIST, M_MIST2, M_MISTD], [4, 3, 2])

def wisp(name, base, direction, length, width, mat, parent, curl=(0, 0, 0), n=3, up=(0, 0, 1)):
    """Brin de brume : n éclats plats bout à bout qui se courbent vers 'curl' (crinière, queue, moustaches)."""
    pos, dv = Vector(base), Vector(direction).normalized()
    seg = length / n
    for k in range(n):
        shard(f"{name}_{k}", width * (1.0 - 0.18 * k), 0.06, seg * 1.25, pos, dv, mat=mat, parent=parent, up=up)
        pos = pos + dv * seg * 0.9
        dv = (dv + Vector(curl) * (1.0 / n)).normalized()

def fin_fan(name, root, tips, parent, mat_ray=M_HORN, mat_memb=M_MIST, ray_t=0.06, memb_t=0.04):
    """Aileron de brume : rayons noirs qui partent de 'root' et membrane translucide entre eux."""
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
wings_root = empty("WINGS_ROOT", master)      # ailerons de brume (coudes, épaules)
head_root  = empty("HEAD_ROOT", master,
                   Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_TILT), 0, 0)).to_matrix().to_4x4() @ Matrix.Scale(HEAD_S, 4))
H = head_root

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT)
# ----------------------------------------------------------
sk = SNOUT_L / 1.55                  # facteur de longueur du museau
wedge("Head_Skull",     (1.5, 1.55, 1.35), (0, 0, 0), mat=M_BODY, parent=H, top_x=0.86, top_y=0.92, bevel=0.08 if BABY_EYES else 0.07)
box("Head_Snout",       (1.1, SNOUT_L, 0.72), (0, -0.62 - SNOUT_L / 2, -0.15), mat=M_BODY, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.78, 1.2 * sk, 0.2), (0, -0.65 - 0.6 * sk, 0.28), rot=(-6, 0, 0), mat=M_SCALEB, parent=H, bevel=0)
box("Head_NosePad",     (1.15, 0.3, 0.55), (0, -0.55 - SNOUT_L, -0.12), mat=M_BODY, parent=H, bevel=0)
box("Head_Jaw",         (1.0, 1.45 * sk, 0.32), (0, -0.53 - 0.72 * sk, -0.68), mat=M_BELLY, parent=H, bevel=0)
box("Head_MouthLine",   (1.04, 1.4 * sk, 0.06), (0, -0.58 - 0.7 * sk, -0.52), mat=M_NOSTRIL, parent=H, bevel=0)

# Front : lune d'argent (anneau) avec gemme lavande, et deux pointes d'argent en croissant
if CIRCLET:
    ring("Head_Moon", 0.36 * CIRCLET_K, 0.09 * CIRCLET_K, 0.08, (0, -0.72, 0.62), (0, -0.35, 1), M_SILVER, H, sides=10, up=(0, 0, 1))
    crystal("Head_MoonGem", 0.16 * CIRCLET_K, 0.1, 0.16 * CIRCLET_K, (0, -0.82, 0.64), (0, -0.4, 1), mat=M_EYE, parent=H)
    box("Head_CircletBand", (1.2, 0.16, 0.12), (0, -0.28, 0.66), rot=(-8, 0, 0), mat=M_SILVER, parent=H, bevel=0)
    for sgn in (-1, 1):
        shard(f"Head_MoonHorn_{sgn}", 0.2 * CIRCLET_K, 0.08, 0.8 * CIRCLET_K, (sgn * 0.5, -0.42, 0.72), (sgn * 0.5, 0.15, 1), mat=M_SILVER, parent=H)

for sgn in (-1, 1):
    # Narines
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -0.72 - SNOUT_L, 0.0), mat=M_NOSTRIL, parent=H, bevel=0)
    if BABY_EYES:
        # Grands yeux de bébé : blanc, grand iris lavande lumineux, pupille ronde, petit reflet blanc
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.62, 0.58), (sgn * 0.76, -0.3, 0.12), mat=M_WHITE, parent=H, bevel=0)
        box(f"Head_Iris_{sgn}",     (0.06, 0.46, 0.5), (sgn * 0.80, -0.33, 0.1), mat=M_EYE, parent=H, bevel=0)
        box(f"Head_Pupil_{sgn}",    (0.05, 0.26, 0.32), (sgn * 0.83, -0.35, 0.08), mat=M_BLACK, parent=H, bevel=0)
        box(f"Head_Shine_{sgn}",    (0.04, 0.1, 0.1), (sgn * 0.855, -0.42, 0.18), mat=M_WHITE, parent=H, bevel=0)
    else:
        # Œil en amande : iris lavande lumineux plus grand que chez les autres, pupille fendue
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.5, 0.34), (sgn * 0.76, -0.35, 0.12), mat=M_SCALEA, parent=H, bevel=0, rot=(0, 0, 0))
        box(f"Head_Iris_{sgn}",     (0.06, 0.4, 0.28), (sgn * 0.80, -0.36, 0.12), mat=M_EYE, parent=H, bevel=0, rot=(0, 0, sgn * -10))
        box(f"Head_Pupil_{sgn}",    (0.05, 0.07, 0.24), (sgn * 0.83, -0.37, 0.12), mat=M_BLACK, parent=H, bevel=0)
    # Sourcils d'argent (sévères chez l'adulte)
    box(f"Head_Brow_{sgn}", (0.33, 0.7, 0.18), (sgn * 0.72, -0.4, 0.44 + (0.08 if BABY_EYES else 0)),
        rot=(BROW_ANGLE, 0, sgn * -8), mat=M_SILVER if BROW_SILVER else M_MIST, parent=H, bevel=0)

    # Crocs fins
    for j in range(FANGS):
        fy = -0.8 - SNOUT_L * (0.18 + 0.27 * j)
        shard(f"Head_Fang_{sgn}_{j}", 0.12, 0.1, 0.4 - 0.07 * j, (sgn * 0.5, fy, -0.5), (0, 0, -1), mat=M_WHITE, parent=H, up=(0, 1, 0))

    # Oreilles : éclats noirs + nageoire de brume ; pointes de joue en brume
    shard(f"Head_Ear_{sgn}", 0.4 * EAR_K, 0.1, 1.0 * EAR_K, (sgn * 0.75, 0.3, 0.2), (sgn * 0.9, 1, 0.15), mat=M_SCALEA, parent=H)
    if EAR_FAN:
        fin_fan(f"Head_EarFan_{sgn}", (sgn * 0.75, 0.35, 0.05),
                [(sgn * 1.6, 1.1, 0.5), (sgn * 2.1, 1.3, 0.0), (sgn * 1.9, 1.2, -0.6)], H)
    shard(f"Head_Cheek1_{sgn}", 0.3, 0.1, 0.8, (sgn * 0.6, -0.6, -0.55), (sgn * 0.9, 0.8, -0.3), mat=M_MIST, parent=H)
    shard(f"Head_Cheek2_{sgn}", 0.3, 0.1, 0.9, (sgn * 0.55, -0.2, -0.6), (sgn * 0.7, 1, -0.6), mat=M_MISTD, parent=H)

    # Cornes noires aux arêtes vives : droites, couchées vers l'arrière, anneaux d'argent
    h0 = Vector((sgn * 0.45, 0.3, 0.62))
    def hp(x, y, z):
        return h0 + (Vector((sgn * x, y, z)) - h0) * HORN_K
    hpts = [h0, hp(0.6, 1.0, 1.0), hp(0.8, 2.0, 1.6), hp(0.95, 3.1, 2.1), hp(1.0, 4.1, 2.45)]
    th = 0.3 * max(0.8, HORN_K)
    chain(f"Head_Horn_{sgn}", hpts, th, th * 0.18, M_HORN, H, bevel=0)
    for k in range(min(HORN_RINGS, 3)):
        a, b = hpts[k + 1], hpts[k + 2]
        thk = th + (th * 0.18 - th) * ((k + 1) / (len(hpts) - 1))
        ring(f"Head_HornBand_{sgn}_{k}", thk * 0.78, 0.07, 0.14, a.lerp(b, 0.15), b - a, M_SILVER, H, sides=6)
    if HORN2:
        # petite corne secondaire qui part vers l'extérieur
        c0 = Vector((sgn * 0.7, 0.2, 0.2))
        chain(f"Head_HornLow_{sgn}", [c0, c0 + Vector((sgn * 0.6, 0.8, 0.25)) * HORN_K, c0 + Vector((sgn * 1.2, 1.7, 0.45)) * HORN_K],
              0.22, 0.05, M_HORN, H, bevel=0)

    # Moustaches de brume qui flottent vers l'arrière
    wb = Vector((sgn * 0.58, -0.4 - SNOUT_L, -0.05))
    wpts = [wb] + [wb + (Vector(p) - Vector((sgn * 0.58, -1.95, -0.05))) * WHISKER_K
                   for p in [(sgn * 1.3, -1.6, -0.45), (sgn * 2.0, -0.8, -0.9), (sgn * 2.5, 0.2, -1.1), (sgn * 3.0, 1.2, -0.8)]]
    chain(f"Head_Whisker_{sgn}", wpts, 0.12, 0.07, M_MIST2, H, bevel=0)
    if WHISKER_K > 0.8:
        crystal(f"Head_WhiskerGem_{sgn}", 0.09, 0.14, 0.14, wpts[-1] + Vector((sgn * 0.1, 0.1, 0)), (sgn * 0.3, 1, 0), mat=M_EYE, parent=H)

# Barbe de brume sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, (0.7 + random.random() * 0.3) * MANE_K,
          (x, -0.3 - 0.6 * sk + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=M_MIST2, parent=H)

# Crinière de brume : brins qui partent de l'arrière du crâne et filent vers l'arrière
for rg in range(MANE_RINGS):
    for k in range(MANE_COUNT):
        ang = math.radians(-150 + k * (300 / max(1, MANE_COUNT - 1)) + rg * 9)
        radial = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (radial.x * 0.55, 0.5 + rg * 0.2, radial.z * 0.5 - 0.05)
        jitter = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.3), random.uniform(-0.15, 0.15)))
        direction = radial * (0.8 - rg * 0.15) + Vector((0, 1.0, 0)) + jitter
        wisp(f"Head_Mane_{rg}_{k}", loc, direction, (2.2 + rg * 0.5 + random.random() * 0.8) * MANE_K, (0.6 - rg * 0.08) * max(0.7, MANE_K),
             mane_mat(), H, curl=(0, 0.2, -0.5), n=MANE_LINK, up=tuple(radial.cross(Vector((0, 1, 0)))))

# ----------------------------------------------------------
# 10. CORPS EN S : segments, ventre, flancs, pics, veines lumineuses, crinière du dos, dissolution de la queue
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
    misty = s >= MIST_START

    # Segment principal : plein au début, de plus en plus brumeux vers la queue
    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R,
        M_MIST if misty else M_BODY, parent, bevel=0 if misty else SEG_BEVEL)

    if not misty:
        # Plaques de ventre lilas (séparées) + bande sombre sur les flancs
        if s < 0.8:
            box(f"{tag}_Belly_{i}", (2 * r * 0.84, L * 0.85, 0.2), mid - d * (r * 0.95), R, M_BELLY, parent, bevel=0)
            for sgn in (-1, 1):
                box(f"{tag}_Flank_{i}_{sgn}", (0.08, L * 0.9, r * 0.5), mid + side * sgn * r - d * r * 0.5,
                    R, M_SCALEB, parent, bevel=0)
        # Écaille dorsale sombre légèrement inclinée
        Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
        box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.18), mid + d * (r * 0.95), Rtilt, M_SCALEA, parent, bevel=0)

        # Veine de brume lumineuse sur chaque flanc (un trait sur deux)
        if GLOW_VEINS and 0.1 < s < 0.85 and True:
            for sgn in (-1, 1):
                box(f"{tag}_Vein_{i}_{sgn}", (0.07, L * 0.8, 0.09), mid + side * sgn * (r + 0.03) + d * r * 0.15,
                    R, M_GLOW, parent, bevel=0)

        # Pics noirs sur le dos : une rangée (ado) ou une double rangée (adulte)
        if SPIKE_ROWS and i % 2 == 0 and 0.08 < s < 0.8:
            if SPIKE_ROWS == 1:
                shard(f"{tag}_Spike_{i}", 0.26 + 0.1 * r, 0.1, 0.4 + r * 0.6, mid + d * r * 0.9, d + t * 0.45, mat=M_HORN, parent=parent)
            else:
                for sgn in (-1, 1):
                    shard(f"{tag}_Spike_{i}_{sgn}", 0.2 + 0.1 * r, 0.1, 0.35 + r * 0.55,
                          mid + d * r * 0.9 + side * sgn * r * 0.4, d + side * sgn * 0.5 + t * 0.45, mat=M_HORN, parent=parent)

        # Anneaux d'argent autour du corps
        if BAND_EVERY and i % BAND_EVERY == BAND_EVERY // 2 and 0.08 < s < 0.78:
            ring(f"{tag}_Band_{i}", r * 1.06, 0.14, 0.26, mid, t, M_SILVER, parent, sides=8, up=tuple(d))
    else:
        # La queue se dissout : brins de brume qui se détachent des segments
        for sgn in (-1, 1):
            wisp(f"{tag}_Dissolve_{i}_{sgn}", mid + side * sgn * r * 0.5, t + side * sgn * 0.5 + d * 0.15,
                 (0.9 + 1.4 * (s - MIST_START) / (1 - MIST_START)) * TAIL_K, 0.3 + r * 0.4, mane_mat(), parent,
                 curl=tuple(d * 0.3), n=2, up=tuple(d))

    # Crinière de brume le long du cou et du dos : brins qui filent vers l'arrière
    if RIBBON_EVERY and RIBBON_RANGE[0] < s < RIBBON_RANGE[1] and i % RIBBON_EVERY == 0:
        for amt in (-0.5, 0.0, 0.5):
            wisp(f"{tag}_Ribbon_{i}_{amt}", mid + d * r * 0.8 + side * amt * r, d * 0.6 + t * 1.0 + side * amt * 0.5,
                 (1.5 + random.random() * 1.0) * MANE_K, 0.5 * max(0.7, MANE_K), mane_mat(), parent,
                 curl=tuple(d * 0.4), n=2, up=tuple(side))

# ----------------------------------------------------------
# 11. PATTES : épaule, avant-bras, bracelet d'argent, aileron de brume, pied à 3 griffes noires
# ----------------------------------------------------------
def paw(name, center):
    k_ = LEG_K
    box(f"{name}_Paw", (0.55 * k_, 0.55 * k_, 0.3 * k_), center, mat=M_BODY, parent=legs_root, bevel=0.04)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0)) * k_
        end = center + Vector((k * 0.24, -0.55, -0.08 if GROUNDED else -0.2)) * k_
        link(f"{name}_Toe_{k}", base, end, 0.14 * k_, M_BODY, legs_root, bevel=0)
        shard(f"{name}_Claw_{k}", 0.12 * k_, 0.12 * k_, 0.28 * k_, end,
              (k * 0.2, -1, -0.4 if GROUNDED else -0.9), mat=M_HORN, parent=legs_root)

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
        link(f"{n}_Cuff", joint.lerp(wrist, 0.62), wrist, cfg["th_low"] + 0.14, M_SILVER, legs_root, up=(1, 0, 0), bevel=0)
        if LEG_FIN_RAYS:
            fin_fan(f"{n}_ElbowFin", joint, [joint + Vector((sgn * 0.5, 0.5, 0.35)) * LEG_K,
                                            joint + Vector((sgn * 0.6, 0.9, -0.05)) * LEG_K,
                                            joint + Vector((sgn * 0.45, 1.1, -0.5)) * LEG_K][:LEG_FIN_RAYS], wings_root)
        paw(n, wrist + Vector((0, -0.2, -0.12)) * LEG_K)

leg("Legs_Front", LEG_FRONT)
leg("Legs_Back", LEG_BACK)

# ----------------------------------------------------------
# 12. AILES : pas d'ailes (oriental). Ailerons de brume : oreilles (9), coudes (11), épaules (14).
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : se dissout en brume (section 10), panache de brume et ornement d'argent au bout
# ----------------------------------------------------------
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
for k in range(TAIL_PLUME_N):
    a = k / TAIL_PLUME_N * 2 * math.pi
    sp = tside * math.cos(a) + td * math.sin(a)
    wisp(f"Tail_Plume_{k}", tip, tt + sp * 0.45, (2.4 + random.random() * 1.0) * TAIL_K, 0.5 * TAIL_K, mane_mat(), tail_root,
         curl=tuple(td * 0.35 + sp * 0.2), n=3, up=tuple(sp.cross(tt)))
if TAIL_ORNAMENT:
    ring("Tail_Ring", 0.7 * TAIL_K, 0.12, 0.1, tip + tt * 0.35 * TAIL_K, tt, M_SILVER, tail_root, sides=10, up=tuple(td))
    crystal("Tail_Gem", 0.2 * TAIL_K, 0.4 * TAIL_K, 0.4 * TAIL_K, tip + tt * 0.1, tt, mat=M_EYE, parent=tail_root, up=tuple(td))
    for k in range(4):
        a = k / 4 * 2 * math.pi + math.pi / 4
        sp = tside * math.cos(a) + td * math.sin(a)
        shard(f"Tail_Star_{k}", 0.28 * TAIL_K, 0.1, 1.0 * TAIL_K, tip + tt * 0.35 * TAIL_K + sp * 0.5 * TAIL_K, sp + tt * 0.3,
              mat=M_SILVER, parent=tail_root, up=tuple(tt))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (Légendaire) : argent, collier, plastron, épaulières, croissant d'aura, FX
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(CHEST_S)
CR = seg_matrix(ct, cd, cside)
if COLLAR:
    ring("Body_Collar", cr * 1.1, 0.16, 0.3, frame_at(COLLAR_S)[0], frame_at(COLLAR_S)[1], M_SILVER, body_root, sides=8, up=tuple(frame_at(COLLAR_S)[2]))
if CHEST_PLATE:
    wedge("Body_ChestPlate", (2 * cr * 1.05, 1.5, 0.3), cmid - cd * (cr + 0.05), CR, M_SILVER, body_root, top_x=0.8, top_y=0.85, bevel=0)
    box("Body_ChestInner", (2 * cr * 0.65, 1.0, 0.14), cmid - cd * (cr + 0.22), CR, M_HORN, body_root, bevel=0)
    crystal("Body_ChestGem", 0.3, 0.2, 0.3, cmid - cd * (cr + 0.28), -cd, mat=M_EYE, parent=body_root, up=tuple(ct))
    ring("Body_ChestMoon", 0.5, 0.1, 0.08, cmid - cd * (cr + 0.3), -cd, M_SILVER, body_root, sides=10, up=tuple(ct))
for sgn in (-1, 1):
    if CHEST_PLATE:
        shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.8, cmid - cd * (cr + 0.25) + cside * sgn * 0.4,
              cside * sgn * 0.6 - ct * 1.0, mat=M_SILVER, parent=body_root)
    if PAULDRONS:
        wedge(f"Body_Pauldron_{sgn}", (0.85, 1.0, 0.45), cmid + cside * sgn * (cr + 0.1) + cd * 0.35,
              CR @ Euler((0, math.radians(sgn * 25), 0)).to_matrix(), M_SILVER, body_root, top_x=0.75, top_y=0.8, bevel=0)
        shard(f"Body_PauldronSpike_{sgn}", 0.22, 0.1, 0.8, cmid + cside * sgn * (cr + 0.3) + cd * 0.6,
              cside * sgn * 0.7 + cd * 0.8, mat=M_HORN, parent=body_root)
    for k in range(SHOULDER_FINS):
        shard(f"Body_ShoulderMist_{sgn}_{k}", 0.4 - k * 0.06, 0.06, 1.4 - k * 0.25,
              cmid + cside * sgn * (cr + 0.1) + cd * (0.1 - k * 0.1), cside * sgn * 0.7 + ct * 0.9 + cd * 0.4,
              mat=M_MIST if k % 2 == 0 else M_MIST2, parent=wings_root)

# Croissant d'aura derrière la tête : pointes d'argent et lavande, arc de cristaux
if AURA_N:
    ac = Vector((0, 2.3, 0.2))
    for k in range(AURA_N):
        a = math.radians(-125 + k * 250 / max(1, AURA_N - 1))
        rad = Vector((math.sin(a), 0, math.cos(a)))
        top = 1.0 - abs(a) / math.radians(125) * 0.55
        shard(f"Head_AuraShard_{k}", 0.3, 0.1, (0.55 + 0.9 * top) * AURA_R / 2.6, ac + rad * (AURA_R + 0.05), rad,
              mat=M_SILVER if k % 2 == 0 else M_EYE, parent=H, up=(0, 1, 0))
    for k in range(AURA_N // 2):
        a = math.radians(-110 + (k + 0.5) * 220 / (AURA_N // 2))
        rad = Vector((math.sin(a), 0, math.cos(a)))
        crystal(f"Head_AuraGem_{k}", 0.1, 0.16, 0.18, ac + rad * AURA_R * 0.82, rad, mat=M_GLOW, parent=H, up=(0, 1, 0))

if ADD_FLOATING_FX:
    lo = Vector([min(p[j] for p in CTRL) for j in range(3)])
    hi = Vector([max(p[j] for p in CTRL) for j in range(3)])
    for k in range(FX_COUNT):
        p = Vector((random.uniform(-3.0, 3.0), random.uniform(lo.y - 2.0, hi.y + 1.0),
                    random.uniform(max(0.6, lo.z - 0.5), HEAD_POS.z + 1.8)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 3 == 0:
            shard(f"FX_Wisp_{k}", 0.35 * FX_K, 0.06, 0.9 * FX_K, p, dirv, mat=M_MIST2, parent=master)
        else:
            crystal(f"FX_Crystal_{k}", 0.08 * FX_K, 0.12 * FX_K, 0.14 * FX_K, p, dirv, mat=M_GLOW, parent=master)
    for k in range(FX_RINGS):
        p = Vector((random.uniform(-2.5, 2.5), random.uniform(lo.y - 1.0, hi.y), random.uniform(max(1.0, lo.z), HEAD_POS.z + 1.0)))
        ring(f"FX_Ring_{k}", random.uniform(0.35, 0.55) * FX_K, 0.07, 0.05, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
             M_SILVER if k % 2 == 0 else M_EYE, master, sides=8)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
