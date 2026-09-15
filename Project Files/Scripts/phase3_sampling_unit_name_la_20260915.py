#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Name` — batch 2: the laser-ablation family (28 cells, 5 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_name_la_20260915.py" [--apply]

Same source rule and cell grammar as batch 1 (phase3_sampling_unit_name_solution_20260915.py):
labelled units quoted with their sample and page; "Sample name only" where units are identified only by
the sample's name, or counted and never labelled; N where nothing is stated.

The U-Pb TAPPs carry the same literature columns as their base TAPPs, and receive byte-identical cells.

TWO LIMITS OF THE SOURCE, stated rather than papered over:
  * Where a table flattens in text extraction so that label-to-meteorite pairing is not recoverable
    (Chernonozhkin 2021 Table 2; Mittlefehldt 2024 Table S1's source column), the labels are quoted
    without asserting which meteorite each belongs to.
  * Where the unit list lives in a supplement or appendix that is not in the archived PDF (Liu 2016
    Table S1; B. Zhang 2022 Appendix 4), the cell says so.

NOTICED, NOT CHANGED. In most LA columns `Sample Name` reads N and `Sampling Unit Type` is blank:
the Rule 13 / Rule 9 fields were never assessed for this corpus. That is a separate backlog.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-15"
FIELD = "Sampling Unit Name"

WZHANG = ("Sample name only — runs in \"NWA 10597 and NWA 6950\" (p.3), counted by reduction group (\"Normal group "
          "n=36\", \"SUIA group n=244\", table p.7), not labelled; reference materials by name (NHB-9, YY12-01, "
          "YG4301, p.3)")
NAKANISHI = ("Labelled: metal grains by host chondrule within each section — e.g. \"N8_02 interior ch2-1\" with LA "
             "\"spot No.\" 201, 202; \"N8_05 margin ch1\"; isolated grain \"iso1\" (table p.6; p.4) — in the sections "
             "\"NWA801-3-8, NWA7184-29-9, and DHO1432-5-5\" (p.2)")
LIU2024 = ("Sample name only — reference-material fusion glasses by name (JB-1b, GSR-3, AGV-2, AC-E, GSR-1, W-2A; "
           "BHVO-2 glass, p.3); \"Nine spot analyses ... were arranged in a grid\" per glass (p.5), unlabelled")
LIU2025 = ("Sample name only — experimental run products by run number, e.g. \"D-2\", \"D-4\", \"D-34\", \"D-46\" "
           "(Table 1, p.3) and \"DAC-41\" (p.4); spots within a run are not labelled")
LIU2016 = ("Labelled sections: \"UT1 to UT3 (formerly referred to as MT-1, MT-2, MT-3)\" (p.3). LA-ICP-MS results are "
           "averages (\"n = 7\", \"n = 13\", table p.9); individual analyses are in \"Table S1 in supporting "
           "information\" (p.7), not in the archived PDF")
WU2023 = ("Sample name only — \"Xenotime samples included BS-1, MG-1, XN02, XENOA and M1567; apatite samples included "
          "Otter Lake, NW-1 and MAP-3; and garnet samples included 14SA36 and 12QL59\" (p.9); spots are counted "
          "per sample, not labelled")
BZHANG = ("Labelled by specimen within each meteorite: \"Cerro del Inca (museum number USNM 7062), Clark County (USNM "
          "1304-a), Fitzwater Pass (CML 0413-6), Klamath Falls (USNM 7008-a and AMNH 4926-psl), Moonbi (USNM "
          "1457-a), Nelson County (USNM 674-b), Oakley (iron) (USNM 780-d), and St. Genevieve County (USNM 454-a)\", "
          "plus a mount of Zinder and a thin section of NWA 1911 (p.4). Individual spots and lines \"are shown in "
          "Appendix 4\" (p.6), not in the archived PDF")
CHERN_OL = ("Sample name only — \"Springwater, ... Brenham, Brahin and Seymchan, and ... Imilac, Cumulus Peak 04071, "
            "Esquel and Fukang\" (p.2); maps and line scans are not given labels of their own in the paper")
CHERN_PH = ("Labelled: phosphate grains per pallasite, \"Ph1\", \"Ph2\", \"Ph3\", \"Ph4\" with mineral (\"stanf\", "
            "\"merr\"), and each \"single parallel measurement\" numbered (Table 2, p.10) — for Brahin, CMS 04071, "
            "Esquel and Seymchan")
MITTLE = ("Labelled: samples within each pallasite, e.g. \"Ac-1\", \"Ad-1\", \"Ah-1\", \"Ah-2\", \"Ah-3\", \"Al-1\", "
          "\"Br-1\" (Table S1, p.14); laser spots carry labels such as \"laser spot 059-Pa-1\" (p.8)")
NAVARRO = ("Sample name only — iron meteorites by name (Table 1, p.2), each analysed as \"fragments about 1 cm\" "
           "(p.3); spots and mapped areas are counted (\"points 176\", p.12), not labelled")

LAQ = {"Nakanishi": NAKANISHI, "Liu et al. 2024": LIU2024,
       "Liu et al. 2025 (GCA 393) Experimental silicate glass": LIU2025,
       "Liu et al. 2025 (GCA 393) Experimental sulfide": LIU2025,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Silicates": LIU2016,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Phosphate": LIU2016}
LASF = {"Zhang et al. 2022 (GCA 323)": BZHANG,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Raster": CHERN_OL,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Line": CHERN_OL,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite phosphate": CHERN_PH,
        "Mittlefehldt": MITTLE,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": NAVARRO,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": NAVARRO}

CELLS = {
 "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v81.csv": {"Zhang et al. 2022 (At. Spectrosc": WZHANG},
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v82.csv": dict(LAQ, **{"Wu+etal2023": WU2023}),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v82.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v79.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v80.csv": dict(LASF),
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
        missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
        if missing:
            raise SystemExit("%s: unmatched columns %s" % (rel, missing))
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
