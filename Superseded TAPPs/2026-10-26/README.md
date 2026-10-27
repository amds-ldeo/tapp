# Superseded TAPPs — 2026-10-26

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v88` | `v89` |
| `LA-MC-ICPMS_TAPP_v91` | `v92` |
| `LA-MC-ICPMS_UPb_TAPP_v86` | `v87` |
| `LA-Q-ICP-MS_TAPP_v96` | `v97` |
| `LA-Q-ICP-MS_UPb_TAPP_v96` | `v97` |
| `LA-SF-ICP-MS_TAPP_v93` | `v94` |
| `LA-SF-ICP-MS_UPb_TAPP_v94` | `v95` |
| `SEM_Composition_TAPP_v83` | `v84` |
| `SEM_TAPP_v85` | `v86` |
| `Solution_MC-ICP-MS_TAPP_v91` | `v92` |
| `Solution_Q-ICP-MS_TAPP_v94` | `v95` |
| `Solution_SF-ICP-MS_TAPP_v89` | `v90` |
| `TEM_TAPP_v67` | `v68` |

13 version(s), 26 file(s) (CSV + xlsx).

## Why

Rules in the TAPP, results in the dataset (conventions.md Rule 14; precedents.md, 2026-10-26).
`Module_Aggregation` v5 → v6 and `Module_UPb` v10 → v11, composed into all 13 Aggregation
consumers by `Project Files/Scripts/aggregation_results_to_dataset_20261026.py`. The change came
from an EPMA team member's review of the v88 review workbook.

- **Retired:** `Combined Results` and `Other Statistics`. Both held results on samples. Their 268
  literature cells (about 77 non-N) are kept only in the versions in this folder.
- **`Analysis Inclusion and Rejection Criteria`:** now holds the rules only. Session tier
  Basic → Editable; key `combined result` → `(none)`.
- **`Goodness-of-Fit or Dispersion Statistic`:** now names the statistic, not its value.
  Procedure tier N/A → Basic, session tier Basic → Editable; key → `reported property`.
- **`Combination Method`:** its description gained an `In the dataset:` sentence.
- **Overlays:** Purpose (J) takes the v6 defaults in all 13 TAPPs; the three U-Pb TAPPs take new
  examples (F) from Module_UPb.
- **Literature cells for the inclusion criteria:** all 45 non-N cells were re-read against the
  rules-only definition. 36 → N, each keeping its earlier reading; 6 kept; 3 kept as Partially
  with the reason restated.
- **Key `combined result`:** retired, with no definer and no consumer left.

## Verification

- `recompose_all_20260812.py --check`: 16 MATCH, 0 DIFFERS. `build_module_register.py`: up to date.
- `validate_tapp.py`: 0 ERROR. The 4 WARN were documentation pointing at the old versions and
  fields; they were fixed in the same change.
- `audit_keys_vs_literature.py`: 0 NEW after one ruling was recorded. The detector reads the oxide
  names in the dispersion cells as target species; they are reported variables, as already ruled
  for Combination Method.
- Fields, tiers and keys changed as listed above; no data type changed.
