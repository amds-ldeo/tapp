# Superseded TAPPs — 2026-08-25

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
| `EPMA_TAPP_v26` | `v65` |
| `EPMA_TAPP_v27` | `v65` |
| `LA-MC-ICPMS_TAPP_v27` | `v72` |
| `LA-MC-ICPMS_TAPP_v28` | `v72` |
| `LA-MC-ICPMS_TAPP_v29` | `v72` |
| `LA-MC-ICPMS_TAPP_v30` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v27` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v28` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v29` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v30` | `v71` |
| `LA-Q-ICP-MS_TAPP_v30` | `v74` |
| `LA-Q-ICP-MS_TAPP_v31` | `v74` |
| `LA-Q-ICP-MS_TAPP_v32` | `v74` |
| `LA-Q-ICP-MS_TAPP_v33` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v30` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v31` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v32` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v33` | `v74` |
| `LA-SF-ICP-MS_TAPP_v29` | `v71` |
| `LA-SF-ICP-MS_TAPP_v30` | `v71` |
| `LA-SF-ICP-MS_TAPP_v31` | `v71` |
| `LA-SF-ICP-MS_TAPP_v32` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v30` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v31` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v32` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v33` | `v72` |
| `Lab-XCT_TAPP_v21` | `v39` |
| `Lab-XCT_TAPP_v22` | `v39` |
| `SEM_Composition_TAPP_v24` | `v61` |
| `SEM_Composition_TAPP_v25` | `v61` |
| `SEM_FIBSEM_TAPP_v15` | `v32` |
| `SEM_FIBSEM_TAPP_v16` | `v32` |
| `SEM_Imaging_TAPP_v15` | `v31` |
| `SEM_Imaging_TAPP_v16` | `v31` |
| `SEM_TAPP_v24` | `v62` |
| `SEM_TAPP_v25` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v31` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v32` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v33` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v34` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v35` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v36` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v37` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v38` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v33` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v34` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v35` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v36` | `v73` |
| `TEM_TAPP_v22` | `v50` |
| `TEM_TAPP_v23` | `v50` |

50 version(s), 100 file(s) (CSV + xlsx).

## Why

`Module_ICPMS` v1, and the start of the Description/Purpose split.

- **`Module_ICPMS` v1 extracted** — 13 of 39 candidate fields admitted, **26 deferred by evidence**
  rather than assumed; the development log entry records the admission test. Composed into the 9
  ICP-MS TAPPs by `apply_module_icpms_20260825.py`.
- **Description/Purpose split, Step 1** — Column J (`Purpose`) added by
  `add_purpose_column_20260825.py`, and the Purpose sentences moved out of Column B descriptions by
  `apply_step1_purpose_20260825.py` and `apply_step1_icpms_slice_20260825.py`. Move only, no rewording.
- **Step 2 rewriting** began with `apply_step2_rewrite_20260825.py`; versions bumped by
  `bump_after_step2_20260825.py`.

## Verification

Not recorded.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
