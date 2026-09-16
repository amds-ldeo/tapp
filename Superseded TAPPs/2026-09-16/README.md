# Superseded TAPPs — 2026-09-16

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v72` | `v73` |
| `LA-Q-ICP-MS_TAPP_v83` | `v84` |
| `LA-Q-ICP-MS_UPb_TAPP_v83` | `v84` |
| `LA-SF-ICP-MS_TAPP_v80` | `v81` |
| `LA-SF-ICP-MS_UPb_TAPP_v81` | `v82` |
| `SEM_Composition_TAPP_v68` | `v69` |
| `SEM_FIBSEM_TAPP_v35` | `v36` |
| `SEM_Imaging_TAPP_v34` | `v35` |
| `SEM_TAPP_v69` | `v70` |
| `TEM_TAPP_v55` | `v56` |

10 version(s), 20 file(s) (CSV + xlsx). Four passes, one per corpus.

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
