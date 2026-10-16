import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Trèfle · Ado
#  Rare · Plante · Classique · monde 1
#  - Ado plus élancé : cou de 5 plaques crème avec lianes, museau plus long, sourcils-feuilles, petits crocs, vraies griffes
#  - Signe distinctif : un grand TRÈFLE sur tige pousse sur le crâne ; cornes crème recourbées à 1 pointe
#  - Collerette et double crête de feuilles, petite crête pâle dans le dos, trèfles lumineux sur flancs, dos, cuisses et queue
#  - Grandes ailes vert-jaune pâle à os ocre avec un trèfle sombre, queue terminée par un grand trèfle ; accent lumineux (Rare)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(1105)            # même dragon à chaque exécution
TAG = "TREFLE_ADO"      # préfixe de tous les objets, matériaux et de la collection
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
# 7. PALETTE DU DRAGON
# ----------------------------------------------------------
# M_BODY = get_mat("Body", "#7DB83A", 0.45)
# ...

# ----------------------------------------------------------
# 8. HIÉRARCHIE
# ----------------------------------------------------------
# master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
# body_root = empty("BODY_ROOT", master) ...

# 9. TÊTE ... 10. CORPS ... 11. PATTES ... 12. AILES ... 13. QUEUE ... 14. RENDU DE RARETÉ / FX

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
# finalize(master)

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Corps ocre doré (couleur de bois clair), ventre crème, feuilles et lianes vertes, trèfles vert vif.
#    Rare : un accent lumineux discret (yeux, trèfles-motifs, pierre au pied, lucioles), strength <= 1.5.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#E2B24A", 0.55)   # corps principal ocre doré
M_BODY2 = get_mat("BodyScale", "#B98A30", 0.55)   # écailles, tibias, dessus des pattes
M_TOP   = get_mat("SnoutTop",  "#EEC862", 0.50)   # dessus du museau (plus clair)
M_DARK  = get_mat("BodyDark",  "#7A5520", 0.60)   # bouche, ombres
M_LEAF1 = get_mat("LeafLight", "#A6E84C", 0.45)   # feuilles claires
M_LEAF2 = get_mat("LeafMid",   "#5DBB35", 0.45)   # feuilles moyennes
M_LEAF3 = get_mat("LeafDark",  "#2F8A2A", 0.50)   # feuilles et lianes sombres
M_CLOV  = get_mat("Clover",    "#7FE03A", 0.40)   # grands trèfles (crâne, cornes, ailes)
M_STEM  = get_mat("CloverStem","#4FA32F", 0.50)   # tiges de trèfle
M_MARK  = get_mat("Mark",      "#9BEF4A", 0.40, emission="#7CF03A", strength=0.7)  # trèfles-motifs (flancs, queue)
M_CREAM = get_mat("Belly",     "#F3E8BC", 0.55)   # ventre en plaques, menton, plastron
M_HORN  = get_mat("Horn",      "#EADBB0", 0.50)   # cornes
M_BARK  = get_mat("Bark",      "#8A6228", 0.75)   # bracelets de bois
M_CLAW  = get_mat("Claw",      "#FBF5E2", 0.35)   # griffes, crocs, pointes d'aile
M_WING  = get_mat("Membrane",  "#CBD866", 0.55)   # membrane des ailes (vert-jaune pâle)
M_WMARK = get_mat("WingMark",  "#4E9A2A", 0.55)   # motifs sur la membrane
M_BONE  = get_mat("WingBone",  "#B88E34", 0.55)   # os des ailes (ocre)
M_SAIL  = get_mat("Sail",      "#DDF3B8", 0.45)   # grande crête pâle dans le dos
M_WHITE = get_mat("EyeWhite",  "#F6F6EA", 0.30)
M_IRIS  = get_mat("Iris",      "#6FE03A", 0.25, emission="#5BE02A", strength=1.0)
M_BLACK = get_mat("Black",     "#0B0F08", 0.30)
M_GEM   = get_mat("Gem",       "#8CFF5E", 0.12, emission="#5CFF3A", strength=1.4)   # pierre lumineuse au pied
M_FLY   = get_mat("Firefly",   "#FFE45A", 0.20, emission="#FFD83A", strength=1.5)   # lucioles
LEAFS = [M_LEAF1, M_LEAF2, M_LEAF3]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
MARK_K = 1.0
WING_DROOP = 0.55
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
FANGS = 2
CHEEK_N = 2
MANE_RINGS = 1
MANE_N = 11
BELLY_N = 5
FLANK_ROWS = 2
FLANK_COLS = 5
NECK_LEAF_X = (-0.4, 0.4)
CREST_N = 5
SHOULDER_LEAVES = 3
BRACER_K = 0.55
LEG_BEV = 1
TAIL_SCALES = True
TAIL_BEV_N = 3
BELLY_SIDES = True
VINES = True
THIGH_LEAVES = 1
GEM = True
WING_SPAN = 5.4
WING_LIFT = 0.6
WING_SWEEP = 0.3
WING_BONE = 0.26
WING_FINGERS = 3
TAIL_L = 5.0
TAIL_STEP = 0.7
TAIL_LEAF = 1.6
FX_N = 8
FX_SIZE = 0.6
FLANK_CLOVERS = 3
BACK_CLOVERS = 2
NECK_VINES = True
SAIL = 0.7
CREST2 = True
LEG_CLOVER = True
TAIL_CLOVERS = True

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
    """Suite de barres qui s'affinent (cornes, tiges, lianes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def leaf_plate(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.06):
    """Feuille en losange (plaque fine) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2),
           base + fy * length, base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def heart(name, c, v, u, L, w, mat, parent, t=0.08):
    """Feuille de trèfle en coeur : 2 lobes (plaques à 4 points). La pointe est en 'c', les lobes
    s'ouvrent vers 'v' (direction) sur la largeur 'u'. L = longueur, w = largeur."""
    c, v, u = Vector(c), Vector(v).normalized(), Vector(u).normalized()
    for s, nm in ((-1, "A"), (1, "B")):
        pts = [c, c + v * (0.4 * L) + u * (s * 0.5 * w), c + v * (0.95 * L) + u * (s * 0.3 * w), c + v * (0.8 * L)]
        plate(f"{name}_{nm}", pts, t, mat, parent)

def clover(name, base, axis, size, mat, parent, stem_mat=None, stem=1.0, tilt=28, spin=0, th=0.12, t=0.08):
    """Trèfle à 3 feuilles (3 coeurs) au bout d'une tige. 'axis' = direction de la tige.
    Les feuilles s'ouvrent à 'tilt' degrés au-dessus du plan perpendiculaire à la tige."""
    base, ax = Vector(base), Vector(axis).normalized()
    top = base + ax * stem
    if stem > 0.05:
        bar(f"{name}_Stem", base - ax * 0.1, top, th, stem_mat or M_STEM, parent)
    e1 = ax.cross(Vector((0, 1, 0)))
    if e1.length < 1e-3:
        e1 = ax.cross(Vector((1, 0, 0)))
    e1.normalize()
    e2 = ax.cross(e1).normalized()
    for k in range(3):
        a = math.radians(spin + 90 + k * 120)
        flat = e1 * math.cos(a) + e2 * math.sin(a)
        v = flat * math.cos(math.radians(tilt)) + ax * math.sin(math.radians(tilt))
        u = ax.cross(v).normalized()
        heart(f"{name}_L{k}", top, v, u, size, size * 0.95, mat, parent, t)

def clover_mark(name, c, normal, size, mat, parent, spin=0, t=0.05):
    """Petit trèfle-motif posé à plat sur la peau : 3 feuilles en losange (plaques fines)."""
    c, n = Vector(c), Vector(normal).normalized()
    e1 = n.cross(Vector((0, 0, 1)))
    if e1.length < 1e-3:
        e1 = n.cross(Vector((0, 1, 0)))
    e1.normalize()
    e2 = n.cross(e1).normalized()
    for k in range(3):
        a = math.radians(spin + 90 + k * 120)
        v = e1 * math.cos(a) + e2 * math.sin(a)
        u = n.cross(v).normalized()
        pts = [c + n * 0.01, c + v * size * 0.55 + u * size * 0.42 + n * 0.01,
               c + v * size * 1.0 + n * 0.01, c + v * size * 0.55 - u * size * 0.42 + n * 0.01]
        plate(f"{name}_L{k}", pts, t, mat, parent)

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

def hleaf(name, w, Ln, loc, direction, mat, up=(0, 0, 1), t=0.08):
    return leaf_plate("Head_" + name, hv(loc), direction, Ln * HS, w * HS, mat, H, up, t * HS)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

def hclover(name, base, axis, size, stem, tilt=28, spin=0):
    clover("Head_" + name, hv(base), axis, size * HS, M_CLOV, H, M_STEM, stem * HS, tilt, spin, 0.13 * HS, 0.09 * HS)

# Crâne carré, gros museau en bloc, arête claire, mâchoire crème, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.95, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.65, 2.1 * SNOUT_K, 1.05), (0, -0.6 - 1.05 * SNOUT_K, -0.22), mat=M_BODY,
       top_x=0.97, top_y=0.98, shift_y=-0.04, bevel=0.08)
hbox("SnoutTop", (1.3, 1.9 * SNOUT_K, 0.14), (0, -0.6 - 1.0 * SNOUT_K, 0.32), mat=M_TOP)
hbox("Jaw", (1.4, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.8), mat=M_CREAM)
hbox("MouthLine", (1.68, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.74), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K

# Narines carrées sur le dessus du museau
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.24, 0.24, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.3, 0.34), mat=M_BLACK)

# Yeux : blanc carré, iris, pupille (ronde + reflets pour le bébé, fine et verticale pour ado / adulte), sourcil-feuille
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.88, 0.95, 0.68, 0.8, 0.4, 0.56
else:
    EW, EH, IW, IH, PW, PH = 0.58, 0.66, 0.42, 0.56, 0.12, 0.5
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.97, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.01, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.05, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.22), (sgn * 1.08, ey - 0.15, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.08, ey + 0.12, ez - 0.2), mat=M_WHITE)
    # sourcil : feuille verte posée à plat au-dessus de l'oeil, pointe vers le museau
    hleaf(f"Brow_{sgn}", 0.4, 1.0 + (0.15 if not IS_BEBE else 0), (sgn * 0.99, ey + 0.55, ez + EH * 0.5 + 0.12),
          (0, -1, -0.25 if not IS_BEBE else 0.0), M_LEAF2, up=(sgn, 0, 0), t=0.08)

# Crocs (ado : 2 par côté, petits ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.74, fy, -0.76), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# Oreilles en feuille et feuilles de joue
for sgn in (-1, 1):
    hshard(f"Ear_{sgn}", 0.7, 0.1, 1.2, (sgn * 0.82, 0.5, 0.3), (sgn * 1, 0.6, 0.5), M_LEAF1)
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.45, 0.08, 0.85 - 0.1 * k, (sgn * 0.88, -0.35 + k * 0.3, -0.45 - k * 0.12),
               (sgn * 0.8, 0.9, -0.5), pick(LEAFS, [3, 4, 2]))

# Collerette de feuilles autour de l'arrière du crâne
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (rad.x * 0.75, 0.65 + ring_i * 0.25, rad.z * 0.7)
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.25) + Vector((0, 1.0, 0)) + jit
        hleaf(f"Mane_{ring_i}_{k}", 0.75 - ring_i * 0.1, 1.2 + ring_i * 0.2 + random.random() * 0.3,
              loc, direction, pick(LEAFS, [4, 3, 2]), up=tuple(rad))

# Cornes crème (bébé : petits moignons ; ado : recourbées + 1 pointe ; adulte : hautes, 2 pointes, trèfle au bout)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.6, 0.35, 0.75), (sgn * 0.78, 0.5, 1.15), (sgn * 0.72, 0.8, 1.45)],
               0.3, 0.12, M_HORN)
    elif IS_ADO:
        h0, h1, h2 = Vector((sgn * 0.62, 0.3, 0.78)), Vector((sgn * 0.85, 0.45, 1.4)), Vector((sgn * 0.8, 0.95, 1.95))
        hchain(f"Horn_{sgn}", [h0, h1, h2, (sgn * 0.62, 1.5, 2.15)], 0.36, 0.14, M_HORN)
        bar(f"Head_HornTine_{sgn}", hv(h1), hv((sgn * 1.2, 0.2, 1.85)), 0.15 * HS, M_HORN, H)
    else:
        a0, a1 = Vector((sgn * 0.62, 0.3, 0.78)), Vector((sgn * 0.95, 0.65, 1.7))
        a2, a3 = Vector((sgn * 1.2, 1.15, 2.5)), Vector((sgn * 1.2, 1.7, 3.15))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.4, 0.17, M_HORN)
        bar(f"Head_HornTine1_{sgn}", hv(a1), hv((sgn * 1.65, 0.3, 2.3)), 0.2 * HS, M_HORN, H)
        bar(f"Head_HornTine2_{sgn}", hv(a2), hv((sgn * 1.75, 0.9, 3.2)), 0.17 * HS, M_HORN, H)
        hclover(f"HornClover_{sgn}", a3, (sgn * 0.25, -0.35, 1), 0.95, 0.25, tilt=30, spin=(0 if sgn > 0 else 60))

# Signe distinctif : le TRÈFLE sur le crâne (bébé : petite pousse ; ado : grande tige ; adulte : couronne de feuilles + bourgeon)
if IS_BEBE:
    hclover("SkullClover", (0, 0.25, 0.7), (0, -0.5, 1), 0.85, 0.7, tilt=30)
elif IS_ADO:
    hchain("SkullStem", [(0, 0.2, 0.7), (0.05, 0.15, 1.3), (0.05, 0.1, 1.85)], 0.2, 0.14, M_STEM)
    hclover("SkullClover", (0.05, 0.1, 1.8), (0, -0.5, 1), 1.35, 0.15, tilt=32)
else:
    hchain("SkullStem", [(0, 0.25, 0.7), (0, 0.2, 1.3), (0, 0.1, 1.85)], 0.2, 0.13, M_STEM)
    hclover("SkullClover", (0, 0.1, 1.8), (0, -0.5, 1), 1.1, 0.12, tilt=34, spin=30)
    for k in range(5):
        a = math.radians(-60 + k * 30)
        hleaf(f"Crown_{k}", 0.55, 1.35, (0.2 * math.sin(a), 0.1, 0.8), (math.sin(a) * 0.7, 0.3, 1.0), pick(LEAFS, [3, 4, 2]),
              up=(1, 0, 0), t=0.07)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs, cou en plaques, ventre, flancs, crête, épaulières, motifs trèfle
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.08, TL * 0.52, BH), (0, -TL * 0.25, ZC), mat=M_BODY, parent=body_root,
      top_x=0.9, top_y=0.92, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.46, BH * 0.94), (0, TL * 0.05, ZC - 0.03 * BH), mat=M_BODY, parent=body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 0.96, TL * 0.5, BH * 0.97), (0, TL * 0.29, ZC - 0.03 * BH), mat=M_BODY, parent=body_root,
      top_x=0.92, top_y=0.9, shift_y=TL * 0.02, bevel=BEV)

def half_w(y):
    """Demi-largeur du torse à la position y (pour poser les écailles sur le flanc)."""
    f = (y + TL * 0.5) / TL
    return BW * (0.51 - 0.06 * min(1, max(0, f)))

# Plastron crème sur le poitrail + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), (0, -TL * 0.5 + 0.04, ZC - BH * 0.1),
    mat=M_CREAM, parent=body_root, bevel=0.05 * SC)
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), (0, y, ZC - BH / 2 + 0.03), mat=M_CREAM, parent=body_root)
    for sgn in ((-1, 1) if BELLY_SIDES else ()):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.3), (sgn * (half_w(y) - 0.01), y, ZC - BH * 0.3),
          mat=M_CREAM, parent=body_root)

# Grandes feuilles plates en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            y = -TL * 0.36 + (TL * 0.78) * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = ZC + BH * (0.26 - 0.18 * r)
            leaf_plate(f"Body_FlankLeaf_{sgn}_{r}_{c}", (sgn * (half_w(y) - 0.04 * SC), y, z), (sgn * 0.25, 1, -0.25),
                       BH * 0.5, BH * 0.3, pick([M_BODY2, M_LEAF2, M_LEAF3, M_BODY2], [3, 3, 2, 3]), body_root,
                       up=(sgn, 0, 0), t=0.06 * SC)

# Motif secondaire (Rare) : petits trèfles lumineux sur les flancs et le dos
for sgn in (-1, 1):
    for k in range(FLANK_CLOVERS):
        y = -TL * 0.3 + (TL * 0.62) * (k + 0.5) / FLANK_CLOVERS
        clover_mark(f"Body_Mark_{sgn}_{k}", (sgn * (half_w(y) + 0.01), y, ZC - BH * (0.0 if k % 2 else 0.12)),
                    (sgn, 0, 0), 0.36 * SC * MARK_K, M_MARK, body_root, spin=k * 40)
for k in range(BACK_CLOVERS):
    y = -TL * 0.25 + (TL * 0.55) * (k + 0.5) / BACK_CLOVERS
    clover_mark(f"Body_BackMark_{k}", (0, y, ZC + BH / 2 + 0.02), (0, 0, 1), 0.4 * SC * MARK_K, M_MARK, body_root, spin=k * 50)

# Cou : courbe lissée de la tête vers le torse, un segment ocre + une plaque crème par maillon
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
    # feuilles de nuque
    for k, amt in enumerate(NECK_LEAF_X):
        leaf_plate(f"Body_NeckLeaf_{i}_{k}", mid + d * r * 0.8 + side * amt * r, d + t * 0.9 + side * amt * 0.5,
                   (1.0 + 0.5 * (1 - s)) * SC + random.random() * 0.3, 0.8 * SC,
                   pick(LEAFS, [3, 4, 2]), body_root, up=tuple(d), t=0.1 * SC)
    for sgn in (-1, 1):
        if i % 2 == 0 or IS_ADULTE:
            leaf_plate(f"Body_NeckSide_{i}_{sgn}", mid + side * sgn * r * 0.9, side * sgn * 0.5 + t * 0.8 + d * 0.3,
                       0.85 * SC, 0.5 * SC, pick(LEAFS, [3, 4, 2]), body_root, up=tuple(d), t=0.07 * SC)
    # liane en écharpe autour du cou (1 maillon sur 2) : barre sombre en travers de la plaque crème
    if NECK_VINES and i % 2 == 1:
        for sgn in (-1, 1):
            bar(f"Body_NeckVine_{i}_{sgn}", mid - d * (r * 1.0) - side * sgn * r * 0.9 + t * Ln * 0.45,
                mid - d * (r * 1.0) + side * sgn * r * 0.2 - t * Ln * 0.45, 0.12 * SC, M_LEAF3, body_root, up=tuple(d))

# Grande crête pâle dans le dos du cou (ado : petite ; adulte : grande + une 2e plus petite = crête double)
if SAIL > 0:
    S_ = SAIL
    yb, zb = NECK_BASE.y + NECK_R[1] * 0.9, NECK_BASE.z + 0.1
    yt, zt = NECK_TOP.y + NECK_R[0] * 0.9, NECK_TOP.z + 0.2
    plate("Body_Sail", [(0, yb + 0.15, zb), (0, yt + 0.05, zt),
                        (0, yt + 1.5 * S_, zt + 1.7 * S_), (0, yb + 2.0 * S_, zb + 1.0 * S_)], 0.16 * SC, M_SAIL, body_root)
    plate("Body_Sail2", [(0, yb + 0.15 + 2.0 * S_ * 0.15, zb + 0.3), (0, yt + 0.6, zt - 0.6),
                         (0, yt + 1.5 * S_ * 0.8, zt - 0.1 + 1.0 * S_), (0, yb + 1.7 * S_, zb + 0.7 * S_)],
          0.2 * SC, M_LEAF1, body_root)

# Crête dorsale en feuilles sur le torse (rangée simple ; Rare = double rangée en ado / adulte)
for k in range(CREST_N):
    y = -TL * 0.38 + (TL * 0.8) * k / max(1, CREST_N - 1)
    shard(f"Body_Crest_{k}", 0.85 * SC, 0.12 * SC, (1.05 - 0.25 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          (0, y, ZC + BH / 2 - 0.05), (0, 0.45, 1), pick(LEAFS, [3, 4, 2]), body_root, up=(1, 0, 0))
    if CREST2:
        for sgn in (-1, 1):
            leaf_plate(f"Body_Crest2_{k}_{sgn}", (sgn * BW * 0.22, y + 0.2, ZC + BH / 2 - 0.05), (sgn * 0.5, 0.55, 1),
                       0.9 * SC, 0.5 * SC, pick(LEAFS, [4, 3, 2]), body_root, up=(0, 1, 0), t=0.07 * SC)

# Épaulières : grappe de feuilles sur chaque épaule
for sgn in (-1, 1):
    for k in range(SHOULDER_LEAVES):
        shard(f"Body_ShoulderLeaf_{sgn}_{k}", 0.45 * SC, 0.08 * SC, (0.95 - 0.1 * k) * SC,
              (sgn * BW * (0.42 + 0.03 * k), -TL * 0.2 + 0.2 * k * SC, ZC + BH * (0.4 - 0.12 * k)),
              (sgn * (0.9 + 0.1 * k), 0.5 + 0.2 * k, 0.5 - 0.5 * k), pick(LEAFS, [3, 4, 2]), body_root)

# ----------------------------------------------------------
# 11. PATTES : épaule / cuisse en wedge, jambe, bracelet de bois, lianes, pied, 3 doigts + 3 griffes
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
    # Bracelet de bois + lianes qui s'enroulent
    bh_ = SHIN_H * BRACER_K
    box(f"{name}_Bracer", (th * 1.06, th * 1.1, bh_), (x, y + yo, FOOT_H + SHIN_H * 0.5),
        mat=M_BARK, parent=legs_root, bevel=LEG_BEV * 0.04 * SC)
    B(f"{name}_BracerTop", (th * 1.12, th * 1.16, 0.1 * SC), (x, y + yo, FOOT_H + SHIN_H * 0.5 + bh_ / 2),
      mat=M_LEAF3, parent=legs_root)
    if VINES:
        for k in (-1, 1):
            B(f"{name}_Vine_{k}", (th * 0.95, 0.09 * SC, 0.11 * SC),
              (x, y + yo - th * 0.56, FOOT_H + SHIN_H * 0.5 + k * bh_ * 0.15),
              rot=(0, k * 35, 0), mat=M_LEAF3, parent=legs_root)
            B(f"{name}_VineSide_{k}", (0.09 * SC, th * 0.95, 0.11 * SC),
              (x + sgn * th * 0.56, y + yo, FOOT_H + SHIN_H * 0.5 + k * bh_ * 0.15),
              rot=(0, 0, k * 35), mat=M_LEAF3, parent=legs_root)
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
    # Feuilles sur la cuisse
    for k in range(THIGH_LEAVES):
        leaf_plate(f"{name}_Leaf_{k}", (x + sgn * th * 0.5, y - th * 0.3 + k * th * 0.35, FOOT_H + SHIN_H + thigh_h * (0.7 - 0.2 * k)),
                   (sgn * 0.6, 0.5, -0.7), (0.95 - 0.12 * k) * SC, 0.5 * SC, pick(LEAFS, [3, 4, 2]), legs_root,
                   up=(0, 1, 0), t=0.07 * SC)
    # Pierre verte lumineuse sur le côté du pied (patte arrière droite et avant gauche)
    if GEM and ((hind and sgn == 1) or ((not hind) and sgn == -1)):
        crystal(f"{name}_Gem", 0.17 * SC, 0.13 * SC, 0.17 * SC, (x + sgn * th * 0.57, fy + yo + th * 0.1, FOOT_H * 0.55),
                (sgn, 0, 0), M_GEM, legs_root)
    # Petit trèfle-motif sur la cuisse (Rare)
    if LEG_CLOVER:
        clover_mark(f"{name}_Mark", (x + sgn * (th * 0.58 + 0.04), y, FOOT_H + SHIN_H + thigh_h * 0.45), (sgn, 0, 0),
                    0.32 * SC * MARK_K, M_MARK, legs_root, spin=20)

LEG_TH_F, LEG_TH_R = BW * 0.42, BW * 0.5
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.32, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES membraneuses (os ocre, membrane vert-jaune pâle, pointes crème, grand trèfle sur chaque membrane)
# ----------------------------------------------------------
for sgn in (-1, 1):
    root = Vector((sgn * BW * 0.3, -TL * 0.08, ZC + BH * 0.5 - 0.1))
    wrist = wing(f"Wings_{sgn}", root, sgn, WING_SPAN, M_BONE, M_WING, wings_root, lift=WING_LIFT, sweep=WING_SWEEP,
                 fingers=WING_FINGERS, bone=WING_BONE, droop=WING_DROOP, memb_t=WING_BONE * 0.45, claw_mat=M_CLAW)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tip = wrist + Vector((sgn * WING_SPAN * (0.38 - 0.18 * f), WING_SPAN * (0.15 + 0.55 * f),
                              -WING_SPAN * (0.05 + WING_DROOP * f)))
        tips.append(tip)
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.7, WING_BONE * 1.2, WING_SPAN * 0.13, tip, tip - wrist, M_CLAW, wings_root)
    shard(f"Wings_{sgn}_WristSpike", WING_BONE * 1.8, WING_BONE * 1.3, WING_SPAN * 0.15, wrist, (sgn * 0.5, 0.2, 1), M_CLAW, wings_root)
    # grand trèfle (motif secondaire) à plat sur la membrane, côté visible
    a_, b_ = tips[0] - wrist, tips[-1] - wrist
    nrm = a_.cross(b_).normalized()
    if nrm.dot(Vector((0, -0.3, 1))) < 0:
        nrm = -nrm
    cen = wrist + (a_ + b_) * 0.42
    vdir = (a_ + b_).normalized()
    for k in range(3):
        ang = math.radians(90 + k * 120)
        udir = nrm.cross(vdir).normalized()
        v = (vdir * math.cos(ang) + udir * math.sin(ang)).normalized()
        u = nrm.cross(v).normalized()
        heart(f"Wings_{sgn}_Clover{k}", cen + nrm * (WING_BONE * 0.3), v, u, WING_SPAN * 0.2, WING_SPAN * 0.19, M_WMARK,
              wings_root, t=WING_BONE * 0.2)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments, plaques crème, crête de feuilles, grand trèfle final
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
    leaf_plate(f"Tail_Crest_{i}", mid + d * r * 0.8, d + t * 0.7, 0.5 * SC + r * 1.1, 0.8 * r + 0.3,
               pick(LEAFS, [3, 4, 2]), tail_root, up=tuple(side), t=0.07 * SC)
    if TAIL_SCALES and i % 2 == 0 and s < 0.85:
        for sgn in (-1, 1):
            leaf_plate(f"Tail_Scale_{i}_{sgn}", mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t, r * 1.1, r * 0.8,
                       pick([M_BODY2, M_LEAF2]), tail_root, up=tuple(side * sgn), t=0.05 * SC)
    if TAIL_CLOVERS and i % 3 == 1 and s < 0.8:
        clover_mark(f"Tail_Mark_{i}", mid + side * (r + 0.02), side, 0.5 * r * MARK_K + 0.12, M_MARK, tail_root, spin=i * 30)
# Bout de queue : anneau de bois puis un grand trèfle à 3 feuilles
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
B("Tail_TipRing", (BW * 0.26, 0.3 * SC, BW * 0.26), tip, seg_matrix(tt_, td_, ts_), M_BARK, tail_root)
clover("Tail_Clover", tip, tt_ * 0.6 + td_ * 0.8, TAIL_LEAF, M_CLOV, tail_root, M_STEM, stem=TAIL_LEAF * 0.45,
       tilt=25, spin=0, th=0.14 * SC, t=0.1 * SC)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motifs trèfles lumineux (flancs, dos, queue, ailes), cornes à 2 pointes, crête double,
#     accent lumineux discret (iris, trèfles-motifs, pierres, lucioles : strength <= 1.5).
#     FX : lucioles jaunes et feuilles qui tombent autour du dragon.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.6 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.55 + BW), random.uniform(-TL * 0.7, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.9, top_z * 0.95)))
        if k % 2 == 0:
            dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
            leaf_plate(f"FX_Leaf_{k}", p, dirv, FX_SIZE * random.uniform(0.8, 1.3), FX_SIZE * 0.55, pick([M_LEAF1, M_LEAF2]),
                       master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04 * SC)
        else:
            crystal(f"FX_Firefly_{k}", FX_SIZE * 0.14, FX_SIZE * 0.22, FX_SIZE * 0.14, p,
                    [random.uniform(-1, 1) for _ in range(3)], M_FLY, master, sides=4)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
