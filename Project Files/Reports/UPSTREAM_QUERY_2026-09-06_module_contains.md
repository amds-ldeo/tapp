# Mandatory literal-pinned `contains` in the modules

**2026-09-06 · from the ADA/geochemBuildingBlocks side · a question, not a change**

Twenty-two constraints across ten modules require an array to *contain* an entry pinned to an
exact literal string. **None of those literals occurs anywhere in the 2,621-record ADA corpus.**
Where the constrained array is present in a record, the record cannot validate; where it is absent,
the constraint silently does nothing.

Nothing has been changed in the modules. This is a description of what we measured and a question
about which way you want it resolved.

**If you read one section, read §3** — that is the measurement.

---

## 1. The shape

Both halves of the pattern appear together. From `modules/core/schema.yaml:393`:

```yaml
schema:contributor:
  type: array
  items:
    type: object
    allOf:
      - if:                                    # (a) conditional — correct
          properties: {schema:roleName: {const: analyst}}
          required: [schema:roleName]
        then:
          properties: {schema:name: {...}}
  allOf:
    - contains:                                # (b) mandatory — the problem
        properties: {schema:roleName: {const: analyst}}
        required: [schema:roleName]
```

**(a) is right.** It says: an entry whose `roleName` is `analyst` must carry a name. It constrains
the entry that exists and is silent about the rest.

**(b) says something much stronger.** It says the array *must include* such an entry — that every
analysis record naming any contributor must name one whose `schema:roleName` is the exact
lowercase string `analyst`.

We think (b) may be doing the work of "the Analyst field is Basic at analysis level" — expressing
requiredness through the discriminator. If so, the requiredness is real but the placement forces a
vocabulary the data does not use.

---

## 2. Where they are

22 constraints, 10 modules. Consumer counts from `composed_tapps.json` (21 TAPPs, 5 of them our
drafts).

| module | consumers | array | required literal |
|---|---|---|---|
| `core` | 21 | `schema:contributor` | `analyst` |
| `core` | 21 | `schema:step` | `Sample preparation` |
| `calibrationFactor` | 19 | `schema:variableMeasured` | `Calibration Factor and Determination Method` |
| `aggregation` | 13 | `schema:variableMeasured` | `Goodness-of-Fit or Dispersion Statistic` |
| `aggregation` | 13 | `dqv:hasQualityMeasurement` | `Goodness-of-Fit` |
| `compositionQC` | 12 | `schema:variableMeasured` | `Detection Limit` |
| `compositionQC` | 12 | `schema:step` | `Data reduction` |
| `icpms` | 9 | `schema:variableMeasured` | `Limit of Quantification (LOQ) Method` |
| `icpms` | 9 | `dqv:hasQualityMeasurement` | `Oxide production ratio` |
| `mcIcpms` | 3 | `dqv:hasQualityMeasurement` | `Peak Flatness` |
| `solutionIntroduction` | 3 | `schema:step` | `Sample digestion` |
| `geochronology` | 3 | `schema:variableMeasured` | six literals, incl. `Age Model`, `Reported Date Type` |
| `uPb` | 3 | `schema:step` | `Sample preparation` |
| `reportingCore` | — | `dqv:hasQualityMeasurement` | `Dispersion Statistic`, `Goodness-of-Fit` |

`reportingCore` is the dissolved module; its file is still present.

---

## 3. What the corpus actually holds

2,621 ADA records. Occurrences of each required literal:

| module | array | required literal | records carrying it |
|---|---|---|---|
| `core` | `schema:contributor` | `analyst` | **0** |
| `core` | `schema:step` | `Sample preparation` | **0** |
| `aggregation` | `schema:variableMeasured` | `Goodness-of-Fit or Dispersion Statistic` | **0** |
| `aggregation` | `dqv:hasQualityMeasurement` | `Goodness-of-Fit` | **0** |
| `calibrationFactor` | `schema:variableMeasured` | `Calibration Factor and Determination Method` | **0** |
| `compositionQC` | `schema:variableMeasured` | `Detection Limit` | **0** |
| `compositionQC` | `schema:step` | `Data reduction` | **0** |
| `icpms` | `schema:variableMeasured` | `Limit of Quantification (LOQ) Method` | **0** |
| `solutionIntroduction` | `schema:step` | `Sample digestion` | **0** |

The discriminators do carry values — just not these:

```
schema:roleName          2 distinct:  'Researcher' (361)   'Other' (286)
dqv:isMeasurementOf      never present in any record
schema:step              never present in any record
```

`analyst` does not appear in the corpus at all.

---

## 4. Which bite now, and which are latent

`contains` applies only when the property is present, so the damage depends on how often ADA
populates each array:

| array | records present | effect |
|---|---|---|
| `schema:contributor` | **578 (22%)** | **fails now** — every one names `Researcher` or `Other` |
| `schema:variableMeasured` | **378 (14%)** | **fails now** for the technique's applicable literals |
| `schema:step` | 0 | latent — fires the moment ADA starts recording process steps |
| `dqv:hasQualityMeasurement` | 0 | latent — same |

The two latent ones are the more awkward, because they will start failing exactly when ADA improves
its metadata.

---

## 5. How we found it, and why it went unnoticed

Building draft TAPPs for five ADA-only techniques (VNMIR, QRIS, XRD, RAMAN, XANES) and validating
each against its own records.

VNMIR, QRIS and XRD came back clean — **but only because none of their 52 records carries
`schema:contributor` at all**, so the constraint never fired. RAMAN and XANES do carry it, and
failed: 4 of 4 and 46 of 241. We initially read the first three as evidence the schemas were sound;
they were evidence that those records don't exercise the constraint.

That is likely why this has stayed invisible. The `geochemProfile` `profile/` schemas that compose
these modules have effectively never been run against the corpus — a sample of `adaEMPA` and
`adaTEM` records fails them 40/40 and 40/40, on `schema:variableMeasured` and
`schema:additionalType`. The constraints are not wrong-looking; they are simply untested against
data.

---

## 6. The question

Three ways we can see, and the choice is a modelling one that belongs with you:

1. **Drop the `contains`, keep the `if/then`.** Requiredness moves to wherever the tier columns are
   expressed. The entry stays constrained when present; nothing is forced to exist.
2. **Keep it, and align the ADA vocabulary.** `schema:roleName` becomes `analyst` where the
   contributor is one, and ADA emits the named `variableMeasured` and `schema:step` entries. This
   is the larger change and lands on the ADA side, not yours.
3. **Keep it, and treat these profiles as aspirational** — a target the archive is working towards,
   not a gate. Then the profiles should probably not be the thing the forms application validates
   against.

Our reading is that (1) matches what Columns C and D already say, and that requiring a literal
`schema:name` inside `variableMeasured` is asking the reported-variable list to double as a
checklist of procedural fields. But we may be misreading the intent, particularly for
`dqv:hasQualityMeasurement`, where pinning `dqv:isMeasurementOf` is a reasonable way to say "this
specific quality measure must be reported".

---

## 7. What we did not do

- No module was edited. All 22 constraints are exactly as delivered.
- Our five draft TAPPs route *around* `aggregation` rather than through it — VNMIR, QRIS, XRD,
  RAMAN and XANES compose `Core`, `SamplingUnitSelection` and `CalibrationFactor` only. That was a
  modelling call (they report per-measurement results, not aggregated values), and it happens to
  avoid the `Goodness-of-Fit` constraint. It does not fix it for the 13 TAPPs that do compose it.
- The `core` `schema:contributor` constraint cannot be routed around: every TAPP composes `Core`.

## Reproducing

```
tools/… scan: modules/*/schema.yaml for  allOf[].contains.properties.<k>.const
corpus:      2,621 rows of core.JsonTable in the ADA forms database
```

Scripts available on request; the measurement is a single pass over the corpus counting literal
occurrences, and a single pass over the module YAML collecting `contains` discriminators.
