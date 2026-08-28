#!/usr/bin/env python3
"""Build Module_CollisionCell — the collision/reaction cell subsystem.

Six fields across the six ICP-MS TAPPs whose instruments have a cell: LA-Q, LA-Q U-Pb, LA-MC,
LA-MC U-Pb, Solution Q, Solution MC. The SF TAPPs are not consumers — sector-field instruments have
no cell and do not carry these fields at all, which is why the consumer set is a real boundary.

C, D, E and Keyed By were already uniform across all six on every field; only the descriptions
diverged, four variants each, and those were merged by reading.

NOT DONE HERE: these six have never been through the Description/Purpose split, so their merged
descriptions still carry rationale in Column B. That is deliberate. Column J is an OVERLAY column,
and compose_tapp writes only OWNED columns for a field already present in a consumer — so Purpose
text placed in the module would not reach the six TAPPs and would be lost, which is exactly the
failure recorded for Module_ArAr on 2026-08-25. The six join the module Step 1 backlog instead.
"""
import csv, json, os, sys
ROOT="/Users/ruolin/Documents/Astromat/TAPPs"; MODDIR=os.path.join(ROOT,"Claude Skills for TAPP","modules")
DATE="2026-08-27"; NAME="CollisionCell"
CONSUMERS=["LA-Q-ICP-MS","LA-Q-ICP-MS U-Pb","LA-MC-ICP-MS","LA-MC-ICP-MS U-Pb",
           "Solution Q-ICP-MS","Solution MC-ICP-MS"]
FIELDS=[
 ("Collision/Reaction Cell (CRC) Configuration",
  "Whether a collision or reaction cell is installed and its operating mode. In standard mode (STD), "
  "no cell gas is introduced and the cell acts only as an ion guide. In kinetic energy discrimination "
  "(KED) mode, helium thermalizes ions so that polyatomic interferences, which have a larger collision "
  "cross-section, are selectively retarded by a cell exit barrier voltage. In dynamic reaction cell "
  "(DRC) mode, a reactive gas selectively neutralizes specific interferences through ion-molecule "
  "reactions. On MS/MS instruments a second mass filter preceding the cell enables precursor-ion "
  "selection. Specific gas types, flow rates and cell voltages are documented in Group 4. Record "
  "'Not installed' where the instrument has no collision/reaction cell.",
  "Basic","Read-Only","Controlled list","channel","hardware"),
 ("Collision Gas Type",
  "Type of collision gas introduced into the collision/reaction cell in KED mode. Helium (He) is the "
  "standard collision gas for kinetic energy discrimination, being low in mass and chemically inert. "
  "Record 'None' if the cell is in STD mode, and 'N/A' where Collision/Reaction Cell (CRC) "
  "Configuration does not include KED or the instrument has no cell.",
  "Basic","Read-Only","Controlled list / Text","channel","acquisition"),
 ("Collision Gas Flow Rate",
  "Flow rate of the collision gas, typically He, introduced into the collision/reaction cell in KED "
  "mode, in mL/min. Controls the degree of ion thermalization and KED efficiency; higher flow rates "
  "give greater interference suppression at the cost of analyte sensitivity. Record 'None' if the "
  "cell is in STD mode, and 'N/A' where Collision/Reaction Cell (CRC) Configuration does not include "
  "KED or the instrument has no cell.",
  "Basic","Editable","Numeric (mL/min)","(none)","acquisition"),
 ("Reaction Gas Type",
  "Type of reactive gas introduced into the dynamic reaction cell (DRC) for interference removal "
  "through ion-molecule reactions. Common reaction gases include NH₃ (e.g., for Fe, Ca, K isotopes), "
  "O₂ (e.g., for As, Ge) and CH₄. Record 'None' if DRC mode is not used, and 'N/A' where "
  "Collision/Reaction Cell (CRC) Configuration does not include DRC or the instrument has no cell.",
  "Advanced","Read-Only","Controlled list / Text","channel","acquisition"),
 ("Reaction Gas Flow Rate",
  "Flow rate of the reactive gas introduced into the dynamic reaction cell (DRC), in mL/min. Record "
  "'None' if DRC mode is not used, and 'N/A' where Collision/Reaction Cell (CRC) Configuration does "
  "not include DRC or the instrument has no cell.",
  "Advanced","Editable","Numeric (mL/min)","(none)","acquisition"),
 ("Cell Exit Discrimination Voltage",
  "Bias voltage applied at the collision/reaction cell exit to discriminate between analyte ions and "
  "low-energy polyatomic interferences in KED mode, in volts (V). A negative bias preferentially "
  "retards slow polyatomic ions while transmitting faster analyte ions, controlling the degree of "
  "polyatomic suppression. Record 'None' if the cell is in STD mode, and 'N/A' where "
  "Collision/Reaction Cell (CRC) Configuration does not include KED or the instrument has no cell.",
  "Basic","Editable","Numeric (V)","(none)","acquisition"),
]
BLOCKS=[{"name":"hardware","target_group":"3. Instrument & Software","placement":"append_to_group",
         "fields":[f[0] for f in FIELDS if f[6]=="hardware"]},
        {"name":"acquisition","target_group":"4. Measurement Information","placement":"append_to_group",
         "fields":[f[0] for f in FIELDS if f[6]=="acquisition"]}]

def main(apply=False):
    reg=json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    names=[f[0] for f in FIELDS]; have={n:set() for n in names}; tiers={n:set() for n in names}
    for e in reg["composed"]:
        b=os.path.basename(e["tapp"]).split("_TAPP")[0]
        rows=list(csv.reader(open(os.path.join(ROOT,e["tapp"]),newline="",encoding="utf-8-sig"))); h=rows[0]
        for r in rows[1:]:
            if r and r[0].strip() in have and len(r)>1 and r[1].strip():
                have[r[0].strip()].add(b)
                tiers[r[0].strip()].add(tuple(r[h.index(c)].strip() for c in
                    ("Procedure-Level Tier","Analysis-Level Tier","Data Type","Keyed By")))
    sets={frozenset(v) for v in have.values()}
    if len(sets)!=1:
        for n,v in have.items(): print("  %-46s %d"%(n,len(v)))
        raise SystemExit("the six fields do not share one consumer set")
    cons=sorted(next(iter(sets)))
    if len(cons)!=6: raise SystemExit("expected 6 consumers, got %d: %s"%(len(cons),cons))
    for n,(_,_,c,d,e_,k,_b) in zip(names,FIELDS):
        if tiers[n]!={(c,d,e_,k)}:
            raise SystemExit("%s: authored C/D/E/I %r does not match the library's %r"%(n,(c,d,e_,k),tiers[n]))
    print("  verified: 6 fields, one consumer set, C/D/E/I match the library exactly")
    print("   ",", ".join(cons))
    hdr=["Metadata Item","Description","Procedure-Level Tier","Analysis-Level Tier","Data Type",
         "Example / Allowed Content","Comments","Last Update","Keyed By","Purpose"]
    rows=[hdr]+[[n,d,c,dd,e_,"","",DATE,k,""] for n,d,c,dd,e_,k,_b in FIELDS]
    man={"module":NAME,
      "title":"Collision/reaction cell — configuration, cell gases and kinetic energy discrimination",
      "layer":2,"version":"1","source_of_truth":"modules/Module_%s.csv"%NAME,
      "owned_columns":["A","B","C","D","E","I"],"overlay_columns":["F","J"],
      "mode_flag_default":"Y","source_comment":"Source: collision/reaction cell module",
      "conditional":False,"blocks":BLOCKS,"consumed_by":CONSUMERS,
      "notes":("The collision/reaction cell subsystem, shared by every ICP-MS TAPP whose instrument "
               "can have a cell. The consumer set is the Q and MC lineages; the SF TAPPs are not "
               "consumers because sector-field instruments have no cell and do not carry these "
               "fields at all. Q and MC share the subsystem for the same reason — a hexapole or "
               "quadrupole cell upstream of the analyser — which is why this is a real layer and not "
               "an accident of which tables happened to be authored together."),
      "extraction":("Extracted 2026-08-27 under Rule 6.10 from the fields left TAPP-owned after "
                    "Module_ICPMS reached 39. Six fields, exactly the Rule 6.10 floor."),
      "decisions":[
        "2026-08-27: C, D, E and Keyed By were ALREADY uniform across all six consumers on every "
        "field; only the descriptions diverged, four variants each. A guard re-checks the authored "
        "tiers against the library and refuses to write on any mismatch, so this module cannot "
        "silently retype a field while merging its prose.",
        "2026-08-27: the four description variants differed in two ways only — LA-MC and Solution MC "
        "add a conditional \"Record 'N/A' where CRC Configuration does not include KED/DRC\", and "
        "Solution MC adds MC-instrument context (most MC-ICP-MS have no cell; Nu Sapphire and Thermo "
        "Neoma MS/MS do). The merged text keeps the conditional, which is real content under W3, and "
        "generalises the instrument context to 'or the instrument has no cell' so it serves Q and MC "
        "alike. The LA descriptions' \"Record 'Not applicable' for SF-ICP-MS instruments\" was "
        "dropped: no SF TAPP consumes this module, so it was guidance about instruments outside the "
        "consumer set.",
        "2026-08-27: these six have NOT been through the Description/Purpose split, so Column B "
        "still carries rationale. Deliberate. Column J is an overlay, and compose_tapp writes only "
        "OWNED columns for a field already present in a consumer, so Purpose text placed here would "
        "not reach the six TAPPs — the loss recorded for Module_ArAr on 2026-08-25. They join the "
        "module Step 1 backlog.",
        "2026-08-27: three further cell fields — Collision/Reaction Gas Mixture Ratio, Reaction "
        "Product Ion / Mass-Shift Transition, Signal Collection Mode — were NOT included. They sit "
        "on a different consumer set (LA-Q, LA-Q U-Pb, Solution Q only), which is three, below the "
        "Rule 6.10 floor. Carrying them as a conditional block would reintroduce conditional modules, "
        "retired library-wide on 2026-08-14. They stay TAPP-owned.",
      ]}
    print("\n  Module_%s: %d fields, %d blocks, %d consumers"%(NAME,len(FIELDS),len(BLOCKS),len(CONSUMERS)))
    if not apply: print("(dry run — pass --apply to write)"); return
    with open(os.path.join(MODDIR,"Module_%s.csv"%NAME),"w",newline="",encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    with open(os.path.join(MODDIR,"Module_%s.json"%NAME),"w",encoding="utf-8") as fh:
        json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  written Module_%s.csv + .json"%NAME)
if __name__=="__main__": main("--apply" in sys.argv)
