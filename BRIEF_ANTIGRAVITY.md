# Dragon Pets Simulator : brief pour Antigravity

## Comment l'utiliser (pour toi, Raboul)

1. Crée un dossier de projet vide et mets-y ce dossier `antigravity` tel quel : `BRIEF_ANTIGRAVITY.md`, `default.project.json` et `src/` avec les deux fichiers Lua fournis.
2. Ouvre ce dossier dans Antigravity.
3. Colle le **Prompt maître** (partie 1) dans une première conversation. Ne demande rien d'autre dans ce message.
4. Ensuite, colle **un seul prompt de phase à la fois** (partie 3), dans l'ordre. Après chaque phase : teste dans Roblox Studio, vérifie la liste « Test », puis fais un commit Git.
5. Si l'agent casse quelque chose, reviens au dernier commit et redonne-lui la phase en lui collant le message d'erreur de la fenêtre Output de Studio.

Pourquoi pas tout d'un coup : un projet de cette taille ne tient pas dans un seul prompt. L'agent perdrait le fil, inventerait des fonctions qui n'existent pas et casserait le code déjà écrit. Les phases ci-dessous sont faites pour qu'il garde le contrôle, et pour que tu comprennes ce qui se passe.

Prérequis : Roblox Studio avec le plugin Rojo installé, Rojo en ligne de commande (via Rokit ou Aftman), Git. Si l'agent te demande d'installer quelque chose, laisse-le t'expliquer comment.

---

## 1. PROMPT MAÎTRE (à coller en premier)

```
Tu es mon développeur Roblox senior et mon professeur. Nous construisons ensemble un jeu Roblox appelé "Dragon Pets Simulator" (simulateur de collection de dragons avec combat). Le fichier BRIEF_ANTIGRAVITY.md contient tout le cahier des charges : lis-le en entier avant de faire quoi que ce soit.

Qui je suis : débutant complet en Lua et en Roblox. Je travaille seul. Explique-moi chaque étape simplement, en français, sans jargon inutile. À la fin de chaque phase, donne-moi la liste exacte de ce que je dois tester dans Roblox Studio.

Règles de travail (obligatoires) :
1. Langage : Luau (Roblox). Les noms dans le code (variables, fichiers, identifiants) sont en anglais ou en ASCII sans accent (ex : "Tenebres", "Epique"). Les textes affichés au joueur sont en français avec accents. Les commentaires sont en français.
2. Outil : Rojo. Tout le code vit dans le dossier src/ et est synchronisé vers Studio via default.project.json. Ne crée jamais de script directement dans Studio.
3. Le SERVEUR décide de tout ce qui compte : or, diamants, tirages d'œufs, dégâts, PV, échanges, achats. Le client affiche et envoie des demandes. Vérifie toujours côté serveur chaque demande reçue d'un RemoteEvent ou RemoteFunction (type, valeur, distance, délai entre deux demandes, possession).
4. Tous les chiffres d'équilibrage (prix, taux, PV, dégâts, durées) sont dans src/ReplicatedStorage/Shared/Config/. Jamais de chiffre magique dans la logique.
5. Code modulaire : un module = une responsabilité. Services serveur dans src/ServerScriptService/Services/, contrôleurs client dans src/StarterPlayer/StarterPlayerScripts/Controllers/.
6. N'invente jamais une API Roblox. Si tu n'es pas sûr qu'une fonction existe, dis-le et propose une alternative.
7. Travaille phase par phase. Ne commence pas la phase suivante tant que je n'ai pas confirmé que la phase en cours fonctionne. Ne réécris pas les fichiers des phases précédentes sans me prévenir et sans me dire pourquoi.
8. Les fichiers DragonModelBuilder.lua et DragonGalleryTest.server.lua sont déjà fournis et testés. Utilise-les tels quels, ne les réécris pas.
9. Pas d'asset externe (pas de modèle ou d'image de la Toolbox) : tout est fait avec des pièces et du code.
10. À chaque fin de phase, propose-moi un message de commit Git en français.
11. Si une demande de ma part contredit ces règles ou le brief, dis-le-moi et propose mieux avant de coder.
12. Les messages de debug utilisent print() préfixé par le nom du module, ex : print("[DataService] profil chargé"). Pas de spam dans la console.

Quand tu as lu le brief, réponds uniquement par : un résumé du jeu en 5 lignes, la liste des phases telles que tu les comprends, et les questions bloquantes éventuelles. Ne code rien encore.
```

---

## 2. CAHIER DES CHARGES (source de vérité pour l'agent)

### 2.1 Concept

Simulateur de collection de dragons avec combat. Le joueur farme de l'or, achète des œufs, obtient des dragons de plus en plus rares, les équipe, les fait évoluer (bébé, jeune, adulte), les envoie combattre des dragons sauvages pour en apprivoiser de nouveaux, avance de monde en monde (5 au lancement) et peut faire des rebirths. Public : tout public, plutôt enfants et jeunes ados. Pas de violence graphique.

### 2.2 Joueur

| Caractéristique | Valeur |
|---|---|
| Niveau max | 50 |
| PV | 100 au niveau 1, +15 par niveau |
| Dégâts du joueur | 5 au niveau 1, +1 par niveau |
| Vitesse de déplacement | 16 |
| Régénération | 2 % des PV max par seconde, uniquement hors combat (5 s sans toucher ni être touché) |
| Mort | respawn au point de départ du monde en cours, protection 3 s, perte de 5 % de l'or porté (plafonnée), jamais de perte de dragon |
| Slots d'équipement | 3 au départ, 5 avec le pass Équipe +2, 8 avec le pass Équipe +3 |

### 2.3 Éléments, forces, faiblesses

Identifiants : `Feu`, `Eau`, `Plante`, `Terre`, `Vol`, `Tenebres`, `Mineral` (affichage : Ténèbres, Minéral).

| Élément | Fort contre | Faible contre |
|---|---|---|
| Feu | Plante | Eau, Terre |
| Eau | Feu, Terre, Mineral | Plante |
| Plante | Eau, Terre | Feu, Vol |
| Terre | Feu, Vol | Eau, Plante |
| Vol | Plante | Terre, Tenebres, Mineral |
| Tenebres | Vol | Mineral |
| Mineral | Tenebres, Vol | Eau |

Multiplicateurs : attaque forte × 1,5 ; attaque faible × 0,75 ; neutre × 1. Un dragon de même élément que l'attaque subit × 0,75.

### 2.4 Statuts

| Statut | Effet | Durée | Source |
|---|---|---|---|
| Brulure | 3 % des PV max par seconde | 5 s | Feu |
| Gel | vitesse de déplacement et d'attaque −40 % | 4 s | Eau |
| Poison | 2 % des PV max par seconde, ne se cumule pas | 8 s | Plante |
| Etourdissement | cible immobilisée | 1,5 s | Terre |
| Peur | dégâts infligés −25 % | 5 s | Tenebres |

Chance d'application : 15 % par attaque (30 % pour Épique et plus). Un statut ne se réapplique pas pendant qu'il est actif. Les boss sont immunisés à l'étourdissement.

### 2.5 Raretés

| Rareté (id) | Dragons au lancement | Multiplicateur PV et dégâts | Bonus de farm (puissance) |
|---|---|---|---|
| Commun | 12 | × 1 | +10 % |
| Rare | 10 | × 1,5 | +25 % |
| Epique | 7 | × 2,2 | +60 % |
| Legendaire | 5 | × 3,3 | +150 % |
| Mythique | 3 | × 5 | +400 % |
| Secret | 2 | × 8 | +1 000 % |
| Mythe | 1 | × 12 | +3 000 % |
| Exclusif (payant) | 2 hors total | × 6 | +600 % |

### 2.6 Archétypes et stades

| Archétype (id) | PV | Dégâts | Vitesse |
|---|---|---|---|
| Equilibre | × 1 | × 1 | × 1 |
| Rapide | × 0,8 | × 0,8 | × 1,3 |
| Tank | × 1,4 | × 0,8 | × 0,8 |
| Brute | × 0,8 | × 1,4 | × 0,8 |

| Stade (id) | Niveaux du dragon | Multiplicateur de stats | Multiplicateur de bonus de farm |
|---|---|---|---|
| Bebe | 1 à 14 | × 0,4 | × 0,5 |
| Jeune | 15 à 34 | × 0,7 | × 0,8 |
| Adulte | 35 à 50 | × 1 | × 1 |

Le niveau max d'un dragon est 50. L'évolution est automatique au niveau du stade suivant, avec le modèle correspondant. Les dragons équipés gagnent de l'XP en combattant.

### 2.7 Formule des statistiques

```
stat finale = stat de base du monde × mult. rareté × mult. archétype × mult. stade × (1 + 0,06 × (niveau − 1))
```

Valeurs de base par monde d'origine :

| Monde | PV de base | Dégâts de base |
|---|---|---|
| 1 | 100 | 10 |
| 2 | 400 | 40 |
| 3 | 1 600 | 160 |
| 4 | 7 000 | 700 |
| 5 | 30 000 | 3 000 |

Vitesse : base 100, une attaque toutes les 1,5 s à 100 de vitesse (plus rapide au-dessus). Exemple de contrôle : Sillon (monde 1, Rare, Brute), Jeune, niveau 20 → PV ≈ 180, dégâts ≈ 31.

Un dragon à 0 PV est K.O. 10 s puis revient, il ne meurt jamais. La « puissance » est un bonus de farm indépendant des PV et dégâts : gain d'or = gain de base du monde × (1 + somme des puissances des dragons équipés × multiplicateur de stade) × boosts × bonus de rebirth.

### 2.8 Œufs

| Œuf | Obtention | Contenu |
|---|---|---|
| Commun du monde | boutique, or | Commun 60 %, Rare 30 %, Epique 9 %, Legendaire 1 % |
| RNG du monde | boutique, or | Rare 45 %, Epique 35 %, Legendaire 17 %, Mythique 3 % (4 % à partir du monde 4) |
| Aux diamants | boutique, diamants (150 au monde 1) | Epique 60 %, Legendaire 38 %, Mythique 2 % |
| Caché | trouvé en explorant | Commun ou Rare |
| De combat | chute sur dragon sauvage battu (5 à 15 %) | Commun ou Rare du monde |
| De dragon de zone | récompense du dragon de zone | le dragon de zone, garanti |
| Exclusif | un par monde, Robux | dragons exclusifs |

Secret et Mythe ne sortent d'aucun œuf standard : croisement mutant, monde 5, événements, récompenses de rebirth. Les tirages sont toujours faits côté serveur.

### 2.9 Combat, capture, dragons de zone

- Dragons sauvages dans le monde (une dizaine par zone), réapparition après 60 s. Combat : les dragons équipés attaquent automatiquement, le joueur peut aussi frapper et esquiver.
- Dégâts reçus par le joueur, en % de ses PV max par coup : bébé 3 %, jeune 6 %, adulte 10 %, élite 15 %.
- Victoire : XP, or, 1 diamant avec ~12 % de chance, chance d'œuf.
- Apprivoisement : seulement bébés et jeunes sauvages. Il faut descendre le dragon sous 30 % de PV puis utiliser un appât de son élément. 25 % de réussite de base, +10 % par appât de meilleure qualité. Échec : le dragon récupère 50 % de ses PV.
- Dragon de zone : un par monde, apparaît toutes les 30 min pour tous les joueurs du serveur. Chaque joueur qui lui a infligé au moins 5 % de ses PV reçoit un œuf de ce dragon, une fois par heure maximum.
- Diamants : ~12 % de chance par dragon battu, éclosion ou coffre caché.

### 2.10 Mondes

| Monde | Nom (provisoire) | Ambiance | Éléments | Dragons sauvages |
|---|---|---|---|---|
| 1 | La Plaine des Aurores | plaine, village, rivière, forêt claire (tutoriel) | Plante, Terre | bébés uniquement, une dizaine, peu agressifs |
| 2 | Les Dunes Ardentes | désert, canyons, oasis, temple ensablé | Feu (majorité), Terre | bébés, quelques jeunes |
| 3 | L'Archipel des Palmiers | plage, palmiers, lagon, îles reliées par des ponts | Eau (majorité), Plante | bébés et jeunes |
| 4 | La Flotte du Typhon | plusieurs bateaux dont un énorme navire central, typhon au milieu de l'eau | Eau, Vol, rarement Tenebres | jeunes, premiers adultes dans le typhon |
| 5 | L'Abysse de l'Épave | grotte sombre, cristaux, minerais, épave de dragon au point d'arrivée | Tenebres, Terre, Mineral | premiers adultes en nombre, 2 à 3 élites (Épique minimum, PV × 4) |

Au-delà du monde 5 : portails « Bientôt disponible », fermés. Le rebirth se débloque à partir du monde 3.

Prix et progression :

| Monde | Œuf commun | Œuf RNG | Temps visé pour un œuf (sans boost) |
|---|---|---|---|
| 1 | 100 or | pas d'œuf RNG | ~1 min |
| 2 | 400 or | 5 000 or | 2 min |
| 3 | 50 000 or | 800 000 or | 4 min |
| 4 | 2 milliards | 40 milliards | 8 min |
| 5 | 500 milliards | 10 000 milliards | 15 à 20 min |

Les gains d'or par action ne sont pas fixés : ils sont à régler en test pour atteindre les temps visés. Le joueur doit pouvoir accéder au monde 2 en 30 à 60 minutes.

Conditions de passage :

| Passage | Dragons différents obtenus | Niveau joueur | Niveau moyen de l'équipe | Boss de passage (PV) |
|---|---|---|---|---|
| 1 vers 2 | 5 | 3 | 5 | Gardien de la Plaine (1 500) |
| 2 vers 3 | 12 | 10 | 12 | Seigneur des Dunes (8 000) |
| 3 vers 4 | 20 | 20 | 22 | Kraken de Corail (50 000) |
| 4 vers 5 | 28 | 32 | 35 | Capitaine Typhon (400 000) |
| 5 vers 6 | 35 | 45 | 45 | Gardien de l'Épave (5 000 000) |

Le boss de passage est un combat unique, rejouable. Portail verrouillé tant que les conditions ne sont pas remplies, avec affichage de ce qui manque.

Dragons de zone (respawn 30 min) : M1 Aurore, M2 Solaris, M3 Neptyr, M4 Leviathan, M5 Quartz.

PV des dragons sauvages : M1 bébé 80 ; M2 bébé 250, jeune 600 ; M3 jeune 2 500 ; M4 jeune 10 000, adulte 35 000 ; M5 adulte 120 000, élite 600 000.

### 2.11 Liste des 40 dragons

Format : id, nom affiché, élément, rareté, archétype.

**Monde 1** : `Pousse` (Pousse, Plante, Commun, Equilibre) ; `Mottin` (Mottin, Terre, Commun, Tank) ; `Brindille` (Brindille, Plante, Commun, Rapide) ; `Galet` (Galet, Terre, Commun, Brute) ; `Trefle` (Trèfle, Plante, Rare, Equilibre) ; `Bruyere` (Bruyère, Terre, Rare, Tank) ; `Sillon` (Sillon, Terre, Rare, Brute) ; `Aurore` (Aurore, Plante, Epique, Equilibre).

**Monde 2** : `Braisillon` (Braisillon, Feu, Commun, Rapide) ; `Cendron` (Cendron, Feu, Commun, Equilibre) ; `Dune` (Dune, Terre, Commun, Tank) ; `Escarbille` (Escarbille, Feu, Rare, Brute) ; `Sirocco` (Sirocco, Feu, Rare, Rapide) ; `Magma` (Magma, Feu, Epique, Brute) ; `Mirage` (Mirage, Terre, Epique, Equilibre) ; `Solaris` (Solaris, Feu, Legendaire, Equilibre).

**Monde 3** : `Ecume` (Écume, Eau, Commun, Rapide) ; `Corail` (Corail, Eau, Commun, Tank) ; `Palmier` (Palmier, Plante, Commun, Equilibre) ; `Maree` (Marée, Eau, Rare, Equilibre) ; `Lagon` (Lagon, Eau, Rare, Rapide) ; `Perle` (Perle, Eau, Epique, Tank) ; `Liane` (Liane, Plante, Epique, Brute) ; `Neptyr` (Neptyr, Eau, Legendaire, Equilibre).

**Monde 4** : `Goeland` (Goéland, Vol, Commun, Rapide) ; `Mousse` (Mousse, Eau, Commun, Tank) ; `Rafale` (Rafale, Vol, Rare, Rapide) ; `Boussole` (Boussole, Eau, Rare, Equilibre) ; `Tempete` (Tempête, Vol, Epique, Brute) ; `Typhon` (Typhon, Eau, Legendaire, Brute) ; `Brume` (Brume, Tenebres, Legendaire, Rapide) ; `Leviathan` (Léviathan, Eau, Mythique, Tank).

**Monde 5** : `Stalactite` (Stalactite, Mineral, Rare, Tank) ; `Ombrelame` (Ombrelame, Tenebres, Epique, Rapide) ; `Quartz` (Quartz, Mineral, Legendaire, Equilibre) ; `Pepite` (Pépite, Mineral, Mythique, Brute) ; `Brillant` (Brillant, Mineral, Mythique, Tank) ; `Revenant` (Revenant, Tenebres, Secret, Brute) ; `Neant` (Néant, Tenebres, Secret, Rapide) ; `Aion` (Aïon, Tenebres, Mythe, Equilibre).

Exclusifs payants (2) : à définir plus tard, prévoir deux emplacements vides dans la config.

### 2.12 Croisement et mutation

- Deux dragons adultes du même élément dans l'incubateur de croisement. Coût en or, incubation 30 min, puis un œuf.
- Le dragon obtenu est de ce même élément, de rareté proche de celle des parents (même rareté ou une de moins, parfois une de plus).
- Œuf mutant : 0,1 % de chance (0,001). Contenu : dragon du même élément et d'une des raretés les plus hautes (Mythique, Secret ou Mythe).
- Les deux parents sont consommés. Un dragon Exclusif ne peut pas être croisé. Un même couple ne peut pas être recroisé avant 24 h.

### 2.13 Économie

- Or : farm actif, combats, vente de dragons. Diamants : rares (combats, éclosions, coffres, Robux).
- Rebirth (à partir du monde 3) : coût en or croissant. Gardé : dragons, diamants, mondes débloqués, Game Passes. Remis à zéro : or et niveau du joueur. Bonus par rebirth : +10 % d'or et +2 % de chance de raretés supérieures. Maximum 20 au lancement.
- Échanges entre joueurs : dragons échangeables entre joueurs, sauf tout ce qui a été payé en Robux. Prévoir le champ « échangeable » sur chaque dragon dès le début ; le système d'échange est activé après le lancement (voir phase 11).

### 2.14 Monétisation (prix en Robux, ajustables)

Game Passes : Équipe +2 (199), Équipe +3 (399, nécessite Équipe +2), Inventaire x2 (249), Éclosion rapide et auto (149), Or x2 permanent (499), Zone VIP (399).

Produits : Boost or x2 15 min (25), Boost or x2 30 min (45), Boost chance 15 min (49), Pack 100 diamants (49), Pack 500 diamants (199), Pack 1 500 diamants (499), Œuf exclusif du monde (149 à 599).

Les identifiants (IDs) Roblox des passes et produits ne sont pas encore créés : mettre `0` comme valeur provisoire dans Config/Monetization.lua et me dire où les remplacer.

### 2.15 Données sauvegardées

Par joueur : or, diamants, niveau, XP, rebirths, mondes débloqués, Game Passes, liste des dragons. Par dragon : identifiant unique (GUID), espèce (id), niveau, XP, stade, échangeable (oui ou non), date d'obtention.

Utiliser DataStoreService avec : pcall et nouvelles tentatives, UpdateAsync, cache en mémoire côté serveur, sauvegarde automatique toutes les 60 secondes, sauvegarde à la sortie du joueur et dans BindToClose, et un numéro de version du format de données pour pouvoir migrer plus tard. Ne jamais sauvegarder pendant que le chargement a échoué (sinon on écrase les données du joueur).

### 2.16 Structure du projet

```
default.project.json
src/
  ReplicatedStorage/Shared/
    Config/            (Rarities, Elements, Archetypes, Stages, Worlds, Dragons, Economy, Monetization, Combat)
    StatCalc.lua       (formules : stats d'un dragon, multiplicateurs d'éléments, puissance)
    DragonModelBuilder.lua   (FOURNI)
  ServerScriptService/
    Services/          (Data, Economy, Hatching, Pet, Combat, Capture, Breeding, World, Boss, Trade, Monetization)
    Dev/DragonGalleryTest.server.lua   (FOURNI, test)
  StarterPlayer/StarterPlayerScripts/
    Controllers/       (UI, PetFollow, Combat, ...)
```

---

## 3. PROMPTS DE PHASE (un à la fois, dans l'ordre)

### Phase 0. Mise en place

```
Phase 0 : mise en place.
1. Vérifie ce qui est installé (Rojo, Git) et dis-moi ce qui manque avec la façon exacte de l'installer.
2. Initialise Git avec un .gitignore adapté à Roblox/Rojo.
3. Crée l'arborescence décrite à la partie 2.16 du brief (dossiers vides inclus, avec un fichier .gitkeep si besoin). Utilise le default.project.json fourni.
4. Crée un petit script de test dans ServerScriptService/Services nommé HelloService.server.lua qui affiche un message dans Output.
5. Explique-moi comment lancer "rojo serve", me connecter depuis le plugin Rojo dans Studio, et vérifier que le message s'affiche.
Test attendu : je lance le jeu dans Studio et je vois le message dans Output. Ensuite supprime HelloService et propose un commit.
```

### Phase 1. Configuration et formules

```
Phase 1 : données de configuration et formules.
Crée dans src/ReplicatedStorage/Shared/Config/ les modules : Elements (forces, faiblesses, statuts), Rarities, Archetypes, Stages, Worlds (5 mondes, prix, conditions de passage, bosses, dragons de zone), Dragons (les 40 dragons de la partie 2.11 avec id, nom affiché, élément, rareté, archétype, monde), Economy (taux d'œufs, valeurs de rebirth, diamants), Combat (dégâts joueur, % de dégâts reçus par stade, durées de statuts).
Crée StatCalc.lua avec : getDragonStats(dragonId, stage, level) → PV, dégâts, vitesse ; getFarmPower(rarity, stage) ; getElementMultiplier(attackElement, defenderElement).
Ajoute un script de test (Dev/StatCalcTest.server.lua) qui affiche l'exemple de contrôle de la partie 2.7 (Sillon, Jeune, niveau 20 : PV ≈ 180, dégâts ≈ 31) et vérifie la table des éléments.
Test attendu : les valeurs affichées correspondent à l'exemple. Vérifie aussi qu'aucun dragon de la liste n'a un id, un élément ou une rareté inconnus.
```

### Phase 2. Sauvegarde et modèles de test

```
Phase 2 : sauvegarde des données et modèles de test.
1. Crée Services/DataService.lua selon la partie 2.15 du brief. API : DataService.getProfile(player), DataService.onProfileLoaded (signal), mise à jour de valeurs via des fonctions (pas d'écriture directe depuis l'extérieur). Format de données versionné.
2. Teste en sauvegardant une valeur "or" de test, quitte, reviens et vérifie qu'elle est restituée. Active "Enable Studio Access to API Services" si nécessaire et explique-moi comment.
3. Les fichiers DragonModelBuilder.lua et DragonGalleryTest.server.lua sont fournis. Vérifie qu'ils sont bien synchronisés, puis lance le jeu : la galerie doit afficher 4 rangées de dragons (éléments, raretés, stades, archétypes) devant le point (0, 4, -60).
4. Crée Shared/DragonModels.lua : une fonction getModel(dragonId, stage) qui lit la config Dragons (élément, rareté, archétype) et appelle DragonModelBuilder.build. Les vrais modèles pourront remplacer ce module plus tard sans toucher au reste du code.
Test attendu : les données sont sauvegardées entre deux sessions, la galerie est visible, aucune erreur dans Output.
```

### Phase 3. Monde 1 et farm

```
Phase 3 : monde 1 et farm d'or.
1. Construis par code (Script de génération Dev/BuildWorld1.server.lua, exécutable une fois) un monde 1 simple en blocs : sol vert, village de départ avec point d'apparition, une rivière en pièces bleues, quelques arbres faits de pièces, une zone de farm avec 3 mannequins d'entraînement.
2. Services/EconomyService.lua : le joueur frappe un mannequin (clic ou touche) et gagne de l'or. Serveur : vérifie la distance, un délai minimum entre deux coups, et calcule le gain (gain de base du monde × multiplicateurs).
3. Contrôleur client UIController : HUD simple en haut de l'écran avec l'or, qui se met à jour en temps réel.
4. L'or est stocké via DataService.
Test attendu : je frappe un mannequin, mon or augmente, il est sauvegardé. Un exploiteur qui envoie la demande trop vite ou de trop loin est ignoré.
```

### Phase 4. Œufs et inventaire

```
Phase 4 : œufs, éclosion et inventaire.
1. Services/HatchingService.lua : achat d'un œuf commun du monde 1 (100 or), tirage pondéré côté serveur avec les taux de Config/Economy (60 / 30 / 9 / 1), choix d'un dragon de la rareté tirée parmi les dragons du monde 1, ajout au profil via DataService (avec GUID, niveau 1, stade Bebe, échangeable = true).
2. Boutique d'œufs dans le monde (un stand avec un ProximityPrompt), animation d'éclosion simple côté client (œuf qui tremble puis le dragon apparaît avec son modèle de test et son nom/rareté).
3. Inventaire client : liste des dragons possédés avec nom, rareté, niveau, stade, aperçu en ViewportFrame avec le modèle de test.
4. Script de test Dev/HatchStatsTest.server.lua : simule 10 000 tirages et affiche la répartition obtenue (doit être proche des taux).
Test attendu : j'achète des œufs, je vois mes dragons dans l'inventaire, la répartition des 10 000 tirages est proche de 60/30/9/1 à environ 1 point près.
```

### Phase 5. Équipement et suivi des dragons

```
Phase 5 : équipement, suivi et multiplicateurs.
1. Services/PetService.lua : équiper et déséquiper un dragon (3 slots au départ, extensible à 5 puis 8 plus tard), validation côté serveur (le joueur possède le dragon, slot libre).
2. Contrôleur PetFollow : les dragons équipés suivent le joueur de façon fluide (interpolation avec lerp, positions autour du joueur, pas de lag réseau), sans collision, avec une animation simple (léger balancement).
3. EconomyService : le gain d'or utilise désormais la puissance des dragons équipés via StatCalc.getFarmPower.
4. UI : boutons pour équiper et déséquiper depuis l'inventaire, affichage du multiplicateur total.
Test attendu : j'équipe 3 dragons, ils me suivent, mes gains d'or augmentent selon leur rareté et leur stade.
```

### Phase 6. Combat

```
Phase 6 : combat.
1. Joueur : niveau, XP, PV (100 + 15 par niveau), régénération hors combat, mort et respawn selon la partie 2.2. Barre de PV dans le HUD.
2. Dragons sauvages dans le monde 1 : une dizaine de bébés qui se baladent, peu agressifs, avec PV 80 et une barre de vie. Réapparition après 60 s. Utilise DragonModels.getModel pour leur apparence (stade Bebe).
3. Services/CombatService.lua : les dragons équipés attaquent automatiquement le dragon ciblé selon leurs stats (StatCalc), cadence selon la vitesse, multiplicateurs d'éléments, statuts (brûlure, gel, poison, étourdissement, peur) avec leurs durées et chances. Les dragons du joueur à 0 PV sont K.O. 10 s puis reviennent.
4. Les dragons sauvages attaquent le joueur (3 % de ses PV max par coup pour un bébé).
5. Récompenses : XP, or, 12 % de chance de diamant. Affichage des dégâts flottants.
Test attendu : je combats un bébé, il perd des PV, je gagne XP et or, je peux mourir et réapparaître sans perdre de dragon. Rien d'important n'est calculé côté client.
```

### Phase 7. Capture, drops, diamants, évolution

```
Phase 7 : capture et évolution.
1. Services/CaptureService.lua : apprivoisement des bébés et jeunes sous 30 % de PV avec un appât de l'élément, chance de réussite selon la partie 2.9, échec = le dragon récupère 50 % de ses PV.
2. Drops d'œufs de combat (5 à 15 %) et œufs cachés dans le monde 1 (3 à 5 emplacements fixes).
3. Diamants : monnaie dans le HUD, œuf aux diamants dans la boutique (150 diamants).
4. Niveaux de dragon et évolution automatique Bebe → Jeune (niveau 15) → Adulte (niveau 35), avec changement de modèle et petite animation. Les dragons équipés gagnent de l'XP en combat.
Test attendu : je capture un bébé, mes dragons montent de niveau et évoluent, les diamants s'accumulent.
```

### Phase 8. Mondes 2 à 5, portails et boss

```
Phase 8 : mondes 2 à 5. Travaille un monde à la fois et demande-moi de valider avant le suivant.
Pour chaque monde : génération par code d'un décor simple en blocs correspondant à l'ambiance de la partie 2.10 (dev/BuildWorldN.server.lua), dragons sauvages avec leurs éléments et stades, boutique d'œufs et prix de la partie 2.10, œufs cachés, portail depuis le hub.
Services/WorldService.lua : conditions de passage (partie 2.10) vérifiées côté serveur, portail verrouillé avec affichage de ce qui manque. Services/BossService.lua : boss de passage (combat unique, rejouable) et dragon de zone toutes les 30 min avec récompense (≥ 5 % des PV du dragon infligés, une fois par heure). Dragons élites du monde 5.
Utilise les valeurs de Config, ne code rien en dur.
Test attendu pour chaque monde : je peux y accéder uniquement si j'ai les conditions, je peux acheter un œuf, combattre, battre le boss de passage et ouvrir le monde suivant.
```

### Phase 9. Croisement et rebirth

```
Phase 9 : croisement, mutation et rebirth.
1. Services/BreedingService.lua selon la partie 2.12 : deux adultes du même élément, coût en or, incubation 30 min (qui continue même si le joueur est déconnecté, avec timestamp), œuf obtenu, 0,1 % de chance d'œuf mutant, parents consommés, exclusifs refusés, même couple refusé pendant 24 h. Interface simple dans le hub.
2. Rebirth selon la partie 2.13 : disponible à partir du monde 3, coût croissant, bonus permanents, remise à zéro de l'or et du niveau du joueur uniquement.
Test attendu : un croisement produit un œuf, un script de test simule 100 000 croisements et affiche environ 0,1 % de mutants, un rebirth garde les dragons et améliore les gains.
```

### Phase 10. Monétisation

```
Phase 10 : monétisation (MarketplaceService).
Services/MonetizationService.lua : Game Passes et produits de la partie 2.14. Utilise ProcessReceipt correctement (enregistre les reçus déjà traités pour éviter de donner deux fois), vérifie les passes à la connexion. Effets : slots d'équipement 5 et 8, inventaire x2, éclosion rapide et auto, or x2, zone VIP, boosts temporaires avec timer sauvegardé, packs de diamants, œufs exclusifs payants.
Config/Monetization.lua avec les IDs à 0 pour l'instant, et dis-moi précisément comment créer les passes et produits dans le Creator Hub, puis où mettre les vrais IDs.
Test attendu : en mode test, je simule l'achat de chaque élément et l'effet s'applique, sans doublon en cas de reçu rejoué.
```

### Phase 11. Qualité, sécurité et mise en ligne

```
Phase 11 : qualité et préparation du lancement.
1. Relis tout le code côté serveur et liste toute faille d'exploit possible (RemoteEvents sans vérification, valeurs envoyées par le client, absence de limites de fréquence). Corrige, puis liste ce qui a été corrigé.
2. Teste la sauvegarde en cas de sortie brutale, en cas de DataStore indisponible, et à la fermeture du serveur.
3. Optimise : nombre de pièces des dragons, boucles coûteuses, réseau.
4. Désactive ou supprime les scripts Dev/ de test avant publication.
5. Prépare la fonction d'échanges entre joueurs (Services/TradeService.lua) mais laisse-la désactivée par un drapeau dans la config : double confirmation, validation serveur, journal des échanges, dragons payants intradables.
6. Donne-moi une checklist de lancement : paramètres du jeu dans le Creator Hub, classification de l'âge, icône, miniature, description, bêta fermée.
```

---

## 4. Modèles 3D de test (fichiers fournis)

- `src/ReplicatedStorage/Shared/DragonModelBuilder.lua` : construit un dragon avec des pièces Roblox selon l'élément (couleurs), la rareté (cornes, pics dorsaux, lueur, particules pour le Mythe), le stade (taille, tête de bébé plus grosse, ailes à partir de Jeune) et l'archétype (silhouette). Le dragon regarde vers −Z, son PrimaryPart est `Body`.
- `src/ServerScriptService/Dev/DragonGalleryTest.server.lua` : affiche 4 rangées de dragons pour voir le résultat dans Studio (éléments, raretés, stades, archétypes). À désactiver ou supprimer avant publication.

Utilisation rapide dans n'importe quel script serveur :

```lua
local Builder = require(game.ReplicatedStorage.Shared.DragonModelBuilder)
local dragon = Builder.build({ Name = "Braisillon", Element = "Feu", Rarity = "Commun", Stage = "Bebe", Archetype = "Rapide" })
dragon.Parent = workspace
dragon:PivotTo(CFrame.new(0, 5, 0))
```

Si un ajustement visuel est nécessaire (proportions, couleurs), dis à l'agent ce que tu veux changer et demande-lui de ne modifier que DragonModelBuilder.lua.
