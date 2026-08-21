#!/usr/bin/env python3
"""
patch_sentinel_cleanup_20260807.py

Clears stray values from the sentinel column ("Literature Assessment") on data rows.

Background
----------
conventions.md requires the sentinel column's data rows to be empty; only group
header rows carry N. Six TAPPs have the literal string "Literature Assessment"
sitting in that column on 22 data rows — a header value that appears to have been
filled down when the sentinel convention was introduced. Any consumer reading the
column to locate the mode/literature boundary sees content where the spec
promises none.

Scope of change
---------------
Sentinel-column cells only. No field name, description, tier, data type, example,
comment, mode flag, or literature assessment value is touched.

Version policy
--------------
No version bump and no Last Update change. This is a data-integrity fix to
metadata infrastructure, not a substantive edit to any field, so neither the
integer-bump rule (structural revision) nor the decimal-bump rule (description or
example change) in conventions.md applies.

Files modified
--------------
    EPMA/EPMA_TAPP_v9.csv                            2 cells
    LA-ICP-MS/LA-ICPMS_TAPP_v13.csv                  1 cell   (stale/frozen branch)
    LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v5.csv         1 cell
    XCT/Lab-XCT_TAPP_v10.csv                         1 cell
    TEM/TEM_TAPP_v9.csv                              1 cell
    SEM/SEM_TAPP_v6.csv                              8 cells
    SEM/SEM_Composition_TAPP_v6.csv                  8 cells
                                                    ---------
                                                    22 cells
"""

from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SENTINEL_HEADER = "Literature Assessment"
COL_ITEM = 0
COL_UPDATE = 7


def is_group_header(row):
    a = row[COL_ITEM].strip() if row else ""
    return bool(a) and bool(re.match(r"^\d+\.\s", a))


def is_separator(row):
    return not any(
        (row[i].strip() if i < len(row) else "") for i in range(COL_ITEM, COL_UPDATE + 1)
    )


def find_tapps(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in {"unpacked_tapp", "Pre-VIM3 Reference Archive (2026-07-24)"}
            and not d.startswith(".")
        ]
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
    if not rows:
        return []

    header = rows[0]
    idx = next((i for i, h in enumerate(header) if h.strip() == SENTINEL_HEADER), None)
    if idx is None:
        return []

    cleared = []
    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= idx or is_separator(row) or is_group_header(row):
            continue
        val = row[idx].strip()
        if not val or val == "N":
            # Empty is correct; "N" is a separate, harmless convention drift that
            # this patch deliberately leaves alone.
            continue
        cleared.append((n, row[COL_ITEM].strip(), val))
        row[idx] = ""

    if cleared and not dry_run:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
    return cleared


def main():
    dry_run = "--dry-run" in sys.argv
    total = 0
    touched = []

    for path in find_tapps(ROOT):
        cleared = patch(path, dry_run=dry_run)
        if not cleared:
            continue
        rel = os.path.relpath(path, ROOT)
        touched.append(rel)
        total += len(cleared)
        print(f"\n{rel}  —  {len(cleared)} cell(s) cleared")
        for n, item, val in cleared:
            print(f"    row {n:>4}  {item[:48]:<48}  removed {val!r}")

    verb = "would be" if dry_run else ""
    print(f"\n{'=' * 78}")
    print(f"{total} sentinel cell(s) {verb} cleared across {len(touched)} file(s).")
    if dry_run:
        print("Dry run — nothing written.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
