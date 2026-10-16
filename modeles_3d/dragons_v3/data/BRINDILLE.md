Brindille

Monde 1 · élément Plante · rareté Commun · archétype Rapide ·
morphologie Amphiptère

Brindille · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brindille » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRINDILLE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRINDILLE_BEBE\`. Préfixe tous
> les objets par \`BRINDILLE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRINDILLE_BEBE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`BRINDILLE_BEBE_BODY_ROOT\`, \`BRINDILLE_BEBE_HEAD_ROOT\`,
> \`BRINDILLE_BEBE_TAIL_ROOT\`, \`BRINDILLE_BEBE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #9DB55A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #748643
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #8AA24C
>
> \- \`Nostril\` (narines) : #475128
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E6DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A2B
>
> \- \`HornTip\` (pointes des cornes, accents) : #B9D36A
>
> \- \`Crest\` (sourcils, crêtes) : #7FA03E
>
> \- \`Crest2\` (crête secondaire) : #B9D36A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #6B4A2B
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #7FA03E
>
> \- \`Claw\` (griffes) : #E6DDB8
>
> \- \`Eye\` (iris) : #4E7A2A --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FA03E
>
> \- \`Extra\` (éléments spéciaux) : #6B4A2B
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B9D36A
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade bébé : silhouette compacte et trapue, grosse tête (environ 30
> % de la hauteur), museau court, pattes courtes et épaisses, grands
> yeux, cornes et épines encore petites, pas de crocs.
>
> \- Signes distinctifs (identiques aux trois stades) : bois en
> brindilles brunes avec bourgeons sur la tête ; liane brune enroulée en
> spirale autour du corps ; ailes en forme de grandes feuilles nervurées
> ; queue terminée par une feuille ; corps de serpent sans pattes.
>
> \- Description de ce stade : Petit serpent vert tendre enroulé en
> spirale sur lui-même, le haut du corps dressé. Grosse tête anguleuse
> aux yeux en éclats lumineux verts. Deux bois de brindilles brunes avec
> de petits bourgeons verts, oreilles en forme de feuilles. Une liane
> brune s\'enroule en spirale autour du corps. Ventre crème. Deux ailes
> en forme de feuilles vertes nervurées sur le haut du dos. Queue qui
> ressort du rouleau, terminée par une feuille.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 15 segments de (0, 0, 3) à (0.35, 0.88, 0.5),
> largeur 1.31 → 0.49, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (1.15, 1.15, 1.01) centré en (0, -0.36, 3.4).
>
> \- Ailes (leaf) partant des omoplates en (0.54, 0.45, 2.42) : bras
> osseux jusqu\'au poignet (1.38, 0.72, 3.11) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.87.
>
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Liane enroulée en spirale autour du corps.
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

Brindille · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brindille » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRINDILLE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRINDILLE_JEUNE\`. Préfixe tous
> les objets par \`BRINDILLE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRINDILLE_JEUNE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRINDILLE_JEUNE_BODY_ROOT\`, \`BRINDILLE_JEUNE_HEAD_ROOT\`,
> \`BRINDILLE_JEUNE_TAIL_ROOT\`, \`BRINDILLE_JEUNE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #8DA351
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #68793C
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #7F9546
>
> \- \`Nostril\` (narines) : #3F4924
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E6DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A2B
>
> \- \`HornTip\` (pointes des cornes, accents) : #B9D36A
>
> \- \`Crest\` (sourcils, crêtes) : #7FA03E
>
> \- \`Crest2\` (crête secondaire) : #B9D36A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #6B4A2B
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #7FA03E
>
> \- \`Claw\` (griffes) : #E6DDB8
>
> \- \`Eye\` (iris) : #4E7A2A --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FA03E
>
> \- \`Extra\` (éléments spéciaux) : #6B4A2B
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B9D36A
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade jeune (ado) : silhouette plus élancée, tête plus petite,
> museau plus long, cou plus long (4 segments), yeux en amande au regard
> sérieux, petits crocs, cornes et épines plus grandes.
>
> \- Signes distinctifs (identiques aux trois stades) : bois en
> brindilles brunes avec bourgeons sur la tête ; liane brune enroulée en
> spirale autour du corps ; ailes en forme de grandes feuilles nervurées
> ; queue terminée par une feuille ; corps de serpent sans pattes.
>
> \- Description de ce stade : Corps de serpent dressé en S, le bas
> enroulé au sol. Écailles en petites feuilles vertes, ventre crème en
> plaques. Bois de brindilles plus longs et ramifiés, crinière de
> feuilles derrière la tête. Lianes brunes enroulées autour du corps.
> Ailes-feuilles plus grandes. Petits crocs. Regard sérieux.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 18 segments de (0, 0, 3.33) à (0.35, 0.88, 0.5),
> largeur 0.93 → 0.36, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (0.94, 0.94, 0.83) centré en (0, -0.3, 3.65).
>
> \- Ailes (leaf) partant des omoplates en (0.38, 0.41, 2.79) : bras
> osseux jusqu\'au poignet (1.67, 0.82, 3.84) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.47.
>
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Liane enroulée en spirale autour du corps.
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

Brindille · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Brindille » au stade ADULTE pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`BRINDILLE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`BRINDILLE_ADULTE\`. Préfixe tous
> les objets par \`BRINDILLE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`BRINDILLE_ADULTE_MASTER_ROOT\` et,
> reliés à lui, ces contrôleurs placés aux articulations :
> \`BRINDILLE_ADULTE_BODY_ROOT\`, \`BRINDILLE_ADULTE_HEAD_ROOT\`,
> \`BRINDILLE_ADULTE_TAIL_ROOT\`, \`BRINDILLE_ADULTE_WING_ROOT\` (G et
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
> exactement 3 unité(s) de haut (bébé 1, jeune 1.8, adulte 3), pieds
> posés sur Z = 0 et centré sur l\'origine ; affichage \`MATERIAL\` dans
> la vue 3D et \`show_relationship_lines\` désactivé.
>
> \### 2. PALETTE DE MATÉRIAUX (Principled BSDF, aspect plastique mat,
> rugosité \~0.45, couleurs hex converties en linéaire)
>
> \- \`Body\` (corps principal) : #7E9148
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #5D6B35
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #748940
>
> \- \`Nostril\` (narines) : #394120
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E6DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A2B
>
> \- \`HornTip\` (pointes des cornes, accents) : #B9D36A
>
> \- \`Crest\` (sourcils, crêtes) : #7FA03E
>
> \- \`Crest2\` (crête secondaire) : #B9D36A
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #6B4A2B
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #7FA03E
>
> \- \`Claw\` (griffes) : #E6DDB8
>
> \- \`Eye\` (iris) : #4E7A2A --- émissif
>
> \- \`Mark\` (taches, motifs) : #7FA03E
>
> \- \`Extra\` (éléments spéciaux) : #6B4A2B
>
> \- \`Extra2\` (éléments spéciaux (2)) : #B9D36A
>
> \- \`White\` (yeux, dents) : #F2F2F2
>
> \- \`Black\` (pupilles) : #0A0A0A
>
> \### 3. MORPHOLOGIE ET STADE
>
> \- Amphiptère : corps de serpent sans pattes, le bas enroulé au sol et
> le haut dressé, deux ailes sur le haut du dos.
>
> \- Stade adulte : puissant et imposant, mâchoire carrée, 3 crocs par
> côté, musculature en grands blocs (pectoraux, épaules), cou de 5
> segments, très grandes cornes et ailes, jamais gore.
>
> \- Signes distinctifs (identiques aux trois stades) : bois en
> brindilles brunes avec bourgeons sur la tête ; liane brune enroulée en
> spirale autour du corps ; ailes en forme de grandes feuilles nervurées
> ; queue terminée par une feuille ; corps de serpent sans pattes.
>
> \- Description de ce stade : Grand serpent dressé presque à la
> verticale, le bas en anneaux au sol. Très grandes ailes-feuilles
> nervurées dressées vers le haut. Bois de brindilles ramifiés couverts
> de bourgeons. Yeux jaunes perçants, crocs fins. Lianes brunes en
> spirale serrée sur tout le corps.
>
> \### 4. ANATOMIE ET PROPORTIONS (unités avant mise à l\'échelle
> finale)
>
> \- Corps de serpent : 21 segments de (0, 0, 3.45) à (0.35, 0.88, 0.5),
> largeur 1.14 → 0.42, plaques de ventre, écailles sur les côtés ; le
> bas forme une spirale posée au sol (centre (0, 1.3, 0.5), rayon 0.95 →
> 0.55).
>
> \- Tête : crâne (1.04, 1.04, 0.91) centré en (0, -0.32, 3.81).
>
> \- Ailes (leaf) partant des omoplates en (0.47, 0.38, 2.97) : bras
> osseux jusqu\'au poignet (2.11, 0.9, 4.3) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 8.12.
>
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Liane enroulée en spirale autour du corps.
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
