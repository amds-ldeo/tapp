#!/usr/bin/env python3
"""
patch_datatype_synonyms_20260807.py

Normalizes drifted Data Type (Column E) labels to the canonical vocabulary in
references/conventions.md.

Background
----------
Four spellings in use across the library are synonyms of types that already
exist in the Data Type Vocabulary. Each substitution below leaves the meaning of
the field unchanged — only the label is normalized.

    'Free text'                     -> 'Text (free)'                  19 rows
    'Controlled vocabulary'         -> 'Controlled list'              13 rows
    'URI'                           -> 'URI / DOI'                     3 rows
    'Controlled vocabulary (list)'  -> 'Controlled list'               2 rows
                                                                     --------
                                                                     37 rows

Why each target is correct
--------------------------
'Text (free)'      The Data Type Vocabulary lists "Text (free)"; "Free text" does
                   not appear. All 19 affected fields are genuine narrative fields
                   (Torch Depth, Drift Correction, Beam Damage Minimization, ...).

'Controlled list'  The vocabulary lists "Controlled list"; "Controlled vocabulary"
                   does not appear. All 13 affected fields carry pipe-separated
                   allowed values in Column F. Rule 3 previously mandated
                   "Controlled vocabulary" for Analytical Mode — that was a defect
                   in conventions.md, corrected the same day as this patch.

'URI / DOI'        Template TAPP Group 1.csv specifies 'URI / DOI' for Laboratory
                   ID and 11 of 14 TAPPs already comply. Conventions define
                   'URI / DOI' as "a persistent identifier, URL, or DOI", which
                   covers the ROR IDs these fields hold. Rule 1 fix.

'Controlled list'  SEM's "Technique per Analyte" is the Rule 2 counterpart of
 (from '(list)')   EPMA's "EPMA Technique per Analyte", which uses 'Controlled
                   list' in all 8 EPMA versions. Harmonization fix.

Scope of change
---------------
Column E only. No field name, description, tier, example, comment, mode flag, or
literature assessment value is touched.

Version policy
--------------
No version bump and no Last Update change, matching the same-day sentinel patch.
Every substitution is a label normalization with identical semantics: nothing
about what a field accepts changes, so neither the integer-bump rule (structural
revision) nor the decimal-bump rule (description or example change) applies.
"""

from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COL_TYPE = 4

# lowercase source label -> canonical label
SYNONYMS = {
    "free text": "Text (free)",
    "controlled vocabulary": "Controlled list",
    "controlled vocabulary (list)": "Controlled list",
    "uri": "URI / DOI",
}


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

    changed = []
    for n, row in enumerate(rows[1:], start=2):
        if len(row) <= COL_TYPE:
            continue
        item = row[0].strip()
        if not item or re.match(r"^\d+\.\s", item):
            continue
        old = row[COL_TYPE].strip()
        new = SYNONYMS.get(old.lower())
        if new and new != old:
            changed.append((n, item, old, new))
            row[COL_TYPE] = new

    if changed and not dry_run:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
    return changed


def main():
    dry_run = "--dry-run" in sys.argv
    total, files = 0, 0
    tally = {}

    for path in find_tapps(ROOT):
        changed = patch(path, dry_run=dry_run)
        if not changed:
            continue
        files += 1
        total += len(changed)
        print(f"\n{os.path.relpath(path, ROOT)}  —  {len(changed)} row(s)")
        for n, item, old, new in changed:
            tally[(old, new)] = tally.get((old, new), 0) + 1
            print(f"    row {n:>4}  {item[:40]:<40}  {old!r} -> {new!r}")

    print(f"\n{'=' * 78}")
    for (old, new), n in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {n:>3}  {old!r:<32} -> {new!r}")
    verb = "would be" if dry_run else ""
    print(f"\n{total} Data Type cell(s) {verb} normalized across {files} file(s).")
    if dry_run:
        print("Dry run — nothing written.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
