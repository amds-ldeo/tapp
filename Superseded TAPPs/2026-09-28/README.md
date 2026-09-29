# Superseded TAPPs — 2026-09-28

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.


## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v77` | `v78` |
| `LA-MC-ICPMS_TAPP_v83` | `v84` |
| `LA-MC-ICPMS_UPb_TAPP_v80` | `v81` |
| `LA-Q-ICP-MS_TAPP_v88` | `v89` |
| `LA-Q-ICP-MS_UPb_TAPP_v88` | `v89` |
| `LA-SF-ICP-MS_TAPP_v85` | `v86` |
| `LA-SF-ICP-MS_UPb_TAPP_v86` | `v87` |
| `Lab-XCT_TAPP_v42` | `v43` |
| `SEM_Composition_TAPP_v73` | `v74` |
| `SEM_FIBSEM_TAPP_v39` | `v40` |
| `SEM_Imaging_TAPP_v38` | `v39` |
| `SEM_TAPP_v74` | `v75` |
| `Solution_MC-ICP-MS_TAPP_v84` | `v85` |
| `Solution_Q-ICP-MS_TAPP_v87` | `v88` |
| `Solution_SF-ICP-MS_TAPP_v82` | `v83` |
| `TEM_TAPP_v60` | `v61` |

16 version(s), 32 file(s) (CSV + xlsx).

## Why

Module_Core v8 → v9. `Sample Preparation Method` was re-keyed `(none)` → `sample`, as Rule 13
already required (gap 5 of `Claude Skills for TAPP/analysis/Pending_Gaps_2026-09-24_Reference_Example.md`).
All 16 TAPPs consume Core, so each was recomposed and bumped once.

In the same pass, `Monitored Elements` in EPMA, SEM and SEM_Composition gained one sentence: a
target species determined by stoichiometry or by difference has no monitored element (gap 6).

Applied by `Project Files/Scripts/gaps5and6_sample_prep_key_20260928.py`. The rule that makes the
re-key coherent at procedure level — projection — was written into conventions.md as 7.3.3 on the
same day.

## Verification

- **Before the patch:** `compose_tapp.py --check` reported 0 of 16 TAPPs drifted.
- **After the patch:** `compose_tapp.py --check` again reported 0 of 16 drifted.
- **`validate_tapp.py`:** 0 ERROR, 0 WARN. The bump raised four `doc-stale-version-ref` WARNs, and all four were resolved:
  - the three form mockups were rebuilt against EPMA v78 and LA-MC v84;
  - the reviewer workbooks were regenerated as v78;
  - the v77 worked example and the round-trip test were registered as historical records.
- **`audit_keys_vs_literature.py`:** 0 NEW findings (73 already adjudicated).

What changed:
- **Keyed By:** one value, `Sample Preparation Method`, `(none)` → `sample`, in all 16 TAPPs.
- **Column B:** one description, `Monitored Elements`, in 3 TAPPs.
- **Nothing else:** no field was added or removed, and no tier or data type changed.
