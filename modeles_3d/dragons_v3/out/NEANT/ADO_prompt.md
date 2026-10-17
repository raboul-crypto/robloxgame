Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Néant » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Néant = Ténèbres, Secret, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Néant : pose, proportions, chaque
élément de la tête, du corps, des ailes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Ado : serpent noir dressé en S sur ses anneaux au sol, cou plus long (NECK_H 5.4), tête sérieuse, 2 ailes (envergure 6,2 m) dressées sur le haut du dos, un anneau lumineux derrière la tête.
- Tête : crâne carré en wedge, museau plus long avec liseré violet, mâchoire indigo, ligne de bouche violette, 2 narines. Yeux : orbite noire, blanc lumineux, pupille fendue noire, sourcils inclinés (16°). 2 petits crocs blancs par côté, 2 écailles de joue par côté, oreilles-nageoires fantômes (alpha 0.55, la gauche plus longue), joue droite fantôme.
- Cornes et couronne : 2 cornes noires en arc (gauche plus longue) à pointe violette lumineuse, couronne de 8 éclats déchirés derrière le crâne (noir, fantôme, violet), 1 fissure lumineuse sur le crâne.
- Signe distinctif : corps noir profond comme un trou noir, liserés violets lumineux, anneaux concentriques violets, yeux blancs lumineux.
- Corps : segments noirs avec liserés violets lumineux sur les flancs (plus fournis à gauche), écailles de flanc violet très sombre, ligne dorsale violette, plaques de ventre indigo, plastron indigo avec gemme, anneau lumineux autour du corps à chaque segment, 3 anneaux concentriques emboîtés sur le dos du torse, 3 anneaux concentriques posés au sol, crête d'éclats déchirés (certains manquent, certains fantômes), épaulières de 3 éclats par côté, fissures lumineuses asymétriques.
- Ailes : 2 ailes : os à liseré violet (strength 1.4), 3 doigts, membrane indigo translucide (alpha 0.62), éclat violet au poignet, 1 lambeau fantôme qui pend. L'aile droite a un doigt de moins et est plus courte.
- Pattes : aucune (amphiptère). LEGS_ROOT ne porte que les anneaux concentriques posés au sol.
- Queue : la queue se redresse au centre de l'anneau ; les segments après 80 % deviennent fantômes, anneau au bout et 5 fragments fantômes qui se détachent.
- Halo : 1 anneau vertical lumineux derrière la tête (axe Y), parenté au MASTER.
- Rendu de rareté (Secret) : Secret à mi-puissance : crête déchirée, fissures émissives (strength 2.6), parties fantômes, aile déchirée, halo d'un anneau lumineux derrière la tête. 22 éclats et 3 petits anneaux flottants.
- Palette (hex, Principled BSDF) :
  Body #0B0910 (corps, léger reflet : metallic 0.25), BodyDark #08070C (segments alternés, dessus du museau), ScaleB #211439 (écailles de flanc, sourcils, éclats),
  Belly #1E2A5E (ventre, mâchoire, plastron), Glow #9B5CFF (émissif : liserés, fissures, pointes de cornes, gemmes), Crest #6E3FC8 (émissif faible : liserés secondaires, os d'ailes),
  RingGlow #9B5CFF (émissif, alpha 0.65 : anneaux concentriques), Membrane #1E2A5E (alpha 0.62), Ghost #2A1850 (alpha 0.55, lueur faible #6E3FC8 : parties fantômes),
  GhostLight #9B5CFF (alpha 0.5, émissif : fragments qui se détachent), Claw #6E3FC8, Eye #F4F0FF (émissif : yeux blancs lumineux), White #F2F2F2 (crocs, reflets), Black #0A0A0A (pupilles), Nostril #050407 (orbites, narines).
  Mêmes couleurs aux 3 stades.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Étrange et inquiétant mais adapté
  à un jeune public (aucun sang, rien de gore).

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du cou), jamais sur les éclats, anneaux, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty NEANT_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « NEANT_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots NEANT_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le corps est un long serpent : une seule courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (BODY_STEP), avec un repère par segment (tangente, dos, côté) et un rayon qui varie par clés. Les points de contrôle (cou dressé en S, descente, anneau au sol, queue qui remonte au centre), RADIUS_KEYS, ZB, NECK_H, COIL_R, HEAD_SCALE, WING_SPAN... sont des variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission sur les liserés, anneaux, fissures, yeux et pointes ; parties fantômes, membranes et anneaux en alpha 0.5 à 0.65. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (7741) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 22 éclats et 3 petits anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes (aucune), 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, anneaux)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
