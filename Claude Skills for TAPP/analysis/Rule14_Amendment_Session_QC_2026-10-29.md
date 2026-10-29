# Rule 14.1 amendment: session-level statistics in the session record, per-measurement statistics in the dataset — proposal, for RD review

2026-10-29. Status: **APPLIED 2026-10-29.** RD accepted all six decisions as recommended. Applied by
`Project Files/Scripts/session_qc_two_level_20261029.py`: Module_ICPMS v19, Module_CompositionQC v8,
Module_Blank v5, Module_UPb v13, EPMA v92 and 12 other TAPPs; conventions 14.1 amended, 14.5 and 14.6
added. One change from the draft text: the overlap sentence is written as one sentence (a semicolon),
so that 14.2's "one sentence beginning `In the dataset:`" holds. Fourth draft. Arose from issue #21. Revisits one
sentence of Rule 14.1 and leaves the Rule 14 sweep of 2026-10-27 standing.

**Earlier drafts, none applied, all superseded:**
1. Every session statistic to the dataset.
2. Every statistical field Read-Only in the session record.
3. Only statistics tied to a row move to the dataset: four fields change to Read-Only.

Draft 3 solved the immediate problem but left the session record inconsistent: some statistic fields
would record the procedure's expected performance, others the session's achieved performance, and
nothing in the record would say which. RD (2026-10-29) chose consistency instead, accepting some
duplication rather than losing information.

## The principle

**What the dataset captures is measurements**, whether on a sample or on a reference material: one row
per measurement, with its values, its own statistics and its metadata.

**The session record captures the session**, including the statistics that describe the session as a
whole. These are recorded whether or not the dataset also carries them, for two reasons:

- **Datasets often omit the reference-material analyses.** Their statistics are then reported only in
  the methods section. RD's experience, and the literature cells, show both habits: "2SD of the
  analyses in each session — Table 7a" next to "within 10% of the GeoReM reference values for most
  trace elements" in the text. If the session record held only expectations, a session whose dataset
  omits its reference materials would have no QC record at all.
- **Some session statistics attach to no measurement at all:** blank levels, a run's method
  detection limit, long-term precision. The dataset is not their home (draft 3), so the session record
  is their only one.

So each statistic field means one thing at each level:

| Level | Holds |
|---|---|
| **Procedure** (Column C) | the method, and the **expected** value |
| **Session** (Column D) | the value **achieved** in this session, by that method |
| **Dataset** | the measurements: samples and, where included, reference materials, each with its own per-measurement statistics |

This is the library's existing convention for level-neutral fields (SKILL.md, common mistake 4: "use
the description to clarify that the procedure registers a target or typical value"). It is also
largely the library's current state. Most of these fields are already C = Basic or Advanced and
D = Basic.

## Guard 1: per-measurement statistics stay in the dataset only

The principle covers **session-level** statistics: one value per session, per reference material or per
reported property. It does **not** bring back the per-measurement values the 2026-10-27 sweep moved
out. A value with one entry per measurement would put rows into a session-grain record (Rule 13).

| Stays dataset-only (per measurement or combined value) | TAPP holds |
|---|---|
| Counting Statistics Error, each analysis | how it is computed, and the sigma level |
| Internal (Within-Measurement) Analytical Precision, each measurement | the statistic, and the cycles it is computed over |
| Error Correlation Between Reported Quantities, ρ for each analysis | which pairs, and how ρ is obtained |
| Discordance, each analysis | the formula |
| Goodness-of-Fit or Dispersion Statistic, each combined value | which statistic |
| Detection Limit, **per analysis** where the procedure computes one | the typical or session limit (below) |

**The 2026-10-27 sweep stands unchanged.**

## Guard 2: the overlap rule

Where the dataset includes the reference-material analyses, the session record's statistics are
computed from those rows. **The rows are the primary record. The session statistic summarises them and
must agree with them.** A disagreement is an error in one of the two, not two readings.

For these fields the `In the dataset:` sentence (14.2) therefore names the **measurements**, not the
statistic:

> *In the dataset: report the analyses of each secondary reference material, where they are included.
> The session value summarises them and must agree with them.*

The overlap is stated in the field itself, so a reader, a schema and a future validator can all see
it.

## Proposed text of 14.1

Replace *"Precision and accuracy on secondary reference materials, detection limits and blanks describe
the measurement and stay in the TAPP, as methods sections treat them."* with:

> **The dataset records measurements** (on samples and, where included, on reference materials), each
> with its own values and per-measurement statistics. **The TAPP records the procedure and the
> session.** For a statistic that describes a session as a whole (precision and accuracy on reference
> materials, detection limits, blank levels, long-term precision), the procedure records the method
> and the expected value, and the session record the value achieved. The session value is recorded
> even where the dataset also carries the analyses it is computed from. Then the analyses are the
> primary record and the session value must agree with them (14.5). A statistic with one value per
> measurement or per combined value belongs to the dataset alone, and the TAPP records only how it is
> computed.

**New 14.5, the overlap rule:** Guard 2 above, as a rule.

**New 14.6, the two-level lead-ins (decision 3).** A field whose value means something different at
the two levels states each one in Column B, in sentences beginning exactly `For the procedure:` and
`For the session:`. The lead-ins are fixed for the reason 14.2 gives: a script, the review-workbook
generator and a schema generator can all find them. This is what makes "one field, two values" legible
without a column split (see "Relation to #9" below).

## Proposals

No field is renamed and no key changes. **One tier changes** (Procedural Blank Level, C).
`Last Update` → the apply date.

| # | Field | TAPPs | Owner | C / D | Change |
|---|---|---|---|---|---|
| 1 | Within-Session Analytical Precision and Assessment Method | 9 ICP-MS | Module_ICPMS v18 | Basic / Basic, kept | two-level sentences; overlap sentence |
| 2 | Analytical Accuracy and Assessment Method | 9 ICP-MS | Module_ICPMS v18 | Basic / Basic, kept | same |
| 3 | Between-Session (Long-Term) Analytical Precision and Assessment Method | 9 ICP-MS | Module_ICPMS v18 | Advanced / Basic, kept | two-level sentences; no dataset sentence |
| 4 | Analytical Precision | EPMA, SEM, SEM_Composition | TAPP-owned | Advanced / Basic, kept | two-level sentences (keeps the 2026-10-29 #21 wording); overlap sentence |
| 5 | Analytical Accuracy | same 3 | TAPP-owned | Advanced / Basic, kept | same |
| 6 | Detection Limit | 12 | Module_CompositionQC v7 | Advanced / Basic, kept | "state whether … procedure-typical … or session-specific" becomes the two-level sentences; dataset sentence kept |
| 7 | EDS Detection Limit, EELS Detection Limit | TEM | TAPP-owned | Advanced / Basic, kept | two-level sentences |
| 8 | Procedural Blank Level | 12 | Module_Blank v4 | **N/A → Advanced** / Basic | two-level sentences; Column J (overlay default) reworded; see decision 4 |

### Draft Column B text

Only the new or changed sentences are shown in full; *[…]* keeps the existing text.

**1. Within-Session Analytical Precision and Assessment Method**
> Precision of repeated measurements of a reference material within a single analytical session, and
> the method used to assess it. The assessment method specifies the reference material or standard
> measured, the number of replicates n, and the statistic reported (1s RSD, 2s RSD, 2SD, 2SE, 95% CI).
> **For the procedure:** the assessment method and the expected within-session precision. **For the
> session:** the precision achieved in this session, assessed by that method. Distinct from the
> internal precision of a single measurement, which derives from counting statistics over the cycles
> of that measurement rather than from repeated analyses. In the dataset: report the analyses of each
> secondary reference material, where they are included. The session value summarises them and must
> agree with them.

**2. Analytical Accuracy and Assessment Method**
> Offset between measured and accepted values for secondary reference materials, and the method used to
> assess it. Specify the reference material and the source of its accepted values, the number of
> analyses, and the quantities assessed. Express the offset in the form appropriate to what the
> procedure reports: percent relative bias for concentrations, or deviation in delta or ratio units
> for isotopic quantities. **For the procedure:** the assessment method, the accepted-value source and
> the expected offset. **For the session:** the offset found in this session, with any systematic bias
> and its likely cause. In the dataset: *[the overlap sentence, as in 1]*.

**3. Between-Session (Long-Term) Analytical Precision and Assessment Method**
> *[existing first sentence]*. Specify the reference material, the number of measurements and
> sessions, the time span covered, and the statistic reported. **For the procedure:** the assessment
> method and the long-term precision on record when the procedure is registered. **For the session:**
> the long-term precision as it stands at this session, including this session's results where they
> contribute.

No dataset sentence: no single dataset holds the analyses it is computed from. Where a procedure assigns
it to each result, the combined uncertainty is dataset content under `Uncertainty Propagation Method`.

**4. Analytical Precision** (EPMA, SEM, SEM_Composition)
> Precision of repeated measurements on the same or equivalent reference material, expressed as 1-sigma
> relative standard deviation (%). State whether the repeats were made within one session
> (repeatability) or across sessions (intermediate precision, in ISO 5725 terms), the reference
> material name and the number of analyses (n). **For the procedure:** the expected precision. **For
> the session:** the precision achieved in this session. In the dataset: *[the overlap sentence]*.

**5. Analytical Accuracy** (same 3)
> Offset between measured and accepted reference values for secondary standards, expressed as percent
> relative bias, with the reference material and the source of its reference value. **For the
> procedure:** the expected offset. **For the session:** the offset found in this session. In the
> dataset: *[the overlap sentence]*.

**6. Detection Limit**
> Detection limit, one per reported concentration variable (one per target species, these being the
> same set), with its units. **For the procedure:** the typical detection limits. **For the session:**
> the limits achieved in this session, where they are determined for the session as a whole (for
> example, from the blanks of the run). The calculation method is recorded separately in Detection
> Limit Method. Record 'N/A' where the procedure reports no concentrations. In the dataset: report the
> detection limit of each analysis, where the procedure computes one.

**7. EDS / EELS Detection Limit** (TEM): *[existing text]*, plus **For the procedure:** the estimated
limits under this procedure's conditions. **For the session:** the limits achieved in this session,
or 'Not determined'.

**8. Procedural Blank Level**
> The level of the analytical blank and, where the reported quantity is a ratio, its composition, since
> a blank subtracted from a ratio biases the result unless its own composition is known. **For the
> procedure:** the typical or maximum blank expected. **For the session:** the blank measured in this
> session. Companion to the blank correction method.

Column J's default currently reads *"Follows the criterion-versus-measurement split the library
applies…"*. No blank criterion field exists: its companion, `Blank / Background Correction Method`, is a
method. With a procedure tier, the field no longer needs that justification. Proposed: *"A blank that
is large relative to the sample, or of unknown composition, biases every result it is subtracted
from."*

### What a data user gets

1. **The session's precision, accuracy, limits and blank**: in the session record, always. They are
   also checkable against the dataset's reference-material rows where those are included.
2. **Agreement with the procedure**: the procedure's expected value against the session's achieved
   value, both in the TAPP's records. A procedure's acceptance threshold, where it has one, is a rule,
   and stays in `Analysis Inclusion and Rejection Criteria`.

## Relation to #9 / #13: kept as a separate decision

The two are compatible, but neither depends on the other.

- **Under the current single Column D,** `Basic` already means "a new value entered at the session,
  required", which is what these fields need. So this proposal works as is.
- **Under the proposed split** (provenance, and obligation as Required/Optional), these fields would
  read: procedure Basic/Advanced; session **fresh**, Required or Optional. The split makes "not inherited
  from the procedure" explicit instead of implied by the vocabulary. This family is a clean worked
  example for #9.
- **14.6's lead-ins do part of the split's work in text:** they say what each level holds. They do not
  replace a structural flag for schema generation. That case belongs in #9.

Bundling the two would hold this fix (about 8 field families) behind a change to all 16 tables and
every module. Recommended: decide #9 on its own, and cite this family there.

## Decisions for RD

1. **Adopt the principle, the new 14.1 text, and Guard 1** (per-measurement statistics dataset-only;
   the sweep stands)?
2. **Adopt 14.5, the overlap rule**, and its `In the dataset:` sentence for fields 1, 2, 4 and 5?
3. **Adopt 14.6, the fixed lead-ins `For the procedure:` / `For the session:`?** Recommended: yes,
   since it mirrors 14.2 and makes the two levels scriptable. Without it, the same content is written
   as ordinary prose.
4. **Procedural Blank Level, C N/A → Advanced**, with the Column J rewording? This is the one tier change.
   Also: should the overlap sentence extend to blank analyses ("report the blank analyses, where they
   are included")? Recommended: **no**. Blanks are measurements on neither a sample nor a reference
   material, so they fall outside the dataset principle.
5. **Between-Session at the session level** means "the long-term figure as it stands at this session".
   Agreed?
6. **Should the session record also summarise per-measurement statistics** (for example "typical
   internal precision this session")? Recommended: **no**. No field asks for it, and adding one would
   reopen Guard 1.

## Scope if all are applied

- **Modules:** Module_ICPMS (3 fields, 9 consumers), Module_CompositionQC (Detection Limit, 12),
  Module_Blank (Procedural Blank Level, 12).
- **TAPP-owned:** Analytical Precision and Analytical Accuracy (EPMA, SEM, SEM_Composition); EDS and EELS
  Detection Limit (TEM).
- **TAPPs bumped:** 13 (the 12 composition TAPPs plus TEM).
- **Docs:** conventions.md 14.1, new 14.5 and 14.6, 14.3's applied list; precedents.md; the schema
  README's tier table, for the blank's new C value; `make_review_workbook.py`'s plain-language text for
  EPMA items 5.12, 6.6, 6.8 and 6.9.
- **Literature cells:** all positive cells were read for draft 3 (about 125). They hold methods,
  typical values, or pointers to session tables, all of which the two-level fields accept. None needs
  changing.
- **EPMA review round (v89):** items 5.12 (blank, C tier), 6.6, 6.8 and 6.9 (text). The bump's
  Superseded README must map them.
- **14.4's candidate validator check** gets a clean exemption: a field carrying the 14.6 lead-ins asks
  for a session value by design.

## Out of scope, noted

1. **LOQ Method** is Advanced / Basic. It is a method field, and Detection Limit Method is Basic /
   Read-Only. A Rule 4 consistency question.
2. **Tuning outcomes** (Oxide Production, Doubly-Charged Species Production, Peak Flatness, Instrument
   Sensitivity, EDS Dead Time) keep their existing patterns. Mostly that is a criterion field at
   procedure level and a measured field in the session. Doubly-Charged Species Production holds both
   in one field. Moving them onto the two-level pattern would be a separate change, and it is not
   needed.
3. **Naming across families.** EPMA/SEM's `Analytical Precision` and ICP-MS's `Within-Session…` hold the
   same quantity under different names (Rule 1/2).
