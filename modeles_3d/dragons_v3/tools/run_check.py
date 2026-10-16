"""Usage: python3 run_check.py script.py out.png [COLL_NAME]
Runs a dragon script in a fresh bpy scene, reports errors, triangle count
(after modifiers), height, object count, and renders a 3/4 thumbnail."""
import sys, math, traceback, runpy, io, contextlib
import bpy
from mathutils import Vector

script, out = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=False)
src = open(script, encoding="utf-8").read()
ns = {"__name__": "__main__"}
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        exec(compile(src, script, "exec"), ns)
    print("RUN_OK")
except Exception:
    print("RUN_ERROR")
    traceback.print_exc()
    sys.exit(1)
print("SCRIPT_STDOUT:", buf.getvalue().strip()[-400:])

dg = bpy.context.evaluated_depsgraph_get()
tris = 0; mins = Vector((1e9,)*3); maxs = Vector((-1e9,)*3); nmesh = 0
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or o.name == "Cube":
        continue
    nmesh += 1
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    me.calc_loop_triangles()
    tris += len(me.loop_triangles)
    mw = o.matrix_world
    for v in me.vertices:
        p = mw @ v.co
        mins = Vector(map(min, mins, p)); maxs = Vector(map(max, maxs, p))
    oe.to_mesh_clear()
size = maxs - mins
print(f"TRIS={tris} MESHES={nmesh} BBOX_MIN={tuple(round(c,2) for c in mins)} BBOX_MAX={tuple(round(c,2) for c in maxs)} SIZE={tuple(round(c,2) for c in size)}")

# ---- render thumbnail ----
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ('CAMERA', 'LIGHT'):
        bpy.data.objects.remove(o, do_unlink=True)
center = (mins + maxs) / 2
radius = max(size.length / 2, 0.01)
def add_cam(name, direction):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = 50
    cam = bpy.data.objects.new(name, cam_data)
    sc.collection.objects.link(cam)
    d = Vector(direction).normalized()
    cam.location = center + d * radius * 2.9
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    return cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN'))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(40), math.radians(10), math.radians(-30))
sc.collection.objects.link(sun)
world = sc.world or bpy.data.worlds.new("W"); sc.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1); bg.inputs[1].default_value = 0.9
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 12
sc.cycles.use_denoising = True
sc.render.resolution_x = 760; sc.render.resolution_y = 600
sc.view_settings.view_transform = 'Standard'
sc.render.film_transparent = False
views = [("a", (-1.0, -1.25, 0.55))]
if len(sys.argv) > 3 and sys.argv[3] == "multi":
    views += [("side", (-1, 0.0, 0.12)), ("front", (0, -1, 0.15))]
for tag, d in views:
    cam = add_cam("Cam_" + tag, d)
    sc.camera = cam
    sc.render.filepath = out if tag == "a" else out.replace(".png", f"_{tag}.png")
    bpy.ops.render.render(write_still=True)
print("RENDER_OK")
