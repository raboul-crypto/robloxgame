Dune

Monde 2 · élément Terre · rareté Commun · archétype Tank · morphologie
Drake

Dune · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Dune » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`DUNE_BEBE\` si elle existe, puis range toutes les pièces
> dans une nouvelle collection \`DUNE_BEBE\`. Préfixe tous les objets
> par \`DUNE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`DUNE_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`DUNE_BEBE_BODY_ROOT\`, \`DUNE_BEBE_NECK_ROOT\`,
> \`DUNE_BEBE_HEAD_ROOT\`, \`DUNE_BEBE_TAIL_ROOT\`,
> \`DUNE_BEBE_LEG_AV_ROOT\` (G et D), \`DUNE_BEBE_LEG_AR_ROOT\` (G et
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
> \- \`Body\` (corps principal) : #CFA56A
>
> \- \`BodyDark\` (genoux, ombres) : #7C6340
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #997A4E
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #B08956
>
> \- \`Nostril\` (narines) : #5D4A30
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EAD3A4
>
> \- \`Horn\` (base des cornes) : #6A4A2E
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A4A2E
>
> \- \`Crest\` (sourcils, crêtes) : #8F6438
>
> \- \`Crest2\` (crête secondaire) : #EAD3A4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #EAD3A4
>
> \- \`Claw\` (griffes) : #EAD3A4
>
> \- \`Eye\` (iris) : #4A2E18 --- émissif
>
> \- \`Mark\` (taches, motifs) : #8F6438
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Drake : quatre pattes, aucune aile, corps bas, large et massif.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : rayures brunes
> ondulées comme des dunes ; collerette autour du cou ; deux cornes
> brunes ; crête de petites bosses.
>
> \- Description de ce stade : Drake trapu couleur sable doré, ventre
> crème. Taches et rayures ondulées brunes sur le dos. Collerette de
> petites plaques taillées en facettes couleur crème autour du cou. Deux
> petites cornes brunes. Crête de bosses brunes. Yeux en éclats lumineux
> bruns.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.98, 1.62, 1.09) centré en (0, 0, 1.33), bassin
> (1.75, 1.4, 0.97) centré en (0, 1.12, 1.27).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (3 rangées).
>
> \- Tête : crâne (1.52, 1.52, 1.33) centré en (0, -1.23, 2.81), museau
> allongé x1, cou de 3 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.61, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 8 segments de (0, 1.82, 1.22) à (0, 5.42, 1.06), qui
> s\'affinent (largeur 1.45 → 0.54) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Crête dorsale : petites bosses le long de la nuque, du dos et de la
> queue.
>
> \- Motifs (waves) répartis sur les flancs du torse et de la queue, en
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

Dune · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Dune » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`DUNE_JEUNE\` si elle existe, puis range toutes les pièces
> dans une nouvelle collection \`DUNE_JEUNE\`. Préfixe tous les objets
> par \`DUNE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`DUNE_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`DUNE_JEUNE_BODY_ROOT\`, \`DUNE_JEUNE_NECK_ROOT\`,
> \`DUNE_JEUNE_HEAD_ROOT\`, \`DUNE_JEUNE_TAIL_ROOT\`,
> \`DUNE_JEUNE_LEG_AV_ROOT\` (G et D), \`DUNE_JEUNE_LEG_AR_ROOT\` (G et
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
> exactement 1.8 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #A97F4A
>
> \- \`BodyDark\` (genoux, ombres) : #654C2C
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #7D5E37
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #956E40
>
> \- \`Nostril\` (narines) : #4C3921
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EAD3A4
>
> \- \`Horn\` (base des cornes) : #6A4A2E
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A4A2E
>
> \- \`Crest\` (sourcils, crêtes) : #8F6438
>
> \- \`Crest2\` (crête secondaire) : #EAD3A4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #EAD3A4
>
> \- \`Claw\` (griffes) : #EAD3A4
>
> \- \`Eye\` (iris) : #4A2E18 --- émissif
>
> \- \`Mark\` (taches, motifs) : #8F6438
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Drake : quatre pattes, aucune aile, corps bas, large et massif.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : rayures brunes
> ondulées comme des dunes ; collerette autour du cou ; deux cornes
> brunes ; crête de petites bosses.
>
> \- Description de ce stade : Plus grand, rayures ondulées bien
> marquées. Collerette d\'écailles en éventail. Cornes brunes. Yeux
> ambre, crocs. Pattes épaisses.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.78, 1.95, 1.09) centré en (0, 0, 1.56), bassin
> (1.57, 1.68, 0.97) centré en (0, 1.34, 1.5).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.25, 1.25, 1.09) centré en (0, -1.62, 3.27), museau
> allongé x1.3, cou de 4 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.51, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 10 segments de (0, 2.18, 1.45) à (0, 7.22, 1.23), qui
> s\'affinent (largeur 1.3 → 0.46) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Crête dorsale : petites bosses le long de la nuque, du dos et de la
> queue.
>
> \- Motifs (waves) répartis sur les flancs du torse et de la queue, en
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

Dune · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Dune » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`DUNE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`DUNE_ADULTE\`. Préfixe tous les
> objets par \`DUNE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`DUNE_ADULTE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`DUNE_ADULTE_BODY_ROOT\`, \`DUNE_ADULTE_NECK_ROOT\`,
> \`DUNE_ADULTE_HEAD_ROOT\`, \`DUNE_ADULTE_TAIL_ROOT\`,
> \`DUNE_ADULTE_LEG_AV_ROOT\` (G et D), \`DUNE_ADULTE_LEG_AR_ROOT\` (G
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
> \- \`Body\` (corps principal) : #8A6236
>
> \- \`BodyDark\` (genoux, ombres) : #533B20
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #664928
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #805A32
>
> \- \`Nostril\` (narines) : #3E2C18
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EAD3A4
>
> \- \`Horn\` (base des cornes) : #6A4A2E
>
> \- \`HornTip\` (pointes des cornes, accents) : #6A4A2E
>
> \- \`Crest\` (sourcils, crêtes) : #8F6438
>
> \- \`Crest2\` (crête secondaire) : #EAD3A4
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #EAD3A4
>
> \- \`Claw\` (griffes) : #EAD3A4
>
> \- \`Eye\` (iris) : #4A2E18 --- émissif
>
> \- \`Mark\` (taches, motifs) : #8F6438
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Drake : quatre pattes, aucune aile, corps bas, large et massif.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : rayures brunes
> ondulées comme des dunes ; collerette autour du cou ; deux cornes
> brunes ; crête de petites bosses.
>
> \- Description de ce stade : Massif. Grande collerette membraneuse en
> éventail autour de la tête, comme un lézard à collerette. Cornes
> brunes recourbées. Crête dorsale. Rayures de dunes.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (2.27, 2.44, 1.22) centré en (0, 0, 1.78), bassin
> (2.01, 2.1, 1.09) centré en (0, 1.68, 1.72).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.37, 1.37, 1.2) centré en (0, -1.91, 3.61), museau
> allongé x1.42, cou de 5 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.76, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 12 segments de (0, 2.73, 1.67) à (0, 8.67, 1.41), qui
> s\'affinent (largeur 1.67 → 0.57) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Crête dorsale : petites bosses le long de la nuque, du dos et de la
> queue.
>
> \- Motifs (waves) répartis sur les flancs du torse et de la queue, en
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
