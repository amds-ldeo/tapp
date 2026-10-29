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
