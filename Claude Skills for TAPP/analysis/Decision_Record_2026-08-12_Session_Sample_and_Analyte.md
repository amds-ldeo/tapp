# Decision Record — The Analysis Record is the Session; `sample` Becomes a Key; and the `analyte` Vocabulary

**Date:** 2026-08-12
**Approved by:** Cosmote
**Status:** APPROVED and **FULLY EXECUTED** — all 12 steps of Part D, on 2026-08-12. Lint held at
0 ERROR / 0 WARN throughout. What remains open is listed below the table and in Part E.

**Scope:** all 16 production TAPPs; four modules; `conventions.md` Rules 7, 10 and a new Rule 13;
`validate_tapp.py`; `precedents.md`; `sync_current_tapps.py`.

| Step | State | Effect |
|---|---|---|
| 1 | done | 13 `Analyte` descriptions reframed around a shared stem; `Detection Limit` harmonised in the 6 LA TAPPs; `measurand` + `analyte` added to the VIM3 table in `conventions.md` |
| 2 | done | `Analyte` re-triaged in `COLB_DIVERGENCE_TRIAGED` (0.01/6 variants → 0.36/4, PRINCIPLED now correct); definer-stem check added to `validate_tapp.py` with `COLB_DEFINER_STEM_EXEMPT` |
| 3 | done | `channel` minted in the three electron-beam TAPPs — 30 keys moved, 19 descriptions rewritten, `Dwell Time per Pixel` register entry rewritten. **EPMA v16→v17, SEM v13→v14, SEM_Composition v13→v14**; `composed_tapps.json` paths updated; all three still compose-MATCH |
| 4+5 | done | Applied together with a single bump. `Mass Resolution per Analyte` → **`Mass Resolution Assignment`**, `analyte`→`channel` in 5 TAPPs, with the cross-reference in `Mass Resolution Setting` updated; `Counting Statistics Error` → `sampling unit x reported property` in 3; `EDS Detection Limit` → `reported property` in TEM. **9 TAPPs bumped**: EPMA v17→v18, SEM v14→v15, SEM_Composition v14→v15, TEM v15→v16, LA-MC v10→v11 (×2), LA-SF v14→v15 / UPb v15→v16, Solution SF v16→v17 |
| 6 | done | `channel` gloss in 7.2 reworded to lead with the general swept/selected axis; examples gained a WDS spectrometer assignment, a demagnetisation step and a DSC setpoint. No row changed |
| 7 | done | `sample` added to `KEY_ANCHORS` **and** to 7.2's anchor table (small merge from step 8, to avoid a window where the validator accepts a key the rules do not document); name-variant key-divergence check added with `KEY_NAME_VARIANT_EXEMPT`, seeded with 3 adjudicated pairs |
| 8+9 | done | The session/sample restructure, applied together. **Rule 13** written; `Sample Name` → `defines: sample` and `Sample Persistent Identifier` → `sample` in all 16 (both descriptions harmonised, so both left the Column B register); `Session Identifier` added to **Module_Group1** and composed into all 16; 17 rows nested to `sample > sampling unit`; `Counting Statistics Error` completed to `sample > sampling unit x reported property`; `A > B x C` specified in 7.3. Four modules edited and version-bumped, **all 16 TAPPs bumped**, all 16 recompose-MATCH |
| 10 | done | **Rule 10.1** added — a shared session calibration correlates *samples*, the second correlation source, now representable. No new field: `Uncertainty Propagation Method` must separate session-systematic from per-analysis random components. A5's sample/standard overlap recorded in Rule 13 and in `precedents.md` |
| 11 | done | Parts A and B lifted into `precedents.md` as four entries (session/sample; analyte; the EPMA channel evidence; `Mass Resolution Assignment`), 182 lines. Lint 0 ERROR / 0 WARN |
| 12 | done inline | Bumping, xlsx regeneration and mirror sync happened within steps 3–9 rather than as a closing pass |

Live `sample` key census after the retrofit: `defines: sample` ×16, `sample` ×32,
`sample > sampling unit` ×17, `sample > sampling unit x reported property` ×3.

**A4 — CLOSED 2026-08-12.** The literature pass was run over all four deferred rows and **none is
re-keyed**: `Isotope Dilution Spike`, `Fusion Flux and Dilution Ratio`,
`Pre-Ablation Surface Treatment` and `Sample Preparation Method` all stay `(none)`, because in every
case the variation visible in the extractions is *across procedures* rather than *within* one.
`Sample Aliquot Mass or Volume` → `sample` is **confirmed** by Makishima et al. 2011, which states
three different mass ranges by sample material inside a single procedure.
`Pre-Analysis Imaging and Screening` → `sample` has **zero** literature coverage and rests on the
field definition alone — untested rather than contradicted. Full record and the
across-columns-is-not-across-samples discriminator: `precedents.md`, "The A4 per-sample audit".

Origin: a question about whether `analyte` is still needed as a field and as a key, given the
element-vs-isotope ambiguity across techniques and the arrival of monitored/reported property
vocabulary. The investigation that followed reached past the vocabulary into the record structure
itself. Sections A and B were written in `precedents.md` style and were lifted into that file in
step 11, together with the two literature results from Part C; sections C–E are working
material and stay here.

---

## 0. What this record decides, in one page

| # | Decision | Churn |
|---|---|---|
| A1 | The analysis record is the **session**, not one sample. `sample` becomes a key. | structural |
| A2 | `Sample Name` becomes `defines: sample`; `Sample Persistent Identifier` becomes `sample`. New **Rule 13**. | 32 rows |
| A3 | `sampling unit`-keyed fields nest: `sample > sampling unit`. | 13 rows |
| A4 | Preparation attaches to the **sample**, not the session. No new key; `preparation step` is unchanged. | ~6 rows |
| A5 | `standard` and `sample` are **overlapping** domains. Both keys retained. | 0 rows, 1 note |
| A6 | Add a `Session Identifier` field holding the lab's own run ID. | 16 rows |
| A7 | Rule 10 extends to inter-sample error correlation via shared session calibration. | rule text |
| A8 | Tier vocabulary (Columns C, D) is unchanged. | 0 rows |
| B1 | `analyte` = the chemical entity determined, at the granularity determined. 7.2's wording stands; 8 contradicting descriptions are deleted. | 8 rows |
| B2 | `analyte` keys **specifications**, never **results**. | 4 rows |
| B3 | `analyte` stays chemistry-only. The `channel` gloss is rewritten to cover non-chemical sweeps. | 1 line |
| C1 | **Test 1 result:** `channel` is real in EPMA. 9 rows move to `channel`; `WDS Spectrometer Channel` becomes the definer. | 30 rows |
| C2 | **Test 2 result:** `Mass Resolution per Analyte` is `channel`, and is renamed. | 5 rows |

---

# Part A — The analysis record is the session

### A1. The analysis record is the session, and `sample` is a key (2026-08-12)

**Decision: the analysis record corresponds to one execution of a procedure — a session — which may
cover many samples. `sample` is added to the key vocabulary as an anchor, applicable wherever a
session can contain more than one sample.**

The framework previously defined the analysis as *the specific execution of that procedure — what
actually happened in a given session, on a given sample, on a given date*, which asserts both
readings at once. Real sessions routinely cover many samples: an LA-ICP-MS run, a solution sequence,
an EPMA session on a mount holding several sections. Each sample carries its own IGSN and may carry
its own preparation history.

**Reasoning.** Group 1 is *already* session-shaped in every TAPP:

```
C=N/A  D=Basic  Analyst
C=N/A  D=Basic  Analysis Start Date
C=N/A  D=Basic  Analysis End Date
```

A start *and* end date describes a session, not a specimen. `Within-Session` and `Between-Session`
precision fields already exist in the QC groups, so "session" was established vocabulary in the
library; it had simply never been made structural. Group 1 was treating the record as a session
while Group 2 treated it as one sample. This record resolves that contradiction in favour of the
session.

**The decisive consequence is not tidiness, it is Rule 10.** A shared session calibration is a source
of error correlation *between samples*. Two analyses from one bracketing sequence are correlated; two
from different sessions are not. With the session unrepresented, that correlation cannot be stated at
all. See A7.

**`Keyed By` carries the level distinction for free.** No new column is required:

| Column I | Means |
|---|---|
| `(none)` | per session — tuning, gas flows, calibration, drift correction |
| `sample` | per sample — identity, preparation, aliquot amounts |
| `sample > sampling unit` | per spot / grain / aliquot within a sample |
| `analyte`, `channel`, `reported property`, `standard` | unchanged |

This is the same argument Rule 7 made against the Column G label `Analyte-Specific`: one label was
concealing four distinct keys. "Analysis-level" was concealing two distinct levels.

**Not settled by this entry:** whether an intermediate *batch* object is also needed for preparation
that spans sessions. A4 avoids the question by attaching preparation to the sample; if that proves
insufficient in practice, a `preparation batch` grouping is the next thing to consider — but not
before there is a field it would key.

---

### A2. `Sample Name` is the definer for `sample` — Rule 13

**Decision: `Sample Name` (currently C=N/A, D=Basic) becomes `defines: sample`.
`Sample Persistent Identifier` becomes `Keyed By = sample`. Both are mandatory in every TAPP, decreed
as Rule 13 in the style of Rules 8 and 9.**

**Reasoning.** 7.4a requires exactly one `defines: sample` per TAPP. `Sample Persistent Identifier` is
the intuitive candidate but is C=Advanced — an optional definer would leave the key's domain
unenumerable in the common case, which is precisely the failure 7.4a exists to prevent. `Sample Name`
is already D=Basic, i.e. mandatory at analysis time, in all 16 TAPPs. C=N/A is correct and stays: the
procedure is sample-neutral and specifies nothing about which samples it will be applied to.

This mirrors Rule 9 exactly — a mandatory field whose job is to declare a domain other fields key off.

**The definer pattern is the one `Sampling Unit` already uses:** type at procedure level, instances at
analysis level. The earlier objection that no procedure can enumerate its future samples was
overstated; the procedure declares the *kind* of sample (already covered by `Target Material`) and the
analysis lists the actual ones.

---

### A3. `sample > sampling unit` — the first real use of containment notation

**Decision: fields currently keyed `sampling unit` become `sample > sampling unit`. The `Sampling Unit`
definer stays `defines: sampling unit`, since it declares the unit *type*, which does not vary by
sample.**

**Reasoning.** 7.3's enumerability test: *can you enumerate B without reference to A?* "Spot 3" is
meaningless without knowing which sample it is on. No → containment, not cross-product.

7.3 currently records that *no field in the current library uses nesting*. By the library's own
7.4a–c logic — retire abstractions that have no user — that was a standing smell. This gives the
notation its first genuine user.

Affected: the 13 `sampling unit` rows (`Analysis Location/Spot Coordinates` ×6, `Beam Current` ×3,
`Beam Damage Minimization` ×3, `Minimum Resolvable Feature Size`, `Partial Volume Effect Criteria`,
`Phase Identification Method` ×2, `Segmentation Threshold Values or Criteria`), plus
`Counting Statistics Error` — see B2, which moves it for a different reason.

---

### A4. Preparation attaches to the sample, not the session

**Decision: sample preparation metadata is keyed by `sample` where it varies per sample. The existing
`preparation step` key is unchanged — no new key is added, and none of its 9 rows moves.**

**Reasoning.** Preparation and measurement are different events. A digestion batch of twenty can split
across two ICP-MS runs; one run can draw on three batches. So `preparation batch` and
`measurement session` are orthogonal groupings, and preparation cannot be attached to the session.
It attaches to the sample, because preparation history travels with the sample. That is the correct
relational answer and it avoids introducing a second grouping axis.

**Why the 9 `preparation step` rows stay put.** Under Rule 7.12 the key is the finest axis attested in
reported data, and papers report one digestion protocol for a whole study — `sample x preparation
step` is not attested. `Digestion Acid(s)`, `Digestion Temperature` and `Digestion Duration` remain
`preparation step` in Solution Q / SF / MC, with `Number of Digestion Steps` remaining
`defines: preparation step`.

**What moves** is a small set of currently-`(none)` Group 2 fields that are genuinely per-sample:

| Field | TAPPs | Now | Proposed |
|---|---|---|---|
| `Sample Aliquot Mass or Volume` | Solution ×3 | `(none)` | `sample` |
| `Isotope Dilution Spike` | Solution ×3 | `(none)` | `sample` — *verify the spike amount varies* |
| `Fusion Flux and Dilution Ratio` | LA ×6 | `(none)` | `sample` — *verify* |
| `Pre-Ablation Surface Treatment` | LA ×6 | `(none)` | `sample` — *verify* |
| `Sample Preparation Method` | all | `(none)` | `sample` where a session mixes preparation routes |
| `Pre-Analysis Imaging and Screening` | most | `(none)` | `sample` |

Rows marked *verify* need a pass over the literature extractions before being moved; the rest follow
from the field definitions. `Sample Aliquot Mass or Volume` is unambiguous — every sample in a
digestion batch has its own aliquot mass, and it cannot be scalar across a session.

---

### A5. `standard` and `sample` are overlapping domains

**Decision: `standard` and `sample` are retained as separate keys, and the overlap between them is
recorded explicitly. A schema generator must not treat them as disjoint.**

**Reasoning.** `standard` names a *role*, not a class of material. Secondary reference materials are
run through the same calibration as unknowns and evaluated against accepted values — they are
simultaneously samples (measured) and standards (anchoring). Many are SESAR-registered with their own
IGSNs. Round-robin materials are unknowns to the analyst and standards to the organiser. Labs promote
well-characterised samples to in-house standards.

The keys stay separate because they key *different fields*: `standard` keys anchoring and QC fields
(33 `standard x reported property` rows); `sample` keys identity and preparation. That one physical
object can play both roles is a registry fact, held by SESAR, not a key fact.

**Stated explicitly because it is the kind of thing a consumer will get wrong silently:** a secondary
RM legitimately appears in both domains within one session, and that is not double counting. A
disjointness constraint between samples and standards would be violated by ordinary sessions.

*Exception:* primary calibration standards are never unknowns — their values are inputs, not results.
The overlap is with secondary RMs specifically, which is also how the library already splits the
fields.

---

### A6. `Session Identifier`

**Decision: add `Session Identifier` (C=N/A, D=Basic, `Keyed By = (none)`) to every TAPP, holding the
laboratory's own run / sequence / batch identifier.**

**Reasoning.** Group 1 currently carries `Analyst` and start/end dates but no session identifier. Now
that the analysis record *is* the session, it needs one. Independent of whether Astromat mints a
persistent identifier at submission — an infrastructure decision outside this record — the lab
already has an identifier the instrument generated (the `.raw` batch, the sequence file name). It
costs the analyst nothing and it is the only thing linking an archived analysis back to the raw
instrument files.

If a repository-minted PID is also introduced, the two coexist: minted PID for citation, lab run ID
for provenance.

---

### A7. Rule 10 extends to inter-sample error correlation

**Decision: Rule 10 (`Error Correlation Between Reported Quantities`) is extended to cover correlation
between samples arising from a shared session calibration.**

**Reasoning.** Rule 10 exists because jointly interpreted quantities have correlated errors. Once the
record is a session, the correlation induced by one calibration across many samples becomes
representable for the first time, and it is exactly the kind a downstream user must know about before
averaging or regressing across samples. This is the scientific payoff of A1 and should be captured in
rule text rather than left implicit.

---

### A8. Tier vocabulary is unchanged

**Decision: Columns C and D keep their current meanings and values. No change.**

Recorded so it is not relitigated. `D=Basic` still means mandatory input at analysis time;
`Read-Only` and `Editable` still mean imported from the procedure. The level distinction A1
introduces is carried by Column I, not by a new tier.

---

# Part B — The `analyte` vocabulary

### B1. `analyte` — definition (2026-08-12)

**Decision: Rule 7.2's existing wording stands unchanged. The eight field descriptions that
contradict it are corrected.**

> **`analyte`** — the chemical entity the procedure sets out to determine, at the granularity at which
> it determines it. Element (EPMA, ICP-MS trace work); valence species (Mössbauer); molecule (GC-MS);
> molecular formula (FTICR-MS). Never the isotope or mass where the isotope is a route to an element;
> never the reported quantity.

**Reasoning.** 7.2 already reads *"the chemical species determined, at whatever granularity the
procedure determines it"* and already carries a non-elemental example (Fe²⁺/Fe³⁺ at valence
resolution). It extends to organic molecules and molecular formulae without amendment. The problem was
never the rule; it was that eight `Analyte` descriptions predate Rule 7 and name a different domain:

| TAPPs | Current description says | Verdict |
|---|---|---|
| LA-MC, LA-MC-UPb, LA-Q, LA-Q-UPb, LA-SF, LA-SF-UPb (6) | *"Isotopes (mass/charge) this procedure is designed to measure"* | **wrong** — names the isotope domain, which has no consumer (7.4c) and is not technique-neutral |
| Solution Q, Solution SF (2) | *"Elements or isotopes"* | **wrong** — the ambiguity written down verbatim |
| EPMA, SEM, SEM_Composition, Solution MC, TEM (5) | element-level | correct |

A proposal to define analyte as "always the element" was considered and rejected: it does not extend
to organic techniques, which are on the roadmap. 7.2's granularity-agnostic wording is better than the
proposed replacement. A later proposal to rename the field `Target Elements` was rejected for the same
reason, plus three others: `Target` already carries a restricted meaning in three field names, the key
would no longer match the field name, and `analyte` is the IUPAC term a curator will search for.

**Why the isotope domain is not the analyte domain — stated carefully, because the obvious argument
does not work.** It is tempting to say isotope-as-analyte merely duplicates `channel` or
`reported property`. That argument proves too much: element-as-analyte duplicates the
reported-property list in *every* concentration-reporting procedure, and the library kept the field
anyway — the isomorphism precedent demoted `analyte` as a **key** for reporting fields without
deleting the **field**. Duplication was never the disqualifier.

Nor is the isotope domain simply `channel` under another name. Misra et al. 2014 acquires ⁴³Ca in both
LR and MR — one isotope, two channels — so the isotope domain is genuinely coarser than `channel` and
finer than `analyte`.

The two reasons that do hold:

1. **7.4c — no consumer.** Every isotope-flavoured field in the library is scalar:
   `Double-Spike Isotope Pair`, `Internal Normalization Element and Isotope Ratio`,
   `Mass Fractionation Law`, `Isotope Dilution Spike`, `Internal Standard Element` — all `(none)`.
   Nothing needs *"one value per isotope, shared across the channels of that isotope."* This is the
   same test that retired `conversion` and `acquisition pass`.
2. **Technique-neutrality.** Fe is Fe by EPMA, ICP-MS, XRF or INAA; ⁵⁶Fe is a position that exists
   only inside a mass spectrometer. A registry whose purpose is matching procedures across techniques
   needs the axis that survives a change of instrument, or *"which procedures determine Fe?"* cannot
   be asked of the electron-beam and mass-spectrometric TAPPs in one query.

**An isotope is never an analyte — unconditionally.** An earlier draft of this entry carried a caveat
admitting nuclides as analytes where the nuclide is the reported determinand (AMS cosmogenics, ¹⁴C,
²¹⁰Pb, ²²⁶Ra). **That caveat is withdrawn.** Working the cases through, every one of them still has
element-level chemistry, and it is the chemistry that the analyte-keyed fields describe:

| Procedure | Analyte | Reported property |
|---|---|---|
| ¹⁰Be / ²⁶Al / ³⁶Cl cosmogenics | **Be, Al, Cl** — the separation chemistry, the ¹⁰B interference, the carrier and the calibration are all elemental | [¹⁰Be] atoms g⁻¹, exposure age |
| ²¹⁰Pb, ²²⁶Ra chronology | **Pb, Ra** | activity |
| ¹⁴C dating | **C** | F¹⁴C, calibrated age |
| ³He/⁴He, D/H, ²³⁵U/²³⁸U | **He, H, U** | the ratios |

No case could be constructed in which an isotope must be the analyte. The unconditional rule is both
correct and far easier for a submitting researcher to apply.

**The reason, and it is the word "species".** Isotopes of an element *are the same chemical species* —
they share every property the analyte-keyed fields describe: separation chemistry, calibration
standard, crystallographic site, chromatographic behaviour, elemental interferences. Valence states do
not (Fe²⁺ and Fe³⁺ differ in coordination, site occupancy and solubility), and neither do compounds.
Isotopes are the **only** axis on which measurement granularity is finer than chemical granularity,
which is why that one case reads as an imposed grouping while valence and compounds feel natural.

**Test for a submitting researcher:** *would a chemist call these different substances?*
⁵⁶Fe vs ⁵⁷Fe — no. Fe²⁺ vs Fe³⁺ — yes. n-C₂₉ vs n-C₃₁ — yes.

---

**Allowed content.** The analyte axis is the chemical-identity axis. It is **not ordered relative to
the element** — it can sit finer, at, inside, or orthogonal to element level:

| Position | Form | Example | Technique |
|---|---|---|---|
| Finer than element | valence / oxidation species | `Fe²⁺, Fe³⁺` | XANES, Mössbauer |
| At element level | element symbols | `Si, Ti, Al, Fe, Rb, Sr` | EPMA, SEM, TEM, ICP-MS, XRF, INAA |
| A chemically defined fraction of an element | operational species | organic carbon (TOC) | Rock-Eval, EA |
| Orthogonal to elements | compounds; molecular formulae | `n-C₂₇, n-C₂₉, n-C₃₁`; `C₁₈H₂₀O₈` | GC-MS, GC-IRMS, LC-MS, FTICR-MS |

**Never allowed**, because the distinction is not a chemical one:

| Excluded | Why | Goes to |
|---|---|---|
| Masses and acquisition addresses — `m/z 238`, `⁵⁶Fe` as an address | a mass is not a species | `channel` |
| Reported quantities — `[Fe]`, `⁸⁷Sr/⁸⁶Sr`, `δ⁵⁶Fe`, `Rb/Sr`, `[¹⁰Be]` | a quantity is not a species | `reported property` |
| Internal standards, interference monitors, carriers — `In`, `²⁰²Hg`, the ⁹Be carrier | not determined | `channel` |
| The same species in a different environment — Fe²⁺ on M1 vs M2, high- vs low-spin | an environment is not a species | `model component`, or `sampling unit` where the environment is a physical subdivision |

That last row is the sharp boundary for the first speciation TAPP: **Fe²⁺ and Fe³⁺ are different
analytes; Fe²⁺-on-M1 and Fe²⁺-on-M2 are not.** 7.2 already splits these — it lists
`Fe²⁺/Fe³⁺ at valence resolution` under `analyte` and `Mössbauer doublets/sextets` under
`model component`. The fitted doublet is a decomposition of the signal; the valence species is the
chemical conclusion drawn from it.

**One granularity per TAPP.** Do not mix `{Rb, Sr, ⁸⁷Sr}` in one list — the analyte-keyed fields would
then carry rows of different kinds, and "the primary calibration standard for Rb" and "for ⁸⁷Sr" are
not the same statement. Declare the granularity in **Phase 0 under 7.7**, alongside the key vocabulary
that section already requires.

**Worked case — a procedure measuring Rb and Sr isotopes and reporting isotope concentrations,
isotope ratios, elemental concentrations and elemental ratios.** `Analyte` = **Rb, Sr**. Two entries.
`Monitored Isotopes` = ⁸⁵Rb, ⁸⁷Rb, ⁸⁴Sr, ⁸⁶Sr, ⁸⁷Sr, ⁸⁸Sr plus spike and monitor masses.
`Reported Variables and Units` = [Rb]; [Sr]; Rb/Sr; ⁸⁷Rb/⁸⁶Sr; ⁸⁷Sr/⁸⁶Sr; [⁸⁷Rb]; [⁸⁶Sr]; age. All
four output kinds are reported properties — they differ in what is reported *about* Rb and Sr, not in
what was determined. Every analyte-keyed field here wants element granularity: Rb and Sr are spiked
and calibrated separately, and the Rb-on-Sr isobaric interference at mass 87 is a statement about the
elements.

---

**Field description granularity is technique-specific; the descriptions share a stem.** The key is
granularity-agnostic. All 13 `Analyte` descriptions were reframed 2026-08-12 to open with one shared
sentence — *"The chemical species this procedure is designed to determine, recorded at whatever
resolution the chemistry is resolved — element(s) for this technique; valence species where a
procedure resolves oxidation state; compounds where it resolves molecules"* — followed by a
technique-specific tail. The nine mass-spectrometric TAPPs additionally carry *"Isotopes are not
analytes: isotopes of an element are the same chemical species"*, which is noise in EPMA, SEM and TEM.

This converts what was a hard six-way Column B divergence into a shared stem plus tails.
**Pre-register the remaining divergence as PRINCIPLED** rather than meeting it as a lint failure when
the first organic or speciation TAPP lands.

**Two boundary tests, both already in the library.**

- *vs `channel`* — would substituting a different isotope, line, or instrument address for the same
  entity leave the target of determination unchanged? Yes → `channel`.
- *vs `reported property`* — could the procedure ever report more than one quantity per analyte? Yes →
  `reported property` was always the right key (the isomorphism precedent, `precedents.md`).

**Why `analyte` is not redundant with `channel` + `reported property`, recorded so it is not reopened.**
The domains have members the others lack, in both directions, in the current library:

- **Channels with no analyte.** `Monitored Isotopes` includes interference-monitor masses (²⁰²Hg to
  correct ²⁰⁴Pb). Internal standards are monitored in essentially every solution ICP-MS procedure and
  are never determinands — Solution_Q's own example content for that field is `67Zn | 115In | 209Bi |
  172Yb`, an internal-standard suite.
- **Analytes with no channel.** `Analyte Estimation Method` exists to record that oxygen is calculated
  by cation stoichiometry — an analyte with no X-ray line, no crystal, no counts. Same for Fe³⁺ by
  charge balance. 7.2's anticipated Mössbauer case is the extreme: 256 velocity channels swept, Fe²⁺
  and Fe³⁺ determined, neither monitored.

Two proposals to merge the domains were considered and rejected. `monitored species` collapses into
`channel` and evicts channel's most useful members (interference monitors, internal standards). A
generalised `analyte` covering physical-property sweeps does the same. In both cases the term being
reached for was `channel` under another name.

**The organic case argues for the separation, not against it.** In ICP-MS the axes are near-parallel
(m/z 238 ≈ ²³⁸U ≈ U), which is why the confusion took hold. In GC-MS they come apart completely: one
monitored channel (m/z 57, the alkane fragment) serves forty determinands, each identified by
retention time plus spectral match. In FTICR-MS of DOM the species is an *assignment from* the
channel, with its own rules and tolerances — a documentable step that needs two domains to sit
between. A library that has already separated them absorbs GC-MS, GC-IRMS and FTICR-MS with no
structural change.

---

### B2. Usage rule — `analyte` keys specifications, not results

**Decision: `analyte` keys specifications — what setup, calibration or correction applies to each
determinand. It never keys results or their quality metrics; those take `reported property` under the
isomorphism precedent.**

**Reasoning.** The rule is descriptive of the library as it stands: of the 80 bare `analyte` rows,
every one is a setup, calibration or correction field. It also catches the two rows the 2026-08-12
isomorphism sweep named but did not reach — that entry said the isomorphism holds *"plausibly for
other per-element reporting fields"* and stopped there:

| Field | TAPPs | Now | Proposed |
|---|---|---|---|
| `Counting Statistics Error` | EPMA, SEM, SEM_Composition | `sampling unit x analyte` | `sample > sampling unit x reported property` |
| `EDS Detection Limit` | TEM | `analyte` | `reported property` |

7.2 already places uncertainties inside `reported property` (*quantities and nominal properties alike,
plus their uncertainties*), so `Counting Statistics Error` was never analyte-keyed by the rule's own
scope. `Detection Limit` is `reported property` in all 12 TAPPs that carry it under that name.

**Why the TEM row escaped, and a validator gap it exposes.** Invariant 7.8.7 matches on field *name*,
and TEM renamed the field to `EDS Detection Limit` / `EELS Sensitivity and Detection Limit`. The name
variance hid the key divergence from the check entirely. **Add a key-divergence check across name
variants**, not only across identical names.

---

### B3. Scope — `analyte` stays chemistry-only; the `channel` gloss is rewritten

**Decision: `analyte` is not generalised to physical-property techniques. The `channel` entry in 7.2 is
reworded to lead with the general form.**

**Reasoning.** Physical-property techniques have no determinand layer, because the determinand and the
reported property are the same thing — porosity is both what you set out to determine and what you
report. Lab-XCT is the evidence: 87 content fields, **80 of them `(none)`** (92% scalar), no `analyte`,
no `channel`. EPMA for comparison is 62% scalar. 7.7 already requires absent anchors to be declared,
and already names `analyte` as absent for XCT, Raman and fission track.

What physical-property techniques do have is a **swept axis** — temperature, field, frequency,
pressure, angle — mapping many-to-one onto reported properties (20 demagnetization steps → one ChRM
direction; ~100 pressure steps → one pore-size distribution). That axis is `channel`: it passes the
zero-signal test, and 7.2 already carries non-chemical members of the domain (*velocity channel
137/256*, *855 cm⁻¹ bin*). Mössbauer velocity is literally a swept stimulus.

The generalisation was made when those examples were written; it was never stated in the definition
line, which reads as detector-hardware-specific. Proposed replacement:

> `channel` — a position on the axis the instrument steps through or selects across: mass, wavelength,
> energy, angle, temperature, field, pressure, time. **The address, not the signal.**

Every existing example still validates. Zero rows change.

---

# Part C — Literature test results

### C1. Test 1 — `channel` is real in EPMA

**Question.** Do the 18 `analyte`-keyed rows in EPMA / SEM / SEM_Composition belong to `analyte`, or
are they a collapsed `channel`? Decisive evidence: does any procedure assign more than one
spectrometer setup to a single element?

**Answer: yes. `channel` exists in EPMA and is distinct from `analyte`.**

- **Jia et al. 2022 (JAAS 37, 2351)**, Table 4 — a per-element WDS setup table carrying eleven of the
  eighteen fields: Element | Spectrometer | Line | Calibration standard | Analysis crystal | kV | nA |
  Peak position | Bg− | Bg+ | Peak counting time | Background counting time.
  - **Cr is measured on two spectrometers with aggregate intensity counting** —
    *"LLIF crystals in spectrometer 2 and 3 for Cr"* (Jia et al. 2022).
  - The map is many-to-many in both directions: Sp2 carries Ti, Mn, Cr, V; Sp3 carries Fe, Co, Ni;
    Sp4 carries Sc, Zr, Nb.
- **Batanova et al. 2018 (IOP Conf. Ser. Mater. Sci. Eng. 304, 012001)** confirms this is standard
  practice rather than idiosyncratic: intensity integration across multiple spectrometers is listed
  among the measures used in many laboratories for beam-sensitive phases. It separately compares
  Ti-Kα on L-type versus H-type spectrometers and recommends between them — the same line on
  different channels giving different results.

**Method note, recorded because it nearly produced a false negative.** The 14 pre-existing EPMA
literature columns record `N` — not stated — for `WDS Spectrometer Channel` in **14 of 14**
procedures, and real content for `X-ray Line` in only 2. That is not evidence of absence: all 14 are
meteoritics and mineralogy application papers, which do not publish the setup table. Method papers do.
A key decision taken on that corpus alone would have been an artifact of paper selection. **When a
key question turns on a parameter table, check that the corpus contains method papers before reading
a null result as evidence.**

**Retrofit — EPMA, SEM, SEM_Composition (10 rows each, 30 total).**

| Field | Now | Proposed |
|---|---|---|
| `WDS Spectrometer Channel` | `analyte` | **`defines: channel per analyte`** |
| `X-ray Line` | `analyte` | `channel` |
| `Diffracting Crystal` | `analyte` | `channel` |
| `Proportional Counter / Detector` | `analyte` | `channel` |
| `WDS PHA Setting` | `analyte` | `channel` |
| `Peak Counting Time` | `analyte` | `channel` |
| `Background Counting Time` | `analyte` | `channel` |
| `Background Position(s)` | `analyte` | `channel` |
| `Sequence` | `analyte` | `channel` |
| `Dwell Time per Pixel` | `analyte` | `channel` |

**Staying `analyte`** (determinand-level): `EPMA Technique per Analyte`, `Analyte Estimation Method`,
`Time-Dependent Intensity Correction`, `Blank Correction`, `Interference Corrections Applied`,
`Interfering Elements`, `Interference Correction Standard`, `Primary Calibration Standard Name`.

**Notes.**

- **EPMA now has the same structure as single-collector ICP-MS.** `WDS Spectrometer Channel` plays
  exactly the role `Monitored Isotopes` plays: it lists which addresses serve each element. This
  resolves the schema developers' observation that the electron-beam TAPPs have no `channel` key at
  all, and it gives 7.3.1 users in both technique families rather than only in mass spectrometry.
- **Column B already said so.** EPMA's `Dwell Time per Pixel` description reads *"For WDS: per
  spectrometer per pixel"* — a key named in the description that Column I did not carry. That is the
  exact failure mode 7.8.9 was implemented to catch, one field at a time.
- **`Primary Calibration Standard Name` is flagged, not moved.** Jia's Table 4 carries it as a setup
  column, but the register entry records per-analyte assignment in 11 of 15 EPMA extractions. Keep
  `analyte`; revisit if a second multi-spectrometer paper shows per-channel standards.
- **SEM and SEM_Composition are not a straight copy.** EDS has no spectrometers, so the `channel` key
  applies only in SEM-WDS mode — a Rule 6.5 conditional-applicability case.
- **`Dwell Time per Pixel` has a register entry** in `KEYED_BY_TECHNIQUE_DEPENDENT` reading *"analyte
  only where compositional mapping exists"*. It needs rewriting.
- **`Background Position(s)`** was `analyte > background position` until that was retired 2026-08-11
  under 7.4c. With `channel` now real, the background offsets are properties of the channel — Jia's
  Table 4 carries Bg− and Bg+ as columns of the setup row.

---

### C2. Test 2 — `Mass Resolution per Analyte` is `channel`

**Question.** Is mass resolution assigned per element or per mass in SF-ICP-MS?

**Answer: per channel. One procedure assigns two resolutions to a single nuclide.**

| Procedure | Assignment | Reading |
|---|---|---|
| Willbold 2005 | LR: Rb, Sr, Y, Zr, Nb, Cs, Ba, La–Nd, Hf, Ta, Pb, Th, U / HR: Eu–Lu | per element |
| Milne et al. 2010 | MR: ⁵⁵Mn, ⁵⁷Fe, ⁵⁹Co, ⁶²Ni, ⁶⁵Cu, ⁶⁸Zn / LR: ¹¹¹Cd, ²⁰⁷Pb | per element |
| Lu et al. 2007 | MR for ⁴⁷Ti, ⁴⁹Ti, ⁹³Nb | per element |
| **Misra et al. 2014** | LR: ⁷Li, ¹¹B, ²⁵Mg, ²⁷Al, **⁴³Ca**, ⁸⁷Sr, ¹¹¹Cd, ¹³⁷Ba, ²³⁸U / MR: ²³Na, **⁴³Ca**, ⁵⁵Mn, ⁵⁶Fe, ⁶⁶Zn | **⁴³Ca in both** |
| Desem 2022, Li 2016 | not stated | — |

⁴³Ca appears in both resolution lists — the *same nuclide* acquired at two resolutions, because Ca is
the denominator for every reported ratio and must be measured in each resolution pass. One analyte,
two channels, several reported properties.

**Decision: change `Mass Resolution per Analyte` from `analyte` to `channel`, and rename it** so the
field name does not embed the wrong key. Renaming triggers Rule 4 propagation across the 5 TAPPs that
carry it (LA-MC, LA-MC-UPb, LA-SF, LA-SF-UPb, Solution SF).

**Reasoning.** Three of six procedures are element-level and one is not. That is sufficient, by the
isomorphism precedent's own logic run in reverse: *declare the domain that does not collapse*. A key
that cannot represent Misra's table forces data loss; a key finer than needed yields 1:1 tables
elsewhere, which is harmless. 7.4a is satisfied — `channel` is already defined in these TAPPs by
`Monitored Isotopes` (`defines: channel per analyte`).

**Side finding.** All 7 LA-SF extractions record `N` for this field; those procedures use a single
resolution throughout. `Mass Resolution per Analyte` may not belong in the LA TAPPs at all. Worth a
look; not a blocker.

---

### C3. Test 3 — deferred

The matrix-element grey zone (elements fully calibrated but never reported) needs a set-difference
between the `Analyte` and `Reported Variables and Units` extractions per procedure — a different query
shape than `audit_keys_vs_literature.py` performs, so a small new script. It may also dissolve: the
clearest cases (internal standard element, IS-by-EPMA) are already classified as `channel` rather than
`analyte` under B1. **Deprioritised. Does not block the schema work.**

---

# Part D — Retrofit plan

Vocabulary fixes first (independent, low churn, keep the lint baseline clean), then the structural
change. Run `validate_tapp.py` after each step; expect 7.8.7 to fire on every changed row.

| # | Step | Files |
|---|---|---|
| 1 | Correct the 8 `Analyte` descriptions (B1) | 8 TAPPs |
| 2 | Unfreeze `Analyte` from the Column B PRINCIPLED register (`validate_tapp.py:240`) and re-triage. Add a guard: a `defines:` row may not be frozen as PRINCIPLED | validator |
| 3 | EPMA/SEM/SEM_Composition channel retrofit (C1); update the `Dwell Time per Pixel` register entry | 3 TAPPs, validator |
| 4 | `Mass Resolution per Analyte` → `channel` + rename (C2) | 5 TAPPs |
| 5 | Isomorphism survivors: `Counting Statistics Error`, `EDS Detection Limit` (B2) | 4 TAPPs |
| 6 | Rewrite the `channel` gloss in 7.2 (B3) | `conventions.md` |
| 7 | Add `sample` to `KEY_ANCHORS`; add the name-variant key-divergence check (B2) | validator |
| 8 | Rule 13; `Sample Name` → `defines: sample`; `Sample PID` → `sample`; add `Session Identifier` | 16 TAPPs, `conventions.md` |
| 9 | `sampling unit` → `sample > sampling unit` (A3); Group 2 per-sample audit (A4) | 16 TAPPs |
| 10 | Extend Rule 10 (A7); record A5's overlap note | `conventions.md`, `precedents.md` |
| 11 | Lift Parts A and B into `precedents.md`; re-lint to 0 ERROR / 0 WARN | skill dir |
| 12 | Version-bump all affected TAPPs, regenerate xlsx, re-sync `Current TAPPs/` (Rule 12) | all |

Steps 8 and 9 are the expensive pair and should be done together — both touch Group 2, and splitting
them would leave the library in a state where `sample` is a key with no definer.

---

# Part E — Not settled by this record

1. **Orientation as an axis.** AMS principal axes, seismic velocity anisotropy, thermal conductivity
   in foliated rock, EBSD. The axis is sample-side (relative to fabric), so `channel` fits awkwardly
   and `sampling unit` is wrong — a direction is not a subdivision. Raise at Phase 0 of the first
   anisotropy TAPP, per 7.7.
2. **Phase identity in XRD.** A Rietveld phase is admissible as `analyte` under B1, is listed under
   `model component` in 7.2, and its abundance is a `reported property`. Three keys with a claim on
   one domain, and `model component` is currently retired for want of a user. XRD will reopen it.
3. **Whether physical-property sweeps are archived per-step.** Decides whether `channel` is attested
   in those TAPPs at all, or whether the sweep stays a scalar description. Checkable against MagIC and
   PANGAEA without reading method papers.
4. **Test 3**, per C3.
5. **Session PID minting policy** — Astromat infrastructure, outside this record. A6 stands either way.
6. **Whether a `preparation batch` object is needed** — see A1's closing note.
7. **RESOLVED 2026-08-12 — `defines: channel per analyte` over-claimed totality.** Option (b) taken: the notation is unchanged and the parent key is documented as optional per row (conventions.md 7.3.1, and a `precedents.md` entry). The eight `Monitored Isotopes` descriptions were rewritten to match. Original statement of the problem follows.

   Added 2026-08-12 after the step 1
   patch. 7.3.1 glosses the form as *"one row per element"*, which asserts that every channel has a
   parent analyte. It does not. Desem et al. 2022 records `Monitored Isotopes` as
   `202Hg, 203Tl, 204Pb, 205Tl, 206Pb, 207Pb, 208Pb` for a procedure whose analyte is **Pb alone** —
   ²⁰²Hg is an interference monitor and ²⁰³Tl/²⁰⁵Tl are the internal standard. Makishima et al. 2011
   (¹⁴⁹Sm) and Lu et al. 2007 (⁹³Nb) show the same. The grouping axis is really the *element of the
   mass*, and elements-of-monitored-masses is a strict superset of analytes.

   Three options, none decided: **(a)** `defines: channel`, with the analyte grouping as a nullable
   attribute of the channel table — matches the data and what the JSON schema needs, but removes the
   binding from Column I; **(b)** keep `defines: channel per analyte` and amend 7.3.1 to say the
   parent key applies *where one exists*, not as a totality claim — one line, keeps the binding
   visible; **(c)** split analyte masses from monitor masses into separate fields — rejected, the run
   table is one list.

   Note this partly vindicates the schema developers' original proposal that channels need an
   `analyte` column: 7.3.1 covers the total case, not the partial one. The same question will arise
   for EPMA's `WDS Spectrometer Channel` under C1 the moment a spectrometer is used for a
   standard-only or background-only measurement.
8. **One optional literature addition:** Jia is a Cameca SXFive and publishes the full setup table;
   Batanova is a JEOL JXA-8230 and does not. A JEOL-based trace-element EPMA paper with an equivalent
   table would confirm the parameter set is vendor-independent before step 3 hard-codes which fields
   are per-channel. Reassurance, not a requirement.
