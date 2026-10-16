import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Sirocco · Ado
#  Rare · Feu · Amphiptère · monde 2
#  - Ado : serpent dressé en S plus long, ailes moyennes en flammes, 2 petits crocs par côté, yeux plus sérieux
#  - Signe distinctif : volutes dorées (tourbillons de vent chaud) sur le corps, ailes aux bords découpés en flammes,
#    longues cornes brunes ramifiées recourbées vers l'arrière
#  - Collerette de flammes autour de la tête et du cou, ventre orange en plaques, 3 crocs par côté
#  - Rare : motif secondaire (volutes), cornes à 2 branches, crête double (flammes + plaques rouges), accent lumineux discret
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(2202)            # même dragon à chaque exécution
TAG = "SIROCCO_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
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
#    Rouge-orange (corps), orange doré (ventre), brun (cornes), or métallique (volutes, pointes),
#    flammes rouge / orange / jaune. Rare : accent lumineux discret (yeux, flammes jaunes ; strength <= 1.5).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#D24A2E", 0.50)   # corps principal, rouge-orange
M_BODY2 = get_mat("BodyDark",  "#A02F20", 0.55)   # segments alternés, plaques rouges de la crête
M_BODYL = get_mat("BodyLight", "#E8693A", 0.45)   # arête du museau, éclats clairs
M_DARK  = get_mat("Mouth",     "#5C1F14", 0.65)   # bouche, narines, anneaux de jointure
M_BELLY = get_mat("Belly",     "#F9A93A", 0.50)   # ventre en plaques, mâchoire, plastron
M_HORN  = get_mat("Horn",      "#6A4026", 0.60)   # cornes brunes
M_GOLD  = get_mat("Gold",      "#E3AA3C", 0.35, metallic=0.7)   # volutes, pointes de corne (métal)
M_F1    = get_mat("FlameRed",  "#DC3A1E", 0.45)   # flammes rouges
M_F2    = get_mat("FlameOrange", "#F58A1E", 0.45) # flammes orange
M_F3    = get_mat("FlameYellow", "#FFC93A", 0.40, emission="#FFB02E", strength=1.2)   # flammes jaunes, accent lumineux
M_BONE  = get_mat("WingBone",  "#7A1E16", 0.55)   # os des ailes
M_MEMB  = get_mat("Membrane",  "#F26A2C", 0.55)   # membrane des ailes
M_CLAW  = get_mat("Claw",      "#F2E4C8", 0.35)   # crocs, griffe du pouce
M_WHITE = get_mat("EyeWhite",  "#F4F1E8", 0.30)
M_IRIS  = get_mat("Iris",      "#F0B030", 0.25, emission="#F0B030", strength=1.2)   # iris doré, lueur discrète
M_BLACK = get_mat("Black",     "#0C0807", 0.30)
FIRE = [M_F1, M_F2, M_F3, M_F2]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADO"
ZB = 2.9
NECK_H = 5.4
COIL_R = 2.1
TAIL_UP = 0.85
RK = 1.08
BODY_STEP = 0.9
HEAD_SCALE = 1.3
SNOUT_K = 0.85
FANGS = 2
CHEEK_N = 2
BEARD_N = 3
MANE_RINGS = 2
MANE_N = 9
HORN_K = 0.8
HORN_BEAM = 4
HORN_TINES = 2
FLAME_K = 0.9
FLAME_FROM = 0.09
FLAME_TO = 0.72
BIB_N = 5
SHOULDER_FLAMES = 3
VOLUTES = 8
CREST_PLATES = True
GROUND_FLAMES = 5
WING_SPAN = 6.8
WING_LIFT = 0.75
WING_SWEEP = 0.45
WING_FINGERS = 4
WING_FLAMES = 3
WING_BONE = 0.17
TAIL_FLAME = 2.3
FX_N = 10
FX_SIZE = 0.8

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
HS = HEAD_SCALE
LK = FLAME_K

def build_ctrl():
    pts = []
    for f, y in ((1.0, -0.30), (0.86, 0.10), (0.62, 0.50), (0.38, 0.45), (0.15, -0.10), (0.0, -0.55)):
        pts.append(Vector((0, y, ZB + NECK_H * f)))
    pts.append(Vector((0, -0.60, ZB * 0.55 + 0.9)))
    pts.append(Vector((0, -0.25, 1.6)))
    pts.append(Vector((0.05, 0.75, 0.3)))
    cy = 0.8 + COIL_R * 1.55
    for k in range(1, 7):
        th = math.radians(55 * k)
        R = COIL_R * (1.0 - 0.45 * (k / 6.0))
        pts.append(Vector((R * math.sin(th) * 1.05, cy - R * math.cos(th), 0.3)))
    pts.append(Vector((-0.25 * COIL_R, cy - 0.25 * COIL_R, 0.9)))
    pts.append(Vector((0.05 * COIL_R, cy + 0.05 * COIL_R, 2.0 * TAIL_UP)))
    pts.append(Vector((0.25 * COIL_R, cy + 0.15 * COIL_R, 3.6 * TAIL_UP)))
    return pts
CTRL = build_ctrl()

RADIUS_KEYS = [(0.0, 0.62), (0.04, 0.74), (0.18, 0.86), (0.30, 1.08), (0.42, 1.12), (0.60, 0.98),
               (0.78, 0.62), (0.90, 0.38), (1.0, 0.16)]
RADIUS_KEYS = [(s, v * RK) for s, v in RADIUS_KEYS]
S_TAIL = 0.64
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
HEAD_PITCH = 6

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)           # pas de pattes (amphiptère) : sert aux flammes posées au sol
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, branches)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def flame(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Flamme en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def volute(name, center, e1, e2, normal, r0, parent, n=6, th=0.09):
    """Volute dorée : petite spirale de barres posée sur le flanc (plan e1/e2, normale 'normal')."""
    center, e1, e2 = Vector(center), Vector(e1), Vector(e2)
    pts = []
    for k in range(n + 1):
        a = k * 1.05
        rr = r0 * (1.0 - 0.8 * k / n)
        pts.append(center + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
    for k in range(n):
        link(f"{name}_{k}", pts[k], pts[k + 1], th, M_GOLD, parent, up=tuple(normal), extra=th * 0.5, bevel=0, depth=0.05)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne carré rouge-orange, museau, mâchoire orange, yeux dorés, cornes brunes ramifiées,
#    collerette de flammes derrière le crâne.
# ----------------------------------------------------------
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

def hflame(name, w, Ln, loc, direction, mat, up=(0, 0, 1), t=0.08):
    return flame("Head_" + name, hv(loc), direction, Ln * HS, w * HS, mat, H, up, t * HS)

def hbar(name, p1, p2, th, mat):
    return bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H)

# Crâne, museau, arête claire, plaque du front, mâchoire orange, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.5, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.04, bevel=0.08)
hbox("SnoutBridge", (0.95, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODYL)
hbox("SnoutTop", (1.25, 0.7 * SNOUT_K + 0.3, 0.1), (0, -0.2, 0.86), mat=M_BODY2)
hbox("Jaw", (1.3, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY)
hbox("MouthLine", (1.53, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.22, 0.06), (sgn * 0.38, SNOUT_FRONT + 0.25, 0.2), mat=M_DARK)
    # petite perle dorée sur le museau (accent métal)
    hbox(f"SnoutGold_{sgn}", (0.2, 0.28, 0.07), (sgn * 0.62, SNOUT_FRONT + 0.6, 0.2), mat=M_GOLD)

# Yeux : blanc, iris doré lumineux, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte)
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
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.22), (sgn * 0.95, ey - 0.05, ez + 0.55), rot=(14, 0, 0),
             mat=M_HORN, bevel=0.02)

# Crocs (ado : 2 petits par côté ; adulte : 3 par côté)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.28 + 0.1 * FANGS / 3, (sgn * 0.68, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles-flammes, flammes de joue et barbe de flammes sous le menton
for sgn in (-1, 1):
    hflame(f"Ear_{sgn}", 0.7, 1.3, (sgn * 0.85, 0.5, 0.3), (sgn * 1, 0.6, 0.5), M_F2, up=(0, 0, 1))
    for k in range(CHEEK_N):
        hflame(f"Cheek_{sgn}_{k}", 0.5, 0.9 - 0.1 * k, (sgn * 0.9, -0.3 + k * 0.32, -0.4 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick(FIRE, [3, 4, 2, 1]), up=(sgn, 0, 0))
for k in range(BEARD_N):
    x = (k - (BEARD_N - 1) / 2) * 0.32
    hflame(f"Beard_{k}", 0.42, 0.95 - 0.1 * abs(x), (x, SNOUT_FRONT * 0.45, -0.88), (x * 0.3, 0.35, -1),
           pick([M_F2, M_F1, M_F3]), up=(1, 0, 0))

# Collerette de flammes derrière le crâne (se prolonge le long du cou)
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / max(1, cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hflame(f"Mane_{ring_i}_{k}", 0.75 - ring_i * 0.1, 1.2 + ring_i * 0.2 + random.random() * 0.3,
               loc, direction, FIRE[(k + ring_i) % 4], up=tuple(rad))

# SIGNE DISTINCTIF : longues cornes brunes recourbées vers l'arrière, ramifiées (2 branches), pointes dorées
#   bébé : 1 corne courte et fine ; ado : cornes ramifiées moyennes ; adulte : grandes cornes à 2 branches
AK = HORN_K
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.5, 0.5, 0.35), (sgn * 0.55, 0.25, 0.78), mat=M_HORN)
    a0 = Vector((sgn * 0.55, 0.25, 0.85))
    a1 = Vector((sgn * 0.85, 0.75, 0.85 + 0.9 * AK))
    a2 = Vector((sgn * 1.15, 1.5, 0.85 + 1.5 * AK))
    a3 = Vector((sgn * 1.05, 2.4, 0.85 + 1.6 * AK))
    pts = [a0, a1, a2, a3][:HORN_BEAM]
    tchain(f"Head_Horn_{sgn}", [hv(p) for p in pts], 0.34 * HS, 0.15 * HS, M_HORN, H)
    last = pts[-1]
    hshard(f"HornGold_{sgn}", 0.2, 0.2, 0.55 * AK, last, (0, 1, 0.25), M_GOLD)
    tines = [(0.55, (sgn * 0.7, 0.15, 0.95)), (0.8, (sgn * 0.4, 0.9, 0.3))][:HORN_TINES]
    for k, (f, off) in enumerate(tines):
        base = a1.lerp(pts[-1] if HORN_BEAM >= 3 else a2, f)
        tip = base + Vector(off) * AK * 0.9
        hbar(f"Horn_{sgn}_Tine{k}", base, tip, 0.2 - 0.03 * k, M_HORN)
        hshard(f"HornTineGold_{sgn}_{k}", 0.15, 0.15, 0.4 * AK, tip, tip - base, M_GOLD)

# Crête de flammes sur le front (3 flammes : rouge, orange, jaune)
for k in range(3):
    hflame(f"Crest_{k}", 0.55, 0.9 + 0.3 * (k == 1), (0, -0.2 + 0.2 * k, 0.8), (0, 0.3 + 0.1 * k, 1.0),
           (M_F1, M_F3, M_F2)[k], up=(0, 1, 0), t=0.07)

# ----------------------------------------------------------
# 10. CORPS : segments rouges, ventre en plaques, plaques de crête, flammes, volutes dorées
# ----------------------------------------------------------
def flame_dir(t, d, side, sgn, k=0.5):
    return t * 0.9 + side * sgn * k - d * 0.1

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
        B(f"{tag}_Joint_{i}", (2.06 * r, 0.12, 1.96 * r), p1, R, M_DARK, parent)
    # Plaques de ventre orange bien séparées
    if s < 0.84:
        B(f"{tag}_Belly_{i}", (1.55 * r, Ln * 0.80, 0.26 * r + 0.06), mid - d * (r * 0.93), R, M_BELLY, parent)
    # Crête double : petites plaques rouges sur le dos (un segment sur deux) + flammes (l'autre)
    if CREST_PLATES and 0.1 < s < 0.78 and i % 2 == 1:
        B(f"{tag}_Plate_{i}", (1.1 * r, Ln * 0.85, 0.2 * r + 0.05), mid + d * (r * 0.92),
          R @ Euler((math.radians(-6), 0, 0)).to_matrix(), M_BONE if (i // 2) % 2 == 0 else M_BODY2, parent)
    if i % 2 == 0 and 0.03 < s < 0.9:
        flame(f"{tag}_Crest_{i}", mid + d * r * 0.9, d * 0.9 + t * 0.8, (0.9 + 0.5 * r) * LK, 0.7 * LK,
              FIRE[(i // 2) % 4], parent, up=tuple(side), t=0.09 * LK)
    # Flammes sur les flancs (pointe vers la queue), plus nombreuses sur la poitrine et les épaules
    if FLAME_FROM < s < FLAME_TO:
        dense = 1.0 if (s < 0.34) else 0.8
        for sgn in (-1, 1):
            if random.random() < dense:
                flame(f"{tag}_FlankFlame_{i}_{sgn}", mid + side * sgn * r * 0.9 - d * 0.15 * r,
                      flame_dir(t, d, side, sgn, 0.55), (1.1 + 0.5 * dense) * LK * (0.8 + 0.5 * r),
                      0.75 * LK, pick(FIRE, [3, 4, 2, 1]), parent, up=tuple(side * sgn + d * 0.3), t=0.09 * LK)

# Volutes dorées (tourbillons de vent chaud) sur les flancs : motif secondaire
vi = 0
for i in range(N):
    s = (i + 0.5) / N
    if s < 0.1 or s > 0.78 or i % 2 == 1 or vi >= VOLUTES * 2:
        continue
    t, d, side = FR[i]
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    r = radius(s)
    for sgn in (-1, 1):
        nrm = side * sgn
        c = mid + nrm * (r * 1.0 + 0.04) - d * (0.05 * r)
        volute(f"{'Body' if s < S_TAIL else 'Tail'}_Volute_{i}_{sgn}", c, t * (1 if sgn > 0 else -1), d, nrm, 0.7 * r,
               body_root if s < S_TAIL else tail_root, th=0.1)
        vi += 1

# Plastron orange et bavoir de flammes sur la poitrine
cmid, ct, cd, cside, cr = frame_at(S_WING + 0.05)
CR = seg_matrix(ct, cd, cside)
B("Body_Plastron", (1.7 * cr, 1.5, 0.3), cmid - cd * (cr + 0.04), CR, M_BELLY, body_root)
for k in range(BIB_N):
    amt = (k - (BIB_N - 1) / 2) * 0.55
    flame(f"Body_Bib_{k}", cmid - cd * cr * 0.9 + cside * amt * cr * 0.8 + ct * 0.4, -cd * 0.5 + ct * 0.7 - Vector((0, 0, 0.5)),
          (1.3 - 0.15 * abs(amt)) * LK * 1.1, 0.8 * LK, FIRE[k % 4], body_root, up=tuple(-cd), t=0.1 * LK)

# Épaulières de flammes + plaque rouge à la base de chaque aile
for sgn in (-1, 1):
    for k in range(SHOULDER_FLAMES):
        flame(f"Body_ShoulderFlame_{sgn}_{k}", cmid + cside * sgn * cr * 0.9 + cd * (0.3 - 0.2 * k) * cr + ct * (-0.4 + 0.3 * k),
              cside * sgn * (0.9 + 0.1 * k) + ct * (0.5 + 0.3 * k) + cd * (0.3 - 0.3 * k), (1.2 - 0.12 * k) * LK, 0.75 * LK,
              FIRE[(k + 1) % 4], body_root, up=tuple(cd), t=0.1 * LK)
    wedge(f"Body_ShoulderPlate_{sgn}", (0.9 * cr, 1.5, 0.45), cmid + cside * sgn * cr * 0.55 + cd * cr * 0.85, seg_matrix(ct, cd, cside),
          M_BONE, body_root, top_x=0.8, top_y=0.8, bevel=0.05)

# Flammes posées au sol autour des anneaux (parentées à LEGS_ROOT)
for k in range(GROUND_FLAMES):
    a = k * 2 * math.pi / GROUND_FLAMES + 0.4
    base = Vector((math.sin(a) * COIL_R * 1.0, 0.8 + COIL_R * 1.55 - math.cos(a) * COIL_R * 1.0, 0.1))
    base += Vector((math.sin(a), -math.cos(a), 0)) * RK * 0.9
    for j in range(2):
        flame(f"Legs_Ember_{k}_{j}", base, Vector((math.sin(a) * (0.6 + j * 0.5), -math.cos(a) * (0.6 + j * 0.5), 0.9 + 0.3 * j)),
              0.9 * LK, 0.5 * LK, FIRE[(k + j) % 4], legs_root, up=(0, 0, 1), t=0.07 * LK)

# ----------------------------------------------------------
# 11. PATTES : aucune (amphiptère, corps de serpent). LEGS_ROOT ne porte que les flammes posées au sol (section 10).
# ----------------------------------------------------------

# ----------------------------------------------------------
# 12. AILES EN FLAMMES : os (bras, avant-bras, doigts) de la fonction wing() + membrane rouge-orange,
#     puis franges de flammes rouge / orange / jaune qui prolongent chaque doigt et chaque bord
# ----------------------------------------------------------
def fire_wing(sgn, root):
    span = WING_SPAN
    wrist = wing(f"Wings_{sgn}", root, sgn, span, M_BONE, M_MEMB, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=0.3, memb_t=0.06, claw_mat=M_CLAW, bevel=0.0)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tips.append(wrist + Vector((sgn * span * (0.38 - 0.18 * f), span * (0.15 + 0.55 * f), -span * (0.05 + 0.3 * f))))
    # normale du plan de l'aile : toutes les flammes de l'aile sont posées dans ce plan
    n = (wrist - root).cross(tips[-1] - wrist).normalized()
    for k, tip in enumerate(tips):
        v = tip - wrist
        for L in range(WING_FLAMES):
            fl = span * (0.4 - 0.07 * L)
            dv = v.normalized() + Vector((sgn * 0.25 * L, 0.3, 0.1 + 0.1 * L))
            dv = dv - n * dv.dot(n)
            flame(f"Wings_{sgn}_Fl_{k}_{L}", tip.lerp(wrist, 0.06 * L) + n * 0.05 * L, dv, fl, span * (0.26 - 0.04 * L),
                  (M_F1, M_F2, M_F3, M_F2)[L % 4], wings_root, up=tuple(n), t=0.07)
        # flammes entre deux doigts, sur le bord de la membrane (2 rangées vers l'intérieur)
        if k < len(tips) - 1:
            for row in range(2):
                mid = tip.lerp(tips[k + 1], 0.5).lerp(wrist, 0.05 + 0.4 * row)
                dv = (tip.lerp(tips[k + 1], 0.5) - wrist).normalized() + Vector((0, 0.3, 0.1))
                dv = dv - n * dv.dot(n)
                flame(f"Wings_{sgn}_Edge_{k}_{row}", mid + n * 0.07, dv, span * (0.34 - 0.08 * row), span * (0.22 - 0.04 * row),
                      FIRE[(k + row + 1) % 4], wings_root, up=tuple(n), t=0.07)
    # frange de flammes sur le bras (bord d'attaque)
    for k in range(2):
        a = root.lerp(wrist, 0.35 + 0.3 * k)
        flame(f"Wings_{sgn}_Lead_{k}", a, Vector((sgn * 0.3, -0.3, 1.0)), span * 0.16, span * 0.08, M_F2, wings_root,
              up=(0, 1, 0), t=0.06)

wmid, wt, wd, wside, wr = frame_at(S_WING)
for sgn in (-1, 1):
    fire_wing(sgn, wmid + wd * wr * 0.8 + wside * sgn * wr * 0.55)

# ----------------------------------------------------------
# 13. QUEUE : fait partie de la même courbe (s > S_TAIL) ; bout = anneau d'or + panache de flammes
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = FR[-1]
B("Tail_TipRing", (0.6 * RK, 0.32, 0.6 * RK), tip, seg_matrix(tt_, td_, ts_), M_GOLD, tail_root)
flame("Tail_TipFlame_A", tip, tt_ + td_ * 0.3, TAIL_FLAME, TAIL_FLAME * 0.5, M_F1, tail_root, up=tuple(ts_), t=0.12 * LK)
flame("Tail_TipFlame_B", tip, tt_ + td_ * 0.3, TAIL_FLAME * 0.82, TAIL_FLAME * 0.42, M_F2, tail_root, up=tuple(td_), t=0.12 * LK)
flame("Tail_TipFlame_C", tip, tt_ + td_ * 0.2 + ts_ * 0.4, TAIL_FLAME * 0.6, TAIL_FLAME * 0.32, M_F3, tail_root, up=tuple(td_), t=0.1 * LK)
flame("Tail_TipFlame_D", tip, tt_ + td_ * 0.2 - ts_ * 0.4, TAIL_FLAME * 0.6, TAIL_FLAME * 0.32, M_F3, tail_root, up=tuple(td_), t=0.1 * LK)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (volutes dorées), cornes à 2 branches avec pointes dorées, crête double (flammes + plaques),
#     accent lumineux discret (iris et flammes jaunes, strength 1.2). Braises en losange qui montent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 3.2
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.6 + 2.0), random.uniform(-2.5, 3.0 + COIL_R * 2.5),
                    random.uniform(1.0, top_z)))
        dirv = Vector([random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 1.0])
        flame(f"FX_Ember_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.45, FIRE[k % 3],
              master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
