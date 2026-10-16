Léviathan

Monde 4 · élément Eau · rareté Mythique · archétype Tank · morphologie
Aquatique · dragon de zone

Léviathan · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Léviathan » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`LEVIATHAN_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`LEVIATHAN_BEBE\`. Préfixe tous
> les objets par \`LEVIATHAN_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`LEVIATHAN_BEBE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`LEVIATHAN_BEBE_BODY_ROOT\`, \`LEVIATHAN_BEBE_NECK_ROOT\`,
> \`LEVIATHAN_BEBE_HEAD_ROOT\`, \`LEVIATHAN_BEBE_TAIL_ROOT\`,
> \`LEVIATHAN_BEBE_LEG_AV_ROOT\` (G et D),
> \`LEVIATHAN_BEBE_LEG_AR_ROOT\` (G et D),
> \`LEVIATHAN_BEBE_FIN_FRONT_ROOT\` (G et D),
> \`LEVIATHAN_BEBE_FIN_REAR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #0E2A55
>
> \- \`BodyDark\` (genoux, ombres) : #081933
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #0A1F3F
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #114465
>
> \- \`Nostril\` (narines) : #061326
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #A9D8E6
>
> \- \`Horn\` (base des cornes) : #E6EEF0
>
> \- \`HornTip\` (pointes des cornes, accents) : #E6EEF0
>
> \- \`Crest\` (sourcils, crêtes) : #1FA8B8
>
> \- \`Crest2\` (crête secondaire) : #E6EEF0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #0E2A55
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #1FA8B8
>
> \- \`Claw\` (griffes) : #E6EEF0
>
> \- \`Eye\` (iris) : #4FF0FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #4FF0FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Aquatique : quatre pattes palmées, nageoires à la place des ailes,
> queue de poisson.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : plaques blindées
> sur le dos ; nageoires immenses ; points et lignes bioluminescents
> cyan ; couronne de cornes nacrées.
>
> \- Description de ce stade : Petit dragon aquatique compact et lourd,
> bleu abyssal et turquoise, ventre bleu pâle. Petites plaques sur le
> dos. Points bioluminescents cyan sur les flancs. Couronne de petites
> cornes nacrées. Grandes nageoires. Queue de poisson. Yeux en éclats
> lumineux cyan.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.74, 1.45, 1.15) centré en (0, 0, 1.42), bassin
> (1.54, 1.25, 1.02) centré en (0, 1, 1.36).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (3 rangées).
>
> \- Tête : crâne (1.6, 1.6, 1.4) centré en (0, -1.16, 3.22), museau
> allongé x1, cou de 3 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.58, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant, doigts palmés.
>
> \- Queue : 8 segments de (0, 1.62, 1.32) à (0, 4.89, 1.17), qui
> s\'affinent (largeur 1.28 → 0.47) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Nageoire Fin_Front en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.77, -0.2, 1.52).
>
> \- Nageoire Fin_Rear en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.68, 1.1, 1.41).
>
> \- Crête dorsale : plaques dressées le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (bio_dots, lines_glow) répartis sur les flancs du torse et
> de la queue, en plaques très fines posées sur la peau.
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

Léviathan · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Léviathan » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`LEVIATHAN_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`LEVIATHAN_JEUNE\`. Préfixe tous
> les objets par \`LEVIATHAN_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`LEVIATHAN_JEUNE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`LEVIATHAN_JEUNE_BODY_ROOT\`, \`LEVIATHAN_JEUNE_NECK_ROOT\`,
> \`LEVIATHAN_JEUNE_HEAD_ROOT\`, \`LEVIATHAN_JEUNE_TAIL_ROOT\`,
> \`LEVIATHAN_JEUNE_LEG_AV_ROOT\` (G et D),
> \`LEVIATHAN_JEUNE_LEG_AR_ROOT\` (G et D),
> \`LEVIATHAN_JEUNE_FIN_FRONT_ROOT\` (G et D),
> \`LEVIATHAN_JEUNE_FIN_REAR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #0B2244
>
> \- \`BodyDark\` (genoux, ombres) : #071429
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #081932
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #0F3F59
>
> \- \`Nostril\` (narines) : #050F1F
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #A9D8E6
>
> \- \`Horn\` (base des cornes) : #E6EEF0
>
> \- \`HornTip\` (pointes des cornes, accents) : #E6EEF0
>
> \- \`Crest\` (sourcils, crêtes) : #1FA8B8
>
> \- \`Crest2\` (crête secondaire) : #E6EEF0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #0E2A55
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #1FA8B8
>
> \- \`Claw\` (griffes) : #E6EEF0
>
> \- \`Eye\` (iris) : #4FF0FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #4FF0FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Aquatique : quatre pattes palmées, nageoires à la place des ailes,
> queue de poisson.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : plaques blindées
> sur le dos ; nageoires immenses ; points et lignes bioluminescents
> cyan ; couronne de cornes nacrées.
>
> \- Description de ce stade : Plaques blindées plus épaisses. Nageoires
> plus grandes. Lignes bioluminescentes. Cornes nacrées. Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.56, 1.74, 1.15) centré en (0, 0, 1.68), bassin
> (1.39, 1.5, 1.02) centré en (0, 1.2, 1.62).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.31, 1.31, 1.15) centré en (0, -1.53, 3.75), museau
> allongé x1.3, cou de 4 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.48, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant, doigts palmés.
>
> \- Queue : 10 segments de (0, 1.95, 1.57) à (0, 6.53, 1.37), qui
> s\'affinent (largeur 1.15 → 0.4) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Nageoire Fin_Front en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.69, -0.24, 1.78).
>
> \- Nageoire Fin_Rear en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.61, 1.3, 1.67).
>
> \- Crête dorsale : plaques dressées le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (bio_dots, lines_glow) répartis sur les flancs du torse et
> de la queue, en plaques très fines posées sur la peau.
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

Léviathan · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Léviathan » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`LEVIATHAN_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`LEVIATHAN_ADULTE\`. Préfixe tous
> les objets par \`LEVIATHAN_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`LEVIATHAN_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`LEVIATHAN_ADULTE_BODY_ROOT\`, \`LEVIATHAN_ADULTE_NECK_ROOT\`,
> \`LEVIATHAN_ADULTE_HEAD_ROOT\`, \`LEVIATHAN_ADULTE_TAIL_ROOT\`,
> \`LEVIATHAN_ADULTE_LEG_AV_ROOT\` (G et D),
> \`LEVIATHAN_ADULTE_LEG_AR_ROOT\` (G et D),
> \`LEVIATHAN_ADULTE_FIN_FRONT_ROOT\` (G et D),
> \`LEVIATHAN_ADULTE_FIN_REAR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #08193A
>
> \- \`BodyDark\` (genoux, ombres) : #050F23
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #06122B
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #0D3853
>
> \- \`Nostril\` (narines) : #040B1A
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #A9D8E6
>
> \- \`Horn\` (base des cornes) : #E6EEF0
>
> \- \`HornTip\` (pointes des cornes, accents) : #E6EEF0
>
> \- \`Crest\` (sourcils, crêtes) : #1FA8B8
>
> \- \`Crest2\` (crête secondaire) : #E6EEF0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #0E2A55
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #1FA8B8
>
> \- \`Claw\` (griffes) : #E6EEF0
>
> \- \`Eye\` (iris) : #4FF0FF --- émissif
>
> \- \`Glow\` (parties lumineuses) : #4FF0FF --- émissif
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Aquatique : quatre pattes palmées, nageoires à la place des ailes,
> queue de poisson.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : plaques blindées
> sur le dos ; nageoires immenses ; points et lignes bioluminescents
> cyan ; couronne de cornes nacrées.
>
> \- Description de ce stade : Colossal. Dos blindé, crête de nageoires.
> Immenses nageoires latérales. Lignes et points bioluminescents.
> Couronne de cornes nacrées. Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (2, 2.17, 1.29) centré en (0, 0, 1.92), bassin (1.77,
> 1.88, 1.14) centré en (0, 1.5, 1.86).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.44, 1.44, 1.26) centré en (0, -1.8, 4.13), museau
> allongé x1.42, cou de 5 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.71, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant, doigts palmés.
>
> \- Queue : 12 segments de (0, 2.44, 1.81) à (0, 7.83, 1.57), qui
> s\'affinent (largeur 1.47 → 0.5) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Nageoire Fin_Front en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.89, -0.3, 2.02).
>
> \- Nageoire Fin_Rear en éventail (plaque translucide + 3 rayons
> osseux) attachée en (0.78, 1.6, 1.91).
>
> \- Crête dorsale : plaques dressées le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (bio_dots, lines_glow) répartis sur les flancs du torse et
> de la queue, en plaques très fines posées sur la peau.
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
