#!/usr/bin/env python3
"""Solution SF-ICP-MS: keyed notation, with every procedure-level cell re-read (2026-09-30).

    python3 "Project Files/Scripts/ssf_keyed_reverify_20260930.py" [--apply] [--out-sim DIR]

The same pass as lasf_keyed_reverify_20260930.py: the literature cells must regenerate each paper's
procedure, so every procedure-level cell of Solution SF's six columns was re-read against its paper, and
the edit was scored by `Project Files/Reports/SSF_Cells_RoundTrip_2026-09-30/roundtrip.py` before it was
applied. Solution SF has no U-Pb twin.

What the re-read found, beyond format (per column in the dicts below):
  * wrong values: Misra's dwell times (Table 3's "samples per peak", 50/100, read as ms; the sample
    times are 0.005–0.05 s) and MR passes (Table 3 gives 5, Table 1 prints 3); Milne's Fe detection
    limit (0.021 nM, not 0.01); Desem's internal precision (the MC-ICP-MS's ±0.001–0.002, not the Attom's);
  * fabricated or borrowed detail: Li's BHVO-2/BCR-2 secondary RMs (FER-2 only); Misra's accuracy
    "against inter-lab consensus values" (the paper compares dilutions of its own consistency standards);
    Willbold's MES said to spike Rb, Y, Nb, Cs, the REE and Th (twelve elements are spiked, none of those
    mono-isotopic ones); Willbold's Ru and Re recorded as internal standards (they correct mass
    fractionation);
  * inverted structure: Misra's `Mass Resolution Assignment` and pulse/analog cells read "LR", "MR"
    and "Applied" as members; its two resolutions are now the Acquisition Pass members, as are
    Willbold's LR and HR solutions;
  * stated facts missing: the isotopes of every column (`Monitored Masses` was `N` or unkeyed),
    Milne's MoO+ regression and Table 4 limits, Lu's two-stage Ti-via-Nb calculation, Misra's
    per-isotope detection modes and Table 4 long-term precision, Willbold's Dixon test, LOQ,
    mass-fractionation power law and combined uncertainty.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
# ---- c1_desem
D = " — "
S4 = "§2.4"
RATIOS = "206Pb/204Pb, 207Pb/204Pb, 208Pb/204Pb, 207Pb/206Pb, 208Pb/206Pb"
RMS = "BCR-2, AGV-2, JB-2, BR, JB-3"
COL1 = {  # Desem et al. 2022 (Applied Geochemistry 143), Nu Attom SC-SF-ICP-MS, Melbourne. Read 2026-09-30: §2.1–2.4, Table 1.
 "Sample Preparation Method": "Soils oven-dried (50 °C, 7 days), not sieved; total-dissolution (TD) and aqua-regia (AR) splits; the SC-SF-ICP-MS splits 'redissolved and diluted to 2 ml in high purity 2% HNO3 doped with 1 ppb of high-purity thallium'" + D + "§2.1, §2.2, " + S4 + "; the rock chips were analysed by MC-ICP-MS only",
 "Digestion Step": ("TD HNO3 leach (3 ml conc. HNO3, 80 °C, 48 h, leachate discarded); TD HF (4 ml conc. HF, 100 °C, 48 h, evaporated); "
                    "TD HNO3 (2 × 1 ml conc. HNO3, 100 °C); TD HCl (5 ml 6 M HCl, 80 °C, 15 h, then centrifuged); "
                    "AR leach (3 ml aqua regia, 3:1 HCl:HNO3, 20 °C, 15 h, then centrifuged)" + D + "§2.2"),
 "Digestion Acid(s)": "TD HNO3 leach: conc. HNO3; TD HF: conc. HF; TD HNO3: conc. HNO3; TD HCl: 6 M HCl; AR leach: aqua regia (3:1 HCl:HNO3)" + D + "§2.2",
 "Final Solution Matrix": "all: 2% HNO3 doped with 1 ppb Tl" + D + S4,
 "Chromatographic Separation Applied": "None" + D + "the SC-SF-ICP-MS splits were analysed unseparated; the anion-exchange separation (§2.3) was for MC-ICP-MS",
 "Detector Configuration": "N" + D + "the Attom's 'deflector peak jump' mode is stated (" + S4 + ")",
 "Instrument Sensitivity": "all: ~1000 kcps/ppb Pb total" + D + "'tuned to provide ~1000 kcps/ppb Pbtotal while maintaining flat-topped peaks' (" + S4 + ")",
 "Target Species": "Pb" + D + "Hg and Tl are monitored: ²⁰²Hg for the Hg interference on ²⁰⁴Pb, ²⁰³Tl and ²⁰⁵Tl for mass bias (" + S4 + ")",
 "Monitored Masses": "204Pb, 206Pb, 207Pb, 208Pb → Pb; 202Hg, 203Tl, 205Tl → none" + D + "'masses 202Hg, 203Tl, 204Pb, 205Tl, 206Tl, 207Pb and 208Pb' (" + S4 + "); '206Tl' is the paper's typo for 206Pb",
 "Dwell Time per Mass": "all: 500 µs" + D + S4,
 "Number of Scans per Replicate": "all: 30 sets of 2000 sweeps" + D + "total analysis time 4.5 min (" + S4 + ")",
 "Number of Replicates": "1" + D + "one acquisition of 30 sets of 2000 sweeps (" + S4 + ")",
 "Wash Time Between Samples": "10 s in each of two 2% HNO3 reservoirs, then a third reservoir for the blank" + D + "the blank solution 'was replaced every 20 samples' (" + S4 + ")",
 "Internal Standard Element": "all: Tl (203Tl, 205Tl), for mass-bias correction" + D + S4,
 "Drift Correction Method": "N",
 "Calibration Strategy per Target Species": "Pb: internal normalisation to 205Tl/203Tl = 2.3871, with Pb mass-bias factors from master Pb vs Tl correlation lines of numerous SRM981 analyses" + D + "§2.3–2.4; SRM981 results 'were primarily used to update the long-term Pb vs Tl mass bias master correlations'",
 "Blank / Background Correction Method": "Blank determination before each sample acquisition (average 900 cps on 208Pb, equivalent to 1.8 ppt Pb); on-line baseline correction" + D + S4,
 "Spectral Interference Corrections Applied": "Y" + D + "'on-line correction for baselines and Hg interference (202Hg/204Pb always <0.043)' (" + S4 + ")",
 "Interfering Species": "204Pb: Hg; other: N" + D + "monitored at 202Hg (" + S4 + ")",
 "Interference Correction Method": "204Pb: on-line correction for Hg interference, monitored at 202Hg; other: N" + D + S4,
 "Uncertainty Level": "2 standard errors for within-run precision; 2sd for the averages of standards" + D + "'Typical within-run precision (2 standards errors)' (" + S4 + "); '(2sd, n = 22)'",
 "Calibration Factor and Determination Method": "all: Pb mass-bias factors from Pb vs Tl mass-bias plots of numerous SRM981 analyses" + D + "'Raw Pb isotope ratios were corrected for instrumental mass fractionation using the measured 205Tl/203Tl and Pb mass bias factors derived from Pb vs Tl isotope mass bias plots generated from numerous analyses of SRM981' (" + S4 + ")",
 "Procedural Blank Level": "Pb: total procedural blank <100 pg" + D + "'total procedural blanks (dissolution and/or leaching, including centrifuging) are estimated to be <100 pg'; sample/blank ratios ≥1500 (§2.3)",
 "Primary Calibration Standard Name": "all [Pb: NIST SRM981]" + D + "for the Pb vs Tl mass-bias master correlations (" + S4 + ")",
 "Reported Variables and Units": RATIOS + D + "dimensionless Pb isotope ratios (" + S4 + ")",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": ("206Pb/204Pb, 207Pb/204Pb: ±0.03–0.06 (±0.17–0.35%); 208Pb/204Pb: ±0.10–0.19 (±0.26–0.50%); "
      "207Pb/206Pb: ±0.0006–0.0012 (±0.07–0.14%); 208Pb/206Pb: ±0.0020–0.0040 (0.09–0.18%)" + D + "'Typical within-run precision (2 standards errors)' (" + S4 + "); the ±0.001–0.002 in §2.3 is the MC-ICP-MS's"),
 "Within-Session Analytical Precision and Assessment Method": RMS + " [all: 2sd of repeat analyses]" + D + "Table 1; 'regular analyses of Tl-doped ~1 ppb solutions of several rock standards (unseparated)' (" + S4 + ")",
 "Analytical Accuracy and Assessment Method": RMS + " [all: % deviation from published Pb isotope values]" + D + "Table 1 and §3",
}
# ---- c2_li
D = " — "
LIM = [("7Li", "Li"), ("9Be", "Be"), ("45Sc", "Sc"), ("52Cr", "Cr"), ("59Co", "Co"), ("60Ni", "Ni"), ("63Cu", "Cu"), ("66Zn", "Zn"),
       ("72Ge", "Ge"), ("85Rb", "Rb"), ("88Sr", "Sr"), ("89Y", "Y"), ("133Cs", "Cs"), ("138Ba", "Ba"), ("139La", "La"), ("140Ce", "Ce"),
       ("141Pr", "Pr"), ("143Nd", "Nd"), ("147Sm", "Sm"), ("153Eu", "Eu"), ("157Gd", "Gd"), ("159Tb", "Tb"), ("163Dy", "Dy"),
       ("165Ho", "Ho"), ("166Er", "Er"), ("169Tm", "Tm"), ("172Yb", "Yb"), ("175Lu", "Lu")]
LI_EL = ", ".join(e for _, e in LIM)
COL2 = {  # Li et al. 2016 (Microchemical Journal 127), Element I, IGGCAS. Read 2026-09-30: §2.1–2.3.2, §3, Tables 1–3, Fig. 7.
 "Target Material": "magnetite; pyrite" + D + "mineral separates from alternating magnetite-rich and pyrite-rich mesobands, Wutai greenstone belt; FER-2 is the reference material",
 "Digestion Step": "HCl-HNO3 attack (1.5 ml 6 M HCl + 0.5 ml 8 M HNO3, 130 °C, 48 h); re-dissolution (evaporated at 130 °C close to dryness, then 1.5 ml 10 M HCl)" + D + "§2.3.1, for magnetite and pyrite; FER-2 took 1 ml 28 M HF + 1 ml 8 M HNO3 at 130 °C for at least 48 h, then 1.5 ml 10 M HCl for 24 h",
 "Digestion Acid(s)": "HCl-HNO3 attack: 6 M HCl + 8 M HNO3; re-dissolution: 10 M HCl" + D + "§2.3.1",
 "Digestion Temperature": "HCl-HNO3 attack: 130 °C; re-dissolution: 130 °C (evaporation)" + D + "§2.3.1",
 "Digestion Duration": "HCl-HNO3 attack: 48 h; re-dissolution: N" + D + "§2.3.1",
 "Final Solution Matrix": "all: 2% HNO3 containing 5 ng/mL Rh" + D + "§2.3.2",
 "Detector Configuration": "Counting" + D + "Table 1 'Detection mode'",
 "Plasma Thermal Mode": "N" + D + "RF power 1300 W (Table 1)",
 "Target Species": LI_EL + D + "the 28 trace elements of Tables 2 and 3",
 "Monitored Masses": "; ".join("%s → %s" % p for p in LIM) + "; 103Rh → none" + D + "Table 2 'Isotope measured'; Table 3 prints 74Ge where Table 2 has 72; ¹⁰³Rh is the internal standard (Table 1)",
 "Reported Variables and Units": LI_EL + " (µg/g)" + D + "Table 3 (FER-2) in µg g⁻¹; the unit of Table 4 (samples) is not stated in its header",
 "Dwell Time per Mass": "all: 100 ms per isotope" + D + "Table 1",
 "Wash Time Between Samples": "60 s" + D + "Table 1; '1 min with 3% v/v HNO3' (§2.1)",
 "Internal Standard Element": "all: Rh (103Rh)" + D + "Table 1",
 "Drift Correction Method": "Rh internal standard" + D + "'In order to correct the instrumental drift, the internal standard concentration of Rh was kept constant at 5 ng mL−1 in the sample, calibration, and blank solutions' (§2.2)",
 "Calibration Strategy per Target Species": "all: external calibration with 103Rh internal standardisation" + D + "multi-element certified solutions (VHG Labs) diluted to 0.1, 1, 5 and 10 ng/mL (§2.2); Table 1 'Calibration: External'",
 "Blank / Background Correction Method": "N" + D + "a blank solution in 2% HNO3 is part of the calibration set (§2.2); the blank correction is not described",
 "Calibration Factor and Determination Method": "N" + D + "external calibration against multi-element solutions at 0.1, 1, 5 and 10 ng/mL with ¹⁰³Rh held at 5 ng/mL (§2.2); no factor is stated",
 "Procedural Blank Level": "Li: 0.026; Be: 0.008; Sc: 0.020; Cr: 0.068; Co: 0.007; Ni: 0.035; Cu: 0.089; Zn: 0.216; Ge: 0.020; Rb: 0.012; Sr: 0.010; Cs: 0.004; Ba: 0.029; other: N" + D + "ng/mL (Table 2); 'the highest blank level in Zn would contribute less than 0.01% of the amount of analyte'",
 "Detection Limit": "Li: 0.024; Be: 0.006; Sc: 0.028; Cr: 0.043; Co: 0.009; Ni: 0.014; Cu: 0.052; Zn: 0.176; Ge: 0.015; Rb: 0.009; Sr: 0.008; Cs: 0.006; Ba: 0.018; other: N" + D + "method detection limits (MDL, 3 s) in ng/g (Table 2); instrumental detection limits are also given, in ng/mL",
 "Detection Limit Method": "all: 3 × SD of six procedural blanks (MDL)" + D + "Table 2 note; the IDL is 3 × SD of six replicate measurements of 2% HNO3",
 "Primary Calibration Standard Name": "all [all: multi-element certified solutions (VHG Labs)]" + D + "diluted to 0.1, 1, 5 and 10 ng/mL (§2.2)",
 "Secondary Reference Materials": "FER-2" + D + "iron-formation reference material (CCRMP), 'used to validate of the proposed method' (§2.2)",
 "Within-Session Analytical Precision and Assessment Method": "FER-2 [all: RSD <5%]" + D + "three analyses, Table 3 (§3)",
 "Analytical Accuracy and Assessment Method": "FER-2 [all: most ratios to literature values within 0.9–1.1]" + D + "Fig. 7 (§3)",
 "Goodness-of-Fit or Dispersion Statistic": "all: s, one standard deviation, and RSD" + D + "'Mean ± 1 s (n = 3)'; 'RSD = standard deviation/mean × 100%'",
}
# ---- c3_lu
D = " — "
S2 = "§2.1.2"
RMS_LU = "JB-1, JB-2, JB-3, JA-1, JA-2, JA-3, JP-1, BHVO-1, AGV-1, PCC-1, DTS-1"
COL3 = {  # Lu et al. 2007 (Chemical Geology 236), ELEMENT at PML. Read 2026-09-30: abstract, §2.1.2, Tables 1b and 2b, §2.5, §2.7 (Ti calculation).
 "Target Material": "basalt; andesite; peridotite; carbonaceous chondrite" + D + "GSJ and USGS silicate reference materials, and four carbonaceous chondrites (Ivuna, Orgueil, Cold Bokkeveld, Allende)",
 "Coupling Description": "The SF-ICP-MS measures Ti as the (47Ti + 49Ti)/93Nb ratio; the Q-ICP-MS measures B, Zr, Nb, Mo, Sn, Sb, Hf and Ta on the same solutions and gives the Nb concentration used for Ti" + D + "abstract; §2.7",
 "Digestion Step": ("ultrasonic HF decomposition (basalts and andesites, <70 °C); bomb HF decomposition (peridotites and meteorites, 30 mol/l HF, 245 °C, mannitol added); "
                    "re-dissolution (dried, then 5 ml 0.5 mol/l HF in an ultrasonic bath, fluorides removed by centrifuging)" + D + "abstract; §2.5"),
 "Digestion Acid(s)": "ultrasonic HF decomposition: HF; bomb HF decomposition: 30 mol/l HF; re-dissolution: 0.5 mol/l HF" + D + "§2.5",
 "Digestion Temperature": "ultrasonic HF decomposition: <70 °C; bomb HF decomposition: 245 °C; re-dissolution: N" + D + "abstract",
 "Digestion Duration": "N",
 "Final Solution Matrix": "all: 0.5 mol/l HF with mannitol, diluted" + D + "'The mannitol and HF concentrations in all samples and standard solutions were diluted to be similar to each other' (§2.5)",
 "Isotope Dilution Spike": "N" + D + "Ti is not spiked; the Zr–Hf and Mo–Sn–Sb spikes serve the ICP-QMS elements",
 "Detector Configuration": "Pulse counting mode" + D + S2,
 "Desolvation System": "N",
 "Plasma Thermal Mode": "N" + D + "plasma power 1.1 kW (Table 1b)",
 "Target Species": "Ti" + D + "'the analysis of Ti by middle resolution' (" + S2 + "); ⁹³Nb is measured as the internal standard",
 "Monitored Masses": "47Ti, 49Ti → Ti; 93Nb → none" + D + "'In one scan, 47Ti and 49Ti together with 93Nb were measured. Signals of 47Ti and 49Ti were summed up to determine a total Ti signal' (" + S2 + ")",
 "Reported Variables and Units": "Ti (µg/g); TiO2" + D + "Ti by ICP-SFMS; Nb is from the ICP-QMS. Detection limits in solution (ng/g) and in rock (µg/g) in Table 2b",
 "Mass Resolution Assignment": "all: middle resolution (M/ΔM = 3000)" + D + "'At this resolution, major interferences on Ti such as 15N16O2+ or 31P16O+ can be separated' (" + S2 + ")",
 "Dwell Time per Mass": "47Ti: 0.18 s; 49Ti: 0.18 s; 93Nb: 0.18 s" + D + "integration time per 1 s (Table 2b)",
 "Number of Scans per Replicate": "all: 30 scans in 50 s" + D + "Table 1b 'Middle resolution 50 s with 30 scans (continuous nebulization)'",
 "Analysis Sequence": "Standard solution every two samples; each sample measurement ~6 min, including ~3 min washing" + D + S2,
 "Wash Time Between Samples": "~3 min with 0.5 mol/l HF" + D + S2 + "; Table 1b: background measured before each sample 'after 200 s wash'",
 "Internal Standard Element": "all: Nb (93Nb)" + D + S2,
 "Drift Correction Method": "Standard solution every two samples" + D + "'No time drift of fTi was observed during measurements over 2 h, thus all fTi were averaged and used' (§2.7)",
 "Calibration Strategy per Target Species": "Ti: two-stage internal standardisation against Nb, X_Ti = X_Nb × f_Ti × S_Ti" + D + "S_Ti is the (47Ti + 49Ti)/93Nb intensity ratio and f_Ti the relative concentration factor from the standard solution; X_Nb from the ICP-QMS Nb/Mo and Nb/Zr ratios (§2.7)",
 "Blank / Background Correction Method": "Background measured before each sample after a 200 s wash" + D + "Table 1b",
 "Isotope Dilution Data Reduction Method": "N" + D + "Ti is determined by internal standardisation, not isotope dilution",
 "Memory Effect Mitigation": "0.5 mol/l HF carrier and wash solution; ~3 min wash per sample" + D + S2,
 "Calibration Factor and Determination Method": "Ti: relative concentration factor f_Ti against Nb, from the standard solution and averaged over the session; other: N" + D + "Eq. 2 (§2.7)",
 "Procedural Blank Level": "N",
 "Constants and Reference Values Used": "N",
 "Primary Calibration Standard Name": "N" + D + "'The standard solution was measured every two samples' (" + S2 + "); its Ti and Nb contents are not stated",
 "Secondary Reference Materials": RMS_LU + D + "GSJ and USGS silicate reference materials (§2.3); the chondrites are samples",
 "Detection Limit": "Ti: 4 µg/g; other: N" + D + "3σ in rock; 21 ng/g in solution (Table 2b)",
 "Detection Limit Method": "all: 3σ" + D + "Table 2b",
 "Within-Session Analytical Precision and Assessment Method": "all [Ti: RSD 3.6% (2.3–5.4%)]" + D + "TTi/93Nb RSD% (Table 2b)",
 "Analytical Accuracy and Assessment Method": RMS_LU + " [all: consistent with previous studies]" + D + "abstract; Tables 5 and 6",
 "Additional Notes": "Continuous sample introduction with an uptake time of 60 s (0.04 ml per measurement); quartz glass torch with sapphire injector (Table 1b)",
}
# ---- c4_milne
D = " — "
S4 = "§2.4"
EL8 = "Mn, Fe, Co, Ni, Cu, Zn, Cd, Pb"
COL4 = {  # Milne et al. 2010 (Analytica Chimica Acta 665), Element 1 at FSU NHMFL. Read 2026-09-30: §2.1–2.6, Tables 1, 2, 4 and 6.
 "Detector Configuration": "N",
 "Desolvation System": "N",
 "Plasma Thermal Mode": "N" + D + "incident RF power 1300 W (Table 2)",
 "Target Species": EL8 + D + "abstract; Table 1",
 "Monitored Masses": ("56Fe, 57Fe → Fe; 60Ni, 62Ni → Ni; 63Cu, 65Cu → Cu; 66Zn, 68Zn → Zn; 110Cd, 111Cd → Cd; 207Pb, 208Pb → Pb; 55Mn → Mn; 59Co → Co; 95Mo → none" + D +
                      "the spike and reference isotopes of Table 1, ⁵⁵Mn and ⁵⁶Fe named in " + S4 + ", and ⁹⁵Mo counted for the MoO⁺ correction; Co is monoisotopic"),
 "Reported Variables and Units": EL8 + " (nM, dissolved)" + D + "dissolved concentrations in seawater",
 "Mass Resolution Assignment": "all: medium resolution (R = 4000) for Mn, Fe, Co, Ni, Cu and Zn, low resolution (R = 300) for Cd and Pb" + D + S4,
 "Internal Standard Element": "all: none" + D + "isotope dilution for Fe, Ni, Cu, Zn, Cd and Pb, standard additions for Co and Mn (§2.5)",
 "Drift Correction Method": "Elution acid, an enriched-isotope standard and a natural-abundance commercial standard measured every 10–12 samples" + D + "'to assess instrument drift and mass bias' (" + S4 + ")",
 "Calibration Strategy per Target Species": "Fe, Ni, Cu, Zn, Cd, Pb: isotope dilution; Mn, Co: standard addition" + D + "standard additions of 50, 100 and 150 µL of the mixed Co and Mn solution to 12 mL sub-samples (§2.3, §2.5)",
 "Blank / Background Correction Method": "All sample concentrations corrected for the ammonium acetate buffer and the extraction procedure (flow manifold, chelating resin, elution acid), which includes the ICP-MS background" + D + "§2.5",
 "Spectral Interference Corrections Applied": "Y" + D + "MoO⁺ on ¹¹⁰Cd and ¹¹¹Cd corrected by counting ⁹⁵Mo (" + S4 + "); Fe and Mn interferences resolved in medium resolution",
 "Interfering Species": "110Cd, 111Cd: MoO+; 56Fe: 40Ar16O and 40Ca16O; 55Mn: 40Ar15N; other: N" + D + S4,
 "Interference Correction Method": ("110Cd, 111Cd: 95Mo counted in all analyses, with slopes from linear regressions of 95Mo/110Cd and 95Mo/111Cd on Cd-free Mo standards (1–100 nM) run at the start and end of each session; "
                                    "56Fe, 55Mn: resolved in medium resolution; other: N" + D + S4),
 "Isotope Dilution Data Reduction Method": "Standard isotope dilution equation (de Jong et al.), with a per-element mass-bias factor applied to the sample isotope ratios" + D + "§2.5",
 "Calibration Factor and Determination Method": ("Fe, Ni, Cu, Zn, Cd, Pb: mass-bias correction factor, measured over true natural isotopic ratio, from replicate analyses of a commercial ICP standard (High Purity Standards); "
                                                 "Mn, Co: slopes of the standard-addition curves; other: N" + D + "§2.5"),
 "Primary Calibration Standard Name": ("all [Fe, Ni, Cu, Zn, Cd, Pb: enriched isotope spike (57Fe, 62Ni, 65Cu, 68Zn, 111Cd, 207Pb) calibrated against ICP High Purity Standards; "
                                       "Mn, Co: mixed Co and Mn standard-addition solution from Spectrosol AA standards]" + D + "§2.1"),
 "Secondary Reference Materials": "NASS-5; SAFe S1; SAFe D2" + D + "NASS-5 (NRCC certified open-ocean seawater) and the SAFe inter-comparison samples (§2.6)",
 "Detection Limit": "Mn: 0.007; Fe: 0.021; Co: 0.002; Ni: 0.026; Cu: 0.007; Zn: 0.005; Cd: 0.0006; Pb: 0.0002" + D + "nM, 3 SD, for the extraction of a 12 mL sample (Table 5)",
 "Detection Limit Method": "all: 3 SD of the reagent blank" + D + "Table 5, for a 12 mL sample",
 "Final Solution Matrix": "all: 1.0 M HNO3" + D + "'extracted trace elements were eluted with 1 mL of 1.0 M Q-HNO3' (§2.2)",
 "Instrument Sensitivity": "59Co: ~5000 cps/nM; 55Mn: ~3100 cps/nM; other: N" + D + "slopes of the standard additions (Fig. 2, Table 4); the highest Mn sensitivity, 3560 cps/nM, at pH 8.1; the 5 ppb In tuning solution gave ~1,000,000 cps",
 "Procedural Blank Level": "Mn: 0.433 ± 0.026; Fe: 2.791 ± 0.083; Co: 0.078 ± 0.006; Ni: 0.457 ± 0.104; Cu: 0.184 ± 0.027; Zn: 3.044 ± 0.018; Cd: 0.045 ± 0.003; Pb: 0.017 ± 0.001" + D + "pmol, mean reagent blank ± 1 SD from one day's analysis, elution acid plus ammonium acetate buffer (Table 5)",
 "Within-Session Analytical Precision and Assessment Method": "NASS-5, SAFe S1, SAFe D2 [all: 95% confidence limit, n = 3]" + D + "Table 6",
 "Analytical Accuracy and Assessment Method": "NASS-5, SAFe S1, SAFe D2 [all: agreement with the NASS-5 certified and SAFe consensus values]" + D + "Table 6",
 "Goodness-of-Fit or Dispersion Statistic": "all: %RSD, with 1 S.D. for blanks" + D + "'The precision is calculated as the percent relative standard deviation (% RSD)'; 'Mean blank ± 1S.D.'",
 "Combination Method": "all: mean of replicate analyses, and average slope of the standard additions" + D + "'Mean blank ± 1S.D.'; 'Average slopes resulting from the regression analysis of Co and Mn standard additions'",
 "Additional Notes": "Off-line pre-concentration on Toyopearl AF-Chelate-650M resin; enriched isotope spikes added before extraction; standard additions for Mn and Co (§2.2–2.3)",
}
# ---- c5_misra
D = " — "
S31 = "§2.3.1"
CS = "CAM-wuellerstorfi, CAM-Uvig-1, CAM-Uvig-2, CAM-Mix"
LR = ["7Li", "11B", "25Mg", "27Al", "43Ca", "87Sr", "111Cd", "137Ba", "238U"]
MR = ["23Na", "55Mn", "56Fe", "66Zn"]
EL = {"7Li": "Li", "11B": "B", "25Mg": "Mg", "27Al": "Al", "43Ca": "none", "87Sr": "Sr", "111Cd": "Cd", "137Ba": "Ba", "238U": "U",
      "23Na": "Na", "55Mn": "Mn", "56Fe": "Fe", "66Zn": "Zn"}
COL5 = {  # Misra et al. 2014 (G-cubed), Element XR, Cambridge. Read 2026-09-30: abstract, §2.1–2.4, Tables 1–4, Figs 1–2.
 "Acquisition Pass": "LR; MR" + D + "low resolution (Δm/m = 300) and medium resolution (Δm/m = 4000) methods, 'Calcium was measured in both low and medium resolution to maintain accuracy of Me/Ca ratios obtained from the two mass resolution modes' (Table 3)",
 "Number of Acquisition Passes": "2" + D + "low and medium resolution (Tables 1 and 3)",
 "Sample Preparation Method": "Handpicked 1–2 mg of species- and size-specific shells, cracked, clay removed (MQ water, methanol), reductively and/or oxidatively cleaned, leached in 0.001 M HNO3, dissolved in 1 M HNO3 and centrifuged; 5 µL of supernatant diluted with 200 µL 0.1 M HNO3 as the Me/Ca stock, Ca measured by ICP-AES, then diluted to [Ca] 10 ppm with 0.1 M HNO3 + 0.3 M HF" + D + "§2.4; the HF-bearing matrix 'was used only in the final dilution step'",
 "Digestion Step": "dissolution (minimum volume of 1 M HNO3, 40–60 µL, then centrifuged 2 min at 10,000 rpm)" + D + "§2.4",
 "Digestion Acid(s)": "dissolution: 1 M HNO3" + D + "§2.4",
 "Digestion Temperature": "N",
 "Final Solution Matrix": "all: 0.1 M HNO3 + 0.3 M HF" + D + "'The acid matrix containing HF was used only in the final dilution step'",
 "Detector Configuration": "Dual mode, fixed for each isotope: counting for 7Li, 11B, 111Cd, 137Ba, 238U, 55Mn, 56Fe, 66Zn and analog for 25Mg, 27Al, 43Ca, 87Sr, 23Na" + D + "Tables 1 and 3; " + "'measured at a fixed detection mode to avoid detection mode switch (pulse to analog) during analysis' (" + S31 + ")",
 "Plasma Thermal Mode": "N" + D + "RF power 1250 W (Table 1)",
 "Target Species": "Li, B, Na, Mg, Al, Mn, Fe, Zn, Sr, Cd, Ba, U" + D + "'The concentrations of foraminiferal trace elements of interest (Li, B, Na, Mg, Al, Mn, Fe, Zn, Sr, Cd, Ba, and U)' (" + S31 + "); Ca is the ratio denominator",
 "Monitored Masses": "; ".join("%s → %s" % (m, EL[m]) for m in LR + MR) + D + "Table 3; ⁴³Ca is measured in both resolutions",
 "Reported Variables and Units": "B/Ca (µmol/mol); Li/Ca, Mg/Ca, Al/Ca, Sr/Ca, Cd/Ca, Ba/Ca, U/Ca, Na/Ca, Mn/Ca, Fe/Ca, Zn/Ca (µmol/mol or mmol/mol)" + D + "Me/Ca ratios; Li, Mg, Al, Sr, Cd, Ba and U in low resolution, Na, Mn, Fe and Zn in medium (Table 3)",
 "Mass Resolution Assignment": "LR: low resolution (Δm/m = 300), for 7Li, 11B, 25Mg, 27Al, 43Ca, 87Sr, 111Cd, 137Ba, 238U; MR: medium resolution (Δm/m = 4000), for 23Na, 43Ca, 55Mn, 56Fe, 66Zn" + D + "Table 3",
 "Dwell Time per Mass": "7Li: 0.005 s; 11B: 0.005 s; 25Mg: 0.01 s; 27Al: 0.01 s; 43Ca: 0.02 s (LR), 0.01 s (MR); 87Sr: 0.04 s; 111Cd: 0.02 s; 137Ba: 0.02 s; 238U: 0.05 s; 23Na: 0.02 s; 55Mn: 0.01 s; 56Fe: 0.05 s; 66Zn: 0.01 s" + D + "'Sample Time' (Table 3); samples per peak 50 or 100 in LR, 25 in MR",
 "Number of Scans per Replicate": "LR: 15 passes × 3 runs; MR: 5 passes × 3 runs" + D + "Table 3; Table 1 prints 3 passes for MR",
 "Analysis Sequence": "Blocks of seven samples, each bracketed by a pair of acid blanks and internal consistency standards (Standard 3 of the calibration)" + D + S31,
 "Internal Standard Element": "all: none" + D + "Me/Ca ratios, with Ca measured in both resolutions",
 "Drift Correction Method": "N" + D + "the blocks of seven are bracketed by acid blanks and a consistency standard; at low calcium concentrations there was 'minimal instrumental sensitivity drift' (" + S31 + ")",
 "Calibration Strategy per Target Species": "all: external calibration with matrix-matched standards, samples and standards concentration-matched within ±5%" + D + "±1% in the Fig. 2 dilution series; at [Ca] of 10 ppm with normal cones, 5 ppm with the Jet and X cones; samples first measured for Ca by ICP-AES (" + S31 + ")",
 "Pulse/Analog Detector Nonlinearity Correction": "all: detector cross-calibration between pulse and analog modes performed daily" + D + S31,
 "Spectral Interference Corrections Applied": "N" + D + "Na, Mn, Fe and Zn are measured in medium resolution (Table 3); no correction is described",
 "Calibration Factor and Determination Method": "N" + D + "'Before sample analysis, mass bias determination was carried out using a foraminiferal matrix matched solution' (" + S31 + "); no factor is stated",
 "Procedural Blank Level": "B: 2.0 ± 1.0 µmol/mol (as B/Ca); other: N" + D + "abstract",
 "Primary Calibration Standard Name": "all [all: matrix-matched Me/Ca calibration standards (Standards 0–8)]" + D + "§2.2, " + S31,
 "Calibration Standard Measurement Frequency": "Standard 3 brackets each block of seven samples" + D + S31,
 "Secondary Reference Materials": "CAM-wuellerstorfi; CAM-Uvig-1; CAM-Uvig-2; CAM-Mix" + D + "the four Cambridge consistency standards (§2.2)",
 "Detection Limit": "B/Ca: 2 µmol/mol; other: N" + D + "'We report a B/Ca detection limit of 2 µmol/mol' (abstract)",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "B/Ca: 1.0%; other: N" + D + "abstract",
 "Desolvation System": "N",
 "Instrument Sensitivity": "N" + D + "'a typical sensitivity of 2.5 × 10^6 cps/ppb on 115In' (§3.1), the tuning isotope; 1 ppb 11B and 115In sensitivities by spray chamber, injector and acid matrix in Table 2",
 "Within-Session Analytical Precision and Assessment Method": "all [B/Ca: 4.0% (2σ), average within-run external precision]" + D + "abstract",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": CS + " [all: ±2σ of repeat analyses over 8 months]" + D + "Table 4; n = 180, 130, 100 and 150",
 "Analytical Accuracy and Assessment Method": CS + " [B/Ca: across degrees of sample dilution]" + D + "Fig. 2",
 "Combination Method": "all: average of 10 measurements within a session, and average of the session averages" + D + "'Open symbols represent an average of 10 measurements acquired during a single instrument session. The solid symbols represent the average of the open symbols'",
 "Additional Notes": "Teflon Scott-type single-pass spray chamber and platinum injector (1.8 mm I.D.) to reduce instrumental boron blanks; HF in the final matrix for rapid boron washout (§2.3)",
}
# ---- c6_willbold
D = " — "
ID_EL = "Sr, Zr, Ba, Nd, Sm, Gd, Dy, Er, Yb, Hf, Pb, U"
RSF_EL = "Rb, Y, Nb, Cs, La, Ce, Pr, Eu, Tb, Ho, Tm, Lu, Ta, Th"
EL26 = "Rb, Sr, Y, Zr, Nb, Cs, Ba, La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, Pb, Th, U"
WM = [("85Rb", "Rb"), ("86Sr, 88Sr", "Sr"), ("89Y", "Y"), ("90Zr, 91Zr", "Zr"), ("93Nb", "Nb"), ("133Cs", "Cs"), ("135Ba, 137Ba", "Ba"),
      ("139La", "La"), ("140Ce", "Ce"), ("141Pr", "Pr"), ("143Nd, 145Nd", "Nd"), ("147Sm, 149Sm", "Sm"), ("151Eu, 153Eu", "Eu"),
      ("155Gd, 158Gd", "Gd"), ("159Tb", "Tb"), ("161Dy, 163Dy", "Dy"), ("165Ho", "Ho"), ("166Er, 167Er", "Er"), ("169Tm", "Tm"),
      ("171Yb, 172Yb", "Yb"), ("175Lu", "Lu"), ("178Hf, 179Hf", "Hf"), ("181Ta", "Ta"), ("207Pb, 208Pb", "Pb"), ("232Th", "Th"),
      ("235U, 238U", "U"), ("47Ti, 49Ti, 99Ru, 101Ru, 185Re, 187Re", "none")]
HR_ISO = "153Eu, 155Gd, 158Gd, 159Tb, 161Dy, 163Dy, 165Ho, 166Er, 167Er, 169Tm, 171Yb, 172Yb, 175Lu"
RMS = "AGV-1, AGV-2, BCR-1, BCR-2, BCR-2G, BIR-1, BIR-1G, BHVO-2, BHVO-2G, G-2, JR-1, KL2-G, ML3B-G, NIST SRM 612, OU-6, PCC-1"
STEPS = ("hotplate HF-HNO3 (non-refractory samples of basaltic composition, 12 h at 130 °C in closed 15 ml Savillex PFA vials); "
         "bomb HF-HNO3 (samples with refractory minerals such as granites, stirred 7 days at 180 °C in Parr bombs, reopened after 3 days and refilled with 0.5 ml HF); "
         "fluoride removal (re-dissolved in a few drops of 14 mol/l HNO3 and evaporated to incipient dryness, repeated twice); "
         "chloride conversion (2 ml 6 mol/l HCl heated at 80 °C, then evaporated at 50 °C); "
         "final uptake (5 ml 7 mol/l HNO3)")
COL6 = {  # Willbold & Jochum 2005 (Geostandards and Geoanalytical Research 29), ELEMENT2 at MPI Mainz. Read 2026-09-30: Experimental, Tables 1–3, Figs 1–2, LOD, combined uncertainty, Results.
 "Target Material": "basalt; andesite; granite; rhyolite; shale; peridotite; synthetic glass" + D + "the rock types of the 17 reference materials of Table 2, including the USGS and MPI-DING glasses",
 "Sample Preparation Method": "About 100 mg whole-rock powder spiked with the three multi-element spikes (MES 1–3), digested in HF-HNO3, converted to chlorides, taken up in 7 mol/l HNO3 and diluted for LR and HR, with a Ru-Re solution added to each dilution" + D + "cleanroom, twice sub-boiled acids (Samples and sample preparation)",
 "Digestion Vessel Type": "Closed 15 ml Savillex PFA vials, placed in Parr bombs for samples with refractory minerals",
 "Digestion Step": STEPS + D + "Samples and sample preparation",
 "Digestion Acid(s)": "hotplate HF-HNO3: 1–2 ml HF (24 mol/l) + 0.2 ml HNO3 (14 mol/l); bomb HF-HNO3: 1–2 ml HF (24 mol/l) + 0.2 ml HNO3 (14 mol/l), and 0.5 ml HF after 3 days; fluoride removal: 14 mol/l HNO3; chloride conversion: 6 mol/l HCl; final uptake: 7 mol/l HNO3",
 "Digestion Temperature": "hotplate HF-HNO3: 130 °C; bomb HF-HNO3: 180 °C; fluoride removal: ca. 80 °C (evaporation); chloride conversion: 80 °C, then 50 °C (evaporation); final uptake: N",
 "Digestion Duration": "hotplate HF-HNO3: 12 h; bomb HF-HNO3: 7 days; other: N",
 "Final Solution Matrix": "LR: 0.4 mol/l HNO3, about 120 µl of the uptake solution diluted to 50 ml (dilution factor ~21000); HR: 0.4 mol/l HNO3, 2.5 ml of the uptake solution diluted with H2O to 50 ml (dilution factor ~1000)" + D + "ca. 6 µl of a Ru-Re solution (60 µg/g Ru, 20 µg/g Re) added to each dilution",
 "Sample Aliquot Mass or Volume": "About 100 mg of whole-rock powder",
 "Chromatographic Separation Applied": "None" + D + "'dissolved rock samples are analysed directly by ID without previous separation'",
 "Isotope Dilution Spike": "Three multi-element spikes: MES 1 (86Sr, 135Ba, 145Nd, 149Sm, 235U), MES 2 (155Gd, 161Dy, 167Er, 171Yb, 207Pb), MES 3 (91Zr, 179Hf)" + D + "Table 1; calibrated by reverse ID against Alfa Aesar specpure solutions, spike-concentration uncertainty 0.5–1% RSD",
 "Detector Configuration": "N",
 "Desolvation System": "N",
 "Plasma Thermal Mode": "N" + D + "RF power 1235 W (Table 3)",
 "Acquisition Pass": "LR; HR" + D + "two solutions of different dilution: dilution factor ~21000 for LR and ~1000 for HR; 'the transmission decreases by a factor of about 100 from the LR to the HR mode'",
 "Number of Acquisition Passes": "2" + D + "the LR and HR solutions",
 "Target Species": EL26 + D + "twelve by isotope dilution and fourteen by relative sensitivity factors (Table 1)",
 "Monitored Masses": "; ".join("%s → %s" % p for p in WM) + D + "the determined ratios of Table 1; Ti, Ru, Eu and Re ratios measured for the in-run mass-fractionation correction",
 "Reported Variables and Units": EL26 + " (µg/g)" + D + "Equations 1 and 2",
 "Mass Resolution Assignment": "LR: M/ΔM = 300, for Rb to Sm and Hf to U; HR: M/ΔM = 11000, for Eu to Lu" + D + "Table 1; HR resolves light REE oxides on the heavy REE",
 "Dwell Time per Mass": "all: 0.1 s, 15 samples per peak" + D + "'Peaks were monitored in electrical scanning mode for 0.1 s' and Table 3",
 "Number of Scans per Replicate": "all: 70 to 120 scans of the whole mass spectrum" + D + "for one analysis, a total acquisition time of 10 minutes per sample",
 "Number of Replicates": "3" + D + "'Triplicate determinations were performed for each digestion'",
 "Analysis Sequence": "N" + D + "a total of ca. 20 minutes per sample 'including the measurement of blank, standard solution, washout'; the order is not stated",
 "Internal Standard Element": "all: the ID-determined elements, for the RSF elements (Table 1 ratios, e.g. 93Nb/90Zr, 175Lu/172Yb)" + D + "Ru and Re are added for the mass-fractionation correction, not as internal standards",
 "Drift Correction Method": "N" + D + "'Instrumental drift of SF-ICP-MS has only a negligible effect on the reproducibility of ID determined concentrations since isotope ratios are used'",
 "Calibration Strategy per Target Species": ID_EL + ": isotope dilution (Eq. 1); " + RSF_EL + ": relative sensitivity factor against an ID-determined element measured in the same resolution and run (Eq. 2)" + D + "Table 1",
 "Blank / Background Correction Method": "N" + D + "'After correction for background and mass fractionation'; the method is not described",
 "Spike / Outlier Filtering Approach": "Dixon outlier test on each block of ten ratios" + D + "'Generally, less than one ratio had to be excluded from the whole data set'",
 "Spectral Interference Corrections Applied": "Y" + D + "the heavy REE are measured in HR to resolve light REE oxides; NIST SRM 612 data for Rb, Zr, Nb, Hf, Ta, Pb and U omitted because of oxide interferences and spiking",
 "Interfering Species": HR_ISO + ": light REE oxides; other: N" + D + "in NIST SRM 612 also 69Ga16O on 85Rb, 74Ge16O on 90Zr, 162Dy16O on 178Hf and 165Ho16O on 181Ta",
 "Interference Correction Method": HR_ISO + ": resolved in HR (M/ΔM = 11000); other: N",
 "Isotope Dilution Data Reduction Method": "Eq. 1 for the ID elements and Eq. 2 for the RSF elements, from mass-fractionation- and background-corrected mean ratios, with R_ik in Eq. 2 corrected for the spike contribution to isotope k",
 "Calibration Factor and Determination Method": ("all: in-run mass-fractionation factors from a power law MF = a × b^(m−c) + d fitted to 47Ti/49Ti, 99Ru/101Ru (LR), 151Eu/153Eu (HR) and 185Re/187Re, "
                                                 "and RSF calibrated once per analytical run on a multi-element standard solution" + D + "'Typical values are a: 0.08 to 0.23, b: 0.96 to 0.98, c: -10 to 10 and d: -0.005 to 0.005'"),
 "Uncertainty Propagation Method": "all: combined standard uncertainty (Eurachem/CITAC 2000), 1–2% for ID and 2–3% for RSF" + D + "components: instrumental drift, matrix effects, ratio measurement, spectroscopic interferences, spike calibration, RSF calibration, mass fractionation and constants (Willbold et al. 2003)",
 "Procedural Blank Level": "N" + D + "the total procedural blanks enter only through the LOD",
 "Primary Calibration Standard Name": ("all [" + ID_EL + ": multi-element spike solutions MES 1–3 calibrated by reverse ID against Alfa Aesar specpure solutions; "
                                       + RSF_EL + ": multi-element standard solution (16–17 µg/g stock from Alfa Aesar specpure solutions, diluted to 1–5 ng/g)]" + D + "Table 1"),
 "Calibration Standard Measurement Frequency": "Standard solution once per analytical run (e.g. once per day)" + D + "RSF values constant within 1s over at least ten hours",
 "Detection Limit": "all: about 0.1 to 10 ng/g sample equivalent for most elements" + D + "Figure 2",
 "Detection Limit Method": "all: 3 s of total procedural blanks including spiking, 50 measurements in LR and 20 in HR" + D + "Limits of detection",
 "Limit of Quantification (LOQ) Method": "all: RSD better than 10% on the low-concentration RM PCC-1, ca. 10 to 900 ng/g" + D + "'about 10 to 20 times the LOD for most elements'",
 "Within-Session Analytical Precision and Assessment Method": "BHVO-1 [all: RSD of triplicate determinations on one digestion, generally better than 1%]" + D + "Table 4",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "BHVO-1 [all: RSD of five independent digestions over 4 months, 1–3%]" + D + "abstract and Table 4; the sixteen other RMs by RSD of three to four independent analyses (Table 5)",
 "Analytical Accuracy and Assessment Method": ("BHVO-1 [all: within 1–2% of published ID data and 2–3% of all published data]; " + RMS +
                                               " [all: most within 3–4% of published data]" + D + "abstract; Table 5"),
 "Combination Method": "all: mean of triplicate determinations per digestion, and mean over the independent analyses of each reference material" + D + "'the mean values of the triplicate determinations and their RSDs' (Table 4); within an analysis, ratios are the mean of all scans (n = 70–120)",
 "Additional Notes": "Magnetic jump followed by electric scan (Table 3); acquisition 10 min per sample; ca. 20 min per sample in all, a mass spectrometer efficiency of almost 90%",
}
# ---- engine
COLS = [  # column number -> label substring
 (1, "Desem+etal2022", COL1), (2, "Li+etal2016", COL2), (3, "Lu+etal2007", COL3),
 (4, "Milne+etal2010", COL4), (5, "Misra+etal2014", COL5), (6, "Willbold2005", COL6),
]
UPB_ONLY = []  # no U-Pb twin
NODATE = "N — the procedure reports no date"
TAPPS = ["Solution_SF-ICP-MS_TAPP_v"]


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
