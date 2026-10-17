Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Adulte Néant » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 5 : Néant = Ténèbres, Secret, morphologie Amphiptère ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois sur l'Adulte Néant : pose, proportions, chaque
élément de la tête, du corps, des ailes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Adulte : grand serpent noir dressé en S (NECK_H 6.6) sur de larges anneaux au sol, tête imposante, 2 grandes ailes (envergure 8 m) dressées derrière le cou, double halo d'anneaux derrière la tête, silhouette déchirée et asymétrique. Étrange et inquiétant mais pas gore.
- Tête : crâne carré en wedge, long museau avec liseré violet, mâchoire indigo, ligne de bouche violette, 2 narines. Yeux : orbite noire, blanc lumineux, pupille fendue noire, sourcils sévères. 3 crocs blancs par côté, 3 écailles de joue par côté, oreilles-nageoires fantômes (gauche plus longue), joue droite fantôme.
- Cornes et couronne : 2 grandes cornes noires en arc de 4 blocs (la droite plus courte) à pointe violette lumineuse, couronne de 13 éclats déchirés derrière le crâne (noir, fantôme, violet, plus longs à gauche), 2 fissures lumineuses sur le crâne.
- Signe distinctif : corps noir profond comme un trou noir, liserés violets lumineux, anneaux concentriques violets, yeux blancs lumineux.
- Corps : segments noirs (2 tons alternés), 2 liserés violets lumineux sur chaque flanc et une ligne dorsale violette, écailles de flanc violet très sombre, plaques de ventre indigo, plastron indigo avec grande gemme violette, un anneau lumineux (alpha 0.65, 16 côtés) autour du corps à chaque segment, 4 anneaux concentriques emboîtés sur le dos du torse (signe distinctif), 4 anneaux concentriques posés au sol autour de l'enroulement, crête d'éclats déchirés (certains manquent, certains fantômes), épaulières de 4 éclats par côté et wedge noir à la base des ailes, fissures lumineuses en zigzag surtout à gauche.
- Ailes : 2 grandes ailes : os à liseré violet (strength 1.65), 4 doigts, membrane indigo translucide (alpha 0.62), éclat violet au poignet, 3 lambeaux fantômes par aile. L'aile droite a un doigt de moins et 12 % plus courte (arrachée en partie).
- Pattes : aucune (amphiptère). LEGS_ROOT ne porte que les anneaux concentriques posés au sol.
- Queue : la queue se redresse au centre de l'anneau ; après 80 % les segments deviennent fantômes (alpha 0.55), anneau lumineux au bout et 8 fragments fantômes qui se détachent.
- Halo : 2 anneaux verticaux lumineux concentriques derrière la tête (axe Y), parentés au MASTER.
- Rendu de rareté (Secret) : Secret complet : parties fantômes (alpha 0.5 à 0.65), fissures et liserés émissifs (strength 3.0), yeux blancs lumineux, silhouette déchirée, double halo derrière la tête. 40 éclats et 6 petits anneaux flottants.
- Palette (hex, Principled BSDF) :
  Body #0B0910 (corps, léger reflet : metallic 0.25), BodyDark #08070C (segments alternés, dessus du museau), ScaleB #211439 (écailles de flanc, sourcils, éclats),
  Belly #1E2A5E (ventre, mâchoire, plastron), Glow #9B5CFF (émissif : liserés, fissures, pointes de cornes, gemmes), Crest #6E3FC8 (émissif faible : liserés secondaires, os d'ailes),
  RingGlow #9B5CFF (émissif, alpha 0.65 : anneaux concentriques), Membrane #1E2A5E (alpha 0.62), Ghost #2A1850 (alpha 0.55, lueur faible #6E3FC8 : parties fantômes),
  GhostLight #9B5CFF (alpha 0.5, émissif : fragments qui se détachent), Claw #6E3FC8, Eye #F4F0FF (émissif : yeux blancs lumineux), White #F2F2F2 (crocs, reflets), Black #0A0A0A (pupilles), Nostril #050407 (orbites, narines).
  Mêmes couleurs aux 3 stades.
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Étrange et inquiétant mais adapté
  à un jeune public (aucun sang, rien de gore).

CONTRAINTES TECHNIQUES
- Budget : 17000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, premiers segments du cou), jamais sur les éclats, anneaux, griffes
  ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty NEANT_ADULTE_MASTER_ROOT avec 5 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT, TAIL_ROOT et WINGS_ROOT.
  Chaque pièce est parentée au bon root. Les pièces de la tête sont placées en coordonnées locales
  de HEAD_ROOT (placé à la base du crâne, légèrement penché vers l'avant).
- Tout dans une collection « NEANT_ADULTE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots NEANT_ADULTE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Le corps est un long serpent : une seule courbe lissée (Catmull-Rom) rééchantillonnée à pas constant (BODY_STEP), avec un repère par segment (tangente, dos, côté) et un rayon qui varie par clés. Les points de contrôle (cou dressé en S, descente, anneau au sol, queue qui remonte au centre), RADIUS_KEYS, ZB, NECK_H, COIL_R, HEAD_SCALE, WING_SPAN... sont des variables en haut du code.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission sur les liserés, anneaux, fissures, yeux et pointes ; parties fantômes, membranes et anneaux en alpha 0.5 à 0.65. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (7741) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 40 éclats et 6 petits anneaux flottants.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale ~11 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes (aucune), 12 ailes, 13 queue, 14 rareté / FX, 15 finalisation).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image et corrige les écarts visibles (couleurs, taille de la tête, ailes, anneaux)
   avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
