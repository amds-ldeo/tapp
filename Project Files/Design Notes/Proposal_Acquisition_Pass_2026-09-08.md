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

### A — currently `channel`, value is per-pass: **7 stay, 1 is re-keyed** (8 fields, 12 cells)

`Dwell Time per Mass`, `Integration Time per Cycle`, `Instrument Sensitivity`,
`Interference Correction Method`, `Collision/Reaction Cell (CRC) Configuration`, `Collision Gas Type`,
`Reaction Product Ion / Mass-Shift Transition` — **stay `channel`**.

An acquisition pass is **coarser** than a channel, so a per-pass value is representable as a per-channel
value with repeats. Rule **7.3.2** already governs this and points the same way: *"declare the finest
key that the literature attests, unconditionally… under-declaring is lossy."* Over-declaring yields 1:1
tables, which the rule calls harmless.

Cost of leaving them: the *fact* that a value is uniform within a pass is not recoverable. Misra states
two dwell times; the current key asks for fourteen.

#### ⚠ Two exceptions — `Mass Resolution Assignment` and `Sequence`

It was listed here in the first draft. It does not belong, and the discriminating question is whether
the value **can vary between channels within a single pass**:

| field | can it vary within one pass? | verdict |
|---|---|---|
| `Dwell Time per Mass` | **yes** — Lu et al. 2007 gives ⁴⁷Ti/⁴⁹Ti a specific dwell, all inside MR | `channel` is genuinely exercised → **stays** |
| `Mass Resolution Assignment` | **no, never** — the pass *is* the resolution setting for its masses | → **`acquisition pass`** |
| `Sequence` (EPMA, added 2026-09-08) | **no** — it *names* the passes: "pass 1 = Mg, Al, Fe, Ca, Ti; pass 2 = Na, Si, Mn, K, Cr" | → **`acquisition pass`**, and a candidate pass definer for EPMA |

For every other category-A field, `channel` over-declares in a way some procedure *does* exercise. For
`Mass Resolution Assignment` it over-declares in a way that **can never** be exercised, because
uniformity within a pass is definitional rather than incidental. That is a re-key, not a tolerable
over-declaration — and it moves the field from the finest key that is attested to the finest key that is
*possible*, which is what 7.3.2 actually asks for.

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

### Does containment actually hold? Four checks

First, what the three forms mean, because they are different mechanisms in different places:

| form | meaning | side |
|---|---|---|
| `A > B` | **containment** — B exists only within A | **consumer** — how a field's values are indexed |
| `A x B` | **cross-product** — A and B are *independent*; one value per combination | **consumer** |
| `defines: A per B` | a **definer** whose child table carries a parent FK | **definer** — one `per` slot each |

`Monitored Masses` already spends its one `per` slot on `target species`. Containment is never written
on a definer, so it does not compete for that slot. **That alone dissolves the collision**; the four
checks below establish that containment is also the *correct* form.

Rule 7.3's stated test: **"Can you enumerate B without reference to A? No → `>`. Yes → `x`."**

**1 — The definition already puts the pass inside the channel's identity.** Rule 7.2's own examples of a
channel are *"m/z 238; **cup L2 at magnet step 1**; Fe Kα on LIF spectrometer 2; Fe L₂,₃ edge…"*. The
acquisition step is already part of what names a channel, decided long before this discussion.

**2 — Enumerability fails, concretely.** Misra's channel domain is `LR: 7Li 11B 25Mg 27Al 43Ca 87Sr
111Cd 137Ba 238U` + `MR: 23Na 43Ca 55Mn 56Fe 66Zn`. Strip the passes and **13 distinct masses remain
against 14 channels** — ⁴³Ca collapses and the missing one cannot be recovered without knowing the
passes. That is the test failing.

**3 — It is not a cross-product.** `x` requires *independent* domains, one value per combination. Two
passes × 13 masses would be **26**; only **14** exist, and which 14 the pass determines entirely.
Independent domains do not produce that sparsity; contained ones do.

**4 — The orphan asymmetry**, the cleanest single discriminator. **Analyte-orphan channels exist** —
¹⁸²W and ¹⁸⁵Re in Nowell's cup array, ²⁰²Hg and ²⁰³Tl in Desem, ⁴³Ca in Misra: monitored, never
determined. A container cannot have members belonging to nothing, so the analyte is a nullable *parent*,
not a container — which is exactly why `target species > channel` was refused and `per` used instead.
**Pass-orphan channels cannot exist**: every channel is acquired in exactly one pass, so the FK is
`NOT NULL`. That is what a container looks like.

**The counter-argument, and why it loses.** One could argue `channel` is the *mass* (13 of them) and
pass × mass is merely a sparse cross-product. It loses on check 1 — the library defined a channel as the
acquisition *address*, not the mass — and on the evidence behind that: in Misra,
`Mass Resolution Assignment` and `Dwell Time per Mass` take **different values for LR/⁴³Ca and
MR/⁴³Ca**. One channel would need two values for one key, the exact failure the 2026-08-12
`Mass Resolution Assignment` re-keying was made to avoid.

**The degenerate case does not break it.** In Lu et al. 2007 there is one pass, so the channels
enumerate fine without it. In a single-sample session the sampling units also enumerate fine without the
sample, and `sample > sampling unit` is still the key on 25 rows. **Containment is a statement about the
structural relationship, not about how many members the outer domain happens to have.**

Summarised against the library's own rejected case:

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
| channel-keyed consumers (§3A) | **7 stay `channel`** under 7.3.2 — the pass is coarser |
| `Mass Resolution Assignment` (§3A) | **re-keyed to `acquisition pass`** — cannot vary within a pass |
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

## 4A. The definer: neutral, domain-named, and EPMA already has it

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

### The definer ENUMERATES the passes; it does not count them — corrected 2026-09-08

An earlier draft proposed **`Number of Acquisition Passes`**, taking `preparation step`'s definer
`Number of Digestion Steps` as the pattern to copy. **That was the wrong lesson**: it is the shape to
avoid, and the library shows why.

**Nine of the ten definers are named for their domain** — `Target Species`, `Sampling Unit`,
`Monitored Masses`, `Collector Configuration`, `EELS Edges`, `Sample Name`, `Reported Variables and
Units`, `Secondary Reference Materials`, `WDS Spectrometer Channel`. `Number of Digestion Steps` is the
sole count-named one, and one of its cells reads:

> **"Two ('These steps were performed twice')"**

A count with **no member identities at all** — yet `Digestion Acid(s)`, `Digestion Duration` and
`Digestion Temperature` are all keyed `preparation step` and must point at members. In that procedure
they have nothing to anchor to. Li et al. 2016 *does* enumerate ("2 (step 1: 6M HCl + 8M HNO₃…; step 2:
evaporate + re-dissolve…)"), so the field works when a curator goes beyond its name — **the name invites
the failure.**

> **Name a definer for its domain and curators enumerate; name it for its cardinality and they answer
> with a cardinality.** Fields keyed by a pass anchor to the *identity* of each pass, so the definer
> must establish those identities. The count falls out of the enumeration; the identities do not fall
> out of the count.

**The definer is therefore `Acquisition Pass`.** Its value enumerates: *"Pass 1 (LR); Pass 2 (MR)"*;
*"Pass 1 = Mg, Al, Fe, Ca, Ti; Pass 2 = Na, Si, Mn, K, Cr"*; *"Pre-ablation; Run 1 (major, MR, 30 µm);
Run 2 (trace, LR, 130 µm)"*.

⚠ `Number of Digestion Steps` is a latent defect of the same kind. It is **module-owned by
`Module_SolutionIntroduction`** (3 consumers), so renaming it is a separate module change — recorded,
not bundled here.

### EPMA already has this field, under the name `Sequence`

So the definer is not a new field everywhere — it is **one library-wide field that EPMA already carries
under a narrower name**. `Sequence` is TAPP-owned (no module owns it) and its Neuman cell is exactly a
pass enumeration: *"Two passes per stage map: pass 1 = Mg, Al, Fe, Ca, Ti; pass 2 = Na, Si, Mn, K, Cr."*

| TAPP | current key | extraction | proposed |
|---|---|---|---|
| EPMA | `channel` | **1 real of 15** | rename to **`Acquisition Pass`**, `defines: acquisition pass`, description rewritten |
| SEM | `channel` | **0 real of 35** | ⚠ see below |
| SEM_Composition | `channel` | **0 real of 9** | ⚠ see below |
| ICP-MS family | — | — | gains `Acquisition Pass` |

⚠ **The SEM snag — 7.4c.** If `Sequence` became `defines: acquisition pass` in all three, SEM would
carry a definer for a key it does not use, and 7.4c says a definer needs a consumer. SEM has no passes
(absent anchor: `WDS Spectrometer Channel` is `N/A` in all 44 SEM-family columns, and SEM-EDS collects
every channel simultaneously). Either retire `Sequence` from the SEM TAPPs — it is 0 real of 44 and
arguably `N/A` there — or leave it as `channel` and register the name divergence under 7.8.7. **Open.**

### A companion scalar, proposed but not settled

**`Number of Acquisition Passes`**, keyed `(none)` — neither a definer nor keyed by anything — to carry
the procedure's structure in a machine-readable form that a free-text enumeration does not. Precedent:
`Number of Blocks per Measurement` and `Number of Cycles per Block` are exactly this shape.

⚠ It faces the **same redundancy question already open for `Mass Resolution Setting`**: is a scalar
summary still needed once the passes enumerate themselves? Both should be answered together rather than
separately.

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

## 4C. Which TAPPs are affected — tested, not assumed

An earlier draft put this at 9 TAPPs by applying Rule 7.8.7 uniformity to the whole ICP-MS family.
**That was inference, not evidence.** Each family was then tested against its own literature, and the
answer moved in both directions.

| | TAPPs | basis |
|---|---|---|
| **Attested multi-pass** — key applies | LA-SF ×2, Solution SF, Solution MC, Solution Q, **EPMA** | 69 surveyed cells; EPMA via Neuman et al. 2025, **extracted 2026-09-08** (see below) |
| **Attested SINGLE-pass** — register as divergence | LA-Q ×2, LA-MC ×2, **TEM** | the question was asked *and answered* |
| **Absent anchor** (Rule 7.7) | SEM ×4, Lab-XCT | no dispersive sequence exists to have |

**~6 TAPPs, not 9.** Four LA variants move out; EPMA moves in.

### LA-Q and LA-MC: positive evidence, not a null

`Multi-Run Sequential Analysis Design` exists in both and was answered — **LA-Q 6 real of 7 columns,
every one "Single spot per location"** (Nakanishi 2022, Liu 2024, Liu 2025 ×2 …); LA-MC's single column
reads "Single line scan per location (1 block of 120 cycles)". These are not corpus gaps; the field was
asked and said *single*. They become registered divergences in `KEYED_BY_TECHNIQUE_DEPENDENT`, the same
treatment `Secondary Reference Materials` received.

⚠ **LA-MC rests on n = 1.** Re-check when its Phase 3 is extended — two further papers are already
listed as outstanding in its Phase 0 record.

### EPMA moves IN, on a paper the library already holds

EPMA's own fields say nothing: `Sequence` **0 real of 14**, `WDS Spectrometer Channel` **0 real of 14**.
But precedents.md already forbids reading that as evidence — *"all 14 are meteoritics and mineralogy
application papers, which do not publish the setup table, whereas method papers do."*

The positive evidence is in **Neuman et al. 2025**, currently extracted only into Lab-XCT:

> "**Two passes** were used to collect X-ray intensities for **Mg, Al, Fe, Ca, and Ti in pass 1, and Na,
> Si, Mn, K, and Cr in pass 2.** These mapping runs each required 18 hr per map…"

Two passes partitioning the target-species domain five and five — structurally identical to Misra's
LR/MR. `Sequence` (currently `channel`, *"order in which spectrometer assignments are acquired"*) is
really per-pass.

**EXTRACTED 2026-09-08 — `EPMA_TAPP_v62`, 16th literature column.** 86 cells, none blank, 37
substantive. `Sequence` moved from **0 real of 14 to 1 real of 15**, and now carries the two-pass
structure verbatim. The paper also gave EPMA its first method-grade values for `Pre-Analysis Imaging and
Screening`, `Dwell Time per Pixel`, `Step Size / Pixel Size`, `Map Dimensions`, `Stage Scan vs. Beam
Scan` and `X-ray Background Correction Method`. `Neuman2025` moved EPMA `N` → `Detailed` in the paper
registry.

⚠ **The extraction surfaced a Column B defect.** `Sequence`'s description reads:

> "Order in which spectrometer assignments are acquired during point analysis. **Not applicable to X-ray
> mapping, where all assigned spectrometers collect simultaneously at each pixel.**"

Neuman **is** X-ray mapping **and** has two passes. Both halves are true separately — within one pass
the fixed spectrometers do collect simultaneously at each pixel — but when the element count exceeds
the spectrometer count the whole map is run again. Ten elements on five fixed spectrometers requires
two passes. The description asserted a non-applicability the evidence disproves, the same shape of
defect as `Mass Resolution per Analyte`'s name asserting the key its evidence disproved.

**FIXED 2026-09-08** in all three carriers (EPMA v63, SEM v61, SEM_Composition v60 — the description was
byte-identical in all three, so they moved together under Rule 7.8.9). It now reads: *"Order in which
spectrometer assignments are acquired, and — where the element suite exceeds the number of spectrometers
— the passes the acquisition is divided into. Within a single pass all assigned spectrometers collect
simultaneously, including at every pixel in X-ray mapping; a suite larger than the spectrometer count
therefore requires the acquisition to be run more than once, each pass covering a different subset of
elements."* Column I was deliberately **not** touched — re-keying to `acquisition pass` belongs to this
proposal, not to a description fix.

⚠ **The audit will not surface this.** At 1 real of 15, `Sequence` sits below
`audit_keys_vs_literature.py`'s evidence threshold, so it reports no finding. The key change has to come
through this proposal, not through Rule 7.12 — a concrete instance of the 7.12.1 point that Phase 3
validation cannot be the gate on Phase 0 design.

### SEM: absent anchor, and the null is physical — but mode-dependent

`WDS Spectrometer Channel` is **`N/A` in all 44 SEM-family columns** (35 SEM + 9 SEM_Composition) —
`N/A`, not `N`. Every attested SEM procedure is EDS, where the SDD collects the whole spectrum
simultaneously. There is no sequence to have, and with 70 literature columns across the four SEM TAPPs
this is the library's largest corpus. The null is trustworthy.

⚠ **Recorded so it is not misread: this is MODE-dependent, not technique-dependent.** A SEM fitted with
WDS would inherit EPMA's pass structure exactly. The finding is "no attested SEM procedure uses WDS",
not "SEM cannot have passes".

### TEM: the one candidate is explicitly simultaneous

Low-loss versus core-loss EELS is the only place a TEM pass could arise — on older spectrometers the two
require separate acquisitions at different settings. Cymes 2023 closes it:

> `EELS Spectrometer` — "Gatan Enfinium ER **Dual EELS** spectrometer (**simultaneous** low-loss and
> core-loss)" · `EELS Acquisition Mode` — "Dual EELS spectrum imaging (simultaneous)"

Positive evidence of single-pass, like LA-Q's.

### The criterion this sharpened: a pass is not a replicate

Zega 2025 looked like a multi-pass case and is not:

> `STEM Frame Averaging` — "**Sequential acquisition** several minutes to >1 h; combined using Python
> (light-element volatilization control)"

Genuinely sequential, genuinely multiple — but the repeats are **identically configured**: the same map
acquired N times and summed to limit beam damage.

> **A pass is a sub-procedure with its own configuration. Identical repeats are replicates.**
> Chernonozhkin's Run 1 and Run 2 differ in spot size, resolution, detector and internal standard;
> Zega's frames differ in nothing. Replication is already carried by `Number of Replicates` and
> `STEM Frame Averaging` and must not migrate to the pass key.

---

## 5. Recommendation

1. **Admit `acquisition pass`** on 7.4a–c, at Phase 0, per 7.12.1. Consumers: ~21 fields across
   **~6 TAPPs** (§4C) — not the 9 an earlier draft inferred from uniformity. **Definer: `Acquisition Pass`** (§4A) — domain-named, not count-named; EPMA already carries it
   as `Sequence`. Not `Multi-Run Sequential Analysis Design`, which fails 7.4a by being absent from all
   three Solution TAPPs and is LA-specific in wording.
2. ~~Settle the definer collision first (§3C).~~ **Done — see §3C RESOLVED.** No definer changes and
   no grammar change; containment is a consumer-side declaration.
3. **Re-key category B, and `Mass Resolution Assignment` from category A.** The other seven
   category-A fields are already correct under 7.3.2.
4. **Re-examine the 2026-08-31 `Desolvation System` decline** on its own terms: Hopp's cell is per-pass,
   and the decline rested partly on the test 7.12.1 has since demoted.

## Open questions

- ~~Is `Multi-Run Sequential Analysis Design` the definer?~~ **Answered in §4A: no.** It becomes a
  consumer. Open successor: does it survive the Rule 6 admission test once `Number of Acquisition
  Passes` exists, or is it absorbed? It currently holds the whole design in prose — the same fidelity
  failure found in `Collector Configuration` (Decision_Record_2026-09-01, §3).
- **The resolution cluster needs rationalising once the key exists.** Three fields would overlap:
  `Mass Resolution Assignment` (per pass, after the §3A correction), `Mass Resolution Setting`
  (`(none)`, "LR and MR" — the procedure-level list, now derivable from the passes) and the new
  `Number of Acquisition Passes`. Their descriptions already cross-reference: *"The overall mode(s)
  used in the procedure are recorded in Mass Resolution Setting."* Is `Setting` still needed when the
  passes enumerate themselves? This is a Rule 6 admission question over three fields, not two, and it
  generalises — the same shape will recur wherever a "Setting" field summarises what the passes now
  carry (`Detector Configuration`, `Plasma Thermal Mode`).
- ~~Extract Neuman et al. 2025 into EPMA.~~ **Done 2026-09-08** — `EPMA_TAPP_v62`.
  ~~Fix `Sequence`'s description.~~ **Done 2026-09-08** — EPMA v63, SEM v61, SEM_Composition v60.
  Remaining successor: decide whether `Sequence` is EPMA's pass definer or a consumer of a neutral
  field. If it is the definer, EPMA
  differs from the ICP-MS family, which needs the neutral field — worth checking against §4A before
  assuming one definer serves both.
- Do the four "stated per run but identical" fields (§2) get keyed? Only if another procedure attests a
  difference — 7.3.2. Worth re-checking when the NGMS and TIMS literature is extracted.
- Does the pre-ablation pass in Chernonozhkin count as an acquisition pass, or as preparation? It uses
  the laser but produces no reported data.
- INAA's passes are separated by **days** (recounting as isotopes decay). Same key, or a different axis?
- How is a cross-pass data dependency (Run 1's Cr as Run 2's internal standard) recorded at all?
