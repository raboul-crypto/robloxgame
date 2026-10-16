Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Léviathan » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Léviathan = Eau, Mythique, archétype Tank, morphologie Aquatique, dragon de zone (boss du monde 4) ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Léviathan : pose, proportions, chaque
élément de la tête, du corps, des nageoires (à la place des ailes), des pattes-palettes et de la queue de poisson, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (la description fait foi si tu n'as pas d'image)
- Pose : Ado plus long et musclé : 4 pattes-palettes (LEG_TH 0.9), cou qui s'allonge (NECK_L 2.6), tête plus petite (HEAD_SCALE 1.4), torse allongé, queue de poisson plus longue (TAIL_L 5.6).
- Tête : crâne en wedge biseauté, museau large (SNOUT_K 1.0) avec arête en plaque métallique, mâchoire pâle distincte avec menton, ligne de bouche, 2 narines. Yeux fendus sérieux : blanc, iris cyan lumineux, pupille fendue, sourcils obliques en plaque d'acier. 2 petits crocs nacrés par côté. 3 plaques métalliques sur le crâne, plaques de joues et de museau, 3 points lumineux cyan par côté sur le museau et 2 lignes lumineuses par côté. 2 épines turquoise du front par côté, 2 nageoires de joue par côté.
- Signes distinctifs : COURONNE DE 7 CORNES NACRÉES en arc derrière le crâne (HORN_L 0.9, la corne du milieu est la plus longue) ; GEMME cyan à 8 faces sertie sur le front (monture métallique à 6 griffes, GEM_R 0.34), 1 gemme(s) saphir par côté sur le crâne ; 2 grandes NAGEOIRES-OREILLES turquoise / saphir / cyan à 6 rayons métalliques (EAR_L 2.8) ; crête-nageoire du crâne (6 rayons, hauteur 1.2) ; HALO FLOTTANT derrière la tête : anneau lumineux cyan (rayon 2.0, 20 côtés) avec 6 gemmes cyan et saphir en orbite ; PLAQUES BLINDÉES sur le dos ; NAGEOIRES IMMENSES ; POINTS ET LIGNES BIOLUMINESCENTS cyan partout.
- Corps : torse en segments biseautés sur une courbe Catmull-Rom (pas 0.5), bleu abyssal, plaques de ventre pâles bien séparées, DOS BLINDÉ : une plaque métallique en wedge par segment (platine bleuté et acier abyssal en alternance), ligne lumineuse cyan au sommet de chaque plaque, pointe métallique sur une plaque sur deux. Sur les flancs : 2 rangée(s) de points bioluminescents et une ligne lumineuse par segment, 3 rangées d'écailles turquoise en quinconce. Plastron métallique avec grande gemme cyan et 1 gemme(s) saphir par côté. Crête-nageoire dorsale continue (hauteur 1.2) à rayons métalliques, crinière de 2 nageoires par segment de cou et par côté.
- Nageoires : à la place des ailes : 2 pectorales IMMENSES en éventail sur les épaules (7 rayons métalliques, envergure PEC_SPAN 5.4, pointe métallique au bout du grand rayon, 1 point(s) lumineux sur chaque rayon), sur une base blindée ; 2 pelviennes (4 rayons) sur les hanches. Membranes translucides turquoise, saphir et cyan clair en alternance. Point lumineux au bout de chaque rayon.
- Pattes : 4 pattes-palettes bleu roi : cuisse en wedge, épaulière blindée en platine, jambe, genouillère métallique, bracelet d'acier avec point lumineux, grand pied plat, 3 doigts palmés + 3 griffes nacrées, petite nageoire de coude à 3 rayons.
- Queue : queue de poisson de 5.6 de long (pas 0.5) : segments qui s'affinent et s'aplatissent, plaques blindées sur les 70 % avant, ventre pâle, écailles, points et lignes lumineux, crête-nageoire continue, 1 paire(s) de nageoires latérales, collier métallique avec gemme cyan, nageoire caudale en V (2 lobes de 5 rayons, 2.6 de long).
- Rendu de rareté (Mythique) : à mi-puissance : plaques sur le dos, la tête et les épaules, 3 sortes de gemmes, halo avec 6 gemmes. FX denses : 18 éclats de cristal, perles et bulles en orbite autour du corps (ellipse) et 6 bulles qui montent.
- Palette (hex, Principled BSDF) :
  Body #123C7C (corps bleu abyssal, métal 0.10), BodyScale #1FB4C8 (écailles, crêtes), Leg #0F4E96 (pattes), BodyDark #081C40 (ombres), Belly #B8E6F4 (ventre, mâchoire),
  Fin #22C4DA / FinDeep #2F6FD8 / FinLight #8CF0F4 (membranes, alpha 0.82), FinRay #7FA9D0 (rayons, métal 0.85), Horn #F0F8FA (cornes nacrées), Claw #F4FAFC (griffes, crocs),
  Plate #A9C9E4 (plaques platine bleuté, métal 0.92, roughness 0.20), PlateDark #355C8E (plaques d'acier abyssal, métal 0.90),
  Glow #5FF4FF avec émission #2FEAFF strength 3.5 (points, lignes, rayons), Gem #4FF0FF avec émission strength 3.5 (gemmes cyan), GemSapphire #2A6CFF avec émission #3A86FF strength 3.0,
  Pearl #F2FBFF avec émission #9FEBFF strength 2.5 (perles flottantes), Halo #BDF8FF avec émission #4FF0FF strength 4.0 (halo, métal 0.6),
  EyeWhite #F6FAFB, Iris #18B8D8 avec émission #4FF0FF strength 4.0, Black #050B16 (pupilles), Nostril #061A3A, Bubble #DDF8FF (alpha 0.5).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Les nageoires sont des plaques en éventail à rayons, les plaques blindées sont des wedges, les gemmes sont des prismes à pointe.

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de la queue), jamais sur les plaques blindées, nageoires, rayons, griffes, écailles, gemmes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty LEVIATHAN_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT (WINGS_ROOT porte les nageoires pectorales et pelviennes).
  Chaque pièce est parentée au bon root (halo et gemmes du halo : HEAD_ROOT ; FX : MASTER_ROOT). Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « LEVIATHAN_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots LEVIATHAN_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (R, TORSO_L, LEG_H, NECK_L, NECK_RISE, HEAD_SCALE, SNOUT_K, FANGS, EAR_L, PEC_SPAN, PEC_RAYS, TAIL_L, CAUDAL_L, ARMOR, HORN_N, HALO_R, GEM_R, DOT_ROWS, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou, le torse et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les points de contrôle (BODY_CTRL, TAIL_CTRL) et les rayons (BODY_R_KEYS, TAIL_R_KEYS) sont des variables faciles à modifier.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission sur les points et lignes, les gemmes, les iris, le halo et les éclats flottants (strength 2.5 à 4). Les nageoires sont translucides (alpha 0.82). Les plaques blindées sont métalliques. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4404) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 24 éclats et bulles flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête, 10 corps, 11 pattes, 12 nageoires, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, halo, plaques, nageoires, queue en V, pattes-palettes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
