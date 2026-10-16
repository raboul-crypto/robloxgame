Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Mirage » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Mirage (Bébé, Ado, Adulte).
   Seul le dragon en haut à droite, nommé « Adulte Mirage », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Mirage = Terre, Épique, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Mirage : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : dragon oriental qui flotte, corps en S. Tête haute en avant, cou qui descend vers
  le poitrail, ventre, puis queue qui remonte derrière et s'enroule vers l'avant.
- Tête : museau long et carré avec narines, mâchoire distincte, yeux jaunes à pupille
  fendue, sourcils sévères, joyau cyan sur le front dans une couronne dorée, oreilles et
  pointes de joues, barbe sous le menton (5 éclats), deux longues moustaches qui retombent vers
  l'arrière, deux bois de cerf ramifiés (3 ramifications chacun) couleur os.
- Crinière : grand éventail d'éclats plats et pointus (or, or clair, brun) derrière la
  tête (3 rangées de 14 éclats), qui continue le long du cou. Ce sont des éclats larges, pas des piques fines.
- Corps : segments dorés, plaques de ventre crème bien séparées, bandes claires sur les
  flancs, écailles dorsales, cristaux cyan hexagonaux en grappes de 1 à 3 sur le dos,
  plastron doré avec une gemme cyan, petites ailes grises sur les épaules (3 éclats par côté).
- Pattes : 4 petites pattes qui pendent (avant au poitrail, arrière au bas du ventre), bracelets
  dorés foncés, 3 griffes blanches par patte.
- Queue : s'affine jusqu'à une touffe de 7 éclats dorés avec un cristal au bout, petites nageoires dorsales sur la fin.
- Rendu de rareté (Épique) : cristaux cyan émissifs (grappes sur le dos, joyau, gemme du plastron,
  bout de queue), ornements dorés (couronne du joyau, plastron, bracelets), 14 petits cristaux cyan qui flottent autour.
- Palette (hex, Principled BSDF, couleurs saturées en espace linéaire) : Gold #E7AD38 (corps, crâne, pattes),
  LightGold #F9CE61 (arête du museau, mâchoire, flancs, moustaches, oreilles), DarkGold #B37C30 (écailles du dos,
  bracelets, plastron, sourcils, couronne du joyau), Brown #895927 (éclats sombres de la crinière),
  Cream #EDDAAA (plaques du ventre), WingGrey #C4BCAA (petites ailes d'épaule), Antler #B3A286 (bois),
  Cyan #3FEDE7 émissif #3FF9ED à 3.0 (cristaux, joyau, gemme), EyeWhite #F6F6F1, Iris #FDE561, Black #302727
  (pupilles, narines), Claw #F9F7EF (griffes).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de
  sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 13 000 triangles maximum après modificateurs (le script en fait environ 12 042, vise 80-95 %). Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, segments, ventre, pattes), jamais sur les éclats, griffes et cristaux. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty MIRAGE_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT,
  LEGS_ROOT, TAIL_ROOT. Chaque pièce est parentée au bon root. Les pièces de la tête sont
  placées en coordonnées locales de HEAD_ROOT.
- Tout dans une collection « MIRAGE_ADULTE ». Le script est relançable : au début, il
  supprime uniquement les objets de cette collection et les enfants des roots
  MIRAGE_ADULTE_*. Il ne touche jamais aux autres modèles de la scène (Bébé, Ado).
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long du corps.
  Les points de contrôle et les rayons sont des listes faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour.
  Couleurs saturées en espace linéaire (le doré ne doit pas virer au beige). Cristaux
  cyan émissifs. Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (1115) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 14 petits cristaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, point le plus bas à Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, épaisseur de la crinière, taille des
   cristaux) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.