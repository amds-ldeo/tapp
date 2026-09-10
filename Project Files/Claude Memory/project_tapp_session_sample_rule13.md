---
name: project-tapp-session-sample-rule13
description: "Rule 13 — the analysis record is the SESSION, not one sample; `sample` is now a key anchor; executed across all 16 TAPPs 2026-08-12"
metadata: 
  node_type: memory
  type: project
---

**Status: EXECUTED 2026-08-12.** All 12 steps of the decision record are done, lint 0 ERROR / 0 WARN throughout. Full record with alternatives: `Claude Skills for TAPP/analysis/Decision_Record_2026-08-12_Session_Sample_and_Analyte.md`. Normative text: `conventions.md` **Rule 13** (+ 10.1, 7.2, 7.3, 7.3.1, 6.13). Reasoning and rejected options: five new `precedents.md` entries.

**The decision.** An analysis record corresponds to **one execution of a procedure — a session — which may cover many samples**, each with its own IGSN and possibly its own preparation. `sample` joins the key vocabulary as an anchor, taking the in-use vocabulary from six keys to **seven** (see [[project_tapp_keyed_by_rule7]], whose "six keys" statement is superseded).

**Rule 13 — three mandatory fields in every TAPP:**

| Field | Group | C | D | Keyed By |
|---|---|---|---|---|
| `Sample Name` | 2 | N/A | Basic | `defines: sample` — **the definer** |
| `Sample Persistent Identifier` | 2 | Advanced | Advanced | `sample` |
| `Session Identifier` | 1 | N/A | Basic | `(none)` — the lab's own run/sequence/batch ID |

`Sample Name` is the definer, not the IGSN: 7.4a needs exactly one definer per key and an optional one (C=Advanced) would leave the domain unenumerable in the common case. `Session Identifier` lives in **Module_Group1**, so it reached all 16 TAPPs by recomposition.

**Live key census:** `defines: sample` ×16, `sample` ×32, `sample > sampling unit` ×17, `sample > sampling unit x reported property` ×3.

**Why:** Group 1 was *already* session-shaped in every TAPP — `Analyst`, `Analysis Start Date`, `Analysis End Date`, all C=N/A D=Basic — and a start *and end* date describes a session, not a specimen, while Group 2 treated the record as one sample. That internal contradiction is what the rule resolves. The decisive payoff is **Rule 10.1**: a shared session calibration correlates *samples*, and with no session object that correlation could not be stated at all. `Keyed By` then carries the per-session / per-sample distinction for free — no new column — which is the same argument Rule 7 made against `Analyte-Specific`: one label was hiding four keys, "analysis-level" was hiding two levels.

**How to apply:**
- Ask of every new field whether it is per **session** (`(none)`), per **sample**, or per **sampling unit within a sample** (`sample > sampling unit`). The old habit of treating "analysis-level" as one level is wrong.
- **Preparation attaches to the sample, not the session** — a digestion batch can split across two runs and a run can draw on three batches, so the two groupings are orthogonal. No `preparation batch` key was minted; existing `preparation step` rows are unchanged.
- **`sample` and `standard` OVERLAP — never model them as disjoint.** Secondary RMs run through the same calibration as unknowns, are evaluated against accepted values, and are often SESAR-registered with their own IGSNs, so one physical object legitimately appears in both domains within a session. A schema asserting disjointness will be violated by ordinary sessions. Primary calibration standards are the exception (their values are inputs).
- Two things a JSON-schema consumer must be told, both now written into `conventions.md`: the `per B` half of `defines: A per B` is a **nullable** parent (interference monitors and internal standards have no analyte — see [[project_tapp_target_species_definition]]), and the analyte list comes from the `defines: analyte` field, never inferred from element symbols in the channel list.

**Version state after the retrofit:** every TAPP bumped — EPMA v19, SEM v16, SEM_Composition v16, SEM_FIBSEM v11, SEM_Imaging v11, TEM v17, Lab-XCT v16, LA-MC v12 (+UPb v12), LA-Q v15 (+UPb v16), LA-SF v16 (+UPb v17), Solution MC v15, Solution Q v17, Solution SF v18. Four modules bumped: Group1 v4, LaserAblation v3, SolutionIntroduction v4, ReportingCore v5, MCICPMS v4. **Do not trust these numbers after any later pass — check with `ls`.**

**The same decision record also settles `analyte`**: it is the chemical species, never the isotope, at whatever resolution the chemistry is resolved; `channel` was minted in the three electron-beam TAPPs on multi-spectrometer evidence (Jia et al. 2022); `Mass Resolution per Analyte` became `Mass Resolution Assignment` keyed `channel`.

**Still open (Part E):** orientation as an axis (AMS, velocity anisotropy) fits neither `channel` nor `sampling unit`; XRD phase identity has a claim from `analyte`, `model component` and `reported property` at once; whether physical-property sweeps are archived per-step (checkable against MagIC/PANGAEA); and the matrix-element grey zone. None blocks — all need a technique that has no TAPP yet.

See [[project_tapp_keyed_by_rule7]], [[project_tapp_module_architecture]], [[project_tapp_folder_layout]], [[reference_skill_paths]].
