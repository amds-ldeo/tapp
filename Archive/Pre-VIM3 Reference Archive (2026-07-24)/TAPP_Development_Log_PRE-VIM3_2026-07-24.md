> **⚠️ ARCHIVED — PRE-VIM3 SNAPSHOT (2026-07-24)**
> This file reflects TAPP terminology *before* alignment with BIPM VIM3 (JCGM 200:2012): "Protocol" = the
> registerable, DOI-bearing object; "Procedure"/"Analysis" = the analysis-level execution. Kept for
> historical record only — **do not use for current TAPP work.** Current version lives at the original
> path in the TAPPs project (same filename, without this suffix).
>
> See the "Aligning TAPP Vocabulary with VIM3" migration plan for the full rationale.

---

# Astromat TAPP Development Log

**Project:** Technique-Aligned Protocol Profiles for Astromat / EarthChem  
**Maintained by:** Astromat curation team  
**Last updated:** 2026-06-16

---

## How to Use This Log

This file records decisions, rationale, open questions, and cross-version changes for all TAPPs under development. It is the authoritative record of *why* something was done, not just *what* was done (the CSV files show *what*).

**Add an entry** whenever you:
- Make a non-obvious tier assignment with a specific rationale
- Deviate from a precedent or add a new one
- Defer a decision explicitly (record the question and what evidence would resolve it)
- Identify a topic that needs community discussion
- Complete a development phase

**Format convention for entries:**  
`YYYY-MM-DD | [TAPP name or CROSS-TAPP] | brief title | body`

---

## Version Control Note

There is currently **no git repository**. Version control is by filename only (e.g., `Lab-XCT_TAPP_v5.csv`). The CSV is the source of truth; xlsx files are generated artifacts. Do not edit xlsx files directly.

---

---

# Part I — Cross-TAPP Conventions & Decisions

These apply to every TAPP in the library. Changes here require review across all active TAPPs.

---

## Column Structure (all TAPPs)

| Col | Content | Notes |
|---|---|---|
| A | Metadata Item | Field name; must follow level-neutral naming rule |
| B | Description | Full field definition and scope |
| C | Protocol-Level Tier | Basic / Advanced / N/A |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced |
| E | Data Type | Controlled vocabulary |
| F | Example / Allowed Content | Examples or controlled list values |
| G | Comments | Short field-level labels (e.g., "Analyte-Specific") |
| H | Last Update | YYYY-MM-DD |
| I … | Mode flag columns | One per mode; start at col I (index 8); order by decreasing frequency |
| — | Sentinel column | Header exactly "Literature Assessment"; cells empty; marks mode/lit boundary |
| — | Literature assessment columns | One per distinct protocol extracted from paper |

**Script dependency:** `scripts/tapp_to_xlsx.py` expects Comments at G (index 6), Last Update at H (index 7), and mode flags starting at I (index 8). TAPPs missing the Comments column cause the script to misidentify mode columns. All TAPPs must have this column.

---

## Tier System

### Protocol-Level Tier (Column C)
| Value | Meaning |
|---|---|
| Basic | Mandatory for protocol registration |
| Advanced | Optional but strongly recommended |
| N/A | Not applicable at protocol level (analysis-level field only) |

### Analysis-Level Tier (Column D)
| Value | Meaning |
|---|---|
| Read-Only | Imported from protocol; cannot be changed by analyst. Also used for fields relevant only at protocol level (value inherited, shown read-only). |
| Editable | Imported from protocol; may be adjusted within protocol-defined bounds at analysis time |
| Basic | Mandatory user input at analysis time; cannot be pre-specified in protocol |
| Advanced | Optional user input at analysis time; recommended for complete documentation |

**Critical invariant:** D=N/A is **not a valid tier**. Every field must have a meaningful analysis-level assignment. (D=N/A was removed because it behaved identically to D=Read-Only in the pipeline — decision recorded in `references/precedents.md` §11.)

**C/D asymmetry pattern:** C=Advanced + D=Basic is valid and important — protocol optionally specifies the field; analysis mandatorily documents it. Example: Detection Limit (C=Advanced, D=Basic).

**Read-Only rule:** If C=Advanced (field may be void in the protocol), the analysis-level tier should almost never be Read-Only (importing a blank would be meaningless). Use Editable or Basic instead.

---

## Field Naming Rules

1. **Level-neutral:** No "Default", "Target" (when meaning ideal), "Achieved", "Typical", "Actual" as prefix/suffix. The tier columns encode level.
2. **Exceptions:** "Target Material" and "Target Feature(s)" retain "Target" because it denotes the material/feature type the protocol is designed to analyze — not a value with a later "achieved" counterpart.
3. **"Protocol" vs "Method":** Use "Protocol" for the registerable object (Protocol Name, Protocol DOI). Use "Method" only for sub-procedures, calculation methods, or assessment methods.
4. **"Analyte-Specific" not "Element-Specific":** Use Analyte-Specific to remain technique-agnostic.
5. **"(Mode Only)" suffix:** Use when a field applies to a single mode only, e.g., "Raster Line Spacing (Mapping Only)".
6. **Template:** Every new TAPP begins Group 1 from `tapp_files/Template TAPP Group 1.csv` to prevent field name and tier drift.

---

## Structural Decisions (from `references/precedents.md`)

These have been formally adopted and propagated across TAPPs. See `references/precedents.md` for full rationale.

| # | Decision | Key rule |
|---|---|---|
| 1 | Protocol value vs. measured value | When protocol specifies a threshold/criterion and analysis records the actual measurement, split into two fields with different tier assignments |
| 2 | Acceptance criterion vs. measured value | [Concept] Method and Threshold (C=Basic, D=Read-Only) + [Concept] (C=N/A, D=Basic) |
| 3 | Single merged field with D=Editable | Use when protocol scope and analysis execution describe the same quantity at different stages (e.g., Analyte) |
| 4 | Editable for software fields | Minor version updates ≠ new protocol; D=Editable for acquisition/reconstruction/analysis software |
| 5 | Reference materials: C=Basic, D=Editable | Protocol commits to specific RM; substitution allowed at analysis time due to availability |
| 6 | Signal smoothing: Y for all modes with caveat | Set mode flag=N only when genuinely inapplicable; use description caveat when applicable but problematic |
| 7 | D=Editable when C=Advanced (field may be void) | If protocol-level tier is Advanced (may be blank), Read-Only at analysis level would import a blank |
| 8 | C=Advanced + D=Basic asymmetry | Valid for QC fields that require accumulated session data but are mandatory for data submission |
| 9 | Beam geometry: D=Read-Only | Categorical protocol design choice; changing beam mode = different analytical approach |
| 10 | Mapping dimension vs. step size | Map extent (sample-determined) = C=N/A, D=Basic; Step size (resolution control) = C=Basic, D=Editable |
| 11 | Coupled technique fields (4 standard) | Group 1: Coupled Technique(s), Coupling Description (C=Advanced, D=Editable); Coupled Protocol DOI, Coupled Dataset or Publication Reference (C=N/A, D=Advanced) |
| 12 | Protocol DOI: C=N/A, D=Basic | DOI does not exist at registration time; mandatory at analysis level; "Pending" is acceptable |

---

## Workflow Phases

| Phase | Lead | Purpose | Output |
|---|---|---|---|
| 0 | Human (AI supporting) | Technique scoping, mode decision, seed papers | Scope document, mode flag assignments |
| 1 | AI | Generate preliminary TAPP from seed papers/templates | Draft CSV, all D-tiers as TBD |
| 2 | Human (AI supporting) | Structured field review — tiers, modes, splits | Revised CSV with all tiers assigned |
| 3 | AI (human validates) | Literature assessment against 8–12 papers | TAPP CSV with assessment columns appended |
| 4 | Human (AI implements) | Post-assessment revision — tiers, missing fields, descriptions | Final TAPP version |

**Phase 3 rule:** Integrate assessment directly into main TAPP CSV (no separate draft CSV). Read original papers; do not use summaries. One column per *distinct protocol*, not per paper. Values: directly stated text | "N" (not reported) | "N/A" (genuinely inapplicable).

**Phase 4 workflow note:** When adding new fields discovered during Phase 4, add them at the *end of their logical group* and populate the literature assessment columns at the same time. This avoids requiring a second round of paper reading.

---

---

# Part II — TAPP: Lab X-ray Computed Tomography (Lab-XCT)

**Current version:** v5  
**File:** `XCT/Lab-XCT_TAPP_v5.csv`  
**Status:** Phase 4 in progress  
**Fields:** 78 content fields  
**Modes:** Single-volume (col I), Multi-volume stitching (col J)  
**Assessment protocols:** 16 distinct protocols from 11 papers

---

## Scope & Mode Decisions

**Technique scope:** Lab-based X-ray CT using industrial/geological microfocus or rotating-anode sources. Excludes: synchrotron XCT (SR-XCT, separate TAPP planned), medical/clinical CT (deferred — see Open Questions), preclinical/small-animal CT (deferred), neutron CT (NCT, separate TAPP planned).

**Mode split decision:** Two modes — Single-volume (most common) and Multi-volume stitching (for samples too large for single FOV). Decided against separate TAPPs for these modes: same instrument, same physics, same data reduction; stitching is an additional processing step, not a different technique. Multi-volume-specific fields carry Y only in the Multi-volume stitching column.

**Excluded from Phase 3 assessment:** Hanna & Ketcham 2018 (review) and Withers et al. 2021 (methods primer) — used as background references, not protocol sources. Withers 2021 was used to validate Output Data Format as C=Basic (appears in Withers minimum reporting checklist).

---

## Version History

### v1.0–v1.3 (Phase 0–1, dates approximate)
- Phase 0 scoping: XCT scope defined, two modes established
- Phase 1: Preliminary TAPP generated
- v1.3: Key structural changes — "Companion NCT Acquisition" replaced by four Coupled fields (rows 15–18); level-neutral naming applied throughout; D-tiers still TBD

### v2 (Phase 2 complete — 2026-05)
**Structural fix:** Added Comments column at G (index 6), shifting Last Update to H and mode flags to I, J. Previously, mode flags were at H, I (indices 7, 8), causing `tapp_to_xlsx.py` to detect only one mode column instead of two (script starts scanning for mode flags at index 8). v1.1–v1.3 xlsx exports were all affected.

**Tier assignments (selected highlights):**
- Laboratory, Laboratory ID: D=Editable (instrument can move; lab name can change)
- Funding Source for Analysis: D=Basic (can be reported as "None")
- Beam Hardening Correction Parameter: C=N/A → C=Advanced, D=Editable (protocol can optionally specify a default; analyst adjusts)
- Spatial Resolution: C=N/A, D=Advanced
- Segmentation Threshold Values: provisional C=Advanced, D=Advanced (later revised)
- Output Data Format: C=Advanced → **C=Basic** (Withers 2021 minimum requirement)

**Field consolidations:**
- "Target Voxel Size" + "Achieved Voxel Size" merged to single "Voxel Size" (C=Basic, D=Editable) — protocol registers target; analyst documents achieved value

**Column structure after v2:**
`Metadata Item | Description | Protocol-Level Tier | Analysis-Level Tier | Data Type | Example/Allowed Content | Comments | Last Update | Single-volume | Multi-volume stitching | Literature Assessment`

### v3 (Phase 3 complete — 2026-05)
**Literature assessment:** 15 distinct protocols from 11 papers appended as columns 11–25.

| Protocol column | Paper | Instrument | Sample |
|---|---|---|---|
| 1 | Eckley 2024 (JSC Scan Record) | Nikon XTH 320 | Bennu particle |
| 2 | Genge et al. 2025 (Nat. Commun.) | Zeiss Versa | Ryugu A0180 |
| 3 | Neuman/Shearer 2025 (JGR/SSR) | NSI custom, UTCT | Apollo 17 core 73002, multi-vol |
| 4 | Neuman et al. 2025 (JGR) | NSI custom, UTCT | Apollo 17 core 73001, multi-vol |
| 5 | Shearer et al. 2024 (SSR) | Nikon XTH 320 | 73001 CSVC engineering |
| 6 | Shearer et al. 2024 (SSR) | Nikon XTH 320 | ANGSA particles |
| 7 | Tomkinson et al. 2015 (MAPS) | Nikon Metris XTH 225 | NWA 5790 nakhlite |
| 8 | Charles et al. 2018 (MAPS) | GE eXplore speCZT | NWA 801 CR2 chondrite |
| 9 | Treiman et al. 2022 (MAPS) | NIST-NeXT NXCT | EET 87503 howardite |
| 10 | Glavin et al. 2023 (MAPS) | Nikon XTH 320 | Murchison CM2 |
| 11 | Nascimento-Dias et al. 2019 (Appl. Radiat. Isot.) | Bruker Skyscan 1173 | NWA 8277 + NWA 6963 |
| 12 | Richard et al. 2019 (Chem. Geol.) | Zeiss Xradia 510 Versa | Olivine (UNAM) |
| 13 | Richard et al. 2019 (Chem. Geol.) | Nikon XTH 320/225 | Synthetic quartz (Strathclyde, combined) |
| 14 | Richard et al. 2019 (Chem. Geol.) | Phoenix Nanotom S | Fluid inclusion minerals C–I (Lorraine) |
| 15 | Tait 2014 (Thesis) | XRADIA XRM500 | Watson 012 H7 chondrite |

### v4 (Phase 3–4 corrections — 2026-05)
**Corrections to Phase 3 data:**

- **Neuman 2025 voxel size:** Original assessment recorded "12.9 µm" for both Neuman protocols. On re-reading the paper, this value does not appear. The paper does not state the voxel size and defers to Ketcham et al. 2022. Both entries corrected to "N (voxel size not stated; see Ketcham et al. 2022)". *Root cause:* 12.9 µm likely sourced from Ketcham et al. 2022 in error during the initial assessment.

- **Richard Strathclyde split:** Original col 13 combined two distinct scan setups for the same sample (Table 1, Section 3.3). Split into col 13 = Whole sample (160 kV, 71 µA, 11.4 W, 25 µm, 0.708 s/projection, 37 min) and col 14 = ROI high-res (160 kV, 46 µA, 7.4 W, 7.7 µm, 1.415 s/projection, 75 min). Total protocols: **16 from 11 papers**.

**Tier change:**
- Segmentation Threshold Values: D=Advanced → **D=Editable**. Rationale: protocol can register default/expected threshold values or methodology; analyst applies and adjusts per dataset. The "or Criteria" in the field name captures protocol-level methodology (Editable pattern), not just analysis-time measurement.

**Text/unit updates:**
- Accelerating Voltage, Tube Current, X-ray Power, Exposure Time: descriptions and examples updated to explicitly allow range reporting (e.g., "90–115 kV") for protocols covering multiple sample types with varied settings
- Voxel Size example: clarified that µm is canonical; µm/pixel is acceptable equivalent; µm³/voxel is voxel *volume* and is NOT a valid unit for voxel size
- Spatial Resolution example: same clarification; µm³/voxel is not a spatial resolution unit

**New fields (with literature assessment populated):**
- `Total Scan Duration` (C=N/A, D=Advanced): added at end of file initially
- `Output Bit Depth` (C=Advanced, D=Editable): added at end of file initially; lit assessment: Eckley=16-bit, Genge=16-bit, Charles=16-bit, Richard ZEISS=32-bit, others N

### v5 (Phase 4 continued — 2026-05-15)
**Accelerating Voltage unit conventions:**
- Description updated: keV (max Bremsstrahlung photon energy) and kV (tube voltage) are numerically equivalent for polychromatic lab XCT: E_max[keV] = V[kV]. Record the unit as stated in the source with a parenthetical note.
- Treiman 2022: `'90 keV max (paper reports max Bremsstrahlung photon energy; numerically equivalent to 90 kV tube voltage)'`
- Tomkinson 2015: `'120 keV (reported in paper as "accelerating voltage of 120 keV"; likely typo for 120 kV)'`
- Glavin 2023: `'160 keV (paper reports as X-ray photon energy; equivalent to 160 kV tube voltage)'`
- Charles 2018 tube current: 32 mA retained as-is (GE eXplore speCZT is a preclinical scanner; mA-range current is correct for this instrument class, not a typo)

**New field:**
- `Rotation Step Size` (C=Advanced, D=Editable): inserted after Number of Projections in Group 4. Lit assessment: Charles=0.4°/view, Glavin=0.115°, Nascimento-Dias=0.4°/step; others N. Rationale: some papers report step size as the primary rotation parameter without stating N_projections directly; having a dedicated field avoids inferring derived values.

**Field relocations:**
- Total Scan Duration moved to end of Group 4 (after Minimum Sub-volume Overlap)
- Output Bit Depth moved to end of Group 5 (after Sub-volume Overlap)

### v6 (Phase 4 continued — 2026-05-15)
**Group 6 (Quality Control & Uncertainty) — all 10 field descriptions revised** based on Withers et al. (2021, *Nat. Rev. Methods Primers*) and Hanna & Ketcham (2017, *MAPS*), following the descriptive-not-instructional convention (descriptions explain what metadata is expected; analytical guidance belongs to the analyst).

Key additions per field:
- **Spatial Resolution**: Added PSF/Ketcham & Hildebrandt 2014 and ASTM E1441-11 as formal measurement references; Brenner–Weiss formula noted as geometric estimate. Unit clarification retained (µm, not µm³/voxel).
- **Beam Hardening**: Added "darker interior and brighter edges" as the characteristic visual signature.
- **Ring Artifacts**: Added caveat that ring correction can alter linear geological features oriented tangentially to the rotation axis (fractures, veins).
- **Metal Streak**: Trimmed to two main forms — starburst streaks and shadowing behind dense phases.
- **PVE Criteria & Assessment**: Added Blob3D as the canonical PSF-based correction tool.
- **Minimum Resolvable Feature Size**: Added Withers et al. 3× (identification) and 10× (morphometry) voxel rules as named references.
- **SNR**: Stripped prescriptive content; retained definition and measurement convention.
- **Cross-Validation Requirement**: Added He pycnometry alongside BSE/SEM-EDS as common validation approaches.
- **Cross-Validation Outcome**: Added note that BSE provides 2D section vs. CT 3D volume; removed prescriptive error thresholds.

Also fixed: title row (`Lab-XCT_TAPP_v5`) present in v5 CSV but absent from all other TAPPs — stripped from v6 to align with project convention. v5 CSV retains its title row for archival continuity.

### v7 (Phase 4 — consistency pass — 2026-05-15)
Full-TAPP consistency pass. 10 targeted changes:

**Data type fixes (3):**
- `Total Scan Duration`: `Numeric (Unit)` → `Text (free)` ("Unit" is a placeholder; mixed min/h units in practice)
- `Rotation Range`: `Numeric (degrees)` → `Numeric (°)` (consistency with Rotation Step Size)
- `Output Bit Depth`: `Categorical` → `Controlled list` (consistency with Detector Binning and similar fields)

**Description fixes (3):**
- `Flat Field Correction`: removed prescriptive "should be Yes for any protocol producing data used in publication" sentence
- `Output Data Format`: removed "and bit depth" from description (bit depth captured by separate Output Bit Depth field); removed bit-depth prefixes from Example column
- `Minimum Sub-volume Overlap`: softened Eckley 2025 language from prescriptive ("recommend ≥500 slices") to descriptive ("report that 500 slices were used…")

**Comments column (4):** Added "Multi-volume only" label to Number of Sub-volumes, Minimum Sub-volume Overlap, Sub-volume Stitching and Registration Method, Sub-volume Overlap.

**No changes needed:** Acquisition Software (0% reporting reflects literature gap, not TAPP error); short descriptions for Technique/Laboratory/Laboratory ID/Protocol Start Date (complete for simple fields); no naming neutrality violations found; no empty Example cells.

---

## Key Decisions — Lab-XCT

| Date | Decision | Rationale |
|---|---|---|
| 2026-05 | Two modes: Single-volume / Multi-volume stitching | Same instrument and physics; stitching is processing step, not technique change |
| 2026-05 | Voxel Size: single field, D=Editable | Protocol registers target; analyst documents achieved; no information-type difference between levels |
| 2026-05 | Output Data Format: C=Basic | Appears in Withers 2021 minimum reporting requirements |
| 2026-05 | Environmental conditions excluded | Lab XCT is not environmentally sensitive; not worth mandatory documentation |
| 2026-05 | Segmentation Threshold Values: C=Advanced, D=Editable | Protocol can register default/expected threshold; analyst adjusts per dataset |
| 2026-05 | X-ray Energy: no separate field | E_max[keV] = V[kV] for polychromatic Bremsstrahlung; fully derivable; would be a duplicate of Accelerating Voltage |
| 2026-05 | Rotation Step Size: C=Advanced | Not always derivable (some papers report only step size, not N_projections); dedicated field avoids inference |
| 2026-05 | Charles 2018 (GE eXplore speCZT) retained in assessment | Informative for assessing TAPP coverage of preclinical CT; classified as "Detailed" in paper_registry pending future review |
| 2026-05 | Range notation accepted for Accelerating Voltage, Tube Current, etc. | Richard 2019 varied settings across samples; descriptions/examples updated to accept "X–Y kV" notation |
| 2026-05 | keV vs kV flag convention | Record value as stated in source; add parenthetical note when source uses keV for what is the tube voltage |

---

## Development Status — Lab-XCT

**2026-05-15 | PAUSED FOR EXPERT REVIEW**
v7 is the current release candidate. Sent to domain expert(s) for review before protocol registration and DOI assignment. Development resumes after expert feedback is received and incorporated.

Files for review:
- `XCT/Lab-XCT_TAPP_v7.csv` (source of truth)
- `XCT/Lab-XCT_TAPP_v7.xlsx` (formatted, for sharing)

Next step on return: incorporate expert feedback → v8 (if revisions needed) → protocol registration.

---

## Open Questions — Lab-XCT

| Status | Question | Context / Evidence needed to resolve |
|---|---|---|
| ⚠️ Pending | Ketcham et al. 2022 as additional lit assessment source | Contains voxel size values for Neuman 2025 protocols (12.9 µm likely from here); consider adding as col 17 in a future version |
| ⚠️ Pending | Shearer 2024 DOI | Not extracted from paper; needs manual lookup |
| ⚠️ Pending | Detector Gain field (Eckley JSC scan record only) | Only 1/16 protocols reports gain in dB; insufficient to add as field; revisit if more protocols are assessed |
| ⚠️ Pending | Charles 2018 GE eXplore speCZT classification | Preclinical/small-animal CT vs. Lab-XCT boundary; medical CT TAPP decision deferred |
| 🔲 Future | Hanna & Ketcham 2018 as seed paper for Phase 5 field review | Comprehensive XCT methods reference; not used in Phase 3 lit assessment (review paper, no specific protocol data) |

---

---

# Part III — TAPP: Laser Ablation Q/SF-ICP-MS (LA-Q/SF-ICP-MS)

**Current version:** v3  
**File:** `LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v3.csv`  
**Status:** Phase 2 complete (cross-TAPP ICP-MS consistency revisions applied); literature assessment 13 protocols across 10 papers  
**Fields:** 110 content fields  
**Modes:** Spot (col I), Transect (col J), Mapping (col K) — 3 modes  
**Assessment protocols:** 13 protocols from 10 papers (cols 12–24)

⚠️ *Note: The detailed decision history for LA-ICP-MS v1–v10 (old naming) has not been backtracked into this log. The entries below reflect what can be inferred from the current TAPP file and from `references/precedents.md`. The TAPP was renamed and restructured to the new path/naming convention in a session not documented here (date unknown, approximately 2026-05 to 2026-06).*

**2026-05-15 | TASK DEFERRED:** Full logbook backtracking for LA-ICP-MS and EPMA (v1–vN decision history, key decisions, open questions) to be completed in a dedicated future session by reviewing session transcripts. Lower priority than continuing active TAPP development.

---

## Version History

### v1 (2026-06 — renaming/restructuring from old LA-ICP-MS v11)
TAPP content carried over from the old `LA-ICP-MS/LA-ICPMS_TAPP_v11.csv` (94-field version under the old naming convention). Renamed and moved to `LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v1.csv`. 13 literature assessment protocols from 10 papers already integrated. Decision history for the original v1–v11 development not reconstructed in this log.

### v2 (2026-06-01 — Analytical Mode addition)
Cross-TAPP consistency: added `Analytical Mode` (C=Basic, D=Read-Only) at the start of Group 4, before `Laser Spot Geometry`. Field serves as the protocol-level declaration of measurement type (Spot / Transect / Mapping), distinct from the mode flag columns (cols I–K) which indicate per-field applicability.

### v3 (2026-06-17 — cross-TAPP ICP-MS consistency pass)
Comprehensive alignment of ICP-MS-relevant fields with Solution Q-ICP-MS TAPP v4 and Solution SF-ICP-MS TAPP v4. Net: +15 content fields (110 total).

**Fields added (Group 3) — instrument-level:**
- `Instrument Serial Number` (C=Advanced, D=Editable): cross-TAPP alignment; minor version updates ≠ new protocol per Precedent 4
- `Torch Type` (C=Advanced, D=Read-Only): cross-TAPP alignment; torch geometry is a fixed instrument property
- `Collision/Reaction Cell (CRC) Configuration` (C=Basic, D=Read-Only, Q-ICP-MS only): STD / KED / DRC / ICP-MS/MS; closes documentation gap for Q instruments (e.g., Agilent 8900 in assessed protocols)

**Fields reorganized (Group 4) — gas flow rates:**
- `Auxiliary and Cool Gas Flow Rates` → split into two separate fields: `Coolant Plasma Gas Flow Rate` and `Auxiliary Gas Flow Rate` (matching Solution TAPP field names)

**Fields added (Group 4) — analyte and signal acquisition:**
- `Monitored Isotopes` (C=Basic, D=Read-Only, both Q and SF): list of isotopes monitored for quality control but not reported as primary analytes; cross-TAPP alignment
- `Mass Resolution per Analyte` (C=Basic, D=Read-Only, SF-ICP-MS only): per-analyte mass resolution assignment (LR/MR/HR); cross-TAPP alignment with Solution SF-ICP-MS
- `E-scan Range` (C=Advanced, D=Read-Only, SF-ICP-MS only): electric scan range (% of center mass) for peak acquisition without re-scanning the magnet
- `Triple Scanning Mode` (C=Advanced, D=Read-Only, SF-ICP-MS only): whether each mass peak is scanned three times per cycle and results averaged
- `Signal Collection Mode` (C=Basic, D=Read-Only, Q-ICP-MS only): pulse counting / analog / dual — cross-TAPP alignment
- `Collision Gas Type` (C=Basic, D=Read-Only, Q-ICP-MS only): gas used in KED mode (typically He)
- `Collision Gas Flow Rate` (C=Basic, D=Editable, Q-ICP-MS only): He flow rate in KED mode
- `Cell Exit Discrimination Voltage` (C=Basic, D=Editable, Q-ICP-MS only): KED voltage applied at cell exit
- `Reaction Gas Type` (C=Advanced, D=Read-Only, Q-ICP-MS only): gas used in DRC mode
- `Reaction Gas Flow Rate` (C=Advanced, D=Editable, Q-ICP-MS only): DRC gas flow rate

**Fields renamed (Group 4):**
- `Spectrometer Dwell Time` → `Dwell Time per Mass` (C=Basic, D=Editable — mapping requires analyst adjustment per session; cross-TAPP naming alignment)

**Tier change (Group 4):**
- `RF Power`: D=Read-Only → D=Editable (minor session-to-session tuning adjustments do not constitute a new protocol)

**Fields added (Group 5) — data reduction:**
- `Isotope Dilution Data Reduction Method` (C=Basic, D=Read-Only): cross-TAPP alignment; captures ID spike + data-reduction approach for ID experiments

**Fields moved and renamed (Group 4 → Group 6):**
- `Drift Monitor Frequency` → `Calibration Standard Measurement Frequency` (C=Basic, D=Read-Only): moved from Group 4 to Group 6 for alignment with both solution TAPPs; renamed to match cross-TAPP terminology; literature assessment data preserved from original row

**Justified differences from Solution TAPPs (not to be changed):**
- `Guard Electrode`: C=Basic in LA (vs. C=Advanced in Solution SF) — solid-sample ablation produces larger plasma load fluctuations; guard electrode status is more critical to document
- Software fields (`Acquisition Software`, `Data Reduction Software`): D=Editable (Precedent 4, consistently applied)
- `Dwell Time per Mass`: D=Editable (mapping requires analyst adjustment; in Solution TAPPs it is D=Read-Only)
- `Analysis Sequence`: D=Editable (extra RMs added mid-session in LA workflows)
- `Number of Replicates`: C=N/A, D=Basic (analysis-determined in LA; not a protocol design choice)
- `Drift Correction Method`: intentionally absent (in LA-ICP-MS, IS normalization IS drift correction — not a separable design choice)

---

## Scope Decisions

**Technique scope:** Quadrupole and single-collector sector-field ICP-MS instruments coupled to laser ablation. Excludes MC (isotope-ratio focus, different metadata), ToF-MS (simultaneous spectrum, different metadata), TQ/MS² (reaction cell, different metadata) — each has its own future TAPP. Covers both ns and fs laser systems within one TAPP (laser pulse width is a protocol-level field, not a scope boundary).

**Mode split:** Three modes reflect the three primary acquisition geometries with distinct metadata requirements. Spot and transect are on a spectrum (point vs. line); mapping is substantially different (raster, spatial resolution metadata, smoothing constraints).

---

## Assessment Protocols (16 columns)

From v11 header, covering: Zhang 2022 (mapping + spot), Chernonozhkin 2021 (mapping, line scan + spot, spot), Chernonozhkin 2024 (mapping, ToF), Masuda 2024 (mapping), Mittlefehldt 2024 (spot), Nakanishi 2022 (spot), Navarro 2024 (spot + mapping), Zhang 2022 at-spectrosc (transect), Liu 2024 (spot), Liu 2025 ×2 (spot silicate + sulfide), Liu 2016 ×2 (spot silicates/oxides + phosphate). Note: one column is an LA-MC-ICP-MS protocol (Zhang 2022 at-spectrosc) and one is LA-ICP-ToF-MS (Chernonozhkin 2024); these were included to bridge toward future TAPPs.

---

## Legacy Workflow Note

`LA-ICP-MS/LA-ICPMS_lit_assessment_review.csv` exists as a standalone lit assessment review file — the legacy format. Per the feedback recorded in memory (`feedback_lit_assessment_workflow.md`), this approach is superseded: assessment is now integrated directly into the main TAPP CSV. This file should not be updated; the v11 CSV is the source of truth.

---

## Key Decisions — LA-ICP-MS (inferred from precedents.md)

The following decisions were first established during LA-ICP-MS development and later formalized as cross-TAPP precedents:

- Ablation Duration vs. Analysis Count Time: separate fields (Precedent 1)
- Oxide Production: two fields split by information type (Precedent 2/3)
- Analyte: single merged field with D=Editable (Precedent 4)
- Scan Speed tier assignment (Precedent 5)
- Signal Smoothing: Y for all modes with compatibility caveat (Precedent 6)
- Uncertainty Propagation: C=Advanced, D=Editable (Precedent 7)
- Signal Integration Interval Method: C=Basic, mode-universal (Precedent 8)
- Detection Limit: C=Advanced, D=Basic asymmetry (Precedent 9)
- Precision/Accuracy: combined method + value fields (Precedent 10)

---

## Open Questions — LA-ICP-MS

| Status | Question |
|---|---|
| ⚠️ Pending | TAPP Planning Table still shows "v1 in development" — needs update to reflect v11 and Phase completion status |
| 🔲 Future | LA-MC-ICP-MS TAPP: seed paper Zhang 2022 (At. Spectrosc.) in-situ Rb-Sr identified |
| 🔲 Future | LA-ICP-ToF-MS TAPP: seed paper Chernonozhkin 2024 identified |
| 🔲 Future | LA-ICP-TQ-MS TAPP: seed paper Masuda 2024 identified |

---

---

# Part IV — TAPP: Electron Probe Microanalysis (EPMA)

**Current version:** v4  
**File:** `EPMA/EPMA_TAPP_v4.csv`  
**Status:** Phase 3–4 complete; detailed decision history not yet reconstructed in this log  
**Fields:** 74 content fields  
**Modes:** Point Analysis (col I), Mapping (col J) — 2 modes  
**Assessment protocols:** 14 distinct protocols from 10 papers

⚠️ *Note: The detailed decision history for EPMA v1–v3 has not yet been backtracked into this log. A future session should review the EPMA session transcripts.*

---

## Scope Decisions

**Technique scope:** Wavelength-dispersive spectrometry (WDS) as primary technique; EDS as subordinate detector; WDS+EDS combined. These are sub-type modes within one TAPP, not separate TAPPs (same instrument platform, same sample preparation, shared metadata).

---

## Assessment Protocols (14 columns)

From v4 header: Ma 2015 (Caltech JEOL 8200), Hu 2020 (IGGCAS JEOL 8100), Liu 2016 ×2 (Cameca SX100 + JEOL 8200), Ma 2017 (Caltech JEOL 8200), Frank 2023 (Cameca SX100, JSC), Broussard 2026 (JEOL 8200, WashU), Seifert 2026 (JEOL 8530, JSC), Pang 2016 (JEOL 8100, Nanjing), McCoy 2025 ×2 (JEOL 8530F+, Smithsonian + Cameca SX-100, K-ALFAA), Zega 2025 (Cameca SX-100 Ultra, K-ALFAA), Barnes 2025 ×2 (JEOL 8230, CRPG + Cameca SX100, NHM).

---

## Open Questions — EPMA

| Status | Question |
|---|---|
| ⚠️ Pending | Decision history for v1–v3 not reconstructed |
| 🔲 Future | WDS dead time vs. EDS dead time asymmetry (Precedent 19) — confirm this is correctly implemented in v4 |

---

---

# Part V — Future Discussion Topics

These items require community input, architectural decisions by the Astromat/EarthChem team, or policy decisions beyond the scope of individual TAPP development.

---

## 1. NCT+XCT Simultaneous Acquisition — TAPP architecture

**Topic:** Should simultaneous neutron + X-ray CT acquisition (e.g., NIST-NeXT NXCT) be handled by a combined NCT+XCT TAPP or by separate Lab-XCT and NCT TAPPs linked via Coupled fields?

**Status:** Tentatively added to TAPP Planning Table (row 45) as a separate future TAPP, priority L. Flagged as TENTATIVE — pending community feedback and technique availability assessment.

**Key consideration:** Unlike sequential coupled techniques (EPMA + LA-ICP-MS), simultaneous NCT+XCT acquisition produces intrinsically co-registered volumes in a single session with one instrument setup. Forcing two-TAPP registration may be architecturally awkward. A combined TAPP would be structured with XCT-specific fields, NCT-specific fields, and coupling-specific fields (co-registration geometry, shared rotation stage).

**Bring to:** Astromat protocol registration infrastructure discussions. The answer depends partly on how the registration system handles Coupled Protocol DOI — whether one DOI can point to two TAPP instances simultaneously.

**Key reference:** Treiman et al. 2022 (MAPS) — coordinated NCT+XCT of EET 87503 howardite at NIST-NeXT.

---

## 2. Medical/Preclinical CT — scope boundary

**Topic:** Should preclinical CT scanners (e.g., GE eXplore speCZT) be in scope for Lab-XCT, or should they be separately classified?

**Status:** Deferred. Charles et al. 2018 in the Lab-XCT assessment used this instrument class (GE eXplore speCZT at Robarts Institute). The TAPP captures most metadata from this paper but HU calibration (CT Number Calibration, C=Advanced in current TAPP) and mA-range currents distinguish preclinical CT from microfocus lab XCT.

**Decision needed:** Is "Preclinical CT" a sub-type of Lab-XCT (same TAPP, platform field) or a separate TAPP? If the former, the Lab-XCT TAPP should add a Platform Type field (microfocus industrial | preclinical | nano-CT | etc.). If the latter, a new planning table entry is needed.

---

## 3. Protocol registration architecture for coupled techniques

**Topic:** How does the Astromat registration system assign DOIs to coupled protocol pairs? Can one DOI reference two TAPP instances? This affects:
- All Coupled Technique fields across TAPPs
- NCT+XCT combined TAPP decision (Item 1 above)
- Future TAPPs where coupling is methodologically standard (e.g., electron backscatter diffraction always accompanying SEM)

**Status:** Registration system is under parallel development. Decision deferred until architecture is defined.

---

## 4. TAPP Planning Table — stale entries

**Topic:** Several entries in `TAPP_Planning_Table.csv` are outdated and should be updated.

| Entry | Issue |
|---|---|
| LA-Q/SF-ICP-MS (#7) | Notes say "TAPP v1 in development"; file is now at v11 |
| XCT (#38) | Originally described sub-type field approach; now split into separate Lab-XCT, SR-XCT TAPPs; note updated 2026-05-15 |
| SR-XCT (row 43) | No priority, notes, or labs assigned |
| NCT+XCT (row 45) | Added 2026-05-15; TENTATIVE status documented in notes |

---

## 5. Version control — git repository

**Status:** No git repository currently. Version control by filename only. Risk: intermediate states not recoverable; diff of decisions across versions requires manual inspection.

**Recommendation:** Initialize a git repository at `/Users/ruolin/Documents/Astromat/TAPPs/`. Commit each TAPP version after xlsx export. Use commit messages to reference the development phase and key changes.

---

---

# Part VI — Paper Registry Status

**File:** `paper_registry.csv`  
**Last updated:** 2026-05-15  
**Total papers:** 32  
**Technique columns:** 18

### Active technique columns (papers with Detailed entries)

| Technique | Detailed | Notes |
|---|---|---|
| EPMA | 11 | Full Phase 3 assessment complete |
| Lab-XCT | 11 | Full Phase 3 assessment complete; Charles 2018 = preclinical CT (classification deferred) |
| LA-Q/SF-ICP-MS | 8 | Phase 3 assessment complete |
| SEM / FIB-SEM | 3 | Secondary technique coverage from multi-technique papers |
| TEM / STEM | 3 | Secondary technique coverage |
| XRD | 2 | Secondary technique coverage |
| XANES | 2 | Secondary technique coverage |
| MC-ICP-MS | 2 | Secondary technique coverage |
| LAF | 2 | Secondary technique coverage |

### Papers covering multiple techniques (7 papers)

These papers were assessed for multiple TAPPs and provide cross-technique coverage:
McCoy 2025, Barnes 2025, Zega 2025, Broussard 2026, Seifert 2026, Frank 2023, Liu 2016.

### Items needing update

| Citation Key | Issue |
|---|---|
| Shearer2024 | DOI = "N" (not extracted); needs lookup |
| Eckley2024 | DOI = "N" (scan record, no DOI); confirmed correct |
| Tait2014 | DOI = "N" (thesis, no DOI); confirmed correct |
| Mittlefehldt2024 | DOI = "N" (appendix document); may need verification |
| Charles2018 | Registered as "Detailed" under Lab-XCT; classification as preclinical CT deferred for future review |

---

---

---

# Part VII — Planning Table Review: ADA Stats Comparison (2026-05-16)

## 2026-05-16 | CROSS-TAPP | ADA stats vs. planning table reconciliation

Compared ADA analytical record counts (`ada_stats_technique.rtf`) against `TAPP_Planning_Table.csv`. Key findings and decisions from this review:

---

### Decisions recorded

**LIT priority: L → H**
Lock-in Thermography has 195 ADA records (7th most common technique). Despite being classified as a non-chemical physical technique (thermal imaging), its ADA volume is too large to leave at Low priority. Promoted to H.

**AFM row renamed to "Atomic Force Microscopy (AFM)"**
Per TAPP nomenclature conventions: AFM (Atomic Force Microscopy) is the **Technique** (the cantilever-based force-sensing platform). PCD-AFM (Particle Cohesion Determination) and SThM-AFM (Scanning Thermal Microscopy) are two **Methods** — distinct applications of AFM to yield different data types. The previous row name "Particle Cohesion Determination with AFM (PCD-AFM)" named a method rather than the technique.
Architecture decision: one AFM TAPP with mode flags for Topography | Thermal (SThM) | Cohesion (PCD). SThM-AFM has 377 records in ADA (5th most common), likely Hayabusa2-specific — scope and priority to be revisited if JAXA submissions continue.

**TDM added to planning table**
Temperature-Dependent Magnetization (1 ADA record) was absent from the planning table. Added as row TDM under Physical Properties, priority L.

**FIB-SEM deferred note added to SEM row**
FIB-SEM (177 ADA records, 8th most common) stays bundled within the SEM TAPP as an instrument variant field. Ion-beam metadata scope (beam current, milling protocol, section geometry) to be reviewed during Phase 0 of SEM TAPP — may require additional fields or a future standalone TAPP. Note added to SEM row in planning table.

**VLMBasemap investigation note added to VLM row**
"VLMBasemap" appears as a separate ADA identifier (15 records). Cannot determine from identifier alone whether this is a data sub-type of VLM or SLS, or a distinct technique. Note added to VLM row; examine ADA records before deciding.

---

### Conceptual decisions recorded

**FINESSE = stepped-heating mode of EA-IRMS**
FINESSE is a stepped-combustion instrument system for C and N isotopic analysis. Mechanistically identical to EA-IRMS but uses a stepped-heating furnace instead of flash combustion. The 4 ADA records under the FINESSE identifier map to the stepped-heating sample introduction mode field of the EA-IRMS TAPP. No separate TAPP needed. The EA-IRMS TAPP (row #19) should use a mode field (or protocol field) named "Sample Introduction Mode" with values: Flash Combustion (EA) | Stepped Heating (FINESSE).

---

### Process decision: planning table as deferred-decision record

Adopted convention: the **Notes column of TAPP_Planning_Table.csv** is the canonical location for deferred decisions, open questions, and scope constraints that apply at TAPP development time. Any decision deferred from a planning discussion (e.g., "FIB-SEM standalone TAPP — revisit in Phase 0") is recorded there with a DEFERRED prefix.

**Workflow updated:** `references/workflow.md` now includes a mandatory step: read `TAPP_Planning_Table.csv` and check the Notes column before beginning Phase 0 for any technique.

---

### Priority mismatches flagged for future review

| Technique | ADA Records | Rank | Current Priority | Flag |
|---|---|---|---|---|
| SThM-AFM | 377 | 5th | L (AFM TAPP) | Hayabusa2-specific? Review if JAXA submissions continue |
| LIT | 195 | 7th | **H** (promoted) | Done |
| FIB-SEM | 177 | 8th | n/a (SEM variant) | DEFERRED to SEM Phase 0 |
| LA-ICP-MS | 8 | 34th | H | Expected — technique is undersubmitted, not rare |
| Raman | 8 | 37th | H | Same — undersubmitted relative to technique importance |

---

---

---

# Part VIII — TAPP: Solution Quadrupole ICP-MS (Solution Q-ICP-MS)

**Current version:** v5  
**File:** `Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v5.csv`  
**Status:** Phase 2 complete (cross-TAPP consistency revisions applied); Phase 3 not yet started  
**Fields:** 97 content fields (per Phase 2 group tally; v3–v4 restructured existing fields)  
**Modes:** None (no mode flag columns)  
**Assessment protocols:** 0 (Phase 3 not yet started)

---

## Scope Decisions

**Technique scope:** Quadrupole ICP-MS with solution sample introduction (nebulizer + spray chamber or desolvation system). Covers both standard Q-ICP-MS and triple-quadrupole (ICP-MS/MS) instruments. Excludes: LA-Q-ICP-MS (separate TAPP), SF-ICP-MS (Part IX), MC-ICP-MS, ToF-ICP-MS.

**No mode flags:** Solution Q-ICP-MS does not have distinct analytical modes requiring separate columns. CRC configuration (STD/KED/DRC) is captured as a Group 3 field; the operating mode is a protocol-level instrument configuration, not a separate analytical mode.

---

## Version History

### v1 (Phase 1 — 2026-06-16)
Preliminary TAPP generated from 4 seed papers and reference TAPP (LA-Q/SF-ICP-MS v2). 86 content fields across 6 groups.

### v2 (Phase 2 revisions — 2026-06-16)
Cross-TAPP consistency pass against LA-Q/SF-ICP-MS reference TAPP and joint review with Solution SF-ICP-MS TAPP.

**Fields added (Group 2):**
- `Number of Digestion Steps` (C=Basic, D=Read-Only): number of sequential digestion steps in the dissolution protocol
- `Chromatographic Separation Applied` (C=Advanced, D=Read-Only): moved from SF-ICP-MS only to both solution TAPPs; chromatographic separation is independent of mass analyser type

**Fields added (Group 3) — aligning with reference TAPP:**
- `ICP-MS Type` (C=Basic, D=Read-Only): controlled list distinguishing Q-ICP-MS from ICP-MS/MS
- `Interface Cone Configuration` (C=Basic, D=Read-Only): replaces "Cone Material and Type"; captures cone geometry
- `Sampler and Skimmer Cone Material` (C=Advanced, D=Read-Only): split from cone field; captures material composition
- `Torch Depth` (C=Advanced, D=Editable): not in v1; aligns with reference TAPP line 106
- `Mass Resolution Setting` (C=Basic, D=Read-Only): fixed at unit resolution for Q; documents instrument class constraint
- `Collision/Reaction Cell (CRC) Configuration` (C=Basic, D=Read-Only): replaces removed "Analytical Mode"; captures STD/KED/DRC mode
- `Detector Configuration` (C=Basic, D=Read-Only): aligns with reference TAPP line 109

**Fields renamed (Group 3):**
- `Guard Electrode Status` → `Guard Electrode` (to match reference TAPP line 107 exactly)

**Fields removed (Group 3):**
- `Cone Material and Type` (split into Interface Cone Configuration + Sampler and Skimmer Cone Material)

**Data Reduction Software** description updated to explicitly state version number should be included (replacing removed Group 5 version field).

**Fields added (Group 4) — aligning with reference TAPP:**
- `Plasma Thermal Mode` (C=Basic, D=Read-Only): normal vs. cool plasma; aligns with reference TAPP line 131
- `Doubly-Charged Species Monitor` (C=Advanced, D=Editable): which mass ratio monitored; aligns with reference TAPP line 136
- `Doubly-Charged Species Production` (C=Advanced, D=Editable): measured doubly-charged rate; aligns with reference TAPP line 137

**Fields renamed (Group 4):**
- `Analytical Mode` (STD/KED/DRC) → REMOVED; concept replaced by `Collision/Reaction Cell (CRC) Configuration` in Group 3
- `Plasma Tuning Acceptance Criteria` → `Oxide Production Method and Threshold` (aligns with reference TAPP line 134)
- `Plasma Condition Check Results` → `Oxide Production` (aligns with reference TAPP line 135)
- `Internal Standard Element(s)` → `Internal Standard Element` (aligns with reference TAPP naming)

**KED/DRC Comments column** updated: references to "Analytical Mode" changed to "CRC Configuration".

**Fields added (Group 5) — aligning with reference TAPP:**
- `Pulse/Analog Detector Nonlinearity Correction` (C=Advanced, D=Editable): aligns with reference TAPP line 164
- `Memory Effect Mitigation` (C=Advanced, D=Editable): aligns with reference TAPP line 168

**Fields renamed (Group 5):**
- `Calibration Strategy` → `Per-Analyte Calibration Strategy` (aligns with reference TAPP line 156)
- `Interfering Species Corrected` → `Interfering Species` (aligns with reference TAPP line 166)

**Fields removed (Group 5):**
- `Data Reduction Software Version`: version now included in Group 3 `Data Reduction Software` description

### v3 (2026-06-16 — no content changes)
Version increment only; no field additions, removals, or tier changes relative to v2. (Likely an xlsx export or minor formatting pass in the session following Phase 2.)

### v4 (2026-06-16 — CRC field restructuring and tier revisions)
Restructuring of CRC-mode-specific fields from separate named rows into shared analyte-block fields; tier corrections based on cross-TAPP review against LA-Q/SF-ICP-MS TAPP.

**Fields added (Group 4):**
- `Analyte` (C=Basic, D=Editable): replaces `Analyte(s)` and `Target Analyte(s)`; naming aligned with reference TAPP
- `Signal Collection Mode` (C=Basic, D=Read-Only): pulse counting / analog / dual; carried over from LA TAPP addition
- `Collision Gas Type` (C=Basic, D=Read-Only): replaces `KED Mode: Collision Gas Type`; generic field covering all KED gas types
- `Collision Gas Flow Rate` (C=Basic, D=Editable): replaces `KED Mode: Collision Gas Flow Rate`
- `Cell Exit Discrimination Voltage` (C=Basic, D=Editable): replaces `KED Mode: KED Voltage`
- `Reaction Gas Type` (C=Advanced, D=Read-Only): replaces `DRC Mode: Reaction Gas Type`
- `Reaction Gas Flow Rate` (C=Advanced, D=Editable): replaces `DRC Mode: Reaction Gas Flow Rate`

**Fields removed (Group 4):**
- `Analyte(s)`, `Target Analyte(s)`: consolidated into `Analyte`
- `KED Mode: Collision Gas Type`, `KED Mode: Collision Gas Flow Rate`, `KED Mode: KED Voltage`
- `DRC Mode: Reaction Gas Type`, `DRC Mode: Reaction Gas Flow Rate`

**Tier changes:**
- `Chromatographic Separation Applied`: C=Advanced → C=Basic (applicable to all protocols using chromatographic pre-concentration)
- `Guard Electrode`: C=Basic → C=Advanced (solution ICP-MS instruments commonly have guard electrode as a fixed design feature; less critical to document than in LA)
- `Isotope Dilution Data Reduction Method`: C=Advanced → C=Basic (mandatory for all ID protocols)
- `Isotope Dilution Spike`: C=Advanced → C=Basic (mandatory for all ID protocols)

### v5 (2026-06-17 — software tier bug fix)
Corrected Precedent 4 violation: minor software version updates do not constitute a new protocol; analysis-level tier must be Editable, not Read-Only.

**Tier changes:**
- `Acquisition Software`: D=Read-Only → D=Editable
- `Data Reduction Software`: D=Read-Only → D=Editable

---

## Key Decisions — Solution Q-ICP-MS

| Date | Decision | Rationale |
|---|---|---|
| 2026-06-16 | No mode flags | CRC configuration (STD/KED/DRC) is a protocol design choice captured in Group 3, not an analytical mode requiring separate columns |
| 2026-06-16 | CRC Configuration in Group 3, not Group 4 | Instrument-level configuration (whether cell is installed and in what operating mode) belongs in Group 3; specific gas parameters stay in Group 4 |
| 2026-06-16 | Mass Resolution Setting: C=Basic, D=Read-Only for Q | Fixed at unit resolution by instrument physics; no operator selection; field documents the instrument class constraint |
| 2026-06-16 | Chromatographic Separation Applied added | Chromatographic separation (e.g., anion exchange for Cu–Zn ID) is ICP-MS-type-independent; applies to Q-ICP-MS equally as to SF-ICP-MS |
| 2026-06-16 | Uncertainty Propagation Method: C=Advanced, D=Editable | Deferred from Phase 2; Group 5 placement retained pending future review |
| 2026-06-16 | Chromatographic Separation split deferred | Splitting into "Applied" and "Procedure" sub-fields flagged for Phase 3/4 review via FLAG comment |

---

## Open Questions — Solution Q-ICP-MS

| Status | Question |
|---|---|
| ⚠️ Pending | Chromatographic Separation Applied: split into (Y/N) + Procedure? Flagged in Comments; defer to Phase 4 post-assessment review |
| ✅ Resolved | Isotope Dilution Data Reduction Method: upgraded to C=Basic in v4 |
| ⚠️ Pending | Sample Aliquot Mass or Volume: FLAG retained for Phase 2 human review — may warrant Basic tier |
| 🔲 Future | Phase 3 literature assessment: 4 seed papers identified (Barrat 2012, Braukmuller 2020, Gleeson 2020, Holdship 2018) |

---

---

# Part IX — TAPP: Solution Sector-Field ICP-MS (Solution SF-ICP-MS)

**Current version:** v5  
**File:** `Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v5.csv`  
**Status:** Phase 2 complete (cross-TAPP consistency revisions applied); Phase 3 not yet started  
**Fields:** 94 content fields (per Phase 2 group tally; v3–v4 restructured existing fields)  
**Modes:** None (no mode flag columns)  
**Assessment protocols:** 0 (Phase 3 not yet started)

---

## Scope Decisions

**Technique scope:** Single-collector sector-field ICP-MS (SF-ICP-MS) with solution sample introduction. Covers instruments using a magnetic sector + electrostatic analyser for high-resolution mass separation (Thermo Element 2, Element XR, Nu Instruments Attom HR). Excludes: MC-ICP-MS (multi-collector, isotope-ratio focus), LA-SF-ICP-MS (separate TAPP via reference TAPP), Q-ICP-MS (Part VIII).

**No mode flags:** Mass resolution mode (LR/MR/HR) is captured as a Group 3 field (`Mass Resolution Setting`) and a Group 4 analyte-specific field (`Mass Resolution per Analyte`), not as separate analytical mode columns.

---

## Version History

### v1 (Phase 1 — 2026-06-16)
Preliminary TAPP generated from 5 seed papers and reference TAPP (LA-Q/SF-ICP-MS v2). 86 content fields across 6 groups.

### v2 (Phase 2 revisions — 2026-06-16)
Cross-TAPP consistency pass against LA-Q/SF-ICP-MS reference TAPP and joint review with Solution Q-ICP-MS TAPP.

**Fields added (Group 2):**
- `Number of Digestion Steps` (C=Basic, D=Read-Only)

**Chromatographic Separation Applied** description updated and FLAG comment added (Phase 2 split consideration). Already present in v1.

**Fields added (Group 3) — aligning with reference TAPP:**
- `ICP-MS Type` (C=Basic, D=Read-Only): "Single-collector sector-field (SF-ICP-MS)"
- `Interface Cone Configuration` (C=Basic, D=Read-Only): replaces "Cone Material and Type"
- `Sampler and Skimmer Cone Material` (C=Advanced, D=Read-Only): split from cone field
- `Torch Depth` (C=Advanced, D=Editable)
- `Guard Electrode` (C=Basic, D=Read-Only): NEW for SF-ICP-MS — confirmed applicable; Thermo Element 2/XR uses grounded guard electrode as a design feature
- `Mass Resolution Setting` (C=Basic, D=Editable): operator-selectable; records mode(s) used in this protocol (LR/MR/HR combinations)
- `Detector Configuration` (C=Basic, D=Read-Only): includes triple-mode (pulse counting/analog/Faraday) description for Element XR

**Fields removed (Group 3):**
- `Cone Material and Type` (split into Interface Cone Configuration + Sampler and Skimmer Cone Material)
- `Accelerating Voltage (HV)`: fixed at 10 kV by instrument design on all current SF-ICP-MS platforms; not operator-selectable; absent from reference TAPP

**Fields added (Group 4):**
- `Plasma Thermal Mode` (C=Basic, D=Read-Only)
- `Doubly-Charged Species Monitor` (C=Advanced, D=Editable): particularly important for SF-ICP-MS since no collision cell suppresses doubly-charged species
- `Doubly-Charged Species Production` (C=Advanced, D=Editable)

**Fields renamed/removed (Group 4):**
- `Analytical Mode` (LR/MR/HR): REMOVED; mass resolution is now captured in Group 3 (protocol-level) and Group 4 `Mass Resolution per Analyte` (analyte-specific)
- `Mass Resolution Setting per Analyte` → `Mass Resolution per Analyte`
- `SEM-Faraday Cross-Calibration Factor`: REMOVED from Group 4; concept moved to Group 5 as `Pulse/Analog Detector Nonlinearity Correction`
- `Plasma Tuning Acceptance Criteria` → `Oxide Production Method and Threshold`
- `Plasma Condition Check Results` → `Oxide Production`
- `Internal Standard Element(s)` → `Internal Standard Element`

**Fields added (Group 5):**
- `Pulse/Analog Detector Nonlinearity Correction` (C=Advanced, D=Editable): replaces Group 4 `SEM-Faraday Cross-Calibration Factor`; description updated for triple-mode instruments
- `Memory Effect Mitigation` (C=Advanced, D=Editable)

**Fields renamed (Group 5):**
- `Calibration Strategy` → `Per-Analyte Calibration Strategy`
- `Interfering Species Corrected` → `Interfering Species`

**Fields removed (Group 5):**
- `Data Reduction Software Version`

### v3 (2026-06-16 — no content changes)
Version increment only; no field additions, removals, or tier changes relative to v2. (Likely an xlsx export or minor formatting pass in the session following Phase 2.)

### v4 (2026-06-16 — field renaming and tier revisions)
Renamed analyte fields and applied tier corrections based on cross-TAPP review.

**Fields added (Group 4):**
- `Analyte` (C=Basic, D=Editable): replaces `Analyte(s)` and `Target Analyte(s)`; naming aligned with reference TAPP

**Fields removed (Group 4):**
- `Analyte(s)`, `Target Analyte(s)`: consolidated into `Analyte`

**Tier changes:**
- `Chromatographic Separation Applied`: C=Advanced → C=Basic (applicable to all protocols using chromatographic pre-concentration)
- `Guard Electrode`: C=Basic → C=Advanced (SF-ICP-MS instruments use guard electrode as a fixed design feature; less critical to document than in LA)
- `Isotope Dilution Data Reduction Method`: C=Advanced → C=Basic (mandatory for all ID protocols)
- `Isotope Dilution Spike`: C=Advanced → C=Basic (mandatory for all ID protocols)

### v5 (2026-06-17 — software tier bug fix)
Corrected Precedent 4 violation: minor software version updates do not constitute a new protocol; analysis-level tier must be Editable, not Read-Only.

**Tier changes:**
- `Acquisition Software`: D=Read-Only → D=Editable
- `Data Reduction Software`: D=Read-Only → D=Editable

---

## Key Decisions — Solution SF-ICP-MS

| Date | Decision | Rationale |
|---|---|---|
| 2026-06-16 | Accelerating Voltage removed | Fixed at 10 kV on all current SF-ICP-MS platforms (Element 2, XR, Attom HR); not operator-selectable; absent from reference TAPP |
| 2026-06-16 | Guard Electrode added to SF-ICP-MS | Web search + reference TAPP confirmed Guard Electrode is actively used on Thermo Element 2/XR (grounded shield electrode is an integral design feature, not an optional add-on) |
| 2026-06-16 | Mass Resolution Setting: C=Basic, D=Editable for SF | Operator-selectable; protocol registers mode(s) used; analyst confirms at session start |
| 2026-06-16 | Mass Resolution per Analyte retained in Group 4 | Per-analyte resolution assignments are analysis metadata complementing the protocol-level Mass Resolution Setting; both fields required |
| 2026-06-16 | SEM-Faraday Cross-Calibration Factor moved from Group 4 to Group 5 | Cross-calibration is a data processing correction, not a measurement parameter; Group 5 placement aligns with reference TAPP; renamed to match reference TAPP terminology |
| 2026-06-16 | Oxide Production thresholds stricter than Q-ICP-MS | SF-ICP-MS lacks collision/reaction cells; all oxide interference suppression is through plasma tuning; CeO+/Ce+ < 0.4% is standard (vs. < 1.5% for Q) |

---

## Open Questions — Solution SF-ICP-MS

| Status | Question |
|---|---|
| ⚠️ Pending | Chromatographic Separation Applied: split into (Y/N) + Procedure? Flagged in Comments; defer to Phase 4 |
| ✅ Resolved | Isotope Dilution Data Reduction Method: upgraded to C=Basic in v4 |
| ⚠️ Pending | Sample Aliquot Mass or Volume: FLAG retained for Phase 2 human review |
| 🔲 Future | Phase 3 literature assessment: 5 seed papers identified (Barrat 2012, de Baar 2008, Georg 2006, Qi 2019, Wimpenny 2019) |

---

---

# Addendum to Part III — Candidate Fields for LA-Q/SF-ICP-MS Future Revision

**2026-06-16 | LA-Q/SF-ICP-MS | Candidate fields identified during Solution ICP-MS TAPP development**
**✅ RESOLVED 2026-06-17 | All four candidate fields addressed in LA-Q/SF-ICP-MS v3**

The following fields were identified during Solution ICP-MS TAPP development as applicable to LA-ICP-MS but absent from the reference TAPP. Three were incorporated directly in v3; one (Drift Correction Method) was consciously excluded with rationale.

| Field | Outcome | Disposition in v3 |
|---|---|---|
| E-scan Range | ✅ Added | Group 4, C=Advanced, D=Read-Only, SF-ICP-MS only |
| Triple Scanning Mode | ✅ Added | Group 4, C=Advanced, D=Read-Only, SF-ICP-MS only |
| Collision/Reaction Cell (CRC) Configuration | ✅ Added | Group 3, C=Basic, D=Read-Only, Q-ICP-MS only |
| Drift Correction Method | ❌ Excluded | In LA-ICP-MS, IS normalization IS drift correction — not a separable design choice as in solution ICP-MS. The Internal Standard Approach field in Group 5 already captures this. Adding a separate Drift Correction Method field would introduce redundancy and potential confusion about what should go where. |

*End of log — last entry 2026-06-17*
