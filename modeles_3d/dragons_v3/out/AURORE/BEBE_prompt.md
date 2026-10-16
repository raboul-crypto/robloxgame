Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Aurore » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Aurore (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Aurore », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Aurore = Plante, Épique, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Aurore : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : petit dragon oriental mignon debout sur ses 4 pattes, cou court qui porte la tête au-dessus
  du poitrail, corps de serpent court et arrondi, queue qui remonte derrière.
- Tête : grosse tête carrée (environ 35 % de la hauteur) en wedge bien biseauté, museau court avec
  arête lime, mâchoire crème, ligne de bouche, 2 narines. Très grands yeux brillants : blanc, grand iris
  vert vif, grande pupille ronde noire et 2 reflets blancs. Pas de crocs. Oreilles-feuilles, 2 feuilles
  de joue par côté, barbe de 2 feuilles, 1 éclat de couronne par côté.
- Signe distinctif : une grande pousse lumineuse au sommet du crâne (tige vert foncé, 2 grandes
  feuilles lime émissives, un bourgeon), entre deux petites cornes beige (3 barres) ; une petite fleur
  de cerisier rose (5 pétales lumineux + coeur doré) au bout de chaque corne.
- Moustaches : courtes moustaches dorées (2 barres) qui s'écartent du museau.
- Crinière : collerette de 2 anneaux de feuilles en losange (9 et 7) vertes, une partie lime
  lumineuse, 2 fleurs roses dedans ; 2 feuilles par segment le long du cou.
- Corps : segments verts biseautés et généreux, plaques de ventre crème séparées, bandes de flanc
  lime / vert, écailles-feuilles un segment sur deux, plaque dorsale vert foncé, crête de feuilles un
  segment sur deux, petite liane vert foncé avec feuilles et fleurs roses sur un flanc.
- Pattes : 4 pattes courtes et épaisses : épaule en wedge, 2 os, feuille au coude, gros pied,
  3 doigts + 3 petites griffes crème. Pas de bracelet.
- Queue : courte, anneau brun au bout et touffe de 3 feuilles + une grande feuille lime lumineuse.
- Rendu de rareté (Épique, une touche) : pousse et quelques feuilles lumineuses, fleurs roses
  lumineuses, iris légèrement lumineux, 8 FX flottants (feuilles, étincelles dorées, étoiles roses).
  Pas encore d'or massif, ni plastron, ni aura.
- Palette (hex, identique aux 3 stades) : Body #6CC02E, BodyScale #4FA524, BodyDark #2C7A1E,
  LeafLight #A8E64A / LeafMid #5DBB2C / LeafDark #2F8A24, Belly #E6D49A, Horn #D9BF8A,
  Gold #F0B72E (moustaches), Brown #7B4A22 (anneau de queue), Claw #F6EEDA, EyeWhite #F4F4EA,
  Black #0B0F08, émissifs : Iris #9BE03C (1.2), LeafGlow #6EE23A (2.4), PinkGlow #FF8EBE (2.2),
  Spark #FFD25A (2.8).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Feuilles en losanges plats, pétales en éclats plats.

CONTRAINTES TECHNIQUES
- Budget : 5 000 triangles maximum après modificateurs (vise 75-95 %). Biseau à 1 segment au plus,
  et seulement sur les gros blocs, jamais sur les feuilles, pétales, griffes ou petites pièces.
  Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty AURORE_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT,
  TAIL_ROOT. Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées
  locales de HEAD_ROOT.
- Tout dans une collection « AURORE_BEBE ». Le script est relançable : au début, il supprime
  uniquement les objets de cette collection et les enfants des roots AURORE_BEBE_*. Il ne touche
  jamais aux autres stades ni aux autres dragons de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (0.45), avec un
  repère par segment et un rayon qui varie le long du corps. CTRL, RADIUS_KEYS, HS, LEG_TH et les
  nombres de feuilles / fleurs sont en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission sur la pousse, les feuilles lumineuses et les fleurs.
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (1108) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 8 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 pas d'ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, yeux, pousse)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
