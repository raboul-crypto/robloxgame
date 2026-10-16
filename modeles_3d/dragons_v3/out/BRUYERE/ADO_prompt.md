Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Ado Bruyère » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Bruyère (Bébé, Ado, Adulte).
   Seul le dragon au milieu, nommé « Ado Bruyère », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Bruyère = Terre, Rare, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Ado Bruyère : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Ado plus long et musclé, 4 pattes épaisses (LEG_H 2,3), torse de 4,2, cou de 3 maillons un peu penché vers l'avant, tête à HEAD_SCALE 1.5, queue de 5 m.
- Tête : crâne carré en wedge, museau allongé avec arête claire, mâchoire brune distincte et ligne de bouche sombre, 2 narines noires et bout du museau. Yeux : blanc, iris ambre avec pupille fendue, sourcils d'écorce sombres inclinés. 2 petits crocs crème par côté. 3 éclats de joue en roche, 2 dalles de roche feuilletées et 4 grands éclats dorés sur le crâne.
- Signes distinctifs : armure de roche or-ocre feuilletée sur le dos, les épaules et la queue, et de la bruyère violet-rose (3 touffe(s) sur le crâne entre 2 cornes brunes avec 1 branche chacune), plus 7 touffes entre les plaques du corps.
- Corps : torse en 3 blocs, plastron crème, 5 plaques de ventre crème bien séparées et bandes crème sur le bas des flancs, flancs : 3 rangées de 4 écailles, 3 bandes de roche feuilletée et 7 taches brun foncé, crête dorsale de 5 dalles, 3 épaulières avec 2 pointe(s) d'or, cape de roche en dalles qui retombent sur les épaules, cou de 3 maillons (segment brun + plaque crème + dalle de roche).
- Pattes : 4 pattes épaisses : cuisse en wedge, genouillère faite de 2 dalles de roche qui se chevauchent, jambe, bracelet doré avec liane dorée lumineuse en spirale et grappe de cristaux ambre, pied plat, 3 doigts et 3 griffes crème par patte, touffe de bruyère à l'arrière de la cuisse.
- Queue : 5 m, plaques crème dessous, dalles de roche dorée sur le dessus, écailles sur les côtés, 2 touffe(s) de bruyère, bout fait d'une grappe de 3 éclats dorés, d'un cristal ambre et d'une touffe de bruyère.
- Rendu de rareté : Rare à mi-puissance : yeux ambre, 2 cristaux ambre et 1 petit cristal rose sur le dos, lianes dorées lumineuses sur les pattes, motif secondaire (3 bandes, 7 taches), 7 éléments flottants.
- Palette (hex, Principled BSDF) :
  Body #A96D34 (corps brun ocre), BodyScale #8C5628 (dessus des pattes, mâchoire, écailles), BodyDark #4E301A (sourcils, bouche, taches),
  Rock1 #D9993A / Rock2 #BF7E2C (plaques de roche or-ocre), RockGold #F2BE4A (grands éclats de roche dorée), Belly #F2D8A0 (ventre en plaques, plastron, menton),
  Horn #5E3F24 (cornes / bois brun foncé), HornTip #A57B46 (pointes et branches claires), Claw #F4E6C4 (griffes, crocs),
  HeatherA #B042A6 / HeatherB #DD77CF / HeatherC #7C2C86 (bruyère violet-rose), Stem #4F8E32 (tiges et petites feuilles),
  EyeWhite #F6F0DC, Iris #FFAE1F (émission ambre #FFA811, strength 1.3), Black #120B06 (pupilles, narines),
  AmberCrystal #FFC247 (cristaux, émission #FFB01F, strength 1.5), GoldVine #F7C040 (lianes dorées, émission #FFAA1A, strength 1.1), PinkGlow #F06BD8 (petit cristal rose, émission strength 1.2).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. La roche est faite de dalles feuilletées qui se chevauchent et d'éclats pointus ; la bruyère est faite de petites pyramides violettes sur tige.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de queue), jamais sur les feuilles/éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRUYERE_ADO_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas d'ailes : Drake).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRUYERE_ADO ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRUYERE_ADO_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment et un rayon qui varie. Les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission discrète limitée aux accents Rare (yeux ambre, cristaux ambre, lianes dorées, petit cristal rose), strength 1.5 au maximum ; tout le reste est mat. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1106) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 7 éléments flottants (éclats de roche, braises ambre, pétales de bruyère).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~7 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes (aucune : Drake, section laissée en commentaire), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, armure de roche, bruyère))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
