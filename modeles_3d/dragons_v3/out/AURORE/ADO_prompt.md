Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Aurore » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Aurore (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Aurore », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Aurore = Plante, Épique, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Aurore : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : jeune dragon oriental debout sur ses 4 pattes, cou dressé, tête haute regardant devant,
  corps de serpent presque horizontal, queue qui remonte derrière et se relève à la verticale.
- Tête : crâne en wedge, museau carré moyen avec arête lime, mâchoire crème, ligne de bouche,
  2 narines, yeux latéraux (blanc, iris vert vif, pupille fendue), sourcils vert foncé, 2 petits crocs
  crème par côté, oreilles-feuilles, 2 feuilles de joue par côté, barbe de 3 feuilles, 2 éclats
  dorés de couronne par côté.
- Bois : bois beige à 2 pointes (3 barres + 2 pointes de chaque côté), 2 feuilles lumineuses par
  bois, 2 fleurs de cerisier roses lumineuses (5 pétales + coeur doré) au bout des pointes. Entre les
  bois, la pousse lumineuse (tige + 2 feuilles lime émissives + bourgeon).
- Moustaches : moustaches dorées moyennes (3 barres) qui s'écartent puis remontent vers l'arrière.
- Crinière : collerette de 2 anneaux de feuilles en losange (11 et 9), vertes avec beaucoup de
  feuilles lime lumineuses et quelques dorées, 4 fleurs roses dedans ; elle continue sur le cou
  (3 feuilles par segment + éclats latéraux).
- Corps : segments verts biseautés, plaques de ventre crème séparées, bandes de flanc lime / vert,
  nervure lime émissive sur chaque flanc, écailles-feuilles un segment sur deux, plaque dorsale
  vert foncé, crête de feuilles en losange à chaque segment (éclats dorés tous les 4), liane vert
  foncé fleurie de roses sur un flanc. Petit plastron brun avec plaque dorée et gemme verte
  émissive, petites épaulières brunes à 2 plumes dorées.
- Pattes : 4 pattes posées au sol, plus longues que celles du bébé : épaule en wedge, 2 os,
  bracelet doré + anneau or foncé, feuille au coude, pied, 3 doigts + 3 vraies griffes crème.
- Queue : bandes dorées tous les 3 segments, anneau doré au bout, touffe de 4 feuilles et une
  grande feuille lime lumineuse.
- Rendu de rareté (Épique, à mi-puissance) : feuilles et pousse lumineuses, nervures lime, fleurs
  roses lumineuses (bois, crinière, liane), aura de 6 feuilles roses émissives derrière la crinière,
  ornements dorés plus petits que sur l'adulte, 10 FX flottants (feuilles, étincelles dorées, étoiles
  roses).
- Palette (hex, identique aux 3 stades) : Body #6CC02E, BodyScale #4FA524, BodyDark #2C7A1E,
  LeafLight #A8E64A / LeafMid #5DBB2C / LeafDark #2F8A24, Belly #E6D49A, Horn #D9BF8A,
  Gold #F0B72E et DarkGold #B87A16 (métal 0.5), Brown #7B4A22, Claw #F6EEDA, EyeWhite #F4F4EA,
  Black #0B0F08, émissifs : Iris #9BE03C (1.2), LeafGlow #6EE23A (2.4), PinkGlow #FF8EBE (2.2),
  Gem #74FF5A (3.0), Spark #FFD25A (2.8).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Feuilles en losanges plats, pétales en éclats plats.

CONTRAINTES TECHNIQUES
- Budget : 8 500 triangles maximum après modificateurs (vise 80-95 %). Biseau à 1 segment au plus,
  et seulement sur les gros blocs, jamais sur les feuilles, pétales, griffes ou petites pièces.
  Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty AURORE_ADO_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT,
  TAIL_ROOT. Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées
  locales de HEAD_ROOT.
- Tout dans une collection « AURORE_ADO ». Le script est relançable : au début, il supprime
  uniquement les objets de cette collection et les enfants des roots AURORE_ADO_*. Il ne touche
  jamais aux autres stades ni aux autres dragons de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (0.5), avec un repère
  par segment et un rayon qui varie le long du corps. CTRL, RADIUS_KEYS, HS, LEG_TH et les nombres de
  feuilles / fleurs sont en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission force 2 à 3 sur les feuilles lumineuses, fleurs, gemme et étincelles.
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (1108) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 10 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 pas d'ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, crinière, bois)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
