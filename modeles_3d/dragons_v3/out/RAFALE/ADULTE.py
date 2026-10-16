import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Rafale · Adulte
#  Rare · Vol · Amphiptère · monde 4
#  - Adulte : long serpent blanc dressé, anneaux larges au sol, immenses ailes de plumes effilées, crête de plumes hérissée
#  - Signes distinctifs : ailes de plumes effilées, bandes de vent argent enroulées sur tout le corps, crête double, queue qui monte en tourbillon de plumes
#  - Dos bleu ciel, ventre bleu très pâle en plaques, crocs fins, collier argent
#  - Rare : motif secondaire (bandes de vent argent), cornes bleues à branche, crête double, accent lumineux discret (iris, pointes de plumes)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4404)            # même dragon à chaque exécution
TAG = "RAFALE_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 11       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 8000          # budget de triangles de ce stade et de cette rareté
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
#    Blanc (corps), bleu ciel (dos, plumes), bleu très pâle (ventre), gris argent métallique (bandes de vent),
#    bleu vif (pointes de plumes, iris). Rare : accent lumineux discret (iris, pointes de plumes ; strength <= 1.3).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",     "#F4F6F9", 0.50)   # corps principal, blanc
M_BODY2 = get_mat("BodyGrey", "#CCD8E2", 0.55)   # segments alternés, anneaux de jointure clairs
M_SKY   = get_mat("Sky",      "#6FB4EE", 0.45)   # dos bleu ciel, plaques dorsales
M_BELLY = get_mat("Belly",    "#DCEBFA", 0.50)   # ventre bleu très pâle, mâchoire, plastron
M_DARK  = get_mat("Mouth",    "#5E6F80", 0.65)   # bouche, narines
M_SILV  = get_mat("Silver",   "#9EA8B4", 0.30, metallic=0.75)   # bandes de vent argent
M_FW    = get_mat("FeatherW", "#F7F9FC", 0.50)   # plumes blanches
M_FS    = get_mat("FeatherS", "#8FC6F2", 0.50)   # plumes bleu ciel
M_FT    = get_mat("FeatherTip", "#2F7FCF", 0.40, emission="#3D8FE0", strength=0.8)   # pointes de plumes, os d'aile (accent discret)
M_BONE  = get_mat("WingBone", "#2F7FCF", 0.45)   # os des ailes, cornes
M_CLAW  = get_mat("Claw",     "#EAF2FA", 0.35)   # crocs
M_WHITE = get_mat("EyeWhite", "#FFFFFF", 0.30)
M_IRIS  = get_mat("Iris",     "#2F9BFF", 0.25, emission="#2F9BFF", strength=1.3)   # iris bleu lumineux
M_BLACK = get_mat("Black",    "#0A1018", 0.30)

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
#   Seul ce bloc change entre BEBE, ADO et ADULTE : le reste du script est identique aux 3 stades.
# ----------------------------------------------------------
STAGE = "ADULTE"
ZB = 3.3
NECK_H = 7.0
COIL_R = 2.7   # rayon des anneaux au sol
TAIL_UP = 1.0   # hauteur de l'hélice de la queue
RK = 1.0   # épaisseur du corps
BODY_STEP = 0.95
HEAD_SCALE = 1.3
SNOUT_K = 1.0
FANGS = 3
CREST_N = 7   # plumes de la crête de tête
CREST_L = 2.6
CREST2 = True   # crête double (plumes latérales)
EAR_N = 3
EAR_L = 1.6
CHEEK_N = 3
HORN_K = 1.0
HORN_TINES = 1
COLLAR = True   # collier argent
FEATHER_K = 1.0   # taille des plumes du corps
BANDS = True   # bandes de vent argent
BAND_EVERY = 2   # une bande tous les N segments
BIB_N = 7
SHOULDER_F = 3
GROUND_F = 6
WING_SPAN = 9.8   # longueur d'une aile (os)
WING_LIFT = 0.6
WING_SWEEP = 0.5
WING_PRIM = 8   # plumes primaires par aile
WING_SEC = 8   # plumes secondaires par aile
WING_COVERT = True   # rangée de couvertures bleues
WING_BONE = 0.2
TAIL_F = 6   # plumes du tourbillon de queue
TAIL_L = 2.6
FX_N = 14
FX_SIZE = 1.1

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
HS = HEAD_SCALE

def build_ctrl():
    """Cou dressé presque droit, anneaux larges au sol, puis queue qui MONTE en tourbillon (hélice)."""
    pts = []
    for f, y in ((1.0, -0.55), (0.86, -0.15), (0.62, 0.20), (0.38, 0.30), (0.15, 0.05), (0.0, -0.45)):
        pts.append(Vector((0, y, ZB + NECK_H * f)))
    pts.append(Vector((0, -0.65, ZB * 0.55 + 0.9)))
    pts.append(Vector((0, -0.30, 1.6)))
    pts.append(Vector((0.05, 0.75, 0.3)))
    cy = 0.8 + COIL_R * 1.45
    for k in range(1, 6):
        th = math.radians(62 * k)
        R = COIL_R * (1.0 - 0.30 * (k / 5.0))
        pts.append(Vector((R * math.sin(th) * 1.15, cy - R * math.cos(th), 0.3 + 0.12 * k)))
    # hélice montante : la queue s'enroule autour d'un axe vertical
    hx, hy = 0.15 * COIL_R, cy - 0.15 * COIL_R
    for k in range(1, 6):
        th = math.radians(62 * 5 + 75 * k)
        R = COIL_R * (0.52 - 0.05 * k)
        pts.append(Vector((hx + R * math.sin(th), hy - R * math.cos(th), 0.9 + 0.95 * k * TAIL_UP)))
    return pts
CTRL = build_ctrl()

RADIUS_KEYS = [(0.0, 0.52), (0.04, 0.62), (0.18, 0.74), (0.30, 0.92), (0.42, 0.96), (0.60, 0.84),
               (0.78, 0.55), (0.90, 0.34), (1.0, 0.16)]
RADIUS_KEYS = [(s, v * RK) for s, v in RADIUS_KEYS]
S_TAIL = 0.62
S_WING = 0.15

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
HEAD_PITCH = 8

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)           # pas de pattes (amphiptère) : sert aux plumes posées au sol
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def feather(name, base, direction, length, width, mat, parent, up=(0, 0, 1), t=0.05, tip_mat=None):
    """Plume : plaque en losange allongé (largeur max à 45 % de la longueur) ; option : pointe d'une autre couleur."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.45 * length) + fx * (width / 2), base + fy * length,
           base + fy * (0.45 * length) - fx * (width / 2)]
    plate(name, pts, t, mat, parent)
    if tip_mat:
        plate(name + "_Tip", [base + fy * (0.62 * length) + fx * (width * 0.3), pts[2],
                              base + fy * (0.62 * length) - fx * (width * 0.3)], t * 1.5, tip_mat, parent)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne blanc, museau, mâchoire bleu pâle, yeux bleus lumineux, crête de plumes rabattue vers l'arrière,
#    plumes-oreilles, cornes-plumes bleues ramifiées, plumes de joue.
# ----------------------------------------------------------
def hv(v):
    return tuple(c * HS for c in v)

def hbox(name, size, loc, rot=None, mat=None, bevel=0.0):
    return box("Head_" + name, hv(size), hv(loc), rot, mat, H, bevel * HS)

def hwedge(name, size, loc, rot=None, mat=None, top_x=0.9, top_y=0.9, shift_y=0.0, bevel=0.0):
    return wedge("Head_" + name, hv(size), hv(loc), rot, mat, H, top_x, top_y, shift_y, bevel * HS)

def hshard(name, w, t, Ln, loc, direction, mat, up=(0, 0, 1)):
    return shard("Head_" + name, w * HS, t * HS, Ln * HS, hv(loc), direction, mat, H, up)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1)):
    return bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up)

def hfeather(name, loc, direction, length, width, mat, up=(0, 0, 1), t=0.06, tip_mat=None):
    return feather("Head_" + name, hv(loc), direction, length * HS, width * HS, mat, H, up, t * HS, tip_mat)

# Crâne, museau, arête, plaque bleu ciel sur le front, mâchoire bleu pâle, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.94, top_y=0.92, bevel=0.10)
hwedge("Snout", (1.4, 2.2 * SNOUT_K, 0.9), (0, -0.6 - 1.1 * SNOUT_K, -0.26), mat=M_BODY,
       top_x=0.92, top_y=0.97, shift_y=-0.05, bevel=0.08)
hbox("SnoutBridge", (0.8, 1.8 * SNOUT_K, 0.12), (0, -0.6 - 1.0 * SNOUT_K, 0.22), mat=M_SKY)
hbox("ForeheadPlate", (1.25, 0.9 * SNOUT_K + 0.3, 0.1), (0, -0.15, 0.86), mat=M_SKY)
hbox("Jaw", (1.2, 2.0 * SNOUT_K, 0.28), (0, -0.55 - 1.05 * SNOUT_K, -0.74), mat=M_BELLY)
hbox("MouthLine", (1.43, 1.95 * SNOUT_K, 0.05), (0, -0.6 - 1.1 * SNOUT_K, -0.69), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.2 * SNOUT_K

for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.34, SNOUT_FRONT + 0.25, 0.18), mat=M_DARK)
    # fine bande argent sur le museau (vent)
    hbox(f"SnoutBand_{sgn}", (0.08, 0.7, 0.06), (sgn * 0.7, SNOUT_FRONT + 0.9, 0.0), mat=M_SILV)

# Yeux : blanc, iris bleu lumineux, pupille (ronde + reflets pour le bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.92, 1.0, 0.72, 0.84, 0.42, 0.6
else:
    EW, EH, IW, IH, PW, PH = 0.74, 0.7, 0.56, 0.6, 0.1, 0.52
for sgn in (-1, 1):
    ey, ez = -0.28, 0.12
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.93, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 0.98, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.02, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.22, 0.24), (sgn * 1.05, ey - 0.16, ez + 0.22), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.05, ey + 0.13, ez - 0.22), mat=M_WHITE)
    else:
        # sourcils : plume bleue rabattue vers l'arrière
        hfeather(f"Brow_{sgn}", (sgn * 0.95, ey - 0.45, ez + 0.52), (sgn * 0.05, 1.0, 0.18), 1.2, 0.34, M_FT, up=(sgn, 0, 0))

# Crocs fins (ado : 2 par côté ; adulte : 3 par côté)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.17, 0.17, 0.3 + 0.1 * FANGS / 3, (sgn * 0.62, fy, -0.7), (0, 0.05, -1),
                   M_CLAW, up=(1, 0, 0))

# SIGNE DISTINCTIF : crête de plumes rabattue vers l'arrière, du front à la nuque (plumes blanches, bleu ciel, pointe bleue).
#   Rare : crête DOUBLE = rangée centrale haute + rangée de petites plumes de chaque côté.
for k in range(CREST_N):
    f = k / max(1, CREST_N - 1)
    base = (0, -0.35 + 1.05 * f, 0.85 - 0.1 * f)
    L = CREST_L * (0.75 + 0.5 * math.sin(math.pi * (0.15 + 0.7 * f)))
    hfeather(f"Crest_{k}", base, (0, 0.55 + 0.7 * f, 0.9 - 0.45 * f), L, 0.62, (M_FW, M_FS)[k % 2], up=(1, 0, 0), t=0.07,
             tip_mat=M_FT)
    if CREST2:
        for sgn in (-1, 1):
            hfeather(f"Crest2_{sgn}_{k}", (sgn * 0.42, base[1] + 0.1, 0.76), (sgn * 0.35, 0.7 + 0.5 * f, 0.55 - 0.3 * f),
                     L * 0.62, 0.4, M_FS if k % 2 == 0 else M_FW, up=(sgn, 0, 0), t=0.06)

# Plumes-oreilles et plumes de joue (balayées vers l'arrière)
for sgn in (-1, 1):
    for k in range(EAR_N):
        hfeather(f"Ear_{sgn}_{k}", (sgn * 0.9, 0.25 + 0.15 * k, 0.25 - 0.22 * k), (sgn * (0.6 + 0.1 * k), 0.9, 0.15 - 0.1 * k),
                 EAR_L - 0.1 * k, 0.5, (M_FS, M_FW, M_FS)[k % 3], up=(0, 0, 1), t=0.06, tip_mat=M_FT if k == 0 else None)
    for k in range(CHEEK_N):
        hfeather(f"Cheek_{sgn}_{k}", (sgn * 0.88, -0.3 + k * 0.3, -0.5 - 0.06 * k), (sgn * 0.6, 0.9, -0.3),
                 0.9 - 0.1 * k, 0.34, M_FW, up=(sgn, 0, 0), t=0.05)

# Cornes-plumes bleues recourbées vers l'arrière (Rare : une branche secondaire)
for sgn in (-1, 1):
    hbox(f"HornBase_{sgn}", (0.4, 0.4, 0.28), (sgn * 0.5, 0.1, 0.8), mat=M_BONE)
    a0 = Vector((sgn * 0.5, 0.1, 0.88))
    a1 = Vector((sgn * 0.7, 0.6, 0.88 + 0.55 * HORN_K))
    a2 = Vector((sgn * 0.8, 1.35, 0.88 + 0.8 * HORN_K))
    chain(f"Head_Horn_{sgn}", [hv(a0), hv(a1), hv(a2)], 0.26 * HS, 0.13 * HS, M_BONE, H, bevel=0)
    hshard(f"HornTip_{sgn}", 0.15, 0.15, 0.5 * HORN_K, a2, (0, 1, 0.2), M_FT)
    if HORN_TINES:
        t2 = a1 + Vector((sgn * 0.4, 0.15, 0.55 * HORN_K))
        hbar(f"HornTine_{sgn}", a1, t2, 0.13, M_BONE)
        hshard(f"HornTineTip_{sgn}", 0.12, 0.12, 0.35 * HORN_K, t2, t2 - a1, M_FT)

# Collier argent autour de la base du crâne (bande de vent)
if COLLAR:
    hbox("NeckBand", (2.0, 0.22, 1.8), (0, 0.78, -0.15), mat=M_SILV)

# ----------------------------------------------------------
# 10. CORPS : segments blancs, dos bleu ciel, ventre bleu pâle, bandes de vent argent enroulées, crête de plumes
# ----------------------------------------------------------
band_i = 0
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
    # Dos bleu ciel : plaque posée sur le haut de chaque segment
    if s < 0.9:
        B(f"{tag}_Back_{i}", (1.5 * r, Ln * 1.0, 0.34 * r + 0.05), mid + d * (r * 0.9), R, M_SKY, parent)
    # Plaques de ventre bleu pâle bien séparées
    if s < 0.86:
        B(f"{tag}_Belly_{i}", (1.5 * r, Ln * 0.80, 0.26 * r + 0.06), mid - d * (r * 0.93), R, M_BELLY, parent)
    # Bande de vent argent : anneau incliné autour du corps, une sur trois, l'inclinaison alterne (effet d'hélice)
    if BANDS and 0.03 < s < 0.95 and i % BAND_EVERY == 1:
        tilt = math.radians(34) * (1 if band_i % 2 == 0 else -1)
        axis = t * math.cos(tilt) + side * math.sin(tilt)
        ring(f"{tag}_WindBand_{i}", r * 1.25, 0.34 * r + 0.06, 0.16, mid, axis, M_SILV, parent, sides=8, up=tuple(d))
        band_i += 1
    # Crête de plumes sur le dos : plumes blanches / bleu ciel qui se couchent vers l'arrière
    if 0.04 < s < 0.80 and i % 2 == 0:
        base = mid + d * (r * 0.95)
        L = (1.0 + 0.5 * r) * FEATHER_K
        feather(f"{tag}_Crest_{i}", base, d * 0.8 + t * 0.9, L, 0.7 * FEATHER_K, M_FW if (i // 2) % 2 == 0 else M_FS, parent,
                up=tuple(side), t=0.07, tip_mat=M_FT if (i // 2) % 3 == 0 else None)
        if CREST2 and i % 4 == 0:
            for sgn in (-1, 1):
                feather(f"{tag}_CrestS_{i}_{sgn}", base + side * sgn * r * 0.4, d * 0.5 + t * 0.9 + side * sgn * 0.5, L * 0.6,
                        0.4 * FEATHER_K, M_FS, parent, up=tuple(d), t=0.06)

# Plastron bleu pâle + plumes de poitrine (vers le bas et l'arrière)
cmid, ct, cd, cside, cr = frame_at(S_WING + 0.05)
CR = seg_matrix(ct, cd, cside)
B("Body_Plastron", (1.7 * cr, 1.5, 0.3), cmid - cd * (cr + 0.04), CR, M_BELLY, body_root)
for k in range(BIB_N):
    amt = (k - (BIB_N - 1) / 2) * 0.55
    feather(f"Body_Bib_{k}", cmid - cd * cr * 0.9 + cside * amt * cr * 0.8 + ct * 0.3, -cd * 0.6 + ct * 0.7,
            (1.1 - 0.12 * abs(amt)) * FEATHER_K, 0.6 * FEATHER_K, M_FW if k % 2 == 0 else M_FS, body_root, up=tuple(cside), t=0.07)
# Plumes d'épaule : petites plumes à la base de chaque aile
for sgn in (-1, 1):
    for k in range(SHOULDER_F):
        feather(f"Body_ShoulderFeather_{sgn}_{k}", cmid + cside * sgn * cr * 0.9 + cd * (0.3 - 0.25 * k) * cr,
                cside * sgn * (0.6 + 0.2 * k) + ct * (0.7 + 0.3 * k) + cd * (0.2 - 0.3 * k), (1.2 - 0.12 * k) * FEATHER_K,
                0.55 * FEATHER_K, (M_FS, M_FW, M_FS)[k % 3], body_root, up=tuple(cd), t=0.07)

# ----------------------------------------------------------
# 11. PATTES : aucune (amphiptère, corps de serpent). LEGS_ROOT ne porte que les plumes posées au sol.
# ----------------------------------------------------------
for k in range(GROUND_F):
    a = k * 2 * math.pi / GROUND_F + 0.4
    cy = 0.8 + COIL_R * 1.45
    base = Vector((math.sin(a) * COIL_R * 1.15, cy - math.cos(a) * COIL_R, 0.1))
    outv = Vector((math.sin(a), -math.cos(a), 0))
    base += outv * RK * 1.5
    feather(f"Legs_Feather_{k}", base, outv * 1.0 + Vector((0, 0, 0.5)), (0.9 * RK + 0.5) * FEATHER_K, 0.5 * FEATHER_K,
            (M_FW, M_FS)[k % 2], legs_root, up=(0, 0, 1), t=0.06)

# ----------------------------------------------------------
# 12. AILES DE PLUMES : bras et avant-bras osseux bleus, membrane pâle à la base, puis 3 rangées de plumes effilées
#     (primaires au poignet, secondaires le long du bras, couvertures bleues), pointes bleues lumineuses
# ----------------------------------------------------------
def feather_wing(sgn, root):
    span = WING_SPAN
    root = Vector(root)
    elbow = root + Vector((sgn * span * 0.38, span * WING_SWEEP * 0.25, span * WING_LIFT * 0.9))
    wrist = root + Vector((sgn * span * 0.62, span * WING_SWEEP * 0.45, span * WING_LIFT))
    link(f"Wings_{sgn}_Arm", root, elbow, WING_BONE * 1.3, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    link(f"Wings_{sgn}_Fore", elbow, wrist, WING_BONE, M_BONE, wings_root, up=(0, 1, 0), bevel=0)
    shard(f"Wings_{sgn}_Thumb", 0.14, 0.1, 0.45, wrist, (sgn * 0.3, -0.6, 0.6), M_CLAW, wings_root)
    u1 = (wrist - root).normalized()
    ref = Vector((sgn * 0.3, 1.0, -0.35))                  # direction moyenne des plumes (vers l'arrière et un peu vers le bas)
    n = u1.cross(ref).normalized()
    b = (ref - u1 * ref.dot(u1)).normalized()                # "arrière" dans le plan de l'aile
    back_root = root + b * span * 0.32
    # membrane pâle à la base (comble le vide entre le bras et les plumes)
    plate(f"Wings_{sgn}_Base", [root, elbow, wrist, wrist + b * span * 0.22, back_root], 0.06, M_FW, wings_root)
    # primaires : éventail de plumes au poignet
    for k in range(WING_PRIM):
        f = k / max(1, WING_PRIM - 1)
        ang = math.radians(22 + 105 * f)
        dv = u1 * math.cos(ang) + b * math.sin(ang)
        L = span * (0.74 - 0.18 * f)
        feather(f"Wings_{sgn}_Prim_{k}", wrist, dv, L, span * 0.115, (M_FW, M_FS)[k % 2], wings_root, up=tuple(n), t=0.06,
                tip_mat=M_FT)
        if WING_COVERT:
            feather(f"Wings_{sgn}_Cov_{k}", wrist + dv * span * 0.05 + n * 0.05, dv, L * 0.55, span * 0.11, (M_FS, M_FW)[k % 2],
                    wings_root, up=tuple(n), t=0.06)
    # secondaires : le long de l'avant-bras puis du bras
    for k in range(WING_SEC):
        f = k / max(1, WING_SEC - 1)
        p = wrist.lerp(elbow, min(1.0, f * 2.0)) if f < 0.5 else elbow.lerp(root, (f - 0.5) * 2.0)
        L = span * (0.5 - 0.2 * f)
        feather(f"Wings_{sgn}_Sec_{k}", p, b * 1.0 + u1 * (0.25 - 0.4 * f) - n * 0.05, L, span * 0.12, (M_FS, M_FW)[k % 2],
                wings_root, up=tuple(n), t=0.06, tip_mat=M_FT if k % 2 == 0 else None)
        if WING_COVERT:
            feather(f"Wings_{sgn}_SecCov_{k}", p + n * 0.05, b * 1.0 + u1 * (0.25 - 0.4 * f), L * 0.5, span * 0.1,
                    (M_FW, M_FS)[k % 2], wings_root, up=tuple(n), t=0.06)

wmid, wt, wd, wside, wr = frame_at(S_WING)
for sgn in (-1, 1):
    feather_wing(sgn, wmid + wd * wr * 0.8 + wside * sgn * wr * 0.55)

# ----------------------------------------------------------
# 13. QUEUE : fait partie de la même courbe (s > S_TAIL), qui monte en hélice ; bout = tourbillon de plumes
# ----------------------------------------------------------
tip = SPINE[-1]
tt_, td_, ts_ = FR[-1]
B("Tail_TipRing", (0.5 * RK, 0.3, 0.5 * RK), tip, seg_matrix(tt_, td_, ts_), M_SILV, tail_root)
for k in range(TAIL_F):
    a = k * 2 * math.pi / TAIL_F
    radial = td_ * math.cos(a) + ts_ * math.sin(a)
    tangential = -td_ * math.sin(a) + ts_ * math.cos(a)
    feather(f"Tail_Whirl_{k}", tip, tt_ * 0.9 + radial * 0.6 + tangential * 0.7, TAIL_L * (0.85 + 0.15 * (k % 2)), TAIL_L * 0.32,
            (M_FW, M_FS)[k % 2], tail_root, up=tuple(radial), t=0.07, tip_mat=M_FT)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (RARE) + FX
#     Rare : motif secondaire (bandes de vent argent), cornes-plumes à branche, crête double (plumes centrales + latérales),
#     accent lumineux discret (iris, pointes de plumes bleues ; strength <= 1.3). FX : plumes qui tourbillonnent.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * 3.0
    for k in range(FX_N):
        a = k * 2.4
        rr = WING_SPAN * 0.35 + 1.5 + (k % 3) * 0.9
        p = Vector((math.cos(a) * rr, 1.5 + COIL_R + math.sin(a) * rr * 0.8, 1.2 + (top_z - 1.5) * ((k * 0.37) % 1.0)))
        dirv = Vector((-math.sin(a), math.cos(a), 0.35))
        feather(f"FX_Feather_{k}", p, dirv, FX_SIZE * (1.0 + 0.3 * (k % 2)), FX_SIZE * 0.32, (M_FW, M_FS)[k % 2], master,
                up=(0, 0, 1), t=0.05)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
