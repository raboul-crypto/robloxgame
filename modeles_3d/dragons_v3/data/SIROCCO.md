Sirocco

Monde 2 · élément Feu · rareté Rare · archétype Rapide · morphologie
Amphiptère

Sirocco · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sirocco » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SIROCCO_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SIROCCO_BEBE\`. Préfixe tous les
> objets par \`SIROCCO_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SIROCCO_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`SIROCCO_BEBE_BODY_ROOT\`, \`SIROCCO_BEBE_HEAD_ROOT\`,
> \`SIROCCO_BEBE_TAIL_ROOT\`, \`SIROCCO_BEBE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #D9502A
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #A13B1F
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #CD5624
>
> \- \`Nostril\` (narines) : #622413
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBCB9A
>
> \- \`Horn\` (base des cornes) : #6A4026
>
> \- \`HornTip\` (pointes des cornes, accents) : #D1A04A --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #F28A1E
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8321E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F28A1E
>
> \- \`Claw\` (griffes) : #6A4026
>
> \- \`Eye\` (iris) : #E8B04A --- émissif
>
> \- \`Mark\` (taches, motifs) : #E8B04A
>
> \- \`Glow\` (parties lumineuses) : #FFC93A --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : motifs de
> volutes (tourbillons de vent chaud) dorés sur le corps ; ailes aux
> bords découpés en flammes ; cornes recourbées vers l\'arrière.
>
> \- Description de ce stade : Petit serpent enroulé, haut du corps
> dressé. Rouge-orange, ventre sable. Volutes dorées sur le corps. Deux
> cornes dorées recourbées vers l\'arrière. Collerette orange. Petites
> ailes orange aux bords en flammes. Yeux en éclats lumineux.
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
> \- Ailes (flame_edge) partant des omoplates en (0.54, 0.45, 2.42) :
> bras osseux jusqu\'au poignet (1.38, 0.72, 3.11) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 4.87.
>
> \- La crinière continue le long du haut du corps.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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

Sirocco · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sirocco » au stade JEUNE (ADO) pour
> mon jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes
> ados), dans un style géométrique Roblox / Blocky Low-Poly : uniquement
> des cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SIROCCO_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SIROCCO_JEUNE\`. Préfixe tous
> les objets par \`SIROCCO_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SIROCCO_JEUNE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`SIROCCO_JEUNE_BODY_ROOT\`, \`SIROCCO_JEUNE_HEAD_ROOT\`,
> \`SIROCCO_JEUNE_TAIL_ROOT\`, \`SIROCCO_JEUNE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #B03F20
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #822F18
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #B14B1D
>
> \- \`Nostril\` (narines) : #4F1C0E
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBCB9A
>
> \- \`Horn\` (base des cornes) : #6A4026
>
> \- \`HornTip\` (pointes des cornes, accents) : #D1A04A --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #F28A1E
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8321E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F28A1E
>
> \- \`Claw\` (griffes) : #6A4026
>
> \- \`Eye\` (iris) : #E8B04A --- émissif
>
> \- \`Mark\` (taches, motifs) : #E8B04A
>
> \- \`Glow\` (parties lumineuses) : #FFC93A --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : motifs de
> volutes (tourbillons de vent chaud) dorés sur le corps ; ailes aux
> bords découpés en flammes ; cornes recourbées vers l\'arrière.
>
> \- Description de ce stade : Dressé en S. Cornes brunes recourbées,
> crête en flammes. Volutes. Ailes rouge-orange découpées en flammes.
> Yeux ambre.
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
> \- Ailes (flame_edge) partant des omoplates en (0.38, 0.41, 2.79) :
> bras osseux jusqu\'au poignet (1.67, 0.82, 3.84) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 6.47.
>
> \- La crinière continue le long du haut du corps.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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

Sirocco · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Sirocco » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`SIROCCO_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`SIROCCO_ADULTE\`. Préfixe tous
> les objets par \`SIROCCO_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`SIROCCO_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`SIROCCO_ADULTE_BODY_ROOT\`, \`SIROCCO_ADULTE_HEAD_ROOT\`,
> \`SIROCCO_ADULTE_TAIL_ROOT\`, \`SIROCCO_ADULTE_WING_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #8A2E18
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #662212
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #973F18
>
> \- \`Nostril\` (narines) : #3E150B
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #EBCB9A
>
> \- \`Horn\` (base des cornes) : #6A4026
>
> \- \`HornTip\` (pointes des cornes, accents) : #D1A04A --- métallique
>
> \- \`Crest\` (sourcils, crêtes) : #F28A1E
>
> \- \`WingBone\` (os des ailes / rayons des nageoires) : #C8321E
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F28A1E
>
> \- \`Claw\` (griffes) : #6A4026
>
> \- \`Eye\` (iris) : #E8B04A --- émissif
>
> \- \`Mark\` (taches, motifs) : #E8B04A
>
> \- \`Glow\` (parties lumineuses) : #FFC93A --- émissif
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
> \- Signes distinctifs (identiques aux trois stades) : motifs de
> volutes (tourbillons de vent chaud) dorés sur le corps ; ailes aux
> bords découpés en flammes ; cornes recourbées vers l\'arrière.
>
> \- Description de ce stade : Grand serpent dressé. Immenses ailes en
> flammes, en dégradé rouge, orange, jaune, avec des volutes. Longues
> cornes brunes. Crocs.
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
> \- Ailes (flame_edge) partant des omoplates en (0.47, 0.38, 2.97) :
> bras osseux jusqu\'au poignet (2.11, 0.9, 4.3) (pointe sur
> l\'articulation), 3 doigts osseux qui s\'écartent vers
> l\'arrière/l\'extérieur, membranes triangulaires tendues entre les os.
> Envergure ≈ 8.12.
>
> \- La crinière continue le long du haut du corps.
>
> \- Motifs (swirls) répartis sur les flancs du torse et de la queue, en
> plaques très fines posées sur la peau.
>
> \- Bandes de vent argentées enroulée en spirale autour du corps.
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
