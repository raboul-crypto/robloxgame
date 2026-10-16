Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Braisillon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Braisillon (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Braisillon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Braisillon = Feu, Commun, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Braisillon : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé wyvern trapu, debout sur 2 pattes arrière courtes et épaisses, torse penché de 8 degrés vers l'avant, énorme tête carrée (HEAD_SCALE 1.25) posée sur un cou de 2 petits maillons, petites ailes-bras qui reposent au sol (poignet à 0.7 de haut), queue courte.
- Tête : crâne carré en wedge, museau très court et carré avec arête orange, mâchoire dorée distincte et ligne de bouche, 2 narines noires. TRÈS grands yeux : blanc, grand iris orangé lumineux, pupille ronde noire, petit reflet blanc. Pas de crocs. 2 petites cornes de basalte, 1 pointe de joue et 1 braise de joue par côté.
- Signe distinctif : la couronne de flammes : 3 flammes (orange, jaune, cœur clair) sur le crâne plus un anneau de 8 petites flammes de crinière. Les braises sur les joues, le dos et les cuisses, et la flamme au bout de la queue, sont déjà là en petit.
- Corps : torse en blocs très arrondis, plastron et 4 plaques de ventre dorées bien séparées, 1 rangée de 4 écailles sur chaque flanc, 3 plaques de basalte sur le dos, 6 braises lumineuses sur le corps. Pas de fissures de lave ni d'armure de basalte sur le cou.
- Ailes : petites ailes-bras orange : 2 os rouge sombre épais (bras, avant-bras), 3 doigts, membrane orange tendue, pointes de basalte au bout des doigts et au poignet. Le poignet touche presque le sol et fait office de bras.
- Pattes : 2 pattes arrière courtes et épaisses : cuisse en wedge, tibia, pied plat, 3 doigts + 3 griffes claires, 1 braise sur la cuisse. Pas d'épaulière.
- Queue : courte (TAIL_L 3.6), sans écailles, terminée par un petit bouquet de 3 flammes de 1.5 de haut.
- Rendu de rareté : Commun, rendu discret : couleurs rouge, doré et noir, 1 signe fort (les flammes), seulement les yeux et quelques braises émissifs. 5 petites braises flottent autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #DC4A22 (corps rouge braise), BodyScale #B93A1E (écailles, dessus des pattes, orteils), BodyDark #7E2616 (bouche, ombres, os d'aile),
  Basalt #2B2522 (plaques, cornes, sourcils), BasaltLight #4A403A (basalte clair en alternance), Belly #F2B650 (ventre en plaques, plastron, menton dorés),
  FlameOrange #F2711C / FlameYellow #FFB52E / FlameHot #FFD65A (flammes), Lava #FF9A1F (braises et fissures, émission orange 1.5),
  Claw #E8DCC0 (griffes, crocs), Membrane #F07A1E (membrane des ailes), MembraneHot #FFA630 (facettes claires), EyeWhite #F4EEDD,
  Iris #FFB52E (émission 2.0), Black #120B08 (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Le basalte est fait de blocs sombres, les flammes sont des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRAISILLON_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRAISILLON_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRAISILLON_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (LEAN, BW, BH, TORSO_L, LEG_H, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, WRIST_Z, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Commun : seules quelques braises, les fissures de lave (Lava, strength 1.5) et les iris (strength 2.0) sont émissifs, rien d'autre. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1109) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 5 petites braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
