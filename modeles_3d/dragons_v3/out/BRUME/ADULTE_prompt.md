Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Brume » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le dragon « Adulte Brume » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Brume = Ténèbres, Légendaire, Rapide, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur l'Adulte Brume : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Long dragon oriental de brume qui flotte en S, tête haute en avant : cou qui descend vers le poitrail, dos qui remonte, creux puis queue qui remonte et se dissout. Puissant mais élégant, mystérieux, jamais effrayant.
- Tête : grosse tête (échelle 1.3) à museau long et carré avec narines, mâchoire lilas, yeux en amande lavande lumineux à pupille fendue, sourcils d'argent sévères, 3 crocs fins par côté, lune d'argent sur le front (anneau, gemme lavande, 2 pointes d'argent) et bandeau d'argent, oreilles en éclats noirs avec nageoire de brume à 3 rayons, pointes de joue de brume, barbe de 5 brins de brume, 2 longues moustaches de brume (chaînes de 4 barres) terminées par une petite gemme lavande.
- Cornes : 2 longues cornes noires droites aux arêtes vives, couchées vers l'arrière, 3 anneaux d'argent chacune, plus 2 petites cornes noires basses qui partent vers l'extérieur.
- Crinière de brume : grand éventail de brume derrière la tête : 3 rangées de 12 brins (3 éclats plats par brin, violet moyen, clair et sombre, translucides), qui continue le long du cou et du dos avec 3 brins de 2 éclats à chaque segment. Matériaux translucides (alpha 0.5 à 0.62).
- Corps : segments violets biseautés, plaques de ventre lilas bien séparées, bandes plus claires sur les flancs, écailles dorsales sombres, veine lavande lumineuse sur chaque flanc, double rangée de pics noirs sur le dos, anneaux d'argent autour du corps (1 tous les 8 segments), collier d'argent au cou, plastron d'argent avec gemme lavande dans un anneau, épaulières d'argent à pic noir, 2 éclats de brume d'épaule.
- Ailes / nageoires : pas d'ailes (oriental) ; les nageoires sont en brume : oreilles, coudes, épaules.
- Pattes : 4 pattes qui pendent (épaule en bloc biseauté, avant-bras, bracelet d'argent, aileron de brume à 3 rayons au coude, pied avec 3 doigts et 3 griffes noires).
- Queue : les segments deviennent de la brume translucide à partir de 74 % du corps, avec des brins qui se détachent de chaque côté, puis un grand panache de 9 brins de brume (3 éclats) et un ornement d'argent au bout (anneau, gemme lavande, 4 éclats d'argent en étoile).
- Rendu de rareté : Légendaire : ornements d'argent métallique (lune, sourcils, plastron, épaulières, collier, anneaux, bracelets, anneaux de cornes), croissant d'aura derrière la tête (15 pointes d'argent et lavande, 7 gemmes lavande), veines lavande émissives, 16 FX flottants (éclats de brume et cristaux lavande) et 3 anneaux (argent et lavande).
- Palette (hex, Principled BSDF, couleurs saturées en espace linéaire) : Body #3A2766 (corps, crâne, pattes),
  ScaleA #2A1C4D (écailles du dos, oreilles), ScaleB #5A3F94 (arête du museau, flancs), Nostril #130D1D (narines, ligne de bouche),
  Belly #B8A2D6 (ventre, menton), Horn #1A1622 (cornes, pics, griffes), Silver #D6DAEA métallique 0.9 (tous les ornements),
  Mist #8F6FC8 alpha 0.55, MistLight #B8A2D6 alpha 0.50, MistDark #5E4496 alpha 0.62 (brume translucide),
  Eye #CDB3FF émissif #CDB3FF à 3.0 (yeux, gemmes), Glow #A98BFF émissif à 2.5 (veines, cristaux, FX),
  White #F2F2F2 (crocs, yeux de bébé), Black #0A0A0A (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin. Blocs biseautés, pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 15,000 triangles maximum après modificateurs (le script en fait environ 11 700, vise 75-95 %). Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, segments, pattes), jamais sur les éclats, cornes, griffes et cristaux. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRUME_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT,
  LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (ailerons de brume). Chaque pièce est parentée au bon root. Les pièces de la tête sont
  placées en coordonnées locales de HEAD_ROOT.
- Tout dans une collection « BRUME_ADULTE ». Le script est relançable : au début, il
  supprime uniquement les objets de cette collection et les enfants des roots
  BRUME_ADULTE_*. Il ne touche jamais aux autres modèles de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long du corps.
  Les points de contrôle et les rayons sont des listes faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour.
  Couleurs saturées en espace linéaire. Yeux, gemmes, veines et cristaux émissifs. Brume en alpha (mode BLENDED).
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 16 petits éléments flottants (éclats de brume et cristaux lavande) et les anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, point le plus bas à Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, épaisseur de la brume,
   taille des cornes) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
