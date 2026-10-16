import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Escarbille · Bébé
#  Rare · Feu · Drake · monde 2
#  - Bébé trapu et arrondi : très grosse tête, museau court, pattes courtes et épaisses, pas de crocs
#  - Signe distinctif : écailles hexagonales de roche noire, fissures de lave lumineuses, grande crinière de flammes en cristal derrière la tête
#  - Crête double : plaques rouges le long de l'échine + rangée de flammes orange entre elles, cristal-corne sur le museau
#  - Rare : motif secondaire (hexagones et fissures), cornes à 2 pointes, accent lumineux discret (yeux, fissures, flammes)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(2201)            # même dragon à chaque exécution
TAG = "ESCARBILLE_BEBE"      # préfixe de tous les objets, matériaux et de la collection
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
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Charbon (corps), roche olive (armure, épaules), orange (ventre, mâchoire), rouge vif (crête, cornes),
#    flammes orange en cristal. Rare : accent lumineux discret (yeux, fissures, flammes ; strength <= 1.5).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#5C4D40", 0.55)   # corps principal, charbon chaud
M_BODY2 = get_mat("BodyScale", "#80674B", 0.60)   # hexagones clairs, dessus du museau
M_DARK  = get_mat("BodyDark",  "#1B1513", 0.65)   # bouche, narines, ombres, genoux
M_STONE = get_mat("Stone",     "#84805A", 0.80)   # roche olive de l'armure (épaules, gantelets)
M_STONE2= get_mat("StoneDark", "#57533A", 0.85)   # roche sombre
M_BELLY = get_mat("Belly",     "#F0872B", 0.50)   # ventre en plaques, plastron, mâchoire
M_FOOT  = get_mat("Foot",      "#7A5B3C", 0.60)   # pieds en blocs brun clair
M_RED   = get_mat("Crest",     "#D02A1C", 0.45)   # plaques rouges de la crête, base des cornes
M_RED2  = get_mat("CrestDark", "#8E1D16", 0.50)   # rouge sombre (cornes, sourcils)
M_TIP   = get_mat("HornTip",   "#FFB02E", 0.40)   # pointes des cornes
M_FLAME = get_mat("Flame",     "#FF9A1F", 0.35, emission="#FF7A10", strength=1.4)   # flammes en cristal
M_FLAME2= get_mat("FlameHot",  "#FFC24A", 0.35, emission="#FFB02E", strength=1.4)   # flammes claires
M_CLAW  = get_mat("Claw",      "#F4E7CF", 0.35)   # griffes et crocs
M_WHITE = get_mat("EyeWhite",  "#F4F1E8", 0.30)
M_IRIS  = get_mat("Iris",      "#F07A12", 0.25, emission="#F07A12", strength=1.2)   # iris orange, lueur discrète
M_BLACK = get_mat("Black",     "#0C0907", 0.30)   # pupilles, narines
M_LAVA  = get_mat("Lava",      "#FFB02E", 0.40, emission="#FF7A10", strength=1.5)   # fissures de lave
STONES = [M_STONE, M_STONE2, M_STONE, M_BODY2]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "BEBE"
BW = 2.5
BH = 1.8
LEG_H = 1.3
TORSO_L = 3.3
NECK_L = 0.8
NECK_LEAN = 0.15
NECK_N = 1
NECK_R = (0.85, 0.95)
HEAD_SCALE = 1.0
SNOUT_K = 0.6
FANGS = 0
HORN_K = 0.5
MANE_N = 3
MANE_K = 0.55
SNOUT_HORN = 0.35
HEAD_ROCKS = 1
CHEEK_N = 1
BEARD = 0
BELLY_N = 4
BELLY_SIDES = False
HEX_ROWS = 1
HEX_COLS = 4
CREST_N = 4
FLAME_ROW = True
SHOULDER_K = 0.55
SHOULDER_ROCKS = 1
NAPE_ROCKS = False
BRACER_K = 0.4
LEG_BEV = 0
KNEE = False
GAUNTLET = False
LEG_CRACKS = 0
CRACKS = 1
TAIL_L = 3.0
TAIL_STEP = 0.55
TAIL_BEV_N = 2
TAIL_FLAMES = 3
CLUB_SIZE = 0.8
FLAME_K = 0.6
SHOULDER_FLAMES = 0
FX_N = 6
FX_SIZE = 0.45

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
HEAD_PITCH = 6                                   # degrés : la tête regarde un peu vers le bas
TAIL_START = Vector((0, TL * 0.42, ZC - 0.12 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def rock(name, size, loc, mat, parent, rot=None, jit=10, tx=0.72, ty=0.78, bevel=0.0):
    """Roche taillée : bloc dont le dessus est rétréci, légèrement tourné au hasard (seed fixe)."""
    if rot is None:
        rot = (random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit * 2, jit * 2))
    return wedge(name, size, loc, rot, mat, parent, top_x=tx, top_y=ty,
                 shift_y=random.uniform(-0.12, 0.12) * size[1], bevel=bevel)

def diamond(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Plaque en losange (braise flottante)."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def hexa(name, loc, normal, r, mat, parent, h=0.07):
    """Hexagone plat de roche posé sur la peau (axe du prisme = normale de la surface)."""
    return prism(name, r, h, loc, normal, mat, parent, sides=6, up=(0, 0, 1))

def crack(name, origin, e1, e2, normal, steps, step_len, heading, parent, th=0.15, mat=None, lim=None):
    """Fissure de lave : marche aléatoire en zigzag sur une face (plan e1/e2), posée sur la surface.
    heading = angle de départ (degrés) dans le plan ; une petite branche part au milieu.
    lim = (u_min, u_max, v_min, v_max) : la fissure reste dans ce rectangle autour de 'origin'."""
    mat = mat or M_LAVA
    e1, e2, normal = Vector(e1), Vector(e2), Vector(normal)
    o = Vector(origin)
    def inside(q):
        if lim is None:
            return True
        u, v = (q - o).dot(e1), (q - o).dot(e2)
        return lim[0] <= u <= lim[1] and lim[2] <= v <= lim[3]
    def walk(p, ang, n, tag, thick):
        pts = [p]
        for _ in range(n):
            ang += random.uniform(-55, 55)
            ln = step_len * random.uniform(0.7, 1.2)
            for _try in range(4):
                a = math.radians(ang)
                q = p + (e1 * math.cos(a) + e2 * math.sin(a)) * ln
                if inside(q):
                    break
                ang += 90
            else:
                break
            p = q
            pts.append(p)
        for i in range(len(pts) - 1):
            link(f"{name}_{tag}{i}", pts[i], pts[i + 1], thick * SC, mat, parent, up=tuple(normal),
                 extra=thick * SC * 0.6, bevel=0, depth=0.05 * SC)
        return pts
    main = walk(Vector(origin), heading, steps, "m", th)
    if steps >= 3:
        walk(main[len(main) // 2], heading + random.choice((-70, 70)), max(1, steps // 2), "b", th * 0.8)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne carré charbon, museau large, mâchoire orange, cristal-corne sur le museau, sourcils rouges,
#    cornes rouges à 2 pointes, crinière de flammes en cristal derrière le crâne.
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

def hrock(name, size, loc, mat, rot=None, jit=12, tx=0.72, ty=0.78):
    return rock("Head_" + name, hv(size), hv(loc), mat, H, rot, jit, tx, ty)

# Crâne, museau large, plaque du dessus, arête, mâchoire orange + menton, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.75, 2.1 * SNOUT_K, 1.0), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.06, bevel=0.08)
hbox("SnoutTop", (1.6, 1.9 * SNOUT_K, 0.16), (0, -0.6 - 1.0 * SNOUT_K, 0.27), mat=M_BODY2, bevel=0.03)
hbox("SnoutBridge", (0.7, 1.2 * SNOUT_K, 0.1), (0, -0.6 - 0.8 * SNOUT_K, 0.37), mat=M_STONE2)
hbox("Jaw", (1.55, 1.95 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY, bevel=0.04)
hbox("Chin", (1.7, 0.4, 0.4), (0, -0.55 - 2.0 * SNOUT_K - 0.08, -0.74), mat=M_BELLY, bevel=0.04)
hbox("MouthLine", (1.8, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.26, 0.24, 0.07), (sgn * 0.5, SNOUT_FRONT + 0.25, 0.36), mat=M_BLACK)

# Cristal-corne orange sur le bout du museau (signe distinctif de l'image : une flamme en cristal)
if SNOUT_HORN > 0:
    k_ = SNOUT_HORN
    hbox("HornBase", (0.8 * k_, 0.8 * k_, 0.2), (0, SNOUT_FRONT + 0.7 * k_, 0.4), mat=M_RED)
    hshard("SnoutCrystal", 0.62 * k_, 0.55 * k_, 1.15 * k_, (0, SNOUT_FRONT + 0.7 * k_, 0.45), (0, -0.25, 1), M_FLAME2, up=(0, 1, 0))

# Yeux : blanc, iris, pupille (ronde + reflets pour bébé, fendue pour ado / adulte) + sourcils rouges
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.9, 0.98, 0.7, 0.82, 0.42, 0.58
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.64, 0.42, 0.54, 0.1, 0.5
for sgn in (-1, 1):
    ey, ez = -0.3, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.07, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.11, 0.11), (sgn * 1.07, ey + 0.13, ez - 0.22), mat=M_WHITE)
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.14), (sgn * 0.96, ey - 0.02, ez + 0.6), mat=M_BODY2)
    else:
        hbox(f"Brow_{sgn}", (0.22, 1.0, 0.28), (sgn * 0.97, ey - 0.05, ez + 0.54), rot=(14, 0, 0),
             mat=M_RED2, bevel=0.02)

# Crocs : ado 2 par côté (petits), adulte 3 par côté (plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.72, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Cornes rouges à 2 pointes (grande corne vers l'arrière + petite pointe orange) et corne de joue
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.55, 0.55, 0.4), (sgn * 0.6, 0.15, 0.82), mat=M_RED2)
    hshard(f"Horn_{sgn}", 0.55, 0.5, 1.7 * HORN_K, (sgn * 0.6, 0.15, 0.95), (sgn * 0.45, 0.8, 0.75), M_RED)
    hshard(f"HornTine_{sgn}", 0.34, 0.3, 0.95 * HORN_K, (sgn * 0.6, 0.05, 0.98), (sgn * 0.9, 0.1, 0.9), M_TIP)
    if not IS_BEBE:
        hshard(f"CheekHorn_{sgn}", 0.45, 0.28, 0.9 + 0.3 * IS_ADULTE, (sgn * 0.88, 0.45, -0.25),
               (sgn * 0.8, 0.9, -0.1), M_RED2)

# Crinière de flammes en cristal derrière le crâne : éventail de grandes flammes orange (signe distinctif)
for k in range(MANE_N):
    f = k / max(1, MANE_N - 1)
    sgn = -1 if k % 2 == 0 else 1
    lvl = k // 2
    x = sgn * (0.12 + 0.2 * lvl)
    ang = sgn * (0.15 + 0.22 * lvl)
    Ln = (2.2 - 0.3 * lvl) * MANE_K
    hshard(f"Mane_{k}", 0.78 - 0.06 * lvl, 0.32, Ln, (x, 0.5 + 0.12 * lvl, 0.75 - 0.08 * lvl),
           (ang, 0.7 + 0.1 * lvl, 1.0 - 0.1 * lvl), M_FLAME if k % 3 else M_FLAME2, up=(0, 1, 0))
# Base de la crinière : plaques rouges sous les flammes
for sgn in (-1, 1):
    hrock(f"ManeBase_{sgn}", (0.8, 0.7, 0.5), (sgn * 0.45, 0.55, 0.85), M_RED, jit=6)
hrock("ManeBaseC", (0.9, 0.7, 0.5), (0, 0.6, 0.9), M_RED2, jit=4)

# Roches : joues sombres, barbe de roche sous la mâchoire
for k in range(HEAD_ROCKS):
    hrock(f"FrontRock_{k}", (0.5, 0.5, 0.3), ((-0.4 + 0.4 * k) * (1 if HEAD_ROCKS > 1 else 0), -0.1, 0.9), STONES[k % 4])
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hrock(f"Cheek_{sgn}_{k}", (0.42, 0.45 + 0.1 * k, 0.32), (sgn * 0.97, -0.1 + 0.42 * k, -0.4 + 0.2 * (k % 2)),
              STONES[(k + 1) % 4], rot=(0, sgn * 82, random.uniform(-15, 15)), jit=0)
if BEARD:
    for k in range(BEARD):
        sgn = -1 if k % 2 == 0 else 1
        hrock(f"Beard_{k}", (0.5, 0.55, 0.5), (sgn * (0.25 + 0.2 * (k // 2)), 0.1 + 0.4 * (k // 2), -1.0), STONES[(k + 1) % 2 + 1])

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, plastron orange, ventre en plaques, hexagones de roche, crête double, cou
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron orange + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_BELLY, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_BELLY, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_BELLY, parent=body_root)

# Hexagones de roche noire en quinconce sur les flancs (motif secondaire de la rareté Rare)
for sgn in (-1, 1):
    for r in range(HEX_ROWS):
        for c in range(HEX_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / HEX_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            hexa(f"Body_Hex_{sgn}_{r}_{c}", (sgn * (half_w(y) + 0.03 * SC), y, z), (sgn, 0, 0), BH * random.uniform(0.1, 0.13),
                 pick([M_BODY2, M_STONE2, M_BODY2, M_DARK]), body_root)

# Crête double : plaques rouges taillées sur l'échine + flammes orange entre les plaques
for k in range(CREST_N):
    f = k / max(1, CREST_N - 1)
    y = -TL * 0.38 + (TL * 0.82) * f
    w = BW * (0.5 - 0.1 * abs(f - 0.3))
    rock(f"Body_Plate_{k}", (w, TL * 0.9 / CREST_N * 1.05, 0.5 * SC + 0.1 * BH * (1 - f)),
         (random.uniform(-0.04, 0.04) * BW, y, ZC + BH / 2 + 0.06 * BH),
         M_RED if k % 2 == 0 else M_RED2, body_root, rot=(random.uniform(-4, 4), 0, random.uniform(-6, 6)), tx=0.7, ty=0.85, bevel=0.03 * SC)
    if FLAME_ROW:
        yy = y + (TL * 0.82) / max(1, CREST_N - 1) * 0.5
        if k < CREST_N - 1:
            shard(f"Body_Flame_{k}", 0.7 * SC * FLAME_K, 0.4 * SC * FLAME_K, (1.5 - 0.5 * f) * SC * FLAME_K,
                  (0, yy, ZC + BH / 2 + 0.2 * BH), (0, 0.55, 1.0), M_FLAME if k % 2 else M_FLAME2, body_root, up=(1, 0, 0))

# Roches d'épaule olive : grappes de blocs (grosses pierres à l'adulte)
for sgn in (-1, 1):
    for k in range(SHOULDER_ROCKS):
        f = k / max(1, SHOULDER_ROCKS - 1)
        s = BW * (0.46 - 0.2 * f) * SHOULDER_K
        rock(f"Body_Shoulder_{sgn}_{k}", (s, s * 1.1, s * 0.8),
             (sgn * BW * (0.46 + 0.07 * f), -TL * (0.22 - 0.14 * f), ZC + BH * (0.42 - 0.2 * f)),
             STONES[(k + 1) % 3], body_root, jit=14, bevel=0.03 * SC if k == 0 else 0)

# Cristaux de flamme sur les épaules (accent lumineux, 2 par côté à l'adulte)
for sgn in (-1, 1):
    for k in range(SHOULDER_FLAMES):
        shard(f"Body_ShoulderFlame_{sgn}_{k}", 0.55 * SC, 0.4 * SC, (1.5 - 0.3 * k) * SC * FLAME_K,
              (sgn * BW * (0.5 + 0.04 * k), -TL * (0.2 - 0.12 * k), ZC + BH * (0.62 - 0.1 * k)),
              (sgn * 0.5, 0.15, 1.0), M_FLAME2 if k % 2 else M_FLAME, body_root, up=(0, 1, 0))

# Cou : courbe lissée de la tête vers le torse, bloc charbon + plaque orange devant par maillon
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
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - d * (r * 0.95), R, M_BELLY, body_root)
    if NAPE_ROCKS:
        rock(f"Body_NapeRock_{i}", (r * 1.1, Ln * 0.9, r * 0.5), mid + d * r * 0.95, M_RED2 if i % 2 else M_STONE2, body_root, rot=None, jit=6)
        if s > 0.25:
            for sgn in (-1, 1):
                hexa(f"Body_NeckHex_{i}_{sgn}", mid + side * sgn * r * 0.99 + d * r * 0.15, (sgn, 0, 0), r * 0.4, M_BODY2, body_root)
        if FLAME_ROW and i < NN - 1:
            shard(f"Body_NapeFlame_{i}", r * 0.8, r * 0.4, r * 1.5 * FLAME_K, mid + d * r * 1.0, d * 0.7 + t * 0.9,
                  M_FLAME if i % 2 else M_FLAME2, body_root, up=tuple(side))

# ----------------------------------------------------------
# 11. PATTES : cuisse en wedge, gantelet de roche olive, genouillère, pied, 3 doigts + 3 griffes
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
    shin_mat = M_STONE if GAUNTLET else M_BODY2
    box(f"{name}_Shin", (th * 0.92, th * 0.97, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=shin_mat, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    bh_ = SHIN_H * BRACER_K
    rock(f"{name}_Bracer", (th * 1.1, th * 1.14, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.62), M_STONE2, legs_root,
         rot=(0, 0, random.uniform(-6, 6)), tx=0.92, ty=0.92, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.0, th * 1.04, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.62 + bh_ / 2 + 0.02),
      mat=M_RED, parent=legs_root)
    # Hexagones de roche sur la cuisse
    for k in range(2):
        hexa(f"{name}_Hex_{k}", (x + sgn * th * 0.66, y + yo + th * (-0.25 + 0.4 * k), FOOT_H + SHIN_H + thigh_h * (0.7 - 0.25 * k)),
             (sgn, 0, 0), th * 0.2, M_BODY2, legs_root)
    if CRACKS:
        crack(f"{name}_ThighCrack", (x + sgn * (th * 0.66 + 0.02), y + yo, FOOT_H + SHIN_H + thigh_h * 0.85),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 3, thigh_h * 0.2, -70, legs_root, th=0.14,
              lim=(-th * 0.5, th * 0.5, -thigh_h * 0.6, 0.0))
    if KNEE:
        rock(f"{name}_Knee", (th * 0.8, th * 0.45, th * 0.6), (x, y + yo - th * 0.62, FOOT_H + SHIN_H + 0.2 * thigh_h),
             M_STONE2, legs_root, jit=5)
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_FOOT, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY2,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    for c in range(LEG_CRACKS):
        dy = -th * 0.25 + th * 0.3 * c
        crack(f"{name}_Crack_{c}", (x + sgn * (th * 0.46 + 0.02), y + yo + dy, FOOT_H + SHIN_H * 0.95),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 3, SHIN_H * 0.24, -90 + 40 * c, legs_root, th=0.15,
              lim=(-th * 0.42 - dy, th * 0.42 - dy, -SHIN_H * 0.9, 0.0))
    if LEG_CRACKS:
        crack(f"{name}_CrackF", (x + sgn * th * 0.15, y + yo - th * 0.485 - 0.02, FOOT_H + SHIN_H * 0.95),
              (1, 0, 0), (0, 0, 1), (0, -1, 0), 3, SHIN_H * 0.24, -80, legs_root, th=0.15,
              lim=(-th * 0.6, th * 0.28, -SHIN_H * 0.9, 0.0))

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments charbon, plaques orange dessous, plaques rouges + flammes dessus,
#     touffe de flammes en cristal au bout (ornement final). Pas de section 12 : le Drake n'a pas d'ailes.
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.25, -0.35, 0.0), (0.5, -0.55, 0.25), (0.75, -0.4, 0.1), (1.0, -0.1, -0.2)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.5)))
TAIL_R = [(0.0, BW * 0.42), (0.3, BW * 0.35), (0.6, BW * 0.26), (0.85, BW * 0.2), (1.0, BW * 0.18)]
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_BELLY, tail_root)
    if i % 2 == 0 and s < 0.85:
        rock(f"Tail_Plate_{i}", (r * 1.2, Ln * 1.1, r * 0.55), mid + d * r * 0.9, M_RED if i % 4 == 0 else M_RED2, tail_root,
             rot=None, jit=5)
    if i % 2 == 1 and s < 0.85 and FLAME_ROW:
        shard(f"Tail_Flame_{i}", r * 0.9, r * 0.5, r * 1.9 * FLAME_K, mid + d * r * 0.85, d * 1.0 + t * 0.5,
              M_FLAME if i % 4 == 1 else M_FLAME2, tail_root, up=tuple(side))
    if i % 2 == 1 and s < 0.85 and not IS_BEBE:
        for sgn in (-1, 1):
            hexa(f"Tail_Hex_{i}_{sgn}", mid + side * sgn * (r * 0.99), (sgn, 0, 0), r * 0.38, M_BODY2, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
CL = CLUB_SIZE
core = tip + tt_ * CL * 0.4
rock("Tail_TipCore", (CL * 1.3, CL * 1.3, CL * 1.1), core, M_STONE, tail_root, rot=(0, 0, 0), tx=0.85, ty=0.85, bevel=0.05 * SC)
rock("Tail_TipTop", (CL * 0.9, CL * 0.9, CL * 0.5), core + Vector((0, 0, CL * 0.55)), M_RED2, tail_root, jit=8)
for k in range(TAIL_FLAMES):
    a = k * 2 * math.pi / TAIL_FLAMES + 0.5
    dv = Vector((math.cos(a) * 0.7, 0.35, 0.8 + 0.4 * math.sin(a)))
    shard(f"Tail_TipFlame_{k}", CL * 0.55, CL * 0.4, CL * (1.5 + 0.3 * (k % 2)), core + Vector((0, 0, CL * 0.5)), dv,
          M_FLAME if k % 2 else M_FLAME2, tail_root)
if CRACKS:
    for sgn in (-1, 1):
        crack(f"Tail_TipCrack_{sgn}", core + Vector((sgn * CL * 0.66, -CL * 0.25, CL * 0.1)), (0, 1, 0), (0, 0, 1), (sgn, 0, 0),
              3, CL * 0.22, -60, tail_root, th=0.15, lim=(-CL * 0.35, CL * 0.85, -CL * 0.5, CL * 0.2))

# ----------------------------------------------------------
# 10b. FISSURES DE LAVE sur les flancs (adulte)
# ----------------------------------------------------------
for sgn in (-1, 1):
    for c in range(CRACKS):
        y0 = -TL * 0.34 + c * TL * 0.22
        crack(f"Body_Crack_{sgn}_{c}", (sgn * (half_w(y0) + 0.09 * SC), y0, ZC + BH * 0.3),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 6, BH * 0.27, -80 + 35 * c, body_root, th=0.15,
              lim=(-TL * 0.16, TL * 0.16, -BH * 0.75, 0.0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (hexagones + fissures), cornes à 2 pointes, crête double (plaques rouges + flammes),
#     accent lumineux discret (yeux, fissures, flammes en cristal : strength <= 1.5).
#     Seuls éléments flottants : braises en losange qui montent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.0 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.3 + 1.0), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 1.0])
        diamond(f"FX_Ember_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.45,
                M_FLAME2 if k % 3 == 0 else (M_FLAME if k % 3 == 1 else M_RED), master,
                up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.06 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
