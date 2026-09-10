# Proposal: `monitored property` — a third layer between determinand and output

**2026-09-10.** Adds one anchor key (`monitored property`), one secondary key (`detector`), and two
fields. Re-keys 95 field-instances. Retires no key and changes no key's definition. Three sandbox
runs behind it; results in §5. Originated in a question about what `channel` actually addresses,
after `acquisition pass` (2026-09-08) removed part of the load `channel` had been carrying.

---

## 1. The defect: `channel` addresses two different things

Two fields in the same TAPP, both keyed `channel`, repeating over demonstrably different domains:

| Field | What the literature attests |
|---|---|
| `Faraday Cup Amplifier Resistor Values` | `All cups: 10¹¹ Ω; L1: 10¹³ Ω (234U)` — **per cup** |
| `Instrument Sensitivity` | `10 V for 140Ce, 4 V for 142Nd, 3.5 V for 152Sm` — **per mass** |

In static multicollection cup and mass are 1:1, so the conflation is invisible. It diverges in two
places the library already documents: multi-dynamic MC procedures, where one cup reads several
masses across steps, and single-collector Q/SF, where one detector reads every mass.

The second case is a live over-declaration. `Ion Counter Dead Time` is keyed `channel` in all nine
ICP-MS TAPPs, which in a single-collector instrument asserts *one dead time per mass*. There is one
detector and therefore one dead time.

**The same conflation, in the electron-beam TAPPs, produced a set-valued address.** `WDS Spectrometer
Channel` enumerates `Si=Sp1; Ti=Sp2; Cr=Sp2+Sp3 (aggregate intensity counting); Fe=Sp3`. `Cr=Sp2+Sp3`
is *one* monitored thing on *two* physical positions, so the channel identity cannot be modelled as
`spectrometer x element` — the only place in the library where an address resists a product form.
That is not an EPMA quirk; it is the hardware axis and the measurand axis being written into one cell.

---

## 2. The model

Three layers, of which the library has two:

```
target species        what the procedure DETERMINES          Rb, Sr
  |
monitored property    what it MEASURES to determine it       85Rb, 86Sr, 87Sr, 83Kr, 167Er2+
  |
reported property     what it REPORTS                        87Sr/86Sr, 87Rb/86Sr, isochron age (Ma)
```

Plus one hardware axis, orthogonal to all three: `detector` — the cup, spectrometer or counter.

**The worked example that produced this** (user's framing, retained because it is the clearest
statement of the model). To design an LA-MC-ICP-MS procedure measuring Rb and Sr: specify the target
species (Rb, Sr); for each, the monitored properties needed to determine it (Rb isotopes, Sr
isotopes, isobaric interference masses); and for each monitored property, which acquisition pass it
was measured in, which cup it was assigned to, what hardware configuration applied, and what
processing method was used. For EELS: for each target species, which edge is used.

**Why the middle layer is not the same as either neighbour.** It is not `target species` — interference
monitors and internal standards are monitored and never determined (⁸³Kr, ¹⁶⁷Er²⁺, ¹⁷³Yb²⁺ in Zhang
et al. 2022). It is not `reported property` — ⁸⁷Sr/⁸⁶Sr is computed from two monitored properties and
is one row of output, not two rows of measurement.

**Why it is not `channel` either.** `channel` is *"the address, not the signal"* — a position on a
swept or selective axis, and its test is *"does the position exist even with zero signal there?"*
Three cases separate them:

| | monitored property | address |
|---|---|---|
| mass shift | Te, via TeO⁺ | m/z 141 |
| doubly charged | Er | m/z 83.5 |
| aggregate counting | Cr | Sp2 **and** Sp3 |

In a mass spectrometer the two are near-isomorphic, which is why one key has served so far. They are
not the same axis.

---

## 3. Survey: what is keyed `channel` today

**25 fields, 113 field-instances, plus 13 compound definers.** Classified by the shape of what they
repeat over:

| Shape | Fields | Attested cells |
|---|---|---|
| the measured mass (detector irrelevant) | Interfering Species, Interference Correction Method, Instrument Sensitivity, Dwell Time per Mass | 110 |
| mass within a pass | Integration Time per Cycle, plus subsets of the row above (Interference Correction Method in MC, Dwell Time per Mass in SF) | 13 *(the field not already counted)* |
| precursor → product transition | the 5 collision/reaction-cell fields | 23 |
| spectrometer assignment (a set) | 9 electron-beam fields | 20 |
| element + edge | 2 EELS fields | 1 |
| **hardware** | Faraday resistor values, Faraday gain calibration, Ion Counter Dead Time, Proportional Counter / Detector | **7** |

**The asymmetry is the argument.** The measurand side carries **167** attested cells across 21 fields;
the hardware side carries **7** across 4, six of them in one field. So the split is `channel` → `monitored property` for 21 fields
and → `detector` for 4, not a redefinition of `channel` toward hardware.

**The first four shapes are one axis.** Shape 2 is shape 1 with the pass factored out — which
`acquisition pass` now does, and already did for `Mass Resolution Assignment` on 2026-09-08 (Milne et
al. 2010: `MR (R ~4000): 55Mn, 57Fe, 59Co…; LR (R ~300): 111Cd, 207Pb`). Shape 3 is shape 1 where the
measured mass differs from the determined one. Shape 5 is shape 1 with a non-mass identity. Shape 4
is shape 1 with the hardware extracted — which is what this proposal extracts.

---

## 4. What each family declares

| Family | `defines: monitored property per target species` | demoted to attribute, keyed `monitored property` | `defines: detector` |
|---|---|---|---|
| MC-ICP-MS (3) | `Monitored Masses` — **add to Solution MC** | `Collector Configuration` | `Faraday Cup Array Configuration` |
| Q / SF (6) | `Monitored Masses` — already present | — | *none — single detector* |
| EPMA / SEM (3) | **`Monitored Elements` — new field** | `WDS Spectrometer Channel`, `X-ray Line`, `Diffracting Crystal`, `WDS PHA Setting` | `WDS Spectrometer Configuration` |
| TEM (1) | `EELS Edges` — already present | — | *none* |

**Two existing fields are promoted, not invented.** `Faraday Cup Array Configuration` and `WDS
Spectrometer Configuration` both sit at `(none)` today and both already enumerate the hardware —
*"nine Faraday cups fitted with 10¹¹ Ω resistors, array spans L4 to H3"*, *"5 Rowland-circle WDS
spectrometers, crystal range LDE1-LIFH"*.

**This dissolves a registered divergence rather than adding one.** `Monitored Masses` is currently
`defines: channel per target species` in the six single-collector TAPPs but demoted to a plain
`target species` consumer in LA-MC, and absent from Solution MC. The register records the reason:
*"defines: channel per target species where there is no collector array; target species where the cup
array defines the channel."* Once the cup array defines `detector` instead, that entry has no cause
and goes dormant.

**Ion Counter Dead Time becomes technique-dependent, and correctly so**: `detector` in the three MC
TAPPs, `(none)` in the six single-collector ones. One register entry, with the rationale being the
over-declaration named in §1.

**The definer names stay technique-specific** — `Monitored Masses`, `Monitored Elements`, `EELS Edges`
— while the key is uniformly `monitored property`. This follows `Reported Variables and Units`, which
defines `reported property` without bearing its name. Recorded so that a later harmonisation pass
does not merge the three names on the mistaken view that one key needs one field name.

---

## 5. Sandbox results

Three runs on disposable copies of the library. Each began by reproducing the live baseline exactly
(0 ERROR / 0 WARN / 39 INFO) before mutating.

**Run 1 — collapse everything to one key named `monitored mass`.** 265 cells, 29 files, 27 compound
definers flattened. Result **0 ERROR, 1 WARN**: `rule7-unused-definer` on TEM's `Target Species`,
whose only `target species` consumer was `EELS Edges`. Rejected on three counts — the name is a
misnomer for the twenty-odd planned TAPPs whose dispersive axis is not a mass (Raman cm⁻¹, XRD 2θ, XANES and
XPS eV, Mössbauer velocity, NMR frequency, EPMA and XRF X-ray wavelength, EELS energy loss); the
mass→element binding is lost in 27 cells and 7.3.1 forbids reconstructing it by parsing; and the
hardware conflation of §1 survives untouched.

**Run 2 — the three-layer model.** First pass: **9 ERROR**, all `rule7-undefined-domain` on
`detector`, and self-diagnosing — 6 single-collector TAPPs declaring it for `Ion Counter Dead Time`
with nothing to enumerate, and 3 electron-beam TAPPs with no spectrometer enumerator. Applying the
two fixes in §4 (dead time → `(none)`; promote `WDS Spectrometer Configuration`) left one
`keyed-by-divergence` WARN on `Ion Counter Dead Time`, which the technique-dependent register
absorbs. **Final: 0 ERROR / 0 WARN / 40 INFO.**

**Run 3 — assignment as attribute** (`Collector Configuration` demoted, `Monitored Masses` promoted).
**1 ERROR**: Solution MC-ICP-MS has 10 `monitored property` consumers and no definer, because the
field is absent from that TAPP. That single error is the whole cost of §4's first row.

**`channel` drops to zero field-instances** across all 16 TAPPs. This is not a 7.4c violation:
*"7.4c constrains definers without consumers, not vocabulary without users"* — the state `sample`
occupied between 2026-08-12 and Rule 13.

---

## 6. The EPMA assumption, and its falsifier

`Monitored Elements` is **element-grained**, with the X-ray line as an attribute keyed to it, rather
than enumerating (element, line) pairs. That is a choice, and it rests on thin evidence.

**What the corpus says.** Only 2 of 15 EPMA procedures state X-ray lines at all — both Ma (Caltech),
both strictly one line per element: `SiKα, AlKα, CaKα (anorthite); NaKα (albite); FeKα (fayalite)…`.
`lit_assessment.md` already warns that lines are routinely unstated and must not be inferred. So this
is *no falsifier found*, not *well evidenced*.

**The one adjacent case does not falsify it.** Hu et al. 2020 records `Cr Kβ on Mn Kα` under
`Interfering Elements`. That names the interfering line, but in Probe for EPMA the correction is
computed from the Cr Kα intensity; nothing states Cr Kβ was separately measured.

**The falsifier, named and narrow: an EPMA procedure measuring one element on two X-ray lines as
separate measurements.** S Kα + S Kβ for sulfur speciation, or Kα + Kβ of one element to calibrate an
overlap correction — both real practice. If one is attested, `Monitored Elements` must move to
(element, line) pairs and `X-ray Line` stops being an attribute. Nothing else in this proposal
changes if that happens; the grain of one definer does.

**Why element-grained is preferred meanwhile.** Making the (element, line) pair the identity puts the
line inside its own address, so `X-ray Line` becomes a field keyed by a domain it partly constitutes.
Element-grained keeps `X-ray Line`, `Diffracting Crystal` and `WDS PHA Setting` as what they are —
attributes of the thing being monitored.

**Rejected name: `Monitored Species`.** In EPMA its membership would be `Si, Ti, Cr, Fe…`, nearly
identical to `Target Species`, sitting in the same group. That is the failure repaired on 2026-09-09,
when a `Target Species` cell was found holding `Collector Configuration` content: two adjacent fields
with confusable roles produce a plausible-looking list in the wrong field, and the error is
unrecoverable without re-reading the source. `monitored species` also carries the 2026-08-12 rejection
of a *merge* proposal, which does not apply to a third layer but does make the term ambiguous in the
record.

---

## 7. What this proposal does NOT do

**It does not retire `channel`.** No field will be keyed by it in the current 16 TAPPs, but twenty-odd
planned techniques sweep an axis with no discrete measurand — Raman spectral bins, DSC
temperature setpoints, demagnetisation field steps, Mössbauer velocity channels. Whether those want
`monitored property` or a genuine swept-axis key is a question for the TAPPs that have the evidence.
Held, not decided.

**It does not fill the foreign-key gap.** Once `Collector Configuration` is keyed `monitored property`,
its *values* are cup labels — members of the `detector` domain. Column I says what a field repeats
over, never what its values reference, so a schema generator must infer the join from Column B. The
same applies to `WDS Spectrometer Channel`. A notation (`monitored property -> detector`) was
considered and is **not** proposed: no consumer has asked, and 7.4b/c exist to stop keys and grammar
being minted ahead of users. Recorded so the question is not reopened from scratch.

**It does not re-extract anything.** Every re-key here is a Column I change. The one content change is
`Monitored Elements`, a new field with no attested cells until Phase 3 revisits the EPMA corpus.

---

## 8. Cost

| | |
|---|---|
| `channel` → `monitored property` | 95 field-instances |
| `channel` → `detector` | 12 |
| `channel` → `(none)` | 6 — the dead-time over-declaration, corrected |
| compound definers re-keyed | 13 |
| existing fields promoted to definers | 2 |
| **new fields** | **2** — `Monitored Masses` in Solution MC; `Monitored Elements` in EPMA/SEM/SEM_Composition |
| technique-dependent register entries | 1 added (`Ion Counter Dead Time`), 1 goes dormant (`Monitored Masses`) |
| validator | add `monitored property` to `KEY_ANCHORS`, `detector` to `KEY_SECONDARY` |
| key audit | its axis detector emits only the label `channel`; needs the new labels or it reports every re-keyed field as `AXIS-MISMATCH` (4 such artifacts in runs 2 and 3) |

Column I is module-owned, so this is a module edit plus a recompose of all 16 TAPPs, not a TAPP-level
patch. `Monitored Elements` is a Rule 6 admission decision and should be taken separately from the
re-key.

---

## 9. What would reverse this

- **An EPMA procedure measuring one element on two lines** — §6. Changes one definer's grain, not the model.
- **`detector` failing 7.4c on evidence.** Its consumer set is 4 fields and only `Faraday Cup Amplifier
  Resistor Values` is attested per-cup (6 cells). `Ion Counter Dead Time`, `Proportional Counter /
  Detector` and `WDS PHA Setting` have **zero** attestations in the whole corpus. If a survey of the MC
  literature finds no second per-cup field, `detector` is carrying one evidenced consumer, and the
  honest response is to hold it and leave those four on `monitored property` until a falsifier appears.
- **A schema consumer that cannot join `Collector Configuration` to the cup domain** — §7. That would
  make the foreign-key notation a requirement rather than a speculation.
