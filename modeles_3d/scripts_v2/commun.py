# Code partage par les scripts v2 (style Roblox) : palette, materiaux, constructeur de noeuds, flamme du front.
# Charge par chaque script avec : exec(open(os.path.join(DIR, "commun.py"), encoding="utf-8").read())
import bpy, math
from mathutils import Vector as V, Matrix

def lin(c): return tuple(x ** 2.2 for x in c)
def rgba(c): return (*lin(c), 1.0)
def sstep(a, b, x):
    t = max(0, min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t)

# ---------------- palette du dragon classique (sRGB), commune aux 3 stades ----------------
PAL = dict(RED=(0.92, 0.17, 0.12), RED_DARK=(0.66, 0.07, 0.07), BELLY=(1.0, 0.85, 0.55), BELLY_DARK=(0.9, 0.66, 0.38),
           FLAME=(1.0, 0.76, 0.12), HORN=(1.0, 0.94, 0.8), SPIKE=(1.0, 0.56, 0.1), WING=(1.0, 0.5, 0.16),
           IRIS=(1.0, 0.64, 0.08), DARK=(0.07, 0.03, 0.04))

def mat(name, c, rough=0.45, emit=0.0, coat=0.15):
    """materiau uni (couleur sRGB). Recupere le materiau s'il existe deja."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*lin(c), 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.2
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(c), 1); b.inputs["Emission Strength"].default_value = emit
    return m

def new_mat(name, rough=0.45, coat=0.15):
    """materiau vide (recree a chaque lancement) pour y brancher des noeuds."""
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    return mat(name, (1, 1, 1), rough, coat=coat)

class Nodes:
    """petit constructeur d'expressions de noeuds de shader. Les arguments sont des nombres, des tuples ou des sorties de noeuds."""
    def __init__(self, m): self.N = m.node_tree.nodes; self.L = m.node_tree.links
    def _in(self, sock, val):
        if isinstance(val, (int, float, tuple)): sock.default_value = val
        else: self.L.new(val, sock)
    def m(self, op, a, b=0.0, c=None, clamp=False):
        n = self.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        self._in(n.inputs[0], a); self._in(n.inputs[1], b)
        if c is not None: self._in(n.inputs[2], c)
        return n.outputs[0]
    def v(self, op, a, b=None, scale=None):
        n = self.N.new("ShaderNodeVectorMath"); n.operation = op; self._in(n.inputs[0], a)
        if b is not None: self._in(n.inputs[1], b)
        if scale is not None: self._in(n.inputs["Scale"], scale)
        return n.outputs["Value"] if op in ('DOT_PRODUCT', 'DISTANCE', 'LENGTH') else n.outputs["Vector"]
    def sep(self, vec):
        n = self.N.new("ShaderNodeSeparateXYZ"); self._in(n.inputs[0], vec); return n.outputs
    def comb(self, x, y, z=0.0):
        n = self.N.new("ShaderNodeCombineXYZ")
        for i, val in enumerate((x, y, z)): self._in(n.inputs[i], val)
        return n.outputs[0]
    def sstep(self, e0, e1, x):
        n = self.N.new("ShaderNodeMapRange"); n.interpolation_type = 'SMOOTHSTEP'; n.clamp = True
        self._in(n.inputs["Value"], x); self._in(n.inputs["From Min"], e0); self._in(n.inputs["From Max"], e1)
        return n.outputs["Result"]
    def inv(self, x): return self.m('SUBTRACT', 1.0, x)
    def mul(self, *xs):
        out = xs[0]
        for x in xs[1:]: out = self.m('MULTIPLY', out, x)
        return out
    def mix(self, fac, a, b):
        n = self.N.new("ShaderNodeMix"); n.data_type = 'RGBA'; self._in(n.inputs["Factor"], fac)
        self._in(n.inputs["A"], a); self._in(n.inputs["B"], b); return n.outputs["Result"]

def flamme(X, pos, HC, FLAMES, rayon, z_min):
    """Facteur 0..1 de la flamme du front (bords nets).
    Dessinee en (longitude, latitude) autour du centre de la tete HC : (0, 0) = face, latitude vers le haut.
    FLAMES : liste de langues (base a, pointe b, rayon max), en radians.
    rayon : distance max au centre de la tete ; z_min : hauteur sous laquelle on ne dessine pas."""
    dx, dy, dz = X.sep(X.v('NORMALIZE', X.v('SUBTRACT', pos, tuple(HC))))[:3]
    q = X.comb(X.m('ARCTAN2', dx, X.m('MULTIPLY', dy, -1.0)), X.m('ARCSINE', dz))
    fl = None
    for a, b, rmax in FLAMES:
        A = V((*a, 0)); AB = V((*b, 0)) - A
        t = X.m('MULTIPLY', X.v('DOT_PRODUCT', X.v('SUBTRACT', q, tuple(A)), tuple(AB)), 1.0 / AB.length_squared, clamp=True)
        d = X.v('DISTANCE', q, X.v('ADD', tuple(A), X.v('SCALE', tuple(AB), scale=t)))
        f = X.m('SUBTRACT', X.m('MULTIPLY', X.m('POWER', X.inv(t), 0.8), rmax), d)
        fl = f if fl is None else X.m('MAXIMUM', fl, f)
    pz = X.sep(pos)[2]
    zone = X.mul(X.sstep(z_min, z_min + 0.1, pz), X.inv(X.sstep(rayon - 0.05, rayon + 0.05, X.v('DISTANCE', pos, tuple(HC)))))
    return X.mul(X.sstep(-0.006, 0.006, fl), zone)
