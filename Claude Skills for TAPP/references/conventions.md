# TAPP Conventions

Controlled vocabulary, structural standards, naming conventions, and file management workflow that must be consistent across all TAPPs. These are binding — deviating from them requires explicit decision and documentation.

---

## Vocabulary: Technique / Method / Procedure / Analysis

These terms are aligned with the BIPM/JCGM 200:2012 *International Vocabulary of Metrology* (VIM3) and must be used consistently. TAPP adopts VIM3's definitions directly for Technique, Method, and Procedure; "Analysis" is a deliberately informal working label rather than a VIM3 term in its own right (see the Analysis row below).

| Term | Definition | TAPP relevance |
|---|---|---|
| **Technique** | The principle(s) of a measurement, which describes the phenomenon serving as a basis of a measurement (VIM3 "measurement principle," §2.4) | Names the TAPP (e.g., "LA-ICP-MS TAPP") |
| **Method** | Generic description of a logical organization of operations used in a measurement (VIM3 "measurement method," §2.5) | Use "Method" for assessment methods, calculation methods, and other named component methods (e.g., "Detection Limit Method", "Signal Integration Interval Method") |
| **Procedure** | Detailed description of a measurement according to one or more measurement principles and to a given measurement method, based on a measurement model and including any calculation to obtain a measurement result (VIM3 "measurement procedure," §2.6). Registerable with a DOI | The object captured in TAPP procedure-level columns (C); receives a DOI upon registration |
| **Analysis** | The working, user-facing label for the specific execution of a procedure in an analytical session — what was actually done, including any deviations. Formally corresponds to VIM3 "measurement" (§2.1: "process of experimentally obtaining one or more quantity values that can reasonably be attributed to a quantity"), but "Analysis" is retained throughout TAPP content (e.g., "Analysis-Level Tier") to avoid a same-document collision with Group 4's unrelated "Measurement Information" | The object captured in TAPP analysis-level columns (D) |
| **Measurand** | Quantity intended to be measured (VIM3 §2.3). **TAPP's `reported property` key is the measurand**, and the `Reported Variables and Units` field (Rule 8) enumerates the measurands of a procedure | Distinguishes the *quantity* measured from the *substance* it is measured on — see `analyte` below |
| **Analyte** | The chemical species a measurement is performed on. Not a VIM3 term; standard IUPAC/ISO usage, and the complement of Measurand — the analyte is *what* is analysed, the measurand is *which quantity* of it is obtained | TAPP's `analyte` key (Rule 7.2). Fe is the analyte; ⁵⁶Fe/⁵⁴Fe and [Fe] in µg/g are measurands |

**Key rule:** Use **"Procedure"** when referring to the registerable procedure object. Use **"Method"** only for assessment methods, calculation methods, or named component methods. Never use "Method" as a synonym for the overall registered procedure.

---

## Tier Vocabulary

### Procedure-Level Tier (Column C)

| Value | Meaning | xlsx color |
|---|---|---|
| Basic | Mandatory for procedure registration. Must be provided to register a valid procedure. | Bold red (C00000) |
| Advanced | Optional for procedure registration. Strongly recommended but not required. | Bold green (375623) |
| N/A | Not applicable at procedure level. Analysis-level field only. | Bold (default) |

### Analysis-Level Tier (Column D)

| Value | Meaning | xlsx color |
|---|---|---|
| Read-Only | Directly imported from the registered procedure; cannot be changed by the analyst. Changing this value means running a different procedure. Fields that are relevant only at procedure level (no session-specific variation) are also assigned Read-Only — the value is inherited from the procedure record and displayed in the analysis form. | Bold blue (0070C0) |
| Editable | Imported from the registered procedure but may be adjusted within procedure-defined bounds (e.g., daily tuning, minor software updates). The procedure registers the target or typical value; the analyst confirms or adjusts it. Editable fields with a Basic procedure-level tier cannot be left void. | Bold purple (7030A0) |
| Basic | Mandatory user input at analysis time. Value comes from the analysis itself and cannot be pre-specified in the procedure. | Bold red (C00000) |
| Advanced | Optional user input at analysis time. Recommended for complete documentation. | Bold green (375623) |

**D=N/A is not a valid analysis-level tier.** Every field must carry a meaningful analysis-level assignment. Fields relevant only at procedure level receive D=Read-Only.

---

## Standard Six-Group Structure

Every TAPP uses these six groups in this order. Group names are section header rows — use bold formatting and a distinct fill color on individual cells. **Do not merge cells for section headers**, as merged cells prevent adding or moving rows later.

| Group | Scope |
|---|---|
| 1. Procedure Identification | Administrative and identity fields for the procedure record. Includes fields for both the procedure object (author, DOI, funding for procedure development) and the analysis record (analyst, session dates, funding for the analysis campaign). Also includes coupling fields documenting any co-registered techniques applied to the same sample. Largely transferable across TAPPs; minor technique-specific additions. Group 1 is **composed** from `modules/Module_Group1.csv` in every TAPP (Rule 6); that module is the canonical field list, tier assignments and descriptions. Do not hand-edit Group 1 in a TAPP — edit the module and recompose. |
| 2. Samples | Target material type (procedure scope), sample form and preparation method (procedure), and per-analysis sample identity (sample name, persistent identifier such as IGSN). Procedure fields describe what the technique is designed to measure; analysis fields identify what was actually analyzed. |
| 3. Instrument & Software | Hardware configuration — the instruments, detectors, and ancillary components used — and the software for acquisition and data reduction. Applies to all measurement techniques: spectrometers, diffractometers, imaging systems, sensors, etc. Hardware fields (instrument manufacturer, model, detector configurations) are D=Read-Only since changing hardware constitutes a different procedure. **Software fields (acquisition software, data reduction software) are D=Editable** — a minor version update does not constitute a new procedure, so analysts may record the version actually used. |
| 4. Measurement Information | Instrument operating conditions and tuning parameters, acquisition settings (timing, spatial, spectral, or other measurement parameters), and the identity of what is being measured (chemical variable, spectral range, physical property, imaging parameter, etc.). The most technique-specific group and typically the largest. |
| 5. Data Processing | Data reduction strategy including calibration and standardization approach, signal or data selection and integration, correction procedures (interferences, matrix effects, drift), normalization, and uncertainty propagation. Mix of procedure-level design choices and analysis-level outcomes. |
| 6. Quality Control & Uncertainty | Reference materials used, detection and quantification limits, precision, and accuracy. Procedure-level fields describe the QC design; analysis-level fields record QC outcomes from the actual session. **Primary calibration standards and secondary reference materials are C=Basic, D=Editable**: the procedure commits to a set of reference materials (mandatory to specify), but material exhaustion or availability may require the analyst to use a substitute at analysis time. |

### Blank rows between groups

One blank row separates each group from the next. Do not use more than one blank row. Blank rows have no content in any column.

---

## Mode Flag Columns

Mode flag columns start at column I (immediately after H, Last Update) and extend one column per analytical mode. The number of mode flag columns and their labels are defined in Phase 0 (Technique Scoping) and remain fixed for the lifetime of the TAPP.

**Single-mode techniques** (e.g., solution ICP-MS): use one mode flag column, or omit mode flag columns entirely if the technique has no meaningful sub-modes.

**Multi-mode techniques** (e.g., LA-ICP-MS with spot/transect/mapping): one column per mode, labeled with the mode name in the header row.

After the last mode flag column, insert one **sentinel column** whose header cell contains exactly `Literature Assessment` (all data rows in this column are empty). The sentinel marks the boundary between mode flag columns and literature assessment columns, allowing the export script to detect the boundary reliably without relying on header length heuristics. Group header rows must have N in the sentinel column (consistent with mode flag column treatment).

The literature assessment columns begin immediately after the sentinel column. Their starting column letter therefore depends on the number of modes and is not fixed across TAPPs.

**Backward compatibility:** TAPPs created before the sentinel convention are still processed correctly — the export script falls back to a length-based heuristic if no sentinel column is found.

### Mode flag values

| Value | Meaning |
|---|---|
| Y | This field applies to this mode and should be reported |
| N | This field is not applicable to this mode |

N/A is **not** a valid value in mode flag columns. Use N for "not applicable to this mode."

### Section header mode flags

Group header rows must have N in all mode flag columns to prevent them from appearing in mode-filtered views.

---

## Coupled Analysis Fields (Group 1 Standard)

Every TAPP includes four standard coupling fields at the end of Group 1, after Procedure Reference(s). These document multi-technique workflows where the same sample or aliquot is analyzed by more than one technique and the results are designed to be interpreted together or where one technique provides input to another.

| Field | C tier | D tier (default) | Notes |
|---|---|---|---|
| Coupled Technique(s) | Advanced | Editable | Technique-specific TAPPs may adjust D tier; most procedures are not always coupled |
| Coupling Description | Advanced | Editable | Free text; must address both the functional relationship and the analytical sequence |
| Coupled Procedure DOI | N/A | Advanced | Analysis-level only; may be "pending" or point to a publication DOI if no procedure registered |
| Coupled Dataset or Publication Reference | N/A | Advanced | Accepts dataset DOI, shared DOI, publication DOI, "same submission", or "pending"; computationally mandatory couplings may warrant D=Basic in specific TAPPs |

**D tier is case-by-case per TAPP.** The defaults above apply to most techniques; individual TAPPs may promote fields to Basic when the coupling is computationally mandatory (e.g., for (U-Th)/He geochronology, where U/Th from ICP-MS and He from noble gas MS must be combined to calculate an age).

**The Coupling Description must address two aspects:**
1. *Functional relationship*: what data or context flows between techniques (e.g., "EPMA SiO₂ concentration used as internal standard in LA-ICP-MS data reduction")
2. *Analytical sequence*: which technique is performed first and why (e.g., "EPMA before LA-ICP-MS because LA-ICP-MS ablation is destructive")

**The Coupled Dataset or Publication Reference** does not replace the Sample Persistent Identifier (Group 2). If coupling is documented only through a shared sample IGSN, the IGSN in Group 2 is sufficient and this field may be "None".

---

## Cross-TAPP Consistency Rules

These rules govern fields and naming decisions that span multiple TAPPs. They are binding for all new TAPPs and must be applied retroactively when an existing TAPP is revised. Deviations require explicit documentation in `references/precedents.md`.

---

### Rule 1 — Shared field names for universally common fields

The following fields appear in virtually every TAPP and must use identical names, descriptions, tier assignments, and (where applicable) controlled vocabulary across all TAPPs. If you need to add or modify any of these fields, the change must be propagated to every TAPP that contains them.

**Group 1 (Procedure Identification) — all fields**
Group 1 is fully cross-TAPP and is composed from `modules/Module_Group1.csv` (Rule 6). Rename, reorder or re-tier a Group 1 field by editing the module and recomposing every TAPP — never by editing a TAPP directly.

**Group 2 (Samples) — two shared fields**
| Field | Standard name |
|---|---|
| Target material scope | Target Material |
| Sample preparation | Sample Preparation Method |

Technique-specific Group 2 additions (e.g., "Sample Mount Type", "Carbon Coat Thickness") are permitted but must not replace or rename the two shared fields above.

**Group 3 (Instrument & Software) — software field names**
The two generic software fields must use these exact names across all TAPPs:

| Field | Standard name | Tier |
|---|---|---|
| Software that runs/controls acquisition | **Acquisition Software** | C=Basic, D=Editable |
| Software that reduces/processes data after acquisition | **Data Reduction Software** | C=Basic, D=Editable |

Technique-specific software fields are permitted (e.g., "Reconstruction Software", "SAED Pattern Simulation Software") and should use descriptive names that make their function clear. They do not replace Acquisition Software and Data Reduction Software unless the technique genuinely has no separate acquisition step.

**Group 6 (Quality Control & Uncertainty) — shared QC terms**
| Standard field name | Do not use |
|---|---|
| Primary Calibration Standard Name | Primary Standard, Calibration Material |
| Secondary Reference Materials | Secondary Standard, Monitor Material |
| Interference Corrections Applied | Spectral Interference Correction |
| Detection Limit | LOD, Limit of Detection |
| Analytical Precision | Precision |
| Analytical Accuracy | Accuracy |
| Counting Statistics Error | Counting Error, Statistical Error |

---

### Rule 2 — Shared field names and mode assignments for the same detection/analytical mode on different instruments

When the same detection modality (e.g., EDS, WDS, CL, EBSD) is implemented on multiple instruments covered by separate TAPPs, the fields describing that modality must use identical names, descriptions, tier assignments, and mode-flag values across those TAPPs. The only permitted divergence is in fields where the physics or operational practice genuinely differs between instruments.

**Examples of correctly shared fields (EDS across EPMA and SEM):**
- EDS Detector Configuration — same name, same tier (C=Advanced, D=Read-Only), same mode flags
- EDS Live Time per Point or Pixel — same name, same tier, same mode flags
- EDS Acquisition Mode — same name, same tier, same mode flags
- EDS Spectral Processing Type — same name, same tier, same mode flags
- EDS Dead Time — same name, same tier, same mode flags

**Examples of permitted divergence (EDS on EPMA vs. SEM vs. TEM):**
- EPMA and SEM: bulk-matrix ZAF/φρz correction framework (shared)
- TEM: thin-film Cliff-Lorimer / ζ-factor framework (different physics → different quantification fields)
- If divergence is large enough, consider a dedicated sub-TAPP or separate TAPP rather than forcing divergent fields into a shared mould

**Workflow for cross-TAPP mode harmonization:**
When adding or revising EDS, WDS, CL, EBSD, or any other shared modality field in one TAPP, explicitly check whether the same field exists in other TAPPs that share that modality and whether the same change should propagate. Document the harmonization decision in `references/precedents.md` if a divergence is intentionally retained.

---

### Rule 3 — "Analytical Mode" field is mandatory in Group 4 of every TAPP

Every TAPP must include an **"Analytical Mode"** field as the first field in Group 4 (Measurement Information), regardless of whether the technique has one mode or many.

**Canonical definition:**
- Field name: `Analytical Mode`
- Procedure-Level Tier: Basic
- Analysis-Level Tier: Read-Only
- Data Type: `Controlled list` (the value used in Column E; "Controlled vocabulary" is not a valid Data Type label — see Data Type Vocabulary below)
- Mode flags: Y for all modes defined for that TAPP
- Allowed values: exactly the mode flag column labels defined in Phase 0 for that TAPP (e.g., "Spot", "Transect", "Mapping" for LA-ICP-MS; "Single-volume", "Multi-volume stitching" for Lab-XCT)
- For multi-mode procedures: list all applicable modes separated by semicolons

**Purpose and distinction from mode flag columns:**
"Analytical Mode" is a procedure-level *declaration* — a human-readable statement of what kind of measurement the procedure covers, required for any user reading or registering the procedure. The mode flag columns (Y/N per field) serve a different function: they indicate which fields apply to which mode and drive filtered sub-TAPP views. These two structures are complementary, not redundant.

**Distinction from mode-specific sub-strategy fields:**
"Analytical Mode" declares the top-level mode. Some TAPPs also have mode-specific sub-strategy fields that coexist with it:
- "Analytical Sub-mode" (TEM) — records the specific technique within a TEM mode (BF-TEM, HAADF-STEM, SAED, PED, etc.)
- "EDS Acquisition Mode" (SEM, EPMA, TEM) — records the spatial acquisition sub-strategy within EDS (point, linescan, map)
- "Beam Mode" (EPMA, SEM) — records the physical beam configuration (focused, defocused, rastered)

These are not replacements for "Analytical Mode" and should not be confused with it.

**Single-mode techniques:** Even if a technique has only one possible mode (e.g., a technique with a single fixed acquisition geometry), include "Analytical Mode" so that procedure records are self-describing and consistent across the TAPP library.

**"Analytical Mode" allowed values must mirror the mode flag column labels exactly:**
The controlled vocabulary for "Analytical Mode" must use the exact strings that appear as mode flag column headers in that TAPP (defined in Phase 0). Do not paraphrase, abbreviate, or substitute synonyms. Because this correspondence must be exact, `Analytical Mode` is **exempt** from the requirement that every Controlled list field offer `N/A | None` — see the exemption table in the Data Type Vocabulary section. This ensures that a procedure declaring `Analytical Mode = WDS Point Analysis` is unambiguously linked to the `WDS Point Analysis` mode flag column, and that sub-TAPP filtering behaves correctly. If mode flag column labels are ever renamed in a future revision, the "Analytical Mode" allowed values must be updated in the same patch.

> **Enforced from 2026-08-24 — `check_analytical_mode_vocabulary` (`rule3-mode-vocab`, WARN).** Only
> the *placement* half of Rule 3 was ever checked (Analytical Mode must be first in Group 4); the
> vocabulary half above was documented and unenforced, and the four SEM tables had drifted to an
> informal vocabulary — SEM offered `EDS | SEM-WDS | CL` against mode columns naming
> `EDS Point Analysis`, `EDS Mapping`, `WDS Point Analysis`, `WDS Mapping`, `CL Point Analysis`,
> `CL Mapping`, plus the generic options this rule exempts it from.
>
> **The cost was not internal.** Curators enter publication values from this list, so a bad Column F
> generates bad data: it produced **84 invalid `Analytical Mode` publication cells**, reported from
> outside as `amds-ldeo/tapp#3` by a consumer generating `ada:analyticalMode` as an enum from the
> mode-flag headers. A controlled list is not only a constraint on the field — it is an instruction
> to whoever fills it, and an informal one propagates.
>
> Third time this pattern has been recorded (7.8.7 keys, 7.8.10 Data Types, now Rule 3 vocabulary):
> **a documented invariant is not an enforced one.** When a rule says the validator "must enforce"
> something, confirm the check exists.

---

### Rule 4 — Propagation obligation when a shared field is modified

Whenever a field covered by Rules 1–3 is added, renamed, re-tiered, or has its description substantively changed in any one TAPP, the author is obligated to propagate that change to every other TAPP that contains the same field **in the same patch or revision cycle**. Deferred propagation is not permitted — it creates silent inconsistency across the library.

**Scope narrowed by Rule 6.** This rule governs shared content that is still *copied* between TAPPs. Content held in a module and composed into consumers is exempt — there is nothing to propagate, because the field exists in exactly one place. See Rule 6.7. Naming and structural constraints that cannot be factored into a module (Rule 1's controlled vocabulary, for example) remain under this rule, and are best enforced by `scripts/validate_tapp.py` rather than by manual propagation.

**Steps:**
1. Identify all TAPPs that contain the field being changed (search across all `*_TAPP_v*.csv` files).
2. Apply the change to each affected TAPP, incrementing its version number.
3. Document the propagation in the patch script header listing all files modified.
4. If a specific TAPP intentionally diverges (Rule 2 permitted divergence), record that decision in `references/precedents.md` rather than silently omitting the propagation.

---

### Rule 5 — "Constants and Reference Values Used" field is mandatory in Group 5 of every TAPP

Every TAPP must include a **"Constants and Reference Values Used"** field as the last field in Group 5
(Data Processing), regardless of whether the technique's data reduction depends on citable physical
constants.

**Canonical definition:**
- Field name: `Constants and Reference Values Used`
- Procedure-Level Tier: Basic
- Analysis-Level Tier: Editable
- Data Type: Text (free)
- Placement: last field in Group 5, immediately before the blank separator row preceding Group 6
- Mode flags: Y for all modes defined for that TAPP (field is universal, not mode-restricted)
- Description: "Physical constants and reference values used in data reduction to calculate the final
  reported quantity (e.g., decay constants for age calculation, standard isotope ratios, or other citable
  reference values used in a correction or calculation), together with their source. Distinct from
  Reference Material Information / Secondary Reference Materials (Group 6), which document accepted values
  for specific calibration/validation materials rather than universal physical constants. Record 'None' if
  no citable, revisable physical constants feed into this procedure's data reduction."

**Purpose:** traceability of any reported quantity that depends on external, periodically-revised physical
constants. A reported value can only be correctly reinterpreted against a future revision of such a
constant if the constant originally used is documented. Most consequential for geochronology (decay
constants; the ²³⁸U/²³⁵U ratio, revised by Hiess et al. 2012 after decades of assumed-constant 137.88) but
written generally, since any technique's data reduction could in principle depend on a citable constant.

**Why C=Basic:** mandatory declaration, mirroring Rule 3's Analytical Mode — the field's universal presence
is itself informative, distinguishing "deliberately none" from "not asked."

**Why D=Editable:** the constants in use are embedded in the data-reduction method; documenting a revision
between procedure registration and a later session shouldn't require a new procedure (same logic as the
Group 3 software fields, D=Editable).

**Scope decision (2026-07-28):** applied universally to every TAPP, including pure-imaging/morphology
techniques (which record "None") — not scoped only to techniques with plausible constant-dependent data
reduction. This matches Rule 3's own precedent that even single-mode/non-applicable cases still get the
field, for the same reason: field presence itself is informative.

**Retrofitting to existing TAPPs (as of 2026-07-28):** EPMA (v8→v9), LA-Q/SF-ICP-MS (v4.1→v5), SEM (v5→v6),
SEM_Composition (v5→v6), SEM_Imaging (v5→v6), SEM_FIBSEM (v5→v6), Solution MC-ICP-MS (v3→v4), Solution
Q-ICP-MS (v6→v7), Solution SF-ICP-MS (v6→v7), TEM (v8→v9), Lab-XCT (v9→v10). Did not touch the stale,
frozen `LA-ICPMS_TAPP_v13.csv` branch (see `reference_la_icpms_lineage.md`).

---

### Rule 6 — Modules: shared field blocks held in one place and composed into TAPPs

A **module** is a block of fields shared by more than one TAPP, held in a single source file and
**composed** into each consuming TAPP by script rather than copied into it by hand. Modules exist
because Rule 4 — the obligation to propagate a change to every TAPP containing a shared field — has
demonstrably failed in practice: `Funding Source for Procedure Development` drifted in 3 of 13 TAPPs
despite being a Group 1 field squarely inside Rule 4's scope, and 14 of 17 Group 1 descriptions in
LA-Q/SF-ICP-MS diverged from the template unnoticed. Composition replaces a rule that depends on
discipline with a property that holds by construction.

---

#### 6.1 Admission test — when something becomes a module field

A field belongs in a module only if **both** conditions hold:

1. **Recurrence** — it is required by more than one TAPP, or by more than one technique's community
   reporting standard.
2. **Specificity** — it is *not* already present in the library under another name, and not an
   instance of a more general field that should hold it instead.

**Condition 2 is the one that gets missed.** Applying it during the geochronology work removed a
field or reframed one on four separate occasions:

| Candidate | Failed because | Resolution |
|---|---|---|
| 9 "general geochronology gaps" | 3 were already covered by existing field descriptions | description harmonization, not new fields |
| `Age Model and Software` | the software half collided with `Data Reduction Software` (Rule 1) | narrowed to `Age Model` |
| `Discordance Assessment and Filter` (U-Pb) | the filter half duplicated a general inclusion field | narrowed to `Discordance Definition and Values` |
| `Radiogenic to Common Pb Ratio (Pb*/Pbc)` (U-Pb) | Ar-Ar's `%40Ar*` is the same quantity | promoted to a Layer 2 field both systems overlay |

Before adding any module field, search the library for near-matches by concept as well as by name
(`validate_tapp.py` reports cross-TAPP name variants), and read the descriptions of what you find.
"Recurs across techniques" is necessary but not sufficient.

---

#### 6.2 Layers

| Layer | What it holds | Examples |
|---|---|---|
| **1 — Instrument TAPP** | the technique itself: Groups 1–4 and technique-specific parts of 5–6 | LA-Q/SF-ICP-MS, TIMS, SEM |
| **2 — Cross-technique module** | fields shared across techniques, defining names, tiers and descriptions | `Group1`, `ReportingCore`, `Geochronology` |
| **3 — System module** | per-system examples and allowed values for Layer 2 fields, plus system-specific extension fields | `UPb`, `ArAr` |

A registered procedure is **Layer 1 × Layer 2 × Layer 3**. Layer 3 must be composed *after* the Layer
2 modules it overlays; composing it first produces a `MISSING from source` report naming the fields
it could not find.

Layers are a property of how a module is used, not a separate mechanism: a Layer 3 module is simply
one whose `overlay_columns` differ from its `owned_columns`.

---

#### 6.3 Module files

Each module is two files in `modules/`:

| File | Contents |
|---|---|
| `Module_<Name>.csv` | the field block, in standard TAPP column order A–H; module-owned columns populated, consumer-owned columns empty |
| `Module_<Name>.json` | the manifest: ownership, placement, applicability, provenance |

Manifest keys:

| Key | Meaning |
|---|---|
| `owned_columns` | columns the module supplies for fields **it introduces**; these overwrite the source |
| `overlay_columns` | columns the module supplies for fields **another module introduced**; defaults to `owned_columns` |
| `blocks` | one or more insertion blocks, each with `name`, `target_group`, `placement`, optional `anchor_field`, `applies_when`, and `fields` |
| `placement` | `replace_group` (module supplies a whole group), `insert_before` (insert at `anchor_field`), or `append_to_group` |
| `mode_flag_default` | flag value for fields the module adds; a module cannot know its consumer's mode set |
| `requires` | modules that must be composed first |

**A module never supplies mode flag columns or the sentinel column** for existing fields — it cannot
know how many modes a consumer defines. For new fields the composer writes `mode_flag_default`, which
the consumer may then correct.

---

#### 6.4 Column ownership

The default split, already the de facto contract of `Template TAPP Group 1.csv`:

| Columns | Owner | Rationale |
|---|---|---|
| A Metadata Item, B Description, C Procedure Tier, D Analysis Tier, E Data Type, **I Keyed By** | **module** | these are what must not drift |
| F Example / Allowed Content | **consumer** (or the Layer 3 module) | examples are technique- and system-specific |
| G Comments, H Last Update | **consumer** | local annotation and edit history |
| mode flags, sentinel, literature assessment | **consumer** | unknown to the module |

This split is what makes an abstract field usable. A Layer 2 field may be named
`Calibration Factor and Determination Method`, but an Ar-Ar geochronologist opening the composed TAPP
reads Column F: *"the J value — give the fluence monitor name, its assumed age and reference…"*. The
abstraction lives in the module definition, which is a maintenance artifact, not a user-facing one.

**A module row is not complete until its consumer supplies Column F.** Where the field is a
`Controlled list`, `validate_tapp.py` reports the missing allowed values, so an incompletely composed
TAPP is visibly incomplete rather than silently wrong.

**Where per-TAPP specificity goes — the three-part rule.** Stated because the intuition that a
consuming TAPP should be free to "adjust the wording a little" is natural, recurring, and wrong:

1. **The most general description lives in the module**, and is never edited in a consumer. A module
   description must not name a specific instrument, analyser or technique.
2. **Per-TAPP specificity goes in Column F**, which is exactly what it is for.
3. **If a TAPP genuinely needs a different description**, that is evidence the field fails the 6.1
   specificity test and should not be module-owned at all — see also 6.5 for the conditional case.

Point 1 is not merely a convention; it is enforced. Editing Column B in a composed TAPP makes
`compose_tapp.py --check` report `DIFFERS`, and the **next recomposition silently overwrites the
edit**. A per-TAPP description tweak is therefore not a policy that can be adopted — it is a change
the tooling undoes.

The reason to hold the line is in the record. Field-*name* consistency was already achieved before
Rule 6 and was not sufficient: 14 of 17 Group 1 descriptions in LA-Q/SF-ICP-MS had diverged from the
template unnoticed, under identical field names. Same name, different meaning is worse than different
names, because it is invisible — a search finds them, a diff does not flag them, and a curator
merging two datasets assumes they agree.

---

#### 6.5 Conditional applicability

Unlike Rules 3 and 5, module fields are **not** universal. Where a module's fields apply under
different conditions, group them into blocks, give each block an `applies_when` sentence, and let
consumers select:

```
python3 scripts/compose_tapp.py --source <tapp>.csv --module ReportingCore:aggregation,blank
```

Applicability is controlled by **which blocks a consumer composes**, not by varying tiers. A module
owns columns C and D, so it cannot express "Basic in this TAPP, Advanced in that one". If a field
genuinely needs different tiers in different TAPPs, that is evidence it is two fields, or that it
does not belong in a module.

---

#### 6.6 Composed TAPPs are generated artifacts

**Never edit a composed TAPP directly**, for the same reason the xlsx must never be edited directly:
it is a build output, not a source. Edit the module or the source TAPP and recompose.

- Composition is **idempotent** — recomposing an already-composed TAPP changes nothing.
- `--check` exits non-zero when a TAPP no longer matches what composition would produce; use it to
  detect hand-edits.
- Composition **preserves** consumer-owned columns, mode flags and literature assessment columns,
  matched by field name.
- Composition **refuses** to drop fields the source has but the module does not define, unless
  `--allow-drop` is given.

---

#### 6.7 Relationship to Rule 4

Rule 4 is unchanged in wording but narrows in scope: it governs shared content that is still
**copied**. Content that has moved into a module is exempt, because there is nothing to propagate.

What remains with Rule 4: naming and vocabulary constraints that cannot be factored into a field
block (Rule 1's "use Detection Limit, not LOD"), fields shared by only two or three TAPPs and not
worth a module, and the obligation to document intentional divergence in `references/precedents.md`.

Naming and structural constraints are better enforced by `scripts/validate_tapp.py` than by
propagation, since a linter catches drift the moment it appears rather than relying on an author to
remember.

---

#### 6.8 Verifying a new module

Before a module is used on a production TAPP:

1. **Predict the diff first, then run `--diff`.** The Group 1 pilot predicted a field-order change,
   one tier bug and 14 description divergences; the run produced those plus two unpredicted Data Type
   cells, which turned out to be real improvements stranded in one TAPP. Predicting first is what
   makes an unexpected result visible instead of plausible.
2. **Check row count, not just the diff.** The pilot's cell-level diff looked perfect while the
   composer was silently eating a blank separator row.
3. **Lint the composed output** (`validate_tapp.py --file`), and confirm Rules 3 and 5 still hold —
   a module inserting at the end of Group 5 would displace `Constants and Reference Values Used`
   and break Rule 5. Insert before it, not after.
4. **Compose twice** and confirm the second pass reports `MATCH`.
5. **Compose into a second, structurally different consumer** — one with a different mode-column
   count, or none at all.

---

#### 6.14 Documentation and registers are linted too (2026-08-12)

Every check before this one looked only at TAPPs. A hand audit on 2026-08-12, run because the
library was about to be handed to an outside developer, found three shipped documents describing a
library that no longer existed: `README_TAPP_for_Schema_Generation.md` still defined the analysis
object as one sample, `SKILL.md`'s key list omitted `sample`, and two live registers pointed at
superseded files. Nothing had failed, because nothing was looking.

`check_library_freshness()` in `validate_tapp.py` now covers the gap:

| Finding | Severity | Meaning |
|---|---|---|
| `doc-stale-version-ref` | WARN | a live document names a TAPP file that has been superseded |
| `doc-retired-field` | WARN | a live document names a field that was retired or renamed |
| `register-stale-module-version` | WARN | `TAPP_Module_Register.csv` disagrees with a module manifest |
| `register-stale-consumers` | WARN | its consumer count disagrees with `composed_tapps.json` |

**What counts as "live".** A prose document (`.md`) or one of the named live registers, unless it is
a **dated record** — a date in the filename, or an entry in `HISTORICAL_DOCS`. A dated record is
*correct* to name the state at its date, so the lint leaves it alone. TAPP CSVs are excluded
entirely: they are data, and every superseded Lab-XCT version legitimately still carries a retired
field as one of its rows.

**Two registers must be maintained by hand, and they are the price of the check.** `RETIRED_FIELDS`
gains an entry whenever a field is retired or renamed — that entry is what lets the check find every
document still naming it. `RETIRED_FIELD_MENTION_OK` exempts the files whose job *is* to name
retirements: `precedents.md` and `conventions.md`, where a retirement going unrecorded would be the
actual defect.

**Run it before handing the library to anyone**, not only before a version bump. The failure this
catches is not a malformed TAPP — it is a correct library described by an out-of-date guide, which is
worse, because the reader has no way to tell.

---

#### 6.13 A module's version lives in two places and they must agree (2026-08-12)

`Module_X.json` carries `"version"`; `composed_tapps.json` records a version for X against every
consuming TAPP. **Nothing checked that they agreed, and both existing divergences had gone
unnoticed for as long as they had existed:**

| Module | Manifest said | Register recorded | Resolution |
|---|---|---|---|
| `ReportingCore` | 3 | v4 × 16 consumers | → **5**, skipping 4 (a content change landed in the same pass, and 4 was already claimed by a different state) |
| `MCICPMS` | 3 | v4 × 3 consumers | → **4**, no content change |

**Which one gives way.** The register is written per TAPP by the composition tooling; the manifest
is hand-edited. The hand-edited one is the likelier to have been missed, so **the manifest is
brought into line with the register**, with the reason recorded in its `decisions` list. Where the
same pass also changes module content, skip past the register's claimed version rather than
colliding with it — a version number must not name two different content states.

**Enforced** by `check_module_versions()` in `validate_tapp.py`:

| Finding | Severity | Meaning |
|---|---|---|
| `module-version-drift` | WARN | manifest and register disagree |
| `module-unused` | INFO | a module in `modules/` is composed into no TAPP |
| `module-version-unreadable` | WARN | the manifest or the register could not be parsed |

`module-unused` is INFO because building a module ahead of its technique is legitimate under 6.10 —
`Module_ArAr` is at v4 with no Ar-Ar TAPP yet. It is reported rather than ignored so it cannot sit
unnoticed if the TAPP *was* expected.

This is another instance of what 7.8 records at length: **a documented invariant is not an enforced
one.** Rule 6 has always implied the two version records agree; nothing made them.

---

#### 6.9 Status and open items (as of 2026-08-10)

**Eight modules exist, and the production library is composed.** The narrative record of the
migration is the `2026-08-08 | CROSS-TAPP | Module architecture (Rule 6)` entry in
`TAPP_Development_Log.md`.

> **Superseded in part — this table is a 2026-08-10 snapshot.** The live record is
> `Project Files/Registers & Planning/TAPP_Module_Register.csv`. Since it was written: consumers rose
> from 14 to 16; on **2026-08-14 `ReportingCore` was dissolved** into `TargetSelection` (2 fields, 13
> consumers), `CalibrationFactor` (1, 14), `Blank` (1, 12) and `Aggregation` (2, 13), leaving no
> conditional module in the library; and on **2026-08-14 `Group1` was retired into `Module_Core`** (28 fields, 6 blocks,
> v1, 16 consumers) — its 18 fields plus the 10 universals that belonged to no module. `Core` is
> unconditional and all-or-nothing; the retired files are in `Archive/Superseded Modules/`. Composition
> was a no-op (`--check` MATCH on all 16) because the five divergent definitions were reconciled
> *before* the module was built, which is why `Core` ships at v1 and its consumers did not churn.

| Module | Layer | Fields | Blocks | Ver | Consumers |
|---|---|---|---|---|---|
| `Group1` *(retired 2026-08-14 → `Core`)* | 2 | 18 | 1 | 2 | 14 |
| `ReportingCore` *(dissolved 2026-08-14 → 4 modules)* | 2 | 6 | 5 | 1 | 14 |
| `LaserAblation` | 2 | 18 | 3 | 1 | 4 |
| `MCICPMS` | 2 | 15 | 3 | 2 | 3 |
| `SolutionIntroduction` | 2 | 16 | 3 | 1 | 3 |
| `Geochronology` | 2 | 6 | 1 | 2 | 2 |
| `UPb` | 3 | 15 | 2 | 2 | 2 |
| `ArAr` | 3 | 16 | 2 | 1 | 0 |

`Project Files/Registers & Planning/TAPP_Module_Register.csv` is the current register. `composed_tapps.json` records which modules and
versions each TAPP was built from, and which TAPPs have been retired.

**Settled since this rule was written:**

- **Content reconciliation before migration** is confirmed necessary and now has a worked method.
  The Group 1 pass produced `Archive/Worksheets (reconciled)/Group1_Reconciliation_Decisions.csv` — a field-by-field record of which
  variant won and why — and changed 11 of 17 descriptions away from the template. Harvest before
  composing, always.
- **That reconciliation cannot be automated.** Selecting among clean candidate descriptions by
  keyword proxy was attempted for `SolutionIntroduction` and failed: 14 of 16 fields scored
  identically and selection fell back to one source by default. Only the *disqualifiers* automate
  (source leaks, technique-specific leakage). Selection requires reading.
- **Description length is not a quality proxy.** Three of the four things that lengthen a description
  make it worse for a module. The `description-source-leak` check in `validate_tapp.py` exists
  because of this.
- **Literature assessment cell loss on group-header rows** was a real composer bug (190 cells) and is
  fixed. Cells survive composition for fields that already exist.

**Still unsettled:**

- ~~**Provenance is recorded but not enforced.**~~ **Largely resolved 2026-08-14.**
  `compose_tapp.py` now **writes** `composed_tapps.json` whenever `--out` produces a versioned TAPP
  inside the library: the tool that performs the composition is the one that knows it happened, so it
  is the one that records it. It carries a same-stem entry forward to the new version, preserving
  `derived_from`, notes and open items, and adds or updates only the modules named on the command
  line. `--no-record` opts out. Two guards keep the register clean: an output path outside the library
  root, or one whose filename is not `*_TAPP_v<N>.csv`, is **not** recorded — composing to a scratch
  path while testing is normal and must not touch the register.

  `TAPP_Module_Register.csv` is now **generated** by `Project Files/Scripts/build_module_register.py`
  (`--check` / `--apply`). Every column but `Status` is derived: `Layer`, `Title` and `Version` from
  the manifest, `Fields` and `Blocks` from the module CSV and manifest, `Consumers` from
  `composed_tapps.json`. **Rows for retired modules are carried through untouched** — an archived
  module has no manifest to regenerate from, and that row *is* the retirement record.

  Building the generator immediately found the gap this rule's next-but-one bullet predicted:
  `Module_Geochronology.json` had never carried a `layer` key, so the derived column came out empty
  where the hand-maintained register had `2`. The manifest was completed rather than the generator
  taught to guess. `Fields` deliberately counts **named rows**, not introduced fields, because that is
  what the column has always meant and what README §9 publishes — for the two Layer 3 modules it
  therefore includes overlay rows (ArAr introduces 4 and overlays 12; UPb introduces 3 and overlays
  12), and silently redefining a published number would be worse than the imprecision.

  What remains open: a composed TAPP still makes no **self-declaration** — you cannot ask a CSV what
  built it without consulting the register. The discipline in 6.6 no longer rests on someone
  remembering to update a file, but it does still rest on the register being the only witness.
- **Module versioning has no increment rule.** Manifests carry a `version` and the build record now
  names it, but nothing defines when to bump it and nothing verifies a recorded version against the
  module's current content.
- **Manifests have no schema.** `Group1` and `Geochronology` omit `layer`; `Group1` and
  `ReportingCore` omit `consumed_by`; `Group1` and `Geochronology` omit `blocks`. The register
  supplies these values, so nothing has broken, but the JSON is not validated against anything.
- **Field removal by a module is untested.** Behaviour when a module does not define a field the
  source has is still blocked by the drop guard rather than handled by design.
- ~~**`SolutionIntroduction` is provisional.**~~ **Resolved 2026-08-10.** All 16 descriptions are
  reconciled and the module is at version `1`. Decisions are recorded field by field in
  `Archive/Worksheets (reconciled)/SolutionIntroduction_Reconciliation_Decisions.csv`, and Column F is complete in all three
  consumers, satisfying the 6.4 condition. The methodological finding stands: the selection criteria
  are sound but not automatable by keyword matching — only the disqualifiers automate.
- **`ArAr` has no consumer.** It is built and verified but unconsumed, awaiting a Noble Gas MS TAPP.
  Per 6.10 its specificity is therefore only as good as its two-system extraction.
- **Two requested modules were deliberately not built.** Q-ICP-MS and SF-ICP-MS residues are 2 and 4
  fields, below the five-field threshold in 6.10. There is also no possible "sector-field" layer:
  **0** fields are shared by SF and MC but not Q.

---

#### 6.10 When to extract a module — modules are extracted, not invented

**Do not create a module from a single instance.** You cannot tell what is general from one TAPP, and
the failure mode is not hypothetical: every specificity failure recorded in 6.1 came from generalising
too early. The most instructive is `Pb*/Pbc`, which sat in the U-Pb module as a U-Pb-specific field
until Ar-Ar was built and `%40Ar*` turned out to be the same quantity. No amount of re-reading the U-Pb
module would have revealed that — only the second instance did.

**Extraction trigger.** Extract a module when *all* of the following hold:

1. A **second** TAPP needs a block of fields an existing TAPP already has.
2. The block is **ten or more placements** — fields × consuming TAPPs. Below that, Rule 4
   propagation is cheaper than a module, and the tooling overhead is not repaid.
3. The block is **coherent** — it corresponds to a real component (an instrument subsystem, a
   detection modality, a reporting standard), not an arbitrary grouping of leftovers.
4. The block is **not a sub-module of an existing module** — see 6.15.

**Why placements rather than fields (amended 2026-08-14).** Condition 2 read "five or more fields"
until the `ReportingCore` dissolution required one- and two-field modules to be legitimate. The
rationale was never field count as such: it is that Rule 4 propagation must cost more than the module
machinery, and propagation cost is the number of **copies to keep in sync** — fields multiplied by
consumers, not fields alone. A one-field module with fourteen consumers is fourteen copies; a
five-field module with two consumers is ten. Ten placements is the *same* calibration point the old
rule used — five fields across the two TAPPs of condition 1 — restated so it scales with consumer
count instead of ignoring it.

The amendment does not reopen past decisions. The two residues 6.9 declined to build remain below the
threshold: `Signal Collection Mode` (1 field × 3 TAPPs = 3 placements) and `E-scan Range` +
`Triple Scanning Mode` (2 × 3 = 6). The five modules of the `ReportingCore` dissolution score 26, 14,
12, 26 and 13.

**The threshold is a floor, not a licence.** Lowering it makes small modules possible, not desirable;
condition 4 is what stops the floor from becoming a slope.

**Prefer three instances to two.** Two TAPPs give you a shared set; three tell you which parts of it
are actually stable. Where a third consumer is foreseeable and near, record the block as a
`generalisation_candidate` in the manifest of the module that first surfaces it, and extract once the
third arrives. `Module_ArAr` carries three such candidates (neutron irradiation, stepped heating,
interference production ratios) for exactly this reason.

**Strategic consequence.** Because modules are extracted rather than invented, module development
cannot run ahead of TAPP development — it is downstream of it. Build TAPPs where no precedent exists;
extract when the second instance appears. The highest-value TAPPs to build next are therefore the ones
that *trigger extractions*, not the ones that are easiest to compose.

**Reconciling divergent versions during extraction.** A block being extracted usually exists in two or
more TAPPs with different text. Choosing between them is where extraction goes wrong.

**Do not rank candidates by length.** Length correlates with quality only loosely, and three of the
four things that lengthen a description make it *worse* for a module: literature-assessment commentary,
technique-specific examples that belong in Column F, and plain verbosity. On 2026-08-08 two candidate
laser descriptions were 3× longer than the incumbent and were nearly adopted; the extra length was
entirely provenance notes about Horstwood's Table 3.

Judge a candidate description against what a module description is *for*:

| Test | A better description… |
|---|---|
| Definition | says what the field is, in terms a non-specialist in that technique can act on |
| Boundary | distinguishes it from adjacent fields it could be confused with |
| Instruction | says what the registrant must record — not what some paper happened to record |
| Neutrality | is technique-neutral; naming a specific technique disqualifies it from a module-owned Column B |
| Cleanliness | carries no examples (Column F) and no source commentary (literature assessment columns) |

The last two are machine-checkable and the linter enforces them: `description-source-leak` flags text
describing what a source document contains. Run `validate_tapp.py` on the candidate TAPPs *before*
comparing descriptions, and disqualify anything it flags. Automate the disqualifiers; read what
survives. A linter cannot tell you which of two clean descriptions is scientifically better.

Tiers are reconciled separately from descriptions and on different evidence — a TAPP may have the
better wording and the worse tier. Both laser-module exceptions of 2026-08-08 were of this kind.

**Worked example (2026-08-08).** The Phase 0 coverage audit for LA-MC-ICP-MS found that 63 of its
fields are shared between LA-Q/SF-ICP-MS and Solution MC-ICP-MS, 18 more are the laser front end held
only in LA-Q/SF, and 13 are the multi-collector analyser held only in Solution MC-ICP-MS. Both blocks
met the trigger, so both were extracted before LA-MC-ICP-MS was composed. The MC analyser block had
unusually strong evidence: those same 13 fields had been independently identified months earlier as the
MC-only content of the LA-ICP-MS Geochronology TAPP — two derivations converging on the same set.

---

#### 6.15 The sub-module test — is this really a new module? (2026-08-14)

Lowering condition 2 to a placement count makes small modules legitimate, and the failure mode that
opens is **proliferation**: a library of one-field modules nobody can navigate, in which 6.1's
specificity condition can no longer be checked from memory. **Every proposed module is therefore
tested against the existing ones before it is built**, and the answer recorded.

Two prongs, in order.

**1. Footprint — mechanical.** Compare the proposed module's consumer set against every existing
module's:

| relation | reading |
|---|---|
| **identical** | the two would always be composed together — candidate for merger |
| **proposed ⊂ existing** | the proposal is a part of the existing module — candidate for absorption |
| **existing ⊂ proposed** | the existing module is a part of the proposal — absorption the other way |
| **overlapping, neither contained** | genuinely independent — proceed |

**2. Subject — judgment.** Where prong 1 nominates a candidate, ask: *reading only the two module
titles, could a registrant say which one a given field is in?* If not, they are one module.

**Resolution: merge unless the subject test separates them.** Footprint identity is common — several
unrelated conditions in this library select the same set of TAPPs — so it nominates, it does not
decide. Coherence (condition 3) is what decides.

**Worked example.** `Analyte` was proposed as its own module with 13 consumers. `Aggregation` also has
13, and they are the **same** 13 — every TAPP that determines a chemical composition. Prong 1
nominated a merger; prong 2 refused it. "Which chemical species does this procedure determine" and
"which analyses contribute to the reported value" are not one subject, and a registrant hunting for
the analyte list would not open a module about aggregation. They stay separate.

The lesson generalises: **co-extension is not coherence.** Those two conditions select the same TAPPs
because determining a composition and aggregating analyses happen to co-occur across this library's
techniques, not because they are one component. A third technique will eventually separate them, and
a merged module would then have to be split — the expensive direction, per 6.10's `Pb*/Pbc` precedent.

**Record the answer** in the manifest as `sub_module_test`: which modules were compared, and why the
proposal survived. An unrecorded answer is indistinguishable from an unasked question — the failure
6.13 and 6.14 both document.

**Direction of travel.** New modules should be unconditional and all-or-nothing. Where a block of
fields applies to only some consumers, that is a separate module with its own `applies_when`, not a
conditional block inside a larger one. The conditional mechanism was retired on 2026-08-14 with the
dissolution of `ReportingCore`, its only user; 6.12 keeps the record of why.

---

#### 6.12 Conditional modules must have their blocks named — and `--check` will not catch it if they do not

> **RETIRED 2026-08-14 — no conditional module exists any longer.** `ReportingCore` was the only one,
> and the only module that was not all-or-nothing: 9 of its 16 consumers held all six fields, and its
> five blocks had four *different* consumer footprints (13 / 14 / 12 / 13). It was therefore four
> independent modules stored in one file, bound by shared provenance rather than shared structure. It
> has been dissolved into `TargetSelection`, `CalibrationFactor`, `Blank` and `Aggregation`, each
> unconditional with a module-level `applies_when`. Composition was a no-op — all 52 module × consumer
> pairs reported `--check` MATCH — because the dissolution moved fields between modules and changed no
> definition. **Every module in the library is now unconditional and all-or-nothing**, which is the
> invariant 6.15 asks new modules to preserve.
>
> **The `conditional` guard in `compose_tapp.py` is deliberately kept**, contrary to the plan that
> retired this rule. It fires only on a manifest declaring `"conditional": true`, of which there are
> now none, so it costs nothing — and it is the tripwire that makes reintroducing a conditional module
> a deliberate act rather than an accident. Deleting safety code because the failure it guards has
> stopped occurring is how the failure comes back.
>
> The rest of this subsection is kept as the record of what went wrong, since the 2026-08-11 incident
> below is the reason the dissolution happened at all. It describes a mechanism no longer in use.

`Module_ReportingCore` declares `"conditional": true`: none of its blocks is universal, each carries an
`applies_when` condition, and **the consuming TAPP selects blocks explicitly**. Composing it without a
selection composes *every* block, silently adding fields the TAPP deliberately omitted.

**`compose_tapp.py --check` does not detect this.** It compares cells in rows that exist and does not
treat an **added row** as a difference — so it reports `MATCH` while its own report says
`added (4): [...]`. A `MATCH` on a conditional module therefore means "the shared cells agree", not
"the field set agrees". Read the `added` line.

Two guards now exist:

1. `compose_tapp.py` **refuses** to compose a module marked `conditional` unless blocks are named:
   `--module ReportingCore:target_selection,calibration_factor`, or `--module ReportingCore:all` to opt
   in to every block deliberately.
2. `composed_tapps.json` records the selection per consumer as `"blocks"`. That registry is the source
   of truth for what each TAPP should contain — read it before recomposing.

**Recorded because it happened.** On 2026-08-11 a recomposition run as `--module ReportingCore` added 18
fields across 7 TAPPs — `Procedural Blank Level` to TEM and Lab-XCT (neither has an analytical blank),
`Target Selection Criteria` and `Pre-Analysis Imaging and Screening` to the three Solution TAPPs (bulk
techniques, which the block's own `applies_when` excludes), and the aggregation and calibration blocks to
SEM_FIBSEM, SEM_Imaging and Lab-XCT. The registry had the correct selections all along; the run ignored
them, and `--check` reported 50/50 MATCH throughout. Detected only because a content-row count moved by
more than the change being made explained.

---

#### 6.11 `source_comment` — recording field provenance in system variants

A module may declare **`source_comment`** in its manifest: a short label that composition writes into
**Column G** of every field the module contributes.

```json
"source_comment": "Source: Geochronology module"
```

**Purpose.** In a system variant such as `LA-Q-ICP-MS_UPb_TAPP`, a reader cannot otherwise tell which
fields belong to the instrument TAPP and which arrived from the geochronology modules. The label is
**documentation only** — `validate_tapp.py` does not read it, it carries no structural meaning, and it is
not part of any schema generated from the TAPP.

**Which fields get labelled.** A Layer 2 module labels all of its fields. A Layer 3 module labels only the
fields its `blocks` *insert*; its Column F overlays sit on fields another module owns, and those keep that
module's label or none. So in a U-Pb variant, six fields read `Source: Geochronology module`, three read
`Source: U-Pb module`, and the ReportingCore fields the U-Pb module overlays with U-Pb-specific examples
stay unlabelled — they are general TAPP fields carrying system-specific examples, not system fields.

**Declared on every module, since 2026-08-14.** The label originally sat only on `Geochronology`,
`UPb` and `ArAr`, on the reasoning that the general modules were "the general TAPP" and labelling them
would be noise. **That decision is superseded, deliberately.** It was made when 8 modules existed, 3 of
them geochronology-specific, and Column G had just been cleared. The library now has 12 modules
supplying **767 of 1706 content rows — 45%** — and a reader of a composed TAPP could not tell which
module any given field came from. Naming the source is what the label is for, and the case that
justified it for geochronology applies with more force everywhere else.

Column G is therefore **no longer almost empty**: it went from 27 labelled rows to 767 in one pass.
Consumers of the CSVs who treated Column G as effectively blank must be told — README §3.1 and §11
carry the correction.

**The label names the OWNER, not the overlayer.** A Layer 3 module labels only the fields its blocks
*insert*; fields it merely overlays with Column F examples keep the label of the module that owns
them. So in a U-Pb variant, `Age Calculation Method` reads `Source: Geochronology module` even though
`Module_UPb` supplied its U-Pb-specific examples, and `Calibration Factor and Determination Method`
reads `Source: Calibration Factor module`. A field in no module — `Monitored Masses`, say — stays
blank, which is now meaningful information rather than the default state.

**Narrow exception to Rule 6.4.** Column G is otherwise consumer-owned. `stamp_source_comment` only ever
fills a Column G cell that is **empty**, so consumer annotation is never overwritten and recomposition is
idempotent. If a consumer later writes its own comment on a labelled field, that comment wins and
survives every subsequent recomposition.

**For future variants this is automatic.** Any new system variant — TIMS × U-Pb, Noble Gas × Ar-Ar —
gets its labels from composition, with nothing to remember.

---

### Rule 7 — "Keyed By": every field declares what its value repeats over

Every content row in every TAPP carries a **`Keyed By`** value stating what the field's value repeats
over — the field's *cardinality key*. A field holding one value per procedure declares `(none)`. A field
holding one value per analyte, per mass, per reported quantity, or per grain declares that key.

Rule 7 replaced the Column G label `Analyte-Specific`, which was doing this job badly. `Analyte-Specific` appeared 150
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
vocabulary. `Reported Variables and Units` reads: *"distinct from Analyte and Monitored Masses, which
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

**Anchors.** Three are universal; two are conditional and legitimately absent from some techniques.

| Value | Keys on | Test to apply | Examples |
|---|---|---|---|
| `sample` *(universal at analysis level)* | the physical specimen a group of reported rows belongs to — the frame within which `sampling unit` nests. Added 2026-08-12 with the decision that the analysis record is the **session**, which may cover many samples | Would a second sample in the same session produce another set of rows? | the specimen behind IGSN:AU1234567; each of 12 sections on one mount; each of 20 solutions in a digestion batch |
| `sampling unit` *(universal)* | a subdivision of the physical sample carrying its own row of values | Would a second grain / spot / phase produce another row? | EPMA analysis point; zircon grain; digestion aliquot; Mössbauer phase; fission-track confined track; XCT segmented phase; OSL aliquot |
| `reported property` *(universal)* | anything the procedure reports, **at any point in the chain** — quantities and nominal properties alike, plus their uncertainties | Does it appear in the reported data product? | ²⁰⁶Pb/²⁰⁴Pb ratio *and* ²⁰⁶Pb/²³⁸U date; ⁵⁶Fe/⁵⁴Fe *and* δ⁵⁶Fe; Dᴇ, D_R *and* OSL age; Fe³⁺/ΣFe; mineral species + match score; porosity |
| `channel` *(where a dispersive, selective or swept axis exists)* | a position on the axis the instrument steps through or selects across — mass, wavelength, energy, angle, temperature, field, pressure, time. **The address, not the signal** | Does the position exist even with zero signal there? | m/z 238; cup L2 at magnet step 1; Fe Kα on LIF spectrometer 2 (one WDS spectrometer assignment); Fe L₂,₃ edge; velocity channel 137/256; 855 cm⁻¹ bin; demagnetisation step 40 mT; DSC temperature setpoint |
| `analyte` *(chemistry only)* | the chemical species determined, at whatever granularity the procedure determines it | Would substituting a different isotope of the same element leave the target of determination unchanged? Yes → `channel`. No → `analyte`. | Si, Mg, Fe, Ca, Ni (EPMA); Fe (MC-ICP-MS); U, Pb, Th (U-Pb); Fe²⁺/Fe³⁺ at valence resolution (Mössbauer) |

**Two notes on the anchors, both dated 2026-08-12.**

*`channel` was reworded, not redefined.* Its gloss previously read "a position on the instrument's
selection axis", which scans as detector hardware and does not visibly invite a swept condition —
temperature in DSC, field step in demagnetisation, pressure step in mercury intrusion, frequency in
impedance spectroscopy. The generalisation was already present in the examples (*velocity channel
137/256* is a Doppler stimulus; *855 cm⁻¹ bin* is a spectral position), just not in the definition
line. Every prior example still validates and no row changed. This closes the question of whether
physical-property techniques need a key of their own for what they sweep: they do not — it is
`channel`.

*`sample` is defined but not yet in use.* It enters the vocabulary with the decision that the
analysis record is the session; the retrofit that populates it (Rule 13, `defines: sample`, the
`sample > sampling unit` nesting, the Group 2 per-sample audit) is steps 8–9 of
`analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md`. Until then no field declares it,
which is not a 7.4c violation — 7.4c constrains definers without consumers, not vocabulary without
users.

**Secondary keys.**

| Value | Keys on | Examples |
|---|---|---|
| `standard` | a reference against which something is anchored — physical **or virtual**. Record which axis it anchors; this varies by technique. | albite (anchors analyte); IRMM-014 (anchors reported property); α-Fe foil NBS SRM 1541 (anchors *channel*); RRUFF reference spectrum (virtual); dosimeter glass |
| `conversion` *(defined, not in use)* | a correction or calculation step, **only where it cannot be attributed to a single reported property** | retired 2026-08-11 — `Constants and Reference Values Used` was its only user *and* its only plausible definer, so it failed 7.4b/7.4c |
| `model component` | a component of a fitted decomposition of the signal | Mössbauer doublets/sextets (IS, QS, B_hf, Area%); Raman fitted peaks; XRD Rietveld phases; EELS edge components |
| `acquisition pass` *(defined, not in use)* | a distinct pass over the sample with its own instrument settings | retired 2026-08-11 — once `Beam Current` moved to `sampling unit`, the only remaining user was `Multi-Run Sequential Analysis Design`, which would have been its own definer |
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
| `A > B` | **containment** — B exists only within A; one value per B within each A | `sampling unit > model component` (Mössbauer components fitted per phase). No field in the current library uses nesting: `analyte > background position` was retired 2026-08-11 under 7.4c |
| `A x B` | **cross-product** — A and B are independent domains; one value per combination. Ordered: read as *"for each A, one value per B."* | `standard x reported property` (`Analytical Precision`); `sampling unit x analyte` (`Counting Statistics Error`) |
| `defines: A` | the field **enumerates** the key domain rather than being keyed by it — it is the header of the child table, not a column in it | `Analyte`; `Reported Variables and Units`; `Reported Date Type` |
| `defines: A per B` | the field enumerates domain A **and** repeats over key B — a definer whose child table carries a parent key. One key only; see 7.3.1 | `Monitored Masses` (`defines: channel per analyte`); `EELS Edges`; `Secondary Reference Materials` |
| `pair: A` | keyed by an unordered pair of A | `Discordance Definition and Values`; error correlation ρ between ²⁰⁶Pb/²³⁸U and ²⁰⁷Pb/²³⁵U |
| `A > B x C` | containment then cross-product — *"within each A, for each B, one value per C."* Added 2026-08-12 | `Counting Statistics Error` (`sample > sampling unit x reported property`): within each sample, for each analysis spot, one uncertainty per reported concentration variable |

**On `A > B x C`.** 7.3.1 declined to specify a compound key on the right of `defines: A per B`,
because `per` and `x` run in opposite directions and the token order would read two ways at once.
That objection does not apply here: `>` and `x` both run **outer-to-inner**, so `A > B x C` reads
left to right in one direction and needs no convention to disambiguate. It is specified now because
a real field requires it — the same standard 7.3.1 set for itself, and the same reason the `x`
ordering convention was justified against an actual reporting table rather than in the abstract.
Two fields in the library use it, both added 2026-08-17: `Counting Statistics Error` (12 TAPPs) and `Internal (Within-Measurement) Analytical Precision and Assessment Method` (9 TAPPs). They share a quantity shape — a per-analysis uncertainty on each reported quantity, within each sample — which is why they share a key.

**The separator is a literal ASCII lowercase `x`, whitespace-delimited — not `×` (U+00D7).**
The cells contain `standard x reported property`. `validate_tapp.py` splits on `\s+x\s+`, so a
multiplication sign would be read as part of a key name and reported as an unknown key. Written out
here because the typographically correct character is the natural thing to type and would break
parsing silently.

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

#### 7.3.1 `defines: A per B` — the definer that is itself keyed

> **Renamed 2026-08-17: `Monitored Isotopes` → `Monitored Masses`.** The field defines the
> `channel` domain, and that domain contains reaction-product and adduct masses as well as atomic
> isotopes — Wu et al. 2023 assign a dwell time to `(176+82)Hf`, Gil-Diaz et al. 2020 measure
> `125Te + 16O → 141TeO`. A field named "Isotopes" invites a curator to prune exactly the members
> that `Dwell Time per Mass` and `Interference Correction Method` are keyed by. `Masses` was chosen
> over `Species` because this document defines Analyte as "the chemical species a measurement is
> performed on"; reusing the word for the channel side would blur that line. The two dated tables
> in 7.11 and 7.12 keep the old name, being records of what was executed on 2026-08-12.

Added 2026-08-12. A field may enumerate one domain while repeating over another: `Monitored Masses`
lists the masses acquired — so it defines `channel` — but it lists them *per analyte element*, one row
per element. Before this form existed, Column I could state only the definer role and the second key
survived in prose, which is how it went unnoticed. Four fields in the library are of this shape; the
survey behind the addition is in `analysis/Survey_ColB_ColI_Report_2026-08-12.md`.

**The parent key is OPTIONAL per row — `per B` means "where a B exists", not "for every row".**
Added 2026-08-12. The gloss above says *"one row per element"*, which asserts that every member of
domain A has a parent in B. It does not, and the counter-example is in the library's own literature:

> Desem et al. 2022 records `Monitored Masses` as `202Hg, 203Tl, 204Pb, 205Tl, 206Pb, 207Pb, 208Pb`
> for a procedure whose analyte is **Pb alone**. ²⁰²Hg is the interference monitor for ²⁰⁴Pb and
> ²⁰³Tl/²⁰⁵Tl are the internal standard for mass fractionation correction. Three elements' worth of
> masses; one analyte.

Makishima et al. 2011 (¹⁴⁹Sm as the ID-IS reference) and Lu et al. 2007 (⁹³Nb as internal standard
for Ti) are the same shape. **Orphan members are normal, not exceptional**: interference monitors,
internal standards, isotopic carriers, and — once `channel` reaches the electron-beam TAPPs — any
spectrometer assignment used for a standard-only or background-only measurement.

Whether the parent is total or partial **varies by field and the notation does not distinguish
them**. `EELS Edges` is total: every ionisation edge belongs to an element. `Monitored Masses` is
partial. Both are written `defines: channel per analyte`, so a consumer must assume partial.

**For a schema generator, concretely.** The child table gets a **nullable** foreign key to the parent
domain, never a required one:

| Do | Do not |
|---|---|
| model the parent as an optional column on the child table | make it `NOT NULL`, or a required property |
| leave it empty for monitors, internal standards and carriers | drop rows that have no parent — they are part of the run table and are needed to assess interference corrections |
| take the parent domain's membership from its own definer (`Analyte`) | **infer membership from the child** — parsing `202Hg` to "Hg" and adding Hg to the analyte list is wrong; Hg is monitored, never determined |

The last row is the failure this note exists to prevent: the analyte list is authoritative and comes
from the `defines: analyte` field, never from the element symbols appearing in the channel list.

**7.4a is unaffected.** `defines: A per B` still creates a requirement for a `defines: B` field,
because *some* rows carry a parent and those rows need a domain to point into. A field whose parent
were empty on every row would not be using the form at all — it would be plain `defines: A`.

**Why the notation was not extended to mark nullability.** A marked form (`defines: A per B?`) was
considered and rejected: it would distinguish total from partial parents, but no field in the library
needs the distinction *enforced*, and the safe reading — assume partial — is correct for both cases.
This follows 7.3.1's own precedent for declining the compound key, and 7.4a–c's for retiring
abstractions with no user. If a consumer ever needs to rely on a parent being total, mark it then.

---

**Note that this is not `A > B`.** The containment form requires B to be unenumerable without A, and
the enumerability test in 7.3 fails here: m/z 238 is a position on the instrument axis and exists
independently of any analyte. `analyte > channel` would assert a containment that does not hold. The
field is a definer with a parent key, not a hierarchy.

**One key only.** The right-hand side takes a single key, not a compound. `defines: A per B x C` is
refused by `validate_tapp.py` (`rule7-compound-definer-key`).

Recorded so the question is not reopened from scratch: the compound form was considered and
deliberately left unspecified, because its token order reads in **two directions at once**. `per`
puts the innermost domain first (A is nested inside the key), while `x` runs outer-to-inner. So
`defines: A per B x C` is written A, B, C while its nesting is B, C, A — neither the nesting order
nor its reverse.

Two fixes exist, and both were rejected *for now* rather than on the merits:

- **Invert `x`** so the whole expression flows innermost-to-outermost. This would rewrite the 42
  existing rows that use `x` and sever the rationale in 7.3 above, where the current order mirrors how
  the reporting table is actually laid out (`Analytical Precision` is reported as a block per reference
  material listing each property).
- **Put the key first** — `per B x C defines: A` — which flows outer-to-inner throughout and leaves
  `x` untouched. Cost: `defines:` stops beginning the cell, and 7.4a–c are all about locating
  definers, so the column stops being scannable at a glance.

Neither cost is worth paying for a form with **zero instances**: all four affected fields take a
single key. This follows the same principle as 7.4a–c retiring `conversion` and `acquisition pass` for
want of a user, and 7.5 declining to populate `keyed_by_overridable` speculatively. When a field
genuinely needs a compound definer key, settle the direction then — against a real reporting table,
which is how the `x` convention earned its own justification. If that day comes, prefer the key-first
form over inverting `x`.

---

#### 7.3.2 Conditional keys — declare the finest key unconditionally (policy, 2026-08-27)

Some fields are scalar in a simple procedure and keyed in a complex one, and say so in Column B:
`Integration Time per Cycle` reads *"Analyte-specific **when** different isotope channels use
different integration schemes."* Column I can declare only one shape. This was raised as gap **G3**
in `Survey_ColB_ColI_Report_2026-08-12` and left open as a policy question.

**Decided 2026-08-27: declare the finest key that the literature attests, unconditionally.** No
conditional marker is added to the notation.

The reasoning is an asymmetry in how the two errors fail. Under-declaring is **lossy**: a consumer
generating a schema from Column I emits a scalar where the reported data is a list, and the
structure survives only in prose it cannot read. That is exactly the defect reported in
amds-ldeo/tapp#1, where `Detection Limit` was typed as a scalar while all 42 attested cells were
per-analyte lists. Over-declaring is merely **verbose**: a simple procedure fills a keyed table with
one row, which is correct, just roomier than it needs to be. A conditional marker would be more
exact than either, but it buys that exactness by making every downstream consumer implement extra
grammar for a handful of rows.

**"Finest attested" still governs, so this does not license inventing keys.** 7.12 is unchanged: the
key is the finest axis attested in *reported data*, not the finest axis imaginable. 7.3.2 only
settles what to do once the literature shows an axis is real but conditional — it says declare it,
rather than declaring the coarse shape because some procedures do not exercise it.

**Consequence for Column B.** Once the key is declared unconditionally, prose saying *"analyte-
specific when …"* restates Column I and is stripped under W5.2. The condition is not lost; it is
expressed by the fact that a simple procedure's keyed table has one row.

#### 7.4 The declaration invariants

**7.4a — every key in use must have its domain enumerated.** For every key K used by any field in a
TAPP, that TAPP must contain a field declaring `defines: K`. A key whose domain is never enumerated
cannot be populated: a consumer told that `Detection Limit` is keyed by reported property, with no field
listing the reported properties, has been given a child table with no rows.

This applies to **every** key, secondary keys included. The first implementation checked only the four
anchors, which was expedient rather than principled and left four secondary keys undefined library-wide.

For compound keys the invariant applies to each component: `standard x reported property` requires both
a `defines: standard` field and a `defines: reported property` field. For `defines: A per B` the field
satisfies the invariant *for A* and creates a requirement *for B* — the domain it enumerates and the key
it repeats over are counted separately.

**An ordinal count enumerates its domain.** A definer need not list its members where they are ordinal
and the count fixes them: `Number of Digestion Steps` is an Integer declaring `defines: preparation
step`, and "3" fully enumerates steps 1, 2, 3. This is the only definer of that shape in the library and
the invariant was written assuming a list, so it is stated here rather than left to be re-argued.

**7.4b — exactly one definer per key.** Two fields both declaring `defines: X` leave a consumer no way
to know which one builds the child table. Where two fields both enumerate a domain, one is the definer
and the other is keyed by it — in a multicollector TAPP `Collector Configuration` defines the channel and
`Monitored Masses` is keyed by analyte; in a single-collector TAPP there is no cup array and
`Monitored Masses` is itself the definer.

**7.4c — a definer needs a consumer.** `defines: X` where no field is keyed by X declares a domain
nothing repeats over. That is a field holding a list, not a key definer, and it should be `(none)`. Many
fields legitimately hold lists — `Interfering Elements`, `EDS Detector Configuration` — without any other
field repeating over their contents.

*Exempt:* the Rule 8 and Rule 9 mandatory fields. `Reported Variables and Units` exists to declare the
procedure's scope boundary and `Sampling Unit` to declare the unit a reported row corresponds to; both
are informative in their own right, so a TAPP with nothing keyed off them is not in error.

**Together, 7.4a–c force unused abstractions out of the vocabulary.** Applying them on 2026-08-11 retired
`conversion`, `acquisition pass`, `background position` and `model component` from active use, taking the
in-use vocabulary from ten keys to six. (Six as of that date; **seven since 2026-08-12**, when
Rule 13 added `sample`.)

Applying 7.4a also makes two fields mandatory in every TAPP. Because both are mandatory-field decrees in
the style of Rules 3 and 5, they are stated as **Rule 8** and **Rule 9** rather than buried here.

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
4. For every key K appearing in the TAPP — including each component of a compound key — **exactly one**
   field declares `defines: K` (7.4a, 7.4b), and no field declares `defines: K` where nothing is keyed by
   K (7.4c; the Rule 8 and Rule 9 fields are exempt).
5. In `A > B` and `A x B`, both A and B are valid keys. In `pair: A`, A is a valid key.
6. `Reported Variables and Units` and `Sampling Unit` are present in every TAPP (Rules 8, 9).
   `Error Correlation Between Reported Quantities` is present in every TAPP whose Phase 0 record declares
   jointly interpreted quantities, and absent elsewhere (Rule 10).
7. **Cross-TAPP**: a field name shared across TAPPs carries the same `Keyed By` in all of them, unless
   listed in the **technique-dependent key register** (`KEYED_BY_TECHNIQUE_DEPENDENT` in
   `validate_tapp.py`), each entry carrying a recorded rationale in `precedents.md`. Currently five
   entries: `Detection Limit`, `Primary Calibration Standard Name`, `Dwell Time per Pixel`,
   `Beam Current`, `Monitored Masses`.

   **The register is a first-class list, not an escape hatch.** Keys are uniform across TAPPs by default,
   because a field name that means one shape here and another shape there is invisible to a curator — the
   same argument Rule 6.4 makes about descriptions. The default is justified empirically: of 252 field
   names appearing in more than one TAPP, **only 3 carry a differing key** (98.8% uniform), so the check
   costs almost nothing while catching drift at the moment it is introduced rather than at the next audit.
   Entries in the register are expected and unremarkable; what is not acceptable is a divergence with no
   recorded reason.
8. **Warning, not error**: a field whose Comments column still contains a mode name matching one of that
   TAPP's mode-flag headers (7.6 cleanup not yet applied).

> **Invariant 7 was specified here but never implemented, and was implemented 2026-08-12.**
> `KEYED_BY_TECHNIQUE_DEPENDENT` was defined in `validate_tapp.py` from the start of Rule 7 and
> never consumed by any check — `check_cross_tapp` covered name variants and tier divergence only.
> Every unregistered `Keyed By` divergence therefore passed silently between the 2026-08-11 retrofit
> and 2026-08-12. It now emits `keyed-by-divergence` (WARN) for unregistered divergences and
> `keyed-by-divergence-registered` (INFO) for the five register entries.
>
> **What the gap had actually let through: one row.** On implementation the check found a single
> unregistered divergence, `Beam Damage Minimization`, introduced by the 7.12 pass itself hours
> earlier — resolved by extending `sampling unit` to `SEM_Composition` and `SEM`, since 7.8.7 makes
> uniformity the default absent a recorded technique reason and defocusing for damage-sensitive
> phases is the same practice in SEM-EDS. The 2026-08-11 retrofit's own uniformity claim therefore
> held; it simply had not been machine-checked. **A documented invariant is not an enforced one** —
> when a rule says the validator "must enforce" something, confirm the check exists.

---

#### 7.8.9 Column B uniformity — the counterpart check, implemented 2026-08-12

7.8.7 justifies the cross-TAPP key check by appeal to *"the same argument Rule 6.4 makes about
descriptions"*. That argument had no enforcement outside module composition. It now does.

**The numbers.** Of 252 field names appearing in more than one TAPP:

| | Count | Share |
|---|---|---|
| Divergent Column I | 5 | 2.0% — each registered with a rationale |
| Divergent Column B | 94 | 37.3% |
| …**substantively** divergent (<0.90 similarity) | **89** | **35.3%** |
| …of those 89, module-owned | **0** | 0% |

The zero is the module architecture working: `compose_tapp.py --check` guarantees description
uniformity wherever a module owns the row. Every one of the 89 is TAPP-owned, where nothing looked.

**Spelling was checked and is not the cause.** Normalising the British/American families
(-ise/-ize, centre/center, artefact/artifact, programme/program) leaves the count at **89 before, 89
after**, with **zero** fields differing by spelling alone. The split is real and worth fixing on its
own account — 151 British against 157 American occurrences library-wide, which is close to an even
divide and therefore has no house style to appeal to — but it explains none of the divergence.

**Why a naive check would have been wrong.** Some divergence is legitimate: a description that names
the technique's own physics *should* differ between EPMA and Lab-XCT. So the 89 were triaged first,
on the drift / principled / bug scheme that `analysis/Test4_Tier_Difference_Triage.csv` used for
tiers. Evidence: `analysis/Triage_ColB_Uniformity_2026-08-12.csv`.

| Verdict | Fields | Meaning |
|---|---|---|
| `PRINCIPLED` | 52 | Technique-specific content that should differ. No action. |
| `MIXED` | 17 | Some variants technique-specific, others merely shorter. Needs the full text. |
| `PARAPHRASE` | 8 | Same content, different words — drift. |
| `SUPERSET` | 7 | One variant covers the others and adds more — harmonise to the fullest. |
| `DRIFT` | 5 | Same content once technique nouns are set aside — harmonise. |

**How the check ships at 0 WARN without endorsing the backlog.** Divergences are frozen in
`COLB_DIVERGENCE_TRIAGED` in `validate_tapp.py`, each carrying its verdict. Registered divergences
report as INFO (`colb-divergence-<verdict>`); anything new reports as **WARN**. Non-`PRINCIPLED`
entries are a **visible backlog**, not an endorsement — they stay countable in every lint run, and
removing an entry after harmonising a field is how the backlog is worked down.

**Harmonisation pass, 2026-08-12.** The 20 `SUPERSET` + `PARAPHRASE` + `DRIFT` fields were
harmonised (`Project Files/Scripts/One-shot (applied)/patch_colB_harmonise_20260812.py`, 71 rows across all 16 TAPPs). **18 became fully
uniform and left the register; the register went 89 → 71 and the backlog 37 → 17 (`MIXED` only).**

Two kept a shared body with a legitimately technique-specific tail, and were **reclassified
`PRINCIPLED`** rather than forced into false uniformity:

- `Oxide Production Method and Threshold` — mis-triaged as `DRIFT`. The oxide proxy is genuinely
  technique-specific: LA uses ThO⁺/Th⁺ (mass 248/232), solution work uses CeO⁺/Ce⁺ (156/140). Only
  the framing sentence and the closing cross-reference to `Oxide Production` harmonise.
- `EDS Dead Time` — EPMA/SEM cross-reference `WDS Dead Time Correction`, which TEM has no analogue
  for; TEM instead carries its `Spectroscopic Detector(s)` conditional.

A third, `EDS Spectral Processing Type`, keeps TEM's conditional but is now similar enough (>0.90)
to fall out of scope entirely — which is the intended behaviour, not a miss.

**Two defects surfaced by reading the full text**, neither visible from the similarity score:
`E-scan Range` in Solution_SF carried its closing sentence **twice** ("Record 'N/A' if E-scan
acquisition is not used. Record 'N/A' where E-scan acquisition mode is not used."); and
`Interference Corrections Applied` prefixed its examples "Common **EPMA** interferences", which
would have been wrong once shared with the SEM TAPPs — generalised to "Common interferences", since
the Ti Kβ / Cr Kβ / Ba Lα overlaps are properties of the X-ray lines, not of the instrument.

**Where the harmonised text came from.** For `SUPERSET` the fullest variant was adopted after
checking it carried no content wrong for the other TAPPs. For `PARAPHRASE` the better-informed
variant won, or the two were composed. `Reported Variables and Units` adopted the **canonical Rule 8
wording** that 10 of 16 TAPPs already carried, which also aligns the field with the rule that
mandates it. `Instrument Manufacturer` and `Electron Source` had differed only by naming the local
instrument ("the SEM", "the TEM/STEM", "the EPMA"); since each TAPP already declares its technique,
"the instrument" loses nothing and gains uniformity.

**Classifier caveat, recorded because the first cut was wrong.** The triage initially called a field
`PRINCIPLED` whenever one variant carried a technique term the others lacked. That badly
over-classified: `Sample Name`'s four variants are one sentence with a local noun swapped ("sample
mount", "TEM section"), which is drift. Technique markers are now **stripped before** comparing
content, so a field is `PRINCIPLED` only when what remains still differs. `PRINCIPLED` is a
triage verdict from a heuristic, not an adjudication — treat the 52 as unreviewed, not as cleared.

---

#### 7.8.10 Column E uniformity — the last unchecked content column, implemented 2026-08-24

**Cross-TAPP**: a field name shared across TAPPs carries the same `Data Type` in all of them, unless
listed in the **Column E divergence register** (`COLE_DIVERGENCE_TRIAGED` in `validate_tapp.py`),
each entry carrying a triage verdict and its evidence in
`analysis/Triage_ColE_Uniformity_2026-08-24.csv`. A companion check applies the same rule across
field-name **variants**, using the two-word suffix test 7.8.7 already defines.

**Why this column needed its own check.** After 7.8.7 and 7.8.9, Column E was the only content
column with nothing looking at it — A, B, C/D and I all had a cross-TAPP check, E had none:

| Column | Check | Since |
|---|---|---|
| A — Metadata Item | `name-variant` | original |
| B — Description | `colb-divergence` (7.8.9) | 2026-08-12 |
| C/D — Tiers | `tier-divergence` | original |
| **E — Data Type** | **`cole-divergence` (7.8.10)** | **2026-08-24** |
| **F — Allowed Content** | **`colf-divergence` (7.8.11)** | **2026-08-30** |
| I — Keyed By | `keyed-by-divergence` (7.8.7) | 2026-08-12 |

**The consequence is not internal.** Column E is what downstream schema generation reads. In
`amds-ldeo/geochemBuildingBlocks`, `Text (free)` generates a string with no `schema:unitText`;
`Numeric (<unit>)` generates a number with `schema:unitText` pinned to that unit as a const; and
`Numeric + unit` generates a number with `schema:unitText` required but unpinned. A field typed
three ways therefore ships **one metadata item in three incompatible shapes**, and blocks the
consumer from collapsing it into a single shared definition. This check exists because
`amds-ldeo/tapp#1` reported exactly that for `Detection Limit`, which is typed `Text (free)` in
EPMA/SEM, `Numeric (ppm or wt%)` in the six LA tables and `Numeric + unit / Text` in the three
Solution tables.

**The numbers.** At implementation, **18** field names carried a divergent Column E and the
companion check found **8** name-variant pairs on top of that. `Detection Limit` and
`Detection Limit Method` were resolved the same day (see below), leaving **16** and **7**.

| Verdict | Fields | Meaning |
|---|---|---|
| LINEAGE | 14 | divergence tracks a known authorship boundary — LA/Solution (9) or EPMA/SEM (5) |
| OPEN | 2 | tracks no boundary; not examined; needs adjudication |
| PRINCIPLED | 0 | adjudicated as legitimate; no action expected |

**Resolved 2026-08-24 — the issue that prompted the check.** `Detection Limit` →
`Numeric + unit / Text` and `Detection Limit Method` → `Controlled list / Text`, uniform across all
12 TAPPs, plus TEM's `EDS Detection Limit`. Both left the register: entries are worked down by
harmonising, never by reclassifying, because an entry for a field that no longer diverges reads as
an unresolved issue. Reasoning and evidence in `precedents.md`; patch in
`Project Files/Scripts/fix_detection_limit_20260824.py`.

**Nothing was marked PRINCIPLED on the way in, deliberately.** 7.8.9's own closing caveat is the
reason: a `PRINCIPLED` verdict recorded from a heuristic against a field nobody has read is how
`Analyte` sat frozen as justified at similarity 0.01 while its divergence reached into the domain
definition itself. Every entry here is a backlog entry, all report INFO on every run, and the
register is worked down by removing entries after harmonising — not by reclassifying them.

**LINEAGE is a provenance label, not a verdict.** Nine ICP-MS fields split the same way — the six LA
tables free text or Boolean, the three Solution tables controlled lists — which is one authorship
boundary, not nine decisions, and all nine would be settled in one pass by the ICP-MS-scoped module
already on the plan. Two details argue the cluster is accumulated drift rather than two coherent
house styles: `Pulse/Analog Detector Nonlinearity Correction` runs the opposite way, and
`Mass Resolution Setting` splits 7/2 because Solution SF sides with the LA tables.

**The companion check consults `KEY_NAME_VARIANT_EXEMPT` first.** Its three entries record why those
pairs are *different fields*, and a rationale for field identity settles both columns at once — two
genuinely distinct fields may of course carry two types. Only the five pairs it does not cover need
an entry in `COLE_NAME_VARIANT_TRIAGED`, and all five are pairs whose **keys agree**, which is
precisely why the 7.8.7 companion never saw them.

> **`EDS Detection Limit` was the lesson.** Its *key* divergence was found by hand on 2026-08-12 and
> fixed — both it and `Detection Limit` became `reported property` — but the Data Type half of the
> same two-column problem was never looked at, and TEM sat on `Text (free)` for twelve days while
> `Detection Limit` went three ways. **Fixing one column of a field is not fixing the field.** When
> a check finds a divergence, ask which *other* columns of that row nothing is checking. Both
> columns were finally closed together on 2026-08-24.

---

#### 7.9 Legends sheet

The Legends sheet gains a fourth table:

**Table 4: Keyed By definitions** — one row per key value used in that TAPP, with its definition from 7.2
and any technique-specific extensions declared in Phase 0; plus the five notation forms from 7.3.

Only keys actually used in that TAPP are listed. A reader of the Lab-XCT legend should not see `analyte`.

---

#### 7.10 Retrofit — executed 2026-08-11

Applied in a single pass across the whole library. Recorded here because the counts are the baseline any
future audit compares against.

| | |
|---|---|
| TAPPs | 16 (after the LA-Q/SF split of the same date) |
| Content rows carrying a `Keyed By` value | **1,690** |
| — non-`(none)` | **372** |
| — `(none)` (scalar) | 1,318 |
| Modules given the column | 8 of 8; `owned_columns` gained `"I"` in all 8 manifests |
| New mandatory field rows inserted | 30 — Rule 8 × 10, Rule 9 × 16, Rule 10 × 4 |
| Comments rows carrying content, before → after | ~330 → **63** |
| — cardinality labels removed | 170 |
| — mode labels removed | 161 |
| — inherited Q/SF comments corrected in the two LA-MC files | 16 |
| Controlled lists completed with `N/A` / `None` (A.4) | 63 |
| Conditions moved from Comments into Column B (A.4) | 10 |
| Scripts | `compose_tapp.py` (`COL_KEYEDBY`, `FIRST_MODE_COL` 8→9, `LETTER` gains `I`, `owned_for()` for `keyed_by_overridable`), `validate_tapp.py` (`check_keyed_by`), `tapp_to_xlsx.py` (column width, Legends Table 4) |

**Sequencing, and why it is not optional.** Modules and manifests first, then recompose, then TAPP-owned
rows. Composed TAPPs are generated artifacts (Rule 6.6): hand-entered values on module-owned rows are
silently overwritten by the next recomposition.

This was demonstrated during the retrofit itself. Applying A.4 wrote condition sentences into Column B on
five module-owned rows in `Solution MC-ICP-MS` — four in `Module_MCICPMS`, one in
`Module_SolutionIntroduction` — and `compose_tapp.py --check` immediately reported `DIFFERS`. The fix was
to make the same edit in the module and recompose, which then correctly propagated the improved
description to the module's other consumers (`LA-MC-ICP-MS` ×2, `Solution Q-ICP-MS`, `Solution SF-ICP-MS`).
That is Rule 6 working as designed, and it is the failure mode this sequencing exists to prevent.

**Verification at completion:** `validate_tapp.py` 0 ERROR and 0 WARN across all 16 TAPPs;
`compose_tapp.py --check` 50/50 MATCH across every TAPP × module pair.

**A.3(b) resolved, and the proposal it came from was wrong.** The draft proposed adding `EDS`, `EELS`
and `4D-STEM` as mode columns to the TEM TAPP. Examining the TAPP showed that would duplicate two
mechanisms it already has, and contradict its own Phase 0 design:

- `Spectroscopic Detector(s)` already states the gating rule in its description — *"EDS and EELS
  parameter fields in Group 4 apply only when the corresponding detector is listed here."* That is a
  conditional, not a mode.
- `Analytical Sub-mode` already enumerates 4D-STEM, EFTEM and Precession ED beneath the three top-level
  modes. TEM's Phase 0 deliberately built a two-level Mode → Sub-mode structure.
- The mode flags already carried applicability correctly: EDS/EELS rows are `Y/Y/N` (both imaging modes,
  not diffraction), 4D-STEM rows `N/N/Y`. The Comments were expressing a *second, orthogonal* condition —
  "this field also requires the detector to be present" — which is precisely what A.4 is for.

The 39 TEM Comments rows were therefore given the A.4 treatment instead: 29 conditional fields gained an
explicit condition in Column B referencing `Spectroscopic Detector(s)` or `Analytical Sub-mode`, with
`N/A` added to Column F; 9 rows whose Comments were explanatory rather than conditional had that prose
folded into Column B. The same treatment then cleared the remaining 22 KED/DRC rows across the MC and
Solution TAPPs, conditioned on `Collision/Reaction Cell (CRC) Configuration`.

**Comments now carries content on zero rows across all 16 TAPPs.** The column is retained by author
decision for future one-off annotation.

> **Correction, 2026-08-12.** Not literally zero. The three composed U-Pb TAPPs carry **27** Comments
> cells, all module provenance stamps (`Source: U-Pb module`, `Source: Geochronology module`). They are
> harmless — arguably the "future one-off annotation" the column was retained for — but the sentence
> above is false as written, and 7.8.8's mode-name warning runs against that column. Found by the
> Column B survey (`analysis/Survey_ColB_ColI_Report_2026-08-12.md`).

Three `Keyed By` corrections fell out of the same examination: `EELS Edges` describes itself as *"the
EELS-specific counterpart to the Analyte field"* and is therefore `defines: channel`, which in turn makes
`EELS Background Subtraction Method` and `EELS Sensitivity and Detection Limit` `channel` rather than
`analyte`. TEM had an edge enumerator all along.

---

#### 7.11 Column B sweep and the 7.3.1 notation extension — executed 2026-08-12

The 7.10 retrofit cleaned Column G and **never swept Column B**. A survey of all 1,691 keyed rows against
their descriptions found the retired `Analyte-Specific` label alive in 46 Column B cells, and — more
consequentially — found that Column I had no way to express what several descriptions were asserting.
Full report and adjudicated findings in `analysis/`.

**What was decided and applied.**

| | |
|---|---|
| Rule 7.3 gains `defines: A per B` (7.3.1), single key only | 19 rows across 3 fields |
| `Monitored Isotopes` → `defines: channel per analyte` | 6 rows |
| `EELS Edges` → `defines: channel per analyte` | 1 row |
| `Secondary Reference Materials` → `defines: standard per analyte`, uniform across all 12 | 12 rows |
| `Calibration Factor and Determination Method` → `reported property` (Module_ReportingCore) | 14 consumers |
| `Integration Time per Cycle` → `channel` (Module_MCICPMS) | 3 consumers |
| `delta or epsilon Value Reference Standard` → `analyte` | 1 row |
| Retired `Analyte-Specific` label removed from Column B | 46 → **0** rows |
| `Analyte`'s stale pointer to the Comments-column label → points at Column I | 5 rows |
| `Detection Limit` / `Detection Limit Method` prose aligned to `reported property` | 15 rows |
| Total cells written | **113** across 14 TAPPs, plus 4 in 2 modules |
| TAPPs bumped | 14 of 16 — `SEM_FIBSEM` and `SEM_Imaging` carry none of the affected fields |
| Module versions | ReportingCore 3 → 4, MCICPMS 3 → 4 |
| Verification | `validate_tapp.py` 0 ERROR / 0 WARN; `compose_tapp.py --check` 16/16 MATCH; retired `Analyte-Specific` label 46 → **0** Column B rows |

**Why `Calibration Factor and Determination Method` is `reported property` and not `analyte`.** Its own
description says the factor *"converts the measured quantity into the reported quantity"*, so there is one
per reported quantity. The decisive constraint is that Module_ReportingCore has 16 consumers including
Lab-XCT, which has **no `analyte` anchor at all** (7.2 — `analyte` is chemistry only). `analyte` would be
invalid there and would force a `keyed_by_overridable` entry, which 7.5 forbids populating speculatively.
A module-owned key must be valid in every consumer; that is a real constraint on key choice, not a
formality.

**G3, conditional keys — policy, not notation.** Two fields described a key that appears only under a
stated condition (`Integration Time per Cycle`: *"analyte-specific when different isotope channels use
different integration schemes"*). **Declare the finest key unconditionally.** A consumer given `channel`
can hold one value when every channel shares it; a consumer given `(none)` cannot hold per-channel values
at all. The finer key is the superset and therefore the safe declaration, and no new notation is needed.
Note this is *not* the A.4 treatment, which handles conditional **applicability** — whether a field
applies at all — a different question from conditional cardinality.

**G2, nested sampling units — deferred.** Rule 9's `Sampling Unit` says *"Where units nest (e.g. confined
tracks within grains), state both levels"*, and no notation expresses a definer whose domain nests within
itself. Deferred because no TAPP in the library populates a nested sampling unit: fission track, the live
case, has no TAPP yet. Settle it when that TAPP is built, which is when the shape will be concrete.

**`Collector Configuration` — cycling left as free text.** Its multi-dynamic configuration list repeats
over a pass/magnet-step axis, which would be the retired `acquisition pass` key. Not reinstated: 7.4b/c
retired it for want of a user, and one user does not justify reviving an abstraction the rule removed.
Splitting the field into a configuration list plus a cycling sequence remains the better option if this
is ever revisited.

**`Desolvation System` — the second candidate, also declined (2026-08-31).** Raised because its cells
assign the introduction path per analyte, per resolution mode and per session — `ESI Apex Ω for HR-mode
dry plasma work; none for MR-mode wet plasma`, `Apex HF (Cr); Apex Omega (Mg)`. Reviving
`acquisition pass` for it would have needed a definer field in every Solution TAPP, and three arguments
say no. The key is **retired by rule**, not merely undefined — a distinction worth stating, because a
missing definer looks like an oversight to fix and a retired key does not. `Collector Configuration`
already made this exact case and was declined; **two users still do not justify reviving an abstraction
7.4b/c removed** for want of any. And the field fails Rule 7's own test: the key is the finest axis
attested in *reported data*, and reported data is indexed by analyte and reported property, never by
which pass produced it — Run 1 and Run 2 merge into one result table. `Desolvation System` therefore
stays `(none)`, with the per-analyte and per-mode assignment written inline, which is the same
convention `Mass Resolution Setting` uses ("where individual analytes are assigned to different modes,
state each"). Revisit only if reported data itself ever becomes pass-indexed.

**Both key questions the sweep left open were then settled against the literature (7.12).** The LA
`Detection Limit` was resolved *against* its key, not its prose, and the `Primary Calibration Standard
Name` register rationale was corrected.

- **No Column B uniformity check exists.** Of 252 field names appearing in more than one TAPP, 5 (2.0%)
  have divergent Column I — each justified in the register — while **89 (35%)** have substantively
  divergent descriptions. **Zero of the 89 are module-owned**: `compose_tapp.py --check` guarantees
  uniformity where a module owns the row and nothing looks anywhere else. 7.8.7 justifies its own check by
  appeal to *"the same argument Rule 6.4 makes about descriptions"* — an argument currently unenforced for
  TAPP-owned fields. Whether uniformity should be *required* there is a design question, since some
  divergence is legitimately technique-specific.

---

#### 7.12 Key validation against the literature assessment — executed 2026-08-12

The 7.11 sweep read Column I against Column B. This pass read it against **the extracted literature**:
231 literature assessment columns, ~17,000 filled cells, the 14 TAPPs with Phase 3 coverage. An
extraction is evidence about a field's *shape* — if 13 procedures all state one beam current, the field
is scalar; if they state a value per element, it is analyte-keyed.

**The rule this produced is now a precedent in `precedents.md`: a field's key is the finest axis
ATTESTED IN REPORTED DATA** — not one merely computed during data reduction, and not one only
conceptually possible. It decides in both directions, which is why it needed naming: `Beam Current`
keeps `sampling unit` because 2 of 13 procedures publish per-phase currents, while LA `Detection Limit`
loses it because the per-spot LOD is computed and then averaged away before anything is reported.

| Change | Rows | Evidence |
|---|---|---|
| `Detection Limit` (LA) `sampling unit x reported property` → `reported property` | 6 | 7 of 7 papers reporting LODs report one per element, aggregated. **Now uniform across all 12 TAPPs — leaves the technique-dependent register** |
| `Isobaric Interference Corrections Applied` `channel` → `(none)` | 9 | All extractions are Yes/No, and the description already says *"a procedure-level Boolean"* |
| `Secondary Reference Materials` → `defines: standard` in the 9 isotope TAPPs | 9 + 9 prose | 16 extractions are plain RM lists; only EPMA/SEM ask for *"assessed elements"*. **Reverses the uniform decision taken earlier the same day, on evidence.** Enters the register |
| `Primary Calibration Standard Name` `(none)` → `analyte` in LA-SF | 2 | Navarro et al. 2024 assigns standards to analyte groups. Enters the register |
| `Beam Damage Minimization` `(none)` → `sampling unit` (EPMA) | 1 | *"Defocused beam 5-10 µm for maskelynite, phosphate, sulfide, and glass"* |

**Keys the audit confirmed rather than changed**, which is the more common outcome and worth recording
so they are not re-litigated: `Beam Current` = `sampling unit`; `Primary Calibration Standard Name` =
`analyte` in EPMA (11 of 15 extractions give one standard per element); `Detection Limit` in EPMA =
`reported property` (per-element values, covered by the isomorphism precedent); `Monitored Isotopes` =
`defines: channel per analyte` (the grouping is implicit in isotope notation — `47Ti, 49Ti, 93Nb`).

**One proposed change was withdrawn after checking the raw cells.** `Within-Session Analytical Precision
and Assessment Method` and `Analytical Accuracy and Assessment Method` scored OVER-DECLARED, but every
Solution extraction references reference materials (*"% deviation from published Pb isotope values for
geological RMs (BCR-2, AGV-2, JB-2, BR, JB-3)"*); the detector required two *named* RMs in one cell and
scored *"USGS/GSJ RMs"* as scalar. They keep `standard x reported property`. Applying it would also have
removed the last consumer of `standard` in Solution Q/SF and orphaned `Secondary Reference Materials` as
a definer under 7.4c. **Read the extraction, not the aggregate.**

**Closed 2026-08-12:** the deferred `Minimum Resolvable Feature Size` question is moot — the field
was retired from Lab-XCT v17 as redundant with `Partial Volume Effect Criteria`, which already
requested the same criterion and already held both attested values. See `precedents.md`,
"Lab-XCT resolution fields — three collapsed to two".

**Coverage limits — absence of evidence is not evidence.** The four SEM TAPPs' 35 columns are `N/A` for
calibration standards throughout, because SEM-EDS is normally standardless, so their `analyte` key is
untested rather than confirmed. `LA-MC-ICPMS_UPb` and `Solution MC-ICP-MS` have no literature assessment
columns, so no key in them has been validated this way. **This validation is now part of Phase 3**: when
literature assessment columns are added or extended, run `scripts/audit_keys_vs_literature.py` and
reconcile before closing the phase. It carries an `ADJUDICATED` table of the 2026-08-12 dispositions,
so a re-run reports only genuinely new disagreements — it printed `0 NEW` at the close of this pass.
Its detectors locate candidates; they do not decide. **Read the raw extraction before changing a key.**

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
  Monitored Masses, which record what was acquired. A procedure may acquire many masses and report a
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

#### 10.1 The second correlation source — shared session calibration (added 2026-08-12)

Rule 10 as written covers correlation **between reported quantities**, keyed `pair: reported
property`. Rule 13 makes a second source representable for the first time: **a calibration shared
across a session correlates the samples measured in it.** Two analyses from one bracketing sequence
are not independent; two from different sessions are. A user averaging or regressing across samples
needs to know which is which, and before Rule 13 there was no session object for the statement to
attach to.

**This does not mint a field.** The two sources are different shapes — one is a pairwise coefficient
between quantities, the other a statement about which uncertainty components are shared — and the
machinery for the second already exists. `Uncertainty Propagation Method` (`Keyed By = reported
property`) requires the analyst to *"state which sources are included in the propagation: counting
statistics, calibration…"*. That statement must now also **separate the session-systematic
components — shared by every sample in the session, and therefore propagable only once when results
are combined — from the per-analysis random components.** This is the distinction Horstwood et al.
2016 formalised for LA-ICP-MS U-Pb, where ages from one session may not have their systematic
uncertainty propagated independently.

`Error Correlation Between Reported Quantities` is unchanged and keeps `pair: reported property`;
the inter-sample axis is not a pair of quantities and does not belong in it.

**Not settled:** whether the systematic/random split eventually warrants its own field rather than a
clause inside `Uncertainty Propagation Method`. It is left inside the existing field because no
TAPP yet reports the two components separately — the same 7.4c-style reasoning that keeps unused
abstractions out of the vocabulary. Revisit when a literature pass shows procedures reporting them
apart.


---

### Rule 11 — "Additional Notes" is the last field of every TAPP

Every TAPP must end with an **`Additional Notes`** field. Not merely the last field of Group 6 — the last
field of the **whole document**.

**Canonical definition:**
- Field name: `Additional Notes`
- Procedure-Level Tier: Advanced · Analysis-Level Tier: Advanced · Data Type: Text (free)
- `Keyed By`: `(none)`
- Placement: the final content row of the TAPP, at the end of Group 6
- Mode flags: Y for all modes
- Description: "Any procedure- or analysis-specific information not captured by a structured field
  anywhere in this TAPP — including anomalies, deviations from the registered procedure, instrument
  modifications, and supplementary context. Scope is the whole document, not Group 6: this is the last
  field of the TAPP and covers all six groups. Use sparingly; a structured field is preferred for
  anything that can be formally categorised."

**Why the position is the rule.** The field's scope is the entire document, and nothing in the row itself
says so — its position does. A field appearing after it silently narrows it to "notes about the things
above me", which is not what it means. Group 6 is where it sits only because every content row must sit
under a group header and Group 6 is last.

**Why not one per group.** Considered and rejected on 2026-08-11. The library gives a direct answer: across
16 TAPPs × 6 groups, exactly **one** group-local notes field has ever been created (`Sample Preparation
Notes`, in one TAPP). Six boxes would also multiply the free-text escape hatch by six, against this
field's own instruction to prefer structured fields, and would leave a note spanning two groups with no
home. A group-local note may still be added where a specific group demonstrably needs one — extracted,
not provisioned, in the spirit of Rule 6.10.

**Enforced at composition, not only by lint.** `Module_ReportingCore`'s `aggregation_qc` block anchors on
`Additional Notes` with `insert_before`, mirroring how the Group 5 blocks anchor on
`Constants and Reference Values Used` for Rule 5. This matters: the rule was broken in the first place
because that block used `append_to_group`, and "append to Group 6" means "after `Additional Notes`".
Any future block targeting Group 6 must anchor the same way.

**Note on composition and position.** `compose_tapp.py` updates a field already present *in place* and
never relocates it — deliberately, so recomposition does not shuffle files. Changing the anchor therefore
governs future insertions only; the 13 rows already in the wrong place needed a one-time move.

**Retrofit (2026-08-11):** description harmonised across 15 TAPPs (three variants were in circulation);
added to `Lab-XCT`, which had never had one; `Goodness-of-Fit or Dispersion Statistic` moved back above it
in 13 TAPPs.

---

---

### Field names

**Level-neutral naming**: Field names must not encode procedure-level or analysis-level framing. Avoid "Default", "Target", "Achieved", "Typical", "Actual" as prefixes or suffixes that signal which level a value belongs to. The tier columns (C and D) carry that information. Use Column B (Description) to clarify that the procedure registers a target or typical value and that analysts may adjust within allowed bounds.
- ✓ "Laser Fluence (Energy Density)", "Carrier Gas and Flow Rate", "Voxel Size"
- ✗ "Default Laser Fluence", "Carrier Gas and Default Flow Rate", "Target Voxel Size"

**Exceptions — "Target" retained for scope-defining fields**: These field types use "Target" because it denotes *what the procedure is aimed at*, not a value with a later "achieved" counterpart. Both are **type-level**: they name the kind of material or feature a procedure is designed for, never the particular portion of a particular sample, which is `Sampling Unit Selection Criteria` (renamed from `Target Selection Criteria` on 2026-09-01 for exactly this reason):
- "Target Material" — the material type the procedure is designed to analyze
- "Target Feature(s)" — the microstructural features or properties the procedure is designed to characterize

**"(Measured)" companion field**: Use to distinguish the analysis-level measured value from the procedure-level acceptance criterion when a split is required (see Q3 in `references/field-review.md` and Oxide Production in `references/precedents.md`).
- Procedure field: "Oxide Production Method and Threshold" (the criterion)
- Analysis field: "Oxide Production" (the measured value)

**"(Mode Only)" suffix**: Use when a field is restricted to a single mode.
- ✓ "Raster Line Spacing (Mapping Only)"

**"Procedure" vs. "Method"**: Use "Procedure" when referring to the registerable procedure object. Use "Method" only for assessment methods, calculation methods, or sub-procedures.
- ✓ "Procedure Name", "Procedure DOI", "Funding Source for Procedure Development"
- ✓ "Detection Limit Method", "Signal Integration Interval Method"
- ✗ "Method Name", "Method DOI" — use "Procedure Name", "Procedure DOI"

**Cardinality is declared in Column I, not in Comments**: the former Column G label "Analyte-Specific" is superseded by Rule 7. Do not reach for `analyte` by default — it applies to fewer than half the fields that once carried that label, and it is absent entirely from techniques with no chemical species (Lab-XCT, Raman, fission track).

### Vocabulary for common concepts

| Preferred term | Avoid | Reason |
|---|---|---|
| Procedure | Method (for the registered procedure object) | Precise vocabulary; see definitions above |
| Keyed By value (Rule 7) | Analyte-Specific, Element-Specific | Cardinality is a column, not a comment; `analyte` is one key among several |
| Analytical mode | Ablation mode, measurement mode | General across techniques |
| Session | Run (when "run" is ambiguous with sub-runs in multi-run designs) | Clarity |
| Background | Gas blank | "Gas blank" is specific to gas-phase instruments; "Background" applies across techniques |
| Detection Limit | LOD, Limit of Detection | Consistent with LA-ICP-MS TAPP field naming |
| Signal integration interval | Integration window | Be consistent within a TAPP |

---

## Data Type Vocabulary

Use these standardized data type labels in Column E:

| Label | Use for |
|---|---|
| Text (free) | Free-text narrative; no controlled vocabulary |
| Controlled list | Value must be one of a defined set — the list is **CLOSED**. List the allowed values in Column F. |
| Numeric (unit) | A number with a specific unit; state the unit in parentheses, e.g., Numeric (W), Numeric (Hz), Numeric (µm) |
| Numeric + unit | A number where the unit is variable and must be stated by the user |
| Integer | Whole number with no unit |
| Date | YYYY-MM-DD format |
| URI / DOI | A persistent identifier, URL, or DOI |
| URI / IGSN | An IGSN-format sample identifier |
| Text / URI | Either free text or a URI reference |

### Compound data types

A field that legitimately accepts more than one *form* of value takes a **compound** Data Type: a
vocabulary label, a space-slash-space separator, and a fallback label — most-preferred form first.
`Text (free)` may be written `Text` when it is the fallback.

The vocabulary already contains one such compound, `Text / URI`; this rule generalises that pattern
rather than introducing a new one.

| Compound | Use for | In use |
|---|---|---|
| `Controlled list / Text` | a defined set of values, but the field also expects a qualifying answer — or accepts one the list cannot express | 211 cells, 40 fields |
| `URI / DOI / Text` | an identifier is preferred, but placeholders such as "pending", "same submission" or "None" are valid answers | 14 uses |
| `Numeric (unit) / Text` | a number is expected, but a qualifying statement is sometimes the honest answer | |

**Use a compound only when the second form is a legitimate answer, not a way to avoid choosing.**
If the fallback would only ever be used to record absence, the field is a plain `Controlled list`
and `N/A | None` in Column F already covers it. The test that decides it: **could the escape ever
be retired by extending the list?** Yes — the out-of-list answer is a member you failed to
enumerate — plain `Controlled list`, and complete the list. No — the answer is a different *shape*,
a term plus a citation or a per-analyte assignment — `Controlled list / Text`.

**Not compounds.** These forms appear in the library and are errors rather than compounds:

| Found | Should be | Why |
|---|---|---|
| `Numeric or Text`, `Numeric (ms) or Text` | `Numeric + unit / Text`, `Numeric (ms) / Text` | the separator is ` / `, not "or" |
| `URI / Text (free)` on an IGSN field | `URI / IGSN` | a named type already exists for this |
| `Numeric + label` | `Text (free)` | the value is a single composite string (e.g. `'+5 mm (High), -5 mm (Low)'`), not a number with an alternative form |

**For all Controlled list fields — plain or compound** — Column F must include `N/A | None` in addition to the technique-specific values. These are conventional *values* a user must be shown they may enter, so that absence is recorded rather than left blank.

**`Other: specify` must NOT appear in Column F.** It left the vocabulary on 2026-08-30, stripped from 226 cells. It was wrong in both places it appeared:

- On a plain `Controlled list`, it **contradicts the type**. The type says the list is closed; the option says it is not. Nothing could see the contradiction, which is exactly how `Technique` came to carry `Other: specify` in 13 of 16 TAPPs — the exemption below was implemented as *skip this field* rather than *verify it stays closed*, so the drift was invisible for months.
- On a `Controlled list / Text`, it is the **wrong prompt**, not merely redundant. A compound wants a listed term *plus* qualification — the citation, the elements affected, the fit window. `Other: specify` invites "pick something else", which is the wrong behaviour.

**It must not appear on any other type either.** On `Text (free)` the field already admits any
answer; on `Numeric (<unit>)` Column F is illustrative. 137 cells across 43 fields were still
carrying it after the controlled-list sweep and were cleared on 2026-08-30. Enforced by
`forbidden-options` in `validate_tapp.py`, which applies to every Data Type and has no
exemptions — note this is deliberately *not* the same scope as `CONTROLLED_LIST_EXEMPT`, which
governs the required options only.

**Prefix an illustrative Column F with `e.g.,`.** On a `Controlled list` the values ARE the
domain; on `Text (free)`, `Integer` or `Numeric (...)` they can only be examples, and the
prefix is what tells a reader — and a scan — which they are looking at.

**A member list on a free-text type is a smell.** `Other: specify` turned out to appear *only*
where Column F was written as a pipe-separated enumeration ending `N/A | None | Other: specify`
— the controlled-list convention exactly — and never on a list prefixed `e.g.,`. Measured
across the 66 such fields on 2026-08-31, the smell was usually harmless: **44 of the 57 with
attested cells had ZERO cells matching any listed member**, at distinctness 0.85–1.00, so the
lists were examples wearing a vocabulary's clothes and took the prefix. Two rules settle it:

- **A numeric or integer field's Column F is always illustrative.** There is no controlled list
  of numbers.
- **A `Text (free)` field's is illustrative when the literature says so** — at most a quarter of
  attested cells matching a member, on three or more cells.

Where a `Text (free)` field's list *is* matched by its cells, the field is probably mis-typed
and wants a Column E decision, not a prefix.

**Where the guidance went.** The reference value of `Other: specify` — telling a user what they may enter — is real, and is now served once by the **Data Type table on the generated xlsx Legends sheet** rather than by 226 inline repetitions that can drift out of sync with the type they describe. Add to that table, not to Column F, when the guidance needs to change.

**Closing a list is a claim, and it has a cost when wrong.** A closed list that is incomplete forces users into wrong answers: amds-ldeo/tapp#3 was 84 invalid publication cells, entered by curators because `Analytical Mode`'s Column F told them `EDS` and `CL` were the allowed values. **Verify a list is complete against its attested literature before closing it.**

`Technique` was the worked example. It was held back from the strip because three TAPPs' lists did not contain their own technique — LA-SF's offered `LA-ICP-MS | LA-ICP-OES | LA-MC-ICP-MS | LA-ICP-ToF-MS | LA-ICP-MS/MS` against 7 attested cells all reading `LA-SF-ICP-MS`. The vocabulary was fixed first (2026-08-30, Rule 1) and closed after:

- **Each list holds the TAPP's own technique, not a menu of siblings.** The three Solution tables already worked this way and are the model: 29 of 29 attested cells match their single listed value.
- **`Technique` is platform-level.** Attested `SEM-EDS`, `fs-LA-Q-ICP-MS` and TEM's `STEM; EDS; EELS` composites name a detector, a laser pulse duration and a set of spectroscopies — all of which other fields already record. A value belongs here only if no more specific field owns it.
- **A subtype-unstated member goes in only where the literature reports coarsely.** The two LA-Q tables gained `LA-ICP-MS (analyser not specified)` for two such cells; LA-SF did not, because all seven of its cells name the analyser. Add members on evidence, not for symmetry.

**Exemption — fields whose allowed values are bound by another rule to an exact enumeration.** A Controlled list field is exempt from the `N/A | None` requirement when a different rule fixes its allowed values to an exact, closed set, and adding the generic options would break that correspondence or be semantically empty.

| Exempt field | Bound by | Why exempt |
|---|---|---|
| `Analytical Mode` | Rule 3 | Allowed values must mirror the mode flag column labels *exactly*, with no paraphrase or substitution, so that sub-TAPP filtering resolves correctly. `N/A` and `None` are meaningless, since every procedure has an analytical mode. |
| `Technique` | Rule 1 | The field is the TAPP's own top-level technique identifier, drawn from the cross-TAPP technique vocabulary. `N/A` and `None` are semantically empty — every procedure has a technique, and a procedure record that declared otherwise would be malformed. Several TAPPs correctly carry a single allowed value (`Solution Q-ICP-MS`), a closed enumeration of one. Added 2026-08-10; see `precedents.md`. **Its exemption is doing double duty as of 2026-08-30**: it is also the one field still carrying `Other: specify`, because its Column F is known incomplete — three TAPPs' lists omit their own technique against 14+ attested cells. Retire that half of the exemption when Rule 1 settles the vocabulary. |

This exemption list is closed — add to it only by explicit decision, recorded here and in `references/precedents.md`. It does **not** extend to mode-adjacent fields such as `Analytical Sub-mode`, `EDS Acquisition Mode`, or `Beam Mode`, whose values are not bound to the mode flag column labels and which therefore carry the generic options like any other Controlled list.

Column F format: all allowed values separated by ` | ` (space-pipe-space). If the list exceeds approximately 8 values, abbreviate with a note "see Legends sheet for complete list."

---

## File Management: CSV and xlsx

### CSV (source of truth)

The CSV is the canonical version of the TAPP. All edits are made here.

- Filename: `[Technique]_TAPP_v[N].csv`
- Encoding: UTF-8
- Column headers in row 1, content from row 2
- Group header rows: populate Column A with the group name (e.g., "1. Procedure Identification"); all other columns blank or N for mode flags
- Blank separator rows: all columns empty
- Tier values: plain text labels exactly as specified in the Tier Vocabulary above

### xlsx export

Generate the xlsx from the CSV using `scripts/tapp_to_xlsx.py`. The script applies:
- Bold + color formatting to all tier values per the vocabulary table
- Bold + fill color to group header rows (no merged cells)
- Wrap text and top alignment for all content cells
- Column widths per the approximate guidelines below
- Legends sheet generated from the tier vocabulary definitions

**Never edit the xlsx directly.** If a change is needed, edit the CSV and regenerate.

### Targeted patch scripts

For small changes to an existing TAPP CSV, write a Python patch script that modifies only the affected rows/columns by coordinate. Template:

```python
import csv

INPUT = 'LA-ICP-MS_TAPP_v5.csv'
OUTPUT = 'LA-ICP-MS_TAPP_v5.csv'  # overwrite in place

with open(INPUT, newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

# Example: update description in row 57 (0-indexed), column B (index 1)
rows[57][1] = 'Updated description text here.'

with open(OUTPUT, 'w', newline='', encoding='utf-8-sig') as f:
    csv.writer(f).writerows(rows)
```

Always print a summary of what was changed and verify by reading back the modified rows.

### Column structure

Every TAPP CSV uses this fixed column order before the mode flag columns:

| Col | Header | Content | Notes |
|---|---|---|---|
| A | Metadata Item | Field name | Level-neutral per naming conventions |
| B | Description / Purpose | Full field description | No mode labels here — those are carried by the mode flag columns |
| C | Procedure-Level Tier | Basic / Advanced / N/A | |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced | D=N/A is not valid |
| E | Data Type | Controlled vocabulary — see Data Type Vocabulary | |
| F | Example / Allowed Content | Examples or controlled list values | Controlled lists must offer N/A and None; see Rule 7 A.4 |
| G | Comments | Short field-level qualifiers that are neither mode nor cardinality — instrument variant, signal/detector, conditional notes | Cardinality goes in Column I (Rule 7); mode applicability goes in the mode flag columns (Rule 3) |
| H | Last Update | YYYY-MM-DD date of most recent substantive edit | |
| I | Keyed By | What the field's value repeats over — see Rule 7 | Never blank on a content row; `(none)` for a scalar |
| I+1 … I+n | Mode flag columns | One column per mode; Y or N | Labels set in Phase 0 |
| (after modes) | Literature Assessment | Sentinel column — header exactly `Literature Assessment`; all data rows empty | Marks boundary before lit assessment columns |
| (after sentinel) | Literature assessment columns | One column per paper extracted in Phase 3 | Starting letter depends on number of modes |

### Approximate column widths for xlsx export

| Column | Width (characters) |
|---|---|
| A (Metadata Item) | 35–40 |
| B (Description) | 65–70 |
| C (Procedure-Level Tier) | 14 |
| D (Analysis-Level Tier) | 14 |
| E (Data Type) | 18 |
| F (Example/Allowed Content) | 45 |
| G (Comments) | 22 |
| H (Last Update) | 14 |
| I (Keyed By) | 24 |
| Mode flag columns | 12 each |
| Sentinel column (`Literature Assessment`) | 4 (narrow; data rows are empty) |
| Literature assessment columns | 28 each |

---

## Legends Sheet

Every TAPP xlsx must include a Legends sheet. The CSV has no Legends sheet — it is generated at export time. The Legends sheet must contain:

**Table 1: Procedure-Level Tier definitions** — Basic, Advanced, N/A with full definitions

**Table 2: Analysis-Level Tier definitions** — Read-Only, Editable, Basic, Advanced, N/A with full definitions

**Table 3: Mode column definitions** — one row per mode defined in Phase 0, with the mode label and its full definition; plus Y and N definitions

**Table 4: Keyed By definitions** (Rule 7) — one row per key value used in that TAPP, with its definition, plus the notation forms. Only keys actually used in that TAPP are listed

The Legends sheet text must be consistent with the definitions in this conventions file.

---

## Version and Date Tracking

Column H (Last Update) contains the date of the most recent substantive edit to each row, in YYYY-MM-DD format. Initialize all rows to the creation date for a new TAPP.

**Version numbering:**
- Major structural revisions (field additions/removals, tier changes, mode flag changes): increment integer version (v4 → v5)
- Description updates, example content improvements, no structural changes: decimal update (v5.1) or column H (Last Update) date update only

TAPP filenames: `[Technique]_TAPP_v[N].csv` and `[Technique]_TAPP_v[N].xlsx`

---

### Rule 13 — the analysis record is the session; `Sample Name`, `Sample Persistent Identifier` and `Session Identifier` are mandatory in every TAPP

**An analysis record corresponds to one execution of a procedure — a session — which may cover many
samples.** Each sample carries its own identity and may carry its own preparation history. Three
fields are therefore mandatory in every TAPP, in the style of Rules 8 and 9:

| Field | Group | C | D | Keyed By | Role |
|---|---|---|---|---|---|
| `Sample Name` | 2 | N/A | Basic | `defines: sample` | enumerates the sample domain — the definer for the `sample` key |
| `Sample Persistent Identifier` | 2 | Advanced | Advanced | `sample` | one IGSN (or equivalent) per sample |
| `Session Identifier` | 1 | N/A | Basic | `(none)` | the laboratory's own run / sequence / batch identifier for the session |

**Why `Sample Name` is the definer and not `Sample Persistent Identifier`.** 7.4a requires exactly
one `defines: sample` per TAPP, and an optional definer would leave the domain unenumerable in the
common case. `Sample Name` is already D=Basic — mandatory at analysis time — in every TAPP; IGSN
registration is not universal, so the identifier field stays Advanced and is keyed *by* the domain
the name defines. C=N/A is correct and deliberate on both: the procedure is sample-neutral and
specifies nothing about which samples it will be applied to.

**Why the session needs its own identifier.** Group 1 was already session-shaped before this rule —
it carries `Analyst`, `Analysis Start Date` and `Analysis End Date`, and a start *and* end date
describes a session, not a specimen — while Group 2 treated the record as one sample. Rule 13
resolves that contradiction in favour of the session. The identifier is the laboratory's own, which
the instrument or acquisition software has already generated, and it is the only link back to the
raw files. Whether a repository additionally mints a persistent identifier on submission is an
infrastructure decision outside this rule; the two coexist.

**What this buys, beyond tidiness.** A shared session calibration is a source of error correlation
*between samples* — two analyses from one bracketing sequence are correlated, two from different
sessions are not. With the session unrepresented that correlation could not be stated at all. See
Rule 10.

**`sample` and `standard` are overlapping domains, not disjoint ones.** Secondary reference
materials are run through the same calibration as unknowns and evaluated against accepted values;
many are SESAR-registered with their own IGSNs. The keys stay separate because they key different
fields — `standard` keys anchoring and QC, `sample` keys identity and preparation — but a secondary
RM legitimately appears in both domains within one session, and that is not double counting. A
schema that asserts disjointness will be violated by ordinary sessions. Primary calibration
standards are the exception: their values are inputs, not results, so they never behave as samples.

Recorded in full, with the reasoning and the alternatives considered, in
`analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md` Part A.

---

### Rule 12 — `Current TAPPs/` mirrors the latest version of every TAPP

**Every time a TAPP is created or a version is bumped, the new CSV and xlsx are copied into
`Current TAPPs/` at the library root, replacing the version they supersede.** The technique folders go
on holding every version; the mirror holds exactly one — the current one.

**Why it exists.** So the whole folder can be handed to another developer as a unit. Nothing to sift,
no ambiguity about which file is current. That purpose is also why a *stale* mirror is worse than no
mirror: a recipient has no way to tell that what they were given is out of date.

**Shape.** Flat — no technique subfolders. Both formats: the CSV is the source of truth, the xlsx is
the colour-coded reading copy with its Legends sheet. Currently 16 TAPPs, 32 files, plus a generated
`README.md` explaining the column layout, where earlier versions live, and where the specification is.

**It is a copy, never an editing target.** Edit the TAPP in its technique folder and re-sync.

#### 12.1 The mirror must be excluded from `discover()` — this is not optional

`Current TAPPs/` is named in `CURRENT_DIR` in `validate_tapp.py` and skipped by `_excluded()`,
alongside `superseded*` and `*archive*`. Without that exclusion:

- every TAPP is found twice, and for equal versions which path is treated as authoritative depends on
  `os.walk` order — so the linter would report a path that varies between runs;
- worse, a copy **accidentally bumped inside the mirror** would win the version comparison and become
  the file `validate_tapp.py` validates, while `compose_tapp.py` went on using the technique-folder
  path from `composed_tapps.json`. The two would silently disagree about which file is live.

Both behaviours were verified by construction before the mirror was created. This is the same
silent-failure class as the exclusion trap noted in 7.8: a directory name decides whether a TAPP is
visible to the tooling at all.

#### 12.2 Enforcement

| | |
|---|---|
| Refresh | `Project Files/Scripts/sync_current_tapps.py --apply` (dry-run by default) |
| Automatic | `bump_and_stamp_20260812.py` calls it at the end of every version bump |
| Check | `validate_tapp.py` → `check_current_tapps`, **WARN** |

The check reports four distinct failures, each fixed by one sync:

| Finding | Meaning |
|---|---|
| `rule12-missing-folder` | the mirror does not exist |
| `rule12-stale` | mirror holds an older version of a TAPP that has since been bumped |
| `rule12-absent` | a current CSV or xlsx never reached the mirror |
| `rule12-extra` | a file in the mirror corresponds to no current TAPP — a superseded version that should have been replaced, or a retired TAPP |
| `rule12-differs` | a mirror file differs in **content** from the library copy — it was edited in place |

**Both the check and the sync compare content hashes, not file sizes** — corrected 2026-08-12.
Size was the original test in `check_current_tapps` and in `sync_current_tapps.py`, and it silently
missed a real change: a regenerated xlsx and its mirror copy were both exactly 42785 bytes with
different content, so the sync reported 15 files to copy instead of 16 and the stale one had to be
found by hand. openpyxl output is especially prone to this — rewriting the same workbook after a
small text edit often lands on an identical size. A size test made the mirror silently stale, which
is precisely the failure 12.1 argues is worse than having no mirror at all.

WARN rather than INFO deliberately. The library is kept at 0 WARN, so a stale mirror cannot be
forgotten; and a rule with no check behind it is the failure mode 7.8 documents at length.
