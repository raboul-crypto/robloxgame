import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Perle · Ado
#  Épique · Eau · Aquatique · monde 3
#  - Ado élancé : cou allongé, yeux en amande avec sourcils, petits crocs, museau plus long
#  - Perle facettée sertie sur le front avec diadème doré, nageoires-oreilles irisées à 6 rayons, coquille nacrée à deux niveaux
#  - Nageoires pectorales à 6 rayons, pattes turquoise à bracelets dorés, plastron doré, perles-lueurs, veines, bulles et perles flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3309)            # même dragon à chaque exécution
TAG = "PERLE_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 8500          # budget de triangles de ce stade et de cette rareté
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
#    Blanc nacré (corps), turquoise (pattes, écailles), nageoires irisées (turquoise / lavande / rose),
#    or (ornements), perle et perles-lueurs émissives (Épique : strength 2 à 2.5).
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      "#F4F0EA", 0.30, 0.12)   # corps blanc nacré
M_SCALE  = get_mat("BodyScale", "#3FBCD0", 0.40)   # écailles et plaques turquoise
M_LEG    = get_mat("Leg",       "#2FB0C8", 0.40)   # pattes turquoise
M_DARK   = get_mat("BodyDark",  "#26799F", 0.45)   # sourcils, ligne de bouche
M_BELLY  = get_mat("Belly",     "#FFFBF3", 0.40)   # ventre en plaques, mâchoire
M_FIN    = get_mat("Fin",       "#5CD0E0", 0.25, alpha=0.85)   # membranes turquoise irisées
M_FIN2   = get_mat("FinLight",  "#C9B8F4", 0.20, alpha=0.85)   # membranes lavande irisées
M_FIN3   = get_mat("FinRose",   "#F7CDE4", 0.20, alpha=0.85)   # membranes rose nacré
M_RAY    = get_mat("FinRay",    "#2E8EBA", 0.40)   # rayons des nageoires
M_HORN   = get_mat("Horn",      "#FBF6EF", 0.30, 0.1)   # cornes nacrées
M_CLAW   = get_mat("Claw",      "#FBF6EF", 0.35)   # griffes, crocs
M_GOLD   = get_mat("Gold",      "#F2BD3A", 0.25, 0.85)   # monture, bracelets, plastron (ornements dorés)
M_PEARL  = get_mat("Pearl",     "#F2FBFF", 0.12, 0.25, emission="#8FE6FF", strength=2.2)   # perle facettée
M_GLOW   = get_mat("Glow",      "#6FF2F0", 0.30, emission="#3FE6F0", strength=2.5)   # perles-lueurs, veines
M_SHELL  = get_mat("Shell",     "#F8E8F0", 0.30, 0.15)   # coquille nacrée rosée
M_SHELL3 = get_mat("ShellLav",  "#E4D8F8", 0.30, 0.15)   # coquille nacrée lavande
M_SHELL2 = get_mat("ShellRib",  "#6FCDE4", 0.35)   # côtes de la coquille
M_WHITE  = get_mat("EyeWhite",  "#F6FAFB", 0.30)
M_IRIS   = get_mat("Iris",      "#1A9AAA", 0.25, emission="#4FE3F0", strength=2.5)  # iris lumineux
M_BLACK  = get_mat("Black",     "#08101A", 0.30)   # pupilles
M_NOSE   = get_mat("Nostril",   "#1E6A86", 0.50)   # narines
M_BUBBLE = get_mat("Bubble",    "#DDF8FF", 0.10, alpha=0.55)   # bulles flottantes (FX)
FINS = [M_FIN, M_FIN2, M_FIN3]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
R = 1.2               # rayon du torse
TORSO_L = 4.0         # longueur du torse (poitrail -> hanches)
LEG_H = 1.15          # hauteur du dessous du ventre
NECK_L = 2.1          # longueur du cou
NECK_RISE = 0.8       # 0 = cou horizontal, 1 = cou vertical
NECK_R = (0.66, 0.84) # rayon du cou (sous la tête, à la base)
HEAD_SCALE = 1.1      # taille de la tête
SNOUT_K = 1.1         # longueur du museau
FANGS = 2             # crocs par côté
EAR_L = 2.5           # longueur des nageoires-oreilles
EAR_RAYS = 6          # rayons des nageoires-oreilles
CREST_H = 1.2         # hauteur de la crête-nageoire du crâne
CREST_RAYS = 6        # rayons de la crête du crâne
HORN_L = 0.95         # longueur des cornes nacrées
HEAD_SPINES = 3       # épines bleues du front, par côté
CHEEK_N = 2           # nageoires de joue par côté
STEP = 0.5            # pas des segments du corps
DORSAL_H = 1.1        # hauteur max de la crête-nageoire du cou
NECK_MANE = 2         # nageoires de crinière par segment de cou et par côté
FLANK_ROWS = 3        # rangées d'écailles turquoise sur les flancs
LEG_TH = 0.62         # épaisseur des pattes
PADDLE = 1.05         # taille des pieds-palettes
ELBOW_FIN = True      # petite nageoire au coude
PEC_SPAN = 3.6        # longueur du grand rayon des pectorales
PEC_RAYS = 6          # rayons des pectorales
PELV_SPAN = 1.7       # longueur des pelviennes
PELV_RAYS = 3         # rayons des pelviennes
TAIL_L = 6.0          # longueur de la queue
TAIL_STEP = 0.5       # pas des segments de queue
TAIL_RISE = 1.1       # remontée du bout de la queue
CAUDAL_L = 2.4        # taille des lobes de la caudale
CAUDAL_RAYS = 5       # rayons de chaque lobe de la caudale
TAIL_FINLETS = 1      # paires de petites nageoires sur la queue
FX_N = 9              # bulles et perles flottantes
FX_SIZE = 0.3         # taille des FX
ORN = 1               # ornements dorés : 0 = aucun, 1 = moyens, 2 = complets
PEARL_R = 0.32        # rayon de la perle du front
SHELL_RIBS = 7        # secteurs de la coquille Saint-Jacques
BEAD_R = 0.17         # perles-lueurs au bout des nageoires (0 = aucune)
VEINS = True          # veines lumineuses sur le cou et la queue

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

def bead_mesh(r):
    """Perle-lueur : octaèdre (6 sommets, 8 triangles)."""
    v = [(r, 0, 0), (-r, 0, 0), (0, r * 1.25, 0), (0, -r * 1.25, 0), (0, 0, r), (0, 0, -r)]
    f = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    return mesh_from("bead", v, f)

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
    if BEAD_R > 0 and L0 >= 1.5:
        for k in range(n):   # perle-lueur au bout de chaque rayon (Épique)
            place(f"{name}_Bead_{k}", bead_mesh(BEAD_R * SC), M_GLOW, tips[k] + (tips[k] - root).normalized() * BEAD_R * SC * 0.4,
                  None, parent)
    for k in range(n - 1):
        a, b = root.lerp(tips[k], 0.93), root.lerp(tips[k + 1], 0.93)
        plate(f"{name}_Memb_{k}", [root, a, b], memb_t, FINS[k % 3], parent)
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
        plate(f"{name}_Memb_{k}", [bases[k], bases[k + 1], tops[k + 1], tops[k]], memb_t, FINS[k % 3], parent)

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
    fan_fin(f"Head_EarFin_{sgn}", hv((sgn * 0.8, 0.45, 0.3)), (sgn * 0.75, -0.05, 1.0), (sgn * 0.6, 1.0, 0.2),
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
                 (sgn * 0.8, 0.9, -0.35 - 0.2 * k), (0.75 - 0.12 * k) * HS, 0.35 * HS, FINS[k % 3], H,
                 up=(0, 0, 1), t=0.05 * HS)

# SIGNE DISTINCTIF : PERLE FACETTÉE sertie sur le front (monture dorée à 6 griffes, diadème, gemmes)
PR = PEARL_R
pc = Vector((0, -0.42, SKULL[2] / 2 * 0.98 + 0.04))        # centre de la monture
pdir = Vector((0, -0.3, 1.0)).normalized()
pm = basis(pdir, (1, 0, 0))
prism("Head_PearlMount", PR * 1.3 * HS, 0.2 * HS, hv(pc), pdir, M_GOLD, H, sides=8)
for k in range(6):
    a = k * math.pi / 3
    off = (pm.col[0] * math.cos(a) + pm.col[2] * math.sin(a)) * PR * 1.12
    shard(f"Head_PearlClaw_{k}", 0.12 * HS, 0.1 * HS, PR * 1.5 * HS, hv(pc + off), pdir * 1.0 + off.normalized() * -0.25, M_GOLD, H,
          up=tuple(off.normalized()))
pp = pc + pdir * PR * 0.85
crystal("Head_Pearl_Top", PR * HS, PR * 0.35 * HS, PR * 0.8 * HS, hv(pp), pdir, M_PEARL, H, sides=8)
crystal("Head_Pearl_Bot", PR * HS, PR * 0.35 * HS, PR * 0.8 * HS, hv(pp), -pdir, M_PEARL, H, sides=8)
if ORN >= 1:   # diadème : 2 épines dorées par côté de la perle, avec une gemme turquoise
    for sgn in (-1, 1):
        for k in range(1 if ORN == 1 else 2):
            hshard(f"Diadem_{sgn}_{k}", 0.2, 0.1, 0.55 - 0.15 * k, (sgn * (0.5 + 0.18 * k), -0.28 + 0.2 * k, 0.7),
                   (sgn * (0.5 + 0.25 * k), -0.2, 1.0), M_GOLD, up=(sgn, 0, 0.3))
        crystal(f"Diadem_Gem_{sgn}", 0.09 * HS, 0.06 * HS, 0.12 * HS, hv((sgn * 0.52, -0.28, 0.72)), (sgn * 0.5, -0.2, 1.0),
                M_GLOW, H, sides=6)

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
    # veine lumineuse et collier doré sur le cou (Épique)
    if VEINS and neck and s > S_CHEST * 0.15:
        B(f"Body_Vein_{i}", (0.12 * SC, Ln * 0.8, 0.1 * SC), mid + d * (r * 0.97 + 0.06 * SC), Rm, M_GLOW, body_root)
    if ORN >= 2 and neck and i % 3 == 1 and s > S_CHEST * 0.25:
        ring(f"Body_Collar_{i}", r * 1.22, 0.24 * SC, 0.3 * SC, mid, tuple(t), M_GOLD, body_root, sides=8)
    # crinière de nageoires turquoise sur les côtés du cou (ado / adulte)
    if neck:
        fade = 1.0 - s / max(1e-3, S_CHEST)
        for sgn in (-1, 1):
            for k in range(NECK_MANE):
                fin_leaf(f"Body_NeckFin_{i}_{sgn}_{k}", mid + side * sgn * r * 0.9 + d * r * (0.35 - 0.45 * k),
                         side * sgn * (0.7 - 0.2 * k) + t * 0.9 + d * 0.35, (0.9 + 0.7 * fade - 0.15 * k) * SC,
                         0.42 * SC, FINS[(i + k) % 3], body_root, up=tuple(side * sgn * 0.8 + d * 0.6), t=0.06 * SC)
    else:
        torso_segs.append(i)
    # base de la crête dorsale
    if s > S_CHEST * 0.35 and neck:   # la crête dorsale s'arrête à la coquille
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
    (M_GOLD if ORN >= 1 else M_BELLY), body_root, bevel=0.05 * SC)
if ORN >= 1:   # gemme du plastron
    crystal("Body_PlastronGem", 0.2 * SC, 0.12 * SC, 0.22 * SC, CHEST + Vector((0, -r * 0.98, -r * 0.35)), (0, -1, 0.3), M_PEARL, body_root, sides=6)

# SIGNE DISTINCTIF : COQUILLE SAINT-JACQUES nacrée sur le dos, comme une carapace
# (charnière devant, secteurs en éventail vers l'arrière, côtes turquoise, bord doré)
SH_Y0 = CHEST.y + TL * 0.05                      # charnière (devant)
SH_Z0 = ZC + R * 1.0
SH_L = TL * 0.86                                # longueur de la coquille
SH_W = R * 1.5                                  # demi-largeur
SH_A = math.radians(62)
def shell_pt(u, f, up=0.0):
    a = u * SH_A
    x = math.sin(a) / math.sin(SH_A) * SH_W * f
    y = SH_Y0 + math.cos(a) * SH_L * f
    z = SH_Z0 + R * 0.16 * f + R * 0.6 * (y - SH_Y0) / SH_L - (x / SH_W) ** 2 * R * 0.5 * f + up
    return Vector((x, y, z))
hinge = shell_pt(0, 0.0)
us = [-1 + 2 * k / SHELL_RIBS for k in range(SHELL_RIBS + 1)]
for k in range(SHELL_RIBS):
    u0, u1 = us[k], us[k + 1]
    um = (u0 + u1) / 2
    plate(f"Shell_Sector_{k}", [hinge, shell_pt(u0, 1.0), shell_pt(um, 1.07), shell_pt(u1, 1.0)], 0.16 * SC,
          M_SHELL if k % 2 else M_SHELL3, body_root)
    if ORN >= 1:   # second niveau, surélevé, plus petit
        plate(f"Shell_Inner_{k}", [hinge, shell_pt(u0, 0.55, 0.08 * R), shell_pt(um, 0.6, 0.08 * R), shell_pt(u1, 0.55, 0.08 * R)],
              0.12 * SC, M_SHELL3 if k % 2 else M_SHELL, body_root)
for k, u in enumerate(us):
    bar(f"Shell_Rib_{k}", hinge, shell_pt(u, 1.04, 0.05 * R), 0.13 * SC, M_SHELL2, body_root)
    if ORN >= 1:
        place(f"Shell_Bead_{k}", bead_mesh(0.17 * SC), M_GLOW, shell_pt(u, 1.1, 0.06 * R), None, body_root)
    if k < SHELL_RIBS and ORN >= 1:
        bar(f"Shell_Rim_{k}", shell_pt(u, 1.05, 0.05 * R), shell_pt(us[k + 1], 1.05, 0.05 * R), 0.12 * SC, M_GOLD, body_root)
box("Shell_Hinge", (R * 0.8, 0.45 * SC, 0.3 * SC), hinge + Vector((0, 0.05, 0.04)), mat=(M_GOLD if ORN >= 1 else M_SHELL2), parent=body_root, bevel=0.04 * SC)
for sgn in (-1, 1):   # oreillettes de la charnière
    wedge(f"Shell_Ear_{sgn}", (0.55 * SC, 0.4 * SC, 0.3 * SC), hinge + Vector((sgn * R * 0.5, -0.05, 0.0)), None, M_SHELL3, body_root, top_x=0.6, top_y=0.8, bevel=0)

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
          (x + sgn * th * 0.12, y, ZC - R * 0.3), mat=M_LEG, parent=legs_root,
          top_x=0.8, top_y=0.75, bevel=0.08 * SC)
    top = Vector((x + sgn * th * 0.15, y, ZC - R * 0.55))
    knee = Vector((x + sgn * th * 0.32, y + (th * 0.35 if hind else -th * 0.1), FOOT_H + LEG_H * 0.5))
    ankle = Vector((x + sgn * th * 0.42, y + (-th * 0.05 if hind else -th * 0.3), FOOT_H * 0.9))
    link(f"{name}_Upper", top, knee, th * 0.95, M_LEG, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0.05 * SC, depth=th * 1.05)
    link(f"{name}_Lower", knee, ankle, th * 0.75, M_LEG, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0, depth=th * 0.8)
    B(f"{name}_Knee", (th * 0.9, th * 0.5, th * 0.55), knee + Vector((0, -th * 0.38, 0)), mat=(M_GOLD if ORN >= 1 else M_SCALE),
      parent=legs_root)
    if ORN >= 1:   # bracelet doré sur la jambe
        ring(f"{name}_Bracelet", th * 0.62, th * 0.2, th * 0.34, knee.lerp(ankle, 0.62), tuple(ankle - knee), M_GOLD, legs_root, sides=8)
    # pied-palette
    F = Vector((ankle.x, ankle.y - th * 0.3, FOOT_H / 2))
    box(f"{name}_Foot", (th * 1.25 * pad, th * 1.2 * pad, FOOT_H), F, mat=M_LEG, parent=legs_root, bevel=0.05 * SC)
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
    fan_fin(f"Wings_Pec_{sgn}", proot, (sgn * 1.0, -0.15, 0.6), (sgn * 0.5, 1.0, 0.05), PEC_RAYS,
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
    if VEINS and s < 0.8:
        B(f"Tail_Vein_{i}", (0.1 * SC, Ln * 0.8, 0.09 * SC), mid + d * (r * hk + 0.05 * SC), Rm, M_GLOW, tail_root)
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
B("Tail_Collar", (R * 0.42, 0.35 * SC, R * 0.55), tip - ct * 0.1 * SC, seg_matrix(ct, cd, cs), (M_GOLD if ORN >= 1 else M_SCALE), tail_root)
froot = tip + ct * 0.05 * SC
fan_fin("Tail_CaudalTop", froot, ct * 0.45 + cd * 1.0, ct * 1.0 + cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L, CAUDAL_L * 0.55, tail_root, ray_th=0.12 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.35 * SC if IS_ADULTE else 0.0))
fan_fin("Tail_CaudalBot", froot, ct * 0.55 - cd * 1.0, ct * 1.0 - cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L * 0.85, CAUDAL_L * 0.5, tail_root, ray_th=0.12 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.3 * SC if IS_ADULTE else 0.0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Épique : silhouette spectaculaire (grandes nageoires-oreilles, crête, coquille), éléments émissifs
#     (perle, perles-lueurs, veines, iris), ornements dorés (monture, plastron, bracelets, collier),
#     FX : bulles et petites perles qui flottent autour du dragon.
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
        rot = (random.uniform(0, 45), random.uniform(0, 45), random.uniform(0, 45))
        if k % 2:   # perle facettée lumineuse
            place(f"FX_Pearl_{k}", crystal_mesh(FX_SIZE * 0.55, FX_SIZE * 0.2, FX_SIZE * 0.45, 6), M_PEARL, p, rot, master)
        else:       # bulle d'eau
            place(f"FX_Bubble_{k}", bubble_mesh(FX_SIZE * random.uniform(0.6, 1.3)), M_BUBBLE, p, rot, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
