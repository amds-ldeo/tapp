#!/usr/bin/env python3
"""
The 12 remaining mechanical findings.

(1) datatype-invalid, 5 rows, TEM only.
    All five resolve to `Text (free)`, which is not a guess — it is what every
    other TAPP in the library already uses for the same kinds of field.
    `Analyte` is `Text (free)` in EPMA, SEM, LA-Q/SF, Solution Q and Solution
    SF; `Acquisition Software` and `Data Reduction Software` are `Text (free)`
    in all five. The two "range" fields hold values like
    '0-20 keV (2048 channels)', which is a range plus a channel count, not a
    number, so `Numeric (unit)` would be wrong.

    Note `Text (free)` also avoids manufacturing new findings: typing the
    software field as `Controlled list` would immediately require
    `N/A | None | Other: specify` in Column F.

(2) name-element-specific, 4 rows. Column B of
    `Isobaric Interference Corrections Applied` reads "Element-specific detail
    …". Replaced with "Analyte-specific" per the technique-agnostic naming rule.

    Scope note: the same string also occurs in a LITERATURE ASSESSMENT column
    ("applied element-specifically") in LA-Q/SF v5. That is verbatim extraction
    describing what a paper did, and is deliberately left alone — the linter
    checks only columns B and F for this reason.

(3) name-level-encoding, 2 rows. `Target Foil Thickness` -> `Foil Thickness`.
    Only 'Target Material' and 'Target Feature(s)' are exempt from the
    level-neutral naming rule; the tier columns already encode whether a value
    is a procedure target or an analysis-level measurement. No collision: no
    other TAPP defines a `Foil Thickness` field.

(4) description-source-leak, 1 row. See the docstring note below — this one is
    a FALSE POSITIVE and is handled by rewording, not by accepting the premise.

Every touched row gets Last Update = 2026-08-10, since all four are substantive
edits to the row under the definition in Version and Date Tracking.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
TODAY = "2026-08-10"
COL_ITEM, COL_DESC, COL_TYPE, COL_EXAMPLE, COL_UPDATE = 0, 1, 4, 5, 7

TEM_TYPES = {
    "SAED Pattern Simulation Software": "Text (free)",
    "EDS Energy Range": "Text (free)",
    "Analyte": "Text (free)",
    "EELS Edges": "Text (free)",
    "EELS Energy Loss Range": "Text (free)",
}

ELEM_FILES = [
    "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v2.csv",
    "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v1.csv",
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv",
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_UPb_TAPP_v5.csv",
]

RENAME_FILES = ["SEM/SEM_TAPP_v6.csv", "SEM/SEM_FIBSEM_TAPP_v6.csv"]

# The linter matched `in the source(?:\s+\w+)?` against "as stated in the source
# and add a parenthetical note". That regex is aimed at commentary describing
# what a source DOCUMENT contains — the Horstwood Table 3 pattern. Here "the
# source" means the publication being catalogued and the sentence is an
# INSTRUCTION to whoever fills the field, which is legitimate description
# content. Rather than delete real guidance to satisfy a heuristic, the sentence
# is reworded to say the same thing without the trigger phrase.
XCT_OLD = "Record the value as stated in the source and add a parenthetical note if the unit used is keV."
XCT_NEW = "Record the value as originally reported, and add a parenthetical note if the unit used is keV."


def load(rel):
    p = ROOT / rel
    rows = list(csv.reader(open(p, encoding="utf-8-sig")))
    return p, rows[0], rows[1:]


def save(p, hdr, body):
    if APPLY:
        with open(p, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows([hdr] + body)


def stamp(r):
    while len(r) <= COL_UPDATE:
        r.append("")
    r[COL_UPDATE] = TODAY


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — 12 mechanical findings\n")
    total = 0

    print("(1) TEM data types")
    p, hdr, body = load("TEM/TEM_TAPP_v9.csv")
    n = 0
    for r in body:
        name = r[COL_ITEM].strip() if r else ""
        if name in TEM_TYPES and r[COL_TYPE] != TEM_TYPES[name]:
            print(f"    {name:34s} {r[COL_TYPE]!r} -> {TEM_TYPES[name]!r}")
            r[COL_TYPE] = TEM_TYPES[name]
            stamp(r)
            n += 1
    save(p, hdr, body)
    print(f"    rows changed: {n}\n")
    total += n

    print("(2) Element-specific -> Analyte-specific (Column B)")
    n = 0
    for rel in ELEM_FILES:
        p, hdr, body = load(rel)
        hit = 0
        for r in body:
            if len(r) > COL_DESC and "element-specific" in r[COL_DESC].lower():
                r[COL_DESC] = (r[COL_DESC].replace("Element-specific", "Analyte-specific")
                                          .replace("Element-Specific", "Analyte-Specific"))
                stamp(r)
                hit += 1
        if hit:
            print(f"    {rel.split('/')[-1]:34s} {hit} row(s)")
        save(p, hdr, body)
        n += hit
    print(f"    rows changed: {n}\n")
    total += n

    print("(3) Target Foil Thickness -> Foil Thickness")
    n = 0
    for rel in RENAME_FILES:
        p, hdr, body = load(rel)
        hit = 0
        for r in body:
            if r and r[COL_ITEM].strip() == "Target Foil Thickness":
                r[COL_ITEM] = "Foil Thickness"
                stamp(r)
                hit += 1
        if hit:
            print(f"    {rel.split('/')[-1]:34s} {hit} row(s)")
        save(p, hdr, body)
        n += hit
    print(f"    rows changed: {n}\n")
    total += n

    print("(4) Lab-XCT Accelerating Voltage — reworded (linter false positive)")
    p, hdr, body = load("XCT/Lab-XCT_TAPP_v10.csv")
    n = 0
    for r in body:
        if r and r[COL_ITEM].strip() == "Accelerating Voltage" and XCT_OLD in r[COL_DESC]:
            r[COL_DESC] = r[COL_DESC].replace(XCT_OLD, XCT_NEW)
            stamp(r)
            n += 1
            print(f"    before: …{XCT_OLD}")
            print(f"    after : …{XCT_NEW}")
    save(p, hdr, body)
    print(f"    rows changed: {n}\n")
    total += n

    print(f"total rows changed: {total}")
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
