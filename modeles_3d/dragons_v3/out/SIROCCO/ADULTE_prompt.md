Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Sirocco » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Sirocco (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Sirocco », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Sirocco = Feu, Rare, Voltigeur, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Sirocco : pose, proportions, chaque
élément de la tête, du corps, des ailes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : grand serpent dressé en S (cou long), anneaux posés au sol avec la queue qui remonte au centre, tête haute regardant vers l'avant et un peu vers le bas (6°), immenses ailes levées vers le haut et l'arrière. Pas de pattes.
- Tête : crâne carré en wedge rouge-orange, long museau, arête claire, plaque du front, mâchoire orange, ligne de bouche, 2 narines, 2 perles dorées. Yeux : blanc, iris doré lumineux, pupille fendue noire, sourcils bruns sévères. 3 crocs blancs par côté. Oreilles-flammes, 3 flammes de joue par côté, 4 flammes de barbe sous le menton.
- Cornes et collerette : 2 LONGUES cornes brunes recourbées vers l'arrière (4 points) avec 2 branches chacune, pointes dorées métalliques, sur des bases brunes ; 3 flammes sur le front ; grande collerette de 3 anneaux de flammes rouge / orange / jaune (12, 10 et 8) derrière le crâne.
- Signe distinctif : VOLUTES DORÉES (tourbillons de vent chaud) sur le corps, AILES AUX BORDS DÉCOUPÉS EN FLAMMES, cornes brunes recourbées vers l'arrière. Les flammes sont des losanges plats rouge, orange et jaune.
- Corps : segments rouge-orange en deux teintes alternées, anneaux sombres aux jointures, plaques de ventre orange bien séparées, plastron orange avec 7 flammes, CRÊTE DOUBLE (flammes sur un segment, petites plaques rouges sur l'autre), flammes sur les flancs (plus denses sur la poitrine), 4 flammes d'épaule par côté et plaque rouge à la base de chaque aile, jusqu'à 14 volutes dorées (spirales de barres) par côté.
- Ailes : 2 IMMENSES ailes en flammes : bras, avant-bras et 5 doigts en os rouge sombre, membrane rouge-orange, 5 couches de flammes (rouge, orange, jaune) au bout de chaque doigt, 2 rangées de flammes entre les doigts, flammes sur le bord d'attaque, griffe de pouce crème. Toutes les flammes sont posées dans le plan de l'aile.
- Queue : la queue suit la même courbe et remonte au centre des anneaux ; bout en anneau doré avec un panache de 4 grandes flammes (rouge, orange, 2 jaunes) ; 6 flammes posées au sol autour des anneaux.
- Rendu de rareté (Rare) : Rare à pleine puissance : motif secondaire (volutes dorées), cornes à 2 branches avec pointes dorées, crête double, ailes en flammes, un accent lumineux discret : iris doré et flammes jaunes émissifs avec strength 1.2. 14 braises en losange flottent autour.
- Palette (hex, Principled BSDF) :
  Body #D24A2E (corps rouge-orange), BodyDark #A02F20 (segments alternés, plaques de crête), BodyLight #E8693A (arête du museau),
  Mouth #5C1F14 (bouche, narines, jointures), Belly #F9A93A (ventre, mâchoire, plastron), Horn #6A4026 (cornes, sourcils),
  Gold #E3AA3C métallique 0.7 (volutes, pointes de corne, anneau de queue), FlameRed #DC3A1E, FlameOrange #F58A1E,
  FlameYellow #FFC93A émission #FFB02E strength 1.2, WingBone #7A1E16 (os des ailes), Membrane #F26A2C (membrane des ailes),
  Claw #F2E4C8 (crocs, griffe de pouce), EyeWhite #F4F1E8, Iris #F0B030 émission strength 1.2, Black #0C0807 (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les flammes sont des plaques fines en losange, les volutes de petites barres dorées en spirale.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du corps), jamais sur
  les flammes, os d'aile, volutes, cornes ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SIROCCO_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT
  (LEGS_ROOT ne porte que les flammes posées au sol : l'amphiptère n'a pas de pattes). Chaque pièce est parentée au
  bon root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne,
  penché de 6° vers l'avant).
- Tout dans une collection « SIROCCO_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SIROCCO_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (ZB, NECK_H, COIL_R, HEAD_SCALE, SNOUT_K, FANGS, MANE_RINGS,
  MANE_N, HORN_K, HORN_TINES, VOLUTES, WING_SPAN, WING_LIFT, WING_FINGERS, WING_FLAMES, TAIL_FLAME, FX_N...) :
  c'est le seul bloc qui change entre Bébé, Ado et Adulte.
- Le corps (cou, descente, anneaux au sol, queue) suit UNE courbe Catmull-Rom (CTRL) rééchantillonnée à pas
  constant, avec un repère par segment (tangente, dos, côté) et un rayon par clés (RADIUS_KEYS), comme le Mirage.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur l'iris et les flammes jaunes, strength 1.2. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (2202) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes (aucune), 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes en flammes, volutes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
