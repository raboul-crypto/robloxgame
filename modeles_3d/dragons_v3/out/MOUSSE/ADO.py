import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Mousse · Ado
#  Commun · Eau · Aquatique · monde 4
#  - Ado lourd et musclé : museau plus long, yeux sérieux avec sourcils, 2 petits crocs, cou un peu plus long
#  - Signe distinctif : COLLERETTE D'ÉCUME blanche en facettes autour du cou + BULLES translucides alignées sur le dos et la queue
#  - Corps en coque de bateau : très large et bas, planches de flanc bleu ardoise, ventre crème en plaques, cou court
#  - Collerette plus fournie, 2 rangées de planches de flanc, nageoires-oreilles à 2 facettes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4421)            # même dragon à chaque exécution
TAG = "MOUSSE_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 4500          # budget de triangles de ce stade et de cette rareté
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
#    Bleu ardoise (corps), ardoise sombre (planches, genoux), crème (ventre), blanc d'écume (collerette).
#    Commun : aucune émission, sauf une lueur faible dans l'iris.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      "#6396BD", 0.55)   # corps principal, bleu ardoise
M_SCALE  = get_mat("BodyScale", "#4A7BA3", 0.55)   # planches sombres de la coque, genouillères
M_SCALEB = get_mat("BodyScaleB", "#8DB3D0", 0.55)  # planches claires, joues
M_DARK   = get_mat("BodyDark",  "#3A5C78", 0.60)   # sourcils, ligne de bouche, dos
M_BELLY  = get_mat("Belly",     "#EDE6D3", 0.55)   # ventre en plaques, plastron, mâchoire
M_FOAM   = get_mat("Foam",      "#F7F9FA", 0.35)   # collerette d'écume (signe distinctif)
M_FOAM2  = get_mat("FoamBlue",  "#CFEAF5", 0.35)   # écume bleutée (deuxième rangée)
M_FIN    = get_mat("Fin",       "#6E93AD", 0.45)   # nageoires épaisses (faces extérieures)
M_FINL   = get_mat("FinLight",  "#A9C6D8", 0.40)   # nageoires épaisses (faces claires)
M_RAY    = get_mat("FinRay",    "#3F6F94", 0.50)   # rayons épais des nageoires
M_HORN   = get_mat("Horn",      "#F7F9FA", 0.45)   # cornes courtes et crêtes
M_CLAW   = get_mat("Claw",      "#A9ADB3", 0.40)   # griffes et crocs gris
M_WHITE  = get_mat("EyeWhite",  "#F2F2F2", 0.30)
M_IRIS   = get_mat("Iris",      "#2A68A0", 0.25, emission="#3A8FD0", strength=1.2)  # seule lueur (yeux)
M_BLACK  = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles
M_NOSE   = get_mat("Nostril",   "#243745", 0.55)   # narines
M_BUBBLE = get_mat("Bubble",    "#CFEAF5", 0.10, alpha=0.5)   # bulles translucides (signe distinctif)
PLANKS = [M_SCALE, M_BODY, M_SCALEB]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
R           = 1.4              # rayon du torse
TORSO_L     = 3.7        # longueur du torse
LEG_H       = 1.1           # hauteur du dessous du ventre
NECK_L      = 1.7         # longueur du cou
NECK_RISE   = 0.45     # 0 = cou horizontal, 1 = vertical
NECK_R      = (1.0, 1.25)   # rayon du cou (haut, bas)
HEAD_SCALE  = 1.38    # taille de la tête
SNOUT_K     = 0.95      # longueur du museau
FANGS       = 2             # crocs par côté
EAR_L       = 2.0          # longueur des nageoires-oreilles
EAR_TH      = 0.26        # épaisseur des nageoires-oreilles
HORN_L      = 0.9         # longueur des cornes
RUFF_N      = 11          # pointes d'écume par rangée (collerette)
RUFF_ROWS   = 2       # rangées de la collerette
RUFF_L      = 1.25        # longueur des pointes d'écume
STEP        = 0.8           # pas des segments du corps
PLANK_ROWS  = 2      # rangées de planches sur les flancs
LEG_TH      = 1.0         # épaisseur des pattes
PADDLE      = 1.0        # taille des pieds-palettes
PEC_SPAN    = 4.0       # longueur des pectorales
PEC_RAYS    = 3
TAIL_L      = 3.8         # longueur de la queue
TAIL_STEP   = 0.85
TAIL_RISE   = 1.1
CAUDAL_L    = 2.8
CAUDAL_RAYS = 3
BUB_R       = 0.5          # rayon des bulles dorsales
BUB_EVERY   = 2        # une bulle tous les n segments
FX_N        = 4
FX_SIZE     = 0.35

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Mousse = coque de bateau : corps très large, bas, cou court. Tout est en unités de travail ;
#    finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = R / 1.4                                     # échelle des petits détails
BW = 1.3                                         # le corps est BW fois plus large que haut (coque)
ZC = LEG_H + R * 0.85                            # hauteur du centre du torse
TL = TORSO_L
CHEST = Vector((0, -TL * 0.42, ZC + R * 0.04))   # poitrail (bas du cou)
HIP = Vector((0, TL * 0.5, ZC - R * 0.06))       # hanches (début de la queue)
NECK_DIR = Vector((0, -(1 - NECK_RISE), NECK_RISE)).normalized()
NECK_TOP = CHEST + NECK_DIR * NECK_L
HEAD_POS = NECK_TOP + Vector((0, -0.5, 0.05)) * HEAD_SCALE
HEAD_PITCH = 8                                   # degrés : la tête regarde vers le bas, comme une proue

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)        # ici : les nageoires pectorales et pelviennes
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def bubble_mesh(r):
    """Bulle low-poly : bipyramide à 6 côtés (12 triangles)."""
    v = [(0, 0, r), (0, 0, -r)] + [(r * math.cos(k * math.pi / 3), r * math.sin(k * math.pi / 3), 0) for k in range(6)]
    f = []
    for k in range(6):
        n = (k + 1) % 6
        f.append((0, 2 + k, 2 + n))
        f.append((1, 2 + n, 2 + k))
    return mesh_from("bubble", v, f)

def bubble(name, center, r, parent, rot=None):
    return place(name, bubble_mesh(r), M_BUBBLE, center, rot or (0, 0, random.uniform(0, 60)), parent)

def fat_fin(name, root, d0, d1, n, L0, L1, parent, ray_th, memb_t, mats=None):
    """NAGEOIRE ÉPAISSE : n gros rayons qui partent de 'root' (du rayon d'attaque d0 au rayon de fuite d1),
    reliés par des membranes épaisses. Moins de rayons et bien plus gros que sur une nageoire fine."""
    mats = mats or [M_FIN, M_FINL]
    root, d0, d1 = Vector(root), Vector(d0).normalized(), Vector(d1).normalized()
    nrm = d0.cross(d1)
    up = tuple(nrm.normalized()) if nrm.length > 1e-4 else (0, 0, 1)
    tips = []
    for k in range(n):
        f = k / max(1, n - 1)
        dk = d0.lerp(d1, f).normalized()
        tip = root + dk * (L0 + (L1 - L0) * f)
        bar(f"{name}_Ray_{k}", root, tip, ray_th * (1.3 if k == 0 else 1.0), M_RAY, parent, up=up, depth=ray_th * 0.9)
        tips.append(tip)
    for k in range(n - 1):
        plate(f"{name}_Memb_{k}", [root, root.lerp(tips[k], 0.95), root.lerp(tips[k + 1], 0.95)], memb_t,
              mats[k % 2], parent)
    return tips

def facet_fin(name, base, direction, length, width, th, parent, up=(0, 0, 1)):
    """NAGEOIRE-OREILLE ÉPAISSE TAILLÉE EN FACETTES : un gros bloc en forme d'aileron de requin
    (plaque épaisse), une plaque claire plus petite posée dessus, et une arête de rayon."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base - fy * 0.1 * length + fx * (-width * 0.25),
           base + fy * length,
           base + fy * 0.3 * length + fx * width,
           base - fy * 0.1 * length + fx * width * 0.6]
    plate(f"{name}_A", pts, th, M_FIN, parent)
    inner = [base + fy * 0.12 * length + fx * width * 0.05, base + fy * 0.8 * length,
             base + fy * 0.34 * length + fx * width * 0.62, base + fy * 0.1 * length + fx * width * 0.4]
    plate(f"{name}_B", inner, th * 1.25, M_FINL, parent)
    bar(f"{name}_Ray", base, base + fy * length * 1.02, th * 0.7, M_RAY, parent, up=tuple(m.col[2]), depth=th * 0.9)

def comb_fin(name, bases, tops, parent, ray_th, memb_t):
    for k in range(len(bases) - 1):
        plate(f"{name}_Memb_{k}", [bases[k], bases[k + 1], tops[k + 1], tops[k]], memb_t, M_FINL if k % 2 else M_FIN, parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Tête de bouledogue : crâne large, museau court et carré, grosses joues, mâchoire crème lourde.
# ----------------------------------------------------------
HS = HEAD_SCALE
def hv(v):
    return Vector(v) * HS

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, tuple(hv(size)), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, tuple(hv(size)), hv(loc), rot, mat, H, top_x, top_y, shift_y * HS, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

SKULL = (2.3, 1.8, 1.55)
hwedge("Skull", SKULL, (0, 0, 0), mat=M_BODY, top_x=0.88, top_y=0.86, bevel=0.14)
hwedge("Snout", (2.0, 1.2 * SNOUT_K, 0.95), (0, -0.7 - 0.6 * SNOUT_K, -0.32), mat=M_BODY, top_x=0.92, top_y=0.95,
       bevel=0.1)
hbox("SnoutBridge", (1.0, 1.0 * SNOUT_K, 0.14), (0, -0.62 - 0.58 * SNOUT_K, 0.18), mat=M_SCALE)
hbox("Jaw", (1.85, 1.15 * SNOUT_K, 0.4), (0, -0.66 - 0.58 * SNOUT_K, -0.82), mat=M_BELLY, bevel=0.05)
hbox("Chin", (1.5, 0.8, 0.4), (0, -0.2, -0.8), mat=M_BELLY)
hbox("MouthLine", (2.03, 1.2 * SNOUT_K, 0.06), (0, -0.7 - 0.6 * SNOUT_K, -0.74), mat=M_DARK)
SNOUT_FRONT = -0.7 - 1.2 * SNOUT_K
# grosses joues en blocs (aspect bouledogue)
for sgn in (-1, 1):
    hwedge(f"Cheek_{sgn}", (0.45, 0.9, 0.6), (sgn * 1.2, 0.05, -0.5), mat=M_SCALEB, top_x=0.7, top_y=0.8, bevel=0.07)
    hbox(f"Nostril_{sgn}", (0.28, 0.3, 0.07), (sgn * 0.55, SNOUT_FRONT + 0.32, 0.0), mat=M_NOSE)
    hbox(f"BrowRidge_{sgn}", (0.9, 0.5, 0.2), (sgn * 0.6, -0.55, 0.72), mat=M_SCALE, bevel=0.05)

# Yeux : blanc, iris bleu foncé (lueur faible), pupille ronde (bébé) puis fendue
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 1.05, 1.1, 0.85, 0.95, 0.46, 0.64
elif IS_ADO:
    EW, EH, IW, IH, PW, PH = 0.62, 0.56, 0.46, 0.48, 0.12, 0.44
else:
    EW, EH, IW, IH, PW, PH = 0.56, 0.5, 0.4, 0.42, 0.1, 0.4
for sgn in (-1, 1):
    ey, ez = -0.4, 0.22
    ex = SKULL[0] / 2 * 0.99
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * ex, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * (ex + 0.04), ey - 0.03, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * (ex + 0.08), ey - 0.05, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.24, 0.24), (sgn * (ex + 0.11), ey - 0.2, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * (ex + 0.11), ey + 0.15, ez - 0.22), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.18, EW + 0.34, 0.2 if IS_ADO else 0.28),
             (sgn * (ex + 0.02), ey - 0.06, ez + EH / 2 + 0.12), rot=(8 if IS_ADO else 14, 0, 0), mat=M_DARK)

# Crocs gris (ado : 2 petits par côté ; adulte : 3). Pas de crocs chez le bébé.
if not IS_BEBE:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.45 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.22, 0.22, 0.26 + 0.05 * FANGS, (sgn * 0.78, fy, -0.68), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# SIGNE DISTINCTIF : nageoires-oreilles ÉPAISSES taillées en facettes (gros ailerons de requin)
for sgn in (-1, 1):
    facet_fin(f"Head_EarFin_{sgn}", hv((sgn * 1.0, 0.5, 0.35)), (sgn * 0.55, 0.45, 0.85), EAR_L * HS, 0.95 * HS * sgn,
              EAR_TH * HS, H, up=(0, 0, 1))
    if EAR_L > 1.6:   # deuxième facette plus petite derrière
        facet_fin(f"Head_EarFin2_{sgn}", hv((sgn * 1.0, 0.7, 0.0)), (sgn * 0.8, 0.8, 0.2), EAR_L * 0.6 * HS,
                  0.6 * HS * sgn, EAR_TH * 0.8 * HS, H, up=(0, 0, 1))

# Cornes courtes et épaisses, crème (bébé : deux moignons)
for sgn in (-1, 1):
    p0 = Vector((sgn * 0.6, 0.15, 0.7))
    p1 = p0 + Vector((sgn * 0.18, 0.35, 0.4)) * HORN_L
    bar(f"Head_Horn_{sgn}_0", hv(p0), hv(p1), 0.34 * HS, M_HORN, H, up=(1, 0, 0))
    shard(f"Head_Horn_{sgn}_1", 0.3 * HS, 0.3 * HS, 0.55 * HORN_L * HS, hv(p1), (sgn * 0.25, 0.6, 0.7), M_HORN, H)

# Petite crête de trois plaques crème sur le crâne (ado / adulte)
if not IS_BEBE:
    for k in range(3):
        hshard(f"Crest_{k}", 0.55, 0.2, 0.6 - 0.1 * k, (0, -0.35 + 0.5 * k, 0.74), (0, 0.55, 1.0), M_HORN, up=(1, 0, 0))

# ----------------------------------------------------------
# 10. CORPS : courbe Catmull-Rom (cou court + torse), segments larges, ventre en plaques,
#     planches de coque sur les flancs, collerette d'écume, bulles dorsales
# ----------------------------------------------------------
BODY_CTRL = [
    NECK_TOP,
    CHEST.lerp(NECK_TOP, 0.5) + Vector((0, 0, NECK_L * 0.06)),
    CHEST,
    Vector((0, -TL * 0.08, ZC + R * 0.03)),
    Vector((0, TL * 0.24, ZC)),
    HIP,
]
SPINE = resample(sample_curve(BODY_CTRL), STEP)
N = len(SPINE) - 1
cum = [0.0]
for i in range(N):
    cum.append(cum[-1] + (SPINE[i + 1] - SPINE[i]).length)
i_chest = min(range(len(SPINE)), key=lambda j: (SPINE[j] - CHEST).length)
S_CHEST = cum[i_chest] / cum[-1]
BODY_R_KEYS = [(0.0, NECK_R[0]), (S_CHEST * 0.75, NECK_R[1]), (S_CHEST + (1 - S_CHEST) * 0.2, R),
               (S_CHEST + (1 - S_CHEST) * 0.65, R * 0.99), (1.0, R * 0.88)]

def seg_info(spine, i, keys):
    p1, p2 = spine[i], spine[i + 1]
    s = (i + 0.5) / (len(spine) - 1)
    t, d, side = frame(p2 - p1)
    return (p1 + p2) / 2, (p2 - p1).length, s, keyed(keys, s), t, d, side

torso_segs = []
bub_spots = []
for i in range(N):
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    Rm = seg_matrix(t, d, side)
    neck = s < S_CHEST
    box(f"Body_Seg_{i}", (2 * r * BW, Ln * 1.32, 2 * r * 0.92), mid, Rm, M_BODY, body_root, bevel=0.09 * SC)
    if s > S_CHEST * 0.2:
        B(f"Body_Belly_{i}", (2 * r * BW * 0.74, Ln * 0.8, 0.22 * SC), mid - d * (r * 0.93 * 0.92), Rm, M_BELLY, body_root)
    Rt = Rm @ Euler((math.radians(-5), 0, 0)).to_matrix()
    B(f"Body_Back_{i}", (2 * r * BW * 0.7, Ln * 0.95, 0.2 * SC), mid + d * (r * 0.92 * 0.97), Rt, M_DARK, body_root)
    if not neck:
        torso_segs.append(i)
    bub_spots.append((i, mid + d * (r * 0.92 * 0.97), d, t, r))

# Planches de coque sur les flancs (écailles bleu ardoise épaisses en plaques horizontales)
for i in torso_segs:
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    for sgn in (-1, 1):
        for row in range(PLANK_ROWS):
            zoff = r * (0.42 - 0.44 * row)
            B(f"Body_Plank_{i}_{sgn}_{row}", (0.2 * SC, Ln * 0.92, r * 0.4),
              mid + side * sgn * (r * BW * 0.985) + d * zoff, seg_matrix(t, d, side),
              PLANKS[(i + row) % 3], body_root)

# Plastron crème sur le poitrail
mid, Ln, s, r, t, d, side = seg_info(SPINE, i_chest, BODY_R_KEYS)
box("Body_Plastron", (r * BW * 1.3, 0.34 * SC, r * 1.1), CHEST + Vector((0, -r * 0.88, -r * 0.3)), (14, 0, 0),
    M_BELLY, body_root, bevel=0.06 * SC)

# SIGNE DISTINCTIF : COLLERETTE D'ÉCUME en facettes autour du cou (2 rangées de pointes + blocs)
i_r = max(1, min(N - 1, int(N * S_CHEST * 0.55)))
cmid, cLn, cs, cr, ct, cd, cside = seg_info(SPINE, i_r, BODY_R_KEYS)
for row in range(RUFF_ROWS):
    n = RUFF_N if row == 0 else RUFF_N - 2
    for k in range(n):
        a = 2 * math.pi * (k + 0.5 * row) / n
        radial = cside * math.cos(a) + cd * math.sin(a)
        rr = cr * (BW if abs(math.cos(a)) > 0.5 else 1.0) * (1.02 + 0.2 * row)
        L = 1.05 * RUFF_L * (1.0 - 0.18 * row) * (0.8 + 0.3 * abs(math.sin(2 * a + row)))
        pos = cmid + radial * rr + ct * (0.25 * row)
        shard(f"Body_Ruff_{row}_{k}", 0.85 * SC, 0.3 * SC, L, pos, radial * 0.9 + ct * 0.55 - cd * 0.0,
              M_FOAM if (k + row) % 2 == 0 else M_FOAM2, body_root, up=tuple(ct))

# ----------------------------------------------------------
# 11. PATTES : piliers épais (quasi des piles de quai), cuisse en wedge, genouillère,
#     grand pied palmé et plat, 3 doigts + 3 griffes grises
# ----------------------------------------------------------
FOOT_H = 0.32 * SC

def leg(name, sgn, y, th, hind):
    x = sgn * R * BW * 0.8
    pad = PADDLE * (1.1 if hind else 1.0)
    wedge(f"{name}_Thigh", (th * 1.45, th * (1.9 if hind else 1.6), R * 1.2),
          (x + sgn * th * 0.1, y, ZC - R * 0.3), mat=M_BODY, parent=legs_root, top_x=0.82, top_y=0.78, bevel=0.1 * SC)
    top = Vector((x + sgn * th * 0.12, y, ZC - R * 0.5))
    knee = Vector((x + sgn * th * 0.25, y + (th * 0.2 if hind else -th * 0.05), FOOT_H + LEG_H * 0.5))
    ankle = Vector((x + sgn * th * 0.3, y + (0 if hind else -th * 0.12), FOOT_H * 0.9))
    link(f"{name}_Upper", top, knee, th * 1.05, M_BODY, legs_root, up=(0, 1, 0), extra=th * 0.4, bevel=0.06 * SC,
         depth=th * 1.15)
    link(f"{name}_Lower", knee, ankle, th * 0.9, M_SCALE, legs_root, up=(0, 1, 0), extra=th * 0.4, bevel=0, depth=th * 0.95)
    B(f"{name}_Knee", (th * 1.1, th * 0.5, th * 0.6), knee + Vector((0, -th * 0.45, 0)), mat=M_DARK, parent=legs_root)
    F = Vector((ankle.x, ankle.y - th * 0.3, FOOT_H / 2))
    box(f"{name}_Foot", (th * 1.5 * pad, th * 1.35 * pad, FOOT_H), F, mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    bases, tips = [], []
    for k in (-1, 0, 1):
        b = F + Vector((k * th * 0.45 * pad, -th * 0.5 * pad, -FOOT_H * 0.15))
        tp = F + Vector((k * th * 0.75 * pad, -th * 1.1 * pad, -FOOT_H * 0.25))
        bar(f"{name}_Toe_{k}", b, tp, th * 0.3, M_SCALE, legs_root, up=(0, 0, 1), depth=FOOT_H * 0.6)
        shard(f"{name}_Claw_{k}", th * 0.24, th * 0.17, th * 0.4, tp - Vector((0, th * 0.05, 0)), (k * 0.25, -1, -0.2),
              M_CLAW, legs_root)
        bases.append(b); tips.append(tp)
    for k in range(2):
        plate(f"{name}_Web_{k}", [bases[k], tips[k] + (bases[k] - tips[k]) * 0.1,
                                  tips[k + 1] + (bases[k + 1] - tips[k + 1]) * 0.1, bases[k + 1]], 0.06 * SC, M_FIN,
              legs_root)

LEG_Y_F, LEG_Y_R = -TL * 0.3, TL * 0.32
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, LEG_Y_F, LEG_TH, False)
    leg(f"Legs_Back_{sgn}", sgn, LEG_Y_R, LEG_TH * 1.05, True)

# ----------------------------------------------------------
# 12. NAGEOIRES (à la place des ailes) : grosses pectorales-palettes épaisses sur les flancs,
#     tombantes vers l'arrière comme des rames, petites pelviennes
# ----------------------------------------------------------
for sgn in (-1, 1):
    proot = Vector((sgn * R * BW * 0.95, -TL * 0.22, ZC + R * 0.15))
    B(f"Wings_PecBase_{sgn}", (0.7 * SC, 1.1 * SC, 0.7 * SC), proot, rot=(0, sgn * 20, 0), mat=M_SCALE, parent=wings_root,
      bevel=0.06 * SC)
    fat_fin(f"Wings_Pec_{sgn}", proot, (sgn * 1.0, -0.15, 0.25), (sgn * 0.55, 1.0, -0.15), PEC_RAYS, PEC_SPAN,
            PEC_SPAN * 0.62, wings_root, ray_th=0.24 * SC, memb_t=0.14 * SC)
    vroot = Vector((sgn * R * BW * 0.95, TL * 0.42, ZC + R * 0.1))
    fat_fin(f"Wings_Pelv_{sgn}", vroot, (sgn * 1.0, 0.1, 0.2), (sgn * 0.4, 1.0, -0.1), 2, PEC_SPAN * 0.5,
            PEC_SPAN * 0.35, wings_root, ray_th=0.2 * SC, memb_t=0.12 * SC)

# ----------------------------------------------------------
# 13. QUEUE DE POISSON LARGE ET PLATE : courbe Catmull-Rom, segments larges qui s'aplatissent,
#     bulles sur la crête, énorme nageoire caudale en V à gros rayons
# ----------------------------------------------------------
TAIL_CTRL = [
    HIP,
    HIP + Vector((0, TAIL_L * 0.3, -R * 0.3)),
    HIP + Vector((0, TAIL_L * 0.62, -R * 0.35)),
    HIP + Vector((0, TAIL_L * 0.85, TAIL_RISE * 0.4)),
    HIP + Vector((0, TAIL_L, TAIL_RISE)),
]
TAIL_R_KEYS = [(0.0, R * 0.88), (0.35, R * 0.7), (0.7, R * 0.48), (1.0, R * 0.3)]
TSP = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TSP) - 1
for i in range(TN):
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    Rm = seg_matrix(t, d, side)
    wk = BW * (1.0 - 0.08 * s)        # reste large : queue plate
    hk = 0.92 - 0.3 * s
    box(f"Tail_Seg_{i}", (2 * r * wk, Ln * 1.32, 2 * r * hk), mid, Rm, M_BODY, tail_root, bevel=(0.07 * SC if s < 0.3 else 0))
    B(f"Tail_Back_{i}", (2 * r * wk * 0.68, Ln * 0.95, 0.16 * SC), mid + d * (r * hk), Rm, M_DARK, tail_root)
    if s < 0.75:
        B(f"Tail_Belly_{i}", (2 * r * wk * 0.72, Ln * 0.8, 0.2 * SC), mid - d * (r * hk * 0.98), Rm, M_BELLY, tail_root)
    if (i % 2 == 0 or not IS_BEBE) and s < 0.75:
        for sgn in (-1, 1):
            B(f"Tail_Plank_{i}_{sgn}", (0.18 * SC, Ln * 1.7, r * hk * 0.7), mid + side * sgn * (r * wk * 0.985), Rm,
              PLANKS[(i // 2) % 3], tail_root)
    bub_spots.append((N + i, mid + d * (r * hk), d, t, r))

tip = TSP[-1]
ct, cd, cs = frame(TSP[-1] - TSP[-2])
B("Tail_Collar", (R * 0.6, 0.4 * SC, R * 0.4), tip - ct * 0.1 * SC, seg_matrix(ct, cd, cs), M_DARK, tail_root)
froot = tip + ct * 0.05 * SC
fat_fin("Tail_CaudalTop", froot, ct * 0.35 + cd * 1.0, ct * 1.0 + cd * 0.25, CAUDAL_RAYS, CAUDAL_L, CAUDAL_L * 0.6,
        tail_root, ray_th=0.26 * SC, memb_t=0.14 * SC)
fat_fin("Tail_CaudalBot", froot, ct * 0.35 - cd * 1.0, ct * 1.0 - cd * 0.25, CAUDAL_RAYS, CAUDAL_L * 0.9,
        CAUDAL_L * 0.55, tail_root, ray_th=0.26 * SC, memb_t=0.14 * SC)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) : BULLES TRANSLUCIDES alignées sur le dos et la queue (signe
#     distinctif, au-dessus d'une petite pointe crème), aucune émission sauf l'iris, FX : bulles flottantes
# ----------------------------------------------------------
for (idx, p, d, t, r) in bub_spots:
    if idx % BUB_EVERY:
        continue
    f = 1.0 - 0.45 * (idx / (N + TN))
    br = BUB_R * f
    shard(f"Body_DorsalShard_{idx}", 0.5 * SC, 0.2 * SC, br * 1.9, p - d * 0.05, d + t * 0.35, M_FOAM, body_root, up=(1, 0, 0))
    bubble(f"Body_Bubble_{idx}", p + d * br * 0.95 + t * br * 0.2, br, body_root)
    if not IS_BEBE and idx % 2 == 0:   # petite bulle satellite posée à côté de la grosse
        sd = (-1, 1)[(idx // 2) % 2]
        bubble(f"Body_BubbleS_{idx}", p + d * br * 0.55 + t * br * 0.9 + Vector(frame(t)[2]) * sd * br * 0.85, br * 0.45, body_root)

if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 2.0
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (R * BW + PEC_SPAN * 0.9),
                    random.uniform(-TL * 0.9, TL * 0.5 + TAIL_L * 0.6),
                    random.uniform(LEG_H * 1.3, top_z)))
        place(f"FX_Bubble_{k}", bubble_mesh(FX_SIZE * random.uniform(0.6, 1.3)), M_BUBBLE, p,
              (random.uniform(0, 45), random.uniform(0, 45), random.uniform(0, 45)), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
