# Superseded TAPPs — 2026-08-24

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
| `EPMA_TAPP_v25` | `v65` |
| `LA-MC-ICPMS_TAPP_v26` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v26` | `v71` |
| `LA-Q-ICP-MS_TAPP_v29` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v29` | `v74` |
| `LA-SF-ICP-MS_TAPP_v28` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v29` | `v72` |
| `SEM_Composition_TAPP_v22` | `v61` |
| `SEM_Composition_TAPP_v23` | `v61` |
| `SEM_FIBSEM_TAPP_v14` | `v32` |
| `SEM_Imaging_TAPP_v14` | `v31` |
| `SEM_TAPP_v22` | `v62` |
| `SEM_TAPP_v23` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v30` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v34` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v32` | `v73` |
| `TEM_TAPP_v21` | `v50` |

17 version(s), 34 file(s) (CSV + xlsx).

## Why

Four independent conformance fixes, one per commit:

- **`Fix SEM Analytical Mode vocabulary and foreign columns`** — `fix_sem_analytical_mode_20260824.py`
- **`Fix Detection Limit typing across 13 TAPPs`** — `fix_detection_limit_20260824.py`, closing
  `amds-ldeo/tapp#1`
- **`Track A: header canon, um->µm, stale open-item cleanup`** — `trackA_conformance_20260824.py`
- **`Add Column E cross-TAPP uniformity check (Rule 7.8.10)`** — the check itself, with
  `triage_colE_uniformity_20260824.py` triaging what it found

The Detection Limit and SEM fixes are the two that bumped TAPP versions.

## Verification

Not recorded. `Add Column E cross-TAPP uniformity check (Rule 7.8.10)` means the
validator itself changed on this date, so no single before/after result would characterise it.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
