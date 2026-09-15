#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Name` — batch 3: EPMA (15 cells, 1 TAPP).

    python3 "Project Files/Scripts/phase3_sampling_unit_name_epma_20260915.py" [--apply]

Same source rule and cell grammar as batches 1-2. One EPMA-specific convention: a reported row is
usually a point analysis inside a grain inside a section, and papers label different levels. Each
cell therefore states the FINEST level the paper labels (section, split, particle, grain) and says
when the finer units — the points — are unlabelled or listed only in a supplement. This is D4 of the
proposal applied: where the analysed points are not named, the containing area that is named stands
for them.

N here means the paper names no specimen for the microprobe work at all (McCoy 2025, both labs): the
curation numbers it does give identify figure images, not analyses, and are not borrowed.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-15"
FIELD = "Sampling Unit Name"
REL = "EPMA/EPMA_TAPP_v71.csv"

CELLS = {
 "Ma+2015":
  "Labelled at section level only: tissintite \"was identified in sections UT1, UT2 and UT3\" (p.2); Table 1 groups "
  "the point analyses by phase and setting (\"Wormy type tissintite\", \"Rimming tissintite\", \"Maskelynite away "
  "from melt pockets\" …) with counts (n = 6, 9, 17 …), not labels (p.5)",
 "Hu+2020":
  "Sample name only — \"a polished thick section of the martian meteorite NWA 8657\" (p.2), not otherwise labelled; "
  "analyses are grouped by phase (\"maskelynite, melt inclusion glasses, silica glasses, coesite aggregates, and "
  "mesostasis\", p.2)",
 "Liu+2016_UT":
  "Labelled at section level: X-ray maps are placed by thin section, e.g. an olivine megacryst \"in Tata-2-C3\" "
  "whose \"Red box outlines the area of X-ray maps\" (Fig. 3 caption, p.7); the sections are \"UT1 to UT3\" and "
  "\"Tata-1-C1 to C3, Tata-2-C1 to C3, and Tata-3-C1 to C3\" (pp.2–3). Map areas carry no labels of their own",
 "Liu+2016_Cal":
  "Labelled: thin sections \"UT1 to UT3\" and \"Tata-1-C1 to C3, Tata-2-C1 to C3, and Tata-3-C1 to C3\" (pp.2–3), "
  "and pyroxene grains within a section, e.g. \"T-3-C2 px1\" to \"T-3-C2 px5\" (Fig. 8, p.12); individual point "
  "analyses are not labelled",
 "Ma+2017":
  "Labelled at section level only: \"The Zagami thin section (USNM 7619)\" (p.3); occurrences are identified by "
  "figure panel (\"First occurrence of liebermannite\", Fig. 1, p.2), not by label",
 "Frank+2023":
  "Labelled at section level: the CAI \"in Ivuna section MZ2\" (p.3), in \"polished mount 'Ivuna MZ2'\" (p.14); the "
  "single CAI and its analysis points carry no labels",
 "Broussard+2026":
  "Labelled: \"OC002 LAB24-2 fragment 1\" and \"fragment 2\" (Figs 3–4, pp.6–7), and within fragment 1 \"lithic "
  "clast LC1\" (Figure S3 caption, p.17); map areas are otherwise unlabelled",
 "Seifert+2026":
  "Labelled: apatite grains numbered within each particle — \"OREX-803166-0 … Ap. #1 Ap. #2 Ap. #3 Ap. #4\" "
  "(Table 1, p.7) — in particles \"OREX-803166-0, OREX-803169-0, and OREX-803173-0\" (p.3) from the mounts "
  "\"OREX-803079-0 and OREX-803080-0\" (p.2)",
 "Pang+2016":
  "Sample name only — NWA 8003; grains are identified by setting (\"garnet grains within the eclogitic mineral "
  "assemblage\", p.4), and the point analyses are in \"Supplementary Table 4\" (p.4), not in the archived PDF",
 "McCoy+2025_SI":
  "N — the Smithsonian microprobe passage names no specimens (\"conducted on Ir-coated specimens\", p.7); the "
  "paper's OREX numbers identify figure images, not microprobe analyses",
 "McCoy+2025_UA":
  "N — the Arizona microprobe passage names no specimen (\"the section was coated with a thin film of carbon\", "
  "p.7); the paper's OREX numbers identify figure images, not microprobe analyses",
 "Zega+2025":
  "Labelled by curation number per particle: \"EMPA data from Bennu particles\" (Fig. 1) cites \"OREX-803095-0\" "
  "and \"OREX-803096-0\", and sulfide compositions \"in samples OREX-803095-0, OREX-803096-0, OREX-803066-0, "
  "OREX-803067-0 and OREX-803070-0\" (p.2); points within particles are not labelled",
 "Barnes+2025 | CRPG":
  "Labelled at split level: \"Samples OREX-800045-103 and OREX-800045-107 ... Aggregate particles (<1 mm) were "
  "mounted in epoxy\" (p.11); particles and points are not labelled, and the data are \"compiled in "
  "Supplementary Table 14\" (p.11), not in the archived PDF",
 "Barnes+2025 | NHM":
  "Labelled: \"The samples OREX-501054-0 and OREX-501059-0 ... fragmented into particles, identified as P1 and "
  "P2\" (p.13); the olivine and pyroxene grains within them are not labelled",
 "Neuman+2025":
  "Labelled at thin-section level: \"The 73001,6014–73001,6021 samples are 50 × 25 mm continuous thin sections\" "
  "(p.6), e.g. the \"73001,6019\" X-ray map (p.11); every map pixel is an analysis, so the section — the "
  "acquisition area — is the unit named",
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
    missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
    if missing:
        raise SystemExit("unmatched columns %s" % missing)
    for i, v in m.items():
        if row[i].strip():
            raise SystemExit("REFUSING: %s already holds %r" % (h[i][:40], row[i][:60]))
        row[i] = v
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), REL)
    print("  %s: %d cells -> %s" % (os.path.basename(REL), len(m), os.path.basename(new)))
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
