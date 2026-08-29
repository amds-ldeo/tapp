#!/usr/bin/env python3
"""Rename both interference-flag fields, and correct the ICP-MS Column F.

Names. "Spectral interference" is the standard umbrella term in BOTH communities — in ICP-MS it
covers isobaric, polyatomic and doubly-charged species; in EPMA/SEM it is the standard term for
X-ray line overlap. The old names were wrong in opposite directions: the ICP-MS field was called
`Isobaric...` while its own description covers "isobaric, polyatomic or residual" interferences, and
the electron-beam field was called simply `Interference...` while its description says "spectral".

  ICP-MS (9, module-owned)  `Isobaric Interference Corrections Applied`
                         -> `Spectral Interference Corrections Applied`
  Electron-beam (3)         `Interference Corrections Applied`
                         -> `X-ray Spectral Interference Corrections Applied`

The `X-ray` qualifier disambiguates the pair, as `X-ray Detector Type` and `X-ray Background
Correction Method` did earlier today, and retires the two register entries for the pair.

Column F. NOT a retype. The ICP-MS field keeps `Controlled list / Text`, which the literature earns:
of 51 attested cells, ZERO are a bare Yes/No — every one carries the answer together with what was
corrected. Column F was the cell that did not match the data, reading `Yes | No | N/A | None` while
describing none of them. Widened to the attested compound form. This is the mirror of the
amds-ldeo/tapp#1 finding: there the Data Type was under-specified against the data; here Column F was.

NOT split into isobaric / polyatomic / residual fields: a single procedure routinely corrects more
than one kind at once (LA-MC corrects doubly-charged AND isobaric; Solution MC isobaric AND argides;
Solution Q oxide AND argide AND isobaric on the same masses), so three flags would mostly all read
"Yes" while losing the species-to-mass pairing. That pairing already lives in `Interfering Species`
and `Interference Correction Method`, both `channel`-keyed.
"""
import csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
DATE="2026-08-27"
OLD_ICP="Isobaric Interference Corrections Applied"; NEW_ICP="Spectral Interference Corrections Applied"
OLD_EB="Interference Corrections Applied";            NEW_EB="X-ray Spectral Interference Corrections Applied"
NEW_F=("e.g., 'Yes — ⁸⁷Rb on ⁸⁷Sr, corrected from the ⁸⁵Rb monitor' | 'Yes — doubly-charged Er and Yb "
       "on the Sr and Rb masses' | 'No explicit corrections applied; medium resolution resolves the "
       "polyatomic interferences' | N/A | None")
EB={"EPMA","SEM","SEM_Composition"}

def main(apply=False):
    # --- module first: it owns the ICP-MS field's name -----------------------------------------
    cp=os.path.join(MODDIR,"Module_ICPMS.csv"); jp=os.path.join(MODDIR,"Module_ICPMS.json")
    mrows=list(csv.reader(open(cp,newline="",encoding="utf-8-sig"))); mh=mrows[0]
    mrow=next((r for r in mrows[1:] if r and r[0].strip()==OLD_ICP),None)
    if mrow is None: raise SystemExit("%s not in Module_ICPMS"%OLD_ICP)
    print("  Module_ICPMS  %r -> %r"%(OLD_ICP,NEW_ICP))
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    nf=nren=0
    plan=[]
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; b=os.path.basename(rel).split("_TAPP")[0]
        rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h=rows[0]; fi=h.index("Example / Allowed Content"); ui=h.index("Last Update")
        n=0
        for r in rows[1:]:
            if not r or not r[0].strip(): continue
            while len(r)<=max(fi,ui): r.append("")
            if r[0].strip()==OLD_ICP:
                r[0]=NEW_ICP; r[fi]=NEW_F; r[ui]=DATE; n+=1; nren+=1; nf+=1
            elif r[0].strip()==OLD_EB and b in EB:
                r[0]=NEW_EB; r[ui]=DATE; n+=1; nren+=1
        if n: plan.append((e,rel,rows,n)); print("    %-20s %d row(s)"%(b,n))
    print("\n  %d row(s) renamed · %d Column F corrected · %d TAPP(s) to bump"%(nren,nf,len(plan)))
    if not apply: print("(dry run — pass --apply to write)"); return
    mrow[0]=NEW_ICP; mrow[mh.index("Last Update")]=DATE
    with open(cp,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(mrows)
    man=json.load(open(jp,encoding="utf-8"))
    for blk in man["blocks"]:
        blk["fields"]=[NEW_ICP if f==OLD_ICP else f for f in blk["fields"]]
    old=man["version"]; man["version"]=str(int(old)+1)
    man["decisions"].append(
      "2026-08-27: `%s` renamed to `%s`. The old name was narrower than the field: its own "
      "description covers isobaric, polyatomic AND residual interferences, while 'isobaric' in "
      "ICP-MS usage specifically excludes polyatomic. 'Spectral interference' is the standard "
      "umbrella term. Data Type UNCHANGED at `Controlled list / Text`, which the literature earns — "
      "of 51 attested cells none is a bare Yes/No; every one carries the answer with what was "
      "corrected. Column F was the mismatch, reading `Yes | No | N/A | None` while describing none "
      "of them, and is widened to the attested compound form. Not split into per-kind fields: one "
      "procedure routinely corrects several kinds at once, and the species-to-mass detail already "
      "lives in `Interfering Species` and `Interference Correction Method`, both channel-keyed."
      %(OLD_ICP,NEW_ICP))
    with open(jp,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  Module_ICPMS v%s -> v%s"%(old,man["version"]))
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
    for o,nn in renames:
        op=os.path.join(ROOT,o)
        if os.path.exists(op): shutil.move(op,os.path.join(sup,os.path.basename(op)))
        x=op[:-4]+".xlsx"
        if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
        subprocess.run([sys.executable,gen,nn],cwd=ROOT,capture_output=True,text=True)
    p=subprocess.run([sys.executable,os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py"),"--apply"],
                     cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__": main("--apply" in sys.argv)
