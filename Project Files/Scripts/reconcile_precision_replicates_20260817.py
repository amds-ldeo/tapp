#!/usr/bin/env python3
"""
Reconcile the precision/reproducibility pair and the replicate-count pair.

A. PRECISION — Solution MC alone used "Reproducibility" where the other 8 ICP-MS TAPPs use
   "Analytical Precision". Four fields become two:
     In-Run Isotope Ratio Reproducibility and Assessment Method
        -> Within-Session Analytical Precision and Assessment Method            (8 -> 9 TAPPs)
     Between-Session Reproducibility and Assessment Method
        -> Between-Session (Long-Term) Analytical Precision and Assessment Method (8 -> 9 TAPPs)

   The definitions already agreed. The MC "In-Run" field reads "Reproducibility of isotope ratio or
   d-value measurements WITHIN A SINGLE ANALYTICAL SESSION ... on REPLICATE ANALYSES of an isotopic
   standard ... run as an unknown during the session" — which is what `Within-Session Analytical
   Precision` asks for, word for word in substance.

   The surviving names are also the metrologically correct ones. This library is VIM3-aligned, and
   VIM3 reserves "reproducibility" for different-laboratory conditions; within-lab across-session
   work is intermediate precision, which the surviving Between-Session description already names.

   **The name was actively causing mis-extraction, which is the real reason to fix it.** "In-Run"
   reads as within one measurement, and two of the three extractions in that field record exactly
   that rather than what the definition asks for:
     Nowell x2  "Within-run errors quoted as 2SE of the mean, 2SE = 2SD/n^0.5 with n = 45"
                -> internal precision of a single measurement, not replicate analyses in a session.
                The paper DOES give the within-session quantity: "the uncertainties for the
                short-term reproducibility of standards analysed in a single analytical session ...
                are quoted as 2 standard deviations (2SD)".
     Ibanez-Mejia "Internal uncertainty determined from counting statistics" -> also internal; the
                paper's within-session quantity is the external reproducibility at 2 sigma of the
                spiked ZrNIST measurements from each run.
   All three cells are corrected here from the papers, which were read in full this session.

B. REPLICATES — `Number of Replicates per Sample` (Solution Q, SF) -> `Number of Replicates` (6 LA),
   and the TIERS reconciled across all 8.

   The bare name survives because "per Sample" is wrong for laser ablation, where replicates are per
   grain or per nominal location rather than per sample — the LA description says so already.

   Tiers diverged C=N/A, D=Basic (LA) against C=Basic, D=Read-Only (Solution), and both were honest
   about their own lineage: the LA extractions read "variable; 12-30 analyses per mineral phase" and
   "variable per run", while the Solution ones read "6 replicates (Table 1)" and "3 runs (Table 3)"
   straight out of a method table. Reconciled to **C=Advanced, D=Basic**: a procedure may register an
   intended replicate count where it has one, and the analysis must record what was actually done.
   Forcing C=Basic would make LA procedures declare a number they cannot know; forcing D=Read-Only
   would stop an analyst recording what was actually run.

NOT touched, though found by the same scan and clearly the same defect class: `Mass Cycles per
Replicate` (Solution Q) and `Number of Scans per Replicate` (Solution SF) carry near-identical
descriptions and are plainly one field. Outside the scope asked for; flagged instead.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"

WS = "Within-Session Analytical Precision and Assessment Method"
BS = "Between-Session (Long-Term) Analytical Precision and Assessment Method"
NR = "Number of Replicates"
RENAME = {"In-Run Isotope Ratio Reproducibility and Assessment Method": WS,
          "Between-Session Reproducibility and Assessment Method": BS,
          "Number of Replicates per Sample": NR}

WS_B = ("Precision of repeated measurements within a single analytical session and the method used to "
        "assess it. Report both the assessment method and the precision values. The assessment method "
        "must specify the reference material or standard measured, the number of replicates n, and the "
        "statistic reported (1s RSD, 2s RSD, 2SD, 2SE, 95% CI). Distinct from the internal precision of "
        "a single measurement, which derives from counting statistics over the cycles of that "
        "measurement rather than from repeated analyses.")
BS_B = ("Precision of measurements across multiple analytical sessions over weeks to months — long-term "
        "or intermediate precision — and the method used to assess it. Report both the assessment "
        "method and the precision values, specifying the reference material, the number of measurements "
        "and sessions, the time span covered, and the statistic reported. Long-term precision is "
        "normally poorer than within-session precision and is the figure a data user should carry when "
        "comparing results from different sessions.")
NR_B = ("Number of replicate measurements performed on the same sample, or on the same nominal location "
        "where the technique is spatially resolved. For spot analysis this is the number of individual "
        "spots per grain or location; for transects, the number of replicate lines; for mapping, the "
        "number of map acquisitions of the same area; for solution work, the number of discrete "
        "replicate measurements acquired per sample solution. The procedure registers an intended "
        "count where it has one; the analysis records the count actually acquired.")

# extraction corrections in Solution MC, from papers read in full this session
FIX = {
 ("Nowell+etal2008", WS): ("Short-term reproducibility of standards analysed in a single analytical "
   "session, quoted as 2 standard deviations (2SD). Distinct from the within-run internal error, which "
   "the paper quotes separately as 2SE of the mean, 2SE = 2SD/n^0.5 with n = 45 for the Neptune and "
   "n = 50 for the Nu Plasma analyses"),
 ("IbanezMejia+Tissot2020", WS): ("External reproducibility at 2 sigma of the spiked ZrNIST measurements "
   "from each run, adopted as the uncertainty on each determination and stated to be similar to or "
   "slightly larger than the internal counting-statistics uncertainty"),
}

JOBS = [
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v26.csv",              "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v27.csv"),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v26.csv",          "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v27.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v25.csv",            "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v26.csv"),
 ("LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v26.csv",        "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v27.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v23.csv",             "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v24.csv"),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v23.csv",         "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v24.csv"),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v30.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v31.csv"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v28.csv","Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v29.csv"),
 ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v27.csv","Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v28.csv"),
]

for src, dst in JOBS:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    hdr = rows[0]
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else len(hdr)
    acts = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        if r[0] in RENAME:
            acts.append(f"{r[0][:26]}... -> {RENAME[r[0]][:26]}...")
            r[0] = RENAME[r[0]]
            r[7] = DATE
        if r[0] == WS and (r[1] != WS_B or r[2] != "Basic"):
            r[1], r[2], r[3], r[7] = WS_B, "Basic", "Basic", DATE
            acts.append("WS def/tier")
        if r[0] == BS and r[1] != BS_B:
            r[1], r[2], r[3], r[7] = BS_B, "Advanced", "Basic", DATE
            acts.append("BS def/tier")
        if r[0] == NR and (r[1] != NR_B or (r[2], r[3]) != ("Advanced", "Basic")):
            r[1], r[2], r[3], r[7] = NR_B, "Advanced", "Basic", DATE
            acts.append("NR def/tier")
        # correct mis-scoped extractions
        for k in range(si + 1, len(hdr)):
            for (frag, field), val in FIX.items():
                if r[0] == field and frag in hdr[k] and (r[k] or '').strip() not in ('', 'N', 'N/A'):
                    if r[k] != val:
                        r[k] = val
                        acts.append(f"fixed {frag} cell")
    assert all(len(r) == len(hdr) for r in rows), f"{src}: ragged"
    if not acts:
        print(f"SKIP  {os.path.basename(src):36} nothing to change")
        continue
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} " + "; ".join(sorted(set(acts))))
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
