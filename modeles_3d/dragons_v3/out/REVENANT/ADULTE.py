import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Revenant · Adulte
#  Secret · Ténèbres · Hydre · monde 5
#  - Adulte : trois têtes imposantes (la centrale plus grande, les latérales tournées vers l'extérieur), corps massif, sans ailes
#  - Cage thoracique d'os apparente autour d'un vide lumineux, colonne d'os, épaulières d'os, patte arrière gauche squelette
#  - Contours qui se dissipent en fumée violette, crêtes translucides, queue qui devient fantôme puis se défait en fragments
#  - Secret complet : tête gauche à mâchoire dissoute, tête droite à corne cassée et crâne troué, voile déchiré, feux follets lilas, yeux et fissures émissifs
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(5317)            # même dragon à chaque exécution
TAG = "REVENANT_ADULTE"      # préfixe de tous les objets, matériaux et de la collection
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
# RÉGLAGES DU STADE (modifie ces valeurs pour retoucher la forme)
# ----------------------------------------------------------
STAGE = "ADULTE"
GLOW_STR = 3.0
BW = 3.3
BH = 2.7
LEG_H = 3.0
TORSO_L = 4.6
NECK_L = 4.6
NECK_LEAN = 1.0
NECK_N = 7
NECK_R = (0.95, 0.74)
NECK_CURVE = 0.8
HEAD_SCALE = 1.05
HEAD_PITCH = 6
HEADS = [(0.0, 0.0, 0.0, 1.0, 0), (-3.0, 0.9, -2.0, 0.82, -26), (3.0, 0.9, -2.0, 0.82, 26)]
SNOUT_L = 1.45
JAW_OPEN = 9
FANGS = 3
HORN_L = 1.4
WISP_H = 1.2
EYE = (0.5, 0.45, 0.36, 0.38, 0.09, 0.34)
BROW_TILT = 20
HEAD_CREST = 6
CHEEK_N = 4
HEAD_CRACKS = 3
RIB_N = 8
BELLY_N = 8
CREST_N = 14
CREST_H = 1.5
SCALE_ROWS = 6
FLANK_CRACKS = 5
SHROUD_N = 9
SMOKE_N = 12
SMOKE_LEN = 1.3
BRACER_K = 0.45
CLAW_K = 0.6
TAIL_L = 6.0
TAIL_STEP = 0.7
TAIL_FADE = 0.62
TAIL_FRAG = 8
TAIL_TIP = 1.3
FX_N = 36
FX_SIZE = 0.4

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Corps noir-violet très sombre, os pâles apparents (côtes, vertèbres, mâchoires, bracelets),
#    ventre violet, fumée violette translucide (alpha 0.5-0.65), feux follets et yeux lilas émissifs.
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#1A1420", 0.60)   # corps, crâne, cous
M_BODYD = get_mat("BodyDark",  "#100C13", 0.65)   # genoux, ombres, épaules, sourcils
M_SCA   = get_mat("ScaleA",    "#130F18", 0.55)   # écailles sombres
M_SCB   = get_mat("ScaleB",    "#322544", 0.50)   # écailles claires (violet)
M_NOSE  = get_mat("Nostril",   "#0C090E", 0.30)   # narines
M_VOID  = get_mat("Void",      "#050308", 0.90)   # vide : orbites, cage thoracique, bouche
M_BELLY = get_mat("Belly",     "#4E2E78", 0.50)   # ventre en plaques, plastron, gorge
M_BONE  = get_mat("Bone",      "#D8CCEA", 0.55)   # os apparents (côtes, vertèbres, museau, mâchoire)
M_TIP   = get_mat("HornTip",   "#CDB3FF", 0.35)   # pointes des cornes, accents clairs
M_CREST = get_mat("Crest",     "#8C64C8", 0.45, alpha=0.62)   # crêtes translucides
M_CREST2= get_mat("Crest2",    "#4E2E78", 0.45, alpha=0.62)   # crête secondaire translucide
M_SMOKE = get_mat("Smoke",     "#8C64C8", 0.40, alpha=0.55)   # fumée violette
M_SMOKE2= get_mat("SmokeLight","#B79AEE", 0.40, alpha=0.50)   # fumée claire
M_SMOKED= get_mat("SmokeDark", "#4E2E78", 0.40, alpha=0.65)   # fumée sombre / parties fantômes
M_CLAW  = get_mat("Claw",      "#E6DCF5", 0.35)   # griffes pâles
M_EYE   = get_mat("Eye",       "#CDB3FF", 0.20, emission="#CDB3FF", strength=GLOW_STR + 0.5)   # yeux
M_GLOW  = get_mat("Glow",      "#CDB3FF", 0.20, emission="#CDB3FF", strength=GLOW_STR)         # fissures, feux follets
M_WISP2 = get_mat("WispViolet","#8C64C8", 0.25, emission="#8C64C8", strength=GLOW_STR)         # cœur violet des flammes
M_WHITE = get_mat("White",     "#F2F2F2", 0.30)   # yeux de bébé, crocs
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles
SMOKES = [M_SMOKE, M_SMOKE2, M_SMOKED]
BODY_MATS, BODY_W = [M_BODY, M_SCA, M_SCB], [6, 3, 1.2]

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

# Une tête par entrée de HEADS : HEAD_ROOT (centrale), HEAD2_ROOT (gauche), HEAD3_ROOT (droite)
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
    """Suite de barres qui s'affinent (cornes, côtes)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def diamond(name, base, direction, length, width, mat, parent, up=(1, 0.3, 0), t=0.05):
    """Plaque en losange (fumée, voile, éclat plat) : base, 2 côtés au tiers, pointe."""
    base = Vector(base)
    m = basis(direction, up)
    fx, fy = m.col[0], m.col[1]
    pts = [base, base + fy * (0.4 * length) + fx * (width / 2), base + fy * length,
           base + fy * (0.4 * length) - fx * (width / 2)]
    return plate(name, pts, t, mat, parent)

def plume(name, base, direction, size, parent, n=3):
    """SIGNE DISTINCTIF : volute de fumée violette translucide (n losanges qui montent et s'effilent)."""
    base, d = Vector(base), Vector(direction).normalized()
    for j in range(n):
        jit = Vector((random.uniform(-0.35, 0.35), random.uniform(-0.35, 0.35), random.uniform(-0.1, 0.2)))
        diamond(f"{name}_{j}", base + d * (size * 0.5 * j) + jit * size * 0.35, d + jit * 0.8, size * (1.0 - 0.2 * j),
                size * (0.55 - 0.1 * j), SMOKES[(j + len(name)) % 3], parent, up=(1, 0.3, 0.2), t=0.05 * size)

def spike(name, base, direction, w, L, parent, up=(1, 0, 0), tip=True, mat=None):
    """Pic sombre à pointe d'os pâle."""
    d = Vector(direction).normalized()
    shard(name, w, w * 0.6, L, base, d, mat or M_BODYD, parent, up=up)
    if tip:
        shard(name + "_Tip", w * 0.42, w * 0.28, L * 0.38, Vector(base) + d * (L * 0.66), d, M_BONE, parent, up=up)

def crack(name, p0, steps, parent, th=0.06, depth=0.05):
    """Fissure émissive lilas en zigzag."""
    p = Vector(p0)
    for i, st in enumerate(steps):
        q = p + Vector(st)
        bar(f"{name}_{i}", p, q, th, M_GLOW, parent, depth=depth)
        p = q

def wisp(name, base, h, w, parent):
    """SIGNE DISTINCTIF : feu follet lilas (flamme en 2 éclats + petite perle lumineuse au-dessus)."""
    shard(name + "_A", w, w * 0.35, h, base, (0, 0.18, 1), M_GLOW, parent, up=(0, 1, 0))
    shard(name + "_B", w * 0.7, w * 0.3, h * 0.65, Vector(base) + Vector((w * 0.1, 0, 0)), (0.25, 0, 1), M_WISP2, parent, up=(1, 0, 0))
    crystal(name + "_Orb", w * 0.2, w * 0.2, w * 0.22, Vector(base) + Vector((0, h * 0.05, h * 1.12)), (0, 0, 1), M_EYE,
            parent, sides=4)

# ----------------------------------------------------------
# 9. TÊTES : une fonction construit une tête complète en coordonnées locales de son root.
#    Tête 1 = centrale (complète). Tête 2 (gauche) : mâchoire à moitié dissoute en fumée.
#    Tête 3 (droite) : corne cassée et fenêtre de vide lumineux dans le crâne (asymétrie).
# ----------------------------------------------------------
def build_head(H, k, hs):
    P = f"Head{k}_"
    def hv(v):
        return tuple(c * hs for c in v)
    def hb(name, size, loc, rot=None, mat=None, bevel=0.0):
        return box(P + name, hv(size), hv(loc), rot, mat, H, bevel * hs)
    SNOUT_FRONT = -0.85 - SNOUT_L

    # Crâne sombre + museau + arête osseuse (os apparents) + plaques d'os sur le front
    wedge(P + "Skull", hv((1.9, 1.75, 1.6)), (0, 0, 0), None, M_BODY, H, top_x=0.86, top_y=0.9, bevel=0.10 * hs)
    wedge(P + "Snout", hv((1.5, SNOUT_L + 0.3, 0.8)), hv((0, -0.85 - SNOUT_L / 2 + 0.15, -0.3)), None, M_BODY, H,
          top_x=0.92, top_y=0.95, bevel=0.07 * hs)
    hb("SnoutBridge", (0.75, SNOUT_L * 0.9, 0.16), (0, SNOUT_FRONT * 0.55 - 0.1, 0.16), mat=M_BONE)
    if not IS_BEBE:
        hb("BoneBrow", (1.3, 0.45, 0.14), (0, -0.3, 0.83), rot=(-8, 0, 0), mat=M_BONE)
        hb("BoneTemple", (1.3, 0.2, 0.12), (0, 0.15, 0.82), rot=(-8, 0, 0), mat=M_BONE)

    # Mâchoire d'os distincte (tête 2 : la moitié avant se dissout en fumée) + gorge violette + vide de la bouche
    jaw_rot = (-JAW_OPEN, 0, 0)
    jl = SNOUT_L + 0.5
    if k == 2 and not IS_BEBE:
        jl = SNOUT_L * 0.55 + 0.4
    jy = -0.75 - jl / 2 + 0.2 + (0 if jl == SNOUT_L + 0.5 else 0.0)
    hb("Jaw", (1.36, jl, 0.42), (0, jy + (SNOUT_L + 0.5 - jl) * 0.0, -0.86 - JAW_OPEN * 0.012), rot=jaw_rot,
       mat=M_BONE, bevel=0.04)
    if k == 2 and not IS_BEBE:   # reste de mâchoire fantôme : plaques translucides qui s'effilent
        for c in range(3):
            diamond(P + f"GhostJaw_{c}", hv((-0.4 + 0.4 * c, jy - jl / 2 - 0.05, -0.86)), hv((0, -1, -0.15)),
                    0.9 * hs * (1 - 0.2 * c), 0.42 * hs, SMOKES[c], H, up=(0, 0, 1), t=0.05 * hs)
    hb("Throat", (1.2, 1.1, 0.3), (0, 0.15, -0.88), mat=M_BELLY)
    if JAW_OPEN > 0:
        hb("MouthVoid", (1.2, SNOUT_L + 0.2, 0.2 + JAW_OPEN * 0.012), (0, -0.85 - SNOUT_L / 2 + 0.2, -0.64), mat=M_VOID)
    else:
        hb("MouthLine", (1.52, SNOUT_L + 0.2, 0.06), (0, -0.85 - SNOUT_L / 2 + 0.2, -0.66), mat=M_VOID)

    # Narines : deux trous de vide
    for sgn in (-1, 1):
        hb(f"Nostril_{sgn}", (0.26, 0.22, 0.08), (sgn * 0.42, SNOUT_FRONT + 0.3, 0.14), mat=M_VOID)

    # Yeux. Bébé : grands yeux doux (blanc, iris lilas lumineux, pupille, reflets).
    # Ado / adulte : orbite vide + éclat lilas en fente, sourcils d'os sombres inclinés.
    for sgn in (-1, 1):
        ex, ey, ez = sgn * 0.97, -0.38, 0.12
        if IS_BEBE:
            hb(f"EyeWhite_{sgn}", (0.1, EYE[0], EYE[1]), (ex, ey, ez), mat=M_WHITE)
            hb(f"Iris_{sgn}", (0.08, EYE[2], EYE[3]), (ex + sgn * 0.04, ey - 0.03, ez - 0.02), mat=M_EYE)
            hb(f"Pupil_{sgn}", (0.07, EYE[4], EYE[5]), (ex + sgn * 0.08, ey - 0.04, ez - 0.03), mat=M_BLACK)
            hb(f"Glint_{sgn}", (0.06, 0.18, 0.2), (ex + sgn * 0.11, ey - 0.17, ez + 0.2), mat=M_WHITE)
            hb(f"Glint2_{sgn}", (0.06, 0.09, 0.09), (ex + sgn * 0.11, ey + 0.1, ez - 0.2), mat=M_WHITE)
        else:
            hb(f"Socket_{sgn}", (0.1, EYE[0] + 0.2, EYE[1] + 0.12), (ex, ey, ez), mat=M_VOID)
            hb(f"EyeShard_{sgn}", (0.1, EYE[2] + 0.1, EYE[3] * 0.55), (ex + sgn * 0.05, ey - 0.03, ez - 0.02),
               rot=(16, 0, 0), mat=M_EYE)
            hb(f"EyeCore_{sgn}", (0.1, EYE[4] + 0.1, EYE[3] * 0.3), (ex + sgn * 0.08, ey - 0.03, ez - 0.02),
               rot=(16, 0, 0), mat=M_WHITE)
            hb(f"Brow_{sgn}", (0.26, EYE[0] + 0.35, 0.24), (sgn * 0.93, ey - 0.05, ez + EYE[1] / 2 + 0.2),
               rot=(BROW_TILT, 0, sgn * -6), mat=M_BODYD, bevel=0.02)

    # Crocs d'os (ado : 2 par côté ; adulte : 3 par côté + crocs du bas)
    for sgn in (-1, 1):
        for f in range(FANGS):
            fy = SNOUT_FRONT + 0.35 + f * 0.45
            shard(f"{P}Fang_{sgn}_{f}", 0.18 * hs, 0.18 * hs, (0.34 + 0.06 * FANGS) * hs, hv((sgn * 0.55, fy, -0.68)),
                  (0, 0.05, -1), M_WHITE, H, up=(1, 0, 0))
            if IS_ADULTE and f < 2 and not (k == 2 and sgn == -1):
                shard(f"{P}FangLow_{sgn}_{f}", 0.14 * hs, 0.14 * hs, 0.3 * hs,
                      hv((sgn * 0.45, fy + 0.25, -0.75 - JAW_OPEN * 0.02)), (0, 0.05, 1), M_WHITE, H, up=(1, 0, 0))

    # Cornes sombres à anneau d'os, pointe d'os et FEU FOLLET lilas. Tête 3 : corne droite cassée.
    for sgn in (-1, 1):
        broken = (k == 3 and sgn == 1 and not IS_BEBE)
        if IS_BEBE:
            hb(f"Horn_{sgn}", (0.36, 0.36, 0.42), (sgn * 0.55, 0.3, 0.95), rot=(-15, sgn * 10, 0), mat=M_BODYD)
            hb(f"HornTip_{sgn}", (0.22, 0.22, 0.2), (sgn * 0.57, 0.36, 1.2), rot=(-15, sgn * 10, 0), mat=M_BONE)
            wisp(f"{P}Wisp_{sgn}", hv((sgn * 0.58, 0.38, 1.33)), WISP_H * hs, 0.34 * hs, H)
        else:
            L = HORN_L
            pts = [(sgn * 0.6, 0.25, 0.7), (sgn * 0.82, 0.55, 0.7 + 0.45 * L), (sgn * 0.9, 0.55 + 0.55 * L, 0.7 + 0.8 * L),
                   (sgn * 0.85, 0.55 + 1.05 * L, 0.7 + 0.95 * L)]
            if broken:
                pts = pts[:3]
            tchain(f"{P}Horn_{sgn}", [hv(p) for p in pts], 0.36 * hs, 0.2 * hs, M_BODYD, H)
            B(f"{P}HornRing_{sgn}", hv((0.44, 0.44, 0.12)), hv(pts[1]), basis(Vector(pts[1]) - Vector(pts[0]), (1, 0, 0)),
              M_BONE, H)
            if broken:   # cassure : éclats d'os et fumée qui s'échappe du moignon
                for c in range(3):
                    shard(f"{P}HornBreak_{sgn}_{c}", 0.2 * hs, 0.14 * hs, 0.5 * hs, hv(pts[2]),
                          (0.3 * c - 0.3, 0.4, 1), M_BONE, H, up=(1, 0, 0))
                plume(f"{P}HornSmoke_{sgn}", hv(pts[2]) , (0.2, 0.3, 1), 0.8 * hs, H, n=3)
            else:
                tip_dir = Vector(pts[3]) - Vector(pts[2])
                shard(f"{P}HornTip_{sgn}", 0.24 * hs, 0.24 * hs, 0.6 * hs * L, hv(pts[3]), tip_dir, M_BONE, H)
                wisp(f"{P}Wisp_{sgn}", hv(Vector(pts[3]) + tip_dir.normalized() * 0.55 * L + Vector((0, 0, 0.1))),
                     WISP_H * hs, 0.38 * hs, H)
            if IS_ADULTE:
                spike(f"{P}BrowHorn_{sgn}", hv((sgn * 0.9, -0.2, 0.55)), (sgn * 0.4, 0.6, 0.9), 0.24 * hs, 0.75 * hs, H)

    # Crête translucide de pics derrière le crâne (alpha) + volutes de fumée sur la nuque
    for c in range(HEAD_CREST):
        y = -0.3 + c * 0.45
        shard(f"{P}Crest_{c}", 0.34 * hs, 0.14 * hs, (0.8 + 0.18 * c) * hs, hv((0, y, 0.74)), (0, 0.7, 1),
              M_CREST if c % 2 == 0 else M_CREST2, H, up=(1, 0, 0))
    plume(f"{P}NapeSmoke", hv((0, 0.55, 0.55)), (0, 0.6, 1), 1.0 * hs, H, n=3)

    # Joues : pics d'os pâles qui pointent vers l'arrière
    for sgn in (-1, 1):
        for c in range(CHEEK_N):
            spike(f"{P}Cheek_{sgn}_{c}", hv((sgn * 0.85, 0.2 + c * 0.25, -0.45 - c * 0.15)),
                  (sgn * 0.6, 1, -0.2 - 0.25 * c), 0.28 * hs, (0.7 - 0.1 * c) * hs, H, up=(0, 0, 1))

    # Fissures lilas lumineuses sur les côtés du crâne
    for sgn in (-1, 1):
        for c in range(HEAD_CRACKS):
            crack(f"{P}Crack_{sgn}_{c}", hv((sgn * 0.985, 0.1 + 0.35 * c, 0.55 - 0.5 * c)),
                  [hv((0, 0.2, -0.25)), hv((0, -0.12, -0.22)), hv((0, 0.22, -0.2))], H, th=0.06 * hs, depth=0.04 * hs)
    # Tête 3 : fenêtre de vide dans le crâne (côté droit), avec une lueur à l'intérieur
    if k == 3 and not IS_BEBE:
        hb("SkullHole", (0.1, 0.7, 0.5), (0.97, 0.3, 0.0), mat=M_VOID)
        hb("SkullHoleGlow", (0.1, 0.3, 0.2), (0.985, 0.35, -0.02), mat=M_GLOW)

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_head(H, k + 1, HEAD_SCALE * hd[3])

# ----------------------------------------------------------
# 10. CORPS : torse et bassin sombres, côtes d'os apparentes (flanc gauche ouvert sur le vide, flanc droit voilé de fumée),
#     colonne d'os, ventre en plaques violettes, plastron avec âme lumineuse, écailles en quinconce, cous Catmull-Rom
# ----------------------------------------------------------
wedge("Body_Chest", (BW * 1.05, TL * 0.56, BH), (0, -TL * 0.2, ZC), None, M_BODY, body_root, top_x=0.92, top_y=0.95,
      bevel=0.12 * SC)
wedge("Body_Pelvis", (BW * 0.95, TL * 0.5, BH * 0.92), (0, TL * 0.25, ZC - 0.04 * BH), None, M_BODY, body_root,
      top_x=0.92, top_y=0.95, bevel=0.12 * SC)
B("Body_Waist", (BW * 0.9, TL * 0.3, BH * 0.85), (0, 0.02 * TL, ZC - 0.02 * BH), None, M_BODYD, body_root)

# Plaques de ventre violettes bien séparées
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.84
    B(f"Body_Belly_{i}", (BW * 0.72, pl, 0.26 * SC), (0, y, ZC - BH * 0.47 - 0.06 * SC), mat=M_BELLY, parent=body_root)

# Plastron : plaques violettes + sternum d'os + âme lumineuse (cristal lilas)
PY = -TL * 0.48 - 0.1 * SC
for r in range(3):
    B(f"Body_Plastron_{r}", (BW * (0.7 - 0.1 * r), 0.28 * SC, BH * 0.2), (0, PY, ZC + BH * (0.12 - 0.24 * r)),
      mat=M_BELLY, parent=body_root)
B("Body_Sternum", (BW * 0.12, 0.2 * SC, BH * 0.62), (0, PY - 0.08 * SC, ZC - BH * 0.1), mat=M_BONE, parent=body_root)
crystal("Body_Soul", 0.26 * SC, 0.1 * SC, 0.24 * SC, (0, PY - 0.18 * SC, ZC - BH * 0.08), (0, -1, 0), M_GLOW, body_root)

# CÔTES D'OS : une cage bombée au-dessus des cuisses. Flanc gauche (-X) = vide + cœur lumineux + RIB_N côtes ;
# flanc droit (+X) = voile de fumée, moins de côtes (silhouette asymétrique)
RIB_Y0, RIB_L = -TL * 0.22, TL * 0.44
for sgn in (-1, 1):
    n_rib = RIB_N if sgn == -1 else max(2, RIB_N - 2)
    B(f"Body_RibVoid_{sgn}", (0.3 * SC, RIB_L, BH * 0.5), (sgn * BW * 0.5, RIB_Y0, ZC + BH * 0.27), mat=M_VOID, parent=body_root)
    if sgn == -1:
        B("Body_RibHeart", (0.2 * SC, RIB_L * 0.36, BH * 0.2), (sgn * BW * 0.55, RIB_Y0, ZC + BH * 0.25), mat=M_GLOW,
          parent=body_root)
    else:
        diamond("Body_RibVeil", (sgn * BW * 0.6, RIB_Y0 + RIB_L * 0.5, ZC + BH * 0.5), (0.3, -1, -0.4), RIB_L * 1.0,
                BH * 0.55, M_SMOKED, body_root, up=(sgn, 0, 0), t=0.05 * SC)
    for j in range(n_rib):
        y = RIB_Y0 - RIB_L * 0.42 + RIB_L * 0.84 * (j + 0.5) / n_rib
        pts = [(sgn * BW * 0.3, y, ZC + BH * 0.52), (sgn * BW * 0.58, y + 0.04 * SC, ZC + BH * 0.46),
               (sgn * BW * 0.67, y + 0.1 * SC, ZC + BH * 0.24), (sgn * BW * 0.6, y + 0.16 * SC, ZC + BH * 0.0)]
        tchain(f"Body_Rib_{sgn}_{j}", pts, 0.22 * SC, 0.16 * SC, M_BONE, body_root, up=(0, 1, 0))

# Épaules (ado / adulte) : wedge sombre + plaque d'os
if not IS_BEBE:
    for sgn in (-1, 1):
        wedge(f"Body_Shoulder_{sgn}", (BW * 0.42, TL * 0.36, BH * 0.62), (sgn * BW * 0.42, -TL * 0.3, ZC + BH * 0.2),
              (0, sgn * 12, 0), M_BODYD, body_root, top_x=0.7, top_y=0.75, bevel=0.06 * SC)
        wedge(f"Body_ShoulderBone_{sgn}", (BW * 0.34, TL * 0.26, BH * 0.16), (sgn * BW * 0.48, -TL * 0.3, ZC + BH * 0.56),
              (0, sgn * 14, 0), M_BONE, body_root, top_x=0.7, top_y=0.7, bevel=0.03 * SC)

# Écailles en quinconce sur les flancs (SCALE_ROWS rangées)
sc_cols = max(3, int(TL * 0.8 / (0.8 * SC)))
for sgn in (-1, 1):
    for r in range(SCALE_ROWS):
        for c in range(sc_cols):
            y = -TL * 0.5 + (TL * 1.0) * (c + 0.5 * (r % 2)) / sc_cols + 0.2
            z = ZC + BH * (0.38 - 0.62 * r / max(1, SCALE_ROWS - 1))
            if RIB_Y0 - RIB_L * 0.55 < y < RIB_Y0 + RIB_L * 0.55 and z > ZC - BH * 0.05:
                continue            # on ne couvre pas la cage thoracique
            shard(f"Body_Scale_{sgn}_{r}_{c}", 0.7 * SC, 0.22 * SC, 0.95 * SC, (sgn * BW * 0.5, y, z),
                  (sgn * 0.35, 1, -0.2), M_SCB if (r + c) % 3 == 0 else M_SCA, body_root, up=(0, 0, 1))

# Colonne d'os le long du dos + crête translucide + volutes de fumée
for c in range(CREST_N):
    y = -TL * 0.36 + (TL * 0.78) * c / max(1, CREST_N - 1)
    h = CREST_H * (1.0 - 0.35 * abs(c / max(1, CREST_N - 1) - 0.3))
    base = Vector((0, y, ZC + BH * 0.5 + 0.05 * SC))
    B(f"Body_Vertebra_{c}", (0.5 * SC, 0.55 * SC, 0.3 * SC), base + Vector((0, 0, 0.05 * SC)), (-10, 0, 0), M_BONE, body_root)
    shard(f"Body_Crest_{c}", 0.55 * SC, 0.2 * SC, h, base + Vector((0, 0.05 * SC, 0.1 * SC)), (0, 0.4, 1),
          M_CREST if c % 2 == 0 else M_CREST2, body_root, up=(1, 0, 0))
    if c % 2 == 1:
        spike(f"Body_Spike_{c}", base + Vector((0, 0.3 * SC, 0)), (0, 0.5, 1), 0.34 * SC, h * 0.7, body_root)
for c in range(SMOKE_N):
    y = -TL * 0.3 + TL * 0.8 * (c + 0.5) / SMOKE_N
    sg = -1 if c % 2 == 0 else 1
    plume(f"Body_Smoke_{c}", (sg * BW * 0.4, y, ZC + BH * 0.5), (sg * 0.45, 0.2, 1), SMOKE_LEN * SC, body_root, n=3)
    plume(f"Body_SmokeLow_{c}", (sg * BW * 0.5, y, ZC - BH * 0.4), (sg * 0.7, 0.1, 0.5), SMOKE_LEN * 0.7 * SC, body_root, n=2)

# Fissures lilas sur les flancs
for sgn in (-1, 1):
    for c in range(FLANK_CRACKS):
        y0 = TL * 0.0 + c * TL * 0.45 / max(1, FLANK_CRACKS)
        crack(f"Body_Crack_{sgn}_{c}", (sgn * BW * 0.535, y0, ZC + BH * random.uniform(0.0, 0.3)),
              [(0, 0.25 * SC, -0.3 * SC), (0, 0.2 * SC, 0.15 * SC), (0, 0.25 * SC, -0.35 * SC)], body_root, th=0.08 * SC)

# Voile déchiré : grandes plaques translucides qui pendent des épaules (silhouette déchirée)
for c in range(SHROUD_N):
    sg = -1 if c % 2 == 0 else 1
    yy = -TL * 0.15 + (c // 2) * TL * 0.28
    diamond(f"Body_Shroud_{c}", (sg * BW * 0.5, yy, ZC + BH * 0.42), (sg * 0.9, 0.5 + 0.2 * c, -0.8),
            (2.2 + 0.4 * (c % 3)) * SC, 1.1 * SC, SMOKES[c % 3], body_root, up=(0, 0, 1), t=0.06 * SC)

# Cous : une courbe Catmull-Rom par tête ; devant violet, dos sombre, vertèbres d'os, pics translucides
NECK_RADIUS_KEYS = [(0.0, NECK_R[0]), (1.0, NECK_R[1])]

def build_neck(k, H, hsc, hx):
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
        ghost = (k == 3 and i == n // 2 and n >= 3)         # un maillon du cou droit est à demi fantôme
        B(nm + "_Inner", (2 * r * 0.8, Ln * 1.3, 2 * r * 0.8), mid, R, M_BODYD, body_root)
        B(nm + "_Front", (2 * r, Ln * 0.86, 2 * r * 0.95), mid - d * 0.06 * r, R, M_SMOKED if ghost else M_BELLY, body_root)
        B(nm + "_Back", (2 * r * 1.12, Ln * 0.92, r * 0.85), mid + d * r * 0.62, R,
          M_SMOKE if ghost else pick(BODY_MATS, BODY_W), body_root)
        for sgn in (-1, 1):
            B(f"{nm}_Side_{sgn}", (r * 0.3, Ln * 0.8, r * 0.75), mid + side * sgn * r * 0.95 + d * r * 0.5, R,
              M_SMOKED if ghost else pick(BODY_MATS, BODY_W), body_root)
        B(nm + "_Vertebra", (r * 0.7, Ln * 0.5, r * 0.28), mid + d * r * 1.12, R, M_BONE, body_root)
        shard(nm + "_Spike", 0.34 * SC, 0.14 * SC, (0.6 + 0.3 * (1 - s)) * SC, mid + d * r * 1.0, d + t * 0.6,
              M_CREST if i % 2 == 0 else M_CREST2, body_root, up=tuple(side))

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_neck(k + 1, H, hd[3], hd[0])

# ----------------------------------------------------------
# 11. PATTES : cuisse / épaule en wedge, tibia sombre (la patte arrière gauche est un squelette d'os),
#     bracelets et genouillères d'os, pied, 3 doigts + 3 griffes pâles, fumée aux pieds
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.22)
SHIN_H = LEG_H * 0.45

def leg(name, sgn, y, th, hind, skel=False):
    x = sgn * (BW * 0.5 - th * 0.28)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.5
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.6 if hind else 1.4), thigh_h),
          (x + sgn * 0.06 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.12), mat=pick([M_BODY, M_BODYD]), parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.07 * SC)
    sy = y + (th * 0.12 if hind else 0)
    kz = FOOT_H + SHIN_H + 0.02
    if skel and not IS_BEBE:
        # patte squelette : deux os parallèles, genou et cheville en articulations d'os, un peu de fumée autour
        for c in (-1, 1):
            bar(f"{name}_Bone_{c}", (x + c * th * 0.22, sy, kz + 0.1), (x + c * th * 0.2, sy - th * 0.05, FOOT_H + 0.05),
                th * 0.26, M_BONE, legs_root)
        B(f"{name}_Knee", (th * 0.8, th * 0.8, th * 0.45), (x, sy - th * 0.05, kz), mat=M_BONE, parent=legs_root)
        B(f"{name}_Ankle", (th * 0.7, th * 0.7, th * 0.3), (x, sy - th * 0.05, FOOT_H + 0.1), mat=M_BONE, parent=legs_root)
        plume(f"{name}_ShinSmoke", (x, sy, FOOT_H + SHIN_H * 0.5), (0.2 * sgn, 0.2, 1), SHIN_H * 0.8, legs_root, n=2)
    else:
        box(f"{name}_Shin", (th * 0.92, th * 0.98, SHIN_H + 0.2), (x, sy, FOOT_H + SHIN_H / 2), mat=M_BODY,
            parent=legs_root, bevel=0.05 * SC)
        bh_ = SHIN_H * BRACER_K
        bz = FOOT_H + SHIN_H * 0.5
        box(f"{name}_Bracer", (th * 1.12, th * 1.18, bh_), (x, sy, bz), mat=M_BONE, parent=legs_root, bevel=0.03 * SC)
        B(f"{name}_BracerRim", (th * 1.18, th * 1.24, 0.08 * SC), (x, sy, bz + bh_ / 2), mat=M_BODYD, parent=legs_root)
        if not IS_BEBE:
            B(f"{name}_Knee", (th * 0.7, th * 0.4, th * 0.5), (x, sy - th * 0.5, kz - 0.05), mat=M_BONE, parent=legs_root)
    fy = sy - th * 0.3
    box(f"{name}_Foot", (th * 1.15, th * 1.75, FOOT_H), (x, fy, FOOT_H / 2), mat=M_BODYD, parent=legs_root, bevel=0.05 * SC)
    B(f"{name}_FootGlow", (th * 1.18, th * 0.08, FOOT_H * 0.25), (x, fy - th * 0.3, FOOT_H * 0.55), mat=M_GLOW, parent=legs_root)
    toe_y = fy - th * 0.88 - th * 0.12
    for c in (-1, 0, 1):
        B(f"{name}_Toe_{c}", (th * 0.3, th * 0.5, FOOT_H * 0.7), (x + c * th * 0.34, toe_y, FOOT_H * 0.35),
          mat=M_SCB, parent=legs_root)
        shard(f"{name}_Claw_{c}", th * 0.22, th * 0.18, th * CLAW_K, (x + c * th * 0.34, toe_y - th * 0.2, FOOT_H * 0.3),
              (c * 0.12, -1, -0.25), M_CLAW, legs_root)
    # le contour du pied se dissipe en fumée
    plume(f"{name}_FootSmoke", (x + sgn * th * 0.4, fy + th * 0.3, FOOT_H * 0.6), (sgn * 0.5, 0.4, 1), th * 0.9, legs_root, n=2)

LEG_TH_F, LEG_TH_R = BW * 0.4, BW * 0.46
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.3, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True, skel=(sgn == -1))

# ----------------------------------------------------------
# 12. AILES : l'Hydre Revenant n'en a pas (les voiles de fumée de la section 10 en tiennent lieu)
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe Catmull-Rom, segments sombres, ventre violet, vertèbres d'os ;
#     après TAIL_FADE elle devient translucide puis se défait en fragments
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
    if s < TAIL_FADE:
        B(f"Tail_Inner_{i}", (2 * r * 0.86, Ln * 1.3, 2 * r * 0.82), mid, R, M_BODYD, tail_root)
        box(f"Tail_Seg_{i}", (2 * r, Ln * 0.9, 2 * r * 0.95), mid, R, pick(BODY_MATS, BODY_W), tail_root,
            bevel=(0.04 * SC if i < 3 else 0))
        B(f"Tail_Belly_{i}", (2 * r * 0.75, Ln * 0.75, 0.2 * SC), mid - d * (r * 0.97), R, M_BELLY, tail_root)
        B(f"Tail_Vertebra_{i}", (r * 0.8, Ln * 0.55, r * 0.3), mid + d * (r * 1.0), R, M_BONE, tail_root)
        shard(f"Tail_Crest_{i}", 0.3 * SC + r * 0.3, 0.14 * SC, 0.4 * SC + r * 0.9, mid + d * r * 0.9, d + t * 0.7,
              M_CREST if i % 2 == 0 else M_CREST2, tail_root, up=tuple(side))
        if i % 2 == 1:
            for sgn in (-1, 1):
                B(f"Tail_Patch_{i}_{sgn}", (0.08 * SC, Ln * 0.5, r * 0.7), mid + side * sgn * r * 1.0 + d * r * 0.1, R,
                  M_GLOW, tail_root)
    else:
        # partie fantôme : bloc translucide plus court (il y a des vides entre les segments) + vertèbre d'os qui reste
        k_ = 1.0 - 0.35 * (s - TAIL_FADE) / max(0.01, 1 - TAIL_FADE)
        B(f"Tail_Ghost_{i}", (2 * r * k_, Ln * 0.62, 2 * r * 0.9 * k_), mid, R, SMOKES[i % 3], tail_root)
        if i % 2 == 0:
            B(f"Tail_GhostBone_{i}", (r * 0.7, Ln * 0.4, r * 0.28), mid + d * (r * 0.95), R, M_BONE, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
for c in range(TAIL_FRAG):       # fragments translucides qui se détachent dans le prolongement de la queue
    off = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.3, 1))) * BW * 0.12
    diamond(f"Tail_Frag_{c}", tip + tt_ * (c * 0.35 * TAIL_TIP) + off, tt_ + off.normalized() * 0.5, TAIL_TIP * (1.1 - 0.1 * c),
            TAIL_TIP * 0.45, SMOKES[c % 3], tail_root, up=(1, 0.2, 0.3), t=0.05 * TAIL_TIP)
crystal("Tail_TipGem", BW * 0.07, TAIL_TIP * 0.3, TAIL_TIP * 0.4, tip, tt_, M_EYE, tail_root, sides=5)
for c in range(3):
    a = c * 2 * math.pi / 3
    off = td_ * math.cos(a) + ts_ * math.sin(a)
    shard(f"Tail_TipBone_{c}", 0.28 * SC, 0.2 * SC, TAIL_TIP * 0.9, tip + off * BW * 0.04, tt_ + off * 0.55, M_BONE,
          tail_root, up=tuple(tt_))
wisp("Tail_Wisp", tip + tt_ * TAIL_TIP * 0.5, WISP_H * 1.1, 0.4 * SC, tail_root)

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (SECRET) + FX
#     Secret : os apparents, vide dans la cage thoracique et les orbites, parties fantômes translucides (alpha),
#     silhouette déchirée et asymétrique, yeux et fissures émissifs, feux follets.
#     FX : éclats d'os, perles de feu follet et lambeaux de fumée qui flottent autour.
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    top_z = NECK_TOP.z + HEAD_SCALE * 1.8
    for c in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.4 + 1.5), random.uniform(-TL * 0.9, TL * 0.6 + TAIL_L * 0.5),
                    random.uniform(LEG_H * 0.6, top_z)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        if c % 3 == 0:        # éclat d'os
            shard(f"FX_Bone_{c}", FX_SIZE * 0.8, FX_SIZE * 0.4, FX_SIZE * 1.8, p, dirv, M_BONE, master)
        elif c % 3 == 1:      # perle de feu follet
            crystal(f"FX_Orb_{c}", FX_SIZE * 0.35, FX_SIZE * 0.4, FX_SIZE * 0.4, p, dirv, M_EYE, master, sides=4)
        else:                 # lambeau de fumée
            diamond(f"FX_Smoke_{c}", p, dirv, FX_SIZE * 2.4, FX_SIZE * 1.1, SMOKES[c % 3], master,
                    up=(random.uniform(-1, 1), random.uniform(-1, 1), 1), t=0.04)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
