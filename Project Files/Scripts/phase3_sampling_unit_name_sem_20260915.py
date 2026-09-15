#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Name` — batch 4: the SEM family (70 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_name_sem_20260915.py" [--apply]

SEM carries 35 procedure columns; SEM_Composition (9), SEM_FIBSEM (8) and SEM_Imaging (18) carry
subsets of them under identical headers, so one value per procedure fills all four TAPPs and shared
columns are byte-identical. Source rule and cell grammar as batches 1-3.

TWO RULES THAT DECIDE MANY CELLS HERE:
  * An identifier is never borrowed across methods in the same paper. Izawa 2010's numbered points
    ("point #1", "spot 34") are μXRD spots, so its SEM cells do not use them; Zega 2025's figure
    captions carry OREX numbers for FIB sections, but no laboratory's FIB passage names the sections
    it cut, so each FIB cell is N and says why.
  * Barnes 2025's BSE (Quanta 3D + Helios) and two FIB columns describe procedures the paper does not
    contain — each column's own `Additional Notes` already records this — so their cells are N.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-15"
FIELD = "Sampling Unit Name"
FILES = ["SEM/SEM_TAPP_v68.csv", "SEM/SEM_Composition_TAPP_v67.csv", "SEM/SEM_FIBSEM_TAPP_v34.csv",
         "SEM/SEM_Imaging_TAPP_v33.csv"]

GARVIE_SE = ("Sample name only — the Tagish Lake \"carbonaceous residue was attached to an Al-SEM stub\" (p.2); "
             "globules are identified by figure panel (\"A) Single sphere, B) three coalesced spheres, C) cluster of "
             "spheres …\", Fig. 1, p.2), not labelled")
GARVIE_FIB = ("Sample name only — the Tagish Lake carbonaceous residue on \"an Al-SEM stub\" (p.2); the globules "
              "sectioned by FIB are not given labels in the text")
GENGE = ("Sample name only — the single particle \"micrometeorite NG-1\", analysed as \"the NG-1 section\" (p.2); "
         "regions are identified by figure panel (\"Alloy-rich regions\", Fig. 2; \"Silicate-dominated areas\", "
         "Fig. 3; pp.3–4), not labelled")
GUCSIK = ("Labelled: \"seven representative grains (designated as B-1 through B-7)\" of \"a Kaba thin section\" (p.2), "
          "shown as the \"analyzed areas\" in Fig. 1 (p.2)")
IZAWA_CL = ("Sample name only — \"polished thin sections\" of Tagish Lake (p.2), not individually labelled; the numbered "
            "points of Table 1 and Fig. 1 (e.g. \"point #1\", \"spot 34\") are μXRD spots, not SEM-CL")
IZAWA_SEM = ("Sample name only — \"the Tagish Lake sections\" (p.3), not individually labelled; the numbered points of "
             "Table 1 and Fig. 1 (e.g. \"point #1\", \"spot 34\") are μXRD spots, not SEM analyses")
LIU_3D = ("Labelled: coal samples \"#1\" (Bofang Mine) and \"#2\" (Yuwu Mine) (Table 1, p.2); the 3D pore-network model "
          "\"only focuses on the coal sample #1\" (p.8)")
LIU_SE = ("Labelled: coal samples \"#1\" (Bofang Mine) and \"#2\" (Yuwu Mine) (Table 1, p.2); imaged areas are not "
          "labelled")
MA17 = ("Labelled: \"section 126A of USNM 7908\" (p.1), \"prepared from a larger Grain 126\" (p.2); the three mineral "
        "locations are \"marked by rectangles\" in Fig. 1 (p.2), not labelled")
PASC = ("Sample name only — \"the NWA 7317 slab\" (p.3), imaged on \"almost the same portion of the VIS-IR SPIM "
        "images\" (p.4); imaged fields and analysis points are not labelled")
ZHOU = ("Sample name only — \"subbituminous coal (SC) and high-volatile bituminous coal (HBC)\" (p.1), one FIB-SEM "
        "volume each; the numbered images (e.g. \"1st\", \"300th\" of sample SC, p.2) are slices, not units")
ZEGA_FIGS = "the paper labels FIB sections (e.g. OREX-803095-100, OREX-501005-100, OREX-803031-101; Figs 2–4) without attributing them to a laboratory"
ZEGA_JSC = ("N — the JSC SEM passage names no specimen (\"The particle was attached to an Al cylinder SEM mount\"; "
            "\"regions of interest\", p.9); the paper's OREX numbers identify figures, not this laboratory's analyses")
ZEGA_UA = ("N — the Arizona SEM passage names no specimen (\"Polished sections were coated with a thin layer ... of "
           "carbon\", p.9); the paper's OREX numbers identify figures, not this laboratory's analyses")
ZEGA_FIB_UA = "N — \"All sections were extracted from varied regions of matrix within the particles\" (p.9), none named; " + ZEGA_FIGS
ZEGA_FIB_UCB = "N — \"Bennu particles were placed on PELCO carbon conductive tabs\" (p.9), none named; " + ZEGA_FIGS
ZEGA_FIB_JSC = ("N — \"FIB sections were prepared from particles dispersed on conductive carbon dots on Al SEM pin mounts\" "
                "(p.10), none named; " + ZEGA_FIGS)
ZEGA_CL = "N — the cathodoluminescence passage names no specimen (p.9)"
BARNES_JSC = ("Labelled: \"Bennu sample OREX-501018-100\" (Extended Data Fig. 8 caption, p.27), \"aggregate QL material "
              "pressed onto a gold (Au) foil mount\" (p.10); the presolar-grain regions are not labelled")
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"), GARVIE_SE),
    (("Garvie et al. 2008", "TEM Sample Preparation"), GARVIE_FIB),
    (("Genge et al. 2025", "BSE Imaging"), GENGE),
    (("Genge et al. 2025", "EDS Point Analysis"), GENGE),
    (("Genge et al. 2025", "EBSD"), GENGE),
    (("Gucsik et al. 2013", "CL Mapping"), GUCSIK),
    (("Gucsik et al. 2013", "EDS Point Analysis"), GUCSIK),
    (("Izawa et al. 2010", "CL Mapping"), IZAWA_CL),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"), IZAWA_SEM),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"), IZAWA_SEM),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"), IZAWA_SEM),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"), IZAWA_SEM),
    (("Liu et al. 2017", "3D Tomography"), LIU_3D),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"), LIU_SE),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"), LIU_SE),
    (("Ma et al. 2017", "BSE Imaging"), MA17),
    (("Ma et al. 2017", "EBSD"), MA17),
    (("Pascucci et al. 2026", "BSE Imaging"), PASC),
    (("Pascucci et al. 2026", "EDS Point Analysis"), PASC),
    (("Pascucci et al. 2026", "EDS Mapping"), PASC),
    (("Pascucci et al. 2026", "| SE Imaging"), PASC),
    (("Zhou et al. 2017", "3D Tomography"), ZHOU),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"), ZEGA_JSC),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"), ZEGA_JSC),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"), ZEGA_UA),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"), ZEGA_UA),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"), ZEGA_UA),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"), ZEGA_FIB_UA),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"), ZEGA_FIB_UCB),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"), ZEGA_FIB_JSC),
    (("Zega et al. 2025", "CL Mapping"), ZEGA_CL),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"), BARNES_JSC),
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
    print("\n  %d cells in %d TAPPs; %d distinct procedure columns" % (sum(p[3] for p in plan), len(plan), len(used)))
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
