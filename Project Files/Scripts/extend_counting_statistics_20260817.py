#!/usr/bin/env python3
"""
Extend `Counting Statistics Error` from the 3 electron-beam TAPPs to the 9 ICP-MS TAPPs, and
harmonise its description across all 12.

ATTESTED IN ICP-MS — 6 of 37 extracted papers, and two of them report the predicted and the observed
value SIDE BY SIDE, which is what justifies keeping this separate from the internal-precision field
added earlier today:
  Mittlefehldt+2024 (LA-SF)  "theoretical 1s analytical precision (counting statistics plus
                             propagation of uncertainties) on the Fe/Mn ratio of pallasite olivine of
                             ~0.6%; standard deviations for each meteorite calculated from the
                             analyses range from 0.6 to 4.0%"
  Barnes+2025                "quadratic combination of internal counting statistics from the sample
                             measurement and external precision from standard replicates"
  IbanezMejia+Tissot2020     "the internal uncertainty determined from counting statistics"
  Willbold2005, Masuda2024, John+Adkins2010 also discuss it.

WHY BOTH FIELDS. `Counting Statistics Error` is the uncertainty PREDICTED from the counts — the
Poisson limit. `Internal (Within-Measurement) Analytical Precision` is the scatter OBSERVED across
the cycles of one measurement. Mittlefehldt quotes 0.6% predicted against 0.6-4.0% observed in the
same sentence; a single field cannot hold both, and the comparison between them is itself the
information — agreement means the measurement is shot-noise limited.

DESCRIPTION harmonised across all 12 TAPPs, because the incumbent text was electron-beam specific
("propagated from counting statistics on peak and background intensities") and would have been wrong
for ICP-MS. Leaving the ICP-MS copies different would create a fresh Rule 7.8.9 divergence.

**The boundary is stated WITHOUT naming the internal-precision field**, which exists in the 9 ICP-MS
TAPPs but not in the 3 electron-beam ones — a cross-reference to a field the reader does not have is
its own defect, the same trap avoided when that field was written. The reference runs the other way
instead: in the 9 ICP-MS TAPPs, where BOTH fields now exist, the internal-precision description is
updated to name `Counting Statistics Error` explicitly. That closes the loop where it is safe to and
nowhere else.

C=Advanced, D=Basic, E=Text (free), Keyed By `sample > sampling unit x reported property` — taken
unchanged from the electron-beam original, which is also the key given to the internal-precision field
this morning, since the two share a quantity shape.
PLACEMENT immediately before `Internal (Within-Measurement) Analytical Precision`, so predicted and
observed sit adjacent and the distinction is visible at the point of use rather than buried.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
CSE = "Counting Statistics Error"
INT = "Internal (Within-Measurement) Analytical Precision and Assessment Method"

CSE_B = ("Uncertainty predicted from counting statistics — the theoretical limit set by the Poisson "
         "distribution of the counts accumulated — for each reported quantity per analysis, with the "
         "sigma level stated. Derived from the counts on the analyte together with those on any "
         "background or blank subtracted from it. Distinct from the scatter actually observed within a "
         "measurement or between repeated measurements, which is recorded separately: where a "
         "procedure reports both, agreement indicates the measurement is shot-noise limited, and a "
         "larger observed scatter indicates a further source of variance.")
CSE_F_ICP = ("e.g., '2SE predicted from counting statistics over 45 cycles' | '~0.6% (1 sigma), "
             "counting statistics plus propagated uncertainties' | 'N/A'")

INT_B_NEW = ("Precision of a single measurement, derived from the scatter of the cycles, sweeps or "
             "integrations that make it up, together with the method used to assess it. State the "
             "statistic (2SE, 2SD, 1s RSD), the number of cycles it is computed over, and the reported "
             "quantity it applies to. This is the finest of the three precision levels the library "
             "records, below within-session and between-session precision: it describes the "
             "repeatability of one analysis rather than agreement between analyses, and is normally "
             "the smallest of the three. Distinct from Counting Statistics Error, which records the "
             "uncertainty predicted from the counts rather than the scatter observed; where a "
             "procedure reports both, record the observed value here and the predicted value there.")

LIT = {
 "Mittlefehldt": ("Theoretical 1 sigma analytical precision from counting statistics plus propagation "
   "of uncertainties, ~0.6% on the Fe/Mn ratio of pallasite olivine; the observed standard deviations "
   "per meteorite range from 0.6 to 4.0%"),
 "IbanezMejia+Tissot2020": ("Internal uncertainty determined from counting statistics, used as the "
   "comparison against the external reproducibility adopted per determination; value not tabulated"),
}

HARMONISE = [   # electron-beam TAPPs: description only
 ("EPMA/EPMA_TAPP_v24.csv", "EPMA/EPMA_TAPP_v25.csv"),
 ("SEM/SEM_TAPP_v21.csv", "SEM/SEM_TAPP_v22.csv"),
 ("SEM/SEM_Composition_TAPP_v21.csv", "SEM/SEM_Composition_TAPP_v22.csv"),
]
EXTEND = [      # ICP-MS TAPPs: insert the field, and update the internal-precision description
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v28.csv", "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v29.csv"),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v28.csv", "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v29.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v27.csv", "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v28.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v28.csv", "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v29.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v25.csv", "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v26.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v25.csv", "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v26.csv"),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v32.csv", "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v33.csv"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v30.csv", "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v31.csv"),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v29.csv", "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v30.csv"),
]

def write(dst, rows):
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

for src, dst in HARMONISE:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    hit = [r for r in rows[1:] if r and r[0] == CSE]
    assert len(hit) == 1, f"{src}: {len(hit)} rows"
    hit[0][1], hit[0][7] = CSE_B, DATE
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):34} description harmonised")
    write(dst, rows)

for src, dst in EXTEND:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    hdr = rows[0]; ncol = len(hdr)
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else ncol
    assert not any(r and r[0] == CSE for r in rows[1:]), f"{src}: already present"
    anchor = next(i for i, r in enumerate(rows) if r and r[0] == INT)
    rows[anchor][1], rows[anchor][7] = INT_B_NEW, DATE
    new = [CSE, CSE_B, "Advanced", "Basic", "Text (free)", CSE_F_ICP, "", DATE,
           "sample > sampling unit x reported property"] + [""] * (ncol - 9)
    for k in range(9, si):
        new[k] = "Y"
    filled = 0
    for k in range(si + 1, ncol):
        new[k] = "N"
        for frag, val in LIT.items():
            if frag in hdr[k]:
                new[k] = val; filled += 1
    rows.insert(anchor, new)
    assert all(len(r) == ncol for r in rows), f"{src}: ragged"
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):34} inserted at {anchor}, "
          f"{filled} lit cell(s), internal-precision description updated")
    write(dst, rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
