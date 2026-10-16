Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Goéland » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Goéland = Vol, Commun, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Goéland : pose, proportions, chaque
élément de la tête, du corps, des ailes-bras, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Bébé trapu et mignon : tête énorme (environ 35 % de la hauteur), corps court penché de 8 degrés, 2 pattes d'oiseau courtes, ailes-bras repliées dont le poignet touche presque le sol, queue courte en éventail.
- Tête : crâne blanc très gros (HEAD_SCALE 1.3), bec jaune court et épais (BEAK_K 0.6) avec mandibule inférieure jaune foncé et fine tache rouge, pas de dents, 2 narines. Yeux latéraux très grands : blanc, grand iris bleu lumineux, pupille noire, petit reflet blanc. Petits sourcils bleus. 2 petites cornes blanches, 1 plume de joue bleue par côté.
- Signes distinctifs : houppe de 2 rangées de 4 plumes bleues (pointes blanches, CREST_K 0.7), cou de 2 maillons, 4 plumes dorsales, 1 rangée de 3 plumes de flanc, 1 plume d'épaule et 1 de cuisse par côté. Pas de collerette.
- Corps : torse en 3 blocs biseautés (largeur 2.3, hauteur 2.2, longueur 3.0), 4 plaques de ventre blanches bien séparées, plastron blanc.
- Ailes-bras (wyvern : les ailes servent de bras) : 2 ailes-bras de 3.4 d'envergure : os bleu foncé épais (0.2), poignet à 0.7 du sol, 3 doigts avec 2 plumes de vol bleues à pointe blanche chacun, membrane bleu ciel, pas de plumes secondaires.
- Pattes : 2 pattes d'oiseau blanches de 1.9 de haut : cuisse emplumée en wedge, tarse fin, pied palmé (palmures #DCE6F2), 3 doigts + doigt arrière, griffes noires, sans biseau.
- Queue : 3.4 de long, pas de 0.7, segments bleus à ventre blanc, 2 segments biseautés, éventail de 5 plumes grises (1.9 de long, demi-ouverture 42 degrés).
- Rendu de rareté (Commun : silhouette lisible, 5 familles de couleurs (bleu, blanc, jaune, gris, noir), seuls les iris brillent (émission faible). Un seul signe fort : les ailes à plumes bleues aux pointes blanches. 4 plumes flottent autour du bébé.)
- Palette (hex, Principled BSDF) :
  Body #7DB6F0 (corps et plumes principales), BodyScale #5F9BE0 (plumes de flanc, dessus des pattes), BodyDark #456A9A (os d'aile, ligne de bouche), Crest #3F78CC (houppe, plumes du dos, sourcils),
  Belly #F6F8FB (tête, ventre en plaques, plastron, pattes, cornes, pointes des plumes), Beak #F5C022 (bec) / BeakLower #E0A410 (mandibule) / BeakSpot #E0452E (tache rouge),
  Fan #A9ADB3 (éventail de queue) / FanDark #80858D (pointes), Web #DCE6F2 (palmures), Claw #26262B (griffes),
  WingFeather #4F85D6 (plumes de vol) / WingLight #8EC1F5 (petites plumes, membrane), EyeWhite #F4F6F9, Iris #2E7FE0 avec émission #4FA0FF strength 1.5 (seule lueur), Black #0A0A0D (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les plumes sont des plaques plates en losange ou des éclats allongés, les plumes de vol sont fines et pointues.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, bec, torse, cuisses), jamais sur les plumes, griffes, os d'aile
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty GOELAND_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les ailes-bras).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « GOELAND_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots GOELAND_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (LEAN, BW, BH, TORSO_L, LEG_H, NECK_L, NECK_N, HEAD_SCALE, BEAK_K, TEETH, CREST_ROWS, CREST_N, WING_SPAN, WRIST_Z, FEATH_PER, TAIL_L, TAIL_FEATH, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée rééchantillonnée à pas constant, avec un repère par segment.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Seule émission : les iris (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 plumes flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 ailes-bras, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, bec, ailes-bras, éventail de queue)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
