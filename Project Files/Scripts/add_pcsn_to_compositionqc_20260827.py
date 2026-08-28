#!/usr/bin/env python3
"""Add `Primary Calibration Standard Name` to Module_CompositionQC (5 -> 6, v1 -> v2).

Unblocked by the G3 policy decision of 2026-08-27 (conventions.md 7.3.2): declare the finest
attested key unconditionally. Its Keyed By therefore becomes `analyte` for all 12 consumers,
changing the seven that declared `(none)`.

The per-analyte axis is attested, which is why `analyte` is the finest ATTESTED key and not an
invented one: 8 of EPMA's 11 extracted cells assign standards per element ("Anorthite (SiKa, AlKa,
CaKa); albite (NaKa); fayalite (FeKa)..."), and the 2026-08-12 literature audit set LA-SF to
`analyte` on Navarro et al. 2024. The seven that declared `(none)` are procedures that do not
exercise the axis, not evidence that the axis is unreal — which is precisely the case 7.3.2 settles.

Five descriptions merged by reading. C, D and E were already uniform across all 12.
"""
import csv, json, os, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
DATE="2026-08-27"; FIELD="Primary Calibration Standard Name"
DESC=("Name and reference material identifier of the primary reference material(s) against which the "
      "instrument is calibrated — converting raw signal intensities to concentrations, or anchoring an "
      "isotope ratio as the bracketing standard or zero-delta reference. Give the material name, its "
      "source or supplier, and a citation for the accepted values used, since results calibrated "
      "against different published values for the same material are not directly comparable.")
C,D,E,K="Basic","Editable","Text (free)","analyte"

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    mod=[e for e in reg["composed"] if any(m["name"]=="CompositionQC" for m in e["modules"])]
    seen={}
    for e in mod:
        rows=list(csv.reader(open(os.path.join(ROOT,e["tapp"]),newline="",encoding="utf-8-sig"))); h=rows[0]
        r=next((x for x in rows[1:] if x and x[0].strip()==FIELD and len(x)>1 and x[1].strip()),None)
        if r is None: raise SystemExit("%s missing from %s"%(FIELD,e["tapp"]))
        seen.setdefault(tuple(r[h.index(c)].strip() for c in
            ("Procedure-Level Tier","Analysis-Level Tier","Data Type")),[]).append(os.path.basename(e["tapp"]))
    if len(mod)!=12: raise SystemExit("expected 12 CompositionQC consumers, got %d"%len(mod))
    if list(seen)!=[(C,D,E)]:
        raise SystemExit("C/D/E are not uniform, or do not match what is authored: %r"%seen)
    print("  verified: %s present in all 12 consumers; C/D/E uniform and matching"%FIELD)

    csvp=os.path.join(MODDIR,"Module_CompositionQC.csv"); jsonp=os.path.join(MODDIR,"Module_CompositionQC.json")
    rows=list(csv.reader(open(csvp,newline="",encoding="utf-8-sig"))); h=rows[0]
    if any(r and r[0].strip()==FIELD for r in rows[1:]): raise SystemExit("already in the module")
    out=[""]*len(h)
    for c,v in (("Metadata Item",FIELD),("Description",DESC),("Procedure-Level Tier",C),
                ("Analysis-Level Tier",D),("Data Type",E),("Keyed By",K),("Last Update",DATE)):
        out[h.index(c)]=v
    rows.append(out)
    man=json.load(open(jsonp,encoding="utf-8"))
    next(b for b in man["blocks"] if b["name"]=="qc")["fields"].append(FIELD)
    old=man["version"]; man["version"]=str(int(old)+1)
    man["decisions"].append(
      "2026-08-27: extended to 6 fields — `Primary Calibration Standard Name` added, unblocked by the "
      "G3 policy decision recorded as conventions.md 7.3.2 (declare the finest ATTESTED key "
      "unconditionally). Its Keyed By becomes `analyte` across all 12, changing the seven that "
      "declared `(none)`. The axis is attested, not invented: 8 of EPMA's 11 extracted cells assign "
      "standards per element, and the 2026-08-12 audit set LA-SF to `analyte` on Navarro et al. 2024. "
      "The seven `(none)` declarations were procedures that do not exercise the axis, which is the "
      "case 7.3.2 settles — a simple procedure now fills a keyed table with one row, which is correct. "
      "Five descriptions merged by reading; C, D and E were already uniform.")
    print("  Module_CompositionQC: %d -> %d fields, v%s -> v%s"%(len(rows)-2,len(rows)-1,old,man["version"]))
    if not apply: print("(dry run — pass --apply to write)"); return
    with open(csvp,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
    with open(jsonp,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  written")
if __name__=="__main__": main("--apply" in sys.argv)
