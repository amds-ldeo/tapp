#!/usr/bin/env python3
"""
patch_lamcicpms_zhang2022_reextract_20260909.py
------------------------------------------------
Phase 3 completion for LA-MC-ICP-MS: re-extract the Zhang et al. 2022 column.

  target : LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v70.csv -> LA-MC-ICPMS_TAPP_v71.csv
  column : index 14 — "Zhang et al. 2022 (At. Spectrosc. 43) ... Line scan (transect)"
  source : LA-MC-ICP-MS/Seed Papers/Zhang et al 2022 - in situ Rb-Sr LA-MC-ICP-MS.pdf
           (10 pages; read in full in this session via pdfplumber, per the Source Rule)

Two jobs, both outstanding since the column was transferred on 2026-08-10.

(1) TARGET SPECIES / COLLECTOR CONFIGURATION MIS-ROUTING.
    patch_lamcicpms_zhang2022_litassess_20260810.py transferred the source TAPP's
    "Analyte" cell verbatim and recorded in its own docstring:

        "the source 'Analyte' cell is a valid name AND description match and transfers
         verbatim, but its content is the paper's Table 1 'Cup-configuration' row. v1
         has a dedicated 'Collector Configuration' field that this content would also
         populate. NOT filled here — that is re-extraction, not transfer. Reported as
         an immediate Phase 3 follow-up."

    That follow-up was never done, and "Analyte" was renamed "Target Species" on
    2026-09-01, so the cell now reads as a target-species list when it is a cup map.
    This matters structurally: Target Species is `defines: target species`, so the
    domain every target-species-keyed field points into was a list of collector
    positions. Collector Configuration (`defines: channel per target species`) was
    blank, so the channel domain was unestablished at the same time.

    Table 1, p.2 (verbatim):
        Cup-configuration  L4 (83Kr), L3 (167Er++), L2 (84Sr), L1 (85Rb), C (86Sr),
                           H1 (173Yb++), H2 (87Sr), and H3 (88Sr).
    Body text, p.2:
        "The Faraday collector configuration of the mass system was composed of an
         array from L4 to H3 to monitor Kr, Rb, Er, Yb, and Sr (Table 1)."

    The target species are Rb and Sr — the paper determines 87Sr/86Sr and 87Rb/86Sr.
    Kr, Er and Yb are monitored solely to correct interferences (83Kr for the gas
    background; 167Er++ and 173Yb++ to compute the doubly-charged corrections). Under
    Rule 7.3.1 those are ORPHAN channel members with no parent target species, which
    is exactly why the cup map cannot serve as the target-species list.

(2) 53 BLANK CELLS.
    references/lit_assessment.md: "Never leave a cell blank. Blank is ambiguous."
    Every blank is resolved here to a value, `N` (applicable, not stated) or `N/A`
    (concept does not apply). Each value below carries its source location.

    The largest N/A block is the collision/reaction cell group (7 fields). The paper
    is explicit that this instrument has no cell — p.1: "During the measurements by
    traditional (MC-)ICP-MS without the reaction/collision cell, the 87Rb interference
    is corrected by monitoring 85Rb"; p.8-9: "Compared to ICP-MS/MS ... or MC-ICP-MS
    with collision cell, the present method cannot measure 87Sr/86Sr in the Rb-rich
    sample". CRC Configuration is therefore `Not installed`, a listed vocabulary term,
    and the dependent gas fields are N/A per their own descriptions.

    The double-spike group (3 fields) and isotope dilution are N/A: this is an in situ
    LA procedure with external calibration and internal normalisation, no spike.

    Procedural Blank Level is N/A rather than N: a procedural blank is a sample-
    preparation concept and there is no chemistry here. The on-peak gas background is
    recorded under Blank / Background Correction Method, which is already filled.

    Baseline Measurement Approach IS filled, and is not a duplicate of Blank /
    Background Correction Method. That field's own description lists three approaches,
    the third being "collecting a defined number of laser-off cycles at the start of
    the same block. State which, and how many cycles or how long." Zhang states
    exactly that (30 laser-off cycles); the Blank field records the correction applied
    to them. Distinct questions, distinct answers.

NOT DONE HERE (reported instead):
  * Analytical Mode's Column F wraps each value in literal single quotes
    ('Spot' | 'Transect' | ...). No other controlled list in this TAPP does. The same
    defect exists in EPMA_TAPP_v63. Column F is module/TAPP overlay, not literature,
    and fixing it library-wide is a separate change with its own scope.
  * Table 1 says "Laser type Yb:YAG femtosecond laser" while p.2 body text says
    "Yb: KGW femtosecond laser amplifier (PHAROS)". The TAPP already records Yb:KGW
    from the body text. The paper contradicts itself; not resolvable from the source,
    left as is and noted in the report.

Column H (Last Update) is NOT touched: re-extracting a literature column is not an
edit to any field definition. Group header rows keep `N`.
"""

import csv, os, sys

SRC = "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v70.csv"
DST = "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v71.csv"
COL = 14

# ---- (1) the mis-routing fix ------------------------------------------------
REROUTE = {
 "Target Species":
   "Rb, Sr (the paper determines ⁸⁷Sr/⁸⁶Sr and ⁸⁷Rb/⁸⁶Sr; p.2 'to monitor Kr, Rb, Er, "
   "Yb, and Sr' names Kr, Er and Yb as monitored, not determined — they carry the "
   "interference corrections and are orphan channel members with no parent species)",
 "Collector Configuration":
   "L4=⁸³Kr (gas background monitor, no target species); L3=¹⁶⁷Er²⁺ (interference monitor, "
   "no target species); L2=⁸⁴Sr (Sr); L1=⁸⁵Rb (Rb); C=⁸⁶Sr (Sr); H1=¹⁷³Yb²⁺ (interference "
   "monitor, no target species); H2=⁸⁷Sr (Sr); H3=⁸⁸Sr (Sr). Static multi-collection, one "
   "configuration throughout (Table 1 'Cup-configuration', p.2; array spans L4–H3, p.2)",
}

# ---- (2) the 53 blanks ------------------------------------------------------
FILL = {
 # 1. Procedure Identification
 "Session Identifier": "N",
 # 2. Samples
 "Sampling Unit":
   "Analysis point — one individual run, a continuous line scan within a single mineral "
   "grain or glass; the paper counts and reports 'individual runs' (36 and 6 for NWA 10597; "
   "94 and 21 for NWA 6950), pp.7-8",
 "Sampling Unit Selection Criteria":
   "Random selection among the target phases — 'The plagioclases, pyroxenes, and ilmenites "
   "in NWA 10597 were measured randomly' (p.7); target phases are plagioclase, pyroxene, "
   "ilmenite and glass (abstract; p.7-8)",
 "Pre-Analysis Imaging and Screening": "N",
 # 3. Instrument & Software
 "Instrument Manufacturer": "Thermo Fisher Scientific",
 "Instrument Serial Number or Lab Identifier": "N",
 "Sampler and Skimmer Cone Material":
   "N (cone types stated as 'X skimmer cone + Jet sample cone', Table 1; materials not stated)",
 "Torch Depth":
   "N (torch position was optimised on NIST 610, p.3, but no value is given)",
 "Torch Type": "N",
 "Collision/Reaction Cell (CRC) Configuration":
   "Not installed — 'traditional (MC-)ICP-MS without the reaction/collision cell' (p.1); "
   "contrasted against 'MC-ICP-MS with collision cell' in the conclusion (pp.8-9)",
 "Sample Introduction":
   "He filled into the two-volume ablation cell; Ar mixed into the sample-out line downstream "
   "of the ablation chamber before the torch; a signal-smoothing device downstream of the "
   "sample cell (Hu et al. 2015) that 'significantly reduced the short-term variability of the "
   "signal'; 12 ml min⁻¹ N₂ added to the carrier gas via a simple Y connector behind the "
   "signal-smoothing device (p.3)",
 "Faraday Cup Array Configuration":
   "Nine Faraday cups fitted with 10¹¹ Ω resistors, plus seven fixed electron multiplier ion "
   "counters; the Faraday collector array spans L4 to H3 (p.2)",
 "Faraday Cup Amplifier Resistor Values":
   "10¹¹ Ω on all nine Faraday cups (p.2)",
 "Faraday Cup Gain Calibration Method": "N",
 # 4. Measurement Information
 "Analytical Mode": "Transect",
 "Spot Diameter (Measured)":
   "N (ablation craters shown in Fig. S2 but no measured diameter is stated)",
 "Ablation Pit Depth and Ablation Rate": "N",
 "Instrument Sensitivity":
   "N (tuning optimised on NIST 610 'for maximum sensitivity', p.3, but no sensitivity value "
   "is stated)",
 "Doubly-Charged Species Monitor":
   "N (¹⁶⁷Er²⁺ and ¹⁷³Yb²⁺ are monitored to correct doubly-charged interferences, p.4, but no "
   "M²⁺ tuning monitor or production ratio is stated)",
 "Doubly-Charged Species Production": "N",
 "Monitored Masses":
   "⁸⁴Sr, ⁸⁶Sr, ⁸⁷Sr, ⁸⁸Sr (Sr); ⁸⁵Rb (Rb); ⁸³Kr, ¹⁶⁷Er²⁺, ¹⁷³Yb²⁺ (monitors, no target "
   "species) — Table 1 'Cup-configuration', p.2",
 "Reported Variables and Units":
   "⁸⁷Sr/⁸⁶Sr (dimensionless ratio); ⁸⁷Rb/⁸⁶Sr (dimensionless ratio); Rb–Sr isochron age (Ma); "
   "initial ⁸⁷Sr/⁸⁶Sr (dimensionless ratio) — Tables 2 and 3",
 "Mass Resolution Assignment":
   "Low resolution for all eight monitored masses — 'the mass spectrometer was operated in low "
   "mass resolution mode' (p.3); Table 1 'Instrument resolution ~ 400 (low mode)'. Single "
   "acquisition pass, so one assignment applies throughout",
 "Ion Counter Dead Time": "N",
 "Collision Gas Type": "N/A",
 "Collision Gas Flow Rate": "N/A",
 "Cell Exit Discrimination Voltage": "N/A",
 "Reaction Gas Type": "N/A",
 "Reaction Gas Flow Rate": "N/A",
 "Number of Blocks per Measurement": "1 (Table 1, 'Block number 1'; p.3 'one block of 120 cycles')",
 "Number of Cycles per Block": "120 (Table 1, 'Cycles of each block 120'; p.3)",
 "Baseline Measurement Approach":
   "Laser-off cycles at the start of the same block — 'the first 30 cycles for background "
   "collection (no laser ablation) and the remaining 90 cycles for signal collection' (p.3); "
   "30 cycles x 0.524 s ≈ 15.7 s",
 "Peak Flatness Method and Threshold":
   "Optimised during tuning on NIST 610 by adjusting the He and Ar gas flow rates, torch "
   "position, RF power and source lens settings 'for maximum sensitivity and optimum peak "
   "flatness' (p.3); no numerical acceptance threshold is stated",
 "Peak Flatness": "N",
 "Collision/Reaction Gas Mixture Ratio": "N/A",
 "Reaction Product Ion / Mass-Shift Transition": "N/A",
 "Acquisition Pass":
   "Single pass — 'The routine data acquisition consisted of one block of 120 cycles (0.524 s "
   "integration time per cycle), with the first 30 cycles for background collection (no laser "
   "ablation) and the remaining 90 cycles for signal collection' (p.3). No second traversal or "
   "alternate configuration is described",
 "Number of Acquisition Passes": "1",
 # 5. Data Processing
 "Calibration Strategy per Target Species":
   "Sr: internal normalisation — ⁸⁸Sr/⁸⁶Sr = 8.37520933 with the exponential law corrects mass "
   "fractionation of ⁸⁷Sr/⁸⁶Sr (p.4). Rb: external calibration — a series of reference glasses "
   "provides an average correction factor for Rb/Sr elemental fractionation, applied to samples "
   "and reference materials; ⁸⁷Rb/⁸⁶Sr computed from the ⁸⁵Rb and ⁸⁸Sr signals with ⁸⁷Rb/⁸⁵Rb = "
   "0.385706 and ⁸⁶Sr/⁸⁸Sr = 0.119351 (p.4)",
 "Mass Bias Correction Strategy":
   "Internal normalisation to an assumed ⁸⁸Sr/⁸⁶Sr = 8.37520933 applying the exponential law "
   "(Russell et al. 1978), after interference correction (p.4). The ⁸⁷Rb isobaric correction on "
   "⁸⁷Sr uses the ⁸⁵Rb signal and a user-specified ⁸⁷Rb/⁸⁵Rb, also via the exponential law, with "
   "that ratio calibrated by measuring reference materials of known ⁸⁷Sr/⁸⁶Sr (p.4)",
 "Uncertainty Level":
   "2SD for reference-material mean values (Table 2); within-run repeatability quoted as U_SD "
   "and U_SE at 95% confidence (Eqs. 1-2, p.5); isochron ages quoted with IsoplotR and Monte "
   "Carlo uncertainties (Table 3)",
 "Isotope Dilution Data Reduction Method": "N/A",
 "Calibration Factor and Determination Method":
   "External calibration factor for Rb/Sr elemental fractionation: 'A series of reference "
   "glasses was analyzed to provide an average correction factor. Then the average factor was "
   "used for the samples and reference materials' (p.4). Applies to ⁸⁷Rb/⁸⁶Sr only; determined "
   "with ISO-Compass software. Factor value not stated",
 "Procedural Blank Level":
   "N/A (in situ laser ablation; no sample-preparation chemistry. The on-peak gas background is "
   "recorded under Blank / Background Correction Method)",
 "Analysis Inclusion and Rejection Criteria":
   "Cycle level: the cycles at the beginning and end of ablation are discarded, leaving 60-70 of "
   "the 90 ablation cycles (p.3). Technical criteria (p.5): (a) data with ⁸⁷Rb/⁸⁶Sr > 1 deleted, "
   "the Rb interference correction being invalid above that; (b) data with ⁸⁸Sr signal < 0.2 V "
   "discarded for poor ⁸⁷Sr/⁸⁶Sr precision. Run level: runs with stable signals go to the Normal "
   "group, runs with large ⁸⁷Rb/⁸⁶Sr variation to the SUIA group (NWA 10597: 36 Normal, 6 SUIA; "
   "NWA 6950: 94 Normal, 21 SUIA). For NWA 6950 only data with initial ⁸⁷Sr/⁸⁶Sr of 0.7025-0.7035 "
   "were kept, those at 0.7072-0.7076 being from glasses and pyroxenes in or around black veins "
   "and interpreted as later-altered (p.8)",
 "Mass Fractionation Law": "Exponential",
 "Internal Normalization Element and Isotope Ratio":
   "Sr, ⁸⁸Sr/⁸⁶Sr = 8.37520933, exponential law (Russell et al. 1978), p.4",
 "Double-Spike Isotope Pair": "N/A",
 "Double-Spike Mixing Ratio": "N/A",
 "Double-Spike Inversion Algorithm": "N/A",
 "Constants and Reference Values Used":
   "⁸⁷Rb decay constant 1.393 ± 0.004 x 10⁻¹¹ yr⁻¹ (Nebel et al. 2011), p.1; ⁸⁸Sr/⁸⁶Sr = "
   "8.37520933 for mass fractionation correction (p.4); ⁸⁷Rb/⁸⁵Rb = 0.385706 and ⁸⁶Sr/⁸⁸Sr = "
   "0.119351 for the ⁸⁷Rb/⁸⁶Sr calculation (p.4); natural ⁸⁷Rb/⁸⁵Rb of 0.38571 cited for the "
   "interference-correction principle (p.1)",
 # 6. Quality Control & Uncertainty
 "Goodness-of-Fit or Dispersion Statistic":
   "MSWD from IsoplotR (Table 3): NWA 10597 Normal group 24, SUIA group 1.5; NWA 6950 Normal "
   "group 21, SUIA group 1.5. The high Normal-group values are attributed to large dispersion, "
   "'especially for the data with ⁸⁷Rb/⁸⁶Sr ranging from 0.05 to 0.15' measured in pyroxenes (p.7)",
}

def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src, dst = os.path.join(root, SRC), os.path.join(root, DST)
    rows = list(csv.reader(open(src, newline='', encoding='utf-8-sig')))
    dry = '--apply' not in sys.argv

    seen, changed = set(), 0
    for x in rows[1:]:
        if not x or not x[0].strip(): continue
        name = x[0].strip()
        while len(x) <= COL: x.append('')
        if name in REROUTE:
            print(f"  REROUTE {name}\n     was: {x[COL][:95]}\n     now: {REROUTE[name][:95]}")
            x[COL] = REROUTE[name]; seen.add(name); changed += 1
        elif name in FILL:
            if x[COL].strip():
                print(f"  !! {name} is not blank ({x[COL][:40]!r}) — refusing"); sys.exit(1)
            x[COL] = FILL[name]; seen.add(name); changed += 1

    missing = (set(REROUTE) | set(FILL)) - seen
    if missing:
        print("  !! field names not found in TAPP:", sorted(missing)); sys.exit(1)

    blanks = [x[0].strip() for x in rows[1:]
              if x and x[0].strip() and len(x) > COL and not x[COL].strip()]
    print(f"\n  cells written : {changed}")
    print(f"  blanks left   : {len(blanks)} {blanks if blanks else ''}")
    if blanks: print("  !! lit_assessment.md forbids blank cells"); sys.exit(1)

    if dry:
        print("\n  DRY RUN — rerun with --apply to write"); return
    with open(dst, 'w', newline='', encoding='utf-8') as fh:
        csv.writer(fh).writerows(rows)
    print(f"\n  wrote {DST}")

if __name__ == '__main__':
    main()
