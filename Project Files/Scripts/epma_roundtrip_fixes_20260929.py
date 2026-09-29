#!/usr/bin/env python3
"""EPMA fixes from the cells round-trip (Project Files/Reports/EPMA_Cells_RoundTrip_2026-09-29), 2026-09-29.

    python3 "Project Files/Scripts/epma_roundtrip_fixes_20260929.py" [--apply]

1. `Analytical Mode`, never assessed in 14 of 15 columns. It is a closed list that pairs a detector
   with a geometry (WDS Point Analysis ...). Six papers name the detector for their EPMA work (Ma+2015,
   Ma+2017, Broussard+2026, Pang+2016, McCoy+2025_UA, Neuman+2025) and get a value. The other nine
   state a geometry (point analyses, maps) but not WDS or EDS, so the cell is `N` with the geometry as
   commentary — the list has no value for "point analysis, detector not stated".
2. Liu+2016_UT `X-ray Line`: the map lines the paper states ("Ca Ka, Al Ka, Fe Ka, and Mg Ka"; "Fe Ka,
   P Ka, Al Ka, Ca Ka, and Cr Ka").
3. Unkeyed cells re-read against the papers (the pilot had covered keyed and definer cells only):
   inferences removed (Hu+2020 "WDS"; Broussard+2026 "EDS not used"; Barnes+2025 "possibly per-pixel";
   Barnes NHM "implied" analytes; McCoy+2025_SI spectrometer lines; Seifert+2026 halogen correction on
   oxygen), cells describing another laboratory's work corrected (McCoy+2025_SI preparation and
   screening; McCoy+2025_UA screening; an LA-ICP-MS clause in Liu+2016_Cal), a matrix correction
   recorded as software moved out, stale notes updated (Frank+2023 secondary RMs), over-precise
   backgrounds ("each side") corrected, and "EPMA-WDS" dropped from three procedure names whose papers
   never say WDS.

Each edit is either a whole new value, or (old substring, new substring) with the old substring as a
premise.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "
NODET = "; WDS or EDS is not stated, and the list has no value without one"

EDITS = {
  "Ma+2015": {
    "Analytical Mode": "WDS Point Analysis" + D + "'WDS: 15 kV; 5 nA; beam in focused mode'; point analyses only",
    "Data Processing Software(s)": ("N" + D + "the 'CITZAF correction procedure' is recorded under Matrix Correction "
                                    "Method; the only software named is Probe for EPMA"),
  },
  "Hu+2020": {
    "Analytical Mode": "N" + D + "quantitative point analyses ('Quantitative analyses of maskelynite ... were conducted by electron probe microanalysis')" + NODET,
    "Procedure Name": ("EPMA-WDS Major Element", "EPMA Major Element"),
    "Data Processing Software(s)": "N" + D + "'The Bence-Albee method was used' is recorded under Matrix Correction Method; no software is named",
    "Additional Notes": [("point analysis WDS only", "point analysis only; WDS or EDS not stated"),
                         ("Detection limits 0.01-0.06 wt% stated per element", "Detection limits 0.01-0.06 wt% stated per oxide")],
  },
  "Liu+2016_UT": {
    "Analytical Mode": "N" + D + "quantitative point analyses and elemental X-ray maps" + NODET,
    "X-ray Line": ("Ca, Al, Fe, Mg, P, Cr: Ka; other: N" + D + "maps: 'Ca Ka, Al Ka, Fe Ka, and Mg Ka' (four sections) "
                   "and 'Fe Ka, P Ka, Al Ka, Ca Ka, and Cr Ka' (two olivine megacrysts); no line is stated for the point "
                   "analyses"),
  },
  "Liu+2016_Cal": {
    "Analytical Mode": "N" + D + "quantitative point analyses" + NODET,
    "Procedure Name": ("EPMA-WDS Major Element", "EPMA Major Element"),
    "Analysis Inclusion and Rejection Criteria": ("; the plateau-region screening of each spot is a signal-based step "
                                                  "recorded under Spike / Outlier Filtering Approach", ""),
  },
  "Ma+2017": {
    "Analytical Mode": ("WDS Point Analysis" + D + "'WDS: 15 kV, 5 nA'; the paper also mentions 'K-mapping by EPMA', "
                        "with no detector or conditions"),
    "Data Processing Software(s)": ("N" + D + "the 'CITZAF correction procedure' is recorded under Matrix Correction "
                                    "Method; the only software named is Probe for EPMA"),
  },
  "Frank+2023": {
    "Analytical Mode": "N" + D + "point analyses and X-ray mapping ('electron microprobe, and X-ray mapping')" + NODET,
    "Additional Notes": ("Secondary standards: USNM San Carlos olivine (Fo90); Kakanui kaersutite.",
                         "No EPMA secondary standard is named (San Carlos olivine standardised the SIMS work)."),
  },
  "Broussard+2026": {
    "Analytical Mode": ("WDS Point Analysis; WDS Mapping" + D + "'wavelength-dispersive quantitative compositional "
                        "mapping and analysis'"),
    "Additional Notes": ("EDS spectrometer present but not used for quantitative analyses.",
                         "An EDS spectrometer is on the instrument; its use is not stated."),
  },
  "Seifert+2026": {
    "Analytical Mode": "N" + D + "14 quantitative point analyses" + NODET,
    "Halogen Correction on Oxygen": ("N" + D + "OH is 'calculated by difference based on 1–F–Cl=OH' (under Target Species "
                                     "Estimation Method); no oxygen-equivalent correction for F and Cl is stated"),
    "Additional Notes": ("Halogen correction on O: Yes. ", ""),
  },
  "Pang+2016": {
    "Analytical Mode": "WDS Point Analysis" + D + "'Electron Probe Micro-Analyzer (EPMA) with wavelength dispersive spectrometers (WDS)'",
  },
  "McCoy+2025_SI": {
    "Analytical Mode": "N" + D + "point analyses with named crystals (LIFL, TAPL, PETL)" + NODET,
    "Procedure Name": ("EPMA Carbonate, Magnetite and Olivine Composition, Bennu (Smithsonian, JEOL 8530F+ Hyperprobe)"),
    "WDS Spectrometer Configuration": ("N" + D + "the crystals (LIFL, TAPL, PETL) are recorded under Diffracting Crystal; "
                                       "the spectrometer configuration and the X-ray lines are not stated"),
    "Sample Preparation Method": ("Ir-coated specimens" + D + "'Electron microprobe analysis was conducted on Ir-coated "
                                  "specimens'; the mounting for the microprobe work is not stated"),
    "Pre-Analysis Imaging and Screening": ("SEM mapping at the Smithsonian" + D + "particles 'analysed at 15 kV and around "
                                           "0.5 nA in high vacuum using a Thermo Fisher Quattro FE-SEM'; 'Maps of loose "
                                           "grains were investigated, then used to inform sectioning' (p.7)"),
    "Additional Notes": ("Silicate/oxide analyses: 15 kV, 10 nA, 1 µm spot; broader standard suite.",
                         "Magnetite and olivine analyses: 15 kV, 10 nA, 1 µm spot; their own standard suite."),
  },
  "McCoy+2025_UA": {
    "Analytical Mode": "WDS Point Analysis" + D + "'Wavelength-dispersive X-ray spectroscopy analyses of Mg,Na phosphate'",
    "Pre-Analysis Imaging and Screening": ("N" + D + "the paper describes SEM characterisation at JSC, the NHM, the "
                                           "Smithsonian and Curtin, not for the K-ALFAA microprobe work"),
  },
  "Zega+2025": {
    "Analytical Mode": ("N" + D + "quantitative point analyses and X-ray maps ('BSE images, element maps and quantitative "
                        "compositional analyses')" + NODET),
    "Additional Notes": ("Silicates/sulfides/oxides: 15 kV, 20 nA, focused, 20 s peak, 10 s/bg each side. Phosphates: 15 kV, "
                         "8 nA, 2 µm defocused, 20 s peak, 10 s/bg each side. Carbonates: 15 kV, 4 nA, 2 µm, 10 s peak, "
                         "5 s/bg each side.",
                         "Silicates/sulfides/oxides: 15 kV, 20 nA, focused, 20 s peak, 10 s on each background. Phosphates: "
                         "15 kV, 8 nA, 2 µm defocused, 20 s peak and 10 s background. Carbonates: 15 kV, 4 nA, 2 µm "
                         "defocused, 10 s peak and 5 s background."),
  },
  "Barnes+2025#JEOL": {
    "Analytical Mode": ("N" + D + "quantitative point analyses on an instrument 'equipped with five wavelength-dispersive "
                        "spectrometers and one silicon drift detector energy dispersive spectrometer'; which detector "
                        "measured which element is not stated"),
    "Additional Notes": (" — unusually short, possibly per-pixel for fast mapping mode", ""),
  },
  "Barnes+2025#Cameca": {
    "Analytical Mode": "N" + D + "point analyses ('Analyses were performed at 20 kV, using a focused 1-μm beam')" + NODET,
    "Additional Notes": ("Analyte list not explicitly given; implied Si, Mg, Fe, Ca, Mn, Cr, Ni, Al, Ti from context.",
                         "Analyte list not given."),
  },
  "Neuman+2025": {
    "Analytical Mode": ("WDS Mapping" + D + "'five EPMA stage maps were acquired using fixed wavelength-dispersive "
                        "spectrometers (WDS)'"),
    "EDS Detector Configuration": "N/A" + D + "WDS mapping procedure",
  },
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


def columns(h):
    s = h.index("Literature Assessment"); out = {}
    for j in range(s + 1, len(h)):
        lab = h[j].replace("\n", " ")
        if not lab.strip():
            continue
        key = lab.split("|")[0].strip()
        if key == "Barnes+2025":
            key += "#JEOL" if "JEOL" in lab else "#Cameca"
        out[key] = j
    return out


def edit(rr, report):
    cols = columns(rr[0]); by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for key, fields in EDITS.items():
        j = cols[key]
        for f, spec in fields.items():
            r = by[f]; old = r[j]
            specs = spec if isinstance(spec, list) else [spec]
            new = old
            for s in specs:
                if isinstance(s, tuple):
                    if s[0] not in new:
                        raise SystemExit("PREMISE: [%s] %s lacks %r" % (key, f, s[0][:60]))
                    new = new.replace(s[0], s[1], 1)
                else:
                    new = s
            if new != old:
                report.append((key, f, old, new)); r[j] = new
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith("EPMA_TAPP_v"))
    rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
    report = []
    edit(rows_of(os.path.join(ROOT, rel)), report)
    print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
    for key, f, old, v in report:
        print("  [%s] %s\n      was: %s\n      now: %s" % (key, f, old[:120], v[:120]))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0
    np_ = os.path.join(ROOT, new)
    q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                       + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
    if q.returncode != 0:
        raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
    write(np_, edit(rows_of(np_), []))
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
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
