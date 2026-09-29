# Documenting an EPMA procedure completely: a worked example

*Built against EPMA TAPP v86, which has 95 fields. Composite and illustrative. The v77 edition, which exposed the six gaps recorded in Appendix B, is kept as `EPMA_Reference_Procedure_Example_v77.md`.*

> **What this is.** This is a worked example of a procedure description and a session report. Together they fill every field of the EPMA TAPP, as a model of what complete documentation looks like in a publication.
>
> **Where the content comes from.** The analytical design and typical values are adapted from the 15 procedures assessed for the TAPP. The main sources are Zega et al. (2025), Barnes et al. (2025), Seifert et al. (2026), McCoy et al. (2025) and Neuman et al. (2025). Where no assessed procedure reports a field, the example adds content; Appendix A counts, for each field, how many of the 15 state it. Appendix A lists every field, where it appears here, and how many assessed procedures report it.
>
> **What is fictional.** The laboratory, people, samples, identifiers, DOIs, grants, dates and every measured result are fictional. Instrument models, software, reference materials and the methods literature cited are real. Do not cite the numbers here as data.

**How repeating information is written.** Anything reported once is prose. Anything that repeats is a table, and the italic line under each table title says what one row is. It names the list the rows repeat over: *Reported per Monitored Element*.

- **Nested lists.** When one list nests inside another, the chain is written from the inside out. *Per Sampling Unit Name per Sample Name* means one row for each analysis point, within each sample.
- **Crossed lists.** When two lists cross, they are joined with ×. *Per Secondary Reference Material × Reported Variable* is a grid: one cell for each reported variable, within each reference material.
- **The eight lists** that everything else repeats over are set up in these places:

| List | Set up in |
|---|---|
| Target Material | §1.3 |
| Target Species | Table 2 |
| Monitored Elements | Table 3 |
| Reported Variables and Units | Table 4 |
| Secondary Reference Materials | Table 7 |
| Sample Name | Table 9 |
| Sampling Unit Name | Table 10 |
| Combined Results | Table 14 |

- **Lists that exist only in a session.** Samples, analysis points and combined results exist only once a session has run. Where a procedure item repeats over one of them, the procedure states it once, as a rule or typical value, and the session gives it per sample, point or combined result.

**Two records.** Part 1 is the registered procedure, written once and cited by DOI. Part 2 is the record of one analytical session run under it.

- A paper that cites a registered procedure needs Part 2, plus one sentence citing the procedure.
- A paper without a registered procedure needs both parts.

---

## Part 1 — The procedure

### 1.1 Identification

**Name and scope.** The procedure is *EML-EPMA-CC v2: EPMA-WDS+EDS major and minor elements in carbonaceous-chondrite silicates, oxides, sulfides, phosphates and carbonates, by point analysis and X-ray mapping (JEOL JXA-8530F Plus)*. The technique is EPMA-WDS+EDS.

**Authorship and laboratory.** The procedure was developed by, and is maintained by, the Example Microanalysis Laboratory, which hosts the instrument (ROR https://ror.org/0example00). It has been in production use since 2025-01-15.

**Funding.** The instrument was funded by Example Agency award EX-INST-0001. Development of the procedure was funded by award EX-DEV-0002.

**Validation.** The procedure is described and validated in Example et al. (2025), doi:10.0000/example.2025.001.

### 1.2 Coupled techniques

**Coupled techniques.** Samples analysed under this procedure are also analysed by two other techniques:

- **FE-SEM** (BSE imaging and EDS mapping), in the Example Microanalysis Laboratory.
- **NanoSIMS** oxygen-isotope analysis of carbonates, in the Example Isotope Laboratory.

**How they connect.** The SEM images locate the phases analysed here. The EPMA composition of each carbonate is used to choose the matrix-matched carbonate reference material for the NanoSIMS instrumental mass-fractionation correction.

**Order of work.**

1. SEM imaging comes first.
2. EPMA follows, because it is non-destructive.
3. The carbon coat is then replaced with gold.
4. NanoSIMS comes last, because sputtering destroys the analysed volume.

### 1.3 Materials, preparation and what counts as one analysis

**Target materials.** The procedure is designed for five material types in carbonaceous chondrites and returned asteroid samples. The list sets the scope, and it is also the list that beam conditions (Table 1) and primary standards (Table 2b) are stated against:

- Silicate mineral (olivine, pyroxene)
- Oxide (magnetite, chromite, ilmenite)
- Sulfide (pyrrhotite, pentlandite)
- Phosphate (apatite, merrillite)
- Carbonate (calcite, dolomite, breunnerite)

**Preparation.** Particles or fragments are embedded in epoxy and dry-polished with diamond, finishing at 0.25 µm. They are then carbon coated to 20 nm, together with the standards. This is the registered preparation; a session reports the preparation of each sample and may vary it (Table 9).

**What one row of results is.** One row of reported results corresponds to one analysis point within a particle. For X-ray mapping it corresponds to one map area; the individual pixels are not reported as separate units.

**How analysis points are chosen.**

- Points are placed at least 3 µm from grain boundaries, cracks and inclusions visible in BSE. For defocused or rastered beams the distance is 5 µm.
- For focused points, grains must be at least 5 µm across. For phosphates and carbonates they must be at least 10 µm across.
- The identity of each phase is confirmed by an EDS spectrum before WDS acquisition begins.
- Map areas are chosen to include every target phase present in a particle.

**Imaging before analysis.** Before EPMA, each sample is imaged by BSE and mapped by EDS on a field-emission SEM at 15 kV and 1 nA, to find the phases to be analysed. The BSE images are registered to stage coordinates, and each analysis point is marked on its BSE image with its point label.

### 1.4 Instrument and software

**Instrument.** Analyses are made on a JEOL JXA-8530F Plus with a Schottky field-emission electron source.

**WDS spectrometers.** The instrument has five JEOL WDS spectrometers, with these crystals:

| Spectrometer | Crystals |
|---|---|
| Sp1 | LDE1, TAP |
| Sp2 | TAP, PETJ |
| Sp3 | PETJ, LIF |
| Sp4 | PETH, LIFH |
| Sp5 | LIF, PETL |

**EDS detector.** The EDS detector is the manufacturer's integrated silicon drift detector: 30 mm² active area, ultra-thin polymer window, 40° take-off angle.

**Acquisition software.** Probe for EPMA v13 (Probe Software) runs both point analyses and maps.

**Data processing software.**

- Probe for EPMA v13 quantifies the point analyses.
- CalcImage v13 produces the quantitative maps.
- XMapTools 4 classifies phases in the maps.

### 1.5 Analytical modes and operating conditions

**Modes.** The procedure covers all four analytical modes: EDS point analysis, EDS mapping, WDS point analysis and WDS mapping.

**Accelerating voltage.** The accelerating voltage is 15 kV. This is the laboratory's standard operating voltage, so no justification is needed.

**Beam conditions for point analysis.** Beam conditions are set per target material (Table 1). Each session records which target material every analysis point belongs to (Table 10), and so which row applies. The beam mode, diameter and raster dimensions in each row agree with one another.

**Table 1. Beam conditions for point analysis.** *Reported per Target Material. Point analysis only; maps have their own conditions, below.*

| Target material | Beam mode | Current (nA) | Diameter (µm) | Raster (µm) | Beam-damage measures |
|---|---|---|---|---|---|
| Silicate mineral | Focused | 20 | 1 | — | None required |
| Oxide | Focused | 20 | 1 | — | None required |
| Sulfide | Focused | 20 | 1 | — | None required |
| Phosphate | Defocused | 8 | 5 | — | F, Cl and Na measured in the first acquisition pass; time-dependent intensity correction for F and Na |
| Carbonate | Rastered | 4 | focused within the raster | 5 × 5 | Na measured in the first acquisition pass; beam rastered to spread the dose |

**Beam conditions for mapping.** An X-ray map scans every material at one set of conditions, so mapping has its own: a focused beam, 50 nA, 1 µm diameter. The beam mode is fixed; a session may adjust the current and diameter, and records them for each map (§2.3).

**Drift correction.** The beam current is measured with the Faraday cup before every point analysis and at the start of every map line, and intensities are normalised to the measured current. Primary standards are re-measured at the start and end of each session, and the drift in standard intensities is interpolated linearly with time.

### 1.6 What is determined, what is measured, and what is reported

The procedure uses three separate lists.

#### Target species

**What is determined.** The procedure determines 18 elements: Si, Ti, Al, Cr, Fe, Mn, Mg, Ca, Na, K, P, S, F, Cl, Ni, Co, O and C. Isotopes are not separate entries.

**Table 2. Target species: how each concentration is obtained.** *Reported per Target Species.*

| Target species | Concentration obtained |
|---|---|
| Si, Ti, Al, Cr, Fe, Mn, Mg, Ca, Na, K, P, S, F, Cl, Ni, Co | Directly, from measured intensity |
| O | By stoichiometry from cation valences; in apatite, OH is calculated by difference assuming F + Cl + OH = 1 apfu (Ketcham 2015) |
| C | By stoichiometry, as CO₂ from cations, in carbonates only |

O and C are not measured, so they have no monitored element (Table 3).

**Table 2b. Primary calibration standards.** *Reported per Target Material × Target Species. One set of standards serves every target material, except that Ca and Mg in carbonates are calibrated on dolomite.*

| Target species | Primary calibration standard, all target materials | Carbonate | Source; accepted values |
|---|---|---|---|
| Si | Springwater olivine, USNM 2566 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| Ti | Ilmenite, USNM 96189 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| Al | Anorthite, USNM 137041 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| Cr | Synthetic Cr₂O₃ | as for all | Laboratory standard; stoichiometric |
| Fe | Rockport fayalite, USNM 85276 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| Mn | Rhodonite | as for all | Laboratory standard; supplier certificate |
| Mg | Springwater olivine, USNM 2566 | Dolomite, USNM 10057 | Smithsonian NMNH; Jarosewich et al. (1980) |
| Ca | Diopside, USNM 117733 | Dolomite, USNM 10057 | Smithsonian NMNH; Jarosewich et al. (1980) |
| Na | Amelia albite | as for all | Laboratory standard; supplier certificate |
| K | Microcline, USNM 143966 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| P | Wilberforce fluorapatite | as for all | Laboratory standard; supplier certificate |
| S | Synthetic FeS (troilite) | as for all | Laboratory standard; stoichiometric |
| F | Synthetic SrF₂ | as for all | Laboratory standard; stoichiometric |
| Cl | Scapolite, USNM R6600-1 | as for all | Smithsonian NMNH; Jarosewich et al. (1980) |
| Ni | Ni metal, 99.99% | as for all | Laboratory standard; stoichiometric |
| Co | Co metal, 99.99% | as for all | Laboratory standard; stoichiometric |

#### Monitored elements

**What is measured.** The procedure monitors 17 elements. Each serves one target species, except Zn. Zn is monitored only to correct its Lα overlap on Na Kα and serves no target species. O and C have no monitored element. The detection method, WDS or EDS, is stated for each monitored element (Table 3), because in combined point analysis it is chosen element by element; it decides which of the WDS-only columns apply.

- **Measured by WDS:** F, Na, K, Cl, Zn, Al, P, Ti, Cr, Mn, Co and Ni.
- **Measured by EDS:** Si, Mg, Fe, Ca and S.

Nothing in the target-species list is inferred from this list, or the other way round.

**Table 3. Monitored elements: detection.** *Reported per Monitored Element, grouped by the Target Species each serves. The last four columns apply to WDS only.*

| Monitored element (serves) | X-ray line | Detection method | Spectrometer (crystal) | Acquisition pass | Detector | PHA mode |
|---|---|---|---|---|---|---|
| F (F) | Kα | WDS | Sp1 (LDE1) | 1 | Low-pressure P10 flow | Differential |
| Na (Na) | Kα | WDS | Sp2 (TAP) | 1 | Low-pressure P10 flow | Differential |
| K (K) | Kα | WDS | Sp3 (PETJ) | 1 | Xe sealed | Integral |
| Cl (Cl) | Kα | WDS | Sp4 (PETH) | 1 | Xe sealed | Integral |
| Zn (none; interference monitor for Na) | Kα | WDS | Sp5 (LIF) | 1 | Xe sealed | Integral |
| Al (Al) | Kα | WDS | Sp1 (TAP) | 2 | Low-pressure P10 flow | Integral |
| P (P) | Kα | WDS | Sp2 (PETJ) | 2 | Low-pressure P10 flow | Integral |
| Ti (Ti) | Kα | WDS | Sp3 (PETJ) | 2 | Xe sealed | Integral |
| Cr (Cr) | Kα | WDS | Sp4 (LIFH) | 2 | Xe sealed | Integral |
| Mn (Mn) | Kα | WDS | Sp5 (LIF) | 2 | Xe sealed | Integral |
| Co (Co) | Kα | WDS | Sp3 (LIF) | 3 | Xe sealed | Integral |
| Ni (Ni) | Kα | WDS | Sp4 (LIFH) + Sp5 (LIF), intensities aggregated | 3 | Xe sealed | Integral |
| Si (Si) | Kα | EDS | — | — | — | — |
| Mg (Mg) | Kα | EDS | — | — | — | — |
| Fe (Fe) | Kα | EDS | — | — | — | — |
| Ca (Ca) | Kα | EDS | — | — | — | — |
| S (S) | Kα | EDS | — | — | — | — |

**Acquisition passes (WDS point analysis).** In WDS point analysis the 12 WDS elements are acquired in three passes. In each pass, all the assigned spectrometers count at the same time. The volatile elements (F, Na, K and Cl) are in the first pass, so they are measured before beam damage builds up. The EDS spectrum is acquired during pass 1.

**Table 3b. Monitored elements: counting and background.** *Reported per Monitored Element. Counting times and background positions apply to WDS point analysis only. Dwell time applies to X-ray mapping only.*

| Monitored element | Peak time (s) | Background time, total (s) | Background positions (mm from peak) | Background correction: points / maps | Map dwell time (ms) |
|---|---|---|---|---|---|
| F | 20 | 20 | −3.2 / +4.5 | Two-point off-peak, exponential / MAN | — |
| Na | 10 | 10 | −4.0 / +4.0 | Two-point off-peak, linear / MAN | 30 |
| K | 10 | 10 | −4.5 / +4.5 | Two-point off-peak, linear / MAN | — |
| Cl | 20 | 20 | −3.0 / +3.0 | Two-point off-peak, linear / MAN | — |
| Zn | 10 | 10 | −3.5 / +3.5 | Two-point off-peak, linear / MAN | — |
| Al | 20 | 20 | −3.5 / +3.5 | Two-point off-peak, linear / MAN | 30 |
| P | 20 | 20 | −4.0 / +4.0 | Two-point off-peak, linear / MAN | 30 |
| Ti | 30 | 30 | −5.0 / +5.0 | Two-point off-peak, linear / MAN | — |
| Cr | 30 | 30 | −3.0 / +3.0 | Two-point off-peak, linear / MAN | 30 |
| Mn | 30 | 30 | −3.5 / +3.5 | Two-point off-peak, linear / MAN | — |
| Co | 40 | 40 | −2.5 / +3.5 | Two-point off-peak, linear / MAN | — |
| Ni | 40 | 40 | −3.0 / +3.0 | Two-point off-peak, linear / MAN | 30 |
| Si, Mg, Fe, Ca, S | — (EDS live time; see §1.7) | — | — | Spectral background, removed by the filter fit / same | 30 (EDS live time per pixel, shared) |

MAN background correction follows Donovan and Tingle (1996).

#### Reported variables

**Table 4. Reported variables and units.** *List of entries.*

| Reported variable | Unit |
|---|---|
| SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe as FeO), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO, CoO | wt% |
| S, F, Cl | wt% (as element) |
| Oxygen equivalent of F and Cl | wt% |
| CO₂, by stoichiometry (carbonates only) | wt% |
| Analytical total | wt% |
| Structural formula | atoms per formula unit (apfu) |
| Element concentration maps: Si, Mg, Fe, Ca, S, Al, Na, P, Cr, Ni | wt% per pixel |
| Phase map and modal abundance | Phase map: nominal property, no unit. Modal abundance: area % |

### 1.7 EDS acquisition

**Acquisition modes.** EDS spectra are acquired in two ways: as point spectra, and as spectrum images that keep a full spectrum at every pixel. Line scans are not used.

**Live time.** The live time is 30 s per analysis point.

### 1.8 X-ray mapping

**How maps are acquired.** Maps are acquired by stage scan with the beam held fixed, at a step size of 2 µm in both X and Y.

**What is mapped.** WDS maps of Na (Sp2, TAP), Al (Sp1, TAP), P (Sp3, PETJ), Cr (Sp4, LIFH) and Ni (Sp5, LIF) are collected in a single pass. P and Ni are assigned to different spectrometers than in point analysis (Table 3), so that all five fit in one pass. An EDS spectrum image is collected at the same time, and gives the Si, Mg, Fe, Ca and S maps. The dwell time is 30 ms per pixel (Table 3b).

**Map size.** Each session records the dimensions and extent of each map.

### 1.9 Data reduction

**Matrix correction.** Intensities are converted to concentrations with the Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995) in Probe for EPMA. The same correction is applied pixel by pixel in CalcImage. Mass absorption coefficients are taken from FFAST (Chantler et al. 2005).

**Dead time.**

- **WDS:** corrected with the logarithmic dead-time expression, using spectrometer-specific constants of 1.1–1.5 µs determined by the laboratory. No measured WDS dead time is reported.
- **EDS:** net peak intensities are extracted by filter fit, a top-hat filter followed by least-squares fitting to measured standard spectra.

**Halogen correction.** Oxygen is corrected for halogen substitution. In apatite, the oxygen equivalent of F and Cl is subtracted from the total, and OH is calculated by difference (Ketcham 2015).

**Background correction.** Background correction for each monitored element is given in Table 3b.

**Table 5. Corrections.** *Reported per Target Species. Target species that are not listed receive none of these corrections.*

| Target species | Time-dependent intensity correction | Blank correction | X-ray line overlap correction | Interfering element | Interference-correction standard |
|---|---|---|---|---|---|
| F | Exponential (apatite) | None | No | — | — |
| Na | Linear | None | Yes: Zn Lα on Na Kα; quantitative interference correction, iterated with the matrix correction | Zn | Synthetic ZnS (Na-free) |
| Mn | None | None | Yes: Cr Kβ on Mn Kα; as above | Cr | Synthetic Cr₂O₃ (Mn-free) |
| Co | None | Zero-concentration blank measured on synthetic forsterite, and the apparent concentration subtracted | Yes: Fe Kβ on Co Kα; as above | Fe | Rockport fayalite, USNM 85276 (Co-free) |
| Ni | None | Zero-concentration blank measured on synthetic forsterite, and the apparent concentration subtracted | No | — | — |

**Table 6. Normalisation, detection limits and counting uncertainty.** *Reported per Reported Variable.*

| Reported variable | Normalisation | Detection-limit method | Typical detection limit, 3σ | Typical counting-statistics uncertainty, 1σ |
|---|---|---|---|---|
| SiO₂, MgO, FeO, CaO (EDS) | None | 3σ of background counts | 0.08–0.15 wt% | ≤1% relative above 10 wt% |
| S (EDS) | None | 3σ of background counts | 0.08 wt% | 2% relative at 35 wt% |
| TiO₂, Al₂O₃, Cr₂O₃, MnO, Na₂O, K₂O, P₂O₅ (WDS) | None | 3σ of background counts | 0.01–0.02 wt% | 1–3% relative at 1 wt% |
| NiO, CoO (WDS) | None | 3σ of background counts | 0.010–0.012 wt% | 15–30% relative at 0.05 wt% |
| F, Cl (WDS) | None | 3σ of background counts | F 0.06 wt%; Cl 0.01 wt% | F 3%, Cl 3% relative in apatite |
| Oxygen equivalent of F and Cl; CO₂; analytical total | None | Not applicable (calculated) | — | Propagated from the contributing variables |
| Structural formula | Normalised to a fixed anion basis by phase: 4 O (olivine), 6 O (pyroxene), 4 O (spinels), 13 anions (apatite; Ketcham 2015), 6 O (dolomite), 3 O (calcite) | Not applicable | — | Propagated |
| Element concentration maps | None | 3σ of background counts, per pixel | 0.2–0.5 wt% (WDS); 0.5–1 wt% (EDS) | 5–10% relative at 10 wt%, per pixel |
| Phase map and modal abundance | None | Not applicable | — | — |

**Calibration factor** *(reported per Reported Variable)*. None, for every reported variable in Table 4. No conversion uses an externally calibrated factor: every concentration comes from k-ratios measured against the primary standards in Table 2b.

**How results are combined** *(reported per Reported Variable)*.

- **Oxide and element concentrations, CO₂, oxygen equivalent and analytical total:** arithmetic mean of the included point analyses, per phase within a sample. Each mean is one combined result (Table 14).
- **Structural formula:** calculated from each mean, not averaged.
- **Element concentration maps, phase map and modal abundance:** not combined; each map is reported on its own.

**Which results enter a mean.** The procedure states these rules once; each session reports their outcome for each combined result (Table 14). A point analysis contributes to its phase mean only if it meets all of these conditions:

- The analytical total falls between 98.5 and 101.5 wt% for silicates, oxides and sulfides. For apatite (OH by difference) the window is 96.0–101.5 wt%. For carbonates (CO₂ by stoichiometry) it is 98.0–102.0 wt%.
- The cation sum is within ±0.03 apfu of the ideal value.
- The point does not overlap a second phase in the post-analysis BSE image.
- The beam current drifted by less than 1% during the analysis.

For each combined result, each session reports how many results were obtained, how many were included, and the reason for each exclusion.

**Reference values.** Oxide conversions and structural formulas use the IUPAC 2021 standard atomic weights (Prohaska et al. 2022). No other constants enter data reduction.

### 1.10 Quality control

**Secondary reference materials.** These materials are measured as unknowns at least three times at the start, middle and end of each session.

**Table 7. Secondary reference materials.** *List of entries.*

| Secondary reference material | Source | Accepted values |
|---|---|---|
| San Carlos olivine, USNM 111312/444 | Smithsonian NMNH | Jarosewich et al. (1980) |
| Kakanui augite, USNM 122142 | Smithsonian NMNH | Jarosewich et al. (1980) |
| Durango apatite, USNM 104021 | Smithsonian NMNH | Jarosewich et al. (1980) |
| Chromite, USNM 117075 | Smithsonian NMNH | Jarosewich et al. (1980) |
| Calcite, USNM 136321 | Smithsonian NMNH | Jarosewich et al. (1980) |

**Table 8. Typical precision and accuracy.** *Reported per Secondary Reference Material × Reported Variable. Each cell gives precision as 1σ RSD (%) / accuracy as % relative bias. "—" means that variable is not assessed on that material.*

| Reported variable | San Carlos olivine | Kakanui augite | Durango apatite | Chromite 117075 | Calcite 136321 |
|---|---|---|---|---|---|
| SiO₂ | 0.6 / +0.4 | 0.6 / −0.5 | — | — | — |
| TiO₂ | — | 3 / +2 | — | — | — |
| Al₂O₃ | — | 1.0 / +1.1 | — | 1.0 / −0.9 | — |
| Cr₂O₃ | — | — | — | 0.6 / +0.5 | — |
| FeO | 1.2 / −0.8 | 1.5 / +0.9 | — | 1.0 / +0.7 | — |
| MgO | 0.5 / +0.3 | 0.7 / −0.6 | — | 1.2 / +1.4 | — |
| CaO | — | 0.6 / +0.4 | 0.5 / −0.3 | — | 0.5 / +0.3 |
| Na₂O | — | 2.5 / −1.8 | — | — | — |
| P₂O₅ | — | — | 0.8 / +0.6 | — | — |
| NiO | 6 / +3 | — | — | — | — |
| F | — | — | 3 / +2.5 | — | — |
| Cl | — | — | 4 / −3 | — | — |

---

## Part 2 — The analytical session

### 2.1 Session identification

**Procedure and session.** This session followed procedure doi:10.0000/example.epma-cc.v2. Its identifier in Probe for EPMA is EML-2026-0412-A.

**Who, where and when.** It was run by Analyst A (ORCID 0000-0000-0000-0000) at the Example Microanalysis Laboratory, as registered, from 2026-04-12 to 2026-04-14.

**Funding.** The analyses were funded by Example Agency award EX-SCI-0003.

**Coupling.** The coupled techniques and the coupling are as registered. The coupled NanoSIMS procedure DOI is pending. The coupled NanoSIMS dataset is included in this submission ("same submission").

### 2.2 Samples and analysis points

**Table 9. Samples.** *List of entries; the other columns are reported per Sample Name.*

| Sample Name | Persistent identifier | Preparation | Imaging and screening before analysis |
|---|---|---|---|
| EX-CC-01 (epoxy mount, 3 particles) | IGSN:EXAMPLE0001 | As registered | FE-SEM BSE mosaic and EDS maps (Mg, Si, Fe, Ca, S, P) of all three particles; points marked on EX-CC-01_P1–P3 BSE images |
| EX-CC-02 (epoxy mount, 2 particles) | IGSN:EXAMPLE0002 | As registered, plus Ar-ion polishing after the final diamond step | FE-SEM BSE mosaic and EDS maps (Mg, Si, Fe, Ca, S, P) of both particles; points marked on EX-CC-02_P1–P2 BSE images |

**Table 10. Analysis points.** *Sampling Unit Name: list of entries per Sample Name. Target material: reported per Sampling Unit Name per Sample Name, for point analysis; it names the row of Table 1 whose beam conditions the point was run under. Consecutive points are written as a label range.*

| Sample Name | Sampling Unit Name | Phase | Target material |
|---|---|---|---|
| EX-CC-01 | P1-01 – P1-08 | Olivine | Silicate mineral |
| EX-CC-01 | P1-09 – P1-12 | Pyroxene | Silicate mineral |
| EX-CC-01 | P2-01 – P2-06 | Magnetite | Oxide |
| EX-CC-01 | P2-07 – P2-11 | Pyrrhotite | Sulfide |
| EX-CC-01 | P3-01 – P3-06 | Apatite | Phosphate |
| EX-CC-01 | M1 (map area) | All phases | — (map; conditions in §2.3) |
| EX-CC-02 | P1-01 – P1-10 | Dolomite | Carbonate |
| EX-CC-02 | P1-11 – P1-16 | Calcite | Carbonate |
| EX-CC-02 | P2-01 – P2-08 | Olivine | Silicate mineral |
| EX-CC-02 | M2 (map area) | All phases | — (map; conditions in §2.3) |

### 2.3 Conditions as run

**Fixed values.** Every value the procedure fixes was used as registered.

**Adjustable values.** Every value the procedure allows a session to adjust was also used as registered, with one exception: Co and Ni. Their peak counting times were raised from 40 s to 60 s, and their total background times from 40 s to 60 s, to lower detection limits in olivine. This stays within the procedure's bounds. The values used as registered include:

- accelerating voltage, beam conditions by target material (Table 1), and drift correction
- software versions (Probe for EPMA v13, CalcImage v13, XMapTools 4)
- the target-species suite
- the reference materials
- the step size and dwell time
- the corrections and reference values

**Maps.** *Reported per Sampling Unit Name per Sample Name, for each map.*

| Map | Beam mode | Current (nA) | Diameter (µm) | Dimensions (pixels) | Area |
|---|---|---|---|---|---|
| M1 | Focused | 50 | 1 | 512 × 512 | 1.024 × 1.024 mm |
| M2 | Focused | 50 | 1 | 384 × 256 | 0.768 × 0.512 mm |

### 2.4 Results of quality control and data reduction

**Blank levels.** The blank levels measured in this session are reported per Target Species, for the target species that are blank-corrected:

- Ni: apparent concentration 35 ± 9 µg/g on synthetic forsterite (n = 5).
- Co: apparent concentration 22 ± 8 µg/g on synthetic forsterite (n = 5).

Neither reported quantity is a ratio, so no blank composition applies.

**Combined results and inclusion.** The session reports eight combined results, one mean per phase per sample (Table 14). Of 53 point analyses acquired, 45 were included; maps M1 and M2 are not combined.

**Table 14. Combined results and the outcome of the inclusion rules.** *Combined Results: list of entries. The other columns are reported per Combined Result.*

| Combined result | Points | Obtained | Included | Excluded, and why |
|---|---|---|---|---|
| Olivine, EX-CC-01 | P1-01 – P1-08 | 8 | 8 | — |
| Pyroxene, EX-CC-01 | P1-09 – P1-12 | 4 | 4 | — |
| Magnetite, EX-CC-01 | P2-01 – P2-06 | 6 | 6 | — |
| Pyrrhotite, EX-CC-01 | P2-07 – P2-11 | 5 | 3 | P2-07, P2-09: overlap with pentlandite |
| Apatite, EX-CC-01 | P3-01 – P3-06 | 6 | 4 | P3-02, P3-05: total outside the window |
| Dolomite, EX-CC-02 | P1-01 – P1-10 | 10 | 8 | P1-03, P1-07: total outside the window |
| Calcite, EX-CC-02 | P1-11 – P1-16 | 6 | 5 | P1-16: overlap at a grain boundary |
| Olivine, EX-CC-02 | P2-01 – P2-08 | 8 | 7 | P2-05: beam-current drift above 1% |

**EDS dead time.** EDS dead time was 18–26% for point analyses and 24–31% during spectrum imaging.

**Table 11. Detection limits in this session.** *Reported per Reported Variable. Values are the medians over the included analyses of each phase, 3σ, and are measured in this session, not typical.*

| Reported variable | Detection limit (wt%) |
|---|---|
| SiO₂ / MgO / FeO / CaO (EDS) | 0.11 / 0.09 / 0.14 / 0.10 |
| S (EDS) | 0.08 |
| TiO₂ / Al₂O₃ / Cr₂O₃ / MnO | 0.015 / 0.012 / 0.018 / 0.016 |
| Na₂O / K₂O / P₂O₅ | 0.018 / 0.009 / 0.020 |
| NiO / CoO (60 s peak) | 0.008 / 0.010 |
| F / Cl | 0.055 / 0.010 |
| Element concentration maps | 0.3 (WDS elements); 0.7 (EDS elements), per pixel |

**Table 12. Precision and accuracy in this session.** *Reported per Secondary Reference Material × Reported Variable. Each cell gives precision as 1σ RSD (%) / accuracy as % relative bias.*

The number of analyses (n) of each material was:

| Material | n |
|---|---|
| San Carlos olivine | 9 |
| Kakanui augite | 6 |
| Durango apatite | 6 |
| Chromite | 5 |
| Calcite | 6 |

| Reported variable | San Carlos olivine | Kakanui augite | Durango apatite | Chromite 117075 | Calcite 136321 |
|---|---|---|---|---|---|
| SiO₂ | 0.5 / +0.3 | 0.7 / −0.6 | — | — | — |
| TiO₂ | — | 2.8 / +1.6 | — | — | — |
| Al₂O₃ | — | 1.1 / +0.9 | — | 0.9 / −1.2 | — |
| Cr₂O₃ | — | — | — | 0.7 / +0.4 | — |
| FeO | 1.0 / −0.6 | 1.6 / +1.2 | — | 1.1 / +0.5 | — |
| MgO | 0.4 / +0.2 | 0.6 / −0.4 | — | 1.3 / +1.1 | — |
| CaO | — | 0.5 / +0.2 | 0.6 / −0.5 | — | 0.4 / +0.6 |
| Na₂O | — | 2.2 / −2.4 | — | — | — |
| P₂O₅ | — | — | 0.7 / +0.8 | — | — |
| NiO | 4 / +2 | — | — | — | — |
| F | — | — | 3.4 / +2.1 | — | — |
| Cl | — | — | 3.8 / −2.6 | — | — |

**Table 13. Counting-statistics uncertainty (excerpt).** *Reported per Sampling Unit Name × Reported Variable per Sample Name. There is one row for each combination; the full table is in Supplementary Table S3. Uncertainties are 1σ, predicted from the counts on the peak and on any background or blank subtracted.*

| Sample Name | Sampling Unit Name | Reported variable | Value (wt%) | 1σ (wt%) |
|---|---|---|---|---|
| EX-CC-01 | P1-03 | SiO₂ | 41.92 | 0.21 |
| EX-CC-01 | P1-03 | FeO | 1.84 | 0.05 |
| EX-CC-01 | P1-03 | MgO | 55.61 | 0.28 |
| EX-CC-01 | P1-03 | NiO | 0.031 | 0.003 |
| EX-CC-01 | P1-03 | Cr₂O₃ | 0.28 | 0.01 |
| EX-CC-01 | P3-04 | P₂O₅ | 41.30 | 0.21 |
| EX-CC-01 | P3-04 | F | 3.21 | 0.09 |
| EX-CC-01 | P3-04 | Cl | 0.62 | 0.02 |
| EX-CC-02 | P1-04 | CaO | 30.10 | 0.15 |
| EX-CC-02 | P1-04 | MgO | 19.80 | 0.12 |
| EX-CC-02 | P1-04 | FeO | 2.40 | 0.06 |
| EX-CC-02 | P1-04 | MnO | 0.61 | 0.02 |

**Table 15. Dispersion and other statistics of the combined results (excerpt: olivine, EX-CC-01, n = 8).** *Reported per Combined Result × Reported Variable. The dispersion statistic is the MSWD (reduced χ²) of the included analyses about their mean, using their counting-statistics uncertainties; the acceptance threshold belongs with the inclusion rules in §1.9. The other statistic reported is the standard error of the mean (1 s.d./√n). Supplementary Table S3 gives every combined result.*

| Reported variable | Mean (wt%) | MSWD | Standard error of the mean (wt%) |
|---|---|---|---|
| SiO₂ | 41.90 | 1.2 | 0.08 |
| FeO | 1.86 | 4.6 | 0.04 |
| MgO | 55.58 | 1.9 | 0.12 |
| NiO | 0.030 | 0.9 | 0.001 |
| MnO | 0.14 | 1.1 | 0.004 |
| CaO | 0.21 | 2.3 | 0.006 |
| Cr₂O₃ | 0.28 | 1.4 | 0.005 |

The FeO scatter exceeds counting statistics. This is consistent with Fe–Mg zoning, which is visible in map M1.

### 2.5 Additional notes

Particle P2 of EX-CC-02 was partly plucked during Ar-ion polishing. Points P2-05 to P2-08 lie on the fragment that remained. No other deviations, anomalies or instrument modifications occurred.

---

## References

Armstrong, J.T. (1995) CITZAF: a package of correction programs for the quantitative electron microbeam X-ray analysis of thick polished materials, thin films, and particles. *Microbeam Analysis* 4, 177–200.

Chantler, C.T., et al. (2005) X-ray form factor, attenuation and scattering tables (FFAST), version 2.1. National Institute of Standards and Technology.

Donovan, J.J. and Tingle, T.N. (1996) An improved mean atomic number background correction for quantitative microanalysis. *Microscopy and Microanalysis* 2, 1–7.

Jarosewich, E., Nelen, J.A. and Norberg, J.A. (1980) Reference samples for electron microprobe analysis. *Geostandards Newsletter* 4, 43–47.

Ketcham, R.A. (2015) Technical note: Calculation of stoichiometry from EMP data for apatite and other phases with mixing on monovalent anion sites. *American Mineralogist* 100, 1620–1623.

Prohaska, T., et al. (2022) Standard atomic weights of the elements 2021 (IUPAC Technical Report). *Pure and Applied Chemistry* 94, 573–600.

*Fictional, for the example only:* Example et al. (2025), doi:10.0000/example.2025.001.
---

## Appendix A — Field coverage

*Generated from EPMA_TAPP_v86.csv by `make_reference_example_appendix.py`. It covers every field in the TAPP, in TAPP order. "Reported per" uses the same wording as the reviewer workbook. "Stated in" counts how many of the 15 assessed procedures report the field. 0 means this example had to add the content.*

| # | TAPP field | Procedure tier | Procedure: reported per | Session tier | Session: reported per | Where in this document | Stated in |
|---|---|---|---|---|---|---|---|
| 1.1 | Procedure Name | Basic | One value per procedure | Read-Only | One value per session | §1.1 | 15 / 15 |
| 1.2 | Technique | Basic | One value per procedure | Read-Only | One value per session | §1.1 | 6 / 15 |
| 1.3 | Procedure Author | Basic | One value per procedure | Read-Only | One value per session | §1.1 | 7 / 15 |
| 1.4 | Laboratory | Basic | One value per procedure | Editable | One value per session | §1.1; §2.1 | 15 / 15 |
| 1.5 | Laboratory ID | Advanced | One value per procedure | Editable | One value per session | §1.1 | 0 / 15 |
| 1.6 | Procedure Start Date | Basic | One value per procedure | Read-Only | One value per session | §1.1 | 0 / 15 |
| 1.7 | Funding Source for Procedure Development | Advanced | One value per procedure | Read-Only | One value per session | §1.1 | 3 / 15 |
| 1.8 | Procedure Reference(s) | Advanced | One value per procedure | Read-Only | One value per session | §1.1 | 15 / 15 |
| 1.9 | Procedure DOI | N/A | — | Basic | One value per session | §2.1 | 0 / 15 |
| 1.10 | Session Identifier | N/A | — | Basic | One value per session | §2.1 | 0 / 15 |
| 1.11 | Analyst | N/A | — | Basic | One value per session | §2.1 | 5 / 15 |
| 1.12 | Analysis Start Date | N/A | — | Basic | One value per session | §2.1 | 0 / 15 |
| 1.13 | Analysis End Date | N/A | — | Basic | One value per session | §2.1 | 0 / 15 |
| 1.14 | Funding Source for Analysis | N/A | — | Basic | One value per session | §2.1 | 15 / 15 |
| 1.15 | Coupled Technique(s) | Advanced | One or more values per procedure | Editable | One or more values per session | §1.2; §2.1 | 15 / 15 |
| 1.16 | Coupling Description | Advanced | One value per procedure | Editable | One value per session | §1.2; §2.1 | 1 / 15 |
| 1.17 | Coupled Procedure DOI | N/A | — | Advanced | One value per session | §2.1 | 0 / 15 |
| 1.18 | Coupled Dataset or Publication Reference | N/A | — | Advanced | One or more values per session | §2.1 | 8 / 15 |
| 2.1 | Target Material | Basic | List of entries | Read-Only | List of entries | §1.3; Table 1; Table 2b | 15 / 15 |
| 2.2 | Sample Preparation Method | Basic | One value per procedure | Editable | One value per Sample Name | §1.3; Table 9 | 13 / 15 |
| 2.3 | Sample Name | N/A | — | Basic | List of entries | Table 9 | 15 / 15 |
| 2.4 | Sampling Unit Type | Basic | One value per procedure | Read-Only | One value per session | §1.3 | 15 / 15 |
| 2.5 | Sampling Unit Name | N/A | — | Basic | List of entries per Sample Name | Table 10 | 15 / 15 |
| 2.6 | Target Material of Sampling Unit | N/A | — | Basic | One value per Sampling Unit Name per Sample Name | Table 10 | 3 / 15 |
| 2.7 | Sample Persistent Identifier | N/A | — | Advanced | One value per Sample Name | Table 9 | 8 / 15 |
| 2.8 | Sampling Unit Selection Criteria | Basic | One value per procedure | Editable | One value per session | §1.3 | 15 / 15 |
| 2.9 | Pre-Analysis Imaging and Screening | Advanced | One value per procedure | Editable | One value per Sample Name | §1.3; Table 9 | 15 / 15 |
| 3.1 | Instrument Manufacturer | Basic | One value per procedure | Read-Only | One value per session | §1.4 | 15 / 15 |
| 3.2 | Instrument Model | Basic | One or more values per procedure | Read-Only | One or more values per session | §1.4 | 15 / 15 |
| 3.3 | Electron Source | Basic | One value per procedure | Read-Only | One value per session | §1.4 | 1 / 15 |
| 3.4 | Acquisition Software | Basic | One value per procedure | Editable | One value per session | §1.4; §2.3 | 4 / 15 |
| 3.5 | Data Processing Software(s) | Basic | One or more values per procedure | Editable | One or more values per session | §1.4; §2.3 | 6 / 15 |
| 3.6 | WDS Spectrometer Configuration | Advanced | One value per procedure | Read-Only | One value per session | §1.4 | 4 / 15 |
| 3.7 | EDS Detector Configuration | Advanced | One or more values per procedure | Read-Only | One or more values per session | §1.4 | 1 / 15 |
| 4.1 | Analytical Mode | Basic | One or more values per procedure | Read-Only | One or more values per session | §1.5 | 15 / 15 |
| 4.2 | Beam Mode | Basic | One value per Target Material | Read-Only | One value per Target Material | Table 1; §2.3 | 14 / 15 |
| 4.3 | Accelerating Voltage | Basic | One value per procedure | Editable | One value per session | §1.5; §2.3 | 15 / 15 |
| 4.4 | Beam Current | Basic | One value per Target Material | Editable | One value per Target Material | Table 1; §2.3 | 14 / 15 |
| 4.5 | Beam Diameter | Basic | One value per Target Material | Editable | One value per Target Material | Table 1; §2.3 | 14 / 15 |
| 4.6 | Beam Raster Dimensions | Advanced | One value per Target Material | Editable | One value per Target Material | Table 1; §2.3 | 2 / 15 |
| 4.7 | Beam Damage Minimization | Advanced | One value per Target Material | Editable | One value per Target Material | Table 1; §2.3 | 5 / 15 |
| 4.8 | Mapping Beam Mode | Basic | One value per procedure | Read-Only | One value per Sampling Unit Name per Sample Name | §1.5; §2.3 | 2 / 15 |
| 4.9 | Mapping Beam Current | Basic | One value per procedure | Editable | One value per Sampling Unit Name per Sample Name | §1.5; §2.3 | 3 / 15 |
| 4.10 | Mapping Beam Diameter | Basic | One value per procedure | Editable | One value per Sampling Unit Name per Sample Name | §1.5; §2.3 | 1 / 15 |
| 4.11 | Drift Correction | Advanced | One value per procedure | Editable | One value per session | §1.5 | 0 / 15 |
| 4.12 | Target Species | Basic | List of entries | Editable | List of entries | §1.6; Table 2 | 13 / 15 |
| 4.13 | Monitored Elements | Basic | List of entries per Target Species | Read-Only | List of entries per Target Species | §1.6; Table 3 | 15 / 15 |
| 4.14 | Reported Variables and Units | Basic | List of entries | Read-Only | List of entries | Table 4 | 15 / 15 |
| 4.15 | X-ray Detection Method per Monitored Element | Basic | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 6 / 15 |
| 4.16 | X-ray Line | Basic | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 4 / 15 |
| 4.17 | Diffracting Crystal | Basic | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 2 / 15 |
| 4.18 | WDS Spectrometer Channel | Advanced | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 1 / 15 |
| 4.19 | Sequence | Advanced | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3; §1.6 | 1 / 15 |
| 4.20 | Proportional Counter / Detector | Advanced | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 0 / 15 |
| 4.21 | WDS PHA Setting | Advanced | One value per Monitored Element | Read-Only | One value per Monitored Element | Table 3 | 0 / 15 |
| 4.22 | Peak Counting Time | Basic | One value per Monitored Element | Editable | One value per Monitored Element | Table 3b; §2.3 | 6 / 15 |
| 4.23 | Background Counting Time | Basic | One value per Monitored Element | Editable | One value per Monitored Element | Table 3b; §2.3 | 5 / 15 |
| 4.24 | Background Position(s) | Advanced | One value per Monitored Element | Editable | One value per Monitored Element | Table 3b | 4 / 15 |
| 4.25 | EDS Live Time per Point or Pixel | Basic | One value per procedure | Editable | One value per session | §1.7 | 0 / 15 |
| 4.26 | EDS Acquisition Mode | Basic | One or more values per procedure | Read-Only | One or more values per session | §1.7 | 14 / 15 |
| 4.27 | Dwell Time per Pixel | Basic | One value per Monitored Element | Editable | One value per Monitored Element | Table 3b; §1.8 | 2 / 15 |
| 4.28 | Step Size / Pixel Size | Basic | One value per procedure | Editable | One value per session | §1.8 | 2 / 15 |
| 4.29 | Map Dimensions | N/A | — | Basic | One value per session | §2.3 | 1 / 15 |
| 4.30 | Map Area | N/A | — | Basic | One value per session | §2.3 | 1 / 15 |
| 4.31 | Stage Scan vs. Beam Scan | Advanced | One value per procedure | Read-Only | One value per session | §1.8 | 2 / 15 |
| 5.1 | Matrix Correction Method | Basic | One value per procedure | Read-Only | One value per session | §1.9 | 6 / 15 |
| 5.2 | Mass Absorption Coefficients (MACs) | Basic | One value per procedure | Read-Only | One value per session | §1.9 | 0 / 15 |
| 5.3 | X-ray Background Correction Method | Basic | One value per Monitored Element | Editable | One value per Monitored Element | Table 3b | 4 / 15 |
| 5.4 | Time-Dependent Intensity Correction | Advanced | One value per Target Species | Editable | One value per Target Species | Table 5 | 0 / 15 |
| 5.5 | Target Species Estimation Method | Advanced | One value per Target Species | Read-Only | One value per Target Species | Table 2 | 2 / 15 |
| 5.6 | Halogen Correction on Oxygen | Advanced | One value per procedure | Editable | One value per session | §1.9 | 1 / 15 |
| 5.7 | WDS Dead Time Correction | Basic | One value per procedure | Read-Only | One value per session | §1.9 | 0 / 15 |
| 5.8 | EDS Spectral Processing Type | Advanced | One value per procedure | Read-Only | One value per session | §1.9 | 0 / 15 |
| 5.9 | Blank Correction | Advanced | One value per Target Species | Editable | One value per Target Species | Table 5 | 0 / 15 |
| 5.10 | Normalization / Standards-Based Correction | Advanced | One value per Reported Variable | Editable | One value per Reported Variable | Table 6 | 1 / 15 |
| 5.11 | Calibration Factor and Determination Method | Basic | One value per Reported Variable | Editable | One value per Reported Variable | §1.9 | 1 / 15 |
| 5.12 | Procedural Blank Level | N/A | — | Basic | One value per Target Species | §2.4 | 14 / 15 |
| 5.13 | Analysis Inclusion and Rejection Criteria | Basic | One value per procedure | Basic | One value per Combined Result | §1.9; Table 14 | 14 / 15 |
| 5.14 | Combination Method | Basic | One value per Reported Variable | Editable | One value per Reported Variable | §1.9 | 6 / 15 |
| 5.15 | Combined Results | N/A | — | Basic | List of entries | Table 14 | 7 / 15 |
| 5.16 | Constants and Reference Values Used | Basic | One value per procedure | Editable | One value per session | §1.9 | 0 / 15 |
| 6.1 | Primary Calibration Standard Name | Basic | One value per Target Material × Target Species | Editable | One value per Target Material × Target Species | Table 2b | 12 / 15 |
| 6.2 | Secondary Reference Materials | Basic | List of entries | Editable | List of entries | Table 7 | 4 / 15 |
| 6.3 | X-ray Line Overlap Corrections Applied | Basic | One value per Target Species | Read-Only | One value per Target Species | Table 5 | 1 / 15 |
| 6.4 | Interfering Elements | Advanced | One value per Target Species | Read-Only | One value per Target Species | Table 5 | 1 / 15 |
| 6.5 | Interference Correction Standard | Advanced | One value per Target Species | Read-Only | One value per Target Species | Table 5 | 1 / 15 |
| 6.6 | Detection Limit | Advanced | One value per Reported Variable | Basic | One value per Reported Variable | Table 6; Table 11 | 10 / 15 |
| 6.7 | Detection Limit Method | Basic | One value per Reported Variable | Read-Only | One value per Reported Variable | Table 6 | 1 / 15 |
| 6.8 | Analytical Precision | Advanced | One value per Secondary Reference Material × Reported Variable | Basic | One value per Secondary Reference Material × Reported Variable | Table 8; Table 12 | 0 / 15 |
| 6.9 | Analytical Accuracy | Advanced | One value per Secondary Reference Material × Reported Variable | Basic | One value per Secondary Reference Material × Reported Variable | Table 8; Table 12 | 1 / 15 |
| 6.10 | Counting Statistics Error | Advanced | One value per Reported Variable | Basic | One value per Sampling Unit Name × Reported Variable per Sample Name | Table 6; Table 13 | 0 / 15 |
| 6.11 | EDS Dead Time | N/A | — | Basic | One value per session | §2.4 | 0 / 15 |
| 6.12 | Goodness-of-Fit or Dispersion Statistic | N/A | — | Basic | One value per Combined Result × Reported Variable | Table 15 | 6 / 15 |
| 6.13 | Other Statistics | N/A | — | Advanced | One value per Combined Result × Reported Variable | Table 15 | 0 / 15 |
| 6.14 | Additional Notes | Advanced | One value per procedure | Advanced | One value per session | §2.5 | 15 / 15 |

**95 fields covered of 95.** 21 are stated in none of the assessed procedures, and 44 in two or fewer.

## Appendix B — The six gaps the v77 edition exposed, at v86

Writing the v77 edition to 100% coverage exposed six places where complete documentation needed a
structure the TAPP did not declare (`EPMA_Reference_Procedure_Example_v77.md`, Appendix B). Four
were closed by v86, and two are held.

1. **Beam conditions vary by phase — closed.** `Target Material` is now a list that beam conditions are
   stated against (Table 1), and each analysis point names its target material (Table 10). Maps have
   their own beam fields (§1.5, §2.3), since Liu et al. (2016) ran one material at 20 nA for points and
   200 nA for maps. *Held:* counting times per phase, which only Zega et al. (2025) state; the example
   still uses one counting time per element.
2. **Per-element values that differ between modes — held.** Table 3b still gives two background methods in
   one cell (two-point off-peak for points, MAN for maps), and §1.8 still reassigns P and Ni for mapping.
   None of the 15 assessed procedures states such a difference, so the TAPP waits for one that does.
3. **Statistics on combined values — closed.** Combined results are a session list (Table 14). The inclusion
   outcome is given per combined result, and the dispersion and other statistics per combined result and
   reported variable (Table 15). How each variable is combined is stated in §1.9.
4. **WDS or EDS chosen element by element — closed.** The detection method is stated per monitored element
   (Table 3), including Zn, which serves no target species. The WDS-only columns are still marked "—" for EDS
   elements. A general mechanism for applicability conditional on another field's value was deferred.
5. **Preparation differs by sample — closed.** Preparation is registered once and reported per sample
   (Table 9).
6. **Target species with no monitored element — closed.** The TAPP now says that a species determined by
   stoichiometry or by difference has none (O and C here).

**One further finding, from the literature rather than the example.** Nine of the 15 assessed papers
state their geometry (point analyses or maps) without naming WDS or EDS. `Analytical Mode` pairs the
two, so those papers cannot give it a value. Splitting EPMA's modes into geometry × detector is held.
