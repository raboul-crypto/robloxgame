Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Braisillon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Braisillon (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Braisillon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Braisillon = Feu, Commun, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Braisillon : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte wyvern puissant et penché de 14 degrés vers l'avant, 2 pattes arrière hautes (LEG_H 3.5), cou de 5 maillons en S, grosse tête (HEAD_SCALE 1.25) regardant vers l'avant, ailes-bras dont le poignet est près du sol (1.2), longue queue de 6.8.
- Tête : crâne carré en wedge, long museau avec arête orange, mâchoire dorée distincte et ligne de bouche, narines noires. Yeux : blanc, iris orangé lumineux, pupille fendue noire, sourcils sévères de basalte. 3 crocs claires par côté, 3 pointes de joue et 3 braises de joue par côté, grandes cornes de basalte recourbées.
- Signe distinctif : couronne de 3 grandes flammes sur le crâne et crinière de flammes sur 2 anneaux (12 flammes à l'extérieur, taille 1.2) dégradé orange, jaune, cœur clair. Armure de basalte noir (2 teintes) parcourue de fissures de lave lumineuses.
- Corps : torse en blocs, plastron et 6 plaques de ventre dorées plus plaques dorées sur les flancs bas, 2 rangées de 4 écailles par flanc, 7 plaques de basalte sur le dos, 4 blocs de basalte par flanc, basalte sur le cou, 3 pointes d'épaulière par côté, 12 braises lumineuses.
- Ailes : grandes ailes-bras orange : 2 os rouge sombre épais (0.32), 3 doigts, membrane orange avec facettes jaunes (MembraneHot), pointes de basalte au bout des doigts et au poignet, envergure 7.2.
- Pattes : 2 pattes arrière : cuisse en wedge avec plaque de basalte et 3 braises, genou de basalte, tibia et protection de basalte avec fissures, pied plat biseauté, 3 doigts + 3 griffes claires.
- Queue : 6.8 de long, écailles sur les côtés, 4 segments biseautés, terminée par un bouquet de 7 flammes de 3.2 de haut.
- Rendu de rareté : Commun poussé au maximum : armure de basalte, fissures de lave et braises faiblement émissives (strength 1.5), yeux émissifs (2.0), ventre et plastron dorés. 12 braises flottent autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #DC4A22 (corps rouge braise), BodyScale #B93A1E (écailles, dessus des pattes, orteils), BodyDark #7E2616 (bouche, ombres, os d'aile),
  Basalt #2B2522 (plaques, cornes, sourcils), BasaltLight #4A403A (basalte clair en alternance), Belly #F2B650 (ventre en plaques, plastron, menton dorés),
  FlameOrange #F2711C / FlameYellow #FFB52E / FlameHot #FFD65A (flammes), Lava #FF9A1F (braises et fissures, émission orange 1.5),
  Claw #E8DCC0 (griffes, crocs), Membrane #F07A1E (membrane des ailes), MembraneHot #FFA630 (facettes claires), EyeWhite #F4EEDD,
  Iris #FFB52E (émission 2.0), Black #120B08 (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Le basalte est fait de blocs sombres, les flammes sont des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRAISILLON_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRAISILLON_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRAISILLON_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (LEAN, BW, BH, TORSO_L, LEG_H, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, WRIST_Z, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Commun : seules quelques braises, les fissures de lave (Lava, strength 1.5) et les iris (strength 2.0) sont émissifs, rien d'autre. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1109) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
