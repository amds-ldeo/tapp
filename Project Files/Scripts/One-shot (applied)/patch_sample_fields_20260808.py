#!/usr/bin/env python3
"""
patch_sample_fields_20260808.py

Two Group 2 changes arising from the Rule 1 naming review.

1. Add `Sample Name` to the three Solution ICP-MS TAPPs
---------------------------------------------------------
Those three hold `Sample Description` ("brief description of sample provenance, form, or
preparation state") and `Sample Persistent Identifier`, but have no field for the sample's
working name — the identifier used in the lab and in the resulting publication. The other
14 TAPPs all carry it. This was mistaken for a naming violation until the descriptions were
read; it is a missing field.

Tiers C=N/A, D=Basic, matching all 14 TAPPs that have it without exception. Description is
the majority text (7 of 14). Placed before Sample Persistent Identifier so Group 2 reads
name, then identifier, then description.

2. Set `Sample Persistent Identifier` to C=Advanced everywhere
--------------------------------------------------------------
The field was split C=N/A/D=Advanced in 14 TAPPs against C=Advanced/D=Basic in the three
Solution TAPPs — a divergence that only became visible once `Sample IGSN` was renamed to
match. Resolved to C=Advanced, so a procedure may declare that it expects samples to carry
a persistent identifier, which is a meaningful standing commitment for Astromat, EarthChem
and SESAR.

The analysis-level tier is NOT changed here and remains split: D=Advanced in 14, D=Basic in
3. Only the procedure-level tier was decided. The linter will continue to report the D-tier
split as tier-divergence, which is the correct state — a known, visible, undecided item
rather than a hidden one.

Version policy
--------------
No version bump, consistent with the other patches of 2026-08-07/08.
"""

from __future__ import annotations

import csv
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()

SOLUTION = [
    "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v7.csv",
    "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v7.csv",
    "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v5.csv",
]

NAME = "Sample Name"
ANCHOR = "Sample Persistent Identifier"
DESC = ("Name or identifier of the sample analysed, as used in the laboratory. Should match the "
        "identifier used in associated publications or data tables.")
EXAMPLE = "e.g., 'Allende MS-1 digest A' | 'NWA 8657 aliquot 2' | 'BHVO-2 replicate 3'"


def find_tapps(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {"unpacked_tapp", "Pre-VIM3 Reference Archive (2026-07-24)"}
                       and not d.startswith(".")]
        for fn in filenames:
            if re.search(r"_TAPP_v\d+(\.\d+)?\.csv$", fn):
                key = fn.rsplit("_v", 1)[0]
                ver = float(re.search(r"_v(\d+(?:\.\d+)?)\.csv$", fn).group(1))
                if key not in out or ver > out[key][0]:
                    out[key] = (ver, os.path.join(dirpath, fn))
    return [v[1] for v in sorted(out.values(), key=lambda x: x[1])]


def main():
    dry = "--dry-run" in sys.argv
    added = tiered = 0

    print("1. add Sample Name to the Solution TAPPs")
    for rel in SOLUTION:
        path = os.path.join(ROOT, rel)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        if any(r and r[0].strip() == NAME for r in rows):
            print(f"   -- {rel}: already present")
            continue
        at = next((i for i, r in enumerate(rows) if r and r[0].strip() == ANCHOR), None)
        if at is None:
            print(f"   !! {rel}: anchor {ANCHOR!r} not found")
            return 2
        row = [""] * len(rows[0])
        row[0], row[1], row[2], row[3], row[4], row[5], row[7] = \
            NAME, DESC, "N/A", "Basic", "Text (free)", EXAMPLE, TODAY
        rows.insert(at, row)
        if not dry:
            csv.writer(open(path, "w", newline="", encoding="utf-8-sig")).writerows(rows)
        added += 1
        print(f"   {rel}: inserted at row {at + 1}, before {ANCHOR}")

    print("\n2. Sample Persistent Identifier -> C=Advanced")
    for path in find_tapps(ROOT):
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        hit = False
        for r in rows[1:]:
            if r and r[0].strip() == ANCHOR and r[2].strip() != "Advanced":
                print(f"   {os.path.relpath(path, ROOT):<52} C={r[2]} -> Advanced   (D={r[3]}, unchanged)")
                r[2] = "Advanced"
                hit = True
        if hit and not dry:
            csv.writer(open(path, "w", newline="", encoding="utf-8-sig")).writerows(rows)
        tiered += hit

    verb = "would be" if dry else ""
    print(f"\n{'=' * 84}")
    print(f"  Sample Name {verb} added to {added} TAPP(s); "
          f"C=Advanced {verb} set in {tiered} TAPP(s).")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
