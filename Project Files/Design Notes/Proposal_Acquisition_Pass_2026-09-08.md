# Proposal: reopen `acquisition pass` — survey and key-assignment impact

**2026-09-08, revised the same day** (§4A definer resolved, §4B scope constraint added, §2 count
corrected). Follows conventions.md **7.12.1** (2026-09-01), which scoped the reported-data test to
Phase 3 validation and removed it as a Phase 0 gate. `acquisition pass` was retired 2026-08-11 and
declined twice on 2026-08-31, on three arguments: retired-by-rule; *"two users still do not justify
reviving an abstraction 7.4b/c removed for want of any"*; and the reported-data test. The third no
longer applies at Phase 0. **This note tests the second, which is a count.**

---

## 1. It is not a noble-gas peculiarity

Six planned techniques are `A3` multi-pass in the 2026-09-01 landscape note (Solution SF, LA-SF, static
NGMS, TIMS, gas pycnometry, INAA), plus MC-ICP-MS as a variant. More to the point, **multi-pass
acquisition is already attested in the built library**, in four TAPPs:

| TAPP | procedure | passes |
|---|---|---|
| LA-SF-ICP-MS (+UPb) | Chernonozhkin et al. 2021, line scan | pre-ablation, Run 1 (major), Run 2 (trace) |
| Solution SF | Misra et al. 2014 | LR + MR |
| | Milne et al. 2010 | MR + LR |
| | Willbold 2005 | LR + HR |
| | Desem et al. 2022 | deflector peak jump |
| Solution MC | Hopp et al. 2021 | MR-mode + HR-mode |
| | Hu et al. 2022 | main configuration + subconfiguration |
| | Nowell et al. 2008 (Nu Plasma) | two-sequence static multi-collection |
| | Barnes et al. 2025 | two cup configurations |
| Solution Q | Gil-Diaz et al. 2020 (iCAP-TQ) | KED (He) + ICP-MS/MS O2 mass-shift |

## 2. Survey result

Scanning every literature-assessment cell in the 16 live TAPPs for two or more named acquisition
configurations in one cell, excluding preparation-side stepping (already keyed `preparation step`):

**39 (field, key) pairs · 69 cells · 4 TAPPs.**

### The fullest case: Chernonozhkin et al. 2021, LA-SF-ICP-MS line scan

**25 fields carry run-structured values, 21 of them keyed `(none)`. Of those 25, 21 genuinely
DIFFER between runs; at least 4 are stated per run with identical values** —
`Make-up Gas and Flow Rate` ("0.947 l min⁻¹, run 1 and run 2"), `Coolant (Plasma) Gas Flow Rate`,
`Analysis Sequence` ("same structure for run 1 and run 2") and `Signal Integration Time`
("Run 2: same structure"). Those four are evidence that the *researcher* thinks in passes, not that
the *field* varies by pass; under 7.3.2 they would be keyed only if some procedure attests a
difference. **The defensible consumer count is ~21, not 25.** The passes differ in:

- **laser hardware** — spot 30 µm vs 130 µm; repetition rate 20 vs 40 Hz; transect vs spot; transect rate
- **mass spectrometer** — MR (M/ΔM 4000) vs LR (300); Faraday used only in Run 1; dwell/duty cycle
- **calibration and reduction** — Run 1 sum-of-oxide normalisation vs Run 2 single-element IS; expanded
  GRM set for Run 2
- **session structure** — 3 replicates of each run; background scans per run

And a **data dependency between passes**:

> `Internal Standard Element` — "Run 1: No single IS; oxide sum normalization; **Run 2: ⁵³Cr
> (concentration from Run 1 major-element analysis on 30 µm spot used as IS for 130 µm spot transect)**"

Run 1's *output* is Run 2's *input*. Nothing in the current structure can express that.

Two further cases show the pass reaching outside acquisition entirely:

> **Hopp et al. 2021** — `Desolvation System`: "ESI Apex Ω for HR-mode dry plasma work; **none** for
> MR-mode wet plasma". `Plasma Thermal Mode`: "either a cyclonic glass spray chamber (wet plasma,
> MR-mode, Pt cones) or an ESI Apex Ω desolvating nebulizer (dry plasma, HR-mode)".
>
> **Willbold 2005** — `Final Solution Matrix`: "0.4 mol/l HNO₃ (**dilution factor ~21000 for LR, ~1000
> for HR**)".

A spray chamber and a dilution factor are not properties of a mass channel. **A pass is a sub-procedure**,
with its own introduction path, plasma condition, dilution, laser settings, resolution, calibration
strategy and cycle count.

---

## 3. Does this change the assignment of current keys?

**No key needs replacing, and no key's definition changes.** The impact sorts into three categories.

### A — currently `channel`, value is per-pass: **no change needed** (8 fields, 12 cells)

`Dwell Time per Mass`, `Integration Time per Cycle`, `Instrument Sensitivity`,
`Interference Correction Method`, `Mass Resolution Assignment`, `Collision/Reaction Cell (CRC)
Configuration`, `Collision Gas Type`, `Reaction Product Ion / Mass-Shift Transition`.

An acquisition pass is **coarser** than a channel, so a per-pass value is representable as a per-channel
value with repeats. Rule **7.3.2** already governs this and points the same way: *"declare the finest
key that the literature attests, unconditionally… under-declaring is lossy."* Over-declaring yields 1:1
tables, which the rule calls harmless.

Cost of leaving them: the *fact* that a value is uniform within a pass is not recoverable. Misra states
two dwell times; the current key asks for fourteen.

### B — currently `(none)`, value is per-pass, **not representable as any existing key** (25 fields, 46 cells)

This is the finding. A laser spot diameter, a desolvation system, a plasma mode, a dilution factor and
an internal-standard strategy are not properties of a `channel`, a `target species`, a `sampling unit`,
a `standard`, a `reported property` or a `sample`. **`(none)` loses the information outright**, which is
precisely the error 7.3.2 calls lossy.

Representative members: `Mass Resolution Setting`, `Laser Spot Geometry`, `Laser Repetition Rate`,
`Laser Spot Path / Ablation Mode`, `Transect Rate`, `Laser Fluence`, `Detector Configuration`,
`Desolvation System`, `Plasma Thermal Mode`, `Final Solution Matrix`, `Internal Standard Approach`,
`Internal Standard Element`, `Elemental Fractionation Correction`, `Signal Integration Time`,
`Background Count Time`, `Number of Scans per Replicate`, `Number of Cycles per Block`,
`Number of Replicates`, `Pulse/Analog Detector Nonlinearity Correction`, `Analysis Sequence`.

**This is the 7.4c consumer set, and it is ~25 fields, not two.** The count argument that carried the
2026-08-31 declines does not survive it.

### C — the definers: **a notation collision that must be settled first** (6 fields, 11 cells)

| field | current key | what the pass does to it |
|---|---|---|
| `Monitored Masses` | `defines: channel per target species` | Misra partitions the domain LR / MR |
| `Collector Configuration` | `defines: channel per target species` | Nowell, Barnes, Hu partition it by configuration |
| `Target Species` | `defines: target species` | Chernonozhkin partitions it Run 1 / Run 2 |

Expressing both groupings needs `defines: channel per (target species × acquisition pass)` — which
Rule **7.3.1 explicitly refuses**; `validate_tapp.py` raises `rule7-compound-definer-key` as an **ERROR**.

### RESOLVED 2026-09-08 — the collision dissolves; no grammar change is needed

**Containment is declared on CONSUMERS, never on definers.** That is the whole answer, and the library
already demonstrates it:

```
Sample Name        defines: sample            <- definer, plain
Sampling Unit      defines: sampling unit     <- definer, plain
...consumers...    sample > sampling unit     <- 46 rows carry the containment
```

No definer in the library carries a containment. So `acquisition pass > channel` is expressed where
fields are keyed, and **`Monitored Masses`, `Collector Configuration` and `Target Species` do not change
at all.** The compound-definer refusal in 7.3.1 stands untouched — it was never the obstacle.

**Does containment actually hold?** 7.3's test is that **B must be unenumerable without A**, and the
library's own worked rejection is instructive: `target species > channel` was refused because *"m/z 238
is a position on the instrument axis and exists independently of any target species."*

The parallel **fails for the pass**, which is why the two cases differ:

| | `target species > channel` | `acquisition pass > channel` |
|---|---|---|
| is the parent external to acquisition? | **yes** — Fe is a chemical fact | **no** — the pass *is* acquisition configuration |
| can a channel exist without the parent? | **yes** — interference monitors and internal standards are analyte-orphans (¹⁸²W, ²⁰²Hg, ⁴³Ca) | **no** — every channel is acquired in exactly one pass |
| verdict | containment refused, `per` used instead | **containment holds** |

A channel is the acquisition **slot**, and the slot `LR/⁴³Ca` is *created by* the LR pass — it is not a
pre-existing position the pass happens to visit. Misra's ⁴³Ca proves it: the same mass yields two
slots because there are two passes. Hence the parent is **NOT NULL** for the pass and **nullable** for
the target species — the asymmetry the two rows above record.

### What actually changes

| | |
|---|---|
| `Monitored Masses` | **unchanged** — `defines: channel per target species` |
| `Collector Configuration` | **unchanged** — `defines: channel per target species` |
| `Target Species` | **unchanged** — `defines: target species` (the domain is the union; the pass partitions it) |
| **new** `Number of Acquisition Passes` | `defines: acquisition pass` |
| the ~21 pass-only consumers (§3B) | `acquisition pass` |
| channel-keyed consumers (§3A) | **stay `channel`** under 7.3.2 — the pass is coarser |
| a field taking one value per channel *within* each pass | `acquisition pass > channel` — available, possibly with no initial users |

⚠ **Side finding.** The 7.3 notation table still reads *"No field in the current library uses
nesting"*. That is **stale**: `sample > sampling unit` carries **25 rows** and
`sample > sampling unit x reported property` a further **21** — 46 in total, since Rule 13. Corrected in
conventions.md in the same pass.

---

## 4. The precedent that decides the shape

**The library already has a serial-step key: `preparation step`.**

```
Number of Digestion Steps   defines: preparation step   Solution MC / Q / SF
Digestion Acid(s)           preparation step            Solution MC / Q / SF
Digestion Duration          preparation step            Solution MC / Q / SF
Digestion Temperature       preparation step            Solution MC / Q / SF
```

One definer, three consumers, three TAPPs — an ordered, non-reorderable step axis on the **preparation**
side. `acquisition pass` is its exact counterpart on the **acquisition** side, with a larger consumer
set. If the shape is legitimate before the instrument, the argument that it is illegitimate inside the
instrument needs to be made explicitly rather than assumed.

---

## 4A. The definer must be new and neutral

`Multi-Run Sequential Analysis Design` **cannot serve**, for a hard reason as well as a conceptual one.

**Rule 7.4a requires a definer in every TAPP that uses the key.** It exists in the six LA TAPPs and is
**absent from all three Solution TAPPs** — where **six of the ten attested multi-pass procedures live**
(Misra, Milne, Willbold, Desem, Hopp, Hu, Nowell, Barnes, Gil-Diaz). Its wording is LA-specific too:
*"multiple sequential runs on the same sample **location** … key **laser** and instrument settings"*,
which does not describe a solution procedure at all.

**And a content field cannot be the definer in principle.** Researchers run passes for different
reasons — resolution in Misra, cup array in Nowell, cell chemistry in Gil-Diaz, plasma mode in Hopp,
spot size and internal-standard strategy in Chernonozhkin. No single content field is present in, or
distinguishing for, all of them. The definer must be neutral about *what* varies.

**The library already has that pattern.** `preparation step`'s definer is **`Number of Digestion
Steps`** — a *count* field, with the steps described inline, presuming nothing about what distinguishes
them. The acquisition-side parallel is **`Number of Acquisition Passes`** (named to match; an ordinal
per row is what Column I already supplies).

`Multi-Run Sequential Analysis Design` then becomes a **consumer** — and possibly a redundant one, since
its content is "describe the passes". Whether it survives the Rule 6 admission test once a real definer
exists is a separate question.

---

## 4B. What constrains which fields may be keyed by a pass

If a pass is a sub-procedure, does every field become pass-keyed by default? **No** — and the boundary
is empirical, not asserted. Sorting the 69 surveyed cells by group:

| group | pass-structured fields |
|---|---|
| **1. Procedure Identification** | **0** |
| 2. Samples | 1 |
| 3. Instrument & Software | 3 |
| 4. Measurement Information | 24 |
| 5. Data Processing | 9 |
| 6. Quality Control & Uncertainty | 2 |

**Group 1 is empty.** Nothing that identifies the procedure — name, DOI, author, laboratory, references,
coupling — varies between passes. **That is what makes a pass a sub-procedure rather than a separate
procedure.** A pass with its own DOI and author would be a different procedure.

The edges sharpen the shape rather than blur it. Group 3's three hits are all **settings**
(`CRC Configuration`, `Desolvation System`, `Mass Resolution Setting`) and never **identity**
(`Instrument Manufacturer`, `Model`, `Serial Number`, `Acquisition Software` are untouched). Group 2's
single hit is `Final Solution Matrix` — the dilution prepared *for* a pass — while `Sample Name`,
`Sample Persistent Identifier`, `Target Material` and `Sampling Unit` are untouched.

> **The constraint:** a field may be keyed `acquisition pass` iff it describes how the measurement is
> **configured, executed or reduced**. Fields that identify the **procedure, the sample, the session or
> the instrument** cannot be — they are what the passes share.

**No new machinery is needed to enforce it.** Every field is scoped by the procedure, and Column I never
records that, because the procedure is the *universal* scope and declaring it carries no information.
Column I records variation *within* a scope. The same applies one level down: declare the pass only
where the value varies, which is Rule **7.3.2** (declare the finest key the literature attests) checked
by Rule **7.12** (validate against extracted procedures). The corrected count in §2 is that test applied
to this survey.

---

## 5. Recommendation

1. **Admit `acquisition pass`** on 7.4a–c, at Phase 0, per 7.12.1. Consumers: ~21 fields across four
   built TAPPs (§2). **Definer: a new, neutral `Number of Acquisition Passes`** (§4A) — not
   `Multi-Run Sequential Analysis Design`, which fails 7.4a by being absent from all three Solution
   TAPPs and is LA-specific in wording.
2. ~~Settle the definer collision first (§3C).~~ **Done — see §3C RESOLVED.** No definer changes and
   no grammar change; containment is a consumer-side declaration.
3. **Re-key category B, leave category A alone.** A is already correct under 7.3.2.
4. **Re-examine the 2026-08-31 `Desolvation System` decline** on its own terms: Hopp's cell is per-pass,
   and the decline rested partly on the test 7.12.1 has since demoted.

## Open questions

- ~~Is `Multi-Run Sequential Analysis Design` the definer?~~ **Answered in §4A: no.** It becomes a
  consumer. Open successor: does it survive the Rule 6 admission test once `Number of Acquisition
  Passes` exists, or is it absorbed? It currently holds the whole design in prose — the same fidelity
  failure found in `Collector Configuration` (Decision_Record_2026-09-01, §3).
- Do the four "stated per run but identical" fields (§2) get keyed? Only if another procedure attests a
  difference — 7.3.2. Worth re-checking when the NGMS and TIMS literature is extracted.
- Does the pre-ablation pass in Chernonozhkin count as an acquisition pass, or as preparation? It uses
  the laser but produces no reported data.
- INAA's passes are separated by **days** (recounting as isotopes decay). Same key, or a different axis?
- How is a cross-pass data dependency (Run 1's Cr as Run 2's internal standard) recorded at all?
