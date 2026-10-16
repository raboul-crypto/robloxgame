Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Brume » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le dragon « Bébé Brume » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Brume = Ténèbres, Légendaire, Rapide, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Brume : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Bébé dragon oriental compact et mignon, posé au sol sur 4 petites pattes épaisses. Corps court en S (tête, cou, dos qui monte, creux, queue qui remonte), grosse tête (environ 35 % de la hauteur) en avant.
- Tête : museau court et carré avec narines, mâchoire lilas, TRÈS GRANDS yeux (blanc, grand iris lavande lumineux, pupille ronde noire, petit reflet blanc), sourcils de brume doux, pas de crocs, petite lune d'argent (anneau avec gemme lavande) sur le front, 2 oreilles en éclats noirs, 2 pointes de joue de brume, 2 petites moustaches de brume.
- Cornes : 2 petites cornes noires droites aux arêtes vives (blocs sans biseau), couchées vers l'arrière, avec 1 anneau d'argent chacune. Pas de petites cornes basses.
- Crinière de brume : 2 rangées de 8 brins de brume (2 éclats plats par brin, violet translucide) derrière la tête, plus un brin sur trois segments le long du cou et du dos (3 brins de 2 éclats), très translucides. Matériaux translucides (alpha 0.5 à 0.62).
- Corps : segments violets biseautés, plaques de ventre lilas bien séparées, bandes plus claires sur les flancs, écailles dorsales sombres. Pas de veines lumineuses ni de pics. Collier d'argent au cou.
- Ailes / nageoires : pas d'ailes (oriental) ; les nageoires sont en brume : oreilles, coudes, épaules.
- Pattes : 4 petites pattes courtes et épaisses posées au sol (épaule en bloc, avant-bras, bracelet d'argent, pied avec 3 doigts et 3 griffes noires). Pas d'aileron de coude.
- Queue : s'affine, les derniers segments deviennent de la brume translucide avec quelques brins qui se détachent, panache de 4 brins de brume au bout, petit ornement d'argent (anneau, gemme lavande, 4 éclats d'argent en étoile).
- Rendu de rareté : le Légendaire est présent en touche : lune d'argent, 1 anneau d'argent par corne, bracelets et collier d'argent, mini croissant d'aura derrière la tête (7 pointes d'argent et lavande, 3 gemmes lavande), ornement de queue, 6 FX flottants (éclats de brume et cristaux lavande) et 1 anneau flottant.
- Palette (hex, Principled BSDF, couleurs saturées en espace linéaire) : Body #4E3485 (corps, crâne, pattes),
  ScaleA #38266B (écailles du dos, oreilles), ScaleB #6E52AE (arête du museau, flancs), Nostril #1C132A (narines, ligne de bouche),
  Belly #B8A2D6 (ventre, menton), Horn #1A1622 (cornes, pics, griffes), Silver #D6DAEA métallique 0.9 (tous les ornements),
  Mist #8F6FC8 alpha 0.55, MistLight #B8A2D6 alpha 0.50, MistDark #5E4496 alpha 0.62 (brume translucide),
  Eye #CDB3FF émissif #CDB3FF à 3.0 (yeux, gemmes), Glow #A98BFF émissif à 2.5 (veines, cristaux, FX),
  White #F2F2F2 (crocs, yeux de bébé), Black #0A0A0A (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin. Blocs biseautés plus généreux, rond et mignon.

CONTRAINTES TECHNIQUES
- Budget : 6,000 triangles maximum après modificateurs (le script en fait environ 4 400, vise 70-90 %). Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, segments, pattes), jamais sur les éclats, cornes, griffes et cristaux. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRUME_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT,
  LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (ailerons de brume). Chaque pièce est parentée au bon root. Les pièces de la tête sont
  placées en coordonnées locales de HEAD_ROOT.
- Tout dans une collection « BRUME_BEBE ». Le script est relançable : au début, il
  supprime uniquement les objets de cette collection et les enfants des roots
  BRUME_BEBE_*. Il ne touche jamais aux autres modèles de la scène.
- Le corps suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long du corps.
  Les points de contrôle et les rayons sont des listes faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour.
  Couleurs saturées en espace linéaire. Yeux, gemmes, veines et cristaux émissifs. Brume en alpha (mode BLENDED).
  Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (4417) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 6 petits éléments flottants (éclats de brume et cristaux lavande) et les anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, point le plus bas à Z = 0.
- Code commenté en français, découpé en sections numérotées.

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, épaisseur de la brume,
   taille des cornes) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
