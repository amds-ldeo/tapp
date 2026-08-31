#!/usr/bin/env python3
"""Add `Mass Resolution Assignment` to Solution MC-ICP-MS (2026-08-30).

Found while checking B4 -- whether `Mass Resolution Setting`'s `Keyed By: (none)` was a lost
key. It was not: the library already splits the concept, and the split is correct.

    Mass Resolution Setting      (none)     the overall mode(s) for the procedure, scalar
    Mass Resolution Assignment   channel    the per-acquisition-mass assignment

The key is `channel`, NOT `analyte`, for the reason its own Column B gives: one analyte may be
acquired at more than one resolution, so the assignment is per acquired mass rather than per
element.

THE REAL GAP is that `Mass Resolution Assignment` sits in only 5 of the 9 ICP-MS TAPPs. Three
of the four absences are correct -- LA-Q x2 and Solution Q are quadrupoles with fixed unit
resolution and nothing to assign, which their own attested cells confirm
(`Unit resolution (quadrupole, fixed)`). Solution MC-ICP-MS is the outlier: a sector-field
instrument with selectable resolution, whose direct sibling LA-MC-ICP-MS carries the field,
and whose own attested cells are exactly the per-mass case --
`High-mass-resolution slit for K; low-mass-resolution slit for Cu and Zn`.

Rule 7.4a is satisfied before the fact: Solution MC already declares
`Collector Configuration` as `defines: channel per analyte` and already carries 10 other
channel-keyed fields.

The row is cloned from LA-MC-ICP-MS -- same analyser family -- with Column F authored from
Solution MC's own attested cell. It lands with ZERO attestation on purpose: the two MC cells
legitimately stay in `Mass Resolution Setting`, whose description explicitly invites them
("where individual analytes are assigned to different modes, state each"). This is a
structural gap being closed, not evidence being moved.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Mass Resolution Assignment"
AFTER = "Reported Variables and Units"

VALUES = {
 "Metadata Item": ITEM,
 "Description": ("Mass resolution mode used for acquisition. One analyte may be acquired at "
                 "more than one resolution, so the assignment is per acquired mass rather than "
                 "per element. The overall mode(s) used in the procedure are recorded in Mass "
                 "Resolution Setting (Group 3)."),
 "Procedure-Level Tier": "Basic",
 "Analysis-Level Tier": "Read-Only",
 "Data Type": "Text (free)",
 "Example / Allowed Content": "HR: K; LR: Cu, Zn | All LR | All MR | N/A | None",
 "Comments": "",
 "Last Update": STAMP,
 "Keyed By": "channel",
 "Purpose": ("The selected resolution determines which polyatomic interferences are physically "
             "resolved by the magnetic sector."),
}

def main():
    dry = "--apply" not in sys.argv
    folder = ROOT / "Solution MC-ICP-MS"
    if not folder.is_dir():
        cands = [d for d in ROOT.iterdir() if d.is_dir() and "MC-ICP-MS" in d.name and "LA" not in d.name]
        if len(cands) != 1:
            print(f"ABORT: cannot locate the Solution MC folder, candidates {cands}"); return 1
        folder = cands[0]
    vs = sorted(int(m.group(1)) for p in folder.glob("Solution_MC-ICP-MS_TAPP_v*.csv")
                if (m := re.fullmatch(r"Solution_MC-ICP-MS_TAPP_v(\d+)", p.stem)))
    if not vs:
        print(f"ABORT: no tables in {folder}"); return 1
    ver = vs[-1]
    src = folder / f"Solution_MC-ICP-MS_TAPP_v{ver}.csv"
    rows = list(csv.reader(open(src, encoding="utf-8-sig")))
    hdr = rows[0]
    iA = hdr.index("Metadata Item")
    if any(len(r) > iA and r[iA] == ITEM for r in rows[1:]):
        print(f"ABORT: {ITEM} already present"); return 1
    # 7.4a — the key must already have a definer in this TAPP
    iK = hdr.index("Keyed By")
    if not any(len(r) > iK and "defines" in r[iK] and "channel" in r[iK] for r in rows[1:]):
        print("ABORT: no `defines: channel` field in this TAPP (Rule 7.4a)"); return 1
    at = next((n for n, r in enumerate(rows) if len(r) > iA and r[iA] == AFTER), None)
    if at is None:
        print(f"ABORT: anchor row '{AFTER}' not found"); return 1
    new = [VALUES.get(h, "") for h in hdr]
    rows.insert(at + 1, new)
    print(f"Solution_MC-ICP-MS_TAPP_v{ver} -> v{ver+1}")
    print(f"  inserting '{ITEM}' at row {at+2}, after '{AFTER}'")
    for h in hdr[:10]:
        print(f"     {h[:28]:28s} = {VALUES.get(h,'')[:74]}")
    print(f"     (+{len(hdr)-10} trailing columns left empty — lands with zero attestation)")
    if not dry:
        dst = folder / f"Solution_MC-ICP-MS_TAPP_v{ver+1}.csv"
        shutil.copyfile(src, dst)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print(f"  wrote {dst.name}")
    print(f"\n{'DRY RUN — ' if dry else ''}1 field added")
    return 0

sys.exit(main())
