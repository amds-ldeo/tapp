#!/usr/bin/env python3
"""Add `EELS Chemical State Determination Method` to the TEM TAPP.

Closes the gap opened on 2026-08-27, when two mis-extracted cells were removed from
`EELS Energy Resolution` — a field typed `Numeric (eV FWHM)` that was holding Fe-valence
determination METHODS. The values were correct data in the wrong field, and there was no right
field to move them to.

Naming follows the library's own vocabulary: `EELS Energy Calibration` already describes accurate
calibration as required for "ELNES edge identification, chemical-state analysis, and inter-lab
comparability" — it names the analysis this field records, while itself recording only the energy-
axis calibration that precedes it. Rule 1 prefix `EELS ` matches the other twelve EELS fields.

Placement: Group 5 (Data Processing), beside `EELS Background Subtraction Method` and
`EELS Plural Scattering Correction`, whose C=Advanced / D=Editable tiers it shares — chemical-state
determination is a reduction and interpretation step, not an acquisition setting.

Data Type `Controlled list / Text` follows the amds-ldeo/tapp#1 precedent for Method fields: both
attested cells name a method FAMILY and carry a citation or qualifier, which is exactly the case
that compound type exists for.

Keyed By `(none)`, deliberately. Rule 7.12 keys on the finest axis ATTESTED IN REPORTED DATA, and
both attested cells determine the state of a single element (Fe). A per-analyte or per-edge axis is
plausible but NOT attested, and 7.3.2 licenses declaring the finest attested key, not the finest
imaginable one. Revisit if a multi-element chemical-state procedure is extracted.

Literature: all 21 columns are `N/A` except the two attested. Papers that report oxidation states by
XPS (Chaves et al. 2023), Mössbauer (Thompson et al. 2020) or citation to other work (Matsumoto
et al. 2021, Zeng et al. 2024) did not determine it by ELNES, so the concept does not apply to those
procedures — `N/A`, not `N`, per lit_assessment.md.
"""
import csv, json, os, re, shutil, subprocess, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; DATE="2026-08-27"
FIELD="EELS Chemical State Determination Method"
DESC=("Method used to determine the chemical or oxidation state of an element from the fine structure "
      "of its ionization edge (ELNES), together with the reference data or calibration the "
      "determination relies on. Name the method family and cite the calibration curve or reference "
      "spectra used. Record 'N/A' where no chemical-state determination is made.")
PURPOSE=("The same edge yields different valence estimates under different calibrations and reference "
         "spectra, so a reported oxidation state is not comparable between studies unless the method "
         "and its reference data are stated.")
C,D,E,K="Advanced","Editable","Controlled list / Text","(none)"
F=("White-line intensity ratio (L3/L2) | Integral white-line ratio against a published calibration "
   "curve | Peak position and lineshape comparison to reference standards | Multiple linear "
   "least-squares (MLLS) fitting to reference spectra | Edge onset energy shift | Other: specify | "
   "N/A | None")
VALUES={
 "Cymes2023 | Apollo 17 soil 71501 pyroxene (1pyx + 2pyx) | HAADF-STEM + Dual EELS + EDS (NRL Nion UltraSTEM200-X)":
   "Integral white-line intensity ratio I(L3)/I(L2) → Van Aken & Liebscher (2002) universal "
   "calibration curve for Fe³⁺/ΣFe; MLLS fitting of Fe L2,3 ELNES with two reference spectra for "
   "oxidation state maps",
 "Mo2022 | Chang'E-5 lunar soil CE5C0400YJFM00505 | TEM-EELS (Shanghai Institute of Ceramics CAS Hitachi HF5000)":
   "Peak position and lineshape comparison to reference standards (qualitative Fe valence state "
   "determination: Fe⁰, Fe²⁺, Fe³⁺)",
}
ANCHOR="EELS Plural Scattering Correction"

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    entry=next(e for e in reg["composed"] if os.path.basename(e["tapp"]).startswith("TEM_"))
    rel=entry["tapp"]
    rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
    h=rows[0]; li=h.index("Literature Assessment")
    if any(r and r[0].strip()==FIELD for r in rows[1:]): raise SystemExit("field already present")
    anchor=next(i for i,r in enumerate(rows) if r and r[0].strip()==ANCHOR)
    new=[""]*len(h)
    for c,v in (("Metadata Item",FIELD),("Description",DESC),("Procedure-Level Tier",C),
                ("Analysis-Level Tier",D),("Data Type",E),("Example / Allowed Content",F),
                ("Last Update",DATE),("Keyed By",K),("Purpose",PURPOSE)):
        new[h.index(c)]=v
    for j in range(10,li): new[j]=["Y","Y","N"][j-10]      # TEM Imaging, STEM Imaging, Electron Diffraction
    new[li]=""                                             # sentinel column is a separator, never a flag
    unmatched=set(VALUES)
    for j in range(li+1,len(h)):
        col=h[j]
        new[j]=VALUES.get(col,"N/A")
        unmatched.discard(col)
    if unmatched: raise SystemExit("literature column(s) not found:\n  %s"%"\n  ".join(sorted(unmatched))[:400])
    rows.insert(anchor+1,new)
    nval=sum(1 for j in range(li+1,len(h)) if new[j]!="N/A")
    print("  %s"%FIELD)
    print("    inserted into Group 5 after %r"%ANCHOR)
    print("    C=%s D=%s E=%s K=%s · modes Y/Y/N"%(C,D,E,K))
    print("    literature: %d attested value(s), %d N/A"%(nval,len(h)-li-1-nval))
    newrel=re.sub(r"_v(\d+)\.csv$",lambda m:"_v%d.csv"%(int(m.group(1))+1),rel)
    print("    %s -> %s"%(os.path.basename(rel),os.path.basename(newrel)))
    if not apply: print("\n(dry run — pass --apply to write)"); return
    with open(os.path.join(ROOT,newrel),"w",newline="",encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    entry["tapp"]=newrel; reg["generated"]=DATE
    with open(os.path.join(ROOT,"composed_tapps.json"),"w",encoding="utf-8") as fh:
        json.dump(reg,fh,indent=2,ensure_ascii=False); fh.write("\n")
    cv=os.path.join(ROOT,"Project Files","Registers & Planning","TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        cr=list(csv.reader(open(cv,newline="",encoding="utf-8-sig")))
        ob,nb=os.path.basename(rel),os.path.basename(newrel)
        for r in cr[1:]:
            for i,c in enumerate(r):
                if ob in c: r[i]=c.replace(ob,nb)
        with open(cv,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(cr)
    sup=os.path.join(ROOT,"Superseded TAPPs",DATE); os.makedirs(sup,exist_ok=True)
    old=os.path.join(ROOT,rel); shutil.move(old,os.path.join(sup,os.path.basename(old)))
    x=old[:-4]+".xlsx"
    if os.path.exists(x): shutil.move(x,os.path.join(sup,os.path.basename(x)))
    subprocess.run([sys.executable,os.path.join(ROOT,"Claude Skills for TAPP","scripts","tapp_to_xlsx.py"),newrel],
                   cwd=ROOT,capture_output=True,text=True)
    p=subprocess.run([sys.executable,os.path.join(ROOT,"Project Files","Scripts","sync_current_tapps.py"),"--apply"],
                     cwd=ROOT,capture_output=True,text=True)
    print("  mirror:",(p.stdout.strip().splitlines() or ["synced"])[-1][:80])
if __name__=="__main__": main("--apply" in sys.argv)
