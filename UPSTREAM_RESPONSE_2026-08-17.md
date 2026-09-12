# Changes since the 2026-08-14 upstream response

Companion to `UPSTREAM_RESPONSE_2026-08-14.md`. Everything below happened after that document was
written. **12 of 16 TAPPs have moved.** Library is at 0 ERROR / 0 WARN, `compose_tapp.py --check`
16/16 MATCH, `Current TAPPs/` synced, `composed_tapps.json` resolving 16/16.

**If you only read one section, read §1 and §6** — §1 is the re-pull table, §6 is the field-name map
you will need to diff against.

---

## 1. Re-pull: 12 TAPPs at new versions

| TAPP | 2026-08-14 | now | fields | lit cols |
|---|---|---|---|---|
| EPMA | v24 | **v25** | 86 | 15 |
| LA-MC-ICPMS | v18 | **v26** | 140 | 1 |
| LA-MC-ICPMS_UPb | v18 | **v26** | 150 | 0 |
| LA-Q-ICP-MS | v20 | **v29** | 130 | 7 |
| LA-Q-ICP-MS_UPb | v21 | **v29** | 140 | 6 |
| LA-SF-ICP-MS | v21 | **v28** | 124 | 7 |
| LA-SF-ICP-MS_UPb | v22 | **v29** | 134 | 7 |
| SEM | v21 | **v22** | 119 | 35 |
| SEM_Composition | v21 | **v22** | 89 | 35 |
| Solution_MC-ICP-MS | v21 | **v30** | 123 | **14** |
| Solution_Q-ICP-MS | v22 | **v34** | 117 | 9 |
| Solution_SF-ICP-MS | v23 | **v32** | 111 | 6 |
| Lab-XCT | v21 | v21 | 88 | 17 |
| SEM_FIBSEM | v14 | v14 | 52 | 35 |
| SEM_Imaging | v14 | v14 | 59 | 35 |
| TEM | v21 | v21 | 90 | 21 |

250 literature-assessment columns library-wide, up from 231. Superseded versions remain in their
technique folders; nothing has been deleted.

---

## 2. What did **not** change — read this before re-deriving anything

No change to: the six-group structure, the tier vocabularies, the sentinel/mode-column layout, Rule 7
notation, the module architecture (still **12 modules**), or any module's field set. Composition is
still a no-op — every one of today's changes is TAPP-owned. `Module_Core`, the four
ReportingCore descendants, `Module_Analyte`, `Module_SolutionIntroduction`, `Module_MCICPMS`,
`Module_LaserAblation`, `Module_Geochronology`, `Module_UPb`, `Module_ArAr` are untouched.

**Neither ICP-MS module was built.** The two we specified — `Module_CRC` (6 fields × 6 TAPPs) and
`Module_ICPMS` (17 × 9) — are designed and justified but deliberately not built; see §7.

---

## 3. Field renames — the map you need

Every one is registered in the linter's `RETIRED_FIELDS`, so any document still using an old name is
flagged automatically. **Nine renames**, all one-to-one:

| old | new | TAPPs |
|---|---|---|
| `Monitored Isotopes` | **`Monitored Masses`** | 8 |
| `Make-up Gas Flow Rate` | **`Make-up Gas and Flow Rate`** | 3 → 9 |
| `Plasma / Make-up Gas Addition` | **`Make-up Gas and Flow Rate`** | 6 → 9 |
| `Sensitivity as Useful Yield` | **`Instrument Sensitivity`** | 6 → 9 |
| `In-Run Isotope Ratio Reproducibility and Assessment Method` | **`Within-Session Analytical Precision and Assessment Method`** | 1 → 9 |
| `Between-Session Reproducibility and Assessment Method` | **`Between-Session (Long-Term) Analytical Precision and Assessment Method`** | 1 → 9 |
| `Number of Replicates per Sample` | **`Number of Replicates`** | 2 → 8 |
| `Mass Cycles per Replicate` | **`Number of Scans per Replicate`** | 1 → 2 |

Six of these are **merges**: a single concept had carried two names because the LA and Solution
lineages were built separately. If you were maintaining a field-name map, six pairs collapse to one
entry each.

---

## 4. New fields — seven

| field | TAPPs | C / D | Data Type | Keyed By |
|---|---|---|---|---|
| `ICP Tuning` | 9 | Advanced / Editable | Text (free) | `(none)` |
| `Instrument Warm-up / Session Duration Limit` | 9 | Advanced / Read-Only | Text (free) | `(none)` |
| `Ion Counter Dead Time` | 9 | Basic / Editable | Numeric (ns) | `channel` |
| `Reaction Product Ion / Mass-Shift Transition` | 3 | Advanced / Read-Only | Text (free) | `channel` |
| `Collision/Reaction Gas Mixture Ratio` | 3 | Advanced / Editable | Text (free) | `channel` |
| `Internal (Within-Measurement) Analytical Precision and Assessment Method` | 9 | Advanced / Basic | Text (free) | `sample > sampling unit x reported property` |
| `Counting Statistics Error` | 3 → **12** | Advanced / Basic | Text (free) | `sample > sampling unit x reported property` |

`Instrument Sensitivity` is also effectively new in the 3 Solution TAPPs (it did not exist there
before) though it is listed above as a rename, since it absorbed the LA field.

**Group 6 in every ICP-MS TAPP now reads as a four-step uncertainty ladder** — you may want to model
this as a group:

> `Counting Statistics Error` (predicted from counts) → `Internal (Within-Measurement)…` (observed
> within one measurement) → `Within-Session…` → `Between-Session (Long-Term)…`

---

## 5. Key changes — three fields re-keyed

| field | was | now |
|---|---|---|
| `Collision/Reaction Cell (CRC) Configuration` | `(none)` | **`channel`** |
| `Collision Gas Type` | `(none)` | **`channel`** |
| `Reaction Gas Type` | `(none)` | **`channel`** |

All three because one paper runs two cell modes on two isotopes of the same element in one study; a
scalar cannot hold that.

**Two schema-relevant consequences:**

1. **`sample > sampling unit x reported property` now has two users**, not one. This is the only
   three-level form in the library and the most complex thing your generator has to emit.
   `README_TAPP_for_Schema_Generation.md` §4 now carries a worked JSON block for it — read that rather
   than inferring the nesting. Read outer-to-inner: within each sample, for each analysis, one value
   per reported property. `>` is containment, `x` is a cross-product.
2. `Monitored Masses` keeps its **registered** key divergence — `analyte` in the two LA-MC TAPPs
   (where `Collector Configuration` defines the channel), `defines: channel per analyte` in the other
   six. That is a `KEYED_BY_TECHNIQUE_DEPENDENT` entry with a recorded rationale, not drift.

---

## 6. Data-type changes — four, all widening

| field | was | now | why |
|---|---|---|---|
| `Collision Gas Type` | `Text (free)` (4) / `Controlled list` (2) | `Controlled list / Text` ×6 | mixtures need a qualifying answer |
| `Reaction Gas Type` | same split, **plus unicode subscripts** vs ASCII | `Controlled list / Text` ×6, **ASCII** | `NH₃` and `NH3` are different strings |
| `Dwell Time per Mass` | `Text (free)` (4) / `Numeric (ms) / Text` (2) | `Numeric (ms) / Text` ×6 | bare text lost the unit |
| `Make-up Gas and Flow Rate` | `Text (free)` / `Numeric (L/min)` | `Numeric (L/min) / Text` ×9 | keeps unit, admits multi-part answers |
| `Instrument Sensitivity` | `Numeric (%)` (LA) | `Numeric + unit / Text` ×9 | holds both V/ppm and useful-yield % |

**The unicode one is the one most likely to break a consumer**: `Reaction Gas Type`'s allowed values
were `NH₃ | O₂ | CH₄` in the four LA TAPPs and `NH3 | O2 | CH4` in the two Solution ones. Now ASCII
everywhere.

Note also: for a compound whose first component is `Controlled list`, Column F offers `N/A | None`
but **not** `Other: specify` — the `/ Text` component already grants the unlisted answer.

---

## 7. The ICP-MS module question — answered, deliberately not built

Your §1 asked for more modules. We measured rather than guessed.

79 unmoduled fields across the 9 ICP-MS TAPPs fall into clean exact footprints: **31 in all 9**, 16 in
the 6 LA tables, 7 in 8, 6 in the CRC-bearing 6. Every candidate clears Rule 6.10's placement
threshold easily, so size is not the constraint — coherence is.

**The trap we had to avoid, and you should too if you re-derive this.** All nine ICP-MS TAPPs descend
from one template, so a field present in all nine may be there because it belongs to the instrument
*or* because it was inherited. Footprint alone cannot tell you. **The literature can**: the LA branch
(27 columns) and the Solution branch (11) were assessed against fully disjoint paper sets, and **21 of
the 31 are independently attested in both**. Those are safe. The rest are not yet.

**Nine of the 31 are not ICP-MS content at all** — `Analysis Sequence`, `Uncertainty Level`,
`Uncertainty Propagation Method`, `Analytical Accuracy…`, `Limit of Quantification (LOQ) Method`,
`Calibration Standard Measurement Frequency`, `Instrument Serial Number or Lab Identifier`,
`Spike / Outlier Filtering Approach`, `Blank / Background Correction Method`. They sit in all nine
only by accident of build order. Every technique quotes an uncertainty convention; EPMA lacks
`Uncertainty Level` because nobody added one. **Moduling these as ICP-MS would freeze an accidental
footprint** — they are gaps in the other seven TAPPs.

Recommended, specified, **not built**:

- **`Module_CRC`** — 6 fields × 6 TAPPs = 36 placements. Build this first: its boundary is physical
  (sector-field instruments have no collision cell), which makes the footprint trustworthy.
- **`Module_ICPMS`** — 17 × 9 = 153 placements. Plasma/torch, interface/analyser, interference
  handling, internal standardisation.
- `Blank / Background Correction Method` needs **no** module: it is the procedure-level partner of
  `Procedural Blank Level`, which `Module_Blank` already owns across 12 consumers. Rule 6.15 prong 1,
  absorption.

---

## 8. Literature assessment — what the corpus now supports

Two full Phase 3 rounds ran. Relevant to you because these columns are the evidence behind every key
and tier you consume.

- **Solution MC-ICP-MS got its first ever literature assessment**: 12 papers → 14 procedure columns,
  585 of 1694 cells attested. It previously had **zero**.
- **Twelve fields that were blank in every Solution Q/SF column were assessed**: 82 of 132 cells
  attested. They had never been asked — they postdate the June extraction. **7 of those 12 are still
  blank in all 231 columns of all 16 TAPPs**, so if you are inferring anything from emptiness, do not.
- Three TQ-ICP-MS papers were registered and assessed, adding 5 columns.

**One methodological point that bears directly on schema confidence.** In a literature column, **blank
and `N` are not the same**. `N` means asked and not stated; blank means the field postdates that
TAPP's Phase 3 and the emptiness carries no information. Splitting them reversed six of our own
verdicts. If you surface literature coverage anywhere, keep them distinct.

---

## 9. Registers and tooling

- **`generate_paper_registry.py` was found drifted and repaired.** It held 21 papers against 55 live
  and would have deleted 34 rows and collapsed the `Solution Q-ICP-MS` / `Solution SF-ICP-MS` split.
  Rebuilt from the live CSV; now round-trips. **Run `--check` before every use.**
- `paper_registry.csv` is now **68 papers × 27 columns**, up from 55 × 23. New columns:
  `Solution ICP-MS` (restored, *derived* from the split pair so a future re-merge stays possible —
  do not hand-edit it), `Thermal Ionization Mass Spectrometry (TIMS)`, `Laser Ablation Q-ICP-MS`,
  `Laser Ablation SF-ICP-MS`. Combined columns are retained alongside their splits by author decision.
- `Laser Ablation ICP-TQ-MS` is **parked** — retained, all rows `N`. Triple-quadrupole platforms
  register under Q-ICP-MS; see §10.
- `composed_tapps.json` and `TAPP_Composed_Variants.csv` are both current; `Current TAPPs/` synced.

---

## 10. Two decisions you may need to encode

**Triple-quadrupole platforms register under the Q-ICP-MS TAPP.** Not under a separate TQ TAPP.
The platform is named in `Instrument Model`, its identity in `ICP-MS Type` (`Triple quadrupole
(ICP-MS/MS)`, already an allowed value), and tandem operation in `CRC Configuration`
(`ICP-MS/MS (triple-quadrupole mode)`). **TAPP assignment is not instrument identity** — analyser
family decides the container, configuration is a field value. Wu et al. 2023 tune in single-quadrupole
mode and switch to TQ mid-session on one instrument, which is the demonstration.

**Combined and split columns coexist by design**, in both the register and the TAPPs. `Solution
ICP-MS` sits beside `Solution Q-ICP-MS`/`Solution SF-ICP-MS`; `Laser Ablation Q/SF-ICP-MS` beside its
two splits. The merged views are retained so a split can be reversed without data loss. Only the
`Solution ICP-MS` column is derived; the LA splits were populated by re-reading all eight papers.

---

## 11. Open, and honestly so

- `Module_CRC` and `Module_ICPMS` specified, **not built**.
- The nine general fields of §7 are library gaps in the other seven TAPPs. `Uncertainty Level` is the
  clearest candidate for a universal rule in the style of Rules 8 and 9.
- Whether `LA-ICP-TQ-MS` deserves a standalone TAPP is **undecided and testable**: add MS/MS-mode
  papers to LA-Q / Solution Q and measure the residue. Our first residue test returned zero and was
  wrong — the sample could not have exercised the fields in question.
- Solution MC-ICP-MS's Phase 3 rests on what its PDFs carry; several papers put digestion and QC
  detail in supplementary material we do not have.
- A composed TAPP still makes **no self-declaration** of what built it; `composed_tapps.json` remains
  the only witness. Unchanged since 2026-08-14 and still the gap we would fix next on the tooling side.
