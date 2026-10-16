"""python3 build.py out/POUSSE/ADULTE.py [--render]
Injecte le kit à la place de '# @@KIT@@', écrit out/<SLUG>/<STAGE>.full.py, lance le contrôle
(bpy) et, avec --render, produit renders/<SLUG>_<STAGE>.png (vue 3/4 avant) et _side.png."""
import sys, subprocess, os
src = sys.argv[1]
kit = open(os.path.join(os.path.dirname(__file__), "kit/kit.py"), encoding="utf-8").read().rstrip() + "\n"
body = open(src, encoding="utf-8").read()
if "# @@KIT@@" not in body:
    sys.exit("ERREUR : ligne '# @@KIT@@' absente")
full = body.replace("# @@KIT@@", kit, 1)
out = src[:-3] + ".full.py"
open(out, "w", encoding="utf-8").write(full)
here = os.path.dirname(os.path.abspath(__file__))
name = os.path.basename(os.path.dirname(os.path.abspath(src))) + "_" + os.path.basename(src)[:-3]
args = [sys.executable, os.path.join(here, "run_check.py"), out]
if "--render" in sys.argv:
    os.makedirs(os.path.join(here, "renders"), exist_ok=True)
    r1 = subprocess.run(args + [os.path.join(here, "renders", name + ".png")], capture_output=True, text=True)
    r2 = subprocess.run(args + [os.path.join(here, "renders", name + "_side.png"), "(1.0, 0.15, 0.25)"], capture_output=True, text=True)
    res = r1
else:
    res = subprocess.run(args, capture_output=True, text=True)
lines = [l for l in (res.stdout + res.stderr).splitlines()
         if any(k in l for k in ("RESULT", "RENDER", "Error", "error", "Traceback", "File \"", "généré", "->"))]
print("\n".join(lines[-25:]))
