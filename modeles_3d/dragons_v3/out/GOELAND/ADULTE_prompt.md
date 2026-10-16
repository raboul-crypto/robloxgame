Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Goéland » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Goéland = Vol, Commun, Rapide, morphologie Wyvern ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Goéland : pose, proportions, chaque
élément de la tête, du corps, des ailes-bras, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Adulte puissant de wyvern à plumes façon oiseau de mer : torse penché de 14 degrés sur 2 grandes pattes d'oiseau, cou en S de 5 maillons, tête haute, grandes ailes-bras dont le poignet touche presque le sol et dont les doigts montent vers l'arrière, longue queue qui traîne avec un éventail.
- Tête : crâne blanc (HEAD_SCALE 1.2), bec jaune crochu long (BEAK_K 1.0) avec mandibule jaune foncé, tache rouge et 3 dents par côté, 2 narines. Yeux : blanc, iris bleu lumineux, pupille noire, sourcils sévères bleu profond. 2 grandes cornes blanches recourbées vers l'arrière, 3 plumes de joue par côté.
- Signes distinctifs : houppe de 3 rangées de 6 plumes bleues à pointe blanche (CREST_K 1.15), collerette de 7 plumes blanches, plumes sur les côtés du cou, 8 plumes dorsales, 2 rangées de 4 plumes de flanc, 3 plumes d'épaule et 3 de cuisse par côté.
- Corps : torse en 3 blocs biseautés (largeur 2.6, hauteur 2.5, longueur 4.8), 6 plaques de ventre blanches bien séparées, plaques blanches sur les flancs bas, plastron blanc.
- Ailes-bras (wyvern : les ailes servent de bras) : 2 grandes ailes-bras de 7.2 d'envergure : os bleu foncé (0.32), poignet à 1.2, 3 doigts avec 4 plumes de vol bleues à pointe blanche chacun, 3 plumes secondaires par aile, couvertures claires, seconde couverture bleue à facettes.
- Pattes : 2 pattes d'oiseau emplumées de 3.5 de haut : culotte bleue, cuisse en wedge biseautée, tarse fin, pied palmé, 3 doigts + doigt arrière, griffes noires.
- Queue : 6.6 de long, pas de 0.8, segments bleus à ventre blanc, écailles plates, 4 segments biseautés, plumes dorsales, éventail de 9 plumes grises (3.4 de long, demi-ouverture 42 degrés).
- Rendu de rareté (Commun au maximum : 5 familles de couleurs (bleu, blanc, jaune, gris, noir), seuls les iris brillent (émission faible), un seul signe fort bien dessiné : les ailes à plumes bleues aux pointes blanches. Détails : ventre en plaques, griffes, plumes. 10 plumes flottantes.)
- Palette (hex, Principled BSDF) :
  Body #7DB6F0 (corps et plumes principales), BodyScale #5F9BE0 (plumes de flanc, dessus des pattes), BodyDark #456A9A (os d'aile, ligne de bouche), Crest #3F78CC (houppe, plumes du dos, sourcils),
  Belly #F6F8FB (tête, ventre en plaques, plastron, pattes, cornes, pointes des plumes), Beak #F5C022 (bec) / BeakLower #E0A410 (mandibule) / BeakSpot #E0452E (tache rouge),
  Fan #A9ADB3 (éventail de queue) / FanDark #80858D (pointes), Web #DCE6F2 (palmures), Claw #26262B (griffes),
  WingFeather #4F85D6 (plumes de vol) / WingLight #8EC1F5 (petites plumes, membrane), EyeWhite #F4F6F9, Iris #2E7FE0 avec émission #4FA0FF strength 1.5 (seule lueur), Black #0A0A0D (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les plumes sont des plaques plates en losange ou des éclats allongés, les plumes de vol sont fines et pointues.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, bec, torse, cuisses), jamais sur les plumes, griffes, os d'aile
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty GOELAND_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les ailes-bras).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « GOELAND_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots GOELAND_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (LEAN, BW, BH, TORSO_L, LEG_H, NECK_L, NECK_N, HEAD_SCALE, BEAK_K, TEETH, CREST_ROWS, CREST_N, WING_SPAN, WRIST_Z, FEATH_PER, TAIL_L, TAIL_FEATH, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée rééchantillonnée à pas constant, avec un repère par segment.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Seule émission : les iris (rareté Commun). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 10 plumes flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 ailes-bras, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, bec, ailes-bras, éventail de queue)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
