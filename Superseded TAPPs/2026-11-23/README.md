# Superseded TAPPs — 2026-11-23

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v92` | `v93` |
| `LA-MC-ICPMS_TAPP_v94` | `v95` |
| `LA-MC-ICPMS_UPb_TAPP_v89` | `v90` |
| `LA-Q-ICP-MS_TAPP_v99` | `v100` |
| `LA-Q-ICP-MS_UPb_TAPP_v99` | `v100` |
| `LA-SF-ICP-MS_TAPP_v96` | `v97` |
| `LA-SF-ICP-MS_UPb_TAPP_v97` | `v98` |
| `Lab-XCT_TAPP_v47` | `v48` |
| `SEM_Composition_TAPP_v87` | `v88` |
| `SEM_FIBSEM_TAPP_v45` | `v46` |
| `SEM_Imaging_TAPP_v44` | `v45` |
| `SEM_TAPP_v89` | `v90` |
| `Solution_MC-ICP-MS_TAPP_v94` | `v95` |
| `Solution_Q-ICP-MS_TAPP_v97` | `v98` |
| `Solution_SF-ICP-MS_TAPP_v92` | `v93` |
| `TEM_TAPP_v69` | `v70` |

16 version(s), 32 file(s) (CSV + xlsx).

## Why

Issues **#19, #22 and #23** of `amds-ldeo/tapp`, applied together so all 16 tables bump once, by
`Project Files/Scripts/bundle_19_22_23_20261123.py`. Modules: Core v11, SamplingUnitSelection v4,
CollisionCell v6, SingleCollector v2, ICPMS v20, CompositionQC v9.

- **#19 (all 16).** The 83 "Group N" references in Column B (82) and Purpose (1) name the section and keep
  the number, or name the field: "the Procedure Identification (Group 1) coupling fields", "Mass Resolution
  Setting, in Instrument & Software (Group 3)". Text only. Conventions: "Referring to another group";
  new validator check `group-ref-bare`.
- **#22 (12 composition tables; conventions 7.13).** `Secondary Reference Materials` → `Reference
  Materials` (every standard, each once); `Primary Calibration Standard Name` → `Calibration Standard`;
  new `Reference Material Type`, `Reference Material Identifier`, `Reference Value Source`, `Reference
  Value`, `Reference Value Uncertainty`, `Reference Value Uncertainty Basis`, `Quality-Control Standards`.
  Interference Correction Standard and the delta reference name entries in Reference Materials; the five
  QC statistics are limited to Quality-Control Standards. Proposal: `Claude Skills for TAPP/analysis/
  Standards_Domain_Proposal_2026-11-19.md` (revision 2).
- **#23 (12 tables with a monitored-property definer).** New `Monitored Property Role` and `Monitored
  Property Role Detail`, keyed `monitored property`.

**Literature cells.** `Reference Materials`: the old secondary list plus the standards named by the
calibration, interference and delta cells (51 distinct cell sets, written by hand in the script's
`LIT22`), every old member id kept. `Quality-Control Standards`: the old secondary lists, as
`all [all: …]`. Role cells: `all: Target` where every member has a target species (37 columns); the
stated role for parentless members (23 columns, `LIT23`), `N` where the paper does not say. **Not
assessed (blank): the six new standard-attribute fields** — a follow-up literature pass.

**Open:** the role list is open; the literature already uses `Mass-bias monitor` twice (Desem et al.
2022, Willbold 2005). Whether to add it to Column F is RD's call, and SMR should hear of it.

## Verification

- Rehearsed on a copy of the library first; then applied.
- `validate_tapp.py --root .`: 0 ERROR, 0 WARN (after adding the two `N/A | None` options and updating
  conventions' version pointers).
- `recompose_all_20260812.py --check`: 16 MATCH.
- `audit_keys_vs_literature.py`: 0 NEW (rulings carried to `Calibration Standard`; new rulings for
  `Quality-Control Standards`, `Monitored Property Role`, `Monitored Property Role Detail`).
- Cell diff in the rehearsal, old vs new, for EPMA, Solution MC and Lab-XCT: only the intended rows changed; no row removed.
- `group-ref-bare` fires 7 times on the superseded Lab-XCT v47 (its 7 references) and 0 times on the
  current library.
- Review workbooks regenerated as EPMA v93.
