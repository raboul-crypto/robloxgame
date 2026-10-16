Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Solaris » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Solaris (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Solaris », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Solaris = Feu, Légendaire, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Solaris : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Ado plus élancé et musclé, debout sur 4 pattes, torse allongé, cou vertical de 5 maillons, tête plus petite et museau plus long que le bébé, regard vers l'avant, ailes ouvertes vers le haut et l'arrière, queue longue qui traîne puis remonte.
- Tête : crâne carré en wedge, museau avec arête en or, mâchoire crème-or et ligne de bouche, 2 narines noires. Yeux latéraux : blanc, iris ambre lumineux, pupille fendue noire, sourcils dorés sévères. 2 crocs crème par côté. Aileron d'oreille doré, 2 plaques de joue dorées par côté, plaques de joue d'armure et plaque frontale d'or avec un rubis lumineux, barbe de 3 flammes dorées sous le menton.
- Signe distinctif (couronne de cornes-flammes et halo) : 2 cornes dorées recourbées par côté (3 barres + 1 dent), chacune terminée par une flamme lumineuse (orange et jaune) ; couronne d'un anneau de 9 éclats-flammes dorés derrière et au-dessus du crâne ; halo de soleil : anneau d'or (rayon 1.7 x la tête) + anneau jaune lumineux + 7 rayons en éclats.
- Corps : torse en 3 blocs rouges, plastron crème-or, 5 plaques de ventre crème séparées par des filets d'or + bandes crème sur les flancs bas, 2 rangées de 6 écailles rouges / orange / dorées par flanc, gorgerin d'or à la base du cou. Cou : segment rouge + plaque crème + filet d'or + 2 flammes de nuque par maillon, flammes dorées sur les côtés. Crête dorsale DOUBLE : 5 grands éclats au centre + 2 rangées latérales plus petites, 2 plaques d'armure dorées sur le dos. SOLEIL de poitrine : bouclier d'or, disque jaune lumineux, anneau d'or clair, 10 rayons-flammes. Épaulières d'or avec emblème rouge en cœur sur fond d'or clair et 4 lames-flammes en éventail ; plaques de hanche et de côte en or.
- Ailes : grandes ailes : armature dorée (bras, avant-bras, 3 doigts), membrane orange lumineuse, flammes au bord (1 par doigt + 2 entre les doigts), 3 paires de motifs de flamme rouges par panneau, pique d'or au poignet.
- Pattes : 4 pattes : cuisse en wedge rouge avec plaque d'or extérieure, genouillère d'or, jambière d'or (tibia métallique), bracelets d'or clair en haut et en bas, 2 flammes lumineuses sur la jambière, pied rouge plat, 3 doigts dorés + 3 griffes dorées.
- Queue : longue (7 segments environ), plaques crème dessous, bandes d'or tous les 3 segments, 1 éclat de crête doré par segment, écailles rouges / orange sur les côtés, anneau d'or puis gerbe de 5 flammes (jaune, orange, or) autour d'une orbe jaune lumineuse.
- Rendu de rareté : Légendaire à mi-puissance : armure d'or (plaque frontale, gorgerin, épaulières, genouillères, plaques de hanche et de cuisse), halo et couronne de flammes, soleil de poitrine, double crête ; yeux, flammes, soleil, rubis et queue ÉMISSIFS (2 à 3.5), membrane faiblement émissive. FX : 20 éléments flottants (braises, orbes, éclats, roches volcaniques) et un anneau runique au sol (12 plots).
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
- Budget : 10000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, armure d'or), jamais sur les flammes, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SOLARIS_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête (couronne et halo compris) sont placées en
  coordonnées locales de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant). Les FX flottants sont enfants du MASTER.
- Tout dans une collection « SOLARIS_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SOLARIS_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur les matériaux marqués émissifs ; l'or est métallique mais reste clair. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (2207) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 20 éléments flottants et l'anneau runique au sol.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, couronne, soleil)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
