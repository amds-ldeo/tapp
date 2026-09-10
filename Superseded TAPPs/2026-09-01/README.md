# Superseded TAPPs — 2026-09-01

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
| `EPMA_TAPP_v58` | `v65` |
| `EPMA_TAPP_v59` | `v65` |
| `EPMA_TAPP_v60` | `v65` |
| `LA-MC-ICPMS_TAPP_v66` | `v72` |
| `LA-MC-ICPMS_TAPP_v67` | `v72` |
| `LA-MC-ICPMS_TAPP_v68` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v66` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v67` | `v71` |
| `LA-MC-ICPMS_UPb_TAPP_v68` | `v71` |
| `LA-Q-ICP-MS_TAPP_v69` | `v74` |
| `LA-Q-ICP-MS_TAPP_v70` | `v74` |
| `LA-Q-ICP-MS_TAPP_v71` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v69` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v70` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v71` | `v74` |
| `LA-SF-ICP-MS_TAPP_v66` | `v71` |
| `LA-SF-ICP-MS_TAPP_v67` | `v71` |
| `LA-SF-ICP-MS_TAPP_v68` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v67` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v68` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v69` | `v72` |
| `Lab-XCT_TAPP_v35` | `v39` |
| `Lab-XCT_TAPP_v36` | `v39` |
| `Lab-XCT_TAPP_v37` | `v39` |
| `SEM_Composition_TAPP_v56` | `v61` |
| `SEM_Composition_TAPP_v57` | `v61` |
| `SEM_Composition_TAPP_v58` | `v61` |
| `SEM_FIBSEM_TAPP_v29` | `v32` |
| `SEM_FIBSEM_TAPP_v30` | `v32` |
| `SEM_Imaging_TAPP_v28` | `v31` |
| `SEM_Imaging_TAPP_v29` | `v31` |
| `SEM_TAPP_v57` | `v62` |
| `SEM_TAPP_v58` | `v62` |
| `SEM_TAPP_v59` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v66` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v67` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v72` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v73` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v68` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v69` | `v73` |
| `TEM_TAPP_v47` | `v50` |
| `TEM_TAPP_v48` | `v50` |

42 version(s), 84 file(s) (CSV + xlsx).

## Why

The `analyte` → `target species` rename, a Lab-XCT Phase 3 gap, and eight audit
findings adjudicated. Three dev-log entries cover the day.

- **`Target Selection Criteria` → `Sampling Unit Selection Criteria`, 13 TAPPs** —
  `bump_samplingunitselection_20260901.py`. The same log entry records the register being found
  drifting.
- **`analyte` → `target species` renamed library-wide** by
  `rename_analyte_to_target_species_20260901.py`, executing the vocabulary settled on 2026-08-12.
- **Lab-XCT: the VOI is not the sampling unit** — a shaped Phase 3 extraction gap closed by
  `patch_labxct_extraction_20260901.py`.
- **Eight audit findings adjudicated** — seven detector artefacts and one real re-key, and the
  session that produced the **unfalsifiability rule** later cited by the `acquisition pass` decision.
- `bump_for_module_20260901.py` was written this day, superseding the 2026-08-27 bump script, which
  had left every `tapp` path in `composed_tapps.json` naming the file it had just moved here. That is
  the mechanism behind the six stale registry entries found the same day, and why
  `register-stale-tapp-path` is now an ERROR.

## Verification

Not recorded as a validator run, but this is the date `register-stale-tapp-path`
became an ERROR after six stale registry entries were found — a verification gap being closed rather
than a verification being reported.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
