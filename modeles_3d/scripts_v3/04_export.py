# Formes v3 - export FBX : un fichier par stade (bebe, ado, adulte), pieces separees, modificateurs appliques.
# Les courbes (cornes, os des ailes, bouche) sont converties en maillages. Ecrit dans modeles_3d/export/.
# Affiche aussi le nombre de triangles par stade (a reduire avant Roblox : < 20 000 par piece, ~4 000 vise par pet).
import bpy, os
DIR = globals().get("DIR", r"C:\Users\user\OneDrive\Documents\robloxcreation\modeles_3d\scripts_v3")
OUT = os.path.join(os.path.dirname(DIR), "export"); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
BILAN = {}
for st in ("Bebe", "Ado", "Adulte"):
    coll = bpy.data.collections[st]; tmp = []; tris = 0
    for o in coll.objects:
        if o.type not in ('MESH', 'CURVE'): continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        c = bpy.data.objects.new("Export_" + o.name, me); c.matrix_world = o.matrix_world.copy()
        sc.collection.objects.link(c); tmp.append(c)
        me.calc_loop_triangles(); tris += len(me.loop_triangles)
    for o in sc.objects: o.select_set(False)
    for c in tmp: c.select_set(True)
    bpy.context.view_layer.objects.active = tmp[0]
    path = os.path.join(OUT, f"dragon_classique_{st.lower()}.fbx")
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
                             bake_space_transform=True, mesh_smooth_type='FACE')
    for c in tmp:
        me = c.data; bpy.data.objects.remove(c, do_unlink=True); bpy.data.meshes.remove(me)
    BILAN[st] = (len(tmp), tris, path)
for st, (n, t, p) in BILAN.items(): print(f"{st}: {n} pieces, {t} triangles -> {p}")
