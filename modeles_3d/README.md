# Modèles 3D des dragons

Modèles faits dans Blender par scripts Python, pilotés depuis Claude via l'extension MCP de Blender.

![Bébé, ado et adulte (v3)](rendus/v3_bebe_ado_adulte.png)

## Démarche

1. **Formes d'abord** : modèle de base en gris perle, lisse, sans texture, pièces séparées (cornes, griffes, plaques, yeux, ailes).
2. **Allègement + dépliage (UV)** pour Roblox : ~4 000 triangles visés par pet, moins de 20 000 par pièce.
3. **Textures à la fin**, une par type de dragon (feu, glace, ombre…), posées sur le même modèle de base.

Les règles de forme (proportions bébé / ado / adulte) sont dans [GUIDE_FORMES.md](GUIDE_FORMES.md).

## État actuel : dragon classique, formes v3

| Stade | Référence | État |
|---|---|---|
| Bébé | bébé dragon assis, très mignon | Fait : tête ronde surdimensionnée, yeux bleu glacier à pupille fendue (regard innocent), pattes en « coussins » à 4 orteils, crête jusqu'au 1er tiers de la queue, pique en losange |
| Ado | esprit « jeune dragon de jeu de plateforme » (sans copier de personnage existant) | Fait : svelte et athlétique, cou plus long, regard déterminé, cornes recourbées, crête jusqu'au bout de la queue |
| Adulte | grand dragon western, en version lissée | Fait : long et sec, très long cou, tête haute, cornes à pointes secondaires, plaques d'armure, ailes immenses |

À affiner : paupières de l'adulte (trop bombées), coin des paupières de l'ado, museau de l'adulte vu de face.
Ensuite : allègement + UV, test d'import dans Roblox Studio, puis les autres types (wyvern, drake, hydre, oriental, amphiptère, aquatique) et les textures.

## Contenu

- `scripts_v3/` : **version actuelle**, à lancer dans l'ordre dans une scène vide :
  1. `commun.py` : outils partagés (chargé par les autres scripts, ne pas lancer seul)
  2. `01_bebe.py` : scène (caméra, éclairage studio, sol) + le bébé
  3. `02_ado.py` : l'ado
  4. `03_adulte.py` : l'adulte + rendu de groupe
  5. `04_export.py` : export FBX d'un fichier par stade dans `export/`
- `blend/Dragon_classique_v3.blend` : la scène v3. `export/dragon_classique_{bebe,ado,adulte}.fbx` : les modèles exportés.
- `scripts_v2/` + `blend/Dragon_classique_v2.blend` : essai intermédiaire (anciennes formes, couleurs unies et motifs nets façon jeux Roblox).
- `scripts/` + `blend/Dragon_classique.blend` : v1 (textures réalistes), abandonnée pour le style Roblox.
- `rendus/` : images de référence (`v3_*` = version actuelle).
- `archive_v1/` : toute première version (21 modèles simples générés d'un coup) et le module Luau de recoloration.

## Lancer les scripts

Dans Blender (onglet Scripting) ou via MCP :

```python
exec(open(r"chemin/vers/scripts_v3/01_bebe.py", encoding="utf-8").read(), {})
```

Les scripts cherchent `commun.py` dans le dossier donné par la variable `DIR` (chemin Windows par défaut) et écrivent leurs rendus dans `photo dragon\wip`. Adapter ces chemins si besoin. Passer `{"RENDER": False}` à `exec` pour sauter les rendus.

## Technique

- Corps : métaballs fondues en un seul maillage lisse ; muscles = volumes plus « durs » (stiffness élevée).
- Tête orientable : `Dragon.head_frame()` tourne toute la tête (volumes + pièces).
- Yeux : globe (sphère) à iris en dégradé + pupille fendue posée sur le globe, paupières = calottes + bourrelet.
- Crête : une plaque triangulaire par maillage, posée sur le dos par lancer de rayon.
