Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Cendron » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Ado Cendron » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Cendron = Feu, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Cendron : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Ado dragon classique plus long et musclé, debout sur 4 pattes (LEG_H 1.7), torse de 3.6, cou de 5 plaques cendre (NECK_L 2.6), tête un peu plus petite (0.98), ailes ouvertes, queue de 5.0.
- Tête : crâne carré, museau plus long avec plaque noire, mâchoire gris cendre, narines noires. Yeux plus sérieux : blanc, iris orange lumineux, pupille fendue noire, sourcils noirs. 2 crocs par côté, 2 pointes de joue, cornes noires recourbées, crinière de 7 piques noires sur 1 anneau.
- Signe distinctif : fissures de lave orange sur le corps (3 sur les flancs, 2 sur le dos, fissures sur les pattes), ventre gris cendre, cornes noires, ailes rouges aux bords gris effilochés.
- Corps : torse en blocs, plastron et 5 plaques de ventre gris cendre plus plaques sur les flancs bas, 2 rangées de 3 écailles par flanc, 1 plaque de basalte fissurée sur le dos, crête de 5 piques noires, 3 piques d'épaule par côté, pointes de nuque.
- Ailes : ailes à 3 doigts : os gris cendre (0.26), membrane rouge, bords gris effilochés (2 franges), 2 fissures orange, pointes noires. Envergure 5.4.
- Pattes : 4 pattes : épaule et cuisse en blocs, 1 pique de cuisse, genouillère sombre fissurée (BRACER_K 0.55), pied plat, 3 doigts + 3 griffes claires.
- Queue : 5.0 de long, écailles et piques noires sur le dos, terminée par 3 pointes noires et une braise (TAIL_TIP 1.4).
- Rendu de rareté : Commun à mi-puissance : rouge, gris cendre, noir, fissures orange non émissives, yeux émissifs. 3 braises flottantes autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #B02E1E (corps rouge braise), BodyScale #8A2318 (écailles, dessus des pattes), BodyDark #4D1511 (genoux, bouche, ombres),
  Crest2 #D8461F (flammèches rouge vif), Belly #A8A29C (ventre en plaques, plastron, menton, gris cendre), AshDark #716B66 (bords d'ailes effilochés),
  Horn #2B2523 (cornes, crête, basalte noir), Rock #3E3632 (plaques de basalte), Claw #EDE6DA (griffes, crocs),
  Membrane #C03520 (membrane rouge), WingBone #8C8784 (os des ailes gris cendre), EyeWhite #F2F2EA, Eye #FF8A12 (iris orange, émission 1.8),
  Black #0A0A0A (pupilles, narines), Glow #FF7A12 (fissures de lave orange vif, non émissif), Ember #FF7A1A (braises flottantes).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les piques sont des éclats plats et pointus, la lave des fissures fines posées à plat sur les blocs.

CONTRAINTES TECHNIQUES
- Budget : 4500 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty CENDRON_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « CENDRON_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots CENDRON_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Commun : seuls les iris (strength 1.8) sont émissifs ; les fissures de lave (Glow) et les braises flottantes ne le sont pas. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1110) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 3 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
