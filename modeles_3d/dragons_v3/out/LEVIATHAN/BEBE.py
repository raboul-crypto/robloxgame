import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Léviathan · Bébé
#  Mythique · Eau · Aquatique (dragon de zone, boss du monde 4) · monde 4
#  - Bébé trapu : énorme tête, très grands yeux brillants à reflets, museau court, pas de crocs, pattes courtes
#  - Gemme cyan sur le front, couronne de 5 petites cornes nacrées, 2 plaques métalliques sur le crâne, nageoires-oreilles turquoise
#  - Plaques blindées platine sur le dos et la queue, points et lignes bioluminescents cyan, nageoires déjà grandes, halo flottant discret
#  - Queue de poisson à caudale en V, quelques bulles et éclats en orbite
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4404)            # même dragon à chaque exécution
TAG = "LEVIATHAN_BEBE"      # préfixe de tous les objets, matériaux et de la collection
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
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Bleu abyssal (corps), turquoise (écailles, crêtes), ventre bleu pâle, cornes nacrées,
#    plaques blindées en métal bleu-argent (Mythique : metallic 0.85-0.95, roughness basse),
#    bioluminescence cyan (points, lignes, gemmes, iris : strength 3 à 4).
# ----------------------------------------------------------
M_BODY   = get_mat("Body",      "#123C7C", 0.38, 0.10)   # corps bleu abyssal
M_SCALE  = get_mat("BodyScale", "#1FB4C8", 0.35)         # écailles, crêtes, dos turquoise
M_LEG    = get_mat("Leg",       "#0F4E96", 0.38, 0.10)   # pattes bleu roi
M_DARK   = get_mat("BodyDark",  "#081C40", 0.45)         # sourcils, ligne de bouche, ombres
M_BELLY  = get_mat("Belly",     "#B8E6F4", 0.40)         # ventre en plaques, mâchoire
M_FIN    = get_mat("Fin",       "#22C4DA", 0.22, alpha=0.82)   # membranes turquoise
M_FIN2   = get_mat("FinDeep",   "#2F6FD8", 0.22, alpha=0.82)   # membranes bleu saphir
M_FIN3   = get_mat("FinLight",  "#8CF0F4", 0.22, alpha=0.82)   # membranes cyan clair
M_RAY    = get_mat("FinRay",    "#7FA9D0", 0.25, 0.85)         # rayons métalliques
M_HORN   = get_mat("Horn",      "#F0F8FA", 0.28, 0.12)         # cornes nacrées
M_CLAW   = get_mat("Claw",      "#F4FAFC", 0.35)               # griffes, crocs
M_PLATE  = get_mat("Plate",     "#A9C9E4", 0.20, 0.92)         # plaques blindées platine bleuté
M_PLATE2 = get_mat("PlateDark", "#355C8E", 0.28, 0.90)         # plaques blindées acier abyssal
M_GLOW   = get_mat("Glow",      "#5FF4FF", 0.30, emission="#2FEAFF", strength=3.5)   # points et lignes bioluminescents
M_GEM    = get_mat("Gem",       "#4FF0FF", 0.10, 0.2, emission="#3FE8FF", strength=3.5)   # gemmes cyan
M_GEM2   = get_mat("GemSapphire", "#2A6CFF", 0.10, 0.2, emission="#3A86FF", strength=3.0) # gemmes saphir
M_PEARL  = get_mat("Pearl",     "#F2FBFF", 0.10, 0.25, emission="#9FEBFF", strength=2.5)  # perles, éclats flottants
M_HALO   = get_mat("Halo",      "#BDF8FF", 0.15, 0.6, emission="#4FF0FF", strength=4.0)   # halo flottant
M_WHITE  = get_mat("EyeWhite",  "#F6FAFB", 0.30)
M_IRIS   = get_mat("Iris",      "#18B8D8", 0.20, emission="#4FF0FF", strength=4.0)        # iris lumineux
M_BLACK  = get_mat("Black",     "#050B16", 0.30)         # pupilles
M_NOSE   = get_mat("Nostril",   "#061A3A", 0.50)         # narines
M_BUBBLE = get_mat("Bubble",    "#DDF8FF", 0.10, alpha=0.5)   # bulles flottantes (FX)
FINS = [M_FIN, M_FIN2, M_FIN3]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "BEBE"
R             = 1.2        # rayon du torse
TORSO_L       = 2.6        # longueur du torse (poitrail -> hanches)
LEG_H         = 0.75       # hauteur du dessous du ventre
NECK_L        = 0.8        # longueur du cou
NECK_RISE     = 0.8        # 0 = cou horizontal, 1 = cou vertical
NECK_R        = (0.8, 0.92) # rayon du cou (sous la tête, à la base)
HEAD_SCALE    = 1.5        # taille de la tête
SNOUT_K       = 0.72       # longueur du museau
FANGS         = 0          # crocs par côté
EAR_L         = 2.0        # longueur des nageoires-oreilles
EAR_RAYS      = 5          # rayons des nageoires-oreilles
CREST_H       = 0.8        # hauteur de la crête-nageoire du crâne
CREST_RAYS    = 5          # rayons de la crête du crâne
HORN_L        = 0.5        # longueur des cornes nacrées de la couronne
HORN_N        = 5          # nombre de cornes de la couronne
HEAD_SPINES   = 0          # épines turquoise du front, par côté
CHEEK_N       = 1          # nageoires de joue par côté
STEP          = 0.6        # pas des segments du corps
DORSAL_H      = 0.7        # hauteur max de la crête-nageoire dorsale
DORSAL_EVERY  = 1          # un rayon métallique tous les N segments (crête)
NECK_MANE     = 0          # nageoires de crinière par segment de cou et par côté
FLANK_ROWS    = 2          # rangées d'écailles turquoise sur les flancs
LEG_TH        = 0.74       # épaisseur des pattes
PADDLE        = 1.0        # taille des pieds-palettes
ELBOW_FIN     = False      # petite nageoire au coude
PEC_SPAN      = 3.2        # longueur du grand rayon des pectorales (nageoires immenses)
PEC_RAYS      = 6          # rayons des pectorales
PELV_SPAN     = 1.2        # longueur des pelviennes
PELV_RAYS     = 3          # rayons des pelviennes
TAIL_L        = 3.6        # longueur de la queue
TAIL_STEP     = 0.6        # pas des segments de queue
TAIL_RISE     = 0.9        # remontée du bout de la queue
CAUDAL_L      = 1.9        # taille des lobes de la caudale
CAUDAL_RAYS   = 4          # rayons de chaque lobe de la caudale
TAIL_FINLETS  = 0          # paires de petites nageoires sur la queue
FX_N          = 14         # éclats, perles et bulles en orbite autour du corps
FX_UP         = 5          # bulles qui montent
FX_SIZE       = 0.28       # taille des FX
ARMOR         = 1          # plaques blindées : 0 = aucune, 1 = moyennes, 2 = complètes (flancs, épaulières)
ARMOR_K       = 0.8        # épaisseur des plaques du dos
SPIKES        = False      # pointes sur les plaques du dos
CAP_N         = 3          # plaques métalliques sur le crâne
HEAD_DOTS     = 3          # points lumineux du museau, par côté
LINES         = True       # lignes bioluminescentes
DOTS          = True       # points bioluminescents sur les flancs
DOT_ROWS      = 2          # rangées de points sur les flancs
GEM_R         = 0.34       # rayon de la gemme du front
GEMS_HEAD     = 0          # gemmes saphir sur le crâne, par côté
GEMS_CHEST    = 0          # gemmes saphir sur le poitrail, par côté
HALO_R        = 1.6        # rayon du halo flottant (0 = aucun)
HALO_Y        = 2.4        # distance du halo derrière la tête
HALO_SIDES    = 16         # nombre de côtés du halo
HALO_GEMS     = 4          # gemmes en orbite sur le halo
BEAD_R        = 0.14       # points lumineux au bout des nageoires (0 = aucun)
FIN_DOTS      = 0          # points lumineux sur chaque rayon des nageoires

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
HEAD_PITCH = 5                                   # degrés : la tête regarde un peu vers le bas

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

def fin_leaf(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Petite nageoire en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def bead_mesh(r):
    """Point bioluminescent : octaèdre (6 sommets, 8 triangles)."""
    v = [(r, 0, 0), (-r, 0, 0), (0, r * 1.25, 0), (0, -r * 1.25, 0), (0, 0, r), (0, 0, -r)]
    f = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    return mesh_from("bead", v, f)

def dot(name, loc, r, parent, mat=None):
    return place(name, bead_mesh(r), mat or M_GLOW, loc, None, parent)

def fan_fin(name, root, d0, d1, n, L0, L1, parent, ray_th, memb_t, bulge=0.12, tip_spike=0.0, dots=0):
    """NAGEOIRE EN ÉVENTAIL (plaques avec rayons) : n rayons qui partent de 'root',
    du rayon d'attaque d0 (le plus long, L0) au rayon de fuite d1 (L1).
    Entre deux rayons : une membrane translucide (turquoise / saphir / cyan en alternance).
    'dots' = points bioluminescents posés sur chaque rayon. Renvoie les pointes."""
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
        for k in range(n):   # point lumineux au bout de chaque rayon
            dot(f"{name}_Bead_{k}", tips[k] + (tips[k] - root).normalized() * BEAD_R * SC * 0.4, BEAD_R * SC, parent)
    if dots > 0:
        for k in range(n):
            for j in range(dots):
                fr = 0.42 + 0.2 * j
                dot(f"{name}_Dot_{k}_{j}", root.lerp(tips[k], fr), BEAD_R * SC * 0.6, parent)
    for k in range(n - 1):
        a, b = root.lerp(tips[k], 0.93), root.lerp(tips[k + 1], 0.93)
        plate(f"{name}_Memb_{k}", [root, a, b], memb_t, FINS[k % 3], parent)
    if tip_spike > 0:
        shard(f"{name}_TipSpike", ray_th * 2.2, ray_th * 1.4, tip_spike, tips[0], tips[0] - root, M_PLATE, parent, up=up)
    return tips

def comb_fin(name, bases, tops, parent, ray_th, memb_t, ray_every=1):
    """NAGEOIRE EN PEIGNE (crête dorsale, crête du crâne) : rayons métalliques reliés par des membranes."""
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

# Crâne large, museau lourd, arête blindée, mâchoire pâle distincte, ligne de bouche
SKULL = (1.9, 1.7, 1.55)
hwedge("Skull", SKULL, (0, 0, 0), mat=M_BODY, top_x=0.84, top_y=0.84, bevel=0.12)
hwedge("Snout", (1.55, 1.65 * SNOUT_K, 0.86), (0, -0.7 - 0.82 * SNOUT_K, -0.3), mat=M_BODY,
       top_x=0.86, top_y=0.92, shift_y=-0.05, bevel=0.09)
hbox("SnoutBridge", (0.75, 1.35 * SNOUT_K, 0.12), (0, -0.62 - 0.78 * SNOUT_K, 0.14),
     mat=(M_PLATE if ARMOR >= 1 else M_SCALE))
hbox("Jaw", (1.35, 1.55 * SNOUT_K, 0.34), (0, -0.66 - 0.77 * SNOUT_K, -0.76), mat=M_BELLY, bevel=0.04)
hbox("Chin", (1.15, 0.7, 0.32), (0, -0.25, -0.72), mat=M_BELLY)
hbox("MouthLine", (1.6, 1.6 * SNOUT_K, 0.05), (0, -0.7 - 0.82 * SNOUT_K, -0.69), mat=M_DARK)
SNOUT_FRONT = -0.7 - 1.65 * SNOUT_K

for sgn in (-1, 1):   # narines
    hbox(f"Nostril_{sgn}", (0.2, 0.24, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.3, 0.12), mat=M_NOSE)

# Yeux : blanc, iris cyan lumineux, pupille (ronde + reflets pour le bébé, fendue ensuite)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.95, 1.0, 0.75, 0.85, 0.42, 0.58
elif IS_ADO:
    EW, EH, IW, IH, PW, PH = 0.68, 0.62, 0.5, 0.52, 0.12, 0.48
else:
    EW, EH, IW, IH, PW, PH = 0.62, 0.56, 0.44, 0.47, 0.1, 0.43
for sgn in (-1, 1):
    ey, ez = -0.3, 0.12
    ex = SKULL[0] / 2 * 0.99
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * ex, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * (ex + 0.04), ey - 0.03, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * (ex + 0.08), ey - 0.05, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.24, 0.24), (sgn * (ex + 0.11), ey - 0.18, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * (ex + 0.11), ey + 0.14, ez - 0.2), mat=M_WHITE)
    else:   # sourcils blindés, sévères
        hbox(f"Brow_{sgn}", (0.2, EW + 0.34, 0.26 if IS_ADO else 0.32),
             (sgn * (ex + 0.02), ey - 0.06, ez + EH / 2 + 0.13), rot=(10 if IS_ADO else 18, 0, 0),
             mat=(M_PLATE2 if ARMOR >= 1 else M_DARK))

for sgn in (-1, 1):   # crocs blancs
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.4 + k * 0.42
        hshard(f"Fang_{sgn}_{k}", 0.18, 0.18, 0.24 + 0.05 * FANGS, (sgn * 0.62, fy, -0.64), (0, 0.05, -1),
               M_CLAW, up=(1, 0, 0))

# BLINDAGE DE LA TÊTE : plaques métalliques sur le crâne, les joues et le museau + points lumineux
if ARMOR >= 1:
    for k in range(CAP_N):
        f = k / max(1, CAP_N - 1)
        hwedge(f"CapPlate_{k}", (1.35 - 0.3 * f, 0.5, 0.2 + 0.05 * (1 - f)), (0, -0.55 + 1.0 * f, SKULL[2] / 2 + 0.03),
               mat=(M_PLATE if k % 2 == 0 else M_PLATE2), top_x=0.75, top_y=0.9)
    for sgn in (-1, 1):
        hwedge(f"CheekPlate_{sgn}", (0.18, 1.0, 0.7), (sgn * (SKULL[0] / 2 + 0.06), 0.62, -0.25), mat=M_PLATE,
               top_x=0.8, top_y=0.9)
        hwedge(f"CheekPlate2_{sgn}", (0.16, 0.7, 0.45), (sgn * (SKULL[0] / 2 + 0.05), 0.6, 0.4), mat=M_PLATE2,
               top_x=0.8, top_y=0.9)
        hbox(f"SnoutPlate_{sgn}", (0.12, 1.1 * SNOUT_K, 0.35), (sgn * 0.76, -0.7 - 0.82 * SNOUT_K, -0.18), mat=M_PLATE2)
for sgn in (-1, 1):   # points bioluminescents du museau et des joues
    for k in range(HEAD_DOTS):
        dot(f"Head_Dot_{sgn}_{k}", hv((sgn * 0.84, SNOUT_FRONT + 0.7 + k * (0.5 + 0.12 * SNOUT_K), 0.02 + 0.05 * (k % 2))),
            0.07 * HS, H)
if LINES:
    for sgn in (-1, 1):
        hbox(f"Head_Line_{sgn}", (0.06, 1.3 * SNOUT_K, 0.06), (sgn * 0.66, -0.7 - 0.82 * SNOUT_K, 0.38), mat=M_GLOW)
        hbox(f"Head_Line2_{sgn}", (0.06, 0.7, 0.06), (sgn * (SKULL[0] / 2 + 0.1), 0.62, 0.1), mat=M_GLOW)

# SIGNE DISTINCTIF : grandes NAGEOIRES-OREILLES turquoise / saphir
for sgn in (-1, 1):
    fan_fin(f"Head_EarFin_{sgn}", hv((sgn * 0.85, 0.45, 0.3)), (sgn * 0.95, 0.0, 0.7), (sgn * 0.9, 0.9, 0.05),
            EAR_RAYS, EAR_L * HS, EAR_L * 0.62 * HS, H, ray_th=0.1 * HS, memb_t=0.05 * HS, bulge=0.15,
            dots=(1 if IS_ADULTE else 0))

# Crête-nageoire sur le dessus du crâne
bases, tops = [], []
for k in range(CREST_RAYS):
    f = k / max(1, CREST_RAYS - 1)
    b = hv((0, -0.2 + 0.9 * f, SKULL[2] / 2 * 0.95 + (0.12 if ARMOR >= 1 else 0)))
    h = CREST_H * (0.75 + 0.35 * math.sin(math.pi * (0.25 + 0.75 * f))) * HS
    bases.append(b)
    tops.append(b + Vector((0, 0.55, 1.0)).normalized() * h)
comb_fin("Head_Crest", bases, tops, H, ray_th=0.09 * HS, memb_t=0.05 * HS)

# COURONNE DE CORNES NACRÉES : un arc de cornes qui s'ouvre derrière le crâne
for k in range(HORN_N):
    f = (k / max(1, HORN_N - 1)) * 2 - 1                    # -1 .. 1
    a = f * math.radians(78)
    lk = HORN_L * (1.0 - 0.38 * abs(f))                     # la corne du milieu est la plus longue
    p0 = Vector((math.sin(a) * 0.82, 0.55 - 0.15 * abs(f), 0.35 + math.cos(a) * 0.3))
    d1 = Vector((math.sin(a) * 0.75, 0.7, 0.55 + 0.35 * math.cos(a))).normalized()
    p1 = p0 + d1 * lk * 0.9
    d2 = Vector((math.sin(a) * 0.5, 0.55, 0.45 + 0.6 * math.cos(a))).normalized()
    p2 = p1 + d2 * lk * 0.85
    bar(f"Head_Crown_{k}_0", hv(p0), hv(p1), 0.26 * HS * (1 - 0.2 * abs(f)), M_HORN, H, up=(0, 0, 1))
    shard(f"Head_Crown_{k}_1", 0.24 * HS, 0.24 * HS, (p2 - p1).length * HS * 1.15, hv(p1), p2 - p1, M_HORN, H)
    if ARMOR >= 2 and k % 2 == 0:   # bague métallique à la base de la corne
        bar(f"Head_CrownBand_{k}", hv(p0 + d1 * lk * 0.35), hv(p0 + d1 * lk * 0.5), 0.33 * HS, M_PLATE, H)

# Épines turquoise du front et nageoires de joue
for sgn in (-1, 1):
    for k in range(HEAD_SPINES):
        hshard(f"Spine_{sgn}_{k}", 0.22, 0.08, 0.5 - 0.06 * k, (sgn * (0.3 + 0.08 * k), -0.55 + 0.32 * k, 0.74),
               (sgn * 0.35, 1, 0.55), M_SCALE, up=(sgn, 0, 0.3))
    for k in range(CHEEK_N):
        fin_leaf(f"Head_Cheek_{sgn}_{k}", hv((sgn * 0.9, -0.05 + k * 0.22, -0.45 - k * 0.1)),
                 (sgn * 0.8, 0.9, -0.35 - 0.2 * k), (0.8 - 0.12 * k) * HS, 0.36 * HS, FINS[k % 3], H,
                 up=(0, 0, 1), t=0.05 * HS)

# GEMME DU FRONT : cristal cyan sur une monture métallique à 6 griffes (+ gemmes saphir de chaque côté)
GR = GEM_R
gc = Vector((0, -0.42, SKULL[2] / 2 * 0.98 + (0.16 if ARMOR >= 1 else 0.04)))
gdir = Vector((0, -0.3, 1.0)).normalized()
gm = basis(gdir, (1, 0, 0))
prism("Head_GemMount", GR * 1.35 * HS, 0.2 * HS, hv(gc), gdir, M_PLATE, H, sides=8)
for k in range(6):
    a = k * math.pi / 3
    off = (gm.col[0] * math.cos(a) + gm.col[2] * math.sin(a)) * GR * 1.15
    shard(f"Head_GemClaw_{k}", 0.12 * HS, 0.1 * HS, GR * 1.5 * HS, hv(gc + off), gdir * 1.0 + off.normalized() * -0.25, M_PLATE, H,
          up=tuple(off.normalized()))
gp = gc + gdir * GR * 0.85
crystal("Head_Gem_Top", GR * HS, GR * 0.4 * HS, GR * 1.0 * HS, hv(gp), gdir, M_GEM, H, sides=8)
crystal("Head_Gem_Bot", GR * HS, GR * 0.4 * HS, GR * 0.8 * HS, hv(gp), -gdir, M_GEM, H, sides=8)
if GEMS_HEAD > 0:
    for sgn in (-1, 1):
        for k in range(GEMS_HEAD):
            crystal(f"Head_SideGem_{sgn}_{k}", 0.1 * HS, 0.07 * HS, 0.14 * HS,
                    hv((sgn * (0.62 + 0.2 * k), -0.5 + 0.1 * k, SKULL[2] / 2 * 0.98 + 0.13)), (sgn * 0.4, -0.2, 1.0), M_GEM2, H, sides=6)

# HALO FLOTTANT derrière la tête : anneau lumineux, anneau extérieur métallique, éclats en orbite
if HALO_R > 0:
    hc = Vector((0, HALO_Y, 0.35))
    ring("Head_Halo", HALO_R * HS, 0.32 * HS, 0.16 * HS, hv(hc), (0, 1, 0), M_HALO, H, sides=HALO_SIDES)
    if ARMOR >= 2:
        ring("Head_HaloOuter", HALO_R * 1.22 * HS, 0.14 * HS, 0.1 * HS, hv(hc + Vector((0, 0.18, 0))), (0, 1, 0), M_PLATE, H, sides=HALO_SIDES)
    for k in range(HALO_GEMS):
        a = k * 2 * math.pi / HALO_GEMS
        crystal(f"Head_HaloGem_{k}", 0.17 * HS, 0.1 * HS, 0.28 * HS,
                hv(hc + Vector((math.cos(a) * HALO_R * 1.0, 0.0, math.sin(a) * HALO_R * 1.0))),
                (math.cos(a), 0.0, math.sin(a)), (M_GEM if k % 2 == 0 else M_GEM2), H, up=(0, 1, 0), sides=6)

# ----------------------------------------------------------
# 10. CORPS : courbe Catmull-Rom (cou + torse), segments, ventre en plaques, DOS BLINDÉ,
#     points et lignes bioluminescents sur les flancs, crinière de nageoires, crête dorsale
# ----------------------------------------------------------
BODY_CTRL = [
    NECK_TOP,
    CHEST.lerp(NECK_TOP, 0.5) + Vector((0, NECK_L * 0.06, 0)),
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
S_CHEST = cum[i_chest] / cum[-1]
BODY_R_KEYS = [(0.0, NECK_R[0]), (S_CHEST * 0.75, NECK_R[1]), (S_CHEST + (1 - S_CHEST) * 0.18, R),
               (S_CHEST + (1 - S_CHEST) * 0.65, R * 0.97), (1.0, R * 0.86)]
DORSAL_KEYS = [(0.0, DORSAL_H * 0.35), (S_CHEST, DORSAL_H * 0.75), (S_CHEST + (1 - S_CHEST) * 0.4, DORSAL_H),
               (1.0, DORSAL_H * 0.7)]

def seg_info(spine, i, keys):
    p1, p2 = spine[i], spine[i + 1]
    s = (i + 0.5) / (len(spine) - 1)
    t, d, side = frame(p2 - p1)
    return (p1 + p2) / 2, (p2 - p1).length, s, keyed(keys, s), t, d, side

def flank_glow(prefix, i, mid, Ln, r, t, d, side, Rm, wk=1.0, rows=2):
    """Points et ligne bioluminescents sur les flancs d'un segment."""
    for sgn in (-1, 1):
        for row in range(rows):
            if (i + row) % 2 == 0 and DOTS:
                dot(f"{prefix}_Dot_{i}_{sgn}_{row}", mid + side * sgn * (r * wk * 1.03) + d * r * (0.05 - 0.55 * row) + t * Ln * 0.1,
                    0.085 * SC, tail_root if prefix.startswith("Tail") else body_root)
        if LINES and i % 2 == 1:
            B(f"{prefix}_Line_{i}_{sgn}", (0.07 * SC, Ln * 1.25, 0.07 * SC), mid + side * sgn * (r * wk * 1.02) - d * r * 0.3, Rm,
              M_GLOW, tail_root if prefix.startswith("Tail") else body_root)

dorsal_b, dorsal_t = [], []
torso_segs = []
for i in range(N):
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    Rm = seg_matrix(t, d, side)
    neck = s < S_CHEST
    box(f"Body_Seg_{i}", (2 * r * 1.06, Ln * 1.32, 2 * r * 0.94), mid, Rm, M_BODY, body_root, bevel=0.07 * SC)
    if s > S_CHEST * 0.2:   # plaques de ventre bien séparées
        B(f"Body_Belly_{i}", (2 * r * 0.8, Ln * 0.78, 0.2 * SC), mid - d * (r * 0.93), Rm, M_BELLY, body_root)
    # DOS BLINDÉ : plaque métallique en wedge, une sur deux plus sombre, ligne lumineuse au sommet
    if ARMOR >= 1 and s > S_CHEST * 0.18:
        pm = M_PLATE if i % 2 == 0 else M_PLATE2
        wedge(f"Body_Plate_{i}", (2 * r * 0.98, Ln * 1.22, 0.4 * SC * ARMOR_K), mid + d * (r * 0.98), Rm, pm, body_root,
              top_x=0.72, top_y=0.88, bevel=0)
        if LINES:
            B(f"Body_PlateGlow_{i}", (0.08 * SC, Ln * 0.9, 0.06 * SC), mid + d * (r * 0.98 + 0.4 * SC * ARMOR_K), Rm, M_GLOW, body_root)
        if SPIKES and i % 2 == 0:
            shard(f"Body_PlateSpike_{i}", 0.5 * SC, 0.12 * SC, (0.8 + 0.5 * ARMOR) * SC, mid + d * (r * 0.98 + 0.3 * SC),
                  d * 1.0 + t * 0.55, M_PLATE, body_root, up=tuple(side))
    elif ARMOR == 0:
        B(f"Body_Back_{i}", (2 * r * 0.72, Ln * 0.95, 0.16 * SC), mid + d * (r * 0.94), Rm, M_SCALE, body_root)
    # plaques de flanc (armure latérale), un segment sur deux
    if ARMOR >= 2 and (not neck) and i % 2 == 0:
        for sgn in (-1, 1):
            wedge(f"Body_Side_{i}_{sgn}", (0.3 * SC, Ln * 1.7, r * 0.8), mid + side * sgn * (r * 1.0) + d * r * 0.42, Rm,
                  M_PLATE2, body_root, top_x=0.6, top_y=0.9, bevel=0)
    if neck and i % 3 == 1 and s > S_CHEST * 0.25 and ARMOR >= 1:   # colliers métalliques sur le cou
        ring(f"Body_Collar_{i}", r * 1.22, 0.24 * SC, 0.3 * SC, mid, tuple(t), M_PLATE, body_root, sides=8)
    flank_glow("Body", i, mid, Ln, r, t, d, side, Rm, rows=DOT_ROWS)
    if neck and NECK_MANE > 0:   # crinière de nageoires sur les côtés du cou
        fade = 1.0 - s / max(1e-3, S_CHEST)
        for sgn in (-1, 1):
            for k in range(NECK_MANE):
                fin_leaf(f"Body_NeckFin_{i}_{sgn}_{k}", mid + side * sgn * r * 0.9 + d * r * (0.35 - 0.45 * k),
                         side * sgn * (0.7 - 0.2 * k) + t * 0.9 + d * 0.35, (0.9 + 0.7 * fade - 0.15 * k) * SC,
                         0.42 * SC, FINS[(i + k) % 3], body_root, up=tuple(side * sgn * 0.8 + d * 0.6), t=0.06 * SC)
    if not neck:
        torso_segs.append(i)
    if s > S_CHEST * 0.35:
        h = keyed(DORSAL_KEYS, s) * SC
        bpt = SPINE[i] + frame(SPINE[min(i + 1, N)] - SPINE[i])[1] * (keyed(BODY_R_KEYS, i / N) * 0.85 + (0.4 * SC * ARMOR_K if ARMOR >= 1 else 0))
        dd = frame(SPINE[min(i + 1, N)] - SPINE[i])
        dorsal_b.append(bpt)
        dorsal_t.append(bpt + (dd[1] * 1.0 + dd[0] * 0.5).normalized() * h)

comb_fin("Body_Dorsal", dorsal_b, dorsal_t, body_root, ray_th=0.1 * SC, memb_t=0.06 * SC, ray_every=DORSAL_EVERY)

# Écailles turquoise en quinconce sur les flancs (sous les points lumineux)
for i in torso_segs:
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    for sgn in (-1, 1):
        for row in range(FLANK_ROWS):
            if (i + row) % 2:
                continue
            shard(f"Body_Scale_{i}_{sgn}_{row}", 0.6 * SC, 0.08 * SC, 0.7 * SC,
                  mid + side * sgn * (r * 1.04) + d * r * (-0.25 - 0.3 * row) - t * Ln * 0.2,
                  side * sgn * 0.22 + t, pick([M_SCALE, M_BODY, M_SCALE]), body_root, up=(sgn, 0, 0))

# Plastron métallique sur le poitrail avec gemme + gemmes de poitrail
mid, Ln, s, r, t, d, side = seg_info(SPINE, i_chest, BODY_R_KEYS)
box("Body_Plastron", (r * 1.55, 0.32 * SC, r * 1.15), CHEST + Vector((0, -r * 0.8, -r * 0.35)), (18, 0, 0),
    (M_PLATE if ARMOR >= 1 else M_BELLY), body_root, bevel=0.05 * SC)
crystal("Body_PlastronGem", 0.26 * SC, 0.16 * SC, 0.3 * SC, CHEST + Vector((0, -r * 1.0, -r * 0.3)), (0, -1, 0.3), M_GEM, body_root, sides=8)
for sgn in (-1, 1):
    for k in range(GEMS_CHEST):
        crystal(f"Body_ChestGem_{sgn}_{k}", 0.13 * SC, 0.09 * SC, 0.16 * SC,
                CHEST + Vector((sgn * r * (0.45 + 0.2 * k), -r * 0.95, -r * (0.05 + 0.4 * k))), (sgn * 0.2, -1, 0.1), M_GEM2, body_root, sides=6)

# ----------------------------------------------------------
# 11. PATTES EN PALETTES : épaulière blindée, cuisse en wedge, bras, genouillère, avant-bras,
#     bracelet métallique, pied large, 3 doigts palmés + 3 griffes blanches
# ----------------------------------------------------------
FOOT_H = 0.3 * SC

def leg(name, sgn, y, th, hind):
    x = sgn * R * 0.8
    pad = PADDLE * (1.15 if hind else 1.0)
    wedge(f"{name}_Thigh", (th * 1.3, th * (1.7 if hind else 1.45), R * 1.25),
          (x + sgn * th * 0.12, y, ZC - R * 0.3), mat=M_LEG, parent=legs_root,
          top_x=0.8, top_y=0.75, bevel=0.08 * SC)
    if ARMOR >= 1:   # épaulière / cuisseau métallique + gemme
        wedge(f"{name}_Pauldron", (th * 1.5, th * (1.55 if hind else 1.3), R * 0.55),
              (x + sgn * th * 0.2, y, ZC + R * 0.18), mat=M_PLATE, parent=legs_root, top_x=0.7, top_y=0.8, bevel=0)
        if ARMOR >= 2:
            wedge(f"{name}_Pauldron2", (th * 1.0, th * 0.9, R * 0.4),
                  (x + sgn * th * 0.2, y, ZC + R * 0.52), mat=M_PLATE2, parent=legs_root, top_x=0.6, top_y=0.7, bevel=0)
            crystal(f"{name}_PauldronGem", 0.17 * SC, 0.1 * SC, 0.22 * SC, (x + sgn * th * 0.75, y, ZC + R * 0.25), (sgn, 0, 0.4),
                    M_GEM, legs_root, sides=6)
    top = Vector((x + sgn * th * 0.15, y, ZC - R * 0.55))
    knee = Vector((x + sgn * th * 0.32, y + (th * 0.35 if hind else -th * 0.1), FOOT_H + LEG_H * 0.5))
    ankle = Vector((x + sgn * th * 0.42, y + (-th * 0.05 if hind else -th * 0.3), FOOT_H * 0.9))
    link(f"{name}_Upper", top, knee, th * 0.95, M_LEG, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0.05 * SC, depth=th * 1.05)
    link(f"{name}_Lower", knee, ankle, th * 0.75, M_LEG, legs_root, up=(0, 1, 0), extra=th * 0.4,
         bevel=0, depth=th * 0.8)
    B(f"{name}_Knee", (th * 0.95, th * 0.5, th * 0.6), knee + Vector((0, -th * 0.38, 0)),
      mat=(M_PLATE if ARMOR >= 1 else M_SCALE), parent=legs_root)
    if ARMOR >= 1:   # bracelet métallique + point lumineux
        ring(f"{name}_Bracelet", th * 0.62, th * 0.22, th * 0.36, knee.lerp(ankle, 0.62), tuple(ankle - knee), M_PLATE2, legs_root, sides=8)
        dot(f"{name}_BraceDot", knee.lerp(ankle, 0.62) + Vector((sgn * th * 0.62, 0, 0)), 0.09 * SC, legs_root)
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
    for k in range(2):   # membranes entre les doigts
        plate(f"{name}_Web_{k}", [bases[k], tips[k] + (bases[k] - tips[k]) * 0.12,
                                  tips[k + 1] + (bases[k + 1] - tips[k + 1]) * 0.12, bases[k + 1]],
              0.05 * SC, M_FIN, legs_root)
    if ELBOW_FIN:
        fan_fin(f"{name}_ElbowFin", knee + Vector((sgn * th * 0.2, th * 0.25, 0)), (sgn * 0.5, 0.6, 0.6),
                (sgn * 0.3, 1.0, -0.2), 3, th * 1.2, th * 0.8, legs_root, ray_th=0.07 * SC, memb_t=0.04 * SC)

LEG_Y_F, LEG_Y_R = -TL * 0.3, TL * 0.3
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, LEG_Y_F, LEG_TH, False)
    leg(f"Legs_Back_{sgn}", sgn, LEG_Y_R, LEG_TH * 1.1, True)

# ----------------------------------------------------------
# 12. NAGEOIRES IMMENSES (à la place des ailes) : grandes pectorales en éventail sur les épaules
#     (rayons métalliques, points lumineux), pelviennes sur les hanches.
# ----------------------------------------------------------
for sgn in (-1, 1):
    proot = Vector((sgn * R * 0.72, -TL * 0.2, ZC + R * 0.62))
    wedge(f"Wings_PecBase_{sgn}", (0.8 * SC, 1.1 * SC, 0.6 * SC), proot, rot=(0, sgn * 30, 0),
          mat=(M_PLATE if ARMOR >= 1 else M_BODY), parent=wings_root, top_x=0.7, top_y=0.8, bevel=0)
    fan_fin(f"Wings_Pec_{sgn}", proot, (sgn * 1.0, -0.3, 0.3), (sgn * 0.6, 1.0, -0.05), PEC_RAYS,
            PEC_SPAN, PEC_SPAN * 0.5, wings_root, ray_th=0.15 * SC, memb_t=0.06 * SC, bulge=0.1,
            tip_spike=(0.6 * SC if not IS_BEBE else 0.0), dots=FIN_DOTS)
    vroot = Vector((sgn * R * 0.85, TL * 0.4, ZC + R * 0.35))
    fan_fin(f"Wings_Pelv_{sgn}", vroot, (sgn * 0.9, 0.15, 0.55), (sgn * 0.35, 1.0, 0.0), PELV_RAYS,
            PELV_SPAN, PELV_SPAN * 0.6, wings_root, ray_th=0.11 * SC, memb_t=0.05 * SC, dots=(1 if FIN_DOTS else 0))

# ----------------------------------------------------------
# 13. QUEUE DE POISSON : courbe Catmull-Rom, dos blindé, points et lignes lumineux,
#     crête-nageoire continue, nageoires latérales, grande caudale en V à rayons métalliques
# ----------------------------------------------------------
TAIL_CTRL = [
    HIP,
    HIP + Vector((0, TAIL_L * 0.3, -R * 0.32)),
    HIP + Vector((0, TAIL_L * 0.62, -R * 0.22)),
    HIP + Vector((0, TAIL_L * 0.85, TAIL_RISE * 0.45)),
    HIP + Vector((0, TAIL_L, TAIL_RISE)),
]
TAIL_R_KEYS = [(0.0, R * 0.86), (0.35, R * 0.62), (0.7, R * 0.38), (1.0, R * 0.22)]
TAIL_DORSAL = [(0.0, DORSAL_H * 0.7), (0.5, DORSAL_H * 0.5), (0.85, DORSAL_H * 0.3), (1.0, DORSAL_H * 0.2)]
TSP = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TSP) - 1
tb, tt_ = [], []
for i in range(TN):
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    Rm = seg_matrix(t, d, side)
    wk = 1.04 - 0.3 * s
    hk = 0.94 + 0.2 * s
    box(f"Tail_Seg_{i}", (2 * r * wk, Ln * 1.32, 2 * r * hk), mid, Rm, M_BODY, tail_root,
        bevel=(0.06 * SC if s < 0.3 else 0))
    if ARMOR >= 1 and s < 0.7:
        wedge(f"Tail_Plate_{i}", (2 * r * wk * 0.92, Ln * 1.2, 0.32 * SC * ARMOR_K), mid + d * (r * hk * 0.98), Rm,
              M_PLATE if i % 2 == 0 else M_PLATE2, tail_root, top_x=0.72, top_y=0.88, bevel=0)
    else:
        B(f"Tail_Back_{i}", (2 * r * wk * 0.68, Ln * 0.95, 0.14 * SC), mid + d * (r * hk), Rm, M_SCALE, tail_root)
    if s < 0.72:
        B(f"Tail_Belly_{i}", (2 * r * wk * 0.75, Ln * 0.78, 0.18 * SC), mid - d * (r * hk * 0.98), Rm, M_BELLY, tail_root)
    if i % 3 == 0 and s < 0.75:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.07 * SC, r * 0.95, mid + side * sgn * (r * wk * 0.98) - d * r * 0.3,
                  side * sgn * 0.25 + t, pick([M_SCALE, M_BODY]), tail_root, up=(sgn, 0, 0))
    if s < 0.85:
        flank_glow("Tail", i, mid, Ln, r, t, d, side, Rm, wk=wk, rows=max(1, DOT_ROWS - 1))
    if s < 0.88:
        h = keyed(TAIL_DORSAL, s) * SC
        bpt = TSP[i] + d * r * hk * (0.85 + (0.3 if ARMOR >= 1 and s < 0.7 else 0))
        tb.append(bpt)
        tt_.append(bpt + (d + t * 0.55).normalized() * h)
comb_fin("Tail_Dorsal", tb, tt_, tail_root, ray_th=0.09 * SC, memb_t=0.05 * SC, ray_every=DORSAL_EVERY)

for k in range(TAIL_FINLETS):
    s = 0.35 + 0.25 * k
    i = min(TN - 1, int(s * TN))
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    for sgn in (-1, 1):
        fan_fin(f"Tail_Finlet_{k}_{sgn}", mid + side * sgn * r * 0.8, side * sgn * 0.9 + t * 0.3 + d * 0.2,
                side * sgn * 0.3 + t, 3, r * 2.0, r * 1.3, tail_root, ray_th=0.07 * SC, memb_t=0.04 * SC)

tip = TSP[-1]
ct, cd, cs = frame(TSP[-1] - TSP[-2])
B("Tail_Collar", (R * 0.46, 0.4 * SC, R * 0.6), tip - ct * 0.1 * SC, seg_matrix(ct, cd, cs), M_PLATE, tail_root)
crystal("Tail_Gem", 0.2 * SC, 0.12 * SC, 0.24 * SC, tip + cd * R * 0.3, cd, M_GEM, tail_root, up=(1, 0, 0), sides=6)
froot = tip + ct * 0.05 * SC
fan_fin("Tail_CaudalTop", froot, ct * 0.45 + cd * 1.0, ct * 1.0 + cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L, CAUDAL_L * 0.55, tail_root, ray_th=0.14 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.4 * SC if not IS_BEBE else 0.0), dots=(1 if IS_ADULTE else 0))
fan_fin("Tail_CaudalBot", froot, ct * 0.55 - cd * 1.0, ct * 1.0 - cd * 0.18, CAUDAL_RAYS,
        CAUDAL_L * 0.85, CAUDAL_L * 0.5, tail_root, ray_th=0.14 * SC, memb_t=0.06 * SC, bulge=0.08,
        tip_spike=(0.35 * SC if not IS_BEBE else 0.0), dots=(1 if IS_ADULTE else 0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (MYTHIQUE) + FX
#     Mythique : plaques blindées en métal sur la tête, le dos, les flancs, la queue et les pattes ;
#     gemmes multiples (front, tempes, poitrail, épaules, halo, queue) ; halo flottant derrière la tête ;
#     points et lignes bioluminescents partout ; nageoires immenses ; FX denses :
#     anneau d'éclats et de bulles en orbite autour du corps + bulles qui montent.
# ----------------------------------------------------------
def bubble_mesh(r):
    """Bulle low-poly : octaèdre (6 sommets, 8 triangles)."""
    v = [(r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r)]
    f = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    return mesh_from("bubble", v, f)

if ADD_FLOATING_FX:
    cy = (CHEST.y + HIP.y) / 2
    rx = R * 1.7 + PEC_SPAN * 0.6
    ry = TL * 0.85 + 1.0
    for k in range(FX_N):
        a = k * 2 * math.pi / FX_N + random.uniform(-0.12, 0.12)
        z = ZC + R * 0.3 + math.sin(a * 2.0) * R * 0.9 + random.uniform(-0.4, 0.4) * R
        p = Vector((math.cos(a) * rx, cy + math.sin(a) * ry, z))
        rot = (random.uniform(0, 45), random.uniform(0, 45), random.uniform(0, 45))
        if k % 3 == 0:   # éclat de cristal cyan
            place(f"FX_Shard_{k}", crystal_mesh(FX_SIZE * 0.5, FX_SIZE * 0.2, FX_SIZE * 0.75, 6), M_GEM, p, rot, master)
        elif k % 3 == 1:
            place(f"FX_Pearl_{k}", crystal_mesh(FX_SIZE * 0.5, FX_SIZE * 0.18, FX_SIZE * 0.4, 6), M_PEARL, p, rot, master)
        else:
            place(f"FX_Bubble_{k}", bubble_mesh(FX_SIZE * random.uniform(0.6, 1.2)), M_BUBBLE, p, rot, master)
    top_z = HEAD_POS.z + HS * 2.0
    for k in range(FX_UP):   # bulles qui montent autour de la tête et du dos
        p = Vector((random.uniform(-1, 1) * (R * 2.2 + 1.0), random.uniform(-TL * 0.8, TL * 0.6), random.uniform(ZC, top_z)))
        place(f"FX_Rise_{k}", bubble_mesh(FX_SIZE * random.uniform(0.35, 0.7)), M_BUBBLE if k % 2 else M_GEM,
              p, (random.uniform(0, 45), random.uniform(0, 45), 0), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
