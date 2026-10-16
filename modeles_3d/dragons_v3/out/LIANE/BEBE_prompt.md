Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Liane » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Seul le dragon « Bébé Liane » (en bas à gauche sur l'image s'il y en a une) est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Liane = Plante, Épique, Brute, morphologie Hydre ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Liane : pose, proportions, chaque
élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : bébé hydre trapu à TROIS têtes sur des cous très courts (1 maillon), debout sur 4 pattes courtes et épaisses, torse large, pas d'ailes, queue courte qui traîne.
- Têtes : la centrale plus grande (échelle 1.25) et deux latérales (échelle 0.8, décalées de ±2.45, tournées de ±22 degrés vers l'extérieur) ; chacune a un gros crâne carré, un museau court (0.85), une mâchoire fermée, pas de crocs, de très grands yeux (blanc, grand iris ambre lumineux, pupille ronde, 2 petits reflets blancs), sourcils d'écorce plats, 2 petits blocs de corne d'écorce, une touffe de 4 feuilles (3 verts) avec un rang intérieur clair, une fleur sur le front (rose pour la centrale, orange pour les latérales).
- Corps : torse et bassin en blocs biseautés vert sapin, 2 plaques de ventre vert clair, plastron vert clair avec 2 clous dorés, carapace d'écorce brune de 4 rangées avec feuilles de crête, 2 lianes vertes en spirale de sens opposés (1.5 tour) avec petites feuilles et 3 fleurs, 1 fleur sur le dos, 3 colonnes d'écailles-feuilles par flanc, cous en blocs verts avec gorge claire, dos d'écorce et bague de liane.
- Pattes : 4 pattes courtes (LEG_H 1.2), épaule et cuisse en wedge, tibia, bracelet d'écorce à bord doré, feuille de genou, pied plat, 3 doigts + 3 griffes ivoire.
- Ailes : aucune (hydre de forêt), pas de WINGS_ROOT.
- Queue : courte (2.4), segments verts, ventre clair, plaques d'écorce, feuilles, bout en grappe de 3 feuilles autour d'un bourgeon de sève lumineux et une fleur rose.
- Signes distinctifs (identiques aux 3 stades) : trois têtes à touffes de feuilles ; lianes entrecroisées sur le corps ; petites fleurs orange et roses ; carapace d'écorce et de feuilles sur le dos.
- Rendu de rareté (Épique) : touche discrète (GLOW_STR 1.8) : yeux ambre, fleurs orange et roses lumineuses à cœur jaune, 1 grappe de sève lumineuse sur le dos, bourgeon de queue lumineux, clous dorés, 3 spores, pétales et feuilles flottants.
- Palette (hex, Principled BSDF) : Body #3A7A2A (corps), BodyDark #2A5A20 (mâchoire, écailles sombres), BodyWarm #4C9232 (écailles chaudes),
  Shadow #183514 (jointures, narines, bouche), Belly #A8D660 (ventre, plastron, gorges), Bark #7E5234 (écorce, cornes), BarkDark #573520 (sourcils, strates),
  Leaf #4FA832, LeafLight #8AD04A, LeafDeep #2F7A28 (feuilles), Vine #5BA83A (lianes), Claw #EDE3C8 (griffes ivoire), Fang #F4EBD0 (crocs),
  Gold #F2B233 (métal 0.9, ornements), EyeWhite #F2F2F2, Black #0A0A0A (pupilles).
  Émissifs : Iris #F28C2E (yeux), FlowerOrange #F28C2E et FlowerPink #F27FA0 (pétales), FlowerHeart #FFD84A (cœur des fleurs), Sap #C8F55A (sève, spores, gemmes), tous à la puissance GLOW_STR du stade.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les feuilles sont des plaques en losange.

CONTRAINTES TECHNIQUES
- Budget : 5,000 triangles maximum après modificateurs (le script en fait environ 4,928, vise 80-100 %). Biseau à 1 segment au plus,
  et seulement sur les gros blocs (têtes, torse, bassin, cuisses, pieds), jamais sur les feuilles, pics, griffes ou petites pièces.
  Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty LIANE_BEBE_MASTER_ROOT avec 6 enfants HEAD_ROOT (tête centrale), HEAD2_ROOT, HEAD3_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT). Chaque pièce est parentée au bon root. Les pièces de chaque tête sont placées en coordonnées locales de son root de tête
  (placé en haut du cou, légèrement penché vers l'avant).
- Tout dans une collection « LIANE_BEBE ». Le script est relançable : au début, il supprime uniquement les objets de cette
  collection et les enfants des roots LIANE_BEBE_*. Il ne touche jamais aux autres stades ni aux autres dragons de la scène.
- Les 3 cous et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un repère par segment et un rayon qui varie
  le long de la courbe. Les proportions (BW, BH, LEG_H, TORSO_L, NECK_L, HEAD_SCALE, TAIL_L...) et la liste HEADS sont des
  variables faciles à modifier dans le bloc « RÉGLAGES DU STADE » en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées en espace linéaire.
  Yeux, fleurs, sève et spores émissifs. Compatible Blender 4.x et 5.x (« Emission Color » ou « Emission »).
- Seed aléatoire fixe (3303) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les spores, pétales et feuilles flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 proportions et hiérarchie, 9 têtes,
  10 corps, 11 pattes, 12 ailes (aucune), 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille des têtes, lueur des fleurs)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
