import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Braisillon · Adulte
#  Commun · Feu · Wyvern · monde 2
#  - Adulte wyvern puissant : cou de 5 maillons en S, mâchoire dorée, 3 crocs par côté, sourcils sévères, grandes cornes de basalte
#  - Armure de basalte noir sur le dos, le cou, les épaules, les genoux et les jambes, parcourue de fissures de lave lumineuses
#  - Crinière de flammes sur 3 anneaux et couronne de 3 grandes flammes, ventre doré en plaques, plastron doré
#  - Grandes ailes-bras orange à facettes jaunes, poignet près du sol, queue terminée par un bouquet de 7 flammes, braises flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1109)            # même dragon à chaque exécution
TAG = "BRAISILLON_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
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
#    Rouge braise (corps), basalte noir (plaques, cornes), or (ventre), flammes orange / jaune, os ivoire (griffes).
#    Commun : seuls les yeux et les braises (petits points de lave) brillent, très doucement.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#DC4A22", 0.50)   # corps principal rouge braise
M_BODY2  = get_mat("BodyScale",  "#B93A1E", 0.50)   # écailles, dessus des pattes, orteils
M_DARK   = get_mat("BodyDark",   "#7E2616", 0.55)   # bouche, ombres, os d'aile, pupilles de peau
M_ROCK   = get_mat("Basalt",     "#2B2522", 0.70)   # plaques de basalte, cornes, sourcils
M_ROCK2  = get_mat("BasaltLight","#4A403A", 0.70)   # basalte plus clair (alternance)
M_CREAM  = get_mat("Belly",      "#F2B650", 0.55)   # ventre en plaques, plastron, menton (doré)
M_FL1    = get_mat("FlameOrange","#F2711C", 0.40)   # flammes orange (crinière, queue)
M_FL2    = get_mat("FlameYellow","#FFB52E", 0.40)   # flammes jaune-orange
M_FL3    = get_mat("FlameHot",   "#FFD65A", 0.40)   # coeur des flammes
M_LAVA   = get_mat("Lava",       "#FF9A1F", 0.40, emission="#FF8A00", strength=1.5)  # braises et fissures
M_CLAW   = get_mat("Claw",       "#E8DCC0", 0.35)   # griffes, crocs
M_WING   = get_mat("Membrane",   "#F07A1E", 0.55)   # membrane des ailes
M_WING2  = get_mat("MembraneHot","#FFA630", 0.55)   # facettes claires de la membrane
M_WHITE  = get_mat("EyeWhite",   "#F4EEDD", 0.30)
M_IRIS   = get_mat("Iris",       "#FFB52E", 0.25, emission="#FFB52E", strength=2.0)
M_BLACK  = get_mat("Black",      "#120B08", 0.30)
FLAMES = [M_FL1, M_FL2, M_FL3]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
LEAN = 14                 # inclinaison du torse vers l'avant (degrés)
BW = 2.6                  # largeur du torse
BH = 2.5                  # hauteur du torse
TORSO_L = 4.8             # longueur du torse
LEG_H = 3.5               # hauteur des pattes arrière
NECK_L = 3.4              # longueur du cou
NECK_LEAN = 1.1           # avancée du cou vers l'avant
NECK_N = 5                # nombre de maillons du cou
NECK_R = (0.85, 1.15)     # rayon du cou (haut, bas)
HEAD_SCALE = 1.25         # taille de la tête
SNOUT_K = 1.0             # longueur du museau
FANGS = 3                 # crocs par côté
CHEEK_SPIKES = 3          # pointes de joue par côté
CHEEK_EMBERS = 3          # braises de joue par côté
MANE_RINGS = 2            # anneaux de flammes de la crinière
MANE_N = 12               # flammes dans l'anneau extérieur
FLAME_K = 1.2             # taille des flammes
BELLY_N = 6               # plaques de ventre
BELLY_SIDES = True        # plaques dorées sur les flancs bas
FLANK_ROWS = 2            # rangées d'écailles de flanc
FLANK_COLS = 4            # écailles par rangée
BACK_PLATES = 7           # plaques de basalte sur le dos
LAVA_CRACKS = True        # fissures de lave sur le basalte
EMBERS = 12               # points de braise sur le corps
NECK_ROCK = True          # basalte sur le cou
PAULDRON = 3              # pointes d'épaulière (0 = pas d'épaulière)
THIGH_EMBERS = 3          # braises sur la cuisse
LEG_BEV = 1               # biseau des jambes
THIGH_ROCK = True         # plaque de basalte sur la cuisse
FLANK_ROCKS = 4           # blocs de basalte par flanc
WING_SPAN = 7.2           # envergure d'une aile
WRIST_Z = 1.2             # hauteur du poignet (près du sol)
WING_BONE = 0.32          # épaisseur des os d'aile
WING_FINGERS = 3          # doigts d'aile
WING_FACETS = True        # facettes claires sur la membrane
TAIL_L = 6.8              # longueur de la queue
TAIL_STEP = 0.8           # pas des segments de queue
TAIL_BEV_N = 4            # segments de queue biseautés
TAIL_SCALES = True        # écailles sur la queue
TAIL_FLAMES = 7           # lames de la flamme de queue
TAIL_FLAME_L = 3.2        # hauteur de la flamme de queue
FX_N = 12                 # braises flottantes
FX_SIZE = 0.7             # taille des braises flottantes

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Wyvern : 2 pattes arrière, torse penché en avant, ailes-bras. Tout est en unités de travail ;
#    finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.2                                    # échelle des petits détails
TL = TORSO_L
LEAN_R = math.radians(LEAN)
PEL_Z = LEG_H * 0.95 + BH * 0.35                 # hauteur du centre du torse
CEN = Vector((0, TL * 0.03, PEL_Z))
TT = Vector((0, math.cos(LEAN_R), -math.sin(LEAN_R)))   # axe du torse (de l'avant vers l'arrière, descend)
TD = Vector((0, math.sin(LEAN_R), math.cos(LEAN_R)))    # dessus du torse
TS = Vector((1, 0, 0))
TR = seg_matrix(TT, TD, TS)                      # repère du torse

def tp(u, x=0.0, z=0.0):
    """Point du torse : u = -0.5 (poitrail) à +0.5 (bassin), x = côté, z = hauteur (dos > 0)."""
    return CEN + TT * (u * TL) + TS * x + TD * z

def LR(rx=0, ry=0, rz=0):
    """Rotation locale au torse (degrés), pour des pièces posées sur le dos et les flancs."""
    return TR @ Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_matrix()

NECK_BASE = tp(-0.44, 0, BH * 0.22)
NECK_TOP = NECK_BASE + Vector((0, -NECK_LEAN, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.15 * HEAD_SCALE, 0.4 * HEAD_SCALE))
HEAD_PITCH = 12                                  # degrés : la tête regarde un peu vers le bas
TAIL_START = tp(0.47, 0, -BH * 0.05)

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
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, os)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def limb(name, p1, p2, w, d, mat, parent, bevel=0.0, wedge_top=None, up=(0, 0, 1)):
    """Bloc entre deux points : largeur w (X local), profondeur d (Z local). wedge_top = rétrécissement du dessus."""
    p1, p2 = Vector(p1), Vector(p2)
    v = p2 - p1
    if wedge_top:
        return place(name, wedge_mesh(w, v.length, d, wedge_top, wedge_top, 0), mat, (p1 + p2) / 2, basis(v, up), parent, bevel)
    return place(name, box_mesh(w, v.length, d), mat, (p1 + p2) / 2, basis(v, up), parent, bevel)

def lava_line(name, loc, length, rot, parent, w=0.07, t=0.05):
    """Fine fissure de lave posée sur une plaque de basalte."""
    return box(name, (w * SC, length, t * SC), loc, rot, M_LAVA, parent, 0)

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

# Crâne, museau, arête du museau, mâchoire dorée distincte, menton, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.3 * SNOUT_K, 0.98), (0, -0.6 - 1.12 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.93, top_y=0.95, shift_y=-0.08, bevel=0.08)
hbox("SnoutBridge", (0.95, 1.9 * SNOUT_K, 0.14), (0, -0.6 - 1.0 * SNOUT_K, 0.24), mat=M_FL1)
hbox("Jaw", (1.4, 2.1 * SNOUT_K, 0.34), (0, -0.55 - 1.0 * SNOUT_K, -0.8), mat=M_CREAM, bevel=0.03)
hbox("Chin", (1.15, 0.9, 0.42), (0, -0.6 - 2.1 * SNOUT_K + 0.35, -0.94), mat=M_CREAM, bevel=0.04)
hbox("MouthLine", (1.6, 2.0 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.7), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.3 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.07), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.22), mat=M_BLACK)
    hbox(f"NostrilGlow_{sgn}", (0.1, 0.1, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.25), mat=M_LAVA)

# Yeux : blanc, iris brillant, pupille (ronde + reflets pour bébé, fendue pour ado / adulte), sourcils
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 1.0, 1.05, 0.78, 0.9, 0.46, 0.64
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.62, 0.44, 0.52, 0.1, 0.5
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.07, ey - 0.17, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.11, 0.11), (sgn * 1.07, ey + 0.13, ez - 0.22), mat=M_WHITE)
        hbox(f"Brow_{sgn}", (0.12, 0.8, 0.14), (sgn * 0.97, ey - 0.02, ez + 0.66), rot=(8, 0, 0), mat=M_ROCK)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.24), (sgn * 0.97, ey - 0.05, ez + 0.5), rot=(16, 0, 0), mat=M_ROCK, bevel=0.02)

# Braises sur les joues (signe distinctif, petits points lumineux)
for sgn in (-1, 1):
    for k in range(CHEEK_EMBERS):
        hbox(f"Ember_{sgn}_{k}", (0.06, 0.2 - 0.03 * k, 0.2 - 0.03 * k), (sgn * 0.97, 0.35 + 0.35 * k, -0.28 - 0.18 * k), mat=M_LAVA)

# Crocs (ado : petits ; adulte : 3 par côté)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.55 + k * 0.5
        hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1), M_CLAW, up=(1, 0, 0))

# Pointes de basalte le long de la mâchoire et des joues
for sgn in (-1, 1):
    for k in range(CHEEK_SPIKES):
        hshard(f"Cheek_{sgn}_{k}", 0.42, 0.14, 0.9 - 0.1 * k, (sgn * 0.9, -0.1 + k * 0.4, -0.5 - k * 0.12),
               (sgn * 0.9, 0.8, -0.3), M_ROCK if k % 2 == 0 else M_ROCK2, up=(sgn, 0, 0))
    # petites oreilles-flammes
    hshard(f"Ear_{sgn}", 0.55, 0.1, 1.0, (sgn * 0.85, 0.45, 0.35), (sgn * 1, 0.7, 0.35), M_FL1)

# Crinière de flammes derrière le crâne : anneaux de lames orange, jaune et cœur chaud
#   Les flammes montent (comme sur le concept) : direction surtout vers +Z, un peu vers l'arrière.
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-120 + k * (240 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.8, 0.6 + ring_i * 0.3, rad.z * 0.7)
        jit = Vector((random.uniform(-0.12, 0.12), random.uniform(0, 0.15), random.uniform(-0.1, 0.1)))
        direction = rad * 0.55 + Vector((0, 0.45 + 0.25 * ring_i, 1.0)) + jit
        hshard(f"Mane_{ring_i}_{k}", 0.6 - ring_i * 0.08, 0.12, (1.1 + 0.35 * abs(math.cos(ang)) + random.random() * 0.4) * FLAME_K,
               loc, direction, pick(FLAMES, [4 - 2 * ring_i, 3, 2 + ring_i]), up=tuple(rad))
# Flamme centrale (signe distinctif) : 3 grandes lames dressées sur le sommet du crâne
for k, (dx, ln, col) in enumerate(((0, 2.6, M_FL2), (-0.38, 1.9, M_FL1), (0.38, 1.9, M_FL1))):
    hshard(f"CrownFlame_{k}", 0.62 if k == 0 else 0.48, 0.14, ln * FLAME_K, (dx, 0.15, 0.78), (dx * 0.4, 0.28, 1), col, up=(1, 0, 0))
hshard("CrownCore", 0.3, 0.1, 1.5 * FLAME_K, (0, 0.1, 0.8), (0, 0.2, 1), M_FL3, up=(1, 0, 0))

# Cornes de basalte recourbées vers l'arrière (bébé : courtes ; ado : moyennes ; adulte : longues + pointe)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.05, 0.7), (sgn * 0.85, 0.2, 1.1), (sgn * 0.8, 0.65, 1.45)], 0.34, 0.13, M_ROCK)
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.1, 0.72), (sgn * 0.95, 0.3, 1.25), (sgn * 1.0, 0.8, 1.8), (sgn * 0.8, 1.4, 2.05)], 0.38, 0.14, M_ROCK)
    else:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.1, 0.72), (sgn * 1.0, 0.35, 1.35), (sgn * 1.2, 0.95, 2.0), (sgn * 1.0, 1.7, 2.45)], 0.42, 0.15, M_ROCK)
        hchain(f"HornB_{sgn}", [(sgn * 0.9, 0.5, 0.2), (sgn * 1.35, 0.85, 0.35), (sgn * 1.55, 1.4, 0.2)], 0.3, 0.12, M_ROCK2)
        hshard(f"HornTip_{sgn}", 0.2, 0.18, 0.6, (sgn * 1.0, 1.7, 2.45), (sgn * -0.3, 0.8, -0.1), M_CLAW)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs inclinés, cou en plaques, ventre, flancs, plaques de basalte, épaulières
# ----------------------------------------------------------
BEV = 0.10 * SC
def torso_block(kind, name, u, ln, hgt, mat, **kw):
    loc = tp(u, 0, 0)
    if kind == "wedge":
        return place(f"Body_{name}", wedge_mesh(BW * kw.get("w", 1.0), TL * ln, hgt, kw.get("tx", 0.9), kw.get("ty", 0.9), kw.get("sy", 0.0)),
                     mat, loc, TR, body_root, kw.get("bev", BEV))
    return place(f"Body_{name}", box_mesh(BW * kw.get("w", 1.0), TL * ln, hgt), mat, loc, TR, body_root, kw.get("bev", BEV))

torso_block("wedge", "Chest", -0.27, 0.46, BH, M_BODY, w=1.08, tx=0.88, ty=0.9, sy=-TL * 0.02)
torso_block("box", "Mid", 0.02, 0.38, BH * 0.95, M_BODY, w=0.98, bev=BEV * 0.8)
torso_block("wedge", "Pelvis", 0.29, 0.44, BH * 0.98, M_BODY, w=0.98, tx=0.9, ty=0.88, sy=TL * 0.02)

def half_w(u):
    return BW * (0.52 - 0.05 * (u + 0.5))

# Plastron doré + plaques de ventre séparées
place("Body_Plastron", box_mesh(BW * 0.84, 0.36 * SC, BH * 0.74), M_CREAM, tp(-0.5, 0, -BH * 0.1), TR, body_root, 0.05 * SC)
for i in range(BELLY_N):
    u = -0.42 + 0.84 * (i + 0.5) / BELLY_N
    pl = TL * 0.84 / BELLY_N * 0.86
    place(f"Body_Belly_{i}", box_mesh(BW * 0.8, pl, 0.2 * SC), M_CREAM, tp(u, 0, -BH / 2 + 0.03), TR, body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            place(f"Body_BellySide_{i}_{sgn}", box_mesh(0.1 * SC, pl, BH * 0.3), M_CREAM,
                  tp(u, sgn * (half_w(u) - 0.01), -BH * 0.3), TR, body_root)

# Écailles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            u = -0.38 + 0.78 * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = BH * (0.26 - 0.18 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, tp(u, sgn * (half_w(u) - 0.03 * SC), z),
                  TT + TS * sgn * 0.3 - TD * 0.1, pick([M_BODY2, M_BODY2, M_DARK]), body_root, up=(sgn, 0, 0))

# Plaques de basalte sur le dos, avec fissures de lave et pointes
for k in range(BACK_PLATES):
    u = -0.36 + 0.72 * k / max(1, BACK_PLATES - 1)
    ln = TL * 0.72 / BACK_PLATES * 0.9
    wdt = BW * (0.52 - 0.12 * abs(u))
    place(f"Body_BackPlate_{k}", wedge_mesh(wdt, ln, 0.34 * SC, 0.85, 0.85, 0), M_ROCK if k % 2 == 0 else M_ROCK2,
          tp(u, 0, BH / 2 + 0.03), TR, body_root, 0.04 * SC)
    if LAVA_CRACKS:
        lava_line(f"Body_BackCrack_{k}", tp(u, 0, BH / 2 + 0.2 * SC), ln * 0.85, LR(0, 0, (22 if k % 2 else -22)), body_root)
    shard(f"Body_BackSpike_{k}", 0.55 * SC, 0.2 * SC, (0.8 + 0.3 * math.sin(k)) * SC, tp(u, 0, BH / 2 + 0.2 * SC),
          TD * 1.0 + TT * 0.55, M_ROCK, body_root, up=(1, 0, 0))

# Blocs de basalte sur les flancs, chacun avec une fissure de lave (armure du concept)
for sgn in (-1, 1):
    for k in range(FLANK_ROCKS):
        u = -0.3 + 0.62 * k / max(1, FLANK_ROCKS - 1)
        z = BH * (0.02 + 0.14 * (k % 2))
        off = half_w(u) + 0.04 * SC
        place(f"Body_FlankRock_{sgn}_{k}", wedge_mesh(BH * 0.4, TL * 0.15, 0.26 * SC, 0.82, 0.82, 0), M_ROCK if k % 2 == 0 else M_ROCK2,
              tp(u, sgn * off, z), LR(0, sgn * 90, 0), body_root, 0.03 * SC)
        if LAVA_CRACKS:
            lava_line(f"Body_FlankCrack_{sgn}_{k}", tp(u, sgn * (off + 0.13 * SC), z), TL * 0.12,
                      LR(0, sgn * 90, 0) @ Euler((0, 0, math.radians(30 if k % 2 else -30))).to_matrix(), body_root)

# Braises : petits points lumineux sur flancs et dos
for k in range(EMBERS):
    u = random.uniform(-0.38, 0.4)
    sgn = random.choice((-1, 1))
    s = random.uniform(0.1, 0.2) * SC
    if k % 3 == 0:
        place(f"Body_Ember_{k}", box_mesh(s, s * 1.3, 0.05), M_LAVA, tp(u, random.uniform(-0.3, 0.3) * BW, BH / 2 + 0.06 * SC), TR, body_root)
    else:
        place(f"Body_Ember_{k}", box_mesh(0.05, s * 1.3, s), M_LAVA, tp(u, sgn * (half_w(u) + 0.0), BH * random.uniform(-0.1, 0.3)), TR, body_root)

# Cou en S : un maillon rouge + une plaque dorée devant + plaque de basalte de côté
NECK_CTRL = []
for tt in (1.0, 0.66, 0.33, 0.0):             # de la tête vers le torse
    u = 1 - tt                                 # 0 = base, 1 = tête
    y = NECK_BASE.y - NECK_LEAN * (u ** 1.6) + 0.22 * NECK_LEAN * math.sin(math.pi * u)
    NECK_CTRL.append(Vector((0, y, NECK_BASE.z + NECK_L * u)))
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_L * 1.05) / NECK_N)
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
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.24 * SC), mid - d * (r * 0.95), R, M_CREAM, body_root)
    if NECK_ROCK:
        shard(f"Body_NeckSpike_{i}", 0.6 * SC, 0.2 * SC, 0.9 * SC, mid + d * r * 0.9, d + t * 0.5, M_ROCK, body_root, up=tuple(side))
        for sgn in (-1, 1):
            if i % 2 == 0 or IS_ADULTE:
                place(f"Body_NeckRock_{i}_{sgn}", box_mesh(0.18 * SC, Ln * 0.8, 2 * r * 0.55), M_ROCK if i % 2 == 0 else M_ROCK2,
                      mid + side * sgn * (r * 0.98), R, body_root)
                if LAVA_CRACKS and i % 2 == 0:
                    place(f"Body_NeckCrack_{i}_{sgn}", box_mesh(0.05 * SC, Ln * 0.5, 0.06 * SC), M_LAVA,
                          mid + side * sgn * (r * 0.98 + 0.1 * SC) + d * 0.1, R @ Euler((0, math.radians(sgn * 30), 0)).to_matrix(), body_root)

# Épaulières de basalte avec fissures et pointes
for sgn in (-1, 1):
    if PAULDRON:
        place(f"Body_Pauldron_{sgn}", wedge_mesh(BW * 0.44, TL * 0.26, 0.62 * SC + 0.2, 0.8, 0.85, 0), M_ROCK,
              tp(-0.24, sgn * BW * 0.5, BH * 0.3), LR(0, sgn * 18, 0), body_root, 0.05 * SC)
        if LAVA_CRACKS:
            lava_line(f"Body_PauldronCrack_{sgn}", tp(-0.24, sgn * BW * 0.52, BH * 0.3 + 0.3 * SC), TL * 0.2, LR(0, sgn * 18, sgn * 25), body_root)
        for k in range(PAULDRON):
            shard(f"Body_PauldronSpike_{sgn}_{k}", 0.4 * SC, 0.16 * SC, (0.9 - 0.15 * k) * SC,
                  tp(-0.3 + 0.07 * k, sgn * BW * (0.5 + 0.02 * k), BH * (0.4 + 0.02 * k)), (sgn * 1.0, 0.5 + 0.3 * k, 0.8), M_ROCK2 if k % 2 else M_ROCK,
                  body_root, up=(0, 0, 1))

# ----------------------------------------------------------
# 11. PATTES : 2 pattes arrière puissantes (cuisse en wedge, jambe, genouillère, pied, 3 doigts + 3 griffes)
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.2)
FOOT_L = LEG_H * 0.62
LEG_TH = BW * 0.46
LEG_Y_U = 0.2                                  # position du bassin où s'attachent les hanches
for sgn in (-1, 1):
    th = LEG_TH
    hp = tp(LEG_Y_U, sgn * (BW * 0.5 - th * 0.1), -BH * 0.12)
    HZ = hp.z
    hip = Vector((hp.x, hp.y, HZ))
    knee = Vector((hip.x + sgn * th * 0.08, hip.y - LEG_H * 0.3, HZ * 0.5))
    ankle = Vector((hip.x, hip.y + LEG_H * 0.12, FOOT_H * 1.1 + HZ * 0.14))
    fy = ankle.y + th * 0.45 - FOOT_L / 2        # centre du pied
    # hanche musclée + cuisse en wedge
    wedge(f"Legs_{sgn}_Hip", (th * 1.5, th * 1.9, th * 1.5), hip + Vector((sgn * 0.05 * th, 0.05, 0.1)), None, M_BODY, legs_root,
          top_x=0.85, top_y=0.85, bevel=0.08 * SC)
    limb(f"Legs_{sgn}_Thigh", hip, knee, th * 1.3, th * 1.55, M_BODY, legs_root, bevel=0.08 * SC, wedge_top=0.82)
    box(f"Legs_{sgn}_Knee", (th * 1.0, th * 0.9, th * 0.9), knee + Vector((0, 0.05, 0)), None, M_BODY2, legs_root, bevel=0.05 * SC)
    place(f"Legs_{sgn}_KneePlate", wedge_mesh(th * 0.95, th * 0.8, 0.28 * SC + 0.1, 0.8, 0.8, 0), M_ROCK,
          knee + Vector((sgn * th * 0.03, -th * 0.5, 0)), basis((0, -1, 0.1), (0, 0, 1)), legs_root, 0.04 * SC)
    limb(f"Legs_{sgn}_Shin", knee, ankle, th * 0.88, th * 0.95, M_BODY2, legs_root, bevel=LEG_BEV * 0.05 * SC)
    # jambière de basalte + fissure de lave
    sh_mid = knee.lerp(ankle, 0.55)
    limb(f"Legs_{sgn}_Greave", knee.lerp(ankle, 0.3), knee.lerp(ankle, 0.82), th * 1.02, th * 1.08, M_ROCK, legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"Legs_{sgn}_GreaveTop", (th * 1.1, th * 1.14, 0.1 * SC), knee.lerp(ankle, 0.28), None, M_ROCK2, legs_root)
    if LAVA_CRACKS:
        B(f"Legs_{sgn}_GreaveCrack", (th * 0.5, 0.06 * SC, 0.08 * SC), sh_mid + Vector((0, -th * 0.56, 0)), (0, sgn * 28, 0), M_LAVA, legs_root)
    # pied plat, talon, 3 doigts + 3 griffes
    box(f"Legs_{sgn}_Foot", (th * 1.15, FOOT_L, FOOT_H), (hip.x, fy, FOOT_H / 2), None, M_BODY, legs_root, bevel=0.06 * SC)
    link(f"Legs_{sgn}_Heel", (hip.x, ankle.y, ankle.z), (hip.x, fy + FOOT_L * 0.3, FOOT_H * 0.8), th * 0.75, M_BODY, legs_root, bevel=0, extra=0.1)
    toe_y = fy - FOOT_L / 2 - th * 0.15
    for k in (-1, 0, 1):
        B(f"Legs_{sgn}_Toe_{k}", (th * 0.3, th * 0.5, FOOT_H * 0.75), (hip.x + k * th * 0.34, toe_y, FOOT_H * 0.38), None, M_BODY2, legs_root)
        shard(f"Legs_{sgn}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, (hip.x + k * th * 0.34, toe_y - th * 0.2, FOOT_H * 0.3),
              (k * 0.12, -1, -0.2), M_CLAW, legs_root)
    # plaque de basalte sur l'extérieur de la cuisse + fissure de lave (comme sur le concept)
    if THIGH_ROCK:
        th_mid = hip.lerp(knee, 0.45)
        th_dir = knee - hip
        place(f"Legs_{sgn}_ThighRock", wedge_mesh(th * 0.95, th_dir.length * 0.75, 0.3 * SC + 0.1, 0.8, 0.85, 0), M_ROCK,
              th_mid + Vector((sgn * th * 0.62, 0, 0)), basis(th_dir, (sgn, 0, 0)), legs_root, 0.04 * SC)
        if LAVA_CRACKS:
            B(f"Legs_{sgn}_ThighCrack", (0.08 * SC, th * 0.7, 0.07 * SC), th_mid + Vector((sgn * (th * 0.62 + 0.15 * SC + 0.05), 0, 0)),
              basis(th_dir, (sgn, 0, 0)) @ Euler((0, 0, math.radians(sgn * 25))).to_matrix(), M_LAVA, legs_root)
    # braises sur la cuisse
    for k in range(THIGH_EMBERS):
        B(f"Legs_{sgn}_Ember_{k}", (0.06, 0.2 * SC, 0.22 * SC), hip.lerp(knee, 0.3 + 0.25 * k) + Vector((sgn * th * 0.68, 0.0, 0.0)), None, M_LAVA, legs_root)

# ----------------------------------------------------------
# 12. AILES-BRAS (wyvern) : le poignet pose presque au sol, les doigts montent vers l'arrière
# ----------------------------------------------------------
WSP = WING_SPAN
for sgn in (-1, 1):
    # épaule sur le haut du poitrail -> coude remonté vers l'arrière -> poignet posé devant, près du sol
    root = tp(-0.22, sgn * BW * 0.42, BH * 0.28)
    elbow = Vector((sgn * (BW * 0.5 + WSP * 0.16), root.y + WSP * 0.16, root.z + WSP * 0.1))
    wrist = Vector((sgn * (BW * 0.5 + WSP * 0.22), root.y - WSP * 0.12, WRIST_Z))
    bar(f"Wings_{sgn}_Arm", root, elbow, WING_BONE * 1.4, M_DARK, wings_root, up=(0, 1, 0))
    bar(f"Wings_{sgn}_Fore", elbow, wrist, WING_BONE * 1.15, M_DARK, wings_root, up=(0, 1, 0))
    place(f"Wings_{sgn}_WristPad", box_mesh(WING_BONE * 2.2, WING_BONE * 2.4, WING_BONE * 2.0), M_ROCK, wrist, None, wings_root, 0.03 * SC)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        # doigts repliés : ils montent haut au-dessus du dos puis s'ouvrent vers l'arrière (éventail)
        tip = wrist + Vector((sgn * WSP * (0.2 + 0.12 * math.sin(math.pi * f)), WSP * (0.3 + 0.62 * f), WSP * (1.05 - 0.6 * f)))
        bar(f"Wings_{sgn}_Finger_{k}", wrist, tip, WING_BONE * (0.9 - 0.2 * f), M_DARK, wings_root, up=(0, 1, 0))
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.5, WING_BONE * 1.3, WSP * 0.14, tip, tip - wrist, M_ROCK, wings_root)
        tips.append(tip)
    anchor = tp(0.2, sgn * BW * 0.44, BH * 0.1)
    ring_pts = [wrist] + tips + [anchor, root]
    for k in range(len(ring_pts) - 2):
        a, b = ring_pts[k + 1], ring_pts[k + 2]
        plate(f"Wings_{sgn}_Memb_{k}", [wrist, a, b], WING_BONE * 0.4, M_WING if k % 2 == 0 else M_WING2, wings_root)
        if WING_FACETS:
            c = (wrist + a + b) / 3
            plate(f"Wings_{sgn}_Facet_{k}", [c.lerp(wrist, 0.45), c.lerp(a, 0.6), c.lerp(b, 0.6)], WING_BONE * 0.55,
                  M_WING2 if k % 2 == 0 else M_FL1, wings_root)
    # griffe du pouce, posée au sol
    shard(f"Wings_{sgn}_ThumbClaw", WING_BONE * 1.1, WING_BONE * 0.9, WSP * 0.17, wrist, (sgn * 0.2, -0.7, -0.8), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques dorées, pointes de basalte, flamme finale
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.25, 0.0), (0.45, -0.6, 0.25), (0.7, -0.92, 0.1), (0.9, -0.95, -0.2), (1.0, -0.8, -0.3)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH)))
TAIL_R = [(0.0, BW * 0.4), (0.3, BW * 0.33), (0.6, BW * 0.24), (0.85, BW * 0.16), (1.0, BW * 0.11)]
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
    if i % 2 == 0 and s < 0.85:
        place(f"Tail_Rock_{i}", wedge_mesh(2 * r * 0.7, Ln * 1.1, 0.3 * SC, 0.8, 0.8, 0), M_ROCK if i % 4 == 0 else M_ROCK2,
              mid + d * (r * 0.95), R, tail_root)
    shard(f"Tail_Spike_{i}", 0.7 * r + 0.15, 0.14 * SC, 0.45 * SC + r * 0.7, mid + d * r * 0.95, d + t * 0.7, M_ROCK, tail_root, up=(1, 0, 0))
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_DARK]), tail_root, up=(sgn, 0, 0))
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
place("Tail_TipRing", box_mesh(BW * 0.26, 0.34 * SC, BW * 0.26), M_ROCK, tip, seg_matrix(tt_, td_, ts_), tail_root)
# Flamme au bout de la queue (signe distinctif) : lames dressées orange, jaune, chaudes
for k in range(TAIL_FLAMES):
    a = k * 2 * math.pi / max(1, TAIL_FLAMES - 1) if k else 0
    off = ts_ * math.cos(a) * 0.5 + td_ * math.sin(a) * 0.5 if k else Vector()
    dirv = Vector((0, 0.35, 1.0)) + off * 0.9 + tt_ * 0.2
    L_ = TAIL_FLAME_L * (1.0 if k == 0 else 0.62 + 0.25 * ((k * 7) % 3) / 2)
    shard(f"Tail_Flame_{k}", BW * (0.3 if k == 0 else 0.22), BW * 0.07, L_, tip + off * BW * 0.1, dirv,
          M_FL2 if k == 0 else FLAMES[k % 3], tail_root, up=tuple(ts_))
shard("Tail_FlameCore", BW * 0.14, BW * 0.05, TAIL_FLAME_L * 0.7, tip, (0, 0.3, 1), M_FL3, tail_root, up=tuple(ts_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, 5 familles de couleurs, aucune émission sauf yeux et braises discrètes.
#     Éléments flottants : petites braises (losanges jaunes et orange) qui s'élèvent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.2 if IS_ADO else 1.6))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WSP * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.8, top_z)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        base = p
        m = basis(dirv, (random.uniform(-1, 1), random.uniform(-1, 1), 1))
        fx, fy_ = m.col[0], m.col[1]
        sz = FX_SIZE * random.uniform(0.7, 1.3)
        plate(f"FX_Ember_{k}", [base, base + fy_ * 0.4 * sz + fx * 0.28 * sz, base + fy_ * sz, base + fy_ * 0.4 * sz - fx * 0.28 * sz],
              0.04 * SC, M_FL2 if k % 2 else M_FL1, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
