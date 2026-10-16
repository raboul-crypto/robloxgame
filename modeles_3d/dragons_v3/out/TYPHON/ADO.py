import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - Typhon · Ado
#  Légendaire · Eau · Hydre · monde 4
#  - Ado : TROIS têtes à crête en vagues sur cous de 3 maillons (la centrale plus grande), silhouette plus longue et musclée, crocs, regard sérieux
#  - Crêtes de vagues plus hautes à bout d'écume, spirales de tourbillon sur les cous et les flancs, anneaux bleu clair sur les cous, pattes palmées
#  - Queue de poisson à rayons, nageoires de mollet, épaules en wedge, pas d'ailes
#  - Légendaire à mi-puissance : couronnes d'argent, plastron à gemme, épaulières, bracelets, aura derrière chaque tête, double rangée de pics, bague et trident de queue, FX d'eau
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed(4404)            # même dragon à chaque exécution
TAG = "TYPHON_ADO"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = 7       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = 10000          # budget de triangles de ce stade et de cette rareté
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
STAGE = "ADO"
GLOW_STR = 2.3                    # puissance de l'émission (yeux, gemmes, aura)
SILVER = True                     # ornements d'argent (Légendaire)
DOUBLE_ROW = True                 # double rangée de pics sur le dos et la tête
AURA_N = 5                        # éclats de l'aura derrière chaque tête (0 = sans)
BW = 3.0                          # largeur du torse
BH = 2.4                          # hauteur du torse
LEG_H = 1.9                       # hauteur des pattes
TORSO_L = 4.0                     # longueur torse + bassin
NECK_L = 2.3                      # hauteur du cou central
NECK_LEAN = 0.5                   # avancée du cou vers l'avant
NECK_N = 3                        # nombre de maillons par cou
NECK_R = (0.78, 0.6)              # rayon du cou : base, haut
NECK_CURVE = 0.6                  # courbure en S des cous
NECK_WAVES = True                 # petites vagues sur les cous
NECK_WAVE_K = 0.9                 # taille des vagues de nuque
NECK_SWIRL = True                 # spirales de tourbillon sur les cous
HEAD_SCALE = 1.0                  # taille de la tête centrale
HEAD_PITCH = 5                    # degrés : la tête regarde vers le bas
HEADS = [(0.0, 0.0, 0.0, 1.0, 0), (-2.6, 0.7, -0.9, 0.82, -24), (2.6, 0.7, -0.9, 0.82, 24)]# (décalage X, Y, Z, échelle, rotation vers l'extérieur en degrés)
SNOUT_L = 1.25                    # longueur du museau
JAW_OPEN = 4                      # ouverture de la gueule (degrés)
FANGS = 2                         # crocs par côté
HORN_L = 1.0                      # longueur des cornes
EYE = (0.55, 0.5, 0.38, 0.42, 0.1, 0.38)# blanc L/H, iris L/H, pupille L/H
BROW_TILT = 16                    # inclinaison des sourcils
TUFT_N = 4                        # vagues de la crête sur chaque tête
TUFT_L = 1.9                      # hauteur des vagues de la crête
CHEEK_N = 2                       # nageoires de joue par côté
SCALE_ROWS = 3                    # rangées d'écailles par flanc
SCALE_COLS = 3                    # écailles par rangée
BELLY_N = 3                       # plaques de ventre
CARA_N = 4                        # plaques et vagues du dos
CREST_H = 1.5                     # hauteur des vagues du dos
SWIRLS = 2                        # spirales de tourbillon par flanc
SWIRL_TURNS = 1.6                 # tours de chaque spirale
BRACER_K = 0.4                    # hauteur du bracelet
CLAW_K = 0.55                     # longueur des griffes
TAIL_L = 4.2                      # longueur de la queue
TAIL_STEP = 0.6                   # pas des segments de queue
TAIL_WAVE_ALL = False             # une vague sur chaque segment de queue
TAIL_RINGS = False                # anneaux de tourbillon sur la queue
TAIL_FIN = 1.7                    # taille de la nageoire caudale
TAIL_FIN_RAYS = True              # rayons supplémentaires sur la nageoire
TRIDENT = True                    # trident d'argent au bout de la queue
CRYS_N = 2                        # cristaux d'eau sur le dos
FX_N = 4                          # éléments flottants (gouttes, bulles, vagues, tourbillons)
FX_SIZE = 0.3                     # taille des FX
FX_SWIRL = True                   # tourbillons flottants

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON (identique aux 3 stades)
#    Bleu océan profond, vert d'eau, ventre turquoise clair, écume blanche, spirales bleu clair,
#    yeux turquoise lumineux, métal argenté (Légendaire).
# ----------------------------------------------------------
M_BODY  = get_mat("Body",      "#1A57A8", 0.50)   # corps principal
M_BODY2 = get_mat("BodyDark",  "#0F2F5E", 0.55)   # genoux, ombres, mâchoire
M_BODY3 = get_mat("ScaleB",    "#1F6E96", 0.50)   # écailles chaudes (bleu-vert)
M_SCALEA = get_mat("ScaleA",   "#14407F", 0.55)   # écailles sombres
M_DARK  = get_mat("Nostril",   "#0A1C36", 0.70)   # narines, jointures, bouche
M_BELLY = get_mat("Belly",     "#9EDDD6", 0.45)   # ventre en plaques, plastron, menton
M_CREST = get_mat("Crest",     "#35BFAE", 0.40)   # crêtes en vague, sourcils, cornes
M_FOAM  = get_mat("Foam",      "#F4F8FA", 0.35)   # écume blanche, crête secondaire
M_MEMB  = get_mat("Membrane",  "#3FB5A8", 0.45)   # nageoires, palmes, oreilles
M_MARK  = get_mat("Mark",      "#7FC8EA", 0.40)   # spirales de tourbillon
M_IRIS  = get_mat("Eye",       "#2FD0C8", 0.25, emission="#2FD0C8", strength=GLOW_STR)      # iris lumineux
M_GEM   = get_mat("Gem",       "#2FE6E0", 0.20, emission="#2FD0C8", strength=GLOW_STR)      # gemmes d'armure
M_AURA  = get_mat("Aura",      "#7FE8F2", 0.25, emission="#5FDCF0", strength=GLOW_STR * 0.9)  # aura, bulles, gouttes
M_SILVER = get_mat("Silver",   "#C6D8EA", 0.22, metallic=0.95)   # métal argenté (Légendaire)
M_CLAW  = get_mat("Claw",      "#F4F8FA", 0.40)   # griffes
M_FANG  = get_mat("Fang",      "#F2F2F2", 0.35)   # crocs
M_WHITE = get_mat("EyeWhite",  "#F2F2F2", 0.30)
M_BLACK = get_mat("Black",     "#0A0A0A", 0.30)   # pupilles
BODY_MATS, BODY_W = [M_BODY, M_SCALEA, M_BODY3], [5, 2, 3]
SCALE_MATS = [M_SCALEA, M_BODY3, M_BODY]

# ----------------------------------------------------------
# 8. PROPORTIONS ET HIÉRARCHIE
#    Tout est en unités de travail ; finalize() met le dragon à TARGET_HEIGHT.
# ----------------------------------------------------------
IS_BEBE, IS_ADO, IS_ADULTE = (STAGE == "BEBE"), (STAGE == "ADO"), (STAGE == "ADULTE")
SC = BH / 2.0                                    # échelle des petits détails
ZC = LEG_H * 0.85 + BH / 2                       # hauteur du centre du torse
TL = TORSO_L
NECK_TOP = Vector((0, -TL * 0.42 - NECK_LEAN, ZC + BH * 0.35 + NECK_L))   # sommet du cou central

master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)

HEAD_ROOT_NAMES = ["HEAD_ROOT", "HEAD2_ROOT", "HEAD3_ROOT"]
head_roots = []
for k, (hx, hdy, hdz, hsc, hyaw) in enumerate(HEADS):
    pos = NECK_TOP + Vector((hx, hdy, hdz))
    mtx = (Matrix.Translation(pos) @ Euler((0, 0, math.radians(hyaw))).to_matrix().to_4x4()
           @ Euler((math.radians(HEAD_PITCH), 0, 0)).to_matrix().to_4x4())
    head_roots.append(empty(HEAD_ROOT_NAMES[k], master, mtx))

# Petits outils (pas de biseau par défaut : réservé aux gros blocs)
def B(name, size, loc, rot=None, mat=None, parent=None, bevel=0.0):
    return box(name, size, loc, rot, mat, parent, bevel)

def bar(name, p1, p2, th, mat, parent, up=(0, 0, 1), depth=None):
    return link(name, p1, p2, th, mat, parent, up, extra=th * 0.5, bevel=0, depth=depth)

def tchain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    """Suite de barres qui s'affinent (cornes, tiges)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        bar(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up)

def blade(name, base, direction, L, w, mat, parent, droop=0.0, up=(0, 0, 1), t=None):
    """Plaque en losange (4 points) : écailles, nageoires, oreilles. Part de 'base', pointe dans 'direction'."""
    base = Vector(base)
    d = Vector(direction).normalized()
    side = d.cross(Vector(up))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    tip = base + d * L + Vector((0, 0, -droop * L))
    mid = base + d * (L * 0.42)
    plate(name, [base, mid + side * w, tip, mid - side * w], t if t is not None else max(0.03, w * 0.14), mat, parent)
    return tip

def wave(name, base, up_dir, L, w, parent, mat=None, curl=1.0, fwd=(0, -1, 0), foam=True, n=3):
    """SIGNE DISTINCTIF : crête en forme de vague. n plaques en arc qui montent depuis 'base' dans 'up_dir'
    puis déferlent vers 'fwd'. L = hauteur, w = demi-largeur. Le sommet porte de l'écume blanche."""
    mat = mat or M_CREST
    base = Vector(base)
    a = Vector(up_dir).normalized()
    f = Vector(fwd).normalized()
    side = a.cross(f)
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    pts, wd = [], []
    for i in range(n + 1):
        s = i / n
        phi = s * (0.9 + 0.9 * curl)
        pts.append(base + a * (L * math.sin(phi)) + f * (L * 0.55 * (1 - math.cos(phi)) * curl))
        wd.append(w * (1.5 - 1.1 * s))                       # largeur du croissant (dans le plan de la vague)
    th = max(0.05, w * 0.55)                                 # épaisseur (dans le sens du côté)
    for i in range(n):
        T = (pts[i + 1] - pts[i]).normalized()
        N = side.cross(T).normalized()
        T2 = (pts[min(n, i + 2)] - pts[i + 1]).normalized() if i + 1 < n else T
        N2 = side.cross(T2).normalized()
        plate(f"{name}_{i}", [pts[i] + N * wd[i] * 0.5, pts[i + 1] + N2 * wd[i + 1] * 0.5,
                              pts[i + 1] - N2 * wd[i + 1] * 0.5, pts[i] - N * wd[i] * 0.5], th, mat, parent)
    if foam:
        tip = pts[n]
        tg = (pts[n] - pts[n - 1]).normalized()
        crystal(f"{name}_Foam", w * 0.5, w * 0.9, w * 0.9, tip - tg * w * 0.2, tg, M_FOAM, parent, sides=4)
        prism(f"{name}_FoamB", w * 0.3, w * 0.5, tip - tg * w * 0.5 + a * w * 0.3, tg, M_FOAM, parent, sides=5)
    return pts[n]

def swirl(name, center, e1, e2, r0, turns, parent, th, mat=None, seg=6, shrink=True):
    """SIGNE DISTINCTIF : spirale de tourbillon (suite de barres) dans le plan (e1, e2) autour de 'center'."""
    mat = mat or M_MARK
    c = Vector(center)
    e1, e2 = Vector(e1).normalized(), Vector(e2).normalized()
    n = max(3, int(seg * turns))
    pts = []
    for j in range(n + 1):
        u = j / n
        ang = 2 * math.pi * turns * u
        rr = r0 * ((1 - 0.8 * u) if shrink else 1.0)
        pts.append(c + e1 * (rr * math.cos(ang)) + e2 * (rr * math.sin(ang)))
    for j in range(n):
        bar(f"{name}_{j}", pts[j], pts[j + 1], th, mat, parent, up=tuple(e1.cross(e2)), depth=th * 0.8)
    return pts

def spike(name, base, direction, w, L, parent, up=(1, 0, 0), mat=None):
    """Pic (sans biseau)."""
    shard(name, w, w * 0.6, L, base, Vector(direction).normalized(), mat or M_FOAM, parent, up=up)

# ----------------------------------------------------------
# 9. TÊTES : une fonction construit une tête complète dans les coordonnées locales de son root.
#    Appelée pour HEAD_ROOT (centrale), HEAD2_ROOT et HEAD3_ROOT. Crête en vagues, oreilles-nageoires,
#    couronne d'argent et aura (Légendaire).
# ----------------------------------------------------------
def build_head(H, k, hs):
    """Tête n° k (1 = centrale) en coordonnées locales de l'empty H, à l'échelle hs."""
    P = f"Head{k}_"
    def hv(v):
        return tuple(c * hs for c in v)
    def hb(name, size, loc, rot=None, mat=None, bevel=0.0):
        return box(P + name, hv(size), hv(loc), rot, mat, H, bevel * hs if (k == 1 or not IS_BEBE) else 0.0)
    SNOUT_FRONT = -0.85 - SNOUT_L

    # Crâne et museau biseautés, arête du museau en crête turquoise
    hb("Skull", (1.9, 1.75, 1.6), (0, 0, 0), mat=M_BODY, bevel=0.12)
    hb("Snout", (1.5, SNOUT_L + 0.3, 0.8), (0, -0.85 - SNOUT_L / 2 + 0.15, -0.3), mat=M_BODY3, bevel=0.08)
    hb("SnoutBridge", (0.75, SNOUT_L * 0.9, 0.16), (0, SNOUT_FRONT * 0.55 - 0.1, 0.16), mat=M_CREST)
    hb("Forehead", (1.3, 0.7, 0.18), (0, -0.55, 0.84), mat=M_SCALEA)

    # Mâchoire distincte (entrouverte chez l'ado et l'adulte), gorge claire, ligne de bouche sombre
    hb("Jaw", (1.36, SNOUT_L + 0.5, 0.42), (0, -0.75 - SNOUT_L / 2 + 0.2, -0.86 - JAW_OPEN * 0.012),
       rot=(-JAW_OPEN, 0, 0), mat=M_BODY2, bevel=0.05)
    hb("Throat", (1.2, 1.1, 0.3), (0, 0.15, -0.88), mat=M_BELLY)
    hb("Chin", (0.9, 0.6, 0.16), (0, -0.75 - SNOUT_L * 0.8, -1.02 - JAW_OPEN * 0.02), mat=M_BELLY)
    hb("Mouth", (1.3, SNOUT_L + 0.3, 0.1 + JAW_OPEN * 0.012), (0, -0.85 - SNOUT_L / 2 + 0.2, -0.67), mat=M_DARK)

    for sgn in (-1, 1):
        hb(f"Nostril_{sgn}", (0.24, 0.2, 0.1), (sgn * 0.42, SNOUT_FRONT + 0.3, 0.13), mat=M_DARK)

    # Yeux : blanc, iris turquoise lumineux, pupille (ronde chez le bébé, fendue ensuite), reflets du bébé
    for sgn in (-1, 1):
        ex, ey, ez = sgn * 0.97, -0.38, 0.12
        hb(f"EyeWhite_{sgn}", (0.1, EYE[0], EYE[1]), (ex, ey, ez), mat=M_WHITE)
        hb(f"Iris_{sgn}", (0.08, EYE[2], EYE[3]), (ex + sgn * 0.04, ey - 0.03, ez - 0.02), mat=M_IRIS)
        hb(f"Pupil_{sgn}", (0.07, EYE[4], EYE[5]), (ex + sgn * 0.08, ey - 0.04, ez - 0.03), mat=M_BLACK)
        if IS_BEBE:
            hb(f"Glint_{sgn}", (0.06, 0.18, 0.2), (ex + sgn * 0.11, ey - 0.17, ez + 0.2), mat=M_WHITE)
            hb(f"Glint2_{sgn}", (0.06, 0.09, 0.09), (ex + sgn * 0.11, ey + 0.1, ez - 0.2), mat=M_WHITE)
        hb(f"Brow_{sgn}", (0.24, EYE[0] + 0.3, 0.24), (sgn * 0.93, ey - 0.05, ez + EYE[1] / 2 + 0.12),
           rot=(BROW_TILT, 0, sgn * -6), mat=M_CREST, bevel=0.02)

    # Crocs (ado : 2 par côté ; adulte : 3 par côté + crocs du bas)
    for sgn in (-1, 1):
        for f in range(FANGS):
            fy = SNOUT_FRONT + 0.35 + f * 0.45
            shard(f"{P}Fang_{sgn}_{f}", 0.18 * hs, 0.18 * hs, (0.34 + 0.06 * FANGS) * hs, hv((sgn * 0.55, fy, -0.68)),
                  (0, 0.05, -1), M_FANG, H, up=(1, 0, 0))
            if IS_ADULTE and f < 2:
                shard(f"{P}FangLow_{sgn}_{f}", 0.14 * hs, 0.14 * hs, 0.3 * hs,
                      hv((sgn * 0.45, fy + 0.25, -0.75 - JAW_OPEN * 0.02)), (0, 0.05, 1), M_FANG, H, up=(1, 0, 0))

    # Cornes turquoise vers l'arrière (bébé : petits blocs), bague d'argent et pointe d'écume
    for sgn in (-1, 1):
        if IS_BEBE:
            hb(f"Horn_{sgn}", (0.36, 0.36, 0.42), (sgn * 0.62, 0.3, 0.95), rot=(-15, sgn * 10, 0), mat=M_CREST)
            hb(f"HornTip_{sgn}", (0.22, 0.22, 0.2), (sgn * 0.64, 0.36, 1.2), rot=(-15, sgn * 10, 0), mat=M_FOAM)
        else:
            L = HORN_L
            pts = [(sgn * 0.7, 0.25, 0.6), (sgn * 0.95, 0.5, 0.6 + 0.45 * L), (sgn * 1.05, 0.5 + 0.55 * L, 0.6 + 0.8 * L),
                   (sgn * 1.0, 0.5 + 1.05 * L, 0.6 + 0.95 * L)]
            tchain(f"{P}Horn_{sgn}", [hv(p) for p in pts], 0.36 * hs, 0.18 * hs, M_CREST, H)
            tip_dir = Vector(pts[3]) - Vector(pts[2])
            shard(f"{P}HornTip_{sgn}", 0.22 * hs, 0.22 * hs, 0.55 * hs * L, hv(pts[3]), tip_dir, M_FOAM, H)
            if SILVER:
                B(f"{P}HornRing_{sgn}", hv((0.44, 0.44, 0.1)), hv(pts[1]),
                  basis(Vector(pts[1]) - Vector(pts[0]), (1, 0, 0)), M_SILVER, H)

    # CRÊTE EN VAGUES sur le crâne : une rangée de vagues du front vers la nuque, de plus en plus hautes
    for c in range(TUFT_N):
        u = c / max(1, TUFT_N - 1)
        wy = -0.6 + 1.25 * u
        h_ = TUFT_L * (0.55 + 0.55 * math.sin(math.pi * (0.2 + 0.8 * u)))
        wave(f"{P}Crest_{c}", hv((0, wy, 0.8)), (0, 0.35 * u, 1.0), h_ * hs, 0.42 * hs, H, M_CREST if c % 2 == 0 else M_MEMB,
             curl=1.0, fwd=(0, -1, 0), foam=True)
    if DOUBLE_ROW:      # seconde rangée de petites vagues blanches de chaque côté (Légendaire)
        for sgn in (-1, 1):
            for c in range(max(2, TUFT_N // 2)):
                wave(f"{P}CrestS_{sgn}_{c}", hv((sgn * 0.62, -0.2 + 0.5 * c, 0.76)), (sgn * 0.4, 0.3, 1.0),
                     TUFT_L * 0.5 * hs, 0.26 * hs, H, M_FOAM, curl=0.8, fwd=(0, -1, 0), foam=False, n=2)

    # Oreilles-nageoires (membrane turquoise) et nageoires de joue
    for sgn in (-1, 1):
        for c in range(CHEEK_N):
            blade(f"{P}Fin_{sgn}_{c}", hv((sgn * 0.88, 0.15 + c * 0.28, -0.3 - c * 0.18)),
                  (sgn * (0.7 + 0.1 * c), 1.0, -0.15 - 0.25 * c), (0.95 - 0.12 * c) * hs, 0.26 * hs,
                  M_MEMB if c % 2 == 0 else M_CREST, H, droop=0.1)

    # Couronne d'argent avec gemme sur le front (Légendaire) : bande, trois pointes, gemme turquoise
    if SILVER and (k == 1 or not IS_BEBE):
        hb("CrownBand", (1.5, 0.2, 0.18), (0, -0.84, 0.74), mat=M_SILVER)
        for c, cx in enumerate((-0.55, 0.0, 0.55)):
            shard(f"{P}CrownSpike_{c}", 0.2 * hs, 0.16 * hs, (0.55 if c == 1 else 0.38) * hs, hv((cx, -0.84, 0.8)),
                  (0, -0.15, 1.0), M_SILVER, H, up=(1, 0, 0))
        crystal(f"{P}CrownGem", 0.15 * hs, 0.1 * hs, 0.14 * hs, hv((0, -0.97, 0.72)), (0, -1, 0), M_GEM, H)
        if AURA_N > 0:  # AURA : anneau de lumière et couronne d'éclats derrière la tête
            R_ = 2.15 * hs
            ctr = hv((0, 1.5, 0.5))
            ring(f"{P}AuraRing", R_, 0.38 * hs, 0.14 * hs, ctr, (0, 1, 0), M_AURA, H, sides=14)
            for c in range(AURA_N):
                ang = math.radians(-35 + 250 * c / max(1, AURA_N - 1))
                dv = Vector((math.cos(ang), 0, math.sin(ang)))
                shard(f"{P}AuraShard_{c}", 0.34 * hs, 0.12 * hs, (0.75 if c % 2 == 0 else 0.5) * hs,
                      Vector(ctr) + dv * R_ * 0.98, dv, M_AURA, H, up=(0, 1, 0))

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_head(H, k + 1, HEAD_SCALE * hd[3])

# ----------------------------------------------------------
# 10. CORPS : torse et bassin biseautés, ventre en plaques, plastron d'argent, dos à plaques,
#     crête dorsale en vagues + double rangée de pics, écailles sur les flancs, spirales, cous Catmull-Rom
# ----------------------------------------------------------
B("Body_Chest", (BW * 1.05, TL * 0.56, BH), (0, -TL * 0.2, ZC), None, M_BODY, body_root, bevel=0.14 * SC)
B("Body_Pelvis", (BW * 0.95, TL * 0.5, BH * 0.92), (0, TL * 0.25, ZC - 0.04 * BH), None, M_BODY, body_root, bevel=0.14 * SC)
B("Body_Waist", (BW * 0.9, TL * 0.3, BH * 0.86), (0, 0, ZC - 0.02 * BH), None, M_BODY2, body_root)

# Plaques de ventre turquoise clair bien séparées
for i in range(BELLY_N):
    y = -TL * 0.42 + (TL * 0.86) * (i + 0.5) / BELLY_N
    pl = (TL * 0.86) / BELLY_N * 0.84
    B(f"Body_Belly_{i}", (BW * 0.72, pl, 0.26 * SC), (0, y, ZC - BH * 0.47 - 0.06 * SC), mat=M_BELLY, parent=body_root)

# Poitrail : plastron clair ; à partir de l'ado, bord d'argent et gemme (Légendaire)
PY = -TL * 0.48 - 0.1 * SC
if IS_BEBE:
    B("Body_ChestBand", (BW * 0.84, 0.3 * SC, BH * 0.5), (0, PY, ZC - BH * 0.12), mat=M_BELLY, parent=body_root, bevel=0.05 * SC)
    for sgn in (-1, 1):
        B(f"Body_ChestStud_{sgn}", (0.18 * SC, 0.1 * SC, 0.18 * SC), (sgn * BW * 0.3, PY - 0.17 * SC, ZC - BH * 0.12),
          mat=M_SILVER, parent=body_root)
    crystal("Body_Gem", 0.2 * SC, 0.08 * SC, 0.16 * SC, (0, PY - 0.14 * SC, ZC - BH * 0.12), (0, -1, 0), M_GEM, body_root)
else:
    for r in range(3):
        B(f"Body_Plastron_{r}", (BW * (0.72 - 0.1 * r), 0.28 * SC, BH * 0.22), (0, PY, ZC + BH * (0.12 - 0.25 * r)),
          mat=M_BELLY, parent=body_root)
    B("Body_PlastronRim", (BW * 0.8, 0.2 * SC, 0.12 * SC), (0, PY + 0.06 * SC, ZC + BH * 0.27), mat=M_SILVER, parent=body_root)
    B("Body_GemSet", (0.55 * SC, 0.2 * SC, 0.55 * SC), (0, PY - 0.12 * SC, ZC - BH * 0.06), rot=(0, 45, 0), mat=M_SILVER,
      parent=body_root)
    crystal("Body_Gem", 0.24 * SC, 0.1 * SC, 0.22 * SC, (0, PY - 0.18 * SC, ZC - BH * 0.06), (0, -1, 0), M_GEM, body_root)

# Épaules musclées (wedge) et épaulières d'argent à pointe (Légendaire)
if not IS_BEBE:
    for sgn in (-1, 1):
        wedge(f"Body_Shoulder_{sgn}", (BW * 0.42, TL * 0.36, BH * 0.62),
              (sgn * BW * 0.42, -TL * 0.3, ZC + BH * 0.2), (0, sgn * 12, 0), M_BODY2, body_root,
              top_x=0.7, top_y=0.75, bevel=0.06 * SC)
        if SILVER:
            wedge(f"Body_Pauldron_{sgn}", (BW * 0.4, TL * 0.32, BH * 0.2),
                  (sgn * BW * 0.46, -TL * 0.3, ZC + BH * 0.56), (0, sgn * 14, 0), M_SILVER, body_root,
                  top_x=0.75, top_y=0.8, bevel=0.04 * SC)
            spike(f"Body_PauldronSpike_{sgn}", (sgn * BW * 0.5, -TL * 0.3, ZC + BH * 0.62), (sgn * 0.4, 0, 1.0),
                  0.34 * SC, 0.8 * SC, body_root, mat=M_SILVER)

# DOS : plaques d'écailles bleues, grande crête de vagues au centre et DOUBLE RANGÉE DE PICS (Légendaire)
for c in range(CARA_N):
    u = c / max(1, CARA_N - 1)
    y = -TL * 0.38 + (TL * 0.8) * u
    wdt = BW * (0.62 - 0.05 * abs(u - 0.4))
    zt = ZC + BH * 0.5
    B(f"Body_Back_{c}", (wdt * 0.5, TL * 0.8 / CARA_N * 1.25, 0.26 * SC), (0, y, zt + 0.07 * SC), (-4, 0, 0),
      SCALE_MATS[c % 3], body_root, bevel=0.04 * SC)
    for sgn in (-1, 1):
        B(f"Body_BackS_{c}_{sgn}", (wdt * 0.36, TL * 0.8 / CARA_N * 1.2, 0.24 * SC),
          (sgn * wdt * 0.4, y + 0.04, zt - 0.1 * SC), (0, sgn * 24, 0), SCALE_MATS[(c + 1) % 3], body_root)
    h = CREST_H * (1.0 - 0.35 * abs(u - 0.3))
    wave(f"Body_Wave_{c}", (0, y + 0.1, zt + 0.1 * SC), (0, 0.3, 1.0), h, 0.36 * SC, body_root, M_CREST if c % 2 == 0 else M_MEMB,
         curl=1.0, fwd=(0, -1, 0))
    if DOUBLE_ROW:
        for sgn in (-1, 1):
            spike(f"Body_Pic_{c}_{sgn}", (sgn * wdt * 0.5, y + 0.1, zt - 0.05 * SC), (sgn * 0.45, 0.35, 1.0),
                  0.3 * SC, h * 0.8, body_root, mat=M_SILVER if c % 2 == 0 else M_FOAM)

# Écailles en quinconce sur les flancs
for sgn in (-1, 1):
    for rr in range(SCALE_ROWS):
        for cc in range(SCALE_COLS):
            y = -TL * 0.42 + (TL * 0.86) * (cc + 0.5 * (rr % 2) + 0.5) / SCALE_COLS
            z = ZC + BH * (0.3 - 0.62 * (rr + 0.5) / SCALE_ROWS)
            xw = BW * (0.525 if y < -TL * 0.02 else 0.48) + 0.02
            blade(f"Body_Scale_{sgn}_{rr}_{cc}", (sgn * xw, y - 0.18 * SC, z), (sgn * 0.25, 1.0, -0.12), 0.62 * SC, 0.26 * SC,
                  pick(SCALE_MATS), body_root, up=(sgn, 0, 0), t=0.05 * SC)

# SPIRALES DE TOURBILLON sur les flancs (bleu clair) et petite écume au centre
for sgn in (-1, 1):
    for c in range(SWIRLS):
        cy = -TL * 0.2 + c * TL * 0.4
        cz = ZC + BH * (0.0 if c % 2 == 0 else 0.1)
        cxs = sgn * (BW * 0.5 + 0.05)
        swirl(f"Body_Swirl_{sgn}_{c}", (cxs, cy, cz), (0, 1, 0), (0, 0, 1), 0.85 * SC, SWIRL_TURNS, body_root,
              0.1 * SC, M_MARK if c % 2 == 0 else M_FOAM, seg=6)
        prism(f"Body_SwirlEye_{sgn}_{c}", 0.12 * SC, 0.1 * SC, (cxs + sgn * 0.03, cy, cz), (sgn, 0, 0), M_FOAM, body_root, sides=5)

# Cous : une courbe Catmull-Rom par tête, rééchantillonnée à pas constant, avec spirales de tourbillon
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
        B(nm + "_Inner", (2 * r * 0.8, Ln * 1.3, 2 * r * 0.8), mid, R, M_DARK, body_root)           # jointure sombre
        B(nm + "_Front", (2 * r, Ln * 0.86, 2 * r * 0.95), mid - d * 0.06 * r, R, M_BODY, body_root)   # bloc de cou
        B(nm + "_Throat", (2 * r * 0.6, Ln * 0.8, r * 0.3), mid - d * r * 1.0, R, M_BELLY, body_root)  # gorge claire
        B(nm + "_Back", (2 * r * 1.12, Ln * 0.92, r * 0.85), mid + d * r * 0.62, R, pick([M_SCALEA, M_BODY2]), body_root)
        for sgn in (-1, 1):
            B(f"{nm}_Side_{sgn}", (r * 0.3, Ln * 0.8, r * 0.75), mid + side * sgn * r * 0.95 + d * r * 0.5, R,
              pick(BODY_MATS, BODY_W), body_root)
        # bague de tourbillon inclinée à chaque articulation
        sgn_t = 1 if i % 2 == 0 else -1
        B(nm + "_Ring", (2 * r * 1.12, Ln * 0.16, 2 * r * 1.08), p1, R @ Euler((0, math.radians(sgn_t * 16), 0)).to_matrix(),
          M_MARK, body_root)
        if NECK_WAVES and i % 2 == 1:
            wave(nm + "_Wave", mid + d * r * 1.0, d + t * 0.3, (0.9 + 0.4 * (1 - s)) * SC * NECK_WAVE_K, 0.3 * SC, body_root,
                 M_CREST, curl=0.9, fwd=-t, foam=True)
        if NECK_SWIRL and i % 2 == 0:
            for sgn in (-1, 1):
                swirl(f"{nm}_Swirl_{sgn}", mid + side * sgn * (r * 1.12), t, d, 0.62 * r * (0.7 + 0.5 * hsc), 1.25, body_root,
                      0.07 * SC, M_MARK, seg=5)

for k, (H, hd) in enumerate(zip(head_roots, HEADS)):
    build_neck(k + 1, H, hd[3], hd[0])

# ----------------------------------------------------------
# 11. PATTES PALMÉES : cuisse / épaule en wedge, tibia, bracelet d'argent à gemme, pied palmé,
#     3 doigts + 3 griffes blanches, nageoire de mollet
# ----------------------------------------------------------
FOOT_H = max(0.3, LEG_H * 0.22)
SHIN_H = LEG_H * 0.45

def leg(name, sgn, y, th, hind):
    x = sgn * (BW * 0.5 - th * 0.28)
    thigh_h = LEG_H - (FOOT_H + SHIN_H) + BH * 0.5
    wedge(f"{name}_Thigh", (th * (1.3 if hind else 1.15), th * (1.6 if hind else 1.4), thigh_h),
          (x + sgn * 0.06 * th, y, FOOT_H + SHIN_H + thigh_h / 2 - 0.12), mat=pick(BODY_MATS, BODY_W), parent=legs_root,
          top_x=0.85, top_y=0.8, shift_y=(th * 0.1 if hind else -th * 0.05), bevel=0.07 * SC)
    sy = y + (th * 0.12 if hind else 0)
    B(f"{name}_Shin", (th * 0.92, th * 0.98, SHIN_H + 0.2), (x, sy, FOOT_H + SHIN_H / 2), None, M_BODY, legs_root, bevel=0.05 * SC)
    # Bracelet bleu à bord d'argent (Légendaire) et gemme
    bh_ = SHIN_H * BRACER_K
    bz = FOOT_H + SHIN_H * 0.55
    box(f"{name}_Bracer", (th * 1.12, th * 1.18, bh_), (x, sy, bz), mat=M_SCALEA, parent=legs_root, bevel=0.03 * SC)
    B(f"{name}_BracerRim", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz + bh_ / 2), mat=M_SILVER, parent=legs_root)
    if not IS_BEBE:
        B(f"{name}_BracerRim2", (th * 1.18, th * 1.24, 0.09 * SC), (x, sy, bz - bh_ / 2), mat=M_SILVER, parent=legs_root)
        crystal(f"{name}_BracerGem", 0.14 * SC, 0.08 * SC, 0.12 * SC, (x, sy - th * 0.6, bz), (0, -1, 0), M_GEM, legs_root)
        # nageoire de mollet qui part vers l'arrière
        blade(f"{name}_ShinFin", (x + sgn * th * 0.45, sy + th * 0.35, FOOT_H + SHIN_H * 0.8), (sgn * 0.5, 1.0, 0.25),
              th * 1.1, th * 0.3, M_MEMB, legs_root, droop=0.1, up=(0, 0, 1))
    # Nageoire de genou
    blade(f"{name}_KneeFin", (x + sgn * th * 0.5, sy + (th * 0.3 if hind else -th * 0.1), FOOT_H + SHIN_H + 0.1),
          (sgn * 0.9, 0.5 if hind else -0.4, 0.5), th * 0.9, th * 0.26, M_CREST, legs_root, droop=0.3, up=(0, 1, 0))
    # Pied plat palmé + 3 doigts + 3 griffes
    fy = sy - th * 0.3
    box(f"{name}_Foot", (th * 1.15, th * 1.75, FOOT_H), (x, fy, FOOT_H / 2), mat=M_BODY2, parent=legs_root, bevel=0.05 * SC)
    toe_y = fy - th * 0.88 - th * 0.12
    for c in (-1, 0, 1):
        B(f"{name}_Toe_{c}", (th * 0.3, th * 0.5, FOOT_H * 0.7), (x + c * th * 0.34, toe_y, FOOT_H * 0.35), mat=M_BODY3,
          parent=legs_root)
        shard(f"{name}_Claw_{c}", th * 0.22, th * 0.18, th * CLAW_K, (x + c * th * 0.34, toe_y - th * 0.2, FOOT_H * 0.3),
              (c * 0.12, -1, -0.25), M_CLAW, legs_root)
    for c in (-0.5, 0.5):       # palmes entre les doigts
        B(f"{name}_Web_{c}", (th * 0.36, th * 0.42, FOOT_H * 0.16), (x + c * th * 0.34, toe_y - th * 0.02, FOOT_H * 0.1),
          mat=M_MEMB, parent=legs_root)

LEG_TH_F, LEG_TH_R = BW * 0.4, BW * 0.46
for sgn in (-1, 1):
    leg(f"Legs_Front_{sgn}", sgn, -TL * 0.3, LEG_TH_F, False)
    leg(f"Legs_Back_{sgn}", sgn, TL * 0.3, LEG_TH_R, True)

# ----------------------------------------------------------
# 12. AILES : Typhon n'a pas d'ailes (hydre aquatique, nageoires sur les pattes et la queue). Pas de WINGS_ROOT.
# ----------------------------------------------------------

# ----------------------------------------------------------
# 13. QUEUE : courbe Catmull-Rom, segments bleus, ventre clair, petites vagues dorsales,
#     queue de poisson (nageoire caudale en V avec rayons) et ornement final d'argent
# ----------------------------------------------------------
TAIL_START = Vector((0, TL * 0.45, ZC - 0.05 * BH))
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
    box(f"Tail_Seg_{i}", (2 * r, Ln * 1.12, 2 * r * 0.95), mid, R, pick(BODY_MATS, BODY_W), tail_root,
        bevel=(0.04 * SC if i < 3 else 0))
    if s < 0.8:
        B(f"Tail_Belly_{i}", (2 * r * 0.75, Ln * 0.75, 0.2 * SC), mid - d * (r * 0.97), R, M_BELLY, tail_root)
    if i % 2 == 0:
        B(f"Tail_Back_{i}", (2 * r * 0.8, Ln * 0.95, 0.22 * SC), mid + d * (r * 0.95), R, pick([M_SCALEA, M_BODY2]), tail_root)
    if i % 2 == 1 or TAIL_WAVE_ALL:
        wave(f"Tail_Wave_{i}", mid + d * r * 0.95, d + t * 0.3, 0.55 * SC + r * 1.0, 0.2 * SC + r * 0.25, tail_root,
             M_CREST if i % 4 == 1 else M_MEMB, curl=0.9, fwd=-t, foam=(i % 4 == 1), n=2)
    if TAIL_RINGS and i % 2 == 0:
        B(f"Tail_Ring_{i}", (2 * r * 1.1, Ln * 0.18, 2 * r * 1.06), p1, R @ Euler((0, math.radians(14 * (1 if i % 4 == 0 else -1)), 0)).to_matrix(),
          M_MARK, tail_root)
tip = TAIL_SPINE[-1]
tt_, td_, ts_ = frame(TAIL_SPINE[-1] - TAIL_SPINE[-2])
Z = Vector((0, 0, 1))
B("Tail_TipBase", (BW * 0.24, 0.35 * SC, BW * 0.22), tip, seg_matrix(tt_, td_, ts_), M_SCALEA, tail_root)
# Nageoire caudale en V (queue de poisson) : deux lobes dans le plan vertical, rayons clairs
LF, HF = TAIL_FIN * 1.0, TAIL_FIN * 1.0
for sg, nm_ in ((1, "Up"), (-1, "Low")):
    a0 = tip + tt_ * 0.1
    a1 = tip + tt_ * (0.4 * LF) + Z * (sg * 0.95 * HF)
    a2 = tip + tt_ * (1.0 * LF) + Z * (sg * 1.1 * HF)
    a3 = tip + tt_ * (0.65 * LF) + Z * (sg * 0.1 * HF)
    plate(f"Tail_Fin{nm_}", [a0, a1, a2, a3], 0.07 * SC, M_MEMB, tail_root)
    plate(f"Tail_FinEdge{nm_}", [a1, a2, a2 + tt_ * 0.05 * LF, a1 + Z * (sg * 0.06 * HF)], 0.1 * SC, M_FOAM, tail_root)
    bar(f"Tail_FinRay{nm_}", a0, a2, 0.07 * SC, M_CREST, tail_root, depth=0.09 * SC)
    if TAIL_FIN_RAYS:
        bar(f"Tail_FinRayB{nm_}", a0, a1.lerp(a2, 0.45), 0.06 * SC, M_MARK, tail_root, depth=0.08 * SC)
        bar(f"Tail_FinRayC{nm_}", a0, a3.lerp(a2, 0.55), 0.06 * SC, M_MARK, tail_root, depth=0.08 * SC)
# Ornement final de queue (Légendaire) : anneau d'argent, gemme et trident
if SILVER:
    ring("Tail_OrnRing", BW * 0.16, 0.12 * SC, 0.1 * SC, tip + tt_ * 0.05, tt_, M_SILVER, tail_root, sides=10)
    crystal("Tail_OrnGem", 0.16 * SC, 0.12 * SC, 0.16 * SC, tip + tt_ * 0.12 + Z * (BW * 0.17), Z, M_GEM, tail_root)
    if TRIDENT:
        shard("Tail_TridentMid", 0.24 * SC, 0.2 * SC, TAIL_FIN * 1.25, tip + tt_ * 0.2, tt_, M_SILVER, tail_root, up=(0, 0, 1))
        for sg in (-1, 1):
            shard(f"Tail_TridentSide_{sg}", 0.2 * SC, 0.17 * SC, TAIL_FIN * 0.85, tip + tt_ * 0.2 + ts_ * (sg * 0.2 * SC),
                  tt_ + ts_ * (sg * 0.55), M_SILVER, tail_root, up=(0, 0, 1))

# ----------------------------------------------------------
# 14. RENDU DE RARETÉ (LÉGENDAIRE) + FX
#     Légendaire : tout l'Épique (cristaux d'eau émissifs, iris lumineux, ornements) + ornements d'argent
#     (couronnes, plastron à gemme, épaulières, bracelets, bagues de cornes), aura derrière chaque tête,
#     double rangée de pics, ornement final de queue. FX : gouttes, bulles, vagues et tourbillons flottants.
# ----------------------------------------------------------
# Cristaux d'eau (émissifs) plantés dans le dos entre les vagues
for c in range(CRYS_N):
    y = -TL * 0.3 + (TL * 0.65) * (c + 0.5) / CRYS_N
    sgn = 1 if c % 2 else -1
    crystal(f"Body_WaterCrystal_{c}", 0.2 * SC, 0.3 * SC, 0.55 * SC, (sgn * BW * 0.24, y, ZC + BH * 0.52),
            (sgn * 0.3, 0.1, 1.0), M_AURA, body_root)

if ADD_FLOATING_FX:
    top_z = NECK_TOP.z + HEAD_SCALE * 1.8
    for c in range(FX_N):
        p = Vector((random.uniform(-1, 1) * (BW * 1.6 + 1.0), random.uniform(-TL * 0.9, TL * 0.6 + TAIL_L * 0.3),
                    random.uniform(LEG_H * 0.6, top_z)))
        m = c % 4
        if m == 0:      # goutte lumineuse
            crystal(f"FX_Drop_{c}", FX_SIZE * 0.4, FX_SIZE * 0.8, FX_SIZE * 0.9, p, (0, 0, 1), M_AURA, master, sides=4)
        elif m == 1:    # bulle
            prism(f"FX_Bubble_{c}", FX_SIZE * 0.5, FX_SIZE * 0.5, p, (random.uniform(-1, 1), random.uniform(-1, 1), 1),
                  M_FOAM, master, sides=6)
        elif m == 2:    # petite vague d'écume
            wave(f"FX_Wave_{c}", p, (0, 0, 1), FX_SIZE * 2.2, FX_SIZE * 0.8, master, M_MEMB, curl=1.0,
                 fwd=(random.uniform(-1, 1), random.uniform(-1, 1), 0), foam=True, n=2)
        else:           # petit tourbillon flottant (surtout ado / adulte)
            if FX_SWIRL:
                swirl(f"FX_Swirl_{c}", p, (1, 0, 0), (0, 1, 0), FX_SIZE * 1.6, 1.25, master, FX_SIZE * 0.22, M_AURA, seg=5)
            else:
                prism(f"FX_Bubble2_{c}", FX_SIZE * 0.35, FX_SIZE * 0.35, p, (0, 0, 1), M_AURA, master, sides=5)

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
finalize(master)
