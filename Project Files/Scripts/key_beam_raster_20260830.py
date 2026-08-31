#!/usr/bin/env python3
"""`Beam Raster Dimensions` -> `sample > sampling unit` (2026-08-30).

The last `(none)` in the electron-beam setup cluster, keyed on the maintainer's decision.

Evidence is thin on its own -- ONE attested cell, `5x5 um2 for carbonates` -- and on the
"add on evidence, not for symmetry" rule that governed the rest of this backlog that would not
have been enough by itself. Two things carry it instead:

  * That single cell IS per phase, and it comes from the same sentence as a `Beam Diameter`
    cell already keyed on the same grounds: `1 um (point analysis); 5x5 um2 raster area for
    carbonates`. One procedural fact, split across two fields.
  * Every other field in the cluster is now `sample > sampling unit` -- `Beam Mode`,
    `Beam Current`, `Beam Diameter`, `Beam Damage Minimization`. A beam-setup field that
    cannot repeat while its four neighbours can is the same inconsistency B3 was opened to fix.

Rasters are used precisely on the beam-sensitive phases, so the field repeats wherever it is
used at all; the thin attestation reflects how rarely rasters are reported, not how rarely
they vary.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Beam Raster Dimensions"
KEY = "sample > sampling unit"

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
        iA, iK, iU = hdr.index("Metadata Item"), hdr.index("Keyed By"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if r[iK].strip() == KEY: continue
            if r[iK].strip() != "(none)":
                print(f"  ABORT: {base} is '{r[iK]}', expected '(none)'"); return 1
            root = KEY.split(">")[-1].strip()
            if not any(len(x) > iK and "defines" in x[iK] and root in x[iK] for x in rows[1:]):
                print(f"  ABORT: {base} has no `defines: {root}` field (Rule 7.4a)"); return 1
            r[iK], r[iU] = KEY, STAMP; hit = True; tot += 1
        if hit:
            print(f"  {base:24s} v{ver} -> v{ver+1}   {ITEM}: (none) -> {KEY}")
            if not dry:
                dst = src.parent / f"{base}_v{ver+1}.csv"
                shutil.copyfile(src, dst)
                with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
