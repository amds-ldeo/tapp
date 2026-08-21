# Superseded TAPPs — 2026-08-11

## LA-Q_SF-ICP-MS (split into Q and SF)

`LA-Q_SF-ICPMS_TAPP_v6` and `LA-Q_SF-ICPMS_UPb_TAPP_v6` were split on 2026-08-11 into separate
single-instrument TAPPs, aligning the laser-ablation family with the solution family, where
`Solution Q-ICP-MS` and `Solution SF-ICP-MS` have always been separate TAPPs.

| Superseded (v6) | Successors (v7) |
|---|---|
| `LA-Q_SF-ICPMS_TAPP_v6.csv` | `LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v7.csv` · `LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v7.csv` |
| `LA-Q_SF-ICPMS_UPb_TAPP_v6.csv` | `LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v7.csv` · `LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v7.csv` |

Version numbering continues the v6 lineage rather than restarting, so the split reads as a
branch rather than as two new techniques. File naming uses `ICP-MS` (not `ICPMS`) to match the
solution TAPPs.

### What the split did

Of 126 content rows in the base TAPP: 7 Q-only, 3 SF-only, 1 applying to both with different
content per instrument (`Mass Resolution Setting`), 115 shared.

- **Q-only, dropped from SF:** Collision/Reaction Cell (CRC) Configuration, Signal Collection Mode,
  Collision Gas Type, Collision Gas Flow Rate, Cell Exit Discrimination Voltage, Reaction Gas Type,
  Reaction Gas Flow Rate
- **SF-only, dropped from Q:** Mass Resolution per Analyte, E-scan Range, Triple Scanning Mode
- **`Mass Resolution Setting`** — the field that motivated the split. Its Column F previously had to
  carry both answers at once (*"Unit resolution — quadrupole (fixed) | Low resolution — SF …"*).
  Each successor now states one. In the Q TAPP the analysis-level tier moves Editable → **Read-Only**,
  because unit resolution is fixed by instrument design and the analyst cannot adjust it.
- **`ICP-MS Type`** allowed-value list narrowed to the relevant analyser in each successor.
- **`Q-ICP-MS only` / `SF-ICP-MS only` comments removed** — redundant once each file describes one
  instrument. `Analyte-Specific` labels preserved.
- **Literature assessment columns split by instrument**, using the instrument named in each column
  header: 6 Q-instrument papers to the Q TAPPs, 7 SF-instrument papers to the SF TAPPs. The combined
  TAPP had assessed Q-instrument papers against SF-only fields and vice versa.

### Seed papers

`LA-Q_SF-ICP-MS/LA-SF-ICP-MS/` (5 U-Pb / apatite PDFs) moved to `LA-SF-ICP-MS/Seed Papers/`,
following the SF successor.

### Row counts

| File | Content rows | Columns (of which literature) |
|---|---|---|
| `LA-Q-ICP-MS_TAPP_v7` | 123 | 18 (6) |
| `LA-SF-ICP-MS_TAPP_v7` | 119 | 19 (7) |
| `LA-Q-ICP-MS_UPb_TAPP_v7` | 132 | 18 (6) |
| `LA-SF-ICP-MS_UPb_TAPP_v7` | 128 | 19 (7) |
