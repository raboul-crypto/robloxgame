Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Dune » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept montrant les 3 stades du dragon Dune (Bébé, Ado, Adulte).
   Seul le dragon en bas à gauche, nommé « Bébé Dune », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 2 : Dune = Terre, Commun, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur le Bébé Dune : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point sur l'image)
- Pose : Bébé trapu et mignon, debout sur 4 pattes courtes et épaisses (LEG_H 1,55), torse de 3,3, cou presque inexistant (1 maillon), très grosse tête (HEAD_SCALE 1.2 sur un corps très compact) regardant vers l'avant, queue courte.
- Tête : crâne carré en wedge brun orangé (Head), museau court avec dessus clair et nez brun, mâchoire et ligne de bouche sombre, menton fait de 2 plaques dentelées empilées, 2 narines noires. Yeux : blanc, iris ambre très grand avec pupille ronde et 2 reflets blancs, pas de sourcils. Pas de crocs. 1 pointe(s) de joue brune(s) avec petite plaque dorée, 3 plaques dorées sur le dessus du crâne (de plus en plus grandes vers l'arrière).
- Signes distinctifs : rayures de dune brunes ondulées sur les flancs (2 rayures de 8 segments), grande collerette de plaques facettées derrière le crâne (1 anneau de 8 plaques), 2 petites cornes beiges recourbées.
- Corps : torse en 3 blocs, plastron crème, 4 plaques de ventre crème bien séparées, dalles de roche facettées (1 rangée de 3) sur le haut des flancs, 1 dalle(s) sombre(s) sur le dos, 1 grosse(s) dalle(s) dorée(s) empilée(s) en épaulière, crête dorsale de 3 plaques pointues, cou de 1 maillon(s) (bloc doré + plaque crème + dalle de roche).
- Pattes : 4 pattes très épaisses : épaule et cuisse en wedge, jambe, genouillère en dalle, bracelet de sable, pied plat, 3 doigts et 3 griffes crème de 0,45 par patte.
- Queue : 2,4 m, 2 pointes de roche et un petit bloc doré au bout ; plaques crème dessous, crête de roche dessus, anneau brun puis bloc doré et grappe de pointes au bout (massue de pierre).
- Rendu de rareté : Commun : rendu volontairement simple, 3 éclats de sable en losange et 1 petit nuage de poussière flottants. 3 familles de couleurs (or sable, brun, crème), un seul signe fort (rayures de dune + collerette de roche).
- Palette (hex, Principled BSDF) :
  Body #E0A63A (corps, or sable), BodyScale #C98A2C (écailles, dessus des pattes, dessous des plaques), Head #C97A2E (crâne et museau, brun orangé),
  Dune #97551F (rayures de dune, nez, joues), BodyDark #5C3519 (dalles sombres du dos, bouche, sourcils),
  PlateLight #F3CB5C / PlateMid #DDA23B (plaques de roche), Belly #F4DDA0 (ventre en plaques, plastron), Horn #EBD0A0 (cornes beiges),
  Claw #F8EDCF (griffes, crocs), EyeWhite #F6F0DC, Iris #E08A14 (très faible lueur ambre, strength 1.0), Black #120A05 (pupilles, narines),
  Dust #DDB86E (poussière et éclats de sable flottants).
- Style : low-poly en blocs biseautés, lisible de loin, comme sur l'image. Pas de sculpture
  organique. Le corps est fait de dalles de roche facettées qui se chevauchent ; la poussière est faite de petits cubes.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds, premiers segments de queue), jamais sur les feuilles/éclats, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty DUNE_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT (pas d'ailes : Drake).
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « DUNE_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots DUNE_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment et un rayon qui varie. Les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, TAIL_L...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Aucune émission (rareté Commun), sauf une très faible lueur ambre sur l'iris. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (1111) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 3 éclats de sable en losange et 1 petit nuage de poussière flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 12 ailes (aucune : Drake, section laissée en commentaire), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, cornes, collerette, rayures))
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
