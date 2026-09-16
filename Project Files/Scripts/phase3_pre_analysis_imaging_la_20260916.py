#!/usr/bin/env python3
"""Phase 3 for `Pre-Analysis Imaging and Screening` — batch 2: the laser-ablation family (26 cells).

    python3 "Project Files/Scripts/phase3_pre_analysis_imaging_la_20260916.py" [--apply]

Same source rule and the same boundary as batch 1: characterisation done BEFORE the measurement to
select or locate the unit, not imaging the procedure performs as its own measurement.

ONE LA-SPECIFIC READING, stated here because it decides five cells. Electron-probe work that precedes
the ablation counts as screening when the paper uses it to locate or qualify the unit — and in three
of these papers it does more than locate: the EMP values become the internal standard the LA data are
normalised to (Liu 2016, Liu 2025). That is the strongest possible form of "how individual analyses
are linked back", so it is recorded with the imaging.

The already-filled Wu 2023 cell (LA-Q only) is left alone; LA-MC is not touched.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Pre-Analysis Imaging and Screening"

NAKANISHI = ("Secondary-electron imaging on the EPMA, used to place every spot — \"Based on the secondary electron "
             "images taken by EPMA, we selected analytical spots for LA-ICP-MS and sampling spots for micro-milling\" "
             "(p.4); the spots carry numbers (\"spot No.\" 201, 202 …) that tie the analyses back to those images "
             "(table p.6)")
LIU2024 = ("N — the fused glass discs are prepared for XRF and then ablated directly; no imaging or screening step is "
           "described before the LA-ICP-MS spots, whose grid is laid out to cover the whole disc (p.5)")
LIU2025 = ("Optical microscopy, then EMP — \"Following examination by optical microscopy to ascertain the integrity of "
           "the experiments and the state of the oxygen buffers, the solid components of the run products were "
           "analysed for major elements, S and Cu, using a JEOL JXA-8230 electron microprobe (EMP)\" (p.2); those EMP "
           "values are then the internal standards for the LA data, \"with Si and Fe obtained from EMP analyses as the "
           "internal standards\" (p.4)")
LIU2016 = ("Petrographic microscopy, SEM and EMP — \"The petrography of these sections was examined using a "
           "petrographic microscope and a scanning electron microscope\", followed by BSE images and element maps "
           "(p.3); the EMP results then serve as internal standards for the ablation data, which are normalised using "
           "\"EMP CaO or MgO values\" for silicates and \"40Ca counts to CaO concentrations from the EMP analysis\" "
           "for phosphate (p.4)")
BZHANG = ("Electron-microprobe mapping, for the pallasites only — \"Quantitative analysis, mixed WDS/EDS element "
          "mapping, and characterization of the mineral phases from NWA 1911 and Zinder were performed\" on the "
          "Bruker instrument, producing Si, Al, Cr, Fe, Mg, Ca, Na, P and Ni maps \"along with backscattered electron "
          "(BSE) maps\" at 6 μm per pixel (pp.5–6); for the irons the paper states only that the rasters were \"taken "
          "on polished surfaces\" (p.5)")
CHERN = ("μXRF mapping of larger sections, on which the ablation is sited — Fe Kα intensity maps identify the mineral "
         "phases \"based on the intensities of the Kα lines of the constituent major elements (Fe, Mg, Ni, Cr, S, Ca "
         "and P)\", and the LA-ICP-MS areas correspond \"to the locations indicated on the larger μXRF maps as black "
         "rectangles\" (p.4). The instrument is a Bruker M4 Tornado with a Rh-anode source at 50 kV and 150 μA, "
         "focused to \"a 25 μm spot (measured for Mo Kα)\" (p.3)")
MITTLE = ("SEM imaging of the grain mounts, used to place the spots — \"The grains were first imaged using a scanning "
          "electron microscope (SEM) to locate regions for analysis. Regions containing surface inclusions were "
          "avoided for analysis\" (p.5); the grains are the same mounts already used for EMPA (p.5)")
NAVARRO_SP = ("N — the preparation is stated without an imaging step: \"Before analyses, fragments about 1 cm were "
              "mounted in epoxy resin, polished, and cleaned with ultrapure water\" (p.3). The meteorites' structural "
              "classes were known beforehand (Table 1, p.2) but no screening of this material is described")
NAVARRO_MAP = ("Chemical etching to reveal the phases before mapping — \"For the mapping experiment, the polished "
               "surface of the Augusto Pestana sample was etched with freshly prepared Nital solution (2% v/v HNO3 ... "
               "in 99.5% absolute ethanol) to reveal the presence of different phases (in this case, kamacite and "
               "plessite)\" (p.3). Not imaging, but the screening step that sites the map")

LAQ = {"Nakanishi": NAKANISHI, "Liu et al. 2024": LIU2024,
       "Liu et al. 2025 (GCA 393) Experimental silicate glass": LIU2025,
       "Liu et al. 2025 (GCA 393) Experimental sulfide": LIU2025,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Silicates": LIU2016,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Phosphate": LIU2016}
LASF = {"Zhang et al. 2022 (GCA 323)": BZHANG,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Raster": CHERN,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Line": CHERN,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite phosphate": CHERN,
        "Mittlefehldt": MITTLE,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": NAVARRO_SP,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": NAVARRO_MAP}

CELLS = {
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v85.csv": dict(LAQ),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v85.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v82.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v83.csv": dict(LASF),
}


def col(header, key):
    k = " ".join(key.split()).lower()
    hits = [i for i, h in enumerate(header) if " ".join(h.split()).lower().startswith(k)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    plan = []
    for rel, cells in CELLS.items():
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        m = {col(h, k): v for k, v in cells.items()}
        if len(m) != len(cells):
            raise SystemExit("%s: two keys matched one column" % rel)
        unhandled = [" ".join(h[i].split())[:60] for i in lit if i not in m and not row[i].strip()]
        if unhandled:
            raise SystemExit("%s: blank columns with no value: %s" % (rel, unhandled))
        for i, v in m.items():
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = v
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, len(m)))
        print("  %-40s %2d cells -> %s" % (os.path.basename(rel), len(m), os.path.basename(new)))
    print("\n  %d cells in %d TAPPs" % (sum(p[3] for p in plan), len(plan)))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for rel, new, rows, _ in plan:
        with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        next(e for e in reg["composed"] if e["tapp"] == rel)["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
