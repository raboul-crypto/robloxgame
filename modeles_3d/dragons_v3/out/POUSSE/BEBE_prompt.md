Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Pousse » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Pousse (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Pousse », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Pousse = Plante, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Pousse : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé trapu, assis bas sur ses 4 pattes courtes et épaisses, tête énorme (environ 35 % de la hauteur) posée presque directement sur le torse (cou de 2 petits maillons), petites ailes à demi ouvertes, queue courte qui remonte à peine.
- Tête : crâne carré en wedge, museau court et carré avec une arête de museau vert clair, mâchoire crème distincte et ligne de bouche vert foncé, 2 narines noires sur le dessus du museau. TRÈS GRANDS YEUX sur les côtés du crâne : blanc carré, grand iris vert vif, pupille noire ronde, 2 petits reflets blancs. Pas de sourcils, pas de crocs. Oreilles en feuille lime, 1 feuille de joue par côté, collerette de 8 feuilles (losanges) derrière le crâne.
- Signe distinctif : LA POUSSE : une tige brune courte plantée au sommet du crâne avec 2 feuilles lime vif en losange qui s'ouvrent vers l'extérieur, entre 2 petites cornes beige recourbées vers l'arrière (2 barres qui s'affinent).
- Corps : torse en 3 blocs (poitrail wedge, milieu, bassin wedge) très arrondis (biseau généreux), plastron crème sur le poitrail, 4 plaques de ventre crème bien séparées, 4 écailles-feuilles par flanc, 3 taches vert foncé, crête simple de 4 feuilles, 2 petites feuilles d'épaule par côté, cou court de 2 maillons avec une plaque crème devant.
- Ailes : petites ailes : 2 os verts (bras, avant-bras) + 2 doigts, membrane lime tendue entre eux, petites pointes crème au bout des doigts et au poignet.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge, tibia, bracelet d'écorce brun, gros pied plat, 3 doigts + 3 griffes crème par patte. Pas de lianes.
- Queue : courte et épaisse (6 segments), plaques crème dessous, une feuille de crête par segment, anneau d'écorce puis 2 feuilles croisées (lime clair et moyen) au bout.
- Rendu de rareté : Commun : rendu volontairement simple. 3 familles de couleurs (vert, crème, brun), aucune émission, un seul signe fort (la pousse) bien dessiné. 4 petites feuilles flottantes autour du bébé.
- Palette (hex, Principled BSDF mats, aucune émission) :
  Body #78BE3C (corps), BodyScale #5FA832 (écailles, dessus des pattes), BodyDark #2F6E22 (sourcils, bouche, taches),
  LeafLight #A6E05A / LeafMid #68B534 / LeafDark #3B8A28 (feuilles : pousse, crinière, crête),
  Belly #EFE3B6 (ventre en plaques, plastron, mâchoire), Horn #DDC79A (cornes / bois), Bark #7E5430 et BarkDark #51351D
  (tronc, bracelets d'écorce), Claw #F6EEDA (griffes, crocs, pointes d'aile), Membrane #8DC947 (membrane des ailes),
  WingBone #3F8626 (os des ailes), EyeWhite #F4F4EA, Iris #7FE03A, Black #0B0F08 (pupilles, narines), Gem #B6F06E (pierre).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles sont des losanges plats ou des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les feuilles, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty POUSSE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « POUSSE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots POUSSE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
