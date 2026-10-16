Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Mottin » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Mottin (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Mottin », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Mottin = Terre, Commun, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Mottin : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Drake massif comme un rocher vivant, debout sur 4 grosses pattes, corps large et bas, cou vertical de 5 maillons, tête haute regardant vers l'avant et un peu vers le bas (6°), queue épaisse qui descend vers le sol puis se termine par une grosse massue. Pas d'ailes.
- Tête : crâne carré en wedge, grand museau plat et large avec plaque plus foncée sur le dessus et arête de roche, mâchoire crème distincte avec menton, ligne de bouche brun foncé, 2 narines noires sur le dessus du museau. Yeux latéraux : blanc, iris orange ambre, pupille fendue noire, sourcils de roche sévères. 3 crocs crème par côté qui descendent de la mâchoire.
- Cornes et roches de tête : 5 cornes plates beige par côté qui s'ouvrent en éventail vers l'arrière et vers l'extérieur (les plus longues au centre), 1 corne de joue par côté vers l'arrière, 3 roches entre les cornes, 3 roches sur chaque joue, une barbe de 4 roches sous la mâchoire.
- Signe distinctif : ARMURE DE ROCHES : 6 grosses plaques de roche taillée le long de l'échine, chacune avec une petite pierre posée dessus, 4 grosses roches empilées sur chaque épaule, roches de nuque et roches latérales sur le cou, et une massue de roches au bout de la queue.
- Corps : torse en 3 blocs (poitrail en wedge, milieu, bassin en wedge), plastron crème, 6 plaques de ventre crème bien séparées + bandes crème sur le bas des flancs, 15 galets taillés en quinconce par flanc (3 rangées de 5, brun-gris, clair et ocre foncé).
- Pattes : 4 pattes énormes : cuisse en wedge ocre, jambe en gantelet de pierre sombre, bracelet de roche avec anneau clair en haut, genouillère de roche à l'avant, 3 galets sur la cuisse, pied plat crème-ocre, 3 doigts ocre foncé + 3 griffes crème par patte.
- Fissures de lave : petites fissures orange en zigzag (avec une branche) sur les flancs (3 par côté), sur les gantelets (2 sur le côté + 1 devant) et sur les côtés de la massue. Elles restent collées à la surface.
- Queue : 6 à 7 segments ocre qui s'affinent, plaques crème dessous, une plaque de roche un segment sur deux sur le dessus, pierres sur les côtés, puis la massue : gros noyau de roche, dessus clair, 6 roches agglomérées autour et 4 pointes beige.
- Rendu de rareté (Commun) : silhouette propre et lisible, 3 familles de couleurs (ocre doré, crème, pierre brun-gris) + beige des cornes, un seul signe fort (l'armure de roches et la massue). Comme sur l'image, seules les fissures de lave sont émissives, en accent faible (strength 1.8). 12 éclats de roche en losange flottent autour du dragon.
- Palette (hex, Principled BSDF) :
  Body #E0983C (corps ocre doré), BodyScale #C27A2C (dessus du museau, doigts, galets ocre), BodyDark #5E3A1C (bouche),
  Rock #7A6350 / RockDark #4B3C30 / RockLight #A08467 (roches, gantelets, barbe), Belly #F3D58C (ventre, plastron, mâchoire),
  Foot #E8BE6A (pieds), Horn #D9B677 (cornes, pointes de la massue), Claw #F6EBCB (griffes, crocs),
  EyeWhite #F6F3EA, Iris #D9741C, Black #0E0A07 (pupilles, narines), Lava #FFA21F émission #FF7A10 (fissures).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les roches sont des blocs au dessus rétréci, légèrement tournés au hasard.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, noyau de la massue), jamais sur
  les roches, griffes, fissures ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MOTTIN_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT : le Drake n'a pas d'ailes). Chaque pièce est parentée au bon root. Les pièces de la
  tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne, penché de 6° vers l'avant).
- Tout dans une collection « MOTTIN_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots MOTTIN_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE,
  SNOUT_K, FANGS, HORN_N, CREST_N, SHOULDER_ROCKS, TAIL_L, CLUB_SIZE, CRACKS, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Seule émission : la lave des fissures. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1102) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 éclats de roche flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, roches, pattes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
