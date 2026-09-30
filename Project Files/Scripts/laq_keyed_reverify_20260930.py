#!/usr/bin/env python3
"""LA-Q-ICP-MS and its U-Pb twin: keyed notation, with every procedure-level cell re-read (2026-09-30).

    python3 "Project Files/Scripts/laq_keyed_reverify_20260930.py" [--apply] [--out-sim DIR]

The user's requirement for this conversion: the literature cells must be enough to regenerate each paper's
procedure. So this is not a reformatting pass. Each of LA-Q's seven procedure columns was re-read against
its paper (methods, instrument tables, table notes, acknowledgements), and every procedure-level cell was
checked, keyed or not. The result is scored by
`Project Files/Reports/LAQ_Cells_RoundTrip_2026-09-30/roundtrip.py`.

The U-Pb twin carries the first six columns with identical cells, so the same edits apply; its nine
geochronology fields, never assessed, become `N — the procedure reports no date`.

What the re-read found, beyond format (details per column in the dicts below):
  * isotopes recorded as target species (Nakanishi, Liu+2024 — including a nonexistent '²¹Sc'), with
    `Monitored Masses` left `N` where the paper lists the masses;
  * inferences written as fact: exclusion of inclusion-bearing analyses, gas blanks "before each spot",
    "fs laser reduces LIEF" for a nanosecond excimer (Liu+2025), "~40 s (inferred from typical protocol)",
    "unit resolution implied", "in-house reduction implied", "background subtracted";
  * another paper's result: Liu+2025's accuracy cell cited Liu+2024's SN-ICP-MS comparison;
  * stated facts missing: Nakanishi's Ar carrier, torch and auxiliary flow; Liu+2025's second laboratory
    and its Si/Fe internal standards; Wu+2023's Ar carrier (0.65 L/min), spot sizes, ARM-1 and the
    Rösel and Zack uncertainty workflow (the cell credited IsoplotR); Liu+2016's per-element LODs;
  * study-level grants recorded as procedure-development funding (the 2026-09-29 rule moves them).

Mechanical clean-ups on every remaining cell of the pass: page tags such as "[P4]" are dropped, and
"N (reason)" / "N/A (reason)" become "N — reason" / "N/A — reason", so they parse as markers.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
# ---- c1_nakanishi
D = " — "
T1 = "Table 1"
COL1 = {  # Nakanishi et al. 2022 (GCA 319), fs-LA-Q-ICP-MS, Tokyo Tech. Read 2026-09-30: §2.1, §2.3, Table 1, §3.2, Table 3, acknowledgements.
 "Funding Source for Procedure Development": "N" + D + "the JSPS Grants-in-Aid support the study as a whole and are recorded under Funding Source for Analysis",
 "Target Material": "CR chondrite metal" + D + "interior, margin and isolated metal grains (p.1); the IVB iron meteorites are the standards",
 "Sample Preparation Method": "Thick sections embedded in petropoxy 154 resin, the surface finalised by polishing with 0.5 µm diamond paste; carbon-coated before the EPMA measurements (§2.1–2.2). Whether the coat was removed before ablation is not stated; the later 0.5 µm polish (§2.5) preceded micromilling, not ablation",
 "Data Processing Software(s)": "N",
 "Mass Resolution Setting": "N",
 "Torch Type": "Quartz torch with quartz injector" + D + T1,
 "Carrier Gas and Flow Rate": "Ar, 0.6 L/min" + D + "Table 1, under 'Ar gas flow rate': 'Carrier gas 0.6 L/min'",
 "Make-up Gas and Flow Rate": "Ar, 0.9–1.2 L/min" + D + "Table 1, 'Make-up gas'",
 "Coolant (Plasma) Gas Flow Rate": "Ar, plasma gas 16 L/min; cool gas 12–13 L/min" + D + "Table 1 lists both rows under 'Ar gas flow rate'",
 "Auxiliary Gas Flow Rate": "Ar, 0.6–1.2 L/min" + D + "Table 1, 'Auxiliary'",
 "Interface Cone Configuration": "Nickel micro-skimmer cone, Xs; nickel sampler cone" + D + T1,
 "Laser Spot Geometry": "all: 30 µm diameter" + D + "'Each spot analysis on the sample produced a pit of 30 µm in diameter' (p.3)",
 "Laser Spot Path / Ablation Mode": "all: Spot" + D + "'ablated by a spot analysis mode' (p.3)",
 "Laser Repetition Rate": "all: 20 Hz",
 "Analysis Sequence": "N" + D + "Warburton Range and Tawallah Valley 'were used as an external standard and a secondary standard, respectively' (p.3); the order of analyses is not described",
 "Target Species": "Co, Ru, Rh, Pd, Re, Os, Ir, Pt, Au" + D + "'The abundances of HSEs were determined with the calibration curve method by measuring isotopes of 59Co, 101Ru, 103Rh, 105Pd, 185Re, 189Os, 193Ir, 195Pt, and 197Au' (p.3). Ni is the internal standard, its concentration from EPMA",
 "Monitored Masses": "⁵⁹Co → Co; ¹⁰¹Ru → Ru; ¹⁰³Rh → Rh; ¹⁰⁵Pd → Pd; ¹⁸⁵Re → Re; ¹⁸⁹Os → Os; ¹⁹³Ir → Ir; ¹⁹⁵Pt → Pt; ¹⁹⁷Au → Au; ⁶¹Ni, ²⁴Mg, ²⁹Si, ³¹P, ³³S → none" + D + "Table 1 'Measured isotopes' and 'Monitored isotopes'; ⁶¹Ni 'was monitored for internal standardization', and Mg, Si, P and S 'to check the involvement of micro-inclusions' (p.3)",
 "Reported Variables and Units": "Ru, Rh, Pd, Re, Os, Ir, Pt, Au (ppm); HSE/Ir ratios; Re/Os abundance ratio" + D + "HSE abundances in metal, e.g. 'Ir abundance ranging from 1.08 to 2.53 ppm' (p.5), with major element abundances from EPMA alongside; the Re/Os abundance ratio feeds the reported 187Re/188Os, 'determined by the mean Re/Os abundance ratios for each of the 1–3 analytical spots measured by LA-ICP-MS' (Table 3, p.8)",
 "Inter-Pass Data Dependency": "N/A" + D + "a single acquisition pass",
 "Number of Replicates": "1–3 spots per metal grain" + D + "'the mean Re/Os abundance ratios for each of the 1–3 analytical spots' (Table 3)",
 "Internal Standard Approach": "all: single element, its concentration measured by EPMA at the ablated spot" + D + "'61Ni was monitored for internal standardization. The concentration of Ni in the ablated spot was obtained by EPMA' (p.3)",
 "Internal Standard Element": "all: Ni (⁶¹Ni)" + D + "concentration from EPMA at the ablated spot (p.3)",
 "Elemental Fractionation Correction": "N" + D + "quantification is by 'the calibration curve method' against Warburton Range with ⁶¹Ni internal standardization (p.3); no fractionation correction as such is described",
 "Uncertainty Propagation Method": "N" + D + "'Analytical uncertainties accompanied with the data are 2SE of individual measurements' (p.4); how they are propagated is not described",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "N" + D + "the paper says only that 'the intensities of individual isotopes rapidly increased to the maximum and decayed to the background level immediately after the end of ablation' (p.3)",
 "Spike / Outlier Filtering Approach": "N" + D + "²⁴Mg, ²⁹Si, ³¹P and ³³S 'were simultaneously monitored to check the involvement of micro-inclusions' (p.3); what was done with an affected analysis is not stated",
 "Blank / Background Correction Method": "N" + D + "the signal 'decayed to the background level immediately after the end of ablation' (p.3); the background correction is not described",
 "Pulse/Analog Detector Nonlinearity Correction": "N",
 "Spectral Interference Corrections Applied": "N",
 "Interfering Species": "N" + D + "²⁴Mg, ²⁹Si, ³¹P and ³³S monitor micro-inclusions, not spectral interferences",
 "Interference Correction Method": "N",
 "Memory Effect Mitigation": "N",
 "Normalization / Standards-Based Correction": "N" + D + "quantification is by 'the calibration curve method' against Warburton Range (p.3)",
 "Primary Calibration Standard Name": "all [Co, Ru, Rh, Pd, Re, Os, Ir, Pt, Au: Warburton Range (IVB iron meteorite)]" + D + "'used as an external standard' with HSE abundances 'given by Walker et al. (2008)'; the calibration curve method (p.3)",
 "Secondary Reference Materials": "Tawallah Valley (IVB iron meteorite)" + D + "'used as ... a secondary standard' (p.3), its HSE abundances from Walker et al. (2008)",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "all: 2SE of individual measurements" + D + "'Analytical uncertainties accompanied with the data are 2SE of individual measurements' (p.4)",
 "Within-Session Analytical Precision and Assessment Method": "N" + D + "the 2SE is stated for individual measurements (p.4), not for a standard",
 "Analytical Accuracy and Assessment Method": "N",
 "Additional Notes": "N",
}
FACTS1 = [
 ("Instrument Model", None, ["X-series 2"]), ("Laser Manufacturer & Model", None, ["IFRIT"]),
 ("Laser Wavelength and Type", None, ["260 nm"]), ("Laser Pulse Duration", None, ["220 fs"]),
 ("Laser Fluence (Energy Density)", None, ["12 J"]), ("Laser Repetition Rate", "all", ["20 Hz"]),
 ("Laser Spot Geometry", "all", ["30 µm"]), ("Laser Spot Path / Ablation Mode", "all", ["Spot"]),
 ("RF Power", None, ["1400 W"]), ("Carrier Gas and Flow Rate", None, ["0.6 L/min"]),
 ("Make-up Gas and Flow Rate", None, ["0.9–1.2"]), ("Auxiliary Gas Flow Rate", None, ["0.6–1.2"]),
 ("Coolant (Plasma) Gas Flow Rate", None, ["16 L/min"]), ("Coolant (Plasma) Gas Flow Rate", None, ["12–13"]),
 ("Interface Cone Configuration", None, ["micro-skimmer"]), ("Torch Type", None, ["quartz injector"]),
 ("Internal Standard Element", "all", ["Ni"]), ("Internal Standard Approach", "all", ["EPMA"]),
 ("Primary Calibration Standard Name", "all/Ir", ["Warburton Range"]), ("Primary Calibration Standard Name", "all/Re", ["Warburton Range"]),
 ("Secondary Reference Materials", None, ["Tawallah Valley"]),
 ("Internal (Within-Measurement) Analytical Precision and Assessment Method", "all", ["2SE"]),
 ("Combination Method", "Re/Os abundance ratio", ["mean"]),
] + [("Monitored Masses", m, [m]) for m in ("⁵⁹Co", "¹⁰¹Ru", "¹⁰³Rh", "¹⁰⁵Pd", "¹⁸⁵Re", "¹⁸⁹Os", "¹⁹³Ir", "¹⁹⁵Pt", "¹⁹⁷Au", "⁶¹Ni", "²⁴Mg", "²⁹Si", "³¹P", "³³S")] \
  + [("Target Species", m, [m]) for m in ("Co", "Ru", "Rh", "Pd", "Re", "Os", "Ir", "Pt", "Au")]

# ---- c2_liu2024
D = " — "
EL32 = "Sc, V, Cr, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Ba, La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, Th, U"
GRM = "AC-E, GSR-1, JB-1b, GSR-3, AGV-2, W-2A"
COL2 = {  # Liu et al. 2024 (JAAS 39, 2728), fs-LA-Q-ICP-MS, IGGCAS. Read 2026-09-30: §2.1–2.3, Table 1, §3.1–3.5, Table 2, acknowledgements.
 "Funding Source for Procedure Development": "N" + D + "the CAS Strategy Priority Research Program and NSFC grant support the study as a whole and are recorded under Funding Source for Analysis",
 "Sample Preparation Method": "Li2B4O7 flux (350.0 ± 0.3 mg) and powdered sample (10.00 ± 0.03 mg) weighed into a small Pt–Au crucible, mixed with a glass rod, NH4Br solution added as a releasing agent, and fused into a mini glass disk on an M4 automatic fluxer; the disk measured for major elements by WD-XRF, then its surface cleaned with ethanol before fs-LA-ICP-MS (§2.3)",
 "Mass Resolution Setting": "N",
 "Detector Configuration": "Dual" + D + "Table 1 'Detector mode: Dual'",
 "Laser Spot Geometry": "all: 100 µm" + D + "'100 µm-diameter ablating spots' (§2.2); Table 1 gives 'Ablation spot size 100 × 100 µm'",
 "Laser Spot Path / Ablation Mode": "all: Single spot" + D + "Table 1 'Ablation mode'",
 "Laser Repetition Rate": "all: 1 Hz",
 "Laser Pulse Duration": "N" + D + "'femtosecond'; the laser's details are in Table S1, not in the archived PDF",
 "Carrier Gas and Flow Rate": "He: chamber gas 0.7 L/min; cup gas 0.1 L/min" + D + "Table 1",
 "Make-up Gas and Flow Rate": "N",
 "Coolant (Plasma) Gas Flow Rate": "15 L/min" + D + "Table 1 'Plasma gas flow'",
 "Auxiliary Gas Flow Rate": "0.85 L/min" + D + "Table 1 'Auxiliary gas flow'",
 "ICP Tuning": "Gas flows optimised by spot ablation of NIST SRM 612 'to obtain maximum signal intensities while maintaining ThO/Th at <0.3% and U/Th at 0.95–1.05' (§2.2); sampling depth 8 mm (Table 1)",
 "Analysis Sequence": "Per spot: 25 s gas blank, 45 s ablation, 25 s washout between analyses (§2.2); the order of standards and unknowns is not described",
 "Target Species": EL32 + D + "the 32 trace elements of Table 2 and §3.1",
 "Monitored Masses": "N" + D + "the isotopes measured are not stated in the paper",
 "Reported Variables and Units": EL32 + D + "concentrations reported as 'Mean' with a '95% CI' per sample (Table 2), which gives no unit; the LODs are in µg g⁻¹ (§3.2). Relative standard deviations are the precision measure (§3.5)",
 "Dwell Time per Mass": "all: 30 ms/10 ms" + D + "Table 1 'Dwell time per isotope'; which isotopes take which is not stated",
 "Inter-Pass Data Dependency": "N/A" + D + "a single acquisition pass",
 "Number of Replicates": "9 spots per glass disk" + D + "'Nine spot analyses (spot size = 100 µm) were arranged in a grid pattern to cover the entire glass' (§3.1); Table 2 'n = 9 spots'",
 "Internal Standard Approach": "all: two internal standard elements, chosen per target element" + D + "Si for Co, Ni, Cu and Zn, and Al for the others, after comparing Si, Ca and Al on GSR-3 (§3.3); the disks were 'initially measured for major elements by WD-XRF' (§2.3)",
 "Internal Standard Element": "all: Si (for Co, Ni, Cu, Zn), Al (for the other trace elements)" + D + "§3.3",
 "Elemental Fractionation Correction": "N" + D + "the paper states that fs lasers 'are considered stoichiometric erosion processes without any element or isotope fractionation effects' (§3.4); no correction is described",
 "Uncertainty Propagation Method": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "N",
 "Signal Integration Time": "N" + D + "ablation lasted 45 s (§2.2); the integration interval is not stated",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "25 s gas blank before each ablation; flux procedure-blank contributions deducted for V, Co, Zn, Ba, La, Ce, Ta and U" + D + "'after measuring a gas blank for 25 s' (§2.2); 'All results of the eight pollution elements above have deducted the flux blank contributions' (§3.2)",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "Table 1 gives 'Detector mode: Dual'; a cross-calibration is not described",
 "Spectral Interference Corrections Applied": "N",
 "Interfering Species": "N" + D + "the flux-blank elements (V, Co, Zn, Ba, La, Ce, Ta, U) are a blank contribution, recorded under Blank / Background Correction Method",
 "Interference Correction Method": "N",
 "Memory Effect Mitigation": "25 s washout between analyses" + D + "§2.2",
 "Normalization / Standards-Based Correction": "N",
 "Primary Calibration Standard Name": "all [all: NIST SRM 612 and NIST SRM 614]" + D + "non-matrix-matched external standards; matrix-matched BHVO-2 borate glass was tested and gave poorer results (§3.4)",
 "Calibration Standard Measurement Frequency": "N",
 "Secondary Reference Materials": GRM + D + "six silicate rock GRMs prepared as lithium borate glasses and 'analyzed to evaluate the performance of the proposed method' (§2.1); reference values from GeoReM (§3.5). The meteorites NWA13190 and NWA14526 are samples, compared with solution ICP-MS",
 "Detection Limit": "all: 0.005–23.5 µg g⁻¹" + D + "LODs of 32 elements in lithium borate glass BHVO-2 (Table S2); 0.007–0.45 µg g⁻¹ calculated for NIST 610 (§3.2)",
 "Detection Limit Method": "all: Pettke (2012)" + D + "§3.2",
 "Limit of Quantification (LOQ) Method": "V, Co, Zn, Ba, La, Ce, Ta, U: blank value + 10SD (IUPAC Gold Book); other: 3.3 × LOD" + D + "§3.2",
 "Within-Session Analytical Precision and Assessment Method": GRM + " [all: RSD better than 10% for most elements]" + D + "§3.5, Fig. 5b; higher RSDs for Zn in GSR-1, Tm, Yb and Lu in GSR-3, Lu in AGV-2, and Ta and U in W-2A",
 "Analytical Accuracy and Assessment Method": GRM + " [all: within 10% of the GeoReM reference values for most trace elements]" + D + "§3.5, Fig. 5a; discrepancies >15% for Co in AGV-2, JB-1b and W-2A, Ni in JB-1b, Cu in AGV-2 and JB-1b, Zn and Hf in GSR-1",
 "Additional Notes": "N",
}
FACTS2 = [
 ("Instrument Model", None, ["8900"]), ("Laser Manufacturer & Model", None, ["GenesisGEO"]),
 ("Laser Wavelength and Type", None, ["343 nm"]), ("Laser Fluence (Energy Density)", None, ["6.79"]),
 ("Laser Spot Geometry", "all", ["100 µm"]), ("Laser Repetition Rate", "all", ["1 Hz"]),
 ("Laser Spot Path / Ablation Mode", "all", ["single spot"]), ("Ablation Duration per Spot", None, ["45 s"]),
 ("Background Count Time", None, ["25 s"]), ("Memory Effect Mitigation", None, ["25 s washout"]),
 ("RF Power", None, ["1550 W"]), ("Coolant (Plasma) Gas Flow Rate", None, ["15 L"]), ("Auxiliary Gas Flow Rate", None, ["0.85"]),
 ("Carrier Gas and Flow Rate", None, ["0.7 L"]), ("Carrier Gas and Flow Rate", None, ["0.1 L"]),
 ("Dwell Time per Mass", "all", ["30 ms/10 ms"]), ("Detector Configuration", None, ["Dual"]),
 ("Oxide Production Method and Threshold", None, ["<0.3%"]), ("Data Processing Software(s)", None, ["Iolite"]),
 ("Internal Standard Element", "all", ["Si (for Co, Ni, Cu, Zn)"]), ("Internal Standard Element", "all", ["Al (for the other"]),
 ("Primary Calibration Standard Name", "all/all", ["NIST SRM 612 and NIST SRM 614"]),
 ("Fusion Flux and Dilution Ratio", None, ["Li"]),
 ("Detection Limit Method", "all", ["Pettke"]), ("Limit of Quantification (LOQ) Method", "U", ["10SD"]),
 ("Limit of Quantification (LOQ) Method", "Sc", ["3.3 × LOD"]),
 ("Combination Method", "Sc", ["mean of n = 9"]), ("Other Statistics", "U", ["95% confidence"]),
] + [("Secondary Reference Materials", m, [m]) for m in ("AC-E", "GSR-1", "JB-1b", "GSR-3", "AGV-2", "W-2A")] \
  + [("Target Species", m, [m]) for m in ("Sc", "Ni", "La", "Lu", "U")] \
  + [("Analytical Accuracy and Assessment Method", "%s/Sc" % m, ["within 10%"]) for m in ("AC-E", "W-2A")]

# ---- c34_liu2025
D = " — "
LA = "§2.2.2"
_SHARED = {  # Liu et al. 2025 (GCA 393, 170). Read 2026-09-30: §2.1 end, §2.2.1–2.2.2, Fig. 1, Table 1 notes, acknowledgements.
 "Funding Source for Procedure Development": "N" + D + "the CAS Strategic Priority Research Program and NSFC grants support the study as a whole and are recorded under Funding Source for Analysis",
 "Laboratory": "Guangzhou Institute of Geochemistry, CAS; Hefei University of Technology" + D + "LA-ICP-MS 'was employed at both the Guangzhou Institute of Geochemistry and Hefei University of Technology' (" + LA + ")",
 "Laser Manufacturer & Model": "Resonetic 193 nm ArF excimer laser; CetacAnalyte HE system" + D + LA,
 "Laser Wavelength and Type": "193 nm ArF excimer" + D + LA,
 "Mass Resolution Setting": "N",
 "Ablation Cell Type": "N" + D + "the paper names the 'CetacAnalyte HE system', not its cell",
 "Laser Repetition Rate": "all: 7 Hz" + D + "'operated at 7 Hz ablation frequency' (" + LA + ")",
 "Laser Pulse Duration": "N",
 "Ablation Duration per Spot": "N",
 "Carrier Gas and Flow Rate": "He; flow not stated" + D + "'Helium served as the carrier gas, to which nitrogen or argon gas was mixed for sensitivity optimization' (" + LA + ")",
 "Make-up Gas and Flow Rate": "N2 or Ar mixed into the He carrier; amounts not stated" + D + LA,
 "RF Power": "N", "Signal Smoothing": "N", "ICP Tuning": "N",
 "Analysis Sequence": "N" + D + "NIST 610 is the external standard and NIST 612 and BCR-2G the monitoring standards (" + LA + "); the sequence is not described",
 "Target Species": "Au, Cu" + D + "'to determine the Au and Cu contents of the quenched run products' (" + LA + ")",
 "Monitored Masses": "N" + D + "the isotopes measured are not stated",
 "Background Count Time": "N",
 "Inter-Pass Data Dependency": "N/A" + D + "a single acquisition pass",
 "Number of Replicates": "N",
 "Internal Standard Approach": "all: an element measured by EMP" + D + "'with Si and Fe obtained from EMP analyses as the internal standards' (" + LA + "); which element serves the glass and which the sulfide is not stated",
 "Internal Standard Element": "all: Si, Fe" + D + "'Si and Fe obtained from EMP analyses as the internal standards' (" + LA + "); the assignment to glass or sulfide is not stated",
 "Elemental Fractionation Correction": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "N",
 "Signal Integration Time": "N",
 "Spike / Outlier Filtering Approach": "Au micronugget spikes identified in the time-resolved signal and removed, or the analysis not considered" + D + "'only analyses free from micronuggets or where the spikes from the micronuggets could be easily removed were considered (Fig. 1)' (" + LA + ")",
 "Blank / Background Correction Method": "N",
 "Spectral Interference Corrections Applied": "N",
 "Normalization / Standards-Based Correction": "N",
 "Primary Calibration Standard Name": "all [Au, Cu: NIST 610]" + D + "'Calibration employed NIST 610 as an external standard' (" + LA + ")",
 "Calibration Standard Measurement Frequency": "N",
 "Secondary Reference Materials": "NIST 612; BCR-2G" + D + "'NIST 612 and BCR-2G as monitoring standards' (" + LA + ")",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Analytical Accuracy and Assessment Method": "N" + D + "data from the two laboratories 'exhibited good agreement, any differences being below 10 %' (" + LA + ")",
}
COL3 = dict(_SHARED, **{  # silicate glass
 "Target Material": "experimental dacitic silicate glass" + D + "quench product",
 "Sample Preparation Method": "Recovered capsules longitudinally sectioned with a wire saw, and one half mounted in epoxy resin (§2.1)",
 "Laser Spot Geometry": "all: 40 µm beam diameter" + D + "'a 40 μm beam diameter for glasses' (" + LA + ")",
 "Reported Variables and Units": "Au (ppm); Cu (ppm)" + D + "Au and Cu contents of the quenched silicate melt, per run (Table 1, p.3); S and H2O come from other methods, and the derived quantity reported is the sulfide/melt partition coefficient DAu (dimensionless, p.2)",
 "Detection Limit": "Au: ~0.01 ppm; Cu: ~0.1 ppm" + D + "'Detection limits for Au and Cu in silicate melts were ~ 0.01 ppm and ~ 0.1 ppm, respectively' (" + LA + ")",
 "Additional Notes": "Run products of 1.0 GPa piston-cylinder experiments, analysed at two laboratories whose data 'exhibited good agreement, any differences being below 10 %' (" + LA + ")",
})
COL4 = dict(_SHARED, **{  # sulfide
 "Target Material": "experimental sulfide" + D + "quench product; pyrrhotite ('po') in the Table 1 notes",
 "Sample Preparation Method": "Recovered capsules longitudinally sectioned with a wire saw, and one half mounted in epoxy resin (§2.1)",
 "Laser Spot Geometry": "all: 20 µm beam diameter" + D + "'20 μm for sulfides, selecting grain sizes larger than 20 µm for the latter' (" + LA + ")",
 "Sampling Unit Selection Criteria": "Sulfide grains larger than 20 µm, wider than the beam" + D + "'20 μm for sulfides, selecting grain sizes larger than 20 µm for the latter' (" + LA + ")",
 "Reported Variables and Units": "Au (ppm); Cu (ppm)" + D + "Au and Cu contents of the quenched sulfide per run (Table 1, p.3), which with the coexisting glass give the sulfide/melt partition coefficient DAu (dimensionless, p.2)",
 "Detection Limit": "N" + D + "detection limits are stated for silicate melts only (" + LA + ")",
 "Additional Notes": "Run products of 1.0 GPa piston-cylinder experiments, analysed at two laboratories whose data 'exhibited good agreement, any differences being below 10 %' (" + LA + ")",
})
_F = [
 ("Instrument Model", None, ["7900"]), ("Laser Manufacturer & Model", None, ["Resonetic"]),
 ("Laser Wavelength and Type", None, ["193 nm"]), ("Laser Fluence (Energy Density)", None, ["2.5"]),
 ("Laser Repetition Rate", "all", ["7 Hz"]), ("Carrier Gas and Flow Rate", None, ["He"]),
 ("Make-up Gas and Flow Rate", None, ["N2 or Ar"]), ("Laboratory", None, ["Hefei"]),
 ("Internal Standard Element", "all", ["Si, Fe"]), ("Internal Standard Approach", "all", ["EMP"]),
 ("Primary Calibration Standard Name", "all/Au", ["NIST 610"]), ("Primary Calibration Standard Name", "all/Cu", ["NIST 610"]),
 ("Secondary Reference Materials", "NIST 612", ["NIST 612"]), ("Secondary Reference Materials", "BCR-2G", ["BCR-2G"]),
 ("Spike / Outlier Filtering Approach", None, ["micronugget"]),
 ("Target Species", "Au", ["Au"]), ("Target Species", "Cu", ["Cu"]),
]
FACTS3 = _F + [("Laser Spot Geometry", "all", ["40 µm"]), ("Detection Limit", "Au", ["0.01 ppm"]), ("Detection Limit", "Cu", ["0.1 ppm"])]
FACTS4 = _F + [("Laser Spot Geometry", "all", ["20 µm"]), ("Sampling Unit Selection Criteria", None, ["larger than 20"])]

# ---- c56_liu2016
D = " — "
M = "Methods, p.4"
TABLE3_EL = "Li, Be, K, Sc, Ti, V, Cr, Mn, Co, Ni, Cu, Zn, Ga, Ge, Rb, Sr, Y, Zr, Nb, Ba, La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Au, Pb, Th, U"
REE = "La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu"
_SHARED = {  # Liu et al. 2016 (M&PS 51), LA-ICP-MS at Virginia Tech. Read 2026-09-30: Methods p.3–4, Table 3 and notes, results on merrillite.
 "Technique": "LA-ICP-MS" + D + "'an Agilent 7500ce inductively coupled plasma–mass spectrometer (ICP-MS), coupled with a GeoLasPro 193 nm Excimer laser-ablation (LA) system' (" + M + ")",
 "Procedure Reference(s)": "Udry et al. (2012); Pernet-Fisher et al. (2014)" + D + "'The analytical procedure is broadly similar to that of Udry et al. (2012) and Pernet-Fisher et al. (2014)' (" + M + ")",
 "Analyst": "N",
 "Funding Source for Analysis": "NASA Cosmochemistry NNX11AG58G and NNN13D465T; NSF EAR-1226270 and EAR-1019770" + D + "acknowledgements; Y.L. was also supported by the Jet Propulsion Laboratory",
 "Sample Preparation Method": "N" + D + "sections UT1 to UT3 (p.3); their preparation is not described",
 "Laser Manufacturer & Model": "GeoLasPro 193 nm Excimer laser-ablation system" + D + M,
 "ICP-MS Type": "N", "Mass Resolution Setting": "N",
 "Laser Fluence (Energy Density)": "7–10 J/m²" + D + "as written: 'a fluence rate of 7–10 J/m2 on the sample' (" + M + ")",
 "Laser Energy": "150 mJ output energy" + D + M,
 "Laser Pulse Duration": "N",
 "Laser Spot Path / Ablation Mode": "all: Spot" + D + "'The time-lapse plots of each spot were examined' (" + M + ")",
 "Laser Repetition Rate": "all: 5 Hz",
 "Plasma Thermal Mode": "N",
 "Analysis Sequence": "N" + D + "'A NIST 610 glass standard was analyzed before and after every session' (" + M + "); the order within a session is not described",
 "Calibration Standard Measurement Frequency": "Before and after every session" + D + "'A NIST 610 glass standard was analyzed before and after every session' (" + M + ")",
 "Dwell Time per Mass": "N",
 "Monitored Masses": "N" + D + "only ⁴⁰Ca is named, as the phosphate internal standard",
 "Background Count Time": "50 s" + D + "'The background was counted for 50 sec before each LA-ICP-MS analysis' (" + M + ")",
 "Inter-Pass Data Dependency": "N/A" + D + "a single acquisition pass",
 "Elemental Fractionation Correction": "N",
 "Uncertainty Propagation Method": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "Plateau region of each spot's time-lapse plot" + D + "'The time-lapse plots of each spot were examined, and only the plateau region was used to quantify the trace element abundances' (" + M + ")",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "N" + D + "the background 'was counted for 50 sec before each LA-ICP-MS analysis' (" + M + "); how it was subtracted is not described",
 "Pulse/Analog Detector Nonlinearity Correction": "N", "Interfering Species": "N", "Interference Correction Method": "N",
 "Primary Calibration Standard Name": "all [all: NIST 610]" + D + "'A NIST 610 glass standard was analyzed before and after every session' (" + M + ")",
 "Detection Limit Method": "all: 3σ of the background counts" + D + "Table 3 note d: 'LOD is the limit of detection estimated based on background counts to 3σ confidence interval'",
 "Limit of Quantification (LOQ) Method": "N",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "N",
}
COL5 = dict(_SHARED, **{  # silicates, oxides and glass
 "Coupling Description": "EMP gives major element compositions; for spots with EMP data, oxide-total normalization 'generally agrees within <10% with the method using EMP CaO or MgO values as internal standards'" + D + M,
 "Target Material": "silicates; oxides; glass" + D + "'For silicates and oxides ...'; '24 and 32 µm diameter were commonly used for silicates and glass' (" + M + "); Tissint martian meteorite",
 "Laser Spot Geometry": "all: 24 and 32 µm diameter, and 90 µm for a few olivine analyses" + D + "'24 and 32 µm diameter were commonly used for silicates and glass, and a few analyses were conducted on olivines using a 90 µm beam to evaluate whether the low signals of REEs are a result of insufficient sampling' (" + M + ")",
 "Target Species": TABLE3_EL + D + "the LA-ICP-MS elements of Table 3 (glasses); the methods do not list them",
 "Reported Variables and Units": TABLE3_EL.replace(", U", ", U (ppm)") + D + "trace element abundances in ppm, glass averages with 1σ and n in Table 3; mineral data in Table S1, not in the archived PDF",
 "Internal Standard Approach": "all: normalization to 100 wt% oxide total" + D + "'For silicates and oxides, trace element abundances were calculated by normalization to 100 wt% oxide total' (" + M + ")",
 "Internal Standard Element": "all: none" + D + "oxide-total normalization (" + M + ")",
 "Normalization / Standards-Based Correction": "all: normalization to 100 wt% oxide total" + D + M,
 "Detection Limit": ("K: 16.7; Ti: 1.12; V: 3; Mn: 4.54; Zn: 0.69; Sr: 0.147; Nb: 0.103; Ba: 0.049; La: 0.113; Ce: 1.102; Pr: 0.580; Nd: 0.129; "
                     "Sm: 0.457; Eu: 0.228; Gd: 0.453; Tb: 0.079; Dy: 0.222; Ho: 0.135; Er: 0.353; Tm: 0.630; Yb: 0.364; Lu: 0.117; Hf: 0.365; "
                     "Ta: 0.333; W: 0.254; other: N" + D + "ppm; Table 3 'LOD' column, beside a single glass-inclusion analysis (n = 1)"),
 "Analytical Accuracy and Assessment Method": "N" + D + "oxide-total normalization 'generally agrees within <10% with the method using EMP CaO or MgO values as internal standards' (" + M + ")",
 "Additional Notes": "The procedure broadly follows Udry et al. (2012) and Pernet-Fisher et al. (2014). Two internal-standard approaches: oxide-total normalization for silicates and oxides, EMP CaO for phosphate. A 90 µm beam on some olivines tested whether low REE signals reflect insufficient sampling (" + M + ")",
})
COL6 = dict(_SHARED, **{  # phosphate (merrillite)
 "Coupling Description": "EMP CaO is the internal standard: 'we calculated the trace element abundances by normalizing the LA-ICP-MS 40Ca counts to CaO concentrations from the EMP analysis'" + D + M,
 "Target Material": "sodium-merrillite" + D + "'We observed only sodium-merrillite' (p.12); Tissint martian meteorite",
 "Laser Spot Geometry": "all: ~24 µm diameter" + D + "'The smaller spot (~24 µm) size was used for phosphate analysis' (" + M + ")",
 "Target Species": REE + ", Sr, Ti" + D + "the merrillite REE (Fig. 9) and Sr and Ti in merrillite; the methods do not list the elements",
 "Reported Variables and Units": REE + " (ppm); Sr; Ti" + D + "merrillite REE, chondrite-normalized in Fig. 9; data in Table S1, not in the archived PDF",
 "Internal Standard Approach": "all: single element measured by EMP" + D + "'normalizing the LA-ICP-MS 40Ca counts to CaO concentrations from the EMP analysis' (" + M + ")",
 "Internal Standard Element": "all: Ca (⁴⁰Ca)" + D + "CaO from EMP (" + M + ")",
 "Normalization / Standards-Based Correction": "all: normalization to EMP CaO" + D + M,
 "Detection Limit": "N" + D + "Table 3's LODs are for the glasses",
 "Analytical Accuracy and Assessment Method": "N",
 "Additional Notes": "N",
})
_F = [
 ("Instrument Model", None, ["7500ce"]), ("Laser Manufacturer & Model", None, ["GeoLasPro"]),
 ("Laser Wavelength and Type", None, ["193 nm"]), ("Laser Repetition Rate", "all", ["5 Hz"]),
 ("Laser Energy", None, ["150 mJ"]), ("Laser Fluence (Energy Density)", None, ["7–10"]),
 ("Background Count Time", None, ["50 s"]), ("Data Processing Software(s)", None, ["AMS"]),
 ("Signal Integration Interval Method", None, ["plateau"]), ("Calibration Standard Measurement Frequency", None, ["before and after"]),
 ("Primary Calibration Standard Name", "all/all", ["NIST 610"]), ("Detection Limit Method", "all", ["3σ"]),
 ("Procedure Reference(s)", None, ["Udry"]),
]
FACTS5 = _F + [("Laser Spot Geometry", "all", ["24 and 32"]), ("Laser Spot Geometry", "all", ["90 µm"]),
               ("Internal Standard Approach", "all", ["100 wt% oxide"]), ("Combination Method", "La", ["average"]),
               ("Detection Limit", "La", ["0.113"]), ("Detection Limit", "Ba", ["0.049"]), ("Goodness-of-Fit or Dispersion Statistic", "La", ["1σ"])]
FACTS6 = _F + [("Laser Spot Geometry", "all", ["~24"]), ("Internal Standard Element", "all", ["Ca"]),
               ("Internal Standard Approach", "all", ["EMP"]), ("Target Material", "sodium-merrillite", ["merrillite"])]

# ---- c7_wu2023
D = " — "
MM = ["27Al", "43Ca", "89Y", "90Zr", "172Yb", "(172+82)Yb", "175Lu", "(175+82)Lu", "(176+82)Hf", "(177+82)Hf", "(178+82)Hf"]
XEN = "MG-1, BS-1, XENOA, M1567"
AP = "Otter Lake, NW-1, MAP-3"
COL7 = {  # Wu et al. 2023 (JAAS 38, 1285), Analyte G2 + iCAP TQ, IGGCAS. Read 2026-09-30: §2 samples, Table 1, data reduction, §3.1, results.
 "Target Material": "xenotime; apatite; garnet" + D + "accessory and metamorphic minerals for in situ Lu-Hf geochronology",
 "Target Species": "Lu, Hf" + D + "Yb is monitored for its interference on (176+82)Hf, and Al, Ca, Y and Zr 'for monitoring inclusions such as Zr for zircons'",
 "Monitored Masses": "175Lu, (175+82)Lu → Lu; (176+82)Hf, (177+82)Hf, (178+82)Hf → Hf; 172Yb, (172+82)Yb, 27Al, 43Ca, 89Y, 90Zr → none" + D + "Table 1 'Isotopes measured (m/z)'",
 "Reported Variables and Units": "176Lu/177Hf; 176Hf/177Hf; common-Hf-corrected single-spot age (Ma); Lu-Hf isochron age (Ma); Lu-Hf weighted-mean age (Ma); Lu concentration; Hf concentration" + D + "single-spot ages from eqn (11); isochron and weighted-mean ages in IsoplotR; Lu and Hf concentrations from Iolite's 'Trace_Element' DRS",
 "Carrier Gas and Flow Rate": "He ablation gas 900 mL/min; Ar carrier gas 0.65 L/min" + D + "Table 1 'Ablation gas flow (He)' and 'Carrier gas flow (Ar)'",
 "Laser Spot Geometry": "all: 50, 90, 150 µm" + D + "Table 1 'Spot size'; chosen according to Lu and Hf contents",
 "Laser Spot Path / Ablation Mode": "all: Single hole drilling, two cleaning pulses" + D + "Table 1 'Sampling mode/pattern'",
 "Laser Repetition Rate": "all: 10 Hz" + D + "Table 1",
 "Collision/Reaction Cell (CRC) Configuration": "all: TQ mode with NH3 reaction gas, the first quadrupole at 1 amu" + D + "tuning first in SQ no-gas mode; 'To avoid interference from 175Lu reaction products ... the required prefiltered mass resolution is 1 amu' (§3.1)",
 "Reaction Gas Type": "all: NH3, high purity (>99.999%)" + D + "supplied in T4; He (>99.999%, T1) was pre-mixed with NH3 before the cell in a test of mixture composition",
 "Collision/Reaction Gas Mixture Ratio": "all: high-purity NH3" + D + "found more effective than the commonly used 1:9 NH3-He mixture; He pre-mixed with NH3 was tested for the effect of mixture composition",
 "Reaction Product Ion / Mass-Shift Transition": "(172+82)Yb, (175+82)Lu, (176+82)Hf, (177+82)Hf, (178+82)Hf: ammonia cluster adduct, mass shift +82; other: N" + D + "(176+82)Hf = 176Hf(14N1H)(14N1H2)3(14N1H3)3; Lu, Yb and Hf reaction products identified over 175–300 amu",
 "Dwell Time per Mass": "27Al: 2 ms; 43Ca: 2 ms; 89Y: 1 ms; 90Zr: 2 ms; 172Yb: 1 ms; (172+82)Yb: 100 ms; 175Lu: 1 ms; (175+82)Lu: 50 ms; (176+82)Hf: 300 ms; (177+82)Hf: 100 ms; (178+82)Hf: 100 ms" + D + "Table 1",
 "Interfering Species": "(176+82)Hf: 176Lu and 176Yb; other: N" + D + "monitored via 175Lu and 172Yb",
 "Interference Correction Method": "(176+82)Hf: reaction-rate correction, subtracting (176Lu/175Lu)true × (175+82)Lu and (176Yb/172Yb)true × (172+82)Yb with 176Lu/175Lu = 0.02655 and 176Yb/172Yb = 0.5887; other: N" + D + "contributions expressed as pLu(%) and pYb(%)",
 "Uncertainty Propagation Method": "all: the Rösel and Zack workflow, combining random uncertainties (measured ratios) with systematic ones (reference material, long-term variance of 1.5%, decay constant, and 1.4% on initial 176Hf/177Hf)" + D + "'The uncertainty propagation workflow reported by Rösel and Zack was adopted in this study'",
 "Normalization / Standards-Based Correction": "176Lu/177Hf, 176Hf/177Hf: external correction of mass bias and fractionation against NIST SRM 610, then a matrix-induced correction against matrix-matched XN02 xenotime; other: N",
 "Combination Method": "Lu-Hf isochron age: isochron regression per sample; Lu-Hf weighted-mean age: weighted mean of the common-Hf-corrected single-spot ages per sample; other: N" + D + "'Isoplot R software was used to calculate isochron and weighted-mean ages'",
 "Primary Calibration Standard Name": "all [Lu, Hf: NIST SRM 610, with XN02 xenotime for the matrix-induced correction]" + D + "NIST SRM 610 recommended values by ID-MC-ICP-MS; XN02 'used as a matrix-matched reference material to correct for matrix-induced elemental fractionation'",
 "Secondary Reference Materials": "ARM-1; " + XEN + "; " + AP + D + "ARM-1 'is used for the quality control' of Lu and Hf concentrations; the xenotime and apatite U–Pb reference materials test the Lu–Hf ages against their ID-TIMS U–Pb ages",
 "Internal (Within-Measurement) Analytical Precision and Assessment Method": "common-Hf-corrected single-spot age: 2SE, ~2.6%; other: N",
 "Within-Session Analytical Precision and Assessment Method": XEN + " [common-Hf-corrected single-spot age: 1.5–8.1%]; " + AP + " [common-Hf-corrected single-spot age: 9.2–36.0%]" + D + "isochron age uncertainties of 3.5–10% for the garnet samples",
 "Analytical Accuracy and Assessment Method": XEN + " [common-Hf-corrected single-spot age: generally better than 1.5%]" + D + "against ID-TIMS U–Pb ages of the same reference materials",
 "Goodness-of-Fit or Dispersion Statistic": "Lu-Hf isochron age, Lu-Hf weighted-mean age: MSWD; other: N" + D + "e.g. MSWD = 2.3 (n = 236, XN02) and MSWD = 0.6 (n = 15, weighted-mean Lu-Hf age 489.8 ± 2.2 Ma)",
}
FACTS7 = [
 ("Laser Manufacturer & Model", None, ["Analyte G2"]), ("Ablation Cell Type", None, ["HelEx"]),
 ("Laser Wavelength and Type", None, ["193 nm"]), ("Laser Pulse Duration", None, ["4-5 ns", "4–5 ns"]),
 ("Laser Fluence (Energy Density)", None, ["4 J"]), ("Laser Repetition Rate", "all", ["10 Hz"]),
 ("Laser Spot Geometry", "all", ["50, 90, 150"]), ("Laser Spot Path / Ablation Mode", "all", ["single hole"]),
 ("Ablation Duration per Spot", None, ["25 s"]), ("RF Power", None, ["1350 W"]),
 ("Coolant (Plasma) Gas Flow Rate", None, ["15.00"]), ("Auxiliary Gas Flow Rate", None, ["0.80"]),
 ("Carrier Gas and Flow Rate", None, ["900"]), ("Carrier Gas and Flow Rate", None, ["0.65"]),
 ("Make-up Gas and Flow Rate", None, ["4.0 mL"]), ("Signal Collection Mode", None, ["peak jump"]),
 ("Total Integration Time per Output Data Point", None, ["0.659"]), ("Mass Resolution Setting", None, ["300"]),
 ("Reaction Gas Type", "all", ["NH3"]), ("Uncertainty Propagation Method", "all", ["Rösel"]),
 ("Primary Calibration Standard Name", "all/Lu", ["NIST SRM 610"]), ("Primary Calibration Standard Name", "all/Hf", ["XN02"]),
 ("Secondary Reference Materials", "ARM-1", ["ARM-1"]), ("Secondary Reference Materials", "MG-1", ["MG-1"]),
 ("Interference Correction Method", "(176+82)Hf", ["0.02655"]), ("Interfering Species", "(176+82)Hf", ["176Yb"]),
 ("Combination Method", "Lu-Hf weighted-mean age", ["weighted mean"]), ("Goodness-of-Fit or Dispersion Statistic", "Lu-Hf isochron age", ["MSWD"]),
 ("Analytical Accuracy and Assessment Method", "MG-1/common-Hf-corrected single-spot age", ["1.5%"]),
] + [("Dwell Time per Mass", m, [v]) for m, v in (("27Al", "2 ms"), ("(176+82)Hf", "300 ms"), ("(175+82)Lu", "50 ms"), ("175Lu", "1 ms"))] \
  + [("Monitored Masses", m, [m]) for m in MM]

# ---- engine
COLS = [  # column number -> label substring (LA-Q order; the U-Pb twin carries 1–6)
 (1, "Nakanishi et al. 2022", COL1), (2, "Liu et al. 2024", COL2),
 (3, "Liu et al. 2025 (GCA 393) Experimental silicate", COL3), (4, "Liu et al. 2025 (GCA 393) Experimental sulfide", COL4),
 (5, "Tissint martian meteorite Silicates", COL5), (6, "Tissint martian meteorite Phosphate", COL6),
 (7, "Wu+etal2023", COL7),
]
UPB_ONLY = ["Chemical Abrasion Conditions", "Age Calculation Method", "Reported Date Type", "Inherited or Initial Signal Correction",
            "Radiogenic Fraction of Measured Signal", "Age Datum / Reference Epoch", "Intermediate Daughter Disequilibrium Correction",
            "Discordance Definition and Values", "Error Correlation Between Reported Quantities"]
NODATE = "N — the procedure reports no date"
TAPPS = ["LA-Q-ICP-MS_TAPP_v", "LA-Q-ICP-MS_UPb_TAPP_v"]


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
