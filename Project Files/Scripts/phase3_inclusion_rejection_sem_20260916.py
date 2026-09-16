#!/usr/bin/env python3
"""Phase 3 for `Analysis Inclusion and Rejection Criteria` — batch 3: the SEM family (44 cells).

    python3 "Project Files/Scripts/phase3_inclusion_rejection_sem_20260916.py" [--apply]

SEM carries 35 procedure columns and SEM_Composition a 9-column subset of them; SEM_FIBSEM and
SEM_Imaging do not carry this field at all, so this batch writes 44 cells, not 70.

THIS CORPUS IS ALMOST ENTIRELY N, and the reason is structural rather than a gap in the papers: an
imaging procedure has no aggregate. It reports an image, a texture, a phase identification — there
is no population of individual results for a rule to admit or exclude. Where a count does appear in
one of these papers it belongs to a NEIGHBOURING method, and the no-borrowing rule keeps it out:
Ma 2017's "n = 4, 8, 15, 65, 3" is its EPMA table, and Genge 2025's "n = 6" is its SIMS oxygen-isotope
population. Neither is an SEM outcome.

The two tomography procedures are the closest thing to an exception and still are not one: they
integrate every voxel of a segmented volume rather than admitting or excluding results.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Analysis Inclusion and Rejection Criteria"
FILES = ["SEM/SEM_TAPP_v73.csv", "SEM/SEM_Composition_TAPP_v72.csv"]

IMAGING = ("N — an imaging procedure reports no aggregate over individual results, and no acceptance or rejection "
           "rule is stated")
EDS = ("N — compositions are reported by phase with no contributing count and no acceptance or rejection rule stated")
MA_EPMA = ("N — no count or rule is stated for the SEM work. The contributing counts in this paper (\"n = 4\", "
           "\"n = 8\", \"n = 15\", \"n = 65\", \"n = 3\"; Table 1, p.2) belong to its EPMA analyses and are not "
           "borrowed")
GENGE_SIMS = ("N — no count or rule is stated for this procedure. The paper's \"(n = 6)\" (p.4) is its SIMS "
              "oxygen-isotope population, not an SEM outcome")
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"), IMAGING),
    (("Garvie et al. 2008", "TEM Sample Preparation"),
     "N — a sample-preparation procedure produces sections rather than results to aggregate, and no selection rule "
     "for them is stated"),
    (("Genge et al. 2025", "BSE Imaging"), GENGE_SIMS),
    (("Genge et al. 2025", "EDS Point Analysis"), GENGE_SIMS),
    (("Genge et al. 2025", "EBSD"), GENGE_SIMS),
    (("Gucsik et al. 2013", "CL Mapping"),
     "N — the seven grains are chosen before analysis (recorded under Sampling Unit Selection Criteria), not admitted "
     "to or excluded from an aggregate; no contributing count or rejection rule is stated"),
    (("Gucsik et al. 2013", "EDS Point Analysis"),
     "N — no contributing count and no acceptance or rejection rule is stated; the grain selection is recorded under "
     "Sampling Unit Selection Criteria"),
    (("Izawa et al. 2010", "CL Mapping"), IMAGING),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"), IMAGING),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"), IMAGING),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"), IMAGING),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"), EDS),
    (("Liu et al. 2017", "3D Tomography"),
     "N — the pore statistics integrate the whole segmented volume rather than admitting or excluding results; the "
     "only stated restriction is of scope, the model focusing \"only ... on the coal sample #1\" (p.8)"),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"), IMAGING),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"), IMAGING),
    (("Ma et al. 2017", "BSE Imaging"), MA_EPMA),
    (("Ma et al. 2017", "EBSD"), MA_EPMA),
    (("Pascucci et al. 2026", "BSE Imaging"), IMAGING),
    (("Pascucci et al. 2026", "EDS Point Analysis"), EDS),
    (("Pascucci et al. 2026", "EDS Mapping"), IMAGING),
    (("Pascucci et al. 2026", "| SE Imaging"), IMAGING),
    (("Zhou et al. 2017", "3D Tomography"),
     "N — no results are admitted or excluded; the volume's adequacy is assessed instead, under \"evaluation of "
     "representative volumes\" (§2.3, p.4), and the reported statistics integrate all ~800 slices"),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"), IMAGING),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"), EDS),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"), IMAGING),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"), IMAGING),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"), IMAGING),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"),
     "N — a sample-preparation procedure produces sections rather than results to aggregate (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"),
     "N — a sample-preparation procedure produces sections rather than results to aggregate (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"),
     "N — a sample-preparation procedure produces sections rather than results to aggregate (p.10)"),
    (("Zega et al. 2025", "CL Mapping"), IMAGING),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"),
     "N — this procedure analyses \"Two O-rich presolar grains\" individually to confirm their phase (p.11), with no "
     "aggregate over results. The >5σ anomaly criterion and the requirement that an anomaly persist \"in multiple "
     "consecutive frames\" (p.11) select grains from the NanoSIMS imaging, and belong to that procedure"),
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
