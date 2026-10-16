Aurore

Monde 1 · élément Plante · rareté Épique · archétype Équilibré ·
morphologie Oriental · dragon de zone

Aurore · Bébé

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Aurore » au stade BÉBÉ pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`AURORE_BEBE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`AURORE_BEBE\`. Préfixe tous les
> objets par \`AURORE_BEBE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`AURORE_BEBE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`AURORE_BEBE_BODY_ROOT\`, \`AURORE_BEBE_HEAD_ROOT\`,
> \`AURORE_BEBE_TAIL_ROOT\`, \`AURORE_BEBE_LEG_AV_ROOT\` (G et D),
> \`AURORE_BEBE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #8FA868
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #6A7C4D
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #9B9B6D
>
> \- \`Nostril\` (narines) : #404C2F
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E8DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A30
>
> \- \`HornTip\` (pointes des cornes, accents) : #F7C6CF
>
> \- \`Crest\` (sourcils, crêtes) : #F2A6A0
>
> \- \`Crest2\` (crête secondaire) : #F6C894
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F6C894
>
> \- \`Claw\` (griffes) : #E8DDB8
>
> \- \`Eye\` (iris) : #E0A21E --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #F7C6CF
>
> \- \`Extra2\` (éléments spéciaux (2)) : #D9B45A --- métallique
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
> \- Signes distinctifs (identiques aux trois stades) : bois de branches
> de cerisier en fleur ; crinière de pétales rose saumon et pêche ;
> longues moustaches dorées enroulées ; lianes fleuries le long du corps
> ; queue en touffe de pétales.
>
> \- Description de ce stade : Petit dragon oriental qui flotte, corps
> de serpent court en S, quatre petites pattes. Tête anguleuse, yeux en
> éclats lumineux dorés. Bois de branches brunes avec des fleurs de
> cerisier. Grosse crinière de pétales rose saumon et pêche autour de la
> tête. Deux longues moustaches dorées qui s\'enroulent. Lianes à
> petites fleurs roses le long du corps. Ventre crème. Queue terminée
> par une touffe de pétales.
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
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Petites fleurs sur le dos.
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

Aurore · Jeune (ado)

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Aurore » au stade JEUNE (ADO) pour mon
> jeu Roblox « Dragon Pets Simulator » (public enfants et jeunes ados),
> dans un style géométrique Roblox / Blocky Low-Poly : uniquement des
> cubes biseautés, des pyramides, des prismes et des plaques fines,
> comme mon bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`AURORE_JEUNE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`AURORE_JEUNE\`. Préfixe tous les
> objets par \`AURORE_JEUNE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`AURORE_JEUNE_MASTER_ROOT\` et, reliés à
> lui, ces contrôleurs placés aux articulations :
> \`AURORE_JEUNE_BODY_ROOT\`, \`AURORE_JEUNE_HEAD_ROOT\`,
> \`AURORE_JEUNE_TAIL_ROOT\`, \`AURORE_JEUNE_LEG_AV_ROOT\` (G et D),
> \`AURORE_JEUNE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #6B8A45
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #4F6633
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #828555
>
> \- \`Nostril\` (narines) : #303E1F
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E8DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A30
>
> \- \`HornTip\` (pointes des cornes, accents) : #F7C6CF
>
> \- \`Crest\` (sourcils, crêtes) : #F2A6A0
>
> \- \`Crest2\` (crête secondaire) : #F6C894
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F6C894
>
> \- \`Claw\` (griffes) : #E8DDB8
>
> \- \`Eye\` (iris) : #E0A21E --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #F7C6CF
>
> \- \`Extra2\` (éléments spéciaux (2)) : #D9B45A --- métallique
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
> \- Signes distinctifs (identiques aux trois stades) : bois de branches
> de cerisier en fleur ; crinière de pétales rose saumon et pêche ;
> longues moustaches dorées enroulées ; lianes fleuries le long du corps
> ; queue en touffe de pétales.
>
> \- Description de ce stade : Corps long en S, vert mousse. Crinière de
> pétales rose et doré plus ample, bois fleuris plus grands, moustaches
> dorées. Yeux dorés en amande. Fleurs le long du corps, queue en touffe
> de pétales.
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
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Petites fleurs sur le dos.
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

Aurore · Adulte

Prompt

> Agis comme un expert en modélisation 3D procédurale sur Blender (API
> Python \`bpy\` et \`bmesh\`).
>
> Écris un script Python complet, exécutable en une seule fois dans
> Blender, qui génère le dragon « Aurore » au stade ADULTE pour mon jeu
> Roblox « Dragon Pets Simulator » (public enfants et jeunes ados), dans
> un style géométrique Roblox / Blocky Low-Poly : uniquement des cubes
> biseautés, des pyramides, des prismes et des plaques fines, comme mon
> bébé dragon rouge de référence.
>
> \### 1. RÈGLES TECHNIQUES STRICTES
>
> \- Nettoyage : supprime le cube par défaut, supprime l\'ancienne
> collection \`AURORE_ADULTE\` si elle existe, puis range toutes les
> pièces dans une nouvelle collection \`AURORE_ADULTE\`. Préfixe tous
> les objets par \`AURORE_ADULTE\_\`.
>
> \- Axes : -Y = avant (le dragon regarde vers -Y), +Z = haut, sol en Z
> = 0. Rotations écrites en degrés.
>
> \- Hiérarchie : un \`Empty\` \`AURORE_ADULTE_MASTER_ROOT\` et, reliés
> à lui, ces contrôleurs placés aux articulations :
> \`AURORE_ADULTE_BODY_ROOT\`, \`AURORE_ADULTE_HEAD_ROOT\`,
> \`AURORE_ADULTE_TAIL_ROOT\`, \`AURORE_ADULTE_LEG_AV_ROOT\` (G et D),
> \`AURORE_ADULTE_LEG_AR_ROOT\` (G et D).
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
> \- \`Body\` (corps principal) : #4C6B33
>
> \- \`ScaleA\` (écailles imbriquées (sombre)) : #384F26
>
> \- \`ScaleB\` (écailles imbriquées (chaude)) : #6D7048
>
> \- \`Nostril\` (narines) : #223017
>
> \- \`Belly\` (ventre segmenté, plastron, menton) : #E8DDB8
>
> \- \`Horn\` (base des cornes) : #6B4A30
>
> \- \`HornTip\` (pointes des cornes, accents) : #F7C6CF
>
> \- \`Crest\` (sourcils, crêtes) : #F2A6A0
>
> \- \`Crest2\` (crête secondaire) : #F6C894
>
> \- \`Membrane\` (membranes, intérieur des oreilles) : #F6C894
>
> \- \`Claw\` (griffes) : #E8DDB8
>
> \- \`Eye\` (iris) : #E0A21E --- émissif
>
> \- \`Extra\` (éléments spéciaux) : #F7C6CF
>
> \- \`Extra2\` (éléments spéciaux (2)) : #D9B45A --- métallique
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
> \- Signes distinctifs (identiques aux trois stades) : bois de branches
> de cerisier en fleur ; crinière de pétales rose saumon et pêche ;
> longues moustaches dorées enroulées ; lianes fleuries le long du corps
> ; queue en touffe de pétales.
>
> \- Description de ce stade : Long dragon oriental majestueux, vert
> foncé. Grands bois de cerisier en pleine floraison. Crinière de
> pétales rose-pêche bordée de doré. Fleurs tout le long du corps. Yeux
> dorés lumineux, crocs fins, griffes. Queue en grande touffe de
> pétales.
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
> \- Crête dorsale : feuilles anguleuses le long de la nuque, du dos et
> de la queue.
>
> \- La crinière continue le long du haut du corps.
>
> \- Petites fleurs sur le dos.
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
