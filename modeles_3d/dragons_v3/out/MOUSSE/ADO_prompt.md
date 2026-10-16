Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Mousse » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Mousse = Eau, Commun, Tank, morphologie Aquatique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Mousse : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Ado lourd et musclé, toujours bas et large comme une coque : tête carrée, cou court et épais, museau un peu plus long, regard sérieux, queue de poisson large qui remonte.
- Tête : crâne en wedge large, museau carré un peu plus long, arête sombre, grosses joues bleu clair, mâchoire crème, ligne de bouche, 2 narines, bourrelets de sourcils. Yeux latéraux plus petits : blanc, iris bleu (lueur faible), pupille fendue, sourcils obliques bleu foncé. 2 petits crocs gris par côté. 2 cornes crème courtes et épaisses, petite crête de 3 plaques crème sur le crâne.
- Signe distinctif n°1 : COLLERETTE D'ÉCUME en facettes autour du cou : 2 rangée(s) de pointes plates (11 pointes sur la première rangée, 2 de moins sur la deuxième, décalée d'un demi-pas), alternant blanc #F7F9FA et bleu glacé #CFEAF5, qui partent vers l'extérieur et l'arrière.
- Signe distinctif n°2 : BULLES TRANSLUCIDES alignées sur le dos et la queue : une bulle (bipyramide à 6 côtés) tous les 2 segments, posée sur une petite pointe d'écume crème qu'on voit à travers, avec une petite bulle satellite à côté de chaque bulle sur deux.
- Signe distinctif n°3 : nageoires-oreilles ÉPAISSES taillées en facettes : un gros aileron de requin (plaque épaisse bleu gris) avec une plaque claire plus petite posée dessus et une arête de rayon, plus une 2e facette plus petite derrière (longueur 2.0).
- Corps : torse sur une courbe Catmull-Rom (cou court et épais + torse), segments en blocs biseautés beaucoup plus larges que hauts (coque, rapport 1.3), plaque de dos bleu foncé, plaques de ventre crème bien séparées, plastron crème sur le poitrail, 2 rangée(s) de planches horizontales sur chaque flanc en alternant 3 bleus (aspect coque en bois).
- Nageoires : à la place des ailes : 2 grosses pectorales-palettes ÉPAISSES (3 gros rayons, longueur 4.0) qui tombent vers l'arrière sur les flancs comme des rames, et 2 petites pelviennes (2 rayons) sur les hanches. Membranes épaisses légèrement translucides.
- Pattes : 4 piliers épais : épaule et cuisse en wedge, jambe en 2 blocs, genouillère bleu foncé, grand pied plat, 3 doigts palmés (membrane) + 3 griffes grises par patte.
- Queue : queue de poisson large et plate de 3.8 de long : segments larges qui restent larges, dos bleu foncé, ventre crème, planches latérales, bulles sur la crête, nageoire caudale en V (2 lobes de 3 gros rayons, taille 2.8).
- Rendu de rareté (Commun) : silhouette propre et lisible, 4 familles de couleurs (bleu ardoise, crème, blanc d'écume, gris), aucune émission sauf la lueur faible de l'iris. 4 bulles translucides flottent autour du dragon.
- Palette (hex, Principled BSDF) :
  Body #6396BD (corps bleu ardoise), BodyScale #4A7BA3 (planches sombres, genouillères, doigts), BodyScaleB #8DB3D0 (planches claires, joues), BodyDark #3A5C78 (dos, sourcils, ligne de bouche),
  Belly #EDE6D3 (ventre en plaques, plastron, mâchoire), Foam #F7F9FA (collerette, pointes sous les bulles, cornes, crête) / FoamBlue #CFEAF5 (collerette, 2e rangée),
  Fin #6E93AD (nageoires épaisses) / FinLight #A9C6D8 (plaques claires) / FinRay #4A7BA3 (rayons),
  Claw #A9ADB3 (griffes, crocs), EyeWhite #F2F2F2, Iris #2A68A0 avec émission #3A8FD0 strength 1.2 (seule lueur), Black #0A0A0A (pupilles), Nostril #243745 (narines), Bubble #CFEAF5 (bulles, alpha 0.5).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les nageoires sont des plaques épaisses, les planches de coque et les pointes d'écume sont des pièces plates.

CONTRAINTES TECHNIQUES
- Budget : 4500 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, joues, torse, cuisses, pieds, premiers segments de la queue, plastron), jamais sur les nageoires, rayons, griffes, écailles
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MOUSSE_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, penché vers l'avant de 8 degrés).
- Tout dans une collection « MOUSSE_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots MOUSSE_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, RUFF_N, RUFF_ROWS, PLANK_ROWS, PEC_SPAN, TAIL_L, CAUDAL_L, BUB_R, BUB_EVERY, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Seule émission : la lueur faible de l'iris (rareté Commun). Les bulles et les membranes sont translucides (alpha 0.5 à 0.9). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4421) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 bulles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, collerette, bulles, queue en V, pattes-palettes))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
