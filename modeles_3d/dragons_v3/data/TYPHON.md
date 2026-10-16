Typhon

Monde 4 · élément Eau · rareté Légendaire · archétype Brute ·
morphologie Hydre

Typhon · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Typhon » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TYPHON_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TYPHON_BEBE\`. Préfixe tous les
> objets par \`TYPHON_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TYPHON_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`TYPHON_BEBE_BODY_ROOT\`, \`TYPHON_BEBE_NECK_ROOT\`,
> \`TYPHON_BEBE_HEAD_ROOT\`, \`TYPHON_BEBE_TAIL_ROOT\`,
> \`TYPHON_BEBE_NECK_G_ROOT\`, \`TYPHON_BEBE_HEAD_G_ROOT\`,
> \`TYPHON_BEBE_NECK_D_ROOT\`, \`TYPHON_BEBE_HEAD_D_ROOT\`,
> \`TYPHON_BEBE_LEG_AV_ROOT\` (G et D), \`TYPHON_BEBE_LEG_AR_ROOT\` (G
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
> \- \`Body\` (corps principal) : #163E78
>
> \- \`BodyDark\` (genoux, ombres) : #0D2548
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #102E59
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #1D5176
>
> \- \`Nostril\` (narines) : #0A1C36
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #9EDDD6
>
> \- \`Crest\` (sourcils, crêtes) : #3FA79A
>
> \- \`Crest2\` (crête secondaire) : #F4F8FA
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #3FA79A
>
> \- \`Claw\` (griffes) : #F4F8FA
>
> \- \`Eye\` (iris) : #2FD0C8 --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FC8EA
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
> \- Signes distinctifs (identiques aux trois stades) : trois têtes à
> crêtes en forme de vagues ; spirales de tourbillon sur les cous ;
> écume blanche au bout des crêtes ; pas d\'ailes.
>
> \- Description de ce stade : Corps trapu sur quatre pattes palmées,
> trois têtes anguleuses sur cous courts (la centrale plus grande). Bleu
> profond et vert d\'eau, ventre turquoise clair. Crête en vague sur
> chaque tête, terminée par de l\'écume blanche. Spirales bleu clair sur
> les cous. Petite queue de poisson. Yeux en éclats lumineux turquoise.
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
> \- Crête dorsale : crête en vague le long de la nuque, du dos et de la
> queue.
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

Typhon · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Typhon » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TYPHON_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TYPHON_JEUNE\`. Préfixe tous les
> objets par \`TYPHON_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TYPHON_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`TYPHON_JEUNE_BODY_ROOT\`, \`TYPHON_JEUNE_NECK_ROOT\`,
> \`TYPHON_JEUNE_HEAD_ROOT\`, \`TYPHON_JEUNE_TAIL_ROOT\`,
> \`TYPHON_JEUNE_NECK_G_ROOT\`, \`TYPHON_JEUNE_HEAD_G_ROOT\`,
> \`TYPHON_JEUNE_NECK_D_ROOT\`, \`TYPHON_JEUNE_HEAD_D_ROOT\`,
> \`TYPHON_JEUNE_LEG_AV_ROOT\` (G et D), \`TYPHON_JEUNE_LEG_AR_ROOT\` (G
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
> \- \`Body\` (corps principal) : #122F5C
>
> \- \`BodyDark\` (genoux, ombres) : #0B1C37
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #0D2344
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #1B4763
>
> \- \`Nostril\` (narines) : #081529
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #9EDDD6
>
> \- \`Crest\` (sourcils, crêtes) : #3FA79A
>
> \- \`Crest2\` (crête secondaire) : #F4F8FA
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #3FA79A
>
> \- \`Claw\` (griffes) : #F4F8FA
>
> \- \`Eye\` (iris) : #2FD0C8 --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FC8EA
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
> \- Signes distinctifs (identiques aux trois stades) : trois têtes à
> crêtes en forme de vagues ; spirales de tourbillon sur les cous ;
> écume blanche au bout des crêtes ; pas d\'ailes.
>
> \- Description de ce stade : Trois cous plus longs. Crêtes en vagues
> plus hautes. Spirales de tourbillon. Crocs, air redoutable.
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
> \- Crête dorsale : crête en vague le long de la nuque, du dos et de la
> queue.
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

Typhon · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Typhon » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`TYPHON_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`TYPHON_ADULTE\`. Préfixe tous
> les objets par \`TYPHON_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`TYPHON_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`TYPHON_ADULTE_BODY_ROOT\`, \`TYPHON_ADULTE_NECK_ROOT\`,
> \`TYPHON_ADULTE_HEAD_ROOT\`, \`TYPHON_ADULTE_TAIL_ROOT\`,
> \`TYPHON_ADULTE_NECK_G_ROOT\`, \`TYPHON_ADULTE_HEAD_G_ROOT\`,
> \`TYPHON_ADULTE_NECK_D_ROOT\`, \`TYPHON_ADULTE_HEAD_D_ROOT\`,
> \`TYPHON_ADULTE_LEG_AV_ROOT\` (G et D), \`TYPHON_ADULTE_LEG_AR_ROOT\`
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
> \- \`Body\` (corps principal) : #0E2448
>
> \- \`BodyDark\` (genoux, ombres) : #08162B
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #0A1B35
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #183F55
>
> \- \`Nostril\` (narines) : #061020
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #9EDDD6
>
> \- \`Crest\` (sourcils, crêtes) : #3FA79A
>
> \- \`Crest2\` (crête secondaire) : #F4F8FA
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #3FA79A
>
> \- \`Claw\` (griffes) : #F4F8FA
>
> \- \`Eye\` (iris) : #2FD0C8 --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FC8EA
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
> \- Signes distinctifs (identiques aux trois stades) : trois têtes à
> crêtes en forme de vagues ; spirales de tourbillon sur les cous ;
> écume blanche au bout des crêtes ; pas d\'ailes.
>
> \- Description de ce stade : Trois têtes imposantes, gueules ouvertes
> à crocs. Crêtes en grandes vagues déferlantes. Corps massif. Spirales
> de typhon sur tout le corps.
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
> \- Crête dorsale : crête en vague le long de la nuque, du dos et de la
> queue.
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
