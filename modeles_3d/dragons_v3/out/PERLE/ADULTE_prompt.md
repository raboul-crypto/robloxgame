Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Perle » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Perle = Eau, Épique, morphologie Aquatique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Perle : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes-palettes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Adulte puissant et fluide : 4 pattes-palettes bien plantées, long cou en col de cygne (NECK_L 4.2), tête haute et un peu penchée vers le bas, torse long portant une coquille, longue queue de poisson qui traîne puis remonte avec une grande caudale.
- Tête : crâne en wedge (HEAD_SCALE 1.3), museau plat et large (SNOUT_K 1.25) avec arête turquoise, mâchoire blanche distincte avec menton, ligne de bouche, 2 narines. Yeux : blanc, iris turquoise lumineux, pupille fendue noire, sourcils sévères bleu profond. 3 crocs nacrés par côté. Cornes nacrées longues vers l'arrière (HORN_L 1.4), 3 épines turquoise du front par côté, 3 nageoires de joue par côté.
- Signes distinctifs : PERLE facettée émissive (bipyramide à 8 faces) sertie sur le front : monture dorée à 6 griffes et DIADÈME de 2 épines dorées par côté avec gemmes turquoise lumineuses ; 2 très grandes nageoires-oreilles irisées (8 rayons, translucides) ; grande crête-nageoire du crâne (7 rayons, 1.6 de haut) ; COQUILLE Saint-Jacques nacrée sur le dos à deux niveaux (9 secteurs rose et lavande, 10 côtes turquoise, bord doré, perles-lueurs, charnière dorée) ; queue de poisson irisée.
- Corps : torse en segments biseautés sur une courbe Catmull-Rom (pas 0.4), blanc nacré, plaques de ventre séparées, plaque de dos turquoise, 5 rangées d'écailles turquoise en quinconce sur les flancs, plastron doré avec gemme lumineuse, crête-nageoire sur le cou (1.5 de haut), crinière de nageoires irisées (3 par segment et par côté), colliers dorés sur le cou, veines lumineuses turquoise sur le cou.
- Nageoires : à la place des ailes : 2 grandes pectorales en éventail (9 rayons, 5.2 de long, pointe au bout) vers l'extérieur et l'arrière, 2 pelviennes (4 rayons) sur les hanches. Membranes translucides irisées turquoise, lavande et rose en alternance. Perle-lueur au bout de chaque rayon.
- Pattes : 4 pattes-palettes turquoise épaisses (0.85) : épaule et cuisse en wedge, jambe, genouillère dorée, bracelet doré, nageoire de coude à 3 rayons, grand pied plat, 3 doigts palmés + 3 griffes nacrées.
- Queue : queue de poisson de 6.8 de long (pas 0.4) : segments qui s'affinent et s'aplatissent, dos turquoise, ventre blanc, écailles, veines lumineuses, crête-nageoire continue, 2 paires de nageoires latérales, collier doré, nageoire caudale en V (2 lobes de 7 rayons, 3.0 de long) avec perles-lueurs.
- Rendu de rareté : Épique au complet : silhouette spectaculaire (nageoires-oreilles, crête, coquille), éléments émissifs (perle du front, gemmes, perles-lueurs au bout de toutes les nageoires et de la coquille, veines, iris), ornements dorés (monture, diadème, plastron, genouillères, bracelets, colliers, bord de la coquille). 14 bulles et petites perles facettées flottent autour du dragon.
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
- Budget : 13000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les nageoires, rayons, griffes, écailles, coquille, perles
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PERLE_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « PERLE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots PERLE_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, NECK_RISE, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, EAR_RAYS, PEC_SPAN, PEC_RAYS, TAIL_L, CAUDAL_L, ORN, PEARL_R, SHELL_RIBS, BEAD_R, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur la perle, les gemmes, les perles-lueurs, les veines, les iris et les perles flottantes (strength 2 à 2.5). Les nageoires sont translucides (alpha 0.85). L'or est métallique. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3309) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 bulles et perles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, perle, coquille, nageoires, queue en V, pattes-palettes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
