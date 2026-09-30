# LA-SF cells round-trip: can each procedure be regenerated from its literature cells? (2026-09-30)

The same test as `../LAQ_Cells_RoundTrip_2026-09-30/`, for LA-SF-ICP-MS after its keyed-notation re-read
(`Project Files/Scripts/lasf_keyed_reverify_20260930.py`). It builds a procedure record from each of LA-SF's
seven literature columns, using only the TAPP and its cells. It then looks up the facts each paper states in
its LA-ICP-MS methods, its instrument tables and appendices (Chernonozhkin+2021 Table B1 and Appendix C;
Navarro+2024 Tables 2, 3 and 5) and its table notes. The edited TAPP was scored before it was applied.

## Result

| | v92 (before) | v93 (after) |
|---|---|---|
| Facts recovered | 122 of 315 (39%) | **315 of 315 (100%)** |
| as structure (value under the right member) | 28 | 242 |
| in another field | 144 | 0 |
| absent, or under the wrong member | 48 | 0 |

**What the 193 misses at v92 were.**
- **Isotopes in the wrong field (144).** All seven columns filed their measured nuclides under
  `Target Species`, with `Monitored Masses` left `N`.
- **Absent.** Zhang+2022's per-element standards. Chernonozhkin's per-run acquisition passes, its 3σ spike
  filter and its veinlet mask. Navarro's make-up gas line and its mapping sequence.
- **Wrong values**, which a recall test counts only as misses: Chernonozhkin's pulse duration, and its
  run 2 recorded as a spot when it is a line scan; Navarro's LODs.

The re-read also removed claims the papers do not make: cross-paper borrowing (Zhang's Ru interference cells
held Navarro's statement), EPMA details in an LA column (Mittlefehldt), a "cosmic spherule" analysis
sequence, and fabricated schedules and funders. The script's docstring lists them.

## Files

`roundtrip.py` (takes a CSV path), `facts.py` (315 facts), `records_v92/`, `records_v93/`,
`score_output_v92.txt`, `score_output_v93.txt`. The U-Pb twin carries the same seven columns with identical
cells, so this score stands for it too. The same limits apply as for the LA-Q test: it measures recall, not
precision; it is not blind; only procedure-level fields are scored.
