---
name: project-tapp-description-purpose-split
description: Description/Purpose split status — modules + 26 ICP-MS fields applied; non-ICP-MS Step 1 routed but NOT applied; 255 ICP-MS cells still untouched
metadata:
  type: project
---

Column B is `Description` (what the field holds + how to record it); Column J is `Purpose` (why it
matters scientifically, consumer-owned). Migration runs Step 1 (move whole sentences, no rewording)
then Step 2 (rewrite, acting only on Step 1 flags). Rules M1–M6 / W1–W4 live in
`Claude Skills for TAPP/analysis/Decision_Record_2026-08-25_Description_Purpose_Split.md`.

State as of 2026-08-27:

- **Step 1 applied everywhere except the ICP-MS leftovers:** all 13 modules (350 sentences), the
  26 ICP-MS-specific TAPP-owned fields (218), and — **applied 2026-08-27 after review** — the 7
  non-ICP-MS TAPPs: 339 cells, of which **146 gained a Purpose** and 193 routed wholly to
  Description and were left untouched. Routing in `analysis/Step1_Routing_NONICPMS_2026-08-27.csv`,
  findings and per-TAPP numbers in `analysis/Report_Step1_NonICPMS_2026-08-27.md`.
- **Step 2 DONE for the ICP-MS TAPP-owned cells too (2026-08-27):** 14 flags — 8 rewrites, 3
  deletions, 3 keeps. `Dwell Time per Mass` S2 was DELETED as the first application of
  conventions.md 7.3.2: conditional-key prose ("may differ between masses where per-mass dwell times
  are programmed") is redundant once Column I declares the finest key unconditionally.
- **Step 2 DONE for the non-ICP-MS TAPPs (2026-08-27)** under rules W1–W5: 72 rewrites, 26 splits,
  8 deletions, **26 flags resolved as no change**, 11 held back. Before/after log in
  `analysis/Step2_Applied_NonICPMS_2026-08-27.csv`. Still outstanding: the module and ICP-MS Step 2
  backlogs (`analysis/Step2_Backlog_Modules_2026-08-25.csv`).
- **W5 governs `Keyed By` flags** (added 2026-08-27): Column I states which axis a value repeats
  over; it cannot state order, alignment with another field, conditionality, or which members apply.
  W5.1 keep (`defines:` forms, compound-key ordering — `conventions.md` 7.3 takes the `x` ordering
  FROM the description) · W5.2 strip · W5.3 Column I defect · W5.4 adjudicate. **W5.3/W5.4 are NOT
  Step 2 work** — they are schema corrections.
- **A quarter of the flags were resolved as no change.** A flag is a question, not a verdict. Do not
  execute a Step 2 queue mechanically.
- **Step 1 APPLIED for the ICP-MS TAPP-owned cells too (2026-08-27).** The backlog was 255 cells /
  44 fields; the four module passes of 2026-08-27 (Module_ICPMS to 39, CompositionQC, CollisionCell,
  LaserAblation to 29) absorbed most of it, leaving **105 cells / 32 texts / 22 fields**, all now
  routed and applied — 37 cells gained a Purpose. Routing in
  `analysis/Step1_Routing_ICPMS_TAPPOWNED_2026-08-27.csv`; 3 STRADDLE + 11 REDUNDANT flags await
  Step 2. **Deferring the split behind the modules was the right call** — it avoided splitting ~150
  cells that the modules then rewrote.

**Set expectations honestly:** splitting delivers the Purpose column and nothing else. Measured on
the ICP-MS slice, it does *not* make divergent descriptions converge (similarity 0.17 → 0.21, 0 of
26 fields converging).

See [[tapp-sentence-segmenter]] for the tool, and [[project-tapp-module-architecture]] for Rule 6.

**MODULE BACKLOG CLOSED 2026-08-27.** The 49 module rows added after the 2026-08-25 module routing
were routed and split; 7 gained a Purpose. **Step 1 is now applied to every row in the library.**
It only worked because overlay-default propagation was fixed the same day — before that, Purpose
written into a module reached no consumer.

**Find a backlog by diffing against the record of what was covered, not by re-detecting it.** A
rationale-word heuristic returned 7 rows here; reading returned a different 7, with ~43% false
positives and ~43% false negatives. The structural question — which module rows are absent from the
2026-08-25 routing CSV? — is exact and needs no judgement.

**STEP 2 COMPLETE LIBRARY-WIDE 2026-08-27.** The 7 module flags were applied — once in each module,
composed out to consumers. Both steps of the Description/Purpose split are now done everywhere.

**Never address a cell's sentences by ORDINAL across a pipeline stage that removes sentences.** The
module Step 2 script keyed edits on the Step 1 routing CSV's sentence numbers; Step 1 had already
moved P-routed sentences out of Column B, so the numbers no longer indexed it. It stopped only
because the index was out of range — one sentence longer and it would have silently rewritten the
wrong sentence, passing every guard. Key on sentence TEXT.

