Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Aurore » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Aurore (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Aurore », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Aurore = Plante, Épique, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Aurore : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : dragon oriental qui flotte, corps en S. Tête haute en avant, cou dressé qui descend vers
  le poitrail, ventre bas, puis queue qui remonte derrière et s'enroule vers l'avant au-dessus du dos.
- Tête : crâne en wedge, long museau carré avec arête lime, mâchoire crème distincte, ligne de bouche
  vert foncé, 2 narines noires, yeux latéraux (blanc, iris vert vif, pupille fendue), sourcils sévères,
  3 crocs crème par côté, oreilles-feuilles, 3 feuilles de joue par côté, barbe de 5 feuilles sous le
  menton, petite couronne de 3 éclats dorés par côté au-dessus des yeux.
- Bois : signe distinctif, deux grands bois beige ramifiés de cerisier (3 barres qui s'affinent + 4
  pointes chacun, bout doré), 4 feuilles lumineuses sur chaque bois et 2 fleurs de cerisier roses (5
  pétales roses lumineux + coeur doré) au bout des pointes. Entre les bois, une pousse lumineuse :
  tige vert foncé, 2 feuilles lime émissives, un bourgeon.
- Moustaches : deux longues moustaches dorées (5 barres) qui partent du museau, s'écartent puis
  remontent en boucle vers l'arrière.
- Crinière : grande collerette de feuilles en losange derrière le crâne, 4 anneaux (17, 15, 13, 11
  feuilles) en vert clair / moyen / foncé, une partie lime lumineuse et quelques feuilles dorées,
  6 fleurs roses piquées dedans. Elle continue le long du cou (4 feuilles par segment + éclats sur
  les côtés).
- Corps : segments verts biseautés, plaques de ventre crème bien séparées, bandes de flanc alternées
  lime / vert, une nervure lime émissive sur chaque flanc, une écaille-feuille par segment et par côté,
  plaque dorsale vert foncé, crête de feuilles en losange (une par segment, éclats dorés tous les 4).
  Une liane vert foncé serpente sur un flanc avec des feuilles et des fleurs de cerisier roses.
  Plastron brun avec plaque dorée, gemme verte émissive et 2 éclats dorés ; épaulières brunes en
  wedge avec 3 plumes dorées chacune.
- Pattes : 4 petites pattes qui pendent (avant au poitrail, arrière au bas du ventre) : épaule en
  wedge, 2 os, bracelet doré avec anneau or foncé, feuille au coude, pied, 3 doigts + 3 griffes crème.
- Queue : s'affine, bandes dorées tous les 3 segments, anneau doré au bout puis touffe de 5 feuilles
  (certaines lumineuses) et une grande feuille lime émissive.
- Rendu de rareté (Épique, complet) : feuilles et pousse lumineuses lime, nervures lime sur les flancs,
  bois en fleurs roses lumineuses, aura de 15 grandes feuilles roses émissives qui rayonnent derrière la
  crinière, ornements dorés (couronne, plastron, épaulières, bracelets, bandes), gemme verte, 14 FX
  flottants (feuilles lime et vertes, étincelles dorées, étoiles roses).
- Palette (hex) : Body #6CC02E (corps), BodyScale #4FA524 (écailles, bas des pattes), BodyDark #2C7A1E
  (sourcils, bouche, dos), LeafLight #A8E64A / LeafMid #5DBB2C / LeafDark #2F8A24 (feuilles),
  Belly #E6D49A (ventre, mâchoire), Horn #D9BF8A (bois), Gold #F0B72E et DarkGold #B87A16 (métal 0.5),
  Brown #7B4A22 (plastron, épaulières), Claw #F6EEDA (griffes, crocs), EyeWhite #F4F4EA, Black #0B0F08,
  émissifs : Iris #9BE03C (lueur 1.2), LeafGlow #6EE23A (2.4), PinkGlow #FF8EBE (2.2),
  Gem #74FF5A (3.0), Spark #FFD25A (2.8).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Feuilles en losanges plats, pétales en éclats plats.

CONTRAINTES TECHNIQUES
- Budget : 13 000 triangles maximum après modificateurs (vise 85-95 %). Biseau à 1 segment au plus,
  et seulement sur les gros blocs (crâne, museau, segments, épaules, pieds), jamais sur les feuilles,
  pétales, griffes ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty AURORE_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT,
  TAIL_ROOT. Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées
  locales de HEAD_ROOT (base du crâne, légère inclinaison).
- Tout dans une collection « AURORE_ADULTE ». Le script est relançable : au début, il supprime
  uniquement les objets de cette collection et les enfants des roots AURORE_ADULTE_*. Il ne touche
  jamais aux autres stades ni aux autres dragons de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (0.5), avec un repère
  par segment (tangente, dos, côté) et un rayon qui varie le long du corps. CTRL, RADIUS_KEYS, HS
  (échelle de la tête), LEG_TH, nombres de feuilles et de fleurs sont en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire (le vert ne doit pas virer au kaki). Émission force 2 à 3 sur les feuilles
  lumineuses, fleurs, gemme et étincelles. Compatible Blender 4.x et 5.x (« Emission Color » ou
  « Emission »).
- Seed aléatoire fixe (1108) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 pas d'ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, crinière, bois)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
