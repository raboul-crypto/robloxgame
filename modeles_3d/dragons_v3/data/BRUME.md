Brume

Monde 4 · élément Ténèbres · rareté Légendaire · archétype Rapide ·
morphologie Oriental

Brume · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brume » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRUME_BEBE\` si elle existe, puis range toutes les pièces
> dans une nouvelle collection \`BRUME_BEBE\`. Préfixe tous les objets
> par \`BRUME_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRUME_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`BRUME_BEBE_BODY_ROOT\`, \`BRUME_BEBE_HEAD_ROOT\`,
> \`BRUME_BEBE_TAIL_ROOT\`, \`BRUME_BEBE_LEG_AV_ROOT\` (G et D),
> \`BRUME_BEBE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #3E2A5E
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #2E1F46
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #4B366E
>
> \- \`Nostril\` (narines) : #1C132A
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B8A2D6
>
> \- \`Horn\` (base des cornes) : #1A1622
>
> \- \`HornTip\` (pointes des cornes, accents) : #1A1622
>
> \- \`Crest\` (sourcils, crêtes) : #8F6FC8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #B8A2D6
>
> \- \`Claw\` (griffes) : #1A1622
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B8A2D6
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Oriental : long corps de serpent ondulé en S qui flotte, quatre
> petites pattes, sans ailes, moustaches et crinière.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : crinière et
> queue faites de brume violette translucide ; yeux lavande lumineux ;
> cornes noires aux arêtes vives ; mystérieux mais jamais effrayant.
>
> \- Description de ce stade : Petit dragon oriental qui flotte en S,
> quatre petites pattes. Violet sombre, ventre lilas. Crinière de brume
> violette translucide. Deux petites cornes noires aux arêtes vives.
> Moustaches de brume. Queue qui se dissout en brume. Yeux en éclats
> lumineux lavande, air doux.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 12 segments de (0, 0, 1.53) à (0, 5.6, 1.79),
> largeur 1.34 → 0.52, plaques de ventre, écailles sur les côtés ;
> ondulation sinusoïdale verticale d\'amplitude 0.45.
>
> \- Tête : crâne (1.47, 1.47, 1.29) centré en (0, -0.51, 1.99).
>
> \- Quatre petites pattes pendantes sous les segments 2 et 6, 3 griffes
> chacune.
>
> \- La crinière continue le long du haut du corps.
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

Brume · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brume » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRUME_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRUME_JEUNE\`. Préfixe tous les
> objets par \`BRUME_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRUME_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`BRUME_JEUNE_BODY_ROOT\`, \`BRUME_JEUNE_HEAD_ROOT\`,
> \`BRUME_JEUNE_TAIL_ROOT\`, \`BRUME_JEUNE_LEG_AV_ROOT\` (G et D),
> \`BRUME_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #33244F
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #261B3A
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #443364
>
> \- \`Nostril\` (narines) : #171024
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B8A2D6
>
> \- \`Horn\` (base des cornes) : #1A1622
>
> \- \`HornTip\` (pointes des cornes, accents) : #1A1622
>
> \- \`Crest\` (sourcils, crêtes) : #8F6FC8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #B8A2D6
>
> \- \`Claw\` (griffes) : #1A1622
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B8A2D6
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Oriental : long corps de serpent ondulé en S qui flotte, quatre
> petites pattes, sans ailes, moustaches et crinière.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : crinière et
> queue faites de brume violette translucide ; yeux lavande lumineux ;
> cornes noires aux arêtes vives ; mystérieux mais jamais effrayant.
>
> \- Description de ce stade : Corps long en S. Crinière de brume plus
> ample. Yeux lavande en amande. Petits crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 15 segments de (0, 0, 1.49) à (0, 6.48, 1.75),
> largeur 0.95 → 0.37, plaques de ventre, écailles sur les côtés ;
> ondulation sinusoïdale verticale d\'amplitude 0.45.
>
> \- Tête : crâne (1.21, 1.21, 1.06) centré en (0, -0.41, 1.87).
>
> \- Quatre petites pattes pendantes sous les segments 2 et 7, 3 griffes
> chacune.
>
> \- La crinière continue le long du haut du corps.
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

Brume · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brume » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRUME_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRUME_ADULTE\`. Préfixe tous les
> objets par \`BRUME_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRUME_ADULTE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`BRUME_ADULTE_BODY_ROOT\`, \`BRUME_ADULTE_HEAD_ROOT\`,
> \`BRUME_ADULTE_TAIL_ROOT\`, \`BRUME_ADULTE_LEG_AV_ROOT\` (G et D),
> \`BRUME_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #2A1D40
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #1F152F
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #3E2E5A
>
> \- \`Nostril\` (narines) : #130D1D
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #B8A2D6
>
> \- \`Horn\` (base des cornes) : #1A1622
>
> \- \`HornTip\` (pointes des cornes, accents) : #1A1622
>
> \- \`Crest\` (sourcils, crêtes) : #8F6FC8 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #B8A2D6
>
> \- \`Claw\` (griffes) : #1A1622
>
> \- \`Eye\` (iris) : #CDB3FF --- émissif
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B8A2D6
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Oriental : long corps de serpent ondulé en S qui flotte, quatre
> petites pattes, sans ailes, moustaches et crinière.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : crinière et
> queue faites de brume violette translucide ; yeux lavande lumineux ;
> cornes noires aux arêtes vives ; mystérieux mais jamais effrayant.
>
> \- Description de ce stade : Long dragon oriental élégant. Crinière et
> nageoires de brume violette. Longues cornes noires. Yeux lavande
> lumineux. Crocs fins, griffes noires.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 18 segments de (0, 0, 1.51) à (0, 7.75, 1.77),
> largeur 1.17 → 0.44, plaques de ventre, écailles sur les côtés ;
> ondulation sinusoïdale verticale d\'amplitude 0.45.
>
> \- Tête : crâne (1.32, 1.32, 1.16) centré en (0, -0.46, 1.92).
>
> \- Quatre petites pattes pendantes sous les segments 2 et 9, 3 griffes
> chacune.
>
> \- La crinière continue le long du haut du corps.
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
