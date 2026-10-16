Neptyr

Monde 3 · élément Eau · rareté Légendaire · archétype Équilibré ·
morphologie Oriental · dragon de zone

Neptyr · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Neptyr » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEPTYR_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEPTYR_BEBE\`. Préfixe tous les
> objets par \`NEPTYR_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEPTYR_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`NEPTYR_BEBE_BODY_ROOT\`, \`NEPTYR_BEBE_HEAD_ROOT\`,
> \`NEPTYR_BEBE_TAIL_ROOT\`, \`NEPTYR_BEBE_LEG_AV_ROOT\` (G et D),
> \`NEPTYR_BEBE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #1E3F7A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #162F5A
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #395E8D
>
> \- \`Nostril\` (narines) : #0E1C37
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #8ED6D0
>
> \- \`Horn\` (base des cornes) : #C9A040 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C9A040 --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #9FDDF5 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #8ED6D0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #1E3F7A
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9FDDF5 ---
> translucide
>
> \- \`Claw\` (griffes) : #C9A040 --- métallique
>
> \- \`Eye\` (iris) : #3FE0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #3FE0FF
>
> \- \`Glow\` (parties lumineuses) : #3FE0FF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #C9A040
>
> \- \`Extra2\` (éléments spéciaux (2)) : #9FDDF5
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
> \- Signes distinctifs (identiques aux trois stades) : bois dorés ;
> crinière et nageoires bleu ciel translucides ; spirales et runes cyan
> lumineuses sur le corps ; moustaches lumineuses ; queue en nageoire
> plumeuse.
>
> \- Description de ce stade : Petit dragon oriental qui flotte, bleu
> nuit, ventre turquoise clair. Deux bois dorés. Crinière et nageoires
> bleu ciel translucides. Moustaches bleu clair lumineuses. Spirales
> cyan lumineuses sur le corps. Queue en grande nageoire plumeuse. Yeux
> en éclats lumineux bleus.
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
> \- Nageoire dorsale continue (plaques translucides + rayons) le long
> du dos et de la queue.
>
> \- Motifs (swirls, runes_glow) répartis sur les flancs du torse et de
> la queue, en plaques très fines posées sur la peau.
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

Neptyr · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Neptyr » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEPTYR_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEPTYR_JEUNE\`. Préfixe tous les
> objets par \`NEPTYR_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEPTYR_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`NEPTYR_JEUNE_BODY_ROOT\`, \`NEPTYR_JEUNE_HEAD_ROOT\`,
> \`NEPTYR_JEUNE_TAIL_ROOT\`, \`NEPTYR_JEUNE_LEG_AV_ROOT\` (G et D),
> \`NEPTYR_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #183263
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #122549
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #35567D
>
> \- \`Nostril\` (narines) : #0B162D
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #8ED6D0
>
> \- \`Horn\` (base des cornes) : #C9A040 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C9A040 --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #9FDDF5 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #8ED6D0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #1E3F7A
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9FDDF5 ---
> translucide
>
> \- \`Claw\` (griffes) : #C9A040 --- métallique
>
> \- \`Eye\` (iris) : #3FE0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #3FE0FF
>
> \- \`Glow\` (parties lumineuses) : #3FE0FF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #C9A040
>
> \- \`Extra2\` (éléments spéciaux (2)) : #9FDDF5
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
> \- Signes distinctifs (identiques aux trois stades) : bois dorés ;
> crinière et nageoires bleu ciel translucides ; spirales et runes cyan
> lumineuses sur le corps ; moustaches lumineuses ; queue en nageoire
> plumeuse.
>
> \- Description de ce stade : Crinière plus ample, yeux cyan lumineux,
> runes lumineuses. Griffes dorées.
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
> \- Nageoire dorsale continue (plaques translucides + rayons) le long
> du dos et de la queue.
>
> \- Motifs (swirls, runes_glow) répartis sur les flancs du torse et de
> la queue, en plaques très fines posées sur la peau.
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

Neptyr · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Neptyr » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`NEPTYR_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`NEPTYR_ADULTE\`. Préfixe tous
> les objets par \`NEPTYR_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`NEPTYR_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`NEPTYR_ADULTE_BODY_ROOT\`, \`NEPTYR_ADULTE_HEAD_ROOT\`,
> \`NEPTYR_ADULTE_TAIL_ROOT\`, \`NEPTYR_ADULTE_LEG_AV_ROOT\` (G et D),
> \`NEPTYR_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #12274F
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #0D1D3A
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #314D6E
>
> \- \`Nostril\` (narines) : #081224
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #8ED6D0
>
> \- \`Horn\` (base des cornes) : #C9A040 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C9A040 --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #9FDDF5 --- translucide
>
> \- \`Crest2\` (crête secondaire) : #8ED6D0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #1E3F7A
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #9FDDF5 ---
> translucide
>
> \- \`Claw\` (griffes) : #C9A040 --- métallique
>
> \- \`Eye\` (iris) : #3FE0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #3FE0FF
>
> \- \`Glow\` (parties lumineuses) : #3FE0FF --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #C9A040
>
> \- \`Extra2\` (éléments spéciaux (2)) : #9FDDF5
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
> \- Signes distinctifs (identiques aux trois stades) : bois dorés ;
> crinière et nageoires bleu ciel translucides ; spirales et runes cyan
> lumineuses sur le corps ; moustaches lumineuses ; queue en nageoire
> plumeuse.
>
> \- Description de ce stade : Long dragon oriental majestueux. Bois
> dorés ramifiés et diadème doré sur le front. Yeux cyan lumineux. Runes
> lumineuses sur tout le corps. Crocs. Nageoires translucides.
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
> \- Nageoire dorsale continue (plaques translucides + rayons) le long
> du dos et de la queue.
>
> \- Motifs (swirls, runes_glow) répartis sur les flancs du torse et de
> la queue, en plaques très fines posées sur la peau.
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
