# Description / Purpose split — rules and staging

**Decision (2026-08-25).** Column B becomes `Description` (what the field holds + how to record it).
New Column J `Purpose` (why it matters scientifically) is consumer-owned. Structural change applied;
content migration runs in two ordered, separately reviewable steps.

## Why two steps

Step 1 moves whole sentences and changes no text. Step 2 rewrites. Keeping them apart means every
change is traceable to a rule, the intermediate state is a valid library that lints clean, and a bad
Step 2 edit can be reverted without redoing the routing. The cost is one extra set of intermediate
versions; the benefit is that no sentence is silently reworded while being moved.

## Step 1 — MOVE ONLY (no text is altered or deleted)

| Rule | |
|---|---|
| **M1** | Sentence 1 always stays in `Description`. Column B must never be left without a definition. |
| **M2** | A sentence that is wholly scientific rationale → `Purpose`. |
| **M3** | A sentence that is wholly definition or instruction-to-the-filler → `Description`. |
| **M4** | A sentence containing **both** → `Description`, flagged `REWRITE-STRADDLE`. Default to Description because it is the primary column: Step 2 extracts *out* of it, so nothing is lost in the interim. |
| **M5** | A sentence containing a clause that duplicates Columns C, D or `Keyed By` → routed by M1–M4, additionally flagged `REWRITE-REDUNDANT`, naming the column it duplicates. |
| **M6** | **Nothing is deleted in Step 1.** Deletion is always a Step 2 act. |

## Step 2 — REWRITE (acts only on Step 1 flags)

| Rule | |
|---|---|
| **W1** | `REWRITE-STRADDLE`: split the sentence; definition/instruction stays in `Description`, rationale moves to `Purpose`. |
| **W2** | `REWRITE-REDUNDANT`: strip the duplicating clause. If nothing survives, delete the sentence — recording which column already carries it. |
| **W3** | An obligation clause duplicates C/D **only** when it asserts this field's own *unconditional* requirement. Conditional obligations ("Required when X is not 'None'") and external-standard citations ("Required by Schaen et al. 2021") are real content and are never stripped — C and D express unconditional tiers only. |
| **W4** | Every W1/W2 edit records the before text, so it is reversible. |
| **W5** | `REWRITE-REDUNDANT(Keyed By: …)` is decided by what Column I *can* express. Column I states **which axis** a value repeats over and how axes nest (`>`), cross (`x`) or are enumerated (`defines:`). It cannot state order, alignment with another field, conditionality, or which members of an axis apply. Prose asserting only the axis is stripped; prose asserting anything Column I cannot encode is content and is kept. Four dispositions, W5.1–W5.4. |

## Evidence for W3, which is the rule that is easy to get wrong

A keyword sweep for obligation/level language across the 358 module-owned sentences returned 31
hits. Read individually, only about 5 were genuine tier duplication. Four were
`"Required by Schaen et al. (2021)"` — an external reporting standard, not our Column C — and one
was `"Required when Coupled Technique(s) is not 'None'"`, a conditional that C and D cannot express.
**The sweep ran roughly 80% false positives, which is why this pass is read rather than matched.**

## Tier semantics the rules rely on

- `C=Basic` — "Mandatory for procedure registration."
- `D=Basic` — "Mandatory user input at analysis time."

`Sampling Unit` S2 reads *"State the unit type at procedure level and the units actually analysed at
analysis level"*, and conventions.md justifies that field's tiers with the same sentence in
substance. That is the clearest case of a description restating C and D.

## W5 in full — the four dispositions

Added 2026-08-27, before Step 2 began, because "strip the clause that duplicates `Keyed By`" is
not safe as a single instruction. Of the 26 `Keyed By` flags raised by the non-ICP-MS Step 1 pass,
only about 19 are the simple case.

| | Disposition | When |
|---|---|---|
| **W5.1** | **KEEP** | The field's Column I is a `defines:` form. The field *enumerates* the key domain — Column I is derived **from** this description, not duplicated by it. Stripping orphans the definition. |
| **W5.2** | **STRIP** | Column I already names the axis and the prose adds nothing else. Column I becomes the single source of truth. |
| **W5.3** | **NOT A REWRITE — Column I defect** | Column I is `(none)` while the prose carries cardinality. The prose is the *only* record that the value repeats. Fix Column I; leave Column B alone. Never strip. |
| **W5.4** | **NOT A REWRITE — adjudicate** | The prose names an axis that *disagrees* with Column I. Two columns contradict each other; that is a finding, not a wording problem. |

**W5.3 and W5.4 are deliberately not Step 2 work.** They are schema corrections wearing the costume
of a wording change, and filing them as rewrites would mislabel them. Route them out of the Step 2
queue to their own item.

### The ordering clause, which is the part most easily got wrong

**Prose that states the ordering of a compound key is never stripped, even when it looks like pure
repetition.** `conventions.md` §7.3 instructs the author to take the `x` ordering *from the field's
own description*:

> *"Choose the order from the field's own description where it states one — `Counting Statistics
> Error` reads 'for each analyte per analysis', and is reported as one row per analysis with a
> column per analyte, giving `sampling unit x analyte`."*

`Counting Statistics Error` is one of the 26 flags. Its S1 still carries that clause, now as *"for
each reported quantity per analysis"*. Strip it and Column I's ordering — which the convention
states is *itself information*, not an arithmetic detail — loses the evidence that justified it, and
the next reviewer re-deriving the key has nothing to work from. The same applies to every compound
or definer key: **8 of the 26 flags carry `x`, `>` or `defines:`, and all 8 lean KEEP.**

### Why this is not "strip every mention of the key"

The instinct to remove all axis prose and restore it later, uniformly, was considered and rejected.
It assumes the hard part is the writing; the hard part is deciding what the uniform expression
should be, and deleting the prose that disambiguates the cases makes that decision harder, not
easier. It would also destroy information in the W5.3 cases in the interval.

Measured, not assumed — `Dwell Time per Pixel` S3 states the per-spectrometer cardinality. In SEM
and SEM_Composition that repeats `Keyed By: channel`. In SEM_FIBSEM and SEM_Imaging **Column I is
`(none)`**, so there the same sentence is the only record that the value repeats at all. A uniform
strip is lossless in two tables and lossy in two others, from identical text.

### A case that looks like W5 and is not

`Technique per Analyte` S3 reads *"List in the same order as the Analyte field."* That has the shape
of "report A for every B", but Column I says only that the value repeats over analyte; it says
nothing about serialization order matching another column. Real content, routed M3 with no flag.
**"Report A for every B" is redundant only when B is exactly the key and nothing further is
asserted.**

### Scope

W5 governs Step 2, whose mandate is Step 1's flags — currently the 7 non-ICP-MS TAPPs. The modules
and the 9 ICP-MS TAPPs carry their own already-applied Step 1 flags, and 255 ICP-MS cells are not
routed at all. W5 is written to be reusable when those arrive, but it must be applied only where
there is reading behind it: a fresh lexical sweep for "for each X" would reproduce the ~80%
false-positive rate recorded for the W3 sweep. What makes the 26 tractable now is that they are
**enumerated**, each carrying the Column I value it duplicates — not that they are findable.

### The queue, and what happened when W5 was first applied mechanically

`analysis/Step2_W5_Queue_KeyedBy_2026-08-27.csv` carries all 26 flags with a **proposed**
disposition: W5.1 keep 9 · W5.2 strip 13 · W5.3 defect 1 · W5.4 adjudicate 2 · read 1. Proposed, not
decided — the column is named `W5_disposition_PROPOSED` deliberately.

**The first run of that classifier was wrong on three rows, in the direction the rule exists to
prevent.** It bucketed the three `Detection Limit` fields as W5.4 contradictions because their text
contains "analyte" while Column I says `reported property`. Read, they say:

> *"…one per reported concentration variable (one per analyte, **these being the same set**)"*

That names the key correctly and then **reconciles** it against the analyte set — an equivalence
Column I has no way to express, and useful precisely because the library has settled elsewhere that
analyte and reported property are not the same thing in general. Content, not contradiction. The
matcher saw two tokens co-occur; the distinction lives in a subordinate clause.

A second error came from the opposite direction: `Analytical Precision` was initially bucketed
W5.1 and `Analytical Accuracy` W5.4, though both carry the same mismatch — only because a note had
been written on one during Step 1 and not the other. **Provenance of a note is not evidence about
the text.**

Two errors in one small classifier over 26 rows, which is the sixth and seventh instance of a
lexical shortcut losing to reading in this project. W5 is a rule for deciding, not a rule that can
be executed. The queue exists to bound the reading, not to replace it.

### Correction to W5.3, 2026-08-27 — the example that motivated it was wrong

W5.3 was introduced with `Dwell Time per Pixel` as its worked case: the sentence *"For WDS mapping,
the dwell time is per spectrometer per pixel"* restates `Keyed By: channel` in SEM and
SEM_Composition, while SEM_FIBSEM and SEM_Imaging carry the same text with `Keyed By: (none)` — read
as a Column I defect, the prose being the only surviving record of cardinality.

**Checked against the mode flags, and it is not a defect.** SEM_FIBSEM declares only
`TEM Sample Preparation` and `3D Tomography`; SEM_Imaging declares `SE Imaging`, `BSE Imaging`,
`CL Point Analysis`, `CL Mapping` and `EBSD`. **Neither declares any WDS mode.** There is no
spectrometer assignment in either sub-TAPP, so the dwell time really is scalar there and `(none)` is
correct. The WDS sentence is inherited boilerplate describing a mode those tables do not have.

That is a **scope leak**, not a cardinality question — the same class as the 70 out-of-scope
literature columns dropped from the SEM sub-TAPPs on 2026-08-24, where the parent SEM table's
content had been copied into children whose declared modes are narrower. It is reclassified `SCOPE`
in the queue, and **W5.3 currently has no instance in this pass.**

W5.3 is kept as a rule — a `(none)` key beside cardinality prose is still a defect worth catching —
but it is now a rule with no worked example, which is worth saying plainly. The argument against
bulk-removing axis prose does not depend on it: it rests on W5.1, and specifically on
`conventions.md` §7.3 taking a compound key's ordering from the field's own description.

**Method note.** The claim that survived three rounds of review here — that the clause was "the only
record of cardinality" in two tables — was never checked against those tables' mode flags. It was
inferred from Column I alone. Checking Column I against Column B, without also checking what the
TAPP declares it does, produces exactly this error.
