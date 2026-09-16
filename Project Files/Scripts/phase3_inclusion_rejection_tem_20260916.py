#!/usr/bin/env python3
"""Phase 3 for `Analysis Inclusion and Rejection Criteria` — batch 4: TEM (21 cells), completing the
field and the four-field in-situ backfill.

    python3 "Project Files/Scripts/phase3_inclusion_rejection_tem_20260916.py" [--apply]

TEM behaves like SEM here rather than like LA: the reported quantity is usually a described structure
or a per-grain composition, not a mean over a population, so there is nothing to admit or exclude.
One genuine exception, and one trap:

  * CYMES 2023 flags an analysis as an outlier and drops it from a plot — "(†not plotted, outlier)"
    in the caption of Table S1 (p.16). That is result-based exclusion, so it is recorded, with the
    limit that the table itself is supplementary and not in the archived PDF.
  * SINGERLING 2025's "(n = 7)" and "(n = 86)" are EPMA populations from OTHER Bennu samples, cited
    for comparison with the TEM data (p.2). Not this procedure's outcome, and not borrowed.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Analysis Inclusion and Rejection Criteria"
REL = "TEM/TEM_TAPP_v59.csv"

NO_AGG = ("N — the reported quantities are structures and per-grain compositions rather than aggregates over "
          "individual results, and no acceptance or rejection rule is stated")
ZEGA = ("N — no contributing count and no acceptance or rejection rule is stated for this laboratory's analyses")
CYMES = ("Partially — one analysis is excluded on result grounds: Table S1 reports the pyroxene lamella and rim "
         "compositions with \"(†not plotted, outlier)\" marking an analysis dropped from the plot (caption, p.16). "
         "The table is supplementary and not in the archived PDF, and no rejection rule or acquired-versus-included "
         "count is stated")

CELLS = {
 "Chaves2023": NO_AGG,
 "Zega2025|HF5000": ZEGA,
 "Zega2025|TitanX": ZEGA,
 "Zega2025|Talos": ZEGA,
 "Zega2025|2500SE": ZEGA,
 "Matsumoto2021|Tecnai": NO_AGG,
 "Matsumoto2021|JEM-3200FSK":
  "N — the iron sulfide compositions are quantified per analysis with the Cliff–Lorimer approximation (p.3); no "
  "contributing count and no acceptance or rejection rule is stated",
 "Matsumoto2021|ARM200F": NO_AGG,
 "KellerBerger2014": NO_AGG,
 "Zeng2024":
  "N — the Ti-oxide phases are identified individually from FFT and SAED patterns (p.2); there is no aggregate over "
  "results and no acceptance or rejection rule is stated",
 "Dobrica2022|Titan G2": NO_AGG,
 "Dobrica2022|TitanX":
  "N — the carbonate compositions are \"extracted from EDS mapping over areas of 5–10 nm\" and normalised to 100% "
  "(p.2); no contributing count and no acceptance or rejection rule is stated",
 "Singerling2025":
  "N — compositions are reported per named grain, with no aggregate over results and no rejection rule. The counts "
  "\"(n = 7)\" and \"(n = 86)\" (p.2) are EPMA populations from other Bennu samples, cited for comparison, and are "
  "not this procedure's outcome",
 "Thompson2020": NO_AGG,
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE":
  "N — Table 2 reports one column per apatite grain rather than an aggregate over results, and no acceptance or "
  "rejection rule is stated",
 "Seifert2026|HF5000":
  "N — Table 2 reports one column per apatite grain rather than an aggregate over results, and no acceptance or "
  "rejection rule is stated",
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos": NO_AGG,
 "Mo2022|HF5000":
  "N — the EELS results are reported as point and line analyses against standard references (p.5); no contributing "
  "count and no acceptance or rejection rule is stated",
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
    missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
    if missing:
        raise SystemExit("unmatched columns %s" % missing)
    for i, v in m.items():
        if row[i].strip():
            raise SystemExit("REFUSING: %s already holds %r" % (h[i][:40], row[i][:60]))
        row[i] = v
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), REL)
    print("  %s: %d cells -> %s (%d N, %d partially)"
          % (os.path.basename(REL), len(m), os.path.basename(new),
             sum(1 for v in CELLS.values() if v.startswith("N ")),
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
