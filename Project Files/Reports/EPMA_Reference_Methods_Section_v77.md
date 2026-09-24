# Methods: electron probe microanalysis — a worked example

> **About this example.** This is a methods section written as it would appear in a paper, following EPMA TAPP v77. It covers the same fictional session as `EPMA_Reference_Procedure_Example_v77.md`. That file sets the content out field by field. This one writes it up as a reader of a journal would expect to see it. All 88 TAPP fields are covered. The laboratory, people, samples, identifiers, grants, dates and all results are fictional. Instruments, software, reference materials and the methods literature cited are real.

---

## 2. Methods

### 2.1 Samples and preparation

We analysed two epoxy mounts of carbonaceous-chondrite material: EX-CC-01 (IGSN:EXAMPLE0001), containing three particles, and EX-CC-02 (IGSN:EXAMPLE0002), containing two. The target phases were olivine and pyroxene, Fe–Ti–Cr oxides (magnetite, chromite, ilmenite), sulfides (pyrrhotite, pentlandite), phosphates (apatite, merrillite) and carbonates (calcite, dolomite, breunnerite). Both mounts were dry-polished with diamond to a final 0.25 µm and carbon coated to 20 nm together with the standards. EX-CC-02 was additionally Ar-ion polished after the final diamond step. Particle P2 of that mount was partly plucked during ion polishing, and all analyses of it lie on the fragment that remained. Before microprobe work, every particle was imaged in backscattered electrons (BSE) and mapped by energy-dispersive spectrometry (EDS) for Mg, Si, Fe, Ca, S and P on a field-emission SEM at 15 kV and 1 nA. The BSE images were registered to stage coordinates, and each analysis point is marked with its label on the BSE image of its particle (Supplementary Fig. S1).

Each point analysis was treated as one analytical result, labelled by particle and point number (for example, EX-CC-01 P1-03). Each X-ray map was treated as one result for its mapped area, without reporting its pixels individually. Points were placed only on grains at least 5 µm across for focused-beam analysis, or at least 10 µm across for phosphates and carbonates. Each point was at least 3 µm (5 µm for defocused or rastered beams) from grain boundaries, cracks and inclusions visible in BSE, and its phase identity was confirmed from its EDS spectrum before WDS acquisition began. Map areas were chosen to include every target phase present in a particle. In total we acquired 53 point analyses and two maps: 29 points and map M1 on EX-CC-01, and 24 points and map M2 on EX-CC-02. Supplementary Table S1 lists every point by sample, label and phase.

### 2.2 Instrumentation

Analyses were made on a JEOL JXA-8530F Plus electron microprobe with a Schottky field-emission source at the Example Microanalysis Laboratory (ROR https://ror.org/0example00), following the laboratory's registered procedure EML-EPMA-CC v2, *EPMA-WDS+EDS major and minor elements in carbonaceous-chondrite silicates, oxides, sulfides, phosphates and carbonates* (doi:10.0000/example.epma-cc.v2). The procedure was developed by the laboratory, has been in routine use since January 2025, and is described and validated in Example et al. (2025). It combines wavelength-dispersive (WDS) and energy-dispersive (EDS) spectrometry and covers point analysis and X-ray mapping by both. The instrument carries five JEOL wavelength-dispersive spectrometers. Their crystals are LDE1/TAP (Sp1), TAP/PETJ (Sp2), PETJ/LIF (Sp3), PETH/LIFH (Sp4) and LIF/PETL (Sp5). It also has the manufacturer's integrated silicon drift detector, with a 30 mm² active area, an ultra-thin polymer window and a 40° take-off angle. Spectrometers Sp1 and Sp2 use low-pressure P10 gas-flow proportional counters, and Sp3–Sp5 use sealed Xe counters. Acquisition was controlled with Probe for EPMA v13 (Probe Software). Point data were quantified in Probe for EPMA v13, quantitative maps were produced with CalcImage v13, and phases were classified from the maps in XMapTools 4. The analyses were performed by Analyst A (ORCID 0000-0000-0000-0000) from 12 to 14 April 2026, in a single session recorded in Probe for EPMA as run EML-2026-0412-A.

### 2.3 Analytical conditions

All analyses were made at 15 kV, the laboratory's standard operating voltage. Beam conditions were set by phase and recorded for each point (Supplementary Table S1). Olivine, pyroxene, oxides and sulfides were analysed with a focused 1 µm beam at 20 nA. Phosphates were analysed with the beam defocused to 5 µm at 8 nA, and carbonates with a focused beam rastered over 5 × 5 µm at 4 nA to spread the dose. X-ray maps were acquired with a focused beam at 50 nA. To limit volatilisation and migration of alkalis and halogens under the beam, Na, K, F and Cl were measured in the first acquisition pass on every point, and time-dependent intensity corrections were applied to Na (linear) and to F in apatite (exponential). The beam current was measured with the Faraday cup before each point and at the start of each map line, and intensities were normalised to it. Primary standards were re-measured at the start and end of the session, and drift in their intensities was interpolated linearly with time.

The procedure determines 18 elements. Si, Mg, Fe, Ca and S were measured by EDS. Ti, Al, Cr, Mn, Na, K, P, F, Cl, Ni and Co were measured by WDS. O and C were not measured: oxygen was calculated by stoichiometry from cation valences, and carbon as CO₂ by stoichiometry in carbonates only. In apatite, OH was calculated by difference assuming F + Cl + OH = 1 atom per formula unit (Ketcham 2015). Zn was also measured by WDS, not to be reported but to correct the overlap of Zn Lα on Na Kα. Table 1 gives, for each measured element, the X-ray line, the spectrometer and crystal, the acquisition pass, the counting times and background positions, the primary standard and the session detection limit.

In WDS point analysis the twelve WDS elements were acquired in three passes, and in each pass all assigned spectrometers counted simultaneously. The first pass measured F, Na, K, Cl and Zn, and the second Al, P, Ti, Cr and Mn. The third measured Co and Ni, with Ni counted on Sp4 and Sp5 at the same time and the two intensities aggregated. The EDS spectrum was acquired during the first pass, with a live time of 30 s. Differential pulse-height analysis was used for F and Na to reject higher-order reflections, and integral mode for all other elements. The procedure specifies peak counting times of 40 s for Co and Ni. In this session we raised them to 60 s, within the procedure's bounds, to lower detection limits in olivine. All other conditions were as registered. Backgrounds were measured at two off-peak positions for every WDS element (Table 1) and interpolated linearly, except for F, where an exponential fit was used to account for curvature of the LDE1 background.

**Table 1.** WDS and EDS analytical conditions for each measured element. Background time is the total of both positions. Detection limits are 3σ of the background, as medians over the included analyses, in wt% oxide (element for S, F and Cl).

| Element | Line | Spectrometer (crystal) | Pass | Peak / background time (s) | Background offsets (mm) | Primary standard | Detection limit (wt%) |
|---|---|---|---|---|---|---|---|
| F | Kα | Sp1 (LDE1) | 1 | 20 / 20 | −3.2 / +4.5 | Synthetic SrF₂ | 0.055 |
| Na | Kα | Sp2 (TAP) | 1 | 10 / 10 | −4.0 / +4.0 | Amelia albite | 0.018 |
| K | Kα | Sp3 (PETJ) | 1 | 10 / 10 | −4.5 / +4.5 | Microcline USNM 143966 | 0.009 |
| Cl | Kα | Sp4 (PETH) | 1 | 20 / 20 | −3.0 / +3.0 | Scapolite USNM R6600-1 | 0.010 |
| Zn* | Kα | Sp5 (LIF) | 1 | 10 / 10 | −3.5 / +3.5 | Synthetic ZnS | — |
| Al | Kα | Sp1 (TAP) | 2 | 20 / 20 | −3.5 / +3.5 | Anorthite USNM 137041 | 0.012 |
| P | Kα | Sp2 (PETJ) | 2 | 20 / 20 | −4.0 / +4.0 | Wilberforce fluorapatite | 0.020 |
| Ti | Kα | Sp3 (PETJ) | 2 | 30 / 30 | −5.0 / +5.0 | Ilmenite USNM 96189 | 0.015 |
| Cr | Kα | Sp4 (LIFH) | 2 | 30 / 30 | −3.0 / +3.0 | Synthetic Cr₂O₃ | 0.018 |
| Mn | Kα | Sp5 (LIF) | 2 | 30 / 30 | −3.5 / +3.5 | Rhodonite | 0.016 |
| Co | Kα | Sp3 (LIF) | 3 | 60 / 60† | −2.5 / +3.5 | Co metal | 0.010 |
| Ni | Kα | Sp4 (LIFH) + Sp5 (LIF) | 3 | 60 / 60† | −3.0 / +3.0 | Ni metal | 0.008 |
| Si | Kα | EDS | — | 30 s live | — | Springwater olivine USNM 2566 | 0.11 |
| Mg | Kα | EDS | — | 30 s live | — | Springwater olivine USNM 2566 | 0.09 |
| Fe | Kα | EDS | — | 30 s live | — | Rockport fayalite USNM 85276 | 0.14 |
| Ca | Kα | EDS | — | 30 s live | — | Diopside USNM 117733 | 0.10 |
| S | Kα | EDS | — | 30 s live | — | Synthetic FeS | 0.08 |

\* Measured only to correct its Lα overlap on Na Kα; not reported.
† 40 / 40 s in the registered procedure; raised for this session.

Smithsonian standards use the accepted values of Jarosewich et al. (1980). The laboratory standards are stoichiometric compounds or use the supplier's certified values.

### 2.4 X-ray mapping

One particle in each mount was mapped: P1 of EX-CC-01 as map M1, and P1 of EX-CC-02 as map M2. Maps were acquired by stage scan with the beam held fixed. The step size was 2 µm in both X and Y, and the dwell time was 30 ms per pixel. WDS maps of Na (Sp2, TAP), Al (Sp1, TAP), P (Sp3, PETJ), Cr (Sp4, LIFH) and Ni (Sp5, LIF) were collected in a single pass. P and Ni were therefore assigned to different spectrometers than in point analysis. An EDS spectrum image, keeping a full spectrum at every pixel, was collected simultaneously and provided the Si, Mg, Fe, Ca and S maps. EDS acquisition used point spectra and spectrum images only; no line scans were made. Map M1 (EX-CC-01) covered 512 × 512 pixels, or 1.024 × 1.024 mm. Map M2 (EX-CC-02) covered 384 × 256 pixels, or 0.768 × 0.512 mm. In the maps, the WDS backgrounds were removed with a mean-atomic-number (MAN) calibration (Donovan and Tingle 1996) rather than off-peak measurement, so all dwell time was spent on peak.

### 2.5 Data reduction

Intensities were converted to concentrations with the Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995) in Probe for EPMA, using mass absorption coefficients from FFAST (Chantler et al. 2005). The same correction was applied pixel by pixel in CalcImage to produce quantitative maps. WDS dead time was corrected with the logarithmic expression and spectrometer-specific constants of 1.1–1.5 µs determined by the laboratory. EDS net intensities were extracted by filter fitting — a top-hat filter followed by least-squares fitting to measured standard spectra — which also removed the EDS background in both points and maps. All concentrations derive from k-ratios against the primary standards; no externally calibrated conversion factor was used for any reported quantity. Oxide conversions and structural formulas used the IUPAC 2021 standard atomic weights (Prohaska et al. 2022).

Three X-ray line overlaps were corrected quantitatively, with the correction iterated together with the matrix correction. The overlap of Fe Kβ on Co Kα was calibrated on Co-free Rockport fayalite, Cr Kβ on Mn Kα on Mn-free synthetic Cr₂O₃, and Zn Lα on Na Kα on Na-free synthetic ZnS. No other element required an overlap correction. For Ni and Co, the apparent concentration measured on Ni- and Co-free synthetic forsterite was subtracted as a blank. In this session the blank was 35 ± 9 µg/g for Ni and 22 ± 8 µg/g for Co (n = 5). No other element was blank-corrected. In apatite, the oxygen equivalent of F and Cl was subtracted from the total.

We report SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe as FeO), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO and CoO as oxides in wt%, and S, F and Cl as elements in wt%. We also report the oxygen equivalent of F and Cl, CO₂ by stoichiometry for carbonates, and analytical totals. Structural formulas are given in atoms per formula unit (apfu), normalised to a fixed anion basis for each phase: 4 O for olivine and spinels, 6 O for pyroxene and dolomite, 3 O for calcite, and 13 anions for apatite (Ketcham 2015). The maps yield element concentrations in wt% per pixel, a phase map, and modal abundances in area %. No other normalisation or standards-based correction was applied.

Mean compositions are reported for each phase in each sample, and a point contributed to its phase mean only if it passed four tests. Its analytical total had to fall between 98.5 and 101.5 wt% for silicates, oxides and sulfides, between 96.0 and 101.5 wt% for apatite (whose OH is calculated by difference), or between 98.0 and 102.0 wt% for carbonates (with CO₂ by stoichiometry). Its cation sum had to lie within ±0.03 apfu of the ideal value, it could not overlap a second phase in the post-analysis BSE image, and the beam current could not have drifted by more than 1% during the analysis. Of the 53 points acquired, 45 passed. Four were excluded for totals outside the window: EX-CC-01 P3-02 and P3-05 (apatite), and EX-CC-02 P1-03 and P1-07 (dolomite). Three were excluded because they overlapped a neighbouring phase: EX-CC-01 P2-07 and P2-09 (pyrrhotite beside pentlandite), and EX-CC-02 P1-16 (calcite at a grain boundary). One, EX-CC-02 P2-05, was excluded for beam-current drift.

### 2.6 Quality control and uncertainties

Five Smithsonian reference materials were analysed as unknowns at the start, middle and end of the session, with accepted values from Jarosewich et al. (1980): San Carlos olivine USNM 111312/444 (n = 9), Kakanui augite USNM 122142 (n = 6), Durango apatite USNM 104021 (n = 6), chromite USNM 117075 (n = 5) and calcite USNM 136321 (n = 6). Supplementary Table S2 reports precision (1σ relative standard deviation) and accuracy (relative deviation from the accepted value) for each material and each reported variable assessed on it. Precision was 0.4–0.7% for oxides above 10 wt%, 0.9–1.6% for FeO and Al₂O₃, 2–4% for TiO₂, Na₂O, F and Cl, and 4% for NiO in San Carlos olivine. Accuracy was within ±1.2% relative for all major oxides and within ±2.6% for the minor oxides and halogens.

Detection limits were calculated as 3σ of the background counts for each reported variable. Table 1 gives the session values. In maps, the detection limit is about 0.3 wt% per pixel for the WDS elements and 0.7 wt% for the EDS elements. For every analysis and every reported variable, Supplementary Table S1 gives the 1σ uncertainty predicted from counting statistics on the peak and on any subtracted background or blank. In olivine, these are about 0.5% relative for SiO₂ and MgO and about 10% for NiO at 0.03 wt%. EDS dead time was 18–26% during point analysis and 24–31% during spectrum imaging.

To test whether each phase mean was a single population, we computed the MSWD of its contributing analyses about their mean, using their counting-statistics uncertainties. For olivine in EX-CC-01 (n = 8), the MSWD ranged from 0.9 (NiO) to 2.3 (CaO) for all oxides except FeO. FeO reached 4.6, consistent with the Fe–Mg zoning visible in map M1. Supplementary Table S3 gives the MSWD for every phase mean and reported variable. No anomalies, instrument modifications or other departures from the registered procedure occurred beyond those noted above.

### 2.7 Coupled analyses

The EPMA data were collected as part of a coupled workflow with SEM and NanoSIMS. SEM imaging came first and located the phases analysed (Section 2.1). EPMA followed because it is non-destructive. After EPMA, the carbon coat was replaced with gold for NanoSIMS oxygen-isotope analysis of the carbonates at the Example Isotope Laboratory, which came last because sputtering destroys the analysed volume. The EPMA composition of each carbonate was used to select the matrix-matched carbonate reference material for the NanoSIMS instrumental mass-fractionation correction. The NanoSIMS procedure is being registered (DOI pending), and its data are included in the same submission as this dataset.

---

### Acknowledgements (funding)

The electron microprobe was funded by Example Agency award EX-INST-0001, and development of the analytical procedure by award EX-DEV-0002. The analyses reported here were funded by Example Agency award EX-SCI-0003.

### Data availability

All point analyses, with their labels, phases, beam conditions and 1σ counting-statistics uncertainties, are given in Supplementary Table S1. The quantitative maps are included in the same data package. The session is recorded as Probe for EPMA run EML-2026-0412-A at the Example Microanalysis Laboratory. It followed the registered procedure doi:10.0000/example.epma-cc.v2. The coupled NanoSIMS data are included in the same submission.

### Supplementary material referred to above

- **Table S1.** Every analysis point: sample, point label, phase, beam mode, current, diameter and raster dimensions, and the full set of reported variables, each with its 1σ counting-statistics uncertainty.
- **Table S2.** Precision and accuracy for each secondary reference material and each reported variable.
- **Table S3.** MSWD for each phase mean and each reported variable.
- **Figure S1.** BSE images of each particle, with every analysis point labelled.

### References

Armstrong, J.T. (1995) CITZAF: a package of correction programs for the quantitative electron microbeam X-ray analysis of thick polished materials, thin films, and particles. *Microbeam Analysis* 4, 177–200.

Chantler, C.T., et al. (2005) X-ray form factor, attenuation and scattering tables (FFAST), version 2.1. National Institute of Standards and Technology.

Donovan, J.J. and Tingle, T.N. (1996) An improved mean atomic number background correction for quantitative microanalysis. *Microscopy and Microanalysis* 2, 1–7.

Jarosewich, E., Nelen, J.A. and Norberg, J.A. (1980) Reference samples for electron microprobe analysis. *Geostandards Newsletter* 4, 43–47.

Ketcham, R.A. (2015) Technical note: Calculation of stoichiometry from EMP data for apatite and other phases with mixing on monovalent anion sites. *American Mineralogist* 100, 1620–1623.

Prohaska, T., et al. (2022) Standard atomic weights of the elements 2021 (IUPAC Technical Report). *Pure and Applied Chemistry* 94, 573–600.

*Fictional, for this example only:* Example et al. (2025), doi:10.0000/example.2025.001.
