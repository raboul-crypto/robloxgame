Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Magma » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Magma (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Magma », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Magma = Feu, Épique, Équilibré, morphologie Hydre ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Magma : pose, proportions, chaque
élément de la tête, du corps, des pattes, des ailes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : dragon hydre à DEUX têtes sur des cous en courbe (4 maillons chacun), debout sur 4 pattes, torse plus long et plus musclé que le Bébé, petites ailes dans le dos, queue qui traîne.
- Têtes : la principale (échelle 1, décalée de 0.7 et tournée de 8 degrés) et la seconde plus petite (0.78, tournée de -20 degrés vers l'extérieur) ; chacune a un crâne carré en roche noire fissurée, un museau (1.25), une mâchoire entrouverte (4 degrés) avec 2 crocs crème par côté, yeux à pupille fendue avec iris orange lumineux, sourcils sévères (16 degrés), 2 grandes cornes de roche à pointe de lave, 3 pics sur le crâne, 2 pics de joue par côté, 1 fissure par côté, 3 flammes.
- Corps : torse et bassin en roche noire en plaques fissurées (BODY_CELL 0.8), quelques plaques encore chaudes rouge-orange, cous en blocs de lave lumineux devant et plaques de roche derrière avec un pic de nuque par maillon, 4 plaques de ventre orange, plastron orange à bord doré avec une gemme de lave, 5 plaques de crête dorsale, 3 fissures par flanc.
- Pattes : 4 pattes (LEG_H 1.9), épaule et cuisse en wedge, tibia en roche fissurée, bracelet sombre à bord doré avec petite gemme, pied, 3 doigts + 3 griffes d'obsidienne, 1 pic par cuisse.
- Ailes : 2 petites ailes d'hydre (envergure 3.6 chacune), bras de roche sombre, 3 doigts, membrane orange-rouge, 1 veine de lave.
- Queue : longue (4.2), segments de roche séparés par des anneaux de lave, ventre orange, crête de pics, fissures sur les côtés, bout en grappe de 3 pics de roche autour d'un cristal de lave.
- Rendu de rareté (Épique, mi-puissance) : fissures et cœur de lave émissifs (GLOW_STR 2.4), pointes rougeoyantes sur les pics et cornes, flammes sur les têtes, ornements dorés (plastron, bracelets, gemmes), 10 braises et éclats de roche flottants.
- Palette (hex, Principled BSDF) : Rock #2B2320 (roche noire), RockDark #1A1513 (strates, sourcils), RockWarm #3D2A22,
  LavaSkin #F2661B et LavaDeep #D9471E (peau de lave, cornes, plaques chaudes), Belly #F28C1E (ventre, gorges, plastron),
  Membrane #E0521B (ailes), Fang #FFE6B8 (crocs), Claw #4A3C38 (griffes en obsidienne), Gold #F2B233 (métal 0.9, ornements),
  EyeWhite #F2F2F2, Black #0A0A0A (pupilles, narines).
  Émissifs : LavaGlow #FFA41E (fissures), LavaCore #FFC233 (cœur de lave, gemmes), Flame #FFD24A et FlameRed #FF5A12
  (flammes), Iris #FF8A12 (yeux), tous à la puissance GLOW_STR du stade.
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 8,500 triangles maximum après modificateurs (le script en fait environ 8,472, vise 80-95 %). Biseau à 1 segment au plus,
  et seulement sur les gros blocs (têtes, torse, bassin, cuisses, pieds), jamais sur les pics, flammes, griffes ou petites pièces.
  Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MAGMA_ADO_MASTER_ROOT avec 6 enfants HEAD_ROOT, HEAD2_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT. Chaque pièce est parentée au bon root.
  Les pièces de chaque tête sont placées en coordonnées locales de son root de tête (placé en haut du cou, légèrement penché vers l'avant).
- Tout dans une collection « MAGMA_ADO ». Le script est relançable : au début, il supprime uniquement les objets de cette
  collection et les enfants des roots MAGMA_ADO_*. Il ne touche jamais aux autres stades (Bébé, Adulte) ni aux autres
  dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment et un rayon qui varie
  le long de la courbe. Les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L...) et la liste HEADS sont des
  variables faciles à modifier dans le bloc « RÉGLAGES DU STADE » en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées en espace linéaire.
  Fissures, cœur de lave, flammes et yeux émissifs. Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (1114) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les braises et éclats de roche flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 proportions et hiérarchie, 9 têtes,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille des têtes, lueur des fissures, ailes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
