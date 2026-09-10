---
name: project-solution-q-icpms-phase0
description: "Phase 0 scoping decisions for the Solution Q-ICP-MS TAPP — technique scope, architecture rationale, mode flags, seed papers, reference TAPP"
metadata: 
  node_type: memory
  type: project
---

Phase 0 for Solution Q-ICP-MS TAPP confirmed 2026-06-15.

**Why:** Building a new TAPP for single-quadrupole solution ICP-MS as part of the Astromat method metadata infrastructure. High priority; key lab contacts: Caltech (Francois Tissot), ASU (Ren Marquez).

## Technique Scope

Single-quadrupole (Q) ICP-MS with solution sample introduction (nebulizer → spray chamber → torch → ICP plasma → quadrupole mass filter → detector). Measures trace and major elemental concentrations in digested or dissolved geological and cosmochemical samples. Unit mass resolution only; polyatomic interference management relies on CRC (collision/reaction cell) modes — He KED, reactive gas DRC (dynamic reaction cell), or CCT (collision cell technology).

**Excludes:**
- TQ-ICP-MS/MS (triple quadrupole / ICP-MS/MS): MS/MS-specific metadata (reaction gas identity, precursor/product ion masses, mass-shift vs. on-mass mode) too distinct — future separate TAPP
- Solution SF-ICP-MS: separate TAPP (see [[project-solution-sf-icpms-phase0]])
- MC-ICP-MS: separate TAPP (isotope ratios, different measurement goal)
- LA-coupled variants: all in separate TAPPs
- ICP-OES: optical detection, not mass spectrometric — separate future TAPP

## Architecture Decision

**Separate TAPPs for Q and SF** (not combined). Rationale:

CRC parameters (reaction gas identity, gas flow, kinetic energy discrimination offset, cell pressure, CRC mode) are central to Q-ICP-MS operation and completely absent from SF-ICP-MS. Mass resolution setting (LR/MR/HR, m/Δm ~300/4000/10000) is central to SF-ICP-MS and a trivial constant (unit resolution) for Q-ICP-MS. Combining them would create dead-end fields in each TAPP with no mode flag mechanism to suppress them cleanly.

**Why LA-Q/SF-ICP-MS stays combined:** CRC is absent from all 13 LA protocols assessed in the v2 TAPP literature assessment. The ablation process dominates LA metadata; the Q/SF distinction reduces to one field (Mass Resolution Setting) which is already handled in v2. Restructuring v2 would cost more than it gains.

## Mode Flag Columns

**None.** Solution Q-ICP-MS is a single-mode technique — there is no meaningful spatial or spectral sub-mode distinction (no equivalent of Spot/Transect/Mapping from LA-ICP-MS). CRC usage is an optional parameter captured as a field value, not a mode flag.

## Seed Papers (7 papers, Phase 1 input)

All located in `Solution Q-ICP-MS/`:
- `29_Hyung&Tissot_2021_JAAS.pdf` — Hyung & Tissot 2021, JAAS
- `Holdship et al, 2018.pdf` — Holdship et al. 2018
- `Liu and Li, 2019.pdf` — Liu & Li 2019
- `Ulrich et al 2010.pdf` — Ulrich et al. 2010
- `Braukmuller et al 2020.pdf` — Braukmuller et al. 2020 (added 2026-06-16)
- `Day et al 2016.pdf` — Day et al. 2016 (added 2026-06-16)
- `Khan et al 2015.pdf` — Khan et al. 2015 (added 2026-06-16)

## Reference TAPP

`LA-Q/SF-ICPMS_TAPP_v2.csv` at `LA-Q:SF-ICP-MS/`

Groups 1, 2, 6 transfer with minor modifications. Group 3 plasma/hardware fields (torch, cones, RF power, gas flows) transfer directly. Group 3 laser fields are absent (no laser). Group 4 will diverge significantly: solution-mode acquisition parameters replace ablation parameters; CRC fields are new. Group 5 data reduction is similar in structure (internal standard, external calibration, drift correction, blank subtraction) but solution-specific.

**How to apply:** Phase 1 should inherit the 6-group structure from v2. Key additions vs. LA TAPP: CRC-related fields in Group 4 (reaction gas, gas flow, KED voltage/energy offset, CRC mode); solution-specific sample prep fields in Group 2 (digestion method, dilution factor, acid matrix).

## Phase 2 — decisions that still hold (merged from the retired phase-2 memory)

The v5 changelog and per-group field counts are dropped: the file is at v72 and every count
moved. Two conceptual decisions survive and are not obvious from the CSV:

- **CRC mode is NOT an "Analytical Mode".** STD/KED/DRC is a cell configuration, so
  `Analytical Mode` was removed and `Collision/Reaction Cell (CRC) Configuration` carries it in
  Group 3. This is why Solution Q has no mode-flag columns.
- **Mode-specific field families were collapsed into generic ones** (2026-06-16): the
  `KED Mode: …` / `DRC Mode: …` families became `Collision Gas Type/Flow Rate`,
  `Reaction Gas Type/Flow Rate`, `Cell Exit Discrimination Voltage` — now all owned by
  `Module_CollisionCell`.

Both Phase 3/4 flags are closed: `Chromatographic Separation Applied` was NOT split into
Applied + Procedure — it became `Controlled list / Text` with `Yes | N/A | None` on 2026-08-31,
the chemistry going in the text half.
