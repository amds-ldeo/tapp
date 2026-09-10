---
name: TEM TAPP Phase 0 Decisions
description: Confirmed Phase 0 scoping decisions for the TEM/STEM TAPP — scope boundary, mode flags, seed papers, literature assessment papers, and reference TAPP
type: project
---
Phase 0 for TEM/STEM TAPP is complete. All decisions confirmed by user as of 2026-05-18.

**Why:** Building a new TAPP for Transmission Electron Microscopy / Scanning Transmission Electron Microscopy as part of the Astromat method metadata infrastructure. Priority H; key lab contact: Hope Ishii (University of Hawaii).

## Technique Scope
TEM/STEM covers: parallel-beam TEM imaging (BF, DF, HRTEM), focused-probe STEM imaging (HAADF, ABF, BF-STEM), electron diffraction (SAED, CBED, nanobeam, precession ED, 4D-STEM), EDS X-ray spectroscopy, and EELS/EFTEM — all performed on electron-transparent specimens at the nanoscale.

FIB sample preparation is a prerequisite step documented in Sample Preparation fields, not part of the TEM analytical scope.

Excludes: SEM (separate TAPP), APT (separate TAPP), SIMS (separate TAPP). Aberration correction and accelerating voltage are field values, not scope boundaries.

## Mode Flag Columns (3 columns, starting at col I)
| Col | Label | Covers |
|-----|-------|--------|
| I | TEM Imaging | BF-TEM, DF-TEM, HRTEM |
| J | STEM Imaging | HAADF-STEM, ABF-STEM, BF-STEM |
| K | Electron Diffraction | SAED, CBED, nanobeam, precession ED, 4D-STEM |

EDS and EELS are NOT separate mode flag columns (per Planning Table row 3: "EDS/EELS = detector sub-field values"). EDS and EELS parameter fields carry mode flags Y,Y,N (applicable to TEM Imaging and STEM Imaging, not Electron Diffraction). A "Spectroscopic Detector(s)" field (C=Basic, D=Editable) serves as the selector.

Chemistry quantification (EDS, EELS) is primarily associated with STEM Imaging as the beam mode, but EFTEM (parallel beam) means EDS/EELS fields are also Y for TEM Imaging.

## Seed Papers (Phase 1 input — 5 papers)
All located in `TEM/`
- ciobanu2011.pdf — HRTEM, SAED, HAADF-STEM, EDS on ore minerals; JEM-ARM200F
- Meteorit...Caplan...chrome spinels using STEM.pdf — Cs-corrected FEI Titan 300 kV; BF/DF TEM, HAADF-STEM, SAED, STEM-EDS, EELS; Hope Ishii's group (UH)
- Meteorit...Mouloud...4D-STEM...Ryugu.pdf — 4D-STEM on Ryugu phyllosilicates
- Meteorit...Stroud...Ryugu organic matter.pdf — multi-lab; all 5 sub-capabilities; EFTEM, nanobeam diffraction
- McCoy2025 at `EPMA/s41586-024-08495-6.pdf` — Bennu evaporites; 200-keV Hitachi HF5000 STEM at U of Arizona; BF-TEM, HAADF-STEM, SAED, STEM-EDS spectrum imaging, EELS (C-K ELNES)

Wirth2009 (methods guide) — consulted for field vocabulary during Phase 1 but NOT a formal seed paper.

## Literature Assessment Papers (Phase 3 input — 9 papers)
TEM folder:
- Chaves et al, 2023.pdf
- Dobrica et al, 2022.pdf
- Keller and Berger, 2014.pdf
- Matsumoto et al, 2021.pdf
- Singerling et al, 2025.pdf
- Thompson et al, 2020.pdf
- Xing et al, 2023.pdf
- Zeng et al, 2024.pdf

Registry (EPMA folder):
- s41561-025-01741-0.pdf (Zega2025) — not yet read for TEM content

Wirth2009 excluded from literature assessment (methods guide, not application paper).

## Reference TAPP
EPMA v4 at `EPMA/EPMA_TAPP_v4.csv`
- 74 fields across 6 groups
- 2 mode columns (Point Analysis col I, Mapping col J) → TEM TAPP will have 3 mode columns
- Column structure: A=Metadata Item | B=Description | C=Protocol-Level Tier | D=Analysis-Level Tier | E=Data Type | F=Example | G=Comments | H=Last Update | I+=mode flags

**How to apply:** Phase 1 should inherit EPMA v4's 6-group structure and adapt fields. Groups 1, 2, 6 transfer with minor modifications. Groups 3–5 are substantially technique-specific for TEM.

## Phase 1 — decisions that still hold (merged from the retired phase-1 memory)

File stats from v1 are dropped: TEM is at v47 and the counts moved long ago. What does not
re-derive from the CSV is WHY fields say what they say.

**Mode-flag rationale.** `Convergence Semi-Angle` N,Y,Y covers both the STEM imaging probe and
probe-based diffraction (CBED, NBD, 4D-STEM); a separate diffraction field handles the SAED
parallel-beam case. EDS/EELS fields are Y,Y,N. `4D-STEM Detector` N,N,Y. `Monochromator` Y,Y,N
(EELS/EFTEM, not pure diffraction). `Specimen Holder` Y,Y,Y.

**Seed-paper provenance embedded in field content** — the hard-to-recover part:
- Ciobanu 2011: camera length 30 vs 150 mm affects Z-contrast purity → `Camera Length`
- Mouloud 2024: 4D-STEM near-parallel convergence (0.1 mrad), smectite 001 dwell trade-off →
  `Convergence Semi-Angle`, `4D-STEM Dwell Time`
- Stroud 2024: 60 kV for organic matter to avoid displacement damage → `Accelerating Voltage`
- Caplan 2021: SAED in-situ Pt calibration → `Diffraction Calibration Reference`
- McCoy 2025: EELS C K-edge ELNES for carbonate ID; CIPS software for SAED → `EELS Target
  Edges`, `Diffraction Data Reduction Software`
