Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Typhon » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades du dragon Typhon (Bébé, Ado, Adulte) si tu en as une ; sinon
   la description ci-dessous fait foi. Seul le stade « Adulte Typhon » est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 4 : Typhon = Eau, Légendaire, Brute, morphologie Hydre ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que décrit le texte) sur l'Adulte Typhon : pose, proportions, chaque
élément des trois têtes, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Adulte massif et imposant, debout sur 4 pattes puissantes, trois têtes sur des cous de 5 maillons en S (la centrale plus haute, les latérales écartées de 26° vers l'extérieur), regard vers l'avant et un peu vers le bas, grande queue de poisson qui traîne.
- Tête : crâne carré, long museau avec arête turquoise, mâchoire distincte entrouverte (9°), ligne de bouche, narines sombres. Yeux : blanc, iris turquoise lumineux, pupille fendue, sourcils sévères turquoise inclinés de 20°. 3 crocs blancs par côté en haut et 2 en bas. Grandes cornes courbes turquoise à pointe blanche et bague d'argent. 3 nageoires de joue par côté. Couronne d'argent à 3 pointes et gemme sur chaque tête.
- Crêtes : SIGNE DISTINCTIF : une grande crête de 7 vagues par tête (plaques en arc de hauteur 2,3, alternance turquoise et vert d'eau, qui déferlent vers l'avant avec de l'écume blanche au sommet), plus une seconde rangée de petites vagues blanches de chaque côté.
- Corps : torse en 3 blocs, plastron turquoise en 3 plaques à bord d'argent avec grande gemme, 6 plaques de ventre, épaules en wedge avec épaulières d'argent à pointe, 24 écailles par flanc (4 rangées de 6), 7 plaques de dos avec 7 vagues et DOUBLE RANGÉE DE PICS (argent et blanc) de chaque côté, 5 cristaux d'eau émissifs, 3 spirales de tourbillon par flanc (1,8 tour) avec un oeil d'écume, cous de 5 maillons : blocs avec gorge claire, anneaux bleu clair, petites vagues de nuque et spirales de tourbillon sur les deux côtés.
- Ailes / nageoires : aucune aile et aucun WINGS_ROOT : pattes palmées avec nageoires de mollet, grande nageoire caudale.
- Pattes : 4 pattes : épaule et cuisse en wedge, tibia, bracelet bleu à 2 bords d'argent et gemme, nageoires de mollet et de genou, pied plat, 3 doigts + 2 palmes + 3 griffes blanches.
- Queue : longue (environ 12 segments), plaques turquoise dessous, vagues dorsales, anneaux de tourbillon bleu clair, grande nageoire caudale en V à rayons (2 lobes turquoise à bord d'écume), anneau d'argent avec gemme et grand trident d'argent (3 pointes) au bout.
- Rendu de rareté : Légendaire complet : tout l'Épique (iris et cristaux d'eau émissifs, ornements) + couronnes d'argent à gemme, aura derrière chaque tête (anneau lumineux + 11 éclats émissifs), plastron, épaulières et bracelets d'argent, double rangée de pics, ornement final de queue (anneau, gemme, trident). 16 FX flottants : gouttes, bulles, mini-vagues et tourbillons.
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
- Budget : 15000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crânes, museaux, torse, cuisses, pieds), jamais sur les vagues, griffes, pics
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty TYPHON_ADULTE_MASTER_ROOT avec pour enfants HEAD_ROOT (tête centrale), HEAD2_ROOT et HEAD3_ROOT
  (têtes latérales), BODY_ROOT, LEGS_ROOT et TAIL_ROOT. Pas de WINGS_ROOT. Chaque pièce est parentée au bon root.
  Les pièces de chaque tête sont placées en coordonnées locales de son root (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « TYPHON_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots TYPHON_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Les trois cous et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe. Les proportions
  (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEADS, HEAD_SCALE, TAIL_L, TAIL_FIN...) sont des variables faciles à modifier en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur Eye, Gem et Aura. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (4404) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les éléments flottants (16 éléments flottants).
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 têtes,
  10 corps, 11 pattes, 12 ailes (aucune), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille des têtes, vagues, pattes)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
