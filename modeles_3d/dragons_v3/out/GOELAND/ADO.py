import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Goéland · Ado
#  Commun · Vol · Wyvern · monde 4
#  - Ado wyvern à plumes : cou de 4 maillons, bec jaune crochu avec tache rouge et petites dents, yeux plus sérieux avec sourcils bleus
#  - Houppe de plumes bleues sur 2 rangées, cornes blanches moyennes, collerette de plumes blanches, plumes de flanc et d'épaule
#  - Ailes-bras à plumes de vol bleues aux pointes blanches, pattes d'oiseau palmées à griffes noires
#  - Queue en éventail de 7 plumes grises, plumes flottantes
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4417)            # même dragon à chaque exécution
TAG = "GOELAND_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 4500          # budget de triangles de ce stade et de cette rareté
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
#    Bleu ciel (corps, plumes), blanc (tête, ventre, pattes), jaune (bec), gris (éventail de queue), noir (griffes).
#    Commun : seuls les iris brillent (légèrement). Aucune autre émission.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#7DB6F0", 0.50)   # corps et plumes principales, bleu ciel
M_BODY2  = get_mat("BodyScale",  "#5F9BE0", 0.50)   # plumes de flanc, dessus des pattes
M_DARK   = get_mat("BodyDark",   "#456A9A", 0.55)   # os d'aile, ombres, ligne de bouche
M_CREST  = get_mat("Crest",      "#3F78CC", 0.45)   # houppe, plumes du dos, sourcils (bleu profond)
M_WHITE_B = get_mat("Belly",     "#F6F8FB", 0.50)   # tête, ventre en plaques, plastron, pattes, cornes, pointes d'ailes
M_BEAK   = get_mat("Beak",       "#F5C022", 0.40)   # bec jaune
M_BEAK2  = get_mat("BeakLower",  "#E0A410", 0.40)   # mandibule inférieure
M_RED    = get_mat("BeakSpot",   "#E0452E", 0.40)   # tache rouge du bec (goéland)
M_GREY   = get_mat("Fan",        "#A9ADB3", 0.55)   # éventail de plumes de queue, gris
M_GREY2  = get_mat("FanDark",    "#80858D", 0.55)   # pointes de plumes de queue
M_WEB    = get_mat("Web",        "#DCE6F2", 0.50)   # palmures entre les doigts de pied
M_CLAW   = get_mat("Claw",       "#26262B", 0.35)   # griffes noires
M_WING   = get_mat("WingFeather","#4F85D6", 0.50)   # plumes de vol des ailes-bras
M_WING2  = get_mat("WingLight",  "#8EC1F5", 0.50)   # petites plumes (couvertures) claires
M_WHITE  = get_mat("EyeWhite",   "#F4F6F9", 0.30)
M_IRIS   = get_mat("Iris",       "#2E7FE0", 0.25, emission="#4FA0FF", strength=1.5)
M_BLACK  = get_mat("Black",      "#0A0A0D", 0.30)
M_LEG    = M_WHITE_B
BLUES = [M_BODY, M_BODY2, M_CREST]
FANS = [M_GREY, M_GREY, M_GREY2]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADO"
LEAN        = 12       # inclinaison du torse vers l'avant (degrés)
BW          = 2.2      # largeur du torse
BH          = 2.1      # hauteur du torse
TORSO_L     = 4.2      # longueur du torse
LEG_H       = 2.8      # hauteur des pattes
NECK_L      = 2.6      # longueur du cou
NECK_LEAN   = 0.8      # avancée du cou
NECK_N      = 4        # maillons du cou
NECK_R      = (0.75, 1.0) # rayon du cou (haut, bas)
HEAD_SCALE  = 1.1      # taille de la tête
BEAK_K      = 0.85     # longueur du bec
TEETH       = 2        # dents par côté
CHEEK_F     = 2        # plumes de joue par côté
CREST_ROWS  = 2        # rangées de la houppe (1 à 3)
CREST_N     = 5        # plumes par rangée de houppe
CREST_K     = 0.9      # taille des plumes de houppe
BELLY_N     = 5        # plaques de ventre
BELLY_SIDES = False    # plaques blanches sur les flancs bas
FLANK_ROWS  = 2        # rangées de plumes de flanc
FLANK_COLS  = 3        # plumes par rangée
BACK_FEATH  = 6        # plumes dorsales
NECK_FEATH  = True     # plumes sur les côtés du cou
RUFF_N      = 5        # plumes de la collerette
SHOULDER_F  = 2        # plumes d'épaule par côté
THIGH_F     = 2        # plumes de cuisse par côté
LEG_BEV     = 0        # biseau des jambes
WING_SPAN   = 5.8      # envergure d'une aile
WRIST_Z     = 1.0      # hauteur du poignet
WING_BONE   = 0.26     # épaisseur des os d'aile
WING_FINGERS= 3        # doigts d'aile
FEATH_PER   = 3        # plumes de vol par doigt
SEC_F       = 2        # plumes secondaires par aile
WING_FACETS = False    # seconde couverture bleue
TAIL_L      = 5.4      # longueur de la queue
TAIL_STEP   = 0.75     # pas des segments de queue
TAIL_BEV_N  = 1        # segments de queue biseautés
TAIL_SCALES = True     # écailles sur la queue
TAIL_FEATH  = 7        # plumes de l'éventail de queue
TAIL_FEATH_L= 2.6      # longueur des plumes d'éventail
FAN_ANGLE   = 42       # demi-ouverture de l'éventail (degrés)
FX_N        = 6        # plumes flottantes
FX_SIZE     = 0.6      # taille des plumes flottantes

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

def feather(name, base, direction, length, width, mat, tip_mat, parent, up=(0, 0, 1), t=0.12, tip=0.34):
    """PLUME : un éclat plat (corps) + une pointe plus claire par-dessus (bout de plume blanc ou gris foncé)."""
    base = Vector(base)
    d = Vector(direction).normalized()
    shard(name, width, t, length, base, d, mat, parent, up)
    if tip_mat is not None:
        shard(name + "_Tip", width * 0.62, t * 1.25, length * tip, base + d * length * (1 - tip) * 0.98, d, tip_mat, parent, up)

# ----------------------------------------------------------
# 9. TÊTE (coordonnées locales de HEAD_ROOT, mises à l'échelle par HEAD_SCALE)
#    Crâne blanc anguleux, bec jaune crochu avec tache rouge, houppe de plumes bleues, 2 petites cornes blanches
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

def hfeather(name, loc, direction, Ln, w, mat, tip_mat=None, up=(0, 0, 1), t=0.1):
    feather("Head_" + name, hv(loc), direction, Ln * HS, w * HS, mat, tip_mat, H, up, t * HS)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS, t1 * HS, mat, H, up)

# Crâne blanc, bec haut (jaune) avec arête, mandibule basse, ligne de bouche, menton
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_WHITE_B, top_x=0.9, top_y=0.88, bevel=0.10)
hwedge("BeakUpper", (1.15, 2.3 * BEAK_K, 0.82), (0, -0.7 - 1.1 * BEAK_K, -0.12), mat=M_BEAK,
       top_x=0.55, top_y=0.8, shift_y=-0.05, bevel=0.07)
hbox("BeakRidge", (0.34, 2.0 * BEAK_K, 0.12), (0, -0.7 - 1.0 * BEAK_K, 0.34), mat=M_BEAK2)
hbox("BeakLower", (0.95, 2.0 * BEAK_K, 0.3), (0, -0.7 - 0.95 * BEAK_K, -0.56), mat=M_BEAK2, bevel=0.03)
hbox("Chin", (0.9, 0.7, 0.34), (0, -0.55, -0.82), mat=M_WHITE_B, bevel=0.03)
hbox("MouthLine", (1.2, 2.1 * BEAK_K, 0.05), (0, -0.7 - 1.0 * BEAK_K, -0.4), mat=M_DARK)
BEAK_FRONT = -0.7 - 2.3 * BEAK_K
# crochet du bec (pointe qui descend) + taches rouges de la mandibule
hshard("BeakHook", 0.5, 0.42, 0.62, (0, BEAK_FRONT + 0.2, -0.08), (0, -0.25, -1), M_BEAK, up=(1, 0, 0))
for sgn in (-1, 1):
    hbox(f"BeakSpot_{sgn}", (0.07, 0.34, 0.16), (sgn * 0.49, BEAK_FRONT + 0.7, -0.56), mat=M_RED)
    hbox(f"Nostril_{sgn}", (0.1, 0.24, 0.1), (sgn * 0.3, BEAK_FRONT + 0.95 * BEAK_K + 0.4, 0.08), mat=M_BLACK)

# Yeux : blanc, iris bleu lumineux, pupille (ronde + reflets pour le bébé, fendue ensuite), sourcils bleus
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
        hbox(f"Brow_{sgn}", (0.12, 0.8, 0.14), (sgn * 0.97, ey - 0.02, ez + 0.66), rot=(8, 0, 0), mat=M_CREST)
    else:
        hbox(f"Brow_{sgn}", (0.16, 1.0, 0.24), (sgn * 0.97, ey - 0.05, ez + 0.5), rot=(16, 0, 0), mat=M_CREST, bevel=0.02)

# Petites dents blanches le long du bec (ado / adulte)
for sgn in (-1, 1):
    for k in range(TEETH):
        fy = BEAK_FRONT + 0.55 + k * 0.5
        hshard(f"Tooth_{sgn}_{k}", 0.18, 0.16, 0.26 + 0.05 * TEETH, (sgn * 0.42, fy, -0.4), (0, 0.05, -1), M_WHITE_B, up=(1, 0, 0))

# Plumes de joue (blanches) qui partent vers l'arrière
for sgn in (-1, 1):
    for k in range(CHEEK_F):
        hfeather(f"Cheek_{sgn}_{k}", (sgn * 0.88, -0.05 + k * 0.4, -0.35 - k * 0.14), (sgn * 0.8, 0.9, -0.35),
                 0.95 - 0.1 * k, 0.42, M_WHITE_B if k % 2 == 0 else M_BODY, None, up=(sgn, 0, 0), t=0.12)

# HOUPPE de plumes bleues (signe distinctif) : rangées de plumes qui se dressent du front vers la nuque
for row in range(CREST_ROWS):
    off = 0.0 if row == 0 else (0.34 if row == 1 else 0.62) * (1 if row else 0)
    for sgn in ((1,) if row == 0 else (-1, 1)):
        for k in range(CREST_N):
            f = k / max(1, CREST_N - 1)
            loc = (sgn * off, -0.35 + 0.95 * f, 0.76 - 0.1 * f - 0.08 * row)
            dirv = (sgn * off * 0.6, 0.3 + 0.9 * f, 1.0 - 0.15 * f)
            Ln = (1.15 + 1.0 * math.sin(math.pi * (0.2 + 0.7 * f)) - 0.18 * row) * CREST_K
            hfeather(f"Crest_{row}_{sgn}_{k}", loc, dirv, Ln, 0.55 - 0.05 * row, (M_CREST, M_BODY, M_BODY2)[(k + row) % 3],
                     M_WHITE_B if (k % 2 == 0 and not IS_BEBE) else None, up=(1, 0, 0), t=0.14)

# Deux petites cornes blanches courbées vers l'arrière
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.05, 0.7), (sgn * 0.78, 0.2, 1.05), (sgn * 0.74, 0.55, 1.3)], 0.3, 0.12, M_WHITE_B)
    elif IS_ADO:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.1, 0.72), (sgn * 0.9, 0.3, 1.2), (sgn * 0.92, 0.75, 1.65)], 0.32, 0.12, M_WHITE_B)
    else:
        hchain(f"Horn_{sgn}", [(sgn * 0.62, 0.1, 0.72), (sgn * 0.95, 0.3, 1.3), (sgn * 1.05, 0.9, 1.85), (sgn * 0.9, 1.5, 2.1)], 0.36, 0.13, M_WHITE_B)
        hshard(f"HornTip_{sgn}", 0.2, 0.18, 0.5, (sgn * 0.9, 1.5, 2.1), (sgn * -0.3, 0.8, 0.1), M_WHITE_B)

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs inclinés, cou en plaques, ventre, plumes de flanc et de dos, collerette
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

# Plastron blanc + plaques de ventre séparées
place("Body_Plastron", box_mesh(BW * 0.84, 0.36 * SC, BH * 0.74), M_WHITE_B, tp(-0.5, 0, -BH * 0.1), TR, body_root, 0.05 * SC)
for i in range(BELLY_N):
    u = -0.42 + 0.84 * (i + 0.5) / BELLY_N
    pl = TL * 0.84 / BELLY_N * 0.86
    place(f"Body_Belly_{i}", box_mesh(BW * 0.8, pl, 0.2 * SC), M_WHITE_B, tp(u, 0, -BH / 2 + 0.03), TR, body_root)
    if BELLY_SIDES:
        for sgn in (-1, 1):
            place(f"Body_BellySide_{i}_{sgn}", box_mesh(0.1 * SC, pl, BH * 0.3), M_WHITE_B,
                  tp(u, sgn * (half_w(u) - 0.01), -BH * 0.3), TR, body_root)

# Plumes de flanc en quinconce (pointe vers l'arrière, bout blanc à l'adulte)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            u = -0.38 + 0.78 * (c + 0.5 * (r % 2)) / FLANK_COLS
            z = BH * (0.26 - 0.18 * r)
            feather(f"Body_Plume_{sgn}_{r}_{c}", tp(u, sgn * (half_w(u) - 0.03 * SC), z), TT + TS * sgn * 0.3 - TD * 0.1,
                    BH * 0.42, BH * 0.3, pick([M_BODY2, M_BODY2, M_WING]), M_WHITE_B if (IS_ADULTE and (r + c) % 2 == 0) else None,
                    body_root, up=(sgn, 0, 0), t=0.08 * SC)

# Plumes dorsales : crête de plumes bleues le long du dos (nuque -> queue)
for k in range(BACK_FEATH):
    u = -0.36 + 0.72 * k / max(1, BACK_FEATH - 1)
    feather(f"Body_BackFeather_{k}", tp(u, 0, BH / 2 + 0.05 * SC), TD * 1.0 + TT * (0.7 + 0.2 * math.sin(k)),
            (1.0 + 0.35 * math.sin(k * 1.3)) * SC, 0.7 * SC, M_CREST if k % 2 == 0 else M_BODY2, None, body_root, up=(1, 0, 0), t=0.2 * SC)

# Cou en S : un maillon bleu + une plaque blanche devant + plumes de côté
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
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.24 * SC), mid - d * (r * 0.95), R, M_WHITE_B, body_root)
    if NECK_FEATH:
        for sgn in (-1, 1):
            feather(f"Body_NeckFeather_{i}_{sgn}", mid + side * sgn * r * 0.85 + d * r * 0.2, side * sgn * 0.4 + Vector((0, 0.8, -0.5)),
                    (0.85 + 0.25 * (1 - s)) * SC, 0.5 * SC, M_BODY2 if i % 2 else M_WING, M_WHITE_B if IS_ADULTE and i % 2 == 0 else None,
                    body_root, up=tuple(d), t=0.1 * SC)
# Collerette de plumes blanches à la base du cou (ado / adulte)
for k in range(RUFF_N):
    a = math.radians(-100 + 200 * k / max(1, RUFF_N - 1))
    off = TS * math.sin(a) * BW * 0.46 + TD * (BH * 0.1) + TT * (-0.05 * TL)
    feather(f"Body_Ruff_{k}", NECK_BASE + off + Vector((0, -0.2 * SC, -0.3 * SC)), TS * math.sin(a) * 0.9 + Vector((0, -0.6, -0.5)),
            (1.1 + 0.3 * math.cos(a)) * SC, 0.55 * SC, M_WHITE_B, None, body_root, up=(0, 0, 1), t=0.14 * SC)

# Plumes d'épaule (couvertures) : petits éclats bleu clair devant les ailes
for sgn in (-1, 1):
    for k in range(SHOULDER_F):
        feather(f"Body_Shoulder_{sgn}_{k}", tp(-0.3 + 0.06 * k, sgn * BW * (0.5 + 0.02 * k), BH * (0.34 + 0.02 * k)),
                (sgn * 0.9, 0.5 + 0.3 * k, 0.45), (0.9 - 0.1 * k) * SC, 0.45 * SC, M_WING2 if k % 2 else M_WING, M_WHITE_B if IS_ADULTE else None,
                body_root, up=(0, 0, 1), t=0.12 * SC)

# ----------------------------------------------------------
# 11. PATTES : 2 pattes d'oiseau blanches (cuisse emplumée en wedge, tarse fin, pied palmé, 3 doigts + doigt arrière, griffes noires)
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.12)
FOOT_L = LEG_H * 0.55
LEG_TH = BW * 0.4
LEG_Y_U = 0.2                                  # position du bassin où s'attachent les hanches
for sgn in (-1, 1):
    th = LEG_TH
    hp = tp(LEG_Y_U, sgn * (BW * 0.5 - th * 0.1), -BH * 0.12)
    HZ = hp.z
    hip = Vector((hp.x, hp.y, HZ))
    knee = Vector((hip.x + sgn * th * 0.08, hip.y - LEG_H * 0.3, HZ * 0.5))
    ankle = Vector((hip.x, hip.y + LEG_H * 0.12, FOOT_H * 1.1 + HZ * 0.14))
    fy = ankle.y + th * 0.45 - FOOT_L / 2        # centre du pied
    # hanche + cuisse emplumée en wedge
    wedge(f"Legs_{sgn}_Hip", (th * 1.6, th * 2.0, th * 1.6), hip + Vector((sgn * 0.05 * th, 0.05, 0.1)), None, M_LEG, legs_root,
          top_x=0.85, top_y=0.85, bevel=0.08 * SC)
    limb(f"Legs_{sgn}_Thigh", hip, knee, th * 1.25, th * 1.45, M_LEG, legs_root, bevel=0.07 * SC, wedge_top=0.82)
    # culotte de plumes sur la cuisse (bleu clair, pointe vers le bas / l'arrière)
    for k in range(THIGH_F):
        feather(f"Legs_{sgn}_Thigh_Plume_{k}", hip.lerp(knee, 0.2 + 0.2 * k) + Vector((sgn * th * 0.62, 0, th * 0.25)),
                (sgn * 0.3, 0.45, -1.0), th * (1.5 - 0.2 * k), th * 0.75, M_BODY2 if k % 2 else M_BODY, M_WHITE_B if IS_ADULTE else None,
                legs_root, up=(sgn, 0, 0), t=th * 0.14)
    box(f"Legs_{sgn}_Knee", (th * 0.95, th * 0.85, th * 0.85), knee + Vector((0, 0.05, 0)), None, M_LEG, legs_root, bevel=0.04 * SC)
    # tarse fin (jambe d'oiseau) : du genou à la cheville
    limb(f"Legs_{sgn}_Shin", knee, ankle, th * 0.62, th * 0.66, M_LEG, legs_root, bevel=LEG_BEV * 0.05 * SC)
    # pied plat, talon, 3 doigts palmés + doigt arrière + griffes noires
    box(f"Legs_{sgn}_Foot", (th * 1.05, FOOT_L * 0.55, FOOT_H), (hip.x, fy + FOOT_L * 0.2, FOOT_H / 2), None, M_LEG, legs_root, bevel=0.05 * SC)
    link(f"Legs_{sgn}_Heel", (hip.x, ankle.y, ankle.z), (hip.x, fy + FOOT_L * 0.3, FOOT_H * 0.8), th * 0.6, M_LEG, legs_root, bevel=0, extra=0.1)
    toe_y = fy - FOOT_L / 2 - th * 0.15
    bases, tips = [], []
    for k in (-1, 0, 1):
        tb = Vector((hip.x + k * th * 0.2, fy - FOOT_L * 0.05, FOOT_H * 0.3))
        tt2 = Vector((hip.x + k * th * 0.62, toe_y - th * 0.55, FOOT_H * 0.3))
        bar(f"Legs_{sgn}_Toe_{k}", tb, tt2, th * 0.3, M_LEG, legs_root, up=(0, 0, 1))
        shard(f"Legs_{sgn}_Claw_{k}", th * 0.2, th * 0.16, th * 0.55, tt2 + Vector((0, -th * 0.15, -FOOT_H * 0.05)),
              (k * 0.15, -1, -0.2), M_CLAW, legs_root)
        bases.append(tb); tips.append(tt2)
    for k in range(2):   # palmures entre les doigts
        plate(f"Legs_{sgn}_Web_{k}", [bases[k], tips[k], tips[k + 1], bases[k + 1]], 0.05 * SC, M_WEB, legs_root)
    # doigt arrière court
    B(f"Legs_{sgn}_Hallux", (th * 0.26, th * 0.55, FOOT_H * 0.6), (hip.x, fy + FOOT_L * 0.55, FOOT_H * 0.3), None, M_LEG, legs_root)
    shard(f"Legs_{sgn}_HalluxClaw", th * 0.18, th * 0.14, th * 0.4, (hip.x, fy + FOOT_L * 0.55 + th * 0.2, FOOT_H * 0.25), (0, 1, -0.1), M_CLAW, legs_root)

# ----------------------------------------------------------
# 12. AILES-BRAS (wyvern) : le poignet pose presque au sol, les doigts montent vers l'arrière
#     et portent de longues plumes de vol bleues aux pointes blanches
# ----------------------------------------------------------
WSP = WING_SPAN
for sgn in (-1, 1):
    # épaule sur le haut du poitrail -> coude remonté vers l'arrière -> poignet posé devant, près du sol
    root = tp(-0.22, sgn * BW * 0.42, BH * 0.28)
    elbow = Vector((sgn * (BW * 0.5 + WSP * 0.16), root.y + WSP * 0.16, root.z + WSP * 0.1))
    wrist = Vector((sgn * (BW * 0.5 + WSP * 0.22), root.y - WSP * 0.12, WRIST_Z))
    bar(f"Wings_{sgn}_Arm", root, elbow, WING_BONE * 1.4, M_DARK, wings_root, up=(0, 1, 0))
    bar(f"Wings_{sgn}_Fore", elbow, wrist, WING_BONE * 1.15, M_DARK, wings_root, up=(0, 1, 0))
    place(f"Wings_{sgn}_WristPad", box_mesh(WING_BONE * 2.2, WING_BONE * 2.4, WING_BONE * 2.0), M_WHITE_B, wrist, None, wings_root, 0.03 * SC)
    tips = []
    for k in range(WING_FINGERS):
        f = k / max(1, WING_FINGERS - 1)
        tip = wrist + Vector((sgn * WSP * (0.2 + 0.12 * math.sin(math.pi * f)), WSP * (0.3 + 0.62 * f), WSP * (1.05 - 0.6 * f)))
        bar(f"Wings_{sgn}_Finger_{k}", wrist, tip, WING_BONE * (0.9 - 0.2 * f), M_DARK, wings_root, up=(0, 1, 0))
        tips.append(tip)
    # plumes de vol : un éventail le long de chaque doigt, bleues avec une pointe blanche
    for k in range(WING_FINGERS):
        tip = tips[k]
        fd = (tip - wrist).normalized()
        trail = (tips[k + 1] - tip).normalized() if k + 1 < WING_FINGERS else Vector((0, 1.0, -0.35)).normalized()
        for j in range(FEATH_PER):
            ff = (j + 1) / FEATH_PER
            p = wrist + (tip - wrist) * (0.35 + 0.65 * ff)
            dirv = fd * 0.55 + trail * (0.5 + 0.25 * (1 - ff))
            Ln = WSP * (0.34 + 0.16 * ff) * (1.0 if k < WING_FINGERS - 1 else 0.85)
            feather(f"Wings_{sgn}_Prim_{k}_{j}", p, dirv, Ln, WSP * 0.085, M_WING if (j + k) % 2 == 0 else M_CREST, M_WHITE_B,
                    wings_root, up=(sgn, 0, 0), t=WING_BONE * 0.45, tip=0.38)
        shard(f"Wings_{sgn}_Spike_{k}", WING_BONE * 1.3, WING_BONE * 1.1, WSP * 0.1, tip, tip - wrist, M_WHITE_B, wings_root)
    # plumes secondaires le long de l'avant-bras (claires)
    for j in range(SEC_F):
        ff = (j + 0.5) / SEC_F
        p = elbow.lerp(wrist, ff)
        feather(f"Wings_{sgn}_Sec_{j}", p, Vector((sgn * 0.25, 0.9, -0.1)) + Vector((0, 0, 0.1 * j)), WSP * (0.3 - 0.04 * ff), WSP * 0.09,
                M_WING2, M_WHITE_B, wings_root, up=(sgn, 0, 0), t=WING_BONE * 0.4)
    # couvertures : petite membrane bleue entre l'épaule, le coude et le poignet
    anchor = tp(0.2, sgn * BW * 0.44, BH * 0.1)
    plate(f"Wings_{sgn}_Cover", [root, elbow, wrist, tips[0]], WING_BONE * 0.4, M_WING2, wings_root)
    if WING_FACETS:
        plate(f"Wings_{sgn}_Cover2", [wrist, tips[0], tips[-1]], WING_BONE * 0.4, M_BODY2, wings_root)
    # griffe du pouce, posée au sol
    shard(f"Wings_{sgn}_ThumbClaw", WING_BONE * 1.1, WING_BONE * 0.9, WSP * 0.17, wrist, (sgn * 0.2, -0.7, -0.8), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE : courbe lissée, segments bleus à ventre blanc, plumes dorsales, ÉVENTAIL de plumes grises au bout
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.25, 0.0), (0.45, -0.6, 0.25), (0.7, -0.92, 0.1), (0.9, -0.95, -0.2), (1.0, -0.8, -0.3)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * BH)))
TAIL_R = [(0.0, BW * 0.4), (0.3, BW * 0.33), (0.6, BW * 0.24), (0.85, BW * 0.17), (1.0, BW * 0.13)]
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
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - d * (r * 0.95), R, M_WHITE_B, tail_root)
    if i % 2 == 0 and s < 0.85:
        feather(f"Tail_Dorsal_{i}", mid + d * r * 0.9, d + t * 0.8, 0.5 * SC + r * 0.9, 0.6 * r + 0.15, M_CREST if i % 4 == 0 else M_BODY2, None,
                tail_root, up=(1, 0, 0), t=0.14 * SC)
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + side * sgn * (r - 0.03), side * sgn * 0.3 + t,
                  pick([M_BODY2, M_WING]), tail_root, up=(sgn, 0, 0))
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
place("Tail_TipBase", box_mesh(BW * 0.3, 0.4 * SC, BW * 0.26), M_WHITE_B, tip, seg_matrix(tt_, td_, ts_), tail_root)
# Éventail de plumes grises (signe distinctif) : plumes étalées en arc horizontal, légèrement relevées
for k in range(TAIL_FEATH):
    f = k / max(1, TAIL_FEATH - 1)
    a = math.radians(-FAN_ANGLE + 2 * FAN_ANGLE * f)
    dirv = tt_ * math.cos(a) + ts_ * math.sin(a) + td_ * (0.16 + 0.12 * (1 - abs(2 * f - 1)))
    L_ = TAIL_FEATH_L * (0.78 + 0.22 * (1 - abs(2 * f - 1)))
    feather(f"Tail_Fan_{k}", tip + tt_ * 0.05, dirv, L_, BW * 0.2, FANS[k % 3] if k % 2 else M_GREY, M_GREY2, tail_root, up=tuple(td_), t=BW * 0.05, tip=0.3)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (COMMUN) + FX
#     Commun : silhouette propre, 5 familles de couleurs (bleu, blanc, jaune, gris, noir), seuls les iris brillent.
#     Un signe fort : ailes à plumes de vol bleues aux pointes blanches. Plumes qui flottent autour du dragon.
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
        plate(f"FX_Feather_{k}", [base, base + fy_ * 0.4 * sz + fx * 0.22 * sz, base + fy_ * sz, base + fy_ * 0.4 * sz - fx * 0.22 * sz],
              0.04 * SC, M_WHITE_B if k % 2 else M_WING2, master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
