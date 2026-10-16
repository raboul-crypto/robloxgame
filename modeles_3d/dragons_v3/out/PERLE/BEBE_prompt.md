Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Perle » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Perle = Eau, Épique, morphologie Aquatique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Perle : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes-palettes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Bébé compact et mignon : énorme tête (HEAD_SCALE 1.45), corps court, 4 pattes-palettes courtes et épaisses turquoise, cou très court, queue de poisson courte qui remonte, nageoires dressées vers le haut et les côtés.
- Tête : crâne en wedge très gros, museau court (SNOUT_K 0.72) plat et large avec arête turquoise, mâchoire blanche, ligne de bouche, 2 narines. Yeux latéraux très grands : blanc, grand iris turquoise lumineux, pupille ronde noire, 2 petits reflets blancs. Pas de crocs. Cornes nacrées courtes (HORN_L 0.45), 1 nageoire de joue par côté.
- Signes distinctifs : PERLE facettée (bipyramide à 8 faces, émissive) sertie sur le front dans une monture dorée à 6 griffes ; 2 grandes nageoires-oreilles irisées (5 rayons) ; crête-nageoire du crâne de 5 rayons ; coquille Saint-Jacques nacrée sur le dos (5 secteurs) ; queue de poisson irisée.
- Corps : torse en segments biseautés sur une courbe Catmull-Rom (pas 0.6), blanc nacré, plaques de ventre blanches séparées, plaque de dos turquoise, 2 rangées d'écailles turquoise sur les flancs, plastron blanc, veines lumineuses turquoise sur le cou.
- Nageoires : à la place des ailes : 2 pectorales en éventail (5 rayons, longueur 2.0) dressées vers le haut et l'extérieur, 2 pelviennes (3 rayons). Membranes translucides irisées en alternance turquoise, lavande et rose. Une petite perle-lueur au bout de chaque rayon.
- Pattes : 4 pattes-palettes turquoise (épaisseur 0.72) : épaule et cuisse en wedge, jambe, genouillère turquoise foncé, grand pied plat, 3 doigts palmés + 3 griffes nacrées. Aucun bracelet doré.
- Queue : queue de poisson de 3.6 de long qui remonte, segments qui s'affinent, dos turquoise, ventre blanc, crête-nageoire continue, veines lumineuses, nageoire caudale en V (2 lobes de 4 rayons, 1.6 de long).
- Rendu de rareté : Épique, en petit : la perle émissive et sa monture dorée, la coquille nacrée, les perles-lueurs aux bouts des nageoires et les veines lumineuses sont déjà là ; pas encore de diadème ni de bracelets. 6 bulles et perles flottent autour du bébé.
- Palette (hex, Principled BSDF) :
  Body #F4F0EA (corps blanc nacré, léger métal 0.12), BodyScale #3FBCD0 (écailles et plaques de dos turquoise), Leg #2FB0C8 (pattes turquoise), BodyDark #26799F (sourcils, ligne de bouche),
  Belly #FFFBF3 (ventre en plaques, mâchoire), Fin #5CD0E0 / FinLight #C9B8F4 / FinRose #F7CDE4 (membranes irisées en alternance, alpha 0.85), FinRay #2E8EBA (rayons des nageoires),
  Horn #FBF6EF (cornes nacrées), Claw #FBF6EF (griffes, crocs), Gold #F2BD3A (monture, diadème, plastron, genouillères, bracelets, colliers, bord de la coquille ; métal 0.85),
  Pearl #F2FBFF avec émission #8FE6FF strength 2.2 (perle facettée du front, gemmes, perles flottantes), Glow #6FF2F0 avec émission #3FE6F0 strength 2.5 (perles-lueurs, veines, gemmes du diadème),
  Shell #F8E8F0 / ShellLav #E4D8F8 (secteurs de la coquille) / ShellRib #6FCDE4 (côtes de la coquille),
  EyeWhite #F6FAFB, Iris #1A9AAA avec émission #4FE3F0 strength 2.5, Black #08101A (pupilles), Nostril #1E6A86 (narines), Bubble #DDF8FF (bulles flottantes, alpha 0.55).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les nageoires sont des plaques en éventail à rayons, les écailles et la coquille sont des plaques plates, la perle est une bipyramide à facettes.

CONTRAINTES TECHNIQUES
- Budget : 5000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les nageoires, rayons, griffes, écailles, coquille, perles
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PERLE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « PERLE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots PERLE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, NECK_RISE, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, EAR_RAYS, PEC_SPAN, PEC_RAYS, TAIL_L, CAUDAL_L, ORN, PEARL_R, SHELL_RIBS, BEAD_R, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur la perle, les gemmes, les perles-lueurs, les veines, les iris et les perles flottantes (strength 2 à 2.5). Les nageoires sont translucides (alpha 0.85). L'or est métallique. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3309) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 bulles et perles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, perle, coquille, nageoires, queue en V, pattes-palettes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
