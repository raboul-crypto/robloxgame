import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Solaris · Adulte
#  Légendaire · Feu · Classique · monde 2
#  - Adulte majestueux : cou de 6 plaques crème cerclées d'or, 3 crocs par côté, barbe de 7 flammes, épaules et cuisses en blocs
#  - Signes distinctifs : grand soleil de poitrine (double anneau d'or, 12 rayons, 2 rubis), bois d'or ramifiés en flammes
#  - Couronne de 2 anneaux de flammes + grand halo de soleil derrière la tête, épaulières d'or à emblème rouge, genouillères
#  - Grandes ailes à armature dorée, membrane lumineuse à bord et motifs de flammes ; queue terminée par une gerbe de 9 flammes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(2207)            # même dragon à chaque exécution
TAG = "SOLARIS_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 15000          # budget de triangles de ce stade et de cette rareté
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
#    Rouge cramoisi + orange (corps), or métallique (armure, cornes, griffes), crème doré (ventre),
#    jaune soleil et orange feu ÉMISSIFS (emblème, flammes, yeux, membranes). Rareté Légendaire.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",          "#D0301C", 0.50)                                   # corps rouge
M_BODY2 = get_mat("BodyScale",     "#E2511F", 0.50)                                   # écailles orange-rouge
M_ORANGE_S = get_mat("Orange",     "#F07A1E", 0.50)                                   # orange vif (écailles, accents)
M_DARK  = get_mat("BodyDark",      "#7E1A12", 0.55)                                   # ombres, bouche, genoux
M_CREAM = get_mat("Belly",         "#F6D98A", 0.45)                                   # ventre en plaques, menton
M_GOLD  = get_mat("Gold",          "#FFC02E", 0.30, metallic=0.55)                     # armure, cornes, bracelets
M_GOLDL = get_mat("GoldLight",     "#FFE070", 0.28, metallic=0.5)                    # or clair (reflets)
M_GLOW  = get_mat("Glow",          "#FFE066", 0.30, emission="#FFD54A", strength=3.5) # soleil, pointes de flamme
M_FLAME = get_mat("Flame",         "#FF8A1E", 0.30, emission="#FF7A14", strength=3.0) # flammes orange
M_EMBER = get_mat("Ember",         "#FF4A14", 0.30, emission="#FF3A0A", strength=2.5) # braises rouges
M_WING  = get_mat("Membrane",      "#FFC046", 0.50, emission="#F59A1E", strength=1.0) # membrane des ailes
M_CLAW  = get_mat("Claw",          "#FFD24A", 0.28, metallic=0.5)                     # griffes dorées
M_FANG  = get_mat("Fang",          "#FFF3D0", 0.35)                                   # crocs
M_IRIS  = get_mat("Iris",          "#FFB020", 0.25, emission="#FFA010", strength=2.5) # iris ambre lumineux
M_WHITE = get_mat("EyeWhite",      "#F6F2E6", 0.30)
M_BLACK = get_mat("Black",         "#140806", 0.30)                                   # pupilles, narines
M_GEM   = get_mat("Gem",           "#FF3A2A", 0.12, emission="#FF2A1A", strength=2.0) # rubis du plastron
M_ROCK  = get_mat("Rock",          "#3A1410", 0.60, emission="#FF3A0A", strength=0.6) # roches volcaniques flottantes
FLAMES = [M_GOLD, M_FLAME, M_GOLDL, M_GLOW]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
BW = 3.0
BH = 2.5
LEG_H = 2.2
TORSO_L = 4.3
NECK_L = 3.6
NECK_LEAN = 0.55
NECK_N = 6
NECK_R = (0.85, 1.15)
HEAD_SCALE = 1.4
SNOUT_K = 1.0
FANGS = 3
CHEEK_N = 4
BEARD_N = 7
CROWN_RINGS = 2
CROWN_N = 11
CROWN_K = 0.85
HALO_R = 2.1
HALO_RAYS = 9
BELLY_N = 6
BELLY_RIMS = True
BELLY_SIDES = True
FLANK_ROWS = 3
FLANK_COLS = 6
NECK_FLAMES = 4
NECK_RIMS = True
CREST_N = 6
CREST_SIDE = True
BACK_PLATES = True
BLADES = 8
PAULDRON_EMBLEM = True
SUN_RAYS = 16
LEG_BEV = 1
SHIN_GOLD = True
KNEE_GUARD = True
BRACER_LOW = True
LEG_FLAMES = 2
SPUR = True
TAIL_SCALES = True
TAIL_BEV_N = 12
TAIL_BANDS = True
WING_SPAN = 8.6
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.32
WING_FINGERS = 3
WING_FLAMES = 5
WING_FLAME_L = 0.2
TAIL_L = 6.5
TAIL_STEP = 0.8
TAIL_FLAMES = 9
TAIL_FLAME_K = 1.3
FX_N = 64
FX_SIZE = 0.7
GROUND_RING = 2.6
GROUND_TICKS = 16
HIP_ARMOR = True
BELLY_BEV = 0.04
TOE_BEV = 0.03
ARMOR = True
GORGET = True
THIGH_ARMOR = True
MARKS = 3
TAIL_SIDE = True

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
    """Suite de barres qui s'affinent (cornes, bois)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def leaf_plate(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Losange plat (braise) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def sun_rays(name, center, direction, r0, length, width, n, mats, parent, a0=0.0, a1=360.0):
    """Rayons d'un soleil : éclats plats posés en cercle autour de 'center' dans le plan perpendiculaire
    à 'direction' (rayons de l'emblème de poitrine, du halo, de la collerette)."""
    m = basis(direction, (0, 0, 1))
    ex, ez = m.col[0], m.col[2]
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k / max(1, n - (0 if a1 - a0 >= 360 else 1))))
        rad = ex * math.cos(a) + ez * math.sin(a)
        L = length * (1.0 + 0.35 * (k % 2))
        shard(f"{name}_{k}", width, 0.1 * length, L, Vector(center) + rad * r0, rad, mats[k % len(mats)], parent,
              up=tuple(Vector(direction)))

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Signes distinctifs : COURONNE de cornes-flammes dorées, halo de soleil derrière le crâne.
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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne, museau, arête du museau en or, mâchoire dorée distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (0.8, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_GOLD)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris ambre lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
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
        # sourcils dorés sévères
        hbox(f"Brow_{sgn}", (0.14, 0.95, 0.22), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0), mat=M_GOLD)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_FANG, up=(1, 0, 0))

# Oreilles-ailerons dorés, plaques de joue, barbe de flammes sous le menton
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.25, (sgn * 0.8, 0.45, 0.3), (sgn * 1, 0.6, 0.45), M_GOLD)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.5, 0.08, 0.95 - 0.1 * k, (sgn * 0.85, -0.3 + k * 0.3, -0.4 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick([M_GOLD, M_GOLDL, M_FLAME], [3, 3, 1]))
for k in range(BEARD_N):
    bx = -0.6 + 1.2 * k / max(1, BEARD_N - 1)
    hshard(f"Beard_{k}", 0.34, 0.08, 0.85 - 0.18 * abs(bx), (bx, SNOUT_FRONT + 0.8 + 0.12 * abs(bx), -0.9),
           (bx * 0.4, -0.55, -1), pick([M_GOLD, M_GOLDL]), up=(1, 0, 0))

# COURONNE : anneaux d'éclats-flammes dorés derrière et au-dessus du crâne (or / or clair / flamme émissive)
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
        hshard(f"Crown_{ring_i}_{k}", 0.78 - ring_i * 0.1, 0.12, Ln, loc, direction,
               pick(FLAMES, [4, 2, 3, 1]), up=tuple(tang))

# Cornes dorées en flammes : bébé = 2 petites ; ado = recourbées + dent ; adulte = bois ramifiés
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.55, 0.1, 0.75), (sgn * 0.85, 0.3, 1.2), (sgn * 0.8, 0.8, 1.6)], 0.34, 0.14, M_GOLD)
        hshard(f"HornFlame_{sgn}", 0.3, 0.08, 0.7, (sgn * 0.8, 0.8, 1.6), (sgn * 0.1, 0.5, 1), M_FLAME, up=(1, 0, 0))
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.6, 0.15, 0.78), (sgn * 0.9, 0.35, 1.4), (sgn * 0.95, 0.9, 1.95),
                               (sgn * 0.7, 1.5, 2.25)], 0.38, 0.15, M_GOLD)
        bar(f"Head_HornTine_{sgn}", hv((sgn * 0.9, 0.35, 1.4)), hv((sgn * 1.4, 0.2, 1.95)), 0.16 * HS, M_GOLD, H)
        hshard(f"HornFlame_{sgn}", 0.5, 0.09, 1.1, (sgn * 0.7, 1.5, 2.25), (0, 0.6, 0.8), M_FLAME, up=(1, 0, 0))
        hshard(f"HornFlameB_{sgn}", 0.28, 0.08, 0.7, (sgn * 1.4, 0.2, 1.95), (sgn * 0.5, 0, 1), M_GLOW, up=(0, 1, 0))
    else:
        a0, a1 = Vector((sgn * 0.6, 0.2, 0.78)), Vector((sgn * 0.95, 0.5, 1.7))
        a2, a3 = Vector((sgn * 1.2, 1.1, 2.2)), Vector((sgn * 1.1, 1.8, 2.6))
        hchain(f"Antler_{sgn}", [a0, a1, a2, a3], 0.42, 0.17, M_GOLD)
        t1p, t2p, t3p = Vector((sgn * 1.7, 0.25, 2.1)), Vector((sgn * 2.05, 1.0, 2.7)), Vector((sgn * 0.8, 0.1, 2.4))
        bar(f"Head_AntlerTine1_{sgn}", hv(a1), hv(t1p), 0.2 * HS, M_GOLD, H)
        bar(f"Head_AntlerTine2_{sgn}", hv(a2), hv(t2p), 0.18 * HS, M_GOLD, H)
        bar(f"Head_AntlerTine3_{sgn}", hv(a1.lerp(a2, 0.5)), hv(t3p), 0.16 * HS, M_GOLD, H)
        for nm, p, dr, m_ in (("A", a3, (0, 0.5, 1), M_FLAME), ("B", t1p, (sgn * 0.6, 0, 1), M_GLOW),
                              ("C", t2p, (sgn * 0.4, 0.3, 1), M_FLAME), ("D", t3p, (0, 0, 1), M_GLOW)):
            hshard(f"AntlerFlame{nm}_{sgn}", 0.6, 0.1, 1.1, tuple(p), dr, m_, up=(1, 0, 0))

# Armure de tête (ado / adulte) : plaque frontale d'or + rubis, plaques de joue
if ARMOR:
    hwedge("ForeheadPlate", (1.2, 1.0, 0.22), (0, -0.05, 0.88), mat=M_GOLD, top_x=0.7, top_y=0.8, bevel=0.04)
    crystal("Head_ForeGem", 0.16 * HS, 0.12 * HS, 0.14 * HS, hv((0, -0.55, 1.0)), (0, -1, 0.6), M_GEM, H)
    for sgn in (-1, 1):
        hwedge(f"CheekPlate_{sgn}", (0.14, 1.0, 0.7), (sgn * 1.0, 0.3, -0.2), mat=M_GOLD, top_x=0.8, bevel=0.0)

# HALO DE SOLEIL (aura) derrière la tête : anneau d'or + anneau lumineux + rayons
if HALO_R > 0:
    hc = (0, 1.3, 0.35)
    ring("Head_HaloRing", HALO_R * HS, 0.4 * HS, 0.16 * HS, hv(hc), (0, 1, 0), M_GOLD, H, sides=20)
    ring("Head_HaloGlow", HALO_R * HS * 0.8, 0.16 * HS, 0.1 * HS, hv((0, 1.4, 0.35)), (0, 1, 0), M_GLOW, H, sides=20)
    sun_rays("Head_HaloRay", hv(hc), (0, 1, 0), HALO_R * HS * 1.0, 0.8 * HS, 0.5 * HS, HALO_RAYS,
             [M_GOLDL, M_FLAME], H, a0=-150, a1=150)
    # lecture : rayons dans le plan XZ de la tête, dirigés vers l'extérieur

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre doré, SOLEIL de poitrine, armure, crête double
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

# Plastron doré + plaques de ventre séparées par des filets d'or
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root, bevel=BELLY_BEV * SC)
    if BELLY_RIMS:
        B(f"Body_BellyRim_{i}", (BW * 0.86, 0.07 * SC, 0.22 * SC), (0, y + pl * 0.54, ZC - BH / 2 + 0.03), mat=M_GOLD, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# SOLEIL sur la poitrine : bouclier d'or, disque lumineux, anneau d'or, rayons en flammes
SUN_C = Vector((0, -TL * 0.5 - 0.05, ZC + BH * 0.02))
wedge("Body_SunShield", (BW * 0.8, 0.24 * SC, BH * 0.78), SUN_C + Vector((0, 0.1, 0)), mat=M_GOLD, parent=body_root,
      top_x=0.85, top_y=1.0, bevel=0.03 * SC)
prism("Body_SunDisc", BH * 0.25, 0.16 * SC, SUN_C + Vector((0, -0.04, 0)), (0, -1, 0), M_GLOW, body_root, sides=12)
ring("Body_SunRing", BH * 0.33, 0.07 * BH, 0.1 * SC, SUN_C + Vector((0, -0.08, 0)), (0, -1, 0), M_GOLDL, body_root, sides=12)
sun_rays("Body_SunRay", SUN_C + Vector((0, -0.07, 0)), (0, -1, 0), BH * 0.34, BH * 0.24, BH * 0.12, SUN_RAYS,
         [M_GLOW, M_FLAME], body_root)
if IS_ADULTE:
    ring("Body_SunRing2", BH * 0.42, 0.05 * BH, 0.08 * SC, SUN_C + Vector((0, -0.05, 0)), (0, -1, 0), M_GOLD, body_root, sides=12)
    for sgn in (-1, 1):
        crystal(f"Body_SunGem_{sgn}", 0.12 * SC, 0.1 * SC, 0.1 * SC, SUN_C + Vector((sgn * BW * 0.34, -0.1, -BH * 0.18)),
                (0, -1, 0.1), M_GEM, body_root)

# Gorgerin d'or à la base du cou (ado / adulte)
if GORGET:
    wedge("Body_Gorget", (BW * 0.85, 0.8 * SC, BH * 0.4), (0, -TL * 0.46, ZC + BH * 0.42), mat=M_GOLD, parent=body_root,
          top_x=0.75, top_y=0.8, bevel=0.04 * SC)

# Écailles rouges / orange en quinconce sur les flancs, quelques-unes cerclées d'or
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_ORANGE_S, M_BODY2, M_GOLD], [3, 2, 2, 1]), body_root, up=(sgn, 0, 0))

# Cou : un segment rouge + une plaque dorée devant par maillon, crête de flammes sur la nuque
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
        B(f"Body_NeckRim_{i}", (2 * r * 0.88, 0.08 * SC, 0.26 * SC), mid - d * (r * 0.95) + t * Ln * 0.5, R, M_GOLD, body_root)
    # crête de flammes sur la nuque
    for k in range(NECK_FLAMES):
        off = (k - (NECK_FLAMES - 1) / 2) * 0.5
        shard(f"Body_NeckFlame_{i}_{k}", 0.6 * SC, 0.1 * SC, (1.2 + 0.6 * (1 - s)) * SC + random.random() * 0.3,
              mid + d * r * 0.8 + side * off * r, d + t * 0.9 + side * off * 0.4, pick(FLAMES, [3, 3, 2, 1]),
              body_root, up=tuple(side))
    if IS_ADULTE or (IS_ADO and i % 2 == 0):
        for sgn in (-1, 1):
            shard(f"Body_NeckSide_{i}_{sgn}", 0.55 * SC, 0.1 * SC, 0.7 * SC, mid + side * sgn * r * 0.85,
                  side * sgn + t * 0.8 + d * 0.3, pick([M_GOLD, M_GOLDL]), body_root, up=tuple(d))

# Crête dorsale DOUBLE : rangée centrale grande + deux rangées latérales plus petites
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.85 * SC, 0.12 * SC, (1.15 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), pick([M_GOLD, M_GOLDL, M_FLAME], [3, 2, 2]), body_root, up=(1, 0, 0))
    if CREST_SIDE:
        for sgn in (-1, 1):
            shard(f"Body_CrestSide_{k}_{sgn}", 0.55 * SC, 0.1 * SC, 0.7 * SC, (sgn * BW * 0.28, y + 0.2, ZC + BH / 2 - 0.08),
                  (sgn * 0.45, 0.5, 1), pick([M_FLAME, M_GOLD]), body_root, up=(1, 0, 0))

# Plaques d'armure dorées sur le dos (ado / adulte)
if BACK_PLATES:
    for sgn in (-1, 1):
        wedge(f"Body_BackPlate_{sgn}", (BW * 0.36, TL * 0.3, 0.24 * SC), (sgn * BW * 0.3, -TL * 0.08, ZC + BH / 2 + 0.01),
              (0, sgn * 8, 0), M_GOLD, body_root, top_x=0.85, top_y=0.85, bevel=0.03)
        B(f"Body_BackPlateB_{sgn}", (BW * 0.3, TL * 0.2, 0.2 * SC), (sgn * BW * 0.3, TL * 0.2, ZC + BH / 2 - 0.02),
          (0, sgn * 6, 0), M_GOLD, body_root)

# ÉPAULIÈRES en or : bloc d'or, emblème rouge en cœur, éventail de lames-flammes
for sgn in (-1, 1):
    pw = BW * 0.4
    px = sgn * (BW * 0.5 + 0.03 * SC)
    py, pz = -TL * 0.2, ZC + BH * 0.34
    wedge(f"Body_Pauldron_{sgn}", (pw, TL * 0.3, BH * 0.5), (px, py, pz), (0, -sgn * 12, 0), M_GOLD, body_root,
          top_x=0.8, top_y=0.85, bevel=0.05 * SC)
    if PAULDRON_EMBLEM:
        B(f"Body_PauldronRim_{sgn}", (0.1 * SC, TL * 0.22, BH * 0.38), (px + sgn * pw * 0.47, py, pz - 0.02), (0, -sgn * 12, 0), M_GOLDL, body_root)
        wedge(f"Body_PauldronEmblem_{sgn}", (0.14 * SC, TL * 0.17, BH * 0.3), (px + sgn * (pw * 0.5 + 0.02), py, pz - 0.02),
              (0, -sgn * 12, 0), M_BODY, body_root, top_x=1.0, top_y=0.7, bevel=0.0)
    if PAULDRON_EMBLEM:
        wedge(f"Body_PauldronUpper_{sgn}", (pw * 0.8, TL * 0.22, BH * 0.18), (px - sgn * pw * 0.05, py, pz + BH * 0.3),
              (0, -sgn * 12, 0), M_GOLDL, body_root, top_x=0.7, top_y=0.8, bevel=0.03 * SC)
    if HIP_ARMOR:
        wedge(f"Body_HipPlate_{sgn}", (0.16 * SC, TL * 0.28, BH * 0.55), (sgn * (BW * 0.5 + 0.02), TL * 0.3, ZC + BH * 0.05),
              mat=M_GOLD, parent=body_root, top_x=0.8, top_y=0.9, bevel=0.03 * SC)
        wedge(f"Body_RibPlate_{sgn}", (0.14 * SC, TL * 0.3, BH * 0.35), (sgn * (BW * 0.5 + 0.02), -TL * 0.02, ZC - BH * 0.18),
              mat=M_GOLD, parent=body_root, top_x=0.8, top_y=0.9, bevel=0.03 * SC)
    for k in range(BLADES):
        f = k / max(1, BLADES - 1)
        shard(f"Body_PauldronBlade_{sgn}_{k}", 0.5 * SC, 0.1 * SC, (1.5 - 0.3 * abs(f - 0.4)) * SC,
              (px - sgn * pw * 0.1, py + 0.35 * SC * (f - 0.2) + 0.1, pz + BH * 0.2),
              (sgn * (0.5 - 0.3 * f), 0.7 * f + 0.1, 0.9 - 0.2 * f), pick([M_GOLD, M_GOLDL, M_FLAME], [3, 3, 1]), body_root,
              up=(1, 0, 0))

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, genouillère, jambière dorée, bracelet, pied rouge, 3 doigts + 3 griffes
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
        mat=(M_GOLD if SHIN_GOLD else M_BODY2), parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    if KNEE_GUARD:
        wedge(f"{name}_Knee", (th * 1.0, th * 0.55, thigh_h * 0.5), (x, y + yo - th * 0.62, FOOT_H + SHIN_H + thigh_h * 0.12),
              mat=M_GOLD, parent=legs_root, top_x=0.7, top_y=0.7, bevel=0.04 * SC)
    if THIGH_ARMOR:
        wedge(f"{name}_ThighPlate", (0.14 * SC, th * 1.2, thigh_h * 0.6), (x + sgn * th * 0.66, y, FOOT_H + SHIN_H + thigh_h * 0.55),
              mat=M_GOLD, parent=legs_root, top_x=0.8, bevel=0.03 * SC)
    # bracelets d'or (haut et bas de jambière)
    bh_ = SHIN_H * 0.2
    box(f"{name}_Bracer", (th * 1.08, th * 1.12, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.82),
        mat=M_GOLDL, parent=legs_root, bevel=LEG_BEV * 0.03 * SC)
    if BRACER_LOW:
        B(f"{name}_BracerLow", (th * 1.06, th * 1.1, bh_ * 0.8), (x, y + yo, FOOT_H + SHIN_H * 0.18), mat=M_GOLDL, parent=legs_root)
    # flammes émissives sur la jambière extérieure
    for k in range(LEG_FLAMES):
        shard(f"{name}_ShinFlame_{k}", th * 0.4, 0.07 * SC, SHIN_H * (0.7 - 0.2 * k), (x + sgn * th * 0.47, y + yo + (k - 0.5) * th * 0.25, FOOT_H + SHIN_H * 0.15),
              (sgn * 0.1, 0, 1), M_FLAME if k == 0 else M_EMBER, legs_root, up=(sgn, 0, 0))
    # Pied plat + 3 doigts + 3 griffes dorées
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_GOLD,
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
# 12. AILES : armature dorée, grande membrane orange lumineuse, bord en flammes, motifs de flamme rouges
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_GOLD, M_WING, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.5, memb_t=WING_BONE * 0.45, claw_mat=M_CLAW)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tips.append(wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                                    -WING_SPAN * (0.05 + 0.5 * f))))
    # bord d'attaque rouge en haut de l'aile (comme sur le concept) + pique au poignet
    shard(f"Wings_{sgn}_WristSpike", WING_BONE * 1.8, WING_BONE * 1.3, WING_SPAN * 0.15, wrist, (sgn * 0.5, 0.2, 1), M_CLAW, wings_root)
    for k, tip in enumerate(tips):
        # flamme au bout de chaque doigt
        shard(f"Wings_{sgn}_TipFlame_{k}", WING_SPAN * 0.07, WING_BONE * 0.5, WING_SPAN * WING_FLAME_L * (1.0 - 0.1 * k), tip,
              (sgn * 0.15, 0.5, 0.9), pick([M_FLAME, M_GLOW]), wings_root, up=(0, 1, 0))
        if k + 1 < len(tips):
            mid = (tip + tips[k + 1]) / 2
            for j in range(WING_FLAMES):
                shard(f"Wings_{sgn}_EdgeFlame_{k}_{j}", WING_SPAN * 0.055, WING_BONE * 0.4, WING_SPAN * WING_FLAME_L * 0.7,
                      tip.lerp(tips[k + 1], (j + 0.5) / WING_FLAMES), (sgn * 0.1, 0.4, 0.9), pick([M_GLOW, M_FLAME, M_FLAME]),
                      wings_root, up=(0, 1, 0))
            # motif de flamme rouge posé sur la membrane (des deux côtés)
            nrm = (tip - wrist).cross(tips[k + 1] - wrist).normalized()
            cen = (wrist + tip + tips[k + 1]) / 3
            for j in range(MARKS):
                sh_ = (tips[k + 1] - tip) * 0.2 * ((j - (MARKS - 1) / 2) * 1.6)
                for side_ in (-1, 1):
                    shard(f"Wings_{sgn}_Mark_{k}_{j}_{side_}", WING_SPAN * 0.06, WING_BONE * 0.25, (cen - wrist).length * (0.85 - 0.15 * j),
                          wrist.lerp(cen, 0.3) + sh_ + nrm * side_ * (WING_BONE * 0.3), cen - wrist + sh_ * 0.3, M_EMBER, wings_root, up=tuple(nrm))

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments rouges, plaques dorées, bandes d'or, FLAMME DORÉE finale
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
        B(f"Tail_Band_{i}", (2 * r * 1.05, Ln * 0.2, 2 * r * 1.0), mid, R, M_GOLD, tail_root)
    shard(f"Tail_Crest_{i}", 0.9 * r + 0.2, 0.1 * SC, 0.55 * SC + r * 0.9, mid + d * r * 0.85, d + t * 0.7,
          pick([M_GOLD, M_FLAME, M_GOLDL], [3, 2, 2]), tail_root, up=(1, 0, 0))
    if TAIL_SIDE and i % 2 == 1 and s < 0.9:
        for sgn in (-1, 1):
            shard(f"Tail_SideSpike_{i}_{sgn}", 0.5 * r + 0.15, 0.08 * SC, 0.5 * SC + r * 0.8, mid + side * sgn * r * 0.9,
                  side * sgn + t * 0.7, pick([M_GOLD, M_FLAME]), tail_root, up=tuple(d))
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_ORANGE_S]), tail_root, up=(sgn, 0, 0))
# flamme dorée au bout : anneau d'or, orbe lumineuse, gerbe de flammes
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.3, 0.34 * SC, BW * 0.3), tip, seg_matrix(tt_, td_, ts_), M_GOLD, tail_root)
prism("Tail_TipOrb", BW * 0.17 * TAIL_FLAME_K, BW * 0.3 * TAIL_FLAME_K, tip + tt_ * (0.25 * SC), tt_, M_GLOW, tail_root, sides=8)
for k in range(TAIL_FLAMES):
    off = (k - (TAIL_FLAMES - 1) / 2)
    shard(f"Tail_Flame_{k}", 0.55 * SC * TAIL_FLAME_K, 0.14 * SC, (2.0 - 0.35 * abs(off)) * SC * TAIL_FLAME_K,
          tip + tt_ * 0.2, tt_ * 0.55 + Vector((0, 0, 0.9)) + ts_ * off * 0.4, [M_GLOW, M_FLAME, M_GOLD][k % 3], tail_root, up=tuple(ts_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (LÉGENDAIRE) + FX : halo, soleil, flammes, or métallique, anneau au sol, braises
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.4 if IS_ADO else 1.7))
    R_FX = WING_SPAN * 0.55 + BW
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * R_FX, random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        kind = k % 7
        if kind in (0, 3, 5):
            leaf_plate(f"FX_Ember_{k}", p, Vector([random.uniform(-1, 1) for _ in range(3)]), FX_SIZE * random.uniform(0.9, 1.4),
                       FX_SIZE * 0.6, pick([M_EMBER, M_FLAME]), master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.05 * SC)
        elif kind in (1, 4):
            prism(f"FX_Orb_{k}", FX_SIZE * random.uniform(0.3, 0.5), FX_SIZE * 0.6, p, (random.uniform(-1, 1), 1, random.uniform(-1, 1)),
                  M_GLOW, master, sides=8)
        elif kind == 2:
            crystal(f"FX_Rock_{k}", FX_SIZE * 0.5, FX_SIZE * 0.7, FX_SIZE * 0.4, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
                    M_ROCK, master, sides=5)
        else:
            shard(f"FX_Spark_{k}", FX_SIZE * 0.4, 0.05 * SC, FX_SIZE * 1.4, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
                  M_GLOW, master, up=(0, 0, 1))
    # anneau runique au sol : deux anneaux (or + lumière) et plots dorés
    if GROUND_RING:
        gr = BW * GROUND_RING
        ring("FX_GroundRing", gr, 0.18 * SC, 0.06, (0, 0, 0.03), (0, 0, 1), M_GOLD, master, sides=24, up=(0, 1, 0))
        ring("FX_GroundGlow", gr * 0.8, 0.1 * SC, 0.05, (0, 0, 0.03), (0, 0, 1), M_GLOW, master, sides=24, up=(0, 1, 0))
        for k in range(GROUND_TICKS):
            a = 2 * math.pi * k / GROUND_TICKS
            B(f"FX_GroundTick_{k}", (0.12 * SC, 0.5 * SC, 0.05), (gr * 1.0 * math.cos(a), gr * 1.0 * math.sin(a), 0.03),
              (0, 0, math.degrees(a) + 90 + 90), M_GOLDL, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
