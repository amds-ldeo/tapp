# Superseded TAPPs — 2026-09-16

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v72` | `v73` |

1 version(s), 2 file(s) (CSV + xlsx).

## Why

The `Sampling Unit Type` literature pass. `Sampling Unit Name` was completed on 2026-09-15; its two
sibling fields were never assessed for four of the six corpora — 131 blank cells in EPMA, the LA
family, the SEM family and TEM. (Solution and Lab-XCT were done when those TAPPs were built.)

### Pass 1 — `Sampling Unit Type` literature, batch 1: EPMA (14 cells)

`../../Project Files/Scripts/phase3_sampling_unit_type_epma_20260916.py`. EPMA v72 → v73. The one
cell already filled (Neuman 2025) was left alone; the script refuses to overwrite a non-blank cell.

**What the type is, for EPMA: what one reported row corresponds to, not what the beam touched.**
Three shapes recur, and each cell says which it is.

- **Per-phase or per-occurrence means** (Ma 2015, Ma 2017, Pang 2016). The row is the phase or the
  grain and the points are its replicates, so the cell carries the n values.
- **Representative or per-grain analyses** (Frank 2023, Seifert 2026, Barnes 2025 both labs). The row
  is the analysis point inside a named grain.
- **Maps** (Liu 2016 UT, Broussard 2026, Zega 2025's phase mapping). Every pixel is classified and the
  reported quantity is a modal fraction over a section or fragment, so the row is that area.

**Tally:** 6 `Phase > Analysis point`, 5 `Grain > …`, 2 map-area types, 1 whole-section type.

## Verification

**Pass 1.**
- **Cell-level diff:** exactly 14 cells changed, all in the `Sampling Unit Type` literature columns.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- **Validator:** `validate_tapp.py` reports 0 ERROR, 0 WARN.
- **Key audit:** `audit_keys_vs_literature.py` regenerated; only file versions changed.
- **Mockups:** both EPMA mockups retargeted to v73 and rebuilt, 72 procedure-level fields unchanged.
