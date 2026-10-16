Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Boussole » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Bébé Boussole » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Boussole = Eau, Rare, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de le Bébé Boussole : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : bébé trapu et rond, debout sur 4 pattes très courtes et épaisses, torse court, cou très court (2 maillons), énorme tête carrée (environ 35 % de la hauteur), petites ailes, queue courte.
- Tête : crâne carré en wedge, museau court (60 % du museau adulte) avec arête gris-bleu et fine ligne dorée, mâchoire parchemin, ligne de bouche, 2 narines noires. Très grands yeux latéraux : blanc, grand iris doré lumineux, pupille ronde noire, 2 petits reflets blancs. Pas de crocs. 1 oreille-nageoire bleue, 2 ailerons de joue (laiton et gris-bleu) et 1 nageoire arrière par côté.
- Signes distinctifs : ROSE DES VENTS dorée sur le front (étoile à 8 branches : 4 longues + 4 courtes, anneau de laiton, lueur douce). 2 cornes en AIGUILLES DE BOUSSOLE sur des socles de laiton sombre : losange allongé en laiton, la gauche avec une pointe ROUGE, la droite avec une pointe laiton sombre.
- Corps : torse en 3 blocs, plastron parchemin avec une rose des vents dorée sur le poitrail (8 branches), 4 plaques de ventre parchemin séparées, 8 écailles bleues en quinconce (1 rangée de 4 par flanc), 1 ligne de carte dorée en tirets par flanc + 1 petite croix lumineuse par flanc, crête de 4 éclats de laiton, 1 pointe d'épaule par côté.
- Ailes : petites ailes-voiles : bras et 2 doigts en laiton, membrane bleue, pointes de laiton sombre au bout des doigts, griffe crème au poignet.
- Pattes : 4 pattes courtes : épaule et cuisse en bloc bleu, tibia sombre, bracelet de laiton avec bague de laiton sombre, pied plat, 3 doigts + 3 griffes crème.
- Queue : courte (6 segments bleus) avec plaques de ventre parchemin et 3 éclats de crête (laiton / gris-bleu), terminée par une petite flèche de boussole : bague de laiton sombre, hampe, pointe de flèche dorée avec 2 barbes et 2 plumes rouges.
- Rendu de rareté (Rare) : discret : motif secondaire (ligne de carte marine dorée), accent lumineux faible (iris, rose des vents, croix : strength 1.0 à 1.3), 2 gouttes d'eau lumineuses et 2 petites étoiles dorées flottent autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #214C98 (corps bleu marine), ScaleA #17376F (écailles sombres, dessus des pattes), ScaleB #4F6C8C (écailles gris-bleu, ailerons),
  BodyDark #0F2650 (sourcils, bouche), Belly #F0E2BC (ventre en plaques, plastron, menton : parchemin),
  Brass #D9AA3E (laiton métallique 0.85, rugosité 0.28 : rose des vents, cornes, bracelets, os d'aile, crête centrale) et BrassDark #A87F28 (bagues, pointes),
  NeedleRed #D8362B (pointe rouge de la corne gauche, empennage), Membrane #5C98DA (voile des ailes), MapLine #E2B84A (lignes de carte, non émissif),
  MapMark #FFD060 (rose des vents, repères : émission #FFB830, strength 1.0), Claw #F0E2BC (griffes, crocs), EyeWhite #F4F4EA,
  Iris #F5B52E (émission #FFB82A, strength 1.2), Black #0A0A0A (pupilles, narines), Droplet #6FE0F0 (gouttes flottantes : émission #4FD8F0, strength 1.3).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les roses des vents sont des étoiles plates à 8 branches (éclats plats) avec un anneau.

CONTRAINTES TECHNIQUES
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, plaques d'épaule), jamais sur les petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BOUSSOLE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BOUSSOLE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BOUSSOLE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission faible seulement sur l'iris, la rose des vents, les croix et les gouttes (Rare : jamais plus de 1.5). Laiton métallique. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4102) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 petits éléments flottants (gouttes d'eau et étoiles dorées).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   la description et corrige les écarts visibles (couleurs, taille de la tête, ailes, détails)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
