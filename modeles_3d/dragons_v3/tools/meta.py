import json
T = """1|Pousse|Plante|Commun|Équilibré|Classique
1|Mottin|Terre|Commun|Tank|Drake
1|Brindille|Plante|Commun|Rapide|Amphiptère
1|Galet|Terre|Commun|Brute|Drake
1|Trèfle|Plante|Rare|Équilibré|Classique
1|Bruyère|Terre|Rare|Tank|Drake
1|Sillon|Terre|Rare|Brute|Wyvern
1|Aurore|Plante|Épique|Équilibré|Oriental
2|Braisillon|Feu|Commun|Rapide|Wyvern
2|Cendron|Feu|Commun|Équilibré|Classique
2|Dune|Terre|Commun|Tank|Drake
2|Escarbille|Feu|Rare|Brute|Drake
2|Sirocco|Feu|Rare|Rapide|Amphiptère
2|Magma|Feu|Épique|Brute|Hydre
2|Mirage|Terre|Épique|Équilibré|Oriental
2|Solaris|Feu|Légendaire|Équilibré|Classique
3|Écume|Eau|Commun|Rapide|Aquatique
3|Corail|Eau|Commun|Tank|Drake
3|Palmier|Plante|Commun|Équilibré|Classique
3|Marée|Eau|Rare|Équilibré|Aquatique
3|Lagon|Eau|Rare|Rapide|Amphiptère
3|Perle|Eau|Épique|Tank|Aquatique
3|Liane|Plante|Épique|Brute|Hydre
3|Neptyr|Eau|Légendaire|Équilibré|Oriental
4|Goéland|Vol|Commun|Rapide|Wyvern
4|Mousse|Eau|Commun|Tank|Aquatique
4|Rafale|Vol|Rare|Rapide|Amphiptère
4|Boussole|Eau|Rare|Équilibré|Classique
4|Tempête|Vol|Épique|Brute|Wyvern
4|Typhon|Eau|Légendaire|Brute|Hydre
4|Brume|Ténèbres|Légendaire|Rapide|Oriental
4|Léviathan|Eau|Mythique|Tank|Aquatique
5|Stalactite|Minéral|Rare|Tank|Drake
5|Ombrelame|Ténèbres|Épique|Rapide|Wyvern
5|Quartz|Minéral|Légendaire|Équilibré|Classique
5|Pépite|Minéral|Mythique|Brute|Drake
5|Brillant|Minéral|Mythique|Tank|Classique
5|Revenant|Ténèbres|Secret|Brute|Hydre
5|Néant|Ténèbres|Secret|Rapide|Amphiptère
5|Aïon|Ténèbres|Mythe|Équilibré|Oriental
Exclusif|Prisma|Vol|Exclusif|Équilibré|Classique
Exclusif|Nébula|Ténèbres|Exclusif|Rapide|Oriental"""
d = json.load(open("dragons_old.json", encoding="utf-8"))
order = []
for line in T.split("\n"):
    m, n, e, r, a, mo = line.split("|")
    d[n].update(monde=m, element=e, rarete=r, archetype=a, morphologie=mo)
    order.append(n)
json.dump({"order": order, "dragons": d}, open("dragons_old.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(d["Galet"]["stages"]["adulte"], ensure_ascii=False, indent=1)[:5000])
