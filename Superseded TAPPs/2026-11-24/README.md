# Superseded TAPPs — 2026-11-24

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v94` | `v95` |
| `LA-MC-ICPMS_TAPP_v96` | `v97` |
| `LA-MC-ICPMS_UPb_TAPP_v91` | `v92` |
| `LA-Q-ICP-MS_TAPP_v101` | `v102` |
| `LA-Q-ICP-MS_UPb_TAPP_v101` | `v102` |
| `LA-SF-ICP-MS_TAPP_v99` | `v100` |
| `LA-SF-ICP-MS_UPb_TAPP_v100` | `v101` |
| `Lab-XCT_TAPP_v48` | `v49` |
| `SEM_Composition_TAPP_v89` | `v90` |
| `SEM_FIBSEM_TAPP_v46` | `v47` |
| `SEM_Imaging_TAPP_v45` | `v46` |
| `SEM_TAPP_v91` | `v92` |
| `Solution_MC-ICP-MS_TAPP_v96` | `v97` |
| `Solution_Q-ICP-MS_TAPP_v100` | `v101` |
| `Solution_SF-ICP-MS_TAPP_v95` | `v96` |
| `TEM_TAPP_v70` | `v71` |

16 version(s), 32 file(s) (CSV + xlsx).

## Why

**The session tier was split into two columns** (issues #9 and #13 on `amds-ldeo/tapp`; proposal posted
2026-11-23, approved by SMR 2026-11-24). Column D used to answer two questions: whether the session record
must carry a field (`Basic` / `Advanced`) and where its value comes from (`Read-Only` / `Editable`).

- **Column D** now holds `Basic` / `Advanced` only, in the same words as Column C.
- **New Column K, `Procedure Value`:** `Fixed` / `Adjustable` / `Not carried over`. Module-owned: all 15
  module manifests take `K` into `owned_columns` and bump one version.
- **Mapping:** `Read-Only` → D = C, K = `Fixed` (740 rows); `Editable` → D = C, K = `Adjustable` (815);
  `Basic` / `Advanced` → unchanged, K = `Not carried over` (364). 1,919 rows in all.
- **Placement:** appended after `Purpose` (J), so Columns A–J keep their letters; the mode flags, sentinel
  and literature columns move one place right. RD decided this as step one and will decide separately
  whether to move the column next to D.
- **Column H** is stamped 2026-11-24 on every content row, since every row changed.
- **Mapping record:** `Claude Skills for TAPP/analysis/Tier_Split_Mapping_2026-11-24.csv` (the nine combinations with row counts) and `Tier_Split_Ledger_2026-11-24.csv` (every TAPP and module row: before, after; 2,090 rows). Every ledger row was checked against the mapping rule: 0 exceptions.

Script: `Project Files/Scripts/tier_split_procedure_value_20261124.py`. Code changed with it:
`compose_tapp.py`, `validate_tapp.py` (new checks `tier-d-retired`, `procvalue-missing`, `-invalid`,
`-inconsistent`, `column-layout`), `tapp_to_xlsx.py` (Column K styling and Legends; mode scan now starts at
L, fixing a bug that treated `Purpose` as a mode flag), `build_form.py`, `make_review_workbook.py` (new
`Procedure Value` and `Procedure Value OK?` columns), `sync_current_tapps.py`.

## Verification

- Rehearsed on a full copy of the library first; then applied.
- **Lossless:** each new table, mapped back to the old vocabulary with Column K removed, matches its
  predecessor in this folder in all 50,512 cells, apart from the Last Update stamps.
- Every table recomposed from the new modules to an identical file during the bump; `compose_tapp.py
  --check` afterwards: 16 MATCH.
- `validate_tapp.py`: 0 ERROR, 0 WARN. Six deliberate breaks on a copy were each caught.
- `audit_keys_vs_literature.py`: 0 NEW. No `Keyed By` value, field, data type or literature cell changed.
- Module register, mirror and schema-spec counts regenerated; review workbooks regenerated as EPMA v95.
