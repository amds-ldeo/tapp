#!/usr/bin/env python3
"""Aggregation fields: literature pass on the Module_Aggregation TAPPs not yet assessed (2026-09-29).

    python3 "Project Files/Scripts/aggregation_fields_20260929.py" [--apply] [--show]

Task 3 of the 2026-09-28 gaps plan. Gap 3 added `Combination Method`, `Combined Results` and `Other
Statistics`, and re-keyed the dispersion statistic, in 13 TAPPs; EPMA and the SEM TAPPs are done. This pass
reads the papers behind the other nine (LA-MC, LA-Q, LA-Q U-Pb, LA-SF, LA-SF U-Pb, Solution MC, Solution Q,
Solution SF, TEM: 78 procedure columns) and fills those fields, plus the dispersion statistic where blank.
The old `Age Model` cells were checked first: they were blank before gap 3, so nothing was lost in the move.

Conventions, as in EPMA:
  * A standard deviation or RSD reported with a mean is the dispersion statistic; a 95% confidence
    interval, a standard error or a 2 sdm is an Other Statistic.
  * `Not combined` only where the paper says so (Chernonozhkin+2021's phosphates); otherwise `N`.
  * A physical composite (Hu+Gao 2008's upper-crust composites) is not a combined result.

Corrected on the way:
  * Dispersion statistic `N` where the paper states the SD or RSD of its replicate means (Craddock, Nowell x2,
    Schönbächler; Hu+Gao, Yu, Makishima, Lu, Gil-Díaz x2; Desem, Li, Lu, Milne, Willbold). The old cells
    read the field as a goodness-of-fit test only; EPMA's convention counts the dispersion of a mean.
  * Inclusion rules the old cells missed: Hopp+2021 (samples with ε196Pt(8/5) > 0.16 left out of the group
    averages), Craddock+2008 (mass-bias drift > ~0.5‰), Nie+2019 (the norite left out of the regression),
    Schönbächler+2025 (outliers outside 2SD rejected).
  * Contributing counts the old cells missed: Navarro+2024 spots (20 in Arraias), Dobrica+2022 (N = 8, 19).
  * Liu+2016's merrillite column had borrowed the glass averages' counts (n = 7, 13).
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "
# Solution MC-ICP-MS. field -> {matcher: value}; OVERWRITE marks corrections of existing cells.
MC = {
 "Combination Method": {
  "Budde": "all: mean of pooled solution replicates per sample; weighted average of recombined separates" + D + "'For samples analyzed several times, reported values represent the mean of pooled solution replicates'; Table 1 notes b and c: 'Weighted average of C3m, C3n, C3i', 'Weighted average of C2, C3m, C3n, C3i, C4'",
  "Craddock": "δ34S: over the replicate analyses of each reference material; the statistic is not named" + D + "Table 3 '# of replicates', with 'External precision (two standard deviations) calculated from replicate analyses'",
  "Hopp": "all: average of n = 10–35 sample-standard bracketed measurements per sample solution; weighted average per iron-meteorite group, over the low-exposure samples (ε196Pt(8/5) ≤ 0.16) where within-group variation is significant; for IC and IIAB also the York-regression intercept of μ54Fe(7/6) against ε196Pt(8/5)" + D + "p.6; Table 1 notes g and h",
  "Hu+etal2022": "all: per sample, over 1 to 12 (typically 5) standard-sample-standard bracketings; the mean of seven CAIs is also shown" + D + "'The reported φE values were calculated based on 1 to 12 (typically 5) STD-SMP-STD bracketings'; Fig. 1 'The dashed line is the average isotopic fractionation' of the seven CAIs",
  "IbanezMejia": "all: weighted mean of all replicate measurements of each fraction" + D + "Table 1 note †: 'Reported values are weighted means of all replicate measurements for each fraction'",
  "Nie+Dauphas": "δ87Rb: average of 5–12 repeat measurements per sample solution; bulk Moon and bulk Earth from unweighted linear regressions against CI-normalised La/U, interpolated to La/U = 1" + D + "'The sample solutions were measured 5–12 times ... and the average δ87Rb values were calculated'; Fig. 1 caption",
  "Nowell+etal2008 | Neptune": "all: average of the reference-material analyses in each session and over all sessions" + D + "Table 7a; 'Average Os ratios for the 94 UMd and 121 DTM RM analyses from all analytical sessions'",
  "Nowell+etal2008 | Nu Plasma": "all: average of the reference-material analyses" + D + "Tables 7b and 8b",
  "Pringle": "δ87Rb: average of repeated measurements per sample; averages per group of samples" + D + "'Reported isotope ratios are averages of repeated measurements of each sample when multiple analyses were possible'; group averages for terrestrial rocks, lunar samples and chondrite groups (Table 1)",
  "Schönbächler": "all: average of the individual measurements of each sample" + D + "Fig. 1: 'the average of each sample with the corresponding uncertainty given as the 2 sd calculated from the individual sample measurements'",
  "vanKooten": "all: mean of ten standard-bracketed analyses per sample measurement; weighted means per chondrite grouplet" + D + "'the reported data represent the mean and 2 × standard error (SE) of ten individual standard-bracketed sample analyses'; 'weighted means of new grouplets CL, CT and a new average for CO chondrites'",
  "Broussard": "δ41K: average of repeat measurements" + D + "'The average d41K value for BHVO-2 was 0.448 ± 0.027'; each sample 'was measured approximately 20 times'",
  "Barnes+etal2025 | Neptune Plus | WUSTL": "N" + D + "the Bennu values carry '(2 s.e.)' (p.2), but how replicate analyses are combined is not stated",
  "Barnes+etal2025 | Neptune Plus | ETH": "all: average of repeated measurements" + D + "'The isotope data were collected on two different days and included four repetitions for Bennu'; 'the Bennu samples averages +0.27 ± 0.08 ε46Ti, −0.02 ± 0.05 ε48Ti and +1.98 ± 0.08 ε50Ti (2 s.e.)' (p.2), which may also include the LLNL aliquot",
 },
 "Combined Results": {
  "Budde": "per-sample means where N > 1 (Table 1, 'N: number of analyses'); chondrule fraction C3 (C3m, C3n, C3i); chondrule fractions combined (C2, C3m, C3n, C3i, C4)" + D + "Table 1 and notes b, c",
  "Craddock": "the reference materials and in-house standards of Table 3, each over its stated number of replicates (3–20)" + D + "Table 3",
  "Hopp": "per-sample averages (n = 10–35 each); IC low-exposure weighted average; IC intercept; IIAB low-exposure weighted average; IIAB intercept; IIC weighted average; IID low-exposure weighted average; IIIAB weighted average; IVA weighted average; IVB weighted average" + D + "Table 1",
  "Hu+etal2022": "per-CAI values (1 to 12 bracketings each); mean of the seven CAIs" + D + "Table 1; Fig. 1",
  "IbanezMejia": "each FC-1 zircon and baddeleyite fraction, over its replicates" + D + "Table 1, 'Replicates': 'Number of times the same purified Zr solution was measured independently'",
  "Nie+Dauphas": "per-sample averages (5–12 measurements each); bulk Moon δ87Rb (+0.03 ± 0.03‰); bulk Earth δ87Rb (−0.13 ± 0.01‰)" + D + "Table 1; Fig. 1 caption",
  "Nowell+etal2008 | Neptune": "UMd and DTM per-session averages; UMd average (94 analyses); DTM average (121 analyses); stable Os ratio averages (215 analyses); LOsST and DROsS averages" + D + "Tables 7a and 8a",
  "Nowell+etal2008 | Nu Plasma": "DTM average; LOsST average" + D + "Tables 7b and 8b",
  "Pringle": "per-sample averages; terrestrial average; low-Ti and high-Ti lunar averages; lunar average; Allende average; carbonaceous chondrite average; enstatite chondrite average" + D + "Table 1",
  "Schönbächler": "per-sample averages (n = number of measurements); BHVO-2 average of two digestions; Ryugu average (all); Ryugu average (samples); Allende average" + D + "Table 1",
  "vanKooten": "per-sample means (ten analyses each); CL grouplet weighted mean; CT grouplet weighted mean; CO average; CM-an average; CT average" + D + "Methods; Figs 2 and 4",
  "Broussard": "BHVO-2 δ41K average" + D + "p.4; whether the sample values average the ~20 measurements is not stated",
  "Barnes+etal2025 | Neptune Plus | WUSTL": "N",
  "Barnes+etal2025 | Neptune Plus | ETH": "Bennu ε46Ti, ε48Ti and ε50Ti average (four repetitions)" + D + "p.2 and Methods",
  "*": "N",
 },
 "Other Statistics": {
  "Budde": "all: 95% confidence interval for samples with N > 3" + D + "Table 1 note: 'the 95% confidence interval (95% CI) for samples with N > 3'; otherwise the uncertainty is BHVO-2's external 2 s.d.",
  "Hopp": "all: 95% confidence interval from Student's t" + D + "'using the average value and Student's t-value for a two-sided 95% confidence interval (95% c.i.)'; group averages '±95% c.i.' (Table 1 note g)",
  "Hu+etal2022": "all: 95% confidence interval from Student's t" + D + "from the sample's own dispersion with six or more bracketings, otherwise from the bracketed standards",
  "Nie+Dauphas": "δ87Rb: 2σ/√n, with σ from the bracketed standards" + D + "'The uncertainty for a sample was calculated using the formula of 2×σ/√n'",
  "Pringle": "δ87Rb: 2 standard errors per sample; 2 standard deviations per group average" + D + "'the 2 standard error (2 se) is reported unless stated otherwise'; '2 sd = 2 × standard deviation' (Table 1)",
  "Schönbächler": "all: 2SE" + D + "Table 1 gives '2SD 2SE' for each sample average",
  "vanKooten": "all: 2SE" + D + "'the mean and 2 × standard error (SE)'",
  "Barnes+etal2025 | Neptune Plus | ETH": "all: 2 s.e." + D + "p.2",
  "*": "N",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "Craddock": "δ34S: two standard deviations of the replicates" + D + "Table 3: 'External precision (two standard deviations) calculated from replicate analyses'",
  "Nowell+etal2008 | Neptune": "all: 2SD" + D + "Table 7a: 'All quoted errors are 2SD'",
  "Nowell+etal2008 | Nu Plasma": "all: 2SD" + D + "'Reported errors are 2SD unless otherwise stated'",
  "Schönbächler": "all: 2SD of the individual measurements" + D + "Fig. 1: 'the 2 sd calculated from the individual sample measurements'",
 },
 "Analysis Inclusion and Rejection Criteria": {
  "Craddock": "Rule: data showing mass-bias drift greater than ~0.5‰ during an individual sample are discarded; no count stated" + D + "'Data that show clear and large mass bias drift (greater than ∼0.5‰) during individual samples should be discarded'",
  "Hopp": "Rule: samples with ε196Pt(8/5) > 0.16 are left out of the low-exposure group averages; four samples excluded" + D + "'we, therefore, excluded four samples that have ε196Pt(8/5) >0.16 to calculate low-exposure averages' (p.9); Table 1 note g",
  "Nie+Dauphas": "Rule: the norite is left out of the bulk-Moon regression for its very light Rb isotopic composition" + D + "Fig. 1 caption: 'excluded from the regression due to its very light Rb isotopic composition (this sample is heterogeneous ...)'",
  "Schönbächler": "Rule: data outside the 2SD uncertainty are rejected as outliers; n stated per sample (n = 13–99 for terrestrial RMs; n = 17–38 for eucrites and Colony)" + D + "Table 1 note: 'An outlier rejection was carried out with rejection of data that falls outside the 2SD uncertainty'",
 },
}
MC_OVERWRITE = {("Goodness-of-Fit or Dispersion Statistic", k) for k in ("Craddock", "Nowell+etal2008 | Neptune", "Nowell+etal2008 | Nu Plasma", "Schönbächler")} | \
               {("Analysis Inclusion and Rejection Criteria", k) for k in ("Craddock", "Hopp", "Nie+Dauphas", "Schönbächler")}

# Solution Q-ICP-MS
SQ = {
 "Combination Method": {
  "Hu+Gao2008": "all: over the replicate analyses of each reference material; the statistic is not named" + D + "Table 2 gives n and 'RSD%' for AGV-1, BHVO-1, G-2, GSR-5 and SCO-1. The upper-crust samples are physical composites ('upper crustal composites from China'), not averages of analyses",
  "Yu+etal2005": "all: average of n replicate analyses of each consistency standard" + D + "Table notes: 'RSD% (relative standard deviation) = [SD of measurements/average ratio]*100%'; 'n, number of replicate analyses'",
  "Makishima": "all: average over repeat measurements" + D + "evaporation-test ratios 'together with the RSD (n = 5)'; detection limits 'an average of eight sessions'",
  "Lu+etal2007": "all: average of repeat runs per sample" + D + "'Orgueil and Allende were analyzed 4 times and twice from the sample digestion, respectively ... analytical results for each run are shown in the table' alongside the averages; bomb-method yields are the 'Average of two tests'",
  "GilDiaz+etal2020 | Agilent": "all: mean of N = 3" + D + "'mean ± SD recovery values of 94 ± 17% (N = 3)' for NCS 73307; experiments were run 'with 3 replicates per experimental condition'",
  "GilDiaz+etal2020 | Thermo XSeries": "Se sorption: mean of the replicate experiments at each condition" + D + "Fig. 2: 'Se sorption kinetics (N = 3)', 'sorption isotherms (N = 2)'; 'Error bars correspond to standard deviations (SD)'",
  "LopezGarcia": "all: average of replicates for the Allende powder; average of the eight Ryugu particles" + D + "'average values of the replicates (n = 5)'; 'The average abundance of the eight samples aligns within 20% of the average CI composition'",
 },
 "Combined Results": {
  "Hu+Gao2008": "AGV-1 (n = 6); BHVO-1 (n = 5); G-2 (n = 7); GSR-5 (n = 4); SCO-1 (n = 4); blank (n = 5)" + D + "Table 2",
  "Yu+etal2005": "each element/Ca ratio of the consistency standards, over its replicates (n = 120, 88, 32, 70, 50)" + D + "Tables 2 and 3",
  "Makishima": "evaporation-test ratios (n = 5); detection limits (average of eight sessions)" + D + "Tables 1 and 2",
  "Lu+etal2007": "Orgueil average (4 runs); Allende average (2 runs); bomb-method yields (average of two tests)" + D + "Tables 3 and 5",
  "GilDiaz+etal2020 | Agilent": "NCS 73307 recovery (N = 3)",
  "GilDiaz+etal2020 | Thermo XSeries": "Se sorption at each sampling time and condition (N = 3); sorption isotherm points (N = 2)" + D + "Fig. 2",
  "LopezGarcia": "Allende replicate average (n = 5); average of the eight Ryugu particles" + D + "supplementary data; Fig. 2",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "Hu+Gao2008": "all: RSD, relative standard deviation in percent" + D + "Table 2: 'The RSD is the relative standard deviation in percent'",
  "Yu+etal2005": "all: RSD% = SD of measurements / average ratio × 100" + D + "table notes",
  "Makishima": "all: RSD" + D + "'The normalised ratios after evaporation together with the RSD (n = 5)'",
  "Lu+etal2007": "all: RSD%" + D + "Tables 5 and 6; 'Averages of the reproducibility (RSD %)'",
  "GilDiaz+etal2020 | Agilent": "all: SD" + D + "'mean ± SD recovery values of 94 ± 17% (N = 3)'",
  "GilDiaz+etal2020 | Thermo XSeries": "Se sorption: SD" + D + "Fig. 2: 'Error bars correspond to standard deviations (SD)'",
 },
}
SQ_OVERWRITE = {("Goodness-of-Fit or Dispersion Statistic", k) for k in SQ["Goodness-of-Fit or Dispersion Statistic"]}

# Solution SF-ICP-MS
SSF = {
 "Combination Method": {
  "Desem": "all: average of repeat analyses of each reference material" + D + "'Results for SRM981 analysed with the NVP samples yield average ...'; averages with '2sd' and n for BCR-2, AGV-2, BR, JB-2 and JB-3",
  "Li+etal2016": "all: mean of three analyses" + D + "'The mean values and respective standard deviations (s) for three analyses were listed in Table 3'",
  "Lu+etal2007": "all: average of repeat runs per sample" + D + "'Orgueil and Allende were analyzed 4 times and twice from the sample digestion, respectively ... analytical results for each run are shown in the table' alongside the averages",
  "Milne": "all: mean of replicate analyses; average slope of the standard additions" + D + "'Mean blank ± 1S.D.'; 'Average slopes resulting from the regression analysis of Co and Mn standard additions'",
  "Misra": "all: average of 10 measurements within a session; average of the session averages" + D + "'Open symbols represent an average of 10 measurements acquired during a single instrument session. The solid symbols represent the average of the open symbols'",
  "Willbold": "all: mean of triplicate determinations per digestion; mean over the independent analyses of each reference material" + D + "'the mean values of the triplicate determinations and their RSDs' (Table 4); 'the mean value and RSD' of the other RMs (Table 5)",
 },
 "Combined Results": {
  "Desem": "SRM981 (n = 22); SRM981 (n = 16); BCR-2 (n = 39); AGV-2 (n = 13); BR (n = 11); JB-2 (n = 9); JB-3 (n = 11)",
  "Li+etal2016": "each reference material in Table 3 (n = 3)",
  "Lu+etal2007": "Orgueil average (4 runs); Allende average (2 runs)" + D + "Table 3",
  "Milne": "blank means; Co and Mn average standard-addition slopes; reference materials (n = 3); GEOTRACES samples (n = 5)",
  "Misra": "session averages of the consistency standards (10 measurements each); overall averages of the session averages" + D + "figures",
  "Willbold": "BHVO-1 (five digestions, triplicate each); sixteen other RMs (three to four analyses each); BCR-2G, BHVO-2G, BIR-1G and NIST SRM 612 (one digestion, triplicate)" + D + "Tables 4 and 5",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "Desem": "all: 2sd" + D + "'(2sd, n = 22)'; averages given with '±2sd%'",
  "Li+etal2016": "all: s, one standard deviation; RSD" + D + "'Mean ± 1 s (n = 3)'; 'RSD = standard deviation/mean × 100%'",
  "Lu+etal2007": "all: RSD%" + D + "'Averages of the reproducibility (RSD %)'",
  "Milne": "all: %RSD; 1 S.D. for blanks" + D + "'The precision is calculated as the percent relative standard deviation (% RSD)'; 'Mean blank ± 1S.D.'",
  "Willbold": "all: RSD" + D + "Tables 4 and 5",
 },
 "Other Statistics": {
  "Misra": "all: 2σ analytical uncertainty on the averages" + D + "'the average of the open symbols with 2σ analytical uncertainty'",
 },
}
SSF_OVERWRITE = {("Goodness-of-Fit or Dispersion Statistic", k) for k in SSF["Goodness-of-Fit or Dispersion Statistic"]}

# LA-MC-ICP-MS
LAMC = {
 "Combination Method": {
  "Zhang et al. 2022 (At. Spectrosc": "Rb–Sr isochron age, initial ⁸⁷Sr/⁸⁶Sr: isochron regression per meteorite and data group, by IsoplotR and by Monte Carlo linear fitting; the Normal group regresses one point per run, the SUIA group every cycle; other: N" + D + "Table 3; Figs 6 and 7; 'This data reduction method was called the smallest unit isochron age (SUIA)'",
 },
 "Combined Results": {
  "Zhang et al. 2022 (At. Spectrosc": "NWA 10597 Normal-group isochron (36 runs); NWA 10597 SUIA isochron (6 runs, 244 cycles); NWA 6950 Normal-group isochron (94 runs); NWA 6950 SUIA isochron (21 runs)" + D + "Table 3; Fig. 6",
 },
}

# LA-Q-ICP-MS (and its U-Pb consumer, which carries the same first six columns)
LAQ = {
 "Combination Method": {
  "Nakanishi": "Re/Os abundance ratio: mean of the 1–3 spots on each metal grain; other: N" + D + "'determined by the mean Re/Os abundance ratios for each of the 1–3 analytical spots measured by LA-ICP-MS' (Table 3)",
  "Liu et al. 2024": "all: mean of n = 9 spots per sample" + D + "Table 2: 'Mean' with '95% CI', 'fs-LA-ICP-MS (n = 9 spots)'",
  "Liu et al. 2025": "N" + D + "Table 1 gives 'one standard deviation' in parentheses, but not what it is taken over",
  "Tissint martian meteorite Silicates": "all: average of n LA-ICP-MS analyses per glass type" + D + "Table 3 note d: 'Average of a number of LA-ICP-MS analysis'",
  "Tissint martian meteorite Phosphate": "N" + D + "the averages of Table 3 (n = 7, n = 13) are glasses; the merrillite LA-ICP-MS data are per analysis",
  "Wu+etal2023": "Lu-Hf isochron and weighted-mean ages: isochron regression, and weighted mean of the common-Hf-corrected single-spot ages, per sample" + D + "'Isoplot R software was used to calculate isochron and weighted-mean ages'",
 },
 "Combined Results": {
  "Nakanishi": "per-grain mean Re/Os ratio for each metal grain in Table 3 (1–3 spots each)",
  "Liu et al. 2024": "each sample in Table 2 (n = 9 spots)",
  "Tissint martian meteorite Silicates": "glass-inclusion average (n = 7); impact-melt glass average (n = 13)" + D + "Table 3",
  "Wu+etal2023": "the weighted-mean and isochron ages of each sample in Figs 8–10, for example the XN02 weighted-mean age (236 of 246 spots) and the weighted mean of 15 session ages (n = 15)",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "Liu et al. 2024": "all: relative standard deviation" + D + "'relative standard deviations are reported as the precision measure'",
  "Tissint martian meteorite Silicates": "all: 1σ, one standard deviation of the average" + D + "Table 3 note b: '1σ is 1 standard deviation of the average'",
 },
 "Other Statistics": {
  "Liu et al. 2024": "all: 95% confidence interval" + D + "Table 2",
 },
 "Analysis Inclusion and Rejection Criteria": {
  "Tissint martian meteorite Phosphate": "N" + D + "the counts 'n = 7' and 'n = 13' (Table 3) are the two glass averages, not merrillite; no contributing count or rule is stated for the merrillite analyses",
 },
}
LAQ_OVERWRITE = {("Analysis Inclusion and Rejection Criteria", "Tissint martian meteorite Phosphate")}

# LA-SF-ICP-MS (and its U-Pb consumer, same seven columns)
LASF = {
 "Combination Method": {
  "Zhang et al. 2022 (GCA 323)": "Ge, Sb, Re, Os, Ir: mean of the spot average and the raster average; other: raster average" + D + "Table 3 title 'Compositions (raster averages)'; note: 'calculated from the mean of the spot average (Appendix 2) and the raster average in this table'",
  "Pallasite olivine Raster": "all: average over the map pixels after masking the P-rich veinlets ('pure' olivine)" + D + "Fig. 4: 'to cancel out the input of the P2O5-rich veinlets to obtain average “pure” olivine values'",
  "Pallasite olivine Line scan": "all: average of 3 replicate measurements" + D + "Table 1: 'The results shown are the average from 3 replicate measurements'",
  "Pallasite phosphate": "all: Not combined" + D + "Table 2: 'All single parallel measurements are presented separately'",
  "Mittlefehldt": "all: average per sample split; weighted mean per meteorite" + D + "'data averaged per sample split' (Table L2), 'meteorite averages' (Table L3); 'Because a weighted mean is calculated for the data'",
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": "all: average of n replicate spot measurements per meteorite" + D + "'average (x̅); s: standard deviation of n measured values'; 'the mean value of 20 spot measurements in the Arraias meteorite'",
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": "all: integrated over the map points assigned to each phase" + D + "Table 5: '176 kamacite points (211,060 µm2) and 1,173 plessite points (1,712,297 µm2)'",
 },
 "Combined Results": {
  "Zhang et al. 2022 (GCA 323)": "raster averages for seven IIIF irons and two pallasites; spot averages" + D + "Table 3; Appendix 2",
  "Pallasite olivine Raster": "'pure' olivine averages from the maps (for example Seymchan and Fukang)",
  "Pallasite olivine Line scan": "each main-group pallasite olivine in Table 1 (3 replicates each)",
  "Mittlefehldt": "per-split averages (Table L2); per-meteorite weighted means (Table L3)",
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": "per-meteorite averages (Table 3 and the data table for Figs 2 and 3), for example Arraias (20 spots)",
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": "kamacite (176 points, 211,060 µm2); plessite (1,173 points, 1,712,297 µm2)" + D + "Table 5",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "Pallasite olivine Line scan": "all: 1 standard deviation" + D + "Table 1: 'the uncertainty corresponds to 1 standard deviation'",
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": "all: s, standard deviation of n measured values; RSD" + D + "data table for Figs 2 and 3",
 },
 "Other Statistics": {
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": "all: 2 sdm" + D + "Table 5",
 },
 "Analysis Inclusion and Rejection Criteria": {
  "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": "Partially — contributing counts are stated ('n: number of replicates'; 'the mean value of 20 spot measurements in the Arraias meteorite'); no acceptance or rejection rule is stated",
 },
}
LASF_OVERWRITE = {("Analysis Inclusion and Rejection Criteria", "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot")}

# TEM
TEM = {
 "Combination Method": {
  "STEM-EDS hyperspectral": "MnO, FeO: mean per carbonate region; other: N" + D + "'region B - N = 19, 6.1 wt% MnO, S.D. 1.4; 3.1 wt% FeO, S.D. 1.0' against 'region A - N = 8'; 'the average dolomite in region A has 51.4 mol% CaCO3'",
  "Xing2023": "N" + D + "review article; it reports no original analyses",
 },
 "Combined Results": {
  "STEM-EDS hyperspectral": "region A carbonates (N = 8); region B carbonates (N = 19); region A dolomite average",
  "Xing2023": "N" + D + "review article; it reports no original analyses",
 },
 "Goodness-of-Fit or Dispersion Statistic": {
  "STEM-EDS hyperspectral": "MnO, FeO: S.D., standard deviation; other: N" + D + "'S.D. – standard deviation'",
 },
 "Analysis Inclusion and Rejection Criteria": {
  "STEM-EDS hyperspectral": "Partially — contributing counts are stated per region (region A N = 8, region B N = 19); no acceptance or rejection rule is stated",
 },
}
TEM_OVERWRITE = {("Analysis Inclusion and Rejection Criteria", "STEM-EDS hyperspectral")}

NEW = ("Combination Method", "Combined Results", "Other Statistics", "Goodness-of-Fit or Dispersion Statistic")
PLAN = {  # TAPP prefix -> (edits, overwrite set)
  "LA-MC-ICPMS_TAPP_v": (LAMC, set()),
  "LA-Q-ICP-MS_TAPP_v": (LAQ, LAQ_OVERWRITE),
  "LA-Q-ICP-MS_UPb_TAPP_v": (LAQ, LAQ_OVERWRITE),
  "LA-SF-ICP-MS_TAPP_v": (LASF, LASF_OVERWRITE),
  "LA-SF-ICP-MS_UPb_TAPP_v": (LASF, LASF_OVERWRITE),
  "Solution_MC-ICP-MS_TAPP_v": (MC, MC_OVERWRITE),
  "Solution_Q-ICP-MS_TAPP_v": (SQ, SQ_OVERWRITE),
  "Solution_SF-ICP-MS_TAPP_v": (SSF, SSF_OVERWRITE),
  "TEM_TAPP_v": (TEM, TEM_OVERWRITE),
}


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def pick(spec, label):
    hits = [k for k in spec if k != "*" and k in label]
    if len(hits) > 1:
        hits.sort(key=len, reverse=True)
        if len(hits[0]) == len(hits[1]):
            raise SystemExit("PREMISE: matchers %r are ambiguous for %r" % (hits, label))
    if hits:
        return hits[0], spec[hits[0]]
    return ("*", spec["*"]) if "*" in spec else (None, None)


def edit(rr, edits, over, report, used):
    h = rr[0]; s = h.index("Literature Assessment")
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    fields = set(edits) | set(NEW)
    for f in fields:
        if f not in by:
            continue
        spec = dict(edits.get(f, {}))
        if f in NEW:
            spec.setdefault("*", "N")
        r = by[f]
        for j in range(s + 1, len(h)):
            label = " ".join(h[j].split())
            if not label:
                continue
            k, v = pick(spec, label)
            if k is None:
                continue
            used.add((f, k))
            old = r[j]
            if old.strip() and (f, k) not in over:
                continue
            if not old.strip() and (f, k) in over:
                raise SystemExit("PREMISE: [%s] %s was expected to hold the cell being corrected" % (label, f))
            if old != v:
                report.append((label, f, old, v)); r[j] = v
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan, used = [], set()
    for pre, (edits, over) in PLAN.items():
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(pre))
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        report = []
        edit(rows_of(os.path.join(ROOT, rel)), edits, over, report, used)
        print("  %s -> %s: %d cells (%d corrections)" % (os.path.basename(rel), os.path.basename(new), len(report),
                                                          sum(1 for x in report if x[2].strip())))
        if "--show" in sys.argv:
            for c, f, old, v in report:
                if v != "N":
                    print("    [%s] %s\n        was: %s\n        now: %s" % (c[:60], f, old[:90], v[:150]))
        plan.append((e, rel, new, edits, over))
    for edits, name in ((MC, "MC"), (SQ, "SQ"), (SSF, "SSF"), (LAMC, "LAMC"), (LAQ, "LAQ"), (LASF, "LASF"), (TEM, "TEM")):
        for f, spec in edits.items():
            for k in spec:
                if k != "*" and (f, k) not in used:
                    raise SystemExit("PREMISE: %s matcher %r for %s matched no column" % (name, k, f))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change except plain N)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for e, rel, new, edits, over in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), edits, over, [], set()))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
        rp = os.path.join(ROOT, "composed_tapps.json")
        reg = json.load(io.open(rp, encoding="utf-8"))
        for x in reg["composed"]:
            if x["tapp"] == rel:
                x["tapp"] = new
        with io.open(rp, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
