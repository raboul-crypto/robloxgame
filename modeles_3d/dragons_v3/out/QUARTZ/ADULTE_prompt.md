Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Quartz » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Adulte Quartz » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Quartz = Minéral, Légendaire, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends de l'Adulte Quartz : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Adulte dragon classique musclé et majestueux, debout sur 4 pattes puissantes (LEG_H 2.3, BW 3.2), cou de 6 plaques d'argent, tête de HEAD_SCALE 1.4, grandes ailes ouvertes (envergure 9.0), queue de 6.5.
- Tête : crâne carré en wedge, long museau, arête en argent, mâchoire claire et ligne de bouche, narines, cristal de museau. Yeux : blanc, iris rose lumineux, pupille fendue, sourcils sévères d'argent. 3 crocs par côté, 4 cristaux de joue par côté, barbe de 5 petits cristaux sous le menton. Cornes en cristal ramifiées : grappe de 4 cristaux, 3 branches (blanche, rose, blanche), socle d'argent. Armure de tête : plaque frontale d'argent avec gemme rose lumineuse, plaques de joue.
- Signes distinctifs : aura derrière la tête : couronne de 2 anneaux de cristaux (12 et 9), grand anneau d'argent, anneau rose lumineux, 10 rayons de quartz ; double rangée de cristaux sur le dos (6 grappes de 4 cristaux + cristaux isolés de chaque côté) ; grappes de 6 cristaux sur chaque épaulière, grappe de 4 cristaux à chaque poignet et cristal au bout de chaque doigt ; cornes en cristal.
- Corps : torse en 3 blocs, plastron clair, 6 plaques de ventre séparées par des filets d'argent, 4 rangées de 7 écailles par flanc, grand coeur de quartz de poitrine (bouclier d'argent, grand cristal rose lumineux, double anneau d'argent, 14 cristaux autour, 2 gemmes roses), gorgerin d'argent, plaques d'argent sur le dos, épaulières d'argent avec gemme rose, plaques de hanche et de côtes, 3 cristaux de nuque par maillon et cristaux sur les côtés du cou.
- Ailes : grandes ailes gris perle à facettes : bras, avant-bras, 3 doigts osseux, membrane en triangles, 4 petits cristaux le long de l'avant-bras, 3 cristaux le long de chaque doigt, grand cristal au bout de chaque doigt, 3 cristaux sur le bord de chaque segment, 3 facettes roses translucides par panneau et par face, griffe de pouce blanche.
- Pattes : 4 pattes musclées : cuisse en wedge avec plaque d'argent, genouillère d'argent, jambière d'argent sombre, 2 bracelets d'argent, 2 cristaux sur la jambière, pied de pierre biseauté, 3 doigts et 3 griffes blanches, ergot aux pattes arrière.
- Queue : segments de pierre le long d'une courbe lissée, ventre en plaques claires sur les 4/5, bandes d'argent, cristal rose ou blanc sur chaque segment, cristaux latéraux, écailles, anneau d'argent et grande géode de 8 cristaux autour d'un cristal rose lumineux au bout.
- Rendu de rareté (Légendaire) : Légendaire complet : coeur de quartz, iris, gemmes, anneau rose et cristal de la géode émissifs (2.6), armure d'argent métallique (front, gorgerin, épaulières, dos, hanches, genouillères, bracelets), aura en couronne de 2 anneaux derrière la tête, double rangée de cristaux sur le dos, géode finale, 64 cristaux et gemmes flottants, anneau runique au sol (16 plots).
- Palette (hex, Principled BSDF mats) :
  Body #837F8A (corps gris pierre), BodyScale #615E68 (écailles sombres, dessus des pattes, orteils), ScaleB #9C8A93 (écailles gris rosé), BodyDark #4B494F (bouche, genoux),
  Belly #D9D4DC (ventre en plaques, plastron, menton), Silver #DAD6E2 (armure, metallic 0.85) / SilverDark #A9A5B7 (rebords, metallic 0.8),
  QuartzPink #F2B8C8 et QuartzWhite #F4F2F5 (cristaux de quartz translucides, alpha 0.82, lueur faible 0.5 à 0.6), QuartzCore #E8789C (cristaux de coeur, gemmes, anneau rose, émission 2.6),
  Membrane #D2CDDC (membrane gris perle), WingBone #A8A2B6 (os d'aile), Claw #F4F2F5 (griffes blanches), Fang #F4F2F5 (crocs),
  EyeWhite #F2F2F2, Iris #E8789C (émission 2.6), Black #0A0A0A (pupilles)
- Style : low-poly en blocs biseautés, lisible de loin. Les cristaux sont des prismes hexagonaux (ou pentagonaux) à pointe, groupés en grappes (un grand cristal central et 2 à 4 cristaux inclinés autour, rose et blanc en alternance). Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 15000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty QUARTZ_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « QUARTZ_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots QUARTZ_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, WING_SPAN, HALO_R / CROWN_N, CREST_N / CREST_CLUSTER, TAIL_L / TAIL_CRYS, FX_N...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Légendaire : seuls les iris, le coeur de quartz, les gemmes, le cristal de la géode et l'anneau rose du sol sont émissifs (2.6) ; les cristaux de quartz sont translucides (alpha 0.82) avec une lueur faible (0.5 à 0.6) ; l'argent est métallique (0.8 à 0.85). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (6029) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 64 cristaux et gemmes flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, lames)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
