> **⚠️ ARCHIVED — PRE-VIM3 SNAPSHOT (2026-07-24)**
> This file reflects TAPP terminology *before* alignment with BIPM VIM3 (JCGM 200:2012): "Protocol" = the
> registerable, DOI-bearing object; "Procedure"/"Analysis" = the analysis-level execution. Kept for
> historical record only — **do not use for current TAPP work.** Current version lives at the original
> path in the TAPPs project (same filename, without this suffix).
>
> See the "Aligning TAPP Vocabulary with VIM3" migration plan for the full rationale.

---

# TAPP Conventions

Controlled vocabulary, structural standards, naming conventions, and file management workflow that must be consistent across all TAPPs. These are binding — deviating from them requires explicit decision and documentation.

---

## Vocabulary: Technique / Method / Protocol / Procedure / Analysis

These terms have precise meanings in the TAPP framework and must be used consistently.

| Term | Definition | TAPP relevance |
|---|---|---|
| **Technique** | A (set of) physical or chemical principles utilized on an apparatus, instrument, or collection of instruments that can be applied to a sample, material, or other medium to yield qualitative or quantitative data | Names the TAPP (e.g., "LA-ICP-MS TAPP") |
| **Method** | An application of a technique to a sample, material, or medium to acquire a specific data type or types, providing results and interpretable outcomes. General — not linked to a specific lab or person | Use "Method" for assessment methods, calculation methods, and named sub-procedures (e.g., "Detection Limit Method", "Signal Integration Interval Method") |
| **Protocol** | A set of stringent guidelines that specify a procedure that an analyst must follow. Registerable with a DOI. A protocol is prescriptive | The object captured in TAPP protocol-level columns (C); receives a DOI upon registration |
| **Procedure** | The documentation of an actual implementation of a protocol in an analytical session — what was actually done, including any deviations | The object captured in TAPP analysis-level columns (D); also called "analysis" in user-facing contexts |
| **Analysis** | Used interchangeably with "procedure" in user-facing contexts (e.g., "Analysis-Level Tier") to avoid confusing users | Preferred user-facing term for the procedure level |

**Key rule:** Use **"Protocol"** when referring to the registerable protocol object. Use **"Method"** only for assessment methods, calculation methods, or named sub-procedures. Never use "Method" as a synonym for the overall registered protocol.

---

## Tier Vocabulary

### Protocol-Level Tier (Column C)

| Value | Meaning | xlsx color |
|---|---|---|
| Basic | Mandatory for protocol registration. Must be provided to register a valid protocol. | Bold red (C00000) |
| Advanced | Optional for protocol registration. Strongly recommended but not required. | Bold green (375623) |
| N/A | Not applicable at protocol level. Analysis-level field only. | Bold (default) |

### Analysis-Level Tier (Column D)

| Value | Meaning | xlsx color |
|---|---|---|
| Read-Only | Directly imported from the registered protocol; cannot be changed by the analyst. Changing this value means running a different protocol. Fields that are relevant only at protocol level (no session-specific variation) are also assigned Read-Only — the value is inherited from the protocol record and displayed in the analysis form. | Bold blue (0070C0) |
| Editable | Imported from the registered protocol but may be adjusted within protocol-defined bounds (e.g., daily tuning, minor software updates). The protocol registers the target or typical value; the analyst confirms or adjusts it. Editable fields with a Basic protocol-level tier cannot be left void. | Bold purple (7030A0) |
| Basic | Mandatory user input at analysis time. Value comes from the analysis (procedure) itself and cannot be pre-specified in the protocol. | Bold red (C00000) |
| Advanced | Optional user input at analysis time. Recommended for complete documentation. | Bold green (375623) |

**D=N/A is not a valid analysis-level tier.** Every field must carry a meaningful analysis-level assignment. Fields relevant only at protocol level receive D=Read-Only.

---

## Standard Six-Group Structure

Every TAPP uses these six groups in this order. Group names are section header rows — use bold formatting and a distinct fill color on individual cells. **Do not merge cells for section headers**, as merged cells prevent adding or moving rows later.

| Group | Scope |
|---|---|
| 1. Protocol Identification | Administrative and identity fields for the protocol record. Includes fields for both the protocol object (author, DOI, funding for protocol development) and the analysis/procedure record (analyst, session dates, funding for the analysis campaign). Also includes coupling fields documenting any co-registered techniques applied to the same sample. Largely transferable across TAPPs; minor technique-specific additions. **Always start from `tapp_files/Template TAPP Group 1.csv`** when building or reviewing Group 1 for any TAPP — it is the canonical field list, tier assignments, and descriptions for all cross-TAPP Group 1 fields. |
| 2. Samples | Target material type (protocol scope), sample form and preparation method (protocol), and per-analysis sample identity (sample name, persistent identifier such as IGSN). Protocol fields describe what the technique is designed to measure; analysis fields identify what was actually analyzed. |
| 3. Instrument & Software | Hardware configuration — the instruments, detectors, and ancillary components used — and the software for acquisition and data reduction. Applies to all measurement techniques: spectrometers, diffractometers, imaging systems, sensors, etc. Hardware fields (instrument manufacturer, model, detector configurations) are D=Read-Only since changing hardware constitutes a different protocol. **Software fields (acquisition software, data reduction software) are D=Editable** — a minor version update does not constitute a new protocol, so analysts may record the version actually used. |
| 4. Measurement Information | Instrument operating conditions and tuning parameters, acquisition settings (timing, spatial, spectral, or other measurement parameters), and the identity of what is being measured (chemical variable, spectral range, physical property, imaging parameter, etc.). The most technique-specific group and typically the largest. |
| 5. Data Processing | Data reduction strategy including calibration and standardization approach, signal or data selection and integration, correction procedures (interferences, matrix effects, drift), normalization, and uncertainty propagation. Mix of protocol-level design choices and analysis-level outcomes. |
| 6. Quality Control & Uncertainty | Reference materials used, detection and quantification limits, precision, and accuracy. Protocol-level fields describe the QC design; analysis-level fields record QC outcomes from the actual session. **Primary calibration standards and secondary reference materials are C=Basic, D=Editable**: the protocol commits to a set of reference materials (mandatory to specify), but material exhaustion or availability may require the analyst to use a substitute at analysis time. |

### Blank rows between groups

One blank row separates each group from the next. Do not use more than one blank row. Blank rows have no content in any column.

---

## Mode Flag Columns

Mode flag columns start at column H and extend one column per analytical mode. The number of mode flag columns and their labels are defined in Phase 0 (Technique Scoping) and remain fixed for the lifetime of the TAPP.

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

Every TAPP includes four standard coupling fields at the end of Group 1, after Protocol Reference(s). These document multi-technique workflows where the same sample or aliquot is analyzed by more than one technique and the results are designed to be interpreted together or where one technique provides input to another.

| Field | C tier | D tier (default) | Notes |
|---|---|---|---|
| Coupled Technique(s) | Advanced | Editable | Technique-specific TAPPs may adjust D tier; most protocols are not always coupled |
| Coupling Description | Advanced | Editable | Free text; must address both the functional relationship and the analytical sequence |
| Coupled Protocol DOI | N/A | Advanced | Analysis-level only; may be "pending" or point to a publication DOI if no protocol registered |
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

**Group 1 (Protocol Identification) — all fields**
Group 1 is fully cross-TAPP. Always build it from `tapp_files/Template TAPP Group 1.csv`. Do not rename, reorder, or re-tier any Group 1 field without updating the template and all existing TAPPs.

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
- Protocol-Level Tier: Basic
- Analysis-Level Tier: Read-Only
- Data Type: Controlled vocabulary
- Mode flags: Y for all modes defined for that TAPP
- Allowed values: exactly the mode flag column labels defined in Phase 0 for that TAPP (e.g., "Spot", "Transect", "Mapping" for LA-ICP-MS; "Single-volume", "Multi-volume stitching" for Lab-XCT)
- For multi-mode protocols: list all applicable modes separated by semicolons

**Purpose and distinction from mode flag columns:**
"Analytical Mode" is a protocol-level *declaration* — a human-readable statement of what kind of measurement the protocol covers, required for any user reading or registering the protocol. The mode flag columns (Y/N per field) serve a different function: they indicate which fields apply to which mode and drive filtered sub-TAPP views. These two structures are complementary, not redundant.

**Distinction from mode-specific sub-strategy fields:**
"Analytical Mode" declares the top-level mode. Some TAPPs also have mode-specific sub-strategy fields that coexist with it:
- "Analytical Sub-mode" (TEM) — records the specific technique within a TEM mode (BF-TEM, HAADF-STEM, SAED, PED, etc.)
- "EDS Acquisition Mode" (SEM, EPMA, TEM) — records the spatial acquisition sub-strategy within EDS (point, linescan, map)
- "Beam Mode" (EPMA, SEM) — records the physical beam configuration (focused, defocused, rastered)

These are not replacements for "Analytical Mode" and should not be confused with it.

**Single-mode techniques:** Even if a technique has only one possible mode (e.g., a technique with a single fixed acquisition geometry), include "Analytical Mode" so that protocol records are self-describing and consistent across the TAPP library.

**"Analytical Mode" allowed values must mirror the mode flag column labels exactly:**
The controlled vocabulary for "Analytical Mode" must use the exact strings that appear as mode flag column headers in that TAPP (defined in Phase 0). Do not paraphrase, abbreviate, or substitute synonyms. This ensures that a protocol declaring `Analytical Mode = WDS Point Analysis` is unambiguously linked to the `WDS Point Analysis` mode flag column, and that sub-TAPP filtering behaves correctly. If mode flag column labels are ever renamed in a future revision, the "Analytical Mode" allowed values must be updated in the same patch.

---

### Rule 4 — Propagation obligation when a shared field is modified

Whenever a field covered by Rules 1–3 is added, renamed, re-tiered, or has its description substantively changed in any one TAPP, the author is obligated to propagate that change to every other TAPP that contains the same field **in the same patch or revision cycle**. Deferred propagation is not permitted — it creates silent inconsistency across the library.

**Steps:**
1. Identify all TAPPs that contain the field being changed (search across all `*_TAPP_v*.csv` files).
2. Apply the change to each affected TAPP, incrementing its version number.
3. Document the propagation in the patch script header listing all files modified.
4. If a specific TAPP intentionally diverges (Rule 2 permitted divergence), record that decision in `references/precedents.md` rather than silently omitting the propagation.

---

### Field names

**Level-neutral naming**: Field names must not encode protocol-level or analysis-level framing. Avoid "Default", "Target", "Achieved", "Typical", "Actual" as prefixes or suffixes that signal which level a value belongs to. The tier columns (C and D) carry that information. Use Column B (Description) to clarify that the protocol registers a target or typical value and that analysts may adjust within allowed bounds.
- ✓ "Laser Fluence (Energy Density)", "Carrier Gas and Flow Rate", "Voxel Size"
- ✗ "Default Laser Fluence", "Carrier Gas and Default Flow Rate", "Target Voxel Size"

**Exceptions — "Target" retained for scope-defining fields**: Two field types use "Target" because it denotes the *material or feature type the protocol is designed to analyze*, not a value with a later "achieved" counterpart:
- "Target Material" — the material type the protocol is designed to analyze
- "Target Feature(s)" — the microstructural features or properties the protocol is designed to characterize

**"(Measured)" companion field**: Use to distinguish the analysis-level measured value from the protocol-level acceptance criterion when a split is required (see Q3 in `references/field-review.md` and Oxide Production in `references/precedents.md`).
- Protocol field: "Oxide Production Method and Threshold" (the criterion)
- Analysis field: "Oxide Production" (the measured value)

**"(Mode Only)" suffix**: Use when a field is restricted to a single mode.
- ✓ "Raster Line Spacing (Mapping Only)"

**"Protocol" vs. "Method"**: Use "Protocol" when referring to the registerable protocol object. Use "Method" only for assessment methods, calculation methods, or sub-procedures.
- ✓ "Protocol Name", "Protocol DOI", "Funding Source for Protocol Development"
- ✓ "Detection Limit Method", "Signal Integration Interval Method"
- ✗ "Method Name", "Method DOI" — use "Protocol Name", "Protocol DOI"

**"Analyte-Specific" vs. "Element-Specific"**: Always use "Analyte-Specific". Techniques may measure molecules, isotope ratios, spectral features, or physical properties rather than individual elements.

### Vocabulary for common concepts

| Preferred term | Avoid | Reason |
|---|---|---|
| Protocol | Method (for the registered protocol object) | Precise vocabulary; see definitions above |
| Analyte-Specific | Element-Specific | Technique-agnostic |
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
| Controlled list | Value must be one of a defined set; list allowed values in Column F |
| Numeric (unit) | A number with a specific unit; state the unit in parentheses, e.g., Numeric (W), Numeric (Hz), Numeric (µm) |
| Numeric + unit | A number where the unit is variable and must be stated by the user |
| Boolean | Yes / No only |
| Integer | Whole number with no unit |
| Date | YYYY-MM-DD format |
| URI / DOI | A persistent identifier, URL, or DOI |
| URI / IGSN | An IGSN-format sample identifier |
| Text / URI | Either free text or a URI reference |

**For all Controlled list fields**, Column F must include the following options in addition to the technique-specific values: `N/A | None | Other: specify`. This ensures users can always document the absence of a feature or an unlisted option without leaving the field blank.

Column F format: all allowed values separated by ` | ` (space-pipe-space). If the list exceeds approximately 8 values, abbreviate with a note "see Legends sheet for complete list."

---

## File Management: CSV and xlsx

### CSV (source of truth)

The CSV is the canonical version of the TAPP. All edits are made here.

- Filename: `[Technique]_TAPP_v[N].csv`
- Encoding: UTF-8
- Column headers in row 1, content from row 2
- Group header rows: populate Column A with the group name (e.g., "1. Protocol Identification"); all other columns blank or N for mode flags
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
| B | Description / Purpose | Full field description | No WDS/EDS/Analyte-Specific labels here — those go in Column G |
| C | Protocol-Level Tier | Basic / Advanced / N/A | |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced | D=N/A is not valid |
| E | Data Type | Controlled vocabulary — see Data Type Vocabulary | |
| F | Example / Allowed Content | Examples or controlled list values | No "Analyte-Specific; " prefixes — that label goes in Column G |
| G | Comments | Short field-level labels: "WDS specific", "EDS specific", "Analyte-Specific", "WDS specific; Analyte-Specific", etc. | Keeps B and F uncluttered |
| H | Last Update | YYYY-MM-DD date of most recent substantive edit | |
| H+1 … H+n | Mode flag columns | One column per mode; Y or N | Labels set in Phase 0 |
| (after modes) | Literature Assessment | Sentinel column — header exactly `Literature Assessment`; all data rows empty | Marks boundary before lit assessment columns |
| (after sentinel) | Literature assessment columns | One column per paper extracted in Phase 3 | Starting letter depends on number of modes |

### Approximate column widths for xlsx export

| Column | Width (characters) |
|---|---|
| A (Metadata Item) | 35–40 |
| B (Description) | 65–70 |
| C (Protocol-Level Tier) | 14 |
| D (Analysis-Level Tier) | 14 |
| E (Data Type) | 18 |
| F (Example/Allowed Content) | 45 |
| G (Comments) | 22 |
| H (Last Update) | 14 |
| Mode flag columns | 12 each |
| Sentinel column (`Literature Assessment`) | 4 (narrow; data rows are empty) |
| Literature assessment columns | 28 each |

---

## Legends Sheet

Every TAPP xlsx must include a Legends sheet. The CSV has no Legends sheet — it is generated at export time. The Legends sheet must contain:

**Table 1: Protocol-Level Tier definitions** — Basic, Advanced, N/A with full definitions

**Table 2: Analysis-Level Tier definitions** — Read-Only, Editable, Basic, Advanced, N/A with full definitions

**Table 3: Mode column definitions** — one row per mode defined in Phase 0, with the mode label and its full definition; plus Y and N definitions

The Legends sheet text must be consistent with the definitions in this conventions file.

---

## Version and Date Tracking

Column H (Last Update) contains the date of the most recent substantive edit to each row, in YYYY-MM-DD format. Initialize all rows to the creation date for a new TAPP.

**Version numbering:**
- Major structural revisions (field additions/removals, tier changes, mode flag changes): increment integer version (v4 → v5)
- Description updates, example content improvements, no structural changes: decimal update (v5.1) or column G date update only

TAPP filenames: `[Technique]_TAPP_v[N].csv` and `[Technique]_TAPP_v[N].xlsx`
