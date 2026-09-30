# LA-Q cells round-trip: can each procedure be regenerated from its literature cells? (2026-09-30)

LA-Q-ICP-MS and its U-Pb twin were converted to the keyed-value notation (conventions 7.3.4) on
2026-09-30, with every procedure-level cell re-read against its paper. The requirement set for the
conversion was that the literature cells alone must be enough to regenerate each paper's procedure. This
test checks that. It builds a procedure record from each of LA-Q's seven literature columns, using only
the TAPP and its cells, and looks up the facts that each paper states. It is the same test as
`../EPMA_Cells_RoundTrip_2026-09-29/`, adapted.

## Files

| File | What it is |
|---|---|
| `roundtrip.py` | Builds the records (stage 1) and scores the facts (stage 2). Takes a CSV path, so an edited TAPP can be scored before it is applied. |
| `facts.py` | 204 stated facts from the seven papers' LA-ICP-MS methods, instrument tables and table notes. A keyed field's facts are listed per member. |
| `records_v95/`, `records_v96/` | One regenerated procedure record per column, before and after. |
| `score_output_v95.txt`, `score_output_v96.txt` | The two runs. |

## Result

| | v95 (before) | v96 (after) |
|---|---|---|
| Facts recovered | 158 of 204 (77%) | **204 of 204 (100%)** |
| as structure (value under the right member) | 41 | 123 |
| as text | 117 | 81 |
| absent, in another field, or in commentary only | 46 | 0 |

What the 46 misses at v95 were:
- **Isotopes filed as target species.** Nakanishi+2022's 14 monitored masses sat in `Target Species`, and
  `Monitored Masses` was `N`.
- **Values in the wrong field.** Auxiliary gas flows were filed under make-up or coolant gas. A dwell time
  was under `Detector Configuration`, and a secondary standard under `Analysis Sequence`.
- **Stated facts missing.** Nakanishi's torch and coolant flows. Liu+2024's internal standard elements and
  its primary standards. Liu+2025's second laboratory, its make-up gas and its internal standards. Liu+2016's
  per-element detection limits, its LOD method and its procedure references.

The re-read also removed things the papers do not say. The test does not measure those, because it asks
only whether stated facts come back; `laq_keyed_reverify_20260930.py` lists them. For example:
- "fs laser reduces LIEF" for a nanosecond excimer;
- ablation times "inferred from typical protocol";
- inclusion-bearing analyses "excluded entirely";
- another paper's accuracy comparison.

## What this shows, and what it does not

- **Parsing is not the bar.** Before the re-read, 27 of LA-Q's structured cells already parsed, yet 46
  stated facts could not be regenerated. The notation makes a key visible; only reading the paper puts
  the right value under it.
- **It measures recall, not precision**, and it is not blind: the facts were listed by the author of the
  cells, after re-reading the same passages. An independent extraction would be a stronger test.
- **Only procedure-level fields are scored** (C = Basic or Advanced). Session-level statistics, such as
  `Other Statistics`, are outside a procedure record.
- **The U-Pb twin carries columns 1–6 with identical cells**, so this score stands for it too.
- **It is a snapshot.** Rerun with `python3 roundtrip.py path/to/LA-Q-ICP-MS_TAPP_vNN.csv` after a bump.
