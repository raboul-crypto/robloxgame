Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Neptyr » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Adulte Neptyr » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Neptyr = Eau, Légendaire, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur l'Adulte Neptyr : pose,
proportions, chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : long dragon oriental d'eau majestueux qui flotte en vague : tête haute en avant, cou qui descend vers le poitrail, dos qui remonte, creux, puis queue qui se redresse derrière avec sa grande nageoire.
- Tête : museau long et carré avec arête claire, mâchoire distincte, narines, yeux cyan émissifs à pupille fendue, sourcils sévères (angle 14), joyau cyan (grand) dans un diadème doré, nageoires-oreilles à 4 rayons, 3 crocs par côté, barbe de 5 éclats, deux longues moustaches lumineuses.
- Crinière et bois : grand éventail de 3 rangées de 18 éclats translucides bleu ciel derrière la tête, qui continue le long du cou ; bois dorés métalliques ramifiés (4 ramifications chacun) ; double rangée de pics dorés sur le dos.
- Corps : segments bleu nuit biseautés (environ 0.6 m de long), plaques de ventre turquoise bien séparées, bandes claires sur les flancs, spirales et runes cyan émissives tous les 6 segments, bandes d'or tous les 8 segments, nageoire dorsale continue (plaques translucides et rayons), plastron doré avec gemme cyan, épaulières dorées, 2 éclats d'aileron translucide par épaule.
- Ailes / nageoires : pas d'ailes (oriental). Nageoire dorsale continue sur le dos et la queue, nageoires-oreilles sur la tête, petits ailerons aux coudes.
- Pattes : 4 pattes qui pendent (avant au poitrail, arrière au bas du ventre), épaule et cuisse en bloc biseauté, avant-bras, bracelet doré, aileron de coude à 3 rayons, pied à 3 doigts et 3 griffes dorées claires.
- Queue : s'affine jusqu'à un collier doré, un cristal cyan, 6 pétales d'or, un anneau runique et une grande nageoire plumeuse translucide de 9 plumes.
- Rendu de rareté (Légendaire) : rendu Légendaire complet : or métallique (bois, diadème, plastron, épaulières, bracelets, bandes, pics, pétales), aura derrière la tête (16 pointes cyan sur un anneau de 2.7 m de rayon, avec anneau doré), runes et spirales cyan émissives sur tout le corps, yeux, joyau et gemmes émissifs, moustaches lumineuses, 16 cristaux et gouttes flottants et 4 anneaux runiques en orbite.
- Palette (hex, Principled BSDF, couleurs saturées en espace linéaire) : Body #1F4FA3 (corps, crâne, pattes),
  ScaleDark #143570 (écailles du dos, mâchoire), ScaleLight #4A86D0 (arête du museau, bandes des flancs),
  Belly #8ED6D0 (plaques du ventre, menton), Gold #E8B93C métallique 0.9 (bois, diadème, plastron, bracelets),
  Fin #9FDDF5 translucide alpha 0.55 (crinière, nageoires), FinRay #6EC1EC (rayons, sourcils),
  Glow #3FE0FF émissif #3FE0FF à 3.0 (runes, spirales, yeux, gemmes), Whisker #9FE8FF émissif #7FEBFF à 2.0
  (moustaches), EyeWhite #F2F2F2, Black #0A0F1E (pupilles, narines), Claw #F4DC8A métallique 0.8 (griffes).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 15,000 triangles maximum après modificateurs (le script en fait environ 11,132, vise 70-100 %). Biseau à 1 segment au plus, et
  seulement sur les gros blocs (segments, crâne, museau, ventre, épaules et cuisses), jamais sur les éclats, griffes et cristaux. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty NEPTYR_ADULTE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT,
  LEGS_ROOT, TAIL_ROOT. Chaque pièce est parentée au bon root. Les pièces de la tête sont
  placées en coordonnées locales de HEAD_ROOT. Les FX flottants sont parentés au MASTER.
- Tout dans une collection « NEPTYR_ADULTE ». Le script est relançable : au début, il
  supprime uniquement les objets de cette collection et les enfants des roots
  NEPTYR_ADULTE_*. Il ne touche jamais aux autres modèles de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (segments d'environ 0.6 m), avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long du corps.
  Les points de contrôle (CTRL) et les rayons (RADIUS_KEYS) sont des listes faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour.
  Couleurs saturées en espace linéaire. Runes, spirales, yeux et gemmes émissifs.
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (3303) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les cristaux, gouttes et anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, point le plus bas à Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
