#!/usr/bin/env python3
"""
Solution MC-ICP-MS — Phase 3 draft (first literature assessment for this TAPP).

Target: Solution_MC-ICP-MS_TAPP_v22.csv (117 content fields, 0 existing literature columns).
Paper set agreed with the user: the 10 PDFs in "Solution MC-ICP-MS/literature assessment/" plus
Broussard 2026 and Barnes 2025, both labelled Detailed for MC-ICP-MS in paper_registry.csv.

12 papers -> 14 procedure columns. Two papers describe more than one procedure under separately
stated conditions, which lit_assessment.md makes separate columns:
  * Nowell et al. 2008 -- Neptune at Durham AND Nu Plasma at NIGL, "The instrument setups employed
    for the Neptune and Nu Plasma measurements were different and are described separately below."
  * Barnes et al. 2025 -- K/Cu/Zn at WUSTL AND Ti at ETH Zurich, different introduction systems and
    resolution slits.

SOURCE KEYS (every cell below traces to a sentence, table cell or figure caption read from the PDF
in this session):
  [Bu] Budde+2016 EPSL 454, 293-303        [Cr] Craddock+2008 Chem Geol 253, 102-113
  [Ho] Hopp+2021 (Fe, Univ Chicago)        [Hu] Hu+2022 Sci Adv (REE, Univ Chicago)
  [IM] Ibanez-Mejia & Tissot 2020 Sci Adv  [Ni] Nie & Dauphas 2019 ApJL 884, L48
  [No] Nowell+2008 Chem Geol 248, 363-393  [Pr] Pringle & Moynier 2017 EPSL 473, 62-70
  [Sc] Schoenbaechler+2025 MAPS            [vK] van Kooten+2026 Nat Astron
  [Br] Broussard+2026 MAPS                 [Ba] Barnes+2025 Nat Astron

CONVENTIONS (references/lit_assessment.md): N = applicable but not stated; N/A = the concept does
not apply to this procedure; never blank. Values recorded only where directly stated.
"Partially" flags a cell where part of what the field asks for is stated and part is not.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
SRC = os.path.join(ROOT, "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v22.csv")
OUT = os.path.join(ROOT, "Solution MC-ICP-MS/Solution_MC-ICP-MS_lit_assessment_draft_2026-08-14.csv")

COLS = [
 "Budde+etal2016 | Neptune Plus | IfP Münster",
 "Craddock+etal2008 | Thermo NEPTUNE | WHOI",
 "Hopp+etal2021 | Neptune (Plus spec) | Univ Chicago",
 "Hu+etal2022 | Neptune Plus | Univ Chicago",
 "IbanezMejia+Tissot2020 | Nu Plasma II | MIT",
 "Nie+Dauphas2019 | Neptune | Univ Chicago",
 "Nowell+etal2008 | Neptune | Durham AHIGL",
 "Nowell+etal2008 | Nu Plasma | NIGL",
 "Pringle+Moynier2017 | Neptune Plus | IPGP",
 "Schönbächler+etal2025 | Neptune Plus | ETH Zurich",
 "vanKooten+etal2026 | Thermo Neoma | Univ Copenhagen",
 "Broussard+etal2026 | Neptune Plus | WUSTL",
 "Barnes+etal2025 | Neptune Plus | WUSTL",
 "Barnes+etal2025 | Neptune Plus | ETH Zurich",
]
BU, CR, HO, HU, IM, NI, NOa, NOb, PR, SC, VK, BR, BAa, BAb = range(14)
N = len(COLS)

OV = {}
def ov(field, d):
    OV.setdefault(field, {}).update(d)

# ---------------------------------------------------------------- Group 1
ov("Technique", {i: 'Solution MC-ICP-MS' for i in range(N)})
ov("Laboratory", {
 BU: 'Institut für Planetologie, University of Münster [Bu sec 2]',
 CR: 'Woods Hole Oceanographic Institution [Cr affiliations]',
 HO: 'University of Chicago [Ho sec 2.3]',
 HU: 'University of Chicago [Hu, MC-ICPMS analysis section]',
 IM: 'Massachusetts Institute of Technology [IM, Zr stable isotope analyses]',
 NI: 'University of Chicago [Ni sec A.3]',
 NOa: 'Arthur Holmes Isotope Geology Laboratory, Durham [No sec 3]',
 NOb: 'NERC Isotope Geosciences Laboratory (NIGL) [No sec 3]',
 PR: 'Institut de Physique du Globe de Paris [Pr affiliations]',
 SC: 'ETH Zurich; sample digestion and separation at Tokyo Institute of Technology [Sc, Mass Spectrometry and Sample Preparation]',
 VK: 'Centre for Star and Planet Formation, Globe Institute, University of Copenhagen [vK affiliations]',
 BR: 'Washington University in St. Louis [Br sec 4]',
 BAa: 'Washington University in St. Louis [Ba, isotope analyses]',
 BAb: 'Institute of Geochemistry and Petrology, ETH Zurich [Ba, Bulk Ti isotopes]'})
ov("Coupled Technique(s)", {
 BU: 'TIMS — Ba isotopes on a Thermo Scientific Triton Plus at the same institute; Hf-W on the same sample digestions [Bu sec 2]',
 CR: 'Laser-ablation MC-ICP-MS — the same NEPTUNE, with a NewWave UP213 laser, "such that laser ablation and solution aspiration can be operated simultaneously" [Cr sec 2.3, Fig. 1]',
 HO: 'Prior Pt, Mo, Ni and/or W isotope analyses on the same digestions [Ho sec 2.1]',
 IM: 'ID-TIMS U-Pb on an Isotopx X-62 at MIT, and solution Q-ICP-MS (Agilent 7700) for Zr and Hf concentrations, on aliquots of the same dissolutions [IM sec Zircon Zr and Hf concentration measurements]',
 SC: 'Mg, K, Ca, Ti, Cr, Fe, Cu, Zn, Mo and Nd isotope data "all obtained from the same sample digestions and are therefore directly comparable" [Sc sec 4]',
 VK: 'ICP-MS for Sr and Rb weathering assessment; Si isotopes on a separate NaOH-fusion aliquot [vK, Methods]',
 BR: 'Laser-fluorination oxygen isotopes on a Thermo Finnigan MAT 253 Plus; K loss monitored by Thermo Fisher iCAP Q ICP-MS [Br sec 4]',
 BAa: 'High-resolution ICP-MS (Thermo Element XR) at LLNL for bulk elemental abundances, on splits of the same digest [Ba, Bulk elemental abundances]',
 BAb: 'Coordinated dissolution shared with the WUSTL K/Cu/Zn procedure; SIMS oxygen isotopes [Ba, Bulk Ti isotopes]'})
ov("Coupling Description", {
 CR: 'Functional: the laser is connected directly to the spray chamber so ablated particles mix with 2% HNO3 and are "effectively analyzed as a wet plasma ensuring that ablated aerosols are closely matrix-matched to solution standards". Sequence: interchangeable — "Our setup allows for interchangeable bulk and in situ S isotope measurement" [Cr sec 2.3]',
 IM: 'Functional: 3 M HCl washes from the U-Pb anion chemistry were collected and became the Zr aliquots, so the same crystal yields a U-Pb date and a Zr isotopic composition. Sequence: U-Pb purification first, Zr purification from its washes [IM sec Zr stable isotope analyses]',
 BR: 'Functional: pre-cut and post-cut fractions either side of the K collection were measured by Q-ICP-MS "to monitor for K loss during column chemistry". Sequence: Q-ICP-MS check before MC-ICP-MS measurement [Br sec 4]'})

# ---------------------------------------------------------------- Group 2
ov("Target Material", {
 BU: 'Chondrules, matrix separates and bulk rock of the Allende CV3 chondrite [Bu sec 2]',
 CR: 'Sulfate minerals (anhydrite, barite, gypsum) and sulfide minerals (pyrite, chalcopyrite) [Cr sec 1]',
 HO: 'Iron meteorites and terrestrial basalt geostandards [Ho sec 2.1]',
 HU: 'Calcium-aluminium-rich inclusions (CAIs) [Hu]',
 IM: 'Single zircon and baddeleyite crystals, and bulk rock [IM sec Mineral separation]',
 NI: 'Silicate rocks — geostandards including basalts, granites and peridotites, and the Allende chondrite [Ni sec A.4]',
 NOa: 'Osmium isotope reference material solutions [No sec 3]',
 NOb: 'Osmium isotope reference material solutions [No sec 3]',
 PR: 'Whole-rock terrestrial igneous rocks, chondrites, achondrites and Apollo lunar samples [Pr sec 2.1]',
 SC: 'Ryugu returned samples, carbonaceous chondrites, eucrites and terrestrial rock reference materials [Sc sec 4, EXPERIMENTAL]',
 VK: 'Bulk chondrite powders [vK, Methods]',
 BR: 'CI chondrite Oued Chebeika 002 and geostandard [Br sec 4]',
 BAa: 'Bennu returned sample aggregate [Ba, isotope analyses]',
 BAb: 'Bennu returned sample aggregate [Ba, Bulk Ti isotopes]'})
ov("Sample Name", {
 BU: 'Three matrix separates, six chondrule fractions (C2, C3, C4; C3m, C3i, C3n) and two bulk rock samples of Allende; BHVO-2 [Bu sec 2]',
 CR: 'IAEA-S-1, S-2, S-4, NBS-123; in-house standards S_Alfa and S_Spex; anhydrite mineral standard Sch-M-2; pyrite FVG-1 [Cr sec 2.1, Table]',
 HO: 'Toluca, Gibeon, Duchesne, Skookum, Tlacotepec and 18 further iron meteorites; BHVO-2, BCR-2; IRMM-524a [Ho sec 2.1, 2.3]',
 HU: 'Group II CAIs including FG-FT-4, FG-FT-8 and FG-FT-9 [Hu, REE extraction]',
 IM: 'FC-1 zircon and baddeleyite crystals; ZrNIST reference solution [IM Table 1]',
 NI: 'BHVO-2, BCR-2, BE-N, W-2, AGV-2, GSR-1, GS-N, G-A, G-3; DTS-2b and PCC-1 synthetic mixes; Allende; NIST SRM984 [Ni sec A.4]',
 NOa: 'UMd, DTM, LOsST and DROsS Os isotope reference materials [No sec 3]',
 NOb: 'DTM and LOsST Os isotope reference materials [No sec 3]',
 PR: 'GS-N, AGV-2, BCR-2, BHVO-2, EW9309 10D, AHANEMO2 D20B; Allende (duplicate splits); NIST SRM984 [Pr sec 2.1, Table 3]',
 SC: 'Ryugu A0106, A0106-A0107 and C0108; Tagish Lake, Tarda, Ivuna (PB and high PT), Orgueil, Murchison, Colony; eucrites Bouvante and Bereba; BHVO-2, BCR-2, AGV-1, SCo-1; NIST SRM 3169 [Sc EXPERIMENTAL, Table 1]',
 VK: 'BHVO2 and DTS-2b processed alongside the samples [vK, Methods]',
 BR: 'Oued Chebeika 002; geostandard BHVO-2; NIST SRM 3141a [Br sec 4]',
 BAa: 'OREX-803015-101 (LLNL split) and OREX-803015-100 (ETH split) of Bennu aggregate; BHVO-2 [Ba]',
 BAb: 'OREX-803015-100, a 5.2 mg aliquot of Bennu aggregate [Ba, Bulk Ti isotopes]'})
ov("Sample Persistent Identifier", {
 BAa: 'Curatorial sample identifiers stated: OREX-803015-101 (LLNL) and OREX-803015-100 (ETH Zurich) [Ba, isotope analyses]',
 BAb: 'OREX-803015-100 [Ba, Bulk Ti isotopes]'})
ov("Sampling Unit", {
 BU: 'Digestion aliquot — "All samples (0.3–0.5 g) were digested in closed Savillex beakers"; chondrule fractions "comprise between 155 and ~3000 chondrules each" [Bu sec 2]',
 CR: 'Purified solution aliquot — "Less than 50 mg of sample was accurately weighed"; "A precise solution volume, corresponding to 500 µg of S" taken for column purification [Cr sec 2.2]',
 HO: 'Solution aliquot of a digestion — "the Fe isotopic compositions were analyzed on solution aliquots (~1-2 mg Fe) of digestions"; five meteorites cut as "~50 mg pieces" [Ho sec 2.1]',
 HU: 'Fraction of a CAI digestion — "Approximately 30% of the matrix cut", "equivalent to 24% fraction of the whole CAI" [Hu, REE extraction]',
 IM: 'Single crystal — "Single zircon and baddeleyite crystals selected for analysis were individually handpicked"; each "individually loaded into clean PFA microcapsules" [IM sec Mineral separation, Zr stable isotope analyses]',
 NI: 'Digestion aliquot — "Samples of about 100 mg or less were digested" [Ni sec A.2]',
 NOa: 'Reference material solution aliquot — 200 ng/ml to 2.5 µg/ml Os, ~300 µl consumed per analysis [No sec 3, 3.3]',
 NOb: 'Reference material solution aliquot — ~6400 µl consumed per analysis [No sec 3.2]',
 PR: 'Weighed powder aliquot — "An aliquot of <=125 mg of powdered sample was weighed depending on the Rb concentration of the sample; masses were calculated to yield >20 ng Rb" [Pr sec 2.2]',
 SC: 'Digestion aliquot — Ryugu "aliquots of <25 mg were analyzed with ~40 to 70 ng Zr"; Tagish Lake 30 mg, Tarda 90 mg, Ivuna 40 and 44 mg "from a larger homogenized powder (550 mg)" [Sc sec 4, EXPERIMENTAL]',
 VK: 'Fraction of a bulk digestion — "Another 5% fraction was used to determine Al/Mg ratios by multi-collector (MC)-ICPMS" [vK, Methods]',
 BAa: 'Split of a single digest — "The solution was then split two ways: about half stayed at WUSTL and half was sent to Lawrence Livermore National Laboratory ... the aliquot was further split into two aliquots" [Ba]',
 BAb: 'A 5.2 mg aliquot of Bennu aggregate [Ba, Bulk Ti isotopes]'})
ov("Sample Preparation Method", {
 BU: 'Chondrule, matrix and bulk rock separates; preparation detailed in the supplementary material [Bu sec 2]',
 CR: 'Mineral standard cut as a 2 mm thick section, polished and mounted on a 45x25 mm petrographic slide for the laser half; solution half dissolved from weighed mineral [Cr sec 2.1]',
 HO: 'Iron meteorite pieces "cut using a diamond saw, polished with SiC abrasive paper, and cleaned in ethanol" [Ho sec 2.1]',
 IM: 'Crushing in a stainless steel mortar, sieving through 375 µm plastic mesh, washing in a plastic gold pan, hand magnet, Frantz LB-1 magnetic separation, methylene iodide heavy liquid, hand picking under high-purity ethanol [IM sec Mineral separation]',
 NI: 'Whole-rock powder [Ni sec A.2]',
 NOa: 'N/A — reference material solutions, no solid preparation [No sec 3]',
 NOb: 'N/A — reference material solutions, no solid preparation [No sec 3]',
 PR: '"Whole rock samples were crushed by hand using an agate mortar until a fine powder was obtained. A minimum of 0.5 g of terrestrial rock or meteorite and 100 mg of lunar samples was crushed in order to avoid non-representational sample analysis" [Pr sec 2.2]',
 SC: 'Homogenised powder — Ivuna aliquots taken "from a larger homogenized powder (550 mg)" [Sc EXPERIMENTAL]',
 VK: 'Bulk powder; for the Si aliquot, NaOH fusion in silver crucibles [vK, Methods]'})
ov("Digestion Acid(s)", {
 BU: '"HF–HNO3(–HClO4), followed by inverse aqua regia" [Bu sec 2]',
 CR: '5 ml HNO3 (50%), then 3 ml concentrated HNO3 + 2 mL HCl (50%); residue dissolved in 4 mL 2% HNO3 [Cr sec 2.2]',
 HO: 'Iron meteorites: aqua regia (3:1 HCl-HNO3). Basalts: HF-HNO3 (2:1) followed by several steps of aqua regia. All converted to chloride and redissolved in 0.25 ml 10 M HCl [Ho sec 2.1]',
 HU: '"redissolved in a 2:1 mixture of HCl:HNO3 for 1 week on a hot plate ... These steps were performed twice"; dried and dissolved in concentrated HNO3, diluted in 3 M HNO3 [Hu, sample dissolution]',
 IM: '29 M HF; after conversion to a chloride matrix for U-Pb. Zr aliquots taken up in 3 M HNO3 + 0.5 M HF [IM sec Zr stable isotope analyses]',
 NI: 'Three steps of concentrated HF–HNO3–HCl–HClO4; step (i) "4 ml 28 M HF + 2 ml 15 M HNO3 + 1 ml 10 M HClO4" [Ni sec A.2]',
 NOa: 'N/A — reference material solutions in 3 or 5 mol/l Teflon-distilled HCl [No sec 3.1, 3.4]',
 NOb: 'N/A — reference material solutions in Teflon-distilled 3 mol/l HCl [No sec 3.2]',
 PR: '"a mixture of concentrated HF/HNO3"; after evaporation "6N HCl was added" to dissolve fluoride complexes [Pr sec 2.2]',
 SC: 'Concentrated HF-HNO3, then a HNO3-HCl mixture, then a HNO3-H2O2 mixture; Ivuna high PT: concentrated HF-HNO3 for 3 days then concentrated HCl for 2 days [Sc EXPERIMENTAL]',
 VK: 'Cr/Mg route: 6 M HCl loading, 10 M HCl pretreatment, 0.5 M HCl, 0.5 M HNO3, 1 M HF, 6 M HCl elutions; Si route: NaOH fusion then Milli-Q water and HNO3 [vK, Methods]',
 BAa: '"concentrated HF and HNO3 in a 3:1 ratio", followed by fluxing in concentrated HNO3 and HCl with 1 ml H2O2 added to remove organics; brought up in 5 ml 0.5 M HNO3 [Ba]',
 BAb: 'Coordinated dissolution shared with the WUSTL split — see the WUSTL column [Ba, Bulk Ti isotopes]'})
ov("Digestion Vessel Type", {
 BU: '"closed Savillex beakers" [Bu sec 2]', CR: '15 ml PTFE digestion vessel [Cr sec 2.2]',
 HO: 'Hot plate, closed vessel not specified beyond "on a hot plate" [Ho sec 2.1]',
 IM: '"clean Teflon microcapsules" inside "a large-volume Parr digestion vessel" [IM sec Zr stable isotope analyses]',
 NI: '30 ml fluoropolymer vessel [Ni sec A.2]',
 NOa: 'N/A', NOb: 'N/A',
 PR: '"closed Teflon bombs" [Pr sec 2.2]',
 SC: 'Octagonal-body Savillex vials; Parr bomb (Ivuna PB, BCR-2, AGV-1); hotplate (BHVO-2) [Sc EXPERIMENTAL]',
 BAa: '"in a closed beaker" [Ba]'})
ov("Digestion Temperature", {
 CR: '"less than 70 °C" for the first evaporation; 70 °C for the total digestion [Cr sec 2.2]',
 HO: 'Iron meteorites 120 °C; basalts 150 °C [Ho sec 2.1]',
 HU: 'Hot plate, temperature not stated [Hu]',
 IM: '215 °C [IM sec Zr stable isotope analyses]',
 PR: '130 °C for both the HF/HNO3 and the 6N HCl steps [Pr sec 2.2]',
 SC: '180 °C (hotplate), 120 °C (HNO3-HCl), 220 °C (Savillex, Tagish Lake and Tarda), 170 °C (Parr bomb, Ivuna PB), 160 °C (Ivuna high PT) [Sc EXPERIMENTAL]',
 VK: '130 °C for the 10 M HCl Cr(VI) speciation step; 720 °C for the NaOH fusion [vK, Methods]',
 BR: '70 °C for the HCl step; 140 °C for the HF/HNO3 mixture [Br sec 4]',
 BAa: '170 °C [Ba]'})
ov("Digestion Duration", {
 CR: 'Not stated for the individual steps beyond "taken to dryness" [Cr sec 2.2]',
 HO: 'Iron meteorites 24 hours; basalts 48 hours [Ho sec 2.1]',
 HU: '1 week per step, performed twice [Hu]',
 IM: 'Zircon 48 hours (U-Pb) and 60 hours (Zr isotopes) [IM sec Zr stable isotope analyses]',
 PR: '">48 h" [Pr sec 2.2]',
 SC: '3–7 days (hotplate), 12 h (HNO3-HCl), "about a week" (Tagish Lake and Tarda), 3 days + 2 days (Ivuna high PT) [Sc EXPERIMENTAL]',
 VK: '3 h (Cr(VI) speciation), >1 week at room temperature (Cr(III) speciation), 13 min (NaOH fusion) [vK, Methods]',
 BR: '20 h for the HF/HNO3 step [Br sec 4]',
 BAa: '48 h [Ba]'})
ov("Number of Digestion Steps", {
 NI: 'Three [Ni sec A.2]', HU: 'Two ("These steps were performed twice") [Hu]',
 SC: 'Ivuna high PT: two (HF-HNO3 then HCl) [Sc EXPERIMENTAL]'})
ov("Final Solution Matrix", {
 CR: '2% (w/w) HNO3, 50 ppm S stock [Cr sec 2.1, 2.2]',
 HO: '0.3 M HNO3 (measured at 10 µg/g Fe in 0.45 M HNO3); all sample and standard solutions "prepared with the same 0.3 M HNO3 solution" [Ho sec 2.2, 2.3]',
 HU: '15–25 ppb for the most abundant isotope [Hu]',
 IM: '0.59 M HNO3 + 0.28 M HF, samples and bracketing standards matched in matrix and at 60 ng/g total Zr [IM sec Zr stable isotope analyses]',
 NI: '0.3 M HNO3, ~15–25 ppb Rb [Ni sec A.3]',
 NOa: '3 or 5 mol/l Teflon-distilled HCl [No sec 3.1, 3.4]', NOb: '3 mol/l Teflon-distilled HCl [No sec 3.2]',
 PR: '0.1N HNO3 [Pr sec 2.2]',
 SC: '0.5 M HNO3 - 0.005 M HF at 30 ppb Zr (also 17 and 60 ppb) [Sc, Mass Spectrometry]',
 VK: '0.5 M HNO3 (Cr); 6 M HCl elution of the final Cr cut [vK, Methods]',
 BR: '300 ppb K solution [Br sec 4]',
 BAa: '200 ppb for K and Zn; 100 ppb for Cu [Ba]'})
ov("Sample Aliquot Mass or Volume", {
 BU: '0.3–0.5 g digested; ~100 ng Mo consumed per measurement [Bu sec 2]',
 CR: '<50 mg weighed; 500 µg S taken for column purification [Cr sec 2.2]',
 HO: '~1-2 mg Fe per analysis; ~50 mg meteorite pieces [Ho sec 2.1]',
 IM: 'Single crystals; ~50 µl (5% of sample) taken for concentration measurement [IM]',
 NI: '~100 mg or less; ~40 ng Rb typical [Ni sec A.2]',
 NOa: 'Up to 600 ng Os consumed per analysis; ~300 µl of solution [No sec 2, 3.3]',
 NOb: '~6400 µl of solution per analysis [No sec 3.2]',
 PR: '<=125 mg powder, calculated to yield >20 ng Rb [Pr sec 2.2]',
 SC: 'Ryugu <25 mg with ~40–70 ng Zr; 15 ng Zr consumed per 30 ppb analysis [Sc]',
 BAb: '5.2 mg [Ba, Bulk Ti isotopes]'})
ov("Chromatographic Separation Applied", {
 BU: 'Yes — two-stage anion exchange for W, with Mo collected in 3 M HNO3 and further purified on Eichrom TRU Resin; Ba separated on AG50-X8 [Bu sec 2]',
 CR: 'Yes — cation exchange AG50-X8 (H+ form), 2.5 ml resin, conditioned with 1.4 N HNO3; S passes through while matrix elements are retained. Yield 98±4% [Cr sec 2.2]',
 HO: 'Yes — AG1-X8 (200-400 mesh) anion resin, 3 ml, 10.5 cm PFA columns; repeated with new resin. Overall Fe yield >99% [Ho sec 2.2]',
 HU: 'Yes — U/TEVA, TODGA, then two-step FPLC on Ln-Spec resin (70 cm x 1.6 mm, 1.4 ml of 25–50 µm resin, 94 steps, 188 ml, 16 h at 70 °C, 0.17 ml/min). Overall yields >95% [Hu, REE extraction and FPLC elution]',
 IM: 'Yes — AG-1X for U-Pb; Ln-Spec (~300 µl, 25–50 µm) for Zr, giving >95% Zr, undetectable REEs and <3% of initial Hf; TODGA first stage for bulk rocks [IM]',
 NI: 'Yes — five steps: AG50W-X8 cation, a second cation column, AG1-X8 anion in 2 M HF for Ti, a 40 cm Eichrom Sr resin column for Rb-K, and an AG50W-X8 clean-up. Yields >95% [Ni sec A.2]',
 NOa: 'N/A — reference material solutions [No sec 3]', NOb: 'N/A — reference material solutions [No sec 3]',
 PR: 'Yes — DGA resin Ca removal (1.8 mL), then AG50 X12 (20 mL and 10 mL) in 3N HCl, then AG50 X8 (1 mL) in 0.5N HCl. Reduces K/Rb by a factor of 200 to K/Rb<2 and gives 88Sr/85Rb<0.005 [Pr sec 2.2, 2.3]',
 SC: 'Yes — four-step separation on anion exchange (AG 1-X8), DGA and LN resin; two-stage anion exchange for Ivuna; three-stage AG 1-X8 + LN for terrestrial samples [Sc EXPERIMENTAL]',
 VK: 'Yes — AG1-X8 anion (1 ml) for Fe, then AG50-X12 cation (1 ml) twice for Cr and Mg [vK, Methods]',
 BR: 'Yes — twice through 1.5 mL Bio-Rad AG50W-X8 100–200 mesh cation resin, loading, matrix elution and K elution all in 0.5 M HNO3 [Br sec 4]',
 BAa: 'Yes — AG1-X8 200–400 mesh anion resin, 5 ml 1.5 M HBr to elute the matrix and 3 ml 0.5 M HNO3 to elute Zn [Ba]',
 BAb: 'Yes — three-step anion exchange chromatography; yields 75–100% [Ba, Bulk Ti isotopes]'})
ov("Isotope Dilution Spike", {
 IM: 'In-house 91Zr-96Zr double spike, added at a 0.43:0.57 spike-to-sample Zr mass ratio [IM sec Zr stable isotope analyses]',
 **{i: 'N/A — no isotope dilution spike; mass bias handled by standard-sample bracketing or internal normalization' for i in (BU, CR, HO, HU, NI, NOa, NOb, PR, SC, VK, BR, BAa, BAb)}})

# ---------------------------------------------------------------- Group 3
ov("Instrument Manufacturer", {
 **{i: 'Thermo Fisher Scientific' for i in range(N) if i != IM},
 IM: 'Nu Instruments — "a Nu Plasma II MC-ICP-MS fitted with an enhanced sensitivity interface" [IM]'})
ov("Instrument Model", {
 BU: 'Neptune Plus [Bu sec 2]', CR: 'NEPTUNE ("Thermo Electron NEPTUNE") [Cr Table 1]',
 HO: 'Neptune "upgraded to Neptune Plus specifications" [Ho sec 2.3]',
 HU: 'Neptune Plus "with the addition of an OnTool booster" [Hu]',
 IM: 'Nu Plasma II [IM]', NI: 'Neptune [Ni sec A.3]', NOa: 'Neptune [No sec 3.1]',
 NOb: 'Nu Plasma [No sec 3.2]', PR: 'Neptune Plus [Pr Table 1]', SC: 'Neptune Plus [Sc]',
 VK: 'Neoma [vK, Methods]', BR: 'Neptune Plus [Br sec 4]', BAa: 'Neptune Plus [Ba]',
 BAb: 'Neptune Plus [Ba, Bulk Ti isotopes]'})
ov("ICP-MS Type", {i: 'Multi-collector sector-field ICP-MS [all columns state "multi-collector inductively coupled plasma mass spectrometer"]' for i in range(N)})
ov("Faraday Cup Array Configuration", {
 NOa: '"The Durham Neptune has a 9 Faraday collector array equipped with 10^11 Ω resistor amplifiers which allow a maximum beam of 50 V per channel" [No sec 3.1]',
 NI: 'Three collectors used [Ni sec A.3]'})
ov("Faraday Cup Amplifier Resistor Values", {
 HO: '10^10 Ω for 56Fe+; 10^11 Ω for 54Fe, 57Fe, 58Fe; 10^12 Ω for the 53Cr and 60Ni interference monitors [Ho sec 2.3]',
 NI: '"All three collectors were equipped with the 10^11 Ω amplifiers" [Ni sec A.3]',
 NOa: '10^11 Ω [No sec 3.1]',
 SC: '10^11 Ω for 90Zr–96Zr and 95Mo; 10^12 Ω for 99Ru and 101Ru [Sc, Mass Spectrometry]',
 VK: '10^11 Ω for 24Mg, 25Mg, 26Mg [vK, Methods]'})
ov("Faraday Cup Gain Calibration Method", {
 NOa: '"Instrument electronic baselines and amplifier gains were then measured, on peak with the line of sight valve closed"; "Although amplifier gains were measured at the start of each session the Virtual Amplifier was used in rotation mode to cancel out amplifier gains" [No sec 3.1]'})
ov("Mass Resolution Setting", {
 CR: '"High (entrance slit); Low (detector slit)" [Cr Table 1]',
 HO: 'Medium or high resolution — "the measurements were made on the flat-topped peak shoulder in either medium-resolution (MR) or high-resolution (HR) mode" [Ho sec 2.3]',
 NI: 'Low resolution [Ni sec A.3]',
 VK: 'Medium resolution, M/ΔM > 6,000 [vK, Methods]',
 BR: 'Measured "on the left \'shoulder\' of the peak to resolve the difference between 40Ar1H+ and 41K+" [Br sec 4]',
 BAa: 'High-mass-resolution slit for K; low-mass-resolution slit for Cu and Zn [Ba]',
 BAb: 'Medium mass resolution, R ≈ 6,600–7,000 (R = m/m0.95 − m0.05) [Ba, Bulk Ti isotopes]'})
ov("Nebulizer Type", {
 BU: 'Savillex C-Flow PFA nebulizer [Bu sec 2]',
 CR: 'PFA-50, Elemental Scientific, Inc. [Cr Table 1]',
 HO: 'Cyclonic glass spray chamber (wet) or ESI Apex Ω desolvating nebulizer (dry) [Ho sec 2.3]',
 IM: 'Cetac Aridus II desolvator nebulizer [IM]',
 NOa: 'ESI PFA-50 micro-flow nebuliser [No sec 3.1]', NOb: 'ESI PFA-50 low uptake nebuliser [No sec 3.4]',
 SC: 'PFA nebulizer with an Aridus II desolvating nebulizer system [Sc]',
 BR: 'Elemental Scientific APEX Omega desolvating nebulizer [Br sec 4]'})
ov("Spray Chamber Type and Cooling Temperature", {
 CR: 'SSI cyclonic spray dual chamber, Elemental Scientific, Inc.; cooling not stated [Cr Table 1]',
 HO: 'Cyclonic glass spray chamber for wet-plasma MR-mode work; cooling not stated [Ho sec 2.3]',
 NI: '"a dual cyclonic-Scott-type quartz spray chamber"; cooling not stated [Ni sec A.3]',
 NOa: 'Glass Expansion micro-cyclonic "Cinnabar" spray chamber; cooling not stated [No sec 3.1]',
 NOb: 'GE Cinnabar micro-cyclonic spray chamber [No sec 3.4]',
 BAa: 'Quartz glass dual cyclonic spray chamber for Cu and Zn; cooling not stated [Ba]'})
ov("Desolvation System", {
 BU: 'Cetac Aridus II [Bu sec 2]',
 CR: 'None — and deliberately: "passing solutions through a desolvating nebulizer to obtain dry plasma conditions is not viable for bulk analysis" [Cr sec 2.3]',
 HO: 'ESI Apex Ω for HR-mode dry plasma work, "with no auxiliary N2 flow"; none for MR-mode wet plasma [Ho sec 2.3]',
 IM: 'Cetac Aridus II — "Analyses were conducted in dry plasma mode" [IM]',
 NI: 'None — spray chamber introduction [Ni sec A.3]',
 NOa: 'None — "Although greater sensitivity could be attained using a desolvating nebuliser such systems have been shown to suffer severe memory problems for Os" [No sec 3.1]',
 NOb: 'None [No sec 3.4]',
 PR: 'APEX, used alongside the spray chamber as an alternative introduction system in different sessions [Pr sec 2.3]',
 SC: 'Aridus II [Sc, Mass Spectrometry]',
 VK: 'ESI Apex HF with an actively cooled membrane unit (Cr); ESI Apex Omega (Mg) [vK, Methods]',
 BR: 'Elemental Scientific APEX Omega [Br sec 4]',
 BAa: 'Elemental Scientific APEX Ω for K ("dry plasma technique"); none for Cu and Zn [Ba]'})
ov("Sample Uptake Rate", {
 BU: '~50 µl/min [Bu sec 2]', CR: '50 µL/min [Cr Table 1]', HO: '~100 µl/min [Ho sec 2.3]',
 NI: '100 µl/min [Ni sec A.3]', NOa: '~80 µl/min, free aspiration [No sec 3.1]',
 NOb: 'Not stated; ~6400 µl consumed over a ~16 min analysis [No sec 3.2]',
 PR: 'Peristaltic pump at 5 rpm [Pr Table 1]',
 SC: '~0.05 mL/min [Sc, Mass Spectrometry]',
 VK: '30 µl/min for Cr and for Mg [vK, Methods]'})

# ---------------------------------------------------------------- Group 4
ov("Analytical Mode", {i: 'Solution nebulisation (continuous)' for i in range(N)})
ov("RF Power", {CR: '~1150 W [Cr Table 1]', PR: '1200 W [Pr Table 1]',
 VK: 'Stated qualitatively — measured "at low radiofrequency power and sample gas inflow" to reduce gas-based interferences [vK, Methods]'})
ov("Coolant (Plasma) Gas Flow Rate", {CR: '~15 L/min Ar [Cr Table 1]', PR: '16 L/min [Pr Table 1]'})
ov("Auxiliary Gas Flow Rate", {CR: '~0.8 L/min Ar [Cr Table 1]', PR: '1.01 L/min [Pr Table 1]'})
ov("Nebulizer Gas Flow Rate", {CR: '~0.8–0.9 L/min Ar (sample gas) [Cr Table 1]', PR: '1.03 L/min (sample gas) [Pr Table 1]'})
ov("Make-up Gas Flow Rate", {
 HO: 'None — the Apex Ω was run "with no auxiliary N2 flow" [Ho sec 2.3]',
 VK: 'None — "The samples were measured without the use of an auxiliary gas to the introduction system to reduce gas-based interferences" [vK, Methods]'})
ov("Guard Electrode", {CR: '"Pt-guard electrode: On, grounded" [Cr Table 1]'})
ov("Plasma Thermal Mode", {
 CR: 'Wet plasma — solutions "introduced as a \'wet\' aerosol (in 2% HNO3) into the ICP torch via a cyclonic spray dual chamber"; dry plasma deliberately rejected as "not viable for bulk analysis" [Cr Fig. 1 caption, sec 2.3]',
 HO: 'Both, by mode — "either a cyclonic glass spray chamber (wet plasma, MR-mode, Pt cones) or an ESI Apex Ω desolvating nebulizer system (dry plasma, HR-mode, Ni cones)" [Ho sec 2.3]',
 IM: 'Dry plasma — "Analyses were conducted in dry plasma mode using a Cetac Aridus II desolvator nebulizer" [IM]',
 BAa: 'Dry plasma for K — "all K isotope analyses were undertaken using a \'dry plasma\' technique with the Elemental Scientific APEX Ω high-sensitivity desolvation system"; wet plasma for Cu and Zn via a quartz glass dual cyclonic spray chamber [Ba]'})
ov("Data Processing Software(s)", {
 NOa: 'Microsoft Excel — "Following analysis all intensity data was exported and re-processed offline using Excel" [No sec 3.1]',
 NOb: 'Online processing on the instrument — "Samples were processed on-line for W and Re interferences and instrumental mass bias" [No sec 3.2]',
 IM: 'Mathematica — "Data were reduced using a minimization approach implemented in Mathematica" [IM]'})
ov("Per-Analyte Calibration Strategy", {
 VK: 'One bracketing standard per analyte — IRMM-014 for Fe, SRM979 for Cr, DTS-2b for Mg [vK, Methods]',
 BAa: 'One bracketing standard per analyte — NIST-SRM 3141a for K, NIST-SRM 976 for Cu, JMC-Lyon for Zn; run concentrations also differ by analyte (200 ppb for K and Zn, 100 ppb for Cu) [Ba]',
 HU: 'One OL-REE series standard per REE, with separate cup configurations for Dy and Yb [Hu]'})
ov("Interface Cone Configuration", {
 CR: 'X-cones [Cr Table 1]', BU: 'Standard sample and (H) skimmer cones [Bu sec 2]',
 HO: 'H skimmer cones [Ho sec 2.3]', NI: 'Normal sampler and skimmer cones [Ni sec A.3]',
 PR: 'Sample cone Jet; skimmer cone H [Pr Table 1]',
 SC: '"Normal skimmer and sampler cones were utilized" [Sc, Mass Spectrometry]',
 VK: 'A Jet and X cone [vK, Methods]'})
ov("Sampler and Skimmer Cone Material", {
 CR: 'Ni [Cr Table 1]', BU: 'Ni [Bu sec 2]',
 HO: '"We used Ni or Pt sampler and H skimmer cones ... The main motivation for using Pt cones was an increase in sensitivity and a decrease in the frequency of cone cleaning" [Ho sec 2.3]',
 NI: 'Ni [Ni sec A.3]'})
ov("ICP Tuning", {
 NOa: '"At the start of each analytical session the Neptune was tuned for maximum sensitivity and optimal peak shape using an Os solution, either the UMd or DTM RMs, and the mass calibration was updated by peak-centering on the centre-cup mass 187Os" [No sec 3.1]',
 SC: '"Tuning was performed to minimize interferences of 40Ar2 16O+ and 40Ar2 14N+ on 96Zr+ and 94Zr+ and with it the on-peak background corrections" [Sc, Mass Spectrometry]',
 VK: 'Measured "at low radiofrequency power and sample gas inflow" deliberately, to reduce gas-based interferences [vK, Methods]'})
ov("Instrument Warm-up / Session Duration Limit", {
 NOa: '"Instrument electronic baselines and amplifier gains were then measured ... while the Neptune was allowed to warm up for half an hour" [No sec 3.1]'})
ov("Instrument Sensitivity", {
 BU: '~1.3 x 10^-10 A total ion beam for a ~100 ppb Mo solution at ~50 µl/min uptake [Bu sec 2]',
 HO: 'Typical 56Fe+ intensities 1.4 nA (wet plasma, MR) to 2 nA (dry plasma, HR) [Ho sec 2.3]',
 HU: '3.5–10 V for the most abundant isotope at 15–25 ppb (10 V for 140Ce, 4 V for 142Nd, 3.5 V for 152Sm) [Hu]',
 IM: '"The average instrumental sensitivity using this setup was around 572 V/ppm of total Zr" [IM]',
 NI: '~1–1.5 V for 85Rb at 15–25 ppb in low resolution [Ni sec A.3]',
 NOa: '"The sensitivity for Os with this set-up was approximately 50 V for a 1 µg ml-1 Os solution at a free-aspiration rate of around 80 µl min-1" [No sec 3.1]',
 SC: 'Total Zr ion beams 3.5–13 V at 30 ppb [Sc, Mass Spectrometry]',
 VK: 'Typical Mg signal intensities 80–90 V [vK, Methods]'})
ov("Analyte", {
 BU: 'Mo (and Ba by TIMS) [Bu sec 2]', CR: 'S [Cr title]', HO: 'Fe [Ho sec 2.3]',
 HU: 'The rare earth elements — La, Ce, Nd, Sm, Eu, Gd, Dy, Er, Yb and Y [Hu]',
 IM: 'Zr [IM]', NI: 'Rb [Ni sec A.3]', NOa: 'Os [No sec 2]', NOb: 'Os [No sec 2]',
 PR: 'Rb [Pr sec 2.3]', SC: 'Zr [Sc]', VK: 'Fe, Cr and Mg [vK, Methods]', BR: 'K [Br sec 4]',
 BAa: 'K, Cu and Zn [Ba]', BAb: 'Ti [Ba, Bulk Ti isotopes]'})
ov("Reported Variables and Units", {
 BU: 'εiMo relative to the Alfa Aesar solution standard, εiMo = [(iMo/96Mo)sample/(iMo/96Mo)standard − 1] x 10^4 [Bu sec 2]',
 CR: 'δ34S and δ33S in permil vs V-CDT [Cr Abstract, sec 2.1]',
 HO: 'µ-notation Fe isotope ratios relative to IRMM-524a [Ho sec 2.3]',
 HU: 'Mass-dependent REE isotopic fractionation relative to the OL-REE standards, in delta notation [Hu]',
 IM: 'δ9x/90ZrNIST in permil — δ91/90Zr, δ92/90Zr, δ94/90Zr and δ96/90Zr [IM Table 1]',
 NI: 'δ87Rb in permil relative to NIST SRM984 [Ni sec A.3]',
 NOa: '187Os/188Os, 186Os/188Os and 184Os/188Os ratios [No sec 2]',
 NOb: '187Os/188Os, 186Os/188Os and 184Os/188Os ratios [No sec 2]',
 PR: 'δ87Rb in permil = [(87Rb/85Rb)sample/(87Rb/85Rb)standard − 1] x 1000 [Pr Eq. 1]',
 SC: 'ε91Zr, ε92Zr and ε96Zr relative to NIST SRM 3169 [Sc Table 1]',
 VK: 'µ-notation Fe relative to IRMM-014, Cr relative to SRM979, Mg relative to DTS-2b [vK, Methods]',
 BR: 'δ41K in permil relative to NIST SRM 3141a [Br sec 4]',
 BAa: 'δ41K, δ65Cu and δ66Zn in permil, each defined explicitly against its bracketing standard [Ba]',
 BAb: 'ε50Ti [Ba, Bulk Ti isotopes]'})
ov("Collector Configuration", {
 CR: '32S(L3), 33S(C), 34S(H3) [Cr Table 1]',
 HO: '54Fe, 56Fe, 57Fe, 58Fe in static mode, with 53Cr and 60Ni monitored simultaneously [Ho sec 2.3]',
 HU: 'Static mode for most REEs; a subconfiguration for Dy and Yb to monitor isobaric interferences [Hu]',
 IM: 'Masses 90, 91, 92, 93, 94, 95, 96 and 98 "measured in static mode at 0.5 amu spacing in the Nu Plasma II collector block" [IM]',
 NI: '85Rb, 87Rb+87Sr and 88Sr on three collectors, 88Sr on H1 [Ni sec A.3]',
 NOa: 'L4=182W, L3=184Os, L2=185Re, L1=186Os, Ax=187Os, H1=188Os, H2=189Os, H3=190Os, H4=192Os, with 184W, 186W and 187Re as interference monitors [No Table 2a]',
 NOb: 'Two-sequence static multi-collection [No sec 3.2, Table 2b]',
 PR: 'L2=84Sr, L1=85Rb, C=86Sr, H1=87Rb+87Sr, H2=88Sr [Pr Table 2]',
 SC: '90Zr–96Zr and 95Mo on 10^11 Ω cups; 99Ru and 101Ru on 10^12 Ω cups [Sc, Mass Spectrometry]',
 VK: '49Ti, 51V, 56Fe alongside 50Cr, 52Cr, 53Cr, 54Cr; 24Mg, 25Mg, 26Mg [vK, Methods]',
 BAb: '"Titanium isotopes were collected in two cup configurations" [Ba, Bulk Ti isotopes]'})
ov("Number of Blocks per Measurement", {
 NOa: '9 blocks [No sec 3.1]', NOb: '1 block [No sec 3.2]',
 NI: 'A single block [Ni sec A.4]', PR: 'Blocks of 20 cycles [Pr sec 2.3]'})
ov("Number of Cycles per Block", {
 BU: '100 isotope ratio measurements, preceded by 40 baseline integrations [Bu sec 2]',
 CR: '20 cycles [Cr Table 1]', HO: '25 (HR) or 50 (MR) cycles [Ho sec 2.3]',
 HU: '40 cycles in the main configuration; the subconfiguration measured twice [Hu]',
 IM: '50 cycles [IM]', NI: '25 cycles [Ni sec A.4]',
 NOa: '5 cycles per block [No sec 3.1]', NOb: '50 cycles [No sec 3.2]',
 PR: '20 cycles [Pr sec 2.3]', SC: '60 ratios [Sc, Mass Spectrometry]',
 VK: 'Fe 200 cycles; Cr 100 cycles; Mg 100 cycles [vK, Methods]',
 BR: '"Each sample was measured approximately 20 times" [Br sec 4]',
 BAb: '40 cycles [Ba, Bulk Ti isotopes]'})
ov("Integration Time per Cycle", {
 BU: '8.4 s [Bu sec 2]', CR: '8.5 s [Cr Table 1]', HO: '8.369 s [Ho sec 2.3]',
 HU: '4.142 s in the subconfiguration [Hu]', IM: '5 s [IM]', NI: '4.194 s [Ni sec A.4]',
 NOa: '4 s [No sec 3.1]', NOb: '8 s for sequence 1 and 4 s for sequence 2 [No sec 3.2]',
 PR: '8.389 s [Pr sec 2.3]', SC: '4.2 s [Sc, Mass Spectrometry]',
 VK: 'Fe 8.3 s; Cr 8.3 s; Mg 16.7 s [vK, Methods]',
 BAb: '4 s [Ba, Bulk Ti isotopes]'})
ov("Baseline Measurement Approach", {
 BU: '40 on-peak-zero baseline integrations of 8.4 s preceding each measurement [Bu sec 2]',
 HO: '"On peak zero intensities from a blank solution measured at the beginning of each sequence were subtracted from all individual measurements" [Ho sec 2.3]',
 IM: '"On-peak-zero correction was done using the mean acid blank intensities before data processing to account for blank contribution as well as any \'memory\' effects from the Aridus II sample introduction system during the run" [IM]',
 NOa: 'Electronic baselines "measured, on peak with the line of sight valve closed"; peak centering and baselines "were not carried out at the start of each analysis to reduce measurement time and conserve sample but were repeated several times during an analytical session" [No sec 3.1]',
 SC: 'Both: "Electronic baselines were measured for 30 s prior to each analysis. An on-peak background correction was performed." [Sc, Mass Spectrometry]',
 VK: 'On-peak baseline — Fe 25 x 16.7 s; Cr 75 s; Mg 25 x 16.7 s [vK, Methods]'})
ov("Wash Time Between Samples", {
 CR: '2 min for solution work (4 min for laser) [Cr Table 1]', HO: '210 s [Ho sec 2.3]',
 HU: '300 s rinsing between bracketed measurements [Hu]',
 NI: '60 s wash in 0.45 M HNO3, with a 90 s take-up time [Ni sec A.4]',
 NOa: '"Teflon-distilled (TD) 3 or 5 mol/l HCl acid was aspirated between analyses until the 192Os beam decreased to acceptable background levels"; not required in single-RM sessions [No sec 3.1]',
 NOb: 'TD 3 mol/l HCl aspirated between analyses until the Os beam decreased to acceptable background levels [No sec 3.2]'})
ov("Analysis Sequence", {
 BU: 'Bracketing runs of the Alfa Aesar solution standard; BHVO-2 digestions "analyzed together with each set of samples" [Bu sec 2]',
 HO: '"Sample analyses were bracketed by measurements of the reference material IRMM-524a" [Ho sec 2.3]',
 HU: 'Standard-sample bracketing — "On average, LREEs were measured nine times bracketed by OL-REE isotope standard spaced apart by 300-s rinsing time" [Hu]',
 IM: '"Each sample measurement was individually bracketed by measurements of the ZrNIST solution spiked at the same level as our samples and matched in concentration (60 ng/g) as well as acid matrix"; each measurement preceded by an acid blank [IM]',
 NI: 'Standard-sample bracketing [Ni sec A.3]',
 PR: 'Standard-sample bracketing; an external pure Rb ICP-MS solution "analyzed as an external standard during each analytical session to monitor the reproducibility" [Pr sec 2.3]',
 SC: 'Standard sample bracketing against NIST SRM 3169; "The Zr standard material NIST SRM 3169 was analyzed in each session" [Sc]',
 VK: 'Standard-sample bracketing, "ten individual standard-bracketed sample analyses" per reported value [vK, Methods]',
 BR: 'Standard-sample bracketing against NIST SRM 3141a; BHVO-2 measured alongside the samples [Br sec 4]',
 BAa: 'Standard-sample bracketing for all analyses; BHVO-2 "analysed alongside all sample analyses" [Ba]'})
ov("Internal Standard Element", {i: 'N/A — mass bias corrected by standard-sample bracketing, internal normalization or a double spike rather than by an added internal standard element' for i in range(N)})
ov("Internal Standard Concentration", {i: 'N/A — no added internal standard element' for i in range(N)})
ov("Oxide Production Method and Threshold", {
 SC: 'Argide and Ar-Ar-oxide interferences on 94Zr and 96Zr minimised by tuning; no numeric threshold stated [Sc, Mass Spectrometry]'})
ov("Peak Flatness Method and Threshold", {
 NOa: 'Tuned for "optimal peak shape"; mass calibration updated by peak-centering on the centre-cup mass 187Os. No numeric threshold stated [No sec 3.1]',
 HO: 'Measurements made "on the flat-topped peak shoulder" in MR or HR mode; no numeric threshold stated [Ho sec 2.3]',
 BR: 'Measurements taken "on the left \'shoulder\' of the peak"; no numeric threshold stated [Br sec 4]'})

# ---------------------------------------------------------------- Group 5
ov("Mass Bias Correction Strategy", {
 BU: 'Internal normalization to 98Mo/96Mo = 1.453173 using the exponential law, plus bracketing against the Alfa Aesar standard [Bu sec 2]',
 CR: 'Standard-sample bracketing against matrix-matched purified S solutions [Cr sec 2.1]',
 HO: 'Internal normalization to 57Fe/56Fe = 0.023095 or 57Fe/54Fe = 0.362549 using the exponential law, with IRMM-524a bracketing [Ho sec 2.3]',
 HU: 'Standard-sample bracketing against OL-REE standards — "SSB is advantageous over the double-spike approach because one can distinguish mass-dependent fractionation from isotopic anomalies" [Hu]',
 IM: '91Zr-96Zr double spike inversion, with ZrNIST bracketing after inversion [IM]',
 NI: 'Standard-sample bracketing against NIST SRM984 [Ni sec A.3]',
 NOa: 'Instrumental mass bias correction applied offline in Excel alongside abundance sensitivity and W/Re interference corrections [No sec 3.1]',
 NOb: '"Samples were processed on-line for W and Re interferences and instrumental mass bias" [No sec 3.2]',
 PR: '"Measurements were made using standard-sample bracketing to correct for instrumental mass bias" [Pr sec 2.3]',
 SC: 'Internal normalization to 94Zr/90Zr = 0.3381 using the exponential law; an initial Mo correction uses a mass bias relative to 91Zr/90Zr = 0.21798; results reported by standard sample bracketing to NIST SRM 3169 [Sc, Mass Spectrometry]',
 VK: 'Standard-sample bracketing [vK, Methods]',
 BR: 'Standard-sample bracketing against NIST SRM 3141a [Br sec 4]',
 BAa: '"To correct for instrument mass bias, the sample–standard bracketing technique was used for all analyses" [Ba]',
 BAb: 'Standard-sample bracketing [Ba, Bulk Ti isotopes]'})
ov("Mass Fractionation Law", {
 BU: 'Exponential law [Bu sec 2]', HO: 'Exponential law [Ho sec 2.3]',
 SC: 'Exponential law [Sc, Mass Spectrometry]',
 IM: 'Power-law form used in the double-spike inversion equation [IM]'})
ov("Double-Spike Isotope Pair", {
 IM: '91Zr-96Zr [IM sec Zr stable isotope analyses]',
 **{i: 'N/A — no double spike used' for i in range(N) if i != IM}})
ov("Double-Spike Mixing Ratio", {
 IM: '0.43:0.57 spike-to-sample Zr mass ratio, described as optimal [IM]',
 **{i: 'N/A — no double spike used' for i in range(N) if i != IM}})
ov("Double-Spike Inversion Algorithm", {
 IM: '"a minimization approach implemented in Mathematica, taking into account all ratios (i.e., 91/90Zr, 92/90Zr, 94/90Zr, and 96/90Zr) with different weighs being assigned to each based on their associated uncertainty", cross-checked against two exact three-ratio solutions [IM]',
 **{i: 'N/A — no double spike used' for i in range(N) if i != IM}})
ov("Internal Normalization Element and Isotope Ratio", {
 BU: '98Mo/96Mo = 1.453173 [Bu sec 2]',
 HO: '57Fe/56Fe = 0.023095 or 57Fe/54Fe = 0.362549, the certified ratios of IRMM-014 [Ho sec 2.3]',
 SC: '94Zr/90Zr = 0.3381 (Minster & Ricard 1981) [Sc, Mass Spectrometry]',
 NI: 'N/A — Rb has two stable isotopes, so internal normalization is not possible; bracketing used instead [Ni sec A.3]',
 PR: 'N/A — Rb has two stable isotopes; bracketing used instead [Pr sec 2.3]'})
ov("Isotope Ratio Reported", {
 BU: 'iMo/96Mo [Bu sec 2]', CR: '34S/32S and 33S/32S [Cr Abstract]',
 HO: 'Fe isotope ratios relative to IRMM-524a [Ho sec 2.3]',
 IM: '91/90Zr, 92/90Zr, 94/90Zr, 96/90Zr [IM Table 1]',
 NI: '87Rb/85Rb [Ni sec A.3]', NOa: '187Os/188Os, 186Os/188Os, 184Os/188Os [No sec 2]',
 NOb: '187Os/188Os, 186Os/188Os, 184Os/188Os [No sec 2]', PR: '87Rb/85Rb [Pr Eq. 1]',
 SC: '91Zr/90Zr, 92Zr/90Zr, 96Zr/90Zr [Sc]',
 BAa: '41K/39K, 65Cu/63Cu, 66Zn/64Zn [Ba]', BAb: '50Ti [Ba, Bulk Ti isotopes]'})
ov("delta or epsilon Value Reference Standard", {
 BU: 'Alfa Aesar solution standard [Bu sec 2]', CR: 'V-CDT scale via IAEA-S-1, S-2, S-4 and NBS-123 [Cr sec 2.1]',
 HO: 'IRMM-524a, "that has an identical isotopic composition to IRMM-014" [Ho sec 2.3]',
 HU: 'OL-REE series, prepared in-house from high-purity ESPI oxide powder [Hu]',
 IM: 'ZrNIST [IM]', NI: 'NIST SRM984 [Ni sec A.3]',
 PR: 'NIST SRM984 RbCl; the basalt geostandard BCR-2 used as an alternative bracketing standard in some sessions [Pr sec 2.3]',
 SC: 'NIST SRM 3169 [Sc]', VK: 'IRMM-014 (Fe), SRM979 (Cr), DTS-2b (Mg) [vK, Methods]',
 BR: 'NIST SRM 3141a [Br sec 4]',
 BAa: 'NIST-SRM 3141a (K), NIST-SRM 976 (Cu), JMC-Lyon (Zn) [Ba]'})
ov("Blank / Background Correction Method", {
 BU: 'On-peak-zero baseline integrations subtracted [Bu sec 2]',
 HO: 'On-peak zero from a blank solution subtracted from all measurements [Ho sec 2.3]',
 IM: 'On-peak-zero correction using mean acid blank intensities [IM]',
 SC: '"An on-peak background correction was performed"; background corrections averaged 0.3, 2 and 98 ppm for 91Zr/90Zr, 92Zr/90Zr and 96Zr/90Zr [Sc, Mass Spectrometry]',
 VK: 'On-peak baseline measurement preceding each analysis [vK, Methods]',
 NOa: 'Corrections applied offline for abundance sensitivity, W and Re atomic interferences and instrumental mass bias [No sec 3.1]'})
ov("Spike / Outlier Filtering Approach", {
 PR: '"any ratio outside 2σ was discarded" [Pr sec 2.3]'})
ov("Isobaric Interference Corrections Applied", {
 BU: 'Yes — Zr and Ru on Mo masses [Bu sec 2]',
 CR: 'Yes — the paper is built around correcting isobaric interferences and mass bias for S [Cr Abstract]',
 HO: 'Yes — 54Cr on 54Fe and 58Ni on 58Fe, plus argide molecular interferences [Ho sec 2.3]',
 HU: 'Yes — Er on Dy, and neighbouring-element isotopes generally [Hu]',
 IM: 'Yes — Mo on Zr [IM]', NI: 'Yes — 87Sr on 87Rb [Ni sec A.3]',
 NOa: 'Yes — W and Re on Os [No Table 2a, sec 3.6]', NOb: 'Yes — W and Re on Os [No sec 3.2]',
 PR: 'Yes — 87Sr on 87Rb, Sr isotopes monitored [Pr Table 2, sec 2.2]',
 SC: 'Yes — Mo and Ru on Zr, plus Fe- and Cr-argides and Ar-Ar-oxides [Sc]',
 VK: 'Yes — 49Ti, 51V and 56Fe monitored to correct interferences on Cr [vK, Methods]',
 BR: 'Yes — 40Ar1H+ on 41K+, resolved by peak-shoulder measurement [Br sec 4]',
 BAa: 'Yes — ArH+ on K, lowered by dry plasma and a high-resolution slit [Ba]'})
ov("Interfering Species", {
 BU: 'Zr and Ru, monitored on 91Zr and 99Ru [Bu sec 2]',
 HO: '54Cr on 54Fe, 58Ni on 58Fe, and argide ions 40Ar13C+, 40Ar14N+, 40Ar16O+, 40Ar16O1H+ and 40Ar18O+ [Ho sec 2.3]',
 HU: '162Er and 164Er on 162Dy and 164Dy [Hu]',
 IM: 'Mo, monitored on masses 95 and 98 [IM]',
 NI: '87Sr on 87Rb, monitored at 88Sr [Ni sec A.3]',
 NOa: '182W/184W/186W and 185Re/187Re [No Table 2a]', NOb: 'W and Re [No sec 3.2]',
 PR: '87Sr on 87Rb; also double-charged Er and Yb isotopes [Pr sec 2.2]',
 SC: '95Mo, 99Ru, 101Ru; 40Ar2 16O+ and 40Ar2 14N+ on 96Zr+ and 94Zr+ [Sc]',
 VK: '49Ti, 51V, 56Fe on the Cr masses [vK, Methods]',
 BR: '40Ar1H+ on 41K+ [Br sec 4]', BAa: 'ArH+ on K [Ba]'})
ov("Interference Correction Method", {
 BU: 'Monitoring 91Zr and 99Ru [Bu sec 2]',
 HO: 'Simultaneous monitoring of 53Cr and 60Ni on 10^12 Ω amplifiers; argides resolved by measuring on the flat-topped peak shoulder in MR or HR mode [Ho sec 2.3]',
 HU: 'Subconfiguration scaling — 166Er measured only in the subconfiguration, 163Dy in both; the 166Er/163Dy ratio is scaled onto the main configuration and multiplied by 162Er/166Er and 164Er/166Er to subtract the interferences [Hu]',
 IM: 'A doping calibration: "Offset δ94/90ZrNIST = −63.4 · x" where x is the total Mo/Zr atomic ratio; the reported data are uncorrected for residual Mo [IM]',
 NI: 'Correction assuming a constant terrestrial 87Sr/88Sr = 0.085, with a sensitivity test over 0.0835–0.0885 showing a maximum shift of 0.008 permil [Ni sec A.3]',
 NOa: 'Monitor isotopes 184W, 186W and 187Re; abundance sensitivity determined by scanning the low mass tail of a 30 V 192Os beam using the SEM and fitting a curve to the tail — 0.5 to 1 ppm in the Os mass range [No sec 3.1]',
 NOb: 'Online W and Re correction; abundance sensitivity greater than 1 ppm "since the analyser pressure was higher at ~2 x 10^-8 mbar" [No sec 3.2]',
 SC: 'Mo and Ru corrections calculated from the signals on mass 95, 99 and 101, with an initial Mo correction using a mass bias relative to 91Zr/90Zr = 0.21798 [Sc, Mass Spectrometry]',
 VK: 'Simultaneous monitoring of 49Ti, 51V and 56Fe [vK, Methods]'})
ov("Memory Effect Mitigation", {
 CR: 'Wash-out 2 min for solution [Cr Table 1]',
 IM: 'On-peak-zero acid blank before each sample "to account for blank contribution as well as any \'memory\' effects from the Aridus II sample introduction system during the run" [IM]',
 NOa: 'Desolvating nebulisers deliberately avoided because of "severe memory problems for Os"; ESI PFA-50 low-uptake nebuliser and GE Cinnabar micro-cyclonic spray chamber chosen "in the hope these would reduce the long Os washout times and poor memory usually associated with solution introduction of Os"; wash acid aspirated until the 192Os beam fell to background — a 99.99% decrease reached after 220 s for DTM [No sec 3.1, 3.4]',
 NOb: 'TD 3 mol/l HCl aspirated between analyses until the Os beam decreased to acceptable background levels [No sec 3.2]',
 HO: '210 s washout between all measurements [Ho sec 2.3]',
 NI: '60 s wash in 0.45 M HNO3 [Ni sec A.4]'})
ov("Uncertainty Level", {
 BU: '2 s.d. for external reproducibility (n = 24 for Mo, n = 14 for Ba) [Bu sec 2]',
 CR: '"external reproducibility is reported at the 2σ error level"; long-term reproducibility "typically 0.20‰ and 0.45‰ (2σ) for solution and laser" [Cr sec 3, Abstract]',
 HU: 'Not stated in the section read [Hu]',
 IM: '"the external reproducibility (at 2σ) of the spiked ZrNIST measurements from each run, which in all cases was similar in magnitude or slightly larger than the internal uncertainty determined from counting statistics" [IM]',
 NOa: '2SD for short- and long-term reproducibility; within-run errors as "2 standard errors of the mean (2SE = 2SD/n^0.5; where n = 45 for the Neptune analyses" [No sec 3]',
 NOb: '2SD and 2SE, with n = 50 for the Nu Plasma analyses [No sec 3]',
 PR: '"the 2 standard error (2se) is reported unless stated otherwise"; for samples analysed fewer than 3 times, "the largest 2 se reported for a sample analyzed multiple times has been used" [Pr sec 2.3]',
 SC: 'Both quoted: "external precision expressed as 2 standard deviations (2SD)" and 2SE per analysis [Sc, Table 1, RESULTS]',
 VK: '"the mean and 2 x standard error (SE) of ten individual standard-bracketed sample analyses" [vK, Methods]',
 BR: 'Stated as ± values on δ41K without an explicit convention in the section read [Br sec 4]',
 BAa: '2 s.d. [Ba]', BAb: '2 s.d. [Ba, Bulk Ti isotopes]'})
ov("Uncertainty Propagation Method", {
 PR: '"Errors are determined from repeated measurements" [Pr sec 2.3]',
 IM: 'External reproducibility of the spiked ZrNIST measurements from each run adopted per determination, compared against internal counting-statistics uncertainty [IM]'})
ov("Isotope Dilution Data Reduction Method", {
 IM: 'Double-spike inversion, Rmeas = [p·RSpike + (1−p)·RStd·(Mx/Mn)^α]·(Mx/Mi)^β, solved by weighted minimisation over four ratios [IM]',
 **{i: 'N/A — no isotope dilution applied' for i in range(N) if i != IM}})
ov("Procedural Blank Level", {
 BU: '"Total procedural blanks were between 0.7 and 1.2 ng and thus negligible, given that several hundred ng of Mo were analyzed for each sample" [Bu sec 2]',
 CR: '"The procedural blank, resulting from chemical processing and purification is ~0.05% (~0.25 µg per 500 µg S used for column chemistry)" [Cr sec 2.2]',
 HO: '"the total procedural blank is ~70 ng and thus negligible considering that 1-2 mg Fe was purified for each sample" [Ho sec 2.2]',
 IM: '"The total mass of non-radiogenic Pb measured in our FC-1 zircon and baddeleyite fractions is indistinguishable from the range of Pb determined in total procedural blanks" [IM]',
 NI: '"The Rb blank of the procedure (digestion and column chemistry) is ~0.14 ng, which accounts for less than 0.5% of total Rb from a typical sample (40 ng)" [Ni sec A.2]',
 SC: '"Total procedural blanks prepared together with Tarda and Tagish Lake contained 0.08 and 0.24 ng Zr, while total blanks treated alongside Ivuna were 0.09 and 0.13 ng Zr" [Sc EXPERIMENTAL]',
 BAb: '"The total procedural blank for Ti was 3.7 ng, resulting in a maximum blank contribution of 0.18% for Ti" [Ba, Bulk Ti isotopes]'})
ov("Analysis Inclusion and Rejection Criteria", {
 BU: 'Partially — "For samples analyzed several times, reported values represent the mean of pooled solution replicates" [Bu sec 2]. No acceptance or rejection rule stated',
 HU: 'Partially — "On average, LREEs were measured nine times"; replicate matrix cuts were measured but "are not used, however, for data interpretation to avoid unnecessary influence of stable isotopic fractionation potentially induced by Mo chemistry" — an explicit exclusion, on chemical rather than statistical grounds [Hu]',
 IM: 'Partially — Table 1 records "Number of times the same purified Zr solution was measured independently in the MC-ICP-MS" and "Reported values are weighted means of all replicate" analyses [IM Table 1 footnotes]. No rejection rule stated',
 NOa: 'Partially — n = 45 per analysis [No sec 3]. No rejection rule stated',
 NOb: 'Partially — n = 50 per analysis [No sec 3]. No rejection rule stated',
 PR: '"any ratio outside 2σ was discarded" — an explicit rejection rule, applied within a measurement. Reported values are "averages of repeated measurements of each sample when multiple analyses were possible" [Pr sec 2.3]',
 SC: 'Partially — n stated per reference material (n = 13–99 for terrestrial RMs over 10 months; n = 17–38 for eucrites and Colony; n = 32 and n = 37 for standard sessions) [Sc Table 1, RESULTS]. No rejection rule stated',
 VK: 'Partially — "the mean ... of ten individual standard-bracketed sample analyses"; "Samples were typically analysed two to four times" [vK, Methods]. No rejection rule stated',
 BR: 'Partially — "Each sample was measured approximately 20 times" [Br sec 4]. No rejection rule stated'})
ov("Constants and Reference Values Used", {
 BU: '98Mo/96Mo = 1.453173 for internal normalization; 134Ba/136Ba = 0.3078 (Carlson et al. 2007) for the TIMS half [Bu sec 2]',
 HO: '57Fe/56Fe = 0.023095 and 57Fe/54Fe = 0.362549, "the certified ratios of IRMM-014" (Craddock and Dauphas, 2010) [Ho sec 2.3]',
 IM: '238U/235U = 137.818 (45), 18O/16O = 0.00205 (44), and α = 0.18 ± 0.02%/amu from repeat NBS-981 analyses; U decay constants of (47); Th/U[magma] = 2.8 ± 1.0 for the initial 230Th disequilibrium correction [IM sec U-Pb]',
 NI: '87Sr/88Sr = 0.085, "which is the terrestrial Sr ratio", used for the 87Sr interference correction; sensitivity tested at 0.0835 and 0.0885 [Ni sec A.3]',
 SC: '94Zr/90Zr = 0.3381 and 91Zr/90Zr = 0.21798, both Minster & Ricard (1981) [Sc, Mass Spectrometry]'})

# ---------------------------------------------------------------- Group 6
ov("Primary Calibration Standard Name", {
 BU: 'Alfa Aesar Mo solution standard [Bu sec 2]',
 CR: 'In-house S_Alfa and S_Spex 20 ppm S solutions, calibrated against IAEA-S-1, S-2, S-4 and NBS-123 [Cr sec 2.1]',
 HO: 'IRMM-524a [Ho sec 2.3]', HU: 'OL-REE series [Hu]', IM: 'ZrNIST [IM]',
 NI: 'NIST SRM984 [Ni sec A.3]',
 NOa: 'UMd, DTM, LOsST and DROsS Os reference materials [No sec 3]',
 NOb: 'DTM and LOsST [No sec 3]',
 PR: 'NIST SRM984 RbCl; BCR-2 as an alternative bracketing standard in some sessions [Pr sec 2.3]',
 SC: 'NIST SRM 3169 [Sc]', VK: 'IRMM-014, SRM979, DTS-2b [vK, Methods]',
 BR: 'NIST SRM 3141a [Br sec 4]',
 BAa: 'NIST-SRM 3141a, NIST-SRM 976, JMC-Lyon [Ba]'})
ov("Calibration Standard Measurement Frequency", {
 IM: 'Every sample — "Each sample measurement was individually bracketed" [IM]',
 HU: 'Every sample, spaced by 300 s rinsing [Hu]',
 SC: 'Each session — "The Zr standard material NIST SRM 3169 was analyzed in each session" [Sc]',
 PR: 'Every sample (bracketing), plus an external pure Rb solution "during each analytical session" [Pr sec 2.3]',
 BR: 'Every sample (bracketing) [Br sec 4]'})
ov("Secondary Reference Materials", {
 BU: 'BHVO-2, "several digestions of which were processed through the full analytical protocol and analyzed together with each set of samples" [Bu sec 2]',
 CR: 'Sch-M-2 anhydrite mineral standard; geological reference samples with known isotope compositions [Cr sec 2.1]',
 HO: 'BHVO-2 and BCR-2 [Ho sec 2.1]',
 NI: 'BHVO-2, BCR-2, BE-N, W-2, AGV-2, GSR-1, GS-N, G-A, G-3; DTS-2b and PCC-1 synthetic mixes; Allende [Ni sec A.4]',
 SC: 'BHVO-2, BCR-2, AGV-1, SCo-1; eucrites Bouvante and Bereba; CO chondrite Colony [Sc RESULTS]',
 VK: 'BHVO2 and DTS-2b, "processed alongside the samples" [vK, Methods]',
 BR: 'BHVO-2 [Br sec 4]', BAa: 'BHVO-2 [Ba]',
 PR: 'BCR-2, AGV-2, BHVO-2, GS-N and other terrestrial rocks [Pr sec 2.1]'})
ov("In-Run Isotope Ratio Reproducibility and Assessment Method", {
 NOa: 'Within-run errors quoted as 2SE of the mean, 2SE = 2SD/n^0.5 with n = 45 [No sec 3]',
 NOb: 'Within-run errors quoted as 2SE of the mean with n = 50 [No sec 3]',
 IM: 'Internal uncertainty determined from counting statistics, compared against external reproducibility [IM]'})
ov("Between-Session Reproducibility and Assessment Method", {
 BU: 'External reproducibility from repeated BHVO-2 measurements: ±0.14 for ε97Mo to ±0.39 for ε92Mo (2 s.d., n = 24); Ba ±0.13 for ε135Ba to ±0.31 for ε138Ba (2 s.d., n = 14) [Bu sec 2]',
 CR: '"Long-term reproducibility of S isotope compositions is typically 0.20‰ and 0.45‰ (2σ) for solution and laser"; long-term reproducibility of in-house solution standards within ±0.2‰ [Cr Abstract, Fig. 4]',
 PR: '"the long-term reproducibility was ±0.01‰ (n = 40)" from a pure Rb ICP-MS solution run as an external standard each session [Pr sec 2.3]',
 SC: 'Terrestrial RMs measured over 10 months (n = 13–99) give average 2SD of 0.3, 0.2 and 1.0 for ε91Zr, ε92Zr and ε96Zr; "The external precision estimated from the geological sample measurements integrates the uncertainty introduced by the chemical separation procedure and mass spectrometry" [Sc RESULTS]',
 IM: 'External reproducibility at 2σ of the spiked ZrNIST measurements from each run [IM]'})
ov("Analytical Accuracy and Assessment Method", {
 BU: '"The εiMo values obtained for BHVO-2 are indistinguishable from the Alfa Aesar standard, demonstrating that the Mo isotopic data are accurate" [Bu sec 2]',
 CR: 'Assessed against IAEA and NBS reference materials on the V-CDT scale and against geological reference samples with known compositions [Cr sec 2.1]',
 NI: 'NIST SRM984 treated as a sample, plus synthetic DTS-2b+SRM984 and PCC-1+SRM984 mixes, "gave δ87Rb values of zero within error"; geostandards and Allende "yielded reproducible results that agree with literature data" [Ni sec A.4]',
 PR: 'An aliquot of SRM984 passed through the full chemistry gave δ87Rb = 0.00 ± 0.03‰, "confirming that no isotope fractionation is caused by the Rb purification procedure"; Allende duplicate splits agreed at 0.12 ± 0.02‰ and 0.14 ± 0.04‰ [Pr sec 2.3]',
 SC: 'Terrestrial and meteorite reference materials measured repeatedly to verify data quality; doping tests with Ti, V, Cr, Mo, Hf and W showed "the observed trace levels have no effect on the accuracy of the Zr isotope data" [Sc]',
 VK: 'BHVO2 and DTS-2b processed alongside the samples [vK, Methods]',
 BR: '"The average d41K value for BHVO-2 was −0.448 ± 0.027‰ which is within error of its previously reported values, for example, −0.46 ± 0.09‰ (Wang et al., 2021)" [Br sec 4]',
 BAa: '"To monitor data quality, the geostandard BHVO-2 was analysed alongside all sample analyses" [Ba]',
 BAb: 'Reproducibility verified against measurements made "under conditions similar to the methods used", quoted as ±0.16 and ±0.26 ε50Ti (2 s.d.) [Ba, Bulk Ti isotopes]',
 HU: 'Assessed in a dedicated "Assessment of data accuracy" section, using replicate matrix cuts and a processed geostandard [Hu]'})

# ---------------------------------------------------------------- build
rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))
out = [["Metadata Item"] + COLS]
groups = miss = filled = 0
for r in rows[1:]:
    if not r or not r[0].strip():
        out.append([""] * (N + 1)); continue
    name = r[0]
    if name[0].isdigit() and not r[2].strip():
        out.append([name] + ["N"] * N); groups += 1; continue
    d = OV.get(name, {})
    cells = [d.get(i, "N") for i in range(N)]
    filled += sum(1 for c in cells if c not in ("N",) and not c.startswith("N/A"))
    if not d: miss += 1
    out.append([name] + cells)

if "--apply" in sys.argv:
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(out)
    print("wrote", OUT)
content = sum(1 for r in out[1:] if r[0] and not r[0][0].isdigit())
print(f"{content} content fields x {N} columns = {content*N} cells")
print(f"  attested/partial : {filled}")
print(f"  fields with no extraction in any column: {miss}")
