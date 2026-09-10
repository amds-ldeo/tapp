# Superseded TAPPs — 2026-08-12

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

> **Reconstructed 2026-09-10.** This folder was parked before bump scripts wrote a README,
> so the notes below were assembled afterwards from the dated entries in
> `../../Project Files/Design Notes/TAPP_Development_Log.md`, the dated commit subjects in
> git, and the dated patch scripts in `../../Project Files/Scripts/`. It is not a
> contemporaneous record.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v13` | `v65` |
| `EPMA_TAPP_v14` | `v65` |
| `EPMA_TAPP_v15` | `v65` |
| `LA-MC-ICPMS_TAPP_v7` | `v72` |
| `LA-MC-ICPMS_TAPP_v8` | `v72` |
| `LA-MC-ICPMS_TAPP_v9` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v7` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v8` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v9` | `v71` |
| `LA-Q-ICP-MS_TAPP_v11` | `v74` |
| `LA-Q-ICP-MS_TAPP_v12` | `v74` |
| `LA-Q-ICP-MS_TAPP_v13` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v12` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v13` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v14` | `v74` |
| `LA-SF-ICP-MS_TAPP_v11` | `v71` |
| `LA-SF-ICP-MS_TAPP_v12` | `v71` |
| `LA-SF-ICP-MS_TAPP_v13` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v12` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v13` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v14` | `v72` |
| `Lab-XCT_TAPP_v13` | `v39` |
| `Lab-XCT_TAPP_v14` | `v39` |
| `SEM_Composition_TAPP_v10` | `v61` |
| `SEM_Composition_TAPP_v11` | `v61` |
| `SEM_Composition_TAPP_v12` | `v61` |
| `SEM_FIBSEM_TAPP_v9` | `v32` |
| `SEM_Imaging_TAPP_v9` | `v31` |
| `SEM_TAPP_v10` | `v62` |
| `SEM_TAPP_v11` | `v62` |
| `SEM_TAPP_v12` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v11` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v12` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v13` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v13` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v14` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v15` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v13` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v14` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v15` | `v73` |
| `TEM_TAPP_v13` | `v50` |
| `TEM_TAPP_v14` | `v50` |

42 version(s), 84 file(s) (CSV + xlsx).

## Why

The Rule 13 session/sample restructure, the `analyte` settlement, and the folder
reorganisation — the largest single-day change in the library's history to that point. Recorded in
full in the development log under *"Rule 13, the `analyte` settlement, and a schema-facing sweep"*.

- **Rule 13** — the analysis record is the **session**, not one sample. `sample` entered the key
  vocabulary as an anchor; `Sample Name` became `defines: sample`, `Sample Persistent Identifier`
  became `sample`, and a new `Session Identifier` was composed into all 16 TAPPs. 17 rows nested to
  `sample > sampling unit`, and `A > B x C` was specified in Rule 7.3 for `Counting Statistics Error`.
- **`analyte` settled** as the chemical species determined, never the isotope — eight contradicting
  descriptions corrected. Nine electron-beam setup fields moved from `analyte` to `channel` on Jia et
  al. 2022, and `WDS Spectrometer Channel` became `defines: channel per analyte`. Rule 7.3.1 was
  amended so the parent key is optional per row, interference monitors being channels with no analyte.
- **Four new validator checks**, two of which found real pre-existing problems: `Module_MCICPMS` at v3
  against a register claiming v4, and a regenerated xlsx byte-identical in size but not content.

Applied by `survey_colB_colI_20260812.py`, `build_colI_survey_findings_20260812.py`,
`triage_colB_uniformity_20260812.py`, `bump_and_stamp_20260812.py` and `recompose_all_20260812.py`.

`fix_paths_after_reorg_20260812.py` ran the same day and is why this folder is
`Superseded TAPPs/2026-08-12/` rather than the root-level `Superseded TAPPs (2026-08-12)/` that the
three earlier retirement folders were originally created as.

## Verification

A contemporaneous lint report survives for this date:
`../../Project Files/Reports/TAPP_Lint_Report_2026-08-12.csv`. It is the last of four consecutive such reports
(2026-08-07, -08, -11, -12), after which the practice lapsed — so no other folder in this tree has an
equivalent. It resumed on 2026-09-10 with `TAPP_Lint_Report_2026-09-10.csv`, which describes the
library as it is now, not as it was when this folder was parked.

Four validator checks were **added** on this date, so the library was not being measured against a
fixed ruleset across the day. Two of the four found real pre-existing defects, both fixed the same
day.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
