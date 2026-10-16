import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Liane · Bébé
#  Épique · Plante · Hydre · monde 3
#  - Bébé : TROIS têtes à touffe de feuilles sur cous très courts (la centrale plus grande), corps trapu, très grands yeux ambre
#  - Lianes entrecroisées sur le corps, petites fleurs orange et roses, carapace d'écorce brune sur le dos
#  - Écailles-feuilles sur les flancs, ventre en plaques vert clair, feuille et bourgeon au bout de la queue
#  - Épique discret : fleurs lumineuses, sève lumineuse, plastron avec clous dorés, spores flottantes
#  - Pas d'ailes (hydre de forêt) : quatre pattes courtes, trois doigts et trois griffes ivoire
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3303)            # même dragon à chaque exécution
TAG = "LIANE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
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
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
GLOW_STR = 1.8                    # puissance de l'émission (fleurs, sève, yeux)
GOLD = False                      # ornements dorés (Épique)
RIBS = False                      # nervures claires sur les grandes feuilles
BW = 2.6                          # largeur du torse
BH = 2.1                          # hauteur du torse
LEG_H = 1.2                       # hauteur des pattes
TORSO_L = 2.9                     # longueur torse + bassin
NECK_L = 0.45                     # hauteur du cou central
NECK_LEAN = 0.1                   # avancée du cou vers l'avant
NECK_N = 2                        # nombre de maillons par cou
NECK_R = (0.78, 0.72)             # rayon du cou : base, haut
NECK_CURVE = 0.0                  # courbure en S des cous
NECK_LEAF_K = 0.8                 # taille des feuilles de nuque
NECK_FLOWERS = False              # fleurs sur les cous
HEAD_SCALE = 1.25                 # taille de la tête centrale
HEAD_PITCH = 0                    # degrés : la tête regarde vers le bas
HEADS = [(0.0, 0.0, 0.0, 1.0, 0), (-2.0, 0.6, -0.35, 0.8, -22), (2.0, 0.6, -0.35, 0.8, 22)]# (décalage X, Y, Z, échelle, rotation vers l'extérieur en degrés)
SNOUT_L = 0.85                    # longueur du museau
JAW_OPEN = 0                      # ouverture de la gueule (degrés)
FANGS = 0                         # crocs par côté
HORN_L = 0.0                      # longueur des cornes
EYE = (0.92, 0.95, 0.68, 0.76, 0.36, 0.48)# blanc L/H, iris L/H, pupille L/H
BROW_TILT = 0                     # inclinaison des sourcils
TUFT_N = 5                        # feuilles de la touffe sur chaque tête
TUFT_L = 1.5                      # longueur des feuilles de la touffe
CHEEK_N = 1                       # feuilles de joue par côté
FLOWER_HEAD2 = False              # fleurs supplémentaires sur les têtes
SCALE_ROWS = 2                    # rangées d'écailles-feuilles par flanc
SCALE_COLS = 4                    # écailles par rangée
BELLY_N = 3                       # plaques de ventre
CARA_N = 4                        # rangées de la carapace d'écorce
CREST_H = 0.9                     # hauteur des feuilles de crête
VINE_TURNS = 1.5                  # tours de chaque liane autour du torse
VINE_SEG = 7                      # segments par tour de liane
VINE_TH = 0.17                    # épaisseur des lianes
VINE_FLOWERS_A = (0.3, 0.7)       # positions (0 à 1) des fleurs sur la liane A
VINE_FLOWERS_B = (0.5,)           # positions des fleurs sur la liane B
FLOWER_N = 2                      # fleurs sur le dos
FLOWER_R = 0.3                    # taille des fleurs
SWIRLS = 0                        # spirales claires par flanc
BRACER_K = 0.32                   # hauteur du bracelet
CLAW_K = 0.45                     # longueur des griffes
THIGH_LEAVES = 0                  # feuilles sur chaque cuisse
TAIL_L = 2.4                      # longueur de la queue
TAIL_STEP = 0.5                   # pas des segments de queue
TAIL_VINE = False                 # lianes sur la queue
TAIL_TIP = 0.9                    # taille des feuilles du bout de queue
TAIL_TIP_LEAVES = 3               # feuilles du bout de queue
TAIL_FLOWER = True                # fleur au bout de la queue
SAP_N = 2                         # grappes de sève lumineuse sur le dos
FX_N = 6                          # spores / pétales / feuilles flottants
FX_SIZE = 0.28                    # taille des FX

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Corps vert sapin, ventre vert clair, écorce brune, feuilles de trois verts, lianes vertes,
#    fleurs orange et roses lumineuses, sève jaune-vert émissive, petits ornements dorés (Épique).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#3A7A2A", 0.55)   # corps principal
M_BODY2 = get_mat("BodyDark",  "#2A5A20", 0.60)   # écailles sombres, mâchoire
M_BODY3 = get_mat("BodyWarm",  "#4C9232", 0.55)   # écailles chaudes
M_DARK  = get_mat("Shadow",    "#183514", 0.70)   # jointures, narines, bouche
M_BELLY = get_mat("Belly",     "#A8D660", 0.50)   # ventre en plaques, plastron, gorges
M_BARK  = get_mat("Bark",      "#7E5234", 0.75)   # écorce (carapace, cornes)
M_BARK2 = get_mat("BarkDark",  "#573520", 0.80)   # écorce sombre (sourcils, strates)
M_LEAF  = get_mat("Leaf",      "#4FA832", 0.55)   # feuilles vert franc
M_LEAF2 = get_mat("LeafLight", "#8AD04A", 0.50)   # feuilles claires
M_LEAF3 = get_mat("LeafDeep",  "#2F7A28", 0.55)   # feuilles profondes
M_VINE  = get_mat("Vine",      "#5BA83A", 0.60)   # lianes
M_IRIS  = get_mat("Iris",      "#F28C2E", 0.25, emission="#F28C2E", strength=GLOW_STR)          # iris ambre
M_FLO_O = get_mat("FlowerOrange", "#F28C2E", 0.45, emission="#F28C2E", strength=GLOW_STR * 0.7)  # fleurs orange
M_FLO_P = get_mat("FlowerPink",   "#F27FA0", 0.45, emission="#F27FA0", strength=GLOW_STR * 0.7)  # fleurs roses
M_HEART = get_mat("FlowerHeart",  "#FFD84A", 0.35, emission="#FFC832", strength=GLOW_STR)        # coeur des fleurs
M_SAP   = get_mat("Sap",       "#C8F55A", 0.30, emission="#B8F040", strength=GLOW_STR)          # sève et spores lumineuses
M_CLAW  = get_mat("Claw",      "#EDE3C8", 0.40)   # griffes ivoire
M_FANG  = get_mat("Fang",      "#F4EBD0", 0.35)   # crocs
M_GOLD  = get_mat("Gold",      "#F2B233", 0.30, metallic=0.9)   # ornements dorés (Épique)
M_WHITE = get_mat("EyeWhite",  "#F2F2F2", 0.30)
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles
LEAVES = [M_LEAF, M_LEAF2, M_LEAF3]
LEAF_W = [4, 3, 3]
BODY_MATS, BODY_W = [M_BODY, M_BODY2, M_BODY3], [5, 2, 3]

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.0                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_TOP = Vector((0, -TL * 0.42 - NECK_LEAN, ZC + BH * 0.35 + NECK_L))   # sommet du cou central
TAIL_START = Vector((0, TL * 0.45, ZC - 0.05 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)

HEAD_ROOT_NAMES = ["HEAD_ROOT", "HEAD2_ROOT", "HEAD3_ROOT"]
head_roots = []
for k, (hx, hdy, hdz, hsc, hyaw) in enumerate(HEADS):
    pos = NECK_TOP + Vector((hx, hdy, hdz))
    mtx = (Matrix.Translation(pos) @ Euler((0, 0, math.radians(hyaw))).to_matrix().to_4x4()
           @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
    head_roots.append(empty(HEAD_ROOT_NAMES[k], master, mtx))

# Petits outils (pas de biseau par défaut : réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, tiges)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def leaf(name, base, direction, L, w, mat, parent, droop=0.25, up=(0, 0, 1), t=None, rib=False):
    """SIGNE DISTINCTIF : feuille = plaque en losange (4 points) qui part de 'base', pointe dans 'direction',
    longueur L, demi-largeur w, pointe qui retombe de 'droop' x L. 'rib' ajoute une nervure claire."""
    base = Vector(base)
    d = Vector(direction).normalized()
    side = d.cross(Vector(up))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    tip = base + d * L + Vector((0, 0, -droop * L))
    mid = base + d * (L * 0.42) + Vector((0, 0, 0.06 * L))
    plate(name, [base, mid + side * w, tip, mid - side * w], t if t is not None else max(0.03, w * 0.14), mat, parent)
    if rib:
        bar(name + "_Rib", base.lerp(tip, 0.04), base.lerp(tip, 0.9), max(0.03, w * 0.12), M_LEAF2, parent,
            depth=max(0.03, w * 0.12))
    return tip

def flower(name, loc, normal, r, parent, petal_mat, petals=5):
    """Fleur : coeur jaune lumineux (prisme) entouré de pétales en plaques."""
    n = Vector(normal).normalized()
    prism(name + "_Heart", r * 0.38, r * 0.28, loc, n, M_HEART, parent, sides=6)
    R = basis(n)
    ax, az = R.col[0], R.col[2]
    for k in range(petals):
        a = 2 * math.pi * k / petals
        dr = ax * math.cos(a) + az * math.sin(a) + n * 0.3
        leaf(f"{name}_Pet_{k}", Vector(loc) + n * (r * 0.05), dr, r, r * 0.46, petal_mat, parent, droop=0.0, up=tuple(n),
             t=r * 0.07)

def spike(name, base, direction, w, L, parent, up=(1, 0, 0), mat=None):
    """Pic d'écorce (sans biseau)."""
    shard(name, w, w * 0.6, L, base, Vector(direction).normalized(), mat or M_BARK, parent, up=up)

# ----------------------------------------------------------
# 9. TÊTES : une fonction construit une tête complète dans les coordonnées locales de son root.
#    Appelée pour HEAD_ROOT (centrale), HEAD2_ROOT et HEAD3_ROOT. Chaque tête a sa touffe de feuilles.
# ----------------------------------------------------------
def build_head(H, k, hs):
    """Tête n° k (1 = centrale) en coordonnées locales de l'empty H, à l'échelle hs."""
    P = f"Head{k}_"
    def hv(v):
        return tuple(c * hs for c in v)
    def hb(name, size, loc, rot=None, mat=None, bevel=0.0):
        return box(P + name, hv(size), hv(loc), rot, mat, H, bevel * hs)
    SNOUT_FRONT = -0.85 - SNOUT_L

    # Crâne et museau biseautés, arête du museau en écorce
    hb("Skull", (1.9, 1.75, 1.6), (0, 0, 0), mat=M_BODY, bevel=0.12)
    hb("Snout", (1.5, SNOUT_L + 0.3, 0.8), (0, -0.85 - SNOUT_L / 2 + 0.15, -0.3), mat=M_BODY3, bevel=0.08)
    hb("SnoutBridge", (0.75, SNOUT_L * 0.9, 0.16), (0, SNOUT_FRONT * 0.55 - 0.1, 0.16), mat=M_BARK)
    hb("Forehead", (1.3, 0.7, 0.18), (0, -0.55, 0.84), mat=M_BARK2)

    # Mâchoire distincte (entrouverte chez l'ado et l'adulte), gorge claire, ligne de bouche sombre
    hb("Jaw", (1.36, SNOUT_L + 0.5, 0.42), (0, -0.75 - SNOUT_L / 2 + 0.2, -0.86 - JAW_OPEN * 0.012),
       rot=(-JAW_OPEN, 0, 0), mat=M_BODY2, bevel=0.05)
    hb("Throat", (1.2, 1.1, 0.3), (0, 0.15, -0.88), mat=M_BELLY)
    hb("Chin", (0.9, 0.6, 0.16), (0, -0.75 - SNOUT_L * 0.8, -1.02 - JAW_OPEN * 0.02), mat=M_BELLY)
    hb("Mouth", (1.3, SNOUT_L + 0.3, 0.1 + JAW_OPEN * 0.012), (0, -0.85 - SNOUT_L / 2 + 0.2, -0.67), mat=M_DARK)

    # Narines
    for sgn in (-1, 1):
        hb(f"Nostril_{sgn}", (0.24, 0.2, 0.1), (sgn * 0.42, SNOUT_FRONT + 0.3, 0.13), mat=M_DARK)

    # Yeux : blanc, iris ambre lumineux, pupille (ronde chez le bébé, fendue ensuite) et reflets
    for sgn in (-1, 1):
        ex, ey, ez = sgn * 0.97, -0.38, 0.12
        hb(f"EyeWhite_{sgn}", (0.1, EYE[0], EYE[1]), (ex, ey, ez), mat=M_WHITE)
        hb(f"Iris_{sgn}", (0.08, EYE[2], EYE[3]), (ex + sgn * 0.04, ey - 0.03, ez - 0.02), mat=M_IRIS)
        hb(f"Pupil_{sgn}", (0.07, EYE[4], EYE[5]), (ex + sgn * 0.08, ey - 0.04, ez - 0.03), mat=M_BLACK)
        if IS_BEBE:
            hb(f"Glint_{sgn}", (0.06, 0.18, 0.2), (ex + sgn * 0.11, ey - 0.17, ez + 0.2), mat=M_WHITE)
            hb(f"Glint2_{sgn}", (0.06, 0.09, 0.09), (ex + sgn * 0.11, ey + 0.1, ez - 0.2), mat=M_WHITE)
        # sourcil d'écorce : plat chez le bébé, incliné et sévère ensuite
        hb(f"Brow_{sgn}", (0.24, EYE[0] + 0.3, 0.24), (sgn * 0.93, ey - 0.05, ez + EYE[1] / 2 + 0.12),
           rot=(BROW_TILT, 0, sgn * -6), mat=M_BARK2, bevel=0.02)

    # Crocs (ado : 2 par côté ; adulte : 3 par côté + crocs du bas)
    for sgn in (-1, 1):
        for f in range(FANGS):
            fy = SNOUT_FRONT + 0.35 + f * 0.45
            shard(f"{P}Fang_{sgn}_{f}", 0.18 * hs, 0.18 * hs, (0.34 + 0.06 * FANGS) * hs, hv((sgn * 0.55, fy, -0.68)),
                  (0, 0.05, -1), M_FANG, H, up=(1, 0, 0))
            if IS_ADULTE and f < 2:
                shard(f"{P}FangLow_{sgn}_{f}", 0.14 * hs, 0.14 * hs, 0.3 * hs,
                      hv((sgn * 0.45, fy + 0.25, -0.75 - JAW_OPEN * 0.02)), (0, 0.05, 1), M_FANG, H, up=(1, 0, 0))

    # Cornes d'écorce vers l'arrière (bébé : petits blocs), bague dorée à l'adulte
    for sgn in (-1, 1):
        if IS_BEBE:
            hb(f"Horn_{sgn}", (0.36, 0.36, 0.42), (sgn * 0.62, 0.3, 0.95), rot=(-15, sgn * 10, 0), mat=M_BARK)
            hb(f"HornTip_{sgn}", (0.22, 0.22, 0.2), (sgn * 0.64, 0.36, 1.2), rot=(-15, sgn * 10, 0), mat=M_BARK2)
        else:
            L = HORN_L
            pts = [(sgn * 0.7, 0.25, 0.6), (sgn * 0.95, 0.5, 0.6 + 0.45 * L), (sgn * 1.05, 0.5 + 0.55 * L, 0.6 + 0.8 * L),
                   (sgn * 1.0, 0.5 + 1.05 * L, 0.6 + 0.95 * L)]
            tchain(f"{P}Horn_{sgn}", [hv(p) for p in pts], 0.36 * hs, 0.18 * hs, M_BARK, H)
            tip_dir = Vector(pts[3]) - Vector(pts[2])
            shard(f"{P}HornTip_{sgn}", 0.22 * hs, 0.22 * hs, 0.55 * hs * L, hv(pts[3]), tip_dir, M_BARK2, H)
            if GOLD:
                B(f"{P}HornRing_{sgn}", hv((0.44, 0.44, 0.1)), hv(pts[1]),
                  basis(Vector(pts[1]) - Vector(pts[0]), (1, 0, 0)), M_GOLD, H)
            # petite feuille au bout de la corne
            leaf(f"{P}HornLeaf_{sgn}", hv(pts[2]), (sgn * 0.5, 0.5, 0.8), 0.9 * hs, 0.25 * hs, M_LEAF2, H, droop=0.2)

    # TOUFFE DE FEUILLES sur le crâne : éventail de feuilles qui partent vers le haut et l'arrière
    for c in range(TUFT_N):
        f = (c - (TUFT_N - 1) / 2) / max(1, (TUFT_N - 1) / 2)          # -1 .. 1
        d = Vector((f * 0.95, 0.5 + 0.2 * abs(f), 1.0 - 0.25 * abs(f)))
        L = TUFT_L * (1.0 - 0.28 * abs(f)) * random.uniform(0.9, 1.1)
        leaf(f"{P}Tuft_{c}", hv((f * 0.5, 0.12 + 0.06 * abs(f), 0.78)), d, L * hs, 0.42 * hs * (1 - 0.2 * abs(f)),
             LEAVES[c % 3], H, droop=0.32, up=(0, 1, 0), rib=RIBS)
    for c in range(TUFT_N // 2):                                       # rang intérieur, plus court et plus clair
        f = (c - (TUFT_N // 2 - 1) / 2) / max(1, (TUFT_N // 2) / 2)
        leaf(f"{P}TuftIn_{c}", hv((f * 0.3, -0.1, 0.8)), (f * 0.5, 0.15, 1.0), TUFT_L * 0.6 * hs, 0.3 * hs, M_LEAF2, H,
             droop=0.15, up=(0, 1, 0))

    # Feuilles de joue (des "oreilles" vertes pointées vers l'arrière) et petites feuilles de menton
    for sgn in (-1, 1):
        for c in range(CHEEK_N):
            leaf(f"{P}Cheek_{sgn}_{c}", hv((sgn * 0.88, 0.15 + c * 0.28, -0.3 - c * 0.18)),
                 (sgn * (0.7 + 0.1 * c), 1.0, -0.15 - 0.25 * c), (0.95 - 0.12 * c) * hs, 0.26 * hs, LEAVES[(c + 1) % 3], H,
                 droop=0.1, up=(0, 0, 1))

    # Fleurs : une sur le front (rose pour la centrale, orange pour les latérales), 2 de plus à l'adulte
    flower(P + "Flower", hv((0.0, -0.1, 0.98)), (0.1, -0.2, 1.0), 0.5 * hs, H, M_FLO_P if k == 1 else M_FLO_O)
    if FLOWER_HEAD2:
        for sgn in (-1, 1):
            flower(f"{P}FlowerS_{sgn}", hv((sgn * 0.62, 0.45, 0.9)), (sgn * 0.5, 0.0, 1.0), 0.32 * hs, H,
                   M_FLO_O if k == 1 else M_FLO_P, petals=5)

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_head(H, k + 1, HEAD_SCALE * hd[3])

# ----------------------------------------------------------
# 10. CORPS : torse et bassin biseautés, ventre en plaques, plastron, carapace d'écorce,
#     lianes entrecroisées en spirale, écailles-feuilles sur les flancs, fleurs, cous en courbe Catmull-Rom
# ----------------------------------------------------------
B("Body_Chest", (BW * 1.05, TL * 0.56, BH), (0, -TL * 0.2, ZC), None, M_BODY, body_root, bevel=0.14 * SC)
B("Body_Pelvis", (BW * 0.95, TL * 0.5, BH * 0.92), (0, TL * 0.25, ZC - 0.04 * BH), None, M_BODY, body_root, bevel=0.14 * SC)
B("Body_Waist", (BW * 0.9, TL * 0.3, BH * 0.86), (0, 0, ZC - 0.02 * BH), None, M_BODY2, body_root)

# Plaques de ventre vert clair bien séparées
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.84
    B(f"Body_Belly_{i}", (BW * 0.72, pl, 0.26 * SC), (0, y, ZC - BH * 0.47 - 0.06 * SC), mat=M_BELLY, parent=body_root)

# Poitrail : plastron vert clair, à bord doré et gemme de sève (Épique) à partir de l'ado
PY = -TL * 0.48 - 0.1 * SC
if IS_BEBE:
    B("Body_ChestBand", (BW * 0.84, 0.3 * SC, BH * 0.5), (0, PY, ZC - BH * 0.12), mat=M_BELLY, parent=body_root, bevel=0.05 * SC)
    for sgn in (-1, 1):
        B(f"Body_ChestStud_{sgn}", (0.18 * SC, 0.1 * SC, 0.18 * SC), (sgn * BW * 0.3, PY - 0.17 * SC, ZC - BH * 0.12),
          mat=M_GOLD, parent=body_root)
else:
    for r in range(3):
        B(f"Body_Plastron_{r}", (BW * (0.72 - 0.1 * r), 0.28 * SC, BH * 0.22), (0, PY, ZC + BH * (0.12 - 0.25 * r)),
          mat=M_BELLY, parent=body_root)
    B("Body_PlastronRim", (BW * 0.8, 0.2 * SC, 0.12 * SC), (0, PY + 0.06 * SC, ZC + BH * 0.27), mat=M_GOLD, parent=body_root)
    B("Body_GemSet", (0.55 * SC, 0.2 * SC, 0.55 * SC), (0, PY - 0.12 * SC, ZC - BH * 0.06), rot=(0, 45, 0), mat=M_GOLD,
      parent=body_root)
    crystal("Body_Gem", 0.24 * SC, 0.1 * SC, 0.22 * SC, (0, PY - 0.18 * SC, ZC - BH * 0.06), (0, -1, 0), M_SAP, body_root)

# Épaules musclées (ado et adulte) : blocs en wedge
if not IS_BEBE:
    for sgn in (-1, 1):
        wedge(f"Body_Shoulder_{sgn}", (BW * 0.42, TL * 0.36, BH * 0.62),
              (sgn * BW * 0.42, -TL * 0.3, ZC + BH * 0.2), (0, sgn * 12, 0), M_BODY2, body_root,
              top_x=0.7, top_y=0.75, bevel=0.06 * SC)

# CARAPACE D'ÉCORCE sur le dos : rangées de plaques (centre + 2 côtés inclinés) qui se chevauchent, feuilles entre elles
for c in range(CARA_N):
    y = -TL * 0.38 + (TL * 0.8) * c / max(1, CARA_N - 1)
    wdt = BW * (0.62 - 0.05 * abs(c / max(1, CARA_N - 1) - 0.4))
    zt = ZC + BH * 0.5
    mt = pick([M_BARK, M_BARK2, M_BARK], None)
    B(f"Body_Bark_{c}", (wdt * 0.5, TL * 0.8 / CARA_N * 1.25, 0.26 * SC), (0, y, zt + 0.07 * SC), (-4, 0, 0), mt, body_root,
      bevel=0.04 * SC)
    for sgn in (-1, 1):
        B(f"Body_BarkS_{c}_{sgn}", (wdt * 0.36, TL * 0.8 / CARA_N * 1.2, 0.24 * SC),
          (sgn * wdt * 0.4, y + 0.04, zt - 0.1 * SC), (0, sgn * 24, 0), pick([M_BARK, M_BARK2]), body_root)
    h = CREST_H * (1.0 - 0.35 * abs(c / max(1, CARA_N - 1) - 0.3))
    leaf(f"Body_CrestLeaf_{c}", (0, y + 0.1, zt + 0.1 * SC), (0, 0.45, 1.0), h, 0.34 * SC, LEAVES[c % 3], body_root,
         droop=0.3, up=(1, 0, 0), rib=RIBS)
    if c % 2 == 0:
        for sgn in (-1, 1):
            leaf(f"Body_BackLeaf_{c}_{sgn}", (sgn * wdt * 0.55, y, zt - 0.1 * SC), (sgn * 1.0, 0.5, 0.6), h * 0.6,
                 0.26 * SC, LEAVES[(c + 1) % 3], body_root, droop=0.3, up=(0, 1, 0))

# Écailles-feuilles en quinconce sur les flancs (le dos des écailles se soulève vers l'arrière)
for sgn in (-1, 1):
    for rr in range(SCALE_ROWS):
        for cc in range(SCALE_COLS):
            y = -TL * 0.42 + (TL * 0.86) * (cc + 0.5 * (rr % 2) + 0.5) / SCALE_COLS
            z = ZC + BH * (0.3 - 0.62 * (rr + 0.5) / SCALE_ROWS)
            xw = BW * (0.525 if y < -TL * 0.02 else 0.48) + 0.02
            leaf(f"Body_Scale_{sgn}_{rr}_{cc}", (sgn * xw, y - 0.18 * SC, z), (sgn * 0.25, 1.0, -0.12), 0.62 * SC, 0.26 * SC,
                 pick([M_BODY2, M_BODY3, M_LEAF3]), body_root, droop=0.0, up=(sgn, 0, 0), t=0.05 * SC)

# LIANES ENTRECROISÉES : deux spirales de sens opposés autour du torse, avec petites feuilles et fleurs
def vine_wrap(name, y0, y1, turns, phase, sgn_turn, th, mat=M_VINE, leaf_every=3, flowers=()):
    seg = max(6, int(turns * VINE_SEG))
    pts, nrm = [], []
    for i in range(seg + 1):
        t = i / seg
        a = phase + sgn_turn * 2 * math.pi * turns * t
        ca, sa = math.cos(a), math.sin(a)
        wy = y0 + (y1 - y0) * t
        hw = BW * (0.525 if wy < -TL * 0.02 else 0.48) * 1.03
        x = hw * math.copysign(abs(ca) ** 0.5, ca)
        z = ZC + BH * 0.5 * 1.03 * math.copysign(abs(sa) ** 0.5, sa) - 0.02 * BH
        pts.append(Vector((x, wy, z)))
        nrm.append(Vector((ca, 0, sa)).normalized())
    for i in range(seg):
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, body_root, up=(0, 1, 0), depth=th * 0.9)
        if i % leaf_every == 1 and nrm[i].z > -0.5:
            leaf(f"{name}_Leaf_{i}", pts[i], nrm[i] * 1.0 + Vector((0, 0.5, 0)), 0.8 * SC, 0.26 * SC,
                 LEAVES[i % 3], body_root, droop=0.35, up=(0, 1, 0))
    for fi in flowers:
        i = min(seg, int(fi * seg))
        flower(f"{name}_Flower_{i}", pts[i] + nrm[i] * 0.1 * SC, nrm[i], FLOWER_R * SC, body_root,
               M_FLO_O if i % 2 else M_FLO_P)

vine_wrap("Body_VineA", -TL * 0.46, TL * 0.46, VINE_TURNS, 0.4, 1, VINE_TH * SC, flowers=VINE_FLOWERS_A)
vine_wrap("Body_VineB", -TL * 0.46, TL * 0.46, VINE_TURNS, 0.4 + math.pi, -1, VINE_TH * SC * 0.9, flowers=VINE_FLOWERS_B)

# Fleurs sur les flancs et le dos
for i in range(FLOWER_N):
    a = random.uniform(-0.9, 0.9)
    fy = -TL * 0.3 + (TL * 0.65) * (i + 0.5) / FLOWER_N
    sgn = -1 if i % 2 else 1
    flower(f"Body_Flower_{i}", (sgn * BW * 0.34, fy, ZC + BH * 0.53), (sgn * 0.4, 0.0, 1.0), FLOWER_R * SC * 1.1, body_root,
           M_FLO_O if i % 2 else M_FLO_P)

# Motifs (swirls) : petites spirales claires posées sur les flancs
for sgn in (-1, 1):
    for c in range(SWIRLS):
        cy = -TL * 0.2 + c * TL * 0.38
        cz = ZC + BH * 0.02
        cxs = sgn * (BW * 0.5 + 0.04)
        pts = []
        for j in range(6):
            ang = j * 0.95
            rr_ = (0.62 - 0.07 * j) * SC
            pts.append(Vector((cxs, cy + rr_ * math.cos(ang), cz + rr_ * math.sin(ang))))
        for j in range(5):
            bar(f"Body_Swirl_{sgn}_{c}_{j}", pts[j], pts[j + 1], 0.09 * SC, M_LEAF2, body_root, up=(1, 0, 0), depth=0.05)

# Cous : une courbe Catmull-Rom par tête, rééchantillonnée à pas constant
NECK_RADIUS_KEYS = [(0.0, NECK_R[0]), (1.0, NECK_R[1])]

def build_neck(k, H, hsc, hx):
    """Cou n° k : de la base sur le poitrail jusqu'à la base du crâne de la tête H."""
    hs = HEAD_SCALE * hsc
    end = H.matrix_basis @ Vector((0, 0.5 * hs, -0.55 * hs))           # base du crâne
    base = Vector((hx * 0.42, -TL * 0.36, ZC + BH * 0.22))
    ctrl = [base,
            base.lerp(end, 0.35) + Vector((hx * 0.05, 0.25 * NECK_CURVE, 0)),
            base.lerp(end, 0.7) + Vector((0, -0.15 * NECK_CURVE, 0)),
            end]
    spine = resample(sample_curve(ctrl), (end - base).length / NECK_N)
    n = len(spine) - 1
    for i in range(n):
        p1, p2 = spine[i], spine[i + 1]
        Ln = (p2 - p1).length
        mid = (p1 + p2) / 2
        s = (i + 0.5) / n
        r = keyed(NECK_RADIUS_KEYS, s) * (0.6 + 0.4 * hsc)
        t, d, side = frame(p2 - p1)
        R = seg_matrix(t, d, side)
        nm = f"Body_Neck{k}_{i}"
        B(nm + "_Inner", (2 * r * 0.8, Ln * 1.3, 2 * r * 0.8), mid, R, M_DARK, body_root)           # jointure sombre
        B(nm + "_Front", (2 * r, Ln * 0.86, 2 * r * 0.95), mid - d * 0.06 * r, R, M_BODY, body_root)   # bloc de cou
        B(nm + "_Throat", (2 * r * 0.6, Ln * 0.8, r * 0.3), mid - d * r * 1.0, R, M_BELLY, body_root)  # gorge claire
        B(nm + "_Back", (2 * r * 1.12, Ln * 0.92, r * 0.85), mid + d * r * 0.62, R, pick([M_BARK, M_BARK2]), body_root)
        for sgn in (-1, 1):
            B(f"{nm}_Side_{sgn}", (r * 0.3, Ln * 0.8, r * 0.75), mid + side * sgn * r * 0.95 + d * r * 0.5, R,
              pick(BODY_MATS, BODY_W), body_root)
        # liane enroulée : bague inclinée à chaque articulation
        sgn_t = 1 if i % 2 == 0 else -1
        B(nm + "_Vine", (2 * r * 1.14, Ln * 0.2, 2 * r * 1.1), p1, R @ Euler((0, math.radians(sgn_t * 16), 0)).to_matrix(),
          M_VINE, body_root)
        leaf(nm + "_Leaf", mid + d * r * 1.0, d + t * 0.9, (0.9 + 0.5 * (1 - s)) * SC * NECK_LEAF_K, 0.3 * SC, LEAVES[(i + k) % 3],
             body_root, droop=0.3, up=tuple(side))
        if NECK_FLOWERS and i % 2 == 1:
            flower(nm + "_Flower", mid + side * r * 1.0, side, 0.4 * SC, body_root, M_FLO_O if k % 2 else M_FLO_P)

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_neck(k + 1, H, hd[3], hd[0])

# ----------------------------------------------------------
# 11. PATTES : cuisse / épaule en wedge, tibia, bracelet d'écorce à bord doré, liane, pied,
#     3 doigts + 3 griffes ivoire, feuille de genou
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.22)
SHIN_H = LEG_H * 0.45

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.28)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.5
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.6 if hind else 1.4), thigh_h),
          (x + sgn * 0.06 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.12), mat=pick(BODY_MATS, BODY_W), parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.07 * SC)
    sy = y + (th * 0.12 if hind else 0)
    B(f"{name}_Shin", (th * 0.92, th * 0.98, SHIN_H + 0.2), (x, sy, FOOT_H + SHIN_H / 2), None, M_BODY, legs_root, bevel=0.05 * SC)
    # Bracelet d'écorce, bord doré (Épique) et liane qui s'enroule
    bh_ = SHIN_H * BRACER_K
    bz = FOOT_H + SHIN_H * 0.55
    box(f"{name}_Bracer", (th * 1.12, th * 1.18, bh_), (x, sy, bz), mat=M_BARK, parent=legs_root, bevel=0.03 * SC)
    B(f"{name}_BracerRim", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz + bh_ / 2), mat=M_GOLD, parent=legs_root)
    if not IS_BEBE:
        B(f"{name}_BracerRim2", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz - bh_ / 2), mat=M_GOLD, parent=legs_root)
        crystal(f"{name}_BracerGem", 0.14 * SC, 0.08 * SC, 0.12 * SC, (x, sy - th * 0.6, bz), (0, -1, 0), M_SAP, legs_root)
        B(f"{name}_Vine", (th * 1.0, th * 1.04, 0.12 * SC), (x, sy, bz + SHIN_H * 0.3), (0, 0, 14 * sgn), M_VINE, legs_root)
    # Feuille de genou
    leaf(f"{name}_KneeLeaf", (x + sgn * th * 0.5, sy + (th * 0.3 if hind else -th * 0.1), FOOT_H + SHIN_H + 0.1),
         (sgn * 0.9, 0.5 if hind else -0.4, 0.5), th * 1.0, th * 0.28, LEAVES[(int(y * 10)) % 3], legs_root, droop=0.5, up=(0, 1, 0))
    # Pied plat + 3 doigts + 3 griffes
    fy = sy - th * 0.3
    box(f"{name}_Foot", (th * 1.15, th * 1.75, FOOT_H), (x, fy, FOOT_H / 2), mat=M_BODY2, parent=legs_root, bevel=0.05 * SC)
    toe_y = fy - th * 0.88 - th * 0.12
    for c in (-1, 0, 1):
        B(f"{name}_Toe_{c}", (th * 0.3, th * 0.5, FOOT_H * 0.7), (x + c * th * 0.34, toe_y, FOOT_H * 0.35), mat=M_BODY3,
          parent=legs_root)
        shard(f"{name}_Claw_{c}", th * 0.22, th * 0.18, th * CLAW_K, (x + c * th * 0.34, toe_y - th * 0.2, FOOT_H * 0.3),
              (c * 0.12, -1, -0.25), M_CLAW, legs_root)
    # Feuilles sur l'arrière de la cuisse
    for c in range(THIGH_LEAVES):
        leaf(f"{name}_ThighLeaf_{c}", (x + sgn * th * 0.45, y + th * (0.25 + 0.3 * c), FOOT_H + SHIN_H + thigh_h * (0.85 - 0.22 * c)),
             (sgn * 0.6, 0.9, 0.35), (0.9 - 0.1 * c) * SC, 0.28 * SC, LEAVES[c % 3], legs_root, droop=0.35, up=(0, 0, 1))

LEG_TH_F, LEG_TH_R = BW * 0.4, BW * 0.46
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.3, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : la Liane n'a pas d'ailes (hydre de forêt, sans ailes). Pas de WINGS_ROOT.
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe Catmull-Rom, segments verts, ventre clair, crête d'écorce, lianes et feuilles,
#     bout en grappe de grandes feuilles autour d'un bourgeon de fleur
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.25, -0.45, 0.0), (0.5, -0.75, 0.25), (0.75, -0.7, 0.35), (1.0, -0.35, 0.15)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.6)))
TAIL_RADIUS_KEYS = [(0.0, BW * 0.38), (0.35, BW * 0.31), (0.7, BW * 0.21), (1.0, BW * 0.12)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_RADIUS_KEYS, s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.12, 2 * r * 0.95), mid, R, pick(BODY_MATS, BODY_W), tail_root,
        bevel=(0.04 * SC if i < 3 else 0))
    if s < 0.8:
        B(f"Tail_Belly_{i}", (2 * r * 0.75, Ln * 0.75, 0.2 * SC), mid - d * (r * 0.97), R, M_BELLY, tail_root)
    if i % 2 == 0:
        B(f"Tail_Bark_{i}", (2 * r * 0.8, Ln * 0.95, 0.22 * SC), mid + d * (r * 0.95), R, pick([M_BARK, M_BARK2]), tail_root)
    leaf(f"Tail_Leaf_{i}", mid + d * r * 0.95, d + t * 0.8, 0.55 * SC + r * 1.1, 0.2 * SC + r * 0.25, LEAVES[i % 3], tail_root,
         droop=0.3, up=tuple(side))
    if TAIL_VINE and i % 2 == 1:
        B(f"Tail_Vine_{i}", (2 * r * 1.1, Ln * 0.2, 2 * r * 1.08), mid, R @ Euler((0, math.radians(14 * (1 if i % 4 == 1 else -1)), 0)).to_matrix(),
          M_VINE, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipBase", (BW * 0.24, 0.35 * SC, BW * 0.22), tip, seg_matrix(tt_, td_, ts_), M_BARK2, tail_root)
crystal("Tail_TipBud", BW * 0.08, TAIL_TIP * 0.35, TAIL_TIP * 0.4, tip, tt_, M_SAP, tail_root)
for c in range(TAIL_TIP_LEAVES):
    a = c * 2 * math.pi / TAIL_TIP_LEAVES
    off = td_ * math.cos(a) + ts_ * math.sin(a)
    leaf(f"Tail_TipLeaf_{c}", tip + off * BW * 0.03, tt_ + off * 0.7, TAIL_TIP, TAIL_TIP * 0.3, LEAVES[c % 3], tail_root,
         droop=0.2, up=tuple(off.cross(tt_)), rib=RIBS)
if TAIL_FLOWER:
    flower("Tail_Flower", tip + td_ * 0.25 * TAIL_TIP + tt_ * 0.3 * TAIL_TIP, td_ + tt_ * 0.5, 0.5 * SC, tail_root, M_FLO_P)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Épique : fleurs orange et roses lumineuses, yeux ambre, sève lumineuse (gemmes, bourgeon de queue),
#     ornements dorés (plastron, bracelets, bagues de cornes). FX : spores lumineuses, pétales et feuilles flottants.
# ----------------------------------------------------------
# Grappes de sève lumineuse plantées dans la carapace du dos
for c in range(SAP_N):
    y = -TL * 0.3 + (TL * 0.65) * (c + 0.5) / SAP_N
    sgn = 1 if c % 2 else -1
    crystal(f"Body_SapCrystal_{c}", 0.2 * SC, 0.3 * SC, 0.5 * SC, (sgn * BW * 0.22, y, ZC + BH * 0.52),
            (sgn * 0.3, 0.1, 1.0), M_SAP, body_root)

if ADD_FLOATING_FX:
    top_z = NECK_TOP.z + HEAD_SCALE * 1.8
    for c in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.5 + 1.0), random.uniform(-TL * 0.9, TL * 0.6 + TAIL_L * 0.3),
                    random.uniform(LEG_H * 0.8, top_z)))
        rot = (random.uniform(0, 90), random.uniform(0, 90), random.uniform(0, 90))
        m = c % 3
        if m == 0:      # spore lumineuse
            prism(f"FX_Spore_{c}", FX_SIZE * 0.45, FX_SIZE * 0.9, p, (random.uniform(-1, 1), random.uniform(-1, 1), 1), M_SAP,
                  master, sides=4)
        elif m == 1:    # pétale rose qui flotte
            leaf(f"FX_Petal_{c}", p, (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.3, 0.6)), FX_SIZE * 2.0,
                 FX_SIZE * 0.8, M_FLO_P if c % 2 else M_FLO_O, master, droop=0.0)
        else:           # feuille qui tombe
            leaf(f"FX_Leaf_{c}", p, (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.6, 0.3)), FX_SIZE * 2.6,
                 FX_SIZE * 0.7, LEAVES[c % 3], master, droop=0.2)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
