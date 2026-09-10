---
name: project-paper-registry-generator-drift
description: DO NOT run generate_paper_registry.py — it has drifted from the live paper_registry.csv and re-running it destroys 34 paper rows and the Solution Q/SF split (found 2026-08-14)
metadata: 
  node_type: memory
  type: project
---

**REPAIRED 2026-08-14 — the generator now round-trips (`--check` → MATCH). 68 papers × 27 columns as of 2026-08-31.**
Its `papers` list was rebuilt *from* the live CSV, so generator and register agree by construction.
It gained `--check` (compare against live) and `--apply` (write); bare invocation is a dry run, and it
refuses to emit blank cells or non-label values. **Run `--check` before every use** — that is the
guard the original lacked. Old version kept at `scratchpad/generate_paper_registry.py.OLD`.

The rest of this note is the record of what was wrong, kept because the failure mode recurs.

---

**`lit_assessment.md` tells you to add papers by editing `Project Files/Scripts/generate_paper_registry.py`
and re-running it. Following that instruction destroyed data.** Verified 2026-08-14:

| | generator | live `paper_registry.csv` |
|---|---|---|
| papers | **21** | **55** |
| technique columns | 17 | 19 |

The generator still declares a single `Solution ICP-MS` column. The live registry has **`Solution
Q-ICP-MS` and `Solution SF-ICP-MS`** separately (since the 2026-08-11 split) plus `Lab X-ray Computed
Tomography (Lab-XCT)`. Re-running it deletes 34 rows and collapses the Q/SF labels that the Solution
literature assessments depend on.

**Fix the generator from the live CSV before ever running it again**, or retire it and state in
`lit_assessment.md` that the CSV is hand-maintained. Same silent-failure class as the `_excluded()`
directory trap (Rule 7.8) and the mirror-exclusion trap (Rule 12.1): a tool that looks like the
maintained route and is not.

**Two schema gaps found at the same time.** No `Thermal Ionization Mass Spectrometry (TIMS)` column,
though TIMS is in `TAPP_Planning_Table.csv` and Budde 2016 and Ibáñez-Mejía & Tissot 2020 both use it
in detail. And the `Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)` column name no longer matches any
"Proposed TAPP Name" — the planning table split it on 2026-08-11. Splitting the column means
re-reading every paper labelled under it.

**Method note when confirming a technique is absent from a paper:** anchor the search. An unanchored
case-insensitive `TEM` matches "sys**tem**" and `SEM` matches "as**sem**blage"; the first search pass
produced 50–80 phantom TEM hits per paper and would have written false Detailed/Brief labels into the
register. Use `\bTEM\b` case-sensitively for acronyms.

See [[project-lit-attestation-method]].
