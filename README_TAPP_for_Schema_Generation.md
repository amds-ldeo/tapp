# TAPP structure — a guide for generating JSON Schemas

Written 2026-08-11 for converting the TAPP spreadsheets into JSON Schemas. It describes what is
actually in the files and what will mislead you if you read them naively. It is not the full
specification — `Claude Skills for TAPP/references/conventions.md` is authoritative and this
summarises the parts that bear on schema generation.

---

## 1. The one thing to get right first

**A TAPP is not one schema. It describes two related objects.**

| Object | What it is | Registered/created when |
|---|---|---|
| **Procedure** | The standing set of guidelines specifying how a technique is applied at a lab. Registerable, citable, gets a DOI. | Once, then reused |
| **Analysis** | One execution of that procedure — one **session**, which may cover many samples. | Every time the procedure is run |

Every field row carries **two independent tier assignments**: Column C says what the field means at
procedure level, Column D what it means at analysis level. A row is not "required" or "optional" — it is
required-or-not *at each of two levels, differently*.

The natural target is therefore either two schemas (`procedure.schema.json`,
`analysis.schema.json`) that share field definitions, or one schema with level-conditional
requiredness. Producing a single flat object with one `required` array loses the distinction the whole
framework exists to express.

An analysis record **references** a procedure (by DOI) and inherits values from it. Columns C and D
together tell you which fields are inherited, which are inherited-but-adjustable, and which must be
supplied fresh.

**The analysis object is a session, not a sample — changed 2026-08-12 (Rule 13).** One analysis
record covers every sample measured in one execution of the procedure. Three fields are mandatory in
every TAPP as a result: `Session Identifier` (`(none)` — the laboratory's own run identifier),
`Sample Name` (`defines: sample`) and `Sample Persistent Identifier` (`sample`). Column I is what
separates the levels: `(none)` at analysis level means *per session*, `sample` means *per sample*,
`sample > sampling unit` means *per spot within a sample*. A schema that flattens analysis-level
fields onto one object loses this, and cannot express that a shared session calibration correlates
the samples measured under it.

---

## 2. Files

16 TAPPs, one per technique or technique variant. **The CSV is the source of truth**; the xlsx is a
generated artifact (colour-coded, with a Legends sheet) and should not be parsed for content.

| TAPP | Modules composed |
|---|---|
| `EPMA/EPMA_TAPP_v*.csv` | Core, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v*.csv` | Core, LaserAblation, MCICPMS, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v*.csv` | Core, LaserAblation, MCICPMS, TargetSelection, CalibrationFactor, Blank, Aggregation, Geochronology, UPb |
| `SEM/SEM_Composition_TAPP_v*.csv` | Core, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `SEM/SEM_FIBSEM_TAPP_v*.csv` | Core, TargetSelection |
| `SEM/SEM_Imaging_TAPP_v*.csv` | Core, TargetSelection |
| `SEM/SEM_TAPP_v*.csv` | Core, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v*.csv` | Core, MCICPMS, CalibrationFactor, Blank, Aggregation, SolutionIntroduction |
| `Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v*.csv` | Core, CalibrationFactor, Blank, Aggregation, SolutionIntroduction |
| `Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v*.csv` | Core, CalibrationFactor, Blank, Aggregation, SolutionIntroduction |
| `TEM/TEM_TAPP_v*.csv` | Core, TargetSelection, CalibrationFactor, Aggregation |
| `XCT/Lab-XCT_TAPP_v*.csv` | Core, TargetSelection, CalibrationFactor |
| `LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v*.csv` | Core, LaserAblation, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v*.csv` | Core, LaserAblation, TargetSelection, CalibrationFactor, Blank, Aggregation, Geochronology, UPb |
| `LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v*.csv` | Core, LaserAblation, TargetSelection, CalibrationFactor, Blank, Aggregation |
| `LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v*.csv` | Core, LaserAblation, TargetSelection, CalibrationFactor, Blank, Aggregation, Geochronology, UPb |

**No module is conditional any more.** Every module listed above is all-or-nothing: a TAPP
composes it or does not, and if it does, it holds every one of that module's fields. The former
`ReportingCore blocks` column is gone — see §9.

**Version numbers move.** Always resolve the current file with `ls`/`find` or by reading
`composed_tapps.json`, which is the machine-readable registry of which TAPPs exist and which modules each
was built from. Do not hard-code filenames.

Encoding is UTF-8 with BOM (`utf-8-sig`). Field content contains superscripts and Greek
(`²⁰⁶Pb/²³⁸U`, `δ⁵⁶Fe`, `J cm⁻²`) — preserve it.

---

## 3. Column structure

Columns A–I are fixed. Everything after them is variable-width and must be located by header, not
position.

| Col | Header | Use in schema generation |
|---|---|---|
| A | `Metadata Item` | The field name. Use as the property key (slugified) and keep the original as `title`. |
| B | `Description` *or* `Description / Purpose` | → `description`. Often carries conditional rules — see §7. |
| C | `Procedure-Level Tier` | Requiredness at procedure level. See §5. |
| D | `Analysis-Level Tier` | Requiredness/mutability at analysis level. See §5. |
| E | `Data Type` | → JSON type + format. See §6. |
| F | `Example / Allowed Content` *or* `Example/Allowed Content` | Either an enumeration or examples — **which one depends on Column E**. See §6. |
| G | `Comments` | Provenance labels only — see §3.1. Carries no structural meaning; exclude from the schema. |
| H | `Last Update` | `YYYY-MM-DD`. Provenance only. |
| I | `Keyed By` | **Cardinality.** This is what makes the schema nested rather than flat. See §4. |
| J … | Mode flag columns | Conditional applicability. Count varies 0–11. See §8. |
| (after modes) | `Literature Assessment` | **Sentinel.** Header is exactly this string; all data rows empty. Marks the end of the mode block. |
| (after sentinel) | Literature assessment columns | Evidence extracted from papers. **Not schema content — exclude.** |

**Parse A–I by position, B and F by position only.** Columns B and F each have two header spellings in
circulation (`Description` / `Description / Purpose`, and with/without spaces around the slash). A–I are
positionally stable; matching on header text will fail on some files.

**Locate the boundaries by header, not index.** Mode flags are the columns between `Keyed By` and the
column headed exactly `Literature Assessment`. Three TAPPs (Solution Q, SF and MC-ICP-MS) have **zero**
mode-flag columns — the sentinel sits immediately after Column I. Code that assumes at least one mode
column will break on those three.

### 3.1 Column G — what the Comments column now holds

Column G was cleared library-wide on 2026-08-11 (mode applicability moved to the mode-flag columns,
cardinality to Column I, conditional rules into Column B) and then **repopulated on 2026-08-14 with
field-provenance labels**. It now carries a label on **767 of 1706 content rows — 45% of the library**.
If you read an earlier drop, this column was almost blank; that is no longer true.

Every field supplied by a module names that module, written automatically by composition
(`source_comment` in the module manifest) — `Source: Core module`, `Source: Laser Ablation module`,
`Source: Calibration Factor module`, and so on for all 12.

**Three rules make this readable:**

1. **The label names the module that OWNS the field, not one that overlays it.** In a U-Pb variant,
   `Age Calculation Method` reads `Source: Geochronology module` even though `Module_UPb` supplied its
   U-Pb-specific Column F examples. A Layer 3 module's label appears only on fields it *inserts* —
   `Discordance Definition and Values` reads `Source: U-Pb module`.
2. **A blank Column G now means the field belongs to no module** — it is native to that TAPP.
   `Monitored Masses` is an example. Blank is information, not absence of information.
3. **A consumer's own comment always wins.** Composition only ever fills an *empty* Column G cell, so
   any annotation a TAPP author wrote survives every recomposition.

Together these let you answer, for any row, where its definition came from and therefore where a
change to it must be made — which is the round-tripping question in §9.

**Still documentation only.** `validate_tapp.py` does not read it, it carries no structural meaning, and it is
**not schema content** — exclude it, or map it to a `$comment` if you want provenance visible in the
output. It says nothing about type, requiredness or cardinality.

One caveat if you use it to reason about provenance: it marks fields the geochronology modules
*contribute*, not everything U-Pb-specific. `Module_UPb` also overlays U-Pb-specific *examples* (Column F)
onto six general fields it does not own — `Calibration Factor and Determination Method`,
`Procedural Blank Level`, `Analysis Inclusion and Rejection Criteria`,
`Goodness-of-Fit or Dispersion Statistic`, `Target Selection Criteria`,
`Pre-Analysis Imaging and Screening` — and those stay unlabelled, because the *field* is general even
though its examples are not.

### Row types

Only one of the three is a field.

1. **Group header** — Column A matches `^\d+\.\s`, e.g. `4. Measurement Information`. Six per TAPP,
   always the same six, always in this order:
   `1. Procedure Identification` · `2. Samples` · `3. Instrument & Software` ·
   `4. Measurement Information` · `5. Data Processing` · `6. Quality Control & Uncertainty`.
   Use them for grouping/`$comment`, not as properties.
2. **Blank separator** — all of A–H empty. Skip.
3. **Content row** — everything else. One field.

---

## 4. `Keyed By` — the cardinality system (Column I)

**This is the column that determines schema shape, and it has no equivalent in an ordinary
spreadsheet-to-schema conversion.** It states what a field's value repeats over. Ignoring it produces a
flat object where roughly 20% of fields should be arrays of objects.

Column I is never blank on a content row.

### Values

| Value | Meaning | Schema consequence |
|---|---|---|
| `(none)` | Scalar — one value per procedure, or **per session** at analysis level. 76% of fields. | Ordinary property on the parent object |
| `sample` | One value per sample covered by the session | Property of an object in the `samples` array |
| `analyte` | One value per chemical species determined — **the element or species, never the isotope** | Property of an object in the `analytes` array |
| `channel` | One value per instrument selection position (mass, cup, X-ray line, energy-loss edge) | Property of an object in the `channels` array |
| `reported property` | One value per reported quantity or nominal property, at any point in the chain — ratios *and* dates alike, plus their uncertainties | Property of an object in the `reportedProperties` array |
| `sampling unit` | One value per subdivision of the sample carrying its own row — grain, spot, aliquot, phase | Property of an object in the `samplingUnits` array |
| `standard` | One value per reference material or reference database entry | Property of an object in the `standards` array |
| `preparation step` | One value per sample-preparation stage | Property of an object in the `preparationSteps` array |
| `defines: X` | **This field enumerates the domain X.** It is the header of the child table, not a column in it | Its value populates the key set for the `X` array |
| `A x B` | Cross-product — one value per combination. **Ordered**: read as "for each A, one value per B" | 2-D: array of objects nested one level |
| `A > B` | Containment — B exists only within A | Nested array. **In use since 2026-08-12**: `sample > sampling unit`, 16 rows |
| `A > B x C` | Containment then cross-product — "within each A, for each B, one value per C" | One row: `sample > sampling unit x reported property` |
| `defines: A per B` | **The field enumerates domain A and carries a parent key into B.** This is the channel↔analyte binding | Child array for A, with a **nullable** foreign key to B on each member |
| `pair: A` | Keyed by an unordered pair of A | Property on a pair object, e.g. `{"between": ["206Pb/238U date", "207Pb/235U date"], "value": …}` |

**Seven** keys are in use library-wide: `sample`, `sampling unit`, `reported property`, `channel`,
`analyte`, `standard`, `preparation step`. (`sample` was added 2026-08-12 with Rule 13.) Four more
(`conversion`, `acquisition pass`, `background position`, `model component`) are documented but
retired from use — you may ignore them.

**Separator is a literal ASCII lowercase `x`, not `×`.** The specification prose in `conventions.md`
renders the cross-product with a multiplication sign, but the CSV cells contain
`standard x reported property`. Split on the regex `\s+x\s+` (or `\s*[x>]\s*` to catch nesting too), not on
`×`. The complete set of values actually present in the library is:

```
(none)
sample                             sampling unit
analyte                            channel
reported property                  preparation step
defines: sample                    defines: sampling unit
defines: analyte                   defines: reported property
defines: standard                  defines: preparation step
defines: channel per analyte       defines: standard per analyte
pair: reported property
sample > sampling unit
sample > sampling unit x reported property
standard x reported property
```

**Eighteen** distinct strings across the whole library — small enough to handle as a closed set.
Recount before you rely on it; this set was last verified 2026-08-12 and has changed twice since
the file was written.

### Invariants you can rely on

- Every key used in a TAPP has **exactly one** field declaring `defines:` it.
- A `defines: X` field exists only where some other field is keyed by X — with two exceptions,
  `Reported Variables and Units` and `Sampling Unit`, which are mandatory in every TAPP for their own
  declarative purpose and may have no consumers.
- A field name normally carries the same `Keyed By` in every TAPP. Five are technique-dependent by
  design: `Detection Limit`, `Primary Calibration Standard Name`, `Dwell Time per Pixel`,
  `Beam Current`, `Monitored Masses`. Do not assume one global mapping of field name → key.
- **Where a TAPP declares both an analyte domain and a channel domain, the field that defines the
  channel carries the binding** as `defines: channel per analyte`. All 13 such TAPPs do, since
  2026-08-12. The defining field differs by technique: `Monitored Masses` (single-collector ICP-MS),
  `Collector Configuration` (multicollector), `WDS Spectrometer Channel` (electron beam),
  `EELS Edges` (TEM).
- **That parent key is optional per row — model it nullable, never `NOT NULL`.** `per B` means "where
  a B exists", not "for every row". Interference monitors, internal standards and carriers are
  channels with no analyte: Desem et al. 2022 monitors `202Hg, 203Tl, 204Pb, 205Tl, 206Pb, 207Pb,
  208Pb` for a procedure whose analyte is **Pb alone**. Keep parentless rows — they are part of the run
  table and are needed to assess interference corrections.
- **Never infer domain membership from a child table.** The analyte list comes from the
  `defines: analyte` field only. Parsing `202Hg` into "Hg" and adding Hg to the analytes records a
  determinand the procedure never determined.

### Worked example

From the LA-SF-ICP-MS U-Pb TAPP (resolve the current version via `composed_tapps.json`):

| Field | Keyed By |
|---|---|
| `Procedure Name` | `(none)` |
| `Session Identifier` | `(none)` |
| `Sample Name` | `defines: sample` |
| `Sample Persistent Identifier` | `sample` |
| `Analyte` | `defines: analyte` |
| `Monitored Masses` | `defines: channel per analyte` |
| `Dwell Time per Mass` | `channel` |
| `Reported Variables and Units` | `defines: reported property` |
| `Analytical Accuracy and Assessment Method` | `standard x reported property` |
| `Discordance Definition and Values` | `pair: reported property` |
| `Counting Statistics Error` | `sample > sampling unit x reported property` |

```jsonc
{
  "procedureName": "LA-ICP-MS U-Pb Zircon v2.1",        // (none) → scalar
  "sessionIdentifier": "2026-03-11_seq04",              // (none) at analysis level = per session

  "samples": [                                          // domain from `Sample Name`
    { "name": "Z-114", "persistentIdentifier": "IGSN:AU1234567" },
    { "name": "Z-115", "persistentIdentifier": "IGSN:AU1234568" }
  ],

  "analytes":  [ { "name": "U" }, { "name": "Pb" } ],    // domain from `Analyte`
  "channels":  [                                         // `defines: channel per analyte`
    { "id": "206Pb", "analyte": "Pb", "dwellTimePerMass": "10 ms" },
    { "id": "238U",  "analyte": "U",  "dwellTimePerMass": "6 ms" },
    { "id": "202Hg", "analyte": null, "dwellTimePerMass": "6 ms" }  // monitor: no parent analyte
  ],
  "reportedProperties": [                                // domain from `Reported Variables and Units`
    { "id": "206Pb/238U date", "unit": "Ma" },
    { "id": "207Pb/235U date", "unit": "Ma" }
  ],

  // standard x reported property -> for each standard, one value per reported property
  "analyticalAccuracy": [
    { "standard": "Plešovice",
      "byReportedProperty": [ { "reportedProperty": "206Pb/238U date", "value": "within 1%" } ] }
  ],

  // pair: reported property
  "discordance": [
    { "between": ["206Pb/238U date", "207Pb/206Pb date"],
      "definition": "100 × (1 − [206Pb/238U date] / [207Pb/206Pb date])" }
  ],

  // sample > sampling unit x reported property — the only three-level form in the library.
  // Read outer-to-inner: within each sample, for each analysis, one value per reported property.
  // `>` is containment (a spot exists only within its sample); `x` is a cross-product.
  "countingStatisticsError": [
    { "sample": "Z-114",
      "bySamplingUnit": [
        { "samplingUnit": "spot-01",
          "byReportedProperty": [
            { "reportedProperty": "206Pb/238U date", "value": "±1.2 Ma (1σ)" }
          ] }
      ] }
  ]
}
```

**The schema can express the relationship; it cannot enumerate the members.** `Analyte` defines the
analyte domain, but *which* analytes exist is content supplied when a procedure is registered. Generate
the array structure and, if you want referential integrity, a validation rule that keyed entries must
reference an id present in the defining field's value.

---

## 5. Tiers — Columns C and D

These drive requiredness. They are independent; read both.

**Column C — Procedure-Level Tier**

| Value | Meaning |
|---|---|
| `Basic` | Mandatory to register a valid procedure |
| `Advanced` | Optional; strongly recommended |
| `N/A` | Not applicable at procedure level — this field captures analysis-level information only |

**Column D — Analysis-Level Tier**

| Value | Meaning |
|---|---|
| `Read-Only` | Imported from the registered procedure; the analyst cannot change it. Changing it means running a different procedure |
| `Editable` | Imported from the procedure but adjustable within procedure-defined bounds (daily tuning, minor deviations) |
| `Basic` | **Mandatory input at analysis time.** The value cannot be known until the analysis runs |
| `Advanced` | Optional input at analysis time |

**`N/A` is not a valid Column D value.** Every field carries a meaningful analysis-level assignment.
If you encounter `N/A` in Column D, the file is malformed.

### Mapping to requiredness

| C | D | Procedure schema | Analysis schema |
|---|---|---|---|
| `Basic` | `Read-Only` | required | required, immutable, inherited |
| `Basic` | `Editable` | required | required, inherited, may be overridden |
| `Basic` | `Basic` | required | required, supplied fresh |
| `Advanced` | any | optional | per D |
| `N/A` | `Basic` | **absent** | required, supplied fresh |
| `N/A` | `Advanced` | **absent** | optional, supplied fresh |

Two structural guarantees: `Read-Only` and `Editable` at analysis level always correspond to `Basic` or
`Advanced` at procedure level (you cannot inherit what was never specified), and `C=N/A` always pairs
with `D=Basic` or `D=Advanced`.

---

## 6. Data types — Columns E and F

Column E is a controlled vocabulary. Column F's meaning **depends on Column E**, which is the single
most important thing to get right in this section.

| Column E | Column F contains | Suggested JSON |
|---|---|---|
| `Text (free)` | *Examples*, usually prefixed `e.g.,`, pipe-separated | `"type": "string"` — **do not** turn F into an `enum` |
| `Controlled list` | *The enumeration*, pipe-separated | `"enum": [...]` from splitting F on `\|` |
| `Controlled list / Text` | The enumeration, but an unlisted value is permitted | `anyOf: [enum, string]` |
| `Numeric (<unit>)` | Examples | `"type": "number"`, unit from inside the parentheses |
| `Numeric + unit` | Examples | Number **and** unit both supplied by the user; unit is variable |
| `Integer` | Examples | `"type": "integer"` |
| `Boolean` | — | `"type": "boolean"` |
| `Date` | — | `"type": "string", "format": "date"` (`YYYY-MM-DD`) |
| `URI / DOI`, `URI / IGSN`, `URI / DOI / Text` | Examples | string with a format/pattern |
| `X / Text` (any compound) | Structured value, with free text as a permitted fallback | `anyOf` |

Notes that will bite otherwise:

- **Units are embedded in Column E**, not separate: `Numeric (s)`, `Numeric (L/min)`, `Numeric (J cm⁻²)`,
  `Numeric (%)`. Extract with `^Numeric \((.+)\)$`. `Numeric + unit` is different — it means the unit is
  *not* fixed and must be supplied alongside the value.
- **Controlled lists are pipe-delimited**, and entries may contain parenthetical glosses:
  `None (STD mode) | KED (He) | DRC (NH3) | Not installed | N/A | Other: specify`.
- **`N/A`, `None` and `Other: specify` are legitimate members**, not nulls or placeholders. Every
  controlled list is required to offer `N/A` and `None` (and `Other: specify` for non-compound lists),
  so an open-world enum is the right model. `N/A` in particular carries meaning — see §7.
- Column F for `Text (free)` fields is illustrative. Treating those pipes as an enumeration is the most
  common way to over-constrain a generated schema.

---

## 7. Conditional applicability lives in Column B

There is no machine-readable conditional column. Where a field applies only under some condition, the
condition is stated as a sentence at the end of Column B, and `N/A` is offered in Column F:

> *"Record 'N/A' where EDS is not listed in Spectroscopic Detector(s)."*
> *"Record 'N/A' where Collision/Reaction Cell (CRC) Configuration does not include KED."*
> *"Record 'N/A' where 4D-STEM is not listed in Analytical Sub-mode."*

These follow the pattern `Record 'N/A' where <Field Name> <condition>.` and reference the governing field
by its exact Column A name. They are extractable with a regex if you want `if`/`then` schema constructs,
but the canonical representation is simply that `N/A` is a permitted value. This was a deliberate design
choice over adding a `Conditional On` column — there are only about 40 such rows library-wide.

---

## 8. Mode flags

The columns between `Keyed By` and the `Literature Assessment` sentinel. One per analytical mode, values
**`Y` or `N` only** (never `N/A`, never blank on a content row). `Y` means the field applies to that mode.

Mode sets are declared per TAPP and vary in size from 0 to 11:

| TAPPs | Modes |
|---|---|
| Solution Q / SF / MC-ICP-MS | **none** — no mode columns at all |
| LA-Q / LA-SF / LA-MC (+ U-Pb variants) | Spot, Transect, Mapping |
| EPMA, SEM_Composition | EDS Point Analysis, EDS Mapping, WDS Point Analysis, WDS Mapping |
| TEM | TEM Imaging, STEM Imaging, Electron Diffraction |
| Lab-XCT | Single-volume, Multi-volume stitching |
| SEM_Imaging | SE Imaging, BSE Imaging, CL Point Analysis, CL Mapping, EBSD |
| SEM_FIBSEM | TEM Sample Preparation, 3D Tomography |
| SEM (full) | all 11 of the SEM-family modes |

Every TAPP also carries a field named `Analytical Mode` (Group 4) whose value declares which modes a
given procedure actually executes. A procedure may declare more than one.

Modes are **not mutually exclusive** — a field may be `Y` for several, and a procedure may run several.
The natural schema treatment is a `modes` array on the procedure plus conditional requiredness: a field
is applicable if any declared mode has `Y`.

---

## 9. Modules → `$defs`

This is the biggest structural win available and it is easy to miss from the spreadsheets alone.

The TAPPs are **composed, not copied**. Shared field blocks live in `Claude Skills for TAPP/modules/`
as a CSV plus a JSON manifest, and are built into consuming TAPPs by script. A field appearing in
several TAPPs is not a coincidence — it is one definition, guaranteed identical in Columns A–E and I.

| Module | Fields | Consumers | Layer |
|---|---|---|---|
| `ArAr` | 16 | 0 (built, unconsumed) | 3 |
| `Core` (Universal TAPP Core) | 30 | 16 | 2 |
| `Geochronology` | 6 | 3 | 2 |
| `LaserAblation` | 18 | 6 | 2 |
| `MCICPMS` | 15 | 3 | 2 |
| `SolutionIntroduction` | 16 | 3 | 2 |
| `TargetSelection` | 2 | 13 | 2 |
| `CalibrationFactor` | 1 | 14 | 2 |
| `Blank` | 1 | 12 | 2 |
| `Aggregation` | 2 | 13 | 2 |
| `UPb` | 15 | 3 | 3 |

**`Group1` no longer exists.** It was retired on 2026-08-14 into **`Core`**, which holds its 18
procedure-identification fields plus the 10 fields present in all 16 TAPPs that previously belonged to
no module — four in Group 2 (`Sample Name`, `Sample Persistent Identifier`, `Target Material`,
`Sampling Unit`), two in Group 3 (`Acquisition Software`, `Data Processing Software(s)`), two in
Group 4 (`Analytical Mode`, `Reported Variables and Units`), one in Group 5 (`Constants and Reference
Values Used`) and one in Group 6 (`Additional Notes`). If you had a `Group1` `$def`, rename it and add
those ten. The retired module files are in `Archive/Superseded Modules/`.

`Core` is **unconditional and all-or-nothing**: every one of its 30 fields is present in every one of
the 16 TAPPs. Its six blocks exist only because the fields insert into six different groups — they are
always composed together, so it emits **one** `$def`, not six. The same is true of every other module —
see the note on `ReportingCore` below.

**Generate one `$def` per module and `$ref` it**, rather than emitting 16 copies of the 28 Core fields.
`composed_tapps.json` tells you which modules each TAPP consumes and at which version. The module CSVs
have the same column layout as a TAPP but only columns A–F and I are meaningful — the module owns field
name, description, tiers, data type and `Keyed By`; the consuming TAPP owns examples, comments, dates and
mode flags.

Consequence for round-tripping: **a schema change to a shared field should be made once, at the module
level.** Editing the same field in 16 places is what the module system exists to prevent.

**`ReportingCore` no longer exists — and with it, the last reason to complicate this.** It was the only
conditional module: its six fields were not universal, its five blocks each carried an `applies_when`,
and each TAPP selected only the blocks that applied. On 2026-08-14 it was **dissolved into four
ordinary modules**, because its blocks had four *different* consumer footprints and were therefore four
independent modules sharing one file:

| new module | fields | consumers | applies when |
|---|---|---|---|
| `TargetSelection` | `Target Selection Criteria`, `Pre-Analysis Imaging and Screening` | 13 | the procedure analyses a selected part of a sample, not the bulk |
| `CalibrationFactor` | `Calibration Factor and Determination Method` | 14 | the reported quantity depends on an externally calibrated factor |
| `Blank` | `Procedural Blank Level` | 12 | the technique has a measurable analytical blank |
| `Aggregation` | `Analysis Inclusion and Rejection Criteria`, `Goodness-of-Fit or Dispersion Statistic` | 13 | the procedure combines multiple analyses into one reported value |

**Consequence for you: "one `$def` per module" is now true without exception**, and there is no block
machinery to model. A TAPP either composes a module — and then holds *every* one of its fields — or does
not. `composed_tapps.json` lists exactly which. The earlier advice to emit one `$def` per block applied
only to `ReportingCore` and is now obsolete; if you keyed `$def` names on its block names, three of the
four carry straight over (`target_selection` → `TargetSelection`, `calibration_factor` →
`CalibrationFactor`, `blank` → `Blank`), and `aggregation` + `aggregation_qc` merge into `Aggregation`.

The field-level facts are unchanged: `Procedural Blank Level` is still absent from TEM and Lab-XCT (no
analytical blank), and `Target Selection Criteria` is still absent from the three Solution TAPPs (bulk
techniques). What changed is that this is now expressed by which modules they compose.

---

## 10. Seven universal fields worth special handling

| Field | Group | Why it matters |
|---|---|---|
| `Session Identifier` | 1 | Identifies the session an analysis record describes — the laboratory's own run/sequence/batch id. Added with Rule 13 (2026-08-12). Present in all 16. |
| `Sample Name` | 2 | `defines: sample` — enumerates the samples covered by the session, and is the definer for the `sample` key. C=N/A, D=Basic in every TAPP. Present in all 16. |
| `Sample Persistent Identifier` | 2 | One IGSN (or equivalent) **per sample**, keyed `sample`. Note that `sample` and `standard` overlap: a secondary reference material is run through the same calibration as an unknown, so it legitimately appears in both domains. **Do not model them as disjoint.** Present in all 16. |
| `Reported Variables and Units` | 4 | Enumerates the reported-property domain **and declares the procedure's scope boundary** — what this procedure reports, and therefore where it stops. A derived quantity inside that list is in scope; anything beyond it belongs to a separate, coupled procedure. Present in all 16. |
| `Sampling Unit` | 2 | Declares the physical subdivision one row of reported values corresponds to (grain, spot, aliquot, phase). Without it a consumer cannot tell whether a reported value is per grain or per sample. Present in all 16. |
| `Constants and Reference Values Used` | 5, always last in the group | Physical constants and reference values used in data reduction, with sources — decay constants, reference isotope ratios. Needed to reinterpret a reported value against a later revision of a constant. Present in all 16. |
| `Additional Notes` | 6, **always the last field of the whole TAPP** | Free-text catch-all whose scope is the entire document, not Group 6 — its position is what says so (Rule 11). Present in all 16. In a schema it is one optional string on the root object, not a Group 6 property. |

Group 1 also always ends with four coupling fields in this order — `Coupled Technique(s)`,
`Coupling Description`, `Coupled Procedure DOI`, `Coupled Dataset or Publication Reference` — which
express that this procedure was run alongside another. That is the mechanism for chaining procedures
(e.g. an OSL age needs a separately measured dose rate), and it maps to a reference between records.

---

## 11. Gotchas

1. **Don't parse the xlsx.** It is generated from the CSV. Colour encodes the tier already present in
   Columns C/D, and the Legends sheet is documentation, not data.
2. **Column G is now 45% populated, and all of it is provenance.** Since 2026-08-14 every module-supplied field names its module (`Source: <name> module`); 767 of 1706 rows. A blank cell means the field belongs to no module. Documentation only, not schema content — see §3.1.
3. **Don't hard-code column indices past I.** Mode-block width varies 0–11; find `Literature Assessment`.
4. **Three TAPPs have no mode columns at all.**
5. **Match A–I by position, not header text** — Columns B and F have two spellings each.
6. **Literature assessment columns are evidence, not schema.** They record what a specific paper reported
   for that field, for coverage assessment. Exclude them from the schema; they may be useful as example
   data.
7. **`N/A` and `None` are values.** Do not coerce to `null`.
8. **Don't build one global field-name → type map.** Five fields are technique-dependent by design (§4),
   and a few field names recur with technique-appropriate descriptions.
9. **Superscripts and Greek matter.** `²⁰⁶Pb/²³⁸U` and `206Pb/238U` should not be silently normalised —
   the notation is part of the reported-variable identity.
10. **Filenames carry versions that move.** Resolve via `composed_tapps.json`.

---

## 12. Validating your understanding

Three scripts in `Claude Skills for TAPP/scripts/` encode the structural rules, and reading them is
faster than reading the prose spec:

- `validate_tapp.py` — every structural invariant, as executable checks. **This is the best single
  reference for what a well-formed TAPP looks like.** Run `--root .` to lint the whole library; the
  current baseline is 0 ERROR, 0 WARN.
- `compose_tapp.py` — how modules are built into TAPPs, including column ownership.
- `tapp_to_xlsx.py` — the CSV→xlsx export, including the Legends sheet content.

Authoritative documentation, in reading order:

| File | Contents |
|---|---|
| `Claude Skills for TAPP/references/conventions.md` | The specification. Rules 1–13; Rule 7 covers `Keyed By`, Rule 13 the session/sample split |
| `Claude Skills for TAPP/references/precedents.md` | Why specific decisions were made; useful when a field looks anomalous |
| `Claude Skills for TAPP/SKILL.md` | Overview and common mistakes |
| `composed_tapps.json` | Machine-readable registry of TAPPs and their modules |
| `Project Files/Design Notes/TAPP_Development_Log.md` | Dated change history |

A good first sanity check: parse one TAPP, count content rows, and confirm you get the same number
`validate_tapp.py` reports. If your parser is counting group headers or separator rows as fields, that
will surface immediately.
