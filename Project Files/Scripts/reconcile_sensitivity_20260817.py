#!/usr/bin/env python3
"""
Reconcile `Sensitivity as Useful Yield` (6 LA TAPPs) with `Instrument Sensitivity` (3 Solution TAPPs)
into a single `Instrument Sensitivity` across all 9 ICP-MS TAPPs.

This one was genuinely closer than the make-up gas case, because the two fields hold physically
DIFFERENT quantities rather than the same quantity under two names:
  useful yield  = percentage of sampled atoms detected as ions — dimensionless efficiency
  sensitivity   = detected signal per unit concentration or mass — V/ppm, cps/ppb, counts/pg
You cannot convert one into the other without knowing how much material was consumed, which is
exactly why Horstwood et al. 2016 recommend useful yield for laser ablation: cps/ppb is not
comparable between labs when spot size, fluence and repetition rate differ.

WHAT THE EVIDENCE SHOWS
  signal-per-concentration   13 filled literature cells across the 3 Solution TAPPs
                             (Ibanez-Mejia "572 V/ppm of total Zr"; Nowell "~50 V for a 1 ug/ml Os
                             solution"; Misra "~2.5 x 10^6 cps/ppb on 115In"; Makishima per-isotope
                             "count pg-1 ml"; and others)
  useful yield               0 filled cells in 28 LA literature columns, and 0 in the Horstwood test
                             TAPP that originated the field. An anchored scan of all 28 PDFs in the
                             LA folders finds it reported ONCE: Masuda et al. 2024, "the achieved
                             useful yield of analytes is about 0.1%". Tang et al. 2014's "ion yields
                             (cps/spot diameter squared)" and Chernonozhkin et al. 2024's "ablation
                             yield" are different quantities and do not count.

So the LA field encodes a community RECOMMENDATION — it came from Horstwood et al. 2016 via the
Horstwood comparison TAPP, not from a survey of reported practice — and practice has followed it
once in ten years of papers. That is a real finding, and the reason to merge rather than retire: the
recommendation is worth keeping, but it does not need a field of its own to survive.

RESOLUTION  one field, `Instrument Sensitivity`, whose compound data type carries both expressions.
  E  `Numeric + unit / Text` (the Solution form) — holds "572 V/ppm" and "0.1% useful yield" alike;
     the LA `Numeric (%)` could hold only the expression nobody reports.
  I  `channel` (the Solution form), replacing LA's `analyte`. Sensitivity is reported per isotope —
     Makishima tabulates it per isotope and Misra quotes it on 115In — and Rule 7.2's test settles it:
     substituting a different isotope of the same element changes the number, because it depends on
     isotopic abundance. Safe under Rule 7.4c: every LA TAPP retains 2-3 other `analyte` consumers
     (`Per-Analyte Calibration Strategy`, `Monitored Masses`, `Primary Calibration Standard Name`),
     so the `Analyte` definer is not orphaned. Safe under 7.4a: all six define `channel`, via
     `Monitored Masses` in the Q and SF variants and `Collector Configuration` in the MC ones.
  B  rewritten to name BOTH expressions and to keep Horstwood's rationale for preferring useful yield
     where material consumption varies. The recommendation moves inside the surviving field.
  F  per TAPP, extended so each lineage now shows both forms — the LA examples keep the Horstwood
     citation and gain Masuda's measured value.

C=N/A and D=Advanced already agreed on both sides.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
NEW = "Instrument Sensitivity"
OLD = "Sensitivity as Useful Yield"

NEW_B = ("Instrument sensitivity achieved in the session, with the isotope or channel it was measured "
         "on and the conditions it applies to. May be expressed either as detected signal per unit "
         "concentration or per unit mass of analyte delivered — counts per second per ppb, volts per "
         "ppm, counts per picogram — or as useful yield, the percentage of sampled atoms ultimately "
         "detected as ions, with the method used to derive it cited. Useful yield is the more "
         "comparable of the two wherever the amount of material consumed varies between procedures, "
         "as it does with spot size, fluence and repetition rate. Records what the instrument actually "
         "delivered; a sensitivity the procedure requires before analyses may begin belongs with the "
         "tuning acceptance criteria.")
NEW_E = "Numeric + unit / Text"
LA_F = ("e.g., '0.42% useful yield (U, method of Horstwood et al. 2016)' | '0.1% useful yield "
        "(analytes, msfs-LA-ICP-MS)' | '1.2 x 10^6 cps/ppb on 115In' | 'N/A'")
SOL_F = ("e.g., '572 V/ppm total Zr' | '~2.5 x 10^6 cps/ppb on 115In' | '0.04 count pg-1 ml (111Cd)' "
         "| '0.1% useful yield' | 'N/A'")

JOBS = [
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v25.csv",              "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v26.csv",              "LA"),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v25.csv",          "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v26.csv",          "LA"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v24.csv",            "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v25.csv",            "LA"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v25.csv",        "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v26.csv",        "LA"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v22.csv",             "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v23.csv",             "LA"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v22.csv",         "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v23.csv",         "LA"),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v29.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v30.csv",  "SOL"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v27.csv","Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v28.csv","SOL"),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v26.csv","Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v27.csv","SOL"),
]

for src, dst, fam in JOBS:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    want = OLD if fam == "LA" else NEW
    hit = [r for r in rows[1:] if r and r[0] == want]
    assert len(hit) == 1, f"{src}: {len(hit)} rows named {want}"
    r = hit[0]
    was = (r[0], r[4], r[8])
    r[0], r[1], r[4], r[5], r[8], r[7] = NEW, NEW_B, NEW_E, (LA_F if fam == "LA" else SOL_F), "channel", DATE
    assert (r[2], r[3]) == ("N/A", "Advanced"), f"{src}: unexpected C/D {(r[2], r[3])}"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} {was[0][:28]:30} E={was[1]:16} I={was[2]}")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
