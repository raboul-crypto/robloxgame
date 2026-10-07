# Ailes naturelles pour l'ADO (a lancer apres ado_v11.py + ado_tex.py)
import bpy, bmesh, math
from mathutils import Vector as V, Matrix
sc = bpy.context.scene; P = "Ado_"; coll = bpy.data.collections["Ado"]
S = Matrix.Translation((5.0, 0, 0)) @ Matrix.Scale(1.15, 4)
body = bpy.data.objects[P + "Body"]
for o in [o for o in bpy.data.objects if o.name.startswith((P + "Wing", P + "WingBone"))]:
    bpy.data.objects.remove(o, do_unlink=True)
WM = bpy.data.materials["AdoWingReal"]; BM = bpy.data.materials["AdoBone"]; CM = bpy.data.materials["AdoClawReal"]

def resample(poly, n):
    poly = [V(p) for p in poly]
    seg = [(poly[i + 1] - poly[i]).length for i in range(len(poly) - 1)]
    tot = sum(seg); out = []
    for k in range(n):
        d = tot * k / (n - 1); i = 0
        while i < len(seg) - 1 and d > seg[i]: d -= seg[i]; i += 1
        out.append(poly[i].lerp(poly[i + 1], min(1.0, d / seg[i] if seg[i] else 0)))
    return out
def smooth_poly(poly, it=2):
    pts = [V(p) for p in poly]
    for _ in range(it):                                   # Chaikin : courbes douces
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]): new += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        new.append(pts[-1]); pts = new
    return pts
def link(o):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); return o
def tube(name, pts, radii, mm):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 10
    cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, pp, r in zip(sp.bezier_points, pts, radii):
        bp.co = V(pp); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r
    o = bpy.data.objects.new(name, cu); cu.materials.append(mm); coll.objects.link(o); o.matrix_world = S; return o

K = 1.35
R = V((0, 0, 0)); E = V((0.32, 0.2, 0.22)); W = V((0.6, 0.12, 0.42))
F = [[W, V((0.95, 0.18, 0.55)), V((1.3, 0.35, 0.48))],
     [W, V((0.92, 0.45, 0.32)), V((1.12, 0.78, 0.1))],
     [W, V((0.78, 0.62, 0.12)), V((0.86, 1.02, -0.14))],
     [W, V((0.62, 0.64, 0.0)), V((0.52, 1.06, -0.3))]]
BODY_REAR = V((0.02, 0.95, -0.22))
SAG = V((0, 0.25, -1)).normalized()

for s in (-1, 1):
    d = V((s * 0.45, 0.1, 1)).normalized()
    h, sh, n, _ = body.ray_cast(V((s * 0.25, -0.15, 1.8)) + d * 4, -d)
    root = sh - n * 0.05
    def W2L(p): return root + V((s * p.x, p.y, p.z)) * K          # aile -> espace local du corps
    nt, nv = 16, 9
    bm = bmesh.new()
    def panel(A, Bc, scallop, sag):
        A = resample(smooth_poly(A), nt); Bc = resample(smooth_poly(Bc), nt)
        grid = []
        for i in range(nt):
            t = i / (nt - 1); row = []
            for j in range(nv):
                v = j / (nv - 1)
                p = A[i].lerp(Bc[i], v)
                w = math.sin(math.pi * v)
                p = p + SAG * (sag * w * math.sin(math.pi * t) ** 0.7)         # creux de voile
                p = p.lerp(W, scallop * w * t ** 3)                             # festons du bord
                row.append(bm.verts.new(W2L(p)))
            grid.append(row)
        for i in range(nt - 1):
            for j in range(nv - 1):
                bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    for a, b in zip(F, F[1:]): panel(a, b, 0.22, 0.07)
    panel([W, E, R], F[3] + [BODY_REAR], 0.0, 0.06)                              # panneau interieur jusqu'au flanc
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(P + f"Wing_{s}"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(P + f"Wing_{s}", me); coll.objects.link(o); o.matrix_world = S
    me.materials.append(WM)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    m1 = o.modifiers.new("sol", 'SOLIDIFY'); m1.thickness = 0.012; m1.offset = 0
    m2 = o.modifiers.new("sub", 'SUBSURF'); m2.levels = 1; m2.render_levels = 2
    for p in me.polygons: p.use_smooth = True
    # os
    tube(P + f"WingBone_arm_{s}", [W2L(R), W2L(E), W2L(W)], [0.05 * K, 0.04 * K, 0.034 * K], BM)
    for k, f in enumerate(F):
        pts = [W2L(p) for p in f]
        tube(P + f"WingBone_f{k}_{s}", pts, [0.026 * K, 0.017 * K, 0.004], BM)
    # griffe du pouce au poignet
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.022 * K, radius2=0, depth=0.09 * K)
    c = bpy.context.object; c.name = P + f"WingBone_thumb_{s}"; c.data.materials.append(CM); link(c)
    dirw = V((s * 0.3, -1, 0.4)).normalized()
    c.matrix_world = S @ Matrix.Translation(W2L(W) + dirw * 0.04 * K) @ dirw.to_track_quat('Z', 'Y').to_matrix().to_4x4()

cam = sc.camera; base = "C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"
def shot(name, tgt, dd, dist):
    dd = V(dd).normalized(); cam.location = V(tgt) + dd * dist; cam.rotation_euler = (-dd).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
shot("ailes_dos", (5.0, 0.6, 2.4), (-0.6, 0.8, 0.7), 11)
shot("ailes_profil", (5.0, 1.0, 1.9), (1, -0.15, 0.15), 15)
shot("ailes_face", (5.0, 0.0, 2.2), (0.5, -1, 0.3), 13)
