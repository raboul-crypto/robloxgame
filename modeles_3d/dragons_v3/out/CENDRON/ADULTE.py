import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Cendron · Adulte
#  Commun · Feu · Classique · monde 2
#  - Adulte puissant : épaules et cuisses en blocs, cou de 6 plaques cendre, 3 crocs par côté, deux grandes cornes noires torsadées
#  - Signe distinctif : fissures de lave orange sur tout le corps, ventre gris cendre, crête noire, ailes rouges aux bords gris effilochés
#  - Plaques de basalte fissurées sur le dos, genouillères sombres, pointes noires sur la nuque, le dos et la queue
#  - Grandes ailes, longue queue terminée par 3 pointes noires et une braise
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1110)            # même dragon à chaque exécution
TAG = "CENDRON_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 6000          # budget de triangles de ce stade et de cette rareté
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
#    Rouge braise (corps), gris cendre (ventre, bords d'ailes), noir basalte (cornes, crête),
#    orange lave (fissures et yeux). Commun : seuls les yeux brillent ; les fissures sont orange vif, sans émission.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#B02E1E", 0.50)   # corps principal rouge braise
M_BODY2 = get_mat("BodyScale", "#8A2318", 0.50)   # écailles, dessus des pattes
M_DARK  = get_mat("BodyDark",  "#4D1511", 0.55)   # genoux, bouche, ombres, taches
M_HOT   = get_mat("Crest2",    "#D8461F", 0.45)   # crête secondaire, flammèches rouge vif
M_ASH   = get_mat("Belly",     "#A8A29C", 0.60)   # ventre en plaques, plastron, menton (gris cendre)
M_ASH2  = get_mat("AshDark",   "#716B66", 0.65)   # bords d'ailes effilochés, ombres de cendre
M_BLACK_ROCK = get_mat("Horn", "#2B2523", 0.55)   # cornes, crête, plaques de basalte
M_ROCK2 = get_mat("Rock",      "#3E3632", 0.65)   # plaques de basalte (épaules, dos)
M_CLAW  = get_mat("Claw",      "#EDE6DA", 0.35)   # griffes, crocs
M_WING  = get_mat("Membrane",  "#C03520", 0.55)   # membrane rouge
M_BONE  = get_mat("WingBone",  "#8C8784", 0.55)   # os des ailes (gris cendre)
M_WHITE = get_mat("EyeWhite",  "#F2F2EA", 0.30)
M_IRIS  = get_mat("Eye",       "#FF8A12", 0.25, emission="#FF7A10", strength=1.8)   # iris orange lumineux
M_PUPIL = get_mat("Black",     "#0A0A0A", 0.30)
M_GLOW  = get_mat("Glow",      "#FF7A12", 0.40)   # fissures de lave orange vif (pas d'émission : Commun)
M_EMBER = get_mat("Ember",     "#FF7A1A", 0.50)   # braises flottantes (non émissives)
M_CREST = M_BLACK_ROCK
SPIKES = [M_BLACK_ROCK, M_BLACK_ROCK, M_ROCK2]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
BW = 2.5
BH = 2.3
LEG_H = 2.1
TORSO_L = 4.3
NECK_L = 3.6
NECK_LEAN = 1.2
NECK_N = 6
NECK_R = (0.85, 1.15)
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
CHEEK_N = 3
MANE_RINGS = 2
MANE_N = 9
BELLY_N = 6
FLANK_ROWS = 3
FLANK_COLS = 5
CRACKS = 4
DORSAL_CRACKS = 3
NECK_SPIKE_X = (-0.4, 0.4)
CREST_N = 6
SHOULDER_SPIKES = 4
ROCK_PLATES = 2
BRACER_K = 0.62
LEG_BEV = 1
LEG_CRACKS = True
TAIL_SCALES = True
TAIL_BEV_N = 2
BELLY_SIDES = True
THIGH_SPIKES = 2
WING_SPAN = 6.6
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.32
WING_FINGERS = 3
WING_FRAY = 3
WING_CRACKS = 3
TAIL_L = 6.5
TAIL_STEP = 0.9
TAIL_TIP = 2.0
FX_N = 4
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

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.9, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, tronc)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def crack(name, pts, th, parent, up, mat=None):
    """Fissure de lave : zigzag de fines barres lumineuses posées sur la peau (up = normale de la surface)."""
    mat = mat or M_GLOW
    for i in range(len(pts) - 1):
        link(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up, extra=th * 0.9, bevel=0, depth=th * 0.45)

def zigzag(y0, z0, n, dy, dz, sgn_x, xfun):
    """Points d'une fissure en zigzag sur un flanc : (x, y, z) ; xfun(y) donne la surface."""
    pts, y, z = [], y0, z0
    for k in range(n + 1):
        pts.append((xfun(y), y, z))
        y += dy * random.uniform(0.7, 1.3)
        z += dz * random.uniform(0.6, 1.3) * (1 if k % 2 == 0 else -0.8)
    return pts

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

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne, museau, arête noire du museau, mâchoire cendre, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (0.7, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_CREST)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_ASH)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
hbox("Chin", (0.8, 0.5, 0.2), (0, -0.55 - 1.85 * SNOUT_K, -0.9), mat=M_ASH)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_DARK)

# Fissures de lave sur le crâne et le museau
hbox("CrackSkull_0", (0.1, 0.9, 0.05), (0.15, 0.1, 0.87), rot=(0, 0, 25), mat=M_GLOW)
if not IS_BEBE:
    hbox("CrackSkull_1", (0.08, 0.7, 0.05), (-0.25, 0.45, 0.86), rot=(0, 0, -30), mat=M_GLOW)
    hbox("CrackSnout_0", (0.07, 0.8, 0.04), (0.35, SNOUT_FRONT + 0.9, 0.2), rot=(0, 0, 20), mat=M_GLOW)
if IS_ADULTE:
    for sgn in (-1, 1):
        hbox(f"CrackCheek_{sgn}", (0.05, 0.7, 0.08), (sgn * 0.96, 0.35, -0.2), rot=(0, 0, 0), mat=M_GLOW)

# Yeux : blanc, iris orange lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.88, 0.95, 0.68, 0.8, 0.4, 0.56
else:
    EW, EH, IW, IH, PW, PH = 0.55, 0.62, 0.4, 0.52, 0.1, 0.48
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_PUPIL)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.22), (sgn * 1.07, ey - 0.15, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, ey + 0.12, ez - 0.2), mat=M_WHITE)
    else:
        # sourcils noirs sévères, inclinés vers le museau
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.24), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(14, 0, 0),
             mat=M_CREST)

# Crocs (bébé : aucun ; ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.55 + k * 0.5
        hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
               M_CLAW, up=(1, 0, 0))

# Oreilles rouges et pointes de joue noires
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.6, 0.1, 1.0, (sgn * 0.8, 0.5, 0.3), (sgn * 1, 0.6, 0.35), M_HOT)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.4, 0.1, 0.8 - 0.1 * k, (sgn * 0.85, -0.3 + k * 0.32, -0.42 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick(SPIKES))

# Éventail de pointes noires derrière le crâne (cendre et basalte)
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hshard(f"Mane_{ring_i}_{k}", 0.55 - ring_i * 0.08, 0.14, 1.1 + ring_i * 0.2 + random.random() * 0.3,
               loc, direction, pick(SPIKES + [M_BODY2], [3, 3, 2, 2][:len(SPIKES) + 1]), up=tuple(rad))

# Cornes noires (bébé : courtes ; ado : longues et recourbées ; adulte : grandes et torsadées)
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.55, 0.55, 0.4), (sgn * 0.62, 0.2, 0.82), mat=M_ROCK2)
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.6, 0.2, 0.9), (sgn * 0.78, 0.4, 1.3), (sgn * 0.7, 0.85, 1.65)],
               0.34, 0.13, M_CREST)
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.25, 0.9), (sgn * 0.85, 0.45, 1.5), (sgn * 0.85, 0.95, 2.05),
                               (sgn * 0.62, 1.6, 2.3)], 0.38, 0.14, M_CREST)
    else:
        pts = [Vector((sgn * 0.62, 0.25, 0.9)), Vector((sgn * 1.0, 0.45, 1.55)), Vector((sgn * 0.8, 0.8, 2.25)),
               Vector((sgn * 1.15, 1.3, 2.8)), Vector((sgn * 0.9, 1.9, 3.15)), Vector((sgn * 0.6, 2.5, 3.2))]
        hchain(f"Horn_{sgn}", pts, 0.46, 0.14, M_CREST)
        for k in (1, 2, 3):          # anneaux rouges sombres : effet torsadé
            c = pts[k]
            hbox(f"HornRing_{sgn}_{k}", (0.56 - 0.07 * k, 0.5, 0.2), (c.x, c.y, c.z), rot=(0, 20 * sgn * k, 30 * sgn), mat=M_DARK)
    if not IS_BEBE:
        hbox(f"HornCrack_{sgn}", (0.07, 0.07, 0.5), (sgn * 0.62, 0.22, 0.95), mat=M_GLOW)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre, flancs, fissures, crête, épaulières
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser écailles et fissures sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron cendre sur le poitrail + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_ASH, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_ASH, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_ASH, parent=body_root)

# Écailles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, (sgn * (half_w(y) - 0.03 * SC), y, z),
                  (sgn * 0.3, 1, -0.1), pick([M_BODY2, M_DARK, M_BODY2]), body_root, up=(sgn, 0, 0))

# Fissures de lave sur les flancs et le dos (signe distinctif)
for sgn in (-1, 1):
    for k in range(CRACKS):
        y0 = -TL * 0.38 + (TL * 0.72) * (k + random.random() * 0.4) / CRACKS
        z0 = ZC + BH * random.uniform(0.1, 0.32)
        pts = zigzag(y0, z0, 3, 0.32 * SC, -0.3 * SC, sgn, lambda y: sgn * (half_w(y) + 0.005))
        crack(f"Body_Crack_{sgn}_{k}", pts, 0.1 * SC + 0.03, body_root, (sgn, 0, 0))
        if IS_ADULTE and k % 2 == 0:       # petite branche
            px, py, pz = pts[2]
            crack(f"Body_CrackB_{sgn}_{k}", [(px, py, pz), (px, py + 0.25 * SC, pz - 0.35 * SC)], 0.08 * SC + 0.03,
                  body_root, (sgn, 0, 0))
for k in range(DORSAL_CRACKS):
    y = -TL * 0.3 + (TL * 0.6) * k / max(1, DORSAL_CRACKS - 1)
    crack(f"Body_BackCrack_{k}", [(-0.28 * BW, y, ZC + BH / 2 + 0.01), (0.0, y + 0.3 * SC, ZC + BH / 2 + 0.01),
                                  (0.26 * BW, y + 0.05 * SC, ZC + BH / 2 + 0.01)], 0.1 * SC + 0.03, body_root, (0, 0, 1))

# Cou : courbe lissée de la tête vers le torse, un segment rouge + une plaque cendre par maillon
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):
    p = NECK_BASE.lerp(NECK_TOP, tt)
    p.y -= 0.3 * NECK_LEAN * math.sin(math.pi * tt)
    NECK_CTRL.append(p)
_neck_curve = sample_curve(NECK_CTRL)
_neck_len = sum((b - a).length for a, b in zip(_neck_curve, _neck_curve[1:]))
NECK_SPINE = resample(_neck_curve, _neck_len / NECK_N * 0.999)   # exactement NECK_N maillons
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
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_ASH, body_root)
    # pointes noires sur la nuque
    for k, amt in enumerate(NECK_SPIKE_X):
        shard(f"Body_NeckSpike_{i}_{k}", 0.5 * SC, 0.12 * SC, (0.8 + 0.4 * (1 - s)) * SC + random.random() * 0.2,
              mid + d * r * 0.85 + side * amt * r, d + t * 0.8 + side * amt * 0.3, pick(SPIKES), body_root, up=tuple(side))
    if IS_ADULTE and i % 2 == 0:
        for sgn in (-1, 1):
            crack(f"Body_NeckCrack_{i}_{sgn}", [mid + side * sgn * (r + 0.01) + d * r * 0.3,
                                                mid + side * sgn * (r + 0.01) - d * r * 0.1 + t * Ln * 0.3,
                                                mid + side * sgn * (r + 0.01) - d * r * 0.5 - t * Ln * 0.1],
                  0.1 * SC + 0.03, body_root, tuple(side * sgn))

# Crête dorsale : pointes noires sur le torse (rouges vifs entre elles chez l'adulte)
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.8 * SC, 0.14 * SC, (1.05 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), pick(SPIKES), body_root, up=(1, 0, 0))
    if IS_ADULTE and k < CREST_N - 1:
        shard(f"Body_Crest2_{k}", 0.55 * SC, 0.1 * SC, 0.7 * SC, (0, y + 0.35 * SC * 1.6, ZC + BH / 2 - 0.05),
              (0, 0.45, 1), M_HOT, body_root, up=(1, 0, 0))

# Épaulières : pointes noires + plaques de basalte fissurées (ado : 1 plaque, adulte : 2)
for sgn in (-1, 1):
    for k in range(SHOULDER_SPIKES):
        shard(f"Body_ShoulderSpike_{sgn}_{k}", 0.45 * SC, 0.12 * SC, (0.9 - 0.1 * k) * SC,
              (sgn * BW * (0.42 + 0.03 * k), -TL * 0.2 + 0.2 * k * SC, ZC + BH * (0.4 - 0.12 * k)),
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.5 * k), pick(SPIKES), body_root)
    if ROCK_PLATES >= 1:
        wedge(f"Body_RockPlate_{sgn}", (BW * 0.5, TL * 0.3, 0.3 * SC + 0.1), (sgn * BW * 0.3, -TL * 0.1, ZC + BH / 2 + 0.02),
              (0, sgn * 8, 0), M_ROCK2, body_root, top_x=0.85, top_y=0.85, bevel=0.04)
        crack(f"Body_RockCrack_{sgn}", [(sgn * BW * 0.22, -TL * 0.2, ZC + BH / 2 + 0.2 * SC + 0.1),
                                        (sgn * BW * 0.32, -TL * 0.1, ZC + BH / 2 + 0.2 * SC + 0.1),
                                        (sgn * BW * 0.26, TL * 0.0, ZC + BH / 2 + 0.2 * SC + 0.1)],
              0.1 * SC + 0.03, body_root, (0, 0, 1))
    if ROCK_PLATES >= 2:
        B(f"Body_RockPlateB_{sgn}", (BW * 0.34, TL * 0.2, 0.24 * SC + 0.05), (sgn * BW * 0.32, TL * 0.17, ZC + BH / 2 - 0.02),
          (0, sgn * 6, 0), M_BLACK_ROCK, body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, tibia, genouillère sombre, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.24)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.9, th * 0.95, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    # Genouillère sombre (bracelet de braise)
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.5),
        mat=M_DARK, parent=legs_root)
    B(f"{name}_BracerTop", (th * 1.12, th * 1.16, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.5 + bh_ / 2),
      mat=M_ROCK2, parent=legs_root)
    if LEG_CRACKS:
        crack(f"{name}_Crack", [(x + sgn * (th * 0.53 + 0.01), y + yo - th * 0.3, FOOT_H + SHIN_H * 0.5 + bh_ * 0.3),
                                (x + sgn * (th * 0.53 + 0.01), y + yo + th * 0.05, FOOT_H + SHIN_H * 0.5),
                                (x + sgn * (th * 0.53 + 0.01), y + yo - th * 0.2, FOOT_H + SHIN_H * 0.5 - bh_ * 0.3)],
              0.09 * SC + 0.03, legs_root, (sgn, 0, 0))
    # Pied plat + 3 doigts + 3 griffes
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    # Pointes de cuisse noires
    for k in range(THIGH_SPIKES):
        shard(f"{name}_Spike_{k}", 0.4 * SC, 0.1 * SC, (0.8 - 0.12 * k) * SC,
              (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
              (sgn * 0.8, 0.5, -0.6), pick(SPIKES), legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES membraneuses : rouges, bords gris cendre effilochés
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_BONE, M_WING, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.55, memb_t=WING_BONE * 0.45, claw_mat=M_BLACK_ROCK)
    elbow = root + Vector((sgn * WING_SPAN * 0.38, WING_SPAN * WING_SWEEP * 0.25, WING_SPAN * WING_LIFT * 0.9))
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tips.append(wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                                    -WING_SPAN * (0.05 + 0.55 * f))))
    # même polygone de bord que wing() : le gris cendre recouvre le tiers extérieur de la membrane
    edge = [elbow.lerp(wrist, 0.5)] + tips
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        plate(f"Wings_{sgn}_Ash_{k}", [wrist.lerp(a, 0.62), a, b, wrist.lerp(b, 0.62)], WING_BONE * 0.6,
              M_ASH if k % 2 == 0 else M_ASH2, wings_root)
    # bords effilochés : petites pointes de cendre qui dépassent du bord libre
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        for j in range(WING_FRAY):
            m = a.lerp(b, (j + 0.5) / WING_FRAY)
            out = (m - wrist).normalized()
            shard(f"Wings_{sgn}_Fray_{k}_{j}", WING_BONE * 1.7, WING_BONE * 0.5, WING_SPAN * 0.1 + random.random() * 0.2,
                  m - out * 0.05, out + Vector((0, 0.3, -0.2)), M_ASH2, wings_root)
    # fissures de lave sur la membrane
    for k in range(WING_CRACKS):
        a = elbow.lerp(wrist, 0.5).lerp(tips[min(k, len(tips) - 1)], 0.2 + 0.12 * k)
        b = a.lerp(wrist, 0.3) + Vector((0, 0.5, -0.6 * WING_SPAN * 0.1))
        crack(f"Wings_{sgn}_Crack_{k}", [a + Vector((0, 0, 0.03)), (a + b) / 2 + Vector((0, 0.25, 0.04)), b + Vector((0, 0, 0.03))],
              0.1 + 0.02 * SC, wings_root, (0, 0, 1))
    for k in range(WING_FINGERS):
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.7, WING_BONE * 1.2, WING_SPAN * 0.12, tips[k], tips[k] - wrist,
              M_BLACK_ROCK, wings_root)
    shard(f"Wings_{sgn}_WristSpike", WING_BONE * 1.8, WING_BONE * 1.3, WING_SPAN * 0.15, wrist, (sgn * 0.5, 0.2, 1),
          M_BLACK_ROCK, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques cendre, crête noire, fissures, pointes finales
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_ASH, tail_root)
    shard(f"Tail_Crest_{i}", 0.8 * r + 0.2, 0.12 * SC, 0.45 * SC + r * 0.8, mid + d * r * 0.85, d + t * 0.7,
          pick(SPIKES), tail_root, up=(1, 0, 0))
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_DARK]), tail_root, up=(sgn, 0, 0))
    if i % 2 == 1 and s < 0.85:
        sg = 1 if (i // 2) % 2 == 0 else -1
        B(f"Tail_Crack_{i}", (0.09 * SC + 0.03, Ln * 0.9, r * 0.55), mid + side * sg * (r + 0.005) - d * r * 0.1,
          R @ Euler((0, math.radians(12 * sg), 0)).to_matrix(), M_GLOW, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_ROCK2, tail_root)
for k, (a_, b_) in enumerate(((0, 0.9), (1, 0.55), (-1, 0.55))):
    shard(f"Tail_TipSpike_{k}", 0.55 * SC, 0.14 * SC, TAIL_TIP * b_, tip, tt_ * 0.9 + ts_ * a_ * 0.5 + td_ * 0.25,
          M_BLACK_ROCK, tail_root, up=tuple(td_))
crystal("Tail_TipEmber", 0.22 * SC, 0.25 * SC, 0.35 * SC, tip + tt_ * 0.1 * SC, tt_ + td_ * 0.5, M_GLOW, tail_root, up=tuple(td_), sides=4)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, 1 signe fort (fissures de lave), émission très faible (yeux, fissures).
#     Seuls éléments flottants : quelques braises orange et flocons de cendre grise qui montent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        mat = M_EMBER if k % 2 == 0 else M_ASH2
        sz = FX_SIZE * random.uniform(0.6, 1.1) * (0.8 if k % 2 == 0 else 1.0)
        pts = [p, p + Vector((0.5 * sz, 0.45 * sz, 0.2 * sz)), p + Vector((0.2 * sz, 0.9 * sz, 0.4 * sz)),
               p + Vector((-0.3 * sz, 0.45 * sz, 0.2 * sz))]
        plate(f"FX_Ember_{k}", pts, 0.05 * SC, mat, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
