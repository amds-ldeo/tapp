#!/usr/bin/env python3
"""
Two user-directed fixes.

(A) `Collision/Reaction Cell (CRC) Configuration`, 4 TAPPs.
    Column F option "Not applicable (SF-ICP-MS)" -> "N/A".

    The parenthetical names one instrument class, but the field now appears in
    LA-MC and LA-MC U-Pb as well, where the reason a cell is absent is not
    "SF-ICP-MS". Generalising to the bare token both matches the convention and
    stops the option asserting something false in three of the four files.

    NOTE: this does NOT clear the finding. The check also wants `None`, which is
    arguably meaningless here — "no collision/reaction cell in use" is already
    `STD (standard mode, no gas)`, and "instrument has no cell" is now `N/A`.
    That leaves the field in the same class as `Technique`: a candidate for the
    closed exemption table rather than a gap to fill. Flagged, not decided.

(B) `sentinel-stray-N`, SEM family, 203 data-row cells.
    Conventions: the sentinel column's data rows must be EMPTY; only group
    headers carry `N`. The SEM TAPPs carry `N` on both. Header cells are
    preserved (6 per file) and only data rows are cleared — the exact inverse of
    the group-header patch applied earlier today, and the reason that patch was
    restricted to header rows.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
SENTINEL = "Literature Assessment"

CRC_FILES = [
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv",
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_UPb_TAPP_v5.csv",
    "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v2.csv",
    "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v1.csv",
]
CRC_OLD, CRC_NEW = "Not applicable (SF-ICP-MS)", "N/A"

SEM_FILES = [
    "SEM/SEM_TAPP_v6.csv",
    "SEM/SEM_Imaging_TAPP_v6.csv",
    "SEM/SEM_Composition_TAPP_v6.csv",
    "SEM/SEM_FIBSEM_TAPP_v6.csv",
]

COL_ITEM, COL_EXAMPLE, COL_UPDATE = 0, 5, 7
TODAY = "2026-08-10"


def is_group_header(name):
    return bool(name) and name[0].isdigit() and "." in name[:3]


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — CRC option + SEM sentinel cleanup\n")

    print("(A) CRC Configuration: 'Not applicable (SF-ICP-MS)' -> 'N/A'")
    n = 0
    for rel in CRC_FILES:
        p = ROOT / rel
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        hit = 0
        for r in rows[1:]:
            if (r and r[COL_ITEM].strip().startswith("Collision/Reaction Cell")
                    and len(r) > COL_EXAMPLE and CRC_OLD in r[COL_EXAMPLE]):
                r[COL_EXAMPLE] = r[COL_EXAMPLE].replace(CRC_OLD, CRC_NEW)
                while len(r) <= COL_UPDATE:
                    r.append("")
                r[COL_UPDATE] = TODAY
                hit += 1
        if APPLY and hit:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        print(f"    {rel.split('/')[-1]:34s} {hit} row(s)")
        n += hit
    print(f"    rows changed: {n}\n")

    print("(B) SEM sentinel column: clear N on DATA rows, keep on headers")
    tot = 0
    for rel in SEM_FILES:
        p = ROOT / rel
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        s = rows[0].index(SENTINEL)
        cleared = kept = 0
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip():
                continue
            if len(r) <= s:
                continue
            if r[s].strip() != "N":
                continue
            if is_group_header(r[COL_ITEM].strip()):
                kept += 1
            else:
                r[s] = ""
                cleared += 1
        if APPLY and cleared:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        print(f"    {rel.split('/')[-1]:34s} cleared {cleared:3d} data rows, kept {kept} headers")
        tot += cleared
    print(f"    cells cleared: {tot}\n")

    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
