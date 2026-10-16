import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Marée · Bébé
#  Rare · Eau · Aquatique · monde 3
#  - Bébé mignon et fin : grosse tête, très grands yeux, museau court, pas de crocs
#  - Signes distinctifs : CRÊTE EN VAGUE DÉFERLANTE (tête + dos, bleu roi -> turquoise -> écume) et VOLUTES de vagues blanches sur les flancs
#  - Dégradé bleu roi sur le dos vers turquoise sur les pattes et le bout de la queue, ventre blanc ; cou en arche, queue de poisson sinueuse
#  - Rare : crête double, cornes à 2 pointes, motif secondaire (volutes), accent lumineux discret (iris, pointes d'écume)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3308)            # même dragon à chaque exécution
TAG = "MAREE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 4       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 4000          # budget de triangles de ce stade et de cette rareté
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
GLOW        = 0.5            # intensité de l'accent lumineux
R           = 1.0               # rayon du torse
TORSO_L     = 3.0         # longueur du torse
LEG_H       = 0.6            # hauteur du dessous du ventre
NECK_L      = 1.5          # longueur du cou
NECK_REACH  = 0.8      # avancée de la tête
NECK_DROP   = 0.55      # hauteur de la tête par rapport au sommet
HEAD_SCALE  = 1.5      # taille de la tête
SNOUT_K     = 0.65        # longueur du museau
FANGS       = 0              # crocs par côté
EAR_L       = 2.0           # longueur des nageoires-oreilles
EAR_RAYS    = 3
HORN_L      = 0.8          # longueur des cornes
CREST_K     = 0.9         # taille de la crête en vague du crâne
WAVE_N      = 5            # plaques par vague
CHEEK_N     = 0
STEP        = 0.62           # pas des segments du corps
CREST_H     = 1.1         # hauteur des vagues dorsales
WAVE_EVERY  = 3       # une vague tous les n segments
SWIRLS      = 1            # volutes par flanc
SWIRL_N     = 5          # segments par bras de volute
LEG_SWIRL   = False        # volute sur les cuisses
LEG_TH      = 0.75         # épaisseur des pattes
PADDLE      = 1.0         # taille des pieds
PEC_SPAN    = 2.6        # longueur des pectorales
PEC_RAYS    = 3
TAIL_L      = 3.4          # longueur de la queue
TAIL_STEP   = 0.62
TAIL_RISE   = 0.9
TAIL_SWAY   = 0.5       # amplitude du S de la queue
CAUDAL_L    = 2.0        # taille des lobes de la caudale
CAUDAL_RAYS = 3
FX_N        = 3
FX_SIZE     = 0.3

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Dégradé bleu roi (dos) -> turquoise (pattes, bout de queue), ventre blanc, volutes et écume blanches.
#    Rare : un motif secondaire (volutes de vagues), crête double, accent lumineux discret
#    (iris + pointes d'écume, strength <= 1.5).
# ----------------------------------------------------------
def lerp_hex(a, b, t):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(round(ca[k] + (cb[k] - ca[k]) * t)) for k in range(3))

GRAD_STOPS = ["#1F5FBF", "#1B72C4", "#1E88C8", "#25A0CC", "#2FB8D0"]      # bleu roi -> turquoise
M_G = [get_mat(f"Grad{k}", GRAD_STOPS[k], 0.40) for k in range(5)]       # dégradé du dos aux pattes
M_BODY   = M_G[1]
M_DARK   = get_mat("BodyDark",  "#133973", 0.50)   # sourcils, ligne de bouche, dessous des nageoires
M_SCALE  = get_mat("BodyScale", "#17468D", 0.45)   # plaques du dos, genouillères
M_BELLY  = get_mat("Belly",     "#F0F6F8", 0.50)   # ventre en plaques, plastron, mâchoire
M_HORN   = get_mat("Horn",      "#1A4FA8", 0.40)   # base des cornes
M_HORNT  = get_mat("HornTip",   "#8FD6EA", 0.35)   # pointes des cornes
M_CREST  = get_mat("Crest",     "#2FB8D0", 0.30)   # crêtes en vague (turquoise)
M_CREST2 = get_mat("Crest2",    "#8FD6EA", 0.30)   # crêtes en vague (bleu clair)
M_MARK   = get_mat("Mark",      "#F0F6F8", 0.35)   # volutes de vagues blanches
M_FOAM   = get_mat("Foam",      "#F0F6F8", 0.30, emission="#8FD6EA", strength=0.9 * GLOW)  # pointes d'écume (accent lumineux)
M_SWIRL2 = get_mat("SwirlLight", "#8FD6EA", 0.30, emission="#8FD6EA", strength=0.8 * GLOW)  # 2e bras des volutes (accent)
M_FIN    = get_mat("Fin",       "#8FD6EA", 0.30, alpha=0.82)   # membranes des nageoires
M_FIN2   = get_mat("FinTeal",   "#2FB8D0", 0.30, alpha=0.82)   # membranes turquoise
M_RAY    = get_mat("FinRay",    "#1F5FBF", 0.40)   # rayons des nageoires
M_CLAW   = get_mat("Claw",      "#F0F6F8", 0.35)   # griffes, crocs
M_WHITE  = get_mat("EyeWhite",  "#F2F2F2", 0.30)
M_IRIS   = get_mat("Iris",      "#1A6AD0", 0.25, emission="#4FB4FF", strength=1.5 * GLOW)  # lueur des yeux
M_BLACK  = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles
M_NOSE   = get_mat("Nostril",   "#103958", 0.50)   # narines
M_BUBBLE = get_mat("Bubble",    "#D6F6FF", 0.10, alpha=0.55)   # bulles flottantes (FX)
FINS = [M_FIN, M_FIN2]
CURL_MATS = [M_HORN, M_G[0], M_G[3], M_CREST, M_CREST2, M_FOAM]   # une vague : bleu roi -> turquoise -> écume

def grad(t):
    """Matériau du dégradé pour t dans [0, 1] (0 = dos bleu roi, 1 = turquoise)."""
    return M_G[max(0, min(4, int(round(t * 4))))]

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Marée = vague : corps long et fin, cou en arche (comme une vague qui déferle), tête qui plonge.
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = R / 1.0                                     # échelle des petits détails
ZC = LEG_H + R * 0.9                             # hauteur du centre du torse
TL = TORSO_L
CHEST = Vector((0, -TL * 0.42, ZC + R * 0.1))    # poitrail (bas du cou)
HIP = Vector((0, TL * 0.5, ZC - R * 0.05))       # hanches (début de la queue)
L_N = NECK_L
# Le cou monte en arrière du poitrail, passe par un sommet puis plonge vers l'avant : arche de vague
NECK_PTS = [CHEST + Vector((0, -L_N * NECK_REACH, L_N * NECK_DROP)),
            CHEST + Vector((0, -L_N * 0.42, L_N * 1.0)),
            CHEST + Vector((0, L_N * 0.1, L_N * 0.62)),
            CHEST]
NECK_TOP = NECK_PTS[0]
HEAD_POS = NECK_TOP + Vector((0, -0.35, -0.05)) * HEAD_SCALE
HEAD_PITCH = 20                                  # degrés : la tête plonge vers l'avant

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

def fan_fin(name, root, d0, d1, n, L0, L1, parent, ray_th, memb_t, bulge=0.1, tip_spike=0.0, mats=None):
    """NAGEOIRE EN ÉVENTAIL : n rayons fins qui partent de 'root', du rayon d'attaque d0 (L0)
    au rayon de fuite d1 (L1), avec des membranes translucides entre les rayons."""
    mats = mats or FINS
    root, d0, d1 = Vector(root), Vector(d0).normalized(), Vector(d1).normalized()
    nrm = d0.cross(d1)
    up = tuple(nrm.normalized()) if nrm.length > 1e-4 else (0, 0, 1)
    tips = []
    for k in range(n):
        f = k / max(1, n - 1)
        dk = d0.lerp(d1, f).normalized()
        Lk = L0 + (L1 - L0) * f + L0 * bulge * math.sin(math.pi * f)
        tip = root + dk * Lk
        bar(f"{name}_Ray_{k}", root, tip, ray_th * (1.3 if k == 0 else 1.0), M_RAY, parent, up=up, depth=ray_th * 0.7)
        tips.append(tip)
    for k in range(n - 1):
        plate(f"{name}_Memb_{k}", [root, root.lerp(tips[k], 0.93), root.lerp(tips[k + 1], 0.93)], memb_t,
              mats[k % 2], parent)
    if tip_spike > 0:
        shard(f"{name}_TipSpike", ray_th * 2.0, ray_th * 1.3, tip_spike, tips[0], tips[0] - root, M_HORNT, parent, up=up)
    return tips

def wave_curl(name, base, up, fwd, size, width, parent, side, n=5, thick=0.07, last_glow=True):
    """CRÊTE EN VAGUE DÉFERLANTE (signe distinctif) : un arc de plaques qui monte puis se recourbe vers
    l'avant. Couleurs : bleu roi à la base, turquoise au milieu, blanc d'écume émissif à la pointe.
    base = pied de la vague, up = direction de montée, fwd = direction du déferlement."""
    base, up, fwd, side = Vector(base), Vector(up).normalized(), Vector(fwd).normalized(), Vector(side).normalized()
    ctr = base + fwd * (size * 0.85)
    outer = []
    for k in range(n + 1):
        a = math.radians(170.0 * k / n)
        outer.append(base + up * (size * math.sin(a) * 0.95) + fwd * (size * 0.85 * (1 - math.cos(a))))
    # arc intérieur : même courbe rapprochée du centre, de plus en plus fine vers la pointe (lame en croissant)
    inner = [ctr + (p - ctr) * (0.5 + 0.45 * k / n) for k, p in enumerate(outer)]
    pts = outer
    for k in range(n):
        m = CURL_MATS[min(len(CURL_MATS) - 1, int(k * (len(CURL_MATS) - 1) / max(1, n - 1)))]
        if k == n - 1 and not last_glow:
            m = M_CREST2
        plate(f"{name}_C{k}", [inner[k], outer[k], outer[k + 1], inner[k + 1]], width * (1.0 - 0.4 * k / n), m, parent)
    return pts

def swirl(name, center, out, axis_a, axis_b, size, parent, arm_mat, arm2_mat, turns=1.25, n=6, th=0.17):
    """VOLUTE DE VAGUE stylisée sur le flanc : spirale à deux bras (blanc + bleu clair lumineux) posée
    sur la peau. center = centre, out = normale vers l'extérieur, axis_a / axis_b = plan de la volute."""
    center, out = Vector(center), Vector(out).normalized()
    A, Bv = Vector(axis_a).normalized(), Vector(axis_b).normalized()
    for arm, mat in enumerate((arm_mat, arm2_mat)):
        ph = math.pi * arm
        prev = None
        for k in range(n + 1):
            u = k / n
            ang = ph + 2 * math.pi * turns * u
            rho = size * (1.0 - 0.82 * u)
            p = center + A * (rho * math.cos(ang)) + Bv * (rho * math.sin(ang)) + out * (0.03 * size)
            if prev is not None:
                link(f"{name}_{arm}_{k}", prev, p, th * size * (1.15 - 0.5 * u) * (1.0 if arm == 0 else 0.7), mat, parent,
                     up=tuple(out), extra=th * size * 0.4, bevel=0, depth=0.1 * size)
            prev = p

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Tête fine et allongée, museau en pointe de proue, deux cornes à 2 pointes, nageoires-oreilles en rubans
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

SKULL = (1.55, 1.7, 1.4)
hwedge("Skull", SKULL, (0, 0, 0), mat=M_G[0], top_x=0.82, top_y=0.84, bevel=0.12)
hwedge("Snout", (1.05, 1.9 * SNOUT_K, 0.74), (0, -0.75 - 0.95 * SNOUT_K, -0.28), mat=M_G[1], top_x=0.7, top_y=0.9,
       shift_y=-0.08, bevel=0.07)
hbox("SnoutBridge", (0.5, 1.5 * SNOUT_K, 0.12), (0, -0.7 - 0.9 * SNOUT_K, 0.1), mat=M_CREST)
hbox("Jaw", (0.9, 1.7 * SNOUT_K, 0.26), (0, -0.7 - 0.9 * SNOUT_K, -0.7), mat=M_BELLY, bevel=0.03)
hbox("Chin", (0.85, 0.7, 0.26), (0, -0.2, -0.68), mat=M_BELLY)
hbox("MouthLine", (1.04, 1.8 * SNOUT_K, 0.05), (0, -0.75 - 0.95 * SNOUT_K, -0.64), mat=M_DARK)
SNOUT_FRONT = -0.75 - 1.9 * SNOUT_K
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.16, 0.22, 0.06), (sgn * 0.24, SNOUT_FRONT + 0.3, 0.08), mat=M_NOSE)

# Yeux : blanc, iris bleu (lueur), pupille ronde (bébé) puis fendue, sourcils
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.95, 1.0, 0.75, 0.85, 0.42, 0.6
elif IS_ADO:
    EW, EH, IW, IH, PW, PH = 0.66, 0.54, 0.48, 0.46, 0.11, 0.42
else:
    EW, EH, IW, IH, PW, PH = 0.62, 0.5, 0.44, 0.42, 0.1, 0.4
for sgn in (-1, 1):
    ey, ez = -0.28, 0.12
    ex = SKULL[0] / 2 * 0.99
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * ex, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * (ex + 0.04), ey - 0.03, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * (ex + 0.08), ey - 0.05, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.22), (sgn * (ex + 0.11), ey - 0.18, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * (ex + 0.11), ey + 0.14, ez - 0.2), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.15, EW + 0.34, 0.18 if IS_ADO else 0.24),
             (sgn * (ex + 0.02), ey - 0.06, ez + EH / 2 + 0.12), rot=(-14 if IS_ADO else -20, 0, 0), mat=M_DARK)

# Crocs blancs (ado : 2 par côté ; adulte : 3)
if not IS_BEBE:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.4 + k * 0.4
            hshard(f"Fang_{sgn}_{k}", 0.16, 0.16, 0.22 + 0.05 * FANGS, (sgn * 0.42, fy, -0.58), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Nageoires-oreilles : longs rubans translucides rejetés vers l'arrière (signe distinctif)
for sgn in (-1, 1):
    fan_fin(f"Head_EarFin_{sgn}", hv((sgn * 0.74, 0.35, 0.15)), (sgn * 0.45, 1.0, 0.5), (sgn * 0.55, 1.0, -0.35),
            EAR_RAYS, EAR_L * HS, EAR_L * 0.5 * HS, H, ray_th=0.09 * HS, memb_t=0.05 * HS, bulge=0.06,
            mats=[M_FIN, M_FIN2])

# Cornes bleues à DEUX POINTES : branche principale vers l'arrière + pointe avant plus courte
for sgn in (-1, 1):
    p0 = Vector((sgn * 0.4, 0.2, 0.62))
    p1 = p0 + Vector((sgn * 0.1, 0.5, 0.35)) * HORN_L
    p2 = p1 + Vector((sgn * 0.05, 0.55, 0.05)) * HORN_L
    bar(f"Head_Horn_{sgn}_0", hv(p0), hv(p1), 0.22 * HS, M_HORN, H, up=(1, 0, 0))
    shard(f"Head_Horn_{sgn}_1", 0.22 * HS, 0.22 * HS, (p2 - p1).length * HS * 1.1, hv(p1), p2 - p1, M_HORNT, H)
    if not IS_BEBE:
        q = p0 + (p1 - p0) * 0.55
        shard(f"Head_Horn_{sgn}_2", 0.18 * HS, 0.18 * HS, 0.55 * HORN_L * HS, hv(q), (sgn * 0.45, -0.7, 0.7), M_HORNT, H)

# CRÊTE EN VAGUE sur le crâne (double : grande vague + petite vague derrière)
wave_curl("Head_Wave", hv((0, 0.5, 0.62)), (0, 0.15, 1.0), (0, -1.0, -0.2), 1.25 * HS * CREST_K, 0.6 * HS, H, (1, 0, 0), n=WAVE_N)
if not IS_BEBE:
    wave_curl("Head_Wave2", hv((0, 0.75, 0.55)), (0, 0.3, 1.0), (0, -1.0, -0.15), 0.75 * HS * CREST_K, 0.4 * HS, H, (1, 0, 0), n=4)

# Nageoires de joue (ado / adulte)
if not IS_BEBE:
    for sgn in (-1, 1):
        for k in range(CHEEK_N):
            base = hv((sgn * 0.72, -0.05 + k * 0.22, -0.4 - k * 0.1))
            tip = base + Vector((sgn * 0.5, 0.9, -0.3 - 0.2 * k)) * HS * 0.8
            plate(f"Head_Cheek_{sgn}_{k}", [base, base.lerp(tip, 0.4) + Vector((0, 0, 0.2 * HS)), tip,
                                            base.lerp(tip, 0.4) - Vector((0, 0, 0.12 * HS))], 0.05 * HS, FINS[k % 2], H)

# ----------------------------------------------------------
# 10. CORPS : courbe Catmull-Rom (cou en arche + torse), segments fins, dégradé de couleurs,
#     ventre en plaques, crête de vagues dorsale (double), volutes sur les flancs
# ----------------------------------------------------------
BODY_CTRL = NECK_PTS + [Vector((0, -TL * 0.08, ZC + R * 0.08)), Vector((0, TL * 0.24, ZC)), HIP]
SPINE = resample(sample_curve(BODY_CTRL), STEP)
N = len(SPINE) - 1
cum = [0.0]
for i in range(N):
    cum.append(cum[-1] + (SPINE[i + 1] - SPINE[i]).length)
i_chest = min(range(len(SPINE)), key=lambda j: (SPINE[j] - CHEST).length)
S_CHEST = cum[i_chest] / cum[-1]
BODY_R_KEYS = [(0.0, R * 0.52), (S_CHEST * 0.7, R * 0.62), (S_CHEST, R * 0.88), (S_CHEST + (1 - S_CHEST) * 0.2, R),
               (S_CHEST + (1 - S_CHEST) * 0.7, R * 0.96), (1.0, R * 0.8)]

def seg_info(spine, i, keys):
    p1, p2 = spine[i], spine[i + 1]
    s = (i + 0.5) / (len(spine) - 1)
    t, d, side = frame(p2 - p1)
    return (p1 + p2) / 2, (p2 - p1).length, s, keyed(keys, s), t, d, side

FWD = Vector((0, -1, 0))
def fwd_for(d):
    f = FWD - d * FWD.dot(d)
    return f.normalized() if f.length > 1e-3 else FWD

torso_segs = []
dorsal_b, dorsal_t = [], []
for i in range(N):
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    Rm = seg_matrix(t, d, side)
    neck = s < S_CHEST
    box(f"Body_Seg_{i}", (2 * r * 1.0, Ln * 1.32, 2 * r * 0.92), mid, Rm, M_G[1 if not neck else 0], body_root, bevel=0.07 * SC)
    # flanc bas turquoise (dégradé : le dos est bleu roi, le bas du flanc est turquoise)
    B(f"Body_Flank_{i}", (2 * r * 1.03, Ln * 1.0, r * 0.5), mid - d * (r * 0.42), Rm, M_G[3], body_root)
    if s > S_CHEST * 0.25:
        B(f"Body_Belly_{i}", (2 * r * 0.72, Ln * 0.78, 0.18 * SC), mid - d * (r * 0.92 * 0.97), Rm, M_BELLY, body_root)
    Rt = Rm @ Euler((math.radians(-6), 0, 0)).to_matrix()
    B(f"Body_Back_{i}", (2 * r * 0.7, Ln * 0.95, 0.15 * SC), mid + d * (r * 0.92 * 0.98), Rt, M_G[0], body_root)
    if not neck:
        torso_segs.append(i)
    bpt = mid + d * (r * 0.9)
    dorsal_b.append(bpt)
    dorsal_t.append(bpt + d * (CREST_H * 0.35 * SC) * (0.7 + 0.3 * math.sin(i)))
    # grande vague dorsale tous les WAVE_EVERY segments (la taille suit la hauteur du dos)
    if i % WAVE_EVERY == 1 and s > S_CHEST * 0.15:
        fade = 1.0 - 0.45 * max(0.0, (s - S_CHEST) / max(1e-3, 1 - S_CHEST))
        wave_curl(f"Body_Wave_{i}", bpt, d + t * 0.35, fwd_for(d), CREST_H * SC * fade, 0.55 * SC, body_root, side, n=4)
        if not IS_BEBE and i % (WAVE_EVERY * 2) == 1:    # petite vague de la 2e rangée de la crête double
            for sgn in (-1, 1):
                wave_curl(f"Body_WaveS_{i}_{sgn}", bpt + side * sgn * r * 0.5, d + t * 0.3 + side * sgn * 0.4, fwd_for(d),
                          CREST_H * SC * fade * 0.45, 0.28 * SC, body_root, side, n=3)
comb_pts = len(dorsal_b)
for k in range(comb_pts - 1):
    plate(f"Body_DorsalFin_{k}", [dorsal_b[k], dorsal_b[k + 1], dorsal_t[k + 1], dorsal_t[k]], 0.05 * SC,
          FINS[k % 2], body_root)

# Plastron blanc sur le poitrail
mid, Ln, s, r, t, d, side = seg_info(SPINE, i_chest, BODY_R_KEYS)
box("Body_Plastron", (r * 1.3, 0.28 * SC, r * 1.0), CHEST + Vector((0, -r * 0.82, -r * 0.35)), (16, 0, 0),
    M_BELLY, body_root, bevel=0.05 * SC)

# MOTIF : volutes de vagues stylisées sur les flancs du torse (signe distinctif)
sw_idx = [torso_segs[int((len(torso_segs) - 1) * (k + 0.5) / SWIRLS)] for k in range(SWIRLS)] if SWIRLS else []
for k, i in enumerate(sw_idx):
    mid, Ln, s, r, t, d, side = seg_info(SPINE, i, BODY_R_KEYS)
    for sgn in (-1, 1):
        swirl(f"Body_Swirl_{k}_{sgn}", mid + side * sgn * r * 1.04 + d * r * 0.12, side * sgn, -t, d, r * 1.0, body_root,
              M_MARK, M_SWIRL2, turns=1.2, n=SWIRL_N)

# ----------------------------------------------------------
# 11. PATTES FINES : épaule / cuisse en wedge, jambe, genouillère, pied palmé, 3 doigts + 3 griffes blanches,
#     petite nageoire dorsale sur l'arrière de la jambe, volute sur la cuisse (ado / adulte)
# ----------------------------------------------------------
FOOT_H = 0.26 * SC

def leg(name, sgn, y, th, hind):
    x = sgn * R * 0.8
    pad = PADDLE * (1.15 if hind else 1.0)
    wedge(f"{name}_Thigh", (th * 1.25, th * (1.7 if hind else 1.45), R * 1.2),
          (x + sgn * th * 0.1, y, ZC - R * 0.3), mat=M_G[2], parent=legs_root, top_x=0.8, top_y=0.75, bevel=0.08 * SC)
    top = Vector((x + sgn * th * 0.15, y, ZC - R * 0.55))
    knee = Vector((x + sgn * th * 0.32, y + (th * 0.5 if hind else -th * 0.1), FOOT_H + LEG_H * 0.5))
    ankle = Vector((x + sgn * th * 0.4, y + (-th * 0.1 if hind else -th * 0.3), FOOT_H * 0.9))
    link(f"{name}_Upper", top, knee, th * 0.9, M_G[2], legs_root, up=(0, 1, 0), extra=th * 0.4, bevel=0.04 * SC, depth=th)
    link(f"{name}_Lower", knee, ankle, th * 0.7, M_G[3], legs_root, up=(0, 1, 0), extra=th * 0.4, bevel=0, depth=th * 0.75)
    B(f"{name}_Knee", (th * 0.85, th * 0.5, th * 0.5), knee + Vector((0, -th * 0.36, 0)), mat=M_SCALE, parent=legs_root)
    if not IS_BEBE:   # nageoire dorsale à l'arrière de la jambe
        shard(f"{name}_LegFin", th * 0.3, th * 0.1, th * 1.1, knee + Vector((0, th * 0.35, 0)), (sgn * 0.15, 0.7, 0.8), M_CREST, legs_root,
              up=(1, 0, 0))
    F = Vector((ankle.x, ankle.y - th * 0.3, FOOT_H / 2))
    box(f"{name}_Foot", (th * 1.2 * pad, th * 1.15 * pad, FOOT_H), F, mat=M_G[4], parent=legs_root, bevel=0.04 * SC)
    bases, tips = [], []
    for k in (-1, 0, 1):
        b = F + Vector((k * th * 0.36 * pad, -th * 0.45 * pad, -FOOT_H * 0.2))
        tp = F + Vector((k * th * 0.85 * pad, -th * 1.3 * pad, -FOOT_H * 0.3))
        bar(f"{name}_Toe_{k}", b, tp, th * 0.22, M_G[4], legs_root, up=(0, 0, 1), depth=FOOT_H * 0.55)
        shard(f"{name}_Claw_{k}", th * 0.18, th * 0.14, th * 0.4, tp - Vector((0, th * 0.05, 0)), (k * 0.3, -1, -0.25), M_CLAW,
              legs_root)
        bases.append(b); tips.append(tp)
    for k in range(2):
        plate(f"{name}_Web_{k}", [bases[k], tips[k] + (bases[k] - tips[k]) * 0.12,
                                  tips[k + 1] + (bases[k + 1] - tips[k + 1]) * 0.12, bases[k + 1]], 0.05 * SC, M_FIN, legs_root)
    if LEG_SWIRL:
        swirl(f"{name}_Swirl", Vector((x + sgn * th * 0.78, y, ZC - R * 0.42)), (sgn, 0, 0), (0, -1, 0), (0, 0, 1), th * 0.55,
              legs_root, M_MARK, M_SWIRL2, turns=1.0, n=5)

LEG_Y_F, LEG_Y_R = -TL * 0.3, TL * 0.3
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, LEG_Y_F, LEG_TH, False)
    leg(f"Legs_Back_{sgn}", sgn, LEG_Y_R, LEG_TH * 1.1, True)

# ----------------------------------------------------------
# 12. NAGEOIRES (à la place des ailes) : longues pectorales balayées vers l'arrière (voiles),
#     petites pelviennes
# ----------------------------------------------------------
for sgn in (-1, 1):
    proot = Vector((sgn * R * 0.8, -TL * 0.2, ZC + R * 0.55))
    B(f"Wings_PecBase_{sgn}", (0.5 * SC, 0.9 * SC, 0.4 * SC), proot, rot=(0, sgn * 25, 0), mat=M_G[1], parent=wings_root)
    fan_fin(f"Wings_Pec_{sgn}", proot, (sgn * 0.55, 0.9, 0.7), (sgn * 0.5, 1.0, -0.35), PEC_RAYS, PEC_SPAN, PEC_SPAN * 0.4,
            wings_root, ray_th=0.12 * SC, memb_t=0.06 * SC, bulge=0.08, tip_spike=(0.5 * SC if not IS_BEBE else 0.0))
    vroot = Vector((sgn * R * 0.85, TL * 0.4, ZC + R * 0.3))
    fan_fin(f"Wings_Pelv_{sgn}", vroot, (sgn * 0.6, 0.9, 0.5), (sgn * 0.4, 1.0, -0.2), 3, PEC_SPAN * 0.5, PEC_SPAN * 0.3,
            wings_root, ray_th=0.09 * SC, memb_t=0.05 * SC)

# ----------------------------------------------------------
# 13. QUEUE DE POISSON LONGUE ET SINUEUSE : courbe Catmull-Rom en S, dégradé vers le turquoise,
#     petites vagues sur la crête, nageoire caudale en croissant à rayons
# ----------------------------------------------------------
SW = R * TAIL_SWAY
TAIL_CTRL = [
    HIP,
    HIP + Vector((SW * 0.5, TAIL_L * 0.25, -R * 0.3)),
    HIP + Vector((-SW, TAIL_L * 0.52, -R * 0.3)),
    HIP + Vector((SW, TAIL_L * 0.8, TAIL_RISE * 0.3)),
    HIP + Vector((0, TAIL_L, TAIL_RISE)),
]
TAIL_R_KEYS = [(0.0, R * 0.78), (0.35, R * 0.52), (0.7, R * 0.32), (1.0, R * 0.18)]
TSP = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TSP) - 1
tb, tt_ = [], []
for i in range(TN):
    mid, Ln, s, r, t, d, side = seg_info(TSP, i, TAIL_R_KEYS)
    Rm = seg_matrix(t, d, side)
    wk, hk = 1.0 - 0.3 * s, 0.94 + 0.2 * s
    box(f"Tail_Seg_{i}", (2 * r * wk, Ln * 1.32, 2 * r * hk), mid, Rm, grad(0.25 + 0.75 * s), tail_root,
        bevel=(0.06 * SC if s < 0.3 else 0))
    B(f"Tail_Back_{i}", (2 * r * wk * 0.66, Ln * 0.95, 0.13 * SC), mid + d * (r * hk), Rm, grad(s * 0.7), tail_root)
    if s < 0.7:
        B(f"Tail_Belly_{i}", (2 * r * wk * 0.72, Ln * 0.78, 0.16 * SC), mid - d * (r * hk * 0.98), Rm, M_BELLY, tail_root)
    bpt = mid + d * (r * hk * 0.9)
    tb.append(bpt)
    tt_.append(bpt + (d + t * 0.4).normalized() * (CREST_H * 0.4 * SC) * (1 - 0.6 * s))
    if i % 3 == 1 and s < 0.85:
        wave_curl(f"Tail_Wave_{i}", bpt, d + t * 0.3, fwd_for(d) * 0.0 + (-t), CREST_H * 0.55 * SC * (1 - 0.6 * s), 0.35 * SC * (1 - 0.4 * s),
                  tail_root, side, n=3)
for k in range(len(tb) - 1):
    plate(f"Tail_DorsalFin_{k}", [tb[k], tb[k + 1], tt_[k + 1], tt_[k]], 0.05 * SC, FINS[k % 2], tail_root)

# Nageoire caudale en croissant : deux lobes recourbés (rayons longs au bord, courts au centre)
tip = TSP[-1]
ct, cd, cs = frame(TSP[-1] - TSP[-2])
B("Tail_Collar", (R * 0.36, 0.3 * SC, R * 0.45), tip - ct * 0.1 * SC, seg_matrix(ct, cd, cs), M_G[4], tail_root)
froot = tip + ct * 0.05 * SC
fan_fin("Tail_CaudalTop", froot, ct * 0.3 + cd * 1.0, ct * 1.0 + cd * 0.1, CAUDAL_RAYS, CAUDAL_L, CAUDAL_L * 0.4, tail_root,
        ray_th=0.1 * SC, memb_t=0.05 * SC, bulge=0.05, tip_spike=0.4 * SC if not IS_BEBE else 0.0)
fan_fin("Tail_CaudalBot", froot, ct * 0.3 - cd * 1.0, ct * 1.0 - cd * 0.1, CAUDAL_RAYS, CAUDAL_L, CAUDAL_L * 0.4, tail_root,
        ray_th=0.1 * SC, memb_t=0.05 * SC, bulge=0.05, tip_spike=0.4 * SC if not IS_BEBE else 0.0)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Motif secondaire : volutes de vagues sur les flancs et les cuisses. Crête double (grande vague +
#     petites vagues). Cornes à 2 pointes. Accent lumineux discret : iris, pointes d'écume des vagues,
#     2e bras des volutes (strength <= 1.5). FX : quelques gouttes qui flottent.
# ----------------------------------------------------------
def drop_mesh(r):
    """Goutte low-poly : bipyramide à 5 côtés."""
    v = [(0, 0, r * 1.5), (0, 0, -r)] + [(r * 0.8 * math.cos(k * 2 * math.pi / 5), r * 0.8 * math.sin(k * 2 * math.pi / 5), 0) for k in range(5)]
    f = []
    for k in range(5):
        n = (k + 1) % 5
        f.append((0, 2 + k, 2 + n))
        f.append((1, 2 + n, 2 + k))
    return mesh_from("drop", v, f)

if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 2.0
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (R * 1.6 + PEC_SPAN * 0.5),
                    random.uniform(-TL * 1.0, TL * 0.5 + TAIL_L * 0.6),
                    random.uniform(LEG_H * 1.2, top_z)))
        place(f"FX_Drop_{k}", drop_mesh(FX_SIZE * random.uniform(0.6, 1.3)), M_FOAM if k % 3 == 0 else M_BUBBLE, p,
              (random.uniform(0, 45), random.uniform(0, 45), random.uniform(0, 45)), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
