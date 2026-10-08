# Formes de base v3 (d'apres references + cahier des charges) : outils partages par 01_bebe, 02_ado, 03_adulte.
# Surface gris perle, mate et lisse (les textures viendront a la fin). Pieces separees : cornes, griffes,
# plaques de crete, yeux, paupieres, ailes, plaques d'armure.
# Charge par chaque script avec : exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())
import bpy, bmesh, math
from mathutils import Vector as V, Matrix, Quaternion

def lin(c): return tuple(x ** 2.2 for x in c)
def lerp(a, b, t): return a + (b - a) * t
def sstep(a, b, x):
    t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def mat(name, c, rough=0.5, emit=0.0, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(c), 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(c), 1); b.inputs["Emission Strength"].default_value = emit
    return m

CLAY = mat("GrisPerle", (0.84, 0.84, 0.86), 0.65)           # corps, paupieres, plaques de crete
KERA = mat("Ivoire", (0.94, 0.91, 0.83), 0.35)              # cornes, griffes, pointes
MEMB = mat("Membrane", (0.76, 0.76, 0.79), 0.7)             # membrane des ailes
DARK = mat("Pupille", (0.02, 0.02, 0.03), 0.05, coat=1.0)
HL = mat("Reflet", (1, 1, 1), 0.1, emit=3.0)
PAD = mat("Coussinet", (0.93, 0.74, 0.77), 0.55)            # coussinets sous les pattes du bebe (piece a part)

def iris_glacier(name="IrisGlacier"):
    """globe oculaire : iris bleu glacier en degrade (clair au centre, profond au bord, anneau sombre)."""
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name); N = m.node_tree.nodes; L = m.node_tree.links; b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.04; b.inputs["Coat Weight"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sp.inputs[0])
    cb = N.new("ShaderNodeCombineXYZ"); L.new(sp.outputs["X"], cb.inputs["X"]); L.new(sp.outputs["Z"], cb.inputs["Y"])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'; L.new(cb.outputs[0], ln.inputs[0])
    back = N.new("ShaderNodeMath"); back.operation = 'GREATER_THAN'; L.new(sp.outputs["Y"], back.inputs[0]); back.inputs[1].default_value = 0.0
    r = N.new("ShaderNodeMath"); r.operation = 'MAXIMUM'; L.new(ln.outputs["Value"], r.inputs[0]); L.new(back.outputs[0], r.inputs[1])
    cr = N.new("ShaderNodeValToRGB"); L.new(r.outputs[0], cr.inputs["Fac"]); e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*lin((0.88, 0.99, 1.0)), 1)
    e[1].position = 0.97; e[1].color = (*lin((0.02, 0.05, 0.12)), 1)
    for pos, c in ((0.3, (0.45, 0.88, 1.0)), (0.62, (0.1, 0.5, 0.95)), (0.84, (0.03, 0.2, 0.55))):
        el = e.new(pos); el.color = (*lin(c), 1)
    L.new(cr.outputs["Color"], b.inputs["Base Color"]); L.new(cr.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.5
    return m

def scene_setup():
    """camera, eclairage de studio doux, sol. Ne touche pas aux dragons."""
    sc = bpy.context.scene
    for o in [o for o in bpy.data.objects if o.name in ("Cam", "Key", "Fill", "Rim", "Top", "Ground")]:
        bpy.data.objects.remove(o, do_unlink=True)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 70
    def light(name, loc, energy, size, color=(1, 1, 1), tgt=(6, 0, 1)):
        L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = color; L.size = size
        o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (V(tgt) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
    light("Key", (12, -12, 12), 3200, 12); light("Fill", (-6, -10, 5), 900, 12, (0.88, 0.92, 1))
    light("Rim", (6, 12, 8), 1500, 10); light("Top", (6, 0, 14), 800, 16)
    w = sc.world or bpy.data.worlds.new("W"); sc.world = w
    bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = (0.5, 0.52, 0.56, 1); bg.inputs[1].default_value = 0.6
    me = bpy.data.meshes.new("Ground"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60)
    bm.to_mesh(me); bm.free(); g = bpy.data.objects.new("Ground", me); sc.collection.objects.link(g)
    g.location.z = -0.12; g.data.materials.append(mat("Sol", (0.32, 0.33, 0.36), 0.9))
    r = sc.render; r.engine = 'BLENDER_EEVEE'; r.resolution_x = 1200; r.resolution_y = 750
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    return sc, cam

def shot(name, tgt, d, dist, only=None, hide=(), base="C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"):
    """rendu ; only = nom du stade a montrer seul ("Bebe", "Ado", "Adulte"), les autres sont masques le temps du rendu.
    hide = noms d'objets a masquer en plus (ex. sol et plateforme pour une vue de dessous)."""
    sc = bpy.context.scene; cam = sc.camera; hidden = []
    for n in hide:
        o = bpy.data.objects.get(n)
        if o and not o.hide_render: o.hide_render = True; hidden.append(o)
    if only:
        for st in ("Bebe", "Ado", "Adulte"):
            if st == only: continue
            c = bpy.data.collections.get(st); p = bpy.data.objects.get("Plateforme_" + st)
            for x in ([c] if c else []) + ([p] if p else []):
                if not x.hide_render: x.hide_render = True; hidden.append(x)
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
    for x in hidden: x.hide_render = False

def face_quat(n, tilt_deg, s, up=None):
    """axe -Y local = normale, Z local ~ vers le haut (up, par defaut vertical), puis inclinaison autour de la normale."""
    up = V((0, 0, 1)) if up is None else V(up); z = (up - n * up.dot(n)).normalized()
    y = -n; x = y.cross(z)
    q = Matrix((x, y, z)).transposed().to_quaternion()
    return q @ Matrix.Rotation(math.radians(tilt_deg * s), 4, 'Y').to_quaternion()

def frame_quat(n, t):
    """-Y local = normale n, Z local = tangente t (projetee)."""
    y = -V(n).normalized(); z = (V(t) - y * V(t).dot(y)).normalized(); x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_quaternion()

def _resample(poly, n):
    poly = [V(p) for p in poly]
    seg = [(poly[i + 1] - poly[i]).length for i in range(len(poly) - 1)]
    tot = sum(seg); out = []
    for k in range(n):
        d = tot * k / (n - 1); i = 0
        while i < len(seg) - 1 and d > seg[i]: d -= seg[i]; i += 1
        out.append(poly[i].lerp(poly[i + 1], min(1.0, d / seg[i] if seg[i] else 0)))
    return out
def _smooth_poly(poly, it=2):
    pts = [V(p) for p in poly]
    for _ in range(it):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]): new += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        new.append(pts[-1]); pts = new
    return pts

class Dragon:
    """Construit un dragon : metaballs -> corps lisse, puis pieces separees (coordonnees locales du corps).
    S = placement dans la scene (translation + echelle). head_frame() permet de tourner la tete.
    Construction en 2 passes : build_body() une 1re fois pour lancer les rayons (yeux, bouche), on ajoute ensuite
    les volumes qui en dependent (paupieres en peau, sillon de la bouche), puis build_body() reconstruit le corps.
    res = finesse des metaballs (plus petit = plus de details, plus de triangles)."""
    def __init__(self, coll_name, prefix, S, res=0.022):
        self.P = prefix; self.S = S; self.claws = []; self.hooks = []; self.pads = []; self.body = None
        self.HP = V((0, 0, 0)); self.HR = Matrix.Identity(3)
        for o in [o for o in bpy.data.objects if o.name.startswith(prefix)]: bpy.data.objects.remove(o, do_unlink=True)
        for m in [m for m in bpy.data.metaballs if m.name.startswith(prefix) and m.users == 0]: bpy.data.metaballs.remove(m)
        sc = bpy.context.scene
        self.coll = bpy.data.collections.get(coll_name) or bpy.data.collections.new(coll_name)
        if self.coll.name not in sc.collection.children: sc.collection.children.link(self.coll)
        self.mb = bpy.data.metaballs.new(prefix + "MB"); self.mb.resolution = res; self.mb.render_resolution = res
        self.mb.threshold = 0.6

    # ---- tete orientable ----
    def head_frame(self, pivot, yaw=0.0, pitch=0.0, roll=0.0):
        self.HP = V(pivot)
        self.HR = (Matrix.Rotation(math.radians(yaw), 3, 'Z') @ Matrix.Rotation(math.radians(pitch), 3, 'X')
                   @ Matrix.Rotation(math.radians(roll), 3, 'Y'))
    def hp(self, p): return self.HP + self.HR @ (V(p) - self.HP)
    def hd(self, d): return self.HR @ V(d)

    # ---- volumes ----
    def ell(self, co, r, size=(1, 1, 1), st=2.4, rot=None, neg=False):
        """volume ellipsoide ; neg=True creuse au lieu d'ajouter."""
        e = self.mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r * 1.74
        e.size_x, e.size_y, e.size_z = size; e.stiffness = st; e.use_negative = neg
        if rot is not None: e.rotation = rot
    def hell(self, co, r, size=(1, 1, 1), st=2.4, neg=False):
        """volume de la tete (suit la rotation de la tete)."""
        self.ell(self.hp(co), r, size, st, self.HR.to_quaternion(), neg)
    def chain(self, pts, n=5, f=1.0, st=2.0):
        """membre continu : points (x, y, z, rayon) interpoles."""
        for i in range(len(pts) - 1):
            A, B = pts[i], pts[i + 1]
            for k in range(n):
                t = k / n; self.ell(tuple(lerp(A[j], B[j], t) for j in range(3)), lerp(A[3], B[3], t) * f, (1, 1, 1), st)
        self.ell(pts[-1][:3], pts[-1][3] * f, (1, 1, 1), st)
    def foot(self, cx, cy, s, size=1.0, toes=4, spread=22, claw_len=0.06, claw_r=0.024):
        """patte en 'coussin' : large paume arrondie qui s'elargit a la base + 4 orteils courts et charnus.
        Les griffes (coniques, separees) sont creees par claws_build()."""
        c = V((cx, cy, 0.0)); z0 = 0.065 * size
        self.ell(c + V((0, -0.03 * size, z0)), 0.13 * size, (1.35, 1.15, 0.62), 2.8)
        for i in range(toes):
            a = math.radians(spread * (i - (toes - 1) / 2) * s); d = V((math.sin(a), -math.cos(a), 0))
            b = c + d * 0.1 * size + V((0, 0, z0 * 0.75))
            for k in range(4):
                t = k / 3; self.ell(b + d * 0.07 * size * t + V((0, 0, -0.01 * size * t)), (0.05 - 0.006 * t) * size, (1, 1, 0.85), 3.0)
            self.claws.append((b + d * 0.125 * size + V((0, 0, -0.008 * size)), d, size, claw_len, claw_r))
    def paw(self, cx, cy, s, size=1.0, toes=4, spread=30, claw_len=0.022, claw_r=0.014):
        """patte ronde de bebe (facon film d'animation) : paume en mitaine plus large que la jambe, 4 gros doigts ronds
        bien separes par des sillons, coussinets sous la paume et sous chaque doigt (pieces a part, creees par
        claws_build), griffes minuscules au bout des doigts. Le bas de la jambe doit arriver vers (cx, cy + 0.03*size, 0.2*size)
        avec un rayon plus petit que la paume."""
        c = V((cx, cy, 0.0)); u = V((0, 0, 1)); k = size
        self.ell(c + V((0, 0.03 * k, 0.07 * k)), 0.1 * k, (1.2, 1.1, 0.7), 2.6)            # paume
        dirs = []
        for i in range(toes):
            a = math.radians(spread * (i - (toes - 1) / 2) * s); d = V((math.sin(a), -math.cos(a), 0)); dirs.append(d)
            self.ell(c + d * 0.14 * k + u * 0.04 * k, 0.036 * k, (1.0, 1.25, 0.95), 3.2, d.to_track_quat('Y', 'Z'))  # doigt rond
            self.claws.append((c + d * 0.178 * k + u * 0.03 * k, d, k, claw_len, claw_r))
            self.pads.append((c + d * 0.13 * k, d, 0.023 * k, 0.028 * k))                       # coussinet du doigt
        for a, b in zip(dirs, dirs[1:]):                                                        # sillons entre les doigts
            dm = (a + b).normalized()
            self.ell(c + dm * 0.16 * k + u * 0.075 * k, 0.012 * k, (0.8, 2.6, 1.8), 2.6, dm.to_track_quat('Y', 'Z'), neg=True)
        self.pads.append((c + V((0, 0.025 * k, 0)), V((0, -1, 0)), 0.065 * k, 0.055 * k))       # coussinet de la paume

    def dragon_foot(self, cx, cy, s, size=1.0, splay=8, claw_len=0.12, claw_r=0.028, rear=True):
        """vraie patte de dragon (ado, adulte) : pied compact et osseux, 3 longs doigts articules vers l'avant
        (phalanges, jointures marquees, coussinets sous les doigts, doigt du milieu plus long) + 1 ergot a l'arriere.
        Griffes recourbees en crochet jusqu'au sol (creees par claws_build). Le bas de la jambe doit arriver
        vers (cx, cy + 0.03*size, 0.17*size)."""
        c = V((cx, cy, 0.0)); u = V((0, 0, 1)); k = size
        self.ell(c + V((0, 0.02 * k, 0.085 * k)), 0.062 * k, (1.15, 1.3, 0.95), 2.6)        # dessus du pied
        for a, ln in ((-33, 0.88), (0, 1.0), (33, 0.88)):
            ang = math.radians((a + splay) * s); d = V((math.sin(ang), -math.cos(ang), 0))
            P = [c + d * 0.045 * k + u * 0.075 * k, c + d * 0.15 * ln * k + u * 0.08 * k,
                 c + d * 0.245 * ln * k + u * 0.056 * k, c + d * 0.32 * ln * k + u * 0.038 * k]
            Rr = [0.04, 0.034, 0.029, 0.024]
            self.chain([(*p, r * k) for p, r in zip(P, Rr)], 3, 1.0, 3.0)
            for p, r in ((P[1], 0.037), (P[2], 0.031)):                                         # jointures
                self.ell(p + u * 0.01 * k, r * k, (0.95, 1.05, 0.9), 3.2)
            self.ell(c + d * 0.15 * ln * k + u * 0.03 * k, 0.03 * k, (1.0, 1.35, 0.75), 3.0)    # coussinets
            self.ell(c + d * 0.29 * ln * k + u * 0.022 * k, 0.023 * k, (1.0, 1.3, 0.75), 3.0)
            self.hooks.append((P[3] + d * 0.012 * k + u * 0.004 * k, d, claw_len * k * (0.85 + 0.15 * ln), claw_r * k))
        if rear:                                                                                # ergot (vers l'arriere, cote interieur)
            d = V((-s * 0.35, 1, 0)).normalized()
            P = [c + d * 0.03 * k + u * 0.11 * k, c + d * 0.09 * k + u * 0.085 * k, c + d * 0.13 * k + u * 0.065 * k]
            self.chain([(*P[0], 0.04 * k), (*P[1], 0.032 * k), (*P[2], 0.026 * k)], 3, 1.0, 2.6)
            self.hooks.append((P[2] + d * 0.01 * k, d, claw_len * k * 0.55, claw_r * k * 0.85))

    def build_body(self):
        """metaballs -> maillage. Rappelee apres ajout de volumes, elle remplace le corps precedent."""
        sc = bpy.context.scene
        if self.body is not None:
            me = self.body.data; bpy.data.objects.remove(self.body, do_unlink=True); bpy.data.meshes.remove(me)
        mo = bpy.data.objects.new(self.P + "MB", self.mb); sc.collection.objects.link(mo)
        for o in sc.objects: o.select_set(False)
        bpy.context.view_layer.objects.active = mo; mo.select_set(True); bpy.context.view_layer.update()
        bpy.ops.object.convert(target='MESH')
        b = bpy.context.view_layer.objects.active; b.name = self.P + "Body"
        for p in b.data.polygons: p.use_smooth = True
        b.data.materials.append(CLAY)
        for c in b.users_collection: c.objects.unlink(b)
        self.coll.objects.link(b); b.matrix_world = self.S; self.body = b
        bpy.context.view_layer.update(); return b

    def hit(self, origin, d, back=4.0):
        d = V(d).normalized(); h, l, n, _ = self.body.ray_cast(V(origin) + d * back, -d)
        return l, n
    def hhit(self, origin, d, back=4.0):
        """rayon dans le repere de la tete."""
        return self.hit(self.hp(origin), self.hd(d), back)

    # ---- pieces ----
    def link(self, o, local=None):
        for c in o.users_collection: c.objects.unlink(o)
        self.coll.objects.link(o); o.matrix_world = self.S @ (local if local is not None else Matrix()); return o
    def tube(self, name, pts, radii, mm, res=8, bev=4, smooth=True):
        cu = bpy.data.curves.new(self.P + name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = res
        cu.bevel_mode = 'ROUND'; cu.bevel_depth = 1; cu.bevel_resolution = bev; cu.use_fill_caps = True
        sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1); sp.use_smooth = smooth
        for bp, pp, r in zip(sp.bezier_points, pts, radii):
            bp.co = V(pp); bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r
        o = bpy.data.objects.new(self.P + name, cu); cu.materials.append(mm); bpy.context.scene.collection.objects.link(o)
        return self.link(o)
    def _mesh_obj(self, name, bm, mm, local, smooth=True):
        me = bpy.data.meshes.new(self.P + name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = smooth
        me.materials.append(mm); o = bpy.data.objects.new(self.P + name, me)
        bpy.context.scene.collection.objects.link(o); return self.link(o, local)
    def sphere(self, name, loc, scl, mm, q=None, seg=24):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1)
        R = q.to_matrix().to_4x4() if q is not None else Matrix()
        return self._mesh_obj(name, bm, mm, Matrix.Translation(loc) @ R @ Matrix.Diagonal((*scl, 1)))
    def lemon(self, name, loc, q, w, h, dep, mm, sharp=1.0, seg=24):
        """amande / plaque bombee (X = largeur, -Y = vers l'exterieur, Z = hauteur)."""
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1)
        for v in bm.verts: v.co.z *= max(0.0, 1 - v.co.x ** 2) ** (0.5 * sharp)
        return self._mesh_obj(name, bm, mm, Matrix.Translation(loc) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((w, dep, h, 1)))
    def cone(self, name, base, tip, r, mm, flat=1.0, flatx=1.0, smooth=True):
        """pointe : cone de base vers tip. flat < 1 l'aplatit a l'horizontale, flatx < 1 sur le cote."""
        base = V(base); tip = V(tip); d = tip - base
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=1, radius2=0, depth=1)
        for v in bm.verts: v.co.z += 0.5
        q = d.to_track_quat('Z', 'Y')
        M = Matrix.Translation(base) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((r * flatx, r * flat, d.length, 1))
        return self._mesh_obj(name, bm, mm, M, smooth)
    def claws_build(self, mm=KERA):
        """griffes separees de la patte : coniques (pattes du bebe), en crochet (dragon_foot) ; + coussinets (paw)."""
        for i, (p, d, rw, rl) in enumerate(self.pads):
            self.sphere(f"Pad_{i}", p + V((0, 0, rw * 0.15)), (rw, rl, rw * 0.35), PAD, d.to_track_quat('-Y', 'Z'), 16)
        for i, (tip, d, sz, L, r) in enumerate(self.claws):
            self.cone(f"Claw_{i}", tip - d * 0.02 * sz, tip + d * L * sz + V((0, 0, -L * 0.45 * sz)), r * sz, mm)
        for i, (b, d, L, r) in enumerate(self.hooks):
            p2 = b + d * 0.92 * L; p2.z = 0.004
            p1 = b.lerp(p2, 0.5) + d * 0.08 * L + V((0, 0, 0.22 * L + 0.25 * (b.z - p2.z)))
            self.tube(f"Claw_h{i}", [b - d * 0.15 * L, p1, p2], [r, r * 0.68, r * 0.06], mm, res=6, bev=3)
    def horn(self, name, pts, radii, mm=KERA, spikes=0, spike_len=0.08, spike_r=0.03):
        """corne a aretes definies (section a facettes) + pointes secondaires le long de l'arete."""
        self.tube(name, pts, radii, mm, res=14, bev=1, smooth=False)
        if spikes:
            path = _resample(_smooth_poly(pts, 3), 40)
            for k in range(spikes):
                i = int(8 + k * 24 / max(1, spikes - 1)) if spikes > 1 else 20
                p, t = path[i], (path[i + 1] - path[i - 1]).normalized()
                up = (V((0, 0, 1)) - t * t.dot(V((0, 0, 1)))).normalized()
                rr = lerp(radii[0], radii[-1], i / 40)
                self.cone(f"{name}_pointe{k}", p + up * rr * 0.4, p + up * (rr + spike_len) + t * spike_len * 0.6, spike_r, mm, smooth=False)
    def spade(self, name, base, d, L, W, thick, mm=KERA):
        """pique en losange au bout de la queue (plat, aretes vives)."""
        d = V(d).normalized(); side = d.cross(V((0, 0, 1))).normalized(); up = side.cross(d)
        P = [V((0, 0, 0)), side * W / 2 + d * L * 0.38, d * L, -side * W / 2 + d * L * 0.38]
        bm = bmesh.new(); top = [bm.verts.new(V(base) + p + up * thick / 2) for p in P]; bot = [bm.verts.new(V(base) + p - up * thick / 2) for p in P]
        bm.faces.new(top); bm.faces.new(list(reversed(bot)))
        for i in range(4): bm.faces.new((top[i], bot[i], bot[(i + 1) % 4], top[(i + 1) % 4]))
        # aretes vives : le bord exterieur est ramene a une lame
        for i in (1, 2, 3):
            mid = (top[i].co + bot[i].co) / 2; top[i].co = mid + up * thick * 0.08; bot[i].co = mid - up * thick * 0.08
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._mesh_obj(name, bm, mm, Matrix(), smooth=False)
    def crest(self, name, path, heights, length, thick, lean=0.35, mm=CLAY):
        """crete de plaques triangulaires acerees (chaque plaque est un maillage separe).
        path : points (x, y, tete?) ; on lance un rayon vertical pour se poser sur le dos."""
        hits = []
        for x, y, in_head in path:
            if in_head: l, n = self.hhit((x, y, 0.0), (0, 0, 1), back=8.0)
            else: l, n = self.hit((x, y, 0.0), (0, 0, 1), back=8.0)
            hits.append((l, n))
        for i, ((l, n), H) in enumerate(zip(hits, heights)):
            a = hits[max(0, i - 1)][0]; b = hits[min(len(hits) - 1, i + 1)][0]; t = (b - a).normalized()
            z = n.normalized(); yv = (t - z * t.dot(z)).normalized(); xv = yv.cross(z)
            Lh = length * (0.6 + 0.4 * H / max(heights)) / 2; th = thick / 2; sink = 0.04 * max(H, 0.1)
            bm = bmesh.new()
            bf1 = bm.verts.new(l - yv * Lh + xv * th - z * sink); bf2 = bm.verts.new(l - yv * Lh - xv * th - z * sink)
            bb1 = bm.verts.new(l + yv * Lh + xv * th - z * sink); bb2 = bm.verts.new(l + yv * Lh - xv * th - z * sink)
            tip = bm.verts.new(l + yv * Lh * (2 * lean) + z * H)
            for f in ((bf1, bb1, tip), (bb2, bf2, tip), (bf2, bf1, tip), (bb1, bb2, tip), (bf1, bf2, bb2, bb1)): bm.faces.new(f)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            self._mesh_obj(f"{name}_{i:02d}", bm, mm, Matrix(), smooth=False)
    def plate(self, name, l, n, t, w, h, dep, mm=CLAY):
        """plaque d'armure osseuse lisse, posee sur la surface (normale n, allongee selon t)."""
        q = frame_quat(n, t) @ Matrix.Rotation(math.radians(90), 4, 'Y').to_quaternion()   # pointes dans le sens de t
        return self.lemon(name, l - n * dep * 0.3, q, h, w, dep, mm, 1.4)                  # feuille effilee : longueur h, largeur w

    # ---- yeux (2 passes : eye_at + eye_brow avant la 2e construction du corps, eye_build + eye_shell_lids apres) ----
    def eye_at(self, s, l, n, nf, R, sink, gaze, spread=0.0):
        """position d'un oeil : centre du globe enfonce de sink*R sous la peau, repere du visage (nf), regard.
        gaze = point vise, LE MEME pour les deux yeux : ils regardent ensemble au meme endroit (pas de strabisme).
        spread = petit ecart symetrique vers l'exterieur (yeux poses sur les cotes du crane, pupilles restant visibles)."""
        c = l - n * R * sink
        g = (V(gaze) - c).normalized() + self.hd(V((s * spread, 0, 0)))
        up = self.hd(V((0, 0, 1)))                       # le "haut" de la tete : paupieres et pupilles suivent son inclinaison
        return dict(s=s, c=c, R=R, qf=face_quat(nf, 0, s, up), g=g.normalized(), up=up)

    def eye_brow(self, E, h=0.95, fwd=0.35, size=1.0, tilt=0.0, w=1.5):
        """arcade (volume de la tete) posee au-dessus de l'oeil, dans le repere du visage : elle recouvre le haut de la
        paupiere -> seul le bord de la paupiere reste visible (pas de dome). h / fwd = hauteur / avancee (fractions de R),
        tilt en degres (+ = bout exterieur releve, - = bout exterieur abaisse)."""
        R, c, s = E["R"], E["c"], E["s"]
        q = E["qf"] @ Quaternion((0, 1, 0), math.radians(-tilt * s))
        self.ell(c + q @ V((0, -fwd * R, h * R)), R * size, (w, 0.62, 0.42), 3.0, q)

    def eye_shell_lids(self, E, up=(0.56, 0), lo=(0.6, 0), thick=0.11):
        """paupieres en coque (bebe, ado) : calottes autour du globe, epaissies au bord arrondi, orientees selon le visage
        (elles ne suivent pas le regard). up / lo = (ouverture 0..1, inclinaison en degres)."""
        s, c, R = E["s"], E["c"], E["R"]; Mf = E["qf"].to_matrix()
        for tag, (op, tilt), sg in (("Haut", up, 1), ("Bas", lo, -1)):
            nrm = Matrix.Rotation(math.radians(tilt * s), 3, 'Y') @ V((0, 0, sg))
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.dot(nrm) < op], context='VERTS')
            lid = self._mesh_obj(f"EyeLid{tag}_{s}", bm, CLAY, Matrix.Translation(c) @ Mf.to_4x4() @ Matrix.Scale(R * 1.04, 4))
            so = lid.modifiers.new("epaisseur", 'SOLIDIFY'); so.thickness = thick; so.offset = 1.0; so.use_even_offset = True
            sb = lid.modifiers.new("arrondi", 'SUBSURF'); sb.levels = 1; sb.render_levels = 1

    def eye_build(self, E, iris, hl=True, pupil=(0.12, 0.62), hl_size=0.12):
        """globe (iris bleu glacier) + pupille fendue verticale tournes vers le point vise ;
        reflet du meme cote sur les deux yeux (lumiere commune).
        pupil = (demi-largeur, demi-hauteur) de la pupille en radians sur le globe (large = pupille dilatee, mignon)."""
        s, c, R = E["s"], E["c"], E["R"]
        qg = face_quat(E["g"], 0, s, E["up"]); Mg = qg.to_matrix()
        self.sphere(f"Eye_{s}", c, (R, R, R), iris, qg, 32)
        # pupille fendue : amande dessinee directement sur la surface du globe
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1)
        for v in bm.verts:
            x, y, z = v.co; z *= max(0.0, 1 - x * x) ** 0.5
            ax, az = z * pupil[0], x * pupil[1]
            v.co = V((math.sin(ax) * math.cos(az), -math.cos(ax) * math.cos(az), math.sin(az))) * (1.012 + y * 0.004)
        self._mesh_obj(f"EyePupil_{s}", bm, DARK, Matrix.Translation(c) @ Mg.to_4x4() @ Matrix.Scale(R, 4))
        if hl:
            dl = (self.hd(V((-0.25, -1.0, 0.0))) + V((0, 0, 0.55))).normalized()
            dl = (dl + E["g"] * 0.6).normalized()
            self.sphere(f"EyeHL_{s}", c + dl * R * 1.0, (R * hl_size,) * 3, HL, None, 12)

    # ---- bouche (2 passes : mouth_at + groove avant la 2e construction, mouth_build apres) ----
    def mouth_at(self, half, yc, n=31):
        """trace de la bouche, d'un coin a l'autre en passant par l'avant du museau.
        half = points (x >= 0, y, z) du milieu de l'avant jusqu'au coin droit (repere de la tete) ; on les lisse,
        on les symetrise, puis chaque point est pose sur la peau par un rayon horizontal dirige vers l'axe du museau
        (vers (0, yc) a l'avant du museau, vers x = 0 sur les cotes). Renvoie [(point, normale)]."""
        right = _resample(_smooth_poly(half, 3), (n + 1) // 2)
        plan = [V((-p.x, p.y, p.z)) for p in reversed(right[1:])] + right
        return self._surf(plan, yc), plan
    def _surf(self, plan, yc):
        out = []
        for p in plan:
            d = V((p.x, p.y - yc, 0)) if p.y < yc else V((1 if p.x >= 0 else -1, 0, 0))
            if d.length < 1e-6: d = V((0, -1, 0))
            l, nn = self.hhit(V((0, p.y, p.z)) if p.y >= yc else V((0, yc, p.z)), d.normalized(), 3.0)
            out.append((l, nn))
        return out
    def groove(self, pts, r, depth=0.35, st=2.6, step=0.5):
        """sillon creuse dans la peau le long des points (volumes negatifs) -> vraie fente de bouche avec ombre."""
        for (a, na), (b, nb) in zip(pts, pts[1:]):
            k = max(1, int((b - a).length / (r * step)))
            for i in range(k):
                t = i / k; p = a.lerp(b, t); nn = na.lerp(nb, t).normalized()
                self.ell(p + nn * r * (1 - depth), r, (1, 1, 1), st, neg=True)
    def mouth_build(self, name, plan, yc, rad, mm=DARK):
        """ligne sombre posee au fond du sillon (apres la 2e construction), plus fine aux coins."""
        pts = self._surf(plan, yc); N = len(pts)
        radii = [rad * (0.35 + 0.65 * math.sin(math.pi * (i + 0.5) / N) ** 0.6) for i in range(N)]
        self.tube(name, [l - nn * rad * 0.6 for l, nn in pts], radii, mm, res=3, bev=2)
        return pts

    def wing(self, s, root, K, F, E, W, rear, raise_deg=20, sweep_deg=0, sag=0.07, scallop=0.22, bone_r=0.03, mm=MEMB, bone=CLAY):
        """aile de chauve-souris : membrane tendue festonnee + os (phalanges). root en coordonnees locales."""
        R = (Matrix.Rotation(math.radians(sweep_deg * s), 3, 'Z') @ Matrix.Rotation(math.radians(-raise_deg * s), 3, 'Y'))
        def W2L(p): return root + R @ (V((s * p.x, p.y, p.z)) * K)
        SAG = V((0, 0.25, -1)).normalized(); nt, nv = 16, 9; bm = bmesh.new()
        def panel(A, Bc, sc_, sg):
            A = _resample(_smooth_poly(A), nt); Bc = _resample(_smooth_poly(Bc), nt); grid = []
            for i in range(nt):
                t = i / (nt - 1); row = []
                for j in range(nv):
                    v = j / (nv - 1); p = A[i].lerp(Bc[i], v); w = math.sin(math.pi * v)
                    p = p + SAG * (sg * w * math.sin(math.pi * t) ** 0.7); p = p.lerp(W, sc_ * w * t ** 3)
                    row.append(bm.verts.new(W2L(p)))
                grid.append(row)
            for i in range(nt - 1):
                for j in range(nv - 1): bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
        for a, b in zip(F, F[1:]): panel(a, b, scallop, sag)
        panel([W, E, V((0, 0, 0))], F[-1] + [rear], 0.0, sag * 0.8)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.004); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = self._mesh_obj(f"Wing_{s}", bm, mm, Matrix())
        m1 = o.modifiers.new("sol", 'SOLIDIFY'); m1.thickness = 0.012; m1.offset = 0
        m2 = o.modifiers.new("sub", 'SUBSURF'); m2.levels = 1; m2.render_levels = 2
        self.tube(f"WingBone_arm_{s}", [W2L(V((0, 0, 0))), W2L(E), W2L(W)], [bone_r * 1.6 * K, bone_r * 1.3 * K, bone_r * 1.1 * K], bone)
        for k, f in enumerate(F):
            self.tube(f"WingBone_f{k}_{s}", [W2L(p) for p in f], [bone_r * 0.8 * K, bone_r * 0.55 * K, 0.004], bone)
        dirw = (W2L(W) - W2L(E)).normalized()
        self.cone(f"WingThumb_{s}", W2L(W), W2L(W) + dirw * 0.07 * K + V((0, -0.03 * K, 0.03 * K)), 0.025 * K, KERA)

def platform(name, x, y, radius):
    """plateforme ronde neutre (dessus a z = 0)."""
    o = bpy.data.objects.get(name)
    if o: bpy.data.objects.remove(o, do_unlink=True)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=72, radius1=radius, radius2=radius, depth=0.12)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = (x, y, -0.06)
    me.materials.append(mat("Plateforme", (0.9, 0.9, 0.92), 0.6)); return o
