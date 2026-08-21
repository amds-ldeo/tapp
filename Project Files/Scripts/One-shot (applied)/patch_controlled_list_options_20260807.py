#!/usr/bin/env python3
"""
patch_controlled_list_options_20260807.py

Adds the required `Other: specify | N/A | None` options to Column F of seven
Controlled list fields that were missing them.

Background
----------
conventions.md requires every Controlled list field to offer `N/A | None |
Other: specify` in Column F so a user can always record an absent or unlisted
value. Seven fields across three TAPPs did not. They became visible only after
the same-day datatype-synonym patch relabelled them from "Controlled vocabulary"
to "Controlled list" — the gaps predate that patch and were hidden by the wrong
label, not caused by it.

`Analytical Mode` is deliberately NOT included. It is exempt from this
requirement (see the exemption table in the Data Type Vocabulary section of
conventions.md) because Rule 3 binds its allowed values to the mode flag column
labels exactly.

House style
-----------
Existing compliant fields append the options in the order
`… | Other: specify | N/A | None`. This patch matches that ordering.

Changes
-------
Six fields are purely additive — existing values are preserved and the options
appended:

    EPMA_TAPP_v9              EDS Acquisition Mode
    SEM_TAPP_v6               Beam Mode, Stage Scan vs. Beam Scan
    SEM_Composition_TAPP_v6   Beam Mode, Stage Scan vs. Beam Scan

Two are a replacement, not an append — the only substantive edit in this patch:

    SEM_TAPP_v6               Technique per Analyte
    SEM_Composition_TAPP_v6   Technique per Analyte

    Column F held an illustrative string ('Si: WDS; Al: WDS; Fe: WDS; Na: EDS;
    C: EDS') rather than an enumeration of allowed values, so appending the
    generic options would have produced something incoherent. EPMA's Rule 2
    counterpart, "EPMA Technique per Analyte", already carries the well-formed
    version — `WDS | EDS | Other: specify | N/A | None` — so these are
    harmonized to it. The per-analyte listing format the example demonstrated is
    already stated in Column B: "List in the same order as the Analyte field."

Scope of change
---------------
Column F only. No field name, description, tier, data type, comment, mode flag,
or literature assessment value is touched.

Version policy
--------------
No version bump and no Last Update change, matching the two earlier patches of
2026-08-07. Adding the standard absence options restores conformance to an
existing rule rather than changing what any field means.
"""

from __future__ import annotations

import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COL_EXAMPLE = 5
SUFFIX = " | Other: specify | N/A | None"

# (relative path, field name, mode, payload)
#   "append"  -> payload is appended to the existing Column F value
#   "replace" -> payload replaces it entirely
EDITS = [
    ("EPMA/EPMA_TAPP_v9.csv", "EDS Acquisition Mode", "append", SUFFIX),
    ("SEM/SEM_TAPP_v6.csv", "Beam Mode", "append", SUFFIX),
    ("SEM/SEM_TAPP_v6.csv", "Stage Scan vs. Beam Scan", "append", SUFFIX),
    ("SEM/SEM_TAPP_v6.csv", "Technique per Analyte", "replace",
     "WDS | EDS | Other: specify | N/A | None"),
    ("SEM/SEM_Composition_TAPP_v6.csv", "Beam Mode", "append", SUFFIX),
    ("SEM/SEM_Composition_TAPP_v6.csv", "Stage Scan vs. Beam Scan", "append", SUFFIX),
    ("SEM/SEM_Composition_TAPP_v6.csv", "Technique per Analyte", "replace",
     "WDS | EDS | Other: specify | N/A | None"),
]


def main():
    dry_run = "--dry-run" in sys.argv

    by_file = {}
    for rel, field, mode, payload in EDITS:
        by_file.setdefault(rel, []).append((field, mode, payload))

    total = 0
    for rel, edits in by_file.items():
        path = os.path.join(ROOT, rel)
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))

        applied = []
        for field, mode, payload in edits:
            hits = [(n, r) for n, r in enumerate(rows[1:], start=2)
                    if r and r[0].strip() == field]
            if len(hits) != 1:
                print(f"  !! {rel}: expected exactly 1 row named {field!r}, found {len(hits)}")
                return 2
            n, row = hits[0]
            old = row[COL_EXAMPLE]
            new = (old + payload) if mode == "append" else payload
            if "Other: specify" in old:
                print(f"  -- {rel} r{n} {field}: already compliant, skipped")
                continue
            row[COL_EXAMPLE] = new
            applied.append((n, field, mode, old, new))

        if applied and not dry_run:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)

        if applied:
            print(f"\n{rel}  —  {len(applied)} field(s)")
            for n, field, mode, old, new in applied:
                print(f"    row {n:>4}  {field}  [{mode}]")
                print(f"        before: {old}")
                print(f"        after:  {new}")
            total += len(applied)

    verb = "would be" if dry_run else ""
    print(f"\n{'=' * 78}")
    print(f"{total} Column F value(s) {verb} updated.")
    if dry_run:
        print("Dry run — nothing written.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
