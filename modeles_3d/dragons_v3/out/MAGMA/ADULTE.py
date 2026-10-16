import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Magma · Adulte
#  Épique · Feu · Hydre · monde 2
#  - Adulte : TROIS têtes (la centrale plus grande, les latérales tournées vers l'extérieur), corps massif
#  - Roche volcanique en plaques séparées par des fentes de lave lumineuse, épaules et cuisses en wedge
#  - Cous en blocs de lave lumineux (gorges orange), gueules entrouvertes avec 3 crocs par côté
#  - Grandes cornes à pointe de lave + cornes de sourcil, crêtes de pics, 4 flammes par tête, petites ailes
#  - Épique complet : fissures, cœur de lave, plastron doré + gemme, bracelets dorés, braises et éclats en FX
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1114)            # même dragon à chaque exécution
TAG = "MAGMA_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 13000          # budget de triangles de ce stade et de cette rareté
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
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
LAVA_SKIN = False        # peau de lave orange (bébé) ou roche noire (ado / adulte)
ROCK_HOT = 1.2           # poids des plaques encore chaudes (rouge-orange) dans la roche
GLOW_STR = 3.0           # puissance de l'émission (fissures, cœur de lave, yeux)
GLOW_TIPS = True         # pointes de lave au bout des pics et des cornes
BW = 3.3                 # largeur du torse
BH = 2.7                 # hauteur du torse
LEG_H = 3.0              # hauteur des pattes
TORSO_L = 4.6            # longueur torse + bassin
NECK_L = 4.6             # hauteur du cou central
NECK_LEAN = 1.0          # avancée du cou vers l'avant
NECK_N = 5               # nombre de maillons par cou
NECK_R = (0.95, 0.74)    # rayon du cou : base, haut
NECK_CURVE = 0.8         # courbure en S des cous
NECK_SPIKE_EVERY = 1     # un pic de nuque tous les n maillons
NECK_SPIKE_K = 1.2
HEAD_SCALE = 1.05        # taille de la tête centrale
HEAD_PITCH = 6           # degrés : la tête regarde un peu vers le bas
# Têtes : (décalage X, décalage Y, décalage Z, échelle, rotation vers l'extérieur en degrés)
HEADS = [(0.0, 0.0, 0.0, 1.0, 0), (-3.0, 0.9, -2.0, 0.82, -26), (3.0, 0.9, -2.0, 0.82, 26)]
SNOUT_L = 1.45           # longueur du museau
JAW_OPEN = 9             # ouverture de la gueule (degrés)
FANGS = 3                # crocs par côté
HORN_L = 1.4             # longueur des cornes
EYE = (0.5, 0.45, 0.36, 0.38, 0.09, 0.34)    # blanc L/H, iris L/H, pupille L/H (fendue)
BROW_TILT = 20           # inclinaison des sourcils (sévérité)
HEAD_CREST = 4           # pics sur le crâne
CHEEK_N = 3              # pics de joue par côté
HEAD_CRACKS = 2          # fissures en zigzag par côté de tête
FLAME_N = 4              # flammes sur chaque tête
FLAME_H = 1.7
BODY_CELL = 0.85         # taille des plaques de roche du corps
BELLY_N = 6              # plaques de ventre
CREST_N = 7              # plaques de crête dorsale
CREST_H = 1.5
FLANK_CRACKS = 4         # fissures par flanc
BRACER_K = 0.45          # hauteur du bracelet (part du tibia)
CLAW_K = 0.6             # longueur des griffes
THIGH_SPIKES = 2         # pics sur chaque cuisse
WING_SPAN = 4.8          # envergure d'UNE aile (petites ailes d'hydre)
WING_LIFT = 0.65
WING_SWEEP = 0.4
WING_FINGERS = 4
WING_BONE = 0.28
WING_VEINS = 2
TAIL_L = 6.0             # longueur de la queue
TAIL_STEP = 0.7          # pas des segments de queue
TAIL_PATCHES = True      # fissures sur les côtés de la queue
TAIL_TIP = 1.3           # taille des pics du bout de queue
TAIL_TIP_SPIKES = 4
FX_N = 14                # nombre de braises / éclats flottants
FX_SIZE = 0.4

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Roche noire volcanique, lave orange (peau, ventre, gorges), fissures et cœur de lave
#    jaune-orange émissifs, flammes, petits ornements dorés (Épique).
#    Le bébé est surtout en peau de lave orange avec des taches de roche noire ;
#    l'ado et l'adulte sont en roche noire, la lave ne se voit plus que dans les fissures et les cous.
# ----------------------------------------------------------
M_ROCK  = get_mat("Rock",      "#2B2320", 0.70)   # roche noire principale
M_ROCK2 = get_mat("RockDark",  "#1A1513", 0.75)   # roche sombre (strates, ombres, sourcils)
M_ROCK3 = get_mat("RockWarm",  "#3D2A22", 0.70)   # roche chaude (variation des plaques)
M_SKIN  = get_mat("LavaSkin",  "#F2661B", 0.50)   # peau de lave orange (bébé surtout)
M_SKIN2 = get_mat("LavaDeep",  "#D9471E", 0.50)   # lave rouge-orange (variation, cornes)
M_BELLY = get_mat("Belly",     "#F28C1E", 0.50)   # ventre en plaques, gorges, plastron
M_GLOW  = get_mat("LavaGlow",  "#FFA41E", 0.40, emission="#FF8A12", strength=GLOW_STR)        # fissures
M_CORE  = get_mat("LavaCore",  "#FFC233", 0.35, emission="#FFB020", strength=GLOW_STR)        # cœur de lave
M_FLAME = get_mat("Flame",     "#FFD24A", 0.40, emission="#FFB21E", strength=GLOW_STR + 0.5)  # flammes jaunes
M_FLAM2 = get_mat("FlameRed",  "#FF5A12", 0.40, emission="#FF4A0A", strength=GLOW_STR + 0.5)  # flammes rouges
M_IRIS  = get_mat("Iris",      "#FF8A12", 0.25, emission="#FF8A12", strength=GLOW_STR)        # iris lumineux
M_WHITE = get_mat("EyeWhite",  "#F2F2F2", 0.30)
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles, narines
M_CLAW  = get_mat("Claw",      "#4A3C38", 0.35)   # griffes en obsidienne
M_FANG  = get_mat("Fang",      "#FFE6B8", 0.35)   # crocs
M_GOLD  = get_mat("Gold",      "#F2B233", 0.30, metallic=0.9)   # ornements dorés (Épique)
M_MEMB  = get_mat("Membrane",  "#E0521B", 0.55)   # membrane des ailes
FLAMES = [M_FLAME, M_FLAM2]

# Matériaux des plaques selon le stade : le bébé est en peau de lave orange avec des taches de roche noire,
# l'ado et l'adulte sont en roche noire avec quelques plaques encore chaudes.
if LAVA_SKIN:
    BODY_MATS, BODY_W = [M_SKIN, M_SKIN2, M_ROCK], [5, 3, 2]
    HEAD_MATS, HEAD_W = [M_SKIN, M_SKIN2, M_ROCK], [6, 3, 1.5]
    NECK_FRONT, TOE_MAT, TAIL_PATCH_MAT = M_SKIN, M_SKIN2, M_ROCK
else:
    BODY_MATS, BODY_W = [M_ROCK, M_ROCK2, M_ROCK3, M_SKIN2], [5, 3, 3, ROCK_HOT]
    HEAD_MATS, HEAD_W = [M_ROCK, M_ROCK2, M_ROCK3], [5, 2, 2]
    NECK_FRONT, TOE_MAT, TAIL_PATCH_MAT = M_CORE, M_ROCK2, M_GLOW

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.0                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_TOP = Vector((0, -TL * 0.42 - NECK_LEAN, ZC + BH * 0.35 + NECK_L))   # sommet du cou central
TAIL_START = Vector((0, TL * 0.45, ZC - 0.05 * BH))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master) if WING_SPAN > 0 else None

# Une tête par entrée de HEADS : HEAD_ROOT (centrale / principale), HEAD2_ROOT, HEAD3_ROOT
HEAD_ROOT_NAMES = ["HEAD_ROOT", "HEAD2_ROOT", "HEAD3_ROOT"]
head_roots = []
for k, (hx, hdy, hdz, hsc, hyaw) in enumerate(HEADS):
    pos = NECK_TOP + Vector((hx, hdy, hdz))
    mtx = (Matrix.Translation(pos) @ Euler((0, 0, math.radians(hyaw))).to_matrix().to_4x4()
           @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
    head_roots.append(empty(HEAD_ROOT_NAMES[k], master, mtx))

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, os)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def rock_block(name, size, loc, rot=None, parent=None, cell=0.8, mats=None, weights=None,
               gap=0.07, thick=0.16, bottom=False, core=None):
    """SIGNE DISTINCTIF : bloc de roche fissurée. Un noyau de lave lumineux (M_CORE) recouvert de plaques
    séparées par de fines fentes : la lave brille entre les plaques. 'cell' = taille visée d'une plaque."""
    sx, sy, sz = size
    R = Matrix.Identity(3) if rot is None else (rot.to_3x3() if isinstance(rot, Matrix)
                                                else Euler([math.radians(a) for a in rot]).to_matrix())
    loc = Vector(loc)
    mats = mats or BODY_MATS
    weights = weights or BODY_W
    B(name + "_Core", (sx * 0.96, sy * 0.96, sz * 0.96), loc, R, core or M_CORE, parent)
    dims = (sx, sy, sz)
    for a in range(3):
        for sgn in (-1, 1):
            if a == 2 and sgn == -1 and not bottom:
                continue
            u, v = [i for i in range(3) if i != a]
            nu = max(1, round(dims[u] / cell))
            nv = max(1, round(dims[v] / cell))
            du, dv = dims[u] / nu, dims[v] / nv
            for i in range(nu):
                for j in range(nv):
                    t = thick * random.uniform(0.7, 1.3)
                    c = [0.0, 0.0, 0.0]
                    c[a] = sgn * (dims[a] / 2 - thick * 0.35 + t * 0.5)
                    c[u] = -dims[u] / 2 + du * (i + 0.5) + random.uniform(-0.04, 0.04) * du
                    c[v] = -dims[v] / 2 + dv * (j + 0.5) + random.uniform(-0.04, 0.04) * dv
                    s = [0.0, 0.0, 0.0]
                    s[a] = t
                    s[u] = du - gap * random.uniform(0.8, 1.3)
                    s[v] = dv - gap * random.uniform(0.8, 1.3)
                    tilt = Euler([math.radians(random.uniform(-3, 3)) for _ in range(3)]).to_matrix()
                    B(f"{name}_P{a}{'p' if sgn > 0 else 'm'}_{i}_{j}", tuple(s), loc + R @ Vector(c), R @ tilt,
                      pick(mats, weights), parent)

def crack(name, p0, steps, parent, th=0.06, depth=0.05):
    """Fissure de lave en zigzag (barres fines émissives) : p0 puis une suite de déplacements."""
    p = Vector(p0)
    for i, st in enumerate(steps):
        q = p + Vector(st)
        bar(f"{name}_{i}", p, q, th, M_GLOW, parent, depth=depth)
        p = q

def spike(name, base, direction, w, L, parent, up=(1, 0, 0), glow_tip=True, mat=None):
    """Pic de roche ; à partir de l'ado, sa pointe rougeoie (éclat de lave au bout)."""
    d = Vector(direction).normalized()
    shard(name, w, w * 0.6, L, base, d, mat or M_ROCK, parent, up=up)
    if glow_tip and GLOW_TIPS:
        shard(name + "_Tip", w * 0.45, w * 0.3, L * 0.35, Vector(base) + d * (L * 0.68), d, M_GLOW, parent, up=up)

def flame(name, base, h, w, parent, lean=(0, 0.25, 1)):
    """Petite flamme : 2 éclats croisés (jaune + rouge) qui montent."""
    lean = Vector(lean)
    shard(name + "_A", w, w * 0.35, h, base, lean, pick(FLAMES, [3, 2]), parent, up=(0, 1, 0))
    shard(name + "_B", w * 0.7, w * 0.3, h * 0.7, base, lean + Vector((0.3, 0, 0)), M_FLAM2, parent, up=(1, 0, 0))

# ----------------------------------------------------------
# 9. TÊTES : une fonction construit une tête complète dans les coordonnées locales de son root.
#    Elle est appelée pour HEAD_ROOT (tête principale), puis HEAD2_ROOT et HEAD3_ROOT.
# ----------------------------------------------------------
def build_head(H, k, hs):
    """Tête n° k (1 = principale) en coordonnées locales de l'empty H, à l'échelle hs."""
    P = f"Head{k}_"
    def hv(v):
        return tuple(c * hs for c in v)
    def hb(name, size, loc, rot=None, mat=None, bevel=0.0):
        return box(P + name, hv(size), hv(loc), rot, mat, H, bevel * hs)
    SNOUT_FRONT = -0.85 - SNOUT_L

    # Crâne et museau en roche fissurée (noyau de lave + plaques), arête du museau
    rock_block(P + "Skull", hv((1.9, 1.75, 1.6)), (0, 0, 0), None, H, cell=0.8 * hs,
               mats=HEAD_MATS, weights=HEAD_W, gap=0.06 * hs, thick=0.14 * hs, bottom=True)
    rock_block(P + "Snout", hv((1.5, SNOUT_L + 0.3, 0.8)), hv((0, -0.85 - SNOUT_L / 2 + 0.15, -0.3)), None, H,
               cell=0.75 * hs, mats=HEAD_MATS, weights=HEAD_W, gap=0.05 * hs, thick=0.12 * hs)
    hb("SnoutBridge", (0.75, SNOUT_L * 0.9, 0.16), (0, SNOUT_FRONT * 0.55 - 0.1, 0.16), mat=M_ROCK2)

    # Mâchoire distincte (entrouverte chez l'adulte) + gorge orange + ligne de bouche en lave
    jaw_rot = (-JAW_OPEN, 0, 0)
    hb("Jaw", (1.36, SNOUT_L + 0.5, 0.42), (0, -0.75 - SNOUT_L / 2 + 0.2, -0.86 - JAW_OPEN * 0.012), rot=jaw_rot,
       mat=HEAD_MATS[0], bevel=0.04)
    hb("Throat", (1.2, 1.1, 0.3), (0, 0.15, -0.88), mat=M_BELLY)
    hb("MouthGlow", (1.3, SNOUT_L + 0.3, 0.1 + JAW_OPEN * 0.012), (0, -0.85 - SNOUT_L / 2 + 0.2, -0.67), mat=M_GLOW)

    # Narines (avec une lueur de lave dès l'ado)
    for sgn in (-1, 1):
        hb(f"Nostril_{sgn}", (0.24, 0.2, 0.08), (sgn * 0.42, SNOUT_FRONT + 0.3, 0.13), mat=M_BLACK)
        if GLOW_TIPS:
            hb(f"NostrilGlow_{sgn}", (0.12, 0.1, 0.09), (sgn * 0.42, SNOUT_FRONT + 0.3, 0.135), mat=M_GLOW)

    # Yeux carrés sur l'avant des côtés : blanc, iris orange lumineux, pupille (ronde + reflets / fendue)
    for sgn in (-1, 1):
        ex, ey, ez = sgn * 0.97, -0.38, 0.12
        hb(f"EyeWhite_{sgn}", (0.1, EYE[0], EYE[1]), (ex, ey, ez), mat=M_WHITE)
        hb(f"Iris_{sgn}", (0.08, EYE[2], EYE[3]), (ex + sgn * 0.04, ey - 0.03, ez - 0.02), mat=M_IRIS)
        hb(f"Pupil_{sgn}", (0.07, EYE[4], EYE[5]), (ex + sgn * 0.08, ey - 0.04, ez - 0.03), mat=M_BLACK)
        if IS_BEBE:
            hb(f"Glint_{sgn}", (0.06, 0.18, 0.2), (ex + sgn * 0.11, ey - 0.17, ez + 0.2), mat=M_WHITE)
            hb(f"Glint2_{sgn}", (0.06, 0.09, 0.09), (ex + sgn * 0.11, ey + 0.1, ez - 0.2), mat=M_WHITE)
        # sourcil de roche : plat chez le bébé, incliné et sévère ensuite
        hb(f"Brow_{sgn}", (0.24, EYE[0] + 0.3, 0.24), (sgn * 0.93, ey - 0.05, ez + EYE[1] / 2 + 0.12),
           rot=(BROW_TILT, 0, sgn * -6), mat=M_ROCK2, bevel=0.02)

    # Crocs (ado : 2 par côté ; adulte : 3 par côté + crocs du bas)
    for sgn in (-1, 1):
        for f in range(FANGS):
            fy = SNOUT_FRONT + 0.35 + f * 0.45
            shard(f"{P}Fang_{sgn}_{f}", 0.18 * hs, 0.18 * hs, (0.34 + 0.06 * FANGS) * hs, hv((sgn * 0.55, fy, -0.68)),
                  (0, 0.05, -1), M_FANG, H, up=(1, 0, 0))
            if IS_ADULTE and f < 2:
                shard(f"{P}FangLow_{sgn}_{f}", 0.14 * hs, 0.14 * hs, 0.3 * hs, hv((sgn * 0.45, fy + 0.25, -0.75 - JAW_OPEN * 0.02)),
                      (0, 0.05, 1), M_FANG, H, up=(1, 0, 0))

    # Cornes de roche à pointe de lave, qui partent vers l'arrière
    for sgn in (-1, 1):
        if IS_BEBE:
            hb(f"Horn_{sgn}", (0.36, 0.36, 0.42), (sgn * 0.55, 0.3, 0.95), rot=(-15, sgn * 10, 0), mat=M_ROCK)
            hb(f"HornTip_{sgn}", (0.22, 0.22, 0.2), (sgn * 0.57, 0.36, 1.2), rot=(-15, sgn * 10, 0), mat=M_ROCK2)
        else:
            L = HORN_L
            pts = [(sgn * 0.6, 0.25, 0.7), (sgn * 0.82, 0.55, 0.7 + 0.45 * L), (sgn * 0.9, 0.55 + 0.55 * L, 0.7 + 0.8 * L),
                   (sgn * 0.85, 0.55 + 1.05 * L, 0.7 + 0.95 * L)]
            tchain(f"{P}Horn_{sgn}", [hv(p) for p in pts], 0.36 * hs, 0.18 * hs, M_ROCK, H)
            B(f"{P}HornRing_{sgn}", hv((0.44, 0.44, 0.12)), hv(pts[1]), basis(Vector(pts[1]) - Vector(pts[0]), (1, 0, 0)),
              M_SKIN2, H)
            tip_dir = Vector(pts[3]) - Vector(pts[2])
            shard(f"{P}HornTip_{sgn}", 0.22 * hs, 0.22 * hs, 0.55 * hs * L, hv(pts[3]), tip_dir, M_GLOW, H)
            # petite corne secondaire au-dessus de l'œil (adulte)
            if IS_ADULTE:
                spike(f"{P}BrowHorn_{sgn}", hv((sgn * 0.9, -0.2, 0.55)), (sgn * 0.4, 0.6, 0.9), 0.24 * hs, 0.75 * hs, H)

    # Crête de pics le long du milieu du crâne (vers l'arrière)
    for c in range(HEAD_CREST):
        y = -0.5 + c * 0.42
        spike(f"{P}Crest_{c}", hv((0, y, 0.72)), (0, 0.7, 1), (0.3 + 0.05 * (c % 2)) * hs, (0.6 + 0.12 * c) * hs, H,
              glow_tip=(c % 2 == 0))

    # Pics de joue / mâchoire, pointés vers l'arrière
    for sgn in (-1, 1):
        for c in range(CHEEK_N):
            spike(f"{P}Cheek_{sgn}_{c}", hv((sgn * 0.85, 0.2 + c * 0.25, -0.45 - c * 0.15)),
                  (sgn * 0.6, 1, -0.2 - 0.25 * c), 0.28 * hs, (0.7 - 0.1 * c) * hs, H, up=(0, 0, 1), glow_tip=False)

    # Fissures de lave sur les côtés du crâne (en plus des fentes entre plaques)
    for sgn in (-1, 1):
        for c in range(HEAD_CRACKS):
            crack(f"{P}Crack_{sgn}_{c}", hv((sgn * 0.985, 0.1 + 0.35 * c, 0.55 - 0.5 * c)),
                  [hv((0, 0.2, -0.25)), hv((0, -0.12, -0.22)), hv((0, 0.22, -0.2))], H, th=0.06 * hs, depth=0.04 * hs)

    # Flammes sur l'arrière du crâne (les 3 stades, plus hautes à l'adulte)
    for c in range(FLAME_N):
        fx = (c - (FLAME_N - 1) / 2) * 0.5
        flame(f"{P}Flame_{c}", hv((fx, 0.35 + 0.1 * (c % 2), 0.7)), FLAME_H * hs * random.uniform(0.75, 1.1),
              0.45 * hs, H, lean=(fx * 0.4, 0.45, 1))

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_head(H, k + 1, HEAD_SCALE * hd[3])

# ----------------------------------------------------------
# 10. CORPS : torse et bassin en roche fissurée, ventre en plaques orange, plastron, crête stratifiée,
#     cous en courbe Catmull-Rom (blocs de lave lumineux devant, plaques de roche derrière)
# ----------------------------------------------------------
rock_block("Body_Chest", (BW * 1.05, TL * 0.56, BH), (0, -TL * 0.2, ZC), None, body_root,
           cell=BODY_CELL, gap=0.08 * SC, thick=0.2 * SC)
rock_block("Body_Pelvis", (BW * 0.95, TL * 0.5, BH * 0.92), (0, TL * 0.25, ZC - 0.04 * BH), None, body_root,
           cell=BODY_CELL, gap=0.08 * SC, thick=0.2 * SC)

# Plaques de ventre orange bien séparées
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.84
    B(f"Body_Belly_{i}", (BW * 0.72, pl, 0.26 * SC), (0, y, ZC - BH * 0.47 - 0.06 * SC), mat=M_BELLY, parent=body_root)

# Poitrail : bandeau de roche sombre (bébé) ou plastron orange à bord doré et gemme de lave (ado / adulte)
PY = -TL * 0.48 - 0.1 * SC
if IS_BEBE:
    B("Body_ChestBand", (BW * 0.9, 0.3 * SC, BH * 0.42), (0, PY, ZC - BH * 0.18), mat=M_ROCK2, parent=body_root,
      bevel=0.04 * SC)
    for sgn in (-1, 1):
        B(f"Body_ChestStud_{sgn}", (0.18 * SC, 0.1 * SC, 0.18 * SC), (sgn * BW * 0.3, PY - 0.17 * SC, ZC - BH * 0.18),
          mat=M_GOLD, parent=body_root)
else:
    for r in range(3):
        B(f"Body_Plastron_{r}", (BW * (0.72 - 0.1 * r), 0.28 * SC, BH * 0.22), (0, PY, ZC + BH * (0.12 - 0.25 * r)),
          mat=M_BELLY, parent=body_root)
    B("Body_PlastronRim", (BW * 0.8, 0.2 * SC, 0.12 * SC), (0, PY + 0.06 * SC, ZC + BH * 0.27), mat=M_GOLD, parent=body_root)
    B("Body_GemSet", (0.55 * SC, 0.2 * SC, 0.55 * SC), (0, PY - 0.12 * SC, ZC - BH * 0.06), rot=(0, 45, 0), mat=M_GOLD,
      parent=body_root)
    crystal("Body_Gem", 0.24 * SC, 0.1 * SC, 0.22 * SC, (0, PY - 0.18 * SC, ZC - BH * 0.06), (0, -1, 0), M_CORE,
            body_root)

# Épaules musclées (adulte et ado) : blocs de roche en wedge avec fissures
if not IS_BEBE:
    for sgn in (-1, 1):
        wedge(f"Body_Shoulder_{sgn}", (BW * 0.42, TL * 0.36, BH * 0.62),
              (sgn * BW * 0.42, -TL * 0.3, ZC + BH * 0.2), (0, sgn * 12, 0), M_ROCK2, body_root,
              top_x=0.7, top_y=0.75, bevel=0.06 * SC)
        crack(f"Body_ShoulderCrack_{sgn}", (sgn * BW * 0.62, -TL * 0.42, ZC + BH * 0.35),
              [(0, 0.3 * SC, -0.3 * SC), (sgn * 0.02, 0.25 * SC, 0.12 * SC), (0, 0.3 * SC, -0.3 * SC)], body_root,
              th=0.07 * SC)

# Crête dorsale : plaques de roche stratifiée (2 strates) + pointe de lave
for c in range(CREST_N):
    y = -TL * 0.36 + (TL * 0.78) * c / max(1, CREST_N - 1)
    h = CREST_H * (1.0 - 0.35 * abs(c / max(1, CREST_N - 1) - 0.3))
    base = Vector((0, y, ZC + BH * 0.5 + 0.05 * SC))
    wedge(f"Body_Crest_{c}", (0.5 * SC, 0.7 * SC, h * 0.6), base + Vector((0, 0, h * 0.25)), (-12, 0, 0),
          pick([M_ROCK, M_ROCK2]), body_root, top_x=0.5, top_y=0.45, shift_y=0.1 * SC)
    spike(f"Body_CrestSpike_{c}", base + Vector((0, 0.05 * SC, h * 0.45)), (0, 0.45, 1), 0.36 * SC, h * 0.75, body_root)

# Fissures de lave sur les flancs
for sgn in (-1, 1):
    for c in range(FLANK_CRACKS):
        y0 = -TL * 0.4 + c * TL * 0.85 / max(1, FLANK_CRACKS)
        crack(f"Body_Crack_{sgn}_{c}", (sgn * BW * 0.535, y0, ZC + BH * random.uniform(0.0, 0.35)),
              [(0, 0.25 * SC, -0.3 * SC), (0, 0.2 * SC, 0.15 * SC), (0, 0.25 * SC, -0.35 * SC)], body_root,
              th=0.08 * SC)

# Cous : une courbe Catmull-Rom par tête, rééchantillonnée à pas constant
NECK_RADIUS_KEYS = [(0.0, NECK_R[0]), (1.0, NECK_R[1])]

def build_neck(k, H, hsc, hx):
    """Cou n° k : de la base sur le poitrail jusqu'à la base du crâne de la tête H."""
    hs = HEAD_SCALE * hsc
    end = H.matrix_basis @ Vector((0, 0.5 * hs, -0.55 * hs))           # base du crâne
    base = Vector((hx * 0.42, -TL * 0.36, ZC + BH * 0.22))
    ctrl = [base,
            base.lerp(end, 0.35) + Vector((hx * 0.05, 0.25 * NECK_CURVE, 0)),
            base.lerp(end, 0.7) + Vector((0, -0.15 * NECK_CURVE, 0)),
            end]
    spine = resample(sample_curve(ctrl), (end - base).length / NECK_N)
    n = len(spine) - 1
    for i in range(n):
        p1, p2 = spine[i], spine[i + 1]
        Ln = (p2 - p1).length
        mid = (p1 + p2) / 2
        s = (i + 0.5) / n
        r = keyed(NECK_RADIUS_KEYS, s) * (0.6 + 0.4 * hsc)
        t, d, side = frame(p2 - p1)
        R = seg_matrix(t, d, side)
        nm = f"Body_Neck{k}_{i}"
        B(nm + "_Inner", (2 * r * 0.8, Ln * 1.3, 2 * r * 0.8), mid, R, M_ROCK2, body_root)        # jointure sombre
        B(nm + "_Lava", (2 * r, Ln * 0.86, 2 * r * 0.95), mid - d * 0.06 * r, R, NECK_FRONT, body_root)  # bloc de gorge
        B(nm + "_Back", (2 * r * 1.12, Ln * 0.92, r * 0.85), mid + d * r * 0.62, R, pick(BODY_MATS, BODY_W), body_root)
        for sgn in (-1, 1):
            B(f"{nm}_Side_{sgn}", (r * 0.3, Ln * 0.8, r * 0.75), mid + side * sgn * r * 0.95 + d * r * 0.5, R,
              pick(BODY_MATS, BODY_W), body_root)
        if i % NECK_SPIKE_EVERY == 0:
            spike(f"{nm}_Spike", mid + d * r * 0.95, d + t * 0.6, 0.32 * SC, (0.55 + 0.3 * (1 - s)) * SC * NECK_SPIKE_K,
                  body_root)

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_neck(k + 1, H, hd[3], hd[0])

# ----------------------------------------------------------
# 11. PATTES : cuisse / épaule en wedge, tibia en roche fissurée, bracelet sombre à bord doré,
#     pied, 3 doigts + 3 griffes d'obsidienne
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.22)
SHIN_H = LEG_H * 0.45

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.28)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.5
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.6 if hind else 1.4), thigh_h),
          (x + sgn * 0.06 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.12), mat=pick(BODY_MATS, BODY_W), parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.07 * SC)
    crack(f"{name}_ThighCrack", (x + sgn * th * 0.62, y - th * 0.4, FOOT_H + SHIN_H + thigh_h * 0.75),
          [(sgn * 0.02, th * 0.25, -th * 0.3), (0, th * 0.1, -th * 0.25), (sgn * 0.02, th * 0.3, -th * 0.2)], legs_root,
          th=0.07 * SC)
    sy = y + (th * 0.12 if hind else 0)
    rock_block(f"{name}_Shin", (th * 0.92, th * 0.98, SHIN_H + 0.2), (x, sy, FOOT_H + SHIN_H / 2), None, legs_root,
               cell=th * 0.55, gap=0.06 * SC, thick=0.12 * SC)
    # Bracelet de roche sombre, bord doré, petite gemme de lave (Épique)
    bh_ = SHIN_H * BRACER_K
    bz = FOOT_H + SHIN_H * 0.55
    box(f"{name}_Bracer", (th * 1.12, th * 1.18, bh_), (x, sy, bz), mat=M_ROCK2, parent=legs_root, bevel=0.03 * SC)
    B(f"{name}_BracerRim", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz + bh_ / 2), mat=M_GOLD, parent=legs_root)
    if not IS_BEBE:
        B(f"{name}_BracerRim2", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz - bh_ / 2), mat=M_GOLD, parent=legs_root)
        crystal(f"{name}_BracerGem", 0.14 * SC, 0.08 * SC, 0.12 * SC, (x, sy - th * 0.6, bz), (0, -1, 0), M_CORE,
                legs_root)
    # Pied plat + 3 doigts + 3 griffes
    fy = sy - th * 0.3
    box(f"{name}_Foot", (th * 1.15, th * 1.75, FOOT_H), (x, fy, FOOT_H / 2), mat=M_ROCK, parent=legs_root,
        bevel=0.05 * SC)
    B(f"{name}_FootGlow", (th * 1.18, th * 0.08, FOOT_H * 0.25), (x, fy - th * 0.3, FOOT_H * 0.55), mat=M_GLOW,
      parent=legs_root)
    toe_y = fy - th * 0.88 - th * 0.12
    for c in (-1, 0, 1):
        B(f"{name}_Toe_{c}", (th * 0.3, th * 0.5, FOOT_H * 0.7), (x + c * th * 0.34, toe_y, FOOT_H * 0.35),
          mat=TOE_MAT, parent=legs_root)
        shard(f"{name}_Claw_{c}", th * 0.22, th * 0.18, th * CLAW_K, (x + c * th * 0.34, toe_y - th * 0.2, FOOT_H * 0.3),
              (c * 0.12, -1, -0.25), M_CLAW, legs_root)
    # Pics de roche sur l'arrière de la cuisse
    for c in range(THIGH_SPIKES):
        spike(f"{name}_Spike_{c}", (x + sgn * th * 0.3, y + th * (0.2 + 0.3 * c), FOOT_H + SHIN_H + thigh_h * (0.85 - 0.2 * c)),
              (sgn * 0.5, 0.8, 0.5), 0.3 * SC, (0.7 - 0.12 * c) * SC, legs_root, up=(0, 0, 1))

LEG_TH_F, LEG_TH_R = BW * 0.4, BW * 0.46
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.3, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES (ado et adulte) : petites ailes d'hydre, os de roche sombre, membrane orange-rouge,
#     pics de roche au bout des doigts. Le bébé n'en a pas.
# ----------------------------------------------------------
if WING_SPAN > 0:
    for sgn in (-1, 1):
        root = Vector((sgn * BW * 0.32, -TL * 0.02, ZC + BH * 0.5))
        wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_ROCK2, M_MEMB, wings_root, lift=WING_LIFT,
                     sweep=WING_SWEEP, fingers=WING_FINGERS, bone=WING_BONE, droop=0.5, memb_t=WING_BONE * 0.4,
                     claw_mat=M_CLAW)
        for c in range(WING_FINGERS):
            f = c / max(1, WING_FINGERS - 1)
            tip = wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                                  -WING_SPAN * (0.05 + 0.5 * f)))
            spike(f"Wings_{sgn}_Spike_{c}", tip, tip - wrist, WING_BONE * 1.6, WING_SPAN * 0.12, wings_root)
        spike(f"Wings_{sgn}_WristSpike", wrist, (sgn * 0.4, 0.3, 1), WING_BONE * 1.8, WING_SPAN * 0.16, wings_root)
        # veines de lave sur la membrane (deux traits lumineux)
        for c in range(WING_VEINS):
            f = (c + 0.5) / WING_VEINS
            a = root.lerp(wrist, 0.35 + 0.3 * f) + Vector((0, 0, -0.02))
            b = wrist + Vector((sgn * WING_SPAN * 0.2, WING_SPAN * (0.2 + 0.35 * f), -WING_SPAN * (0.12 + 0.3 * f)))
            bar(f"Wings_{sgn}_Vein_{c}", a.lerp(b, 0.15), a.lerp(b, 0.85), WING_BONE * 0.35, M_GLOW, wings_root,
                up=(0, 1, 0), depth=WING_BONE * 0.55)

# ----------------------------------------------------------
# 13. QUEUE : courbe Catmull-Rom, segments de roche séparés par des anneaux de lave, ventre orange,
#     crête stratifiée, bout en grappe de pics de roche autour d'un cristal de lave
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.25, -0.45, 0.0), (0.5, -0.75, 0.25), (0.75, -0.7, 0.35), (1.0, -0.35, 0.15)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH * 0.6)))
TAIL_RADIUS_KEYS = [(0.0, BW * 0.38), (0.35, BW * 0.31), (0.7, BW * 0.21), (1.0, BW * 0.12)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_RADIUS_KEYS, s)
    t, d, side = frame(p2 - p1)
    R = seg_matrix(t, d, side)
    B(f"Tail_Core_{i}", (2 * r * 0.86, Ln * 1.3, 2 * r * 0.82), mid, R, M_CORE, tail_root)
    box(f"Tail_Seg_{i}", (2 * r, Ln * 0.9, 2 * r * 0.95), mid, R, pick(BODY_MATS, BODY_W), tail_root,
        bevel=(0.04 * SC if i < 3 else 0))
    if s < 0.8:
        B(f"Tail_Belly_{i}", (2 * r * 0.75, Ln * 0.75, 0.2 * SC), mid - d * (r * 0.97), R, M_BELLY, tail_root)
    spike(f"Tail_Crest_{i}", mid + d * r * 0.85, d + t * 0.7, 0.3 * SC + r * 0.25, 0.35 * SC + r * 0.9, tail_root,
          glow_tip=(i % 2 == 0))
    if TAIL_PATCHES and i % 2 == 1:
        for sgn in (-1, 1):
            B(f"Tail_Patch_{i}_{sgn}", (0.08 * SC, Ln * 0.5, r * 0.7), mid + side * sgn * r * 1.0 + d * r * 0.1, R,
              TAIL_PATCH_MAT, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipBase", (BW * 0.24, 0.35 * SC, BW * 0.22), tip, seg_matrix(tt_, td_, ts_), M_ROCK2, tail_root)
crystal("Tail_TipGem", BW * 0.08, TAIL_TIP * 0.35, TAIL_TIP * 0.4, tip, tt_, M_CORE, tail_root)
for c in range(TAIL_TIP_SPIKES):
    a = c * 2 * math.pi / TAIL_TIP_SPIKES
    off = td_ * math.cos(a) + ts_ * math.sin(a)
    spike(f"Tail_TipSpike_{c}", tip + off * BW * 0.06, tt_ + off * 0.55, 0.3 * SC, TAIL_TIP, tail_root,
          up=tuple(tt_), glow_tip=False)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Épique : fissures et cœur de lave émissifs, flammes sur les têtes, pointes rougeoyantes,
#     ornements dorés (bracelets, plastron), gemmes de lave. FX : braises et éclats de roche qui flottent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = NECK_TOP.z + HEAD_SCALE * 1.6
    for c in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.1 + WING_SPAN * 0.5), random.uniform(-TL * 0.9, TL * 0.6 + TAIL_L * 0.3),
                    random.uniform(LEG_H, top_z)))
        rot = (random.uniform(0, 90), random.uniform(0, 90), random.uniform(0, 90))
        if c % 3 == 2:   # éclat de roche noire
            B(f"FX_Rock_{c}", (FX_SIZE * 1.2, FX_SIZE * 0.9, FX_SIZE * 0.5), p, rot, M_ROCK, master)
        else:            # braise
            B(f"FX_Ember_{c}", (FX_SIZE * 0.6,) * 3, p, rot, pick([M_FLAME, M_GLOW, M_FLAM2]), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
