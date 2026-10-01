#!/usr/bin/env python3
"""Solution Q-ICP-MS: keyed notation, with every procedure-level cell re-read (2026-09-30).

    python3 "Project Files/Scripts/sq_keyed_reverify_20260930.py" [--apply] [--out-sim DIR]

The same pass as ssf_keyed_reverify_20260930.py, for Solution Q's nine columns: Hu & Gao 2008, Yu+2005,
Makishima+2011, Long+2025, Lu+2007 (its ICP-QMS half), Gil-Díaz+2020 (three instruments, three columns) and
López García+2026. Every procedure-level cell was re-read against its paper, and the edit was scored by
`Project Files/Reports/SQ_Cells_RoundTrip_2026-09-30/roundtrip.py` before it was applied.

What the re-read found, beyond format (per column in the dicts below):
  * a table's wrong column, again: Makishima's detection limits held Table 1's sensitivity column
    (Cd 0.04, In 0.5, Tl 0.5, Bi 0.6), not its 3s limits (0.8, 0.2, 0.9, 0.2 pg/ml); its units were µg/g,
    not ng/g;
  * values filed under the wrong instrument: Gil-Díaz's XSeries 2 column held the Te limit (0.01 µg/L)
    as its Se limit (0.06), and the iCAP-TQ column lacked its Se work (O2 mode, four isotopes, NIST 1640a);
  * fabricated or unsupported detail: "STD, no gas" cell modes for Hu, Yu and Makishima; "on-peak zero"
    blanks and "matrix-matched standards at fixed intervals" for Yu; "ID-IS inherently corrects for
    interferences" and a Ta spike for Lu; "octopole, no gas (PML practice)" for Makishima; "KED", "same
    dissolved aliquots" and "direct analysis" for Long; "pure 118Sn solution" for Hu; a "~300" m/Δm
    for every quadrupole;
  * wrong values: López García's second and third digestion steps used H2O, not H2O2, and its cell modes
    were all "KED" where Group-1 ran mostly without gas and O2 served Ga, As, Se, Cd, In, Na, P, K and Ca;
  * stated facts missing: Yu's Table 2 detection limits, three-month precision and accuracy, its 66Zn
    argide correction; Lu's make-up gas, daily P/A factor, Table 2a limits and blanks; Makishima's
    procedure reference; Hu's peak hopping and blank table; López García's In–Tl, Ti and Zr–Hf spikes
    and 2σ convention.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
# ---- c1_hu
D = " — "
S31 = "§3.1"
EL48 = ("Li, Be, B, Sc, V, Cr, Co, Ni, Cu, Zn, Ga, Ge, As, Rb, Sr, Y, Zr, Nb, Mo, Cd, In, Sn, Sb, Te, Cs, Ba, "
        "La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Tl, Pb, Bi, Th, U")
RM5 = "AGV-1, BHVO-1, G-2, GSR-5, SCO-1"
RM18 = "JP-1, DTS-1, BHVO-2, BIR-1, JB-3, GSR-3, DNC-1, W-2, AGV-2, BCR-2, JA-3, GSR-2, JG-3, GSR-1, RGM-1, GSR-4, SGR-1, GSR-6"
HU_BLANK = "Li: 0.036 ± 0.028; Be: 0.00091 ± 0.00049; B: 0.39 ± 0.26; Sc: 0.033 ± 0.011; V: 0.50 ± 0.38; Cr: 0.53 ± 0.16; Co: 0.0046 ± 0.0032; Ni: 0.065 ± 0.037; Cu: 0.072 ± 0.022; Zn: 0.80 ± 0.56; Ga: 0.0037 ± 0.0020; Ge: 0.0081 ± 0.0040; As: 0.021 ± 0.009; Rb: 0.11 ± 0.05; Sr: 0.018 ± 0.018; Y: 0.0018 ± 0.0017; Zr: 0.0030 ± 0.0015; Nb: 0.0012 ± 0.0012; Mo: 0.035 ± 0.030; Cd: 0.0026 ± 0.0015; In: 0.00016 ± 0.00004; Sn: 0.0083 ± 0.0016; Sb: 0.010 ± 0.006; Te: 0.00097 ± 0.00014; Cs: 0.00060 ± 0.00034; Ba: 0.075 ± 0.063; La: 0.0025 ± 0.0020; Ce: 0.0028 ± 0.0016; Pr: 0.00056 ± 0.00042; Nd: 0.0019 ± 0.0017; Sm: 0.00079 ± 0.00036; Eu: 0.00023 ± 0.00014; Gd: 0.00063 ± 0.00054; Tb: 0.00013 ± 0.00005; Dy: 0.00058 ± 0.00038; Ho: 0.00013 ± 0.00008; Er: 0.00027 ± 0.00020; Tm: 0.00011 ± 0.00003; Yb: 0.00043 ± 0.00025; Lu: 0.00015 ± 0.00007; Hf: 0.0010 ± 0.0012; Ta: 0.00017 ± 0.00009; W: 0.023 ± 0.010; Tl: 0.0026 ± 0.0009; Pb: 0.043 ± 0.020; Bi: 0.00049 ± 0.00028; Th: 0.00062 ± 0.00050; U: 0.00027 ± 0.00025"
COL1 = {  # Hu & Gao 2008 (Chemical Geology 253), ELAN 6100 DRC at NWU Xi'an. Read 2026-09-30: §2, §3.1, §3.3, §3.4, Tables 2 and 3.
 "Target Material": ("andesite; basalt; granite; granodiorite; rhyolite; peridotite; dunite; dolerite; diabase; shale; sandstone; limestone; loess; graywacke" + D +
                     "the reference materials of Tables 2 and 3, and the upper-crustal samples: PAAS, SCO-1, worldwide loess and Chinese composites of graywackes, shales and granites (§2)"),
 "Sample Preparation Method": "Fifty milligrams of rock powder digested in a sealed PTFE-lined stainless steel bomb, taken up and made up to 50 ml with ultra-pure water and Rh internal standard" + D + "clean-room conditions (§3.3); for As and Te, 4.80 ml of sample solution plus 0.20 ml ethanol",
 "Digestion Step": ("bomb attack (1 ml HNO3 + 1 ml HF, 190 °C for 48 h, then evaporated to incipient dryness and twice taken to dryness with 1 ml HNO3); "
                    "re-dissolution (1.5 ml HNO3 + 2.5 ml ultra-pure water, capped, 150 °C overnight)" + D + "§3.3 numbers five operations; the evaporations carry no attack of their own"),
 "Digestion Acid(s)": "bomb attack: HNO3 + HF; re-dissolution: HNO3" + D + "§3.3",
 "Digestion Temperature": "bomb attack: 190 °C; re-dissolution: 150 °C" + D + "§3.3",
 "Digestion Duration": "bomb attack: 48 h; re-dissolution: overnight" + D + "§3.3",
 "Final Solution Matrix": "all: 1.5 ml HNO3 and 2.5 ml water made up to 50 ml with ultra-pure water and 0.50 ml of 1.0 µg/ml Rh" + D + "§3.3",
 "Chromatographic Separation Applied": "None" + D + "the digest is analysed directly (§3.3)",
 "Isotope Dilution Spike": "None",
 "Mass Resolution Setting": "N",
 "Collision/Reaction Cell (CRC) Configuration": "N" + D + "an ELAN 6100 DRC; no cell gas or cell mode is described (" + S31 + ")",
 "Desolvation System": "N",
 "Nebulizer Gas Flow Rate": "N" + D + "'optimized to obtain maximum signal intensities for Mg, Co, Rh, Ce, Pb and U' (" + S31 + ")",
 "Plasma Thermal Mode": "N" + D + "RF power 1350 W (" + S31 + ")",
 "Target Species": EL48 + D + "the forty-eight trace elements of Table 2",
 "Reported Variables and Units": EL48 + " (ppm)" + D + "Table 2; blanks in ppb",
 "Monitored Masses": "114Cd → Cd; 115In → In; 118Sn → Sn" + D + "the masses of the other elements are not stated; ¹¹⁸Sn⁺ is measured to correct the Sn interferences (" + S31 + "), and whether it is also the Sn analytical mass is not stated",
 "Dwell Time per Mass": "all: 0.15 s" + D + "'peak hopping (one point per peak) was used with a dwell time of 0.15 s' (" + S31 + ")",
 "Number of Scans per Replicate": "all: three sweeps per reading and three readings per replicate" + D + S31,
 "Signal Collection Mode": "Peak hopping, one point per peak" + D + S31,
 "Wash Time Between Samples": "N" + D + "'manual analyses in which care was taken to completely wash-out B and Ta signals between samples' (" + S31 + ")",
 "Internal Standard Element": "all: Rh" + D + S31 + ", §3.3",
 "Internal Standard Concentration": "0.50 ml of 1.0 µg/ml Rh in the 50 ml final solution" + D + "§3.3",
 "Oxide Production Method and Threshold": "CeO+/Ce+ and Ce2+/Ce+ below 2.5%, with the nebulizer gas flow optimised for maximum Mg, Co, Rh, Ce, Pb and U signals" + D + S31,
 "Doubly-Charged Species Monitor": "Ce2+/Ce+" + D + S31,
 "Doubly-Charged Species Production": "Ce2+/Ce+ below 2.5%" + D + S31,
 "Drift Correction Method": "Rh internal standard, and a calibration solution analysed repeatedly as a drift monitor over the run" + D + "drift minimised by flushing a rock solution for 30 min before tuning (" + S31 + ")",
 "Calibration Strategy per Target Species": "all: calibration solution, with Rh as internal standard" + D + "'repeatedly analyzing a calibration solution as a drift monitor' (" + S31 + "); its composition is not stated",
 "Spectral Interference Corrections Applied": "Y" + D + "114,115Sn+ on 114Cd+ and 115In+ (" + S31 + ")",
 "Interfering Species": "114Cd: 114Sn+; 115In: 115Sn+; other: N" + D + S31,
 "Interference Correction Method": "114Cd, 115In: calibrated through the measurement of 118Sn+; other: N" + D + S31,
 "Isotope Dilution Data Reduction Method": "None",
 "Calibration Factor and Determination Method": "N" + D + "'The isotope interferences of 114,115Sn+ on 114Cd+ and 115In+ were calibrated through the measurement of 118Sn+' (" + S31 + "); no factor is stated",
 "Procedural Blank Level": HU_BLANK + D + "ppb, mean ± STD of n = 5 blanks (Table 2)",
 "Combination Method": "all: over the replicate analyses of each reference material" + D + "the statistic is not named; Table 2 gives n and 'RSD%'. The upper-crust samples are physical composites, not averages of analyses",
 "Primary Calibration Standard Name": "N" + D + "'a calibration solution' (" + S31 + "), not named",
 "Secondary Reference Materials": RM5 + ", " + RM18 + D + "five in Table 2 for accuracy and precision; eighteen more in Table 3 for Mo, Cd, In, Sn, Sb, W, Tl, Bi, As and Te (§3.4)",
 "Within-Session Analytical Precision and Assessment Method": RM5 + " [all: RSD of n = 4–7 analyses, usually <8%]" + D + "Table 2 and §3.4; whether the replicates share a session is not stated",
 "Analytical Accuracy and Assessment Method": (RM5 + " [all: agreement with GeoReM preferred values (AGV-1, BHVO-1) and Govindaraju 1994 (G-2, GSR-5, SCO-1), better than 8% for most elements]; "
                                               + RM18 + " [Mo, Cd, In, Sn, Sb, W, Tl, Bi, As, Te: reasonable agreement with Govindaraju 1994 and GeoReM]" + D + "Tables 2 and 3, §3.4"),
 "Additional Notes": "Auto lens voltages optimised on a 10 ng/ml Mg, Co, Rh, Ce, Pb and U solution; As and Te measured in 4.80 ml sample solution plus 0.20 ml ethanol; HF boiled before sub-boiling distillation to remove volatile As" + D + "§3.1, §3.2, §3.3",
}
# ---- c2_yu
D = " — "
YM = [("7Li", "Li", "10", "2500"), ("11B", "B", "10", "1000"), ("25Mg", "Mg", "0.5", "800"), ("46Ca", "none", "2", "0.5"),
      ("27Al", "Al", "0.5", "15000"), ("55Mn", "Mn", "0.5", "12000"), ("66Zn", "Zn", "5", "2500"), ("87Sr", "Sr", "0.5", "1500"),
      ("111Cd", "Cd", "60", "1500"), ("238U", "U", "20", "9000")]
YR = "Li/Ca, B/Ca, Mg/Ca, Al/Ca, Mn/Ca, Zn/Ca, Sr/Ca, Cd/Ca, U/Ca"
COL2 = {  # Yu, Day, Greaves & Elderfield 2005 (G-cubed 6), Elan DRC II at Cambridge. Read 2026-09-30: §2–3.6, Tables 1 and 2, Figs 1–2.
 "Target Material": "foraminiferal calcite" + D + "core-top Cibicidoides wuellerstorfi from the north Atlantic Ocean (§4)",
 "Sample Preparation Method": ("Ten to twenty tests handpicked, crushed gently, cleaned of clays (water, methanol) and silicates, reductively and oxidatively cleaned, "
                               "rinsed twice in 0.001 M HNO3 and dissolved in 200 µl 0.075 M HNO3. 20 µl diluted for Ca by ICP-AES, the remainder diluted to 100 ppm Ca" + D + "§2"),
 "Digestion Step": "dissolution (200 µl 0.075 M HNO3)" + D + "§2; the paper does not call it a digestion",
 "Digestion Acid(s)": "dissolution: 0.075 M HNO3" + D + "§2",
 "Digestion Temperature": "N",
 "Digestion Duration": "N",
 "Digestion Vessel Type": "N",
 "Final Solution Matrix": "all: 0.075 M HNO3 at 100 ppm Ca" + D + "§2; working standards diluted with the same acid",
 "Sample Aliquot Mass or Volume": "Ten to twenty tests, about 300 µg of shells" + D + "§2; one measurement uses 250 µl at 100 ppm Ca, equivalent to 60 µg calcite",
 "Chromatographic Separation Applied": "None",
 "Mass Resolution Setting": "N",
 "Collision/Reaction Cell (CRC) Configuration": "N" + D + "an Elan DRC II; no cell gas or cell mode is described",
 "Detector Configuration": "Pulse counting for all isotopes" + D + "Table 1; 'We determined all isotopes using pulse mode to avoid the need for cross calibration' (§3.1)",
 "Desolvation System": "N",
 "Plasma Thermal Mode": "N" + D + "RF power 1300 W (Table 1)",
 "Instrument Warm-up / Session Duration Limit": "Cone conditioning with pure Ca solution (100 ppm) for 0.5–1 hours before optimisation" + D + "§3.4; blanks stable over a typical run of ~5 hr (§3.2)",
 "Instrument Sensitivity": "; ".join("%s: %s cps/ppb" % (m, c) for m, _, _, c in YM) + D + "typical count rate (Table 1); ~40 kHz for 1 ppb ¹¹⁵In at 60 µl/min (§2)",
 "Target Species": "Li, B, Mg, Al, Mn, Zn, Sr, Cd, U" + D + "as element/Ca ratios; Ca is the denominator",
 "Reported Variables and Units": "Li/Ca, B/Ca, Mn/Ca, Zn/Ca, Cd/Ca (µmol/mol); Mg/Ca, Sr/Ca, Al/Ca (mmol/mol); U/Ca (nmol/mol)" + D + "Table 2 note a",
 "Monitored Masses": "; ".join("%s → %s" % (m, e) for m, e, _, _ in YM) + D + "Table 1; ⁴⁶Ca for its low abundance, ¹¹¹Cd to avoid Sn on ¹¹²Cd and ¹¹⁴Cd (§3.1, §3.3)",
 "Dwell Time per Mass": "; ".join("%s: %s ms" % (m, d) for m, _, d, _ in YM) + D + "ms/amu (Table 1)",
 "Number of Scans per Replicate": "all: 250 sweeps per reading, 1 reading per replicate" + D + "Table 1",
 "Number of Replicates": "6" + D + "Table 1",
 "Analysis Sequence": "8 external calibration standards, then 50–80 samples interspersed with drift correction standards every 3 samples" + D + "6–10 hours (§3.4)",
 "Wash Time Between Samples": "60 s" + D + "Table 1; uptake time 65 s",
 "Signal Collection Mode": "Peak hopping" + D + "Table 1",
 "Internal Standard Element": "all: none" + D + "element/Ca intensity ratios against matrix-matched external standards (§3)",
 "Internal Standard Concentration": "N/A",
 "Oxide Production Method and Threshold": "CeO/Ce within 3%" + D + "'Plasma robustness was monitored by constraining CeO/Ce ratio within 3%' (§2)",
 "Drift Correction Method": "Drift monitors of intermediate concentration every 3 samples, corrected off-line by linear interpolation between two consecutive monitors" + D + "§3.4",
 "Calibration Strategy per Target Species": "all: external matrix-matched standards at 100 ppm Ca, element/Ca intensity ratios on 8-point linear calibration lines" + D + "R² usually > 0.999 (§3.4)",
 "Blank / Background Correction Method": "Average blank subtracted from the average raw intensities of 6 replicate scans" + D + "blanks in the same acid as used for dissolution and dilution (§3.2)",
 "Pulse/Analog Detector Nonlinearity Correction": "N/A" + D + "all isotopes in pulse mode 'to avoid the need for cross calibration' (§3.1)",
 "Spectral Interference Corrections Applied": "Y" + D + "⁴⁰Ar²⁶Mg on ⁶⁶Zn corrected off-line; ⁷Li¹⁸O, ⁴⁶Ti and ⁸⁷Rb found insignificant; HNO3 polyatomics on ⁶⁶Zn negligible (§3.3)",
 "Interfering Species": "25Mg: 7Li18O; 46Ca: 46Ti; 66Zn: 40Ar26Mg and 1H2 14N 18O 16O2+; 87Sr: 87Rb; other: N" + D + "Table 1 note c",
 "Interference Correction Method": ("66Zn: off-line correction, 66Zn/46Ca corrected = measured − CF × 25Mg/46Ca measured, with CF = (K1 − K2)/(K3 − K4) from the slopes of Mg and Zn serial standards; "
                                    "25Mg, 46Ca, 87Sr: none, found insignificant; other: N" + D + "Eqs 1–2, §3.3"),
 "Isotope Dilution Data Reduction Method": "None",
 "Memory Effect Mitigation": "Longer washout and uptake times for B, and a quartz spray chamber to reduce B blanks" + D + "§2, §3.2",
 "Calibration Factor and Determination Method": ("Zn/Ca: argide correction factor CF calculated daily from one Mg and one Zn standard, typically ~0.002; "
                                                 "other: slopes and intercepts of the calibration lines" + D + "§3.3, §3.4"),
 "Procedural Blank Level": "Li, Mg, Sr: <1%; Cd: <2%; Zn: <4%; U: <5%; B: 5%; other: N" + D + "relative to typical foraminiferal ratios; Ca also <1%; B was 30% with a glass spray chamber (§3.2)",
 "Combination Method": "all: average of n replicate analyses of each standard" + D + "Table 2 notes",
 "Primary Calibration Standard Name": ("all [all: gravimetric multielement stock standards, a 10,000 µg/ml Ca standard spiked with certified 1,000 µg/ml Li, B, Al, Mn, Zn, Sr, Cd and U solutions, "
                                       "diluted with 0.075 M HNO3 to 100 ppm Ca]" + D + "§2; minor elements in the Ca standard measured by ICP-AES"),
 "Calibration Standard Measurement Frequency": "8 calibration standards per run, drift monitors every 3 samples" + D + "§3.4",
 "Secondary Reference Materials": "N" + D + "precision and accuracy are assessed on external standards of known ratio (Table 2); core-top results are compared with published data (Table 4)",
 "Detection Limit": ("Li/Ca: 0.5; B/Ca: 15; Mg/Ca: 0.03; Al/Ca: 0.05; Mn/Ca: 0.3; Zn/Ca: 0.05; Sr/Ca: 0.02; Cd/Ca: 0.005; U/Ca: 0.5"
                     + D + "in the units of the ratio (Table 2)"),
 "Detection Limit Method": "all: 3 × SD/m, with SD of several measurements of a sample whose ratio is close to the blank and m the calibration slope" + D + "Table 2 note b",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": ("all [Li/Ca: 2.42%; B/Ca: 4.17%; Mg/Ca: 1.39%; Al/Ca: 14.06%; Mn/Ca: 0.93%; "
     "Zn/Ca: 2.83% (1.2–7.8), 5.05% (0.5–1.2); Sr/Ca: 0.92%; Cd/Ca: 2.37% (0.07–0.24), 4.80% (0.01–0.07); U/Ca: 2.54%]"
     + D + "RSD of external standards over three months, n = 120 except Zn/Ca 88 and 32, Cd/Ca 50 and 70 (Table 2, §3.6)"),
 "Analytical Accuracy and Assessment Method": ("all [Li/Ca: 0.39%; B/Ca: 2.57%; Mg/Ca: 0.61%; Al/Ca: 9.30%; Mn/Ca: 0.23%; Zn/Ca: 0.82% (1.2–7.8), 1.69% (0.5–1.2); "
     "Sr/Ca: 0.34%; Cd/Ca: 0.93% (0.07–0.24), 0.80% (0.01–0.07); U/Ca: 1.09%]" + D + "Acc.% = (average measured − true)/true × 100 on external standards (Table 2)"),
 "Additional Notes": "Cetac ASX-100 autosampler; auto lens on; 0.03 mm ID pump tubing at 12 rpm; Ca matrix effects tested over 60–240 ppm Ca (Table 1, §2, §3.5)",
}
# ---- c3_makishima
D = " — "
MN = "Makishima and Nakamura (2006)"
RMS_IG = "JB-2, JB-3, JA-1, JA-2, JA-3, JP-1, BHVO-1, AGV-1, PCC-1, DTS-1"
RMS_NIST = "NIST SRM 610, NIST SRM 612, NIST SRM 614, NIST SRM 616"
COL3 = {  # Makishima, Nakamura et al. 2011 (Geostandards and Geoanalytical Research 35), Agilent 7500cs at PML. Read 2026-09-30: Experimental, Results, Tables 1–5, Figs 1–4.
 "Procedure Reference(s)": MN + D + "'Details of these methods and ICP operating conditions are described in Makishima and Nakamura (2006)'",
 "Target Material": "basalt; andesite; peridotite; dunite; synthetic glass; carbonaceous chondrite" + D + "GSJ and USGS silicate RMs, NIST SRM 610–616 glasses, and Orgueil, Murchison and Allende",
 "Sample Preparation Method": ("Rock powders decomposed with the Sm spike; NIST glasses crushed roughly in a silicon nitride mortar, chips hand-picked, washed and dried; "
                               "solutions diluted with 0.5 mol/l HNO3 to a dilution factor ≥ 1000" + D + "clean room at PML; NIST SRM 610 decomposed without spike, the Sm spike added to its solution"),
 "Digestion Step": ("ultrasonic HF-HClO4 (basalts, andesites and NIST SRM 612, 614, 616, with the Sm spike, in an ultrasonic bath, dried to decompose fluorides); "
                    "bomb HF (peridotites and chondrites, with the Sm spike, in a TFE bomb at 245 °C); HClO4 drying (the bomb digests); final uptake (0.5 mol/l HNO3)" + D + "after Yokoyama et al. (1999) and " + MN),
 "Digestion Acid(s)": "ultrasonic HF-HClO4: HF + HClO4; bomb HF: HF; HClO4 drying: HClO4; final uptake: 0.5 mol/l HNO3",
 "Digestion Temperature": "bomb HF: 245 °C; other: N",
 "Digestion Duration": "N",
 "Digestion Vessel Type": "TFE bomb for peridotites and chondrites" + D + "the vessel for the ultrasonic digestion is not stated",
 "Final Solution Matrix": "all: 0.5 mol/l HNO3, dilution factor ≥ 1000" + D + "the same acid for calibrator, sample and washout solutions",
 "Sample Aliquot Mass or Volume": "15–42 mg (basalts and andesites); 30–63 mg (peridotites); 8–22 mg (NIST glasses); 9–28 mg (chondrites)",
 "Isotope Dilution Spike": "149Sm-enriched spike" + D + "for the ID of Sm, whose ¹⁴⁹Sm intensity is the internal standard for Cd, In, Tl and Bi",
 "Mass Resolution Setting": "N",
 "Collision/Reaction Cell (CRC) Configuration": "N",
 "Plasma Thermal Mode": "N",
 "Instrument Sensitivity": "111Cd: 0.04; 115In: 0.5; 149Sm: 0.09; 205Tl: 0.5; 209Bi: 0.6" + D + "count pg⁻¹ ml (Table 1)",
 "Procedural Blank Level": "Cd: 16 pg; In: <0.2 pg; Tl: 4 pg; Bi: 3 pg" + D + "total dissolution blanks, similar for the ultrasonic and bomb digestions, n = 4 (Table 1)",
 "Target Species": "Cd, In, Tl, Bi" + D + "Sm is determined by ID as the internal standard",
 "Reported Variables and Units": "Cd, In, Tl, Bi (µg/g)" + D + "Tables 3–5; detection limits in pg/ml and ng/g",
 "Monitored Masses": "111Cd → Cd; 115In → In; 205Tl → Tl; 209Bi → Bi; 95Mo, 113Cd, 118Sn, 149Sm → none" + D + "Table 1; '113Cd was not used for Cd determination, because the correction of 113In was far larger than the MoO correction'",
 "Dwell Time per Mass": "95Mo, 111Cd, 113Cd, 115In, 118Sn, 149Sm: 0.11 ms; 205Tl, 209Bi: 0.18 ms" + D + "'ms per 1 s' (Table 1)",
 "Analysis Sequence": "Multi-element standard solution after every third sample, Mo standard solution after every sixth sample" + D + "each measurement ~6 min, including ~200 s wash",
 "Wash Time Between Samples": "~200 s with 0.5 mol/l HNO3" + D + "0.5 mol/l HF aspirated for 200 s after the Mo standard",
 "Internal Standard Element": "all: Sm (149Sm)" + D + "the spike isotope (ID-IS)",
 "Internal Standard Concentration": "N" + D + "Sm at 1.22 ng/ml in the calibrator",
 "Oxide Production Method and Threshold": "CeO+/Ce+ < 0.01 under the operating conditions" + D + "MoO+/Mo+ from a Mo standard every sixth sample, 0.8–7.4 × 10⁻⁴ during the study",
 "Drift Correction Method": "Mass discrimination corrected with the mean elemental ratios of the calibrator measured before and after each sample" + D + "step (d)",
 "Calibration Strategy per Target Species": "Cd, In, Tl, Bi: isotope dilution–internal standardisation (ID-IS) against 149Sm" + D + "Eq. 2; Sm by isotope dilution (Eq. 1)",
 "Blank / Background Correction Method": "N",
 "Spectral Interference Corrections Applied": "Y" + D + "MoO⁺ on ¹¹¹Cd, ¹¹⁵Sn on ¹¹⁵In; ⁷¹Ga⁴⁰Ar⁺ on ¹¹¹Cd < 0.3%, negligible",
 "Interfering Species": "111Cd: 95Mo16O+ and 71Ga40Ar+; 113Cd: 97Mo16O+ and 113In+; 115In: 115Sn+; other: N" + D + "Table 1",
 "Interference Correction Method": ("111Cd: (95MoO+ + 94MoOH+) subtracted using the mean MoO+/Mo+ of the Mo standard measured before and after the sample; "
                                    "115In: isobaric correction with 115Sn/118Sn = 0.014; 113Cd: net 113In with 113In/115In = 0.0448; other: N" + D + "steps (b)–(c)"),
 "Isotope Dilution Data Reduction Method": "Eq. 1 for Sm (ID), with the pseudo-concentration Q calibrated on spike-standard mixtures, and Eq. 2 for Cd, In, Tl and Bi (ID-IS)" + D + "details in " + MN,
 "Memory Effect Mitigation": "~200 s wash with 0.5 mol/l HNO3, and 200 s with 0.5 mol/l HF after the Mo standard, since Mo was difficult to wash out with HNO3",
 "Calibration Factor and Determination Method": "Cd, In, Tl, Bi: relative concentration factor f_G against Sm, from the calibrator measured before and after the sample" + D + "Eq. 2",
 "Uncertainty Propagation Method": "Cd: total uncertainty estimated < 7%, from matrix and oxide errors (< 3% and < 5%) and an intermediate precision of 3%; other: N",
 "Constants and Reference Values Used": "115Sn/118Sn = 0.014 and 113In/115In = 0.0448 (Rosman and Taylor 1998); 94Mo/95Mo = 0.58; MoOH+/MoO+ ~0.15 (measured); 111Cd/113Cd = 1.05 as reference",
 "Primary Calibration Standard Name": "all [Cd, Tl, Bi: multi-element standard solution, 0.110 ng/ml; In: the same solution, 0.111 ng/ml]" + D + "with Sm at 1.22 ng/ml",
 "Calibration Standard Measurement Frequency": "After every third sample",
 "Secondary Reference Materials": RMS_IG + ", " + RMS_NIST + D + "the chondrites are samples",
 "Detection Limit": "Cd: 0.8; In: 0.2; Tl: 0.9; Bi: 0.2" + D + "3s, in pg/ml in solution and in ng/g in silicates at DF 1000 (Table 1)",
 "Detection Limit Method": "all: 3s of the background signal of 0.5 mol/l HNO3, average of eight sessions" + D + "Results",
 "Within-Session Analytical Precision and Assessment Method": "all [Cd: 2.0%; In, Tl, Bi: 1.6%]" + D + "RPD of X/¹⁴⁹Sm between neighbouring calibrator runs (Table 1)",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": ("JB-2, JB-3, JA-1, JA-2, JA-3, BHVO-1, AGV-1 [Cd: 3–10%]; JP-1, PCC-1, DTS-1 [Cd: 7–16%]; "
                                                                             + RMS_NIST + " [Cd: 2–3%; In: 0.7–3%; Tl: 6–12%; Bi: 1–4%]" + D + "intermediate precision, RSD of n = 4–8 separate decompositions (Tables 3 and 4)"),
 "Analytical Accuracy and Assessment Method": ("JB-2, JB-3, JA-1, JA-2, JA-3 [Cd: broadly similar to the reference values of Govindaraju (1994) and Imai et al. (1995)]; "
                                               "BHVO-1, AGV-1 [Cd: differ from those reference values]" + D + "Table 3; In, Tl and Bi compared with previous studies"),
 "Additional Notes": "ICP operating conditions as in " + MN + "; pseudo-flow injection with transient signals integrated as total counts, ~0.013 ml per measurement; an evaporation test showed no loss of Cd, In, Tl or Bi (ratios 0.996–0.999, Table 2)",
}
# ---- c4_long
D = " — "
LQ = "'analyzing atomic masses from 23 (Na) to 75 (As) in a collision-reaction cell, utilizing helium gas at a flow rate of 5 mL/min' (Methods)"
COL4 = {  # Long et al. 2025 (Nature Communications), Agilent 7900 at IPGP. Read 2026-09-30: Methods ("Major and trace elements", "Zinc isotopes"). One paragraph.
 "Coupled Technique(s)": "MC-ICP-MS" + D + "Zn isotopes on a Thermo Neptune Plus at IPGP (Methods)",
 "Coupling Description": "N" + D + "the elements are measured by Q-ICP-MS and the Zn isotopes by MC-ICP-MS; whether on the same solutions is not stated",
 "Target Material": "carbonaceous chondrite" + D + "CM, CY, CV, CR and CO chondrites (abstract and text)",
 "Chromatographic Separation Applied": "N" + D + "the chemical purification described is for the Zn isotopes",
 "Mass Resolution Setting": "N",
 "Collision/Reaction Cell (CRC) Configuration": "m/z 23–75: collision-reaction cell with helium; other: N" + D + LQ + "; the masses are not listed",
 "Collision Gas Type": "m/z 23–75: He; other: N" + D + LQ,
 "Collision Gas Flow Rate": "5 mL/min" + D + LQ,
 "Desolvation System": "N",
 "Plasma Thermal Mode": "N",
 "Target Species": "N" + D + "'The elemental content of samples was analyzed' (Methods); the element list is in Tables S1–S2",
 "Reported Variables and Units": "N" + D + "concentrations in µg/g in the text (e.g. '[Zn] = 309 µg/g'); the list is in Tables S1–S2",
 "Internal Standard Element": "all: Sc, In, Re" + D + "'added to the sample solutions to correct for any signal drift and matrix effects' (Methods)",
 "Drift Correction Method": "Sc, In and Re internal standards" + D + "Methods",
 "Calibration Strategy per Target Species": "all: external calibration on a mixture of certified standards across a range of concentrations, with Sc, In and Re as internal standards" + D + "Methods",
 "Spectral Interference Corrections Applied": "N" + D + "polyatomic interferences were 'mitigated' with He in the collision-reaction cell, not corrected",
 "Calibration Factor and Determination Method": "N" + D + "'A mixture of certified standards was measured across a range of concentrations to convert count measurements into solution concentrations' (Methods)",
 "Primary Calibration Standard Name": "all [all: a mixture of certified standards]" + D + "not named (Methods)",
 "Additional Notes": "The Zn-isotope procedure digests ~35 mg of bulk powder in HNO3-HF at 120 °C for ~48 h; the digestion for the elemental analysis is not stated" + D + "Methods",
}
# ---- c5_lu
D = " — "
RMS_LUQ = "JB-1, JB-2, JB-3, JA-1, JA-2, JA-3, JP-1, BHVO-1, AGV-1, PCC-1, DTS-1"
LUM = [("10B, 11B", "B"), ("90Zr, 91Zr", "Zr"), ("93Nb", "Nb"), ("95Mo, 97Mo", "Mo"), ("118Sn, 119Sn", "Sn"), ("121Sb, 123Sb", "Sb"), ("178Hf, 179Hf", "Hf"), ("181Ta", "Ta")]
COL5 = {  # Lu et al. 2007 (Chemical Geology 236), Agilent 7500cs at PML. Read 2026-09-30: §2.1.1, Tables 1a, 2a and 4, §2.2–2.8, §3.6–3.7. The ICP-SFMS half is in Solution SF.
 "Coupled Technique(s)": "SF-ICP-MS" + D + "Ti on a Finnigan ELEMENT at PML (§2.1.2)",
 "Coupling Description": "The Q-ICP-MS measures B, Zr, Nb, Mo, Sn, Sb, Hf and Ta, and its Nb (from Nb/Mo and Nb/Zr) is used for the SF-ICP-MS Ti calculation on the same solutions" + D + "§2.5, §2.8",
 "Target Material": "basalt; andesite; peridotite; carbonaceous chondrite" + D + "GSJ and USGS RMs, and Ivuna, Orgueil, Cold Bokkeveld and Allende",
 "Sample Preparation Method": "Powders weighed with the B, Zr–Hf and Mo–Sn–Sb spikes and decomposed with 30 mol/l HF and mannitol, dried, dissolved in 0.5 mol/l HF, fluorides removed by centrifuging, and the supernatant diluted" + D + "§2.5; GSJ samples and PCC-1 further pulverised (§2.3)",
 "Digestion Step": ("ultrasonic HF decomposition (basalts and andesites, <70 °C); bomb HF decomposition (peridotites and meteorites, 245 °C, mannitol added after heating); "
                    "re-dissolution (dried, then 5 ml 0.5 mol/l HF in an ultrasonic bath, fluorides removed by centrifuging)" + D + "abstract; §2.5"),
 "Digestion Acid(s)": "ultrasonic HF decomposition: 30 mol/l HF; bomb HF decomposition: 30 mol/l HF; re-dissolution: 0.5 mol/l HF" + D + "§2.5",
 "Digestion Temperature": "ultrasonic HF decomposition: <70 °C; bomb HF decomposition: 245 °C; re-dissolution: N" + D + "abstract",
 "Digestion Vessel Type": "Teflon (TFM-PTFE) bomb for peridotites and meteorites" + D + "§2.2.3, §2.5",
 "Final Solution Matrix": "all: 0.5 mol/l HF with mannitol, diluted" + D + "'The mannitol and HF concentrations in all samples and standard solutions were diluted to be similar to each other' (§2.5)",
 "Sample Aliquot Mass or Volume": "~20 mg (basalts and andesites); ~50 mg (peridotites); ~10 mg (meteorites)" + D + "§2.5",
 "Chromatographic Separation Applied": "None" + D + "the method 'does not require ion-exchange separation' (§1); only the Zr–Hf spike was purified",
 "Isotope Dilution Spike": "10B spike; 91Zr–179Hf mixed spike; 97Mo–119Sn–121Sb mixed spike" + D + "§2.2.2–2.2.4; Nb and Ta are not spiked",
 "Torch Type": "Quartz glass torch with Pt injector" + D + "Table 1a",
 "Spray Chamber Type and Cooling Temperature": "Scott double-pass, cooled at 2 °C, made of Teflon" + D + "Table 1a",
 "Guard Electrode": "Shield torch used" + D + "§2.1.1",
 "Mass Resolution Setting": "N",
 "Collision/Reaction Cell (CRC) Configuration": "all: no gas introduced into the octopole collision cell" + D + "'collision gases were not introduced into the cell' (§2.1.1)",
 "Detector Configuration": "Pulse counting and analog (>10^6 cps), switched automatically" + D + "Zr, Nb, Mo and Sb sometimes in analog at DF < ~250 (§2.1.1)",
 "Desolvation System": "N",
 "Sample Uptake Rate": "N" + D + "self-aspiration (Table 1a); pseudo-FI uses 0.013 ml per sample (§2.6)",
 "Make-up Gas and Flow Rate": "Ar, 0.25 l/min" + D + "Table 1a",
 "Plasma Thermal Mode": "N" + D + "plasma power 1.6 kW (Table 1a)",
 "ICP Tuning": "N",
 "Target Species": "B, Zr, Nb, Mo, Sn, Sb, Hf, Ta" + D + "Ti is measured by the SF-ICP-MS",
 "Reported Variables and Units": "B, Zr, Nb, Mo, Sn, Sb, Hf, Ta (µg/g)" + D + "Tables 5–8; Nb from Nb/Zr and Nb/Mo, Ta from Ta/Mo and Ta/Hf, and their averages",
 "Monitored Masses": "; ".join("%s → %s" % p for p in LUM) + D + "'In one scan, 10B, 11B, 90Zr, ... and 181Ta were measured' (§2.1.1)",
 "Dwell Time per Mass": "10B, 11B: 0.0801 s; 90Zr, 91Zr: 0.0032 s; 93Nb: 0.0320 s; 95Mo, 97Mo, 118Sn, 119Sn, 121Sb, 123Sb: 0.0481 s; 178Hf, 179Hf: 0.0641 s; 181Ta: 0.2083 s" + D + "integration time per 1 s (Table 2a)",
 "Number of Scans per Replicate": "all: 48 scans in 30 s, 1 point per mass" + D + "Table 1a",
 "Analysis Sequence": "Standard solution every two samples; each sample ~6 min including ~3 min wash. Pseudo-FI: a 40 s background step with the probe in the sample, then 30 s of sample signal" + D + "§2.1.1, §2.6",
 "Wash Time Between Samples": "~3 min with 0.5 mol/l HF" + D + "§2.1.1; background measured after a 200 s wash (Table 1a)",
 "Signal Collection Mode": "1 point per mass" + D + "Table 1a",
 "Internal Standard Element": "all: the ID-determined Zr, Mo and Hf, as references for Nb and Ta (ID-IS)" + D + "§2.8, §3.5; Mo is preferred",
 "Internal Standard Concentration": "N/A",
 "Oxide Production Method and Threshold": "CeO+/Ce+ < 1%" + D + "Table 1a",
 "Drift Correction Method": "Mass discrimination from the standard solution average, usually without drift over 2 h; when drift was observed, the standard measured before and after the sample was averaged" + D + "§2.7, §2.8",
 "Calibration Strategy per Target Species": "B, Zr, Mo, Sn, Sb, Hf: isotope dilution (Eq. 1); Nb, Ta: isotope dilution–internal standardisation (ID-IS) against Zr, Mo or Hf" + D + "§2.7, §2.8",
 "Blank / Background Correction Method": "Background measured before each sample after a 200 s wash, and procedural blank corrections from Table 4 applied to all analyses" + D + "Table 1a; §3.6, corrections usually <1% in basalts and andesites and <4% in peridotites and meteorites",
 "Pulse/Analog Detector Nonlinearity Correction": "all: P/A factor determined each day before measurement" + D + "§2.1.1",
 "Spectral Interference Corrections Applied": "N",
 "Isotope Dilution Data Reduction Method": "Eq. 1 with the pseudo-concentration Q calibrated on spike–standard mixtures, and the mass discrimination correction factor applied to the measured ratios" + D + "§2.7",
 "Memory Effect Mitigation": "0.5 mol/l HF as carrier and wash, which washes out Zr, Nb, Hf and Ta; ~20 min of 0.5 mol/l HF after REE work in HNO3" + D + "§2.1.1",
 "Calibration Factor and Determination Method": ("B, Zr, Mo, Sn, Sb, Hf: mass discrimination correction factor, natural ratio over the measured standard average (0.87–0.96 for 11B/10B, 0.94–1.04 for the others); "
                                                 "Nb, Ta: relative concentration factor f_J against the reference element, from the standard solution" + D + "§2.7, §2.8"),
 "Constants and Reference Values Used": ("Spike ratios 91Zr/90Zr 29.0, 97Mo/95Mo 201, 119Sn/118Sn 30.1, 121Sb/123Sb 199, 179Hf/178Hf 25.1, against natural 0.218, 0.600, 0.355, 1.34, 0.499 (Rosman and Taylor 1998); "
                                         "11B/10B spike 0.05348 and natural 4.053 by TIMS (Makishima et al. 1997)" + D + "§2.7"),
 "Procedural Blank Level": "B: 13–185 pg (ultrasonic); Zr: 0.9–29, 55; Nb: 2–5, 3; Mo: 0.2–10, ~134; Sn: ~323, ~276; Sb: 0.7–9, ~60; Hf: <12, <8; Ta: 0.6–7, 0.6–2" + D + "total procedural blank in pg, ultrasonic then bomb method (Table 4)",
 "Primary Calibration Standard Name": ("all [B, Zr, Nb, Mo, Hf, Ta: mixed standard solution from the Alfa Aesar Specpure refractory metals plasma standard (Stock No. 44270); "
                                       "Sn, Sb: the same mixed solution, from Kanto Kagaku AAS solutions]" + D + "§2.2.6; isotope and element ratios checked against CLMS-4 (Spex)"),
 "Calibration Standard Measurement Frequency": "Every two samples" + D + "§2.1.1",
 "Secondary Reference Materials": RMS_LUQ + D + "§2.3; the chondrites are samples",
 "Detection Limit": "B: 45 (10B), 11 (11B); Zr: 13 (90Zr), 43 (91Zr); Nb: 1; Mo: 2 (95Mo), 14 (97Mo); Sn: 3 (118Sn), 5 (119Sn); Sb: 2 (121Sb), 0.7 (123Sb); Hf: 0.7 (178Hf), 1 (179Hf); Ta: 0.3" + D + "ng/g in rock, 3σ (Table 2a); in solution, in pg/g",
 "Detection Limit Method": "all: 3σ, calculated for silicate samples at the dilution factor of ~340 where matrix effects are absent" + D + "§3.6",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": ("B: 2.4% (11B/10B); Zr: 3.2% (91Zr/90Zr); Nb: 3.1% (93Nb/91Zr), 0.8% (93Nb/97Mo); Mo: 1.0% (97Mo/95Mo); "
     "Sn: 0.7% (119Sn/118Sn); Sb: 0.6% (121Sb/123Sb); Hf: 0.5% (179Hf/178Hf); Ta: 2.4% (181Ta/97Mo), 0.5% (181Ta/179Hf)" + D + "RSD% of each ratio measurement, ranges in Table 2a"),
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": RMS_LUQ + " [all: average reproducibility 1.0–4.6% RSD]" + D + "§3.7, Tables 5–6; Mo in JB-1 (15%) excluded as heterogeneous",
 "Analytical Accuracy and Assessment Method": RMS_LUQ + " [all: compared with reference values (Govindaraju 1994, Imai et al. 1995 and others)]" + D + "Tables 5–6; 'a significant difference exists for B in JA-2'",
 "Additional Notes": "Pseudo-flow injection with the ASX-100 autosampler; recovery yields from Ca–Al–Mg fluorides tested in 19 synthetic solutions (§2.4, §2.6)",
}
# ---- c678_gildiaz
D = " — "
TRI = ("tri-acid digestion (30 mg in closed PP DigiTUBEs on a heating block, 2 h at 110 °C, with 750 µL 14 M HNO3, 1.5 mL 10 M HCl and 2.5 mL 29 M HF); "
       "re-dissolution (evaporated at 120 °C, re-dissolved with 250 µL 14 M HNO3 and heating, brought to 10 mL with Milli-Q water)")
TRI_ACID = "tri-acid digestion: 14 M HNO3 + 10 M HCl + 29 M HF; re-dissolution: 14 M HNO3"
MW = ("microwave digestion (40–50 mg, START 1500, 3 mL 65% HNO3, 0.5 mL 30% H2O2, 0.25 mL 40% HF and 0.5 mL Milli-Q water, ramped to 210 °C and held 10 min, cooled overnight); "
      "Se recovery (evaporated to dryness at 70 °C in PTFE vessels, recovered with 270 µL 65% HNO3 at 70 °C for 1 h, made up to 6 mL)")
EXTR = ("F1 acetate (500 mg, 10 mL 1 M NaOAc with 5 M HOAc pH adjustment, 6 h shaking at 25 °C); F2 ascorbate (200 mg, 12.5 mL ascorbate solution pH 8, 24 h at 25 °C); "
        "F3 H2O2 (500 mg, 2.5 mL 30% H2O2 at pH 5 + 1.5 mL 30% H2O2 + 2.5 mL 1 M ammonium acetate, 2 h + 3 h at 85 °C + 30 min shaking at 25 °C); "
        "F4 HCl (200 mg, 12.5 mL 1 M HCl, 24 h at 25 °C); F4N HNO3 (200 mg, 12.5 mL 1 M HNO3, 24 h at 25 °C)")
S23, S24 = "§2.3", "§2.4"
COL6 = {  # Gil-Díaz et al. 2020 (Chemical Geology 532) — Agilent 8800, Basel: Te and 77Se in the particle digestates of the 1000 mg/L SPM isotherm. Read §2.2–2.4.
 "Target Material": "suspended particulate matter" + D + "digestates of the particles from the 1000 mg/L SPM isotherm experiments in freshwater (" + S23 + ", " + S24 + ")",
 "Sample Preparation Method": "SPM recovered by centrifugation, oven dried, ground in agate mortars and totally digested: tri-acid for Te, microwave for Se (Se is volatile above 70 °C)" + D + "§2.2",
 "Digestion Step": TRI + "; " + MW + D + "§2.2; the first two steps for Te, the last two for Se",
 "Digestion Acid(s)": TRI_ACID + "; microwave digestion: HNO3 + H2O2 + HF; Se recovery: 65% HNO3" + D + "§2.2",
 "Digestion Temperature": "tri-acid digestion: 110 °C; re-dissolution: 120 °C (evaporation); microwave digestion: up to 210 °C; Se recovery: 70 °C" + D + "§2.2",
 "Digestion Duration": "tri-acid digestion: 2 h; microwave digestion: 10 min at 210 °C, then cooled overnight; Se recovery: 1 h; other: N" + D + "§2.2",
 "Digestion Vessel Type": "Closed PP tubes (DigiTUBEs, SCP Science) for Te; microwave vessels (START 1500, MLS) then PTFE vessels for Se" + D + "§2.2",
 "Final Solution Matrix": "N" + D + "Te digests brought to 10 mL with Milli-Q water, Se digests to 6 mL (§2.2)",
 "Sample Aliquot Mass or Volume": "30 mg (Te, tri-acid); 40–50 mg (Se, microwave)" + D + "§2.2",
 "Collision/Reaction Cell (CRC) Configuration": "125Te, 77Se: oxygen-shift mode with O2 as cell gas; other: N" + D + S23 + ", " + S24,
 "Target Species": "Te, Se",
 "Reported Variables and Units": "Te, Se" + D + "particulate concentrations from the digestates; units not stated for this instrument",
 "Monitored Masses": "125Te → Te; 77Se → Se; 103Rh → none" + D + "the spiked isotopes; ¹⁰³Rh is the internal standard",
 "Collision Gas Type": "125Te, 77Se: O2; other: N" + D + "'oxygen-shift mode using O2 as collision gas' (" + S23 + ")",
 "Reaction Gas Type": "N" + D + "the paper calls the O2 a collision gas",
 "Reaction Product Ion / Mass-Shift Transition": "125Te: 125Te + 16O → 141TeO; 77Se: 77Se + 16O → 93SeO; other: N" + D + S23 + ", " + S24,
 "Internal Standard Element": "all: 103Rh" + D + "'to correct for matrix effects' (" + S23 + ")",
 "Calibration Strategy per Target Species": "Te, Se: external calibration with 103Rh as internal standard" + D + S23 + ", " + S24,
 "Spectral Interference Corrections Applied": "N" + D + "the O2 mass shift avoids 'doubly charged Rare Earth Element (REE) interferences' on ⁷⁷Se rather than correcting them",
 "Interfering Species": "77Se: doubly charged REE, mainly 154Sm++ and 154Gd++; other: N" + D + S24,
 "Interference Correction Method": "77Se: avoided by the oxygen-shift mode; other: N" + D + S24,
 "Secondary Reference Materials": "NCS 73307" + D + "stream sediment, for the total digestions",
 "Analytical Accuracy and Assessment Method": "NCS 73307 [Te: 94 ± 17% recovery (N = 3); Se: 70–134% recovery (N = 3)]" + D + S23 + ", " + S24,
 "Combination Method": "all: mean ± SD of N = 3" + D + "'mean ± SD recovery values of 94 ± 17% (N = 3)'",
}
COL7 = {  # Gil-Díaz et al. 2020 — Thermo iCAP-TQ: Te in total digestions and selective extractions (KED and O2 modes), Se in selective extractions (O2 mode). Read §2.2–2.4, Table 1.
 "Target Material": "sediment" + D + "suspended particulate matter: total digestions and the selective-extraction fractions F1–F4 and F4N",
 "Sample Preparation Method": "SPM recovered by centrifugation, oven dried (70 °C), ground in agate mortars and aliquoted for tri-acid total digestion and parallel selective extractions (two replicates per extraction mode)" + D + "§2.2, Table 1",
 "Digestion Step": TRI + "; " + EXTR + D + "§2.2 and Table 1 (after Audry et al. 2006)",
 "Digestion Acid(s)": TRI_ACID + "; F1 acetate: 1 M NaOAc + 5 M HOAc; F2 ascorbate: ascorbate solution; F3 H2O2: 30% H2O2 + 1 M ammonium acetate; F4 HCl: 1 M HCl; F4N HNO3: 1 M HNO3",
 "Digestion Temperature": "tri-acid digestion: 110 °C; re-dissolution: 120 °C (evaporation); F1 acetate, F2 ascorbate, F4 HCl, F4N HNO3: 25 °C; F3 H2O2: 85 °C, then 25 °C",
 "Digestion Duration": "tri-acid digestion: 2 h; F1 acetate: 6 h; F2 ascorbate, F4 HCl, F4N HNO3: 24 h; F3 H2O2: 2 h + 3 h, then 30 min; other: N",
 "Digestion Vessel Type": "Closed PP tubes (DigiTUBEs, SCP Science) for the total digestion; acid-washed PP Falcon 50 mL tubes for the extractions" + D + "§2.2",
 "Final Solution Matrix": "N" + D + "digests brought to 10 mL with Milli-Q water; extracts in their extraction reagents",
 "Sample Aliquot Mass or Volume": "30 mg (total digestion); 200–500 mg per extraction" + D + "§2.2, Table 1",
 "Chromatographic Separation Applied": "None",
 "Acquisition Pass": "KED; O2 mode" + D + "'126Te measured in KED-mode (He)'; '125Te ... in mass-shift O2-mode'; Se 'with the O2-mode' (" + S23 + ", " + S24 + ")",
 "Number of Acquisition Passes": "2",
 "Collision/Reaction Cell (CRC) Configuration": "126Te: KED with He; 125Te, 77Se, 78Se, 80Se, 82Se: mass-shift O2 mode; other: N" + D + S23 + ", " + S24,
 "Target Species": "Te, Se" + D + "natural Te from ¹²⁶Te, spiked Te from ¹²⁵Te; natural Se from ⁷⁸Se, ⁸⁰Se, ⁸²Se, spiked Se from ⁷⁷Se",
 "Reported Variables and Units": "Te, Se (mg/kg)" + D + "particulate concentrations",
 "Monitored Masses": "125Te, 126Te → Te; 77Se, 78Se, 80Se, 82Se → Se" + D + S23 + ", " + S24,
 "Collision Gas Type": "126Te: He; 125Te, 77Se, 78Se, 80Se, 82Se: O2; other: N" + D + S23 + ", " + S24,
 "Reaction Gas Type": "N" + D + "the O2 mode is named, not its gas role",
 "Reaction Product Ion / Mass-Shift Transition": "N" + D + "'mass-shift O2-mode'; the product ions are not stated for this instrument",
 "Calibration Strategy per Target Species": "Te, Se: external calibration" + D + S23 + ", " + S24,
 "Spectral Interference Corrections Applied": "Y" + D + "⁸⁶Sr⁴⁰Ar, ¹¹⁰Cd¹⁶O, ¹¹⁰Pd¹⁶O and ¹²⁶Xe on ¹²⁶Te corrected; Se polyatomic interferences eliminated by the O2 mode",
 "Interfering Species": "126Te: 86Sr40Ar, 110Cd16O, 110Pd16O and 126Xe; 77Se: 40Ar37Cl, 154Sm++ and 154Gd++; 78Se: 78Kr, 156Gd++ and 156Dy++; 82Se: 81Br1H and 82Kr; other: N" + D + S23 + ", " + S24,
 "Interference Correction Method": ("126Te: corrections established with respective monoelemental solutions, each influencing < 0.1% (Filella and Rodushkin 2018), and 126Xe from 2% HNO3 analytical blanks; "
                                    "77Se, 78Se, 82Se: eliminated with the O2 mode; other: N" + D + S23 + ", " + S24),
 "Uncertainty Level": "Mean ± SD",
 "Procedural Blank Level": "Te: ~35 µg/L in the F3 extraction blanks; other: N" + D + "three blanks of each extraction; the F3 contamination is attributed to the H2O2 or ammonium acetate (§2.2)",
 "Secondary Reference Materials": "NIST 1643f, NCS 73307, NIST 1640a" + D + "freshwater, stream sediment and freshwater",
 "Analytical Accuracy and Assessment Method": ("NIST 1643f [Te: 95 ± 5% (KED), 89 ± 10% (O2), N = 5; Se: 95 ± 3%]; NCS 73307 [Te: 99 ± 14% (KED), 70 ± 19% (O2), N = 4]; NIST 1640a [Se: 85 ± 2%]"
                                               + D + "recoveries (" + S23 + ", " + S24 + ")"),
 "Detection Limit": "Te: 0.1 ng/L; other: N" + D + "N = 10; natural Te in the extractions 5-fold (F2) to 200-fold (F4) above the LOD",
}
COL8 = {  # Gil-Díaz et al. 2020 — Thermo XSeries 2 (KIT): dissolved Se in the kinetics and isotherm solutions; dissolved Te on an 'X-Series II' with no laboratory named. Read §2.3, §2.4.
 "Target Material": "estuarine water" + D + "filtered freshwater and seawater from the sorption kinetics and isotherm experiments",
 "Acquisition Pass": "Te run; Se run" + D + "dissolved Te 'directly analysed by ICP-MS (X-Series II, Thermo Fisher Scientific)' (" + S23 + "), no laboratory named; dissolved Se on the 'XSeries 2, Thermo Fisher Scientific, KIT' (" + S24 + ")",
 "Number of Acquisition Passes": "2",
 "Final Solution Matrix": "Te run: seawater matrices diluted in 2% HNO3, freshwater analysed directly; Se run: N" + D + S23,
 "Collision/Reaction Cell (CRC) Configuration": "Se masses: CCT mode, collision cell with He:H2; other: N" + D + "the Se masses are not listed; no cell mode is stated for Te (" + S24 + ")",
 "Target Species": "Te, Se",
 "Reported Variables and Units": "Te, Se (µg/L)" + D + "dissolved concentrations",
 "Monitored Masses": "N" + D + "the masses are not stated",
 "Collision Gas Type": "Se masses: He + H2; other: N" + D + S24,
 "Collision/Reaction Gas Mixture Ratio": "Se masses: He:H2 = 92% : 8%; other: N" + D + "'to minimise 40Ar37Cl interferences' (" + S24 + ")",
 "Internal Standard Element": "Se run: 103Rh and 115In; Te run: N" + D + S24,
 "Calibration Strategy per Target Species": "Te: external calibration, in an adapted salty matrix for seawater; Se: external calibration with 103Rh and 115In internal standards" + D + S23 + ", " + S24,
 "Spectral Interference Corrections Applied": "N" + D + "⁴⁰Ar³⁷Cl on Se 'minimised' by the collision cell, not corrected",
 "Interfering Species": "Se masses: 40Ar37Cl; other: N" + D + S24,
 "Interference Correction Method": "Se masses: minimised by the He:H2 collision mixture; other: N" + D + S24,
 "Secondary Reference Materials": "CRM-TMDW, NIST 1643f" + D + "drinking water and freshwater",
 "Analytical Accuracy and Assessment Method": "CRM-TMDW [Se: 98–106% recovery (N = 16)]; NIST 1643f [Se: 100–102% (N = 16); Te: 85–91% (N = 4)]" + D + S23 + ", " + S24,
 "Detection Limit": "Te: 0.01 µg/L; Se: 0.06 µg/L" + D + "N = 10 (" + S23 + ", " + S24 + ")",
 "Combination Method": "Te, Se: mean of the replicate experiments at each condition" + D + "Figs 1–2: kinetics N = 3, isotherms N = 2; 'Error bars correspond to standard deviations (SD)'",
 "Goodness-of-Fit or Dispersion Statistic": "Te, Se: SD" + D + "Figs 1–2",
}
# ---- c9_lopez
D = " — "
REE = "La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu"
G1 = "Li, Be, Sc, Ga, As, Se, Rb, Sr, Y, Ag, Cd, In, Cs, Ba, " + REE + ", Tl, Pb, Bi, Th, U"
G1_SQ = "Li, Be, Sc, Rb, Sr, Y, Ag, Cs, Ba, " + REE + ", Tl, Pb, Bi, Th, U"
G1_O2 = "Ga, As, Se, Cd, In"
G2 = "Na, Mg, Al, P, K, Ca, V, Cr, Mn, Fe, Co, Ni, Cu, Zn"
G2_KED = "Mg, Al, V, Cr, Mn, Fe, Co, Ni, Cu, Zn"
G2_O2 = "Na, P, K, Ca"
G3 = "Ti, Zr, Nb, Hf, Ta, Mo, W"
REP = G1 + ", " + G2 + ", Ti, Zr, Nb, Hf, Mo"
COL9 = {  # López García et al. 2026 (Meteoritics & Planetary Science), iCAP TQ at Institute of Science Tokyo. Read 2026-09-30: Materials and Methods, Table 1 and its note.
 "Target Material": "carbonaceous asteroid particle; carbonaceous chondrite" + D + "eight Ryugu TD1 particles, and the Smithsonian Allende powder for reproducibility",
 "Sample Preparation Method": "Particles individually weighed on a Mettler Toledo XPR2U microbalance (0.1 µg readability) and transferred to PFA vials without powdering" + D + "ISO class 5 cleanroom; acids distilled once",
 "Digestion Step": ("HF-HNO3 attack (0.2 mL HF + 0.1 mL HNO3 + 0.4 mL water, 3 h in an ultrasonic bath, then capped 12 h at 120 °C and 5 days at 220 °C, dried at 100 °C); "
                    "HNO3-HCl step (0.2 mL HNO3 + 0.2 mL HCl + 0.2 mL H2O, sealed, 150 °C for 1 day, dried at 100 °C); "
                    "HNO3 step (0.2 mL HNO3 + 0.2 mL H2O, 80 °C for 1 day, dried at 90 °C); final uptake (5 mL 0.5 M HNO3)" + D + "Acid digestion"),
 "Digestion Acid(s)": "HF-HNO3 attack: HF + HNO3; HNO3-HCl step: HNO3 + HCl; HNO3 step: HNO3; final uptake: 0.5 M HNO3",
 "Digestion Temperature": "HF-HNO3 attack: 120 °C, then 220 °C; HNO3-HCl step: 150 °C; HNO3 step: 80 °C; final uptake: N",
 "Digestion Duration": "HF-HNO3 attack: 3 h ultrasonic, 12 h, then 5 days; HNO3-HCl step: 1 day; HNO3 step: 1 day; final uptake: N",
 "Digestion Vessel Type": "PFA hexagonal cap vials (6 mL, Savillex), tightly capped with polypropylene wrenches" + D + "'to maintain high-pressure–temperature conditions'",
 "Final Solution Matrix": "Group-1: 0.5 M HNO3, DF 20,000; Group-2: 0.5 M HNO3, DF 200,000; Group-3: 0.5 M HNO3 with ~0.05 M HF, DF 20,000" + D + "digests in 5 mL 0.5 M HNO3 at DF 1200–3400",
 "Sample Aliquot Mass or Volume": "1.478–4.325 mg per particle; 20 mg of Allende" + D + "4%–10% aliquots for Group-1 and Group-3, 0.4 mL of the Group-1 solution for Group-2",
 "Isotope Dilution Spike": "113In–203Tl (Group-1, ID-IS); 49Ti; 91Zr–179Hf; 97Mo–182W (Group-3)" + D + "with enrichments and concentrations stated (Methods)",
 "Collision/Reaction Cell (CRC) Configuration": (G1_SQ + ": non-gas SQ mode; " + G1_O2 + ", " + G2_O2 + ": O2 mode; " + G2_KED + ", " + G3 + ": He KED mode" + D + "Methods"),
 "Acquisition Pass": "Group-1; Group-2; Group-3" + D + "the grouping of Yokoyama, Nagashima, et al. (2023), each on its own solution",
 "Number of Acquisition Passes": "3",
 "Target Species": G1 + ", " + G2 + ", " + G3 + D + "54 elements in three groups",
 "Reported Variables and Units": REP + " (µg/g)" + D + "Table 1; 'Although the abundances of Ta and W were measured, the data for these elements were excluded from the results due to high blank contributions (>30%)'",
 "Monitored Masses": "N" + D + "the analytical masses are in the supplementary data; the spike isotopes are ¹¹³In, ²⁰³Tl, ⁴⁹Ti, ⁹¹Zr, ¹⁷⁹Hf, ⁹⁷Mo and ¹⁸²W, with ¹⁰³Rh as internal standard",
 "Collision Gas Type": G2_KED + ", " + G3 + ": He; " + G1_O2 + ", " + G2_O2 + ": O2; other: N" + D + "Group-1 otherwise in non-gas SQ mode",
 "Reaction Gas Type": "N" + D + "the O2 mode is named, not its gas role",
 "Reaction Product Ion / Mass-Shift Transition": "N",
 "Internal Standard Element": "Group-1: 103Rh, with the 113In–203Tl ID-IS; Group-2: 103Rh; Group-3: 91Zr and 179Hf, for Nb and Ta" + D + "Methods",
 "Calibration Strategy per Target Species": (G1 + ": 113In–203Tl ID-IS (Yokoyama et al. 2017); " + G2 + ": calibration curve with 103Rh internal standardisation; "
                                             "Ti, Zr, Mo, Hf, W: isotope dilution; Nb, Ta: ID-IS with 91Zr and 179Hf" + D + "Methods; Kagami and Yokoyama (2021) for Group-3"),
 "Isotope Dilution Data Reduction Method": "ID-IS of Yokoyama et al. (2017) for Group-1 and of Kagami and Yokoyama (2021) for Group-3, isotope dilution for Ti, Zr, Mo, Hf and W",
 "Uncertainty Level": "2σ" + D + "Table 1",
 "Primary Calibration Standard Name": ("all [" + G1 + ": XSTC-13 and XSTC-1 (SPEX CertiPrep); " + G2 + ": XSTC-13 and a custom P-Ca solution from single-element standards (Fujifilm-Wako); "
                                       + G3 + ": MISA05-1 (AccuStandard)]" + D + "Methods"),
 "Secondary Reference Materials": "Smithsonian Allende powder" + D + "20 mg, dissolved and measured under the same procedure, n = 5",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "N" + D + "the Allende replicate averages and uncertainties are in the supplementary materials",
 "Combination Method": "all: average of the replicates (n = 5) for the Allende powder, and the average of the eight Ryugu particles" + D + "'The average abundance of the eight samples aligns within 20% of the average CI composition'",
 "Additional Notes": "Group-1 dilution made after at least 30 min ultrasonic homogenisation 'to avoid elemental fractionation in the solution'; 175 µL of 100 ng/g Rh added as internal standard" + D + "Methods",
}
# ---- engine
COLS = [  # column number -> label substring
 (1, "Hu+Gao2008", COL1), (2, "Yu+etal2005", COL2), (3, "Makishima+etal2011", COL3), (4, "Long+etal2025", COL4),
 (5, "Lu+etal2007", COL5), (6, "GilDiaz+etal2020 | Agilent 8800", COL6), (7, "GilDiaz+etal2020 | Thermo iCAP-TQ", COL7),
 (8, "GilDiaz+etal2020 | Thermo XSeries 2", COL8), (9, "LopezGarcia+etal2026", COL9),
]
UPB_ONLY = []  # no U-Pb twin
NODATE = "N — the procedure reports no date"
TAPPS = ["Solution_Q-ICP-MS_TAPP_v"]


def clean(v):
    v = re.sub(r"\s*\[P[0-9][^\]]*\]", "", v)
    v = re.sub(r"\s*\[P20-Ack\]", "", v)
    m = re.match(r"^(N/A|N)\s*\((.*)\)\s*$", v, re.S)
    if m:
        v = "%s — %s" % (m.group(1), m.group(2))
    return v.replace(" (same as silicate protocol)", "")


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def edit(rr, report):
    h = rr[0]; s = h.index("Literature Assessment")
    labs = {j: " ".join(h[j].split()) for j in range(s + 1, len(h)) if h[j].strip()}
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    proc = {r[0].strip() for r in rr[1:] if r and len(r) > 2 and r[2].strip()}
    for n, sub, cells in COLS:
        js = [j for j, l in labs.items() if sub in l]
        if not js:
            continue
        if len(js) != 1:
            raise SystemExit("PREMISE: %r matches %d columns" % (sub, len(js)))
        j = js[0]
        for f, v in cells.items():
            if f not in by:
                raise SystemExit("PREMISE: no field %r" % f)
            if by[f][j] != v:
                report.append((n, f, by[f][j], v)); by[f][j] = v
        for f in UPB_ONLY:
            if f in by and not by[f][j].strip():
                report.append((n, f, "", NODATE)); by[f][j] = NODATE
        for f in proc:
            if f in cells or f not in by:
                continue
            old = by[f][j]; new = clean(old)
            if new != old:
                report.append((n, f, old, new)); by[f][j] = new
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    sim = sys.argv[sys.argv.index("--out-sim") + 1] if "--out-sim" in sys.argv else None
    todo = []
    for pre in TAPPS:
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(pre))
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        report = []
        rr = edit(rows_of(os.path.join(ROOT, rel)), report)
        print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
        if sim:
            os.makedirs(sim, exist_ok=True); write(os.path.join(sim, os.path.basename(new)), rr)
        todo.append((e, rel, new))
    if not apply:
        print("\n(dry run — pass --apply to write; --out-sim DIR writes the edited CSVs for checking)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new in todo:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), []))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
        rp = os.path.join(ROOT, "composed_tapps.json")
        reg = json.load(io.open(rp, encoding="utf-8"))
        for x in reg["composed"]:
            if x["tapp"] == rel:
                x["tapp"] = new
        with io.open(rp, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
