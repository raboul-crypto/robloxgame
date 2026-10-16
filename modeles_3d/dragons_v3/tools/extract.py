import re, json
lines = open("scripts.md", encoding="utf-8").read().split("\n")
# Find dragon header lines "Monde X · élément ... · morphologie ..."
dragons = []
i = 0
text = "\n".join(lines)
# split into stage blocks by header "Name · Bébé|Jeune (ado)|Adulte" followed by "Prompt"
pat = re.compile(r"^(?P<name>[^\n>]+?) · (?P<stage>Bébé|Jeune \(ado\)|Adulte)\n\nPrompt\n", re.M)
heads = list(pat.finditer(text))
print(len(heads))
out = {}
meta_pat = re.compile(r"Monde (\d+) · élément (\S+) · rareté (\S+) · archétype (\S+) ·\s*\n?\s*morphologie (\S+)")
for k, m in enumerate(heads):
    end = heads[k+1].start() if k+1 < len(heads) else len(text)
    block = text[m.end():end]
    prompt_part = block.split("Script Python Blender")[0]
    p = "\n".join(l[2:] if l.startswith("> ") else ("" if l == ">" else l) for l in prompt_part.split("\n"))
    p = p.replace("\\", "")
    p = re.sub(r"(?<!\n)\n(?!\n)", " ", p)  # unwrap
    before = text[max(0, m.start()-600):m.start()]
    mm = list(meta_pat.finditer(before))
    name = m.group("name").strip()
    d = out.setdefault(name, {"name": name, "stages": {}})
    if mm:
        g = mm[-1].groups()
        d.update(monde=int(g[0]), element=g[1], rarete=g[2], archetype=g[3], morphologie=g[4])
    st = {"Bébé": "bebe", "Jeune (ado)": "jeune", "Adulte": "adulte"}[m.group("stage")]
    pal = re.findall(r"- `(\w+)` \(([^)]*(?:\([^)]*\))?[^)]*)\) : (#[0-9A-Fa-f]{6})([^\n-]*)", p)
    def sect(title):
        r = re.search(r"### \d+\. " + title + r"[^\n]*\n(.*?)(?=\n### |\nNe tronque|\Z)", p, re.S)
        return r.group(1).strip() if r else ""
    d["stages"][st] = {
        "palette": [{"slot": a, "role": b, "hex": c, "note": e.strip(" —-")} for a, b, c, e in pal],
        "morpho_stade": sect("MORPHOLOGIE ET STADE"),
        "anatomie": sect("ANATOMIE ET PROPORTIONS"),
        "pose": sect("POSE"),
    }
json.dump(out, open("dragons_old.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out))
for n, d in out.items():
    print(n, d.get("monde"), d.get("rarete"), d.get("morphologie"), {s: len(v["palette"]) for s, v in d["stages"].items()})
