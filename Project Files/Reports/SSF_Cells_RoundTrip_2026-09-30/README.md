# Solution SF cells round-trip: can each procedure be regenerated from its literature cells? (2026-09-30)

The same test as `../LASF_Cells_RoundTrip_2026-09-30/`, run on Solution SF-ICP-MS after its keyed-notation
re-read (`Project Files/Scripts/ssf_keyed_reverify_20260930.py`). It builds a procedure record from each of
Solution SF's six literature columns, using only the TAPP and its cells. It then looks up the facts each
paper states in its methods, instrument tables and table notes:
- Desem+2022 §2.4;
- Li+2016 Tables 1–3;
- Lu+2007 Table 1b and §2.7;
- Milne+2010 Tables 1, 2 and 5;
- Misra+2014 Tables 1, 3 and 4;
- Willbold & Jochum 2005 Tables 1 and 3.

The edited TAPP was scored before it was applied.

## Result

| | v88 (before) | v89 (after) |
|---|---|---|
| Facts recovered | 124 of 245 (51%) | **245 of 245 (100%)** |
| as structure (value under the right member) | 22 | 177 |
| in another field | 19 | 0 |
| absent, or under the wrong member | 102 | 0 |

**What the 121 misses at v88 were.**
- **Isotopes (73).** Every column left `Monitored Masses` as `N` or unkeyed. All 28 of Li's nuclides and 37
  of Willbold's 45 were absent. Willbold's other eight, including its Ti, Ru and Re monitors, appeared only in
  other fields.
- **Absent, or filed elsewhere.** Li's calibration solutions, limits and FER-2 precision. Willbold's LR/HR
  assignment, spike list, Dixon test, detection-limit method and BHVO-1 accuracy; its ID/RSF split was under
  the data-reduction fields. Misra's resolution passes, detection limit, consistency standards and long-term
  precision. Lu's Ti calculation and limit. Milne's drift schedule and SAFe D2.
- **Wrong values**, which a recall test counts only as misses: Misra's dwell times and Milne's Fe detection
  limit.

The re-read also removed claims the papers do not make: Li's extra reference materials, Misra's
"inter-lab consensus" accuracy, and Willbold's spiked mono-isotopic elements. The script's docstring lists
them.

## Files

`roundtrip.py` (takes a CSV path), `facts.py` (245 facts), `records_v88/`, `records_v89/`,
`score_output_v88.txt` and `score_output_v89.txt`. The same limits apply as for the LA tests:
- it measures recall, not precision;
- it is not blind;
- only procedure-level fields are scored. Misra's procedural blank, which is analysis-level, was dropped
  from the facts for that reason.
