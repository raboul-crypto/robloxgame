Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Aïon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Aïon = Ténèbres, Mythe, Équilibré, morphologie Oriental ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur l'Adulte Aïon : pose,
proportions, chaque élément de la tête, du corps, des pattes et de la queue, et la palette.
Puis liste les contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : dragon oriental primordial qui flotte, corps en S. Tête haute en avant, cou qui descend vers
  le poitrail, dos qui monte puis creux, queue qui remonte et se redresse. Posé sur ses 4 petites pattes.
- Tête : Museau long et carré avec narines, mâchoire distincte, yeux en amande or lumineux à pupille fendue, sourcils sévères dorés, 3 crocs par côté, 5 éclats d'oreille par côté, barbe de 5 éclats, 2 longues moustaches dorées. Narines noires, joyau violet lumineux sur le front.
- Cornes et couronne : grands bois dorés ramifiés (6 ramifications par côté), couronne d'or complète (bandeau, 3 pointes centrales, ailes, 2 gemmes latérales, joyau violet frontal dans un cadre d'or).
- Crinière : crinière immense en 4 rangées de 20 éclats (violet vif, violet profond, or), crinière de nuque en 2 rangées sur tout le cou. Ce sont des éclats larges et plats, pas des piques fines.
- Corps : long corps en S (~18 m), ventre en plaques violet clair, bandes claires sur les flancs, runes et sabliers dorés sur tout le corps, constellations émissives (étoiles blanc-violet reliées par des traits), bandes d'or, double rangée de pics dorés, crête de losanges violets, plastron d'or avec gemme et sablier, 2 épaulières d'or à 3 pointes.
- Ailes : aucune (oriental). Les épaulières et la crinière servent d'ornements.
- Pattes : 4 pattes à épaule wedge, avant-bras, bracelet d'or avec gemme, pointe de coude, pied à 3 doigts et 3 griffes pâles.
- Queue : collier d'or, grand cristal violet, éventail de 9 plumes violettes et or, 6 pétales, anneau runique et sablier final lumineux.
- Rendu de rareté (Mythe, la plus haute du jeu) : halo cosmique derrière la tête (4 anneaux violet / or / blanc / or lumineux, 20 éclats, étoiles, 10 runes), 4 anneaux runiques flottants inclinés autour du corps (or ou violet, 12 runes et étoiles chacun), 24 étoiles + 5 anneaux + 3 sabliers flottants. Tout est émissif violet, or ou blanc étoile.
- Palette : corps #4A2B8C ; écailles sombres, narines et bouche #2A1660 ; arête du museau et bandes des flancs
  #7448C8 ; ventre #9467E8 ; or ancien métallique #E8C35A (cornes, couronne, plastron, runes, bracelets) ;
  or vif #FFD45A (pointes, accents) ; crinière violet vif #8A4DFF et violet profond #5A2FBF ; émission or
  #FFD45A (yeux, runes lumineuses) ; émission violette #A56BFF (halo, gemmes, anneaux) ; étoiles #EBDDFF ;
  traits de constellation #8D5CFF ; blanc yeux et crocs #F2F2F2 ; pupilles #0A0612 ; griffes #F2E6B8.
  (Bébé et Ado utilisent les mêmes teintes, un peu plus sombres sur le corps.)
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 20000 triangles maximum après modificateurs, avec un biseau d'un seul segment sur les gros
  blocs seulement (pas sur les éclats, griffes, runes, petites pièces).
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty AION_ADULTE_MASTER_ROOT avec pour enfants AION_ADULTE_HEAD_ROOT, AION_ADULTE_BODY_ROOT,
  AION_ADULTE_LEGS_ROOT, AION_ADULTE_TAIL_ROOT. Les pièces de la tête sont en coordonnées locales de HEAD_ROOT.
  Les FX, le halo et les anneaux flottants sont reliés au MASTER ou à la tête.
- Tout dans une collection « AION_ADULTE ». Le script est relançable : il supprime l'ancienne collection et les
  anciens objets de ce stade avant de recréer.
- Le corps suit une courbe Catmull-Rom (points de contrôle CTRL) rééchantillonnée à pas constant, avec un
  repère par segment et un rayon par clés (RADIUS_KEYS).
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Émission pour les yeux,
  runes lumineuses, étoiles, halo et gemmes.
- Seed aléatoire fixe (5005) pour que le dragon soit identique à chaque exécution.
- Option ADD_FLOATING_FX = True/False pour les éléments flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (palette, hiérarchie, tête, corps, pattes,
  ailes, queue, rareté / FX, finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec l'image et corrige les
   écarts visibles avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
