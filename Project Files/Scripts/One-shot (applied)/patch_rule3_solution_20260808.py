#!/usr/bin/env python3
"""
patch_rule3_solution_20260808.py

Adds the mandatory `Analytical Mode` field (Rule 3) to the three Solution ICP-MS TAPPs,
which have never carried it.

Rule 3 requires the field in every TAPP "regardless of whether the technique has one mode
or many", explicitly including single-mode techniques, "so that procedure records are
self-describing and consistent across the TAPP library". These three were the only
outstanding violations in the library.

Placement and tiers are fixed by the rule: first field in Group 4, C=Basic, D=Read-Only,
Controlled list, Y for all modes.

Allowed values
--------------
Phase 0 for all three defined no mode flag columns, so there is no column-label list for
the allowed values to mirror. The single mode is the introduction geometry that defines
the technique, with flow injection offered because it is a genuine alternative to
continuous nebulisation on the same instrument:

    Solution nebulisation (continuous) | Flow injection

`Analytical Mode` is exempt from the `N/A | None | Other: specify` requirement (see the
exemption table in the Data Type Vocabulary section of conventions.md), so those are not
added.

Version policy
--------------
No version bump, consistent with the other patches of 2026-08-07/08. Adding a field is
normally an integer bump, but these TAPPs are tracked against composed modules in
composed_tapps.json and a bump here would desynchronise that record for no gain.
"""

from __future__ import annotations

import csv
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()

TARGETS = [
    "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v7.csv",
    "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v7.csv",
    "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v5.csv",
]

NAME = "Analytical Mode"
DESC = ("Top-level declaration of the kind of measurement this procedure covers. Solution ICP-MS "
        "has a single routine mode — continuous nebulisation of a digested solution — so this TAPP "
        "defines no mode flag columns; the field is still required (Rule 3) so that a procedure "
        "record is self-describing and comparable with multi-mode TAPPs across the library.")
TIER_C, TIER_D, DTYPE = "Basic", "Read-Only", "Controlled list"
EXAMPLE = "Solution nebulisation (continuous) | Flow injection"


def main():
    dry = "--dry-run" in sys.argv
    total = 0

    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        width = len(rows[0])

        if any(r and r[0].strip() == NAME for r in rows):
            print(f"  -- {rel}: already present, skipped")
            continue

        g4 = next((i for i, r in enumerate(rows) if r and re.match(r"^4\.\s", r[0].strip())), None)
        if g4 is None:
            print(f"  !! {rel}: Group 4 header not found")
            return 2

        row = [""] * width
        row[0], row[1], row[2], row[3], row[4], row[5], row[7] = \
            NAME, DESC, TIER_C, TIER_D, DTYPE, EXAMPLE, TODAY
        rows.insert(g4 + 1, row)

        if not dry:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)
        total += 1
        print(f"  {rel}")
        print(f"      inserted at row {g4 + 2} as first field in Group 4  "
              f"(C={TIER_C}, D={TIER_D}, {DTYPE})")

    verb = "would be" if dry else ""
    print(f"\n{'=' * 76}")
    print(f"  Analytical Mode {verb} added to {total} TAPP(s).")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
