Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Mottin » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Mottin (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Mottin », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Mottin = Terre, Commun, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Mottin : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue (pas d'ailes), et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé drake trapu comme un petit rocher, assis bas sur 4 pattes courtes et épaisses, énorme tête carrée (environ 35 % de la hauteur) presque posée sur le torse (cou d'un seul maillon), queue courte avec une petite massue.
- Tête : crâne carré en wedge, museau court, plat et large avec plaque plus foncée et arête de roche sur le dessus, mâchoire crème distincte avec menton, ligne de bouche brun foncé, 2 narines noires. TRÈS GRANDS YEUX latéraux : blanc, grand iris orange ambre, pupille noire ronde, 2 petits reflets blancs. Pas de sourcils, pas de crocs. 3 petites cornes plates beige par côté en éventail vers l'arrière, 1 roche entre les cornes, 1 roche de joue par côté.
- Signe distinctif : ARMURE DE ROCHES en petit : 4 petites plaques de roche taillée le long de l'échine, 1 roche sur chaque épaule, et une petite massue de 3 roches + noyau au bout de la queue.
- Corps : torse en 3 blocs (poitrail wedge, milieu, bassin wedge) arrondis, plastron crème, 4 plaques de ventre crème bien séparées, 4 galets en une rangée par flanc, cou d'un maillon avec plaque crème devant.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge ocre, jambe, bracelet de roche, 1 galet sur la cuisse, gros pied plat crème-ocre, 3 doigts ocre foncé + 3 griffes crème par patte. Pas de genouillère ni de gantelet, pas de fissures.
- Queue : courte et épaisse (2.6 de long), plaques crème dessous, massue : noyau de roche avec dessus clair + 3 roches agglomérées, sans pointes.
- Rendu de rareté (Commun) : silhouette propre et lisible, 3 familles de couleurs (ocre doré, crème, pierre brun-gris) + beige des cornes, un seul signe fort (l'armure de roches et la massue). Aucune émission à ce stade. Rendu volontairement simple. 4 éclats de roche en losange flottent autour du bébé.
- Palette (hex, Principled BSDF) :
  Body #E0983C (corps ocre doré), BodyScale #C27A2C (dessus du museau, doigts, galets ocre), BodyDark #5E3A1C (bouche),
  Rock #7A6350 / RockDark #4B3C30 / RockLight #A08467 (roches, plaques d'armure, barbe, sourcils), Belly #F3D58C (ventre, plastron, mâchoire),
  Foot #E8BE6A (pieds), Horn #D9B677 (cornes, pointes de la massue), Claw #F6EBCB (griffes, crocs),
  EyeWhite #F6F3EA, Iris #D9741C (iris orange ambre, sans émission), Black #0E0A07 (pupilles, narines), Lava #FFA21F émission #FF7A10 strength 1.8 (fissures, adulte seulement).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les roches sont des blocs au dessus rétréci, légèrement tournés au hasard.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, noyau de la massue), jamais sur les roches, griffes, cornes, éclats
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MOTTIN_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas de WINGS_ROOT : le Drake n'a pas d'ailes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « MOTTIN_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots MOTTIN_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, SNOUT_K, FANGS, HORN_N, CREST_N, SHOULDER_ROCKS, TAIL_L, CLUB_SIZE, CRACKS, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun) sauf les fissures de lave de l'adulte. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1102) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 éclats de roche flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, roches, massue))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
