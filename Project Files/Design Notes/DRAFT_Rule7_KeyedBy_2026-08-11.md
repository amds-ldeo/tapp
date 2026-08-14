# DRAFT — Rules 7–10 for `references/conventions.md`

Status: **EXECUTED AND RATIFIED 2026-08-11.** Rules 7-10 are now in
`Claude Skills for TAPP/references/conventions.md`; this file is kept as the working record of the
reasoning, the six tests behind it, and the Appendix A audits. The convention text in `conventions.md`
is authoritative — where the two differ, that one wins.

Retrofit outcome: 16 TAPPs, 1,690 rows keyed (372 non-`(none)`), 8 modules, 30 new mandatory field rows,
Comments reduced from ~330 populated rows to 63. `validate_tapp.py --root .` 0 ERROR / 0 WARN;
`compose_tapp.py --check` 50/50 MATCH. All 16 version-bumped, xlsx regenerated. See the
2026-08-11 entry in `TAPP_Development_Log.md`.

Author decisions incorporated: `Keyed By` at Column I; single-pass retrofit; the two new mandatory fields
promoted to their own rule numbers (8, 9); `Error Correlation` library-wide but restricted in scope
(Rule 10); `SKILL.md` Common Mistake #5 rewritten; the `x` cross-product notation with an ordering
convention; Comments column retained.

Insert after Rule 6, before the `### Field names` section.

---

### Rule 7 — "Keyed By": every field declares what its value repeats over

Every content row in every TAPP carries a **`Keyed By`** value stating what the field's value repeats
over — the field's *cardinality key*. A field holding one value per procedure declares `(none)`. A field
holding one value per analyte, per mass, per reported quantity, or per grain declares that key.

Rule 7 exists because the label it replaces was doing this job badly. `Analyte-Specific` appeared 150
times across 45 field names and was found to carry **at least four distinct keys** while missing a fifth
entirely:

| Symptom | Evidence |
|---|---|
| Fewer than half of labelled fields are actually keyed by analyte | 22 of 45 (49%) |
| The label conflates keys with opposite tier signatures | analyte/channel fields are 90% D=Read-Only-or-Editable; reported-property fields are 82% D=Basic (Fisher exact p = 9.8 × 10⁻⁶) |
| Fields with the same label cannot be joined | one Fe-isotope session yields row counts 1, 6, 6, 3, 2, 2, 2, 0 under a single label |
| A whole key had no label at all | 13 unlabelled fields are keyed by reported property, including all 6 fields of Module_Geochronology and Rule 5's `Constants and Reference Values Used` |
| The label is technique-conditional, not universal | XCT 0 instances, SEM_Imaging 1, SEM_FIBSEM 1, TEM 3 — 5 of 150 across the four least chemical TAPPs |

The framework had already written the distinction into a field description without propagating it into the
vocabulary. `Reported Variables and Units` reads: *"distinct from Analyte and Monitored Isotopes, which
record what was acquired. A procedure may acquire many masses and report a small number of derived
quantities."*

**`Analyte-Specific` is not renamed or redefined by this rule. It is demoted** — from a label to one value
among several, and not the most common one.

---

#### 7.1 Column placement

`Keyed By` is inserted as **Column I, immediately after H (Last Update) and before the first mode-flag
column**. Columns A–H are unchanged. Mode-flag columns, the `Literature Assessment` sentinel and all
literature assessment columns shift right by one.

| Col | Header |
|---|---|
| A–H | Metadata Item, Description, Procedure-Level Tier, Analysis-Level Tier, Data Type, Example / Allowed Content, Comments, Last Update — **unchanged** |
| **I** | **`Keyed By`** — one value from 7.2, using the notation in 7.3; never blank on a content row |
| I+1 … | Mode flag columns, sentinel, literature assessment columns |

This is safe because the column structure section already states: *"There is no fixed column letter for
either boundary."* Both boundaries are located by header, not position — the sentinel by its exact header
text, the mode flags by falling between `Keyed By` and the sentinel. Locating the mode block as "between
`Keyed By` and the sentinel" is the only parser change required, and Rule 6.4's ownership letters (A–E
module, F–H consumer) are untouched.

**Placement trade-off, recorded so it is not relitigated.** `Keyed By` belongs *semantically* next to
Column E: Data Type states what kind of value a field holds, `Keyed By` states how many, and a metadata
form generator reads the two together. It is placed at I instead because Rule 6.4 assigns module column
ownership by letter and the module manifests encode those letters literally
(`"owned_columns": ["A","B","C","D","E","F"]`, `"overlay_columns": ["F"]`). Inserting at F would silently
change the meaning of every `owned_columns` list, every "Column F/G/H" reference in `conventions.md`,
`SKILL.md`, `field-review.md` and `lit_assessment.md`, and the ownership logic in `compose_tapp.py`.
Position I buys stable A–H lettering at the cost of the semantic adjacency; the adjacency is documented
here instead.

---

#### 7.2 Key vocabulary

**Anchors.** Two are universal; two are conditional and legitimately absent from some techniques.

| Value | Keys on | Test to apply | Examples |
|---|---|---|---|
| `sampling unit` *(universal)* | a subdivision of the physical sample carrying its own row of values | Would a second grain / spot / phase produce another row? | EPMA analysis point; zircon grain; digestion aliquot; Mössbauer phase; fission-track confined track; XCT segmented phase; OSL aliquot |
| `reported property` *(universal)* | anything the procedure reports, **at any point in the chain** — quantities and nominal properties alike, plus their uncertainties | Does it appear in the reported data product? | ²⁰⁶Pb/²⁰⁴Pb ratio *and* ²⁰⁶Pb/²³⁸U date; ⁵⁶Fe/⁵⁴Fe *and* δ⁵⁶Fe; Dᴇ, D_R *and* OSL age; Fe³⁺/ΣFe; mineral species + match score; porosity |
| `channel` *(where a dispersive or selective axis exists)* | a position on the instrument's selection axis — **the address, not the signal** | Does the position exist even with zero signal there? | m/z 238; cup L2 at magnet step 1; Fe Kα on LIF spectrometer 2; Fe L₂,₃ edge; velocity channel 137/256; 855 cm⁻¹ bin |
| `analyte` *(chemistry only)* | the chemical species determined, at whatever granularity the procedure determines it | Would substituting a different isotope of the same element leave the target of determination unchanged? Yes → `channel`. No → `analyte`. | Si, Mg, Fe, Ca, Ni (EPMA); Fe (MC-ICP-MS); U, Pb, Th (U-Pb); Fe²⁺/Fe³⁺ at valence resolution (Mössbauer) |

**Secondary keys.**

| Value | Keys on | Examples |
|---|---|---|
| `standard` | a reference against which something is anchored — physical **or virtual**. Record which axis it anchors; this varies by technique. | albite (anchors analyte); IRMM-014 (anchors reported property); α-Fe foil NBS SRM 1541 (anchors *channel*); RRUFF reference spectrum (virtual); dosimeter glass |
| `conversion` | a correction or calculation step, **only where it cannot be attributed to a single reported property** | ²⁰⁴Pb common-Pb composition (feeds all dates); Mössbauer Debye temperatures (two constants, one Fe³⁺/ΣFe); XCT beam-hardening |
| `model component` | a component of a fitted decomposition of the signal | Mössbauer doublets/sextets (IS, QS, B_hf, Area%); Raman fitted peaks; XRD Rietveld phases; EELS edge components |
| `acquisition pass` | a distinct pass over the sample with its own instrument settings | EPMA Na/K at 10 nA vs. Si/Mg/Fe at 40 nA; `Multi-Run Sequential Analysis Design`; Raman 532 nm vs. 785 nm |
| `preparation step` | a stage in sample preparation | multi-step digestion (temperature, duration, acid per step); sequential chromatography columns; etch steps |

**Technique-specific extensions** are permitted. They are declared in Phase 0 (7.7) and listed in the
TAPP's Legends sheet. Prefer an existing anchor before minting one: `phase`, `sub-volume`, `replicate`,
`spot` and `grain` are all `sampling unit`; `cup`, `detector` and `energy-loss edge` are all `channel`.

**`mode` is not a valid value.** Mode applicability is carried by the mode-flag columns (Rule 3). A mode
key would duplicate existing machinery.

---

#### 7.3 Notation

| Form | Meaning | Example |
|---|---|---|
| `(none)` | scalar — one value per procedure/analysis. The default and the most common value. | `RF Power`; `Instrument Make and Model` |
| `A > B` | **containment** — B exists only within A; one value per B within each A | `analyte > background position`; `sampling unit > model component` (Mössbauer components fitted per phase) |
| `A x B` | **cross-product** — A and B are independent domains; one value per combination. Ordered: read as *"for each A, one value per B."* | `standard x reported property` (`Analytical Precision`); `sampling unit x analyte` (`Counting Statistics Error`) |
| `defines: A` | the field **enumerates** the key domain rather than being keyed by it — it is the header of the child table, not a column in it | `Analyte`; `Monitored Isotopes`; `Reported Variables and Units`; `Reported Date Type` |
| `pair: A` | keyed by an unordered pair of A | `Discordance Definition and Values`; error correlation ρ between ²⁰⁶Pb/²³⁸U and ²⁰⁷Pb/²³⁵U |

**Distinguishing `>` from `x` — the enumerability test.** *Can you enumerate B without reference to A?*

- **No → `>`.** Background positions are stated relative to a peak; "high side, +2 mm" is meaningless
  without knowing which analyte's peak. Mössbauer sub-spectral components come from fitting one phase's
  spectrum and do not exist independently of that phase.
- **Yes → `x`.** Secondary reference materials are enumerated by their own field, independently of any
  reported property. Analysis spots are enumerated independently of any analyte. `Analytical Precision` is
  therefore a two-dimensional table — one row per reported property, one column per reference material —
  not a hierarchy.

Getting this wrong asserts a containment that does not exist, which is worse than declaring a single key,
because it implies a parent-child relationship a consumer will try to build a schema around.

**Ordering convention for `x` — the order carries meaning.** `A x B` reads *"for each A, one value per
B"*: the first key is the **outer** domain, the second the **inner**. `standard x reported property` says
this field is reported for every reported property, within every standard.

The two orderings yield the same number of cells, so this is not an arithmetic distinction. It is stated
for two reasons. First, **consistency of labelling** — without a stated convention the same field is
written both ways across TAPPs and the cross-TAPP consistency check (7.8.7) cannot compare them. Second,
**the order is itself information**: it tells a reader how the field is organised in practice, and it is
how the reporting table is actually laid out. `Analytical Precision` is reported as a block per reference
material listing each property, not as a block per property listing each material.

Choose the order from the field's own description where it states one — `Counting Statistics Error` reads
*"for each analyte per analysis"*, and is reported as one row per analysis with a column per analyte,
giving `sampling unit x analyte`.

`defines:` is the distinction that the old label could not make. `Analyte` and `Detection Limit` both wore
`Analyte-Specific`, but one *is* the list and the other is indexed *by* the list.

---

#### 7.4 The declaration invariant

**For every key K used by any field in a TAPP, that TAPP must contain at least one field declaring
`defines: K`.** A key whose domain is never enumerated cannot be populated: a consumer told that
`Detection Limit` is keyed by reported property, with no field listing the reported properties, has been
given a child table with no rows.

Applying this invariant to the current library makes two fields mandatory across all TAPPs. Because both
are mandatory-field decrees in the style of Rules 3 and 5, they are stated as **Rule 8** and **Rule 9**
rather than buried here.

For compound keys, the invariant applies to each component: `reported property × standard` requires a
`defines: reported property` field *and* a `defines: standard` field.

---

#### 7.5 Module ownership

`Keyed By` states what a field's value repeats over. That is a property of the field definition, not of
the consuming TAPP, so it is **module-owned**, alongside Columns A–E under Rule 6.4.

| Column | Owner |
|---|---|
| A, B, C, D, E, **I (`Keyed By`)** | module |
| F (Example), G (Comments), H (Last Update), mode flags, sentinel, literature assessment | consumer |

Rule 6.4's existing letters are unchanged; the table gains one entry.

**Override mechanism.** A module may permit a consumer to override `Keyed By` for named fields by listing
them in a `keyed_by_overridable` array in the module manifest. `compose_tapp.py --check` then tolerates a
difference on those rows only, and reports `DIFFERS` everywhere else as usual.

The mechanism is specified because the need is demonstrated, but **no module field currently requires it.**
The two known technique-dependent fields — `Primary Calibration Standard Name` (`analyte` in EPMA,
`reported property` in MC-ICP-MS) and `Secondary Reference Materials` — are TAPP-owned, not module-owned.
Every module field audited holds one key across all consumers: Module_Geochronology's six are all
`reported property`, Module_MCICPMS's `Collector Configuration` is `channel` everywhere,
Module_ReportingCore's `Goodness-of-Fit or Dispersion Statistic` is `reported property` everywhere.
Do not populate `keyed_by_overridable` speculatively.

---

#### 7.6 Consequence for the Comments column

The Comments column (now H) reverts to what the column structure section says it is for: short field-level
qualifiers. It no longer carries cardinality labels, and it should no longer carry mode qualifiers either,
since those duplicate the mode flags.

**Remove** — covered by that TAPP's own mode flags:

| TAPP | Redundant labels |
|---|---|
| EPMA, SEM, SEM_Composition | `WDS specific`, `EDS specific`, `SEM-WDS specific`, `EDS and SEM-WDS`, `EBSD specific`, `CL specific`, `FIB-SEM specific`, `3D Tomography specific`, `TEM Sample Preparation specific` |
| TEM | `TEM imaging`, `STEM imaging`, `Electron Diffraction` |
| Lab-XCT | `Multi-volume only` |

**Retain** — *not* covered by mode flags:

| Label | Why it must stay |
|---|---|
| `Q-ICP-MS only`, `SF-ICP-MS only` | LA-Q/SF modes are Spot / Transect / Mapping — these are **instrument variants** |
| `EDS`, `EELS` in TEM | TEM modes are TEM Imaging / STEM Imaging / Electron Diffraction — these are **signals**, not modes |
| `KED`, `DRC`, `Double-spike only`, `Internal normalization only` | the three Solution TAPPs have **no mode-flag columns at all** |
| `Only relevant when Desolvation System is not 'None'` and similar | **conditional applicability** (Rule 6.5), not mode |

**Do not delete before validating.** A row commented `WDS specific` but flagged `Y` under EDS Point
Analysis is a data inconsistency to resolve, not a comment to remove. Run the flag/comment agreement check
first and reconcile every disagreement; only then strip the redundant text.

---

#### 7.7 Phase 0 obligation

Phase 0 must now declare **two** things, not one:

1. the mode set and its flag column labels (existing requirement), and
2. the technique's key vocabulary — which anchors apply, which are absent, and any technique-specific
   extensions with their definitions.

Both belong in Phase 0 for the same reason. Getting the keys wrong is as expensive to correct
retroactively as getting the modes wrong, because both are structural and both propagate into every row.

Record explicitly which anchors are **absent** — `analyte` for XCT, Raman and fission track; `channel`
for fission track. An absent anchor is a finding, not an omission.

---

#### 7.8 Validator invariants

`validate_tapp.py` must enforce:

1. Every content row has a non-empty `Keyed By`. Group header rows and blank separator rows are exempt.
2. Every value resolves to a vocabulary term from 7.2, a Phase 0 technique-specific extension declared for
   that TAPP, or a valid 7.3 notation form.
3. `mode` is never used as a key.
4. For every key K appearing in the TAPP — including each component of a compound key — at least one field
   declares `defines: K`.
5. In `A > B` and `A x B`, both A and B are valid keys. In `pair: A`, A is a valid key.
6. `Reported Variables and Units` and `Sampling Unit` are present in every TAPP (Rules 8, 9).
   `Error Correlation Between Reported Quantities` is present in every TAPP whose Phase 0 record declares
   jointly interpreted quantities, and absent elsewhere (Rule 10).
7. **Cross-TAPP**: a field name shared across TAPPs carries the same `Keyed By` in all of them, unless
   listed in a technique-dependent exceptions register. Currently two entries: `Primary Calibration
   Standard Name`, `Secondary Reference Materials`. This mirrors the Rule 1 / Rule 4 consistency logic.
8. **Warning, not error**: a field whose Comments column still contains a mode name matching one of that
   TAPP's mode-flag headers (7.6 cleanup not yet applied).

---

#### 7.9 Legends sheet

The Legends sheet gains a fourth table:

**Table 4: Keyed By definitions** — one row per key value used in that TAPP, with its definition from 7.2
and any technique-specific extensions declared in Phase 0; plus the five notation forms from 7.3.

Only keys actually used in that TAPP are listed. A reader of the Lab-XCT legend should not see `analyte`.

---

#### 7.10 Retrofit — single pass across all 14 TAPPs

| Item | Count |
|---|---|
| Content rows requiring a `Keyed By` value | **1,419** across 14 TAPPs |
| — non-trivial judgment | **223** (150 re-keyed from `Analyte-Specific`, 73 newly keyed) |
| — mechanical `(none)` | ~1,196 |
| Modules requiring the new column | **5 of 8** — Geochronology (6/6 fields affected), UPb (8/15), ArAr (7/16), MCICPMS (3/15), ReportingCore (1/6) |
| Module manifests requiring `owned_columns` to gain `"I"` | **all 8** (addition only — no renumbering, since A–H are unchanged) |
| New mandatory field rows to insert | Rules 8 and 9: 2 × 14 = 28. Rule 10: restricted scope, ~4 TAPPs |
| TAPPs requiring version bump + xlsx regeneration | 14 |
| Scripts | `compose_tapp.py` (column I ownership, `keyed_by_overridable`), `tapp_to_xlsx.py` (column I formatting width 22, Legends Table 4), `validate_tapp.py` (invariants 1–8) |
| Skill docs | `conventions.md` (Rules 7–10; column structure table; column width table; Legends section; Comments column description; Rule 6.4 ownership table; the "Analyte-Specific" entry in the vocabulary table), `SKILL.md` (Common Mistake #5; column structure table), `field-review.md` (~line 160), `workflow.md` (Phase 0) |

The per-TAPP judgment load is concentrated, not spread: EPMA 30, SEM 30, SEM_Composition 30,
LA-QSF_UPb 24, LA-MC_UPb 25 account for 139 of the 223.

**Sequencing.** Modules and manifests first, then recompose, then TAPP-owned rows — otherwise recomposition
overwrites hand-entered values on module rows (Rule 6.6). Column insertion is mechanical, but SEM and
SEM_Composition carry 35 literature-assessment columns each, all of which shift; verify column counts
before and after every file.

---

### Rule 8 — "Reported Variables and Units" is mandatory in Group 4 of every TAPP

Every TAPP must include a **`Reported Variables and Units`** field in Group 4, regardless of whether the
technique produces derived quantities. Currently present in 4 of 14 TAPPs (the LA variants only); missing
from EPMA, all four SEM, all three Solution, TEM and Lab-XCT — including Solution MC-ICP-MS, where derived
quantities are the entire output.

**Canonical definition:**
- Field name: `Reported Variables and Units`
- Procedure-Level Tier: Basic · Analysis-Level Tier: Read-Only · Data Type: Text (free)
- `Keyed By`: `defines: reported property`
- Placement: Group 4, immediately after `Analyte` (or after `Analytical Mode` where no `Analyte` field
  exists)
- Mode flags: Y for all modes
- Description: "The final variable(s) this procedure reports and their units — distinct from Analyte and
  Monitored Isotopes, which record what was acquired. A procedure may acquire many masses and report a
  small number of derived quantities; without this field a data consumer cannot tell which. Record every
  reported variable, including intermediate quantities that are reported alongside final ones (e.g. both
  the ²⁰⁶Pb/²³⁸U ratio and the ²⁰⁶Pb/²³⁸U date). Where a reported variable is a nominal property with no
  magnitude (e.g. a mineral identification), record the variable and leave the unit as 'N/A — nominal
  property'."

**Purpose — two jobs.** First, it enumerates the `reported property` key domain, satisfying the Rule 7.4
invariant for the most heavily used key in the library. Second, it declares the procedure's **scope
boundary**: a derived quantity stays inside the TAPP when every input comes from this measurement plus
procedure-registered constants and calibrations, and becomes a *coupled* procedure when any input requires
another measurement. A U-Pb date is composed into the TAPP; an OSL age, which requires K/Th/U determined by
a separate technique, is coupled via the Group 1 coupling fields.

**Why the boundary must be declared per procedure, not per technique.** Jayasuriya et al. (2004) impose
fO₂ as an experimental condition and measure Fe³⁺/ΣFe; McCammon et al. (2004) derive fO₂ from Fe³⁺/ΣFe on
the same technique and the same analyte. The same quantity is an input in one procedure and an output in
the other. No technique-level rule can express that; a per-procedure declaration can.

**Why C=Basic:** mandatory declaration, following Rules 3 and 5 — universal presence is itself
informative.

**Why D=Read-Only:** the reported variable set is a defining property of the registered procedure. An
analysis that reports a different variable set is running a different procedure.

---

### Rule 9 — "Sampling Unit" is mandatory in Group 2 of every TAPP

Every TAPP must include a **`Sampling Unit`** field in Group 2 (Samples). No TAPP currently declares the
physical subdivision to which one row of reported values corresponds. `Sample Name` names the sample, not
the unit.

**Canonical definition:**
- Field name: `Sampling Unit`
- Procedure-Level Tier: Basic · Analysis-Level Tier: Basic · Data Type: Controlled list + Text
- `Keyed By`: `defines: sampling unit`
- Placement: Group 2, immediately after `Sample Name`
- Mode flags: Y for all modes
- Description: "The physical subdivision of the sample to which one row of reported values corresponds —
  the unit that is analysed and reported, as distinct from the sample as a whole. State the unit type at
  procedure level and the units actually analysed at analysis level. Where units nest (e.g. confined
  tracks within grains), state both levels."
- Example / Allowed Content: `Whole sample | Aliquot | Grain | Spot | Analysis point | Phase | Sub-volume
  | Track | Region of interest` + free text for the instances analysed

**Purpose:** without it, a consumer cannot tell whether a reported value is per grain, per spot, per
aliquot or per phase. McCammon et al. (2004) report four Fe³⁺/ΣFe values from a single run product because
four phases coexist in it; nothing in the present structure expresses that, and a curator merging such a
dataset would have no basis for deciding whether four rows represent four samples or one.

**Why C=Basic:** the procedure declares the kind of unit it is designed to analyse.

**Why D=Basic:** the units actually analysed — which grains, which spots, which phases — cannot be known
until the session runs.

---

### Rule 10 — "Error Correlation Between Reported Quantities" is required where quantities are jointly interpreted

**Scope: restricted, not universal.** Unlike Rules 3, 5, 8 and 9, this field is required only in TAPPs
whose procedures report two or more quantities that are **interpreted jointly** — any procedure producing
a concordia plot, an isochron, a three-isotope plot, or any other regression or ratio taken across two
reported quantities. Where present it sits in Group 5, immediately before
`Constants and Reference Values Used` (which Rule 5 requires to remain last).

Currently in scope: `LA-Q_SF-ICPMS_UPb`, `LA-MC-ICPMS_UPb`, `Solution MC-ICP-MS` (double-spike inversion
and three-isotope work), and `Module_Geochronology` consumers generally. Determined per TAPP in Phase 0
alongside the key vocabulary (7.7); a TAPP that reports only independent quantities omits the field rather
than recording `N/A`.

This departs from the Rule 5 precedent deliberately. Rule 5's universal-presence argument — that
"deliberately none" is informative — holds for constants, which any data reduction chain might use. A
correlation coefficient between reported quantities is meaningless where quantities are never jointly
interpreted, and 10 of 14 TAPPs would carry a permanently empty field.

**Canonical definition:**
- Field name: `Error Correlation Between Reported Quantities`
- Procedure-Level Tier: Advanced · Analysis-Level Tier: Basic · Data Type: Numeric + Text
- `Keyed By`: `pair: reported property`
- Placement: Group 5, immediately before `Constants and Reference Values Used`
- Mode flags: Y for all modes of the TAPPs in which it appears
- Description: "The correlation coefficient between pairs of reported quantities whose uncertainties are
  not independent, together with the pair it applies to and how it was obtained. Concordia and isochron
  regressions cannot be reconstructed without it."

**Purpose:** verified gap. An exact-phrase search for "error correlation", "rho" and "correlation
coefficient" returns nothing in LA-Q/SF-ICPMS_UPb v6, LA-MC-ICPMS_UPb v2 or Module_UPb.
`Uncertainty Propagation Method` propagates to *"the final reported value"* — singular, with no treatment
of correlation between values — and `Uncertainty Level` covers only the sigma convention. Concordia
ellipses therefore cannot be reconstructed from what the TAPPs currently capture.

**Why library-wide rather than a geochronology module field.** It recurs across dating systems (U-Pb
concordia; Ar-Ar, Rb-Sr and Re-Os isochrons) but also occurs outside geochronology (triple-oxygen
δ¹⁷O/δ¹⁸O; double-spike inverted ratios in MC-ICP-MS), so it fails Rule 6.1's specificity condition.
Module_Geochronology's own manifest sets this precedent explicitly: *"Fields that recur across dating
systems but also occur elsewhere … are general TAPP gaps and are handled as library-wide rules, not here."*

**Lowest priority of the three new fields.** Rules 8 and 9 close structural gaps affecting every TAPP;
Rule 10 touches roughly four. It can be deferred to a later pass without undermining Rules 7–9.

---

## `SKILL.md` — replacement for Common Mistake #5

The current text is the mechanism that produced the defect Rule 7 corrects: it instructs every TAPP author
to reach for the least universal axis by default.

**Remove:**

> **5. Using "Element-Specific" instead of "Analyte-Specific".** The correct term is Analyte-Specific to
> remain technique-agnostic across all TAPP types.

**Replace with:**

> **5. Recording how many values a field holds in the Comments column.** Cardinality is declared in
> Column I (`Keyed By`) under Rule 7, never in Comments. Ask what the field's value repeats over and
> declare that key: `(none)`, `analyte`, `channel`, `reported property`, `sampling unit`, or one of the
> secondary keys. Do not reach for `analyte` by default — it applies to fewer than half the fields that
> once carried the `Analyte-Specific` label, and it is absent entirely from techniques with no chemical
> species (XCT, Raman, fission track). The Comments column carries only qualifiers that are neither mode
> nor cardinality; mode applicability belongs in the mode-flag columns.

`SKILL.md` also carries a column structure table that must gain the Column I row.

**Both copies must be updated.** The project copy at `Claude Skills for TAPP/SKILL.md` is the source of
truth; the skill installation copy does not auto-sync and must be re-copied afterwards.

---

## Appendix A — Flag/comment agreement check, and what should replace the Comments column

Run 2026-08-11 against all 14 current TAPPs, read-only. Nothing was modified.

### A.1 Agreement check result — no flag data bugs found

142 rows carry a Comments-column mode label that can be checked against that TAPP's own mode flags.
**39 disagree (27%).** The direction is uniform: in every case the flags are as precise as or more precise
than the comment. No case was found where the flags are wrong and the comment right.

| Pattern | Rows | Reading |
|---|---|---|
| Comment **coarser** than the flags | ~28 | `FIB-SEM specific` spans TEM Sample Preparation *and* 3D Tomography, but `Lift-out Method` is sample-prep only and `Slice Thickness` is tomography only. `WDS specific` on `Peak Counting Time` where WDS Mapping is legitimately `N` — mapping uses dwell time per pixel, and `Sequence`'s own description already says *"Not applicable to X-ray mapping."* |
| Comment **narrower** than reality | 5 | TEM `Convergence Semi-Angle` and `Camera Length` commented `STEM imaging` but flagged `Y` for Electron Diffraction. Both are fundamental to CBED. Flags right, comment wrong. |
| **Needs a specialist call** | 6 | `Step Size / Pixel Size` (SEM, SEM_Composition) commented `EDS specific` but flagged `Y` for WDS Mapping and `N` for EDS Point Analysis — it is *mapping*-specific, not EDS-specific; a genuine mislabel. `Halogen Correction on Oxygen` commented `SEM-WDS specific` but flagged `Y` under EDS Point Analysis — needs a decision on whether the correction applies to EDS quantification. |

**Consequence for 7.6.** The prerequisite is satisfied. The mode-label cleanup can proceed in the same pass
as the Rule 7 retrofit, because deleting these comments loses no correct information — the flags already
carry it, more precisely. Only the 6 rows above need review, and none of them blocks the pass.

**Incidental finding.** `LA-MC-ICPMS_TAPP_v3` carries `Q-ICP-MS only` and
`SF-ICP-MS: adjustable mass resolution … Q-ICP-MS: unit resolution only` comments, inherited from
`LA-Q_SF-ICPMS_TAPP_v6` when it was derived. These are wrong for a multi-collector TAPP and should be
removed rather than migrated. This is the same class of inherited-description problem already logged in
`composed_tapps.json` open items for that file.

### A.2 What remains in the Comments column, and how to structure it

After removing mode labels and `Analyte-Specific`, 95 rows retain content. The residue is not
miscellaneous — it falls into five groups, three of which are structured data wearing free text.

| Group | Rows | Content | Proposal |
|---|---|---|---|
| **Instrument variant** | 38 | `Q-ICP-MS only`, `SF-ICP-MS only`, `SF-ICP-MS: adjustable mass resolution (300–10,000)` | **Second flag family** (A.3) |
| **Signal / detector** | 37 | `EDS`, `EELS`, `KED`, `DRC`, `EELS (EFTEM)` | **Second flag family** (A.3) |
| **Conditional applicability** | 10 | `Only relevant when Desolvation System is not 'None'`; `Only relevant when Internal Standard Element is not 'None'`; `Only relevant when E-scan acquisition mode is used` | **New `Conditional On` column** (A.4) |
| **Recording instruction** | 5 | `record 'N/A' if not applicable` | Fold into Column B, following the Rule 5 description's own precedent |
| **Explanatory prose / working notes** | 5 | HAADF collection-angle physics; camera-length calibration note; `C=Advanced vs Basic: pending lit assessment` | Prose → Column B. Working notes → `TAPP_Development_Log.md`, not the TAPP. |

### A.3 Resolution — no new column mechanism is needed

The rev. 2 proposal for a general "flag family" mechanism is **withdrawn**. Three existing mechanisms
between them absorb the whole residue, and the author's proposed TAPP split removes the largest group
outright.

**(a) Instrument variant (38 rows) — split the LA-Q/SF TAPP.** The combined TAPP is the library's outlier:
`Solution Q-ICP-MS` and `Solution SF-ICP-MS` are already separate TAPPs with separate Phase 0 records.
There is no principled reason for the laser-ablation front end to change that, and a registered procedure
describes one instrument.

Feasibility is confirmed. Of 126 content rows in `LA-Q_SF-ICPMS_TAPP_v6`:

| | Rows |
|---|---|
| Q-ICP-MS only | 7 |
| SF-ICP-MS only | 3 |
| Applies to both, with **different content per instrument** | 1 — `Mass Resolution Setting` |
| Shared, unlabelled | 115 |

`Mass Resolution Setting` is the strongest argument for the split, not against it: its Column F currently
has to carry both answers at once (*"SF-ICP-MS: adjustable mass resolution (300–10,000); Q-ICP-MS: unit
resolution only"*). After the split each file states one.

The 91% overlap is not duplication — it is what Rule 6 composition exists to handle. Two consequences to
plan for:

- `LA-Q_SF-ICPMS_TAPP` and `LA-Q_SF-ICPMS_UPb_TAPP` become four files, taking the library from 14 TAPPs
  to 16. Retrofit counts in 7.10 must be recomputed against 16.
- With `LA-Q` + `Solution Q` and `LA-SF` + `Solution SF` each sharing an analyser block, a
  `Module_QuadrupoleICPMS` / `Module_SectorFieldICPMS` pair becomes a live extraction candidate. Per Rule
  6.10 modules are extracted, not invented — flag it, do not build it in this pass.

**(b) Signal / detector (37 rows) — additional mode columns, not a new family.** Mode flags are already
independent Y/N columns with no exclusivity constraint, so a field can be `Y` for STEM Imaging and `Y` for
EDS simultaneously. The rev. 2 orthogonality objection was wrong: the existing mechanism already expresses
orthogonal axes.

**Multiplicity is real and settles the shape of the fix.** Seven TEM rows name two or more signals:

| Field | Signals named |
|---|---|
| `STEM Dwell Time per Pixel` | EDS, EELS, 4D-STEM |
| `Spectroscopic Detector(s)`, `Analyte`, `STEM Probe Diameter`, `STEM Probe Current`, `STEM Scan Dimensions`, `STEM Frame Averaging` | EDS, EELS |

A single column holding a delimited list of applicable signals would reintroduce exactly the
structure-in-free-text problem this exercise is removing. Independent Y/N columns carry multiplicity
natively. So: **TEM Phase 0 is revised to add `EDS`, `EELS` and `4D-STEM` as mode columns**, and Rule 3's
`Analytical Mode` allowed-value list gains them.

EPMA's and SEM's `EDS` / `CL` / `EBSD` comments need nothing new — those TAPPs' existing mode columns
already cover them, so the comments are simply deleted under 7.6.

**(c) KED / DRC (10 rows) — conditional, not mode.** `Solution Q-ICP-MS` deliberately defines no mode flag
columns; its `Analytical Mode` field records *"Solution ICP-MS has a single routine mode — continuous
nebulisation."* Cell-gas mode is not that axis. KED and DRC applicability depends on the **value** of
`Collision/Reaction Cell (CRC) Configuration`, which makes it a conditional — handled by A.4.

### A.4 Resolution — `N/A` as allowed content, no `Conditional On` column

The rev. 2 proposal for a `Conditional On` column is **withdrawn** in favour of the author's approach:
allow `N/A` as explicit content in the dependent field.

Ten rows do not justify a new column plus a syntax plus validator logic. Two implementation requirements
keep the information intact:

1. **The condition is stated in Column B**, so the analyst knows when `N/A` applies — e.g. *"Record 'N/A'
   where Desolvation System is 'None'."* This is exactly the precedent Rule 5's own description sets.
2. **`N/A` is an explicit value in Column F**, not implied. Where Column F is a controlled list, `N/A`
   joins it; `validate_tapp.py` already reports controlled lists missing allowed values.

**Known trade-off, accepted.** A form generator cannot auto-hide a dependent field from a Column B
sentence the way it could from a parsed condition. Revisit only if the conditional count grows well beyond
ten.

### A.5 Net effect

| Destination | Rows | Mechanism |
|---|---|---|
| Delete — mode flags already carry it | 133 | existing |
| Removed by the LA-Q/SF split | 38 | TAPP split |
| TEM mode columns `EDS` \| `EELS` \| `4D-STEM` | 19 | existing (Phase 0 revision) |
| Column B condition + `N/A` in Column F | 10 | existing |
| Column B (descriptions, recording instructions) | 9 | existing |
| Development log (working notes) | 1 | existing |
| **Genuine free-text comments remaining** | **~3** | |

**No new column is added beyond `Keyed By` itself.** The Comments column becomes vestigial; whether to
retire it or keep it for one-off annotation is the author's call, and retaining it is harmless.

---

## Remaining decisions for the author

1. **The `×` ordering convention** (7.3) is new in this revision and fixes the canonical order of the
   reclassified fields as `standard × reported property` and `sampling unit × analyte`. Confirm before the
   retrofit encodes it.
2. **`Interference Correction Standard` was reverted** from a cross-product to plain `analyte` on review —
   the reference material is the *value* in the cell, not a second dimension, exactly as `X-ray Line` holds
   a channel as its value while being keyed by analyte. Seven cross-product fields remain, not eight.
   `Detection Limit` is flagged technique-dependent (`sampling unit × reported property` in LA, plain
   `reported property` in solution) and is resolved per TAPP during the retrofit.
3. **Sequencing of the LA-Q/SF split relative to the Rule 7 retrofit.** Splitting first means the retrofit
   runs against 16 stable files; retrofitting first means the split inherits `Keyed By` values already
   populated. Splitting first is cleaner — the split changes which fields exist, and Rule 7 assigns a key
   to every field that exists.
4. **The 6 rows in A.1 needing a specialist call** — `Step Size / Pixel Size` (mislabelled `EDS specific`
   when it is mapping-specific) and `Halogen Correction on Oxygen` (does the correction apply to EDS
   quantification?).
5. **Whether to retire the Comments column** once A.5 leaves ~3 rows in it.

Withdrawn from rev. 2 and requiring no decision: the flag-family mechanism (A.3) and the `Conditional On`
column (A.4). Both are superseded by existing machinery.
