# Superseded TAPPs — 2026-08-27

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
| `EPMA_TAPP_v31` | `v65` |
| `EPMA_TAPP_v32` | `v65` |
| `EPMA_TAPP_v33` | `v65` |
| `EPMA_TAPP_v34` | `v65` |
| `EPMA_TAPP_v35` | `v65` |
| `EPMA_TAPP_v36` | `v65` |
| `EPMA_TAPP_v37` | `v65` |
| `EPMA_TAPP_v38` | `v65` |
| `EPMA_TAPP_v39` | `v65` |
| `EPMA_TAPP_v40` | `v65` |
| `LA-MC-ICPMS_TAPP_v39` | `v72` |
| `LA-MC-ICPMS_TAPP_v40` | `v72` |
| `LA-MC-ICPMS_TAPP_v41` | `v72` |
| `LA-MC-ICPMS_TAPP_v42` | `v72` |
| `LA-MC-ICPMS_TAPP_v43` | `v72` |
| `LA-MC-ICPMS_TAPP_v44` | `v72` |
| `LA-MC-ICPMS_TAPP_v45` | `v72` |
| `LA-MC-ICPMS_TAPP_v46` | `v72` |
| `LA-MC-ICPMS_TAPP_v47` | `v72` |
| `LA-MC-ICPMS_TAPP_v48` | `v72` |
| `LA-MC-ICPMS_TAPP_v49` | `v72` |
| `LA-MC-ICPMS_TAPP_v50` | `v72` |
| `LA-MC-ICPMS_TAPP_v51` | `v72` |
| `LA-MC-ICPMS_TAPP_v52` | `v72` |
| `LA-MC-ICPMS_TAPP_v53` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v39` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v40` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v41` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v42` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v43` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v44` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v45` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v46` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v47` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v48` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v49` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v50` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v51` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v52` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v53` | `v71` |
| `LA-Q-ICP-MS_TAPP_v42` | `v74` |
| `LA-Q-ICP-MS_TAPP_v43` | `v74` |
| `LA-Q-ICP-MS_TAPP_v44` | `v74` |
| `LA-Q-ICP-MS_TAPP_v45` | `v74` |
| `LA-Q-ICP-MS_TAPP_v46` | `v74` |
| `LA-Q-ICP-MS_TAPP_v47` | `v74` |
| `LA-Q-ICP-MS_TAPP_v48` | `v74` |
| `LA-Q-ICP-MS_TAPP_v49` | `v74` |
| `LA-Q-ICP-MS_TAPP_v50` | `v74` |
| `LA-Q-ICP-MS_TAPP_v51` | `v74` |
| `LA-Q-ICP-MS_TAPP_v52` | `v74` |
| `LA-Q-ICP-MS_TAPP_v53` | `v74` |
| `LA-Q-ICP-MS_TAPP_v54` | `v74` |
| `LA-Q-ICP-MS_TAPP_v55` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v42` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v43` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v44` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v45` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v46` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v47` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v48` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v49` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v50` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v51` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v52` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v53` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v54` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v55` | `v74` |
| `LA-SF-ICP-MS_TAPP_v41` | `v71` |
| `LA-SF-ICP-MS_TAPP_v42` | `v71` |
| `LA-SF-ICP-MS_TAPP_v43` | `v71` |
| `LA-SF-ICP-MS_TAPP_v44` | `v71` |
| `LA-SF-ICP-MS_TAPP_v45` | `v71` |
| `LA-SF-ICP-MS_TAPP_v46` | `v71` |
| `LA-SF-ICP-MS_TAPP_v47` | `v71` |
| `LA-SF-ICP-MS_TAPP_v48` | `v71` |
| `LA-SF-ICP-MS_TAPP_v49` | `v71` |
| `LA-SF-ICP-MS_TAPP_v50` | `v71` |
| `LA-SF-ICP-MS_TAPP_v51` | `v71` |
| `LA-SF-ICP-MS_TAPP_v52` | `v71` |
| `LA-SF-ICP-MS_TAPP_v53` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v42` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v43` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v44` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v45` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v46` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v47` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v48` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v49` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v50` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v51` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v52` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v53` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v54` | `v72` |
| `Lab-XCT_TAPP_v24` | `v39` |
| `Lab-XCT_TAPP_v25` | `v39` |
| `Lab-XCT_TAPP_v26` | `v39` |
| `Lab-XCT_TAPP_v27` | `v39` |
| `Lab-XCT_TAPP_v28` | `v39` |
| `SEM_Composition_TAPP_v29` | `v61` |
| `SEM_Composition_TAPP_v30` | `v61` |
| `SEM_Composition_TAPP_v31` | `v61` |
| `SEM_Composition_TAPP_v32` | `v61` |
| `SEM_Composition_TAPP_v33` | `v61` |
| `SEM_Composition_TAPP_v34` | `v61` |
| `SEM_Composition_TAPP_v35` | `v61` |
| `SEM_Composition_TAPP_v36` | `v61` |
| `SEM_Composition_TAPP_v37` | `v61` |
| `SEM_Composition_TAPP_v38` | `v61` |
| `SEM_FIBSEM_TAPP_v19` | `v32` |
| `SEM_FIBSEM_TAPP_v20` | `v32` |
| `SEM_FIBSEM_TAPP_v21` | `v32` |
| `SEM_FIBSEM_TAPP_v22` | `v32` |
| `SEM_Imaging_TAPP_v18` | `v31` |
| `SEM_Imaging_TAPP_v19` | `v31` |
| `SEM_Imaging_TAPP_v20` | `v31` |
| `SEM_Imaging_TAPP_v21` | `v31` |
| `SEM_TAPP_v30` | `v62` |
| `SEM_TAPP_v31` | `v62` |
| `SEM_TAPP_v32` | `v62` |
| `SEM_TAPP_v33` | `v62` |
| `SEM_TAPP_v34` | `v62` |
| `SEM_TAPP_v35` | `v62` |
| `SEM_TAPP_v36` | `v62` |
| `SEM_TAPP_v37` | `v62` |
| `SEM_TAPP_v38` | `v62` |
| `SEM_TAPP_v39` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v42` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v43` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v44` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v45` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v46` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v47` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v48` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v49` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v50` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v51` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v52` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v53` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v47` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v48` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v49` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v50` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v51` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v52` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v53` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v54` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v55` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v56` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v57` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v58` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v59` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v45` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v46` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v47` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v48` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v49` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v50` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v51` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v52` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v53` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v54` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v55` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v56` | `v73` |
| `TEM_TAPP_v27` | `v50` |
| `TEM_TAPP_v28` | `v50` |
| `TEM_TAPP_v29` | `v50` |
| `TEM_TAPP_v30` | `v50` |
| `TEM_TAPP_v31` | `v50` |
| `TEM_TAPP_v32` | `v50` |
| `TEM_TAPP_v33` | `v50` |
| `TEM_TAPP_v34` | `v50` |

172 version(s), 344 file(s) (CSV + xlsx).

## Why

`Module_CompositionQC`, the non-ICP-MS half of the Description/Purpose split, and the
completion of `Module_ICPMS` — 172 versions parked, the largest single day in this folder tree.

- **`Module_CompositionQC v1: the 12-TAPP quantitative-composition layer`** —
  `build_compositionqc_20260827.py`, bumped by `bump_for_compositionqc_20260827.py`
- **`Apply Step 1 of the Description/Purpose split to the 7 non-ICP-MS TAPPs`** and
  **`Step 2 for the 7 non-ICP-MS TAPPs: 91 flags acted on, 26 resolved as no change`** —
  the `step1_routes_*`, `apply_step1_*`, `step2_edits_*` and `apply_step2_*` scripts of that date
- **`Move Analysis Sequence into Module_ICPMS; module complete at 39 fields`** —
  `add_analysis_sequence_to_module_20260827.py`, closing the module opened on 2026-08-25
- **`Correct W5.3: the Dwell Time case is a scope leak, not a Column I defect`** — a correction to
  the working note, not to a TAPP
- Field-level items: `add_elnes_field_20260827.py`, `fix_eels_energy_resolution_20260827.py`,
  `rename_detector_type_20260827.py`, `rename_interference_20260827.py`,
  `universalise_spm_20260827.py`, `extend_laserablation_20260827.py`

## Verification

Not recorded. `Correct W5.3: the Dwell Time case is a scope leak, not a Column I
defect` is a same-day correction to the day's own working note.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
