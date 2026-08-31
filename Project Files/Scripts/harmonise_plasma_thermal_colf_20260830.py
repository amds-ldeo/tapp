#!/usr/bin/env python3
"""Harmonise `Plasma Thermal Mode` Column F; first entry off the 7.8.11 backlog (2026-08-30).

Three variants across nine ICP-MS TAPPs, and it is NOT only the verbosity I assumed when
triaging it:

    [6] LA tables      Normal plasma (>1000 W RF) | Cool plasma (<=900 W RF) |
                       Mixed: specify mode per analytical sub-run | N/A | None
    [2] Solution Q/SF  Normal plasma | Cool plasma | Mixed: specify | N/A | None
    [1] Solution MC    Normal plasma | Cool plasma | N/A | None          <- Mixed MISSING

Solution MC lacks the `Mixed` member altogether, so a procedure that switched mode between
sub-runs had no value to select there. That is a gap, not drift.

The LA form wins: it is the majority (6 of 9), it is the only complete one, and it carries the
RF thresholds where someone choosing a value can see them. Column B states the same thresholds
after the B5 fix, but Column B is not what a picker reads.

Column F is TAPP-owned here -- `Module_ICPMS` owns A-E and I for this field but not F -- so
this is a plain TAPP edit and no module changes.

`Plasma Thermal Mode` is then REMOVED from COLF_DIVERGENCE_TRIAGED rather than reclassified,
per the rule recorded with that registry: an entry for a field that no longer diverges reads
as a standing decision that was never made.

NOT CHANGED, flagged: the member `Mixed: specify mode per analytical sub-run` carries a
trailing instruction. Now that the field is `Controlled list / Text`, the compound already
expects a listed term plus qualification, and the Legends sheet carries that guidance -- so
the ": specify ..." tail is arguably redundant in the same way `Other: specify` was. It is a
genuine member of the domain, unlike `Other: specify`, so it is left alone rather than swept
in on an argument this commit is not making.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Plasma Thermal Mode"
TARGET = ("Normal plasma (>1000 W RF) | Cool plasma (≤900 W RF) | "
          "Mixed: specify mode per analytical sub-run | N/A | None")

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
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if r[iE].strip() != "Controlled list / Text":
                print(f"  ABORT: {base} type is '{r[iE]}'"); return 1
            if r[iF].strip() == TARGET: continue
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            print(f"      was: {r[iF]}")
            r[iF], r[iU] = TARGET, STAMP; hit = True; tot += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  now: {TARGET}")
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
