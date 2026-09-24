# Pending: six structural gaps exposed by the EPMA reference example (2026-09-24)

**Status: OPEN — documented, not acted on.** No TAPP, module or rule has been changed. Recorded so that the analysis survives until work resumes.

**Where the gaps came from.** Writing `Project Files/Reports/EPMA_Reference_Procedure_Example_v77.md` required filling all 88 fields of EPMA TAPP v77. That exposed six places where complete documentation needs structure the TAPP does not declare. Appendix B of the example states them briefly. This note records:

- the fixes proposed on 2026-09-24,
- the evidence behind each fix,
- what each fix would touch,
- the recommended order.

## Two kinds of level dependence

Gaps 1 and 5 look alike, since in both a field's cardinality seems to differ between the procedure record and the session record. They are different problems.

- **Projection (gap 5).** This is one key read at two levels. `sample` and `sampling unit` are enumerated by definers that are C=N/A (`Sample Name`, `Sampling Unit Name`), because "the procedure is sample-neutral" (Rule 13). At procedure level those domains are empty by definition, so a field keyed `sample` holds a single value there. No new declaration is needed.
- **Substitution (gap 1).** Here the procedure needs a domain of its own that the session realises through a different one. The keys genuinely differ, and neither can be derived from the other without a linking field.

**The projection rule is currently unwritten.** When reading at procedure level, drop from the key every domain whose definer is C=N/A. Seven EPMA fields already depend on this implicitly:

- the five beam fields, keyed `sample > sampling unit`, all C=Basic or C=Advanced;
- `Pre-Analysis Imaging and Screening`, keyed `sample`, C=Advanced;
- `Counting Statistics Error`.

The rule appears nowhere in `conventions.md`. The review workbook generator (`Project Files/Reports/make_review_workbook.py`, `phrase()`) invented it. It should be written into Rule 7, so that a schema consumer applies it the same way.

## The gaps

### Gap 5 — preparation can differ by sample

**The problem.** `Sample Preparation Method` is keyed `(none)` in all 16 TAPPs. The Core module owns Column I for it. Rule 13 already says each sample "may carry its own preparation history" and that "`sample` keys identity and preparation". The module was never brought into line with the rule.

**Fix.** Re-key the field to `sample`, and keep the tiers at C=Basic, D=Editable. The tiers then read: the procedure registers the preparation, and each sample inherits it and may deviate. Under the projection rule, the procedure level is unchanged.

**Evidence.** Rule 13 is the authority. The literature evidence is thin: 1 of 128 literature cells across the library states sample-specific preparation (Seifert+2026: "one mount ion-polished before carbon coating").

**Cost.**

- Edit the Core module.
- Bump the module's JSON version.
- Recompose all 16 TAPPs.
- Pass `compose_tapp.py --check` and the validator.

**Open question.** Should the same test — can this differ between samples in one session? — be applied to the other `(none)` fields in Group 2? `Sampling Unit Selection Criteria` is the obvious candidate.

### Gap 1 — beam conditions vary by phase at procedure level

**The problem.** The five beam fields are keyed `sample > sampling unit`, a domain that does not exist until a session runs. Their procedure-level value therefore projects to one value, or "one or more values", per procedure. Published procedures give these values per phase group.

**Fix.**

1. **A new domain, `phase group`**, defined by a procedure-level field ("Phase Groups": the groups of phases the procedure analyses under distinct conditions). A procedure that does not vary conditions declares one group.
2. **Beam Mode, Beam Current, Beam Diameter, Beam Raster Dimensions and Beam Damage Minimization** take `phase group` as their procedure-level key. The session key stays `sample > sampling unit`. This needs an explicit override on top of the projection rule, for example `sample > sampling unit | procedure: phase group`. These are the only fields that need one.
3. **A session field giving each sampling unit's phase group**, keyed `sample > sampling unit`. Without it, a consumer cannot tell which procedure value a unit inherited. The reference example's Table 10 needed a "Phase" column that no TAPP field holds.

**Not Target Material.** Target Material is the wrong grain for this domain. Liu+2016 analyses maskelynite (silicate glass) with phosphate and sulfide at 10 nA, and olivine, pyroxene and oxides at 20 nA. That splits Target Material's silicate class. The grouping is the procedure's own choice.

**Evidence.** This is the strongest of the six: per-phase values appear in 7 of 15 EPMA procedures for Beam Mode, 6 of 15 for current and diameter, and 4 of 15 for damage minimisation. It completes the 2026-09-08 acquisition-pass precedent (conventions Rule 7.2), which settled the session half: beam conditions vary by mineral, and `sample > sampling unit` carries that.

**Scope.** EPMA, SEM and TEM, not Core.

**Held.** Counting times per phase (`phase group x monitored property`) are attested only by Zega+2025 (1 of 15). Revisit when a second procedure attests them.

### Gap 3 — aggregate statistics belong to a phase mean

**The problem.** The inclusion outcome and the dispersion statistic describe one mean per phase per sample. `Goodness-of-Fit or Dispersion Statistic` is keyed by `reported property` alone. `Analysis Inclusion and Rejection Criteria` is keyed `(none)`.

**Fix.**

1. **A session-level domain, `aggregate`.** Each entry is one reported mean together with its contributing sampling units. In EPMA an aggregate is a phase mean per sample; in geochronology it is roughly one weighted-mean date per sample.
2. **Re-key the two fields:**
   - Dispersion statistic: `aggregate x reported property`.
   - Inclusion outcome: `aggregate`.

**Reopens a decision.** `Analysis Inclusion and Rejection Criteria` deliberately combines the criterion and the outcome, and its Purpose cites the precision/accuracy precedent. Under an aggregate key the two halves need different keys:

- criterion: `(none)` at procedure level;
- outcome: `aggregate` at session level.

One field cannot carry both, which is a stronger reason to split than existed when the two were merged. The blind round-trip test (`Project Files/Reports/EPMA_Narrative_RoundTrip_2026-09-17/`) split them without being asked.

**Cost.** The Aggregation module owns both fields, so the change is library-wide. Check the geochronology TAPPs before acting.

### Gap 4 — WDS or EDS chosen element by element within a mode

**The problem.** In a combined WDS+EDS point analysis, the WDS-only per-element fields do not apply to the EDS-measured elements:

- Diffracting Crystal,
- WDS Spectrometer Channel,
- Proportional Counter / Detector,
- WDS PHA Setting,
- the counting times.

Mode flags work per mode, not per element.

**Fix.**

1. **Re-key `EPMA Technique per Target Species` to `monitored property`.** A condition must sit at the grain of the fields it gates, and these fields are keyed by monitored element.
2. **Add field-level conditional applicability**, for example an "Applies When" column holding `EPMA Technique = WDS`, evaluated per row of the shared key.

**The mechanism has wide use.** 47 fields across the library already state a condition in Column B prose, including:

| Field | TAPPs where the condition is stated |
|---|---|
| Coupling Description ("required when Coupled Technique(s) is not None") | 16 |
| Calibration Factor and Determination Method | 14 |
| Detection Limit | 12 |
| Beam Raster Dimensions ("when Beam Mode = Rastered") | 3 |

**Cost.** This is the largest change of the six: a new column, which the module manifests (`owned_columns`, `overlay_columns`) must account for.

### Gap 2 — per-element values can differ between modes

**The problem.** In the example, the same element uses:

- two-point off-peak background for points and MAN for maps;
- a different spectrometer for maps than for points.

**Status: hold.** None of the 15 EPMA procedures attests this. Neuman+2025 maps only, with MAN, and Zega+2025 runs points only, with off-peak backgrounds. The example invented the case. It is realistic, but it is invented.

**If attested.** Follow the existing `Peak Counting Time` (point) / `Dwell Time per Pixel` (mapping) pattern: mode-flagged twin fields for `X-ray Background Correction Method` and `WDS Spectrometer Channel`. A `mode` key is not an option, because Rule 7.2 forbids it.

**Falsifier.** One procedure reporting both points and maps with a different background method or spectrometer assignment for the same element.

### Gap 6 — target species with no monitored element

**The problem.** O and C are determined by stoichiometry and have no entry under `Monitored Elements`. The TAPP allows this, but never states it.

**Action.** Low priority. A sentence in the `Monitored Elements` description would do: "a target species determined by stoichiometry has no monitored element". It would protect a consumer that expects at least one per target species.

## Recommended order

| Order | Gap | Why here |
|---|---|---|
| 1 | Gap 5, plus the projection rule | Already decided by Rule 13. No new syntax. The rule is the default that gap 1's override departs from. |
| 2 | Gap 1 | Strongest evidence. Needs the override notation. |
| 3 | Gap 3 | Needs a check against the geochronology TAPPs first. |
| 4 | Gap 4 | Largest design change. |
| — | Gap 2 | Held until attested. |
| — | Gap 6 | A one-sentence description edit, whenever convenient. |

Every change follows the usual gates:

- run `check_field_ownership.py` before editing;
- edit the module and recompose, never a TAPP directly;
- `compose_tapp.py --check`;
- `validate_tapp.py` at 0 ERROR / 0 WARN;
- bump the version and sync `Current TAPPs/`.
