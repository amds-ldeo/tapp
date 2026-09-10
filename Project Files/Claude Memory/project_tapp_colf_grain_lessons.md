---
name: project-tapp-colf-grain-lessons
description: What 18 Column F backlog entries had in common — grain failures, axis leaks, and descriptions that misdirect; plus the measurement artefacts that fooled the scans
metadata:
  type: project
---

Distilled from clearing the Rule 7.8.11 backlog (2026-08-30/31) and the Data Type pass that
produced it. See [[project-tapp-datatype-two-type-scheme]] for what was applied and
[[project-tapp-colb-coli-survey]] for the check itself.

## The dominant defect was GRAIN, not missing members

A list pitched below the level at which its domain closes cannot be fixed by adding members —
extending it never terminates. Four entries were this, and each looked like "missing members"
in a gap scan:

| field | enumerated | domain |
|---|---|---|
| `Sample Mounting Method` | specific vessels (straw, capillary, wax) | any container |
| `Chromatographic Separation Applied` | resins (AG1-X8, TRU, UTEVA) | **24 attested cells, 24 distinct** |
| `Pulse/Analog Detector Nonlinearity Correction` | whole correction procedures, as sentences | unbounded |
| `Target Material` (LA half) | named minerals (feldspar, pyroxene, olivine) | no spinel, garnet, zircon… |

**The test:** could indefinitely many attested values be added as members without the domain
closing? If yes, raise the axis and let the `/ Text` half carry the specifics.

**The mirror image exists too.** `Electron Source` was too FINE — it demanded Cold vs Schottky
where the paper said only "FEG", so 14 cells fell into `Other:`. **A closed list whose members
carry a subtype needs a subtype-unstated member.** Both failures present identically in a scan.

## Second defect: a neighbouring field's value folded into the members

`FESEM` in `Instrument Variant` (belongs to `Electron Source`) · `fs-` in `Technique`
(`Laser Pulse Duration`) · the vendor in `WDS Dead Time Correction` (`Instrument Manufacturer`)
· `Iron meteorite` in `Target Material` (the bulk-specimen axis). Related: **combinatorial
members** — `FIB-SEM dual-beam + VP`, `{default,adjusted} x {Cameca,JEOL}` — which never survive
their axes being separated; use the `; ` join instead.

And **collisions**: `Not applicable (…)` against `N/A`; `Not applied` against `None`. Whichever
a curator picks, the other becomes noise.

## Where cells land on the wrong axis, the DESCRIPTION sent them there

`Primary Calibration Standard Name` read as though a reference material always exists, so
standardless answers scattered into two other fields. `Instrument Variant` collected `FESEM`
×10. `Coupled Technique(s)` said "use the same controlled vocabulary as the Technique field"
and 121 cells ignored it. **Fix the description, not just the members.**

## PRINCIPLED vs drift

**A member is principled if it names a capability, preparation or target the technique does not
have.** `EDS Acquisition Mode` (EELS is TEM-only), `Sample Preparation Method` (Solution
destroys the sample), `Target Material` (in-situ targets a phase, bulk targets the specimen),
`ICP-MS Type`. Harmonise the shared core, keep the scoped extras. **Check the overlap for
wording drift even when the verdict is PRINCIPLED** — `Sample Preparation Method` had none and
needed no edit at all.

## Measurement artefacts — five, all found by READING

1. `N (not stated) [P4]` — the not-reported sentinel written long-form, counted as an extraction
2. `[P4]` provenance tags scored as content
3. `(stated section 3.1)` / `(explicitly stated: "…")` embedded inside values
4. a parenthetical that is part of the term (`Field Emission (FEG)`, `Normal plasma (1000 W RF)`)
5. **`None` / `N/A` counted as a member match** — inflates bare% wherever absence is common;
   `Isotope Dilution Spike` measured 50% bare with ZERO genuine matches

**And the dominant false positive:** per-analyte or per-phase assignment
(`LIFL (Fe, Mn); TAPL (Mg)`) reads as qualification but is a **Column I `Keyed By` matter**.
The scan was wrong on **6 of 8** thin-evidence fields for this. Calibrate any scan against
`Technique` / `Analytical Mode` / `Instrument Manufacturer`, which must land ≥85% bare.

**My own triage notes were wrong twice** (`Plasma Thermal Mode`, `Diffracting Crystal`). Read
the variants before acting on a note.
