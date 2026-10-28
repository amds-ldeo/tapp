# Rule 14 sweep: fields that hold dataset values — findings, for RD review

2026-10-26. Status: **APPLIED 2026-10-27** (`Project Files/Scripts/rule14_sweep_20261027.py`). RD agreed proposals 1–5, the rename and the Detection Limit sentence; **proposal 6 was declined**: Analysis Location/Spot Coordinates stays, because coordinates are a property of the sampling unit. Correction: rows 3 and the Inherited field are owned by **Module_Geochronology**, not TAPP-owned. `check_field_ownership.py` missed block-less manifests, and was fixed the same day. Follows conventions.md Rule 14
(rules in the TAPP, results in the dataset), which left this sweep open in 14.4.

## Method

All 358 distinct fields across the 16 current TAPPs. A field was a candidate if its procedure
tier is N/A (it exists only in the session record), or if its Column B asks for a value, result,
count, uncertainty or statistic: 99 candidates. Every candidate description was read. The full
name list was then scanned for results phrased some other way (abundances, porosity, phase
assignments); it added none.

Each field was put to the Rule 14.1 test: does the value describe a **sample** (data table) or the
**measurement** (methods section)? For the fields that failed, the literature cells were read as a
second test.

## Result: 6 fields hold results on samples

The literature agrees, and strongly. Five of the six have **no** attestation in any methods section
(194 cells, every one N): papers print these values in their data tables. The sixth, Internal
Precision, has 9 positive cells, and each names the *statistic* ("2SE of individual measurements"),
not a value.

| # | Field | TAPPs | Owner | Current key | Lit (non-N / N) | What is data | What stays |
|---|---|---|---|---|---|---|---|
| 1 | Counting Statistics Error | 12 | Module_CompositionQC | sample > sampling unit x reported property | 0 / 113 | the uncertainty of each analysis | how it is computed, and the sigma level |
| 2 | Internal (Within-Measurement) Analytical Precision and Assessment Method | 9 | Module_ICPMS | sample > sampling unit x reported property | 9 / 48 | the precision of each measurement | the statistic, and the cycles it is computed over |
| 3 | Radiogenic Fraction of Measured Signal | 3 (U-Pb) | TAPP-owned | reported property | 0 / 13 | the fraction for each analysis | nothing: the correction is Inherited or Initial Signal Correction |
| 4 | Discordance Definition and Values | 3 (U-Pb) | Module_UPb | pair: reported property | 0 / 13 | "the discordance values obtained" | the definition (formula) |
| 5 | Error Correlation Between Reported Quantities | 4 | TAPP-owned; **mandated by Rule 10** | pair: reported property | 0 / 27 | ρ for each analysis | which pairs, and how ρ is obtained |
| 6 | Analysis Location/Spot Coordinates | 6 (LA) | Module_LaserAblation | sample > sampling unit | 0 / 28 | each spot's coordinates | nothing |

## Proposals

Same pattern as Module_Aggregation v6: keep the method, move the value, end Column B with an
`In the dataset:` sentence.

1. **Counting Statistics Error** → the method only: what the uncertainty is computed from (the
   peak and any subtracted background or blank) and at what sigma. Key → `reported property`;
   tiers Advanced / Editable (now Advanced / Basic). *In the dataset: report, for each analysis and
   reported quantity, the counting-statistics uncertainty at the stated sigma level.*
2. **Internal Precision** → the statistic and the number of cycles, sweeps or integrations it is
   computed over (what its 9 attested cells already hold). Key → `reported property`; tiers
   Advanced / Editable. *In the dataset: report, for each measurement and reported quantity, the
   internal precision.*
3. **Radiogenic Fraction of Measured Signal → retire.** Nothing procedural is left. Its dataset
   sentence moves to Inherited or Initial Signal Correction: *In the dataset: report, for each
   analysis, the radiogenic fraction of the measured signal.*
4. **Discordance Definition and Values** → the definition only. **Rename to "Discordance
   Definition"?** A rename is a schema change (a migration note, plus RETIRED_FIELDS for the old
   name). *In the dataset: report the discordance of each analysis.*
5. **Error Correlation Between Reported Quantities** → which pairs are correlated and how ρ is
   obtained. *In the dataset: report ρ for each analysis and pair.* **Rule 10 mandates this field
   and must be amended in the same change**, since the field it mandates would no longer hold the
   coefficient.
6. **Analysis Location/Spot Coordinates → retire, or keep?** This one is the least clear-cut.
   Coordinates are not a result; they record where the measurement was made. But they are an
   attribute of each spot and are printed in data tables, and the record already links to each
   spot through Sampling Unit Name (Rule 13). Proposal: retire, and give Sampling Unit Name the
   sentence *In the dataset: give each sampling unit's location (stage coordinates, or a position
   relative to a named feature).*

## Checked and kept (pass the 14.1 test)

- **Measurement performance**, as 14.1 names it:
  - detection limits (all variants), Procedural Blank Level;
  - the precision and accuracy family (6 fields), Calibration Factor and Determination Method.
- **Session tuning and acquisition outcomes:**
  - Oxide Production, Doubly-Charged Species Production, Peak Flatness;
  - Instrument Sensitivity, EDS Dead Time, Spot Diameter (Measured), Signal Integration Time.
- **Image-quality outcomes:**
  - Lab-XCT: Signal-to-Noise Ratio, Effective Spatial Resolution, the three artifact assessments,
    Partial Volume Effect Assessment, Cross-Validation Outcome;
  - EBSD: Mean Angular Deviation, Indexing Rate.
- **Extents of what was acquired:**
  - map and EDS map dimensions, Map Area, Mapping Area, Transect Length;
  - VOI Applied, the sub-volume fields, Total Scan Duration, voxel and image-stack dimensions.
- **Record identity and provenance (Rule 13):** Sample Name, Sampling Unit Name, Target Material
  of Sampling Unit, Sample Persistent Identifier, plus the session identity fields.

## Out of scope, noted

1. **A different boundary: sample metadata.** Sample Description, Sample Mass and Sample
   Dimensions describe the specimen, and arguably belong in the sample registry (IGSN/SESAR), not
   the dataset and not the TAPP. That is a separate question from Rule 14.
2. **A Rule 7 question, not a Rule 14 one.** Several of the acquisition extents are keyed `(none)`
   although a session with several maps or transects has one per map. Examples: Map Dimensions,
   Map Area, Mapping Area, Transect Length.
3. **A possible exception.** Detection Limit allows "session-specific measured values". Where a
   procedure computes a detection limit for each analysis (common in EPMA), that per-analysis
   value is dataset content. The field itself stays.

## Decisions for RD

1. Apply proposals 1–5 as written?
2. Proposal 6: retire Analysis Location/Spot Coordinates, or keep it?
3. Rename "Discordance Definition and Values" → "Discordance Definition"?
4. Detection Limit: add a sentence, *In the dataset: report the detection limit of each analysis,
   where the procedure computes one*?

**Scope if all are applied:** 4 modules (CompositionQC, ICPMS, UPb, LaserAblation) plus 2
TAPP-owned fields, reaching about 14 TAPPs, plus a Rule 10 amendment.
