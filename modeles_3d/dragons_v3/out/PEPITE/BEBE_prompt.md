Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Pépite » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Pépite = Minéral, Mythique, Brute, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Pépite : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Bébé compact et trapu, debout sur 4 pattes courtes et épaisses, cou très court (1 maillon), grosse tête, queue courte qui finit en massue de pépites. Pas d'ailes (Drake).
- Tête : crâne carré en wedge d'or poli, museau court et large avec dessus plus sombre et arête claire, mâchoire pâle distincte et ligne de bouche, 2 narines noires. Grands yeux ronds : blanc, grand iris ambre lumineux, grande pupille ronde noire, 2 reflets blancs ; pas de sourcils, pas de crocs. 3 cornes d'or courtes en éventail par côté. 3 pépites sur le crâne entre les cornes, 1 pépites de joue par côté. Gemme rubis au front et 1 petites gemmes de tempe (ambre, émeraude, diamant).
- Signe distinctif : de grosses PÉPITES D'OR BRUT bosselées (icosphères basses aux sommets déplacés, seed fixe) en 3 teintes d'or (#D9A21B, #B8860F, #F6DC7A) sur le crâne, la nuque, les épaules, les flancs, le dos, les pattes et la queue.
- Halo : un HALO d'or flotte derrière la tête : anneau d'or épais (rayon 1,1 x la tête), anneau lumineux plus petit à l'intérieur, 6 pièces d'or sur l'anneau, pas de rayons.
- Corps : torse en 3 blocs d'or (poitrail en wedge, milieu, bassin en wedge), plastron or pâle avec un anneau d'or et une gemme ambre sertie + 2 petites gemmes (rubis, émeraude), 4 plaques de ventre or pâle bien séparées, pépites en quinconce sur les flancs (2 rangées de 4), armure dorsale de 4 plaques d'or, 2 grosses pépites d'épaule par côté + gemme émeraude, 10 éclats d'or lumineux (émissifs) sur le dos, cou de 1 maillon (bloc d'or + plaque pâle devant). Pas de veines (stade trop petit).
- Pattes : 4 pattes épaisses : cuisse en wedge, tibia en pépite sombre, bracelet d'or avec dessus clair, pépites sur la cuisse, pied plat en or, 3 doigts pâles + 3 griffes crème par patte.
- Queue : courte (environ 5 segments), plaques pâles dessous, grosse pépite par segment pair, massue de pépites (1 noyau + 4 pépites, 2 gemmes).
- Rendu de rareté (Mythique) : or métallique (metallic 0,8-0,9, rugosité basse) sur presque tout le corps, gemmes multiples (ambre, rubis, émeraude, petit diamant), éclats et veines ÉMISSIFS (strength 2-3,5), halo flottant derrière la tête. FX denses : 12 pièces d'or en 2 anneaux en orbite et 12 éclats d'or ou gemmes qui dérivent. Pas d'anneau au sol.
- Palette (hex, Principled BSDF ; metallic entre parenthèses) :
  Body #E6B422 (0,9, corps, cornes), BodyScale #CC9E1D (0,85, museau dessus, plaques, pieds), BodyDark #8A6C14 (0,6, bouche, ombres),
  Nugget #D9A21B / NuggetDark #B8860F / NuggetLight #F6DC7A (pépites), Belly #F4D77A (0,55, ventre, plastron, mâchoire),
  HornTip #FFF0B0, Crest #C8961A (sourcils), Coin #FFD24A (1,0, pièces), Claw #FBF1D0 (griffes, crocs),
  EyeWhite #F6F3EA, Iris #E0861E (émission #FFA21F), Black #0E0A07, Glow #FFE27A (émission #FFD54A, halo et éclats),
  Vein #FFE9A0 (émission #FFD34A), gemmes : GemAmber #FFAE1A, GemRuby #E0243A, GemEmerald #22C46E, GemDiamond #EAF7FF (émissives).
- Style : low-poly en blocs biseautés d'or, lisible de loin. Pas de sculpture organique ; les pépites sont des formes irrégulières à peu de faces.

CONTRAINTES TECHNIQUES
- Budget : 7000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les pépites, griffes, gemmes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty PEPITE_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant). Les FX flottants sont parentés au MASTER.
- Tout dans une collection « PEPITE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots PEPITE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, TAIL_L...) sont des variables faciles à modifier dans le bloc « RÉGLAGES DU STADE ».
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission sur les yeux, éclats, veines, gemmes et halo seulement. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5101) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les pièces et éclats flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, le Drake n'a pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, pépites, halo)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
