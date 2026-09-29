# Superseded TAPPs — 2026-09-29

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor | Pass |
|---|---|---|
| `EPMA_TAPP_v81` | `v82` | Column F |
| `LA-MC-ICPMS_TAPP_v86` | `v87` | Column F |
| `LA-MC-ICPMS_UPb_TAPP_v83` | `v84` | Column F |
| `LA-Q-ICP-MS_TAPP_v91` | `v92` | Column F |
| `LA-Q-ICP-MS_UPb_TAPP_v91` | `v92` | Column F |
| `LA-SF-ICP-MS_TAPP_v88` | `v89` | Column F |
| `LA-SF-ICP-MS_UPb_TAPP_v89` | `v90` | Column F |
| `SEM_Composition_TAPP_v78` | `v79` | Column F |
| `SEM_TAPP_v79` | `v80` | Column F |
| `Solution_MC-ICP-MS_TAPP_v87` | `v88` | Column F |
| `Solution_Q-ICP-MS_TAPP_v90` | `v91` | Column F |
| `Solution_SF-ICP-MS_TAPP_v85` | `v86` | Column F |
| `TEM_TAPP_v63` | `v64` | Column F |
| `EPMA_TAPP_v82` | `v83` | EPMA pilot |

14 version(s), 28 file(s) (CSV + xlsx). EPMA was bumped twice, once per pass.

## Why

**First pass — Column F describes one member's value.** Conventions 7.3.4, written this day, says a
keyed field's Column F is what one member's input box accepts, with no member labels. 139 rows in 13
TAPPs carried labels ('SiO2: 0.02 wt%', 'Smithsonian anorthite (Si Ka, Al Ka, Ca Ka)', 'Si=Sp1;
Ti=Sp2', 'ArCl+ on 75As'), and each was rewritten by hand to the value alone. In the same pass:
- `Acquisition Pass` examples moved to definer-cell form.
- `Plasma Thermal Mode` lost `Mixed: specify mode per analytical sub-run`, since the field is keyed by
  acquisition pass. This reverses the 2026-08-30 harmonisation.
- Module_UPb v9 → v10 (its two Column F overlays) and Module_ICPMS v16 → v17 (six defaults).

Applied by `Project Files/Scripts/colf_value_only_20260929.py`.

**Second pass — the EPMA pilot of the keyed-value notation.** Every keyed and definer literature
cell in EPMA's 15 procedure columns was rewritten into the notation (156 cells), re-reading each
source paper. Converting needs the paper, and the reading corrected extraction errors: inferred
values, values with no source, and stated values the cells had missed. The script's docstring lists
them. Applied by `Project Files/Scripts/epma_keyed_pilot_20260929.py`. v83 was first written with
`Kα` in `X-ray Line`, which the controlled list spells `Ka`. That uncommitted v83 was discarded,
v82 restored from this folder, and the corrected script re-applied as v83.

## Verification

- `compose_tapp.py --check`: 0 of 16 drifted, before and after each pass.
- `validate_tapp.py`: 0 ERROR, 0 WARN after each pass. The new check `keyed-cell` (7.3.4) reports
  the other TAPPs' backlog at INFO. EPMA is in `KEYED_NOTATION_ENFORCED`, so a regression there is
  WARN. Two EPMA cells are registered in `KEYED_CELL_EXCEPTIONS` (Ma+2017 detection limit and
  accuracy, stated per element against oxide reported properties).
- `audit_keys_vs_literature.py`: 0 NEW. One new finding (`X-ray Line` read as target species) was
  adjudicated CONSISTENT: monitored elements and target species share names in EPMA.
- The form mockups were rebuilt against EPMA v83 and LA-MC v87, and the reviewer workbooks
  regenerated as v83. The v81 and v82 workbooks were removed.
- Changed: Column F in 139 TAPP rows and 8 module rows; 156 EPMA literature cells. No field, tier,
  data type or `Keyed By` value changed. One controlled-list member was removed (`Plasma Thermal Mode`).
