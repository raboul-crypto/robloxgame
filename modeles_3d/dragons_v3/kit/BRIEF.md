# Brief sous-agent : un dragon, 3 stades, 3 prompts + 3 scripts Blender

Tu travailles pour Raboul (étudiant dev, projet Roblox « Dragon Pets Simulator »). Tout ce que tu écris
(prompts, commentaires de code) est en **français**, ton direct et simple, sans emojis.

Le but : refaire son ancien document de scripts Blender (42 dragons × 3 stades) au niveau de qualité de
son nouvel exemple, l'**Adulte Mirage v3**, et rendre chaque dragon **plus stylé selon sa rareté**, avec
plus de détails. Tu t'occupes d'UN dragon (indiqué dans ta mission) et de ses 3 stades : BEBE, ADO, ADULTE.

## Fichiers à lire avant de commencer (dans /home/claude/work)

1. `ref/mirage_adulte_prompt.txt` — **le format de prompt à reproduire** (structure, ton, niveau de précision).
2. `ref/mirage_adulte_ref.py` — **la barre de qualité du code** (lis-le en entier : formes biseautées,
   crinière en éclats, ventre en plaques séparées, cristaux en grappes, bracelets, griffes, seed fixe...).
3. `kit/kit.py` — les fonctions communes (sections 1 à 6) qui seront injectées dans chaque script.
   Tu NE les réécris PAS : tu les appelles. Liste : `hex_lin, get_mat, mesh_from, box_mesh, wedge_mesh,
   shard_mesh, crystal_mesh, prism_mesh, ring_mesh, plate_mesh, basis, place, box, wedge, shard,
   crystal, prism, ring, plate, link, chain, empty, pick, catmull, sample_curve, resample, frame,
   keyed, seg_matrix, wing, finalize`. Si tu as besoin d'une forme en plus, écris ta propre fonction
   dans ta partie du script (après `# @@KIT@@`), en bmesh/from_pydata.
4. `kit/template.py` — le début obligatoire de chaque script (en-tête, réglages, nettoyage, `# @@KIT@@`).
5. `data/<SLUG>.md` — l'ancien prompt du dragon pour ses 3 stades : palette hex, signes distinctifs,
   description de chaque stade, proportions. C'est ta source pour l'identité du dragon.
6. `ref/concepts/<SLUG>.jpg` **si le fichier existe** — l'image de concept (Bébé en bas à gauche, Ado au
   milieu, Adulte en haut à droite). Regarde-la avec l'outil Read. Si elle existe, **l'image gagne pour
   l'apparence** (couleurs, formes, accessoires) ; l'ancien prompt sert pour le reste.

## Ce que tu livres

Dans `/home/claude/work/out/<SLUG>/` :
- `BEBE.py`, `ADO.py`, `ADULTE.py` — le script de chaque stade : copie de `kit/template.py` remplie
  (placeholders `{...}` remplacés, lignes de description de l'en-tête écrites), la ligne `# @@KIT@@`
  laissée telle quelle, puis ta partie (sections 7 à 15). Termine par `finalize(master)`.
- `BEBE_prompt.md`, `ADO_prompt.md`, `ADULTE_prompt.md` — le prompt de chaque stade (format plus bas).
- `report.json` — `{"slug": ..., "stages": {"BEBE": {"tris": n, "objects": n, "notes": "..."}, ...}}`.

Tester : `cd /home/claude/work && python3 build.py out/<SLUG>/ADULTE.py --render`
→ affiche le nombre de triangles, la taille, minZ, et crée `renders/<SLUG>_ADULTE.png` (3/4 avant) et
`renders/<SLUG>_ADULTE_side.png` (profil). **Ouvre les deux images avec Read et corrige ce qui cloche**
(pièces qui flottent, vides entre cou/corps/pattes, ailes à l'envers, tête trop petite, couleurs ternes,
silhouette illisible). Fais au moins 2 tours rendu → correction par stade. Compare avec le concept si
tu en as un. Ne modifie jamais `kit/`, `build.py`, `run_check.py`, ni les dossiers des autres dragons.
La machine n'a que 2 CPU partagés entre plusieurs agents : lance un seul rendu à la fois, sans `&`.

## Réglages imposés

- `SEED` : un entier fixe propre au dragon (le même pour les 3 stades).
- `TARGET_HEIGHT` : BEBE 4, ADO 7, ADULTE 11 (mètres). `finalize` met le dragon à cette hauteur, pieds
  (ou ventre) sur Z = 0, centré. Construis donc à n'importe quelle échelle, mais de façon cohérente.
- `BEVEL_SEGMENTS = 1`. Biseau seulement sur les gros blocs (`bevel=` > 0) ; pas de biseau sur les éclats,
  griffes, cristaux, petites pièces.
- `TRI_BUDGET` selon le tableau ci-dessous. **Vise 70 à 100 % du budget** : plus la rareté est haute, plus
  il y a de détails. Ne dépasse jamais le budget avec `BEVEL_SEGMENTS = 1` et `ADD_FLOATING_FX = True`.

| Rareté | BEBE | ADO | ADULTE |
|---|---|---|---|
| Commun | 3000 | 4500 | 6000 |
| Rare | 4000 | 6000 | 8000 |
| Épique | 5000 | 8500 | 13000 |
| Légendaire | 6000 | 10000 | 15000 |
| Mythique, Secret, Exclusif | 7000 | 11000 | 17000 |
| Mythe | 8000 | 13000 | 20000 |

## Hiérarchie (noms exacts, préfixe = TAG, par ex. `POUSSE_ADULTE_`)

`MASTER_ROOT` (PLAIN_AXES) avec pour enfants : `HEAD_ROOT`, `BODY_ROOT`, `LEGS_ROOT`, `TAIL_ROOT`, plus
`WINGS_ROOT` si le dragon a des ailes ou des nageoires, et `HEAD2_ROOT`, `HEAD3_ROOT` pour les hydres.
`HEAD_ROOT` est placé à la base du crâne (matrice translation + légère rotation) et **toutes les pièces de
la tête sont en coordonnées locales de HEAD_ROOT** (comme dans le Mirage). Chaque pièce est parentée au
bon root. Pas de squelette. FX flottants parentés au MASTER, créés seulement si `ADD_FLOATING_FX`.

## Stades (GDD partie 13)

- **BEBE** : mignon et arrondi (blocs biseautés plus généreux), grosse tête (~35 % de la hauteur), museau
  court, **très grands yeux brillants** (blanc + grand iris + pupille + petit reflet blanc), pattes courtes
  et épaisses, cornes et épines en version courte, pas de crocs. Il porte déjà en petit TOUS les signes
  distinctifs et la palette de l'adulte. Rendu de rareté présent mais discret.
- **ADO** : silhouette qui s'allonge, plus musclé, vraies griffes, petits crocs, yeux plus sérieux
  (sourcils), cornes / crinière / crête à mi-taille, rendu de rareté à mi-puissance.
- **ADULTE** : réaliste et puissant (épaules et cuisses en `wedge`, ventre en plaques séparées, griffes
  blanches, crocs, sourcils sévères), tous les signes distinctifs à pleine taille, rendu de rareté complet.
- **Continuité** : même palette hex et mêmes motifs aux 3 stades pour qu'on reconnaisse le bébé une fois
  adulte.

## Morphologies (GDD partie 13)

- **Classique** : 4 pattes + 2 ailes membraneuses (fonction `wing`), debout sur ses 4 pattes.
- **Wyvern** : 2 pattes arrière puissantes, les ailes servent de bras (le poignet de l'aile touche presque
  le sol ou se replie devant), posture penchée en avant.
- **Drake** : 4 pattes, pas d'ailes, massif, large, bas sur pattes.
- **Hydre** : 2 ou 3 têtes (3 à l'adulte) sur des cous en courbe (Catmull-Rom), corps massif, petites ailes
  ou aucune.
- **Oriental** : long corps de serpent en S qui flotte, 4 petites pattes, pas d'ailes (ou ailerons),
  moustaches, crinière — modèle direct : le Mirage.
- **Amphiptère** : corps de serpent avec ailes, sans pattes ; corps en S posé sur ses anneaux, ailes ouvertes.
- **Aquatique** : nageoires à la place des ailes (plaques avec rayons), queue de poisson (nageoire caudale
  en V), membres en palettes, crête dorsale en nageoire.
- Les corps longs (oriental, amphiptère, aquatique, cous d'hydre, queues longues) suivent une **courbe
  Catmull-Rom rééchantillonnée à pas constant**, avec un repère par segment et un rayon par clés
  (`CTRL`, `RADIUS_KEYS` en haut de la section, faciles à modifier), exactement comme le Mirage.

## Rendu de rareté — le cœur de la mise à jour

Chaque stade ajoute ce qui correspond à sa rareté (à l'ADULTE en entier, ADO environ 60 %, BEBE une touche) :

- **Commun** : silhouette propre et lisible, 3 à 5 couleurs, pas d'émission (sauf yeux possibles), 1 signe
  distinctif fort et bien dessiné. Détail = écailles, ventre en plaques, griffes, crête simple.
- **Rare** : + un motif secondaire (bandes, taches, veines claires), cornes plus travaillées (2 pointes ou
  ramifiées), crête double, **un accent lumineux discret** (yeux ou une marque émissive faible, strength ≤ 1.5).
- **Épique** : silhouette spectaculaire (crinière en éclats, grande crête, cornes imposantes), **éléments
  émissifs** (cristaux, veines, braises, fleurs lumineuses selon l'élément, strength 2-3), petits ornements
  dorés (bracelets, plastron), FX flottants (6 à 14 petits éléments).
- **Légendaire** : tout l'Épique + **ornements d'armure/métal** (or ou argent métallique, couronne,
  épaulières, plastron avec gemme), aura (anneau ou couronne d'éclats émissifs derrière la tête), double
  rangée de pics, FX flottants plus nombreux et plus grands, queue avec un ornement final marquant.
- **Mythique** : matériau précieux sur une grande partie du corps (or massif, diamant facetté, metallic
  0.6-1.0, roughness basse), gemmes multiples, **halo flottant** derrière la tête, éclats émissifs partout,
  FX denses (anneau de pièces / éclats en orbite).
- **Secret** : identité étrange et inquiétante (spectral, os apparents, vide, fissures émissives, parties
  semi-transparentes avec `alpha` 0.5-0.7), silhouette déchirée/asymétrique, yeux émissifs, FX de fragments.
- **Exclusif** : thème cosmétique très fort (Prisma : couleurs arc-en-ciel qui changent segment par segment ;
  Nébula : noir/violet avec étoiles émissives et crinière en nébuleuse), émission sur les motifs, FX à thème.
- **Mythe** (Aïon) : le plus spectaculaire du jeu : couronne, plusieurs anneaux runiques flottants (`ring`),
  halo cosmique, constellations émissives sur le corps, crinière immense, FX très riches.

Couleurs par élément (GDD) : Feu rouge/orange, Eau bleu/turquoise, Plante vert/brun clair, Terre brun/ocre,
Vol blanc/bleu ciel, Ténèbres violet/noir, Minéral gris pierre + reflets du minerai. Garde la palette hex
de l'ancien prompt, mais **sature-la si elle est terne** (le Mirage v1 virait au beige : à éviter).

## Qualité attendue du code (comme le Mirage v3)

- Sections numérotées et commentées en français (7. PALETTE, 8. HIÉRARCHIE, 9. TÊTE, 10. CORPS,
  11. PATTES, 12. AILES / NAGEOIRES, 13. QUEUE, 14. RENDU DE RARETÉ / FX, 15. FINALISATION).
- Tête détaillée : crâne + museau + arête du museau + mâchoire distincte + ligne de bouche, narines, yeux
  (blanc, iris, pupille ; fendue pour ado/adulte), sourcils, cornes/oreilles/joues, crocs (ado/adulte).
- Corps : segments, ventre en plaques crème bien séparées, écailles dorsales, flancs, signes distinctifs.
- Pattes : épaule/cuisse, avant-bras, bracelet ou genouillère selon la rareté, pied, 3 doigts + 3 griffes.
- Pièces symétriques dans `for sgn in (-1, 1):`, noms suffixés.
- Toutes les pièces s'interpénètrent un peu : **aucune pièce ne flotte** (sauf FX volontaires).
- Pas de `bpy.ops`. Le script tourne en une fois, sans erreur, dans Blender 4.x et 5.x.
- Positions et tailles clés en variables en haut des sections (HEAD_POS, CTRL, RADIUS_KEYS, LEG_*,
  WING_SPAN...) pour que Raboul puisse retoucher la forme facilement.

## Format du prompt (fichier `<STADE>_prompt.md`, texte brut, ~45-75 lignes)

Reprends la structure exacte de `ref/mirage_adulte_prompt.txt`, adaptée au dragon et au stade.
Nom affiché : « Bébé Pousse », « Ado Pousse », « Adulte Pousse ».

```
Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « <Stade> <Nom> » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. <Si concept :> Une image de concept montrant les 3 stades du dragon <Nom> (Bébé, Ado, Adulte).
   Seul le dragon <en bas à gauche / au milieu / en haut à droite>, nommé « <Stade> <Nom> », est à modéliser.
   <Sinon :> Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde <n> : <Nom> = <Élément>, <Rareté>, <Archétype>, morphologie <Morpho> ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
(identique au Mirage, adapté)

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : ...
- Tête : ...
- <Crinière / cornes / crête> : ...
- Corps : ...
- <Ailes / nageoires> : ...
- Pattes : ...
- Queue : ...
- Rendu de rareté (<Rareté>) : ce qui rend ce stade plus stylé (ornements, émission, FX...).
- Palette : liste des couleurs hex avec leur rôle.
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : <TRI_BUDGET> triangles maximum après modificateurs ...
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty <TAG>_MASTER_ROOT avec ses enfants ... Les pièces de la tête sont placées en
  coordonnées locales de HEAD_ROOT.
- Tout dans une collection « <TAG> ». Le script est relançable : ...
- <si corps long :> courbe Catmull-Rom ...
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. ... émissifs ...
- Seed aléatoire fixe ...
- Option ADD_FLOATING_FX ...
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale <4/7/11> m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
(identique au Mirage)
```

Le prompt doit décrire **exactement ce que fait ton script** (mêmes éléments, mêmes couleurs), pour que
Raboul puisse le redonner à une IA avec l'image et obtenir le même dragon ou demander une retouche.

## Fin de mission

Quand les 3 stades passent (`RESULT: OK`, triangles ≤ budget et ≥ ~70 % du budget, minZ ≈ 0, rendus
vérifiés), écris `report.json` et réponds en 5 lignes max : triangles par stade, ce qui rend chaque stade
stylé, et tout problème restant. Ne colle pas le code dans ta réponse.

## Retour du dragon pilote (Pousse) — à appliquer

- **Exemple terminé** : `out/POUSSE/` (3 scripts + 3 prompts) et `renders/POUSSE_*.png`. Lis `out/POUSSE/ADULTE.py`
  et `out/POUSSE/ADULTE_prompt.md` pour voir le niveau attendu. Bonne pratique reprise de lui : un même corps
  de script pour les 3 stades, avec un bloc « RÉGLAGES DU STADE » en haut (BW, BH, LEG_H, TORSO_L, NECK_L,
  HEAD_SCALE, WING_SPAN, TAIL_L, nombre de feuilles/pics...) qui change d'un stade à l'autre.
- `wing(..., bevel=0.0)` et `chain(..., bevel=None)` acceptent maintenant un paramètre `bevel` : les os d'aile
  ne sont plus biseautés par défaut (moins de triangles).
- Les feuilles/écailles plates en losange (`plate` à 4 points) lisent mieux que des éclats fins et coûtent peu.
- `finalize` mesure maintenant la vraie boîte après modificateurs : hauteur exacte et minZ = 0.
- Français du prompt : « sur l'Adulte Pousse », « sur l'Ado Pousse », « sur le Bébé Pousse ».

## Reprise (20 h 40) — à lire aussi

- Une première série d'agents a été interrompue. Si `out/<SLUG>/` contient déjà des `BEBE.py`, `ADO.py`,
  `ADULTE.py`, **pars de ces fichiers** : rends-les, compare au concept, améliore-les, puis termine ce qui
  manque (prompts `*_prompt.md`, `report.json`). Ne repars de zéro que si un fichier est vraiment raté.
- Rendus : `build.py --render` utilise maintenant le moteur **Workbench** (environ 6 s pour les deux vues).
  Workbench montre les couleurs des matériaux mais **pas la lueur de l'émission** : c'est normal. Pour un
  contrôle final de l'émission, une fois par stade au plus : `RENDER_ENGINE=CYCLES python3 build.py ... --render`.
- Un hook de sécurité peut te demander de « présenter des faits » avant ta première commande Bash ou avant
  d'écrire un fichier pour la première fois : réponds-y en 2-4 lignes (ce que fait la commande / quel
  fichier, pourquoi), puis relance la même opération.
- Dans les prompts, écris « l'Adulte <Nom> », « l'Ado <Nom> », « le Bébé <Nom> » (jamais « le Adulte »).
- Dragons sans image de concept (mondes 3, 4, 5, exclusifs, et Cendron) : `data/<SLUG>.md` fait foi pour
  l'identité ; ton prompt utilise la variante « Une image de concept des 3 stades si tu en as une ; sinon
  la description ci-dessous fait foi » et la description doit alors être assez précise pour se suffire.
- Exemples terminés à lire pour ta morphologie (dès qu'ils existent, avec `report.json`) : Classique
  `out/POUSSE/`, Drake `out/MOTTIN/`, Amphiptère `out/BRINDILLE/`, Wyvern `out/BRAISILLON/`,
  Oriental `out/MIRAGE/`, Hydre `out/MAGMA/`, Aquatique `out/ECUME/`. Inspire-toi de leur structure, mais
  ton dragon doit avoir sa propre identité (signes distinctifs, palette, rendu de rareté).
