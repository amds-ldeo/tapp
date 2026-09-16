#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Type` — batch 1: EPMA (14 cells).

    python3 "Project Files/Scripts/phase3_sampling_unit_type_epma_20260916.py" [--apply]

`Sampling Unit Type` was assessed for Solution and Lab-XCT only; the other four corpora (EPMA, LA,
SEM, TEM) were never done — 131 blank cells. This is batch 1 of that pass.

Source rule as for `Sampling Unit Name`: values stated in the PDF, with the page. Cell grammar
follows the two corpora already filled — a term from Column F first, nested with ">" where the
paper reports at two levels, then a parenthetical or dashed gloss quoting the evidence.

WHAT THE TYPE IS, FOR EPMA. The question is what one reported row corresponds to, not what the beam
touched. Three shapes recur:
  * per-phase or per-occurrence MEANS (Ma 2015, Ma 2017, Pang 2016) — the row is the phase or grain,
    the points are its replicates, and the cell says so with the n values;
  * REPRESENTATIVE or per-grain analyses (Frank 2023, Seifert 2026, Barnes 2025) — the row is the
    analysis point inside a named grain;
  * MAPS (Liu 2016 UT, Broussard 2026, Zega 2025 phase mapping) — every pixel is classified and the
    reported quantity is a modal fraction over a section or fragment, so the row is that area.

The one filled cell (Neuman 2025) is left alone; the script refuses to overwrite a non-blank cell.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Type"
REL = "EPMA/EPMA_TAPP_v72.csv"

CELLS = {
 "Ma+2015":
  "Phase > Analysis point — Table 1 reports one column per phase and textural setting (\"Wormy type "
  "tissintite\", \"Maskelynite away from melt pockets\" …), each the mean of n = 5–17 focused-beam "
  "point analyses (p.5)",
 "Hu+2020":
  "Phase > Analysis point — \"Quantitative analyses of maskelynite, melt inclusion glasses, silica "
  "glasses, coesite aggregates, and mesostasis were conducted by electron probe microanalysis\" (p.2); "
  "points are grouped by phase, not reported individually in the archived PDF",
 "Liu+2016_UT":
  "Whole sample (thin section) > Phase — \"elemental X-ray maps (Ca Ka, Al Ka, Fe Ka, and Mg Ka) of four "
  "sections\" (p.3); the reported quantity is a modal fraction, \"the number of pixels attributed to each "
  "mineral ... divided by the total number of pixels in the whole section\" (p.3)",
 "Liu+2016_Cal":
  "Phase > Analysis point — \"Major and minor element compositions of selected minerals\" by phase "
  "(Table 2, p.6); glass compositions are means, \"EMP avg (n = 73)\" and \"avg (n = 14)\" (Table 3, p.9)",
 "Ma+2017":
  "Grain > Analysis point — Table 1 reports one column per occurrence (\"Type liebermannite\", \"The second "
  "liebermannite\", \"The third liebermannite\", \"Lingunite next to type liebermannite\" …), each the mean "
  "of n = 2–6 points (p.3)",
 "Frank+2023":
  "Phase > Analysis point — \"Representative electron-microprobe measurements of melilite, grossmanite, and "
  "spinel are given in Table 1\" (p.5), all within the single Ivuna CAI",
 "Broussard+2026":
  "Region of interest > Phase — \"wavelength-dispersive quantitative compositional mapping and analysis\" "
  "(p.3) of whole fragments; phases are identified within a map (\"Round Phy1 phyllosilicate clast\", "
  "\"Lithic clast (LC1)\", Fig. 3, p.6) and abundances given per section (\"sulfides which make up 2.3 "
  "areal% of the section\", p.6)",
 "Seifert+2026":
  "Grain > Analysis point — Table 1 reports one column per apatite grain (\"Ap. #1\" … \"Ap. #5\") within "
  "each of the three particles (p.7)",
 "Pang+2016":
  "Phase > Analysis point — compositions are reported as per-phase means, \"The average compositions "
  "(Supplementary Table 1) of orthopyroxene\" (p.2) and \"41 ± 8 mol% on average; based on 13 analyses\" "
  "(p.4); the individual points are in a supplement not in the archived PDF",
 "McCoy+2025_SI":
  "Phase > Analysis point — \"Electron microprobe analysis was conducted on Ir-coated specimens\" (p.7); "
  "results are reported by phase, e.g. \"the calcite has near-end member composition (4 mol.% or less MgCO3 "
  "and FeCO3)\" (p.2)",
 "McCoy+2025_UA":
  "Phase > Analysis point — \"EMPA analyses were carried out using a Cameca SX-100 electron microprobe "
  "located at K-ALFAA\" (p.7); results are reported by phase, not per named point",
 "Zega+2025":
  "Grain > Phase — sulfide compositions are reported per grain within named particles (\"Pyrrhotite "
  "compositions measured by EMPA\", p.2), and \"phase mapping via electron microprobe analysis (EMPA)\" "
  "gives modal abundances of carbonates, sulfides and magnetite per particle (p.2)",
 "Barnes+2025 | CRPG":
  "Grain > Analysis point — \"Aggregate particles (<1 mm) were mounted in epoxy\" and mapped \"of the "
  "different grains\"; \"Quantitative analyses were performed with ... beam diameter of 1 µm\", the beam "
  "rastered \"over 5 × 5 µm2\" for carbonates (p.11)",
 "Barnes+2025 | NHM":
  "Grain > Analysis point — \"Olivine and pyroxene grains were identified and characterized at the NHM\" in "
  "particles P1 and P2, and \"Analyses were performed at 20 kV, using a focused 1-μm beam\" (p.13)",
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
