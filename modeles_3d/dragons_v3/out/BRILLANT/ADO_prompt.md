Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Brillant » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Brillant = Minéral, Mythique, Tank, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur l'Ado Brillant : pose, proportions,
chaque élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Ado élancé, debout sur 4 pattes, cou de 5 plaques, tête plus petite, ailes à moitié ouvertes, queue à géode.
- Tête : crâne carré en wedge de diamant bleuté, museau carré avec arête de platine, mâchoire claire distincte et ligne de bouche, 2 narines noires, petit cristal bleuté sur le bout du museau, oreilles-ailerons de cristal. Yeux latéraux plus sérieux : blanc, iris bleu glacé lumineux, pupille fendue noire, sourcils de platine ; 2 petits crocs par côté. Grande corne de diamant + 2 branches par côté sur une base de platine. Cristaux de joue et petits cristaux sous le menton.
- Signe distinctif : corps de DIAMANT blanc-bleuté fait de facettes translucides : losanges plats translucides posés sur les flancs (3 rangées de 6 facettes par côté), grappes de cristaux de diamant (6 faces, pointe) sur le dos, la nuque, les épaules, les pattes et la queue, ailes en cristal facetté. Reflets arc-en-ciel DISCRETS : seulement quelques éclats rose, or, menthe, cyan ou violet (environ 1 cristal sur 7) sur les cristaux, une facette de flanc sur 7, le halo, la géode et les éclats flottants.
- Halo : un HALO flotte derrière la tête : anneau de platine épais (rayon 1,7 x la tête), anneau bleu glacé lumineux à l'intérieur, 8 rayons de cristaux blancs avec quelques éclats arc-en-ciel, et 1 anneau de 10 cristaux derrière et au-dessus du crâne.
- Corps : torse en 3 blocs (poitrail et bassin en wedge), plastron blanc, 5 plaques de ventre blanches bien séparées avec filets de platine, CŒUR DE DIAMANT sur la poitrine : bouclier de platine, grand cristal bleu glacé lumineux, anneau de platine, 10 cristaux en couronne. Armure de platine : plaque de front avec gemme, joues, gorgerin, épaulières, plaques de dos et de hanche, genouillères, jambières. Cou de 5 maillons (bloc de diamant + plaque claire devant + rebord de platine, cristaux de nuque). Dos : rangée de 5 grappes de 3 cristaux + cristaux latéraux.
- Ailes : ailes à demi ouvertes : os bleu clair, membrane de cristal translucide, 2 facettes par membrane, 2 cristaux sur le bord, grappe au poignet. Ailes moyennes.
- Pattes : 4 pattes épaisses : cuisse en wedge de diamant, tibia en platine sombre, bracelets de platine, pied plat, 3 doigts + 3 griffes blanches par patte, éperon, cristaux sur les jambières.
- Queue : moyenne (environ 6 segments), plaques claires dessous, bandes de platine tous les 3 segments, cristal de crête par segment, géode de 5 cristaux.
- Rendu de rareté (Mythique) : diamant et platine métalliques (metallic 0,65-0,95, rugosité basse) sur tout le corps, cristaux et membranes translucides (alpha 0,7-0,85), cœur, yeux, gemmes et halo ÉMISSIFS (strength 2,5-3), halo flottant, FX denses : 44 éclats, cristaux et gemmes qui dérivent autour du dragon, anneau runique de platine + anneau lumineux au sol (rayon 2,4 x la largeur du corps).
- Palette (hex, Principled BSDF ; metallic entre parenthèses) :
  Body #D2ECFB (0,65, corps), BodyScale #B0D8F2 (0,7, facettes sombres, pieds), ScaleB #EEF8FF (0,65, facettes claires),
  BodyDark #86B0D0 (bouche, ombres), Belly #F4FBFF (0,4, ventre, plastron, mâchoire), Platinum #EEF8FF (0,95, armure) / PlatinumDark #CFE6F6 (0,85, rebords),
  DiamondBlue #CDEBFF et DiamondWhite #FFFFFF (cristaux translucides alpha 0,78, lueur faible), DiamondCore #7FD0FF (émission #7FD0FF, cœur, géode),
  éclats arc-en-ciel (alpha 0,85, émission 1) : #FFA6D2 rose, #FFE49A or, #9CFFD2 menthe, #86EAFF cyan, #BBA2FF violet,
  Membrane #EAF7FF (alpha 0,7), WingBone #C4E6F8 (0,75), Claw et Fang #F7FBFD, EyeWhite #F2F2F2, Iris #7FD0FF (émission), Black #0A0A0A.
  Doit rester nettement différent de Quartz (rose) : ici tout est blanc, bleu glacé et transparent.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique ; les cristaux sont des prismes à pointe, les facettes des losanges plats.

CONTRAINTES TECHNIQUES
- Budget : 11000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les cristaux, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRILLANT_ADO_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant). Les FX flottants sont parentés au MASTER.
- Tout dans une collection « BRILLANT_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRILLANT_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L...) sont des variables faciles à modifier dans le bloc « RÉGLAGES DU STADE ».
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Alpha < 1 avec mode de fusion BLENDED pour les cristaux et les membranes. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (5102) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les éclats flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, ailes, halo)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
