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
