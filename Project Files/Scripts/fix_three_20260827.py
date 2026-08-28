#!/usr/bin/env python3
"""Three content corrections carried over from the Step 1/Step 2 findings.

1. `Dwell Time per Pixel` — SCOPE. SEM_FIBSEM and SEM_Imaging inherited the parent SEM description,
   which documents EDS and WDS compositional mapping. Neither declares any EDS or WDS mode
   (SEM_FIBSEM: TEM Sample Preparation, 3D Tomography; SEM_Imaging: SE/BSE Imaging, CL Point
   Analysis, CL Mapping, EBSD), so that text describes modes those tables do not have. Same class as
   the 70 out-of-scope literature columns dropped from these sub-TAPPs on 2026-08-24. The field
   itself is in scope — both raster-scan — so the description is narrowed, not removed.

2. `Target Feature(s)` (Lab-XCT) — two internal Phase 3 planning notes were sitting in the published
   Description. They are project bookkeeping, not field documentation, and move to Comments.

3. `Flat Field Correction` (Lab-XCT) — the cell ends `"...lab XCT;."`, a stray semicolon left by a
   truncated sentence. Punctuation only.
"""
import csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; DATE="2026-08-27"
NEW_DWELL=("Time the electron beam dwells on each pixel during raster scanning, or on each step "
           "position during mapping, in microseconds or milliseconds.")
NOTES=("Note for Phase 3 literature assessment: evaluate whether procedures in the literature are "
       "feature-specific (acquisition parameters tuned to a specific feature type, e.g., "
       "opaque-phase contrast) or general-purpose (designed to capture all structural features in a "
       "given sample type). This will inform whether the field warrants a controlled list or "
       "remains free text.")

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    edits=[]; renames=[]
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; b=os.path.basename(rel).split("_TAPP")[0]
        if b not in ("SEM_FIBSEM","SEM_Imaging","Lab-XCT"): continue
        rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h=rows[0]; ib=1; ic=h.index("Comments"); iu=h.index("Last Update"); ip=h.index("Purpose")
        n=0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            f=r[0].strip()
            while len(r)<=max(ic,iu,ip): r.append("")
            if b in ("SEM_FIBSEM","SEM_Imaging") and f=="Dwell Time per Pixel":
                if "WDS mapping" not in r[ib]: raise SystemExit("%s: unexpected text"%b)
                edits.append((b,f,"scope-narrowed",r[ib],NEW_DWELL)); r[ib]=NEW_DWELL; r[iu]=DATE; n+=1
            elif b=="Lab-XCT" and f=="Target Feature(s)":
                if NOTES not in r[ib]: raise SystemExit("Target Feature(s): planning notes not found verbatim")
                new=r[ib].replace(NOTES,"").strip()
                if r[ic].strip(): raise SystemExit("Target Feature(s): Comments not empty")
                edits.append((b,f,"planning notes -> Comments",r[ib],new)); r[ib]=new; r[ic]=NOTES; r[iu]=DATE; n+=1
            elif b=="Lab-XCT" and f=="Flat Field Correction":
                if ";." not in r[ip]: raise SystemExit("Flat Field Correction: stray ';.' not found in Purpose")
                new=r[ip].replace(";.",".")
                edits.append((b,f,"punctuation",r[ip],new)); r[ip]=new; r[iu]=DATE; n+=1
        if n:
            new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
            renames.append((e,rel,new,rows)); print("  %-14s %d edit(s) -> %s"%(b,n,os.path.basename(new)))
    for b,f,kind,before,after in edits:
        print("\n  [%s] %s · %s\n    before: %s\n    after : %s"%(b,f,kind,before[:150],after[:150] or "(moved)"))
    if not apply: print("\n(dry run — pass --apply to write)"); return
    for e,rel,new,rows in renames:
        with open(os.path.join(ROOT,new),"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
        e["tapp"]=new
    reg["generated"]=DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(reg,fh,indent=2,ensure_ascii=False); fh.write("\n")
    pm={os.path.basename(o):os.path.basename(n) for _,o,n,_ in renames}
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
    for _,rel,new,_ in renames:
        old=os.path.join(ROOT,rel)
        if os.path.exists(old): shutil.move(old,os.path.join(sup,os.path.basename(old)))
        x=old[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
        subprocess.run([sys.executable,gen,new],cwd=ROOT,capture_output=True,text=True)
    s=os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py")
    p=subprocess.run([sys.executable,s,"--apply"],cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__": main("--apply" in sys.argv)
