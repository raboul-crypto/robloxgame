Rafale

Monde 4 · élément Vol · rareté Rare · archétype Rapide · morphologie
Amphiptère

Rafale · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Rafale » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`RAFALE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`RAFALE_BEBE\`. Préfixe tous les
> objets par \`RAFALE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`RAFALE_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`RAFALE_BEBE_BODY_ROOT\`, \`RAFALE_BEBE_HEAD_ROOT\`,
> \`RAFALE_BEBE_TAIL_ROOT\`, \`RAFALE_BEBE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #F4F6F9
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #B5B6B8
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #CCD8E2
>
> \- \`Nostril\` (narines) : #6E6F70
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E3EEF8
>
> \- \`HornTip\` (pointes des cornes, accents) : #2F7FCF
>
> \- \`Crest\` (sourcils, crêtes) : #9CC9EE
>
> \- \`Crest2\` (crête secondaire) : #2F7FCF
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #2F7FCF
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9CC9EE
>
> \- \`Eye\` (iris) : #2F7FCF --- émissif
>
> \- \`Mark\` (taches, motifs) : #B8C0C9
>
> \- \`Extra\` (éléments spéciaux) : #B8C0C9
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : corps de serpent
> blanc et bleu ciel ; ailes de plumes effilées ; bandes de vent
> stylisées gris argent enroulées autour du corps ; crête de plumes ;
> queue terminée en tourbillon de plumes.
>
> \- Description de ce stade : Petit serpent enroulé, haut du corps
> dressé. Blanc, dos bleu ciel, ventre bleu très pâle. Petite crête de
> plumes bleues sur la tête. Deux ailes de plumes effilées. Bandes de
> vent gris argent enroulées autour du corps. Queue terminée par un
> petit tourbillon de plumes. Yeux en éclats lumineux bleus.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 15 segments de (0, 0, 3) à (0.35, 0.88, 0.5),
> largeur 1.31 → 0.49, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (1.15, 1.15, 1.01) centré en (0, -0.36, 3.4).
>
> \- Ailes (feather) partant des omoplates en (0.54, 0.45, 2.42) : bras
> osseux jusqu\'au poignet (1.38, 0.72, 3.11) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.87.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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

Rafale · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Rafale » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`RAFALE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`RAFALE_JEUNE\`. Préfixe tous les
> objets par \`RAFALE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`RAFALE_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`RAFALE_JEUNE_BODY_ROOT\`, \`RAFALE_JEUNE_HEAD_ROOT\`,
> \`RAFALE_JEUNE_TAIL_ROOT\`, \`RAFALE_JEUNE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #E2E8EF
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #A7ACB1
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #BFCEDC
>
> \- \`Nostril\` (narines) : #66686C
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E3EEF8
>
> \- \`HornTip\` (pointes des cornes, accents) : #2F7FCF
>
> \- \`Crest\` (sourcils, crêtes) : #9CC9EE
>
> \- \`Crest2\` (crête secondaire) : #2F7FCF
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #2F7FCF
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9CC9EE
>
> \- \`Eye\` (iris) : #2F7FCF --- émissif
>
> \- \`Mark\` (taches, motifs) : #B8C0C9
>
> \- \`Extra\` (éléments spéciaux) : #B8C0C9
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : corps de serpent
> blanc et bleu ciel ; ailes de plumes effilées ; bandes de vent
> stylisées gris argent enroulées autour du corps ; crête de plumes ;
> queue terminée en tourbillon de plumes.
>
> \- Description de ce stade : Dressé en S, longiligne. Ailes de plumes
> plus longues. Crête de plumes rabattue vers l\'arrière. Bandes de
> vent. Petits crocs, regard vif.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 18 segments de (0, 0, 3.33) à (0.35, 0.88, 0.5),
> largeur 0.93 → 0.36, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (0.94, 0.94, 0.83) centré en (0, -0.3, 3.65).
>
> \- Ailes (feather) partant des omoplates en (0.38, 0.41, 2.79) : bras
> osseux jusqu\'au poignet (1.67, 0.82, 3.84) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.47.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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

Rafale · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Rafale » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`RAFALE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`RAFALE_ADULTE\`. Préfixe tous
> les objets par \`RAFALE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`RAFALE_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`RAFALE_ADULTE_BODY_ROOT\`, \`RAFALE_ADULTE_HEAD_ROOT\`,
> \`RAFALE_ADULTE_TAIL_ROOT\`, \`RAFALE_ADULTE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #D0DAE5
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #9AA1A9
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #B3C5D5
>
> \- \`Nostril\` (narines) : #5E6267
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E3EEF8
>
> \- \`HornTip\` (pointes des cornes, accents) : #2F7FCF
>
> \- \`Crest\` (sourcils, crêtes) : #9CC9EE
>
> \- \`Crest2\` (crête secondaire) : #2F7FCF
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #2F7FCF
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9CC9EE
>
> \- \`Eye\` (iris) : #2F7FCF --- émissif
>
> \- \`Mark\` (taches, motifs) : #B8C0C9
>
> \- \`Extra\` (éléments spéciaux) : #B8C0C9
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : corps de serpent
> blanc et bleu ciel ; ailes de plumes effilées ; bandes de vent
> stylisées gris argent enroulées autour du corps ; crête de plumes ;
> queue terminée en tourbillon de plumes.
>
> \- Description de ce stade : Long serpent dressé, immenses ailes de
> plumes effilées. Crête de plumes hérissée. Bandes de vent enroulées
> sur tout le corps. Queue en tourbillon de plumes. Crocs fins.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 21 segments de (0, 0, 3.45) à (0.35, 0.88, 0.5),
> largeur 1.14 → 0.42, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (1.04, 1.04, 0.91) centré en (0, -0.32, 3.81).
>
> \- Ailes (feather) partant des omoplates en (0.47, 0.38, 2.97) : bras
> osseux jusqu\'au poignet (2.11, 0.9, 4.3) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 8.12.
>
> \- Crête dorsale : plumes le long de la nuque, du dos et de la queue.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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
