#!/usr/bin/env python3
"""Recompose every TAPP whose composition now differs, bump it, and stamp Last Update on exactly
the rows that changed. Generic: works for any composition change.

Composes to the NEW version path so each superseded copy is the file as it was published.
"""
import csv, json, os, re, shutil, subprocess, sys, tempfile
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE=os.path.join(ROOT,"Claude Skills for TAPP","scripts","compose_tapp.py")
DATE="2026-08-27"
def flags(mods):
    out=[]
    for m in mods:
        spec=m["name"]
        if m.get("blocks"): spec+=":"+(m["blocks"] if isinstance(m["blocks"],str) else ",".join(m["blocks"]))
        out+=["--module",spec]
    return out
def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    plan=[]
    for e in reg["composed"]:
        rel=e["tapp"]
        p=subprocess.run([sys.executable,COMPOSE,"--source",os.path.join(ROOT,rel)]+flags(e["modules"])+["--check"],
                         cwd=ROOT,capture_output=True,text=True)
        if p.returncode==1: plan.append(e)
        elif p.returncode!=0: raise SystemExit("check failed for %s"%rel)
    print("  %d TAPP(s) differ"%len(plan))
    if not plan: return
    for e in plan:
        rel=e["tapp"]; new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
        print("  %-36s -> %s"%(os.path.basename(rel),os.path.basename(new)))
    if not apply: print("(dry run — pass --apply to write)"); return
    renames=[]
    for e in plan:
        rel=e["tapp"]; new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
        before={r[0].strip():list(r) for r in csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")) if r and r[0].strip()}
        p=subprocess.run([sys.executable,COMPOSE,"--source",os.path.join(ROOT,rel)]+flags(e["modules"])+["--out",os.path.join(ROOT,new)],
                         cwd=ROOT,capture_output=True,text=True)
        if p.returncode!=0: raise SystemExit("compose failed %s\n%s"%(rel,p.stdout[-900:]))
        np_=os.path.join(ROOT,new); rows=list(csv.reader(open(np_,newline="",encoding="utf-8-sig")))
        h=rows[0]; iu=h.index("Last Update"); n=0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            b=before.get(r[0].strip())
            if b is None: continue
            if [c for c in r[:iu]]+[c for c in r[iu+1:]] != [c for c in b[:iu]]+[c for c in b[iu+1:]]:
                while len(r)<=iu: r.append("")
                r[iu]=DATE; n+=1
        with open(np_,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
        e["tapp"]=new; renames.append((rel,new)); print("  composed %s (%d row(s) stamped)"%(os.path.basename(new),n))
    # compose_tapp.record_composition rewrites composed_tapps.json during the loop above —
    # including each module's version. Writing back the copy loaded BEFORE the loop would
    # discard those updates, which is how CompositionQC came to read v2 against a v3 manifest.
    # Reload, then apply only what this script owns (the tapp paths and the generated date).
    paths={os.path.basename(o):os.path.basename(n) for o,n in renames}
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    for e in reg["composed"]:
        b=os.path.basename(e["tapp"])
        if b in paths: e["tapp"]=e["tapp"].replace(b,paths[b])
    reg["generated"]=DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(reg,fh,indent=2,ensure_ascii=False); fh.write("\n")
    pm={os.path.basename(o):os.path.basename(n) for o,n in renames}
    cv=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in cr[1:]:
            for i,c in enumerate(r):
                for o,nn in pm.items():
                    if o in c: r[i]=c.replace(o,nn)
        with open(cv,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(cr)
    sup=os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    gen=os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for old,new in renames:
        o=os.path.join(ROOT,old)
        if os.path.exists(o): shutil.move(o,os.path.join(sup,os.path.basename(o)))
        x=o[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
        subprocess.run([sys.executable,gen,new],cwd=ROOT,capture_output=True,text=True)
    s=os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py")
    p=subprocess.run([sys.executable,s,"--apply"],cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__": main("--apply" in sys.argv)
