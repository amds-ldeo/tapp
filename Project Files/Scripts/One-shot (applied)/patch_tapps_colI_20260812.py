#!/usr/bin/env python3
"""TAPP-owned patches from the 2026-08-12 Column B / Column I survey.

Run AFTER patch_modules_colI_20260812.py and recompose_all_20260812.py --apply, per Rule 6.6.
Every field touched here is TAPP-owned (verified against modules/ before writing this script),
so none of these edits can be reverted by a later recomposition.

  Class 1  definer carrying a second key -> the new Rule 7.3 form
           Monitored Isotopes            defines: channel  -> defines: channel per analyte   (6)
           EELS Edges                    defines: channel  -> defines: channel per analyte   (1)
           Secondary Reference Materials defines: standard -> defines: standard per analyte (12)
           and the 9 isotope descriptions gain an explicit per-analyte ask, worded for isotope
           work ("the analytes assessed against it") rather than copying EPMA's "assessed
           elements". Per the 2026-08-12 decision the key is uniform across all 12, so no
           technique-dependent register entry is needed.

  Class 4  Analyte's stale pointer to the retired Comments-column label -> points at Column I

  Class 5/6  the retired `Analyte-Specific` label removed from Column B where Column I already
           carries the cardinality correctly

  Class 6  Detection Limit / Detection Limit Method prose aligned to `reported property`,
           naming the reported concentration variable and the analyte isomorphism inline.
           delta or epsilon Value Reference Standard -> `analyte`: the zero-delta anchor is
           chosen per element system (IRMM-014 for Fe), not per reported ratio; both delta-56
           and delta-57 share one anchor.

  Class 3  Dwell Time per Mass prose reworded to the declared `channel` key.

Dry-run by default. Pass --apply to write. Reports a FAIL and writes nothing if any expected
string is absent, so a drifted file cannot be silently half-patched.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

COL_B, COL_I = 1, 8

STALE_A = ("Fields below flagged as Analyte-Specific in the Comments column apply individually "
           "to each element in this list.")
STALE_B = ("Fields flagged as Analyte-Specific in the Comments column apply individually to each "
           "element or isotope in this list.")
NEW_A = ("Fields whose Keyed By column declares 'analyte' apply individually to each element in "
         "this list.")
NEW_B = ("Fields whose Keyed By column declares 'analyte' apply individually to each element or "
         "isotope in this list.")

DL_ISO = "one per reported concentration variable (one per analyte, these being the same set)"

# (field, kind, old, new)
#   kind 'I'    -> whole-cell replacement of Column I, old must match exactly
#   kind 'B'    -> substring replacement in Column B, old must be present
#   kind 'B?'   -> substring replacement in Column B, applied only where present (variant-specific)
EDITS = [
    # ---------------- Class 1 — key changes
    ("Monitored Isotopes", "I", "defines: channel", "defines: channel per analyte"),
    ("EELS Edges", "I", "defines: channel", "defines: channel per analyte"),
    ("Secondary Reference Materials", "I", "defines: standard", "defines: standard per analyte"),
    # Class 1 — the 9 isotope descriptions gain the per-analyte ask
    ("Secondary Reference Materials", "B?",
     "Include material name, source, and citation for accepted values used for comparison.",
     "Include material name, source, the analytes assessed against it, and citation for accepted "
     "values used for comparison."),
    ("Secondary Reference Materials", "B?",
     "Specify material name and expected-value source.",
     "Specify material name, the analytes assessed against it, and expected-value source."),
    ("Secondary Reference Materials", "B?",
     "Specify material name and the isotopic composition reference source",
     "Specify material name, the analytes assessed against it, and the isotopic composition "
     "reference source"),

    # ---------------- Class 4 — stale cross-reference
    ("Analyte", "B?", " " + STALE_A, " " + NEW_A),
    ("Analyte", "B?", " " + STALE_B, " " + NEW_B),

    # ---------------- Class 5 — prose duplicates Column I
    ("Monitored Isotopes", "B", " Analyte-specific field.", ""),
    ("Mass Resolution per Analyte", "B", " Analyte-specific field.", ""),
    ("Per-Analyte Calibration Strategy", "B?",
     " Analyte-specific when different elements use different strategies.",
     " Where different elements use different strategies, record each."),
    ("Per-Analyte Calibration Strategy", "B?",
     "Free text; list analyte-specific strategies as needed.",
     "Free text; list the strategy for each analyte or analyte group as needed."),

    # ---------------- Class 6 — prose contradicts Column I; Column I is correct
    ("Interfering Species", "B?", " Analyte-specific.", ""),
    ("Interference Correction Method", "B?", " Analyte-specific.", ""),
    ("Isobaric Interference Corrections Applied", "B?", " Analyte-specific.", ""),
    ("Isotope Ratio Reported", "B?", " Analyte-specific.", ""),
    ("delta or epsilon Value Reference Standard", "B?", " Analyte-specific.", ""),
    ("delta or epsilon Value Reference Standard", "I", "reported property", "analyte"),

    # ---------------- Class 6 — Detection Limit family aligned to reported property
    ("Detection Limit", "B?",
     "Elemental detection limits for each analyte, applicable when",
     "Elemental detection limits, " + DL_ISO + ", applicable when"),
    ("Detection Limit", "B?",
     "Elemental detection limits for each analyte.",
     "Elemental detection limits, " + DL_ISO + "."),
    ("Detection Limit", "B?",
     "Method detection limit at 99% confidence (3-sigma) for each analyte, derived from counting "
     "statistics on peak and background. Include the method and resulting value per analyte.",
     "Method detection limit at 99% confidence (3-sigma), " + DL_ISO + ", derived from counting "
     "statistics on peak and background. Include the method and the resulting value for each."),
    ("Detection Limit", "B?",
     "Method detection limit at 99% confidence for each analyte. Include the method used and the "
     "resulting value per analyte.",
     "Method detection limit at 99% confidence, " + DL_ISO + ". Include the method used and the "
     "resulting value for each."),
    ("Detection Limit", "B?",
     "Session detection limit for each measured isotope, expressed in",
     "Session detection limit, one per reported concentration variable, expressed in"),
    ("Detection Limit", "B?",
     "Report the value(s) and units per isotope or element group.",
     "Report the value(s) and units per measured isotope or element group, these being the "
     "reported concentration variables."),
    ("Detection Limit Method", "B?",
     "Method used to calculate detection limits for each analyte where concentration data are "
     "reported.",
     "Method used to calculate detection limits for each reported concentration variable, where "
     "concentration data are reported."),
    ("Detection Limit Method", "B?",
     "Method used to calculate detection limits for each analyte.",
     "Method used to calculate detection limits for each reported concentration variable."),

    # ---------------- Class 3 — conditional key reworded to the declared key
    ("Dwell Time per Mass", "B?",
     "May differ per analyte if analyte-specific dwell times are programmed.",
     "May differ between masses where per-mass dwell times are programmed."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    by_field = defaultdict(list)
    for f, kind, old, new in EDITS:
        by_field[f].append((kind, old, new))

    failures = []
    applied = defaultdict(int)
    total_rows = 0

    for path in V.discover(ROOT):
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        name = os.path.basename(path)
        dirty = False
        for n, r in enumerate(rows[1:], start=2):
            if not r or len(r) <= COL_I:
                continue
            field = r[0].strip()
            if field not in by_field:
                continue
            for kind, old, new in by_field[field]:
                if kind == "I":
                    if r[COL_I].strip() != old:
                        continue
                    r[COL_I] = new
                    dirty = True
                    applied[(field, "I", old)] += 1
                    total_rows += 1
                else:
                    if old not in r[COL_B]:
                        if kind == "B":
                            failures.append(f"{name} r{n} '{field}' col B: expected "
                                            f"{old!r} not found")
                        continue
                    r[COL_B] = r[COL_B].replace(old, new).replace("  ", " ").strip()
                    dirty = True
                    applied[(field, "B", old[:46])] += 1
                    total_rows += 1
        if dirty and args.apply:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)

    for (field, col, old), n in sorted(applied.items()):
        print(f"  {n:3d} x  {field[:42]:44s} col {col}  {old!r}")
    print(f"\n{total_rows} cell(s) across {len(applied)} distinct edits")

    # Every edit in the table must have found at least one row, or the table has drifted
    # from the library and the survey's counts no longer describe the files.
    for f, kind, old, new in EDITS:
        if not any(k[0] == f and k[1] == kind[0] and (k[2] == old or k[2] == old[:46])
                   for k in applied):
            failures.append(f"edit never matched: '{f}' col {kind[0]} {old[:70]!r}")

    if failures:
        print("\nFAILURES:")
        for x in failures:
            print("  " + x)
        sys.exit(1)
    print("OK" + ("" if args.apply else " (dry run — pass --apply to write)"))


if __name__ == "__main__":
    main()
