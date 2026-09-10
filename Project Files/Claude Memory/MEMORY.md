# Memory Index

## How the library is built
- [TAPP Folder Layout](project_tapp_folder_layout.md) — **Rule 12's `Current TAPPs/` mirror is a COPY, never an editing target**; skill folder stays a direct child of root
- [Git / GitHub Setup](project_git_github_setup.md) — `amds-ldeo/tapp`, branch **master**; `.gitignore` is an **allowlist**; save with `tapp-save.sh`; **never force-push**
- [TAPP Module Architecture (Rule 6)](project_tapp_module_architecture.md) — 14 live modules; **run `check_field_ownership.py` before editing ANY field**, and `compose_tapp.py --check` as a gate
- [TAPP Skill Installation Sync](project_tapp_skill_sync.md) — no auto-sync; **install is fully populated as of 2026-09-10**; `cmp -s` per file, copy only what differs, re-verify
- [TAPP Skill Reference File Locations](reference_skill_paths.md) — project folder is the source of truth; the old "not in the install" claim is **corrected**

## Conventions and rules
- [TAPP "Keyed By" / Rule 7](project_tapp_keyed_by_rule7.md) — Column I, invariants 7.4a–c, **8-key vocabulary**; `acquisition pass` was retired and came back 2026-09-08
- [Column I Survey + Rules 7.3.1 / 7.8.9 / 7.8.11](project_tapp_colB_colI_survey.md) — ⚠ its headline rule was **superseded by 7.12.1**; the Column B/F cross-TAPP checks
- [Target Species Definition](project_tapp_target_species_definition.md) — `target species` (was `analyte`) = the chemical **species**; **an isotope is NEVER one**; search by `reported property`
- [Session/Sample Restructure + Rule 13](project_tapp_session_sample_rule13.md) — the analysis record is the **SESSION**, not one sample; `sample`/`standard` OVERLAP
- [Data Type Two-Type Scheme](project_tapp_datatype_two_type_scheme.md) — **APPLIED**: `Controlled list` = CLOSED, `/ Text` = open; `Boolean` and `Other: specify` retired; **5 measurement artefacts distrust any bare-fraction**
- [Column F Grain & Axis Lessons](project_tapp_colf_grain_lessons.md) — the recurring defect is **wrong GRAIN, not missing members**; then a neighbour's value folded in; then a misdirecting **description**
- [Description/Purpose Split Status](project_tapp_description_purpose_split.md) — **both steps complete library-wide 2026-08-27**; find a backlog by diffing the coverage record, not by re-detecting it
- [TAPP VIM3 Terminology Migration](project_tapp_vim3_terminology.md) — Protocol→Procedure, old Procedure→Measurement; executed 2026-07-24, corrected 2026-07-29
- [TAPP Rule 5 — Constants and Reference Values](project_tapp_rule5_constants_retrofit.md) — universal scope, retrofitted 2026-07-28; 2 pre-existing gaps found, not fixed
- [Literature Attestation Method](project_lit_attestation_method.md) — **split blank from `N` before reading a zero**; disjoint-branch literature beats the common-descent trap

## Per-technique decisions
- [TEM TAPP](project_tem_tapp_phase0.md) — scope, 3 mode flags, seed papers, and the **provenance behind specific field content** (60 kV for organics)
- [SEM TAPP](project_sem_tapp_phase0.md) — scope, 8 mode flags, FIB-SEM as instrument variant; **beam settings vary by PHASE, not element** → `sample > sampling unit`
- [Solution Q-ICP-MS](project_solution_q_icpms_phase0.md) — no mode flags; **CRC mode is not an "Analytical Mode"**, which is why
- [Solution SF-ICP-MS](project_solution_sf_icpms_phase0.md) — no mode flags; mass resolution SPLITS into `Setting` (scalar) + `Assignment` (`channel`, **not target species**)
- [Lab-XCT Resolution Fields](project_labxct_resolution_fields.md) — **9 of 10 XCT papers use "spatial resolution" to mean voxel size** — the field reads near-empty, correctly
- [LA-ICP-MS Lineage](reference_la_icpms_lineage.md) — one lineage; LA-Q/SF split 2026-08-11; `LA-ICP-MS/` is papers-only

## Tooling and outside parties
- [Schema Dev Requests + Module Redesign](project_schema_dev_upstream_requests.md) — the 2026-08-14 reconciliation; register and composition record are GENERATED
- [Paper Registry Generator](project_paper_registry_generator_drift.md) — **not derived from the TAPPs**; a hardcoded table. Run `--check` first
- [TAPP Sentence Segmenter](tapp_sentence_segmenter.md) — `Project Files/Scripts/tapp_segment.py`; 3 bugs fixed 2026-08-27, all found by reading not by its checks
- [Horstwood Geochronology Comparison](project_horstwood_geochron_tapp.md) — **79% of fields are general across Q/SF/MC**: the argument against splitting a technique per instrument
