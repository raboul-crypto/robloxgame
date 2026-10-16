Revenant

Monde 5 · élément Ténèbres · rareté Secret · archétype Brute ·
morphologie Hydre

Revenant · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Revenant » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`REVENANT_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`REVENANT_BEBE\`. Préfixe tous
> les objets par \`REVENANT_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`REVENANT_BEBE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`REVENANT_BEBE_BODY_ROOT\`, \`REVENANT_BEBE_NECK_ROOT\`,
> \`REVENANT_BEBE_HEAD_ROOT\`, \`REVENANT_BEBE_TAIL_ROOT\`,
> \`REVENANT_BEBE_NECK_G_ROOT\`, \`REVENANT_BEBE_HEAD_G_ROOT\`,
> \`REVENANT_BEBE_NECK_D_ROOT\`, \`REVENANT_BEBE_HEAD_D_ROOT\`,
> \`REVENANT_BEBE_LEG_AV_ROOT\` (G et D), \`REVENANT_BEBE_LEG_AR_ROOT\`
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
> exactement 1 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #1A1420
>
> \- \`BodyDark\` (genoux, ombres) : #100C13
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #130F18
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #322544
>
> \- \`Nostril\` (narines) : #0C090E
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #4E2E78
>
> \- \`Horn\` (base des cornes) : #1A1420
>
> \- \`HornTip\` (pointes des cornes, accents) : #CDB3FF
>
> \- \`Crest\` (sourcils, crêtes) : #8C64C8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #4E2E78 --- translucide
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8C64C8
>
> \- \`Claw\` (griffes) : #8C64C8
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #CDB3FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Hydre : trois têtes sur trois cous (la centrale plus grande), corps
> de drake sur quatre pattes, sans ailes.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : trois têtes ;
> contours qui se dissipent en fumée violette ; petites flammes lilas
> (feux follets) au bout des cornes ; reste mignon.
>
> \- Description de ce stade : Trois petites têtes anguleuses sur cous
> courts, corps trapu sur quatre pattes. Noir et violet. Les bords du
> corps se dissipent en fumée violette. Petites flammes lilas au bout
> des cornes. Yeux en éclats lumineux lilas, air doux.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.98, 1.62, 1.09) centré en (0, 0, 1.35), bassin
> (1.75, 1.4, 0.97) centré en (0, 1.12, 1.29).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (3 rangées).
>
> \- Trois cous et trois têtes : tête centrale (1.52, 1.52, 1.33) en (0,
> -1.23, 2.83), têtes latérales x0.82 tournées de 24° vers l\'extérieur.
>
> \- Pattes : 4 pattes, épaisseur 0.61, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 8 segments de (0, 1.82, 1.24) à (0, 5.42, 1.08), qui
> s\'affinent (largeur 1.45 → 0.54) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
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

Revenant · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Revenant » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`REVENANT_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`REVENANT_JEUNE\`. Préfixe tous
> les objets par \`REVENANT_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`REVENANT_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`REVENANT_JEUNE_BODY_ROOT\`, \`REVENANT_JEUNE_NECK_ROOT\`,
> \`REVENANT_JEUNE_HEAD_ROOT\`, \`REVENANT_JEUNE_TAIL_ROOT\`,
> \`REVENANT_JEUNE_NECK_G_ROOT\`, \`REVENANT_JEUNE_HEAD_G_ROOT\`,
> \`REVENANT_JEUNE_NECK_D_ROOT\`, \`REVENANT_JEUNE_HEAD_D_ROOT\`,
> \`REVENANT_JEUNE_LEG_AV_ROOT\` (G et D),
> \`REVENANT_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #2A1C36
>
> \- \`BodyDark\` (genoux, ombres) : #191120
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #1F1528
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #3D2A53
>
> \- \`Nostril\` (narines) : #130D18
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #4E2E78
>
> \- \`Horn\` (base des cornes) : #1A1420
>
> \- \`HornTip\` (pointes des cornes, accents) : #CDB3FF
>
> \- \`Crest\` (sourcils, crêtes) : #8C64C8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #4E2E78 --- translucide
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8C64C8
>
> \- \`Claw\` (griffes) : #8C64C8
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #CDB3FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Hydre : trois têtes sur trois cous (la centrale plus grande), corps
> de drake sur quatre pattes, sans ailes.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : trois têtes ;
> contours qui se dissipent en fumée violette ; petites flammes lilas
> (feux follets) au bout des cornes ; reste mignon.
>
> \- Description de ce stade : Trois cous plus longs. Fumée violette
> plus présente sur le dos et la queue. Feux follets au bout des cornes.
> Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.78, 1.95, 1.09) centré en (0, 0, 1.59), bassin
> (1.57, 1.68, 0.97) centré en (0, 1.34, 1.53).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Trois cous et trois têtes : tête centrale (1.25, 1.25, 1.09) en (0,
> -1.62, 3.29), têtes latérales x0.82 tournées de 24° vers l\'extérieur.
>
> \- Pattes : 4 pattes, épaisseur 0.51, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 10 segments de (0, 2.18, 1.48) à (0, 7.22, 1.26), qui
> s\'affinent (largeur 1.3 → 0.46) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
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

Revenant · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Revenant » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`REVENANT_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`REVENANT_ADULTE\`. Préfixe tous
> les objets par \`REVENANT_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`REVENANT_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`REVENANT_ADULTE_BODY_ROOT\`, \`REVENANT_ADULTE_NECK_ROOT\`,
> \`REVENANT_ADULTE_HEAD_ROOT\`, \`REVENANT_ADULTE_TAIL_ROOT\`,
> \`REVENANT_ADULTE_NECK_G_ROOT\`, \`REVENANT_ADULTE_HEAD_G_ROOT\`,
> \`REVENANT_ADULTE_NECK_D_ROOT\`, \`REVENANT_ADULTE_HEAD_D_ROOT\`,
> \`REVENANT_ADULTE_LEG_AV_ROOT\` (G et D),
> \`REVENANT_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #4E2E78
>
> \- \`BodyDark\` (genoux, ombres) : #2F1C48
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #3A2259
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #563781
>
> \- \`Nostril\` (narines) : #231536
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #4E2E78
>
> \- \`Horn\` (base des cornes) : #1A1420
>
> \- \`HornTip\` (pointes des cornes, accents) : #CDB3FF
>
> \- \`Crest\` (sourcils, crêtes) : #8C64C8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #4E2E78 --- translucide
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #8C64C8
>
> \- \`Claw\` (griffes) : #8C64C8
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #CDB3FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Hydre : trois têtes sur trois cous (la centrale plus grande), corps
> de drake sur quatre pattes, sans ailes.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : trois têtes ;
> contours qui se dissipent en fumée violette ; petites flammes lilas
> (feux follets) au bout des cornes ; reste mignon.
>
> \- Description de ce stade : Trois têtes imposantes. Corps massif dont
> les contours fument. Feux follets lilas. Crocs. Reste lisible, jamais
> gore.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (2.27, 2.44, 1.22) centré en (0, 0, 1.81), bassin
> (2.01, 2.1, 1.09) centré en (0, 1.68, 1.75).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Trois cous et trois têtes : tête centrale (1.37, 1.37, 1.2) en (0,
> -1.91, 3.64), têtes latérales x0.82 tournées de 24° vers l\'extérieur.
>
> \- Pattes : 4 pattes, épaisseur 0.76, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 12 segments de (0, 2.73, 1.7) à (0, 8.67, 1.44), qui
> s\'affinent (largeur 1.67 → 0.57) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
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
