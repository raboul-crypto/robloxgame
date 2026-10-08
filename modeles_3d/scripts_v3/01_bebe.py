# Formes v3 - BEBE (esprit "bebe dragon de film d'animation" facon Krokmou, sans le copier + cahier des charges).
# Bebe dragon assis, gris perle, lisse. Tete LARGE ET PLATE (pas une boule) : crane bas et large, front plat entre
# les yeux, grosses joues, museau court, large et arrondi, grande bouche souriante d'une joue a l'autre ; tres grands
# yeux ecartes a grosses pupilles (regard tendre), tete penchee sur le cote. Corps en poire assis bien droit, pattes
# avant droites a grosses pattes rondes (4 gros doigts ronds separes, coussinets dessous, griffes minuscules), cuisses rondes, queue qui s'enroule
# vers l'avant avec pique en losange, grandes ailes basses posees sur les cotes. Elements propres au jeu (pas Krokmou) :
# petites cornes, crete de plaques, pique de queue, couleur blanche. A lancer en premier (met en place la scene).
import bpy, math, os
from mathutils import Vector as V, Matrix
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v3")
exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())
scene_setup()

D = Dragon("Bebe", "Bebe_", Matrix(), res=0.018)
HC = V((0, -0.45, 1.38))
D.head_frame((0, -0.3, 1.0), yaw=10, roll=-12)              # tete penchee sur le cote (mignon)
# ---- tete large et plate ----
D.hell(HC, 0.52, (1.3, 1.0, 0.68), 2.6)                      # crane bas et large (dessus plat)
D.hell((0, -0.08, 1.44), 0.4, (1.05, 0.9, 0.72), 2.6)         # arriere du crane
D.hell((0, -0.72, 1.55), 0.3, (1.4, 0.8, 0.5), 2.6)           # front plat entre les yeux
D.hell((0, -0.95, 1.3), 0.3, (1.35, 0.9, 0.6), 2.8)           # museau court et large
D.hell((0, -1.1, 1.36), 0.17, (1.5, 0.85, 0.7), 3.0)          # bout du nez arrondi
D.hell((0, -0.82, 1.1), 0.28, (1.45, 1.05, 0.5), 2.8)         # machoire large
for s in (-1, 1):
    D.hell((s * 0.47, -0.6, 1.22), 0.27, (0.9, 1.0, 0.85), 2.8)   # grosses joues
    D.hell((s * 0.1, -1.18, 1.43), 0.05, (1, 1, 0.8), 3.2)       # bourrelets des narines
    dl = D.hd(V((s * 0.5, 0.82, 0.12)).normalized())               # oreilles : lobes souples vers l'arriere
    D.ell(D.hp((s * 0.66, 0.02, 1.5)), 0.15, (1.6, 0.32, 0.75), 3.2, dl.to_track_quat('X', 'Z'))
# ---- cou court ----
D.chain([(0, -0.2, 0.86, 0.25), (0, -0.26, 0.98, 0.24), (0, -0.3, 1.1, 0.24)], 3)
# ---- corps en poire, assis bien droit ----
D.ell((0, 0.05, 0.47), 0.47, (0.95, 0.95, 1.0), 2.4)          # ventre
D.ell((0, -0.16, 0.76), 0.34, (0.95, 0.85, 1.0), 2.4)         # poitrail
for s in (-1, 1):
    D.ell((s * 0.13, -0.42, 0.72), 0.14, (1, 0.7, 0.9), 3.2)
    D.chain([(s * 0.22, -0.34, 0.74, 0.15), (s * 0.24, -0.44, 0.44, 0.13), (s * 0.26, -0.52, 0.26, 0.115)])  # pattes avant droites
    D.paw(s * 0.26, -0.56, s, 1.4)                                                                           # grosses pattes rondes a doigts
    D.ell((s * 0.37, 0.18, 0.36), 0.32, (0.85, 1.1, 0.95), 2.4)                                             # cuisses rondes
    D.paw(s * 0.45, -0.16, s, 1.35)
TAIL = [(0, 0.5, 0.32, 0.2), (0.2, 0.86, 0.17, 0.15), (0.52, 0.98, 0.12, 0.115), (0.8, 0.8, 0.1, 0.085), (0.94, 0.48, 0.1, 0.065), (0.92, 0.16, 0.1, 0.048)]
D.chain(TAIL, 5, 0.95)                                        # queue qui s'enroule vers l'avant
body = D.build_body()                                           # 1re passe : sert a placer les yeux et la bouche

# ---- yeux : tres grands, ecartes sur le devant du visage, grosses pupilles (regard tendre), ils regardent ensemble ----
IRIS = iris_glacier("IrisBebe")
GAZE = D.hp((0, -12.0, 1.45))                                   # point vise au loin, commun aux deux yeux (regard parallele)
EYES = []
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.56, -0.8, 0.2)); nf = (n + D.hd((0, -0.65, 0))).normalized()
    EYES.append(D.eye_at(s, l, n, nf, 0.22, 0.6, GAZE, spread=0.08))
# ---- bouche : grand sourire d'une joue a l'autre ----
MOUTH_YC = -0.95
MP, MPLAN = D.mouth_at([(0, -1.26, 1.18), (0.15, -1.2, 1.175), (0.28, -1.06, 1.18), (0.38, -0.9, 1.2), (0.45, -0.75, 1.25), (0.48, -0.66, 1.31)], MOUTH_YC)
D.groove(MP, 0.022, 0.32)
body = D.build_body()                                           # 2e passe : corps final

for E in EYES:
    D.eye_build(E, IRIS, pupil=(0.3, 0.5), hl_size=0.16); D.eye_shell_lids(E, up=(0.74, 6), lo=(0.8, 0), thick=0.09)
for s in (-1, 1):
    l2, n2 = D.hhit((s * 0.1, -1.18, 1.45), (s * 0.25, -1, 0.55))
    D.sphere(f"Nostril_{s}", l2 - n2 * 0.01, (0.03, 0.03, 0.02), DARK, n2.to_track_quat('-Y', 'Z'), 12)
D.mouth_build("Mouth", MPLAN, MOUTH_YC, 0.012)

# ---- petites cornes courtes recourbees vers l'arriere (sur le dessus plat du crane) ----
for s in (-1, 1):
    l, n = D.hhit(HC, (s * 0.42, 0.25, 0.85)); b = l - n * 0.04
    D.horn(f"Horn_{s}", [b + D.hd(v) for v in ((0, 0, 0), (s * 0.04, 0.1, 0.1), (s * 0.09, 0.24, 0.13), (s * 0.14, 0.36, 0.1))],
           [0.085, 0.07, 0.045, 0.008])
# ---- crete : du haut de la tete au premier tiers de la queue ----
D.crest("Crest", [(0, -0.4, True), (0, -0.2, True), (0, 0.0, True), (0, 0.28, False), (0, 0.45, False), (0.05, 0.62, False), (0.14, 0.8, False)],
        [0.07, 0.09, 0.09, 0.11, 0.11, 0.1, 0.08], 0.13, 0.035)
a, b = V(TAIL[-2][:3]), V(TAIL[-1][:3]); dt = (b - a).normalized()
D.spade("TailTip", b - dt * 0.03, dt, 0.28, 0.22, 0.05, CLAY)
D.claws_build()
# ---- grandes ailes basses, posees sur les cotes (os + membrane tendue) ----
E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))], [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))], [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))]]
for s in (-1, 1):                                               # sur le dos derriere les epaules, ouvertes vers le bas sur les cotes
    l, n = D.hit((s * 0.22, 0.2, 0.55), (s * 0.7, 0.25, 1))
    D.wing(s, l - n * 0.04, 1.2, F, E, W, V((0.02, 0.7, -0.22)), raise_deg=-38, sweep_deg=18, bone_r=0.035)
platform("Plateforme_Bebe", 0, 0.1, 1.6)
print("bebe v3 OK")

if globals().get("RENDER", True):
    shot("v3_bebe", (0, -0.1, 0.8), (0.6, -1, 0.35), 9.0, only="Bebe")
    shot("v3_bebe_face", (0, -0.4, 1.1), (0.12, -1, 0.12), 6.5, only="Bebe")
    shot("v3_bebe_profil", (0, 0.1, 0.9), (1, -0.05, 0.12), 9.0, only="Bebe")
    shot("v3_bebe_dos", (0, 0.2, 0.9), (0.5, 1, 0.5), 9.0, only="Bebe")
    shot("v3_bebe_pattes", (0, -0.45, 0.15), (0.35, -1, 0.45), 3.2, only="Bebe")
    shot("v3_bebe_dessous", (0, -0.3, 0.05), (0.15, -0.5, -1), 3.6, only="Bebe", hide=("Ground", "Plateforme_Bebe"))
    mid = (EYES[0]["c"] + EYES[1]["c"]) / 2; fw = D.hd(V((0, -1, 0)))
    shot("v3_bebe_yeux", mid + fw * 0.2, fw + V((0.3, 0, 0.12)), 3.4, only="Bebe")
