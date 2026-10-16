import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - {NOM} · {STADE}
#  {RARETE} · {ELEMENT} · {MORPHO} · monde {MONDE}
#  - (4 à 6 lignes : ce que le script construit, les signes distinctifs)
# Avant du dragon = -Y, haut = +Z, unité = mètre
# ==========================================================

random.seed({SEED})            # même dragon à chaque exécution
TAG = "{SLUG}_{STADE_UP}"      # préfixe de tous les objets, matériaux et de la collection
TARGET_HEIGHT = {HEIGHT}       # hauteur finale en mètres (bébé 4, ado 7, adulte 11)
BEVEL_SEGMENTS = 1             # 0 = sans biseau (environ moitié moins de triangles)
TRI_BUDGET = {BUDGET}          # budget de triangles de ce stade et de cette rareté
ADD_FLOATING_FX = True         # éléments flottants autour du dragon (cristaux, braises...)
COLL_NAME = TAG

# ----------------------------------------------------------
# 0. NETTOYAGE (ne touche qu'à ce dragon et à ce stade)
# ----------------------------------------------------------
coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)

def belongs_to_tag(obj):
    """Vrai si l'objet est un root de ce dragon ou un de ses enfants. Les autres stades ne sont jamais touchés."""
    o = obj
    while o is not None:
        if o.name.startswith(TAG + "_"):
            return True
        o = o.parent
    return False

to_delete = [o for o in bpy.data.objects
             if coll in o.users_collection or belongs_to_tag(o)
             or (o.name == "Cube" and o.type == 'MESH' and len(o.data.vertices) == 8)]
for obj in to_delete:
    bpy.data.objects.remove(obj, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)

# @@KIT@@

# ----------------------------------------------------------
# 7. PALETTE DU DRAGON
# ----------------------------------------------------------
# M_BODY = get_mat("Body", "#7DB83A", 0.45)
# ...

# ----------------------------------------------------------
# 8. HIÉRARCHIE
# ----------------------------------------------------------
# master = empty("MASTER_ROOT", dtype='PLAIN_AXES')
# body_root = empty("BODY_ROOT", master) ...

# 9. TÊTE ... 10. CORPS ... 11. PATTES ... 12. AILES ... 13. QUEUE ... 14. RENDU DE RARETÉ / FX

# ----------------------------------------------------------
# 15. FINALISATION
# ----------------------------------------------------------
# finalize(master)
