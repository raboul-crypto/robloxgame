import docx,re,json,unicodedata
d=docx.Document('/root/.claude/uploads/5f89345c-b2b8-5260-bcd1-62a3626100e4/d1dbeef2-Dragon_Pets_Scripts_Blender.docx')
P=[p.text for p in d.paragraphs]
st={}
for i,t in enumerate(P):
    m=re.match(r'^([^#].*?) · (Bébé|Jeune \(ado\)|Adulte)$',t)
    if m: st.setdefault(m.group(1),[]).append((m.group(2),i))
print(len(st), [k for k,v in st.items() if len(v)!=3])
order=list(st)
def slug(n): return unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().upper().replace(' ','_')
out=[]
for k,name in enumerate(order):
    stages=st[name]
    hdr=P[stages[0][1]-1]
    m=re.match(r'(?:Monde )?(\S+) · élément (\S+) · rareté (\S+) · archétype (\S+) · morphologie (\S+)',hdr)
    if not m: print('HDR?',name,repr(hdr)); continue
    D=dict(nom=name,slug=slug(name),monde=m.group(1),element=m.group(2),rarete=m.group(3),archetype=m.group(4),morphologie=m.group(5),stades={})
    for j,(sname,i0) in enumerate(stages):
        end=stages[j+1][1] if j+1<len(stages) else (st[order[k+1]][0][1]-2 if k+1<len(order) else len(P))
        block=P[i0:end]
        code_i=next(x for x,t in enumerate(block) if t.startswith('Script Python Blender'))
        prompt=block[2:code_i]
        pal=[]; sig=desc=stade=''; morph=''; anat=[]; sec=''
        for t in prompt:
            if t.startswith('###'): sec=t; continue
            mm=re.match(r'- `(\w+)` \((.*)\) : (#[0-9A-Fa-f]{6})',t)
            if mm: pal.append(dict(nom=mm.group(1),role=mm.group(2),hex=mm.group(3).upper()))
            if t.startswith('- Signes distinctifs'): sig=t.split(':',1)[1].strip()
            elif t.startswith('- Description de ce stade'): desc=t.split(':',1)[1].strip()
            elif t.startswith('- Stade '): stade=t.split(':',1)[1].strip()
            elif sec.startswith('### 3') and t.startswith('- '): morph=t[2:]
            elif sec.startswith('### 4') and t.startswith('- '): anat.append(t[2:])
        key={'Bébé':'bebe','Jeune (ado)':'jeune','Adulte':'adulte'}[sname]
        D['stades'][key]=dict(palette=pal,description=desc,regles_stade=stade,anatomie_ancienne=anat)
        D['signes']=sig; D['morpho_desc']=morph
    out.append(D)
json.dump(out,open('data/dragons.json','w'),ensure_ascii=False,indent=1)
print(len(out))
x=[o for o in out if o['nom']=='Solaris'][0]
print(json.dumps({k:v for k,v in x.items() if k!='stades'},ensure_ascii=False,indent=1)); print(json.dumps(x['stades']['adulte'],ensure_ascii=False,indent=1)[:2500])
