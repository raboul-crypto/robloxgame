Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Trèfle » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Trèfle (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Trèfle », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Trèfle = Plante, Rare, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Trèfle : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé trapu, assis bas sur 4 pattes courtes et épaisses, tête énorme (environ 35 % de la hauteur) presque posée sur le torse (cou d'un maillon), petites ailes à demi ouvertes, queue courte qui se termine par 2 feuilles.
- Tête : crâne carré en wedge, museau court et large avec dessus plus clair, mâchoire crème distincte et ligne de bouche brun, 2 narines carrées. TRÈS GRANDS YEUX : blanc carré, grand iris vert vif lumineux, pupille ronde, 2 petits reflets blancs, petit sourcil-feuille vert. Pas de crocs. Oreilles et 2 feuilles de joue en feuille verte, collerette d'un anneau de 9 feuilles derrière le crâne, 2 petits moignons de cornes crème.
- Signe distinctif : UN PETIT TRÈFLE sur tige verte planté au sommet du crâne (petite pousse à 3 feuilles).
- Corps : torse en 3 blocs arrondis, plastron crème, 4 plaques de ventre crème séparées, 1 rangée de 4 grandes feuilles par flanc, cou d'un maillon avec plaque crème, crête de 4 feuilles, 2 feuilles d'épaule par côté, 2 petits trèfles lumineux sur les flancs.
- Ailes : petites ailes : os ocre (bras et 2 doigts), membrane vert-jaune pâle, pointes crème au bout des doigts et au poignet, 1 petit trèfle foncé sur chaque membrane.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge ocre, jambe, bracelet de bois avec lianes vertes, 1 feuille sur la cuisse, gros pied plat, 3 doigts + 3 griffes crème par patte. Pas de pierre aux pieds.
- Queue : courte (2.8 de long), plaques crème dessous, une feuille de crête par segment, anneau de bois puis 2 feuilles au bout.
- Rendu de rareté (Rare) : silhouette lisible, motif secondaire (petits trèfles-motifs lumineux, grand trèfle sur les ailes), crête double, accent lumineux discret (strength 1.5 au maximum), pas de métal ni d'aura. 4 lucioles jaunes et feuilles flottent autour du bébé.
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
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les feuilles, trèfles, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty TREFLE_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « TREFLE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots TREFLE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, FANGS, MANE_N, WING_SPAN, WING_FINGERS, TAIL_L, SAIL, FLANK_CLOVERS, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Rare : un accent lumineux discret seulement (iris, trèfles-motifs, pierres, lucioles), strength 1.5 au maximum. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1105) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 lucioles et feuilles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, trèfles, feuilles))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
