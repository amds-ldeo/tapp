"""
Example values for the reviewer workbook, one per EPMA TAPP field.

Source: the highlighted spans of EPMA_Reference_Methods_Section_v77_highlighted.md — the
worked example. Labels simplified 2026-10-26 so a reviewer can follow them row by row: samples
CC-1 and CC-2 (were EX-CC-01/02); points named by mineral and number, ol3 = the third olivine
point (were particle-point labels, P1-03); maps Map 1 and Map 2; catalogue numbers dropped from
standard names; Target Material lists only the minerals analysed. Values are unchanged.
The v86 methods section carries the same labels (RELABEL in make_highlighted_methods.py). Everything here is fictional (lab, samples, identifiers, results), as the
worked example states. Table 1 content is rewritten as phrases ("X for Y; ..."). Nothing
is added that the worked example does not say.

A value is either a string (the same in every mode) or a dict. Dict keys, most specific
first: a mode name, then 'point' / 'map', then 'eds' / 'wds', then 'all'. 'all' is
required and is what the all-modes workbook shows. Per-mode values only filter the worked
example to the elements, units and conditions that mode uses.
"""

MODES = ('EDS Point Analysis', 'EDS Mapping', 'WDS Point Analysis', 'WDS Mapping')
_KIND = {'EDS Point Analysis': ('point', 'eds'), 'EDS Mapping': ('map', 'eds'),
         'WDS Point Analysis': ('point', 'wds'), 'WDS Mapping': ('map', 'wds')}

_WDS_PT = 'Ti, Al, Cr, Mn, Na, K, P, F, Cl, Ni, Co'
_EDS = 'Si, Mg, Fe, Ca, S'
_WDS_MAP = 'Na, Al, P, Cr, Ni'

EXAMPLES = {
 # ---- 1. Procedure identification
 'Procedure Name': 'EPMA-CC v2: major and minor elements in carbonaceous-chondrite minerals by WDS and EDS',
 'Technique': 'EPMA-WDS+EDS (combines wavelength-dispersive and energy-dispersive spectrometry)',
 'Procedure Author': 'Example Microanalysis Laboratory',
 'Laboratory': 'Example Microanalysis Laboratory',
 'Laboratory ID': 'https://ror.org/0example00',
 'Procedure Start Date': 'January 2025',
 'Funding Source for Procedure Development': 'Example Agency grant A (instrument); grant B (procedure development)',
 'Procedure Reference(s)': 'Example et al. (2025)',
 'Procedure DOI': 'doi:10.0000/epma-cc.v2',
 'Session Identifier': 'Run 2026-04-12',
 'Analyst': 'Analyst A (ORCID 0000-0000-0000-0000)',
 'Analysis Start Date': '2026-04-12',
 'Analysis End Date': '2026-04-14',
 'Funding Source for Analysis': 'Example Agency grant C',
 'Coupled Technique(s)': 'SEM; NanoSIMS (oxygen isotopes of carbonates, Example Isotope Laboratory)',
 'Coupling Description': 'EPMA carbonate compositions select the matrix-matched reference material for the NanoSIMS mass-fractionation correction; SEM first, EPMA next (non-destructive), NanoSIMS last (sputtering destroys the analysed volume)',
 'Coupled Procedure DOI': 'pending',
 'Coupled Dataset or Publication Reference': 'same submission',
 # ---- 2. Samples
 'Target Material': 'Silicate mineral (olivine, pyroxene); oxide (magnetite); sulfide (pyrrhotite); phosphate (apatite); carbonate (dolomite, calcite)',
 'Sample Preparation Method': 'Epoxy mount, dry-polished with diamond to 0.25 µm, carbon coated to 20 nm, for CC-1; the same, plus Ar-ion polishing after the final diamond step, for CC-2',
 'Sample Name': 'CC-1; CC-2',
 'Sampling Unit Type': {
     'all': 'Analysis point, labelled by mineral and number (ol3 = the third olivine point); each X-ray map is one result for its mapped area',
     'point': 'Analysis point (one point analysis = one result), labelled by mineral and number (ol3 = the third olivine point)',
     'map': 'Map area (one map = one result; pixels are not reported individually)'},
 'Sampling Unit Name': {
     'all': 'CC-1: ol1–ol8, px1–px4, mag1–mag6, po1–po5, ap1–ap6 (29 points); CC-2: dol1–dol10, cal1–cal6, ol1–ol8 (24 points); Map 1 in CC-1, Map 2 in CC-2',
     'point': 'CC-1: ol1–ol8, px1–px4, mag1–mag6, po1–po5, ap1–ap6 (29 points); CC-2: dol1–dol10, cal1–cal6, ol1–ol8 (24 points)',
     'map': 'Map 1 in CC-1; Map 2 in CC-2'},
 'Target Material of Sampling Unit': 'CC-1: silicate mineral for ol1–ol8 and px1–px4; oxide for mag1–mag6; sulfide for po1–po5; phosphate for ap1–ap6. CC-2: carbonate for dol1–dol10 and cal1–cal6; silicate mineral for ol1–ol8',
 'Sample Persistent Identifier': 'IGSN:EX0001 for CC-1; IGSN:EX0002 for CC-2',
 'Sampling Unit Selection Criteria': {
     'all': 'Grains at least 5 µm across (10 µm for phosphates and carbonates); at least 3 µm from boundaries, cracks and inclusions in BSE (5 µm for defocused or rastered beams); phase confirmed from its EDS spectrum first; map areas include every target phase in a particle',
     'point': 'Grains at least 5 µm across (10 µm for phosphates and carbonates); at least 3 µm from boundaries, cracks and inclusions in BSE (5 µm for defocused or rastered beams); phase confirmed from its EDS spectrum first',
     'map': 'Map areas chosen to include every target phase present in a particle'},
 'Pre-Analysis Imaging and Screening': 'BSE imaging and EDS maps (Mg, Si, Fe, Ca, S, P) on a field-emission SEM at 15 kV and 1 nA, registered to stage coordinates, each point labelled on its BSE image — for both CC-1 and CC-2',
 # ---- 3. Instrument & software
 'Instrument Manufacturer': 'JEOL',
 'Instrument Model': 'JXA-8530F Plus',
 'Electron Source': 'Schottky field-emission',
 'Acquisition Software': 'Probe for EPMA v13 (Probe Software)',
 'Data Processing Software(s)': {
     'all': 'Probe for EPMA v13 (point quantification); CalcImage v13 (quantitative maps); XMapTools 4 (phase classification of maps)',
     'point': 'Probe for EPMA v13',
     'map': 'CalcImage v13 (quantitative maps); XMapTools 4 (phase classification)'},
 'WDS Spectrometer Configuration': 'Five JEOL spectrometers: LDE1/TAP (Sp1); TAP/PETJ (Sp2); PETJ/LIF (Sp3); PETH/LIFH (Sp4); LIF/PETL (Sp5)',
 'EDS Detector Configuration': 'Integrated silicon drift detector: 30 mm² active area, ultra-thin polymer window, 40° take-off angle',
 # ---- 4. Measurement information
 'Analytical Mode': 'EDS point analysis; EDS mapping; WDS point analysis; WDS mapping',
 'Beam Mode': 'Focused for silicate minerals, oxides and sulfides; defocused for phosphates; rastered for carbonates',
 'Beam Current': '20 nA for silicate minerals, oxides and sulfides; 8 nA for phosphates; 4 nA for carbonates',
 'Beam Diameter': '1 µm (focused) for silicate minerals, oxides and sulfides; 5 µm (defocused) for phosphates; focused within the raster for carbonates',
 'Beam Raster Dimensions': '5 × 5 µm for carbonates',
 'Beam Damage Minimization': {
     'all': 'Defocused beam for phosphates; rastered beam for carbonates; Na, K, F and Cl measured in the first acquisition pass on every point',
     'EDS Point Analysis': 'Defocused beam for phosphates; rastered beam for carbonates'},
 'Mapping Beam Mode': 'Focused, for Map 1 and Map 2',
 'Mapping Beam Current': '50 nA, for Map 1 and Map 2',
 'Mapping Beam Diameter': '1 µm (focused), for Map 1 and Map 2',
 'Accelerating Voltage': '15 kV (the laboratory\'s standard operating voltage)',
 'Drift Correction': 'Beam current measured with the Faraday cup before each point and at the start of each map line, intensities normalised to it; primary standards re-measured at the start and end of the session, drift interpolated linearly with time',
 'Target Species': 'Si, Ti, Al, Cr, Fe, Mn, Mg, Ca, Na, K, P, S, F, Cl, Ni, Co, O, C (18 elements)',
 'Monitored Elements': {
     'all': '%s (EDS); %s (WDS); Zn (WDS, only to correct Zn Lα on Na Kα)' % (_EDS, _WDS_PT),
     'eds': _EDS,
     'WDS Point Analysis': '%s; Zn (only to correct Zn Lα on Na Kα)' % _WDS_PT,
     'WDS Mapping': _WDS_MAP},
 'Reported Variables and Units': {
     'all': 'SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO, CoO in wt%; S, F, Cl in wt%; O equivalent of F and Cl; CO₂ by stoichiometry; totals; structural formulas in apfu; element maps in wt% per pixel; phase map; modal abundance in area %',
     'point': 'SiO₂, TiO₂, Al₂O₃, Cr₂O₃, FeO (total Fe), MnO, MgO, CaO, Na₂O, K₂O, P₂O₅, NiO, CoO in wt%; S, F, Cl in wt%; O equivalent of F and Cl; CO₂ by stoichiometry (carbonates); totals; structural formulas in apfu',
     'map': 'Element concentrations in wt% per pixel; phase map; modal abundances in area %'},
 'X-ray Detection Method per Monitored Element': {
     'all': 'EDS for %s; WDS for %s and for Zn (interference monitor)' % (_EDS, _WDS_PT),
     'eds': 'EDS for %s' % _EDS,
     'WDS Point Analysis': 'WDS for %s and for Zn (interference monitor)' % _WDS_PT,
     'WDS Mapping': 'WDS for %s' % _WDS_MAP},
 'X-ray Line': {
     'all': 'Kα for every monitored element',
     'eds': 'Kα for %s' % _EDS,
     'WDS Point Analysis': 'Kα for every WDS element, including Zn',
     'WDS Mapping': 'Kα for %s' % _WDS_MAP},
 'Diffracting Crystal': {
     'all': 'LDE1 for F; TAP for Na, Al; PETJ for K, P, Ti; PETH for Cl; LIF for Zn, Mn, Co; LIFH for Cr; LIFH + LIF for Ni',
     'WDS Mapping': 'TAP for Na, Al; PETJ for P; LIFH for Cr; LIF for Ni'},
 'WDS Spectrometer Channel': {
     'all': 'Sp1 for F, Al; Sp2 for Na, P; Sp3 for K, Ti, Co; Sp4 for Cl, Cr; Sp5 for Zn, Mn; Sp4 + Sp5 for Ni (intensities aggregated)',
     'WDS Mapping': 'Sp1 for Al; Sp2 for Na; Sp3 for P; Sp4 for Cr; Sp5 for Ni'},
 'Sequence': 'Pass 1 for F, Na, K, Cl, Zn; pass 2 for Al, P, Ti, Cr, Mn; pass 3 for Co, Ni',
 'Proportional Counter / Detector': {
     'all': 'Low-pressure P10 gas-flow counter for Sp1 and Sp2 (F, Al, Na, P); sealed Xe counter for Sp3–Sp5 (K, Ti, Co, Cl, Cr, Zn, Mn, Ni)',
     'WDS Mapping': 'Low-pressure P10 gas-flow counter for Al, Na; sealed Xe counter for P, Cr, Ni'},
 'WDS PHA Setting': {
     'all': 'Differential for F, Na; integral for all other elements',
     'WDS Mapping': 'Differential for Na; integral for Al, P, Cr, Ni'},
 'Peak Counting Time': '20 s for F, Cl, Al, P; 10 s for Na, K, Zn; 30 s for Ti, Cr, Mn; 60 s for Co, Ni (40 s in the registered procedure)',
 'Background Counting Time': '20 s for F, Cl, Al, P; 10 s for Na, K, Zn; 30 s for Ti, Cr, Mn; 60 s for Co, Ni (total of both positions)',
 'Background Position(s)': '−3.2 / +4.5 mm for F; −4.0 / +4.0 mm for Na, P; −4.5 / +4.5 mm for K; −3.0 / +3.0 mm for Cl, Cr, Ni; −3.5 / +3.5 mm for Zn, Al, Mn; −5.0 / +5.0 mm for Ti; −2.5 / +3.5 mm for Co',
 'EDS Live Time per Point or Pixel': '30 s per point',
 'EDS Acquisition Mode': 'Point spectra; spectrum images (full spectrum at every pixel); no line scans',
 'Dwell Time per Pixel': {
     'all': '30 ms per pixel for Na, Al, P, Cr, Ni (WDS) and for the EDS spectrum image',
     'EDS Mapping': '30 ms per pixel (EDS spectrum image, one live time for Si, Mg, Fe, Ca, S)',
     'WDS Mapping': '30 ms per pixel for Na, Al, P, Cr, Ni'},
 'Step Size / Pixel Size': '2 µm in both X and Y',
 'Map Dimensions': '512 × 512 pixels for Map 1; 384 × 256 pixels for Map 2',
 'Map Area': '1.024 × 1.024 mm for Map 1; 0.768 × 0.512 mm for Map 2',
 'Stage Scan vs. Beam Scan': 'Stage scan with the beam held fixed',
 # ---- 5. Data processing
 'Matrix Correction Method': {
     'all': 'Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995) in Probe for EPMA; applied pixel by pixel in CalcImage for maps',
     'point': 'Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995) in Probe for EPMA',
     'map': 'Armstrong/Love–Scott φ(ρz) matrix correction (Armstrong 1995), applied pixel by pixel in CalcImage'},
 'Mass Absorption Coefficients (MACs)': 'FFAST (Chantler et al. 2005)',
 'X-ray Background Correction Method': {
     'all': 'Removed by filter fitting for Si, Mg, Fe, Ca, S (EDS); two-point off-peak, linear for WDS elements in points, exponential for F; MAN calibration (Donovan and Tingle 1996) for WDS maps',
     'eds': 'Removed by filter fitting for %s' % _EDS,
     'WDS Point Analysis': 'Two-point off-peak, interpolated linearly for all WDS elements except F; exponential fit for F',
     'WDS Mapping': 'Mean-atomic-number (MAN) calibration (Donovan and Tingle 1996) for %s' % _WDS_MAP},
 'Time-Dependent Intensity Correction': 'Linear for Na; exponential for F (in apatite); none for other elements',
 'Target Species Estimation Method': 'Directly from measured intensities for every measured element; by stoichiometry from cation valences for O; as CO₂ by stoichiometry for C (carbonates only); OH in apatite by difference, F + Cl + OH = 1 apfu (Ketcham 2015)',
 'Halogen Correction on Oxygen': 'Oxygen equivalent of F and Cl subtracted from the total (apatite)',
 'WDS Dead Time Correction': 'Logarithmic expression; spectrometer-specific constants of 1.1–1.5 µs',
 'EDS Spectral Processing Type': 'Filter fitting: a top-hat filter followed by least-squares fitting to measured standard spectra',
 'Blank Correction': 'Apparent concentration measured on Ni- and Co-free synthetic forsterite subtracted, for Ni and Co; none for other elements',
 'Normalization / Standards-Based Correction': {
     'all': 'Structural formulas normalised to a fixed anion basis: 4 O for olivine and spinels, 6 O for pyroxene and dolomite, 3 O for calcite, 13 anions for apatite (Ketcham 2015); none for other reported variables',
     'map': 'None'},
 'Calibration Factor and Determination Method': 'None, for every reported variable (concentrations from k-ratios against the primary standards)',
 'Procedural Blank Level': '35 ± 9 µg/g for Ni; 22 ± 8 µg/g for Co (n = 5)',
 'Analysis Inclusion and Rejection Criteria': {
     'all': 'Totals 98.5–101.5 wt% (silicates, oxides, sulfides), 96.0–101.5 (apatite), 98.0–102.0 (carbonates); cation sum within ±0.03 apfu; points overlapping a second phase rejected; points with beam drift above 1% rejected',
     'map': 'None: maps are not combined'},
 'Combination Method': {
     'all': 'Arithmetic mean of the included points, per phase within each sample, for every oxide and element concentration; maps and structural formulas not combined',
     'map': 'Not combined: maps are reported pixel by pixel'},
 'Constants and Reference Values Used': 'IUPAC 2021 standard atomic weights (Prohaska et al. 2022)',
 # ---- 6. Quality control & uncertainty
 'Primary Calibration Standard Name': {
     'all': 'Springwater olivine for Si, Mg; Rockport fayalite for Fe; diopside for Ca; dolomite for Ca, Mg in carbonates; synthetic FeS for S; synthetic SrF₂ for F; Amelia albite for Na; microcline for K; scapolite for Cl; anorthite for Al; Wilberforce fluorapatite for P; ilmenite for Ti; synthetic Cr₂O₃ for Cr; rhodonite for Mn; Co metal for Co; Ni metal for Ni; synthetic ZnS for Zn (Smithsonian values: Jarosewich et al. 1980)',
     'eds': 'Springwater olivine for Si, Mg; Rockport fayalite for Fe; diopside for Ca; dolomite for Ca, Mg in carbonates; synthetic FeS for S (Smithsonian values: Jarosewich et al. 1980)',
     'WDS Point Analysis': 'Synthetic SrF₂ for F; Amelia albite for Na; microcline for K; scapolite for Cl; anorthite for Al; Wilberforce fluorapatite for P; ilmenite for Ti; synthetic Cr₂O₃ for Cr; rhodonite for Mn; Co metal for Co; Ni metal for Ni; synthetic ZnS for Zn (Smithsonian values: Jarosewich et al. 1980)',
     'WDS Mapping': 'Amelia albite for Na; anorthite for Al; Wilberforce fluorapatite for P; synthetic Cr₂O₃ for Cr; Ni metal for Ni'},
 'Secondary Reference Materials': 'San Carlos olivine; Kakanui augite; Durango apatite; chromite; calcite (accepted values: Jarosewich et al. 1980)',
 'X-ray Line Overlap Corrections Applied': {
     'all': 'Yes for Co (Fe Kβ on Co Kα), Mn (Cr Kβ on Mn Kα) and Na (Zn Lα on Na Kα), quantitative and iterated with the matrix correction; no for all other elements',
     'eds': 'No for %s' % _EDS,
     'WDS Mapping': 'Yes for Na (Zn Lα on Na Kα); no for Al, P, Cr, Ni'},
 'Interfering Elements': {
     'all': 'Fe for Co; Cr for Mn; Zn for Na',
     'eds': 'None',
     'WDS Mapping': 'Zn for Na'},
 'Interference Correction Standard': {
     'all': 'Co-free Rockport fayalite for Co; Mn-free synthetic Cr₂O₃ for Mn; Na-free synthetic ZnS for Na',
     'eds': 'None required',
     'WDS Mapping': 'Na-free synthetic ZnS for Na'},
 'Detection Limit': {
     'all': 'Points (wt%): 0.11 SiO₂, 0.09 MgO, 0.14 FeO, 0.10 CaO, 0.08 S (EDS); 0.055 F, 0.018 Na₂O, 0.009 K₂O, 0.010 Cl, 0.012 Al₂O₃, 0.020 P₂O₅, 0.015 TiO₂, 0.018 Cr₂O₃, 0.016 MnO, 0.010 CoO, 0.008 NiO (WDS). Maps: about 0.3 wt% per pixel (WDS), 0.7 wt% (EDS)',
     'EDS Point Analysis': '0.11 wt% for SiO₂; 0.09 for MgO; 0.14 for FeO; 0.10 for CaO; 0.08 for S',
     'WDS Point Analysis': '0.055 wt% for F; 0.018 for Na₂O; 0.009 for K₂O; 0.010 for Cl; 0.012 for Al₂O₃; 0.020 for P₂O₅; 0.015 for TiO₂; 0.018 for Cr₂O₃; 0.016 for MnO; 0.010 for CoO; 0.008 for NiO',
     'EDS Mapping': 'About 0.7 wt% per pixel for the EDS elements',
     'WDS Mapping': 'About 0.3 wt% per pixel for the WDS elements'},
 'Detection Limit Method': '3σ of the background counts, for every reported variable',
 'Analytical Precision': '0.4–0.7% for oxides above 10 wt%; 0.9–1.6% for FeO and Al₂O₃; 2–4% for TiO₂, Na₂O, F and Cl; 4% for NiO in San Carlos olivine (1σ RSD; San Carlos olivine n = 9, Kakanui augite n = 6, Durango apatite n = 6, chromite n = 5, calcite n = 6)',
 'Analytical Accuracy': 'Within ±1.2% relative for all major oxides; within ±2.6% for minor oxides and halogens',
 'Counting Statistics Error': {
     'all': '1σ from counting statistics on the peak and on any subtracted background or blank, for every analysis and every reported variable; in olivine about 0.5% relative for SiO₂ and MgO, about 10% for NiO at 0.03 wt%',
     'EDS Point Analysis': '1σ from counting statistics on the peak and background, for every analysis and every reported variable; about 0.5% relative for SiO₂ and MgO in olivine',
     'WDS Point Analysis': '1σ from counting statistics on the peak and on any subtracted background or blank, for every analysis and every reported variable; about 10% relative for NiO at 0.03 wt% in olivine'},
 'EDS Dead Time': {
     'all': '18–26% during point analysis; 24–31% during spectrum imaging',
     'EDS Point Analysis': '18–26%',
     'EDS Mapping': '24–31% during spectrum imaging'},
 'Goodness-of-Fit or Dispersion Statistic': 'MSWD of the included points about the mean, for every oxide and element concentration; none for structural formulas, which are not combined',
 'Additional Notes': 'Part of CC-2 was plucked during ion polishing; its olivine points (ol1–ol8) lie on the remaining fragment. No other anomalies, instrument modifications or departures',
}


def example(name, mode=None):
    v = EXAMPLES[name]
    if isinstance(v, str):
        return v
    if 'all' not in v:
        raise KeyError('no "all" example for %s' % name)
    if mode is None:
        return v['all']
    for k in (mode,) + _KIND[mode]:
        if k in v:
            return v[k]
    return v['all']
