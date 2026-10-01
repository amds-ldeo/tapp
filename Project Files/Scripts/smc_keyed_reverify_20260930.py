#!/usr/bin/env python3
"""Solution MC-ICP-MS: keyed notation, with every procedure-level cell re-read (2026-09-30).

    python3 "Project Files/Scripts/smc_keyed_reverify_20260930.py" [--apply] [--out-sim DIR]

The last TAPP of the keyed-notation backlog, done as the Solution Q and SF passes were: every procedure-level
cell of Solution MC's fourteen columns (twelve papers) re-read against its paper, and the edit scored by
`Project Files/Reports/SMC_Cells_RoundTrip_2026-09-30/roundtrip.py` before it was applied.

What the re-read found, beyond format (per column in the dicts below):
  * wrong values: Ibañez-Mejia & Tissot's Zr-only crystals were dissolved for 60 h at 215 °C (48 h is the
    dated crystals'); Nowell's Nu Plasma nebuliser is a GE Micromist (not the Neptune's PFA-50) at ~400
    µl/min; Nowell's Neptune W/Re monitors are ¹⁸²W and ¹⁸⁵Re, not "¹⁸²W/¹⁸⁴W/¹⁸⁶W"; van Kooten's digestion
    acids were the column reagents, not the Parr-bomb HNO3:HF;
  * stated facts recorded as unstated: Nie & Dauphas's digestion steps (ii) and (iii), and its Parr-bomb
    fallback; Nowell's Nu Plasma two-sequence cup table (Table 2b) recorded as "no mass list"; the
    Schönbächler session precision of NIST SRM 3169; Barnes's ETH digestion ("see the WUSTL column");
  * missing structure: configurations measured separately — Hopp's wet-MR and dry-HR set-ups, Hu's main and
    sub-configuration, Nowell's two Nu Plasma sequences, Pringle's spray chamber and APEX, van Kooten's
    Fe, Cr and Mg runs, Barnes's K, Cu and Zn runs and two Ti configurations — are now Acquisition Pass
    members, so introduction, plasma, resolution, cycles and matrix cells say which set-up they describe;
  * isotopes, interference monitors and isotope ratios recorded without bindings or members in all fourteen
    columns, and reported δ/ε/μ quantities that were not definer members.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
# ---- c01_budde
D = " — "
EMO = "ε92Mo, ε94Mo, ε95Mo, ε97Mo, ε100Mo"
COL1 = {  # Budde et al. 2016 (EPSL 454), Neptune Plus at Münster. Read 2026-09-30: §2 (samples and analytical methods), Table 1 and notes.
 "Target Material": "chondrule; matrix; bulk chondrite" + D + "separates and bulk rock of the Allende CV3 chondrite",
 "Digestion Step": "HF–HNO3(–HClO4) attack (closed Savillex beakers on a hotplate); inverse aqua regia" + D + "§2",
 "Digestion Acid(s)": "HF–HNO3(–HClO4) attack: HF + HNO3 (+ HClO4); inverse aqua regia: HNO3 + HCl" + D + "§2",
 "Desolvation System": "all: Cetac Aridus II" + D + "with a Savillex C-Flow PFA nebulizer",
 "Instrument Sensitivity": "N" + D + "total ion beam ~1.3 × 10⁻¹⁰ A for a ~100 ppb Mo solution at ~50 µl/min",
 "Target Species": "Mo" + D + "Ba by TIMS (Triton Plus) on the same digestions",
 "Monitored Masses": "92Mo, 94Mo, 95Mo, 96Mo, 97Mo, 98Mo, 100Mo → Mo; 91Zr, 99Ru → none" + D + "the εⁱMo ratios to ⁹⁶Mo with ⁹⁸Mo/⁹⁶Mo normalisation; ⁹¹Zr and ⁹⁹Ru monitor the isobars",
 "Reported Variables and Units": EMO + D + "εⁱMo = [(ⁱMo/⁹⁶Mo)sample/(ⁱMo/⁹⁶Mo)standard − 1] × 10⁴, relative to the Alfa Aesar standard",
 "Number of Cycles per Block": "all: 100 isotope ratio measurements, preceded by 40 baseline integrations" + D + "§2",
 "Integration Time per Cycle": "all: 8.4 s" + D + "§2",
 "Isotope Ratio Reported": "ε92Mo: 92Mo/96Mo; ε94Mo: 94Mo/96Mo; ε95Mo: 95Mo/96Mo; ε97Mo: 97Mo/96Mo; ε100Mo: 100Mo/96Mo" + D + "normalised to ⁹⁸Mo/⁹⁶Mo = 1.453173",
 "delta or epsilon Value Reference Standard": "Mo: Alfa Aesar Mo solution standard" + D + "mean of bracketing runs",
 "Spectral Interference Corrections Applied": "Y, Zr and Ru on the Mo masses, corrected by monitoring 91Zr and 99Ru" + D + "§2; details in the supplementary material",
 "Interfering Species": "N" + D + "Zr and Ru isobars; the affected masses are listed only in the supplementary material",
 "Interference Correction Method": "N" + D + "corrected by monitoring ⁹¹Zr and ⁹⁹Ru; details in the supplementary material",
 "Procedural Blank Level": "Mo: 0.7–1.2 ng" + D + "'negligible, given that several hundred ng of Mo were analyzed for each sample'",
 "Combination Method": "all: mean of pooled solution replicates per sample, and weighted averages of recombined separates" + D + "§2; Table 1 notes b and c",
 "Primary Calibration Standard Name": "all [Mo: Alfa Aesar Mo solution standard]" + D + "bracketing runs (§2)",
 "Secondary Reference Materials": "BHVO-2" + D + "'several digestions of which were processed through the full analytical protocol and analyzed together with each set of samples'",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "BHVO-2 [all: ±0.14 (ε97Mo) to ±0.39 (ε92Mo), 2 s.d., n = 24]" + D + "external reproducibility (§2, Table S2); Ba by TIMS ±0.13–0.31 (n = 14)",
 "Analytical Accuracy and Assessment Method": "BHVO-2 [all: εⁱMo indistinguishable from the Alfa Aesar standard]" + D + "§2",
}
# ---- c02_craddock
D = " — "
CR_RMS = "IAEA-S-1, IAEA-S-2, IAEA-S-4, NBS-123"
COL2 = {  # Craddock et al. 2008 (Chemical Geology 253), NEPTUNE at WHOI. Read 2026-09-30: §2.1–2.4, §3.1–3.2, Tables 1–3, Figs 1–4. The laser half is the coupled technique.
 "Target Material": "sulfide; sulfate; elemental sulfur; seawater" + D + "Table 3: Ag2S, ZnS, pyrite, pyrrhotite, anhydrite, Fe(III) sulfate, elemental S and modern seawater",
 "Sample Preparation Method": "Less than 50 mg weighed, digested, S purified on AG50-X8 cation exchange and diluted with 2% HNO3 to a 50 ppm S stock; for laser work, a 2 mm thick polished section on a petrographic slide" + D + "§2.1–2.2",
 "Digestion Step": ("HNO3 attack (5 ml 50% HNO3, hot plate below 70 °C, to dryness); HNO3–HCl digestion (3 ml concentrated HNO3 + 2 ml 50% HCl, sealed PTFE vessel, 70 °C, to dryness); "
                    "re-dissolution (4 ml 2% HNO3, AgCl from Ag2S removed by centrifugation)" + D + "§2.2"),
 "Digestion Acid(s)": "HNO3 attack: 50% HNO3; HNO3–HCl digestion: concentrated HNO3 + 50% HCl; re-dissolution: 2% HNO3" + D + "§2.2",
 "Digestion Temperature": "HNO3 attack: below 70 °C; HNO3–HCl digestion: 70 °C; re-dissolution: N" + D + "§2.2",
 "Digestion Duration": "N" + D + "'taken to dryness'",
 "Final Solution Matrix": "all: 2% HNO3" + D + "a 50 ppm S stock (§2.2); standards at 20 ppm S",
 "Chromatographic Separation Applied": "Yes, AG50-X8 (H+) cation exchange, 2.5 ml resin conditioned with 1.4 N HNO3; S and oxyanions pass, matrix retained; yield 98 ± 4% (§2.2)",
 "Desolvation System": "all: none" + D + "'passing solutions through a desolvating nebulizer to obtain dry plasma conditions is not viable for bulk analysis' (§2.3)",
 "Plasma Thermal Mode": "all: wet plasma" + D + "solutions 'introduced as a wet aerosol (in 2% HNO3)' (Fig. 1)",
 "Monitored Masses": "32S, 33S, 34S → S" + D + "§2.4; ³⁶S not reported because of its low abundance and Ar interferences",
 "Reported Variables and Units": "δ34S, δ33S" + D + "‰ on the V-CDT scale (§2.4)",
 "Collector Configuration": "32S: L3; 33S: C; 34S: H3" + D + "Table 1",
 "Number of Cycles per Block": "all: 20 cycles" + D + "Table 1, §2.4",
 "Integration Time per Cycle": "all: 8.5 s" + D + "Table 1, §2.4",
 "Baseline Measurement Approach": "5 s at the beginning of each analysis with the ion beams deflected" + D + "§2.4",
 "Analysis Sequence": "Each sample bracketed by standards analysed immediately before and after, with 2% HNO3 blanks aspirated periodically through the session" + D + "§2.4, §3.2",
 "Wash Time Between Samples": "2 min" + D + "Table 1; 4 min after laser analyses",
 "Mass Bias Correction Strategy": "Standard-sample bracketing with matrix-matched purified S solutions, linear interpolation between the biases of two neighbouring standards, sample and standard matched within ~20% in intensity at ~10 V" + D + "§2.4, §3.1",
 "Isotope Ratio Reported": "δ34S: 34S/32S; δ33S: 33S/32S" + D + "§2.4",
 "delta or epsilon Value Reference Standard": "S: V-CDT, through in-house S_Spex and S_Alfa calibrated against IAEA-S-1 (δ34S = −0.3‰)" + D + "§2.4",
 "Blank / Background Correction Method": "Average on-peak-zero background from periodic 2% HNO3 blanks, measured on the low-mass shoulder, subtracted per isotope off-line" + D + "~30–50 mV on ³²S (§2.4, §3.1)",
 "Spike / Outlier Filtering Approach": "None, no automatic 2σ rejection of outlying cycles" + D + "'Automatic rejection of outlying cycles (2σ outlier criterion) offered within the NEPTUNE software is not performed' (§2.4)",
 "Spectral Interference Corrections Applied": "Y, molecular interferences resolved in high resolution" + D + "³²S¹H on mass 33 unresolved",
 "Interfering Species": "32S: 16O16O, 64Zn2+, 15N16O1H; 33S: 17O16O, 16O16O1H, 32S1H, 66Zn2+; 34S: 18O16O, 17O16O1H, 33S1H, 68Zn2+" + D + "Table 2",
 "Interference Correction Method": ("32S, 34S: resolved in high resolution on the interference-free low-mass shoulder, hydride effects corrected by standard-sample bracketing; "
                                    "33S: as for 32S, but 32S1H (>10% of mass 33) is unresolved" + D + "hydride rate checked per measurement from (³³S + ³²SH)/³²S against ³⁴S/³²S (§3.1)"),
 "Uncertainty Level": "1σ internal precision for individual analyses, 2σ external reproducibility for replicates" + D + "§2.4",
 "Procedural Blank Level": "S: ~0.05% (~0.25 µg per 500 µg S)" + D + "§2.2",
 "Combination Method": "δ34S, δ33S: over the replicate analyses of each standard" + D + "Table 3 '# of replicates', with 2σ external precision",
 "Goodness-of-Fit or Dispersion Statistic": "δ34S, δ33S: two standard deviations of the replicates" + D + "Table 3 note",
 "Primary Calibration Standard Name": "all [S: in-house S_Spex and S_Alfa 20 ppm S solutions, from Spex CertiPrep and Alfa Aesar Specpure stocks]" + D + "§2.1; calibrated against IAEA-S-1",
 "Secondary Reference Materials": CR_RMS + ", Alfa, Sch-M-2, SW-Woods Hole, FeIII-sulfate, GAV-18, Ward's Py, Ward's Po" + D + "Table 3",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "Alfa [δ34S: ±0.21‰, 2σ, 20–30 replicates]; Sch-M-2 [δ34S: ±0.45‰, 2σ, 12 replicates, laser]" + D + "§3.2; S_Spex ±0.18‰; δ³³S an order of magnitude worse",
 "Analytical Accuracy and Assessment Method": CR_RMS + " [δ34S: consistent with published consensus values within uncertainty]" + D + "§2.4, Table 3",
 "Additional Notes": "Laser half: NewWave UP213 (213 nm), He carrier, 60 µm spot, 180 × 80 µm raster, 5 µm/s, 10 Hz, ~9–10 J/cm², ablated aerosol mixed with 2% HNO3 in the spray chamber" + D + "Table 1",
}
# ---- c03_hopp
D = " — "
ARG = "40Ar13C+, 40Ar14N+, 40Ar16O+, 40Ar16O1H+ and 40Ar18O+"
COL3 = {  # Hopp et al. 2021 (EPSL / preprint), Neptune (Plus spec) at Chicago. Read 2026-09-30: §2.1–2.3, Eqs 1–2, Table 1 and notes.
 "Coupled Technique(s)": "N" + D + "the Fe was measured on digestions previously analysed for Pt, Mo, Ni and/or W isotopes (Kruijer et al. 2017 and others)",
 "Target Material": "iron meteorite; basalt" + D + "23 iron meteorites from nine groups; BHVO-2 and BCR-2",
 "Digestion Step": ("iron aqua regia (iron meteorites, ~50 mg pieces, 3:1 HCl–HNO3, hot plate); basalt HF–HNO3 (basalts, 2:1, hot plate); basalt aqua regia (several steps); "
                    "chloride conversion (redissolved in 0.25 ml 10 M HCl)" + D + "§2.1"),
 "Digestion Acid(s)": "iron aqua regia: 3:1 HCl–HNO3; basalt HF–HNO3: 2:1 HF–HNO3; basalt aqua regia: aqua regia; chloride conversion: 10 M HCl" + D + "§2.1",
 "Digestion Temperature": "iron aqua regia: 120 °C; basalt HF–HNO3: 150 °C; other: N" + D + "§2.1",
 "Digestion Duration": "iron aqua regia: 24 h; basalt HF–HNO3: 48 h; other: N" + D + "§2.1",
 "Digestion Vessel Type": "N" + D + "'on a hot plate'",
 "Final Solution Matrix": "all: 10 µg/g Fe in 0.45 M HNO3" + D + "§2.3; 'All sample and standard solutions were prepared with the same 0.3 M HNO3 solution', concentrations matched within ≤2%",
 "Sampler and Skimmer Cone Material": "Pt sampler (wet plasma, MR) or Ni sampler (dry plasma, HR), with H skimmer cones" + D + "§2.3",
 "Faraday Cup Amplifier Resistor Values": "56Fe: 10^10 Ω; 54Fe, 57Fe, 58Fe: 10^11 Ω; 53Cr, 60Ni: 10^12 Ω" + D + "§2.3",
 "Mass Resolution Setting": "MR or HR, on the flat-topped peak shoulder" + D + "§2.3",
 "Acquisition Pass": "MR; HR" + D + "'either a cyclonic glass spray chamber (wet plasma, MR-mode, Pt cones) or an ESI Apex Ω desolvating nebulizer system (dry plasma, HR-mode, Ni cones)' (§2.3)",
 "Number of Acquisition Passes": "2" + D + "alternative configurations; samples marked (HR) in Table 1",
 "Mass Resolution Assignment": "MR: medium resolution; HR: high resolution" + D + "§2.3",
 "Nebulizer Type": "N" + D + "introduced through a cyclonic glass spray chamber or an ESI Apex Ω system",
 "Spray Chamber Type and Cooling Temperature": "Cyclonic glass spray chamber, for MR wet-plasma work" + D + "§2.3",
 "Desolvation System": "MR: none; HR: ESI Apex Ω, with no auxiliary N2 flow" + D + "§2.3",
 "Plasma Thermal Mode": "MR: wet plasma; HR: dry plasma" + D + "§2.3",
 "Instrument Sensitivity": "56Fe: 1.4 nA (wet plasma, MR) to 2 nA (dry plasma, HR)" + D + "§2.3",
 "Monitored Masses": "54Fe, 56Fe, 57Fe, 58Fe → Fe; 53Cr, 60Ni → none" + D + "§2.3; ⁵³Cr and ⁶⁰Ni monitor ⁵⁴Cr and ⁵⁸Ni",
 "Reported Variables and Units": '"μ54Fe(7/6)", "μ58Fe(7/6)", "μ56Fe(7/4)", "μ58Fe(7/4)", δ56Fe' + D + "μ in ppm (Eq. 1), δ in ‰ (Eq. 2), relative to IRMM-524a",
 "Collector Configuration": "54Fe, 56Fe, 57Fe, 58Fe, 53Cr, 60Ni: Faraday collectors, static mode" + D + "§2.3; cup assignments not stated",
 "Number of Cycles per Block": "HR: 25 cycles; MR: 50 cycles" + D + "§2.3",
 "Integration Time per Cycle": "all: 8.369 s" + D + "§2.3",
 "Isotope Ratio Reported": ('"μ54Fe(7/6)": 54Fe/56Fe normalised to 57Fe/56Fe; "μ58Fe(7/6)": 58Fe/56Fe normalised to 57Fe/56Fe; "μ56Fe(7/4)": 56Fe/54Fe normalised to 57Fe/54Fe; '
                            '"μ58Fe(7/4)": 58Fe/54Fe normalised to 57Fe/54Fe; δ56Fe: 56Fe/54Fe' + D + "Eqs 1–2 and Table 1 notes; (k/j) names the normalising ratio"),
 "delta or epsilon Value Reference Standard": "Fe: IRMM-524a" + D + "'that has an identical isotopic composition to IRMM-014' (§2.3)",
 "Interfering Species": "54Fe: 54Cr+ and argides; 58Fe: 58Ni+ and argides; 56Fe, 57Fe: argides; other: N" + D + "argides " + ARG + " (§2.3)",
 "Interference Correction Method": ("54Fe: 54Cr monitored on 53Cr, argides resolved on the peak shoulder; 58Fe: 58Ni monitored on 60Ni, argides resolved on the peak shoulder; "
                                    "56Fe, 57Fe: argides resolved on the flat-topped peak shoulder in MR or HR; other: N" + D + "after purification Cr/Fe ≤ 1.7 × 10⁻⁶ and Ni/Fe ≤ 2 × 10⁻⁶ (§2.2)"),
 "Uncertainty Level": "95% confidence interval from Student's t" + D + "over n = 10–35 repeat measurements of each sample solution (§2.3)",
 "Procedural Blank Level": "Fe: ~70 ng" + D + "'negligible considering that 1-2 mg Fe was purified for each sample' (§2.2)",
 "Combination Method": ("all: average of n = 10–35 sample-standard bracketed measurements per sample solution, and weighted averages per group over the low-exposure samples (ε196Pt(8/5) ≤ 0.16), "
                        "with York-regression intercepts for IC and IIAB" + D + "§2.3; Table 1 notes g, h"),
 "Primary Calibration Standard Name": "all [Fe: IRMM-524a]" + D + "bracketing standard (§2.3)",
 "Secondary Reference Materials": "BHVO-2, BCR-2" + D + "§2.1",
 "Analytical Accuracy and Assessment Method": ('BHVO-2, BCR-2 ["μ54Fe(7/6)": average 2 ± 2 (95% c.i.); "μ58Fe(7/6)": average 4 ± 6 (95% c.i.); other: normal within uncertainties]'
                                               + D + "§3; agreeing with Schiller et al. (2020)"),
}
# ---- c04_hu
D = " — "
REE8 = "Ce, Nd, Sm, Eu, Gd, Dy, Er, Yb"
PHI = "φCe, φNd, φSm, φEu, φGd, φDy, φEr, φYb"
COL4 = {  # Hu et al. (Science Advances 7, 2021), Neptune Plus with OnTool booster at Chicago. Read 2026-09-30: Materials and Methods, Eq. 1, Table 1 and caption, Assessment of data accuracy.
 "Target Material": "calcium-aluminium-rich inclusion" + D + "fine-grained CAIs from Allende slabs and one coarse-grained CAI (TS32); BCR-2 is the geostandard",
 "Sample Preparation Method": "CAIs extracted from Allende slabs with a stainless steel dental tool and powdered, digested, REEs recovered from the U/TEVA matrix cut, extracted on TODGA and separated by two-step FPLC on Ln-Spec" + D + "Materials and Methods, after Tissot et al. (34)",
 "Digestion Step": ("HF–HNO3–HClO4 attack (3:1 HF/HNO3 with a few drops of HClO4, hot plate, 160 °C, 2 weeks); HCl–HNO3 attack (evaporated, then 2:1 HCl:HNO3, 1 week on a hot plate); "
                    "final uptake (dried, dissolved in concentrated HNO3, diluted in 3 M HNO3 and centrifuged)" + D + "the two attacks 'were performed twice to ensure complete digestion'"),
 "Digestion Acid(s)": "HF–HNO3–HClO4 attack: 3:1 HF/HNO3 + HClO4; HCl–HNO3 attack: 2:1 HCl:HNO3; final uptake: concentrated HNO3, then 3 M HNO3",
 "Digestion Temperature": "HF–HNO3–HClO4 attack: 160 °C; other: N",
 "Digestion Duration": "HF–HNO3–HClO4 attack: 2 weeks; HCl–HNO3 attack: 1 week; final uptake: N",
 "Final Solution Matrix": "N" + D + "standards 'diluted to the same concentration as the sample, in the same acid'; 15–25 ppb for the LREEs, 1.5–10 ppb for Eu and the HREEs",
 "Sample Aliquot Mass or Volume": "N" + D + "~30% of the U/TEVA matrix cut, equivalent to 24% of the whole CAI; CAIs of 15–440 mg",
 "Desolvation System": "all: Apex Omega desolvating nebulizer" + D + "Materials and Methods",
 "Acquisition Pass": "main configuration; subconfiguration" + D + "for Dy and Yb 'a subconfiguration was used to monitor isobaric interferences'; the cup configurations are in table S2",
 "Number of Acquisition Passes": "2" + D + "the subconfiguration only for Dy and Yb",
 "Instrument Sensitivity": "140Ce: 10 V; 142Nd: 4 V; 152Sm: 3.5 V; 151Eu, 158Gd: 2 V; 164Dy: 3 V; 166Er, 174Yb: 1.5 V; other: N" + D + "at 15–25 ppb (LREE) or 1.5–10 ppb; the text prints '151Er' for ¹⁵¹Eu",
 "Target Species": REE8 + D + "isotopic compositions; concentrations of all REEs were also measured",
 "Monitored Masses": "140Ce, 142Ce → Ce; 142Nd, 144Nd, 146Nd → Nd; 148Sm, 152Sm → Sm; 151Eu, 153Eu → Eu; 156Gd, 158Gd → Gd; 162Dy, 163Dy, 164Dy → Dy; 166Er, 168Er → Er; 172Yb, 174Yb → Yb" + D + "the ratios of Table 1, ¹⁴²Nd and ¹⁶³Dy named in the text; the full cup configurations are in table S2",
 "Reported Variables and Units": PHI + D + "‰/amu relative to the OL-REE standards (Eq. 1)",
 "Number of Cycles per Block": "main configuration: 40 cycles; subconfiguration: 2, measured at the beginning" + D + "Materials and Methods",
 "Integration Time per Cycle": "all: 8.184 s" + D + "4.142 s in the subconfiguration",
 "Baseline Measurement Approach": "60 s baseline after 60 s take-up, per measurement" + D + "idle time zero between cycles of one configuration, 10 s after a configuration change",
 "Collector Configuration": "N" + D + "static mode for most REEs, a subconfiguration for Dy and Yb; the cup configurations are in table S2",
 "Combination Method": "all: per sample, over 1 to 12 (typically 5) STD-SMP-STD bracketings" + D + "'The reported φE values were calculated based on 1 to 12 (typically 5) STD-SMP-STD bracketings'; Fig. 1 also shows the mean of seven CAIs",
 "Isotope Ratio Reported": "φCe: 142Ce/140Ce; φNd: 146Nd/144Nd; φSm: 152Sm/148Sm; φEu: 153Eu/151Eu; φGd: 158Gd/156Gd; φDy: 164Dy/162Dy; φEr: 168Er/166Er; φYb: 174Yb/172Yb" + D + "Table 1 caption; 'the two most abundant isotopes for each REE'",
 "delta or epsilon Value Reference Standard": REE8 + ": OL-REE series" + D + "prepared in-house from high-purity ESPI oxide powders",
 "Mass Bias Correction Strategy": "Standard-sample bracketing, each sample ratio normalised to the average of the two bracketing OL-REE standards, diluted to the same concentration in the same acid" + D + "'SSB is advantageous over the double-spike approach because one can distinguish mass-dependent fractionation from isotopic anomalies'",
 "Calibration Strategy per Target Species": REE8 + ": standard-sample bracketing against the OL-REE standard of the same element",
 "Blank / Background Correction Method": "Background corrected off-line in a spreadsheet, from the 60 s baseline" + D + "'correcting for background and isobaric interferences'",
 "Interfering Species": "162Dy: 162Er; 164Dy: 164Er; other: N" + D + "isobars of neighbouring elements in general",
 "Interference Correction Method": ("162Dy, 164Dy: 166Er from the subconfiguration, scaled through 166Er/163Dy to the main configuration and multiplied by 162Er/166Er and 164Er/166Er; "
                                    "other: monitoring another isotope of the interfering element and subtracting its intensity at natural abundance" + D + "Materials and Methods"),
 "Uncertainty Level": "95% confidence interval" + D + "Student's t, from the sample's own φE values with six or more brackets, otherwise from standards bracketed by standards",
 "Procedural Blank Level": REE8 + ": < 0.25 ng" + D + "'negligible compared to the amounts of REEs in the samples'",
 "Primary Calibration Standard Name": "all [" + REE8 + ": OL-REE series]",
 "Secondary Reference Materials": "BCR-2" + D + "'processed with the CAIs'",
 "Analytical Accuracy and Assessment Method": "BCR-2 [all: zero within error bars, typically < 0.05‰/amu]" + D + "Assessment of data accuracy; replicates from the Mo-chemistry matrix cut agree, with LREEs shifted ~0.1‰/amu",
}
# ---- c05_ibanez
D = " — "
DZR = "δ91/90Zr, δ92/90Zr, δ94/90Zr, δ96/90Zr"
COL5 = {  # Ibañez-Mejia & Tissot 2019 (Science Advances 5), Nu Plasma II at MIT. Read 2026-09-30: Materials and Methods (reference material, mineral separation, CA, U-Pb, Zr stable isotope analyses), Table 1 notes.
 "Target Material": "zircon; baddeleyite; bulk rock" + D + "single crystals and bulk rock of the FC-1 anorthositic gabbro (Duluth Complex)",
 "Digestion Step": ("chemical abrasion (19 zircons for U-Pb, annealed at 900 °C for 60 h, then leached in 29 M HF in a Parr vessel at 215 °C for 12 h); "
                    "U-Pb dissolution (dated crystals, 29 M HF in microcapsules in a Parr vessel, 215 °C, 48 h); "
                    "Zr-only dissolution (crystals not dated, fluxed in 20% HNO3 at 60 °C for 2 h, then 29 M HF in microcapsules in a Parr vessel, 215 °C, 60 h); "
                    "spike equilibration (with the ⁹¹Zr–⁹⁶Zr spike, fluxed at 140 °C overnight, dried down twice and redigested)" + D + "Materials and Methods"),
 "Digestion Acid(s)": "chemical abrasion: 29 M HF; U-Pb dissolution: 29 M HF; Zr-only dissolution: 20% HNO3, then 29 M HF; spike equilibration: N",
 "Digestion Temperature": "chemical abrasion: 900 °C (annealing), then 215 °C; U-Pb dissolution: 215 °C; Zr-only dissolution: 60 °C, then 215 °C; spike equilibration: 140 °C",
 "Digestion Duration": "chemical abrasion: 60 h, then 12 h; U-Pb dissolution: 48 h; Zr-only dissolution: 2 h, then 60 h; spike equilibration: overnight",
 "Final Solution Matrix": "all: 0.59 M HNO3 + 0.28 M HF at 60 ng/g total Zr" + D + "samples and bracketing standards matched in concentration and acid matrix",
 "Desolvation System": "all: Cetac Aridus II" + D + "'Analyses were conducted in dry plasma mode'",
 "Nebulizer Type": "N" + D + "introduction through a Cetac Aridus II desolvator nebulizer",
 "Plasma Thermal Mode": "all: dry plasma",
 "Instrument Sensitivity": "N" + D + "'around 572 V/ppm of total Zr'",
 "Monitored Masses": "90Zr, 91Zr, 92Zr, 94Zr, 96Zr → Zr; mass 93, 95Mo, 98Mo → none" + D + "'Masses 90, 91, 92, 93, 94, 95, 96, and 98 were measured ... allowing direct monitoring of all Zr isotopes and Mo interferences (masses 95 and 98)'; the use of mass 93 is not stated",
 "Reported Variables and Units": DZR + D + "‰ relative to ZrNIST; δ⁹⁴/⁹⁰Zr is the one discussed",
 "Collector Configuration": "90Zr, 91Zr, 92Zr, mass 93, 94Zr, 95Mo, 96Zr, 98Mo: static mode at 0.5 amu spacing in the Nu Plasma II collector block",
 "Number of Cycles per Block": "all: 50 cycles",
 "Integration Time per Cycle": "all: 5 s",
 "Isotope Ratio Reported": "δ91/90Zr: 91Zr/90Zr; δ92/90Zr: 92Zr/90Zr; δ94/90Zr: 94Zr/90Zr; δ96/90Zr: 96Zr/90Zr",
 "delta or epsilon Value Reference Standard": "Zr: ZrNIST" + D + "a NIST gravimetric Zr solution being calibrated as an isotopic reference material",
 "Interfering Species": "N" + D + "Mo isobars, monitored on masses 95 and 98",
 "Interference Correction Method": "N" + D + "the reported data 'are uncorrected for residual Mo'",
 "Additional Notes": "Mo doping test: Offset δ94/90ZrNIST = −63.4 · x, x the Mo/Zr atomic ratio" + D + "used to show the residual Mo is negligible",
 "Uncertainty Propagation Method": "all: the 2σ external reproducibility of the spiked ZrNIST in each run, assigned to each determination" + D + "'similar in magnitude or slightly larger than the internal uncertainty determined from counting statistics'",
 "Procedural Blank Level": "N" + D + "the blank comparison stated concerns non-radiogenic Pb in the U-Pb work",
 "Constants and Reference Values Used": "N" + D + "the constants stated (²³⁸U/²³⁵U = 137.818, ¹⁸O/¹⁶O = 0.00205, α = 0.18%/amu) belong to the coupled ID-TIMS U-Pb work",
 "Primary Calibration Standard Name": "all [Zr: ZrNIST, spiked at the same level as the samples]",
 "Within-Session Analytical Precision and Assessment Method": "ZrNIST [all: 2σ external reproducibility of the spiked ZrNIST measurements in each run]",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "N",
 "Counting Statistics Error": "N" + D + "the internal counting-statistics uncertainty is used for comparison but not tabulated",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "all: internal uncertainty from counting statistics" + D + "similar in magnitude to or slightly smaller than the external reproducibility assigned to each determination",
}
# ---- c06_nie
D = " — "
NIE_RMS = "BHVO-2, BCR-2, BE-N, W-2, AGV-2, GSR-1, GS-N, G-A, G-3"
COL6 = {  # Nie & Dauphas 2019 (ApJL 884), Neptune at Chicago. Read 2026-09-30: Appendix A.1–A.4, Figs 7–8.
 "Target Material": "lunar rock; terrestrial rock; carbonaceous chondrite" + D + "lunar samples, geostandards (basalts, granites, peridotite mixes) and Allende",
 "Digestion Step": ("HF–HNO3–HClO4 attack (4 ml 28 M HF + 2 ml 15 M HNO3 + 1 ml 10 M HClO4, closed 30 ml fluoropolymer beaker, 130 °C, 24 h); "
                    "HCl–HNO3 attack (dried at 130 °C, 4.5 ml 11 M HCl + 1.5 ml 15 M HNO3, closed, 130 °C, 24 h, repeated twice); "
                    "HNO3 attack (dried, 4 ml 15 M HNO3, closed, hotplate, 24 h); Parr bomb (undigested residue, 175–180 °C, at least 3 days)" + D + "A.1; the bomb step only when a sample was not fully digested"),
 "Digestion Acid(s)": "HF–HNO3–HClO4 attack: 28 M HF + 15 M HNO3 + 10 M HClO4; HCl–HNO3 attack: 11 M HCl + 15 M HNO3; HNO3 attack: 15 M HNO3; Parr bomb: N",
 "Digestion Temperature": "HF–HNO3–HClO4 attack: 130 °C; HCl–HNO3 attack: 130 °C; HNO3 attack: N; Parr bomb: 175–180 °C",
 "Digestion Duration": "HF–HNO3–HClO4 attack: 24 h; HCl–HNO3 attack: 24 h, twice; HNO3 attack: 24 h; Parr bomb: at least 3 days",
 "Final Solution Matrix": "all: 0.3 M HNO3, ~15–25 ppb Rb" + D + "samples and standards matched in Rb concentration within 1%",
 "Faraday Cup Amplifier Resistor Values": "85Rb, 87Rb, 88Sr: 10^11 Ω" + D + "'All three collectors were equipped with the 10^11 Ω amplifiers'",
 "Desolvation System": "all: none" + D + "a dual cyclonic-Scott-type quartz spray chamber",
 "Instrument Sensitivity": "85Rb: ~1–1.5 V at 15–25 ppb in low resolution",
 "Monitored Masses": "85Rb, 87Rb → Rb; 88Sr → none" + D + "⁸⁸Sr monitors ⁸⁷Sr on ⁸⁷Rb",
 "Reported Variables and Units": "δ87Rb" + D + "‰ relative to NIST SRM984",
 "Collector Configuration": "85Rb: L2; 87Rb: axial (A); 88Sr: H1" + D + "A.3",
 "Number of Cycles per Block": "all: 25 cycles" + D + "a single block",
 "Integration Time per Cycle": "all: 4.194 s",
 "Wash Time Between Samples": "60 s with 0.45 M HNO3" + D + "take-up time 90 s",
 "Analysis Sequence": "Standard-sample bracketing, with the 0.3 M HNO3 dilution acid measured before and after each sample and standard under identical conditions" + D + "A.3",
 "Isotope Ratio Reported": "δ87Rb: 87Rb/85Rb",
 "delta or epsilon Value Reference Standard": "Rb: NIST SRM984",
 "Blank / Background Correction Method": "Average intensity of the two bracketing 0.3 M HNO3 blank measurements subtracted from each sample and standard" + D + "background 0.001–0.003 V on ⁸⁵Rb",
 "Interfering Species": "87Rb: 87Sr; other: N" + D + "monitored on ⁸⁸Sr",
 "Interference Correction Method": "87Rb: 87Sr subtracted from 88Sr assuming a constant 87Sr/88Sr = 0.085; other: N" + D + "0.0835–0.0885 shifts δ⁸⁷Rb by 0.008‰ at most",
 "Uncertainty Level": "2σ/√n" + D + "σ from the standards treated as samples, n the replicates of the sample",
 "Procedural Blank Level": "Rb: ~0.14 ng" + D + "less than 0.5% of the Rb of a typical sample (40 ng)",
 "Combination Method": "δ87Rb: average of 5–12 repeat measurements per sample solution" + D + "bulk Moon and Earth from regressions against La/U (Fig. 1)",
 "Primary Calibration Standard Name": "all [Rb: NIST SRM984]",
 "Secondary Reference Materials": NIE_RMS + ", SRM984 as a sample, DTS-2b + SRM984, PCC-1 + SRM984, Allende" + D + "A.4",
 "Analytical Accuracy and Assessment Method": ("SRM984 as a sample, DTS-2b + SRM984, PCC-1 + SRM984 [δ87Rb: zero within error]; " + NIE_RMS + ", Allende [δ87Rb: reproducible, agree with published results]"
                                               + D + "A.4, Fig. 8"),
}
# ---- c078_nowell
D = " — "
OSR = "190Os/188Os, 189Os/188Os, 187Os/188Os, 186Os/188Os, 184Os/188Os"
OS_IRR = "; ".join("%s: %s" % (r, r) for r in OSR.split(", "))
MB = "Exponential law, internal normalisation to 192Os/188Os = 3.083, and to 189Os/188Os = 1.21978 for comparison" + D + "§3.5; the discussion uses the ¹⁹²Os/¹⁸⁸Os-corrected values"
COL7 = {  # Nowell et al. 2008 (Chemical Geology 248) — Neptune at Durham. Read 2026-09-30: §3.1, §3.4–3.6, Tables 2a, 3 and 7a.
 "Target Material": "Os reference material solution" + D + "UMd, DTM, LOsST and DROsS",
 "Final Solution Matrix": "all: Teflon-distilled 3 or 5 mol/l HCl" + D + "200 ng/ml to 2.5 µg/ml Os",
 "Desolvation System": "all: none" + D + "desolvating nebulisers 'have been shown to suffer severe memory problems for Os' (§3.1)",
 "Instrument Sensitivity": "N" + D + "~50 V for a 1 µg/ml Os solution at ~80 µl/min free aspiration",
 "Monitored Masses": "184Os, 186Os, 187Os, 188Os, 189Os, 190Os, 192Os → Os; 182W, 185Re → none" + D + "Table 2a; ¹⁸²W and ¹⁸⁵Re are the monitor isotopes",
 "Reported Variables and Units": OSR + D + "Table 7a",
 "Collector Configuration": "182W: L4; 184Os: L3; 185Re: L2; 186Os: L1; 187Os: Ax; 188Os: H1; 189Os: H2; 190Os: H3; 192Os: H4" + D + "Table 2a",
 "Number of Cycles per Block": "all: 5 cycles" + D + "9 blocks (§3.1)",
 "Integration Time per Cycle": "all: 4 s",
 "Mass Bias Correction Strategy": "Internal normalisation, applied offline in Excel with the abundance-sensitivity and W/Re corrections" + D + "§3.1, §3.5",
 "Mass Fractionation Law": "Exponential law" + D + "§3.5",
 "Internal Normalization Element and Isotope Ratio": "192Os/188Os = 3.083" + D + "189Os/188Os = 1.21978 also used for comparison",
 "Isotope Ratio Reported": OS_IRR + D + "normalised to ¹⁹²Os/¹⁸⁸Os = 3.083",
 "Blank / Background Correction Method": "Abundance sensitivity (0.5–1 ppm, from the low-mass tail of a 30 V 192Os beam on the SEM) corrected offline" + D + "§3.1",
 "Interfering Species": "184Os: 184W; 186Os: 186W; 187Os: 187Re; other: N" + D + "Table 2a",
 "Interference Correction Method": "184Os, 186Os: W subtracted from the 182W monitor with 182W/184W and 182W/186W interference ratios; 187Os: Re from the 185Re monitor with 185Re/187Re; other: N" + D + "ratios from doping experiments (§3.6.1, Table 3), e.g. ¹⁸⁵Re/¹⁸⁷Re = 0.598120",
 "Primary Calibration Standard Name": "N" + D + "internal normalisation; the four Os RMs are the materials measured",
 "Secondary Reference Materials": "UMd, DTM, LOsST, DROsS",
 "Within-Session Analytical Precision and Assessment Method": "UMd, DTM [all: 2SD of the analyses in each session]" + D + "Table 7a",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "UMd [187Os/188Os: 0.113795 ± 25 (2SD, n = 94)]; DTM [187Os/188Os: 0.173923 ± 26 (2SD, n = 121)]" + D + "9 sessions over 11 months (Table 7a)",
 "Analytical Accuracy and Assessment Method": "UMd [187Os/188Os: +26 ppm; 186Os/188Os: −125 ppm]; DTM [187Os/188Os: −12 ppm; 186Os/188Os: −108 ppm]" + D + "offset from Durham N-TIMS (Table 7a)",
 "Faraday Cup Amplifier Resistor Values": "all: 10^11 Ω" + D + "a maximum beam of 50 V per channel",
 "Faraday Cup Gain Calibration Method": "all: amplifier gains measured on peak with the line of sight valve closed at the start of each session, with the Virtual Amplifier in rotation mode to cancel them" + D + "§3.1",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "all: 2SE = 2SD/n^0.5, n = 45 cycles" + D + "within-run errors (§3)",
}
COL8 = {  # Nowell et al. 2008 — Nu Plasma at NIGL. Read 2026-09-30: §3.2, §3.5, Table 2b, Table 7a (NIGL row).
 "Target Material": "Os reference material solution" + D + "DTM and LOsST",
 "Final Solution Matrix": "all: Teflon-distilled 3 mol/l HCl",
 "Nebulizer Type": "GE Micromist" + D + "§3.2",
 "Sample Uptake Rate": "~400 µl/min, free aspiration" + D + "§3.2; ~6400 µl over a ~16 min analysis",
 "Desolvation System": "all: none" + D + "GE Micromist nebuliser and Cinnabar spray chamber (§3.2)",
 "Instrument Sensitivity": "N" + D + "~20 V for a 1 µg/ml Os solution at ~400 µl/min",
 "Acquisition Pass": "sequence 1; sequence 2" + D + "'masses 183W to 189Os collected in the first sequence and 188Os to 192Os collected in the second sequence with a 4 s magnet settle time between sequences' (§3.2)",
 "Number of Acquisition Passes": "2",
 "Monitored Masses": "184Os, 186Os, 187Os, 188Os, 189Os, 190Os, 192Os → Os; 183W, 185Re → none" + D + "Table 2b; ¹⁸³W and ¹⁸⁵Re are the monitor isotopes",
 "Reported Variables and Units": "187Os/188Os, 186Os/188Os, 184Os/188Os" + D + "Table 7a (NIGL row)",
 "Collector Configuration": "183W: L2; 184Os: L1; 185Re: Ax; 186Os: H1; 187Os: H2; 188Os: H3 (sequence 1), L2 (sequence 2); 189Os: H4 (sequence 1), L1 (sequence 2); 190Os: Ax; 192Os: H2 (sequence 2)" + D + "Table 2b",
 "Number of Cycles per Block": "all: 50 cycles" + D + "1 block",
 "Integration Time per Cycle": "183W, 184Os, 185Re, 186Os, 187Os: 8 s; 190Os, 192Os: 4 s; 188Os, 189Os: 8 s (sequence 1), 4 s (sequence 2)" + D + "Table 2b",
 "Peak Flatness Method and Threshold": "N" + D + "¹⁸⁸Os used for peak-centering in both sequences, zoom quad adjusted for optimal peak alignment",
 "Mass Bias Correction Strategy": "Internal normalisation, processed on-line with the W and Re corrections" + D + "§3.2",
 "Mass Fractionation Law": "Exponential law" + D + "'was also used for the Nu Plasma measurements' (§3.5)",
 "Internal Normalization Element and Isotope Ratio": "192Os/188Os = 3.083" + D + "Table 7a",
 "Isotope Ratio Reported": "187Os/188Os: 187Os/188Os; 186Os/188Os: 186Os/188Os; 184Os/188Os: 184Os/188Os",
 "Interfering Species": "184Os: 184W; 186Os: 186W; 187Os: 187Re; other: N" + D + "Table 2b",
 "Interference Correction Method": "184Os, 186Os: W from the 183W monitor; 187Os: Re from the 185Re monitor; other: N" + D + "on-line; abundance sensitivity not measured, likely > 1 ppm at ~2 × 10⁻⁸ mbar",
 "Primary Calibration Standard Name": "N" + D + "internal normalisation; DTM and LOsST are the materials measured",
 "Secondary Reference Materials": "DTM, LOsST",
 "Within-Session Analytical Precision and Assessment Method": "DTM [187Os/188Os: 0.173910 ± 21 (2SD, n = 9)]" + D + "session 23-05-06 (Table 7a)",
 "Analytical Accuracy and Assessment Method": "DTM [187Os/188Os: compared with Durham N-TIMS 0.173927 ± 5]" + D + "Table 7a",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "all: 2SE = 2SD/n^0.5, n = 50 cycles" + D + "within-run errors (§3)",
}
# ---- c09_pringle
D = " — "
COL9 = {  # Pringle & Moynier 2017 (EPSL 473), Neptune Plus at IPGP. Read 2026-09-30: §2.1–2.3, Tables 1–3.
 "Target Material": "terrestrial rock; chondrite; achondrite; lunar rock" + D + "basalts, andesite, granite; CC, OC and EC chondrites; eucrite, angrite; Apollo basalts and norite",
 "Digestion Step": "HF/HNO3 attack (concentrated HF/HNO3, closed Teflon bombs, 130 °C, >48 h); HCl step (after evaporation, 6N HCl at 130 °C to dissolve fluoride complexes, then evaporated to dryness)" + D + "§2.2",
 "Digestion Acid(s)": "HF/HNO3 attack: concentrated HF/HNO3; HCl step: 6N HCl",
 "Digestion Temperature": "HF/HNO3 attack: 130 °C; HCl step: 130 °C",
 "Digestion Duration": "HF/HNO3 attack: >48 h; HCl step: N",
 "Acquisition Pass": "spray chamber; APEX" + D + "'measured using both the spray chamber and the APEX sample introduction systems' in most cases (§2.3)",
 "Number of Acquisition Passes": "2",
 "Final Solution Matrix": "spray chamber: 0.1N HNO3, 10 ppb Rb; APEX: 0.1N HNO3, 4 ppb Rb" + D + "§2.2–2.3",
 "Nebulizer Type": "ESI PFA MicroFlow nebulizer (100 µL/min)" + D + "§2.3",
 "Spray Chamber Type and Cooling Temperature": "Quartz cyclonic spray chamber" + D + "§2.3",
 "Desolvation System": "spray chamber: none; APEX: APEX desolvating introduction system" + D + "the APEX 'routinely yielded lower precisions (by ~0.03‰)'",
 "Faraday Cup Amplifier Resistor Values": "all: 10^11 Ω" + D + "§2.3",
 "Mass Resolution Setting": "Low resolution" + D + "§2.3",
 "Instrument Sensitivity": "85Rb: ~1.0 V" + D + "at 10 ppb (spray chamber) or 4 ppb (APEX); high beams avoided for memory",
 "Monitored Masses": "85Rb, 87Rb → Rb; 84Sr, 86Sr, 88Sr → none" + D + "Table 2; 'Strontium was monitored using the 88Sr ion beams'",
 "Reported Variables and Units": "δ87Rb" + D + "‰ relative to the bracketing standard (Eq. 1)",
 "Collector Configuration": "84Sr: L2; 85Rb: L1; 86Sr: C; 87Rb: H1 (with 87Sr); 88Sr: H2" + D + "Table 2",
 "Number of Blocks per Measurement": "N" + D + "'blocks of 20 cycles'",
 "Number of Cycles per Block": "all: 20 cycles",
 "Integration Time per Cycle": "all: 8.389 s",
 "Isotope Ratio Reported": "δ87Rb: 87Rb/85Rb",
 "delta or epsilon Value Reference Standard": "Rb: NIST SRM984 RbCl" + D + "BCR-2 as the bracketing standard in some sessions",
 "Blank / Background Correction Method": "Instrumental background measured at the beginning of and throughout each session (typically < 1 mV on 85Rb) and subtracted" + D + "§2.3",
 "Interfering Species": "87Rb: 87Sr; other: N" + D + "doubly charged Er and Yb are separated chemically (§2.2)",
 "Interference Correction Method": "87Rb: 87Sr corrected from the 88Sr monitor; other: N" + D + "final ⁸⁸Sr/⁸⁵Rb < 0.005",
 "Uncertainty Propagation Method": "δ87Rb: 2 se from repeated measurements, with the largest 2 se of a multiply analysed sample used for samples run fewer than 3 times" + D + "§2.3",
 "Combination Method": "δ87Rb: average of repeated measurements per sample, and averages per sample group" + D + "§2.3; Table 3",
 "Other Statistics": "δ87Rb: 2 standard errors per sample, and 2 standard deviations per group average" + D + "Table 1 notes",
 "Primary Calibration Standard Name": "all [Rb: NIST SRM984 RbCl, with BCR-2 in some sessions]",
 "Secondary Reference Materials": "BCR-2, AGV-2, BHVO-2, GS-N, SRM984 through chemistry, Allende, pure Rb ICP-MS solution" + D + "§2.3",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "pure Rb ICP-MS solution [δ87Rb: ±0.01‰ (n = 40)]" + D + "run as an external standard each session",
 "Analytical Accuracy and Assessment Method": "SRM984 through chemistry [δ87Rb: 0.00 ± 0.03‰]; Allende [δ87Rb: duplicate splits 0.12 ± 0.02‰ and 0.14 ± 0.04‰]" + D + "§2.3",
 "Additional Notes": "Extraction voltage −2000 V; peristaltic pump 5 rpm (Table 1)",
}
# ---- c10_schon
D = " — "
SC_RMS = "BHVO-2, BCR-2, AGV-1, SCo-1, Bouvante, Bereba, Colony"
COL10 = {  # Schönbächler et al. 2025 (Meteoritics & Planetary Science), Neptune Plus at ETH Zurich. Read 2026-09-30: Samples and methods, Results (precision and accuracy), Table 1 note.
 "Target Material": "returned asteroid sample; carbonaceous chondrite; eucrite; terrestrial rock" + D + "Ryugu (A0106, A0106-A0107, C0108), Tagish Lake, Tarda, Ivuna, Colony, Bouvante, Bereba and terrestrial RMs",
 "Digestion Step": ("hotplate HF–HNO3 (Ryugu, 180 °C, 3–7 days); HNO3–HCl (120 °C, 12 h); HNO3–H2O2 dissolution; high-PT HF–HNO3 (Tagish Lake, Tarda, octagonal-body Savillex vials, 220 °C, about a week); "
                    "Parr bomb (Ivuna PB, BCR-2, AGV-1, HF–HNO3, 170 °C); Ivuna high-PT (HF–HNO3 for 3 days, then HCl for 2 days, Savillex vial in an oven at 160 °C)" + D + "BHVO-2 in HF–HNO3 on a hotplate"),
 "Digestion Acid(s)": "hotplate HF–HNO3: concentrated HF–HNO3; HNO3–HCl: HNO3–HCl; HNO3–H2O2 dissolution: HNO3–H2O2; high-PT HF–HNO3: concentrated HF–HNO3; Parr bomb: concentrated HF–HNO3; Ivuna high-PT: concentrated HF–HNO3, then concentrated HCl",
 "Digestion Temperature": "hotplate HF–HNO3: 180 °C; HNO3–HCl: 120 °C; high-PT HF–HNO3: 220 °C; Parr bomb: 170 °C; Ivuna high-PT: 160 °C; other: N",
 "Digestion Duration": "hotplate HF–HNO3: 3–7 days; HNO3–HCl: 12 h; high-PT HF–HNO3: about a week; Ivuna high-PT: 3 days, then 2 days; other: N",
 "Final Solution Matrix": "all: 0.5 M HNO3–0.005 M HF at 30 ppb Zr" + D + "samples and standards",
 "Faraday Cup Amplifier Resistor Values": "90Zr, 91Zr, 92Zr, 94Zr, 96Zr, 95Mo: 10^11 Ω; 99Ru, 101Ru: 10^12 Ω",
 "Desolvation System": "all: Aridus II",
 "Instrument Sensitivity": "N" + D + "total Zr ion beams 3.5–13 V at 30 ppb",
 "Monitored Masses": "90Zr, 91Zr, 92Zr, 94Zr, 96Zr → Zr; 95Mo, 99Ru, 101Ru → none",
 "Reported Variables and Units": "ε91Zr, ε92Zr, ε96Zr" + D + "relative to NIST SRM 3169 (Eq. 1)",
 "Collector Configuration": "N" + D + "cup positions not stated; amplifiers under Faraday Cup Amplifier Resistor Values",
 "Number of Cycles per Block": "all: 60 ratios" + D + "static collection",
 "Integration Time per Cycle": "all: 4.2 s",
 "Isotope Ratio Reported": "ε91Zr: 91Zr/90Zr; ε92Zr: 92Zr/90Zr; ε96Zr: 96Zr/90Zr" + D + "normalised to ⁹⁴Zr/⁹⁰Zr = 0.3381",
 "delta or epsilon Value Reference Standard": "Zr: NIST SRM 3169",
 "Interfering Species": "94Zr: 40Ar2 14N+; 96Zr: 40Ar2 16O+; other: N" + D + "Mo and Ru isobars, corrected from masses 95, 99 and 101; the affected masses are not listed",
 "Interference Correction Method": ("94Zr, 96Zr: argide interferences minimised by tuning, with an on-peak background correction; "
                                    "other: Mo and Ru corrected from the signals on masses 95, 99 and 101, with an initial Mo correction using a mass bias relative to 91Zr/90Zr = 0.21798" + D + "after Schönbächler et al. (2004)"),
 "Procedural Blank Level": "Zr: 0.08–0.24 ng" + D + "0.08 and 0.24 ng with Tarda and Tagish Lake, 0.09 and 0.13 ng with Ivuna",
 "Primary Calibration Standard Name": "all [Zr: NIST SRM 3169]",
 "Secondary Reference Materials": SC_RMS,
 "Within-Session Analytical Precision and Assessment Method": "all [ε91Zr: 0.35; ε92Zr: 0.21; ε96Zr: 1.00]" + D + "2SD of NIST SRM 3169 for an average session at 30 ppb (n = 32)",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": SC_RMS + " [ε91Zr: 0.3; ε92Zr: 0.2; ε96Zr: 1.0]" + D + "average 2SD over 10 months, n = 13–99 (eucrites and Colony n = 17–38)",
 "Analytical Accuracy and Assessment Method": SC_RMS + " [all: measured repeatedly to verify data quality]" + D + "doping tests with Ti, V, Cr, Mo, Hf and W 'have no effect on the accuracy of the Zr isotope data'",
}
# ---- c11_vankooten
D = " — "
COL11 = {  # van Kooten et al. 2026 (Nature Astronomy), Thermo Neoma at Copenhagen. Read 2026-09-30: Methods (sample preparation, MC-ICPMS).
 "Target Material": "bulk chondrite; chondrule" + D + "anomalous and grouped carbonaceous chondrites; type I chondrules from Leoville (CV)",
 "Sample Preparation Method": "Handpieces cut into 2 mm slabs with a diamond wire saw; saw dust and crushed fusion-crust-free pieces digested; chondrules drilled out with tungsten carbide bits" + D + "Methods",
 "Digestion Step": "Parr bomb (3:1 7 M HNO3 : 28 M HF, 1 day at 150 °C and 2 days at 210 °C); aqua regia (dried, taken up for two more days on a hotplate); NaOH fusion (Si portion, silver crucibles, 720 °C, 13 min)" + D + "Methods",
 "Digestion Acid(s)": "Parr bomb: 3:1 7 M HNO3 : 28 M HF; aqua regia: aqua regia; NaOH fusion: NaOH, then Milli-Q water and HNO3",
 "Digestion Temperature": "Parr bomb: 150 °C, then 210 °C; aqua regia: N; NaOH fusion: 720 °C",
 "Digestion Duration": "Parr bomb: 3 days; aqua regia: 2 days; NaOH fusion: 13 min",
 "Digestion Vessel Type": "Parr bombs; silver crucibles for the NaOH fusion",
 "Final Solution Matrix": "N" + D + "the Cr cut is eluted in 6 M HCl; the measurement matrix is not stated",
 "Sample Aliquot Mass or Volume": "~100–200 mg of saw dust and crushed pieces" + D + "5% fractions for ICPMS and for Al/Mg",
 "Acquisition Pass": "Fe; Cr; Mg" + D + "separate introduction systems and acquisition settings (Methods)",
 "Number of Acquisition Passes": "3",
 "Mass Resolution Setting": "Medium resolution, M/ΔM > 6,000" + D + "defined by the 5% to 95% peak edge width",
 "Mass Resolution Assignment": "all: medium resolution" + D + "'to resolve gas-based interferences on the high-mass side'",
 "Faraday Cup Amplifier Resistor Values": "24Mg, 25Mg, 26Mg: 10^11 Ω; other: N",
 "Desolvation System": "Fe: ESI Apex2HF with an actively cooled membrane unit; Cr: ESI Apex HF with an actively cooled membrane unit; Mg: ESI Apex Omega",
 "Sample Uptake Rate": "30 µl/min" + D + "for Fe, Cr and Mg",
 "Interface Cone Configuration": "Jet sampler and X skimmer cones" + D + "stated for the Cr measurements",
 "Make-up Gas and Flow Rate": "None, no auxiliary gas to the introduction system for Cr" + D + "Cr 'measured without the use of an auxiliary gas to the introduction system to reduce gas-based interferences'",
 "RF Power": "N" + D + "Cr measured 'at low radiofrequency power and sample gas inflow'",
 "Instrument Sensitivity": "24Mg, 25Mg, 26Mg: 80–90 V; other: N" + D + "typical signal intensities",
 "Target Species": "Fe, Cr, Mg" + D + "Si isotopes come from a separate NaOH-fusion procedure",
 "Monitored Masses": "54Fe, 56Fe, 57Fe, 58Fe → Fe; 50Cr, 52Cr, 53Cr, 54Cr → Cr; 24Mg, 25Mg, 26Mg → Mg; 60Ni, 49Ti, 51V → none" + D + "⁶⁰Ni and ⁵³Cr monitored in the Fe run, ⁴⁹Ti, ⁵¹V and ⁵⁶Fe in the Cr run",
 "Reported Variables and Units": "μ54Fe, μ53Cr, μ54Cr, μ26Mg*" + D + "μ relative to IRMM-014, SRM979 and DTS-2b; μ³⁰Si from the separate Si procedure",
 "Collector Configuration": "N" + D + "cup positions not stated; Fe set-up follows Schiller et al.",
 "Number of Cycles per Block": "Fe: 200 cycles; Cr: 100 cycles; Mg: 100 cycles",
 "Integration Time per Cycle": "54Fe, 56Fe, 57Fe, 58Fe, 50Cr, 52Cr, 53Cr, 54Cr: 8.3 s; 24Mg, 25Mg, 26Mg: 16.7 s; other: N",
 "Baseline Measurement Approach": "On-peak baseline before each analysis: 25 × 16.7 s for Fe and Mg, 75 s for Cr",
 "Mass Bias Correction Strategy": "Standard-sample bracketing" + D + "against IRMM-014, SRM979 and DTS-2b; the normalisation is not restated (Fe follows Schiller et al.)",
 "delta or epsilon Value Reference Standard": "Fe: IRMM-014; Cr: SRM979; Mg: DTS-2b",
 "Calibration Strategy per Target Species": "Fe: bracketing against IRMM-014; Cr: bracketing against SRM979; Mg: bracketing against DTS-2b",
 "Blank / Background Correction Method": "On-peak baseline measured before each analysis",
 "Interfering Species": "54Fe: 54Cr; 58Fe: 58Ni; other: N" + D + "isobars on the Cr masses from Ti, V and Fe, monitored on ⁴⁹Ti, ⁵¹V and ⁵⁶Fe",
 "Interference Correction Method": "54Fe: 54Cr corrected from 53Cr; 58Fe: 58Ni corrected from 60Ni; other: N" + D + "Ti, V and Fe on Cr corrected from ⁴⁹Ti, ⁵¹V and ⁵⁶Fe",
 "Combination Method": "all: mean of ten standard-bracketed analyses per measurement, samples typically analysed two to four times, and weighted means per grouplet",
 "Primary Calibration Standard Name": "all [Fe: IRMM-014; Cr: SRM979; Mg: DTS-2b]",
 "Secondary Reference Materials": "BHVO2, DTS-2b" + D + "'processed alongside the samples'",
 "Analytical Accuracy and Assessment Method": "N" + D + "BHVO2 and DTS-2b results are in Supplementary Dataset 2",
}
# ---- c12_broussard
D = " — "
COL12 = {  # Broussard et al. 2026 (Meteoritics & Planetary Science), Neptune Plus at WUSTL. Read 2026-09-30: Bulk chemistry analysis (digestion), Potassium isotope analysis.
 "Target Material": "CI chondrite" + D + "Oued Chebeika 002 (LAB24-2 fragments A and B); BHVO-2 is the geostandard",
 "Sample Preparation Method": "Two fragments (39.49 mg and 48.34 mg) digested; ~7 mg of sample from the digest solutions taken for K" + D + "Bulk chemistry analysis; Potassium isotope analysis",
 "Digestion Step": ("HF–HNO3 attack (3:2 concentrated HF : double-distilled HNO3 in PFA vials, hotplate, 150 °C, ~1 week); H2O2 step (dried under a heat lamp, 1 mL concentrated HNO3 with 1 mL H2O2 added in 0.1 mL increments); "
                    "HCl step (dried, dissolved in double-distilled HCl); final uptake (dried, 5 mL 2% HNO3)" + D + "after Lauretta et al. (2024)"),
 "Digestion Acid(s)": "HF–HNO3 attack: 3:2 HF : HNO3; H2O2 step: concentrated HNO3 + H2O2; HCl step: HCl; final uptake: 2% HNO3",
 "Digestion Temperature": "HF–HNO3 attack: 150 °C; other: N",
 "Digestion Duration": "HF–HNO3 attack: ~1 week; other: N",
 "Digestion Vessel Type": "PFA vials",
 "Sample Aliquot Mass or Volume": "~7 mg of sample" + D + "from the OC002A and OC002B solutions",
 "Final Solution Matrix": "all: 300 ppb K" + D + "the acid is not stated",
 "Desolvation System": "all: Elemental Scientific APEX Omega" + D + "'to improve sensitivity and minimize the generation of hydrides'",
 "Nebulizer Type": "N" + D + "introduction through an Elemental Scientific APEX Omega desolvating nebulizer",
 "Target Species": "K",
 "Monitored Masses": "39K, 41K → K" + D + "δ⁴¹K from ⁴¹K/³⁹K",
 "Reported Variables and Units": "δ41K" + D + "‰ relative to NIST SRM 3141a",
 "Number of Cycles per Block": "N" + D + "'Each sample was measured approximately 20 times'",
 "Isotope Ratio Reported": "δ41K: 41K/39K",
 "delta or epsilon Value Reference Standard": "K: NIST SRM 3141a",
 "Interfering Species": "41K: 40Ar1H+; other: N",
 "Interference Correction Method": "41K: resolved by measuring on the left shoulder of the peak; other: N",
 "Uncertainty Level": "N" + D + "± values on δ⁴¹K without a stated convention",
 "Combination Method": "δ41K: average of approximately 20 repeat measurements" + D + "'The average d41K value for BHVO-2 was −0.448 ± 0.027‰'",
 "Primary Calibration Standard Name": "all [K: NIST SRM 3141a]",
 "Analytical Accuracy and Assessment Method": "BHVO-2 [δ41K: −0.448 ± 0.027‰, within error of reported values such as −0.46 ± 0.09‰ (Wang et al. 2021)]",
}
# ---- c1314_barnes
D = " — "
BDIG = ("HF–HNO3 attack (concentrated HF and HNO3 3:1, closed beaker, 170 °C, 48 h); HNO3–HCl flux (concentrated HNO3 and HCl, 1 ml H2O2 added slowly during the HNO3 flux to remove organics); "
        "final uptake (5 ml 0.5 M HNO3)")
BACID = "HF–HNO3 attack: 3:1 concentrated HF : HNO3; HNO3–HCl flux: concentrated HNO3 and HCl, with H2O2; final uptake: 0.5 M HNO3"
COORD = "coordinated dissolution of an ~20.66 mg split (OREX-803015-0) at WUSTL"
COL13 = {  # Barnes et al. 2025 (Nature Astronomy 9) — WUSTL Neptune Plus, K, Cu, Zn. Read 2026-09-30: Analytical techniques (coordinated dissolution, K/Cu/Zn).
 "Target Material": "returned asteroid sample" + D + "Bennu aggregate OREX-803015",
 "Sample Preparation Method": "One digest split two ways: about half at WUSTL for K, Cu and Zn, half to LLNL and on to ETH Zurich" + D + COORD,
 "Digestion Step": BDIG + D + COORD,
 "Digestion Acid(s)": BACID,
 "Digestion Temperature": "HF–HNO3 attack: 170 °C; other: N",
 "Digestion Duration": "HF–HNO3 attack: 48 h; other: N",
 "Digestion Vessel Type": "Closed beaker",
 "Sample Aliquot Mass or Volume": "~20.66 mg split, about half used at WUSTL",
 "Chromatographic Separation Applied": "Yes, K: triple-pass AG50W-X8 cation exchange; Cu and Zn: AG1-X8 anion exchange (Cu in 22 ml 6 M HCl, Zn in 10 ml 3 M HNO3), with a second pass for Cu and an HBr–HNO3 AG1-X8 step for Zn",
 "Acquisition Pass": "K; Cu; Zn" + D + "K in dry plasma with high mass resolution, Cu and Zn in wet plasma with low resolution",
 "Number of Acquisition Passes": "3",
 "Final Solution Matrix": "K: 200 ppb; Cu: 100 ppb; Zn: 200 ppb" + D + "samples and standards; the acid is not stated",
 "Mass Resolution Setting": "High-mass-resolution slit for K, low-mass-resolution slit for Cu and Zn",
 "Mass Resolution Assignment": "K: high resolution; Cu: low resolution; Zn: low resolution",
 "Spray Chamber Type and Cooling Temperature": "Quartz glass dual cyclonic spray chamber, for Cu and Zn",
 "Desolvation System": "K: Elemental Scientific APEX Ω; Cu: none; Zn: none",
 "Plasma Thermal Mode": "K: dry plasma; Cu: wet plasma; Zn: wet plasma" + D + "'To lower the ArH+ peak and significantly increase the K signal intensity'",
 "Target Species": "K, Cu, Zn",
 "Monitored Masses": "39K, 41K → K; 63Cu, 65Cu → Cu; 64Zn, 66Zn → Zn" + D + "the ratios of the δ definitions",
 "Reported Variables and Units": "δ41K, δ65Cu, δ66Zn" + D + "‰ relative to the bracketing standards",
 "Isotope Ratio Reported": "δ41K: 41K/39K; δ65Cu: 65Cu/63Cu; δ66Zn: 66Zn/64Zn",
 "delta or epsilon Value Reference Standard": "K: NIST-SRM 3141a; Cu: NIST-SRM 976; Zn: JMC-Lyon",
 "Calibration Strategy per Target Species": "K: bracketing against NIST-SRM 3141a; Cu: bracketing against NIST-SRM 976; Zn: bracketing against JMC-Lyon",
 "Spectral Interference Corrections Applied": "N" + D + "ArH⁺ on K lowered by dry plasma and a high-resolution slit, not corrected",
 "Interfering Species": "41K: ArH+; other: N" + D + "'To lower the ArH+ peak'",
 "Interference Correction Method": "41K: lowered by dry plasma and the high-mass-resolution slit; other: N",
 "Uncertainty Level": "2 s.d." + D + "Bennu values carry 2 s.e. in the main text",
 "Primary Calibration Standard Name": "all [K: NIST-SRM 3141a; Cu: NIST-SRM 976; Zn: JMC-Lyon]",
 "Analytical Accuracy and Assessment Method": "N" + D + "'the geostandard BHVO-2 was analysed alongside all sample analyses'; results in Supplementary Table 9",
}
COL14 = {  # Barnes et al. 2025 — ETH Zurich Neptune Plus, Ti. Read 2026-09-30: Analytical techniques (coordinated dissolution; Bulk Ti isotopes, ETH Zurich).
 "Target Material": "returned asteroid sample" + D + "Bennu aggregate OREX-803015-100",
 "Sample Preparation Method": "A 5.2 mg aliquot of the coordinated digest (OREX-803015-100), sent from WUSTL via LLNL" + D + COORD,
 "Digestion Step": BDIG + D + COORD,
 "Digestion Acid(s)": BACID,
 "Digestion Temperature": "HF–HNO3 attack: 170 °C; other: N",
 "Digestion Duration": "HF–HNO3 attack: 48 h; other: N",
 "Digestion Vessel Type": "Closed beaker",
 "Chromatographic Separation Applied": "Yes, three-step anion exchange chromatography after ref. 71; yields 75–100%",
 "Acquisition Pass": "configuration 1; configuration 2" + D + "'Titanium isotopes were collected in two cup configurations'",
 "Number of Acquisition Passes": "2",
 "Monitored Masses": "46Ti, 47Ti, 48Ti, 49Ti, 50Ti → Ti; 44Ca, 51V, 52Cr, 53Cr → none" + D + "⁴⁴Ca in configuration 1; ⁵¹V, ⁵²Cr, ⁵³Cr in configuration 2",
 "Reported Variables and Units": "ε46Ti, ε48Ti, ε50Ti" + D + "parts per 10⁴ relative to an in-house Alfa Aesar Ti wire standard",
 "Collector Configuration": "46Ti, 47Ti, 48Ti, 44Ca: configuration 1; 51V, 52Cr, 53Cr: configuration 2; 49Ti, 50Ti: both configurations" + D + "cup positions not stated",
 "Number of Cycles per Block": "all: 40 cycles",
 "Integration Time per Cycle": "46Ti, 47Ti, 48Ti, 44Ca: 8.39 s; 51V, 52Cr, 53Cr: 4.19 s; 49Ti, 50Ti: 8.39 s (configuration 1), 4.19 s (configuration 2)",
 "Faraday Cup Amplifier Resistor Values": "48Ti: 10^11 Ω; other: N" + D + "'a signal of around 40 V over a 10^11-Ω resistor on 48Ti'",
 "Instrument Sensitivity": "48Ti: ~40 V" + D + "about 0.3 µg Ti consumed per measurement",
 "Mass Bias Correction Strategy": "Internal normalisation to 49Ti/47Ti = 0.749766 with the exponential law, reported relative to the bracketing in-house Alfa Aesar Ti wire standard",
 "Mass Fractionation Law": "Exponential law",
 "Internal Normalization Element and Isotope Ratio": "49Ti/47Ti = 0.749766" + D + "ref. 72",
 "Isotope Ratio Reported": "ε46Ti: 46Ti/47Ti; ε48Ti: 48Ti/47Ti; ε50Ti: 50Ti/47Ti",
 "delta or epsilon Value Reference Standard": "Ti: in-house Alfa Aesar Ti wire standard",
 "Interfering Species": "46Ti, 48Ti: Ca; 50Ti: V and Cr; other: N",
 "Interference Correction Method": "46Ti, 48Ti: corrected from 44Ca; 50Ti: corrected from 51V, 52Cr and 53Cr; other: N",
 "Procedural Blank Level": "Ti: 3.7 ng" + D + "a maximum blank contribution of 0.18%",
 "Primary Calibration Standard Name": "all [Ti: in-house Alfa Aesar Ti wire standard]",
 "Secondary Reference Materials": "BHVO-2, Agua Zarcas" + D + "Agua Zarcas is a CM2 chondrite",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "BHVO-2 [ε46Ti: ±0.17; ε48Ti: ±0.09; ε50Ti: ±0.16]" + D + "2 s.d. of 9 analyses",
 "Analytical Accuracy and Assessment Method": "BHVO-2, Agua Zarcas [all: analysed alongside Bennu to verify accuracy and reproducibility]",
 "Combination Method": "all: average of four repetitions over two days" + D + "Bennu +0.27 ± 0.08 ε⁴⁶Ti, −0.02 ± 0.05 ε⁴⁸Ti, +1.98 ± 0.08 ε⁵⁰Ti (2 s.e.)",
}
# ---- engine
COLS = [  # column number -> label substring
 (1, "Budde+etal2016", COL1), (2, "Craddock+etal2008", COL2), (3, "Hopp+etal2021", COL3), (4, "Hu+etal2022", COL4),
 (5, "IbanezMejia+Tissot2020", COL5), (6, "Nie+Dauphas2019", COL6), (7, "Nowell+etal2008 | Neptune", COL7),
 (8, "Nowell+etal2008 | Nu Plasma", COL8), (9, "Pringle+Moynier2017", COL9), (10, "Schönbächler+etal2025", COL10),
 (11, "vanKooten+etal2026", COL11), (12, "Broussard+etal2026", COL12), (13, "Barnes+etal2025 | Neptune Plus | WUSTL", COL13),
 (14, "Barnes+etal2025 | Neptune Plus | ETH", COL14),
]
UPB_ONLY = []  # no U-Pb twin
NODATE = "N — the procedure reports no date"
TAPPS = ["Solution_MC-ICP-MS_TAPP_v"]


def clean(v):
    v = re.sub(r"\s*\[P[0-9][^\]]*\]", "", v)
    v = re.sub(r"\s*\[P20-Ack\]", "", v)
    m = re.match(r"^(N/A|N)\s*\((.*)\)\s*$", v, re.S)
    if m:
        v = "%s — %s" % (m.group(1), m.group(2))
    v = re.sub(r"^(Yes|Y) — ", r"\1, ", v)  # the detail of a yes is the value, not commentary
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
