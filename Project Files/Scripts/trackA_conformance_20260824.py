#!/usr/bin/env python3
"""
trackA_conformance_20260824.py — Track A conformance repairs. No semantic change.

Two repairs, both bringing files back to a canon they had drifted from:

A1  Column header names, against the canonical table in conventions.md "Column structure".
    Column B is `Description / Purpose` in 6 electron-beam TAPPs and `Description` in the other
    10; column F is `Example / Allowed Content` in 10 and `Example/Allowed Content` in the 6 LA
    tables. The canon is not the majority — conventions.md declares `Description / Purpose` and
    `Example / Allowed Content`, and every Module_*.csv already emits both, so the composed rows
    and the hand-written rows currently disagree about what column B is called. The 10 and the 6
    are repaired toward the doc.

A2  ASCII `um` in a Data Type unit, against `µm` used everywhere else. Four cells, all EPMA.
    Checked before changing: EPMA uses `µ` 48 times elsewhere in the same file ("0.25 µm
    diamond", "Defocused 5-10 µm"), so this is a slip in four cells, not a file-wide encoding
    choice that should be left alone.

NO VERSION BUMP, and no `Last Update` restamp. Neither repair changes what any field means: A1
touches only the header row, and A2 rewrites one unit as the same unit correctly spelled. Bumping
10 TAPPs would cascade into composed_tapps.json, 10 xlsx regenerations and the Rule 12 mirror for
zero semantic change. Recorded here because "what counts as structural" is an open question in
TAPP_Development_Log.md; if the call goes the other way this is cheap to redo with a bump.

Usage:  python3 trackA_conformance_20260824.py [--root ...] [--apply]
"""

from __future__ import annotations

import argparse
import csv
import json
import os

HEADER_CANON = {
    1: ("Description", "Description / Purpose"),
    5: ("Example/Allowed Content", "Example / Allowed Content"),
}

DATATYPE_FIXES = {
    "Numeric (um)": "Numeric (µm)",
    "Numeric pair (um x um)": "Numeric pair (µm x µm)",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    with open(os.path.join(root, "composed_tapps.json"), encoding="utf-8") as fh:
        paths = [c["tapp"] for c in json.load(fh)["composed"]]

    n_hdr = n_dt = n_files = 0
    for rel in sorted(paths):
        p = os.path.join(root, rel)
        with open(p, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
        changed = []

        for col, (wrong, right) in HEADER_CANON.items():
            if col < len(rows[0]) and rows[0][col] == wrong:
                rows[0][col] = right
                changed.append(f"header {chr(65 + col)}: {wrong!r} -> {right!r}")
                n_hdr += 1

        for row in rows[1:]:
            if len(row) > 4 and row[4] in DATATYPE_FIXES:
                changed.append(f"{row[0]}: {row[4]!r} -> {DATATYPE_FIXES[row[4]]!r}")
                row[4] = DATATYPE_FIXES[row[4]]
                n_dt += 1

        if not changed:
            continue
        n_files += 1
        print(f"{rel}")
        for c in changed:
            print(f"    {c}")
        if args.apply:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    verb = "applied" if args.apply else "would change (dry run)"
    print(f"\n{verb}: {n_files} files, {n_hdr} header cells, {n_dt} Data Type cells")
    if not args.apply:
        print("re-run with --apply to write")


if __name__ == "__main__":
    main()
