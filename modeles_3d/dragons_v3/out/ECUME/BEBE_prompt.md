Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Écume » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Écume = Eau, Commun, Rapide, morphologie Aquatique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Écume : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes-palettes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Bébé aquatique trapu, assis bas sur 4 pattes-palettes courtes, énorme tête (environ 35 % de la hauteur) sur un cou très court qui monte presque droit, torse court sur une courbe Catmull-Rom, petite queue de poisson qui remonte vers l'arrière.
- Tête : crâne arrondi en wedge, museau plat et large mais court (SNOUT_K 0.72) avec arête bleu foncé, mâchoire blanche distincte avec menton, ligne de bouche bleu profond, 2 narines sur le dessus. TRÈS GRANDS YEUX sur les côtés : blanc carré, grand iris bleu lumineux, pupille noire ronde, 2 petits reflets blancs. Pas de sourcils, pas de crocs. 2 cornes-épines nacrées courtes vers l'arrière, taches d'écume sur le crâne et sur le museau.
- Signe distinctif : 2 grandes NAGEOIRES-OREILLES translucides en éventail (4 rayons bleus + membranes turquoise et nacrées) de chaque côté du crâne, plus une petite crête-nageoire de 4 rayons sur le dessus du crâne, et 4 taches d'écume blanches (hexagones) sur le torse.
- Corps : cou court + torse en segments de bloc biseautés qui suivent la courbe, plaque de dos bleu profond sur chaque segment, plaques de ventre blanches bien séparées, plastron blanc sur le poitrail, une rangée d'écailles bleues en quinconce sur les flancs, petite crête-nageoire dorsale continue (hauteur 0.6).
- Nageoires : à la place des ailes : 2 petites nageoires pectorales en éventail (4 rayons, envergure 1.9) dressées sur les épaules, 2 petites pelviennes (3 rayons) sur les hanches, sans pointe au bout.
- Pattes : 4 pattes-palettes courtes et épaisses : cuisse en wedge, haut de jambe, genouillère bleu foncé, jambe, pied large et plat, 3 doigts avec membranes nacrées entre eux (pattes palmées) + 3 griffes blanches par patte. Pas de nageoire au coude.
- Queue : queue de poisson courte (3.6 de long, pas de 0.9), segments qui s'aplatissent sur les côtés vers le bout, dos bleu foncé, ventre blanc, crête-nageoire qui continue, taches d'écume, puis nageoire caudale en V : 2 lobes à 3 rayons turquoise et nacrés.
- Rendu de rareté (Commun) : silhouette propre et lisible, 3 familles de couleurs (bleu, blanc, turquoise), aucune émission sauf la lueur faible de l'iris, un seul signe fort (les nageoires-oreilles). Détails : écailles, ventre en plaques, griffes, crête-nageoire simple. Rendu volontairement simple à ce stade. 2 bulles d'eau translucides flottent autour du bébé.
- Palette (hex, Principled BSDF) :
  Body #3FA0E0 (corps bleu eau), BodyScale #2879C2 (plaques du dos, écailles, genouillères, doigts, épines du front), BodyDark #1B4C84 (sourcils, ligne de bouche),
  Belly #F2F6F8 (ventre en plaques, plastron, mâchoire, menton), Foam #FFFFFF (taches d'écume hexagonales),
  Fin #36D6CF (membranes turquoise, alpha 0.85) / FinLight #A6EEF4 (membranes nacrées, alpha 0.85) / FinRay #1E8CC8 (rayons des nageoires),
  Horn #CDEFF6 (cornes-épines nacrées), Claw #F2F6F8 (griffes, crocs), EyeWhite #F4F8FA, Iris #1E86E0 avec émission #3FB8FF strength 1.2 (seule lueur),
  Black #0A0F14 (pupilles), Nostril #123A5C (narines), Bubble #D6F6FF (bulles flottantes, alpha 0.55).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les nageoires sont des plaques en éventail à rayons, les écailles et taches d'écume sont des pièces plates.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les nageoires, rayons, griffes, écailles, taches d'écume
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty ECUME_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « ECUME_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots ECUME_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, NECK_RISE, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, EAR_RAYS, PEC_SPAN, PEC_RAYS, TAIL_L, CAUDAL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Seule émission : la lueur faible de l'iris (rareté Commun). Les nageoires sont translucides (alpha 0.85). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1117) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 2 bulles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, nageoires, queue en V, pattes-palettes))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
