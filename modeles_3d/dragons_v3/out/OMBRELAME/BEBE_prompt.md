Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Ombrelame » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Bébé Ombrelame » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Ombrelame = Ténèbres, Épique, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends du Bébé Ombrelame : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Bébé wyvern trapu, penché de 10 degrés, 2 pattes courtes et épaisses (LEG_H 2.1), cou de 2 maillons, très grosse tête (HEAD_SCALE 1.75, environ 35 % de la hauteur), ailes-bras courtes (envergure 4.4), queue de 4.4.
- Tête : crâne en wedge et museau très court, arête du museau avec une petite lame, mâchoire gris violet et ligne de bouche, narines. Très grands yeux : blanc, grand iris violet lumineux, pupille ronde, 2 reflets blancs, sourcils violets fins. Pas de crocs. 2 petites cornes violettes à pointe claire, oreilles en lame, 1 lame de joue par côté.
- Signes distinctifs : crinière en lames (1 anneau de 8 lames, 3 lames sur le crâne), ailes-bras dont le bord est une rangée de lames facettées (3 par segment, 3 segments) avec une lame au bout de chaque doigt, petite queue terminée par une lame facettée (taille 1.1), 1 liseré violet lumineux sur chaque flanc et sur la queue.
- Corps : torse en 3 blocs penchés, plastron gris violet et 4 plaques de ventre biseautées, 2 rangées de 3 écailles par flanc, 4 lames sur le dos, 2 lames sur chaque épaule, cou en plaques avec une lame de nuque par maillon.
- Ailes : ailes-bras noir violacé : bras, avant-bras, 3 doigts osseux violets, membrane en triangles, bord en lames, lame de poignet, griffe de pouce et 2 petites griffes au poignet. Pas de bracelet.
- Pattes : 2 pattes arrière : cuisse en wedge, tibia, genouillère en lame, bande claire sur le tibia, 1 lame sur la cuisse, pied plat biseauté, 3 doigts et 3 griffes pâles.
- Queue : segments le long d'une courbe lissée, ventre en plaques claires sur les 3/4 avant, une lame sur chaque segment du dos, 1 liseré lumineux, grande lame facettée au bout (une seule lame, pas de lames latérales).
- Rendu de rareté (Épique) : Épique en touche discrète : iris (2.4) et liserés (2.4) émissifs, 6 lames et cristaux violets flottants. Pas d'or sur le bébé.
- Palette (hex, Principled BSDF mats) :
  Body #33204A (corps noir violacé), BodyScale #241636 (écailles sombres, dessus des pattes, orteils), ScaleB #3F2760 (écailles plus claires), BodyDark #140C1E (bouche, genoux),
  Belly #8E7BAA (ventre en plaques, plastron, menton), Horn #6A44A8 (cornes, sourcils), HornTip #C79BFF (pointes de cornes), Blade #4A2F6E / BladeLight #7A55B0 (lames facettées, metallic 0.55),
  Membrane #3A2458 (membrane des ailes), WingBone #6A44A8 (os d'aile), Claw #D9C8F5 (griffes pâles), Fang #EDE6F8 (crocs), EyeWhite #F2F2F2, Iris #C79BFF (émission 2.4), Black #0A0A0A (pupilles),
  Glow #B07CFF (liserés, nervure de la lame, cristaux, émission 2.4), Gold #D8B050 (ornements dorés, metallic 0.85)
- Style : low-poly en blocs biseautés, lisible de loin. Les lames sont des éclats facettés à arête centrale (8 à 10 triangles), les liserés sont de petites barres lumineuses posées sur la peau. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 5000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty OMBRELAME_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « OMBRELAME_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots OMBRELAME_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TL, PITCH, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, TAIL_L, TAIL_BLADE...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Épique : seuls les iris (2.4), les liserés et les cristaux (2.4) sont émissifs, le corps et les lames ne le sont pas. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5531) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 lames et cristaux violets flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, lames)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
