Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Solaris » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Solaris (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Solaris », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Solaris = Feu, Légendaire, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Solaris : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte majestueux et puissant, debout et droit sur 4 pattes épaisses, torse large, cou vertical de 6 maillons, tête haute regardant vers l'avant et un peu vers le bas, grandes ailes ouvertes vers le haut et l'arrière, longue queue qui traîne puis remonte.
- Tête : crâne carré en wedge, long museau carré avec arête en or, mâchoire crème-or distincte et ligne de bouche, 2 narines noires. Yeux latéraux : blanc, iris ambre lumineux, pupille fendue noire, sourcils dorés sévères. 3 crocs crème par côté. Aileron d'oreille doré, 4 plaques de joue dorées par côté + plaque de joue d'armure, plaque frontale d'or avec rubis lumineux, barbe de 7 flammes dorées sous le menton.
- Signe distinctif (couronne de cornes-flammes et halo) : 2 grands bois d'or ramifiés par côté (3 barres + 3 pointes), chaque pointe terminée par une flamme lumineuse (orange et jaune) ; COURONNE de 2 anneaux d'éclats-flammes (11 + 8) en or, or clair et flamme orange derrière et au-dessus du crâne ; grand HALO de soleil : anneau d'or épais (rayon 2.1 x la tête) + anneau jaune lumineux + 9 rayons en éclats dorés et orange.
- Corps : torse en 3 blocs rouges, plastron crème-or, 6 plaques de ventre crème séparées par des filets d'or + bandes crème sur les flancs bas, 3 rangées de 6 écailles rouges / orange / dorées par flanc, gorgerin d'or. Cou de 6 maillons : segment rouge + plaque crème + filet d'or + 4 flammes de nuque + flammes dorées latérales. Crête dorsale DOUBLE : 6 grands éclats au centre + 2 rangées latérales, 2 grandes plaques d'armure dorées sur le dos. GRAND SOLEIL de poitrine : bouclier d'or large, disque jaune lumineux, DOUBLE anneau d'or, 16 rayons-flammes alternés jaune et orange, 2 rubis lumineux. Épaulières d'or avec emblème rouge en cœur sur fond d'or clair + plaque haute + 8 lames-flammes en éventail ; plaques de hanche et de côte en or.
- Ailes : grandes ailes : armature dorée épaisse (bras, avant-bras, 3 doigts), membrane orange lumineuse, bord en flammes (1 par doigt + 5 entre les doigts), 3 paires de motifs de flamme rouges par panneau, pique d'or au poignet.
- Pattes : 4 pattes épaisses : cuisse en wedge rouge avec plaque d'or extérieure, genouillère d'or, jambière d'or métallique, bracelets d'or clair en haut et en bas, 2 flammes lumineuses sur la jambière, pied rouge plat, 3 doigts dorés + 3 griffes dorées, éperon doré derrière chaque pied.
- Queue : longue (8 segments environ), plaques crème dessous, bandes d'or tous les 3 segments, 1 éclat de crête dorée par segment, pointes dorées et écailles sur les côtés, anneau d'or puis grande gerbe de 9 flammes (jaune, orange, or) autour d'une grosse orbe jaune lumineuse : la flamme dorée finale.
- Rendu de rareté : Légendaire en entier : or métallique (metallic 0.5) en armure sur la tête, le cou, les épaules, les hanches, les cuisses, les genoux, les jambes, le dos ; couronne + halo + soleil de poitrine (aura) ; double rangée de pics ; yeux, flammes, soleil, rubis et orbe de queue ÉMISSIFS (strength 2 à 3.5), membrane faiblement émissive (1.0). FX : 64 éléments flottants (braises en losange, orbes jaunes, étincelles, roches volcaniques sombres) et un grand anneau runique au sol (anneau d'or + anneau lumineux + 16 plots).
- Palette (hex, Principled BSDF) :
  Body #D0301C (corps rouge), BodyScale #E2511F (écailles orange-rouge), Orange #F07A1E (accents), BodyDark #7E1A12 (bouche, ombres),
  Belly #F6D98A (ventre en plaques, plastron, mâchoire), Gold #FFC02E metallic 0.55 (armure, cornes, bracelets, crête),
  GoldLight #FFE070 metallic 0.5 (or clair, anneaux), Claw #FFD24A metallic 0.5 (griffes), Fang #FFF3D0 (crocs),
  Glow #FFE066 émissif 3.5 (soleil, orbes, pointes de flamme), Flame #FF8A1E émissif 3.0 (flammes), Ember #FF4A14 émissif 2.5 (braises, motifs de flamme),
  Membrane #FFC046 émissif faible 1.0 (ailes), Iris #FFB020 émissif 2.5 (yeux), EyeWhite #F6F2E6, Black #140806 (pupilles, narines),
  Gem #FF3A2A émissif 2.0 (rubis), Rock #3A1410 émissif 0.6 (roches flottantes).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les flammes sont des éclats plats et pointus ; l'armure est faite de blocs et de wedges dorés.

CONTRAINTES TECHNIQUES
- Budget : 15000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, armure d'or), jamais sur les flammes, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SOLARIS_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête (couronne et halo compris) sont placées en
  coordonnées locales de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant). Les FX flottants sont enfants du MASTER.
- Tout dans une collection « SOLARIS_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SOLARIS_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur les matériaux marqués émissifs ; l'or est métallique mais reste clair. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (2207) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 64 éléments flottants et l'anneau runique au sol.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, couronne, soleil)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
