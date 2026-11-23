# Standards domain: a list of standards, and per-role assignments — proposal, for RD review

2026-11-19. Status: **APPLIED 2026-11-23 (revision 2, SMR agreed), with `Reference Value` split into value, uncertainty and basis (RD).** Applied by `Project Files/Scripts/bundle_19_22_23_20261123.py` with #19 and #23; conventions 7.13. Originally: DRAFT, revision 2. Arose from issue #22 (SMR, 2026-10-31).
Revision 1 (D1–D7 and Appendix A, below) was posted to #22 on 2026-11-19. SMR agreed with the gap and
with its three differences, and counter-proposed two tables with the role on the assignment. Revision 2
takes that design and adapts it to the one-value-per-member rule. **Where revision 2 and revision 1
differ, revision 2 holds.** Nothing changes until SMR confirms revision 2 and RD approves.

## Revision 2 (after SMR's reply of 2026-11-19)

### What SMR proposed

- **Table 1, the standards.** One row per standard: name/identifier, the standard's own material,
  citation for the reference values, optionally expected precision and accuracy. Nothing in it says
  what the standard calibrates.
- **Table 2, the assignment.** Keyed `target material x target species` (#6's key), with two columns:
  the standard (a row of table 1) and its role. #6 becomes this table, renamed. #7 and #8 fold into it
  as role values.
- Rows keyed by `standard` can't sit in a module, because on his side a module can't constrain a
  keyed-table column array.
- Add the certified value and its uncertainty.
- One general role vocabulary; per-technique restriction as a SHACL `sh:in` on the technique's shape.

### What we take

- **The role belongs to the assignment, not to the standard.** This is right, and it removes revision
  1's multi-valued `Reference Material Role` (D2). San Carlos olivine is primary for one phase and
  secondary for another: the role describes the pairing, not the material.
- **Table 1 as he describes it**: #1 (definer), #3 Type, #4 Identifier, #5 Reference Value Source.
- **The certified value**, as a new field (R3).
- **One vocabulary**, restricted per technique on his side.
- **The rename of #6** (R2).

### Where it needs adapting

**A. One key cell holds more than one role, so table 2 can't be one field.** Our keys allow one value
per member (7.3.4). In the Solution MC literature, 12 procedures fill both `Primary Calibration
Standard Name` and `delta or epsilon Value Reference Standard`. **In 10 of the 12 they name the same
material for the same species**: Rb: NIST SRM984 as the bracketing standard *and* the zero-delta
reference (Nie & Dauphas 2019; Pringle & Moynier 2017); Fe, Cr, Mg (van Kooten et al. 2026); K, Cu, Zn
(Barnes et al. 2025). In the other two the materials differ: Craddock et al. 2008 brackets with in-house
S solutions and reports against V-CDT; Hopp et al. 2021 brackets with IRMM-524a and reports against
IRMM-014. So one (target material, target species) cell holds a calibration standard and a delta
reference, sometimes the same material and sometimes not, and LA adds a third: Wu et al. 2023 calibrate
Lu and Hf on NIST SRM 610 and correct the matrix with XN02 xenotime. A single field with a role column
would need two values in one cell.

**Resolution: one assignment field per role, each keyed by species, each value naming an entry in
#1.** In his schema these pivot into exactly his table 2, one row per (target material, target
species, role) with the standard as the value. The key of that table is
`target material x target species x role`, which is unique, and the role is a column. The TAPP keeps
the roles as separate fields for three reasons, and only the first is about the key:
1. one value per member (above);
2. **the tiers differ by role**: #8 (delta reference) is C=N/A, D=Basic, because the reporting
   reference is chosen per study, while #6 is Basic/Editable. One field can carry one tier pair;
3. **the keys differ by role**: #7 and #8 are keyed by bare `target species`, which SMR's reply
   allows ("unless their key really is bare `target species`"). Interference overlaps and delta scales
   don't depend on the phase; calibration does (McCoy+2025_UA).

**B. Not every role in the vocabulary is a per-species assignment.** Of revision 1's seven:
- `Primary calibration` → #6.
- `Bracketing` → also #6. In sample–standard bracketing the bracketing standard *is* the calibration
  standard (#6's description already says so); the scheme is in `Calibration Standard Measurement
  Frequency` and `Calibration Strategy per Target Species`. A separate role would record one fact
  twice.
- `Interference correction` → #7.
- `Delta or epsilon reference` → #8.
- `Secondary (quality control)` → **a new assignment field, `Quality-Control Standards`** (R4), keyed
  `target material x target species`. Secondaries are matched to phases too: McCoy+2025_SI lists
  carbonate secondaries and magnetite/olivine secondaries separately. Unlike the calibration roles, a
  cell routinely names several materials (Nie & Dauphas list twelve for Rb), so its value is a list of
  entries in #1. That's allowed because the list is one value of one role.
- `Drift monitor` → **dropped as a role.** Drift is monitored by re-running a primary or a secondary;
  it's a use, recorded in `Analysis Sequence` and in the secondary's description, not a separate
  assignment.
- `Matrix correction` → **deferred.** One procedure in 171 (Wu et al. 2023). Until a second one turns
  up, record it in #6's cell (*"Lu, Hf: NIST SRM 610, with XN02 xenotime for the matrix correction"*),
  as the literature cell does now.

So the role vocabulary for his table 2 is four values, each backed by one field: primary calibration
(#6), interference correction (#7), delta or epsilon reference (#8), secondary (R4).

**C. Module placement is a constraint of his generator, not of the TAPPs.** Module ownership is an
authoring device: composition writes every module row into each consuming table, and the 16 delivered
tables carry all of them. Module_CompositionQC already owns `defines: standard`, and Module_ICPMS
already owns three `standard x reported property` fields; both compose without trouble. If his
generator builds per-technique shapes, it builds them from the composed tables, where these rows
already are. Nothing changes on our side.

**D. The certified value is keyed `standard x reported property`, not `standard`.** A standard has one
accepted value per property (Kakanui kaersutite has an SiO2, an Al2O3, a MgO…), so the value can't sit
in table 1 as one cell. `Constants and Reference Values Used` explicitly leaves reference-material
values to the standards fields, and none of them asks for the value today, so the gap is real.

**E. Expected precision and accuracy stay in #9–#13**, keyed `standard x reported property`, as SMR
also says elsewhere in his reply. They are per property, so they can't be one cell of table 1 either.

### Decisions for RD (revision 2)

**R1. Table 1 as revision 1 drafted it, minus the role.** `Reference Materials` (`defines:
standard`, renamed from `Secondary Reference Materials`), `Reference Material Type`, `Reference
Material Identifier`, `Reference Value Source`, all as in Appendix A. **Drop `Reference Material Role`
(D2).** *Recommended.*

**R2. Rename #6 `Primary Calibration Standard Name` → `Calibration Standard`.** Key unchanged
(`target material x target species`). It matches `Calibration Standard Measurement Frequency`, and
"Name" is wrong once the value is a pointer. *Recommended.*

**R3. Add `Reference Value`, keyed `standard x reported property`.** C=Advanced, D=Editable,
`Text (free)`: the accepted value and its uncertainty, with the uncertainty's basis
(e.g. *"MgO: 12.80 ± 0.12 wt% (2s)"*). The citation stays in `Reference Value Source`. Advanced
because most papers cite a compilation rather than restate its values. *Recommended.*

**R4. Add `Quality-Control Standards`, keyed `target material x target species`.** C=Basic,
D=Editable (the tiers `Secondary Reference Materials` has now), `Text (free)`; the value names one or
more entries in `Reference Materials`. *Recommended.* This is what makes a standard a secondary; the
D7 sentence on #9–#13 then reads *"Reported for the standards named in `Quality-Control Standards`
…"*.

**R5. Keep #7 and #8 as separate fields**, values now naming entries in #1, keys and tiers unchanged.
*Recommended*, for reasons A.2 and A.3.

**R6. Reply to SMR before applying.** He agreed revision 1's direction, so revision 2 needs his
confirmation of three points: one field per role (pivoted on his side), the four-value vocabulary, and
`standard x reported property` for the certified value.

### Revision 2 field table

| # | Field | vs revision 1 | C | D | E | I | Owner (where) |
|---|---|---|---|---|---|---|---|
| 1 | `Reference Materials` | unchanged | Basic | Editable | Text (free) | `defines: standard` | CompositionQC (12) |
| 2 | ~~`Reference Material Role`~~ | **dropped** | | | | | |
| 3 | `Reference Material Type` | unchanged | Advanced | Editable | Text (free) | `standard` | CompositionQC (12) |
| 4 | `Reference Material Identifier` | unchanged | Advanced | Editable | Text (free) | `standard` | CompositionQC (12) |
| 5 | `Reference Value Source` | unchanged | Basic | Editable | Text (free) | `standard` | CompositionQC (12) |
| 5a | `Reference Value` | **new** (R3) | Advanced | Editable | Text (free) | `standard x reported property` | CompositionQC (12) |
| 6 | `Calibration Standard` | **renamed** from `Primary Calibration Standard Name` (R2) | Basic | Editable | Text (free) | `target material x target species` | CompositionQC (12) |
| 6a | `Quality-Control Standards` | **new** (R4) | Basic | Editable | Text (free) | `target material x target species` | CompositionQC (12) |
| 7 | `Interference Correction Standard` | unchanged | Advanced | Read-Only | Text (free) | `target species` | TAPP (EPMA, SEM, SEM_Composition) |
| 8 | `delta or epsilon Value Reference Standard` | unchanged | N/A | Basic | Text (free) | `target species` | TAPP (Solution MC) |
| 9–13 | QC statistics | D7 sentence now names #6a | as now | as now | as now | `standard x reported property` | as now |

**Draft text for the new and changed rows:**

**5a. `Reference Value`**
- B: The accepted value of each reported property for each reference material, with its uncertainty
  and the basis of that uncertainty (for example 2s, or 95% confidence). The source is recorded in
  `Reference Value Source`.
- F: e.g., 12.80 ± 0.12 wt% (2s) | 0.70918 ± 0.00001 (2SE) | 337.13 ± 0.37 Ma (95% CI)
- J: Without the accepted value an accuracy figure can't be recomputed, only read.

**6. `Calibration Standard`**: B as Appendix A #6, plus *"Where the calibration standard is also run
in sample–standard bracketing, it is the bracketing standard; record the scheme in `Calibration
Standard Measurement Frequency`."*

**6a. `Quality-Control Standards`**
- B: The reference material(s) run as unknowns to check the results for each target species in each
  target material, assessing accuracy independently of the calibration and monitoring drift. Name one
  or more entries in `Reference Materials`.
- F: e.g., San Carlos olivine | Kakanui kaersutite, USNM 111312/444 | BHVO-2, BCR-2
- J: Only a material that played no part in the calibration tests its accuracy.

### How a session's measurements reach the standards (unchanged from SMR's reply)

1. **Which standard calibrated a reported value:** the result's (target material, target species)
   joins to #6. Usually a procedure property; a session that deviates edits it (D=Editable).
2. **A measurement of a standard:** the dataset row's target is the entry's identifier in #1.
3. **Precision and accuracy:** #9–#13, keyed `standard x reported property`.
4. **Matrix matching:** compare #3 (the standard's material) with the target material in #6's key.

---

*Revision 1 follows, kept for the record.*

## Revision 1 (posted to #22, 2026-11-19)

### The problem

The `standard` key is defined broadly (conventions 7, key table): *"a reference against which
something is anchored, physical or virtual"*. The domain that key enumerates is narrower:

- **Only `Secondary Reference Materials` defines `standard`** (Module_CompositionQC, 12 TAPPs). So the
  members of the domain are the QC materials and nothing else.
- **Every other standard is a value, not a member.** It is a name written into some other field:

| Field | Owner | Keyed by | Where | What it anchors |
|---|---|---|---|---|
| `Primary Calibration Standard Name` | Module_CompositionQC | `target material x target species` | 12 | concentration, or the bracketing / zero-delta ratio |
| `Interference Correction Standard` | TAPP | `target species` | EPMA, SEM, SEM_Composition | the overlap correction |
| `delta or epsilon Value Reference Standard` | TAPP | `target species` | Solution MC | the delta scale |
| `EDS Calibration Standard(s)` | TAPP | `(none)` | TEM | EDS quantification |

- **Nothing records a standard's role, material or identifier** as a field of its own. Each sits in
  free text, when it is recorded at all.
- **A dataset row that measures a standard has nothing to point to** unless the standard is a
  secondary. Rule 14.5 now says the session's QC values summarise the dataset's analyses of each
  secondary reference material. A primary measured as a bracketing standard, or a delta reference
  run as an unknown, can't be cited the same way.

SMR's ask is a `defines: standard` list of every standard used, each with its role, target, material,
name or identifier, the target species and target materials it serves, a citation for its reference
values, and expected/achieved statistics.

### What the literature shows (171 procedure columns)

| Field | Applies (rows) | Filled | Names a catalogue or registry ID |
|---|---|---|---|
| `Primary Calibration Standard Name` | 113 | 68 | 34 |
| `Secondary Reference Materials` | 113 | 49 | 27 |
| `delta or epsilon Value Reference Standard` | 14 | 12 | 8 |
| `EDS Calibration Standard(s)` | 21 | 3 | 1 |
| `Interference Correction Standard` | 56 | 1 | 0 |

"ID" here means a catalogue string such as `NIST SRM 612`, `USNM 111312` or `BCR-2G`, found by
pattern. It is a lower bound, and none of them is an IGSN.

**The same material holds more than one role in one procedure.** This is the finding that decides the
shape:

- **Nie & Dauphas 2019** (Solution MC): NIST SRM984 is the primary bracketing standard, the
  zero-delta reference, *and* a secondary, listed as *"SRM984 as a sample"* and spiked into DTS-2b
  and PCC-1.
- **McCoy+2025_SI** (EPMA): magnetite, San Carlos olivine and Springwater olivine are calibration
  standards *and* secondaries, each for a different phase.
- **Craddock et al. 2008** (Solution MC): in-house S solutions are calibrated against IAEA-S-1, which is
  also in the secondary list; the delta reference is V-CDT, a scale and not a material in the lab.
- **Wu et al. 2023** (LA-Q): XN02 xenotime is used for a matrix-induced fractionation correction, a role
  none of our fields names.

So one material can't be filed under one role. A list per role (primaries here, secondaries there)
would give SRM984 three entries and three identifiers. The domain has to be one list, with the role
recorded per member.

### Proposal

**One domain, one identifier space.** Every standard used in a procedure or session is a member of
`standard`. The fields that say which standard serves what point to members of that list instead of
holding names.

| SMR's attribute | How it would be carried | Change |
|---|---|---|
| Name / identifier | the definer's member label, plus a new identifier field | D1, D5 |
| Primary or secondary | a new role field, keyed `standard`, more than one value allowed | D2 |
| Standardisation target | the role, plus the assignment fields below | D2, D3 |
| Target species it calibrates | `Primary Calibration Standard Name` (already `target material x target species`); `Interference Correction Standard`, `delta … Reference Standard` (already `target species`) | D3 |
| Target material context | the same assignment field's `target material` component | D3: no new field |
| Material of the standard | a new field, keyed `standard` | D4 |
| Citation for the reference values | a new field, keyed `standard` | D6 |
| Expected / achieved statistics | `Analytical Precision`, `Analytical Accuracy` and the ICP-MS precision and accuracy fields, already `standard x reported property`, two-level since 2026-10-29 | none (D7: wording) |
| An ID a dataset row can point to | the member's identifier: its registry ID where it has one, otherwise one the record assigns | D5 |

#### Decisions for RD

**D1. Broaden the existing definer rather than add a second one.**
Rename `Secondary Reference Materials` to `Reference Materials`, still `defines: standard`, and make
its description cover every standard: calibration, bracketing, QC, interference, delta reference,
matrix correction. *Recommended.* A key has one definer (7.4), and two lists would give a material in
two roles two identities, which is exactly the Nie & Dauphas case. The cost is a field rename in 12
TAPPs and a re-read of the 49 filled literature cells, which currently list secondaries only.

**D2. Add `Reference Material Role`, keyed `standard`.**
C=Basic, D=Editable, `Controlled list / Text`, more than one value per member. Proposed vocabulary,
to be checked against the literature before applying:
`Primary calibration` | `Bracketing` | `Secondary (quality control)` | `Interference correction` |
`Delta or epsilon reference` | `Matrix correction` | `Drift monitor`.
*Recommended.* This is what lets a schema say "standards whose role includes secondary" when it
validates the QC statistics, and it is the same move #23 proposes for monitored properties.
**Internal standards are excluded:** in ICP-MS an internal standard is an element already in the
sample (`Internal Standard Element`), not a reference material, so it belongs to the
monitored-property role in #23, not to this domain.

**D3. Keep the assignment fields where they are; change what their values are.**
`Primary Calibration Standard Name`, `Interference Correction Standard` and `delta or epsilon Value
Reference Standard` keep their keys. Their descriptions change to *"name an entry in `Reference
Materials`"*, so a value is a pointer, not free text. The material name, source and citation move out
of the primary's description into the definer and D4–D6. *Recommended.* These fields already answer
SMR's "which target species" and "which target material" questions with the right key, and
`target material x target species` came from evidence (McCoy+2025_UA, 2026-09-29). A field that
repeated the same pairing from the standard's side would be a second home for one fact.
Optional, and not recommended now: drop "Name" from `Primary Calibration Standard Name`. It would be
more accurate, but it's a second rename for one change. Better done in a later naming pass.

**D4. Add `Reference Material Type`, keyed `standard`.**
C=Advanced, D=Editable, `Text (free)`, for example `olivine`, `synthetic silicate glass`,
`metal`, `solution`. *Recommended, as its own field and not a `Target Material` entry.* `Target
Material` lists what the procedure is designed to analyse. A standard's material is a property of the
standard, and the match between the two (matrix matching) is already expressed by D3's
`target material` component. Listing standards' materials in `Target Material` would make the
procedure claim to analyse its own calibrants.

**D5. Add `Reference Material Identifier`, keyed `standard`.**
C=Advanced, D=Editable, `Text (free)`, the registry or catalogue identifier where one exists: IGSN,
`NIST SRM 612`, `USNM 111312`, a GeoReM entry. Modelled on `Sample Persistent Identifier`.
*Recommended.* The record-assigned local ID SMR describes, for standards with no registry ID, is
the schema's member ID, not a TAPP field. Add one sentence to the schema README saying so. Note the
Rule 13 overlap: a secondary that is also registered as a sample (an IGSN) may appear in both
domains, and a dataset row measuring it may cite either ID. The README should say they will be the
same identifier where both exist.

**D6. Add `Reference Value Source`, keyed `standard`.**
C=Basic, D=Read-Only, `Text (free)`: the publication or compilation giving the accepted values, such
as *"Jochum et al. 2011, doi:…"* or *"GeoReM preferred values"*. *Recommended, keyed `standard` rather
than `standard x reported property`*, using the keyed-value notation (7.3.4) where values for one
material come from more than one source. Re-key only if the literature check finds per-element
sources are common. The primary's description already asks for this citation; it moves here (D3).

**D7. Say which standards the QC statistics apply to.**
Add to `Analytical Precision`, `Analytical Accuracy` and the three ICP-MS precision and accuracy
fields: *"Reported for standards whose role includes secondary (quality control); a primary
calibration standard's agreement with its own accepted values is not a test of accuracy."*
*Recommended.* Once the domain includes primaries, `standard x reported property` would otherwise
invite circular accuracy figures.

### Out of scope

- **Instrument-axis calibration references:** `CL Wavelength Calibration Reference`, `Diffraction
  Calibration Reference`, `EELS Energy Calibration`, `CT Number Calibration`. They anchor an instrument
  axis (wavelength, camera length, energy, CT number), not a reported property, and stay `(none)`
  scalars. The key definition allows them in the domain; nothing yet needs them there.
- **TEM `EDS Calibration Standard(s)`.** TEM doesn't consume Module_CompositionQC. Folding it in means
  either adding the module to TEM or a TAPP-owned definer there. Defer until TEM's composition
  reporting is reviewed; 3 of 21 columns fill it.
- **`Calibration Standard Measurement Frequency` and `Analysis Sequence`**: unchanged. They describe
  the session's order of runs, not the standards.

### Before applying

1. **Re-read the literature cells** for the broadened definer: add primaries, interference, delta and
   matrix-correction standards to each procedure's `Reference Materials` cell, and fill D2, D4–D6
   where the paper states them. Expect most D4–D6 cells to stay blank or `N`.
2. **Check the D2 vocabulary** against every filled cell of the four standards fields. Add or drop
   terms on evidence.
3. **Run `check_field_ownership.py`** on every field touched. Module_CompositionQC owns the definer, the
   primary and the statistics' A–E/I; the rest are TAPP-owned.
4. Gates: `validate_tapp.py`, `recompose_all_20260812.py --check`, `audit_keys_vs_literature.py`
   (the new `standard` consumers need `standard` members in the literature cells), mirror sync.

### Interaction with other issues

- **#23 (monitored-property role):** same pattern, a role attribute per member. Keep the two role
  vocabularies separate (a standard and a monitored mass are different kinds of thing), but write the
  two proposals together so the fields read alike.
- **Rule 14.5:** after this change, the overlap sentence ("report the analyses of each secondary
  reference material") can point dataset rows at a `standard` member ID, for any role.

### Appendix A: the fields after D1–D7 (draft text)

Order follows the proposed placement in Module_CompositionQC: the definer, its four attributes, then
the assignment fields, then the statistics. **Bold** in the Status column marks a change.

| # | Field | Status | C | D | E | I | Owner | In |
|---|---|---|---|---|---|---|---|---|
| 1 | `Reference Materials` | **renamed** from `Secondary Reference Materials`; **B, F, J rewritten** | Basic | Editable | Text (free) | `defines: standard` | CompositionQC | 12 |
| 2 | `Reference Material Role` | **new** | Basic | Editable | Controlled list / Text | `standard` | CompositionQC | 12 |
| 3 | `Reference Material Type` | **new** | Advanced | Editable | Text (free) | `standard` | CompositionQC | 12 |
| 4 | `Reference Material Identifier` | **new** | Advanced | Editable | Text (free) | `standard` | CompositionQC | 12 |
| 5 | `Reference Value Source` | **new** (citation moved out of #6) | Basic | Editable | Text (free) | `standard` | CompositionQC | 12 |
| 6 | `Primary Calibration Standard Name` | **B, F, J revised**; key unchanged | Basic | Editable | Text (free) | `target material x target species` | CompositionQC | 12 |
| 7 | `Interference Correction Standard` | **B, F revised** | Advanced | Read-Only | Text (free) | `target species` | TAPP | EPMA, SEM, SEM_Composition |
| 8 | `delta or epsilon Value Reference Standard` | **B, F revised** | N/A | Basic | Text (free) | `target species` | TAPP | Solution MC |
| 9 | `Analytical Precision` | **one sentence added** | Advanced | Basic | Text (free) | `standard x reported property` | TAPP | EPMA, SEM, SEM_Composition |
| 10 | `Analytical Accuracy` | **one sentence added** | Advanced | Basic | Text (free) | `standard x reported property` | TAPP | EPMA, SEM, SEM_Composition |
| 11 | `Within-Session Analytical Precision and Assessment Method` | **one sentence added** | Basic | Basic | Text (free) | `standard x reported property` | ICPMS | 9 |
| 12 | `Between-Session (Long-Term) Analytical Precision and Assessment Method` | **one sentence added** | Advanced | Basic | Text (free) | `standard x reported property` | ICPMS | 9 |
| 13 | `Analytical Accuracy and Assessment Method` | **one sentence added** | Basic | Basic | Text (free) | `standard x reported property` | ICPMS | 9 |

Tiers, data types and keys of the existing rows (1, 6–13) are unchanged.

#### Draft text

**1. `Reference Materials`**
- B: Every reference material or reference scale used in the procedure or session: calibration and
  bracketing standards, quality-control (secondary) materials, and materials used for interference,
  matrix or delta corrections. List each material once, whatever roles it holds. The fields that
  assign standards (`Primary Calibration Standard Name`, `Interference Correction Standard`,
  `delta or epsilon Value Reference Standard`) name entries in this list.
- F: e.g., NIST SRM 612 | Kakanui kaersutite | San Carlos olivine | IRMM-014 | V-CDT | None
- J: A result can be checked only against the standards that produced it, and a material used in
  several roles is one standard, not several.

**2. `Reference Material Role`**
- B: What each reference material is used for. A material may hold more than one role, for example
  a bracketing standard that is also run as an unknown; record every role it holds.
- F: Primary calibration | Bracketing | Secondary (quality control) | Interference correction |
  Delta or epsilon reference | Matrix correction | Drift monitor
- J: Only a material run as a secondary tests accuracy; a calibration standard agrees with its own
  accepted values by construction.

**3. `Reference Material Type`**
- B: The kind of material each reference material is (mineral, glass, metal, solution, gas, or a
  reference scale), with the mineral or phase name where it has one.
- F: e.g., olivine | synthetic silicate glass | metal | single-element solution | reference scale
- J: A mismatch between a standard's matrix and the samples' is a common source of bias in microbeam
  and laser-ablation analysis.

**4. `Reference Material Identifier`**
- B: The registry or catalogue identifier of each reference material, where one exists: an IGSN, a
  certifying body's catalogue number (NIST, IRMM, USGS) or a museum catalogue number (USNM). Where
  the material is also registered as a sample, give the same identifier as in `Sample Persistent
  Identifier`. Leave blank for an in-house material with no registered identifier.
- F: e.g., NIST SRM 612 | USNM 111312/444 | IRMM-014 | IGSN:IEXXX0001
- J: Material names are reused across lots and suppliers; the identifier says which material was used.

**5. `Reference Value Source`**
- B: The publication or compilation giving the accepted values used for each reference material, with
  a DOI where available. Where values for different properties of one material come from different
  sources, say which applies to which.
- F: e.g., Jochum et al. 2011, doi:10.1111/j.1751-908X.2011.00120.x | GeoReM preferred values |
  certificate of analysis
- J: Results calibrated against different published values for the same material are not directly
  comparable. *(moved from #6)*

**6. `Primary Calibration Standard Name`**
- B: The reference material against which each target species is calibrated in each target material,
  converting raw signal intensities to concentrations, or anchoring an isotope ratio as the bracketing
  standard. Name an entry in `Reference Materials`. Where calibration instead uses the vendor's stored
  library or theoretical response factors rather than measured reference materials ('standardless' or
  'semi-quantitative' quantification), record that here, naming the library or model used. 'None'
  means no calibration was performed at all, which is a different answer.
- F: e.g., Smithsonian anorthite | NIST SRM 612 | IRMM-014
- J: Which standard calibrates which target species in which material decides whether the calibration
  is matrix-matched.
- Removed: *"Give the material name, its source or supplier, and a citation for the accepted values
  used"* (now #1, #4, #5), and *"or zero-delta reference"* (that is #8's job).

**7. `Interference Correction Standard`**
- B: The reference material used to quantify the interference correction for each affected target
  species. Name an entry in `Reference Materials`.
- F: e.g., Synthetic TiO2 | Chromite USNM 117075
- Removed from F: the overlap in parentheses (*"Ti Kb overlap"*), which describes the correction, not
  the standard.

**8. `delta or epsilon Value Reference Standard`**
- B: The isotopic reference used as the zero-delta anchor for expressing isotopic compositions in delta
  (δ, per mil) or epsilon (ε, per ten thousand) notation: δⁱX = [(ⁱX/ʲX)sample / (ⁱX/ʲX)reference − 1]
  × 1000‰. The reporting reference is a per-study or per-publication decision. Name an entry in
  `Reference Materials`, and give the isotope ratio used for normalization.
- F: e.g., IRMM-014 | NIST SRM 981 | JMC Lyon | Sn_IPGP (in-house standard)
- Removed: *"lot or batch number"* (now #4) and the citation in F (now #5).

**9–13. The QC statistics**, the same sentence added to each, placed before its `In the dataset:`
sentence where it has one:
> Reported for standards whose role includes secondary (quality control); a primary calibration
> standard's agreement with its own accepted values is not a test of accuracy.

For the three precision fields (#9, #11, #12), the second clause would read *"… is not an independent
test of precision"*.

#### Notes

- **Session-added standards.** #1 is Editable at session level, so a session may add a material the
  procedure didn't register. That is why #2–#5 are Editable rather than Read-Only: a member added in
  the session needs its attributes filled in the session.
- **#7 stays Read-Only** although its value points into an Editable list. A session that changed its
  interference standard would be changing the correction, which the procedure fixes.
- **#8 stays C=N/A.** Pointing to a member doesn't change that the delta reference is chosen per study;
  the member it names may be one added in the session.
