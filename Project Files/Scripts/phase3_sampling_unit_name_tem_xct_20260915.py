#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Name` — batch 5: TEM (21 cells) and Lab-XCT (14 cells).

    python3 "Project Files/Scripts/phase3_sampling_unit_name_tem_xct_20260915.py" [--apply]

Same source rule and cell grammar as batches 1-4. Conventions specific to this batch:
  * TEM. The unit is the electron-transparent specimen (FIB section, ultramicrotome section, crushed
    grains on a grid). Where the paper labels the grains or regions inside a section, the cell names
    both levels. Zega 2025's laboratory passages name no specimen; its figure captions carry FIB-section
    OREX numbers without attributing them to a laboratory, so — as in the SEM batch — each lab cell is N
    and says why. Xing 2023 is a review with no original analyses.
  * Lab-XCT. The unit is the scanned volume. Where a paper counts volumes (a stitched core's "six
    volumes") or particles without labelling them, the cell is "Sample name only". 2-D slices that a
    paper labels (Tomkinson 2015) are named as the finest labelled level of the one scanned chip.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-15"
FIELD = "Sampling Unit Name"

ZEGA_FIGS = ("the paper labels FIB sections (e.g. OREX-803095-100, OREX-803096-100, OREX-501005-100; Figs 2–3, p.3) "
             "without attributing them to a laboratory")
MATS = ("Labelled: FIB section \"11_5A_1\" prepared from Apollo 11 soil grain \"11_5A\" (p.3; \"No. Lunar11_5A\", "
        "Fig. 2 caption, p.5) — the one section, observed in all three TEMs (\"We observed the prepared section\", "
        "p.3); the Apollo 17 soil 78481,49 grains were examined by SEM only (p.3)")
DOBRICA_UH = ("Labelled: \"Four FIB sections\" from micrometeorite 03-36-46 (p.2) — \"region A (UH-001 ...)\", "
              "\"region B (UH-002 ...)\", \"Ca-phosphates (UH-003 ...)\" and \"magnetite (UH-006 ...)\" (p.3)")
DOBRICA_MF = ("Labelled: FIB sections from micrometeorite 03-36-46 — the carbonate compositions \"extracted from EDS "
              "mapping ... (at the Molecular Foundry)\" (p.2) are those of \"region A (UH-001 ...)\" and \"region B "
              "(UH-002 ...)\" (Fig. 5 caption, p.7)")
SEIFERT = ("Labelled: \"the FIB section (OREX-803173-100) with Ap. #1 and Ap. #2 labeled\" (Fig. 5 caption, p.9), "
           "cut from \"A cluster of two apatite grains\" (p.7); both instruments analysed \"The FIB section\" (p.3)")
CYMES = ("Labelled: one FIB section of Apollo 17 soil 71501 \"containing a pyroxene grain labeled “1pyx” "
         "and a surface-adhered pyroxene grain labeled “2pyx”\" (p.3)")

TEM = {
 "Chaves2023":
  "N — FIB sections were extracted from \"individual magnetite grains from the irradiated regions\" of the pellets "
  "(p.3) and are identified by irradiation condition (e.g. \"Altered rim on 4 keV He+ irradiated magnetite\", Fig. 9, "
  "p.9), not labelled",
 "Zega2025|HF5000":
  "N — the Arizona TEM passage names no specimen (\"Characterization of the FIB sections was performed using the "
  "200 keV Hitachi HF5000 STEM\", p.10); " + ZEGA_FIGS,
 "Zega2025|TitanX":
  "N — the Berkeley TEM passage names no specimen (\"TEM analysis was done on an FEI TitanX microscope\", p.10); "
  + ZEGA_FIGS,
 "Zega2025|Talos":
  "N — the Goethe passage names no specimen (\"TEM samples were prepared by crushing the grain\", p.10); "
  + ZEGA_FIGS,
 "Zega2025|2500SE":
  "N — the JSC TEM passage names no specimen (\"FIB sections were analysed using a JEOL 2500SE\", p.10); "
  + ZEGA_FIGS,
 "Matsumoto2021|Tecnai": MATS,
 "Matsumoto2021|JEM-3200FSK": MATS,
 "Matsumoto2021|ARM200F": MATS,
 "KellerBerger2014":
  "Labelled: \"particles RA-QD02-0125 and RA-QD02-0211\" (p.2); the \"thin sections (approximately 60-nm thick) ... "
  "prepared using ultramicrotomy\" from them (p.2) are not labelled",
 "Zeng2024":
  "Labelled: the Chang'e-5 glass bead \"CE5C0600YJFM00304\" (p.5), from which one \"FIB slice\" was prepared (p.6); "
  "regions within it are labelled \"Area 1\" and \"Area 2\" (Fig. 1, p.2)",
 "Dobrica2022|Titan G2": DOBRICA_UH,
 "Dobrica2022|TitanX": DOBRICA_MF,
 "Singerling2025":
  "Labelled: \"28 fine particles from the crushed sample OREX-800045–102, within which we identified four Na,Ca "
  "carbonates: grains 4, 11 ..., 22, and 27\" (p.2); the other fine particles are not labelled",
 "Thompson2020":
  "Sample name only — \"three individual chips of the CM2 Murchison meteorite\" (p.3); the \"four electron "
  "transparent ... sections\" are described by lasering dose and target (a matrix region, a sulfide grain, an "
  "olivine grain; p.4), not labelled",
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE": SEIFERT,
 "Seifert2026|HF5000": SEIFERT,
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos":
  "Labelled: \"Two grains were selected from CE-5 lunar soil (CE5C0400YJFM00505)\" (p.2), \"CE5C0400YJFM00505-G1\" "
  "and \"CE5C0400YJFM00505-G2\", with a \"FIB foil extracted from\" each (Figs 1, 3–4, pp.3–4)",
 "Mo2022|HF5000":
  "Labelled: \"The same FIB foil extracted from CE5C0400YJFM00505-G1 for the AES analysis was also analyzed using "
  "TEM-EELS\" (p.5)",
}

XCT = {
 "Eckley 2024":
  "Sample name only — the scan record's \"Sample name: OREX-800099-0\", \"Sample type: Asteroid Bennu particle\" "
  "(p.1); one whole-particle scan",
 "Genge et al. 2025":
  "Labelled: scans \"A0180-A and A0180-B\" of Ryugu sample A0180 (p.7)",
 "core 73002 Multi-volume":
  "Sample name only — core 73002, \"A series of six volumes was acquired\" and stitched \"to create a continuous data "
  "set for each core\" (Neuman et al. 2025, p.4); the volumes are counted, not labelled",
 "Neuman et al. 2025 (JGR Planets) Apollo 17 core 73001":
  "Sample name only — core 73001, \"A series of nine scan volumes was acquired along the length of the core\" "
  "(p.5); the volumes are counted, not labelled",
 "73001 CSVC":
  "Sample name only — the 73001 CSVC; scans are identified by position and stage (\"the bottom portion of 73001 "
  "still within the CSVC before (b) and after (c) piercing\", \"the top portion\", Fig. 7, p.27), not labelled",
 "Apollo 17 particles":
  "Sample name only — \"132 particles were scanned from 73002 ... and 220 particles from 73001\" (p.28), each "
  "\"individually bagged\"; the particles are counted and shown by lithology (Fig. 8, p.28), not labelled",
 "Tomkinson et al. 2015":
  "Labelled: 2-D slices of the one scanned volume — \"XCT slice 500\" to \"XCT slice 1000\" (Table 1, p.2) — "
  "of \"a single 2.7 g chip\" of NWA 5790 (p.3)",
 "Glavin et al. 2023":
  "Labelled: the split \"Murchison B (mass = 4.6430 g)\", scanned in its sealed vial; its counterpart \"Murchison A\" "
  "was the unscanned control (p.3)",
 "Nascimento-Dias":
  "Sample name only — \"fragments of about 4 mm of both meteorites\", NWA 8277 and NWA 6963 (p.5); not otherwise "
  "labelled",
 "Richard et al. 2019|Olivine":
  "Labelled: \"a single olivine phenocryst (1.0 mm large) separated from Sample A\" (p.2), hosting one silicate melt "
  "inclusion (Fig. 1, p.4)",
 "Richard et al. 2019|Whole sample":
  "Labelled: \"Sample B was scanned both entirely and on a 1.4 × 1.4 × 1.4 mm region of interest\" (p.2) — this "
  "column is the whole-sample scan; its inclusions are numbered (\"#3\", Fig. 2, p.5)",
 "Richard et al. 2019|ROI scan":
  "Labelled: the region-of-interest scan of Sample B, \"shown in Fig. 2 (fluid inclusion #3)\" (Table 1 note, p.3)",
 "Richard et al. 2019|(C-I)":
  "Labelled: \"Sample #\" C, D, E, F, G, H and I, each scanned on the Phoenix Nanotom S (Table 1, p.3)",
 "Tait 2014":
  "Sample name only — \"An 8 mm diameter core was drilled from the Watson 012 sample and then scanned\" (p.9); "
  "not otherwise labelled",
}

FILES = {"TEM/TEM_TAPP_v54.csv": TEM, "XCT/Lab-XCT_TAPP_v41.csv": XCT}


def col(header, key):
    parts = [p.strip().lower() for p in key.split("|")]
    hits = [i for i, h in enumerate(header) if all(p in " ".join(h.split()).lower() for p in parts)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    plan = []
    for rel, cells in FILES.items():
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        m = {col(h, k): v for k, v in cells.items()}
        if len(m) != len(cells):
            raise SystemExit("%s: two keys matched one column" % rel)
        missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
        if missing:
            raise SystemExit("%s: unmatched columns %s" % (rel, missing))
        for i, v in m.items():
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = v
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, len(m)))
        print("  %-28s %2d cells -> %s" % (os.path.basename(rel), len(m), os.path.basename(new)))
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
