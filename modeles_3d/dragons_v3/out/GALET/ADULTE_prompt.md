Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Galet » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Galet (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Galet », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Galet = Terre, Commun, Brute, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Galet : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue (pas d'ailes), et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte drake massif et bas, debout sur 4 énormes pattes, corps large, cou puissant de 4 maillons qui monte en avant, tête haute regardant vers l'avant et un peu vers le bas, queue épaisse qui descend puis remonte légèrement. Pas d'ailes.
- Tête : crâne carré en wedge, museau large avec galet clair sur l'arête, mâchoire ocre distincte, ligne de bouche brun foncé, 2 narines noires. Yeux latéraux : blanc, iris ambre, pupille fendue noire, sourcils sévères en galet plat avec un petit galet dessus. 3 crocs crème par côté + 2 dents du bas. 2 grandes cornes beige (base plus sombre) vers le haut et l'arrière, 2 cornes latérales courtes + 1 corne de mâchoire par côté, 8 éclats de pierre en crête sur le crâne, 7 galets sur le crâne, 3 éclats de joue par côté.
- Signe distinctif : la CRÊTE DE GALETS sur la tête, le dos et la queue (8 éclats de crête dorsale, 20 galets plats sur le dos) et les ÉNORMES ROCHERS aux épaules (4 pointes par épaule) et aux hanches.
- Corps : torse en 3 blocs (poitrail wedge, milieu, bassin wedge), plastron ocre, 6 plaques de ventre ocre bien séparées + blocs ocre sur le bas des flancs, 4 rangées de 5 écailles de pierre en quinconce par flanc, 9 taches brun foncé, cou de 4 maillons : bloc gris-beige + plaque ocre devant + éclat de crête + galets sur les côtés.
- Pattes : 4 pattes énormes : cuisse en wedge avec plaque ocre devant, jambe, manchette de pierre sombre, genouillère et coudière de gros galets avec une pointe, pied plat, 3 doigts beige clair + 3 griffes crème par patte.
- Queue : 5.8 de long, segments de plus en plus fins, plaques ocre dessous, éclat de crête sur chaque segment, écailles de pierre sur les côtés, gros rocher au bout avec 4 pointes beige.
- Rendu de rareté (Commun) : silhouette propre et lisible, 3 familles de couleurs (pierre gris-beige, ocre, beige clair), aucune émission sauf les yeux, un seul signe fort (la crête de galets et les rochers d'épaule). Détails : écailles de pierre, ventre ocre en plaques, griffes. 12 galets et éclats ocre flottent autour du dragon.
- Palette (hex, Principled BSDF) :
  Body #A39078 (corps, pierre gris-beige), Pebble #CDBB9C (galets clairs, écailles claires, bout des doigts), StoneDark #74665A (galets sombres, manchettes, genouillères sombres, sourcils),
  BodyDark #45362A (bouche, taches, narines), Ochre #F2AE24 (ventre en plaques, plastron, mâchoire, plaque de cuisse), OchreDark #D08A14 (plaques de ventre alternées, éclats ocre foncé),
  Horn #E9D7AA (cornes, pointes de la crête) / HornBase #B09A72 (base des cornes), Claw #EFE6D0 (griffes, crocs),
  EyeWhite #F4EFE2, Iris #F28A12 avec émission #FF9A1F strength 1.2 (yeux ambre, seule lueur), Black #0E0B08 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les galets sont des blocs à 6 ou 7 côtés au dessus rétréci, légèrement tournés au hasard ; les éclats sont plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les galets, éclats, cornes, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty GALET_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas de WINGS_ROOT : le Drake n'a pas d'ailes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « GALET_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots GALET_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_N, HEAD_SCALE, SNOUT_K, FANGS, HORN_L, CREST_N, BACK_PEBBLES, HEAD_SPIKES, TAIL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission, sauf les yeux ambre (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1104) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 galets et éclats flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, galets, pattes))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
