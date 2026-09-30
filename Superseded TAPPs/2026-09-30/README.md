# Superseded TAPPs — 2026-09-30

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor | Pass |
|---|---|---|
| `Lab-XCT_TAPP_v44` | `v45` | keyed notation |
| `TEM_TAPP_v66` | `v67` | keyed notation |
| `LA-MC-ICPMS_TAPP_v89` | `v90` | keyed notation |
| `EPMA_TAPP_v86` | `v87` | empty column removed |
| `Lab-XCT_TAPP_v45` | `v46` | empty column removed |
| `LA-MC-ICPMS_TAPP_v90` | `v91` | Sample Form retired |
| `LA-MC-ICPMS_UPb_TAPP_v85` | `v86` | Sample Form retired |
| `LA-Q-ICP-MS_TAPP_v94` | `v95` | Sample Form retired |
| `LA-Q-ICP-MS_UPb_TAPP_v94` | `v95` | Sample Form retired |
| `LA-SF-ICP-MS_TAPP_v91` | `v92` | Sample Form retired |
| `LA-SF-ICP-MS_UPb_TAPP_v92` | `v93` | Sample Form retired |
| `Lab-XCT_TAPP_v46` | `v47` | prep Method assessed, Notes retired |
| `LA-Q-ICP-MS_TAPP_v95` | `v96` | keyed notation, re-read |
| `LA-Q-ICP-MS_UPb_TAPP_v95` | `v96` | keyed notation, re-read |

14 version(s), 28 file(s) (CSV + xlsx).

## Why

**The keyed-value notation (conventions 7.3.4) for the three smallest TAPPs in the backlog.** Converted as
SEM was on 2026-09-29. Definer cells open with a member list, and the original cell follows as commentary,
so no transcribed quote is lost. Target Material names what was analysed, not the sample. Keyed value cells
take `all:` or name their members. Cells that already parsed were reviewed for meaning too; in TEM, most
Target Material and several Target Species cells parsed only by accident. The changes:
- Lab-XCT: 1 cell.
- TEM: 46 cells.
- LA-MC: 28 cells.

LA-MC is the first ICP-MS-style TAPP converted and sets the pattern for the others:
- acquisition-pass fields key to the one pass;
- monitored masses bind to their target species with `→ Sr`, and interference monitors with `→ none`;
- `standard x reported property` and `target material x target species` cells use `all [ … ]`.

One of the cells was task 3's `Combination Method` for Zhang+2022, which had a `;` inside its value. All
three TAPPs join `KEYED_NOTATION_ENFORCED`. Applied by
`Project Files/Scripts/keyed_notation_tem_xct_lamc_20260930.py`.

## Verification

- The edits were simulated before being applied: every structured cell in the three TAPPs parses and names
  only definer members.
- `compose_tapp.py --check`: 16 of 16 match.
- `validate_tapp.py`: 0 ERROR, 0 WARN, with the three TAPPs now enforced. The LA-MC form mockup was rebuilt at
  v90 and still prefills 92 fields.
- `audit_keys_vs_literature.py`: 0 NEW.
- Changed: 75 literature cells; no field, tier, data type or key.

## EPMA v86 → v87: an empty literature column removed

EPMA v86 had a literature column with no header and no content in any row, between Barnes+2025 (NHM
London) and Neuman+2025. It described no procedure, showed as a blank column in the xlsx and the review
workbook, and put Neuman+2025 at column index 30. v87 removes it, and puts the Neuman+2025 header on one
line with ` | ` separators like the others; the round-trip records already used that form. Nothing else
changed: no field, tier, data type, key or literature cell. Applied by
`Project Files/Scripts/epma_remove_empty_column_20260930.py`.

Re-issued at v87: the five review workbooks and the two EPMA form mockups (the Neuman mockup's `litcol`
moves from 30 to 29). The narrative, worked example and methods section stay at v86, since their content
still holds; the v86 example joins `HISTORICAL_DOCS`.

### Verification

- All 106 data rows are identical to v86 once the removed column is set aside.
- `compose_tapp.py --check`: 16 of 16 match.
- `validate_tapp.py`: 0 ERROR, 0 WARN.
- `audit_keys_vs_literature.py`: 0 NEW.
- Both EPMA mockups are byte-identical to their v86 builds apart from the version string.

## Lab-XCT v45 → v46: the same defect, and a validator check for it

A scan of all 16 TAPPs for EPMA's defect found one more: Lab-XCT's last literature column, after Tait
2014, had no header. v21–v28 carried an unheaded spacer before Charles et al. and Treiman et al.; when
those two off-scope papers were removed on 2026-08-30 (v32), the spacer stayed and ended up last. Its
only content was a surplus `N` in Sample Preparation Method, whose other 14 cells are also `N`, so no
row was shifted. v46 removes it. Lab-XCT's multi-line headers are its own style and were left alone.
Applied by `Project Files/Scripts/labxct_remove_empty_column_20260930.py`.

`validate_tapp.py` gains `lit-column-unheaded` (ERROR) and `lit-column-empty` (WARN). Neither spacer
had been seen by any check: `check_keyed_cells` skips unheaded columns, so their cells were never
parsed. The new check fires on the parked EPMA v86 and Lab-XCT v45 and on no live TAPP.

Found in passing and **not** addressed here: Lab-XCT's Core-module `Sample Preparation Method` reads `N`
for all 14 papers, while its own `Sample Preparation Notes` holds preparation details for 12 of them.

### Verification

- All 101 data rows are identical to v45 once the removed column is set aside.
- `compose_tapp.py --check`: 16 of 16 match.
- `validate_tapp.py`: 0 ERROR, 0 WARN.
- `audit_keys_vs_literature.py`: 0 NEW.

## The six LA TAPPs: `Sample Form / Analytical Substrate` retired

The field restated Module_Core's `Sample Preparation Method` for one technique ("the form as it enters
the ablation cell"), so it failed Rule 6.1. Across the 15 distinct literature columns it held nothing
that `Sample Preparation Method` or a neighbouring field did not already hold. 4 of its cells
contradicted `Sample Preparation Method`, and 2 had lost content. Its key, `(none)`, also disagreed
with Core's `sample`. Module_LaserAblation went from v11 to v12 (29 → 28 fields). In the six TAPPs:
- the row was dropped;
- `Sample Preparation Method`'s Column F gained the two pellet values, and `Liquid` was dropped;
- in LA-Q, the Wu+2023 `Sample Preparation Method` cell was corrected from sample provenance to `N`.

Applied by `Project Files/Scripts/retire_sample_form_20260930.py`. The reasoning is in precedents.md,
2026-09-30. The LA-MC Spot mockup was rebuilt at v91.

### Verification

- Each new version differs from its predecessor in exactly: one row removed, `Sample Preparation
  Method` Column F and Last Update, and (LA-Q only) the Wu+2023 cell. Row order is otherwise identical.
- `compose_tapp.py --check`: 16 of 16 match.
- `validate_tapp.py`: 0 ERROR, 0 WARN, 944 INFO, unchanged from before the pass. `RETIRED_FIELDS`
  gained the field name.
- `audit_keys_vs_literature.py`: 0 NEW.
- The LA-MC Spot mockup differs from its v90 build only in the removed field, the two new values and the
  version string (123 procedure-level fields, 91 prefilled).

## Lab-XCT v46 → v47: `Sample Preparation Method` assessed, `Sample Preparation Notes` retired

This is the item the v46 section left open. Method (Module_Core, keyed `sample`) had joined Lab-XCT on
2026-08-27 but had never been assessed. Its 14 cells are now filled from the papers, re-read on
2026-09-30: 13 attested, and Eckley 2024 stays `N`. Each cell is one form plus quoted commentary
(7.3.3). Richard C–I names its per-sample forms in the commentary.

With Method filled, the TAPP-local free-text `Sample Preparation Notes` had nothing left to hold:
- forms and preparation steps belong to Method;
- holders and containment belong to `Sample Mounting Method`;
- post-scan steps were outside its "before scanning" scope.

So the user decided to retire it. Two containment facts moved into `Sample Mounting Method`: Neuman
73001's retained steel sleeve, and Shearer's scan inside the unopened 73001 CSVC. Method's Column F
dropped its two holder terms, which duplicated Mounting's list. It gained "Separated grain or crystal"
and "Polished section or chip". Re-reading also corrected four Notes cells (Richard B, Richard C–I,
Shearer CSVC, Tomkinson); see precedents.md, 2026-09-30. No module, tier, data type or key changed.
Applied by `Project Files/Scripts/labxct_retire_prep_notes_20260930.py`.

### Verification

- The dry run changed only the intended cells: Method F, H and 13 literature cells, and Mounting H
  and 2 literature cells. The one row, `Sample Preparation Notes`, was removed, taking v46's 102 rows
  to 101.
- `compose_tapp.py --check`: 16 of 16 match.
- `validate_tapp.py`: 0 ERROR, 0 WARN. The INFO summary is identical to v46's.
- `audit_keys_vs_literature.py`: 0 NEW.

## LA-Q-ICP-MS and its U-Pb twin, v95 → v96: keyed notation, with every cell re-read

The requirement for this conversion was that the literature cells alone must regenerate each paper's
procedure. Each of LA-Q's seven columns was re-read against its paper: methods, instrument tables, table
notes and acknowledgements. Every procedure-level cell was checked, keyed or not. The U-Pb twin carries
columns 1–6 with identical cells, so the same edits apply to it. Its nine geochronology fields, never
assessed, became `N — the procedure reports no date`.

Changed: 347 cells in LA-Q and 376 in the twin. Most are the mechanical clean-ups: page tags dropped, and
"N (reason)" rewritten as "N — reason". The substantive changes, per column, are in the script's dicts:
- **isotopes as target species**, with `Monitored Masses` left `N` (Nakanishi+2022, Liu+2024, which even
  had a nonexistent ²¹Sc);
- **inferences stated as fact**, such as exclusion of inclusion-bearing analyses, "fs laser reduces LIEF"
  for a nanosecond excimer, and ablation times "inferred from typical protocol";
- **another paper's result**: Liu+2025's accuracy cell cited Liu+2024's comparison;
- **stated facts missing**: gas flows, a torch, a second laboratory, internal standards, per-element LODs,
  ARM-1, and the Rösel and Zack uncertainty workflow;
- **study-level grants** recorded as procedure-development funding.

Applied by `Project Files/Scripts/laq_keyed_reverify_20260930.py`. Both TAPPs join `KEYED_NOTATION_ENFORCED`.

**Verification.**
- Before applying, the edited CSVs were simulated. Every structured cell parses and names only definer
  members, and the round-trip (`Project Files/Reports/LAQ_Cells_RoundTrip_2026-09-30/`) recovers **204 of
  204 stated facts (100%), 123 as structure**. The same test on v95 recovers 158 (77%), 41 as structure.
- After applying: `compose_tapp.py --check` 16 of 16 match; `validate_tapp.py` 0 ERROR, 0 WARN, with LA-Q
  enforced.
- `audit_keys_vs_literature.py` raised two findings, both caused by the new wording and both adjudicated
  KEEP: `Laser Spot Path` read 'each spot' in a data-reduction quote, and `Normalization` reads `all:` as
  scalar. So 0 NEW.
- No field, tier, data type or key changed.

