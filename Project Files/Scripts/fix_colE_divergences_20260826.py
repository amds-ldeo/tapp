#!/usr/bin/env python3
"""
fix_colE_divergences_20260826.py — resolve 9 of the 10 remaining Column E divergences.

Each decision is taken on literature evidence, by the rule already used for the Detection Limit
pair: where attested values cluster into families the type is `Controlled list / Text`; where they
are nearly all distinct it is `Text (free)`; where a unit is unanimous in the attestations it is
pinned, and paired with `/ Text` when a qualitative answer is also attested.

The five EPMA/SEM fields do NOT share one answer, which is what the evidence overturned:

  Beam Diameter            13 attested, µm unanimous — but 5 read "Focused (exact diameter N)",
                           so the qualitative answer is real   -> Numeric (µm) / Text
  Step Size / Pixel Size   3 attested, all µm, some per-map lists -> Numeric (µm) / Text
  Beam Raster Dimensions   attested as "5×5 µm²", a pair        -> Numeric pair (µm x µm)
  Map Area                 0 attested; same quantity shape as above -> Numeric pair (µm x µm)
  Dwell Time per Pixel     1 attested and it is "~0.5 s per step", which DISPROVES EPMA's
                           Numeric (ms) pin                     -> Numeric + unit

  Mass Bias Correction Strategy   0.93 distinct -> Text (free); Solution MC's Controlled list is
                                  far too tight for values like "Internal normalization to
                                  98Mo/96Mo = 1.453173 using the exponential law"
  Phase Identification Method     0.96 distinct -> Text (free)
  Internal Standard Approach      0.66 distinct -> Controlled list / Text
  Pulse/Analog Detector
    Nonlinearity Correction       0.53 distinct -> Controlled list / Text

NOT decided here: `Sample Preparation Method`. Its 123 attested cells at 0.50 distinctness do
cluster ("polished thin section", "polished thick section", "grain mount", ...), so the evidence
points at Controlled list / Text — but that needs a Column F vocabulary authored and agreed across
15 TAPPs spanning every technique in the library. It is left at Text (free) and stays registered.

Usage:  python3 fix_colE_divergences_20260826.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys
DATE="2026-08-26"; COL_ITEM,COL_TYPE,COL_UPDATE=0,4,7
NEW={
 "Beam Diameter":"Numeric (µm) / Text",
 "Step Size / Pixel Size":"Numeric (µm) / Text",
 "Beam Raster Dimensions":"Numeric pair (µm x µm)",
 "Map Area":"Numeric pair (µm x µm)",
 "Dwell Time per Pixel":"Numeric + unit",
 "Mass Bias Correction Strategy":"Text (free)",
 "Phase Identification Method":"Text (free)",
 "Internal Standard Approach":"Controlled list / Text",
 "Pulse/Analog Detector Nonlinearity Correction":"Controlled list / Text",
}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=os.path.join(os.path.dirname(__file__),"..",".."))
    ap.add_argument("--apply",action="store_true")
    a=ap.parse_args(); root=os.path.abspath(a.root)
    reg=json.load(open(os.path.join(root,"composed_tapps.json"),encoding="utf-8"))
    renames=[]
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; rows=list(csv.reader(open(os.path.join(root,rel),newline="",encoding="utf-8-sig")))
        ch=[]
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip(): continue
            f=r[COL_ITEM].strip()
            if f in NEW and r[COL_TYPE].strip()!=NEW[f]:
                ch.append((f,r[COL_TYPE].strip(),NEW[f])); r[COL_TYPE]=NEW[f]; r[COL_UPDATE]=DATE
        if not ch: continue
        newrel=re.sub(r"_v(\d+)\.csv$",lambda m:f"_v{int(m.group(1))+1}.csv",rel)
        renames.append((rel,newrel))
        print(f"  {os.path.basename(rel):<36} -> {os.path.basename(newrel)}")
        for f,o,n in ch: print(f"        {f:<46} {o!r} -> {n!r}")
        if a.apply:
            with open(os.path.join(root,newrel),"w",newline="",encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{len(renames)} TAPP(s)")
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
    print(f"  {(r.stdout.strip().splitlines() or ['synced'])[-1][:70]}")
if __name__=="__main__": main()
