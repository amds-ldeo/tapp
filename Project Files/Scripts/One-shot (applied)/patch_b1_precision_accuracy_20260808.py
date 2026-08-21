#!/usr/bin/env python3
"""
patch_b1_precision_accuracy_20260808.py

Promotes two Group 6 fields to C=Basic in LA-Q/SF-ICP-MS, ahead of composing the
Geochronology and U-Pb modules into it.

    Within-Session Analytical Precision and Assessment Method   C=Advanced -> Basic
    Analytical Accuracy and Assessment Method                   C=Advanced -> Basic

Why
---
Test 4 triaged the 26 tier differences between the LA-ICP-MS Geochronology TAPP and
LA-Q/SF-ICP-MS: 21 were drift, 1 was a bug on the LA-Q/SF side, and 4 were principled.
Of those 4, only these two are genuinely geochronology-exclusive — the other two
(Ablation Cell Type, Laser Pulse Duration) are good ideas that should propagate on
their own merits.

All six geochronology reporting standards surveyed place precision and accuracy in
their required tier: Condon et al. 2024, Schaen et al. 2021, Rooney et al. 2024,
Flowers et al. 2024, Kohn et al. 2024, Mahan et al. 2023. Both geochronology TAPPs
already carry C=Basic; LA-Q/SF-ICP-MS carries C=Advanced. Composing geochronology
into LA-Q/SF without promoting them would silently drop the one requirement those six
communities agree on.

Scope
-----
Column C only, two rows, one file. Analysis-level tier (D=Basic) is unchanged, as are
descriptions, examples, mode flags and literature assessment columns.

Both fields are in Group 6, which is not composed — only Group 1 is a build output —
so editing them directly is correct and will not be overwritten by recomposition.

Version policy
--------------
No version bump, consistent with the other patches of 2026-08-07/08. The change makes
an existing field mandatory rather than altering what it means.

Not done here
-------------
LA-ICPMS_TAPP_v13 (the stale, frozen branch) and the three Solution ICP-MS TAPPs also
carry C=Advanced. They are left alone: the geochronology merge concerns LA-Q/SF-ICP-MS,
and whether solution work should mandate precision and accuracy is a separate question
with no reporting standard behind it yet.
"""

from __future__ import annotations

import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "LA-Q:SF-ICP-MS", "LA-Q:SF-ICPMS_TAPP_v5.csv")
COL_ITEM, COL_C, COL_D = 0, 2, 3

FIELDS = {
    "Within-Session Analytical Precision and Assessment Method": "Basic",
    "Analytical Accuracy and Assessment Method": "Basic",
}


def main():
    dry = "--dry-run" in sys.argv
    with open(TARGET, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    edits = []
    for n, row in enumerate(rows[1:], start=2):
        name = row[COL_ITEM].strip() if row else ""
        if name in FIELDS:
            want = FIELDS[name]
            if row[COL_C].strip() == want:
                print(f"  -- row {n}: {name} already C={want}, skipped")
                continue
            edits.append((n, name, row[COL_C], want, row[COL_D]))
            row[COL_C] = want

    if len(edits) != len(FIELDS):
        found = {e[1] for e in edits}
        missing = set(FIELDS) - found
        if missing:
            print(f"  !! field(s) not found or already correct: {sorted(missing)}")

    if edits and not dry:
        with open(TARGET, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

    print(f"\n{os.path.relpath(TARGET, ROOT)}")
    for n, name, old, new, d in edits:
        print(f"    row {n:>4}  {name}")
        print(f"           C: {old} -> {new}   (D={d}, unchanged)")

    verb = "would be" if dry else ""
    print(f"\n{'=' * 76}")
    print(f"  {len(edits)} tier cell(s) {verb} promoted to C=Basic.")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
