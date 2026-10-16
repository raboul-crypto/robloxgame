Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Stalactite » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Si tu as une image (Bébé, Ado, Adulte), seul le dragon en bas à gauche, nommé « Bébé Stalactite », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Stalactite = Minéral, Rare, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Stalactite : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Drake trapu et arrondi : debout sur 4 pattes, cou de 1 bloc, tête regardant vers l'avant et un peu vers le bas (7°), queue épaisse qui descend vers le sol. Pas d'ailes. Gabarit Tank.
- Tête : crâne carré en wedge gris pierre, très gros (tête environ 35 % de la hauteur), museau court avec plaque claire dessus et arête de calcaire, mâchoire gris clair distincte avec menton, ligne de bouche sombre, 2 narines noires. YEUX très grands (blanc, grand iris bleu pâle lumineux, pupille ronde, 2 petits reflets blancs), petit sourcil de roche, pas de crocs. 2 plaque(s) de roche sur le front, 2 sur chaque joue. BARBE de 2 stalactites de calcaire qui pendent sous la mâchoire. Grappe de 2 cristaux bleu pâle translucides sur le front (sur un bloc sombre).
- Cornes : 2 cornes de pierre à 2 pointes : grande corne de calcaire blanc vers l'arrière + pointe plus courte ombrée vers l'extérieur, sur des bases de roche sombre (versions courtes).
- Signe distinctif : STALAGMITES DE CALCAIRE : forêt de 5 grandes pointes blanc-gris taillées en facettes le long de l'échine (sur des bases de roche), 4 pointes plus petites de chaque côté (crête double), 4 petits cristaux translucides entre elles, stalagmites sur la queue (1 segment sur 2), 3 stalactites qui pendent sous le poitrail ; GRAPPES DE CRISTAUX TRANSLUCIDES (2 cristaux) sur les épaules (1 par côté) et au bout de la queue.
- Corps : torse en 3 blocs gris pierre (poitrail et bassin en wedge), plastron gris clair, 4 plaques de ventre gris clair bien séparées + bandes claires sur le bas des flancs, 2 strate(s) de roche claire/sombre en 3 morceaux irréguliers sur chaque flanc, plaques de roche en losange en quinconce (2 rangées de 3), 2 veine(s) de minerai lumineuse(s) en zigzag par flanc, 2 roche(s) d'épaule par côté, cou de 1 bloc avec plaque claire devant chaque bloc.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge gris, jambe grise, pied plat gris clair, 3 doigts + 3 GRIFFES DE PIERRE épaisses blanc-gris par patte.
- Queue : queue épaisse qui s'affine (Catmull-Rom), plaques claires dessous, stalagmites dessus, puis une massue de roche (2 blocs) hérissée de 4 stalagmites et d'une grappe de 3 cristaux (ornement final).
- Rendu de rareté (Rare) : motif secondaire (strates + plaques de roche + veines de minerai claires), cornes à 2 pointes, crête double de stalagmites, un accent lumineux discret : iris, cristaux et veines émissifs avec strength 1.2 à 1.4 (pas plus de 1.5). 6 éléments flottants (petits cristaux translucides et éclats de calcaire en losange) autour du dragon. Rendu discret : le bébé porte déjà tous les signes, en petit.
- Palette (hex, Principled BSDF) :
  Body #74869B (corps gris pierre bleuté), BodyLight #92A3B5 (dessus du museau, pieds), BodyDark #4B5663 (bouche, bases de cristaux),
  Stone #8191A4 / StoneDark #5A6676 (plaques de roche : épaules, jambes, sourcils, bout de queue), Strata #B8C3CC (strates claires, bracelets),
  Belly #D5D9DD (ventre, plastron, mâchoire), Limestone #ECE8DC / LimeShade #C9C3B1 (stalagmites, stalactites, cornes), Claw #E3E1DA (griffes de pierre, crocs),
  Crystal #BFE3F2 translucide (alpha 0.78) émission #8FD4F0 strength 1.2 et CrystalDeep #7FC4E6 (alpha 0.85) émission strength 1.3 (cristaux),
  Vein #A8DCF2 émission strength 1.4 (veines de minerai), EyeWhite #F2F5F7, Iris #7FC4E6 émission strength 1.2, Black #0E1216 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les stalagmites/stalactites sont des cônes à 5 facettes ; les cristaux sont des prismes à 6 faces à pointe, en grappes sur un bloc sombre ; les roches sont des blocs au dessus rétréci, légèrement tournés au hasard.

CONTRAINTES TECHNIQUES
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur
  les éclats, griffes, cristaux, coraux ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty STALACTITE_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT : le Drake n'a pas d'ailes). Chaque pièce est parentée au bon root. Les pièces de la
  tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne, penché vers l'avant).
- Tout dans une collection « STALACTITE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots STALACTITE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, SNOUT_K, FANGS, HORN_K, BEARD, CREST_N, SIDE_ROW, CLUSTER_N, SHOULDER_ROCKS, STRATA, CRACKS, TAIL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur l'iris, les cristaux et les veines, strength 1.5 au maximum ; cristaux semi-transparents (alpha 0.78 et 0.85). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5502) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, signes
   distinctifs, pattes) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
