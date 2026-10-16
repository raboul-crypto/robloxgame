Mirage

Monde 2 · élément Terre · rareté Épique · archétype Équilibré ·
morphologie Oriental

Mirage · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Mirage » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`MIRAGE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`MIRAGE_BEBE\`. Préfixe tous les
> objets par \`MIRAGE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`MIRAGE_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`MIRAGE_BEBE_BODY_ROOT\`, \`MIRAGE_BEBE_HEAD_ROOT\`,
> \`MIRAGE_BEBE_TAIL_ROOT\`, \`MIRAGE_BEBE_LEG_AV_ROOT\` (G et D),
> \`MIRAGE_BEBE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #C9A35E
>
> \- \`BodyDark\` (genoux, ombres) : #796238
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #957946
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #B99656
>
> \- \`Nostril\` (narines) : #5A492A
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBDDB8
>
> \- \`Horn\` (base des cornes) : #C79A3E --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C79A3E
>
> \- \`Crest\` (sourcils, crêtes) : #C9A35E
>
> \- \`Crest2\` (crête secondaire) : #B38B4D
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F2D58A
>
> \- \`Claw\` (griffes) : #C79A3E
>
> \- \`Eye\` (iris) : #9A7444 --- émissif
>
> \- \`Mark\` (taches, motifs) : #9A7444
>
> \- \`Extra\` (éléments spéciaux) : #2EC4B6
>
> \- \`Extra2\` (éléments spéciaux (2)) : #F2D58A --- translucide
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
> \- Signes distinctifs (identiques aux trois stades) : gemme turquoise
> en losange sur le front ; crinière vaporeuse dorée et translucide
> comme de l\'air chaud ; taches façon léopard ; longues moustaches
> dorées.
>
> \- Description de ce stade : Petit dragon oriental qui flotte en S,
> quatre petites pattes. Sable doré à taches brun clair, ventre crème.
> Deux cornes dorées, gemme turquoise en losange sur le front. Crinière
> dorée vaporeuse et translucide. Longues moustaches dorées enroulées.
> Queue en touffe vaporeuse. Yeux en éclats lumineux bruns.
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
> \- Motifs (leopard) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
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

Mirage · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Mirage » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`MIRAGE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`MIRAGE_JEUNE\`. Préfixe tous les
> objets par \`MIRAGE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`MIRAGE_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`MIRAGE_JEUNE_BODY_ROOT\`, \`MIRAGE_JEUNE_HEAD_ROOT\`,
> \`MIRAGE_JEUNE_TAIL_ROOT\`, \`MIRAGE_JEUNE_LEG_AV_ROOT\` (G et D),
> \`MIRAGE_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #B38B4D
>
> \- \`BodyDark\` (genoux, ombres) : #6B532E
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #846739
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #A9854B
>
> \- \`Nostril\` (narines) : #513F23
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBDDB8
>
> \- \`Horn\` (base des cornes) : #C79A3E --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C79A3E
>
> \- \`Crest\` (sourcils, crêtes) : #C9A35E
>
> \- \`Crest2\` (crête secondaire) : #B38B4D
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F2D58A
>
> \- \`Claw\` (griffes) : #C79A3E
>
> \- \`Eye\` (iris) : #9A7444 --- émissif
>
> \- \`Mark\` (taches, motifs) : #9A7444
>
> \- \`Extra\` (éléments spéciaux) : #2EC4B6
>
> \- \`Extra2\` (éléments spéciaux (2)) : #F2D58A --- translucide
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
> \- Signes distinctifs (identiques aux trois stades) : gemme turquoise
> en losange sur le front ; crinière vaporeuse dorée et translucide
> comme de l\'air chaud ; taches façon léopard ; longues moustaches
> dorées.
>
> \- Description de ce stade : Corps long en S, taches brunes. Crinière
> dorée translucide plus ample, cornes dorées, gemme turquoise. Yeux
> dorés.
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
> \- Motifs (leopard) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
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

Mirage · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Mirage » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`MIRAGE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`MIRAGE_ADULTE\`. Préfixe tous
> les objets par \`MIRAGE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`MIRAGE_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`MIRAGE_ADULTE_BODY_ROOT\`, \`MIRAGE_ADULTE_HEAD_ROOT\`,
> \`MIRAGE_ADULTE_TAIL_ROOT\`, \`MIRAGE_ADULTE_LEG_AV_ROOT\` (G et D),
> \`MIRAGE_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #9A7440
>
> \- \`BodyDark\` (genoux, ombres) : #5C4626
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #72562F
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #997642
>
> \- \`Nostril\` (narines) : #45341D
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBDDB8
>
> \- \`Horn\` (base des cornes) : #C79A3E --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C79A3E
>
> \- \`Crest\` (sourcils, crêtes) : #C9A35E
>
> \- \`Crest2\` (crête secondaire) : #B38B4D
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F2D58A
>
> \- \`Claw\` (griffes) : #C79A3E
>
> \- \`Eye\` (iris) : #9A7444 --- émissif
>
> \- \`Mark\` (taches, motifs) : #9A7444
>
> \- \`Extra\` (éléments spéciaux) : #2EC4B6
>
> \- \`Extra2\` (éléments spéciaux (2)) : #F2D58A --- translucide
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
> \- Signes distinctifs (identiques aux trois stades) : gemme turquoise
> en losange sur le front ; crinière vaporeuse dorée et translucide
> comme de l\'air chaud ; taches façon léopard ; longues moustaches
> dorées.
>
> \- Description de ce stade : Long dragon oriental or et bronze,
> écailles fines. Gemme turquoise. Crinière de vapeurs dorées
> translucides, nageoires vaporeuses le long du corps. Griffes, crocs.
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
> \- Motifs (leopard) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
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
