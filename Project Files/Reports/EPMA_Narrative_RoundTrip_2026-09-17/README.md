# Blind round-trip test: EPMA narrative → TAPP structure (2026-09-17)

Tests how much of a TAPP's structure survives being rewritten as plain prose. A natural-language
rendering of `EPMA_TAPP_v77.csv` was handed to an isolated agent with no access to the TAPP. The agent
rebuilt the structured table from the prose alone, and the result was scored cell by cell against v77.

## Files

| File | What it is |
|---|---|
| `blind_input_narrative.md` | The exact input the agent saw: `EPMA/EPMA_TAPP_v77_Narrative.md` with its "rendering of EPMA TAPP v77" subtitle removed, so the source couldn't be looked up. |
| `reconstruction.csv` | The agent's output: 108 rows, each with section, field name, both tiers, Keyed By, four mode flags, verbatim evidence, confidence, and an ambiguity note. |
| `build_recon.py` | The script the agent wrote to produce the CSV. Only its output path was changed on archiving; re-running it reproduces `reconstruction.csv` byte-for-byte. |
| `score.py` | Aligns the reconstruction to v77 and scores it. The field alignment is hand-written in the list `A`. Runs from any directory. |
| `score_output.txt` | Output of `score.py` as run on 2026-09-17. |

## Protocol

- **Isolation:** the agent was told to read only the input file and to use no skill, filesystem search or web access. It made 2 tool calls: read the file, write the CSV.
- **Given:** the target *vocabulary* only — tier names and meanings, the Keyed By notation and key names, and the four mode columns. No values.
- **Not blind:** the alignment of its 108 rows to the 88 v77 fields was done by the narrative's author. Every row mapped to exactly one field, with no invented or missing fields. For a field split into several rows, the first row is scored.

## Result

Section 88/88 · procedure tier 88/88 · analysis tier 87/88 · Keyed By 87/88 · mode cells 352/352 ·
whole row 86/88. Confidence was well calibrated (high 43/43, medium 41/42, low 2/3 fully correct).

**Field boundaries were not recovered:** 14 fields were split into 34 rows. Where the prose lists what a field contains, the agent read each part as its own item: calibration factor → factor + method + uncertainty; inclusion criteria → rules + three outcome counts.

The two errors:
- `Beam Damage Minimization` was keyed `(none)`: the "for each analysis point" scope sentence was not carried two sentences forward.
- `Analysis Inclusion and Rejection Criteria` got D=Editable: the prose gives the rules and the outcome different session roles, and the TAPP's single D=Basic combines them.

## Limits on what this shows

- The narrative was written from the TAPP, in a deliberately fixed phrasing (must/should, fixed/may adjust, "for each", one mode per paragraph). The score applies to that kind of prose, not to ordinary methods sections.
- The agent was given the vocabulary.
- The alignment was not blind, and scoring the first row of split fields is lenient.
- The agent ran on the same model that wrote the narrative.
- Data type, allowed values, descriptions and provenance were stripped from the narrative, so they were not tested.

It is a snapshot of v77: a version bump makes the scores stale.
