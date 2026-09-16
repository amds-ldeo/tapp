#!/usr/bin/env python3
"""Phase 3 for `Analysis Inclusion and Rejection Criteria` — batch 1: EPMA (14 cells).

    python3 "Project Files/Scripts/phase3_inclusion_rejection_epma_20260916.py" [--apply]

Run against the definition settled in Module_Aggregation v4 (amds-ldeo/tapp#4) and the key decision
recorded on 2026-09-16. Two rules follow from them and decide every cell here:

  * THE UNIT IS AN INDIVIDUAL RESULT — the value of the reported quantity from one acquisition. A
    per-phase mean of n point analyses is an aggregate, and those n points are its individual
    results, so a stated n is part of this field's outcome even when no rejection rule accompanies
    it. Those cells read "Partially — …", the grammar the Solution corpus already uses.
  * THE SPLIT WITH SIGNAL FILTERING IS BY BASIS, not by unit. A discard made on the signal (spikes,
    cycles, a compromised acquisition) belongs to `Spike / Outlier Filtering Approach` however large
    the thing discarded; only result-based selection belongs here.

Counts stated for a NEIGHBOURING method are not this procedure's outcome: Barnes 2025's "Bennu
(n = 58)" is its SIMS oxygen-isotope population and Frank 2023's "n = 9" is a SIMS standard, so
neither is borrowed into an EPMA cell.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Analysis Inclusion and Rejection Criteria"
REL = "EPMA/EPMA_TAPP_v76.csv"

CELLS = {
 "Ma+2015":
  "Partially — the contributing counts are stated per aggregate, each Table 1 column being the mean of n point "
  "analyses of one phase and textural setting (n = 6, 6, 6, 9, 17, 7 and 5; p.5), with one standard deviation of the "
  "mean. No acceptance or rejection rule, and no acquired-versus-included count, is stated",
 "Hu+2020":
  "N — analyses are reported by phase with no contributing count and no acceptance or rejection rule stated",
 "Liu+2016_UT":
  "N — the modal fractions use every pixel of the mapped section (\"the number of pixels attributed to each mineral "
  "was divided by the total number of pixels in the whole section\", p.3); nothing is admitted or excluded",
 "Liu+2016_Cal":
  "Partially — contributing counts are stated for the glass aggregates (\"EMP avg (n = 73)\" and \"avg (n = 14)\", "
  "Table 3, p.9) and for the mineral means (n = 7, n = 13, table p.9). No acceptance or rejection rule is stated; the "
  "plateau-region screening of each spot is a signal-based step recorded under Spike / Outlier Filtering Approach",
 "Ma+2017":
  "Partially — each Table 1 column is the mean of n point analyses of one occurrence (n = 6, 2, 3, 3, 5 and 4; p.3), "
  "with one standard deviation of the mean. No acceptance or rejection rule is stated",
 "Frank+2023":
  "N — the microprobe analyses are reported as \"Representative electron-microprobe measurements\" (p.5) with no "
  "contributing count and no selection rule. The counts on p.8 (n = 9, n = 7) are SIMS standard populations, not "
  "microprobe aggregates",
 "Broussard+2026":
  "Partially — the carbonate compositions are means of stated counts (\"Dolomite contains 2.0 ± 0.4 wt% Fe and "
  "3.0 ± 0.9 wt% Mn (n = 37)\"; \"Magnesite contains 14.5 ± 2.7 wt% Fe and 4.6 ± 2.5 wt % Mn (n = 23)\", p.5). No "
  "acceptance or rejection rule is stated",
 "Seifert+2026":
  "N — Table 1 reports one column per named apatite grain rather than an aggregate over results, and no acceptance or "
  "rejection rule is stated",
 "Pang+2016":
  "Partially — the reported averages state their contributing counts (\"based on 12 analyses\" for orthopyroxene, "
  "and \"14 analyses\" for augite, p.2; \"based on 13 analyses\" and \"34 ± 7 mol% on average; 19 analyses\" for "
  "the Ca-Eskola component, p.4). No acceptance or rejection rule is stated",
 "McCoy+2025_SI":
  "N — compositions are reported by phase with no contributing count and no selection rule stated",
 "McCoy+2025_UA":
  "N — compositions are reported by phase with no contributing count and no selection rule stated",
 "Zega+2025":
  "N — no contributing count and no acceptance or rejection rule is stated for the microprobe analyses; the modal "
  "abundances come from classified phase-map pixels rather than from admitting or excluding results (p.9)",
 "Barnes+2025 | CRPG":
  "N — the analyses are \"compiled in Supplementary Table 14\" (p.11), not in the archived PDF, and no count or "
  "selection rule is stated in the text. The \"Bennu (n = 58)\" population (Fig. 5, p.6) is the SIMS oxygen-isotope "
  "dataset, not this procedure's",
 "Barnes+2025 | NHM":
  "N — no contributing count and no acceptance or rejection rule is stated for the olivine and pyroxene analyses",
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
    print("  N: %d   Partially: %d" % (sum(1 for v in CELLS.values() if v.startswith("N ")),
                                       sum(1 for v in CELLS.values() if v.startswith("Partially"))))
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
