#!/usr/bin/env python3
"""
apply_icpms_merges_20260826.py — item 3: one authoritative Description for the 26 ICP-MS fields.

Two acts per field, in order:

  1. RELOCATE. Front-end- or analyser-specific content that cannot live in a description shared by
     nine consumers moves to that TAPP's Column F, which is consumer-owned. The sentences are
     hand-specified, not detected: three attempts at detecting them by word-set overlap all failed
     the same way — they cannot distinguish "same content, different words" from "new content", and
     each returned hundreds of restated definitions. 22 sentences across 12 fields, 51 instances,
     none of which the target Column F already covered.

  2. MERGE. Description is replaced by the agreed text from
     analysis/Merge_ICPMS_Descriptions_2026-08-26.csv — 24 of 26 synthesised, 2 adopted verbatim.

Usage:  python3 apply_icpms_merges_20260826.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys
sys.path.insert(0,"/private/tmp/claude-501/-Users-ruolin-Documents-Astromat-TAPPs/784752d4-09f5-46ef-b7b1-b7e3d1a8e501/scratchpad")
from icpms_reloc import RELOC
DATE="2026-08-26"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=os.path.join(os.path.dirname(__file__),"..",".."))
    ap.add_argument("--apply",action="store_true")
    a=ap.parse_args(); root=os.path.abspath(a.root)
    rows=list(csv.reader(open(os.path.join(root,"Claude Skills for TAPP","analysis",
        "Merge_ICPMS_Descriptions_2026-08-26.csv"),newline="",encoding="utf-8-sig")))[1:]
    MERGE={r[0]:r[2] for r in rows}
    reg=json.load(open(os.path.join(root,"composed_tapps.json"),encoding="utf-8"))
    renames=[]; nreloc=nmerge=0
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]
        if "ICP" not in rel: continue
        rr=list(csv.reader(open(os.path.join(root,rel),newline="",encoding="utf-8-sig"))); ch=0
        for r in rr[1:]:
            if not r or r[0].strip() not in MERGE or not r[1].strip(): continue
            f=r[0].strip()
            for s in RELOC.get(f,[]):
                if s in r[1] and s not in r[5]:
                    r[5]=(r[5].strip()+" | "+s).strip(" |") if r[5].strip() else s
                    nreloc+=1
            if r[1].strip()!=MERGE[f]:
                r[1]=MERGE[f]; r[7]=DATE; ch+=1; nmerge+=1
        if not ch: continue
        new=re.sub(r"_v(\d+)\.csv$",lambda m:f"_v{int(m.group(1))+1}.csv",rel)
        renames.append((rel,new))
        print(f"  {os.path.basename(rel):<34} {ch:>3} merged -> {os.path.basename(new)}")
        if a.apply:
            with open(os.path.join(root,new),"w",newline="",encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rr)
    print(f"\n{nreloc} sentence(s) relocated to Column F · {nmerge} description(s) replaced · {len(renames)} TAPPs")
    if not a.apply:
        print("(dry run — pass --apply to write)"); return
    pm={os.path.basename(o):os.path.basename(n) for o,n in renames}
    for e in reg["composed"]:
        b=os.path.basename(e["tapp"])
        if b in pm: e["tapp"]=e["tapp"].replace(b,pm[b])
    reg["generated"]=DATE
    json.dump(reg,open(os.path.join(root,"composed_tapps.json"),"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    open(os.path.join(root,"composed_tapps.json"),"a").write("\n")
    cv=os.path.join(root,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        for r in cr[1:]:
            for i,c in enumerate(r):
                for o,n in pm.items():
                    if o in c: r[i]=c.replace(o,n)
        csv.writer(open(cv,"w",newline="",encoding="utf-8-sig")).writerows(cr)
    sup=os.path.join(root,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    for old,_ in renames:
        p=os.path.join(root,old); shutil.move(p,os.path.join(sup,os.path.basename(p)))
        x=p[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
    gen=os.path.join(root,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py")
    for _,n in renames: subprocess.run([sys.executable,gen,n],cwd=root,capture_output=True,text=True)
    s=os.path.join(root,"Project Files","Scripts","sync_current_tapps.py")
    r=subprocess.run([sys.executable,s,"--apply"],cwd=root,capture_output=True,text=True)
    print(f"  {(r.stdout.strip().splitlines() or ['synced'])[-1][:60]}")

if __name__=="__main__": main()
