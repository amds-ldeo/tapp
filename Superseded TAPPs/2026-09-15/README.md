# Superseded TAPPs — 2026-09-15

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v68` | `v72` |
| `EPMA_TAPP_v69` | `v72` |
| `EPMA_TAPP_v70` | `v72` |
| `EPMA_TAPP_v71` | `v72` |
| `LA-MC-ICPMS_TAPP_v78` | `v82` |
| `LA-MC-ICPMS_TAPP_v79` | `v82` |
| `LA-MC-ICPMS_TAPP_v80` | `v82` |
| `LA-MC-ICPMS_TAPP_v81` | `v82` |
| `LA-MC-ICPMS_UPb_TAPP_v77` | `v80` |
| `LA-MC-ICPMS_UPb_TAPP_v78` | `v80` |
| `LA-MC-ICPMS_UPb_TAPP_v79` | `v80` |
| `LA-Q-ICP-MS_TAPP_v79` | `v83` |
| `LA-Q-ICP-MS_TAPP_v80` | `v83` |
| `LA-Q-ICP-MS_TAPP_v81` | `v83` |
| `LA-Q-ICP-MS_TAPP_v82` | `v83` |
| `LA-Q-ICP-MS_UPb_TAPP_v79` | `v83` |
| `LA-Q-ICP-MS_UPb_TAPP_v80` | `v83` |
| `LA-Q-ICP-MS_UPb_TAPP_v81` | `v83` |
| `LA-Q-ICP-MS_UPb_TAPP_v82` | `v83` |
| `LA-SF-ICP-MS_TAPP_v76` | `v80` |
| `LA-SF-ICP-MS_TAPP_v77` | `v80` |
| `LA-SF-ICP-MS_TAPP_v78` | `v80` |
| `LA-SF-ICP-MS_TAPP_v79` | `v80` |
| `LA-SF-ICP-MS_UPb_TAPP_v77` | `v81` |
| `LA-SF-ICP-MS_UPb_TAPP_v78` | `v81` |
| `LA-SF-ICP-MS_UPb_TAPP_v79` | `v81` |
| `LA-SF-ICP-MS_UPb_TAPP_v80` | `v81` |
| `Lab-XCT_TAPP_v39` | `v41` |
| `Lab-XCT_TAPP_v40` | `v41` |
| `SEM_Composition_TAPP_v64` | `v67` |
| `SEM_Composition_TAPP_v65` | `v67` |
| `SEM_Composition_TAPP_v66` | `v67` |
| `SEM_FIBSEM_TAPP_v32` | `v34` |
| `SEM_FIBSEM_TAPP_v33` | `v34` |
| `SEM_Imaging_TAPP_v31` | `v33` |
| `SEM_Imaging_TAPP_v32` | `v33` |
| `SEM_TAPP_v65` | `v68` |
| `SEM_TAPP_v66` | `v68` |
| `SEM_TAPP_v67` | `v68` |
| `Solution_MC-ICP-MS_TAPP_v79` | `v83` |
| `Solution_MC-ICP-MS_TAPP_v80` | `v83` |
| `Solution_MC-ICP-MS_TAPP_v81` | `v83` |
| `Solution_MC-ICP-MS_TAPP_v82` | `v83` |
| `Solution_Q-ICP-MS_TAPP_v82` | `v86` |
| `Solution_Q-ICP-MS_TAPP_v83` | `v86` |
| `Solution_Q-ICP-MS_TAPP_v84` | `v86` |
| `Solution_Q-ICP-MS_TAPP_v85` | `v86` |
| `Solution_SF-ICP-MS_TAPP_v78` | `v82` |
| `Solution_SF-ICP-MS_TAPP_v79` | `v82` |
| `Solution_SF-ICP-MS_TAPP_v80` | `v82` |
| `Solution_SF-ICP-MS_TAPP_v81` | `v82` |
| `TEM_TAPP_v51` | `v54` |
| `TEM_TAPP_v52` | `v54` |
| `TEM_TAPP_v53` | `v54` |

54 version(s), 108 file(s) (CSV + xlsx). Six passes touched the library today; several TAPPs
were superseded by four or five of them.

## Why

Six passes on the same day: three answering GitHub issues, then three batches of the literature pass the third made necessary.

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

### Pass 3 — `Sampling Unit` split into a type and a named list of units (amds-ldeo/tapp#8)

`../../Project Files/Scripts/split_sampling_unit_20260915.py`. Module_Core v7 → v8; all 16 TAPPs.

**The defect.** `Sampling Unit` was keyed `defines: sampling unit`, but its values are types (Grain |
Spot | Phase …), and a type cannot list a domain's members (7.4a). The 46 field-instances keyed
`sample > sampling unit` therefore had child tables with no rows to attach to, and nothing tied a unit
to its sample.

**The change**, per the proposal's five decisions (all taken as recommended):
- **`Sampling Unit Type`** (renamed): C=Basic, **D=Read-Only**, keyed **`(none)`**. Its type list and
  literature cells are unchanged.
- **`Sampling Unit Name`** (new, directly after): C=N/A, D=Basic, Text (free), keyed
  **`defines: sample > sampling unit`**. That is a new containment-definer form whose parent is
  required, unlike `per`'s nullable one. Its literature cells start blank.

**Tooling changed in the same pass:**
- **`validate_tapp.py`**
  - parses `defines: A > B`;
  - requires both Rule 9 fields;
  - registers the old name as retired, with a guard for the live names it heads.
- **`build_schema_spec_counts.py`** now resolves its root from its own location. A hardcoded root made
  the sandbox check the real library; nothing was written.
- **`_body.html`** (mockup page script) resolves the new definer key.

**Documents:** Rule 9 rewritten; the key-notation tables in `conventions.md` and the schema README
gained the new form; schema README §4, §9 and §10 reworded (§10 is now eight universal fields); the
deferred nested-units note (G2) records that its trigger has been met.

Design, evidence, decisions and the sandbox result:
`../../Project Files/Design Notes/Proposal_Sampling_Unit_Identity_2026-09-15.md`.

### Pass 4 — `Sampling Unit Name` literature, batch 1: the Solution family (29 cells)

`../../Project Files/Scripts/phase3_sampling_unit_name_solution_20260915.py`. Solution MC (14),
Solution Q (9) and Solution SF (6) columns.

Every value was read from the PDF, quoted and paged. The cell grammar:
- **labelled units**, quoted with their sample;
- **"Sample name only"** where the paper identifies units only by the sample's name, as one unit per
  sample or with replicates counted but not labelled;
- **N** where no identifier is stated.

Of the 29: 15 labelled, 12 sample name only, 2 N.

Two neighbouring cells look wrong and were left for a separate pass:
- Nie & Dauphas 2019's `Sample Name` omits its six Apollo samples;
- Barnes 2025 WUSTL's `Sample Name` names the Ti splits, not the WUSTL digest.

### Pass 5 — `Sampling Unit Name` literature, batch 2: the laser-ablation family (28 cells)

`../../Project Files/Scripts/phase3_sampling_unit_name_la_20260915.py`. LA-MC (1), LA-Q (7) and its
U-Pb variant (6), LA-SF (7) and its U-Pb variant (7). Same source rule and cell grammar as pass 4.

- **Tally:** 11 labelled, 17 sample name only, 0 N.
- **U-Pb variants:** they share their literature columns with the base TAPPs and received
  byte-identical cells.
- **Two limits are stated in the cells:**
  - where a flattened table hides which label belongs to which meteorite, the labels are quoted
    without asserting a pairing;
  - where the unit list is in a supplement not in the archived PDF, the cell says so.

**Fixed by hand after the pass:** `TAPP_Composed_Variants.csv` still named the pre-pass LA-Q and
LA-SF U-Pb versions, for the same reason as on 2026-09-11: a patch that bumps a TAPP without
composing it does not advance that register. Both paths were set, and the LA-MC mockup was rebuilt
from v82.

### Pass 6 — `Sampling Unit Name` literature, batch 3: EPMA (15 cells)

`../../Project Files/Scripts/phase3_sampling_unit_name_epma_20260915.py`. Same source rule and cell
grammar as passes 4–5.

**One EPMA-specific convention.** A reported row is usually a point inside a grain inside a section,
and papers label different levels. Each cell states the **finest level the paper labels** (section,
split, particle or grain) and says when the points themselves are unlabelled or only in a supplement.
This is D4 applied: where points are not named, the named containing area stands for them.

- **Tally:** 11 labelled, 3 of them at section level only; 2 sample name only; 2 N.
- **The two N cells** are McCoy 2025 (both labs), whose microprobe passages name no specimen. The
  curation numbers the paper does give identify figure images, not analyses, and were not borrowed.

**Mockups.** All three were rebuilt after each pass (EPMA v69, then v70; LA-MC v79, then v80). Pass 1
removed one procedure-level field, so `cfg.json`'s hand-written footer counts were updated to match
(LA-MC 124 → 123). Pass 2 changed no counts; pass 3 added only an analysis-level field, so the procedure forms kept their counts, and the pages were rebuilt against EPMA v71 and LA-MC v81.

## Verification

**Pass 1.**
- **Cell-level diff:** 32 cells, `Sample Persistent Identifier` Column C and Last Update, once per
  TAPP.

**Pass 2.**
- **Cell-level diff:** 52 cells, Column B and Last Update of the two Aggregation fields, once per
  consumer.

**Pass 3.**
- **Cell-level diff:** in every TAPP, exactly +1 row (`Sampling Unit Name`, directly after the type,
  literature cells blank). The renamed row changed in A, B, D, H and I only. Every other row is
  byte-identical, including all 46 consumers.
- **Rule 7.4a/b/c** pass with the new definer.
- **The same change was first run on a sandbox copy,** with identical results.

**Pass 4.**
- **Cell-level diff:** exactly 29 cells changed, all in `Sampling Unit Name` literature columns.
- **Rows:** no row added or removed.

**Pass 5.**
- **Cell-level diff:** exactly 28 cells changed, all in `Sampling Unit Name` literature columns.
- **Rows:** no row added or removed.
- **U-Pb variants:** their shared columns are identical to the base TAPPs'.

**Pass 6.**
- **Cell-level diff:** exactly 15 cells changed, all in `Sampling Unit Name` literature columns.
- **Rows:** no row added or removed.
- **Mockups:** both EPMA mockups rebuilt from v72, with counts unchanged.

**All passes.**
- **Structure:** row counts, headers and field sets unchanged in every TAPP.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- **Key audit:** `audit_keys_vs_literature.py` regenerated; lines changed only in file version and
  row position, and no finding changed.
- **Registers:** `build_module_register.py --check` and `build_schema_spec_counts.py` are current.
- **Validator:** `validate_tapp.py` reported 0 ERROR / 0 WARN before the save.
