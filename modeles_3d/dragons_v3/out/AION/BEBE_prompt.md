Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Aïon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Aïon = Ténèbres, Mythe, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Aïon : pose,
proportions, chaque élément de la tête, du corps, des pattes et de la queue, et la palette.
Puis liste les contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : dragon oriental primordial qui flotte, corps en S. Tête haute en avant, cou qui descend vers
  le poitrail, dos qui monte puis creux, queue qui remonte et se redresse. Posé sur ses 4 petites pattes.
- Tête : Grosse tête (~35 % de la hauteur), museau court et carré, très grands yeux (blanc, grand iris or lumineux, pupille ronde, reflet blanc), pas de crocs, sourcils discrets dorés, 3 éclats d'oreille par côté, barbe de 3 éclats. Narines noires, joyau violet lumineux sur le front.
- Cornes et couronne : petits bois dorés (1 branche principale + 2 ramifications), couronne d'or minuscule (bandeau + 3 pointes + joyau violet frontal).
- Crinière : crinière violette et dorée en 2 rangées de 14 éclats derrière la tête, petite crinière de nuque. Ce sont des éclats larges et plats, pas des piques fines.
- Corps : corps court en S (segments biseautés, ventre en plaques violet clair, écailles dorsales sombres), quelques runes et sabliers dorés espacés, 1 petite constellation, petite crête de losanges, petit plastron d'or avec gemme.
- Ailes : aucune (oriental). Les épaulières et la crinière servent d'ornements.
- Pattes : 4 petites pattes épaisses (épaule en wedge, avant-bras, bracelet d'or, pied à 3 doigts et 3 griffes pâles).
- Queue : bout de queue avec collier d'or, petit cristal violet, éventail de 5 plumes, 4 pétales, petit anneau et sablier doré.
- Rendu de rareté (Mythe, la plus haute du jeu) : petit halo cosmique derrière la tête (2 anneaux + 10 éclats + runes), 1 anneau runique flottant autour du corps, 6 étoiles + 2 anneaux + 1 sablier flottants (ADD_FLOATING_FX). Tout est émissif violet, or ou blanc étoile.
- Palette : corps #4A2B8C ; écailles sombres, narines et bouche #2A1660 ; arête du museau et bandes des flancs
  #7448C8 ; ventre #9467E8 ; or ancien métallique #E8C35A (cornes, couronne, plastron, runes, bracelets) ;
  or vif #FFD45A (pointes, accents) ; crinière violet vif #8A4DFF et violet profond #5A2FBF ; émission or
  #FFD45A (yeux, runes lumineuses) ; émission violette #A56BFF (halo, gemmes, anneaux) ; étoiles #EBDDFF ;
  traits de constellation #8D5CFF ; blanc yeux et crocs #F2F2F2 ; pupilles #0A0612 ; griffes #F2E6B8.
  (Bébé et Ado utilisent les mêmes teintes, un peu plus sombres sur le corps.)
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 8000 triangles maximum après modificateurs, avec un biseau d'un seul segment sur les gros
  blocs seulement (pas sur les éclats, griffes, runes, petites pièces).
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty AION_BEBE_MASTER_ROOT avec pour enfants AION_BEBE_HEAD_ROOT, AION_BEBE_BODY_ROOT,
  AION_BEBE_LEGS_ROOT, AION_BEBE_TAIL_ROOT. Les pièces de la tête sont en coordonnées locales de HEAD_ROOT.
  Les FX, le halo et les anneaux flottants sont reliés au MASTER ou à la tête.
- Tout dans une collection « AION_BEBE ». Le script est relançable : il supprime l'ancienne collection et les
  anciens objets de ce stade avant de recréer.
- Le corps suit une courbe Catmull-Rom (points de contrôle CTRL) rééchantillonnée à pas constant, avec un
  repère par segment et un rayon par clés (RADIUS_KEYS).
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Émission pour les yeux,
  runes lumineuses, étoiles, halo et gemmes.
- Seed aléatoire fixe (5005) pour que le dragon soit identique à chaque exécution.
- Option ADD_FLOATING_FX = True/False pour les éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (palette, hiérarchie, tête, corps, pattes,
  ailes, queue, rareté / FX, finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec l'image et corrige les
   écarts visibles avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
