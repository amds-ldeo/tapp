#!/usr/bin/env python3
"""
patch_c1_c3_20260808.py

C1 and C3 from the ReportingCore triage. C2 needs no action — see below.

C1 — Uncertainty Propagation Method -> Uncertainty Level and Propagation
------------------------------------------------------------------------
Renamed in the 8 TAPPs carrying the old name, and the description extended to require the
uncertainty LEVEL (1-sigma / 2-sigma / 95% confidence) alongside the propagation method.

Why this matters beyond tidiness: the better name exists only in the two geochronology TAPPs,
which are pending retirement. Retiring them without adopting it would delete the *concept* of
recording the uncertainty level from the library — and all six geochronology reporting
standards surveyed require it explicitly (Condon 2024, Schaen 2021, Rooney 2024, Flowers 2024,
Kohn 2024, Mahan 2023), with Flowers additionally distinguishing standard error from standard
deviation.

TIER LEFT AT C=Advanced, and this is a deliberate tension. precedents.md carries an explicit
reasoned decision for Advanced: "Many labs use informal uncertainty estimates without a
formally specified propagation framework. Requiring a formal propagation method as Basic would
either exclude many legitimate procedures or generate low-quality boilerplate." That reasoning
holds for the propagation FRAMEWORK. It does not obviously hold for the LEVEL, which every lab
has and which six standards mandate — and the two geochronology TAPPs set the merged field to
C=Basic for that reason.

Merging a Basic-worthy component with an Advanced-worthy one into a single field is the real
problem here. The cleaner resolution is to split: `Uncertainty Level` (C=Basic) and
`Uncertainty Propagation Method` (C=Advanced). That is a larger change and reverses a
documented precedent, so it is flagged rather than taken.

C2 — blank correction naming: NO ACTION
----------------------------------------
The whitespace variant was already resolved (patch_rule1_names_20260808). Two names remain and
neither should be merged:

    Blank Correction (EPMA, SEM, SEM_Composition; C=Advanced/D=Editable)
        concerns blank standards and carbon-coat contribution to the C signal — a
        standard-based determination, not a background subtraction. Verified by reading.

    Gas Blank (the two geochronology TAPPs; C=Basic/D=Read-Only)
        same concept as Blank / Background Correction Method, but both files are pending
        retirement under A3. Renaming files about to be superseded is churn.

C3 — Primary Calibration Standard Name descriptions
----------------------------------------------------
Seven of thirteen TAPPs already require the accepted value and its source; six do not. Those
six are extended. `Secondary Reference Materials` already states it in all 13 and is untouched.

Without the accepted value and its citation, a reported calibration is not reinterpretable: two
labs using "NIST 610" against different published values for the same element produce results
that are not comparable, and nothing in the record reveals it.

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

OLD_NAME = "Uncertainty Propagation Method"
NEW_NAME = "Uncertainty Level and Propagation"
NEW_DESC = (
    "The level at which uncertainties are quoted — 1-sigma, 2-sigma, or 95% confidence, and "
    "whether a measured spread is reported as a standard error or a standard deviation — together "
    "with the approach used to propagate analytical uncertainty through the data reduction chain "
    "to the final reported value. State which sources are included in the propagation: counting "
    "statistics, calibration standard uncertainty, internal standard uncertainty, drift correction, "
    "and any systematic contributions. A reported uncertainty is not interpretable without both "
    "halves — the same numeric value means different things at 1-sigma and at 95% confidence."
)

C3_ADDITION = (" Include the material name, its source or supplier, and a citation for the accepted "
               "values used, since results calibrated against different published values for the "
               "same material are not directly comparable.")
C3_FIELD = "Primary Calibration Standard Name"
C3_MARKER = re.compile(r"accepted value|certif|citation|reference value|source", re.I)


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
    c1 = c3 = 0

    for path in find_tapps(ROOT):
        rel = os.path.relpath(path, ROOT)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        names = {r[0].strip() for r in rows[1:] if r and r[0].strip()}
        touched = False

        for r in rows[1:]:
            nm = r[0].strip() if r else ""

            if nm == OLD_NAME:
                if NEW_NAME in names:
                    print(f"  !! {rel}: {NEW_NAME!r} already exists — collision, SKIPPED")
                    continue
                r[0], r[1] = NEW_NAME, NEW_DESC
                touched = True
                c1 += 1
                print(f"  C1  {rel}\n        {OLD_NAME!r} -> {NEW_NAME!r}  (C={r[2]} unchanged)")

            elif nm == NEW_NAME and not re.search(r"standard error|1-sigma", r[1], re.I):
                r[1] = NEW_DESC
                touched = True
                print(f"  C1  {rel}: description harmonised on existing {NEW_NAME!r}")

            if nm == C3_FIELD and not C3_MARKER.search(r[1]):
                r[1] = r[1].rstrip() + C3_ADDITION
                touched = True
                c3 += 1
                print(f"  C3  {rel}: {C3_FIELD} description extended")

        if touched and not dry:
            csv.writer(open(path, "w", newline="", encoding="utf-8-sig")).writerows(rows)

    verb = "would be" if dry else ""
    print(f"\n{'=' * 84}")
    print(f"  C1: {c1} field(s) renamed.   C3: {c3} description(s) extended.   {verb}")
    if dry:
        print("  Dry run — nothing written.")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
