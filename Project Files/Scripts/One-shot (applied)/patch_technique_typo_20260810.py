#!/usr/bin/env python3
"""
`Others: specify` -> `Other: specify` in Column F of the `Technique` field.

conventions.md fixes the token as `Other: specify` (singular) throughout. Three
TAPPs carry the plural form. This is a genuine typo and wrong under any reading
of the rule.

It does NOT by itself clear the `controlled-list-options` finding on `Technique`,
which also reports `N/A` and `None` as missing. Whether those two belong on
`Technique` at all is a separate, open question — every procedure has a
technique, so they are arguably semantically empty, which is the reasoning that
put `Analytical Mode` in the closed exemption table. Not decided here.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv

TARGETS = [
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v5.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_UPb_TAPP_v5.csv",
    ROOT / "XCT" / "Lab-XCT_TAPP_v10.csv",
]

OLD, NEW = "Others: specify", "Other: specify"
COL_EXAMPLE = 5


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — Technique Column F typo\n")
    total = 0
    for p in TARGETS:
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        hit = 0
        for r in rows[1:]:
            if not r or r[0].strip() != "Technique":
                continue
            if len(r) > COL_EXAMPLE and OLD in r[COL_EXAMPLE]:
                print(f"  {p.relative_to(ROOT)}")
                print(f"      before: {r[COL_EXAMPLE]}")
                r[COL_EXAMPLE] = r[COL_EXAMPLE].replace(OLD, NEW)
                print(f"      after : {r[COL_EXAMPLE]}")
                hit += 1
        if APPLY and hit:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        total += hit
    print(f"\ncells changed: {total}")
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
