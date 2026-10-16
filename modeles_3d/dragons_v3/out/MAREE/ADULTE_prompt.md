Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Marée » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Marée = Eau, Rare, Équilibré, morphologie Aquatique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Marée : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Adulte puissant et fluide : long cou en arche de vague (monte derrière le poitrail, passe par un sommet puis plonge vers l'avant), tête penchée de 20 degrés vers le bas, 4 pattes fines et musclées, torse long, longue queue de poisson sinueuse en S qui remonte en croissant.
- Tête : crâne en wedge fin, museau long en pointe de proue, arête turquoise, mâchoire blanche avec menton, ligne de bouche, 2 narines. Yeux en amande : blanc, iris bleu lumineux, pupille fendue noire, sourcils sévères bleu foncé. 3 crocs blancs par côté. Cornes bleues à 3 pointes (branche arrière, pointe de bout, pointe avant), 2 nageoires de joue turquoise par côté.
- Signe distinctif n°1 : CRÊTE EN VAGUE DÉFERLANTE. Sur le crâne, une vague faite de 6 lames en croissant qui montent puis se recourbent vers l'avant (bleu #1A4FA8 à la base, bleu roi, turquoise, bleu clair, pointe blanche d'écume émissive), doublée d'une 2e petite vague derrière (crête double). Sur le dos et le cou : une vague du même type tous les 2 segments, avec en plus de petites vagues sur les côtés une fois sur deux (2e rangée de la crête double), plus une fine nageoire dorsale continue (plaques turquoise / bleu clair alternées) ; de petites vagues continuent sur la queue.
- Signe distinctif n°2 : VOLUTES de vagues stylisées sur les flancs : 3 spirale(s) par flanc (à 2 bras : un blanc #F0F6F8, un bleu clair #8FD6EA faiblement émissif, environ 1.2 tour, 6 segments par bras), plus 1 volute sur chaque cuisse (5 segments).
- Signe distinctif n°3 : nageoires-oreilles : 5 rayons fins en éventail étroit rejetés vers l'arrière (rubans translucides turquoise / bleu clair, longueur 3.4).
- Dégradé de couleurs : dos et dessus du cou bleu roi #1F5FBF, flancs bleu #1B72C4, bas des flancs turquoise #25A0CC, haut des pattes #1E88C8, jambes #25A0CC, pieds #2FB8D0, la queue passe du bleu au turquoise du hanche au bout.
- Corps : torse sur une courbe Catmull-Rom (cou en arche + torse), segments biseautés plus fins que ceux d'Écume, bande turquoise sur le bas du flanc, plaque de dos bleu roi, plaques de ventre blanches bien séparées, plastron blanc sur le poitrail.
- Nageoires : à la place des ailes : 2 longues pectorales balayées vers l'arrière comme des voiles (5 rayons, longueur 4.8, pointe au bout du grand rayon), et 2 pelviennes à 3 rayons sur les hanches. Membranes translucides turquoise / bleu clair en alternance, rayons bleu roi.
- Pattes : 4 pattes fines : épaule et cuisse en wedge (dégradé), jambe en 2 barres, genouillère bleu foncé, grand pied turquoise, 3 doigts palmés + 3 griffes blanches par patte, petite nageoire turquoise à l'arrière de la jambe.
- Queue : queue de poisson de 7.0 de long en S (amplitude 0.8), segments qui s'affinent et passent du bleu au turquoise, ventre blanc, nageoire dorsale continue et petites vagues, nageoire caudale en croissant (2 lobes de 5 rayons, taille 3.4) avec une pointe claire au bout des grands rayons.
- Rendu de rareté (Rare) : motif secondaire (volutes de vagues), crête double, cornes à plusieurs pointes, dégradé de couleurs, et un accent lumineux discret : iris (strength 1.5), pointes d'écume des vagues et 2e bras des volutes (strength 0.9 et 0.8), rien de plus. 9 gouttes d'eau flottent autour du dragon.
- Palette (hex, Principled BSDF) :
  dégradé Grad0 #1F5FBF / Grad1 #1B72C4 / Grad2 #1E88C8 / Grad3 #25A0CC / Grad4 #2FB8D0, BodyDark #133973 (sourcils, ligne de bouche), BodyScale #17468D (plaque de dos, genouillères),
  Belly #F0F6F8 (ventre, plastron, mâchoire), Horn #1A4FA8 / HornTip #8FD6EA (cornes), Crest #2FB8D0 / Crest2 #8FD6EA (vagues, arête du museau),
  Mark #F0F6F8 (volutes), Foam #F0F6F8 émissif #8FD6EA (pointes d'écume), SwirlLight #8FD6EA émissif (2e bras des volutes),
  Fin #8FD6EA / FinTeal #2FB8D0 (membranes, alpha 0.82), FinRay #1F5FBF (rayons), Claw #F0F6F8 (griffes, crocs), EyeWhite #F2F2F2,
  Iris #1A6AD0 avec émission #4FB4FF (lueur), Black #0A0A0A (pupilles), Nostril #103958 (narines), Bubble #D6F6FF (gouttes, alpha 0.55).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les vagues sont des lames en croissant, les nageoires des plaques en éventail à rayons, les volutes des barres plates.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue, plastron), jamais sur les nageoires, rayons, griffes, écailles
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MAREE_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, penché vers l'avant de 20 degrés).
- Tout dans une collection « MAREE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots MAREE_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, NECK_REACH, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, CREST_H, WAVE_EVERY, SWIRLS, PEC_SPAN, TAIL_L, TAIL_SWAY, CAUDAL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission discrète seulement (Rare) : iris, pointes d'écume des vagues et 2e bras des volutes, strength 1.5 au maximum. Les nageoires sont translucides (alpha 0.82). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3308) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 9 gouttes d'eau flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, dégradé, crête en vague, volutes, cou en arche, queue en croissant))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
