Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Palmier » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Bébé Palmier » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Palmier = Plante, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de le Bébé Palmier : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : bébé trapu et rond, debout sur 4 pattes très courtes et épaisses, torse court, cou très court (2 maillons), énorme tête carrée (environ 35 % de la hauteur), petites ailes, queue courte.
- Tête : crâne carré en wedge, museau court (60 % de la longueur adulte) avec arête claire, mâchoire beige distincte, ligne de bouche, 2 narines noires, petite bande brune sur le museau. Très grands yeux latéraux : blanc, grand iris ambre, pupille ronde noire, 2 petits reflets blancs. Pas de crocs. 1 petite oreille-folioles et 1 feuille de joue par côté.
- Signe distinctif : la CRINIÈRE DE PALMES : 5 palmes en éventail derrière le crâne, chacune avec nervure verte en 2 barres qui retombe en arc et 2 paires de folioles triangulaires (2 teintes de vert). Entre elles, 2 petites cornes brunes recourbées vers l'arrière.
- Corps : torse en 3 blocs, plastron beige avec 1 bande brune, 4 plaques de ventre beige séparées par des bandes brunes (ventre en tronc de palmier), 3 bandes brunes en travers du dos, 3 écailles-feuilles par flanc, crête de 4 éclats verts, 2 petites feuilles d'épaule par côté.
- Ailes : petites ailes faites de 3 palmes en éventail (nervure verte + 2 paires de folioles), accrochées à un bras et un avant-bras verts, avec une petite membrane de raccord et une griffe au poignet.
- Pattes : 4 pattes courtes : épaule et cuisse en bloc, tibia, bracelet beige avec 1 anneau brun, pied plat, 3 doigts + 3 griffes crème.
- Queue : courte (6 segments beige) avec une bande brune à chaque joint et une bande dorsale verte, 3 éclats de crête, terminée par 2 noix de coco brunes (anneau brun de raccord).
- Rendu de rareté : Commun : silhouette propre, 3 familles de couleurs (vert, beige, brun), AUCUNE émission, un seul signe fort (la crinière de palmes) et le motif tronc (beige + bandes brunes). 2 palmes flottent autour du dragon.
- Palette (hex, Principled BSDF mats, aucune émission) :
  Body #5FB02E (corps), BodyScale #4A9526 (écailles, dessus des pattes), BodyDark #2F5A1A (sourcils, bouche),
  FrondLight #86D03F / FrondMid #5FB02E / FrondDark #3F8326 (palmes : crinière, ailes, crête),
  Belly #E3C593 (ventre en plaques, anneaux de tronc, menton), TrunkRing #8A5E30 (bandes brunes de tronc),
  Horn #7A4A28 (cornes), Coconut #6B4226 et CoconutCap #47291A (noix de coco), Claw #F4ECD8 (griffes, crocs, pointes de corne),
  WingBone #4A7F2E (bras d'aile, nervures des palmes), EyeWhite #F4F4EA, Iris #D8902C (ambre), Black #0B0F08 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les palmes sont des nervures en barres avec des folioles triangulaires plates.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de queue), jamais sur les petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PALMIER_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « PALMIER_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots PALMIER_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 2 palmes flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   la description et corrige les écarts visibles (couleurs, taille de la tête, ailes, détails)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
