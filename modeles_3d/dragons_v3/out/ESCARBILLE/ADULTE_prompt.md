Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Escarbille » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Escarbille (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Escarbille », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Escarbille = Feu, Rare, Brute, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Escarbille : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Drake massif comme un bloc de roche volcanique : corps large et bas, debout sur 4 grosses pattes, cou de 5 blocs, tête haute regardant vers l'avant et un peu vers le bas (6°), queue épaisse qui descend vers le sol. Pas d'ailes.
- Tête : crâne carré en wedge charbon, grand museau large avec plaque plus claire dessus et arête de roche, mâchoire orange distincte avec menton, ligne de bouche sombre, 2 narines noires, GRAND cristal-corne orange sur le bout du museau (sur une base rouge). Yeux : blanc, iris orange lumineux, pupille fendue noire, sourcils rouge sombre sévères. 3 crocs blancs par côté.
- Cornes et crinière : 2 cornes rouges à 2 pointes (grande corne rouge vers l'arrière + pointe orange vers l'extérieur) sur des bases rouge sombre, 1 corne de joue par côté, 9 grandes flammes de cristal orange en éventail derrière le crâne (les plus grandes au centre) sur des plaques rouges ; 3 roches sur le front, 3 sur chaque joue, 3 roches de barbe sous la mâchoire.
- Signe distinctif : ROCHE VOLCANIQUE ET FLAMMES : écailles hexagonales de roche noire, fissures de lave lumineuses, flammes en cristal orange (crinière, crête, épaules, bout de queue). CRÊTE DOUBLE : 6 plaques rouges taillées (rouge vif et rouge sombre en alternance) le long de l'échine et 5 flammes de cristal orange entre elles ; 4 grosses roches olive par épaule, avec 2 cristaux de flamme orange sur chaque épaule ; roches de nuque et 4 flammes le long de la nuque.
- Corps : torse en 3 blocs charbon (poitrail et bassin en wedge), plastron orange, 6 plaques de ventre orange bien séparées + bandes orange sur le bas des flancs, 15 hexagones de roche noire en quinconce par flanc (3 rangées de 5), hexagones sur les côtés du cou, 4 fissures de lave en zigzag (avec une branche) par flanc.
- Pattes : 4 pattes énormes : cuisse en wedge charbon, jambe en gantelet de roche olive, bracelet de roche sombre avec anneau rouge, genouillère de roche à l'avant, 2 hexagones et 1 fissure de lave sur la cuisse, 2 fissures sur le côté de la jambe + 1 devant, pied plat brun clair, 3 doigts + 3 griffes blanc crème par patte.
- Queue : queue épaisse qui s'affine (Catmull-Rom), plaques orange dessous, plaques rouges un segment sur deux et flammes de cristal orange sur l'autre, hexagones sur les côtés, puis un bout en roche olive avec dessus rouge sombre, 4 grandes flammes de cristal orange (ornement final) et 2 fissures de lave.
- Rendu de rareté (Rare) : Rare à pleine puissance : motif secondaire (hexagones de roche + fissures de lave partout), cornes à 2 pointes, crête double, crinière de flammes de cristal, un accent lumineux discret : yeux, flammes et fissures émissifs avec strength 1.2 à 1.5 (pas plus). 14 braises en losange flottent autour.
- Palette (hex, Principled BSDF) :
  Body #5C4D40 (corps charbon chaud), BodyScale #80674B (hexagones clairs, dessus du museau, doigts), BodyDark #1B1513 (bouche, ombres),
  Stone #84805A / StoneDark #57533A (roche olive : épaules, gantelets, bout de queue), Belly #F0872B (ventre, plastron, mâchoire),
  Foot #7A5B3C (pieds), Crest #D02A1C / CrestDark #8E1D16 (plaques de crête, cornes, sourcils), HornTip #FFB02E (pointes de corne),
  Flame #FF9A1F émission #FF7A10 et FlameHot #FFC24A émission #FFB02E, strength 1.4 (flammes de cristal), Claw #F4E7CF (griffes, crocs),
  EyeWhite #F4F1E8, Iris #F07A12 émission strength 1.2, Black #0C0907 (pupilles, narines), Lava #FFB02E émission #FF7A10 strength 1.5 (fissures).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les roches sont des blocs au dessus rétréci, légèrement tournés au hasard ; les hexagones sont des prismes plats posés sur la peau.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur
  les roches, flammes, griffes, fissures ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty ESCARBILLE_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT : le Drake n'a pas d'ailes). Chaque pièce est parentée au bon root. Les pièces de la
  tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne, penché de 6° vers l'avant).
- Tout dans une collection « ESCARBILLE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots ESCARBILLE_ADULTE_*. Il ne touche jamais aux autres
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
- Option ADD_FLOATING_FX pour ajouter ou non les 14 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, flammes, fissures, pattes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
