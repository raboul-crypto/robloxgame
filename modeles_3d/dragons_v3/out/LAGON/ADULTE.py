import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Lagon · Adulte
#  Rare · Eau · Amphiptère · monde 3
#  - Adulte : grand serpent turquoise dressé en S, anneaux au sol, immenses ailes translucides parcourues de reflets d'eau
#  - Signes distinctifs : couronne d'épines-nageoires (crête en éventail double), nageoires-oreilles, losanges sur les flancs
#  - Ventre ivoire en plaques, 3 crocs par côté, nageoire dorsale, nageoire caudale en V au bout de la queue
#  - Rare : motif secondaire (losanges clairs, reflets d'eau), cornes à 2 pointes, crête double, accent lumineux discret
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(3303)            # même dragon à chaque exécution
TAG = "LAGON_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 8000          # budget de triangles de ce stade et de cette rareté
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
#    Turquoise (corps), turquoise sombre (segments, losanges), ivoire (ventre), bleu glacier (crêtes-nageoires,
#    translucides), cyan pâle (pointes). Rare : accent lumineux discret (yeux, reflets d'eau ; strength <= 1.5).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",     "#1FB2C4", 0.45)   # corps principal, turquoise
M_BODY2 = get_mat("BodyDark", "#1792A8", 0.50)   # segments alternés, narines, plaques du dos
M_BODYL = get_mat("BodyLight", "#4FD0DB", 0.40)  # arête du museau, centre des losanges
M_DARK  = get_mat("Mouth",    "#0B4752", 0.65)   # bouche, jointures
M_BELLY = get_mat("Belly",    "#F2EBD8", 0.50)   # ventre en plaques, mâchoire, plastron
M_MARK  = get_mat("Diamond",  "#128A9A", 0.40)   # losanges des flancs (écailles)
M_FIN   = get_mat("Fin",      "#8FE0E8", 0.35, alpha=0.78)   # crête-nageoire, nageoires-oreilles (translucide)
M_FINB  = get_mat("FinBone",  "#1FB2C4", 0.45)   # rayons des nageoires
M_TIP   = get_mat("Tip",      "#CFF5F7", 0.35)   # pointes, cornes, griffes de nageoire
M_MEMB  = get_mat("Membrane", "#6FDCE6", 0.30, alpha=0.62)   # membrane des ailes (translucide)
M_VEIN  = get_mat("Caustic",  "#E4FFFF", 0.30, emission="#9FF4FF", strength=0.9)   # reflets d'eau sur les ailes (discret)
M_WHITE = get_mat("EyeWhite", "#F4F8F8", 0.30)
M_IRIS  = get_mat("Iris",     "#16C7DD", 0.25, emission="#16C7DD", strength=1.3)   # iris turquoise lumineux
M_BLACK = get_mat("Black",    "#06141A", 0.30)
M_DROP  = get_mat("Drop",     "#BFF7FF", 0.25, emission="#7FE9F7", strength=0.9, alpha=0.85)   # gouttes d'eau

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADULTE"
ZB = 3.2
NECK_H = 6.6
NECK_LEAN = 1.1         # inclinaison du cou vers l'avant
COIL_R = 2.4            # rayon des anneaux au sol
TAIL_UP = 1.0
RK = 1.0                # épaisseur du corps
BODY_STEP = 0.95
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
FAN_N = 7               # rayons de la crête-nageoire
FAN_L = 3.0
FAN2_N = 5              # petit éventail devant (crête double)
EAR_N = 3
EAR_L = 1.5
CHEEK_N = 3
COLLAR_N = 9            # épines de la collerette
WHISK = 2
HORN_K = 1.0
HORN_TINES = 1
DORSAL = 1.0            # taille de la nageoire dorsale
SHOULDER_FIN = 3
GROUND_FINS = 6
WING_SPAN = 9.5         # longueur d'une aile (os)
WING_LIFT = 0.85
WING_SWEEP = 0.45
WING_FINGERS = 5
WING_VEINS = 3          # lignes de reflets d'eau par membrane
WING_BONE = 0.2
TAIL_FIN = 3.0
FX_N = 14
FX_SIZE = 0.9

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
HS = HEAD_SCALE

def build_ctrl():
    """Corps en S (cou de cygne qui se penche vers l'avant), puis spirale posée au sol qui part à gauche."""
    pts = []
    for f, y in ((1.0, -1.10), (0.86, -0.35), (0.62, 0.55), (0.38, 0.75), (0.15, 0.25), (0.0, -0.45)):
        pts.append(Vector((0, y * NECK_LEAN, ZB + NECK_H * f)))
    pts.append(Vector((0, -0.55, ZB * 0.55 + 0.9)))
    pts.append(Vector((0, -0.20, 1.6)))
    pts.append(Vector((-0.05, 0.75, 0.3)))
    cy = 0.8 + COIL_R * 1.55
    for k in range(1, 7):
        th = math.radians(55 * k)
        R = COIL_R * (1.0 - 0.45 * (k / 6.0))
        pts.append(Vector((-R * math.sin(th) * 1.12, cy - R * math.cos(th), 0.3)))
    pts.append(Vector((0.30 * COIL_R, cy - 0.20 * COIL_R, 0.7)))
    pts.append(Vector((0.05 * COIL_R, cy + 0.10 * COIL_R, 1.2 * TAIL_UP)))
    pts.append(Vector((-0.15 * COIL_R, cy + 0.30 * COIL_R, 2.0 * TAIL_UP)))
    return pts
CTRL = build_ctrl()

RADIUS_KEYS = [(0.0, 0.58), (0.04, 0.70), (0.18, 0.82), (0.30, 1.04), (0.42, 1.08), (0.60, 0.94),
               (0.78, 0.58), (0.90, 0.36), (1.0, 0.18)]
RADIUS_KEYS = [(s, v * RK) for s, v in RADIUS_KEYS]
S_TAIL = 0.66
S_WING = 0.17

SPINE = resample(sample_curve(CTRL), BODY_STEP)
N = len(SPINE) - 1
for i in range(len(SPINE)):
    s_ = i / N
    SPINE[i].z = max(SPINE[i].z, keyed(RADIUS_KEYS, s_) * 0.96)

FR = []
_d = Vector((0, 1, 0))
for i in range(N):
    t = (SPINE[i + 1] - SPINE[i]).normalized()
    _d = (_d - t * _d.dot(t)).normalized()
    FR.append((t, _d.copy(), t.cross(_d).normalized()))

def radius(s):
    return keyed(RADIUS_KEYS, s)

def frame_at(s):
    i = min(N - 1, max(0, int(s * N)))
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = FR[i]
    return mid, t, d, side, radius(s)

HEAD_POS = SPINE[0] + Vector((0, -0.25 * HS, 0.60 * HS))
HEAD_PITCH = 10

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)           # pas de pattes (amphiptère) : sert aux gouttes et nageoires posées au sol
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def fan(name, origin, dirs, lengths, parent, normal, spine_th=0.1, mat_memb=None, mat_bone=None, tip_mat=None, memb_t=0.05):
    """Éventail de nageoire : rayons (barres) qui partent de 'origin' + membrane translucide entre deux rayons."""
    origin = Vector(origin)
    tips = []
    for k, (dv, L) in enumerate(zip(dirs, lengths)):
        tip = origin + Vector(dv).normalized() * L
        tips.append(tip)
        bar(f"{name}_Ray_{k}", origin, tip, spine_th, mat_bone or M_FINB, parent, up=tuple(normal))
        if tip_mat:
            shard(f"{name}_RayTip_{k}", spine_th * 1.6, spine_th * 1.2, L * 0.18, tip,
                  Vector(dv), tip_mat, parent, up=tuple(normal))
    for k in range(len(tips) - 1):
        mid = (tips[k] + tips[k + 1]) / 2
        # le bord de la membrane est un peu en retrait entre deux rayons (bord festonné)
        mid = origin.lerp(mid, 0.9)
        plate(f"{name}_Memb_{k}", [origin, tips[k], mid, tips[k + 1]], memb_t, mat_memb or M_FIN, parent)
    return tips

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne turquoise, museau, mâchoire ivoire, yeux turquoise lumineux, crête-nageoire en éventail,
#    nageoires-oreilles, petites cornes pâles, barbillons.
# ----------------------------------------------------------
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1)):
    return bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up)

def hfan(name, origin, dirs, lengths, normal, th=0.1, mat_memb=None, tip=True, mt=0.05):
    return fan("Head_" + name, hv(origin), dirs, [L * HS for L in lengths], H, normal, th * HS,
               mat_memb or M_FIN, M_FINB, M_TIP if tip else None, mt * HS)

# Crâne, museau, arête claire, plaque du front, mâchoire ivoire, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.5, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.04, bevel=0.08)
hbox("SnoutBridge", (0.95, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODYL)
hbox("ForeheadPlate", (1.25, 0.8 * SNOUT_K + 0.3, 0.1), (0, -0.2, 0.86), mat=M_BODY2)
hbox("Jaw", (1.3, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY)
hbox("MouthLine", (1.53, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.22, 0.06), (sgn * 0.38, SNOUT_FRONT + 0.25, 0.2), mat=M_DARK)
    # petit losange sur le museau (motif)
    hbox(f"SnoutMark_{sgn}", (0.2, 0.34, 0.07), (sgn * 0.62, SNOUT_FRONT + 0.7, 0.2), mat=M_MARK)

# Yeux : blanc, iris turquoise lumineux, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.92, 1.0, 0.72, 0.84, 0.42, 0.6
else:
    EW, EH, IW, IH, PW, PH = 0.72, 0.74, 0.54, 0.62, 0.11, 0.54
for sgn in (-1, 1):
    ey, ez = -0.28, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.93, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 0.98, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.02, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.05, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.05, ey + 0.13, ez - 0.22), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.2), (sgn * 0.95, ey - 0.05, ez + 0.55), rot=(14, 0, 0),
             mat=M_BODY2, bevel=0.02)
        hbox(f"BrowLight_{sgn}", (0.1, 0.8, 0.08), (sgn * 1.0, ey - 0.05, ez + 0.68), rot=(14, 0, 0), mat=M_TIP)

# Crocs (ado : 2 petits par côté ; adulte : 3 par côté)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.28 + 0.1 * FANGS / 3, (sgn * 0.68, fy, -0.74), (0, 0.05, -1),
                   M_TIP, up=(1, 0, 0))

# SIGNE DISTINCTIF : crête-nageoire en éventail sur la tête (plan YZ, derrière le crâne)
#   rayons turquoise + membrane translucide + pointes pâles. Rare : crête DOUBLE (grand éventail + petit éventail devant).
def _fan_dirs(n, a0, a1):
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * k / max(1, n - 1))
        out.append((0, math.cos(a), math.sin(a)))     # a = 0 : vers l'arrière, a = 90 : vers le haut
    return out
hfan("Crest", (0, 0.45, 0.75), _fan_dirs(FAN_N, 15, 120), [FAN_L * (0.75 + 0.25 * math.sin(math.pi * k / max(1, FAN_N - 1)))
     for k in range(FAN_N)], (1, 0, 0), th=0.1, mt=0.07)
if FAN2_N:
    hfan("Crest2", (0, -0.1, 0.85), _fan_dirs(FAN2_N, 50, 125), [FAN_L * 0.5 for _ in range(FAN2_N)], (1, 0, 0),
         th=0.08, mat_memb=M_TIP, mt=0.05)

# Nageoires-oreilles (de chaque côté du crâne) et nageoires de joue
for sgn in (-1, 1):
    dirs = [(sgn * 0.9, 0.55, 0.25), (sgn * 0.8, 0.8, 0.0), (sgn * 0.6, 0.95, -0.25)][:EAR_N]
    hfan(f"Ear_{sgn}", (sgn * 0.85, 0.35, 0.12), dirs, [EAR_L, EAR_L * 1.1, EAR_L * 0.85][:EAR_N],
         (0, 0, 1), th=0.08, mt=0.05)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.34, 0.1, 0.8 - 0.12 * k, (sgn * 0.88, -0.2 + k * 0.28, -0.55 - 0.08 * k),
               (sgn * 0.7, 0.8, -0.4), M_FIN, up=(sgn, 0, 0))
    # barbillons : deux petites moustaches fines qui tombent du museau
    hbar(f"Whisker_{sgn}", (sgn * 0.5, SNOUT_FRONT + 0.4, -0.35), (sgn * 0.95, SNOUT_FRONT + 0.95, -0.95 - 0.2 * WHISK), 0.1, M_TIP)
    if WHISK:
        hbar(f"Whisker2_{sgn}", (sgn * 0.95, SNOUT_FRONT + 0.95, -0.95 - 0.2 * WHISK),
             (sgn * 1.15, SNOUT_FRONT + 1.7, -1.1 - 0.35 * WHISK), 0.07, M_TIP)

# Collerette d'épines-nageoires : arc de pointes translucides derrière le crâne (couronne autour de la nuque)
for k in range(COLLAR_N):
    ang = math.radians(-125 + k * (250 / max(1, COLLAR_N - 1)))
    rad = Vector((math.sin(ang), 0, math.cos(ang)))
    loc = (rad.x * 0.85, 0.8, rad.z * 0.8 - 0.1)
    hshard(f"Collar_{k}", 0.5, 0.1, 1.1 + 0.25 * math.cos(ang), loc, rad * 0.8 + Vector((0, 1.0, 0)),
           M_FIN if k % 2 == 0 else M_TIP, up=tuple(rad))

# Cornes pâles courtes, recourbées vers l'arrière (Rare : 2 pointes)
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.45, 0.45, 0.3), (sgn * 0.5, 0.15, 0.82), mat=M_BODY2)
    a0 = Vector((sgn * 0.5, 0.15, 0.9))
    a1 = Vector((sgn * 0.7, 0.6, 0.9 + 0.7 * HORN_K))
    a2 = Vector((sgn * 0.75, 1.3, 0.9 + 1.0 * HORN_K))
    chain(f"Head_Horn_{sgn}", [hv(a0), hv(a1), hv(a2)], 0.28 * HS, 0.14 * HS, M_TIP, H, bevel=0)
    hshard(f"HornTip_{sgn}", 0.16, 0.16, 0.5 * HORN_K, a2, (0, 1, 0.3), M_TIP)
    if HORN_TINES:
        t2 = a1 + Vector((sgn * 0.45, 0.2, 0.55 * HORN_K))
        hbar(f"HornTine_{sgn}", a1, t2, 0.14, M_TIP)
        hshard(f"HornTineTip_{sgn}", 0.12, 0.12, 0.35 * HORN_K, t2, t2 - a1, M_TIP)

# ----------------------------------------------------------
# 10. CORPS : segments turquoise, ventre en plaques, losanges sur les flancs, nageoire dorsale double
# ----------------------------------------------------------
def diamond(name, c, e1, e2, a, b, th, mat, parent):
    """Losange plat (écaille) centré en c, demi-diagonales a (selon e1) et b (selon e2)."""
    c, e1, e2 = Vector(c), Vector(e1), Vector(e2)
    plate(name, [c - e1 * a, c - e2 * b, c + e1 * a, c + e2 * b], th, mat, parent)

for i in range(N):
    p1, p2 = SPINE[i], SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / N
    r = radius(s)
    t, d, side = FR[i]
    R = seg_matrix(t, d, side)
    parent = body_root if s < S_TAIL else tail_root
    tag = "Body" if s < S_TAIL else "Tail"

    box(f"{tag}_Seg_{i}", (2 * r, Ln * 1.30, 1.9 * r), mid, R, M_BODY if i % 2 == 0 else M_BODY2, parent,
        bevel=(0.08 * r if s < 0.42 else 0.0))
    # Anneau sombre à la jointure
    if 0.02 < s < 0.86:
        B(f"{tag}_Joint_{i}", (2.06 * r, 0.1, 1.96 * r), p1, R, M_DARK, parent)
    # Plaques de ventre ivoire bien séparées
    if s < 0.86:
        B(f"{tag}_Belly_{i}", (1.55 * r, Ln * 0.80, 0.26 * r + 0.06), mid - d * (r * 0.93), R, M_BELLY, parent)
    # Losanges sur les flancs : grand losange turquoise sombre + petit losange clair au centre
    if 0.04 < s < 0.92:
        for sgn in (-1, 1):
            nrm = side * sgn
            c = mid + nrm * (r * 1.0 + 0.03) + d * (0.05 * r)
            diamond(f"{tag}_Diamond_{i}_{sgn}", c, t, d, Ln * 0.62, r * 0.62, 0.07, M_MARK, parent)
            if i % 2 == 0:
                diamond(f"{tag}_DiamondL_{i}_{sgn}", c + nrm * 0.03, t, d, Ln * 0.3, r * 0.3, 0.07, M_BODYL, parent)
    # Crête double : nageoire dorsale translucide (1 segment sur 2) + petites plaques sombres entre (l'autre)
    if DORSAL and 0.06 < s < 0.80:
        if i % 2 == 0:
            hgt = (0.9 + 0.7 * r) * DORSAL
            base = mid + d * (r * 0.9)
            tip = base + d * hgt - t * 0.15
            plate(f"{tag}_DorsalFin_{i}", [base - t * Ln * 0.65, tip, base + t * Ln * 0.65], 0.06, M_FIN, parent)
            bar(f"{tag}_DorsalRay_{i}", base, tip, 0.1, M_FINB, parent, up=tuple(side))
        else:
            B(f"{tag}_Plate_{i}", (1.0 * r, Ln * 0.85, 0.2 * r + 0.05), mid + d * (r * 0.92),
              R @ Euler((math.radians(-6), 0, 0)).to_matrix(), M_BODY2, parent)

# Plastron ivoire sur la poitrine
cmid, ct, cd, cside, cr = frame_at(S_WING + 0.05)
CR = seg_matrix(ct, cd, cside)
B("Body_Plastron", (1.7 * cr, 1.5, 0.3), cmid - cd * (cr + 0.04), CR, M_BELLY, body_root)
# Nageoires d'épaule : petit éventail translucide à la base de chaque aile
for sgn in (-1, 1):
    if SHOULDER_FIN:
        o = cmid + cside * sgn * cr * 0.85 + cd * cr * 0.3
        dirs = [cside * sgn * 0.9 + ct * 0.2 + cd * 0.5, cside * sgn * 0.7 + ct * 0.6 + cd * 0.3, cside * sgn * 0.4 + ct * 0.9]
        fan(f"Body_ShoulderFin_{sgn}", o, dirs, [1.4 * RK + 0.3, 1.6 * RK + 0.4, 1.2 * RK + 0.3][:SHOULDER_FIN],
            body_root, tuple(cd), 0.1, M_FIN, M_FINB, M_TIP, 0.05)

# ----------------------------------------------------------
# 11. PATTES : aucune (amphiptère, corps de serpent). LEGS_ROOT ne porte que les nageoires posées au sol.
#     Petites nageoires-vagues posées autour des anneaux (rappel de l'eau).
# ----------------------------------------------------------
for k in range(GROUND_FINS):
    a = k * 2 * math.pi / GROUND_FINS + 0.3
    cy = 0.8 + COIL_R * 1.55
    base = Vector((-math.sin(a) * COIL_R * 1.12, cy - math.cos(a) * COIL_R, 0.1))
    outv = Vector((-math.sin(a), -math.cos(a), 0))
    base += outv * RK * 1.0
    shard(f"Legs_Wave_{k}", 0.7 * RK + 0.2, 0.12, 0.9 * RK + 0.5, base, outv + Vector((0, 0, 0.8)), M_FIN, legs_root)

# ----------------------------------------------------------
# 12. AILES : ailes membraneuses turquoise translucides (fonction wing()) + reflets d'eau
#     (veines claires qui ondulent comme la lumière au fond d'une piscine)
# ----------------------------------------------------------
def water_wing(sgn, root):
    span = WING_SPAN
    wrist = wing(f"Wings_{sgn}", root, sgn, span, M_FINB, M_MEMB, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.3, memb_t=0.05, claw_mat=M_TIP, bevel=0.0)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tips.append(wrist + Vector((sgn * span * (0.38 - 0.18 * f), span * (0.15 + 0.55 * f), -span * (0.05 + 0.3 * f))))
    # reflets d'eau : lignes brisées claires entre deux doigts (zig-zag), posées sur la membrane
    n = (wrist - root).cross(tips[-1] - wrist).normalized()
    for k in range(len(tips) - 1):
        for row in range(WING_VEINS):
            f0 = 0.35 + 0.5 * row / max(1, WING_VEINS)
            pts = []
            for j in range(4):
                u = j / 3.0
                a = wrist.lerp(tips[k], f0 + 0.12 * (1 if j % 2 else -1))
                b = wrist.lerp(tips[k + 1], f0 - 0.12 * (1 if j % 2 else -1))
                pts.append(a.lerp(b, u) + n * 0.05)
            for j in range(3):
                link(f"Wings_{sgn}_Vein_{k}_{row}_{j}", pts[j], pts[j + 1], 0.07, M_VEIN, wings_root, up=tuple(n),
                     extra=0.04, bevel=0, depth=0.04)
    # bords des doigts : petite pointe pâle
    for k, tp in enumerate(tips):
        shard(f"Wings_{sgn}_Tip_{k}", 0.3, 0.1, span * 0.1, tp, tp - wrist, M_TIP, wings_root, up=tuple(n))

wmid, wt, wd, wside, wr = frame_at(S_WING)
for sgn in (-1, 1):
    water_wing(sgn, wmid + wd * wr * 0.8 + wside * sgn * wr * 0.55)

# ----------------------------------------------------------
# 13. QUEUE : même courbe (s > S_TAIL) ; bout = nageoire caudale en V (poisson) avec rayons
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = FR[-1]
B("Tail_TipRing", (0.55 * RK, 0.3, 0.55 * RK), tip, seg_matrix(tt_, td_, ts_), M_TIP, tail_root)
lobes = []
for sgn in (-1, 1):
    # deux lobes (haut / bas) de la caudale, dans le plan (tangente, dos)
    dirs = [tt_ * 0.5 + td_ * sgn * 1.0, tt_ * 0.8 + td_ * sgn * 0.6, tt_ * 1.0 + td_ * sgn * 0.25, tt_ * 1.0]
    Ls = [TAIL_FIN * 1.0, TAIL_FIN * 0.92, TAIL_FIN * 0.75, TAIL_FIN * 0.55]
    fan(f"Tail_Caudal_{sgn}", tip, dirs, Ls, tail_root, tuple(ts_), 0.1, M_FIN, M_FINB, M_TIP, 0.07)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (losanges + reflets d'eau sur les ailes), cornes à 2 pointes, crête double (éventail double
#     + nageoire dorsale + plaques), accent lumineux discret (iris, reflets, gouttes ; strength <= 1.3).
#     FX : gouttes d'eau qui flottent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 3.0
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.6 + 2.0), random.uniform(-2.5, 3.0 + COIL_R * 2.5),
                    random.uniform(1.0, top_z)))
        crystal(f"FX_Drop_{k}", FX_SIZE * 0.32, FX_SIZE * 0.55, FX_SIZE * 0.55, p,
                (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), 1.0), M_DROP, master, sides=4)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
