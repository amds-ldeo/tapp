#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Selection Criteria` — batch 1: EPMA (14 cells).

    python3 "Project Files/Scripts/phase3_sampling_unit_selection_epma_20260916.py" [--apply]

Third and last of the three sibling fields. The field is in-situ only — the three Solution TAPPs do
not carry it — so this pass covers the same 131 columns as the `Sampling Unit Type` pass.

THE LINE THIS PASS HOLDS, because without it the field would simply restate its neighbour. The field
asks how the analysed unit is PICKED OUT within the sample. So:
  * a stated rule or reason is recorded and quoted — a size cut-off, a textural position, an
    identification step, an exclusion;
  * an act of picking by phase is a rule ("Olivine and pyroxene grains were identified and
    characterized", "Apatite grains ... were identified via EDS mapping");
  * a bare list of the phases a table reports is NOT. That is the evidence for `Sampling Unit Type`,
    and copying it here would make two fields say one thing. Those cells are N, and each says that
    the paper names the phases but states no rule for choosing the individual units.

N is therefore common and is the honest answer: most EPMA papers report what they measured without
saying how those grains, points or map areas were chosen.

The one cell already filled (Neuman 2025) is left alone; the script refuses to overwrite a non-blank
cell.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Selection Criteria"
REL = "EPMA/EPMA_TAPP_v73.csv"

NO_RULE = ("N — the paper names the phases it analysed (see `Sampling Unit Type`) but states no rule for "
           "choosing the individual units")

CELLS = {
 "Ma+2015":
  "Textural position relative to the shock-melt pockets — the analyses are grouped as \"Wormy type "
  "tissintite\", \"Rimming tissintite\", \"Maskelynite associated with wormy tissintite\" and \"Maskelynite "
  "away from melt pockets\" (Table 1, p.5), the phase itself occurring \"only in maskelynite less than "
  "~25 μm of a shock melt pocket\" (p.1)",
 "Hu+2020": NO_RULE,
 "Liu+2016_UT":
  "N — the map areas are shown rather than specified: a \"Red box outlines the area of X-ray maps\" on an "
  "olivine megacryst (Fig. 3 caption, p.7), with no stated rule for placing them",
 "Liu+2016_Cal": NO_RULE,
 "Ma+2017":
  "Occurrence of the target phase — the units analysed are the observed occurrences of the new mineral: "
  "\"A first occurrence of liebermannite was observed with lingunite, silica, ilmenite, and baddeleyite ... "
  "(this is the type material). A second occurrence ... A third occurrence is shown in Fig. 1c, close to "
  "the type occurrence\" (p.4)",
 "Frank+2023":
  "Opportunistic — the object analysed \"was found by David Frank in Ivuna section MZ2 during a study of "
  "the minor-element compositions of matrix olivine and pyroxene in types 1, 2, and 3 chondrites\" (p.3); "
  "no rule was applied to choose it, and it is the section's only CAI",
 "Broussard+2026": NO_RULE,
 "Seifert+2026":
  "Identification by EDS, then by CL — \"Apatite grains in OREX-803079-0 and OREX-803080-0 were identified "
  "via EDS mapping and point analysis\", after which \"CL images were obtained for each apatite grain to "
  "search for zoning or internal structures not resolvable in EDS maps\" (p.2)",
 "Pang+2016":
  "Spatial position within the shock assemblage — garnet is analysed \"within the eclogitic mineral "
  "assemblage of zoned veins\" and contrasted with grains \"in either thin melt veins or the edge zones of "
  "zoned melt veins\" (p.4); the individual grains are not otherwise chosen by a stated rule",
 "McCoy+2025_SI": NO_RULE,
 "McCoy+2025_UA": NO_RULE,
 "Zega+2025":
  "N — beam conditions are given per phase (\"Quantitative analyses of silicates, sulfides and oxides were "
  "run using a focused beam\"; \"A 2-μm defocused beam size, lower beam currents and shorter count times "
  "were used for phosphate and carbonate analyses\", p.9), but that is a setting per phase, not a rule for "
  "choosing which grains were analysed",
 "Barnes+2025 | CRPG":
  "Size — \"Aggregate particles (<1 mm) were mounted in epoxy, polished and were subsequently carbon "
  "coated\" (p.11); the grains analysed within them are not otherwise chosen by a stated rule",
 "Barnes+2025 | NHM":
  "Phase identity — \"Olivine and pyroxene grains were identified and characterized at the NHM\" (p.13), "
  "the paper's target being the anhydrous silicates in particles P1 and P2",
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
    print("  N cells: %d of %d" % (sum(1 for v in CELLS.values() if v.startswith("N ")), len(CELLS)))
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
