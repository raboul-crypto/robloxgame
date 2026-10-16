# ----------------------------------------------------------
# 1. MATÉRIAUX (réutilisés s'ils existent, toujours mis à jour)
# ----------------------------------------------------------
def hex_lin(h, a=1.0):
    """Couleur hex (#RRGGBB) -> RGBA en espace linéaire (ce que Blender attend)."""
    h = h.lstrip("#")
    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), a)

def get_mat(name, hexcol, roughness=0.45, metallic=0.0, emission=None, strength=2.5, alpha=1.0):
    """Principled BSDF. 'emission' = hex de la lueur (cristaux, braises, yeux...).
    Compatible Blender 4.x et 5.x ('Emission Color' ou 'Emission')."""
    full = f"{TAG}_{name}"
    mat = bpy.data.materials.get(full) or bpy.data.materials.new(full)
    mat.use_nodes = True
    col = hex_lin(hexcol)
    mat.diffuse_color = col
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        if emission:
            bsdf.inputs[key].default_value = hex_lin(emission)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = strength
        elif "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.0
        bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = 'BLENDED'
        elif hasattr(mat, "blend_method"):
            mat.blend_method = 'BLEND'
    return mat

# ----------------------------------------------------------
# 2. MESHES DE BASE (bmesh / from_pydata, jamais bpy.ops)
# ----------------------------------------------------------
def mesh_from(name, verts, faces):
    me = bpy.data.meshes.new(f"{TAG}_{name}")
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me

def box_mesh(sx, sy, sz):
    x, y, z = sx / 2, sy / 2, sz / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_from("box", v, f)

def wedge_mesh(sx, sy, sz, top_x=0.7, top_y=0.8, shift_y=0.0):
    """Bloc dont le dessus est rétréci (top_x, top_y en proportion) et décalé en Y :
    crânes, museaux, cuisses musclées, plaques d'armure."""
    x, y, z = sx / 2, sy / 2, sz / 2
    tx, ty = x * top_x, y * top_y
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-tx, -ty + shift_y, z), (tx, -ty + shift_y, z), (tx, ty + shift_y, z), (-tx, ty + shift_y, z)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_from("wedge", v, f)

def shard_mesh(w, t, L):
    """Éclat plat et pointu orienté vers +Y (crinière, écailles, griffes, flammes, feuilles)."""
    v = [(-w * 0.25, 0, 0), (0, 0, t * 0.25), (w * 0.25, 0, 0), (0, 0, -t * 0.25),
         (-w / 2, L * 0.35, 0), (0, L * 0.35, t / 2), (w / 2, L * 0.35, 0), (0, L * 0.35, -t / 2),
         (0, L, 0)]
    f = [(0, 1, 2, 3), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
         (4, 8, 5), (5, 8, 6), (6, 8, 7), (7, 8, 4)]
    return mesh_from("shard", v, f)

def crystal_mesh(r, h, tip, sides=6):
    """Prisme à pointe orienté vers +Y (cristaux, gemmes, perles taillées)."""
    v = []
    for k in range(sides):
        a = k * 2 * math.pi / sides
        v.append((r * math.cos(a), 0, r * math.sin(a)))
    for k in range(sides):
        a = k * 2 * math.pi / sides
        v.append((r * 0.9 * math.cos(a), h, r * 0.9 * math.sin(a)))
    v.append((0, h + tip, 0))
    f = [tuple(range(sides - 1, -1, -1))]
    for k in range(sides):
        n = (k + 1) % sides
        f.append((k, n, sides + n, sides + k))
    for k in range(sides):
        n = (k + 1) % sides
        f.append((sides + k, sides + n, 2 * sides))
    return mesh_from("crystal", v, f)

def prism_mesh(r, h, sides=6, top=1.0):
    """Prisme / disque à n faces, axe +Y (galets, disques, pupilles rondes, perles)."""
    v = []
    for k in range(sides):
        a = k * 2 * math.pi / sides
        v.append((r * math.cos(a), -h / 2, r * math.sin(a)))
    for k in range(sides):
        a = k * 2 * math.pi / sides
        v.append((r * top * math.cos(a), h / 2, r * top * math.sin(a)))
    f = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
    for k in range(sides):
        n = (k + 1) % sides
        f.append((k, n, sides + n, sides + k))
    return mesh_from("prism", v, f)

def ring_mesh(r, w, t, sides=12):
    """Anneau plat (halo, bracelet, anneau runique) dans le plan XZ, axe +Y."""
    v, f = [], []
    for k in range(sides):
        a = k * 2 * math.pi / sides
        for rr, yy in ((r + w / 2, -t / 2), (r - w / 2, -t / 2), (r - w / 2, t / 2), (r + w / 2, t / 2)):
            v.append((rr * math.cos(a), yy, rr * math.sin(a)))
    for k in range(sides):
        n = (k + 1) % sides
        for j in range(4):
            jn = (j + 1) % 4
            f.append((k * 4 + j, k * 4 + jn, n * 4 + jn, n * 4 + j))
    return mesh_from("ring", v, f)

def plate_mesh(pts, t):
    """Membrane épaisse (aile, nageoire, feuille) à partir d'un polygone 3D convexe 'pts'
    (coordonnées du parent). Épaisseur t le long de la normale."""
    pts = [Vector(p) for p in pts]
    c = sum(pts, Vector()) / len(pts)
    nrm = Vector()
    for i in range(len(pts)):
        nrm += (pts[i] - c).cross(pts[(i + 1) % len(pts)] - c)
    nrm = nrm.normalized() if nrm.length > 1e-6 else Vector((0, 0, 1))
    n = len(pts)
    v = [tuple(p + nrm * t / 2) for p in pts] + [tuple(p - nrm * t / 2) for p in pts]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    return mesh_from("plate", v, f)

# ----------------------------------------------------------
# 3. OUTILS DE PLACEMENT
# ----------------------------------------------------------
def basis(direction, up=(0, 0, 1)):
    """Matrice 3x3 dont l'axe local Y suit 'direction'."""
    y = Vector(direction).normalized()
    x = y.cross(Vector(up))
    if x.length < 1e-4:
        x = y.cross(Vector((0, 1, 0)))
        if x.length < 1e-4:
            x = y.cross(Vector((1, 0, 0)))
    x.normalize()
    z = x.cross(y).normalized()
    return Matrix((x, y, z)).transposed()

def place(name, mesh, mat, loc, rot=None, parent=None, bevel=0.0):
    obj = bpy.data.objects.new(f"{TAG}_{name}", mesh)
    coll.objects.link(obj)
    if parent:
        obj.parent = parent
    if rot is None:
        R = Matrix.Identity(3)
    elif isinstance(rot, Matrix):
        R = rot.to_3x3()
    else:
        R = Euler([math.radians(a) for a in rot]).to_matrix()
    obj.matrix_basis = Matrix.Translation(Vector(loc)) @ R.to_4x4()
    mesh.materials.append(mat)
    if bevel > 0 and BEVEL_SEGMENTS > 0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = BEVEL_SEGMENTS
        m.limit_method = 'ANGLE'
    return obj

def box(name, size, loc, rot=None, mat=None, parent=None, bevel=0.04):
    return place(name, box_mesh(*size), mat, loc, rot, parent, bevel)

def wedge(name, size, loc, rot=None, mat=None, parent=None, top_x=0.7, top_y=0.8, shift_y=0.0, bevel=0.04):
    return place(name, wedge_mesh(*size, top_x, top_y, shift_y), mat, loc, rot, parent, bevel)

def shard(name, w, t, L, loc, direction, mat=None, parent=None, up=(0, 0, 1)):
    return place(name, shard_mesh(w, t, L), mat, loc, basis(direction, up), parent)

def crystal(name, r, h, tip, loc, direction, mat=None, parent=None, up=(0, 0, 1), sides=6):
    return place(name, crystal_mesh(r, h, tip, sides), mat, loc, basis(direction, up), parent)

def prism(name, r, h, loc, direction=(0, 1, 0), mat=None, parent=None, sides=6, top=1.0, up=(0, 0, 1), bevel=0.0):
    return place(name, prism_mesh(r, h, sides, top), mat, loc, basis(direction, up), parent, bevel)

def ring(name, r, w, t, loc, direction=(0, 1, 0), mat=None, parent=None, sides=12, up=(0, 0, 1)):
    return place(name, ring_mesh(r, w, t, sides), mat, loc, basis(direction, up), parent)

def plate(name, pts, t, mat=None, parent=None):
    return place(name, plate_mesh(pts, t), mat, (0, 0, 0), None, parent)

def link(name, p1, p2, thick, mat, parent, up=(0, 0, 1), extra=0.12, bevel=0.03, depth=None):
    """Barre entre deux points (os de patte, bois, moustache, os d'aile)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    dz = thick if depth is None else depth
    return place(name, box_mesh(thick, d.length + extra, dz), mat, (p1 + p2) / 2, basis(d, up), parent, bevel)

def chain(name, pts, t0, t1, mat, parent, up=(0, 0, 1), bevel=None):
    """Suite de barres qui s'affinent de t0 à t1 (bois ramifiés, moustaches, tentacules)."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        link(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up, extra=th * 0.6, bevel=min(0.03, th * 0.2) if bevel is None else bevel)

def empty(name, parent=None, mtx=None, dtype='ARROWS'):
    e = bpy.data.objects.new(f"{TAG}_{name}", None)
    coll.objects.link(e)
    e.empty_display_type = dtype
    e.empty_display_size = 0.6
    if parent:
        e.parent = parent
    if mtx is not None:
        e.matrix_basis = mtx
    return e

def pick(mats, weights=None):
    """Choix aléatoire (reproductible grâce à la seed) parmi plusieurs matériaux."""
    return random.choices(mats, weights=weights)[0]

# ----------------------------------------------------------
# 4. COURBES (corps de serpent, cous longs, queues)
# ----------------------------------------------------------
def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

def sample_curve(ctrl, per_span=16):
    ctrl = [Vector(p) for p in ctrl]
    ext = [ctrl[0] + (ctrl[0] - ctrl[1])] + ctrl + [ctrl[-1] + (ctrl[-1] - ctrl[-2])]
    pts = []
    for i in range(1, len(ext) - 2):
        for k in range(per_span):
            pts.append(catmull(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / per_span))
    pts.append(ctrl[-1].copy())
    return pts

def resample(pts, spacing):
    """Rééchantillonne une polyligne à pas constant."""
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + (pts[i] - pts[i - 1]).length)
    total = cum[-1]
    n = max(2, int(total / spacing))
    out, j = [], 0
    for k in range(n + 1):
        d = k * total / n
        while j < len(cum) - 2 and cum[j + 1] < d:
            j += 1
        seg = cum[j + 1] - cum[j]
        t = (d - cum[j]) / seg if seg > 0 else 0
        out.append(pts[j].lerp(pts[j + 1], t))
    return out

def frame(tangent, ref=(1, 0, 0)):
    """Repère d'un segment : tangente, dos, côté (+X)."""
    t = Vector(tangent).normalized()
    d = Vector(ref).cross(t)
    if d.length < 1e-4:
        d = Vector((0, 1, 0)).cross(t)
    d.normalize()
    side = t.cross(d).normalized()
    return t, d, side

def keyed(keys, s):
    """Interpolation linéaire dans une liste [(s, valeur), ...] (rayons, épaisseurs)."""
    for (s0, r0), (s1, r1) in zip(keys, keys[1:]):
        if s <= s1:
            return r0 + (r1 - r0) * (s - s0) / (s1 - s0)
    return keys[-1][1]

def seg_matrix(t, d, side):
    """Matrice qui aligne X = côté, Y = tangente, Z = dos."""
    return Matrix((side, t, d)).transposed()

# ----------------------------------------------------------
# 5. AILE MEMBRANEUSE (os + doigts + membranes), réutilisable
# ----------------------------------------------------------
def wing(name, root, sgn, span, mat_bone, mat_memb, parent, lift=0.35, sweep=0.35, fingers=3,
         bone=0.16, droop=0.25, memb_t=0.05, claw_mat=None, bevel=0.0):
    """Aile de dragon côté 'sgn' (+1 = +X, -1 = -X) qui part de 'root' (coord. du parent).
    span = longueur d'UNE aile. lift = montée du poignet, sweep = recul vers +Y.
    Renvoie la position du poignet (utile pour griffes / ornements)."""
    root = Vector(root)
    elbow = root + Vector((sgn * span * 0.38, span * sweep * 0.25, span * lift * 0.9))
    wrist = root + Vector((sgn * span * 0.62, span * sweep * 0.45, span * lift))
    link(f"{name}_Arm", root, elbow, bone * 1.25, mat_bone, parent, up=(0, 1, 0), bevel=bevel)
    link(f"{name}_Fore", elbow, wrist, bone, mat_bone, parent, up=(0, 1, 0), bevel=bevel)
    tips = []
    for k in range(fingers):
        f = k / max(1, fingers - 1)
        tip = wrist + Vector((sgn * span * (0.38 - 0.18 * f), span * (0.15 + 0.55 * f), -span * (0.05 + droop * f)))
        link(f"{name}_Finger_{k}", wrist, tip, bone * (0.8 - 0.15 * f), mat_bone, parent, up=(0, 1, 0), bevel=bevel)
        tips.append(tip)
    # Membranes tendues entre les doigts, puis jusqu'au flanc
    edge = [elbow.lerp(wrist, 0.5)] + tips + [root + Vector((sgn * span * 0.05, span * 0.45, -span * 0.12))]
    for k in range(len(edge) - 1):
        a, b = edge[k], edge[k + 1]
        plate(f"{name}_Memb_{k}", [wrist, a, b], memb_t, mat_memb, parent)
    plate(f"{name}_Memb_Root", [root, elbow, wrist, edge[-1]], memb_t, mat_memb, parent)
    if claw_mat:
        shard(f"{name}_ThumbClaw", 0.12, 0.08, 0.35, wrist, (sgn * 0.3, -0.6, 0.8), mat=claw_mat, parent=parent)
    return wrist

# ----------------------------------------------------------
# 6. FINALISATION : taille, sol, triangles, vue
# ----------------------------------------------------------
def finalize(master):
    """Met le dragon à TARGET_HEIGHT, pieds (ou ventre) sur Z = 0, centré en X/Y,
    puis affiche le nombre de triangles après modificateurs."""
    bpy.context.view_layer.update()
    meshes = [o for o in coll.objects if o.type == 'MESH']
    def bounds():
        """Boîte englobante exacte (après modificateurs) de toutes les pièces."""
        dg = bpy.context.evaluated_depsgraph_get()
        mn, mx = Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))
        for o in meshes:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ev.matrix_world
            for v in me.vertices:
                w = mw @ v.co
                mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
            ev.to_mesh_clear()
        return mn, mx
    mn, mx = bounds()
    s = TARGET_HEIGHT / max(1e-6, (mx.z - mn.z))
    master.matrix_basis = Matrix.Scale(s, 4) @ master.matrix_basis
    bpy.context.view_layer.update()
    mn, mx = bounds()
    c = (mn + mx) / 2
    master.matrix_basis = Matrix.Translation((-c.x, -c.y, -mn.z)) @ master.matrix_basis
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for o in meshes:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        ev.to_mesh_clear()
    screen = getattr(bpy.context, "screen", None)
    if screen:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.overlay.show_relationship_lines = False
    print(f"{TAG} généré : {len(meshes)} pièces, {tris} triangles (budget {TRI_BUDGET}), "
          f"hauteur {TARGET_HEIGHT} m.")
    if tris > TRI_BUDGET:
        print("  -> au-dessus du budget : mets BEVEL_SEGMENTS = 0 ou ADD_FLOATING_FX = False.")
    return tris
