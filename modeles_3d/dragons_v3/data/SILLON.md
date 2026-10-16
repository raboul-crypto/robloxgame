Sillon

Monde 1 · élément Terre · rareté Rare · archétype Brute · morphologie
Wyvern

Sillon · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sillon » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SILLON_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SILLON_BEBE\`. Préfixe tous les
> objets par \`SILLON_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SILLON_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`SILLON_BEBE_BODY_ROOT\`, \`SILLON_BEBE_NECK_ROOT\`,
> \`SILLON_BEBE_HEAD_ROOT\`, \`SILLON_BEBE_TAIL_ROOT\`,
> \`SILLON_BEBE_LEG_AR_ROOT\` (G et D), \`SILLON_BEBE_WING_ROOT\` (G et
> D).
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
> \- \`Body\` (corps principal) : #5E3F27
>
> \- \`BodyDark\` (genoux, ombres) : #382617
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #462F1D
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #523722
>
> \- \`Nostril\` (narines) : #2A1C12
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B07A45
>
> \- \`Horn\` (base des cornes) : #C8B08A
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A625A
>
> \- \`Crest\` (sourcils, crêtes) : #4B321F
>
> \- \`Crest2\` (crête secondaire) : #B07A45
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4B321F
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #5E3F27
>
> \- \`Claw\` (griffes) : #3E3934
>
> \- \`Eye\` (iris) : #C27A1E --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : une corne sur le
> museau en forme de soc de charrue ; crinière d\'épines brunes sur le
> crâne et le dos ; ailes-bras terminées par de grandes griffes en forme
> de pelle ; plaques sur la queue.
>
> \- Description de ce stade : Petite wyvern debout sur ses deux pattes
> arrière. Brun chocolat, masque caramel autour des yeux en éclats
> lumineux ambre, ventre caramel en plaques. Une corne grise sur le
> museau en forme de soc de charrue. Épines brunes sur le crâne et le
> dos. Ailes repliées le long du corps qui servent de bras, terminées
> par de grosses griffes gris foncé en forme de pelle. Queue à plaques.
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
> \- Ailes (membrane) partant des omoplates en (0.65, 0.11, 2.6) : bras
> osseux jusqu\'au poignet (1.4, -0.11, 2.2) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.62.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
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

Sillon · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sillon » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SILLON_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SILLON_JEUNE\`. Préfixe tous les
> objets par \`SILLON_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SILLON_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`SILLON_JEUNE_BODY_ROOT\`, \`SILLON_JEUNE_NECK_ROOT\`,
> \`SILLON_JEUNE_HEAD_ROOT\`, \`SILLON_JEUNE_TAIL_ROOT\`,
> \`SILLON_JEUNE_LEG_AR_ROOT\` (G et D), \`SILLON_JEUNE_WING_ROOT\` (G
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
> \- \`Body\` (corps principal) : #553923
>
> \- \`BodyDark\` (genoux, ombres) : #332215
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #3F2A1A
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #4B331F
>
> \- \`Nostril\` (narines) : #261A10
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B07A45
>
> \- \`Horn\` (base des cornes) : #C8B08A
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A625A
>
> \- \`Crest\` (sourcils, crêtes) : #4B321F
>
> \- \`Crest2\` (crête secondaire) : #B07A45
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4B321F
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #5E3F27
>
> \- \`Claw\` (griffes) : #3E3934
>
> \- \`Eye\` (iris) : #C27A1E --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : une corne sur le
> museau en forme de soc de charrue ; crinière d\'épines brunes sur le
> crâne et le dos ; ailes-bras terminées par de grandes griffes en forme
> de pelle ; plaques sur la queue.
>
> \- Description de ce stade : Plus élancé, debout. Corne-soc beige
> recourbée sur le museau. Crinière d\'épines. Ailes brunes repliées en
> bras griffus. Yeux ambre, crocs. Longue queue à plaques épineuses.
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
> \- Ailes (membrane) partant des omoplates en (0.58, 0.1, 3.07) : bras
> osseux jusqu\'au poignet (1.74, -0.24, 2.46) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.14.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
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

Sillon · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sillon » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SILLON_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SILLON_ADULTE\`. Préfixe tous
> les objets par \`SILLON_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SILLON_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`SILLON_ADULTE_BODY_ROOT\`, \`SILLON_ADULTE_NECK_ROOT\`,
> \`SILLON_ADULTE_HEAD_ROOT\`, \`SILLON_ADULTE_TAIL_ROOT\`,
> \`SILLON_ADULTE_LEG_AR_ROOT\` (G et D), \`SILLON_ADULTE_WING_ROOT\` (G
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
> exactement 3 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #4B321F
>
> \- \`BodyDark\` (genoux, ombres) : #2D1E13
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #382517
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #452E1D
>
> \- \`Nostril\` (narines) : #22160E
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B07A45
>
> \- \`Horn\` (base des cornes) : #C8B08A
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A625A
>
> \- \`Crest\` (sourcils, crêtes) : #4B321F
>
> \- \`Crest2\` (crête secondaire) : #B07A45
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #4B321F
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #5E3F27
>
> \- \`Claw\` (griffes) : #3E3934
>
> \- \`Eye\` (iris) : #C27A1E --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : une corne sur le
> museau en forme de soc de charrue ; crinière d\'épines brunes sur le
> crâne et le dos ; ailes-bras terminées par de grandes griffes en forme
> de pelle ; plaques sur la queue.
>
> \- Description de ce stade : Wyvern musclée, posture penchée en avant.
> Corne-soc imposante, crête d\'épines du crâne à la queue. Griffes de
> pelleteuse aux poignets des ailes. Membranes brunes tachetées.
> Écailles brun et ocre très détaillées, crocs.
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
> \- Ailes (membrane) partant des omoplates en (0.74, 0.11, 3.57) : bras
> osseux jusqu\'au poignet (2.22, -0.33, 2.79) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.75.
>
> \- Crête dorsale : épines pyramidales le long de la nuque, du dos et
> de la queue.
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
