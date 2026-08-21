#!/usr/bin/env python3
"""
Phase 3 (second round) — literature assessment of the 12 fields that are blank in every
literature assessment column of Solution_Q-ICP-MS_TAPP_v22 and Solution_SF-ICP-MS_TAPP_v23.

WHY THESE 12: they postdate the June 2026 Phase 3 extraction. Version history shows them
entering at v6->v7 (Rules 5/8/9 + ReportingCore), v7->v8, v12->v16 (Session Identifier)
and v20->v21 (Instrument Manufacturer split). The papers were read before the fields existed.

SOURCES — every cell below traces to a sentence, table cell or figure caption read from the
source PDF in this session (pdfplumber text dumps of the PDFs in each TAPP's
"Literature assessment" folder). Citation keys used inline:

  Q columns
  [H]  Hu & Gao 2008, Chem. Geol. 253, 205-221  -- PerkinElmer ELAN 6100 DRC, NWU Xi'an
  [Y]  Yu et al. 2005, G-cubed 6, Q08P01        -- PerkinElmer ELAN DRC II, Univ Cambridge
  [M]  Makishima et al. 2011, GGR 35, 57-67     -- Agilent 7500cs, PML Okayama
  [Lo] Long et al. 2025, Nat. Commun. 16, 6146  -- Agilent 7900, IPGP France
  [Lu] Lu et al. 2007, Chem. Geol. 236, 13-26   -- Agilent 7500cs (ICP-QMS), PML Okayama

  SF columns
  [D]  Desem et al. 2022, Appl. Geochem. 143, 105361 -- Nu Attom SC-SF-ICP-MS, Univ Melbourne
  [Li] Li et al. 2016, Microchem. J. 127, 237-246    -- Thermo Element I, IGGCAS Beijing
  [Lu] Lu et al. 2007 (same paper, ICP-SFMS half)   -- Finnigan ELEMENT, PML Okayama
  [Mi] Milne et al. 2010, Anal. Chim. Acta 665, 200-207 -- Thermo Finnigan Element 1, FSU NHMFL
  [Ms] Misra et al. 2014, G-cubed 15, 1617-1628     -- Thermo Element XR, Univ Cambridge
  [W]  Willbold et al. 2005, GGR 29, 63-82          -- ThermoFinnigan ELEMENT2, MPI Mainz

CONVENTIONS (references/lit_assessment.md): N = applicable but not stated; N/A = concept does
not apply; never blank. Values recorded only where directly stated. "Partially" prefixes a cell
where part of what the field asks for is stated and part is not, and says which is missing.
"""
import csv, os

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"

Q_COLS = [
    "Hu+Gao2008 | PerkinElmer ELAN 6100 DRC | NWU Xi'an",
    "Yu+etal2005 | PerkinElmer ELAN DRC II | Univ Cambridge",
    "Makishima+etal2011 | Agilent 7500cs | PML Okayama",
    "Long+etal2025 | Agilent 7900 | IPGP France",
    "Lu+etal2007 | Agilent 7500cs | PML Okayama",
]
SF_COLS = [
    "Desem+etal2022 | Nu Attom SC-SF-ICP-MS | Univ Melbourne",
    "Li+etal2016 | Thermo Element I | IGGCAS Beijing",
    "Lu+etal2007 | Finnigan ELEMENT | PML Okayama",
    "Milne+etal2010 | Thermo Finnigan Element I | FSU NHMFL",
    "Misra+etal2014 | Thermo Element XR | Univ Cambridge",
    "Willbold2005 | ThermoFinnigan ELEMENT2 | MPI Mainz",
]

# ---------------------------------------------------------------- Q-ICP-MS
Q = {
"1. Procedure Identification": ["N"] * 5,
"Session Identifier": [
 'N',
 'N -- "a typical run (~5 hr)" referenced [Y sec 3.2]; no run identifier stated',
 'N -- "an average of eight sessions" referenced [M, Basic performances]; no session identifier stated',
 'N',
 'N',
],
"2. Samples": ["N"] * 5,
"Sample Name": [
 'AGV-1 (andesite), BHVO-1 (basalt), G-2 (granite), SCO-1 (shale), GSR-5 (shale); GSR-6 and "another eighteen international" RMs; worldwide loess and Chinese upper-crustal composites [H Table 2, sec 3.4, Table 1]',
 'Partially -- sample type named ("core top Cibicidoides wuellerstorfi from the north Atlantic Ocean") [Y sec 1]; no individual sample identifiers stated in the methods',
 'JB-2, JB-3, JA-1, JA-2, JA-3, JP-1, BHVO-1, AGV-1, PCC-1, DTS-1; NIST SRM 610, 612, 614, 616 glasses [M, Silicate reference materials]',
 'PCA 02010, B-7904, LON 94101 and further CM/CY chondrites [Lo Fig. 3 caption, Methods]',
 'JB-1, JB-2, JB-3, JA-1, JA-2, JA-3, JP-1 (GSJ); BHVO-1, AGV-1, PCC-1, DTS-1 (USGS); Ivuna (CI1), Orgueil (CI1), Cold Bokkeveld (CM2), Allende (USNM 3529, Split 1, Pos. 23) [Lu sec 2.3]',
],
"Sampling Unit": [
 'Aliquot of rock powder -- "Fifty milligrams of sample powder were placed in a home-made PTFE-lined stainless steel bomb"; final solution made up to 50 ml [H sec 3.3]',
 'Aliquot of dissolved foraminiferal calcite -- "Ten to twenty individual foraminifera tests were handpicked"; cleaned samples "dissolved in 200 ul 0.075M HNO3", then split (20 ul for [Ca] by ICP-AES, remainder for ICP-MS) [Y sec 2]',
 'Test portion / solution aliquot -- "The amount of test portion used was 15-42 mg for basalt and andesite samples, and 30-63 mg for peridotite samples"; NIST glasses "a few grains totalling 8-22 mg were used in one analysis"; "the same sample solution aliquot" [M, Silicate reference materials; Introduction]',
 'N -- no digestion mass or aliquot stated for the elemental (Q-ICP-MS) determination; the "approximately 35 mg of homogenized bulk powder" in Methods belongs to the Zn-isotope MC-ICP-MS procedure',
 'Weighed test portion -- "Approximately 20 mg of basalt and andesite samples were weighed"; "Approximately 50 mg for peridotites and approximately 10 mg for meteorites were weighed"; 9-18 mg for carbonaceous chondrites [Lu sec 2.5, 3.9]',
],
"3. Instrument & Software": ["N"] * 5,
"Instrument Manufacturer": [
 'PerkinElmer -- "a PerkinElmer SCIEX ELAN 6100 DRC ICP-MS" [H sec 3.1]',
 'PerkinElmer -- "a Perkin-Elmer Elan DRC II instrument" [Y sec 2]',
 'Agilent -- "Agilent 7500cs; Yokogawa Analytical Systems, Mitaka, Japan" [M, Instrumentation]',
 'Agilent -- "an Agilent 7900 Quadrupole Inductively Coupled Plasma Mass Spectrometry instrument" [Lo, Methods]',
 'Agilent -- "A Q-pole type ICP mass spectrometer, Agilent 7500 cs (Yokogawa Analytical Systems, Japan)" [Lu sec 2.1, Table 1a]',
],
"4. Measurement Information": ["N"] * 5,
"Analytical Mode": [
 'Solution nebulisation (continuous) -- "A glass microconcentric nebulizer (MCN) and a cyclonic spray chamber comprised the sample introduction system, with a typical sample uptake rate of 0.20 ml/min" [H sec 3.1]',
 'Solution nebulisation (continuous) -- quartz cyclonic spray chamber and "glass micro-concentric nebulizer Micromist FM005 ... producing an uptake rate of ~60 ul/min at a pump rate of 12 rpm"; Cetac ASX100 autosampler [Y sec 2]',
 'Flow injection -- "The pseudo-flow injection (FI) sample introduction technique, in which transient signals were integrated as total counts, was employed with the ID-IS method to minimise total sample consumption volume (~0.013 ml)" [M, Instrumentation]',
 'Solution nebulisation (continuous) -- "The sample was introduced into a Scott spray chamber through a MicroMist nebulizer at an uptake rate of 0.2 mL/min" [Lo, Methods]',
 'Flow injection -- "pseudo-FI" declared as the data acquisition mode [Lu Table 1a]; sec 2.6 "Pseudo-flow injection (FI) method for ICP-QMS", explicitly contrasted with "the continuous sample introduction method"',
],
"Reported Variables and Units": [
 'Forty-eight trace element concentrations (ppm); blanks (ppb) [H Table 2 header]',
 'Element/Ca ratios: Mg/Ca, Sr/Ca, Al/Ca (mmol/mol); Li/Ca, B/Ca, Mn/Ca, Zn/Ca, Cd/Ca (umol/mol); U/Ca (nmol/mol) [Y Table 2 footnote a]',
 'Cd, In, Tl and Bi mass fractions (ng g-1) [M Table 1 "Detection limit in silicates (ng g-1)", Table 3]',
 'Partially -- "The elemental content of samples was analyzed"; concentration unit ug/g attested ("[Zn] = 309 ug/g", "144 ug/g") [Lo, Methods; Fig. 3 caption]; the reported variable list is in Tables S1-S2, not in the paper',
 'B, Ti, Zr, Nb, Mo, Sn, Sb, Hf and Ta mass fractions (ug g-1) [Lu Tables 5-8]; detection limits in solution (pg g-1) and in rock (ng g-1) [Table 2a]',
],
"5. Data Processing": ["N"] * 5,
"Uncertainty Level": [
 'RSD% -- "The RSD is the relative standard deviation in percent"; n = 4-7 per reference material [H Table 2 and footnote]',
 'RSD% -- "RSD% (relative standard deviation) = [SD of measurements/average ratio]*100%" [Y Table 2 footnote b]',
 'RSD% (n = 5) and RPD (relative percentage difference) -- both used; "RPD, relative percentage difference" [M Table 1 footnote, Table 2, Results]',
 'N -- no uncertainty convention stated for the elemental (Q-ICP-MS) data; the "2SD, n = 4" in Methods applies to the delta-66Zn MC-ICP-MS results',
 'RSD% with observed ranges in parentheses [Lu Table 2a and footnote]',
],
"Calibration Factor and Determination Method": [
 'Partially -- "Drift corrections are carried out using Rh as an internal standard and by repeatedly analyzing a calibration solution as a drift monitor over the duration of a run"; "The isotope interferences of 114,115Sn+ on 114Cd+ and 115In+ were calibrated through the measurement of 118Sn+" [H sec 3.1]. No factor value or its uncertainty stated',
 'Correction factor CF for the 40Ar26Mg interference on 66Zn: "In this case, CF is 0.0022"; "Generally, CF values are around ~0.002"; "CF was calculated daily by Ks defined by 0.075M HNO3 and two (one each of Mg and Zn) diluted standards" [Y Fig. 1 caption]. Calibration slopes and intercepts applied to convert intensity ratios to element/Ca ratios [Y sec 3.4]',
 'Relative concentration factors f_G and S_Gi ("the ratio of the concentration in the solution to the signal intensity of the measured isotope") in the ID-IS equation, obtained from calibrator solutions measured before and after the sample; mass discrimination correction "based on the mean elemental ratios obtained from the calibrator solution measurements"; MoO+/Mo+ from a Mo standard run "after every sixth sample" [M, ID-IS method]. No numeric factor values reported',
 'Partially -- "A mixture of certified standards was measured across a range of concentrations to convert count measurements into solution concentrations" [Lo, Methods]. No factor value, determination detail or uncertainty stated',
 'Recovery-yield factors "determined by the calibration curve and the ID methods using ICP-QMS"; Nb and Ta yields "obtained by ID-IS method"; "Errors in the yield determination are estimated to be ~7%; thus >~93% is considered to be the perfect yield" [Lu sec 2.4]',
],
"Procedural Blank Level": [
 'Per-element blanks in ppb with standard deviation, n = 5 (e.g. B 0.39 +/- 0.26; Zn 0.80 +/- 0.56; Pb 0.043 +/- 0.020; V 0.50 +/- 0.38) [H Table 2, "Blank" columns]',
 'Reported as blank contribution relative to typical foraminiferal test ratios: "<1% for Ca, Mg, Sr and Li; higher blanks were observed for Cd (<2%), and U (<5%) ... and for Zn (<4%)"; "The B blank was substantially decreased to ~5% by the employment of a quartz spray chamber, compared with ~30% when using a glass spray chamber" [Y sec 3.2]',
 '"Total dissolution blanks for the ultrasonic bath and bomb digestions were similar at <16 pg for each element (n = 4)"; per-element blanks Cd 16 pg, In <0.2 pg, Tl 4 pg, Bi 3 pg [M Table 1 "Blank (pg)", Silicate reference materials]',
 'N',
 'Blanks in spike solutions (pg g-1) and total procedural blank (pg) tabulated per element [Lu Table 4]; "Blank effects for Ti, Zr, Mo, Hf and Ta from the Ca-Al-Mg solutions and the total procedure were <0.2% and negligible. The blank effects for Sn and Sb ... were 0.4-9% and 0.2-6%" [sec 2.4]; "Blank corrections using the values shown in Table 4 were applied to all analyses. The blank corrections were usually <1% in basalt and andesite analyses and <4% in peridotite reference materials" [sec 3.6]',
],
"Analysis Inclusion and Rejection Criteria": [
 'Partially -- replicate counts stated per reference material (n = 6, 5, 7, 4, 4; blanks n = 5) [H Table 2]. No acceptance or rejection rule, and no acquired-versus-included count, stated',
 'Partially -- number of replicate analyses stated per ratio (n = 120, 88, 32, 70, 50) [Y Table 2]. No acceptance or rejection rule stated',
 'Partially -- n = 5 (evaporation test), n = 4 (dissolution blanks), "an average of eight sessions" for detection limits [M Tables 1-2]. No acceptance or rejection rule stated. 113Cd was excluded as a determination channel -- "113Cd was not used for Cd determination, because the correction of 113In was far larger than the MoO correction" -- which is a channel decision, not an analysis-inclusion decision',
 'N',
 'Partially -- "Orgueil and Allende were analyzed 4 times and twice from the sample digestion, respectively. ... As the sample amounts used were small, and the carbonaceous chondrites are heterogeneous, analytical results for each run are shown in the table" alongside the averages [Lu sec 3.9]. No acceptance or rejection rule stated',
],
"Constants and Reference Values Used": [
 'N',
 'Natural isotopic abundances used to select isotopes and derive correction factors: the Li standard "was artificially depleted of 7Li (92.32% vs 92.48% for natural)"; "The natural abundance of 11B (80.17%) is also different from values of foraminiferal samples which are expected to be 80.40-80.43% if assumed to have d11B ratios of 25-27 permil", giving "correction factors (0.9983 for Li and 0.9968-0.9971 for B)"; 111Cd 12.8%, 112Cd 24.1%, 114Cd 28.7%, 238U 99.3% [Y sec 2, sec 3.1]',
 '"113In/115In = 0.0448 (Rosman and Taylor 1998)" used in the In correction; "For a 94Mo/95Mo value of 0.58" and MoOH+/MoO+ "a value of ~0.15 was obtained", both used in the Mo-oxide correction [M, ID-IS method; Mo oxide correction]',
 'N',
 'Partially -- the ID equation is built on spike and natural isotope ratios, and the mixed standard solution is referenced to the B isotope ratio standard of Makishima et al. (1997) [Lu sec 2.2.4, 2.7]. No constant values or their sources are tabulated',
],
"Goodness-of-Fit or Dispersion Statistic": [
 'N',
 'N for the quantity this field defines. A calibration-curve fit statistic is reported -- "The calibration curves determined from multiple standards are linear and R2 are usually greater than 0.999" [Y sec 3.4] -- which measures the fit of the calibration, not whether scatter among contributing analyses exceeds analytical uncertainty',
 'N',
 'N',
 'N',
],
"6. Quality Control & Uncertainty": ["N"] * 5,
}

# ---------------------------------------------------------------- SF-ICP-MS
SF = {
"1. Procedure Identification": ["N"] * 6,
"Session Identifier": [
 'N -- "A typical session comprised analyses of up to 50 unknowns and 15 standards" [D sec 2.4]; no session identifier stated',
 'N',
 'N',
 'N -- "Each analytical session would begin and end with the analysis of a series of Mo standards (1-100 nM)"; "an analysis sequence"; "1 day\'s analysis"; "three separate days of analyses" [Mi sec 2.4, Tables 4-5]. No session or sequence identifier stated',
 'N -- "a single instrument session" referenced [Ms Fig. 2 caption]; no session identifier stated',
 'N',
],
"2. Samples": ["N"] * 6,
"Sample Name": [
 'Soil and rock samples from boreholes BH1, BH2 (Sunbury), BH3, BH4 (Kalkallo), BH5 (Greenvale), BH6, BH (Wallan), incl. BH3a; reference materials BCR-2, BR, AGV-2, JB-2, JB-3, NIST SRM981, and Broken Hill Main Lode galena [D Fig. 1 caption, Tables 1-2, sec 3.1]',
 'mag_1, mag_3, mag_5, py_2, py_4; iron-formation reference material FER-2 (CCRMP, CANMET MMSL, Canada) [Li Table 4, sec 2.2]',
 'JB-1, JB-2, JB-3, JA-1, JA-2, JA-3, JP-1 (GSJ); BHVO-1, AGV-1, PCC-1, DTS-1 (USGS); Ivuna (CI1), Orgueil (CI1), Cold Bokkeveld (CM2), Allende (USNM 3529, Split 1, Pos. 23) [Lu sec 2.3]',
 'Open-ocean seawater reference materials SAFe S1, SAFe D2 and NASS-5; GEOTRACES inter-calibration samples GS (surface) and GD (deep); depth-profile samples from the BATS station, 31 deg 45\' N, 64 deg 05\' W, 23 June 2008 [Mi Tables 6-7, Fig. 3 caption]',
 'In-house consistency standards CAM-wuellerstorfi, CAM-Uvig-1, CAM-Uvig-2 and CAM-Mix; Globigerinoides sacculifer specimens of the 300-355 um size fraction [Ms sec 2.2, sec 2.4, Fig. 2 caption]',
 'AGV-1, AGV-2, BCR-1, BCR-2, BCR-2G, BIR-1, BIR-1G, BHVO-1, BHVO-2, BHVO-2G, G-2, JR-1, KL2-G, ML3B-G, NIST SRM 612, OU-6, PCC-1 -- tabulated with issuing organisation and split/position numbers (e.g. BHVO-1 Split 15 Pos 26; G-2 Split 58 Pos 23) [W Table 2]',
],
"Sampling Unit": [
 'Weighed split of a digest or leachate -- rock chips 0.05-0.24 g, soils 1-2.3 g; "weighed splits taken for trace element and high-precision Pb isotope analysis by MC-ICPMS. At least 50% of each solution was retained for Pb isotope analysis by SC-SF-ICP-MS and Q-ICP-MS"; "Small splits of the soil samples (TD, AR) were used for Pb isotope analysis on a Nu Instruments Attom" [D sec 2.2, sec 2.4]',
 'Aliquot of the digest solution -- 50 mg FER-2 and "approximately 100 mg of the studied mineral samples" digested; "a small aliquot sample solution was taken for column separation", "7.2 mg Fe in 10% aliquot of magnetite solution"; "A 1.8 g sample solution (in 2 g of 10 M HCl) was weighed and loaded" [Li sec 2.3, sec 3.2]',
 'Weighed test portion -- "Approximately 20 mg of basalt and andesite samples were weighed"; "Approximately 50 mg for peridotites and approximately 10 mg for meteorites"; 9-18 mg for carbonaceous chondrites [Lu sec 2.5, 3.9]',
 '12 mL sub-sample (aliquot) of an acidified seawater sample -- "Acidified seawater samples ... were sub-sampled (12 mL) into clean 30 mL FEP Teflon bottles. The 12 mL aliquots were spiked"; "standard additions ... were added to individual 12 mL sub-samples of the same sample"; "Standard additions of Co and Mn were performed on a further four aliquots (1 mL) of the elution acid" [Mi sec 2.3, sec 3.3]',
 'Dissolved foraminiferal test aliquot -- "capable of analyzing small masses of calcite (5-10 mg), including single foraminifera specimens"; "Leached samples were dissolved in a minimum volume of 1 M HNO3 (40-60 uL) ... centrifuged for 2 min at 10,000 rpm and the supernatant was used for Me/Ca analysis. A 5 uL aliquot ..." [Ms sec 1, sec 2.2]',
 'Digestion, with determinations nested inside it -- "Five independent analyses (different spikings/digestions) of BHVO-1 were carried out over a time period of 4 months. Triplicate determinations were performed for each digestion"; "Only one digestion was prepared for the USGS reference glasses ... and were measured in triplicate" [W, Results]',
],
"3. Instrument & Software": ["N"] * 6,
"Instrument Manufacturer": [
 'Nu Instruments -- "a Nu Instruments Attom SC-SF-ICP-MS" [D sec 2.4]',
 'Thermo Fisher Scientific -- "An Inductively Coupled Sector Plasma Mass Spectrometer (Element I, ThermoFisher, USA)" [Li sec 2.1]',
 'Thermo Fisher Scientific -- "(b) ICP-SFMS, Finnigan ELEMENT" [Lu Table 1b]; stated as "Finnigan ELEMENT", the pre-Thermo brand name',
 'Thermo Fisher Scientific -- "a Thermo-Finnigan Element I (E1) HR-ICP-MS"; "Instrument ThermoFinnigan Element1" [Mi sec 2.4, Table 2]',
 'Thermo Fisher Scientific -- "a Thermo Element XR, a single collector sector field high resolution inductively coupled plasma mass spectrometer" [Ms sec 2.3]',
 'Thermo Fisher Scientific -- "a ThermoFinnigan ELEMENT2 mass spectrometer" [W sec Introduction, Table 3]',
],
"4. Measurement Information": ["N"] * 6,
"Analytical Mode": [
 'Solution nebulisation (continuous) -- "The Attom was operated with a Glass Expansion cyclonic spray chamber and glass nebulizer (uptake rate 0.33 ml/min)"; "both operated in wet plasma mode"; ESI SC-2 DX autosampler [D sec 2.4]',
 'Solution nebulisation (continuous) -- "Sample uptake rate 200 uL min-1" [Li Table 1]; "The components of the sample introduction system: nebulizer, spray chamber, torch, and the cones" [sec 2.1]',
 'Solution nebulisation (continuous) -- stated in the acquisition parameters: "Middle resolution 50 s with 30 scans (continuous nebulization)" [Lu Table 1b]',
 'Solution nebulisation (continuous) -- "Nebuliser PFA microflow (PFA-100), Elemental Scientific"; "Nebuliser sample uptake rate 150 uL min-1"; "Autosampler CETAC ASX-100" [Mi Table 2]. The flow-injection manifold of sec 2.2 is the offline pre-concentration step, not the ICP-MS introduction: "prevented the online coupling of the flow injection system directly to an ICP-MS" [sec 2.3]',
 'Solution nebulisation (continuous) -- "a Teflon Scott type (single pass) spray chamber was constructed"; "we used a platinum injector (1.8 mm I.D.)"; ESI nebulizer [Ms sec 2.3, Tables 1-2]',
 'Solution nebulisation (continuous) -- "The ELEMENT2 was equipped with an ESI microconcentric Teflon nebuliser (flow rate ca. 100 ul min-1) and an ESI Teflon spray chamber"; "Sample uptake rate ca. 100 ul min-1" [W Table 3]',
],
"Reported Variables and Units": [
 '206Pb/204Pb, 207Pb/204Pb, 208Pb/204Pb, 207Pb/206Pb, 208Pb/206Pb -- dimensionless isotope ratios [D Tables 1-2, Fig. 2]',
 'Mass fractions of Li, Be, Sc, Cr, Co, Ni, Cu, Zn, Rb, Sr, Ge, Cs, Ba, Y and the REE [Li Tables 3-4]; detection limits in ng mL-1 [Table 2]. Concentration unit is not stated in the Table 4 header',
 'Ti and Nb mass fractions by ICP-SFMS (ug g-1); TiO2 also reported [Lu Tables 5-8]; detection limits in solution (ng g-1) and in rock (ug g-1) [Table 2b]',
 'Dissolved Mn, Fe, Co, Ni, Cu, Zn, Cd and Pb concentrations in nM [Mi Tables 6-7 and captions, "All concentrations are in nM"]',
 'B/Ca and Me/Ca (Li, Mg, Al, Sr, Cd, Ba, U in low resolution; Na, Mn, Fe, Zn in medium resolution) in umol/mol and mmol/mol [Ms sec 2.3.1, Tables 3-4, Fig. 2]',
 'Trace element mass fractions in ug g-1 -- Eqs (1) and (2) both return "ug g-1"; limits of detection as rock equivalents in ng g-1 [W Eqs 1-2, Fig. 2, Tables 4-5]',
],
"5. Data Processing": ["N"] * 6,
"Uncertainty Level": [
 'Both conventions stated: 2SD for external reproducibility ("(2sd, n = 22)", "%2sd", "n = 9 for JB-2 and n = 11 for JB-3, +/-2sd%") and 2SE for internal precision ("typical internal precision (2se)", "Typical within-run precision (2 standard errors)") [D sec 2.3, sec 2.4, Tables 1-2]',
 '1 standard deviation -- "The mean values and respective standard deviations (s) for three analyses"; "Mean +/- s (n = 3)"; "RSD = standard deviation/mean x 100%" [Li sec 3.3, Table 4]',
 'RSD% with observed ranges in parentheses [Lu Table 2b and footnote]',
 'Mixed and each stated: "Mean blank +/- 1 S.D. (pmoles)" [Mi Table 5]; "The precision is calculated as the percent relative standard deviation (%RSD) (n = 3)" [Table 4 footnote]; "95% confidence limit" [Table 6 caption]',
 '2 sigma -- "with 2r analytical uncertainty" and "the gray area represents the 2r spread in the B/Ca measured at 10 ppm [Ca]Matrix" (r = sigma in the extracted text) [Ms Fig. 2 caption, Fig. 5 caption]',
 'RSD for repeatability of triplicate determinations [W Tables 4-5]; "confidence intervals (1s)"; the method result is quoted as a "combined standard uncertainty" [W Abstract, sec Accuracy and reproducibility]',
],
"Calibration Factor and Determination Method": [
 'Instrumental mass-fractionation factor: "Raw Pb isotope ratios were corrected for instrumental mass fractionation using the measured 205Tl/203Tl and Pb mass bias factors derived from Pb vs Tl isotope mass bias plots generated from numerous analyses of SRM981"; "Pb mass bias factors were taken from master Pb-Tl mass bias correlation lines" [D sec 2.4, sec 2.3]. The magnitude "ca. 0.7% per mass unit" is stated for the MC-ICP-MS, not for the SC-SF-ICP-MS',
 'Partially -- "Calibration External" against multi-element standards at 0.1, 1, 5 and 10 ng mL-1 with 103Rh internal standard held at 5 ng mL-1 in sample, calibration and blank solutions [Li Table 1, sec 2.2]. No calibration factor value or uncertainty stated',
 'Recovery-yield factors "determined by the calibration curve and the ID methods"; "The Ti yield was determined from the TTi/Nb ratio by ICP-SFMS"; "Errors in the yield determination are estimated to be ~7%" [Lu sec 2.4]',
 'Mass-bias correction factor per element: "A mass bias correction factor for each of the six elements was calculated from the measured natural isotopic ratio divided by the true natural isotopic ratio. The correction factor for each element was then incorporated into the isotope dilution equation"; Co and Mn quantified from standard-addition slopes, tabulated with SD and %RSD (Mn 2797 +/- 205, 3055 +/- 125, 3174 +/- 170; Co 6124 +/- 305, 4335 +/- 143, 5352 +/- 159) [Mi sec 2.5, Table 4]',
 'Partially -- "Me/Ca determinations by Element XR were carried out using a set of external calibration standards"; "Samples and standards were concentration matched within +/-5%" [Ms sec 2.3.1]. No calibration factor value or uncertainty stated',
 'Relative sensitivity factors (RSF) appear explicitly in Eq. (2) for mono-isotopic elements; in-run mass-fractionation factors fitted with a power law MF = a x b^(m-c) + d, "Typical values are a: 0.08 to 0.23, b: 0.96 to 0.98, c: -10 to 10 and d: -0.005 to 0.005"; spike concentrations "calibrated by applying a reverse ID against certified standard solutions (Alfa Aesar, specpure) using TIMS, MC-ICP-MS and SF-ICP-MS", and "The uncertainty of spike concentrations has been estimated to 0.5-1% RSD" [W Eqs 2-4, sec Relative sensitivity factors]',
],
"Procedural Blank Level": [
 '"Typical column blanks were <20 pg Pb, while total procedural blanks (dissolution and/or leaching, including centrifuging) are estimated to be <100 pg"; "sample/blank ratios were >=1500, rendering blank corrections negligible" [D sec 2.3]. Per-acquisition instrumental blank on the Attom: "Each sample acquisition was preceded by a blank determination (average 900cps on 208Pb, equivalent to 1.8 ppt Pb in solution)" [sec 2.4]',
 '"The concentration of elements in the procedural blank ranged from 0.004 ng mL-1 (Cs) to 0.216 ng mL-1 (Zn)"; "the highest blank level in Zn would contribute less than 0.01% of the amount of analyte" [Li sec 3.3]',
 'Blanks in spike solutions (pg g-1) and total procedural blank (pg) tabulated per element [Lu Table 4]; "The blank corrections were usually <1% in basalt and andesite analyses and <4% in peridotite reference materials"; "Total Sn blank levels are ~300 pg in both the ultrasonic and the bomb methods" [sec 3.6]',
 'Per-element reagent blank with 1 S.D. in pmoles, broken down into elution acid and ammonium acetate buffer contributions (Mn 0.433 +/- 0.026; Fe 2.791 +/- 0.083; Co 0.078 +/- 0.006; Ni 0.457 +/- 0.104; Cu 0.184 +/- 0.027; Zn 3.044 +/- 0.018; Cd 0.045 +/- 0.003; Pb 0.017 +/- 0.001) [Mi Table 5]',
 '"Our procedural B/Ca blank of 2.0 +/- 1.0 umol/mol" [Ms Abstract]; instrumental 11B blank in cps tabulated against spray chamber material, injector material and acid matrix (2011-19,750 cps) [Table 2]',
 'Partially -- "Limits of detection (LOD) were calculated according to the 3s criterion on a data set of fifty measurements in LR mode and twenty measurements in HR mode of total procedural blanks (including spiking)"; LODs "ranged between about 0.1 and 10 ng g-1 sample equivalents for most elements" [W sec Limits of detection]. The blank levels themselves are not tabulated',
],
"Analysis Inclusion and Rejection Criteria": [
 'Partially -- n stated per averaged result (BCR-2 n = 39, AGV-2 n = 13, BR n = 11, JB-2 n = 9, JB-3 n = 11, SRM981 n = 22 and n = 16) [D Tables 1-2]. One documented exclusion, from the quality assessment rather than from a reported aggregate: "Results for the pure Pb standard NIST SRM981, analysed many times with the soil samples, are not included here, because it contains no matrix and may thus not a be a good indicator of data quality for the soil samples analysed here" [sec 3.1]. No acceptance or rejection rule, and no acquired-versus-included count, stated',
 'Partially -- "The mean values and respective standard deviations (s) for three analyses were listed in Table 3"; n = 3 throughout [Li sec 3.3, Tables 3-4]. No acceptance or rejection rule stated',
 'Partially -- "Orgueil and Allende were analyzed 4 times and twice from the sample digestion, respectively ... analytical results for each run are shown in the table" alongside the averages [Lu sec 3.9]. No acceptance or rejection rule stated',
 'Partially -- "The blank solutions were analysed at least three times on the ICP-MS"; "parallel triplicate samples"; n = 3 for reference materials and n = 5 for the GEOTRACES samples [Mi sec 3.3, sec 3.4, Tables 6-7]. No acceptance or rejection rule stated',
 'Partially -- "Open symbols represent an average of 10 measurements acquired during a single instrument session. The solid symbols represent the average of the open symbols"; and for a second figure "which is a total of 15 measurements"; acquisition structured as 3 runs x 15 passes (low resolution) or 3 x 5 (medium) [Ms Fig. 2 caption, Fig. 5 caption, Table 3]. No acceptance or rejection rule stated',
 'Partially, and the most complete of the six -- "Five independent analyses (different spikings/digestions) of BHVO-1 were carried out over a time period of 4 months. Triplicate determinations were performed for each digestion"; "the results of three to four independent analyses of sixteen other RMs"; "Only one digestion was prepared for the USGS reference glasses BCR-2G, BHVO-2G and BIR-1G, and NIST SRM 612 respectively and were measured in triplicate" [W, Results]. No acceptance or rejection rule stated',
],
"Constants and Reference Values Used": [
 '205Tl/203Tl = 2.3871 (Woodhead 2002), used to correct instrumental mass fractionation by internal normalisation with the exponential law [D sec 2.3, sec 2.4]',
 'N',
 'Partially -- the ID equation is built on spike and natural isotope ratios, and the mixed standard solution is referenced to the B isotope ratio standard of Makishima et al. (1997) [Lu sec 2.2.4, 2.7]. No constant values or their sources are tabulated',
 'Partially -- "A mass bias correction factor for each of the six elements was calculated from the measured natural isotopic ratio divided by the true natural isotopic ratio" [Mi sec 2.5]. The true natural isotopic ratios used, and their source, are not stated',
 'N',
 'Relative atomic masses M_El and M_S "(Loss 2003)"; "the known natural isotopic abundances of the isotopes i and k in the sample (Rosman and Taylor 1998)", stated to be adequately known ("uncertainty < 0.2%"); in-run mass fractionation determined "by comparing determined 47Ti/49Ti, 99Ru/101Ru (in LR mode), 151Eu/153Eu (in HR mode) and 185Re/187Re ratios with known values (Rosman and Taylor 1998)". For Pb the paper compares two reference choices -- "average Pb isotope abundances (Rosman and Taylor 1998)" versus the BHVO-1 TIMS composition of "Woodhead and Hergt 2000" -- and quantifies the consequence: "The difference between both approaches is 0.4% (concentration of Pb: 2.13 ug g-1 versus 2.14 ug g-1)" [W Eqs 1-3, sec Relative sensitivity factors]',
],
"Goodness-of-Fit or Dispersion Statistic": [
 'N for the quantity this field defines. A regression statistic is reported for the measured-versus-nominal comparison -- "The data distributions around the nominal compositions (Fig. 2) have slopes near 1 (with correlation coefficients of 0.75-0.85)" [D sec 3.1] -- which is not a test of whether scatter among contributing analyses exceeds analytical uncertainty',
 'N',
 'N',
 'N -- standard-addition regressions are reported with average slope, SD and %RSD, but no fit statistic [Mi Table 4, Fig. 2]',
 'N',
 'N -- a power law is fitted to the calculated mass fractionation factors, but no fit statistic is reported [W Fig. 1, Eq. 4]',
],
"6. Quality Control & Uncertainty": ["N"] * 6,
}

ORDER = [
 "1. Procedure Identification", "Session Identifier", "",
 "2. Samples", "Sample Name", "Sampling Unit", "",
 "3. Instrument & Software", "Instrument Manufacturer", "",
 "4. Measurement Information", "Analytical Mode", "Reported Variables and Units", "",
 "5. Data Processing", "Uncertainty Level", "Calibration Factor and Determination Method",
 "Procedural Blank Level", "Analysis Inclusion and Rejection Criteria",
 "Constants and Reference Values Used", "",
 "6. Quality Control & Uncertainty", "Goodness-of-Fit or Dispersion Statistic",
]

def write(path, cols, data):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Metadata Item"] + cols)
        for item in ORDER:
            if item == "":
                w.writerow([""] * (len(cols) + 1))
            else:
                w.writerow([item] + data[item])
    print(f"wrote {path}")

write(os.path.join(ROOT, "Solution Q-ICP-MS",
      "Solution_Q-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv"), Q_COLS, Q)
write(os.path.join(ROOT, "Solution SF-ICP-MS",
      "Solution_SF-ICP-MS_lit_assessment_draft_newfields_2026-08-14.csv"), SF_COLS, SF)

# ---- attestation tally -------------------------------------------------
FIELDS = [i for i in ORDER if i and not i[0].isdigit()]
print(f"\n{'field':44} {'Q (n=5)':>10} {'SF (n=6)':>10}  {'total':>7}")
tot_a = tot_p = tot_n = 0
for fld in FIELDS:
    row = []
    for data, n in ((Q, 5), (SF, 6)):
        a = p = 0
        for c in data[fld]:
            if c.startswith("N/A"): pass
            elif c.startswith("Partially"): p += 1
            elif c.startswith("N -") or c == "N" or c.startswith("N for"): pass
            else: a += 1
        row.append((a, p, n))
    (qa, qp, _), (sa, sp, _) = row
    tot_a += qa + sa; tot_p += qp + sp; tot_n += 11 - qa - sa - qp - sp
    print(f"{fld:44} {f'{qa}+{qp}p/5':>10} {f'{sa}+{sp}p/6':>10}  {f'{qa+sa}+{qp+sp}p/11':>7}")
print(f"\nTOTAL cells: attested {tot_a}, partial {tot_p}, N {tot_n}  (of {len(FIELDS)*11})")
