# Superseded TAPPs — 2026-09-16

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v72` | `v75` |
| `EPMA_TAPP_v73` | `v75` |
| `EPMA_TAPP_v74` | `v75` |
| `LA-Q-ICP-MS_TAPP_v83` | `v86` |
| `LA-Q-ICP-MS_TAPP_v84` | `v86` |
| `LA-Q-ICP-MS_TAPP_v85` | `v86` |
| `LA-Q-ICP-MS_UPb_TAPP_v83` | `v86` |
| `LA-Q-ICP-MS_UPb_TAPP_v84` | `v86` |
| `LA-Q-ICP-MS_UPb_TAPP_v85` | `v86` |
| `LA-SF-ICP-MS_TAPP_v80` | `v83` |
| `LA-SF-ICP-MS_TAPP_v81` | `v83` |
| `LA-SF-ICP-MS_TAPP_v82` | `v83` |
| `LA-SF-ICP-MS_UPb_TAPP_v81` | `v84` |
| `LA-SF-ICP-MS_UPb_TAPP_v82` | `v84` |
| `LA-SF-ICP-MS_UPb_TAPP_v83` | `v84` |
| `SEM_Composition_TAPP_v68` | `v71` |
| `SEM_Composition_TAPP_v69` | `v71` |
| `SEM_Composition_TAPP_v70` | `v71` |
| `SEM_FIBSEM_TAPP_v35` | `v38` |
| `SEM_FIBSEM_TAPP_v36` | `v38` |
| `SEM_FIBSEM_TAPP_v37` | `v38` |
| `SEM_Imaging_TAPP_v34` | `v37` |
| `SEM_Imaging_TAPP_v35` | `v37` |
| `SEM_Imaging_TAPP_v36` | `v37` |
| `SEM_TAPP_v69` | `v72` |
| `SEM_TAPP_v70` | `v72` |
| `SEM_TAPP_v71` | `v72` |
| `TEM_TAPP_v55` | `v58` |
| `TEM_TAPP_v56` | `v58` |
| `TEM_TAPP_v57` | `v58` |

30 version(s), 60 file(s) (CSV + xlsx). Twelve passes: three literature fields, four corpora each.

## Why

The `Sampling Unit Type` literature pass. `Sampling Unit Name` was completed on 2026-09-15; its two
sibling fields were never assessed for four of the six corpora — 131 blank cells in EPMA, the LA
family, the SEM family and TEM. (Solution and Lab-XCT were done when those TAPPs were built.)

### Pass 1 — `Sampling Unit Type` literature, batch 1: EPMA (14 cells)

`../../Project Files/Scripts/phase3_sampling_unit_type_epma_20260916.py`. EPMA v72 → v73. The one
cell already filled (Neuman 2025) was left alone; the script refuses to overwrite a non-blank cell.

**What the type is, for EPMA: what one reported row corresponds to, not what the beam touched.**
Three shapes recur, and each cell says which it is.

- **Per-phase or per-occurrence means** (Ma 2015, Ma 2017, Pang 2016). The row is the phase or the
  grain and the points are its replicates, so the cell carries the n values.
- **Representative or per-grain analyses** (Frank 2023, Seifert 2026, Barnes 2025 both labs). The row
  is the analysis point inside a named grain.
- **Maps** (Liu 2016 UT, Broussard 2026, Zega 2025's phase mapping). Every pixel is classified and the
  reported quantity is a modal fraction over a section or fragment, so the row is that area.

**Tally:** 6 `Phase > Analysis point`, 5 `Grain > …`, 2 map-area types, 1 whole-section type.

### Pass 2 — `Sampling Unit Type` literature, batch 2: the laser-ablation family (26 cells)

`../../Project Files/Scripts/phase3_sampling_unit_type_la_20260916.py`. LA-Q v83 → v84, LA-Q U-Pb
v83 → v84, LA-SF v80 → v81, LA-SF U-Pb v81 → v82. LA-MC was already filled; so was Wu 2023 in LA-Q.

**What decides the type in LA is what the laser's motion makes of the unit.** A spot analysis reports
a spot inside something — a metal grain (Nakanishi 2022), a fused glass disc (Liu 2024), a quenched
run product (Liu 2025). A raster or map reports the area covered, and the paper says what that area
is: a whole polished specimen surface read as "raster averages" (Zhang 2022), one olivine crystal
(Chernonozhkin 2021), or a region chosen for the phases in it (Navarro 2024).

**Tally:** 7 grain-level parents, 2 phase-level, 2 whole-sample, 1 aliquot, 1 region of interest.

**Fixed by hand after the pass:** `TAPP_Composed_Variants.csv` again named the pre-pass U-Pb versions
— the third time. A patch that bumps a TAPP without composing it does not advance that register.

**One new key finding, adjudicated rather than applied.** Filling the field made
`audit_keys_vs_literature.py` score `Sampling Unit Type` UNDER-DECLARED in EPMA and LA: the detector
reads the nested notation inside one cell (`Grain > Spot`) as several units per procedure. It is one
procedure reporting at two levels. Keyed `(none)` deliberately — recorded in `ADJUDICATED` and as a
third trap in `precedents.md`: **a field that declares what the axis IS cannot be keyed by that
axis**, and under Rule 9 the units are enumerated by `Sampling Unit Name`, the containment definer.

### Passes 3–4 — `Sampling Unit Type` literature, batches 3–4: SEM (70 cells) and TEM (21 cells)

`../../Project Files/Scripts/phase3_sampling_unit_type_sem_20260916.py` and
`..._tem_20260916.py`. SEM v69 → v70, SEM_Composition v68 → v69, SEM_FIBSEM v35 → v36, SEM_Imaging
v34 → v35, TEM v55 → v56. **With these, the field is complete: 0 blank literature cells library-wide.**

**In SEM the procedure's own product decides the type,** and the five products differ: imaging
reports the imaged field, EDS point analysis a point inside a phase, mapping the mapped area read for
its phases, FIB preparation the section it cuts out of a particle, and tomography the serial-sectioned
volume. **In TEM it is almost always the electron-transparent specimen** — the FIB section is the
unit, and phases, grains or regions are reported inside it. Two papers depart from that and say so:
Keller & Berger 2014 ultramicrotomes whole particles and reports spectrum images of individual grains,
Singerling 2025 crushes a particle onto a grid and reports grains.

**Where `Sampling Unit Name` was N, the type usually is not.** Zega 2025's laboratory passages name no
specimen, which made every Name cell N — but each passage still says what KIND of unit it worked on
("Characterization of regions of interest ...", "All sections were extracted from varied regions of
matrix within the particles"). Only 7 of the 133 cells are N: three Barnes 2025 procedures the paper
does not contain, Xing 2023's review, and three older cells.

**Tally across all four batches (133 cells):** Grain 38, Whole sample 33, Phase 24, Sub-volume 18,
Region of interest 9, N 7, Aliquot 2, Analysis point 1, Laser spot 1.

**Noticed, not changed.** The Solution cells written when that TAPP was built use free-text heads
("Digestion aliquot", "Weighed powder aliquot", "Split of a single digest") rather than the Column F
vocabulary the other five corpora now use. They are accurate and evidence-backed; normalising them is
a separate decision, not a silent edit.

### Passes 5–8 — `Sampling Unit Selection Criteria` literature, all four corpora (131 cells)

`../../Project Files/Scripts/phase3_sampling_unit_selection_{epma,la,sem,tem}_20260916.py`. EPMA
v74, LA-Q v85 + U-Pb v85, LA-SF v82 + U-Pb v83, the four SEM TAPPs (v71/v70/v37/v36) and TEM v57.
The field is in-situ only — the three Solution TAPPs do not carry it — so this covers the same 131
columns as the Type pass. **All three sibling fields now read zero blanks.**

**The line this pass had to hold.** The field asks how the analysed unit is picked out. A stated rule
or reason is recorded; a bare list of the phases a table reports is not, because that is the Type's
evidence and copying it would make two fields say one thing. An act of picking by phase ("Olivine and
pyroxene grains were identified and characterized") is a rule; a table caption naming phases is not.

**Where a technique destroys its target, the paper defends the choice.** LA and TEM state a criterion
far more often than EPMA and SEM do — a laser spot and a FIB cut cannot be taken back, so method
sections justify where they were placed: spots picked off prior electron images, maps sited on a μXRF
survey, sections cut where sulfides reach the surface, regions chosen because earlier ion-probe work
damaged them least. An electron image is free and repeatable, so SEM papers mostly image what they
image and say nothing — 20 of its 35 procedures are N.

**One paper answers the question by denying it,** and that is a value, not an N: Singerling 2025
states "We did not use any specific parameters in selecting which particles to investigate (i.e., they
were selected arbitrarily)".

**Tally across the 133 cells:** 72 state a criterion, 61 are N.

**A second key finding, adjudicated rather than applied.** The audit scored this field UNDER-DECLARED
in EPMA and LA-SF, reading the criterion's own vocabulary — grains, spots, rims — as per-unit values.
Kept `(none)`: the rule is stated once and applied to every unit, and the units are the OUTPUT of
applying it, so they cannot index it. Recorded in `ADJUDICATED` and appended to the precedent the
Type pass established.

### Passes 9–12 — `Pre-Analysis Imaging and Screening` literature, all four corpora (131 cells)

`../../Project Files/Scripts/phase3_pre_analysis_imaging_{epma,la,sem,tem}_20260916.py`. EPMA v75,
LA-Q v86 + U-Pb v86, LA-SF v83 + U-Pb v84, the four SEM TAPPs (v72/v71/v38/v37), TEM v58. **The field
is complete, and with it the last of the four fields that were blank on all 131 in-situ columns.**

**The boundary that decides the N cells:** imaging the procedure performs as its own measurement is
not screening. An EPMA BSE image taken on the microprobe is part of the procedure; a BSE image taken
on a separate SEM to find the grain the probe will analyse is this field. That line is why SEM is
N-heavy again (20 of 35) while EPMA has no N at all — in an SEM paper the imaging usually IS the
procedure, whereas an EPMA paper almost always images somewhere else first.

**TEM always has a prior step, because the specimen has to be made.** Something must be imaged to
decide where to cut, and most of these papers say so: SEM imaging of the target grain, an optical
search across 25 glass beads for the one with an impact crater, CL imaging of apatite zoning before
the FIB transect is placed.

**The screening step and the selection criterion are one act described twice.** The four SEM papers
that state a criterion are exactly the four that describe a prior survey — μXRD reconnaissance,
optical-CL, VIS-IR spectral imaging, NanoSIMS isotope imaging. The two fields are not redundant (one
holds the rule, the other the instrument and settings) but they are attested by the same sentences,
which is a useful check on both.

**Tally across the 148 columns:** 83 state a screening step, 65 are N.

**A third key finding, adjudicated rather than applied.** The audit scored the field AXIS-MISMATCH in
LA-SF, proposing `monitored property + target species` over the declared `sample`, because the cells
quote what the screening maps show ("Si, Al, Cr, Fe, Mg, Ca, Na, P, and Ni maps"). Those lists say
what one map contains; they are not a value per element. Kept `sample` — screening happens once per
sample, before the procedure runs.

## Verification

**Pass 1.**
- **Cell-level diff:** exactly 14 cells changed, all in the `Sampling Unit Type` literature columns.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Composition:** `recompose_all_20260812.py --check` reports 16 MATCH, 0 DIFFERS.
- **Validator:** `validate_tapp.py` reports 0 ERROR, 0 WARN.
- **Key audit:** `audit_keys_vs_literature.py` regenerated. It raised one NEW finding on
  `Sampling Unit Type`, which pass 2 then adjudicated (see below); nothing else changed.
- **Mockups:** both EPMA mockups retargeted to v73 and rebuilt, 72 procedure-level fields unchanged.

**Pass 2.**
- **Cell-level diff:** exactly 26 cells changed across four TAPPs (6 + 6 + 7 + 7), all in the
  `Sampling Unit Type` literature columns; the U-Pb variants match their base TAPPs.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Composition:** 16 MATCH, 0 DIFFERS. **Validator:** 0 ERROR, 0 WARN after the variants register
  and the two mockup document references were advanced.
- **Key audit:** regenerated; the one new finding is adjudicated above, and no other finding changed.

**Passes 3–4.**
- **Cell-level diff:** 70 cells across the four SEM TAPPs (35 + 9 + 8 + 18) and 21 in TEM, all in the
  `Sampling Unit Type` literature columns.
- **Shared columns:** every SEM_Composition, SEM_FIBSEM and SEM_Imaging column holds the identical
  SEM cell — checked programmatically, not by eye.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Completeness:** a sweep of the Rule 12 mirror reports 0 blank `Sampling Unit Type` literature
  cells in the library.
- **Composition:** 16 MATCH, 0 DIFFERS. **Validator:** 0 ERROR, 0 WARN. **Key audit:** regenerated,
  no new finding beyond the one adjudicated in pass 2.

**Passes 5–8.**
- **Cell-level diff:** 14 + 26 + 70 + 21 = 131 cells, all in the `Sampling Unit Selection Criteria`
  literature columns; the U-Pb variants match their base TAPPs and the three SEM subsets hold the
  identical SEM cell, both checked programmatically.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Completeness:** a sweep of the Rule 12 mirror reports 0 blank cells in all three sampling-unit
  fields — Name, Type and Selection Criteria.
- **Composition:** 16 MATCH, 0 DIFFERS. **Validator:** 0 ERROR, 0 WARN. **Key audit:** regenerated,
  0 findings left unadjudicated.
- **Mockups:** both EPMA mockups retargeted to v74 and rebuilt; the point-analysis form's prefilled
  count rose 33 → 34 as Ma 2017 gained a criterion. **Variants register** advanced for the U-Pb bumps.

**Passes 9–12.**
- **Cell-level diff:** 14 + 26 + 70 + 21 = 131 cells, all in the `Pre-Analysis Imaging and Screening`
  literature columns; U-Pb variants match their bases and the three SEM subsets hold the identical
  SEM cell, both checked programmatically.
- **Rows:** no row added or removed; no field, tier, data type or `Keyed By` value changed.
- **Completeness:** 0 blank cells in this field, and none in any of the four fields that were blank
  on all 131 in-situ columns as of this morning.
- **Composition:** 16 MATCH, 0 DIFFERS. **Validator:** 0 ERROR, 0 WARN. **Key audit:** regenerated,
  0 findings left unadjudicated.
- **Mockups:** EPMA retargeted to v75 and rebuilt; the point-analysis form's prefilled count rose
  34 → 35. **Variants register** advanced for the U-Pb bumps.
