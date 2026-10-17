Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Revenant » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Revenant = Ténèbres, Secret, Brute, morphologie Hydre ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Revenant : pose, proportions, chaque
élément des trois têtes, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : silhouette qui s'allonge, corps plus musclé sur 4 pattes, trois têtes sur des cous plus longs en S (la centrale plus grande, les latérales tournées de 22° vers l'extérieur), sans ailes.
- Têtes : crâne carré, museau en bloc avec arête d'os pâle, mâchoire d'os distincte et ligne de bouche, 2 narines noires, yeux en éclats lilas émissifs à pupille fendue, sourcils. Cous en s (4 segments, catmull-rom), 2 petits crocs d'os par côté, sourcils inclinés de 16°, yeux plus sérieux.
- Signe distinctif : trois têtes ; contours qui se dissipent en fumée violette translucide ; cornes sombres à anneau d'os, un feu follet lilas au bout de chaque corne, corne cassée sur la tête de droite.
- Corps : torse noir-violet très sombre, 4 côtes d'os apparentes sur le flanc gauche (vide lumineux), colonne d'os sur le dos, patte arrière gauche squelette, 2 plaques de voile déchiré qui pendent des épaules. Écailles en quinconce sur les flancs, plaques de ventre violettes bien séparées et plastron avec cristal lilas. 8 pics de crête translucides, 7 volutes de fumée violette sur le dos et la queue, 3 fissures lilas émissives sur les flancs.
- Ailes : aucune (hydre sans ailes), donc pas de WINGS_ROOT.
- Pattes : 4 pattes épaisses, 3 doigts et 3 griffes pâles, bracelets et genouillères d'os, fumée violette aux pieds.
- Queue : queue de 4,2 m qui devient fantôme puis se défait en 6 fragments translucides.
- Rendu de rareté (Secret) : Secret à mi-puissance : fissures émissives, voile déchiré translucide, tête gauche à mâchoire à moitié dissoute en fumée, corne cassée à droite (strength 2.6). FX flottants : 20 éclats d'os, perles de feu follet et lambeaux de fumée.
- Palette (hex, Principled BSDF) :
  Body #1A1420 (corps, crânes, cous), BodyDark #100C13 (genoux, épaules, sourcils), ScaleA #130F18 / ScaleB #322544 (écailles),
  Void #050308 (vide : orbites, cage thoracique, bouche), Nostril #0C090E, Belly #4E2E78 (ventre, plastron, gorge), Bone #D8CCEA (os apparents, museau, mâchoire, bracelets),
  HornTip #CDB3FF (pointes de cornes), Crest #8C64C8 et Crest2 #4E2E78 (crêtes translucides, alpha 0.62),
  Smoke #8C64C8 (alpha 0.55), SmokeLight #B79AEE (alpha 0.50), SmokeDark #4E2E78 (alpha 0.65) pour la fumée et les parties fantômes,
  Claw #E6DCF5, Eye #CDB3FF (émissif), Glow #CDB3FF (émissif : fissures, feux follets), WispViolet #8C64C8 (émissif : cœur des flammes), White #F2F2F2, Black #0A0A0A.
  Mêmes couleurs aux 3 stades.
- Style : low-poly en blocs biseautés, lisible de loin, étrange mais pas gore (aucun sang, pas de chair). Pas de sculpture
  organique.

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crânes, torse, bassin, premiers segments des cous), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty REVENANT_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT (tête centrale), HEAD2_ROOT (gauche), HEAD3_ROOT (droite), BODY_ROOT, LEGS_ROOT et TAIL_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de chaque tête sont placées en coordonnées locales
  de son root (placé à la base du crâne).
- Tout dans une collection « REVENANT_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots REVENANT_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Les trois cous suivent chacun une courbe Catmull-Rom rééchantillonnée à pas constant, avec un repère par segment et un rayon par clés (NECK_R). La queue de même.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur les yeux, fissures et feux follets ; fumée et crêtes en alpha 0.5 à 0.65. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5317) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les éclats et lambeaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 têtes,
  10 corps, 11 pattes, 12 ailes (aucune), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille des têtes, cous, fumée)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
