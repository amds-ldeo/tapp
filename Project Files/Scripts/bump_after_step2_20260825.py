#!/usr/bin/env python3
"""Version-bump every TAPP and module edited by Step 2, then refresh xlsx, registers and mirror."""
from __future__ import annotations
import csv, glob, json, os, re, shutil, subprocess, sys
DATE="2026-08-25"; ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
apply = "--apply" in sys.argv

bumped={}
for mp in sorted(glob.glob(os.path.join(ROOT,"Claude Skills for TAPP","modules","*.json"))):
    name=os.path.basename(mp).replace("Module_","").replace(".json","")
    man=json.load(open(mp,encoding="utf-8"))
    old=man.get("version","1"); new=str(int(old)+1); bumped[name]=(old,new)
    if apply:
        man["version"]=new
        json.dump(man,open(mp,"w",encoding="utf-8"),indent=4,ensure_ascii=False); open(mp,"a").write("\n")
print(f"modules bumped: {len(bumped)}")

reg_path=os.path.join(ROOT,"composed_tapps.json"); reg=json.load(open(reg_path,encoding="utf-8"))
renames=[]
for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
    rel=e["tapp"]; new=re.sub(r"_v(\d+)\.csv$",lambda m:f"_v{int(m.group(1))+1}.csv",rel)
    renames.append((rel,new)); print(f"  {os.path.basename(rel)} -> {os.path.basename(new)}")
if not apply:
    print("(dry run)"); sys.exit()
for old,new in renames: shutil.copy(os.path.join(ROOT,old), os.path.join(ROOT,new))
pathmap={os.path.basename(o):os.path.basename(n) for o,n in renames}
for e in reg["composed"]:
    b=os.path.basename(e["tapp"])
    if b in pathmap: e["tapp"]=e["tapp"].replace(b,pathmap[b])
    for m in e["modules"]:
        if m["name"] in bumped and m.get("version")==bumped[m["name"]][0]: m["version"]=bumped[m["name"]][1]
reg["generated"]=DATE
json.dump(reg,open(reg_path,"w",encoding="utf-8"),indent=2,ensure_ascii=False); open(reg_path,"a").write("\n")
mr=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Module_Register.csv")
if os.path.exists(mr):
    rows=list(csv.reader(open(mr,newline="",encoding="utf-8-sig")))
    if "Version" in rows[0]:
        vi=rows[0].index("Version")
        for r in rows[1:]:
            if r and r[0].strip() in bumped and r[vi].strip()==bumped[r[0].strip()][0]: r[vi]=bumped[r[0].strip()][1]
        csv.writer(open(mr,"w",newline="",encoding="utf-8-sig")).writerows(rows)
cv=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
if os.path.exists(cv):
    rows=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
    for r in rows[1:]:
        for i,c in enumerate(r):
            for o,n in pathmap.items():
                if o in c: r[i]=c.replace(o,n)
    csv.writer(open(cv,"w",newline="",encoding="utf-8-sig")).writerows(rows)
sup=os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
for old,_ in renames:
    p=os.path.join(ROOT,old)
    if os.path.exists(p): shutil.move(p,os.path.join(sup,os.path.basename(p)))
    x=p[:-4]+".xlsx"
    if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
gen=os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
for _,n in renames: subprocess.run([sys.executable,gen,n],cwd=ROOT,capture_output=True,text=True)
for s in ["build_module_register.py","sync_current_tapps.py"]:
    for d in ["Project Files/Scripts","Claude Skills for TAPP/scripts"]:
        p=os.path.join(ROOT,d,s)
        if os.path.exists(p):
            r=subprocess.run([sys.executable,p,"--apply"],cwd=ROOT,capture_output=True,text=True)
            print(f"  {s}: {(r.stdout.strip().splitlines() or ['ran'])[-1][:70]}"); break
print("done")
