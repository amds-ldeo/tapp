#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Selection Criteria` — batch 3: the SEM family (70 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_selection_sem_20260916.py" [--apply]

Same source rule and the same line against `Sampling Unit Type` as batches 1-2.

SEM IS THE MOST N-HEAVY CORPUS FOR THIS FIELD, and the reason is the opposite of LA's. A laser
destroys its target, so a paper defends where it put the beam; an electron image is free and
repeatable, so papers image what they image and say nothing about choosing. The criteria that do
appear are of one kind: a PRIOR SURVEY that located the units — optical-CL before Gucsik's spectra,
μXRD reconnaissance before Izawa's SEM work, VIS-IR spectral imaging before Pascucci's fields, and
NanoSIMS isotope imaging before Barnes's two EDS targets.

Barnes 2025's BSE and two FIB columns are N because the paper does not contain those procedures at
all, as their own `Additional Notes` record.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Selection Criteria"
FILES = ["SEM/SEM_TAPP_v70.csv", "SEM/SEM_Composition_TAPP_v69.csv", "SEM/SEM_FIBSEM_TAPP_v36.csv",
         "SEM/SEM_Imaging_TAPP_v35.csv"]

GUCSIK = ("Freedom from defects, after a prior survey — \"Following a systematic optical microscope"
          "cathodoluminescence study of a Kaba thin section, seven representative grains (designated as B-1 "
          "through B-7) were selected for further analyses because they did not contain any irregular "
          "fracturing or crystallographic imperfections\" (p.2)")
IZAWA_FIRST = ("Located by prior μXRD reconnaissance — the paper's stated strategy is \"an initial, non-destructive "
               "in situ reconnaissance step using micro X-ray diffraction (mXRD) ... to identify features of "
               "interest, followed by spatially correlated mXRD, scanning electron microscopy with "
               "energy-dispersive X-ray spectroscopy (SEM-EDX), and cathodoluminescence (CL) analysis\" (p.2)")
IZAWA_SECOND = ("Follow-up on features already located — this is the third stage of the paper's strategy, \"finally "
                "higher resolution SEM-BSE mapping to establish spatial context for textural variation\" (p.2), on "
                "features identified by the earlier μXRD and SEM-EDX/CL stages")
PASC = ("Spatial co-registration with the spectral imagery — the SEM work targets \"almost the same portion of the "
        "VIS-IR SPIM images\" (p.4), so that the two datasets can be compared on the same area of the slab")
LIU_NONE = ("N — the selection stated is of samples, not units: \"Two highrank coals formed from regional "
            "metamorphism collected from the southern Qinshui basin were selected\" (p.1); no rule is given for the "
            "imaged areas")
ZEGA_UNSPEC = ("N — the passage says regions of interest were characterized (\"Characterization of regions of "
               "interest was performed at an accelerating voltage of 15 kV\", p.9) but gives no rule for choosing "
               "them")
ZEGA_NONE = "N — the passage states the mounting and imaging conditions only, and no rule for choosing units (p.9)"
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"),
     "N — no rule is given for which globules were imaged; the stated criterion is at sample level, \"Several "
     "millimeter-sized pieces of the pristine Tagish Lake meteorite free of fusion crust were digested in HCl and "
     "HF in order to concentrate the carbonaceous materials\" (p.1)"),
    (("Garvie et al. 2008", "TEM Sample Preparation"),
     "N — the paper claims the capability without stating a rule: \"The rapid site-specific cross-sectioning "
     "capabilities of the FIB allow the preservation of the internal morphology of the nanoglobules\" (p.1), but "
     "which globules were sectioned is not said"),
    (("Genge et al. 2025", "BSE Imaging"),
     "N — the target phases are named (see `Sampling Unit Type`) but no rule is given for choosing the imaged areas"),
    (("Genge et al. 2025", "EDS Point Analysis"),
     "N — the target phases are named (see `Sampling Unit Type`) but no rule is given for choosing the analysed "
     "points"),
    (("Genge et al. 2025", "EBSD"),
     "N — no rule is given for choosing which grains were indexed"),
    (("Gucsik et al. 2013", "CL Mapping"), GUCSIK),
    (("Gucsik et al. 2013", "EDS Point Analysis"),
     GUCSIK + "; the same grains carry the microprobe analyses"),
    (("Izawa et al. 2010", "CL Mapping"), IZAWA_FIRST),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"), IZAWA_FIRST),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"), IZAWA_FIRST),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"), IZAWA_SECOND),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"), IZAWA_SECOND),
    (("Liu et al. 2017", "3D Tomography"),
     "N — the paper states the scope of the model rather than a rule for siting the volume: it \"only focuses on "
     "the coal sample #1\" (p.8)"),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"), LIU_NONE),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"), LIU_NONE),
    (("Ma et al. 2017", "BSE Imaging"),
     "N — the imaged occurrences are shown rather than chosen by a stated rule; the three mineral locations are "
     "\"marked by rectangles\" in Fig. 1 (p.2) within \"section 126A of USNM 7908\" (p.1)"),
    (("Ma et al. 2017", "EBSD"),
     "N — no rule is given for choosing which crystals were indexed; the patterns are reported for the type and "
     "associated crystals as they occur (Fig. 3, p.3)"),
    (("Pascucci et al. 2026", "BSE Imaging"), PASC),
    (("Pascucci et al. 2026", "EDS Point Analysis"), PASC),
    (("Pascucci et al. 2026", "EDS Mapping"), PASC),
    (("Pascucci et al. 2026", "| SE Imaging"), PASC),
    (("Zhou et al. 2017", "3D Tomography"),
     "Stated, but by procedure rather than by criterion — \"an area within the coal sample was selected for FIB-SEM "
     "tomography\" following a published procedure (p.3), and the volume's adequacy is then tested under "
     "\"evaluation of representative volumes\" (§2.3, p.4); no rule is given for where the area was placed"),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"), ZEGA_UNSPEC),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"), ZEGA_UNSPEC),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"), ZEGA_NONE),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"), ZEGA_NONE),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"),
     "Coverage of heterogeneity — \"The compositional heterogeneity of the particles was assessed through EDS "
     "mapping\" (p.9); no finer rule is given for placing the maps"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"),
     "Position within the particle — \"All sections were extracted from varied regions of matrix within the "
     "particles\" (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"),
     "N — the passage states only how particles were mounted, \"Bennu particles were placed on PELCO carbon "
     "conductive tabs\" (p.9), and no rule for choosing where to cut"),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"),
     "N — the passage states only that \"FIB sections were prepared from particles dispersed on conductive carbon "
     "dots on Al SEM pin mounts\" (p.10), and no rule for choosing where to cut"),
    (("Zega et al. 2025", "CL Mapping"), ZEGA_NONE),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"),
     "Isotopic anomaly, found by prior NanoSIMS imaging — grains \"were considered presolar if their isotopic "
     "composition differed from the reference ratios by >5σ and if the isotopic anomaly was present in multiple "
     "consecutive frames\", and of those \"Two O-rich presolar grains were also analysed by SEM-EDS to further "
     "constrain the phase\" (p.11)"),
    (("Barnes et al. 2025", "BSE Imaging (FEI Quanta"), BARNES_NONE),
    (("Barnes et al. 2025", "TEM Sample Preparation (FEI Helios G4"), BARNES_NONE),
    (("Barnes et al. 2025", "TEM Sample Preparation (FEI Helios 660"), BARNES_NONE),
]


def value_for(header):
    hs = " ".join(header.split())
    hits = [v for parts, v in VALUES if all(p in hs for p in parts)]
    if len(hits) != 1:
        raise SystemExit("header %r matched %d value entries" % (hs[:90], len(hits)))
    return hits[0]


def main(apply=False):
    plan, used = [], set()
    for rel in FILES:
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        n = 0
        for i in range(s + 1, len(h)):
            if not h[i].strip():
                continue
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = value_for(h[i]); used.add(" ".join(h[i].split())); n += 1
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, n))
        print("  %-32s %2d cells -> %s" % (os.path.basename(rel), n, os.path.basename(new)))
    n_N = sum(1 for _, v in VALUES if v.startswith("N "))
    print("\n  %d cells in %d TAPPs; %d distinct procedure columns; %d of them N"
          % (sum(p[3] for p in plan), len(plan), len(used), n_N))
    if len(used) != len(VALUES):
        raise SystemExit("PREMISE: %d value entries but %d distinct columns" % (len(VALUES), len(used)))
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
