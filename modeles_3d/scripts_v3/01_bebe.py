# Formes v3 - BEBE (d'apres l'image de reference + cahier des charges).
# Bebe dragon assis, gris perle, lisse. Tete surdimensionnee et ronde (museau court, machoire un peu carree,
# narines marquees), cou distinct, corps globuleux avec pectoraux naissants, pattes avant en "coussins" avec
# 4 orteils et griffes coniques ivoire, pattes arriere charnues, queue effilee avec pique en losange,
# crete de plaques triangulaires du haut de la tete au premier tiers de la queue, yeux a globe + paupieres,
# tete tournee legerement sur le cote. A lancer en premier (met en place la scene).
import bpy, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v3")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())
scene_setup()

D = Dragon("Bebe", "Bebe_", Matrix())
HC = V((0, -0.38, 1.44))
D.head_frame((0, -0.3, 1.0), yaw=12)                        # regarde legerement sur le cote
# ---- tete ----
D.hell(HC, 0.6, (1.12, 0.98, 0.9), 2.6)                      # crane rond
D.hell((0, -0.92, 1.18), 0.31, (1.1, 1.05, 0.7), 2.8)         # museau court
D.hell((0, -1.12, 1.2), 0.2, (1.15, 0.9, 0.72), 3.0)          # bout du nez
D.hell((0, -0.84, 1.0), 0.22, (1.25, 1.1, 0.55), 3.0)         # machoire un peu carree
for s in (-1, 1):
    D.hell((s * 0.3, -0.74, 1.15), 0.21, (1, 1, 0.9), 3.0)    # joues
    D.hell((s * 0.075, -1.22, 1.27), 0.07, (1, 1, 0.8), 3.2)  # bourrelets des narines
# ---- cou distinct ----
D.chain([(0, -0.22, 0.86, 0.24), (0, -0.28, 1.0, 0.22), (0, -0.32, 1.12, 0.22)], 3)
for s in (-1, 1): D.ell((s * 0.12, -0.36, 0.98), 0.12, (0.8, 1, 1.4), 3.2)
# ---- corps globuleux, pectoraux naissants ----
D.ell((0, 0.05, 0.5), 0.48, (0.95, 1.0, 0.95), 2.4)
D.ell((0, -0.18, 0.72), 0.34, (0.92, 0.85, 0.95), 2.4)
for s in (-1, 1):
    D.ell((s * 0.13, -0.44, 0.7), 0.15, (1, 0.7, 0.9), 3.2)
    D.chain([(s * 0.22, -0.38, 0.72, 0.15), (s * 0.25, -0.44, 0.42, 0.145), (s * 0.27, -0.48, 0.17, 0.165)])   # pattes avant
    D.foot(s * 0.27, -0.55, s, 1.25, claw_len=0.05, claw_r=0.022)
    D.ell((s * 0.36, 0.2, 0.38), 0.32, (0.85, 1.1, 0.92), 2.4)                                                # cuisses
    D.foot(s * 0.44, -0.12, s, 1.2, claw_len=0.05, claw_r=0.022)
TAIL = [(0, 0.5, 0.35, 0.2), (0.12, 0.8, 0.2, 0.15), (0.3, 1.0, 0.14, 0.11), (0.5, 1.06, 0.12, 0.08), (0.66, 0.98, 0.12, 0.055)]
D.chain(TAIL, 5, 0.95)
body = D.build_body()

# ---- yeux : globe bleu glacier, pupille fendue, paupieres arrondies (regard innocent) ----
IRIS = iris_glacier("IrisBebe")
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.4, -0.92, 0.0)); nf = (n + D.hd((0, -0.7, 0))).normalized()
    D.eye(s, l, n, nf, 0.185, IRIS, lid_up=(0.74, 0), lid_lo=(0.76, 0), sink=0.42)
    l2, n2 = D.hhit((s * 0.08, -1.22, 1.3), (s * 0.25, -1, 0.5))
    D.sphere(f"Nostril_{s}", l2 - n2 * 0.012, (0.036, 0.036, 0.024), DARK, n2.to_track_quat('-Y', 'Z'), 12)
D.mouth("Mouth", [-1.22, -1.12, -1.0, -0.88, -0.76], [1.06, 1.05, 1.05, 1.07, 1.11], [0.008, 0.013, 0.014, 0.013, 0.007])

# ---- cornes enroulees (aretes definies) + deux petites pointes frontales + oreilles-nageoires ----
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.48, 0.2, 0.85)); b = l - n * 0.05
    D.horn(f"Horn_{s}", [b + D.hd(v) for v in ((0, 0, 0), (s * 0.05, 0.12, 0.16), (s * 0.13, 0.32, 0.22), (s * 0.23, 0.5, 0.2), (s * 0.32, 0.62, 0.3))],
           [0.12, 0.1, 0.075, 0.045, 0.008])
    l, n = D.hhit(HC, (s * 0.12, -0.35, 0.93)); b = l - n * 0.02
    D.cone(f"HornSmall_{s}", b, b + n * 0.17 + D.hd((0, 0.05, 0)), 0.05, KERA, smooth=False)
    l, n = D.hhit(HC, (s * 0.92, 0.12, -0.05)); b = l - n * 0.03
    D.cone(f"Ear_{s}", b, b + D.hd((s * 0.24, 0.26, -0.08)), 0.14, CLAY, flatx=0.3)
# ---- crete : du haut de la tete (entre les cornes) au premier tiers de la queue ----
D.crest("Crest", [(0, -0.3, True), (0, -0.12, True), (0, 0.05, True), (0, 0.28, False), (0, 0.45, False), (0.05, 0.62, False), (0.1, 0.78, False)],
        [0.08, 0.1, 0.1, 0.12, 0.12, 0.1, 0.08], 0.13, 0.035)
a, b = V(TAIL[-2][:3]), V(TAIL[-1][:3]); dt = (b - a).normalized()
D.spade("TailTip", b - dt * 0.03, dt, 0.3, 0.22, 0.05, CLAY)
D.claws_build()
# ---- petites ailes (os + membrane tendue) ----
E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))], [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))], [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))]]
for s in (-1, 1):
    l, n = D.hit((s * 0.2, 0.05, 0.85), (s * 0.45, 0.2, 1))
    D.wing(s, l - n * 0.04, 0.6, F, E, W, V((0.02, 0.7, -0.22)), raise_deg=30, sweep_deg=10, bone_r=0.035)
platform("Plateforme_Bebe", 0, 0.1, 1.6)
print("bebe v3 OK")

if globals().get("RENDER", True):
    shot("v3_bebe", (0, -0.1, 0.8), (0.6, -1, 0.35), 9.0, only="Bebe")
    shot("v3_bebe_face", (0, -0.4, 1.1), (0.12, -1, 0.12), 6.5, only="Bebe")
    shot("v3_bebe_profil", (0, 0.1, 0.9), (1, -0.05, 0.12), 9.0, only="Bebe")
