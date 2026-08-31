#!/usr/bin/env python3
"""Data Type reclassification, commit 3 of 3 — close `Technique` (2026-08-30).

Held back from commit 2 because its Column F was known incomplete: three TAPPs' lists did
not contain their own technique. Closing an incomplete list is what produced
amds-ldeo/tapp#3's 84 invalid publication cells, so the vocabulary is fixed FIRST and the
`Other: specify` strip follows.

Adjudicated (Rule 1, cross-TAPP technique vocabulary):

  A1  Each list holds the TAPP's OWN technique, not a menu of siblings. The three Solution
      TAPPs already worked this way and are the model -- 29 of 29 attested cells match their
      single listed value. The four LA-Q/LA-SF tables shared a generic menu that both omitted
      their own technique (LA-SF: 0 of 7 attested cells matched) and offered techniques they
      are not (OES, ToF).
  A2  The fs/ns laser distinction is NOT part of the technique identifier. `Laser Pulse
      Duration` already records it, with `290 fs (Yb:KGW)` among its own examples, so the
      attested `fs-LA-Q-ICP-MS` cells would duplicate a field that already holds it.
  A3  Lab-XCT adopts the papers' `Lab XCT` over `XCT (laboratory, polychromatic cone-beam)`,
      which matched nothing; `Lab XCT (nano-CT)` is attested 4x and joins as a real variant.
  A5  Technique is PLATFORM-level. Attested `SEM-EDS` and TEM's `STEM; EDS; EELS` composites
      name detectors, which `Spectroscopic Detector(s)` already records.

`LA-ICP-MS (analyser not specified)` is added to the two LA-Q tables only, where 2 cells
report the platform without naming the analyser. This is the subtype-unstated pattern from
`Electron Source`: a closed list that enumerates subtypes needs a member for the coarse
answer. LA-SF does NOT get one -- all 7 of its cells name the analyser. Members are added
where evidence warrants, not for symmetry.

`N/A | None` is removed from the five lists still carrying it. Rule 1 exempts `Technique`
from those options as semantically empty -- every procedure has a technique -- and the
Solution tables already omit them.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"

NEW = {
 "EPMA_TAPP":                "EPMA-WDS | EPMA-EDS | EPMA-WDS+EDS",
 "SEM_TAPP":                 "SEM | SEM/FIB-SEM",
 "SEM_Composition_TAPP":     "SEM | SEM/FIB-SEM",
 "SEM_FIBSEM_TAPP":          "SEM | SEM/FIB-SEM",
 "SEM_Imaging_TAPP":         "SEM | SEM/FIB-SEM",
 "TEM_TAPP":                 "TEM | STEM | TEM/STEM",
 "Lab-XCT_TAPP":             "Lab XCT | Lab XCT (nano-CT)",
 "LA-MC-ICPMS_TAPP":         "LA-MC-ICP-MS",
 "LA-MC-ICPMS_UPb_TAPP":     "LA-MC-ICP-MS",
 "LA-Q-ICP-MS_TAPP":         "LA-Q-ICP-MS | LA-ICP-MS (analyser not specified)",
 "LA-Q-ICP-MS_UPb_TAPP":     "LA-Q-ICP-MS | LA-ICP-MS (analyser not specified)",
 "LA-SF-ICP-MS_TAPP":        "LA-SF-ICP-MS",
 "LA-SF-ICP-MS_UPb_TAPP":    "LA-SF-ICP-MS",
 "Solution_MC-ICP-MS_TAPP":  "Solution MC-ICP-MS",
 "Solution_Q-ICP-MS_TAPP":   "Solution Q-ICP-MS",
 "Solution_SF-ICP-MS_TAPP":  "Solution SF-ICP-MS",
}

def main():
    dry = "--apply" not in sys.argv
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    missing = set(NEW) - set(seen)
    if missing:
        print(f"ABORT: no table found for {sorted(missing)}"); return 1
    n = 0
    for base, (ver, src) in sorted(seen.items()):
        if base not in NEW:
            print(f"  ABORT: {base} has no Technique vocabulary defined"); return 1
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != "Technique": continue
            if r[iE].strip() != "Controlled list":
                print(f"  ABORT: {base} Technique is '{r[iE]}'"); return 1
            if r[iF] == NEW[base]: continue
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            print(f"      was: {r[iF]}")
            print(f"      now: {NEW[base]}")
            r[iF], r[iU] = NEW[base], STAMP; hit = True; n += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{n} Technique cell(s) rewritten")
    return 0

sys.exit(main())
