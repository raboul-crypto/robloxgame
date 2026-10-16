Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Ombrelame » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Adulte Ombrelame » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Ombrelame = Ténèbres, Épique, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de l'Adulte Ombrelame : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Adulte wyvern fine et rapide, penchée de 18 degrés, 2 pattes arrière hautes (LEG_H 4.6), cou de 5 maillons, tête de HEAD_SCALE 1.3, ailes-bras très grandes (envergure 7.5, poignet bas), longue queue de 8.
- Tête : crâne carré en wedge, long museau, arête avec une lame, mâchoire gris violet et ligne de bouche, narines. Yeux : blanc, iris violet lumineux, pupille fendue, sourcils sévères violets avec une lame d'arcade. 3 crocs par côté, 2 éclats lumineux au coin de chaque oeil, 4 lames de joue par côté, barbe de 5 lames, grandes cornes violettes à 2 pointes plus une corne basse, pointes claires, anneaux dorés.
- Signes distinctifs : crinière en lames à 3 anneaux (14, 12 et 10 lames), 5 lames sur le crâne, ailes-bras dont le bord est une rangée de lames facettées (8 par segment, 3 segments), 4 lames sur l'avant-bras, 4 lames par doigt, grande lame au bout de chaque doigt, liserés violets lumineux (3 par flanc, sur les cuisses, le long des doigts et du bord des ailes, 3 sur la queue), queue-lame : grande lame facettée (taille 2.3) avec une seconde lame claire par-dessus, nervure lumineuse et 2 lames latérales par côté.
- Corps : torse en 3 blocs, plastron gris violet avec plaque dorée et gemme violette lumineuse, 6 plaques de ventre biseautées, 4 rangées de 7 écailles par flanc, 6 lames de côtes par flanc, 8 grandes lames sur le dos avec 7 petites lames entre elles et 8 lames latérales, 4 lames par épaule, cou de 5 maillons avec lames de nuque et lames latérales.
- Ailes : très grandes ailes-bras noir violacé : bras, avant-bras, 3 doigts violets terminés par une lame, membrane en triangles, bord en lames facettées avec liseré lumineux, bracelet doré, lame de poignet, griffe de pouce et 2 griffes au poignet.
- Pattes : 2 pattes arrière : cuisse en wedge avec 3 lames, tibia avec 2 lames, genouillère en lame, bande claire, bracelet de cheville doré, liseré lumineux sur la cuisse, pied biseauté, 3 doigts et 3 griffes pâles.
- Queue : segments le long d'une courbe lissée, ventre en plaques claires sur les 3/4 avant, une lame sur chaque segment du dos, lames latérales sur chaque segment, écailles, liserés, anneau doré, grande lame facettée au bout.
- Rendu de rareté (Épique) : Épique au maximum : iris, éclats d'yeux, liserés, nervure de la lame et cristaux émissifs (2.4), ornements dorés (cornes, plastron, poignets, chevilles, bout de queue), 14 lames et cristaux violets flottants.
- Palette (hex, Principled BSDF mats) :
  Body #33204A (corps noir violacé), BodyScale #241636 (écailles sombres, dessus des pattes, orteils), ScaleB #3F2760 (écailles plus claires), BodyDark #140C1E (bouche, genoux),
  Belly #8E7BAA (ventre en plaques, plastron, menton), Horn #6A44A8 (cornes, sourcils), HornTip #C79BFF (pointes de cornes), Blade #4A2F6E / BladeLight #7A55B0 (lames facettées, metallic 0.55),
  Membrane #3A2458 (membrane des ailes), WingBone #6A44A8 (os d'aile), Claw #D9C8F5 (griffes pâles), Fang #EDE6F8 (crocs), EyeWhite #F2F2F2, Iris #C79BFF (émission 2.4), Black #0A0A0A (pupilles),
  Glow #B07CFF (liserés, nervure de la lame, cristaux, émission 2.4), Gold #D8B050 (ornements dorés, metallic 0.85)
- Style : low-poly en blocs biseautés, lisible de loin. Les lames sont des éclats facettés à arête centrale (8 à 10 triangles), les liserés sont de petites barres lumineuses posées sur la peau. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 13000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty OMBRELAME_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « OMBRELAME_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots OMBRELAME_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TL, PITCH, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, BLADE_N, TAIL_L, TAIL_BLADE...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Épique : seuls les iris, les éclats d'yeux, les liserés, la nervure de la lame et les cristaux sont émissifs (strength 2.4), le corps et les lames ne le sont pas. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5531) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 lames et cristaux violets flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, lames)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
