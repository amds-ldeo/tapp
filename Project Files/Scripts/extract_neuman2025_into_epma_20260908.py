#!/usr/bin/env python3
"""Phase 3: extract Neuman et al. 2025 (JGR Planets 130, e2024JE008556) into the EPMA TAPP.

The paper was already extracted into Lab-XCT for its XCT content; its section 2.6 "Electron Microprobe
Quantitative Imaging" is a method-grade EPMA description that had never been extracted. It is also the
evidence that EPMA acquires in multiple passes (Proposal_Acquisition_Pass_2026-09-08 section 4C).

Every value below traces to a sentence in section 2.6 or 2.2 read in the session that wrote this file,
per the Source Rule in lit_assessment.md. `N` = applicable but not stated; `N/A` = does not apply.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
SRC = os.path.join(ROOT, "EPMA", "EPMA_TAPP_v61.csv")
DST = os.path.join(ROOT, "EPMA", "EPMA_TAPP_v62.csv")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-08"
HEADER = "Neuman+2025\n| WashU St. Louis\n| WDS Mapping (JEOL JXA-8200)"

V = {
# --- 1. Procedure Identification -------------------------------------------------
"Procedure Name": "EPMA-WDS quantitative compositional mapping, Apollo 17 core 73001 continuous thin sections (Washington University in St. Louis)",
"Technique": "EPMA-WDS",
"Procedure Author": "N (no individual operator named for the EPMA work)",
"Laboratory": "Washington University in St. Louis",
"Laboratory ID": "N",
"Procedure Start Date": "N",
"Funding Source for Procedure Development": "N",
"Procedure Reference(s)": "Neuman et al. 2025, J. Geophys. Res. Planets 130, e2024JE008556; doi:10.1029/2024JE008556 (section 2.6)",
"Procedure DOI": "N",
"Session Identifier": "N",
"Analyst": "N",
"Analysis Start Date": "N",
"Analysis End Date": "N",
"Funding Source for Analysis": "N",
"Coupled Technique(s)": "BSE mosaic imaging (same JEOL JXA-8200); QEMSCAN (FEI QUANTA 650 FEG-SEM, Univ. Manchester); optical microscopy (Keyence VHX 7000, NASA JSC); micro-XCT (custom NSI instrument, UTCT)",
"Coupling Description": "Single-element and RGB composite X-ray maps are compared with BSE and optical image mosaics (reflected light, plane polarized, crossed polars) to discriminate crystalline from glassy phases; an Al-Mg-Fe RGB composite X-ray map is used to discriminate feldspathic (red) from ferromagnesian (green and blue) phases",
"Coupled Procedure DOI": "N",
"Coupled Dataset or Publication Reference": "N",
# --- 2. Samples ------------------------------------------------------------------
"Target Material": "Lunar regolith (Apollo 17 double drive tube, lower section 73001), as continuous thin sections",
"Sample Preparation Method": "Core extruded and dissected in 0.5 cm depth intervals; the remaining material impregnated with epoxy to create a continuous thin section set of the entire core; sections are 50 x 25 mm. Carbon coating N",
"Sample Name": "73001,6014-73001,6021",
"Sampling Unit": "Analysis point - each map pixel is a fully quantitative analysis (1,024 x 1,024 per stage map; five stage maps per thin section; 20 x 10^6 analyses across all slides)",
"Sample Persistent Identifier": "N (NASA curation sample numbers given as names; not stated as persistent identifiers)",
"Sampling Unit Selection Criteria": "N - continuous thin sections of the whole core; five stage maps per section, no selection rule stated",
"Pre-Analysis Imaging and Screening": "BSE mosaic: approximately 325 backscattered-electron images collected with the JEOL guide-net mapping software at 15 kV, 2 nA probe current and 70x magnification, stitched with the ImageJ Fiji grid-collection stitching plug-in (Donovan et al., 2021) into a 20k x 5k pixel mosaic at ~1.5 um pixel resolution",
# --- 3. Instrument & Software ----------------------------------------------------
"Instrument Manufacturer": "JEOL",
"Instrument Model": "JEOL JXA-8200",
"Electron Source": "N",
"Acquisition Software": "JEOL guide-net mapping software (BSE mosaic); N for the WDS stage maps",
"Data Processing Software(s)": "Probe Software CalcImage and Probe for EPMA (full Phi(rho-z) correction at each pixel); MATLAB routines generating 32-bit floating point .tiff quantitative maps; Fiji and MATLAB for stitching; ENVI input image stacks",
"WDS Spectrometer Configuration": "Fixed wavelength-dispersive spectrometers; count not stated (five elements collected per pass)",
"EDS Detector Configuration": "N/A - WDS mapping; no EDS used for the EPMA work",
# --- 4. Measurement Information --------------------------------------------------
"Analytical Mode": "WDS Mapping",
"Beam Mode": "Fixed 10 um beam (stated 'a fixed 10 um electron beam')",
"Accelerating Voltage": "15 kV (stage maps and BSE mosaic)",
"Beam Current": "100 nA probe current (stage maps); 2 nA (BSE mosaic)",
"Beam Diameter": "10 um (fixed)",
"Beam Raster Dimensions": "N/A - stage scan, not beam scan",
"Beam Damage Minimization": "N",
"Drift Correction": "N",
"Target Species": "Mg, Al, Fe, Ca, Ti, Na, Si, Mn, K, Cr (ten elements, collected in two passes)",
"Reported Variables and Units": "Quantitative element and oxide wt.% maps; cation stoichiometry; derived mineral endmember maps (32-bit floating point .tiff)",
"EPMA Technique per Target Species": "WDS (all ten elements)",
"X-ray Line": "N",
"Diffracting Crystal": "N",
"WDS Spectrometer Channel": "N - spectrometer-to-element assignments not stated",
"Sequence": "Two passes per stage map: pass 1 = Mg, Al, Fe, Ca, Ti; pass 2 = Na, Si, Mn, K, Cr",
"Proportional Counter / Detector": "N",
"WDS PHA Setting": "N",
"Peak Counting Time": "25 msec dwell per pixel, all on-peak - the MAN background correction 'allows all map collection time to be dedicated to on-peak X-ray measurement'",
"Background Counting Time": "N/A - MAN (mean atomic number) background calibration; no off-peak counting",
"Background Position(s)": "N/A - MAN background calibration; no off-peak positions",
"EDS Live Time per Point or Pixel": "N/A",
"EDS Acquisition Mode": "N/A",
"Dwell Time per Pixel": "25 msec",
"Step Size / Pixel Size": "9.5 um (stage maps); ~1.5 um per pixel (BSE mosaic)",
"Map Dimensions": "1,024 x 1,024 pixels per stage map; five stage maps per thin section",
"Map Area": "N - not stated directly (1,024 pixels at 9.5 um step corresponds to ~9.7 mm per side)",
"Stage Scan vs. Beam Scan": "Stage scan (stated 'EPMA stage maps')",
# --- 5. Data Processing ----------------------------------------------------------
"Matrix Correction Method": "Full Phi(rho-z) correction applied at each pixel, of the form C = k x ZAF, where ZAF is the compositionally dependent correction for atomic number, X-ray absorption and characteristic fluorescence in both sample and standard",
"Mass Absorption Coefficients (MACs)": "N",
"X-ray Background Correction Method": "MAN (mean atomic number) background calibration, using EPMA standards spanning a range of average atomic number Z",
"Time-Dependent Intensity Correction": "N",
"Target Species Estimation Method": "N",
"Halogen Correction on Oxygen": "N/A",
"WDS Dead Time Correction": "N",
"EDS Spectral Processing Type": "N/A",
"Blank Correction": "N",
"Normalization / Standards-Based Correction": "k-ratio against the calibration standard: k = (P-B)smp / (P-B)std, the background-corrected relative peak X-ray intensity at each pixel compared to the calibration standard",
"Calibration Factor and Determination Method": "N",
"Procedural Blank Level": "N/A",
"Analysis Inclusion and Rejection Criteria": "N",
"Constants and Reference Values Used": "N",
# --- 6. Quality Control & Uncertainty --------------------------------------------
"Primary Calibration Standard Name": "N - 'EPMA standards having a range of average atomic number Z' are used for the MAN background calibration; individual standards not named",
"Secondary Reference Materials": "N",
"X-ray Line Overlap Corrections Applied": "N",
"Interfering Elements": "N",
"Interference Correction Standard": "N",
"Detection Limit": "0.1-0.2 element wt.% for all elements in this map set",
"Detection Limit Method": "N - attributed to the MAN background correction dedicating all map collection time to on-peak measurement, 'which improves precision and detection limits'",
"Analytical Precision": "N",
"Analytical Accuracy": "N",
"Counting Statistics Error": "N",
"EDS Dead Time": "N/A",
"Goodness-of-Fit or Dispersion Statistic": "N",
"Additional Notes": "Multi-pass WDS mapping: two passes per stage map, five elements each; 18 hr per map; 20 x 10^6 fully quantitative analyses across all slides. Recorded in the acquisition-pass proposal (2026-09-08) as the evidence that EPMA partitions the target-species domain across passes.",
}


def main(apply=False):
    rows = list(csv.reader(open(SRC, newline="", encoding="utf-8-sig")))
    hdr = rows[0]
    missing = [f for f in V if f not in {r[0] for r in rows[1:] if r}]
    if missing:
        raise SystemExit("fields not in the TAPP: %s" % missing)
    unfilled = [r[0] for r in rows[1:]
                if r and r[0].strip() and not (r[0][0].isdigit() and "." in r[0][:3]) and r[0] not in V]
    print("  %d values prepared; %d content field(s) with no value" % (len(V), len(unfilled)))
    for f in unfilled:
        print("     UNFILLED:", f)
    if unfilled:
        raise SystemExit("every content row must be filled — see lit_assessment.md")
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    shutil.copy2(SRC, DST)
    rows = list(csv.reader(open(DST, newline="", encoding="utf-8-sig")))
    rows[0].append(HEADER)
    for r in rows[1:]:
        while len(r) < len(rows[0]) - 1:
            r.append("")
        if not r or not r[0].strip():
            r.append("")
        elif r[0][0].isdigit() and "." in r[0][:3]:
            r.append("N")                      # group headers take N
        else:
            r.append(V[r[0]])
    with open(DST, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
    print("  wrote", os.path.basename(DST), "-", len(rows[0]), "columns")

    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    for e in reg["composed"]:
        if e["tapp"] == "EPMA/EPMA_TAPP_v61.csv":
            e["tapp"] = "EPMA/EPMA_TAPP_v62.csv"
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for f in (SRC, SRC[:-4] + ".xlsx"):
        if os.path.exists(f):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
    subprocess.run([sys.executable, XLSX, DST], cwd=ROOT, capture_output=True, text=True)
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])


if __name__ == "__main__":
    main("--apply" in sys.argv)
