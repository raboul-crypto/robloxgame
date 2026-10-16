Braisillon

Monde 2 · élément Feu · rareté Commun · archétype Rapide · morphologie
Wyvern

Braisillon · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Braisillon » au stade BÉBÉ pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRAISILLON_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRAISILLON_BEBE\`. Préfixe tous
> les objets par \`BRAISILLON_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRAISILLON_BEBE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRAISILLON_BEBE_BODY_ROOT\`, \`BRAISILLON_BEBE_NECK_ROOT\`,
> \`BRAISILLON_BEBE_HEAD_ROOT\`, \`BRAISILLON_BEBE_TAIL_ROOT\`,
> \`BRAISILLON_BEBE_LEG_AR_ROOT\` (G et D),
> \`BRAISILLON_BEBE_WING_ROOT\` (G et D).
>
> \- Fonctions primitives (construites avec \`bmesh\`, sans \`bpy.ops\`)
> :
>
> 1\. \`add_box()\` : cube dont l\'échelle est appliquée au maillage
> AVANT d\'ajouter un modificateur \`BEVEL\` (largeur 0.04, 2 segments,
> limitée à 30 % de la plus petite dimension) pour des biseaux
> uniformes.
>
> 2\. \`add_pyramid()\` : cône à 4 sommets tourné de 45° sur Z pour
> aligner les faces sur X/Y, pointe vers +Z, puis rotation finale et
> position ; léger biseau.
>
> 3\. \`add_prism()\` : prisme à n faces (galets, disques, perles).
>
> 4\. \`add_scale()\` (vraies écailles) : prisme triangulaire plat
> construit avec \`bmesh\`, pointe vers l\'arrière (+Y local), avec un
> lacet d\'environ 14° pour que l\'avant s\'enfonce dans la peau et que
> seule la pointe ressorte, en quinconce.
>
> 5\. \`add_plate()\` : plaque fine triangulée + modificateur
> \`SOLIDIFY\` (membranes, feuilles, nageoires).
>
> \- Pièces symétriques construites dans des boucles \`for side in (-1,
> 1):\` avec le suffixe G/D.
>
> \- À la fin : mise à l\'échelle du MASTER pour que le dragon mesure
> exactement 1 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #D9452B
>
> \- \`BodyDark\` (genoux, ombres) : #82291A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #A13320
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #CD4B25
>
> \- \`Nostril\` (narines) : #621F13
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F2D3A8
>
> \- \`Horn\` (base des cornes) : #2E2622
>
> \- \`HornTip\` (pointes des cornes, accents) : #2E2622
>
> \- \`Crest\` (sourcils, crêtes) : #F07A1E
>
> \- \`Crest2\` (crête secondaire) : #FFC23A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #F07A1E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F07A1E ---
> translucide
>
> \- \`Claw\` (griffes) : #2E2622
>
> \- \`Eye\` (iris) : #FFB52E --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFB52E --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Wyvern : deux pattes arrière seulement, les ailes servent de bras
> (griffes au poignet), posture penchée en avant.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : points lumineux
> de braises sur le corps ; couronne d\'épines orange avec une flamme au
> centre ; flamme au bout de la queue ; ailes-bras orange.
>
> \- Description de ce stade : Petite wyvern debout sur deux pattes.
> Rouge vermillon, ventre crème. Petits points lumineux jaune-orange
> (braises) sur les joues, le dos et les cuisses. Couronne d\'épines
> orange sur la tête, avec une épine centrale en forme de flamme.
> Petites ailes-bras orange. Flamme vive au bout de la queue. Yeux en
> éclats lumineux bruns.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.5, 1.45, 1.15) centré en (0, 0, 1.82), bassin (1.33,
> 1.25, 1.02) centré en (0, 1, 1.76) (tout le tronc incliné de 24° vers
> le haut autour des hanches, posture de wyvern).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (3 rangées).
>
> \- Tête : crâne (1.6, 1.6, 1.4) centré en (0, -0.86, 4.24), museau
> allongé x1, cou de 3 segments.
>
> \- Pattes : 2 pattes arrière seulement, épaisseur 0.54, pieds à plat
> au sol (Z = 0) avec 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 8 segments de (0, 1.55, 1.47) à (0, 4.82, 1.66), qui
> s\'affinent (largeur 1.1 → 0.41) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (flame_edge) partant des omoplates en (0.65, 0.11, 2.6) :
> bras osseux jusqu\'au poignet (1.4, -0.11, 2.2) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.62.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
>
> \- Motifs (embers_glow, lines_glow) répartis sur les flancs du torse
> et de la queue, en plaques très fines posées sur la peau.
>
> \- Toutes les pièces s\'interpénètrent franchement (chevauchement
> d\'au moins 0.15) : aucun vide entre cou, torse, pattes, pieds et
> queue.
>
> \### 5. POSE
>
> Pose neutre et symétrique pour pouvoir le riguer ensuite : debout (ou
> posé/enroulé selon la morphologie), gueule fermée, regard vers
> l\'avant, ailes ou nageoires à demi ouvertes.
>
> Ne tronque aucune partie du code. Fournis le script Python complet et
> directement fonctionnel.

Braisillon · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Braisillon » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRAISILLON_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRAISILLON_JEUNE\`. Préfixe tous
> les objets par \`BRAISILLON_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRAISILLON_JEUNE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRAISILLON_JEUNE_BODY_ROOT\`, \`BRAISILLON_JEUNE_NECK_ROOT\`,
> \`BRAISILLON_JEUNE_HEAD_ROOT\`, \`BRAISILLON_JEUNE_TAIL_ROOT\`,
> \`BRAISILLON_JEUNE_LEG_AR_ROOT\` (G et D),
> \`BRAISILLON_JEUNE_WING_ROOT\` (G et D).
>
> \- Fonctions primitives (construites avec \`bmesh\`, sans \`bpy.ops\`)
> :
>
> 1\. \`add_box()\` : cube dont l\'échelle est appliquée au maillage
> AVANT d\'ajouter un modificateur \`BEVEL\` (largeur 0.04, 2 segments,
> limitée à 30 % de la plus petite dimension) pour des biseaux
> uniformes.
>
> 2\. \`add_pyramid()\` : cône à 4 sommets tourné de 45° sur Z pour
> aligner les faces sur X/Y, pointe vers +Z, puis rotation finale et
> position ; léger biseau.
>
> 3\. \`add_prism()\` : prisme à n faces (galets, disques, perles).
>
> 4\. \`add_scale()\` (vraies écailles) : prisme triangulaire plat
> construit avec \`bmesh\`, pointe vers l\'arrière (+Y local), avec un
> lacet d\'environ 14° pour que l\'avant s\'enfonce dans la peau et que
> seule la pointe ressorte, en quinconce.
>
> 5\. \`add_plate()\` : plaque fine triangulée + modificateur
> \`SOLIDIFY\` (membranes, feuilles, nageoires).
>
> \- Pièces symétriques construites dans des boucles \`for side in (-1,
> 1):\` avec le suffixe G/D.
>
> \- À la fin : mise à l\'échelle du MASTER pour que le dragon mesure
> exactement 1.8 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #B5472E
>
> \- \`BodyDark\` (genoux, ombres) : #6D2B1C
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #863522
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #B44D27
>
> \- \`Nostril\` (narines) : #512015
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F2D3A8
>
> \- \`Horn\` (base des cornes) : #2E2622
>
> \- \`HornTip\` (pointes des cornes, accents) : #2E2622
>
> \- \`Crest\` (sourcils, crêtes) : #F07A1E
>
> \- \`Crest2\` (crête secondaire) : #FFC23A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #F07A1E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F07A1E ---
> translucide
>
> \- \`Claw\` (griffes) : #2E2622
>
> \- \`Eye\` (iris) : #FFB52E --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFB52E --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Wyvern : deux pattes arrière seulement, les ailes servent de bras
> (griffes au poignet), posture penchée en avant.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : points lumineux
> de braises sur le corps ; couronne d\'épines orange avec une flamme au
> centre ; flamme au bout de la queue ; ailes-bras orange.
>
> \- Description de ce stade : Rouge brique, debout. Cornes noires
> recourbées, épines orange en flammes. Veines lumineuses sur le corps.
> Ailes orange translucides. Flamme au bout de la queue. Yeux orange,
> regard vif.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.35, 1.74, 1.15) centré en (0, 0, 2.2), bassin (1.2,
> 1.5, 1.02) centré en (0, 1.2, 2.14) (tout le tronc incliné de 24° vers
> le haut autour des hanches, posture de wyvern).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.31, 1.31, 1.15) centré en (0, -1.2, 5.02), museau
> allongé x1.3, cou de 4 segments.
>
> \- Pattes : 2 pattes arrière seulement, épaisseur 0.45, pieds à plat
> au sol (Z = 0) avec 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 10 segments de (0, 1.86, 1.79) à (0, 6.44, 2.07), qui
> s\'affinent (largeur 0.99 → 0.35) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (flame_edge) partant des omoplates en (0.58, 0.1, 3.07) :
> bras osseux jusqu\'au poignet (1.74, -0.24, 2.46) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.14.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
>
> \- Motifs (embers_glow, lines_glow) répartis sur les flancs du torse
> et de la queue, en plaques très fines posées sur la peau.
>
> \- Toutes les pièces s\'interpénètrent franchement (chevauchement
> d\'au moins 0.15) : aucun vide entre cou, torse, pattes, pieds et
> queue.
>
> \### 5. POSE
>
> Pose neutre et symétrique pour pouvoir le riguer ensuite : debout (ou
> posé/enroulé selon la morphologie), gueule fermée, regard vers
> l\'avant, ailes ou nageoires à demi ouvertes.
>
> Ne tronque aucune partie du code. Fournis le script Python complet et
> directement fonctionnel.

Braisillon · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Braisillon » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRAISILLON_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRAISILLON_ADULTE\`. Préfixe
> tous les objets par \`BRAISILLON_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRAISILLON_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRAISILLON_ADULTE_BODY_ROOT\`, \`BRAISILLON_ADULTE_NECK_ROOT\`,
> \`BRAISILLON_ADULTE_HEAD_ROOT\`, \`BRAISILLON_ADULTE_TAIL_ROOT\`,
> \`BRAISILLON_ADULTE_LEG_AR_ROOT\` (G et D),
> \`BRAISILLON_ADULTE_WING_ROOT\` (G et D).
>
> \- Fonctions primitives (construites avec \`bmesh\`, sans \`bpy.ops\`)
> :
>
> 1\. \`add_box()\` : cube dont l\'échelle est appliquée au maillage
> AVANT d\'ajouter un modificateur \`BEVEL\` (largeur 0.04, 2 segments,
> limitée à 30 % de la plus petite dimension) pour des biseaux
> uniformes.
>
> 2\. \`add_pyramid()\` : cône à 4 sommets tourné de 45° sur Z pour
> aligner les faces sur X/Y, pointe vers +Z, puis rotation finale et
> position ; léger biseau.
>
> 3\. \`add_prism()\` : prisme à n faces (galets, disques, perles).
>
> 4\. \`add_scale()\` (vraies écailles) : prisme triangulaire plat
> construit avec \`bmesh\`, pointe vers l\'arrière (+Y local), avec un
> lacet d\'environ 14° pour que l\'avant s\'enfonce dans la peau et que
> seule la pointe ressorte, en quinconce.
>
> 5\. \`add_plate()\` : plaque fine triangulée + modificateur
> \`SOLIDIFY\` (membranes, feuilles, nageoires).
>
> \- Pièces symétriques construites dans des boucles \`for side in (-1,
> 1):\` avec le suffixe G/D.
>
> \- À la fin : mise à l\'échelle du MASTER pour que le dragon mesure
> exactement 3 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #8A2A1C
>
> \- \`BodyDark\` (genoux, ombres) : #531911
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #661F15
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #97391A
>
> \- \`Nostril\` (narines) : #3E130D
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F2D3A8
>
> \- \`Horn\` (base des cornes) : #2E2622
>
> \- \`HornTip\` (pointes des cornes, accents) : #2E2622
>
> \- \`Crest\` (sourcils, crêtes) : #F07A1E
>
> \- \`Crest2\` (crête secondaire) : #FFC23A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #F07A1E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F07A1E ---
> translucide
>
> \- \`Claw\` (griffes) : #2E2622
>
> \- \`Eye\` (iris) : #FFB52E --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFB52E --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Wyvern : deux pattes arrière seulement, les ailes servent de bras
> (griffes au poignet), posture penchée en avant.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : points lumineux
> de braises sur le corps ; couronne d\'épines orange avec une flamme au
> centre ; flamme au bout de la queue ; ailes-bras orange.
>
> \- Description de ce stade : Rouge sombre, musclé. Cornes noires,
> lignes de lave lumineuses sur les écailles. Grandes ailes orange
> flamboyantes. Flamme au bout de la queue. Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.73, 2.17, 1.29) centré en (0, 0, 2.52), bassin
> (1.53, 1.88, 1.14) centré en (0, 1.5, 2.46) (tout le tronc incliné de
> 24° vers le haut autour des hanches, posture de wyvern).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.44, 1.44, 1.26) centré en (0, -1.41, 5.67), museau
> allongé x1.42, cou de 5 segments.
>
> \- Pattes : 2 pattes arrière seulement, épaisseur 0.66, pieds à plat
> au sol (Z = 0) avec 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 12 segments de (0, 2.34, 2.03) à (0, 7.73, 2.36), qui
> s\'affinent (largeur 1.27 → 0.43) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (flame_edge) partant des omoplates en (0.74, 0.11, 3.57) :
> bras osseux jusqu\'au poignet (2.22, -0.33, 2.79) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.75.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
>
> \- Motifs (embers_glow, lines_glow) répartis sur les flancs du torse
> et de la queue, en plaques très fines posées sur la peau.
>
> \- Toutes les pièces s\'interpénètrent franchement (chevauchement
> d\'au moins 0.15) : aucun vide entre cou, torse, pattes, pieds et
> queue.
>
> \### 5. POSE
>
> Pose neutre et symétrique pour pouvoir le riguer ensuite : debout (ou
> posé/enroulé selon la morphologie), gueule fermée, regard vers
> l\'avant, ailes ou nageoires à demi ouvertes.
>
> Ne tronque aucune partie du code. Fournis le script Python complet et
> directement fonctionnel.
