# Superseded TAPPs — 2026-10-27

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v89` | `v90` |
| `LA-MC-ICPMS_TAPP_v92` | `v93` |
| `LA-MC-ICPMS_UPb_TAPP_v87` | `v88` |
| `LA-Q-ICP-MS_TAPP_v97` | `v98` |
| `LA-Q-ICP-MS_UPb_TAPP_v97` | `v98` |
| `LA-SF-ICP-MS_TAPP_v94` | `v95` |
| `LA-SF-ICP-MS_UPb_TAPP_v95` | `v96` |
| `SEM_Composition_TAPP_v84` | `v85` |
| `SEM_TAPP_v86` | `v87` |
| `Solution_MC-ICP-MS_TAPP_v92` | `v93` |
| `Solution_Q-ICP-MS_TAPP_v95` | `v96` |
| `Solution_SF-ICP-MS_TAPP_v90` | `v91` |

12 version(s), 24 file(s) (CSV + xlsx).

## Why

The Rule 14 sweep: method in the TAPP, per-analysis values in the dataset (conventions.md 14.3;
precedents.md, 2026-10-27). Applied by `Project Files/Scripts/rule14_sweep_20261027.py`, which
bumped four modules: Module_CompositionQC v6→v7, Module_ICPMS v17→v18, Module_Geochronology v8→v9
and Module_UPb v11→v12.

- **Counting Statistics Error and Internal (Within-Measurement) Analytical Precision:** now the
  method only. Key `sample > sampling unit x reported property` → `reported property`; session
  tier Basic → Editable.
- **Discordance Definition and Values:** renamed `Discordance Definition`, the formula only. The
  row was renamed in each source, so its literature cells are kept.
- **Radiogenic Fraction of Measured Signal:** retired. Its 13 literature cells, all N, are kept only
  in the versions in this folder.
- **Error Correlation Between Reported Quantities:** amended under Rule 10. Session tier
  Basic → Editable; data type Text (free).
- **Detection Limit and Inherited or Initial Signal Correction:** each gained an `In the dataset:`
  sentence.
- **Consumer examples:** where they held values, they were rewritten.

## Verification

- `recompose_all_20260812.py --check`: 16 MATCH.
- `validate_tapp.py`: 0 ERROR. One WARN was the schema README naming the old Discordance field; it
  was fixed in the same change.
- `audit_keys_vs_literature.py`: 0 NEW.
- Literature cells were not re-read. Every cell of the changed fields is N or names a statistic,
  and a field that asks for less cannot turn an N into a Y.
