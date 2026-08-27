# Step 1 (routing only) for the non-ICP-MS TAPP-owned descriptions — 2026-08-27

**Routing:** `Step1_Routing_NONICPMS_2026-08-27.csv` — 556 rows, one per sentence.

**APPLIED 2026-08-27**, after review, by `Project Files/Scripts/apply_step1_nonicpms_20260827.py`.
All 7 non-ICP-MS TAPPs bumped. See "As applied" at the end.

## Scope

| | |
|---|---|
| TAPPs | 7 non-ICP-MS: EPMA, SEM, SEM_Composition, SEM_Imaging, SEM_FIBSEM, TEM, Lab-XCT |
| Cells covered | **339** TAPP-owned Description cells (EPMA 49, SEM 82, SEM_Composition 52, SEM_Imaging 27, SEM_FIBSEM 20, TEM 54, Lab-XCT 55) |
| Distinct texts | 212 (182 distinct field names; SEM variants share wording) |
| Sentences routed | 556 — 212 S1 (M1) and 344 non-S1, every one read individually |

Module-owned fields and the 26 ICP-MS-specific fields were split in earlier passes and are excluded.

## Outcome

| | |
|---|---|
| Sentences staying in Description | 440 |
| Sentences moving to Purpose | 116 |
| Texts that gain a Purpose | 94 of 212 — **118 texts stay wholly in Description** |
| `REWRITE-STRADDLE` flags for Step 2 | 25 |
| `REWRITE-REDUNDANT` flags for Step 2 | 76 |

Rules applied: M1 182, M1+M5 30, M2 116, M3 160, M4 22, M4+M5 3, M5 43.

**Verification.** Every one of the 212 texts reconstructs exactly from its Description and Purpose
halves — same multiset of words, no sentence dropped or duplicated, and no text left with an empty
Description (M1). Machine-checked before the CSV was written: every non-S1 sentence carries a route,
no S1 is routed to Purpose, no row lacks a reason.

**Expectations, stated honestly.** This delivers Purpose separation and nothing else. It was measured
on the ICP-MS slice that splitting does *not* make divergent descriptions converge (mean similarity
0.17 → 0.21, 0 of 26 fields converging). The value is the column itself.

## The segmenter had three bugs, found by reading

The reviewed segmenter carried into this pass from the module and ICP-MS work. Reading its output
on this corpus exposed three defects that its own anomaly checks did not flag:

1. **A possessive apostrophe opened a quote that never closed.** `the procedure's target` put the
   segmenter into "inside quotes" mode for the rest of the cell, suppressing *every* later sentence
   break. Lab-XCT's `Applicable Sample Dimension Range` came out as 2 sentences instead of 5.
2. **A sentence may begin with a digit.** `…in micrometers. 0 indicates a fully focused beam.` and
   `…reducing file size. 1×1 indicates no binning.` were never split. The second matters: it fused a
   rationale clause to a definition that must separate. Fixed only after `.`, never after `;`, where
   a digit is the next item of a list (`; 200-600 nm for XANES`).
3. **A sentence may begin with a quoted term.** `Instrument Variant` S1 was a four-sentence run-on
   because the next sentence opened `'Standard SEM': …`.

**No already-applied work was corrupted.** Every earlier pass was re-segmented under the fixed
segmenter: the 138-row module corpus changes in exactly 2 cells (`Session Identifier`,
`Internal Standard Element`), and in both the suppressed sentences are scope boundaries and filler
instructions that route to Description anyway — the same place the old segmentation left them. The
three corrections that *would* have changed a routing outcome are all inside this pass's own scope.

The segmenter now lives at `Project Files/Scripts/tapp_segment.py` instead of in a session
scratchpad, because the two apply scripts that used it import it from a `/private/tmp` path that no
longer belongs to any live session.

## Findings that are not Step 1's job to fix

These are recorded, not acted on. M6: nothing is deleted in Step 1.

- **Lab-XCT writes the tier into its defining sentence, as house style.** Fourteen S1s open
  `Procedure-level specification of…`, `Analysis-level record of…`, or close
  `…as registered by the procedure`. All 14 duplicate Column C or D and are flagged. Because M1
  forbids emptying Description, Step 2 must strip the clause (W2), never the sentence. This is
  concentrated enough that Step 2 on Lab-XCT is largely one repeated edit.
- **`Target Feature(s)` (Lab-XCT) carries two internal project notes in its published Description**
  — *"Note for Phase 3 literature assessment: evaluate whether procedures in the literature are
  feature-specific… "* and *"This will inform whether the field warrants a controlled list or
  remains free text."* These are working notes, not field documentation. They belong in Comments or
  the backlog and are in neither Description nor Purpose. Routed to Description by default and
  flagged in the Reason column.
- **`Flat Field Correction` (Lab-XCT) Column B ends `"…standard practice in all quantitative lab
  XCT;."`** — a stray `;.`, so the sentence is truncated in the source. Not a routing problem.
- **`EDS Live Time per Point or Pixel` (EPMA and TEM) documents its own rename** — *"Previously
  referred to as 'EDS Acquisition Time'…"*, *"Renamed to align with TEM-EDS usage…"*. Field-naming
  history is Comments material, not Description. Same for `X-ray Power` S4, which justifies the
  field's existence rather than the measurement.
- **`Detection Limit Method` (EPMA) S3 invites analyst entry** — *"When the procedure does not
  specify a method, the analyst should complete this field"* — while its Analysis-Level Tier is
  `Read-Only`. A conditional obligation is real content under W3, so it is not stripped, but the
  tension with D is real.
- **`Dwell Time per Pixel` S3** states the per-spectrometer cardinality. In SEM and
  SEM_Composition that restates `Keyed By: channel`; in SEM_FIBSEM and SEM_Imaging `Keyed By` is
  `(none)`, so there the same clause is the *only* record of cardinality. Stripping it uniformly in
  Step 2 would lose information in two of the four tables.
- **`Beam Current` (EPMA) S2** says the value *"often varies by phase type or analyte"* while
  `Keyed By` is `sample > sampling unit`. Not a duplication — a disagreement about the axis.

## Also outstanding, out of this pass's scope

The nine ICP-MS TAPPs still hold **255 unsplit TAPP-owned Description cells** (83 distinct texts
across 44 field names) beyond the 26 already done. These are the fields the planned ICP-MS-scoped
modules would absorb, so splitting them before that decision would mean doing the work twice.

---

## As applied (2026-08-27)

| TAPP | TAPP-owned cells | gained a Purpose |
|---|---|---|
| EPMA | 49 | 11 |
| SEM | 82 | 34 |
| SEM_Composition | 52 | 21 |
| SEM_Imaging | 27 | 12 |
| SEM_FIBSEM | 20 | 10 |
| TEM | 54 | 22 |
| Lab-XCT | 55 | 36 |
| **total** | **339** | **146** |

The other 193 cells route wholly to Description and were left byte-for-byte untouched — not
rewritten, not restamped. Lab-XCT gains a Purpose on 36 of 55 cells, the highest share in the
library, which is the same house style that produced its 14 tier-duplicating S1 sentences: that
lineage wrote rationale into Column B more freely than the others.

**How it was applied.** Routing was looked up by each cell's OWN segmented text rather than by field
name plus a variant label, so a cell whose wording had drifted since review would fail to match and
be skipped rather than split against a routing decided for different words. Nothing was skipped:
all 339 matched. Three guards had to pass per row — routing covers every sentence, Column B keeps at
least one sentence (M1), and Description + Purpose reproduce the original's exact multiset of words.
None fired.

**Verified after the write, against the superseded originals rather than against the script's own
intentions:** 583 cells compared (the 339 TAPP-owned plus every module-owned cell in the same
tables), 146 split, 437 identical, **0 violations** — no word lost or invented, no Description
emptied, no S1 altered, and no module-owned row touched. `0 ERROR / 0 WARN / 53 INFO`; 16 MATCH,
0 DIFFERS; module register up to date.

**What Step 2 inherits.** The 101 flags stand as recorded — 25 `REWRITE-STRADDLE`, 76
`REWRITE-REDUNDANT` — and the flagged text is now sitting in Column B, which is where W1 and W2
expect to find it. The routing CSV remains the record of what moved and why, so any Step 2 edit is
still traceable to a Step 1 rule.

---

## Step 2 applied (2026-08-27)

Rules W1–W5, acting only on Step 1's flags. Log with every before/after pair (W4) in
`analysis/Step2_Applied_NonICPMS_2026-08-27.csv` — 133 rows.

| Action | Count |
|---|---|
| `REWRITE` — clause stripped (W2 / W5.2) | 72 |
| `SPLIT` — definition kept, rationale moved to Purpose (W1) | 26 |
| `KEEP` — flag raised in Step 1, resolved as no change | 26 |
| `DELETE` — sentence was wholly a restatement (W2) | 8 |
| `DEFERRED` | 1 |

93 cells changed across the 7 TAPPs; 490 cells with a Description were untouched. Verified against
the superseded originals: **0 violations** — no Description emptied, none grew unexpectedly.
`0 ERROR / 0 WARN / 53 INFO`; 16 MATCH; register up to date.

**26 of 101 flags resolved as "no change", and that is the headline result.** A flag is a question,
not a verdict. The ones that survived scrutiny:

- **`defines:` fields** (`WDS Spectrometer Channel`, `EELS Edges`) — Column I is derived *from* those
  descriptions, so stripping them would orphan the key. W5.1.
- **`Dwell Time per Pixel` S2/S3 in EPMA** — revised from the queue's proposed W5.2 strip. The two
  sentences form one WDS-vs-EDS contrast: WDS carries one value per spectrometer, EDS a single
  value. Column I holds **one** key per field and cannot say the cardinality differs by mode.
- **`Background Correction Method` S2/S3** — Column F lists all 11 methods flat and never says which
  belong to WDS and which to EDS. The mapping is content Column F lacks.
- **`EDS Spectral Processing Type`, `Output Bit Depth`, `BSE Detector Type`** — Column F *names*
  these values; the descriptions carry their sequence, their gray-level counts and their mechanism.

**Held back, deliberately:** the 10 flags on the 7 fields a 12-TAPP composition module would absorb
(6 of the 7 carry five distinct descriptions, so extraction will re-merge Column B regardless), and
`Dwell Time per Pixel` S3, which needs a scope decision rather than a wording edit — see the W5.3
correction in the decision record.

### Two things caught while authoring, both worth recording

**A Step 1 flag withdrawal silently failed.** `BSE Detector Type` S4 was un-flagged during Step 1
after the Column F rule was refined, but the edit was written as a `str.replace` against a reason
string that had already changed. Python's `replace` returns the string unchanged when it does not
match and raises nothing, so the withdrawal was reported as done and was not. Step 2 reached the
right end state independently (KEEP), but the routing CSV records a flag that should not exist.
**A no-op `replace` is indistinguishable from a successful one unless the result is asserted.**

**One authored rewrite asserted something the source did not.** A draft of the `HAADF Collection
Angles` split rendered *"Inner angle is most critical"* as *"the more critical of the two"* — turning
a superlative into a comparison between inner and outer angles that the source never makes. Caught
by the word-level diff of every recast, not by reading the sentence back, which had looked fine
twice. The guard that flags any word appearing in the rewrite but not the original is what surfaced
it; it fired 38 times, 37 of them benign grammar, and was worth every false positive.

