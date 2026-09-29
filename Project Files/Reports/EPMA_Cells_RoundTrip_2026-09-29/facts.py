"""Procedure facts stated in each EPMA paper's EPMA methods paragraph(s), for the cells round-trip.

One entry per fact: (field, member, tokens, source). `member` is the key member the fact belongs to
(None for an unkeyed field or a definer). For `target material x target species` it is
"outer/inner". `tokens`: the fact is recovered if ANY token appears in the right place (case-, space-,
dash- and Greek-insensitive). A keyed field's facts are listed per member, because recovering *which
member* a value belongs to is the point of the test.

Scope: EPMA work only (SEM, EBSD, SIMS, TEM and LA-ICP-MS paragraphs of the same papers are excluded),
procedure-level facts only (C = Basic or Advanced), and only what the paper states in the text or a
table footnote read on 2026-09-29. Written by the author of the cells, so NOT blind; see README.
"""

def per(field, pairs, src):
    return [(field, m, [t] if isinstance(t, str) else t, src) for m, t in pairs]


def each(field, members, token, src):
    return [(field, m, [token] if isinstance(token, str) else token, src) for m in members]


FACTS = {
  "Ma+2015": [
    ("Instrument Model", None, ["8200"], "JEOL 8200 electron microprobe"),
    ("Accelerating Voltage", None, ["15 kV"], "WDS: 15 kV; 5 nA"),
    ("Beam Current", "all", ["5 nA"], "WDS: 15 kV; 5 nA"),
    ("Beam Mode", "all", ["focus"], "beam in focused mode"),
    ("X-ray Detection Method per Monitored Element", "all", ["WDS"], "WDS"),
    ("Acquisition Software", None, ["Probe for EPMA"], "interfaced with the Probe for EPMA program"),
    ("Matrix Correction Method", None, ["CITZAF"], "processed with the CITZAF correction procedure"),
  ] + per("Primary Calibration Standard Name", [("all/Si", "anorthite"), ("all/Al", "anorthite"), ("all/Ca", "anorthite"),
          ("all/Na", "albite"), ("all/Fe", "fayalite"), ("all/Mg", "forsterite"), ("all/Mn", "Mn2SiO4"),
          ("all/Ti", "TiO2"), ("all/Cr", "Cr2O3"), ("all/K", "microcline")], "Standards for analysis were ...")
    + each("X-ray Line", ["Si", "Al", "Ca", "Na", "Fe", "Mg", "Mn", "Ti", "Cr", "K"], "Ka", "SiKα ... KKα")
    + per("Detection Limit", [("K2O", "0.02"), ("Cr2O3", "0.05"), ("MnO", "0.06")], "Table 1 footnote c"),

  "Hu+2020": [
    ("Instrument Model", None, ["8100"], "JEOL JXA-8100"),
    ("Accelerating Voltage", None, ["15 kV"], "The accelerating voltage was 15 kV"),
    ("Beam Current", "all", ["10 nA"], "the beam current was 10 nA"),
    ("Matrix Correction Method", None, ["Bence-Albee"], "The Bence-Albee method was used"),
    ("X-ray Line Overlap Corrections Applied", "Mn", ["Yes"], "interference of the Ka line of Mn by the Kb line of Cr was corrected"),
    ("Interfering Elements", "Mn", ["Cr"], "as above"),
  ] + per("Primary Calibration Standard Name", [("all/Si", "kaersutite"), ("all/Mg", "kaersutite"), ("all/Fe", "kaersutite"),
          ("all/Na", "jadeite"), ("all/Al", "jadeite"), ("all/Ca", "bustamite"), ("all/Mn", "bustamite"),
          ("all/K", "K-feldspar"), ("all/Ti", "rutile"), ("all/Cr", "Cr2O3")], "The EPMA standards were ...")
    + per("Detection Limit", [("K2O", "0.01"), ("SiO2", "0.02"), ("Al2O3", "0.02"), ("MgO", "0.02"), ("CaO", "0.02"),
          ("Na2O", "0.02"), ("TiO2", "0.03"), ("Cr2O3", "0.03"), ("FeO", "0.05"), ("MnO", "0.06")], "The detection limits are ..."),

  "Liu+2016_Cal": [
    ("Instrument Model", None, ["8200"], "a JEOL JXA-8200 EMP at Caltech"),
    ("Accelerating Voltage", None, ["15 kV"], "15 kV accelerating voltage"),
  ] + per("Beam Current", [("olivine", "20 nA"), ("pyroxene", "20 nA"), ("Fe-Ti-Cr oxides", "20 nA"), ("maskelynite", "10 nA"),
          ("phosphate", "10 nA"), ("sulfide", "10 nA"), ("glass", "10 nA")], "Analytical conditions for olivine, ...")
    + per("Beam Diameter", [("olivine", "1-2"), ("pyroxene", "1-2"), ("Fe-Ti-Cr oxides", "1-2"), ("maskelynite", "5-10"),
          ("phosphate", "5-10"), ("sulfide", "5-10"), ("glass", "5-10")], "1–2 µm beam diameter; defocused beam of 5–10 µm")
    + each("Beam Mode", ["maskelynite", "phosphate", "sulfide", "glass"], "defocus", "analyzed using a defocused beam")
    + per("Detection Limit", [("SiO2", "0.03"), ("TiO2", "0.03"), ("Al2O3", "0.03"), ("MgO", "0.03"), ("CaO", "0.03"),
          ("FeO", "0.05-0.1"), ("MnO", "0.05-0.1"), ("Cr2O3", "0.05-0.1"), ("NiO", "0.05-0.1"), ("Na2O", "0.05-0.1"),
          ("K2O", "0.05-0.1"), ("P2O5", "0.05-0.1")], "Detection limits are typically ..."),

  "Liu+2016_UT": [
    ("Instrument Model", None, ["SX100"], "Cameca SX100 electron microprobe (EMP) at the University of Tennessee"),
    ("Accelerating Voltage", None, ["15 kV", "15 keV"], "15 keV accelerating potential"),
    ("Mapping Beam Current", None, ["20 nA"], "a 20 nA focused beam (section maps)"),
    ("Mapping Beam Current", None, ["200 nA"], "200 nA current (olivine megacryst maps)"),
    ("Mapping Beam Mode", None, ["focus"], "focused beam"),
    ("Step Size / Pixel Size", None, ["8-12"], "a step size of 8–12 µm"),
    ("Step Size / Pixel Size", None, ["2 µm", "2 um"], "a step size of 2 µm (megacryst maps)"),
    ("Dwell Time per Pixel", "Fe", ["0.5 s"], "a dwell time of ~0.5 s at each step"),
  ] + each("X-ray Line", ["Ca", "Al", "Fe", "Mg", "P", "Cr"], "Ka", "Ca Ka, Al Ka, Fe Ka, Mg Ka; Fe, P, Al, Ca, Cr Ka"),

  "Ma+2017": [
    ("Instrument Model", None, ["8200"], "JEOL 8200 electron microprobe"),
    ("Accelerating Voltage", None, ["15 kV"], "WDS: 15 kV, 5 nA"),
    ("Beam Current", "all", ["5 nA"], "WDS: 15 kV, 5 nA"),
    ("Beam Mode", "all", ["focus"], "beam in focused mode"),
    ("X-ray Detection Method per Monitored Element", "all", ["WDS"], "WDS"),
    ("Acquisition Software", None, ["Probe for EPMA"], "Probe for EPMA program"),
    ("Matrix Correction Method", None, ["CITZAF"], "CITZAF correction procedure"),
    ("Peak Counting Time", "all", ["20 s"], "Counting times were 20 s on-peak"),
    ("Background Counting Time", "all", ["10 s"], "10 s each on high and low background positions"),
    ("Background Position(s)", "all", ["high"], "high and low background positions"),
    ("Secondary Reference Materials", None, ["feldspar"], "feldspar standards as unknowns"),
  ] + per("Primary Calibration Standard Name", [("all/Si", "microcline"), ("all/Al", "microcline"), ("all/K", "microcline"),
          ("all/Ca", "anorthite"), ("all/Na", "albite"), ("all/Fe", "fayalite"), ("all/Mg", "forsterite"),
          ("all/Ti", "TiO2"), ("all/Cr", "Cr2O3"), ("all/Mn", "Mn-olivine")], "Standards for analysis were ...")
    + each("X-ray Line", ["Si", "Al", "K", "Ca", "Na", "Fe", "Mg", "Ti", "Cr", "Mn"], "Ka", "SiKa ... MnKa")
    + per("Detection Limit", [("Si", "0.05"), ("Ti", "0.04"), ("Al", "0.06"), ("Fe", "0.06"), ("Mg", "0.02"), ("Ca", "0.02"),
          ("Na", "0.03"), ("K", "0.02"), ("Cr", "0.05"), ("Mn", "0.06")], "The detection limits (wt%) are ...")
    + per("Analytical Accuracy", [("feldspar standards/Si", "1-2%"), ("feldspar standards/Al", "1-2%"), ("feldspar standards/Ca", "1-2%"),
          ("feldspar standards/Na", "1-2%"), ("feldspar standards/K", "1-2%")], "The accuracy is 1–2% for Si, Al, Ca, Na, and K"),

  "Frank+2023": [
    ("Instrument Model", None, ["SX100"], "Cameca SX100 electron microprobe at ARES"),
    ("Accelerating Voltage", None, ["20 kV"], "performed at 20 kV and 20 nA"),
    ("Beam Current", "all", ["20 nA"], "20 nA"),
    ("Beam Mode", "all", ["focus"], "using a focused beam of 1 µm"),
    ("Beam Diameter", "all", ["1 µm", "1 um"], "a focused beam of 1 µm"),
    ("Peak Counting Time", "all", ["10-50 s"], "Peak count times were 10–50 s"),
  ] + per("Primary Calibration Standard Name", [("all/" + e, "Kakanui") for e in ["Si", "Al", "Ti", "K", "Na", "Fe", "Mg", "Ca"]]
          + [("all/S", "troilite"), ("all/Mn", "rhodonite"), ("all/Cr", "chromium metal"), ("all/Ni", "nickel metal"),
             ("all/P", "apatite"), ("all/V", "vanadium metal")], "Standards were Kakanui kaersutite for ...")
    + per("Detection Limit", [("Al2O3", "0.03-0.04"), ("K2O", "0.03-0.04"), ("CaO", "0.03-0.04"), ("Na2O", "0.05"),
          ("MgO", "0.05"), ("SiO2", "0.05"), ("FeO", "0.05"), ("MnO", "0.05"), ("P2O5", "0.06-0.09"), ("SO2", "0.06-0.09"),
          ("TiO2", "0.06-0.09"), ("V2O3", "0.06-0.09"), ("Cr2O3", "0.06-0.09"), ("NiO", "0.06-0.09")], "Detection limits are typically ..."),

  "Broussard+2026": [
    ("Instrument Model", None, ["8200"], "the JEOL JXA-8200 electron microprobe"),
    ("WDS Spectrometer Configuration", None, ["five", "5 wavelength"], "equipped with five wavelength-dispersive spectrometers"),
    ("Acquisition Software", None, ["Probe for EPMA"], "acquired using the Probe for EPMA microanalysis software"),
    ("Matrix Correction Method", None, ["CITZAF"], "matrix correction using the CITZAF"),
    ("Accelerating Voltage", None, ["15 kV"], "15 kV accelerating potential"),
    ("Beam Current", "all", ["25 nA"], "25 nA probe current for point analysis"),
    ("X-ray Background Correction Method", "other", ["MAN", "mean atomic number"], "the mean atomic number (MAN) background calibration"),
    ("X-ray Background Correction Method", "F", ["polynomial"], "a polynomial fit to the background determined on representative phases"),
    ("Diffracting Crystal", "F", ["LDE1"], "using the LDE1 diffracting crystal"),
    ("Primary Calibration Standard Name", "all/F", ["F-phlogopite"], "synthetic F-phlogopite used as the primary standard"),
    ("Target Species Estimation Method", "O", ["stoichiometry"], "Oxygen was calculated by elemental stoichiometry"),
    ("Target Species Estimation Method", "CO2", ["stoichiometry"], "CO2 was calculated by stoichiometry"),
    ("Target Species Estimation Method", "H2O", ["analytical total"], "water estimated by inspection of the analytical total"),
    ("Secondary Reference Materials", None, ["Smithsonian"], "Secondary standards including the Smithsonian Microbeam standards"),
    ("Data Processing Software(s)", None, ["CalcImage"], "correction made using CalcImage"),
    ("Data Processing Software(s)", None, ["Quantitative Microanalysis Explorer"], "and the Quantitative Microanalysis Explorer"),
  ],

  "Seifert+2026": [
    ("Instrument Model", None, ["8530"], "the JEOL 8530 EMPA at NASA JSC"),
    ("Accelerating Voltage", None, ["15 kV"], "performed at 15kV, 20nA"),
    ("Beam Current", "all", ["20 nA"], "20nA"),
    ("Beam Diameter", "all", ["2 µm", "2 um"], "using a 2μm probe size"),
    ("Beam Damage Minimization", "all", ["Durango"], "compared analyses of Durango apatite ... 10μm and 3μm spot size"),
    ("Target Species Estimation Method", "OH", ["difference"], "calculated by difference based on 1–F–Cl=OH"),
  ] + per("Primary Calibration Standard Name", [("all/F", "SrF2"), ("all/Na", "albite"), ("all/Mg", "olivine"),
          ("all/Si", "quartz"), ("all/P", "apatite"), ("all/Ca", "apatite"), ("all/S", "barite"), ("all/Cl", "tugtupite"),
          ("all/Mn", "rhodonite"), ("all/Fe", "ilmenite")], "Standards used for the phosphate measurements include ..."),

  "Pang+2016": [
    ("Instrument Model", None, ["8100"], "JEOL8100 Electron Probe Micro-Analyzer"),
    ("X-ray Detection Method per Monitored Element", "all", ["WDS"], "with wavelength dispersive spectrometers (WDS)"),
    ("Accelerating Voltage", None, ["15 kV"], "accelerated at 15kV"),
    ("Beam Current", "all", ["20 nA"], "a focused beam of 20nA ... at the same beam current"),
    ("Beam Mode", "plagioclase and its polymorphs", ["defocus"], "plagioclase and its polymorphs ... a defocused beam"),
    ("Beam Mode", "other", ["focus"], "Measurements of most minerals were performed with a focused beam"),
    ("Beam Diameter", "plagioclase and its polymorphs", ["2-5"], "a defocused beam (2–5 µm in diameter)"),
    ("Detection Limit", "all", ["0.02"], "better than 0.02 wt%"),
  ],

  "McCoy+2025_SI": [
    ("Instrument Model", None, ["8530F"], "JEOL 8530F+ Hyperprobe"),
    ("Accelerating Voltage", None, ["15 kV"], "run at 15 kV and 10 nA"),
    ("Beam Current", "all", ["10 nA"], "15 kV and 10 nA"),
    ("Beam Diameter", "carbonate", ["5 µm", "5 um"], "an analytical spot size of 5 µm"),
    ("Beam Diameter", "magnetite", ["1 µm", "1 um"], "an analytical spot size of 1 µm"),
    ("Beam Diameter", "olivine", ["1 µm", "1 um"], "an analytical spot size of 1 µm"),
    ("Diffracting Crystal", "Fe", ["LIFL"], "Fe and Mn were analysed using a LIFL crystal"),
    ("Diffracting Crystal", "Mn", ["LIFL"], "as above"),
    ("Diffracting Crystal", "Mg", ["TAPL"], "Mg using a TAPL crystal"),
    ("Diffracting Crystal", "Ca", ["PETL"], "Ca using a PETL crystal"),
    ("Sample Preparation Method", None, ["Ir"], "conducted on Ir-coated specimens"),
    ("Primary Calibration Standard Name", "all/Fe", ["magnetite", "siderite"], "Standard analyses were performed on magnetite, calcite, dolomite, siderite and rhodonite"),
  ] + [("Secondary Reference Materials", None, [m], "Secondary standardization was conducted using ...")
       for m in ["calcite", "dolomite", "rhodochrosite", "magnetite", "San Carlos", "Springwater"]],

  "McCoy+2025_UA": [
    ("Instrument Model", None, ["SX-100", "SX100"], "Cameca SX-100 electron microprobe"),
    ("Sample Preparation Method", None, ["20 nm", "carbon"], "coated with a thin film of carbon (20nm)"),
    ("Accelerating Voltage", None, ["15 kV"], "acceleration voltage of 15kV"),
    ("Beam Current", "Mg,Na phosphate", ["8 nA"], "beam current of 8nA"),
    ("Beam Diameter", "Mg,Na phosphate", ["1 µm", "1 um", "1-µm"], "using a 1-µm beam size"),
  ] + per("Primary Calibration Standard Name", [("Mg,Na phosphate/F", "fluorapatite"), ("Mg,Na phosphate/P", "fluorapatite"),
          ("Mg,Na phosphate/Ca", "fluorapatite"), ("Mg,Na phosphate/Si", "Fo92"), ("Mg,Na phosphate/Mg", "Fo92"),
          ("Mg,Na phosphate/Fe", "fayalite"), ("Mg,Na phosphate/Al", "anorthite"), ("Mg,Na phosphate/S", "baryte"),
          ("Mg,Na phosphate/K", "feldspar"), ("Mg,Na phosphate/Cl", "scapolite"),
          ("carbonate/Na", "albite"), ("carbonate/Si", "Fo92"), ("carbonate/Mg", "dolomite"), ("carbonate/Ca", "calcite"),
          ("carbonate/Mn", "Mn carbonate"), ("carbonate/P", "apatite"), ("carbonate/S", "baryte"),
          ("carbonate/Fe", "fayalite")], "The standards used for Mg,Na phosphate were ...; For carbonates ..."),

  "Zega+2025": [
    ("Instrument Model", None, ["SX-100", "SX100"], "Cameca SX-100 Ultra electron microprobe"),
    ("Accelerating Voltage", None, ["15 kV"], "run at 15 kV"),
    ("Mapping Beam Current", None, ["20 nA"], "X-ray maps and BSE images were run at 15kV and 20nA"),
  ] + per("Beam Current", [("silicates", "20 nA"), ("sulfides", "20 nA"), ("oxides", "20 nA"), ("phosphates", "8 nA"),
          ("carbonates", "4 nA")], "15 kV, 20 nA ...; 8 nA; 4 nA")
    + per("Beam Mode", [("silicates", "focus"), ("sulfides", "focus"), ("oxides", "focus"), ("phosphates", "defocus"),
          ("carbonates", "defocus")], "a focused beam; a 2-µm defocused beam size")
    + per("Beam Diameter", [("phosphates", "2 µm"), ("carbonates", "2 µm")], "A 2-μm defocused beam size")
    + per("Beam Damage Minimization", [("phosphates", "defocus"), ("carbonates", "defocus")], "A 2-µm defocused beam size, lower beam currents and shorter count times ... to minimize possible beam damage effects")
    + [("Peak Counting Time", None, ["20 s"], "20 s peak time (silicates, sulfides, oxides; phosphates)"),
       ("Peak Counting Time", None, ["10 s"], "10 s peak (carbonates)"),
       ("Background Counting Time", None, ["10 s"], "10 s on each background"),
       ("Background Counting Time", None, ["5 s"], "5 s background (carbonates)")],

  "Barnes+2025#JEOL": [
    ("Instrument Model", None, ["8230"], "JEOL JXA-8230 electron microprobe analyser"),
    ("WDS Spectrometer Configuration", None, ["five", "5 wavelength"], "equipped with five wavelength-dispersive spectrometers"),
    ("Accelerating Voltage", None, ["20 kV"], "an accelerating voltage of 20 kV"),
    ("Beam Current", "all", ["10 nA"], "a probe current of 10 nA"),
    ("Beam Diameter", "all", ["1 µm", "1 um"], "beam diameter of 1 µm"),
    ("Beam Mode", "carbonates", ["raster"], "For carbonates, we rastered the beam"),
    ("Beam Raster Dimensions", "carbonates", ["5 × 5", "5x5", "5 x 5"], "over 5 × 5 µm2"),
  ] + per("Primary Calibration Standard Name", [("all/Mg", "Springwater"), ("all/Si", "Springwater"), ("all/Fe", "fayalite"),
          ("all/Ca", "wollastonite"), ("all/Na", "albite"), ("all/Al", "albite"), ("all/K", "orthoclase"), ("all/Ti", "rutile"),
          ("all/Ni", "Ni metal"), ("all/Cr", "chromite"), ("all/Mn", "rhodochrosite")], "We used different standards ...")
    + per("Peak Counting Time", [("Al", "200 ms"), ("Ti", "200 ms"), ("Ca", "200 ms"), ("Mn", "200 ms"), ("Cr", "200 ms"),
          ("Mg", "20 ms"), ("Fe", "20 ms"), ("Si", "20 ms")], "The total peak + background counting time was ...")
    + per("Detection Limit", [("Mg", "0.025"), ("Fe", "0.025"), ("Si", "0.05"), ("K", "0.05"), ("Na", "0.05"), ("Ca", "0.005"),
          ("Al", "0.02"), ("Ti", "0.005"), ("Cr", "0.015"), ("Mn", "0.008")], "Detection limits were ..."),

  "Barnes+2025#Cameca": [
    ("Instrument Model", None, ["SX100"], "a CAMECA SX100 electron microprobe"),
    ("Accelerating Voltage", None, ["20 kV"], "Analyses were performed at 20 kV"),
    ("Beam Mode", "all", ["focus"], "using a focused 1-μm beam"),
    ("Beam Diameter", "all", ["1 µm", "1 um"], "a focused 1-μm beam"),
    ("Detection Limit", None, ["250 ppm"], "Typical detection limits for transition metals were around 250 ppm"),
  ],

  "Neuman+2025": [
    ("Instrument Model", None, ["8200"], "the JEOL JXA-8200 electron microprobe"),
    ("Pre-Analysis Imaging and Screening", None, ["2 nA"], "BSE images ... at 15 kV, 2 nA probe current, and 70x magnification"),
    ("X-ray Detection Method per Monitored Element", "all", ["WDS"], "fixed wavelength-dispersive spectrometers (WDS)"),
    ("Stage Scan vs. Beam Scan", None, ["stage"], "five EPMA stage maps"),
    ("Step Size / Pixel Size", None, ["9.5"], "a step size of 9.5 μm"),
    ("Mapping Beam Diameter", None, ["10 µm", "10 um"], "a fixed 10 μm electron beam"),
    ("Accelerating Voltage", None, ["15 kV"], "at 15 kV"),
    ("Mapping Beam Current", None, ["100 nA"], "100 nA probe current"),
    ("Dwell Time per Pixel", "all", ["25 msec", "25 ms"], "a dwell time of 25 msec"),
    ("Data Processing Software(s)", None, ["CalcImage"], "processed using Probe Software CalcImage"),
    ("Data Processing Software(s)", None, ["MATLAB"], "processed using a set of MATLAB routines"),
    ("Matrix Correction Method", None, ["Φ(ρz)", "phi-rho-z", "phi(rho z)", "ZAF"], "a full Φ(ρz) correction at each pixel"),
    ("X-ray Background Correction Method", "all", ["MAN"], "a mean atomic number (MAN) background calibration"),
    ("Detection Limit", "all", ["0.1-0.2"], "detection limits ... 0.1–0.2 element wt.% for all elements"),
  ] + per("Sequence", [("Mg", "pass 1"), ("Al", "pass 1"), ("Fe", "pass 1"), ("Ca", "pass 1"), ("Ti", "pass 1"),
          ("Na", "pass 2"), ("Si", "pass 2"), ("Mn", "pass 2"), ("K", "pass 2"), ("Cr", "pass 2")], "Two passes were used ..."),
}


# Which analytical modes each procedure covers, as its EPMA paragraph states them. Added because
# `Analytical Mode` is the field a record needs to know which mode-flagged fields apply. Where the paper
# names the detector, the fact is the list value; where it states only the geometry (point analyses,
# maps), the fact is the geometry alone — the closed list cannot hold it, so it can at best be commentary.
MODES = {
    "Ma+2015": ["WDS Point Analysis"], "Ma+2017": ["WDS Point Analysis", "K-mapping"],
    "Broussard+2026": ["WDS Point Analysis", "WDS Mapping"], "Pang+2016": ["WDS Point Analysis"],
    "McCoy+2025_UA": ["WDS Point Analysis"], "Neuman+2025": ["WDS Mapping"],
    "Hu+2020": ["point"], "Liu+2016_Cal": ["point"], "Liu+2016_UT": ["point", "map"],
    "Frank+2023": ["point", "map"], "Seifert+2026": ["point"], "McCoy+2025_SI": ["point"],
    "Zega+2025": ["point", "map"], "Barnes+2025#JEOL": ["point"], "Barnes+2025#Cameca": ["point"],
}
for _k, _ms in MODES.items():
    FACTS[_k] += [("Analytical Mode", None, [_m], "procedure performs: %s" % _m) for _m in _ms]
