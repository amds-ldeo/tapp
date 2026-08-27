#!/usr/bin/env python3
"""Build Module_CompositionQC — the shared quality-control apparatus of the 12 TAPPs that report
quantitative composition calibrated against reference materials.

Consumer set: EPMA, SEM, SEM_Composition and the 9 ICP-MS TAPPs. Absent from exactly the four
techniques that do not report calibrated composition: SEM_Imaging, SEM_FIBSEM, TEM, Lab-XCT.
Module_ICPMS's own extraction note set these fields aside on 2026-08-25 as "a candidate layer of
their own"; this is that layer.

FIVE fields, not seven. Excluded, each for a stated reason:

  Sample Preparation Method          — 15 consumers, not 12, and sits in Group 2. A different
                                       consumer set is a different module; it also carries its own
                                       unresolved D-tier split (Editable 11 / Read-Only 4).
  Primary Calibration Standard Name  — its Keyed By splits `analyte` (5) / `(none)` (7), and unlike
                                       Secondary Reference Materials the per-analyte axis IS
                                       attested: 8 of EPMA's 11 extracted cells assign standards per
                                       element ("Anorthite (SiKa, AlKa, CaKa); albite (NaKa); ..."),
                                       and the 2026-08-12 audit set LA-SF to `analyte` on Navarro et
                                       al. 2024. Declaring one key for all 12 would answer the G3
                                       policy question recorded in Survey_ColB_ColI_Report_2026-08-12
                                       ("always declare the finest key?") by fiat, for one field.
                                       Deferred until that policy is decided.
"""
import csv, json, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
DATE = "2026-08-27"
NAME = "CompositionQC"

CONSUMERS = ["EPMA","SEM","SEM_Composition","LA-Q-ICP-MS","LA-SF-ICP-MS","LA-MC-ICP-MS",
             "LA-Q-ICP-MS U-Pb","LA-SF-ICP-MS U-Pb","LA-MC-ICP-MS U-Pb",
             "Solution Q-ICP-MS","Solution SF-ICP-MS","Solution MC-ICP-MS"]

# field -> (Description, C, D, E, KeyedBy, Example, group-block)
FIELDS = [
 ("Detection Limit",
  "Detection limit, one per reported concentration variable (one per analyte, these being the same "
  "set). State the units and whether the values are procedure-typical estimates or session-specific "
  "measured values. The calculation method is recorded separately in Detection Limit Method. Record "
  "'N/A' where the procedure reports no concentrations.",
  "Advanced","Basic","Numeric + unit / Text","reported property","qc"),

 ("Detection Limit Method",
  "Formula or approach used to calculate the detection limits, with a citation for the method where "
  "one exists. Must be consistent with the values reported in Detection Limit.",
  "Basic","Read-Only","Controlled list / Text","reported property","qc"),

 ("Counting Statistics Error",
  "Uncertainty predicted from counting statistics — the theoretical limit set by the Poisson "
  "distribution of the counts accumulated — for each reported quantity per analysis, with the sigma "
  "level stated. Derived from the counts on the analyte together with those on any background or "
  "blank subtracted from it. Distinct from the scatter actually observed within a measurement or "
  "between repeated measurements, which is recorded separately: where a procedure reports both, "
  "agreement indicates the measurement is shot-noise limited, and a larger observed scatter "
  "indicates a further source of variance.",
  "Advanced","Basic","Text (free)","sample > sampling unit x reported property","qc"),

 ("Secondary Reference Materials",
  "Quality-control reference material(s) measured as unknowns alongside samples to assess accuracy "
  "independently and to monitor drift. Give the material name, its source, and a citation for the "
  "accepted or reference values used for comparison.",
  "Basic","Editable","Text (free)","defines: standard","qc"),

 ("Normalization / Standards-Based Correction",
  "Post-acquisition normalization applied to the reported data beyond the primary calibration — for "
  "example correction to a reference value derived from secondary reference materials, or correction "
  "for a systematic bias those materials reveal. Record 'None' if no additional normalization is "
  "applied.",
  "Advanced","Editable","Text (free)","reported property","reduction"),
]

BLOCKS = [
 {"name":"qc","target_group":"6. Quality Control & Uncertainty","placement":"append_to_group",
  "fields":[f[0] for f in FIELDS if f[6]=="qc"]},
 {"name":"reduction","target_group":"5. Data Processing","placement":"append_to_group",
  "fields":[f[0] for f in FIELDS if f[6]=="reduction"]},
]

def main(apply=False):
    # --- verify the consumer set is exactly what we think, before writing anything -------------
    reg = json.load(open(os.path.join(ROOT,"composed_tapps.json"),encoding="utf-8"))
    names = [f[0] for f in FIELDS]
    have = {n:set() for n in names}
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"]).split("_TAPP")[0]
        rows = list(csv.reader(open(os.path.join(ROOT,e["tapp"]),newline="",encoding="utf-8-sig")))
        for r in rows[1:]:
            if r and r[0].strip() in have and len(r)>1 and r[1].strip(): have[r[0].strip()].add(b)
    sets = {frozenset(v) for v in have.values()}
    if len(sets) != 1:
        for n,v in have.items(): print("  %-42s %d consumers"%(n,len(v)))
        raise SystemExit("the five fields do not share one consumer set")
    consumers = sorted(next(iter(sets)))
    if len(consumers) != 12: raise SystemExit("expected 12 consumers, got %d: %s"%(len(consumers),consumers))
    print("  verified: all 5 fields present in exactly the same 12 TAPPs")
    print("   ", ", ".join(consumers))

    hdr = ["Metadata Item","Description","Procedure-Level Tier","Analysis-Level Tier","Data Type",
           "Example / Allowed Content","Comments","Last Update","Keyed By","Purpose"]
    rows = [hdr]
    for name,desc,c,d,e_,k,_blk in FIELDS:
        rows.append([name,desc,c,d,e_,"","",DATE,k,""])

    man = {
      "module": NAME,
      "title": "Composition quality control — detection limits, counting statistics, secondary reference materials and standards-based normalization",
      "layer": 2,
      "version": "1",
      "source_of_truth": "modules/Module_%s.csv" % NAME,
      "owned_columns": ["A","B","C","D","E","I"],
      "overlay_columns": ["F","J"],
      "mode_flag_default": "Y",
      "source_comment": "Source: Composition QC module",
      "conditional": False,
      "blocks": BLOCKS,
      "consumed_by": CONSUMERS,
      "notes": ("What every procedure that reports a calibrated quantitative composition shares, "
                "independent of how the sample is introduced and of what does the measuring. The "
                "consumer set is exactly the 12 TAPPs that report composition; the four it is absent "
                "from — SEM_Imaging, SEM_FIBSEM, TEM, Lab-XCT — are the imaging and structural "
                "techniques, which is why the set is a real boundary and not an accident of "
                "authoring. Four of the five fields sit in Group 6; `Normalization / Standards-Based "
                "Correction` sits in Group 5 because it is a data-reduction step, and is carried in "
                "its own block."),
      "extraction": ("Extracted 2026-08-27 under Rule 6.10, from the set Module_ICPMS set aside on "
                     "2026-08-25 as 'the quantitative-composition set ... a candidate layer of their "
                     "own'. Candidate set was 7; two were excluded. `Sample Preparation Method` has "
                     "15 consumers, not 12, and a different consumer set is a different module. "
                     "`Primary Calibration Standard Name` is deferred on its Keyed By split — see "
                     "decisions."),
      "decisions": [
        "2026-08-27: `Counting Statistics Error` ships UNCHANGED — its Columns B, C, D, E and I were "
        "already byte-identical across all 12, so for that field this module changes nothing and "
        "simply converts 12 hand-maintained copies into one owned definition.",

        "2026-08-27: the other four descriptions were MERGED BY READING, five variants each. "
        "Lineage-specific content was relocated to consumer-owned Column F rather than dropped, "
        "following the 2026-08-26 Module_ICPMS precedent. Worksheet: "
        "analysis/Merge_CompositionQC_Descriptions_2026-08-27.csv.",

        "2026-08-27: `Secondary Reference Materials` Keyed By resolved to `defines: standard`, "
        "changing EPMA, SEM and SEM_Composition from `defines: standard per analyte`. The literature "
        "decides it: across all 12 TAPPs, ZERO extracted cells are per-analyte shaped — EPMA's own "
        "four are plain standard lists ('USNM San Carlos olivine (Fo90); Kakanui kaersutite'), and "
        "SEM and SEM_Composition have no extractions at all. Only Column F's template example was "
        "per-analyte, and a template can invite a column nobody fills (Rule 7.12 / the AGN "
        "precedent). The structural argument agrees: the per-element assessment of a secondary "
        "standard lives in `Analytical Accuracy` and `Analytical Precision`, both keyed "
        "`standard x reported property`, so carrying it here duplicated their key.",

        "2026-08-27: `Detection Limit Method` drops EPMA's sentence 'When the procedure does not "
        "specify a method, the analyst should complete this field.' It contradicted that field's own "
        "Analysis-Level Tier, which is Read-Only in all 12 — a tension flagged during the Step 1 "
        "routing and resolved here rather than propagated into a module.",

        "2026-08-27: `Primary Calibration Standard Name` DEFERRED, and it is the one field of the "
        "seven left out for a reason that may change. Its Keyed By splits `analyte` (EPMA, SEM, "
        "SEM_Composition, LA-SF, LA-SF U-Pb) against `(none)` (7 others), and unlike Secondary "
        "Reference Materials the per-analyte axis is genuinely attested — 8 of EPMA's 11 extracted "
        "cells assign standards per element. A module owns Column I, so shipping it means declaring "
        "one key for all 12: `analyte` over-declares for the seven, `(none)` destroys structure the "
        "literature attests. That is the G3 conditional-key policy question recorded in "
        "Survey_ColB_ColI_Report_2026-08-12 — 'declare the finest key unconditionally, or add a "
        "conditional marker?' — and it should be decided as policy, not settled sideways by one "
        "field's extraction.",
      ],
    }

    print("\n  Module_%s: %d fields, %d blocks, %d consumers" % (NAME,len(FIELDS),len(BLOCKS),len(CONSUMERS)))
    if not apply:
        print("(dry run — pass --apply to write)"); return
    with open(os.path.join(MODDIR,"Module_%s.csv"%NAME),"w",newline="",encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    with open(os.path.join(MODDIR,"Module_%s.json"%NAME),"w",encoding="utf-8") as fh:
        json.dump(man,fh,indent=4,ensure_ascii=False); fh.write("\n")
    print("  written Module_%s.csv + .json"%NAME)

if __name__ == "__main__":
    main("--apply" in sys.argv)
