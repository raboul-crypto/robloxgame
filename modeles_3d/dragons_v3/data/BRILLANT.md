Brillant

Monde 5 · élément Minéral · rareté Mythique · archétype Tank ·
morphologie Classique · dragon de zone

Brillant · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brillant » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRILLANT_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRILLANT_BEBE\`. Préfixe tous
> les objets par \`BRILLANT_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRILLANT_BEBE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`BRILLANT_BEBE_BODY_ROOT\`, \`BRILLANT_BEBE_NECK_ROOT\`,
> \`BRILLANT_BEBE_HEAD_ROOT\`, \`BRILLANT_BEBE_TAIL_ROOT\`,
> \`BRILLANT_BEBE_LEG_AV_ROOT\` (G et D), \`BRILLANT_BEBE_LEG_AR_ROOT\`
> (G et D), \`BRILLANT_BEBE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #E8F4FA --- translucide
>
> \- \`BodyDark\` (genoux, ombres) : #8B9296
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #ACB5B9
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #C7DAE4
>
> \- \`Nostril\` (narines) : #686E70
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F7FBFD
>
> \- \`Horn\` (base des cornes) : #E8F4FA
>
> \- \`HornTip\` (pointes des cornes, accents) : #A8D8F0
>
> \- \`Crest\` (sourcils, crêtes) : #A8D8F0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #A8D8F0
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #E8F4FA ---
> translucide
>
> \- \`Claw\` (griffes) : #F7FBFD
>
> \- \`Eye\` (iris) : #7FD0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8D8F0
>
> \- \`Extra\` (éléments spéciaux) : #7FD0FF
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Classique : quatre pattes et deux ailes membraneuses attachées aux
> omoplates, une queue.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : corps fait de
> facettes de diamant translucides ; reflets arc-en-ciel discrets ;
> ailes en cristal facetté.
>
> \- Description de ce stade : Petit dragon classique compact, fait de
> facettes de diamant blanc-bleuté translucides. Reflets arc-en-ciel
> discrets sur les arêtes. Petites cornes en diamant. Petites ailes en
> cristal. Yeux en éclats lumineux bleu clair.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.58, 1.45, 1.15) centré en (0, 0, 1.57), bassin (1.4,
> 1.25, 1.02) centré en (0, 1, 1.51).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (3 rangées).
>
> \- Tête : crâne (1.6, 1.6, 1.4) centré en (0, -1.16, 3.37), museau
> allongé x1, cou de 3 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.55, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 8 segments de (0, 1.62, 1.47) à (0, 4.89, 1.32), qui
> s\'affinent (largeur 1.16 → 0.43) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (crystal) partant des omoplates en (0.6, 0.05, 2.06) : bras
> osseux jusqu\'au poignet (1.58, 0.36, 2.86) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 5.59.
>
> \- Crête dorsale : cristaux pointus le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (diamonds) répartis sur les flancs du torse et de la queue,
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

Brillant · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brillant » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRILLANT_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRILLANT_JEUNE\`. Préfixe tous
> les objets par \`BRILLANT_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRILLANT_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`BRILLANT_JEUNE_BODY_ROOT\`, \`BRILLANT_JEUNE_NECK_ROOT\`,
> \`BRILLANT_JEUNE_HEAD_ROOT\`, \`BRILLANT_JEUNE_TAIL_ROOT\`,
> \`BRILLANT_JEUNE_LEG_AV_ROOT\` (G et D),
> \`BRILLANT_JEUNE_LEG_AR_ROOT\` (G et D), \`BRILLANT_JEUNE_WING_ROOT\`
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
> exactement 1.8 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #C4E6F6 --- translucide
>
> \- \`BodyDark\` (genoux, ombres) : #768A94
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #91AAB6
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #AED0E0
>
> \- \`Nostril\` (narines) : #58686F
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F7FBFD
>
> \- \`Horn\` (base des cornes) : #E8F4FA
>
> \- \`HornTip\` (pointes des cornes, accents) : #A8D8F0
>
> \- \`Crest\` (sourcils, crêtes) : #A8D8F0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #A8D8F0
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #E8F4FA ---
> translucide
>
> \- \`Claw\` (griffes) : #F7FBFD
>
> \- \`Eye\` (iris) : #7FD0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8D8F0
>
> \- \`Extra\` (éléments spéciaux) : #7FD0FF
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Classique : quatre pattes et deux ailes membraneuses attachées aux
> omoplates, une queue.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : corps fait de
> facettes de diamant translucides ; reflets arc-en-ciel discrets ;
> ailes en cristal facetté.
>
> \- Description de ce stade : Corps plus solide, facettes plus nettes
> et plus grandes. Ailes en cristal facetté. Cornes en diamant. Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.42, 1.74, 1.15) centré en (0, 0, 1.88), bassin
> (1.26, 1.5, 1.02) centré en (0, 1.2, 1.81).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.31, 1.31, 1.15) centré en (0, -1.53, 3.95), museau
> allongé x1.3, cou de 4 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.46, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 10 segments de (0, 1.95, 1.76) à (0, 6.53, 1.57), qui
> s\'affinent (largeur 1.04 → 0.37) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (crystal) partant des omoplates en (0.54, 0.06, 2.36) : bras
> osseux jusqu\'au poignet (2.03, 0.53, 3.57) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.63.
>
> \- Crête dorsale : cristaux pointus le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (diamonds) répartis sur les flancs du torse et de la queue,
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

Brillant · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brillant » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRILLANT_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRILLANT_ADULTE\`. Préfixe tous
> les objets par \`BRILLANT_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRILLANT_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRILLANT_ADULTE_BODY_ROOT\`, \`BRILLANT_ADULTE_NECK_ROOT\`,
> \`BRILLANT_ADULTE_HEAD_ROOT\`, \`BRILLANT_ADULTE_TAIL_ROOT\`,
> \`BRILLANT_ADULTE_LEG_AV_ROOT\` (G et D),
> \`BRILLANT_ADULTE_LEG_AR_ROOT\` (G et D),
> \`BRILLANT_ADULTE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #A8D8F0 --- translucide
>
> \- \`BodyDark\` (genoux, ombres) : #658290
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #7CA0B2
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #9BC7DD
>
> \- \`Nostril\` (narines) : #4C616C
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #F7FBFD
>
> \- \`Horn\` (base des cornes) : #E8F4FA
>
> \- \`HornTip\` (pointes des cornes, accents) : #A8D8F0
>
> \- \`Crest\` (sourcils, crêtes) : #A8D8F0
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #A8D8F0
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #E8F4FA ---
> translucide
>
> \- \`Claw\` (griffes) : #F7FBFD
>
> \- \`Eye\` (iris) : #7FD0FF --- émissif
>
> \- \`Mark\` (taches, motifs) : #A8D8F0
>
> \- \`Extra\` (éléments spéciaux) : #7FD0FF
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Classique : quatre pattes et deux ailes membraneuses attachées aux
> omoplates, une queue.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : corps fait de
> facettes de diamant translucides ; reflets arc-en-ciel discrets ;
> ailes en cristal facetté.
>
> \- Description de ce stade : Imposant et massif. Corps de diamant
> taillé en grandes facettes. Grandes ailes en cristal. Cornes en
> diamant. Crocs.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Torse avant (1.82, 2.17, 1.29) centré en (0, 0, 2.14), bassin
> (1.61, 1.88, 1.14) centré en (0, 1.5, 2.08).
>
> \- Poitrail avec plastron couleur ventre, 3 plaques de ventre sous le
> torse, écailles en quinconce sur les flancs (4 rangées).
>
> \- Tête : crâne (1.44, 1.44, 1.26) centré en (0, -1.8, 4.36), museau
> allongé x1.42, cou de 5 segments.
>
> \- Pattes : 4 pattes, épaisseur 0.68, pieds à plat au sol (Z = 0) avec
> 3 griffes en pyramide pointées vers l\'avant.
>
> \- Queue : 12 segments de (0, 2.44, 2.03) à (0, 7.83, 1.8), qui
> s\'affinent (largeur 1.33 → 0.45) en suivant une courbe de -14° à +9°,
> avec un fort chevauchement (x1.32) ; plaques de ventre sous les 3/4
> avant, écailles sur les côtés.
>
> \- Ailes (crystal) partant des omoplates en (0.69, 0.08, 2.68) : bras
> osseux jusqu\'au poignet (2.62, 0.69, 4.27) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 9.84.
>
> \- Crête dorsale : cristaux pointus le long de la nuque, du dos et de
> la queue.
>
> \- Motifs (diamonds) répartis sur les flancs du torse et de la queue,
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
