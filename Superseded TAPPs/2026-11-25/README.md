# Superseded TAPPs — 2026-11-25

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v95` | `v96` |
| `Lab-XCT_TAPP_v49` | `v50` |
| `SEM_Composition_TAPP_v90` | `v91` |
| `SEM_TAPP_v92` | `v93` |
| `TEM_TAPP_v71` | `v72` |

5 version(s), 10 file(s) (CSV + xlsx).

## Why

Two issues from SMR, both approved on 2026-11-25, applied in one bump by
`Project Files/Scripts/xct_fields_map_grid_20261125.py`:

- **amds-ldeo/tapp#15, map grids (EPMA, SEM, SEM_Composition, TEM).** Every grid pair now states its
  order, X (along a scan line) first, Y second: `Map Dimensions`, `STEM Scan Dimensions`, `Beam Raster
  Dimensions`, `Step Size / Pixel Size`, `Map Area` (Column B). `Step Size / Pixel Size` and `Map Area`
  were retyped to `Numeric pair (µm x µm)` (Column E), with Column F rewritten to pairs and the
  total-area examples dropped. In SEM and SEM_Composition, `EDS Map Dimensions` was renamed
  `Map Dimensions` (Column A). 27 cells in 13 rows.
- **amds-ldeo/tapp#13, XCT keys (Lab-XCT).** Two new rows: `Detector Gain` (Group 3; Advanced /
  Advanced / Adjustable; `Numeric + unit / Text`) and `Reconstructed Volume Dimensions` (Group 5;
  N/A / Advanced / Not carried over; `Text (free)`). Both are keyed `(none)` and flagged Y in both
  modes. Their 14 literature cells were read from the papers in `XCT/Literature Assessment/`.

Column H is stamped 2026-11-25 on every changed or added row.

## Verification

- Each new table was compared with its predecessor cell by cell. Only the listed rows differ, in the
  listed columns (A, B, E, F and H), and no row moved. Lab-XCT differs only by the two inserted rows.
- All 5 recomposed identically. `validate_tapp.py`: 0 ERROR, 0 WARN.
  `audit_keys_vs_literature.py`: 0 NEW.
- Register, mirror and schema spec counts were refreshed (content rows 1,919 → 1,921). The EPMA review
  workbooks were regenerated as v96.
- **What changed:** two data types (`Step Size / Pixel Size`, `Map Area`), one field name in two tables,
  and two new fields. No tier, `Procedure Value` or `Keyed By` value of an existing row changed.
