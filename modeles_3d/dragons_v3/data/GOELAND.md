Goéland

Monde 4 · élément Vol · rareté Commun · archétype Rapide · morphologie
Wyvern

Goéland · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Goéland » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`GOELAND_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`GOELAND_BEBE\`. Préfixe tous les
> objets par \`GOELAND_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`GOELAND_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`GOELAND_BEBE_BODY_ROOT\`, \`GOELAND_BEBE_NECK_ROOT\`,
> \`GOELAND_BEBE_HEAD_ROOT\`, \`GOELAND_BEBE_TAIL_ROOT\`,
> \`GOELAND_BEBE_LEG_AR_ROOT\` (G et D), \`GOELAND_BEBE_WING_ROOT\` (G
> et D).
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
> \- \`Body\` (corps principal) : #8FB8E6
>
> \- \`BodyDark\` (genoux, ombres) : #566E8A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #6A88AA
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #759CCC
>
> \- \`Nostril\` (narines) : #405368
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F4F5F7
>
> \- \`Horn\` (base des cornes) : #F4F5F7
>
> \- \`HornTip\` (pointes des cornes, accents) : #F4F5F7
>
> \- \`Crest\` (sourcils, crêtes) : #4F7FC4
>
> \- \`Crest2\` (crête secondaire) : #8FB8E6
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4F7FC4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8FB8E6
>
> \- \`Claw\` (griffes) : #2A2A2E
>
> \- \`Eye\` (iris) : #2E6FC0 --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #E8C23A
>
> \- \`Extra2\` (éléments spéciaux (2)) : #A9ADB3
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
> \- Signes distinctifs (identiques aux trois stades) : wyvern à plumes
> façon oiseau de mer : bec jaune, houppe de plumes bleues, ailes-bras à
> plumes bleues aux pointes blanches, queue en éventail de plumes
> grises, pattes d\'oiseau.
>
> \- Description de ce stade : Petite wyvern à plumes, debout sur deux
> pattes d\'oiseau blanches à griffes noires. Tête blanche anguleuse,
> bec jaune court, houppe de plumes bleues, deux petites cornes
> blanches. Ailes-bras à plumes bleues aux pointes blanches. Queue en
> éventail de plumes grises. Yeux en éclats lumineux bleus.
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
> \- Ailes (feather) partant des omoplates en (0.65, 0.11, 2.6) : bras
> osseux jusqu\'au poignet (1.4, -0.11, 2.2) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.62.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
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

Goéland · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Goéland » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`GOELAND_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`GOELAND_JEUNE\`. Préfixe tous
> les objets par \`GOELAND_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`GOELAND_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`GOELAND_JEUNE_BODY_ROOT\`, \`GOELAND_JEUNE_NECK_ROOT\`,
> \`GOELAND_JEUNE_HEAD_ROOT\`, \`GOELAND_JEUNE_TAIL_ROOT\`,
> \`GOELAND_JEUNE_LEG_AR_ROOT\` (G et D), \`GOELAND_JEUNE_WING_ROOT\` (G
> et D).
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
> \- \`Body\` (corps principal) : #6FA0D6
>
> \- \`BodyDark\` (genoux, ombres) : #436080
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #52769E
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #5F8CC1
>
> \- \`Nostril\` (narines) : #324860
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F4F5F7
>
> \- \`Horn\` (base des cornes) : #F4F5F7
>
> \- \`HornTip\` (pointes des cornes, accents) : #F4F5F7
>
> \- \`Crest\` (sourcils, crêtes) : #4F7FC4
>
> \- \`Crest2\` (crête secondaire) : #8FB8E6
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4F7FC4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8FB8E6
>
> \- \`Claw\` (griffes) : #2A2A2E
>
> \- \`Eye\` (iris) : #2E6FC0 --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #E8C23A
>
> \- \`Extra2\` (éléments spéciaux (2)) : #A9ADB3
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
> \- Signes distinctifs (identiques aux trois stades) : wyvern à plumes
> façon oiseau de mer : bec jaune, houppe de plumes bleues, ailes-bras à
> plumes bleues aux pointes blanches, queue en éventail de plumes
> grises, pattes d\'oiseau.
>
> \- Description de ce stade : Élancé. Bec crochu jaune, houppe de
> plumes. Ailes-bras à plumes. Longue queue grise. Yeux bleus perçants.
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
> \- Ailes (feather) partant des omoplates en (0.58, 0.1, 3.07) : bras
> osseux jusqu\'au poignet (1.74, -0.24, 2.46) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.14.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
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

Goéland · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Goéland » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`GOELAND_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`GOELAND_ADULTE\`. Préfixe tous
> les objets par \`GOELAND_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`GOELAND_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`GOELAND_ADULTE_BODY_ROOT\`, \`GOELAND_ADULTE_NECK_ROOT\`,
> \`GOELAND_ADULTE_HEAD_ROOT\`, \`GOELAND_ADULTE_TAIL_ROOT\`,
> \`GOELAND_ADULTE_LEG_AR_ROOT\` (G et D), \`GOELAND_ADULTE_WING_ROOT\`
> (G et D).
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
> \- \`Body\` (corps principal) : #4F7FC4
>
> \- \`BodyDark\` (genoux, ombres) : #2F4C76
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #3A5E91
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #4975B4
>
> \- \`Nostril\` (narines) : #243958
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F4F5F7
>
> \- \`Horn\` (base des cornes) : #F4F5F7
>
> \- \`HornTip\` (pointes des cornes, accents) : #F4F5F7
>
> \- \`Crest\` (sourcils, crêtes) : #4F7FC4
>
> \- \`Crest2\` (crête secondaire) : #8FB8E6
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4F7FC4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8FB8E6
>
> \- \`Claw\` (griffes) : #2A2A2E
>
> \- \`Eye\` (iris) : #2E6FC0 --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #E8C23A
>
> \- \`Extra2\` (éléments spéciaux (2)) : #A9ADB3
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
> \- Signes distinctifs (identiques aux trois stades) : wyvern à plumes
> façon oiseau de mer : bec jaune, houppe de plumes bleues, ailes-bras à
> plumes bleues aux pointes blanches, queue en éventail de plumes
> grises, pattes d\'oiseau.
>
> \- Description de ce stade : Grand. Bec crochu, crête de plumes
> hérissée. Grandes ailes. Longue queue de plumes. Écailles bleues sur
> les pattes, griffes noires.
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
> \- Ailes (feather) partant des omoplates en (0.74, 0.11, 3.57) : bras
> osseux jusqu\'au poignet (2.22, -0.33, 2.79) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.75.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
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
