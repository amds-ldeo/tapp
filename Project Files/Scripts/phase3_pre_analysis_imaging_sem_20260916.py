#!/usr/bin/env python3
"""Phase 3 for `Pre-Analysis Imaging and Screening` — batch 3: the SEM family (70 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_pre_analysis_imaging_sem_20260916.py" [--apply]

Same source rule and the same boundary as batches 1-2, and the boundary does most of the work here:
in an SEM paper the imaging usually IS the procedure, so an image is only this field's business when
the paper puts it before the procedure in order to find something.

FOUR PAPERS DO THAT, and they are the same four that stated a selection criterion — which is the
point: a screening step and the criterion it serves are one act described twice. Izawa 2010 runs μXRD
first as a "no-touch first-pass reconnaissance"; Gucsik 2013 runs an optical-CL survey; Pascucci 2026
acquires VIS-IR spectral images before the section is even coated; Barnes 2025 finds its two EDS
targets by NanoSIMS isotope imaging. Zega 2025's JSC laboratory adds a fifth, smaller case: optical
documentation before coating.

Everywhere else the cell is N, and says what the paper describes instead.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Pre-Analysis Imaging and Screening"
FILES = ["SEM/SEM_TAPP_v71.csv", "SEM/SEM_Composition_TAPP_v70.csv", "SEM/SEM_FIBSEM_TAPP_v37.csv",
         "SEM/SEM_Imaging_TAPP_v36.csv"]

IZAWA = ("Micro X-ray diffraction reconnaissance — the paper's first stage is \"an initial, non-destructive in situ "
         "reconnaissance step using micro X-ray diffraction (mXRD) to document meteorite mineralogy and textures and "
         "to identify features of interest\", valuable as \"a 'no-touch' first-pass reconnaissance, which may identify "
         "areas for further study\"; it then gives \"point-by-point correlation of crystal structure data with other "
         "microscopic and microanalytical data\" (p.2)")
GUCSIK = ("Optical microscope-cathodoluminescence survey — \"Following a systematic optical microscope"
          "cathodoluminescence study of a Kaba thin section, seven representative grains (designated as B-1 through "
          "B-7) were selected for further analyses\" (p.2); the grain labels tie the later measurements back to that "
          "survey (Fig. 1, p.2)")
PASC = ("VIS-IR imaging spectroscopy, acquired before the section was prepared — the fragment was embedded and "
        "polished \"after the SPectral IMager (SPIM) reflectance spectroscopy imagery acquisition\" and only then "
        "carbon coated \"for further SEM-EDS and EMPA-WDS analyses\" (p.3). The SEM work is then registered to those "
        "images: \"To cover approximately the same area of the SPIM images (9.7 mm large), 10 BSE images, with four "
        "consecutive images in the same row, were acquired and mosaicked\" (p.3)")
ZEGA_JSC = ("Optical microscopy before coating — \"After initial documentation by optical microscopy, the sample was "
            "sputter coated with ~5 nm of C to assist with charge dissipation during SEM analysis\" (p.9)")
ZEGA_NONE = ("N — the passage describes mounting and coating only (\"Polished sections were coated with a thin layer "
             "(0.1 nm) of carbon to mitigate charge build-up\", p.9); no prior imaging or screening is described")
SELF = ("N — the imaging this procedure performs is its own measurement, not a screening step before it; the paper "
        "describes no prior characterisation used to locate the units")
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"), SELF),
    (("Garvie et al. 2008", "TEM Sample Preparation"),
     "N — the SEM imaging and the FIB sectioning are one session on one instrument, \"Images were acquired with a Nova "
     "200 NanoLab DualBeam FIB/SEM\" (p.2); no separate prior screening step is described"),
    (("Genge et al. 2025", "BSE Imaging"), SELF),
    (("Genge et al. 2025", "EDS Point Analysis"), SELF),
    (("Genge et al. 2025", "EBSD"), SELF),
    (("Gucsik et al. 2013", "CL Mapping"), GUCSIK),
    (("Gucsik et al. 2013", "EDS Point Analysis"), GUCSIK),
    (("Izawa et al. 2010", "CL Mapping"), IZAWA),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"), IZAWA),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"), IZAWA),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"),
     IZAWA + "; this procedure is the third stage, run on features the earlier stages located"),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"),
     IZAWA + "; this procedure is the third stage, run on features the earlier stages located"),
    (("Liu et al. 2017", "3D Tomography"),
     "N — X-ray micro-CT is run on the same samples (\"The scanning area of the X-ray CT scan was 2 mm in diameter and "
     "1 mm in height ... pixel resolution was 1 µm\", p.3), but as a parallel measurement feeding the same pore-network "
     "model, not as a screening step that sites the FIB-SEM volume"),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"), SELF),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"), SELF),
    (("Ma et al. 2017", "BSE Imaging"), SELF),
    (("Ma et al. 2017", "EBSD"),
     "N — no prior screening is described; the EBSD patterns are acquired on the same instrument as the BSE imaging, "
     "\"an HKL EBSD system on the ZEISS 1550VP SEM\" (p.2)"),
    (("Pascucci et al. 2026", "BSE Imaging"), PASC),
    (("Pascucci et al. 2026", "EDS Point Analysis"), PASC),
    (("Pascucci et al. 2026", "EDS Mapping"), PASC),
    (("Pascucci et al. 2026", "| SE Imaging"), PASC),
    (("Zhou et al. 2017", "3D Tomography"),
     "N — the preparation is mechanical and chemical only (\"polished with dry emery paper and then ground by argon "
     "ion\", p.3); no imaging or screening precedes the tomography"),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"), ZEGA_JSC),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"), ZEGA_JSC),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"), ZEGA_NONE),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"), ZEGA_NONE),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"), ZEGA_NONE),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"),
     "SEM imaging and EDS mapping of the same particles, reported immediately before the FIB work in the Methods — SE "
     "and BSE images on the Hitachi S-4800 and EDS mapping of \"The compositional heterogeneity of the particles\" "
     "(p.9); the paper does not state explicitly that the sections were sited from those images"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"),
     "N — the passage states only that \"Bennu particles were placed on PELCO carbon conductive tabs\" (p.9); no prior "
     "imaging or screening is described for this laboratory"),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"),
     "N — the passage states only that \"FIB sections were prepared from particles dispersed on conductive carbon dots "
     "on Al SEM pin mounts\" (p.10); no prior imaging or screening is described for this laboratory"),
    (("Zega et al. 2025", "CL Mapping"),
     "N — the cathodoluminescence passage describes the instrument and beam conditions only (p.9)"),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"),
     "NanoSIMS isotope imaging — the two grains this procedure analyses were found by raster ion imaging of the Au "
     "foil mount, each image \"256 × 256 pixels, analysed at 1,800 μs per pixel for 32 frames\", with grains counted "
     "presolar if their composition \"differed from the reference ratios by >5σ\" and the anomaly persisted across "
     "frames; \"Two O-rich presolar grains were also analysed by SEM-EDS to further constrain the phase\" (p.11)"),
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
