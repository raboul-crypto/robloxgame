import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Stalactite · Ado
#  Rare · Minéral · Drake · monde 5
#  - Ado drake plus massif et bas : cou de 3 blocs, petits crocs, sourcils de roche, plaques de pierre sur les pattes
#  - Signes distinctifs : stalagmites plus longues et effilées sur le dos, cristaux plus nombreux (front, épaules, bout de queue), barbe de stalactites
#  - Rare : strates + veines de minerai, cornes à 2 pointes, crête double, lueur discrète (yeux, cristaux, veines)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(5502)            # même dragon à chaque exécution
TAG = "STALACTITE_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
#    Gris pierre bleuté (corps), calcaire blanc-gris (stalagmites, cornes, griffes), gris clair (ventre),
#    cristaux bleu pâle translucides. Rare : accent lumineux discret (yeux, cristaux, veines ; strength <= 1.5).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#74869B", 0.65)   # corps principal, gris pierre bleuté
M_BODY2 = get_mat("BodyLight", "#92A3B5", 0.65)   # dessus du museau, pieds, blocs clairs
M_DARK  = get_mat("BodyDark",  "#4B5663", 0.75)   # bouche, narines, bases de cristaux, ombres
M_STONE = get_mat("Stone",     "#8191A4", 0.85)   # plaques de roche (épaules, jambes)
M_STONE2= get_mat("StoneDark", "#5A6676", 0.85)   # roche sombre
M_STRATA= get_mat("Strata",    "#B8C3CC", 0.70)   # strates claires sur les flancs
M_BELLY = get_mat("Belly",     "#D5D9DD", 0.55)   # ventre en plaques, plastron, mâchoire
M_LIME  = get_mat("Limestone", "#ECE8DC", 0.50)   # calcaire blanc : stalagmites, stalactites, cornes
M_LIME2 = get_mat("LimeShade", "#C9C3B1", 0.55)   # calcaire ombré (stalagmites du second rang)
M_CLAW  = get_mat("Claw",      "#E3E1DA", 0.40)   # griffes de pierre et crocs
M_CRYS  = get_mat("Crystal",   "#BFE3F2", 0.20, emission="#8FD4F0", strength=1.2, alpha=0.78)   # cristaux translucides
M_CRYS2 = get_mat("CrystalDeep","#7FC4E6", 0.20, emission="#5DB6E6", strength=1.3, alpha=0.85)  # cristaux plus profonds
M_VEIN  = get_mat("Vein",      "#A8DCF2", 0.30, emission="#8FD4F0", strength=1.4)   # veines de minerai lumineuses
M_WHITE = get_mat("EyeWhite",  "#F2F5F7", 0.30)
M_IRIS  = get_mat("Iris",      "#7FC4E6", 0.25, emission="#7FC4E6", strength=1.2)   # iris bleu pâle, lueur discrète
M_BLACK = get_mat("Black",     "#0E1216", 0.30)   # pupilles, narines
STONES = [M_STONE, M_STONE2, M_STONE, M_BODY2]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADO"
BW = 3.0
BH = 2.2
LEG_H = 1.8
TORSO_L = 4.2
NECK_L = 1.7
NECK_LEAN = 0.3
NECK_N = 3
NECK_R = (0.9, 1.1)
HEAD_SCALE = 1.1
SNOUT_K = 0.85
FANGS = 2
HORN_K = 0.75
BEARD = 3
BEARD_K = 0.85
HEAD_CRYS = 3
HEAD_ROCKS = 2
CHEEK_N = 2
BELLY_N = 5
BELLY_SIDES = True
STRATA = 2
CREST_N = 5
SLAB_ROWS = 3
SLAB_COLS = 4
CHEST_STAL = 4
DORSAL_CRYS = True
CREST_K = 0.85
SIDE_ROW = True
SHOULDER_K = 0.8
SHOULDER_ROCKS = 3
SHOULDER_CLUSTERS = 1
CLUSTER_N = 3
CLUSTER_K = 0.9
NAPE_STAL = True
ARMOR = True
BRACER_K = 0.5
LEG_BEV = 1
KNEE = True
LEG_CRACKS = 1
CRACKS = 3
TAIL_L = 4.6
TAIL_STEP = 0.75
TAIL_BEV_N = 3
TAIL_STAL_EVERY = 2
CLUB_SIZE = 1.0
TIP_STAL = 4
TIP_CRYS = 3
FX_N = 8
FX_SIZE = 0.55

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
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def rock(name, size, loc, mat, parent, rot=None, jit=10, tx=0.72, ty=0.78, bevel=0.0):
    """Roche taillée : bloc dont le dessus est rétréci, légèrement tourné au hasard (seed fixe)."""
    if rot is None:
        rot = (random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit * 2, jit * 2))
    return wedge(name, size, loc, rot, mat, parent, top_x=tx, top_y=ty,
                 shift_y=random.uniform(-0.12, 0.12) * size[1], bevel=bevel)

def stal(name, base, direction, r, length, mat, parent, up=(0, 0, 1)):
    """Pointe de calcaire taillée en facettes (stalagmite) : pied à 5 faces qui s'effile en pointe."""
    return crystal(name, r, length * 0.3, length * 0.7, base, direction, mat, parent, up=up, sides=5)

def cluster(name, base, direction, n, size, parent, mat_list=None, spread=0.55):
    """Grappe de cristaux translucides : n prismes à pointe qui partent d'un bloc sombre, en éventail."""
    mat_list = mat_list or (M_CRYS, M_CRYS2)
    base, d0 = Vector(base), Vector(direction).normalized()
    B(name + "_Base", (size * 0.9, size * 0.9, size * 0.32), base, rot=(0, 0, random.uniform(0, 90)), mat=M_DARK, parent=parent)
    for k in range(n):
        a = k * 2.4 + random.uniform(-0.3, 0.3)
        f = 0.0 if k == 0 else spread
        dv = d0 + Vector((math.cos(a) * f, math.sin(a) * f, 0.0)) * (1.0 if k else 0.0)
        L = size * (1.5 - 0.22 * k + random.uniform(-0.1, 0.1))
        crystal(f"{name}_{k}", size * (0.2 if k == 0 else 0.16), L * 0.55, L * 0.45, base + d0 * size * 0.1, dv,
                mat_list[k % 2], parent, up=(0, 1, 0), sides=6)

def crack(name, origin, e1, e2, normal, steps, step_len, heading, parent, th=0.15, mat=None, lim=None):
    """Veine de minerai lumineuse : marche aléatoire en zigzag sur une face (plan e1/e2), posée sur la surface.
    heading = angle de départ (degrés) dans le plan ; une petite branche part au milieu.
    lim = (u_min, u_max, v_min, v_max) : la veine reste dans ce rectangle autour de 'origin'."""
    mat = mat or M_VEIN
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
            ang += random.uniform(-38, 38)
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

def diamond(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Plaque en losange (éclat flottant)."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne carré gris pierre, museau, mâchoire gris clair avec barbe de stalactites, sourcils de roche,
#    cornes de calcaire à 2 pointes, grappe de cristaux sur le front.
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

hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.75, 2.1 * SNOUT_K, 1.0), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.06, bevel=0.08)
hbox("SnoutTop", (1.55, 1.9 * SNOUT_K, 0.16), (0, -0.6 - 1.0 * SNOUT_K, 0.27), mat=M_BODY2, bevel=0.03)
hbox("SnoutBridge", (0.7, 1.2 * SNOUT_K, 0.1), (0, -0.6 - 0.8 * SNOUT_K, 0.37), mat=M_LIME)
hbox("Jaw", (1.55, 1.95 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY, bevel=0.04)
hbox("Chin", (1.7, 0.4, 0.4), (0, -0.55 - 2.0 * SNOUT_K - 0.08, -0.74), mat=M_BELLY, bevel=0.04)
hbox("MouthLine", (1.8, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.26, 0.24, 0.07), (sgn * 0.5, SNOUT_FRONT + 0.25, 0.36), mat=M_BLACK)

# Yeux : blanc, iris, pupille (ronde + reflets pour bébé, fendue pour ado / adulte) + sourcils de roche
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
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.14), (sgn * 0.96, ey - 0.02, ez + 0.6), mat=M_STONE2)
    else:
        hrock(f"Brow_{sgn}", (0.3, 1.1, 0.34), (sgn * 0.97, ey - 0.05, ez + 0.54), M_STONE2, rot=(14, 0, 0), jit=0)

# Crocs : ado 2 par côté (petits), adulte 3 par côté (plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.72, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Cornes de pierre à 2 pointes (calcaire blanc) + corne de joue
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.6, 0.6, 0.4), (sgn * 0.6, 0.15, 0.82), mat=M_STONE2)
    hshard(f"Horn_{sgn}", 0.55, 0.5, 1.7 * HORN_K, (sgn * 0.6, 0.15, 0.95), (sgn * 0.4, 0.75, 0.8), M_LIME)
    hshard(f"HornTine_{sgn}", 0.34, 0.3, 0.95 * HORN_K, (sgn * 0.6, 0.05, 0.98), (sgn * 0.9, 0.1, 0.9), M_LIME2)
    if not IS_BEBE:
        hshard(f"CheekHorn_{sgn}", 0.45, 0.28, 0.9 + 0.3 * IS_ADULTE, (sgn * 0.88, 0.45, -0.25),
               (sgn * 0.8, 0.9, -0.1), M_LIME2)

# Grappe de cristaux translucides sur le front (Rare : accent lumineux discret)
if HEAD_CRYS:
    cluster("Head_Crystals", Vector(hv((0, -0.35, 0.86))), (0, -0.15, 1.0), HEAD_CRYS, 0.7 * HS, H)

# Barbe de stalactites : pointes de calcaire qui pendent sous la mâchoire et le menton
for k in range(BEARD):
    f = k / max(1, BEARD - 1)
    sgn = -1 if k % 2 == 0 else 1
    stal(f"Head_Beard_{k}", hv((sgn * (0.12 + 0.22 * (k // 2)), -0.5 - 1.7 * SNOUT_K * (1 - f * 0.75), -0.88)), (0, 0.05, -1),
         0.16 * HS, (0.95 - 0.35 * abs(f - 0.4)) * HS * BEARD_K, M_LIME if k % 2 == 0 else M_LIME2, H, up=(1, 0, 0))

# Roches : plaques du front, joues
for k in range(HEAD_ROCKS):
    hrock(f"FrontRock_{k}", (0.5, 0.5, 0.3), ((-0.4 + 0.4 * k) * (1 if HEAD_ROCKS > 1 else 0), 0.0, 0.88), STONES[k % 4])
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hrock(f"Cheek_{sgn}_{k}", (0.42, 0.45 + 0.1 * k, 0.32), (sgn * 0.97, -0.1 + 0.42 * k, -0.4 + 0.2 * (k % 2)),
              STONES[(k + 1) % 4], rot=(0, sgn * 82, random.uniform(-15, 15)), jit=0)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, plastron, ventre en plaques, strates, forêt de stalagmites, grappes de cristaux, cou
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

# Plastron + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_BELLY, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_BELLY, parent=body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.32),
              mat=M_BELLY, parent=body_root)

# Strates : bandes de roche claire/sombre, légèrement irrégulières, sur les flancs (motif secondaire Rare)
for sgn in (-1, 1):
    for b in range(STRATA):
        z = ZC + BH * (0.3 - 0.2 * b)
        for sgm in range(3):
            y = -TL * 0.3 + TL * 0.3 * sgm + random.uniform(-0.04, 0.04) * TL
            B(f"Body_Strata_{sgn}_{b}_{sgm}", (0.14 * SC, TL * random.uniform(0.26, 0.31), BH * random.uniform(0.07, 0.1)),
              (sgn * (half_w(y) + 0.03 * SC), y, z + random.uniform(-0.03, 0.03) * BH),
              mat=M_STRATA if (b + sgm) % 2 == 0 else M_STONE2, parent=body_root)

# Plaques de roche en quinconce sur les flancs (écailles de pierre, motif secondaire Rare)
for sgn in (-1, 1):
    for r_ in range(SLAB_ROWS):
        for c_ in range(SLAB_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c_ + 0.5 * (r_ % 2)) / SLAB_COLS
            z = ZC + BH * (0.18 - 0.2 * r_)
            x = sgn * (half_w(y) + 0.045 * SC)
            sz = BH * 0.11
            plate(f"Body_Slab_{sgn}_{r_}_{c_}", [(x, y - sz * 1.1, z), (x, y, z + sz * 0.8), (x, y + sz * 1.1, z), (x, y, z - sz * 0.8)],
                  0.07 * SC, (M_STRATA, M_STONE, M_BODY2, M_STONE)[(r_ + c_) % 4], body_root)

# Stalactites du poitrail : pointes de calcaire qui pendent sous le plastron
for k in range(CHEST_STAL):
    f = (k + 0.5) / CHEST_STAL
    stal(f"Body_ChestStal_{k}", (BW * (-0.32 + 0.64 * f), -TL * 0.5 + 0.1, ZC - BH * 0.42), (0, -0.15, -1.0), 0.16 * SC,
         (0.9 + 0.5 * math.sin(math.pi * f)) * SC, M_LIME if k % 2 == 0 else M_LIME2, body_root, up=(1, 0, 0))

# Forêt de stalagmites : rangée centrale de grandes pointes + 2 rangées plus petites sur les côtés (crête double)
for k in range(CREST_N):
    f = k / max(1, CREST_N - 1)
    y = -TL * 0.38 + (TL * 0.82) * f
    Lh = (2.6 - 0.9 * abs(f - 0.35)) * SC * CREST_K
    rock(f"Body_CrestBase_{k}", (BW * 0.36, TL * 0.8 / CREST_N, 0.28 * SC), (0, y, ZC + BH / 2 + 0.01 * BH), M_STONE2, body_root,
         rot=(0, 0, 0), tx=0.7, ty=0.8)
    stal(f"Body_Stal_{k}", (0, y, ZC + BH / 2 + 0.05 * BH), (0, 0.18 + 0.1 * f, 1.0), 0.42 * SC * CREST_K, Lh * 0.9,
         M_LIME if k % 2 == 0 else M_LIME2, body_root, up=(1, 0, 0))
    if DORSAL_CRYS and k < CREST_N - 1:
        crystal(f"Body_DorsalCrystal_{k}", 0.17 * SC, 0.5 * SC, 0.55 * SC * CREST_K,
                (0, y + (TL * 0.82) / max(1, CREST_N - 1) * 0.5, ZC + BH / 2 + 0.03 * BH), (0, 0.1, 1.0),
                M_CRYS if k % 2 == 0 else M_CRYS2, body_root, up=(0, 1, 0))
    if SIDE_ROW and k < CREST_N - 1:
        yy = y + (TL * 0.82) / max(1, CREST_N - 1) * 0.5
        for sgn in (-1, 1):
            stal(f"Body_StalSide_{sgn}_{k}", (sgn * BW * 0.27, yy, ZC + BH / 2 - 0.02 * BH), (sgn * 0.35, 0.22, 1.0), 0.3 * SC * CREST_K,
                 Lh * 0.55, M_LIME2 if k % 2 == 0 else M_LIME, body_root, up=(1, 0, 0))

# Roches d'épaule + grappes de cristaux sur les épaules
for sgn in (-1, 1):
    for k in range(SHOULDER_ROCKS):
        f = k / max(1, SHOULDER_ROCKS - 1)
        s = BW * (0.46 - 0.2 * f) * SHOULDER_K
        rock(f"Body_Shoulder_{sgn}_{k}", (s, s * 1.1, s * 0.8),
             (sgn * BW * (0.46 + 0.07 * f), -TL * (0.22 - 0.14 * f), ZC + BH * (0.42 - 0.2 * f)),
             STONES[(k + 1) % 3], body_root, jit=14, bevel=0.03 * SC if k == 0 else 0)
    for k in range(SHOULDER_CLUSTERS):
        cluster(f"Body_ShoulderCrystals_{sgn}_{k}", Vector((sgn * BW * (0.5 + 0.02 * k), -TL * (0.2 - 0.16 * k), ZC + BH * (0.66 - 0.12 * k))),
                (sgn * 0.45, 0.0, 1.0), CLUSTER_N, 0.7 * SC * CLUSTER_K, body_root)

# Cou : courbe lissée de la tête vers le torse, bloc gris + plaque claire devant par maillon, petites pointes sur la nuque
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
    if NAPE_STAL and i < NN - 1:
        stal(f"Body_NapeStal_{i}", mid + d * r * 0.85, d * 0.8 + t * 0.55, r * 0.4, r * 1.7 * CREST_K, M_LIME if i % 2 else M_LIME2,
             body_root, up=tuple(side))

# ----------------------------------------------------------
# 11. PATTES : cuisse en wedge, jambe à plaques de roche, bracelet, genouillère, pied, 3 doigts + 3 griffes de pierre
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.26)
SHIN_H = LEG_H * 0.42

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.3)
    yo = th * 0.15 if hind else 0
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.45
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.7 if hind else 1.5), thigh_h),
          (x + sgn * 0.05 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.1), mat=M_BODY, parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.08 * SC)
    box(f"{name}_Shin", (th * 0.92, th * 0.97, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=M_STONE if ARMOR else M_BODY, parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    if ARMOR:
        rock(f"{name}_Bracer", (th * 1.1, th * 1.14, SHIN_H * BRACER_K), (x, y + yo, FOOT_H + SHIN_H * 0.62), M_STONE2, legs_root,
             rot=(0, 0, random.uniform(-6, 6)), tx=0.92, ty=0.92)
        B(f"{name}_BracerTop", (th * 1.0, th * 1.04, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.62 + SHIN_H * BRACER_K / 2 + 0.02),
          mat=M_STRATA, parent=legs_root)
    if KNEE:
        rock(f"{name}_Knee", (th * 0.8, th * 0.45, th * 0.6), (x, y + yo - th * 0.62, FOOT_H + SHIN_H + 0.2 * thigh_h),
             M_STONE2, legs_root, jit=5)
    if KNEE:
        cluster(f"{name}_KneeCrystals", Vector((x, y + yo - th * 0.9, FOOT_H + SHIN_H + 0.2 * thigh_h)), (0, -0.7, 1.0), 3, 0.5 * th * 0.6, legs_root)
    if LEG_CRACKS:
        crack(f"{name}_ThighVein", (x + sgn * (th * 0.66 + 0.02), y + yo, FOOT_H + SHIN_H + thigh_h * 0.85),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 3, thigh_h * 0.2, -70, legs_root, th=0.12,
              lim=(-th * 0.5, th * 0.5, -thigh_h * 0.6, 0.0))
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_BODY,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.26, th * 0.2, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments gris, plaques claires dessous, stalagmites dessus,
#     bout de queue en massue de roche hérissée de stalagmites et de cristaux (ornement final).
#     Pas de section 12 : le Drake n'a pas d'ailes.
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
    if i % TAIL_STAL_EVERY == 0 and s < 0.9:
        stal(f"Tail_Stal_{i}", mid + d * r * 0.8, d * 1.0 + t * 0.45, r * 0.6, (2.0 - 0.9 * s) * r * 1.4 * CREST_K,
             M_LIME if i % 2 == 0 else M_LIME2, tail_root, up=tuple(side))
    if i % 2 == 1 and s < 0.85 and not IS_BEBE:
        for sgn in (-1, 1):
            B(f"Tail_Strata_{i}_{sgn}", (0.12 * SC, Ln * 0.9, r * 0.28), mid + side * sgn * (r * 0.97), R,
              M_STRATA if i % 4 == 1 else M_STONE2, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
CL = CLUB_SIZE
core = tip + tt_ * CL * 0.4
rock("Tail_TipCore", (CL * 1.3, CL * 1.3, CL * 1.1), core, M_STONE, tail_root, rot=(0, 0, 0), tx=0.85, ty=0.85, bevel=0.05 * SC)
rock("Tail_TipTop", (CL * 0.9, CL * 0.9, CL * 0.5), core + Vector((0, 0, CL * 0.55)), M_STONE2, tail_root, jit=8)
for k in range(TIP_STAL):
    a = k * 2 * math.pi / TIP_STAL + 0.5
    dv = Vector((math.cos(a) * 0.7, 0.35, 0.8 + 0.4 * math.sin(a)))
    stal(f"Tail_TipStal_{k}", core + Vector((0, 0, CL * 0.5)), dv, CL * 0.26, CL * (1.7 + 0.35 * (k % 2)),
         M_LIME if k % 2 == 0 else M_LIME2, tail_root)
if TIP_CRYS:
    cluster("Tail_TipCrystals", core + Vector((0, tt_.y * CL * 0.3, CL * 0.62)), (0, 0.2, 1.0), TIP_CRYS, CL * 0.8, tail_root)

# ----------------------------------------------------------
# 10b. VEINES DE MINERAI sur les flancs (motif secondaire Rare, lueur discrète)
# ----------------------------------------------------------
for sgn in (-1, 1):
    for c in range(CRACKS):
        y0 = -TL * 0.34 + c * TL * 0.28
        crack(f"Body_Vein_{sgn}_{c}", (sgn * (half_w(y0) + 0.09 * SC), y0, ZC + BH * 0.3),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 5, BH * 0.25, -80 + 35 * c, body_root, th=0.12,
              lim=(-TL * 0.16, TL * 0.16, -BH * 0.75, 0.0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (strates + veines de minerai), cornes à 2 pointes, crête double de stalagmites,
#     accent lumineux discret (yeux, cristaux, veines : strength <= 1.5).
#     Seuls éléments flottants : petits cristaux et éclats de calcaire qui dérivent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.0 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.3 + 1.0), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 1.0])
        if k % 2 == 0:
            crystal(f"FX_Crystal_{k}", FX_SIZE * 0.22, FX_SIZE * 0.5, FX_SIZE * 0.5, p, dirv, M_CRYS if k % 4 == 0 else M_CRYS2, master, up=(0, 1, 0))
        else:
            diamond(f"FX_Chip_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.45, M_LIME, master,
                    up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.06 * SC)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
