import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Nébula · Bébé
#  Exclusif · Ténèbres · Oriental · monde exclusif (payant)
#  - Long dragon oriental qui flotte en croissant de lune : tête en haut devant, ventre bas, queue qui remonte
#  - Corps noir et violet parsemé d'étoiles à 4 branches émissives, bandes de nébuleuse bleu / rose / violet sur les flancs
#  - Crinière en nébuleuse (grands éclats translucides lumineux) le long du cou et du dos, cornes en croissant
#  - Yeux étoilés, étoile frontale, anneaux d'orbite lumineux derrière la tête et le corps, étoiles flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(9091)            # même dragon à chaque exécution
TAG = "NEBULA_BEBE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 4       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 7000          # budget de triangles de ce stade et de cette rareté
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
STAGE = "BEBE"
HEAD_TILT = 3                 # inclinaison de la tête vers l'avant (degrés)
SNOUT_L = 1.0                 # longueur du museau
BABY_EYES = True              # True = très grands yeux ronds avec reflet (bébé)
BROW_ANGLE = -4               # sourcils : plus l'angle est grand, plus le regard est sévère
HORN_K = 0.5                  # taille des cornes en croissant (1 = pleine taille)
WHISKER_K = 0.5               # longueur des moustaches
BEARD_N = 0                   # éclats de barbe
FANGS = 0                     # crocs par côté
MANE_RINGS, MANE_COUNT, MANE_K = 2, 7, 0.6   # crinière nébuleuse de la tête : rangées, éclats par rangée, taille
BODY_MANE_K = 0.5             # taille de la crinière le long du dos (0 = aucune)
BODY_MANE_END = 0.92                  # la crinière du dos s'arrête à s = 0.92
STAR_CHANCE = 0.55             # probabilité d'étoiles sur chaque côté d'un segment
STAR_K = 1.0                  # taille des étoiles du corps
HALO_N = 4                    # éclats du halo derrière la tête
ORBIT_RINGS = 1               # anneaux d'orbite derrière le dragon (0 à 2)

CTRL_K = 0.42                 # échelle du corps (la tête garde sa taille : petit corps = grosse tête)
RAD_K = 0.75                  # épaisseur du corps
RING_R = 2.3                  # rayon du premier anneau d'orbite

# Colonne vertébrale : croissant de lune (tête en haut devant, ventre bas, queue qui remonte)
CTRL = [
    (0.0, -1.4, 8.8),    # sous le crâne
    (0.0, -0.7, 8.0),
    (0.0,  0.5, 6.8),    # cou
    (0.0,  2.0, 5.3),
    (0.0,  3.6, 3.9),    # poitrail
    (0.2,  5.4, 2.9),
    (0.5,  7.2, 2.6),    # bas du ventre
    (0.5,  9.0, 3.4),
    (0.2, 10.4, 4.9),    # hanches
    (-0.2, 11.0, 6.7),   # queue qui remonte
    (-0.5, 10.8, 8.4),
    (-0.6, 10.0, 9.6),   # bout de queue en comète
]
RADIUS_KEYS = [(0.0, 0.62), (0.08, 0.74), (0.2, 0.92), (0.35, 1.0), (0.5, 0.96),
               (0.65, 0.8), (0.82, 0.5), (1.0, 0.2)]
RADIUS_KEYS = [(a, b * RAD_K) for a, b in RADIUS_KEYS]
CTRL = [tuple(c * CTRL_K for c in p) for p in CTRL]
HEAD_POS = Vector(CTRL[0]) + Vector((0, -0.1, 0.1))   # base du crâne (HEAD_ROOT), collée au début du corps
SEG_STEP = 0.52               # longueur d'un segment du corps
TAIL_START = 0.62                     # à partir de s = 0.62, les segments vont dans TAIL_ROOT
TUFT_N, TUFT_L = 5, 0.9               # comète au bout de la queue : éclats, longueur
FX_COUNT = 10                 # étoiles flottantes
FX_SPREAD = 1.8               # largeur de la zone des étoiles flottantes
FX_SIZE = 0.3                         # taille des étoiles flottantes

# Pattes : position sur le corps (s), vecteurs haut et bas de patte, épaisseurs, écart sur le côté.
LEG_FRONT = dict(s=0.3, upper=(0, -0.45, -0.7), lower=(0, -0.55, -0.35), th_up=0.46, th_low=0.36, push=0.3)
LEG_BACK  = dict(s=0.62, upper=(0, -0.5, -0.5), lower=(0, 0.3, -0.7),   th_up=0.52, th_low=0.38, push=0.28)
LEG_K = 1.2                   # taille des épaules, pieds et griffes
LEG_D = 0.75                  # longueur des segments de patte

# ----------------------------------------------------------
# 7. PALETTE (identique aux 3 stades) : noir-violet, violets, nébuleuse bleu / rose / violet, étoiles blanches émissives
# ----------------------------------------------------------
M_VOID   = get_mat("Void",     "#150B2E", 0.40, 0.05)   # corps principal, crâne (noir violacé)
M_VIOLET = get_mat("Violet",   "#43248A", 0.40, 0.10)   # flancs, pattes, museau
M_PURPLE = get_mat("Purple",   "#6A3FC8", 0.35, 0.10)   # écailles du dos, plastron
M_DEEP   = get_mat("Deep",     "#24124A", 0.45, 0.10)   # sourcils, bracelets, bouche, narines
M_BELLY  = get_mat("Belly",    "#8863E6", 0.45)         # plaques du ventre
M_HORN   = get_mat("Horn",     "#1B1040", 0.30, 0.20)   # cornes en croissant
M_NEB_V  = get_mat("NebulaV",  "#8A4FE0", 0.30, 0.0, emission="#8A4FE0", strength=1.8, alpha=0.78)   # nébuleuse violette
M_NEB_P  = get_mat("NebulaP",  "#E05AC8", 0.30, 0.0, emission="#E05AC8", strength=1.8, alpha=0.78)   # nébuleuse rose
M_NEB_B  = get_mat("NebulaB",  "#4A7FFF", 0.30, 0.0, emission="#4A7FFF", strength=1.8, alpha=0.78)   # nébuleuse bleue
M_STAR   = get_mat("Star",     "#FFFFFF", 0.10, 0.0, emission="#FFFFFF", strength=6.0)   # étoiles blanches
M_STAR_B = get_mat("StarBlue", "#BFD6FF", 0.10, 0.0, emission="#9CC0FF", strength=5.0)   # étoiles bleu pâle
M_STAR_P = get_mat("StarPink", "#FFC4F2", 0.10, 0.0, emission="#FF9BE6", strength=5.0)   # étoiles rose pâle
M_WHITE  = get_mat("EyeWhite", "#EDE6FF", 0.30)
M_EYE    = get_mat("EyeDark",  "#0A0618", 0.20)         # fond des yeux (nuit)
M_CLAW   = get_mat("Claw",     "#FFFFFF", 0.30)         # griffes, crocs
M_RING   = get_mat("Ring",     "#9B6CFF", 0.30, 0.0, emission="#8A4FE0", strength=2.6)   # anneaux d'orbite
NEBS = [M_NEB_V, M_NEB_P, M_NEB_B]
STARS = [M_STAR, M_STAR, M_STAR_B, M_STAR_P]

def mane_mat():
    """Éclats de nébuleuse : mélange violet / rose / bleu translucides."""
    return pick(NEBS, [4, 3, 3])

def body_mat(s):
    """Couleur du corps le long de la colonne : du noir de la tête au violet du ventre, puis du noir au bout."""
    v = 0.5 + 0.5 * math.sin(s * 9.0)
    return M_VOID if v < 0.4 else (M_VIOLET if v < 0.8 else M_PURPLE)

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
IS_BEBE = (STAGE == "BEBE")

# Petite forme en plus : l'étoile à 4 branches (plate, dans le plan XY local, normale = Z local)
def star_mesh(R, t=None):
    t = R * 0.22 if t is None else t
    r = R * 0.22
    v = [(R, 0, 0), (r, r, 0), (0, R, 0), (-r, r, 0), (-R, 0, 0), (-r, -r, 0), (0, -R, 0), (r, -r, 0),
         (0, 0, t), (0, 0, -t)]
    f = []
    for k in range(8):
        n = (k + 1) % 8
        f.append((k, n, 8))
        f.append((n, k, 9))
    return mesh_from("star", v, f)

def star(name, R, loc, normal, mat, parent, spin=0.0):
    """Étoile émissive posée sur une surface : 'normal' = direction vers l'extérieur."""
    n = Vector(normal).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    tang = n.cross(ref).normalized()
    tang = tang * math.cos(spin) + n.cross(tang) * math.sin(spin)
    return place(name, star_mesh(R), mat, loc, basis(tang, n), parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT)
# ----------------------------------------------------------
sk = SNOUT_L / 1.55                  # facteur de longueur du museau
box("Head_Skull",       (1.5, 1.55, 1.35), (0, 0, 0), mat=M_VOID, parent=H, bevel=0.07)
box("Head_Snout",       (1.15, SNOUT_L, 0.72), (0, -0.62 - SNOUT_L / 2, -0.15), mat=M_VOID, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.8, 1.2 * sk, 0.2), (0, -0.65 - 0.6 * sk, 0.28), rot=(-6, 0, 0), mat=M_PURPLE, parent=H, bevel=0.03)
box("Head_NosePad",     (1.2, 0.3, 0.55), (0, -0.55 - SNOUT_L, -0.12), mat=M_VIOLET, parent=H, bevel=0)
box("Head_Jaw",         (1.05, 1.45 * sk, 0.32), (0, -0.53 - 0.72 * sk, -0.68), mat=M_VIOLET, parent=H, bevel=0)
box("Head_MouthLine",   (1.08, 1.4 * sk, 0.06), (0, -0.58 - 0.7 * sk, -0.52), mat=M_DEEP, parent=H, bevel=0)

# Étoile frontale dans un croissant : deux éclats nacrés en arc autour de l'étoile
box("Head_StarSocket", (0.7, 0.5, 0.16), (0, -0.62, 0.66), rot=(-20, 0, 0), mat=M_DEEP, parent=H, bevel=0.03)
star("Head_ForeheadStar", 0.42 * (1.0 if not IS_BEBE else 0.8), (0, -0.74, 0.72), (0, -0.5, 1), M_STAR, H)
for sgn in (-1, 1):
    shard(f"Head_Crescent_{sgn}", 0.2, 0.1, 0.7, (sgn * 0.42, -0.6, 0.62), (sgn * 0.35, 0.1, 1), mat=M_NEB_B if sgn < 0 else M_NEB_P, parent=H)

for sgn in (-1, 1):
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -0.72 - SNOUT_L, 0.0), mat=M_DEEP, parent=H, bevel=0)
    if BABY_EYES:
        # Très grands yeux de bébé : fond nuit, grande étoile blanche, reflet
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.66, 0.64), (sgn * 0.76, -0.3, 0.12), mat=M_EYE, parent=H, bevel=0)
        star(f"Head_EyeStar_{sgn}", 0.34, (sgn * 0.81, -0.3, 0.1), (sgn, 0, 0), M_STAR, H)
        star(f"Head_EyeGlint_{sgn}", 0.12, (sgn * 0.84, -0.42, 0.24), (sgn, 0, 0), M_STAR_P, H)
    else:
        # Yeux étoilés : fond nuit, anneau violet, étoile blanche à 4 branches
        box(f"Head_EyeWhite_{sgn}", (0.08, 0.5, 0.42), (sgn * 0.76, -0.35, 0.12), mat=M_EYE, parent=H, bevel=0)
        star(f"Head_EyeStar_{sgn}", 0.3, (sgn * 0.81, -0.37, 0.12), (sgn, 0, 0), M_STAR, H)
        box(f"Head_EyeRim_{sgn}", (0.06, 0.56, 0.06), (sgn * 0.77, -0.35, 0.36), mat=M_NEB_V, parent=H, bevel=0)
    box(f"Head_Brow_{sgn}", (0.35, 0.7, 0.22), (sgn * 0.72, -0.4, 0.44 + (0.08 if BABY_EYES else 0)),
        rot=(BROW_ANGLE, 0, sgn * -8), mat=M_DEEP, parent=H, bevel=0.03)

    # Crocs
    for k in range(FANGS):
        shard(f"Head_Fang_{sgn}_{k}", 0.1, 0.1, 0.32, (sgn * 0.45, -0.95 - 0.38 * k * sk - 0.1, -0.55),
              (0, 0.05, -1), mat=M_CLAW, parent=H, up=(1, 0, 0))

    # Oreilles / nageoires de nébuleuse et pointes de joues
    shard(f"Head_Ear_{sgn}", 0.5, 0.1, 1.2, (sgn * 0.75, 0.3, 0.35), (sgn * 0.8, 1, 0.4), mat=M_NEB_V, parent=H)
    shard(f"Head_Cheek1_{sgn}", 0.3, 0.1, 0.8, (sgn * 0.6, -0.6, -0.55), (sgn * 0.9, 0.8, -0.3), mat=M_NEB_B, parent=H)
    shard(f"Head_Cheek2_{sgn}", 0.3, 0.1, 0.9, (sgn * 0.55, -0.2, -0.6), (sgn * 0.7, 1, -0.6), mat=M_NEB_P, parent=H)

    # Cornes en croissant : se courbent vers l'arrière puis remontent, pointe étoilée
    k_ = HORN_K
    hp = [Vector((sgn * 0.45, 0.3, 0.6)), Vector((sgn * 0.8, 0.9, 1.0)), Vector((sgn * 1.0, 1.9, 1.15)),
          Vector((sgn * 0.95, 2.9, 1.45)), Vector((sgn * 0.7, 3.6, 2.2))]
    hp = [hp[0]] + [hp[0] + (p - hp[0]) * k_ for p in hp[1:]]
    chain(f"Head_Horn_{sgn}", hp, 0.34 * max(0.8, k_), 0.12, M_HORN, H, bevel=0.03)
    star(f"Head_HornStar_{sgn}", 0.32 * max(0.7, k_), hp[-1] + Vector((0, 0.1, 0.25)), (sgn * 1, 0, 0), M_STAR_B, H, spin=0.5)
    link(f"Head_HornSpur_{sgn}", hp[1], hp[1] + Vector((sgn * 0.5, -0.3, 0.9)) * k_, 0.16 * max(0.8, k_), M_HORN, H, bevel=0)

    # Longues moustaches en rubans de nébuleuse qui flottent vers l'arrière
    wb = Vector((sgn * 0.58, -0.4 - SNOUT_L, -0.05))
    wpts = [wb] + [wb + (Vector(p) - Vector((sgn * 0.58, -1.95, -0.05))) * WHISKER_K
                   for p in [(sgn * 1.3, -1.6, -0.45), (sgn * 1.9, -0.7, -0.9), (sgn * 2.3, 0.5, -1.2), (sgn * 2.2, 1.6, -0.9)]]
    chain(f"Head_Whisker_{sgn}", wpts, 0.12, 0.07, M_NEB_B if sgn < 0 else M_NEB_P, H, bevel=0)

# Barbe d'éclats de nébuleuse sous le menton
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, (0.7 + random.random() * 0.3) * MANE_K,
          (x, -0.3 - 0.6 * sk + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=mane_mat(), parent=H)

# Crinière en nébuleuse : grand éventail d'éclats translucides lumineux derrière la tête
for rg in range(MANE_RINGS):
    for k in range(MANE_COUNT):
        ang = math.radians(-155 + k * (310 / (MANE_COUNT - 1)) + rg * 8)
        radial = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (radial.x * 0.6, 0.4 + rg * 0.3, radial.z * 0.55 - 0.05)
        jitter = Vector((random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.2), random.uniform(-0.2, 0.2)))
        direction = radial * (1.1 - rg * 0.3) + Vector((0, 1.0, 0)) + jitter
        shard(f"Head_Mane_{rg}_{k}", (0.7 - rg * 0.08) * max(0.8, MANE_K), 0.14,
              (1.6 + rg * 0.4 + random.random() * 0.6) * MANE_K,
              loc, direction, mat=mane_mat(), parent=H, up=tuple(radial.cross(Vector((0, 1, 0)))))

# Halo d'étoiles derrière la tête (arc d'étoiles et de pointes lumineuses)
for k in range(HALO_N):
    a = math.radians(-120 + k * 240 / max(1, HALO_N - 1))
    pos = (math.sin(a) * 2.4, 1.9, math.cos(a) * 2.0 + 0.1)
    star(f"Head_Halo_{k}", (0.32 + 0.14 * (k % 3)) * max(0.7, MANE_K), pos, (0, -1, 0), STARS[k % 4], H, spin=k)

# ----------------------------------------------------------
# 10. CORPS EN CROISSANT : segments, ventre, bandes de nébuleuse, étoiles, crinière du dos
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
    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R, body_mat(s), parent, bevel=0.06)

    # Plaques de ventre séparées
    if s < 0.88:
        box(f"{tag}_Belly_{i}", (2 * r * 0.86, L * 0.85, 0.22), mid - d * (r * 0.95), R, M_BELLY, parent, bevel=0.03)

    # Écaille dorsale légèrement inclinée
    Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
    box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.2), mid + d * (r * 0.95), Rtilt, M_DEEP if i % 2 else M_PURPLE, parent, bevel=0.03)

    # Bandes de nébuleuse sur les flancs : bleu, rose, violet qui tournent d'un segment à l'autre
    for sgn in (-1, 1):
        box(f"{tag}_Cloud_{i}_{sgn}", (0.1, L * 0.92, r * 0.95), mid + side * sgn * r - d * r * 0.15,
            R, NEBS[(i + (0 if sgn < 0 else 1)) % 3], parent, bevel=0)

    # Étoiles émissives sur les flancs et sur le dos
    for sgn in (-1, 1):
        if random.random() < STAR_CHANCE:
            off = random.uniform(-0.55, 0.45) * r
            Rs = random.uniform(0.14, 0.3) * STAR_K * (0.6 + 0.6 * r)
            star(f"{tag}_Star_{i}_{sgn}", Rs, mid + side * sgn * (r + 0.07) + d * off + t * random.uniform(-0.15, 0.15),
                 side * sgn, random.choice(STARS), parent, spin=random.random() * 3)
    if i % 2 == 0:
        star(f"{tag}_DorsalStar_{i}", 0.22 * STAR_K * (0.6 + 0.6 * r), mid + d * (r * 0.95 + 0.14) + side * random.uniform(-0.3, 0.3) * r,
             d, random.choice(STARS), parent, spin=random.random() * 3)

    # Crinière de nébuleuse qui coule du cou à la queue : un éclat central + deux latéraux
    if BODY_MANE_K > 0 and s < BODY_MANE_END:
        fade = 1.0 - 0.55 * s
        n_mane = 3 if s < 0.45 else 1
        for k in range(n_mane):
            amt = (k - (n_mane - 1) / 2) * 0.9 + random.uniform(-0.1, 0.1)
            shard(f"{tag}_Mane_{i}_{k}", 0.65 * max(0.8, BODY_MANE_K), 0.12,
                  (1.1 + 1.0 * fade + random.random() * 0.5) * BODY_MANE_K,
                  mid + d * r * 0.85 + side * amt * r * 0.4, d + t * 0.95 + side * amt * 0.45,
                  mat=NEBS[(i + k) % 3], parent=parent)
        if s < 0.3:
            for sgn in (-1, 1):
                shard(f"{tag}_NeckSide_{i}_{sgn}", 0.4, 0.1, (0.8 + 0.5 * fade) * BODY_MANE_K,
                      mid + side * sgn * r * 0.85, side * sgn + t * 0.8 + d * 0.3,
                      mat=NEBS[(i + 1 + (sgn > 0)) % 3], parent=parent)

    # Petites nageoires dorsales de nébuleuse sur la fin de la queue
    if s >= 0.82:
        shard(f"Tail_Fin_{i}", 0.35 * r + 0.1, 0.08, 0.5 + r * 0.6, mid + d * r * 0.9, d + t * 0.8,
              mat=NEBS[i % 3], parent=tail_root)

# Plastron : plaque violette avec étoile blanche, cadre en éclats bleu et rose
CHEST_S = 0.3
cmid, ct, cd, cside, cr = frame_at(CHEST_S)
CR = seg_matrix(ct, cd, cside)
box("Body_ChestPlate", (2 * cr * 1.05, 1.4, 0.25), cmid - cd * (cr + 0.05), CR, M_PURPLE, body_root, bevel=0.05)
box("Body_ChestInner", (2 * cr * 0.7, 1.0, 0.12), cmid - cd * (cr + 0.2), CR, M_DEEP, body_root, bevel=0.03)
star("Body_ChestStar", 0.5, cmid - cd * (cr + 0.3), -cd, M_STAR, body_root)
for sgn in (-1, 1):
    shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.8, cmid - cd * (cr + 0.25) + cside * sgn * 0.35,
          cside * sgn * 0.6 - ct * 1.0, mat=NEBS[1 + (sgn > 0)], parent=body_root)
    for k in range(3):
        shard(f"Body_ShoulderFin_{sgn}_{k}", 0.5 - k * 0.08, 0.08, 1.3 - k * 0.2,
              cmid + cside * sgn * (cr + 0.1) + cd * (0.35 - k * 0.15) - ct * (0.3 - k * 0.25),
              ct * 0.6 + cd * 0.8 + cside * sgn * 0.6, mat=NEBS[k % 3], parent=body_root)

# ----------------------------------------------------------
# 11. PATTES : 4 petites pattes tenues contre le ventre, bracelets sombres, griffes blanches
# ----------------------------------------------------------
def paw(name, center):
    k_ = LEG_K
    box(f"{name}_Paw", (0.55 * k_, 0.55 * k_, 0.3 * k_), center, mat=M_VIOLET, parent=legs_root, bevel=0.04)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0)) * k_
        end = center + Vector((k * 0.24, -0.55, -0.2)) * k_
        link(f"{name}_Toe_{k}", base, end, 0.14 * k_, M_VIOLET, legs_root, bevel=0)
        shard(f"{name}_Claw_{k}", 0.12 * k_, 0.12 * k_, 0.28 * k_, end, (k * 0.2, -1, -0.9), mat=M_CLAW, parent=legs_root)

def leg(name, cfg):
    mid, t, d, side, r = frame_at(cfg["s"])
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.85 - d * 0.15
        joint = root + Vector((sgn * cfg["push"], 0, 0)) + Vector(cfg["upper"]) * LEG_D
        wrist = joint + Vector((sgn * 0.05, 0, 0)) + Vector(cfg["lower"]) * LEG_D
        box(f"{n}_Shoulder", (0.62 * LEG_K,) * 3, root, mat=M_VIOLET, parent=legs_root, bevel=0.06)
        link(f"{n}_Upper", root, joint, cfg["th_up"], M_VIOLET, legs_root, up=(1, 0, 0), bevel=0.05)
        link(f"{n}_Lower", joint, wrist, cfg["th_low"], M_VIOLET, legs_root, up=(1, 0, 0), bevel=0.04)
        link(f"{n}_Cuff", joint.lerp(wrist, 0.6), wrist, cfg["th_low"] + 0.14, M_DEEP, legs_root, up=(1, 0, 0), bevel=0.03)
        star(f"{n}_CuffStar", 0.16 * LEG_K, joint.lerp(wrist, 0.5) + Vector((sgn * (cfg["th_low"] / 2 + 0.1), 0, 0)),
             (sgn, 0, 0), M_STAR_B, legs_root)
        shard(f"{n}_ElbowSpike", 0.25 * LEG_K, 0.08, 0.6 * LEG_K, joint, (sgn * 0.4, 0.8, 0.2), mat=NEBS[1], parent=legs_root)
        paw(n, wrist + Vector((0, -0.2, -0.12)) * LEG_K)

leg("Legs_Front", LEG_FRONT)
leg("Legs_Back", LEG_BACK)

# ----------------------------------------------------------
# 12. AILES : pas de grandes ailes (oriental) -> ailerons de nébuleuse sur les épaules, voir section 10
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : collier, comète d'éclats de nébuleuse et grande étoile au bout
# ----------------------------------------------------------
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
box("Tail_TipCollar", (0.5, 0.4, 0.5), tip, seg_matrix(tt, td, tside), M_DEEP, tail_root, bevel=0.03)
for k in range(TUFT_N):
    a = k / TUFT_N * 2 * math.pi
    spread = tside * math.cos(a) + td * math.sin(a)
    shard(f"Tail_Tuft_{k}", 0.4, 0.1, TUFT_L * (0.7 + 0.5 * random.random()), tip, tt + spread * 0.55,
          mat=NEBS[k % 3], parent=tail_root)
star("Tail_TipStar", 0.6, tip + tt * 0.55, tside, M_STAR, tail_root)
star("Tail_TipStarB", 0.45, tip + tt * 0.55, td, M_STAR_B, tail_root, spin=0.8)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (EXCLUSIF) : anneaux d'orbite, étoiles flottantes
# ----------------------------------------------------------
lo = Vector([min(p[j] for p in CTRL) for j in range(3)])
hi = Vector([max(p[j] for p in CTRL) for j in range(3)])
if ORBIT_RINGS > 0:
    cy, cz = (lo.y + hi.y) / 2 + 0.2, (lo.z + hi.z) / 2 + 0.3
    for k in range(ORBIT_RINGS):
        rr = RING_R + k * 1.1 * RING_R / 4.9
        ring(f"Orbit_Ring_{k}", rr, 0.14 + 0.05 * k, 0.08, (-2.2 - k * 0.5, cy, cz), (1, 0, 0), M_RING, master, sides=28)
        for j in range(3):
            a = j * 2.1 + k
            star(f"Orbit_Star_{k}_{j}", 0.38, (-2.2 - k * 0.5, cy + rr * math.cos(a), cz + rr * math.sin(a)), (1, 0, 0),
                 STARS[(j + k) % 4], master, spin=a)

if ADD_FLOATING_FX:
    for k in range(FX_COUNT):
        p = Vector((random.uniform(-1, 1) * FX_SPREAD, random.uniform(lo.y - 2.0, hi.y + 1.5), random.uniform(max(1.0, lo.z - 0.5), hi.z + 1.2)))
        nrm = Vector([random.uniform(-1, 1) for _ in range(3)])
        star(f"FX_Star_{k}", FX_SIZE * random.uniform(0.6, 1.3), p, nrm, STARS[k % 4], master, spin=random.random() * 3)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
