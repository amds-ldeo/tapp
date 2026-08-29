#!/usr/bin/env python3
"""Three agreed register-clearing changes.

A. `Monitored Masses` Keyed By `analyte` -> `defines: channel per analyte` in LA-MC-ICPMS and
   LA-MC-ICPMS_UPb. Not merely drift: those two tables key `Interference Correction Method` by
   `channel` while nothing in them declares `defines: channel`, so the key had no definer. The other
   six consumers already carry the definer form, conventions.md 7.3.1 uses this very field as its
   worked example of `defines: A per B`, and the two outliers have ZERO attested cells against 14
   in the six. `Analyte` is `defines: analyte` in both, so the `per B` half is satisfied.

B. `STEM Dwell Time per Pixel` -> `Dwell Time per Pixel` in TEM. A Rule 1 name variant that should
   not have existed: the register's own note said so. The stated reason for keeping it separate —
   STEM has no spectrometer, so the dwell is scalar — is already how `Dwell Time per Pixel` behaves
   in SEM_FIBSEM and SEM_Imaging, which carry it with `Keyed By: (none)`. Data Type harmonised to
   `Numeric + unit` to match the five existing consumers.

C. `Background Correction Method` -> `X-ray Background Correction Method` in EPMA, SEM and
   SEM_Composition. The field stays exactly what it was; the name stops colliding with ICP-MS's
   `Blank / Background Correction Method`, whose physics is unrelated. Same move as
   `Detector Type` -> `X-ray Detector Type` earlier today, and it retires a triage entry the
   register has had to keep explaining.
"""
import csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; DATE="2026-08-27"
def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    plan=[]
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; b=os.path.basename(rel).split("_TAPP")[0]
        rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h=rows[0]; ki=h.index("Keyed By"); ei=h.index("Data Type"); ui=h.index("Last Update")
        n=0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            f=r[0].strip()
            while len(r)<=max(ki,ei,ui): r.append("")
            if f=="Monitored Masses" and b.startswith("LA-MC") and r[ki].strip()=="analyte":
                r[ki]="defines: channel per analyte"; r[ui]=DATE; n+=1
                print("  A %-18s Monitored Masses  K: analyte -> defines: channel per analyte"%b)
            elif f=="STEM Dwell Time per Pixel" and b=="TEM":
                r[0]="Dwell Time per Pixel"; r[ei]="Numeric + unit"; r[ui]=DATE; n+=1
                print("  B %-18s renamed -> 'Dwell Time per Pixel', E: Numeric (ms) -> Numeric + unit"%b)
            elif f=="Background Correction Method" and b in ("EPMA","SEM","SEM_Composition"):
                r[0]="X-ray Background Correction Method"; r[ui]=DATE; n+=1
                print("  C %-18s renamed -> 'X-ray Background Correction Method'"%b)
        if n: plan.append((e,rel,rows,n))
    print("\n  %d TAPP(s) to bump"%len(plan))
    if not apply: print("(dry run — pass --apply to write)"); return
    renames=[]
    for e,rel,rows,n in plan:
        new=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
        with open(os.path.join(ROOT,new),"w",newline="",encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        e["tapp"]=new; renames.append((rel,new))
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
    p=subprocess.run([sys.executable,os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py"),"--apply"],
                     cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__": main("--apply" in sys.argv)
