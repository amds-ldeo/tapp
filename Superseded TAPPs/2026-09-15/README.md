# Superseded TAPPs — 2026-09-15

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v68` | `v70` |
| `EPMA_TAPP_v69` | `v70` |
| `LA-MC-ICPMS_TAPP_v78` | `v80` |
| `LA-MC-ICPMS_TAPP_v79` | `v80` |
| `LA-MC-ICPMS_UPb_TAPP_v77` | `v79` |
| `LA-MC-ICPMS_UPb_TAPP_v78` | `v79` |
| `LA-Q-ICP-MS_TAPP_v79` | `v81` |
| `LA-Q-ICP-MS_TAPP_v80` | `v81` |
| `LA-Q-ICP-MS_UPb_TAPP_v79` | `v81` |
| `LA-Q-ICP-MS_UPb_TAPP_v80` | `v81` |
| `LA-SF-ICP-MS_TAPP_v76` | `v78` |
| `LA-SF-ICP-MS_TAPP_v77` | `v78` |
| `LA-SF-ICP-MS_UPb_TAPP_v77` | `v79` |
| `LA-SF-ICP-MS_UPb_TAPP_v78` | `v79` |
| `Lab-XCT_TAPP_v39` | `v40` |
| `SEM_Composition_TAPP_v64` | `v66` |
| `SEM_Composition_TAPP_v65` | `v66` |
| `SEM_FIBSEM_TAPP_v32` | `v33` |
| `SEM_Imaging_TAPP_v31` | `v32` |
| `SEM_TAPP_v65` | `v67` |
| `SEM_TAPP_v66` | `v67` |
| `Solution_MC-ICP-MS_TAPP_v79` | `v81` |
| `Solution_MC-ICP-MS_TAPP_v80` | `v81` |
| `Solution_Q-ICP-MS_TAPP_v82` | `v84` |
| `Solution_Q-ICP-MS_TAPP_v83` | `v84` |
| `Solution_SF-ICP-MS_TAPP_v78` | `v80` |
| `Solution_SF-ICP-MS_TAPP_v79` | `v80` |
| `TEM_TAPP_v51` | `v53` |
| `TEM_TAPP_v52` | `v53` |

29 version(s), 58 file(s) (CSV + xlsx). Thirteen TAPPs appear twice because both passes touched
them; Lab-XCT, SEM_FIBSEM and SEM_Imaging carry no Module_Aggregation fields and appear once.

## Why

Two passes on the same day, each answering one GitHub issue.

### Pass 1 — `Sample Persistent Identifier` becomes analysis-only (amds-ldeo/tapp#7)

`../../Project Files/Scripts/sample_pid_analysis_only_20260915.py`. Module_Core v6 → v7; all 16 TAPPs.

- **The change.** C went from Advanced to N/A. D stays Advanced; key, type and description are
  unchanged.
- **Why.** The field identifies the samples `Sample Name` lists, and Rule 13 already made
  `Sample Name` C=N/A because a procedure is sample-neutral. The identifier inherits that, and a
  `URI / IGSN` field has nothing to hold at procedure level.
- **What was superseded.** The 2026-08-08 reason for C=Advanced, that a procedure could declare it
  expects IGSNs, is a policy rather than an identifier; if it is wanted, it is a separate field.
- **Updated to match:** the Rule 13 table and reasoning in `conventions.md`, a dated note in
  `precedents.md`, and the schema README's §10 row.

### Pass 2 — Module_Aggregation names the level it aggregates (amds-ldeo/tapp#4)

`../../Project Files/Scripts/aggregation_name_the_level_20260915.py`. Module_Aggregation v3 → v4;
its 13 consumers.

**The question.** `Analysis Inclusion and Rejection Criteria` spoke of "individual analyses" and
"points inside a single analysis" without defining either. Schema generation must place the field at
one level, and "analysis" names three things in this library.

**What the literature cells showed** (this field's and `Spike / Outlier Filtering Approach`'s):
- **The contributing units come at three levels:** replicate measurements of one solution or
  location, spots or grains within a sample (Wu 2023: 246 spots, 236 in the weighted mean), and
  independent aliquots or digestions (Willbold 2005). The description now says "individual result":
  one acquisition's own value of the reported quantity. "Replicate" alone would have excluded the
  last two levels.
- **The boundary with filtering is basis, not unit.** `Spike / Outlier Filtering Approach` records
  whole acquisitions discarded on signal grounds (Nakanishi 2022, Chernonozhkin 2021), so the old
  split into "points" versus "whole analyses" did not hold. Signal-based discards stay in that field,
  whose description is unchanged. Result-based selection belongs here.
- **The "point" is a cycle or a scan.** A cycle in simultaneous collection and a scan or sweep in
  sequential collection are the same level under two names. The description names them without
  naming either field, because neither exists in all 13 consumers.

**`Goodness-of-Fit or Dispersion Statistic`** now says "contributing individual results" to match.

**Not changed:**
- **The field name.** The description carries the definition; a rename would ripple through
  registers, documents and the downstream schema.
- **Tiers and data type.**
- **The key,** still `(none)`, but flagged: the outcome counts ("how many obtained, how many
  included") vary per aggregate, which is a Rule 7 question for a separate decision.
- **Some existing literature cells now sit awkwardly** under the sharper definition. Zhang 2022
  (LA-MC) and Pringle & Moynier 2017 describe within-acquisition discards, which is signal
  filtering. López-García 2026 and Makishima 2011 describe excluding a whole species or channel.
  They are recorded here for a follow-up pass, not moved.

**Mockups.** All three were rebuilt after each pass (EPMA v69, then v70; LA-MC v79, then v80). Pass 1
removed one procedure-level field, so `cfg.json`'s hand-written footer counts were updated to match
(LA-MC 124 → 123). Pass 2 changed no counts.

## Verification

**Pass 1.**
- **Cell-level diff:** 32 cells, `Sample Persistent Identifier` Column C and Last Update, once per
  TAPP.

**Pass 2.**
- **Cell-level diff:** 52 cells, Column B and Last Update of the two Aggregation fields, once per
  consumer.

**Both passes.**
- **Structure:** row counts, headers and field sets unchanged in every TAPP.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- **Key audit:** `audit_keys_vs_literature.py` regenerated; lines changed only in file version and
  row position, and no finding changed.
- **Registers:** `build_module_register.py --check` and `build_schema_spec_counts.py` are current.
- **Validator:** `validate_tapp.py` reported 0 ERROR / 0 WARN before the save.
