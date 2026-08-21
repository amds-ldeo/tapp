#!/usr/bin/env python3
"""
patch_rule1_names_20260808.py

Harmonises field names that Rule 1 requires to be identical across TAPPs.

Eight candidate violations were surfaced while extracting Module_SolutionIntroduction.
Reading the descriptions rather than matching the names reduced that to five. The three
rejected candidates are recorded below, because "these two fields have similar names" is
not evidence that they are the same field — that was the error that produced the list.

APPLIED — five renames, verified same concept
---------------------------------------------
    Blank/Background Correction Method        -> Blank / Background Correction Method
    Normalization/Standards-Based Correction  -> Normalization / Standards-Based Correction
    Spike/Outlier Filtering Approach          -> Spike / Outlier Filtering Approach
        The first three are whitespace only. The spaced form is the majority in every case
        (5 vs 3, 8 vs 5, 7 vs 3) and matches the space-pipe-space convention used elsewhere.

    Sample IGSN                               -> Sample Persistent Identifier
        Same concept, both URI / IGSN. The canonical name is technique-agnostic and does not
        presuppose that the identifier is an IGSN; it is in 14 TAPPs against 3.

    Sample Sequence Design                    -> Analysis Sequence
        Same concept — measurement order of samples, blanks and standards within a session.
        7 TAPPs against 3.

REJECTED — similar names, different fields
------------------------------------------
    Sample Description  vs  Sample Name
        NOT the same. "Brief description of sample provenance, form, or preparation state"
        versus "Name or identifier of the sample as used in the laboratory". The Solution
        TAPPs hold Sample Description and have no Sample Name at all — so this is a MISSING
        FIELD in three TAPPs, not a naming violation. Sample Description is itself a field
        the other 14 TAPPs lack, and may be worth propagating the other way.

    Make-up Gas Flow Rate  vs  Plasma / Make-up Gas Addition
        NOT the same. The solution field is argon added downstream of a DESOLVATION SYSTEM;
        the LA field is gas mixed into the carrier stream downstream of the ABLATION CELL.
        Different positions in different introduction systems. Both correct where they are.

    Blank Correction (EPMA, SEM)  vs  Blank / Background Correction Method
        NOT merged. EPMA's concerns blank standards and carbon-coat contribution to the C
        signal; the LA/solution field concerns gas or instrument background. Related in role,
        different in substance, and differently tiered. Left alone pending a decision.

DEFERRED — structural, not naming
---------------------------------
    Instrument identity is divergent in STRUCTURE, not just name: six TAPPs split it into
    "Instrument Manufacturer" + "Instrument Model", seven combine it as
    "ICP-MS Manufacturer & Model", three as "Instrument Make and Model", one as
    "CT System Manufacturer and Model". Merging one field into two, or vice versa, is a
    structural change across the library and is out of scope for a rename.

Note on tiers
-------------
Renaming does not align tiers, and two of these pairs are differently tiered
(Sample Persistent Identifier: C=N/A/D=Advanced in 14 TAPPs vs C=Advanced/D=Basic in the
three Solution TAPPs; Analysis Sequence: D=Editable vs D=Read-Only). That is deliberate.
Renaming converts a HIDDEN inconsistency — the same field under two names, which no check
could see — into a VISIBLE one that validate_tapp.py reports as tier-divergence. Aligning
the tiers is a separate decision on separate evidence.

Version policy
--------------
No version bump, consistent with the other patches of 2026-08-07/08.
"""

from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

RENAMES = {
    "Blank/Background Correction Method": "Blank / Background Correction Method",
    "Normalization/Standards-Based Correction": "Normalization / Standards-Based Correction",
    "Spike/Outlier Filtering Approach": "Spike / Outlier Filtering Approach",
    "Sample IGSN": "Sample Persistent Identifier",
    "Sample Sequence Design": "Analysis Sequence",
}


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
    total, files = 0, 0

    for path in find_tapps(ROOT):
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))

        present = {r[0].strip() for r in rows[1:] if r and r[0].strip()}
        edits = []
        for n, row in enumerate(rows[1:], start=2):
            old = row[0].strip() if row else ""
            new = RENAMES.get(old)
            if not new:
                continue
            if new in present:
                print(f"  !! {os.path.relpath(path, ROOT)} row {n}: {new!r} already exists — "
                      f"renaming {old!r} would collide. SKIPPED.")
                continue
            edits.append((n, old, new))
            row[0] = new

        if edits and not dry:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)
        if edits:
            files += 1
            total += len(edits)
            print(f"\n{os.path.relpath(path, ROOT)}")
            for n, old, new in edits:
                print(f"    row {n:>4}  {old!r}\n              -> {new!r}")

    verb = "would be" if dry else ""
    print(f"\n{'=' * 84}")
    print(f"  {total} field name(s) {verb} harmonised across {files} file(s).")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
