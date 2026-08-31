#!/usr/bin/env python3
"""Harmonise `Guard Electrode` Column F; 7.8.11 backlog (2026-08-30).

Two variants across nine ICP-MS TAPPs, differing in one member's wording only:

    [6] LA tables      On | Off | Not applicable (instrument does not have guard electrode) | N/A | None
    [3] Solution       On | Off | Not installed | N/A | None

Same concept, two phrasings -- so this is a rename, not a member gain or loss.

THE MINORITY FORM WINS, which is why this is not a mechanical majority vote.
`Not applicable (instrument does not have guard electrode)` collides with `N/A`, which is
already in the same list and means exactly "not applicable". A picker faced with both cannot
tell them apart, and whichever they choose the other becomes noise. `Not installed` says the
distinct thing the member is actually for -- the hardware is absent, as opposed to present and
switched off -- and it is the wording `Collision/Reaction Cell (CRC) Configuration` already
uses for absent cell hardware (`Not installed | STD | KED | DRC`). Adopting it makes the two
hardware-presence fields agree.

Neither phrasing is attested: the two literature cells read `"Pt-guard electrode: On,
grounded"` and `On (shield torch system used)`, so nothing is lost by preferring the clearer
one.

Column F is TAPP-owned -- `Module_ICPMS` owns A-E and I for this field, not F -- so no module
changes.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Guard Electrode"
TARGET = "On | Off | Not installed | N/A | None"

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
            if r[iF].strip() == TARGET: continue
            print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {r[iF]}")
            r[iF], r[iU] = TARGET, STAMP; hit = True; tot += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  now: {TARGET}\n\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
