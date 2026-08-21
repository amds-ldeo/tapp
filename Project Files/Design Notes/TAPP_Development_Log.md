
> **Layout note, 2026-08-12.** The repository was reorganised on this date: loose root files moved
> into `Project Files/` (`Scripts/`, `Registers & Planning/`, `Reports/`, `Design Notes/`,
> `Presentations & Figures/`, `Reference/`), the four dated superseded folders were consolidated under
> `Superseded TAPPs/`, and working files moved to `Archive/`. **Paths written in dated entries below
> were correct when written and have not been rewritten.** For current locations see
> `Project Files/Design Notes/PLAN_Folder_Reorganisation_2026-08-12.md`.
> **Terminology note (2026-07-24):** TAPP vocabulary was realigned with BIPM VIM3 (JCGM 200:2012) on this
> date — "Protocol" is now "Procedure"; the old "Procedure" is formally "Measurement" (VIM3 §2.1), though
> the working label "Analysis" is unchanged. **Part I below has been updated to the new terminology.**
> Every dated entry from Part II onward keeps its original wording and uses whichever terminology was
> current when it was written — do not treat those entries as current guidance on vocabulary.
> **If Part I ever appears to disagree with `references/conventions.md`, conventions.md is authoritative**
> — it is the living source of truth; this log is a historical record of decisions, not a restatement of
> current rules. When pulling rationale from a specific past entry, search for the topic rather than
> reading the file end-to-end, to avoid pulling old terminology into new drafting.

---

# Astromat TAPP Development Log

**Project:** Technique-Aligned Procedure Profiles for Astromat / EarthChem  
**Maintained by:** Astromat curation team  
**Last updated:** 2026-08-08

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

**Retired TAPPs** live in `Superseded TAPPs (YYYY-MM-DD)/` with a README mapping their content to wherever it now lives. They are excluded from `validate_tapp.py` discovery. Dated entries below that discuss a retired TAPP are left as written — per this log's convention, entries preserve the state at the time. As of 2026-08-08 the two LA-ICP-MS Geochronology TAPPs (General, Horstwood Test) are retired; they are referenced throughout Parts III–V and in the 2026-07 entries.

**Composed TAPPs** are build outputs for the groups a module supplies (Rule 6). Do not hand-edit those groups; edit the module and recompose. `composed_tapps.json` records which TAPP was built from which module versions.

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
| C | Procedure-Level Tier | Basic / Advanced / N/A |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced |
| E | Data Type | Controlled vocabulary |
| F | Example / Allowed Content | Examples or controlled list values |
| G | Comments | Short field-level labels (e.g., "Analyte-Specific") |
| H | Last Update | YYYY-MM-DD |
| I … | Mode flag columns | One per mode; start at col I (index 8); order by decreasing frequency |
| — | Sentinel column | Header exactly "Literature Assessment"; cells empty; marks mode/lit boundary |
| — | Literature assessment columns | One per distinct procedure extracted from paper |

**Script dependency:** `scripts/tapp_to_xlsx.py` expects Comments at G (index 6), Last Update at H (index 7), and mode flags starting at I (index 8). TAPPs missing the Comments column cause the script to misidentify mode columns. All TAPPs must have this column.

---

## Tier System

### Procedure-Level Tier (Column C)
| Value | Meaning |
|---|---|
| Basic | Mandatory for procedure registration |
| Advanced | Optional but strongly recommended |
| N/A | Not applicable at procedure level (analysis-level field only) |

### Analysis-Level Tier (Column D)
| Value | Meaning |
|---|---|
| Read-Only | Imported from procedure; cannot be changed by analyst. Also used for fields relevant only at procedure level (value inherited, shown read-only). |
| Editable | Imported from procedure; may be adjusted within procedure-defined bounds at analysis time |
| Basic | Mandatory user input at analysis time; cannot be pre-specified in procedure |
| Advanced | Optional user input at analysis time; recommended for complete documentation |

**Critical invariant:** D=N/A is **not a valid tier**. Every field must have a meaningful analysis-level assignment. (D=N/A was removed because it behaved identically to D=Read-Only in the pipeline — decision recorded in `references/precedents.md` §11.)

**C/D asymmetry pattern:** C=Advanced + D=Basic is valid and important — procedure optionally specifies the field; analysis mandatorily documents it. Example: Detection Limit (C=Advanced, D=Basic).

**Read-Only rule:** If C=Advanced (field may be void in the procedure), the analysis-level tier should almost never be Read-Only (importing a blank would be meaningless). Use Editable or Basic instead.

---

## Field Naming Rules

1. **Level-neutral:** No "Default", "Target" (when meaning ideal), "Achieved", "Typical", "Actual" as prefix/suffix. The tier columns encode level.
2. **Exceptions:** "Target Material" and "Target Feature(s)" retain "Target" because it denotes the material/feature type the procedure is designed to analyze — not a value with a later "achieved" counterpart.
3. **"Procedure" vs "Method":** Use "Procedure" for the registerable object (Procedure Name, Procedure DOI). Use "Method" only for sub-procedures, calculation methods, or assessment methods.
4. **"Analyte-Specific" not "Element-Specific":** Use Analyte-Specific to remain technique-agnostic.
5. **"(Mode Only)" suffix:** Use when a field applies to a single mode only, e.g., "Raster Line Spacing (Mapping Only)".
6. **Template:** Every new TAPP begins Group 1 from `tapp_files/Template TAPP Group 1.csv` to prevent field name and tier drift.

---

## Structural Decisions (from `references/precedents.md`)

These have been formally adopted and propagated across TAPPs. See `references/precedents.md` for full rationale.

| # | Decision | Key rule |
|---|---|---|
| 1 | Procedure value vs. measured value | When procedure specifies a threshold/criterion and analysis records the actual measurement, split into two fields with different tier assignments |
| 2 | Acceptance criterion vs. measured value | [Concept] Method and Threshold (C=Basic, D=Read-Only) + [Concept] (C=N/A, D=Basic) |
| 3 | Single merged field with D=Editable | Use when procedure scope and analysis execution describe the same quantity at different stages (e.g., Analyte) |
| 4 | Editable for software fields | Minor version updates ≠ new procedure; D=Editable for acquisition/reconstruction/analysis software |
| 5 | Reference materials: C=Basic, D=Editable | Procedure commits to specific RM; substitution allowed at analysis time due to availability |
| 6 | Signal smoothing: Y for all modes with caveat | Set mode flag=N only when genuinely inapplicable; use description caveat when applicable but problematic |
| 7 | D=Editable when C=Advanced (field may be void) | If procedure-level tier is Advanced (may be blank), Read-Only at analysis level would import a blank |
| 8 | C=Advanced + D=Basic asymmetry | Valid for QC fields that require accumulated session data but are mandatory for data submission |
| 9 | Beam geometry: D=Read-Only | Categorical procedure design choice; changing beam mode = different analytical approach |
| 10 | Mapping dimension vs. step size | Map extent (sample-determined) = C=N/A, D=Basic; Step size (resolution control) = C=Basic, D=Editable |
| 11 | Coupled technique fields (4 standard) | Group 1: Coupled Technique(s), Coupling Description (C=Advanced, D=Editable); Coupled Procedure DOI, Coupled Dataset or Publication Reference (C=N/A, D=Advanced) |
| 12 | Procedure DOI: C=N/A, D=Basic | DOI does not exist at registration time; mandatory at analysis level; "Pending" is acceptable |

---

## Module Architecture (Rule 6, adopted 2026-08-08)

Shared field content is no longer copied between TAPPs. It is held in one **module** file and
**composed** into consuming TAPPs by `scripts/compose_tapp.py`. Rule 4's propagation obligation had
demonstrably failed: `Funding Source for Procedure Development` had drifted in 3 of 13 TAPPs despite
being a Group 1 field, and 14 of 17 Group 1 descriptions in LA-Q/SF-ICP-MS had diverged unnoticed.

**Three layers.** A registered procedure is Layer 1 x Layer 2 x Layer 3.

| Layer | Holds | Examples |
|---|---|---|
| 1 — Instrument TAPP | the technique: Groups 1–4, technique-specific parts of 5–6 | LA-Q/SF-ICP-MS, TEM, SEM |
| 2 — Cross-technique module | field names, descriptions, tiers, data types | Group1, ReportingCore, Geochronology, LaserAblation, MCICPMS, SolutionIntroduction |
| 3 — System module | per-system Column F content plus system-specific fields | UPb, ArAr |

**Column ownership.** Module owns A–E. Consumer owns F (examples), G (comments), H (last update),
mode flags, and literature assessment columns — a module cannot know a consumer's mode set. This is
what lets an abstract field be usable: `Calibration Factor and Determination Method` reads as the J
value to an Ar-Ar geochronologist and as the EARTHTIME tracer to a U-Pb one, from the same field.

**Composed TAPPs are build outputs.** Never hand-edit a composed group; edit the module and
recompose. `compose_tapp.py --check` reports whether a file still matches what composition produces.

**Modules are extracted, not invented** (Rule 6.10). Never from one instance — you cannot tell what
is general from a single TAPP. Extract when a *second* TAPP needs a block of >=5 coherent fields;
prefer three instances to two. Module development is therefore downstream of TAPP development.

Registers: `TAPP_Module_Register.csv` (modules), `TAPP_Composed_Variants.csv` (instrument x system),
`composed_tapps.json` (which TAPP was built from which module versions).

---

## Tooling (added 2026-08-08)

| Script | Purpose |
|---|---|
| `scripts/validate_tapp.py` | lints every TAPP against the structural invariants and cross-TAPP rules; run before any version bump |
| `scripts/compose_tapp.py` | builds a TAPP from a source plus modules; `--diff`, `--check`, `--allow-drop`, block selection |
| `scripts/tapp_to_xlsx.py` | unchanged; exports CSV to formatted xlsx |

The linter is now the primary enforcement mechanism for naming and structural conventions. Rule 4
narrows to content that is still copied; anything held in a module cannot drift by construction.

---

## Workflow Phases

| Phase | Lead | Purpose | Output |
|---|---|---|---|
| 0 | Human (AI supporting) | Technique scoping, mode decision, seed papers | Scope document, mode flag assignments |
| 1 | AI | Generate preliminary TAPP from seed papers/templates | Draft CSV, all D-tiers as TBD |
| 2 | Human (AI supporting) | Structured field review — tiers, modes, splits | Revised CSV with all tiers assigned |
| 3 | AI (human validates) | Literature assessment against 8–12 papers | TAPP CSV with assessment columns appended |
| 4 | Human (AI implements) | Post-assessment revision — tiers, missing fields, descriptions | Final TAPP version |

**Phase 3 rule:** Integrate assessment directly into main TAPP CSV (no separate draft CSV). Read original papers; do not use summaries. One column per *distinct procedure*, not per paper. Values: directly stated text | "N" (not reported) | "N/A" (genuinely inapplicable).

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

**Current version:** v4.1  
**File:** `LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v4.1.csv`  
**Status:** Phase 2 complete (cross-TAPP ICP-MS consistency revisions applied); literature assessment 13 protocols across 10 papers  
**Fields:** 110 content fields (unchanged from v3 — v4 and v4.1 were description/tier-text fixes only, not field additions; see note below on v4's undocumented gap)  
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

### v4 (date unknown — not logged)
File exists on disk (`LA-Q:SF-ICPMS_TAPP_v4.csv`) but no entry was made in this log at the time. Content changes between v3 and v4, if any, were not captured here.

### v4.1 (2026-07-28 — RF Power description fix; cross-TAPP consistency re-check)
While building the Horstwood-derived LA-ICP-MS U-Th-Pb Geochronology TAPP (a separate exercise comparing a human-workshop-derived reporting standard against this TAPP's field set), a cross-check flagged three apparent inconsistencies between this TAPP and the three solution ICP-MS TAPPs (Q, SF, MC): `Guard Electrode` tier, `Dwell Time per Mass` tier, and `RF Power` description text. Checking this log's own v3 entry (above) before acting showed two of the three are **intentional, already-justified design decisions** from the 2026-06-17 consistency pass, not drift — `Guard Electrode` (C=Basic here vs. Advanced in solution TAPPs, because solid-sample ablation produces larger plasma load fluctuations) and `Dwell Time per Mass` (D=Editable here vs. Read-Only in solution TAPPs, because mapping requires analyst adjustment, a mode solution ICP-MS doesn't have). **Both left unchanged** — re-confirmed correct, not re-litigated.

**Fixed:**
- `RF Power` description text updated. The v3 entry (above) deliberately changed D=Read-Only → D=Editable ("minor session-to-session tuning adjustments do not constitute a new protocol"), but the description text was never updated to match and still read "Fixed in the procedure; cannot be changed by analysts without defining a new procedure" — a genuine leftover contradiction between tier and description, confirmed by checking that no similar "Fixed... cannot be changed" language exists in any of the three solution TAPPs' RF Power fields, all of which are also D=Editable. New description follows the session-tuning phrasing pattern already used for `Torch Depth` in this same file.

No field additions, removals, or other tier changes. 110 content fields (unchanged).

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
| LA-Q/SF-ICP-MS (#7) | ✅ RESOLVED 2026-07-28 — Notes updated to reflect current v4.1 status (110 fields; Phase 2/3 literature assessment against 13 protocols from 10 papers), and to clarify that `LA-Q:SF-ICP-MS` is the renamed, actively-maintained folder while `LA-ICP-MS`/`LA-ICPMS_TAPP_v13.csv` is a stale, frozen branch, not a separate TAPP. See memory `reference_la_icpms_lineage.md`. |
| XCT (#38) | Originally described sub-type field approach; now split into separate Lab-XCT, SR-XCT TAPPs; note updated 2026-05-15 |
| SR-XCT (row 43) | No priority, notes, or labs assigned |
| NCT+XCT (row 45) | Added 2026-05-15; TENTATIVE status documented in notes |

---

## 5. "Constants and Reference Values Used" — mandatory cross-TAPP field (Rule 5)

**Topic:** Make a new field, `Constants and Reference Values Used` (Group 5, C=Basic, D=Editable), mandatory
in every TAPP — physical constants/reference values used in data reduction (decay constants, standard
isotope ratios, etc.), distinct from Group 6's Reference Material Information. Motivated by a gap found
while building the Horstwood-derived LA-ICP-MS U-Th-Pb Geochronology test TAPP: Horstwood et al. (2016)'s
own Table 4 footnote cites "Decay constants of Jaffey et al. (1971)" but their Table 3 metadata template
never asks for this as a structured item. Traceability concern: decay constants and isotope ratios do get
revised (e.g. ²³⁸U/²³⁵U: 137.88 per Steiger & Jäger 1977 → 137.818 per Hiess et al. 2012).

**Status:** ✅ EXECUTED 2026-07-28. User resolved the open scoping question as **fully universal** (option
a in the briefing) before the retrofit began. Completed across all 11 production TAPPs plus
`references/conventions.md` (Rule 5) and `references/precedents.md`. Full record: see the dated entry
`2026-07-28 | CROSS-TAPP | Rule 5 — "Constants and Reference Values Used" added to all TAPPs` at the end of
this log.

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


---

## 2026-07-24 | CROSS-TAPP | Adopted VIM3-aligned terminology

TAPP vocabulary realigned with BIPM VIM3 (JCGM 200:2012), on advice from geoscience experts consulted on
techniques and analysis, replacing the project's bespoke in-house definitions. Source:
`Measurement Term Definitions VIM3.xlsx`.

**Mapping:** Technique and Method keep their labels (definitions refined to VIM3 "measurement principle"
§2.4 and "measurement method" §2.5 wording). "Protocol" → "Procedure" (VIM3 "measurement procedure," §2.6)
— the registerable, DOI-bearing object, TAPP's procedure-level Column C. The old "Procedure" (analysis-level
execution) is formally "Measurement" (VIM3 §2.1), but the working label stays **"Analysis"** — Column D
header is unchanged ("Analysis-Level Tier") — to avoid colliding with Group 4's existing "Measurement
Information" and to keep a smaller migration footprint. TAPP acronym: Technique-Aligned **Procedure**
Profiles.

**Scope of this change:** `references/conventions.md`, `workflow.md`, `field-review.md`, `precedents.md`,
`lit_assessment.md`, both `SKILL.md` copies, `tapp_files/Template TAPP Group 1.csv`, and
`scripts/tapp_to_xlsx.py` were updated in place (pre-migration snapshots kept in
`Pre-VIM3 Reference Archive (2026-07-24)/`). This log's Part I (Cross-TAPP Conventions) was updated to
match; Parts II onward (dated per-TAPP history) were left untouched — see the banner at the top of this
file. All 12 current-version TAPP CSVs were migrated to new integer-bumped versions (v7→v8, etc.); prior
versions remain unchanged on disk as the historical record.

**Known follow-up:** Solution Q-ICP-MS and Solution SF-ICP-MS both have a pending Open Question
(Chromatographic Separation Applied — split into Y/N + "Procedure"?) proposing a candidate field literally
named "Procedure." Whoever picks this up at Phase 4 should name it something else (e.g.,
"Chromatographic Separation Method") to avoid colliding with the new formal term.

---

## 2026-07-28 | CROSS-TAPP | Rule 5 — "Constants and Reference Values Used" added to all TAPPs

Full retrofit executed per `RETROFIT-BRIEFING_Constants-Field-Rule5.md` (written by a prior session after
the field was first identified and added to the standalone Horstwood-derived LA-ICP-MS Geochronology test
TAPP — see Part V item 5, updated above). New rule documented as Rule 5 in `references/conventions.md`
(Cross-TAPP Consistency Rules) and as a precedent entry under "Group 5: Data Processing" in
`references/precedents.md`.

**Scope decision:** applied universally to every TAPP — including pure-imaging/morphology techniques
(SEM_Imaging, Lab-XCT), which record "None" — rather than scoped only to techniques with plausible
constant-dependent data reduction. This was the briefing's Section 3 open question; confirmed with the user
before executing. Matches Rule 3's own precedent for "Analytical Mode" (even N/A cases get the field, since
its universal presence is itself informative).

**Field:** `Constants and Reference Values Used`, inserted as the last field in Group 5 (Data Processing)
in every TAPP. C=Basic, D=Editable, Text (free). Mode flags set to Y across every mode-flag column (field
is universal, not mode-restricted). Comments column (G) left empty, matching the actual Rule 3 "Analytical
Mode" precedent verified across EPMA/TEM/Lab-XCT before patching — `references/conventions.md` documents
Column G as short WDS/EDS/Analyte-Specific labels, not rule-provenance notes, so the briefing's draft
"Source: ..." Comments text was not used.

**Retrofitted (11 TAPPs, all integer version bumps, xlsx regenerated for each):**
EPMA v8→v9 · LA-Q/SF-ICP-MS v4.1→v5 · SEM v5→v6 · SEM_Composition v5→v6 · SEM_Imaging v5→v6 ·
SEM_FIBSEM v5→v6 · Solution MC-ICP-MS v3→v4 · Solution Q-ICP-MS v6→v7 · Solution SF-ICP-MS v6→v7 ·
TEM v8→v9 · Lab-XCT v9→v10.

Prior versions remain unchanged on disk as the historical record (version control by filename only, per
the note at the top of this log). Did **not** touch the stale, frozen `LA-ICPMS_TAPP_v13.csv` branch (see
`reference_la_icpms_lineage.md`) or re-touch the standalone Horstwood test TAPP, which already carries the
field from its own v5 under a geochronology-specific description — that TAPP is a comparison exercise, not
part of this production retrofit.

**Known follow-ups surfaced during the retrofit, not actioned (out of scope for this pass):**
- Five TAPPs have no blank separator row between Group 5 and Group 6 — SEM_Composition, SEM_Imaging,
  SEM_FIBSEM, Solution Q-ICP-MS, Solution SF-ICP-MS — contrary to the "one blank row between groups"
  convention. The new field was inserted as the new last Group 5 row in each, matching each file's existing
  structure; the missing separator itself was left as found.
- `Analytical Mode` (Rule 3) is absent from all three Solution ICP-MS TAPPs (MC-ICP-MS, Q-ICP-MS,
  SF-ICP-MS). Consistent with the 2026-06 Analytical Mode retrofit list above (Part I / precedents.md),
  which never covered this family — a pre-existing gap, not introduced here.
- Individual per-technique `### vN` Version History entries were not added for this change (following the
  2026-07-24 VIM3 entry's precedent of one consolidated CROSS-TAPP entry for a uniform whole-library
  change, rather than duplicating the same note across every Part). EPMA, SEM (and its three sub-TAPPs),
  TEM, and Solution MC-ICP-MS have no dedicated Part in this log at all; this entry is their only record of
  the v9/v6/v4 bump.

---

## 2026-07-29 | CROSS-TAPP | Collision/reaction cells extended to MC-ICP-MS

User flagged that modern MC-ICP-MS instruments — Nu Instruments Sapphire and Thermo Scientific Neoma
MS/MS — carry a hexapole collision/reaction cell (CRC), and asked whether the CRC-related fields already
in the TAPP library (previously tagged Q-ICP-MS-only, inherited from quadrupole ICP-MS/MS instruments
like the Agilent 8900) should also apply to MC-ICP-MS. Verified via instrument brochures/specifications
before acting (see `MC-ICP-MS_Technology_Update_2026-07-29.txt` for full source notes):

- **Nu Sapphire**: dual-path MC-ICP-MS — conventional high-energy multi-collector path plus a low-energy
  hexapole CRC path (STD/KED/DRC-style operation); 170+ units installed worldwide. Sapphire XD extends
  this further as a dual-path MC-ICP-MS/MS.
  - Confirmed real, current, CRC-equipped MC-ICP-MS.
- **Thermo Neoma MS/MS**: hexapole CRC with a pre-cell mass filter — but the pre-cell filter is a
  **double Wien filter** (crossed E/B-field velocity selector), not a quadrupole. It produces a
  trapezoidal, comparatively low-resolution mass "window" set as a percentage of maximum magnetic field,
  architecturally distinct from the quadrupole pre-filter on Q-ICP-MS/MS instruments.
  - Confirmed CRC-equipped; confirmed its pre-cell selector is NOT the same mechanism as
    `Signal Collection Mode` (peak hopping/scanning) — see decision below.
- **SF-ICP-MS** (Element XR, Nu AttoM): no evidence of CRC adoption on any current single-collector
  sector-field instrument; these remain purely resolution-based (LR/MR/HR, ~300/4000/10000). Sources
  consistently frame high-resolution SF and collision-cell Q/MS as alternative, competing approaches to
  interference removal, not a CRC-adopting and a CRC-abstaining variant of the same architecture.
  - No change warranted for SF-ICP-MS.

**Decision:** of the seven CRC-cluster fields (all originally added to LA-Q/SF-ICP-MS TAPP v3, then
imported into the Horstwood test TAPP tagged "Q-ICP-MS only"), six are genuinely about the cell itself
and its gas chemistry — these were retagged to also apply to MC-ICP-MS. The seventh,
`Signal Collection Mode`, describes quadrupole sequential peak-hopping/scanning and was left Q-ICP-MS-only:
even on a CRC-equipped MC-ICP-MS, the collector array still performs genuinely simultaneous
multi-collection, and Neoma's Wien-filter pre-cell selection is a different concept entirely (a
mass-window pre-selector, not a sequential-scan mode) — extending this field to MC would have been
incorrect, not just imprecise.

**Changes made:**
- **Horstwood-derived LA-ICP-MS U-Th-Pb Geochronology test TAPP, v5→v6** (standalone comparison exercise
  — see Part V item 5 and the experiment report, not part of production TAPP library): `Collision/Reaction
  Cell (CRC) Configuration`, `Collision Gas Type`, `Collision Gas Flow Rate`, `Cell Exit Discrimination
  Voltage`, `Reaction Gas Type`, `Reaction Gas Flow Rate` — MC-ICP-MS flag N→Y, Comments tag updated to
  "Q-ICP-MS and MC-ICP-MS only", Description and Allowed Content text updated to name the enabling
  instruments and to distinguish "SF-ICP-MS" from "MC-ICP-MS without a collision/reaction cell" as two
  separate N/A reasons. `Signal Collection Mode` description enriched to explain why it stays Q-only
  (flags unchanged). All 7 fields' Last Update bumped to 2026-07-29.
- **Solution MC-ICP-MS TAPP, v4→v5**: the same six fields did not exist in this TAPP at all (it
  previously had zero CRC-related fields) and were added new, mirroring Solution Q-ICP-MS's own versions
  per Rule 1/Rule 2 (shared-field-name harmonization) — same names, same Procedure-Level tiers, adapted
  Description/Comments text to name Nu Sapphire/Neoma MS/MS and to state the CRC-absent case as the N/A
  default (opposite framing from Solution Q-ICP-MS, where a cell is the norm). `Collision/Reaction Cell
  (CRC) Configuration` inserted in Group 3 after `Mass Resolution Setting`; the other five inserted in
  Group 4 after `Sample Sequence Design`, before `Internal Standard Element`. `Signal Collection Mode` was
  **not** added — same reasoning as above (simultaneous collection is intrinsic to the MC architecture
  regardless of CRC presence).
- **LA-Q/SF-ICP-MS TAPP**: no change. This TAPP has no MC-ICP-MS dimension at all (Q and SF only; MC is
  planning-table row 7a, a separate future TAPP) — its own CRC-cluster fields' Q/SF framing is unaffected
  by this decision. Also currently mid-literature-assessment (new seed papers being incorporated,
  Spot/Transect/Mapping + per-paper columns present in the working v5 file) — left untouched to avoid
  colliding with that in-progress work.

**Other technology-driven gap identified, not yet actioned:** the Neoma MS/MS double-Wien-filter pre-cell
mass-window selector has no corresponding field in any TAPP — it is not the same concept as
`Signal Collection Mode` or as any existing Group 3/4 field. Flagged as a candidate future field
(tentatively "Pre-Cell Mass Filter Configuration," Group 3) but not added this pass; see the txt writeup
for full reasoning. Recommend resolving with the user before adding, consistent with how other novel
field proposals have been handled in this project (discuss before implementing, not fait accompli).

---

## 2026-07-30 | Horstwood TAPP v7, and new LA-ICP-MS Geochronology (General) TAPP v1

**Motivating question:** how specific is the Horstwood-derived test TAPP to U-Th-Pb geochronology, and
could it be generalized to other LA-ICP-MS-compatible geochronometer systems (Rb-Sr, Sm-Nd, Lu-Hf,
U-series, Re-Os)? Investigated by reading the full TAPP field-by-field (not just the one field the user
had already spotted — `Common-Pb Correction, Composition and Uncertainty`) against this project's own
Phase 0 split-vs-combine test (`references/workflow.md`: "would a researcher familiar with one variant
immediately understand a procedure written for the other, with only minor unfamiliar vocabulary?").
Finding: the overwhelming majority of the TAPP (all of Groups 1-4, most of Group 5) is already
isotope-system-agnostic; the `Technique` field's controlled list (Group 1) and `Common-Pb Correction` were
the two genuine structural constraints, plus a long tail of description/example wording that is
U-Th-Pb-flavored without being restrictive.

**Literature check performed first:** searched for a Horstwood-equivalent (multi-institution,
workshop-consensus reporting standard) for Rb-Sr, Lu-Hf, and U-series LA-ICP-MS geochronology. None
exists for Rb-Sr or Lu-Hf — both are active fields with genuinely competing, non-convergent methodologies
(confirmed directly: Glorie et al. 2024 states published Rb-Sr methodologies "vary significantly"). A
genuine consensus paper exists for U-series generally (Dutton et al. 2017, *Quaternary Geochronology*
39:142-149, 12 authors, institutionally connected to Horstwood 2016 via two shared co-authors), but it is
not LA-specific and is written mostly by solution/TIMS practitioners. Horstwood 2016 itself seeded an
ongoing GSA Bulletin series ("Reporting and Interpretation of Geochronologic Data") that has since covered
Ar-Ar, (U-Th)/He, fission-track, Re-Os, and ID-TIMS U-Pb — but not Rb-Sr, Lu-Hf, Sm-Nd, or K-Ca as of this
writing. Given no comparison target exists for the systems of interest, proceeded by first-principles
decay-scheme analysis instead of literature comparison, per user direction.

**First-principles finding:** every parent-daughter geochronometer has some analog of common-Pb
correction — a non-radiogenic daughter-isotope component present at/after formation that must be
accounted for before the radiogenic ingrowth can be interpreted as an age. Confirmed structurally
identical mechanism (differing only in which element and which model composition) for: initial-Sr
correction (Rb-Sr), εNd/initial-Nd relative to CHUR (Sm-Nd), εHf/initial-Hf relative to CHUR (Lu-Hf),
detrital-Th correction (U-series — verified via the actual decay chain, ²³⁴U→²³⁰Th, that this is a
daughter-side correction, not parent-side, after initially mis-stating this to the user and correcting it
directly), and common-Os correction (Re-Os). Separately confirmed this correction class is
**isotope-system-dependent but instrument-independent** — needed identically whether measured by
LA-ICP-MS, solution MC-ICP-MS, SIMS, or TIMS — while the existing `Elemental Fractionation Correction`
field is the inverse case (instrument-dependent, isotope-system-independent: a pure laser-ablation
artifact). Also identified one likely genuine gap while doing this analysis: no field in the TAPP captures
*which equation* converts a corrected ratio into a reported age (concordia intercept vs. weighted mean vs.
isochron regression, etc.) — added as `Age/Model-Age Calculation Method`.

**Changes made:**

1. **Horstwood-derived LA-ICP-MS U-Th-Pb Geochronology test TAPP, v6→v7** (still explicitly scoped to
   U-Th-Pb — this file remains the comparison-exercise TAPP, not the generalized one):
   `LA-ICPMS_Geochron_Horstwood_TAPP_v7.csv`. Added one new field, `Age/Model-Age Calculation Method`
   (Group 5, Advanced/Read-Only, Controlled list, inserted immediately after `Common-Pb Correction,
   Composition and Uncertainty` and before `Constants and Reference Values Used` — logical order:
   correct the ratios, decide how to compute the age from them, list the constants that calculation used,
   propagate uncertainty into the final value). Tier follows the TAPP's own established precedent for
   new fields with no Table 3 or sibling-TAPP precedent (Advanced). Verified via exact diff against v6:
   exactly one row inserted, nothing else changed. Field count 122→123.

2. **New TAPP: LA-ICP-MS Geochronology (General), v1** — new folder
   `LA-ICP-MS Geochronology (General)/`, file `LA-ICPMS_Geochron_TAPP_v1.csv` (+ .xlsx). Created by
   copying Horstwood v7 in full and modifying exactly one field:
   `Common-Pb Correction, Composition and Uncertainty` → renamed and generalized to
   `Initial/Common-Daughter Correction, Composition and Uncertainty`, with its Description now naming
   and cross-referencing the equivalent concept and community vocabulary across all six systems above
   (common-Pb / initial-Sr / εNd / εHf / detrital-Th / common-Os), so a domain reader recognizes their own
   system's terminology. Procedure- and Analysis-Level tiers, Data Type, and mode flags left unchanged
   from the source field (Basic/Read-Only/Text (free)/Y,Y,Y) — the concept's universality across systems
   argues for keeping it Basic, not demoting it. Verified via exact diff against Horstwood v7: exactly one
   row modified, all 134 other rows byte-identical, confirming this is a targeted generalization, not a
   reconstruction. Field count 123, same as Horstwood v7 (rename/generalize, not add/remove).
   **Deliberately not touched in this pass**, per explicit user instruction to skip straight to literature
   assessment rather than redo Phase 0-2 scoping: the `Technique` field's controlled list (still reads
   "...U-(Th-)Pb Geochronology" only, no Rb-Sr/Lu-Hf/etc. options — will require "Other: specify" until
   revised), the `Target Material` mineral list (zircon/monazite/apatite-biased, though it has an "Other:
   specify" escape hatch), and the scattered Pb/U/Th-flavored description and example text elsewhere in
   the TAPP (e.g. `Oxide Production Method and Threshold`'s ThO⁺/Th⁺ framing, `Detection Limit`'s
   "U, Th, and/or Pb" wording). These are left as-is deliberately, on the reasoning that Phase 3
   (Literature Assessment) is designed to surface exactly this kind of gap empirically against real
   papers, rather than have it guessed at preemptively — consistent with the user's explicit instruction
   to skip Phases 0-2 for this TAPP.

**Next step (not yet started):** Phase 3-style literature assessment of the new general TAPP against
application papers for Rb-Sr, Lu-Hf, and/or U-series LA-ICP-MS geochronology (see the literature-landscape
findings above for candidate seed papers per system — none of them carry Horstwood's "community consensus"
weight, so this assessment will function as an ordinary Phase 3 literature assessment, not a second
Horstwood-style comparison).

---

## 2026-07-30 | Corrected 7 paper-direct fields mistiered Advanced instead of Basic

**Trigger:** user spotted `IC Dead Time` was tagged Advanced despite being pure paper-direct content
(`Comments` = exactly "Source: Table 3 (Horstwood et al. 2016)", no restructuring note), which should
default to Basic per this TAPP's own established tier-assignment rule (Table 3 is explicitly framed by
its authors as "the recommended minimum metadata," so paper-direct/paper-split content defaults to Basic
— see Section 3.3 / Table 1 of the experiment report).

**Audited all 33 paper-direct/paper-split fields rather than fixing only the one flagged item.** Found 9
total not tagged Basic. Evaluated each individually rather than blanket-flipping:

- **5 confirmed as clear misses**, no principled reason found for the deviation: `Imaging`,
  `Ablation Cell Type`, `Laser Pulse Duration`, `IC Dead Time`, `Uncertainty Level and Propagation`.
- **2 judgment calls**, presented to the user with reasoning rather than resolved unilaterally:
  `Make-up Gas Flow` (plausible principled case for Advanced — conditionally relevant only when a
  desolvating nebulizer/tracer path exists, matching how make-up gas flow is tiered in the sibling
  solution-ICP-MS TAPPs) and `Ablation Pit Depth/Ablation Rate` (weaker case, leaned toward miss but
  lower confidence). **User decided: convert both to Basic anyway, to avoid the added complexity of a
  conditional-tier exception; a user can report "N/A" for Make-up Gas Flow at analysis time if it
  genuinely doesn't apply.**
- **2 fields confirmed NOT misses, left unchanged**, on inspection they are a structurally different
  category the Basic-default rule was never meant to cover: `Spot Diameter (Measured)` and
  `'Sensitivity' as Useful Yield` are both N/A at procedure level (not Advanced) — they are the
  *measured* half of a target/measured field split (analysis-time-only values, following the same
  pattern as `Oxide Production Method and Threshold` vs. `Oxide Production`), not procedure-level content
  that was merely under-tiered. `Other Information` was also confirmed not a miss — it is the free-text
  catch-all/overflow field, correctly Advanced by the same convention used for "Additional Notes"-style
  fields library-wide, not a specific reportable metadata item.

**Changes made:** all 7 confirmed-and-decided fields (the 5 clear misses + the 2 judgment calls, per the
user's decision) changed from Procedure-Level Tier `Advanced` to `Basic`. Applied identically to both
files that carry this content:

- **Horstwood-derived LA-ICP-MS U-Th-Pb Geochronology test TAPP, v7→v8**:
  `LA-ICPMS_Geochron_Horstwood_TAPP_v8.csv`.
- **LA-ICP-MS Geochronology (General) TAPP, v1→v2**: `LA-ICPMS_Geochron_TAPP_v2.csv`. Propagated to this
  file too since it inherited the identical bug from being copied off Horstwood v7 before this fix — not
  a separate decision, a mechanical consequence of fixing the same rule in a sibling file with the same
  content.

Both verified via exact diff: only the 7 named rows changed in each file, and only their Procedure-Level
Tier and Last Update columns — no other cell, no other field, touched. Field counts unchanged (123 in
both — this is a pure tier correction, not a field add/remove).

**Not touched:** the experiment report docx. Its Table 1 documents the tier-assignment *rule*
methodology, not a field-by-field tier breakdown or any aggregate Basic-vs-Advanced count, so nothing in
it becomes inaccurate from this fix.

---

## 2026-08-08 | CROSS-TAPP | Module architecture (Rule 6); geochronology TAPPs retired

Single continuous session. It began as a question about the LA-ICP-MS Geochronology TAPP and ended
with a module architecture, a linter, two new TAPPs, and the retirement of the TAPPs that raised the
question. Recorded here in one entry because the parts are not separable — each step was forced by
the previous one.

### The originating question, and why the obvious answer was wrong

The LA-ICP-MS Geochronology TAPP used **instrument** columns (Q-ICP-MS / SF-ICP-MS / MC-ICP-MS)
where every other TAPP uses analytical mode columns. The proposal on the table was to rename mode
columns to "application" columns library-wide so geochronology could sit alongside spot and mapping.

Surveying all 11 TAPPs showed mode labels are **measurement configuration** — detector x sampling
geometry (`EDS Mapping`, `SE Imaging`, `Electron Diffraction`) — not application. Renaming the
column header would not change what the labels mean. The reason geochronology *feels* different is
that in LA-ICP-MS the detector does not determine the property: the same counts become a
concentration, a ratio, or an age depending on **data reduction**. Hence the rule, now proposed for
conventions:

> A distinction fixed **before or during acquisition** is a mode. A distinction fixed **after
> acquisition, in data reduction** is not, and mode columns are the wrong instrument for it.

Five tests were run. Summarised because the artifacts survive in `Claude Skills for TAPP/analysis/`:

- **Test 1** — ~18 plausible LA-ICP-MS "applications" exist and the set is unbounded; only 2–3 would
  change the TAPP. A closed column set is impossible.
- **Test 2** — 11 property classes cover all 72 planning-table rows. Geochronology is a *reported
  quantity class*, peer of "elemental composition", not of "spot".
- **Test 3** — geochronology vs LA-Q/SF differ by only 4–5 genuine fields out of ~110, all in
  Group 5, but by **26 tier assignments**.
- **Test 4** — of those 26: **81% drift, 15% principled, 4% bug**. Only two were genuinely
  geochronology-exclusive. The tier obstacle to merging was two fields wide, not 26.
- **Test 5** — 15 candidate module fields against six dating systems (U-Pb ID-TIMS, Ar-Ar, Re-Os,
  (U-Th)/He, fission track, luminescence). 11 recur in 6 of 6, **including two that share no isotope
  machinery**. Five of the six community standards use a two-tier required/recommended split — the
  Basic/Advanced vocabulary independently validated by six communities.

### The discipline that shaped everything after

Test 5 measured *recurrence* but not *specificity*. Adding the second condition — "and is not already
in the library under another name" — changed the answer four times:

| Candidate | Failure | Resolution |
|---|---|---|
| 15 fields recurring across 6 dating systems | 9 also occur outside geochronology | module shrank to 5; the 9 became `ReportingCore` |
| `Age Model and Software` | software half collided with `Data Reduction Software` | narrowed to `Age Model` |
| 9 "general gaps" | 3 already covered by existing descriptions | 6 new fields, not 9 |
| `Pb*/Pbc` as U-Pb-specific | Ar-Ar's `%40Ar*` is the same quantity | promoted to Layer 2 as `Radiogenic Fraction of Measured Signal` |

The last is the instructive one: only building a *second* system module could reveal that a field in
the first had over-claimed specificity. This is why Rule 6.10 forbids extracting from one instance.

### What was built

**Rule 6** in `references/conventions.md`, ten subsections: admission test, layers, module file
format, column ownership, conditional block selection, generated-artifact discipline, relationship
to Rule 4, verification steps, status, and the extraction trigger. Precedent entry in
`references/precedents.md`. Composition route added to `references/workflow.md` as a second entry
point to the five phases, with a Phase 0 coverage audit.

**Eight modules.** Group1 (18) · ReportingCore (6, 5 selectable blocks) · Geochronology (6) ·
UPb (15) · ArAr (16) · LaserAblation (18) · MCICPMS (15) · SolutionIntroduction (16, provisional).

**Two scripts** — `validate_tapp.py`, `compose_tapp.py`.

**Two new TAPPs** — `LA-MC-ICPMS_TAPP_v1` and its U-Pb variant, the first built by the composition
route. Phase 0 done against Zhang et al. 2022 (in situ Rb-Sr by LA-MC-ICP-MS); 14 of 15
methodological requirements were already covered by composition. Phase 2/3 still outstanding.

**Planning table restructured** into three registers: instrument TAPPs (67 rows, + Route, Modules
Composed, Status), modules, and composed variants. Rows #7d, #26 and #9 were removed as TAPPs —
each is an instrument x system composition, not a technique. #27 Fission Track was **retained**,
because EDM has no separate instrument parent; it is the genuine exception.

### Library changes

Group 1 migrated to composed in all 14 TAPPs (265 cells). ReportingCore composed into 14 of 17 with
per-TAPP block selection. Rule 3 (`Analytical Mode`) added to the three Solution TAPPs, closing a gap
open since before the 2026-07-28 Rule 5 retrofit flagged it. Compound Data Types ratified. Five Rule 1
name harmonisations. `Sample Name` added to the three Solution TAPPs. `Sample Persistent Identifier`
resolved to C=Advanced across all 17. `Uncertainty Propagation Method` renamed to `Uncertainty Level
and Propagation` in 8 TAPPs. `Primary Calibration Standard Name` descriptions strengthened in 6.

**Three spec bugs found in our own documentation**, all corrected: Rule 3 mandated `Controlled
vocabulary` as a Data Type, which is not in the vocabulary (should be `Controlled list`); SKILL.md's
column table omitted the Comments column, shifting every letter after F; and the
`N/A | None | Other: specify` requirement collided with Rule 3's exact-enumeration requirement for
`Analytical Mode`, now an explicit exemption.

Lint went **505 -> 477 findings, ERROR 0 throughout**, across a library that grew from 14 to 15
live TAPPs while two were retired.

### Geochronology TAPPs retired

`LA-ICP-MS Geochronology (General)` and `(Horstwood Test)` moved to
`Superseded TAPPs (2026-08-08)/` with a README mapping every piece of content to where it now lives.
Verified first: **all 124 fields in each checked against the two composed U-Pb variants, 0 uncovered;
0 literature assessment columns, so no Phase 3 extraction was lost.** Nothing deleted. Analysis
artifacts still cited by the conventions were moved to `Claude Skills for TAPP/analysis/` rather than
archived. `validate_tapp.py` now excludes archive folders by pattern, so future retirement is a move
rather than a code edit.

The equivalent registerable profiles are `LA-Q_SF-ICPMS_UPb_TAPP_v5` and `LA-MC-ICPMS_UPb_TAPP_v1`.

### Errors made and corrected during the session — recorded because the pattern recurs

- **Claimed the LA-MC-ICP-MS residue was "transient-signal isotope ratio measurement" without a
  source.** The coverage audit was empirical; that characterisation was my own domain knowledge,
  written into a build script and a provenance manifest where it read as established. Reading Zhang
  2022 showed the direction was right but the magnitude overstated — one field and one description,
  not a body of content. Both artifacts corrected to say so.
- **Used description length as a proxy for quality** during module reconciliation, and nearly adopted
  two laser descriptions that were longer only because they contained Horstwood Table 3 provenance
  notes. Three of the four things that lengthen a description make it *worse* for a module. Added the
  `description-source-leak` linter check, which found 25 instances, 24 of them in the two TAPPs being
  reconciled *from*.
- **Claimed 8 Rule 1 naming violations; only 5 survived reading the descriptions.** `Sample
  Description` is not `Sample Name` (it is a *missing field* in three TAPPs); `Make-up Gas Flow Rate`
  is not `Plasma / Make-up Gas Addition` (different positions in different introduction systems).
  Name similarity is not evidence of field identity.
- **Two composer bugs**, both caught by checking something the diff did not cover: a swallowed blank
  separator row (caught by row count) and 190 dropped literature-assessment cells on group-header
  rows (caught by counting cells). A third — duplicate insertion instead of in-place update — only
  surfaced when composing a module back into the TAPP it was extracted from.

### Open, and deliberately not closed

- 15 of 16 `SolutionIntroduction` descriptions are **unreconciled**. An attempt to apply the Rule 6.10
  criteria by keyword proxy failed: 14 of 16 scored identically and selection fell back to Solution
  Q-ICP-MS by default. **The criteria are sound but not automatable** — only the disqualifiers are.
  Module marked `1-provisional`.
- `Uncertainty Level and Propagation` merges a Basic-worthy component (the level, mandated by six
  standards) with an Advanced-worthy one (the propagation framework, per an existing precedent).
  Splitting is the cleaner fix and reverses a documented decision; flagged, not taken.
- `Analysis Sequence` tiers split three ways; `Sample Persistent Identifier` D-tier split 14/3. Both
  recorded in `precedents.md` as known unresolved rather than settled by majority.
- Q-ICP-MS and SF-ICP-MS modules were requested and **not built**: 2 and 4 fields respectively, below
  Rule 6.10's threshold of 5. There is also no "sector-field" layer — 0 fields are shared by SF and
  MC but not Q.
- Instrument identity diverges *structurally*, not just by name: 6 TAPPs split manufacturer and model
  into two fields, 7 combine them, 3 use a third form. Out of scope for a rename.
- `LA-ICPMS_TAPP_v13` is now the last stale artifact and is the remaining `rule5` violation.
- 245 `date-missing` findings — bulk data entry, pre-existing.
- LA-MC-ICP-MS needs Phase 2/3; Zhang et al. 2018 and a Lu-Hf paper are needed first.

---

## 2026-08-10 | CROSS-TAPP | `Property Type` vocabulary logged; conventions §6.9 corrected

### `Property Type` — 64 distinct values across 65 rows

The 2026-08-08 restructure split the planning table into three registers but did not touch the
`Property Type` column, and no log entry recorded it. Logging it now, because it was the only open
item in the library with no written record anywhere — it survived only in session memory.

The column is effectively free text: **64 distinct values over 65 populated rows.** Exactly one value
recurs (`Elemental composition (trace/major)`, twice). Every other row is unique.

It is not noise, though. The values are compound and consistently so, along two axes:

- **Property class** — Elemental · Isotopic · Molecular/organic · Physical · Spectral ·
  Morphological/structural. These are the same classes Test 2 used to establish that geochronology is
  a *reported-quantity class* rather than a mode; `Property Type` is that same distinction at finer
  grain.
- **Qualifier** — spatial mode (`in situ`, `spatially resolved`, `bulk`, `imaging`, `surface`),
  analyte scope (`major`, `minor`, `trace`, `REE`), or a named target (`noble gases`, `amino acids`,
  `Fe oxidation state`).

Several rows carry more than one class, `;`-delimited — SEM is
`Morphological; Elemental (EDS); Crystallographic (EBSD); Spectral (CL)`. So this is a **multi-valued**
field, not a single-valued one, which is part of why a flat vocabulary never emerged on its own.

**Deliberately not resolved.** The plausible shape is a controlled class list plus a free-text
qualifier, multi-valued where a technique genuinely reports several classes. But the discipline in
6.1 and 6.10 applies beyond modules: this is 65 instances of a distinction nobody has yet had to
*use*. The real consumer would be search/faceting on the Astromat side, and its requirements are not
known. Generalising now would repeat the failure recorded in 6.1. Deferred until that requirement is
concrete — and now recorded, so it is not rediscovered a third time.

### `references/conventions.md` §6.9 rewritten

§6.9 still read *"Five modules exist"* and *"**No production TAPP has yet been composed** — all work
to date is in scratch files, and the library is unchanged."* It was written mid-session on 2026-08-08
and never updated when the migration landed later the same day, so it contradicted the log entry
above it, `TAPP_Module_Register.csv`, and `composed_tapps.json` simultaneously. Of the stale records
identified in review, this was the one most likely to mislead, since it sits in the document that
Rule 6 tells you to read first.

Rewritten to current state: eight modules with a register table, four items moved from unsettled to
settled, and the genuinely open ones restated.

Moved to **settled**: content reconciliation before migration is necessary (Group 1 changed 11 of 17
descriptions away from the template); that reconciliation is *not* automatable (the keyword-proxy
attempt on `SolutionIntroduction` scored 14 of 16 identically); description length is not a quality
proxy; and the group-header literature-assessment cell loss was a real composer bug, now fixed.

Three of the original four unsettled items turned out to be **partially** resolved, which the rewrite
states rather than rounding in either direction:

- Provenance is now *recorded* in `composed_tapps.json` but not *enforced*. `compose_tapp.py` neither
  writes nor reads that file, `validate_tapp.py` does not check it, and it is maintained by the
  one-off `patch_*` / `migrate_*` scripts. It can drift from the library silently, so the discipline
  in 6.6 still rests on convention.
- Module versioning is likewise recorded but has no increment rule and nothing verifies a recorded
  version against the module's current content.
- Field removal by a module remains untested and still handled by the drop guard rather than by
  design.

One new item surfaced while verifying the counts: **the module manifests have no schema.** `Group1`
and `Geochronology` omit `layer`; `Group1` and `ReportingCore` omit `consumed_by`; `Group1` and
`Geochronology` omit `blocks`. `TAPP_Module_Register.csv` supplies the missing values, so nothing has
broken and no output is affected, but nothing validates the JSON either. Recorded, not fixed.

Module field counts were checked against the module CSVs before being written into §6.9; all eight
match the register exactly.

### `LA-ICPMS_TAPP_v13` retired — the stale LA-ICP-MS branch archived

`LA-ICP-MS/` and `LA-Q_SF-ICP-MS/` were never two TAPPs; they are one lineage under two folder names,
split by a mid-development rename. The branches synced at v11/v12 (100% identical field sets in both
rounds), after which only LA-Q/SF was developed. `v13` is `v12` plus the VIM3 pass and the
2026-08-08 Group 1 composition. It looked current — highest version number, recent timestamp — and
had already caused one comparison workbook to be built against the wrong file and rebuilt.

**Field verification: 95 fields, 0 uncovered** against LA-Q/SF v5.

A name-only diff first reported three uncovered fields. All three dissolved on reading — the same
lesson as 2026-08-08 ("name similarity is not evidence of field identity"), running the other way:
`Auxiliary and Cool Gas Flow Rates` is covered by *two* better fields (`Coolant (Plasma) Gas Flow
Rate` + `Auxiliary Gas Flow Rate`); `Spectrometer Dwell Time` is a rename of `Dwell Time per Mass`
with a **byte-identical** description and identical tiers; `Drift Monitor Frequency` is covered by
`Calibration Standard Measurement Frequency`, whose description explicitly defines the drift-monitoring
bracketing interval. The corrected generalisation: **a name diff over-reports in both directions, and
the only way to close it is to read the descriptions.**

**Unlike the 2026-08-08 retirements, this one had literature assessment content to protect** — 16
columns and 1,436 filled cells, against LA-Q/SF v5's 13. The three extra columns (89 cells each, 267
total) exist nowhere else. They were dropped from LA-Q/SF correctly, each being out of scope for a
Q/SF TAPP, and each maps onto a planning-table row:

| Archived column | Instrument | Destination |
|---|---|---|
| Chernonozhkin et al. 2024 (JAAS 39) | LA-ICP-ToF-MS | row 7b — planned |
| Masuda et al. 2024 (M&PS 59) | TQ (iCAP TQ, KED) | row 7c — planned; already names this as its seed paper |
| Zhang et al. 2022 (At. Spectrosc. 43) | fs-LA-MC-ICP-MS | row 7a — **exists** at v1 with **zero** lit columns |

The third is live material, not archive: `LA-MC-ICPMS_TAPP_v1` ran its Phase 0 coverage audit against
that exact paper and has no Phase 3 content at all. Pointers were written into rows 7a/7b/7c naming
the archived file, so the columns are found when those TAPPs are built. **The transfer itself was not
performed** — it is field-name-matched rather than a column copy, and folding a Phase 3 step into a
retirement is how content gets mangled.

**What deliberately did not move.** `Validation Papers/` and the loose method PDFs stay in
`LA-ICP-MS/`. `paper_registry.csv` records that exact path for **10 papers**, and those papers are the
Phase 3 sources for the *live* LA-Q/SF TAPP, which has no papers folder of its own. Archiving them
would have filed the current TAPP's provenance under "superseded" and broken the registry. The folder
is retained, demoted to a source-paper folder, and carries a README saying there is no TAPP in it.
The folder name is deliberately unchanged, because the registry references it.

31 files moved to `Superseded TAPPs (2026-08-10)/LA-ICP-MS (stale branch)/`. Nothing deleted.
`composed_tapps.json` composed 15 → 14, retired 2 → 3. `Module_Group1` consumers 15 → 14 (recomputed
from the manifest, not decremented); all other module counts unchanged, since v13 consumed only
Group 1.

**Lint 477 → 395, ERROR 0.** The library's only `rule5` violation was v13's and is gone with it;
`date-missing` 245 → 194, `tier-divergence` 18 → 15, `name-element-specific` 5 → 4.

### Date cleanup — `date-format` closed, `date-missing` 194 → 96

Two problems that looked like one bulk-entry chore and were not.

**`date-format`, 22 rows, EPMA only.** `5/11/26` → `2026-05-11`. Disambiguated rather than assumed:
EPMA's other dates cluster at 2026-05-13 (32 rows), so the M/D/YY reading lands two days earlier,
while D/M/YY would give 2026-11-05 — a future date. Only one reading is possible. Closed.

**`date-missing`, 98 rows fixed.** The first question was whether this was a composition bug.
It was not: `v4.1` had **exactly the same 49 empty rows** and **0** dates were lost between v4.1 and
v5. These rows were simply never initialised, contrary to the instruction in Version and Date
Tracking to "initialize all rows to the creation date for a new TAPP".

The temptation was to stamp `2026-08-10` across all 98. That would have been **fabricated
provenance** — column H is defined as "the date of the most recent substantive edit to each row", and
most of these rows have not been edited since May. So the date was *computed* instead: walk the
development lineage in chronological order and, for each field, find the last version in which its
substantive content — description, both tiers, data type — actually changed.

The lineage is continuous and its dates are self-consistent (file mtime ≥ max in-file date in every
version, so mtime is a safe proxy for when a version was produced): v6 05-06 → v7 05-07 → v8/v9 05-13
→ v10/v11 05-14 → LA-Q/SF v1 05-22 → v2 06-01 → v3 06-17 → v4 07-24 → v4.1 07-28 → v5 08-08. The
stale `LA-ICPMS v12/v13` were excluded, being a parallel branch whose content duplicates v1/v2.

Result, identical in both LA-Q/SF v5 and its U-Pb variant, **0 unresolved**:

| Computed date | Rows | What happened then |
|---|---|---|
| 2026-05-06 | 22 | never substantively edited since the earliest surviving version |
| 2026-05-22 | 1 | the LA-ICP-MS → LA-Q/SF rename |
| 2026-07-24 | 18 | the VIM3 terminology migration |
| 2026-08-08 | 8 | the Group 1 reconciliation and module composition |

Verified before applying: `Technique` is byte-identical from v6 to v5 and correctly receives
2026-05-06; the 20 fields whose content changed between v4.1 and v5 correctly resolve to 2026-08-08.

**No version bump.** Conventions state that a column H date update alone does not warrant one.
`compose_tapp.py --check` reports `MATCH` against Group1, LaserAblation and ReportingCore, confirming
column H is consumer-owned under 6.4 and that editing it directly does not desynchronise a composed
TAPP. Three xlsx regenerated.

**96 findings deliberately left**, both LA-MC-ICP-MS files. A separate session is concurrently
rewriting them to v2 to add the Zhang et al. 2022 literature assessment column recovered from the
retired v13. Editing them in parallel would clobber that work. They inherit the same empty cells from
LA-Q/SF v5 and should get the same lineage-computed treatment once that lands — the field names are
shared, so the map already computed applies.

**Lint 395 → 275, ERROR 0.** `date-format` 22 → 0; `date-missing` 194 → 96.

### Group-header flag cells — 100 findings were one fix; 60 applied

`mode-flag-group-header` (60) and `sentinel-group-header` (40) had a single root cause: group-header
rows carried empty cells where conventions require `N` ("Group header rows must have N in all mode
flag columns to prevent them from appearing in mode-filtered views"). The linter classes it cosmetic —
an empty flag is not `Y`, so headers already stay out of filtered views.

Note the asymmetry the patch had to respect: in the **sentinel** column, group headers must be `N`
but **data rows must be empty**. Writing `N` indiscriminately would have manufactured the existing
`sentinel-stray-N` finding (4 occurrences, SEM family) across the library. Header rows only;
`sentinel-stray-N` held at 4 afterwards, confirming nothing leaked onto data rows.

60 cells set across 6 TAPPs. `compose_tapp.py --check` returns `MATCH`; 6 xlsx regenerated. The
remaining 40 are the two LA-MC-ICP-MS files, skipped for the same concurrency reason as the dates.

An early version of this patch globbed `*_TAPP_v*.csv` and matched **44 files, 422 cells** — it had
picked up `.migration_backup_group1_20260808/`, the archived stale branch, and every historical `vN`
in each live folder. Target selection was rewritten to derive from a fresh lint report, which is
correct by construction: only files that actually carry the finding. Worth remembering — the live
library is 14 files, but a naive glob over this project sees three times that.

### `controlled-list-options` (48) is **not** one fix — it is four problems

Checked because it looked mechanical. It is not one fix, but the first classification of it was
**wrong and is corrected here**, because the error is instructive.

**Retracted: there is no linter compound-rule bug.** The first pass claimed the checker was ignoring
the compound clause and flagging `Coupled Technique(s)` fields that already carried `N/A`. It is not.
`validate_tapp.py` implements the clause correctly — for a compound it drops `Other: specify` from
the required set and still requires `N/A | None`, exactly as conventions specify. All nine
`Coupled Technique(s)` findings are genuine; none of those Column F values contains `N/A`.

Two mistakes produced the false claim. The classifier bucketed a finding by its **Data Type** without
checking **which token** was reported missing — so a compound missing `N/A` (a real gap) was filed
as "compound rule misapplied". And the Column F quoted as counter-evidence came from
`LA-Q_SF-ICPMS_TAPP_v5`, which **is not among the nine flagged** — a non-flagged file was used to
argue that flagged files were false positives. The general lesson, third time in this log: *check the
specific instances the tool reports, not a representative you picked yourself.*

Corrected classification of all 48:

| Count | Class | What it needs |
|---|---|---|
| 39 | Genuine gap | mechanical append, with a per-field check that `None` means anything |
| 5 | **Column F is entirely EMPTY** on a `Controlled list` field | a real defect, worse than a missing token — a controlled list with no allowed values. `Coupled Technique(s)` in all three Solution TAPPs; `Mass Fractionation Law` in both LA-MC files |
| 4 | Semantic `N/A` present as longer wording | `Collision/Reaction Cell (CRC) Configuration` offers "Not applicable (SF-ICP-MS)", more informative than a bare `N/A`. Normalise, or teach the checker to accept it — a judgment call |

**Fixed now: the `Others: specify` typo**, 3 instances (`Technique` in LA-Q/SF v5, its U-Pb variant,
and Lab-XCT v10). Conventions fix the token as singular. This corrects a genuine error but clears no
finding on its own, since `N/A` and `None` are also absent from those rows — which is why the total
holds at 215.

**`Technique` remains an exemption candidate.** `N/A` and `None` are arguably semantically empty for
it — every procedure has a technique — which is precisely the reasoning that exempted
`Analytical Mode`. The three Solution TAPPs make the case plainly: their Column F is a single value
(`Solution Q-ICP-MS`), a closed enumeration of one. But the exemption table is explicitly **closed**,
and adding to it requires an explicit decision recorded in both `conventions.md` and
`precedents.md`. Flagged, not taken.

**Lint 275 → 215, ERROR 0.**

### The 5 empty Column F cells — filled

A `Controlled list` field with an empty Column F has no allowed values at all: the Data Type promises
a closed vocabulary and none is supplied. That is a defect rather than a missing convention token,
which is why these 5 were treated separately from the 39 that merely lack `N/A | None |
Other: specify`.

Scope was checked before acting, because empty Column F is common — 37 to 39 cells in each Solution
TAPP, 22 in LA-MC v2. For `Text (free)` and `Numeric` fields an empty F is merely a missing example
and is optional. It is only load-bearing on a `Controlled list`. Exactly 5 such cells existed, so the
linter's scope was right and no wider sweep was warranted.

Column F is consumer-owned — modules own A–E — so all five were edited in the TAPP, not the module.
`compose_tapp.py --check` returns `MATCH` against Group1 and MCICPMS afterwards.

**`Mass Fractionation Law`** (LA-MC v2, LA-MC U-Pb v1) was copied verbatim from Solution MC-ICP-MS
v5: `Exponential | Linear | Power | N/A | None | Other: specify`. Same field, same module
(`MCICPMS`), sibling consumers — Rule 4 consistency, not invention. Plain `Controlled list`, so
`Other: specify` is required.

**`Coupled Technique(s)`** (Solution Q v7, SF v7, MC v5) is `Controlled list / Text`, so the compound
rule applies: `N/A | None` required, `Other: specify` deliberately omitted because the `/ Text`
component already permits an unlisted answer. Values are technique names per the field's own
description, and differ by TAPP rather than being one generic list:

- **Q and SF** measure concentrations in digested aliquots, so the characteristic couplings are
  isotope-ratio work on the same digestion (MC-ICP-MS, TIMS), in-situ comparison (LA-ICP-MS), major
  elements (EPMA), and Noble Gas MS — the last being the (U-Th)/He case that conventions.md itself
  cites as its example of a computationally mandatory coupling.
- **MC** measures ratios, and its characteristic coupling runs the other way: Q or SF first, to
  determine concentration before spiking and dilution.

These are a defensible starting vocabulary rather than a community standard, and are worth a domain
review.

LA-MC v2 and its U-Pb variant were included despite the concurrent-session caution that governed the
date and header patches: that session's output had been stable for over two hours, and the edit
touches a single consumer-owned cell that module composition does not write.

**Lint 215 → 210, ERROR 0.** `controlled-list-options` 48 → 43.

### LA-MC-ICP-MS residue closed — and an mtime trap worth recording

With the literature-assessment transfer landed, the two deferred patches were re-run against
`LA-MC-ICPMS_TAPP_v2` and `LA-MC-ICPMS_UPb_TAPP_v1`: 40 group-header flag cells and 96 dates.

**The date run nearly wrote fabricated provenance, and the cause is worth remembering.** Part 1
derived each version's date from filesystem **mtime**, which was safe then because nothing in the
chain had been touched. By the time part 2 ran that was no longer true — the day's own patches
(dates, header flags, the Column F fill) had rewritten `LA-Q_SF-ICPMS_TAPP_v5` and both LA-MC files,
pushing their mtimes to 2026-08-10. The first dry run duly reported 8 rows per file dated
**2026-08-10**, where the correct answer is **2026-08-08**: those fields last changed when LA-MC v1
was composed, not today. Reading mtime after editing a file silently converts "composed on 08-08"
into "edited today" — precisely the fabrication the computed-date method exists to prevent.

Fixed by pinning every version date explicitly, from the lineage survey taken *before* any of the
day's edits plus the build dates in `composed_tapps.json`. `version_date()` now raises rather than
falling back to mtime for an unlisted file, so the trap cannot silently reopen. **General rule: a
derived-provenance computation must not read mutable filesystem metadata from files the same session
is editing.**

The chain was also extended along the real derivation path, since LA-MC carries `MCICPMS`,
`Geochronology` and `UPb` blocks the LA-Q/SF lineage never had:

    LA-MC v2     <- LA-MC v1 <- LA-Q/SF v5 <- … <- LA-ICPMS v6
    LA-MC UPb v1 <- LA-MC v1 <- LA-Q/SF v5 <- … <- LA-ICPMS v6

`LA-MC-ICPMS_TAPP_v1.csv` is retained on disk and is load-bearing as a chain link even though v2
supersedes it. Result: 48 filled per file, **0 unresolved**, distribution 21/1/18/8 across
2026-05-06 / 05-22 / 07-24 / 08-08 — matching the LA-Q/SF pattern.

Verified afterwards: `compose_tapp.py --check` returns `MATCH` on all four modules for v2, and the
transferred Zhang et al. 2022 literature assessment column is intact at 95 filled cells. Two xlsx
regenerated.

**Lint 210 → 74, ERROR 0.** `date-missing` 96 → **0**; `mode-flag-group-header` 30 → **0**;
`sentinel-group-header` 10 → **0**. All three checks are now clean library-wide.

### The last 12 mechanical findings — four checks cleared

**5 × `datatype-invalid`, TEM only.** All resolve to `Text (free)`, which is not a judgement call but
the library's existing answer: `Analyte` is `Text (free)` in EPMA, SEM, LA-Q/SF, Solution Q and
Solution SF, and `Acquisition Software` / `Data Reduction Software` are `Text (free)` in all five.
TEM had invented four local labels (`List of element symbols`, `List of element + edge label`,
`Text (keV)`, `Text (eV)`) plus `Controlled vocabulary + version`. The two range fields hold values
like `0-20 keV (2048 channels)` — a range plus a channel count, not a number, so `Numeric (unit)`
would have been wrong. `Text (free)` also avoids manufacturing new findings: typing the software
field as `Controlled list` would immediately demand `N/A | None | Other: specify` in Column F.

**4 × `name-element-specific`.** Column B of `Isobaric Interference Corrections Applied` read
"Element-specific detail …". Now "Analyte-specific". The string also occurs in a **literature
assessment** column in LA-Q/SF v5 ("applied element-specifically") and was deliberately left alone —
that is verbatim extraction describing what a paper did, which is exactly why the check reads only
columns B and F. Worth noting the finding was nearly missed on inspection because the text is
lower-case `Element-specific` and the first search for it was case-sensitive.

**2 × `name-level-encoding`.** `Target Foil Thickness` → `Foil Thickness` in SEM v6 and SEM FIB-SEM
v6. Only `Target Material` and `Target Feature(s)` are exempt from level-neutral naming; the tier
columns already encode whether a value is a procedure target or an analysis measurement. Verified no
collision — no other TAPP defines a `Foil Thickness` field, and the field is not module-owned, so
there is no Rule 4 propagation beyond these two files.

*Left open deliberately:* whether a field rename warrants an integer version bump. Version and Date
Tracking lists additions, removals, tier changes and mode-flag changes as major revisions, and a
rename is none of those literally, but it is more than a description edit. Handled here as a Last
Update bump. **If a rename counts as structural, SEM and SEM FIB-SEM need v7.** Also unresolved and
larger: FIB-SEM plausibly wants *two* fields here — a procedure-level target thickness and an
analysis-level achieved thickness — which is the split described in Common Mistake 1. Not opened.

**1 × `description-source-leak` — a FALSE POSITIVE, and recorded as one.** The pattern
`in the source(?:\s+\w+)?` matched Lab-XCT `Accelerating Voltage`: *"Record the value as stated in
the source and add a parenthetical note if the unit used is keV."* That regex targets commentary
about what a source **document** contains — the Horstwood Table 3 pattern it was built for. Here "the
source" means the publication being catalogued, and the sentence is an **instruction to whoever fills
the field**, which is legitimate description content. Deleting real guidance to satisfy a heuristic
would be the wrong repair, so the sentence was reworded to say the same thing without the trigger
("as originally reported"). The regex remains slightly over-broad on the phrase `in the source`
followed by a conjunction; not changed, since this was its only false hit in the library.

All 12 rows stamped `2026-08-10`. `compose_tapp.py --check` returns `MATCH` across Group1,
ReportingCore and LaserAblation for every touched file; 8 xlsx regenerated.

**Lint 74 → 62, ERROR 0.** `datatype-invalid`, `name-element-specific`, `name-level-encoding` and
`description-source-leak` are all now **0**.

### Three user decisions taken

**`Technique` added to the controlled-list exemption table.** The table had been closed with a single
entry since 2026-08-08. `N/A` and `None` are semantically empty for `Technique` — every procedure has
one — which is the same argument that exempted `Analytical Mode`, reached independently. The three
Solution TAPPs make it concrete: their Column F is a single value, a closed enumeration of one.
Recorded in `conventions.md` and `precedents.md`; `CONTROLLED_LIST_EXEMPT` updated in
`validate_tapp.py`. **No TAPP content changed** — checker and convention only. Clears 6 findings.

The precedent entry is explicit that this does **not** extend to `Coupled Technique(s)`, where `None`
is load-bearing: it is how a procedure records that no coupling is intended, and the Group 1 standard
depends on that value.

**`Collision/Reaction Cell (CRC) Configuration`: `Not applicable (SF-ICP-MS)` → `N/A`** in 4 TAPPs.
The parenthetical named one instrument class, but the field now also appears in LA-MC and LA-MC U-Pb,
where the reason a cell is absent is not "SF-ICP-MS" — so the option was asserting something false in
three of the four files. **This does not clear the finding**: the check still wants `None`. Whether
`None` means anything here is doubtful — "no cell in use" is already `STD (standard mode, no gas)` and
"instrument has no cell" is now `N/A` — which puts the field in the same class as `Technique`, a
candidate for the exemption table rather than a gap. Recorded as adjacent-and-open in `precedents.md`.

**`sentinel-stray-N` cleared, 203 cells across the SEM family.** Data rows in the sentinel column must
be empty; only group headers carry `N`. The SEM TAPPs had `N` on both. Header cells were preserved (6
per file) and only data rows cleared — the exact inverse of the group-header patch applied earlier
the same day, which is why that patch was deliberately restricted to header rows.

**Lint 62 → 52, ERROR 0.** `sentinel-stray-N` 4 → **0**; `controlled-list-options` 43 → 37.

### `SolutionIntroduction` reconciliation — worksheet built, and the task is smaller than recorded

The module has been `1-provisional` since extraction, described in three places as "15 of 16
descriptions unreconciled". Measured against the actual sources, **the real number of decisions is
12**, and the difference matters because it changes what the task is.

The three source variants survive in the **pre-composition** versions — composition overwrote columns
A–E in the live files — and all 16 fields are present in all three, so nothing was lost:

    Q  -> Solution_Q-ICP-MS_TAPP_v6.csv    (v7 is composed)
    SF -> Solution_SF-ICP-MS_TAPP_v6.csv   (v7 is composed)
    MC -> Solution_MC-ICP-MS_TAPP_v4.csv   (v5 is composed)

Breakdown: **3 fields are byte-identical** across all three sources (`Digestion Temperature`,
`Digestion Duration`, `Sample Uptake Rate`) — the default selection was trivially correct and there
is nothing to decide. **1** was already decided on evidence (`Isotope Dilution Spike` → MC). Of the
remaining 12, **8 are two-way** because two sources agree, and only **4 are genuine three-way reads**
(`Digestion Acid(s)`, `Chromatographic Separation Applied`, `Final Solution Matrix`,
`Desolvation System`).

`SolutionIntroduction_Reconciliation_WORKSHEET.csv` / `.xlsx` mirrors the column shape of
`Group1_Reconciliation_Decisions.csv` — the established record format — with the three candidate
texts placed side by side, each row labelled with its divergence class and with which source the
current module text came from.

The typical divergence is small and factual rather than stylistic. `Digestion Vessel Type` is
representative: all three share an identical opening sentence, and SF and MC add
"(e.g., Parr bombs required for complete silicate digestion at high temperatures)" while Q does not.
That is exactly the kind of difference the keyword proxy could not score and a reader resolves in
seconds — which is why the failed automation attempt is recorded as a methodological finding rather
than a tooling gap.

### Column F across the three Solution TAPPs — divergence classified, not just counted

Column F is **consumer-owned** (6.4), so divergence there is legitimate *by design*. The useful
question is therefore not "are these different?" but "is each difference **earned**?" — and there is
a single test that answers it: **does the content depend on the mass analyser?**

Measured across the live composed files: 6 fields identical, 4 two-way, 6 three-way. But the raw
counts mislead — **5 of the 6 "identical" fields are identical only because all three are empty.**
That is a gap, not agreement, and 6.4 is explicit that a module row is not complete until its
consumer supplies Column F.

Classified:

| Disposition | Count | Fields |
|---|---|---|
| **KEEP — earned** | 5 | `Isotope Dilution Spike`, `Chromatographic Separation Applied`, `Nebulizer Type`, `Spray Chamber Type and Cooling Temperature`, `Final Solution Matrix` |
| **HARMONISE — drift** | 5 | `Digestion Vessel Type`, `Digestion Acid(s)`, `Desolvation System`, `Nebulizer Gas Flow Rate`, `Wash Time Between Samples` |
| **WRITE — gap** | 5 | `Sample Aliquot Mass or Volume`, `Digestion Temperature`, `Digestion Duration`, `Sample Uptake Rate`, `Internal Standard Concentration` |
| OK | 1 | `Number of Digestion Steps` |

The earned five are genuinely analyser-driven: MC lists double spikes (IRMM-3636, Sn/Fe) because
double-spiking is an MC-ICP-MS mass-bias technique with no quadrupole counterpart; MC needs
quantitative separation resins (TRU, UTEVA, AG-MP-1, thiol) that a trace-element run skips entirely.
This is Rule 6.4 working exactly as intended — abstraction in B, instantiation in F.

The drifting five are not. Digestion vessels and acids do not know what detector sits downstream, yet
MC alone lists `TFE/TFM bomb` and adds `HF-HNO3-HClO4` while dropping `Aqua regia`. `Desolvation
System` is the same four or five instruments in a different order with spelling drift (`Apex IR` vs
`Apex-IR`). `Nebulizer Gas Flow Rate` reads 0.8-1.1 / 0.8-1.0 / 0.85-1.05 L/min — three different
ceilings with no instrument reason. Proposed resolution is the **union**, so no lab's real practice is
dropped.

`Final Solution Matrix` is the interesting hybrid and is filed under KEEP with a caveat: MC genuinely
runs lower acid strengths, but states them as molarity (`0.3 M HNO3`) where Q/SF use percent. The
values are earned; the **notation** is drift.

Delivered as `SolutionIntroduction_ColumnF_WORKSHEET.csv` / `.xlsx`.

**The five drifting values are now harmonised** — 12 cells across the three TAPPs. All three files
now agree on every one, `--check` returns `MATCH` against `SolutionIntroduction`, and three xlsx were
regenerated. Lint holds at 52, ERROR 0.

**A naive union was wrong on three of the five**, and the failures share a cause: treating Column F as
a uniform option list when the field's Data Type says otherwise.

- `Desolvation System` — the union preserved **both** spellings, `Apex IR` *and* `Apex-IR`,
  faithfully reproducing the exact drift it was supposed to remove. The list was internally
  inconsistent to begin with (`ApexQ`, `Apex IR`, `Apex-HF`), so all three TAPPs were normalised to
  the `Apex Q | Apex IR | Apex HF` pattern.
- `Nebulizer Gas Flow Rate` — Data Type is `Numeric (L/min)`, so Column F holds an example *range*,
  not allowed values. The union produced the meaningless
  `0.8-1.1 L/min | 0.8-1.0 L/min | 0.85-1.05 L/min`. Replaced with the single encompassing range.
- `Digestion Vessel Type` / `Digestion Acid(s)` — content correct, but new options were appended at
  the end. Reordered so related entries sit together (`TFE/TFM bomb` beside `Parr bomb`).

General lesson, and the second time today a set-operation looked like the answer and wasn't: **a
union is only valid where the values are a set.** Where Column F holds a range, a notation, or an
ordered list, set logic silently produces nonsense that still parses.

**Flagged, not fixed:** `Digestion Acid(s)` has Data Type `Text (free)` while `Digestion Vessel Type`
— structurally identical, a pipe-delimited option list ending `N/A | None | Other: specify` — is
`Controlled list`. One of the two is mistyped. Column E is module-owned, so it belongs with the
Column B reconciliation rather than here.

**Resolved the same day.** The two fields ask for different *kinds* of answer: an acid mixture is
compositional and effectively open-ended, whereas a vessel type is a device with a finite common set.
A controlled list for the vessel would have been defensible, but both are now `Text (free)`, chosen
for the simpler and more permissive pair. Changed in `Module_SolutionIntroduction.csv` (Column E is
module-owned) and recomposed into all three consumers — predicted 1 cell per TAPP, delivered exactly
1, `MATCH` afterwards.

### The 5 empty Column F cells — filled

None of the five is a `Controlled list`; all are `Numeric (unit)` or `Text (free)`, so Column F holds
an illustrative example rather than an enumeration, and no vocabulary needed sourcing.

Values are typical working ranges for solution ICP-MS of geological and extraterrestrial material,
written to show the *shape* of an acceptable answer. Each is annotated with the condition that
selects it — `90-120 °C (hotplate, Savillex beaker)` versus `150-190 °C (Parr bomb, refractory
phases)` — because the useful content of an example range is what makes it that value. They are
illustrative, not normative, and not drawn from a specific reference; a lab records its own.

The same values went to all three TAPPs: every one of these parameters sits in the digestion or
introduction chain, upstream of the mass analyser. `Sample Uptake Rate` was the closest call, since
MC commonly self-aspirates at low flow, so its example spans that case explicitly
(`50-100 µL/min (self-aspirating PFA nebulizer)`) rather than being split three ways.

15 cells filled. **Every field in the `SolutionIntroduction` block now has Column F content in all
three consumers** — the 6.4 completeness condition is satisfied for this module. `--check` returns
`MATCH` for all three, three xlsx regenerated, lint holds at 52 / ERROR 0.

### All 12 Column B decisions drafted for review

The blocker was never that the texts are unreadable — it was that a **keyword proxy** could not
discriminate between them. Reading them can. All 12 are drafted with Winner, Rationale and Adopted
description, in the shape of `Group1_Reconciliation_Decisions.csv`. Nothing applied to the module.

**The distinction that decided four rows.** The disqualifier "a module description must not be
technique-specific" needs a finer edge than it first appears. Naming an **analyser** ("prior to
MC-ICP-MS analysis") is disqualifying, because three TAPPs consume this module. Naming a **purpose**
("for isotope-ratio work") is not — it is a conditional that is true and useful for any consumer
doing that work, which is what 6.5 contemplates. Several MC variants carry the best consequence
content in the module wrapped in analyser-naming; those were adopted with the wrapper removed rather
than rejected. Rejecting them would have discarded real content on a technicality.

**Outcome:** 5 adopt MC, 3 adopt Q/SF or Q, 4 are synthesized. That MC wins so often is not
deference to the longest text — the Aug 8 lesson holds — but because MC's authors wrote *trade-offs*,
which is the highest-value description content: `Desolvation System` alone records that desolvation
buys sensitivity at the cost of mass bias stability, which tells a user when **not** to use it.

**Two rows where the majority is wrong, and one to read closely:**

- **`Nebulizer Type` — 2-of-3 agreement is not evidence.** SF and MC both say the nebulizer "affects
  droplet size distribution and **uptake rate**" — but `Sample Uptake Rate` is a separate field in
  this same module, so the majority wording blurs the boundary between two adjacent fields. Q's
  "sample introduction efficiency" names the property the nebulizer actually governs. Recommended Q,
  against the majority, on the boundary criterion.
- **`Spray Chamber…` — adopt MC but trim.** Its first added clause ("Scott double-pass and cyclonic
  are standard") merely restates Column F and was dropped per 6.4; its second explains that a spray
  chamber may sit downstream of a desolvating nebulizer, which is genuine boundary content linking
  this field to `Desolvation System`.
- **`Chromatographic Separation Applied` — flagged HIGH.** MC has the only variant that says *why*
  separation is needed, but names the analyser twice. The synthesized text carries MC's reasoning on
  SF's frame, and asserts that separation is "usually mandatory for isotope-ratio procedures and
  optional for concentration measurement" — a generalisation from MC's stronger claim that a
  separation chemist may want to soften.

**Residue noted, not changed:** `Internal Standard Concentration` carries "(µg/L or ppb)" in Column B
while its Data Type is already `Numeric (µg/L)` — a unit duplicated across B and E. Worth dropping at
the next module edit.

### Applied — `Module_SolutionIntroduction` promoted to version 1

All 12 accepted as drafted. **9 of the 12 changed the module**; the other 3 were already correct —
`Sample Aliquot Mass or Volume`, `Nebulizer Type` and `Internal Standard Concentration` all resolved
to the Q/SF text the default selection had happened to pick. Together with the 3 byte-identical rows
and the pre-decided `Isotope Dilution Spike`, that is 7 no-ops and 9 edits, which reconciles exactly.

Recomposition predicted 9 cells per TAPP and delivered 9 in each of the three; `--check` returns
`MATCH` for all three afterwards. Lint holds at **52, ERROR 0**. Three xlsx regenerated.

**The provisional marker is gone.** It existed for one reason — that 15 of 16 descriptions had been
selected by default rather than decided — and that is no longer true. Version `1-provisional` → `1`,
status `provisional` → `active` in `TAPP_Module_Register.csv`, the three version references in
`composed_tapps.json` updated, the manifest's `reconciliation` note rewritten to record what was
decided rather than why it could not be, and the open item struck from conventions §6.9.

`SolutionIntroduction_Reconciliation_Decisions.csv` is now the permanent record, in the same shape as
`Group1_Reconciliation_Decisions.csv` — the second module to have one.

**Version numbers of the three consuming TAPPs were NOT bumped**, and the reasoning is worth stating
because it will recur. Version and Date Tracking assigns integer bumps to field additions, removals,
tier changes and mode-flag changes; description updates take "a decimal update or column H date
update only". Everything applied here is a description, example or data-type change, so column H
was stamped `2026-08-10` on every touched row and the filenames left alone. The one debatable element
is `Digestion Vessel Type`'s Data Type change, which is a Column E edit and not on either list.
**If that is read as structural, the three TAPPs need Q v8 / SF v8 / MC v6.** Flagged rather than
assumed, since renaming files ripples into `composed_tapps.json`, the planning table and every xlsx.

**What this closes.** `SolutionIntroduction` was the only module shipping content nobody had
verified. Of the eight modules, seven are now settled; `ArAr` remains built-but-unconsumed, which is
a different and weaker condition — its specificity is untested rather than its content unreviewed.

---

## 2026-08-10 | CROSS-TAPP | `Uncertainty Level` split from `Uncertainty Propagation Method`

`Uncertainty Level and Propagation` split into two fields across the 7 TAPPs that carried it:

| Field | C | D | Data Type |
|---|---|---|---|
| `Uncertainty Level` | **Basic** | **Read-Only** | `Controlled list / Text` |
| `Uncertainty Propagation Method` | Advanced | Editable | `Text (free)` |

### The precedent was narrowed, not reversed — and the distinction is the whole argument

This was carried as "reverses a documented decision", which turned out to be the wrong
characterisation, and checking it changed the shape of the work.

`precedents.md` holds "Uncertainty Propagation Method — Advanced/Editable rather than
Basic/Read-Only". Reading it, its argument is **entirely about the propagation framework**: many labs
use informal uncertainty estimates without a formally specified framework, so mandating one at Basic
would either exclude legitimate procedures or generate boilerplate. That is sound, and it is preserved
untouched — the propagation half keeps C=Advanced/D=Editable and **takes its original name back**, so
the precedent applies to it by name again.

The decisive detail is the entry's title. It was written when the field was called
`Uncertainty Propagation Method` — propagation only. The **level** was merged in later, by the
2026-08-08 rename to `Uncertainty Level and Propagation`, and inherited C=Advanced by accident of
packaging rather than by argument. Nothing was ever written justifying the level as optional. So the
split restores the precedent's scope rather than overturning it, and no argument had to be defeated.

### Why the level is Basic

`analysis/Test5_Geochronology_Module_CrossSystem.csv` row 3 records "Uncertainty Level Convention" as
REQUIRED in **6 of 6** independent community dating standards, recommends C=Basic / D=Read-Only, and
records its status as "PARTIAL — folded into geochron Uncertainty Level and Propagation". Unlike a
propagation framework there is no informal case to exclude: every lab that reports an uncertainty
quotes it at some level, and a value whose level is unstated is uninterpretable.

The strongest evidence was in the merged field's own description, whose closing sentence read *"A
reported uncertainty is not interpretable without **both halves**"* — a description stating outright
that it held two fields, one of which six standards make mandatory while the packaging made it
optional.

D=Read-Only does not hit the precedent's void-import trap, which applies only when C=Advanced: a
C=Basic field always carries a procedure value to inherit, and the level is a standing lab convention
rather than a session decision.

### Execution

Not a module field — at 2 fields it is below Rule 6.10's five-field threshold — so this was Rule 4
propagation across 7 TAPPs. `Uncertainty Level` was inserted immediately **before** the propagation
field, which sits well inside Group 5 in all 7, leaving Rule 5's requirement that
`Constants and Reference Values Used` remain last in Group 5 undisturbed; verified afterwards in all
7. Mode flags were cloned from the propagation row so the new field carries the same applicability;
the sentinel cell was left empty, as required for a data row.

**Literature assessment cells on the new field were left empty.** Existing extractions stay on the
propagation row where they were made (13, 13, 1, 0, 5, 6, 0 across the seven). Several visibly
contain level information — "2SE of individual spot measurements reported" — so a Phase 3 re-pass
could populate the new row, but copying them wholesale would fabricate extraction never performed
against this field.

**All 7 integer-bumped**, adding a field being a major structural revision: LA-Q/SF v5→v6 and its
U-Pb variant, LA-MC v2→v3, LA-MC U-Pb v1→v2, Solution Q and SF v7→v8, Solution MC v5→v6. Old versions
remain in place. `composed_tapps.json` paths and `derived_from` references updated, planning table
statuses updated for rows 5, 5a, 6, 7 and 7a, 7 xlsx generated. Composition re-verified against every
module on every new version — 28 module-TAPP pairs, all `MATCH`.

**Lint 52, ERROR 0, unchanged** — the new field introduced no findings, and the linter is now reading
the bumped versions.

### Generalisation recorded

When a field name contains "and", check whether its two halves warrant the same tier. This one merged
a component mandated by six community standards with a component deliberately left optional, and the
merge silently demoted the mandatory half. A compound field name is a reasonable place to look for a
mis-tiered requirement — `Spray Chamber Type and Cooling Temperature` and
`Calibration Factor and Determination Method` are the obvious next candidates to check.

### Rule 6.4 extended — where per-TAPP specificity goes

Prompted by a proposal to keep the most general description in the module and "modify for each new
TAPP if needed". The first half is already the rule. The second half was tested rather than argued:
appending one clause to a Column B description in a copy of Solution Q v7 made
`compose_tapp.py --check` report `DIFFERS`, and the next recomposition would overwrite it silently.
A per-TAPP description tweak is not a policy that can be adopted — it is a change the tooling undoes.

The need behind the proposal is already met by Column F, which exists for exactly this. Recorded in
6.4 as a three-part rule: the general description lives in the module and is never edited in a
consumer; per-TAPP specificity goes in Column F; and if a TAPP genuinely needs a different
description, that is evidence the field fails the 6.1 specificity test and should not be module-owned.

Also recorded there, because it is the load-bearing argument: **field-name consistency was already
achieved before Rule 6 and was not sufficient.** 14 of 17 Group 1 descriptions had diverged under
identical field names. Same name, different meaning is worse than different names, because it is
invisible — a search finds them, a diff does not flag them, and a curator merging two datasets
assumes they agree.

---

## 2026-08-10 | LA-MC-ICP-MS v1 → v2 | Phase 3 opened: Zhang et al. 2022 assessment column transferred

The `Zhang et al. 2022 (At. Spectrosc. 43)` column — one of the three columns that existed nowhere
outside the retired `LA-ICPMS_TAPP_v13`, and the only one whose destination TAPP already exists —
moved into LA-MC-ICP-MS. That paper is this TAPP's own Phase 0 seed, so the column was assessment
content sitting in an archive while the live TAPP it describes had **zero** literature assessment
columns. v2 has one.

The retirement entry above deliberately left this undone, on the grounds that folding a
field-name-matched transfer into a file move is how content gets mangled. That was right: v13 has 107
fields and LA-MC-ICP-MS 132, and a column copy would have silently misaligned from Group 3 onward.

### The transfer, and what a name match was not sufficient to decide

89 filled source cells, matched by Metadata Item. **85 matched by name**, and — applying the lesson
recorded in the retirement entry, that a name diff over-reports in *both* directions — all 85 had
their descriptions compared rather than assumed. 83 are byte-identical. The two that differ,
`Ablation Cell Type` and `RF Power`, are compatible refinements in LA-MC-ICP-MS (added washout
rationale; `RF Power` relaxed from "fixed, cannot be changed" to a registered target the analyst may
fine-adjust, consistent with its D=Editable). Neither changes what the Zhang value means.

The remaining 4 were resolved by reading, and against Table 1 of the source PDF, which was re-read in
session rather than trusted from the archived cells:

| Source field | Resolution |
|---|---|
| `Auxiliary and Cool Gas Flow Rates` | **split** into `Coolant (Plasma) Gas Flow Rate` + `Auxiliary Gas Flow Rate` — the same two-field resolution the retirement entry found for LA-Q/SF, and Table 1 states them as two separate rows |
| `Drift Monitor Frequency` | → `Calibration Standard Measurement Frequency`, whose description defines the drift-monitoring bracketing interval |
| `Spectrometer Dwell Time` | → `Integration Time per Cycle` |
| `Pulse/Analog Detector Nonlinearity Correction` | **no destination**; not transferred |

**The dwell-time case resolves differently here than it did for LA-Q/SF, and the difference is the
point.** The retirement entry mapped `Spectrometer Dwell Time` onto `Dwell Time per Mass` — a
byte-identical rename. LA-MC-ICP-MS **has no `Dwell Time per Mass`**: it is one of the six sequential-
analyser fields Phase 0 dropped, because a multi-collector array does not dwell on masses in
sequence. So the abstract field mapping is unavailable, and the routing had to be decided on the
cell's *content* instead: the recorded value is "0.524 s integration time per cycle", which is
Table 1's `Integration Time (s) 0.524 s` row and is exactly what the simultaneous-collection field
asks for. A correct mapping between two TAPPs is not automatically correct between a third.

`Pulse/Analog Detector Nonlinearity Correction` is reported rather than placed. Its value was
`N/A (MC-ICP-MS … no pulse/analog transition)` — the field does not apply to this technique, which is
why the TAPP omits it, so the cell carries no information to lose. `Ion Counter Dead Time` is not a
substitute; its own description says so explicitly.

### One thing found and deliberately not acted on

`Analyte` is a valid name *and* description match and transferred verbatim — but its content
(`L4 (⁸³Kr), L3 (¹⁶⁷Er²⁺), … H3 (⁸⁸Sr)`) is Table 1's row labelled **Cup-configuration**, and
LA-MC-ICP-MS has a dedicated `Collector Configuration` field that v13 did not. Nothing is lost — the
text is in the TAPP — but it is in one field where it belongs in two. Populating the second is
re-extraction, not transfer, and was left for the extraction pass.

This is the same shape as the four fields Rule 6.1 records: the destination TAPP is more specific than
the source, so a faithful transfer preserves the *text* while under-using the *structure*.

### What is not filled

**45 fields carry no Zhang value.** Six were blank in the source column too (fields added to v13 after
that assessment was made). The other 39 are LA-MC-ICP-MS's own — largely the MC block that Phase 0
composed in specifically: `Collector Configuration`, the three Faraday cup fields,
`Mass Bias Correction Strategy`, `Number of Blocks per Measurement`, `Number of Cycles per Block`,
`Baseline Measurement Approach`, `Peak Flatness Method and Threshold` / `Peak Flatness`.

They are left **blank, not `N`**. `N` asserts "applicable but not stated in the paper", and that
assertion cannot be made by a transfer — only by reading the paper against each field. Blank records
"not assessed", matching what the source column itself did for its own post-hoc fields.

**Several are directly available.** Table 1 alone states `Block number 1`, `Cycles of each block 120`,
the cup configuration, and the X-skimmer/JET cone setup; the text states peak flatness as a tuning
objective and the laser-off-cycles baseline. The PDF is at
`LA-MC-ICP-MS/Seed Papers/Zhang et al 2022 - in situ Rb-Sr LA-MC-ICP-MS.pdf`. That is a Phase 3
extraction pass and is the obvious next step — **this transfer starts Phase 3, it does not close it.**
Zhang et al. 2018 and a Lu-Hf paper are still outstanding per Phase 0 §5.

### Verification

- Columns A–L **byte-identical** to v1; the change is one appended column.
- `compose_tapp.py --check` reports **MATCH** for all four modules (`Group1`, `LaserAblation`,
  `MCICPMS`, `ReportingCore`), confirming literature assessment columns are consumer-owned under
  Rule 6.4 and that adding one does not desynchronise a composed TAPP.
- Source-cell accounting balances: 85 direct + 2 renamed + 1 split into 2 + 1 unplaced = 89 in,
  89 destination cells out. Asserted in the patch script, not eyeballed.
- Group header rows carry `N` in the new column per `references/lit_assessment.md`. The source column
  left them blank; normalised to the documented convention and to dominant library practice (EPMA,
  SEM, TEM, Solution Q/SF).
- Column H untouched — adding an assessment column is not a substantive edit to any field definition.
- xlsx regenerated: 13 columns, 3 mode flags, sentinel at col 11, 1 literature assessment column.

**Lint 275 → 275, ERROR 0 — this change adds zero findings**, verified by running the full validator
with the new file present and again with it removed.

**A note on the baseline.** This work was briefed against a baseline of 395. That figure was correct
when the session started and is now stale: the date-cleanup entry immediately above landed at 13:20
today, mid-session, and took the library 395 → 275. The two sessions did not collide — that entry
explicitly left the 96 LA-MC-ICP-MS `date-missing` findings alone for this one, and this one touched
no file that one touched. Those 96 remain open and should get the same lineage-computed treatment;
the field names are shared with LA-Q/SF v5, so the map already computed applies.

`LA-MC-ICPMS_UPb_TAPP_v1` still derives from v1 and does **not** carry the column. Recompose from v2.


---

## 2026-08-11 — LA-Q/SF-ICP-MS split into LA-Q-ICP-MS and LA-SF-ICP-MS

**Why.** The combined TAPP was the library's outlier: `Solution Q-ICP-MS` and `Solution SF-ICP-MS` have
always been separate TAPPs with separate Phase 0 records, and a registered procedure describes one
instrument. The split arose from the Rule 7 ("Keyed By") work — the Comments-column audit found 38 rows
carrying `Q-ICP-MS only` / `SF-ICP-MS only` labels, i.e. free text doing the job of a structural
distinction. Splitting removes the need for an instrument-variant column entirely.

**Split arithmetic** (base TAPP, 126 content rows): 7 Q-only, 3 SF-only, 1 applying to both with different
content per instrument, 115 shared.

| Successor | Content rows | Cols (lit) |
|---|---|---|
| `LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v7.csv` | 123 | 18 (6) |
| `LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v7.csv` | 119 | 19 (7) |
| `LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v7.csv` | 132 | 18 (6) |
| `LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v7.csv` | 128 | 19 (7) |

**Content changes beyond row selection**
- `Mass Resolution Setting` — the field that motivated the split. Column F previously carried both answers
  at once (*"Unit resolution — quadrupole (fixed) | Low resolution — SF …"*). Each successor now states
  one. **In the Q TAPP D moves Editable -> Read-Only**, because unit resolution is fixed by instrument
  design and the analyst cannot adjust it. This is the one tier change in the split.
- `ICP-MS Type` — allowed-value list narrowed to the relevant analyser in each successor.
- `Q-ICP-MS only` / `SF-ICP-MS only` comments removed as redundant. `Analyte-Specific` labels preserved
  (verified on `Mass Resolution per Analyte`, whose Comments read `SF-ICP-MS only; Analyte-Specific`).
- Literature assessment columns split by the instrument named in each column header: 6 Q-instrument papers
  to the Q TAPPs, 7 SF-instrument papers to the SF TAPPs. The combined TAPP had been assessing
  Q-instrument papers against SF-only fields and vice versa.

**Naming and lineage.** `ICP-MS` not `ICPMS`, matching the solution TAPPs. Versioning continues the v6
lineage at v7 rather than restarting, so the split reads as a branch. Parent archived to
`Superseded TAPPs (2026-08-11)/LA-Q_SF-ICP-MS (split into Q and SF)/` with a README holding the
field-level record. The SF seed-paper folder moved to `LA-SF-ICP-MS/Seed Papers/`.

**Verification**
- `validate_tapp.py`: 0 ERROR on all four files. 6 WARN (Q) / 5 WARN (SF), all `controlled-list-options`
  — identical in kind and count to the pre-split v6 baseline, so the split introduced nothing. These
  warnings will clear when the Rule 7 draft's A.4 decision (`N/A` as an explicit Column F value) is applied.
- `compose_tapp.py --check`: **16/16 MATCH** across Group1, LaserAblation, ReportingCore on all four files,
  plus Geochronology and UPb on the two U-Pb variants. Module integrity fully preserved.

**Registries updated.** `composed_tapps.json` (2 entries -> 4; 16 composed TAPPs total),
`TAPP_Composed_Variants.csv` (LA-Q/SF x U-Pb -> two rows; also corrected a stale LA-MC-ICP-MS x U-Pb path
that still pointed at v1 while current is v2), `TAPP_Planning_Table.csv` (row 7 -> 7 LA-Q + 7a LA-SF, with
LA-MC / LA-ICP-ToF-MS / LA-ICP-TQ-MS renumbered 7b/7c/7d), `TAPP_Module_Register.csv` (Group1 and
ReportingCore 14 -> 16 consumers; LaserAblation 4 -> 6; Geochronology and UPb 2 -> 3).

**Library is now 16 TAPPs.** Rule 7 retrofit counts in `DRAFT_Rule7_KeyedBy_2026-08-11.md` §7.10 must be
recomputed against 16 before that pass runs.

**Deferred to the Rule 7 pass, not done here**
- `LA-MC-ICPMS_TAPP_v3` and `LA-MC-ICPMS_UPb_TAPP_v2` each carry 8 rows of `Q-ICP-MS only` /
  `SF-ICP-MS only` comments inherited from LA-Q_SF when they were derived. Wrong for a multi-collector
  TAPP. Deferred rather than patched in place so they get one version bump, not two. Recommendation:
  rather than blanking the CRC rows, align them with `Solution MC-ICP-MS`, which already carries the
  correct wording (*"only applicable to collision/reaction-cell-equipped MC-ICP-MS instruments"*).
- A `Module_QuadrupoleICPMS` / `Module_SectorFieldICPMS` pair is now a live extraction candidate, since
  `LA-Q` + `Solution Q` and `LA-SF` + `Solution SF` each share an analyser block. Per Rule 6.10 modules are
  extracted, not invented — flagged, not built.


---

## 2026-08-11 — Rule 7 "Keyed By" retrofit (Rules 7–10) across the whole library

**Why.** The Column G label `Analyte-Specific` — 150 instances across 45 field names — was found by a
six-test audit (`RepeatKey_Audit_Test1-4_2026-08-10.csv`, 154 rows) to conflate at least four distinct
cardinality keys while missing a fifth entirely. Fewer than half the labelled fields were actually keyed
by analyte (22/45). The analyte/channel cluster was 90% D=Read-Only-or-Editable while the reported-property
cluster was 82% D=Basic (Fisher exact p = 9.8e-06) — two structurally different classes of field under one
label. Thirteen unlabelled fields were keyed by reported property, including all six fields of
Module_Geochronology and Rule 5's `Constants and Reference Values Used`.

**What replaced it.** A `Keyed By` column at **Column I** (after Last Update, before the mode flags),
declaring what each field's value repeats over. Anchors: `sampling unit` and `reported property`
(universal), `channel` and `analyte` (conditional — `analyte` is absent from Lab-XCT, Raman and fission
track). Secondary: `standard`, `conversion`, `model component`, `acquisition pass`, `preparation step`.
Notation: `(none)`, `A > B` (containment), `A x B` (cross-product, first key outer), `defines: A`,
`pair: A`. Column I was chosen over the semantically better Column F because module manifests encode
column letters literally; the trade-off is recorded in conventions.md 7.1.

**Executed**

| | |
|---|---|
| TAPPs | 16 |
| Content rows carrying a Keyed By value | 1,690 (372 non-`(none)`) |
| Modules | 8 of 8, plus `"I"` added to all 8 manifests |
| New mandatory field rows | 30 — Rule 8 x 10, Rule 9 x 16, Rule 10 x 4 |
| Comments rows with content, before -> after | ~330 -> 63 |
| Controlled lists completed with N/A / None (A.4) | 63 |
| Conditions moved from Comments into Column B (A.4) | 10 |

New rules: **Rule 8** (`Reported Variables and Units` mandatory in Group 4 — enumerates the
reported-property domain and declares the procedure's scope boundary), **Rule 9** (`Sampling Unit`
mandatory in Group 2 — no TAPP previously declared the subdivision one row of reported values corresponds
to), **Rule 10** (`Error Correlation Between Reported Quantities`, restricted to TAPPs reporting jointly
interpreted quantities; verified absent library-wide before adding, so concordia ellipses could not be
reconstructed from what the TAPPs captured).

**Scripts.** `compose_tapp.py` — `COL_KEYEDBY`, `FIRST_MODE_COL` 8->9, `LETTER` gains `I`, and
`owned_for()` implementing `keyed_by_overridable` (specified but deliberately unpopulated — every module
field audited holds one key across all consumers). `validate_tapp.py` — new `check_keyed_by` enforcing the
blank check, vocabulary, the forbidden `mode` key, invariant 4, Rules 8/9 presence, and a warning when
Comments still names a mode. `tapp_to_xlsx.py` — column width and Legends Table 4, listing only the keys
each TAPP actually uses.

**Docs.** Rules 7–10 spliced into `conventions.md` with the column structure table, width table, Legends
section, Column B/F/G notes, Rule 6.4 ownership table and the vocabulary table all updated.
`SKILL.md` Common Mistake #5 rewritten — the old text ("use Analyte-Specific rather than
Element-Specific") was the mechanism that produced the defect, since it told every TAPP author to reach
for the least universal axis by default. `field-review.md` and `workflow.md` (Phase 0 now declares the key
vocabulary alongside the mode set, and records which anchors are **absent**).

**Sequencing proved itself.** Modules first, recompose, then TAPP-owned rows. Applying A.4 wrote condition
sentences into Column B on five module-owned rows in Solution MC-ICP-MS; `compose_tapp.py --check`
reported DIFFERS immediately. Fixing it in the module and recomposing propagated the improved description
to four other consumers. That is Rule 6.6 working exactly as designed.

**Verification.** `validate_tapp.py --root .`: **0 ERROR, 0 WARN**, 15 INFO (tier-divergence).
`compose_tapp.py --check`: **50/50 MATCH** across every TAPP x module pair. Every new version has a
regenerated xlsx.

**One INFO is newly ours and now documented.** `Mass Resolution Setting` diverges — D=Read-Only in
LA-Q-ICP-MS (unit resolution is fixed by instrument design) versus D=Editable in the SF and MC TAPPs.
Recorded in `precedents.md` per the validator's Rule 2/4 prompt. The other 14 tier divergences pre-date
this pass.

**Versions bumped (all 16).** EPMA v9->v10; LA-Q v7->v8 (+U-Pb); LA-SF v7->v8 (+U-Pb); LA-MC v3->v4;
LA-MC U-Pb v2->v3; SEM / SEM_Composition / SEM_FIBSEM / SEM_Imaging v6->v7; Solution MC v6->v7;
Solution Q v8->v9; Solution SF v8->v9; TEM v9->v10; Lab-XCT v10->v11.

**Deferred, explicitly.** The draft's A.3(b) proposed adding `EDS`, `EELS` and `4D-STEM` as mode columns
to the TEM TAPP, which would move 35 Comments rows into the mode flags. That is a Phase 0 revision needing
per-row Y/N judgements across 87 fields x 3 new modes — not mechanical, and not done here. Those rows keep
their Comments labels legitimately under 7.6 until it is.

**Comments column retained** at the author's decision, now carrying 63 rows: TEM signal/detector labels
(pending the deferred item above), KED/DRC cell applicability, and a handful of genuine qualifiers.


---

## 2026-08-11 (later) — TEM Comments resolved by conditional treatment, not mode columns; Comments column now empty library-wide

**The A.3(b) proposal was wrong and was abandoned on inspection.** The plan was to add `EDS`, `EELS` and
`4D-STEM` as mode columns to the TEM TAPP. Reading the TAPP showed that would duplicate two mechanisms it
already has and contradict its own Phase 0 design:

- `Spectroscopic Detector(s)` already states the gating rule in its own description: *"EDS and EELS
  parameter fields in Group 4 apply only when the corresponding detector is listed here."* A conditional,
  not a mode.
- `Analytical Sub-mode` already enumerates 4D-STEM, EFTEM and Precession ED beneath the three top-level
  modes — TEM Phase 0 deliberately built a two-level Mode -> Sub-mode structure.
- The mode flags already carried applicability correctly (EDS/EELS rows `Y/Y/N`, 4D-STEM rows `N/N/Y`).
  The Comments were carrying a *second, orthogonal* condition, which is what A.4 exists for.

**What was done instead — A.4 treatment.**

| | |
|---|---|
| TEM conditional fields given an explicit condition in Column B | 29 |
| TEM rows whose Comments were explanatory prose, folded into Column B | 9 |
| `N/A` added to Column F (TEM) | 19 |
| KED/DRC rows across LA-MC (+U-Pb), Solution MC and Solution Q, conditioned on `Collision/Reaction Cell (CRC) Configuration` | 22 |
| EPMA rows whose bare `EDS` comment the mode flags already carried | 2 |

Conditions reference the field that governs them by name — `Spectroscopic Detector(s)`,
`Analytical Sub-mode`, `Collision/Reaction Cell (CRC) Configuration` — so the dependency is stated where a
reader will meet it.

**Comments now carries content on ZERO rows across all 16 TAPPs** (was ~330 before the Rule 7 pass, 63
after it, 0 now). The column is retained by author decision for future one-off annotation.

**Three Keyed By corrections** fell out of the same examination. `EELS Edges` describes itself as *"the
EELS-specific counterpart to the Analyte field"* — it enumerates the edge domain, so it is
`defines: channel`. That in turn makes `EELS Background Subtraction Method` and
`EELS Sensitivity and Detection Limit` `channel` rather than `analyte`. During the main retrofit I had
assigned those two `analyte` on the assumption that TEM had no edge enumerator; it had one all along.

**Versioning.** TEM was bumped v10 -> v11 because it carried the three Keyed By corrections. The other
files received description and example updates with no structural change, which under the version
convention is a Last Update date bump only — no integer increment. All 16 xlsx regenerated.

**Verification.** `validate_tapp.py --root .`: 0 ERROR, 0 WARN, 15 INFO (the same pre-existing
tier-divergence set, one of which is the documented `Mass Resolution Setting` divergence).
`compose_tapp.py --check`: 50/50 MATCH. No module-owned row was edited in a TAPP this time — the
CRC and gas fields are TAPP-owned, checked before editing.


---

## 2026-08-11 (later still) — category A tier divergences reconciled to the LA family

Following the post-retrofit lint audit, the four "cohort drift" divergences were reconciled toward the
LA/geochronology tier assignments. Ten tier cells across the three Solution ICP-MS TAPPs:

| Field | Change | TAPPs |
|---|---|---|
| `Analytical Accuracy and Assessment Method` | C=Advanced -> Basic | Solution MC, Q, SF |
| `Within-Session Analytical Precision and Assessment Method` | C=Advanced -> Basic | Solution Q, SF |
| `Guard Electrode` | C=Advanced -> Basic | Solution MC, Q, SF |
| `Dwell Time per Mass` | D=Read-Only -> Editable | Solution Q, SF |

**Reconciled toward LA rather than toward the majority.** The LA assignment is the one with an argument
behind it: accuracy and within-session precision are at least as central to solution ICP-MS as to laser
ablation, since solution work is the reference method for concentration. There was no basis for them being
mandatory in one family and optional in the other.

**Two fields touched only two of the three Solution TAPPs.** Solution MC-ICP-MS has no
`Dwell Time per Mass` (a multi-collector does not dwell on masses) and records within-session
reproducibility under `In-Run Isotope Ratio Reproducibility and Assessment Method`. That field was left
alone — it is a differently-named field, not a divergent one, and whether it should follow the same
reconciliation is a separate question.

**Versions.** Solution MC v7->v8, Solution Q v9->v10, Solution SF v9->v10 — integer bumps, tier changes
being a major structural revision under the version convention. None of the four fields is module-owned
(checked before editing), so no recomposition was needed.

**Verification.** `compose_tapp.py --check` 50/50 MATCH; `validate_tapp.py --root .` 0 ERROR, 0 WARN,
**11 INFO** (down from 15). `TAPP_Lint_Report_2026-08-11.csv` regenerated.

**Remaining 11, all recorded in `precedents.md`:** five documented as intentional (`Analysis Sequence`,
`Sample Persistent Identifier`, `Mass Resolution Setting`, `EDS Detector Configuration`,
`EDS Live Time per Point or Pixel`), three category B with a technique argument now written down
(`Sample Preparation Method`, `Per-Analyte Calibration Strategy`, `Phase Identification Method`), and
three category C still needing a decision (`Detection Limit Method`, `EDS Acquisition Mode`,
`Step Size / Pixel Size`).


---

## 2026-08-11 (final) — category C tier divergences resolved

**`Detection Limit Method` -> C=Basic, D=Read-Only in all 12 TAPPs.** Was C=Advanced everywhere with D
split (Basic in the 9 ICP-MS TAPPs, Editable in EPMA/SEM/SEM_Composition), so this is a re-tiering, not
only a divergence fix.

- C=Basic follows the `Uncertainty Level` precedent of 2026-08-10: a reported detection limit is not
  interpretable without knowing whether it is 3-sigma of background, Longerich et al. 1996, or 10x blank SD.
- D=Read-Only is what the field's own description already asserted in prose: *"Must be consistent with the
  method applied to generate the Detection Limit values reported above."*
- The pair now follows the Oxide Production pattern: method is procedure-fixed (Basic/Read-Only), values
  are a session outcome (`Detection Limit` unchanged at C=Advanced/D=Basic).

**`Step Size / Pixel Size` -> C=Basic, D=Editable in SEM and SEM_Composition**, reconciled to EPMA. The
author's initial reading was C=N/A/D=Basic; that was declined because the existing precedent
"Analysis-level only fields (C=N/A) for spatially determined mapping parameters" already rules on this
field. It assigns C=N/A to map *extent* (dictated by whichever feature is chosen at analysis time) and
C=Basic/D=Editable to step size, which controls intrinsic spatial *resolution* and is a procedure design
choice. EPMA was already compliant; SEM and SEM_Composition were the drifted pair.

**`EDS Acquisition Mode` -> unchanged, reclassified as intentional.** It had been sorted into category C on
tier values alone, without checking how the field interacts with each family's mode columns. The EPMA/SEM
description says it specifies beam positioning *"within the declared Analytical Mode"*, and those TAPPs
carry `EDS Point Analysis` and `EDS Mapping` flags — the acquisition strategy follows from the declared
mode, so D=Read-Only. TEM's modes encode nothing about EDS strategy, leaving it a genuine per-session
choice, so D=Editable. Reconciling would make one family wrong. Recorded under the "EDS architecture"
precedent alongside the two EDS tier differences already documented there.

**Scope.** 14 tier cells across 12 TAPPs. Neither field is module-owned (checked before editing), so no
recomposition was needed. Integer version bumps, tier changes being a major structural revision: EPMA
v10->v11, SEM v7->v8, SEM_Composition v7->v8, LA-Q v8->v9 (+U-Pb), LA-SF v8->v9 (+U-Pb), LA-MC v4->v5,
LA-MC U-Pb v3->v4, Solution MC v8->v9, Solution Q v10->v11, Solution SF v10->v11.

**One bump was made in error and reverted.** A filename substring match caught `SEM_FIB`**`SEM_TAPP`** and
bumped SEM_FIBSEM to v8 although it carries neither field. The v8 file was verified byte-identical to v7,
deleted, and the registries reverted. No data was affected.

**Verification.** `compose_tapp.py --check` 50/50 MATCH; `validate_tapp.py --root .` 0 ERROR, 0 WARN,
**9 INFO**. `TAPP_Lint_Report_2026-08-11.csv` regenerated.

**Divergence trajectory across the day: 15 -> 11 -> 9.** Of the 9 remaining, 6 are recorded as intentional
(`Analysis Sequence` in part, `Sample Persistent Identifier`, `Mass Resolution Setting`,
`EDS Detector Configuration`, `EDS Live Time per Point or Pixel`, `EDS Acquisition Mode`) and 3 are
category B, left open by choice with their technique arguments written down (`Sample Preparation Method`,
`Per-Analyte Calibration Strategy`, `Phase Identification Method`).


---

## 2026-08-11 (recording audit) — module versions bumped, two record gaps closed

A completeness check after the day's work found three things unrecorded. All now fixed.

**1. Module versions had not been bumped.** All eight modules gained Column I (`Keyed By`) under Rule 7 —
a structural change to a module — and `Module_MCICPMS` and `Module_SolutionIntroduction` additionally
gained the A.4 condition sentences in their descriptions. Their version numbers had stayed put, so the
register, the manifests and `composed_tapps.json` were internally consistent but all recording a
pre-change state: a consumer could not tell that `Module_Group1` v2 today differed from v2 yesterday.

Bumped: ArAr 1->2, Geochronology 2->3, Group1 2->3, LaserAblation 1->2, MCICPMS 2->3, ReportingCore 1->2,
SolutionIntroduction 1->2, UPb 2->3. Each manifest gained a `decisions` note saying what changed.
`TAPP_Module_Register.csv` and the per-consumer `version` fields in `composed_tapps.json` updated to match.

**2. The `Keyed By` exceptions register disagreed between doc and code.** `conventions.md` 7.8.7 said
"Currently two entries"; `KEYED_BY_EXCEPTIONS` in `validate_tapp.py` holds four — `Detection Limit` and
`Dwell Time per Pixel` were added during the retrofit when their technique-dependence was discovered, and
the rule text was never updated. The doc now lists all four with their rationale.

**3. Memory recorded LA-Q and LA-SF at v7.** They reached v9 the same day. The memory entry now points at
the folders rather than pinned filenames, with a note that versions moved several times in one day.

Verified unaffected: the `RepeatKey_Audit_Test1-4` CSV already records both EELS fields as `channel`,
matching where the TAPPs ended up — the `analyte` assignment was a transient error inside the retrofit's
key map, corrected during the TEM pass, and never reached the artifact.


---

## 2026-08-11 (final) — Rule 7 declaration invariants strengthened; vocabulary shrinks from ten keys to six

The author proposed two rules: a `Keyed By` label may only be used if the field that defines it exists,
and there may be only one such defining field. Both were adopted, and both found real defects.

**7.4a — the invariant now applies to every key, not just the four anchors.** The first implementation
checked anchors only, which was expedient rather than principled. Applying it universally surfaced four
undefined keys: `conversion` (16 TAPPs), `acquisition pass` (11), `background position` (3),
`preparation step` (3).

**7.4b — exactly one definer per key.** Seven violations: `channel` had two definers in the LA-MC pair
and three in TEM; `reported property` had two in the three U-Pb TAPPs and in Solution MC.

**7.4c — a definer needs a consumer**, which is the sharpening the second rule implies. `defines: X`
where nothing is keyed by X describes a field holding a list, not a key definer. This is what made
`EDS Detector Configuration` and `Imaging and Diffraction Detectors` wrong: they were marked
`defines: channel` during the retrofit specifically to satisfy the old invariant 4, which was solving the
symptom. Rules 8 and 9 fields are exempt — they are mandatory for their own declarative purpose.

**Net effect: the in-use vocabulary went from ten keys to six** — `sampling unit`, `reported property`,
`channel`, `analyte`, `standard`, `preparation step`. Retired but still documented: `conversion`,
`acquisition pass`, `background position`, `model component`. That is the invariants doing their job,
forcing out abstractions that never earned their place.

**38 Keyed By cells changed across 16 TAPPs**, plus 4 module fields (`Reported Date Type` in
Geochronology/UPb/ArAr; `Number of Digestion Steps` in SolutionIntroduction). Modules first, recompose,
then TAPP-owned rows — 9 recompositions.

**`Beam Current` — the author challenged the `acquisition pass` assignment and was right to.** The
literature settles it: three of five extractions are scalar, and the two that vary do so **by phase**
(Liu et al. 2016: *"20 nA (olivine, pyroxene, Fe-Ti-Cr oxides); 10 nA (maskelynite…)"*), not by analyte.
Keyed `sampling unit` in the three compositional TAPPs and `(none)` in the two imaging-only ones —
the same treatment `Dwell Time per Pixel` already had.

**Per-TAPP keys were considered and rejected.** The author asked whether keys should simply be specified
TAPP by TAPP. They already are — Column I is per-TAPP — so the question was really whether to keep the
cross-TAPP consistency check. The measurement decided it: of 252 field names appearing in more than one
TAPP, only 3 carry a differing key, so the check is 98.8% free and its value is forcing a reason to be
recorded at the moment of divergence. The register was renamed from "exceptions" to the
**technique-dependent key register**, pruned of `Secondary Reference Materials` (listed speculatively
during the retrofit but never actually divergent), and extended with `Beam Current` and
`Monitored Isotopes` — five entries, each with a rationale now in `precedents.md`.

**Two substring-matching bugs, both caught by dry runs**, both `SEM_FIB`**`SEM_TAPP`** matching a rule
meant for `SEM_TAPP`. Fixed by matching the filename token before `_TAPP` exactly.

**Verification.** `validate_tapp.py --root .` 0 ERROR, 0 WARN, 9 INFO; `compose_tapp.py --check` 50/50
MATCH. All 16 TAPPs integer-bumped with xlsx regenerated (EPMA v12, SEM v9, SEM_Composition v9,
SEM_FIBSEM v8, SEM_Imaging v8, LA-Q v10 +U-Pb, LA-SF v10 +U-Pb, LA-MC v6, LA-MC U-Pb v5, Solution MC v10,
Solution Q v12, Solution SF v12, TEM v12, Lab-XCT v12). Four modules bumped: ArAr 2->3, Geochronology
3->4, SolutionIntroduction 2->3, UPb 3->4.


---

## 2026-08-11 (addendum) — `x` vs `×` reconciled, and a latent regex bug fixed

Surfaced while writing `README_TAPP_for_Schema_Generation.md` for the JSON-schema conversion work.

**The docs and the data disagreed on the cross-product separator.** `conventions.md` and `precedents.md`
rendered it typographically as `A × B` (U+00D7); the CSV cells contain `standard x reported property`
with an ASCII lowercase `x`, and `validate_tapp.py` splits on ASCII. A parser written from the prose
would have failed silently — the whole string would be read as one unknown key name.

**Resolved toward ASCII**, since the data and the code already agreed and only the prose was the
outlier. Eleven notation instances corrected across `conventions.md` (9) and `precedents.md` (2), plus
twelve in the superseded draft so nobody reads the wrong form there. Prose multiplication was left
alone — `µm × µm`, `10× blank SD`, `9.8 × 10⁻⁶`, `Layer 1 × Layer 2 × Layer 3`, `Rule 9 × 16` are all
still the multiplication sign, which is correct. A note now states the separator explicitly in
`conventions.md` 7.3, because the typographically correct character is the natural thing to type.

**A latent bug in the same area, found by testing the regex rather than reading it.**
`KEY_SPLIT_RE` was `\s*(?:>|x)\s*` — with `\s*` (zero or more) around the `x` it splits inside any key
name containing an x: `flux` -> `['flu', '']`, `matrix` -> `['matri', '']`, `xenon` -> `['', 'enon']`.
No key in the current vocabulary contains an inner x, so nothing was broken, but a technique-specific
key declared in a future Phase 0 would have mis-split silently. Tightened to `\s*>\s*|\s+x\s+`, which
requires the cross-product separator to be whitespace-delimited. Verified against both the real key
strings and the pathological cases.

**Verification.** `validate_tapp.py --root .` 0 ERROR, 0 WARN, 9 INFO — unchanged, confirming the
tightened regex still parses all 16 in-use key strings correctly.


---

## 2026-08-11 (addendum 2) — field provenance labels in geochronology variants (Rule 6.11)

**Request:** in system variants such as `LA-Q-ICP-MS_UPb_TAPP`, label the fields that came from the
geochronology modules in the Comments column, so a reader can see where they came from. Documentation
only — not for schema generation or TAPP structure. General-TAPP fields stay unlabelled. Applies to
future variants too.

**Implemented as composition, not annotation.** A module may now declare `source_comment` in its manifest;
`compose_tapp.py` writes that label into Column G for the fields the module contributes. Declared on
`Geochronology` ("Source: Geochronology module"), `UPb` ("Source: U-Pb module") and `ArAr`
("Source: 40Ar/39Ar module"). Deliberately **not** on Group1, ReportingCore, LaserAblation, MCICPMS or
SolutionIntroduction — those are the general TAPP and labelling them would be noise.

**Result: 9 labelled rows per U-Pb variant, 27 library-wide.** Six read `Source: Geochronology module`
(Age Calculation Method, Reported Date Type, Inherited or Initial Signal Correction, Radiogenic Fraction
of Measured Signal, Age Model, Age Datum / Reference Epoch); three read `Source: U-Pb module` (Chemical
Abrasion Conditions, Intermediate Daughter Disequilibrium Correction, Discordance Definition and Values).
The other 13 TAPPs are untouched.

**A Layer 3 module labels only what its blocks insert.** Module_UPb also overlays Column F on six
ReportingCore fields with U-Pb-specific examples — `Calibration Factor and Determination Method`,
`Procedural Blank Level`, `Analysis Inclusion and Rejection Criteria`, `Goodness-of-Fit or Dispersion
Statistic`, `Target Selection Criteria`, `Pre-Analysis Imaging and Screening`. Those stay **unlabelled**:
they are general TAPP fields carrying system-specific examples, not system fields. Worth knowing when
reading a U-Pb variant — U-Pb-specific *content* is not confined to the labelled rows.

**Narrow exception to Rule 6.4**, documented as Rule 6.11. Column G is otherwise consumer-owned;
`stamp_source_comment` only ever fills an **empty** Column G cell, so consumer annotation is never
clobbered and recomposition is idempotent — verified by `--check` returning MATCH 50/50 immediately after
the stamping pass.

**Future variants are automatic.** TIMS x U-Pb and Noble Gas x Ar-Ar (both planned in
`TAPP_Composed_Variants.csv`) will get their labels from composition with nothing to remember. This is
also why it was built into the composer rather than applied as a one-off edit.

**Versions.** Modules: Geochronology 4->5, UPb 4->5, ArAr 3->4. TAPPs: LA-Q U-Pb v10->v11,
LA-SF U-Pb v10->v11, LA-MC U-Pb v5->v6. `validate_tapp.py --root .` 0 ERROR, 0 WARN, 9 INFO.


---

## 2026-08-11 (addendum 3) — Rule 11: Additional Notes is the last field of every TAPP

**Reported:** `Goodness-of-Fit or Dispersion Statistic` was sitting *beneath* `Additional Notes`.

**Cause.** `Module_ReportingCore`'s `aggregation_qc` block used `"placement": "append_to_group"` on Group 6.
Append means end-of-group, and `Additional Notes` was already there — so composition put the statistic
after it, in the 13 TAPPs that compose that block. Purely mechanical; no decision was made.

The contrast inside the same manifest is the tell: ReportingCore's three *Group 5* blocks all use
`insert_before` anchored on `Constants and Reference Values Used`, precisely so they cannot land after
the field Rule 5 requires to stay last. `Additional Notes` never had that protection, because until now
**no rule said it had to be last.** Searched `conventions.md`, `field-review.md` and `SKILL.md` — nothing.

**Group 6 is the right group; the position was wrong.** The field is a QC statistic (MSWD, chi-squared,
dispersion) answering whether a reported aggregate is defensible as a single population.

**Scope decision — one field, not one per group.** The author's reframing is that `Additional Notes` is a
whole-document field, not a Group 6 field. Per-group repetition was considered and rejected on evidence:
across 16 TAPPs x 6 groups, exactly **one** group-local notes field has ever been created
(`Sample Preparation Notes`, one TAPP). Six boxes would also multiply the free-text escape hatch by six —
against the field's own instruction to prefer structured fields — and would leave a note spanning two
groups with no home. A group-local note may still be added where a specific group demonstrably needs one.

**Rule 11 added**, stating the position is the rule: scope is the whole document, and nothing in the row
says so except that nothing follows it. A field appearing after it silently narrows it to "notes about the
things above me".

**Executed**

| | |
|---|---|
| `aggregation_qc` placement | `append_to_group` -> `insert_before`, anchored on `Additional Notes` |
| Descriptions harmonised | 15 TAPPs — three variants were in circulation (12 / 3 split) |
| `Additional Notes` added | `Lab-XCT`, which had never had one (15 of 16 before) |
| Rows physically moved | 13 |
| Validator | new `rule11` check: field present, and last content row of the TAPP |

**Composition updates in place and never relocates.** Recomposing all 16 after the anchor change moved
nothing — `compose_tapp.py` deliberately updates a field already present rather than re-inserting it, so
recomposition does not shuffle files. The new anchor governs future insertions; the 13 existing rows
needed a one-time migration. Worth remembering: changing an anchor does not retro-fix placement.

**Verification.** 16/16 TAPPs now end with `Additional Notes`. `compose_tapp.py --check` 50/50 MATCH;
`validate_tapp.py --root .` 0 ERROR, 0 WARN, 9 INFO. All 16 integer-bumped with xlsx regenerated;
`Module_ReportingCore` v2 -> v3.


---

## 2026-08-11 (correction) — 18 fields wrongly added by an unselected conditional module, reverted

**My error, found while refreshing version numbers in the schema README.** The content-row count had moved
1690 -> 1709, but Rule 11 only explained +1. The other +18 came from the Rule 11 pass, where I recomposed
`ReportingCore` into all 16 consumers as `--module ReportingCore` — with no block selection.

`Module_ReportingCore` is `"conditional": true`. Its blocks are not universal; each carries an
`applies_when` condition and the consuming TAPP selects explicitly. Composing without a selection composes
every block.

**What was wrongly added — every case excluded by the block's own applies_when:**

| TAPP | Added |
|---|---|
| SEM_FIBSEM, SEM_Imaging | Calibration Factor and Determination Method, Procedural Blank Level, Analysis Inclusion and Rejection Criteria, Goodness-of-Fit or Dispersion Statistic (4 each) |
| Solution MC / Q / SF | Target Selection Criteria, Pre-Analysis Imaging and Screening (2 each) — the block says *"Omit for bulk techniques (solution ICP-MS...)"* |
| TEM | Procedural Blank Level — no analytical blank |
| Lab-XCT | Procedural Blank Level, Analysis Inclusion and Rejection Criteria, Goodness-of-Fit or Dispersion Statistic |

**`composed_tapps.json` had the correct selections recorded all along.** I did not read them. The
module-architecture memory warns about exactly this: *"It is hand-maintained — compose_tapp.py neither
writes nor reads it and validate_tapp.py does not check it, so it can drift silently."*

**`compose --check` did not catch it, and that changes how earlier verification in this session should be
read.** It compares cells in rows that exist and does not treat an added row as a difference — it reports
`MATCH` while printing `added (4): [...]` in the same output. Every "50/50 MATCH" cited during this
session was therefore blind to field *additions* from a conditional module. For the six non-conditional
modules the field sets are fixed and present, so MATCH meant what it appeared to mean; the blind spot is
specific to ReportingCore's blocks.

**Fixed**
- 18 rows removed; content rows back to **1691** (1690 + the one legitimate Rule 11 addition).
- Verified field-by-field against the recorded block selections: **0 mismatches across all 16**.
- Backfilled the 6 consumers whose `blocks` were unrecorded (the LA family, all `all`).
- `compose_tapp.py` now **refuses** to compose a `conditional` module without named blocks, and accepts
  `:all` as a deliberate opt-in. Verified: bare `--module ReportingCore` errors; `:target_selection`
  and `:all` both work.
- Recorded as Rule 6.12 in `conventions.md`.

**Corrected in place rather than bumped.** The affected v13/v11/v10/v9 files were created minutes earlier
in the same session and never consumed; a v14 whose only content is "undo the mistake in v13" would add
noise to the version history rather than information.

**Verification after the revert.** `compose_tapp.py --check` using the recorded selections: 50/50 MATCH.
`validate_tapp.py --root .` 0 ERROR, 0 WARN, 9 INFO. 16/16 TAPPs end with `Additional Notes`. All xlsx
regenerated.

---

## 2026-08-12 (later session) — Rule 13, the `analyte` settlement, and a schema-facing sweep

Began as a question about whether `analyte` was still needed as a field and a key, given
element-vs-isotope ambiguity across techniques. It reached past the vocabulary into the record
structure. Full record: `Claude Skills for TAPP/analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md`;
six new `precedents.md` entries carry the reasoning.

**Rule 13 — the analysis record is the session, not one sample.** Group 1 was already session-shaped
(`Analyst`, `Analysis Start Date`, `Analysis End Date`) while Group 2 treated the record as one sample.
`sample` enters the key vocabulary as an anchor — seven in-use keys, not six. `Sample Name` becomes
`defines: sample`, `Sample Persistent Identifier` becomes `sample`, and a new `Session Identifier` was
added to Module_Group1 and composed into all 16. 17 rows nested to `sample > sampling unit`;
`A > B x C` specified in 7.3 for `Counting Statistics Error`. **Rule 10.1** added: a shared session
calibration correlates *samples*, and `Uncertainty Propagation Method` must now separate
session-systematic from per-analysis random components.

**`analyte` settled.** The chemical species determined, at whatever resolution the chemistry is
resolved — never the isotope, unconditionally. Eight contradicting descriptions corrected; all 13
reframed around a shared opening sentence. Three merge proposals rejected (`monitored species`, a
generalised `analyte`, `Target Elements`), all of which collapse into `channel`. `measurand` added to
the VIM3 table and mapped to `reported property`.

**Two literature tests, both decisive.** `channel` is real in the electron-beam TAPPs — Jia et al.
2022 measures Cr on two spectrometers with aggregate intensity counting — so 9 setup fields moved from
`analyte` to `channel` and `WDS Spectrometer Channel` became `defines: channel per analyte`. And
`Mass Resolution per Analyte` → **`Mass Resolution Assignment`**, keyed `channel`, on Misra et al.
2014 acquiring ⁴³Ca in both LR and MR. *Method note:* 14 of 14 pre-existing EPMA extractions said "not
stated" for spectrometer assignment — a null that was an artefact of the corpus holding application
papers rather than method papers.

**The channel↔analyte binding is now explicit in all 13 TAPPs that declare both domains**, after
`Collector Configuration` moved to `defines: channel per analyte` (Module_MCICPMS v5). 7.3.1 amended:
the parent key is **optional per row** — interference monitors and internal standards are channels
with no analyte — with a do/don't table for schema generators.

**Four new validator checks**, each regression-tested against the defect that motivated it: the
definer shared-stem check (7.4a corollary), key divergence across field-name *variants*,
module-manifest-vs-register version drift, and content-hash rather than size comparison in both
`check_current_tapps` and `sync_current_tapps.py`. The last two each found a real pre-existing
problem — `Module_MCICPMS` at v3 against a register claiming v4, and a regenerated xlsx that was
byte-identical in size but not content.

**Housekeeping.** 45 dangling cross-references cleared (descriptions naming sibling fields absent from
the consuming TAPP); Module_ReportingCore v6. Lab-XCT: the resolution fields re-extracted against all
ten source PDFs, `Minimum Resolvable Feature Size` retired as redundant with `Partial Volume Effect
Criteria`, `Spatial Resolution` → `Effective Spatial Resolution (PSF/MTF)`.

**A4 remains partly open by design** — four Group 2 fields were tested against the literature and none
re-keyed, because the variation visible in the extractions is across *procedures*, not across samples.

**Verification.** All 16 TAPPs bumped and re-registered; `recompose_all --check` 16 MATCH;
`validate_tapp.py` 0 ERROR / 0 WARN / 89 INFO; `Current TAPPs/` sha256-verified against source;
installed skill copy in sync (26 files).

**Also updated in this pass, after they were found stale:** `README_TAPP_for_Schema_Generation.md`
(§1 analysis-is-a-session, §2 version-free file table, §4 the whole key section, §10 seven universal
fields, §12 Rules 1–13), `SKILL.md` (Rule 13 invariant; `sample` added to the key list in mistake #5),
and a stale deferral in `conventions.md` 7.12 naming the now-retired Lab-XCT field.

---

## 2026-08-14 — module architecture rebuilt in response to the schema developer's upstream requests

**Trigger.** The JSON-schema developer filed `upstream-requests.md`: 83 LA fields in no module, seven
near-universal fields in no module, one orphan field, and delivery-mechanics questions. Every count
they reported reproduced exactly against the live library. Their one methodological gap was that the
precondition test covered Columns C/D/E/I but **not B** — which Rule 6.4 makes module-owned, and
which is the founding evidence for Rule 6 existing at all. Testing Column B changed the answer: of
their seven "structurally identical" fields, only three had identical descriptions. The three clean
ones were exactly those governed by an explicit universal rule (5, 8, 11); the four divergent ones
had no rule. **A rule enforces by discipline; a module enforces by construction** — which is the
argument for the whole day's work.

### What changed

| | before | after |
|---|---|---|
| modules | 8 | **12** |
| module × consumer pairs | 50 | **99** |
| conditional modules | 1 (`ReportingCore`) | **0** |
| Column G populated rows | 27 | **767 of 1706 (45%)** |
| lint | 0 ERROR / 0 WARN | 0 ERROR / 0 WARN |

1. **Five field definitions reconciled** — `Acquisition Software` (8 variants), `Data Reduction
   Software` (7), `Analytical Mode` (6), `Target Material` (7), plus the `Sample Persistent
   Identifier` tier split. 63 Column B rewrites. Record:
   `Archive/Worksheets (reconciled)/ModuleCore_Reconciliation_Decisions.csv`.
2. **`Data Reduction Software` → `Data Processing Software(s)`.** Group 5 is already named "Data
   Processing"; TEM had stretched "reduction" to cover image processing; Lab-XCT refused the name
   outright. Not every technique *reduces* data — XCT reconstruction expands it. Lab-XCT's
   `Segmentation and Analysis Software` was absorbed into it (→16/16); `Reconstruction Software` was
   **retained** as technique-specific, being a stage the other fifteen lack and one reported in 12 of
   16 XCT papers.
3. **`Module_Group1` retired into `Module_Core`** — its 18 fields plus the universals that belonged to
   no module. Multi-block, not `replace_group`: the new fields sit in Groups 2–6, where
   `replace_group` would drop every technique-specific field. Group 1 order is now enforced by
   `validate_tapp.py` (`group1-order`, `group1-coupling`), which was always the stronger check.
4. **`ReportingCore` dissolved** into `TargetSelection`, `CalibrationFactor`, `Blank`, `Aggregation`.
   It was the only conditional module and the only one not all-or-nothing: 9 of 16 consumers held all
   six fields, and its five blocks had **four different consumer footprints** — four independent
   modules sharing a file, bound by shared provenance rather than structure.
5. **`Module_Analyte`** extracted (1 field, 13 consumers). Its build guard **refused first**: `Analyte`
   had 4 unreconciled description variants. Reconciled, then composed.
6. **Instrument field split** — `Instrument Manufacturer` (Controlled list) + `Instrument Model`.
   Six TAPPs already had the pair; ten carried one combined field under three names. Split rather
   than merged because Manufacturer as a controlled list is a **discovery facet** that free-text
   make-and-model cannot support.
7. **Column G provenance labels extended to all modules** (Rule 6.11). Supersedes the recorded
   decision not to label the general modules "because it would be noise" — written when 8 modules
   existed, 3 of them geochronology-specific. At 12 modules a reader could not tell what came from
   where.
8. **Register-writing tooling built.** `compose_tapp.py` now writes `composed_tapps.json` *and*
   `TAPP_Composed_Variants.csv`; `build_module_register.py` generates `TAPP_Module_Register.csv`.
   Closes most of Rule 6.9's "provenance is recorded but not enforced".

### Rule changes

- **6.10 condition 2 amended**: "five or more fields" → "**ten or more placements**" (fields ×
  consumers). Not a new number — the same calibration point restated so it scales with consumer
  count. Does not reopen past decisions: the two residues 6.9 declined score 3 and 6 placements.
- **6.15 added — the sub-module test.** Every proposed module is tested against the existing ones:
  footprint (mechanical) nominates, subject (judgment) decides, merge unless the subject test
  separates them. Recorded in each manifest as `sub_module_test`.
- **6.12 marked retired**, kept as the record of the 2026-08-11 over-composition incident. The
  `conditional` guard in `compose_tapp.py` was **deliberately kept** despite the plan to remove it:
  it fires only on `"conditional": true`, of which there are now none, so it costs nothing and makes
  reintroduction a deliberate act.

### Findings worth keeping

- **The six LA tables are not one instance.** They descend from one 2026-08-11 split, but Phase 3 ran
  independently: LA-Q has 6 literature procedures, LA-SF has 7, **fully disjoint**, and 58 of the 73
  candidate fields (79%) are attested in both. That clears Rule 6.10's "prefer three to two".
- **Description identity is a lineage artefact.** 72/73 within LA; **11/48** once the independent
  Solution TAPPs are added. Reconciliation cost lives at the lineage boundary.
- **Reconcile before composing, never after.** Every module built today composed as a **no-op**
  (`--check` MATCH), so each shipped at v1 with no consumer churn. Doing it the other way would have
  re-versioned 16 TAPPs per reconciliation round.
- **Co-extension is not coherence.** `Analyte` and `Aggregation` have identical 13-TAPP footprints and
  are still separate modules. Recorded as Rule 6.15's worked example.
- **A check that stops running looks exactly like a check that passes.** Retiring `Module_Group1` made
  `check_group1_template()` fall back to a non-existent path and skip silently. It now takes a
  `restrict` argument; without it, 160 false findings (10 universals × 16 TAPPs).

### Open

- Solution ICP-MS TAPPs appear to be **missing ICP-MS fields the LA TAPPs carry** — `ICP Tuning`,
  `Instrument Warm-up / Session Duration Limit`, `Ion Counter Dead Time`, `Sensitivity as Useful
  Yield`, `Plasma / Make-up Gas Addition`. Same underlying instrument, so probably a gap rather than a
  real difference. **Needs a literature assessment, and must precede the ICP-MS module extraction** —
  a module built from the six LA tables alone would silently ratify the gap.
- Solution MC-ICP-MS still has **0 literature columns**.
- The ICP-MS-scoped module (62 fields still unmoduled across all six LA tables) is **not** the same as
  `Module_LaserAblation`, which is the laser front end. Only ~16 of the 62 are genuinely LA-only.
- A composed TAPP still makes **no self-declaration** of what built it; the register is the only
  witness. Field removal is still only `--allow-drop`, which cannot distinguish a deliberate
  retirement from an omission.

---

## 2026-08-14 (later) — the twelve unassessed fields, and why "not attested" was the wrong reading

**Trigger.** New fields had accumulated in the Solution TAPPs and needed testing against the
literature. Twelve were blank in **every** literature column of both Solution Q and SF — and the same
twelve in each.

**They had never been asked.** Version history put them at v6→v7 (Rules 5/8 + ReportingCore), v7→v8,
v12→v16 (Rule 13) and v20→v21 (the instrument split); the papers were read in June, before the fields
existed. The reading generalised: **7 of the 12 are blank in all 231 literature columns of all 16
TAPPs.** This was a library-wide backlog, not a Solution defect.

**Six of the twelve were never open to a keep/drop decision** — Rules 3, 5, 8, 9 and 13 mandate them,
on the explicit argument that universal presence distinguishes "deliberately none" from "not asked".
That is exactly the case a field the literature never fills was written for.

**Result: 82 of 132 cells attested, 20 partial, 30 N. All twelve kept.** Findings worth keeping:

- `Analytical Mode`'s two-value list is right and **both values are used** — Makishima 2011 runs
  pseudo-flow-injection, and Lu 2007 runs *both* on two instruments in one paper.
- `Uncertainty Level` earns its place by disagreement: six conventions across eleven procedures, two
  of which (**RPD**, **combined standard uncertainty**) were not in its allowed values.
- `Analysis Inclusion and Rejection Criteria` splits cleanly: every procedure reports the *outcome*
  (n included), **not one** reported an acceptance rule. The field's two halves have very different
  attestation.
- `Goodness-of-Fit or Dispersion Statistic` is 0/11 by definitional mismatch — papers report a
  *calibration* fit statistic (R² > 0.999), which the field as worded excludes and nothing else holds.
- **Literature assessment cannot test an analysis-level identifier field.** `Session Identifier` is
  0/11 and always will be; three procedures nonetheless organise themselves by session in prose.

### The ICP-MS module question, answered by measurement rather than by footprint

79 unmoduled fields across the 9 ICP-MS TAPPs fall into clean exact footprints — 31 fields in all 9,
16 in the 6 LA tables, 7 in 8, 6 in the CRC-bearing 6. Placement counts clear Rule 6.10 easily, so the
binding constraints are coherence and specificity, not size.

**The trap: footprint 9 does not mean "ICP-MS-specific".** All nine descend from one template, so a
field in all nine may be inherited rather than general. **The literature settles it**, because the LA
branch (27 columns) and Solution branch (11) were assessed against disjoint paper sets: **21 of the 31
are attested in both**.

**And a zero must be read carefully.** Splitting blank from `N` reversed six verdicts — six fields
have *never been asked* of the LA literature, so their zeros are artifacts, not evidence.

Recommended and **not yet built**: `Module_CRC` (6 × 6, boundary physical — SF instruments have no
cell) before `Module_ICPMS` (17 × 9). Nine general fields excluded from both: they sit in all 9 only
by accident of build order and are gaps in the other seven TAPPs, not ICP-MS content.
`Blank / Background Correction Method` needs no module at all — it is the procedure-level partner of
`Procedural Blank Level`, which `Module_Blank` already owns.

### Four gap fields added — closing this log's own open item

`ICP Tuning` (attested 6 of 11), `Sensitivity as Useful Yield` → **a new `Instrument Sensitivity`**
(solution work reports cps/ppb, never useful yield), `Instrument Warm-up / Session Duration Limit`,
and `Ion Counter Dead Time` (distinct from the pulse/analog cross-calibration Solution already had).

**`Plasma / Make-up Gas Addition` was not the duplicate it looked like.** The Solution field was
scoped to desolvation only — *"Record 'N/A' if no desolvation system is used"* — while Lu 2007 reports
make-up Ar on a cooled Scott chamber with no desolvator. A description defect, now fixed.

Declined: `Signal Smoothing` (squid/ARIS exist because ablation is pulsed), `Sample Introduction`
(`Module_SolutionIntroduction` is its counterpart), `Multi-Run Sequential Analysis Design`.

---

## 2026-08-14 (later) — `generate_paper_registry.py` found drifted, and repaired

**`lit_assessment.md` instructed adding papers by editing the generator and re-running it. Following
that instruction would have destroyed data.** The script held **21 papers against 55 live**, declared
a single `Solution ICP-MS` column where the register had `Solution Q-ICP-MS` and `Solution SF-ICP-MS`
separately, and lacked `Lab X-ray Computed Tomography (Lab-XCT)` entirely. Re-running it would have
deleted 34 rows and collapsed the Q/SF split.

Rebuilt **from the live CSV**, so generator and register now agree by construction. It gained
`--check` (compare, non-zero exit on difference) and `--apply`; a bare run is a dry run; it refuses to
emit blank cells or non-label values. **`--check` before every use** is now written into
`lit_assessment.md`, replacing the instruction that caused this.

Same silent-failure class as the `_excluded()` directory trap (7.8) and the mirror-exclusion trap
(12.1): **a tool that looks like the maintained route and is not.**

Register also gained `Solution ICP-MS` back (derived from the split pair, so the merged view survives
if the split is ever reversed) and a `Thermal Ionization Mass Spectrometry (TIMS)` column, and the
combined LA column was split into `LA-Q-ICP-MS` / `LA-SF-ICP-MS` after re-reading all eight papers
under it — a clean 4/4. Two corrections found by reading: `Barnes2025` Solution SF N → Detailed,
`Navarro2024` Solution Q N → Detailed.

**Method note, recorded because it nearly wrote false data:** anchor acronym searches. An unanchored
case-insensitive `TEM` matches "sys**tem**" and `SEM` matches "as**sem**blage"; the first technique
scan produced 50–80 phantom hits per paper.

---

## 2026-08-17 — Solution MC-ICP-MS Phase 3, its first

The TAPP had **0 literature columns** since it was built. 12 papers → **14 procedure columns**
(Nowell describes two instruments at two labs; Barnes two labs), **585 of 1694 cells attested**.

Notable: `Constants and Reference Values Used` hits 6 of 13 with citations, better than the 4 of 11 in
Q/SF; `Instrument Sensitivity` is confirmed by seven independent statements, all in V/ppm, nA or
volts and **none** a useful yield; and Pringle & Moynier's *"any ratio outside 2σ was discarded"* was,
at that point, the only explicit rejection rule in 24 solution procedures.

---

## 2026-08-17 — triple-quadrupole platforms register under Q-ICP-MS, decided then re-tested

**Decision.** A TQ instrument registers under the **Q-ICP-MS TAPP**, with the platform named in
`Instrument Model`, its identity in `ICP-MS Type` (whose list already offered `Triple quadrupole`),
and tandem operation in `CRC Configuration`. **TAPP assignment is not instrument identity**: analyser
*family* decides the TAPP, *configuration* is a field value — the same line the library already draws
in making Spot/Transect/Mapping mode flags rather than three TAPPs.

**A reasoning error worth remembering.** Liu 2024's Agilent 8900 was first assigned to LA-Q by
refusing to infer TQ operation from a model number. That inverted the source rule: the label asserts
*single-quadrupole operation*, inferred from **silence**, while the model designation is written down.
Right answer, wrong reason.

**Then the author supplied three TQ papers, and one conclusion changed.** The earlier "residue zero"
against Masuda 2024 was **an artefact of the sample** — Masuda ran KED, never tandem, so the
hypothesis was untested rather than refuted. Against papers that do tandem chemistry the residue is
small but real:

- **`Reaction Product Ion / Mass-Shift Transition`** added (3 Q TAPPs) — five transitions across two
  labs and two reagent gases (`125Te + ¹⁶O → 141TeO`; `(176+82)Hf` NH₃ adducts). `Monitored Masses`
  records the mass measured, not the chemistry that produced it.
- **`CRC Configuration` re-keyed `(none)` → `channel`** — Gil-Diaz runs KED for ¹²⁶Te and O₂
  mass-shift for ¹²⁵Te *in one study*, which a scalar controlled list cannot express.
- **`Monitored Isotopes` → `Monitored Masses`** (8 TAPPs). The field *defines* the channel domain,
  and that domain demonstrably contains molecular products and adducts; a field named "Isotopes"
  invites a curator to prune exactly the members that `Dwell Time per Mass` is keyed by. `Masses` was
  chosen over `Species` because this library uses *species* to define `analyte`.
- **`Collision/Reaction Gas Mixture Ratio`** added once a second, production instance appeared
  (Gil-Diaz's He:H₂ 92:8 alongside Wu's NH₃:He 1:9).

**Generalise: a residue of zero means "no residue in this sample", not "no residue".** State what the
corpus could not have shown.

---

## 2026-08-17 — reconciliation sweep: five split-name pairs closed, two uncertainty fields added

Every pair existed because the LA and Solution lineages were built separately. **None would have
surfaced from reading descriptions; each was settled by comparing what curators had extracted.**

| retired | survives |
|---|---|
| `Make-up Gas Flow Rate`, `Plasma / Make-up Gas Addition` | `Make-up Gas and Flow Rate` (9) |
| `Sensitivity as Useful Yield` | `Instrument Sensitivity` (9) |
| `In-Run Isotope Ratio Reproducibility…` | `Within-Session Analytical Precision…` (9) |
| `Between-Session Reproducibility…` | `Between-Session (Long-Term) Analytical Precision…` (9) |
| `Number of Replicates per Sample` | `Number of Replicates` (8) |
| `Mass Cycles per Replicate` | `Number of Scans per Replicate` (2) |

Method and findings, each recorded in `precedents.md`:

- **Compare extractions, not descriptions.** A description states intent; an extraction states what
  curators actually did. Descriptions had converged for make-up gas while proving nothing.
- **Merging non-synonyms needs stronger evidence.** Useful yield and cps/ppb are physically different
  quantities; the merge was justified by **13 attestations against 1** — useful yield appears once in
  28 LA PDFs, and the field had come from a Horstwood best-practice *recommendation*, not from
  observed practice. It survives as one permitted expression inside the merged field.
- **When a name and a description disagree, the extractions follow the name.** "In-Run" drew *internal*
  precision into a field defined as within-session; two of its three cells were wrong and were
  corrected from the papers. A curator reads Column A far more often than Column B.
- **A missing field does not leave a hole — it displaces data into the nearest field that will take
  it.** That is why the mis-extractions were invisible: the cells were plausibly filled.

Two fields added to close the level the library lacked:
**`Internal (Within-Measurement) Analytical Precision and Assessment Method`** (9 ICP-MS) and
**`Counting Statistics Error`** extended from the 3 electron-beam TAPPs to all 9 ICP-MS (now 12).
Group 6 now reads as a ladder: predicted → observed-internal → within-session → between-session.
Mittlefehldt 2024 quotes *"theoretical 1σ … ~0.6%"* against observed *"0.6 to 4.0%"* in one sentence,
which is why two fields rather than one.

- **A cross-reference is safe only in the direction of the smaller footprint.** `Counting Statistics
  Error` (12) does not name the internal-precision field (9); the internal-precision field does name
  it. Where footprints are *disjoint*, neither may name the other — `Number of Scans per Replicate`
  and `Number of Cycles per Block` state their boundary generically instead.
- **Adjacency beats separation** for closely related fields, reversing the instinct after the "In-Run"
  finding. Separation is what let the mis-extraction hide.

### Open

- `Module_CRC` and `Module_ICPMS` are **specified but not built**.
- The nine general fields of the ICP-MS analysis are **library gaps in the other seven TAPPs**, not
  ICP-MS content — `Uncertainty Level` most obviously, a candidate for a universal rule in the style
  of Rules 8 and 9.
- `LA-ICP-TQ-MS` remains a **parked** registry column and a deferred planning-table row. To settle it,
  add MS/MS-mode papers to LA-Q / Solution Q and re-measure the residue. Build nothing in advance.
- Solution MC-ICP-MS's Phase 3 covers Groups 1–6 but its Group 2/6 coverage rests on what the PDFs
  carry; several papers place digestion and QC detail in supplementary material.
