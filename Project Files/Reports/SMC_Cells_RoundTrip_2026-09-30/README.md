# Solution MC cells round-trip: can each procedure be regenerated from its literature cells? (2026-09-30)

The same test as `../SQ_Cells_RoundTrip_2026-09-30/`, run on Solution MC-ICP-MS after its keyed-notation re-read
(`Project Files/Scripts/smc_keyed_reverify_20260930.py`). This was the last TAPP in the keyed-notation backlog.
The test builds a procedure record from each of Solution MC's fourteen literature columns (twelve papers),
using only the TAPP and its cells. It then looks up the facts each paper states in its MC-ICP-MS methods, cup
tables and table notes. The edited TAPP was scored before it was applied.

## Result

| | v90 (before) | v91 (after) |
|---|---|---|
| Facts recovered | 160 of 252 (63%) | **252 of 252 (100%)** |
| as structure (value under the right member) | 4 | 149 |
| in another field | 20 | 0 |
| absent, commentary only, or not assessed | 72 | 0 |

**What the 92 misses at v90 were.**
- **The per-isotope and per-setup structure (33 of the misses).** None of the columns had working mass
  bindings. Introduction, plasma, cycles and integration settings that differ between set-ups had no members
  to key them. The set-ups are Hopp's MR/HR, Hu's two configurations, Nowell's two Nu sequences, Pringle's
  spray chamber and APEX, van Kooten's Fe/Cr/Mg and Barnes's K/Cu/Zn and two Ti configurations.
- **Stated facts recorded as unstated.**
  - Nie's digestion steps (ii) and (iii).
  - Nowell's Nu Plasma cup table.
  - Schönbächler's per-session SRM 3169 precision.
  - Barnes's ETH digestion, which was recorded as "see the WUSTL column".
- **Detail in commentary (19).** Values written as `Yes — detail` keep the detail out of the value. The pass
  rewrites them as `Yes, detail`.
- **Wrong values**, which a recall test counts only as misses:
  - Ibañez-Mejia & Tissot's 48 h for the Zr-only dissolution, which is actually 60 h;
  - Nowell's Nu Plasma nebuliser, which is a Micromist, not a PFA-50;
  - Nowell's W monitors;
  - van Kooten's digestion acids.

Facts in analysis-level fields (reference standard, sensitivity, procedural blank) were dropped from
`facts.py`, because only procedure-level fields are scored.

## Files

`roundtrip.py` (takes a CSV path), `facts.py` (252 facts), `records_v90/`, `records_v91/`,
`score_output_v90.txt` and `score_output_v91.txt`. The same limits apply as for the earlier tests:
- it measures recall, not precision;
- it is not blind.
