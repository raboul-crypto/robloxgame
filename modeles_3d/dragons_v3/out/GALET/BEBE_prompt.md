Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Galet » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Galet (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Galet », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Galet = Terre, Commun, Brute, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Galet : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue (pas d'ailes), et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé drake trapu et bas, 4 pattes courtes et très épaisses, énorme tête carrée (environ 35 % de la hauteur) posée presque directement sur le torse (cou de 2 petits maillons), queue courte et épaisse.
- Tête : crâne carré en wedge, museau court et large avec galet clair sur l'arête, mâchoire ocre distincte et ligne de bouche brun foncé, 2 narines noires. TRÈS GRANDS YEUX latéraux : blanc, grand iris ambre, pupille noire ronde, 2 petits reflets blancs, petit sourcil de galet plat et doux. Pas de crocs. 2 petites cornes beige courtes (base plus sombre), 3 éclats de pierre sur le crâne, 1 éclat de joue par côté, 3 galets sur le crâne.
- Signe distinctif : la CRÊTE DE GALETS : 4 éclats de pierre sur le dos, 5 galets plats sur le dos, 3 éclats sur le crâne, 2 pointes sur chaque épaule, rocher d'épaule.
- Corps : torse en 3 blocs (poitrail wedge, milieu, bassin wedge) arrondis, plastron ocre, 3 plaques de ventre ocre séparées + blocs ocre sur le bas des flancs, 2 rangées de 3 écailles de pierre par flanc, 5 taches brun foncé, cou de 2 maillons avec plaque ocre devant et éclat de nuque.
- Pattes : 4 pattes courtes et très épaisses : cuisse en wedge avec plaque ocre devant, jambe, manchette de pierre sombre, gros pied plat, 3 doigts + 3 griffes crème par patte. Pas de genouillère.
- Queue : courte et épaisse (2.6 de long, 4 segments), plaque ocre dessous, un éclat de crête par segment, rocher au bout avec 4 petites pointes.
- Rendu de rareté (Commun) : silhouette propre et lisible, 3 familles de couleurs (pierre gris-beige, ocre, beige clair), aucune émission sauf les yeux, un seul signe fort (la crête de galets et les rochers d'épaule). Détails : écailles de pierre, ventre ocre en plaques, griffes. Rendu volontairement simple. 6 galets flottent autour du bébé.
- Palette (hex, Principled BSDF) :
  Body #A39078 (corps, pierre gris-beige), Pebble #CDBB9C (galets clairs, écailles claires, bout des doigts), StoneDark #74665A (galets sombres, manchettes, genouillères sombres, sourcils),
  BodyDark #45362A (bouche, taches, narines), Ochre #F2AE24 (ventre en plaques, plastron, mâchoire, plaque de cuisse), OchreDark #D08A14 (plaques de ventre alternées, éclats ocre foncé),
  Horn #E9D7AA (cornes, pointes de la crête) / HornBase #B09A72 (base des cornes), Claw #EFE6D0 (griffes, crocs),
  EyeWhite #F4EFE2, Iris #F28A12 avec émission #FF9A1F strength 1.2 (yeux ambre, seule lueur), Black #0E0B08 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les galets sont des blocs à 6 ou 7 côtés au dessus rétréci, légèrement tournés au hasard ; les éclats sont plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les galets, éclats, cornes, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty GALET_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas de WINGS_ROOT : le Drake n'a pas d'ailes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « GALET_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots GALET_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_N, HEAD_SCALE, SNOUT_K, FANGS, HORN_L, CREST_N, BACK_PEBBLES, HEAD_SPIKES, TAIL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission, sauf les yeux ambre (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1104) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 galets flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, galets, pattes))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
