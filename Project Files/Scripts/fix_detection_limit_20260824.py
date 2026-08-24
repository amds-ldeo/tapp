#!/usr/bin/env python3
"""
fix_detection_limit_20260824.py — resolve amds-ldeo/tapp#1.

`Detection Limit` was typed three ways and `Detection Limit Method` four, across 12 TAPPs. Column E
drives downstream schema generation, so one metadata item was being generated in three incompatible
shapes and could not be collapsed into a shared definition. Both converge here, on forms the library
already defines — for `Detection Limit` the target already exists in the 3 Solution tables.

  Detection Limit         Text (free) / Numeric (ppm or wt%) / Numeric + unit / Text
                          -> `Numeric + unit / Text`                     (9 tables move, 3 already there)
  Detection Limit Method  Text (free) / Text / URI / Controlled list
                          -> `Controlled list / Text` + a uniform Column F   (all 12 move)
  EDS Detection Limit     Text (free) -> `Numeric + unit / Text`         (TEM; same field semantically,
                          keys already harmonised to `reported property` 2026-08-12)

WHY NOT A PINNED UNIT. Of 42 literature-attested `Detection Limit` cells, ZERO are a bare number —
29 per-analyte lists, 6 ranges across analytes, 4 qualitative. The attested units span mass fraction
(wt%, ppm, µg g⁻¹), mass concentration (µg/L, ng/L, pg/mL) and molar (nM, µmol/mol), so no const is
right across them; µg/L is the normal form for solution work, where the LOD is a property of the
solution and not the rock. The LA `Numeric (ppm or wt%)` cell was also contradicted by its own row:
Column B names three units and Column F's example is a string. `Numeric + unit` is the vocabulary's
term for exactly this — "a number where the unit is variable and must be stated by the user" — and
the `/ Text` half is earned by the 10 attested cells that are ranges or qualitative statements, not
an escape from choosing. Precedent: `Instrument Sensitivity`, the structural twin (keyed, dimensioned
per-channel figure of merit), is `Numeric + unit / Text` across 9 TAPPs.

WHY THE METHOD IS A COMPOUND. All 10 attested cells name a formula, cite a source, or both — none is
free prose. A typical value is "Longerich et al. (1996): LOD = (3SD/S) × √(1/Nb + 1/Na)": a named
family AND a reference AND an equation. Solution's `Controlled list` held the family but not the
citation; LA's `Text / URI` held the citation but not the family. Each was half the answer.

COLUMN F. The compound takes the allowed-value list, per the convention every other
`Controlled list / Text` field follows. Per conventions.md a compound whose first component is
`Controlled list` offers `N/A | None` but NOT `Other: specify` — the `/ Text` half already grants
that permission and requiring it would ask twice. `3σ blank` and `3σ background` are attested;
`3× blank mean` and `Poisson statistics` are inherited from the incumbent Solution list;
`3σ counting statistics` is added for the electron-beam family, which has NO literature attestation
on this field but whose Column F examples ("3-sigma from counting statistics", Goldstein 2018;
Llovet 2020 Eq. 4) record the technique norm. That last one is the only value here not resting on
attestation, and it is stated plainly rather than buried: the alternative was forcing EPMA and SEM
into `Poisson statistics`, which is the same over-tightening this patch exists to undo.

The LA Column F citation examples are dropped in favour of the list; the instruction they carried
survives in Column B, which already reads "Reference or description of the method used…".

Usage:  python3 fix_detection_limit_20260824.py [--root ...] [--apply]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys

DATE = "2026-08-24"
COL_ITEM, COL_TYPE, COL_EXAMPLE, COL_UPDATE = 0, 4, 5, 7

METHOD_ALLOWED = ("3σ blank | 3σ background | 3σ counting statistics | 3× blank mean | "
                  "Poisson statistics | N/A | None")

# field name -> (new Data Type, new Column F or None to leave alone)
CHANGES = {
    "Detection Limit":        ("Numeric + unit / Text", None),
    "EDS Detection Limit":    ("Numeric + unit / Text", None),
    "Detection Limit Method": ("Controlled list / Text", METHOD_ALLOWED),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    reg_path = os.path.join(root, "composed_tapps.json")
    with open(reg_path, encoding="utf-8") as fh:
        reg = json.load(fh)

    renames = []
    for entry in sorted(reg["composed"], key=lambda e: e["tapp"]):
        rel = entry["tapp"]
        path = os.path.join(root, rel)
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))

        touched = []
        for row in rows[1:]:
            if len(row) <= COL_TYPE:
                continue
            name = row[COL_ITEM].strip()
            if name not in CHANGES:
                continue
            new_type, new_f = CHANGES[name]
            before = (row[COL_TYPE], row[COL_EXAMPLE])
            if row[COL_TYPE] != new_type:
                row[COL_TYPE] = new_type
            if new_f is not None and row[COL_EXAMPLE] != new_f:
                row[COL_EXAMPLE] = new_f
            if (row[COL_TYPE], row[COL_EXAMPLE]) != before:
                row[COL_UPDATE] = DATE
                touched.append((name, before[0], row[COL_TYPE]))

        if not touched:
            continue

        base = os.path.basename(rel)
        newver = int(re.search(r"_v(\d+)\.csv$", base).group(1)) + 1
        newbase = re.sub(r"_v\d+\.csv$", f"_v{newver}.csv", base)
        renames.append((rel, os.path.join(os.path.dirname(rel), newbase)))

        print(f"{base}  ->  {newbase}")
        for n, old, new in touched:
            print(f"      {n:<24} {old!r} -> {new!r}")

        if args.apply:
            with open(os.path.join(root, os.path.dirname(rel), newbase),
                      "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{len(renames)} TAPP(s) changed")
    if not args.apply:
        print("(dry run — pass --apply to write)")
        return

    # --- registers -----------------------------------------------------------
    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in renames}
    for entry in reg["composed"]:
        b = os.path.basename(entry["tapp"])
        if b in pathmap:
            entry["tapp"] = entry["tapp"].replace(b, pathmap[b])
    reg["generated"] = DATE
    with open(reg_path, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"  composed_tapps.json: {len(pathmap)} path(s) updated")

    cv = os.path.join(root, "Project Files", "Registers & Planning",
                      "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in crows[1:]:
            for i, cell in enumerate(r):
                for old, new in pathmap.items():
                    if old in cell:
                        r[i] = cell.replace(old, new)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(crows)
        print("  TAPP_Composed_Variants.csv updated")

    # --- retire superseded, into the DATED SUBFOLDER ------------------------
    # `Superseded TAPPs/<DATE>/`, never a root-level `Superseded TAPPs (<DATE>)/`: .gitignore is an
    # allowlist keyed on `!/Superseded TAPPs/`, so a new root folder would be silently untracked and
    # the superseded versions would never reach GitHub.
    sup = os.path.join(root, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for old, _ in renames:
        oldp = os.path.join(root, old)
        shutil.move(oldp, os.path.join(sup, os.path.basename(oldp)))
        oldx = oldp[:-4] + ".xlsx"
        if os.path.exists(oldx):
            shutil.move(oldx, os.path.join(sup, os.path.basename(oldx)))
    print(f"  retired {len(renames)} CSV(s) + xlsx to Superseded TAPPs/{DATE}/")

    # --- xlsx, then the Rule 12 mirror (sync copies xlsx, it does not build them) ---
    gen = os.path.join(root, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, new in renames:
        r = subprocess.run([sys.executable, gen, new], cwd=root, capture_output=True, text=True)
        if r.returncode:
            print(f"  WARN xlsx failed for {new}: {r.stderr.strip()[:160]}")
    print(f"  regenerated {len(renames)} xlsx")

    sync = os.path.join(root, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, sync, "--apply"], cwd=root, capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    print(f"  Rule 12 mirror: {tail[0].strip() if tail else 'sync ran'}")


if __name__ == "__main__":
    main()
