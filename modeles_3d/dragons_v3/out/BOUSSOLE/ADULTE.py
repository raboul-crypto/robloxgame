import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Boussole · Adulte
#  Rare · Eau · Classique · monde 4
#  - Adulte musclé et droit : cou de 5 plaques à bagues de laiton, épaules et cuisses en blocs, 3 crocs par côté
#  - Rose des vents dorée sur le front et GRANDE rose lumineuse sur la poitrine, hautes cornes-aiguilles à 2 pointes (gauche : pointe rouge)
#  - Plaques dorées sur les épaules, crête dorsale double, lignes de carte marine + route + repères lumineux sur les flancs
#  - Grandes ailes-voiles bordées de laiton avec étoile de rose des vents, queue à grande flèche de boussole dorée, gouttes et étoiles flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4102)            # même dragon à chaque exécution
TAG = "BOUSSOLE_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
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
#    Bleu marine (corps), parchemin (ventre), laiton doré métallique (rose des vents, cornes, ailes), rouge (pointe d'aiguille).
#    Rare : accent lumineux discret (iris, rose des vents, repères de carte : strength <= 1.5).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#214C98", 0.45)   # corps principal bleu marine saturé
M_BODY2 = get_mat("ScaleA",    "#17376F", 0.50)   # écailles sombres, dessus des pattes
M_SCALEB= get_mat("ScaleB",    "#4F6C8C", 0.45)   # écailles gris-bleu
M_DARK  = get_mat("BodyDark",  "#0F2650", 0.55)   # sourcils, bouche, genoux
M_CREAM = get_mat("Belly",     "#F0E2BC", 0.55)   # ventre en plaques, plastron, menton (parchemin)
M_GOLD  = get_mat("Brass",     "#D9AA3E", 0.28, metallic=0.85)   # laiton : cornes, bracelets, os d'aile, rose
M_GOLD2 = get_mat("BrassDark", "#A87F28", 0.35, metallic=0.80)   # laiton sombre : bagues, pointes
M_RED   = get_mat("NeedleRed", "#D8362B", 0.35)   # pointe rouge d'une corne
M_MEMB  = get_mat("Membrane",  "#5C98DA", 0.50)   # membrane des ailes (voile)
M_LINE  = get_mat("MapLine",   "#E2B84A", 0.35, metallic=0.5)    # fines lignes de carte marine
M_MARK  = get_mat("MapMark",   "#FFD060", 0.30, emission="#FFB830", strength=1.0)  # rose des vents et repères (lueur douce)
M_CLAW  = get_mat("Claw",      "#F0E2BC", 0.35)   # griffes, crocs
M_WHITE = get_mat("EyeWhite",  "#F4F4EA", 0.30)
M_IRIS  = get_mat("Iris",      "#F5B52E", 0.25, emission="#FFB82A", strength=1.2)   # iris doré lumineux
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)
M_DROP  = get_mat("Droplet",   "#6FE0F0", 0.15, emission="#4FD8F0", strength=1.3)   # gouttes d'eau flottantes
SCALES = [M_BODY2, M_SCALEB, M_BODY]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
BW = 2.5
BH = 2.3
LEG_H = 2.1
TORSO_L = 4.3
NECK_L = 3.6
NECK_LEAN = 0.55
NECK_N = 6
NECK_R = (0.85, 1.15)
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
CHEEK_N = 3
HORN_L = 3.0
HORN_SPUR = True
HEAD_FINS = 3
ROSE_CHEST = 2.0
BELLY_N = 6
BELLY_SIDES = True
FLANK_ROWS = 2
FLANK_COLS = 6
MAP_LINES = 2
MAP_ROUTE = True
MAP_MARKS = 3
NECK_BANDS = True
CREST_N = 6
CREST2 = True
SHOULDER_PLATES = 1.0
SHOULDER_SPIKES = 2
BRACER_K = 0.62
LEG_BEV = 1
LEG_MARK = True
THIGH_SPIKES = 2
TAIL_BEV_N = 4
TAIL_LINES = True
WING_SPAN = 6.6
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_DROOP = 0.55
WING_BONE = 0.32
WING_FINGERS = 3
WING_ROSE = True
TAIL_L = 6.5
TAIL_STEP = 0.8
ARROW = 2.2
FX_N = 12
FX_SIZE = 0.7


# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 1.9                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_BASE = Vector((0, -TL * 0.36, ZC + BH * 0.2))
NECK_TOP = NECK_BASE + Vector((0, -NECK_LEAN, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.1 * HEAD_SCALE, 0.45 * HEAD_SCALE))
HEAD_PITCH = 7                                   # degrés : la tête regarde un peu vers le bas
TAIL_START = Vector((0, TL * 0.42, ZC - 0.12 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def rose(name, c, normal, size, parent, spin=0.0, th=0.1, mat_main=None, mat_diag=None, mat_ring=None, with_ring=True, diag=True):
    """ROSE DES VENTS : étoile à 8 branches (4 longues cardinales + 4 courtes en diagonale) posée à plat
    dans le plan perpendiculaire à 'normal', avec un anneau de laiton autour du centre."""
    c = Vector(c)
    n = Vector(normal).normalized()
    u = n.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = n.cross(Vector((0, 1, 0)))
    u.normalize()
    v = n.cross(u).normalized()
    for k in range(8):
        a = math.radians(k * 45 + spin)
        dv = u * math.cos(a) + v * math.sin(a)
        long_ = (k % 2 == 0)
        if not long_ and not diag:
            continue
        shard(f"{name}_P{k}", size * (0.3 if long_ else 0.2), th, size * (1.0 if long_ else 0.58), c, dv,
              (mat_main or M_MARK) if long_ else (mat_diag or M_GOLD), parent, up=tuple(n))
    if with_ring:
        ring(f"{name}_Ring", size * 0.34, size * 0.1, th * 1.1, c + n * th * 0.2, tuple(n), mat_ring or M_GOLD, parent, sides=8)

def needle(name, base, direction, length, width, mat, tip_mat, parent, up=(0, 0, 1), th=None):
    """AIGUILLE DE BOUSSOLE : losange allongé + petite pointe de couleur (rouge ou laiton)."""
    d = Vector(direction).normalized()
    th = width * 0.75 if th is None else th
    shard(f"{name}_Body", width, th, length, base, d, mat, parent, up=up)
    shard(f"{name}_Tip", width * 0.62, th * 0.62, length * 0.42, Vector(base) + d * length * 0.72, d, tip_mat, parent, up=up)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
# ----------------------------------------------------------
HS = HEAD_SCALE
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_SCALEB)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
# Fines lignes de carte dorées sur le museau
hbox("SnoutLine", (0.7, 0.07, 0.04), (0, -0.6 - 0.5 * SNOUT_K, 0.26), mat=M_LINE)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris doré lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.88, 0.95, 0.68, 0.8, 0.4, 0.56
else:
    EW, EH, IW, IH, PW, PH = 0.55, 0.62, 0.4, 0.52, 0.1, 0.48
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.22), (sgn * 1.07, ey - 0.15, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, ey + 0.12, ez - 0.2), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.14, 0.95, 0.22), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0),
             mat=M_DARK, bevel=0.02)
        hbox(f"BrowLine_{sgn}", (0.16, 0.95, 0.05), (sgn * 0.98, ey - 0.05, ez + 0.66), rot=(14, 0, 0), mat=M_LINE)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Ailerons de joue en laiton et oreilles-nageoires bleues
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.6, 0.1, 1.15, (sgn * 0.85, 0.55, 0.2), (sgn * 1, 0.7, 0.2), M_MEMB)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.4, 0.08, 0.85 - 0.12 * k, (sgn * 0.88, -0.3 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.4), M_GOLD if k % 2 == 0 else M_SCALEB)

# SIGNE DISTINCTIF 1 : la ROSE DES VENTS dorée sur le front
rose("Head_Rose", hv((0, -0.15, 0.89)), (0, -0.28, 1.0), 0.62 * HS, H, spin=0, th=0.09 * HS)

# SIGNE DISTINCTIF 2 : deux cornes en AIGUILLES DE BOUSSOLE (gauche = pointe rouge, droite = pointe laiton)
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.5, 0.5, 0.4), (sgn * 0.62, 0.3, 0.85), mat=M_GOLD2, bevel=0.04)
    needle(f"Head_Needle_{sgn}", hv((sgn * 0.62, 0.3, 0.95)), (sgn * 0.22, 0.42, 1.0), HORN_L * HS, 0.46 * HS,
           M_GOLD, M_RED if sgn == -1 else M_GOLD2, H, up=(1, 0, 0))
    if HORN_SPUR:
        # 2e pointe : petite aiguille secondaire qui part vers l'avant et l'extérieur
        needle(f"Head_Spur_{sgn}", hv((sgn * 0.72, 0.2, 1.05)), (sgn * 0.8, -0.35, 0.9), HORN_L * 0.42 * HS, 0.3 * HS,
               M_GOLD, M_GOLD2, H, up=(1, 0, 0))

# Petite crête de nageoires dorées derrière le crâne
for k in range(HEAD_FINS):
    for sgn in (-1, 1):
        hshard(f"Fin_{sgn}_{k}", 0.45, 0.08, 1.0 - 0.1 * k, (sgn * (0.35 + 0.15 * k), 0.75 + 0.1 * k, 0.4 - 0.2 * k),
               (sgn * (0.5 + 0.3 * k), 1.0, 0.25 - 0.25 * k), M_SCALEB if k % 2 else M_GOLD, up=(0, 0, 1))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre, flancs, lignes de carte, crête double, épaulières
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les écailles et lignes sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron parchemin + ROSE DES VENTS sur la poitrine
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
rose("Body_Rose", (0, -TL * 0.5 - 0.17 * SC, ZC - BH * 0.08), (0, -1, 0), ROSE_CHEST, body_root, spin=0, th=0.12 * SC)
# Plaques de ventre séparées
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Écailles bleues en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick(SCALES, [3, 3, 1]), body_root, up=(sgn, 0, 0))

# LIGNES DE CARTE MARINE dorées : parallèles en tirets + une route en diagonale + croix de repère lumineuses
for sgn in (-1, 1):
    for j in range(MAP_LINES):
        z = ZC + BH * (0.34 - 0.2 * j)
        for q in range(3):
            y = -TL * 0.3 + q * TL * 0.27
            B(f"Body_MapLine_{sgn}_{j}_{q}", (0.09 * SC, TL * 0.19, 0.09 * SC), (sgn * (half_w(y) + 0.015 * SC), y, z),
              mat=M_LINE, parent=body_root)
    if MAP_ROUTE:
        pts = [(-TL * 0.3, ZC + BH * 0.1), (-TL * 0.05, ZC - BH * 0.12), (TL * 0.18, ZC + BH * 0.18), (TL * 0.38, ZC - BH * 0.08)]
        for q in range(len(pts) - 1):
            (ya, za), (yb, zb) = pts[q], pts[q + 1]
            link(f"Body_MapRoute_{sgn}_{q}", (sgn * (half_w(ya) + 0.02 * SC), ya, za), (sgn * (half_w(yb) + 0.02 * SC), yb, zb),
                 0.09 * SC, M_LINE, body_root, up=(sgn, 0, 0), extra=0.0, bevel=0)
    for q in range(MAP_MARKS):
        y = -TL * 0.3 + q * TL * 0.3 + 0.1 * TL
        z = ZC + BH * (-0.12 if q % 2 == 0 else 0.18)
        for a in (45, -45):
            B(f"Body_MapMark_{sgn}_{q}_{a}", (0.06 * SC, 0.3 * SC, 0.06 * SC), (sgn * (half_w(y) + 0.03 * SC), y, z),
              rot=(a, 0, 0), mat=M_MARK, parent=body_root)

# Cou : courbe lissée, un segment bleu + une plaque parchemin par maillon (+ bague de laiton)
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):
    p = NECK_BASE.lerp(NECK_TOP, tt)
    p.y -= 0.3 * NECK_LEAN * math.sin(math.pi * tt)
    NECK_CTRL.append(p)
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_L * 1.04) / NECK_N)
NN = len(NECK_SPINE) - 1
for i in range(NN):
    p1, p2 = NECK_SPINE[i], NECK_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / NN
    r = keyed([(0, NECK_R[0]), (1, NECK_R[1])], s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.22, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_CREAM, body_root)
    if NECK_BANDS:
        B(f"Body_NeckBand_{i}", (2 * r * 1.04, Ln * 0.1, 2 * r * 1.0), p1, R, M_GOLD2, body_root)
    for sgn in (-1, 1):
        if i % 2 == 0:
            shard(f"Body_NeckSide_{i}_{sgn}", 0.5 * SC, 0.1 * SC, 0.7 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, pick([M_SCALEB, M_MEMB, M_GOLD], [3, 3, 1]), body_root)

# Crête dorsale : une rangée centrale de laiton + (si CREST2) deux rangées latérales bleu-gris
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    hh = (1.0 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC
    shard(f"Body_Crest_{k}", 0.7 * SC, 0.12 * SC, hh, (0, y, ZC + BH / 2 - 0.05), (0, 0.5, 1), M_GOLD, body_root, up=(1, 0, 0))
    if CREST2:
        for sgn in (-1, 1):
            shard(f"Body_Crest2_{k}_{sgn}", 0.45 * SC, 0.1 * SC, hh * 0.65, (sgn * BW * 0.22, y + 0.1, ZC + BH / 2 - 0.08),
                  (sgn * 0.3, 0.5, 1), M_SCALEB if k % 2 else M_BODY2, body_root, up=(1, 0, 0))

# Épaulières : plaques de laiton (wedge) + éclats, pour l'ado (petites) et l'adulte
for sgn in (-1, 1):
    if SHOULDER_PLATES:
        wedge(f"Body_Pauldron_{sgn}", (BW * 0.42, TL * 0.26, 0.34 * SC * SHOULDER_PLATES),
              (sgn * BW * 0.4, -TL * 0.2, ZC + BH / 2 + 0.02), (0, sgn * 14, 0), M_GOLD, body_root,
              top_x=0.8, top_y=0.8, bevel=0.04 * SC)
        B(f"Body_PauldronRim_{sgn}", (BW * 0.34, TL * 0.2, 0.1 * SC), (sgn * BW * 0.42, -TL * 0.2, ZC + BH / 2 + 0.2 * SC * SHOULDER_PLATES),
          (0, sgn * 14, 0), M_GOLD2, body_root)
    for k in range(SHOULDER_SPIKES):
        shard(f"Body_ShoulderSpike_{sgn}_{k}", 0.4 * SC, 0.1 * SC, (0.95 - 0.12 * k) * SC,
              (sgn * BW * (0.46 + 0.02 * k), -TL * 0.2 + 0.25 * k * SC, ZC + BH * (0.35 - 0.1 * k)),
              (sgn * (0.9 + 0.1 * k), 0.4 + 0.2 * k, 0.5), M_SCALEB if k % 2 else M_GOLD, body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, bracelet de laiton, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    yy = y + (th * 0.15 if hind else 0)
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, yy, FOOT_H + SHIN_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    # Bracelet de laiton + bague sombre
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, yy, FOOT_H + SHIN_H * 0.5),
        mat=M_GOLD, parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.12, th * 1.16, 0.1 * SC), (x, yy, FOOT_H + SHIN_H * 0.5 + bh_ / 2), mat=M_GOLD2, parent=legs_root)
    if LEG_MARK:
        # petite croix lumineuse sur le bracelet (repère de carte)
        for a in (45, -45):
            B(f"{name}_BracerMark_{a}", (0.05 * SC, th * 0.38, 0.06 * SC), (x + sgn * th * 0.56, yy, FOOT_H + SHIN_H * 0.5),
              rot=(a, 0, 0), mat=M_MARK, parent=legs_root)
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + (th * 0.15 if hind else 0), FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + (th * 0.15 if hind else 0) - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    for k in range(THIGH_SPIKES):
        shard(f"{name}_Fin_{k}", 0.4 * SC, 0.07 * SC, (0.8 - 0.12 * k) * SC,
              (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
              (sgn * 0.8, 0.5, -0.6), M_SCALEB, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES-VOILES : os de laiton, membrane bleue, étoile de rose des vents sur la voile
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_GOLD, M_MEMB, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=WING_DROOP, memb_t=WING_BONE * 0.4, claw_mat=M_CLAW)
    # pointes de laiton au bout de chaque doigt (mêmes formules que wing())
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tip = wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                              -WING_SPAN * (0.05 + WING_DROOP * f)))
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.6, WING_BONE * 1.2, WING_SPAN * 0.12, tip, tip - wrist, M_GOLD2, wings_root)
    if WING_ROSE:
        c = wrist + Vector((sgn * WING_SPAN * 0.2, WING_SPAN * 0.3, -WING_SPAN * (0.05 + WING_DROOP * 0.45)))
        rose(f"Wings_{sgn}_Rose", c + Vector((0, 0, WING_BONE * 0.3)), (0, 0.35, 1), WING_SPAN * 0.12, wings_root,
             spin=15, th=WING_BONE * 0.5, with_ring=False, diag=False)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments bleus, plaques parchemin, crête, FLÈCHE DE BOUSSOLE dorée au bout
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.35, 0.0), (0.45, -0.7, 0.3), (0.7, -0.62, 0.15), (0.9, -0.15, -0.25), (1.0, 0.45, -0.4)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.42), (0.3, BW * 0.36), (0.6, BW * 0.26), (0.85, BW * 0.17), (1.0, BW * 0.11)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_R, s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.3, 2 * r * 0.95), mid, R, M_BODY, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    if i % 2 == 0:
        shard(f"Tail_Crest_{i}", 0.8 * r + 0.2, 0.1 * SC, 0.5 * SC + r * 0.8, mid + d * r * 0.85, d + t * 0.7,
              M_GOLD if i % 4 == 0 else M_SCALEB, tail_root, up=(1, 0, 0))
    if TAIL_LINES and i % 3 == 2 and s < 0.8:
        B(f"Tail_Band_{i}", (2 * r * 1.05, Ln * 0.14, 2 * r * 1.0), p1, R, M_GOLD2, tail_root)
    if TAIL_LINES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            B(f"Tail_Line_{i}_{sgn}", (0.06 * SC, Ln * 0.9, 0.05 * SC), mid + side * sgn * (r + 0.01), R, M_LINE, tail_root)
# Bout de queue : bague de laiton, hampe et GRANDE POINTE DE FLÈCHE dorée avec 2 barbes et un empennage rouge
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_GOLD2, tail_root)
adir = (tt_ + td_ * 0.35).normalized()
bar("Tail_ArrowShaft", tip, tip + adir * ARROW * 0.7, ARROW * 0.18, M_GOLD2, tail_root, up=tuple(ts_))
head_base = tip + adir * ARROW * 0.6
shard("Tail_ArrowHead", ARROW * 0.95, ARROW * 0.16, ARROW * 1.5, head_base, adir, M_GOLD, tail_root, up=tuple(ts_))
for sgn in (-1, 1):
    shard(f"Tail_ArrowBarb_{sgn}", ARROW * 0.3, ARROW * 0.12, ARROW * 0.8, head_base + adir * ARROW * 0.15, adir * 0.4 + td_ * (sgn * 0.9), M_GOLD2, tail_root, up=tuple(ts_))
    shard(f"Tail_ArrowFletch_{sgn}", ARROW * 0.22, ARROW * 0.1, ARROW * 0.6, tip + adir * ARROW * 0.05, (-adir * 0.5 + td_ * sgn * 0.8), M_RED, tail_root, up=tuple(ts_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (lignes de carte marine + route + repères), cornes à 2 pointes, crête double,
#     accent lumineux discret (iris, rose des vents, repères : strength <= 1.5).
#     FX : gouttes d'eau lumineuses et petites étoiles dorées qui flottent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = [random.uniform(-1, 1) for _ in range(3)]
        if k % 2 == 0:
            crystal(f"FX_Drop_{k}", FX_SIZE * 0.16, FX_SIZE * 0.26, FX_SIZE * 0.2, p, dirv, M_DROP, master, sides=4)
        else:
            rose(f"FX_Star_{k}", p, dirv, FX_SIZE * 0.4, master, spin=random.uniform(0, 45), th=FX_SIZE * 0.05, with_ring=False, diag=False)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
