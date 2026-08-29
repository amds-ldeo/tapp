#!/usr/bin/env python3
"""Make `Sample Preparation Method` universal (16 TAPPs) and move it into Module_Core.

Decided 2026-08-27. Three changes, in order:

 1. ADD the field to Lab-XCT, the only TAPP lacking it. Excluding it meant an XCT procedure could
    not report a preparation that actually happened — and its papers do report one: "Chips (~10.3 g)
    crushed with mortar and pestle ... split into two ~4.6 g portions", "Decanted for XCT; sample
    split along fractures during mounting into pipette tips", "None; chip used as received". Those
    are forms, being squeezed into the free-text `Sample Preparation Notes` for want of a Method
    field. The two fields stay distinct: Method is the FORM (controlled list), Notes is the handling
    STEPS applied before scanning (free text).

 2. RESOLVE the D-tier divergence to Editable across all 16, changing TEM and the three Solution
    TAPPs from Read-Only. This CORRECTS the adjudication recorded earlier the same day, which called
    the split principled on a perfect 15/15 correlation with the presence of a companion detail
    field. The correlation was real; the causation was not. The literature settles it: TEM reports
    5 DISTINCT preparation methods across 21 extractions (FIB lift-out Ga, FIB lift-out Ga+,
    crushing/dispersion on grid, ultramicrotomy, Ar ion milling), and the Solution TAPPs report
    9-of-10, 6-of-6 and 6-of-6 distinct values. The METHOD itself varies session to session; the
    companion fields carry digestion temperature and duration, i.e. details, not the choice between
    FIB and ultramicrotomy. D=Read-Only made that choice unrecordable.

 3. MOVE it into Module_Core (30 -> 31 fields), `samples` block. Only possible once (1) and (2) are
    done: Core has 16 consumers and owns Column D, so a 15-consumer field with a split D could not
    have gone in.
"""
import csv, json, os, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
DATE="2026-08-27"; FIELD="Sample Preparation Method"
DESC=("The form in which the sample is presented to the instrument, and the preparation that brought "
      "it to that form — for example mounting, sectioning, polishing, coating, crushing, fusion, or "
      "extraction of an electron-transparent section. Record 'None' where the material is analysed "
      "as received.")
C,D,E,K="Basic","Editable","Controlled list / Text","(none)"
XCT_F=("Bulk specimen or fragment (as received) | Core or trimmed billet | Powder or crushed split | "
       "Mounted in tube, straw or pipette tip | Sealed or bagged for containment | Polished block or "
       "epoxy mount | Other: specify | N/A | None")

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    added=retiered=0
    for e in sorted(reg["composed"],key=lambda x:x["tapp"]):
        rel=e["tapp"]; b=os.path.basename(rel).split("_TAPP")[0]
        rows=list(csv.reader(open(os.path.join(ROOT,rel),newline="",encoding="utf-8-sig")))
        h=rows[0]; di=h.index("Analysis-Level Tier"); ui=h.index("Last Update")
        li=h.index("Literature Assessment")
        r=next((x for x in rows[1:] if x and x[0].strip()==FIELD),None)
        changed=False
        if r is None:
            if b!="Lab-XCT": raise SystemExit("%s unexpectedly lacks %s"%(b,FIELD))
            # insert into Group 2, after Sample Preparation Notes so the pair reads together
            anchor=next(i for i,x in enumerate(rows) if x and x[0].strip()=="Sample Preparation Notes")
            new=[""]*len(h)
            new[0]=FIELD; new[1]=DESC; new[2]=C; new[di]=D; new[4]=E
            new[h.index("Example / Allowed Content")]=XCT_F
            new[ui]=DATE; new[h.index("Keyed By")]=K
            for j in range(10,li): new[j]="Y"
            for j in range(li,len(h)): new[j]="N"
            rows.insert(anchor+1,new); added+=1; changed=True
            print("  Lab-XCT: inserted %r after Sample Preparation Notes (modes Y/Y, %d literature cells set N)"
                  %(FIELD,len(h)-li))
        else:
            if r[di].strip()=="Read-Only":
                r[di]="Editable"; r[ui]=DATE; retiered+=1; changed=True
                print("  %-20s D=Read-Only -> Editable"%b)
        # NEVER open for writing outside --apply. `open(path,"w")` truncates the moment the
        # `with` runs, regardless of what the body decides — a dry run that opened every TAPP this
        # way emptied all 16 files before writing nothing to them.
        if apply and changed:
            with open(os.path.join(ROOT,rel),"w",newline="",encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print("\n  inserted into %d TAPP · re-tiered %d TAPP(s)"%(added,retiered))
    if not apply: print("(dry run — pass --apply to write)"); return
    # --- add to Module_Core -------------------------------------------------------------------
    cp=os.path.join(MODDIR,"Module_Core.csv"); jp=os.path.join(MODDIR,"Module_Core.json")
    mrows=list(csv.reader(open(cp,newline="",encoding="utf-8-sig"))); mh=mrows[0]
    if any(x and x[0].strip()==FIELD for x in mrows[1:]): raise SystemExit("already in Core")
    out=[""]*len(mh)
    for c,v in (("Metadata Item",FIELD),("Description",DESC),("Procedure-Level Tier",C),
                ("Analysis-Level Tier",D),("Data Type",E),("Keyed By",K),("Last Update",DATE)):
        out[mh.index(c)]=v
    mrows.append(out)
    with open(cp,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(mrows)
    man=json.load(open(jp,encoding="utf-8"))
    next(b for b in man["blocks"] if b["name"]=="samples")["fields"].append(FIELD)
    old=man["version"]; man["version"]=str(int(old)+1)
    man.setdefault("decisions",[]).append(
      "2026-08-27: `Sample Preparation Method` added — Core 30 -> 31 fields. It was present in 15 of "
      "16 TAPPs; adding it to Lab-XCT made it universal. Excluding it meant an XCT procedure could "
      "not report a preparation that had happened, and its papers do report one (crushing and "
      "splitting, mounting in pipette tips, 'chip used as received'), squeezed into the free-text "
      "`Sample Preparation Notes` for want of a Method field. The two remain distinct fields: Method "
      "is the FORM as a controlled list, Notes is the handling STEPS before scanning. Its D-tier "
      "split (Editable 11 / Read-Only 4) was resolved to Editable, correcting an adjudication made "
      "earlier the same day that called the split principled: the literature shows the METHOD itself "
      "varies session to session (TEM reports 5 distinct methods across 21 extractions; the Solution "
      "TAPPs 9, 6 and 6 distinct), so Read-Only made a real choice unrecordable.")
    with open(jp,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  Module_Core v%s -> v%s, %d -> %d fields"%(old,man["version"],len(mrows)-2,len(mrows)-1))
if __name__=="__main__": main("--apply" in sys.argv)
