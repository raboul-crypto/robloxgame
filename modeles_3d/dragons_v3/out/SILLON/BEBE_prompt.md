Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Sillon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Sillon (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Sillon », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Sillon = Terre, Rare, Brute, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Sillon : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé wyvern trapue debout sur 2 pattes arrière courtes et épaisses (LEG_H 2.1), torse penché de 10 degrés, énorme tête (HEAD_SCALE 1.75, environ 35 % de la hauteur) sur un cou de 2 petits maillons, ailes-bras repliées, queue de 4.4.
- Tête : crâne carré en wedge, museau court, mâchoire crème distincte, narines noires. TRÈS grands yeux ambre : blanc, grand iris, pupille ronde noire, 2 reflets blancs. Pas de crocs. Petites cornes beiges, 1 feuille de joue par côté.
- Signe distinctif : la corne-SOC de charrue en pierre grise (Stone) plantée sur le museau, en petit. Couronne de 3 petites épines brunes sur le crâne, crinière d'épines brunes et de feuilles d'automne (1 anneau de 7) sur la nuque et le dos.
- Corps : torse en blocs arrondis, 4 plaques de ventre crème bien séparées, 2 rangées de 3 écailles-feuilles par flanc, crête de 4 épines, 2 feuilles d'épaule par côté, 1 feuille de poitrail, 2 plaques de masque sur la tête. Aucune fissure lumineuse.
- Ailes : ailes-bras repliées : os bruns (0.3), membrane brune avec 2 taches sombres, petite griffe en PELLE de pierre au poignet. Envergure 4.4.
- Pattes : 2 pattes arrière courtes et épaisses (cuisse en wedge, 1 feuille de cuisse), protège-tibias gris-vert moussus, pied plat, 3 doigts + 3 griffes crème.
- Queue : 4.4 de long, 6 segments biseautés, terminée par une petite lame en soc de 1.3.
- Rendu de rareté : Rare, discret : yeux ambre lumineux (1.2), pas de fissures, plus un motif secondaire (feuilles d'automne ambre, orange, ocre, olive). 5 feuilles flottantes.
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
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty SILLON_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « SILLON_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots SILLON_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (PITCH, BW, BH, TL, LEG_H, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, TAIL_L, TAIL_BLADE...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Rare : un accent lumineux discret seulement, les fissures ambre (Glow, strength 1.4) et les iris (strength 1.2). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1107) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 5 feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
