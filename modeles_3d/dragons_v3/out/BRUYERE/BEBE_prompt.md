Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Bruyère » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Bruyère (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Bruyère », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 1 : Bruyère = Terre, Rare, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Bruyère : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé trapu et mignon, debout sur 4 pattes courtes et épaisses (LEG_H 1,5), torse court, cou presque inexistant de 2 maillons, très grosse tête (HEAD_SCALE 1.8) regardant vers l'avant, queue courte.
- Tête : crâne carré en wedge, museau court avec arête claire, mâchoire brune distincte et ligne de bouche sombre, 2 narines noires et bout du museau. Yeux : blanc, iris ambre très grand avec pupille ronde et 2 reflets blancs, pas de sourcils. Pas de crocs. 2 éclats de joue en roche, 2 dalles de roche feuilletées et 3 grands éclats dorés sur le crâne.
- Signes distinctifs : armure de roche or-ocre feuilletée sur le dos, les épaules et la queue, et de la bruyère violet-rose (1 touffe(s) sur le crâne entre 2 petites cornes brunes recourbées), plus 3 touffes entre les plaques du corps.
- Corps : torse en 3 blocs, plastron crème, 4 plaques de ventre crème bien séparées, flancs : 2 rangées de 4 écailles, 2 bandes de roche feuilletée et 3 taches brun foncé, crête dorsale de 4 dalles, 2 épaulières avec 1 pointe(s) d'or, dalles de roche sur les épaules, cou de 2 maillons (segment brun + plaque crème + dalle de roche).
- Pattes : 4 pattes épaisses : cuisse en wedge, genouillère faite de 2 dalles de roche qui se chevauchent, jambe, bracelet doré lisse, pied plat, 3 doigts et 3 griffes crème par patte.
- Queue : 3 m, 3 segments larges, plaques crème dessous, dalles de roche dorée sur le dessus, 1 touffe(s) de bruyère, bout fait d'une grappe de 2 éclats dorés.
- Rendu de rareté : Rare, version discrète : yeux ambre lumineux et 1 cristal ambre sur le dos ; motif secondaire réduit (2 bandes, 3 taches), 3 petits éléments flottants (éclat de roche, braise ambre, pétale de bruyère).
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
- Budget : 4000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de queue), jamais sur les feuilles/éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty BRUYERE_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas d'ailes : Drake).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « BRUYERE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots BRUYERE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment et un rayon qui varie. Les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission discrète limitée aux accents Rare (yeux ambre, cristaux ambre, lianes dorées, petit cristal rose), strength 1.5 au maximum ; tout le reste est mat. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1106) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 3 éléments flottants (éclats de roche, braises ambre, pétales de bruyère).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes (aucune : Drake, section laissée en commentaire), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, armure de roche, bruyère))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
