Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Lagon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi. Si tu as une image,
   seul le dragon en bas à gauche, nommé « Bébé Lagon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Lagon = Eau, Rare, Rapide, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image (quand elle existe) et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description ci-dessous impose) sur le Bébé Lagon : pose, proportions,
chaque élément de la tête, du corps, des ailes et de la queue, et la palette. Puis liste les contraintes du GDD
qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : petit serpent turquoise enroulé, cou court qui se penche vers l'avant, tête énorme (environ 35 % de la hauteur), petites ailes. Pas de pattes. Tête inclinée de 10° vers l'avant.
- Tête : crâne carré en wedge turquoise #1FB2C4, museau très court, arête claire #4FD0DB, plaque du front sombre, mâchoire ivoire #F2EBD8, ligne de bouche, 2 narines, 1 petit losange foncé de chaque côté du museau. Yeux : très grands (blanc, grand iris turquoise lumineux, pupille ronde noire, 2 petits reflets blancs), pas de crocs, pas de sourcils.
- SIGNE DISTINCTIF, crête-nageoire : éventail de 4 rayons derrière le crâne, dans le plan vertical : rayons turquoise, pointes pâles #CFF5F7, membrane translucide bleu glacier #8FE0E8 (matériau alpha 0.78). 2 nageoires-oreilles en éventail de chaque côté du crâne, 1 nageoire(s) de joue par côté, 5 épines de collerette en arc derrière le crâne.
- Cornes : 2 petites cornes pâles recourbées vers l'arrière sur bases turquoise sombre, une seule pointe pour le Bébé.
- Corps : segments turquoise en deux teintes alternées (#1FB2C4 / #1792A8), anneaux sombres #0B4752 aux jointures, plaques de ventre ivoire bien séparées, plastron ivoire. SIGNE DISTINCTIF : écailles en LOSANGES sur les flancs (grand losange #128A9A, petit losange clair #4FD0DB un segment sur deux). Nageoire dorsale translucide (un segment sur deux, taille 0.8) en alternance avec de petites plaques sombres.
- Ailes : 2 ailes membraneuses turquoise translucides (alpha 0.62, #6FDCE6) : bras, avant-bras et 3 doigts en os #1FB2C4, griffe de pouce pâle, petite pointe pâle au bout de chaque doigt. Reflets d'eau : 1 ligne(s) brisée(s) claire(s) entre deux doigts (comme la lumière au fond d'une piscine), faiblement émissives (strength 0.9). Envergure d'une aile environ 5.6 (unités de travail).
- Queue : même courbe que le corps ; le bout porte un anneau pâle et une nageoire caudale en V (poisson) : 2 lobes de 4 rayons avec membrane translucide, longueur 1.7. 4 petites nageoires-vagues posées au sol autour des anneaux.
- Rendu de rareté (Rare), discret : motif secondaire (losanges clairs + reflets d'eau sur les ailes), cornes à 2 pointes (une seule sur le Bébé), crête simple (la double arrive à l'Ado), accent lumineux discret : iris turquoise (strength 1.3), reflets d'eau (0.9) et gouttes (0.9). 6 gouttes d'eau (cristaux à 4 pans, translucides) flottent autour.
- Palette (hex, Principled BSDF) :
  Body #1FB2C4 (corps), BodyDark #1792A8 (segments alternés, sourcils, plaques du dos), BodyLight #4FD0DB (arête du museau, petits losanges),
  Mouth #0B4752 (bouche, narines, jointures), Belly #F2EBD8 (ventre, mâchoire, plastron), Diamond #128A9A (losanges),
  Fin #8FE0E8 translucide (crête, oreilles, dorsale, caudale), FinBone #1FB2C4 (rayons, os d'aile), Tip #CFF5F7 (pointes, cornes, crocs),
  Membrane #6FDCE6 translucide, Caustic #E4FFFF émission #9FF4FF strength 0.9, EyeWhite #F4F8F8, Iris #16C7DD émission strength 1.3,
  Black #06141A (pupilles), Drop #BFF7FF émission #7FE9F7 strength 0.9 translucide.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les nageoires sont des plaques fines (rayons en barres + membrane), les losanges des plaques plates posées sur la peau.

CONTRAINTES TECHNIQUES
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du corps), jamais sur
  les nageoires, plumes, os d'aile, cornes ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty LAGON_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT
  (LEGS_ROOT ne porte que les pièces posées au sol : l'amphiptère n'a pas de pattes). Chaque pièce est parentée au
  bon root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne,
  penché de 10° vers l'avant).
- Tout dans une collection « LAGON_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots LAGON_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (ZB, NECK_H, NECK_LEAN, COIL_R, HEAD_SCALE, SNOUT_K, FANGS, FAN_N, FAN2_N, EAR_N, DORSAL, WING_SPAN, WING_LIFT, WING_FINGERS, WING_VEINS, TAIL_FIN, FX_N...) :
  c'est le seul bloc qui change entre Bébé, Ado et Adulte.
- Le corps (cou, descente, anneaux au sol, queue) suit UNE courbe Catmull-Rom (CTRL) rééchantillonnée à pas
  constant, avec un repère par segment (tangente, dos, côté) et un rayon par clés (RADIUS_KEYS), comme le Mirage.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur l'iris, les reflets d'eau des ailes et les gouttes, strength 1.3 au maximum. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3303) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 gouttes d'eau flottant.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes (aucune), 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, éventail de crête, losanges, ailes translucides)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
