# Module_Aggregation: rules in the TAPP, results in the dataset — DRAFT for RD review

2026-10-26. Status: **APPLIED 2026-10-26**, after RD approved all three decisions in section 6
(Module_Aggregation v6, Module_UPb v11, 13 consumers bumped; script
`Project Files/Scripts/aggregation_results_to_dataset_20261026.py`). One refinement during
application: the U-Pb examples and Purpose text come from Module_UPb's overlay rows, so that
module was edited too. The literature re-read gave 36 → N, 6 kept and 3 restated (section 4
estimated "most" → N). The text below is the proposal as approved.

Origin: an EPMA team member's review comment (5.13–5.15 look unnecessary; users have their own
acceptance criteria and complete one TAPP per analytical setup), and RD's reply that fields
capturing actual results belong in the dataset, not the metadata record.

## 1. The principle

The TAPP records the **rules** by which values are produced; the **dataset** carries the values
and results themselves. Where a field hands something to the dataset, its description says what,
in one sentence beginning **"In the dataset:"**.

The line that keeps QC fields in the TAPP: results *on samples* (a phase mean, its MSWD, which
points went into it) are data; results that characterise *the measurement's performance*
(precision and accuracy on secondary reference materials, detection limits) are metadata, as
methods sections treat them.

### Proposed convention text (for `references/conventions.md`)

> **Dataset hand-off sentence.** Where a field governs values that are reported in the dataset
> rather than in the metadata record, its Description ends with one sentence beginning
> "In the dataset:" that states what the dataset reports and at what grain (for example "for each
> combined value", "for each individual result"). The fixed lead-in is what lets a script collect
> these sentences, across TAPPs, into a draft data-reporting guideline. The sentence states a
> reporting expectation; it does not make the dataset value part of the TAPP.

## 2. Field-by-field proposal

Module v5 → v6. Columns A–E and I are module-owned; F and J are overlay defaults that consumers
own after composition (section 3).

### 2.1 Combination Method — description extended, otherwise unchanged

| | Current (v5) | Proposed (v6) |
|---|---|---|
| B | Whether the reported variable is an individual result or combines several, and if combined, how: … Record the model only; the software implementing it belongs in Data Processing Software. | *(unchanged, plus:)* **In the dataset:** report each combined value with its uncertainty and the number of individual results it combines, and identify, for each individual result, the combined value it contributes to. |
| C / D / E / I | Basic / Editable / Text (free) / reported property | unchanged |

### 2.2 Combined Results — RETIRE

Every part of it is a result: which points went into each mean, and how many. Its method content
("what the individual results are combined over: per grain, per phase within a sample") is
already in Combination Method. Its own Purpose says it exists to give the inclusion *outcome*
and the dispersion *values* a row to attach to; with both moved to the dataset it has no job.

### 2.3 Analysis Inclusion and Rejection Criteria — rules only

| | Current (v5) | Proposed (v6) |
|---|---|---|
| B | The rules determining which individual results contribute to a combined result, **together with the outcome of applying them: how many results were obtained, how many were included, and on what grounds any were excluded.** An individual result is … Distinct from filtering the acquired signal …: this field records which finished results enter the combined result, and on what grounds. | The rules determining which individual results contribute to a combined result: the limits a result must meet (for example on analytical total or stoichiometry) and the grounds on which one is rejected (for example overlap onto a neighbouring phase, or an outlier test with its threshold), including any acceptance threshold on the dispersion statistic. An individual result is … *(unchanged)*. Distinct from filtering the acquired signal … *(unchanged)*: this field records the rules by which finished results enter a combined result. **In the dataset:** flag each individual result excluded from a combined value, with the rule that excluded it. |
| C | Basic | Basic |
| D | Basic | **Editable** — a session may tighten a limit, and records the one it applied |
| I | combined result | **(none)** — the pre-v5 key, restored. v5 re-keyed it only because *outcome counts* differ per combined value; the rules do not |
| F (default) | *(blank)* | e.g., 'Totals 98.5–101.5 wt%; points overlapping a neighbouring phase rejected' \| 'All results included; no filter applied' |
| J (default) | Criteria and outcome are combined in one field because neither is interpretable without the other, following the precision/accuracy precedent. | The same measurements give different combined values under different acceptance rules, so the rules are needed to reproduce a combined value from its individual results. |

The current J states the design decision this proposal reverses. The precedent it cites
(precision/accuracy) is the measurement-performance case that section 1 keeps in the TAPP. The
inclusion outcome is a sample result, so the precedent does not carry over.

### 2.4 Goodness-of-Fit or Dispersion Statistic — which statistic, not its value

| | Current (v5) | Proposed (v6) |
|---|---|---|
| B | The statistic reported to show whether scatter among the individual results contributing to a combined result exceeds what analytical uncertainty alone predicts, **together with its value**. The procedure may still state an acceptance threshold, which belongs with the inclusion criteria. | The statistic used to describe the scatter among the individual results contributing to a combined value, or to test whether that scatter exceeds what analytical uncertainty alone predicts: for example one standard deviation of the mean, or the MSWD with its probability of fit. A threshold for accepting it belongs with the inclusion criteria. **In the dataset:** report, for each combined value, the value of the statistic, and any further statistic (for example the standard error of the mean, or a 95% confidence interval) beside it, named. |
| C | N/A ("the value cannot be known before the analysis") | **Basic** — which statistic is used is known before any session. *Basic, not Advanced:* a '±' beside a mean cannot be read without it (one standard deviation and a standard error differ by √n) |
| D | Basic | **Editable** |
| I | combined result x reported property | **reported property** — the pre-v5 key, restored |
| F (default) | *(blank)* | e.g., One standard deviation of the mean \| MSWD with probability of fit |
| J (default) | Answers whether a combined result is defensible as a single population. The value cannot be known before the analysis. | Without the statistic named, the uncertainty given with a combined value cannot be interpreted, nor can whether the combined results form a single population be judged. |

### 2.5 Other Statistics — RETIRE

It is "any statistic … with the statistic named **and its value**": with the value moved to the
dataset only the name is left, and the Dispersion statistic's dataset sentence now covers that ("any further statistic … beside it, named").

### 2.6 Key `combined result` — RETIRE from the Rule 7 vocabulary

After 2.2–2.5 it has no definer and no consumer, so it fails 7.4a–c, exactly as `conversion`
did. Its vocabulary row (conventions.md, the `combined result` row of the key table) becomes a
retirement record, with *what would revive it*: a **rule** (not an outcome) that differs between
combined values of the same reported variable in one procedure.

## 3. Consumer overlays to rewrite (F and J are consumer-owned)

- **J of Inclusion Criteria: all 13 consumers** hold the v5 default verbatim. Replace with the
  new default.
- **J of Dispersion statistic: all 13** hold the v5 default. Replace.
- **F of both fields in the 3 UPb TAPPs** (LA-MC/LA-Q/LA-SF-ICP-MS_UPb) hold outcome/value
  examples:
  - Inclusion: '30 grains analysed, 24 included; excluded 4 discordant beyond −5% to +10% and 2 with Pb\*/Pbc < 20' → 'Discordance beyond −5% to +10% rejected; Pb\*/Pbc < 20 rejected'
  - Dispersion: 'MSWD = 1.13 (n = 24), probability of fit 0.31' | 'MSWD = 4.2; excess scatter…' → 'MSWD with probability of fit; Model-3 regression where MSWD exceeds the stated cutoff'
- **Combination Method J:** 10 at the default, 3 (UPb) differ. Unaffected.

## 4. Literature consequences

- **Inclusion Criteria: 45 non-N cells across 13 TAPPs must be re-read** (38 "Partially", 4
  "Rule:", 3 other). In EPMA every "Partially" attests a *count* only ("n = 6, 6, …"), and none of
  the 14 EPMA papers states a rule. Those cells become N under the new definition. The library
  will then show what the papers show: rules are rarely stated, and counts are in the tables, which
  is the data.
- **Dispersion statistic:** cells that name the statistic ("one standard deviation of the mean")
  stay valid; cells that attest only a value need re-reading. Expect few.
- **Combined Results (≈60 non-N cells) and Other Statistics (≈17)** leave with their rows.
  Superseded TAPP versions keep them.

## 5. Everything else the change touches

1. `precedents.md`: new entry, 2026-10-26, reversing the 2026-09-28 design (Gap 3 of
   `Pending_Gaps_2026-09-24_Reference_Example.md`), with the reason.
2. Module manifest: v6 decision entry; `Combined Results` and `Other Statistics` removed from the
   `inclusion` and `dispersion` blocks.
3. Validator `RETIRED_FIELDS`: add both fields.
4. Recompose all 13 consumers (version bump each; EPMA → v89); `compose_tapp.py --check`, 16 MATCH;
   `build_module_register.py`; `Current TAPPs/` mirror.
5. Review workbook generator: drop `combined result` from SESSION_ONLY / DISPLAY / NOUN / DEFINES;
   drop the two fields' PROSE and examples; rewrite PROSE for 5.13 and the dispersion statistic
   with their "In the dataset:" sentences; regenerate the workbooks and PDF.
6. Worked example (`review_examples.py`) and the v86 methods section's highlight map, where
   their spans point at the retired fields: the 5.13 outcome example ("excluded for totals: ap2,
   ap5 …") becomes an example of a dataset flag, not a TAPP entry.
7. Revise the reply to the EPMA team member: 5.13–5.15 now go their way.
8. Follow-up, separate change: sweep the library for other fields that are really dataset values
   (Counting Statistics Error is a candidate), and a note to the data-template side asking
   whether per-result group membership and exclusion flags are supported.

## 6. Decisions for RD

1. Tiers: Inclusion Criteria D Basic → Editable; Dispersion statistic C N/A → **Basic**, D →
   Editable. (Module tiers are provisional by the manifest's own statement.)
2. Keep Inclusion Criteria at C = Basic although 0 of 14 EPMA papers state a rule? The
   literature reflects current practice. The tier reflects what is needed to reproduce a combined
   value.
3. Drop "which further statistics are reported" entirely (as proposed), or keep it as a
   procedure-level field?
