# Superseded TAPPs — 2026-09-15

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v68` | `v69` |
| `LA-MC-ICPMS_TAPP_v78` | `v79` |
| `LA-MC-ICPMS_UPb_TAPP_v77` | `v78` |
| `LA-Q-ICP-MS_TAPP_v79` | `v80` |
| `LA-Q-ICP-MS_UPb_TAPP_v79` | `v80` |
| `LA-SF-ICP-MS_TAPP_v76` | `v77` |
| `LA-SF-ICP-MS_UPb_TAPP_v77` | `v78` |
| `Lab-XCT_TAPP_v39` | `v40` |
| `SEM_Composition_TAPP_v64` | `v65` |
| `SEM_FIBSEM_TAPP_v32` | `v33` |
| `SEM_Imaging_TAPP_v31` | `v32` |
| `SEM_TAPP_v65` | `v66` |
| `Solution_MC-ICP-MS_TAPP_v79` | `v80` |
| `Solution_Q-ICP-MS_TAPP_v82` | `v83` |
| `Solution_SF-ICP-MS_TAPP_v78` | `v79` |
| `TEM_TAPP_v51` | `v52` |

16 version(s), 32 file(s) (CSV + xlsx).

## Why

**`Sample Persistent Identifier` became analysis-only: C went from Advanced to N/A.** The change was
made once, in Module_Core (v6 → v7), and recomposition carried it into all 16 TAPPs. Script:
`../../Project Files/Scripts/sample_pid_analysis_only_20260915.py`.

- **What was raised.** amds-ldeo/tapp#7 (Stephen Richard): the field identifies the samples listed
  in `Sample Name`, which is C=N/A, so it should be analysis-only too.
- **The library already reasoned that way.** Rule 13 gives `Sample Name` C=N/A because the
  procedure is sample-neutral. That ground applies equally to the samples' identifiers.
- **The data type agrees.** The field is typed `URI / IGSN`, and a registered procedure has no
  sample whose IGSN it could hold.
- **The earlier reason no longer stands.** C=Advanced was set on 2026-08-08 so that a procedure
  could declare it *expects* identifiers. That is a policy, not an identifier. No procedure column
  ever held one here, and if such a policy is wanted it belongs in a separate field.

**Unchanged:**
- D stays Advanced, optional at analysis time, because IGSN registration is not universal.
- `Keyed By` stays `sample`.
- The data type stays `URI / IGSN`.
- C=N/A with D=Advanced is a legal pair, which the schema README's tier table maps to "absent" from
  the procedure schema and "optional, supplied fresh" in the analysis schema.

**Updated to match:**
- `conventions.md`: the Rule 13 table and its reasoning. The C=N/A statement now covers all three
  Rule 13 fields.
- `precedents.md`: a dated note on the entry that recorded C=Advanced.
- `README_TAPP_for_Schema_Generation.md`: the §10 row now states the tiers.
- The three mockups: rebuilt against EPMA v69 and LA-MC v79, since each procedure form lost one
  field. `cfg.json`'s hand-written footer counts now match the rebuild: EPMA 72, LA-MC 124 → 123.

## Verification

- **Cell-level diff** of all 16 superseded/successor pairs: only 32 cells changed, `Sample
  Persistent Identifier` Column C (16) and Last Update (16). Row counts, headers and field sets are
  unchanged in every TAPP.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- **Key audit:** `audit_keys_vs_literature.py` regenerated. Its 60 changed lines differ only in file
  version and row position; no finding changed. No Column I key or literature column was touched.
- **Registers:** `build_module_register.py --check` and `build_schema_spec_counts.py` are current;
  the schema-spec counts did not move, as a tier change should not move them.
  `TAPP_Composed_Variants.csv` was advanced by composition itself.
- **Validator:** `validate_tapp.py` reported 0 ERROR / 0 WARN before the save.
