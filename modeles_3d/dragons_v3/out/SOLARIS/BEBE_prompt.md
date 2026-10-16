Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Solaris » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Solaris (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Solaris », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Solaris = Feu, Légendaire, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Solaris : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé trapu et compact, debout sur 4 pattes courtes et épaisses, torse court, cou presque inexistant (1 maillon), énorme tête carrée tenue haute, regard vers l'avant, petites ailes à demi ouvertes, queue courte qui remonte légèrement.
- Tête : crâne carré en wedge, museau court et carré avec arête en or, mâchoire crème-or distincte et ligne de bouche rouge sombre, 2 narines noires. TRÈS GRANDS yeux latéraux : blanc, grand iris ambre lumineux, pupille ronde noire, 2 petits reflets blancs. Pas de crocs, pas de sourcils. 1 aileron d'oreille doré et 1 plaque de joue dorée par côté.
- Signe distinctif (couronne de cornes-flammes et halo) : 2 petites cornes dorées en 2 barres par côté, chacune terminée par une petite flamme orange lumineuse ; couronne d'un anneau de 10 éclats-flammes dorés (or, or clair, flamme orange) derrière et au-dessus du crâne ; petit halo : anneau d'or (rayon 1.3 x la tête) + anneau jaune lumineux + 5 rayons dorés.
- Corps : torse en 3 blocs rouges, plastron crème-or, 4 plaques de ventre crème bien séparées, 2 rangées de 4 écailles rouges et orange en quinconce par flanc, crête dorée de 4 grands éclats. SOLEIL de poitrine : petit bouclier d'or, disque jaune lumineux, anneau d'or clair et 10 rayons-flammes alternés jaune et orange. 3 lames-flammes dorées en éventail sur chaque épaule (épaulière d'or simple).
- Ailes : petites ailes : bras et avant-bras dorés, 3 doigts, membrane orange lumineuse, 2 flammes au bord entre les doigts + 1 flamme au bout de chaque doigt, 2 motifs de flamme rouges par panneau de membrane, griffe de pouce dorée.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge rouge, tibia rouge-orange, bracelet d'or clair, pied rouge plat, 3 doigts dorés + 3 griffes dorées par patte. Pas de genouillère ni d'armure.
- Queue : courte (5 segments environ), plaques crème dessous, 1 éclat de crête doré/orange par segment, anneau d'or au bout puis petite gerbe de 3 flammes (jaune, orange, or) autour d'une orbe jaune lumineuse.
- Rendu de rareté : Légendaire en version discrète : or métallique sur les cornes, la crête, les griffes, les bracelets et l'épaulière ; soleil de poitrine et petit halo ; yeux, flammes, soleil et queue ÉMISSIFS (strength 2.5 à 3.5) ; membrane des ailes faiblement émissive (1.0). FX : 12 éléments flottants (braises en losange, orbes jaunes, éclats, roches volcaniques sombres) et un anneau runique au sol (anneau d'or + anneau lumineux, 8 plots).
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
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, armure d'or), jamais sur les flammes, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SOLARIS_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête (couronne et halo compris) sont placées en
  coordonnées locales de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant). Les FX flottants sont enfants du MASTER.
- Tout dans une collection « SOLARIS_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SOLARIS_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur les matériaux marqués émissifs ; l'or est métallique mais reste clair. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (2207) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 éléments flottants et l'anneau runique au sol.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, couronne, soleil)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
