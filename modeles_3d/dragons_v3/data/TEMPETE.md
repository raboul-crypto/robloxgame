Tempête

Monde 4 · élément Vol · rareté Épique · archétype Brute · morphologie
Wyvern

Tempête · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Tempête » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TEMPETE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TEMPETE_BEBE\`. Préfixe tous les
> objets par \`TEMPETE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TEMPETE_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`TEMPETE_BEBE_BODY_ROOT\`, \`TEMPETE_BEBE_NECK_ROOT\`,
> \`TEMPETE_BEBE_HEAD_ROOT\`, \`TEMPETE_BEBE_TAIL_ROOT\`,
> \`TEMPETE_BEBE_LEG_AR_ROOT\` (G et D), \`TEMPETE_BEBE_WING_ROOT\` (G
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
> \- \`Body\` (corps principal) : #4A5361
>
> \- \`BodyDark\` (genoux, ombres) : #2C323A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #373D48
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #6A707B
>
> \- \`Nostril\` (narines) : #21252C
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EEF1F4
>
> \- \`HornTip\` (pointes des cornes, accents) : #2B2F36
>
> \- \`Crest\` (sourcils, crêtes) : #EEF1F4
>
> \- \`Crest2\` (crête secondaire) : #A8B1BC
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4A5361
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A5361
>
> \- \`Claw\` (griffes) : #2B2F36
>
> \- \`Eye\` (iris) : #7FC8F0 --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8B1BC
>
> \- \`Extra\` (éléments spéciaux) : #EEF1F4
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
> \- Signes distinctifs (identiques aux trois stades) : crinière de
> nuage gris-blanc ; ailes-bras larges gris orage aux bords effilochés
> en nuage ; spirales de vent claires sur le corps ; pas d\'éclairs (la
> Foudre est un élément futur).
>
> \- Description de ce stade : Petite wyvern debout sur deux pattes.
> Gris orage, ventre gris clair. Petite crinière de nuage blanc en
> facettes sur la tête et la nuque. Ailes-bras larges dont les bords
> s\'effilochent en petits nuages. Spirales de vent claires sur les
> flancs. Queue terminée par une touffe de nuage. Yeux en éclats
> lumineux bleu glacier.
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
> \- Ailes (cloud) partant des omoplates en (0.65, 0.11, 2.6) : bras
> osseux jusqu\'au poignet (1.4, -0.11, 2.2) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.62.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
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

Tempête · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Tempête » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TEMPETE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TEMPETE_JEUNE\`. Préfixe tous
> les objets par \`TEMPETE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TEMPETE_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`TEMPETE_JEUNE_BODY_ROOT\`, \`TEMPETE_JEUNE_NECK_ROOT\`,
> \`TEMPETE_JEUNE_HEAD_ROOT\`, \`TEMPETE_JEUNE_TAIL_ROOT\`,
> \`TEMPETE_JEUNE_LEG_AR_ROOT\` (G et D), \`TEMPETE_JEUNE_WING_ROOT\` (G
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
> \- \`Body\` (corps principal) : #3D4553
>
> \- \`BodyDark\` (genoux, ombres) : #252932
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #2D333D
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #616771
>
> \- \`Nostril\` (narines) : #1B1F25
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EEF1F4
>
> \- \`HornTip\` (pointes des cornes, accents) : #2B2F36
>
> \- \`Crest\` (sourcils, crêtes) : #EEF1F4
>
> \- \`Crest2\` (crête secondaire) : #A8B1BC
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4A5361
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A5361
>
> \- \`Claw\` (griffes) : #2B2F36
>
> \- \`Eye\` (iris) : #7FC8F0 --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8B1BC
>
> \- \`Extra\` (éléments spéciaux) : #EEF1F4
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
> \- Signes distinctifs (identiques aux trois stades) : crinière de
> nuage gris-blanc ; ailes-bras larges gris orage aux bords effilochés
> en nuage ; spirales de vent claires sur le corps ; pas d\'éclairs (la
> Foudre est un élément futur).
>
> \- Description de ce stade : Plus costaud, debout. Crinière de nuage
> plus grande. Ailes larges à bords nuageux, griffes au poignet.
> Spirales de vent. Crocs, regard dur.
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
> \- Ailes (cloud) partant des omoplates en (0.58, 0.1, 3.07) : bras
> osseux jusqu\'au poignet (1.74, -0.24, 2.46) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.14.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
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

Tempête · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Tempête » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TEMPETE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TEMPETE_ADULTE\`. Préfixe tous
> les objets par \`TEMPETE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TEMPETE_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`TEMPETE_ADULTE_BODY_ROOT\`, \`TEMPETE_ADULTE_NECK_ROOT\`,
> \`TEMPETE_ADULTE_HEAD_ROOT\`, \`TEMPETE_ADULTE_TAIL_ROOT\`,
> \`TEMPETE_ADULTE_LEG_AR_ROOT\` (G et D), \`TEMPETE_ADULTE_WING_ROOT\`
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
> \- \`Body\` (corps principal) : #323845
>
> \- \`BodyDark\` (genoux, ombres) : #1E2229
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #252933
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #595E68
>
> \- \`Nostril\` (narines) : #16191F
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EEF1F4
>
> \- \`HornTip\` (pointes des cornes, accents) : #2B2F36
>
> \- \`Crest\` (sourcils, crêtes) : #EEF1F4
>
> \- \`Crest2\` (crête secondaire) : #A8B1BC
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4A5361
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A5361
>
> \- \`Claw\` (griffes) : #2B2F36
>
> \- \`Eye\` (iris) : #7FC8F0 --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8B1BC
>
> \- \`Extra\` (éléments spéciaux) : #EEF1F4
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
> \- Signes distinctifs (identiques aux trois stades) : crinière de
> nuage gris-blanc ; ailes-bras larges gris orage aux bords effilochés
> en nuage ; spirales de vent claires sur le corps ; pas d\'éclairs (la
> Foudre est un élément futur).
>
> \- Description de ce stade : Wyvern massive. Crinière de nuages
> d\'orage gris et blancs. Très grandes ailes aux bords en nuage.
> Spirales de vent sur le corps. Mâchoire puissante, crocs, griffes
> anthracite.
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
> \- Ailes (cloud) partant des omoplates en (0.74, 0.11, 3.57) : bras
> osseux jusqu\'au poignet (2.22, -0.33, 2.79) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.75.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
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
