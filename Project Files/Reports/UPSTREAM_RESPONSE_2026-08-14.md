# Response to "Requests to the TAPP library"

Reply to `upstream-requests.md`, 2026-08-14. Checked against the live library, not the 2026-08-13 drop.

**Short version.** Every count in §1 and §2 reproduces exactly. Two requests (§3, §4) already have
answers in the library and need no work. §1 and §2 are both accepted, with one methodological
correction that changes the order of the work and one structural change that will make your schema
generation simpler than either of us was planning.

---

## Already landed — every TAPP has moved (2026-08-14)

**Step 1 of the plan below is done.** Five field definitions were reconciled and the change was applied
across the library, so **all 16 TAPPs are at a new version**. Re-pull before doing anything else; the
2026-08-13 drop you are working from is now one version behind everywhere.

| TAPP | 2026-08-13 drop | now |
|---|---|---|
| EPMA | v20 | **v24** |
| LA-MC-ICPMS | v13 | **v18** |
| LA-MC-ICPMS_UPb | v13 | **v18** |
| LA-Q-ICP-MS | v15 | **v20** |
| LA-Q-ICP-MS_UPb | v16 | **v21** |
| LA-SF-ICP-MS | v16 | **v21** |
| LA-SF-ICP-MS_UPb | v17 | **v22** |
| Lab-XCT | v17 | **v21** |
| SEM | v17 | **v21** |
| SEM_Composition | v17 | **v21** |
| SEM_FIBSEM | v11 | **v14** |
| SEM_Imaging | v11 | **v14** |
| Solution_MC-ICP-MS | v16 | **v21** |
| Solution_Q-ICP-MS | v17 | **v22** |
| Solution_SF-ICP-MS | v18 | **v23** |
| TEM | v17 | **v21** |

`composed_tapps.json` and `Current TAPPs/` are both refreshed and consistent; the manifest's 16 paths
all resolve. Superseded versions remain in their technique folders, so nothing you already have has
been deleted.

**What changed inside them** — 63 Column B rewrites, one field rename in 15 TAPPs, one absorption in
Lab-XCT, and two single-column fixes in the three Solution TAPPs:

| change | scope |
|---|---|
| `Data Reduction Software` → **`Data Processing Software(s)`** | renamed in 15 TAPPs |
| Lab-XCT `Segmentation and Analysis Software` → **absorbed into the same field** | field now 16/16 |
| Column B reconciled: `Acquisition Software`, `Data Processing Software(s)`, `Analytical Mode`, `Target Material` | all 16 |
| `Target Material` Column E `Text (free)` → `Controlled list / Text` | 3 Solution TAPPs |
| `Sample Persistent Identifier` Column D `Basic` → **`Advanced`** | 3 Solution TAPPs |
| `Analyte` description reconciled (4 variants → 1) | 13 TAPPs |
| **Instrument field split** into `Instrument Manufacturer` + `Instrument Model` | 10 TAPPs split; both now 16/16 |
| Column G provenance labels added | 767 rows across all 16 |

**The one that will bite a field-name map:** `Data Reduction Software` no longer exists anywhere in the
library. It is registered as a retired name in our linter, so any document still using it is now
flagged automatically.

**Lab-XCT keeps `Reconstruction Software`** as a technique-specific field. Do not fold it into
`Data Processing Software(s)` — reconstruction is a stage the other fifteen techniques do not have, and
it is substantively reported in 12 of 16 XCT papers.

All four reconciled descriptions are now **byte-identical across every TAPP holding them**, which is
the precondition for `Module_Core`. If you were planning to diff descriptions to detect shared fields,
that signal just got much stronger.

---

## First: your numbers are right

All of it reproduces against `Current TAPPs/` and `Claude Skills for TAPP/modules/`:

| claim | yours | ours |
|---|---|---|
| distinct fields across the 6 LA tables | 153 | 153 |
| in all six | 115 | 115 |
| of those, in a module | 42 | 42 |
| of those, in no module | 73 | 73 |
| shared by 4–5 tables, no module | 10 | 10 |
| fields failing the identity test | 3, named | same 3 |
| the seven near-universal fields | 16/16/16/16/16/15/13 | identical |

Nothing below is a dispute about measurement.

---

## The one correction: the identity test needs Column B

Your precondition test covers Columns C, D, E and I. **Column B is also module-owned** under Rule 6.4,
and description drift under identical field names is the founding evidence for the whole module
system — 14 of 17 Group 1 descriptions had diverged unnoticed before Rule 6 existed. Same name,
different meaning is worse than different names, because a diff does not flag it.

Running the test on Column B changes §2 substantially:

| field | description variants across its TAPPs |
|---|---|
| `Reported Variables and Units` | **1** — identical in all 16 |
| `Constants and Reference Values Used` | **1** — identical in all 16 |
| `Additional Notes` | **1** — identical in all 16 |
| `Acquisition Software` | 8 |
| `Data Reduction Software` *(since renamed `Data Processing Software(s)`)* | 7 |
| `Analytical Mode` | 6 |
| `Analyte` | 4 |

So "there is nothing to reconcile before they could move" holds for three of the seven, not all seven.

The pattern is worth noting, because it is the argument for doing this at all: **the three clean
fields are exactly the three governed by an explicit universal rule** — Rule 8, Rule 5 and Rule 11.
The four divergent ones have no rule. A rule enforces by discipline and this is what discipline
produced; a module enforces by construction.

---

## §1 — accepted, with a wider scope than the drafts assume

**On the "six independent tables" framing.** All six LA tables descend from one LA-Q/SF table split on
2026-08-11, so 72 of 73 descriptions being byte-identical is partly common descent rather than
convergent evidence. That mattered less than it first appeared, because Phase 3 has been run
independently on the branches:

| TAPP | literature procedures assessed |
|---|---|
| LA-Q-ICP-MS (now v18) | **6** (Nakanishi 2022; Liu 2024; Liu 2025 ×2; Liu 2016 ×2) |
| LA-SF-ICP-MS (now v19) | **7** (Zhang 2022 GCA 323; Chernonozhkin 2021 ×3; Mittlefehldt 2024; Navarro 2024 ×2) |
| LA-MC-ICPMS (now v16) | 1 |
| the three U-Pb variants | inherited from their parents; LA-MC_UPb has none |

The Q and SF paper sets are **fully disjoint**, and **58 of your 73 candidates (79%) are attested
independently in both**. That clears Rule 6.10's "prefer three instances to two", so the extraction is
justified — your instinct here was better than our first reading of it.

**Scope.** 48 of the 73 are present in all nine ICP-MS TAPPs, not just the six LA ones; only 17 are
genuinely LA-only. But description identity falls from 72/73 within LA to **11/48** across the nine,
and the divergences are systematic LA-vs-Solution splits. So there are two options and we are taking
the first:

1. **LA-scoped now** — descriptions already agree, roughly one field to reconcile, unblocks your six
   configs.
2. **ICP-MS-scoped later** — 9 consumers, but ~37 description reconciliations by hand, and Solution
   MC-ICP-MS has **0** literature columns, so part of it would be generalising from an unassessed
   TAPP.

Doing (1) first does not waste work: the same reconciliations are needed for (2) either way.

**Three small corrections to the proposal.**

- `Mass Resolution Setting` is cited as technique-dependent per README §4. §4's list of five is about
  `Keyed By`; this field's divergence is in Column D (Editable on SF/MC where the analyst selects,
  Read-Only on Q where the instrument fixes it). The conclusion — stays per-table, per Rule 6.5 — is
  right; the citation is not, and we are adding the exception to the README.
- The **Sample / specimen** group is described as shared by every technique. Four of its eight are
  (`Sample Name`, `Sample Persistent Identifier`, `Sampling Unit`, `Target Material`);
  `Sample Preparation Method` is 15/16; `Analysis Sequence` is ICP-MS-only; and
  `Fusion Flux and Dilution Ratio` is LA-only and attested in only one of the two lineages.
- The six collision/reaction-cell fields you flagged as differently worded: yes, one description is
  needed, and it is on our list rather than yours.

---

## §2 — accepted, and it is becoming a bigger change

Confirmed: nine fields are present in **all 16** TAPPs with no module — your seven minus
`Data Reduction Software` (15/16, since renamed) and `Analyte` (13/16), plus `Sample Name`,
`Sample Persistent Identifier`, `Sampling Unit` and `Target Material`.

Three of them had already drifted, which was the live argument for fixing this now. Two are now
resolved; the third is still open:

- `Sample Persistent Identifier` — was `D=Advanced` in 13 TAPPs, `D=Basic` in the three Solution
  TAPPs, in a **Rule 13 mandatory** field. **Resolved: `D=Advanced` library-wide.** `Sample Name` is
  already `D=Basic` everywhere, so the mandatory burden of identifying the sample is carried, and an
  IGSN often does not exist at submission for experimental products or newly split fragments.
- `Target Material` — was 7 description variants and 2 data types. **Resolved**: one description,
  `Controlled list / Text` everywhere.
- `Sample Preparation Method` — 2 tier variants. **Still open**; not part of this pass.

**What we are doing.** Rather than adding fields to `Group1`, `Group1` is being **retired** and
replaced by `Module_Core` (v2, **30 fields**): its 18 fields plus the universals, unconditional, multi-block only
because the fields insert into five different groups. `Group1` is a group-shaped module
(`replace_group` on Group 1) and the new fields belong to Groups 2, 4, 5 and 6, with `Additional
Notes` required to be the last field of the whole TAPP under Rule 11 — so folding them into `Group1`
would physically relocate them.

Your suggestion to put them in `ReportingCore` was reasonable given what you could see, and it
surfaced a real problem — see below.

**On the two that are not universal:**

- `Data Reduction Software` **has been renamed `Data Processing Software(s)`** and is now 16/16
  (done 2026-08-14 — see the version table above). Group 5 is already named "Data Processing"; TEM had
  already stretched "reduction" to cover image processing; and Lab-XCT refused the name outright,
  splitting it into `Reconstruction Software` and `Segmentation and Analysis Software`. Not every
  technique *reduces* data — XCT reconstruction expands it. Lab-XCT's `Segmentation and Analysis
  Software` was absorbed into the new field; `Reconstruction Software` **stays** as an XCT-specific
  field, being a stage the other fifteen techniques do not have and one reported in 12 of 16 XCT
  papers.
- `Analyte` stays conditional — it applies only to techniques determining chemical composition
  (13/16). It gets its own module.

**Your Rule 7 question, answered.** A definer moving into a shared module is safe here. In all 13
composition TAPPs `Analyte` is the sole `defines: analyte`; in the other three there is **no definer
and no field keyed by `analyte`**. The module's applicability condition and the Rule 7 invariant have
the same footprint, so omitting the module can never strand a consumer.

---

## §3 — `Error Correlation Between Reported Quantities`: neither module

Already settled in `conventions.md` Rule 10, which you do not have. Two things it records:

- The field is in **four** TAPPs, not only the U-Pb ones. The fourth is **Solution MC-ICP-MS**, which
  consumes neither `Geochronology` nor `UPb` — so either module would strand it.
- The reasoning is explicit: it recurs across dating systems but also occurs outside geochronology
  (triple-oxygen δ¹⁷O/δ¹⁸O, double-spike inverted ratios), so it fails Rule 6.1's specificity
  condition and stays library-wide.

At four fields it is also below the extraction threshold on its own. No change.

---

## §4 — delivery mechanics

**`composed_tapps.json` is not broken.** All 16 paths resolve from the **library root**; they resolve
0/16 against a folder containing only `Current TAPPs/`, which is what came off Drive. Rewriting them
to basenames would break them for the library, so instead we are stating the resolution rule in
`Current TAPPs/README.md`. Resolving by filename, as you are doing, is correct and will keep working.

**Modules ship in two places, not three.** `Claude Skills for TAPP/references/modules/` **does not
exist** in the library — please say where you saw it, as it may be an artefact of the Drive copy.

**The `.json` beside each `.csv` is a second source, not a generated view**, and you should read it.
It carries what the CSV cannot: `blocks`, `applies_when`, `owned_columns`, `version`. Reading only the
CSVs is the direct cause of the `ReportingCore` misreading below — its six rows are a flat list with
nothing marking any structure, and all of the conditionality lives in the manifest.

---

## The thing that will change your schema work: `ReportingCore` is being dissolved

Your §2 suggestion — put unconditional fields into `ReportingCore` — plus your own note that they
"would need to be unconditional, or a block every TAPP selects", identified a real defect rather than
a misunderstanding. Two facts:

- It is the **only** module that is not all-or-nothing. 9 of its 16 consumers hold all six fields; the
  rest hold 2, 2, 3, 4, 4, 4 and 5. Every other module — `Group1`, `LaserAblation`, `MCICPMS`,
  `SolutionIntroduction`, `Geochronology`, `UPb` — is all-or-nothing in every consumer.
- Its five blocks have **four different consumer footprints**: `target_selection` 13,
  `calibration_factor` 14, `blank` 12, `aggregation` + `aggregation_qc` 13.

So it is four independent modules stored in one file, bound by shared provenance rather than shared
structure. It is being split into `TargetSelection`, `CalibrationFactor`, `Blank` and `Aggregation`,
each unconditional with a module-level `applies_when`, plus `Analyte` as a fifth.

**What this means for you.** In the interim, "one `$def` per module" is wrong for this one module —
`$ref`-ing a single six-field `ReportingCore` definition from SEM_Imaging asserts four fields it does
not have. Until the split lands, emit **one `$def` per block** and read `composed_tapps.json` →
`modules[].blocks` to know which to reference:

```json
// SEM_Imaging — registered as ReportingCore:target_selection
{ "allOf": [
  { "$ref": "#/$defs/Group1" },
  { "$ref": "#/$defs/RC_target_selection" }
]}

// Solution_Q-ICP-MS — registered as
// ReportingCore:calibration_factor,blank,aggregation,aggregation_qc
{ "allOf": [
  { "$ref": "#/$defs/Group1" },
  { "$ref": "#/$defs/SolutionIntroduction" },
  { "$ref": "#/$defs/RC_calibration_factor" },
  { "$ref": "#/$defs/RC_blank" },
  { "$ref": "#/$defs/RC_aggregation" },
  { "$ref": "#/$defs/RC_aggregation_qc" }
]}
```

One distinction to avoid a trap: a manifest block encodes either *placement* (where rows land in the
spreadsheet) or *applicability* (whether the consumer takes them). Only applicability survives into a
schema. `Module_Core` will have about five blocks purely because its fields insert into five groups,
but all five are always composed together — it emits **one** `$def`. The rule is one `$def` per
independently selectable unit, which mechanically means: manifest has `"conditional": true` → one per
block; otherwise → one per module.

**After the split, "one `$def` per module" becomes true again for every module**, and the block
machinery disappears from your side entirely. If you key your `$def` names on the **block** names —
`target_selection`, `calibration_factor`, `blank`, `aggregation` — those survive into the new module
names, so the transition costs you a prefix rather than a rewrite.

---

## Where a field's definition comes from — read Column G

Column G used to be almost blank and safe to ignore. **As of 2026-08-14 it carries a provenance label
on 767 of 1706 content rows (45%)**, naming the module each field came from. It is the fastest way to
answer "where does a change to this field have to be made?" — which matters because a shared field
must be changed once, in its module, not sixteen times.

| what you see in Column G | what it means |
|---|---|
| `Source: Core module` | universal field, owned by `Core`, present in all 16 TAPPs |
| `Source: Laser Ablation module` | supplied by `LaserAblation` to its 6 consumers |
| `Source: Calibration Factor module` | supplied by `CalibrationFactor` to its 14 consumers |
| `Source: Geochronology module` / `Source: U-Pb module` | the geochronology layers, as before |
| **blank** | the field belongs to **no module** — it is native to that TAPP |

Three rules govern it, and the third is the one that would otherwise mislead you.

**1. A blank cell is information.** It means the field is TAPP-native, not that provenance is unknown.
`Monitored Isotopes` in the LA tables is an example.

**2. A consumer's own comment wins.** Composition only ever fills an *empty* Column G cell, so any
annotation a TAPP author wrote survives every recomposition. If you see prose that is not a `Source:`
label, a human wrote it deliberately.

**3. The label names the module that OWNS the field, not one that merely overlays it.** A Layer 3
module such as `UPb` supplies system-specific Column F *examples* onto fields other modules own, and
does not relabel them. In `LA-Q-ICP-MS_UPb`:

| field | Column G | Column F supplied by |
|---|---|---|
| `Age Calculation Method` | `Source: Geochronology module` | `UPb` (U-Pb date equations, Jaffey decay constants) |
| `Calibration Factor and Determination Method` | `Source: Calibration Factor module` | `UPb` (EARTHTIME ET535 tracer) |
| `Discordance Definition and Values` | `Source: U-Pb module` | `UPb` — it inserts this one |

**So a single row can draw on two modules**: its definition, tiers, data type and `Keyed By` from the
owner named in Column G, and its examples from a system module that is *not* named there. For schema
generation the owner is what matters — it determines which `$def` the field belongs to. The overlay
affects Column F only, which is example content rather than schema structure.

Column G remains **documentation only** — no structural meaning, not schema content. Exclude it, or
map it to `$comment` if you want provenance visible in the generated schema.

---

## Order of work upstream

1. ~~Reconcile 5 field definitions — `Acquisition Software`, `Data Processing Software(s)`,
   `Analytical Mode`, `Target Material`, and the `Sample Persistent Identifier` tier split.~~
   **DONE 2026-08-14** — all 16 TAPPs bumped; see the version table at the top.
2. ~~Compose `Module_Core`; retire `Group1`.~~ **DONE** — `Core` v2, **30 fields**.
3. Dissolve `ReportingCore` into four modules, plus `Analyte`.
4. Extract the LA-scoped modules from your groupings.
5. ICP-MS-wide consolidation — deferred until Solution MC-ICP-MS has a Phase 3.

Steps 2 and 3 are one break, not two — take them together. Step 1 is already a version bump on every
TAPP, but it changes no field set and no module, so nothing on your side needs restructuring for it —
only the filenames and the four reconciled descriptions.

**Please hold the six LA configs** until step 4. The drafts are not wasted; they are the starting
candidate set, and the 67 of 71 that already have a placement in a technique sidecar still do.

## What you can act on today

- **Re-pull the library.** All 16 TAPPs are at a new version; nothing you have is current.
- **Apply the rename `Data Reduction Software` → `Data Processing Software(s)`** in any authored
  paths or field-name maps. This one has already landed, so it is not a future change to plan for.
- **Drop any Lab-XCT path for `Segmentation and Analysis Software`** — it is now
  `Data Processing Software(s)`. Keep `Reconstruction Software`, which is unchanged.
- **Apply the instrument split.** `ICP-MS Manufacturer & Model`, `Instrument Make and Model` and
  `CT System Manufacturer and Model` are all gone, replaced everywhere by the pair
  `Instrument Manufacturer` (Controlled list — a vendor facet you can query) and `Instrument Model`
  (free text). Both are `Core` fields present in all 16.
- **Read Column G** — it is 45% populated now and names each field's owning module. See the section
  above.
- §3 and §4 need nothing from you beyond resolving by filename, which you already do.
- Switch to one `$def` per block for `ReportingCore` only; everything else stays one per module.
- Start reading the `Module_*.json` manifests alongside the CSVs.
- **`Group1` is gone — renamed and extended to `Core`** (landed 2026-08-14). Rename your `Group1`
  `$def` and add the 10 universals listed in README §9. `Core` is unconditional and all-or-nothing:
  **30** fields, present in all 16 TAPPs, **one `$def`** despite having six blocks (they are placement
  blocks, always composed together — not independently selectable like `ReportingCore`'s).
  No TAPP file changed and no version moved for this: composition reported MATCH on all 16, because
  the definitions were reconciled first. Retired module files are in `Archive/Superseded Modules/`.
- **`ReportingCore` is gone too — dissolved into four ordinary modules** (landed 2026-08-14):
  `TargetSelection` (2 fields, 13 consumers), `CalibrationFactor` (1, 14), `Blank` (1, 12),
  `Aggregation` (2, 13). **"One `$def` per module" is now true without exception** — no module in the
  library is conditional, so there is no block machinery to model at all. The one-`$def`-per-block
  advice earlier in this document applied only to `ReportingCore` and is obsolete; three block names
  carry straight over (`target_selection`, `calibration_factor`, `blank`), and `aggregation` +
  `aggregation_qc` merge into `Aggregation`. Again no TAPP file changed and no version moved: all 52
  module x consumer pairs reported MATCH.
- Nothing further is pending on the module restructuring. Next upstream is step 4, the LA-scoped
  modules.

---

## Also recorded, so it is not re-litigated

- **Rule 6.10's extraction threshold has been amended** (2026-08-14) from "five or more fields" to
  "ten or more placements" (fields × consuming TAPPs), so that a one-field module with fourteen
  consumers is legitimate while a five-field module with two consumers is not. It does not reopen past
  decisions: the two residues previously declined score 3 and 6 placements and stay unbuilt.
- **A sub-module test is now required** before any new module is built (Rule 6.15), specifically to
  prevent the proliferation of tiny modules the threshold change would otherwise permit.
- **Lab-XCT's Column F for `Reported Variables and Units`** still carries generic module examples
  rather than XCT ones. Being fixed; do not treat those values as XCT-specific.
