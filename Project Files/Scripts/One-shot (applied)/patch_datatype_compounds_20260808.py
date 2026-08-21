#!/usr/bin/env python3
"""
patch_datatype_compounds_20260808.py

Two cleanups arising from ratifying compound Data Types in conventions.md.

Cleanup 1 — malformed compounds (11 rows, 4 distinct fixes)
-----------------------------------------------------------
    'Numeric + label'       -> 'Text (free)'          Background Position(s), 3 TAPPs
    'Numeric or Text'       -> 'Numeric + unit / Text' Detection Limit, 3 TAPPs
    'Numeric (ms) or Text'  -> 'Numeric (ms) / Text'   Dwell Time per Mass, 2 TAPPs
    'URI / Text (free)'     -> 'URI / IGSN'            Sample IGSN, 3 TAPPs

  'Numeric + label' becomes Text (free) rather than a compound: the value is a single
  composite string ("+5 mm (High), -5 mm (Low)"), not a number with an alternative form.
  'URI / Text (free)' on an IGSN field becomes the named type URI / IGSN, which already
  exists for exactly this purpose.

Cleanup 2 — compound controlled lists missing absence values (23 rows)
---------------------------------------------------------------------
  A field typed 'Controlled list / ...' must offer N/A and None in Column F so a user can
  record absence. It does NOT need 'Other: specify' — the compound's Text component already
  permits an unlisted answer. These 23 rows became visible only once compounds were ratified
  and the linter began checking them; the gaps predate that change.

Scope of change
---------------
Columns E and F only. No field name, description, tier, comment, mode flag, or literature
assessment value is touched.

Version policy
--------------
No version bump and no Last Update change, consistent with the 2026-08-07 patches. Cleanup 1
corrects malformed labels to their well-formed equivalents with no change of meaning; cleanup 2
restores conformance to an existing rule.
"""

from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COL_ITEM, COL_TYPE, COL_EXAMPLE = 0, 4, 5

MALFORMED = {
    "numeric + label": "Text (free)",
    "numeric or text": "Numeric + unit / Text",
    "numeric (ms) or text": "Numeric (ms) / Text",
    "uri / text (free)": "URI / IGSN",
}
ABSENCE = ["N/A", "None"]


def find_tapps(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {"unpacked_tapp", "Pre-VIM3 Reference Archive (2026-07-24)"}
                       and not d.startswith(".")]
        for fn in filenames:
            if re.search(r"_TAPP_v\d+(\.\d+)?\.csv$", fn):
                out.append(os.path.join(dirpath, fn))
    latest = {}
    for p in out:
        key = os.path.basename(p).rsplit("_v", 1)[0]
        ver = float(re.search(r"_v(\d+(?:\.\d+)?)\.csv$", p).group(1))
        if key not in latest or ver > latest[key][0]:
            latest[key] = (ver, p)
    return [v[1] for v in sorted(latest.values(), key=lambda x: x[1])]


def patch(path, dry_run=False):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    edits = []
    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= COL_EXAMPLE:
            continue
        item = row[COL_ITEM].strip()
        if not item or re.match(r"^\d+\.\s", item):
            continue
        dt = row[COL_TYPE].strip()

        # Cleanup 1
        new = MALFORMED.get(dt.lower())
        if new:
            edits.append((n, item, "E", dt, new))
            row[COL_TYPE] = dt = new

        # Cleanup 2 — runs after, so a row fixed above is re-evaluated under its new type
        if dt.startswith("Controlled list /"):
            ex = row[COL_EXAMPLE]
            missing = [v for v in ABSENCE if v.lower() not in ex.lower()]
            if missing:
                addition = "".join(f" | {v}" for v in missing)
                edits.append((n, item, "F", f"…{ex[-34:]}", f"…{ex[-34:]}{addition}"))
                row[COL_EXAMPLE] = ex + addition

    if edits and not dry_run:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
    return edits


def main():
    dry_run = "--dry-run" in sys.argv
    total_e = total_f = 0
    files = 0

    for path in find_tapps(ROOT):
        edits = patch(path, dry_run=dry_run)
        if not edits:
            continue
        files += 1
        print(f"\n{os.path.relpath(path, ROOT)}")
        for n, item, col, old, new in edits:
            if col == "E":
                total_e += 1
                print(f"    row {n:>4}  [E]  {item[:34]:<34}  {old!r} -> {new!r}")
            else:
                total_f += 1
                print(f"    row {n:>4}  [F]  {item[:34]:<34}  {old} -> {new}")

    verb = "would be" if dry_run else ""
    print(f"\n{'=' * 78}")
    print(f"  {total_e} Data Type cell(s) and {total_f} Column F cell(s) {verb} updated "
          f"across {files} file(s).")
    if dry_run:
        print("  Dry run — nothing written.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
