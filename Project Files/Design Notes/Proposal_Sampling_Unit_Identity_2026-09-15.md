# Proposal: name the sampling units — split the unit type from the units

**2026-09-15. Decisions D1–D5 taken as recommended (Ruolin Deng, same day). APPLIED the same day: Module_Core v8, all 16 TAPPs, Rule 9 rewritten.** See §5 for each decision and §9 for the sandbox result. Raised by amds-ldeo/tapp#8 (Stephen Richard):
*"along with Sample Persistent Identifier, won't we need to have a sampling Unit identifier that is
related to its parent sample?"* The answer is yes. The gap it points at is a Rule 7.4a breach that
has stood since `Sampling Unit` was given `defines: sampling unit`.

Proposes one new field and one changed field, both in Module_Core, reaching all 16 TAPPs. Five
decisions in §5, each taken as recommended.

---

## 1. The defect: the `sampling unit` domain has a definer that cannot list it

`Sampling Unit` is keyed `defines: sampling unit`. Rule 7.4a says a definer must list the members of
its domain, because "a key whose domain is never enumerated cannot be populated". But the field's
values are **types**, from a controlled list:

```
Whole sample | Aliquot | Grain | Spot | Analysis point | Phase | Sub-volume | Region of interest | N/A | None
```

"Spot" says what kind of unit was analysed, not which units. It is the same failure 2026-09-08 found in
`Number of Digestion Steps`, where a count gave "rows with no identity". A type does the same: a
consumer cannot attach "20 nA" to "Spot".

And the domain has consumers. **46 field-instances across 12 fields** are keyed by it, all in the
containment form (25 as `sample > sampling unit`, 21 as `sample > sampling unit x reported property`):

| Field | Keyed By | TAPPs |
|---|---|--:|
| `Counting Statistics Error` | `sample > sampling unit x reported property` | 12 |
| `Internal (Within-Measurement) Analytical Precision and Assessment Method` | `sample > sampling unit x reported property` | 9 |
| `Analysis Location/Spot Coordinates` | `sample > sampling unit` | 6 |
| `Beam Mode`, `Beam Current`, `Beam Diameter`, `Beam Raster Dimensions`, `Beam Damage Minimization` | `sample > sampling unit` | 3 each |
| `Phase Identification Method` | `sample > sampling unit` | 2 |
| `Segmentation Threshold Values or Criteria`, `Partial Volume Effect Criteria` | `sample > sampling unit` | 1 each |

Every one of those is a child table whose rows have nothing to identify them by. `Analysis
Location/Spot Coordinates` is the sharpest: it records *where each unit is*, for units that are never
named.

Samples already have the structure this is missing. Rule 13 gives `Sample Name` `defines: sample`
(C=N/A, D=Basic, free text), with `Sample Persistent Identifier` keyed by the domain it defines.
Sampling units have only the type.

---

## 2. How it got here: one field was meant to hold both, and the split made that invisible

This was not an oversight in Rule 9. Its canonical text meant `Sampling Unit` to carry **both**:

> "State the unit type at procedure level **and the units actually analysed at analysis level**."
> Example / Allowed Content: the type list "**+ free text for the instances analysed**".
> **Why D=Basic:** "the units actually analysed — which grains, which spots, which phases — cannot be
> known until the session runs."

On 2026-08-25, step 2 of the Description/Purpose split **deleted that sentence** as
`REWRITE-REDUNDANT (C=Basic + D=Basic)`. The tiers were taken to say it already. They cannot:

- **D=Basic means the value is supplied fresh at analysis time.** The analysis value *replaces* the
  procedure value rather than adding to it. One cell holds the type at registration and would have
  to hold a member list at analysis. Those are two different kinds of information in one field.
  This is Common Mistake #1, and the reason the Oxide Production pair was split.
- **Neither half is keyable.** A free-text list of instances in the cell a controlled type list
  occupies is not something a schema generator can turn into rows.

So the dual design was never representable, and the deletion removed the only sentence that showed
it was intended.

---

## 3. Evidence: what the literature cells record

`Sampling Unit` has **177** literature cells across the 16 TAPPs: **44** with content, **2** `N`,
and **131 blank** (never asked; most of the electron-beam and LA corpus).

- **All 44 contentful cells record the type.** Some add a count or a nesting path: "Digestion
  aliquot", "Laser spot — 246 spot analyses", "Region of interest (individual fluid inclusion) >
  Phase".
- **A few name the units anyway, because the paper does.**
  - López-García et al. 2026: individually weighed Bennu particles *A0066, A0238, A0247 …*
  - Genge et al. 2025: sub-samples *A0180-A* and *A0180-B*.
  - Barnes et al. 2025: the ETH aliquot *OREX-803015-100*. This one currently sits in
    `Sample Name`, and whether it is a sample or a sampling unit of the aggregate is exactly the
    ambiguity this proposal resolves.
- **One case cannot be listed at all.** Neuman et al. 2025 (EPMA) makes every map pixel a quantitative
  analysis point: 1,024 × 1,024 per stage map, about 20 × 10⁶ in all. Any design must say what gets
  named when units run to millions (§5, D4).

The field was never asked for identities, so the corpus does not measure how often papers name their
units. The cases above show it happens, and that the type alone cannot carry it.

---

## 4. The model

Split the one field into two, in Group 2, following Rule 13's sample pair:

| Field | C | D | Data Type | Keyed By | Role |
|---|---|---|---|---|---|
| **`Sampling Unit Type`** — renamed from `Sampling Unit` (D2) | Basic | Read-Only (D3) | Controlled list / Text | `(none)` | the kind of unit the procedure is designed to analyse |
| **`Sampling Unit Name`** — new | N/A | Basic | Text (free) | `defines: sample > sampling unit` (D1) | lists the units analysed in this session, each within its sample |

Draft descriptions:

- **`Sampling Unit Type`.** The kind of physical subdivision of the sample to which one row of
  reported values corresponds — the unit that is analysed and reported, as distinct from the sample
  as a whole. Where units nest (e.g. confined tracks within grains), state both levels. The units
  themselves are listed in `Sampling Unit Name`.
- **`Sampling Unit Name`.** The name or label of each sampling unit analysed in this session, as the
  laboratory records it, together with the sample it belongs to — e.g. a spot number, a grain label,
  a map or region-of-interest name, or an aliquot identifier. Where units are too numerous to name
  individually, such as map pixels or reconstructed voxels, name the acquisition area they belong to
  instead.

**Placement.** `Sampling Unit Type` stays where `Sampling Unit` is. `Sampling Unit Name` goes
immediately after it.

What this changes for the 46 consumers: **nothing in their rows.** Their key stays `sample > sampling
unit`. It now points at a field that actually lists the domain, with each unit's parent sample
attached.

---

## 5. Decisions needed

**D1 — the definer's notation. DECIDED as recommended.** Recommended: **`defines: sample > sampling unit`**.

| Option | For | Against |
|---|---|---|
| **`defines: sample > sampling unit`** | Matches the containment form all 46 consumers already use. States that every unit belongs to a sample. | New definer grammar: the validator's key parser, 7.3/7.4 in `conventions.md` and the schema README's key table all need a line. |
| `defines: sampling unit per sample` | Existing notation, no grammar change. | 7.3.1 documents the `per` parent as **nullable** ("a consumer must assume partial"). A schema generator following it would make the parent optional, which is wrong: a sampling unit with no sample does not exist. |
| plain `defines: sampling unit` | No change at all. | No parent link, which is the gap #8 raised. |

The rule against minting grammar ahead of users does not apply: the users already exist (46).

**D2 — rename `Sampling Unit` → `Sampling Unit Type`. DECIDED as recommended.** Recommended: **yes.** After the split, a field
named `Sampling Unit` that no longer defines `sampling unit` is exactly the confusion #8 started
from. Cost: a `RETIRED_FIELDS` entry, Rule 9's text, the documents naming it, the mockups, and a
renamed property downstream. The blocks composition path does not handle renames, so this needs a
rename-aware script (`bump_samplingunitselection_20260901.py` is the template). The alternative,
keeping the name, costs less and leaves the ambiguity in place.

**D3 — `Sampling Unit Type`'s analysis tier. DECIDED as recommended.** Recommended: **Read-Only.** Every contentful literature
cell records the type once per procedure column, the same shape as `Analytical Mode` (C=Basic,
D=Read-Only): analysing grains instead of spots is a different procedure. Choose **Editable** if
sessions are expected to mix unit types under one registered procedure. No evidence of that was
found, but it was not specifically sought.

**D4 — units that cannot be named individually. DECIDED as recommended.** Recommended: **name the acquisition area** (map,
sub-volume, region of interest) and treat pixel- or voxel-level values as data, not metadata rows.
This is written into the draft description above. The alternative is a range or pattern syntax
("pixels 1–1,048,576 of map 3"), which invents structure no consumer has asked for.

**D5 — sub-sample persistent identifiers. DECIDED as recommended (deferred).** Recommended: **defer.** `Sample Persistent Identifier`
currently says "where a sample and its sub-samples are separately registered, record the identifier
at the level actually analysed", so a sub-sample IGSN lands in the sample's field. A `Sampling Unit
Persistent Identifier` (C=N/A, D=Advanced, `URI / IGSN`, keyed `sample > sampling unit`) would fix
that. But the corpus has not been checked for sub-sample IGSNs, and 7.4c wants an attested consumer
first.

---

## 6. What this proposal does NOT do

- **It does not settle nested units.** The G2 deferral (conventions, Rule 7 decisions) waits for "a
  TAPP that populates a nested sampling unit". **That trigger has now been met:** Lab-XCT's literature
  cells show two-level nesting six times ("Sub-volume > Grain", "Region of interest > Phase" ×4, "Whole
  sample > Phase"). This proposal keeps "state both levels" as free text and recommends reopening G2
  as its own decision.
- **It does not re-extract anything.** The 44 type cells move with the renamed field unchanged.
  `Sampling Unit Name` starts blank in every literature column. That is a Phase 3 backlog of 177
  procedure columns, and blank correctly reads as "not asked".
- **It does not change the 46 consumers.** Their keys and rows stay as they are.
- **It does not touch Module_SamplingUnitSelection.** `Pre-Analysis Imaging and Screening` asks "how
  individual analyses are linked back to the images". Once units have names, that link has something
  to point at, and its description can say so in a later pass.

---

## 7. Cost

| | |
|---|---|
| Module_Core | v7 → v8: 1 field renamed, re-keyed and re-tiered; 1 field added |
| TAPPs | all 16 recomposed with a rename-aware script; +1 row each |
| literature cells | 44 move with the rename unchanged; 177 new blank cells |
| rules | Rule 9 rewritten; Rule 13's table gains a row, or Rule 9 carries both fields; 7.3/7.4 gain the definer form (D1) |
| validator | key parser accepts `defines: A > B` (D1); `RETIRED_FIELDS` entry (D2) |
| key audit | definer detection must read the new form, or it will report `sampling unit` undefined |
| documents | schema README §1, §4 (key table and prose) and §10; the three mockups |
| downstream | geochemBuildingBlocks: one renamed property, and the `samplingUnits` array gains its key field |

---

## 8. What would reverse this

- **A schema consumer that holds unit identity in the data file, not the metadata record.** The
  definer would then point at the data file's unit column rather than list names. That changes D1 and
  D4, not the split.
- **Routine mixing of unit types within one session** would move D3 to Editable.
- **A technique whose units are unnameable at every level**, not just at pixel scale, would make
  `Sampling Unit Name` empty by design. That would argue for a different anchor for that technique,
  not against the field.

---

## Before applying

Run it in a sandbox first, as the `monitored property` proposal did:
- recompose all 16 TAPPs with the renamed and added fields;
- confirm the row counts (+1 each) and that the 46 consumers are byte-identical;
- confirm the validator's 7.4a/b/c checks pass with the new definer.

---

## 9. Sandbox result, 2026-09-15

Run on a 42 MB copy of the library (skill folder, `Current TAPPs/`, `Project Files/`, the module
archive, the schema README, `composed_tapps.json` and the 16 working CSVs). Its baseline matched the
real library exactly: 0 ERROR / 0 WARN / 37 INFO, 16 MATCH. The migration script was
`split_sampling_unit_20260915.py`.

**The data change behaved as designed:**
- **Rows:** in all 16 TAPPs, exactly +1 row, `Sampling Unit Name`, directly after `Sampling Unit
  Type`, with blank literature cells.
- **The renamed row** changed in Columns A, B, D, H and I only. C (Basic), E and Column F's type list
  are unchanged, and its literature cells carried over.
- **Every other row is byte-identical,** including all 46 consumers.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH.
- **Rule 7.4a/b/c** pass with the new definer: `sampling unit` has exactly one definer in every TAPP,
  and `sample` is still defined once, by `Sample Name`.
- **Key audit:** all 61 findings are identical.
- **Mockups:** all three rebuilt with `defines: sample > sampling unit` in their data and no remaining
  reference to the old definer key.

**What the tooling needed:**
- **`validate_tapp.py`**
  - `parse_keyed_by` must recognise `defines: A > B`. Without it, the form parses as defining both
    `sample` and `sampling unit`, which is a multiple-definers ERROR against `Sample Name`. It is now
    kind `defines_in`, with the domain on the right and the parent as a used key; both sides are
    restricted to a single key, as for `per`.
  - `RULE9_FIELD` renamed; `Sampling Unit Name` made mandatory and exempted from 7.4c alongside it.
  - `Sampling Unit` added to `RETIRED_FIELDS`, with a guard for the live names it heads (`Type`,
    `Name`, `Selection`). Without the guard the substring test flags every document naming
    `Sampling Unit Selection Criteria`, and the module register's "Sampling Unit Selection" title.
- **The mockup page script (`_body.html`)** looks up each domain's definer by exact key and strips
  only a `per` suffix. Without the fix, the sampling-unit domain silently shows as "not established".
- **`build_schema_spec_counts.py` had the real library's path hard-coded.** In the sandbox it
  checked the real repo and reported "up to date" while the copy's counts went stale: 1,781 content
  rows recorded against 1,797 actual. Nothing was written to the real repo, which was verified clean.
  Fixed to resolve its root from its own location; this fix is worth taking regardless of this
  proposal.

**Remaining findings after those fixes:** 0 ERROR, and only the WARNs the real change resolves in the
same pass:
- the schema README names `Sampling Unit` in four places (§4 prose, §9 Core list, §9 rename note,
  §10 table);
- the Reports README points at the pre-bump mockup versions.

**Not exercised in the sandbox:** the mockup page's JavaScript in a browser (no JS runtime available).
The data was checked, the rendering was not.

