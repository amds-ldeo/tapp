#!/usr/bin/env python3
"""Extend Module_LaserAblation 19 -> 29 fields (manifest v6 -> v7).

Ten fields present in exactly the six LA TAPPs and unowned by any module. **Zero content change:**
all ten are already byte-identical across all six consumers on every module-owned column
(A, B, C, D, E, I), so composition rewrites them to the values they already hold. Same shape as
Module_ICPMS v1 and the Analysis Sequence move — nine hand-maintained copies become one owned
definition. A guard re-verifies that agreement per field before anything is written.

The ten map onto the module's four existing blocks by their current group, so no new block is needed.
"""
import csv, json, os, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
DATE="2026-08-27"
ASSIGN={"la_sample":["Fusion Flux and Dilution Ratio","Sample Form / Analytical Substrate"],
        "la_hardware":["Sample Introduction"],
        "la_acquisition":["Background Count Time","Carrier Gas and Flow Rate","Mapping Area",
                          "Multi-Run Sequential Analysis Design","Signal Smoothing"],
        "la_reduction":["Elemental Fractionation Correction","Matrix Offset Correction (LIEF)"]}
OWN=["Metadata Item","Description","Procedure-Level Tier","Analysis-Level Tier","Data Type","Keyed By"]

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    la=[e for e in reg["composed"] if any(m["name"]=="LaserAblation" for m in e["modules"])]
    if len(la)!=6: raise SystemExit("expected 6 LA consumers, got %d"%len(la))
    fields=[f for fs in ASSIGN.values() for f in fs]
    canon={}
    for f in fields:
        seen={}
        for e in la:
            rows=list(csv.reader(open(os.path.join(ROOT,e["tapp"]),newline="",encoding="utf-8-sig")))
            h=rows[0]; r=next((x for x in rows[1:] if x and x[0].strip()==f),None)
            if r is None: raise SystemExit("%s missing from %s"%(f,e["tapp"]))
            seen[tuple((r[h.index(c)].strip() if len(r)>h.index(c) else "") for c in OWN)]=e["tapp"]
        if len(seen)!=1:
            raise SystemExit("%s is NOT uniform across the 6 LA TAPPs (%d variants) — this extension "
                             "assumes zero content change"%(f,len(seen)))
        canon[f]=list(seen)[0]
    print("  verified: all %d fields byte-identical across all 6 LA consumers"%len(fields))

    csvp=os.path.join(MODDIR,"Module_LaserAblation.csv"); jsonp=os.path.join(MODDIR,"Module_LaserAblation.json")
    rows=list(csv.reader(open(csvp,newline="",encoding="utf-8-sig"))); h=rows[0]
    existing={r[0].strip() for r in rows[1:] if r and r[0].strip()}
    for f in fields:
        if f in existing: raise SystemExit("%s already in the module"%f)
    idx={c:h.index(c) for c in OWN}
    for f in fields:
        out=[""]*len(h)
        for c,v in zip(OWN,canon[f]): out[idx[c]]=v
        out[h.index("Last Update")]=DATE
        rows.append(out)
    man=json.load(open(jsonp,encoding="utf-8"))
    for b in man["blocks"]:
        if b["name"] in ASSIGN: b["fields"].extend(ASSIGN[b["name"]])
    old=man["version"]; man["version"]=str(int(old)+1)
    man.setdefault("decisions",[]).append(
      "2026-08-27: extended 19 -> 29 fields. Ten fields present in exactly the six LA TAPPs and "
      "unowned by any module were taken over: Background Count Time, Carrier Gas and Flow Rate, "
      "Elemental Fractionation Correction, Fusion Flux and Dilution Ratio, Mapping Area, Matrix "
      "Offset Correction (LIEF), Multi-Run Sequential Analysis Design, Sample Form / Analytical "
      "Substrate, Sample Introduction, Signal Smoothing. ZERO content change — all ten were already "
      "byte-identical across all six consumers on A, B, C, D, E and I, verified per field by a guard "
      "that refuses to write otherwise, so composition rewrites them to the values they already "
      "hold. The only cell that moves in each TAPP is the Column G provenance stamp. They map onto "
      "the module's four existing blocks by their current group, so no new block was needed. This is "
      "the same shape as Module_ICPMS v1: six hand-maintained copies become one owned definition.")
    print("  Module_LaserAblation: %d -> %d fields, manifest v%s -> v%s"%(len(existing),len(existing)+len(fields),old,man["version"]))
    if not apply: print("(dry run — pass --apply to write)"); return
    with open(csvp,"w",newline="",encoding="utf-8-sig") as fh: csv.writer(fh).writerows(rows)
    with open(jsonp,"w",encoding="utf-8") as fh: json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  written")
if __name__=="__main__": main("--apply" in sys.argv)
