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

def shot(name, tgt, d, dist, only=None, base="C:\\Users\\user\\OneDrive\\Documents\\photo dragon\\wip\\"):
    """rendu ; only = nom du stade a montrer seul ("Bebe", "Ado", "Adulte"), les autres sont masques le temps du rendu."""
    sc = bpy.context.scene; cam = sc.camera; hidden = []
    if only:
        for st in ("Bebe", "Ado", "Adulte"):
            if st == only: continue
            c = bpy.data.collections.get(st); p = bpy.data.objects.get("Plateforme_" + st)
            for x in ([c] if c else []) + ([p] if p else []):
                if not x.hide_render: x.hide_render = True; hidden.append(x)
    d = V(d).normalized(); cam.location = V(tgt) + d * dist; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = base + name + ".png"; bpy.ops.render.render(write_still=True)
    for x in hidden: x.hide_render = False

def face_quat(n, tilt_deg, s):
    """axe -Y local = normale, Z local ~ vers le haut, puis inclinaison autour de la normale."""
    up = V((0, 0, 1)); z = (up - n * up.dot(n)).normalized()
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
    S = placement dans la scene (translation + echelle). head_frame() permet de tourner la tete."""
    def __init__(self, coll_name, prefix, S):
        self.P = prefix; self.S = S; self.claws = []
        self.HP = V((0, 0, 0)); self.HR = Matrix.Identity(3)
        for o in [o for o in bpy.data.objects if o.name.startswith(prefix)]: bpy.data.objects.remove(o, do_unlink=True)
        sc = bpy.context.scene
        self.coll = bpy.data.collections.get(coll_name) or bpy.data.collections.new(coll_name)
        if self.coll.name not in sc.collection.children: sc.collection.children.link(self.coll)
        self.mb = bpy.data.metaballs.new(prefix + "MB"); self.mb.resolution = 0.022; self.mb.render_resolution = 0.022
        self.mb.threshold = 0.6

    # ---- tete orientable ----
    def head_frame(self, pivot, yaw=0.0, pitch=0.0, roll=0.0):
        self.HP = V(pivot)
        self.HR = (Matrix.Rotation(math.radians(yaw), 3, 'Z') @ Matrix.Rotation(math.radians(pitch), 3, 'X')
                   @ Matrix.Rotation(math.radians(roll), 3, 'Y'))
    def hp(self, p): return self.HP + self.HR @ (V(p) - self.HP)
    def hd(self, d): return self.HR @ V(d)

    # ---- volumes ----
    def ell(self, co, r, size=(1, 1, 1), st=2.4, rot=None):
        e = self.mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r * 1.74
        e.size_x, e.size_y, e.size_z = size; e.stiffness = st
        if rot is not None: e.rotation = rot
    def hell(self, co, r, size=(1, 1, 1), st=2.4):
        """volume de la tete (suit la rotation de la tete)."""
        self.ell(self.hp(co), r, size, st, self.HR.to_quaternion())
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

    def build_body(self):
        sc = bpy.context.scene
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
        """griffes coniques acerees, separees de la patte."""
        for i, (tip, d, sz, L, r) in enumerate(self.claws):
            self.cone(f"Claw_{i}", tip - d * 0.02 * sz, tip + d * L * sz + V((0, 0, -L * 0.45 * sz)), r * sz, mm)
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

    def eye(self, s, l, n, nf, R, iris, lid_up=(0.4, 0), lid_lo=(0.6, 0), sink=0.45, rim=0.0, lid_thick=0.14, hl=True):
        """oeil : globe (sphere) enfonce dans l'orbite, pupille fendue verticale posee sur le globe,
        paupieres superieure et inferieure saillantes et arrondies (calottes epaissies au bord adouci ;
        rim > 0 ajoute en plus un bourrelet le long du bord).
        lid_up / lid_lo = (ouverture 0..1, inclinaison en degres) ; l'inclinaison donne l'expression."""
        q = face_quat(nf, 0, s); c = l - n * R * sink; Mq = q.to_matrix()
        self.sphere(f"Eye_{s}", c, (R, R, R), iris, q, 32)
        # pupille fendue : amande dessinee directement sur la surface du globe
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1)
        for v in bm.verts:
            x, y, z = v.co; z *= max(0.0, 1 - x * x) ** 0.5
            ax, az = z * 0.12, x * 0.62
            v.co = V((math.sin(ax) * math.cos(az), -math.cos(ax) * math.cos(az), math.sin(az))) * (1.012 + y * 0.004)
        self._mesh_obj(f"EyePupil_{s}", bm, DARK, Matrix.Translation(c) @ Mq.to_4x4() @ Matrix.Scale(R, 4))
        if hl:
            dl = Mq @ V((-0.3, -0.85, 0.42)).normalized()
            self.sphere(f"EyeHL_{s}", c + dl * R * 1.0, (R * 0.12, R * 0.12, R * 0.12), HL, None, 12)
        # paupieres
        for tag, (op, tilt), up in (("Haut", lid_up, 1), ("Bas", lid_lo, -1)):
            nrm = Matrix.Rotation(math.radians(tilt * s), 3, 'Y') @ V((0, 0, up))
            Rl = 1.04; bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.dot(nrm) < op], context='VERTS')
            M = Matrix.Translation(c) @ Mq.to_4x4() @ Matrix.Scale(R * Rl, 4)
            lid = self._mesh_obj(f"EyeLid{tag}_{s}", bm, CLAY, M)
            if lid_thick > 0:                                    # epaisseur + bord arrondi
                so = lid.modifiers.new("epaisseur", 'SOLIDIFY'); so.thickness = lid_thick; so.offset = 1.0; so.use_even_offset = True
                sb = lid.modifiers.new("arrondi", 'SUBSURF'); sb.levels = 1; sb.render_levels = 1
            e1 = nrm.cross(V((0, 1, 0))).normalized(); e2 = nrm.cross(e1); rad = math.sqrt(max(0.0, 1 - op * op))
            ring = [nrm * op + (e1 * math.cos(a) + e2 * math.sin(a)) * rad for a in [k * 2 * math.pi / 48 for k in range(48)]]
            front = [p.y < -0.35 for p in ring]
            if rim <= 0 or all(front) or not any(front): continue
            k0 = next(i for i in range(48) if front[i] and not front[i - 1])
            arc = []
            for k in range(48):
                p = ring[(k0 + k) % 48]
                if p.y >= -0.35: break
                arc.append(c + Mq @ (p * R * Rl))
            if len(arc) >= 3:
                rr = [R * rim * (0.4 if i in (0, len(arc) - 1) else 1.0) for i in range(len(arc))]
                self.tube(f"EyeLid{tag}Bord_{s}", arc, rr, CLAY, res=4, bev=3)

    def mouth(self, name, ys, zs, radii, mm=DARK):
        """ligne de bouche : points poses sur le cote du museau (rayons depuis le cote, dans le repere de la tete)."""
        out = {}
        for s in (-1, 1):
            pts = []
            for y, z in zip(ys, zs):
                o = self.hp((s * 2.0, y, z)); d = self.hd((-s, 0, 0))
                h_, l, n, _ = self.body.ray_cast(o, d)
                if h_: pts.append((l - n * 0.006, n))
            if len(pts) >= 2: self.tube(f"{name}_{s}", [p for p, _ in pts], radii[:len(pts)], mm)
            out[s] = pts
        return out

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
