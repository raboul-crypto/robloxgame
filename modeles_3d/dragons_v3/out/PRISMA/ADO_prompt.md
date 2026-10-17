Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Prisma » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades du dragon Prisma (Bébé, Ado, Adulte) si tu en as une ; sinon la
   description ci-dessous fait foi. Seul l'Ado Prisma est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau « Dragons exclusifs (payants) » : Prisma = Vol, Exclusif, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Prisma (ou ce que la description impose) : pose,
proportions, chaque élément de la tête, du corps, des ailes ou ailerons, des pattes et de la queue, et la
palette. Puis liste les contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Ado nacré plus musclé, debout sur 4 pattes, cou de 5 maillons, tête plus haute, ailes ouvertes, queue qui s'allonge et remonte.
- Tête : crâne en wedge, museau avec arête de 4 bandes de couleurs, mâchoire crème distincte, ligne de bouche, narines. Yeux plus sérieux : blanc, iris bleu clair lumineux, pupille fendue, sourcils colorés. 2 petits crocs par côté. Oreilles prismatiques, 2 pointes de joue par côté.
- Signe distinctif : couleurs d'arc-en-ciel qui changent segment par segment : 11 bandes dorsales, un maillon de cou par couleur (plaque de dos colorée + cristal), une bande par maillon de queue, bracelets de pattes à 2 bagues colorées. Gemme blanche émissive au front et sur le plastron.
- Crinière et cornes : crinière de 2 rangées de 12 éclats ; 2 cornes nacrées de 4 barres avec pointes de cristal ; halo de 7 éclats derrière la tête.
- Corps : torse en 3 blocs, plastron, 5 plaques de ventre séparées + plaques de flanc, 3 rangées x 5 écailles prismatiques par flanc, crête de 6 cristaux, 4 éclats d'épaulière par côté.
- Ailes : os nacrés, 3 doigts, membrane en 4 anneaux de couleurs par secteur, pointes de cristal, perles colorées, traînée arc-en-ciel de 8 rubans.
- Pattes : 4 pattes, épaule et cuisse en wedge, tibia, bracelet coloré, pied plat, 3 doigts + 3 griffes blanches, petit cristal sur le pied arrière.
- Queue : bande colorée + plaque crème + cristal par segment, écailles sur les côtés, éventail de 7 cristaux.
- Rendu de rareté (Exclusif, mi-puissance) : tout ce qui est coloré est émissif, 34 cristaux flottants.
- Palette (hex, Principled BSDF mats) :
  Body #EEEAF8 (corps nacré), BodyScale #CFC6EC (dessus des pattes, plaques de dos), BodyDark #7F76B4 (sourcils, bouche, narines),
  Belly #FFFFFF (ventre en plaques, plastron, mâchoire), Horn #F8F6FF (cornes), Claw #FFFFFF (griffes, crocs, pointes d'aile),
  WingBone #F4F1FF (os des ailes), EyeWhite #F4F4F8, Iris #5AB8FF (émissif 3.0), Black #0A0A12, Gem #FFFFFF (émissif 3.5).
  Arc-en-ciel, 8 couleurs : #FF4D5E, #FF9A3C, #FFE14A, #4DE07A, #3FD8FF, #5A7BFF, #B070FF, #FF5FD0, en 3 versions :
  écailles et bandes (émission 1.6), cristaux vifs (émission 3.2), membranes d'aile (émission 1.1, alpha 0.8).
  La couleur change à chaque segment : fonction rb(i) = couleur numéro i modulo 8.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les éclats et les
  étoiles sont des pièces plates et pointues.

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et seulement sur les gros
  blocs (crâne, museau, torse, segments), jamais sur les éclats, griffes, étoiles ou petites pièces. Le script
  affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PRISMA_ADO_MASTER_ROOT avec ses enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT. Chaque pièce est parentée au bon
  root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne).
- Tout dans une collection « PRISMA_ADO ». Le script est relançable : au début, il supprime uniquement les objets de
  cette collection et les enfants des roots PRISMA_ADO_*. Il ne touche jamais aux autres stades ni aux autres
  dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie. Proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L...) en variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées en espace
  linéaire. Émission sur tous les motifs prismatiques (rareté Exclusif). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (7707) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 34 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec l'image (ou la description)
   et corrige les écarts visibles (couleurs, taille de la tête, ailes, motifs) avant de me le rendre.
   Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
