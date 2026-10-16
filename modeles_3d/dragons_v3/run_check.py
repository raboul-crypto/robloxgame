"""Usage: python3 run_check.py script.py [render.png]
Runs a dragon script in a fresh bpy scene, prints triangle count (after modifiers),
height, min Z, object count, and optionally renders a 3/4 front preview with Cycles CPU."""
import sys, math, bpy, traceback
from mathutils import Vector
path = sys.argv[1]; render = sys.argv[2] if len(sys.argv) > 2 else None
bpy.ops.wm.read_factory_settings(use_empty=False)
src = open(path, encoding="utf-8").read()
# bpy.context.screen is None in background mode: tolerate view-setting code
try:
    exec(compile(src, path, "exec"), {"__name__": "__main__"})
except Exception:
    traceback.print_exc(); print("RESULT: ERROR"); sys.exit(1)
dg = bpy.context.evaluated_depsgraph_get()
tris = 0; mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3); nobj = 0
for o in bpy.context.scene.objects:
    if o.type != 'MESH': continue
    nobj += 1
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    me.calc_loop_triangles(); tris += len(me.loop_triangles)
    for v in me.vertices:
        w = ev.matrix_world @ v.co
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    ev.to_mesh_clear()
print(f"RESULT: OK tris={tris} objects={nobj} size=({mx.x-mn.x:.2f},{mx.y-mn.y:.2f},{mx.z-mn.z:.2f}) minZ={mn.z:.3f} maxZ={mx.z:.3f}")
if render:
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o.type in ('CAMERA','LIGHT'): bpy.data.objects.remove(o, do_unlink=True)
    c = (mn + mx) / 2; ext = max(mx - mn)
    cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam)
    cam_d.lens = 50
    view = Vector((0.9, -1.6, 0.55)).normalized() if len(sys.argv) < 4 else Vector(eval(sys.argv[3])).normalized()
    cam.location = c + view * ext * 1.65
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    for i, (rot, en) in enumerate([((math.radians(50), 0, math.radians(30)), 3.5), ((math.radians(60), 0, math.radians(-140)), 1.5)]):
        ld = bpy.data.lights.new(f"sun{i}", 'SUN'); ld.energy = en
        lo = bpy.data.objects.new(f"sun{i}", ld); lo.rotation_euler = rot; sc.collection.objects.link(lo)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = (0.55, 0.6, 0.68, 1); bg.inputs[1].default_value = 0.6
    sc.world = w
    gm = bpy.data.meshes.new("ground"); r = ext * 3
    gm.from_pydata([(c.x-r,c.y-r,0),(c.x+r,c.y-r,0),(c.x+r,c.y+r,0),(c.x-r,c.y+r,0)],[],[(0,1,2,3)])
    g = bpy.data.objects.new("ground", gm); sc.collection.objects.link(g)
    gmat = bpy.data.materials.new("groundmat"); gmat.diffuse_color = (0.35,0.36,0.38,1)
    gmat.use_nodes = True; gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3,0.31,0.33,1)
    gm.materials.append(gmat)
    import os
    if os.environ.get("RENDER_ENGINE", "WORKBENCH") == "CYCLES":
        sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
        sc.cycles.use_denoising = False
    else:  # rapide pour les itérations : couleurs des matériaux, lumière studio, ombres
        sc.render.engine = 'BLENDER_WORKBENCH'
        sh = sc.display.shading
        sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
        sh.show_shadows = True; sh.show_cavity = True; sh.cavity_type = 'WORLD'
        sh.background_type = 'VIEWPORT'; sh.background_color = (0.55, 0.6, 0.68)
    sc.render.resolution_x = 800; sc.render.resolution_y = 800
    sc.view_settings.view_transform = 'Standard'
    sc.render.filepath = render
    bpy.ops.render.render(write_still=True)
    print("RENDER:", render)
