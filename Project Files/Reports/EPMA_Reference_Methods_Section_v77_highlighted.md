# Methods: electron probe microanalysis — a worked example

> **About this example.** This is a methods section written as it would appear in a paper, following EPMA TAPP v77. It covers the same fictional session as `EPMA_Reference_Procedure_Example_v77.md`. That file sets the content out field by field. This one writes it up as a reader of a journal would expect to see it. All 88 TAPP fields are covered. The laboratory, people, samples, identifiers, grants, dates and all results are fictional. Instruments, software, reference materials and the methods literature cited are real.

> **Highlighting.** <mark>Highlighted</mark> text is information that fills a field of EPMA TAPP v77: a value, a choice, an identifier, a rule or an outcome. Text that is not highlighted is what joins that information into readable prose: connecting phrases, pointers to tables and supplements, rationale the TAPP does not ask for, and citations of methods literature. Every cell of Table 1 is highlighted. Generated from `EPMA_Reference_Methods_Section_v77.md` by `make_highlighted_methods.py`.

---

## 2. Methods

### 2.1 Samples and preparation

We analysed two <mark>epoxy mounts</mark> <mark>of carbonaceous-chondrite material</mark>: <mark>EX-CC-01</mark> (<mark>IGSN:EXAMPLE0001</mark>), containing three particles, and <mark>EX-CC-02</mark> (<mark>IGSN:EXAMPLE0002</mark>), containing two. The target phases were <mark>olivine and pyroxene, Fe–Ti–Cr oxides (magnetite, chromite, ilmenite), sulfides (pyrrhotite, pentlandite), phosphates (apatite, merrillite) and carbonates (calcite, dolomite, breunnerite)</mark>. Both mounts were <mark>dry-polished with diamond to a final 0.25 µm and carbon coated to 20 nm</mark> together with the standards. EX-CC-02 was <mark>additionally Ar-ion polished after the final diamond step</mark>. <mark>Particle P2 of that mount was partly plucked during ion polishing, and all analyses of it lie on the fragment that remained</mark>. Before microprobe work, every particle was <mark>imaged in backscattered electrons (BSE) and mapped by energy-dispersive spectrometry (EDS) for Mg, Si, Fe, Ca, S and P on a field-emission SEM at 15 kV and 1 nA</mark>. The BSE images were <mark>registered to stage coordinates, and each analysis point is marked with its label on the BSE image of its particle</mark> (Supplementary Fig. S1).

<mark>Each point analysis was treated as one analytical result</mark>, <mark>labelled by particle and point number</mark> (for example, EX-CC-01 P1-03). <mark>Each X-ray map was treated as one result for its mapped area, without reporting its pixels individually</mark>. Points were placed only on grains <mark>at least 5 µm across for focused-beam analysis, or at least 10 µm across for phosphates and carbonates</mark>. Each point was <mark>at least 3 µm (5 µm for defocused or rastered beams) from grain boundaries, cracks and inclusions visible in BSE</mark>, and <mark>its phase identity was confirmed from its EDS spectrum before WDS acquisition began</mark>. <mark>Map areas were chosen to include every target phase present in a particle</mark>. In total we acquired <mark>53 point analyses and two maps: 29 points and map M1 on EX-CC-01, and 24 points and map M2 on EX-CC-02</mark>. Supplementary Table S1 lists every point by sample, label and phase.

### 2.2 Instrumentation

Analyses were made on a <mark>JEOL</mark> <mark>JXA-8530F Plus</mark> electron microprobe with a <mark>Schottky field-emission source</mark> at the <mark>Example Microanalysis Laboratory</mark> (ROR <mark>https://ror.org/0example00</mark>), following the laboratory's registered procedure <mark>EML-EPMA-CC v2, *EPMA-WDS+EDS major and minor elements in carbonaceous-chondrite silicates, oxides, sulfides, phosphates and carbonates*</mark> (<mark>doi:10.0000/example.epma-cc.v2</mark>). The procedure was <mark>developed by the laboratory</mark>, has been in routine use since <mark>January 2025</mark>, and is described and validated in <mark>Example et al. (2025)</mark>. It <mark>combines wavelength-dispersive (WDS) and energy-dispersive (EDS) spectrometry</mark> and <mark>covers point analysis and X-ray mapping by both</mark>. The instrument carries <mark>five JEOL wavelength-dispersive spectrometers</mark>. Their crystals are <mark>LDE1/TAP (Sp1), TAP/PETJ (Sp2), PETJ/LIF (Sp3), PETH/LIFH (Sp4) and LIF/PETL (Sp5)</mark>. It also has the manufacturer's <mark>integrated silicon drift detector, with a 30 mm² active area, an ultra-thin polymer window and a 40° take-off angle</mark>. Spectrometers Sp1 and Sp2 use <mark>low-pressure P10 gas-flow proportional counters</mark>, and Sp3–Sp5 use <mark>sealed Xe counters</mark>. Acquisition was controlled with <mark>Probe for EPMA v13 (Probe Software)</mark>. Point data were quantified in <mark>Probe for EPMA v13</mark>, quantitative maps were produced with <mark>CalcImage v13</mark>, and phases were classified from the maps in <mark>XMapTools 4</mark>. The analyses were performed by <mark>Analyst A (ORCID 0000-0000-0000-0000)</mark> from <mark>12 to 14 April 2026</mark>, in a single session recorded in Probe for EPMA as run <mark>EML-2026-0412-A</mark>.

### 2.3 Analytical conditions

All analyses were made at <mark>15 kV, the laboratory's standard operating voltage</mark>. Beam conditions were set by phase and recorded for each point (Supplementary Table S1). Olivine, pyroxene, oxides and sulfides were analysed with a <mark>focused 1 µm beam at 20 nA</mark>. Phosphates were analysed with the beam <mark>defocused to 5 µm at 8 nA</mark>, and carbonates with a <mark>focused beam rastered over 5 × 5 µm at 4 nA</mark> to spread the dose. X-ray maps were acquired with a <mark>focused beam at 50 nA</mark>. To limit volatilisation and migration of alkalis and halogens under the beam, <mark>Na, K, F and Cl were measured in the first acquisition pass on every point</mark>, and <mark>time-dependent intensity corrections were applied to Na (linear) and to F in apatite (exponential)</mark>. The beam current was <mark>measured with the Faraday cup before each point and at the start of each map line, and intensities were normalised to it</mark>. <mark>Primary standards were re-measured at the start and end of the session, and drift in their intensities was interpolated linearly with time</mark>.

The procedure determines 18 elements. <mark>Si, Mg, Fe, Ca and S were measured by EDS</mark>. <mark>Ti, Al, Cr, Mn, Na, K, P, F, Cl, Ni and Co were measured by WDS</mark>. O and C were not measured: <mark>oxygen was calculated by stoichiometry from cation valences, and carbon as CO₂ by stoichiometry in carbonates only</mark>. In apatite, <mark>OH was calculated by difference assuming F + Cl + OH = 1 atom per formula unit (Ketcham 2015)</mark>. <mark>Zn was also measured by WDS</mark>, not to be reported but to <mark>correct the overlap of Zn Lα on Na Kα</mark>. Table 1 gives, for each measured element, the X-ray line, the spectrometer and crystal, the acquisition pass, the counting times and background positions, the primary standard and the session detection limit.

In WDS point analysis the twelve WDS elements were acquired in <mark>three passes</mark>, and in each pass all assigned spectrometers counted simultaneously. The first pass measured <mark>F, Na, K, Cl and Zn</mark>, and the second <mark>Al, P, Ti, Cr and Mn</mark>. The third measured <mark>Co and Ni</mark>, with <mark>Ni counted on Sp4 and Sp5 at the same time and the two intensities aggregated</mark>. The EDS spectrum was acquired during the first pass, with a <mark>live time of 30 s</mark>. <mark>Differential pulse-height analysis was used for F and Na</mark> to reject higher-order reflections, and <mark>integral mode for all other elements</mark>. The procedure specifies <mark>peak counting times of 40 s for Co and Ni</mark>. In this session we <mark>raised them to 60 s</mark>, within the procedure's bounds, to lower detection limits in olivine. <mark>All other conditions were as registered</mark>. Backgrounds were <mark>measured at two off-peak positions for every WDS element</mark> (Table 1) and <mark>interpolated linearly</mark>, except for F, where <mark>an exponential fit</mark> was used to account for curvature of the LDE1 background.

**Table 1.** WDS and EDS analytical conditions for each measured element. Background time is the total of both positions. Detection limits are <mark>3σ of the background</mark>, as medians over the included analyses, in wt% oxide (element for S, F and Cl).

| Element | Line | Spectrometer (crystal) | Pass | Peak / background time (s) | Background offsets (mm) | Primary standard | Detection limit (wt%) |
|---|---|---|---|---|---|---|---|
| <mark>F</mark> | <mark>Kα</mark> | <mark>Sp1 (LDE1)</mark> | <mark>1</mark> | <mark>20 / 20</mark> | <mark>−3.2 / +4.5</mark> | <mark>Synthetic SrF₂</mark> | <mark>0.055</mark> |
| <mark>Na</mark> | <mark>Kα</mark> | <mark>Sp2 (TAP)</mark> | <mark>1</mark> | <mark>10 / 10</mark> | <mark>−4.0 / +4.0</mark> | <mark>Amelia albite</mark> | <mark>0.018</mark> |
| <mark>K</mark> | <mark>Kα</mark> | <mark>Sp3 (PETJ)</mark> | <mark>1</mark> | <mark>10 / 10</mark> | <mark>−4.5 / +4.5</mark> | <mark>Microcline USNM 143966</mark> | <mark>0.009</mark> |
| <mark>Cl</mark> | <mark>Kα</mark> | <mark>Sp4 (PETH)</mark> | <mark>1</mark> | <mark>20 / 20</mark> | <mark>−3.0 / +3.0</mark> | <mark>Scapolite USNM R6600-1</mark> | <mark>0.010</mark> |
| <mark>Zn*</mark> | <mark>Kα</mark> | <mark>Sp5 (LIF)</mark> | <mark>1</mark> | <mark>10 / 10</mark> | <mark>−3.5 / +3.5</mark> | <mark>Synthetic ZnS</mark> | — |
| <mark>Al</mark> | <mark>Kα</mark> | <mark>Sp1 (TAP)</mark> | <mark>2</mark> | <mark>20 / 20</mark> | <mark>−3.5 / +3.5</mark> | <mark>Anorthite USNM 137041</mark> | <mark>0.012</mark> |
| <mark>P</mark> | <mark>Kα</mark> | <mark>Sp2 (PETJ)</mark> | <mark>2</mark> | <mark>20 / 20</mark> | <mark>−4.0 / +4.0</mark> | <mark>Wilberforce fluorapatite</mark> | <mark>0.020</mark> |
| <mark>Ti</mark> | <mark>Kα</mark> | <mark>Sp3 (PETJ)</mark> | <mark>2</mark> | <mark>30 / 30</mark> | <mark>−5.0 / +5.0</mark> | <mark>Ilmenite USNM 96189</mark> | <mark>0.015</mark> |
| <mark>Cr</mark> | <mark>Kα</mark> | <mark>Sp4 (LIFH)</mark> | <mark>2</mark> | <mark>30 / 30</mark> | <mark>−3.0 / +3.0</mark> | <mark>Synthetic Cr₂O₃</mark> | <mark>0.018</mark> |
| <mark>Mn</mark> | <mark>Kα</mark> | <mark>Sp5 (LIF)</mark> | <mark>2</mark> | <mark>30 / 30</mark> | <mark>−3.5 / +3.5</mark> | <mark>Rhodonite</mark> | <mark>0.016</mark> |
| <mark>Co</mark> | <mark>Kα</mark> | <mark>Sp3 (LIF)</mark> | <mark>3</mark> | <mark>60 / 60†</mark> | <mark>−2.5 / +3.5</mark> | <mark>Co metal</mark> | <mark>0.010</mark> |
| <mark>Ni</mark> | <mark>Kα</mark> | <mark>Sp4 (LIFH) + Sp5 (LIF)</mark> | <mark>3</mark> | <mark>60 / 60†</mark> | <mark>−3.0 / +3.0</mark> | <mark>Ni metal</mark> | <mark>0.008</mark> |
| <mark>Si</mark> | <mark>Kα</mark> | <mark>EDS</mark> | — | <mark>30 s live</mark> | — | <mark>Springwater olivine USNM 2566</mark> | <mark>0.11</mark> |
| <mark>Mg</mark> | <mark>Kα</mark> | <mark>EDS</mark> | — | <mark>30 s live</mark> | — | <mark>Springwater olivine USNM 2566</mark> | <mark>0.09</mark> |
| <mark>Fe</mark> | <mark>Kα</mark> | <mark>EDS</mark> | — | <mark>30 s live</mark> | — | <mark>Rockport fayalite USNM 85276</mark> | <mark>0.14</mark> |
| <mark>Ca</mark> | <mark>Kα</mark> | <mark>EDS</mark> | — | <mark>30 s live</mark> | — | <mark>Diopside USNM 117733</mark> | <mark>0.10</mark> |
| <mark>S</mark> | <mark>Kα</mark> | <mark>EDS</mark> | — | <mark>30 s live</mark> | — | <mark>Synthetic FeS</mark> | <mark>0.08</mark> |

\* <mark>Measured only to correct its Lα overlap on Na Kα</mark>; not reported.
† <mark>40 / 40 s in the registered procedure</mark>; raised for this session.

Smithsonian standards use the <mark>accepted values of Jarosewich et al. (1980)</mark>. The laboratory standards are <mark>stoichiometric compounds or use the supplier's certified values</mark>.

### 2.4 X-ray mapping

One particle in each mount was mapped: <mark>P1 of EX-CC-01 as map M1, and P1 of EX-CC-02 as map M2</mark>. Maps were acquired by <mark>stage scan with the beam held fixed</mark>. The step size was <mark>2 µm in both X and Y</mark>, and the dwell time was <mark>30 ms per pixel</mark>. WDS maps of <mark>Na (Sp2, TAP), Al (Sp1, TAP), P (Sp3, PETJ), Cr (Sp4, LIFH) and Ni (Sp5, LIF)</mark> were collected in a single pass. P and Ni were therefore assigned to different spectrometers than in point analysis. An <mark>EDS spectrum image</mark>, keeping a full spectrum at every pixel, was collected simultaneously and provided the Si, Mg, Fe, Ca and S maps. EDS acquisition used <mark>point spectra and spectrum images only; no line scans were made</mark>. Map M1 (EX-CC-01) covered <mark>512 × 512 pixels</mark>, or <mark>1.024 × 1.024 mm</mark>. Map M2 (EX-CC-02) covered <mark>384 × 256 pixels</mark>, or <mark>0.768 × 0.512 mm</mark>. In the maps, the WDS backgrounds were removed with a <mark>mean-atomic-number (MAN) calibration (Donovan and Tingle 1996)</mark> rather than off-peak measurement, so all dwell time was spent on peak.

### 2.5 Data reduction

Intensities were converted to concentrations with the <mark>Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995)</mark> in Probe for EPMA, using mass absorption coefficients from <mark>FFAST (Chantler et al. 2005)</mark>. The same correction was <mark>applied pixel by pixel in CalcImage</mark> to produce quantitative maps. WDS dead time was corrected with the <mark>logarithmic expression and spectrometer-specific constants of 1.1–1.5 µs</mark> determined by the laboratory. EDS net intensities were extracted by <mark>filter fitting — a top-hat filter followed by least-squares fitting to measured standard spectra</mark> — which also <mark>removed the EDS background in both points and maps</mark>. All concentrations derive from k-ratios against the primary standards; <mark>no externally calibrated conversion factor was used for any reported quantity</mark>. Oxide conversions and structural formulas used the <mark>IUPAC 2021 standard atomic weights (Prohaska et al. 2022)</mark>.

<mark>Three X-ray line overlaps were corrected quantitatively, with the correction iterated together with the matrix correction</mark>. The overlap of <mark>Fe Kβ on Co Kα</mark> was calibrated on <mark>Co-free Rockport fayalite</mark>, <mark>Cr Kβ on Mn Kα</mark> on <mark>Mn-free synthetic Cr₂O₃</mark>, and <mark>Zn Lα on Na Kα</mark> on <mark>Na-free synthetic ZnS</mark>. <mark>No other element required an overlap correction</mark>. For Ni and Co, <mark>the apparent concentration measured on Ni- and Co-free synthetic forsterite was subtracted as a blank</mark>. In this session the blank was <mark>35 ± 9 µg/g for Ni and 22 ± 8 µg/g for Co (n = 5)</mark>. <mark>No other element was blank-corrected</mark>. In apatite, <mark>the oxygen equivalent of F and Cl was subtracted from the total</mark>.

We report <mark>SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe as FeO), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO and CoO as oxides in wt%</mark>, and <mark>S, F and Cl as elements in wt%</mark>. We also report <mark>the oxygen equivalent of F and Cl, CO₂ by stoichiometry for carbonates, and analytical totals</mark>. Structural formulas are given in <mark>atoms per formula unit (apfu)</mark>, <mark>normalised to a fixed anion basis for each phase: 4 O for olivine and spinels, 6 O for pyroxene and dolomite, 3 O for calcite, and 13 anions for apatite (Ketcham 2015)</mark>. The maps yield <mark>element concentrations in wt% per pixel, a phase map, and modal abundances in area %</mark>. <mark>No other normalisation or standards-based correction was applied</mark>.

<mark>Mean compositions are reported for each phase in each sample</mark>, and a point contributed to its phase mean only if it passed four tests. Its analytical total had to fall <mark>between 98.5 and 101.5 wt% for silicates, oxides and sulfides, between 96.0 and 101.5 wt% for apatite (whose OH is calculated by difference), or between 98.0 and 102.0 wt% for carbonates (with CO₂ by stoichiometry)</mark>. Its cation sum had to lie <mark>within ±0.03 apfu of the ideal value</mark>, it <mark>could not overlap a second phase in the post-analysis BSE image</mark>, and the beam current could not have <mark>drifted by more than 1% during the analysis</mark>. <mark>Of the 53 points acquired, 45 passed</mark>. <mark>Four were excluded for totals outside the window: EX-CC-01 P3-02 and P3-05 (apatite), and EX-CC-02 P1-03 and P1-07 (dolomite)</mark>. <mark>Three were excluded because they overlapped a neighbouring phase: EX-CC-01 P2-07 and P2-09 (pyrrhotite beside pentlandite), and EX-CC-02 P1-16 (calcite at a grain boundary)</mark>. <mark>One, EX-CC-02 P2-05, was excluded for beam-current drift</mark>.

### 2.6 Quality control and uncertainties

Five Smithsonian reference materials were analysed as unknowns at the start, middle and end of the session, with <mark>accepted values from Jarosewich et al. (1980)</mark>: <mark>San Carlos olivine USNM 111312/444 (n = 9)</mark>, <mark>Kakanui augite USNM 122142 (n = 6)</mark>, <mark>Durango apatite USNM 104021 (n = 6)</mark>, <mark>chromite USNM 117075 (n = 5)</mark> and <mark>calcite USNM 136321 (n = 6)</mark>. Supplementary Table S2 reports precision (1σ relative standard deviation) and accuracy (relative deviation from the accepted value) for each material and each reported variable assessed on it. Precision was <mark>0.4–0.7% for oxides above 10 wt%, 0.9–1.6% for FeO and Al₂O₃, 2–4% for TiO₂, Na₂O, F and Cl, and 4% for NiO in San Carlos olivine</mark>. Accuracy was <mark>within ±1.2% relative for all major oxides and within ±2.6% for the minor oxides and halogens</mark>.

Detection limits were calculated as <mark>3σ of the background counts</mark> for each reported variable. Table 1 gives the session values. In maps, the detection limit is about <mark>0.3 wt% per pixel for the WDS elements and 0.7 wt% for the EDS elements</mark>. For every analysis and every reported variable, Supplementary Table S1 gives the <mark>1σ uncertainty predicted from counting statistics on the peak and on any subtracted background or blank</mark>. In olivine, these are about <mark>0.5% relative for SiO₂ and MgO and about 10% for NiO at 0.03 wt%</mark>. EDS dead time was <mark>18–26% during point analysis and 24–31% during spectrum imaging</mark>.

To test whether each phase mean was a single population, we computed the <mark>MSWD of its contributing analyses about their mean, using their counting-statistics uncertainties</mark>. For olivine in EX-CC-01 (n = 8), the MSWD ranged from <mark>0.9 (NiO) to 2.3 (CaO)</mark> for all oxides except FeO. FeO reached <mark>4.6</mark>, consistent with the Fe–Mg zoning visible in map M1. Supplementary Table S3 gives the MSWD for every phase mean and reported variable. <mark>No anomalies, instrument modifications or other departures from the registered procedure occurred beyond those noted above</mark>.

### 2.7 Coupled analyses

The EPMA data were collected as part of a coupled workflow with <mark>SEM and NanoSIMS</mark>. <mark>SEM imaging came first</mark> and located the phases analysed (Section 2.1). <mark>EPMA followed because it is non-destructive</mark>. After EPMA, <mark>the carbon coat was replaced with gold for NanoSIMS oxygen-isotope analysis of the carbonates at the Example Isotope Laboratory, which came last because sputtering destroys the analysed volume</mark>. <mark>The EPMA composition of each carbonate was used to select the matrix-matched carbonate reference material for the NanoSIMS instrumental mass-fractionation correction</mark>. The NanoSIMS procedure is being registered (<mark>DOI pending</mark>), and its data are <mark>included in the same submission as this dataset</mark>.

---

### Acknowledgements (funding)

The electron microprobe was funded by <mark>Example Agency award EX-INST-0001</mark>, and development of the analytical procedure by <mark>award EX-DEV-0002</mark>. The analyses reported here were funded by <mark>Example Agency award EX-SCI-0003</mark>.

### Data availability

All point analyses, with their labels, phases, beam conditions and 1σ counting-statistics uncertainties, are given in Supplementary Table S1. The quantitative maps are included in the same data package. The session is recorded as Probe for EPMA run <mark>EML-2026-0412-A</mark> at the Example Microanalysis Laboratory. It followed the registered procedure <mark>doi:10.0000/example.epma-cc.v2</mark>. The coupled NanoSIMS data are <mark>included in the same submission</mark>.

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
