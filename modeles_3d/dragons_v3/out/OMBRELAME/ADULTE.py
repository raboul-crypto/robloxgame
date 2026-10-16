import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Ombrelame · Adulte
#  Épique · Ténèbres · Wyvern · Rapide · monde 5
#  - Adulte : wyvern fine et rapide, penchée en avant, 2 pattes arrière hautes, ailes-bras très grandes, 3 crocs par côté
#  - Crinière de lames à 3 anneaux, grandes cornes à 2 pointes + corne basse à pointes claires, anneaux dorés
#  - Ailes-bras aux bords en rangées de lames facettées (5 par segment), liserés violets lumineux le long des os et du bord, bracelets dorés
#  - Queue-lame : grande lame facettée à nervure lumineuse, lames latérales ; lames sur le dos, les épaules, les genoux et les cuisses
#  - Épique : iris, liserés, nervure de la lame et cristaux lumineux (2,4), plastron et ornements dorés, 14 lames et cristaux flottants
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(5531)            # même dragon à chaque exécution
TAG = "OMBRELAME_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
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
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Ténèbres : noir violacé + violet clair lumineux. Lames = métal violet sombre aux facettes nettes.
#    Épique : liserés, iris et cristaux émissifs (2,2 à 2,4), petits ornements dorés.
# ----------------------------------------------------------
M_BODY   = get_mat("Body",       "#33204A", 0.50)   # corps principal, noir violacé
M_BODY2  = get_mat("BodyScale",  "#241636", 0.55)   # écailles sombres, dessus des pattes, orteils
M_SCALEB = get_mat("ScaleB",     "#3F2760", 0.50)   # écailles plus claires
M_DARK   = get_mat("BodyDark",   "#140C1E", 0.55)   # bouche, genoux, ombres
M_CREAM  = get_mat("Belly",      "#8E7BAA", 0.55)   # ventre en plaques, plastron, menton (gris violet)
M_HORN   = get_mat("Horn",       "#6A44A8", 0.40)   # cornes, sourcils
M_TIP    = get_mat("HornTip",    "#C79BFF", 0.30)   # pointes de cornes, accents clairs
M_BLADE  = get_mat("Blade",      "#4A2F6E", 0.28, metallic=0.55)   # lames facettées
M_BLADE2 = get_mat("BladeLight", "#7A55B0", 0.25, metallic=0.55)   # lames claires
M_WING   = get_mat("Membrane",   "#3A2458", 0.55)   # membrane des ailes-bras
M_BONE   = get_mat("WingBone",   "#6A44A8", 0.40)   # os des ailes
M_CLAW   = get_mat("Claw",       "#D9C8F5", 0.30)   # griffes pâles
M_FANG   = get_mat("Fang",       "#EDE6F8", 0.35)   # crocs
M_WHITE  = get_mat("EyeWhite",   "#F2F2F2", 0.30)
M_IRIS   = get_mat("Iris",       "#C79BFF", 0.25, emission="#C79BFF", strength=2.4)   # yeux violets lumineux
M_BLACK  = get_mat("Black",      "#0A0A0A", 0.30)
M_GLOW   = get_mat("Glow",       "#B07CFF", 0.30, emission="#B07CFF", strength=2.4)   # liserés lumineux
M_GOLD   = get_mat("Gold",       "#D8B050", 0.30, metallic=0.85)                       # ornements dorés (Épique)
BLADES = [M_BLADE, M_BLADE, M_BLADE2, M_HORN]
BLADEW = [4, 3, 3, 2]

# ----------------------------------------------------------
# REGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
BW = 2.7                 # largeur du torse
BH = 2.5                 # hauteur du torse
LEG_H = 4.6              # hauteur des pattes (hanche -> sol)
TL = 4.8                 # longueur du torse
PITCH = 18               # inclinaison du torse vers l'avant (degrés)
NECK_L = 3.4             # hauteur du cou
NECK_FWD = 1.6           # avancée du cou
NECK_N = 5               # nombre de maillons du cou
NECK_R = (1.1, 0.8)      # rayon du cou (base, haut)
NECK_BLADES = True       # lames sur les côtés du cou
HEAD_SCALE = 1.3         # taille de la tête
SNOUT_K = 1.0            # longueur du museau
FANGS = 3                # crocs par côté
CHEEK_N = 4              # lames de joue
MANE_RINGS = 3           # anneaux de la crinière en lames
MANE_N = 14              # lames par anneau
MANE_K = 0.8             # longueur des lames de crinière
EYE_GLOW = 2             # éclats lumineux au coin de chaque oeil
CROWN_N = 5              # lames sur le crâne
GOLD = True              # ornements dorés
BELLY_N = 6              # plaques de ventre
FLANK_ROWS = 4
FLANK_COLS = 7
CREST_N = 8              # lames du dos
CREST_SIDE = True
SHOULDER_BLADES = 4      # lames d'épaule
LISERE_FLANK = 3         # liserés lumineux par flanc
LISERE_N = 8             # barres par liseré
LEG_TH_K = 0.5           # épaisseur des pattes (fraction de BW)
THIGH_BLADES = 3
LISERE_LEG = True
WING_SPAN = 7.5
WING_ELBOW = (0.42, 0.3, 0.32)
WING_WRIST = (0.26, -0.1, 0.62)   # x, y en fraction d'envergure ; z = hauteur du poignet en fraction de LEG_H
WING_TIPS = [(0.5, 0.3, 0.95), (0.48, 0.72, 0.68), (0.3, 1.0, 0.3)]
WING_BONE = 0.34
WING_MEMB_T = 0.12
ARM_BLADES = 4
FINGER_BLADES = 4
BLADE_N = 8              # lames par segment du bord de l'aile
TAIL_L = 8.0
TAIL_STEP = 0.9
TAIL_BEV_N = 12
TAIL_SCALES = True
LISERE_TAIL_AT = [2, 4, 7]  # segments de queue qui portent un liseré
TAIL_BLADE = 2.3         # taille de la lame de queue
TAIL_SIDE_BLADES = 2
FX_N = 14
FX_SIZE = 0.8
RIB_BLADES = 6          # lames de côtes par flanc
CREST_MINI = True       # petites lames entre les grandes lames du dos
TAIL_SIDE_ALL = True     # lames latérales sur chaque segment de queue
BEARD_N = 5             # lames sous le menton
CALF_BLADES = 2          # lames sur le tibia

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
#    Wyvern : 2 pattes arrière, tronc penché vers l'avant, les ailes servent de bras (poignet posé devant).
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.2                                    # échelle des petits détails
HS = HEAD_SCALE
P = math.radians(PITCH)
F = Vector((0, -math.cos(P), -math.sin(P)))      # axe du torse, vers l'avant (penché)
SIDEV = Vector((1, 0, 0))
UPT = F.cross(SIDEV)                             # "haut" du torse (perpendiculaire à F)
RT = basis(F)                                    # rotation des blocs du torse
HIP_Z = LEG_H                                    # hauteur de la hanche
ZC = HIP_Z + BH * 0.3 - 0.3 * TL * math.sin(P)   # centre du torse
C = Vector((0, 0, ZC))
PELVIS = C - F * (0.3 * TL)
CHEST = C + F * (0.3 * TL)
NECK_BASE = CHEST + F * (0.17 * TL) + UPT * (BH * 0.28)
NECK_TOP = NECK_BASE + Vector((0, -NECK_FWD, NECK_L))
HEAD_POS = NECK_TOP + Vector((0, -0.25 * HS, 0.35 * HS))
HEAD_PITCH = 12                                  # degrés : la tête regarde un peu vers le bas
TAIL_START = PELVIS + Vector((0, 0.2 * TL, 0.0))

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
wings_root = empty("WINGS_ROOT", master)
H = head_root

def tpos(s, up=0.0, side=0.0):
    """Point du torse : s = position le long de l'axe (en fraction de TL, + vers l'avant)."""
    return C + F * (s * TL) + UPT * up + SIDEV * side

# Petits outils (sans biseau par défaut : le biseau est réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def blade_mesh(W, T, L):
    """LAME facettée (8 triangles) orientée vers +Y : largeur W suivant Z local, épaisseur T suivant X,
    arête centrale marquée. Signe distinctif : ailes-bras et queue en lames."""
    v = [(0, 0, -W * 0.18), (0, 0, W * 0.18), (0, L * 0.38, W / 2), (0, L * 0.38, -W / 2), (0, L, 0),
         (T / 2, L * 0.3, 0), (-T / 2, L * 0.3, 0)]
    f = []
    for e in (5, 6):
        f += [(e, 1, 2), (e, 2, 4), (e, 4, 3), (e, 3, 0), (e, 0, 1)]
    return mesh_from("blade", v, f)

def blade(name, W, T, L, loc, direction, mat, parent, up=(0, 0, 1)):
    """Lame placée : 'up' donne le sens de la largeur."""
    return place(name, blade_mesh(W, T, L), mat, loc, basis(direction, up), parent)

def lisere(name, pts, th, parent, nrm=(0, 0, 1)):
    """Liseré violet lumineux : petites barres émissives posées bout à bout sur la peau."""
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        link(f"{name}_{i}", pts[i], pts[i + 1], th, M_GLOW, parent, up=tuple(nrm), extra=th * 0.5, bevel=0, depth=th * 0.7)

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

def hblade(name, W, T, Ln, loc, direction, mat, up=(0, 0, 1)):
    return blade("Head_" + name, W * HS, T * HS, Ln * HS, hv(loc), direction, mat, H, up)

def hchain(name, pts, t0, t1, mat, up=(0, 0, 1)):
    tchain("Head_" + name, [hv(p) for p in pts], t0 * HS * 1.4, t1 * HS * 1.4, mat, H, up)

def hbar(name, p1, p2, th, mat, up=(0, 0, 1), depth=None):
    bar("Head_" + name, hv(p1), hv(p2), th * HS, mat, H, up, None if depth is None else depth * HS)

# Crâne, museau, arête du museau, mâchoire distincte, ligne de bouche
hwedge("Skull", (1.9, 1.8, 1.7), (0, 0, 0), mat=M_BODY, top_x=0.92, top_y=0.9, bevel=0.10)
hwedge("Snout", (1.55, 2.1 * SNOUT_K, 0.95), (0, -0.6 - 1.05 * SNOUT_K, -0.28), mat=M_BODY,
       top_x=0.94, top_y=0.96, shift_y=-0.06, bevel=0.08)
hbox("SnoutBridge", (1.0, 1.7 * SNOUT_K, 0.12), (0, -0.6 - 0.95 * SNOUT_K, 0.22), mat=M_BODY2)
hbox("Jaw", (1.35, 1.95 * SNOUT_K, 0.3), (0, -0.55 - 1.0 * SNOUT_K, -0.78), mat=M_CREAM)
hbox("MouthLine", (1.58, 1.9 * SNOUT_K, 0.05), (0, -0.6 - 1.05 * SNOUT_K, -0.72), mat=M_DARK)
SNOUT_FRONT = -0.6 - 2.1 * SNOUT_K
SF = SNOUT_FRONT
# Petite lame sur le museau (arête qui court vers le front)
hblade("SnoutBlade", 0.5, 0.1, 1.3 * SNOUT_K + 0.3, (0, SF + 0.5 * SNOUT_K, 0.3), (0, 1, 0.12), M_BLADE2, up=(0, 0, 1))
# Narines
for sgn in (-1, 1):
    hbox(f"Nostril_{sgn}", (0.2, 0.22, 0.06), (sgn * 0.4, SNOUT_FRONT + 0.25, 0.2), mat=M_BLACK)

# Yeux : blanc, iris violet lumineux, pupille (ronde + reflets pour bébé, fendue pour ado / adulte)
if IS_BEBE:
    EW, EH, IW, IH, PW, PH = 0.88, 0.95, 0.68, 0.8, 0.4, 0.56
else:
    EW, EH, IW, IH, PW, PH = 0.55, 0.62, 0.4, 0.52, 0.1, 0.48
for sgn in (-1, 1):
    ey, ez = -0.3, 0.1
    hbox(f"EyeWhite_{sgn}", (0.1, EW, EH), (sgn * 0.96, ey, ez), mat=M_WHITE)
    hbox(f"Iris_{sgn}", (0.08, IW, IH), (sgn * 1.0, ey - 0.02, ez - 0.01), mat=M_IRIS)
    hbox(f"Pupil_{sgn}", (0.07, PW, PH), (sgn * 1.04, ey - 0.03, ez - 0.02), mat=M_BLACK)
    if IS_BEBE:
        hbox(f"Glint_{sgn}", (0.06, 0.2, 0.22), (sgn * 1.07, ey - 0.15, ez + 0.2), mat=M_WHITE)
        hbox(f"Glint2_{sgn}", (0.06, 0.1, 0.1), (sgn * 1.07, ey + 0.12, ez - 0.2), mat=M_WHITE)
        hbox(f"Brow_{sgn}", (0.14, 0.8, 0.16), (sgn * 0.97, ey - 0.02, ez + 0.6), rot=(8, 0, 0), mat=M_HORN)
    else:
        # sourcils sévères violets + lame d'arcade dessus
        hbox(f"Brow_{sgn}", (0.2, 1.0, 0.26), (sgn * 0.97, ey - 0.05, ez + 0.52), rot=(16, 0, 0), mat=M_HORN, bevel=0.02)
        hblade(f"BrowBlade_{sgn}", 0.3, 0.1, 0.9, (sgn * 0.99, ey - 0.4, ez + 0.74), (0, -1, 0.2), M_BLADE2, up=(1, 0, 0))
    # éclats lumineux (liseré) au coin de l'oeil
    for k in range(EYE_GLOW):
        hshard(f"EyeGlow_{sgn}_{k}", 0.16, 0.06, 0.5 + 0.1 * k, (sgn * 0.95, ey + 0.55 + 0.28 * k, ez - 0.05 - 0.12 * k),
               (sgn * 0.5, 0.9, -0.15 * k), M_GLOW, up=(1, 0, 0))

# Crocs (bébé : aucun ; ado : 2 par côté ; adulte : 3 par côté, plus longs)
if FANGS:
    for sgn in (-1, 1):
        for k in range(FANGS):
            fy = SNOUT_FRONT + 0.55 + k * 0.5
            hshard(f"Fang_{sgn}_{k}", 0.2, 0.2, 0.3 + 0.12 * FANGS / 3, (sgn * 0.7, fy, -0.74), (0, 0.05, -1),
                   M_FANG, up=(1, 0, 0))

# Barbe de lames sous le menton
for k in range(BEARD_N):
    bx = -0.5 + 1.0 * k / max(1, BEARD_N - 1)
    hblade(f"Beard_{k}", 0.3, 0.09, 0.8 - 0.2 * abs(bx), (bx, SNOUT_FRONT + 0.9 + 0.1 * abs(bx), -0.9),
           (bx * 0.4, -0.5, -1), BLADES[k % 3], up=(1, 0, 0))

# Oreilles en lame + lames de joue
for sgn in (-1, 1):
    hblade(f"Ear_{sgn}", 0.7, 0.12, 1.15 if not IS_BEBE else 0.8, (sgn * 0.85, 0.5, 0.2), (sgn * 1, 0.6, 0.3), M_BLADE, up=(0, 0, 1))
    for k in range(CHEEK_N):
        hblade(f"Cheek_{sgn}_{k}", 0.42 - 0.04 * k, 0.1, 0.9 - 0.1 * k, (sgn * (0.95 + 0.05 * k), -0.05 + k * 0.4, -0.3 - k * 0.12),
               (sgn * 0.9, 0.7, -0.3), M_BLADE2 if k % 2 else M_BLADE, up=(0, 0, 1))

# Crinière en lames : anneaux d'éclats facettés derrière le crâne et sur la nuque (quelques lames claires)
for ring_i in range(MANE_RINGS):
    cnt = MANE_N - ring_i * 2
    for k in range(cnt):
        ang = math.radians(-150 + k * (300 / (cnt - 1)) + ring_i * 9)
        rad = Vector((math.sin(ang), 0, math.cos(ang)))
        tang = Vector((math.cos(ang), 0, -math.sin(ang)))
        loc = (rad.x * (0.8 + 0.3 * ring_i), 0.65 + ring_i * 0.45, rad.z * (0.75 + 0.3 * ring_i))
        jit = Vector((random.uniform(-0.15, 0.15), random.uniform(0, 0.2), random.uniform(-0.15, 0.15)))
        direction = rad * (0.9 - ring_i * 0.2) + Vector((0, 1.0, 0)) + jit
        Ln = (1.2 + 0.6 * max(0.0, math.cos(ang))) * (1 + 0.25 * ring_i) * MANE_K
        m = [M_BLADE, M_BLADE2, M_HORN][(k + ring_i) % 3]
        hblade(f"Mane_{ring_i}_{k}", 0.62 - ring_i * 0.05, 0.14, Ln, (loc[0] * 1.05, loc[1], loc[2] * 1.05), direction, m, up=tuple(tang))

# Cornes : bébé = 2 petits cônes, ado = recourbées + 1 pointe, adulte = longues, 2 pointes + corne basse (pointes claires)
for sgn in (-1, 1):
    if IS_BEBE:
        hchain(f"Horn_{sgn}", [(sgn * 0.55, 0.2, 0.75), (sgn * 0.78, 0.4, 1.2), (sgn * 0.7, 0.9, 1.6)], 0.34, 0.13, M_HORN)
        hshard(f"HornTip_{sgn}", 0.22, 0.2, 0.55, (sgn * 0.7, 0.9, 1.6), (0, 0.5, 1), M_TIP, up=(1, 0, 0))
    elif IS_ADO:
        a0, a1 = Vector((sgn * 0.6, 0.25, 0.78)), Vector((sgn * 0.85, 0.5, 1.45))
        a2, a3 = Vector((sgn * 1.0, 1.1, 2.1)), Vector((sgn * 0.85, 1.85, 2.5))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.38, 0.14, M_HORN)
        hbar(f"HornTine_{sgn}", a1, (sgn * 1.4, 0.0, 2.15), 0.2, M_HORN)
        hshard(f"HornTip_{sgn}", 0.26, 0.24, 0.7, tuple(a3), (0, 0.7, 0.6), M_TIP, up=(1, 0, 0))
        hshard(f"HornTipB_{sgn}", 0.22, 0.2, 0.6, (sgn * 1.4, 0.0, 2.15), (sgn * 0.4, -0.2, 1), M_TIP, up=(0, 1, 0))
    else:
        a0, a1 = Vector((sgn * 0.6, 0.3, 0.78)), Vector((sgn * 0.95, 0.6, 1.6))
        a2, a3 = Vector((sgn * 1.2, 1.4, 2.3)), Vector((sgn * 1.05, 2.4, 2.8))
        hchain(f"Horn_{sgn}", [a0, a1, a2, a3], 0.46, 0.15, M_HORN)
        hbar(f"HornTine1_{sgn}", a1, (sgn * 1.5, 0.25, 2.1), 0.22, M_HORN)
        hbar(f"HornTine2_{sgn}", a2, (sgn * 1.65, 1.0, 2.9), 0.2, M_HORN)
        hchain(f"HornLow_{sgn}", [(sgn * 0.85, 0.6, 0.35), (sgn * 1.35, 1.2, 0.6), (sgn * 1.6, 1.95, 0.75)], 0.3, 0.12, M_HORN)
        for nm, p, dr in (("A", a3, (0, 0.7, 0.6)), ("B", (sgn * 1.5, 0.25, 2.1), (sgn * 0.5, 0, 1)),
                          ("C", (sgn * 1.65, 1.0, 2.9), (sgn * 0.3, 0.3, 1)), ("D", (sgn * 1.6, 1.95, 0.75), (0, 0.8, 0.2))):
            hshard(f"HornTip{nm}_{sgn}", 0.28, 0.26, 0.75, p, dr, M_TIP, up=(1, 0, 0))
    if GOLD:
        a0 = Vector((sgn * 0.6, 0.3, 0.78))
        a1 = Vector((sgn * 0.95, 0.6, 1.6)) if IS_ADULTE else Vector((sgn * 0.85, 0.5, 1.45))
        hbox(f"HornRing_{sgn}", (0.62, 0.5, 0.2), a0.lerp(a1, 0.5), rot=(0, sgn * 10, 0), mat=M_GOLD)

# Crête du crâne : lames en rangée centrale (dressées vers l'arrière)
for k in range(CROWN_N):
    hblade(f"Crown_{k}", 0.55, 0.14, 1.1 + 0.15 * CROWN_N * 0.4 - 0.12 * abs(k - CROWN_N / 2),
           (0, 0.55 + 0.38 * k, 0.8 + 0.02 * k), (0, 0.55, 1), BLADES[k % 3], up=(1, 0, 0))

# ----------------------------------------------------------
# 10. CORPS : torse en 3 blocs penchés, cou en plaques, ventre, flancs, lames sur le dos, liserés lumineux
# ----------------------------------------------------------
BEV = 0.10 * SC
wedge("Body_Chest", (BW * 1.1, TL * 0.46, BH * 1.06), CHEST - F * (0.02 * TL), RT, M_BODY, body_root,
      top_x=0.88, top_y=0.9, shift_y=-TL * 0.02, bevel=BEV)
box("Body_Mid", (BW * 0.98, TL * 0.44, BH * 0.96), C, RT, M_BODY, body_root, bevel=BEV * 0.8)
wedge("Body_Pelvis", (BW * 1.0, TL * 0.46, BH * 1.0), PELVIS, RT, M_BODY, body_root,
      top_x=0.9, top_y=0.88, shift_y=TL * 0.02, bevel=BEV)
HALF_W = BW * 0.5

# Plastron gris violet + plaques de ventre séparées
box("Body_Plastron", (BW * 0.84, 0.34 * SC, BH * 0.72), CHEST + F * (TL * 0.22) - UPT * (BH * 0.08),
    RT, M_CREAM, body_root, bevel=0.05 * SC)
if GOLD:
    # plastron doré : plaque en wedge + gemme violette lumineuse au centre
    wedge("Body_GoldPlate", (BW * 0.5, 0.18 * SC, BH * 0.34), CHEST + F * (TL * 0.235) + UPT * (BH * 0.0), RT, M_GOLD, body_root,
          top_x=0.7, top_y=1.0, bevel=0.03 * SC)
    crystal("Body_ChestGem", 0.13 * SC, 0.26 * SC, 0.16 * SC, CHEST + F * (TL * 0.245) + UPT * (BH * 0.0), F, M_IRIS, body_root, up=tuple(UPT), sides=4)
for i in range(BELLY_N):
    s = -0.4 + 0.8 * (i + 0.5) / BELLY_N
    pl = (TL * 0.8) / BELLY_N * 0.86
    B(f"Body_Belly_{i}", (BW * 0.8, pl, 0.2 * SC), tpos(s, -BH / 2 + 0.03), RT, M_CREAM, body_root, bevel=0.04 * SC)
    for sgn in (-1, 1):
        B(f"Body_BellySide_{i}_{sgn}", (0.1 * SC, pl, BH * 0.28), tpos(s, -BH * 0.3, sgn * (HALF_W - 0.01)),
          RT, M_CREAM, body_root, bevel=0.03 * SC)

# Écailles en quinconce sur les flancs (pointe vers l'arrière)
for sgn in (-1, 1):
    for r in range(FLANK_ROWS):
        for c in range(FLANK_COLS):
            s = -0.36 + 0.74 * (c + 0.5 * (r % 2)) / FLANK_COLS
            up = BH * (0.24 - 0.17 * r)
            shard(f"Body_Scale_{sgn}_{r}_{c}", BH * 0.3, 0.08 * SC, BH * 0.34, tpos(s, up, sgn * (HALF_W - 0.03 * SC)),
                  -F + SIDEV * sgn * 0.3 - UPT * 0.1, pick([M_BODY2, M_BODY2, M_SCALEB]), body_root, up=(sgn, 0, 0))

# Lames de côtes sous les flancs (pointent vers l'arrière et le bas)
for sgn in (-1, 1):
    for k in range(RIB_BLADES):
        s = -0.3 + 0.62 * k / max(1, RIB_BLADES - 1)
        blade(f"Body_Rib_{sgn}_{k}", 0.5 * SC, 0.12 * SC, 0.95 * SC, tpos(s, -BH * 0.32, sgn * (HALF_W - 0.02)),
              -F * 0.9 - UPT * 0.5 + SIDEV * sgn * 0.5, BLADES[k % 3], body_root, up=tuple(SIDEV * sgn))

# Liserés violets lumineux sur les flancs (signe distinctif) : traits brisés en chevron qui suivent le torse
for sgn in (-1, 1):
    for j in range(LISERE_FLANK):
        up0 = BH * (0.12 - 0.19 * j)
        pts = [tpos(-0.34 + 0.07 * k, up0 + (0.05 * BH if k % 2 else -0.05 * BH), sgn * (HALF_W + 0.04)) for k in range(LISERE_N)]
        lisere(f"Body_Lisere_{sgn}_{j}", pts, 0.09 * SC, body_root, nrm=SIDEV * sgn)

# Cou : courbe lissée du torse vers la tête, un segment sombre + une plaque claire par maillon
NECK_CTRL = []
for tt in (0.0, 0.33, 0.66, 1.0):
    sm = tt * tt * (3 - 2 * tt)
    NECK_CTRL.append(NECK_BASE + Vector((0, -NECK_FWD * sm, NECK_L * tt)))
NECK_SPINE = resample(sample_curve(NECK_CTRL), (NECK_L * 1.05) / NECK_N)
NN = len(NECK_SPINE) - 1
for i in range(NN):
    p1, p2 = NECK_SPINE[i], NECK_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / NN
    r = keyed([(0, NECK_R[0]), (1, NECK_R[1])], s)
    R = basis(p2 - p1)
    dz, sd = R.col[2], R.col[0]               # dz = arrière du cou (dos), sd = côté
    box(f"Body_Neck_{i}", (2 * r, Ln * 1.25, 2 * r * 0.95), mid, R, M_BODY, body_root, bevel=0.06 * SC)
    B(f"Body_NeckPlate_{i}", (2 * r * 0.8, Ln * 0.82, 0.22 * SC), mid - dz * (r * 0.95), R, M_CREAM, body_root)
    # nuque : lame dressée
    blade(f"Body_NeckBlade_{i}", 0.7 * SC, 0.16 * SC, (1.1 - 0.3 * s) * SC * 1.2, mid + dz * r * 0.95,
          dz + (p2 - p1).normalized() * (-0.5), BLADES[i % 3], body_root, up=tuple(sd))
    if NECK_BLADES:
        for sgn in (-1, 1):
            shard(f"Body_NeckSide_{i}_{sgn}", 0.45 * SC, 0.1 * SC, 0.7 * SC, mid + dz * r * 0.5 + sd * sgn * r * 0.95,
                  sd * sgn + dz * 0.3 - (p2 - p1).normalized() * 0.4, M_BLADE2, body_root, up=tuple(dz))

# Dos : rangée de grandes lames, plus une rangée de petites lames de chaque côté (adulte)
for k in range(CREST_N):
    s = -0.38 + 0.78 * k / max(1, CREST_N - 1)
    blade(f"Body_Crest_{k}", 0.9 * SC, 0.18 * SC, (1.5 - 0.35 * abs(k / max(1, CREST_N - 1) - 0.4)) * SC,
          tpos(s, BH / 2 - 0.02), -F * 0.45 + UPT, BLADES[k % 3], body_root, up=(1, 0, 0))
    if CREST_MINI and k < CREST_N - 1:
        shard(f"Body_CrestMini_{k}", 0.55 * SC, 0.12 * SC, 0.75 * SC, tpos(s + 0.39 / max(1, CREST_N - 1), BH / 2 - 0.02),
              -F * 0.4 + UPT, M_BLADE2, body_root, up=(1, 0, 0))
    if CREST_SIDE:
        for sgn in (-1, 1):
            shard(f"Body_CrestSide_{k}_{sgn}", 0.5 * SC, 0.12 * SC, 0.7 * SC, tpos(s + 0.03, BH * 0.4, sgn * BW * 0.28),
                  -F * 0.5 + UPT * 0.8 + SIDEV * sgn * 0.5, M_BLADE, body_root, up=(1, 0, 0))

# Épaules : plaque d'épaule sombre + éventail de lames
for sgn in (-1, 1):
    sh = CHEST + SIDEV * sgn * BW * 0.5 + UPT * BH * 0.42 - F * 0.05 * TL
    wedge(f"Body_ShoulderPad_{sgn}", (BW * 0.5, TL * 0.3, 0.3 * SC + 0.2), sh, RT @ Euler((0, math.radians(sgn * 22), 0)).to_matrix(),
          M_BODY2, body_root, top_x=0.85, top_y=0.85, bevel=0.05 * SC)
    for k in range(SHOULDER_BLADES):
        f_ = k / max(1, SHOULDER_BLADES - 1)
        blade(f"Body_ShoulderBlade_{sgn}_{k}", 0.55 * SC, 0.14 * SC, (1.3 - 0.3 * abs(f_ - 0.4)) * SC,
              sh + SIDEV * sgn * (0.1 * BW) + F * (0.25 - 0.5 * f_) * TL * 0.3 + UPT * 0.1,
              SIDEV * sgn * (0.7 - 0.3 * f_) + UPT * 0.7 - F * (0.2 + 0.6 * f_), BLADES[k % 3], body_root, up=tuple(F))

# ----------------------------------------------------------
# 11. PATTES ARRIÈRE (wyvern : 2 pattes) : hanche, cuisse, tibia, genouillère en lame, pied, 3 doigts + 3 griffes
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.16)
LEG_TH = BW * LEG_TH_K
HIP_Y = PELVIS.y - 0.05 * TL
for sgn in (-1, 1):
    x = sgn * (BW * 0.5 - LEG_TH * 0.2)
    hip = Vector((x, HIP_Y, HIP_Z + BH * 0.05))
    knee = Vector((x + sgn * 0.04 * LEG_TH, HIP_Y - LEG_H * 0.28, LEG_H * 0.5))
    ank = Vector((x, HIP_Y + LEG_H * 0.16, FOOT_H + LEG_H * 0.12))
    wedge(f"Legs_Haunch_{sgn}", (LEG_TH * 1.35, LEG_TH * 1.9, LEG_H * 0.46 + BH * 0.3), hip - Vector((0, -0.05, LEG_H * 0.12)),
          None, M_BODY, legs_root, top_x=0.8, top_y=0.85, shift_y=LEG_TH * 0.1, bevel=0.1 * SC)
    link(f"Legs_Thigh_{sgn}", hip - Vector((0, 0, LEG_H * 0.1)), knee, LEG_TH * 1.2, M_BODY, legs_root, extra=0.2,
         bevel=0.08 * SC, depth=LEG_TH * 1.45)
    link(f"Legs_Shin_{sgn}", knee, ank, LEG_TH * 0.95, M_BODY2, legs_root, extra=0.15, bevel=0.05 * SC, depth=LEG_TH * 1.0)
    B(f"Legs_Knee_{sgn}", (LEG_TH * 1.15, LEG_TH * 0.7, LEG_TH * 0.9), knee + Vector((0, -LEG_TH * 0.15, 0)), None, M_DARK, legs_root)
    # genouillère : lame qui pointe vers l'avant et l'extérieur
    blade(f"Legs_KneeBlade_{sgn}", LEG_TH * 0.7, LEG_TH * 0.22, LEG_TH * 1.5, knee + Vector((sgn * LEG_TH * 0.5, -LEG_TH * 0.35, 0.1)),
          (sgn * 0.5, -1, 0.15), M_BLADE2, legs_root, up=(0, 0, 1))
    # bande claire sur le tibia (+ anneau doré)
    g0, g1 = knee.lerp(ank, 0.3), knee.lerp(ank, 0.8)
    link(f"Legs_Greave_{sgn}", g0, g1, LEG_TH * 1.1, M_CREAM, legs_root, extra=0.05, bevel=0.03 * SC, depth=LEG_TH * 1.12)
    if GOLD:
        ring(f"Legs_Anklet_{sgn}", LEG_TH * 0.62, LEG_TH * 0.28, LEG_TH * 0.24, knee.lerp(ank, 0.9), direction=(ank - knee), mat=M_GOLD,
             parent=legs_root, sides=6)
    B(f"Legs_Heel_{sgn}", (LEG_TH * 0.9, LEG_TH * 0.9, FOOT_H * 1.4), Vector((x, ank.y + LEG_TH * 0.1, FOOT_H * 0.9)), None, M_BODY2, legs_root)
    fy = ank.y - LEG_TH * 0.75
    box(f"Legs_Foot_{sgn}", (LEG_TH * 1.2, LEG_TH * 2.1, FOOT_H), (x, fy, FOOT_H / 2), None, M_BODY, legs_root, bevel=0.06 * SC)
    toe_y = fy - LEG_TH * 1.05 - LEG_TH * 0.1
    for k in (-1, 0, 1):
        B(f"Legs_Toe_{sgn}_{k}", (LEG_TH * 0.3, LEG_TH * 0.5, FOOT_H * 0.72), (x + k * LEG_TH * 0.36, toe_y, FOOT_H * 0.36), None, M_BODY2, legs_root)
        shard(f"Legs_Claw_{sgn}_{k}", LEG_TH * 0.22, LEG_TH * 0.18, LEG_TH * 0.62, (x + k * LEG_TH * 0.36, toe_y - LEG_TH * 0.18, FOOT_H * 0.34),
              (k * 0.12, -1, -0.05), M_CLAW, legs_root)
    for k in range(CALF_BLADES):
        blade(f"Legs_CalfBlade_{sgn}_{k}", LEG_TH * 0.45, LEG_TH * 0.12, LEG_TH * 1.0, knee.lerp(ank, 0.35 + 0.3 * k) + Vector((sgn * LEG_TH * 0.5, LEG_TH * 0.3, 0)),
              (sgn * 0.5, 0.7, -0.3), BLADES[(k + 1) % 3], legs_root, up=(0, 0, 1))
    # lames sur la cuisse (vers l'arrière) et liseré lumineux
    for k in range(THIGH_BLADES):
        blade(f"Legs_ThighBlade_{sgn}_{k}", LEG_TH * 0.5, LEG_TH * 0.14, LEG_TH * (1.1 - 0.2 * k),
              hip.lerp(knee, 0.2 + 0.32 * k) + Vector((sgn * LEG_TH * 0.7, 0.1, 0.0)), (sgn * 0.5, 0.9, 0.2), M_BLADE, legs_root, up=(0, 0, 1))
    if LISERE_LEG:
        pts = [hip.lerp(knee, 0.12 + 0.12 * k) + Vector((sgn * (LEG_TH * 0.72 + 0.03), 0.1 * (-1) ** k * LEG_TH, 0)) for k in range(5)]
        lisere(f"Legs_Lisere_{sgn}", pts, 0.09 * SC, legs_root, nrm=(sgn, 0, 0))

# ----------------------------------------------------------
# 12. AILES-BRAS (wyvern) : épaule, coude vers l'arrière, poignet posé devant, griffes + bracelet,
#     3 doigts qui montent vers l'arrière, membrane sombre dont le bord est une rangée de LAMES facettées
#     avec un liseré violet lumineux le long des os et du bord.
# ----------------------------------------------------------
SP = WING_SPAN
CLAW_L = 0.18 * SP
WRIST_Z = LEG_H * WING_WRIST[2] + CLAW_L * 0.2
for sgn in (-1, 1):
    S = CHEST + SIDEV * sgn * BW * 0.48 + UPT * BH * 0.36 - F * 0.02 * TL
    E = S + Vector((sgn * WING_ELBOW[0] * SP, WING_ELBOW[1] * SP, WING_ELBOW[2] * SP))
    W = Vector((sgn * (BW * 0.5 + WING_WRIST[0] * SP), CHEST.y + WING_WRIST[1] * SP, WRIST_Z))
    tips = [W + Vector((sgn * a * SP, b * SP, c * SP)) for (a, b, c) in WING_TIPS]
    Hpt = Vector((sgn * BW * 0.45, PELVIS.y + 0.12 * TL, PELVIS.z + 0.15 * BH))   # bord de fuite accroché au haut de la hanche
    bn = WING_BONE
    link(f"Wings_{sgn}_Arm", S, E, bn * 1.3, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.3)
    link(f"Wings_{sgn}_Fore", E, W, bn * 1.1, M_BONE, wings_root, up=(0, 1, 0), extra=0.2, bevel=0, depth=bn * 1.1)
    wedge(f"Wings_{sgn}_Shoulder", (bn * 2.2, bn * 2.2, bn * 2.2), S, None, M_BODY2, wings_root, bevel=0.06 * SC)
    for k, tp in enumerate(tips):
        link(f"Wings_{sgn}_Finger_{k}", W, tp, bn * (0.85 - 0.12 * k), M_BONE, wings_root, up=(0, 1, 0), extra=0.1, bevel=0, depth=bn * 0.85)
        # lame au bout de chaque doigt
        blade(f"Wings_{sgn}_TipBlade_{k}", bn * 2.6, bn * 0.9, SP * (0.2 - 0.03 * k), tp, tp - W, M_BLADE2, wings_root, up=(0, 0, 1))
        # liseré lumineux le long de l'os du doigt
        lisere(f"Wings_{sgn}_FingerGlow_{k}", [W.lerp(tp, 0.2 + 0.2 * j) + Vector((0, 0, bn * 0.62)) for j in range(4)], bn * 0.3,
               wings_root, nrm=(0, 0, 1))
    # lames du bord d'attaque (avant-bras) et des doigts
    for j in range(ARM_BLADES):
        p = E.lerp(W, (j + 0.5) / ARM_BLADES)
        blade(f"Wings_{sgn}_ArmBlade_{j}", SP * 0.07, bn * 0.5, SP * 0.12, p + Vector((0, 0, bn * 0.4)), Vector((sgn * 0.15, -0.5, 0.9)),
              BLADES[j % 3], wings_root, up=tuple(W - E))
    for k, tp in enumerate(tips):
        for j in range(FINGER_BLADES):
            p = W.lerp(tp, 0.35 + 0.55 * j / max(1, FINGER_BLADES - 1) if FINGER_BLADES > 1 else 0.6)
            blade(f"Wings_{sgn}_FingerBlade_{k}_{j}", SP * 0.05, bn * 0.5, SP * 0.1, p, Vector((sgn * 0.2, 0.7, 0.35)),
                  BLADES[(j + k) % 3], wings_root, up=tuple(tp - W))
    # membrane : triangles en éventail autour du poignet
    edge = tips + [Hpt]
    for k in range(len(edge) - 1):
        plate(f"Wings_{sgn}_Memb_{k}", [W, edge[k], edge[k + 1]], WING_MEMB_T, M_WING, wings_root)
    plate(f"Wings_{sgn}_Memb_A", [W, Hpt, S], WING_MEMB_T, M_WING, wings_root)
    plate(f"Wings_{sgn}_Memb_B", [W, S, E], WING_MEMB_T, M_WING, wings_root)
    # bord en lames : rangée de lames facettées qui pointent vers l'extérieur le long du bord de fuite,
    # + liseré lumineux juste à l'intérieur du bord
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        nrm = (a - W).cross(b - W).normalized()
        lisere(f"Wings_{sgn}_EdgeGlow_{k}", [a.lerp(b, 0.05 + 0.18 * j).lerp(W, 0.06) + nrm * (WING_MEMB_T * 0.9) for j in range(6)],
               bn * 0.26, wings_root, nrm=tuple(nrm))
        for j in range(BLADE_N):
            t = (j + 0.5) / BLADE_N
            p = a.lerp(b, t)
            out = (p - W).normalized()
            blade(f"Wings_{sgn}_EdgeBlade_{k}_{j}", SP * 0.085, WING_MEMB_T * 1.5, SP * random.uniform(0.12, 0.18) * (1.0 + 0.4 * (j % 2)),
                  p - out * SP * 0.02, out * 0.9 + Vector((0, 0.25, -0.35)), BLADES[(j + k) % 3], wings_root, up=tuple(nrm))
    # poignet : bloc, bracelet doré, grande griffe + 2 petites griffes
    wedge(f"Wings_{sgn}_WristBlock", (bn * 2.2, bn * 2.4, bn * 2.0), W, None, M_BODY2, wings_root, bevel=0.0)
    blade(f"Wings_{sgn}_WristBlade", bn * 2.2, bn * 0.8, SP * 0.13, W + Vector((sgn * bn * 0.6, 0.0, bn * 0.9)), (sgn * 0.4, 0.3, 1), M_BLADE2,
          wings_root, up=(1, 0, 0))
    if GOLD:
        ring(f"Wings_{sgn}_Bracelet", bn * 1.45, bn * 0.7, bn * 0.55, E.lerp(W, 0.85), direction=(W - E), mat=M_GOLD, parent=wings_root, sides=6)
    fd = Vector((sgn * 0.12, -1, -0.75))
    shard(f"Wings_{sgn}_ThumbClaw", bn * 1.2, bn * 1.0, CLAW_L, W + Vector((0, -0.1, -0.05)), fd, M_CLAW, wings_root)
    for k in (-1, 1):
        shard(f"Wings_{sgn}_Claw_{k}", bn * 0.8, bn * 0.7, CLAW_L * 0.7, W + Vector((k * bn * 0.9, -0.1, -0.02)), (k * 0.25, -1, -0.75), M_CLAW, wings_root)

# ----------------------------------------------------------
# 13. QUEUE EN LAME : courbe lissée, segments, lames sur le dos, liserés, GRANDE LAME facettée au bout
# ----------------------------------------------------------
TAIL_CTRL = []
for tt, dz, dx in ((0, 0, 0), (0.2, -0.15, 0.0), (0.45, -0.28, 0.25), (0.7, -0.22, 0.1), (0.9, 0.02, -0.2), (1.0, 0.2, -0.3)):
    TAIL_CTRL.append(TAIL_START + Vector((dx * BW * 0.3, TAIL_L * tt, dz * TAIL_L * 0.35)))
TAIL_R = [(0.0, BW * 0.40), (0.3, BW * 0.34), (0.6, BW * 0.25), (0.85, BW * 0.17), (1.0, BW * 0.12)]
TAIL_SPINE = resample(sample_curve(TAIL_CTRL), TAIL_STEP)
TN = len(TAIL_SPINE) - 1
for i in range(TN):
    p1, p2 = TAIL_SPINE[i], TAIL_SPINE[i + 1]
    Ln = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / TN
    r = keyed(TAIL_R, s)
    R = basis(p2 - p1)
    dz, sd = R.col[2], R.col[0]
    t_ = (p2 - p1).normalized()
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.3, 2 * r * 0.95), mid, R, M_BODY, tail_root, bevel=(0.05 * SC if i < TAIL_BEV_N else 0))
    if s < 0.78:
        B(f"Tail_Belly_{i}", (2 * r * 0.8, Ln * 0.82, 0.18 * SC), mid - dz * (r * 0.95), R, M_CREAM, tail_root)
    blade(f"Tail_Crest_{i}", 0.85 * r + 0.2, 0.16 * SC, 0.6 * SC + r * 0.9, mid + dz * r * 0.85, dz + t_ * 0.7, BLADES[i % 3], tail_root, up=tuple(sd))
    if TAIL_SIDE_ALL and s < 0.9:
        for sgn in (-1, 1):
            blade(f"Tail_SideSpike_{i}_{sgn}", 0.5 * r + 0.2, 0.1 * SC, 0.5 * SC + r * 0.9, mid + sd * sgn * r * 0.9,
                  sd * sgn + t_ * 0.8, BLADES[(i + 1) % 3], tail_root, up=tuple(dz))
    if TAIL_SCALES and i % 2 == 1 and s < 0.85:
        for sgn in (-1, 1):
            shard(f"Tail_Scale_{i}_{sgn}", r * 0.7, 0.06 * SC, r * 1.0, mid + sd * sgn * (r - 0.03), sd * sgn * 0.3 + t_,
                  pick([M_BODY2, M_SCALEB]), tail_root, up=(sgn, 0, 0))
    if i in LISERE_TAIL_AT:
        for sgn in (-1, 1):
            lisere(f"Tail_Lisere_{i}_{sgn}", [mid + sd * sgn * (r + 0.03) + t_ * Ln * (-0.5 + 0.33 * j) + dz * r * 0.25 * (-1) ** j for j in range(4)],
                   0.08 * SC, tail_root, nrm=tuple(sd * sgn))
tip = TAIL_SPINE[-1]
tt_ = (TAIL_SPINE[-1] - TAIL_SPINE[-2]).normalized()
RT_TIP = basis(tt_)
tdz, tsd = RT_TIP.col[2], RT_TIP.col[0]
B("Tail_TipBlock", (BW * 0.3, 0.6 * SC, BW * 0.3), tip, RT_TIP, M_BODY2, tail_root)
if GOLD:
    ring("Tail_TipRing", BW * 0.2, BW * 0.12, 0.3 * SC, tip - tt_ * 0.3 * SC, direction=tt_, mat=M_GOLD, parent=tail_root, sides=6)
# grande lame de queue : lame facettée verticale, deuxième lame plus claire par-dessus, nervure lumineuse, lames latérales
TB = TAIL_BLADE
blade("Tail_Blade", TB * 1.1, TB * 0.18, TB * 2.6, tip + tt_ * 0.1, tt_ + Vector((0, 0, 0.12)), M_BLADE, tail_root, up=tuple(tdz))
blade("Tail_BladeEdge", TB * 0.5, TB * 0.22, TB * 2.3, tip + tt_ * 0.25, tt_ + Vector((0, 0, 0.12)), M_BLADE2, tail_root, up=tuple(tdz))
shard("Tail_BladeRib", TB * 0.12, TB * 0.1, TB * 2.0, tip + tt_ * 0.3 + tdz * 0.02, tt_ + Vector((0, 0, 0.12)), M_GLOW, tail_root, up=tuple(tdz))
for sgn in (-1, 1):
    for j in range(TAIL_SIDE_BLADES):
        blade(f"Tail_SideBlade_{sgn}_{j}", TB * 0.55, TB * 0.12, TB * (1.1 - 0.25 * j),
              tip - tt_ * (0.2 * SC + 0.8 * TB * j * 0.5), tt_ * 0.6 + tsd * sgn * 0.9 + tdz * (0.1 - 0.3 * j), BLADES[j % 3], tail_root, up=tuple(tdz))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (ÉPIQUE) + FX
#     Épique : crinière et ailes en lames, liserés / iris / cristaux lumineux (2,2 à 2,4),
#     ornements dorés (cornes, plastron, poignets, chevilles, queue), cristaux et lames flottants.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = HEAD_POS.z + HS * (3.4 if IS_ADULTE else (2.0 if IS_ADO else 1.5))
    for k in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (SP * 0.6 + BW), random.uniform(-TL * 0.9 - NECK_FWD, TL * 0.5 + TAIL_L * 0.4),
                    random.uniform(LEG_H * 0.8, top_z * 0.95)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if k % 3 == 2:
            crystal(f"FX_Crystal_{k}", FX_SIZE * 0.14, FX_SIZE * 0.3, FX_SIZE * 0.22, p, dirv, M_GLOW, master, sides=4)
        else:
            blade(f"FX_Blade_{k}", FX_SIZE * 0.5, FX_SIZE * 0.14, FX_SIZE * random.uniform(1.0, 1.5), p, dirv, pick([M_BLADE, M_BLADE2]), master)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
