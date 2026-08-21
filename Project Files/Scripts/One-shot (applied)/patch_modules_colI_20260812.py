#!/usr/bin/env python3
"""Module patches from the 2026-08-12 Column B / Column I survey. Modules first (Rule 6.6).

  Module_ReportingCore  Calibration Factor and Determination Method
                        Column I (none) -> reported property
                        Its own description says the factor "converts the measured quantity into
                        the reported quantity", so there is one per reported quantity. Chosen over
                        `analyte` because ReportingCore has 16 consumers including Lab-XCT, which
                        has no analyte anchor at all (7.2 — analyte is chemistry only); `analyte`
                        would be invalid there and would force a speculative
                        keyed_by_overridable entry, which 7.5 forbids.
                        7.4a is satisfied everywhere: Reported Variables and Units is mandatory
                        in all 16 TAPPs under Rule 8 and declares `defines: reported property`.

  Module_MCICPMS        Integration Time per Cycle  Column I (none) -> channel
                        G3 policy, settled 2026-08-12: where a key is present only under a stated
                        condition, declare the finest key unconditionally. A consumer given
                        `channel` can hold one value when every channel shares it; a consumer
                        given `(none)` cannot hold per-channel values at all, so the finer key is
                        the superset and the safe declaration. The description names isotope
                        channels explicitly. 7.4a holds: Collector Configuration declares
                        `defines: channel` in all three consumers.

                        Collector Configuration  Column B reworded only.
                        Column I stays `defines: channel`. The multi-dynamic cycling axis is left
                        as free text rather than reviving the `acquisition pass` key, which 7.4b/c
                        retired for want of a user — one user does not justify reinstating an
                        abstraction the rule deliberately removed.

Both MCICPMS descriptions also drop the retired `Analyte-Specific` term (Rule 7.6 cleaned Column G
and never swept Column B). Meaning is preserved; only the label goes.

Dry-run by default. Pass --apply to write.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COL_I = 8
COL_B = 1

OLD_CC = ("Includes all interference-monitor masses collected in addition to analyte isotopes. "
          "Analyte-specific: different element systems require different mass assignments within "
          "the collector array span.")
NEW_CC = ("Includes all interference-monitor masses collected in addition to analyte isotopes. "
          "Different element systems require different mass assignments within the collector "
          "array span.")

OLD_ITC = ("Procedure specifies the standard integration time; analyst may confirm or adjust "
           "within procedure bounds. Analyte-specific when different isotope channels use "
           "different integration schemes.")
NEW_ITC = ("Procedure specifies the standard integration time; analyst may confirm or adjust "
           "within procedure bounds. Where different isotope channels use different integration "
           "schemes, record the time for each channel.")

# (module file, field, column, expected old value, new value)
PATCHES = [
    ("Module_ReportingCore.csv", "Calibration Factor and Determination Method",
     COL_I, "(none)", "reported property"),
    ("Module_MCICPMS.csv", "Integration Time per Cycle", COL_I, "(none)", "channel"),
    ("Module_MCICPMS.csv", "Collector Configuration", COL_B, OLD_CC, NEW_CC),
    ("Module_MCICPMS.csv", "Integration Time per Cycle", COL_B, OLD_ITC, NEW_ITC),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    by_file = {}
    for fn, field, col, old, new in PATCHES:
        by_file.setdefault(fn, []).append((field, col, old, new))

    failures = 0
    for fn, edits in by_file.items():
        path = os.path.join(MODULES, fn)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        changed = 0
        for field, col, old, new in edits:
            hits = [n for n, r in enumerate(rows) if r and r[0].strip() == field]
            if len(hits) != 1:
                print(f"  FAIL {fn}: expected exactly 1 row named '{field}', found {len(hits)}")
                failures += 1
                continue
            n = hits[0]
            cur = rows[n][col] if col < len(rows[n]) else ""
            if col == COL_B:
                # Substring replacement — the description is long and only its tail changes.
                if old not in cur:
                    print(f"  FAIL {fn} '{field}' col {'ABCDEFGHI'[col]}: "
                          f"expected tail not found.\n        have: ...{cur[-140:]}")
                    failures += 1
                    continue
                rows[n][col] = cur.replace(old, new)
            else:
                if cur.strip() != old:
                    print(f"  FAIL {fn} '{field}' col {'ABCDEFGHI'[col]}: "
                          f"expected {old!r}, found {cur.strip()!r}")
                    failures += 1
                    continue
                rows[n][col] = new
            changed += 1
            print(f"  {'APPLY' if args.apply else 'DRY'} {fn} r{n+1} '{field}' "
                  f"col {'ABCDEFGHI'[col]}")
            if col == COL_I:
                print(f"        {old!r} -> {new!r}")
            else:
                print(f"        ...{old[-90:]}\n     -> ...{new[-90:]}")
        if args.apply and changed and not failures:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)
            print(f"  WROTE {path}")

    if failures:
        print(f"\n{failures} failure(s) — nothing written.")
        sys.exit(1)
    print("\nOK" + ("" if args.apply else " (dry run — pass --apply to write)"))


if __name__ == "__main__":
    main()
