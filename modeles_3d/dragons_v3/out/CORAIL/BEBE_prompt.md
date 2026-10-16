Tu es un artiste technique 3D. Tu vas écrire un script Python pour Blender (bpy) qui génère
le modèle 3D du dragon « Bébé Corail » de mon jeu Roblox Dragon Pets Simulator.

PIÈCES JOINTES
1. Une image de concept des 3 stades si tu en as une ; sinon la description ci-dessous fait foi.
   Si tu as une image (Bébé, Ado, Adulte), seul le dragon en bas à gauche, nommé « Bébé Corail », est à modéliser.
2. Le GDD du jeu (Dragon_Pets_GDD_v2.3.docx). Lis en priorité :
   - partie 9, tableau du monde 3 : Corail = Eau, Commun, Tank, morphologie Drake ;
   - partie 13, Direction artistique : style par stade, morphologies, couleurs,
     « Fabrication des modèles ».
   Si l'image et le GDD se contredisent, l'image gagne pour l'apparence, le GDD gagne pour
   les contraintes techniques.

ÉTAPE 1 — AVANT D'ÉCRIRE DU CODE
Décris en 10 à 15 puces ce que tu vois (ou ce que la description impose) sur le Bébé Corail : pose, proportions,
chaque élément de la tête, du corps, des pattes et de la queue, et la palette. Puis liste les
contraintes du GDD qui s'appliquent. Je valide avant que tu codes.

CE QUE LE MODÈLE DOIT REPRODUIRE (vérifie chaque point)
- Pose : Drake trapu et arrondi : debout sur 4 pattes, cou de 1 bloc, tête regardant vers l'avant et un peu vers le bas (8°), queue épaisse qui descend vers le sol. Pas d'ailes. Gabarit Tank.
- Tête : crâne carré en wedge bleu azur, très gros (tête environ 35 % de la hauteur), museau court avec plaque bleu clair dessus, mâchoire crème distincte avec menton, ligne de bouche sombre, 2 narines noires, 1 tache(s) bleu clair par côté du crâne. YEUX très grands (blanc, grand iris bleu lumineux, pupille ronde, 2 petits reflets blancs), pas de sourcils, pas de crocs. Nageoires-oreilles : 2 rayons bleu clair (2 teintes en alternance) en éventail sur une base de chaque côté du crâne.
- Bois de corail : 2 bois de corail saumon sur des bases corail sombre, au dessus du crâne : chaque bois est une barre épaisse qui se ramifie sur 1 niveau (une branche latérale au 55 % de la barre + la suite du tronc au bout, branches terminées en pointe), taille courte.
- Signe distinctif : BOIS DE CORAIL saumon (tête), coraux ramifiés en rangée le long du dos (3 sur des bases sombres) et de la queue (1 tous les 3 segments), COQUILLE SAINT-JACQUES beige rosé (5 nervures en éventail, charnière en haut) en épaulette (1 par côté), NAGEOIRES-OREILLES bleu clair.
- Corps : torse en 3 blocs bleu azur (poitrail et bassin en wedge), plastron crème, 4 plaques de ventre crème bien séparées, écailles en quinconce sur les flancs (1 rangée de 4 : 3 losanges sombres/clairs + 1 taches hexagonales bleu clair par flanc), cou de 1 bloc avec plaque crème devant chaque bloc.
- Pattes : 4 pattes courtes et épaisses : cuisse en wedge bleu, jambe bleue, pied plat bleu clair, 3 doigts bleus + 3 griffes blanc-gris par patte.
- Queue : queue épaisse qui s'affine (Catmull-Rom), plaques crèmes dessous, coraux dessus, puis un bout en bloc corail sombre avec un bouquet de 2 coraux.
- Rendu de rareté (Commun) : silhouette propre et lisible, 5 familles de couleurs (bleu, bleu clair, crème, corail, beige rosé), un seul signe fort (le corail) bien dessiné, aucune émission sauf la lueur douce de l'iris. 4 bulles flottantes (petits prismes bleu clair) autour du dragon. Rendu discret : le bébé porte déjà tous les signes, en petit.
- Palette (hex, Principled BSDF) :
  Body #2670B8 (corps azur), BodyLight #4A9BDD (dessus du museau, pieds, base des oreilles), BodyDark #17426F (bouche, plaques sombres, bracelets),
  Mark #7CC2EA (taches bleu clair, nageoires-oreilles, aileron de queue), Belly #EDE6D6 (ventre, plastron, mâchoire),
  Coral #FF917D (bois, crête dorsale) / CoralDark #E8625A (bases, sourcils, branches basses), Shell #E8CDB8 / ShellDark #D3A58F (coquilles),
  Claw #E9ECEF (griffes, crocs), EyeWhite #F4F7FA, Iris #2AA0EE émission strength 1.0 (seule lueur du dragon), Black #0A1018 (pupilles, narines),
  Bubble #BFE6F7 (bulles flottantes).
- Style : low-poly en blocs biseautés, lisible de loin. Pas de sculpture organique. Les coraux sont des barres épaisses qui se ramifient (une branche latérale + la suite du tronc, pointe en éclat) ; les coquilles sont des éventails de nervures en toit.

CONTRAINTES TECHNIQUES
- Budget : 3000 triangles maximum après modificateurs. Biseau à 1 segment au plus, et
  seulement sur les gros blocs (crâne, museau, torse, cuisses, pieds), jamais sur
  les éclats, griffes, cristaux, coraux ou petites pièces. Le script affiche le total de triangles à la fin.
- Pièces séparées, sans squelette (le rig viendra plus tard, GDD partie 13).
- Hiérarchie : un empty CORAIL_BEBE_MASTER_ROOT avec 4 enfants HEAD_ROOT, BODY_ROOT, LEGS_ROOT et TAIL_ROOT
  (pas de WINGS_ROOT : le Drake n'a pas d'ailes). Chaque pièce est parentée au bon root. Les pièces de la
  tête sont placées en coordonnées locales de HEAD_ROOT (placé à la base du crâne, penché vers l'avant).
- Tout dans une collection « CORAIL_BEBE ». Le script est relançable : au début, il supprime uniquement
  les objets de cette collection et les enfants des roots CORAIL_BEBE_*. Il ne touche jamais aux autres
  stades ni aux autres dragons de la scène.
- Un bloc « RÉGLAGES DU STADE » en haut du code (BW, BH, LEG_H, TORSO_L, NECK_L, NECK_N, HEAD_SCALE, SNOUT_K, FANGS, ANTLER_K, ANTLER_DEPTH, CORAL_N, SHELL_N, EAR_N, TAIL_L, FX_N...) : c'est le seul
  bloc qui change entre Bébé, Ado et Adulte.
- Le cou et la queue suivent une courbe lissée (Catmull-Rom) rééchantillonnée à pas constant, avec un
  repère par segment (tangente, dos, côté) et un rayon qui varie le long de la courbe.
- Crée les meshes avec bmesh / from_pydata, pas avec bpy.ops dans les boucles.
- Matériaux Principled BSDF réutilisés s'ils existent, mais toujours mis à jour. Couleurs saturées
  en espace linéaire. Émission seulement sur l'iris, strength 1.0. Compatible Blender 4.x et 5.x.
- Seed aléatoire fixe (3301) pour que chaque exécution donne le même dragon.
- Option ADD_FLOATING_FX pour ajouter ou non les 4 bulles flottantes.
- Conventions : avant du dragon = -Y, haut = +Z, unité = mètre, hauteur totale 4 m, posé sur Z = 0.
- Code commenté en français, découpé en sections numérotées (7 palette, 8 hiérarchie, 9 tête,
  10 corps, 11 pattes, 13 queue, 14 rareté / FX, 15 finalisation ; pas de section 12, pas d'ailes).

LIVRAISON
1. Le script complet dans un seul fichier .py.
2. Si tu as accès à Blender : lance-le, fais une capture de la vue 3D, compare avec
   l'image (ou la description) et corrige les écarts visibles (couleurs, taille de la tête, signes
   distinctifs, pattes) avant de me le rendre. Donne le nombre de triangles.
3. Une liste courte des réglages à changer pour ajuster la forme.
