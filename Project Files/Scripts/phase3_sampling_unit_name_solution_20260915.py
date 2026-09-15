#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Name` — batch 1: the Solution ICP-MS family (29 cells, 3 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_name_solution_20260915.py" [--apply]

`Sampling Unit Name` was added 2026-09-15 (amds-ldeo/tapp#8, split_sampling_unit_20260915.py) with
every literature cell blank, because no paper had ever been asked how it names its units. This fills
the Solution MC (14), Solution Q (9) and Solution SF (6) columns.

SOURCE RULE. Every value was read from the source PDF in the session that wrote this script, in
reading-order text (PyMuPDF), and carries its PDF page. Column F of the field defines what is sought:
the name or label of each unit analysed, with the sample it belongs to.

THE CELL GRAMMAR, applied the same way throughout:
  * Labelled units: the labels, with their sample, quoted and paged.
  * "Sample name only": the paper identifies its units, but only by the sample's own name — one unit
    per sample, or replicates that are counted and never labelled.
  * N: no sample or unit identifier is stated (reason given where it helps).

NOT DONE. No value is taken from a neighbouring cell (`Sample Name`, `Sampling Unit Type`): those are
our earlier readings, not evidence. Computed rows are not units — Budde 2016's "C3b" and "C2–C4c" are
weighted means of measured fractions and are excluded.

NOTICED, NOT CHANGED. Nie & Dauphas 2019's `Sample Name` cell omits the six Apollo samples its
Table 1 reports; Barnes 2025 WUSTL's `Sample Name` cell names the LLNL and ETH Ti splits, not the WUSTL
digest. Both are neighbouring fields, left for a separate pass.
"""

import csv, io, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-15"
FIELD = "Sampling Unit Name"

CELLS = {
"Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v82.csv": {
 "Budde+etal2016":
  "Labelled within Allende: bulk \"MS-A\", \"MS-B\"; matrix \"M1\", \"M2\", \"M3\"; chondrules \"C1\", \"C2\", "
  "\"C3m\", \"C3n\", \"C3i\", \"C4\" (Table 1, p.3). \"C3b\" and \"C2–C4c\" in the same table are weighted means, "
  "not units. BHVO-2 by name only",
 "Craddock+etal2008":
  "Sample name only — Table 3 lists \"IAEA-S-1\", \"IAEA-S-2\", \"IAEA-S-4\", \"NBS-123\" and the in-house "
  "standards Alfa and Spex (p.4); replicates are counted (\"# of replicates\"), not labelled",
 "Hopp+etal2021":
  "Sample name only — meteorites by name, e.g. \"Toluca, Gibeon, Duchesne, Skookum, Tlacotepec\" (p.5); the "
  "digestion aliquots and ~50 mg pieces carry no labels of their own",
 "Hu+etal2022":
  "Labelled: each CAI by name under its specimen number — Table 1's \"Sample\" and \"CAI name\" columns give "
  "e.g. ME-3364-25.2 \"FG-FT-3\", ME-2639-16.2 \"FG-FT-4\", AL3S5 \"FG-FT-8\", AL4S6 \"FG-FT-9\", AL8S2 "
  "\"FG-FT-10\" (p.3); † marks a second analysis of FG-FT-4, -8 and -9. BCR-2 by name only",
 "IbanezMejia+Tissot2020":
  "Labelled: single crystals of FC-1 — zircons \"z1\"–\"z16\" with \"3_z…\" and \"4_z…\" series (e.g. "
  "\"4_z15R\", \"4_z17\"), baddeleyites \"b1\"–\"b8\" with \"3_b…\" and \"4_b…\" series, and bulk rock \"WR1\" "
  "(Table 1, pp.4–6); \"CA\"/\"Untr.\" beside each label marks chemical abrasion, not identity",
 "Nie+Dauphas2019":
  "Labelled for the lunar rocks by Apollo sample and split number: \"12002.613\", \"12018.301\", \"12052.353\", "
  "\"10017.413\", \"74275.361\", \"77215.276\" (Table 1, p.2), the last a \"white-colored fragment\"; terrestrial "
  "rocks by name only (BCR-2, BHVO-2 …)",
 "Nowell+etal2008 | Neptune":
  "Labelled for LOsST only: \"LOsST 17-03-06 (Aliq 1)\" (Table 8b, p.22) — the Neptune and Nu Plasma runs "
  "\"were made on two different aliquots of the LOsST RM\" (p.24); UMd, DTM and DROsS by name and session date",
 "Nowell+etal2008 | Nu Plasma":
  "Labelled for LOsST only: \"23-05-06NIGL (Aliq 2)\" (Table 8b, p.22), the second of the \"two different "
  "aliquots of the LOsST RM\" (p.24); DTM by name only",
 "Pringle+Moynier2017":
  "Labelled for the one duplicated sample: \"Allende I\" and \"Allende II\" (Table 1, p.4), \"duplicate splits "
  "from the same powder aliquot\" (p.3); every other sample by name only",
 "Schönbächler+etal2025":
  "Labelled by digestion where a sample was digested more than one way: \"Ivuna PB\" and \"Ivuna high PT\", "
  "\"30 mg Tagish Lake (labeled high PT)\" and \"90 mg Tarda (high PT)\" (p.4); Ryugu A0106, A0106-A0107 "
  "and C0108 and the other samples by name only",
 "vanKooten+etal2026":
  "Labelled where a meteorite was analysed twice: \"NWA 16569 (1)\", \"NWA 16569 (2)\", \"NWA 16554 (1)\", "
  "\"NWA 16554 (2)\" (Table 1, p.2); the other chondrites by name only",
 "Broussard+etal2026":
  "Labelled: two solutions of the OC002 fragment — \"Approximately 7 mg of sample from the LAB24-2 OC002A and "
  "OC002B solutions ... were used for potassium stable isotope analysis\" (p.3)",
 "Barnes+etal2025 | WUSTL":
  "Labelled: split \"OREX-803015-0\" — \"An ~20.66 mg split of Bennu aggregate (OREX-803015-0) was dissolved at "
  "WUSTL\" (p.7); the half of the solution kept at WUSTL is given no identifier of its own. The paper states "
  "its scheme: splits take \"suffixes of -100, -101, -102\" on the parent's number (p.7)",
 "Barnes+etal2025 | ETH":
  "Labelled: aliquot \"OREX-803015-100\" — \"a 5.2 mg aliquot of Bennu aggregate (OREX-803015-100)\" (p.7)",
},
"Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v85.csv": {
 "Hu+Gao2008":
  "Sample name only — Table 2 reports \"AGV-1\", \"BHVO-1\", \"G-2\", \"SCO-1\", \"GSR-5\" with replicate counts "
  "(n = 6, 5, 7, 4, 4) and no replicate labels (p.4)",
 "Yu+etal2005":
  "N — only the sample type is named (core-top Cibicidoides wuellerstorfi); no sample or aliquot identifiers "
  "are stated",
 "Makishima+etal2011":
  "Labelled for the meteorites: \"Orgueil #1\", \"Orgueil #2\", \"Murchison #1\", \"Murchison #2\", \"Allende #1\", "
  "\"Allende #2\" (table, p.9) — \"Two powder aliquots were used for each meteorite\" (p.9); geostandards by "
  "name only",
 "Long+etal2025":
  "Sample name only — meteorites by name (e.g. PCA 02010, PCA 02012); PCA 02010's \"Two separate fragments\" "
  "are distinguished by their values, not by labels (p.2)",
 "Lu+etal2007":
  "Sample name only, except the Allende powder: \"the Smithsonian reference Allende powder (USNM 3529, Split 1, "
  "Pos. 23)\" (p.5). Solutions \"#1\"–\"#8\" (p.7) are synthetic yield-test solutions, not samples",
 "GilDiaz+etal2020 | 8800":
  "N — the sorption-isotherm solutions carry no sample or unit identifiers",
 "GilDiaz+etal2020 | iCAP":
  "Labelled by extraction: fractions \"F1\", \"F2\", \"F3\", \"F4\" and \"F4N\" of the equilibrated sediment, "
  "\"two replicates per extraction mode\" (p.2); replicates not labelled",
 "GilDiaz+etal2020 | XSeries":
  "N — the sorption-kinetics and isotherm solutions carry no sample or unit identifiers",
 "LopezGarcia+etal2026":
  "Sample name only — each Ryugu particle was \"individually weighed\" and digested whole, so it is its own "
  "unit: \"A0066, A0238, A0247, A0256, A0259, A0268, A0301, and A0313\" (p.3)",
},
"Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v81.csv": {
 "Desem+etal2022":
  "Labelled by digestion: \"rock TD, soil TD, soil AR splits\" of each borehole sample (p.3), e.g. sample "
  "\"BH3a\" (p.2); splits are not numbered",
 "Li+etal2016":
  "Sample name only — \"mag_1\", \"mag_3\", \"mag_5\", \"py_2\", \"py_4\", each reported as \"Mean ± s (n = 3)\" "
  "with the replicates unlabelled (table, p.8)",
 "Lu+etal2007":
  "Sample name only, except the Allende powder: \"the Smithsonian reference Allende powder (USNM 3529, Split 1, "
  "Pos. 23)\" (p.5). Solutions \"#1\"–\"#8\" (p.7) are synthetic yield-test solutions, not samples",
 "Milne+etal2010":
  "Sample name only — seawater samples by name (SAFe S1, SAFe D2, NASS-5; GEOTRACES \"(GS)\" and \"(GD)\", p.4); "
  "the 12 mL sub-samples are not labelled",
 "Misra+etal2014":
  "Sample name only — consistency standards \"CAM-Uvig-1\", \"CAM-Uvig-2\", \"CAM-wuellerstorfi\", \"CAM-Mix\" "
  "(p.6); in the cleaning test each core-top sample was \"split into three fractions\" identified only by "
  "cleaning sequence (p.4)",
 "Willbold2005":
  "Labelled for BHVO-1: digestions \"BHVO-1 (1)\" to \"BHVO-1 (5)\", each with determinations \"1 2 3\" (Table 4, "
  "pp.8–9); the other reference materials by name with their issuing split and position (e.g. AGV-1 Split 35 "
  "Pos 13; Table 2, p.6)",
},
}


def col(header, key):
    parts = [p.strip().lower() for p in key.split("|")]
    hits = [i for i, h in enumerate(header) if all(p in " ".join(h.split()).lower() for p in parts)]
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
        missing = [" ".join(h[i].split())[:50] for i in lit if i not in m]
        if missing:
            raise SystemExit("%s: unmatched columns %s" % (rel, missing))
        for i, v in m.items():
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = v
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, len(m)))
        print("  %-52s %2d cells -> %s" % (os.path.basename(rel), len(m), os.path.basename(new)))
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
