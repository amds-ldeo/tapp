# Solution ICP-MS — second-round literature assessment of the new fields, and the ICP-MS module question

2026-08-14. Sources: `Solution_Q-ICP-MS_TAPP_v22`, `Solution_SF-ICP-MS_TAPP_v23`,
`Solution_MC-ICP-MS_TAPP_v21`; the 13 PDFs in the two `Literature assessment` folders;
`Project Files/Registers & Planning/paper_registry.csv`.

Draft extractions:
`Solution Q-ICP-MS/Solution_Q-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv`,
`Solution SF-ICP-MS/Solution_SF-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv`.
Build script with the full source docstring is in the session scratchpad
(`build_newfield_drafts.py`); copy it to `Project Files/Scripts/One-shot (applied)/` when the
drafts are incorporated.

---

## 1. What "the new fields" actually are

Twelve fields are blank in **every** literature assessment column of both TAPPs, and they are
**the same twelve in each**. Version history says why: they postdate the June 2026 Phase 3
extraction.

| Entered at | Fields |
|---|---|
| v6→v7 (Rules 5/8, ReportingCore) | Analytical Mode, Reported Variables and Units*, Calibration Factor and Determination Method, Procedural Blank Level, Analysis Inclusion and Rejection Criteria, Constants and Reference Values Used, Goodness-of-Fit or Dispersion Statistic, Sample Name |
| v7→v8 | Reported Variables and Units, Sampling Unit, Uncertainty Level |
| v12→v16 (Rule 13) | Session Identifier |
| v20→v21 (instrument split) | Instrument Manufacturer |

The papers were read before the fields existed. **Nothing here failed a literature test; nothing
had been asked.**

### This is a library-wide backlog, not a Solution problem

Across all 16 TAPPs and all 231 literature columns:

| Field | attested | N | blank |
|---|---|---|---|
| Session Identifier | 0 | 0 | 231 |
| Sampling Unit | 0 | 0 | 231 |
| Reported Variables and Units | 0 | 0 | 231 |
| Constants and Reference Values Used | 0 | 0 | 231 |
| Calibration Factor and Determination Method | 0 | 0 | 161 |
| Analysis Inclusion and Rejection Criteria | 0 | 0 | 144 |
| Goodness-of-Fit or Dispersion Statistic | 0 | 0 | 144 |
| Procedural Blank Level | 0 | 0 | 123 |
| Uncertainty Level | 0 | 0 | 38 |
| Sample Name | 81 | 136 | 13 |
| Instrument Manufacturer | 158 | 16 | 56 |
| Analytical Mode | 96 | 44 | 91 |

Only the electron-beam TAPPs, whose Phase 3 ran later, carry any data for the last three. The
LA TAPPs have the identical gap — see §4.

---

## 2. Six of the twelve are not open to a keep/drop decision

| Field | Held by | Constraint |
|---|---|---|
| Analytical Mode | Module_Core | **Rule 3** — mandatory in Group 4 of every TAPP |
| Constants and Reference Values Used | Module_Core | **Rule 5** — mandatory, universal, "None" is a valid answer |
| Reported Variables and Units | Module_Core | **Rule 8** — mandatory in Group 4 |
| Sampling Unit | Module_Core | **Rule 9** — mandatory in Group 2 |
| Sample Name, Session Identifier | Module_Core | **Rule 13** — mandatory in every TAPP |
| Instrument Manufacturer | Module_Core v2 | 16/16 by the 2026-08-14 instrument split; a `Controlled list` discovery facet |

Rules 3, 5, 8 and 9 all make the same argument explicitly: **universal presence is itself
informative — it distinguishes "deliberately none" from "not asked."** A field that the
literature never fills is exactly the case those rules were written to cover. For these six the
assessment can only populate cells and sharpen Column F; it cannot remove the field.

The other six sit in `Module_CalibrationFactor` (14 consumers), `Module_Blank` (12),
`Module_Aggregation` (13 × 2) and — for `Uncertainty Level` alone — **no module at all**
(Column G is blank, which since 2026-08-14 is information, not absence). Dropping any of the
five module-owned ones means removing a consumer from a module, not editing a TAPP.

---

## 3. Extraction result — 11 procedures × 12 fields

5 Q columns (Hu+Gao 2008, Yu 2005, Makishima 2011, Long 2025, Lu 2007) and 6 SF columns
(Desem 2022, Li 2016, Lu 2007, Milne 2010, Misra 2014, Willbold 2005). **82 of 132 cells
attested, 20 partial, 30 N.**

| Field | Q (n=5) | SF (n=6) | Verdict |
|---|---|---|---|
| Instrument Manufacturer | 5 | 6 | **KEEP** — 11/11 |
| Analytical Mode | 5 | 6 | **KEEP** — 11/11, and both list values are attested |
| Sample Name | 4+1p | 6 | **KEEP** — 11/11 |
| Sampling Unit | 4 | 6 | **KEEP** — 10/11 |
| Reported Variables and Units | 4+1p | 6 | **KEEP** — 11/11 |
| Uncertainty Level | 4 | 6 | **KEEP** — 10/11 |
| Procedural Blank Level | 4 | 5+1p | **KEEP** — 10/11 |
| Calibration Factor and Determination Method | 3+2p | 4+2p | **KEEP** — 11/11 |
| Constants and Reference Values Used | 2+1p | 2+2p | **KEEP** — 7/11, and Rule 5 anyway |
| Analysis Inclusion and Rejection Criteria | 0+4p | 0+6p | **KEEP, revise wording** — 10/11 partial |
| Session Identifier | 0 | 0 | **KEEP** — untestable by this method, see below |
| Goodness-of-Fit or Dispersion Statistic | 0 | 0 | **KEEP but flag** — see below |

### Findings worth acting on

**`Analytical Mode` — the two-value list is right, and both values are used.** Makishima 2011
states *"The pseudo-flow injection (FI) sample introduction technique … was employed"*, and Lu
2007 runs **both** modes on two instruments in one paper: `pseudo-FI` on the ICP-QMS and
*"Middle resolution 50 s with 30 scans (continuous nebulization)"* on the ICP-SFMS. Milne 2010
marks the boundary from the other side — its flow-injection manifold is *offline*
pre-concentration, since *"[this] prevented the online coupling of the flow injection system
directly to an ICP-MS"*. That distinction should go into Column F.

**`Uncertainty Level` earns its place by disagreement, not by presence.** The 11 procedures use
at least six conventions: RSD% (Hu, Yu, Makishima, Lu, Willbold), 1SD (Li, Milne), 2SD *and*
2SE in the same procedure (Desem), 2σ (Misra), 95% confidence limit (Milne, Table 6), RPD
(Makishima), and "combined standard uncertainty" (Willbold). **RPD and combined standard
uncertainty are not in Column F's allowed list** — add them, or the field forces a wrong answer.

**`Analysis Inclusion and Rejection Criteria` — one half of the field is universal, the other
half is never stated.** All 10 non-empty cells are partial in the same way: every procedure
reports the *outcome* (n included per aggregate — Desem n = 39/13/11/9, Yu n = 120/88/32/70/50,
Willbold "five independent analyses … triplicate determinations were performed for each
digestion"), and **not one** states an acceptance or rejection *rule*, or an
acquired-versus-included count. The field's own description says the two are combined "because
neither is interpretable without the other". That is a defensible design, but registrants will
answer half of it; the description should say the outcome is the mandatory half and the criteria
are recorded where the procedure defines them.

**`Constants and Reference Values Used` is sparse but load-bearing where it appears.** Willbold
2005 is the model answer: relative atomic masses from Loss (2003), natural isotopic abundances
from Rosman and Taylor (1998) at <0.2% uncertainty — and it *quantifies why the field exists*,
showing that choosing between two published Pb reference compositions changes the reported Pb
concentration by 0.4% (2.13 vs 2.14 µg g⁻¹). Makishima 2011 gives `113In/115In = 0.0448 (Rosman
and Taylor 1998)`; Desem 2022 gives `205Tl/203Tl = 2.3871 (Woodhead 2002)`; Yu 2005 gives the Li
and B abundance-derived correction factors 0.9983 and 0.9968–0.9971. Four clean hits in 11 is
low, but every one is exactly the failure mode Rule 5 was written for. **Use these as Column F
examples — the current example is a U-Pb decay constant, which reads as inapplicable to a
solution trace-element registrant and probably explains under-reporting.**

**`Session Identifier` is 0/11, and cannot be otherwise.** It is C=N/A, D=Basic — the
laboratory's own run identifier, which no paper publishes. Three procedures nonetheless
*organise themselves by session*: Desem *"A typical session comprised analyses of up to 50
unknowns and 15 standards"*, Milne *"Each analytical session would begin and end with the
analysis of a series of Mo standards"*, Misra *"a single instrument session"*. The concept is
attested even though the identifier is not. **Literature assessment is not a valid test for
analysis-level identifier fields** — worth stating as a general rule, since three of the twelve
are of this kind.

**`Goodness-of-Fit or Dispersion Statistic` is 0/11, and the reason is a definitional
mismatch.** The field asks for a statistic showing *"whether scatter among the contributing
analyses exceeds what analytical uncertainty alone predicts"* — MSWD-shaped, for defending an
aggregate as one population. Solution ICP-MS papers do report fit statistics, but of the
*calibration*: Yu 2005 *"The calibration curves … are linear and R2 are usually greater than
0.999"*; Desem 2022 *"slopes near 1 (with correlation coefficients of 0.75–0.85)"*; Milne 2010
tabulates standard-addition slopes with SD and %RSD. **Neither is what the field asks for, and
neither currently has a home.** Two options, both defensible: leave the field (it is
`Module_Aggregation`, 13 consumers, and geochronology genuinely needs it) and accept it reads
empty in Solution work; or extend `Calibration Factor and Determination Method`'s Column F to
invite the calibration fit statistic, which is where a registrant would look for it. **I
recommend the second — it costs one Column F edit and captures a quantity three of eleven
procedures report.**

### The paper registry adds nothing here, and that is the correct answer

The registry lists 5 `Detailed` papers for Solution Q and 6 for Solution SF — **exactly the 5
and 6 that are already literature columns.** The three additional Q papers are labelled `Brief`,
and reading them confirms the labels: Robin-Popieul 2012 names *"an Agilent 7500CE quadrupole
ICP-MS system also at ISTerre"* with no operating conditions; John & Adkins 2010 uses Q-ICP-MS
only to *"measure final sample [Fe] before isotope analysis"* on any of three instruments; Wang
2025's solution work is incidental to its LA-ICP-MS. **No new columns are warranted** — adding
one would contradict the registry's own criterion that `Brief` is "not useful as a TAPP source
on its own". Registry unchanged; no new papers assessed, so no new rows.

---

## 4. The ICP-MS module

### 4.1 The footprints are clean

Of 79 unmoduled fields present in ≥2 of the 9 ICP-MS TAPPs, they fall into a small number of
exact footprints:

| Fields | Footprint | Placements |
|---|---|---|
| **31** | all 9 ICP-MS TAPPs, no other TAPP | 279 |
| **16** | the 6 LA tables only | 96 |
| **7** | 8 TAPPs (all but Solution MC) | 56 |
| **6** | the 6 CRC-bearing tables (Q and MC lineages, not SF) | 36 |
| 5 | 12 TAPPs incl. EPMA/SEM — not ICP-MS-scoped | — |
| 2 | LA-SF + Solution SF | 6 |
| 2 | the 3 Solution TAPPs | 6 |

All are far above Rule 6.10's ten-placement floor. **Placement count is not the binding
constraint; coherence (condition 3) and specificity (6.1 condition 2) are.**

### 4.2 The trap: footprint 9 does not mean "ICP-MS-specific"

All nine ICP-MS TAPPs share ancestry. A field in all nine may be there because it belongs to the
instrument, or merely because it was in the template they all descend from — the same
one-instance problem Rule 6.10 warns about. **The literature settles it**, because the two
lineage branches were assessed against fully disjoint paper sets (27 LA columns, 11 Solution
columns).

**21 of the 31 are independently attested in both branches** and are safe on that evidence:

> Internal Standard Element · Internal Standard Approach · Mass Resolution Setting · ICP-MS Type ·
> RF Power · Isobaric Interference Corrections Applied · Memory Effect Mitigation · Interfering
> Species · Interference Correction Method · Oxide Production Method and Threshold · Coolant
> (Plasma) Gas Flow Rate · Detector Configuration · Interface Cone Configuration · Plasma Thermal
> Mode · Auxiliary Gas Flow Rate · Guard Electrode · Analytical Accuracy and Assessment Method ·
> Blank / Background Correction Method · Within-Session Analytical Precision and Assessment
> Method · Analysis Sequence · Calibration Standard Measurement Frequency

**A one-branch zero is often an artifact, not evidence.** Splitting "N" from blank is essential:
six fields have **never been asked** of the LA literature (all cells blank) — `Sampler and
Skimmer Cone Material`, `Torch Depth`, `Mass Bias Correction Strategy`, `Uncertainty Level`,
`Per-Analyte Calibration Strategy`, `Doubly-Charged Species Production`/`Monitor`. The LA TAPPs
carry the **same** post-Phase-3 backlog as the Solution TAPPs. Do not read those as "LA doesn't
do this".

### 4.3 Recommended: build `Module_ICPMS` from the instrument, not from the footprint

Nine of the 31 are general analytical concepts that are ICP-MS-only *by accident of build
order*, and they fail Rule 6.1's specificity test — they are not ICP-MS fields, they are gaps in
the other seven TAPPs:

> Analysis Sequence · Blank / Background Correction Method · Spike / Outlier Filtering Approach ·
> **Uncertainty Level** · Uncertainty Propagation Method · Analytical Accuracy and Assessment
> Method · Limit of Quantification (LOQ) Method · Calibration Standard Measurement Frequency ·
> Instrument Serial Number or Lab Identifier

Every technique quotes an uncertainty convention; EPMA and SEM have no `Uncertainty Level` only
because nobody added one. **Moduling these as ICP-MS would freeze an accidental footprint** and
make the eventual correction the expensive kind (6.10's `Pb*/Pbc` precedent).

`Blank / Background Correction Method` is the sharpest case and needs no new module at all:
it is the **procedure-level partner of `Procedural Blank Level`**, which `Module_Blank` already
owns across 12 consumers. Rule 6.15 prong 1 reads *proposed ⊂ existing → absorption*.
**Recommend: move it into `Module_Blank` after checking the other 3 consumers.**

That leaves a coherent instrument module:

| Block | Fields |
|---|---|
| Plasma and torch | RF Power · Coolant (Plasma) Gas Flow Rate · Auxiliary Gas Flow Rate · Torch Type · Torch Depth · Plasma Thermal Mode · Guard Electrode |
| Interface and analyser | Interface Cone Configuration · Sampler and Skimmer Cone Material · ICP-MS Type · Mass Resolution Setting |
| Interference handling | Interfering Species · Interference Correction Method · Isobaric Interference Corrections Applied · Oxide Production · Oxide Production Method and Threshold · Memory Effect Mitigation |
| Internal standardisation | Internal Standard Element |

**17 fields × 9 consumers = 153 placements.** Unconditional, all-or-nothing, one footprint —
the shape 6.15 asks for.

Deliberately held back:
- **The 8-footprint set** (Detector Configuration, Internal Standard Approach, Monitored
  Isotopes, Doubly-Charged ×2, Within-/Between-Session Precision) is footprint-9-minus-Solution-MC.
  A second module at footprint 8 would fail 6.15 prong 2 — no registrant could tell
  "ICP-MS" from "ICP-MS except MC" by title. Resolve by deciding whether Solution MC genuinely
  lacks them; **that decision needs Solution MC's Phase 3, which does not exist (0 literature
  columns).** The existing deferral stands.
- `Isotope Dilution Data Reduction Method` and `Per-Analyte Calibration Strategy` are attested
  11/11 in Solution and never asked in LA. ID is not ICP-MS-specific — TIMS will need it.
  Record both as `generalisation_candidate` in the manifest rather than moduling them as ICP-MS.
- `Signal Integration Interval Method` / `Signal Integration Time` are attested 27/27 in LA and
  never stated in Solution (asked, all N). They are the ablation-transient fields; keep them out
  until it is clear they mean the same thing in a steady-state solution run.

### 4.4 `Module_CRC` — the cleanest candidate in the library

Six fields, one exact footprint of six TAPPs (LA-Q, LA-Q_UPb, LA-MC, LA-MC_UPb, Solution Q,
Solution MC): `Collision/Reaction Cell (CRC) Configuration`, `Collision Gas Type`, `Collision Gas
Flow Rate`, `Reaction Gas Type`, `Reaction Gas Flow Rate`, `Cell Exit Discrimination Voltage`.
**36 placements.** The SF tables are excluded because sector-field instruments resolve
interferences by mass resolution instead — a real technique boundary, not an accident, which is
what makes the footprint trustworthy. Rule 6.15: overlaps `Module_MCICPMS` without containment
(prong 1 → independent); "collision/reaction cell" and "multi-collector" are plainly
distinguishable subjects (prong 2). **Recommend building it, and before `Module_ICPMS` — it is
smaller, its boundary is physical, and it exercises the same tooling.**

### 4.5 The LA-versus-Solution asymmetry, settled against the literature

The five fields flagged as possibly missing from the Solution TAPPs, judged on the 11 procedures
read this session:

| Field | Verdict |
|---|---|
| **ICP Tuning** | **Genuine gap — add to all 3 Solution TAPPs.** Attested in 6 of 11: Hu 2008 (autolens optimised on a 10 ng/ml multi-element solution, nebuliser gas tuned to keep CeO⁺/Ce⁺ and Ce²⁺/Ce⁺ below 2.5%), Yu 2005 (*"optimized daily using a 10 ppb Mg-In-U standard"*), Li 2016, Desem 2022 (*"tuned to provide ~1000 kcps/ppb Pb_total while maintaining flat-topped peaks"*), Milne 2010, Misra 2014 — which even sets tuning **acceptance criteria** (*"2,500,000 cps/ppb on 115In … were set as operational criteria"*) |
| **Sensitivity as Useful Yield** | **Genuine gap — add.** Attested in 5 of 11: Yu 2005 (*"~40 kHz for 1 ppb 115In at a sample uptake rate of 60 µl/min"*), Makishima 2011 (Table 1, `count pg⁻¹ ml`), Desem 2022, Milne 2010 (*"~5000 cps nM⁻¹"*), Misra 2014 (*"~2.5 × 10⁶ cps/ppb on 115In"*) |
| **Instrument Warm-up / Session Duration Limit** | **Probable gap — add.** Attested in 2 of 11: Hu 2008 (*"flushing through a rock solution for 30 min before tuning the instrument for a run"*), Yu 2005 (*"blanks for all isotopes were stable during a typical run (~5 hr)"*) |
| **Plasma / Make-up Gas Addition** | **Not a gap — a duplicate name.** The Solution TAPPs already carry `Make-up Gas Flow Rate`, and Lu 2007 reports *"Make-up Ar gas flow rate 0.25 l/min"* for the ICP-QMS. Rule 6.1 condition 2: **reconcile the two names before either enters a module** |
| **Ion Counter Dead Time** | **Leave for now.** Not stated in any of the 11; the adjacent `Pulse/Analog Detector Nonlinearity Correction` already exists in Solution Q and SF. Revisit with Solution MC's Phase 3 |

---

## 5. Recommended order of work

1. Review the two draft CSVs; patch the 12 rows into `Solution_Q-ICP-MS` v23 and
   `Solution_SF-ICP-MS` v24.
2. Column F edits that fall out of the assessment: add RPD and combined standard uncertainty to
   `Uncertainty Level`; add a non-geochronological example to `Constants and Reference Values
   Used`; note the offline-FI boundary on `Analytical Mode`; decide the calibration-fit question
   on `Goodness-of-Fit` / `Calibration Factor`.
3. Reword `Analysis Inclusion and Rejection Criteria` so the outcome is the mandatory half.
4. Run `audit_keys_vs_literature.py` — Rule 7.12 makes it a Phase 3 step and the literature
   columns have just changed.
5. Add `ICP Tuning`, `Sensitivity as Useful Yield` and `Instrument Warm-up / Session Duration
   Limit` to the 3 Solution TAPPs; reconcile `Plasma / Make-up Gas Addition` against
   `Make-up Gas Flow Rate`.
6. Build `Module_CRC` (6 × 6).
7. Reconcile descriptions, then build `Module_ICPMS` (17 × 9). Reconcile **before** composing —
   that is what let `Module_Core` ship at v1 as a no-op.
8. Move `Blank / Background Correction Method` into `Module_Blank`.
9. Separately from all of the above: the nine general fields of §4.3 are library gaps in the
   other seven TAPPs, not ICP-MS content. `Uncertainty Level` in particular is a candidate for a
   universal rule in the style of Rules 8 and 9.
