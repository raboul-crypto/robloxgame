Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Cendron » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Adulte Cendron » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Cendron = Feu, Commun, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Cendron : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte dragon classique puissant et droit, debout sur 4 pattes épaisses (LEG_H 2.1), torse de 4.3, cou de 6 plaques cendre (NECK_L 3.6), grosse tête (1.3) regardant vers l'avant, grandes ailes ouvertes, longue queue de 6.5.
- Tête : crâne carré en wedge, long museau avec plaque noire, mâchoire gris cendre distincte et ligne de bouche, narines noires. Yeux : blanc, iris orange lumineux, pupille fendue noire, sourcils sévères noirs. 3 crocs par côté, 3 pointes de joue, 2 grandes cornes noires torsadées recourbées vers l'arrière, crinière de 9 piques noires sur 2 anneaux.
- Signe distinctif : les fissures de lave orange sur tout le corps (4 sur les flancs, 3 sur le dos, sur les jambes, les ailes et la queue), ventre gris cendre, crête noire.
- Corps : torse en blocs, plastron et 6 plaques de ventre gris cendre plus plaques sur les flancs bas, 3 rangées de 5 écailles par flanc, 2 plaques de basalte fissurées sur le dos, crête de 6 piques noires, 4 piques d'épaule par côté, 2 piques de nuque.
- Ailes : grandes ailes à 3 doigts : os gris cendre épais (0.32), membrane rouge, bords gris effilochés (3 franges), 3 fissures orange, pointes noires. Envergure 6.6.
- Pattes : 4 pattes épaisses : épaule et cuisse en wedge, 2 piques de cuisse, genouillères sombres fissurées (BRACER_K 0.62), pied plat biseauté, 3 doigts + 3 griffes blanches.
- Queue : 6.5 de long, écailles, piques noires sur le dos, 2 segments biseautés, terminée par 3 grandes pointes noires et une braise (TAIL_TIP 2.0).
- Rendu de rareté : Commun poussé au maximum : basalte fissuré, bords effilochés, genouillères, yeux émissifs (1.8), aucune autre émission. 4 braises flottent autour du dragon.
- Palette (hex, Principled BSDF mats) :
  Body #B02E1E (corps rouge braise), BodyScale #8A2318 (écailles, dessus des pattes), BodyDark #4D1511 (genoux, bouche, ombres),
  Crest2 #D8461F (flammèches rouge vif), Belly #A8A29C (ventre en plaques, plastron, menton, gris cendre), AshDark #716B66 (bords d'ailes effilochés),
  Horn #2B2523 (cornes, crête, basalte noir), Rock #3E3632 (plaques de basalte), Claw #EDE6DA (griffes, crocs),
  Membrane #C03520 (membrane rouge), WingBone #8C8784 (os des ailes gris cendre), EyeWhite #F2F2EA, Eye #FF8A12 (iris orange, émission 1.8),
  Black #0A0A0A (pupilles, narines), Glow #FF7A12 (fissures de lave orange vif, non émissif), Ember #FF7A1A (braises flottantes).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les piques sont des éclats plats et pointus, la lave des fissures fines posées à plat sur les blocs.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty CENDRON_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « CENDRON_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots CENDRON_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Commun : seuls les iris (strength 1.8) sont émissifs ; les fissures de lave (Glow) et les braises flottantes ne le sont pas. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1110) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 braises flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, flammes ou feuilles)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
