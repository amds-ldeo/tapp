#!/usr/bin/env python3
"""Phase 3 for `Pre-Analysis Imaging and Screening` — batch 1: EPMA (14 cells).

    python3 "Project Files/Scripts/phase3_pre_analysis_imaging_epma_20260916.py" [--apply]

Fourth field of the sampling-unit cluster, and the last of the four that are blank on all 131 in-situ
columns. The three Solution TAPPs do not carry it.

WHAT COUNTS. The field asks for characterisation done BEFORE the measurement in order to select or
locate the unit — technique, instrument, settings, and how analyses are linked back to the images.
So:
  * a stated prior step is recorded with its instrument ("the petrographic texture of NWA 8003 was
    observed using a JEOL 7000F ... FEG-SEM");
  * imaging the procedure performs as its own measurement is NOT this field. An EPMA BSE image taken
    on the microprobe is part of the procedure, not a screening step before it.
  * where a paper lists its methods as a suite without saying which came first, the cell records the
    imaging and says the order is not stated. That is honest about what the source supports.

N means the paper describes no prior characterisation at all.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Pre-Analysis Imaging and Screening"
REL = "EPMA/EPMA_TAPP_v74.csv"

MA_SUITE = ("SEM BSE imaging on a ZEISS 1550VP field-emission SEM, which locates the occurrences the probe then "
            "analyses — \"SEM BSE image showing tissintite in a shock melt pocket, in Tissint section UT2\" "
            "(Fig. 1 caption, p.2). The paper lists EPMA, SEM, EBSD, synchrotron XRD and micro-Raman as one suite "
            "(p.2) without stating the order")
MCCOY = ("Optical microscopy, then FE-SEM/EDS characterisation — particles \"were characterized using a JEOL 7600 F "
         "FE-SEM equipped with a 170-mm2 SSD type Oxford Instruments Ultim Max EDS detector\", and \"Following "
         "initial documentation by optical microscopy, samples were sputter coated\" (p.7); the SEM work is "
         "reported for the JSC facility, the microprobe work for this laboratory")

CELLS = {
 "Ma+2015": MA_SUITE,
 "Hu+2020":
  "SEM imaging and EDS mapping on three instruments before the probe — \"Scanning electron microscopy (SEM) imaging "
  "and energy dispersive X-ray spectroscopy (EDS) mapping were conducted\" on a Nova NanoSEM 450 at IGGCAS, a "
  "SUPRA55 at NAOC and a JEOL JSM-7100F at NIPR, after which \"Quantitative analyses ... were conducted by electron "
  "probe microanalysis (EPMA) with the JEOL JXA-8100 at IGGCAS\" (p.2)",
 "Liu+2016_UT":
  "Petrographic microscopy and SEM — \"The petrography of these sections was examined using a petrographic "
  "microscope and a scanning electron microscope\" before the microprobe work (p.3)",
 "Liu+2016_Cal":
  "Petrographic microscopy and SEM — \"The petrography of these sections was examined using a petrographic "
  "microscope and a scanning electron microscope\" (p.3); the same sections then went to both microprobes",
 "Ma+2017":
  "SEM BSE imaging on a ZEISS 1550VP field-emission SEM — \"Backscattered electron (BSE) imaging was performed using "
  "a Carl Zeiss, LLC 1550VP field emission SEM\" (p.2), locating the three occurrences of the new mineral in the "
  "Zagami thin section (Fig. 1, p.2). The paper lists EPMA, SEM, EBSD, synchrotron XRD and micro-Raman as one suite "
  "(p.2) without stating the order",
 "Frank+2023":
  "Petrographic microscopy and SEM — \"The CAI was characterized by petrographic microscope, scanning electron "
  "microscope, electron microprobe, and X-ray mapping before being measured for oxygen isotopes\" (p.3); the object "
  "itself had been found during an earlier survey of matrix compositions (p.3)",
 "Broussard+2026":
  "Optical microscopy of the same thin section — \"Eleven OC002 LAB24-2 fragments were mounted and dry-polished in a "
  "petrographic thin section used for optical microscopy and electron probe microanalyses\" (p.3)",
 "Seifert+2026":
  "SEM EDS mapping, then CL imaging, on the JEOL 7900F at JSC — \"Apatite grains in OREX-803079-0 and OREX-803080-0 "
  "were identified via EDS mapping and point analysis\", after which \"CL images were obtained for each apatite grain "
  "to search for zoning or internal structures not resolvable in EDS maps\", collected \"at 5 kV with beam currents "
  "ranging from 1 to 1.5 nA\" (p.2); the numbered grains (Ap. #1 …) tie the probe analyses back to those images",
 "Pang+2016":
  "SEM petrography — \"The petrographic texture of NWA 8003 was observed using a JEOL 7000F field emission gun "
  "scanning electron microscope (FEG-SEM) at Hokkaido University\" (p.7); phase identifications also rest on Raman "
  "spectra and EBSD patterns (p.4)",
 "McCoy+2025_SI": MCCOY,
 "McCoy+2025_UA": MCCOY,
 "Zega+2025":
  "SEM imaging and EDS mapping before the probe — particles were characterized by SE and BSE imaging and by EDS "
  "mapping of \"The compositional heterogeneity of the particles\" (p.9), and the paper's Fig. 1 pairs those BSE "
  "images with the EMPA data (p.2); the Methods list SEM before electron microprobe analysis without stating an "
  "explicit order",
 "Barnes+2025 | CRPG":
  "SEM imaging and multi-element EDS mapping — \"SEM observations were performed on the samples using a JEOL "
  "JSM-6510 with 3-nA primary beam at 15 kV. We also performed multi-element EDS mapping (Mg, Si, Fe, Ni, S, Na, Ca "
  "and Al) of the different grains\", after which \"Quantitative chemical analyses were performed using a JEOL "
  "JXA-8230 electron microprobe\" (p.11)",
 "Barnes+2025 | NHM":
  "SEM characterisation at the NHM — \"Olivine and pyroxene grains were identified and characterized at the NHM\" "
  "and \"Following characterization by SEM/EPMA, an additional carbon coat was added for a total thickness of ~30 "
  "nm\" (p.13); additional quantitative data came from a Zeiss EVO 15LS analytical SEM with an Oxford X-Max80 EDS "
  "(p.13)",
}


def col(header, key):
    parts = [p.strip().lower() for p in key.split("|")]
    hits = [i for i, h in enumerate(header) if all(p in " ".join(h.split()).lower() for p in parts)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    rows = list(csv.reader(io.open(os.path.join(ROOT, REL), newline="", encoding="utf-8-sig")))
    h = rows[0]; s = h.index("Literature Assessment")
    lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
    row = next(r for r in rows if r and r[0].strip() == FIELD)
    m = {col(h, k): v for k, v in CELLS.items()}
    if len(m) != len(CELLS):
        raise SystemExit("two keys matched one column")
    unhandled = [" ".join(h[i].split())[:60] for i in lit if i not in m and not row[i].strip()]
    if unhandled:
        raise SystemExit("blank columns with no value: %s" % unhandled)
    for i, v in m.items():
        if row[i].strip():
            raise SystemExit("REFUSING: %s already holds %r" % (h[i][:40], row[i][:60]))
        row[i] = v
    kept = [" ".join(h[i].split())[:40] for i in lit if i not in m]
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), REL)
    print("  %s: %d cells -> %s" % (os.path.basename(REL), len(m), os.path.basename(new)))
    print("  already filled, left alone: %s" % (kept or "none"))
    print("  N cells: %d" % sum(1 for v in CELLS.values() if v.startswith("N")))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0
    with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT, check=True, capture_output=True, text=True)
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    old = os.path.join(ROOT, REL)
    for f in (old, old[:-4] + ".xlsx"):
        if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    next(e for e in reg["composed"] if e["tapp"] == REL)["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
