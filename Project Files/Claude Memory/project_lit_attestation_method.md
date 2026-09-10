---
name: project-lit-attestation-method
description: "Two method rules for reading literature-assessment columns as evidence, established 2026-08-14 during the Solution ICP-MS new-field round"
metadata: 
  node_type: memory
  type: project
---

Full findings: `Claude Skills for TAPP/analysis/Report_Solution_ICPMS_NewFields_and_ICPMS_Module_2026-08-14.md`.

**1. Always split blank from `N` before reading a zero.** A field with 0 attestations means
nothing until you know which. `N` = asked, not stated (real evidence). **Blank = the field
postdates that TAPP's Phase 3 and the zero is an artifact.** On 2026-08-14 this reversed six
verdicts: `Sampler and Skimmer Cone Material`, `Torch Depth`, `Mass Bias Correction Strategy`,
`Uncertainty Level`, `Per-Analyte Calibration Strategy`, `Doubly-Charged Species
Production`/`Monitor` all read "LA doesn't do this" on a naive tally and are in fact never asked
of the LA literature.

**The backlog is library-wide, not Solution-specific.** 7 fields are blank in all 231 literature
columns of all 16 TAPPs — every field added by Rules 5/8/9/13 and the ReportingCore descendants
postdates every Phase 3 except the electron-beam ones. Expect the same 12-field gap in any TAPP
whose Phase 3 predates 2026-07.

**2. Common descent is the footprint trap; disjoint literature is the test.** The 9 ICP-MS TAPPs
all descend from one template, so a field present in all 9 may be technique-general *or* just
inherited. The LA branch (27 columns) and Solution branch (11 columns) were assessed against
**fully disjoint paper sets**, so attestation in both is independent evidence. 21 of 31
candidates clear it. Use this before extracting any module from a single lineage — see
[[project-tapp-module-architecture]] Rule 6.10.

**3. Literature assessment cannot test analysis-level identifier fields.** `Session Identifier`
is 0/11 and always will be — no paper publishes a lab run ID. Three of the 11 procedures
nonetheless *organise by session* in prose. Do not read 0/11 on a C=N/A identifier field as
evidence against it; Rules 3/5/8/9/13 mandate presence precisely because "not asked" and
"deliberately none" must stay distinguishable.

See [[project_solution_q_icpms_phase0]], [[project_solution_sf_icpms_phase0]],
[[project_schema_dev_upstream_requests]].
