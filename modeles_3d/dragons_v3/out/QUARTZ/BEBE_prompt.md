Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Quartz » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le stade « Bébé Quartz » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Quartz = Minéral, Légendaire, Équilibré, morphologie Classique ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu comprends du Bébé Quartz : pose, proportions, chaque
élément de la tête, du corps, des ailes, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE
- Pose : Bébé dragon classique compact, debout sur 4 pattes courtes et épaisses (LEG_H 0.8), cou d'un seul maillon, très grosse tête (HEAD_SCALE 1.05, environ 35 % de la hauteur), petites ailes (envergure 4.0), queue de 2.8.
- Tête : crâne en wedge et museau très court, arête du museau, mâchoire claire et ligne de bouche, narines, petit cristal rose au bout du museau. Très grands yeux : blanc, grand iris rose lumineux, pupille ronde, 2 reflets blancs, sourcils gris pierre fins. Pas de crocs. 2 petits cristaux de quartz (1 rose, 1 blanc) en guise de cornes par côté, oreilles en éclat gris perle, 1 cristal de joue par côté.
- Signes distinctifs : cristaux de quartz rose et blanc translucides : 4 petites grappes de 2 cristaux sur le dos, cristal de nuque sur le cou, 3 cristaux de géode au bout de la queue, cornes en cristal, ailes gris perle avec 1 cristal au bout de chaque doigt et 1 facette rose sur la membrane.
- Corps : torse en 3 blocs, plastron clair et 4 plaques de ventre biseautées, 2 rangées de 4 écailles par flanc, petit coeur de quartz sur la poitrine (bouclier d'argent, cristal rose lumineux, anneau d'argent, 8 petits cristaux autour), 3 cristaux par épaulière.
- Ailes : petites ailes gris perle : bras, avant-bras, 3 doigts osseux, membrane en triangles, grappe de 2 cristaux au poignet, 1 cristal sur le bord, griffe de pouce blanche. Pas d'armure.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge, jambe en bloc, pied plat biseauté, 3 doigts de pierre et 3 griffes blanches. Pas d'armure sur le bébé.
- Queue : segments de pierre le long d'une courbe lissée, ventre en plaques claires sur les 4/5, un cristal rose ou blanc sur chaque segment, anneau d'argent et petite géode de 3 cristaux roses et blancs autour d'un cristal rose lumineux au bout.
- Rendu de rareté (Légendaire) : Légendaire en touche : coeur de quartz et iris émissifs (2.6), petite aura de 6 cristaux et anneau d'argent + rose lumineux derrière la tête, anneau runique au sol (argent + rose lumineux, 8 plots), 12 cristaux et gemmes flottants. Pas d'armure sur le bébé.
- Palette (hex, Principled BSDF mats) :
  Body #837F8A (corps gris pierre), BodyScale #615E68 (écailles sombres, dessus des pattes, orteils), ScaleB #9C8A93 (écailles gris rosé), BodyDark #4B494F (bouche, genoux),
  Belly #D9D4DC (ventre en plaques, plastron, menton), Silver #DAD6E2 (armure, metallic 0.85) / SilverDark #A9A5B7 (rebords, metallic 0.8),
  QuartzPink #F2B8C8 et QuartzWhite #F4F2F5 (cristaux de quartz translucides, alpha 0.82, lueur faible 0.5 à 0.6), QuartzCore #E8789C (cristaux de coeur, gemmes, anneau rose, émission 2.6),
  Membrane #D2CDDC (membrane gris perle), WingBone #A8A2B6 (os d'aile), Claw #F4F2F5 (griffes blanches), Fang #F4F2F5 (crocs),
  EyeWhite #F2F2F2, Iris #E8789C (émission 2.6), Black #0A0A0A (pupilles)
- Style : low-poly en blocs biseautés, lisible de loin. Les cristaux sont des prismes hexagonaux (ou pentagonaux) à pointe, groupés en grappes (un grand cristal central et 2 à 4 cristaux inclinés autour, rose et blanc en alternance). Pas de sculpture organique.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur les éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty QUARTZ_BEBE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « QUARTZ_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots QUARTZ_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, WING_SPAN, TAIL_L, HALO_R, TAIL_CRYS...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Rareté Légendaire : seuls les iris, le coeur de quartz, les gemmes et l'anneau rose du sol sont émissifs (2.6) ; les cristaux de quartz sont translucides (alpha 0.82) avec une lueur faible (0.5 à 0.6). Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (6029) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 12 cristaux et gemmes flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, lames)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
