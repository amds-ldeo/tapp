#!/usr/bin/env python3
"""Batch key update from the literature-assessment audit (2026-08-12, second pass).

Every change here is backed by counted extractions, not by reading a description. The governing
rule the audit produced:

    THE KEY IS THE FINEST AXIS ATTESTED IN REPORTED DATA — not one merely computed, and not one
    that is only conceptually possible.

That rule resolves both directions. `Beam Current` keeps `sampling unit` because 2 of 13 procedures
do publish per-phase currents; LA `Detection Limit` loses it because the per-spot value is computed
and then averaged away before anything is reported.

Changes
-------
1  Detection Limit (6 LA)          sampling unit x reported property -> reported property
   7 of 7 papers that report LODs report one per element, aggregated. Navarro 2024: the LOD "must
   be calculated for each acquisition", then "Table 3 shows the median values obtained for each
   element". Chernonozhkin C5: LODs "are the average of all LODs". Per-spot LODs appear only as
   `<LOD` censoring flags on individual concentrations. Makes the field UNIFORM across all 12
   TAPPs, so it leaves the technique-dependent register.

2  Isobaric Interference Corrections Applied (9)   channel -> (none)
   All extractions are Yes/No ("Yes (fs laser reduces interferences)"), and the field's own
   description already says "A procedure-level Boolean". Two independent lines of evidence. The
   per-mass detail lives in Interfering Species and Interference Correction Method, which keep
   `channel`.

3  Secondary Reference Materials (9 isotope TAPPs)  defines: standard per analyte -> defines: standard
   Reverses this morning's uniform decision on evidence. 16 extractions in LA-SF/Solution are plain
   standard lists ("BCR-2, AGV-2, JB-2, BR, JB-3") with no per-analyte breakdown; only EPMA/SEM ask
   for "assessed elements". EPMA + SEM_Composition + SEM keep `defines: standard per analyte`. The
   per-analyte wording added to the 9 isotope descriptions this morning is rolled back. Adds a
   technique-dependent register entry.

4  Primary Calibration Standard Name (2 LA-SF)     (none) -> analyte
   Navarro 2024 assigns standards to analyte groups: "North Chile Filomena for Fe/Co/Ni/Cu/Ga/Ge/
   As/W/Au; Hoba for Ru/Rh/Pd/Re/Os/Ir/Pt". 1 of 7, but the axis is attested in reported data, which
   is the same threshold Beam Current was kept on. LA-Q and both Solution TAPPs stay `(none)` —
   unanimously single-standard or one joint calibration set.

5  Beam Damage Minimization (EPMA)                 (none) -> sampling unit
   "Defocused beam 5-10 um for maskelynite, phosphate, sulfide, and glass" — per phase.

NOT applied, though initially proposed
--------------------------------------
`Within-Session Analytical Precision and Assessment Method` and `Analytical Accuracy and Assessment
Method` KEEP `standard x reported property`. The audit scored them OVER-DECLARED, but the raw
extractions contradict that: every Solution accuracy cell references reference materials ("% deviation
from published Pb isotope values for geological RMs (BCR-2, AGV-2, JB-2, BR, JB-3)"). The detector
required two *named* RMs in one cell and scored "USGS/GSJ RMs" as scalar. Detector precision failure,
not a finding. Keeping them also preserves `standard` as a used key in Solution Q/SF, without which
Secondary Reference Materials would have become an unused definer under 7.4c.

`Minimum Resolvable Feature Size` (Lab-XCT) deferred: 5 scalar extractions, but multi-volume scanning
could exercise the per-sub-volume axis.

Dry-run by default. Pass --apply to write.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

COL_B, COL_I = 1, 8

# (field, tapp-prefix filter or None for all, old Column I, new Column I)
KEY_EDITS = [
    ("Detection Limit", ("LA-",), "sampling unit x reported property", "reported property"),
    ("Isobaric Interference Corrections Applied", None, "channel", "(none)"),
    ("Secondary Reference Materials", ("LA-", "Solution_"),
     "defines: standard per analyte", "defines: standard"),
    ("Primary Calibration Standard Name", ("LA-SF-ICP-MS",), "(none)", "analyte"),
    ("Beam Damage Minimization", ("EPMA",), "(none)", "sampling unit"),
]

# Roll back this morning's per-analyte additions to the 9 isotope descriptions.
DESC_EDITS = [
    ("Secondary Reference Materials",
     "Include material name, source, the analytes assessed against it, and citation for accepted "
     "values used for comparison.",
     "Include material name, source, and citation for accepted values used for comparison."),
    ("Secondary Reference Materials",
     "Specify material name, the analytes assessed against it, and expected-value source.",
     "Specify material name and expected-value source."),
    ("Secondary Reference Materials",
     "Specify material name, the analytes assessed against it, and the isotopic composition "
     "reference source",
     "Specify material name and the isotopic composition reference source"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    applied, failures = [], []
    for path in V.discover(ROOT):
        base = os.path.basename(path)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        dirty = False
        for n, r in enumerate(rows[1:], start=2):
            if not r or len(r) <= COL_I or not r[0].strip():
                continue
            fld = r[0].strip()

            for f, pref, old, new in KEY_EDITS:
                if fld != f:
                    continue
                if pref and not base.startswith(pref):
                    continue
                if r[COL_I].strip() != old:
                    failures.append(f"{base} r{n} '{f}' col I: expected {old!r}, "
                                    f"found {r[COL_I].strip()!r}")
                    continue
                r[COL_I] = new
                dirty = True
                applied.append((base, n, f, "I", old, new))

            for f, old, new in DESC_EDITS:
                if fld != f or old not in r[COL_B]:
                    continue
                r[COL_B] = r[COL_B].replace(old, new)
                dirty = True
                applied.append((base, n, f, "B", old[:44], new[:44]))

        if dirty and args.apply:
            with open(path, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    for base, n, f, col, old, new in applied:
        print(f"  {'APPLY' if args.apply else 'DRY':5s} {base[:32]:34s} r{n:<4} {f[:40]:42s} "
              f"{col}  {old!r} -> {new!r}")

    from collections import Counter
    c = Counter((f, col) for _, _, f, col, _, _ in applied)
    print(f"\n{len(applied)} cell(s):")
    for (f, col), n in sorted(c.items()):
        print(f"  {n:3d}  {f[:52]:54s} col {col}")

    if failures:
        print("\nFAILURES (nothing written):")
        for x in failures:
            print("  " + x)
        sys.exit(1)
    print("\nOK" + ("" if args.apply else " (dry run — pass --apply to write)"))


if __name__ == "__main__":
    main()
