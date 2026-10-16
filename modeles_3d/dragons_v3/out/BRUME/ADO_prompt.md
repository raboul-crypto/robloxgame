Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Brume » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le dragon « Ado Brume » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Brume = Ténèbres, Légendaire, Rapide, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur l'Ado Brume : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Ado dragon oriental qui flotte en S, plus long et plus musclé que le bébé : tête en avant, cou qui descend vers le poitrail, dos qui remonte, creux, puis queue qui remonte. 4 pattes qui pendent.
- Tête : museau plus long, mâchoire lilas, yeux en amande lavande lumineux à pupille fendue, sourcils de brume, 1 croc fin par côté, lune d'argent sur le front (anneau, gemme lavande, 2 pointes d'argent) et bandeau d'argent, oreilles en éclats noirs, 3 brins de barbe de brume, 2 moustaches de brume plus courtes.
- Cornes : 2 cornes noires droites aux arêtes vives, couchées vers l'arrière (70 % de la taille adulte), avec 2 anneaux d'argent chacune.
- Crinière de brume : 2 rangées de 9 brins de brume (3 éclats plats par brin) derrière la tête, plus un brin sur trois segments le long du cou et du dos (3 brins de 2 éclats), violet translucide. Matériaux translucides (alpha 0.5 à 0.62).
- Corps : segments violets biseautés, plaques de ventre lilas séparées, bandes plus claires sur les flancs, écailles dorsales sombres, veine lavande lumineuse sur chaque flanc, une rangée de pics noirs sur le dos, collier et petit plastron d'argent (gemme lavande dans un anneau), épaulières d'argent à pic noir, 1 éclat de brume d'épaule.
- Ailes / nageoires : pas d'ailes (oriental) ; les nageoires sont en brume : oreilles, coudes, épaules.
- Pattes : 4 pattes qui pendent (épaule en bloc, avant-bras, bracelet d'argent, aileron de brume à 2 rayons au coude, pied avec 3 doigts et 3 griffes noires).
- Queue : se dissout en brume à partir de 80 % du corps (segments translucides et brins qui se détachent), panache de 5 brins de brume, ornement d'argent au bout (anneau, gemme lavande, 4 éclats d'argent).
- Rendu de rareté : le Légendaire à mi-puissance : lune d'argent, plastron, épaulières, collier et bracelets d'argent, croissant d'aura derrière la tête (9 pointes d'argent et lavande, 4 gemmes), veines lumineuses, ornement de queue, 10 FX flottants (éclats de brume et cristaux lavande) et 2 anneaux.
- Palette (hex, Principled BSDF, couleurs saturées en espace linéaire) : Body #432D75 (corps, crâne, pattes),
  ScaleA #31215A (écailles du dos, oreilles), ScaleB #634AA0 (arête du museau, flancs), Nostril #171024 (narines, ligne de bouche),
  Belly #B8A2D6 (ventre, menton), Horn #1A1622 (cornes, pics, griffes), Silver #D6DAEA métallique 0.9 (tous les ornements),
  Mist #8F6FC8 alpha 0.55, MistLight #B8A2D6 alpha 0.50, MistDark #5E4496 alpha 0.62 (brume translucide),
  Eye #CDB3FF émissif #CDB3FF à 3.0 (yeux, gemmes), Glow #A98BFF émissif à 2.5 (veines, cristaux, FX),
  White #F2F2F2 (crocs, yeux de bébé), Black #0A0A0A (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin. Blocs biseautés sur les gros volumes.

CONTRAINTES TECHNIQUES
- Budget : 10,000 triangles maximum après modificateurs (le script en fait environ 7 500, vise 70-90 %). Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, segments, pattes), jamais sur les éclats, cornes, griffes et cristaux. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRUME_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT,
  LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (ailerons de brume). Chaque pièce est parentée au bon root. Les pièces de la tête sont
  placées en coordonnées locales de HEAD_ROOT.
- Tout dans une collection « BRUME_ADO ». Le script est relançable : au début, il
  supprime uniquement les objets de cette collection et les enfants des roots
  BRUME_ADO_*. Il ne touche jamais aux autres modèles de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long du corps.
  Les points de contrôle et les rayons sont des listes faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour.
  Couleurs saturées en espace linéaire. Yeux, gemmes, veines et cristaux émissifs. Brume en alpha (mode BLENDED).
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 10 petits éléments flottants (éclats de brume et cristaux lavande) et les anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, point le plus bas à Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, épaisseur de la brume,
   taille des cornes) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
