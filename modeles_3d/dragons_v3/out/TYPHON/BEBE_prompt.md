Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Typhon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades du dragon Typhon (Bébé, Ado, Adulte) si tu en as une ; sinon
   la description ci-dessous fait foi. Seul le stade « Bébé Typhon » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Typhon = Eau, Légendaire, Brute, morphologie Hydre ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que décrit le texte) sur le Bébé Typhon : pose, proportions, chaque
élément des trois têtes, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Bébé compact et trapu, debout sur 4 pattes courtes et épaisses, trois énormes têtes carrées (la centrale plus grande, 30 à 35 % de la hauteur) posées presque directement sur le torse par un cou d'un seul maillon, regardant vers l'avant, petite queue de poisson qui traîne.
- Tête : crâne carré biseauté, museau court avec arête turquoise, mâchoire fermée et ligne de bouche, 2 narines sombres, PAS de crocs. Très grands yeux : grand blanc carré, grand iris turquoise lumineux, grande pupille ronde noire, 2 reflets blancs. Sourcils plats turquoise. Petites cornes en blocs turquoise à pointe blanche. Les têtes latérales (échelle 0,8, tournées de 22° vers l'extérieur) sont plus simples.
- Crêtes : SIGNE DISTINCTIF : une crête en forme de vague sur chaque tête, 3 vagues (plaques en arc qui montent puis déferlent vers l'avant, hauteur 1,1) avec de l'écume blanche (petit cristal et perle) au sommet.
- Corps : torse en 3 blocs, plastron turquoise clair avec 2 clous d'argent et une gemme turquoise, 2 plaques de ventre, 6 écailles par flanc (2 rangées de 3), 3 plaques de dos bleues avec 3 vagues, 1 spirale de tourbillon bleu clair de 1,4 tour par flanc, cou d'un maillon avec anneau bleu clair.
- Ailes / nageoires : aucune aile et aucun WINGS_ROOT : ce sont des pattes palmées et une queue de poisson.
- Pattes : 4 pattes courtes : bloc d'épaule et cuisse biseauté, tibia, bracelet bleu à bord d'argent, pied plat, 3 doigts avec 2 palmes turquoise entre eux, 3 griffes blanches courtes, nageoire de genou turquoise.
- Queue : courte (4 segments environ), plaques turquoise dessous, petites vagues sur le dos, nageoire caudale en V (2 lobes turquoise à bord d'écume, 1 rayon par lobe) et un anneau d'argent avec gemme au bout.
- Rendu de rareté : Légendaire, présent mais discret : couronne d'argent avec 3 pointes et une gemme sur la tête centrale, clous d'argent et gemme sur le plastron, anneau d'argent de queue, 1 cristal d'eau émissif sur le dos, bulles, gouttes et mini-vagues flottantes (4). Pas d'aura, pas de double rangée de pics.
- Palette (hex, Principled BSDF ; seuls Eye, Gem et Aura sont émissifs) :
  Body #1A57A8 (corps), BodyDark #0F2F5E (genoux, mâchoire, ombres), ScaleA #14407F (écailles sombres, dos), ScaleB #1F6E96 (écailles chaudes, museau),
  Nostril #0A1C36 (narines, bouche, jointures), Belly #9EDDD6 (ventre en plaques, plastron, gorge, menton),
  Crest #35BFAE (crêtes en vagues, sourcils, cornes), Foam #F4F8FA (écume, pointes, pics), Membrane #3FB5A8 (nageoires, palmes),
  Mark #7FC8EA (spirales de tourbillon, anneaux), Eye #2FD0C8 (iris, émissif), Gem #2FE6E0 (gemmes, émissif),
  Aura #7FE8F2 (aura, gouttes, bulles, cristaux d'eau, émissif), Silver #C6D8EA (métal, metallic 0.95),
  Claw #F4F8FA (griffes), Fang #F2F2F2 (crocs), EyeWhite #F2F2F2, Black #0A0A0A (pupilles).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les vagues sont des
  croissants plats faits de 2 ou 3 plaques en arc, les écailles et nageoires des losanges plats.

CONTRAINTES TECHNIQUES
- Budget : 6000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crânes, museaux, torse, cuisses, pieds), jamais sur les vagues, griffes, pics
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty TYPHON_BEBE_MASTER_ROOT avec pour enfants HEAD_ROOT (tête centrale), HEAD2_ROOT et HEAD3_ROOT
  (têtes latérales), BODY_ROOT, LEGS_ROOT et TAIL_ROOT. Pas de WINGS_ROOT. Chaque pièce est parentée au bon root.
  Les pièces de chaque tête sont placées en coordonnées locales de son root (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « TYPHON_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots TYPHON_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Les trois cous et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEADS, HEAD_SCALE, TAIL_L, TAIL_FIN...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur Eye, Gem et Aura. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4404) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les éléments flottants (4 éléments flottants (gouttes, bulles, mini-vagues)).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 têtes,
  10 corps, 11 pattes, 12 ailes (aucune), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille des têtes, vagues, pattes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
