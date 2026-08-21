> **⚠️ ARCHIVED — PRE-VIM3 SNAPSHOT (2026-07-24)**
> This file reflects TAPP terminology *before* alignment with BIPM VIM3 (JCGM 200:2012): "Protocol" = the
> registerable, DOI-bearing object; "Procedure"/"Analysis" = the analysis-level execution. Kept for
> historical record only — **do not use for current TAPP work.** Current version lives at the original
> path in the TAPPs project (same filename, without this suffix).
>
> See the "Aligning TAPP Vocabulary with VIM3" migration plan for the full rationale.

---

# TAPP Precedent Decisions

This file documents the key non-obvious decisions made during LA-ICP-MS TAPP development, with the reasoning that led to each decision. These serve as precedents for future TAPPs — when a similar question arises, check here before opening a new discussion.

Each entry follows the format: **Decision → Reasoning → Generalization**.

---

## Group 4: Measurement Information

### Ablation Duration vs. Analysis Count Time

**Decision:** These are two distinct fields with different tier assignments. Ablation Duration per Spot is protocol-level Basic (C=Basic, D=Editable for spot mode only). Analysis Count Time was removed as a protocol-level field and replaced by Signal Integration Time at analysis level only (C=N/A, D=Basic, spot/transect only, J=N).

**Reasoning:** Ablation Duration is set in the acquisition method file before the session begins and is a deliberate protocol design choice (it reflects a trade-off between signal accumulation, sample consumption, and throughput). A reproducibility expert needs to know it. Analysis Count Time, by contrast, is the width of the integration window selected during data reduction after the ablation transient is inspected — it depends on when the signal stabilizes and may vary by sample. The Signal Integration Interval Method (the rule for choosing the window) is protocol-level; the resulting count time is analysis-level.

**Generalization:** Whenever a protocol specifies a duration and data reduction later selects a sub-interval of that duration, treat them as separate fields: the duration belongs in Group 4 (Measurement Information) at protocol level; the selected interval belongs in Group 5 (Data Processing) at analysis level. The method for selecting the interval is protocol-level (Group 5); the resulting time is analysis-level (Group 5, C=N/A).

**Mode note:** For mapping, the per-pixel cycle time is determined entirely by dwell times (a protocol-level Group 4 field) — there is no post-hoc window selection per pixel. So Signal Integration Time is J=N (not applicable to mapping). The description must explain this explicitly.

---

### Ablation Duration — mode-dependent tier

**Decision:** Ablation Duration per Spot is protocol-level Basic for spot analysis only (H=Y, I=N, J=N). The corresponding concept for transect (total transect duration) and mapping (total map acquisition time) is analysis-level, not protocol-level, and therefore is not a TAPP field at all.

**Reasoning:** For spot analysis, ablation duration is set once in the acquisition method and applied identically to every analysis — it is genuinely protocol-level. For transect, the total duration depends on the transect length, which is determined at analysis time by the size of the grain or feature being profiled. The protocol fixes the scan speed; the transect length (and therefore duration) varies by sample. For mapping, the total acquisition time depends on the map area, which is also sample-dependent. In both cases, the protocol captures what it can (scan speed for transect; scan speed + line spacing for mapping) and leaves the variable parts to the analysis record.

**Generalization:** When a duration is fully determined by the protocol (spot mode), it belongs in the TAPP. When a duration is determined by a fixed protocol parameter × a variable sample parameter (transect: speed × length), the protocol captures the fixed parameter and the analysis captures the variable one. Total duration is always analysis-level in this case.

---

### Oxide Production: two fields, not one

**Decision:** Two separate fields: "Oxide Production Method and Threshold" (C=Basic, D=Read-Only) captures the acceptance criterion and measurement proxy; "Oxide Production" (C=N/A, D=Basic) captures the actual measured ratio from the session.

**Reasoning:** These serve fundamentally different purposes. The threshold is a quality gate used during instrument tuning before analysis begins — it is part of the protocol design and should never change between analyses following the same protocol. The measured value documents actual plasma conditions in the session and varies day to day. Combining them in one field either conflates a criterion with a measurement or forces one of them to be blank in most entries.

**Generalization:** Whenever a protocol specifies an acceptance criterion (threshold, maximum allowable value, or minimum acceptable value) and the analysis records an actual measurement against that criterion, split into two fields: [Concept] Method and Threshold (protocol-level) and [Concept] (analysis-level measured). Other techniques where this pattern applies: instrumental blank threshold (solution ICP-MS), peak flatness criterion (MC-ICP-MS), detector dead time threshold (TIMS).

---

### Analyte — single merged field

**Decision:** One field: "Analyte" (C=Basic, D=Editable). The protocol registers the isotope suite the protocol is designed to measure; at analysis level the analyst records the specific isotopes actually measured in the session, which may be a subset of the protocol scope.

**Reasoning:** "Target Analyte" and "Analyte" represent the same type of information (an isotope list) at different stages, not fundamentally different data. D=Editable correctly models the relationship: the protocol-registered suite is imported into the analysis metadata form; the analyst may narrow it if certain masses were excluded due to interference issues or detector limitations in that session. This is structurally identical to other session-tunable parameters (laser fluence, flow rates), which also use D=Editable. Splitting into two fields (as done in earlier versions) created an unnecessary decoupling — the protocol value could not be auto-imported into the analysis form.

**Contrast with Oxide Production split:** The Oxide Production pair (acceptance criterion vs. measured value) is kept as two separate fields because the criterion and the measurement are *different types of information* — one is a quality gate, the other is an instrumental outcome. The Analyte case has no such distinction: protocol scope and analysis execution are the same quantity at different stages.

**Generalization:** When a protocol defines the intended scope of measurements and individual analyses may execute a subset of that scope, use a single field with C=Basic, D=Editable. Do not split. This applies to: isotope suites (isotope ratio MS), element panels (ICP-MS), spectral windows (Raman, FTIR), feature sets (XCT). The split pattern is reserved for cases where the protocol-level and analysis-level components are genuinely different types of information (criterion vs. measurement).

---

### Scan Speed — protocol or analysis level?

**Decision:** Scan speed is protocol-level (C=Advanced, D=Editable) for methods where it is fixed, but becomes analysis-level when the protocol specifies a target spatial resolution rather than a fixed speed. The TAPP field "Transect Rate, Mapping Rate or Step Size" is protocol-level.

**Reasoning:** When a protocol specifies "scan speed = 9 µm s⁻¹" as an invariant, this is a genuine protocol parameter — it constrains every analysis following this protocol. When a protocol instead specifies "target pixel size = 5 µm" (from which scan speed is calculated at analysis time based on spot size and repetition rate), the target pixel size is protocol-level and the resulting scan speed is analysis-level. In the TAPP, the field captures the protocol-level specification (either fixed speed or target resolution/rate); the description explains both interpretations.

**Generalization:** When a parameter is either directly fixed by the protocol or derivable from other fixed protocol parameters (making it a protocol-level derived value), it belongs in the TAPP. When it is derived at analysis time from a combination of protocol parameters and sample-dependent variables, it is analysis-level.

---

### Signal Smoothing — applicable to all modes with caveat

**Decision:** Signal Smoothing applies to all modes (H=Y, I=Y, J=Y) but the description explicitly flags that smoothing devices are generally incompatible with high-resolution mapping.

**Reasoning:** Excluding mapping entirely (J=N) would hide an important methodological fact: using a smoothing device for mapping degrades spatial resolution by averaging aerosol pulses from successive laser shots. Analysts choosing to run a smoothed mapping protocol should be aware of this. By keeping J=Y with a warning in the description, the TAPP ensures the field appears in mapping contexts where the user can explicitly note "None" — documenting an intentional absence rather than a missing value.

**Generalization:** Set J=N (or equivalent mode flag) only when the concept is genuinely inapplicable (e.g., "Ablation Duration per Spot" cannot apply to mapping because there is no discrete "spot analysis"). Set J=Y with a caveat when the concept applies but its implementation or appropriateness differs for mapping. This preserves the ability to document the absence of a parameter as a deliberate choice.

---

## Group 5: Data Processing

### Uncertainty Propagation Method — Advanced/Editable rather than Basic/Read-Only

**Decision:** C=Advanced (not Basic), D=Editable (not Read-Only).

**Reasoning (two parts):**
- Why Advanced at protocol level: Many labs use informal uncertainty estimates (e.g., "SD of replicate analyses") without a formally specified propagation framework. Requiring a formal propagation method as Basic would either exclude many legitimate protocols or generate low-quality boilerplate. Advanced encourages rigorous labs to document their approach without mandating it universally.
- Why Editable at analysis level: If D=Read-Only and the protocol-level value is void (because C=Advanced and the author chose not to specify it), Read-Only would import a blank value that the analyst cannot fill in. Editable allows the analyst to complete this field when the protocol author left it unspecified, without constituting a violation of the protocol.

**Generalization:** When a field is Advanced at protocol level (meaning it may be void in the protocol), the analysis-level tier should almost never be Read-Only. Read-Only imports the protocol value — importing void is useless. Use Editable instead, allowing the analyst to supply the value. This is the standard resolution for the "Advanced protocol / analysis needs a value" tension.

---

### Signal Integration Interval Method — protocol-level Basic

**Decision:** C=Basic (the approach is protocol-level and mandatory). The description covers spot/transect (time-window selection) and mapping (VOI selection, phase masking) as mode-specific implementations of the same concept.

**Reasoning:** Without documenting the integration approach, a data record is uninterpretable: the reader cannot know whether specific phases were excluded from integration, whether an automated or manual approach was used, or whether the data is spatially averaged or phase-specific. This is arguably one of the most important data provenance fields in Group 5. It should be Basic.

The fact that the approach means different things for different modes (time-window vs. VOI) does not disqualify it from being a single field — the description handles the mode-specific implementation. The underlying concept (how was the usable signal distinguished from the non-usable signal?) is universal.

**Generalization:** When a concept is mode-universal in purpose but mode-specific in implementation, keep it as one field and address the implementation variation in the description. Do not split into mode-specific fields unless the implementations are so different that a shared field name would be genuinely misleading.

---

## Group 6: Quality Control & Uncertainty

### Detection Limit — C=Advanced, D=Basic asymmetry

**Decision:** C=Advanced (optional at protocol level), D=Basic (mandatory at analysis level). This asymmetry is intentional.

**Reasoning:** At protocol registration time, formal LOD characterization may not yet be complete — a newly designed protocol may be registered before extensive blank measurements have been accumulated. Requiring LOD as Basic at protocol level would either block registration of new protocols or result in unreliable LOD values that the community cannot trust. Advanced is appropriate: thorough labs will include it; others will add it as the protocol matures. At analysis time, however, LOD is non-negotiable for data credibility: a published dataset without LODs cannot be properly interpreted near detection limits. Basic is appropriate at analysis level.

**Generalization:** The C/D asymmetry (Advanced protocol / Basic analysis) is the correct design for any QC metric that requires accumulated session data to characterize properly but is mandatory for any complete data submission. Other fields that warrant this treatment: detection limit method, precision, accuracy, LOQ.

### Precision and Accuracy — combined value + assessment method

**Decision:** Each precision/accuracy field captures both the assessment method and the resulting values in a single combined field. These are not split into separate "Method" and "Value" fields despite the LOD/LOD-Method split precedent.

**Reasoning:** The LOD/LOD-Method split was justified because LOD Method is a formula (a protocol-level design choice) while LOD Value is session-specific (an analysis-level outcome). For precision and accuracy, both the method and the value are Advanced/Basic at the same levels — they belong together. The method (which reference material, how many replicates, which statistic) is inseparable from the value because the same number means different things depending on how it was obtained. Splitting them would create two fields that are always filled together, adding complexity without benefit.

The description for each precision/accuracy field must explicitly require both components: the assessment method (RM used, n, statistic) and the values (per element or element group). A value without a method context is nearly uninterpretable for cross-study comparison.

**Generalization:** Split method from value when they have different tier assignments (LOD pattern). Merge them when they have the same tier assignments and are always used together (precision/accuracy pattern). The test: would either component ever be filled without the other? If no, merge.

---

## Structural Decisions

### D=N/A removed as a valid analysis-level tier

**Decision:** D=N/A is no longer a valid analysis-level tier. Fields that are relevant only at protocol level (no session-specific variation, no fresh analyst input) are assigned D=Read-Only. The protocol value is inherited into the analysis metadata form and displayed as read-only.

**Reasoning:** D=N/A ("not applicable at analysis level") and D=Read-Only ("imported from protocol, cannot be changed") produced identical behavior in the analysis submission pipeline: the value comes from the protocol and the analyst cannot modify it. The distinction provided no functional difference. Removing D=N/A simplifies the tier system to four valid analysis-level values and eliminates a source of inconsistency (e.g., "Funding Source for Protocol Development" was N/A while structurally identical fields like "Protocol Author" were Read-Only). The new invariant: every field must have a meaningful analysis-level assignment.

---

### Level-neutral field naming

**Decision:** Field names must not encode which level a value belongs to. Prefixes and suffixes such as "Default", "Target", "Achieved", "Typical", and "Actual" are not used in field names. The tier columns (C and D) encode level. Column B (Description) clarifies that the protocol registers a target or typical value and that analysts may adjust within allowed bounds.

**Reasoning:** Level-embedded names ("Default Laser Fluence", "Target Analyte", "Achieved Voxel Size") required either maintaining a separate column mapping protocol names to analysis names, or accepting that the Column A names were unusable as-is when building an analysis metadata form. Level-neutral names ("Laser Fluence", "Analyte", "Voxel Size") work directly at both levels.

**Exceptions retained:** "Target Material" and "Target Feature(s)" keep "Target" because it means *the material or feature type the protocol is designed to analyze*, not a value with a later achieved counterpart. These fields have no analysis-level counterpart requiring a different name.

---

### Coupled analysis fields — four standard fields in Group 1

**Decision:** Every TAPP includes four standard fields at the end of Group 1 (after Protocol Reference(s)) documenting multi-technique workflows: Coupled Technique(s), Coupling Description, Coupled Protocol DOI, and Coupled Dataset or Publication Reference. Default tiers: Coupled Technique(s) C=Advanced/D=Editable; Coupling Description C=Advanced/D=Editable; Coupled Protocol DOI C=N/A/D=Advanced; Coupled Dataset or Publication Reference C=N/A/D=Advanced. Individual TAPPs may adjust D tiers when coupling is computationally mandatory.

**Reasoning:** Many analytical techniques are routinely applied in combination — EPMA providing internal standard concentrations for LA-ICP-MS, XCT paired with NCT for complementary contrast, ICP-MS and noble gas MS jointly required for (U-Th)/He geochronology. Without standardised fields capturing what is coupled, how the coupling works functionally, and where the companion data lives, multi-technique datasets cannot be navigated or reproduced reliably. Group 1 is the correct location because coupling is an administrative and provenance property of the protocol design, not an instrument parameter.

**Why four fields and not fewer:** Coupled Technique(s) and Coupling Description are separated because the former enables machine-readable filtering (find all protocols coupled with EPMA) while the latter carries human-readable context that cannot be reduced to a controlled list. Coupled Protocol DOI and Coupled Dataset or Publication Reference are separated because the protocol DOI is stable and citable immediately upon protocol registration, while the dataset reference may be pending, co-submitted, or shared — the two fields have different lifecycles and reliability profiles.

**Dataset reference limitations:** A DOI pointing to a combined dataset submission does not uniquely identify which instrument produced which portion. Where coupling is documented only through a shared sample IGSN, the IGSN in Group 2 (Sample Persistent Identifier) is sufficient and the Coupled Dataset or Publication Reference field may be "None". The Coupled Protocol DOI is generally more reliable than the dataset reference and is the preferred machine-actionable link.

---

### Analysis-level fields in Group 1 (Protocol Identification)

**Decision:** Several analysis-level fields (Analyst, Analysis Start/End Date, Funding Source for Analysis) reside in Group 1 alongside protocol-level fields such as Protocol Name and Protocol Author.

**Reasoning:** Group 1 serves as the administrative header for both the protocol record and the analysis record. Analysis-level identity fields (who ran the analysis, when, under what funding) are logically co-located with protocol identity fields (who designed the protocol, when, under what funding) even though they have different tier assignments. Separating them into a different group would fragment the administrative context.

The mixed-tier nature of Group 1 is a feature, not a design inconsistency. It reflects the reality that the same form serves both protocol registration and analysis documentation.

### Protocol DOI — C=N/A, D=Basic (mandatory at analysis level)

**Decision:** Protocol DOI has no protocol-level value (C=N/A, because the DOI does not exist at the time of registration) but is mandatory at analysis level (D=Basic). The description explicitly states that if a DOI has been applied for but not yet minted, "pending" is an acceptable placeholder.

**Reasoning:** This field exists primarily as a policy instrument to encourage protocol registration. Making it mandatory at analysis level creates a direct incentive: analysts who want to submit data must have a protocol DOI (or at least have applied for one). The "pending" option prevents analysts from being blocked while waiting for DOI assignment.

The C=N/A / D=Basic combination is unusual (most analysis-level Basic fields also have a protocol-level presence) but is correct here because the DOI is a product of the registration process, not an input to it.

---

### Group 1 template — use `tapp_files/Template TAPP Group 1.csv` as canonical starting point

**Decision:** Every new TAPP begins Group 1 from `tapp_files/Template TAPP Group 1.csv`. The template contains the correct field list, tier assignments, and technique-neutral descriptions for all cross-TAPP Group 1 fields. Technique-specific examples and coupling descriptions are added in the TAPP-specific file.

**Reasoning:** Group 1 is designed to be largely transferable across TAPPs. Maintaining a single template prevents drift in field names, tier assignments, and descriptions across the TAPP library. The Coupled Technique(s) and Coupling Description fields in the template use technique-neutral language; each TAPP's example column provides technique-specific coupling examples.

---

### Group 3 software fields — D=Editable

**Decision:** Acquisition software and data reduction software fields in Group 3 are D=Editable (not D=Read-Only).

**Reasoning:** A minor version update to acquisition or data reduction software (e.g., Probe for EPMA v12.9 → v12.9.5, Iolite 4.6 → 4.7) does not constitute a new protocol — instrument hardware, operating conditions, and data reduction algorithms are unchanged. Analysts running under a minor version update should document the actual version used without being forced to register a new protocol. D=Editable is correct: the protocol registers the software name and major version; the analyst confirms or updates the minor version at analysis time.

**Contrast with hardware fields:** Instrument manufacturer, model, detector configurations, and other hardware parameters are D=Read-Only because a hardware change (different instrument, different detector) fundamentally changes what is being measured and must constitute a new protocol.

---

### Reference materials (Group 6) — C=Basic, D=Editable

**Decision:** Primary Calibration Standard Name and Secondary Reference Materials are C=Basic, D=Editable.

**Reasoning:** The protocol must commit to a specific set of reference materials (C=Basic — mandatory for protocol registration, because the choice of standards directly determines the accuracy of all results). However, at analysis time, a primary standard may be exhausted, unavailable, or temporarily substituted due to logistics. D=Editable allows the analyst to document the actual material used without being forced to register a new protocol for what is effectively a material availability substitution. The analyst is expected to note any substitution explicitly. This applies to both primary calibration standards and secondary reference materials (QC standards).

---

### WDS vs. EDS dead time — intentional asymmetry between correction method and measured value

**Decision:** WDS dead time is documented as a protocol-level correction *method* (WDS Dead Time Correction, C=Basic, D=Read-Only in Group 5) with no separate measured value field. EDS dead time is documented as an analysis-level measured *percentage* (EDS Dead Time, C=N/A, D=Basic in Group 5) with no protocol-level correction method field. These are two separate fields with no "method + value" paired structure.

**Reasoning:** The physics of dead time handling differs fundamentally between the two detector types:
- **WDS:** Dead time correction is a user-selectable mathematical algorithm (constant 3 µs, high-precision, logarithmic, etc.) embedded in the data reduction software. The analyst chooses the algorithm as a protocol design decision; it is applied transparently during intensity-to-concentration conversion. No standalone "WDS dead time" value is separately reported because the correction is absorbed into the quantitative result.
- **EDS:** Dead time correction is automatic — managed entirely by the SDD detector electronics. No user-selectable algorithm exists. What is reported is the *percent dead time*: the fraction of total acquisition time the detector spent processing rather than counting, which serves as a QC metric for count rate management. Values above ~40% indicate excessive count rate and degraded data quality.

**Generalization:** When a correction is user-selectable and algorithm-dependent, document the method at protocol level (no measured value needed). When a correction is hardware-automatic and produces a reportable QC metric, document the metric at analysis level (no method needed). Do not force a method+value split onto detector-specific processes that do not share the same structure.

---

### Beam mode (geometry) — D=Read-Only

**Decision:** Beam Mode (Focused / Defocused / Raster in EPMA; equivalent geometry fields in other techniques) is D=Read-Only.

**Reasoning:** The beam geometry is a protocol design choice tied to the target material type and analysis objective. A protocol that specifies "Focused beam for anhydrous silicates; 5 µm Defocused for glass and hydrous phases" encodes a deliberate methodological decision. Analysts follow this specification — they do not deviate from the beam mode at analysis time. Changing beam mode constitutes a different analytical approach and should trigger protocol review. D=Read-Only is correct; D=Editable would imply the analyst may override the mode without a protocol change, which is not intended.

**Contrast with Beam Diameter and Beam Current**, which are D=Editable: those are tunable operating parameters that the protocol specifies as targets and the analyst confirms or fine-tunes. Beam Mode is a categorical choice, not a continuously tunable parameter.

---

### Analysis-level only fields (C=N/A) for spatially determined mapping parameters

**Decision:** Map Dimensions (pixel count in X and Y) and Map Area (physical extent in µm × µm) have C=N/A, D=Basic. Step Size / Pixel Size (spatial resolution) has C=Basic, D=Editable.

**Reasoning:** The protocol specifies *how fine* to map (Step Size = C=Basic — a deliberate resolution design choice). The *extent* of each map — how many pixels and what physical area — is determined entirely at analysis time by the sample feature or region of interest being mapped. A protocol cannot pre-specify which grain boundary or geological texture to map. Map Dimensions and Map Area are therefore analysis-level only (C=N/A, D=Basic): they must be recorded by the analyst but cannot be pre-specified.

**Generalization:** When a mapping parameter is determined by the spatial extent of an arbitrary sample feature chosen at analysis time, it is C=N/A (cannot be pre-specified in the protocol). When it controls the intrinsic spatial resolution of the technique (step size, dwell time), it is C=Basic (a protocol design choice the analyst may adjust within bounds).

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
- EDS Detector Configuration: C=Advanced in EPMA (instrument infrastructure, rarely protocol-defining); C=Basic in TEM (detector geometry — SDD position, window type — is a primary protocol factor for thin-film EDS sensitivity).
- EDS Live Time per Point or Pixel: C=Basic in EPMA (per-point time is a core protocol decision for count statistics); C=Advanced in TEM (acquisition time is secondary to probe current and sample thickness in thin-film EDS; the protocol specifies approximate targets, not binding values).

**Future direction:** As the TAPP family grows to include SEM-EDS and dedicated EDS protocols, consider creating "EDS Acquisition" as a shared module (fields 1–8 above) that is referenced by technique-specific TAPPs, rather than duplicating field definitions. A formal "EDS (bulk)" TAPP (covering EPMA + SEM bulk EDS) and "EDS (thin film)" TAPP (covering TEM/STEM EDS) would enable the quantification fields to be developed properly for each domain without compromising the shared acquisition vocabulary.

---

### "Analytical Mode" as a mandatory Group 4 field — purpose, placement, and distinction from related fields

**Context:** During a cross-TAPP consistency review of SEM_Composition_TAPP_v3 and EPMA_TAPP_v6 (2026-06), it was noted that the two TAPPs treated mode declaration differently. SEM v3 had an "Analytical Mode" field in Group 4; EPMA v6 had "Beam Mode" but no "Analytical Mode". This triggered a broader decision about whether "Analytical Mode" should be universal.

**Decision:** "Analytical Mode" is a mandatory first field in Group 4 (Measurement Information) in every TAPP, regardless of whether the TAPP has one analytical mode or many. It is assigned C=Basic, D=Read-Only, and flagged Y for all modes.

**Reasoning:** The mode flag columns (Y/N per field) answer the question "does this field apply to mode X?" — they serve a filtering and applicability function consumed by the sub-TAPP generation script and by the formatted xlsx view. "Analytical Mode" answers a different question: "what kind of measurement does this protocol describe?" — it is a human-readable declaration consumed by anyone reading a registered protocol record. A protocol registrant must be able to state in one field what the protocol covers. The two structures are complementary, not redundant.

**Why C=Basic, D=Read-Only:**
C=Basic because the analytical mode is the most fundamental protocol-level declaration — omitting it makes the protocol record ambiguous. D=Read-Only because if the analyst changes the mode they are running a different protocol, not adjusting within protocol-defined bounds.

**Allowed values are drawn from the mode flag column labels of that TAPP:**
The controlled vocabulary for "Analytical Mode" must match the mode flag column labels defined in Phase 0. This ensures internal consistency — a protocol that declares "Analytical Mode = WDS Point Analysis" will have all WDS Point Analysis fields marked Y in the mode flag columns, and sub-TAPP generation will include it in a WDS-filtered view. If the mode flag labels change in a future revision, "Analytical Mode" allowed values must be updated to match.

**Distinction from mode-specific sub-strategy fields that coexist with "Analytical Mode":**
Several TAPPs have additional mode-related fields in Group 4 that are NOT replacements for "Analytical Mode":

| Field | TAPP(s) | What it captures |
|---|---|---|
| Beam Mode | EPMA, SEM | Physical beam configuration (focused / defocused / rastered) — independent of analytical mode |
| EDS Acquisition Mode | EPMA, SEM, TEM | Spatial acquisition sub-strategy within EDS (point / linescan / map) |
| Analytical Sub-mode | TEM | Specific technique within a top-level TEM mode (BF-TEM, HAADF-STEM, SAED, PED, etc.) |

These fields describe *how* the measurement is conducted within a declared mode, not *what mode* the protocol targets. All four can coexist in the same TAPP without conflict.

**Retrofitting to existing TAPPs (as of 2026-06):**
The following TAPPs had "Analytical Mode" added during the 2026-06 review:
- EPMA: added in v7
- SEM: already present in v3; retained in v4
- LA-Q:SF-ICP-MS: added in v2
- Lab-XCT: added in v8
- TEM: added in v7
- LA-ICP-MS: added in v12

**Generalization:** Whenever a new TAPP is created, place "Analytical Mode" as the first field in Group 4 with C=Basic, D=Read-Only, allowed values = mode flag column labels. For single-mode techniques, the allowed values list contains one entry and the field still must be present.
