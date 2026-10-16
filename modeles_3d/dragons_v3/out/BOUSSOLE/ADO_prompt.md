Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Boussole » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Ado Boussole » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Boussole = Eau, Rare, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de l'Ado Boussole : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : ado élancé, debout sur 4 pattes plus longues, cou de 4 maillons incliné vers l'avant, tête plus petite par rapport au corps, grandes ailes-voiles, queue plus longue.
- Tête : crâne en wedge, museau allongé avec arête gris-bleu et fine ligne dorée, mâchoire parchemin, ligne de bouche, 2 narines noires. Yeux latéraux plus sérieux : blanc, iris doré lumineux, pupille fendue, sourcils bleu très sombre soulignés d'un trait doré. 2 petits crocs crème par côté, oreille-nageoire bleue, 2 ailerons de joue et 2 nageoires arrière (laiton / gris-bleu) par côté.
- Signes distinctifs : ROSE DES VENTS dorée sur le front. 2 cornes en AIGUILLES DE BOUSSOLE (socle de laiton sombre, losange en laiton de 2 unités de long) : la gauche à pointe ROUGE, la droite à pointe laiton sombre ; chaque corne a une 2e pointe plus petite qui part vers l'avant et l'extérieur (rare : cornes plus travaillées).
- Corps : torse en 3 blocs, plastron parchemin avec rose des vents dorée sur la poitrine, 5 plaques de ventre parchemin + bandes sur le bas des flancs, 20 écailles bleues en quinconce (2 rangées de 5 par flanc), cou de 4 maillons (segment bleu + plaque parchemin + bague de laiton sombre à chaque joint + ailerons latéraux). Lignes de carte marine dorées : 1 parallèle en tirets, 1 route en 3 segments, 2 croix lumineuses par flanc. Crête double : rangée centrale de 5 éclats de laiton + 2 rangées latérales d'éclats bleu-gris. Petites plaques de laiton sur les épaules (wedge) + 1 pointe d'épaule.
- Ailes : ailes-voiles : bras et 3 doigts en laiton, membrane bleue, pointes de laiton sombre au bout des doigts, griffe crème au poignet, petite étoile lumineuse de rose des vents sur la voile.
- Pattes : 4 pattes : épaule et cuisse en wedge, tibia sombre, bracelet de laiton avec bague sombre, pied plat, 3 doigts + 3 griffes crème, 1 nageoire gris-bleu sur la cuisse.
- Queue : 7 segments bleus avec plaques de ventre parchemin, crête de laiton / gris-bleu, 2 bagues de laiton sombre, petites lignes dorées sur les côtés, terminée par une flèche de boussole dorée (hampe, pointe, 2 barbes, empennage rouge).
- Rendu de rareté (Rare), à mi-puissance : motif secondaire (carte marine), cornes à 2 pointes, crête double, accent lumineux discret (iris, rose, croix), 4 gouttes d'eau lumineuses et 4 étoiles dorées flottantes.
- Palette (hex, Principled BSDF mats) :
  Body #214C98 (corps bleu marine), ScaleA #17376F (écailles sombres, dessus des pattes), ScaleB #4F6C8C (écailles gris-bleu, ailerons),
  BodyDark #0F2650 (sourcils, bouche), Belly #F0E2BC (ventre en plaques, plastron, menton : parchemin),
  Brass #D9AA3E (laiton métallique 0.85, rugosité 0.28 : rose des vents, cornes, bracelets, os d'aile, crête centrale) et BrassDark #A87F28 (bagues, pointes),
  NeedleRed #D8362B (pointe rouge de la corne gauche, empennage), Membrane #5C98DA (voile des ailes), MapLine #E2B84A (lignes de carte, non émissif),
  MapMark #FFD060 (rose des vents, repères : émission #FFB830, strength 1.0), Claw #F0E2BC (griffes, crocs), EyeWhite #F4F4EA,
  Iris #F5B52E (émission #FFB82A, strength 1.2), Black #0A0A0A (pupilles, narines), Droplet #6FE0F0 (gouttes flottantes : émission #4FD8F0, strength 1.3).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les roses des vents sont des étoiles plates à 8 branches (éclats plats) avec un anneau.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, plaques d'épaule), jamais sur les petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BOUSSOLE_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BOUSSOLE_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BOUSSOLE_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de
  contrôle, les rayons et les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN,
  TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission faible seulement sur l'iris, la rose des vents, les croix et les gouttes (Rare : jamais plus de 1.5). Laiton métallique. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4102) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 8 petits éléments flottants (gouttes d'eau et étoiles dorées).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   la description et corrige les écarts visibles (couleurs, taille de la tête, ailes, détails)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
