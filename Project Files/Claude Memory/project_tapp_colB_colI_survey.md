---
name: project-tapp-colb-coli-survey
description: "Column B vs Column I survey 2026-08-12 — the definer/notation/description findings and what was executed. ⚠ Its headline rule ('the key is the finest axis attested in REPORTED data') was SUPERSEDED 2026-09-01 by Rule 7.12.1; read the correction at the top before applying anything here"
metadata: 
  node_type: memory
  type: project
---

> ### ⚠ Correction, 2026-09-08 — read before applying anything below
>
> This file's **"THE RULE (now a precedent)"** — *a field's key is the finest axis attested in
> **reported data*** — is no longer how a key is decided. **Rule 7.12.1 (2026-09-01)** scoped that
> test to **Phase 3 validation**; whether an axis *may* be a key is decided at Phase 0 on the 7.4a–c
> invariants and nowhere else. **Rule 7.3.2 (2026-08-28)** then settled the conditional case: declare
> the finest key the literature attests, **unconditionally**. The 2026-08-31 sentence *"revisit only
> if reported data itself ever becomes pass-indexed"* was the specific misuse that forced 7.12.1, and
> it was what wrongly kept `acquisition pass` retired — that key is now in use (92 rows).
> **7.12 still binds as a Phase 3 audit**, and the `Detection Limit` case below is still its correct
> worked example; what changed is that it is no longer a design-time gate.
>
> Also closed since this file was written: the **17-field MIXED backlog** (cleared 2026-08-30, the
> register now holds 14 entries all PRINCIPLED), the **Column B uniformity check** it lists as
> deferred (built as Rule 7.8.9), and `Number of Digestion Steps` — named below as a *clean* definer
> — which was the library's last scalar-typed definer and became **`Digestion Step`, `Text (free)`**
> on 2026-09-08. Terminology: `analyte` is **`target species`** since 2026-09-01. Dated findings
> below keep their original wording, per the development log's convention.

**Status: SURVEY COMPLETE AND EXECUTED 2026-08-12.** All decisions taken and applied — see
"What was executed" at the bottom. Rule **7.3.1** and **7.11** in `conventions.md` are the record.
Deliverables in `Claude Skills for TAPP/analysis/`:
`Survey_ColB_ColI_Report_2026-08-12.md` (the report), `Survey_ColI_Findings_2026-08-12.csv` (20
adjudicated findings, 8 classes, 92 rows), plus the two raw sweeps (`AxisA`, `AxisB_definers`).
Scripts (moved 2026-08-12 to `Project Files/Scripts/`): `survey_colB_colI_20260812.py`,
`build_colI_survey_findings_20260812.py`. See [[project_tapp_folder_layout]].

**Trigger.** `Monitored Isotopes` declares `defines: channel` while its description says *"isotope(s)
monitored per analyte element… Analyte-specific field."* — an `analyte` key asserted in prose that
Rule 7.3 notation cannot carry.

**Finding 1 — the definer population is small and half of it is broken.** The library has **70
definer rows under only 8 distinct field names**, so this class was adjudicated exhaustively, not
sampled. **5 of the 8 are affected:** `Monitored Isotopes` (6 rows), `EELS Edges` (1), `Secondary
Reference Materials` (3 of 12), `Collector Configuration` (3, module-owned) all carry an undeclared
second key; `Sampling Unit` (16) describes a self-nesting domain. Clean: `Analyte`,
`Reported Variables and Units`, `Number of Digestion Steps`. Two of the four would **not** have been
found by grepping for `Analyte-Specific` — `EELS Edges` implies the key only through its value
naming convention, `Secondary Reference Materials` only through *"assessed elements"*.

**Finding 2 — three distinct notation gaps, not one.** G1 definer-with-a-key (4 fields, 13 rows) ·
G2 self-nesting domain (`Sampling Unit`, 16 rows) · G3 conditional key (`Integration Time per Cycle`,
`Dwell Time per Mass`, 5 rows — a key that appears only under a stated condition; may be a policy
call, "always declare the finest key", rather than a notation gap).

**Finding 3 — Rule 7.6 swept Column G and never touched Column B.** 46 rows still contain the
retired `Analyte-Specific` label: 19 bare cardinality assertions (7 duplicate the declared key, 12
disagree with it), 5 a **stale cross-reference** — `Analyte` in EPMA/SEM/SEM_Composition/Solution_Q/
Solution_SF still says *"Fields below flagged as Analyte-Specific in the Comments column"*, and those
TAPPs' Comments columns are empty on every row — and 11 legitimate prose.

**Finding 4 — the description asymmetry, the most generalizable result.** Of 252 field names in more
than one TAPP: **5 (2.0%) have divergent Column I** and are individually justified in the
technique-dependent register; **89 (35%) have substantively divergent Column B** (<0.90 similarity).
**Zero of the 89 are module-owned** — `compose_tapp.py --check` guarantees uniformity where a module
owns the row, and nothing looks anywhere else. Column I is checked by 7.8.7; Column B has no
counterpart check. Worst: `Acquisition Software` (8 variants), `Target Material` (7),
`Data Reduction Software` (7), `Analytical Mode` (6), `Analyte` (6).

**Four key adjudications — ALL DECIDED 2026-08-12, listed with the answer:**
1. `Calibration Factor and Determination Method` — declared `(none)` in 14 TAPPs, description says it
   holds the factor whose *strategy* is per-analyte. **MODULE-OWNED in ReportingCore, 16 consumers** —
   one edit settles it library-wide, and a TAPP-level edit would be silently reverted (Rule 6.6).
2. `Detection Limit` / `Detection Limit Method` — description names a different key from Column I in
   **all 12** TAPPs, in both register variants. Hypothesis worth settling as a precedent: for
   concentration-reporting procedures the `analyte` and `reported property` domains are isomorphic.
   Note this is the field Rule 7.3 uses as its own worked example of defines-vs-keyed-by.
3. `Secondary Reference Materials` — not in the register, so one key must serve all 12 TAPPs.
4. `delta or epsilon Value Reference Standard` — 1 row; anchor is per element system.

**Recommended separator for G1: `defines: <domain> per <key-expression>`**, not the `defines: A. B`
first proposed. `per` marks which token is which role, keeps the right-hand side a full Rule 7.3 key
expression (`defines: standard per analyte x reported property` still parses), matches the words the
descriptions already use, and avoids `.` colliding with sentence punctuation. Split on `\s+per\s+`;
no in-use key contains `" per "`. **Rule 7.4a imposes no new burden** — all 24 G1-candidate rows sit
in TAPPs that already declare `defines: analyte`. Alternative to extending the grammar is splitting
the affected fields (no grammar change, and the Oxide Production precedent favors splitting) —
recommended *against* for the three mapping fields where the mapping is the content, *for*
`Collector Configuration`.

**Methodological lesson: a regex sweep cannot answer this question.** 321 raw hits; 19 field names
adjudicated as false positives, almost all one class — **`per X` denoting a rate, unit, count or
schedule, not a key** (`Ablation Duration per Spot`, `Number of Replicates`, `Background Count Time`'s
*"before each ablation"*). The false-positive list is recorded in the findings CSV so a future sweep
does not re-raise them.

---

## What was executed 2026-08-12

**Notation.** `x` kept as-is (user decision — do not revisit without reading 7.3.1). Rule **7.3.1**
adds `defines: <domain> per <single key>`. The compound form `defines: A per B x C` is **refused** by
`validate_tapp.py` (`rule7-compound-definer-key`) and deliberately unspecified: its token order reads
in two directions at once (`per` puts the innermost first, `x` runs outer-to-inner), and neither fix is
worth paying for a form with zero instances. **If it is ever needed, prefer the key-first form
(`per B x C defines: A`) over inverting `x`** — inverting rewrites 42 rows and severs 7.3's
reporting-table rationale.

**Answers applied:** `Calibration Factor and Determination Method` → `reported property` (module
ReportingCore; `analyte` was invalid because Lab-XCT is a consumer and has no analyte anchor — *a
module-owned key must be valid in every consumer*, which is a real constraint on key choice).
`Detection Limit` → keys kept, prose aligned, **isomorphism recorded as a precedent** in
`precedents.md`. `Secondary Reference Materials` → `defines: standard per analyte` in **all 12**
(user chose uniform over the EPMA/SEM-only split I recommended; the 9 isotope descriptions gained a
per-analyte ask worded for isotope work). Description-uniformity check **deferred**.

**G2/G3 resolved without new notation.** G3 conditional keys → **declare the finest key
unconditionally** (`channel` is a superset of per-analyte; `(none)` cannot hold per-channel values at
all). Note this is *not* the A.4 treatment, which is conditional *applicability*, a different question.
G2 nested sampling units → deferred until the fission-track TAPP exists. `Collector Configuration`
cycling → left free text rather than reviving the retired `acquisition pass`.

**Totals:** 113 cells across 14 TAPPs + 4 cells in 2 modules; 81 rows stamped; retired
`Analyte-Specific` label in Column B **46 → 0**. 14 of 16 TAPPs bumped (`SEM_FIBSEM`/`SEM_Imaging`
carry none of the affected fields). Modules ReportingCore 3→4, MCICPMS 3→4. Verified 0 ERROR / 0 WARN
and 16/16 compose MATCH; xlsx regenerated; skill install re-synced.

**Still open, recorded in 7.11:** (1) the LA `Detection Limit` prose says *"Session detection limit"*
while its key declares `sampling unit` — a factual question about what LA procedures report, not
vocabulary; (2) the register rationale for `Primary Calibration Standard Name` says *"reported property
in isotope work"* but the files carry `(none)`; (3) no Column B uniformity check exists.

**Reusable scripts, now in `Project Files/Scripts/`** (moved 2026-08-12, see [[project_tapp_folder_layout]]): `survey_colB_colI_20260812.py`,
`build_colI_survey_findings_20260812.py`, `recompose_all_20260812.py` (recomposes/checks all 16 from
`composed_tapps.json` — generally useful, not specific to this pass), `bump_and_stamp_20260812.py`.

---

## Second pass — keys validated against the literature assessment (Rule 7.12, same day)

**The reusable output is a standing tool + a decision rule.** `Claude Skills for TAPP/scripts/`**`audit_keys_vs_literature.py`** compares every Column I key against the literature assessment
extractions (231 columns, ~17k cells, the 14 TAPPs with Phase 3 coverage) and is **now a Phase 3 step
in conventions Rule 7.12**. It carries an `ADJUDICATED` table of the 2026-08-12 dispositions, so a
re-run reports only genuinely new disagreements — it prints `0 NEW` as of this pass. Reads `TAPP_ROOT`
/ `TAPP_AUDIT_OUT` env vars.

**THE RULE (now a precedent):** a field's key is the **finest axis attested in REPORTED data** — not
one merely computed during data reduction, not one only conceptually possible. It decides in both
directions, which is why it needed naming:
- `Beam Current` **keeps** `sampling unit` — 2 of 13 procedures publish per-phase currents.
- LA `Detection Limit` **loses** it — Navarro 2024 says the LOD "must be calculated for each
  acquisition" then reports "median values for each element"; Chernonozhkin C5 averages all LODs.
  Per-spot LODs surface only as `<LOD` censoring flags. **7 of 7 papers report one LOD per element.**

**Applied (36 cells, 10 TAPPs bumped):** `Detection Limit` LA → `reported property` (**now uniform
across all 12 → LEFT the technique-dependent register**); `Isobaric Interference Corrections Applied`
`channel` → `(none)` (all extractions Boolean; description already said "procedure-level Boolean");
`Secondary Reference Materials` → `defines: standard` in the 9 isotope TAPPs, **reversing the same-day
uniform decision on evidence** (16 extractions are plain RM lists; only EPMA/SEM ask "assessed
elements") → entered the register; `Primary Calibration Standard Name` → `analyte` in LA-SF (Navarro
assigns standards to analyte groups) → register rationale corrected, it had claimed "reported property
in isotope work" which no TAPP ever carried; `Beam Damage Minimization` → `sampling unit` (EPMA).

**Keys the audit CONFIRMED (don't relitigate):** `Beam Current`=`sampling unit`;
`Primary Calibration Standard Name`=`analyte` in EPMA (11 of 15 give one standard per element);
`Detection Limit` in EPMA=`reported property`; `Monitored Isotopes`=`defines: channel per analyte`.

**Two traps that produced confident wrong findings — both recorded in precedents.md:**
1. **Schedule language is not cardinality.** "measured before each ablation", "calculated per
   analysis" say *when*, not how many. `Blank / Background Correction Method` flagged on 22
   extractions is correctly `(none)`.
2. **Read the raw extraction, not the aggregate.** I proposed demoting `Analytical Accuracy and
   Assessment Method` from `standard x reported property` and **withdrew it** — every Solution cell
   references RMs ("% deviation … for geological RMs (BCR-2, AGV-2, JB-2, BR, JB-3)"); my detector
   needed 2 *named* RMs per cell and scored "USGS/GSJ RMs" as scalar. Applying it would also have
   orphaned `Secondary Reference Materials` as a definer under 7.4c. Also fixed: `XRAY_LINE_RE` with
   `re.I` matched "**Ima**ging"/"**Pla**net" → a phantom 120-evidence finding.

**Coverage limits — absence of evidence is not evidence.** The 4 SEM TAPPs' 35 columns are `N/A`
throughout for calibration standards (SEM-EDS is standardless), so their `analyte` key is untested, not
confirmed. `LA-MC-ICPMS_UPb` and `Solution MC-ICP-MS` have **no** lit-assessment columns — no key in
them is validated this way.

---

## Third pass — Column B uniformity check (Rule 7.8.9, same day)

**Built the counterpart to 7.8.7 for descriptions.** `COLB_DIVERGENCE_TRIAGED` in
`validate_tapp.py` freezes the 89 substantively divergent shared field names, each with a triage
verdict; registered ones report INFO (`colb-divergence-<verdict>`), anything **new** reports WARN.
Ships at 0 WARN / 103 INFO. Functionally tested: removing a register entry makes it WARN.

**Triage** (`analysis/Triage_ColB_Uniformity_2026-08-12.csv`, built by
`triage_colB_uniformity_20260812.py`): PRINCIPLED 52 · MIXED 17 · PARAPHRASE 8 · SUPERSET 7 ·
DRIFT 5. **The 37 non-PRINCIPLED are a visible backlog**, countable in every lint run; removing an
entry after harmonising is how it is worked down.

**Two things checked and ruled out — don't re-derive these:**
1. **Spelling is NOT the cause.** Normalising -ise/-ize, centre/center, artefact/artifact leaves
   89 before → 89 after, and **zero** fields differ by spelling alone. (The split is real and
   separately worth fixing: 151 British vs 157 American occurrences library-wide, near even, so
   there is no house style to appeal to.)
2. **0 of the 89 are module-owned** — the module architecture guarantees uniformity where it owns
   the row; every divergence is TAPP-owned.

**Classifier caveat:** the first cut called a field PRINCIPLED whenever one variant carried a
technique term the others lacked — badly over-classified (`Sample Name`'s 4 variants are one
sentence with a noun swapped: "sample mount", "TEM section"). Fixed by **stripping technique
markers before comparing content**. **Treat the 52 PRINCIPLED as a heuristic verdict, not an
adjudication** — unreviewed, not cleared.

**Repeated my own trap again:** I nearly reported `Sample Name` as having a truncated description
(`"...the sample analysed,"`) — that was my own print statement cutting at 220 chars. Full text was
145 chars and fine. **Print full field text when adjudicating, or check the length.**

**HARMONISATION APPLIED (fourth pass, same day).** The 20 SUPERSET+PARAPHRASE+DRIFT fields were
harmonised — `patch_colB_harmonise_20260812.py`, **71 rows across all 16 TAPPs**, every TAPP bumped.
**18 of 20 became fully uniform and left the register: 89 → 71 entries, backlog 37 → 17 (MIXED only).**
Two kept a shared body + legitimately technique-specific tail and were **reclassified PRINCIPLED**:
`Oxide Production Method and Threshold` (mis-triaged as DRIFT — the oxide proxy really is
technique-specific: ThO+/Th+ in LA, CeO+/Ce+ in solution) and `EDS Dead Time` (EPMA/SEM cross-ref
`WDS Dead Time Correction`, which TEM lacks). A third, `EDS Spectral Processing Type`, kept TEM's
conditional but rose above 0.90 similarity and fell out of scope — intended, not a miss.

**Two defects only visible in the full text, not in the similarity score:** `E-scan Range` in
Solution_SF carried its closing sentence TWICE; `Interference Corrections Applied` said "Common
**EPMA** interferences" and would have been wrong once shared with SEM (generalised — those Kβ/Lα
overlaps are properties of the X-ray lines, not the instrument).

**Harmonisation choices worth reusing:** `Reported Variables and Units` adopted the **canonical Rule
8 wording** already in 10 of 16 TAPPs, aligning the field with the rule that mandates it.
`Instrument Manufacturer` / `Electron Source` had differed only by naming the local instrument ("the
SEM", "the TEM/STEM", "the EPMA") — since each TAPP already declares its technique, "the instrument"
loses nothing. Spelling was NOT normalised library-wide; each target keeps its source variant's
spelling because no house style is decided.

**Still open:** the 17-field MIXED backlog (needs reading variant by variant — some variants are
technique-specific, others merely shorter); `Minimum Resolvable Feature Size` (Lab-XCT) deferred — 5 scalar extractions but
multi-volume scanning may exercise the axis. 6 lit-assessment *cells* still prefix values with the
retired "Analyte-specific:" label (Solution Q/SF); left alone because they are extraction records, and
they happen to confirm their fields' keys. Column B uniformity check (89 divergent names) still
deferred.

See [[project_tapp_keyed_by_rule7]], [[project_tapp_module_architecture]], [[reference_skill_paths]].


## Rule 7.8.11 — `colf-divergence` (2026-08-30)

Column F was the last content column with no cross-TAPP check. **Scoped to controlled-list
types**, because Column F is *normative* on a controlled list (it IS the domain) and merely
*illustrative* on `Text (free)` / `Numeric (...)`: **18 controlled-list fields diverge against
109 of other types**, so an unscoped check would have shipped 127 mostly-correct findings and
been ignored. Compares the member SET, order- and case-insensitive.

**BACKLOG CLEARED 2026-08-31** — all 18 triaged entries closed: **9 harmonised and deleted,
9 PRINCIPLED**. Baseline 23 -> 41 INFO when the check shipped, then down to 31.

Two verdict shapes recurred, and the test that separates them: **a member is principled if it
names a capability, preparation or target the technique does not have.** `EDS Acquisition
Mode`, `Sample Preparation Method` and `Target Material` all kept technique-scoped members
while their shared cores were harmonised; `Sample Preparation Method` needed no edit at all.

**The dominant defect was GRAIN, not missing members.** `Sample Mounting Method` enumerated
vessels, `Pulse/Analog` enumerated correction procedures, `Chromatographic Separation Applied`
enumerated resins (24 attested cells, 24 distinct), `Target Material`'s LA list enumerated
named minerals. All unbounded; all fixed by raising the axis and letting `/ Text` carry the
specifics. **`Coupled Technique(s)` went further and was RETYPED to `Text (free)`** via
Module_Core — 121 cells, 0 bare, a controlled list controlling nothing.

**Second recurring defect: a neighbouring field's value folded into the members.** `FESEM` in
`Instrument Variant` (Electron Source), `fs-` in `Technique` (Laser Pulse Duration), vendor in
`WDS Dead Time Correction` (Instrument Manufacturer), `Iron meteorite` in `Target Material`
(the bulk-specimen axis). And **collisions**: `Not applicable (...)` against `N/A`,
`Not applied` against `None`.

**MY OWN TRIAGE NOTES WERE WRONG TWICE** — `Plasma Thermal Mode` ("different verbosity"; Solution
MC was missing a member outright) and `Diffracting Crystal` ("may be PRINCIPLED"; it was not).
Read the variants before acting on a note.

Originally frozen as: **5 PRINCIPLED** (`Technique`, `Analytical Mode`,
`Matrix Correction Method`, `ICP-MS Type`, `Instrument Manufacturer`) + **12 BACKLOG**
(`Plasma Thermal Mode` harmonised off it the same day — and the triage note was WRONG: it said
"different verbosity", but Solution MC was missing the `Mixed` member outright. **Read the
variants before acting on a triage note.**)
The PRINCIPLED class was needed from day one — `ICP-MS Type` legitimately lists only each
TAPP's own analyser family. Work a BACKLOG entry down by harmonising and DELETING it, never by
reclassifying. See [[project-tapp-datatype-two-type-scheme]].
