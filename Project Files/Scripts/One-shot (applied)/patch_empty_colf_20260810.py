#!/usr/bin/env python3
"""
Fill the 5 `Controlled list` fields whose Column F is entirely empty.

A Controlled list field with no Column F has no allowed values at all — the
Data Type promises a closed vocabulary and none is given. That is a defect, not
a missing convention token, and it is why these 5 are worth more care than the
39 findings that are merely missing `N/A | None | Other: specify`.

Column F is consumer-owned (modules own A–E), so these are edited in the TAPP
and not in the module.

--- Mass Fractionation Law (LA-MC-ICPMS v2, LA-MC-ICPMS_UPb v1) ---

Both consume Module_MCICPMS, as does Solution MC-ICP-MS v5, which already
carries a complete list. Copied verbatim rather than reinvented — same field,
same module, sibling consumers, Rule 4 consistency. Data Type is a plain
`Controlled list`, so `Other: specify` is required here.

--- Coupled Technique(s) (Solution Q v7, SF v7, MC v5) ---

Data Type is `Controlled list / Text`, a compound: conventions require `N/A |
None` but NOT `Other: specify`, because the `/ Text` component already permits
an unlisted answer.

Values are technique names, per the field's own description ("Use the same
controlled vocabulary as the Technique field"), and are technique-appropriate
rather than a single generic list:

  * Q and SF measure concentrations in digested aliquots. Characteristic
    couplings are isotope-ratio work on the same digestion (MC-ICP-MS, TIMS),
    in-situ comparison (LA-ICP-MS), major elements (EPMA), and Noble Gas MS —
    the last being the (U-Th)/He case conventions.md itself cites as the
    example of a computationally mandatory coupling.
  * MC measures ratios, and its characteristic coupling runs the other way:
    Q or SF first, to determine concentration before spiking and dilution.

These are Column F example/allowed content and are a reasonable starting
vocabulary, not a closed community standard — worth a domain review.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
COL_TYPE, COL_EXAMPLE = 4, 5

MFL = "Exponential | Linear | Power | N/A | None | Other: specify"

EDITS = [
    ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v2.csv", "Mass Fractionation Law", MFL),
    ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v1.csv", "Mass Fractionation Law", MFL),
    ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v7.csv", "Coupled Technique(s)",
     "Solution MC-ICP-MS | TIMS | LA-ICP-MS | EPMA | Noble Gas MS | INAA | None | N/A"),
    ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v7.csv", "Coupled Technique(s)",
     "Solution MC-ICP-MS | TIMS | LA-ICP-MS | EPMA | Noble Gas MS | INAA | None | N/A"),
    ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v5.csv", "Coupled Technique(s)",
     "Solution Q-ICP-MS | Solution SF-ICP-MS | TIMS | LA-MC-ICP-MS | None | N/A"),
]


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — fill empty Column F on Controlled list fields\n")
    done = 0
    for rel, field, value in EDITS:
        p = ROOT / rel
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        touched = False
        for r in rows[1:]:
            if not r or r[0].strip() != field:
                continue
            while len(r) <= COL_EXAMPLE:
                r.append("")
            if r[COL_EXAMPLE].strip():
                print(f"  SKIP {rel} :: {field} — Column F already populated: "
                      f"{r[COL_EXAMPLE][:60]}")
                continue
            print(f"  {rel}")
            print(f"      field : {field}")
            print(f"      type  : {r[COL_TYPE]}")
            print(f"      set F : {value}")
            r[COL_EXAMPLE] = value
            touched = True
            done += 1
        if APPLY and touched:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        print()
    print(f"cells filled: {done}")
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
