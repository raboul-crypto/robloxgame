# Paquet voxel pour raboul-crypto/robloxgame

Copier le contenu de ce dossier à la racine du dépôt (les chemins correspondent déjà à `default.project.json` / Rojo).

## Fichiers

- `src/ReplicatedStorage/Shared/VoxelDragonBuilder.lua` : nouveau. Construit un dragon voxel en Parts (fusionnées), avec effet de particules selon l'élément. Cache par espèce + stade, puis `Clone()`.
- `src/ReplicatedStorage/Shared/VoxelDragons/*.lua` : nouveau. 42 modules de données (une espèce = 3 stades).
- `src/ReplicatedStorage/Shared/DragonModels.lua` : **remplace** l'existant. Utilise le voxel si disponible, sinon l'ancien `DragonModelBuilder` (inchangé).
- `src/ServerScriptService/Dev/VoxelGalleryTest.server.lua` : galerie de test (mettre `ENABLED = false` avant publication).
- `modeles_3d/voxel/` : viewer autonome (export OBJ/GLB par dragon) et prompts.

Aucun autre fichier du jeu n'est modifié : `PetFollowController` appelle déjà `DragonModels.getModel`.

## Correspondance des identifiants

Tous les Id de `Config/Dragons.lua` sont couverts sauf `Exclusif1` (Dragon Flamboyant, Feu), qui garde l'ancien modèle.
- `Exclusif2` (Dragon du Crépuscule) = Nébula du viewer.
- `Prisma` (Vol) est fourni mais n'est relié à aucun Id : à renommer en `Exclusif1` si tu veux l'utiliser (élément différent).

## Chiffres

- 1 cellule = 0,16 stud (adulte ≈ 8 studs ; Léviathan et Aïon × 1,35).
- Parts par modèle : bébé 140–370, adulte 330–1 130 (Magma et Prisma les plus lourds).
