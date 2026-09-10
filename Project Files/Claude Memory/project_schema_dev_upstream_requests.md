---
name: project-schema-dev-upstream-requests
description: "Evaluation of the JSON-schema developer's 2026-08-14 upstream requests, and the module-architecture decisions that came out of it"
metadata: 
  node_type: memory
  type: project
---

Schema developer (SMR side) filed `upstream-requests.md` (2026-08-14) asking for more modules.
All their measured counts reproduce exactly against the live library — their tooling reads it
correctly. Their one methodological gap: the identity test covered Columns C/D/E/I but **not B**,
which Rule 6.4 makes module-owned. See [[project-tapp-module-architecture]].

**Key measurements (2026-08-14, re-derive with scripts if the library has moved):**
- The 6 LA tables descend from one 2026-08-11 split, but Phase 3 makes them *not* one instance:
  LA-Q has 6 literature procedures, LA-SF has 7, **fully disjoint**; LA-MC has 1, LA-MC_UPb has 0.
  58 of the 73 candidate fields (79%) are attested independently in both the Q and SF sets.
  That clears Rule 6.10's "prefer three instances to two" — LA-scoped modules are justified.
- Description identity holds *within* LA (72/73) and collapses across lineages (11/48 over the
  9 ICP-MS TAPPs). Reconciliation cost lives at the lineage boundary, not inside LA.
- 9 fields are in all 16 TAPPs with no module. 3 already drifted: `Sample Persistent Identifier`
  (tier, 3 Solution TAPPs), `Target Material` (7 descriptions, 2 data types), `Sample Preparation
  Method`. The clean ones are exactly those governed by an explicit universal rule (R5/R8/R11) —
  **rule-governed fields did not drift; ungoverned ones did.**
- `ReportingCore` is the ONLY module that is not all-or-nothing (9/16 consumers hold all six).
  Its 5 blocks have 4 *different* footprints (13/14/12/13), so it is 4 independent modules in one
  file. Its blocks are invisible in the CSV — they exist only in the JSON manifest, which is why
  the developer (reading only CSVs) misread it as a general reporting module.

**Decisions made (user confirmed):**
1. Retire `Module_Group1`; build `Module_Core` = its 18 fields + the 9 universals, unconditional,
   multi-block by target group. Do the 5 description reconciliations BEFORE composing so it ships
   at v1 (`Acquisition Software`, `Data Processing Software(s)`, `Analytical Mode`,
   `Target Material`, + the `Sample Persistent Identifier` tier split).
2. Rename `Data Reduction Software` → `Data Processing Software(s)`: Group 5 is already named
   "Data Processing", TEM already stretched "reduction" to cover image processing, and Lab-XCT
   refused the name. Not all techniques *reduce* data — XCT reconstruction expands it.
   Lab-XCT: absorb `Segmentation and Analysis Software` into it (that stage produces the reported
   variables); **keep `Reconstruction Software`** as XCT-specific — a stage the other 15 lack,
   substantively reported in 12/16 XCT papers.
3. `Analyte` is composition-only (13/16) so it cannot go in an unconditional module. No composition
   module is possible — only 3 fields have that footprint and 2 are already ReportingCore's.
   It gets its own module. Rule 7 is safe: the 3 non-composition TAPPs have no `defines: analyte`
   AND no field keyed by analyte, so the footprints cannot disagree.
4. **Dissolve `ReportingCore` into 4 all-or-nothing modules** (TargetSelection, CalibrationFactor,
   Blank, Aggregation) + `Analyte`. Retires Rule 6.12, the `conditional` guard at
   `compose_tapp.py:306`, and the README §9 defensive paragraph. Needs Rule 6.10's 5-field
   threshold amended to depend on *consumer count*, not field count.
5. Sequencing: answer §3/§4 → tell dev "one $def per block" → reconcile → `Module_Core` →
   ReportingCore split → LA modules. ICP-MS-wide consolidation deferred until Solution MC-ICP-MS
   has a Phase 3 (it has 0 literature columns).

**EXECUTED 2026-08-14 (steps 1–2 of the sequencing above):**
- Reconciliation applied: 63 Column B rewrites, `Data Reduction Software` → `Data Processing
  Software(s)` (15 TAPPs), Lab-XCT `Segmentation and Analysis Software` absorbed into it (→16/16,
  `Reconstruction Software` retained), `Target Material` Column E and `Sample Persistent Identifier`
  Column D fixed in the 3 Solution TAPPs. **All 16 TAPPs bumped one version.**
- `Module_Core` built at **v1, 28 fields** (not 27 — the absorption promoted `Data Processing
  Software(s)` to universal). 6 blocks, unconditional, all-or-nothing. `Module_Group1` retired to
  `Archive/Superseded Modules/`.
- **Composition was a no-op — `--check` MATCH on all 16.** Reconciling before composing is what
  bought that; the module ships at v1 and no consumer churned. Repeat this order for future modules.
- `Module_Core` uses the **blocks path, never `replace_group`**: replace_group rebuilds its target
  group from the module and would drop every technique-specific field in Groups 2–6. The blocks path
  updates existing fields in place. Group 1 order is enforced by `validate_tapp.py`
  (`group1-order`, `group1-coupling`), not by composition.
- `check_group1_template()` gained a `restrict` argument — Group 1's owner is now `Module_Core.csv`,
  which also holds 10 fields from Groups 2–6; without the restriction it reports 160 false
  `group1-missing` findings (10 × 16).

**ALSO EXECUTED 2026-08-14 (step 3): `ReportingCore` dissolved.** Into `TargetSelection` (2 fields,
13 consumers), `CalibrationFactor` (1, 14), `Blank` (1, 12), `Aggregation` (2, 13 — merges the old
`aggregation` + `aggregation_qc`, which were never independently selectable). All unconditional.
`ReportingCore` archived. **No conditional module remains in the library**, so "one $def per module"
is now true without exception — tell any schema consumer this.
- All 52 new pairs `--check` MATCH; no TAPP file changed, no version moved.
- Consumer sets were derived from actual field presence and independently reproduced every block
  selection the register had recorded — a useful cross-validation to repeat.
- `Module_UPb` and `Module_ArAr` `requires` had to be rewritten (they named ReportingCore).
- **The `conditional` guard in `compose_tapp.py` was KEPT**, deviating from the plan to delete it: it
  fires only on `"conditional": true`, of which there are now none, so it costs nothing and is the
  tripwire making reintroduction deliberate. Rule 6.12 retained as the record of the 2026-08-11
  incident, marked retired.
- Library now: **11 modules, 86 module×consumer pairs** (was 8 and 50), 0 ERROR / 0 WARN.
- Rule 6.15's prong 2 flagged `Geochronology` vs `UPb` as IDENTICAL footprints (both the same 3
  TAPPs) — NOT merged, they differ by layer (2 vs 3) and subject. Good demonstration that footprint
  identity nominates but does not decide.

**`Module_Analyte` BUILT 2026-08-14** (1 field, 13 consumers, v1). Its build guard **refused first**:
`Analyte` had 4 description variants and had never been reconciled (it was outside Core's set). So a
13-TAPP reconciliation + bump ran first, then the module composed as a no-op. Adopted text = the
8-TAPP variant minus its closing cross-reference to `Monitored Isotopes`, which is absent from 5 of
the 13 holders — and losing it costs nothing because `Monitored Isotopes` already states the boundary
from its own side. **Lesson: a uniformity guard in a module-build script is what catches this; keep
one in every future module builder.**

**COLUMN G PROVENANCE LABELS — EXECUTED 2026-08-14.** Rule 6.11 `source_comment` extended from 3
modules to all 12; **767 of 1706 content rows (45%) now name their module**, up from 27. All 16 TAPPs
bumped. Guard in the script asserted Column G was the ONLY column that changed — worth reusing.
- **The label names the OWNER, not the overlayer.** `Age Calculation Method` in a U-Pb variant reads
  `Source: Geochronology module` even though UPb supplied all its Column F examples. A blank Column G
  now MEANS "field belongs to no module" — it is information, not absence.
- Superseded the recorded 6.11 decision not to label general modules ("would be noise") — that was
  written at 8 modules; at 12 the reader can't tell what came from where.
- Caught a gap in the new recorder: `compose_tapp.py` updated `composed_tapps.json` but not
  `TAPP_Composed_Variants.csv`, which the linter flagged at WARN. Recorder now updates **both**.

**"LA-scoped modules" ≠ `Module_LaserAblation`.** LaserAblation is the *laser front end* (fluence,
spot, ablation cell). The ICP-MS back end — RF power, cones, torch, gas flows, interference handling —
was the unbuilt work, correctly scoped to ICP-MS (9 TAPPs) rather than LA (6). **BUILT: it is
`Module_ICPMS`, 39 fields, at v10 as of 2026-08-31.** No Q or SF module was warranted (residues 3 and
6 placements, below the 10 threshold); MC already existed as `Module_MCICPMS`.

**INSTRUMENT FIELDS SPLIT — EXECUTED 2026-08-14** (Ruolin chose split over merge). 6 electron-beam
TAPPs already had `Instrument Manufacturer` + `Instrument Model`; the other 10 carried one combined
field under three names. Split the 10 → **both fields now 16/16 and owned by `Module_Core` v2
(30 fields)**. Split rather than merged because Manufacturer is a `Controlled list` and therefore a
**discovery facet** ("find every procedure on a JEOL"), which free-text make-and-model cannot support.
- The combined field's Column F was already in `Instrument Model` form (`Thermo Scientific iCAP TQ`),
  so the rename carried examples across; only the new Manufacturer row needed a vocabulary.
- `Instrument Model` adopts `Text (free)`: EPMA had `Controlled list`, but a module owns Column E and
  cannot vary it. EPMA's enumeration survives as Column F allowed content.
- **Convention learned:** a `Controlled list` Column F must offer `N/A` and `None` — the linter
  enforces this (`controlled-list-options`). My first vocabularies omitted them, 10 WARNs.

**ALSO OPEN:** Solution ICP-MS TAPPs may genuinely lack ICP-MS fields the LA TAPPs have (`ICP Tuning`,
`Instrument Warm-up / Session Duration Limit`, `Ion Counter Dead Time`, `Sensitivity as Useful Yield`,
`Plasma / Make-up Gas Addition`) — same underlying instrument, so probably a gap rather than a real
difference. Needs field-by-field triage before the ICP-MS module is built.

**REMAINING:** step 4, the ICP-MS-scoped modules. Library is now 12 modules / **99 pairs** / 0 ERROR-WARN.

**REGISTER-WRITING TOOLING BUILT 2026-08-14** (closes most of Rule 6.9's "provenance is recorded but
not enforced"):
- `compose_tapp.py` now **writes** `composed_tapps.json` when `--out` produces a versioned TAPP inside
  the library. Carries a same-stem entry forward to the new version, preserving `derived_from`/notes.
  `--no-record` opts out. **Two guards**: output outside the library root, or a filename not matching
  `*_TAPP_v<N>.csv`, is not recorded — so composing to scratch while testing can't pollute it.
- `Project Files/Scripts/build_module_register.py` **generates** `TAPP_Module_Register.csv`
  (`--check`/`--apply`). All columns but Status derived. **Retired-module rows are carried through**
  untouched — an archived module has no manifest, and that row IS the retirement record.
- Building it found the gap Rule 6.9 predicted: `Module_Geochronology.json` never had a `layer` key.
  Manifest completed rather than generator taught to guess.
- `Fields` counts **named rows, not introduced fields** — that is what the column has always meant and
  what README §9 publishes; for ArAr/UPb it includes their 12 overlay rows each.
- STILL OPEN: a composed TAPP makes no self-declaration; the register is still the only witness.
  Field removal is still only `--allow-drop`, which cannot distinguish deliberate retirement from
  omission — that is the next gap if topology changes (move/rename/merge/split) become routine.

**Answers already in the library the developer lacked:** §3 (`Error Correlation Between Reported
Quantities` belongs to no module) is settled in Rule 10 — it is in 4 TAPPs including Solution
MC-ICP-MS, which consumes neither geochronology module. §4: `composed_tapps.json` paths resolve
16/16 from the library root; they only fail because the developer received `Current TAPPs/` alone.
`Claude Skills for TAPP/references/modules/` does not exist.

**Renamed 2026-09-01, after the README was sent:** `TargetSelection` -> `SamplingUnitSelection` (v3), field `Target Selection Criteria` -> `Sampling Unit Selection Criteria`. Same 2 fields, same 13 consumers. `README_TAPP_for_Schema_Generation.md` carries a migration note for the developer's existing `$def`. The 2026-08-14 dissolution text above keeps the old name as the record of that pass. See `analysis/Decision_Record_2026-09-01_Sampling_Unit_Selection.md`.
