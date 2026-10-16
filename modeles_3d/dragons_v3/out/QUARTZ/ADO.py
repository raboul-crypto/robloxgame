import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Quartz · Ado
#  Légendaire · Minéral · Classique · Équilibré · monde 5
#  - Ado : dragon classique élancé, cou de 5 plaques, crocs, yeux fendus, sourcils d'argent
#  - Cornes en cristal (grand cristal rose + 2 branches), aura de cristaux et anneau d'argent derrière la tête, armure d'argent (front, gorgerin, épaulières, genouillères, hanches)
#  - Grappes de quartz sur les épaules et le dos (double rangée), coeur de quartz sur la poitrine, ailes gris perle avec cristaux sur les os, facettes roses
#  - Queue cerclée d'argent avec une géode de 5 cristaux, 24 cristaux flottants, anneau runique au sol
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(6029)            # même dragon à chaque exécution
TAG = "QUARTZ_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Minéral : gris pierre + ventre gris clair + argent métallique (armure), cristaux de quartz rose et blanc
#    translucides (alpha 0,8, lueur faible), cristaux de coeur et yeux roses ÉMISSIFS. Rareté Légendaire.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",       "#837F8A", 0.55)                                    # corps gris pierre
M_BODY2 = get_mat("BodyScale",  "#615E68", 0.60)                                    # écailles sombres, dessus des pattes
M_SCALEB = get_mat("ScaleB",    "#9C8A93", 0.55)                                    # écailles gris rosé
M_DARK  = get_mat("BodyDark",   "#4B494F", 0.60)                                    # bouche, genoux, ombres
M_CREAM = get_mat("Belly",      "#D9D4DC", 0.45)                                    # ventre en plaques, plastron, menton
M_SILVER = get_mat("Silver",    "#DAD6E2", 0.25, metallic=0.85)                     # armure d'argent
M_SILVER2 = get_mat("SilverDark", "#A9A5B7", 0.30, metallic=0.80)                   # argent sombre (rebords)
M_QP    = get_mat("QuartzPink", "#F2B8C8", 0.12, emission="#F2A6BE", strength=0.6, alpha=0.82)   # quartz rose translucide
M_QW    = get_mat("QuartzWhite", "#F4F2F5", 0.12, emission="#FFFFFF", strength=0.5, alpha=0.82)   # quartz blanc translucide
M_QC    = get_mat("QuartzCore", "#E8789C", 0.15, emission="#FF7FAE", strength=2.6)  # cristaux de coeur lumineux
M_WING  = get_mat("Membrane",   "#D2CDDC", 0.35, metallic=0.15)                     # membrane gris perle
M_BONE  = get_mat("WingBone",   "#A8A2B6", 0.35, metallic=0.3)                      # os des ailes
M_CLAW  = get_mat("Claw",       "#F4F2F5", 0.30)                                    # griffes blanches
M_FANG  = get_mat("Fang",       "#F4F2F5", 0.35)                                    # crocs
M_IRIS  = get_mat("Iris",       "#E8789C", 0.25, emission="#FF7FAE", strength=2.6)  # iris rose lumineux
M_WHITE = get_mat("EyeWhite",   "#F2F2F2", 0.30)
M_BLACK = get_mat("Black",      "#0A0A0A", 0.30)                                    # pupilles, narines
CRYS = [M_QP, M_QW, M_QP, M_QC]
CRYSW = [4, 4, 3, 1]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
BW = 1.9
BH = 1.8
LEG_H = 1.7
TORSO_L = 3.6
NECK_L = 2.6
NECK_LEAN = 0.45
NECK_N = 5
NECK_R = (0.7, 0.9)
HEAD_SCALE = 0.98
SNOUT_K = 1.0
FANGS = 2                # crocs par côté
CHEEK_N = 2              # cristaux de joue
BEARD_N = 3              # petits cristaux sous le menton
CROWN_RINGS = 1          # anneaux de cristaux derrière le crâne
CROWN_N = 10
CROWN_K = 1.0
HALO_R = 1.7             # rayon de l'aura derrière la tête
HALO_RAYS = 8
SILVER = True            # arête du museau en argent
ARMOR = True             # armure de tête
HEART_RAYS = 10          # cristaux autour du coeur de quartz
GORGET = True
BELLY_N = 5
BELLY_RIMS = True
BELLY_SIDES = True
BELLY_BEV = 0.03
FLANK_ROWS = 3
FLANK_COLS = 6
NECK_RIMS = True
NECK_CRYS = 2            # cristaux de nuque par maillon
CREST_N = 5              # grappes sur le dos
CREST_K = 1.0            # taille des grappes
CREST_CLUSTER = 3        # cristaux par grappe
CREST_SIDE = True
BACK_PLATES = True
PAULDRON_EMBLEM = True
PAULDRON_CRYS = 4        # cristaux par épaulière
HIP_ARMOR = True
LEG_BEV = 1
SHIN_SILVER = True
KNEE_GUARD = True
THIGH_ARMOR = True
BRACER_LOW = True
LEG_CRYS = 2
SPUR = False
TOE_BEV = 0.02
TAIL_L = 5.0
TAIL_STEP = 0.7
TAIL_BEV_N = 3
TAIL_BANDS = True
TAIL_SIDE = False
TAIL_SCALES = True
TAIL_CRYS = 5            # cristaux de la géode au bout de la queue
TAIL_CRYS_K = 1.0        # taille de la géode
WING_SPAN = 6.8
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.26
WING_FINGERS = 3
WING_CRYS = 2            # cristaux sur le bord de la membrane
WING_CRYS_L = 0.17
WRIST_CLUSTER = 3        # cristaux de la grappe de poignet
FINGER_CRYS = 1
ARM_CRYS = 2
FACETS = 2               # facettes roses sur la membrane
FX_N = 24
FX_SIZE = 0.6
GROUND_RING = 2.4
GROUND_TICKS = 12

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

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (bois, bases de cornes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def crys(name, base, direction, L, mat, parent, up=(0, 0, 1), r=None, sides=6):
    """Un cristal de quartz : prisme hexagonal à pointe, longueur totale L, posé sur 'base' et dirigé vers 'direction'."""
    rr = L * 0.17 if r is None else r
    return crystal(name, rr, L * 0.68, L * 0.32, base, direction, mat, parent, up=up, sides=sides)

def cluster(name, base, direction, L, parent, n=3, mats=None, up=(0, 0, 1), spread=0.4, phase=0.0):
    """GRAPPE de cristaux de quartz (signe distinctif) : un grand cristal central + (n-1) cristaux inclinés
    autour, en rose, blanc et parfois rose lumineux."""
    d = Vector(direction).normalized()
    m = basis(d, up)
    sx, sz = m.col[0], m.col[2]
    mats = mats or CRYS
    crys(f"{name}_0", base, d, L, mats[0] if mats is CRYS else mats[0], parent, up=up)
    for i in range(1, n):
        a = phase + i * 2 * math.pi / max(1, n - 1)
        side = sx * math.cos(a) + sz * math.sin(a)
        dd = d + side * spread * 1.7
        crys(f"{name}_{i}", Vector(base) + side * L * 0.12, dd, L * (0.62 - 0.12 * (i % 2)), mats[i % len(mats)], parent, up=up, sides=5)

def pk(weights=None):
    """Matériau de quartz au hasard (reproductible)."""
    return pick(CRYS, weights or CRYSW)

def leaf_plate(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Losange plat (facette) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def crys_ring(name, center, direction, r0, length, width, n, mats, parent, a0=0.0, a1=360.0):
    """Cristaux posés en cercle autour de 'center' dans le plan perpendiculaire à 'direction'
    (aura derrière la tête, collerette du plastron)."""
    m = basis(direction, (0, 0, 1))
    ex, ez = m.col[0], m.col[2]
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k / max(1, n - (0 if a1 - a0 >= 360 else 1))))
        rad = ex * math.cos(a) + ez * math.sin(a)
        L = length * (1.0 + 0.35 * (k % 2))
        crystal(f"{name}_{k}", width * 0.3, L * 0.65, L * 0.35, Vector(center) + rad * r0, rad, mats[k % len(mats)], parent,
                up=tuple(Vector(direction)), sides=5)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Signes distinctifs : CORNES en cristal, aura d'éclats de quartz derrière le crâne.
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

def hcrys(name, loc, direction, L, mat, up=(0, 0, 1), sides=6):
    return crys("Head_" + name, hv(loc), direction, L * HS, mat, H, up=up, sides=sides)

def hcluster(name, loc, direction, L, n=3, mats=None, up=(0, 0, 1), spread=0.4):
    cluster("Head_" + name, hv(loc), direction, L * HS, H, n, mats, up, spread)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1)):
    bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up)

# Crâne, museau, arête du museau en argent, mâchoire claire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (0.8, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=(M_SILVER if SILVER else M_BODY2))
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K
# petit cristal rose sur le bout du museau
hcrys("NoseCrystal", (0, SNOUT_FRONT + 0.35, 0.36), (0, -0.4, 1), 0.55 + 0.25 * (not IS_BEBE), M_QP, up=(1, 0, 0), sides=5)

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris rose lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.16), (sgn * 0.97, ey - 0.02, ez + 0.6), rot=(8, 0, 0), mat=M_BODY2)
    else:
        # sourcils sévères en argent
        hbox(f"Brow_{sgn}", (0.14, 0.95, 0.22), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0), mat=M_SILVER)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_FANG, up=(1, 0, 0))

# Oreilles-ailerons gris perle, cristaux de joue, petite grappe sous le menton
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.15, (sgn * 0.8, 0.45, 0.3), (sgn * 1, 0.6, 0.45), M_WING)
    for k in range(CHEEK_N):
        hcrys(f"Cheek_{sgn}_{k}", (sgn * 0.85, -0.3 + k * 0.3, -0.35 - k * 0.12), (sgn * 0.8, 0.7, -0.5), 0.95 - 0.1 * k,
              M_QP if k % 2 == 0 else M_QW, up=(0, 0, 1), sides=5)
for k in range(BEARD_N):
    bx = -0.5 + 1.0 * k / max(1, BEARD_N - 1)
    hcrys(f"Chin_{k}", (bx, SNOUT_FRONT + 0.8 + 0.12 * abs(bx), -0.9), (bx * 0.4, -0.5, -1), 0.8 - 0.2 * abs(bx),
          M_QW if k % 2 else M_QP, up=(1, 0, 0), sides=5)

# COURONNE : anneaux d'éclats de quartz derrière et au-dessus du crâne (rose / blanc / rose lumineux)
for ring_i in range(CROWN_RINGS):
    cnt = CROWN_N - ring_i * 3
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        tang = Vector((math.cos(ang), 0, -math.sin(ang)))
        loc = (rad.x * 0.8, 0.6 + ring_i * 0.3, rad.z * 0.75)
        jit = Vector((random.uniform(-0.1, 0.1), random.uniform(0, 0.2), random.uniform(-0.1, 0.1)))
        direction = rad * (0.9 - ring_i * 0.3) + Vector((0, 0.9, 0)) + jit
        Ln = (1.0 + 1.3 * max(0.0, math.cos(ang))) * (1 - 0.25 * ring_i) * CROWN_K
        hcrys(f"Crown_{ring_i}_{k}", loc, direction, Ln, pk(), up=tuple(tang), sides=5)

# CORNES EN CRISTAL : bébé = 2 petits cristaux ; ado = grand cristal + 2 branches ; adulte = grappes ramifiées
for sgn in (-1, 1):
    if IS_BEBE:
        hcrys(f"Horn_{sgn}", (sgn * 0.55, 0.15, 0.7), (sgn * 0.25, 0.35, 1), 1.25, M_QP, up=(1, 0, 0))
        hcrys(f"HornB_{sgn}", (sgn * 0.8, 0.3, 0.7), (sgn * 0.7, 0.3, 1), 0.7, M_QW, up=(1, 0, 0), sides=5)
    elif IS_ADO:
        hcrys(f"Horn_{sgn}", (sgn * 0.55, 0.15, 0.75), (sgn * 0.3, 0.4, 1), 2.3, M_QP, up=(1, 0, 0))
        hcrys(f"HornB_{sgn}", (sgn * 0.8, 0.3, 0.8), (sgn * 0.9, 0.2, 1), 1.4, M_QW, up=(0, 1, 0), sides=5)
        hcrys(f"HornC_{sgn}", (sgn * 0.7, 0.6, 0.8), (sgn * 0.3, 1.0, 0.8), 1.3, M_QP, up=(1, 0, 0), sides=5)
        hbox(f"HornBase_{sgn}", (0.62, 0.55, 0.3), (sgn * 0.6, 0.2, 0.78), rot=(0, sgn * 10, 0), mat=M_SILVER)
    else:
        hcluster(f"Horn_{sgn}", (sgn * 0.55, 0.15, 0.78), (sgn * 0.3, 0.4, 1), 3.2, 4, [M_QP, M_QW, M_QP], up=(1, 0, 0), spread=0.5)
        hcrys(f"HornB_{sgn}", (sgn * 0.85, 0.3, 0.85), (sgn * 1.0, 0.2, 0.8), 1.9, M_QW, up=(0, 1, 0), sides=5)
        hcrys(f"HornC_{sgn}", (sgn * 0.75, 0.7, 0.85), (sgn * 0.4, 1.0, 0.7), 1.9, M_QP, up=(1, 0, 0), sides=5)
        hcrys(f"HornD_{sgn}", (sgn * 0.9, 0.5, 0.4), (sgn * 1.0, 0.8, 0.2), 1.4, M_QW, up=(0, 0, 1), sides=5)
        hbox(f"HornBase_{sgn}", (0.75, 0.6, 0.3), (sgn * 0.6, 0.2, 0.78), rot=(0, sgn * 10, 0), mat=M_SILVER)

# Armure de tête (ado / adulte) : plaque frontale d'argent + gemme rose, plaques de joue
if ARMOR:
    hwedge("ForeheadPlate", (1.2, 1.0, 0.22), (0, -0.05, 0.88), mat=M_SILVER, top_x=0.7, top_y=0.8, bevel=0.04)
    crystal("Head_ForeGem", 0.16 * HS, 0.12 * HS, 0.14 * HS, hv((0, -0.55, 1.0)), (0, -1, 0.6), M_QC, H)
    for sgn in (-1, 1):
        hwedge(f"CheekPlate_{sgn}", (0.14, 1.0, 0.7), (sgn * 1.0, 0.3, -0.2), mat=M_SILVER, top_x=0.8, bevel=0.0)

# AURA : anneau d'argent + anneau rose lumineux derrière la tête + rayons de quartz
if HALO_R > 0:
    hc = (0, 1.3, 0.35)
    ring("Head_HaloRing", HALO_R * HS, 0.4 * HS, 0.16 * HS, hv(hc), (0, 1, 0), M_SILVER, H, sides=20)
    ring("Head_HaloGlow", HALO_R * HS * 0.8, 0.16 * HS, 0.1 * HS, hv((0, 1.4, 0.35)), (0, 1, 0), M_QC, H, sides=20)
    crys_ring("Head_HaloRay", hv(hc), (0, 1, 0), HALO_R * HS * 1.0, 0.8 * HS, 0.5 * HS, HALO_RAYS, [M_QW, M_QP], H, a0=-150, a1=150)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre clair, COEUR de quartz, armure d'argent, double rangée de cristaux
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les écailles sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron clair + plaques de ventre séparées (filets d'argent)
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root, bevel=BELLY_BEV * SC)
    if BELLY_RIMS:
        B(f"Body_BellyRim_{i}", (BW * 0.86, 0.07 * SC, 0.22 * SC), (0, y + pl * 0.54, ZC - BH / 2 + 0.03), mat=M_SILVER, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root, bevel=BELLY_BEV * 0.6 * SC)

# COEUR DE QUARTZ sur la poitrine : bouclier d'argent, grand cristal rose lumineux, anneau d'argent, couronne de cristaux
HEART = Vector((0, -TL * 0.5 - 0.05, ZC + BH * 0.02))
wedge("Body_HeartShield", (BW * 0.8, 0.24 * SC, BH * 0.78), HEART + Vector((0, 0.1, 0)), mat=M_SILVER, parent=body_root,
      top_x=0.85, top_y=1.0, bevel=0.03 * SC)
crys("Body_HeartGem", HEART + Vector((0, -0.04, 0)), (0, -1, 0.05), BH * 0.62, M_QC, body_root, up=(0, 0, 1), r=BH * 0.17)
ring("Body_HeartRing", BH * 0.33, 0.07 * BH, 0.1 * SC, HEART + Vector((0, -0.08, 0)), (0, -1, 0), M_SILVER2, body_root, sides=12)
crys_ring("Body_HeartCrys", HEART + Vector((0, -0.07, 0)), (0, -1, 0), BH * 0.34, BH * 0.3, BH * 0.16, HEART_RAYS, [M_QP, M_QW], body_root)
if IS_ADULTE:
    ring("Body_HeartRing2", BH * 0.43, 0.05 * BH, 0.08 * SC, HEART + Vector((0, -0.05, 0)), (0, -1, 0), M_SILVER, body_root, sides=12)
    for sgn in (-1, 1):
        crystal(f"Body_HeartGemSide_{sgn}", 0.12 * SC, 0.1 * SC, 0.1 * SC, HEART + Vector((sgn * BW * 0.34, -0.1, -BH * 0.18)),
                (0, -1, 0.1), M_QC, body_root)

# Gorgerin d'argent à la base du cou (ado / adulte)
if GORGET:
    wedge("Body_Gorget", (BW * 0.85, 0.8 * SC, BH * 0.4), (0, -TL * 0.46, ZC + BH * 0.42), mat=M_SILVER, parent=body_root,
          top_x=0.75, top_y=0.8, bevel=0.04 * SC)

# Écailles de pierre en quinconce sur les flancs (grises et gris rosé)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_SCALEB, M_BODY2, M_SILVER2], [3, 2, 2, 1]), body_root, up=(sgn, 0, 0))

# Cou : un segment gris + une plaque claire par maillon, cristaux sur la nuque
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
    if NECK_RIMS:
        B(f"Body_NeckRim_{i}", (2 * r * 0.88, 0.08 * SC, 0.26 * SC), mid - d * (r * 0.95) + t * Ln * 0.5, R, M_SILVER, body_root)
    for k in range(NECK_CRYS):
        off = (k - (NECK_CRYS - 1) / 2) * 0.5
        crys(f"Body_NeckCrys_{i}_{k}", mid + d * r * 0.8 + side * off * r, d + t * 0.9 + side * off * 0.4,
             (1.2 + 0.6 * (1 - s)) * SC * (0.85 if k else 1.1), M_QP if (i + k) % 2 == 0 else M_QW, body_root, up=tuple(side), sides=5)
    if IS_ADULTE or (IS_ADO and i % 2 == 0):
        for sgn in (-1, 1):
            crys(f"Body_NeckSide_{i}_{sgn}", mid + side * sgn * r * 0.85, side * sgn + t * 0.8 + d * 0.3, 0.75 * SC,
                 M_QW, body_root, up=tuple(d), sides=5)

# Dos : DOUBLE rangée de cristaux (grappes au centre, cristaux isolés sur les côtés)
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    cluster(f"Body_Crest_{k}", (0, y, ZC + BH / 2 - 0.05), (0, 0.35, 1), (1.7 - 0.35 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC * CREST_K,
            body_root, n=CREST_CLUSTER, mats=[M_QP, M_QW, M_QP, M_QW], up=(1, 0, 0), spread=0.45, phase=k)
    if CREST_SIDE:
        for sgn in (-1, 1):
            crys(f"Body_CrestSide_{k}_{sgn}", (sgn * BW * 0.28, y + 0.2, ZC + BH / 2 - 0.08), (sgn * 0.45, 0.4, 1), 1.0 * SC,
                 M_QW if k % 2 else M_QP, body_root, up=(1, 0, 0), sides=5)

# Plaques d'armure d'argent sur le dos (ado / adulte)
if BACK_PLATES:
    for sgn in (-1, 1):
        wedge(f"Body_BackPlate_{sgn}", (BW * 0.36, TL * 0.3, 0.24 * SC), (sgn * BW * 0.3, -TL * 0.08, ZC + BH / 2 + 0.01),
              (0, sgn * 8, 0), M_SILVER, body_root, top_x=0.85, top_y=0.85, bevel=0.03)
        B(f"Body_BackPlateB_{sgn}", (BW * 0.3, TL * 0.2, 0.2 * SC), (sgn * BW * 0.3, TL * 0.2, ZC + BH / 2 - 0.02),
          (0, sgn * 6, 0), M_SILVER, body_root)

# ÉPAULIÈRES d'argent : bloc, rebord, grande grappe de cristaux en éventail
for sgn in (-1, 1):
    pw = BW * 0.4
    px = sgn * (BW * 0.5 + 0.03 * SC)
    py, pz = -TL * 0.2, ZC + BH * 0.34
    wedge(f"Body_Pauldron_{sgn}", (pw, TL * 0.3, BH * 0.5), (px, py, pz), (0, -sgn * 12, 0), M_SILVER, body_root,
          top_x=0.8, top_y=0.85, bevel=0.05 * SC)
    if PAULDRON_EMBLEM:
        B(f"Body_PauldronRim_{sgn}", (0.1 * SC, TL * 0.22, BH * 0.38), (px + sgn * pw * 0.47, py, pz - 0.02), (0, -sgn * 12, 0), M_SILVER2, body_root)
        crystal(f"Body_PauldronGem_{sgn}", 0.14 * SC, 0.12 * SC, 0.12 * SC, (px + sgn * (pw * 0.5 + 0.02), py, pz - 0.02),
                (sgn, 0, 0.1), M_QC, body_root)
        wedge(f"Body_PauldronUpper_{sgn}", (pw * 0.8, TL * 0.22, BH * 0.18), (px - sgn * pw * 0.05, py, pz + BH * 0.3),
              (0, -sgn * 12, 0), M_SILVER2, body_root, top_x=0.7, top_y=0.8, bevel=0.03 * SC)
    if HIP_ARMOR:
        wedge(f"Body_HipPlate_{sgn}", (0.16 * SC, TL * 0.28, BH * 0.55), (sgn * (BW * 0.5 + 0.02), TL * 0.3, ZC + BH * 0.05),
              mat=M_SILVER, parent=body_root, top_x=0.8, top_y=0.9, bevel=0.03 * SC)
        wedge(f"Body_RibPlate_{sgn}", (0.14 * SC, TL * 0.3, BH * 0.35), (sgn * (BW * 0.5 + 0.02), -TL * 0.02, ZC - BH * 0.18),
              mat=M_SILVER, parent=body_root, top_x=0.8, top_y=0.9, bevel=0.03 * SC)
    for k in range(PAULDRON_CRYS):
        f = k / max(1, PAULDRON_CRYS - 1)
        crys(f"Body_PauldronCrys_{sgn}_{k}", (px - sgn * pw * 0.1, py + 0.35 * SC * (f - 0.2) + 0.1, pz + BH * 0.2),
             (sgn * (0.5 - 0.3 * f), 0.7 * f + 0.1, 0.9 - 0.2 * f), (1.6 - 0.3 * abs(f - 0.4)) * SC,
             M_QP if k % 2 == 0 else M_QW, body_root, up=(1, 0, 0), sides=5)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, genouillère d'argent, jambière, bracelet, pied de pierre, 3 doigts + 3 griffes blanches
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    yo = th * 0.15 if hind else 0
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=(M_SILVER2 if SHIN_SILVER else M_BODY2), parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    if KNEE_GUARD:
        wedge(f"{name}_Knee", (th * 1.0, th * 0.55, thigh_h * 0.5), (x, y + yo - th * 0.62, FOOT_H + SHIN_H + thigh_h * 0.12),
              mat=M_SILVER, parent=legs_root, top_x=0.7, top_y=0.7, bevel=0.04 * SC)
    if THIGH_ARMOR:
        wedge(f"{name}_ThighPlate", (0.14 * SC, th * 1.2, thigh_h * 0.6), (x + sgn * th * 0.66, y, FOOT_H + SHIN_H + thigh_h * 0.55),
              mat=M_SILVER, parent=legs_root, top_x=0.8, bevel=0.03 * SC)
    # bracelets d'argent (haut et bas de jambière)
    bh_ = SHIN_H * 0.2
    box(f"{name}_Bracer", (th * 1.08, th * 1.12, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.82),
        mat=M_SILVER, parent=legs_root, bevel=LEG_BEV * 0.03 * SC)
    if BRACER_LOW:
        B(f"{name}_BracerLow", (th * 1.06, th * 1.1, bh_ * 0.8), (x, y + yo, FOOT_H + SHIN_H * 0.18), mat=M_SILVER, parent=legs_root)
    # cristaux de quartz sur la jambière extérieure
    for k in range(LEG_CRYS):
        crys(f"{name}_ShinCrys_{k}", (x + sgn * th * 0.47, y + yo + (k - 0.5) * th * 0.3, FOOT_H + SHIN_H * 0.15),
             (sgn * 0.5, 0.1 * (k - 0.5), 1), SHIN_H * (0.75 - 0.2 * k), M_QP if k == 0 else M_QW, legs_root, up=(sgn, 0, 0), sides=5)
    # Pied de pierre + 3 doigts + 3 griffes blanches
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root, bevel=TOE_BEV * SC)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    if SPUR:
        shard(f"{name}_Spur", th * 0.22, th * 0.2, th * 0.5, (x, fy + yo + th * 1.0, FOOT_H * 0.6), (0, 1, 0.3), M_CLAW, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : os gris perle, grande membrane à facettes, cristaux sur les os, grappe au poignet et au bout des doigts
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_BONE, M_WING, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.5, memb_t=WING_BONE * 0.45, claw_mat=M_CLAW)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tips.append(wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                                    -WING_SPAN * (0.05 + 0.5 * f))))
    # grappe de cristaux au poignet
    cluster(f"Wings_{sgn}_WristCrys", wrist, (sgn * 0.4, 0.2, 1), WING_SPAN * 0.2, wings_root, n=WRIST_CLUSTER,
            mats=[M_QP, M_QW], up=(1, 0, 0), spread=0.5)
    for k, tip in enumerate(tips):
        # cristal au bout de chaque doigt + petits cristaux le long de l'os
        crys(f"Wings_{sgn}_TipCrys_{k}", tip, (tip - wrist), WING_SPAN * WING_CRYS_L * (1.0 - 0.1 * k), pk([3, 3, 1, 0]), wings_root, up=(0, 0, 1))
        for j in range(FINGER_CRYS):
            crys(f"Wings_{sgn}_FingerCrys_{k}_{j}", wrist.lerp(tip, 0.3 + 0.55 * j / max(1, FINGER_CRYS)) + Vector((0, 0, WING_BONE * 0.4)),
                 Vector((sgn * 0.2, 0.2, 1)), WING_SPAN * 0.07, M_QP if (j + k) % 2 else M_QW, wings_root, up=(1, 0, 0), sides=5)
        if k + 1 < len(tips):
            for j in range(WING_CRYS):
                crys(f"Wings_{sgn}_EdgeCrys_{k}_{j}", tip.lerp(tips[k + 1], (j + 0.5) / WING_CRYS), (sgn * 0.1, 0.3, -0.9),
                     WING_SPAN * WING_CRYS_L * 0.55, M_QW if j % 2 else M_QP, wings_root, up=(0, 1, 0), sides=5)
            # facettes rose translucide posées sur la membrane (des deux côtés)
            nrm = (tip - wrist).cross(tips[k + 1] - wrist).normalized()
            cen = (wrist + tip + tips[k + 1]) / 3
            for j in range(FACETS):
                sh_ = (tips[k + 1] - tip) * 0.2 * ((j - (FACETS - 1) / 2) * 1.6)
                for side_ in (-1, 1):
                    leaf_plate(f"Wings_{sgn}_Facet_{k}_{j}_{side_}", wrist.lerp(cen, 0.25) + sh_ + nrm * side_ * (WING_BONE * 0.3),
                               cen - wrist + sh_ * 0.3, (cen - wrist).length * (0.85 - 0.15 * j), WING_SPAN * 0.07,
                               M_QP if j % 2 == 0 else M_QW, wings_root, up=tuple(nrm), t=WING_BONE * 0.2)
    # os de l'avant-bras ornés de petits cristaux
    for j in range(ARM_CRYS):
        crys(f"Wings_{sgn}_ArmCrys_{j}", root.lerp(wrist, 0.2 + 0.7 * j / max(1, ARM_CRYS)) + Vector((0, 0, WING_BONE * 0.5)),
             Vector((sgn * 0.3, 0.1, 1)), WING_SPAN * 0.09, M_QW if j % 2 else M_QP, wings_root, up=(1, 0, 0), sides=5)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments de pierre, plaques d'argent, cristaux, GÉODE de quartz finale
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
    if s < 0.8:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    if TAIL_BANDS and i % 3 == 1 and s < 0.9:
        B(f"Tail_Band_{i}", (2 * r * 1.05, Ln * 0.2, 2 * r * 1.0), mid, R, M_SILVER, tail_root)
    crys(f"Tail_Crest_{i}", mid + d * r * 0.85, d + t * 0.7, (0.7 * SC + r * 1.3), M_QP if i % 2 == 0 else M_QW, tail_root, up=tuple(side), sides=5)
    if TAIL_SIDE and i % 2 == 1 and s < 0.9:
        for sgn in (-1, 1):
            crys(f"Tail_SideCrys_{i}_{sgn}", mid + side * sgn * r * 0.9, side * sgn + t * 0.7, 0.6 * SC + r * 0.9,
                 M_QW if i % 4 == 1 else M_QP, tail_root, up=tuple(d), sides=5)
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_SCALEB]), tail_root, up=(sgn, 0, 0))
# GÉODE finale : anneau d'argent, gros cristal rose lumineux, couronne de cristaux roses et blancs
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.3, 0.34 * SC, BW * 0.3), tip, seg_matrix(tt_, td_, ts_), M_SILVER, tail_root)
crys("Tail_TipCore", tip + tt_ * (0.1 * SC), tt_ + Vector((0, 0, 0.2)), BW * 0.9 * TAIL_CRYS_K, M_QC, tail_root, up=tuple(ts_), r=BW * 0.11 * TAIL_CRYS_K)
for k in range(TAIL_CRYS):
    off = (k - (TAIL_CRYS - 1) / 2)
    crys(f"Tail_TipCrys_{k}", tip + tt_ * 0.1, tt_ * 0.55 + Vector((0, 0, 0.8)) + ts_ * off * 0.45, (2.2 - 0.3 * abs(off)) * SC * TAIL_CRYS_K,
         M_QW if k % 2 else M_QP, tail_root, up=tuple(ts_), sides=5)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (LÉGENDAIRE) + FX : aura, coeur de quartz, argent métallique, géode, cristaux flottants, anneau au sol
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.4 if IS_ADO else 1.7))
    R_FX = WING_SPAN * 0.55 + BW
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * R_FX, random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        kind = k % 6
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if kind in (0, 3):
            crys(f"FX_Crystal_{k}", p, dirv, FX_SIZE * random.uniform(1.3, 2.0), M_QP, master, sides=5)
        elif kind in (1, 4):
            crys(f"FX_CrystalW_{k}", p, dirv, FX_SIZE * random.uniform(1.0, 1.7), M_QW, master, sides=5)
        elif kind == 2:
            crystal(f"FX_Gem_{k}", FX_SIZE * 0.3, FX_SIZE * 0.5, FX_SIZE * 0.4, p, dirv, M_QC, master, sides=4)
        else:
            crystal(f"FX_Silver_{k}", FX_SIZE * 0.25, FX_SIZE * 0.4, FX_SIZE * 0.35, p, dirv, M_SILVER, master, sides=4)
    # anneau runique au sol : anneau d'argent + anneau rose lumineux et plots
    if GROUND_RING:
        gr = BW * GROUND_RING
        ring("FX_GroundRing", gr, 0.18 * SC, 0.06, (0, 0, 0.03), (0, 0, 1), M_SILVER, master, sides=24, up=(0, 1, 0))
        ring("FX_GroundGlow", gr * 0.8, 0.1 * SC, 0.05, (0, 0, 0.03), (0, 0, 1), M_QC, master, sides=24, up=(0, 1, 0))
        for k in range(GROUND_TICKS):
            a = 2 * math.pi * k / GROUND_TICKS
            B(f"FX_GroundTick_{k}", (0.12 * SC, 0.5 * SC, 0.05), (gr * 1.0 * math.cos(a), gr * 1.0 * math.sin(a), 0.03),
              (0, 0, math.degrees(a) + 180), M_SILVER2, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
