# Survey — Column B descriptions against Column I (`Keyed By`)

**Date:** 2026-08-12 · **Scope:** all 16 TAPPs (1,691 keyed content rows) and all 8 modules
**Trigger:** `Monitored Isotopes` in LA-Q-ICP-MS v11 declares `defines: channel` while its
description states *"Specific isotope(s) monitored **per analyte element**… Analyte-specific field."*
The analyte key is asserted in prose and absent from Column I, and the notation of Rule 7.3 has no
form that could carry it.

**Scripts:** `survey_colB_colI_20260812.py` (sweep) → `build_colI_survey_findings_20260812.py`
(adjudication). Counts in this report are recomputed from the library at build time.

**Deliverables:**

| File | Contents |
|---|---|
| `Survey_ColI_Findings_2026-08-12.csv` | 20 adjudicated findings in 8 classes, 92 affected rows, each with its evidence quote, owner (module vs TAPP) and proposed action; plus 19 field names adjudicated as false positives |
| `Survey_ColB_vs_ColI_AxisA_2026-08-12.csv` | Raw sweep — 321 cardinality-language hits in Column B, classified REDUNDANT / EXTRA / CONFLICT against Column I |
| `Survey_ColB_vs_ColI_AxisB_definers_2026-08-12.csv` | All 70 definer rows, 8 distinct field names — the complete population for the reported defect |

---

## 1. Both stated problems are confirmed

### 1.1 `Monitored Isotopes` is not the only case — 5 of the 8 definers in the library are affected

The library contains **70 definer rows under only 8 distinct field names**. That population is small
enough to adjudicate exhaustively, so this class is now closed rather than sampled.

| Definer | `defines:` | TAPPs | Verdict |
|---|---|---|---|
| `Monitored Isotopes` | channel | 6 | **Second key `analyte`, undeclared** — the reported case |
| `EELS Edges` | channel | 1 (TEM) | **Second key `analyte`, undeclared** |
| `Secondary Reference Materials` | standard | 3 of 12 | **Second key `analyte`, undeclared** (EPMA + 2 SEM variants only) |
| `Collector Configuration` | channel | 3 | **Second key on a pass/magnet-step axis, undeclared** |
| `Sampling Unit` | sampling unit | 16 | **Self-nesting domain the notation cannot express** |
| `Analyte` | analyte | 13 | Key correct; description carries a stale cross-reference (§1.2) |
| `Reported Variables and Units` | reported property | 16 | Clean |
| `Number of Digestion Steps` | preparation step | 3 | Clean, but enumerates by *count* — the only definer of this shape |

Two of the four second-key cases would **not** have been found by searching for the retired
`Analyte-Specific` label, which is the point of running a survey rather than a grep:

- `EELS Edges` says only *"specified by element symbol and edge label (e.g., Fe L2,3; O K)"* and
  *"the EELS-specific counterpart to the Analyte field"*. The analyte key is implied by the naming
  convention of the values, never asserted.
- `Secondary Reference Materials` says *"Include material name, **assessed elements**, number of
  analyses (n), and measured vs. accepted values"* — a per-analyte table inside a
  `standard`-defining field, with no cardinality vocabulary anywhere in the sentence.

`Collector Configuration` is a different shape again: *"For multi-dynamic procedures, list all
configurations and the cycling sequence."* Its second axis is the `acquisition pass` key, retired
2026-08-11 under 7.4b/c for want of a user. This field is a user. Reinstating the key and splitting
the field into a configuration list plus a cycling sequence are both defensible; splitting may be
better here, and is not better for `Monitored Isotopes`, where the analyte-to-mass mapping *is* the
field's content.

`Sampling Unit` — Rule 9's mandatory field — says *"Where units nest (e.g. confined tracks within
grains), state both levels."* Rule 7.3 provides `A > B` for containment between two *different*
keys, and nothing for a definer enumerating a domain nested within itself. Fission track is the
live case.

### 1.2 Descriptions have never been swept — quantified three ways

**(a) The retired `Analyte-Specific` label survives in 46 Column B rows.** Rule 7.6 cleaned
Column G and left Column B untouched. Broken down:

| Sub-class | Rows | Disposition |
|---|---|---|
| Bare cardinality assertion (`"Analyte-specific field."` appended) | 19 | 7 duplicate the declared key verbatim → delete. 12 disagree with it → adjudicate, then delete or extend Column I |
| Stale cross-reference | 5 | See below |
| Legitimate semantic or conditional prose | 11 | Keep (consider rewording off the retired term) |
| Other / drafting guidance | 11 | Mostly optional cleanup |

The stale cross-reference is the sharpest instance. In 5 TAPPs — EPMA, SEM, SEM_Composition,
Solution_Q, Solution_SF — the `Analyte` field reads:

> *"Fields below flagged as Analyte-Specific in the Comments column apply individually to each
> element in this list."*

The Comments column of those 5 TAPPs is empty on **every** row. The instruction cannot be followed;
it points at a mechanism Rule 7 dismantled.

**(b) 89 of 252 shared field names carry substantively divergent descriptions — and none of them
are module-owned.**

| | Count | Share |
|---|---|---|
| Field names appearing in more than one TAPP | 252 | — |
| …with divergent Column I | 5 | **2.0%** |
| …with divergent Column B | 94 | 37.3% |
| …divergent beyond trivial rewording (<0.90 similarity) | **89** | **35.3%** |
| …of those 89 that are module-owned | **0** | 0% |

The asymmetry is the finding. Column I is 98% uniform and *checked* by 7.8.7, with its five
exceptions individually justified in the technique-dependent register. Column B is 65% uniform and
*unchecked*. Rule 7.8.7 justifies its own check by appeal to *"the same argument Rule 6.4 makes
about descriptions"* — but that argument is enforced only where a module owns the row.
`compose_tapp.py --check` guarantees uniformity for module-owned fields, and the zero in the last
row of that table is the machinery working. Everywhere else nothing looks.

Worst cases (6–8 distinct descriptions each): `Acquisition Software`, `Target Material`,
`Data Reduction Software`, `Analytical Mode`, `Analyte`, `Mass Resolution Setting`.

**(c) The `Detection Limit` family disagrees with its own key in all 12 TAPPs that carry it.**

| Variant | Column I | Description says |
|---|---|---|
| EPMA, SEM ×2, Solution ×3 | `reported property` | *"detection limits **for each analyte**"*, *"the resulting value **per analyte**"* |
| LA ×6 | `sampling unit x reported property` | *"for each **measured isotope**… per **isotope or element group**"* (names `channel`) |

Rule 7.3 uses this very field as its worked example of the defines/keyed-by distinction — *"`Analyte`
and `Detection Limit` both wore `Analyte-Specific`, but one *is* the list and the other is indexed
*by* the list"* — so the mismatch sits in the framework's own illustration. A plausible resolution:
for concentration-reporting procedures the `analyte` and `reported property` domains are isomorphic
(one concentration variable per element), which would make both readings correct and the prose
merely imprecise. The framework has never stated that, and it recurs across the library, so it is
worth settling as a precedent rather than per field. **Needs adjudication, not a text edit.**

---

## 2. What the sweep could not do, and why hand adjudication was needed

The regex battery returned 321 hits. 19 field names were adjudicated as **false positives** and
recorded in the findings CSV so a future sweep does not re-raise them. Nearly all belong to one
class: **`per X` in a field name or description denoting a rate, unit, count or schedule rather than
a cardinality key.**

- `Ablation Duration per Spot`, `EDS Live Time per Point or Pixel`,
  `Total Integration Time per Output Data Point` — `per X` is the *unit of measure*.
- `Number of Replicates`, `Number of Projections`, `Mass Cycles per Replicate` — scalar counts.
- `Background Count Time` — *"before each ablation event"*, *"once per raster line"* is a
  **schedule**, not a cardinality.
- `Mass Resolution Setting` — correctly delegates the per-analyte case to a separate
  `Mass Resolution per Analyte` field. Not a gap.

Any future automated check on this axis will have a high false-positive rate for this reason.

---

## 3. Three notation gaps, not one

The reported case is one of three distinct shapes Rule 7.3 cannot currently express.

| Gap | Shape needed | Affected |
|---|---|---|
| **G1 — definer with a key** | field enumerates domain D *and* repeats over key K | 4 definers, 13 rows |
| **G2 — self-nesting domain** | definer enumerates D nested within D | `Sampling Unit`, 16 rows |
| **G3 — conditional key** | scalar or coarse key that becomes finer under a stated condition | `Integration Time per Cycle`, `Dwell Time per Mass`, 5 rows |

G3 is worth noting because it is invisible from Column I alone. `Integration Time per Cycle`
declares `(none)` and says *"Analyte-specific **when** different isotope channels use different
integration schemes."* The declaration takes the narrower reading; the wider one survives only in
prose. The choice is between declaring the finest key unconditionally (over-declaring for simple
procedures) and adding a conditional marker. **G3 is a policy decision, not a notation gap, if the
answer is "always declare the finest key."**

### On the separator

`defines: A. B` was the form proposed when the defect was reported. Recommend against `.`, and for
a form that keeps the two roles distinguishable and the right-hand side a full key expression:

```
defines: <domain> per <key-expression>
```

`defines: channel per analyte` · `defines: standard per analyte`

Reasons:

1. **Role visibility.** In `defines: channel. analyte` neither token is marked; a reader must know
   the convention to tell the defined domain from the key. `per` states the relation.
2. **Composability.** The right-hand side stays a Rule 7.3 key expression, so
   `defines: standard per analyte x reported property` remains expressible without further grammar.
   `defines: standard. analyte x reported property` does not parse unambiguously.
3. **It matches the prose.** The descriptions already say it: *"isotope(s) monitored **per** analyte
   element."* The notation extracts the words already there.
4. **Parsing.** Split on `\s+per\s+`; no key in the vocabulary contains `" per "`. A `.` collides
   with ordinary sentence punctuation elsewhere in the row.

Either way the change is not silent: `validate_tapp.py` matches `^defines:\s*(.+)$` and would read
the whole tail as one domain name, reporting an unknown key. So the grammar, the validator's
`check_keyed_by`, and Rule 7.9's Legends Table 4 must land in the same pass.

**Also worth deciding: whether extension is needed at all for G1.** The alternative is to split
each affected field, which needs no grammar change — and the framework already prefers splitting in
an analogous case (Common Mistake #1, the Oxide Production precedent). The recommendation is to
extend rather than split for `Monitored Isotopes`, `EELS Edges` and `Secondary Reference
Materials`, because in those three the mapping between the two domains *is* the field's content and
splitting would scatter it. `Collector Configuration` is the one case where splitting looks better.

---

## 4. Remediation path — module ownership decides where the fix goes

Column B and Column I are both module-owned under Rules 6.4 and 7.5. Three findings sit on
module-owned rows and must be fixed in the module and recomposed, never in the TAPP (Rule 6.6):

| Field | Module | Consumers |
|---|---|---|
| `Calibration Factor and Determination Method` | ReportingCore (also UPb, ArAr) | **16** |
| `Collector Configuration`, `Integration Time per Cycle` | MCICPMS | 3 |
| `Number of Digestion Steps` | SolutionIntroduction | 3 |

`Calibration Factor and Determination Method` is the highest-leverage row in the survey: declared
`(none)` in 14 TAPPs, while its own description distinguishes it from *"Per-Analyte Calibration
Strategy, which states which approach applies to which analyte: this field records the resulting
factor itself."* If the strategy is per analyte, the resulting factor is too. Because
ReportingCore has 16 consumers, one module edit settles it library-wide — and a hand edit in the
TAPPs would be silently reverted by the next recomposition, exactly the failure 7.10 documents.

Rule 7.4a imposes **no new burden**: every TAPP hosting a G1 field already carries an `Analyte`
field declaring `defines: analyte`, verified across all 24 affected rows. No new mandatory field
is required anywhere.

---

## 5. Incidental finding

Rule 7.10 states *"Comments now carries content on zero rows across all 16 TAPPs."* Actual count:
**27 non-empty rows**, all in the three composed U-Pb TAPPs, all module provenance stamps
(`Source: U-Pb module`, `Source: Geochronology module`). Harmless, and arguably the "future one-off
annotation" the column was retained for — but the sentence in the rule is false as written, and
7.8.8's mode-name warning runs against that column.

---

## 6. Suggested sequence

1. **Decide the three notation questions** (G1 separator and whether to extend or split; G2 nesting;
   G3 conditional-key policy). Everything else depends on these.
2. **Adjudicate the four open key questions**, in descending leverage:
   `Calibration Factor and Determination Method` (16 consumers, module) → `Detection Limit` /
   `Detection Limit Method` (12 TAPPs, precedent-worthy) → `Secondary Reference Materials` (12
   TAPPs, not in the register, so one key must serve all) → `delta or epsilon Value Reference
   Standard` (1 row).
3. **Sweep Column B** for the 46 retired-label rows and the 5 stale cross-references — mechanical
   once step 1 and 2 are settled. Modules first, then recompose, then TAPP-owned rows (7.10).
4. **Consider a description-uniformity check** for the 89 divergent shared field names, as the
   Column B counterpart to 7.8.7. Whether uniformity should be *required* for TAPP-owned fields is
   a design question — some divergence is legitimately technique-specific — but it is currently
   neither required nor visible.
5. `validate_tapp.py` + `tapp_to_xlsx.py` (Legends Table 4) + version bumps + regenerate xlsx.
