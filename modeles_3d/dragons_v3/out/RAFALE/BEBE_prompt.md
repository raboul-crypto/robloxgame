Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Rafale » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi. Si tu as une image,
   seul le dragon en bas à gauche, nommé « Bébé Rafale », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Rafale = Vol, Rare, Rapide, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image (quand elle existe) et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description ci-dessous impose) sur le Bébé Rafale : pose, proportions,
chaque élément de la tête, du corps, des ailes et de la queue, et la palette. Puis liste les contraintes du GDD
qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : petit serpent blanc enroulé, haut du corps dressé, cou court, tête énorme (environ 35 % de la hauteur), petites ailes de plumes. Pas de pattes. Tête inclinée de 8° vers l'avant.
- Tête : crâne carré en wedge blanc #F4F6F9, museau très court, arête et plaque du front bleu ciel #6FB4EE, mâchoire bleu pâle #DCEBFA, ligne de bouche, 2 narines, fine bande argent de chaque côté du museau. Yeux : très grands (blanc, grand iris bleu lumineux, pupille ronde noire, 2 petits reflets blancs), pas de crocs, pas de sourcils.
- SIGNE DISTINCTIF, crête de plumes : 5 plumes du front à la nuque, rabattues vers l'arrière, blanches et bleu ciel en alternance avec une pointe bleue #2F7FCF. 2 plumes-oreilles et 1 plume(s) de joue par côté, balayées vers l'arrière.
- Cornes : 2 cornes bleues #2F7FCF recourbées vers l'arrière, sur des bases bleues, pointe bleue vive, une seule pointe pour le Bébé.
- Corps : segments blancs en deux teintes (#F4F6F9 / #CCD8E2), dos bleu ciel #6FB4EE (plaque sur le haut de chaque segment), plaques de ventre bleu très pâle bien séparées, plastron pâle avec 4 plumes de poitrine, 2 plumes d'épaule par côté. SIGNE DISTINCTIF : BANDES DE VENT gris argent métallique #9EA8B4 enroulées autour du corps : anneaux à 8 côtés inclinés de 34°, une bande tous les 4 segments, l'inclinaison alterne (effet d'hélice). Crête de plumes sur le dos : une plume blanche ou bleu ciel tous les 2 segments, couchée vers l'arrière.
- Ailes : 2 ailes de PLUMES effilées (pas de membrane) : bras et avant-bras en os bleus, petite membrane pâle à la base, 5 plumes primaires en éventail au poignet, 4 plumes secondaires le long du bras, pointes bleues légèrement lumineuses, griffe de pouce pâle. Toutes les plumes sont posées dans le plan de l'aile. Envergure d'une aile environ 5.6 (unités de travail).
- Queue : même courbe que le corps ; elle remonte en hélice au-dessus des anneaux ; bout en anneau argent avec un TOURBILLON de 4 plumes (blanches et bleu ciel) qui tournent autour de l'axe de la queue, longueur 1.3. 5 plumes posées au sol autour des anneaux.
- Rendu de rareté (Rare), discret : motif secondaire (bandes de vent argent), cornes à branche (pas sur le Bébé), crête simple (la double arrive à l'Adulte), accent lumineux discret : iris bleu (strength 1.3) et pointes de plumes bleues (0.8). 6 plumes qui tourbillonnent autour du dragon.
- Palette (hex, Principled BSDF) :
  Body #F4F6F9 (corps blanc), BodyGrey #CCD8E2 (segments alternés), Sky #6FB4EE (dos, front, arête du museau), Belly #DCEBFA (ventre, mâchoire, plastron),
  Mouth #5E6F80 (bouche, narines), Silver #9EA8B4 métallique 0.75 (bandes de vent, collier, anneau de queue), FeatherW #F7F9FC, FeatherS #8FC6F2,
  FeatherTip #2F7FCF émission #3D8FE0 strength 0.8 (pointes de plumes), WingBone #2F7FCF (os d'aile, cornes), Claw #EAF2FA (crocs, pouce),
  EyeWhite #FFFFFF, Iris #2F9BFF émission strength 1.3, Black #0A1018 (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les plumes sont des plaques fines en losange allongé (avec une pointe d'une autre couleur), les bandes de vent des anneaux plats.

CONTRAINTES TECHNIQUES
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du corps), jamais sur
  les nageoires, plumes, os d'aile, cornes ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty RAFALE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT
  (LEGS_ROOT ne porte que les pièces posées au sol : l'amphiptère n'a pas de pattes). Chaque pièce est parentée au
  bon root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne,
  penché de 8° vers l'avant).
- Tout dans une collection « RAFALE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots RAFALE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (ZB, NECK_H, COIL_R, TAIL_UP, HEAD_SCALE, SNOUT_K, FANGS, CREST_N, EAR_N, FEATHER_K, BAND_EVERY, WING_SPAN, WING_LIFT, WING_PRIM, WING_SEC, TAIL_F, FX_N...) :
  c'est le seul bloc qui change entre Bébé, Ado et Adulte.
- Le corps (cou, descente, anneaux au sol, queue) suit UNE courbe Catmull-Rom (CTRL) rééchantillonnée à pas
  constant, avec un repère par segment (tangente, dos, côté) et un rayon par clés (RADIUS_KEYS), comme le Mirage.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur l'iris et les pointes de plumes, strength 1.3 au maximum. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4404) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 plumes flottant.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes (aucune), 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, crête de plumes, bandes de vent argent, plumes des ailes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
