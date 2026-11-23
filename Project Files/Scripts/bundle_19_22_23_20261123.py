#!/usr/bin/env python3
"""Issues #19, #22, #23 in one bump of all 16 TAPPs.

    python3 "Project Files/Scripts/bundle_19_22_23_20261123.py" [--apply]

#19 (SMR confirmed option 2, 2026-11-23). The 83 "Group N" references in Column B (82) and Purpose (1)
name the section and keep the number ("Procedure Identification (Group 1)"), or name the field where one
field is meant ("Mass Resolution Setting, in Instrument & Software (Group 3)").

#22 (revision 2, agreed by SMR 2026-11-23; analysis/Standards_Domain_Proposal_2026-11-19.md). One list of
standards, per-role assignments:
  * `Secondary Reference Materials` -> `Reference Materials`, still `defines: standard`, now every
    standard used, each once. Its literature cells become the union of the old secondary list and the
    standards named by the calibration, interference and delta fields; every old member id is kept, so
    the statistics cells keyed `standard x reported property` still resolve.
  * New, keyed `standard`: Reference Material Type, Reference Material Identifier, Reference Value
    Source. New, keyed `standard x reported property`: Reference Value, Reference Value Uncertainty,
    Reference Value Uncertainty Basis (RD 2026-11-23: three fields, not one formatted cell).
  * `Primary Calibration Standard Name` -> `Calibration Standard` (key unchanged); its value names an
    entry in Reference Materials. New `Quality-Control Standards`, keyed `target material x target
    species`, takes the secondary role; its cells carry the old secondary lists.
  * TAPP-owned: Interference Correction Standard and delta or epsilon Value Reference Standard name an
    entry in Reference Materials. The five QC statistics fields are limited to Quality-Control Standards.
  * The six new attribute fields' literature cells are left BLANK (not assessed): no paper was re-read
    for them. A follow-up literature pass is recorded in the Superseded README.

#23 (SMR confirmed 2026-11-23). New TAPP-owned `Monitored Property Role` and `Monitored Property Role
Detail`, keyed `monitored property`, after the defining field in the 12 tables that have one. Literature
cells: every member with a target species is `Target`; each parentless member gets the role its cell
states, or `N` where the cell does not say. Two procedures (Desem et al. 2022, Willbold 2005) monitor
masses for mass-bias correction, a role outside the four listed values; the list is open, so the cells
say `Mass-bias monitor`, and RD is told.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
from superseded_readme import write_skeleton  # noqa: E402
import keyed_cells as K  # noqa: E402

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-11-23"

# ======================================================================================================
# #19 — "Group N" references.  (field, column, old, new); applied wherever the field is, module or TAPP.
# ======================================================================================================
G19 = [
    ("Coupled Dataset or Publication Reference", "B",
     "captured in Sample Persistent Identifier (Group 2)",
     "captured in Sample Persistent Identifier, in Samples (Group 2)"),
    ("Pre-Analysis Imaging and Screening", "B",
     "recorded in the Group 1 coupling fields",
     "recorded in the Procedure Identification (Group 1) coupling fields"),
    ("Constants and Reference Values Used", "B",
     "Distinct from the Group 6 reference-material fields",
     "Distinct from the reference-material fields in Quality Control & Uncertainty (Group 6)"),
    ("Additional Notes", "B",
     "Scope is the whole document, not Group 6:",
     "Scope is the whole document, not Quality Control & Uncertainty (Group 6):"),
    ("Collision/Reaction Cell (CRC) Configuration", "B",
     "cell voltages are documented in Group 4",
     "cell voltages are documented in the collision- and reaction-gas fields of Measurement Information (Group 4)"),
    ("Mass Resolution Assignment", "B",
     "recorded in Mass Resolution Setting (Group 3)",
     "recorded in Mass Resolution Setting, in Instrument & Software (Group 3)"),
    ("Detector Configuration", "B",
     "recorded in Pulse/Analog Detector Nonlinearity Correction (Group 5)",
     "recorded in Pulse/Analog Detector Nonlinearity Correction, in Data Processing (Group 5)"),
    ("Beam Hardening Correction Method", "J",
     "Hardware pre-filtering (Group 4: X-ray Pre-filter)",
     "Hardware pre-filtering (X-ray Pre-filter, in Measurement Information, Group 4)"),
    ("Ring Artifact Correction Method", "B",
     "recorded separately in Group 6",
     "recorded separately in Ring Artifact Severity and Correction Outcome, in Quality Control & Uncertainty (Group 6)"),
    ("Sub-volume Overlap", "B",
     "May differ from the minimum sub-volume overlap required specified in the procedure (Group 4) if",
     "May differ from the minimum the procedure specifies in Minimum Sub-volume Overlap, in Measurement Information (Group 4), if"),
    ("Spectroscopic Detector(s)", "B",
     "EDS and EELS parameter fields in Group 4 apply",
     "EDS and EELS parameter fields in Measurement Information (Group 4) apply"),
]
G19_EXPECT = 83

# ======================================================================================================
# #22 — standards.
# ======================================================================================================
SRM, PCS = "Secondary Reference Materials", "Primary Calibration Standard Name"
RM, CS, QCS = "Reference Materials", "Calibration Standard", "Quality-Control Standards"
RMT, RMI, RVS = "Reference Material Type", "Reference Material Identifier", "Reference Value Source"
RV, RVU, RVB = "Reference Value", "Reference Value Uncertainty", "Reference Value Uncertainty Basis"
ICS, DEL = "Interference Correction Standard", "delta or epsilon Value Reference Standard"
AP, AA = "Analytical Precision", "Analytical Accuracy"
WS = "Within-Session Analytical Precision and Assessment Method"
BS = "Between-Session (Long-Term) Analytical Precision and Assessment Method"
AAM = "Analytical Accuracy and Assessment Method"

# module rows: name -> (B, C, D, E, F, I, J)
NEW22 = {
    RM: ("Every reference material or reference scale used in the procedure or session: calibration and "
         "bracketing standards, quality-control (secondary) materials, and materials used for interference "
         "or delta corrections. List each material once, whatever roles it holds; the fields that assign "
         "standards to target species name entries in this list.",
         "Basic", "Editable", "Text (free)",
         "e.g., NIST SRM 612 | Kakanui kaersutite | San Carlos olivine | IRMM-014 | V-CDT | None",
         "defines: standard",
         "A result can be checked only against the standards that produced it, and a material that serves "
         "several roles is one standard, not several."),
    RMT: ("The kind of material each reference material is (mineral, glass, metal, solution, gas or reference "
          "scale), with the mineral or phase name where it has one.",
          "Advanced", "Editable", "Text (free)",
          "e.g., olivine | synthetic silicate glass | metal | single-element solution | reference scale",
          "standard",
          "A mismatch between a standard's matrix and the samples' is a common source of bias in microbeam "
          "and laser-ablation analysis."),
    RMI: ("The registry or catalogue identifier of each reference material, where one exists: an IGSN, a "
          "certifying body's catalogue number (NIST, IRMM, USGS) or a museum catalogue number (USNM). Where "
          "the material is also registered as a sample, give the same identifier as in Sample Persistent "
          "Identifier. Record 'None' for an in-house material with no registered identifier.",
          "Advanced", "Editable", "Text (free)",
          "e.g., NIST SRM 612 | USNM 111312/444 | IRMM-014 | None",
          "standard",
          "Material names are reused across lots and suppliers; the identifier says which material was used."),
    RVS: ("The publication, compilation or certificate giving the accepted values used for each reference "
          "material, with a DOI where available. Where values for different properties of one material come "
          "from different sources, say which applies to which.",
          "Basic", "Editable", "Text (free)",
          "e.g., Jochum et al. 2011, doi:10.1111/j.1751-908X.2011.00120.x | GeoReM preferred values | "
          "certificate of analysis",
          "standard",
          "Results calibrated against different published values for the same material are not directly "
          "comparable."),
    RV: ("The accepted value of each reported property for each reference material, as a number with its "
         "unit. Its uncertainty is recorded in Reference Value Uncertainty and its source in Reference Value "
         "Source.",
         "Advanced", "Editable", "Numeric + unit / Text",
         "e.g., 12.80 wt% | 0.70918 | 337.13 Ma",
         "standard x reported property",
         "Without the accepted value an accuracy figure can be read but not recomputed."),
    RVU: ("The uncertainty of each accepted value in Reference Value, in the same unit, at the level stated in "
          "Reference Value Uncertainty Basis.",
          "Advanced", "Editable", "Numeric + unit / Text",
          "e.g., 0.12 wt% | 0.00001 | 0.37 Ma",
          "standard x reported property",
          "An accuracy figure means something only against the uncertainty of the value it is measured against."),
    RVB: ("What the uncertainty in Reference Value Uncertainty represents: its coverage and how it was obtained.",
          "Advanced", "Editable", "Controlled list / Text",
          "1s | 2s | 2SE | 95% confidence interval | Expanded (k = 2) | N/A | None",
          "standard x reported property",
          "The basis is the part most often left implicit, and the part an accuracy calculation depends on."),
    CS: ("The reference material against which each target species is calibrated in each target material, "
         "converting raw signal intensities to concentrations, or anchoring an isotope ratio as the bracketing "
         "standard. Name an entry in Reference Materials. Where calibration instead uses the vendor's stored "
         "library or theoretical response factors rather than measured reference materials — 'standardless' or "
         "'semi-quantitative' quantification — record that here, naming the library or model used. 'None' "
         "means no calibration was performed at all, which is a different answer.",
         "Basic", "Editable", "Text (free)", None,          # F: the consumer's own examples are kept
         "target material x target species",
         "Which standard calibrates which target species in which material decides whether the calibration "
         "is matrix-matched."),
    QCS: ("The reference material(s) run as unknowns to check the results for each target species in each "
          "target material, assessing accuracy independently of the calibration and monitoring drift. Name "
          "one or more entries in Reference Materials.",
          "Basic", "Editable", "Text (free)",
          "e.g., San Carlos olivine | BHVO-2, BCR-2 | NIST 612, BCR-2G",
          "target material x target species",
          "Only a material that played no part in the calibration tests its accuracy."),
}
QC_BLOCK = ["Detection Limit", "Detection Limit Method", "Counting Statistics Error",
            RM, RMT, RMI, RVS, RV, RVU, RVB, CS, QCS]
AFTER_RM = [RMT, RMI, RVS, RV, RVU, RVB]          # inserted directly after Reference Materials

# TAPP-owned text
ICS_B = ("The reference material used to quantify the interference correction for each affected target "
         "species. Name an entry in Reference Materials.")
ICS_F = "e.g., Synthetic TiO2 | Chromite USNM 117075"
DEL_OLD = ("Specify the standard name, lot or batch number where applicable, and the certified or consensus "
           "isotope ratio used for normalization.")
DEL_NEW = "Name an entry in Reference Materials, and give the isotope ratio used for normalization."
DEL_F = "e.g., IRMM-014 | CRM-112a / SRM-960 | NIST SRM 981 | NIST SRM 3102a | Sn_IPGP (in-house standard) | JMC Lyon | N/A | None"
QC_ACC = ("Reported for the standards named in Quality-Control Standards; a calibration standard's agreement "
          "with its own accepted values is not a test of accuracy.")
QC_PREC = ("Reported for the standards named in Quality-Control Standards; a calibration standard's agreement "
           "with its own accepted values is not an independent test of precision.")
QC_SENT = {AP: QC_PREC, WS: QC_PREC, BS: QC_PREC, AA: QC_ACC, AAM: QC_ACC}

# Literature cells. Each entry is matched by a substring that occurs in exactly one (SEC, PRI, INT, DEL)
# combination; ADD = members appended to the old secondary list; NOTE = commentary for Reference Materials.
LIT22 = [
    ("Si, Al, Ca: anorthite", "anorthite, albite, fayalite, forsterite, Mn2SiO4, TiO2, Cr2O3, microcline",
     "the calibration standards (p.3); no secondary is named"),
    ("natural kaersutite", "natural kaersutite, jadeite, bustamite, K-feldspar, synthetic rutile, Cr2O3",
     "the calibration standards (p.2); no secondary is named"),
    ("Asbestos microcline", "Asbestos microcline, synthetic anorthite, Amelia albite, synthetic fayalite, "
     "synthetic forsterite, synthetic TiO2, synthetic Cr2O3, synthetic Mn-olivine",
     "feldspar standards run as unknowns, not named individually; the rest calibrate (p.2)"),
    ("Kakanui kaersutite; S: Canyon", "Kakanui kaersutite, Canyon Diablo troilite, rhodonite, chromium metal, "
     "nickel metal, apatite, vanadium metal",
     "the calibration standards (pp.3–4); no EPMA secondary is named, and San Carlos olivine standardised "
     "the SIMS measurements"),
    ("synthetic F-phlogopite", "synthetic F-phlogopite",
     "the phlogopite calibrates F; the other calibration standards and the Smithsonian secondaries are not "
     "named individually"),
    ("Wilburforce apatite", "SrF2, albite, SW olivine, quartz, Wilburforce apatite, barite, tugtupite, "
     "rhodonite, ilmenite", "the calibration standards (p.3); no secondary is named"),
    ("calcite, dolomite, rhodochrosite, magnetite", "siderite (R-2460), rhodonite, chromite (USNM 117075), "
     "ilmenite (USNM 96189), manganite (USNM 157872), bytownite (R-2912), forsterite (P140)",
     "calibration standards: magnetite (USNM 114887), calcite (USNM 13621), dolomite (USNM 10057), siderite "
     "and rhodonite for carbonates; chromite, ilmenite, magnetite, manganite, bytownite, forsterite, San "
     "Carlos olivine (USNM 111312/444) and Springwater olivine (USNM 2566) for magnetite and olivine; the "
     "secondaries are calcite, dolomite and rhodochrosite (carbonates) and magnetite, San Carlos and "
     "Springwater olivine (p.7)"),
    ("Fo92 olivine", "fluorapatite, Fo92 olivine, rhodonite, fayalite, anorthite, baryte, potassium feldspar, "
     "scapolite, albite, dolomite, calcite, Mn carbonate, apatite",
     "the calibration standards for Mg,Na phosphate and carbonate (p.7); no secondary is named"),
    ("wollastonite", "Springwater olivine, fayalite, wollastonite, albite, orthoclase, rutile, Ni metal, "
     "chromite, rhodochrosite", "the calibration standards (p.11); no secondary is named"),
    ("NKT-1G", "NIST 612, BHVO-2G, BCR-2G, NKT-1G, TB-1G, ATHO-G, KL2-G, ML3B-G, StHs6/80-G, T1-G",
     "the glasses calibrate ⁸⁷Rb/⁸⁶Sr; NHB-9, YY12-01 and YG4301 are run as unknowns for ⁸⁷Sr/⁸⁶Sr, "
     "reference values in Table 2"),
    ("Warburton Range", "Warburton Range (IVB iron meteorite)",
     "Warburton Range calibrates and Tawallah Valley is the secondary; HSE abundances from Walker et al. "
     "(2008) (p.3)"),
    ("NIST SRM 612 and NIST SRM 614] — non-matrix", "NIST SRM 612, NIST SRM 614",
     "NIST SRM 612 and 614 calibrate; the six rock glasses are secondaries, values from GeoReM (§2.1, §3.4–3.5)"),
    ("Au, Cu: NIST 610", "NIST 610",
     "NIST 610 calibrates; NIST 612 and BCR-2G are monitoring standards (§2.2.2)"),
    ("all [all: NIST 610] — 'A NIST 610", "NIST 610",
     "the calibration standard, 'analyzed before and after every session' (Methods, p.4); no secondary is stated"),
    ("XN02 xenotime", "NIST SRM 610, XN02 xenotime",
     "NIST SRM 610 calibrates Lu and Hf and XN02 corrects the matrix; the rest are secondaries"),
    ("NIST SRM 1263a", "North Chile (Filomena, IIAB), NIST SRM 1263a V-Cr steel, Hoba (IVB)",
     "the calibration standards; no secondary is named"),
    ("BHVO-2G, BIR-1G] — linear", "NIST SRM 612, NIST SRM 614, USGS GSD-1G, USGS GSE-1G, BHVO-2G, BIR-1G",
     "the calibration glasses (§2.1, App. C1); no secondary is named"),
    ("BM90/21-G", "NIST SRM 612, NIST SRM 614, USGS GSD-1G, USGS GSE-1G, BHVO-2G, BIR-1G, KL2-G, ML3B-G, "
     "StHs6/80-G, T1-G, ATHO-G, BM90/21-G, GOR128-G, GOR132-G",
     "the calibration glasses (App. C2); no secondary is named"),
    ("MPI-DING and USGS glass", "MPI-DING and USGS glass reference materials",
     "the calibration glasses, not named individually (App. C3)"),
    ("BCR-2g, BHVO-2g and BIR-1g", "BCR-2g, BHVO-2g, BIR-1g",
     "USGS calibration glasses, GeoReM preferred values (§3.3); no secondary is named"),
    ("NIST SRM 612 and North Chile", "NIST SRM 612",
     "NIST SRM 612 and North Chile (Filomena, IIAB) calibrate; North Chile is also run as an unknown for "
     "intermediate precision"),
    ("Oxford factory internal standards", "Oxford factory internal standards",
     "the vendor's stored standards behind the XPP correction (p.2); no secondary is named"),
    ("Alfa Aesar Mo solution", "Alfa Aesar Mo solution standard",
     "the Mo solution is the bracketing standard and zero-delta reference; BHVO-2 is processed with each set "
     "of samples"),
    ("S_Spex", "S_Spex, S_Alfa (in-house S solutions), V-CDT (reference scale)",
     "S_Spex and S_Alfa bracket and are calibrated against IAEA-S-1; results are reported against V-CDT; the "
     "rest are secondaries (Table 3)"),
    ("IRMM-524a", "IRMM-524a",
     "IRMM-524a is the bracketing standard and zero-delta reference (§2.3); BHVO-2 and BCR-2 are secondaries "
     "(§2.1)"),
    ("OL-REE", "OL-REE series (in-house)",
     "OL-REE is the bracketing standard and zero-delta reference; BCR-2 is 'processed with the CAIs'"),
    ("ZrNIST", "ZrNIST", "the bracketing standard and zero-delta reference; no secondary is named"),
    ("all [Rb: NIST SRM984]", "NIST SRM984",
     "NIST SRM984 is the bracketing standard and zero-delta reference, and is also run as a sample (A.4)"),
    ("UMd, DTM, LOsST, DROsS", "",
     "Os reference solutions measured as unknowns; internal normalisation, so no calibration standard"),
    ("DTM and LOsST are the materials measured", "",
     "Os reference solutions measured as unknowns; internal normalisation, so no calibration standard"),
    ("NIST SRM984 RbCl", "NIST SRM984 RbCl",
     "NIST SRM984 is the bracketing standard and zero-delta reference, with BCR-2 bracketing in some "
     "sessions; the rest are secondaries (§2.3)"),
    ("NIST SRM 3169", "NIST SRM 3169",
     "the bracketing standard and zero-delta reference; the rest are secondaries"),
    ("SRM979", "IRMM-014, SRM979",
     "IRMM-014, SRM979 and DTS-2b bracket Fe, Cr and Mg and anchor their deltas; BHVO2 and DTS-2b are "
     "'processed alongside the samples'"),
    ("all [K: NIST SRM 3141a]", "NIST SRM 3141a",
     "the bracketing standard and zero-delta reference; BHVO-2 is the secondary"),
    ("NIST-SRM 976", "NIST-SRM 3141a, NIST-SRM 976, JMC-Lyon",
     "the bracketing standards and zero-delta references for K, Cu and Zn; BHVO-2 is the secondary"),
    ("Ti wire", "Alfa Aesar Ti wire standard (in-house)",
     "the bracketing standard and zero-delta reference; BHVO-2 and Agua Zarcas (a CM2 chondrite) are run as "
     "secondaries"),
    ("'a calibration solution'", "calibration solution (not named)",
     "five secondaries in Table 2 for accuracy and precision, eighteen more in Table 3 (§3.4); the "
     "calibration solution is not named (§3.1)"),
    ("gravimetric multielement stock", "gravimetric multi-element Ca standard (in-house)",
     "a 10,000 µg/ml Ca standard spiked with certified Li, B, Al, Mn, Zn, Sr, Cd and U solutions (§2); no "
     "secondary is named"),
    ("0.110 ng/ml", "multi-element standard solution",
     "the standard solution calibrates Cd, In, Tl and Bi; the rest are secondaries; the chondrites are samples"),
    ("a mixture of certified standards", "mixture of certified standards (not named)",
     "the calibration standards are not named (Methods); no secondary is named"),
    ("Stock No. 44270", "Alfa Aesar Specpure refractory metals plasma standard (Stock No. 44270), Kanto "
     "Kagaku AAS solutions, CLMS-4 (Spex)",
     "the mixed standard solution calibrates, checked against CLMS-4 (§2.2.6); the rest are secondaries "
     "(§2.3); the chondrites are samples"),
    ("CRM-TMDW", "", "drinking water and freshwater secondaries; no calibration standard is named"),
    ("NCS 73307 — stream sediment, for the total", "", "stream sediment, for the total digestions; no calibration standard is named"),
    ("NIST 1643f, NCS 73307, NIST 1640a", "", "freshwater, stream sediment and freshwater secondaries; no calibration standard is named"),
    ("XSTC-13", "XSTC-13, XSTC-1 (SPEX CertiPrep), custom P-Ca solution (Fujifilm-Wako single-element "
     "standards), MISA05-1 (AccuStandard)",
     "the calibration solutions (Methods); the Smithsonian Allende powder is the secondary, n = 5"),
    ("NIST SRM981", "NIST SRM981",
     "NIST SRM981 calibrates the Pb vs Tl mass-bias correlations (§2.4); the rest are secondaries (Tables 1–2)"),
    ("VHG Labs", "multi-element certified solutions (VHG Labs)",
     "the calibration solutions (§2.2); FER-2 validates the method"),
    ("'The standard solution was measured", "standard solution (not named)",
     "the calibration solution is not named (§2.1.2); the rest are secondaries (§2.3); the chondrites are samples"),
    ("Spectrosol", "ICP High Purity Standards, Spectrosol AA standards",
     "High Purity Standards calibrate the isotope spikes and Spectrosol solutions the Mn and Co standard "
     "additions (§2.1); NASS-5 and the SAFe samples are secondaries (§2.6)"),
    ("Standards 0–8", "Standards 0–8 (matrix-matched Me/Ca calibration standards)",
     "the calibration standards (§2.2, §2.3.1); the four Cambridge consistency standards are secondaries"),
    ("MES 1–3", "Alfa Aesar specpure solutions, multi-element spike solutions MES 1–3, multi-element "
     "standard solution",
     "the spikes are calibrated by reverse ID against the Alfa Aesar solutions, which also make the standard "
     "solution (Table 1); the rest are secondaries (Table 5)"),
]

# ======================================================================================================
# #23 — monitored-property role.
# ======================================================================================================
DEFINERS = ("Monitored Masses", "Monitored Elements")
ROLE, ROLED = "Monitored Property Role", "Monitored Property Role Detail"
NEW23 = {
    ROLE: ("Why each monitored property is measured. Target: to determine its target species. Interference "
           "monitor: to correct an interference on another monitored property, including a gas background. "
           "Internal standard: it is the internal-standard mass, whose known concentration normalises the "
           "others. Phase monitor: to detect contamination by another phase, such as a micro-inclusion, "
           "rather than to quantify or correct anything. A monitored property may hold more than one role. "
           "One with the role Target has a target species; one with any other role may have one but need not.",
           "Basic", "Read-Only", "Controlled list / Text",
           "Target | Interference monitor | Internal standard | Phase monitor | N/A | None",
           "monitored property",
           "Without the role, a monitored property with no target species cannot be told apart from one whose "
           "target species was left out."),
    ROLED: ("For a monitored property whose role is not Target, what it serves: the interference it corrects "
            "and the monitored property it corrects it on, the target species it standardises, or the phase it "
            "detects. The correction itself is recorded with the interference correction fields.",
            "Advanced", "Read-Only", "Text (free)",
            "e.g., ⁸⁷Rb on ⁸⁷Sr | MoO⁺ on Cd | all target species | micro-inclusions | Cr Kβ on Mn Kα",
            "monitored property",
            "Names the dependency a reader needs to check a correction, without restating the correction."),
}
# matched by a substring of the defining cell: (role cell, detail cell)
LIT23 = [
    ("⁸³Kr, ¹⁶⁷Er²⁺", "⁸³Kr, ¹⁶⁷Er²⁺, ¹⁷³Yb²⁺: Interference monitor; other: Target",
     "⁸³Kr: gas background; ¹⁶⁷Er²⁺, ¹⁷³Yb²⁺: N — the interferences they monitor are not stated"),
    ("⁶¹Ni, ²⁴Mg", "⁶¹Ni: Internal standard; ²⁴Mg, ²⁹Si, ³¹P, ³³S: Phase monitor; other: Target",
     "⁶¹Ni: all target species; ²⁴Mg, ²⁹Si, ³¹P, ³³S: micro-inclusions — 'to check the involvement of "
     "micro-inclusions' (p.3)"),
    ("172Yb, (172+82)Yb", "172Yb, (172+82)Yb, 27Al, 43Ca, 89Y, 90Zr: N; other: Target — the roles of the "
     "masses with no target species are not stated (Table 1)", "N — not stated"),
    ("91Zr, 99Ru → none", "91Zr, 99Ru: Interference monitor; other: Target",
     "91Zr, 99Ru: the Zr and Ru isobars on Mo"),
    ("53Cr, 60Ni → none", "53Cr, 60Ni: Interference monitor; other: Target",
     "53Cr: ⁵⁴Cr on ⁵⁴Fe; 60Ni: ⁵⁸Ni on ⁵⁸Fe"),
    ("mass 93", "95Mo, 98Mo: Interference monitor; mass 93: N; other: Target — the use of mass 93 is not stated",
     "95Mo, 98Mo: Mo interferences on Zr"),
    ("88Sr → none — ⁸⁸Sr monitors", "88Sr: Interference monitor; other: Target", "88Sr: ⁸⁷Sr on ⁸⁷Rb"),
    ("182W, 185Re", "182W, 185Re: Interference monitor; other: Target",
     "N — the isobars they monitor are not stated"),
    ("183W, 185Re", "183W, 185Re: Interference monitor; other: Target",
     "N — the isobars they monitor are not stated"),
    ("84Sr, 86Sr, 88Sr → none", "84Sr, 86Sr, 88Sr: Interference monitor; other: Target",
     "N — 'Strontium was monitored using the 88Sr ion beams'; the interference is not stated"),
    ("95Mo, 99Ru, 101Ru → none", "95Mo, 99Ru, 101Ru: N; other: Target — their role is not stated",
     "N — not stated"),
    ("60Ni, 49Ti, 51V", "53Cr, 56Fe: Target, Interference monitor; 60Ni, 49Ti, 51V: Interference monitor; "
     "other: Target", "60Ni, 53Cr: monitored in the Fe run; 49Ti, 51V, 56Fe: monitored in the Cr run"),
    ("44Ca, 51V, 52Cr, 53Cr", "44Ca, 51V, 52Cr, 53Cr: N; other: Target — their role is not stated",
     "N — not stated"),
    ("46Ca → none", "46Ca: N; other: Target — the role of ⁴⁶Ca is not stated beyond its low abundance",
     "N — not stated"),
    ("113Cd, 118Sn, 149Sm", "95Mo: Interference monitor; 113Cd, 118Sn, 149Sm: N; other: Target — '113Cd was "
     "not used for Cd determination'", "95Mo: MoO on Cd"),
    ("103Rh → none — the spiked", "103Rh: Internal standard; other: Target", "103Rh: all target species"),
    ("202Hg, 203Tl", "203Tl, 205Tl: Mass-bias monitor; 202Hg: N; other: Target — Tl corrects mass bias through "
     "the Pb vs Tl correlations (§2.4)", "203Tl, 205Tl: mass bias on Pb"),
    ("103Rh → none — Table 2", "103Rh: Internal standard; other: Target", "103Rh: all target species"),
    ("93Nb → none", "93Nb: N; other: Target — its role is not stated", "N — not stated"),
    ("95Mo → none", "95Mo: Interference monitor; other: Target", "95Mo: MoO⁺ on Cd"),
    ("43Ca → none", "43Ca: N; other: Target — its role is not stated", "N — not stated"),
    ("47Ti, 49Ti, 99Ru", "47Ti, 49Ti, 99Ru, 101Ru, 185Re, 187Re: Mass-bias monitor; other: Target — measured "
     "for the in-run mass-fractionation correction", "47Ti, 49Ti, 99Ru, 101Ru, 185Re, 187Re: in-run mass "
     "fractionation"),
]

MODULE_EDITS = {   # module -> decision text
    "Core": "{d} v{v}. Issue #19: Group-number references name their section (Coupled Dataset or Publication "
            "Reference, Constants and Reference Values Used, Additional Notes).",
    "SamplingUnitSelection": "{d} v{v}. Issue #19: Pre-Analysis Imaging and Screening names the Procedure "
                             "Identification (Group 1) coupling fields.",
    "CollisionCell": "{d} v{v}. Issue #19: CRC Configuration names the gas fields' section.",
    "SingleCollector": "{d} v{v}. Issue #19: Detector Configuration names the section of the nonlinearity field.",
    "ICPMS": "{d} v{v}. Issue #22: the three QC statistics are limited to Quality-Control Standards.",
    "CompositionQC": "{d} v{v}. Issue #22 (revision 2): Secondary Reference Materials -> Reference Materials "
                     "(every standard, each once); Primary Calibration Standard Name -> Calibration Standard; new "
                     "Reference Material Type, Reference Material Identifier, Reference Value Source, Reference "
                     "Value, Reference Value Uncertainty, Reference Value Uncertainty Basis, Quality-Control "
                     "Standards.",
}

COL = dict(A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9)


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


def apply_g19(rows, counts):
    for r in rows[1:]:
        if not r:
            continue
        for f, c, old, new in G19:
            if r[0].strip() == f and len(r) > COL[c] and old in r[COL[c]]:
                r[COL[c]] = r[COL[c]].replace(old, new)
                counts[f] = counts.get(f, 0) + 1


def insert_sentence(b, sent):
    assert sent not in b
    i = b.find("For the procedure:")
    if i < 0:
        return b.rstrip() + " " + sent
    return b[:i] + sent + " " + b[i:]


def lit_cols(h):
    s = h.index("Literature Assessment")
    return s, [j for j in range(s + 1, len(h)) if h[j].strip()]


def build22(sec, pri, ics, dlt):
    """-> (Reference Materials cell, Quality-Control Standards cell)."""
    combo = " ".join(x or "" for x in (sec, pri, ics, dlt))
    hits = [e for e in LIT22 if e[0] in combo]
    sec_struct = sec and not K.is_marker(sec)
    filled = any(x and not K.is_marker(x) for x in (sec, pri, ics, dlt))
    if not filled:
        return sec, sec                                  # both markers: carry the secondary marker
    assert len(hits) == 1, "LIT22: %d matches for %r" % (len(hits), combo[:120])
    _, add, note = hits[0]
    if sec_struct:
        part, comm = K.split_commentary(sec)
        rm = part + (", " + add if add else "") + " — " + note
        mems = []
        for ent in K.split_top(part, ";"):
            mems += [m.strip() for m in K.split_top(ent, ",") if m.strip()]
        qc = "all [all: %s]" % ", ".join(mems) + (" — " + comm if comm else "")
        old_ids = {K.norm(m) for m, _ in K.parse_definer(sec)[0]}
        new_ids = {K.norm(m) for m, _ in K.parse_definer(rm)[0]}
        assert old_ids <= new_ids, ("lost members", old_ids - new_ids)
    else:
        assert add, "no members for %r" % combo[:80]
        rm, qc = add + " — " + note, sec
    ms, errs = K.parse_definer(rm)
    assert not errs, (errs, rm)
    if qc and not K.is_marker(qc):
        st, msg = K.check_cell(qc, "target material x target species", {})
        assert st == "ok", (msg, qc)
    return rm, qc


def build23(defcell):
    if K.is_marker(defcell):
        s, _ = K.split_commentary(defcell)
        return s, s
    ms, errs = K.parse_definer(defcell)
    assert not errs
    orph = [m for m, p in ms if p and K.norm(p) == "none"]
    if not orph:
        return "all: Target", "N/A — every monitored property is a target"
    hits = [e for e in LIT23 if e[1] and e[0] in defcell]
    assert len(hits) == 1, "LIT23: %d matches for %r" % (len(hits), defcell[:100])
    _, role, det = hits[0]
    known = {K.norm(m) for m, _ in ms}
    for cell in (role, det):
        st, msg = K.check_cell(cell, "monitored property", {"monitored property": known})
        assert st in ("ok", "skip"), (msg, cell)
    return role, det


def new_row(width, name, spec, flags_from, lit):
    B, C, D, E, F, I, J = spec
    r = [""] * width
    r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8], r[9] = name, B, C, D, E, F or "", DATE, I, J
    for j, v in flags_from.items():
        r[j] = v
    for j, v in lit.items():
        r[j] = v
    return r


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))

    # ---------------- modules (in memory) ----------------
    M, J = {}, {}
    for m in MODULE_EDITS:
        p = os.path.join(MODULES, "Module_%s.csv" % m)
        M[m] = rows_of(p)
        J[m] = json.load(io.open(p[:-4] + ".json", encoding="utf-8"))
    g19c = {}
    for m in ("Core", "SamplingUnitSelection", "CollisionCell", "SingleCollector"):
        apply_g19(M[m], g19c)
    for r in M["ICPMS"][1:]:
        if r and r[0] in QC_SENT:
            r[1] = insert_sentence(r[1], QC_SENT[r[0]]); r[7] = DATE
    q = M["CompositionQC"]; hq = q[0]
    names = [r[0] for r in q[1:]]
    assert SRM in names and PCS in names and RM not in names, "PREMISE: CompositionQC already changed"
    out = [hq]
    for r in q[1:]:
        if r[0] == SRM:
            r = list(r); spec = NEW22[RM]
            r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[8], r[9] = RM, spec[0], spec[1], spec[2], spec[3], spec[4], DATE, spec[5], spec[6]
            out.append(r)
            for n in AFTER_RM:
                s = NEW22[n]
                out.append([n, s[0], s[1], s[2], s[3], s[4], "", DATE, s[5], s[6]])
        elif r[0] == PCS:
            r = list(r); s = NEW22[CS]
            r[0], r[1], r[7], r[8], r[9] = CS, s[0], DATE, s[5], s[6]
            out.append(r)
            s = NEW22[QCS]
            out.append([QCS, s[0], s[1], s[2], s[3], s[4], "", DATE, s[5], s[6]])
        else:
            out.append(r)
    M["CompositionQC"] = out
    for b in J["CompositionQC"]["blocks"]:
        if b["name"] == "qc":
            assert b["fields"] == ["Detection Limit", "Detection Limit Method", "Counting Statistics Error",
                                   SRM, PCS], b["fields"]
            b["fields"] = QC_BLOCK
    J["CompositionQC"]["title"] = J["CompositionQC"]["title"].replace(
        "secondary reference materials", "reference materials and their assignment")

    # ---------------- consumers (plan + build in memory) ----------------
    assert sum(g19c.values()) == 6, ("module #19 rows", g19c)
    plan, g19t, stats = [], {}, {"rm": 0, "qc": 0, "role": 0}
    built = {}
    for e in reg["composed"]:
        rel = e["tapp"]
        src = rows_of(os.path.join(ROOT, rel)); h = src[0]; w = len(h)
        s, lits = lit_cols(h)
        modes = list(range(10, s))
        byname = {r[0].strip(): r for r in src[1:] if r}
        apply_g19(src, g19t)
        # ---- #22, only where Module_CompositionQC is consumed
        if SRM in byname:
            sec_r, pri_r = byname[SRM], byname[PCS]
            ics_r, del_r = byname.get(ICS), byname.get(DEL)
            g = lambda r, j: (r[j].strip() if r is not None and j < len(r) else None)
            rmc, qcc = {}, {}
            for j in lits:
                rmc[j], qcc[j] = build22(g(sec_r, j), g(pri_r, j), g(ics_r, j), g(del_r, j))
            fl = {j: sec_r[j] for j in modes}
            newsrc = [h]
            for r in src[1:]:
                n = r[0].strip() if r else ""
                if n == SRM:
                    r = list(r) + [""] * (w - len(r))
                    r[0], r[5], r[7], r[9] = RM, NEW22[RM][4], DATE, NEW22[RM][6]
                    for j in lits:
                        r[j] = rmc[j]
                    newsrc.append(r); stats["rm"] += 1
                    for n2 in AFTER_RM:
                        newsrc.append(new_row(w, n2, NEW22[n2], fl, {}))
                elif n == PCS:
                    r = list(r) + [""] * (w - len(r))
                    r[0], r[7], r[9] = CS, DATE, NEW22[CS][6]
                    newsrc.append(r)
                    newsrc.append(new_row(w, QCS, NEW22[QCS], {j: r[j] for j in modes}, qcc)); stats["qc"] += 1
                else:
                    newsrc.append(r)
            src = newsrc
        for r in src[1:]:
            n = r[0].strip() if r else ""
            if n == ICS:
                r[1], r[5], r[7] = ICS_B, ICS_F, DATE
            elif n == DEL:
                assert DEL_OLD in r[1], "PREMISE: delta B"
                r[1], r[5], r[7] = r[1].replace(DEL_OLD, DEL_NEW), DEL_F, DATE
            elif n in (AP, AA):
                r[1] = insert_sentence(r[1], QC_SENT[n]); r[7] = DATE
        # ---- #23
        newsrc = [src[0]]
        for r in src[1:]:
            newsrc.append(r)
            n = r[0].strip() if r else ""
            if n in DEFINERS:
                fl = {j: r[j] for j in modes}
                rc, dc = {}, {}
                for j in lits:
                    rc[j], dc[j] = build23(r[j].strip() if j < len(r) else "")
                newsrc.append(new_row(w, ROLE, NEW23[ROLE], fl, rc))
                newsrc.append(new_row(w, ROLED, NEW23[ROLED], fl, dc)); stats["role"] += 1
        src = newsrc
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        built[rel] = src
        plan.append((e, rel, new))
        print("  %-34s -> %s" % (os.path.basename(rel), os.path.basename(new)))

    total = sum(g19t.values())
    print("\n  #19: %d references rewritten %s" % (total, json.dumps(g19t)))
    assert total == G19_EXPECT, "expected %d #19 references, found %d" % (G19_EXPECT, total)
    print("  #22: %d TAPPs with Reference Materials; #23: %d TAPPs with the role fields" % (stats["rm"], stats["role"]))
    assert stats["rm"] == 12 and stats["qc"] == 12 and stats["role"] == 12, stats
    assert len(plan) == 16
    vers = {m: J[m]["version"] for m in M}
    print("  modules: " + ", ".join("%s v%s->v%d" % (m, v, int(v) + 1) for m, v in vers.items()))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # ---------------- write modules ----------------
    newver = {m: str(int(v) + 1) for m, v in vers.items()}
    for m in M:
        p = os.path.join(MODULES, "Module_%s.csv" % m)
        write(p, M[m])
        jp = p[:-4] + ".json"
        ind = 4 if io.open(jp, encoding="utf-8").read().startswith("{\n    ") else 2
        J[m]["version"] = newver[m]
        J[m]["decisions"].append(MODULE_EDITS[m].format(d=DATE, v=newver[m]))
        with io.open(jp, "w", encoding="utf-8") as fh:
            json.dump(J[m], fh, indent=ind, ensure_ascii=False); fh.write("\n")

    # ---------------- write, compose, stamp, park ----------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        old_rows = rows_of(os.path.join(ROOT, rel))
        write(np_, built[rel])
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-2000:], q.stderr[-800:]))
        rr = rows_of(np_)
        ren = {RM: SRM, CS: PCS}
        old = {r[0].strip(): r for r in old_rows[1:] if r}
        for r in rr[1:]:
            n = r[0].strip() if r else ""
            if not n:
                continue
            o = old.get(ren.get(n, n))
            if o is None or [r[i] for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)] != [o[i] if i < len(o) else "" for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)]:
                if r[7] != "" and o is not None:
                    r[7] = DATE
                elif o is None:
                    r[7] = DATE
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        e["tapp"] = news[stem]
        for m in e["modules"]:
            if m["name"] in newver:
                m["version"] = newver[m["name"]]
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
