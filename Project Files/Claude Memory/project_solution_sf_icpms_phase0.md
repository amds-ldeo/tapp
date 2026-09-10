---
name: project-solution-sf-icpms-phase0
description: "Phase 0 scoping decisions for the Solution SF-ICP-MS TAPP — technique scope, architecture rationale, mode flags, seed papers, reference TAPP"
metadata: 
  node_type: memory
  type: project
---

Phase 0 for Solution SF-ICP-MS TAPP confirmed 2026-06-15.

**Why:** Building a new TAPP for single-collector sector-field solution ICP-MS as part of the Astromat method metadata infrastructure. High priority; key lab contacts: Caltech (Francois Tissot), ASU (Ren Marquez).

## Technique Scope

Single-collector sector-field (SF) ICP-MS — also called HR-ICP-MS — with solution sample introduction (nebulizer → spray chamber → torch → ICP plasma → magnetic + electrostatic sector → single detector). Measures trace and major elemental concentrations in digested or dissolved geological and cosmochemical samples. Selectable mass resolution (low ~300 / medium ~4000 / high ~10 000 m/Δm) resolves polyatomic interferences by mass rather than by chemical reaction, without CRC. Instruments include Thermo Scientific Element 2, Element XR, Nu Instruments Nu Attom ES.

**Excludes:**
- Solution Q-ICP-MS: separate TAPP (see [[project-solution-q-icpms-phase0]])
- TQ-ICP-MS/MS: future separate TAPP
- MC-ICP-MS: separate TAPP (multi-collector, isotope-ratio focus, cup configuration metadata)
- LA-coupled variants: separate TAPPs
- ICP-OES: optical detection, not mass spectrometric — future separate TAPP

## Architecture Decision

**Separate TAPPs for Q and SF** (not combined). See [[project-solution-q-icpms-phase0]] for full rationale. The key SF-specific fields that justify a separate TAPP:
- Mass resolution setting per analyte (LR/MR/HR) — primary protocol decision determining which elements can be cleanly measured
- SEM–Faraday detector cross-calibration — hardware feature of Element 2/XR
- No CRC fields (absent from SF-ICP-MS workflow; uses resolution instead)

## Mode Flag Columns

**None.** Mass resolution is an analyte-specific field value within a single protocol, not a structural mode distinction. A single SF-ICP-MS session may use LR for most masses and MR or HR for specific interference-prone analytes (e.g., MR for ⁵⁶Fe to separate from ⁴⁰Ar¹⁶O); this is captured in an Analyte-Specific field, not via mode flag columns.

This decision may be revisited at Phase 2 if the seed paper review reveals that LR vs. HR protocols are structurally distinct enough (e.g., different analyte lists, different QC standards) to warrant mode flags.

## Seed Papers (5 papers, Phase 1 input)

All located in `Solution SF-ICP-MS/`:
- `barrat2012.pdf` — Barrat et al. 2012
- `Braukmuller et al 2018.pdf` — Braukmuller et al. 2018
- `Burney and Neal 2019.pdf` — Burney & Neal 2019
- `Gaschnig et al 2015.pdf` — Gaschnig et al. 2015
- `Wang et al 2014.pdf` — Wang et al. 2014

## Reference TAPP

`LA-Q/SF-ICPMS_TAPP_v2.csv` at `LA-Q:SF-ICP-MS/`

Groups 1, 2, 6 transfer with minor modifications. Group 3 plasma/hardware fields (torch, cones, RF power, gas flows) transfer directly. Group 3 laser fields absent (no laser). Group 4 will diverge significantly from LA TAPP: no ablation parameters; resolution setting fields central; CRC fields absent. Group 5 data reduction similar in structure to Q-ICP-MS (internal standard, external calibration, drift correction, blank subtraction) but resolution-mode-specific interference correction replaces CRC-based correction.

**How to apply:** Phase 1 should inherit the 6-group structure from v2. Key SF-specific additions vs. LA TAPP: mass resolution setting (analyte-specific) in Group 4; SEM–Faraday cross-calibration in Group 3; resolution-specific interference correction method in Group 5.

## Cross-TAPP Consistency Notes

- Groups 1 and 2 must be identical to Solution Q-ICP-MS TAPP for all shared fields (propagation rule).
- Group 3 plasma hardware fields (torch geometry, cone configuration, RF power, gas flows, guard electrode) must be identical between Solution Q-ICP-MS and Solution SF-ICP-MS where the same concept applies; diverge only where hardware genuinely differs.
- LA-Q/SF-ICP-MS TAPP shares Group 3 ICP-MS hardware fields (cones, torch, gas flows) — keep naming and tier assignments consistent for fields that exist in both solution TAPPs and the LA TAPP.

**Terminology superseded 2026-08-11.** "Analyte-Specific" was a Column G label that no longer exists; cardinality is now declared in Column I (`Keyed By`) under Rule 7, and Comments is empty library-wide. Where this note says a field is analyte-specific, read it as `Keyed By: analyte`. See [[project_tapp_keyed_by_rule7]].

## Phase 2 — decisions that still hold (merged from the retired phase-2 memory)

The v5 changelog and per-group counts are dropped; the file is at v68. The durable part is the
mass-resolution split recorded above, plus: Solution SF carries no mode-flag columns, and the
detector-mode fields (`Detector Configuration`, `Pulse/Analog Detector Nonlinearity Correction`)
are shared with the Q lineage rather than SF-specific.
