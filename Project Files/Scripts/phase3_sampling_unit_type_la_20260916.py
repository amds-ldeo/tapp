#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Type` — batch 2: the laser-ablation family (26 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_type_la_20260916.py" [--apply]

Same source rule and cell grammar as batch 1 (EPMA). LA-MC is already filled and is not touched;
the U-Pb variants share their literature columns with their base TAPPs and receive identical cells.

THE LA-SPECIFIC QUESTION is what the laser's motion makes of the unit. A spot analysis reports a
spot inside something (a grain, a phase, a fused glass); a raster or map reports the area covered,
and the paper says what that area is (a whole polished surface, one olivine crystal, a region chosen
for its phases). Each cell names both levels, parent first.

The one cell already filled (Wu 2023, in LA-Q only) is left alone; the script refuses to overwrite a
non-blank cell.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Type"

NAKANISHI = ("Grain > Spot — HSE abundances are reported per metal grain, each with its LA \"spot No.\" "
             "(table p.6); the grains are typed by where they sit — interior grains in a chondrule, margin "
             "grains in its surficial shell, isolated grains in the matrix (p.1)")
LIU2024 = ("Aliquot (fused Li-borate glass disc) > Spot — \"Nine spot analyses ... were "
           "arranged in a grid pattern to cover the entire glass\" (p.5), and compositions are reported as "
           "the mean of those spots, \"fs-LA-ICP-MS (n = 9 spots)\" (Table 2, p.8)")
LIU2025_GL = ("Phase (quenched silicate glass of one experimental run) > Spot — \"A Resonetic 193 nm ArF "
              "excimer laser with a 40 μm beam diameter for glasses\" (p.4); Au and Cu contents are reported "
              "per run (Table 1, p.3)")
LIU2025_SU = ("Phase (quenched sulfide of one experimental run) > Spot — \"20 μm for sulfides, selecting grain "
              "sizes larger than 20 µm for the latter\" (p.4); Au and Cu contents are reported per run "
              "(Table 1, p.3)")
LIU2016 = ("Phase > Spot — \"The time-lapse plots of each spot were examined, and only the plateau region was "
           "used to quantify the trace element abundances\" (p.4); abundances are reported as per-phase means "
           "(\"n = 7\", \"n = 13\", table p.9), the individual spots being in a supplement not in the archived PDF")
BZHANG = ("Whole sample (polished specimen surface) > Region of interest (raster) — irons \"were analyzed using a "
          "raster scan over a few millimeters\" with a 50 μm beam, and compositions are reported as \"raster "
          "averages\" per specimen (Table 3, pp.4–5); Ge comes from a set of five 150 μm spots on five of "
          "the irons (p.4)")
CHERN_MAP = ("Grain (individual olivine crystal) > Region of interest (2D map) — \"2D trace element mapping of "
             "olivine crystals\" (p.1); the reported dataset is \"seven 2D element maps of PMG olivine crystals\", "
             "filtered and median-smoothed before analysis (p.6)")
CHERN_LINE = ("Grain (individual olivine crystal) > Region of interest (line scan) — \"a second line-scan was "
              "completed on top of the first one, using a laser spot of 130 μm diameter ... and a translation "
              "speed of 10 μm s−1\" (p.3)")
CHERN_PH = ("Grain (phosphate crystal) > Spot — compositions are reported per named phosphate grain (\"Ph1\" … "
            "\"Ph4\", with \"stanf\" or \"merr\"), each an average of numbered \"single parallel measurement\" "
            "spots (Table 2, p.10)")
MITTLE = ("Grain (olivine grain fragment) > Spot — \"The laser was run in spot mode with a 75 µm spot size\" (p.5); "
          "results are reported as average analyses per sample, and individual spots carry labels such as "
          "\"laser spot 059-Pa-1\" (p.8). Line scans across grain fragments were also run (p.3)")
NAVARRO_SP = ("Whole sample (polished ~1 cm fragment) > Spot — \"fragments about 1 cm were mounted in epoxy resin, "
              "polished, and cleaned with ultrapure water\" (p.3); the reported quantity is the meteorite's bulk "
              "composition for chemical classification (Table 1, p.2)")
NAVARRO_MAP = ("Region of interest > Phase — \"elemental mapping, conducted within regions featuring diverse phases "
               "of the Augusto Pestana meteorite\" (p.1); the map is read for the phases it resolves, \"even without "
               "prior knowledge regarding natural structural variations\" (p.1)")

LAQ = {"Nakanishi": NAKANISHI, "Liu et al. 2024": LIU2024,
       "Liu et al. 2025 (GCA 393) Experimental silicate glass": LIU2025_GL,
       "Liu et al. 2025 (GCA 393) Experimental sulfide": LIU2025_SU,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Silicates": LIU2016,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Phosphate": LIU2016}
LASF = {"Zhang et al. 2022 (GCA 323)": BZHANG,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Raster": CHERN_MAP,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Line": CHERN_LINE,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite phosphate": CHERN_PH,
        "Mittlefehldt": MITTLE,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": NAVARRO_SP,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": NAVARRO_MAP}

CELLS = {
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v83.csv": dict(LAQ),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v83.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v80.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v81.csv": dict(LASF),
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
