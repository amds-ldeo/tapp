---
name: tapp-sentence-segmenter
description: The TAPP sentence segmenter lives at Project Files/Scripts/tapp_segment.py; the two 2026-08-25 apply scripts import a dead scratchpad path and cannot be re-run as written
metadata:
  type: reference
---

`Project Files/Scripts/tapp_segment.py` — the sentence segmenter for the Description/Purpose split.
Splits on `.` / `;` followed by a sentence start, never inside parentheses or quotes.

**It is not re-runnable from the old location.** `apply_step1_purpose_20260825.py` and
`apply_step1_icpms_slice_20260825.py` both `sys.path.insert` a
`/private/tmp/claude-501/.../784752d4-.../scratchpad` path belonging to an ended session. They are
kept as records of what was applied; anything new must import the repo copy.

Three bugs were fixed on 2026-08-27, all found by **reading** its output, none by its own anomaly
sweep (which returned 1 flag, and that one was a false positive):

1. a possessive apostrophe (`the procedure's target`) opened a quote that never closed, suppressing
   every later sentence break in the cell;
2. a sentence may begin with a digit (`0 indicates…`, `1×1 indicates…`) — allowed after `.` only,
   never after `;`, where a digit is the next list item;
3. a sentence may begin with a quoted term (`'Standard SEM': …`).

Re-segmenting all 1750 Description cells confirmed **no already-applied work was corrupted**: the
module corpus changes in 2 cells and both route to Description either way.

The lesson is recorded in `references/precedents.md`: reading finds defects whose signature is
semantic (a well-formed but wrong segment); automation establishes the blast radius once the shape
is known. Read first, then measure. See [[project-tapp-description-purpose-split]].
