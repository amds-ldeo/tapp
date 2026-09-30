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

5 version(s), 10 file(s) (CSV + xlsx).

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
