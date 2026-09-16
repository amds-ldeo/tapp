#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Selection Criteria` — batch 4: TEM (21 cells), completing the field.

    python3 "Project Files/Scripts/phase3_sampling_unit_selection_tem_20260916.py" [--apply]

Same source rule and the same line against `Sampling Unit Type` as batches 1-3. With this batch the
third and last sibling field is complete, and with it the whole sampling-unit trio.

TEM STATES THIS FIELD ALMOST AS OFTEN AS LA DOES, for the same underlying reason: a FIB section costs
a day of work and destroys what it cuts, so the paper defends where it was cut. Chaves 2023 gives a
size cut-off, Dobrica 2022 avoids regions damaged by earlier ion-probe work, Thompson 2020 picks its
targets in the SEM first, Seifert 2026 cuts across two grains chosen for their zoning.

Singerling 2025 is the one paper in the whole pass that states the ABSENCE of a criterion outright —
"We did not use any specific parameters in selecting which particles to investigate (i.e., they were
selected arbitrarily)". That is a stated value, not an N: the paper answers the question.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Selection Criteria"
REL = "TEM/TEM_TAPP_v56.csv"

ZEGA_LAB = ("N — this laboratory's passage states its instrument and conditions only; the one stated siting rule "
            "belongs to the FIB work, \"All sections were extracted from varied regions of matrix within the "
            "particles\" (p.9)")
SEIFERT = ("Zoning, seen in CL before extraction — \"A cluster of two apatite grains that exhibit oscillatory and "
           "complex zoning, respectively, were selected for FIB extraction and TEM analysis (OREX-803173-100)\" "
           "(p.7)")
CYMES = ("Position on the space-weathered surface — the section was cut through \"The space-weathered surface of the "
         "sample, containing a pyroxene grain labeled “1pyx” and a surface-adhered pyroxene grain labeled "
         "“2pyx,”\" which \"was first protected with a 1–2 lm thick layer of electron beam deposited "
         "amorphous carbon\" (p.3)")
MO = ("N — \"Two grains were selected from CE-5 lunar soil (CE5C0400YJFM00505)\" (p.2), but no criterion is given "
      "for the choice; the only stated constraint is on the dispersed material, \"Several lunar soil grains smaller "
      "than 50 μm were dispersed on aluminum double-sided tape\" (p.2)")

CELLS = {
 "Chaves2023":
  "Size, and irradiation state — \"We selected individual magnetite grains from the irradiated regions that were "
  "large enough (>15 μm) to extract FIB sections\" (p.3)",
 "Zega2025|HF5000": ZEGA_LAB,
 "Zega2025|TitanX": ZEGA_LAB,
 "Zega2025|Talos":
  "N — this laboratory crushed its material rather than sectioning it (\"TEM samples were prepared by crushing the "
  "grain\", p.10), and no rule is given for which grains were taken",
 "Zega2025|2500SE": ZEGA_LAB,
 "Matsumoto2021|Tecnai":
  "Exposure of the target phase at the surface — \"We prepared a FIB section (11_5A_1) from an area where the iron "
  "sulfides (5 mm width) are exposed on the surface of grain\" (p.3)",
 "Matsumoto2021|JEM-3200FSK":
  "Phase identity within the one section — the quantitative EDX analyses are of \"the iron sulfides\" exposed at the "
  "space-weathered surface (p.3); no finer rule is given for the analysed points",
 "Matsumoto2021|ARM200F":
  "Position within the one section — mapping targets the space-weathered rim and the phases beneath it, the section "
  "having been cut where \"the iron sulfides ... are exposed on the surface of grain\" (p.3)",
 "KellerBerger2014":
  "N — the particles were allocated rather than chosen (\"We were allocated particles RA-QD02-0125 and RA-QD02-0211\", "
  "p.2), and no rule is given for the ultramicrotome sections taken from them",
 "Zeng2024":
  "Presence of an impact feature — of 25 glass beads, \"A micrometeorite impact crater was observed on the surface of "
  "one of these 25 glass beads (CE5C0600YJFM00304) using an optical microscope\" (p.5), and \"An ultra-thin foil of "
  "the micrometeorite impact crater was prepared for TEM observations\" (p.6)",
 "Dobrica2022|Titan G2":
  "Phase targeting, and avoidance of earlier beam damage — sections were cut at phases \"identified in the polished "
  "section by SEM/EDS\", and \"Additionally, we selected the regions that were the least damaged by the ion "
  "microprobe measurements performed during previous studies\" (p.3); two sections target carbonates, the others "
  "\"regions containing micrometer-sized secondary phases such as Ca-phosphates ... and magnetite\" (p.3)",
 "Dobrica2022|TitanX":
  "Phase targeting — the mapping is of the carbonate-bearing sections, \"The elemental compositions of carbonates "
  "reported here were extracted from EDS mapping over areas of 5–10 nm (at the Molecular Foundry)\" (p.2)",
 "Singerling2025":
  "None, stated explicitly — \"We did not use any specific parameters in selecting which particles to investigate "
  "(i.e., they were selected arbitrarily)\" (p.2)",
 "Thompson2020":
  "Picked in the SEM first, by lasering dose and phase — \"We identified regions of interest in the SEM for further "
  "investigation in the TEM\", and the four sections comprise a 1× lasered matrix region, a 5× lasered matrix region "
  "\"dominated by phyllosilicates\", a 5× lasered sulfide grain and a 5× lasered olivine grain (p.4)",
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE": SEIFERT,
 "Seifert2026|HF5000": SEIFERT,
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos": MO,
 "Mo2022|HF5000":
  "Continuity with the earlier analyses — \"The same FIB foil extracted from CE5C0400YJFM00505-G1 for the AES "
  "analysis was also analyzed using TEM-EELS\" (p.5)",
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
    print("  %s: %d cells -> %s (%d N)" % (os.path.basename(REL), len(m), os.path.basename(new),
                                           sum(1 for v in CELLS.values() if v.startswith("N "))))
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
