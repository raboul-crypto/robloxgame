Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Trèfle » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Trèfle (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Trèfle », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Trèfle = Plante, Rare, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Trèfle : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte puissant et droit, debout sur 4 pattes épaisses, torse trapu, cou vertical de 6 maillons, tête haute regardant vers l'avant et un peu vers le bas, grandes ailes ouvertes vers le haut et l'arrière, longue queue qui traîne puis remonte.
- Tête : crâne carré en wedge, museau en bloc avec dessus plus clair, mâchoire crème distincte, ligne de bouche, narines carrées. Yeux latéraux : blanc carré, iris vert lumineux, pupille fendue noire, sourcils-feuilles sévères. 3 crocs crème par côté. Oreilles et 3 feuilles de joue par côté, collerette de 2 anneaux (16 feuilles).
- Signe distinctif : UN TRÈFLE SUR CHAQUE CORNE : 2 hautes cornes crème à 2 pointes, chacune portant un trèfle vert vif au bout, et un trèfle sur tige au sommet du crâne dans une couronne de feuilles avec un bourgeon.
- Corps : torse en 3 blocs, plastron crème, 6 plaques de ventre crème bien séparées + bandes sur les flancs, 3 rangées de 6 grandes feuilles en quinconce par flanc, cou de 6 maillons (plaque crème devant, 3 feuilles de nuque, lianes en écharpe), grande crête pâle dans le dos du cou + 2e plus petite (crête double), double rangée de 6 feuilles sur le torse, 4 feuilles d'épaulière par côté, 4 petits trèfles lumineux par flanc et 3 sur le dos.
- Ailes : grandes ailes (envergure 6.6) : bras et avant-bras ocre épais, 3 doigts, membrane vert-jaune pâle, grandes pointes crème au bout de chaque doigt et au poignet, grand trèfle de 3 cœurs vert foncé sur chaque membrane.
- Pattes : 4 pattes épaisses : épaule et cuisse en wedge, jambe, gros bracelet de bois avec lianes vertes, 2 feuilles sur chaque cuisse, petit trèfle lumineux sur la cuisse, pied plat, 3 doigts + 3 griffes crème par patte, pierre verte lumineuse sur le côté de 2 pieds.
- Queue : longue (6.5), plaques crème dessous, une feuille de crête par segment, écailles sur les côtés, petits trèfles lumineux, puis anneau de bois et grand trèfle à 3 feuilles au bout.
- Rendu de rareté (Rare) : silhouette lisible, motif secondaire (petits trèfles-motifs lumineux, grand trèfle sur les ailes), crête double, accent lumineux discret (strength 1.5 au maximum), pas de métal ni d'aura. 14 lucioles jaunes et feuilles flottent autour du dragon.
- Palette (hex, Principled BSDF) :
  Body #E2B24A (corps ocre doré, couleur de bois clair), BodyScale #B98A30 (écailles, tibias, dessus des pattes), SnoutTop #EEC862 (dessus du museau), BodyDark #7A5520 (bouche, ombres),
  LeafLight #A6E84C / LeafMid #5DBB35 / LeafDark #2F8A2A (feuilles, sourcils-feuilles, lianes), Clover #7FE03A (grands trèfles du crâne et des cornes), CloverStem #4FA32F (tiges),
  Mark #9BEF4A avec émission #7CF03A strength 0.7 (petits trèfles-motifs sur les flancs, le dos, les cuisses et la queue), Belly #F3E8BC (ventre en plaques, plastron, menton),
  Horn #EADBB0 (cornes), Bark #8A6228 (bracelets de bois, anneau de queue), Claw #FBF5E2 (griffes, crocs, pointes d'aile),
  Membrane #CBD866 (membrane des ailes, vert-jaune pâle), WingMark #4E9A2A (grand trèfle sur chaque aile), WingBone #B88E34 (os des ailes), Sail #DDF3B8 (grande crête pâle dans le dos),
  EyeWhite #F6F6EA, Iris #6FE03A avec émission #5BE02A strength 1.0, Black #0B0F08 (pupilles, narines), Gem #8CFF5E avec émission #5CFF3A strength 1.4 (pierres vertes aux pieds), Firefly #FFE45A avec émission #FFD83A strength 1.5 (lucioles).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles sont des losanges plats ou des éclats plats et pointus ; les trèfles sont faits de 3 cœurs plats autour d'une tige.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les feuilles, trèfles, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty TREFLE_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « TREFLE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots TREFLE_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, FANGS, MANE_N, WING_SPAN, WING_FINGERS, TAIL_L, SAIL, FLANK_CLOVERS, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Rare : un accent lumineux discret seulement (iris, trèfles-motifs, pierres, lucioles), strength 1.5 au maximum. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1105) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 lucioles et feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, trèfles, feuilles))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
