Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Sillon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Sillon (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Sillon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Sillon = Terre, Rare, Brute, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Sillon : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte wyvern musclée penchée de 18 degrés en avant, 2 hautes pattes arrière (LEG_H 4.6), cou de 5 maillons, tête de 1.3, ailes-bras avec poignet près du sol, longue queue de 8.0.
- Tête : crâne carré en wedge, museau avec la grande corne-SOC de charrue en pierre, mâchoire crème distincte, narines noires. Yeux : blanc, iris ambre, pupille fendue noire, sourcils sévères. 3 crocs par côté, 3 feuilles de joue, cornes beiges à 2 pointes plus corne basse, 3 plaques de masque, 4 épines de couronne.
- Signe distinctif : la corne-SOC en pierre sur le museau, la crinière d'épines brunes et de feuilles d'automne (2 anneaux, 12 à l'extérieur), la lame en soc au bout de la queue et les pelles de pierre aux poignets.
- Corps : cou à feuilles, 6 plaques de ventre crème, 3 rangées de 6 écailles-feuilles par flanc, crête double de 8 épines, 4 feuilles d'épaule et 3 de poitrail par côté, épaulières de pierre moussue, 3 fissures ambre sur le corps et 1 sur le cou.
- Ailes : grandes ailes-bras : os bruns épais (0.34), membrane brune avec 6 taches et des fissures ambre, griffes en PELLE de pierre au poignet, pointes crème. Envergure 7.5.
- Pattes : 2 pattes arrière : cuisse en wedge avec 2 feuilles, protège-tibias gris-vert moussus avec fissure ambre, pied plat, 3 doigts + 3 griffes crème.
- Queue : 8.0 de long, plaques de pierre, écailles, 4 segments biseautés, fissure ambre et lame en soc de 2.4 lumineuse au bout.
- Rendu de rareté : Rare complet : fissures ambre lumineuses sur le corps, les ailes et la queue (1.4), yeux ambre (1.2), cornes à 2 pointes, crête double, membranes tachetées. 12 feuilles flottantes.
- Palette (hex, Principled BSDF mats) :
  Body #C98A4C (corps caramel terracotta), BodyScale #A8642F (écailles, dessus des pattes), BodyDark #4A2A16 (sourcils, bouche, ombres),
  Belly #F2C987 (ventre en plaques, plastron, menton), Horn #E9D4A8 (cornes beiges), Stone #9A9486 (corne-soc, plaques de pierre), StoneDark #6E6B5C (pierre sombre),
  Greave #80905A / GreaveDark #58643C (protège-tibias gris-vert moussus), Crest #8A4A22 (épines brunes),
  LeafAmber #F6B73C / LeafOrange #E0761F / LeafOchre #C48A2A / LeafOlive #8C9238 (feuilles d'automne),
  Membrane #A65A33 (membrane), MembraneSpot #7E4127 (taches), WingBone #6A3B22 (os d'aile), Claw #F4EAD2 (griffes, crocs, pointes),
  EyeWhite #F6F0DE, Iris #F7A81C (émission 1.2), Black #120A06 (pupilles), Glow #FFB02E (fissures ambre, émission 1.4).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles d'automne sont des losanges plats, les épines des éclats pointus.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SILLON_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « SILLON_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SILLON_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (PITCH, BW, BH, TL, LEG_H, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, TAIL_L, TAIL_BLADE...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Rare : un accent lumineux discret seulement, les fissures ambre (Glow, strength 1.4) et les iris (strength 1.2). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1107) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
