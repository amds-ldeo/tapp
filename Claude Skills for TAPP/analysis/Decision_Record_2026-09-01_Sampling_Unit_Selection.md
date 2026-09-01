# Decision Record — `Target Selection Criteria` → `Sampling Unit Selection Criteria`

**Date:** 2026-09-01 · **Status:** EXECUTED · **Scope:** 13 TAPPs, 1 module, 2 fields, 26 rows

Normative outcome in `conventions.md` (level-neutral naming, "Target" exceptions). Release script:
`Project Files/Scripts/bump_samplingunitselection_20260901.py`.

---

## 1. The finding: "Target" carried four senses, and only one moved

A sweep of all 16 live TAPPs for `\btargets?\b` returns ~40 field/column pairs. Reading them
separates four distinct senses. **Only sense B was in scope.**

| Sense | Meaning | Where | Disposition |
|---|---|---|---|
| **A** — type-level design intent | what the procedure is *aimed at* | `Target Material` (16/16), `Target Feature(s)` (1) | **Kept.** This is the sanctioned exception in `conventions.md`. |
| **B** — instance-level locus | the portion of *this* sample actually picked out | `Target Selection Criteria` (13); `Pre-Analysis Imaging and Screening` description (13) | **Renamed.** |
| **C** — set-point vs achieved | the value the procedure registers as its target | ~12 fields' prose: `Voxel Size`, `Foil Thickness`, `Double-Spike Mixing Ratio`, `Internal Standard Concentration`, `Carrier Gas and Flow Rate`, `Make-up Gas and Flow Rate`, `ICP Tuning`, `EELS Energy Loss Range`, `EDS Counting Statistics`, `Applicable Sample Dimension Range`, `Exposure Time per Projection`, `Sample Preparation Details` | **Untouched, deliberately.** `conventions.md` bans Default/Target/Achieved in field *names* and routes the target-vs-achieved distinction into Column B. Sweeping these would break a rule, not fix one. |
| **D** — X-ray tube hardware | anode geometry | `X-ray Source Configuration` (description, Purpose, **and Column F controlled values** — "Reflection target, microfocal"), `X-ray Tube Anode Material` | **Untouched.** Standard X-ray terminology; Column F is a controlled vocabulary. |

**The validator had already been bent for sense B.** `TARGET_EXEMPT` in `validate_tapp.py` existed to
let three field names past the ban on "Target"; `Target Selection Criteria` was the only member using
the instance-level sense. Needing an exemption was the signal the name was wrong. The set is now two,
and both survivors are type-level.

## 2. Why this name

`Sampling Unit Selection Criteria` ties the field to the `sampling unit` key, which is exactly the
domain it selects from, and follows the existing `VOI Selection Criteria` pattern (Lab-XCT) of
`<domain> Selection Criteria` with a concrete head noun. No name collision: the library holds
`Sampling Unit` (16, `defines: sampling unit`) and now these two.

**Column I stays `(none)`.** The field holds one set of rules per procedure, not one value per unit.
The new name will tempt a future pass to key it `sampling unit`; it should not be.

## 3. The four decisions

1. **Rename the module too — YES.** `Module_TargetSelection` → `Module_SamplingUnitSelection` (v2 → v3).
   Otherwise Column G stamps 26 rows with a module named for the retired sense.
2. **Lab-XCT `VOI Selection Criteria` overlap — RECORDED, DEFERRED.** Lab-XCT now carries both
   `Sampling Unit Selection Criteria` ("which part of the sample is analysed") and
   `VOI Selection Criteria` ("how the Volume of Interest is defined for quantitative analysis"). In
   XCT the VOI arguably *is* the sampling unit. The rename made a latent overlap visible; it did not
   create it. Settle it against Lab-XCT's declared `Sampling Unit` value in a Phase 4 pass.
3. **`Pre-Analysis Imaging and Screening` — REWORDED.** "select or locate the analysed target" →
   "select or locate the sampling unit to be analysed".
4. **Fold in the Purpose split — WITHDRAWN ON EVIDENCE. See §4.**

## 4. Decision 4 was withdrawn: blank Purpose here is adjudicated, not a backlog

The scoping pass observed that `Module_TargetSelection` was one of only three modules with 0/N Purpose
filled and proposed folding the Description/Purpose split into this rename. **That premise was wrong.**

`precedents.md` (2026-08-27, "Module Step 1 backlog closed") records that *"Step 1 of the
Description/Purpose split is now applied to every row in the library, module-owned and TAPP-owned
alike."* The routing record `analysis/Step1_Routing_ALL_MODULES_2026-08-25.csv` shows all **six**
sentences across the two fields examined individually and routed **D** (Description) under M1/M3.

**Empty Purpose on these rows is the adjudicated outcome.** Inventing Purpose text because the rows
were being rewritten anyway would have manufactured content the split deliberately did not produce.

What survived of decision 4: the closing disambiguation sentence of the renamed field **stays in
Description** (consistent with M3, and with the precedent's own lesson that sentences doing
definitional or scope work stay in Description even when they read as rationale) and was *extended* —
it now distinguishes the field from `Sampling Unit` as well as from `Target Material`, because the
rename makes `Sampling Unit` the nearer neighbour.

## 5. Root cause found: the composition registry drifts silently, and why

Before this pass, **6 of 16 `composed_tapps.json` entries pointed at superseded files** (EPMA v56 vs
live v58; SEM_Composition v54/v56; SEM_FIBSEM v28/v29; SEM_Imaging v27/v28; SEM v55/v57; TEM v45/v47).

Diffed on module-owned columns (A,B,C,D,E,I): **0 diffs, 0 rows added or removed.** No Rule 6.6
violation — the live files were composition-clean and only the registry paths were stale.

**But it was a live hazard, and it was silent twice over.** `compose_tapp.py` writes to the recorded
path, so a recomposition edits the superseded copy, reports MATCH, and leaves the live TAPP untouched.
And `check_library_freshness` derives its "what is current" map from these same paths, so
`doc-stale-version-ref` had quietly begun measuring live documents against a stale baseline.
`recompose_all --check` reported **16 MATCH** throughout while checking the wrong files.

**Root cause: `bump_for_module_20260827.py` sets `generated` but never updates `e["tapp"]`** — it moves
the published file into `Superseded TAPPs/` and leaves the registry naming it. Every bump through that
script advanced the library and left the registry one version behind.

## 6. A field rename cannot be expressed by composition

`compose_tapp.py` matches module rows to TAPP rows by field name, so a renamed module field is **added**
while the old row survives — both end up in the TAPP, and the consumer-owned Column F of the old row is
orphaned. Verified by dry-run `--diff` on Lab-XCT before any write. Column A is therefore renamed in the
new version *before* composing it.

Related: `stamp_source_comment` only ever fills an **empty** Column G (so consumer annotation is never
clobbered and recomposition stays idempotent). The cost is that a module rename orphans every stamp it
has already written — 26 of them here — and recomposition reports MATCH. Column G is patched explicitly.

## 7. What was executed

| | |
|---|---|
| Registry paths reconciled | 6 (before anything else) |
| Module | `Module_TargetSelection` → `Module_SamplingUnitSelection`, v2 → v3 |
| Field | `Target Selection Criteria` → `Sampling Unit Selection Criteria`, 13 TAPPs |
| Column B rewritten | 2 module rows (rename + `Sampling Unit` disambiguation + Pre-Analysis rewording) |
| Column G stamps repaired | 26 (13 TAPPs × 2 fields) |
| TAPPs bumped | 13 (+1 each); 26 files moved to `Superseded TAPPs/2026-09-01/` |
| Cross-references updated | `Module_UPb.csv` (Column F overlay row), `README_TAPP_for_Schema_Generation.md` (17 refs + migration note) |
| Registers | `TAPP_Module_Register.csv` regenerated; `TargetSelection` row hand-set to retired / 0 consumers |
| Docs | `conventions.md` exception list 3 → 2, with both survivors stated as type-level |
| Skill install | whole directory re-synced, verified with `cmp` |

`Module_ArAr` no longer exists, so its former cross-reference needed no action. The 3 Solution TAPPs
do not compose the module (bulk techniques) and were untouched.

## 8. Three guards added, all functionally tested

Documented invariants are not enforced ones, so each was tested by injecting the fault.

| Check | Severity | Fires when | Test |
|---|---|---|---|
| `register-stale-tapp-path` | **ERROR** | a `composed_tapps.json` path is not the live file | reverted one path → 1 ERROR ✓ |
| `register-tapp-absent` / `register-tapp-unregistered` | ERROR / WARN | registry and disk disagree on membership | — |
| `stamp-orphaned-module` | WARN | Column G names a `Source: … module` no manifest declares | injected `Source: Ghost module` → 1 WARN ✓ |
| per-field `RETIRED_FIELD_MENTION_OK` | — | (refinement) exemptions are now per-field, not per-file | added a stray retired name to the README → still caught ✓ |

The last one matters because `README_TAPP_for_Schema_Generation.md` is the live spec handed to the
schema developer; a blanket exemption there would have hidden a genuinely stale field name. It is now
exempt only for `Target Selection Criteria`, which its migration note must name.

**`bump_samplingunitselection_20260901.py` updates the registry paths** — the line the 08-27 script
was missing. Any future bump script must do the same; the ERROR check now catches it if one does not.

## 9. Verification

`recompose_all --check` **16 MATCH / 0 DIFFERS / 0 ERROR** · `validate_tapp.py --root .`
**0 ERROR / 0 WARN / 34 INFO** — byte-identical to the pre-pass baseline · module register up to date ·
`Current TAPPs/` 16 CSV + 16 xlsx, matching live · skill install verified with `cmp`.

## 10. Open

- **Decision 2** — the Lab-XCT `Sampling Unit Selection Criteria` / `VOI Selection Criteria` overlap.
- **Older bump scripts** (`bump_for_module_20260827.py`, `recompose_changed_and_bump_20260827.py`,
  `bump_after_step2_20260825.py`, `bump_and_stamp_20260812.py`) still omit the registry-path update.
  They are dated records and were left as they are; the ERROR check is the safety net. A future bump
  should copy the 2026-09-01 script, not the 2026-08-27 one.
- The wider `Analyte` / `channel` / `reported property` naming question raised by the schema developer
  is untouched by this pass and remains open.
