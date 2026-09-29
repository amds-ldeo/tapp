#!/usr/bin/env python3
"""EPMA pilot of the keyed-value notation (conventions 7.3.4), 2026-09-29.

    python3 "Project Files/Scripts/epma_keyed_pilot_20260929.py" [--apply]

Rewrites every keyed and definer literature cell of EPMA's 15 procedure columns into the notation,
re-reading each source paper (EPMA/*.pdf; Neuman 2025 from XCT/Literature Assessment). Converting a
cell needs the paper, because a bare value must become either `all:` (stated without restriction)
or a list of named members, and the reading turned up extraction errors that are corrected here:

  * inferred values removed (the 2026-09-28 "Defocused" lesson): "Focused" where the paper gives only
    a diameter or no mode (Hu+2020, Liu+2016 both, Seifert+2026, McCoy+2025 both); "Beam Damage
    Minimization" where Liu+2016 gives no reason for its defocused beam; two-point off-peak methods
    where no background method is named;
  * values with no source in the paper: Liu+2016_Cal's counting times and background method (they
    match Ma+2017, same laboratory); Pang+2016's target species; McCoy+2025_SI's silicate/oxide
    element list and the elements attached to its carbonate standards; Frank+2023's secondary RMs
    (San Carlos olivine standardised the SIMS work); Seifert+2026's standard assignments;
  * values the paper states but the cell missed: Ma+2017 counting times; Hu+2020's full detection
    limit list; Liu+2016's section-map conditions (20 nA, focused); Zega+2025's map conditions;
    Broussard+2026's F as a monitored element; Seifert+2026's OH by difference.

Where a stated value cannot be written against the field's key without inference, the cell keeps
the text as commentary and the case is registered in validate_tapp.py (KEYED_CELL_EXCEPTIONS):
  * Ma+2017 detection limits and accuracy are per element; the paper reports oxides;
  * McCoy+2025_UA standards are per phase and element (Mg: Fo92 olivine and rhodonite for phosphate,
    dolomite for carbonate) — the target species key cannot hold them;
  * Zega+2025 counting times are per material — the held counting-time case of gap 1.

Values in a controlled-list field use the Column F spelling ('Ka', not 'Kα'); the paper's own spelling
stays in the commentary quote.

Cells whose field is keyed by session-only domains (the mapping twins) are not parsed, but are
corrected where the reading showed them wrong.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import keyed_cells as K

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "

OXIDES_LIU = "SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, NiO, P2O5, K2O, V2O3, La2O3, Ce2O3"
LIU_TM = ("olivine; pyroxene; Fe-Ti-Cr oxides; maskelynite; phosphate; sulfide; glass" + D +
          "the analytical conditions are given for these groups (p.3)")
LIU_POINT = {
    "Target Material": LIU_TM,
    "Beam Mode": ("maskelynite, phosphate, sulfide, glass: Defocused; other: N" + D + "'Maskelynite, phosphate, "
                  "sulfide, and glass were analyzed using a defocused beam of 5–10 µm size'; for olivine, pyroxene "
                  "and Fe-Ti-Cr oxides only a '1–2 µm beam diameter' is given, not a mode"),
    "Beam Current": ("olivine, pyroxene, Fe-Ti-Cr oxides: 20 nA; maskelynite, phosphate, sulfide, glass: 10 nA"
                     + D + "p.3"),
    "Beam Diameter": ("olivine, pyroxene, Fe-Ti-Cr oxides: 1–2 µm; maskelynite, phosphate, sulfide, glass: 5–10 µm"
                      + D + "p.3"),
    "Beam Damage Minimization": ("N" + D + "a defocused 5–10 µm beam at 10 nA is used for maskelynite, phosphate, "
                                 "sulfide and glass, but the paper gives no reason for it"),
    "Target Species": ("Si, Ti, Al, Mg, Ca, Fe, Mn, Cr, Ni, Na, K, P" + D + "read from the detection-limit sentence, "
                       "which names their oxides (p.3)"),
    "Reported Variables and Units": (OXIDES_LIU + "; modal-area fraction per mineral (vol%); Mg#; En, Fs, Wo" + D +
                                     "oxide wt% 'of selected minerals' (Table 2), with V2O3, La2O3 and Ce2O3 for the "
                                     "oxides and merrillite; glass means with 1σ (Table 3); modal abundances from the "
                                     "X-ray maps (Table 1)"),
    "Detection Limit": ("SiO2, TiO2, Al2O3, MgO, CaO: <0.03 wt%; FeO, MnO, Cr2O3, NiO, Na2O, K2O, P2O5: <0.05–0.1 wt%; "
                        "other: N" + D + "'Detection limits are typically <0.03 wt% for SiO2, TiO2, Al2O3, MgO, and "
                        "CaO; <0.05–0.1 wt% for FeO, MnO, Cr2O3, NiO, Na2O, K2O, and P2O5' (p.3)"),
}
NOT_NAMED_BG = "N" + D + "no background method is named"

EDITS = {
  "Ma+2015": {
    "Target Material": ("tissintite; maskelynite; pigeonite; fayalite" + D + "Table 1: wormy and rimming tissintite, "
                        "associated maskelynite, pigeonite and fayalite surrounding tissintite"),
    "Beam Mode": "all: Focused" + D + "'WDS: 15 kV; 5 nA; beam in focused mode' (p.3)",
    "Beam Current": "all: 5 nA" + D + "p.3",
    "Beam Diameter": "N" + D + "'beam in focused mode' is recorded under Beam Mode; no diameter is given",
    "Target Species": "Si, Ti, Al, Cr, Fe, Mn, Mg, Ca, Na, K" + D + "from the standards sentence (p.3)",
    "Reported Variables and Units": ("SiO2, TiO2, Al2O3, FeO, MgO, CaO, Na2O, K2O, Cr2O3, MnO; cations per formula "
                                     "unit; Ca/(Ca+Na+K); Ca-Eskola component; An content of the precursor plagioclase"
                                     + D + "oxide wt% with totals and 1 s.d. of the mean, cations on 6 or 8 oxygens "
                                     "(Table 1); Ca-Eskola (mol%) and An58–69 (p.1)"),
    "X-ray Detection Method per Monitored Element": "all: WDS" + D + "'WDS: 15 kV; 5 nA'",
    "X-ray Line": ("Si, Al, Ca, Na, Fe, Mg, Mn, Ti, Cr, K: Ka" + D + "'anorthite (SiKα, AlKα, CaKα); albite (NaKα); "
                   "fayalite (FeKα); forsterite (MgKα); Mn2SiO4 (MnKα); TiO2 (TiKα); Cr2O3 (CrKα); and microcline (KKα)'"),
    "Primary Calibration Standard Name": ("Si, Al, Ca: anorthite; Na: albite; Fe: fayalite; Mg: forsterite; "
                                          "Mn: Mn2SiO4; Ti: TiO2; Cr: Cr2O3; K: microcline" + D + "p.3"),
    "Detection Limit": ("K2O: 0.02 wt% K; Cr2O3: 0.05 wt% Cr; MnO: 0.06 wt% Mn; other: N" + D + "Table 1 footnote c, "
                        "attached to the b.d. entries of the K2O, Cr2O3 and MnO rows: 'b.d. = below detection limit: "
                        "0.02 wt% K, 0.05 wt% Cr, 0.06 wt% Mn'"),
  },
  "Hu+2020": {
    "Target Material": ("maskelynite; melt inclusion glasses; silica glasses; coesite aggregates; mesostasis" + D +
                        "'Quantitative analyses of maskelynite, melt inclusion glasses, silica glasses, coesite "
                        "aggregates, and mesostasis were conducted by EPMA' (p.2)"),
    "Beam Mode": "N" + D + "only 15 kV and 10 nA are given",
    "Beam Current": "all: 10 nA" + D + "'The accelerating voltage was 15 kV, and the beam current was 10 nA'",
    "Beam Diameter": "N" + D + "only 15 kV and 10 nA are given",
    "Reported Variables and Units": ("SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, K2O" + D + "oxide wt% for "
                                     "maskelynite, melt inclusion glasses, silica glasses, coesite aggregates and "
                                     "mesostasis (p.2)"),
    "X-ray Line": "Mn: Ka; other: N" + D + "'X-ray interference of the Ka line of Mn by the Kb line of Cr was corrected'",
    "Primary Calibration Standard Name": ("Si, Mg, Fe: natural kaersutite; Na, Al: jadeite; Ca, Mn: bustamite; "
                                          "K: K-feldspar; Ti: synthetic rutile; Cr: Cr2O3" + D + "p.2"),
    "X-ray Line Overlap Corrections Applied": ("Mn: Yes; other: N" + D + "'X-ray interference of the Ka line of Mn by "
                                               "the Kb line of Cr was corrected'"),
    "Interfering Elements": "Mn: Cr Kb; other: N" + D + "as above",
    "Detection Limit": ("K2O: 0.01 wt%; SiO2, Al2O3, MgO, CaO, Na2O: 0.02 wt%; TiO2, Cr2O3: 0.03 wt%; FeO: 0.05 wt%; "
                        "MnO: 0.06 wt%" + D + "p.2"),
  },
  "Liu+2016_UT": dict(LIU_POINT, **{
    "Monitored Elements": ("Si, Ti, Al, Mg, Ca, Fe, Mn, Cr, Ni, Na, K, P" + D + "point analyses on both instruments "
                           "(the detection-limit sentence names their oxides); maps: 'Ca Ka, Al Ka, Fe Ka, and Mg Ka' "
                           "(four sections) and 'Fe Ka, P Ka, Al Ka, Ca Ka, and Cr Ka' (two olivine megacrysts, "
                           "collected on 'the EMP' — the instrument is not named)"),
    "Dwell Time per Pixel": ("Fe, P, Al, Ca, Cr: ~0.5 s; other: N" + D + "'a dwell time of ~0.5 s at each step' for "
                             "the olivine megacryst maps; the section-map dwell time is not stated"),
    "Mapping Beam Mode": "Focused (section maps and olivine megacryst maps)" + D + "'a 20 nA focused beam'; 'a focused beam of 15 kV voltage and 200 nA current'",
    "Mapping Beam Current": "20 nA (section maps: Ca, Al, Fe, Mg Kα); 200 nA (olivine megacryst maps)" + D + "p.3",
  }),
  "Liu+2016_Cal": dict(LIU_POINT, **{
    "Peak Counting Time": ("N" + D + "Liu 2016 states no counting times; the earlier values matched Ma+2017 (same "
                           "laboratory) and had no source in this paper"),
    "Background Counting Time": "N" + D + "as for Peak Counting Time",
    "Background Position(s)": "N" + D + "as for Peak Counting Time",
    "X-ray Background Correction Method": NOT_NAMED_BG,
  }),
  "Ma+2017": {
    "Target Material": ("liebermannite; lingunite; maskelynite" + D + "Table 1: 'Analytical data for liebermannite and "
                        "associated lingunite and maskelynite'"),
    "Beam Mode": "all: Focused" + D + "'WDS: 15 kV, 5 nA, beam in focused mode' (p.2)",
    "Beam Current": "all: 5 nA" + D + "p.2",
    "Beam Diameter": "N" + D + "'beam in focused mode' is recorded under Beam Mode; no diameter is given",
    "Beam Damage Minimization": ("all: low beam current (5 nA)" + D + "'Although a low beam current of 5 nA was used "
                                 "for the analysis, the low cation sum (0.92) for the K-site is likely due to diffusion "
                                 "of Na away from the electron beam' (p.3)"),
    "Reported Variables and Units": ("SiO2, TiO2, Al2O3, FeO, CaO, Na2O, K2O; cations per formula unit; density" + D +
                                     "oxide wt% with totals and 1 s.d. of the mean, cations on 8 oxygens (Table 1); "
                                     "'Magnesium, Cr, and Mn were also analyzed but were below the detection limit in "
                                     "all cases'; calculated density 3.98 g cm-3 (p.3)"),
    "X-ray Detection Method per Monitored Element": "all: WDS" + D + "'WDS: 15 kV, 5 nA'",
    "X-ray Line": ("Si, Al, K, Ca, Na, Fe, Mg, Ti, Cr, Mn: Ka" + D + "'Asbestos microcline (SiKa, AlKa, KKa), synthetic "
                   "anorthite (CaKa), Amelia albite (NaKa), synthetic fayalite (FeKa), synthetic forsterite (MgKa), "
                   "synthetic TiO2 (TiKa), synthetic Cr2O3 (CrKa), and synthetic Mn-olivine (MnKa)'"),
    "Primary Calibration Standard Name": ("Si, Al, K: Asbestos microcline; Ca: synthetic anorthite; Na: Amelia albite; "
                                          "Fe: synthetic fayalite; Mg: synthetic forsterite; Ti: synthetic TiO2; "
                                          "Cr: synthetic Cr2O3; Mn: synthetic Mn-olivine" + D + "p.2"),
    "Peak Counting Time": ("all: 20 s" + D + "'Counting times were 20 s on-peak and 10 s each on high and low "
                           "background positions' (p.2)"),
    "Background Counting Time": "all: 10 s on each of the high and low background positions" + D + "as above",
    "Background Position(s)": "all: high and low" + D + "'high and low background positions'; offsets not given",
    "Secondary Reference Materials": "feldspar standards" + D + "'based on analysis of feldspar standards as unknowns'; not named individually",
    "Detection Limit": ("Si: 0.05 wt%; Ti: 0.04 wt%; Al: 0.06 wt%; Fe: 0.06 wt%; Mg: 0.02 wt%; Ca: 0.02 wt%; "
                        "Na: 0.03 wt%; K: 0.02 wt%; Cr: 0.05 wt%; Mn: 0.06 wt%" + D + "'The detection limits (wt%) are "
                        "0.05 Si, 0.04 Ti, ...' (p.2) — stated per element, while Table 1 reports oxides"),
    "Analytical Accuracy": ("feldspar standards [Si, Al, Ca, Na, K: 1–2%; other: N]" + D + "'The accuracy is 1–2% for "
                            "Si, Al, Ca, Na, and K, based on analysis of feldspar standards as unknowns' — per element, "
                            "while Table 1 reports oxides"),
  },
  "Frank+2023": {
    "Target Material": "melilite; spinel; grossmanite" + D + "Table 1: 'Chemical compositions for the major minerals in the Ivuna CAI'",
    "Beam Mode": "all: Focused" + D + "'Analyses were performed at 20 kV and 20 nA using a focused beam of 1 μm' (p.3)",
    "Beam Current": "all: 20 nA" + D + "p.3",
    "Beam Diameter": "all: 1 µm" + D + "p.3",
    "Reported Variables and Units": ("SO2, P2O5, Na2O, K2O, MgO, Al2O3, SiO2, CaO, TiO2, V2O3, FeO, Cr2O3, MnO, NiO; "
                                     "åkermanite content" + D + "oxide wt% with totals (Table 1); Åk14–31 (p.5)"),
    "Peak Counting Time": "all: 10–50 s" + D + "'Peak count times were 10–50 s' — a range; per-element times not given",
    "Primary Calibration Standard Name": ("Si, Al, Ti, K, Na, Fe, Mg, Ca: Kakanui kaersutite; S: Canyon Diablo "
                                          "troilite; Mn: rhodonite; Cr: chromium metal; Ni: nickel metal; P: apatite; "
                                          "V: vanadium metal" + D + "pp.3–4"),
    "Secondary Reference Materials": ("N" + D + "no EPMA secondary standard is named; San Carlos olivine standardised "
                                      "the SIMS oxygen-isotope measurements, and Kakanui kaersutite is a primary standard"),
    "Detection Limit": ("Al2O3, K2O, CaO: 0.03–0.04 wt%; Na2O, MgO, SiO2, FeO, MnO: 0.05 wt%; P2O5, SO2, TiO2, V2O3, "
                        "Cr2O3, NiO: 0.06–0.09 wt%" + D + "'typically' (p.4)"),
  },
  "Broussard+2026": {
    "Target Material": ("phyllosilicate (matrix); oxide (magnetite, ilmenite); sulfide (pyrrhotite, pentlandite); "
                        "carbonate (dolomite, magnesite); phosphate (Ca phosphate, Na-Mg hydrous phosphate)" + D +
                        "phases analysed and mapped by EPMA (results)"),
    "Beam Current": "all: 25 nA" + D + "'15 kV accelerating potential and 25 nA probe current for point analysis'",
    "Target Species": ("F, O, CO2, H2O" + D + "F measured; 'Oxygen was calculated by elemental stoichiometry with water "
                       "estimated by inspection of the analytical total, and for carbonates, CO2 was calculated by "
                       "stoichiometry'; the other analysed elements are not named"),
    "Monitored Elements": "F" + D + "'Fluorine measurement was made using the LDE1 diffracting crystal'; no other element is named",
    "X-ray Detection Method per Monitored Element": "all: WDS" + D + "'wavelength-dispersive quantitative compositional mapping and analysis'",
    "Diffracting Crystal": "F: LDE1" + D + "p.3",
    "X-ray Background Correction Method": ("F: polynomial fit to the background determined on representative phases; "
                                           "other: Mean Atomic Number (MAN)" + D + "'the mean atomic number (MAN) "
                                           "background calibration was made using these standards'"),
    "Target Species Estimation Method": ("O, CO2: Stoichiometry from cations; H2O: estimated by inspection of the "
                                         "analytical total; F: Direct (measured)" + D + "p.3"),
    "Primary Calibration Standard Name": ("F: synthetic F-phlogopite; other: N" + D + "'natural and synthetic minerals "
                                          "routinely used in the analytical facility'"),
  },
  "Seifert+2026": {
    "Beam Mode": "N" + D + "'a 2μm probe size' is recorded under Beam Diameter; no mode is named",
    "Beam Current": "all: 20 nA" + D + "'14 analyses were performed at 15kV, 20nA, using a 2μm probe size'",
    "Beam Diameter": "all: 2 µm" + D + "as above",
    "Beam Damage Minimization": ("all: Durango apatite compared at 10 μm and 3 μm spot sizes, with no significant "
                                 "volatile loss" + D + "'in order to assess volatilization of halogens using our beam conditions'"),
    "Target Species": ("P, F, Cl, Ca, Mn, Fe, Na, Mg, Si, S, OH" + D + "the ten elements analysed (p.3); OH "
                       "'calculated by difference based on 1–F–Cl=OH' (p.4)"),
    "Reported Variables and Units": ("F, Cl, Na2O, MgO, SiO2, SO3, P2O5, CaO, MnO, FeO" + D + "wt% with totals, per "
                                     "named grain (Table 1)"),
    "Target Species Estimation Method": ("OH: By difference; other: Direct (measured)" + D + "'Hydroxyl was not measured "
                                         "directly in this study and therefore was calculated by difference based on "
                                         "1–F–Cl=OH'; formulae on 13 anions (Ketcham 2015)"),
    "Primary Calibration Standard Name": ("F: SrF2; Na: albite; Mg: SW olivine; Si: quartz; P, Ca: Wilburforce apatite; "
                                          "S: barite; Cl: tugtupite; Mn: rhodonite; Fe: ilmenite" + D + "p.3"),
  },
  "Pang+2016": {
    "Target Material": ("plagioclase and its polymorphs" + D + "'Measurements of most minerals were performed with a "
                        "focused beam ... whereas measurements of plagioclase and its polymorphs were performed with a "
                        "defocused beam'; the other minerals are not listed (EPMA data in Supplementary Table 4)"),
    "Beam Mode": "plagioclase and its polymorphs: Defocused; other: Focused" + D + "Methods",
    "Beam Current": "all: 20 nA" + D + "'a focused beam of 20nA ... at the same beam current'",
    "Beam Diameter": "plagioclase and its polymorphs: 2–5 µm; other: N" + D + "'a defocused beam (2–5 μm in diameter)'",
    "Target Species": ("N" + D + "no element is named in the paper; the analysed elements are in Supplementary Table 4, "
                       "which is not in the archived PDF"),
    "Reported Variables and Units": ("En, Fs, Wo; Ca-Eskola component; empirical formulae" + D + "mol% (p.2, p.4); "
                                     "the oxide analyses are in Supplementary Tables 1–4, not in the archived PDF"),
    "X-ray Detection Method per Monitored Element": "all: WDS" + D + "'JEOL8100 ... with wavelength dispersive spectrometers (WDS)'",
    "Primary Calibration Standard Name": "N" + D + "'Natural and synthetic standards were used'",
    "Detection Limit": "all: better than 0.02 wt% (typical)" + D + "'Typical detection limits for oxides of most elements were better than 0.02 wt%'",
  },
  "McCoy+2025_SI": {
    "Target Material": ("carbonate; magnetite; olivine" + D + "'Carbonate analyses were run at 15 kV and 10 nA ...; "
                        "analyses of magnetite and olivine were run under the same conditions' (p.7)"),
    "Beam Mode": "N" + D + "only spot sizes are given",
    "Beam Current": "all: 10 nA" + D + "p.7",
    "Beam Diameter": ("carbonate: 5 µm; magnetite, olivine: 1 µm" + D + "'with an analytical spot size of 5 µm' "
                      "(carbonates); 'Analyses were conducted at 15kV and 10nA, with an analytical spot size of 1µm' "
                      "(the magnetite and olivine sentence)"),
    "Target Species": ("Fe, Mn, Mg, Ca" + D + "the carbonate analyses, named with their crystals; the elements of the "
                       "magnetite and olivine analyses are not named"),
    "Diffracting Crystal": "Fe, Mn: LIFL; Mg: TAPL; Ca: PETL" + D + "p.7",
    "Primary Calibration Standard Name": ("N" + D + "standards are named without their elements: magnetite (USNM "
                                          "114887), calcite (USNM 13621), dolomite (USNM 10057), siderite (R-2460) and "
                                          "rhodonite (carbonates); chromite (USNM 117075), ilmenite (USNM 96189), "
                                          "magnetite (USNM 114887), manganite (USNM 157872), bytownite (R-2912), "
                                          "forsterite (P140), San Carlos olivine (USNM 111312/444) and Springwater "
                                          "olivine (USNM 2566) (magnetite and olivine)"),
    "Secondary Reference Materials": ("calcite, dolomite, rhodochrosite, magnetite, San Carlos olivine, Springwater "
                                      "olivine" + D + "carbonates: calcite, dolomite and rhodochrosite; magnetite and "
                                      "olivine: magnetite, San Carlos olivine and Springwater olivine (p.7)"),
  },
  "McCoy+2025_UA": {
    "Target Material": "\"Mg,Na phosphate\"; carbonate" + D + "p.7",
    "Beam Mode": "N" + D + "only a '1-µm beam size' is given, for the phosphate analyses",
    "Beam Current": "\"Mg,Na phosphate\": 8 nA; other: N" + D + "carbonate conditions are not stated",
    "Beam Diameter": "\"Mg,Na phosphate\": 1 µm; other: N" + D + "'using a 1-µm beam size'",
    "Target Species": ("F, P, Ca, Si, Mg, Fe, Al, S, K, Cl, Na, Mn" + D + "phosphate standards name F, P, Ca, Si, Mg, "
                       "Fe, Al, S, K, Cl; carbonate standards name Na, Si, Mg, Ca, Mn, P, S, Fe"),
    "Monitored Elements": "F, P, Ca, Si, Mg, Fe, Al, S, K, Cl, Na, Mn" + D + "as for Target Species",
    "X-ray Detection Method per Monitored Element": ("F, P, Ca, Si, Mg, Fe, Al, S, K, Cl: WDS; other: N" + D +
                                                     "'Wavelength-dispersive X-ray spectroscopy analyses of Mg,Na "
                                                     "phosphate'; stated for the phosphate analyses only"),
    "Primary Calibration Standard Name": ("N" + D + "standards are stated per phase and element, so one element has "
                                          "several: 'fluorapatite (F, P, Ca), Fo92 olivine (Si, Mg), rhodonite (Mg), "
                                          "fayalite (Fe), anorthite (Al), baryte (S), potassium feldspar (K) and "
                                          "scapolite (Cl)' for Mg,Na phosphate; 'albite (Na), Fo92 olivine (Si), "
                                          "dolomite (Mg), calcite (Ca), Mn carbonate (Mn), apatite (P), baryte (S) and "
                                          "fayalite (Fe)' for carbonates"),
    "Reported Variables and Units": ("N" + D + "phosphate and carbonate compositions are reported by phase (p.2); the "
                                     "quantitative analyses are in the supplementary tables, not in the archived PDF"),
  },
  "Zega+2025": {
    "Target Material": "silicates; sulfides; oxides; phosphates; carbonates" + D + "p.9",
    "Beam Mode": ("silicates, sulfides, oxides: Focused; phosphates, carbonates: Defocused" + D + "'Quantitative "
                  "analyses of silicates, sulfides and oxides were run using a focused beam ... A 2-μm defocused beam "
                  "size ... for phosphate and carbonate analyses'"),
    "Beam Current": "silicates, sulfides, oxides: 20 nA; phosphates: 8 nA; carbonates: 4 nA" + D + "p.9",
    "Beam Diameter": "phosphates, carbonates: 2 µm; other: N" + D + "p.9",
    "Beam Damage Minimization": ("phosphates, carbonates: 2 µm defocused beam, lower beam currents and shorter count "
                                 "times; other: N" + D + "'to minimize possible beam damage effects'"),
    "Reported Variables and Units": ("Fe + Co, S, Ni; modal abundance of carbonates, sulfides and magnetite" + D +
                                     "sulfide compositions in at% (Fig. 1); modal abundances '0.4–3.4%, ~3–8% and ~3–5%' "
                                     "from the EMPA phase maps (p.2)"),
    "Peak Counting Time": ("N" + D + "stated per material, not per element, and no element is named: '20 s peak time' "
                           "(silicates, sulfides, oxides), '20 s peak' (phosphates), '10 s peak' (carbonates)"),
    "Background Counting Time": ("N" + D + "stated per material: '10 s on each background' (silicates, sulfides, "
                                 "oxides), '10 s background' (phosphates), '5 s background' (carbonates)"),
    "Background Position(s)": "N" + D + "'10 s on each background' implies two positions, which are not given",
    "X-ray Background Correction Method": NOT_NAMED_BG,
    "Primary Calibration Standard Name": "N" + D + "'Well-characterized natural and synthetic materials were used as standards'",
    "Mapping Beam Current": "20 nA" + D + "'X-ray maps and BSE images were run at 15kV and 20nA'",
  },
  "Barnes+2025#JEOL": {
    "Target Material": ("carbonates" + D + "'Quantitative chemical analyses ... to determine the chemical compositions "
                        "of minerals'; carbonates are the only material named with conditions of their own"),
    "Beam Mode": "carbonates: Rastered; other: N" + D + "'For carbonates, we rastered the beam over 5×5 µm2'",
    "Beam Current": "all: 10 nA" + D + "'an accelerating voltage of 20 kV, a probe current of 10 nA and beam diameter of 1 µm'",
    "Beam Diameter": "all: 1 µm" + D + "as above",
    "Beam Raster Dimensions": "carbonates: 5 × 5 µm²; other: N/A" + D + "as above",
    "Target Species": ("Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe, Si, Na, K" + D + "'(1) Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe and Si "
                       "(session 1) and (2) Na, K, Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe and Si (session 2)' (p.11)"),
    "Monitored Elements": "Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe, Si, Na, K" + D + "as for Target Species",
    "Reported Variables and Units": ("Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe, Si, Na, K" + D + "mineral compositions for the "
                                     "two element suites; values 'compiled in Supplementary Table 14', not in the "
                                     "archived PDF"),
    "Peak Counting Time": ("Al, Ti, Ca, Mn, Cr: 200 ms total (peak + background); Mg, Fe, Si: 20 ms total (peak + "
                           "background); other: N" + D + "'The total peak + background counting time was 200 ms for "
                           "Al, Ti, Ca, Mn and Cr, and 20 ms for Mg, Fe and Si'"),
    "Background Counting Time": "N" + D + "only the total peak + background time is stated (see Peak Counting Time)",
    "Primary Calibration Standard Name": ("Mg, Si: Springwater olivine; Fe: fayalite; Ca: wollastonite; Na, Al: albite; "
                                          "K: orthoclase; Ti: rutile; Ni: Ni metal; Cr: chromite; Mn: rhodochrosite"
                                          + D + "p.11"),
    "Detection Limit": ("Mg: 0.025 wt%; Fe: 0.025 wt%; Si, K, Na: 0.05 wt%; Ca: 0.005 wt%; Al: 0.02 wt%; Ti: 0.005 wt%; "
                        "Cr: 0.015 wt%; Mn: 0.008 wt%; other: N" + D + "p.11"),
  },
  "Barnes+2025#Cameca": {
    "Target Material": "olivine; pyroxene" + D + "'Olivine and pyroxene grains were identified and characterized at the NHM' (p.13)",
    "Beam Mode": "all: Focused" + D + "'Analyses were performed at 20 kV, using a focused 1-μm beam'",
    "Beam Diameter": "all: 1 µm" + D + "as above",
    "Reported Variables and Units": ("major and minor element abundances; Mg#" + D + "'Major and minor element abundances' "
                                     "of olivine and pyroxene; 'the Mg# of olivine grains is >83' (p.13)"),
    "Detection Limit": ("N" + D + "'Typical detection limits for transition metals were around 250 ppm'; the elements "
                        "are not named"),
  },
  "Neuman+2025": {
    "Target Material": "lunar regolith (Apollo 17 double drive tube, lower section 73001)" + D + "as continuous thin sections",
    "Beam Raster Dimensions": "N/A" + D + "stage scan, not beam scan",
    "Monitored Elements": ("Mg, Al, Fe, Ca, Ti, Na, Si, Mn, K, Cr" + D + "'Two passes were used to collect X-ray "
                           "intensities for Mg, Al, Fe, Ca, and Ti in pass 1, and Na, Si, Mn, K, and Cr in pass 2' (p.6)"),
    "Reported Variables and Units": ("element wt% maps; oxide wt% maps; cation stoichiometry; mineral endmember maps"
                                     + D + "32-bit floating point .tiff"),
    "X-ray Detection Method per Monitored Element": "all: WDS" + D + "p.6",
    "WDS Spectrometer Channel": "N" + D + "spectrometer-to-element assignments are not stated",
    "Sequence": ("Mg, Al, Fe, Ca, Ti: pass 1; Na, Si, Mn, K, Cr: pass 2" + D + "'Two passes were used to collect X-ray "
                 "intensities for Mg, Al, Fe, Ca, and Ti in pass 1, and Na, Si, Mn, K, and Cr in pass 2'"),
    "Peak Counting Time": "N/A" + D + "mapping-only procedure; the 25 msec per-pixel dwell is under Dwell Time per Pixel",
    "Background Counting Time": "N/A" + D + "MAN background calibration; no off-peak counting",
    "Background Position(s)": "N/A" + D + "MAN background calibration; no off-peak positions",
    "Dwell Time per Pixel": ("all: 25 msec" + D + "the MAN background correction 'allows all map collection time to be "
                             "dedicated to on-peak X-ray measurement'"),
    "X-ray Background Correction Method": ("all: Mean Atomic Number (MAN)" + D + "MAN background calibration, using "
                                           "'EPMA standards having a range of average atomic number Z'"),
    "Normalization / Standards-Based Correction": ("all: k-ratio against the calibration standard" + D + "k = "
                                                   "(P-B)smp / (P-B)std, the background-corrected relative peak X-ray "
                                                   "intensity at each pixel compared to the calibration standard"),
    "Primary Calibration Standard Name": ("N" + D + "'EPMA standards having a range of average atomic number Z' are used "
                                          "for the MAN background calibration; individual standards not named"),
    "Detection Limit": "all: 0.1–0.2 element wt%" + D + "'for all elements in this map set'",
    "Detection Limit Method": ("N" + D + "attributed to the MAN background correction dedicating all map collection "
                               "time to on-peak measurement, 'which improves precision and detection limits'"),
  },
}


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


def columns(h):
    """Column key -> index. The two Barnes+2025 columns are told apart by instrument."""
    s = h.index("Literature Assessment"); out = {}
    for j in range(s + 1, len(h)):
        lab = h[j].replace("\n", " ")
        if not lab.strip():
            continue
        key = lab.split("|")[0].strip()
        if key == "Barnes+2025":
            key += "#JEOL" if "JEOL" in lab else "#Cameca"
        assert key not in out, key
        out[key] = j
    return out


def edit(rr, report):
    h = rr[0]; cols = columns(h)
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    n = 0
    for colkey, fields in EDITS.items():
        j = cols[colkey]
        for f, v in fields.items():
            r = by[f]
            if r[j] != v:
                report.append((colkey, f, r[j], v)); r[j] = v; n += 1
    return rr, n


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith("EPMA_TAPP_v"))
    rel = e["tapp"]
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
    report = []
    rr, n = edit(rows_of(os.path.join(ROOT, rel)), report)
    print("  %s -> %s: %d cells rewritten" % (os.path.basename(rel), os.path.basename(new), n))
    if "--show" in sys.argv:
        for c, f, old, v in report:
            print("\n[%s] %s\n  was: %s\n  now: %s" % (c, f, old, v))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change)"); return 0
    np_ = os.path.join(ROOT, new)
    q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                       + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
    rr, _ = edit(rows_of(np_), [])
    write(np_, rr)
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
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
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
