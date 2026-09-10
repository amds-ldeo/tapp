---
name: project-tapp-datatype-two-type-scheme
description: Data Type vocabulary reduced to two Controlled list forms (closed + / Text); Boolean retired; full reclassification measured 2026-08-30 but NOT yet applied
metadata:
  type: project
---

DECIDED 2026-08-30, **not yet applied to any CSV**. Column E's controlled-list vocabulary
becomes exactly two forms:

- **`Controlled list`** = CLOSED. The enum is the domain. `Other: specify` is REMOVED from
  Column F — the type, not the prose, says whether an unlisted value is allowed.
- **`Controlled list / Text`** = enum plus a legitimately different shape of answer.

`Controlled list (open)` was considered and rejected: it and `/ Text` emit the same
validation shape, and the only property separating them (facetability — see the
`Instrument Manufacturer` rationale in `modules/Module_Core.json`) was judged not worth a
third label. `Boolean` is RETIRED — 7 cells, 3 fields, of which only 1 of 4 attested cells
was a bare Yes/No; all three go to `Controlled list / Text`.

**Why this is a real change, not a relabel.** Bare `Controlled list` is read as closed
everywhere the term is load-bearing, but 178 of 197 library cells carried `Other: specify`
and were open. Fields verdicted "open" must have Column F COMPLETED (their residual
non-bare cells are the missing members), or the closed type is false.

**The measurement caveat that cost two rebuilds.** An automated bare-vs-qualified scan
over the literature columns overcalled `/ Text` badly. Four artefacts, all found by
READING cells, none by the script's own checks:
1. `N (not stated) [P4]` — the not-reported sentinel is written long-form, not just bare `N`
2. `[P4]` provenance tags appended to values
3. `(stated section 3.1)` / `(explicitly stated: "...")` — extraction provenance INSIDE the value
4. a parenthetical that is part of the term (`Field Emission (FEG)`, `Normal plasma (1000 W RF)`)

**FIFTH ARTEFACT, found 2026-08-31: counting `None` / `N/A` as a member match.** Every
controlled list carries `None`, so a field where absence is a common answer scores a high
bare% on nothing at all. `Isotope Dilution Spike` measured 50% bare — all six were `None`,
genuine member matches ZERO — and `Internal Standard Element` 43% the same way. Both would
have been retyped on the metric alone. Exclude `None`/`N/A` before reading a bare-fraction.

**The dominant false positive, and the generalisation worth keeping:** per-analyte /
per-phase assignment (`LIFL (Fe, Mn); TAPL (Mg); PETL (Ca)`) reads as qualification to any
text heuristic, but it is a **Column I `Keyed By` matter, not a Data Type one** —
precedents.md:1722. Three such fields already declare `Keyed By: channel` and were nearly
retyped wrongly. The scan was wrong on **6 of 8** thin-evidence fields for this reason.
Calibrate any future scan against `Technique` / `Analytical Mode` / `Instrument
Manufacturer`, which must land ≥85% bare.

Calibrated results live in the session scratchpad as
`controlled_list_reclassification.csv` (64 evidenced fields). See
[[project-tapp-colB-colI-survey]], [[project-lit-attestation-method]],
[[project-tapp-keyed-by-rule7]].

**Step (a) APPLIED 2026-08-30** — Column F completion for the four closed electron-beam
lists (`Electron Source`, `BSE Detector Type`, `X-ray Background Correction Method`,
`CL Acquisition Mode`), 14 cells, 6 TAPPs bumped: EPMA v42, SEM v41, SEM_Composition v40,
SEM_FIBSEM v24, SEM_Imaging v23, TEM v36. Script
`Project Files/Scripts/complete_colF_electronbeam_20260830.py`. `Other: specify` was KEPT
on purpose — validate_tapp.py:514 still requires it on a plain `Controlled list`, so the
strip must land in the same commit as the validator change. Validator held at
0 ERROR / 0 WARN / 23 INFO.

**Only 5 of 42 closed fields had true vocabulary gaps**, not the 26 the gap detector
flagged. The rest were synonym variance in the literature cells (category b) or answers on
the wrong axis (category c) — `Instrument Variant` collected `FESEM` ×10, which is the
`Electron Source` axis. Three of the five gaps were ONE defect: **a closed list that
enumerates subtypes needs a subtype-unstated member**, or a paper reporting the coarse
answer is forced into `Other:`.

**2026-08-30, after step (a).** `Dwell Time per Pixel` Column F units fixed (EPMA v43,
TEM v37). Category (b) DECLINED — normalising literature cells edits evidence, and no
validator check reads right of the `Literature Assessment` sentinel, so nothing requires
it; take it additively (a canonical column beside the extraction) if ever wanted.
Category (c) turned out EMPTY — every "misfiled" cell had a correctly-filed answer already
in its destination, so there was nothing to move; the `Analytical Mode` autosampler case
was my own gap detector fragmenting a long cell.

That investigation surfaced a **Rule 1 name-variant pair**, now resolved (TEM v38):
TEM's `EDS Quantification Method` -> **`Matrix Correction Method`**, the name EPMA/SEM/
SEM_Composition already used. Perfectly disjoint along the EPMA/SEM <-> TEM boundary;
C/D/E/I already matched, so it was Column A + B only. Column F stays technique-specific
(bulk XPP/PAP/ZAF vs thin-film Cliff-Lorimer/zeta-factor). **The merged field's type is
unresolved**: EPMA/SEM scored closed (100% bare), TEM scored `/ Text` (5 of 7 qualified);
merged ~64%, and `/ Text` is the safer resolution — decide it in the coordinated commit.
`EDS Quantification Method` no longer exists, so the classification is 41 closed / 40
`/ Text`, not 42/40.

**`Other: specify` — settled 2026-08-30.** Strip all 226. The 138 closed cells MUST lose it
(the type says closed, the option says otherwise, and nothing can see the contradiction —
that is exactly how `Technique` drifted open in 13 of 16 TAPPs). The 88 `/ Text` cells lose
it because it is the WRONG PROMPT, not merely redundant: a compound wants a term PLUS
qualification, not "pick something else". The user's reference argument is answered instead
by a **Data Type table on the generated xlsx Legends sheet** — stated once where users read
it, rather than 226 inline repetitions that can drift. Safeguard: close a list only once
verified complete — an incomplete closed list is what produced amds-ldeo/tapp#3's 84
invalid publication cells.

**APPLIED in three commits (2026-08-30).** Commit 1 `d586b25` — 51 retypes, `Boolean`
retired from `VALID_DATA_TYPES`/`_ATOMIC`. Commit 2 `9d526e4` — 213-cell `Other: specify`
strip, 7 `/ Text`→`Controlled list` retypes, `CONTROLLED_LIST_REQUIRED` → `[N/A, None]` plus
a new `CONTROLLED_LIST_FORBIDDEN` check, Data Type table on the xlsx Legends sheet,
conventions.md + precedents.md. All 16 TAPPs bumped. Baseline held 0/0/23 throughout.

Library is now **41 closed fields (160 cells) / 40 `Controlled list / Text` (211 cells)**.

**COMMIT 3 DONE `d1f6f63` — `Technique` closed, `Other: specify` fully retired.** Zero
controlled-list cells in the library carry it. Adjudicated: each list holds the TAPP's OWN
technique, not a menu; `Technique` is PLATFORM-level (attested `SEM-EDS`, `fs-LA-Q-ICP-MS`,
TEM's `STEM; EDS; EELS` name a detector / pulse duration / spectroscopies that other fields
already own); Lab-XCT took the papers' `Lab XCT`; the subtype-unstated member went to LA-Q
only, not LA-SF — **add members on evidence, not for symmetry**. `N/A | None` also left
Technique's lists (Rule 1: semantically empty).

**The validator's two exemptions are NOT the same exemption.** `CONTROLLED_LIST_EXEMPT`
governs the REQUIRED options only; the forbidden-options check has none. Conflating them is
what let Technique drift open in 13 of 16 TAPPs.

SUPERSEDED — was: **Only commit 3 remains: `Technique`.** Its 13 `Other: specify` cells are HELD and it keeps
its `CONTROLLED_LIST_EXEMPT` entry, because three TAPPs' lists omit their own technique
(LA-SF's list has no `LA-SF-ICP-MS` against 14 attested cells; LA-Q likewise; Lab-XCT says
`XCT (laboratory, polychromatic cone-beam)` where papers say `Lab XCT`). Needs Rule 1
cross-TAPP vocabulary adjudication first. Closing an incomplete list is what produced
amds-ldeo/tapp#3's 84 invalid publication cells.

**Verify a new check FIRES, not just that it passes.** The `CONTROLLED_LIST_FORBIDDEN` check
was tested by injecting a violation and confirming the WARN, then restoring.

**Found in passing, not fixed:** 137 cells of NON-controlled-list type still carry
`Other: specify` — 125 `Text (free)` and 12 `Numeric (L/min)` — where it is meaningless. Out
of scope for this pass; worth its own cleanup.

**Open / not done:** Column F completion for the ~19 closable fields; the ~226-cell
`Other: specify` strip; `validate_tapp.py` changes (`VALID_DATA_TYPES`, `_ATOMIC`,
`CONTROLLED_LIST_REQUIRED`:514, `CONTROLLED_LIST_EXEMPT`:520 retires); conventions.md +
precedents.md entries; and the separate `Dwell Time per Pixel` Column F unit fix (EPMA, TEM).
`Technique` Column F is DEFERRED — three TAPPs' lists omit their own technique (LA-SF's
list has no `LA-SF-ICP-MS` against 14 attested cells), but it is a Rule 1 cross-TAPP
vocabulary matter. Category (b) normalisation and (c) misfiled cells are undecided; both
edit literature-assessment cells, i.e. evidence, not schema.


## Adjudication backlog worked down 2026-08-30 (B1–B9)

`f4f062b` B1 — **Rule 7.8.11 `colf-divergence`**, scoped to controlled-list types (18 diverge
vs 109 on other types, where Column F is illustrative). 5 PRINCIPLED + 13 BACKLOG frozen.
Baseline 23 → **41 INFO**.
`2d6afd4` B2 — 137 `Other: specify` cells on `Text (free)`/`Numeric` stripped; forbidden check
made type-universal. **ZERO in the library now.** Finding: the option appeared *only* where
Column F was written as a member list, never on an `e.g.,` list — so **a member list on a
free-text type is a smell**; 43 fields may be mis-typed (open).
`932d751` B3 — `X-ray Background Correction Method` → `channel` (its whole cluster is, incl.
`Background Position(s)`); `Beam Mode` → `sample > sampling unit` (matches `Beam Current`).
`Desolvation System` NOT keyed: its cluster is scalar and its variation spans three axes.
**CORRECTED 2026-08-31 — I wrote that `acquisition pass` merely lacked a definer. It is RETIRED
BY RULE.** 7.4b/c retired it with `conversion`, `background position` and `model component` on
2026-08-11 ("7.4a-c force unused abstractions out of the vocabulary"), and reviving it for
`Collector Configuration` was already declined in writing — "one user does not justify reviving
an abstraction the rule removed". `Desolvation System` is the SECOND declined candidate. It also
fails Rule 7's own test: the key is the finest axis attested in REPORTED DATA, and reported data
is indexed by analyte, never by which pass produced it — Run 1 and Run 2 merge into one table.
**A retired key is not a missing definer.** [[project-tapp-keyed-by-rule7]] already said
"documented but retired from use"; I had the fact and did not apply it.
`f28188d` B4 — no key was lost. `Mass Resolution Setting` `(none)` is correct; the pair is
`Mass Resolution Assignment` keyed **`channel`, not `analyte`** (one analyte can be acquired at
more than one resolution). Added that field to Solution MC, the one sector-field TAPP lacking it.
`3bada95` B7 — `Sample Mounting Method` rebuilt: **the grain was wrong, not the members.** It
enumerated specific vessels (unbounded); now holder classes, with `/ Text` carrying the vessel.
**Mirror of the `Electron Source` fix** — too fine there, too specific here; both look like
"missing members" and neither is fixed by adding any.
`44f2718` B8 — **no new field.** Standardless already lives in `Primary Calibration Standard
Name` (`Oxford factory internal standards`). The *description* was the defect and caused the
scatter. **Second time an "apparent missing field" was an existing one** (after
`EDS Quantification Method` = `Matrix Correction Method`) — CHECK FOR AN EXISTING HOME FIRST.
`3f7279e` B9 — `VP-SEM / ESEM` split (the library already distinguished them in
`Chamber Pressure`); dropped `FIB-SEM dual-beam + VP` as a **combinatorial member** — those do
not survive a split; use the `; ` join instead.

**Recurring lesson across B7/B8/B9: where a run of attested cells lands on the wrong axis or
outside the list, the DESCRIPTION is usually what sent them there.**

ALL CLOSED as of 2026-08-31 — Column F backlog (18/18), free-text typing candidates, both
`Beam Diameter` and `Beam Raster Dimensions` keyed, TEM's `Matrix Correction Method` members
fixed, and `acquisition pass` declined as above.
