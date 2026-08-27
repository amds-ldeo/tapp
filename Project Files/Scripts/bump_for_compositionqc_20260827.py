#!/usr/bin/env python3
"""Recompose and bump the 12 CompositionQC consumers.

Composition writes straight to the NEW version path, so each superseded copy is the file as it was
published. `Last Update` is stamped on the five rows that became module-owned.
"""
import csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE=os.path.join(ROOT,"Claude Skills for TAPP","scripts","compose_tapp.py")
DATE="2026-08-27"
FIELDS={"Detection Limit","Detection Limit Method","Counting Statistics Error",
        "Secondary Reference Materials","Normalization / Standards-Based Correction"}

def flags(mods):
    out=[]
    for m in mods:
        spec=m["name"]
        if m.get("blocks"): spec+=":"+(m["blocks"] if isinstance(m["blocks"],str) else ",".join(m["blocks"]))
        out+=["--module",spec]
    return out

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    targets=[e for e in reg["composed"] if any(m["name"]=="CompositionQC" for m in e["modules"])]
    if len(targets)!=12: raise SystemExit("expected 12 consumers, found %d"%len(targets))
    plan=[]
    for e in targets:
        rel=e["tapp"]
        new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
        plan.append((e,rel,new)); print("  %-36s -> %s"%(os.path.basename(rel),os.path.basename(new)))
    if not apply: print("(dry run — pass --apply to write)"); return
    for e,rel,new in plan:
        cmd=[sys.executable,COMPOSE,"--source",os.path.join(ROOT,rel)]+flags(e["modules"])+["--out",os.path.join(ROOT,new)]
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        if p.returncode!=0: raise SystemExit("compose failed %s\n%s\n%s"%(rel,p.stdout[-1200:],p.stderr[-600:]))
        np_=os.path.join(ROOT,new); rows=list(csv.reader(open(np_,newline="",encoding="utf-8-sig")))
        h=rows[0]; iu=h.index("Last Update"); ic=h.index("Comments"); n=0
        for r in rows[1:]:
            if r and r[0].strip() in FIELDS:
                while len(r)<=max(iu,ic): r.append("")
                if r[ic].strip()!="Source: Composition QC module":
                    raise SystemExit("%s: %s missing provenance stamp"%(new,r[0]))
                r[iu]=DATE; n+=1
        if n!=5: raise SystemExit("%s: stamped %d of 5 rows"%(new,n))
        with open(np_,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
        print("  composed %s"%os.path.basename(new))
    pm={os.path.basename(o):os.path.basename(n) for _,o,n in plan}
    cv=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in cr[1:]:
            for i,c in enumerate(r):
                for o,n in pm.items():
                    if o in c: r[i]=c.replace(o,n)
        with open(cv,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(cr)
    sup=os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    gen=os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for _,rel,new in plan:
        old=os.path.join(ROOT,rel)
        if os.path.exists(old): shutil.move(old,os.path.join(sup,os.path.basename(old)))
        x=old[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
        subprocess.run([sys.executable,gen,new],cwd=ROOT,capture_output=True,text=True)
    r=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8")); r["generated"]=DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(r,fh,indent=2,ensure_ascii=False); fh.write("\n")
    s=os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py")
    p=subprocess.run([sys.executable,s,"--apply"],cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__=="__main__": main("--apply" in sys.argv)
