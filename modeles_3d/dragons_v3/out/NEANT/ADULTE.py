import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Néant · Adulte
#  Secret · Ténèbres · Amphiptère · monde 5
#  - Adulte : grand serpent noir dressé en S sur ses anneaux, tête imposante (crocs, sourcils sévères, pupille fendue), grandes ailes à os violets
#  - Signes distinctifs : corps noir profond comme un trou noir, liserés violets lumineux, anneaux concentriques (corps, dos, sol, halo derrière la tête)
#  - Secret complet : crête et couronne déchirées, fissures émissives, parties fantômes (alpha 0.5-0.65), aile droite arrachée en partie, queue qui se défait
#  - Yeux blancs lumineux, fragments et anneaux fantômes qui flottent
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(7741)            # même dragon à chaque exécution
TAG = "NEANT_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 17000          # budget de triangles de ce stade et de cette rareté
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
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
GLOW_STR = 3.0
ZB = 3.2
NECK_H = 6.6
COIL_R = 2.4
TAIL_UP = 1.0
RK = 1.0
BODY_STEP = 0.6
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
HORN_K = 1.0
CHEEK_N = 3
MANE_N = 13
HEAD_CRACKS = 2
CREST_K = 1.1
RING_EVERY = 1
RING_SIDES = 16
CRACK_EVERY = 2
BACK_RINGS = 4
SHOULDER_N = 4
GROUND_RINGS = 4
WING_SPAN = 8.0
WING_LIFT = 0.5
WING_FINGERS = 4
WING_BONE = 0.24
WING_GLOW = True
WING_RAGS = 3
TAIL_FRAG = 8
TAIL_FRAG_K = 1.2
HALO_N = 2
FX_N = 40
FX_SIZE = 0.9
FX_RINGS = 6



# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Corps noir profond (trou noir), liserés et anneaux violets émissifs, indigo (ventre, membranes),
#    yeux blancs lumineux. Secret : parties fantômes translucides (alpha 0.5-0.65), fissures émissives.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#0B0910", 0.32, 0.25)   # corps principal : noir profond, léger reflet
M_BODY2 = get_mat("BodyDark",  "#08070C", 0.40)         # segments alternés, dessus du museau
M_BODYL = get_mat("ScaleB",    "#211439", 0.40)         # écailles plus claires (violet très sombre)
M_BELLY = get_mat("Belly",     "#1E2A5E", 0.50)         # ventre en plaques, mâchoire, plastron (indigo)
M_RIM   = get_mat("Glow",      "#9B5CFF", 0.25, 0.0, "#9B5CFF", GLOW_STR)          # liserés, fissures, pointes de cornes
M_RIMD  = get_mat("Crest",     "#6E3FC8", 0.30, 0.0, "#6E3FC8", GLOW_STR * 0.55)   # liserés secondaires, os d'aile
M_RING  = get_mat("RingGlow",  "#9B5CFF", 0.25, 0.0, "#9B5CFF", GLOW_STR * 0.8, 0.65)   # anneaux concentriques (alpha 0.65)
M_MEMB  = get_mat("Membrane",  "#1E2A5E", 0.55, 0.0, None, 0.0, 0.62)              # membranes d'ailes translucides
M_GHOST = get_mat("Ghost",     "#2A1850", 0.45, 0.0, "#6E3FC8", 0.6, 0.55)         # parties fantômes (alpha 0.55)
M_GHOSTL= get_mat("GhostLight","#9B5CFF", 0.30, 0.0, "#9B5CFF", 1.2, 0.5)          # fragments qui se détachent
M_CLAW  = get_mat("Claw",      "#6E3FC8", 0.35)         # griffes
M_EYE   = get_mat("Eye",       "#F4F0FF", 0.20, 0.0, "#F4F0FF", GLOW_STR + 1.0)    # yeux : blanc lumineux
M_WHITE = get_mat("White",     "#F2F2F2", 0.30)         # crocs, reflets des yeux
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)         # pupilles
M_VOID  = get_mat("Nostril",   "#050407", 0.80)         # orbites, narines, bouche

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
HS = HEAD_SCALE

# Points de contrôle de la colonne (Catmull-Rom) : cou dressé en S, descente, anneaux au sol, queue qui remonte
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
CY = 0.8 + COIL_R * 1.55                          # centre de l'anneau au sol

RADIUS_KEYS = [(0.0, 0.62), (0.04, 0.74), (0.18, 0.86), (0.30, 1.08), (0.42, 1.12), (0.60, 0.98),
               (0.78, 0.62), (0.90, 0.38), (1.0, 0.16)]
RADIUS_KEYS = [(s, v * RK) for s, v in RADIUS_KEYS]
S_TAIL = 0.64                                     # au-delà : pièces parentées à TAIL_ROOT
S_WING = 0.17                                     # position des épaules (ailes) le long de la colonne
S_GHOST = 0.80                                    # au-delà : le corps devient fantôme (translucide)

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
legs_root = empty("LEGS_ROOT", master)           # pas de pattes (amphiptère) : porte les anneaux posés au sol
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
# ----------------------------------------------------------
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

def hbar(name, p1, p2, th, mat):
    return bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H)

# Crâne carré, museau, arête du museau violette, mâchoire indigo distincte, ligne de bouche lumineuse
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.5, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.96, top_y=0.97, shift_y=-0.04, bevel=0.08)
hbox("SnoutBridge", (0.5, 1.7 * SNOUT_K, 0.1), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_RIM)      # liseré du museau
hbox("SnoutTop", (1.25, 0.7 * SNOUT_K + 0.3, 0.1), (0, -0.2, 0.86), mat=M_BODY2)
hbox("Jaw", (1.3, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_BELLY)
hbox("MouthLine", (1.53, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_RIMD)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.22, 0.22, 0.06), (sgn * 0.38, SNOUT_FRONT + 0.25, 0.2), mat=M_VOID)

# Yeux : orbite noire, blanc lumineux, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte), sourcils
if IS_BEBE:
    EW, EH, PW, PH = 0.95, 1.0, 0.42, 0.62
else:
    EW, EH, PW, PH = 0.74, 0.62, 0.1, 0.56
for sgn in (-1, 1):
    ey, ez = -0.28, 0.12
    hbox(f"EyeSocket_{sgn}", (0.1, EW + 0.2, EH + 0.2), (sgn * 0.92, ey, ez), mat=M_VOID)
    hbox(f"Eye_{sgn}", (0.1, EW, EH), (sgn * 0.98, ey - 0.02, ez), mat=M_EYE)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.07, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, ey + 0.13, ez - 0.22), mat=M_WHITE)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.05, 0.22), (sgn * 0.95, ey - 0.05, ez + 0.52), rot=(16, 0, 0),
             mat=M_BODYL, bevel=0.02)

# Crocs (ado : 2 par côté ; adulte : 3)
for sgn in (-1, 1):
    for k in range(FANGS):
        fy = SNOUT_FRONT + 0.55 + k * 0.5
        hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.28 + 0.1 * FANGS / 3, (sgn * 0.68, fy, -0.74), (0, 0.05, -1),
               M_WHITE, up=(1, 0, 0))

# Cornes : arc de blocs noirs vers l'arrière, pointe violette lumineuse. Corne gauche plus longue (asymétrie).
for sgn in (-1, 1):
    hk = HORN_K * (1.0 if sgn == -1 else 0.78)
    a0 = Vector((sgn * 0.55, 0.3, 0.7))
    a1 = Vector((sgn * 0.85, 0.85, 0.7 + 0.8 * hk))
    a2 = Vector((sgn * 1.0, 1.6, 0.7 + 1.35 * hk))
    a3 = Vector((sgn * 0.9, 2.4, 0.7 + 1.55 * hk))
    pts = [a0, a1, a2] + ([a3] if hk > 0.7 else [])
    for i in range(len(pts) - 1):
        hbar(f"Horn_{sgn}_{i}", pts[i], pts[i + 1], 0.34 - 0.07 * i, M_BODY)
    tip = pts[-1]
    hshard(f"HornTip_{sgn}", 0.26, 0.2, 0.5 + 0.5 * hk, tip, (sgn * 0.1, 0.6, 0.5), M_RIM, up=(1, 0, 0))

# Nageoires d'oreille fantômes (translucides) + joue fantôme à droite (silhouette déchirée)
if not IS_BEBE:
    for sgn in (-1, 1):
        hshard(f"Ear_{sgn}", 0.7, 0.1, 1.5 if sgn == -1 else 1.0, (sgn * 0.9, 0.5, 0.2), (sgn * 1.0, 0.8, 0.35), M_GHOST, up=(0, 0, 1))
    hbox("CheekGhost", (0.2, 0.9, 0.7), (0.98, 0.15, -0.35), mat=M_GHOST)
for sgn in (-1, 1):
    for k in range(CHEEK_N):
        hshard(f"Cheek_{sgn}_{k}", 0.4, 0.1, 0.8 - 0.1 * k, (sgn * 0.92, -0.2 + k * 0.32, -0.45 - k * 0.1),
               (sgn * 1.0, 0.7, -0.5), M_RIMD if k % 2 == 0 else M_BODYL, up=(0, 0, 1))

# Couronne de fragments déchirés derrière le crâne (noir / fantôme / lumineux)
for k in range(MANE_N):
    ang = math.radians(-150 + k * (300 / max(1, MANE_N - 1)))
    rad = Vector((math.sin(ang), 0, math.cos(ang)))
    loc = (rad.x * 0.75, 0.7, rad.z * 0.7)
    ln = (1.0 + random.random() * 0.8) * (1.25 if rad.x < 0 else 0.85)
    direction = rad * 0.8 + Vector((0, 1.0, 0.1))
    hshard(f"Mane_{k}", 0.55, 0.12, ln, loc, direction, [M_BODY, M_GHOST, M_RIMD, M_BODYL][k % 4], up=tuple(rad))

# Fissures émissives sur le crâne (zigzag asymétrique)
for k in range(HEAD_CRACKS):
    z0 = 0.75 - 0.3 * k
    hbox(f"Crack_{k}_a", (0.07, 0.8, 0.07), (-0.45 + 0.25 * k, -0.4, 0.88 - 0.05 * k), rot=(0, 0, 25), mat=M_RIM)
    hbox(f"Crack_{k}_b", (0.07, 0.6, 0.07), (-0.2 + 0.25 * k, -0.05, 0.88 - 0.05 * k), rot=(0, 0, -30), mat=M_RIM)

# ----------------------------------------------------------
# 10. CORPS : segments noirs, liserés violets, anneaux concentriques, ventre indigo, crête déchirée
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(S_WING + 0.05)
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
    ghost = s > S_GHOST

    # Segment principal : noir (fantôme près du bout de la queue)
    mat_seg = M_GHOST if ghost else (M_BODY if i % 2 == 0 else M_BODY2)
    box(f"{tag}_Seg_{i}", (2 * r, Ln * 1.30, 1.9 * r), mid, R, mat_seg, parent,
        bevel=(0.08 * r if s < 0.42 else 0.0))
    if ghost:
        continue
    # Liserés violets lumineux le long des flancs (haut et bas) : une ligne par côté, plus fournie à gauche
    for sgn in (-1, 1):
        B(f"{tag}_Rim_{i}_{sgn}", (0.08, Ln * 1.05, 0.1 * r), mid + side * sgn * r * 1.0 + d * (0.42 * r), R, M_RIM, parent)
        if sgn == -1 and s < 0.7:
            B(f"{tag}_RimLow_{i}", (0.07, Ln * 0.9, 0.08 * r), mid + side * -r * 1.0 - d * (0.35 * r), R, M_RIMD, parent)
    # Écailles de flanc violet sombre (une par côté et par segment) + liseré dorsal
    if s < 0.78:
        for sgn in (-1, 1):
            B(f"{tag}_Flank_{i}_{sgn}", (0.14, Ln * 0.82, 0.42 * r), mid + side * sgn * r * 0.99 - d * (0.05 * r), R, M_BODYL, parent)
        B(f"{tag}_DorsalLine_{i}", (0.3 * r, Ln * 0.7, 0.08), mid + d * (r * 0.97), R, M_RIMD, parent)
    # Plaques de ventre indigo bien séparées
    if s < 0.8:
        B(f"{tag}_Belly_{i}", (1.55 * r, Ln * 0.80, 0.26 * r + 0.06), mid - d * (r * 0.93), R, M_BELLY, parent)
    # Écailles sombres sur le dos (un segment sur deux)
    if 0.1 < s < 0.76 and i % 2 == 1:
        B(f"{tag}_Scale_{i}", (1.3 * r, Ln * 0.85, 0.2 * r + 0.05), mid + d * (r * 0.92),
          R @ Euler((math.radians(-6), 0, 0)).to_matrix(), M_BODYL, parent)
    # Anneau concentrique lumineux autour du corps (tous les RING_EVERY segments)
    if RING_EVERY and 0.03 < s < 0.78 and i % RING_EVERY == 0:
        ring(f"{tag}_Ring_{i}", r * 1.12, 0.16 * r + 0.04, 0.1, mid, t, M_RING, parent, sides=RING_SIDES, up=tuple(d))
    # Crête déchirée sur le dos : éclats irréguliers, certains manquent, certains sont fantômes
    if 0.03 < s < 0.78 and i % 2 == 0 and random.random() > 0.2:
        lv = (0.9 + 0.6 * r) * CREST_K * random.uniform(0.7, 1.3)
        shard(f"{tag}_Crest_{i}", 0.7 * CREST_K, 0.1, lv, mid + d * r * 0.9, d * 0.9 + t * 0.8,
              [M_BODYL, M_GHOST, M_RIMD][(i // 2) % 3], parent, up=tuple(side))
    # Fissures émissives (asymétriques : surtout à gauche)
    if CRACK_EVERY and 0.08 < s < 0.7 and i % CRACK_EVERY == 1:
        sg = -1 if (i // CRACK_EVERY) % 3 else 1
        c0 = mid + side * sg * r * 1.02 + d * 0.1 * r
        B(f"{tag}_Crack_{i}_a", (0.06, Ln * 0.55, 0.07 * r), c0, R @ Euler((0, 0, math.radians(28))).to_matrix(), M_RIM, parent)
        B(f"{tag}_Crack_{i}_b", (0.06, Ln * 0.5, 0.07 * r), c0 - d * 0.28 * r + t * Ln * 0.3,
          R @ Euler((0, 0, math.radians(-30))).to_matrix(), M_RIM, parent)

# Anneaux concentriques emboîtés posés sur le dos du torse (signe distinctif)
for j in range(BACK_RINGS):
    rr = cr * (0.28 + 0.22 * j)
    ring(f"Body_BackRing_{j}", rr, 0.09 + 0.02 * j, 0.07, cmid + cd * cr * 0.97 + ct * 0.4, cd, M_RING, body_root,
         sides=RING_SIDES, up=tuple(ct))

# Plastron indigo large + épaulières en wedge à la base des ailes
CR = seg_matrix(ct, cd, cside)
B("Body_Plastron", (1.5 * cr, 1.3, 0.22), cmid - cd * (cr + 0.04), CR, M_BELLY, body_root)
crystal("Body_ChestGem", 0.3 * cr, 0.9 * cr, 0.5, cmid - cd * (cr + 0.1), -cd + ct * 0.1, M_RIM, body_root, up=tuple(ct))   # gemme du plastron
for sgn in (-1, 1):
    for k in range(SHOULDER_N):
        shard(f"Body_Shoulder_{sgn}_{k}", 0.6, 0.12, (1.2 - 0.12 * k) * CREST_K,
              cmid + cside * sgn * cr * 0.9 + cd * (0.3 - 0.2 * k) * cr + ct * (-0.4 + 0.3 * k),
              cside * sgn * (0.9 + 0.1 * k) + ct * (0.5 + 0.3 * k) + cd * (0.3 - 0.3 * k),
              M_BODYL if k % 2 == 0 else M_GHOST, body_root, up=tuple(cd))
    wedge(f"Body_ShoulderPlate_{sgn}", (0.9 * cr, 1.5, 0.45), cmid + cside * sgn * cr * 0.55 + cd * cr * 0.85, seg_matrix(ct, cd, cside),
          M_BODY, body_root, top_x=0.8, top_y=0.8, bevel=0.05)

# Anneaux concentriques posés au sol autour de l'enroulement (trou noir : disque d'accrétion), parentés à LEGS_ROOT
for j in range(GROUND_RINGS):
    ring(f"Legs_GroundRing_{j}", COIL_R * 1.0 + RK * (1.5 + 0.8 * j), 0.22 + 0.06 * (GROUND_RINGS - j), 0.08,
         (0, CY, 0.05 + 0.01 * j), (0, 0, 1), M_RING if j % 2 == 0 else M_RIMD, legs_root, sides=RING_SIDES * 2, up=(0, 1, 0))

# ----------------------------------------------------------
# 11. PATTES : aucune (amphiptère, corps de serpent). LEGS_ROOT ne porte que les anneaux posés au sol (section 10).
# ----------------------------------------------------------

# ----------------------------------------------------------
# 12. AILES : os noirs à liseré violet, membranes indigo translucides (alpha 0.62), aile droite déchirée
# ----------------------------------------------------------
wmid, wt, wd, wside, wr = frame_at(S_WING)
for sgn in (-1, 1):
    root = wmid + wd * wr * 0.8 + wside * sgn * wr * 0.55
    fingers = WING_FINGERS if sgn == -1 else max(2, WING_FINGERS - 1)       # aile droite : un doigt arraché
    span = WING_SPAN * (1.0 if sgn == -1 else 0.88)
    wrist = wing(f"Wings_{sgn}", root, sgn, span, M_RIMD if WING_GLOW else M_BODY, M_MEMB, wings_root,
                 lift=WING_LIFT, sweep=0.3, fingers=fingers, bone=WING_BONE, droop=0.3, memb_t=0.05, claw_mat=None)
    # articulation du poignet : éclat violet lumineux
    crystal(f"Wings_{sgn}_Wrist", 0.28 * WING_BONE / 0.16, 0.7 * WING_BONE / 0.16, 0.5, wrist, (sgn * 0.3, 0.2, 1), M_RIM, wings_root)
    # lambeaux fantômes qui pendent de l'aile (silhouette déchirée)
    for k in range(WING_RAGS):
        a = wrist + Vector((sgn * span * (0.1 + 0.12 * k), span * (0.2 + 0.1 * k), -span * (0.2 + 0.1 * k)))
        shard(f"Wings_{sgn}_Rag_{k}", span * 0.07, 0.05, span * 0.18, a, (sgn * 0.2, 0.3, -1), M_GHOST, wings_root, up=(1, 0, 0))

# ----------------------------------------------------------
# 13. QUEUE : suite de la courbe ; le bout devient fantôme puis se défait en fragments
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = FR[-1]
ring("Tail_TipRing", 0.5 * RK + 0.15, 0.1, 0.08, tip, tt_, M_RING, tail_root, sides=RING_SIDES, up=tuple(td_))
for k in range(TAIL_FRAG):
    a = tip + tt_ * (0.6 + 0.7 * k) + td_ * (0.4 * k) + ts_ * (0.35 * ((-1) ** k)) * (0.5 + 0.3 * k)
    shard(f"Tail_Frag_{k}", 0.55 * RK, 0.1, (1.1 - 0.1 * k) * TAIL_FRAG_K, a, tt_ + td_ * 0.3 + ts_ * 0.2 * ((-1) ** k),
          M_GHOSTL if k % 2 == 0 else M_GHOST, tail_root, up=tuple(td_))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (SECRET) + FX
#     Halo-trou noir : anneaux verticaux derrière la tête (ado/adulte), fragments flottants,
#     éclats noirs à liseré violet, anneaux fantômes.
# ----------------------------------------------------------
HP = HEAD_POS
if HALO_N:
    for j in range(HALO_N):
        ring(f"Halo_{j}", HS * (2.6 + 0.9 * j), 0.3 + 0.08 * (HALO_N - j), 0.1, HP + Vector((0, 1.7 * HS + 0.25 * j, 0.1 * HS)),
             (0, 1, 0), M_RING if j % 2 == 0 else M_RIMD, master, sides=RING_SIDES * 2, up=(0, 0, 1))
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 2.4
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (WING_SPAN * 0.95 + 2.0), random.uniform(-2.5, 3.0 + COIL_R * 2.5),
                    random.uniform(0.8, top_z)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        shard(f"FX_Shard_{k}", FX_SIZE * 0.6, 0.08, FX_SIZE * random.uniform(0.9, 1.6), p, dirv,
              [M_GHOSTL, M_BODYL, M_RIM, M_GHOST][k % 4], master, up=(random.uniform(-1, 1), random.uniform(-1, 1), 1))
    for k in range(FX_RINGS):
        p = Vector((random.uniform(-1, 1) * WING_SPAN * 0.7, random.uniform(-1.5, 2.0 + COIL_R * 2.0), random.uniform(1.5, top_z)))
        ring(f"FX_Ring_{k}", FX_SIZE * random.uniform(0.6, 1.0), 0.07, 0.05, p, Vector([random.uniform(-1, 1) for _ in range(3)]),
             M_RING, master, sides=10)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
