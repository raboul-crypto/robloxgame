"""Banc de test : exécute un script dragon dans Blender headless, vérifie, compte les triangles, rend 2 vues.
Usage : bl/bin/python tools/run.py script.py [out.png] [--json]"""
import sys, os, json, math, traceback, runpy
import bpy
from mathutils import Vector

script = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
bpy.ops.wm.read_factory_settings(use_empty=False)
report = {"script": os.path.basename(script), "ok": True, "errors": [], "warnings": []}
before = set(o.name for o in bpy.data.objects)
try:
    code = open(script, encoding="utf-8").read()
    exec(compile(code, script, "exec"), {"__name__": "__main__"})
    # deuxième exécution : le script doit être relançable sans doublon
    n1 = len(bpy.data.objects)
    exec(compile(code, script, "exec"), {"__name__": "__main__"})
    n2 = len(bpy.data.objects)
    if n1 != n2:
        report["warnings"].append(f"relance : {n1} objets puis {n2} (doublons ?)")
except Exception:
    report["ok"] = False
    report["errors"].append(traceback.format_exc()[-1500:])

dg = bpy.context.evaluated_depsgraph_get()
tris = 0; meshes = []
lo = Vector((1e9,)*3); hi = Vector((-1e9,)*3)
roots = [o for o in bpy.data.objects if o.name.endswith("_MASTER_ROOT")]
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    meshes.append(o)
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    tris += len(me.loop_triangles)
    mw = ev.matrix_world
    for v in me.vertices:
        p = mw @ v.co
        lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    ev.to_mesh_clear()
    r = o
    while r.parent: r = r.parent
    if not r.name.endswith("_MASTER_ROOT"):
        report["warnings"].append(f"objet hors hiérarchie : {o.name}")
report.update(triangles=tris, objets=len(meshes), roots=[r.name for r in roots],
              collections=[c.name for c in bpy.data.collections],
              bbox_min=[round(x, 2) for x in lo], bbox_max=[round(x, 2) for x in hi],
              hauteur=round(hi.z - lo.z, 2), longueur=round(hi.y - lo.y, 2), largeur=round(hi.x - lo.x, 2))
if len(report["warnings"]) > 8:
    report["warnings"] = report["warnings"][:8] + [f"... {len(report['warnings'])-8} de plus"]

if out and meshes:
    sc = bpy.context.scene
    for o in [o for o in bpy.data.objects if o.type in ('CAMERA', 'LIGHT')]:
        bpy.data.objects.remove(o, do_unlink=True)
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_cavity = True
    sh.cavity_type = 'WORLD'; sh.show_shadows = False; sh.show_object_outline = True
    sc.render.resolution_x = 640; sc.render.resolution_y = 640
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("W"); sc.world.color = (0.82, 0.82, 0.80)
    sc.display.shading.background_type = 'VIEWPORT'
    center = (lo + hi) / 2; size = max(hi - lo)
    cam_data = bpy.data.cameras.new("C"); cam_data.type = 'ORTHO'; cam_data.ortho_scale = size * 1.15
    cam = bpy.data.objects.new("CAM", cam_data); sc.collection.objects.link(cam); sc.camera = cam
    views = {"face34": Vector((-1.0, -1.3, 0.55)), "profil": Vector((1, 0, 0.08)), "face": Vector((0, -1, 0.1))}
    files = []
    for name, d in views.items():
        d = d.normalized()
        cam.location = center + d * size * 3
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        f = out.replace(".png", f"_{name}.png")
        sc.render.filepath = f
        bpy.ops.render.render(write_still=True)
        files.append(f)
    try:
        from PIL import Image
        ims = [Image.open(f) for f in files]
        W = sum(i.width for i in ims); H = max(i.height for i in ims)
        canvas = Image.new("RGB", (W, H), (255, 255, 255))
        x = 0
        for i in ims:
            canvas.paste(i, (x, 0)); x += i.width
        canvas.save(out)
        for f in files: os.remove(f)
    except Exception as e:
        report["warnings"].append(f"assemblage rendu : {e}")
    report["render"] = out
print("REPORT_JSON " + json.dumps(report, ensure_ascii=False))
