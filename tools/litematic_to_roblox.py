"""Litematic -> boîtes fusionnées (greedy meshing) pour Roblox.

Grille à demi-blocs (chaque bloc Minecraft = 2x2x2 sous-cellules) pour garder
les dalles et les escaliers fidèles. Sortie : un ModuleScript Luau.

Usage : python litematic_to_roblox.py <fichier.litematic> <sortie.luau>
Dépendances : pip install nbtlib numpy
"""
import sys, math, os
import numpy as np
import nbtlib

src, out = sys.argv[1], sys.argv[2]
reg = list(nbtlib.load(src)["Regions"].values())[0]
sx, sy, sz = [abs(int(reg["Size"][k])) for k in "xyz"]
pal = []
for p in reg["BlockStatePalette"]:
    pal.append((str(p["Name"]).split(":")[1], {str(k): str(v) for k, v in p.get("Properties", {}).items()}))
bits = max(2, math.ceil(math.log2(len(pal))))
Lp = [int(v) & 0xFFFFFFFFFFFFFFFF for v in reg["BlockStates"]]
mask = (1 << bits) - 1

n = sx * sy * sz
idx = np.zeros(n, dtype=np.int32)
for i in range(n):
    s = i * bits; li = s >> 6; o = s & 63
    v = Lp[li] >> o
    if o + bits > 64:
        v |= Lp[li + 1] << (64 - o)
    idx[i] = v & mask
grid = idx.reshape(sy, sz, sx)  # [y][z][x]
AIR = {i for i, (nm, _) in enumerate(pal) if nm.endswith("air")}

# centre : milieu du plancher principal
FLOOR_Y = 78
fl = np.argwhere(~np.isin(grid[FLOOR_Y], list(AIR)))
cz = (fl[:, 0].min() + fl[:, 0].max()) / 2
cx = (fl[:, 1].min() + fl[:, 1].max()) / 2
filled = ~np.isin(grid, list(AIR))
y0 = int(np.argwhere(filled)[:, 0].min())

SOLID = {
    "deepslate_bricks": "deepslate",
    "deepslate_brick_slab": "deepslate",
    "nether_brick_stairs": "netherbrick",
    "tinted_glass": "tinted_glass",
    "magma_block": "magma",
    "glowstone": "glowstone",
    "barrier": "barrier",
    "black_stained_glass": "black_glass",
    "glass": "glass",
    "redstone_block": "redstone",
}
FACE = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
LEFT = {"north": "west", "west": "south", "south": "east", "east": "north"}
RIGHT = {v: k for k, v in LEFT.items()}

def side(f):
    fx, fz = FACE[f]
    return {(dx, dz) for dx in (0, 1) for dz in (0, 1)
            if (fx == 1 and dx == 1) or (fx == -1 and dx == 0) or (fz == 1 and dz == 1) or (fz == -1 and dz == 0)}

def quarter_cells(facing, shape):
    back = side(facing)
    if shape == "straight":
        return back
    lr = LEFT[facing] if shape.endswith("left") else RIGHT[facing]
    return (back & side(lr)) if shape.startswith("outer") else (back | side(lr))

kinds = sorted(set(SOLID.values()))
H = {k: np.zeros((sy * 2, sz * 2, sx * 2), dtype=bool) for k in kinds}
small = []

for (y, z, x) in np.argwhere(filled):
    name, props = pal[grid[y, z, x]]
    if name in SOLID:
        g = H[SOLID[name]]
        Y, Z, X = 2 * y, 2 * z, 2 * x
        if name == "deepslate_brick_slab":
            t = props.get("type", "bottom")
            if t == "double":
                g[Y:Y + 2, Z:Z + 2, X:X + 2] = True
            elif t == "top":
                g[Y + 1, Z:Z + 2, X:X + 2] = True
            else:
                g[Y, Z:Z + 2, X:X + 2] = True
        elif name == "nether_brick_stairs":
            top = props.get("half") == "top"
            base_y, step_y = (Y + 1, Y) if top else (Y, Y + 1)
            g[base_y, Z:Z + 2, X:X + 2] = True
            for dx, dz in quarter_cells(props.get("facing", "north"), props.get("shape", "straight")):
                g[step_y, Z + dz, X + dx] = True
        else:
            g[Y:Y + 2, Z:Z + 2, X:X + 2] = True
    else:
        small.append((name, int(x), int(y), int(z), props))

def greedy(g):
    vis = np.zeros_like(g)
    boxes = []
    Ymax, Zmax, Xmax = g.shape
    for (y, z, x) in np.argwhere(g):
        if vis[y, z, x]:
            continue
        w = 1
        while x + w < Xmax and g[y, z, x + w] and not vis[y, z, x + w]:
            w += 1
        d = 1
        while z + d < Zmax and g[y, z + d, x:x + w].all() and not vis[y, z + d, x:x + w].any():
            d += 1
        h = 1
        while y + h < Ymax and g[y + h, z:z + d, x:x + w].all() and not vis[y + h, z:z + d, x:x + w].any():
            h += 1
        vis[y:y + h, z:z + d, x:x + w] = True
        boxes.append((x, y, z, w, h, d))
    return boxes

OX, OZ, OY = int(round(cx * 2)), int(round(cz * 2)), y0 * 2
result = {}
total = 0
for k in kinds:
    if not H[k].any():
        continue
    b = greedy(H[k])
    result[k] = [(x - OX, y - OY, z - OZ, w, h, d) for (x, y, z, w, h, d) in b]
    total += len(b)
    print(k, len(b), "pavés")

rods = {}
for name, x, y, z, p in small:
    if name == "end_rod":
        f = p.get("facing", "up")
        ax = "x" if f in ("east", "west") else ("z" if f in ("north", "south") else "y")
        rods.setdefault(ax, set()).add((x, y, z))
rod_out = []
for ax, cells in rods.items():
    done = set()
    for c in sorted(cells):
        if c in done:
            continue
        x, y, z = c
        ln = 1
        while True:
            nxt = (x + ln, y, z) if ax == "x" else ((x, y, z + ln) if ax == "z" else (x, y + ln, z))
            if nxt in cells:
                done.add(nxt); ln += 1
            else:
                break
        done.add(c)
        rod_out.append((ax, x * 2 - OX, y * 2 - OY, z * 2 - OZ, ln))
print("end_rod", len(rod_out), "barres")

others = []
for name, x, y, z, p in small:
    if name == "end_rod":
        continue
    f = p.get("facing") or next((s for s in ("north", "south", "east", "west") if p.get(s) == "true"), "north")
    others.append((name, x * 2 - OX, y * 2 - OY, z * 2 - OZ, f))
print("petits objets", len(others))
print("TOTAL parts ~", total + len(rod_out) + len(others))

def enc(rows):
    return ",".join(str(v) for r in rows for v in r)

axmap = {"x": 1, "y": 2, "z": 3}
lines = [
    "--!strict",
    "-- Généré automatiquement depuis lobby.litematic par tools/litematic_to_roblox.py",
    "-- Ne pas modifier à la main : relancer le script de conversion à la place.",
    "-- Unités : sous-cellules (1 bloc Minecraft = 2 sous-cellules). Origine = centre du plancher, bas du build.",
    "return {",
    f"\tsizeBlocks = Vector3.new({sx}, {sy}, {sz}),",
    "\tboxes = {",
]
for k, rows in result.items():
    lines.append(f"\t\t{k} = \"{enc(rows)}\",")
lines.append("\t},")
lines.append("\trods = \"" + enc([(axmap[a], x, y, z, l) for a, x, y, z, l in rod_out]) + "\",")
lines.append("\tprops = {")
for name, x, y, z, f in others:
    lines.append(f"\t\t{{\"{name}\", {x}, {y}, {z}, \"{f}\"}},")
lines.append("\t},")
lines.append("}")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("fichier", os.path.getsize(out), "octets")
