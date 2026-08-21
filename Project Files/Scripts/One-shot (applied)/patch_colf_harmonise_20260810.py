#!/usr/bin/env python3
"""
Harmonise the 5 drifting Column F values across the three Solution ICP-MS TAPPs.

These five were classified as drift because their content does not depend on the
mass analyser: digestion vessels and acids do not know what detector sits
downstream, and a rinse time is a memory-effect property, not a detector one.

A NAIVE UNION WAS WRONG ON THREE OF THE FIVE, and the failures are instructive —
each comes from treating Column F as a uniform list when the field's Data Type
says otherwise:

  * `Desolvation System` — the union preserved BOTH spellings, `Apex IR` and
    `Apex-IR`, faithfully reproducing the drift it was meant to remove. The list
    was internally inconsistent anyway (`ApexQ`, `Apex IR`, `Apex-HF`), so all
    three are normalised to the `Apex Q | Apex IR | Apex HF` pattern.

  * `Nebulizer Gas Flow Rate` — Data Type is `Numeric (L/min)`, so Column F holds
    an example RANGE, not allowed values. The union produced the meaningless
    `0.8-1.1 L/min | 0.8-1.0 L/min | 0.85-1.05 L/min`. Replaced with the single
    encompassing range.

  * `Digestion Vessel Type` / `Digestion Acid(s)` — union content was right but
    appended new options at the end. Reordered so related entries sit together
    (`TFE/TFM bomb` beside `Parr bomb`), which is what a reader scans for.

FLAGGED, NOT FIXED: `Digestion Acid(s)` has Data Type `Text (free)` while
`Digestion Vessel Type` — structurally identical, a pipe-delimited option list
ending in `N/A | None | Other: specify` — is `Controlled list`. One of the two is
mistyped. Column E is MODULE-owned, so this cannot be repaired here; it belongs
with the module reconciliation.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
TODAY = "2026-08-10"
COL_ITEM, COL_EXAMPLE, COL_UPDATE = 0, 5, 7

TARGETS = [
    ROOT / "Solution Q-ICP-MS" / "Solution_Q-ICP-MS_TAPP_v7.csv",
    ROOT / "Solution SF-ICP-MS" / "Solution_SF-ICP-MS_TAPP_v7.csv",
    ROOT / "Solution MC-ICP-MS" / "Solution_MC-ICP-MS_TAPP_v5.csv",
]

HARMONISED = {
    "Digestion Vessel Type":
        "Savillex beaker | Parr bomb | TFE/TFM bomb | Carius tube | HPA-S | "
        "Open beaker | N/A | None | Other: specify",
    "Digestion Acid(s)":
        "HF–HNO3 | HF–HNO3–HClO4 | HNO3–HCl | HNO3 only | Aqua regia | "
        "N/A | None | Other: specify",
    "Desolvation System":
        "Aridus I | Aridus II | Apex Q | Apex IR | Apex HF | "
        "None | N/A | Other: specify",
    "Nebulizer Gas Flow Rate":
        "0.8–1.1 L/min",
    "Wash Time Between Samples":
        "120 | 180 | 210 | 300",
}


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — harmonise 5 Column F values\n")
    total = 0
    for p in TARGETS:
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        changed = []
        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            name = r[COL_ITEM].strip()
            if name not in HARMONISED:
                continue
            while len(r) <= COL_UPDATE:
                r.append("")
            if r[COL_EXAMPLE].strip() == HARMONISED[name]:
                continue
            before = r[COL_EXAMPLE] or "(EMPTY)"
            r[COL_EXAMPLE] = HARMONISED[name]
            r[COL_UPDATE] = TODAY
            changed.append((name, before))
        if APPLY and changed:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        print(f"  {p.name}  ({len(changed)} changed)")
        for name, before in changed:
            print(f"      {name}")
            print(f"         was: {before[:96]}")
            print(f"         now: {HARMONISED[name][:96]}")
        total += len(changed)
        print()
    print(f"cells changed: {total}")
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
