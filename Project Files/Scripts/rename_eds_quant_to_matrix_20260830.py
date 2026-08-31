#!/usr/bin/env python3
"""Rule 1 name-variant resolution: TEM `EDS Quantification Method` -> `Matrix Correction
Method` (2026-08-30).

Found while checking whether the SEM tables needed `EDS Quantification Method` added. They
did not — the field already existed there under another name, and the split is perfectly
disjoint along the EPMA/SEM <-> TEM authorship boundary the register tracks as LINEAGE:

    Matrix Correction Method    EPMA, SEM, SEM_Composition   (TEM does not have it)
    EDS Quantification Method   TEM                          (EPMA/SEM do not have it)

Both answer the same question — how measured X-ray intensities were converted to
concentrations — with technique-appropriate members (bulk XPP/PAP/ZAF vs thin-film
Cliff-Lorimer/zeta-factor). Adding the TEM name to SEM would have duplicated the field.

`Matrix Correction Method` wins: 3 tables to 1, and it does not falsely narrow the EPMA/SEM
field to EDS when those tables also do WDS.

Columns C, D, E and I already MATCH across all four (Basic / Read-Only / `Controlled list` /
`(none)`), so this is a Column A + Column B change only. TEM adopts the EPMA/SEM description
verbatim, which is already uniform across those three — the name and the description win
together, and adopting it leaves colb-divergence clean.

Column F is NOT harmonised: it is technique-appropriate allowed content, and thin-film
quantification genuinely differs from bulk matrix correction.

NOT DONE HERE: the merged field's Data Type. EPMA/SEM classified CLOSED (7 attested,
100% bare); TEM classified `/ Text` (7 attested, 5 qualified — k-factor sourcing and
absorption-correction status). Merged that is ~64% bare, i.e. MIXED, and `/ Text` is the
safer resolution because a compound accommodates both. All four read `Controlled list`
today, so the rename alone keeps the type uniform; the retype belongs in the coordinated
Data Type commit.
"""
import csv, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
OLD, NEW = "EDS Quantification Method", "Matrix Correction Method"
DESC = ("X-ray matrix correction algorithm applied during quantitative EDS or WDS data "
        "reduction. For X-ray mapping, applies when raw count maps are converted to "
        "quantitative concentration maps.")

def main():
    dry = "--apply" not in sys.argv
    src = ROOT / "TEM" / "TEM_TAPP_v37.csv"
    dst = ROOT / "TEM" / "TEM_TAPP_v38.csv"
    if not src.exists():
        print(f"MISSING {src}"); return 1
    rows = list(csv.reader(open(src, encoding="utf-8-sig")))
    hdr = rows[0]
    iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
    iU = hdr.index("Last Update")
    if any(r[iA] == NEW for r in rows[1:] if len(r) > iA):
        print(f"ABORT: TEM already carries a '{NEW}' row — merge, do not rename."); return 1
    hit = 0
    for r in rows[1:]:
        if len(r) <= iU or r[iA] != OLD: continue
        print(f"TEM_TAPP_v37 -> v38")
        print(f"   A: {r[iA]}\n   -> {NEW}")
        print(f"   B: {r[iB][:110]}\n   -> {DESC[:110]}")
        r[iA], r[iB], r[iU] = NEW, DESC, STAMP
        hit += 1
    if hit != 1:
        print(f"ABORT: expected exactly 1 '{OLD}' row, found {hit}"); return 1
    if not dry:
        shutil.copyfile(src, dst)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{hit} row renamed")
    return 0

sys.exit(main())
