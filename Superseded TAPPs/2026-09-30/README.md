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

3 version(s), 6 file(s) (CSV + xlsx).

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
