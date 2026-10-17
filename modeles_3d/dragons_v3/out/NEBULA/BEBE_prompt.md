Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Nébula » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades du dragon Nébula (Bébé, Ado, Adulte) si tu en as une ; sinon la
   description ci-dessous fait foi. Seul le Bébé Nébula est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau « Dragons exclusifs (payants) » : Nébula = Ténèbres, Exclusif, Rapide, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Nébula (ou ce que la description impose) : pose,
proportions, chaque élément de la tête, du corps, des ailes ou ailerons, des pattes et de la queue, et la
palette. Puis liste les contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Bébé oriental en petit croissant de lune posé au sol, corps court et épais, tête énorme (environ 35 % de la hauteur), queue qui remonte en comète.
- Tête : crâne et museau courts noirs, arête du museau violette, mâchoire et ligne de bouche, narines. Très grands yeux : fond nuit, grande étoile blanche à 4 branches, petit reflet rose. Pas de crocs, sourcils discrets. Étoile frontale dans un support avec 2 éclats de croissant bleu et rose.
- Cornes et crinière : 2 petites cornes noires en croissant avec une étoile bleue ; crinière nébuleuse de 2 rangées de 7 éclats translucides violet / rose / bleu ; 2 courtes moustaches en ruban de nébuleuse ; mini halo de 4 étoiles.
- Corps : colonne en croissant (courbe Catmull-Rom) épaisse, segments noir / violet / pourpre, plaques de ventre violet clair séparées, écaille dorsale par segment, bandes de nébuleuse bleu / rose / violet qui tournent d'un segment à l'autre sur les flancs, étoiles émissives à 4 branches sur les flancs et le dos, petite crinière de nébuleuse le long du dos, plastron avec étoile.
- Ailes : aucune (oriental) ; éclats de nébuleuse en ailerons sur les épaules.
- Pattes : 4 petites pattes violettes épaisses, bracelet sombre avec une étoile bleue, 3 doigts + 3 griffes blanches.
- Queue : petit collier sombre, 5 éclats de comète et 2 grandes étoiles au bout.
- Rendu de rareté (Exclusif, discret) : étoiles et nébuleuse émissives, 1 anneau d'orbite avec 3 étoiles, 10 étoiles flottantes.
- Palette (hex, Principled BSDF mats) :
  Void #150B2E (corps, crâne), Violet #43248A (flancs, pattes, museau), Purple #6A3FC8 (écailles du dos, plastron), Deep #24124A (sourcils, bracelets, bouche),
  Belly #8863E6 (plaques du ventre), Horn #1B1040 (cornes), EyeWhite #EDE6FF, EyeDark #0A0618, Claw #FFFFFF (griffes, crocs).
  Nébuleuse translucide émissive (alpha 0.78, émission 1.8) : NebulaV #8A4FE0, NebulaP #E05AC8, NebulaB #4A7FFF (crinière, bandes de flanc, moustaches, ailerons).
  Étoiles émissives : Star #FFFFFF (6.0), StarBlue #BFD6FF (5.0), StarPink #FFC4F2 (5.0). Ring #9B6CFF (anneaux d'orbite, émission 2.6).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les éclats et les
  étoiles sont des pièces plates et pointues.

CONTRAINTES TECHNIQUES
- Budget : 7000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et seulement sur les gros
  blocs (crâne, museau, torse, segments), jamais sur les éclats, griffes, étoiles ou petites pièces. Le script
  affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty NEBULA_BEBE_MASTER_ROOT avec ses enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas d'ailes). Chaque pièce est parentée au bon
  root. Les pièces de la tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne).
- Tout dans une collection « NEBULA_BEBE ». Le script est relançable : au début, il supprime uniquement les objets de
  cette collection et les enfants des roots NEBULA_BEBE_*. Il ne touche jamais aux autres stades ni aux autres
  dragons de la scène.
- Le corps (cou, ventre, queue) suit une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon par clés. Les points de contrôle (CTRL), RADIUS_KEYS et SEG_STEP sont des variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées en espace
  linéaire. Émission sur les étoiles, la nébuleuse et les anneaux (rareté Exclusif). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (9091) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 10 éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec l'image (ou la description)
   et corrige les écarts visibles (couleurs, taille de la tête, ailes, motifs) avant de me le rendre.
   Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
