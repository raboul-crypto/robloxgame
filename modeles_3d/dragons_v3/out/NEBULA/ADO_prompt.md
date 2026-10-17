Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Nébula » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades du dragon Nébula (Bébé, Ado, Adulte) si tu en as une ; sinon la
   description ci-dessous fait foi. Seul l'Ado Nébula est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau « Dragons exclusifs (payants) » : Nébula = Ténèbres, Exclusif, Rapide, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Nébula (ou ce que la description impose) : pose,
proportions, chaque élément de la tête, du corps, des ailes ou ailerons, des pattes et de la queue, et la
palette. Puis liste les contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Ado oriental qui flotte en croissant de lune, plus long et plus musclé, tête relevée.
- Tête : crâne en bloc, museau plus long avec arête violette, mâchoire distincte, ligne de bouche, narines. Yeux étoilés plus sérieux : fond nuit, étoile blanche, anneau supérieur violet, sourcils sombres inclinés. 2 petits crocs par côté. Étoile frontale dans un croissant, oreilles et 2 pointes de joue en nébuleuse. Barbe de 3 éclats.
- Cornes et crinière : 2 cornes noires en croissant (chaîne de 4 barres) avec étoile bleu pâle et éperon ; crinière de 3 rangées de 11 éclats nébuleux ; moustaches en rubans nébuleux ; halo de 9 étoiles.
- Corps : colonne en croissant, segments noir / violet / pourpre, plaques de ventre séparées, écailles dorsales, bandes de nébuleuse bleu / rose / violet sur les flancs, étoiles émissives, crinière de nébuleuse le long du cou et du dos, plastron avec étoile et éclats en cadre, 3 éclats d'épaule par côté.
- Ailes : aucune (oriental).
- Pattes : 4 pattes violettes à épaule, jambe haute et basse, bracelet sombre avec étoile, éperon de coude, 3 doigts + 3 griffes blanches.
- Queue : collier sombre, 7 éclats de comète, 2 étoiles, ailerons de nébuleuse sur la fin.
- Rendu de rareté (Exclusif, mi-puissance) : 2 anneaux d'orbite avec des étoiles, 26 étoiles flottantes.
- Palette (hex, Principled BSDF mats) :
  Void #150B2E (corps, crâne), Violet #43248A (flancs, pattes, museau), Purple #6A3FC8 (écailles du dos, plastron), Deep #24124A (sourcils, bracelets, bouche),
  Belly #8863E6 (plaques du ventre), Horn #1B1040 (cornes), EyeWhite #EDE6FF, EyeDark #0A0618, Claw #FFFFFF (griffes, crocs).
  Nébuleuse translucide émissive (alpha 0.78, émission 1.8) : NebulaV #8A4FE0, NebulaP #E05AC8, NebulaB #4A7FFF (crinière, bandes de flanc, moustaches, ailerons).
  Étoiles émissives : Star #FFFFFF (6.0), StarBlue #BFD6FF (5.0), StarPink #FFC4F2 (5.0). Ring #9B6CFF (anneaux d'orbite, émission 2.6).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les éclats et les
  étoiles sont des pièces plates et pointues.

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et seulement sur les gros
  blocs (crâne, museau, torse, segments), jamais sur les éclats, griffes, étoiles ou petites pièces. Le script
  affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty NEBULA_ADO_MASTER_ROOT avec ses enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas d'ailes). Chaque pièce est parentée au bon
  root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne).
- Tout dans une collection « NEBULA_ADO ». Le script est relançable : au début, il supprime uniquement les objets de
  cette collection et les enfants des roots NEBULA_ADO_*. Il ne touche jamais aux autres stades ni aux autres
  dragons de la scène.
- Le corps (cou, ventre, queue) suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon par clés. Les points de contrôle (CTRL), RADIUS_KEYS et SEG_STEP sont des variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées en espace
  linéaire. Émission sur les étoiles, la nébuleuse et les anneaux (rareté Exclusif). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (9091) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 26 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec l'image (ou la description)
   et corrige les écarts visibles (couleurs, taille de la tête, ailes, motifs) avant de me le rendre.
   Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
