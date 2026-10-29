# Superseded TAPPs — 2026-10-29

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

> **TODO — skeleton.** The table below is generated from the folder contents. The prose
> sections marked TODO still need writing: say WHY these versions were superseded and what
> was verified, then delete this block. See `../2026-09-09/README.md` for a routine bump and
> `../2026-08-10/README.md` for a retirement.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v90` | `v91` |
| `SEM_Composition_TAPP_v85` | `v86` |
| `SEM_TAPP_v87` | `v88` |

3 version(s), 6 file(s) (CSV + xlsx).

## Why

GitHub issues amds-ldeo/tapp #18 (dwell time vs detector live time) and #21 (precision labels).
Applied by `Project Files/Scripts/dwell_live_precision_20261029.py`. All three fields are TAPP-owned,
so no module changed.

- **EPMA `EDS Live Time per Point or Pixel`:** now per point or per pixel, with the description
  identical to SEM's (Rule 2). The EDS Mapping flag went from N to Y, and a mapping example was
  added. The sentence "In EPMA, acquisition is always per point" is gone.
- **EPMA `Dwell Time per Pixel`:** the time the beam dwells on each pixel. For EDS it is the real
  (clock) time, and the description points to the live-time field for the dead-time-corrected time.
  It used to say "For EDS: total live-time per spectrum per pixel".
- **`Analytical Precision` (EPMA, SEM, SEM_Composition):** now opens "Precision of repeated
  measurements…", not "Reproducibility…", and asks whether the repeats were made within one session
  (repeatability) or across sessions (intermediate precision, ISO 5725).

The EPMA review workbooks were regenerated as v91 (`make_review_workbook.py`, with the plain-language
text for all three fields updated to match).

**For the v89 review round** (`TAPPs for review/Sent/2026-10-27_EPMA_v89/`), v91 has the same 93
fields in the same order, so item numbers carry over. Three rows changed:

| Item | Field | v89/v90 | v91 |
|---|---|---|---|
| 4.25 | EDS Live Time per Point or Pixel | per analysis point; EDS Point Analysis only | per point or per pixel; EDS Mapping added |
| 4.27 | Dwell Time per Pixel | for EDS, the live time per pixel | for EDS, the beam's real time per pixel; live time recorded in 4.25 |
| 6.8 | Analytical Precision | "the reproducibility of repeated measurements" | "the precision of repeated measurements", plus within one session or across sessions |

## Verification

- Cell diff against the superseded versions: 12 cells changed. EPMA: Description and Last Update
  for all three fields, plus EDS Live Time's example and EDS Mapping flag. SEM and SEM_Composition:
  Description and Last Update of `Analytical Precision`. No field name, tier, data type or
  `Keyed By` value changed.
- `validate_tapp.py`: 0 ERROR, 0 WARN.
- `recompose_all_20260812.py --check`: 16 MATCH. Recomposing each new version in place left every
  cell unchanged.
- `audit_keys_vs_literature.py`: 0 NEW.
- `sync_current_tapps.py`: 0 to copy, 0 to remove.
- Literature cells were not re-read. None of EPMA's 15 procedures is an EDS procedure, so every
  live-time cell stays N/A. The precision cells answer the same question as before.

---

# Second bump, same day — Rule 14.1 amendment (session statistics)

`superseded_readme.py` never overwrites an existing README, so this section is written by hand.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v91` | `v92` |
| `LA-MC-ICPMS_TAPP_v93` | `v94` |
| `LA-MC-ICPMS_UPb_TAPP_v88` | `v89` |
| `LA-Q-ICP-MS_TAPP_v98` | `v99` |
| `LA-Q-ICP-MS_UPb_TAPP_v98` | `v99` |
| `LA-SF-ICP-MS_TAPP_v95` | `v96` |
| `LA-SF-ICP-MS_UPb_TAPP_v96` | `v97` |
| `SEM_Composition_TAPP_v86` | `v87` |
| `SEM_TAPP_v88` | `v89` |
| `Solution_MC-ICP-MS_TAPP_v93` | `v94` |
| `Solution_Q-ICP-MS_TAPP_v96` | `v97` |
| `Solution_SF-ICP-MS_TAPP_v91` | `v92` |
| `TEM_TAPP_v68` | `v69` |

13 version(s), 26 file(s) (CSV + xlsx).

## Why

The Rule 14.1 amendment, `Claude Skills for TAPP/analysis/Rule14_Amendment_Session_QC_2026-10-29.md`
(fourth draft). RD accepted all six decisions on 2026-10-29. Applied by
`Project Files/Scripts/session_qc_two_level_20261029.py`.

- **A statistic that describes the session as a whole** now states both levels in Column B. The
  procedure holds the method and the expected value (`For the procedure:`), and the session record
  holds the value achieved (`For the session:`). This is conventions 14.6.
- **The precision and accuracy fields** end with the overlap sentence (14.5): where the dataset
  includes the reference-material analyses, the session value must agree with them.
- **Modules:**
  - Module_ICPMS v19 (Within-Session, Accuracy, Between-Session)
  - Module_CompositionQC v8 (Detection Limit)
  - Module_Blank v5 (Procedural Blank Level)
  - Module_UPb v13 (overlay Purpose only)
- **TAPP-owned:** `Analytical Precision` and `Analytical Accuracy` (EPMA, SEM, SEM_Composition), and
  `EDS Detection Limit` and `EELS Detection Limit` (TEM).
- **The one tier change:** `Procedural Blank Level` C N/A → Advanced. Its Purpose now reads "A blank
  that is large relative to the sample, or of unknown composition, biases every result it is
  subtracted from." It previously cited a criterion-versus-measurement split, but no blank criterion
  field exists.

The EPMA review workbooks were regenerated as v92, with plain-language text updated for the four
EPMA fields.

**For the v89 review round** (`TAPPs for review/Sent/2026-10-27_EPMA_v89/`), v92 has the same 93
fields in the same order, so item numbers carry over. Besides the three v91 rows above, four rows
changed:

| Item | Field | v89–v91 | v92 |
|---|---|---|---|
| 5.12 | Procedural Blank Level | procedure tier N/A; "the blank level measured in the session" | procedure tier **Advanced**; expected blank (procedure) and measured blank (session) |
| 6.6 | Detection Limit | "state whether … typical estimate or … session-specific" | typical limits (procedure) and limits achieved in the session |
| 6.8 | Analytical Precision | one value, conditions stated | expected (procedure) and achieved (session), plus the overlap sentence |
| 6.9 | Analytical Accuracy | one value | expected (procedure) and found (session), plus the overlap sentence |

## Verification

- **Cell diff against the superseded versions.** No row was added, removed or reordered, and no field
  name, Data Type, `Keyed By`, Example, mode flag or literature cell changed.
  - EPMA, SEM and SEM_Composition: 9 cells each.
  - The nine ICP-MS TAPPs: 12 each.
  - TEM: 4.
  - Only Description, Last Update, Purpose (blank only) and Procedure-Level Tier (blank only) changed.
- **Each changed field** carries exactly one `For the procedure:` and one `For the session:`
  (asserted in the script).
- **Gates:**
  - `validate_tapp.py`: 0 ERROR, 0 WARN.
  - `recompose_all_20260812.py --check`: 16 MATCH.
  - `audit_keys_vs_literature.py`: 0 NEW.
  - `sync_current_tapps.py`: 0 to copy, 0 to remove.
- **Literature cells were not re-read.** All ~125 positive cells were read for the proposal's third
  draft. They hold methods, typical values or pointers to session tables, and the two-level fields
  accept all three.
