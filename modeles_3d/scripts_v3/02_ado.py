# Formes v3 - ADO (esprit "jeune dragon de jeu de plateforme" facon Spyro, sans le copier + cahier des charges).
# Evolution du bebe : plus grand, svelte et athletique, torse plus long, musculature visible (pectoraux, abdominaux,
# epaules, cuisses), tete plus allongee (museau prononce, joues encore rondes, machoire robuste), cou plus long,
# queue longue et epaisse a la base avec un grand pique en losange, crete de plaques de la tete au bout de la queue,
# cornes plus longues et plus recourbees, 2 petites pointes frontales, yeux a globe au regard determine,
# pattes longues a 4 orteils et griffes allongees. Debout, tete tournee vers le spectateur. A lancer apres 01_bebe.py.
import bpy, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v3")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())

D = Dragon("Ado", "Ado_", Matrix.Translation((5.0, 0, 0)) @ Matrix.Scale(1.15, 4))
HC = V((0, -0.95, 2.22))
D.head_frame((0, -0.82, 2.08), yaw=14, roll=-6)               # tourne vers le spectateur, legerement inclinee
# ---- tete ----
D.hell(HC, 0.37, (1.0, 1.08, 0.92), 2.6)                      # crane
D.hell((0, -0.8, 2.3), 0.28, (0.95, 1.0, 0.9))                 # arriere du crane
D.hell((0, -1.3, 2.1), 0.21, (0.88, 1.55, 0.72), 2.8)          # museau prononce
D.hell((0, -1.56, 2.14), 0.13, (0.95, 0.9, 0.85), 3.0)         # bout du nez
D.hell((0, -1.2, 1.98), 0.2, (1.0, 1.5, 0.58), 2.8)            # machoire robuste
for s in (-1, 1):
    D.hell((s * 0.2, -1.0, 2.05), 0.16, (0.9, 1.1, 0.9), 3.0)  # joues encore rondes
    D.hell((s * 0.15, -1.1, 2.34), 0.1, (1.3, 1.1, 0.55), 3.2) # arcades
    D.hell((s * 0.065, -1.62, 2.2), 0.055, (1, 1, 0.8), 3.2)  # bourrelets des narines
# ---- cou plus long ----
D.chain([(0, -0.45, 1.4, 0.23), (0, -0.55, 1.66, 0.2), (0, -0.66, 1.88, 0.185), (0, -0.77, 2.06, 0.18), (0, -0.86, 2.16, 0.18)], 4)
# ---- torse long et athletique ----
D.ell((0, -0.32, 1.18), 0.37, (0.85, 0.95, 1.05), 2.6)         # cage thoracique
D.ell((0, 0.08, 1.16), 0.33, (0.8, 1.2, 0.9), 2.6)             # cotes
D.ell((0, 0.5, 1.12), 0.26, (0.74, 1.05, 0.84), 2.6)           # taille
D.ell((0, 0.84, 1.16), 0.31, (0.85, 0.95, 0.92), 2.6)          # hanches
for s in (-1, 1):
    D.ell((s * 0.14, -0.56, 1.08), 0.17, (1, 0.75, 1.0), 3.2)  # pectoraux
    D.ell((s * 0.28, -0.34, 1.26), 0.16, (0.9, 1.1, 1.0), 3.2) # epaules
    for y in (-0.12, 0.08, 0.28): D.ell((s * 0.07, y, 0.9), 0.07, (1.2, 1.4, 0.35), 3.0)     # abdominaux (relief discret)
    D.chain([(s * 0.22, -0.36, 1.15, 0.19), (s * 0.28, -0.28, 0.76, 0.145), (s * 0.29, -0.4, 0.34, 0.12), (s * 0.29, -0.48, 0.11, 0.11)])
    D.ell((s * 0.28, -0.32, 0.86), 0.15, (0.9, 1.0, 1.3), 3.0) # avant-bras
    D.foot(s * 0.29, -0.54, s, 1.2, claw_len=0.085, claw_r=0.025)
    D.chain([(s * 0.25, 0.84, 1.1, 0.26), (s * 0.31, 0.62, 0.7, 0.17), (s * 0.32, 0.92, 0.36, 0.125), (s * 0.32, 0.82, 0.11, 0.11)])
    D.ell((s * 0.28, 0.8, 0.96), 0.25, (0.8, 1.05, 1.15), 3.2) # cuisses
    D.foot(s * 0.32, 0.76, s, 1.25, claw_len=0.085, claw_r=0.025)
TAIL = [(0, 1.08, 1.16, 0.24), (0.02, 1.5, 1.06, 0.18), (0.06, 1.95, 0.95, 0.13), (0.12, 2.4, 0.88, 0.09), (0.18, 2.78, 0.9, 0.06), (0.22, 3.02, 0.94, 0.045)]
D.chain(TAIL, 5, 0.95)
body = D.build_body()

# ---- yeux au regard determine ----
IRIS = iris_glacier("IrisAdo")
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.58, -0.78, 0.12)); nf = (n + D.hd((0, -0.45, 0))).normalized()
    D.eye(s, l, n, nf, 0.115, IRIS, lid_up=(0.55, -6), lid_lo=(0.66, 0), sink=0.38, rim=0)
    l2, n2 = D.hhit((s * 0.07, -1.65, 2.22), (s * 0.3, -1, 0.4))
    D.sphere(f"Nostril_{s}", l2 - n2 * 0.01, (0.028, 0.028, 0.018), DARK, n2.to_track_quat('-Y', 'Z'), 12)
M = D.mouth("Mouth", [-1.62, -1.5, -1.35, -1.2, -1.06], [2.07, 2.05, 2.03, 2.04, 2.08], [0.008, 0.012, 0.013, 0.012, 0.006])
for s, pts in M.items():
    if len(pts) >= 3:
        p, n = pts[1]; b = p - n * 0.008
        D.cone(f"Fang_{s}", b, b + D.hd((0, -0.01, -0.065)), 0.018, KERA)

# ---- cornes plus longues et recourbees, 2 pointes frontales, pointes de joues ----
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.42, 0.62, 0.66)); b = l - n * 0.05
    D.horn(f"Horn_{s}", [b + D.hd(v) for v in ((0, 0, 0), (s * 0.06, 0.24, 0.1), (s * 0.11, 0.5, 0.14), (s * 0.12, 0.74, 0.28), (s * 0.1, 0.86, 0.44))],
           [0.11, 0.095, 0.065, 0.035, 0.006])
    l, n = D.hhit(HC, (s * 0.14, -0.5, 0.85)); b = l - n * 0.02
    D.cone(f"HornSmall_{s}", b, b + n * 0.13 + D.hd((0, 0.06, 0)), 0.04, KERA, smooth=False)
    for k, (dz, lg) in enumerate(((0.05, 0.24), (-0.12, 0.18))):
        l, n = D.hhit((0, -1.0, 2.05), (s, 0.4, dz)); b = l - n * 0.02
        D.cone(f"Cheek_{s}_{k}", b, b + D.hd((s * 0.1, lg, 0.02)), 0.045, KERA, smooth=False)
# ---- crete du haut de la tete au bout de la queue ----
def tail_x(y):
    if y <= TAIL[0][1]: return 0.0
    for a, b in zip(TAIL, TAIL[1:]):
        if a[1] <= y <= b[1]: return lerp(a[0], b[0], (y - a[1]) / (b[1] - a[1]))
    return TAIL[-1][0]
YS = [-0.42, -0.2, 0.05, 0.3, 0.55, 0.8, 1.05, 1.3, 1.55, 1.8, 2.05, 2.3, 2.55, 2.75]
path = [(0, -0.9, True), (0, -0.7, True)] + [(tail_x(y), y, False) for y in YS]
heights = [0.1, 0.12] + [0.14, 0.16, 0.18, 0.18, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.08]
D.crest("Crest", path, heights, 0.16, 0.04)
a, b = V(TAIL[-2][:3]), V(TAIL[-1][:3]); dt = (b - a).normalized()
D.spade("TailTip", b - dt * 0.04, dt, 0.42, 0.3, 0.06, CLAY)
D.claws_build()
# ---- ailes plus grandes, phalanges plus robustes ----
E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))], [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))],
     [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))], [W, V((0.62, 0.64, 0.0)), V((0.52, 1.06, -0.3))]]
for s in (-1, 1):
    l, n = D.hit((s * 0.22, -0.2, 1.35), (s * 0.45, 0.1, 1))
    D.wing(s, l - n * 0.05, 1.25, F, E, W, V((0.02, 0.85, -0.22)), raise_deg=30, sweep_deg=10, bone_r=0.034)
platform("Plateforme_Ado", 5.0, 0.7, 2.6)
print("ado v3 OK")

if globals().get("RENDER", True):
    S = D.S
    shot("v3_ado", (5.0, 0.5, 1.7), (0.6, -1, 0.3), 17, only="Ado")
    shot("v3_ado_tete", S @ D.hp(HC) + V((0, -0.3, -0.1)), (0.55, -1, 0.12), 6.5, only="Ado")
    shot("v3_ado_profil", (5.0, 0.8, 1.7), (1, -0.05, 0.12), 17, only="Ado")
