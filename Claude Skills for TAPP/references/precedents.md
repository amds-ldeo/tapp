# TAPP Precedent Decisions

This file documents the key non-obvious decisions made during LA-ICP-MS TAPP development, with the reasoning that led to each decision. These serve as precedents for future TAPPs — when a similar question arises, check here before opening a new discussion.

Each entry follows the format: **Decision → Reasoning → Generalization**.

---

## Group 4: Measurement Information

### Ablation Duration vs. Analysis Count Time

**Decision:** These are two distinct fields with different tier assignments. Ablation Duration per Spot is procedure-level Basic (C=Basic, D=Editable for spot mode only). Analysis Count Time was removed as a procedure-level field and replaced by Signal Integration Time at analysis level only (C=N/A, D=Basic, spot/transect only, J=N).

**Reasoning:** Ablation Duration is set in the acquisition method file before the session begins and is a deliberate procedure design choice (it reflects a trade-off between signal accumulation, sample consumption, and throughput). A reproducibility expert needs to know it. Analysis Count Time, by contrast, is the width of the integration window selected during data reduction after the ablation transient is inspected — it depends on when the signal stabilizes and may vary by sample. The Signal Integration Interval Method (the rule for choosing the window) is procedure-level; the resulting count time is analysis-level.

**Generalization:** Whenever a procedure specifies a duration and data reduction later selects a sub-interval of that duration, treat them as separate fields: the duration belongs in Group 4 (Measurement Information) at procedure level; the selected interval belongs in Group 5 (Data Processing) at analysis level. The method for selecting the interval is procedure-level (Group 5); the resulting time is analysis-level (Group 5, C=N/A).

**Mode note:** For mapping, the per-pixel cycle time is determined entirely by dwell times (a procedure-level Group 4 field) — there is no post-hoc window selection per pixel. So Signal Integration Time is J=N (not applicable to mapping). The description must explain this explicitly.

---

### Ablation Duration — mode-dependent tier

**Decision:** Ablation Duration per Spot is procedure-level Basic for spot analysis only (H=Y, I=N, J=N). The corresponding concept for transect (total transect duration) and mapping (total map acquisition time) is analysis-level, not procedure-level, and therefore is not a TAPP field at all.

**Reasoning:** For spot analysis, ablation duration is set once in the acquisition method and applied identically to every analysis — it is genuinely procedure-level. For transect, the total duration depends on the transect length, which is determined at analysis time by the size of the grain or feature being profiled. The procedure fixes the scan speed; the transect length (and therefore duration) varies by sample. For mapping, the total acquisition time depends on the map area, which is also sample-dependent. In both cases, the procedure captures what it can (scan speed for transect; scan speed + line spacing for mapping) and leaves the variable parts to the analysis record.

**Generalization:** When a duration is fully determined by the procedure (spot mode), it belongs in the TAPP. When a duration is determined by a fixed procedure parameter × a variable sample parameter (transect: speed × length), the procedure captures the fixed parameter and the analysis captures the variable one. Total duration is always analysis-level in this case.

---

### Oxide Production: two fields, not one

**Decision:** Two separate fields: "Oxide Production Method and Threshold" (C=Basic, D=Read-Only) captures the acceptance criterion and measurement proxy; "Oxide Production" (C=N/A, D=Basic) captures the actual measured ratio from the session.

**Reasoning:** These serve fundamentally different purposes. The threshold is a quality gate used during instrument tuning before analysis begins — it is part of the procedure design and should never change between analyses following the same procedure. The measured value documents actual plasma conditions in the session and varies day to day. Combining them in one field either conflates a criterion with a measurement or forces one of them to be blank in most entries.

**Generalization:** Whenever a procedure specifies an acceptance criterion (threshold, maximum allowable value, or minimum acceptable value) and the analysis records an actual measurement against that criterion, split into two fields: [Concept] Method and Threshold (procedure-level) and [Concept] (analysis-level measured). Other techniques where this pattern applies: instrumental blank threshold (solution ICP-MS), peak flatness criterion (MC-ICP-MS), detector dead time threshold (TIMS).

---

### Analyte — single merged field

**Decision:** One field: "Analyte" (C=Basic, D=Editable). The procedure registers the isotope suite the procedure is designed to measure; at analysis level the analyst records the specific isotopes actually measured in the session, which may be a subset of the procedure scope.

**Reasoning:** "Target Analyte" and "Analyte" represent the same type of information (an isotope list) at different stages, not fundamentally different data. D=Editable correctly models the relationship: the procedure-registered suite is imported into the analysis metadata form; the analyst may narrow it if certain masses were excluded due to interference issues or detector limitations in that session. This is structurally identical to other session-tunable parameters (laser fluence, flow rates), which also use D=Editable. Splitting into two fields (as done in earlier versions) created an unnecessary decoupling — the procedure value could not be auto-imported into the analysis form.

**Contrast with Oxide Production split:** The Oxide Production pair (acceptance criterion vs. measured value) is kept as two separate fields because the criterion and the measurement are *different types of information* — one is a quality gate, the other is an instrumental outcome. The Analyte case has no such distinction: procedure scope and analysis execution are the same quantity at different stages.

**Generalization:** When a procedure defines the intended scope of measurements and individual analyses may execute a subset of that scope, use a single field with C=Basic, D=Editable. Do not split. This applies to: isotope suites (isotope ratio MS), element panels (ICP-MS), spectral windows (Raman, FTIR), feature sets (XCT). The split pattern is reserved for cases where the procedure-level and analysis-level components are genuinely different types of information (criterion vs. measurement).

---

### Scan Speed — procedure or analysis level?

**Decision:** Scan speed is procedure-level (C=Advanced, D=Editable) for methods where it is fixed, but becomes analysis-level when the procedure specifies a target spatial resolution rather than a fixed speed. The TAPP field "Transect Rate, Mapping Rate or Step Size" is procedure-level.

**Reasoning:** When a procedure specifies "scan speed = 9 µm s⁻¹" as an invariant, this is a genuine procedure parameter — it constrains every analysis following this procedure. When a procedure instead specifies "target pixel size = 5 µm" (from which scan speed is calculated at analysis time based on spot size and repetition rate), the target pixel size is procedure-level and the resulting scan speed is analysis-level. In the TAPP, the field captures the procedure-level specification (either fixed speed or target resolution/rate); the description explains both interpretations.

**Generalization:** When a parameter is either directly fixed by the procedure or derivable from other fixed procedure parameters (making it a procedure-level derived value), it belongs in the TAPP. When it is derived at analysis time from a combination of procedure parameters and sample-dependent variables, it is analysis-level.

---

### Signal Smoothing — applicable to all modes with caveat

**Decision:** Signal Smoothing applies to all modes (H=Y, I=Y, J=Y) but the description explicitly flags that smoothing devices are generally incompatible with high-resolution mapping.

**Reasoning:** Excluding mapping entirely (J=N) would hide an important methodological fact: using a smoothing device for mapping degrades spatial resolution by averaging aerosol pulses from successive laser shots. Analysts choosing to run a smoothed mapping procedure should be aware of this. By keeping J=Y with a warning in the description, the TAPP ensures the field appears in mapping contexts where the user can explicitly note "None" — documenting an intentional absence rather than a missing value.

**Generalization:** Set J=N (or equivalent mode flag) only when the concept is genuinely inapplicable (e.g., "Ablation Duration per Spot" cannot apply to mapping because there is no discrete "spot analysis"). Set J=Y with a caveat when the concept applies but its implementation or appropriateness differs for mapping. This preserves the ability to document the absence of a parameter as a deliberate choice.

---

## Group 5: Data Processing

### Uncertainty Propagation Method — Advanced/Editable rather than Basic/Read-Only

> **Scope narrowed 2026-08-10.** This entry governs the PROPAGATION FRAMEWORK only. The
> uncertainty *level* was split out into its own field, `Uncertainty Level` (C=Basic,
> D=Read-Only) — see "Uncertainty Level split from Uncertainty Propagation Method" below.
> The reasoning here is unchanged and still applies to propagation.

**Decision:** C=Advanced (not Basic), D=Editable (not Read-Only).

**Reasoning (two parts):**
- Why Advanced at procedure level: Many labs use informal uncertainty estimates (e.g., "SD of replicate analyses") without a formally specified propagation framework. Requiring a formal propagation method as Basic would either exclude many legitimate procedures or generate low-quality boilerplate. Advanced encourages rigorous labs to document their approach without mandating it universally.
- Why Editable at analysis level: If D=Read-Only and the procedure-level value is void (because C=Advanced and the author chose not to specify it), Read-Only would import a blank value that the analyst cannot fill in. Editable allows the analyst to complete this field when the procedure author left it unspecified, without constituting a violation of the procedure.

**Generalization:** When a field is Advanced at procedure level (meaning it may be void in the procedure), the analysis-level tier should almost never be Read-Only. Read-Only imports the procedure value — importing void is useless. Use Editable instead, allowing the analyst to supply the value. This is the standard resolution for the "Advanced procedure / analysis needs a value" tension.

---

### Signal Integration Interval Method — procedure-level Basic

**Decision:** C=Basic (the approach is procedure-level and mandatory). The description covers spot/transect (time-window selection) and mapping (VOI selection, phase masking) as mode-specific implementations of the same concept.

**Reasoning:** Without documenting the integration approach, a data record is uninterpretable: the reader cannot know whether specific phases were excluded from integration, whether an automated or manual approach was used, or whether the data is spatially averaged or phase-specific. This is arguably one of the most important data provenance fields in Group 5. It should be Basic.

The fact that the approach means different things for different modes (time-window vs. VOI) does not disqualify it from being a single field — the description handles the mode-specific implementation. The underlying concept (how was the usable signal distinguished from the non-usable signal?) is universal.

**Generalization:** When a concept is mode-universal in purpose but mode-specific in implementation, keep it as one field and address the implementation variation in the description. Do not split into mode-specific fields unless the implementations are so different that a shared field name would be genuinely misleading.

---

### "Constants and Reference Values Used" as a mandatory Group 5 field — purpose and distinction from Reference Material Information

**Context:** Identified while building a test TAPP for LA-ICP-MS U-Th-Pb Geochronology (derived from
Horstwood et al. 2016's community reporting standard), motivated directly by a footnote in the paper's own
Table 4 ("Decay constants of Jaffey et al. (1971) used") — information the paper's own Table 3 metadata
template never captured as a structured item, despite feeding directly into every reported age.

**Decision:** Mandatory field in Group 5 of every TAPP (Rule 5), C=Basic, D=Editable, Text (free). Record
"None" when not applicable. Applied universally — including pure-imaging/morphology TAPPs — rather than
scoped only to techniques with plausible constant-dependent data reduction (decided 2026-07-28; see Rule 5
in `references/conventions.md`).

**Reasoning:** Community-recommended values for physical constants used in data reduction — decay
constants, standard isotope ratios — are periodically revised. The ²³⁸U/²³⁵U ratio is a concrete precedent:
long assumed constant at 137.88 (Steiger & Jäger 1977), then shown by Hiess et al. (2012) to vary in
nature, prompting many labs to adopt 137.818 or sample-specific values instead. A reported age computed
under the old value cannot be correctly reinterpreted against the new one unless the original value used is
documented. This is distinct from Reference Material Information (Group 6), which documents accepted
values of *specific materials* (e.g., zircon 91500's isotopic composition) rather than *universal physical
constants* that apply regardless of which material was run.

**Generalization:** Most consequential for geochronology and any isotope-dilution-dependent technique
(⁴⁰Ar/³⁹Ar, Sm-Nd, Rb-Sr all have analogous decay-constant-revision histories), but written generally since
data reduction in any technique could in principle depend on a citable, revisable constant. Mirrors the
"Analytical Mode" precedent (Rule 3, above in Group 4): a mandatory cross-TAPP field whose universal
presence is itself informative, distinguishing "deliberately none" from "not asked."

---

## Group 6: Quality Control & Uncertainty

### Detection Limit — C=Advanced, D=Basic asymmetry

**Decision:** C=Advanced (optional at procedure level), D=Basic (mandatory at analysis level). This asymmetry is intentional.

**Reasoning:** At procedure registration time, formal LOD characterization may not yet be complete — a newly designed procedure may be registered before extensive blank measurements have been accumulated. Requiring LOD as Basic at procedure level would either block registration of new procedures or result in unreliable LOD values that the community cannot trust. Advanced is appropriate: thorough labs will include it; others will add it as the procedure matures. At analysis time, however, LOD is non-negotiable for data credibility: a published dataset without LODs cannot be properly interpreted near detection limits. Basic is appropriate at analysis level.

**Generalization:** The C/D asymmetry (Advanced procedure / Basic analysis) is the correct design for any QC metric that requires accumulated session data to characterize properly but is mandatory for any complete data submission. Other fields that warrant this treatment: detection limit method, precision, accuracy, LOQ.

### Precision and Accuracy — combined value + assessment method

**Decision:** Each precision/accuracy field captures both the assessment method and the resulting values in a single combined field. These are not split into separate "Method" and "Value" fields despite the LOD/LOD-Method split precedent.

**Reasoning:** The LOD/LOD-Method split was justified because LOD Method is a formula (a procedure-level design choice) while LOD Value is session-specific (an analysis-level outcome). For precision and accuracy, both the method and the value are Advanced/Basic at the same levels — they belong together. The method (which reference material, how many replicates, which statistic) is inseparable from the value because the same number means different things depending on how it was obtained. Splitting them would create two fields that are always filled together, adding complexity without benefit.

The description for each precision/accuracy field must explicitly require both components: the assessment method (RM used, n, statistic) and the values (per element or element group). A value without a method context is nearly uninterpretable for cross-study comparison.

**Generalization:** Split method from value when they have different tier assignments (LOD pattern). Merge them when they have the same tier assignments and are always used together (precision/accuracy pattern). The test: would either component ever be filled without the other? If no, merge.

---

## Structural Decisions

### D=N/A removed as a valid analysis-level tier

**Decision:** D=N/A is no longer a valid analysis-level tier. Fields that are relevant only at procedure level (no session-specific variation, no fresh analyst input) are assigned D=Read-Only. The procedure value is inherited into the analysis metadata form and displayed as read-only.

**Reasoning:** D=N/A ("not applicable at analysis level") and D=Read-Only ("imported from procedure, cannot be changed") produced identical behavior in the analysis submission pipeline: the value comes from the procedure and the analyst cannot modify it. The distinction provided no functional difference. Removing D=N/A simplifies the tier system to four valid analysis-level values and eliminates a source of inconsistency (e.g., "Funding Source for Procedure Development" was N/A while structurally identical fields like "Procedure Author" were Read-Only). The new invariant: every field must have a meaningful analysis-level assignment.

---

### Level-neutral field naming

**Decision:** Field names must not encode which level a value belongs to. Prefixes and suffixes such as "Default", "Target", "Achieved", "Typical", and "Actual" are not used in field names. The tier columns (C and D) encode level. Column B (Description) clarifies that the procedure registers a target or typical value and that analysts may adjust within allowed bounds.

**Reasoning:** Level-embedded names ("Default Laser Fluence", "Target Analyte", "Achieved Voxel Size") required either maintaining a separate column mapping procedure names to analysis names, or accepting that the Column A names were unusable as-is when building an analysis metadata form. Level-neutral names ("Laser Fluence", "Analyte", "Voxel Size") work directly at both levels.

**Exceptions retained:** "Target Material" and "Target Feature(s)" keep "Target" because it means *the material or feature type the procedure is designed to analyze*, not a value with a later achieved counterpart. These fields have no analysis-level counterpart requiring a different name.

---

### Coupled analysis fields — four standard fields in Group 1

**Decision:** Every TAPP includes four standard fields at the end of Group 1 (after Procedure Reference(s)) documenting multi-technique workflows: Coupled Technique(s), Coupling Description, Coupled Procedure DOI, and Coupled Dataset or Publication Reference. Default tiers: Coupled Technique(s) C=Advanced/D=Editable; Coupling Description C=Advanced/D=Editable; Coupled Procedure DOI C=N/A/D=Advanced; Coupled Dataset or Publication Reference C=N/A/D=Advanced. Individual TAPPs may adjust D tiers when coupling is computationally mandatory.

**Reasoning:** Many analytical techniques are routinely applied in combination — EPMA providing internal standard concentrations for LA-ICP-MS, XCT paired with NCT for complementary contrast, ICP-MS and noble gas MS jointly required for (U-Th)/He geochronology. Without standardised fields capturing what is coupled, how the coupling works functionally, and where the companion data lives, multi-technique datasets cannot be navigated or reproduced reliably. Group 1 is the correct location because coupling is an administrative and provenance property of the procedure design, not an instrument parameter.

**Why four fields and not fewer:** Coupled Technique(s) and Coupling Description are separated because the former enables machine-readable filtering (find all procedures coupled with EPMA) while the latter carries human-readable context that cannot be reduced to a controlled list. Coupled Procedure DOI and Coupled Dataset or Publication Reference are separated because the procedure DOI is stable and citable immediately upon procedure registration, while the dataset reference may be pending, co-submitted, or shared — the two fields have different lifecycles and reliability profiles.

**Dataset reference limitations:** A DOI pointing to a combined dataset submission does not uniquely identify which instrument produced which portion. Where coupling is documented only through a shared sample IGSN, the IGSN in Group 2 (Sample Persistent Identifier) is sufficient and the Coupled Dataset or Publication Reference field may be "None". The Coupled Procedure DOI is generally more reliable than the dataset reference and is the preferred machine-actionable link.

---

### Analysis-level fields in Group 1 (Procedure Identification)

**Decision:** Several analysis-level fields (Analyst, Analysis Start/End Date, Funding Source for Analysis) reside in Group 1 alongside procedure-level fields such as Procedure Name and Procedure Author.

**Reasoning:** Group 1 serves as the administrative header for both the procedure record and the analysis record. Analysis-level identity fields (who ran the analysis, when, under what funding) are logically co-located with procedure identity fields (who designed the procedure, when, under what funding) even though they have different tier assignments. Separating them into a different group would fragment the administrative context.

The mixed-tier nature of Group 1 is a feature, not a design inconsistency. It reflects the reality that the same form serves both procedure registration and analysis documentation.

### Procedure DOI — C=N/A, D=Basic (mandatory at analysis level)

**Decision:** Procedure DOI has no procedure-level value (C=N/A, because the DOI does not exist at the time of registration) but is mandatory at analysis level (D=Basic). The description explicitly states that if a DOI has been applied for but not yet minted, "pending" is an acceptable placeholder.

**Reasoning:** This field exists primarily as a policy instrument to encourage procedure registration. Making it mandatory at analysis level creates a direct incentive: analysts who want to submit data must have a procedure DOI (or at least have applied for one). The "pending" option prevents analysts from being blocked while waiting for DOI assignment.

The C=N/A / D=Basic combination is unusual (most analysis-level Basic fields also have a procedure-level presence) but is correct here because the DOI is a product of the registration process, not an input to it.

---

### Group 1 template — superseded by `modules/Module_Group1.csv` (migrated 2026-08-08)

**Decision (2026-05):** Every new TAPP begins Group 1 from a shared template holding the field list, tier assignments and technique-neutral descriptions; technique-specific examples are added per TAPP.

**Superseded 2026-08-08.** The template was *copied* into each TAPP, and the copies drifted: 14 of 17 descriptions in LA-Q/SF-ICP-MS diverged, field order diverged in 5 TAPPs, and one tier diverged in 3. Group 1 is now **composed** from `modules/Module_Group1.csv` under Rule 6, so the content exists in one place and cannot drift. The column-ownership split the template established informally — shared descriptions and tiers, per-TAPP examples — became the formal module contract.

**Reasoning:** Group 1 is designed to be largely transferable across TAPPs. Maintaining a single template prevents drift in field names, tier assignments, and descriptions across the TAPP library. The Coupled Technique(s) and Coupling Description fields in the template use technique-neutral language; each TAPP's example column provides technique-specific coupling examples.

---

### Group 3 software fields — D=Editable

**Decision:** Acquisition software and data reduction software fields in Group 3 are D=Editable (not D=Read-Only).

**Reasoning:** A minor version update to acquisition or data reduction software (e.g., Probe for EPMA v12.9 → v12.9.5, Iolite 4.6 → 4.7) does not constitute a new procedure — instrument hardware, operating conditions, and data reduction algorithms are unchanged. Analysts running under a minor version update should document the actual version used without being forced to register a new procedure. D=Editable is correct: the procedure registers the software name and major version; the analyst confirms or updates the minor version at analysis time.

**Contrast with hardware fields:** Instrument manufacturer, model, detector configurations, and other hardware parameters are D=Read-Only because a hardware change (different instrument, different detector) fundamentally changes what is being measured and must constitute a new procedure.

---

### Reference materials (Group 6) — C=Basic, D=Editable

**Decision:** Primary Calibration Standard Name and Secondary Reference Materials are C=Basic, D=Editable.

**Reasoning:** The procedure must commit to a specific set of reference materials (C=Basic — mandatory for procedure registration, because the choice of standards directly determines the accuracy of all results). However, at analysis time, a primary standard may be exhausted, unavailable, or temporarily substituted due to logistics. D=Editable allows the analyst to document the actual material used without being forced to register a new procedure for what is effectively a material availability substitution. The analyst is expected to note any substitution explicitly. This applies to both primary calibration standards and secondary reference materials (QC standards).

---

### WDS vs. EDS dead time — intentional asymmetry between correction method and measured value

**Decision:** WDS dead time is documented as a procedure-level correction *method* (WDS Dead Time Correction, C=Basic, D=Read-Only in Group 5) with no separate measured value field. EDS dead time is documented as an analysis-level measured *percentage* (EDS Dead Time, C=N/A, D=Basic in Group 5) with no procedure-level correction method field. These are two separate fields with no "method + value" paired structure.

**Reasoning:** The physics of dead time handling differs fundamentally between the two detector types:
- **WDS:** Dead time correction is a user-selectable mathematical algorithm (constant 3 µs, high-precision, logarithmic, etc.) embedded in the data reduction software. The analyst chooses the algorithm as a procedure design decision; it is applied transparently during intensity-to-concentration conversion. No standalone "WDS dead time" value is separately reported because the correction is absorbed into the quantitative result.
- **EDS:** Dead time correction is automatic — managed entirely by the SDD detector electronics. No user-selectable algorithm exists. What is reported is the *percent dead time*: the fraction of total acquisition time the detector spent processing rather than counting, which serves as a QC metric for count rate management. Values above ~40% indicate excessive count rate and degraded data quality.

**Generalization:** When a correction is user-selectable and algorithm-dependent, document the method at procedure level (no measured value needed). When a correction is hardware-automatic and produces a reportable QC metric, document the metric at analysis level (no method needed). Do not force a method+value split onto detector-specific processes that do not share the same structure.

---

### Beam mode (geometry) — D=Read-Only

**Decision:** Beam Mode (Focused / Defocused / Raster in EPMA; equivalent geometry fields in other techniques) is D=Read-Only.

**Reasoning:** The beam geometry is a procedure design choice tied to the target material type and analysis objective. A procedure that specifies "Focused beam for anhydrous silicates; 5 µm Defocused for glass and hydrous phases" encodes a deliberate methodological decision. Analysts follow this specification — they do not deviate from the beam mode at analysis time. Changing beam mode constitutes a different analytical approach and should trigger procedure review. D=Read-Only is correct; D=Editable would imply the analyst may override the mode without a procedure change, which is not intended.

**Contrast with Beam Diameter and Beam Current**, which are D=Editable: those are tunable operating parameters that the procedure specifies as targets and the analyst confirms or fine-tunes. Beam Mode is a categorical choice, not a continuously tunable parameter.

---

### Analysis-level only fields (C=N/A) for spatially determined mapping parameters

**Decision:** Map Dimensions (pixel count in X and Y) and Map Area (physical extent in µm × µm) have C=N/A, D=Basic. Step Size / Pixel Size (spatial resolution) has C=Basic, D=Editable.

**Reasoning:** The procedure specifies *how fine* to map (Step Size = C=Basic — a deliberate resolution design choice). The *extent* of each map — how many pixels and what physical area — is determined entirely at analysis time by the sample feature or region of interest being mapped. A procedure cannot pre-specify which grain boundary or geological texture to map. Map Dimensions and Map Area are therefore analysis-level only (C=N/A, D=Basic): they must be recorded by the analyst but cannot be pre-specified.

**Generalization:** When a mapping parameter is determined by the spatial extent of an arbitrary sample feature chosen at analysis time, it is C=N/A (cannot be pre-specified in the procedure). When it controls the intrinsic spatial resolution of the technique (step size, dwell time), it is C=Basic (a procedure design choice the analyst may adjust within bounds).

---

### EDS architecture — instrument-agnostic acquisition fields vs. technique-specific quantification

**Context:** EDS is implemented across multiple instruments covered by separate TAPPs (EPMA, SEM, TEM/STEM). During Phase 4 revision of the TEM TAPP (2026-05), a cross-TAPP EDS harmonization review compared EDS fields in EPMA_TAPP_v5 and TEM_TAPP_v5.

**Decision:** EDS acquisition and detection fields are harmonized across TAPPs (identical field names, descriptions, and tier assignments where the physics is the same). EDS quantification fields diverge by instrument because the underlying physical model differs. The two quantification frameworks are treated as separate architectural domains — not harmonized — and are candidates for dedicated "EDS (bulk)" and "EDS (thin film)" TAPPs in the future.

**Harmonized fields (acquisition and detection layer):**
- EDS Detector Configuration — same field name and structure in EPMA and TEM
- EDS Live Time per Point or Pixel — harmonized name (renamed from "EDS Acquisition Time" in EPMA v5); description notes the EPMA per-point convention vs. TEM per-point/per-pixel distinction
- EDS Energy Range — instrument-agnostic
- EDS Spectral Processing Type — same field in both TAPPs (background fitting, peak deconvolution, etc.)
- EDS Dead Time — same field; C=N/A, D=Basic in both (hardware-automatic correction, QC metric only)
- Analyte (EDS) — merged from Target Analyte (EDS) + Analyte (EDS) in TEM v5, per the level-neutral naming rule (see below)
- EDS Calibration Standard(s) — same intent across instruments
- EDS Detection Limit — same intent

**Divergent fields (quantification layer):**
- EPMA uses ZAF or phi-rho-z matrix correction for bulk samples (infinite or semi-infinite geometry). The sample absorbs the full electron interaction volume. Quantification is well-established and software-implemented.
- TEM/STEM uses Cliff-Lorimer k-factor or ζ-factor methods for electron-transparent thin-film specimens (~30–100 nm). The sample is thin enough that absorption and fluorescence corrections are minimal or zero; the signal model is fundamentally different.
- These two quantification frameworks share no meaningful overlap in method vocabulary, calibration approach, or correction hierarchy. Harmonization would produce meaninglessly broad controlled vocabulary.

**Tier differences that remain intentional:**
- EDS Detector Configuration: C=Advanced in EPMA (instrument infrastructure, rarely procedure-defining); C=Basic in TEM (detector geometry — SDD position, window type — is a primary procedure factor for thin-film EDS sensitivity).
- EDS Live Time per Point or Pixel: C=Basic in EPMA (per-point time is a core procedure decision for count statistics); C=Advanced in TEM (acquisition time is secondary to probe current and sample thickness in thin-film EDS; the procedure specifies approximate targets, not binding values).
- EDS Acquisition Mode: D=Read-Only in EPMA/SEM/SEM_Composition; D=Editable in TEM (added 2026-08-11). The
  divergence follows from the two families' different mode sets, not from drift. The EPMA/SEM description
  says the field specifies beam positioning *"within the declared Analytical Mode"*, and those TAPPs carry
  `EDS Point Analysis` and `EDS Mapping` mode flag columns — once the mode is declared the acquisition
  strategy follows from it, so the value is imported and fixed. TEM's modes are TEM Imaging / STEM Imaging
  / Electron Diffraction, which encode nothing about EDS acquisition strategy, leaving it a genuine
  per-session choice. Reconciling would make one family wrong.

**Future direction:** As the TAPP family grows to include SEM-EDS and dedicated EDS procedures, consider creating "EDS Acquisition" as a shared module (fields 1–8 above) that is referenced by technique-specific TAPPs, rather than duplicating field definitions. A formal "EDS (bulk)" TAPP (covering EPMA + SEM bulk EDS) and "EDS (thin film)" TAPP (covering TEM/STEM EDS) would enable the quantification fields to be developed properly for each domain without compromising the shared acquisition vocabulary.

---

### "Analytical Mode" as a mandatory Group 4 field — purpose, placement, and distinction from related fields

**Context:** During a cross-TAPP consistency review of SEM_Composition_TAPP_v3 and EPMA_TAPP_v6 (2026-06), it was noted that the two TAPPs treated mode declaration differently. SEM v3 had an "Analytical Mode" field in Group 4; EPMA v6 had "Beam Mode" but no "Analytical Mode". This triggered a broader decision about whether "Analytical Mode" should be universal.

**Decision:** "Analytical Mode" is a mandatory first field in Group 4 (Measurement Information) in every TAPP, regardless of whether the TAPP has one analytical mode or many. It is assigned C=Basic, D=Read-Only, and flagged Y for all modes.

**Reasoning:** The mode flag columns (Y/N per field) answer the question "does this field apply to mode X?" — they serve a filtering and applicability function consumed by the sub-TAPP generation script and by the formatted xlsx view. "Analytical Mode" answers a different question: "what kind of measurement does this procedure describe?" — it is a human-readable declaration consumed by anyone reading a registered procedure record. A procedure registrant must be able to state in one field what the procedure covers. The two structures are complementary, not redundant.

**Why C=Basic, D=Read-Only:**
C=Basic because the analytical mode is the most fundamental procedure-level declaration — omitting it makes the procedure record ambiguous. D=Read-Only because if the analyst changes the mode they are running a different procedure, not adjusting within procedure-defined bounds.

**Allowed values are drawn from the mode flag column labels of that TAPP:**
The controlled vocabulary for "Analytical Mode" must match the mode flag column labels defined in Phase 0. This ensures internal consistency — a procedure that declares "Analytical Mode = WDS Point Analysis" will have all WDS Point Analysis fields marked Y in the mode flag columns, and sub-TAPP generation will include it in a WDS-filtered view. If the mode flag labels change in a future revision, "Analytical Mode" allowed values must be updated to match.

**Distinction from mode-specific sub-strategy fields that coexist with "Analytical Mode":**
Several TAPPs have additional mode-related fields in Group 4 that are NOT replacements for "Analytical Mode":

| Field | TAPP(s) | What it captures |
|---|---|---|
| Beam Mode | EPMA, SEM | Physical beam configuration (focused / defocused / rastered) — independent of analytical mode |
| EDS Acquisition Mode | EPMA, SEM, TEM | Spatial acquisition sub-strategy within EDS (point / linescan / map) |
| Analytical Sub-mode | TEM | Specific technique within a top-level TEM mode (BF-TEM, HAADF-STEM, SAED, PED, etc.) |

These fields describe *how* the measurement is conducted within a declared mode, not *what mode* the procedure targets. All four can coexist in the same TAPP without conflict.

**Retrofitting to existing TAPPs (as of 2026-06):**
The following TAPPs had "Analytical Mode" added during the 2026-06 review:
- EPMA: added in v7
- SEM: already present in v3; retained in v4
- LA-Q:SF-ICP-MS: added in v2
- Lab-XCT: added in v8
- TEM: added in v7
- LA-ICP-MS: added in v12

**Generalization:** Whenever a new TAPP is created, place "Analytical Mode" as the first field in Group 4 with C=Basic, D=Read-Only, allowed values = mode flag column labels. For single-mode techniques, the allowed values list contains one entry and the field still must be present.

---

### Modules — why composition replaced copying, and what the specificity test caught

**Context:** A review of the LA-ICP-MS Geochronology TAPP (2026-08) found it used instrument columns
(Q / SF / MC-ICP-MS) where every other TAPP uses analytical mode columns. Testing whether mode columns
should be renamed "application" columns led instead to a three-layer module architecture, formalised as
Rule 6.

**Decision:** Shared field content is held in one module file and composed into consuming TAPPs by
script, not copied into each TAPP and kept in step by hand.

**Reasoning:** Rule 4's propagation obligation had already failed on live content. `Funding Source for
Procedure Development` was C=Basic in 3 of 13 TAPPs against a template value of Advanced — a Group 1
field, squarely inside Rule 4's scope — and nobody noticed until a scripted comparison was run. 14 of 17
Group 1 descriptions in LA-Q/SF-ICP-MS had diverged from the template, and the divergence ran in both
directions: some were stranded *improvements* that never flowed back. Composition converts a rule that
depends on discipline into a property that holds by construction.

**The specificity test is the load-bearing part.** "Recurs across techniques" is necessary but not
sufficient for module membership; the field must also not already exist in the library under another
name. Applying condition 2 changed the answer four times:

| Candidate | Failure | Resolution |
|---|---|---|
| 15 fields recurring across 6 dating systems | 9 also occur outside geochronology | module shrank to 5; the 9 became `ReportingCore` |
| `Age Model and Software` | software half collided with `Data Reduction Software` (Rule 1) | narrowed to `Age Model` |
| 9 "general gaps" | 3 already covered by existing descriptions, 1 was a name-harmonization | 6 new fields, not 9 |
| `Pb*/Pbc` as a U-Pb extension | Ar-Ar's `%40Ar*` is the same quantity | promoted to Layer 2 as `Radiogenic Fraction of Measured Signal` |

The last is the most instructive: only building a *second* system module revealed that a field in the
first had over-claimed specificity. Expect the third and fourth system modules to do the same.

**Generalization:** Before adding any shared field, search the library by concept as well as by name and
read what you find. The default assumption should be that a plausible new shared field is already
present under a different name, or is an instance of something more general.

**Column ownership as the usability answer:** A Layer 2 field can carry an abstract name
(`Calibration Factor and Determination Method`) provided the consuming system module owns Column F. An
Ar-Ar geochronologist reads "the J value — give the fluence monitor, its assumed age and reference";
a U-Pb geochronologist reads "the EARTHTIME tracer, calibrated per Condon et al. (2015)". Same field,
same tiers, one place to query. The abstraction is a maintenance artifact, never user-facing. Splitting
such a field per system would destroy exactly the cross-system queryability that motivates it.

**Placement constraint discovered in build:** a module contributing to Group 5 must insert *before*
`Constants and Reference Values Used`, not append after it, or Rule 5 breaks.

---

### Known unresolved tier divergences (recorded, not decided)

Rule 4 step 4 requires that intentional or unresolved divergence be recorded here rather than
silently left in place. These two surfaced on 2026-08-08 during the Rule 1 naming harmonisation and
are deliberately left open.

**`Analysis Sequence` — RESOLVED 2026-08-27 to C=Basic, D=Editable across all 9 TAPPs.**
See the entry at the end of this file. The three-way split recorded here on 2026-08-08 (C=Basic /
D=Editable in 5, C=Basic / D=Read-Only in the 3 Solution tables, C=Advanced / D=Editable in the 2
geochronology tables) had already lost its C dimension to later harmonisation; the D split was
settled by the shared Column B.

Absent from 7 TAPPs (EPMA, SEM x4, TEM, Lab-XCT), where the sequence of standards and unknowns is
less formalised. Whether those need the field is a separate question, still open.

**`Sample Persistent Identifier` — D split 14/3.**

C was resolved to Advanced across all 17 TAPPs on 2026-08-08, so a procedure may declare that it
expects samples to carry a persistent identifier — a meaningful standing commitment given Astromat,
EarthChem and SESAR. D was split: D=Advanced in 14, D=Basic in the three Solution ICP-MS TAPPs.
The question was whether supplying an IGSN at analysis time should be mandatory — a policy decision
about how hard to push registration, not a technical one, and it was left open rather than resolved
by majority.

> **CLOSED — verified 2026-08-24.** The field now reads C=Advanced, D=Advanced, `URI / IGSN`, keyed
> `sample` in **all 16 TAPPs**; the divergence no longer exists and `validate_tapp.py` reports no
> `tier-divergence` for it. The entry is kept for the reasoning, not as an open item. `Analysis
> Sequence` above is still genuinely split (6 D=Editable / 3 D=Read-Only across 9 TAPPs) and is
> still reported.

**Why these are recorded rather than fixed.** Both became visible only because the fields were
renamed to their canonical forms; before that they were the same field under two names, which no
check could detect. Renaming converts a hidden inconsistency into one `validate_tapp.py` reports as
`tier-divergence`. That is the intended end state for an undecided item: visible and tracked, not
resolved by whichever spelling happened to be more common.

---

#### 2026-08-11 audit — the remaining ten, and what they have in common

A full lint (`Project Files/Reports/TAPP_Lint_Report_2026-08-11.csv`) after the Rule 7 retrofit reports **15**
`tier-divergence` findings across the 16-TAPP library. Five are already accounted for: the two above,
`Mass Resolution Setting` (recorded in its own entry, and the only one that should *not* converge), and
`EDS Detector Configuration` and `EDS Live Time per Point or Pixel`, both recorded as intentional under
"EDS architecture" above.

**The ten remaining divergences split along development-cohort lines, not technique-need lines.** Nine of
the ten separate either LA/geochronology from Solution ICP-MS, or EPMA/SEM from TEM — the exact groups in
which those TAPPs were developed. That is the signature of drift-by-cohort, each family having absorbed
its own tier instincts, rather than ten independent design decisions. It is the same diagnosis this
section already reaches for `Analysis Sequence`.

**A. Cohort drift — RESOLVED 2026-08-11, reconciled to the LA family tiers**

| Field | Was | Now | TAPPs changed |
|---|---|---|---|
| `Analytical Accuracy and Assessment Method` | C=Advanced (Solution) vs C=Basic (LA) | **C=Basic** everywhere | Solution MC, Q, SF |
| `Within-Session Analytical Precision and Assessment Method` | C=Advanced (Solution) vs C=Basic (LA) | **C=Basic** everywhere | Solution Q, SF |
| `Guard Electrode` | C=Advanced (Solution) vs C=Basic (LA) | **C=Basic** everywhere | Solution MC, Q, SF |
| `Dwell Time per Mass` | D=Read-Only (Solution) vs D=Editable (LA) | **D=Editable** everywhere | Solution Q, SF |

Ten tier cells across the three Solution ICP-MS TAPPs. **Reconciled toward LA rather than toward the
majority**, because the LA assignment is the one with an argument behind it: accuracy and within-session
precision are at least as central to solution ICP-MS as to laser ablation — solution work is the reference
method for concentration — so there was no basis for them being mandatory in one family and optional in
the other. The direction of travel was drift, not design.

Two fields changed in only two of the three Solution TAPPs: Solution MC-ICP-MS has no
`Dwell Time per Mass` (a multi-collector does not dwell on masses) and records within-session
reproducibility under the differently-named `In-Run Isotope Ratio Reproducibility and Assessment Method`,
which was left untouched. Whether that field should follow the same reconciliation is a separate question,
since it is a different field, not a divergent one.

Scope: Solution MC v7→v8, Solution Q v9→v10, Solution SF v9→v10 — integer bumps, tier changes being a
major structural revision. `tier-divergence` findings fell 15 → 11.

**B. Plausibly intentional — a technique argument exists, but it was never written down**

| Field | Split | The argument |
|---|---|---|
| `Sample Preparation Method` | D=Read-Only in Solution ×3 + TEM; D=Editable in the other 11 | Preparation is procedure-fixed where it is chemical and destructive (digestion, FIB foil) and adjustable where it is a mount that can be repolished or recoated |
| `Per-Analyte Calibration Strategy` | C=Advanced in Solution MC only; C=Basic in 8 | In single-element isotope work there is effectively one analyte, so a per-analyte strategy barely applies |
| `Phase Identification Method` | Lab-XCT C=Advanced/D=Editable; TEM C=Basic/D=Read-Only | In XCT it is an analysis-time segmentation choice; in TEM it is a procedure-level commitment to a diffraction or EDS approach |

**C. RESOLVED 2026-08-11**

| Field | Was | Now | Basis |
|---|---|---|---|
| `Detection Limit Method` | C=Advanced in all 12; D=Basic in 9, D=Editable in 3 | **C=Basic, D=Read-Only** in all 12 | C=Basic follows the `Uncertainty Level` precedent — a reported detection limit is not interpretable without knowing whether it is 3σ of background, Longerich et al. 1996, or 10× blank SD. D=Read-Only is what the field's own description already asserts: *"Must be consistent with the method applied to generate the Detection Limit values reported above."* Produces the Oxide Production pattern — method procedure-fixed, values a session outcome (`Detection Limit` stays C=Advanced/D=Basic) |
| `Step Size / Pixel Size` | EPMA C=Basic/D=Editable; SEM, SEM_Composition C=Advanced/D=Basic | **C=Basic, D=Editable** in all 3 | Reconciled to EPMA, which was already compliant with the existing precedent "Analysis-level only fields (C=N/A) for spatially determined mapping parameters". That entry rules step size C=Basic/D=Editable because it controls intrinsic spatial *resolution* — a procedure design choice — as opposed to map extent, which is dictated by the feature chosen at analysis time and is C=N/A |
| `EDS Acquisition Mode` | — | **unchanged** | Reclassified as intentional; recorded under "EDS architecture" above |

14 tier cells across 12 TAPPs. `tier-divergence` findings fell 11 → 9.

**Recorded, not decided — category B only.** Tier assignments are the library owner's call; the Rule 4
obligation discharged for those three is visibility. Categories A and C were both reconciled on
2026-08-11 (above), taking the library from 15 `tier-divergence` findings to 9 — of which 6 are now
recorded as intentional and 3 remain open by choice.


---

### `Technique` added to the controlled-list exemption table (2026-08-10)

**Decision.** `Technique` is exempt from the requirement that every `Controlled list` field offer
`N/A | None | Other: specify`. The exemption table in `conventions.md` — previously closed with a
single entry, `Analytical Mode` — now has two.

**Reasoning.** It is the same argument that exempted `Analytical Mode`, reached independently. The
field is the TAPP's own top-level technique identifier, drawn from the cross-TAPP technique
vocabulary under Rule 1. `N/A` and `None` are not merely unnecessary but semantically empty: every
procedure has a technique, and a procedure record declaring `Technique = None` would be malformed
rather than informative.

The three Solution ICP-MS TAPPs make the case concretely. Their Column F is a single value —
`Solution Q-ICP-MS`, `Solution SF-ICP-MS`, `Solution MC-ICP-MS` — a closed enumeration of one. There
is nothing an `N/A` option could usefully express there.

**What this does not extend to.** The exemption is for `Technique` itself, not for
`Coupled Technique(s)`, where `None` is meaningful and load-bearing: it is how a procedure records
that no coupling is intended, and the Group 1 standard depends on that value. Nor does it extend to
`Analytical Sub-mode`, `EDS Acquisition Mode` or `Beam Mode`, which the `Analytical Mode` entry
already excludes.

**Still open, and adjacent.** `Collision/Reaction Cell (CRC) Configuration` is arguably in the same
class. After its `Not applicable (SF-ICP-MS)` option was generalised to `N/A` on 2026-08-10, the
check still reports `None` as missing — but "no collision/reaction cell in use" is already
`STD (standard mode, no gas)` and "the instrument has no cell" is now `N/A`, so `None` would add a
third spelling of something already expressible. Not decided; it needs the same explicit call this
entry records for `Technique`.

**Scope of effect.** Clears 6 findings (`Technique` in LA-Q/SF v5 and its U-Pb variant, Lab-XCT v10,
and the three Solution TAPPs). No TAPP content changed — the exemption is a checker and convention
change only.

---

### Uncertainty Level split from Uncertainty Propagation Method (2026-08-10)

**Decision.** `Uncertainty Level and Propagation` is split into two fields across all 7 TAPPs that
carried it:

| Field | C | D | Data Type |
|---|---|---|---|
| `Uncertainty Level` | Basic | Read-Only | `Controlled list / Text` |
| `Uncertainty Propagation Method` | Advanced | Editable | `Text (free)` |

**This narrows the earlier precedent rather than reversing it.** The "Advanced/Editable" entry was
written when the field was named `Uncertainty Propagation Method` — propagation only — and its
argument is entirely about the propagation framework: many labs use informal uncertainty estimates
without a formally specified framework, so mandating one at Basic would exclude legitimate procedures
or generate boilerplate. That argument is sound and is preserved untouched on the propagation half,
which takes its original name back so the precedent applies to it by name again.

What the precedent never covered is the **level**. That concept was merged in by the 2026-08-08
rename to `Uncertainty Level and Propagation` and inherited C=Advanced by accident of packaging
rather than by argument. Nothing was ever written to justify treating the level as optional.

**Why the level is Basic.** `analysis/Test5_Geochronology_Module_CrossSystem.csv` row 3 records
"Uncertainty Level Convention" as REQUIRED in **6 of 6** independent community dating standards, with
recommended tiers C=Basic / D=Read-Only, and its status as "PARTIAL — folded into geochron
Uncertainty Level and Propagation". Unlike a propagation framework, there is no informal case to
exclude: every lab that reports an uncertainty quotes it at some level, and a value whose level is
unstated is not interpretable. The old description said as much itself — *"A reported uncertainty is
not interpretable without both halves"* — which is a description admitting it holds two fields.

**Why D=Read-Only does not hit the void-import trap.** The earlier entry's generalisation — that an
Advanced procedure-level field should almost never be Read-Only at analysis level, because Read-Only
imports a value that may be void — applies specifically when C=Advanced. A C=Basic field always
carries a procedure value for the analysis to inherit, and the level is a standing lab convention
rather than a session decision, so Read-Only is correct.

**Generalisation.** When a field's name contains "and", check whether the two halves warrant the same
tier. This one merged a component mandated by six community standards with a component deliberately
left optional, and the merge silently demoted the mandatory half to optional. A compound field name
is a reasonable place to look for a mis-tiered requirement.

**Scope.** 7 TAPPs, all integer-bumped because adding a field is a major structural revision:
LA-Q/SF v5→v6 (+U-Pb), LA-MC v2→v3, LA-MC U-Pb v1→v2, Solution Q v7→v8, Solution SF v7→v8,
Solution MC v5→v6. The field is in no module — at 2 fields it is below Rule 6.10's five-field
extraction threshold — so this was Rule 4 propagation.

**Literature assessment cells on the new field were left empty.** Existing extractions remain on the
propagation row where they were made. Several visibly contain level information ("2SE of individual
spot measurements reported"), so a Phase 3 re-pass could populate the new row, but copying them
wholesale would fabricate extraction never performed against this field.

---

### `Mass Resolution Setting` — D=Read-Only in LA-Q-ICP-MS, D=Editable everywhere else (2026-08-11)

**Decision:** an intentional cross-TAPP tier divergence, recorded here because `validate_tapp.py`
reports it as `tier-divergence` INFO and Rule 2/4 requires intentional divergences to be documented.

| TAPP | C | D |
|---|---|---|
| LA-Q-ICP-MS, LA-Q-ICP-MS U-Pb | Basic | **Read-Only** |
| LA-SF-ICP-MS, LA-SF-ICP-MS U-Pb, LA-MC-ICP-MS (+U-Pb) | Basic | Editable |
| Solution Q / SF / MC-ICP-MS | Basic | Read-Only |

**Reasoning.** On a quadrupole, mass resolution is fixed at unit resolution by instrument design — the
analyst cannot adjust it, so D=Editable would assert a session-tunable parameter that does not exist. On
a sector-field instrument the analyst genuinely selects low, medium or high resolution per session, which
is D=Editable by definition.

**Origin.** The divergence became visible only when the combined LA-Q/SF-ICP-MS TAPP was split on
2026-08-11. Before the split, one row had to serve both instruments and its Column F carried both answers
at once — *"Unit resolution — quadrupole (fixed) | Low resolution — SF (~300 m/Δm) …"* — with D=Editable,
which was correct for SF and wrong for Q. The field is the clearest single argument for having made the
split: a combined TAPP cannot carry two different tier assignments for one row.

**Not a candidate for reconciliation.** Unlike the divergences recorded under "Known unresolved tier
divergences", this one should not converge. The two values describe two different instruments and both
are correct.


---

### Technique-dependent key register (Rule 7.8.7) — the five entries and why

A field name normally carries the same `Keyed By` in every TAPP. These five are the ones where the
technique genuinely makes it differ. The register is a first-class list, not an escape hatch: uniformity
is the default because a field name that means one shape here and another shape there is invisible to a
curator — the same argument Rule 6.4 makes about descriptions.

**The default is justified empirically.** Of 252 field names appearing in more than one TAPP, **only 3
carry a differing key — 98.8% are already uniform.** The cross-TAPP check therefore costs almost nothing
and catches drift at the moment it is introduced, rather than at the next audit. The alternative
considered and rejected on 2026-08-11 was to make keys freely per-TAPP; that would have rebuilt, in a new
column, exactly the problem the tier-divergence audit had spent the same day untangling — 15 divergences
of which 6 were intentional and 9 were drift, and none recorded at the time it was introduced.

| Field | Keys | Why the technique makes it differ |
|---|---|---|
| ~~`Detection Limit`~~ | **Left the register 2026-08-12** — now `reported property` in all 12 | The rationale was *"laser ablation yields a detection limit per spot, because each spot has its own background"*. True of the **computation** and false of the **reporting**: see the literature-audit entry below. The field is now uniform and needs no entry |
| `Primary Calibration Standard Name` | `analyte` in EPMA/SEM/SEM_Composition **and LA-SF**; `(none)` in LA-Q, LA-MC and the 3 Solution TAPPs | In WDS each analyte has its own calibration standard (albite for Na, Kakanui kaersutite for Si/Al/Ti) — confirmed by 11 of 15 EPMA extractions. LA-SF added 2026-08-12: Navarro et al. 2024 assigns standards to analyte groups (*"North Chile Filomena for Fe/Co/Ni/Cu/Ga/Ge/As/W/Au; Hoba for Ru/Rh/Pd/Re/Os/Ir/Pt"*). LA-Q and Solution are unanimously a single primary or one joint calibration set. The old rationale claimed *"reported property in isotope work"*, which no TAPP ever carried |
| `Secondary Reference Materials` | `defines: standard per analyte` in EPMA/SEM/SEM_Composition; `defines: standard` in the 9 isotope TAPPs | Added 2026-08-12. The electron-beam descriptions ask for *"assessed elements"* per RM; the 16 LA-SF/Solution extractions are plain RM lists (*"BCR-2, AGV-2, JB-2, BR, JB-3"*) with no per-analyte breakdown |
| `Dwell Time per Pixel` | `analyte` in EPMA/SEM/SEM_Composition; `(none)` in SEM_FIBSEM/SEM_Imaging | Per element during compositional mapping; a single scan parameter in imaging-only procedures |
| `Beam Current` | `sampling unit` in EPMA/SEM/SEM_Composition; `(none)` in SEM_FIBSEM/SEM_Imaging | Added 2026-08-11 — see below |
| `Monitored Isotopes` | `defines: channel per analyte` in LA-Q, LA-SF (+U-Pb), Solution Q, Solution SF; `analyte` in LA-MC-ICP-MS (+U-Pb) | Where a collector array exists, the cup is the channel and `Collector Configuration` is the definer (7.4b), leaving `Monitored Isotopes` keyed by analyte. Single-collector instruments have no cup array, so it is itself the definer — and it enumerates masses *per analyte element*, which is what the 7.3.1 form added 2026-08-12 records. **Amended 2026-08-12:** that demotion had a side effect nobody noticed — it dropped the channel↔analyte binding in the three multicollector TAPPs, since `Collector Configuration` was plain `defines: channel`. Fixed by moving the binding onto the definer that survives: `Collector Configuration` is now `defines: channel per analyte` (Module_MCICPMS v5). All 13 TAPPs declaring both domains now carry an explicit binding |

**`Beam Current` — the evidence, because the obvious answers were both wrong.** It was first keyed
`acquisition pass` on the reasoning that EPMA runs Na/K at low current and major elements at high. The
field's own description says *"Often varies by phase type or analyte"*, and the extracted literature
settles which dominates: three of five papers report a scalar (`5 nA`, `10 nA`), and the two that vary do
so **by phase** — Liu et al. 2016, both instruments: *"20 nA (olivine, pyroxene, Fe-Ti-Cr oxides); 10 nA
(maskelynite…)"*. No extraction reports a per-analyte current. Hence `sampling unit`, phase being a
sampling unit under 7.2, with `Sampling Unit` (Rule 9) already present in every TAPP as its definer.

The per-analyte case remains real and is documented in the field description. It was not adopted as the
key because the evidence does not support it as the dominant pattern, and `sampling unit x analyte` was
rejected as over-modelling — it would force a two-dimensional table on the majority of procedures that
need one number.

**Retiring `acquisition pass` followed.** Once `Beam Current` moved, its only remaining user was
`Multi-Run Sequential Analysis Design`, which would have had to be its own definer — a violation of 7.4c.
The key is documented in 7.2 but unused.

---

### The analyte / reported-property isomorphism for concentration-reporting procedures (2026-08-12)

**Decision: where a procedure reports one concentration per analyte, the `analyte` and `reported
property` domains are isomorphic, and `reported property` is the key to declare.**

The 2026-08-12 Column B survey found `Detection Limit` naming a different key in its description than in
Column I in **all 12 TAPPs that carry it** — prose saying *"detection limits for each analyte"* against
`Keyed By = reported property`, and in the LA variants *"for each measured isotope … per isotope or element
group"* against `sampling unit x reported property`. The mismatch is conspicuous because Rule 7.3 uses this
very field as its worked example of the defines/keyed-by distinction.

The prose was not wrong so much as naming the other side of an identity nobody had written down. A
procedure reporting Fe, Mg and Ca concentrations reports exactly three concentration variables; the set of
analytes and the set of reported properties have the same members, so "one per analyte" and "one per
reported property" describe the same table. **The declaration takes `reported property`** for two reasons:

1. **It is the universal anchor.** `reported property` exists in every TAPP by Rule 8, `analyte` does not
   exist at all in Lab-XCT, Raman or fission track (7.2 — `analyte` is chemistry only). A key valid
   everywhere beats a key valid in the chemical subset, and it keeps one field name from needing a register
   entry it does not otherwise need.
2. **It survives the derived case.** When the procedure reports δ⁵⁶Fe rather than an Fe concentration, the
   isomorphism breaks: one analyte, several reported properties. `reported property` stays correct;
   `analyte` silently under-counts. Declaring the domain that does not collapse is the safer default.

Descriptions were aligned to say *"one per reported concentration variable (one per analyte, these being
the same set)"* — naming the declared key while keeping the analyst-facing language, since "per analyte" is
how the community reads a detection-limit table.

**Generalize this before reaching for `analyte`.** The same isomorphism holds for `Detection Limit Method`
and plausibly for other per-element reporting fields. Where it holds, prefer `reported property`; the
question to ask is whether the procedure could ever report more than one quantity per analyte, and if it
could, `analyte` was never the right key.

**Not settled by this entry:** the LA `Detection Limit` prose says *"Session detection limit"* while its key
declared `sampling unit` (per spot), which the register rationale also stated. That is a factual question
about what the LA procedures report, not a vocabulary question.

> **SETTLED by the attested-axis rule in the very next entry (2026-08-12), confirmed 2026-08-24.** The
> LA variant lost `sampling unit` and the field is `reported property` in all 12 TAPPs that carry it;
> `Detection Limit` left `KEYED_BY_TECHNIQUE_DEPENDENT` on the same date. The prose and the key now
> agree. **Its Column E did not follow** — the Data Type is still split three ways, which is
> `amds-ldeo/tapp#1` and is tracked in `COLE_DIVERGENCE_TRIAGED` as OPEN (conventions.md 7.8.10).

---

### Validating keys against the literature assessment — the attested-axis rule (2026-08-12)

**Decision: a field's `Keyed By` is the finest axis ATTESTED IN REPORTED DATA — not an axis that is
merely computed during data reduction, and not one that is only conceptually possible.**

This rule came out of auditing all 16 TAPPs' Column I against their literature assessment columns
(231 extraction columns, ~17,000 filled cells, 14 TAPPs with Phase 3 coverage). Evidence and audit
in `analysis/Audit_ColI_vs_LitAssess.csv`. It is stated as a precedent because it decides
cases in **both** directions, and the two halves look contradictory until the rule is named:

- **`Beam Current` keeps `sampling unit`.** 10 of 13 extractions are a bare scalar (`5 nA`,
  `10 nA`) — but 2 publish per-phase values: *"20 nA (olivine, pyroxene, Fe-Ti-Cr oxides); 10 nA
  (maskelynite, phosphate, sulfide, glass)"*. The axis reaches the reader, so a consumer must be
  able to hold it, and the scalar case is that axis with one member.
- **`Detection Limit` loses `sampling unit`.** Every LA paper that reports LODs reports one per
  element for the session. Navarro et al. 2024 states the per-spot case as strongly as it can be
  stated — *"as the amount of material ablated in LA sampling is often significantly different for
  each analysis, the LOD must be calculated for each acquisition"* — and then reports *"the median
  values obtained for each element"*. Chernonozhkin et al. 2021 appendix C5: the LOD *"can be
  calculated for each individual analysis or for each string of pixels"*, and the tabulated values
  *"are the average of all LODs"*. The per-spot LOD never surfaces as a reported row; it surfaces
  as a `<LOD` censoring flag on an individual concentration, which is a property of that
  concentration, not a value of this field.

**Why "attested in reported data" and not "computed":** Column I tells a consumer how many values to
expect in the metadata record. An axis that exists only inside the data-reduction software produces
no rows to hold. Declaring it builds a two-dimensional child table that every submitter fills with
one row — the same over-modelling that `sampling unit x analyte` was rejected for on `Beam Current`.

**Generalization — how to run this validation on any TAPP with Phase 3 coverage.** For each keyed
field, read across the literature assessment columns and ask what shape the extractions take. Then:

| Observed across extractions | Declared | Action |
|---|---|---|
| All scalar, no procedure attests the axis | keyed | Drop the axis |
| Any procedure publishes per-X values | `(none)` | Add X |
| Enumerates axis B, key names axis A | A | Re-key to B, or record why both |
| A bare list of types, no values per member | `(none)` | Correct — a list is not a key (7.4c) |

**Two traps, both hit during this audit.** They are recorded because both produced confident,
wrong findings:

1. **Schedule language is not cardinality.** *"Gas blank measured before each ablation"* and
   *"LOD calculated per analysis"* describe **when** something happens, not how many values the
   field holds. `Blank / Background Correction Method` was flagged on 22 extractions and is
   correctly `(none)` — it holds one method.
2. **Check the raw extraction, not the aggregated verdict.** `Analytical Accuracy and Assessment
   Method` was scored OVER-DECLARED and proposed for demotion from `standard x reported property`.
   The raw cells refute it: *"% deviation from published Pb isotope values for geological RMs
   (BCR-2, AGV-2, JB-2, BR, JB-3)"*. A detector requiring two *named* reference materials in one
   cell scored *"USGS/GSJ RMs"* as scalar. The change was dropped — and had it been applied, it
   would have removed the last consumer of `standard` in Solution Q/SF and orphaned
   `Secondary Reference Materials` as a definer under 7.4c.

**Coverage limit, so absence of evidence is not read as evidence.** `SEM_Composition` and `SEM` carry
35 literature columns in which `Primary Calibration Standard Name` is `N/A` on all of them, because
SEM-EDS is normally standardless; their `analyte` key is inherited from EPMA and is untested rather
than contradicted. `LA-MC-ICPMS_UPb` and `Solution MC-ICP-MS` have no literature assessment columns
at all, so no key in them has been validated this way.

---

### The analysis record is the session, and `sample` becomes a key (2026-08-12)

**Decision: an analysis record corresponds to one execution of a procedure — a session — which may
cover many samples. `sample` enters the key vocabulary as an anchor.** Decreed as Rule 13; the full
record with alternatives is `analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md`.

**Reasoning.** The framework previously defined the analysis as *"what actually happened in a given
session, on a given sample, on a given date"*, asserting both readings at once. Real sessions cover
many samples, each with its own IGSN and possibly its own preparation history.

Group 1 was **already session-shaped** in every TAPP — `Analyst`, `Analysis Start Date`,
`Analysis End Date`, all C=N/A, D=Basic. A start *and* end date describes a session, not a specimen,
and `Within-Session` / `Between-Session` precision fields already existed in the QC groups. Group 1
treated the record as a session while Group 2 treated it as one sample; this resolves that
contradiction in favour of the session.

**The decisive consequence is Rule 10.1, not tidiness.** A shared session calibration correlates
samples. With no session object the correlation could not be stated at all.

**`Keyed By` carries the level distinction for free** — `(none)` is per session, `sample` per sample,
`sample > sampling unit` per spot within a sample. No new column. This is the same argument Rule 7
made against `Analyte-Specific`: one label was concealing four keys, and "analysis-level" was
concealing two levels.

**Alternative rejected: keep analysis = one sample, add a `Session Identifier` only.** Cheaper —
zero Column I churn — and it recovers the error-correlation link. Rejected because the redundancy is
not the real cost: that option leaves "analysis-level" permanently unable to say whether a field is
per-session or per-sample, which is the exact defect Rule 7 exists to cure.

**An argument used against the `sample` key, and why it was wrong.** It was first claimed that a
`sample` key cannot satisfy 7.4a because no procedure can enumerate its future samples. That is
overstated: `Sampling Unit` already demonstrates the pattern — declare the *type* at procedure
level, the *instances* at analysis level — and `Sample Name` now does the same. The SESAR argument
also narrows on inspection: it argues against re-modelling the IGSN parent–child hierarchy, not
against recording which samples a session covered, which is a many-to-many link SESAR does not hold.

**`sample` and `standard` are overlapping domains, not disjoint ones.** `standard` names a *role*,
not a class of material. Secondary reference materials are run through the same calibration as
unknowns and evaluated against accepted values; many are SESAR-registered with their own IGSNs;
round-robin materials are unknowns to the analyst and standards to the organiser. The keys stay
separate because they key different fields — `standard` keys anchoring and QC, `sample` keys identity
and preparation — but a secondary RM legitimately appears in **both** domains within one session and
that is not double counting. **Stated because a consumer will get it wrong silently:** a schema
asserting disjointness between samples and standards will be violated by ordinary sessions. Primary
calibration standards are the exception — their values are inputs, not results.

**Preparation attaches to the sample, not the session.** A digestion batch of twenty can split across
two runs; one run can draw on three batches. So `preparation batch` and `measurement session` are
orthogonal groupings and preparation cannot hang off the session. No new key: the existing
`preparation step` rows are unchanged, and only genuinely per-sample quantities move to `sample`.

**Not settled by this entry:** whether an intermediate *batch* object is eventually needed;
the residue of the Group 2 per-sample audit (`Isotope Dilution Spike`,
`Fusion Flux and Dilution Ratio`, `Pre-Ablation Surface Treatment`, `Sample Preparation Method`),
which needs a literature pass; and whether the repository mints a session PID alongside the
laboratory run identifier, which is an infrastructure decision.

---

### `analyte` is the chemical species, never the isotope (2026-08-12)

**Decision: `analyte` is the chemical entity a procedure sets out to determine, at whatever
resolution the chemistry is resolved. An isotope is never an analyte — unconditionally.**

Rule 7.2's wording was already correct and is unchanged; eight `Analyte` descriptions that
contradicted it — six saying *"Isotopes (mass/charge)"*, two saying *"Elements or isotopes"* — were
corrected, and all 13 were reframed around a shared opening sentence.

**Two boundary tests, both already in the library.** Against `channel`: would substituting a
different isotope, line or address for the same entity leave the target of determination unchanged?
Yes → `channel`. Against `reported property`: could the procedure ever report more than one quantity
per analyte? Yes → `reported property` was always the right key (the isomorphism precedent above).

**The obvious argument against isotope-as-analyte does not work, and is recorded so it is not
re-run.** It is tempting to say the isotope domain merely duplicates `channel` or `reported
property`. That proves too much: element-as-analyte duplicates the reported-property list in *every*
concentration-reporting procedure, and the library kept the field anyway. Duplication was never the
disqualifier. Nor is the isotope domain simply `channel` renamed — Misra et al. 2014 acquires ⁴³Ca in
both LR and MR, so it is genuinely coarser than `channel` and finer than `analyte`.

**The two reasons that do hold.** (1) **7.4c — no consumer.** Every isotope-flavoured field in the
library is scalar: `Double-Spike Isotope Pair`, `Internal Normalization Element and Isotope Ratio`,
`Mass Fractionation Law`, `Isotope Dilution Spike`, `Internal Standard Element`. Nothing needs "one
value per isotope, shared across the channels of that isotope" — the same test that retired
`conversion` and `acquisition pass`. (2) **Technique-neutrality.** Fe is Fe by EPMA, ICP-MS, XRF or
INAA; ⁵⁶Fe exists only inside a mass spectrometer. A registry that matches procedures across
techniques needs the axis that survives a change of instrument.

**Why the asymmetry with valence is not arbitrary.** Isotopes of an element *are the same chemical
species* — same separation chemistry, calibration standard, crystallographic site, chromatographic
behaviour, elemental interferences. Valence states are not, and neither are compounds. Isotopes are
the only axis on which measurement granularity is finer than chemical granularity, which is why that
one case reads as an imposed grouping while valence and compounds feel natural. Test for a
submitting researcher: *would a chemist call these different substances?*

**Allowed content.** The axis is chemical identity and is **not ordered relative to the element**:
finer (Fe²⁺, Fe³⁺ — XANES, Mössbauer), at element level (Si, Fe, Rb, Sr), a chemically defined
fraction of an element (organic carbon), or orthogonal to elements (n-C₂₉ alkane; C₁₈H₂₀O₈).
Never allowed, because the distinction is not chemical: masses and acquisition addresses (→
`channel`), reported quantities (→ `reported property`), internal standards / interference monitors /
carriers (→ `channel`), and the same species in a different environment — Fe²⁺ on M1 vs M2, high- vs
low-spin (→ `model component`). **Fe²⁺ and Fe³⁺ are different analytes; Fe²⁺-on-M1 and Fe²⁺-on-M2
are not.** One granularity per TAPP, declared in Phase 0 under 7.7.

**Worked case.** A procedure measuring Rb and Sr isotopes and reporting isotope concentrations,
isotope ratios, elemental concentrations and elemental ratios: `Analyte` = **Rb, Sr** — two entries.
All four output kinds are reported properties; they differ in what is reported *about* Rb and Sr, not
in what was determined.

**Three merge proposals rejected.** `monitored species` collapses into `channel` and evicts its most
useful members — interference monitors and internal standards, which are monitored and never
determined. A generalised `analyte` covering physical-property sweeps does the same; Lab-XCT at 92%
scalar shows those techniques have no determinand layer, because determinand and reported property
coincide there. `Target Elements` cannot hold a molecule, a valence species or a nuclide.

**Analyte is not the discovery axis, and its description should not claim to be.** A sentence
promising that `Analyte` "enables matching of procedures to analytical needs" was added and then
removed: [Fe] by LA-Q-ICP-MS and δ⁵⁶Fe by LA-MC-ICP-MS both carry `Analyte = Fe`, and only
`Reported Variables and Units` separates them. **The field exists because the key exists** — 44
fields declare `Keyed By = analyte` and become uninterpretable without a definer (7.4a). If procedure
discovery is a requirement, the fix is a controlled vocabulary on `Reported Variables and Units`,
which is `Text (free)` today; leaning on `Analyte` will not deliver it.

**Not settled by this entry:** phase identity in XRD, which has a claim from `analyte`,
`model component` and `reported property` at once; orientation as an axis (AMS, velocity anisotropy),
which fits neither `channel` nor `sampling unit` cleanly; and the matrix-element grey zone — an
element fully calibrated but never reported.

---

### `channel` is real in the electron-beam TAPPs — the multi-spectrometer evidence (2026-08-12)

**Decision: EPMA, SEM and SEM_Composition gain the `channel` key. `WDS Spectrometer Channel` becomes
`defines: channel per analyte`; nine WDS setup fields move from `analyte` to `channel`; eight
determinand-level fields stay `analyte`.**

Those three TAPPs previously carried 54 of the library's 80 `analyte` rows and **zero** `channel`
rows, while Rule 7.2's own worked example of a channel was *"Fe Kα on LIF spectrometer 2"*. The
question was whether the spectrometer assignment is a genuine second axis or collapses one-to-one
onto the analyte.

**Evidence.** Jia et al. 2022 (JAAS 37, 2351) Table 4 is a per-element WDS setup table carrying
eleven of the eighteen fields, and measures **Cr on two spectrometers with aggregate intensity
counting**. Its spectrometer/analyte map is many-to-many in both directions: Sp2 carries Ti, Mn, Cr,
V; Sp3 carries Fe, Co, Ni; Sp4 carries Sc, Zr, Nb. Batanova et al. 2018 (IOP Conf. Ser. 304, 012001)
records multi-spectrometer intensity integration among the measures used in many laboratories, and
separately compares Ti-Kα on L-type versus H-type spectrometers.

**Result: EPMA now has the same structure as single-collector ICP-MS**, with `WDS Spectrometer
Channel` playing the role `Monitored Isotopes` plays, and 7.3.1's `defines: A per B` form has users
in both technique families rather than only in mass spectrometry.

**Method note, recorded because it nearly produced a false negative.** The 14 pre-existing EPMA
literature columns record `N` — not stated — for `WDS Spectrometer Channel` in **14 of 14**
procedures. That is not evidence of absence: all 14 are meteoritics and mineralogy application
papers, which do not publish the setup table, whereas method papers do. **When a key question turns
on a parameter table, confirm the corpus contains method papers before reading a null result as
evidence.**

---

### `Mass Resolution Assignment` — one analyte, two resolution channels (2026-08-12)

**Decision: `Mass Resolution per Analyte` is renamed `Mass Resolution Assignment` and re-keyed from
`analyte` to `channel` in all five TAPPs carrying it.**

**Evidence.** Of six Solution SF-ICP-MS extractions, three assign resolution per element (Willbold
2005, Milne et al. 2010, Lu et al. 2007) — but **Misra et al. 2014 lists ⁴³Ca in both the LR and the
MR set**, because Ca is the denominator of every reported ratio and must be measured in each
resolution pass. One analyte, two acquisition channels.

**Reasoning.** Three of six being element-level is not decisive; one being non-collapsing is. This is
the isomorphism precedent's own logic run in reverse — *declare the domain that does not collapse*. A
key that cannot represent Misra's table forces data loss; a key finer than needed yields 1:1 tables
elsewhere, which is harmless. The field was renamed because its name asserted the key the evidence
disproved, and the cross-reference in `Mass Resolution Setting` was updated with it.

**Side finding, not acted on:** all seven LA-SF extractions record `N` for this field — those
procedures use a single resolution throughout, so it may not belong in the LA TAPPs at all.

---

### `defines: A per B` — the parent key is optional per row (2026-08-12)

**Decision: the `per B` half of `defines: A per B` means "where a B exists", not "for every row".
7.3.1's gloss is amended; the notation is unchanged and no Column I value moves.**

**The defect.** 7.3.1 introduced the form saying `Monitored Isotopes` *"lists them per analyte
element, one row per element"*, which asserts a total function from channel to analyte. Desem et al.
2022 records `202Hg, 203Tl, 204Pb, 205Tl, 206Pb, 207Pb, 208Pb` for a procedure whose analyte is **Pb
alone** — ²⁰²Hg is the interference monitor for ²⁰⁴Pb, ²⁰³Tl/²⁰⁵Tl the internal standard. Makishima
et al. 2011 (¹⁴⁹Sm) and Lu et al. 2007 (⁹³Nb) are the same shape. Orphan members are normal:
interference monitors, internal standards, carriers, and any spectrometer assignment used for a
standard-only or background-only measurement.

**Alternatives considered.** (a) Drop to plain `defines: channel`, carrying the analyte grouping as a
nullable attribute of the channel table — closest to a relational model and what a schema generator
would write by hand, but it removes the binding from Column I, which is the one place a curator sees
it, and the binding is exactly what the schema developers flagged as *"real and unrepresented"*.
(c) Split monitor masses into a separate field — rejected outright: the run table is one list, and
splitting it would make interference assessment read across two fields. (b) was taken.

**Reasoning.** The cost of (b) is that a consumer must be *told* the parent is optional, which is one
line of documentation; the cost of (a) is a permanent loss of expressiveness in the column the rules
are read from. Whether a parent is total or partial varies by field and the notation does not
distinguish — `EELS Edges` is total, `Monitored Isotopes` is partial, both written
`defines: channel per analyte` — so the safe reading is "assume partial", and that reading is correct
for both.

**The failure this guards against, stated because it is silent.** The analyte list is authoritative
and comes from the `defines: analyte` field. It must never be inferred from the element symbols
appearing in the channel list: parsing `202Hg` to "Hg" and adding Hg to the analytes would record a
determinand the procedure never determined. The child table takes a **nullable** foreign key, and
orphan rows are kept, not dropped — they are part of the run table and are needed to assess the
interference corrections.

**7.4a is unaffected:** `defines: A per B` still requires a `defines: B` field, because the rows that
do carry a parent need a domain to point into.

**A marked form (`defines: A per B?`) was considered and rejected** — it would distinguish total from
partial, but no field needs the distinction enforced and the safe reading covers both. Same standard
7.3.1 set for declining the compound key, and 7.4a–c for retiring abstractions with no user. Mark it
when a consumer needs to rely on a parent being total.

**Applies to all four fields using the form:** `Monitored Isotopes` (partial), `WDS Spectrometer
Channel` (total today, partial the moment a spectrometer serves a standard-only measurement),
`EELS Edges` (total), `Secondary Reference Materials` (`defines: standard per analyte`).
The eight `Monitored Isotopes` descriptions were rewritten in step to say so in the place a curator
reads.

---

### The A4 per-sample audit — four fields tested, none re-keyed (2026-08-12)

**Decision: `Isotope Dilution Spike`, `Fusion Flux and Dilution Ratio`,
`Pre-Ablation Surface Treatment` and `Sample Preparation Method` stay `(none)`. Only
`Sample Aliquot Mass or Volume` is confirmed as `sample`.**

Rule 13 made `sample` a live key, raising the question of which Group 2 fields vary per sample within
a session. Four were marked *verify* and tested against the literature assessment columns.

| Field | Evidence | Verdict |
|---|---|---|
| `Sample Aliquot Mass or Volume` | Makishima et al. 2011 states **15–63 mg (silicates); 8–22 mg (NIST glass); 9–28 mg (chondrites)** — a range varying by sample *within one procedure*. Misra et al. 2014: 1–2 mg per shell sample | **`sample` — confirmed** |
| `Isotope Dilution Spike` | 11 extractions. Every one names a single spike *material* for the procedure (¹⁴⁹Sm; ⁵⁷Fe/⁶²Ni/⁶⁵Cu/⁶⁸Zn/¹¹¹Cd/²⁰⁷Pb; a multi-element spike). The field records the material, not the amount added | `(none)` |
| `Fusion Flux and Dilution Ratio` | 14 extractions, **13 of them N/A**. The one fusion procedure states one ratio (Li₂B₄O₇, 1:35) for the whole procedure | `(none)` |
| `Pre-Ablation Surface Treatment` | 14 extractions. Stated in 2, and in both cases once for the procedure | `(none)` |
| `Sample Preparation Method` | One near-miss: Seifert et al. 2026 records *"Fragments embedded in epoxy; dry-polished…; **one mount ion-polished** before carbon coating"* — genuine per-sample variation, but carried inline in free text | `(none)` |

**The discriminator, recorded because it is easy to misread.** Several papers appear at first glance
to show per-sample variation: Zega et al. 2025 prepares Bennu material five different ways;
Chernonozhkin et al. 2021 applies a pre-ablation pass to its trace-element run but not its mapping
run; Navarro et al. 2024 etches the *same* fragment with Nital for a second run. **In every case the
variation is across literature assessment columns, and a column is one procedure, not one sample.**
Variation across columns is exactly what separate procedure records already express; it says nothing
about whether a field repeats within a procedure. Only variation *inside a single cell* — Makishima's
three mass ranges — attests a per-sample key.

**Why `Sample Preparation Method` stays `(none)` despite a real instance.** A4 qualified it as
`sample` *"where a session mixes preparation routes"*, and Seifert's ion-polished mount is such a
mix. It stays scalar because a free-text field can carry "route X, one mount also Y" — which is
precisely how the paper reports it — whereas re-keying would impose a per-sample table on the large
majority of procedures that use one route throughout. Revisit if mixed-route sessions become common;
the field would then need `sample`, not a longer sentence.

**One key left untested rather than validated.** `Pre-Analysis Imaging and Screening` was moved to
`sample` on the strength of its own definition — imaging performed to select targets, with individual
analyses linked back to the images, is per sample almost by construction. It has **zero** literature
extractions in any TAPP, so under 7.12 it is *untested rather than contradicted*, in the same sense
as the `Primary Calibration Standard Name` coverage limit recorded above. Stated so it is not later
mistaken for a validated key.

**Minor observations, not acted on.** `Fusion Flux and Dilution Ratio` is `N/A` in 13 of 14
procedures — a field of very narrow applicability, which is a Rule 6.5 conditional-block question
rather than a key question. And `Pre-Ablation Surface Treatment`'s description says the treatment is
applied *"immediately before each analysis"*; that is a statement of timing, not of cardinality, and
Column I is right to stay `(none)` — noted because it reads at a glance like the Column B key leak
7.8.9 exists to catch.

---

### The channel↔analyte binding must live on whichever field defines the channel (2026-08-12)

**Decision: `Collector Configuration` becomes `defines: channel per analyte` in the three
multicollector TAPPs, and its description asks for the analyte each cup serves.** Module_MCICPMS
v4 → v5; LA-MC v12→v13 (+U-Pb), Solution MC v15→v16.

**The defect, which was a side effect of a correct decision.** 7.4b allows exactly one definer per
key, so where a cup array exists `Collector Configuration` is the channel definer and
`Monitored Isotopes` is demoted to plain `analyte`. That much is right and is in the
technique-dependent key register. What it silently cost: `Collector Configuration` was plain
`defines: channel`, so nothing stated which cup served which analyte. Solution MC has no
`Monitored Isotopes` field at all, so the relationship existed nowhere but inside a free-text cup
string; LA-MC had two unjoined mass lists — masses per cup and masses per analyte — with no field
asserting they enumerate the same masses.

**Why that mattered more than it looks.** The only way to recover the binding was to parse element
symbols out of the cup string and match them against the analyte list — which is exactly the
inference 7.3.1 forbids (*"never infer membership from the child"*). The three TAPPs left a consumer
with no legitimate route to a relationship the other ten state outright.

**The fix generalises the rule rather than special-casing it:** the binding belongs on whichever
field defines the channel domain, whatever that field is called — `Monitored Isotopes` in
single-collector ICP-MS, `WDS Spectrometer Channel` in the electron-beam TAPPs, `EELS Edges` in TEM,
`Collector Configuration` where a cup array exists. Monitor and internal-standard cups carry no
parent, which 7.3.1's nullable-parent semantics already cover.

**Found by asking a schema developer's question against the library rather than in the abstract:**
*"when a TAPP declares both an analyte domain and a channel domain, what says which channels measure
which analyte?"* Ten TAPPs answered it; three did not, and the three were invisible until the
question was run as a query.

---

### Lab-XCT resolution fields — three collapsed to two (2026-08-12)

**Decision: `Minimum Resolvable Feature Size` is retired; `Spatial Resolution` becomes
`Effective Spatial Resolution (PSF/MTF)`. Lab-XCT v16 → v17, 98 fields → 97.**

**What prompted it.** A schema developer asked whether `Spatial Resolution` and
`Minimum Resolvable Feature Size` were the same property. They are not — one is contrast-independent
(can two features be *separated*), the other contrast-dependent (can a feature be *seen and
quantified*), which is why the second was keyed `sample > sampling unit` and the first was scalar.
Checking the question against the literature produced a different answer than either field's
definition predicted.

**The literature finding, which is the durable part.** Re-reading all ten source PDFs:
**nine of ten use the phrase "spatial resolution" to mean the voxel size.** Genge: *"Spatial
resolutions (in voxels) were 0.625 µm"*. Richard: *"spatial resolution of 2.06 µm/px (8.7 µm³/vx)"*.
Tomkinson: *"a resolution of 10.3 × 10.3 × 10.3 µm³ per voxel"*. **One procedure of seventeen**
reports an effective resolution — Glavin's *"resolution limits of ~30 µm (around 3× the voxel
size)"*, and that is a rule of thumb, not an MTF measurement. The extractions were faithful; the
field's name simply meant something stricter than the community's use of the same words. Hence the
qualifier in the new name, and a line in the description telling curators to file the paper's
"spatial resolution" under `Voxel Size`.

**Why the third field went, and it is not the reason first proposed.** The suggestion was that a
minimum feature size is "arbitrary and subjective". That alone does not disqualify a field — the
library keeps `Analysis Inclusion and Rejection Criteria`, which is entirely judgement, because a
stated cut-off changes the reported number and must be recorded. **The real ground is redundancy:**
`Partial Volume Effect Criteria` already asks for *"the minimum feature size criterion adopted for
the procedure (in voxels or µm)"*, and already held both real criteria in the corpus — Genge's
≥5.4 µm and Tomkinson's ~3 voxels, the latter with the retired field reading `N` for the same
procedure. Genge's criterion was recorded in **both** fields simultaneously. The criterion/measurement
split (the Oxide Production pattern) does not earn its keep where the measurement half has one
instance and that instance duplicates a resolution limit.

The Withers et al. (2021) convention — ≥3 voxels to identify, ≥10 for reliable shape and volume —
moved into `Partial Volume Effect Criteria`, which asked for the number but offered no norm for
choosing it, together with the reason it matters: *"the criterion materially changes reported modal
abundances and size distributions, so two datasets are not comparable without it."*

**Two extraction traps found on the way, both of which a keyword-driven pass would have made worse.**
Neuman's and Shearer's *"spatial resolution of 60 µm"* is a **multispectral core imager** — filter
wheel, halogen source, incidence angles — not XCT. Treiman's *"reconstructed voxel dimension of 15 µm
with a minimum resolution of 30 µm"* is explicitly *"The **NCT** tomograms"*, i.e. neutron; that
paper reports no X-ray parameters at all, and its Lab-XCT cells now say so. Two Richard threshold
cells were cleared: their "~2 µm" was the paper's *measured size of a vapour phase*, not a declared
limit.

**Generalise:** before trusting a field's literature column, check what the papers mean by the
field's own name. A term that is precise in the TAPP may be loose in the community, and the
extractions will be faithful to the papers rather than to the definition.

---

## Triple-quadrupole instruments register under the Q-ICP-MS TAPP (2026-08-14)

**Decision.** A triple-quadrupole ICP-MS registers under the **Q-ICP-MS TAPP** — LA or Solution —
not under a separate TQ TAPP. The platform is named in `Instrument Model`, its identity in
`ICP-MS Type` (whose controlled list already offered `Triple quadrupole (ICP-MS/MS)` in both Q
TAPPs), and tandem operation, where used, in `Collision/Reaction Cell (CRC) Configuration`
(`ICP-MS/MS (triple-quadrupole mode)`).

**The principle: TAPP assignment is not instrument identity.** The instrument is recorded in its own
fields, so the container need not be named after it. **Analyser family** decides the TAPP —
quadrupole, sector, and multi-collector are different measurement principles in the VIM3 sense.
**Configuration** is a field value. This is the same line the library already draws when it makes
Spot / Transect / Mapping mode flags inside one TAPP rather than three TAPPs.

**How the question arose, and the reasoning error worth remembering.** Liu et al. 2024 use an Agilent
8900 — a TQ platform — and state no MS/MS mode, no tandem operation and no cell gas; Table 1 lists
single-quadrupole conditions. The first assignment was `LA-Q-ICP-MS`, justified by refusing to infer
TQ operation from a model number. **That inverted the source rule.** The label asserts
single-quadrupole operation, which the paper never states, inferred from *silence*; the model
designation, by contrast, is written down. Where a stated fact and an absence disagree, the stated
fact governs. The right answer was the same, for the opposite reason.

**Practitioner usage agrees.** Masuda et al. 2024 describe their iCAP TQ as *"a sensitivity-enhanced
quadrupole-based ICP-MS system"* and discuss gas versus non-gas CRC modes, never MS/MS. The stale
v13 extraction for that paper, written long before this decision, independently recorded the
instrument as `Thermo Fisher Scientific iCAP TQ (Q-ICP-MS with CRC)`.

### The standalone-TAPP question was settled by measurement, not by argument

The planning table hypothesised that LA-ICP-TQ-MS needed *"reaction cell gas identity and flow, MS/MS
operational mode (mass-shift vs. on-mass), reaction product ions monitored"*. That hypothesis was
tested against the only TQ paper in the corpus, using the 89-cell Masuda 2024 column preserved in
`Superseded TAPPs/2026-08-10/LA-ICP-MS (stale branch)/LA-ICPMS_TAPP_v13.csv`:

| | |
|---|---|
| Masuda cells carrying content | **62** |
| Field names absent from `LA-Q-ICP-MS_TAPP_v21` | **6** |
| Of those, genuinely new concepts | **0** |

All six are pre-rename spellings of fields the Q TAPP already has:
`ICP-MS Manufacturer & Model` → `Instrument Manufacturer` + `Instrument Model` ·
`Data Reduction Software` → `Data Processing Software(s)` ·
`Auxiliary and Cool Gas Flow Rates` → the two separate flow fields ·
`Drift Monitor Frequency` → `Calibration Standard Measurement Frequency` ·
`Spectrometer Dwell Time` → `Dwell Time per Mass` ·
`Uncertainty Level and Propagation` → the two fields it was split into.

**Residue zero. No TQ TAPP is warranted on current evidence** — and note *why* the hypothesised
distinct metadata did not appear: Masuda ran the instrument in **KED mode**, a collision-cell mode
available on any quadrupole, not in MS/MS mode. The hypothesis was never tested by this paper.

**The test that would settle it, stated so it is not re-argued from scratch.** Find papers that
actually operate in MS/MS mode — mass-shift or on-mass product-ion chemistry — add them as
literature-assessment columns to the existing LA-Q / Solution Q TAPPs, and count the residue again.
A coherent block above Rule 6.10's threshold justifies a module or a TAPP; two stray fields justify
two fields. Build nothing in advance: this is Rule 6.10's *"modules are extracted, not invented"*
applied one level up, and Rule 2's test that a split is earned only when divergence is large enough
that forcing it into the shared mould distorts the mould.

`Laser Ablation ICP-TQ-MS (LA-ICP-TQ-MS)` is retained in `paper_registry.csv` but **parked** — all
rows `N`. Masuda2024 moved to `LA-Q-ICP-MS`; Liu2024 stays there.

### CRC vocabulary harmonised in the same pass

Three vocabularies were in circulation across the 6 TAPPs holding
`Collision/Reaction Cell (CRC) Configuration`. Two defects mattered:

- **Solution Q could not record tandem operation at all** — no `ICP-MS/MS` value — which is the field
  this decision relies on.
- **Solution Q overloaded `None`**, using `None (STD mode)` for "cell present, no gas". Three of its
  five extractions read that way for instruments that demonstrably have a cell; Lu et al. 2007 states
  *"Our instrument has a collision cell with octapoles, but collision gases were not introduced into
  the cell"* — which is STD, not None. Those three cells were migrated.

Resolved to two lists, split by analyser family rather than forced identical, since Column F is
consumer-owned (Rule 6.4):

- **Q family** `Not installed | STD | KED | DRC | KED+DRC | ICP-MS/MS | N/A | None | Other: specify`
- **MC family** `Not installed | STD | KED | DRC | N/A | None | Other: specify`

`ICP-MS/MS` was **removed** from the two LA-MC TAPPs — a multi-collector has no second quadrupole, so
the value invited an answer that cannot be true. `Not installed` was **added** to the four LA TAPPs,
which lacked it; it is the value that separates "no cell hardware" from "cell present, no gas", and
therefore what lets an `N` in a literature column mean "not reported" rather than being confused with
either. Column B was left alone: it already carries four registered variants, and editing it would
create new Rule 7.8.9 divergence for no gain.

---

## The TQ decision re-tested against tandem papers (2026-08-17)

Three TQ-ICP-MS papers were supplied in `LA-Q-ICP-MS/TQ literature assessment/` to verify the
2026-08-14 decisions. **Both decisions hold. One of them no longer holds for the reason first given.**

| Paper | Introduction | Cell mode | Genuine tandem? |
|---|---|---|---|
| Wu et al. 2023 | LA (Photon Machines Analyte G2) + iCAP TQ | TQ + NH₃ mass-shift | yes |
| Gil-Diaz et al. 2020 | **solution** — Agilent 8800 and iCAP-TQ | O₂ mass-shift **and** KED | yes |
| López García et al. 2026 | **solution** — iCAP TQ | He KED only | no |

Two of the three are solution work despite being filed under LA-Q-ICP-MS.

**Decision 1 — TQ registers under Q-ICP-MS — confirmed, on better evidence than it was made.**
Wu tunes *"in the solution single-quadrupole (SQ) and no-gas modes"* and then *"switched to
triple-quadrupole (TQ) and NH₃ mode"*. **One instrument spans both within one session.** If Q and TQ
were different techniques the procedure would change technique halfway through tuning. Configuration,
not technique — demonstrated rather than argued.

**Decision 2 — no standalone TQ TAPP — confirmed, but the "residue zero" finding of 2026-08-14 was an
artefact of the sample.** Masuda gave zero because it ran KED and never tandem. Against papers that
do tandem chemistry the residue is small but real, and it is precisely one of the three things the
planning table predicted:

| Predicted distinct metadata | Outcome |
|---|---|
| reaction cell gas identity and flow | already had fields — `Reaction Gas Type`, `Reaction Gas Flow Rate` |
| MS/MS operational mode | needed a **key change**, not a field — see below |
| reaction product ions monitored | **the one genuine gap** — one new field |

**Generalise: a residue of zero means "no residue in this sample", not "no residue".** State what the
corpus could not have shown. Masuda could never have exercised the tandem fields, so the hypothesis
was untested, not refuted — and saying so is what made the second round worth running.

### Three changes applied

**1. `Monitored Isotopes` → `Monitored Masses` (8 TAPPs).** The field is the `defines: channel`
definer, and the channel domain contains non-isotopic members: Wu assigns a dwell time to
`(176+82)Hf` (300 ms), Gil-Diaz measures `125Te + ¹⁶O → 141TeO` and `77Se + ¹⁶O → 93SeO`. A field
named "Isotopes" invites a curator to prune exactly the members that `Dwell Time per Mass` and
`Interference Correction Method` are keyed by, breaking Rule 7.4a. Not cosmetic.

`Masses` was chosen over `Species` — the author's first suggestion — because conventions.md defines
Analyte as *"the chemical species a measurement is performed on"*, so reusing "species" for the
channel side would blur the analyte/channel line the 2026-08-12 decision record settled. `Masses`
also pairs with the channel-keyed `Dwell Time per Mass`. The registered key divergence is preserved:
`analyte` in the two LA-MC TAPPs, `defines: channel per analyte` in the other six.

**2. `Reaction Product Ion / Mass-Shift Transition` added to the 3 Q TAPPs**, keyed `channel`,
C=Advanced / D=Read-Only. `Monitored Masses` records the mass measured; this records the chemistry
that produced it — precursor, reagent gas, product. Without it a consumer cannot tell which analyte a
shifted mass reports. Not provisioned into the SF or MC TAPPs: no instances (Rule 6.10).

**3. `Collision/Reaction Cell (CRC) Configuration` re-keyed `(none)` → `channel` (6 TAPPs).**
Gil-Diaz uses two cell modes for two isotopes of the *same element* in one study — *"126Te measured
in KED-mode (He)"* against ¹²⁵Te in mass-shift O₂ mode. A scalar Controlled list cannot express that.
Rule 7.11 G3 decides it: declare the finest key unconditionally, because *"a consumer given `(none)`
cannot hold per-channel values at all"*. This also corrects the vocabulary harmonised on 2026-08-14,
which had assumed one cell mode per procedure.

**Declined, each a single instance (Rule 6.10).** Wu's ~14 Q1/Q3/CR lens voltages — `ICP Tuning`
holds the approach; the He/NH₃ gas mixture, which Wu describes as an experiment *"to test the effect
of mixture composition on reaction efficiency"* rather than the production procedure; and the
p_Lu/p_Yb reaction rates, which `Interference Correction Method` already covers by asking for *"the
production rate factor"*.

**Literature cells for the new field are `N`, not `N/A`.** Inferring "no mass shift" from a stated STD
or KED value is the step the Inference Rule forbids: *"If a value is logically implied by other stated
values but not written explicitly, record N."*

---

## Cell-gas mixture field, and the cross-TAPP consistency audit that came with it (2026-08-17)

**`Collision/Reaction Gas Mixture Ratio` added** to LA-Q, LA-Q_UPb and Solution Q. Declined on
2026-08-17 as a single instance; the TQ round supplied a second, and a production one:

> Wu et al. 2023 — *"the commonly used 1:9 NH₃–He mixture"*, and high-purity He pre-mixed with NH₃
> before the cell to test mixture composition (an experiment).
> Gil-Diaz et al. 2020, XSeries 2 — *"collision cell with He:H₂ mixture at 92% : 8% to minimise
> ⁴⁰Ar³⁷Cl interferences"* (the production procedure).

`Collision Gas Type` already offered `He+H2`, so the mixture **identity** had a home and the
**proportions** did not. Same three TAPPs as `Reaction Product Ion / Mass-Shift Transition`, on the
same reasoning: attested in LA-Q and Solution Q, U-Pb variant follows its parent, nothing provisioned
into MC or SF.

### The audit found four defects, three of them older than this session

Every field touched during the TQ work was compared across all TAPPs holding it, on Columns C, D, E
and I. **Column E is a definition column and divergence in it is a defect; Column F is
consumer-owned and legitimately varies.**

| Field | Was | Now |
|---|---|---|
| `Collision Gas Type` | `Text (free)` in 4 LA, `Controlled list` in 2 Solution | `Controlled list / Text` ×6 |
| `Reaction Gas Type` | same split, plus unicode subscripts (NH₃, O₂, CH₄) against ASCII | `Controlled list / Text` ×6, ASCII adopted |
| `Dwell Time per Mass` | `Text (free)` in 4 LA, `Numeric (ms) / Text` in 2 Solution | `Numeric (ms) / Text` ×6 |
| `Collision Gas Type`, `Reaction Gas Type` | `Keyed By = (none)` | `channel` |

**The re-key of 2026-08-17 was incomplete, and the TAPP already contained the proof.** `CRC
Configuration` was re-keyed to `channel` on the strength of Gil-Diaz running two cell modes for two
isotopes of one element — but the gases that *define* the mode were left scalar. The extraction
written into Solution Q the same day reads `Collision Gas Type = "He for KED; O2 for the mass-shift
mode"`: a per-channel value in a `(none)`-keyed field. **When a key changes, re-key the block, not the
field** — the fields that co-vary with it are where the inconsistency hides.

**Deliberately not re-keyed:** `Collision Gas Flow Rate`, `Reaction Gas Flow Rate`, `Cell Exit
Discrimination Voltage`. They co-vary with cell mode by physics, but no paper in the corpus states
them per channel, and Rule 7.12 decides on what is attested in reported data rather than on what is
physically possible. Flagged rather than assumed — the same discipline that kept `Beam Current` at
`sampling unit` and moved LA `Detection Limit` off it.

**Confirmed uniform, recorded so it is not re-checked:** `ICP Tuning`, `Instrument Warm-up / Session
Duration Limit`, `Instrument Sensitivity`, `Ion Counter Dead Time`, `Reaction Product Ion /
Mass-Shift Transition`, `CRC Configuration`, `ICP-MS Type`, `Sensitivity as Useful Yield`,
`Make-up Gas Flow Rate`, `Plasma / Make-up Gas Addition`, and both gas flow-rate fields — each
identical in C, D, E and I across every TAPP holding it. The one surviving divergence is
`Monitored Masses` (`analyte` in the two LA-MC TAPPs against `defines: channel per analyte`
elsewhere), which is the registered `KEYED_BY_TECHNIQUE_DEPENDENT` entry and correct.

### Closed 2026-08-17 — two concepts that carried two names each

> **Both entries below are now closed; the heading formerly read "Still open".** Corrected
> 2026-08-24 after an audit found this section, and the two that follow it, describing items that
> the 2026-08-17 reconciliations had already resolved. A register of open items that lists closed
> ones cannot be planned from — which is why the closures are now stated inline rather than only in
> the entries further down the file.

Not divergence *within* a field, so the audit above passes them, but they are the same cross-TAPP
naming problem one level up, and both were surfaced earlier in the session:

- `Instrument Sensitivity` (3 Solution TAPPs, `Numeric + unit / Text`, keyed `channel`) against
  `Sensitivity as Useful Yield` (6 LA TAPPs, `Numeric (%)`, keyed `analyte`). Deliberate as of
  2026-08-14 — the quantities genuinely differ — but they will have to be reconciled if an ICP-MS
  module ever owns either.
- `Make-up Gas Flow Rate` (3 Solution) against `Plasma / Make-up Gas Addition` (6 LA). Flagged
  2026-08-14 as needing reconciliation, still unreconciled.

---

## `Make-up Gas Flow Rate` and `Plasma / Make-up Gas Addition` reconciled (2026-08-17)

One field under two names since the LA and Solution lineages were built separately. Now
**`Make-up Gas and Flow Rate`**, uniform across all 9 ICP-MS TAPPs
(C=Advanced, D=Editable, E=`Numeric (L/min) / Text`, Keyed By `(none)`).

**The extractions settled it, not the descriptions.** After the 2026-08-14 broadening the two Column
B texts read similarly, which is suggestive but not decisive — descriptions can converge while fields
still hold different things. The literature columns are the harder evidence, and every filled cell on
both sides records the same two quantities: the argon make-up flow, and the presence or explicit
absence of a small sensitivity-enhancement addition.

> LA: *"Ar make-up: 0.9–1.2 l min⁻¹; Ar auxiliary: 0.6–1.2 l min⁻¹"* · *"Ar make-up: 0.81–0.99 l min⁻¹
> (mapping); N₂ explicitly not added"* · *"N₂ or Ar mixed into He carrier for sensitivity optimization"*
> Solution: *"0.25 L/min supplementary Ar for PFA micronebulizer"* · *"None — the Apex Ω was run 'with
> no auxiliary N₂ flow'"*

**Generalise: to test whether two fields are one, compare what has been extracted into them, not what
their descriptions say.** A description states intent; an extraction states what curators actually put
there. Where the two disagree, the extractions are the fact.

**Why neither incumbent name survived.**
- `Plasma / Make-up Gas Addition` collided with `Coolant (Plasma) Gas Flow Rate` in the same TAPP —
  two fields whose names both open by invoking the plasma, only one of which is a plasma gas.
- `Make-up Gas Flow Rate` said only "Flow Rate" while the field demonstrably holds the gas identity
  too (*"0.25 L/min supplementary Ar"*).
- `Make-up Gas and Flow Rate` matches `Carrier Gas and Flow Rate`, its nearest sibling in the same gas
  block and the library's established form for a field carrying gas identity together with flow.

**Column E** took the Solution form, `Numeric (L/min) / Text`, over the LA bare `Text (free)`: the
compound keeps the unit while still admitting the multi-part answers the extractions contain. C, D and
Keyed By already agreed on both sides. Column F was left per TAPP — consumer-owned, and each
lineage's examples are already right for its technique.

Both old names are in `RETIRED_FIELDS`. The documents naming them are all dated records — the
2026-08-14 report and MC extraction notes, the development log, and earlier entries in this file —
which are correct as written at their date and were not rewritten.

---

## `Sensitivity as Useful Yield` merged into `Instrument Sensitivity` (2026-08-17)

Now one field across all 9 ICP-MS TAPPs: C=N/A, D=Advanced, E=`Numeric + unit / Text`,
Keyed By `channel`. 13 extraction cells carried across.

**This case was closer than the make-up gas one, and for a reason worth recording: the two fields held
physically different quantities.** Useful yield is a dimensionless efficiency — the percentage of
sampled atoms detected as ions. Sensitivity is signal per unit concentration or mass. Neither converts
into the other without knowing how much material was consumed, which is precisely why Horstwood et al.
2016 recommend useful yield for laser ablation: cps/ppb is not comparable between laboratories when
spot size, fluence and repetition rate differ. Merging fields that are *not* synonyms needs a stronger
argument than "they answer the same question", and the evidence supplied one.

| | attestation |
|---|---|
| signal per unit concentration or mass | **13** filled cells across the 3 Solution TAPPs — 572 V/ppm total Zr (Ibáñez-Mejía); ~50 V for a 1 µg/ml Os solution (Nowell); ~2.5 × 10⁶ cps/ppb on ¹¹⁵In (Misra); per-isotope counts pg⁻¹ ml (Makishima) |
| useful yield | **0** filled cells in 28 LA literature columns, and 0 in the Horstwood comparison TAPP that originated the field. An anchored scan of all 28 PDFs in the LA folders finds it reported **once**: Masuda et al. 2024, *"the achieved useful yield of analytes is about 0.1%"* |

Tang et al. 2014's *"ion yields (cps/spot diameter squared)"* and Chernonozhkin et al. 2024's
*"ablation yield"* were checked and are different quantities; they do not count as instances.

**The finding underneath the numbers: the LA field encoded a community recommendation, not observed
practice.** It entered the library from Horstwood et al. 2016 via the Horstwood comparison TAPP —
whose own copy of the field also has zero literature cells — and practice has followed it once in the
whole corpus. That is the argument for *merging* rather than *retiring*: the recommendation is worth
keeping, but it does not need a field of its own to survive. It now lives in the merged Column B,
which states both expressions and keeps Horstwood's reason for preferring useful yield where material
consumption varies, and in the LA Column F examples.

**Key changed `analyte` -> `channel`**, taking the Solution form. Sensitivity is reported per isotope
(Makishima tabulates it per isotope; Misra quotes it on ¹¹⁵In), and Rule 7.2's test settles it —
substituting a different isotope of the same element changes the number, because it depends on
isotopic abundance. Checked before applying: every LA TAPP retains 2–3 other `analyte` consumers, so
the `Analyte` definer is not orphaned under 7.4c, and all six define `channel` (via `Monitored Masses`
in the Q and SF variants, `Collector Configuration` in the MC ones) so 7.4a holds.

**Column E** took `Numeric + unit / Text` over `Numeric (%)`: the compound holds both expressions,
whereas the LA type could hold only the one nobody reports.

### Closed 2026-08-17 — candidates from a crude name-overlap scan

Both Solution/LA name splits are now closed. A word-overlap scan over fields with disjoint ICP-MS
footprints throws up 18 pairs, most of them false positives sharing only generic words. Two look like
the same lineage-split pattern and are worth a look when convenient — **their descriptions and
extractions have not been compared, so these are candidates, not findings**:

- `Between-Session (Long-Term) Analytical Precision and Assessment Method` (Q/SF) against
  `Between-Session Reproducibility and Assessment Method` (MC); likewise
  `Within-Session Analytical Precision and Assessment Method` against
  `In-Run Isotope Ratio Reproducibility and Assessment Method`.
- `Number of Replicates` (LA) against `Number of Replicates per Sample` (Solution Q/SF).

Apply the same test that settled the two closed cases: compare what has been extracted into them.

---

## Precision/reproducibility pair and `Number of Replicates` reconciled (2026-08-17)

Four fields became two, and a tier divergence closed. Solution MC alone had used "Reproducibility"
where the other eight ICP-MS TAPPs use "Analytical Precision":

| retired | survives | footprint |
|---|---|---|
| `In-Run Isotope Ratio Reproducibility and Assessment Method` | `Within-Session Analytical Precision and Assessment Method` | 8 → **9** |
| `Between-Session Reproducibility and Assessment Method` | `Between-Session (Long-Term) Analytical Precision and Assessment Method` | 8 → **9** |
| `Number of Replicates per Sample` | `Number of Replicates` | 6 → **8** |

**The definitions already agreed** — the MC "In-Run" field read *"Reproducibility of isotope ratio or
δ-value measurements **within a single analytical session** … on **replicate analyses** of an isotopic
standard … run as an unknown **during the session**"*, which is `Within-Session Analytical Precision`
in substance. The surviving names are also the metrologically correct ones: this library is
VIM3-aligned, and VIM3 reserves *reproducibility* for different-laboratory conditions, while
within-lab across-session work is *intermediate precision* — the term the surviving Between-Session
description already uses.

### The finding: a field name was silently corrupting its own extractions

**"In-Run" reads as within one measurement, and two of the three extractions in that field recorded
exactly that instead of what the definition asked for.**

> Nowell ×2 — *"Within-run errors quoted as 2SE of the mean, 2SE = 2SD/n^0.5 with n = 45"* — the
> internal precision of a single measurement, over its cycles. The paper does give the within-session
> quantity, in the adjacent sentence: *"the uncertainties for the short-term reproducibility of
> standards analysed in a single analytical session … are quoted as 2 standard deviations (2SD)"*.
> Ibáñez-Mejía — *"Internal uncertainty determined from counting statistics"* — also internal; its
> within-session quantity is the external reproducibility at 2σ of the spiked ZrNIST from each run.

All three cells were corrected from the papers, which had been read in full earlier in the session.
**Generalise: when a field name and its description disagree, the extractions follow the name.** A
curator reads Column A far more often than Column B, so a misleading name does not merely look untidy
— it produces wrong data, and the wrongness is invisible because every cell is plausibly filled.

### Tier divergence on `Number of Replicates`, and why neither side was wrong

C=N/A, D=Basic in LA against C=Basic, D=Read-Only in Solution — and each was honest about its own
lineage. The LA extractions read *"variable; 12–30 analyses per mineral phase"* and *"variable per
run"*; the Solution ones read *"6 replicates (Table 1)"* and *"3 runs (Table 3)"*, straight out of a
method table. Reconciled to **C=Advanced, D=Basic**: a procedure registers an intended count where it
has one, and the analysis records what was actually acquired. C=Basic would force LA procedures to
declare a number they cannot know; D=Read-Only would stop an analyst recording what was actually run.
The bare name survives because *"per Sample"* is wrong for spatially resolved work, where replicates
are per grain or per location — as the LA description already said.

### Closed 2026-08-17 — same defect class, outside the scope asked for

> **Closed.** `Mass Cycles per Replicate` is retired; `Number of Scans per Replicate` survives in
> both Solution Q and Solution SF (C=Basic, D=Read-Only, `Integer`, keyed `(none)`). Verified
> 2026-08-24. The original text follows.

`Mass Cycles per Replicate` (Solution Q) and `Number of Scans per Replicate` (Solution SF) carried
near-identical descriptions — *"Number of complete mass scans (sweeps) accumulated per analytical
replicate"* against *"Number of complete mass scans accumulated per analytical replicate"* — and are
plainly one field. One TAPP each; a two-line rename whenever wanted.

**Internal precision has no field anywhere in the library.** It is well attested — Nowell (2SE over
45 and 50 cycles), Ibáñez-Mejía (counting statistics), Desem (*"internal precision (2se) of
±0.001–0.002"*), Misra — and it is currently being written into the within-session field for want of
anywhere else, which is what made the "In-Run" mis-extractions so easy to miss. Three levels exist in
isotope work (internal within one measurement, within-session across analyses, between-session), the
library has fields for two of them, and the gap is real.

---

## `Internal (Within-Measurement) Analytical Precision and Assessment Method` added (2026-08-17)

Added to all 9 ICP-MS TAPPs — C=Advanced, D=Basic, `Text (free)`, keyed
`sample > sampling unit x reported property` — closing the gap found while reconciling the
precision pair. Group 6 now reads as a ladder in every ICP-MS TAPP:

> **Internal** (within one measurement) → **Within-Session** (across analyses in a session) →
> **Between-Session** (across sessions)

**Why the gap mattered more than an ordinary missing field.** Level 1 was already being written into
the within-session field for want of anywhere else, which is exactly what made the 2026-08-17 "In-Run"
mis-extractions invisible: the cells were plausibly filled with a real, carefully extracted number
that answered a different question. A missing field does not leave a hole — it displaces data into
the nearest field that will take it.

Attested across both lineages and all three analyser families: Nowell 2008 (*"2SE = 2SD/n^0.5; where
n=45 for the Neptune analyses and n=50 for the Nu Plasma"*), Ibáñez-Mejía & Tissot 2020 (counting
statistics), Desem 2022 (*"typical internal precision (2se) of ±0.001–0.002 for 206Pb/204Pb"*),
Wu 2023 (*"uncertainties (2SE) of single-spot ages were ~2.6%"*), LA-MC (*"SE at 95% confidence per
individual run"*). Five cells were filled on insertion from papers already read.

### Rule 6.1 condition 2 — the close call, recorded because it nearly went the other way

`Counting Statistics Error` already exists in EPMA, SEM and SEM_Composition: *"1-sigma uncertainty
propagated from counting statistics on peak and background intensities, for each reported
concentration variable per analysis."* Same **level** — one measurement — but a different
**quantity**: it is the uncertainty *predicted* from counts, where ICP-MS internal precision is
usually the *observed* scatter of the cycles making up the measurement.

The decisive evidence is that Ibáñez-Mejía quotes **both, in one sentence, and compares them** —
the external reproducibility was *"similar in magnitude or slightly larger than the internal
uncertainty determined from counting statistics"*. Two quantities a paper places side by side cannot
share one field.

**The description draws that boundary without naming `Counting Statistics Error`**, because that
field is not present in any ICP-MS TAPP and a cross-reference to a field the reader does not have is
its own defect. It says instead: *"Distinct from an uncertainty predicted from counting statistics,
which some procedures quote alongside it for comparison."*

**Key** matches `Counting Statistics Error` exactly — `sample > sampling unit x reported property`.
The same quantity shape deserves the same key, and this is the second field in the library to use
Rule 7.3's containment-then-cross-product form: within each sample, for each analysis, one precision
per reported quantity. Rule 7.4a holds in all 9, since `Sample Name`, `Sampling Unit` and
`Reported Variables and Units` are mandatory everywhere under Rules 13, 9 and 8.

**Tiers** C=Advanced, D=Basic, matching `Between-Session (Long-Term)`. C=Basic would force every
ICP-MS procedure to declare an internal precision, including trace-element work that never separates
it from the reported uncertainty.

**Open, and now visible:** `Counting Statistics Error` is attested in Solution MC (Ibáñez-Mejía) but
exists only in the three electron-beam TAPPs. Extending it to the ICP-MS TAPPs is the natural
companion to this addition and was deliberately not bundled with it.

---

## `Counting Statistics Error` extended to the ICP-MS TAPPs (2026-08-17)

Now in **12 TAPPs** — the 3 electron-beam ones it started in, plus all 9 ICP-MS — uniform at
C=Advanced, D=Basic, `Text (free)`, keyed `sample > sampling unit x reported property`. Group 6 in
every ICP-MS TAPP now reads:

> **Counting Statistics Error** (predicted from the counts) → **Internal** (observed within one
> measurement) → **Within-Session** → **Between-Session**

**Attested in 6 of 37 extracted ICP-MS papers, and two of them report the predicted and observed
values side by side** — which is what justifies two fields rather than one:

> Mittlefehldt et al. 2024 — *"theoretical 1σ analytical precision (counting statistics plus
> propagation of uncertainties) on the Fe/Mn ratio of pallasite olivine of ~0.6%; standard deviations
> for each meteorite calculated from the analyses range from 0.6 to 4.0%"*
> Barnes et al. 2025 — *"quadratic combination of internal counting statistics from the sample
> measurement and external precision from standard replicates"*

0.6% predicted against 0.6–4.0% observed, in one sentence. No single field holds that, and the
comparison is itself the information: agreement means the measurement is shot-noise limited, and a
larger observed scatter points to a further source of variance. The harmonised description now says
exactly that, so the reason the two fields coexist is visible at the point of use.

**Description harmonised across all 12.** The incumbent text was electron-beam specific — *"propagated
from counting statistics on peak and background intensities"* — and would have been simply wrong in an
ICP-MS TAPP. Leaving the ICP-MS copies different would have created a fresh Rule 7.8.9 divergence, so
one technique-neutral text now covers both: counts on the analyte together with any background or
blank subtracted from it.

### Cross-references were made to run one way only, deliberately

`Counting Statistics Error` exists in 12 TAPPs; `Internal (Within-Measurement) Analytical Precision`
exists in 9. So:

- the **`Counting Statistics Error`** description states the boundary **without naming** the
  internal-precision field, because three of its holders do not have that field;
- the **internal-precision** description, which lives only where both fields are present, **does name
  `Counting Statistics Error`** explicitly.

**Generalise: a cross-reference is safe only in the direction of the smaller footprint.** Naming a
field the reader may not have is the same defect as a stale reference — the linter cannot catch it,
because nothing is wrong with the file, only with what it tells the reader to look for.

**Placement is adjacent, on purpose.** The instinct after the "In-Run" mis-extraction was to keep
similar fields apart; the opposite is right. Separation is what let internal precision be written into
the within-session field unnoticed. Two closely related fields sitting next to each other, each naming
what the other holds, is what makes a curator choose correctly.

---

## `Mass Cycles per Replicate` merged into `Number of Scans per Replicate` (2026-08-17)

The last of the split-name pairs, and the simplest: identical C=Basic, D=Read-Only, E=Integer,
Keyed By `(none)`, and descriptions differing by one parenthesis — *"Number of complete mass scans
(sweeps) accumulated per analytical replicate"* against *"Number of complete mass scans accumulated
per analytical replicate"*. Extractions matched in shape on both sides (*"250 sweeps per replicate"*,
*"48 scans per 30 s acquisition"*, *"2000 sweeps per set × 30 sets"*, *"LR: 15 passes × 3 runs"*).
7 cells preserved; now uniform across Solution Q and SF.

**The name was not a coin toss, despite one TAPP each.** "Cycle" already means something specific in
this library, and the difference is physical: `Number of Cycles per Block` defines a cycle as *"a
single set of **simultaneous** Faraday cup readings"*, whereas a scan is a **sequential** traversal of
the monitored masses. Simultaneous multi-collection and sequential scanning are different acquisition
physics, so reserving *cycle* for one and *scan* for the other preserves a real distinction — keeping
"Mass Cycles" would have blurred it. The surviving name also matches the library's established
`Number of X per Y` form.

**No cross-reference between the two**, because their footprints are **disjoint** — Solution Q/SF
against the three MC TAPPs. Naming either in the other's description would point every reader at a
field they do not have. This is the same rule recorded earlier today, in its strictest case: where
footprints are disjoint the reference is unsafe in *both* directions, so the boundary is stated
generically instead — *"distinct from a cycle in simultaneous multi-collection"*.

Not extended to the LA TAPPs: no LA paper in the corpus states a scan count, and laser ablation
acquires a continuous transient where the equivalent information sits in `Ablation Duration per Spot`
and `Total Integration Time per Output Data Point`.

### All flagged split-name pairs are now closed

`Make-up Gas` · `Instrument Sensitivity` · the precision/reproducibility pair · `Number of Replicates`
· `Number of Scans per Replicate`. The word-overlap scan's remaining candidates were checked and are
genuinely distinct fields sharing generic words.

---

## `Instrument Sensitivity` tested against an external template and left at `channel` (2026-08-23)

**No change applied.** All 9 ICP-MS TAPPs keep Keyed By `channel`. Recorded because the argument for
changing it was good enough that it will be made again.

The AGN ICP-MS Template — a community workbook built as an explicitly relational schema, eight
worksheets each joined on `analyticalSessionID` — devotes a whole sheet to sensitivity and keys it by
`sensitivityReferenceMaterial` × `targetMass`, with `sensitivityBeamSize` alongside. That is a clean,
well-formed cross-product, and read on its own it says TAPP's `channel` is missing an axis. TAPP's own
Column B appeared to concede the point, asking for the value "with the isotope or channel it was
measured on *and the conditions it applies to*" — cardinality in the description, which Rule 7 treats
as a smell.

**The literature does not support it.** 30 filled extraction cells across the 9 TAPPs; none reports
sensitivity per reference material.

| observed shape | evidence |
|---|---|
| one value per session | 572 V/ppm total Zr (Ibáñez-Mejía); ~1000 kcps/ppb Pb<sub>total</sub> (Desem); ~50 V for a 1 µg/ml Os solution (Nowell); total Zr beams 3.5–13 V at 30 ppb (Schönbächler) |
| one value per isotope — `channel` | Makishima 2011 tabulates ¹¹¹Cd, ¹¹⁵In, ¹⁴⁹Sm, ²⁰⁵Tl, ²⁰⁹Bi; Hu 2022 gives 10 V for ¹⁴⁰Ce, 4 V for ¹⁴²Nd, 3.5 V for ¹⁵²Sm; Yu 2005 tabulates CPS/ppb per isotope |
| per **reference material** | **0** |
| nearest second axis anyone reports | *hardware configuration*, not `standard` — Misra 2014 across spray chamber and injector; Hopp 2021 wet vs dry plasma, MR vs HR |

`audit_keys_vs_literature.py` concurs: the field is absent from its 38 findings, so declared shape and
observed shape agree.

**The reasoning is already precedent.** `Elemental Fractionation Correction` was adjudicated 2026-08-12
at 14 ev — *"reference materials are mentioned because the correction uses them, not because the field
repeats over them."* Sensitivity is the same case. The tuning concentrations quoted beside these values
("1 ppb ¹¹⁵In", "~100 ppb Mo solution") qualify one number; they do not make it repeat. `ICP Tuning`
keeps `(none)` on identical grounds despite naming both RMs and isotopes.

### The general lesson: a template is a hypothesis, not attestation

This is the first time an external reporting template was used as key evidence, and the failure mode is
worth naming. A template is a **prospective schema** — it records what its authors think ought to be
captured. A literature extraction records what practitioners actually reported. Rule 7.12 already
breaks the tie ("the key is the finest axis attested in reported data"), and it should be applied to
template-derived proposals exactly as to any other. A template can invite a column nobody fills.

Two other proposals from the same comparison — `Primary Calibration Standard Name` keyed by
`reported property` (AGN keys the PRM by `reductionTarget`), and reference-material ablation
conditions keyed by `standard` (AGN carries separate beam size / fluence / repetition rate for
primary, matrix and sensitivity RMs) — are **held pending the same literature test**, not adopted.

**Do not re-open on template evidence alone.** Reopen if a literature audit finds procedures publishing
sensitivity as a table over reference materials; the AGN sheet by itself has now been weighed.

---

## `Detection Limit` and `Detection Limit Method` typed (2026-08-24) — amds-ldeo/tapp#1

**Decision.** `Detection Limit` → **`Numeric + unit / Text`**; `Detection Limit Method` →
**`Controlled list / Text`** with a uniform Column F. Applied to all 12 TAPPs carrying the pair,
plus TEM's `EDS Detection Limit`. Keyed By is unchanged (`reported property`, settled 2026-08-12).

**The question came from outside.** A schema-generation consumer reported that the same metadata
item was being generated in three incompatible shapes — `Text (free)` → a string with no
`schema:unitText`; `Numeric (ppm or wt%)` → a number with `schema:unitText` pinned to a const;
`Numeric + unit / Text` → a number with `schema:unitText` required but unpinned — which blocked
collapsing 12 duplicated parameters into one shared definition. The issue asked whether a detection
limit is a dimensioned number (making EPMA/SEM the outlier) or legitimately free text (making the
numeric typing over-tight).

**The literature answered it, and the answer was neither.** Of 42 attested cells across the 13
TAPPs, **zero** are a bare number: 29 per-analyte lists, 6 ranges across analytes, 4 qualitative.
So option (1) is false. But the values are not prose either — they are dimensioned quantities that
simply repeat over an axis the Data Type column cannot express, which is what `Keyed By:
reported property` had been saying all along.

**No const can be correct.** The attested units span three dimensions — mass fraction (wt%, ppm,
µg g⁻¹), mass concentration (µg/L, ng/L, pg/mL) and molar (nM, µmol/mol). µg/L is the *normal* form
for solution work, where the LOD is a property of the solution and not the rock, so adopting the LA
`ppm or wt%` verbatim — which the issue floated — would have been actively wrong for three TAPPs.
The LA cell was in any case contradicted by its own row: Column B named three units while Column E
pinned one, and Column F's example was a string.

**Generalise: when a keyed field's Data Type looks wrong, check whether the column is being asked to
carry cardinality.** Column E states what kind of value a field holds and `Keyed By` states how many;
each lineage here had independently collapsed a keyed multi-value into one Column E cell, and had
collapsed it differently. EPMA/SEM degraded to free text (lossy but honest), LA to a pinned scalar
(lossy and wrong), Solution split the difference and happened to land on the right answer.

**Precedent for the form.** `Instrument Sensitivity` is the structural twin — a keyed, dimensioned,
per-channel figure of merit — and has been `Numeric + unit / Text` across 9 TAPPs since 2026-08-14.
The `/ Text` half is earned, not an escape from choosing: 10 of the 42 attested cells are ranges or
qualitative statements, and *"LODs not formally reported; all concentrations above detection limits
except noted"* is a real answer to the question the field asks.

**Why the Method is a compound too.** All 10 of its attested cells name a formula, cite a source, or
both; none is free prose. A typical value — *"Longerich et al. (1996): LOD = (3SD/S) × √(1/Nb +
1/Na)"* — is a named family **and** a reference **and** an equation. Solution's `Controlled list`
held the family but not the citation; LA's `Text / URI` held the citation but not the family. Each
was half the answer, which is exactly the case `Controlled list / Text` exists for.

**Column F**: `3σ blank | 3σ background | 3σ counting statistics | 3× blank mean | Poisson
statistics | N/A | None`. No `Other: specify` — a compound whose first component is `Controlled
list` must not ask twice for permission the `/ Text` half already grants. `3σ counting statistics`
is the one value not resting on literature attestation; the electron-beam TAPPs have none on this
field, and it is taken from their own Column F examples (Goldstein 2018, Llovet 2020 Eq. 4) because
the alternative was forcing EPMA and SEM into `Poisson statistics` — the same over-tightening the
patch exists to undo. **Recorded rather than buried**, so a future reader can challenge that one
value without re-deriving the other six.

**Not settled by this entry:** `EELS Sensitivity and Detection Limit` (TEM) keeps `Text (free)`. It
bundles a specification (ZLP energy resolution) with a result (detection limit), so no single type
fits it; splitting the field is the cleaner fix and remains open — see `KEY_NAME_VARIANT_EXEMPT`.

---

## `Internal Standard Approach` retired from the solution lineage (2026-08-26)

**Decision.** Retired from Solution Q-ICP-MS and Solution SF-ICP-MS; kept in the six LA TAPPs with
the in-situ meaning, and moved into `Module_LaserAblation` (18 → 19 fields), whose consumer set it
now matches exactly. This cleared the last entry in `COLE_DIVERGENCE_TRIAGED`.

**It was never a typing problem, which is how it was first diagnosed.** The field appeared as a
Column E divergence — `Text (free)` in the 6 LA tables, `Controlled list` in Solution Q/SF — and was
retyped to `Controlled list / Text` on a 0.66 distinctness ratio. That retype tripped the Column F
check, which forced a reading of what the two lineages actually meant:

> LA — *"Method used to determine the internal standard (IS) **concentration** for each unknown
> sample"* → `Single element from EPMA (SiO₂ wt% used as IS)`, `Sum-of-major-oxide normalization`
>
> Solution — *"**Role(s) assigned** to the internal standard(s) in data reduction"* →
> `Drift correction only | Matrix normalization | Drift + matrix normalization`

**The question is only meaningful in situ.** When the internal standard is native to the sample, how
its concentration was obtained is a real design choice with several defensible answers. When it is
added to a solution, the concentration is known by construction and the answer is always the same —
and its value is already in `Internal Standard Concentration`. So the field was copied into a
lineage where it had no discriminating answer, and rather than being dropped it was **repurposed**
to ask something else.

**What it was repurposed to ask, three other fields already answered.** All 11 attested Solution
cells were checked individually before removal:

| Solution cell | already recorded in |
|---|---|
| `Drift correction (Rh as IS)` ×3 | `Drift Correction Method` = *"IS normalization (Rh)"* |
| `ID internal standard (149Sm for drift + concentration)` | `Isotope Dilution Data Reduction Method` + `Internal Standard Element` |
| `Mass fractionation correction (Tl for Pb mass bias)` | `Drift Correction Method` = *"Tl mass bias correction…"* |
| `N/A (no IS; matrix-matched external calibration)` | `Drift Correction Method` = *"Standard bracketing…"* |

**Generalise: a field that must be repurposed to stay useful in a second lineage probably does not
belong there.** The tell is not that the descriptions differ — plenty of legitimate fields differ by
technique — but that the *question* has only one possible answer on one side. Check that before
reconciling the wording.

**A methodological caution recorded with it.** A token-overlap test of the 11 cells against the
other fields reported 8 as carrying unique content. They did not: the "unique" tokens were
*drift*, *correction*, *concentration* — role words supplied by the destination field's NAME, which
a cell-content comparison cannot see. The redundancy was only visible by reading. This is the fifth
occasion in one working session on which a lexical shortcut misread what reading settled, against
three occasions on which an automated invariant check caught what reading missed. Both are
necessary; neither substitutes for the other.

---

## The reviewed segmenter had three bugs, and reading found all three (2026-08-27)

**Context.** The sentence segmenter written for the Description/Purpose split had been reviewed and
used on two passes — 358 module-owned sentences and 218 ICP-MS-slice sentences — before it was
pointed at the 212 non-ICP-MS TAPP-owned texts. It carried three defects into all of that work.

| Bug | Effect |
|---|---|
| A possessive apostrophe (`the procedure's target`) was treated as an opening quote | Quote state never closed, suppressing **every** subsequent sentence break in the cell |
| A sentence beginning with a digit was not recognised | `…in micrometers. 0 indicates…`, `…file size. 1×1 indicates no binning.` stayed fused |
| A sentence beginning with a quoted term was not recognised | `Instrument Variant` S1 stayed a four-sentence run-on |

**How they were found, and how they were not.** An automated anomaly sweep over the same corpus —
very short segments, segments starting lowercase, missing terminal punctuation, unbalanced
parentheses — returned **one** flag, and that one was a correctly segmented short instruction. All
three real bugs were found by reading the segmenter's output. The apostrophe bug is the instructive
one: its symptom is a segment that is *too long*, and every cheap structural check for a bad segment
looks for something malformed. A run-on of four grammatical sentences is not malformed.

**Then automation established the blast radius, which reading could not.** Re-segmenting all 1750
Description cells and the 138 module rows under the fixed segmenter showed the module corpus changes
in exactly two cells, and that in both the newly separated sentences route to Description anyway —
so no applied work was corrupted. Reading 1888 cells to establish that would not have been done.

**Generalise: the two methods fail in opposite directions, and that is why the split of labour is
stable.** Reading finds defects whose signature is semantic (a segment that is well-formed but
wrong). Automated invariants find the scope of a defect once its shape is known, and catch the
mechanical slips reading skims past. This is the sixth lexical-shortcut failure recorded against the
fourth automated-check save; the ratio keeps favouring reading for *discovery* and automation for
*extent*. Neither ordering works alone: reading first, then measure.

**Operational consequence.** The segmenter now lives at `Project Files/Scripts/tapp_segment.py`.
Both apply scripts that used it (`apply_step1_purpose_20260825.py`,
`apply_step1_icpms_slice_20260825.py`) import it from a `/private/tmp/claude-501/...` scratchpad
path belonging to a session that has ended. Those scripts are already applied and are kept as
records, but they are **not re-runnable as written** — anything new must import the repo copy.

---

## `Analysis Sequence` D-tier divergence resolved by its own description (2026-08-27)

**Decision.** `D=Read-Only` → **`D=Editable`** in Solution MC-, Q- and SF-ICP-MS, making all nine
ICP-MS TAPPs `C=Basic, D=Editable`. This closed the older of the two divergences that the
"Known unresolved tier divergences" section above had deliberately left open since 2026-08-08.

**What changed was not the argument but the evidence.** In 2026-08-08 the three Solution tables
still carried wording inherited from `Sample Sequence Design`, and with three lineages describing
the field differently the tier split could be read as tracking a real difference in meaning. The
2026-08-26 merge of the 26 ICP-MS descriptions made Column B **identical across all nine**, and the
shared text ends:

> *"Adjustments must maintain the bracketing strategy defined in the procedure."*

A sentence that constrains **how** the analyst may adjust presupposes that the analyst may adjust.
That is what `D=Editable` means. So the harmonised description contradicts `D=Read-Only`, and the
question — *is the run order analyst-adjustable, or does changing it make a different procedure?* —
is answered by the field's own text rather than by majority vote among the tables.

**Generalise: harmonising a description can settle a tier divergence that was left open for want of
evidence.** The 2026-08-08 entry was right to leave it open — at that time the descriptions differed
and neither answer was better supported. Re-open the register's open items after any pass that
merges wording; a divergence recorded as unresolved may have become decidable without anyone
revisiting it. Worth doing for `Sample Persistent Identifier`, the other entry in that section,
which is a policy question and probably will **not** be settled this way.

**Consequence, executed the same day.** `Analysis Sequence` was the only one of the 26
ICP-MS-specific fields left out of `Module_ICPMS`, and this divergence was the reason. It has now
been moved in: `Module_ICPMS` **38 → 39 fields, manifest v4 → v5**, placed in the `session` block
whose target group `4. Measurement Information` is where the field already sat in all nine.

**The move changed no TAPP content.** All six module-owned columns (A, B, C, D, E, I) were already
byte-identical across the nine consumers once the D-tier was resolved, so composition rewrote them
to the values they already held. The only cell that changed in each TAPP is the Column G provenance
stamp `Source: ICP-MS module` — one cell per TAPP, nine in total, confirmed by `--check` before the
write. The four lineage-specific Column F example sets (LA bracketing counts; SSB and double-spike
for Solution MC; matrix-matched bracketing for Solution SF) are untouched, because F is an overlay
column and a consumer keeps its own. This is the same shape as `Module_ICPMS` v1, which converted
nine hand-maintained copies of 13 fields into one owned definition without changing any content.

With this, all **39** ICP-MS-specific fields identified at extraction are module-owned, and the
26-field merge that began on 2026-08-26 is complete.

---

## `Module_CompositionQC` — the 12-TAPP quantitative-composition layer (2026-08-27)

**Decision.** Five fields extracted into a new Layer 2 module consumed by the 12 TAPPs that report a
calibrated quantitative composition: `Detection Limit`, `Detection Limit Method`,
`Counting Statistics Error`, `Secondary Reference Materials`, and
`Normalization / Standards-Based Correction`. `Module_ICPMS` set this set aside on 2026-08-25 as
"the quantitative-composition set ... a candidate layer of their own"; this is that layer.

**The consumer set is a real boundary, not an artefact of authoring.** All five fields are present in
exactly the same 12 TAPPs and absent from exactly the same four — SEM_Imaging, SEM_FIBSEM, TEM and
Lab-XCT, which are the imaging and structural techniques. A module whose fields disagreed about their
consumers would be a sign the grouping was invented; these agree to the TAPP.

**Two of the seven candidates were excluded, and the reasons differ.**

`Sample Preparation Method` has **15** consumers, not 12, and sits in Group 2. A different consumer
set is a different module. It also carries an unresolved D-tier split (Editable 11 / Read-Only 4).

`Primary Calibration Standard Name` is the one deferred for a reason that may change, and it is worth
stating precisely because it looks superficially like `Secondary Reference Materials`, which was
resolved. Its `Keyed By` splits `analyte` (5 TAPPs) against `(none)` (7). A module owns Column I, so
shipping it means declaring one key for all 12 — and **the per-analyte axis is genuinely attested**:
8 of EPMA's 11 extracted cells assign standards per element (*"Anorthite (SiKα, AlKα, CaKα); albite
(NaKα); fayalite (FeKα)…"*), and the 2026-08-12 audit set LA-SF to `analyte` on Navarro et al. 2024.
`analyte` over-declares for the seven; `(none)` destroys structure the literature attests. That is
exactly the **G3 conditional-key policy question** recorded in `Survey_ColB_ColI_Report_2026-08-12` —
*declare the finest key unconditionally, or add a conditional marker?* — and it should be decided as
policy, not settled sideways by one field's extraction.

**`Secondary Reference Materials` went the other way, and the literature is why.**
`defines: standard per analyte` (EPMA, SEM, SEM_Composition) → **`defines: standard`** (all 12).
Across all 12 TAPPs, **zero** extracted cells are per-analyte shaped: EPMA's own four are plain
standard lists (*"USNM San Carlos olivine (Fo90); Kakanui kaersutite"*), and SEM and SEM_Composition
have no extractions at all. Only Column F's template example was per-analyte — and a template can
invite a column nobody fills. The structural argument agrees: the per-element assessment of a
secondary standard lives in `Analytical Accuracy` and `Analytical Precision`, both keyed
`standard x reported property`, so carrying it here duplicated their key.

**Generalise: two fields can look like the same problem and separate cleanly on evidence.** Both were
`Keyed By` divergences on the same lineage boundary, in adjacent rows, about the same `analyte` axis.
One resolved on 0-of-12 attestation; the other is blocked because 8-of-11 attest it. The
distinguishing test was not the shape of the divergence but whether the finer axis appears in
reported data — Rule 7.12, applied per field rather than per pattern.

**What modularising did that splitting could not.** The Description/Purpose split was measured and
found *not* to make divergent descriptions converge (0.17 → 0.21 similarity, 0 of 26 fields
converging). Extraction does: these five went from **5 distinct descriptions each to 1**, with each
lineage's Column F preserved as an overlay. Convergence is what a module is for; the split was never
going to deliver it, and this is the contrast worth remembering when choosing between the two.

**Effect on the registers.** 53 → 47 INFO. `Secondary Reference Materials` left both
`keyed-by-divergence-registered` and `colb-definer-stem-registered`; `colb-divergence-principled`
24 → 22 and `colb-divergence-mixed` 11 → 9. Registers shrink by harmonising, never by reclassifying.

---

## Two more modules, and the difference between an extension and an extraction (2026-08-27)

**`Module_LaserAblation` 19 → 29 fields (v6 → v7).** Ten fields present in exactly the six LA TAPPs
and unowned by any module: `Background Count Time`, `Carrier Gas and Flow Rate`, `Elemental
Fractionation Correction`, `Fusion Flux and Dilution Ratio`, `Mapping Area`, `Matrix Offset
Correction (LIEF)`, `Multi-Run Sequential Analysis Design`, `Sample Form / Analytical Substrate`,
`Sample Introduction`, `Signal Smoothing`.

**All ten were already byte-identical across all six consumers on every owned column** — a pure
ownership transfer, no authoring risk, and they mapped onto the module's four existing blocks by
their current group so no new block was needed. INFO was unchanged at 47, because fields that agree
were never in a divergence register to begin with. This is the cheapest kind of module work and it
is worth looking for first: the question "which unowned fields already agree?" is answerable
mechanically, and the answer was ten.

**`Module_CollisionCell` v1, 6 fields, 6 consumers.** The collision/reaction cell subsystem, shared
by the Q and MC lineages. The SF TAPPs are not consumers because sector-field instruments have no
cell and do not carry these fields at all — the consumer set falls out of the hardware, which is the
signature of a real layer rather than an accident of which tables were authored together. C, D, E and
`Keyed By` were already uniform on every field; only the descriptions diverged, four variants each,
and those were merged by reading. INFO 47 → 41.

**Three cell fields were left out and the reason is structural.** `Collision/Reaction Gas Mixture
Ratio`, `Reaction Product Ion / Mass-Shift Transition` and `Signal Collection Mode` sit on a
*different* consumer set — LA-Q, LA-Q U-Pb and Solution Q only. Three is below the Rule 6.10 floor,
and carrying them as a conditional block would reintroduce conditional modules, retired library-wide
on 2026-08-14. A module whose blocks have different consumer sets is two modules wearing one name.

**Generalise: sort module candidates by whether their columns already agree, not by size.** The ten
LA fields and the six CRC fields looked equivalent in the survey — both "a coherent block of unowned
fields on a clean consumer set". They were not equivalent in cost at all: one was a transfer that
could be verified mechanically and written the same hour, the other needed six merges by reading.
The distinguishing query is cheap to run and should precede the choice.

### A guard fired correctly, and the failure mode it exposed

The LaserAblation bump refused to write because the provenance stamp it was told to expect
(`Source: laser ablation module`) did not match the module's actual `source_comment`
(`Source: Laser Ablation module`). Right outcome — but it fired **after** `compose_tapp` had already
written one composed file and, through `record_composition`, advanced that TAPP's entry in
`composed_tapps.json` to a version that then had to be deleted. The registry was left pointing at a
file that did not exist.

**A late guard is not a safe guard when the step it guards has already committed side effects.**
Recovery was simple only because the registry repair is mechanical: any entry pointing at a missing
file whose predecessor exists is rolled back one version. Worth knowing that `compose_tapp --out`
mutates the register as a side effect, so any script that composes and then validates must be able
to undo the register, or must validate before composing.

---

## G3 decided — declare the finest attested key unconditionally (2026-08-27)

**Decision.** Recorded as `conventions.md` **7.3.2**. Where a field is scalar in a simple procedure
and keyed in a complex one, Column I declares the finest key the literature attests, unconditionally.
No conditional marker is added to the key notation.

**The two errors are not symmetric, and that is the whole argument.** Under-declaring is lossy: a
consumer generating a schema from Column I emits a scalar where the reported data is a list, and the
structure survives only in prose it cannot read. That is exactly the defect reported in
amds-ldeo/tapp#1. Over-declaring is verbose: a simple procedure fills a keyed table with one row,
which is correct, just roomier. A conditional marker would be more exact than either and was
rejected on cost — it makes every downstream consumer implement extra grammar for a handful of rows.

**7.12 is unchanged and still binding.** "Finest *attested*" — 7.3.2 does not license inventing keys.
It settles only what to do once the literature shows an axis is real but conditionally exercised.

**The gap turned out to be nearly closed already.** G3 was raised on 2026-08-12 over 5 rows in
`Integration Time per Cycle` and `Dwell Time per Mass`. Both now declare `channel` across every
consumer — they were resolved in passing by later Column I work, and nobody recorded that the policy
question they raised had lost its examples. **A policy question can be answered by drift before it is
answered by decision**; the register should be re-read before a policy is drafted, not only before it
is applied.

**One live case, and it was the one that surfaced the question.**
`Primary Calibration Standard Name` → `analyte` across all 12, changing the seven that declared
`(none)`, and with that it joined `Module_CompositionQC` as its sixth field (v1 → v2). The axis is
attested rather than assumed: 8 of EPMA's 11 extracted cells assign standards per element, and the
2026-08-12 audit had already set LA-SF to `analyte` on Navarro et al. 2024. The seven `(none)`
declarations were procedures that do not exercise the axis — the case 7.3.2 exists for.

Registers: 41 → 39 INFO; the field left `keyed-by-divergence-registered` (4 → 3) and
`colb-divergence-principled` fell 16 → 15.

---

## Overlay defaults never reached consumers, and 18 cells were sitting undelivered (2026-08-27)

**Defect.** The 2026-08-25 decision declared Column J `Purpose` an **overlay** column: *"the module
supplies a default Purpose that a consumer inherits on composition and owns thereafter — the same
relationship Column F already has."* That was never implemented. `compose_overlay` writes only
**owned** columns for a field already present in the consumer, so a module's overlay value reached a
consumer only when the field was newly inserted. For every field a consumer already had — which is
every field, whenever a module is extracted from existing TAPPs — the default was silently dropped.

**It was not hypothetical.** Measured across the library: **18 cells** of Purpose text authored in
`Module_ICPMS` (`Guard Electrode`, `Interface Cone Configuration`, `ICP-MS Type`) had never reached
the six LA consumers, which showed empty where the module had content. The three Solution consumers
had the text only because the 2026-08-25 ICP-MS slice pass wrote it into the TAPPs directly.

**Fix.** Overlay columns are now filled **only where the consumer's cell is empty**. A consumer's own
value is never overwritten, which is what "inherits, and owns thereafter" requires. Blast radius was
exactly those 18 cells, all Column J, all previously blank.

**How it stayed hidden for two days.** It was worked around three times before it was diagnosed —
once for `Module_ArAr` (recorded at the time, but read as a quirk of a module with no consumers),
once for `Module_CollisionCell`, once for `Primary Calibration Standard Name` — each time by leaving
rationale in Column B and deferring the split. **Three workarounds for one cause is the signal; the
first two were each cheap enough to take.**

### And a register-clobbering bug in the bump scripts, same session, same shape

`compose_tapp.record_composition` rewrites `composed_tapps.json` during composition, including each
module's recorded version. The bump helper loaded the register **before** its compose loop and wrote
that copy back afterwards, discarding those updates — which is how `CompositionQC` came to record v2
against a v3 manifest and raise `module-version-drift`. Fixed by reloading the register after the
loop and applying only what the script owns.

Twice in one session a script and `compose_tapp` both wrote `composed_tapps.json` and the script
won. **`compose_tapp --out` mutates the register as a side effect; any wrapper must either reload
after it or not write the register at all.**

---

## Module Step 1 backlog closed, and the heuristic that nearly scoped it wrongly (2026-08-27)

**Done.** The 49 module rows that entered their modules *after* the 2026-08-25 module routing were
routed and split: `Module_ICPMS`'s 26 merged descriptions, `Module_LaserAblation`'s 11, and the two
modules built on 2026-08-27. 68 non-S1 sentences read; **7 rows gained a Purpose**, in
`CollisionCell` (4), `LaserAblation` (2) and `ICPMS` (1). Step 1 of the Description/Purpose split is
now applied to every row in the library, module-owned and TAPP-owned alike.

**It only became possible today.** Purpose written into a module reached no consumer until the
overlay-default propagation was fixed earlier the same day. Had this backlog been cleared a week
ago, the Purpose text would have sat in the modules and arrived nowhere — the `Module_ArAr` loss,
repeated at scale.

### The backlog was found structurally, and a lexical heuristic had it about half wrong

A first pass looked for rationale words in Column B — *improves, controls, because, at the cost of,
efficiency, suppression* — and returned **7 rows**. That number was right by coincidence and the
membership was not. Set against what reading actually routed to Purpose:

- **3 false positives** — `Core · Data Processing Software(s)`, `ICPMS · Isobaric Interference
  Corrections Applied`, `LaserAblation · Mapping Area`. Each contains a rationale-shaped word inside
  a sentence that is doing definitional or scope work.
- **3 false negatives** — `CollisionCell · Collision Gas Type` and `· CRC Configuration`,
  `ICPMS · Sampler and Skimmer Cone Material`. Each carries real rationale in vocabulary the word
  list did not anticipate ("is standard for", "enables", "is used ... for its greater corrosion
  resistance").

Roughly 43% wrong in each direction, on a 7-row answer that looked precise.

**What found it correctly was a structural question, not a better word list:** *which module rows are
absent from the 2026-08-25 routing CSV?* That is exact, cheap, and needs no judgement — 49 rows, of
which 41 were multi-sentence. **When a backlog has a written record of what was covered, diff against
the record; do not re-detect the population.** The reading then went where it belongs: deciding
routes, not finding candidates.

---

## Step 2 on module rows, and why a sentence NUMBER is the wrong key (2026-08-27)

The 7 flags from the module Step 1 backlog were applied — 4 rewrites, 2 splits, 1 deletion, across
`CompositionQC`, `ICPMS` and `LaserAblation`. Each was made **once in the module** and composed out
to its consumers, which is the return on having extracted those fields.

**The Step 2 script failed on its first run, and the failure is worth keeping.** It addressed
sentences by their number in the Step 1 routing CSV. But Step 1 had already *removed* the P-routed
sentences from Column B, so those numbers no longer index the column: `Carrier Gas and Flow Rate` S2
had gone to Purpose, shifting S3 into position 2. The script asked for sentence 3 of a two-sentence
cell and stopped.

It stopped rather than mis-edited only because the index was out of range. Had the cell held one
more sentence, **the edit would have silently landed on the wrong one** — a rewrite applied to a
sentence nobody reviewed, passing every guard, because the guards check word preservation and
non-emptiness, not identity.

**Fixed by keying every Step 2 edit on the original sentence TEXT.** A text key is immune to Step 1's
removals and to any later reordering, and it fails loudly and specifically when the target is absent
("it may already have been edited, or moved to Purpose by Step 1"). The TAPP-level Step 2 passes had
used text matching from the start; only this module pass regressed to positions.

**Generalise: never address a cell's contents by ordinal across a pipeline stage that can remove
contents.** Step 1 is exactly such a stage. The routing CSV's sentence numbers are a record of what
was decided, not a handle on what is now there.

---

## `Sample Preparation Method` — no module, and a tier divergence that is principled (2026-08-27)

**There is no Sample Preparation module to build, and the reason is worth stating rather than
leaving as an open backlog item.** Group 2 is already almost entirely module-owned: `Module_Core`
holds the four universal fields, `Module_UPb` two, `Module_LaserAblation` three,
`Module_SolutionIntroduction` nine. What remains TAPP-owned is `Sample Preparation Method` and a
handful of single-TAPP fields. **One field cannot be a module** — Rule 6.10 requires five.

**Nor can it join `Module_Core`.** Core has 16 consumers; `Sample Preparation Method` has 15, absent
from Lab-XCT. The obvious question was whether Lab-XCT's `Sample Preparation Notes` is a Rule 1 name
variant that would close the gap. **It is not.**

| | `Sample Preparation Method` | `Sample Preparation Notes` |
|---|---|---|
| Data Type | `Controlled list / Text` | `Text (free)` |
| Column C | Basic | Advanced |
| Asks | what **form** the sample is in — polished thin section, grain mount, fused bead, FIB lift-out, whole-rock powder | what **steps** were applied — trimmed, dried, wrapped in PTFE, "scanned as received" |

XCT scans an intact object, so there is no preparation *form* to choose from; that is why Lab-XCT
carries no `Sample Preparation Method`, and the two fields are complementary rather than duplicates.
Renaming either would merge a controlled vocabulary into free prose.

### The D-tier divergence is principled, and structurally determined

`Sample Preparation Method` splits `D=Editable` (11) / `D=Read-Only` (4) — the fifth of the five
`tier-divergence` findings, and the one hidden behind the summary's "(+1 more)". It is not drift.
The split falls **exactly** on whether the TAPP has a companion field that absorbs session-specific
preparation detail:

- **`D=Read-Only` (4)** — the three Solution TAPPs, whose `Digestion Temperature`,
  `Digestion Duration` and `Sample Aliquot Mass or Volume` are all `D=Editable`; and TEM, whose
  `Sample Preparation Details` is `D=Editable`. The *method* is fixed by the procedure; the session's
  variation is recorded next door.
- **`D=Editable` (11)** — EPMA, the four SEM tables and the six LA tables. **None** has such a
  companion, so the field itself must carry the variation. EPMA's own description says so:
  *"Includes session-specific variations from the procedure standard."*

**Zero exceptions in 15 TAPPs.** Recorded here as intentional under Rule 2/4; no data changes.

> **SUPERSEDED the same day — this adjudication was wrong.** The 15/15 correlation was real; the
> causation was not. See "`Sample Preparation Method` made universal" below: the literature shows the
> *method itself* varies session to session, so `D=Read-Only` made a real choice unrecordable, and
> the companion fields carry details rather than the method. The field is now `D=Editable` in all 16.
> **A perfect correlation across a small library is not evidence of a principle — it is a hypothesis,
> and it must still be tested against what the procedures report.**

**Generalise: a tier divergence can be a consequence of field inventory rather than a disagreement.**
The same field is legitimately Read-Only where a neighbour is Editable and Editable where it stands
alone. Before harmonising a D-tier split, check whether the tables that differ also differ in what
*else* they carry — the test is cheap and it settled this one outright.

---

## `Sample Preparation Method` made universal, and into `Module_Core` (2026-08-27)

**Decision (maintainer's call).** The field is now present in **all 16 TAPPs** and owned by
`Module_Core` (30 → 31 fields, v4 → v5), `D=Editable` throughout.

**The argument for universality is that absence forecloses a true statement.** Lab-XCT was the only
TAPP without it, on the reasoning that XCT scans intact objects. But if an XCT procedure *does* scan
a prepared sample, it had no way to say so. Its own literature shows this happening: *"Chips
(~10.3 g) crushed with mortar and pestle ... split into two ~4.6 g portions"*, *"Decanted for XCT;
sample split along fractures during mounting into pipette tips"*, *"None; chip used as received"* —
forms, being squeezed into the free-text `Sample Preparation Notes` for want of a Method field.

**The two fields remain distinct and both are kept.** `Sample Preparation Method` is the **form**, a
controlled list at `C=Basic` — thin section, grain mount, fused bead, FIB lift-out, whole-rock
powder, and now bulk/core/powder/mounted for XCT. `Sample Preparation Notes` is the **handling steps**
before scanning, free text at `C=Advanced` — trimmed, dried, wrapped in PTFE. Preparation performed
by the analysing laboratory (making a section, lifting out a lamella) is not the same claim as
handling applied to material in transit or storage.

### The D-tier adjudication made hours earlier was wrong, and the literature is what overturned it

That entry called the `Editable` 11 / `Read-Only` 4 split principled because it correlated perfectly
with whether the TAPP had a companion field absorbing session-specific detail. **Fifteen of fifteen,
and still wrong.** The extractions settle it:

| TAPP | attested | distinct methods |
|---|---|---|
| TEM | 21 | **5** — FIB lift-out (Ga), FIB lift-out (Ga+), crushing/dispersion on grid, ultramicrotomy, Ar ion milling |
| Solution MC | 10 | 9 |
| Solution Q | 6 | 6 |
| Solution SF | 6 | 6 |

The *method* varies session to session in exactly the four tables that declared it `Read-Only`. The
companion fields carry digestion temperature and duration — **details**, not the choice between FIB
and ultramicrotomy. `Read-Only` made that choice unrecordable, which is the lossy direction, the same
asymmetry that decided G3 (7.3.2) earlier the same day.

**Generalise: test a structural hypothesis against the reported data before recording it as a
principle.** The companion-field correlation was checked against *field inventory* — what the tables
carry — and not against *extractions* — what the procedures do. It took one query to overturn, and
the query was available the whole time.

**Only after both changes could the field enter Core**, which has 16 consumers and owns Column D: a
15-consumer field with a split D was ineligible on two independent counts.


---

## `EELS Chemical State Determination Method` — closing the gap the Detection Limit fix opened (2026-08-27)

**Added to TEM.** `C=Advanced`, `D=Editable`, `Controlled list / Text`, `Keyed By: (none)`, Group 5,
modes Y/Y/N. TAPP-owned: EELS is a TEM technique and no other TAPP carries the concept, so there is
nothing to extract.

**Why it exists.** Earlier the same day two cells were removed from `EELS Energy Resolution`, a field
typed `Numeric (eV FWHM)` that was holding Fe-valence determination *methods*. They were correct data
in the wrong field — and there was no right field to move them to, so the removal left them homeless.
This is the field they belonged in all along.

**The library's own vocabulary named the gap.** `EELS Energy Calibration` describes accurate
calibration as required for *"ELNES edge identification, chemical-state analysis, and inter-lab
comparability"* — it names the analysis while recording only the energy-axis calibration that
precedes it. A field that cites a neighbouring activity it does not itself record is a reasonable
place to look for a missing field.

**Data Type follows the amds-ldeo/tapp#1 precedent.** Both attested cells name a method *family* and
carry a citation or qualifier — *"Integral white-line intensity ratio I(L3)/I(L2) → Van Aken &
Liebscher (2002) universal calibration curve"*, *"Peak position and lineshape comparison to reference
standards (qualitative Fe valence state determination: Fe⁰, Fe²⁺, Fe³⁺)"*. That is exactly the shape
`Controlled list / Text` exists for, and it matches `Detection Limit Method`.

**`Keyed By: (none)`, deliberately.** A per-analyte or per-edge axis is plausible — a procedure could
determine Fe and Ti states separately — but **both attested cells determine one element**. Rule 7.12
keys on the finest axis *attested in reported data*, and 7.3.2 licenses declaring the finest
**attested** key, not the finest imaginable one. Revisit if a multi-element chemical-state procedure
is extracted.

**Literature: 2 attested, 19 `N/A`, 0 `N`.** The distinction was read, not assumed. Four other
assessed papers mention oxidation states, and none determined them by ELNES: Chaves et al. (2023) used
XPS (Fe-2p, O-1s, incident X-ray), Thompson et al. (2020) used Mössbauer, and Matsumoto et al. (2021)
and Zeng et al. (2024) cite other people's measurements. For those procedures the concept does not
apply — `N/A`, not `N`, per `lit_assessment.md`. **A keyword sweep for "oxidation state" would have
returned all six and been wrong about four of them.**

---

## `Module_ArAr` retired, not deleted (2026-08-27)

Moved to `Archive/Superseded Modules/` alongside `Group1` and `ReportingCore`; the module register
carries the row forward as `retired — carried`. 15 live modules → 14; `module-unused` cleared,
37 → 36 INFO.

**Retired rather than deleted, because the work is not wrong — only unused.** Sixteen fields, four of
which nothing else in the library can use (`Neutron Irradiation Conditions`, `Neutron-Induced
Interfering Isotope Production Ratios`, `Gas Extraction and Release Schedule`,
`F Value (40Ar*/39ArK)`), plus Step 1 routing already applied on 2026-08-25. The planning table still
carries *Static Noble Gas & Nitrogen Mass Spectrometry* at priority **H** — the instrument half of
the composition this module was built as the system half of. Reviving it is a file move.

**The retirement reason is written into the manifest before the move**, so the archived copy explains
itself without reference to a register it no longer appears in.

**The library already had this mechanism and it is worth naming.** A module is "live" if its files
are in `modules/`; `build_module_register.py` carries forward any register row whose files are gone.
So retirement is a *move*, not a delete, and the register is what remembers. Deleting the files
outright would have left the row to be regenerated away and the design lost to git archaeology.

**It cost something while it lived, and that is recorded.** The 2026-08-25 module Step 1 pass stripped
Purpose sentences from its descriptions with nowhere to put them — a module composed into no TAPP had
no consumer to inherit them — which is what prompted declaring Column J an overlay column. A module
with no consumers is not free; it is exercised by every library-wide pass and cannot absorb the result.

---

## Two name variants retired; and a key "divergence" that was already correctly adjudicated (2026-08-27)

**`STEM Dwell Time per Pixel` → `Dwell Time per Pixel`** (TEM), Data Type harmonised `Numeric (ms)`
→ `Numeric + unit`. A Rule 1 name variant that should not have existed, as the register's own backlog
note said. The stated reason for keeping it separate — STEM has no spectrometer, so the dwell is
scalar — is *already* how `Dwell Time per Pixel` behaves in SEM_FIBSEM and SEM_Imaging, which carry
it with `Keyed By: (none)`. The field handled the scalar case before the variant was minted.

**`Background Correction Method` → `X-ray Background Correction Method`** (EPMA, SEM,
SEM_Composition). Meaning unchanged; the name stops colliding with ICP-MS's
`Blank / Background Correction Method`, whose physics is unrelated. Same move as `Detector Type` →
`X-ray Detector Type` earlier the same day. Both retire register entries that existed only to keep
explaining a coincidence of naming.

Registers: 36 → 33 INFO. `cole-name-variant-triaged` and one `keyed-by-name-variant-registered`
cleared.

### The `Monitored Masses` proposal was wrong, and the register already said why

It was proposed that LA-MC-ICPMS and LA-MC-ICPMS_UPb be changed from `analyte` to
`defines: channel per analyte`, on the evidence that the other six consumers use the definer form,
that conventions.md 7.3.1 names this field as its worked example, and that those two tables key
`Interference Correction Method` by `channel` with no visible definer.

**Applying it raised two ERRORs immediately.** `Collector Configuration` is already
`defines: channel per analyte` in both tables: a multi-collector instrument enumerates its channels
as collector cups, not as scanned masses, so `Monitored Masses` is keyed *by* analyte there rather
than defining the channel domain. Rule 7's `rule7-multiple-definers` invariant caught it before
commit. Reverted.

**And the register entry already carried exactly that reason:**

> `"Monitored Masses": "defines: channel per analyte where there is no collector array; analyte where the cup array defines the channel"`

The divergence had been correctly adjudicated, with the precise mechanism written down. The proposal
came from reading the register's *list of entries* and not this entry's *reason text*.

**Generalise: a register of adjudicated divergences is documentation, not a to-do list.** Every entry
in `KEYED_BY_TECHNIQUE_DEPENDENT` carries the reason it was accepted. Read the reason before
proposing to close the entry — the argument for closing it may be the argument that was already
weighed and rejected. This is the second wrong call on a key divergence in one session; the first
was caught by reading the literature, this one by an ERROR-level invariant. **Both halves of the
method earned their place today.**

---

## Both interference-flag fields renamed; the Data Type was right and Column F was wrong (2026-08-27)

| | was | now |
|---|---|---|
| ICP-MS (9, module-owned) | `Isobaric Interference Corrections Applied` | **`Spectral Interference Corrections Applied`** |
| Electron-beam (3) | `Interference Corrections Applied` | **`X-ray Line Overlap Corrections Applied`** |

**Both old names were wrong, in opposite directions.** The ICP-MS name said *isobaric* while its own
description covers "isobaric, polyatomic or residual" — and in ICP-MS usage "isobaric" specifically
*excludes* polyatomic, so the name understated the field. The electron-beam name said only
*interference* while its description says "spectral". "Spectral interference" is the standard
umbrella in ICP-MS; "X-ray line overlap" is the standard electron-beam term and is the wording its
own sibling `Interfering Elements` already uses: *"Element(s) whose X-ray lines overlap with the
measured peak"*.

**`Controlled list / Text` was RIGHT and Boolean would have been wrong.** Of **51 attested cells,
zero are a bare Yes/No** — every one carries the answer together with what was corrected
(*"Yes — ⁸⁷Rb on ⁸⁷Sr…"*, *"No explicit corrections applied; monitoring of Mg, Si, P, S used to
detect and exclude inclusion-contaminated…"*). **Column F was the cell that did not match the data**,
reading `Yes | No | N/A | None` while describing none of them; it is widened to the attested form.

This is the mirror of amds-ldeo/tapp#1. There the Data Type was under-specified against the
literature; here it was correct and Column F was under-specified. **When a type and its allowed
content disagree, check which one the extractions support before assuming the type is the defect.**

**Not split into isobaric / polyatomic / residual fields.** A single procedure routinely corrects
several kinds at once — LA-MC corrects doubly-charged *and* isobaric; Solution MC isobaric *and*
argides; Solution Q oxide *and* argide *and* isobaric on the same masses. Three flags would mostly
all read "Yes" while losing the species-to-mass pairing, which already lives in `Interfering Species`
and `Interference Correction Method`, both `channel`-keyed. One general flag plus two fine-grained
keyed fields is the architecture the field's own description already describes.

### The first rename moved the collision instead of dissolving it

`X-ray Spectral Interference Corrections Applied` was tried first and raised two fresh WARNs. The
name-variant checks match by **containment**, not by `normalize_name` (which only collapses
punctuation) — and `Spectral Interference Corrections Applied` is a substring of the X-ray form, so
the pair was still flagged, just under new names. `X-ray Line Overlap Corrections Applied` shares no
stem and dissolves the entry outright. **A disambiguating prefix does not disambiguate a check that
matches on containment.**

Registers: 33 → 31 INFO; the `cole-name-variant` and `keyed-by-name-variant` entries for this pair
are both retired.

---

## The Data Type vocabulary reduced to two controlled-list forms; `Boolean` and `Other: specify` retired (2026-08-30)

**The defect.** Bare `Controlled list` is read as *closed* everywhere the term is load-bearing —
JSON Schema `enum`, XSD `enumeration`, SKOS. In this library **178 of 197 such cells carried
`Other: specify`** and were open. The label asserted closure and was wrong 90% of the time, and the
open/closed distinction lived de facto in Column F — the one content column with no cross-TAPP
check. `Technique` proves the cost: its Rule 1 exemption was implemented as *skip this field*
rather than *verify it stays closed*, so it drifted to open in **13 of 16 TAPPs** unseen.

**Rejected: a three-type scheme.** `Controlled list (open)` was considered and dropped. It and
`/ Text` emit the same validation shape — neither rejects an out-of-enum value — so openness cannot
separate them. The only property that does is facetability (the `Instrument Manufacturer` rationale
in `Module_Core.json`: a discovery facet needs a near-complete enum, which `/ Text` destroys), and
that was judged too thin to carry a third label.

**Adopted.** `Controlled list` = closed. `Controlled list / Text` = open, and expects a listed term
*plus* qualification. `Boolean` retired: of 4 attested cells across its 3 fields only **one** was a
bare Yes/No. `Other: specify` retired from all 226 cells — on a closed list it contradicts the
type, on a compound it asks for the wrong thing. Its reference value moved to a Data Type table on
the generated xlsx Legends sheet.

**Applied in three commits**, because only part of it was coupled. Retypes (51 cells) landed first:
the validator already exempted compounds from the `Other: specify` requirement, so
`Controlled list` → `/ Text` relaxed rather than tightened. The strip (213 cells), the two
`/ Text` → `Controlled list` retypes, and the `CONTROLLED_LIST_REQUIRED` inversion had to land
together or the baseline went 0 → ~226 WARN.

**`Technique` was held back** and still carries `Other: specify`. Closing a list that is incomplete
is what produced amds-ldeo/tapp#3's 84 invalid publication cells. Verify completeness before
closing.

### The measurement lesson — the scan was wrong, and reading found it

Classification was measured by scoring each field's attested cells as bare list members vs
qualified. **Four artefacts made the first run untrustworthy, every one found by reading cells, none
by the script's own checks:** the not-reported sentinel written long-form as `N (not stated) [P4]`
and counted as an extraction; `[P4]` provenance tags scored as content; `(stated section 3.1)` and
`(explicitly stated: "…")` embedded inside values; and parentheticals that are part of the term
(`Field Emission (FEG)`, `Normal plasma (1000 W RF)`) read as qualification.

**The dominant false positive generalises.** Per-analyte and per-phase assignment —
`LIFL (Fe, Mn); TAPL (Mg); PETL (Ca)` — reads as qualification to any text heuristic but is a
**Column I `Keyed By` matter, not a Data Type one**. Three such fields already declared
`Keyed By: channel` and were nearly retyped wrongly. On the thin-evidence fields the scan was wrong
on **6 of 8**. Calibrate any future scan against `Technique`, `Analytical Mode` and
`Instrument Manufacturer`, which must land ≥85% bare.

### Two findings that fell out of the same pass

**A closed list that enumerates subtypes needs a subtype-unstated member**, or a paper reporting the
coarse answer is forced into `Other:`. `Electron Source` showed it plainest — 14 cells read
`Other: FEG (type not specified in paper)` because the list demanded Cold vs Schottky. Three of the
five true vocabulary gaps found were this one defect. Of 26 closed fields with unmatched values,
only **5** had real gaps; the rest were synonym variance in the extraction cells, or answers on the
wrong axis (`Instrument Variant` collected `FESEM` ×10, which is the `Electron Source` axis).

**Normalising extraction cells was declined.** Rewriting a literature cell asserts something about a
named third party, and no validator check reads right of the `Literature Assessment` sentinel — so
nothing required it. Take it additively (a canonical column beside the extraction) if ever wanted.

---

## `Technique` closed, after its vocabulary was fixed (2026-08-30)

The last field carrying `Other: specify`, held back from the strip because its Column F was
known incomplete. **Three TAPPs' lists did not contain their own technique** — LA-SF offered
`LA-ICP-MS | LA-ICP-OES | LA-MC-ICP-MS | LA-ICP-ToF-MS | LA-ICP-MS/MS` against 7 attested cells
all reading `LA-SF-ICP-MS`, and Lab-XCT offered `XCT (laboratory, polychromatic cone-beam)`
against 14 cells reading `Lab XCT`. Closing it in that state would have repeated
amds-ldeo/tapp#3 exactly.

**Adjudicated four ways.** Each list holds the TAPP's *own* technique, not a menu of siblings —
the three Solution tables already worked this way, 29 of 29 attested cells matching their single
listed value. `Technique` is **platform-level**: the attested `SEM-EDS`, `fs-LA-Q-ICP-MS` and
TEM `STEM; EDS; EELS` composites name a detector, a laser pulse duration and a set of
spectroscopies, each already owned by another field — `fs-` in particular would duplicate
`Laser Pulse Duration`, whose own examples include `290 fs (Yb:KGW)`. Lab-XCT adopts the papers'
`Lab XCT`, plus `Lab XCT (nano-CT)` on 4 attested cells. And the two LA-Q tables gain
`LA-ICP-MS (analyser not specified)` — the subtype-unstated pattern — while LA-SF does not,
because all seven of its cells name the analyser. **Add members on evidence, not for symmetry.**

`N/A | None` also left the five lists still carrying them: Rule 1 already exempts `Technique`
from those as semantically empty, and the Solution tables had always omitted them.

**The validator's two exemptions are not the same exemption.** `CONTROLLED_LIST_EXEMPT` governs
the REQUIRED options only. The forbidden-options check has no exemptions at all — verified by
injecting `Other: specify` into `Technique` itself and confirming the WARN. A field can be
exempt from owing `N/A | None` while still being forbidden `Other: specify`; conflating the two
is what let `Technique` drift open in 13 of 16 TAPPs in the first place, since its exemption was
implemented as *skip this field* rather than *verify it stays closed*.

---

## Rule 7.8.11 — Column F gets the cross-TAPP check it had been missing (2026-08-30)

Column F was the last content column with nothing looking at it, and it earned a check the
hard way: **three separate defects in a single pass traced to it**, every one found by reading
because nothing was watching. `Dwell Time per Pixel` kept unit-free numerals in EPMA and TEM
after its type moved to `Numeric + unit`. The interference flags read `Yes | No | N/A` while
describing none of 51 attested cells. And `Technique` carried `Other: specify` in 13 of 16
TAPPs against its own Rule 1 exemption.

**Scoped to controlled-list types, and that scoping is the whole design.** Column F is
*normative* on a `Controlled list` — it IS the domain — and merely *illustrative* on
`Text (free)` or `Numeric (<unit>)`, where each technique's examples should differ. The numbers
bear it out: **18 controlled-list fields diverge against 109 fields of other types**. An
unscoped check would have shipped 127 findings, nearly all correct behaviour, and been ignored.

Comparison is on the member SET, order- and case-insensitive, so a reordered list is not a
finding. The 18 are frozen in `COLF_DIVERGENCE_TRIAGED` so the check ships at 0 WARN: **5
PRINCIPLED** (`Technique`, `Analytical Mode`, `Matrix Correction Method`, `ICP-MS Type`,
`Instrument Manufacturer` — all four of the first adjudicated during the 2026-08-30 Data Type
pass, with the domain genuinely differing per TAPP) and **13 BACKLOG**, not yet examined.

**A PRINCIPLED class was required from day one, not added later.** `ICP-MS Type` is the proof:
each TAPP lists only its own analyser family, and a Q-ICP-MS TAPP offering MC would be the
defect. Without the class the check would flag it forever and train people to ignore it.

---

## `Sample Mounting Method` — a vocabulary rebuilt because its GRAIN was wrong (2026-08-30)

The clearest case in the library of a Column F invented rather than observed: five of six
attested cells named a vessel the list did not contain.

| | |
|---|---|
| listed | straw, glass capillary, wax, modelling clay, flat quartz window, PTFE tape, stage pin |
| attested | pipette tips, plexiglass tube, custom PVC tube, glass vial, polystyrene support |

**The defect was the grain, not the members.** The list enumerated SPECIFIC VESSELS, and that
domain is unbounded — any container can hold a sample, so extending it never terminates.
Enumerating **holder classes** does terminate, and the `/ Text` half already existed to carry
the specific vessel: `Tube or vial — 1 cm plastic straw`. All seven attested cells map onto
the eight rebuilt members.

**This is the mirror of the `Electron Source` fix.** There the list was too FINE for what
papers report — it demanded Cold vs Schottky where the paper said only "FEG" — and the fix was
one coarse member. Here the list was too SPECIFIC throughout, and the fix was a coarser axis
for every member. Both failures look like "missing members" in a gap scan; neither is fixed by
adding any.

**Two of the six cells also showed containment PLUS a sealing layer** — `triple-sealed Teflon
bag` inside a plexiglass tube, `triple-bagged in Teflon` then inside a straw — contamination
control for planetary material, which the old list could not express at all because it forced
a single choice. Column B now asks for both layers.

**Generalises:** when attested cells cluster as *instances of* the listed members rather than
alternatives to them, the list is pitched at the wrong grain. Count how many attested values
could be added as members without the domain closing — if the answer is "indefinitely many",
raise the axis instead of extending the list.
