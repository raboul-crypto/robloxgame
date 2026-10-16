Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Brindille » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Brindille (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Brindille », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Brindille = Plante, Commun, Rapide, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Brindille : pose, proportions, chaque
élément de la tête, du corps, des ailes-feuilles et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Adulte puissant et noble, grand serpent dressé en S (cou de 6,6 m), tête haute et regardant vers l'avant, anneaux massifs au sol, très grandes ailes-feuilles dressées en V derrière le cou.
- Tête : crâne carré en wedge, museau en bloc (long) avec arête claire, plaque de bois sur le front, mâchoire crème distincte et ligne de bouche sombre, 2 narines noires. Yeux latéraux : blanc, iris vert avec pupille fendue noire et sourcils d'écorce sévères.. 3 crocs crème par côté. Oreilles en feuille, 3 feuilles de joue par côté, barbe de 4 feuilles sous le menton, collerette de 12 + 10 en 2 anneaux feuilles derrière le crâne.
- Signe distinctif : des bois de brindilles beiges imposants : 1 barre de 4 maillons, 3 branches et un rameau secondaire par branche, petit rameau sur le front (ANT_K 1.0), un petit bourgeon vert au bout de chaque brindille, et une pousse centrale (5 feuilles) entre les bois. Une liane brune (barres brunes alternées, petites feuilles) s'enroule en spirale serrée autour du corps.
- Corps : serpent en S fait de segments de bois (2 tons alternés), un anneau d'écorce sombre à chaque jointure, veines de bois claires et sombres sur chaque segment, plaques d'écorce brune sur le dos (un segment sur deux), plaques de ventre crème bien séparées, plastron crème large avec bavoir de 5 feuilles, 4 feuilles d'épaulière par côté + plaque d'écorce en wedge à la base des ailes, crête de feuilles sur le dos, feuilles sur tous les flancs (plus denses sur la poitrine).
- Ailes : 2 très grandes ailes-feuilles de 8,5 m (WING_L), en losange nervuré : bord et nervure centrale vert foncé, 3 paires de nervures secondaires, membrane lime, grande pointe crème au sommet et pointe latérale, articulation en bois à la base.
- Pattes : aucune (amphiptère). 6 touffes de feuilles posées au sol autour des anneaux, parentées à LEGS_ROOT.
- Queue : le corps s'enroule en anneau décroissant puis la queue se redresse au centre, anneau d'écorce puis 3 grandes feuilles croisées (lime, moyen, foncé) de 2,6 m.
- Rendu de rareté : Commun : silhouette propre et lisible, détails de bois, d'écorce et de feuilles à pleine taille. 14 feuilles flottantes. 3 familles de couleurs (bois, crème, vert), aucune émission, un seul signe fort (bois + liane).
- Palette (hex, Principled BSDF) :
  Body #C99A5B (corps, bois tan), BodyDark #B08044 (segments alternés, dessus du museau), BodyLight #E2BE82 (arête du museau, veines claires),
  Bark #7A4E26 (liane, plaques d'écorce, sourcils), BarkDark #4F3017 (anneaux de jointure, bouche, narines), Belly #F1E6BC (ventre en plaques, mâchoire, plastron),
  Horn #D9B880 (bois de brindilles), LeafLight #A9DC45 / LeafMid #5DB82C / LeafDark #2F8A2A (feuilles), Bud #8BE03A (bourgeons au bout des bois),
  Membrane #86C640 (membrane des ailes-feuilles), WingBone #3C8426 (bord et nervure centrale), WingVein #5FAA30 (nervures secondaires),
  Claw #F6EEDA (crocs, pointes d'aile), EyeWhite #F4F4EA, Iris #6EDB35 (très faible lueur, strength 0.8), Black #0B0F08 (pupilles, narines).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les feuilles sont des losanges plats ; le corps est fait de planches de bois (blocs biseautés).

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du cou et du corps), jamais sur les feuilles/éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRINDILLE_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (LEGS_ROOT ne porte que les touffes de feuilles posées au sol : le dragon n'a pas de pattes).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRINDILLE_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRINDILLE_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le corps est un long serpent : une seule courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie par clés. Les points de contrôle (cou dressé en S, descente, anneau au sol, queue qui remonte au centre), RADIUS_KEYS, ZB, NECK_H, COIL_R, HEAD_SCALE, WING_L... sont des variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun), sauf une très faible lueur sur l'iris. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1103) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 feuilles en losange flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes-feuilles, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, bois, liane))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
