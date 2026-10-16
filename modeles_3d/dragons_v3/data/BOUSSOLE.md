Boussole

Monde 4 · élément Eau · rareté Rare · archétype Équilibré · morphologie
Classique

Boussole · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Boussole » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BOUSSOLE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BOUSSOLE_BEBE\`. Préfixe tous
> les objets par \`BOUSSOLE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BOUSSOLE_BEBE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`BOUSSOLE_BEBE_BODY_ROOT\`, \`BOUSSOLE_BEBE_NECK_ROOT\`,
> \`BOUSSOLE_BEBE_HEAD_ROOT\`, \`BOUSSOLE_BEBE_TAIL_ROOT\`,
> \`BOUSSOLE_BEBE_LEG_AV_ROOT\` (G et D), \`BOUSSOLE_BEBE_LEG_AR_ROOT\`
> (G et D), \`BOUSSOLE_BEBE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #1F3A66
>
> \- \`BodyDark\` (genoux, ombres) : #13233D
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #172B4B
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #434D56
>
> \- \`Nostril\` (narines) : #0E1A2E
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E9DDBF
>
> \- \`Horn\` (base des cornes) : #C8A048 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C8322A
>
> \- \`Crest\` (sourcils, crêtes) : #C8A048
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8A048 ---
> métallique
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4E6A8F
>
> \- \`Claw\` (griffes) : #E9DDBF
>
> \- \`Eye\` (iris) : #D9A62E --- émissif
>
> \- \`Mark\` (taches, motifs) : #C8A048 --- métallique
>
> \- \`Extra\` (éléments spéciaux) : #C8A048
>
> \- \`Extra2\` (éléments spéciaux (2)) : #C8322A
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
> \- Signes distinctifs (identiques aux trois stades) : rose des vents
> dorée sur le front puis sur la poitrine ; deux cornes en forme
> d\'aiguilles de boussole, l\'une à pointe rouge ; ailes bordées de
> laiton comme des voiles ; fines lignes de carte marine dorées sur le
> corps ; queue terminée en flèche.
>
> \- Description de ce stade : Petit dragon classique compact, bleu
> marine, ventre crème parchemin. Rose des vents dorée sur le front.
> Deux petites cornes en forme d\'aiguilles de boussole, l\'une à pointe
> rouge. Petites ailes bleu-gris bordées de laiton. Fines lignes dorées
> comme sur une carte marine. Queue terminée par une petite pointe en
> flèche dorée. Yeux en éclats lumineux dorés.
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
> \- Ailes (membrane) partant des omoplates en (0.6, 0.05, 2.06) : bras
> osseux jusqu\'au poignet (1.58, 0.36, 2.86) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 5.59.
>
> \- Motifs (stripes) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
>
> \- Emblème de rose des vents doré sur la poitrine.
>
> \- Coquillages (ou plaques) en éventail posés sur les épaules.
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

Boussole · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Boussole » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BOUSSOLE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BOUSSOLE_JEUNE\`. Préfixe tous
> les objets par \`BOUSSOLE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BOUSSOLE_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`BOUSSOLE_JEUNE_BODY_ROOT\`, \`BOUSSOLE_JEUNE_NECK_ROOT\`,
> \`BOUSSOLE_JEUNE_HEAD_ROOT\`, \`BOUSSOLE_JEUNE_TAIL_ROOT\`,
> \`BOUSSOLE_JEUNE_LEG_AV_ROOT\` (G et D),
> \`BOUSSOLE_JEUNE_LEG_AR_ROOT\` (G et D), \`BOUSSOLE_JEUNE_WING_ROOT\`
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
> \- \`Body\` (corps principal) : #1A3058
>
> \- \`BodyDark\` (genoux, ombres) : #101D35
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #132441
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #40464D
>
> \- \`Nostril\` (narines) : #0C1628
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E9DDBF
>
> \- \`Horn\` (base des cornes) : #C8A048 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C8322A
>
> \- \`Crest\` (sourcils, crêtes) : #C8A048
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8A048 ---
> métallique
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4E6A8F
>
> \- \`Claw\` (griffes) : #E9DDBF
>
> \- \`Eye\` (iris) : #D9A62E --- émissif
>
> \- \`Mark\` (taches, motifs) : #C8A048 --- métallique
>
> \- \`Extra\` (éléments spéciaux) : #C8A048
>
> \- \`Extra2\` (éléments spéciaux (2)) : #C8322A
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
> \- Signes distinctifs (identiques aux trois stades) : rose des vents
> dorée sur le front puis sur la poitrine ; deux cornes en forme
> d\'aiguilles de boussole, l\'une à pointe rouge ; ailes bordées de
> laiton comme des voiles ; fines lignes de carte marine dorées sur le
> corps ; queue terminée en flèche.
>
> \- Description de ce stade : Élancé. Cornes-aiguilles plus longues.
> Rose des vents dorée sur la poitrine. Ailes comme des voiles, bordées
> de laiton. Lignes de carte. Petits crocs.
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
> \- Ailes (membrane) partant des omoplates en (0.54, 0.06, 2.36) : bras
> osseux jusqu\'au poignet (2.03, 0.53, 3.57) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 7.63.
>
> \- Motifs (stripes) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
>
> \- Emblème de rose des vents doré sur la poitrine.
>
> \- Coquillages (ou plaques) en éventail posés sur les épaules.
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

Boussole · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Boussole » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BOUSSOLE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BOUSSOLE_ADULTE\`. Préfixe tous
> les objets par \`BOUSSOLE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BOUSSOLE_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BOUSSOLE_ADULTE_BODY_ROOT\`, \`BOUSSOLE_ADULTE_NECK_ROOT\`,
> \`BOUSSOLE_ADULTE_HEAD_ROOT\`, \`BOUSSOLE_ADULTE_TAIL_ROOT\`,
> \`BOUSSOLE_ADULTE_LEG_AV_ROOT\` (G et D),
> \`BOUSSOLE_ADULTE_LEG_AR_ROOT\` (G et D),
> \`BOUSSOLE_ADULTE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #162647
>
> \- \`BodyDark\` (genoux, ombres) : #0D172B
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #101C35
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #3D3F41
>
> \- \`Nostril\` (narines) : #0A1120
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E9DDBF
>
> \- \`Horn\` (base des cornes) : #C8A048 --- métallique
>
> \- \`HornTip\` (pointes des cornes, accents) : #C8322A
>
> \- \`Crest\` (sourcils, crêtes) : #C8A048
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8A048 ---
> métallique
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #4E6A8F
>
> \- \`Claw\` (griffes) : #E9DDBF
>
> \- \`Eye\` (iris) : #D9A62E --- émissif
>
> \- \`Mark\` (taches, motifs) : #C8A048 --- métallique
>
> \- \`Extra\` (éléments spéciaux) : #C8A048
>
> \- \`Extra2\` (éléments spéciaux (2)) : #C8322A
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
> \- Signes distinctifs (identiques aux trois stades) : rose des vents
> dorée sur le front puis sur la poitrine ; deux cornes en forme
> d\'aiguilles de boussole, l\'une à pointe rouge ; ailes bordées de
> laiton comme des voiles ; fines lignes de carte marine dorées sur le
> corps ; queue terminée en flèche.
>
> \- Description de ce stade : Musclé. Grande rose des vents dorée sur
> la poitrine, cornes-aiguilles imposantes. Grandes ailes-voiles.
> Plaques dorées sur les épaules. Queue terminée en flèche de boussole.
> Crocs.
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
> \- Ailes (membrane) partant des omoplates en (0.69, 0.08, 2.68) : bras
> osseux jusqu\'au poignet (2.62, 0.69, 4.27) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 9.84.
>
> \- Motifs (stripes) répartis sur les flancs du torse et de la queue,
> en plaques très fines posées sur la peau.
>
> \- Emblème de rose des vents doré sur la poitrine.
>
> \- Coquillages (ou plaques) en éventail posés sur les épaules.
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
