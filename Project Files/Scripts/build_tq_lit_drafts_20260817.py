#!/usr/bin/env python3
"""
Phase 3 for the three TQ-ICP-MS papers in LA-Q-ICP-MS/TQ literature assessment/.

They do not all belong to one TAPP:
  Wu et al. 2023          LASER ABLATION  -> LA-Q-ICP-MS      1 column
  Gil-Diaz et al. 2020    SOLUTION        -> Solution Q-ICP-MS 3 columns (three instruments)
  Lopez Garcia et al. 2026 SOLUTION       -> Solution Q-ICP-MS 1 column

Gil-Diaz uses three instruments under different conditions and in different laboratories, which
lit_assessment.md makes three columns ("One column per instrument is the default when two
instruments are used in the same paper, even if conditions are partially shared"):
  Agilent 8800 QQQ  (Basel)  - Te and Se by oxygen-shift
  Thermo iCAP-TQ             - particulate Te, KED for 126Te and O2 mass-shift for 125Te
  Thermo XSeries 2  (KIT)    - dissolved Se, CCT mode, single quadrupole

SOURCES  [W] Wu+2023 JAAS 38,1285  ·  [G] Gil-Diaz+2020 Chem Geol 532,119370
         [L] Lopez Garcia+2026 M&PS 61,580
Conventions: N = applicable but not stated; N/A = concept does not apply; never blank.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv

LAQ_SRC = "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v22.csv"
SOLQ_SRC = "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v26.csv"

LAQ_COLS = ["Wu+etal2023 | Analyte G2 + iCAP TQ ICP-MS/MS | IGGCAS"]
SOLQ_COLS = [
 "GilDiaz+etal2020 | Agilent 8800 QQQ | FHNW Basel",
 "GilDiaz+etal2020 | Thermo iCAP-TQ | lab not stated",
 "GilDiaz+etal2020 | Thermo XSeries 2 | KIT Karlsruhe",
 "LopezGarcia+etal2026 | Thermo iCAP TQ | Institute of Science Tokyo",
]
G8, GT, GX, LG = 0, 1, 2, 3

W = {}   # LA-Q, single column
def w(f, v): W[f] = [v]

S = {}   # Solution Q, four columns
def s(f, d): S[f] = d

# ------------------------------------------------------------------ Wu 2023 (LA-Q)
w("Technique", "LA-ICP-MS/MS (LA-Q-ICP-MS, triple-quadrupole platform)")
w("Laboratory", "Institute of Geology and Geophysics, Chinese Academy of Sciences (IGGCAS)")
w("Target Material", "Xenotime, apatite and garnet — accessory and metamorphic minerals for in situ Lu-Hf geochronology")
w("Sample Name", "Xenotime XN02, MG-1, BS-1, XENOA, M1567; apatite Otter Lake, NW-1, MAP-3; two metamorphic garnets; NIST SRM 610")
w("Sampling Unit", "Laser spot — 246 spot analyses on XN02 alone; spot diameters 50-150 um depending on Lu and Hf contents")
w("Sample Preparation Method", "Megacrysts and single crystals; XN02 megacrysts from the Datas alluvial deposits, SE Brazil")
w("Instrument Manufacturer", "Thermo Fisher Scientific")
w("Instrument Model", "iCap TQ ICP-MS/MS (Thermo Fisher Scientific, Bremen, Germany)")
w("ICP-MS Type", "Triple quadrupole (ICP-MS/MS) — operated in both single-quadrupole (SQ) and triple-quadrupole (TQ) modes")
w("Laser Manufacturer & Model", "Photon Machines Analyte G2 (Teledyne CETAC, Omaha, USA)")
w("Laser Wavelength and Type", "193 nm")
w("Laser Pulse Duration", "4-5 ns")
w("Laser Fluence (Energy Density)", "4 J cm-2")
w("Laser Repetition Rate", "10 Hz")
w("Spot Diameter (Measured)", "50, 90, 150 um")
w("Ablation Cell Type", "HelEx ablation cell")
w("Carrier Gas and Flow Rate", "He, 900 mL min-1 ablation gas flow")
w("Plasma / Make-up Gas Addition", "N2 enhancement gas, 4.0 mL min-1, added to the carrier gas after the sample chamber to enhance sensitivity; an 80% sensitivity improvement is reported")
w("RF Power", "1350 W")
w("Coolant (Plasma) Gas Flow Rate", "15.00 L min-1 Ar")
w("Auxiliary Gas Flow Rate", "0.80 L min-1 Ar")
w("Interface Cone Configuration", "High sensitivity sample and skimmer cones")
w("Sampler and Skimmer Cone Material", "N — 'high sensitivity' cones specified, material not stated")
w("Mass Resolution Setting", "~300")
w("Detector Configuration", "Single SEM in double mode, counting and analog")
w("Signal Collection Mode", "Peak jump")
w("Collision/Reaction Cell (CRC) Configuration",
  "ICP-MS/MS (triple-quadrupole mode) with NH3 reaction gas for analysis; tuning first performed in single-quadrupole (SQ) no-gas mode")
w("Reaction Gas Type", "NH3, high purity (>99.999%), supplied in T4; He (>99.999%, T1) pre-mixed with NH3 before the cell in a test of mixture composition. High-purity NH3 found more effective than the commonly used 1:9 NH3-He mixture")
w("Reaction Product Ion / Mass-Shift Transition",
  "Ammonia cluster adducts, mass shift +82: (176+82)Hf = 176Hf(14N1H)(14N1H2)3(14N1H3)3; likewise (177+82)Hf, (178+82)Hf, (175+82)Lu, (172+82)Yb. Lu, Yb and Hf reaction products identified over 175-300 amu")
w("Monitored Masses", "27Al, 43Ca, 89Y, 90Zr, 172Yb, (172+82)Yb, 175Lu, (175+82)Lu, (176+82)Hf, (177+82)Hf, (178+82)Hf")
w("Dwell Time per Mass", "27Al 2 ms, 43Ca 2 ms, 89Y 1 ms, 90Zr 2 ms, 172Yb 1 ms, (172+82)Yb 100 ms, 175Lu 1 ms, (175+82)Lu 50 ms, (176+82)Hf 300 ms, (177+82)Hf 100 ms, (178+82)Hf 100 ms")
w("Total Integration Time per Output Data Point", "0.659 s")
w("Cell Exit Discrimination Voltage", "CR exit lens -40.00 V (cell bias -4.200 V, CR amplitude 189.3 V, CR entry lens -144.0 V also tabulated)")
w("ICP Tuning", "Two-stage: first optimised in solution single-quadrupole and no-gas modes to tune for a robust plasma (U/Th = 1.00-1.05) and minimise oxides (ThO/Th < 0.5%); then switched to TQ and NH3 mode, with lenses tuned to maximise sensitivity for Hf reaction products while keeping Lu and Yb reaction rates low")
w("Oxide Production Method and Threshold", "ThO/Th < 0.5%, checked during SQ no-gas tuning")
w("Analyte", "Lu and Hf (with Yb monitored for interference); Al, Ca, Y and Zr monitored for inclusions")
w("Reported Variables and Units", "176Lu/177Hf and 176Hf/177Hf ratios; Lu-Hf isochron and weighted-mean ages (Ma)")
w("Ablation Duration per Spot", "25 s")
w("Laser Spot Path / Ablation Mode", "Single hole drilling, two cleaning pulses")
w("Background Count Time", "N — gas-blank correction applied in Iolite, duration not stated")
w("Acquisition Software", "N")
w("Data Processing Software(s)", "Iolite v.3.7 for gas-blank-corrected intensities, raw ratios and uncertainties; an in-house Microsoft Excel spreadsheet for drift, elemental fractionation and matrix-induced bias; IsoplotR for isochron and weighted-mean ages")
w("Blank / Background Correction Method", "Gas-blank-corrected intensities calculated in Iolite v.3.7 from time-resolved intensities")
w("Isobaric Interference Corrections Applied", "Yes — 176Lu and 176Yb on (176+82)Hf")
w("Interfering Species", "176Lu and 176Yb on the (176+82)Hf product mass, monitored via 175Lu and 172Yb")
w("Interference Correction Method",
  "Reaction-rate correction: (176+82)Hf = (176+82)total - (176Lu/175Lu)true x (175+82)Lu_measured - (176Yb/172Yb)true x (172+82)Yb_measured, using 176Lu/175Lu = 0.02655 and 176Yb/172Yb = 0.5887; contributions expressed as pLu(%) and pYb(%)")
w("Primary Calibration Standard Name", "NIST SRM 610")
w("Secondary Reference Materials", "XN02 xenotime as a matrix-matched reference material to correct matrix-induced elemental fractionation of Lu/Hf between SRM 610 and the samples")
w("Constants and Reference Values Used",
  "NIST SRM 610 recommended values 176Lu/177Hf = 0.1379 +/- 0.0050 and 176Hf/177Hf = 0.282111 +/- 0.000009, as determined by ID-MC-ICP-MS; 176Lu/175Lu = 0.02655; 176Yb/172Yb = 0.5887; 177Hf/178Hf = 0.682; 176Lu half-life ~37.12 Ga")
w("Normalization / Standards-Based Correction",
  "Two-step calibration: external correction of mass bias and fractionation against NIST SRM 610, then a matrix-induced correction against matrix-matched XN02 xenotime")
w("Uncertainty Level", "2SE for single-spot ages; uncertainties on weighted-mean ages quoted at 2s")
w("Uncertainty Propagation Method", "Uncertainty propagation workflow implemented in IsoplotR")
w("Analysis Inclusion and Rejection Criteria",
  "Acquired and included counts both stated: 'A total of 246 spot analyses were undertaken in 20 analytical sessions over 3 months, 236 of which yielded a weighted-mean age of 515.4 +/- 1.2 Ma'. The rejection rule itself is not stated")
w("Goodness-of-Fit or Dispersion Statistic", "MSWD reported with each aggregate age — e.g. MSWD = 2.3 (n = 236, XN02) and MSWD = 0.6 (n = 15, weighted-mean Lu-Hf age 489.8 +/- 2.2 Ma)")
w("Analytical Accuracy and Assessment Method", "Accuracy of common-Hf corrected single-spot xenotime ages generally better than 1.5%, assessed against ID-TIMS U-Pb ages of the same reference materials")
w("Within-Session Analytical Precision and Assessment Method", "Precision of common-Hf corrected single-spot ages 1.5-8.1% (xenotime) and 9.2-36.0% (apatite); isochron age uncertainties 3.5-10% for garnet")
w("Session Identifier", "N — 20 analytical sessions over 3 months referenced, no identifier stated")
w("Analysis Sequence", "N")

# ------------------------------------------------------------------ Gil-Diaz + Lopez Garcia (Solution Q)
s("Technique", ["Solution Q-ICP-MS (triple-quadrupole platform)", "Solution Q-ICP-MS (triple-quadrupole platform)",
                "Solution Q-ICP-MS", "Solution Q-ICP-MS (triple-quadrupole platform)"])
s("Laboratory", ["N — 'Agilent 8800, Basel, Switzerland'; the Basel-area author affiliation is FHNW",
                 "N — instrument given as 'iCAP-TQ, Thermo' with no laboratory stated",
                 "Karlsruhe Institute of Technology (KIT), Germany",
                 "Institute of Science Tokyo"])
s("Target Material", ["Estuarine suspended particulate matter and sediment (Gironde Estuary sorption experiments)",
                      "Estuarine sediment — total digestions and selective extraction fractions",
                      "Estuarine water — dissolved Se from sorption kinetics and isotherms",
                      "Carbonaceous asteroid particles (Ryugu, Hayabusa2 TD1) and the Allende chondrite"])
s("Sample Name", ["N — SPM isotherm experiment at 1000 mg/L", "Selective extraction fractions F1-F4 and F4N; CRM NCS 73307",
                  "N — sorption kinetics and isotherm solutions; CRMs CRM-TMDW and NIST 1643f",
                  "Ryugu particles A0066, A0238, A0247, A0256, A0259, A0268, A0301, A0313; Smithsonian Allende powder"])
s("Sampling Unit", ["N", "Weighed sediment aliquot — 30 mg for tri-acid digestion; 200-500 mg per selective extraction fraction",
                    "N — sub-sampled water aliquots",
                    "Individual particle, weighed: A0066 4.325 mg, A0238 1.868 mg, A0247 2.311 mg, A0256 2.378 mg, A0259 1.478 mg, A0268 1.902 mg, A0301 1.923 mg, A0313 2.012 mg; 20 mg Allende"])
s("Sample Preparation Method", ["N", "Dried at 50 C and homogenised in an agate mortar before microwave digestion",
                                "N", "Particles individually weighed on a Mettler Toledo XPR2U microbalance (0.1 ug readability) and transferred to PFA vials without powdering"])
s("Digestion Acid(s)", ["N",
  "Tri-acid HNO3+HCl+HF: 750 uL HNO3 (14M), 1.5 mL HCl (10M), 2.5 mL HF (29M); re-dissolved in 250 uL HNO3. Microwave route for Se: 3 mL HNO3, 0.5 mL H2O2, 0.25 mL HF, 0.5 mL Milli-Q",
  "N", "0.2 mL HF + 0.1 mL HNO3 + 0.4 mL water; then 0.2 mL HNO3 + 0.2 mL HCl + 0.2 mL H2O2; final 0.2 mL HNO3 + 0.2 mL H2O2"])
s("Digestion Vessel Type", ["N", "Closed PP tubes (DigiTUBEs, SCP Science) on a heating block; PTFE vessels for evaporation; microwave START1500 (MLS GmbH)",
                            "N", "PFA hexagonal cap vials (6 mL, Savillex), tightly capped with polypropylene wrenches to maintain high-pressure conditions"])
s("Digestion Temperature", ["N", "110 C on the heating block; evaporation at 120 C; microwave ramp to 210 C held 10 min; evaporation at 70 C",
                            "N", "120 C, then 220 C, then 100 C; second stage 150 C; final 80 C"])
s("Digestion Duration", ["N", "2 h at 110 C; microwave 10 min at 210 C then cooling overnight",
                         "N", "3 h ultrasonic agitation, 12 h at 120 C, 5 days at 220 C, 1 day at 150 C, 1 day at 80 C"])
s("Number of Digestion Steps", ["N", "N", "N", "Four heating stages are described"])
s("Final Solution Matrix", ["N", "Made up to 10 mL with Milli-Q water (18.2 MOhm); Se route made up to 6 mL",
                            "N", "5 mL 0.5 M HNO3, dilution factors 1200 (A0066) to 3400 (A0259); Group-1 aliquots diluted to DF 20,000; Group-3 in 0.5 M HNO3 + ~0.05 M HF"])
s("Sample Aliquot Mass or Volume", ["N", "30 mg (tri-acid) and 40-50 mg (microwave)", "N",
                                    "1.478-4.325 mg per particle; 4-10% aliquot taken for Group-1"])
s("Chromatographic Separation Applied", ["N", "No — sequential selective extractions (acetate, ascorbate, H2O2, HCl/HNO3) rather than chromatography", "N", "N"])
s("Instrument Manufacturer", ["Agilent", "Thermo Fisher Scientific", "Thermo Fisher Scientific", "Thermo Fisher Scientific"])
s("Instrument Model", ["Agilent 8800 (QQQ-ICP-MS)", "iCAP-TQ", "XSeries 2", "iCAP TQ"])
s("ICP-MS Type", ["Triple quadrupole (ICP-MS/MS)", "Triple quadrupole (ICP-MS/MS)",
                  "Single-collector quadrupole (Q-ICP-MS)", "Triple quadrupole (ICP-MS/MS)"])
s("Collision/Reaction Cell (CRC) Configuration",
  ["ICP-MS/MS (triple-quadrupole mode), oxygen-shift with O2 as cell gas",
   "Per analyte: KED (He) for 126Te; ICP-MS/MS O2 mass-shift mode for spiked/experimental 125Te",
   "CCT mode (collision cell) with a He:H2 mixture", "KED (He) mode"])
s("Collision Gas Type", ["O2 (used as the collision/reaction gas for the mass shift)", "He for KED; O2 for the mass-shift mode",
                         "He+H2 mixture at 92% : 8%, to minimise 40Ar37Cl interferences", "He"])
s("Reaction Gas Type", ["O2", "O2 (for the 125Te mass-shift mode)", "N/A — collision mode only", "N/A — KED only"])
s("Reaction Product Ion / Mass-Shift Transition",
  ["125Te + 16O -> 141TeO; 77Se + 16O -> 93SeO", "125Te + 16O -> 141TeO (mass-shift O2 mode); 126Te measured on-mass in KED",
   "N/A — on-mass measurement in CCT mode", "N/A — on-mass measurement in KED mode"])
s("Monitored Masses", ["125Te; 77Se", "125Te and 126Te (and their O-shifted products)", "N — Se isotopes not individually stated",
                       "54 elements measured in three groups: Group-1 trace elements, Group-2 major and minor elements, Group-3 HFSE plus Mo and W"])
s("Analyte", ["Te and Se", "Te", "Se",
              "54 elements: Li, Be, Sc, Ga, As, Se, Rb, Sr, Y, Ag, Cd, In, Cs, Ba, La-Lu, Tl, Pb, Bi, Th, U; Na, Mg, Al, P, K, Ca, V, Cr, Mn, Fe, Co, Ni, Cu, Zn; Ti, Zr, Nb, Hf, Ta, Mo, W"])
s("Reported Variables and Units", ["Te and Se concentrations (ug L-1; mg kg-1)", "Particulate Te concentration (mg kg-1)",
                                   "Dissolved Se concentration (ug L-1)", "Elemental abundances, CI-normalised ratios"])
s("Internal Standard Element", ["103Rh, to correct for matrix effects", "N", "103Rh and 115In",
                                "103Rh for the calibration-curve elements; 113In-203Tl for the ID-IS method; 91Zr and 179Hf for Nb and Ta"])
s("Per-Analyte Calibration Strategy",
  ["External calibration for both Te and Se", "External calibration",
   "External calibration",
   "Three strategies by group: calibration curve with 103Rh internal standardisation; 113In-203Tl ID-IS (Yokoyama et al. 2017); isotope dilution for Ti, Zr, Mo, Hf and W; 91Zr and 179Hf as internal standards for Nb and Ta"])
s("Isotope Dilution Data Reduction Method", ["N", "N", "N",
  "ID-IS method of Kagami and Yokoyama (2021); isotope dilution for Ti, Zr, Mo, Hf and W"])
s("Isotope Dilution Spike", ["N", "N", "N", "97Mo (94.19%, Mo = 28 ng/g) and 182W (94.07%, W = 12 ng/g), dissolved in ~1 M HF"])
s("Primary Calibration Standard Name", ["N", "N", "N", "XSTC-13 and a custom solution for the calibration-curve elements; MISA05-1 (AccuStandard Inc.) for Group-3"])
s("Secondary Reference Materials", ["N", "NCS 73307 stream sediment", "CRM-TMDW drinking water and NIST 1643f freshwater",
                                    "Smithsonian Allende powder (20 mg), dissolved and measured n = 5 under the same procedure"])
s("Analytical Accuracy and Assessment Method",
  ["Recovery on NCS 73307 total digestions 94 +/- 17% (N = 3)",
   "Recoveries: NIST 1643f 95 +/- 5% (N = 5) in KED mode and 89 +/- 10% (N = 5) in O2 mode; NCS 73307 99 +/- 14% (N = 4) in KED and 70 +/- 19% (N = 4) in O2 mode",
   "Recoveries 98-... % on CRM-TMDW and NIST 1643f", "N"])
s("Isobaric Interference Corrections Applied",
  ["Yes — oxygen shift used to move the analyte away from interferences, including doubly-charged REE on 77Se",
   "Yes — 86Sr40Ar, 110Cd16O and 110Pd16O on 126Te, and 126Xe from the acid blank",
   "Yes — 40Ar37Cl on Se, minimised by the He:H2 collision mixture", "N"])
s("Interfering Species", ["Doubly-charged rare earth elements on 77Se",
                          "86Sr40Ar, 110Cd16O, 110Pd16O on 126Te; 126Xe from 2% HNO3 analytical blanks",
                          "40Ar37Cl", "N"])
s("Interference Correction Method",
  ["Mass shift away from the interference rather than mathematical correction",
   "Corrections established with respective monoelemental solutions, each influencing <0.1% (Filella and Rodushkin, 2018)",
   "Collision-cell suppression using the He:H2 mixture", "N"])
s("Detection Limit", ["N", "LOD 0.1 ng L-1 (N = 10); selective-extraction Te concentrations 5-fold (F2) to 200-fold (F4) above LOD",
                      "LOD 0.01 ug L-1 (N = 10)", "N"])
s("Procedural Blank Level", ["N", "Three blanks run for each extraction; 126Xe contribution from 2% HNO3 analytical blanks noted",
                             "N", "N — blank data stated to be in the supplementary material; Ta and W blank contributions exceeded 30%"])
s("Analysis Inclusion and Rejection Criteria",
  ["N", "N", "N",
   "Explicit rule and outcome: 'Although the abundances of Ta and W were measured, the data for these elements were excluded from the results due to high blank contributions (>30%) during the ICP-MS analysis'"])
s("Uncertainty Level", ["Mean +/- SD", "Mean +/- SD", "N", "N — replicate averages (n = 5) and associated uncertainties stated to be in the supplementary material"])
s("Analytical Mode", ["Solution nebulisation (continuous)"] * 4)
s("Session Identifier", ["N"] * 4)

# ------------------------------------------------------------------ build
def build(src, cols, data, out):
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    res = [["Metadata Item"] + cols]
    n_att = 0
    for r in rows[1:]:
        if not r or not r[0].strip():
            res.append([""] * (len(cols) + 1)); continue
        name = r[0]
        if name[0].isdigit() and not r[2].strip():
            res.append([name] + ["N"] * len(cols)); continue
        vals = data.get(name, ["N"] * len(cols))
        assert len(vals) == len(cols), f"{name}: {len(vals)} values for {len(cols)} columns"
        n_att += sum(1 for v in vals if v != "N" and not v.startswith("N/A") and not v.startswith("N —"))
        res.append([name] + list(vals))
    if APPLY:
        with open(os.path.join(ROOT, out), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(res)
    content = sum(1 for x in res[1:] if x[0] and not x[0][0].isdigit())
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(out):58} "
          f"{content} fields x {len(cols)} cols, {n_att} attested")
    unknown = [k for k in data if k not in {x[0] for x in res}]
    if unknown: print(f"    !! field names not in the TAPP: {unknown}")

build(LAQ_SRC, LAQ_COLS, W, "LA-Q-ICP-MS/LA-Q-ICP-MS_lit_assessment_draft_TQ_2026-08-17.csv")
build(SOLQ_SRC, SOLQ_COLS, S, "Solution Q-ICP-MS/Solution_Q-ICP-MS_lit_assessment_draft_TQ_2026-08-17.csv")
if not APPLY: print("\ndry run — rerun with --apply")
