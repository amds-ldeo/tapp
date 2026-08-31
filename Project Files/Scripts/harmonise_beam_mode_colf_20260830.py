#!/usr/bin/env python3
"""Harmonise `Beam Mode` Column F; 7.8.11 backlog (2026-08-30).

Two variants across the three electron-beam TAPPs, differing in two cosmetic ways:

    [2] SEM, SEM_Composition   'Focused' | 'Defocused' | 'Rastered' | N/A | None
    [1] EPMA                   Focused | Defocused | Raster | N/A | None

    ->  all three              Focused | Defocused | Rastered | N/A | None

Quoting goes, matching the house norm and the `Stage Scan vs. Beam Scan` harmonisation earlier
today. `Rastered` beats `Raster` on two grounds: it is the attested form (`Rastered 5x5 um2 for
carbonates`), and it is parallel with `Focused` and `Defocused` -- all three describe the state
the beam is in, which is what the field asks.

This is a RENAME of one member, so the additive guard used for the superset cases would refuse
it. The script asserts the exact expected before-value in each table instead, which is the
stricter check for a rename: it cannot silently rewrite a list that has drifted since.

Not module-owned. The field is `Controlled list / Text` and keyed `sample > sampling unit`;
neither changes here.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Beam Mode"
TARGET = "Focused | Defocused | Rastered | N/A | None"
EXPECT = {"'Focused' | 'Defocused' | 'Rastered' | N/A | None",
          "Focused | Defocused | Raster | N/A | None"}

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
        iA, iF, iU = hdr.index("Metadata Item"), hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            cur = r[iF].strip()
            if cur == TARGET: continue
            if cur not in EXPECT:
                print(f"  ABORT: {base} Column F is not one of the two known variants:\n     {cur}")
                return 1
            print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {cur}")
            r[iF], r[iU] = TARGET, STAMP; hit = True; tot += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  now: {TARGET}\n\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
