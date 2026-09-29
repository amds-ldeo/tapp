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
| `EPMA_TAPP_v83` | `v84` | standards re-key |
| `LA-MC-ICPMS_TAPP_v87` | `v88` | standards re-key |
| `LA-MC-ICPMS_UPb_TAPP_v84` | `v85` | standards re-key |
| `LA-Q-ICP-MS_TAPP_v92` | `v93` | standards re-key |
| `LA-Q-ICP-MS_UPb_TAPP_v92` | `v93` | standards re-key |
| `LA-SF-ICP-MS_TAPP_v89` | `v90` | standards re-key |
| `LA-SF-ICP-MS_UPb_TAPP_v90` | `v91` | standards re-key |
| `SEM_Composition_TAPP_v79` | `v80` | standards re-key |
| `SEM_TAPP_v80` | `v81` | standards re-key |
| `Solution_MC-ICP-MS_TAPP_v88` | `v89` | standards re-key |
| `Solution_Q-ICP-MS_TAPP_v91` | `v92` | standards re-key |
| `Solution_SF-ICP-MS_TAPP_v86` | `v87` | standards re-key |
| `TEM_TAPP_v64` | `v65` | standards re-key |
| `EPMA_TAPP_v84` | `v85` | round-trip fixes |
| `EPMA_TAPP_v85` | `v86` | remaining fields |
| `SEM_TAPP_v81` | `v82` | SEM never-assessed fields |
| `SEM_Composition_TAPP_v80` | `v81` | SEM never-assessed fields |
| `SEM_Imaging_TAPP_v41` | `v42` | SEM never-assessed fields |
| `SEM_FIBSEM_TAPP_v42` | `v43` | SEM never-assessed fields |
| `SEM_TAPP_v82` | `v83` | phantom Barnes columns removed |
| `SEM_Imaging_TAPP_v42` | `v43` | phantom Barnes columns removed |
| `SEM_FIBSEM_TAPP_v43` | `v44` | phantom Barnes columns removed |

36 version(s), 72 file(s) (CSV + xlsx). EPMA was bumped five times on this date, once per pass.

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

**Third pass — standards re-key and EELS detection limit.** Module_CompositionQC v5 → v6 re-keys
`Primary Calibration Standard Name` to `target material x target species` in all 12 composition TAPPs.
TEM's `EELS Detection Limit` moves to `reported property`. EPMA's 8 stated standards cells became
two-level (`all [ … ]`; McCoy+2025_UA per phase). Applied by
`Project Files/Scripts/rekey_standards_eels_20260929.py`.

**Fourth pass — fixes from the EPMA cells round-trip.** The round-trip
(`Project Files/Reports/EPMA_Cells_RoundTrip_2026-09-29/`) found three gaps, and 37 EPMA literature
cells were changed to close them:
- `Analytical Mode` filled in all 15 columns: 6 with a value, 9 `N`, because their papers name no
  detector;
- Liu+2016_UT's map X-ray lines filled;
- 21 unkeyed cells corrected after a re-read against the papers.

Applied by `Project Files/Scripts/epma_roundtrip_fixes_20260929.py`.

**Fifth pass — EPMA's remaining blank cells.** 205 literature cells were filled from the papers'
methods, table notes, acknowledgements and data-availability statements, among them the three
Aggregation fields, `Target Material of Sampling Unit` and the funding and dataset fields. The
lab-internal fields were sampled first. `Laboratory ID` and `Procedure Start Date` appear in 0 of 12
papers, so they stay blank by decision. `Funding Source for Procedure Development` appears in 3 of 12,
so it was assessed. Applied by `Project Files/Scripts/epma_remaining_fields_20260929.py`.

**Sixth pass — the SEM TAPPs' never-assessed fields.** Gap 1 left the link field, the point beam fields,
the mapping twins, the detection method per element and the Aggregation fields blank in every SEM column;
six other fields had never been assessed either. Each of the 11 source papers was re-read and 840 cells
were filled across the four SEM TAPPs (632 SEM, 164 SEM_Composition, 36 SEM_Imaging, 8 SEM_FIBSEM). The
variants' columns are the same procedures as SEM's, so each procedure was read once. Few values are
stated: Gucsik+2013's focused beam, Pascucci+2026's SEM-EDS map area and its damage measure, and
Zhou+2017's per-sample means (the only SEM combined results). Every averaged composition in the SEM
papers is from EPMA. Two `Monitored Elements` cells were corrected on the way: Pascucci+2026's EDS map
does name its elements, and Barnes+2025's quoted element list was CRPG's JSM-6510 work, not the JSC
SEM-EDS. Applied by `Project Files/Scripts/sem_never_assessed_fields_20260929.py`.

**Seventh pass — three phantom Barnes+2025 columns removed.** BSE Imaging on the JSC Quanta 3D/Helios
and TEM Sample Preparation on two JSC Helios instruments describe procedures the paper does not contain;
its FIB work is in the companion Zega+2025, which has its own columns. On the user's decision they were
removed from SEM (35 → 32 columns), SEM_Imaging (18 → 17) and SEM_FIBSEM (8 → 6). Barnes+2025's JSC SEM-EDS
column stays. Applied by `Project Files/Scripts/sem_remove_phantom_barnes_20260929.py`.

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

**Third pass.** `compose_tapp.py --check`: 0 of 16 drifted after the pass. `validate_tapp.py`: 0 ERROR,
0 WARN. EPMA's two-level cells pass the enforced `keyed-cell` check, including McCoy+2025_UA's phase
members. Two register entries left, since their keys no longer diverge: the standards entry in
`KEYED_BY_TECHNIQUE_DEPENDENT`, and the EELS pair in `KEY_NAME_VARIANT_EXEMPT`.
`audit_keys_vs_literature.py`: 0 NEW; the two standards rulings are marked re-keyed. The mockups were
rebuilt against EPMA v84 and LA-MC v88, and the reviewer workbooks regenerated as v84. Changed: Keyed By,
1 value in 12 TAPPs and 1 in TEM; Column B, 1 (TEM); 8 EPMA literature cells. No field, tier or data type
changed.

**Fourth pass.** `compose_tapp.py --check`: 0 of 16 drifted. `validate_tapp.py`: 0 ERROR, 0 WARN.
`audit_keys_vs_literature.py`: 0 NEW. The mockups and reviewer workbooks were regenerated at v85. The
round-trip was re-scored on v85: 350 of 369 facts recovered (95%), up from 338 (92%) on v84. Changed:
37 EPMA literature cells; no field, tier, data type or key.

**Fifth pass.** `compose_tapp.py --check`: 0 of 16 drifted. `validate_tapp.py`: 0 ERROR, 0 WARN; every
new keyed cell parses against its definer. `audit_keys_vs_literature.py`: 2 new findings, both
adjudicated CONSISTENT (`Combination Method`, `Goodness-of-Fit or Dispersion Statistic`), so 0 NEW.
The mockups and reviewer workbooks were regenerated at v86. The only procedure-level cells left
unassessed in EPMA are the 24 lab-internal ones, blank by decision. Changed: 205 literature cells; no
field, tier, data type or key.

**Sixth pass.** `compose_tapp.py --check`: 16 of 16 match. `validate_tapp.py`: 0 ERROR, 0 WARN.
`audit_keys_vs_literature.py`: 0 NEW. No SEM-dependent report is versioned, so nothing was rebuilt.
The only blank literature cells left in the SEM TAPPs are `Session Identifier`, blank by decision.
Changed: 840 literature cells, 2 of them corrections; no field, tier, data type or key.

**Seventh pass.** `compose_tapp.py --check`: 16 of 16 match. `validate_tapp.py`: 0 ERROR, 0 WARN.
`audit_keys_vs_literature.py`: 0 NEW. `generate_paper_registry.py --check`: MATCH; Barnes+2025 stays
Detailed for SEM, on its CRPG, Hokkaido and JSC SEM work. Changed: 6 literature columns removed; no field,
tier, data type or key.
