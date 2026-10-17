import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Pépite · Ado
#  Mythique · Minéral · Drake · monde 5
#  - Drake plus costaud : crocs, sourcils d'or, cornes en éventail, armure dorsale de plaques et de pépites
#  - Signes distinctifs : pépites bosselées sur le dos, les flancs, les épaules et la queue ; massue de pépites sertie de gemmes
#  - Rareté Mythique : halo de pièces et de rayons, gemmes multiples (ambre, rubis, émeraude), veines d'or lumineuses, pièces en orbite
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(5101)            # même dragon à chaque exécution
TAG = "PEPITE_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 11000          # budget de triangles de ce stade et de cette rareté
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
#    Or métallique brillant (corps, cornes, armure), or pâle (ventre, pointes), pépites d'or brut bosselées
#    (3 teintes d'or), gemmes multiples (ambre, rubis, émeraude, diamant) et éclats d'or ÉMISSIFS.
#    Rareté Mythique : metallic 0,8-0,9 et rugosité basse sur presque tout le corps.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#E6B422", 0.26, metallic=0.9)                     # corps en or brillant
M_BODY2 = get_mat("BodyScale", "#CC9E1D", 0.30, metallic=0.85)                    # dessus du museau, plaques, pieds
M_DARK  = get_mat("BodyDark",  "#8A6C14", 0.45, metallic=0.6)                     # bouche, narines, ombres
M_NUG1  = get_mat("Nugget",    "#D9A21B", 0.32, metallic=0.85)                    # pépites d'or brut
M_NUG2  = get_mat("NuggetDark", "#B8860F", 0.42, metallic=0.8)                    # pépites sombres (brut)
M_NUG3  = get_mat("NuggetLight", "#F6DC7A", 0.20, metallic=0.9)                   # pépites polies, claires
M_CREAM = get_mat("Belly",     "#F4D77A", 0.28, metallic=0.55)                    # ventre en plaques, plastron, menton
M_HORN  = get_mat("Horn",      "#E6B422", 0.24, metallic=0.9)                     # cornes
M_TIP   = get_mat("HornTip",   "#FFF0B0", 0.20, metallic=0.7)                     # pointes claires
M_CREST = get_mat("Crest",     "#C8961A", 0.30, metallic=0.85)                    # sourcils, crêtes
M_COIN  = get_mat("Coin",      "#FFD24A", 0.18, metallic=1.0)                     # pièces d'or (halo, orbite)
M_CLAW  = get_mat("Claw",      "#FBF1D0", 0.30)                                   # griffes et crocs
M_WHITE = get_mat("EyeWhite",  "#F6F3EA", 0.30)
M_IRIS  = get_mat("Iris",      "#E0861E", 0.25, emission="#FFA21F", strength=3.0) # iris ambre lumineux
M_BLACK = get_mat("Black",     "#0E0A07", 0.30)
M_GLOW  = get_mat("Glow",      "#FFE27A", 0.25, emission="#FFD54A", strength=3.5) # éclats d'or lumineux, halo
M_VEIN  = get_mat("Vein",      "#FFE9A0", 0.30, emission="#FFD34A", strength=2.0) # veines d'or en fusion
M_AMBER = get_mat("GemAmber",  "#FFAE1A", 0.10, emission="#FF9E10", strength=2.2) # gemme ambre
M_RUBY  = get_mat("GemRuby",   "#E0243A", 0.10, emission="#FF2038", strength=2.0) # rubis
M_EMER  = get_mat("GemEmerald", "#22C46E", 0.10, emission="#20E080", strength=1.8) # émeraude
M_DIAM  = get_mat("GemDiamond", "#EAF7FF", 0.08, emission="#BFE6FF", strength=1.6) # petit diamant
NUGS = [M_NUG1, M_NUG2, M_NUG3, M_NUG1]
GEMS = [M_AMBER, M_RUBY, M_EMER, M_DIAM, M_AMBER]

# ----------------------------------------------------------
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADO"
BW = 2.7
BH = 2.0
LEG_H = 2.0
TORSO_L = 3.9
NECK_L = 1.9
NECK_LEAN = 0.35
NECK_N = 3
NECK_R = (0.8, 0.98)
HEAD_SCALE = 1.05
SNOUT_K = 1.0
FANGS = 2
HORN_N = 4
HORN_K = 0.85
HEAD_NUGS = 4
CHEEK_N = 3
BEARD = 2
BELLY_N = 5
BELLY_SIDES = True
FLANK_ROWS = 4
FLANK_COLS = 6
CREST_N = 5
STACK = True
BACK_ROWS = True
SHOULDER_K = 0.8
SHOULDER_ROCKS = 4
NAPE_ROCKS = True
BRACER_K = 0.5
LEG_BEV = 1
LEG_PEBBLES = 3
KNEE = True
GAUNTLET = False
LEG_GEM = True
LEG_CRACKS = 0
CRACKS = 2
TAIL_L = 4.8
TAIL_STEP = 0.75
TAIL_BEV_N = 3
TAIL_SCALES = True
CLUB_SIZE = 1.2
CLUB_ROCKS = 5
CLUB_SPIKES = 3
CLUB_GEMS = 3
CLUB_SUB = True
NUG_SUB = 1
GEM_N = 3
HALO_R = 1.45
HALO_COINS = 9
HALO_RAYS = 7
SPARKS = 12
FX_COINS = 14
FX_SPARKS = 14
FX_SIZE = 0.6
GROUND_RING = 1.9

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

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1)):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def nugget_mesh(sx, sy, sz, sub, bump):
    """Pépite d'or brut : icosphère très basse résolution dont chaque sommet est déplacé au hasard (seed fixe)."""
    bm = bmesh.new()
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=0.5)
    except TypeError:
        bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=0.5)
    for v in bm.verts:
        d = v.co.normalized() * 0.5 * random.uniform(1 - bump, 1 + bump)
        v.co = Vector((d.x * sx, d.y * sy, d.z * sz * (0.8 if d.z < 0 else 1.0)))
    me = bpy.data.meshes.new(f"{TAG}_nugget")
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me

def rock(name, size, loc, mat, parent, rot=None, jit=10, tx=0.72, ty=0.78, bevel=0.0, sub=1, bump=0.24):
    """Pépite bosselée posée en 'loc' (tx, ty, bevel gardés pour compatibilité, non utilisés)."""
    if rot is None:
        rot = (random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit * 2, jit * 2))
    s = max(size) * 0.0 + 1.18
    return place(name, nugget_mesh(size[0] * s, size[1] * s, size[2] * s, sub, bump), mat, loc, rot, parent)

def slab(name, size, loc, mat, parent, rot=None, jit=10, tx=0.72, ty=0.78, bevel=0.0):
    """Plaque d'or taillée : bloc dont le dessus est rétréci, légèrement tourné au hasard."""
    if rot is None:
        rot = (random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit * 2, jit * 2))
    return wedge(name, size, loc, rot, mat, parent, top_x=tx, top_y=ty,
                 shift_y=random.uniform(-0.12, 0.12) * size[1], bevel=bevel)

def diamond(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Plaque en losange (éclat d'or flottant)."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def coin(name, r, loc, direction, parent, mat=None, sides=10):
    """Pièce d'or : disque fin à 10 faces."""
    return prism(name, r, r * 0.22, loc, direction, mat or M_COIN, parent, sides=sides)

def gem(name, r, loc, direction, mat, parent, sides=6):
    """Gemme taillée : prisme à pointe (rubis, ambre, émeraude, diamant)."""
    return crystal(name, r, r * 0.8, r * 0.7, loc, direction, mat, parent, sides=sides)

def crack(name, origin, e1, e2, normal, steps, step_len, heading, parent, th=0.09, mat=None, lim=None):
    """Veine d'or en fusion : marche aléatoire en zigzag sur une face (plan e1/e2), posée sur la surface.
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
#    Crâne carré en or poli, museau court et large, mâchoire pâle, cornes en éventail, pépites sur le crâne,
#    gemme au front, HALO d'or (anneau + pièces + rayons) flottant derrière la tête.
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

def hrock(name, size, loc, mat, rot=None, jit=12, sub=1):
    return rock("Head_" + name, hv(size), hv(loc), mat, H, rot, jit, sub=sub)

hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.75, 2.1 * SNOUT_K, 1.0), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.06, bevel=0.08)
hbox("SnoutTop", (1.6, 1.9 * SNOUT_K, 0.16), (0, -0.6 - 1.0 * SNOUT_K, 0.27), mat=M_BODY2, bevel=0.03)
hbox("SnoutBridge", (0.7, 1.2 * SNOUT_K, 0.1), (0, -0.6 - 0.8 * SNOUT_K, 0.37), mat=M_NUG3)
hbox("Jaw", (1.55, 1.95 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM, bevel=0.04)
hbox("Chin", (1.7, 0.4, 0.4), (0, -0.55 - 2.0 * SNOUT_K - 0.08, -0.74), mat=M_CREAM, bevel=0.04)
hbox("MouthLine", (1.8, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.26, 0.24, 0.07), (sgn * 0.5, SNOUT_FRONT + 0.25, 0.36), mat=M_BLACK)

# Yeux : blanc, iris ambre lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte) + sourcils d'or
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
    else:
        hbox(f"Brow_{sgn}", (0.2, 1.0, 0.26), (sgn * 0.97, ey - 0.05, ez + 0.54), rot=(14, 0, 0),
             mat=M_CREST, bevel=0.02)

# Crocs : ado 2 par côté (petits), adulte 3 par côté (plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.72, fy, -0.74), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Cornes d'or en éventail vers l'arrière, pointe claire
for sgn in (-1, 1):
    for k in range(HORN_N):
        f = k / max(1, HORN_N - 1)
        Ln = (1.05 + 0.85 * (1 - f)) * HORN_K
        hshard(f"Horn_{sgn}_{k}", 0.72 + 0.12 * (1 - f), 0.4, Ln,
               (sgn * (0.2 + 0.58 * f), 0.1 + 0.25 * f, 0.72 - 0.15 * f),
               (sgn * (0.22 + 0.85 * f), 1.0, 0.8 - 0.4 * f), M_HORN if k % 2 == 0 else M_TIP)
    if IS_ADO or IS_ADULTE:
        hshard(f"CheekHorn_{sgn}", 0.45, 0.28, 1.0 + 0.3 * IS_ADULTE, (sgn * 0.88, 0.45, -0.25),
               (sgn * 0.8, 0.9, -0.1), M_HORN)

# Pépites : crête entre les cornes, joues, barbe sous la mâchoire
for k in range(HEAD_NUGS):
    hrock(f"CrestNug_{k}", (0.55, 0.6, 0.45 + 0.1 * (k % 2)),
          ((-0.35 + 0.35 * k) * (1 if HEAD_NUGS > 1 else 0), 0.35 + 0.1 * (k % 2), 0.9), NUGS[k % 4], sub=NUG_SUB)
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hrock(f"Cheek_{sgn}_{k}", (0.42, 0.45 + 0.1 * k, 0.36), (sgn * 0.97, -0.1 + 0.42 * k, -0.4 + 0.2 * (k % 2)),
              NUGS[(k + 1) % 4], rot=(0, sgn * 82, random.uniform(-15, 15)), jit=0)
if BEARD:
    for k in range(BEARD):
        sgn = -1 if k % 2 == 0 else 1
        hrock(f"Beard_{k}", (0.5, 0.55, 0.5), (sgn * (0.25 + 0.2 * (k // 2)), 0.1 + 0.4 * (k // 2), -1.0), NUGS[(k + 1) % 3])

# Gemme au front (rubis) + gemmes de tempe (ambre, émeraude)
if GEM_N > 0:
    gem("Head_ForeGem", 0.2 * HS, hv((0, -0.55, 0.98)), (0, -0.4, 1), M_RUBY, H)
for k in range(1, GEM_N):
    sgn = 1 if k % 2 else -1
    gem(f"Head_TempleGem_{k}", 0.13 * HS, hv((sgn * (0.55 + 0.25 * (k // 2)), -0.35, 0.9)), (sgn * 0.5, -0.3, 1),
        GEMS[k % 5], H)

# HALO FLOTTANT derrière la tête : anneau d'or, anneau lumineux, pièces sur l'anneau, rayons d'or
if HALO_R > 0:
    hc = (0, 1.45, 0.45)
    ring("Head_HaloRing", HALO_R * HS, 0.34 * HS, 0.14 * HS, hv(hc), (0, 1, 0), M_BODY, H, sides=20)
    ring("Head_HaloGlow", HALO_R * HS * 0.78, 0.14 * HS, 0.1 * HS, hv((0, 1.55, 0.45)), (0, 1, 0), M_GLOW, H, sides=20)
    for k in range(HALO_COINS):
        a = 2 * math.pi * k / HALO_COINS
        coin(f"Head_HaloCoin_{k}", 0.3 * HS, hv((HALO_R * math.cos(a), 1.4, 0.45 + HALO_R * math.sin(a))), (0, 1, 0.1), H)
    for k in range(HALO_RAYS):
        a = math.radians(-150 + 300 * k / max(1, HALO_RAYS - 1))
        rad = Vector((math.sin(a), 0, math.cos(a)))
        shard(f"Head_HaloRay_{k}", 0.4 * HS, 0.1 * HS, (0.4 + 0.25 * (k % 2)) * HS,
              Vector(hv((rad.x * HALO_R * 1.08, 1.45, 0.45 + rad.z * HALO_R * 1.08))), rad, M_GLOW if k % 2 else M_TIP, H, up=(0, 1, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs d'or, plastron à gemme, ventre en plaques, flancs en pépites, dos en armure de pépites
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

# Plastron or pâle + gemme ambre sertie + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
CH_C = Vector((0, -TL * 0.5 - 0.1, ZC - BH * 0.08))
ring("Body_ChestRing", BH * 0.3, 0.09 * BH, 0.12 * SC, CH_C, (0, -1, 0), M_BODY, body_root, sides=10)
gem("Body_ChestGem", BH * 0.2, CH_C + Vector((0, 0.03, 0)), (0, -1, 0), M_AMBER, body_root, sides=8)
if GEM_N > 1:
    for sgn in (-1, 1):
        gem(f"Body_ChestGemS_{sgn}", BH * 0.09, CH_C + Vector((sgn * BW * 0.27, 0.0, BH * 0.05)), (0, -1, 0), GEMS[1 + (sgn > 0)], body_root)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Pépites bosselées en quinconce sur les flancs
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.24 - 0.17 * r)
            s = BH * random.uniform(0.27, 0.38)
            rock(f"Body_Nug_{sgn}_{r}_{c}", (s * 1.1, s * 1.2, s * 0.8), (sgn * (half_w(y) + 0.03 * SC), y, z),
                 pick([M_NUG1, M_NUG3, M_BODY2, M_NUG2], [4, 2, 3, 1]), body_root, rot=(0, sgn * 80, random.uniform(-18, 18)), jit=0, sub=NUG_SUB)

# Armure dorsale : plaques d'or le long de l'échine, une grosse pépite sur chaque plaque, deux rangées latérales
for k in range(CREST_N):
    f = k / max(1, CREST_N - 1)
    y = -TL * 0.38 + (TL * 0.82) * f
    w = BW * (0.62 - 0.14 * abs(f - 0.3))
    slab(f"Body_Plate_{k}", (w, TL * 0.9 / CREST_N * 1.25, 0.42 * SC + 0.1 * BH * (1 - f)),
         (random.uniform(-0.05, 0.05) * BW, y, ZC + BH / 2 + 0.06 * BH),
         M_BODY if k % 2 == 0 else M_BODY2, body_root, rot=(random.uniform(-4, 4), 0, random.uniform(-6, 6)), tx=0.8, ty=0.85, bevel=0.03 * SC)
    if STACK:
        rock(f"Body_PlateNug_{k}", (w * 0.55, TL * 0.9 / CREST_N * 0.8, 0.4 * SC), (random.uniform(-0.2, 0.2) * BW, y + random.uniform(-0.1, 0.1),
             ZC + BH / 2 + 0.06 * BH + 0.32 * SC), NUGS[k % 4], body_root, jit=6, sub=NUG_SUB)
    for sgn in ((-1, 1) if BACK_ROWS else ()):
        rock(f"Body_BackNug_{k}_{sgn}", (w * 0.42, w * 0.46, 0.42 * SC), (sgn * BW * 0.33, y + random.uniform(-0.15, 0.15), ZC + BH / 2 - 0.02 * BH),
             NUGS[(k + 1 + (sgn > 0)) % 4], body_root, jit=8, sub=NUG_SUB)

# Épaules : grappes de grosses pépites + gemme émeraude
for sgn in (-1, 1):
    for k in range(SHOULDER_ROCKS):
        f = k / max(1, SHOULDER_ROCKS - 1)
        s = BW * (0.46 - 0.2 * f) * SHOULDER_K
        rock(f"Body_Shoulder_{sgn}_{k}", (s, s * 1.1, s * 0.8),
             (sgn * BW * (0.46 + 0.07 * f), -TL * (0.22 - 0.14 * f), ZC + BH * (0.42 - 0.2 * f)),
             NUGS[(k + 1) % 4], body_root, jit=14, sub=NUG_SUB if k == 0 else 1)
    if GEM_N > 1:
        gem(f"Body_ShoulderGem_{sgn}", BW * 0.07, (sgn * BW * 0.6, -TL * 0.22, ZC + BH * 0.62), (sgn * 0.6, 0, 1), M_EMER, body_root)

# Éclats d'or lumineux semés sur le dos et les flancs
for k in range(SPARKS):
    f = (k + 0.5) / SPARKS
    sgn = 1 if k % 2 else -1
    crystal(f"Body_Spark_{k}", 0.1 * SC, 0.12 * SC, 0.16 * SC,
            (sgn * BW * random.uniform(0.15, 0.4), -TL * 0.4 + TL * 0.85 * f, ZC + BH / 2 + 0.55 * SC + random.uniform(0, 0.25) * SC),
            (0, 0, 1), M_GLOW, body_root, sides=4)

# Cou : un bloc d'or + une plaque pâle devant par maillon, pépites de nuque
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
    if NAPE_ROCKS:
        rock(f"Body_NapeNug_{i}", (r * 1.1, Ln * 0.9, r * 0.55), mid + d * r * 0.95, NUGS[(i + 1) % 4], body_root, jit=6, sub=NUG_SUB)
        if s > 0.25:
            for sgn in (-1, 1):
                rock(f"Body_NeckNug_{i}_{sgn}", (r * 0.7, Ln * 0.75, r * 0.6), mid + side * sgn * r * 0.95 + d * r * 0.2,
                     NUGS[(i + (sgn > 0)) % 4], body_root, jit=10)

# ----------------------------------------------------------
# 11. PATTES : cuisse en wedge, jambière d'or, bracelet à gemme, pied, 3 doigts + 3 griffes claires
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
    box(f"{name}_Shin", (th * 0.92, th * 0.97, SHIN_H + 0.1), (x, y + yo, FOOT_H + SHIN_H / 2),
        mat=(M_BODY2 if not GAUNTLET else M_NUG2), parent=legs_root, bevel=LEG_BEV * 0.05 * SC)
    bh_ = SHIN_H * BRACER_K
    slab(f"{name}_Bracer", (th * 1.1, th * 1.14, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.62), M_BODY, legs_root,
         rot=(0, 0, random.uniform(-6, 6)), tx=0.92, ty=0.92, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.0, th * 1.04, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.62 + bh_ / 2 + 0.02),
      mat=M_NUG3, parent=legs_root)
    if GEM_N > 0 and LEG_GEM:
        gem(f"{name}_BracerGem", th * 0.14, (x + sgn * (th * 0.56), y + yo, FOOT_H + SHIN_H * 0.62), (sgn, 0, 0), GEMS[(int(y * 3) + (sgn > 0)) % 5], legs_root)
    for k in range(LEG_PEBBLES):
        s = th * random.uniform(0.28, 0.4)
        rock(f"{name}_Pebble_{k}", (s, s * 1.1, s * 0.8),
             (x + sgn * th * 0.62, y + yo + th * (-0.3 + 0.3 * k), FOOT_H + SHIN_H + thigh_h * (0.7 - 0.22 * (k % 3))),
             NUGS[k % 4], legs_root, rot=(0, sgn * 80, random.uniform(-20, 20)), jit=0, sub=NUG_SUB)
    if KNEE:
        rock(f"{name}_Knee", (th * 0.8, th * 0.5, th * 0.6), (x, y + yo - th * 0.62, FOOT_H + SHIN_H + 0.2 * thigh_h),
             M_NUG3, legs_root, jit=5, sub=NUG_SUB)
    fy = y - th * 0.35
    box(f"{name}_Foot", (th * 1.15, th * 1.9, FOOT_H), (x, fy + yo, FOOT_H / 2),
        mat=M_BODY2, parent=legs_root, bevel=0.06 * SC)
    toe_y = fy + yo - th * 0.95 - th * 0.12
    for k in (-1, 0, 1):
        B(f"{name}_Toe_{k}", (th * 0.28, th * 0.5, FOOT_H * 0.72), (x + k * th * 0.32, toe_y, FOOT_H * 0.36), mat=M_CREAM,
          parent=legs_root)
        shard(f"{name}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (x + k * th * 0.32, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    for c in range(LEG_CRACKS):
        dy = -th * 0.25 + th * 0.3 * c
        crack(f"{name}_Vein_{c}", (x + sgn * (th * 0.46 + 0.02), y + yo + dy, FOOT_H + SHIN_H * 0.95),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 3, SHIN_H * 0.24, -90 + 40 * c, legs_root, th=0.09,
              lim=(-th * 0.42 - dy, th * 0.42 - dy, -SHIN_H * 0.9, 0.0))

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments d'or, plaques pâles, pépites, grosse massue de pépites sertie de gemmes
#     (pas de section 12 : le Drake n'a pas d'ailes)
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_CREAM, tail_root)
    if i % 2 == 0 and s < 0.85:
        rock(f"Tail_Nug_{i}", (r * 1.3, Ln * 1.2, r * 0.55), mid + d * r * 0.9, NUGS[(i // 2) % 4], tail_root, jit=5, sub=NUG_SUB)
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            rock(f"Tail_Stone_{i}_{sgn}", (r * 0.6, Ln * 0.9, r * 0.6), mid + side * sgn * (r * 0.95), NUGS[(i + 1) % 3 + 1 - (i % 2)],
                 tail_root, jit=8)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
CL = CLUB_SIZE
core = tip + tt_ * CL * 0.45
rock("Tail_ClubCore", (CL * 1.6, CL * 1.6, CL * 1.4), core, M_NUG1, tail_root, rot=(0, 0, 0), sub=2 if CLUB_SUB else 1, bump=0.16)
rock("Tail_ClubTop", (CL * 1.0, CL * 1.0, CL * 0.6), core + Vector((0, 0, CL * 0.7)), M_NUG3, tail_root, jit=8, sub=NUG_SUB)
for k in range(CLUB_ROCKS):
    a = k * 2 * math.pi / CLUB_ROCKS + 0.4
    off = Vector((math.cos(a) * CL * 0.78, random.uniform(-0.4, 0.4) * CL, math.sin(a) * CL * 0.6))
    rock(f"Tail_ClubNug_{k}", (CL * 0.6, CL * 0.6, CL * 0.5), core + off, NUGS[k % 4], tail_root, jit=15, sub=NUG_SUB)
for k in range(CLUB_SPIKES):
    a = k * 2 * math.pi / CLUB_SPIKES + 1.0
    dv = Vector((math.cos(a), 0.25, math.sin(a)))
    shard(f"Tail_ClubSpike_{k}", CL * 0.4, CL * 0.35, CL * 0.8, core + dv * CL * 0.7, dv, M_HORN if k % 2 == 0 else M_TIP, tail_root)
for k in range(CLUB_GEMS):
    a = k * 2 * math.pi / CLUB_GEMS + 0.2
    dv = Vector((math.cos(a), -0.5, math.sin(a)))
    gem(f"Tail_ClubGem_{k}", CL * 0.17, core + dv.normalized() * CL * 0.78, dv, GEMS[k % 5], tail_root)
if CRACKS:
    for sgn in (-1, 1):
        crack(f"Tail_ClubVein_{sgn}", core + Vector((sgn * CL * 0.78, -CL * 0.3, CL * 0.1)), (0, 1, 0), (0, 0, 1), (sgn, 0, 0),
              3, CL * 0.25, -60, tail_root, th=0.1, lim=(-CL * 0.4, CL * 0.95, -CL * 0.55, CL * 0.2))

# ----------------------------------------------------------
# 10b. VEINES D'OR EN FUSION (émissives) sur les flancs
# ----------------------------------------------------------
for sgn in (-1, 1):
    for c in range(CRACKS):
        y0 = -TL * 0.3 + c * TL * 0.28
        crack(f"Body_Vein_{sgn}_{c}", (sgn * (half_w(y0) + 0.02), y0, ZC + BH * 0.3),
              (0, 1, 0), (0, 0, 1), (sgn, 0, 0), 4, BH * 0.22, -80 + 35 * c, body_root, th=0.1,
              lim=(-TL * 0.13, TL * 0.13, -BH * 0.7, 0.0))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (MYTHIQUE) + FX
#     Or métallique sur tout le corps, pépites, gemmes multiples, veines et éclats émissifs, halo de pièces
#     derrière la tête. FX : deux anneaux de pièces d'or en orbite + éclats d'or et gemmes qui dérivent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.0 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    R_FX = BW * 1.35 + 1.0
    zmid = (LEG_H * 0.9 + top_z * 0.9) / 2
    ymid = TL * 0.05 + TAIL_L * 0.12
    for k in range(FX_COINS):
        ring_i = k % 2
        a = 2 * math.pi * (k // 2) / max(1, FX_COINS // 2) + 0.5 * ring_i
        rr = R_FX * (1.0 + 0.3 * ring_i) + TL * 0.2
        p = Vector((rr * math.cos(a), ymid + rr * 0.9 * math.sin(a), zmid + (-1) ** ring_i * (top_z - LEG_H) * 0.28 + 0.4 * math.sin(3 * a)))
        coin(f"FX_Coin_{k}", FX_SIZE * 0.55, p, (math.cos(a), math.sin(a) * 0.9, 0.4 + 0.5 * math.sin(2 * a)), master)
    for k in range(FX_SPARKS):
        p = Vector((random.uniform(-1, 1) * (BW * 1.5 + 1.0), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 4 == 3:
            gem(f"FX_Gem_{k}", FX_SIZE * 0.32, p, dirv, GEMS[k % 5], master)
        else:
            diamond(f"FX_Spark_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.5, M_GLOW if k % 2 else M_NUG3,
                    master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.07 * SC)
    if GROUND_RING:
        gr = BW * GROUND_RING
        ring("FX_GroundRing", gr, 0.18 * SC, 0.06, (0, 0, 0.03), (0, 0, 1), M_BODY, master, sides=24, up=(0, 1, 0))
        ring("FX_GroundGlow", gr * 0.82, 0.1 * SC, 0.05, (0, 0, 0.03), (0, 0, 1), M_GLOW, master, sides=24, up=(0, 1, 0))

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
