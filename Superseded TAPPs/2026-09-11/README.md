# Superseded TAPPs — 2026-09-11

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `Solution_MC-ICP-MS_TAPP_v76` | `v77` |

1 version(s), 2 file(s) (CSV + xlsx).

## Why

Six literature cells corrected against the source PDFs by
`../../Project Files/Scripts/patch_faraday_barnes_solutionmc_20260911.py`. The errors surfaced
while checking amds-ldeo/tapp#6, which meant reading every Solution MC paper for how it describes
its detectors.

- **`Faraday Cup Array Configuration`, four cells.**
  - Craddock 2008 and Nowell 2008 (NIGL Nu Plasma) read `N`, but both papers state the array:
    nine Faraday cups, and a 7-Faraday "U–Pb" collector block.
  - Nie 2019 read "Three collectors used". That is how many collectors the procedure used, which
    `Collector Configuration` already records. The paper states the array: nine Faraday collectors.
  - Nowell 2008 (Durham Neptune) gains its page reference and the SEM ion counter the same paper
    uses for abundance sensitivity. The field asks whether an ion counter is present.
- **Barnes 2025, ETH Zurich, two cells.** `Monitored Masses` quoted a sentence that does not exist
  in the paper. It joined the ETH Ti procedure's opening to the LLNL procedure described
  immediately after it, bringing in ⁴⁵Sc, which only LLNL measured. The cell now gives ETH's two
  cup configurations, and `Collector Configuration` lists both.

The cause of the Barnes error is recorded for reuse: `pdftotext -layout` interleaves the two
columns of a journal page, so a quote lifted from it can join two sentences. Quote from
reading-order text only.

Four further Barnes-ETH cells disagree with the ETH passage, and a fifth cites a value not found
in it. All five were reported rather than changed, because the correction was scoped to the cells
above: `Integration Time per Cycle`, `Reported Variables and Units`, `Isotope Ratio Reported`,
`Mass Bias Correction Strategy` and `Analytical Accuracy and Assessment Method`.

## Verification

- A cell-level diff of v76 against v77 shows **exactly 6 cells changed**, all in literature
  columns. Row count (141) and header are unchanged.
- No field, tier, data type, description or `Keyed By` value changed.
- The literature columns are not module-owned, so composition cannot revert these edits:
  `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- `validate_tapp.py`: 0 ERROR / 0 WARN / 39 INFO, identical to the baseline before the patch.
- `audit_keys_vs_literature.py` regenerated. Its 7 changed lines differ only in the file name
  (v76 → v77); no finding appeared, disappeared or changed.
- `build_schema_spec_counts.py`: current.
