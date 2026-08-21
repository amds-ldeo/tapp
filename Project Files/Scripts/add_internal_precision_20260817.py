#!/usr/bin/env python3
"""
Add `Internal (Within-Measurement) Analytical Precision and Assessment Method` to all 9 ICP-MS TAPPs.

THE GAP. Isotope work reports precision at three levels; the library had fields for two:
  1. internal        within ONE measurement, over its cycles or sweeps        <- missing
  2. within-session  across replicate analyses in one session                 <- exists
  3. between-session across sessions, weeks to months                         <- exists
Level 1 was being written into the within-session field for want of anywhere else, which is what made
the "In-Run" mis-extractions of 2026-08-17 so easy to miss: the cells looked plausibly filled.

ATTESTED across both lineages and all three analyser families:
  Nowell+2008   (Sol MC)  "Within run errors for individual analyses are quoted as 2 standard errors
                          of the mean (2SE = 2SD/n^0.5; where n=45 for the Neptune analyses and n=50
                          for the Nu Plasma analyses)"
  IbanezMejia   (Sol MC)  "the internal uncertainty determined from counting statistics"
  Desem+2022    (Sol SF)  "typical internal precision (2se) of +/-0.001-0.002 for 206Pb/204Pb and
                          +/-0.003-0.005 for 208Pb/204Pb"
  Wu+2023       (LA-Q)    "The uncertainties (2SE) of single-spot ages were ~2.6%"
  LA-MC                   "Standard error (USE = SE at 95% confidence) ... per individual run"

RULE 6.1 CONDITION 2 — checked, and it is close. `Counting Statistics Error` already exists in EPMA,
SEM and SEM_Composition: "1-sigma uncertainty propagated from counting statistics on peak and
background intensities, for each reported concentration variable per analysis." That is the same
LEVEL — one measurement — but a different QUANTITY: it is the uncertainty PREDICTED from counts,
whereas internal precision as reported in ICP-MS is usually the OBSERVED scatter of the cycles making
up the measurement. The two are not interchangeable, and Ibanez-Mejia quotes both in one sentence and
compares them — "similar in magnitude or slightly larger than the internal uncertainty determined
from counting statistics" — which a single field could not hold.

The description therefore draws the boundary WITHOUT naming `Counting Statistics Error`, since that
field is not present in the ICP-MS TAPPs and a cross-reference to a field the reader does not have is
its own defect.

KEY `sample > sampling unit x reported property`, matching `Counting Statistics Error` exactly — the
same quantity shape deserves the same key, and it is the form Rule 7.3 documents for
containment-then-cross-product: within each sample, for each analysis, one precision per reported
quantity. Rule 7.4a holds in all 9: `Sample Name`, `Sampling Unit` and `Reported Variables and Units`
are mandatory everywhere under Rules 13, 9 and 8.

TIERS C=Advanced, D=Basic, matching `Between-Session (Long-Term)`. C=Basic would force every ICP-MS
procedure to declare an internal precision, including trace-element work that does not separate it.
PLACEMENT immediately before `Within-Session Analytical Precision`, so the three levels read as a
ladder in Group 6.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
NEW = "Internal (Within-Measurement) Analytical Precision and Assessment Method"
ANCHOR = "Within-Session Analytical Precision and Assessment Method"

NEW_B = ("Precision of a single measurement, derived from the scatter of the cycles, sweeps or "
         "integrations that make it up, together with the method used to assess it. State the "
         "statistic (2SE, 2SD, 1s RSD), the number of cycles it is computed over, and the reported "
         "quantity it applies to. This is the finest of the three precision levels the library "
         "records, below within-session and between-session precision: it describes the repeatability "
         "of one analysis rather than agreement between analyses, and is normally the smallest of the "
         "three. Distinct from an uncertainty predicted from counting statistics, which some "
         "procedures quote alongside it for comparison; where both are reported, record the observed "
         "value here and the predicted one with the uncertainty propagation.")
NEW_F = ("e.g., '2SE = 2SD/sqrt(n), n = 45 cycles' | '+/-0.001-0.002 (2SE) on 206Pb/204Pb' | "
         "'~2.6% (2SE) on single-spot ages' | 'N/A'")

LIT = {
 "Nowell+etal2008 | Neptune": ("Within-run errors for individual analyses quoted as 2 standard errors "
   "of the mean, 2SE = 2SD/n^0.5, with n = 45 cycles"),
 "Nowell+etal2008 | Nu Plasma": ("Within-run errors for individual analyses quoted as 2 standard errors "
   "of the mean, 2SE = 2SD/n^0.5, with n = 50 cycles"),
 "IbanezMejia+Tissot2020": ("Internal uncertainty determined from counting statistics; stated to be "
   "similar in magnitude to or slightly smaller than the external reproducibility adopted per determination"),
 "Desem+etal2022": ("A single analysis of 30-40 10-s integrations gives typical internal precision "
   "(2SE) of +/-0.001-0.002 for 206Pb/204Pb and +/-0.003-0.005 for 208Pb/204Pb"),
 "Wu+etal2023": "Uncertainties (2SE) of single-spot ages were ~2.6%",
}

JOBS = [
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v27.csv:LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v28.csv",
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v27.csv:LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v28.csv",
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v26.csv:LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v27.csv",
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v27.csv:LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v28.csv",
 "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v24.csv:LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v25.csv",
 "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v24.csv:LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v25.csv",
 "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v31.csv:Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v32.csv",
 "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v29.csv:Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v30.csv",
 "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v28.csv:Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v29.csv",
]

for job in JOBS:
    src, dst = job.split(":")
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    hdr = rows[0]; ncol = len(hdr)
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else ncol
    assert not any(r and r[0] == NEW for r in rows[1:]), f"{src}: already present"
    anchor = next(i for i, r in enumerate(rows) if r and r[0] == ANCHOR)
    new = [NEW, NEW_B, "Advanced", "Basic", "Text (free)", NEW_F, "", DATE,
           "sample > sampling unit x reported property"]
    new += [""] * (ncol - len(new))
    for k in range(9, si):
        new[k] = "Y"
    filled = 0
    for k in range(si + 1, ncol):
        new[k] = "N"
        for frag, val in LIT.items():
            if all(t in hdr[k] for t in frag.split(" | ")):
                new[k] = val; filled += 1
    rows.insert(anchor, new)
    assert all(len(r) == ncol for r in rows), f"{src}: ragged"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} inserted at row {anchor}, "
          f"{filled} literature cell(s) filled")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
