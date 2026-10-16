Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Pousse » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Pousse (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Pousse », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Pousse = Plante, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Pousse : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte puissant et droit, debout sur 4 pattes épaisses, torse court et trapu, cou vertical de 5 maillons, tête haute regardant vers l'avant et un peu vers le bas, grandes ailes ouvertes vers le haut et l'arrière, longue queue qui traîne puis remonte.
- Tête : crâne carré en wedge, long museau carré avec arête claire, mâchoire crème distincte et ligne de bouche, 2 narines noires sur le dessus. Yeux latéraux : blanc, iris vert vif, pupille fendue noire, sourcils sévères vert foncé. 3 crocs crème par côté. Oreilles en feuille, 3 feuilles de joue par côté, collerette de 2 anneaux de feuilles (12 + 10 losanges) derrière le crâne.
- Signe distinctif : UN PETIT ARBRE pousse sur le crâne : tronc brun en 3 barres, 2 branches, cime faite de 8 cubes de feuilles (3 teintes de vert, légèrement tournés) + 2 petits cubes de feuilles au bout des branches. Il est entouré de 2 grands bois beige ramifiés (chacun : 3 barres + 3 pointes) qui montent et recourbent vers l'arrière.
- Corps : torse en 3 blocs, plastron crème, 6 plaques de ventre crème bien séparées + bandes crème sur le bas des flancs, 15 écailles-feuilles en quinconce par flanc (3 rangées de 5), 9 taches vert foncé, crête de 6 feuilles, 4 feuilles d'épaulière par côté, 2 plaques d'écorce brune sur le dos, cou de 5 maillons : segment vert + plaque crème devant + 3 feuilles de nuque + feuilles latérales.
- Ailes : grandes ailes : bras et avant-bras vert foncé épais, 3 doigts, membrane lime, grandes pointes crème au bout de chaque doigt et au poignet.
- Pattes : 4 pattes épaisses : épaule et cuisse en wedge, tibia, gros bracelet d'écorce brun avec anneau sombre en haut et 2 lianes vert foncé, pied plat, 3 doigts + 3 griffes crème par patte, 2 feuilles sur chaque cuisse, une petite pierre verte (non émissive) sur le côté du pied arrière droit.
- Queue : longue (8 segments), plaques crème dessous, une feuille de crête par segment, écailles sur les côtés, anneau d'écorce puis 2 grandes feuilles croisées (lime clair et moyen) au bout.
- Rendu de rareté : Commun : silhouette propre et lisible, 3 familles de couleurs (vert, crème, brun), AUCUNE émission, un seul signe fort (l'arbre). Détails : écailles-feuilles, ventre en plaques, griffes, crête simple. 12 feuilles en losange flottent autour du dragon.
- Palette (hex, Principled BSDF mats, aucune émission) :
  Body #78BE3C (corps), BodyScale #5FA832 (écailles, dessus des pattes), BodyDark #2F6E22 (sourcils, bouche, taches),
  LeafLight #A6E05A / LeafMid #68B534 / LeafDark #3B8A28 (feuilles : pousse, crinière, crête),
  Belly #EFE3B6 (ventre en plaques, plastron, mâchoire), Horn #DDC79A (cornes / bois), Bark #7E5430 et BarkDark #51351D
  (tronc, bracelets d'écorce), Claw #F6EEDA (griffes, crocs, pointes d'aile), Membrane #8DC947 (membrane des ailes),
  WingBone #3F8626 (os des ailes), EyeWhite #F4F4EA, Iris #7FE03A, Black #0B0F08 (pupilles, narines), Gem #B6F06E (pierre).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles sont des losanges plats ou des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les feuilles, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty POUSSE_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « POUSSE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots POUSSE_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
