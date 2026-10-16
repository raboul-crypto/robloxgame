Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Pousse » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Pousse (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Pousse », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Pousse = Plante, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Pousse : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Ado élancé et plus droit, debout sur 4 pattes, cou de 4 maillons qui se lève, tête plus petite que chez le bébé regardant vers l'avant, grandes ailes ouvertes vers le haut et l'arrière, queue qui s'allonge.
- Tête : crâne wedge, museau plus long, arête de museau claire, mâchoire crème et ligne de bouche, 2 narines noires. Yeux sérieux sur les côtés : blanc, iris vert, pupille FENDUE noire, sourcils vert foncé inclinés vers le museau. 2 petits crocs crème par côté. Oreilles en feuille, 2 feuilles de joue par côté, collerette de 11 feuilles (losanges) derrière le crâne.
- Signe distinctif : LA POUSSE : tige brune de 2 barres avec 2 grandes feuilles lime vif, 2 petites feuilles plus bas et un bourgeon central, entre 2 cornes beige longues (3 barres) recourbées vers l'arrière.
- Corps : torse en 3 blocs, plastron crème, 5 plaques de ventre crème séparées + bandes crème sur le bas des flancs, 10 écailles-feuilles en quinconce par flanc (2 rangées de 5), 7 taches vert foncé, crête de 5 feuilles, 3 feuilles d'épaule par côté, cou de 4 maillons : segment vert + plaque crème devant + 2 feuilles de nuque + feuilles latérales.
- Ailes : grandes ailes : bras et avant-bras vert foncé épais, 3 doigts, membrane lime, pointes crème au bout de chaque doigt et au poignet.
- Pattes : 4 pattes plus musclées : cuisse en wedge, tibia, bracelet d'écorce brun avec anneau sombre en haut et 2 lianes vert foncé, pied plat, 3 doigts + 3 griffes crème, 1 feuille sur chaque cuisse.
- Queue : longue (7 segments), plaques crème dessous, crête de feuilles, petites écailles sur les côtés, anneau d'écorce et 2 feuilles croisées au bout.
- Rendu de rareté : Commun, à mi-puissance : pas d'émission, plus de détails que le bébé (écailles, plaques, lianes), 8 feuilles flottantes.
- Palette (hex, Principled BSDF mats, aucune émission) :
  Body #78BE3C (corps), BodyScale #5FA832 (écailles, dessus des pattes), BodyDark #2F6E22 (sourcils, bouche, taches),
  LeafLight #A6E05A / LeafMid #68B534 / LeafDark #3B8A28 (feuilles : pousse, crinière, crête),
  Belly #EFE3B6 (ventre en plaques, plastron, mâchoire), Horn #DDC79A (cornes / bois), Bark #7E5430 et BarkDark #51351D
  (tronc, bracelets d'écorce), Claw #F6EEDA (griffes, crocs, pointes d'aile), Membrane #8DC947 (membrane des ailes),
  WingBone #3F8626 (os des ailes), EyeWhite #F4F4EA, Iris #7FE03A, Black #0B0F08 (pupilles, narines), Gem #B6F06E (pierre).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles sont des losanges plats ou des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 4500 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les feuilles, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty POUSSE_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « POUSSE_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots POUSSE_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 8 feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
