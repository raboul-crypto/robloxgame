Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Braisillon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Braisillon (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Braisillon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Braisillon = Feu, Commun, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Braisillon : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Ado wyvern plus long et musclé, torse penché de 12 degrés, 2 pattes arrière hautes (LEG_H 2.8), cou de 4 maillons, tête un peu plus petite (HEAD_SCALE 1.1), ailes-bras dont le poignet est posé près du sol (1.0), queue de 5.6.
- Tête : crâne et museau carrés (museau plus long), arête orange, mâchoire dorée distincte, narines noires. Yeux plus sérieux : blanc, iris orangé lumineux, pupille fendue noire, sourcils de basalte. 2 crocs par côté, 2 pointes de joue, 1 braise de joue par côté, cornes de basalte recourbées.
- Signe distinctif : crinière de flammes sur 2 anneaux (8 flammes à l'extérieur) et couronne de 3 flammes, taille 0.95. Plaques de basalte noir avec fissures de lave sur le dos, le cou et les cuisses.
- Corps : torse en blocs, plastron et 5 plaques de ventre dorées, 2 rangées de 3 écailles par flanc, 5 plaques de basalte sur le dos, 3 blocs de basalte par flanc, basalte sur le cou, 2 pointes d'épaulière par côté, 6 braises lumineuses.
- Ailes : ailes-bras orange : 2 os rouge sombre (épaisseur 0.26), 3 doigts, membrane orange sans facettes, pointes de basalte au bout des doigts, envergure 5.8.
- Pattes : 2 pattes arrière : cuisse en wedge avec plaque de basalte et 2 braises, tibia, pied plat, 3 doigts + 3 griffes claires. Sans biseau sur les jambes.
- Queue : 5.6 de long, écailles sur les côtés, 1 segment biseauté, terminée par une flamme de 5 lames de 2.4 de haut.
- Rendu de rareté : Commun à mi-puissance : rouge, doré et noir, fissures de lave et braises faiblement émissives (strength 1.5), yeux émissifs. 5 braises flottantes autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #DC4A22 (corps rouge braise), BodyScale #B93A1E (écailles, dessus des pattes, orteils), BodyDark #7E2616 (bouche, ombres, os d'aile),
  Basalt #2B2522 (plaques, cornes, sourcils), BasaltLight #4A403A (basalte clair en alternance), Belly #F2B650 (ventre en plaques, plastron, menton dorés),
  FlameOrange #F2711C / FlameYellow #FFB52E / FlameHot #FFD65A (flammes), Lava #FF9A1F (braises et fissures, émission orange 1.5),
  Claw #E8DCC0 (griffes, crocs), Membrane #F07A1E (membrane des ailes), MembraneHot #FFA630 (facettes claires), EyeWhite #F4EEDD,
  Iris #FFB52E (émission 2.0), Black #120B08 (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Le basalte est fait de blocs sombres, les flammes sont des éclats plats et pointus.

CONTRAINTES TECHNIQUES
- Budget : 4500 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRAISILLON_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRAISILLON_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRAISILLON_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (LEAN, BW, BH, TORSO_L, LEG_H, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, WRIST_Z, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Commun : seules quelques braises, les fissures de lave (Lava, strength 1.5) et les iris (strength 2.0) sont émissifs, rien d'autre. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1109) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 5 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
