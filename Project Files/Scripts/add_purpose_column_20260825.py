#!/usr/bin/env python3
"""
add_purpose_column_20260825.py — Phase 1 of the Description/Purpose split.

STRUCTURE ONLY. Adds Column J `Purpose`, empty, and renames Column B to `Description`.
No description text moves; no field changes meaning. Phase 2 (routing sentences from B into J)
is a separate, reviewed pass.

Why J and not C. Column ownership is declared per module by LETTER (`owned_columns`), and all 13
manifests own only A-F and I — none references a column past I. Appending at J therefore changes
ZERO manifests, where inserting at C would silently redefine every one of them, plus every
"Column F/G/H" reference in the docs and the ownership logic in compose_tapp.py. This is the same
trade recorded for `Keyed By`, which went to I rather than F for exactly this reason: stable
lettering bought at the cost of semantic adjacency, with the adjacency cost documented.

Mode-flag detection is the one thing that has to move: mode columns are located as the span
between the last fixed column and the `Literature Assessment` sentinel, so FIRST_MODE_COL goes
9 -> 10 in both validate_tapp.py and compose_tapp.py. Both use it only through the constant.

No version bump: consistent with the 2026-08-24 Track A reasoning, this changes no field's
meaning. Versions bump in Phase 2, when content actually moves.

Usage:  python3 add_purpose_column_20260825.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re

PURPOSE_AT = 9   # column J, immediately after Keyed By (I)

def migrate_csv(path, is_module):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if not rows: return None
    hdr = rows[0]
    hdr[0] = hdr[0].replace("﻿", "")
    if hdr[1] in ("Description / Purpose", "Description"):
        hdr[1] = "Description"
    if is_module:                      # modules own Description; Purpose is consumer-owned
        return rows, "header only"
    if len(hdr) > PURPOSE_AT and hdr[PURPOSE_AT] == "Purpose":
        return rows, "already migrated"
    for r in rows:
        while len(r) < PURPOSE_AT: r.append("")
    rows[0].insert(PURPOSE_AT, "Purpose")
    for r in rows[1:]: r.insert(PURPOSE_AT, "")
    return rows, "column added"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(); root = os.path.abspath(a.root)

    targets = [(os.path.join(root, e["tapp"]), False)
               for e in json.load(open(os.path.join(root, "composed_tapps.json")))["composed"]]
    targets += [(p, True) for p in sorted(glob.glob(
        os.path.join(root, "Claude Skills for TAPP", "modules", "*.csv")))]

    for path, is_mod in targets:
        res = migrate_csv(path, is_mod)
        if not res: continue
        rows, what = res
        print(f"  {'[module] ' if is_mod else '         '}{os.path.basename(path):<40} {what}")
        if a.apply:
            with open(path, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    edits = [("Claude Skills for TAPP/scripts/validate_tapp.py",
              [("FIRST_MODE_COL = 9", "COL_PURPOSE = 9    # Column J — consumer-owned (Phase 1, 2026-08-25)\nFIRST_MODE_COL = 10")]),
             ("Claude Skills for TAPP/scripts/compose_tapp.py",
              [("FIRST_MODE_COL = 9", "COL_PURPOSE = 9    # Column J — consumer-owned, never module-owned\nFIRST_MODE_COL = 10"),
               ('LETTER = {c: i for i, c in enumerate("ABCDEFGHI")}',
                'LETTER = {c: i for i, c in enumerate("ABCDEFGHIJ")}')])]
    for rel, subs in edits:
        p = os.path.join(root, rel)
        t = open(p, encoding="utf-8").read()
        for old, new in subs:
            if old not in t:
                print(f"  WARN not found in {rel}: {old!r}"); continue
            t = t.replace(old, new, 1)
            print(f"  {os.path.basename(rel)}: {old.splitlines()[0]!r} -> updated")
        if a.apply: open(p, "w", encoding="utf-8").write(t)

    if not a.apply: print("\n(dry run — pass --apply to write)")

if __name__ == "__main__":
    main()
