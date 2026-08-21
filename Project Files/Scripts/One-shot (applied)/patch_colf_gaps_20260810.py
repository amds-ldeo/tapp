#!/usr/bin/env python3
"""
Fill the 5 Column F cells that were empty in all three Solution ICP-MS TAPPs.

Rule 6.4: "A module row is not complete until its consumer supplies Column F."
These five had no example content in any consumer.

None of the five is a `Controlled list` — they are `Numeric (unit)` or
`Text (free)` — so Column F holds an ILLUSTRATIVE EXAMPLE, not an enumeration of
allowed values, and no controlled vocabulary needs sourcing.

    Sample Aliquot Mass or Volume   Numeric (mg or mL)
    Digestion Temperature           Numeric (°C)
    Digestion Duration              Text (free)
    Sample Uptake Rate              Numeric (µL/min or mL/min)
    Internal Standard Concentration Numeric (µg/L)

Values below are typical working ranges for solution ICP-MS of geological and
extraterrestrial material, written to show the SHAPE of an acceptable answer and
to convey the parameter's practical span. They are illustrative, not normative,
and are not drawn from a specific reference — a lab should record its own.

Each example is annotated with the condition that selects it (hotplate vs Parr
bomb, self-aspirating vs peristaltic), because the useful information in an
example of a range is *what makes it that value*.

The same values are applied to all three TAPPs: every one of these parameters
belongs to the digestion or introduction chain, which is upstream of the mass
analyser and does not vary with it. `Sample Uptake Rate` is the closest call —
MC commonly self-aspirates at low flow — so its example spans that case
explicitly rather than being split three ways.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
TODAY = "2026-08-10"
COL_ITEM, COL_TYPE, COL_EXAMPLE, COL_UPDATE = 0, 4, 5, 7

TARGETS = [
    ROOT / "Solution Q-ICP-MS" / "Solution_Q-ICP-MS_TAPP_v7.csv",
    ROOT / "Solution SF-ICP-MS" / "Solution_SF-ICP-MS_TAPP_v7.csv",
    ROOT / "Solution MC-ICP-MS" / "Solution_MC-ICP-MS_TAPP_v5.csv",
]

GAPS = {
    "Sample Aliquot Mass or Volume":
        "e.g., '50 mg (whole-rock silicate)' | '25 mg (mass-limited meteorite)' | "
        "'100 mg (low-abundance trace elements)' | '1–5 mL (aqueous sample)'",
    "Digestion Temperature":
        "e.g., '90–120 °C (hotplate, Savillex beaker)' | "
        "'150–190 °C (Parr bomb, refractory phases)' | '220 °C (HPA-S)'",
    "Digestion Duration":
        "e.g., '12 h' | '24 h' | '48 h (refractory accessory phases)' | "
        "'3 days (multi-step with intermediate dry-down)'",
    "Sample Uptake Rate":
        "e.g., '50–100 µL/min (self-aspirating PFA nebulizer)' | "
        "'200–400 µL/min (micro-flow, peristaltic)' | '1 mL/min (conventional concentric)'",
    "Internal Standard Concentration":
        "e.g., '5 µg/L In' | '10 µg/L Rh' | '1–10 µg/L (In, Rh, Re multi-element)' | "
        "'20 µg/L (high-dilution runs)'",
}


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — fill 5 empty Column F cells\n")
    total = 0
    for p in TARGETS:
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        changed = []
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip():
                continue
            name = r[COL_ITEM].strip()
            if name not in GAPS:
                continue
            while len(r) <= COL_UPDATE:
                r.append("")
            if r[COL_EXAMPLE].strip():
                print(f"    SKIP {name} — already populated: {r[COL_EXAMPLE][:50]}")
                continue
            r[COL_EXAMPLE] = GAPS[name]
            r[COL_UPDATE] = TODAY
            changed.append((name, r[COL_TYPE]))
        if APPLY and changed:
            with open(p, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        print(f"  {p.name}  ({len(changed)} filled)")
        for name, dtype in changed:
            print(f"      {name}  [{dtype}]")
            print(f"         {GAPS[name][:104]}")
        total += len(changed)
        print()
    print(f"cells filled: {total}")
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
