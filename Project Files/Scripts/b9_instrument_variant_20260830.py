#!/usr/bin/env python3
"""B9 — split `VP-SEM / ESEM` and drop the combinatorial member (2026-08-30).

Papers report the two halves separately -- `VP (Variable Pressure)` x4 and
`ESEM (Environmental SEM)` x2 against `VP-SEM / ESEM` x6 -- and they are genuinely different
instruments: variable pressure runs a dry gas at low chamber pressure for uncoated or charging
specimens, while an environmental SEM runs water vapour at higher pressure for hydrated ones
and needs a gaseous secondary electron detector. THE LIBRARY ALREADY DISTINGUISHES THEM
ELSEWHERE -- `Chamber Pressure` carries `30 Pa (H2O vapor, ESEM)` against
`130 Pa (N2, VP-SEM)` -- so the combined member was the outlier, not the distinction.

    was:  Standard SEM | FIB-SEM dual-beam | VP-SEM / ESEM | FIB-SEM dual-beam + VP | N/A | None
    now:  Standard SEM | FIB-SEM dual-beam | VP-SEM | ESEM | N/A | None

`FIB-SEM dual-beam + VP` goes too. It is a COMBINATORIAL member -- one product of two axes --
and combinatorial members do not survive a split: separating VP from ESEM would demand a
`+ ESEM` twin, then a `+ ESEM + something` next time. It has ZERO attested cells, and the
`; ` join convention already sanctioned for `Analytical Mode` under Rule 3 expresses the same
thing without multiplying members: `FIB-SEM dual-beam; VP-SEM`. Column B now says so.

Column B also gains a pointer that 10 attested cells needed: `FESEM (Field Emission SEM)`
appears 10 times in this field and is NOT a platform variant -- field emission is a SOURCE,
recorded by `Electron Source`, which already carries the FEG members. Same reasoning as the
B8 description fix: where a decade of cells lands on the wrong axis, the description is what
sent them there.

TAPP-owned, `Controlled list` (closed), 4 SEM tables.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Instrument Variant"
OLD_F = "Standard SEM | FIB-SEM dual-beam | VP-SEM / ESEM | FIB-SEM dual-beam + VP | N/A | None"
NEW_F = "Standard SEM | FIB-SEM dual-beam | VP-SEM | ESEM | N/A | None"
NEW_B = ("Broad platform type of the instrument. 'Standard SEM': dedicated electron-only SEM "
         "column. 'FIB-SEM dual-beam': combined focused ion beam and SEM columns (enables TEM "
         "specimen preparation, 3D serial sectioning, ion-beam milling). 'VP-SEM': "
         "variable-pressure SEM, a dry gas at low chamber pressure for uncoated or charging "
         "specimens. 'ESEM': environmental SEM, water vapour at higher pressure for hydrated "
         "specimens, requiring a gaseous secondary electron detector. Where an instrument "
         "combines categories, join them with '; ' — 'FIB-SEM dual-beam; VP-SEM' — rather "
         "than looking for a combined member. This field records the COLUMN AND CHAMBER "
         "configuration only: field emission is a source type and belongs in Electron Source, "
         "not here.")

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
        iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
        iE, iF = hdr.index("Data Type"), hdr.index("Example / Allowed Content")
        iU = hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if r[iE].strip() != "Controlled list":
                print(f"  ABORT: {base} type is '{r[iE]}'"); return 1
            if r[iF].strip() != OLD_F:
                print(f"  ABORT: {base} Column F unexpected:\n     {r[iF]}"); return 1
            r[iF], r[iB], r[iU] = NEW_F, NEW_B, STAMP
            hit = True; tot += 1
        if hit:
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            if not dry:
                dst = src.parent / f"{base}_v{ver+1}.csv"
                shutil.copyfile(src, dst)
                with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    print(f"  F: {OLD_F}\n  -> {NEW_F}")
    return 0

sys.exit(main())
