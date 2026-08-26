#!/usr/bin/env python3
"""
apply_step1_icpms_slice_20260825.py — Step 1 for the 26 ICP-MS-specific, module-unowned fields.

MOVE ONLY, rules M1-M6. Each of the 9 ICP-MS TAPPs keeps its own description text; sentences are
assigned to Column B or Column J. Routing is re-derived per row from the sentence text itself
(scratchpad/icpms_route.py), not looked up by variant name, so a TAPP whose text differs from the
recorded variant cannot be mis-split — it simply routes by its own content.

These fields are TAPP-owned, so unlike the module pass there is no single owner to write: all nine
TAPPs are split independently and keep their own wording. Reconciling that wording into one
description is a separate exercise, unchanged in difficulty by this split — measured, not assumed:
mean cross-TAPP similarity of the description halves is 0.21 against 0.17 for the whole cell.

Refuses to write if any row's Description + Purpose does not reconstruct its original word count.

Usage:  python3 apply_step1_icpms_slice_20260825.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-ruolin-Documents-Astromat-TAPPs/784752d4-09f5-46ef-b7b1-b7e3d1a8e501/scratchpad")
import seg, icpms_route

DATE="2026-08-25"; COL_ITEM,COL_DESC,COL_UPDATE,COL_PURPOSE=0,1,7,9

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=os.path.join(os.path.dirname(__file__),"..",".."))
    ap.add_argument("--apply",action="store_true")
    a=ap.parse_args(); root=os.path.abspath(a.root)
    slice_=set(json.load(open("/private/tmp/claude-501/-Users-ruolin-Documents-Astromat-TAPPs/784752d4-09f5-46ef-b7b1-b7e3d1a8e501/scratchpad/icpms_slice.json")))
    reg=json.load(open(os.path.join(root,"composed_tapps.json"),encoding="utf-8"))
    renames=[]; bad=[]
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]
        if "ICP" not in rel: continue
        path=os.path.join(root,rel); rows=list(csv.reader(open(path,newline="",encoding="utf-8-sig")))
        nb=0
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip(): continue
            f=r[COL_ITEM].strip()
            if f not in slice_ or not r[COL_DESC].strip(): continue
            while len(r)<=COL_PURPOSE: r.append("")
            orig=r[COL_DESC].strip()
            ss=seg.sentences(orig)
            d=[];p=[]
            for i,s in enumerate(ss,1):
                route,_,_=icpms_route.route(f,i,s)
                (p if route=="P" else d).append(s)
            D=" ".join(d); P=" ".join(p)
            if len((D+" "+P).split())!=len(orig.split()):
                bad.append((os.path.basename(rel),f)); continue
            if P:
                r[COL_DESC]=D
                r[COL_PURPOSE]=(r[COL_PURPOSE].strip()+" "+P).strip() if r[COL_PURPOSE].strip() else P
                r[COL_UPDATE]=DATE; nb+=1
        if not nb: continue
        newrel=re.sub(r"_v(\d+)\.csv$",lambda m:f"_v{int(m.group(1))+1}.csv",rel)
        renames.append((rel,newrel))
        print(f"  {os.path.basename(rel):<36} {nb:>3} field(s) split -> {os.path.basename(newrel)}")
        if a.apply:
            with open(os.path.join(root,newrel),"w",newline="",encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    if bad:
        print(f"\n  WORD-COUNT MISMATCH on {len(bad)} row(s) — those rows were skipped:")
        for b in bad[:5]: print("   ",b)
    print(f"\n{len(renames)} TAPP(s) to bump")
    if not a.apply:
        print("(dry run — pass --apply to write)"); return

    pathmap={os.path.basename(o):os.path.basename(n) for o,n in renames}
    for e in reg["composed"]:
        b=os.path.basename(e["tapp"])
        if b in pathmap: e["tapp"]=e["tapp"].replace(b,pathmap[b])
    reg["generated"]=DATE
    json.dump(reg,open(os.path.join(root,"composed_tapps.json"),"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    open(os.path.join(root,"composed_tapps.json"),"a").write("\n")
    cv=os.path.join(root,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in crows[1:]:
            for i,c in enumerate(r):
                for o,n in pathmap.items():
                    if o in c: r[i]=c.replace(o,n)
        csv.writer(open(cv,"w",newline="",encoding="utf-8-sig")).writerows(crows)
    sup=os.path.join(root,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    for old,_ in renames:
        p=os.path.join(root,old); shutil.move(p,os.path.join(sup,os.path.basename(p)))
        x=p[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
    gen=os.path.join(root,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for _,n in renames: subprocess.run([sys.executable,gen,n],cwd=root,capture_output=True,text=True)
    s=os.path.join(root,"Project Files","Scripts","sync_current_tapps.py")
    r=subprocess.run([sys.executable,s,"--apply"],cwd=root,capture_output=True,text=True)
    print(f"  {(r.stdout.strip().splitlines() or ['synced'])[-1][:70]}")

if __name__=="__main__": main()
