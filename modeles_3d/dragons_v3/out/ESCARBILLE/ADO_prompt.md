Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Escarbille » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Escarbille (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Escarbille », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Escarbille = Feu, Rare, Brute, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Escarbille : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Drake plus long et plus musclé : torse allongé, cou de 3 blocs, tête plus petite et museau plus long, 4 pattes plus hautes, queue plus longue. Pas d'ailes.
- Tête : crâne carré en wedge charbon, museau large, plaque du dessus et arête de roche, mâchoire orange avec menton, ligne de bouche sombre, 2 narines noires, cristal-corne orange sur le museau (taille moyenne). Yeux plus sérieux : blanc, iris orange lumineux, pupille fendue noire, sourcils rouge sombre inclinés. 2 petits crocs blancs par côté.
- Cornes et crinière : 2 cornes rouges à 2 pointes (grande corne rouge + pointe orange), 1 corne de joue par côté, 6 flammes de cristal orange en éventail derrière le crâne sur des plaques rouges ; 2 roches sur le front, 2 sur chaque joue, 2 roches de barbe sous la mâchoire.
- Signe distinctif : ROCHE VOLCANIQUE ET FLAMMES : écailles hexagonales de roche noire, fissures de lave lumineuses, flammes en cristal orange (crinière, crête, épaules, bout de queue). 5 plaques rouges taillées le long de l'échine avec 4 flammes de cristal orange entre elles (crête double), 2 roches olive par épaule avec 1 cristal de flamme orange chacune, roches de nuque rouge sombre et 2 flammes sur la nuque.
- Corps : torse en 3 blocs charbon, plastron orange, 5 plaques de ventre orange + bandes orange sur le bas des flancs, 10 hexagones de roche noire en relief par flanc (2 rangées de 5), hexagones sur le cou, 2 fissures de lave par flanc.
- Pattes : 4 pattes : cuisse en wedge charbon, jambe brun-gris, bracelet de roche sombre avec anneau rouge, genouillère de roche, 2 hexagones et 1 fissure de lave sur la cuisse, 1 fissure sur la jambe, pied plat brun clair, 3 doigts + 3 griffes blanc crème.
- Queue : queue qui s'affine (Catmull-Rom), plaques orange dessous, plaques rouges et flammes de cristal dessus, hexagones sur les côtés, bout en roche olive avec 3 flammes de cristal orange.
- Rendu de rareté (Rare) : Rare à mi-puissance : hexagones et fissures de lave, cornes à 2 pointes, crête double, accent lumineux discret (yeux, flammes et fissures émissifs, strength 1.2 à 1.5). 9 braises en losange flottent autour.
- Palette (hex, Principled BSDF) :
  Body #5C4D40 (corps charbon chaud), BodyScale #80674B (hexagones clairs, dessus du museau, doigts), BodyDark #1B1513 (bouche, ombres),
  Stone #84805A / StoneDark #57533A (roche olive : épaules, gantelets, bout de queue), Belly #F0872B (ventre, plastron, mâchoire),
  Foot #7A5B3C (pieds), Crest #D02A1C / CrestDark #8E1D16 (plaques de crête, cornes, sourcils), HornTip #FFB02E (pointes de corne),
  Flame #FF9A1F émission #FF7A10 et FlameHot #FFC24A émission #FFB02E, strength 1.4 (flammes de cristal), Claw #F4E7CF (griffes, crocs),
  EyeWhite #F4F1E8, Iris #F07A12 émission strength 1.2, Black #0C0907 (pupilles, narines), Lava #FFB02E émission #FF7A10 strength 1.5 (fissures).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les roches sont des blocs au dessus rétréci, légèrement tournés au hasard ; les hexagones sont des prismes plats posés sur la peau.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur
  les roches, flammes, griffes, fissures ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty ESCARBILLE_ADO_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT : le Drake n'a pas d'ailes). Chaque pièce est parentée au bon root. Les pièces de la
  tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne, penché de 6° vers l'avant).
- Tout dans une collection « ESCARBILLE_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots ESCARBILLE_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE,
  SNOUT_K, FANGS, HORN_K, MANE_N, SNOUT_HORN, CREST_N, HEX_ROWS, CRACKS, FLAME_K, TAIL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur les flammes, les fissures et l'iris, strength 1.5 au maximum. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (2201) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 9 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, flammes, fissures, pattes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
