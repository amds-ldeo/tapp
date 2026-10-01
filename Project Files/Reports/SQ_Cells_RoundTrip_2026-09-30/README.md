# Solution Q cells round-trip: can each procedure be regenerated from its literature cells? (2026-09-30)

The same test as `../SSF_Cells_RoundTrip_2026-09-30/`, run on Solution Q-ICP-MS after its keyed-notation re-read
(`Project Files/Scripts/sq_keyed_reverify_20260930.py`). It builds a procedure record from each of Solution
Q's nine literature columns, using only the TAPP and its cells. It then looks up the facts each paper states
in its methods, instrument tables and table notes:
- Hu & Gao 2008 §3.1–3.4 and Table 2;
- Yu+2005 Tables 1–2;
- Makishima+2011 Table 1;
- Long+2025 Methods;
- Lu+2007 Tables 1a, 2a and 4;
- Gil-Díaz+2020 §2.2–2.4 and Table 1, across three instruments;
- López García+2026 Methods and Table 1.

The edited TAPP was scored before it was applied.

## Result

| | v93 (before) | v94 (after) |
|---|---|---|
| Facts recovered | 152 of 234 (65%) | **234 of 234 (100%)** |
| as structure (value under the right member) | 31 | 152 |
| in another field | 16 | 0 |
| absent, under the wrong member, or not assessed | 66 | 0 |

**What the 82 misses at v93 were.**
- **Per-instrument and per-group structure absent (most of the 32 misses in columns 6–9).** Gil-Díaz's three instruments and López
  García's three measurement groups lost which cell mode, gas, matrix and calibrator went with which
  elements. The iCAP-TQ column had no Se at all.
- **Tables not transcribed.** Yu's Table 2 detection limits, precision and accuracy. Lu's Table 2a limits
  and precision. Makishima's Table 1 limits, which were the sensitivity column instead. Hu's blank table.
- **Stated settings missing.** Hu's peak hopping and sweeps. Yu's drift monitors every 3 samples and cone
  conditioning. Lu's daily P/A factor, constants and blank correction. Makishima's procedure reference.
  López García's spikes and 2σ convention.
- **Wrong values**, which a recall test counts only as misses: Makishima's detection limits, Gil-Díaz's Se
  limit, and López García's digestion reagents (H2O, not H2O2) and cell modes.

The re-read also removed claims the papers do not make, which a recall test cannot catch:
- "STD, no gas" cell modes;
- "on-peak zero" blanks;
- "ID-IS inherently corrects for interferences";
- a Ta spike;
- "KED" and "same dissolved aliquots" for Long;
- a "pure ¹¹⁸Sn solution";
- an m/Δm of ~300 for every quadrupole.

The script's docstring lists them.

## Files

`roundtrip.py` (takes a CSV path), `facts.py` (234 facts), `records_v93/`, `records_v94/`,
`score_output_v93.txt` and `score_output_v94.txt`. The same limits apply as for the earlier tests:
- it measures recall, not precision;
- it is not blind;
- only procedure-level fields are scored.
