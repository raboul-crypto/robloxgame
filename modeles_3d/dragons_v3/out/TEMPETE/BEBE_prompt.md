Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Tempête » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Bébé Tempête » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Tempête = Vol, Épique, Brute, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de le Bébé Tempête : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Bébé wyvern trapu, penché de 10 degrés, 2 pattes courtes et épaisses (LEG_H 2.1), cou de 2 maillons, très grosse tête (HEAD_SCALE 1.75, environ 35 % de la hauteur), ailes-bras courtes (envergure 4.4), queue de 4.4.
- Tête : crâne en wedge et museau très court, arête du museau, mâchoire claire et ligne de bouche, narines. Très grands yeux : blanc, grand iris bleu glacier lumineux, pupille ronde, 2 reflets blancs, sourcils de nuage fins. Pas de crocs. 2 petites cornes anthracite, oreilles en éclat, 1 nuage de joue par côté.
- Signes distinctifs : crinière de nuage blanc et gris (1 anneau de 8 nuages, 3 éclats sur le crâne), touffe de nuage au bout de la queue, ailes-bras aux bords effilochés en nuages (2 nuages par segment), 1 spirale de vent claire sur chaque flanc et sur la queue. Pas d'éclairs : la Foudre est un élément futur.
- Corps : torse en 3 blocs penchés, plastron clair et 4 plaques de ventre, 2 rangées de 3 écailles par flanc, 4 nuages et éclats sur le dos, 1 nuage sur chaque épaule, cou en plaques avec nuage de nuque.
- Ailes : ailes-bras gris orage : bras, avant-bras, 3 doigts osseux avec pointes anthracite, membrane en triangles avec bandes claires, bord effiloché en nuages, griffe de pouce et 2 petites griffes au poignet. Pas de bracelet.
- Pattes : 2 pattes arrière : cuisse en wedge, tibia, genouillère de nuage, bande claire sur le tibia, pied plat biseauté, 3 doigts et 3 griffes anthracite.
- Queue : segments le long d'une courbe lissée, ventre en plaques claires sur les 3/4 avant, nuages et éclats blancs sur le dos, spirales de vent, touffe de nuage au bout.
- Rendu de rareté (Épique) : Épique en touche discrète : iris (2.4) et spirales de vent (2.2) émissifs, quelques nuages et éclats de vent flottants (6). Pas d'or sur le bébé.
- Palette (hex, Principled BSDF mats) :
  Body #6B80A2 (corps gris orage bleuté), BodyScale #4D5F80 (écailles, dessus des pattes, orteils), BodyDark #2C3650 (sourcils, bouche, genoux),
  Belly #EAF0F8 (ventre en plaques, plastron, menton), Cloud #F6FAFF / CloudGrey #B3C1D6 / CloudDark #8E9CB8 (nuages de la crinière, du dos, des bords d'ailes),
  Horn #2D3342 (cornes), Membrane #8EA3C6 (membrane des ailes), MembraneBand #B4C6E0 (bandes claires), WingBone #5A6A8A (os d'aile),
  Claw #2D3342 (griffes), Fang #EEF2F8 (crocs), EyeWhite #F2F6FC, Iris #7FC8F0 (émission 2.4), Black #0A0D14 (pupilles),
  WindGlow #CBE9FF (spirales de vent, émission 2.2), Gold #D8B050 (ornements dorés, metallic 0.85)
- Style : low-poly en blocs biseautés, lisible de loin. Les nuages sont des cubes facettés tournés qui se chevauchent
  (blanc, gris clair, gris d'orage), les éclats sont plats et pointus. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 5000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty TEMPETE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « TEMPETE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots TEMPETE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TL, PITCH, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Épique : seuls les iris (2.4) et les spirales de vent (2.2) sont émissifs (strength 2.2 à 2.4), les nuages et le corps ne le sont pas. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 nuages et éclats de vent flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, nuages)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
