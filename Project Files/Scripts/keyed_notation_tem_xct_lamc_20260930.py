#!/usr/bin/env python3
"""Keyed-value notation (conventions 7.3.4) for TEM, Lab-XCT and LA-MC-ICP-MS (2026-09-30).

    python3 "Project Files/Scripts/keyed_notation_tem_xct_lamc_20260930.py" [--apply] [--show]

The three smallest TAPPs in the keyed-notation backlog, converted as SEM was (sem_keyed_notation_20260929.py):
  * definer cells open with a member list, and the original cell follows as commentary after ` — `, so
    every transcribed quote survives. Target Material names what was analysed, not the sample;
  * keyed value cells take `all:` or name their members;
  * cells that already parse were reviewed for meaning too, since a description can parse by accident.

LA-MC is the first ICP-MS-style TAPP converted, and sets the pattern for the others:
  * acquisition-pass fields key to the one pass member (`all:` where there is one pass);
  * monitored masses bind to their target species with `→ Sr`, and interference monitors with `→ none`;
  * `standard x reported property` and `target material x target species` cells use `all [ … ]`.

Also fixed: the task-3 `Combination Method` cell for Zhang+2022 had a `;` inside its value.
All three TAPPs join `KEYED_NOTATION_ENFORCED` once every structured cell parses.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
D = " — "
P = "prepend"   # (P, members): members + " — " + the original cell

TASKS = {
 "Lab-XCT_TAPP_v": {
  ("Reported Variables and Units", 2): (P, "microchondrule and sulphide-silicate object diameter (µm); shape factor; object abundance; particle volume"),
 },
 "TEM_TAPP_v": {
  ("Target Material", 1): (P, "synthetic magnetite"),
  ("Target Material", 6): (P, "iron sulfides; pyroxene"), ("Target Material", 7): (P, "iron sulfides; pyroxene"),
  ("Target Material", 8): (P, "iron sulfides; pyroxene"),
  ("Target Material", 9): (P, "olivine"),
  ("Target Material", 10): (P, "basaltic impact glass"),
  ("Target Material", 11): (P, "carbonates; phyllosilicates; magnetite; sulfides; phosphates"),
  ("Target Material", 12): (P, "carbonates"),
  ("Target Material", 13): (P, '"Na,Ca carbonates"; phyllosilicates; sulfides'),
  ("Target Material", 14): (P, "CM2 carbonaceous chondrite"),
  ("Target Material", 16): (P, "apatite"), ("Target Material", 17): (P, "apatite"),
  ("Target Material", 18): (P, "pyroxene"), ("Target Material", 19): (P, "pyroxene"),
  ("Target Material", 20): (P, "lunar soil grains"), ("Target Material", 21): (P, "lunar soil grains"),
  ("Target Species", 2): ("set", "Si, Mg, Al, Fe, S, Ni, C" + D + "sheet silicates Si, Mg, Al, Fe; sulfides Fe, S, Ni; carbonates and nanoglobules C, Si, Fe"),
  ("Target Species", 10): ("set", "Ti, O, Fe" + D + "Cu Kα and Cu Kβ from the TEM grid were also detected"),
  ("Target Species", 12): ("set", "Mg, Ca, Fe, Mn, Si, Al, Cr, C, O, S, P" + D + "from Table 1"),
  ("Target Species", 13): ("set", "Na, Ca, C, O, Mg, Fe, Si, F, Cl" + D + "from Tables 1 and A1"),
  ("Target Species", 14): ("set", "Fe; Ni; S; Si; O; Mg; Ca" + D + "EDX maps of irradiated matrix, olivine, and sulfide sections"),
  ("Reported Variables and Units", 1): (P, "Fe concentration (at%); O concentration (at%); rim thickness (nm); d-spacing (Å); defect microstructure (nominal)"),
  ("Reported Variables and Units", 2): (P, "phase identification (nominal); d-spacing (nm); phase composition (At%); sulfide polytype (nominal); Fe3+/ΣFe"),
  ("Reported Variables and Units", 3): (P, "elemental distribution; phase composition (At%); phase identification (nominal)"),
  ("Reported Variables and Units", 4): (P, "phase identification (nominal); phase composition (At%)"),
  ("Reported Variables and Units", 5): (P, "phase identification (nominal); d-spacing (nm); phase composition (At%); sulfide polytype (nominal); Fe3+/ΣFe"),
  ("Reported Variables and Units", 6): (P, "rim structure (nominal); rim thickness (nm); solar-flare track density; iron whisker morphology (nominal); iron whisker crystallography (nominal); whisker length (nm)"),
  ("Reported Variables and Units", 7): (P, "iron sulfide composition; pyroxene end-member composition (En, Wo, Fs)"),
  ("Reported Variables and Units", 8): (P, "elemental distribution; phase identification (nominal); spatial relations of the phases (nominal)"),
  ("Reported Variables and Units", 9): (P, "quantitative element abundances; spatial distribution of elements; rim thickness (nm); rim structure (nominal); npFe presence (nominal); solar-flare track density (cm-2)"),
  ("Reported Variables and Units", 10): (P, "phase identification (nominal); unit-cell parameters (Å, Å3); space group (nominal); grain size (nm); composition (at%)"),
  ("Reported Variables and Units", 11): (P, "crystalline phase identification (nominal); carbonate microstructure (nominal); textural relations (nominal)"),
  ("Reported Variables and Units", 12): (P, "carbonate composition (mole%); MnO (wt%); FeO (wt%)"),
  ("Reported Variables and Units", 13): (P, "carbonate composition (at%); change in composition over time (at%); grain dimensions (nm); grain area (µm2); areal fraction of carbonates; phase identification (nominal)"),
  ("Reported Variables and Units", 14): (P, "rim microstructure (nominal); rim composition; melt-layer thickness (nm); nanoparticle size (nm); nanoparticle composition; vesicle and melt textures (nominal)"),
  ("Reported Variables and Units", 16): (P, "F, Cl, SiO2, P2O5, CaO, MnO, Fe2O3 (wt%); total (wt%); crystallinity (nominal); crystal orientation (nominal); textural relationships (nominal)"),
  ("Reported Variables and Units", 17): (P, "F, Cl, SiO2, P2O5, CaO, MnO, Fe2O3 (wt%); total (wt%); crystallinity (nominal); crystal orientation (nominal); textural relationships (nominal)"),
  ("Reported Variables and Units", 18): (P, "iron oxidation state (nominal); Fe oxidation-state distribution (nominal); nanophase iron particle size (nm); nanophase iron abundance; lamella width (nm); lamellar and rim microstructure (nominal)"),
  ("Reported Variables and Units", 19): (P, "iron oxidation state (nominal); Fe oxidation-state distribution (nominal); nanophase iron particle size (nm); nanophase iron abundance; lamella width (nm); lamellar and rim microstructure (nominal)"),
  ("Reported Variables and Units", 20): (P, "elemental maps; phase identification (nominal); lattice spacing"),
  ("Reported Variables and Units", 21): (P, '"Fe L3,2 spectra"; Fe oxidation state (nominal)'),
  ("EDS Detection Limit", 12): ("set", "all: <0.1 wt%" + D + "stated for TEM EDS measurements"),
  ("EDS Detection Limit", 15): ("set", "all: ~1000 ppm (~0.1 wt%)" + D + "for major elements; a general statement in a review, not a measured value"),
  ("EELS Detection Limit", 15): ("set", "all: ~10 ppm" + D + "STEM-EELS, for transition metals and lanthanides in powdered glass with high beam stability; a general statement in a review"),
  ("EELS Edges", 19): ("set", '"Fe L2,3 edge" (700–735 eV) → Fe; "O K-edge" (528–550 eV) → O'),
  ("EELS Edges", 21): ("set", '"Fe L3,2 edge" (~707–709 eV) → Fe' + D + "L3 peak at 707.7 eV for Fe⁰, 707.2 eV for Fe²⁺, 709.0 eV for Fe³⁺"),
 },
 "LA-MC-ICPMS_TAPP_v": {
  ("Target Species", 1): ("set", "Rb, Sr" + D + "the paper determines ⁸⁷Sr/⁸⁶Sr and ⁸⁷Rb/⁸⁶Sr; p.2 'to monitor Kr, Rb, Er, Yb, and Sr' names Kr, Er and Yb as monitored, not determined — they carry the interference corrections and have no parent species"),
  ("Target Material", 1): ("set", "lunar meteorite silicates (plagioclase, pyroxene, ilmenite, glass)"),
  ("Monitored Masses", 1): ("set", "⁸⁴Sr, ⁸⁶Sr, ⁸⁷Sr, ⁸⁸Sr → Sr; ⁸⁵Rb → Rb; ⁸³Kr, ¹⁶⁷Er²⁺, ¹⁷³Yb²⁺ → none" + D + "Table 1 'Cup-configuration', p.2; ⁸³Kr is the gas background monitor, ¹⁶⁷Er²⁺ and ¹⁷³Yb²⁺ the interference monitors"),
  ("Secondary Reference Materials", 1): ("set", "NHB-9, YY12-01 (natural clinopyroxenes); YG4301 (anorthite)" + D + "measured as unknowns for ⁸⁷Sr/⁸⁶Sr data quality evaluation; reference values in Table 2"),
  ("Collision/Reaction Cell (CRC) Configuration", 1): ("set", "all: Not installed" + D + "'traditional (MC-)ICP-MS without the reaction/collision cell' (p.1); contrasted against 'MC-ICP-MS with collision cell' in the conclusion (pp.8-9)"),
  ("Faraday Cup Amplifier Resistor Values", 1): ("set", "all: 10¹¹ Ω" + D + "on all nine Faraday cups (p.2)"),
  ("Collector Configuration", 1): ("set", "⁸³Kr: L4; ¹⁶⁷Er²⁺: L3; ⁸⁴Sr: L2; ⁸⁵Rb: L1; ⁸⁶Sr: C; ¹⁷³Yb²⁺: H1; ⁸⁷Sr: H2; ⁸⁸Sr: H3" + D + "static multi-collection, one configuration throughout (Table 1 'Cup-configuration', p.2; array spans L4–H3, p.2)"),
  ("Integration Time per Cycle", 1): ("set", "all: 0.524 s" + D + "one block of 120 cycles = 62.88 s total"),
  ("Interfering Species", 1): ("set", "⁸⁴Sr: ¹⁶⁸Er²⁺; ⁸⁵Rb: ¹⁷⁰Er²⁺ + ¹⁷⁰Yb²⁺; ⁸⁶Sr: ¹⁷²Yb²⁺; ⁸⁷Sr: ¹⁷⁴Yb²⁺ and ⁸⁷Rb (isobaric); other: N"),
  ("Interference Correction Method", 1): ("set", "⁸⁴Sr, ⁸⁵Rb, ⁸⁶Sr: doubly charged Er and Yb corrected with the measured ¹⁶⁷Er²⁺ and ¹⁷³Yb²⁺ signals and natural isotope ratios; ⁸⁷Sr: doubly charged Yb corrected the same way, then ⁸⁷Rb isobaric correction from the measured ⁸⁵Rb signal and ⁸⁷Rb/⁸⁵Rb with exponential-law mass bias; other: N" + D + "sequential: (a) the doubly charged corrections, then (b) the ⁸⁷Rb correction"),
  ("Laser Spot Geometry", 1): ("set", "all: 50–60 µm circular"),
  ("Laser Spot Path / Ablation Mode", 1): ("set", "all: Transect" + D + "continuous line scan at 2–6 µm s⁻¹"),
  ("Laser Repetition Rate", 1): ("set", "all: 10–30 Hz" + D + "varied based on Sr concentration in samples"),
  ("Transect Rate, Mapping Rate or Step Size", 1): ("set", "all: 2–6 µm s⁻¹" + D + "varied based on Sr concentration in target minerals"),
  ("Mass Resolution Assignment", 1): ("set", "all: low resolution" + D + "for all eight monitored masses: 'the mass spectrometer was operated in low mass resolution mode' (p.3); Table 1 'Instrument resolution ~ 400 (low mode)'"),
  ("Inter-Pass Data Dependency", 1): ("set", "N/A" + D + "a single acquisition pass, so there is no dependency between passes; one line scan per location (1 block of 120 cycles at 0.524 s integration)"),
  ("Number of Cycles per Block", 1): ("set", "all: 120" + D + "Table 1, 'Cycles of each block 120' (p.3)"),
  ("Internal Standard Approach", 1): ("set", "all: no conventional internal standard, external calibration only" + D + "Rb/Sr elemental fractionation corrected by a series of reference glasses; ⁸⁷Sr/⁸⁶Sr mass bias corrected by exponential law using ⁸⁸Sr/⁸⁶Sr = 8.37521"),
  ("Internal Standard Element", 1): ("set", "all: none" + D + "no conventional internal standard; ⁸⁵Rb is used to calculate ⁸⁷Rb/⁸⁶Sr via ⁸⁷Rb/⁸⁵Rb, and Rb/Sr elemental fractionation is calibrated externally with reference glasses"),
  ("Elemental Fractionation Correction", 1): ("set", "all: Rb/Sr fractionation corrected externally with a series of reference glasses, with no explicit downhole correction" + D + "the femtosecond laser substantially reduces elemental fractionation; the exponential law corrects Sr isotope mass bias (⁸⁸Sr/⁸⁶Sr = 8.37521)"),
  ("Uncertainty Propagation Method", 1): ("set", "⁸⁷Sr/⁸⁶Sr, ⁸⁷Rb/⁸⁶Sr: standard error (SE = SD/√n) for repeatability within individual runs, assessed from a signal-intensity regression; other: N"),
  ("Normalization / Standards-Based Correction", 1): ("set", "⁸⁷Sr/⁸⁶Sr: ⁸⁸Sr/⁸⁶Sr = 8.37520933 with the exponential law; ⁸⁷Rb/⁸⁶Sr: ⁸⁷Rb/⁸⁵Rb = 0.385706 and ⁸⁶Sr/⁸⁸Sr = 0.119351, with the external calibration factor from reference glasses; other: N"),
  ("Calibration Factor and Determination Method", 1): ("set", "⁸⁷Rb/⁸⁶Sr: average correction factor from a series of reference glasses, value not stated; other: N" + D + "'A series of reference glasses was analyzed to provide an average correction factor. Then the average factor was used for the samples and reference materials' (p.4); determined with ISO-Compass software"),
  ("Combination Method", 1): ("set", "Rb–Sr isochron age, initial ⁸⁷Sr/⁸⁶Sr: isochron regression per meteorite and data group, by IsoplotR and by Monte Carlo linear fitting, one point per run for the Normal group and every cycle for the SUIA group; other: N" + D + "Table 3; Figs 6 and 7; 'This data reduction method was called the smallest unit isochron age (SUIA)'"),
  ("Primary Calibration Standard Name", 1): ("set", "all [Rb: series of reference glasses (NIST 612, BHVO-2G, BCR-2G, NKT-1G, TB-1G, ATHO-G, KL2-G, ML3B-G, StHs6/80-G, T1-G); Sr: N]" + D + "the glasses calibrate ⁸⁷Rb/⁸⁶Sr; Sr is internally normalised to ⁸⁸Sr/⁸⁶Sr; NIST 610 was used for instrument parameter optimization; NHB-9, YY12-01 and YG4301 were unknowns for ⁸⁷Sr/⁸⁶Sr quality evaluation"),
  ("Within-Session Analytical Precision and Assessment Method", 1): ("set", "all [⁸⁷Sr/⁸⁶Sr, ⁸⁷Rb/⁸⁶Sr: standard error at 95% confidence (USE) per individual run, dependent on signal intensity]" + D + "regression in Fig. 3; relative errors for ⁸⁷Rb/⁸⁶Sr ±3% for most reference glasses, and for ⁸⁷Sr/⁸⁶Sr <0.2‰ where ⁸⁷Rb/⁸⁶Sr <1"),
  ("Analytical Accuracy and Assessment Method", 1): ("set", "all [⁸⁷Sr/⁸⁶Sr: relative error <0.2‰ where ⁸⁷Rb/⁸⁶Sr <1 (12 of 14 reference materials); ⁸⁷Rb/⁸⁶Sr: within ±3% for 11 glasses]" + D + "exceptions NIST 610 (−2.97%), NIST 612 (+2.02%), ATHO-G (+2.89%), all within the stated ±3% criterion"),
  ("Goodness-of-Fit or Dispersion Statistic", 1): ("set", "Rb–Sr isochron age, initial ⁸⁷Sr/⁸⁶Sr: MSWD from IsoplotR; other: N" + D + "Table 3: NWA 10597 Normal group 24, SUIA group 1.5; NWA 6950 Normal group 21, SUIA group 1.5. The high Normal-group values are attributed to large dispersion, 'especially for the data with ⁸⁷Rb/⁸⁶Sr ranging from 0.05 to 0.15' measured in pyroxenes (p.7)"),
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


def edit(rr, tasks, report):
    h = rr[0]; s = h.index("Literature Assessment")
    cols = [j for j in range(s + 1, len(h)) if h[j].strip()]
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for (f, n), (how, v) in tasks.items():
        if f not in by:
            raise SystemExit("PREMISE: no field %r" % f)
        j = cols[n - 1]; old = by[f][j]
        if how == P:
            if old.startswith(v + D):
                continue
            if not old.strip() or old.strip() in ("N", "N/A"):
                raise SystemExit("PREMISE: [%d] %s is %r" % (n, f, old))
            new = v + D + old
        else:
            new = v
            if not old.strip():
                raise SystemExit("PREMISE: [%d] %s is blank" % (n, f))
        if old != new:
            report.append((n, f, old, new)); by[f][j] = new
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    todo = []
    for pre, tasks in TASKS.items():
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(pre))
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        report = []
        edit(rows_of(os.path.join(ROOT, rel)), tasks, report)
        print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
        if "--show" in sys.argv:
            for n, f, old, v in report:
                print("    [%d] %s\n        now: %s" % (n, f, v[:170]))
        todo.append((e, rel, new, tasks))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new, tasks in todo:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), tasks, []))
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
