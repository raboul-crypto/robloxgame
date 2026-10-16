import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

# ==========================================================
# DRAGON PETS SIMULATOR - ADULTE MIRAGE (v3 : fidèle au concept)
#  - Pose en S, tête haute, dragon oriental "flottant"
#  - Crinière en éclats, bois ramifiés, moustaches tombantes
#  - Ventre en plaques crème, plastron avec gemme, cristaux en grappes
#  - Pattes avec bracelets dorés et griffes
# Avant du dragon = -Y, haut = +Z
# ==========================================================

random.seed(7)                 # même résultat à chaque exécution
ADD_FLOATING_FX = True         # petits cristaux flottants autour du dragon
COLL_NAME = "MIRAGE_ADULTE"

# ----------------------------------------------------------
# 0. NETTOYAGE (nouvelle version + restes de l'ancien script)
# ----------------------------------------------------------
coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)

def belongs_to_adulte(obj):
    """Vrai si l'objet est un root MIRAGE_ADULTE ou un de ses enfants (ancien script inclus).
    Les modèles Bébé / Ado ne sont jamais touchés."""
    o = obj
    while o is not None:
        if o.name.startswith("MIRAGE_ADULTE"):
            return True
        o = o.parent
    return False

to_delete = [o for o in bpy.data.objects
             if coll in o.users_collection or belongs_to_adulte(o) or o.name == "Cube"]
for obj in to_delete:
    bpy.data.objects.remove(obj, do_unlink=True)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)

# ----------------------------------------------------------
# 1. MATÉRIAUX (mis à jour à chaque exécution)
# ----------------------------------------------------------
def get_mat(name, color, roughness=0.45, metallic=0.0, emission=None, strength=2.5):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
            bsdf.inputs[key].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = strength
    return mat

# Couleurs en espace linéaire (Blender) : saturées pour garder un vrai doré à l'écran
M_GOLD   = get_mat("Mirage_Gold",      (0.80, 0.42, 0.04, 1), 0.35, 0.15)
M_LGOLD  = get_mat("Mirage_LightGold", (0.95, 0.62, 0.12, 1), 0.40, 0.10)
M_DGOLD  = get_mat("Mirage_DarkGold",  (0.45, 0.20, 0.03, 1), 0.35, 0.20)
M_BROWN  = get_mat("Mirage_Brown",     (0.25, 0.10, 0.02, 1), 0.60)
M_CREAM  = get_mat("Mirage_Cream",     (0.85, 0.70, 0.40, 1), 0.50)
M_WING   = get_mat("Mirage_WingGrey",  (0.55, 0.50, 0.40, 1), 0.55)
M_ANTLER = get_mat("Mirage_Antler",    (0.45, 0.36, 0.24, 1), 0.60)
M_CYAN   = get_mat("Mirage_Cyan",      (0.05, 0.85, 0.80, 1), 0.10, 0.0, (0.05, 0.95, 0.85, 1), 3.0)
M_WHITE  = get_mat("Mirage_EyeWhite",  (0.92, 0.92, 0.88, 1), 0.30)
M_IRIS   = get_mat("Mirage_Iris",      (0.98, 0.78, 0.12, 1), 0.20)
M_BLACK  = get_mat("Mirage_Black",     (0.03, 0.02, 0.02, 1), 0.20)
M_CLAW   = get_mat("Mirage_Claw",      (0.95, 0.93, 0.86, 1), 0.30)

# ----------------------------------------------------------
# 2. MESHES DE BASE (créés directement, sans bpy.ops = rapide)
# ----------------------------------------------------------
def mesh_from(name, verts, faces):
    me = bpy.data.meshes.new(name)
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
    return mesh_from("MIR_box", v, f)

def shard_mesh(w, t, L):
    """Éclat plat et pointu orienté vers +Y (crinière, écailles, griffes)."""
    v = [(-w * 0.25, 0, 0), (0, 0, t * 0.25), (w * 0.25, 0, 0), (0, 0, -t * 0.25),
         (-w / 2, L * 0.35, 0), (0, L * 0.35, t / 2), (w / 2, L * 0.35, 0), (0, L * 0.35, -t / 2),
         (0, L, 0)]
    f = [(0, 1, 2, 3), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
         (4, 8, 5), (5, 8, 6), (6, 8, 7), (7, 8, 4)]
    return mesh_from("MIR_shard", v, f)

def crystal_mesh(r, h, tip):
    """Prisme hexagonal à pointe, orienté vers +Y."""
    v = []
    for k in range(6):
        a = k * math.pi / 3
        v.append((r * math.cos(a), 0, r * math.sin(a)))
    for k in range(6):
        a = k * math.pi / 3
        v.append((r * 0.9 * math.cos(a), h, r * 0.9 * math.sin(a)))
    v.append((0, h + tip, 0))
    f = [tuple(range(5, -1, -1))]
    for k in range(6):
        n = (k + 1) % 6
        f.append((k, n, 6 + n, 6 + k))
    for k in range(6):
        n = (k + 1) % 6
        f.append((6 + k, 6 + n, 12))
    return mesh_from("MIR_crystal", v, f)

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
    obj = bpy.data.objects.new("MIR_" + name, mesh)
    coll.objects.link(obj)
    if parent:
        obj.parent = parent
    if rot is None:
        R = Matrix.Identity(3)
    elif isinstance(rot, Matrix):
        R = rot
    else:
        R = Euler([math.radians(a) for a in rot]).to_matrix()
    obj.matrix_basis = Matrix.Translation(Vector(loc)) @ R.to_4x4()
    mesh.materials.append(mat)
    if bevel > 0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
    return obj

def box(name, size, loc, rot=None, mat=M_GOLD, parent=None, bevel=0.04):
    return place(name, box_mesh(*size), mat, loc, rot, parent, bevel)

def shard(name, w, t, L, loc, direction, mat=M_GOLD, parent=None, up=(0, 0, 1)):
    return place(name, shard_mesh(w, t, L), mat, loc, basis(direction, up), parent)

def crystal(name, r, h, tip, loc, direction, parent=None, mat=M_CYAN, up=(0, 0, 1)):
    return place(name, crystal_mesh(r, h, tip), mat, loc, basis(direction, up), parent)

def link(name, p1, p2, thick, mat, parent, up=(0, 0, 1), extra=0.12, bevel=0.03):
    """Barre entre deux points (os de patte, bois, moustache)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return place(name, box_mesh(thick, d.length + extra, thick), mat, (p1 + p2) / 2, basis(d, up), parent, bevel)

def chain(name, pts, t0, t1, mat, parent, up=(0, 0, 1)):
    n = len(pts) - 1
    for i in range(n):
        th = t0 + (t1 - t0) * (i / max(1, n - 1))
        link(f"{name}_{i}", pts[i], pts[i + 1], th, mat, parent, up, extra=th * 0.6, bevel=min(0.03, th * 0.2))

def empty(name, parent=None, mtx=None, dtype='ARROWS'):
    e = bpy.data.objects.new("MIRAGE_ADULTE_" + name, None)
    coll.objects.link(e)
    e.empty_display_type = dtype
    e.empty_display_size = 0.6
    if parent:
        e.parent = parent
    if mtx is not None:
        e.matrix_basis = mtx
    return e

def pick_mane_mat():
    return random.choices([M_GOLD, M_LGOLD, M_BROWN, M_DGOLD], weights=[4, 3, 2, 2])[0]

# ----------------------------------------------------------
# 4. HIÉRARCHIE (mêmes roots que l'ancien script)
# ----------------------------------------------------------
HEAD_POS = Vector((0, -0.4, 9.2))
master    = empty("MASTER_ROOT", dtype='PLAIN_AXES')
body_root = empty("BODY_ROOT", master)
legs_root = empty("LEGS_ROOT", master)
tail_root = empty("TAIL_ROOT", master)
head_root = empty("HEAD_ROOT", master,
                  Matrix.Translation(HEAD_POS) @ Euler((math.radians(5), 0, 0)).to_matrix().to_4x4())
H = head_root

# ----------------------------------------------------------
# 5. TÊTE (coordonnées locales à HEAD_ROOT)
# ----------------------------------------------------------
box("Head_Skull",       (1.5, 1.55, 1.35), (0, 0, 0), mat=M_GOLD, parent=H, bevel=0.07)
box("Head_Snout",       (1.15, 1.55, 0.72), (0, -1.4, -0.15), mat=M_GOLD, parent=H, bevel=0.06)
box("Head_SnoutBridge", (0.8, 1.2, 0.2), (0, -1.25, 0.28), rot=(-6, 0, 0), mat=M_LGOLD, parent=H, bevel=0.03)
box("Head_NosePad",     (1.2, 0.3, 0.55), (0, -2.1, -0.12), mat=M_GOLD, parent=H)
box("Head_Jaw",         (1.05, 1.45, 0.32), (0, -1.25, -0.68), mat=M_LGOLD, parent=H)
box("Head_MouthLine",   (1.08, 1.4, 0.06), (0, -1.28, -0.52), mat=M_DGOLD, parent=H, bevel=0)

# Joyau frontal + couronne dorée
box("Head_GemSocket", (0.7, 0.5, 0.16), (0, -0.62, 0.66), rot=(-20, 0, 0), mat=M_DGOLD, parent=H, bevel=0.03)
crystal("Head_Gem", 0.22, 0.15, 0.22, (0, -0.78, 0.68), (0, -0.45, 1), parent=H)

for sgn in (-1, 1):
    # Narines
    box(f"Head_Nostril_{sgn}", (0.2, 0.06, 0.18), (sgn * 0.27, -2.27, 0.0), mat=M_BLACK, parent=H, bevel=0)
    # Œil : blanc, iris jaune, pupille fendue
    box(f"Head_EyeWhite_{sgn}", (0.08, 0.45, 0.36), (sgn * 0.76, -0.35, 0.12), mat=M_WHITE, parent=H, bevel=0.01)
    box(f"Head_Iris_{sgn}",     (0.06, 0.26, 0.30), (sgn * 0.80, -0.38, 0.12), mat=M_IRIS, parent=H, bevel=0)
    box(f"Head_Pupil_{sgn}",    (0.05, 0.07, 0.26), (sgn * 0.83, -0.38, 0.12), mat=M_BLACK, parent=H, bevel=0)
    box(f"Head_Brow_{sgn}",     (0.35, 0.7, 0.22), (sgn * 0.72, -0.4, 0.44), rot=(12, 0, sgn * -8), mat=M_DGOLD, parent=H, bevel=0.03)

    # Couronne autour du joyau
    shard(f"Head_GemFrame_{sgn}", 0.25, 0.12, 0.6, (sgn * 0.3, -0.65, 0.7), (sgn * 0.5, 0.1, 1), mat=M_LGOLD, parent=H)
    shard(f"Head_Crown_{sgn}", 0.32, 0.12, 0.85, (sgn * 0.45, -0.1, 0.7), (sgn * 0.4, 0.6, 1), mat=M_GOLD, parent=H)

    # Oreilles / nageoires et pointes de joues
    shard(f"Head_Ear_{sgn}", 0.42, 0.1, 1.0, (sgn * 0.75, 0.3, 0.35), (sgn * 0.8, 1, 0.4), mat=M_LGOLD, parent=H)
    shard(f"Head_Cheek1_{sgn}", 0.3, 0.1, 0.8, (sgn * 0.6, -0.6, -0.55), (sgn * 0.9, 0.8, -0.3), mat=M_LGOLD, parent=H)
    shard(f"Head_Cheek2_{sgn}", 0.3, 0.1, 0.9, (sgn * 0.55, -0.2, -0.6), (sgn * 0.7, 1, -0.6), mat=M_GOLD, parent=H)

    # Bois de cerf ramifiés
    a0 = Vector((sgn * 0.45, 0.35, 0.65))
    a1 = Vector((sgn * 0.9, 0.9, 1.8))
    a2 = Vector((sgn * 1.2, 1.6, 2.9))
    a3 = Vector((sgn * 1.25, 2.3, 3.6))
    chain(f"Head_Antler_{sgn}", [a0, a1, a2, a3], 0.32, 0.18, M_ANTLER, H)
    link(f"Head_AntlerTine1_{sgn}", a1, (sgn * 1.1, 0.3, 2.7), 0.18, M_ANTLER, H)
    link(f"Head_AntlerTine2_{sgn}", a2, (sgn * 1.8, 1.3, 3.6), 0.16, M_ANTLER, H)
    link(f"Head_AntlerTine3_{sgn}", a2.lerp(a3, 0.4), (sgn * 0.85, 2.0, 3.9), 0.14, M_ANTLER, H)

    # Longues moustaches qui tombent vers l'arrière
    chain(f"Head_Whisker_{sgn}",
          [(sgn * 0.58, -1.95, -0.05), (sgn * 1.3, -1.6, -0.45), (sgn * 1.8, -0.8, -1.0),
           (sgn * 2.0, 0.2, -1.8), (sgn * 1.9, 0.8, -2.6)], 0.10, 0.07, M_LGOLD, H)

# Barbe sous le menton
for k in range(5):
    x = (k - 2) * 0.18
    shard(f"Head_Beard_{k}", 0.22, 0.08, 0.7 + random.random() * 0.3,
          (x, -0.9 + abs(x) * 0.5, -0.82), (x * 0.4, 0.5, -1), mat=pick_mane_mat(), parent=H)

# Crinière en éventail derrière la tête
for ring in range(3):
    count = 14
    for k in range(count):
        ang = math.radians(-155 + k * (310 / (count - 1)) + ring * 8)
        radial = Vector((math.sin(ang), 0, math.cos(ang)))
        loc = (radial.x * 0.6, 0.4 + ring * 0.3, radial.z * 0.55 - 0.05)
        jitter = Vector((random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.2), random.uniform(-0.2, 0.2)))
        direction = radial * (1.1 - ring * 0.3) + Vector((0, 1.0, 0)) + jitter
        shard(f"Head_Mane_{ring}_{k}", 0.65 - ring * 0.08, 0.14, 1.4 + ring * 0.3 + random.random() * 0.5,
              loc, direction, mat=pick_mane_mat(), parent=H, up=tuple(radial.cross(Vector((0, 1, 0)))))

# ----------------------------------------------------------
# 6. COLONNE VERTÉBRALE EN S (courbe lissée)
# ----------------------------------------------------------
CTRL = [Vector(p) for p in [
    (0.0, -0.2, 9.0),   # sous le crâne
    (0.0,  0.3, 8.3),
    (0.0,  0.9, 7.1),   # cou
    (0.0,  0.9, 5.8),
    (0.0,  0.3, 4.6),   # poitrail
    (0.0,  0.1, 3.3),
    (0.3,  0.9, 2.2),
    (0.6,  2.4, 1.7),   # bas du ventre
    (0.6,  3.9, 2.2),
    (0.4,  5.2, 3.0),   # hanches
    (0.1,  6.4, 4.1),
    (-0.3, 7.2, 5.4),   # queue qui remonte
    (-0.6, 7.4, 6.6),
    (-0.9, 6.9, 7.5),
    (-1.0, 6.1, 7.7),   # bout de queue enroulé vers l'avant
]]

def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

def sample_curve(ctrl, per_span=16):
    ext = [ctrl[0] + (ctrl[0] - ctrl[1])] + ctrl + [ctrl[-1] + (ctrl[-1] - ctrl[-2])]
    pts = []
    for i in range(1, len(ext) - 2):
        for k in range(per_span):
            pts.append(catmull(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / per_span))
    pts.append(ctrl[-1].copy())
    return pts

def resample(pts, spacing):
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

SPINE = resample(sample_curve(CTRL), 0.5)
N = len(SPINE) - 1
X_AXIS = Vector((1, 0, 0))

def frame(tangent):
    t = tangent.normalized()
    d = X_AXIS.cross(t).normalized()      # dos
    side = t.cross(d).normalized()        # côté (+X)
    return t, d, side

RADIUS_KEYS = [(0.0, 0.6), (0.08, 0.72), (0.2, 0.92), (0.3, 0.98), (0.45, 0.92),
               (0.6, 0.75), (0.8, 0.45), (1.0, 0.2)]

def radius(s):
    for (s0, r0), (s1, r1) in zip(RADIUS_KEYS, RADIUS_KEYS[1:]):
        if s <= s1:
            return r0 + (r1 - r0) * (s - s0) / (s1 - s0)
    return RADIUS_KEYS[-1][1]

def frame_at(s):
    i = min(N - 1, max(0, int(s * N)))
    mid = (SPINE[i] + SPINE[i + 1]) / 2
    t, d, side = frame(SPINE[i + 1] - SPINE[i])
    return mid, t, d, side, radius(s)

# ----------------------------------------------------------
# 7. CORPS, VENTRE, CRÊTE, CRISTAUX, CRINIÈRE DU COU
# ----------------------------------------------------------
for i in range(N):
    p1, p2 = SPINE[i], SPINE[i + 1]
    L = (p2 - p1).length
    mid = (p1 + p2) / 2
    s = (i + 0.5) / N
    r = radius(s)
    t, d, side = frame(p2 - p1)
    R = Matrix((side, t, d)).transposed()
    parent = body_root if s < 0.62 else tail_root
    tag = "Body" if s < 0.62 else "Tail"

    # Segment principal
    box(f"{tag}_Seg_{i}", (2 * r, L * 1.25, 2 * r * 0.95), mid, R, M_GOLD, parent, bevel=0.06)

    # Plaques de ventre crème (segmentées)
    if s < 0.85:
        box(f"{tag}_Belly_{i}", (2 * r * 0.86, L * 0.85, 0.22), mid - d * (r * 0.95), R, M_CREAM, parent, bevel=0.03)
        # Bandes latérales claires (comme les plaques de flanc du concept)
        for sgn in (-1, 1):
            box(f"{tag}_Flank_{i}_{sgn}", (0.1, L * 0.9, r * 1.1), mid + side * sgn * r - d * r * 0.2,
                R, M_LGOLD, parent, bevel=0.02)

    # Écaille dorsale légèrement inclinée
    Rtilt = R @ Euler((math.radians(-8), 0, 0)).to_matrix()
    box(f"{tag}_Dorsal_{i}", (2 * r * 0.92, L * 0.95, 0.2), mid + d * (r * 0.95), Rtilt, M_DGOLD, parent, bevel=0.03)

    # Grappes de cristaux cyan sur le dos
    if 0.22 < s < 0.82 and i % 2 == 0:
        n_cr = 1 + (random.random() < 0.6) + (random.random() < 0.35)
        for c in range(n_cr):
            off = 0.0 if c == 0 else random.choice((-1, 1)) * random.uniform(0.25, 0.45) * r
            direction = d + t * 0.55 + side * (off * 0.8) + Vector([random.uniform(-0.1, 0.1) for _ in range(3)])
            scale = r * (1.0 if c == 0 else random.uniform(0.55, 0.75))
            crystal(f"{tag}_Crystal_{i}_{c}", 0.3 * scale, 0.7 * scale, 0.45 * scale,
                    mid + d * (r * 0.85) + side * off + t * random.uniform(-0.1, 0.1),
                    direction, parent=parent)

    # Petites nageoires dorsales sur la queue
    if s >= 0.82:
        shard(f"Tail_Fin_{i}", 0.35 * r + 0.1, 0.08, 0.5 + r * 0.6, mid + d * r * 0.9, d + t * 0.8,
              mat=M_LGOLD, parent=tail_root)

    # Crinière qui coule le long du cou
    if s < 0.2:
        fade = 1.0 - s / 0.2
        for k, amt in enumerate((-1.5, -0.5, 0.5, 1.5)):
            amt = amt * 0.35 + random.uniform(-0.1, 0.1)
            shard(f"Body_NeckMane_{i}_{k}", 0.6, 0.12, 1.0 + 0.9 * fade + random.random() * 0.4,
                  mid + d * r * 0.8 + side * amt * r * 0.5, d + t * 0.9 + side * amt,
                  mat=pick_mane_mat(), parent=body_root)
        for sgn in (-1, 1):
            shard(f"Body_NeckSide_{i}_{sgn}", 0.32, 0.1, 0.7 + 0.5 * fade,
                  mid + side * sgn * r * 0.85, side * sgn + t * 0.8 + d * 0.3,
                  mat=pick_mane_mat(), parent=body_root)

# Bout de queue : touffe + cristal
tip = SPINE[-1]
tt, td, tside = frame(SPINE[-1] - SPINE[-2])
box("Tail_TipCollar", (0.5, 0.4, 0.5), tip, Matrix((tside, tt, td)).transposed(), M_DGOLD, tail_root, bevel=0.03)
for k in range(7):
    a = k / 7 * 2 * math.pi
    spread = tside * math.cos(a) + td * math.sin(a)
    shard(f"Tail_Tuft_{k}", 0.35, 0.1, 1.0 + random.random() * 0.5, tip, tt + spread * 0.6,
          mat=random.choice([M_LGOLD, M_GOLD]), parent=tail_root)
crystal("Tail_TipCrystal", 0.18, 0.4, 0.35, tip + tt * 0.2, tt, parent=tail_root)

# ----------------------------------------------------------
# 8. PLASTRON AVEC GEMME + PETITES AILES D'ÉPAULE
# ----------------------------------------------------------
cmid, ct, cd, cside, cr = frame_at(0.24)
CR = Matrix((cside, ct, cd)).transposed()
box("Body_ChestPlate", (2 * cr * 1.05, 1.4, 0.25), cmid - cd * (cr + 0.05), CR, M_DGOLD, body_root, bevel=0.05)
box("Body_ChestInner", (2 * cr * 0.7, 1.0, 0.12), cmid - cd * (cr + 0.2), CR, M_GOLD, body_root, bevel=0.03)
crystal("Body_ChestGem", 0.3, 0.2, 0.28, cmid - cd * (cr + 0.2), -cd, parent=body_root, up=tuple(ct))
for sgn in (-1, 1):
    shard(f"Body_ChestFrame_{sgn}", 0.3, 0.1, 0.7, cmid - cd * (cr + 0.25) + cside * sgn * 0.35,
          cside * sgn * 0.6 - ct * 1.0, mat=M_LGOLD, parent=body_root)
    for k in range(3):
        shard(f"Body_Wing_{sgn}_{k}", 0.5 - k * 0.08, 0.08, 1.3 - k * 0.2,
              cmid + cside * sgn * (cr + 0.1) + cd * (0.35 - k * 0.15) - ct * (0.3 - k * 0.25),
              ct * 0.6 + cd * 0.8 + cside * sgn * 0.6, mat=M_WING, parent=body_root)

# ----------------------------------------------------------
# 9. PATTES AVEC BRACELETS ET GRIFFES
# ----------------------------------------------------------
def paw(name, center, sgn):
    box(f"{name}_Paw", (0.55, 0.55, 0.3), center, mat=M_GOLD, parent=legs_root, bevel=0.04)
    for k in (-1, 0, 1):
        base = center + Vector((k * 0.17, -0.22, 0))
        end = center + Vector((k * 0.24, -0.55, -0.2))
        link(f"{name}_Toe_{k}", base, end, 0.14, M_GOLD, legs_root)
        shard(f"{name}_Claw_{k}", 0.12, 0.12, 0.28, end, (k * 0.2, -1, -0.9), mat=M_CLAW, parent=legs_root)

def leg(name, s, upper, lower, th_up, th_low, side_push):
    mid, t, d, side, r = frame_at(s)
    for sgn in (-1, 1):
        n = f"{name}_{sgn}"
        root = mid + side * sgn * r * 0.85 - d * 0.15
        joint = root + Vector((sgn * side_push, 0, 0)) + Vector(upper)
        wrist = joint + Vector((sgn * 0.05, 0, 0)) + Vector(lower)
        box(f"{n}_Shoulder", (0.62, 0.62, 0.62), root, mat=M_GOLD, parent=legs_root, bevel=0.06)
        link(f"{n}_Upper", root, joint, th_up, M_GOLD, legs_root, up=(1, 0, 0), bevel=0.05)
        link(f"{n}_Lower", joint, wrist, th_low, M_GOLD, legs_root, up=(1, 0, 0), bevel=0.04)
        link(f"{n}_Cuff", joint.lerp(wrist, 0.6), wrist, th_low + 0.14, M_DGOLD, legs_root, up=(1, 0, 0), bevel=0.03)
        shard(f"{n}_ElbowSpike", 0.25, 0.08, 0.6, joint, (sgn * 0.4, 0.8, 0.2), mat=M_LGOLD, parent=legs_root)
        paw(n, wrist + Vector((0, -0.2, -0.12)), sgn)

leg("Legs_Front", 0.24, (0, -0.55, -0.75), (0, -0.75, -0.25), 0.48, 0.38, 0.35)
leg("Legs_Back",  0.55, (0, -0.7, -0.45),  (0, 0.35, -0.8),   0.6,  0.42, 0.30)

# ----------------------------------------------------------
# 10. PETITS CRISTAUX FLOTTANTS (optionnel)
# ----------------------------------------------------------
if ADD_FLOATING_FX:
    for k in range(14):
        p = Vector((random.uniform(-2.5, 2.5), random.uniform(-2.0, 8.0), random.uniform(1.5, 11.0)))
        dirv = Vector([random.uniform(-1, 1) for _ in range(3)])
        crystal(f"FX_Crystal_{k}", 0.08, 0.12, 0.12, p, dirv, parent=master)

# ----------------------------------------------------------
# 11. VUE
# ----------------------------------------------------------
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.overlay.show_relationship_lines = False

bpy.context.view_layer.update()
print(f"Adulte Mirage v3 généré : {len(coll.objects)} objets dans la collection '{COLL_NAME}'.")