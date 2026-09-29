# EPMA cells round-trip: can a procedure be regenerated from its literature cells? (2026-09-29)

The EPMA literature columns were converted to the keyed-value notation (conventions 7.3.4) on
2026-09-29. This test asks what that buys. It builds a procedure record from each of EPMA's 15
literature columns using only the TAPP and its cells. It then checks the record against the
procedure facts that each paper's EPMA methods paragraph states. It is the reverse direction of
`../EPMA_Narrative_RoundTrip_2026-09-17/`, which went from prose to structure.

## Files

| File | What it is |
|---|---|
| `roundtrip.py` | Builds the records (stage 1) and scores the facts (stage 2). Runs from any directory. |
| `facts.py` | The stated facts: 367 in all, with a keyed field's facts listed per member, and each with its source sentence. |
| `records/*.json` | One regenerated procedure record per column: every procedure-level field with its status and parsed value. |
| `score_output.txt` | Output of `roundtrip.py` against `EPMA_TAPP_v84.csv`. |

## Result

**Stage 1 — what the record holds.** EPMA's 15 columns have 1,140 procedure-level cells, i.e. fields
with C = Basic or Advanced:

| Status | Cells | Share |
|---|---|---|
| not stated (`N`) | 466 | 41% |
| free text | 223 | 20% |
| not applicable (`N/A`) | 138 | 12% |
| structured (keyed or definer, parsed) | 136 | 12% |
| not assessed (blank) | 130 | 11% |
| stated only in commentary | 47 | 4% |

**Stage 2 — does it reproduce the paper?** 338 of 367 stated facts (92%) are recovered: 280 as
structure (the value under the right member) and 58 as free text. The 29 not recovered:

- **17 are `Analytical Mode`, never assessed in 14 of 15 columns.** A record cannot say which modes a
  procedure covers, and so which mode-flagged fields apply. That matters most for the three columns
  that do both points and maps: Liu+2016_UT, Broussard+2026 and Zega+2025.
- **6 are Liu+2016_UT's X-ray lines.** The paper names them for the maps ("Ca Ka, Al Ka, Fe Ka, and
  Mg Ka"). The cell is `N`, and the lines survive only as prose in `Mapping Beam Current`.
- **6 are in commentary only**, where the stated value does not fit the field's key:
  - Zega+2025's counting times, 4 facts, per material (held);
  - McCoy+2025_SI's standards, named without their elements;
  - Barnes+2025 NHM's detection limit for "transition metals".

**Per procedure:** 12 of 15 columns recover 89% or more; Neuman+2025 recovers all 25. The three low
ones are Liu+2016_UT (50%: the mode and X-ray-line gaps), Barnes+2025 NHM (67%, 4 of 6) and Zega+2025
(74%: per-material counting times).

## What this shows, and what it does not

- **The keyed notation did its job.** Every per-member fact in a converted keyed field came back under
  the right member: standards per element, X-ray lines, detection limits, per-material beam
  conditions, and McCoy+2025_UA's per-phase standards.
- **It measures recall, not precision.** It asks whether stated facts come back, not whether the
  record holds things the paper does not say. The pilot re-read the keyed and definer cells, but not
  EPMA's 184 unkeyed values, and at least one of those is wrong: McCoy+2025_SI's `WDS Spectrometer
  Configuration` reads "LIFL (Fe Ka, Mn Ka); TAPL (Mg Ka) …", while the paper names crystals, not lines.
- **It is not blind.** The facts were listed by the author of the cells, after re-reading the same
  paragraphs. An independent extraction would be a stronger test.
- **Free text is readable, not typed.** "15 kV" found in `Accelerating Voltage` counts as recovered, but
  a consumer still has to parse it. Session-keyed cells can also hold what a procedure should state as
  one value. For example, Liu+2016_UT's `Mapping Beam Current` holds two map currents.
- **Only the EPMA methods paragraphs were used**, and only procedure-level fields. A procedure
  regenerated from these records is as complete as those paragraphs; 41% `N` is the paper's silence,
  not a defect.
- **It is a snapshot of v84**, and a version bump makes the scores stale.

## What would close the gaps

1. Fill `Analytical Mode` in EPMA's 15 columns (17 facts).
2. Fill Liu+2016_UT's `X-ray Line` from the map sentence (6 facts).
3. Re-read EPMA's unkeyed cells against the papers; the pilot covered only keyed and definer cells.
4. Revisit the commentary-only cases when their keys are decided (Zega's counting times are held).
