# Superseded TAPPs — 2026-09-28

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.


## What was superseded, and by what

| Superseded | Successor | Pass |
|---|---|---|
| `EPMA_TAPP_v77` | `v78` | gaps 5 and 6 |
| `LA-MC-ICPMS_TAPP_v83` | `v84` | gaps 5 and 6 |
| `LA-MC-ICPMS_UPb_TAPP_v80` | `v81` | gaps 5 and 6 |
| `LA-Q-ICP-MS_TAPP_v88` | `v89` | gaps 5 and 6 |
| `LA-Q-ICP-MS_UPb_TAPP_v88` | `v89` | gaps 5 and 6 |
| `LA-SF-ICP-MS_TAPP_v85` | `v86` | gaps 5 and 6 |
| `LA-SF-ICP-MS_UPb_TAPP_v86` | `v87` | gaps 5 and 6 |
| `Lab-XCT_TAPP_v42` | `v43` | gaps 5 and 6 |
| `SEM_Composition_TAPP_v73` | `v74` | gaps 5 and 6 |
| `SEM_FIBSEM_TAPP_v39` | `v40` | gaps 5 and 6 |
| `SEM_Imaging_TAPP_v38` | `v39` | gaps 5 and 6 |
| `SEM_TAPP_v74` | `v75` | gaps 5 and 6 |
| `Solution_MC-ICP-MS_TAPP_v84` | `v85` | gaps 5 and 6 |
| `Solution_Q-ICP-MS_TAPP_v87` | `v88` | gaps 5 and 6 |
| `Solution_SF-ICP-MS_TAPP_v82` | `v83` | gaps 5 and 6 |
| `TEM_TAPP_v60` | `v61` | gaps 5 and 6 |
| `EPMA_TAPP_v78` | `v79` | gap 1 |
| `LA-MC-ICPMS_TAPP_v84` | `v85` | gap 1 |
| `LA-MC-ICPMS_UPb_TAPP_v81` | `v82` | gap 1 |
| `LA-Q-ICP-MS_TAPP_v89` | `v90` | gap 1 |
| `LA-Q-ICP-MS_UPb_TAPP_v89` | `v90` | gap 1 |
| `LA-SF-ICP-MS_TAPP_v86` | `v87` | gap 1 |
| `LA-SF-ICP-MS_UPb_TAPP_v87` | `v88` | gap 1 |
| `Lab-XCT_TAPP_v43` | `v44` | gap 1 |
| `SEM_Composition_TAPP_v74` | `v75` | gap 1 |
| `SEM_FIBSEM_TAPP_v40` | `v41` | gap 1 |
| `SEM_Imaging_TAPP_v39` | `v40` | gap 1 |
| `SEM_TAPP_v75` | `v76` | gap 1 |
| `Solution_MC-ICP-MS_TAPP_v85` | `v86` | gap 1 |
| `Solution_Q-ICP-MS_TAPP_v88` | `v89` | gap 1 |
| `Solution_SF-ICP-MS_TAPP_v83` | `v84` | gap 1 |
| `TEM_TAPP_v61` | `v62` | gap 1 |

32 version(s), 64 file(s) (CSV + xlsx): every TAPP was bumped twice on this date, once per pass.

## Why

**First pass — gaps 5 and 6.**


Module_Core v8 → v9. `Sample Preparation Method` was re-keyed `(none)` → `sample`, as Rule 13
already required (gap 5 of `Claude Skills for TAPP/analysis/Pending_Gaps_2026-09-24_Reference_Example.md`).
All 16 TAPPs consume Core, so each was recomposed and bumped once.

In the same pass, `Monitored Elements` in EPMA, SEM and SEM_Composition gained one sentence: a
target species determined by stoichiometry or by difference has no monitored element (gap 6).

Applied by `Project Files/Scripts/gaps5and6_sample_prep_key_20260928.py`. The rule that makes the
re-key coherent at procedure level — projection — was written into conventions.md as 7.3.3 on the
same day.

**Second pass — gap 1.** Module_Core v9 → v10: `Target Material` becomes `defines: target material` in
all 16 TAPPs, exempt from 7.4c where nothing is keyed by it. EPMA then changes in four ways:
- **Beam fields.** The five point-analysis beam fields are keyed `target material` and flagged for point modes only.
- **Mapping twins.** New `Mapping Beam Mode`, `Mapping Beam Current` and `Mapping Beam Diameter`, flagged for the mapping modes and keyed per map.
- **Link field.** New `Target Material of Sampling Unit`, which links each analysis point to its material.
- **Literature cells.** Map conditions in the Liu+2016_UT, Frank+2023, Broussard+2026 and Neuman+2025 columns move to the mapping twins.

Applied by `Project Files/Scripts/gap1_target_material_20260928.py`.

## Verification

- **Before the patch:** `compose_tapp.py --check` reported 0 of 16 TAPPs drifted.
- **After the patch:** `compose_tapp.py --check` again reported 0 of 16 drifted, after each of the two passes.
- **`validate_tapp.py`:** 0 ERROR, 0 WARN. The bump raised four `doc-stale-version-ref` WARNs, and all four were resolved:
  - the three form mockups were rebuilt against EPMA v78 and LA-MC v84;
  - the reviewer workbooks were regenerated as v78;
  - the v77 worked example and the round-trip test were registered as historical records.
- **`audit_keys_vs_literature.py`:** 0 NEW findings (73 already adjudicated).

What changed:
- **Keyed By:** one value, `Sample Preparation Method`, `(none)` → `sample`, in all 16 TAPPs.
- **Column B:** one description, `Monitored Elements`, in 3 TAPPs.
- **Nothing else:** no field was added or removed, and no tier or data type changed.

**Second pass (gap 1).**
- `validate_tapp.py`: 0 ERROR, 0 WARN. Reaching that took three registrations:
  - the SEM beam-key divergence, in `KEYED_BY_TECHNIQUE_DEPENDENT`;
  - the three point/map name pairs, in `KEY_NAME_VARIANT_EXEMPT`;
  - `Target Material of Sampling Unit`, in `TARGET_EXEMPT`.
- The mockups were rebuilt against v79 / v85, and the reviewer workbooks regenerated as v79.
- `audit_keys_vs_literature.py`: the one new finding (`Beam Damage Minimization` observed as per-`sampling unit`) was answered by `KEY_SUBSUMES["target material"] = {"sampling unit"}`. The detector reads phase names as sampling units. The four beam adjudications were rewritten for the new key. Result: 0 NEW.
- Changed:
  - Keyed By: 1 value in Core (16 TAPPs) and 5 in EPMA.
  - Mode flags: 4 EPMA fields, YYYY → YNYN.
  - Fields: 4 added to EPMA.
  - Literature cells: 11 edited or created in the four mapping-reporting columns.
  - Tiers and data types of existing fields: none.

