---
name: project-sem-tapp-phase0
description: "SEM TAPP Phase 0 decisions — technique scope, 8 mode flags, seed papers, reference TAPP, FIB-SEM architecture decision"
metadata: 
  node_type: memory
  type: project
---

## Phase 0 Decisions: SEM TAPP

**Technique scope:** Scanning Electron Microscopy (SEM) including FIB-SEM as an instrument variant. Excludes: TEM/STEM (requires electron-transparent foils, separate TAPP), EPMA (dedicated microprobe, separate TAPP).

**FIB-SEM architecture:** FIB-SEM captured as Instrument Variant field in Group 3 (not a separate TAPP). TEM Sample Preparation and 3D Tomography are FIB-SEM-exclusive mode columns.

**8 Mode flag columns (cols I–P):**
1. SE Imaging — SEM + FIB-SEM
2. BSE Imaging — SEM + FIB-SEM
3. EDS — SEM + FIB-SEM; fields ported from EPMA TAPP v5 with tier review
4. SEM-WDS — SEM + FIB-SEM; fields ported from EPMA TAPP v5 with tier review
5. CL — SEM + FIB-SEM
6. EBSD — SEM + FIB-SEM
7. TEM Sample Preparation — FIB-SEM only
8. 3D Tomography — FIB-SEM only

**CCI (Charge Contrast Imaging):** VP-SEM variant within SE Imaging mode, not a separate mode column.

**Reference TAPP:** EPMA TAPP v5 (structural template); TEM TAPP v6 consulted for electron microscopy field conventions.

**Seed papers (Phase 1):**
- McCoy 2025 (`s41586-024-08495-6.pdf`, EPMA folder) — SE, BSE, EDS, CL, EBSD, TEM Prep; multi-lab
- Saif 2017 (`Saif et al, 2017 FIB-SEM.pdf`, SEM folder) — BSE, EDS, 3D Tomography; FEI Helios NanoLab 660
- Ferus 2020 (`Ferus et al, 2020.pdf`, SEM folder) — SE, BSE, EDS, SEM-WDS, EBSD; TESCAN MIRA 3 + Oxford Wave 700 (only non-EPMA WDS paper)
- Hamers 2016 (`Hamers et al, 2016.pdf`, SEM folder) — CL spectroscopy, TEM Sample Preparation; best CL parameters documentation

**Why:** EPMA EDS/WDS fields reused for cross-TAPP consistency; tier assignments reviewed for SEM-specific context (e.g., Faraday cup fields → N/A for SEM, beam current precision lower than EPMA).

## Phase 1 — decisions that still hold (merged from the retired phase-1 memory)

v1 field counts are dropped; SEM is at v57.

**Mode-flag applicability.** `Image Pixel Size` and `Dwell Time per Pixel` apply to SE, BSE and
3D Tomography. `Chamber Pressure` is Y for SE, BSE, EDS, WDS, CL, EBSD and N for TEM Prep and
3D Tomo.

**`Beam Current` keying — RESOLVED 2026-08-11, and the reasoning generalised later.** Not
analyte-keyed: the literature shows beam current varying by PHASE, not element (Liu et al.
2016 — 20 nA silicates, 10 nA maskelynite), so it is `Keyed By: sample > sampling unit` in the
compositional SEM TAPPs and `(none)` in SEM_Imaging/SEM_FIBSEM. The whole electron-beam setup
cluster followed it on 2026-08-31: `Beam Mode`, `Beam Diameter`, `Beam Raster Dimensions` and
`Beam Damage Minimization` are all `sample > sampling unit`. See [[project-tapp-keyed-by-rule7]].

**Stale label warning.** Where older notes say a field is "Analyte-Specific" (a Column G label
that no longer exists), read `Keyed By: analyte`. Comments is empty library-wide.
