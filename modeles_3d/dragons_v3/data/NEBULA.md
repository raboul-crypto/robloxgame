Nébula

Exclusif · élément Ténèbres · rareté Exclusif · archétype Rapide ·
morphologie Oriental

Nébula · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Nébula » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEBULA_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEBULA_BEBE\`. Préfixe tous les
> objets par \`NEBULA_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEBULA_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`NEBULA_BEBE_BODY_ROOT\`, \`NEBULA_BEBE_HEAD_ROOT\`,
> \`NEBULA_BEBE_TAIL_ROOT\`, \`NEBULA_BEBE_LEG_AV_ROOT\` (G et D),
> \`NEBULA_BEBE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #0E0A1A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #0A0713
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #291946
>
> \- \`Nostril\` (narines) : #06040C
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #3A1E6E
>
> \- \`Horn\` (base des cornes) : #0E0A1A
>
> \- \`HornTip\` (pointes des cornes, accents) : #FFFFFF
>
> \- \`Crest\` (sourcils, crêtes) : #8A4FE0
>
> \- \`Crest2\` (crête secondaire) : #E05AC8
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A7FFF
>
> \- \`Claw\` (griffes) : #FFFFFF
>
> \- \`Eye\` (iris) : #FFFFFF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFFFFF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #8A4FE0
>
> \- \`Extra2\` (éléments spéciaux (2)) : #4A7FFF
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
> \- Signes distinctifs (identiques aux trois stades) : corps noir et
> violet parsemé d\'étoiles qui scintillent ; crinière en nébuleuse ;
> yeux étoilés.
>
> \- Description de ce stade : Petit dragon oriental qui flotte. Noir et
> violet, parsemé d\'étoiles blanches qui scintillent. Crinière en
> nébuleuse violet, magenta et bleu. Petites cornes. Yeux en éclats
> lumineux étoilés.
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
> \- Motifs (stars_glow) répartis sur les flancs du torse et de la
> queue, en plaques très fines posées sur la peau.
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

Nébula · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Nébula » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEBULA_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEBULA_JEUNE\`. Préfixe tous les
> objets par \`NEBULA_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEBULA_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`NEBULA_JEUNE_BODY_ROOT\`, \`NEBULA_JEUNE_HEAD_ROOT\`,
> \`NEBULA_JEUNE_TAIL_ROOT\`, \`NEBULA_JEUNE_LEG_AV_ROOT\` (G et D),
> \`NEBULA_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #2A1550
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #1F103B
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #3D216B
>
> \- \`Nostril\` (narines) : #130924
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #3A1E6E
>
> \- \`Horn\` (base des cornes) : #0E0A1A
>
> \- \`HornTip\` (pointes des cornes, accents) : #FFFFFF
>
> \- \`Crest\` (sourcils, crêtes) : #8A4FE0
>
> \- \`Crest2\` (crête secondaire) : #E05AC8
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A7FFF
>
> \- \`Claw\` (griffes) : #FFFFFF
>
> \- \`Eye\` (iris) : #FFFFFF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFFFFF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #8A4FE0
>
> \- \`Extra2\` (éléments spéciaux (2)) : #4A7FFF
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
> \- Signes distinctifs (identiques aux trois stades) : corps noir et
> violet parsemé d\'étoiles qui scintillent ; crinière en nébuleuse ;
> yeux étoilés.
>
> \- Description de ce stade : Corps long en S. Étoiles plus nombreuses.
> Crinière nébuleuse plus ample. Crocs.
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
> \- Motifs (stars_glow) répartis sur les flancs du torse et de la
> queue, en plaques très fines posées sur la peau.
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

Nébula · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Nébula » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEBULA_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEBULA_ADULTE\`. Préfixe tous
> les objets par \`NEBULA_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEBULA_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`NEBULA_ADULTE_BODY_ROOT\`, \`NEBULA_ADULTE_HEAD_ROOT\`,
> \`NEBULA_ADULTE_TAIL_ROOT\`, \`NEBULA_ADULTE_LEG_AV_ROOT\` (G et D),
> \`NEBULA_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #3A1E6E
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #2B1651
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #48277F
>
> \- \`Nostril\` (narines) : #1A0E32
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #3A1E6E
>
> \- \`Horn\` (base des cornes) : #0E0A1A
>
> \- \`HornTip\` (pointes des cornes, accents) : #FFFFFF
>
> \- \`Crest\` (sourcils, crêtes) : #8A4FE0
>
> \- \`Crest2\` (crête secondaire) : #E05AC8
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4A7FFF
>
> \- \`Claw\` (griffes) : #FFFFFF
>
> \- \`Eye\` (iris) : #FFFFFF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #FFFFFF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #8A4FE0
>
> \- \`Extra2\` (éléments spéciaux (2)) : #4A7FFF
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
> \- Signes distinctifs (identiques aux trois stades) : corps noir et
> violet parsemé d\'étoiles qui scintillent ; crinière en nébuleuse ;
> yeux étoilés.
>
> \- Description de ce stade : Long dragon oriental. Étoiles
> scintillantes sur tout le corps. Grande crinière nébuleuse. Cornes
> longues. Crocs.
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
> \- Motifs (stars_glow) répartis sur les flancs du torse et de la
> queue, en plaques très fines posées sur la peau.
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
