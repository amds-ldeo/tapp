#!/usr/bin/env python3
"""`Beam Diameter` -> `sample > sampling unit` (2026-08-30).

Noticed while keying `Beam Mode` in B3: `Beam Diameter` sat at `(none)` while the rest of its
cluster was keyed, and `Beam Mode`'s cells were embedding diameters per phase. Checking the
field's OWN cells confirms it rather than inferring from the neighbour -- 6 of 13 attested
cells vary by mineral phase:

    1-2 um (olivine, pyroxene, Fe-Ti-Cr oxides); 5-10 um defocused (maskelynite, phosphate...)
    Focused (exact diameter N); 2-5 um defocused (plagioclase and polymorphs)
    5 um (carbonates); 1 um (silicates/oxides)
    Focused (silicates, sulfides, oxides); 2 um defocused (phosphates, carbonates)
    1 um (point analysis); 5x5 um2 raster area for carbonates

Same 6-of-13 ratio as `Beam Mode`, from the same papers naming the same phases: one procedural
fact -- a different beam setup per phase -- expressed across several fields. `sampling unit` is
the key whose domain covers phases, and the containment form matches the three beam fields
already keyed: `Beam Current`, `Beam Damage Minimization`, `Beam Mode`.

NOT DONE, flagged: `Beam Raster Dimensions` is the last `(none)` in the cluster and its single
attested cell (`5x5 um2 for carbonates`) is also per phase -- from the same paper, the same
sentence. The cluster argument says key it; N=1 says wait. Left for a decision rather than
swept in on symmetry.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Beam Diameter"
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
