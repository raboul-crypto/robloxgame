# Formes v3 - ADULTE (2e image de reference + cahier des charges).
# Evolution finale de l'ado : long, sec, athletique et dangereux (pas "boudine"). Cage thoracique large et profonde
# qui se resserre vers un abdomen tonique, epaules et cuisses enormes et separees, tres long cou musclé, tete haute
# allongee (long museau, machoires puissantes, os de la machoire visibles, arcades lourdes), longues pattes massives
# a 4 orteils et tres longues griffes, queue longue avec un immense pique en losange, crete de grandes plaques de la
# tete au bout de la queue, cornes tres longues a pointes secondaires, excroissances osseuses sur les joues,
# plaques d'armure lisses (tete, dos, epaules, cuisses), ailes immenses et anguleuses. A lancer apres 02_ado.py.
import bpy, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v3")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())

X0 = 13.5
D = Dragon("Adulte", "Adulte_", Matrix.Translation((X0, 0, 0)) @ Matrix.Scale(1.3, 4))
HC = V((0, -1.95, 3.55))
D.head_frame((0, -1.62, 3.42), yaw=15, pitch=10, roll=-5)    # tete haute, legerement inclinee vers le spectateur
# ---- tete allongee ----
D.hell(HC, 0.27, (0.95, 1.25, 0.82), 2.6)                     # crane
D.hell((0, -1.78, 3.62), 0.25, (1.0, 1.0, 0.9))                # arriere du crane
D.hell((0, -2.38, 3.47), 0.19, (0.9, 1.8, 0.66), 2.8)          # long museau
D.hell((0, -2.75, 3.42), 0.12, (0.95, 0.9, 0.75), 3.0)         # bout du nez
D.hell((0, -2.28, 3.33), 0.18, (1.0, 1.85, 0.55), 2.8)         # machoire puissante
for s in (-1, 1):
    D.hell((s * 0.16, -2.0, 3.38), 0.13, (0.9, 1.5, 0.8), 3.2) # os de la machoire
    D.hell((s * 0.13, -2.1, 3.66), 0.075, (1.4, 1.6, 0.5), 3.6) # arcades
    D.hell((s * 0.06, -2.82, 3.47), 0.05, (1, 1, 0.8), 3.2)    # bourrelets des narines
# ---- tres long cou musclé ----
D.chain([(0, -0.85, 1.95, 0.34), (0, -1.08, 2.35, 0.29), (0, -1.25, 2.75, 0.25), (0, -1.36, 3.08, 0.225), (0, -1.5, 3.33, 0.21), (0, -1.65, 3.48, 0.2)], 4)
for s in (-1, 1): D.ell((s * 0.1, -1.0, 2.25), 0.14, (0.8, 1.0, 1.6), 3.0)
# ---- torse sec et athletique ----
D.ell((0, -0.5, 1.65), 0.5, (0.82, 1.05, 1.0), 2.6)            # cage thoracique large et profonde
D.ell((0, -0.88, 1.45), 0.25)                                   # sternum
D.ell((0, 0.2, 1.55), 0.36, (0.75, 1.15, 0.8), 2.6)             # abdomen
D.ell((0, 0.62, 1.55), 0.3, (0.72, 1.0, 0.78), 2.6)             # taille
D.ell((0, 1.02, 1.62), 0.38, (0.85, 0.95, 0.9), 2.6)            # hanches
for s in (-1, 1):
    D.ell((s * 0.18, -0.9, 1.5), 0.22, (1, 0.75, 1.0), 3.3)    # pectoraux
    for y in (-0.1, 0.12, 0.34): D.ell((s * 0.08, y, 1.24), 0.08, (1.2, 1.4, 0.35), 3.0)   # abdominaux (relief discret)
    D.ell((s * 0.4, -0.62, 1.78), 0.27, (0.85, 1.1, 1.0), 3.2) # epaules enormes
    D.ell((s * 0.45, -0.42, 1.32), 0.17, (0.85, 1.0, 1.4), 3.0)# triceps
    D.chain([(s * 0.38, -0.6, 1.6, 0.24), (s * 0.47, -0.45, 1.02, 0.17), (s * 0.47, -0.74, 0.42, 0.13), (s * 0.47, -0.84, 0.12, 0.12)])
    D.ell((s * 0.48, -0.58, 0.78), 0.15, (0.9, 1.0, 1.4), 3.0) # avant-bras
    D.foot(s * 0.47, -0.92, s, 1.7, claw_len=0.15, claw_r=0.03)
    D.chain([(s * 0.38, 1.02, 1.5, 0.32), (s * 0.47, 0.7, 0.98, 0.2), (s * 0.47, 1.15, 0.5, 0.14), (s * 0.47, 1.0, 0.12, 0.12)])
    D.ell((s * 0.41, 0.94, 1.28), 0.27, (0.85, 1.05, 1.15), 3.2)   # cuisses enormes
    D.ell((s * 0.37, 1.22, 1.3), 0.22, (0.8, 1.0, 1.2), 3.0)       # arriere des cuisses
    D.foot(s * 0.47, 0.92, s, 1.75, claw_len=0.15, claw_r=0.03)
TAIL = [(0, 1.38, 1.6, 0.3), (0.05, 1.95, 1.38, 0.24), (0.15, 2.55, 1.08, 0.18), (0.3, 3.15, 0.78, 0.13), (0.45, 3.7, 0.58, 0.095), (0.55, 4.15, 0.5, 0.07), (0.6, 4.5, 0.52, 0.05)]
D.chain(TAIL, 5, 0.95)
body = D.build_body()

# ---- yeux feroces ----
IRIS = iris_glacier("IrisAdulte")
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.55, -0.8, 0.2)); nf = (n + D.hd((0, -0.35, 0))).normalized()
    D.eye(s, l, n, nf, 0.085, IRIS, lid_up=(0.36, -28), lid_lo=(0.52, 10), sink=0.32)
    l2, n2 = D.hhit((s * 0.07, -2.85, 3.5), (s * 0.3, -1, 0.5))
    D.sphere(f"Nostril_{s}", l2 - n2 * 0.01, (0.03, 0.03, 0.02), DARK, n2.to_track_quat('-Y', 'Z'), 12)
M = D.mouth("Mouth", [-2.85, -2.65, -2.4, -2.15, -1.9], [3.35, 3.33, 3.32, 3.33, 3.38], [0.009, 0.014, 0.016, 0.015, 0.007])
for s, pts in M.items():
    for i, (dz, ln) in ((1, (-1, 0.1)), (2, (-1, 0.08)), (3, (1, 0.07))):
        if i < len(pts):
            p, n = pts[i]; b = p + D.hd((0, 0, -0.01 if dz < 0 else 0.01)) - n * 0.01
            D.cone(f"Fang_{s}_{i}", b, b + D.hd((0, -0.015, dz * ln)), 0.022, KERA)

# ---- cornes tres longues a pointes secondaires, pointes frontales, excroissances des joues ----
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.4, 0.62, 0.68)); b = l - n * 0.05
    D.horn(f"Horn_{s}", [b + D.hd(v) for v in ((0, 0, 0), (s * 0.12, 0.35, 0.05), (s * 0.22, 0.72, 0.06), (s * 0.28, 1.05, 0.18), (s * 0.26, 1.32, 0.36))],
           [0.11, 0.095, 0.07, 0.04, 0.006], spikes=3, spike_len=0.1, spike_r=0.03)
    l, n = D.hhit(HC, (s * 0.14, -0.5, 0.85)); b = l - n * 0.02
    D.cone(f"HornSmall_{s}", b, b + n * 0.15 + D.hd((0, 0.07, 0)), 0.04, KERA, smooth=False)
    for k, (dz, lg) in enumerate(((0.1, 0.16), (-0.1, 0.13), (-0.3, 0.1))):
        l, n = D.hhit((0, -2.0, 3.4), (s, 0.3, dz)); b = l - n * 0.02
        D.cone(f"Cheek_{s}_{k}", b, b + D.hd((s * 0.08, lg, 0.02)), 0.04, KERA, smooth=False)
# ---- plaques d'armure osseuse lisses (tete, dos, epaules, cuisses) ----
l, n = D.hhit((0, -2.05, 3.55), (0, -0.1, 1)); D.plate("ArmorTete", l, n, D.hd((0, 1, 0)), 0.13, 0.26, 0.03)
for s in (-1, 1):
    for k, y in enumerate((-0.55, -0.2, 0.15, 0.5, 0.85)):
        l, n = D.hit((s * 0.2, y, 1.6), (s * 0.35, 0, 1)); D.plate(f"ArmorDos_{s}_{k}", l, n, (0, 1, 0), 0.08, 0.2, 0.022)
    l, n = D.hit((s * 0.4, -0.62, 1.78), (s, 0, 0.6)); D.plate(f"ArmorEpaule_{s}", l, n, (0, 1, -0.3), 0.14, 0.32, 0.028)
    l, n = D.hit((s * 0.41, 0.94, 1.28), (s, 0.1, 0.3)); D.plate(f"ArmorCuisse_{s}", l, n, (0, 1, -0.2), 0.14, 0.32, 0.028)
# ---- crete de grandes plaques de la tete au bout de la queue ----
def tail_x(y):
    if y <= TAIL[0][1]: return 0.0
    for a, b in zip(TAIL, TAIL[1:]):
        if a[1] <= y <= b[1]: return lerp(a[0], b[0], (y - a[1]) / (b[1] - a[1]))
    return TAIL[-1][0]
YS = [-1.42, -1.3, -1.18, -1.02, -0.85, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.85, 2.2, 2.55, 2.9, 3.25, 3.6, 3.9, 4.2]
path = [(0, -1.85, True), (0, -1.65, True)] + [(tail_x(y), y, False) for y in YS]
heights = [0.14, 0.16, 0.16, 0.18, 0.2, 0.22, 0.26, 0.3, 0.32, 0.34, 0.34, 0.32, 0.3, 0.28, 0.26, 0.24, 0.22, 0.2, 0.17, 0.15, 0.13, 0.12, 0.1]
D.crest("Crest", path, heights, 0.22, 0.05, lean=0.4)
a, b = V(TAIL[-2][:3]), V(TAIL[-1][:3]); dt = (b - a).normalized()
D.spade("TailTip", b - dt * 0.05, dt, 0.7, 0.5, 0.09, CLAY)
D.claws_build()
# ---- ailes immenses et anguleuses, phalanges epaisses ----
E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))], [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))],
     [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))], [W, V((0.62, 0.64, 0.0)), V((0.52, 1.06, -0.3))]]
for s in (-1, 1):
    l, n = D.hit((s * 0.3, -0.45, 1.95), (s * 0.45, 0.1, 1))
    D.wing(s, l - n * 0.06, 2.5, F, E, W, V((0.02, 0.8, -0.22)), raise_deg=28, sweep_deg=18, scallop=0.38, bone_r=0.04)
platform("Plateforme_Adulte", X0, 1.0, 5.2)
print("adulte v3 OK")

if globals().get("RENDER", True):
    S = D.S
    shot("v3_adulte", (X0, 0.6, 2.6), (0.6, -1, 0.3), 32, only="Adulte")
    shot("v3_adulte_tete", S @ D.hp(HC) + V((0, -0.4, 0.0)), (0.55, -1, 0.12), 8.5, only="Adulte")
    shot("v3_adulte_profil", (X0, 1.0, 2.6), (1, -0.05, 0.1), 32, only="Adulte")
    shot("v3_bebe_ado_adulte", (7.0, 0.8, 2.4), (0.22, -1, 0.26), 44)
