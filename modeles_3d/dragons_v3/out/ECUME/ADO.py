import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Écume · Ado
#  Commun · Eau · Aquatique · monde 3
#  - Ado élancé : cou plus long en col de cygne, museau plus long, yeux en amande avec sourcils, 2 petits crocs
#  - Signe distinctif : grandes NAGEOIRES-OREILLES en éventail (5 rayons) + taches d'écume, épines bleues sur le front
#  - Corps sur courbe Catmull-Rom, ventre en plaques, écailles en quinconce, crête-nageoire dorsale continue
#  - Nageoires pectorales en éventail (5 rayons) comme des ailes, pattes-palettes palmées, queue de poisson en V
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1117)            # même dragon à chaque exécution
TAG = "ECUME_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
#    Bleu eau (corps), bleu profond (dos, écailles), blanc (ventre, écume), turquoise (nageoires).
#    Commun : aucune émission, sauf une lueur faible dans l'iris.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      "#3FA0E0", 0.42)   # corps principal, bleu eau
M_SCALE  = get_mat("BodyScale", "#2879C2", 0.45)   # écailles, plaques du dos, genouillères
M_DARK   = get_mat("BodyDark",  "#1B4C84", 0.50)   # sourcils, ligne de bouche
M_BELLY  = get_mat("Belly",     "#F2F6F8", 0.50)   # ventre en plaques, plastron, mâchoire
M_FOAM   = get_mat("Foam",      "#FFFFFF", 0.35)   # taches d'écume (signe distinctif)
M_FIN    = get_mat("Fin",       "#36D6CF", 0.30, alpha=0.85)   # membranes turquoise translucides
M_FIN2   = get_mat("FinLight",  "#A6EEF4", 0.25, alpha=0.85)   # membranes claires nacrées
M_RAY    = get_mat("FinRay",    "#1E8CC8", 0.40)   # rayons des nageoires
M_HORN   = get_mat("Horn",      "#CDEFF6", 0.40)   # cornes-épines nacrées
M_CLAW   = get_mat("Claw",      "#F2F6F8", 0.35)   # griffes, crocs
M_WHITE  = get_mat("EyeWhite",  "#F4F8FA", 0.30)
M_IRIS   = get_mat("Iris",      "#1E86E0", 0.25, emission="#3FB8FF", strength=1.2)  # seule lueur (yeux)
M_BLACK  = get_mat("Black",     "#0A0F14", 0.30)   # pupilles
M_NOSE   = get_mat("Nostril",   "#123A5C", 0.50)   # narines
M_BUBBLE = get_mat("Bubble",    "#D6F6FF", 0.10, alpha=0.55)   # bulles flottantes (FX)
FINS = [M_FIN, M_FIN2]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
R = 1.05             # rayon du torse
TORSO_L = 4.0        # longueur du torse (poitrail -> hanches)
LEG_H = 1.15         # hauteur du dessous du ventre
NECK_L = 2.1         # longueur du cou
NECK_RISE = 0.8      # 0 = cou horizontal, 1 = cou vertical
NECK_R = (0.66, 0.84)  # rayon du cou (sous la tête, à la base)
HEAD_SCALE = 1.1
SNOUT_K = 1.1        # longueur du museau
FANGS = 2            # crocs par côté
EAR_L = 2.2          # longueur des nageoires-oreilles (signe distinctif)
EAR_RAYS = 5
CREST_H = 1.0        # hauteur de la crête-nageoire du crâne
CREST_RAYS = 4
HORN_L = 0.85        # longueur des cornes-épines
HEAD_SPINES = 3      # épines bleues du front, par côté
CHEEK_N = 2          # petites nageoires de joue par côté
STEP = 0.7          # pas des segments du corps
DORSAL_H = 0.95      # hauteur max de la crête-nageoire dorsale
NECK_MANE = 0        # nageoires de crinière par segment de cou et par côté
FLANK_ROWS = 2       # rangées d'écailles sur les flancs
FOAM_N = 7          # taches d'écume sur le torse
LEG_TH = 0.62        # épaisseur des pattes
PADDLE = 1.05        # taille des pieds-palettes
ELBOW_FIN = True     # petite nageoire au coude
PEC_SPAN = 3.3       # longueur du grand rayon des nageoires pectorales
PEC_RAYS = 5
PELV_SPAN = 1.6
PELV_RAYS = 3
TAIL_L = 6.0
TAIL_STEP = 0.85
TAIL_RISE = 1.1      # remontée du bout de la queue
CAUDAL_L = 2.2       # taille des lobes de la nageoire caudale
CAUDAL_RAYS = 4
TAIL_FINLETS = 1     # paires de petites nageoires sur la queue
FX_N = 4             # bulles flottantes
FX_SIZE = 0.28

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = R / 1.2                                     # échelle des petits détails
ZC = LEG_H + R * 0.92                            # hauteur du centre du torse
TL = TORSO_L
CHEST = Vector((0, -TL * 0.42, ZC + R * 0.12))   # poitrail (bas du cou)
HIP = Vector((0, TL * 0.5, ZC - R * 0.08))       # hanches (début de la queue)
NECK_DIR = Vector((0, -(1 - NECK_RISE), NECK_RISE)).normalized()
NECK_TOP = CHEST + NECK_DIR * NECK_L + Vector((0, -R * 0.25, 0))
HEAD_POS = NECK_TOP + Vector((0, -0.2, 0.5)) * HEAD_SCALE
HEAD_PITCH = 4                                   # degrés : la tête regarde un peu vers le bas

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)        # ici : les nageoires pectorales et pelviennes
H = head_root

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def fin_leaf(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Petite nageoire en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def fan_fin(name, root, d0, d1, n, L0, L1, parent, ray_th, memb_t, bulge=0.12, tip_spike=0.0):
    """NAGEOIRE EN ÉVENTAIL (plaques avec rayons) : n rayons qui partent de 'root',
    du rayon d'attaque d0 (le plus long, L0) au rayon de fuite d1 (L1).
    Entre deux rayons : une membrane translucide (turquoise / claire en alternance).
    Les rayons dépassent un peu de la membrane : bord festonné. Renvoie les pointes."""
    root, d0, d1 = Vector(root), Vector(d0).normalized(), Vector(d1).normalized()
    nrm = d0.cross(d1)
    up = tuple(nrm.normalized()) if nrm.length > 1e-4 else (0, 0, 1)
    tips = []
    for k in range(n):
        f = k / max(1, n - 1)
        dk = d0.lerp(d1, f).normalized()
        Lk = L0 + (L1 - L0) * f + L0 * bulge * math.sin(math.pi * f)
        tip = root + dk * Lk
        bar(f"{name}_Ray_{k}", root, tip, ray_th * (1.35 if k == 0 else 1.0), M_RAY, parent, up=up,
            depth=ray_th * 0.75)
        tips.append(tip)
    for k in range(n - 1):
        a, b = root.lerp(tips[k], 0.93), root.lerp(tips[k + 1], 0.93)
        plate(f"{name}_Memb_{k}", [root, a, b], memb_t, FINS[k % 2], parent)
    if tip_spike > 0:
        shard(f"{name}_TipSpike", ray_th * 2.2, ray_th * 1.4, tip_spike, tips[0], tips[0] - root, M_HORN, parent, up=up)
    return tips

def comb_fin(name, bases, tops, parent, ray_th, memb_t, ray_every=1):
    """NAGEOIRE EN PEIGNE (crête dorsale, crête du crâne) : une rangée de rayons
    (base -> sommet) reliés par des membranes quadrangulaires."""
    for k in range(len(bases)):
        if k % ray_every == 0 or k == len(bases) - 1:
            tip = bases[k] + (tops[k] - bases[k]) * 1.1
            bar(f"{name}_Ray_{k}", bases[k], tip, ray_th, M_RAY, parent, up=(1, 0, 0), depth=ray_th * 0.75)
    for k in range(len(bases) - 1):
        plate(f"{name}_Memb_{k}", [bases[k], bases[k + 1], tops[k + 1], tops[k]], memb_t, FINS[k % 2], parent)

def foam(name, center, normal, size, parent, sat=None):
    """TACHE D'ÉCUME : disque blanc hexagonal posé sur la peau (+ 1 ou 2 petites gouttes)."""
    center, normal = Vector(center), Vector(normal).normalized()
    prism(name, size, 0.07 * SC, center, direction=normal, mat=M_FOAM, parent=parent, sides=6)
    if sat:
        for j, off in enumerate(sat):
            prism(f"{name}_s{j}", size * 0.45, 0.07 * SC, center + Vector(off), direction=normal,
                  mat=M_FOAM, parent=parent, sides=6)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
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

# Crâne arrondi, museau plat et large (museau de poisson-dragon), arête claire,
# mâchoire blanche distincte, ligne de bouche
SKULL = (1.8, 1.7, 1.5)
hwedge("Skull", SKULL, (0, 0, 0), mat=M_BODY, top_x=0.84, top_y=0.84, bevel=0.12)
hwedge("Snout", (1.5, 1.65 * SNOUT_K, 0.82), (0, -0.7 - 0.82 * SNOUT_K, -0.3), mat=M_BODY,
       top_x=0.86, top_y=0.92, shift_y=-0.05, bevel=0.09)
hbox("SnoutBridge", (0.75, 1.35 * SNOUT_K, 0.12), (0, -0.62 - 0.78 * SNOUT_K, 0.12), mat=M_SCALE)
hbox("Jaw", (1.3, 1.55 * SNOUT_K, 0.32), (0, -0.66 - 0.77 * SNOUT_K, -0.74), mat=M_BELLY, bevel=0.04)
hbox("Chin", (1.1, 0.7, 0.3), (0, -0.25, -0.7), mat=M_BELLY)
hbox("MouthLine", (1.53, 1.6 * SNOUT_K, 0.05), (0, -0.7 - 0.82 * SNOUT_K, -0.68), mat=M_DARK)
SNOUT_FRONT = -0.7 - 1.65 * SNOUT_K

# Narines sur le dessus du museau
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.24, 0.06), (sgn * 0.38, SNOUT_FRONT + 0.3, 0.1), mat=M_NOSE)

# Yeux : blanc, iris bleu (lueur faible), pupille (ronde + reflets pour le bébé, fendue ensuite)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.9, 0.95, 0.7, 0.8, 0.4, 0.55
elif IS_ADO:
    EW, EH, IW, IH, PW, PH = 0.66, 0.6, 0.48, 0.5, 0.12, 0.46
else:
    EW, EH, IW, IH, PW, PH = 0.6, 0.55, 0.42, 0.46, 0.1, 0.42
for sgn in (-1, 1):
    ey, ez = -0.3, 0.12
    ex = SKULL[0] / 2 * 0.99
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * ex, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * (ex + 0.04), ey - 0.03, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * (ex + 0.08), ey - 0.05, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.22), (sgn * (ex + 0.11), ey - 0.18, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * (ex + 0.11), ey + 0.14, ez - 0.2), mat=M_WHITE)
    else:
        # sourcils (ado : obliques ; adulte : plus épais et plus sévères)
        hbox(f"Brow_{sgn}", (0.16, EW + 0.3, 0.2 if IS_ADO else 0.26),
             (sgn * (ex + 0.02), ey - 0.06, ez + EH / 2 + 0.12), rot=(10 if IS_ADO else 17, 0, 0),
             mat=M_DARK)

# Crocs blancs (ado : 2 par côté, petits ; adulte : 3 par côté)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.4 + k * 0.42
        hshard(f"Fang_{sgn}_{k}", 0.18, 0.18, 0.24 + 0.05 * FANGS, (sgn * 0.6, fy, -0.62), (0, 0.05, -1),
               M_CLAW, up=(1, 0, 0))

# SIGNE DISTINCTIF : grandes NAGEOIRES-OREILLES translucides en éventail
for sgn in (-1, 1):
    fan_fin(f"Head_EarFin_{sgn}", hv((sgn * 0.8, 0.45, 0.3)), (sgn * 0.5, 0.05, 1.0), (sgn * 0.55, 1.0, -0.2),
            EAR_RAYS, EAR_L * HS, EAR_L * 0.62 * HS, H, ray_th=0.1 * HS, memb_t=0.05 * HS, bulge=0.15)

# Crête-nageoire sur le dessus du crâne (peigne de rayons)
bases, tops = [], []
for k in range(CREST_RAYS):
    f = k / max(1, CREST_RAYS - 1)
    b = hv((0, -0.45 + 1.15 * f, SKULL[2] / 2 * 0.95))
    h = CREST_H * (0.75 + 0.35 * math.sin(math.pi * (0.25 + 0.75 * f))) * HS
    bases.append(b)
    tops.append(b + Vector((0, 0.55, 1.0)).normalized() * h)
comb_fin("Head_Crest", bases, tops, H, ray_th=0.09 * HS, memb_t=0.05 * HS)

# Cornes-épines nacrées vers l'arrière (bébé : courtes ; adulte : longues)
for sgn in (-1, 1):
    p0 = Vector((sgn * 0.45, 0.25, 0.68))
    p1 = p0 + Vector((sgn * 0.12, 0.5, 0.45)) * (HORN_L / 1.0)
    p2 = p1 + Vector((sgn * 0.05, 0.6, 0.12)) * (HORN_L / 1.0)
    bar(f"Head_Horn_{sgn}_0", hv(p0), hv(p1), 0.24 * HS, M_HORN, H)
    shard(f"Head_Horn_{sgn}_1", 0.24 * HS, 0.24 * HS, (p2 - p1).length * HS * 1.1, hv(p1), p2 - p1, M_HORN, H)

# Épines bleues du front (ado / adulte)
for sgn in (-1, 1):
    for k in range(HEAD_SPINES):
        hshard(f"Spine_{sgn}_{k}", 0.22, 0.08, 0.5 - 0.06 * k, (sgn * (0.25 + 0.08 * k), -0.55 + 0.32 * k, 0.66),
               (sgn * 0.35, 1, 0.55), M_SCALE, up=(sgn, 0, 0.3))

# Petites nageoires de joue (pointes turquoise vers l'arrière)
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        fin_leaf(f"Head_Cheek_{sgn}_{k}", hv((sgn * 0.8, -0.05 + k * 0.22, -0.45 - k * 0.1)),
                 (sgn * 0.8, 0.9, -0.35 - 0.2 * k), (0.75 - 0.12 * k) * HS, 0.35 * HS, FINS[k % 2], H,
                 up=(0, 0, 1), t=0.05 * HS)

# Taches d'écume sur la tête (mêmes aux 3 stades)
for sgn in (-1, 1):
    foam(f"Head_Foam_{sgn}", hv((sgn * 0.52, 0.35, SKULL[2] / 2 * 0.98)), (sgn * 0.25, 0, 1), 0.17 * HS, H,
         sat=[tuple(hv((sgn * 0.12, 0.25, 0.0)))])
    foam(f"Head_FoamSnout_{sgn}", hv((sgn * 0.71, SNOUT_FRONT + 0.75, -0.25)), (sgn, 0, 0), 0.12 * HS, H)

# ----------------------------------------------------------
# 10. CORPS : courbe Catmull-Rom (cou + torse), segments, ventre en plaques, dos, écailles,
#     crinière de nageoires du cou, crête-nageoire dorsale, taches d'écume
# ----------------------------------------------------------
# Points de contrôle du cou et du torse (de la tête vers les hanches) : à retoucher ici
BODY_CTRL = [
    NECK_TOP,
    CHEST.lerp(NECK_TOP, 0.5) + Vector((0, NECK_L * 0.08, 0)),   # cou en col de cygne
    CHEST,
    Vector((0, -TL * 0.08, ZC + R * 0.06)),
    Vector((0, TL * 0.24, ZC)),
    HIP,
]
SPINE = resample(sample_curve(BODY_CTRL), STEP)
N = len(SPINE) - 1
cum = [0.0]
for i in range(N):
    cum.append(cum[-1] + (SPINE[i + 1] - SPINE[i]).length)
i_chest = min(range(len(SPINE)), key=lambda j: (SPINE[j] - CHEST).length)
S_CHEST = cum[i_chest] / cum[-1]                  # fraction de la courbe où commence le torse
# Rayon le long de la courbe (s = 0 sous la tête, s = 1 aux hanches)
BODY_R_KEYS = [(0.0, NECK_R[0]), (S_CHEST * 0.75, NECK_R[1]), (S_CHEST + (1 - S_CHEST) * 0.18, R),
               (S_CHEST + (1 - S_CHEST) * 0.65, R * 0.97), (1.0, R * 0.86)]
# Hauteur de la crête-nageoire dorsale le long du corps
DORSAL_KEYS = [(0.0, DORSAL_H * 0.35), (S_CHEST, DORSAL_H * 0.75), (S_CHEST + (1 - S_CHEST) * 0.4, DORSAL_H),
               (1.0, DORSAL_H * 0.7)]

def seg_info(spine, i, keys):
    p1, p2 = spine[i], spine[i + 1]
    s = (i + 0.5) / (len(spine) - 1)
    t, d, side = frame(p2 - p1)
    return (p1 + p2) / 2, (p2 - p1).length, s, keyed(keys, s), t, d, side

dorsal_b, dorsal_t = [], []
torso_segs = []
for i in range(N):
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    Rm = seg_matrix(t, d, side)
    neck = s < S_CHEST
    box(f"Body_Seg_{i}", (2 * r * 1.06, Ln * 1.32, 2 * r * 0.94), mid, Rm, M_BODY, body_root, bevel=0.07 * SC)
    # plaques de ventre blanches bien séparées
    if s > S_CHEST * 0.2:
        B(f"Body_Belly_{i}", (2 * r * 0.78, Ln * 0.78, 0.2 * SC), mid - d * (r * 0.93), Rm, M_BELLY, body_root)
    # plaque de dos bleu profond (dos sombre / ventre clair, comme un poisson)
    Rt = Rm @ Euler((math.radians(-6), 0, 0)).to_matrix()
    B(f"Body_Back_{i}", (2 * r * 0.72, Ln * 0.95, 0.16 * SC), mid + d * (r * 0.94), Rt, M_SCALE, body_root)
    # crinière de nageoires turquoise sur les côtés du cou (ado / adulte)
    if neck:
        fade = 1.0 - s / max(1e-3, S_CHEST)
        for sgn in (-1, 1):
            for k in range(NECK_MANE):
                fin_leaf(f"Body_NeckFin_{i}_{sgn}_{k}", mid + side * sgn * r * 0.9 + d * r * (0.35 - 0.45 * k),
                         side * sgn * (0.7 - 0.2 * k) + t * 0.9 + d * 0.35, (0.9 + 0.7 * fade - 0.15 * k) * SC,
                         0.42 * SC, FINS[(i + k) % 2], body_root, up=tuple(side * sgn * 0.8 + d * 0.6), t=0.06 * SC)
    else:
        torso_segs.append(i)
    # base de la crête dorsale
    if s > S_CHEST * 0.35:
        h = keyed(DORSAL_KEYS, s) * SC
        bpt = SPINE[i] + frame(SPINE[min(i + 1, N)] - SPINE[i])[1] * (keyed(BODY_R_KEYS, i / N) * 0.85)
        dd = frame(SPINE[min(i + 1, N)] - SPINE[i])
        dorsal_b.append(bpt)
        dorsal_t.append(bpt + (dd[1] * 1.0 + dd[0] * 0.5).normalized() * h)

comb_fin("Body_Dorsal", dorsal_b, dorsal_t, body_root, ray_th=0.1 * SC, memb_t=0.06 * SC)

# Écailles en quinconce sur les flancs du torse (pointe vers l'arrière)
for i in torso_segs:
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    for sgn in (-1, 1):
        for row in range(FLANK_ROWS):
            if (i + row) % 2:
                continue
            shard(f"Body_Scale_{i}_{sgn}_{row}", 0.6 * SC, 0.08 * SC, 0.7 * SC,
                  mid + side * sgn * (r * 1.04) + d * r * (0.45 - 0.42 * row) - t * Ln * 0.2,
                  side * sgn * 0.22 + t, pick([M_SCALE, M_BODY, M_SCALE]), body_root, up=(sgn, 0, 0))

# Plastron blanc sur le poitrail
mid, Ln, s, r, t, d, side = seg_info(SPINE, i_chest, BODY_R_KEYS)
box("Body_Plastron", (r * 1.45, 0.3 * SC, r * 1.05), CHEST + Vector((0, -r * 0.8, -r * 0.35)), (18, 0, 0),
    M_BELLY, body_root, bevel=0.05 * SC)

# Taches d'écume sur les flancs et le dos (signe distinctif)
for k in range(FOAM_N):
    i = random.choice(torso_segs)
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    sgn = (-1, 1)[k % 2]
    if k % 4 == 3:   # sur le haut du dos, à côté de la plaque sombre
        c = mid + d * (r * 0.95) + side * sgn * r * random.uniform(0.8, 0.95) + t * random.uniform(-0.2, 0.2) * Ln
        foam(f"Body_Foam_{k}", c, d, random.uniform(0.2, 0.28) * SC, body_root)
    else:            # sur le flanc
        c = mid + side * sgn * (r * 1.09) + d * r * random.uniform(-0.45, 0.65) + t * random.uniform(-0.3, 0.3) * Ln
        sat = [tuple(t * 0.42 * SC + d * 0.15 * SC)] if random.random() < 0.5 else None
        foam(f"Body_Foam_{k}", c, side * sgn, random.uniform(0.26, 0.36) * SC, body_root, sat=sat)

# ----------------------------------------------------------
# 11. PATTES EN PALETTES : épaule / cuisse en wedge, bras, genouillère, avant-bras,
#     pied large et plat, 3 doigts palmés (membrane) + 3 griffes blanches
# ----------------------------------------------------------
FOOT_H = 0.3 * SC

def leg(name, sgn, y, th, hind):
    x = sgn * R * 0.8
    pad = PADDLE * (1.15 if hind else 1.0)
    # masse de l'épaule / de la cuisse, collée au flanc
    wedge(f"{name}_Thigh", (th * 1.3, th * (1.7 if hind else 1.45), R * 1.25),
          (x + sgn * th * 0.12, y, ZC - R * 0.3), mat=M_BODY, parent=legs_root,
          top_x=0.8, top_y=0.75, bevel=0.08 * SC)
    top = Vector((x + sgn * th * 0.15, y, ZC - R * 0.55))
    knee = Vector((x + sgn * th * 0.32, y + (th * 0.35 if hind else -th * 0.1), FOOT_H + LEG_H * 0.5))
    ankle = Vector((x + sgn * th * 0.42, y + (-th * 0.05 if hind else -th * 0.3), FOOT_H * 0.9))
    link(f"{name}_Upper", top, knee, th * 0.95, M_BODY, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0.05 * SC, depth=th * 1.05)
    link(f"{name}_Lower", knee, ankle, th * 0.75, M_BODY, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0, depth=th * 0.8)
    B(f"{name}_Knee", (th * 0.9, th * 0.5, th * 0.55), knee + Vector((0, -th * 0.38, 0)), mat=M_SCALE,
      parent=legs_root)
    # pied-palette
    F = Vector((ankle.x, ankle.y - th * 0.3, FOOT_H / 2))
    box(f"{name}_Foot", (th * 1.25 * pad, th * 1.2 * pad, FOOT_H), F, mat=M_BODY, parent=legs_root, bevel=0.05 * SC)
    bases, tips = [], []
    for k in (-1, 0, 1):
        b = F + Vector((k * th * 0.38 * pad, -th * 0.45 * pad, -FOOT_H * 0.2))
        tp = F + Vector((k * th * 0.85 * pad, -th * 1.3 * pad, -FOOT_H * 0.3))
        bar(f"{name}_Toe_{k}", b, tp, th * 0.24, M_SCALE, legs_root, up=(0, 0, 1), depth=FOOT_H * 0.55)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.15, th * 0.42, tp - Vector((0, th * 0.05, 0)),
              (k * 0.3, -1, -0.25), M_CLAW, legs_root)
        bases.append(b); tips.append(tp)
    for k in range(2):   # membranes entre les doigts (pattes palmées)
        plate(f"{name}_Web_{k}", [bases[k], tips[k] + (bases[k] - tips[k]) * 0.12,
                                  tips[k + 1] + (bases[k + 1] - tips[k + 1]) * 0.12, bases[k + 1]],
              0.05 * SC, M_FIN2, legs_root)
    # petite nageoire de coude (ado / adulte)
    if ELBOW_FIN:
        fan_fin(f"{name}_ElbowFin", knee + Vector((sgn * th * 0.2, th * 0.25, 0)), (sgn * 0.5, 0.6, 0.6),
                (sgn * 0.3, 1.0, -0.2), 3, th * 1.2, th * 0.8, legs_root, ray_th=0.07 * SC, memb_t=0.04 * SC)

LEG_Y_F, LEG_Y_R = -TL * 0.3, TL * 0.3
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, LEG_Y_F, LEG_TH, False)
    leg(f"Legs_Back_{sgn}", sgn, LEG_Y_R, LEG_TH * 1.1, True)

# ----------------------------------------------------------
# 12. NAGEOIRES (à la place des ailes) : grandes pectorales en éventail sur les épaules,
#     petites pelviennes sur les hanches. Plaques translucides + rayons bleus.
# ----------------------------------------------------------
for sgn in (-1, 1):
    proot = Vector((sgn * R * 0.72, -TL * 0.2, ZC + R * 0.62))
    B(f"Wings_PecBase_{sgn}", (0.55 * SC, 0.9 * SC, 0.45 * SC), proot, rot=(0, sgn * 30, 0), mat=M_BODY,
      parent=wings_root)
    fan_fin(f"Wings_Pec_{sgn}", proot, (sgn * 0.6, -0.08, 1.0), (sgn * 0.45, 1.0, 0.1), PEC_RAYS,
            PEC_SPAN, PEC_SPAN * 0.5, wings_root, ray_th=0.13 * SC, memb_t=0.06 * SC, bulge=0.1,
            tip_spike=(0.5 * SC if not IS_BEBE else 0.0))
    vroot = Vector((sgn * R * 0.85, TL * 0.4, ZC + R * 0.35))
    fan_fin(f"Wings_Pelv_{sgn}", vroot, (sgn * 0.9, 0.15, 0.55), (sgn * 0.35, 1.0, 0.0), PELV_RAYS,
            PELV_SPAN, PELV_SPAN * 0.6, wings_root, ray_th=0.1 * SC, memb_t=0.05 * SC)

# ----------------------------------------------------------
# 13. QUEUE DE POISSON : courbe Catmull-Rom, segments aplatis sur les côtés vers le bout,
#     ventre en plaques, crête-nageoire qui continue, petites nageoires latérales,
#     nageoire caudale en V (deux lobes à rayons)
# ----------------------------------------------------------
TAIL_CTRL = [
    HIP,
    HIP + Vector((0, TAIL_L * 0.3, -R * 0.32)),
    HIP + Vector((0, TAIL_L * 0.62, -R * 0.22)),
    HIP + Vector((0, TAIL_L * 0.85, TAIL_RISE * 0.45)),
    HIP + Vector((0, TAIL_L, TAIL_RISE)),
]
TAIL_R_KEYS = [(0.0, R * 0.86), (0.35, R * 0.6), (0.7, R * 0.36), (1.0, R * 0.2)]
TAIL_DORSAL = [(0.0, DORSAL_H * 0.7), (0.5, DORSAL_H * 0.5), (0.85, DORSAL_H * 0.3), (1.0, DORSAL_H * 0.2)]
TSP = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TSP) - 1
tb, tt_ = [], []
for i in range(TN):
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    Rm = seg_matrix(t, d, side)
    wk = 1.04 - 0.3 * s            # la queue s'aplatit sur les côtés vers le bout
    hk = 0.94 + 0.2 * s
    box(f"Tail_Seg_{i}", (2 * r * wk, Ln * 1.32, 2 * r * hk), mid, Rm, M_BODY, tail_root,
        bevel=(0.06 * SC if s < 0.3 else 0))
    B(f"Tail_Back_{i}", (2 * r * wk * 0.68, Ln * 0.95, 0.14 * SC), mid + d * (r * hk), Rm, M_SCALE, tail_root)
    if s < 0.72:
        B(f"Tail_Belly_{i}", (2 * r * wk * 0.75, Ln * 0.78, 0.18 * SC), mid - d * (r * hk * 0.98), Rm, M_BELLY, tail_root)
    if i % 3 == 0 and s < 0.75:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.07 * SC, r * 0.95, mid + side * sgn * (r * wk * 0.98),
                  side * sgn * 0.25 + t, pick([M_SCALE, M_BODY]), tail_root, up=(sgn, 0, 0))
    if i % 3 == 1 and s < 0.8:
        sgn = (-1, 1)[(i // 3) % 2]
        foam(f"Tail_Foam_{i}", mid + side * sgn * (r * wk * 1.03) + d * r * 0.2, side * sgn, 0.24 * SC, tail_root,
             sat=[tuple(t * 0.28 * SC - d * 0.1 * SC)])
    if s < 0.88:
        h = keyed(TAIL_DORSAL, s) * SC
        bpt = TSP[i] + d * r * hk * 0.85
        tb.append(bpt)
        tt_.append(bpt + (d + t * 0.55).normalized() * h)
comb_fin("Tail_Dorsal", tb, tt_, tail_root, ray_th=0.09 * SC, memb_t=0.05 * SC)

# Petites nageoires latérales le long de la queue
for k in range(TAIL_FINLETS):
    s = 0.35 + 0.25 * k
    i = min(TN - 1, int(s * TN))
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    for sgn in (-1, 1):
        fan_fin(f"Tail_Finlet_{k}_{sgn}", mid + side * sgn * r * 0.8, side * sgn * 0.9 + t * 0.3 + d * 0.2,
                side * sgn * 0.3 + t, 3, r * 2.0, r * 1.3, tail_root, ray_th=0.07 * SC, memb_t=0.04 * SC)

# Nageoire caudale en V : lobe haut et lobe bas, avec une encoche au milieu
tip = TSP[-1]
ct, cd, cs = frame(TSP[-1] - TSP[-2])
B("Tail_Collar", (R * 0.42, 0.35 * SC, R * 0.55), tip - ct * 0.1 * SC, seg_matrix(ct, cd, cs), M_SCALE, tail_root)
froot = tip + ct * 0.05 * SC
fan_fin("Tail_CaudalTop", froot, ct * 0.45 + cd * 1.0, ct * 1.0 + cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L, CAUDAL_L * 0.55, tail_root, ray_th=0.12 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.35 * SC if IS_ADULTE else 0.0))
fan_fin("Tail_CaudalBot", froot, ct * 0.55 - cd * 1.0, ct * 1.0 - cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L * 0.85, CAUDAL_L * 0.5, tail_root, ray_th=0.12 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.3 * SC if IS_ADULTE else 0.0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre et lisible, 3 familles de couleurs (bleu, blanc, turquoise),
#     aucune émission (sauf la lueur faible de l'iris). Détails : écailles, ventre en plaques,
#     griffes, crête-nageoire simple. Un seul signe fort : les grandes nageoires-oreilles.
#     FX : quelques bulles d'eau qui flottent autour du dragon.
# ----------------------------------------------------------
def bubble_mesh(r):
    """Bulle low-poly : octaèdre (6 sommets, 8 triangles)."""
    v = [(r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r)]
    f = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    return mesh_from("bubble", v, f)

if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 1.5
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (R * 1.6 + PEC_SPAN * 0.6),
                    random.uniform(-TL * 0.9, TL * 0.5 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 1.2, top_z)))
        place(f"FX_Bubble_{k}", bubble_mesh(FX_SIZE * random.uniform(0.6, 1.3)), M_BUBBLE, p,
              (random.uniform(0, 45), random.uniform(0, 45), random.uniform(0, 45)), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
