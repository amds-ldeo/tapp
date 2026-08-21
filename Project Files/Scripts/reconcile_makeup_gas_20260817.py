#!/usr/bin/env python3
"""
Reconcile `Make-up Gas Flow Rate` (3 Solution TAPPs) and `Plasma / Make-up Gas Addition` (6 LA TAPPs)
into a single field, `Make-up Gas and Flow Rate`, across all 9 ICP-MS TAPPs.

THEY ARE ONE FIELD, and the extractions prove it rather than the descriptions:
  LA   "Ar make-up: 0.9-1.2 l min-1; Ar auxiliary: 0.6-1.2 l min-1"
       "Ar make-up: 0.81-0.99 l min-1 (mapping); N2 explicitly not added"
       "N2 or Ar mixed into He carrier for sensitivity optimization"
  Sol  "0.25 L/min supplementary Ar for PFA micronebulizer"
       "None - the Apex Omega was run 'with no auxiliary N2 flow'"
Every cell on both sides records the same two things: the argon make-up flow, and the presence or
explicit absence of a small sensitivity-enhancement addition. Same concept, same content shape.

NAME `Make-up Gas and Flow Rate`, chosen over either incumbent:
  * It matches `Carrier Gas and Flow Rate`, its nearest sibling in the same gas block, exactly in
    form — that is the library's established pattern for a field holding gas identity AND flow.
  * It drops the "Plasma /" prefix, which collides with `Coolant (Plasma) Gas Flow Rate` in the same
    TAPP. Two fields whose names both begin by invoking the plasma, one of which is not a plasma gas,
    is a confusion the reconciliation should remove rather than carry forward.
  * It fixes the Solution name, which said only "Flow Rate" while the field demonstrably holds the
    gas identity too ("0.25 L/min supplementary Ar").

COLUMNS
  B  rewritten technique-neutral, covering both an ablation cell and a desolvation system as the
     upstream context, and both roles of the gas (make-up to maintain delivery, small N2/H2 additions
     to enhance sensitivity). Both incumbents' instruction to state "None" explicitly is kept — it is
     what makes an absent value distinguishable from an unreported one.
  E  -> `Numeric (L/min) / Text` (the Solution form) in all 9. The LA form was bare `Text (free)`,
     which loses the unit; the compound says "a flow in L/min, with text where a qualifying or
     multi-part answer is needed", which is what the extractions actually contain.
  C=Advanced, D=Editable, I=(none) already agreed on both sides — unchanged.
  F  left per TAPP: consumer-owned, and the LA and Solution examples are both already correct for
     their technique.

Both old names go into RETIRED_FIELDS so the doc-staleness check can find any live document still
naming them. The documents that do name them are all dated records (the 2026-08-14 report and notes,
the development log, precedents.md), which are correct as written at their date and are not rewritten.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
NEW = "Make-up Gas and Flow Rate"
OLD = {"Make-up Gas Flow Rate", "Plasma / Make-up Gas Addition"}

NEW_B = ("Supplementary gas added to the sample-carrying stream between the sample introduction system "
         "and the plasma, with its identity and the procedure-registered target flow rate. Argon make-up "
         "is standard and maintains total gas delivery where the carrier flow alone is insufficient — "
         "downstream of an ablation cell, or of a desolvation system that has removed solvent load. "
         "Small nitrogen or hydrogen additions are also made here to enhance sensitivity for some "
         "elements; record them with their own flow, whose unit commonly differs from the make-up flow. "
         "Record 'None' explicitly where no supplementary gas is added, to distinguish it from not "
         "reported.")
NEW_E = "Numeric (L/min) / Text"

JOBS = [
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v24.csv",              "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v25.csv"),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v24.csv",          "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v25.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v23.csv",            "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v24.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v24.csv",        "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v25.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v21.csv",             "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v22.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v21.csv",         "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v22.csv"),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v28.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v29.csv"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v26.csv","Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v27.csv"),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v25.csv","Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v26.csv"),
]

for src, dst in JOBS:
    p = os.path.join(ROOT, src)
    rows = list(csv.reader(open(p, encoding='utf-8-sig')))
    hit = [r for r in rows[1:] if r and r[0] in OLD]
    assert len(hit) == 1, f"{src}: found {len(hit)} rows to reconcile"
    r = hit[0]
    was = r[0]
    r[0], r[1], r[4], r[7] = NEW, NEW_B, NEW_E, DATE
    assert (r[2], r[3], r[8]) == ("Advanced", "Editable", "(none)"), \
        f"{src}: unexpected C/D/I {(r[2], r[3], r[8])}"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} '{was}' -> '{NEW}'")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
