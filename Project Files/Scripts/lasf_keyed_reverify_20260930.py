#!/usr/bin/env python3
"""LA-SF-ICP-MS and its U-Pb twin: keyed notation, with every procedure-level cell re-read (2026-09-30).

    python3 "Project Files/Scripts/lasf_keyed_reverify_20260930.py" [--apply] [--out-sim DIR]

The same pass as laq_keyed_reverify_20260930.py: the literature cells must regenerate each paper's
procedure, so every procedure-level cell of LA-SF's seven columns was re-read against its paper, and the
edit was scored by `Project Files/Reports/LASF_Cells_RoundTrip_2026-09-30/roundtrip.py` before it was
applied. The U-Pb twin carries the same seven columns; its nine geochronology fields become
`N — the procedure reports no date`.

What the re-read found, beyond format (per column in the dicts below):
  * cross-paper borrowing: Zhang+2022's three Ru-interference cells ("⁹⁹Ru used instead of ¹⁰¹Ru to avoid
    ⁴⁰Ar⁶¹Ni⁺") are Navarro+2024's statement, not Zhang's (who measured ¹⁰²Ru); Mittlefehldt's Marjalahti
    control, Grubb's test and 0.6% precision are the EMPA work's; a "cosmic spherule" analysis sequence in
    Chernonozhkin's mapping column comes from no pallasite paper;
  * fabricated detail: bracketing schedules, "daily tuning", "cross-calibration performed", "mathematical
    corrections", "8 sessions over 1 year", FAPESP funding, "10–50 ms ... per paper text";
  * wrong values: Chernonozhkin's pulse (4 ns, not ~5 ns) and run 2 (a 130 µm line scan, not a spot);
    Navarro's LODs (Table 3 gives Fe 60 µg/g, Ni 36, Ir 0.2; the cell had Fe 5300, Ir 0.04);
    farringtonite listed as a phosphate the paper rules out;
  * stated facts missing: Zhang's acquired masses and per-element standards; Chernonozhkin's Table B1
    nuclide lists per run, the 3σ spike filter and the veinlet mask; Navarro's make-up gas line and
    mapping sequence;
  * isotopes recorded as target species, with `Monitored Masses` left `N`, in all seven columns.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
# ---- c1_zhang
D = " — "
S = "§2.2"
EL23 = "P, V, Cr, Mn, Fe, Co, Ni, Cu, Ga, Ge, As, Mo, Ru, Rh, Pd, Sn, Sb, W, Re, Os, Ir, Pt, Au"
MASS = [("³¹P", "P"), ("⁵¹V", "V"), ("⁵³Cr", "Cr"), ("⁵⁵Mn", "Mn"), ("⁵⁷Fe", "Fe"), ("⁵⁹Co", "Co"), ("⁶⁰Ni", "Ni"), ("⁶³Cu", "Cu"),
        ("⁷¹Ga", "Ga"), ("⁷⁴Ge", "Ge"), ("⁷⁵As", "As"), ("⁹⁵Mo", "Mo"), ("¹⁰²Ru", "Ru"), ("¹⁰³Rh", "Rh"), ("¹⁰⁶Pd", "Pd"), ("¹²⁰Sn", "Sn"),
        ("¹²¹Sb", "Sb"), ("¹⁸²W", "W"), ("¹⁸⁵Re", "Re"), ("¹⁹⁰Os", "Os"), ("¹⁹³Ir", "Ir"), ("¹⁹⁵Pt", "Pt"), ("¹⁹⁷Au", "Au")]
COL1 = {  # B. Zhang et al. 2022 (GCA 323, 202), LA-SF-ICP-MS at FSU. Read 2026-09-30: §2.1 samples, §2.2 LA-ICP-MS, §2.3, Table 3 title and note.
 "Sample Preparation Method": "Polished slabs of the irons; a mount of Zinder and a section of NWA 1911 for the pallasites (§2.1); no acid treatment is described for the LA-ICP-MS specimens",
 "Laser Manufacturer & Model": "ElectroScientific Instruments New Wave UP193FX" + D + S,
 "Detector Configuration": "Triple mode detection at 65% duty cycle" + D + "'triple mode detection at 65% duty cycle' (" + S + ")",
 "Acquisition Pass": "raster; Ge spots" + D + "'Irons were analyzed using a raster scan over a few millimeters'; 'To obtain more precise Ge, a set of five 150 µm spots were analyzed at 50 Hz for 20 s on five of the irons' (" + S + ")",
 "Laser Spot Geometry": "raster: 50 µm beam spot; Ge spots: 150 µm" + D + S,
 "Laser Spot Path / Ablation Mode": "raster: raster scan over a few millimeters; Ge spots: spot" + D + S,
 "Laser Repetition Rate": "raster: 50 Hz; Ge spots: 50 Hz" + D + S,
 "Transect Rate, Mapping Rate or Step Size": "raster: 10 µm/s; Ge spots: N/A" + D + "'scanned at 10 µm/s' (" + S + ")",
 "Ablation Duration per Spot": "20 s for the Ge spots" + D + "'analyzed at 50 Hz for 20 s' (" + S + "); the raster duration is not stated",
 "Laser Fluence (Energy Density)": "N",
 "Laser Pulse Duration": "N", "RF Power": "N", "Oxide Production Method and Threshold": "N",
 "Raster Line Spacing (Mapping Only)": "N",
 "Analysis Sequence": "N",
 "Calibration Standard Measurement Frequency": "N",
 "Target Species": EL23 + D + "the 23 elements whose peaks were acquired (" + S + ")",
 "Monitored Masses": "; ".join("%s → %s" % m for m in MASS) + D + "'were used to acquire the peaks 31P, 51V, ... and 197Au' (" + S + ")",
 "Reported Variables and Units": "P, Fe, Co, Ni (mg/g); V, Cr, Mn, Cu, Ga, Ge, As, Mo, Ru, Rh, Pd, Sn, Sb, W, Re, Os, Ir, Pt, Au (µg/g)" + D + "abundances in metal, Table 3 (raster averages) with spot averages in Appendix 2; 'Concentrations below detection limits are not shown'",
 "Dwell Time per Mass": "N",
 "Background Count Time": "N",
 "Inter-Pass Data Dependency": "N" + D + "the Ge value combines both passes (Combination Method), but no pass uses another's data",
 "Number of Replicates": "N" + D + "'a set of five 150 µm spots were analyzed ... on five of the irons, including both slabs of Klamath Falls' (" + S + ")",
 "Internal Standard Approach": "N" + D + "'Standardization techniques followed those of Humayun (2012)' (" + S + ")",
 "Internal Standard Element": "N" + D + "not stated; standardization follows Humayun (2012)",
 "Elemental Fractionation Correction": "N" + D + "'Standardization techniques followed those of Humayun (2012)' (" + S + "); the standards are under Primary Calibration Standard Name",
 "Uncertainty Propagation Method": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "N",
 "Signal Integration Time": "N" + D + "the Ge spots were ablated for 20 s (" + S + ")",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "N",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "'triple mode detection at 65% duty cycle' (" + S + "); a cross-calibration is not described",
 "Spectral Interference Corrections Applied": "N" + D + "the 150 µm Ge spots produced 'a sufficiently bright beam to resolve Ge from background argide interferences' (" + S + "); no correction is described",
 "Interfering Species": "⁷⁴Ge: background argides; other: N" + D + "overcome by the brighter 150 µm Ge spots, not corrected (" + S + ")",
 "Interference Correction Method": "N" + D + "the argide interference on Ge was avoided with a brighter beam, not corrected",
 "Memory Effect Mitigation": "N",
 "Normalization / Standards-Based Correction": "N",
 "Primary Calibration Standard Name": ("all [Fe, Co, Ni, Cu, As, W, Au: North Chile (Filomena, IIAB) and NIST SRM 1263a V-Cr steel; Ga, Ge: North Chile (Filomena, IIAB); "
                                       "Ru, Rh, Pd, Re, Os, Ir, Pt: Hoba (IVB); V, Cr, Mo: NIST SRM 1263a V-Cr steel; other: N]" + D +
                                       "'The standard used for Fe, Co, Ni, Cu, Ga, Ge, As, W, and Au is North Chile (Filomena; IIAB) (Wasson et al., 1989), and the standard for Ru, Rh, Pd, Re, Os, Ir, and Pt is Hoba (IVB) (Walker et al., 2008). NIST SRM 1263a V-Cr steel was also used for V, Cr, Fe, Co, Ni, Cu, As, Mo, W, and Au' (" + S + ")"),
 "Detection Limit": "N" + D + "'Concentrations below detection limits are not shown' (Table 3); the limits are not given",
 "Detection Limit Method": "N",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Analytical Accuracy and Assessment Method": "N" + D + "compared with NAA on the same irons rather than a standard: differences 'mostly ... within the range of ±40%', within ±10% for Ni, Co and Ga, up to 30% for Au and As, and W in Cerro del Inca 4.39 ng/g by LA-ICP-MS against 1.06 ng/g by INAA (§2.3)",
 "Additional Notes": "The raster pass gives the 23-element dataset; a separate set of 150 µm spots on five irons gives more precise Ge, since the raster 'failed to yield useful Ge abundances for Klamath Falls' (" + S + ")",
}
FACTS1 = [
 ("Instrument Model", None, ["Element XR"]), ("Laser Manufacturer & Model", None, ["UP193FX"]),
 ("Mass Resolution Setting", None, ["400"]), ("Detector Configuration", None, ["65%"]),
 ("Laser Spot Geometry", "raster", ["50 µm"]), ("Laser Spot Geometry", "Ge spots", ["150 µm"]),
 ("Transect Rate, Mapping Rate or Step Size", "raster", ["10 µm"]), ("Laser Repetition Rate", "raster", ["50 Hz"]),
 ("Laser Repetition Rate", "Ge spots", ["50 Hz"]), ("Ablation Duration per Spot", None, ["20 s"]),
 ("Interfering Species", "⁷⁴Ge", ["argide"]),
 ("Primary Calibration Standard Name", "all/Fe", ["North Chile"]), ("Primary Calibration Standard Name", "all/Ir", ["Hoba"]),
 ("Primary Calibration Standard Name", "all/Mo", ["1263a"]), ("Primary Calibration Standard Name", "all/Ge", ["North Chile"]),
 ("Combination Method", "Ge", ["mean of the spot average and the raster average"]),
 ("Procedure Reference(s)", None, ["Humayun"]), ("Acquisition Pass", "Ge spots", ["Ge spots"]),
] + [("Monitored Masses", m, [m]) for m, _ in MASS] + [("Target Species", e, [e]) for _, e in MASS]

# ---- c234_chernonozhkin
D = " — "
B1 = "Table B1"
def masses(pairs):
    return "; ".join("%s → %s" % (m, e) for m, e in pairs)
MAP = [("²⁵Mg", "Mg"), ("²⁷Al", "Al"), ("²⁹Si", "Si"), ("³¹P", "P"), ("⁴⁵Sc", "Sc"), ("⁵¹V", "V"), ("⁵³Cr", "Cr"), ("⁵⁵Mn", "Mn"),
       ("⁵⁷Fe", "Fe"), ("⁶⁰Ni", "Ni"), ("⁷¹Ga", "Ga"), ("¹³⁹La", "La"), ("¹⁵³Eu", "Eu"), ("¹⁹⁵Pt", "Pt")]
RUN1 = [("²⁵Mg", "Mg"), ("²⁹Si", "Si"), ("³¹P", "P"), ("⁴⁴Ca", "Ca"), ("⁵³Cr", "Cr"), ("⁵⁵Mn", "Mn"), ("⁵⁷Fe", "Fe")]
RUN2 = [("⁷Li", "Li"), ("⁴⁵Sc", "Sc"), ("⁵¹V", "V"), ("⁵⁹Co", "Co"), ("⁶⁰Ni", "Ni"), ("⁶³Cu", "Cu"), ("⁶⁶Zn", "Zn"),
        ("⁸⁹Y", "Y"), ("⁹⁰Zr", "Zr"), ("⁹³Nb", "Nb"), ("¹³³Cs", "Cs"), ("¹³⁷Ba", "Ba"), ("¹³⁹La", "La"), ("¹⁴⁰Ce", "Ce"), ("¹⁴¹Pr", "Pr"),
        ("¹⁴⁵Nd", "Nd"), ("¹⁴⁷Sm", "Sm"), ("¹⁵³Eu", "Eu"), ("¹⁵⁸Gd", "Gd"), ("¹⁵⁹Tb", "Tb"), ("¹⁶⁴Dy", "Dy"), ("¹⁶⁵Ho", "Ho"), ("¹⁶⁰Er", "Er"),
        ("¹⁶⁹Tm", "Tm"), ("¹⁷⁴Yb", "Yb"), ("¹⁷⁵Lu", "Lu"), ("¹⁸⁰Hf", "Hf"), ("¹⁸¹Ta", "Ta"), ("¹⁸²W", "W"), ("¹⁸⁵Re", "Re"), ("¹⁹³Ir", "Ir"),
        ("¹⁹⁵Pt", "Pt"), ("¹⁹⁷Au", "Au"), ("²³²Th", "Th"), ("²³⁸U", "U")]
PH = [("²³Na", "Na"), ("²⁵Mg", "Mg"), ("²⁷Al", "Al"), ("²⁹Si", "Si"), ("³¹P", "P"), ("³⁹K", "K"), ("⁴⁴Ca", "Ca"), ("⁴⁵Sc", "Sc"), ("⁴⁷Ti", "Ti"),
      ("⁵¹V", "V"), ("⁵³Cr", "Cr"), ("⁵⁵Mn", "Mn"), ("⁵⁷Fe", "Fe"), ("⁵⁹Co", "Co"), ("⁶⁰Ni", "Ni"), ("⁶³Cu", "Cu"), ("⁶⁶Zn", "Zn"), ("⁸⁵Rb", "Rb"),
      ("⁸⁸Sr", "Sr"), ("⁸⁹Y", "Y"), ("⁹⁰Zr", "Zr"), ("⁹³Nb", "Nb"), ("¹³³Cs", "Cs"), ("¹³⁷Ba", "Ba"), ("¹³⁹La", "La"), ("¹⁴⁰Ce", "Ce"),
      ("¹⁴¹Pr", "Pr"), ("¹⁴⁵Nd", "Nd"), ("¹⁴⁷Sm", "Sm"), ("¹⁵³Eu", "Eu"), ("¹⁵⁸Gd", "Gd"), ("¹⁵⁹Tb", "Tb"), ("¹⁶⁴Dy", "Dy"), ("¹⁶⁵Ho", "Ho"),
      ("¹⁶⁰Er", "Er"), ("¹⁶⁹Tm", "Tm"), ("¹⁷⁴Yb", "Yb"), ("¹⁷⁵Lu", "Lu"), ("¹⁸⁰Hf", "Hf"), ("¹⁸¹Ta", "Ta"), ("²⁰⁸Pb", "Pb"), ("²³²Th", "Th"), ("²³⁸U", "U")]
def els(pairs):
    seen = []
    for _, e in pairs:
        if e not in seen:
            seen.append(e)
    return ", ".join(seen)
GLASS6 = "NIST SRM 612, NIST SRM 614, USGS GSD-1G, USGS GSE-1G, BHVO-2G, BIR-1G"

_SHARED = {  # Chernonozhkin et al. 2021 (Chem Geol 562), Ghent. Read 2026-09-30: §2.1–2.2.4, §3.1–3.4, Appendices B (Table B1) and C (C1–C5, Table C1).
 "Funding Source for Procedure Development": "N" + D + "the BELSPO, FWO, BOF-UGent and Humboldt support is for the study as a whole and is recorded under Funding Source for Analysis",
 "Sample Preparation Method": "Flat polished thick sections (§2.1)",
 "Laser Wavelength and Type": "193 nm ArF* excimer" + D + "§2.2.2",
 "Laser Pulse Duration": "4 ns" + D + "Table B1; §2.2.2 says '<5 ns'",
 "Detector Configuration": "Triple" + D + "Table B1 'Detection mode'",
 "Signal Smoothing": "N",
 "Oxide Production Method and Threshold": "N",
 "Elemental Fractionation Correction": "N",
 "Uncertainty Propagation Method": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Signal Integration Interval Method": "N",
 "Secondary Reference Materials": "N",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Analytical Accuracy and Assessment Method": "N",
}
COL2 = dict(_SHARED, **{  # olivine 2D mapping
 "Acquisition Pass": "map" + D + "a single pass: 'The laser scanned a grid of parallel, adjacent lines' (§2.2.2)",
 "Pre-Ablation Surface Treatment": "N",
 "Mass Resolution Setting": "Low (M/ΔM = 300)" + D + "§2.2.2",
 "Mass Resolution Assignment": "all: low resolution (M/ΔM = 300)" + D + B1,
 "Laser Beam Energy Profile": "Flat-topped" + D + "'The laser beam is characterized by a flat-topped energy profile' (§2.2.2)",
 "Laser Spot Geometry": "all: 20 µm × 20 µm square-masked" + D + "§2.2.2",
 "Laser Spot Path / Ablation Mode": "all: grid of parallel, adjacent lines" + D + "§2.2.2; the grid runs 'from the metal-olivine margin to the olivine cores'",
 "Laser Repetition Rate": "all: 20 Hz",
 "Transect Rate, Mapping Rate or Step Size": "all: 9 µm/s" + D + "translation speed (§2.2.2)",
 "Raster Line Spacing (Mapping Only)": "Adjacent lines" + D + "'a grid of parallel, adjacent lines using a 20 µm × 20 µm square-masked laser spot' (§2.2.2)",
 "Make-up Gas and Flow Rate": "Ar, 0.81–0.99 L/min" + D + "Table B1; 'No N2 was blent into ICP to avoid elevated nitrogen-based spectral interferences'",
 "Coolant (Plasma) Gas Flow Rate": "Ar, 15 L/min" + D + B1,
 "Auxiliary Gas Flow Rate": "Ar, 0.81 L/min" + D + B1,
 "RF Power": "800 W" + D + "cool plasma (§2.2.2, Table B1)",
 "Plasma Thermal Mode": "all: cool plasma (800 W RF)" + D + "'Cool plasma conditions (800 W RF power) were used to reduce Ar-based interferences and to increase the sensitivity of the analysis' (§2.2.2)",
 "ICP Tuning": "N" + D + "oxide-based interferences 'were further minimized during tuning' (App. C4); no tuning procedure is described",
 "Analysis Sequence": "N" + D + "the glasses were 'measured in the same analytical session' (§2.1); the sequence is not described",
 "Target Species": els(MAP) + D + "the 14 nuclides of the mapping (§2.2.2)",
 "Monitored Masses": masses(MAP) + D + "'a total scan cycle time of 1.944 s for 14 nuclides' (§2.2.2)",
 "Reported Variables and Units": els(MAP) + " (concentration maps, µg/g); Fa#; principal-component scores" + D + "'2D concentration matrices of all target elements'; pure-olivine averages in Table E1",
 "Dwell Time per Mass": "all: 0.01 s sample time" + D + "10 samples per peak, mass window 100%, duty cycle 1.944 s (Table B1); the scan method 'speed-optimized'",
 "Background Count Time": "10 gas-blank scans before each line, 80 during ablation" + D + B1,
 "Inter-Pass Data Dependency": "N/A" + D + "a single pass",
 "Number of Replicates": "N",
 "Internal Standard Approach": "all: sum normalization of MgO, FeO, SiO2 and P2O5 to 100 wt% in each pixel (Liu et al., 2008)" + D + "the oxide sum is a 'virtual, evenly distributed IS' (App. C1, equations 1–2)",
 "Internal Standard Element": "all: none" + D + "a virtual internal standard from the oxide sum (App. C1)",
 "Spike / Outlier Filtering Approach": "P-rich veinlet pixels masked: P2O5 above the best-fitting Gaussian of each map's P2O5 histogram plus 3 standard deviations" + D + "§3.1; 'A MATLAB script was applied to mask pixels representing veinlets'",
 "Blank / Background Correction Method": "Gas blank before each string of pixels; the average background preceding each analysis subtracted" + D + "App. C5",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "'Triple' detection (Table B1); a cross-calibration is not described",
 "Spectral Interference Corrections Applied": "No mathematical correction" + D + "argide interferences reduced by cool plasma, oxide interferences 'less prevalent as a result of the dry plasma conditions and ... further minimized during tuning', and plasma-gas and atmospheric interferences 'corrected by background subtraction' (App. C4)",
 "Interfering Species": ("²⁵Mg: ¹²C¹³C⁺; ²⁷Al: ¹³C¹⁴N⁺; ²⁹Si: ¹³C¹⁶O⁺ and ¹⁴N¹⁵N⁺; ³¹P: ¹⁵N¹⁶O⁺ and ¹³C¹⁸O⁺; ⁴⁵Sc: ²⁹Si¹⁶O⁺; ⁵¹V: ³⁵Cl¹⁶O⁺ and ⁴⁰Ar¹¹B⁺; "
                         "⁵³Cr: ⁴⁰Ar¹³C⁺ and ³⁷Cl¹⁶O⁺; ⁵⁵Mn: ⁴⁰Ar¹⁵N⁺ and ³⁹K¹⁶O⁺; ⁵⁷Fe: ⁴⁰Ar¹⁶O¹H⁺ and ³⁹K¹⁸O⁺; ⁶⁰Ni: ⁴⁴Ca¹⁶O⁺ and ²⁴Mg³⁶Ar⁺; "
                         "⁷¹Ga: ³¹P⁴⁰Ar⁺, ⁵⁵Mn¹⁶O⁺ and ⁵³Cr¹⁸O⁺; ¹⁵³Eu: ¹³⁷Ba¹⁶O⁺; other: N" + D + "Table C1, a 'non-exhaustive list', which also lists doubly charged ions"),
 "Interference Correction Method": "⁶⁰Ni, ⁷¹Ga: argide interferences reduced by cool plasma conditions; other: N" + D + "'argide-based interferences were reduced by the application of cool plasma conditions (e.g., 36Ar24Mg+ and 40Ar31P+ interferences for 60Ni and 71Ga, respectively)'; interferences present at all times are 'corrected by background subtraction' (App. C4)",
 "Memory Effect Mitigation": "Washout typically less than 1 s" + D + "§2.2.2",
 "Normalization / Standards-Based Correction": "all: after calibration, each pixel re-normalised so that the MgO, FeO, SiO2 and P2O5 sum is 100 wt%" + D + "App. C1, equations 3–4; the per-pixel sums had 'varied between 95-99 wt %'",
 "Primary Calibration Standard Name": "all [all: " + GLASS6 + "]" + D + "linear regression on the internally normalised data; each glass processed as 3 replicate 2 mm line scans (§2.1, App. C1)",
 "Calibration Standard Measurement Frequency": "N" + D + "the glasses were 'measured in the same analytical session' (§2.1)",
 "Detection Limit": "all: per-pixel LODs, averaged over the map" + D + "Table E1 (Na = 1, Nb = 10), App. C5",
 "Detection Limit Method": "all: Longerich et al. (1996), LOD = 3SD/S × √(1/Nb + 1/Na)" + D + "Na = 1 and Nb = 10 for a pixel (App. C5)",
 "Limit of Quantification (LOQ) Method": "all: as the LOD, with 10 SD instead of 3 SD" + D + "App. C5",
 "Additional Notes": "Cool plasma (800 W) mapping with a lateral resolution of approximately 20 µm; P-rich veinlets masked before averaging (§2.2.2, §3.1)",
})
COL3 = dict(_SHARED, **{  # olivine line scans, run 1 + run 2
 "Acquisition Pass": "run 1 (major elements); run 2 (trace elements)" + D + "two line-scans on the same 400 µm line, each after pre-ablation; 'Every analysis was carried out 3 times' (§2.2.3)",
 "Pre-Ablation Surface Treatment": "Pre-ablation before each analysis: 2 J/cm², 20 Hz, 150 µm square-masked spot, 300 µm/s" + D + "'to avoid bias in the trace element concentrations due to re-deposition of ablated sample material after previous analyses' (§2.2.3)",
 "Mass Resolution Setting": "run 1: medium (M/ΔM = 4000); run 2: low (M/ΔM = 300)" + D + "§2.2.3",
 "Mass Resolution Assignment": "run 1: medium resolution (M/ΔM = 4000); run 2: low resolution (M/ΔM = 300)" + D + "§2.2.3",
 "Laser Spot Geometry": "run 1: 30 µm diameter circular-masked; run 2: 130 µm diameter" + D + "§2.2.3",
 "Laser Spot Path / Ablation Mode": "run 1: line scan, 400 µm; run 2: line scan on top of run 1, 400 µm" + D + "'a second line-scan was completed on top of the first one' (§2.2.3)",
 "Laser Fluence (Energy Density)": "4.72 J/cm² (both runs)" + D + "§2.2.3",
 "Laser Repetition Rate": "run 1: 20 Hz; run 2: 40 Hz",
 "Transect Rate, Mapping Rate or Step Size": "run 1: 10 µm/s; run 2: 10 µm/s",
 "Ablation Duration per Spot": "50 s of sample ablation per 400 µm line, both runs" + D + B1,
 "Make-up Gas and Flow Rate": "Ar, 0.947 L/min (both runs)" + D + "Table B1; no N2 added",
 "Coolant (Plasma) Gas Flow Rate": "Ar, 15 L/min" + D + B1,
 "Auxiliary Gas Flow Rate": "Ar, 0.90 L/min" + D + B1,
 "Plasma Thermal Mode": "N" + D + "RF power 1000 W for both runs (Table B1); only the mapping is described as cool plasma",
 "ICP Tuning": "N",
 "Analysis Sequence": "MPI-DING and USGS reference materials at the start and end of each analytical session; every analysis carried out 3 times" + D + "§2.2.3",
 "Target Species": els(RUN1 + RUN2) + D + "run 1 measures Mg, Si, P, Ca, Cr, Mn, Fe; run 2 the 36 trace and minor elements (§2.2.3)",
 "Monitored Masses": masses(RUN1) + "; " + masses([p for p in RUN2]) + D + "run 1: '25Mg, 29Si, 31P, 44Ca, 53Cr, 55Mn and 57Fe'; run 2: 36 nuclides (§2.2.3), ⁵³Cr also in run 2 (Table B1)",
 "Reported Variables and Units": els(RUN1 + RUN2) + " (µg/g); Fa#" + D + "Table 1, 'the average from 3 replicate measurements'",
 "Dwell Time per Mass": "all: 0.01 s sample time" + D + "run 1: 18 samples per peak, duty cycle 2.069 s; run 2: 7 samples per peak, 2.062 s (Table B1)",
 "Background Count Time": "5 gas-blank scans and 24 ablation scans per analysis, both runs; 10 s of blank per run" + D + B1,
 "Inter-Pass Data Dependency": "run 1: N/A; run 2: normalised to the Cr concentration from run 1" + D + "'The Cr concentrations calculated from this run were then used for internal standardization to normalize the data of the second, trace element run' (§2.2.3)",
 "Number of Replicates": "3" + D + "'Every analysis was carried out 3 times' (§2.2.3); Table B1 '400 µm lines, n = 3'",
 "Internal Standard Approach": "run 1: sum normalization of the oxides to 100 wt% (Liu et al., 2008); run 2: single element from run 1" + D + "§2.2.3, App. C2",
 "Internal Standard Element": "run 1: none (oxide sum); run 2: Cr (concentration from run 1)" + D + "§2.2.3",
 "Signal Integration Time": "N" + D + "50 s of sample ablation per line (Table B1); the integration window is not stated",
 "Spike / Outlier Filtering Approach": "Surface-impurity spikes removed with a 3 sigma filter; results with significant spikes not included in Table 1; Pb and U not presented because of multiple spikes" + D + "§3.3",
 "Blank / Background Correction Method": "Gas blank before each line analysis; the average background preceding each analysis subtracted" + D + "App. C5",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "'Triple' detection (Table B1); at the 130 µm spot, major elements saturate the detector 'even when using the triple detection mode' (App. C2)",
 "Spectral Interference Corrections Applied": "No mathematical correction" + D + "interferences present at all times are 'corrected by background subtraction'; others are partly accounted for by similar concentrations in the calibration standards (App. C4)",
 "Interfering Species": "N" + D + "Table C1 lists interferences on the mapping nuclides; none is listed for the line-scan runs",
 "Interference Correction Method": "N",
 "Memory Effect Mitigation": "11 s of washout per run" + D + B1,
 "Normalization / Standards-Based Correction": "N" + D + "the normalisation is the internal standardisation (Internal Standard Approach)",
 "Primary Calibration Standard Name": "all [all: " + GLASS6 + ", KL2-G, ML3B-G, StHs6/80-G, T1-G, ATHO-G, BM90/21-G, GOR128-G, GOR132-G]" + D + "for both runs, 'repeatedly measured with the corresponding laser settings' (App. C2)",
 "Calibration Standard Measurement Frequency": "Start and end of each analytical session" + D + "'MPI-DING and USGS reference materials were measured at the start and end of each analytical session' (§2.2.3)",
 "Detection Limit": "Cu: 0.28 ng/g; Cs: 4.9 ng/g; Ba: 16 ng/g; W: 5.4 ng/g; Re: 0.42 ng/g; Ir: 0.95 ng/g; Pt: 0.73 ng/g; Au: 1.8 ng/g; Nb: 0.61 ng/g; other: Table 1" + D + "stated in §3.3; LODs averaged over analyses (Na = 24, Nb = 5). §3.3 also gives 33 ng/g for Sr, which is not among the measured nuclides",
 "Detection Limit Method": "all: Longerich et al. (1996), LOD = 3SD/S × √(1/Nb + 1/Na)" + D + "Na = 24 and Nb = 5 (App. C5)",
 "Limit of Quantification (LOQ) Method": "all: as the LOD, with 10 SD instead of 3 SD" + D + "App. C5",
 "Additional Notes": "Two line-scan runs on the same line after pre-ablation: run 1 (30 µm, medium resolution) gives the major elements and Cr, which normalises run 2 (130 µm, low resolution) for the trace elements (§2.2.3, App. C2)",
})
COL4 = dict(_SHARED, **{  # phosphate spots
 "Target Material": "stanfieldite; merrillite" + D + "Ca-phosphate grains: stanfieldite in Brahin and CMS 04071, merrillite in Esquel and Seymchan (§2.1, §3.4); farringtonite was ruled out",
 "Acquisition Pass": "spot" + D + "a single pass: 'All elements were measured during single spot ablation' (§2.2.4)",
 "Pre-Ablation Surface Treatment": "N",
 "Laser Spot Geometry": "all: 110 µm diameter circular-masked" + D + "§2.2.4",
 "Laser Spot Path / Ablation Mode": "all: single spot ablation" + D + "§2.2.4",
 "Laser Repetition Rate": "all: 20 Hz",
 "Coolant (Plasma) Gas Flow Rate": "Ar, 15 L/min" + D + B1,
 "Auxiliary Gas Flow Rate": "Ar, 0.85 L/min" + D + B1,
 "Plasma Thermal Mode": "N" + D + "RF power 1000 W (Table B1)",
 "ICP Tuning": "N",
 "Analysis Sequence": "MPI-DING and USGS glasses at the beginning and repeatedly at the end of each analytical session" + D + "App. C3",
 "Target Species": els(PH) + D + "'The intensities of 43 nuclides were recorded' (§2.2.4)",
 "Monitored Masses": masses(PH) + D + "§2.2.4",
 "Reported Variables and Units": els(PH) + " (µg/g); phosphate mineral (nominal)" + D + "Table 2, each 'single parallel measurement' listed per grain",
 "Dwell Time per Mass": "all: 0.01 s sample time" + D + "5 samples per peak, duty cycle 1.813 s, mass window 150% for ²³Na–⁴⁷Ti and 100% for the others (Table B1)",
 "Inter-Pass Data Dependency": "N/A" + D + "a single pass",
 "Number of Replicates": "N" + D + "Table 2 lists each 'single parallel measurement' per grain; 'Parallel analyses of single phosphate grains are highly reproducible' (§3.4)",
 "Internal Standard Approach": "all: sum normalization of the element oxides to 100 wt% (Liu et al., 2008)" + D + "App. C3",
 "Internal Standard Element": "all: none" + D + "oxide-sum normalisation (App. C3)",
 "Signal Integration Time": "N" + D + "20 s of spot ablation (§2.2.4)",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "Gas blank before each spot; the average background preceding each analysis subtracted" + D + "App. C5",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "'Triple' detection (Table B1)",
 "Spectral Interference Corrections Applied": "N",
 "Interfering Species": "N",
 "Interference Correction Method": "N",
 "Normalization / Standards-Based Correction": "N" + D + "the normalisation is the internal standardisation (Internal Standard Approach)",
 "Primary Calibration Standard Name": "all [all: MPI-DING and USGS glass reference materials]" + D + "'In the absence of suited phosphate reference material' (App. C3)",
 "Calibration Standard Measurement Frequency": "Beginning and repeatedly at the end of each analytical session" + D + "App. C3",
 "Detection Limit": "N",
 "Detection Limit Method": "N",
 "Additional Notes": "No phosphate reference material exists, so glasses calibrate (App. C3); grains identified as stanfieldite or merrillite from a Ca/(Ca + Mg) plot (§3.4)",
})
_F = [("Instrument Model", None, ["Element XR"]), ("Laser Manufacturer & Model", None, ["Analyte G2"]),
      ("Ablation Cell Type", None, ["HELEX"]), ("Laser Pulse Duration", None, ["4 ns"]), ("Detector Configuration", None, ["Triple"])]
FACTS2 = _F + [("Laser Spot Geometry", "all", ["20 µm × 20 µm"]), ("Laser Repetition Rate", "all", ["20 Hz"]),
  ("Transect Rate, Mapping Rate or Step Size", "all", ["9 µm"]), ("Laser Fluence (Energy Density)", None, ["5-7", "5–7"]),
  ("RF Power", None, ["800 W"]), ("Plasma Thermal Mode", "all", ["cool plasma"]), ("Make-up Gas and Flow Rate", None, ["0.81–0.99"]),
  ("Auxiliary Gas Flow Rate", None, ["0.81"]), ("Carrier Gas and Flow Rate", None, ["0.200"]), ("Memory Effect Mitigation", None, ["1 s"]),
  ("Internal Standard Approach", "all", ["100 wt%"]), ("Spike / Outlier Filtering Approach", None, ["3 standard deviations"]),
  ("Primary Calibration Standard Name", "all/all", ["GSD-1G"]), ("Detection Limit Method", "all", ["Longerich"]),
  ("Interference Correction Method", "⁶⁰Ni", ["cool plasma"]), ("Interfering Species", "⁶⁰Ni", ["²⁴Mg³⁶Ar"]),
  ("Laser Beam Energy Profile", None, ["flat"])] + [("Monitored Masses", m, [m]) for m, _ in MAP]
FACTS3 = _F + [("Laser Spot Geometry", "run 1", ["30 µm"]), ("Laser Spot Geometry", "run 2", ["130 µm"]),
  ("Laser Repetition Rate", "run 1", ["20 Hz"]), ("Laser Repetition Rate", "run 2", ["40 Hz"]),
  ("Transect Rate, Mapping Rate or Step Size", "run 2", ["10 µm"]), ("Mass Resolution Assignment", "run 1", ["4000"]),
  ("Mass Resolution Assignment", "run 2", ["300"]), ("Laser Fluence (Energy Density)", None, ["4.72"]),
  ("Pre-Ablation Surface Treatment", None, ["150 µm"]), ("Internal Standard Element", "run 2", ["Cr"]),
  ("Internal Standard Approach", "run 1", ["100 wt%"]), ("Inter-Pass Data Dependency", "run 2", ["Cr"]),
  ("Number of Replicates", None, ["3"]), ("Spike / Outlier Filtering Approach", None, ["3 sigma"]),
  ("Calibration Standard Measurement Frequency", None, ["start and end"]), ("Detection Limit", "Au", ["1.8"]),
  ("Primary Calibration Standard Name", "all/all", ["GOR132-G"])] + [("Monitored Masses", m, [m]) for m, _ in RUN1 + RUN2]
FACTS4 = _F + [("Laser Spot Geometry", "all", ["110 µm"]), ("Laser Repetition Rate", "all", ["20 Hz"]),
  ("Laser Fluence (Energy Density)", None, ["3.5"]), ("Ablation Duration per Spot", None, ["20 s"]),
  ("Internal Standard Approach", "all", ["100 wt%"]), ("Primary Calibration Standard Name", "all/all", ["MPI-DING"]),
  ("Target Material", "merrillite", ["merrillite"]), ("Target Material", "stanfieldite", ["stanfieldite"])] + [("Monitored Masses", m, [m]) for m, _ in PH]

# ---- c567
D = " — "
M33 = "§3.3"
MIT = [("²⁵Mg", "Mg"), ("²⁷Al", "Al"), ("³¹P", "P"), ("⁴³Ca", "Ca"), ("⁴⁴Ca", "Ca"), ("⁴⁵Sc", "Sc"), ("⁴⁷Ti", "Ti"), ("⁴⁹Ti", "Ti"),
       ("⁵¹V", "V"), ("⁵²Cr", "Cr"), ("⁵³Cr", "Cr"), ("⁵⁹Co", "Co"), ("⁶⁰Ni", "Ni"), ("⁶¹Ni", "Ni"), ("⁶²Ni", "Ni"), ("⁶⁴Zn", "Zn"),
       ("⁶⁶Zn", "Zn"), ("⁶⁹Ga", "Ga"), ("⁷¹Ga", "Ga")]
MIT_EL = "Mg, Al, P, Ca, Sc, Ti, V, Cr, Co, Ni, Zn, Ga"
COL5 = {  # Mittlefehldt 2024, Appendix A (GCA), JSC. Read 2026-09-30: §2 sample preparation, §3.3 LA-ICP-MS, §4 results, §6.1.
 "Laser Manufacturer & Model": "New Wave UP-193 solid state laser" + D + M33,
 "ICP-MS Type": "Magnetic-sector" + D + "'magnetic-sector Thermo Fisher Element-XR ICP-MS' (" + M33 + ")",
 "Mass Resolution Setting": "Medium (m/Δm of 4000)" + D + M33,
 "Mass Resolution Assignment": "all: medium resolution (m/Δm of 4000)" + D + M33,
 "Laser Spot Geometry": "all: 75 µm spot size" + D + M33,
 "Laser Spot Path / Ablation Mode": "all: spot mode" + D + "'The laser was run in spot mode' (" + M33 + ")",
 "Analysis Sequence": "N" + D + "the Marjalahti control belongs to the EMPA work (§3.1)",
 "Target Species": MIT_EL + D + "the elements of the 19 nuclides measured (" + M33 + ")",
 "Monitored Masses": "; ".join("%s → %s" % p for p in MIT) + D + "'The nuclides measured were 25Mg, 27Al, 31P, 43Ca, 44Ca, 45Sc, 47Ti, 49Ti, 51V, 52Cr, 53Cr, 59Co, 60Ni, 61Ni, 62Ni, 64Zn, 66Zn, 69Ga and 71Ga' (" + M33 + ")",
 "Reported Variables and Units": MIT_EL + " (µg/g)" + D + "olivine trace element contents, individual data in Table L1, averages per sample split in Table L2 and per meteorite in Table L3 (§4)",
 "Dwell Time per Mass": "N" + D + "the files documenting the analysis parameters 'were lost' (" + M33 + ")",
 "Background Count Time": "N" + D + "the analysis parameters were lost (" + M33 + ")",
 "Inter-Pass Data Dependency": "N/A" + D + "a single pass",
 "Internal Standard Approach": "all: single element, its concentration from EMPA" + D + "'25Mg was used as the indexing element for quantification with the EMPA data used as the standardizing values' (" + M33 + ")",
 "Internal Standard Element": "all: Mg (²⁵Mg)" + D + M33,
 "Elemental Fractionation Correction": "N",
 "Signal Integration Interval Method": "Time steps with enhanced count rates from inclusions or heterogeneity excluded" + D + "'Analysis time steps that had enhanced count rates due to inclusions or heterogeneity were excluded from the data reduction'; inclusions show as 'time steps with enhanced P, Ca, Co, Ni and/or Zn count rates' (" + M33 + ")",
 "Spike / Outlier Filtering Approach": "Time steps with enhanced count rates from inclusions or heterogeneity excluded from the data reduction" + D + M33,
 "Blank / Background Correction Method": "N",
 "Spectral Interference Corrections Applied": "N" + D + "the analysis parameters were lost (" + M33 + ")",
 "Interfering Species": "N",
 "Interference Correction Method": "N" + D + "medium mass resolution (m/Δm of 4000) was used; its purpose is not stated (" + M33 + ")",
 "Normalization / Standards-Based Correction": "N",
 "Primary Calibration Standard Name": "all [all: USGS glasses BCR-2g, BHVO-2g and BIR-1g]" + D + "'Preferred values from the GeoReM website ... were used to define the calibration lines' (" + M33 + ")",
 "Secondary Reference Materials": "N",
 "Counting Statistics Error": "N" + D + "the ~0.6% precision on Fe/Mn is for the EMPA (§3.1)",
 "Combination Method": "all: average per sample split, and weighted mean per meteorite" + D + "'data averaged per sample split' (Table L2), 'meteorite averages' (Table L3); 'Because a weighted mean is calculated for the data' (§6.1)",
 "Analytical Accuracy and Assessment Method": "N" + D + "LA-ICP-MS Sc agrees with INAA 'with scatter of roughly ±0.5 µg/g'; Cr scatters more (§6.1)",
 "Additional Notes": "The files documenting the analysis parameters (gas flows, laser power, etc.) were lost during an extended shutdown of the JSC ICP-MS laboratory; the grains are the EMPA grain mounts, 'low in inclusions, [but] not devoid of them' (" + M33 + ")",
}
NAV = [("⁵²Cr", "Cr"), ("⁵⁷Fe", "Fe"), ("⁵⁹Co", "Co"), ("⁶¹Ni", "Ni"), ("⁶⁵Cu", "Cu"), ("⁶⁹Ga", "Ga"), ("⁷²Ge", "Ge"), ("⁷⁵As", "As"),
       ("⁹⁹Ru", "Ru"), ("¹⁰³Rh", "Rh"), ("¹⁰⁵Pd", "Pd"), ("¹⁸²W", "W"), ("¹⁸⁵Re", "Re"), ("¹⁸⁹Os", "Os"), ("¹⁹³Ir", "Ir"), ("¹⁹⁵Pt", "Pt"), ("¹⁹⁷Au", "Au")]
NAV_EL = "Cr, Fe, Co, Ni, Cu, Ga, Ge, As, Ru, Rh, Pd, W, Re, Os, Ir, Pt, Au"
_NAV = {  # Navarro et al. 2024 (ACS ESC 8, 281), UNICAMP. Read 2026-09-30: Experimental section, Table 2, results (calibration, LOD, precision), Table 3, Table 5, acknowledgements.
 "Funding Source for Procedure Development": "N" + D + "the acknowledgements name CNPq grant 316191/2021-3 (J.E.) and support for a conference presentation; neither is for procedure development",
 "Laser Manufacturer & Model": "Excite 193 (Teledyne)" + D + "Table 2",
 "Detector Configuration": "Triple mode" + D + "Table 2 'detector range'; 'performed in low-resolution and triple mode detection'",
 "Mass Resolution Assignment": "all: low resolution (300)" + D + "Table 2",
 "Laser Pulse Duration": "4 ns" + D + "Table 2",
 "Make-up Gas and Flow Rate": "Ar makeup gas, combined via a T-piece near the torch; Table 2 lists a nebulizer gas flow rate of 1.1 L/min" + D + "Table 2",
 "Coolant (Plasma) Gas Flow Rate": "16 L/min" + D + "Table 2 'plasma gas flow rate'",
 "Auxiliary Gas Flow Rate": "0.9 L/min" + D + "Table 2",
 "Signal Smoothing": "N",
 "ICP Tuning": "ICP-MS and laser settings optimised daily 'to achieve the compromise between optimum signal intensity and low oxide formation, as specified by the factory'; mass calibration and detector cross-calibration 'systematically checked and redone if required'" + D + "Experimental section",
 "Oxide Production Method and Threshold": "N",
 "Target Species": NAV_EL + D + "Table 2",
 "Monitored Masses": "; ".join("%s → %s" % p for p in NAV) + D + "Table 2, with relative abundances; for Fe and Ni the lower-abundance isotopes 'allow their measurement in the analog mode'",
 "Reported Variables and Units": "Fe, Ni (g/100 g); Cr, Co, Cu, Ga, Ge, As, Ru, Rh, Pd, W, Re, Os, Ir, Pt, Au (µg/g); chemical classification (nominal)" + D + "Table 3 and Table 5",
 "Dwell Time per Mass": "all: 0.02 s sample time" + D + "E-scan, 100 samples per peak (Table 2)",
 "Internal Standard Approach": "all: sum normalization, Fe + Ni + Co = 100%" + D + "'In the final step, sum normalization was applied to the major constituents of iron meteorites, specifically Fe + Ni + Co = 100%. This ... eliminated the conventional practice of needing an internal standard'",
 "Internal Standard Element": "all: none" + D + "Fe + Ni + Co sum normalisation",
 "Elemental Fractionation Correction": "N",
 "Uncertainty Propagation Method": "N",
 "Matrix Offset Correction (LIEF)": "N",
 "Pulse/Analog Detector Nonlinearity Correction": "N" + D + "'detector cross-calibration were systematically checked and redone if required'; Fe and Ni measured on low-abundance isotopes in analog mode",
 "Spectral Interference Corrections Applied": "No mathematical correction; isotopes chosen to avoid interferences" + D + "'the molecular species 40Ar61Ni interferes severely at mass 101 ... so a better choice is 99Ru, although it is interfered with by the species 40Ar59Co but much less intensely. All used isotopes (Table 2) were chosen based on the above criteria'",
 "Interfering Species": "⁹⁹Ru: ⁴⁰Ar⁵⁹Co, much less intensely than ⁴⁰Ar⁶¹Ni on ¹⁰¹Ru; other: N" + D + "polyatomic ions from Fe and Ni with plasma species are the main concern",
 "Interference Correction Method": "⁹⁹Ru: isotope selection, avoiding ¹⁰¹Ru; other: N" + D + "isotopes were chosen to be free of elemental isobaric interference",
 "Normalization / Standards-Based Correction": "all: Fe + Ni + Co = 100% sum normalisation after calibration" + D + "the final step of the 3D Trace Elements DRS",
 "Primary Calibration Standard Name": "all [all: NIST SRM 612 and North Chile (Filomena, IIAB)]" + D + "median yield correction factors for NIST SRM 612 relative to North Chile, then least-squares calibration per 15 min block, interpolated in time (3D Trace Elements DRS)",
 "Secondary Reference Materials": "North Chile" + D + "'also measured as an unknown sample several times, on different days, over four months', for intermediate precision; eight other known iron meteorites validate against published INAA values",
}
COL6 = dict(_NAV, **{  # spot analysis
 "Laser Spot Geometry": "all: 150 µm" + D + "Table 2 'spot diameter'",
 "Goodness-of-Fit or Dispersion Statistic": "all: s, standard deviation of n measured values, and RSD" + D + "data table for Figs 2 and 3",
 "Laser Spot Path / Ablation Mode": "all: spot" + D + "Experimental section",
 "Laser Repetition Rate": "all: 10 Hz",
 "Ablation Duration per Spot": "40 s" + D + "'20 s of blank measurement (laser-firing with the shutter closed), followed by 40 s of sample ablation'",
 "Background Count Time": "20 s" + D + "laser firing with the shutter closed, before each ablation",
 "Analysis Sequence": "3 × NIST SRM 612 and 3 × North Chile, then blocks of ten unknowns, each followed by 2 × NIST SRM 612 and 2 × North Chile" + D + "Experimental section",
 "Calibration Standard Measurement Frequency": "Every ten unknowns (about every 15 min)" + D + "calibration blocks bracket blocks of ten unknowns; 'every 15 min calibration block'",
 "Inter-Pass Data Dependency": "N/A" + D + "a single pass",
 "Number of Replicates": "20 spots in Arraias; n per meteorite in Table 3" + D + "'the mean value of 20 spot measurements in the Arraias meteorite'",
 "Signal Integration Interval Method": "N",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "20 s blank before each spot, laser firing with the shutter closed; LODs calculated per acquisition in iolite 4" + D + "Experimental section",
 "Memory Effect Mitigation": "N",
 "Detection Limit": "As: 2; Au: 0.1; Co: 2; Cr: 19; Cu: 0.8; Fe: 60; Ga: 0.3; Ge: 3; Ir: 0.2; Ni: 36; Os: 0.2; Pd: 0.5; Pt: 0.3; Re: 0.1; Rh: 0.1; Ru: 1; W: 1" + D + "µg/g, median values (Table 3 'LOD')",
 "Detection Limit Method": "all: Longerich et al., calculated for each acquisition in iolite 4" + D + "'the LOD must be calculated for each acquisition'; Table 3 gives the medians",
 "Within-Session Analytical Precision and Assessment Method": "N" + D + "precision is stated for samples: RSD <15% for 20 spots in Arraias except Cr (20%), Ir (16%) and Os (20%), and better than 20% for the other meteorites",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "North Chile [all: RSD 20% at worst]" + D + "measured as an unknown over four months; its RSD represents 'the laboratory reproducibility or intermediate precision conditions'",
 "Analytical Accuracy and Assessment Method": "N" + D + "assessed on eight known iron meteorites, not a standard: 'More than 75% of published values are within the respective LA-ICP-MS result ±2s'; relative differences 'almost always within ±20%' (Fig. 2)",
 "Additional Notes": "Two measurement standards complement each other: North Chile for matrix similarity and NIST SRM 612 for its well-known composition; Fe + Ni + Co = 100% normalisation removes the need for an internal standard",
})
COL7 = dict(_NAV, **{  # mapping
 "Laser Spot Geometry": "all: 150 µm² square spot" + D + "as written: 'targeting a 150 μm2 square spot'",
 "Laser Spot Path / Ablation Mode": "all: scanning (elemental mapping)" + D + "Experimental section",
 "Laser Repetition Rate": "all: 10 Hz",
 "Transect Rate, Mapping Rate or Step Size": "all: 10 µm/s" + D + "'scanning at a speed of 10 μm s−1'",
 "Raster Line Spacing (Mapping Only)": "N",
 "Background Count Time": "1 min at the start and at the end of the mapping sequence" + D + "Experimental section",
 "Analysis Sequence": "1 min background, 3 × NIST SRM 612, 3 × North Chile, a 30 min measurement over the unknown area, then 3 × North Chile, 3 × NIST SRM 612 and background" + D + "Experimental section",
 "Calibration Standard Measurement Frequency": "Before and after the 30 min map" + D + "Experimental section",
 "Inter-Pass Data Dependency": "N/A" + D + "a single pass",
 "Number of Replicates": "N",
 "Signal Integration Interval Method": "N",
 "Spike / Outlier Filtering Approach": "N",
 "Blank / Background Correction Method": "1 min background at the start and end of the mapping sequence" + D + "Experimental section",
 "Memory Effect Mitigation": "N",
 "Detection Limit": "N",
 "Detection Limit Method": "N",
 "Within-Session Analytical Precision and Assessment Method": "N",
 "Between-Session (Long-Term) Analytical Precision and Assessment Method": "N",
 "Analytical Accuracy and Assessment Method": "N",
 "Uncertainty Propagation Method": "N",
 "Additional Notes": "Mapping over regions with diverse phases of Augusto Pestana; Fe + Ni + Co = 100% normalisation 'is mandatory when acquiring elemental maps of multiphasic samples'",
})
_FN = [("Instrument Model", None, ["Element XR"]), ("Laser Manufacturer & Model", None, ["Excite 193"]),
       ("Ablation Cell Type", None, ["HelEx"]), ("Laser Pulse Duration", None, ["4 ns"]), ("Laser Fluence (Energy Density)", None, ["7 J"]),
       ("RF Power", None, ["1200 W"]), ("Coolant (Plasma) Gas Flow Rate", None, ["16 L"]), ("Auxiliary Gas Flow Rate", None, ["0.9"]),
       ("Make-up Gas and Flow Rate", None, ["1.1"]), ("Guard Electrode", None, ["on"]), ("Mass Resolution Setting", None, ["300"]),
       ("Detector Configuration", None, ["triple"]), ("Dwell Time per Mass", "all", ["0.02 s"]), ("Data Processing Software(s)", None, ["iolite"]),
       ("Internal Standard Approach", "all", ["Fe + Ni + Co"]), ("Primary Calibration Standard Name", "all/all", ["North Chile"]),
       ("Primary Calibration Standard Name", "all/all", ["NIST SRM 612"]), ("Interfering Species", "⁹⁹Ru", ["⁴⁰Ar⁵⁹Co"])]
FACTS5 = [("Instrument Model", None, ["Element"]), ("Laser Manufacturer & Model", None, ["UP-193"]), ("Mass Resolution Setting", None, ["4000"]),
          ("Laser Spot Geometry", "all", ["75 µm"]), ("Internal Standard Element", "all", ["Mg"]), ("Internal Standard Approach", "all", ["EMPA"]),
          ("Primary Calibration Standard Name", "all/all", ["BCR-2g"]), ("Data Processing Software(s)", None, ["Lee"]),
          ("Spike / Outlier Filtering Approach", None, ["enhanced count rates"]), ("Combination Method", "Mg", ["weighted mean"])] + \
         [("Monitored Masses", m, [m]) for m, _ in MIT]
FACTS6 = _FN + [("Laser Spot Geometry", "all", ["150 µm"]), ("Laser Repetition Rate", "all", ["10 Hz"]), ("Ablation Duration per Spot", None, ["40 s"]),
          ("Background Count Time", None, ["20 s"]), ("Analysis Sequence", None, ["ten unknowns"]), ("Detection Limit", "Fe", ["60"]),
          ("Detection Limit", "Ir", ["0.2"]), ("Number of Replicates", None, ["20"]), ("Secondary Reference Materials", "North Chile", ["North Chile"])] + \
         [("Monitored Masses", m, [m]) for m, _ in NAV]
FACTS7 = _FN + [("Laser Spot Geometry", "all", ["150 µm²"]), ("Transect Rate, Mapping Rate or Step Size", "all", ["10 µm"]),
          ("Analysis Sequence", None, ["30 min"]), ("Background Count Time", None, ["1 min"])]

COL4_ = COL4
COL5 = COL5
# ---- engine
COLS = [  # column number -> label substring (LA-SF order; the U-Pb twin carries the same seven)
 (1, "Zhang et al. 2022 (GCA 323)", COL1), (2, "Pallasite olivine Raster mapping", COL2),
 (3, "Pallasite olivine Line scan", COL3), (4, "Pallasite phosphate", COL4_),
 (5, "Mittlefehldt 2024", COL5), (6, "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot", COL6),
 (7, "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster", COL7),
]
UPB_ONLY = ["Chemical Abrasion Conditions", "Age Calculation Method", "Reported Date Type", "Inherited or Initial Signal Correction",
            "Radiogenic Fraction of Measured Signal", "Age Datum / Reference Epoch", "Intermediate Daughter Disequilibrium Correction",
            "Discordance Definition and Values", "Error Correlation Between Reported Quantities"]
NODATE = "N — the procedure reports no date"
TAPPS = ["LA-SF-ICP-MS_TAPP_v", "LA-SF-ICP-MS_UPb_TAPP_v"]


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
