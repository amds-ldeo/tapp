# TAPP Development Workflow

Detailed guidance for each phase. Read the phase you are currently in; you do not need to read ahead.

---

## Before Starting a New TAPP

**Always read `Project Files/Registers & Planning/TAPP_Planning_Table.csv` before beginning Phase 0 for any technique.** The Notes column records deferred decisions, open questions, and scope constraints from prior planning sessions — including decisions about adjacent techniques, mode-bundling choices, and items explicitly flagged for review at TAPP development time. Do not skip this step: some rows have DEFERRED flags that directly constrain Phase 0 decisions.

---

## Before Assessing or Describing a TAPP's State

**Always read the actual TAPP CSV before making any claim about its current state** — including tier assignments, field counts, column structure, version, or what work remains. Do not infer the state from the workflow's description of what "should" exist at a given phase. The TAPP may have been developed non-linearly, with some steps done out of order or ahead of schedule.

Specifically: before stating whether D-tiers are assigned, whether mode flags are set, whether literature columns are present, or what phase the TAPP is in — read the file and report what is actually there.

---

## Before Consulting the Dev Log for Rationale

**Search `Project Files/Design Notes/TAPP_Development_Log.md` for the specific topic rather than reading it end-to-end.** The log's Part I (Cross-TAPP Conventions) is kept current; every dated entry from Part II onward preserves the terminology in use when it was written, which may be superseded (see the banner at the top of that file). Pulling a large, undifferentiated span of the log into context before drafting new TAPP content risks carrying old terminology into new work. `references/conventions.md` is always the authoritative source for current vocabulary and structural rules.

---

## Choosing a Route: Greenfield or Composition

There are two ways into the five-phase workflow. Decide which before Phase 0 — the choice changes what Phases 1–3 have to cover, and picking greenfield when composition applies means rewriting content that already exists somewhere in the library.

| | **Greenfield** | **Composition** |
|---|---|---|
| **Use when** | no existing TAPP covers a substantial part of the technique | two or more existing TAPPs, plus modules, already cover most of it |
| **Phase 1** | AI drafts the whole TAPP from seed papers | extract any missing modules, compose, draft only the **residue** |
| **Phase 2** | review every field | review the residue in full; spot-check composed fields |
| **Phase 3** | literature assessment across the whole TAPP | literature assessment focused on the residue |
| **Phase 4** | revise | revise, and **push any generalisable revision back into the module** |

The phases are the same; composition changes how much each has to do.

### The Phase 0 coverage audit (composition route only)

Before deciding, quantify the overlap. For the candidate technique, identify the existing TAPPs that share its instrument components and compute:

- fields **shared** by those TAPPs — generic content, much of it already module-held
- fields unique to each — the components the new technique combines
- the **residue**: what the new technique needs that no existing TAPP has

Worked example (LA-MC-ICP-MS, 2026-08-08):

| | Fields |
|---|---|
| LA-Q/SF-ICP-MS | 126 |
| Solution MC-ICP-MS | 104 |
| shared by both | 63 |
| LA-Q/SF only — of which 18 are the laser front end | 63 |
| Solution MC only — of which 13 are the MC analyser | 41 |

≈ 90% of LA-MC-ICP-MS already exists, distributed across two TAPPs. The residue — measuring isotope ratios on a *transient* rather than steady-state signal — is small but is the scientifically hard part, and gets the full Phase 2/3 treatment.

**The audit's real output is a module extraction list.** Content that exists only inside TAPPs cannot be composed; composing it would mean copying, which is what Rule 6 exists to prevent. See Rule 6.10 for when a block qualifies for extraction.

### What the composition route does not shortcut

- **The residue still needs the full workflow.** It is new content and has no precedent to lean on.
- **Composed fields still need a spot-check in Phase 2.** A field correct for its parent technique may be wrong for the new one — tier assignments especially.
- **Phase 0 scoping is unchanged.** Modes, scope and split-vs-combine decisions must still be settled first, and composition cannot rescue a wrong mode decision.

---

## Phase 0 — Technique Scoping

**Purpose:** Establish the scope, sub-modes, and structural decisions that shape every subsequent phase. Skipping or rushing this phase is the single most expensive mistake in TAPP development — it leads to retroactive revision of dozens of fields later.

**Who leads:** Human (with AI supporting research and framing).

**Inputs:** A technique name and a general intent to develop a TAPP.

**Outputs:**
- Technique scope document (1–2 paragraphs): what the technique IS, what it is NOT, and how it relates to adjacent techniques that get separate TAPPs
- Sub-mode decision: either (a) list of modes with mode flag column assignments and labels, or (b) decision to create separate TAPPs per mode
- Key vocabulary decision (Rule 7): which `Keyed By` anchors apply to this technique, which are **absent**, and any technique-specific keys with their definitions. Record absences explicitly — `analyte` does not apply to Lab-XCT, Raman or fission track, and `channel` does not apply to fission track. An absent anchor is a finding, not an omission
- Phase 1 inputs: seed papers and/or existing procedure templates (see below)
- Reference TAPP: which existing TAPP to use as the structural template (default: LA-ICP-MS)

**Key decisions to make in Phase 0:**

Mode set and key vocabulary are both settled here, for the same reason: each is structural, each propagates into every row, and each is expensive to correct retroactively.

### Split-vs-combine for sub-modes

Sub-modes warrant **separate mode flag columns within one TAPP** when they share the same fundamental instrument platform and data product type, differing primarily in how the measurement is spatially, temporally, or spectrally structured. The metadata required to describe the procedure is mostly shared, with a handful of mode-specific fields.

Sub-modes warrant **separate TAPPs** when the physical measurement principle or the fundamental data product type differs, such that a researcher familiar with one mode would not immediately understand a procedure written for the other.

Examples across technique families:

| Scenario | Decision | Reason |
|---|---|---|
| LA-ICP-MS: spot / transect / mapping | Mode flags in one TAPP | Same instrument, same data reduction framework; differ only in ablation path and a handful of spatial parameters |
| EPMA: WDS / EDS | Mode flags in one TAPP | Same instrument platform; differ in spectrometer type and resolution |
| LA-ICP-MS vs. solution ICP-MS | Separate TAPPs | Different sample introduction mechanism, matrix effects, and calibration strategies |
| Raman spectroscopy: point / map / depth profile | Mode flags in one TAPP | Same instrument and spectral data product; differ in spatial acquisition strategy |
| Raman vs. FTIR | Separate TAPPs | Different physical principles, different spectral regions, fundamentally different sample-beam interaction |
| SEM imaging: secondary electron / backscattered / EDS mapping | Mode flags in one TAPP | Same instrument platform; differ in signal type collected |
| SEM vs. TEM | Separate TAPPs | Fundamentally different beam energy, sample preparation, and spatial resolution regime |
| Noble gas MS: step-heating / total fusion | Mode flags in one TAPP | Same instrument; differ in sample degassing strategy |

When in doubt, ask: would a researcher familiar with one variant immediately understand a procedure written for the other, with only minor unfamiliar vocabulary? If yes → mode flags. If no → separate TAPPs.

### Mode flag column assignments

Once the modes are identified, assign one column per mode starting at column I (immediately after H, Last Update), in order of decreasing frequency of use (put the most common mode first). Record the column label for each mode — this becomes the header for that mode's flag column in the TAPP.

For **single-mode techniques**, use one mode flag column set to Y for all applicable fields, or omit mode flag columns entirely if sub-mode distinctions are irrelevant.

### Inputs for Phase 0

**Technique scope and mode identification** should be grounded in review papers — broad methodological overviews, instrument-platform reviews, and community best-practice papers that survey the full landscape of the technique. These are not seed papers; they inform scope decisions and mode flag definitions but are not carried forward into Phase 1 field generation.

### Inputs for Phase 1

Two types of input material inform Phase 1, and either or both may be provided:

**Seed papers** are application papers and procedure papers drawn from the relevant technique directories. The primary selection criterion is **mode coverage**: the seed paper set must collectively cover all analytical modes identified in Phase 0. Within that constraint, prefer papers that report instrument parameters and analytical conditions in detail (dedicated methods sections, supplementary procedure tables, or data reduction appendices). Brief method summaries that omit key parameters are weak seed papers but acceptable if they are the only available source for a given mode.

**Existing procedure templates** are pre-existing structured descriptions of procedure requirements:
- Community checklists or reporting guidelines from professional societies or data repositories
- Procedure templates from instrument manufacturers
- Procedure documents from journals with mandatory metadata requirements
- Other TAPPs for related techniques that suggest transferable field vocabulary

Seed papers drive *field discovery* (what parameters exist and matter for each mode?). Procedure templates drive *structural decisions* (how should fields be organized and scoped?). Both are useful for different reasons; the best Phase 1 inputs combine them.

---

## Phase 1 — Preliminary TAPP Generation

**Purpose:** Generate a draft TAPP from seed papers and/or existing procedure templates, using the reference TAPP structure as a template.

**Who leads:** AI.

**Inputs:** Technique scope document, mode flag column assignments, seed papers and/or existing procedure templates, reference TAPP.

**Outputs:** Preliminary TAPP as a CSV file with all six groups populated.

### What the AI does in Phase 1

1. Read all seed papers and procedure templates thoroughly before generating any fields.
2. Inherit the six-group structure from the reference TAPP: (1) Procedure Identification, (2) Samples, (3) Instrument & Software, (4) Measurement Information, (5) Data Processing, (6) Quality Control & Uncertainty.
3. For each field, propose: name, description, data type, example content, procedure-level tier, and mode flag values.
4. Flag fields where the procedure-vs-analysis distinction is uncertain. Do not silently assign a tier for ambiguous fields — mark them for Phase 2 review.
5. Flag fields where a split (one field → two) might be appropriate. Common split candidates: threshold vs. measured value; method vs. result; procedure target vs. session-actual.

### What NOT to do in Phase 1

- Do not attempt to be exhaustive. A preliminary TAPP with 60–70 fields is better than one with 120 fields including redundant or poorly-scoped items. Fields can be added in Phase 4.
- Do not finalize descriptions. Phase 1 descriptions are working drafts; they will be substantially revised in Phase 2.

### Analysis-level tiers in Phase 1

Assign **preliminary** analysis-level D-tier values in Phase 1 based on judgment from the seed papers. These are working drafts — they will be evaluated and refined during Phase 2 review, and confirmed or revised against literature evidence in Phase 3. Flag any D-tier assignment that feels uncertain; these are priority items for Phase 2 discussion.

### Typical field count by group (from LA-ICP-MS experience)

The following is provided as a reference only. The actual field count for any TAPP is determined by the technique and the Phase 2 review — there is no upper or lower bound enforced by group.

| Group | Typical field count |
|---|---|
| 1. Procedure Identification | 12–16 |
| 2. Samples | 6–10 |
| 3. Instrument & Software | 10–14 |
| 4. Measurement Information | 20–30 |
| 5. Data Processing | 12–18 |
| 6. Quality Control & Uncertainty | 8–12 |
| **Total** | **68–100** |

Groups 4 and 5 are the most technique-specific. Groups 1, 2, and 6 are largely transferable from the LA-ICP-MS template with minor modifications.

---

## Phase 2 — Structured Field Review

**Purpose:** Refine every field in the preliminary TAPP through principled evaluation of four questions. This is where the intellectual work of procedure metadata design happens.

**Who leads:** Human (with AI supporting specific items on request).

**Inputs:** Preliminary TAPP CSV from Phase 1.

**Outputs:** Revised TAPP CSV with procedure-level tiers assigned, descriptions finalized, mode flags confirmed, and rationale recorded for non-obvious decisions.

### The Four-Question Review

Apply these questions to every field in Groups 3–6 (Groups 1 and 2 are mostly transferable and need lighter review). Work through the groups in order; decisions in Group 3 often inform Groups 4 and 5.

#### Question 1 — Ontological: Procedure or Analysis?

*Is this field's value set before the session begins (procedure-level) or determined during or after the session (analysis-level)?*

Heuristics:
- **Procedure-level**: The value is decided during method design and applied consistently across all analyses following this procedure. A researcher running this procedure at a different lab would need to know this value.
- **Analysis-level**: The value cannot be known until the analysis is performed. It depends on the specific sample, the session date, instrument condition that day, or data reduction decisions made after the fact.
- **Both levels**: Some fields have a procedure-level component (the target or threshold) and an analysis-level component (the measured or actual result). These typically warrant splitting. See `references/precedents.md`.

Key test: *Could this value appear in a registered procedure document before any analysis is run?* If yes → procedure-level. If it requires actual data → analysis-level.

#### Question 2 — Mode Applicability: Which modes?

*For each analytical mode defined in Phase 0, does this field apply (Y) or not (N)?*

Evaluate the field against each mode independently. Three outcomes per mode:

- **Y — applies, same meaning**: The field applies to this mode with the same interpretation as other modes.
- **Y — applies, different meaning**: The field applies but means something different in this mode. Keep as one field; add mode-specific clarification to the description.
- **N — does not apply**: The concept does not meaningfully exist for this mode.

When a field applies to only one mode, consider encoding the restriction in the field name (e.g., "Raster Line Spacing (Mapping Only)") if the mode restriction is fundamental to the concept.

**"Not applicable" vs. "not typically done":** Set N only when the concept itself does not exist for that mode. Set Y (with a description note) when the concept exists but is rarely used — this preserves the ability to document the absence as a deliberate choice.

This question must be answered for every mode defined in Phase 0, not just three — if the technique has five modes, evaluate all five.

#### Question 3 — Granularity: One or Two Fields?

*Should this concept be one field or split into two?*

Split when:
- The two components have different tier assignments (procedure target vs. analysis measurement)
- Users would legitimately search or filter on each component independently

Do not split when:
- The two components are always reported together
- Splitting would create a field that is almost always blank
- The combined field is already concise and unambiguous

Common split candidates across technique families:
- Acceptance criterion / threshold (procedure) vs. measured value (analysis) — split when these are genuinely different types of information (e.g., Oxide Production Method and Threshold vs. Oxide Production)

Fields that should NOT be split — use D=Editable instead:
- Procedure scope vs. analysis execution for the same quantity (e.g., Analyte: procedure registers the intended suite; analyst records the actual subset) — use C=Basic, D=Editable
- Procedure target vs. session-actual value for tunable parameters (e.g., flow rates, fluence, spot size) — use D=Editable, not a separate analysis-level field

#### Question 4 — Tier Assignment: Assign C and D values

*Given the procedure-to-analysis linkage, what are the appropriate tier values?*

See `references/field-review.md` for decision tables and heuristics. Key rules:

- **C=Basic**: The procedure is under-specified without this field.
- **C=Advanced**: Best practice but not mandatory for registration.
- **C=N/A**: This field can only be known at analysis time.
- **D=Read-Only**: Changing this value would mean running a different procedure. Also used for fields that are relevant only at procedure level — the value is inherited from the procedure record and shown read-only in the analysis form.
- **D=Editable**: Procedure target or typical value; legitimately confirmed or adjusted during the session within procedure-defined bounds.
- **D=Basic**: Analyst must provide this value from the analysis; it cannot be pre-specified in the procedure.
- **D=Advanced**: Useful but not required for a credible analysis record.
- **D=N/A is not valid.** Every field must have a meaningful analysis-level assignment. See `references/conventions.md` and `references/precedents.md`.

### Recording Rationale

For every non-obvious tier assignment or structural decision, record a brief rationale note. A separate running document is fine. Rationale becomes essential when community reviewers challenge specific choices and prevents the same debates recurring on TAPP updates.

---

## Phase 3 — Literature Assessment

**Purpose:** Evaluate the TAPP against real-world reporting practices using 8–12 application papers. Validates tier assignments, surfaces missing fields, enables demotion of over-specified fields, and identifies metadata reported in the literature but absent from the TAPP.

**Who leads:** AI (with human validation of a sample).

**Inputs:** Revised TAPP CSV from Phase 2, selected application papers.

**Outputs:** TAPP CSV with literature assessment columns added (one column per extracted procedure); a list of candidate missing metadata items with rationale.

### Paper Selection Criteria

Select papers that maximize variation across:
- **Analytical modes** (if the technique has sub-modes): include papers using each mode
- **Target materials**: different matrices create different calibration and other technique-specific challenges
- **Instrument generations**: older vs. newer instruments reveal which fields are time-stable
- **Laboratories**: different lab conventions reveal which fields are truly standard vs. lab-specific
- **Scientific applications**: different disciplinary communities may have different reporting norms

Aim for 8–12 papers. Fewer than 8 may miss important variation; more than 12 adds diminishing returns.

### Procedure Separation

A single paper may contain multiple distinct procedures. Separate them into distinct assessment columns when:
- Different analytical modes are used in the same paper
- Different instrument settings are used for different target materials (constituting distinct procedures)
- A multi-run or multi-stage design is used where each run/stage constitutes a distinct sub-procedure

Give each column a header identifying: paper citation, target material, and analytical mode.

Keep all fixed columns unchanged — specifically the columns specifying metadata item names, descriptions, tiers, data types, examples, and mode flags. The exact column letters of these fixed columns depend on the number of modes defined in Phase 0.

### Filling the Assessment

For each field and each procedure column:
- Report the actual value as directly stated in the paper (paraphrase where needed for length)
- Use **N** when the field is applicable to this procedure but not reported in the paper, or when the value can only be inferred from context but is not directly stated
- Use **N/A** when the field is genuinely not applicable to this procedure (e.g., a spatial scanning parameter for a point-only technique)
- Never leave blank — blank is ambiguous between N and N/A

**Inference rule:** If a value is logically implied by other reported values but not stated directly, record N. Only directly stated values are reported. This prevents the assessment from mixing reported data with the assessor's interpretation.

**Source rule:** Every extraction must be traced to a specific sentence, table cell, or figure caption in the source document. Never rely on session summaries, prior notes, or common practice as a substitute for reading the original text. If the source document has not been read directly in the current session, read it before filling any column. Detection limits, interference corrections, and other values reported in tables or supplementary material are as valid as those in the main text — check tables explicitly.

### Identifying Missing Metadata Items

After filling all procedure columns, scan systematically for concepts that appear consistently in the papers but have no corresponding TAPP row. For each candidate missing item:
- Describe the concept and what it documents
- Identify which papers report it and how (with brief examples)
- Propose a field name, description, data type, and tier assignment
- Note which mode(s) it applies to

Present these as a structured list for human review before Phase 4. Do not add them to the TAPP unilaterally.

### Post-Assessment Analysis

After filling all columns, count for each field:
- How many procedures report a value (not N, not N/A)
- How many procedures mark N/A (genuinely not applicable)
- Reporting rate among applicable procedures = (reported) / (reported + N)

Use these rates to inform Phase 4:
- Near 0% reporting → candidate for demotion to Advanced or removal
- Near 100% reporting → confirm as Basic; consider raising D tier if currently Advanced
- Inconsistent reporting → description may need clarification or scope narrowing

---

## Phase 4 — Post-Assessment Revision

**Purpose:** Revise the TAPP based on what the literature assessment revealed.

**Who leads:** Human (with AI implementing agreed changes via targeted patch scripts).

**Inputs:** Assessed TAPP CSV from Phase 3, post-assessment analysis, list of candidate missing fields.

**Outputs:** Final TAPP CSV (vN); regenerated xlsx for sharing.

### Systematic Review Checklist

Work through these checks in order:

1. **Zero-reporting fields**: 0% reporting among applicable procedures → demote to Advanced, move concept to description note, or remove. Do not remove if important for reproducibility even when currently under-reported — document in rationale.

2. **Missing fields**: Review candidate list from Phase 3. Add agreed new fields with appropriate tiers, descriptions, and mode flags.

3. **Tier mismatches**: Fields where literature reporting rate contradicts the assigned tier. Example: a Basic field reported by only 2 of 12 papers should reconsider whether Advanced is more appropriate.

4. **Description inadequacies**: Fields where reported content in papers reveals the description does not fully capture what users report. Update accordingly.

5. **Analysis-level tier assignments**: Assign or confirm all D column tier values based on literature evidence. This is the primary purpose of Phase 3 from a tier-assignment perspective.

6. **Mode flag corrections**: Papers may use a technique in a mode not anticipated in Phase 0. Correct mode flags and add mode definitions to the Legends sheet if needed.

### Implementing Changes

Use targeted patch scripts (see `references/conventions.md`) for small changes. For large structural revisions (many new fields, group reordering), regenerate the CSV from scratch. Always increment the version number and regenerate the xlsx after Phase 4 changes are complete.

### Version Numbering

Major structural revisions (field additions/removals, tier changes, mode flag changes) → increment integer version (v4 → v5).
Description updates and example content improvements with no structural changes → decimal update (v5.1) or column H (Last Update) date update only.
