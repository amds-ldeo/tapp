---
name: project-tapp-keyed-by-rule7
description: "Rules 7-10 — the Keyed By cardinality column at Column I that replaced the Analyte-Specific label; executed across all 16 TAPPs 2026-08-11. In-use vocabulary is now EIGHT keys (`target species` since 2026-09-01, `acquisition pass` reinstated 2026-09-08)"
metadata: 
  node_type: memory
  type: project
---

**Status: EXECUTED AND RATIFIED 2026-08-11.** Rules 7–10 are in `references/conventions.md`. All 16 TAPPs carry a **`Keyed By` column at Column I**. Final verification: `validate_tapp.py --root .` 0 ERROR / 0 WARN / 9 INFO (recorded tier divergences); `compose_tapp.py --check` 50/50 MATCH.

**What it replaced.** The Column G label `Analyte-Specific` — 150 instances across 45 field names — conflated at least four cardinality keys and missed a fifth. Fewer than half the labelled fields were actually keyed by analyte (22/45); the analyte/channel cluster was 90% D=Read-Only-or-Editable while the reported-property cluster was 82% D=Basic (Fisher exact p = 9.8e-06). The label was coined in EPMA/SEM where analyte ≡ channel ≡ measurand are 1:1 and it cannot break; 53% of its instances were there. Evidence: `Archive/Worksheets (reconciled)/RepeatKey_Audit_Test1-4_2026-08-10.csv` (six tests, 154 rows).

**In-use vocabulary — EIGHT keys as of 2026-09-08** (six when this rule was written): `sampling unit` · `reported property` · `channel` · **`target species`** · `standard` · `preparation step` · **`sample`** (added with Rule 13 — see [[project_tapp_session_sample_rule13]]; the notation also gained `A > B x C`, and `channel` reached the electron-beam TAPPs) · **`acquisition pass`**. Documented but retired from use: `conversion`, `background position`, `model component` — **three, not four**. Notation: `(none)`, `A > B` (containment), `A × B` (cross-product, **first key is the outer domain** — "for each A, one value per B"), `defines: A`, `pair: A`.

**The three declaration invariants (7.4a–c)** are what shrank the vocabulary from ten keys to six, and they are the load-bearing part of the rule:
- **7.4a** every key in use — secondary keys included — must have a field declaring `defines:` it
- **7.4b** exactly one definer per key per TAPP
- **7.4c** a definer needs a consumer; `defines: X` where nothing is keyed by X is a field holding a list, not a definer. Rules 8/9 fields are exempt.

**Rules 8–10.** Rule 8 `Reported Variables and Units` (Group 4, all 16) — enumerates the reported-property domain *and* declares the procedure's scope boundary. Rule 9 `Sampling Unit` (Group 2, all 16). Rule 10 `Error Correlation Between Reported Quantities` (Group 5, restricted to the 4 TAPPs reporting jointly interpreted quantities).

**Technique-dependent key register** (`KEYED_BY_TECHNIQUE_DEPENDENT` in `validate_tapp.py`, rationales in `precedents.md`). *As of 2026-08-12 the five entries are:* `Primary Calibration Standard Name`, `Secondary Reference Materials`, `Dwell Time per Pixel`, `Beam Current`, `Monitored Isotopes` — `Detection Limit` **left** the register when the literature audit made it uniform.

**⚠ Invariant 7.8.7 was documented but NOT implemented until 2026-08-12.** `KEYED_BY_TECHNIQUE_DEPENDENT` was defined and never consumed; `check_cross_tapp` covered only name variants and tier divergence. So every unregistered `Keyed By` divergence passed silently for a day. Now emits `keyed-by-divergence` (WARN) / `keyed-by-divergence-registered` (INFO). It had let through exactly one row (`Beam Damage Minimization`, introduced the same day). **General lesson: a documented invariant is not an enforced one — when a rule says the validator "must enforce" something, grep for the check before trusting a clean lint.** Keys are **uniform across TAPPs by default** — of 252 field names in more than one TAPP, only 3 differ (98.8% uniform), so the cross-TAPP check is nearly free and its value is forcing a *reason* to be recorded at the moment of divergence.

**The Comments column is empty on all rows** across all 16 TAPPs (was ~330 populated). Retained by author decision for future one-off annotation. Mode applicability lives in the mode-flag columns; conditional applicability is stated in Column B with `N/A` as an explicit Column F value (the A.4 treatment). *Correction 2026-08-12: not literally zero — the three composed U-Pb TAPPs carry 27 module provenance stamps (`Source: U-Pb module`). Rule 7.10's "zero rows across all 16 TAPPs" is false as written.*

**Rule 7.6 cleaned Column G only — Column B was never swept, and Rule 7.3's notation had three known gaps.** See [[project_tapp_colB_colI_survey]]: 5 of the 8 definer field names carried an undeclared second key or an inexpressible domain shape, 46 Column B rows carried the retired `Analyte-Specific` label, and 89 of 252 shared field names had divergent descriptions with no check on them. **All three closed since**: 7.3.1 added `defines: A per B`, the label went 46 → 0 on 2026-08-12, and Rule 7.8.9 built the Column B check (its harmonisation backlog closed 2026-08-30).

**How to apply:** before writing any TAPP field, ask what its value repeats over and record that key in Column I. Do **not** reach for `target species` by default — it is the *least* universal of the anchors and is absent entirely from Lab-XCT, Raman and fission track. Phase 0 now declares the key vocabulary alongside the mode set, **including which anchors are absent** — an absent anchor is a finding, not an omission. Sequencing for any change touching modules is forced: edit the module, recompose, then TAPP-owned rows (Rule 6.6).

**Two recurring script traps, both hit twice this session:** filename substring matching (`SEM_FIB`**`SEM_TAPP`** matches a rule written for `SEM_TAPP`) — match the token before `_TAPP` exactly; and editing a module-owned column in a TAPP, which `compose --check` catches as `DIFFERS` and the next recomposition silently overwrites.

See [[project_tapp_module_architecture]], [[reference_la_icpms_lineage]], [[reference_skill_paths]].

**Rule 7.3.2 — conditional keys, decided 2026-08-27.** Where a field is scalar in a simple procedure
and keyed in a complex one, **declare the finest ATTESTED key unconditionally**; no conditional
marker was added to the notation. Reason: under-declaring is *lossy* (a consumer emits a scalar where
the data is a list — the amds-ldeo/tapp#1 defect), over-declaring is merely *verbose* (a simple
procedure gets a one-row keyed table, which is correct). 7.12 still binds — "finest **attested**",
not finest imaginable. Applied to `Primary Calibration Standard Name` -> `analyte` in all 12.
Note the G3 question had already lost its original examples to drift before it was decided: re-read
the register before drafting a policy, not only before applying it.
