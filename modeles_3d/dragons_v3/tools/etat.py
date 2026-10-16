import os, json, glob
L = ["# État des dragons", "", "| Dragon | Scripts | Prompts | Vérifié (report.json) |", "|---|---|---|---|"]
D = json.load(open("data/dragons.json"))
for d in D:
    s = d["slug"]; p = f"out/{s}"
    sc = sum(os.path.exists(f"{p}/{x}.py") for x in ("BEBE", "ADO", "ADULTE"))
    pr = sum(os.path.exists(f"{p}/{x}_prompt.md") for x in ("BEBE", "ADO", "ADULTE"))
    rp = "oui" if os.path.exists(f"{p}/report.json") else "non"
    L.append(f"| {d['nom']} ({d['rarete']}, {d['morphologie']}) | {sc}/3 | {pr}/3 | {rp} |")
open("ETAT.md", "w").write("\n".join(L) + "\n")
