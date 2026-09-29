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
| `facts.py` | The stated facts: 369 in all, with a keyed field's facts listed per member, and each with its source sentence. |
| `records/*.json`, `records_v85/*.json` | One regenerated procedure record per column, for v84 and v85: every procedure-level field with its status and parsed value. |
| `score_output.txt`, `score_output_v85.txt` | Output of `roundtrip.py` (v84) and `roundtrip.py v85`. |

## Result

**Stage 1 — what the record holds (v84).** EPMA's 15 columns have 1,140 procedure-level cells, i.e. fields
with C = Basic or Advanced:

| Status | Cells | Share |
|---|---|---|
| not stated (`N`) | 466 | 41% |
| free text | 223 | 20% |
| not applicable (`N/A`) | 138 | 12% |
| structured (keyed or definer, parsed) | 136 | 12% |
| not assessed (blank) | 130 | 11% |
| stated only in commentary | 47 | 4% |

**Stage 2 — does it reproduce the paper? (v84)** 338 of 369 stated facts (92%) are recovered: 280 as
structure (the value under the right member) and 58 as free text. The 31 not recovered:

- **19 are `Analytical Mode`, never assessed in 14 of 15 columns.** A record cannot say which modes a
  procedure covers, and so which mode-flagged fields apply.
- **6 are Liu+2016_UT's X-ray lines.** The paper names them for the maps; the cell is `N`, and the
  lines survive only as prose in `Mapping Beam Current`.
- **6 are in commentary only**, where the stated value does not fit the field's key:
  - Zega+2025's counting times, 4 facts, per material (held);
  - McCoy+2025_SI's standards, named without their elements;
  - Barnes+2025 NHM's detection limit for "transition metals".

## After the fixes (v85, the same day)

`Project Files/Scripts/epma_roundtrip_fixes_20260929.py` changed 37 cells:
- It filled `Analytical Mode` (15 cells).
- It filled Liu+2016_UT's map X-ray lines (1 cell).
- It re-read EPMA's unkeyed cells against the papers, which the pilot had not done, and corrected
  21 of them, listed below.

**Result: 350 of 369 facts (95%) recovered, 286 as structure.** No stated fact is now missing, not
assessed, or in the wrong field. Six procedures recover every fact. The 19 left are all commentary-only:

- **14 are procedures whose paper states the geometry but not the detector.** Nine of the 15 papers
  say "quantitative point analyses" or "X-ray maps" without naming WDS or EDS, and `Analytical Mode`
  is a closed list that pairs a detector with a geometry (`WDS Point Analysis`, …). So the cell is
  `N`, and the geometry sits in commentary. This is a limit of the field, not of the extraction.
  gap 4 of `Pending_Gaps_2026-09-24_Reference_Example.md` records the same two axes as its "larger
  alternative": split EPMA's modes into geometry × detector.
- **4 are Zega+2025's per-material counting times** (held with gap 1).
- **1 is McCoy+2025_SI's standards, named without their elements.**
- **1 is Barnes+2025 NHM's "transition metals" detection limit.**

**What the unkeyed re-read found (precision, which stage 2 does not measure):**
- **Stated as fact but not in the paper:** Hu+2020's "WDS"; Broussard+2026's "EDS not used";
  Barnes+2025's "possibly per-pixel"; the Barnes NHM analytes "implied from context"; McCoy+2025_SI's
  X-ray lines in `WDS Spectrometer Configuration`; Seifert+2026's halogen correction on oxygen.
- **Another laboratory's work in the cell:** McCoy+2025_SI's preparation and screening came from the
  JSC SEM work; McCoy+2025_UA's screening likewise. Liu+2016_Cal carried an LA-ICP-MS clause.
- **Misfiled:** a matrix correction (CITZAF, Bence-Albee) recorded as software.
- **Stale:** Frank+2023's note still named the SIMS standard as the EPMA secondary RM.
- **Over-precise:** Zega+2025's "each side" backgrounds.
- **Names:** "EPMA-WDS" in three procedure names whose papers never say WDS.

**v86, after EPMA's remaining fields were filled** (`score_output_v86.txt`). The facts score is unchanged
at 350 of 369, because those fields come from tables and acknowledgements, which the fact list does not
cover. Stage 1 changes: only 24 procedure-level cells are left unassessed, all of them `Laboratory ID`
and `Procedure Start Date`, blank by decision.

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
- **It is a snapshot of v84 and v85**, and a later version bump makes the scores stale. Rerun with
  `python3 roundtrip.py vNN` to score a later version.

## What is left

1. **Decide whether EPMA's modes should split into geometry × detector** (14 facts). Until then, a
   paper that does not name its detector cannot give `Analytical Mode` a value.
2. **The commentary-only cases wait on their keys:** Zega's counting times are held.
3. **Carry the same conversion and re-read to the other 15 TAPPs.** This test applies to EPMA only.
