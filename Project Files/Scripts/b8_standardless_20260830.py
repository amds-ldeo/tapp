#!/usr/bin/env python3
"""B8 — no new field: pin `Primary Calibration Standard Name` to cover standardless
quantification (2026-08-30).

B8 asked where standardless / virtual-standards quantification lives in EPMA and SEM, on the
assumption that a standards-mode field was missing. Checking first showed it is NOT missing:

    SEM and SEM_Composition, `Primary Calibration Standard Name`, Pascucci et al. 2026
        -> "Oxford factory internal standards"

That is the virtual-standard library, recorded in the right field, for the very papers that
prompted the question. TEM has the same home under its own name, `EDS Calibration Standard(s)`.
So this is the second time in this backlog -- after `EDS Quantification Method`, which turned
out to be `Matrix Correction Method` under another name -- that an apparent missing field was
an existing one. CHECK FOR AN EXISTING HOME BEFORE ADDING A FIELD.

WHAT IS ACTUALLY WRONG is the description. It reads as though a primary reference MATERIAL
always exists -- "Give the material name, its source or supplier, and a citation for the
accepted values" -- so an analyst doing standardless work finds no home and puts the answer
somewhere else. That is exactly what happened: the same Pascucci value also sits in
`Analyte Estimation Method` and `EDS Spectral Processing Type`, neither of which asks that
question. The scatter is a symptom of the description, and the description is the fix.

Written technique-neutrally and applied to all 12 TAPPs carrying the field, because Column B
is uniform here and splitting it would trip `colb-divergence`. Standardless has an ICP-MS
analogue -- semi-quantitative work on stored response factors rather than matrix-matched
standards -- so one sentence serves both.

NOT DONE, flagged: TEM's `Matrix Correction Method` still lists `Standardless` and `Direct
comparison to reference spectra`, which are STANDARDS-MODE values sitting in a
matrix-correction field. Standardless is a question about where the k-factors came from, not
about the algorithm that corrects for matrix effects; the two are orthogonal. Removing them
is a design change to a field merged only days ago and wants its own decision.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Primary Calibration Standard Name"

OLD_TAIL = ("Give the material name, its source or supplier, and a citation for the accepted "
            "values used.")
ADD = (" Where calibration instead uses the vendor's stored library or theoretical response "
       "factors rather than measured reference materials — 'standardless' or "
       "'semi-quantitative' quantification — record that here, naming the library or model "
       "used. 'None' means no calibration was performed at all, which is a different answer.")

def main():
    dry = "--apply" not in sys.argv
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    tot = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iB, iU = hdr.index("Metadata Item"), hdr.index("Description"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if ADD.strip() in r[iB]: continue
            if not r[iB].rstrip().endswith(OLD_TAIL):
                print(f"  ABORT: {base} description does not end as expected:\n     ...{r[iB][-90:]}")
                return 1
            r[iB] = r[iB].rstrip() + ADD
            r[iU] = STAMP; hit = True; tot += 1
        if hit:
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            if not dry:
                dst = src.parent / f"{base}_v{ver+1}.csv"
                shutil.copyfile(src, dst)
                with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
