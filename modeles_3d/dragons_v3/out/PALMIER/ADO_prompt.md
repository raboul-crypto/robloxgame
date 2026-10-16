Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Palmier » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Ado Palmier » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Palmier = Plante, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de l'Ado Palmier : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : ado élancé, debout sur 4 pattes plus longues, cou de 4 maillons incliné vers l'avant, tête un peu plus petite par rapport au corps, grandes ailes, queue plus longue.
- Tête : crâne en wedge, museau allongé avec arête claire, mâchoire beige et ligne de bouche, 2 narines noires, bande brune sur le museau. Yeux latéraux plus sérieux : blanc, iris ambre, pupille fendue, sourcils vert foncé. 2 petits crocs crème par côté, oreille-folioles et 1 feuille de joue par côté.
- Signe distinctif : la CRINIÈRE DE PALMES : 6 longues palmes en éventail (nervure en 2 barres qui retombe, 3 paires de folioles). Entre elles, 2 cornes brunes recourbées à pointe crème.
- Corps : torse en 3 blocs, plastron beige à 2 bandes brunes, 5 plaques de ventre beige séparées par des bandes brunes, 4 bandes brunes sur le dos, 8 écailles-feuilles sur les flancs (2 rangées de 4), crête de 5 éclats, 3 feuilles d'épaule par côté. Cou de 4 maillons : segment vert + plaque beige dessous + bande brune à chaque joint + éclats latéraux.
- Ailes : ailes faites de 3 palmes en éventail (nervure verte, 4 paires de folioles) sur un bras et un avant-bras verts, membrane de raccord, griffe au poignet.
- Pattes : 4 pattes : épaule et cuisse en wedge, tibia, bracelet beige à anneau brun, pied plat, 3 doigts + 3 griffes crème, 1 feuille sur chaque cuisse.
- Queue : 7 segments beige avec bande brune à chaque joint et bande dorsale verte, crête d'éclats, terminée par 2 noix de coco brunes à calotte fibreuse et une petite touffe de 3 palmes.
- Rendu de rareté : Commun, à mi-puissance : aucune émission, 3 familles de couleurs, ventre et queue en tronc annelé, 3 palmes flottent autour du dragon.
- Palette (hex, Principled BSDF mats, aucune émission) :
  Body #5FB02E (corps), BodyScale #4A9526 (écailles, dessus des pattes), BodyDark #2F5A1A (sourcils, bouche),
  FrondLight #86D03F / FrondMid #5FB02E / FrondDark #3F8326 (palmes : crinière, ailes, crête),
  Belly #E3C593 (ventre en plaques, anneaux de tronc, menton), TrunkRing #8A5E30 (bandes brunes de tronc),
  Horn #7A4A28 (cornes), Coconut #6B4226 et CoconutCap #47291A (noix de coco), Claw #F4ECD8 (griffes, crocs, pointes de corne),
  WingBone #4A7F2E (bras d'aile, nervures des palmes), EyeWhite #F4F4EA, Iris #D8902C (ambre), Black #0B0F08 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les palmes sont des nervures en barres avec des folioles triangulaires plates.

CONTRAINTES TECHNIQUES
- Budget : 4500 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de queue), jamais sur les petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PALMIER_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « PALMIER_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots PALMIER_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 3 palmes flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   la description et corrige les écarts visibles (couleurs, taille de la tête, ailes, détails)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
