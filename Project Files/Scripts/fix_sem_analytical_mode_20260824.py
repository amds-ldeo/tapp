#!/usr/bin/env python3
"""
fix_sem_analytical_mode_20260824.py — resolve amds-ldeo/tapp#3.

The issue reports 84 `Analytical Mode` publication cells across the four SEM tables that are not
drawn from those tables' own mode columns, in two classes. Investigation found both classes share
ONE root cause, and that the reported cells are the visible part of a larger problem.

ROOT CAUSE (part A). Column F of the `Analytical Mode` row in the four SEM tables was authored
against an informal SEM vocabulary instead of each table's mode-flag headers. SEM offers
`EDS | SEM-WDS | CL` where its mode columns say `EDS Point Analysis | EDS Mapping |
WDS Point Analysis | WDS Mapping | CL Point Analysis | CL Mapping`, and the sub-TAPPs additionally
offer modes they do not declare. Rule 3 requires the exact strings, "no paraphrase, abbreviate, or
substitute synonyms", and exempts this field from `N/A | None | Other: specify`. Curators typed
`EDS` and `CL` into the publication cells because the table told them those were the allowed
values — so the bad vocabulary generated the bad cells. All 12 other TAPPs are compliant; the four
SEM tables are the only violators, which is exactly the set the issue identifies.

PART B — the 84 cells (issue Class 1). Fixable mechanically, contrary to the issue's expectation
that most "need someone who knows the paper to pick the token". Each literature column's HEADER
already names the mode in canonical form — `Gucsik et al. 2013 | Forsterite, Kaba meteorite (CV3) |
CL Mapping (JEOL JSM-5410LV)` — and all 35 SEM headers use tokens from the table's own vocabulary,
with zero exceptions. The row disagrees with its own header in 29 of 35 cells, including 11 that
say a bare `N` for a mode the header states plainly. The curator already recorded the mode; the row
is a hand-typed duplicate that drifted. EPMA is the precedent: same header convention, and zero
invalid cells. Cells are therefore set from the header, which also repairs the bare `N`s (checked
first: they carry no parenthetical, so no curator note is lost).

PART C — foreign columns (issue Class 2), approved by the maintainer. All four SEM tables carry the
IDENTICAL 35 literature columns, unfiltered, so the sub-TAPPs document procedures whose mode they do
not declare — `SEM_FIBSEM` carries Gucsik's CL study across all 58 of its fields. The `Analytical
Mode` row is merely where this became visible, being the only row checkable against a vocabulary.
Columns whose header mode is not declared by the table are dropped: 26 from SEM_Composition, 17 from
SEM_Imaging, 27 from SEM_FIBSEM.

    Verified before deleting anything: all 70 foreign columns exist in the parent SEM table, and
    every data cell in them is byte-identical there. Zero information is lost — the parent keeps all
    35 columns and remains the complete SEM evidence base.

Usage:  python3 fix_sem_analytical_mode_20260824.py [--root ...] [--apply]
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
COL_ITEM, COL_EXAMPLE, COL_UPDATE = 0, 5, 7
FIRST_MODE_COL = 9
SENTINEL = "Literature Assessment"

SEM = ["SEM/SEM_TAPP_v23.csv", "SEM/SEM_Composition_TAPP_v23.csv",
       "SEM/SEM_Imaging_TAPP_v14.csv", "SEM/SEM_FIBSEM_TAPP_v14.csv"]

# One realistic multi-mode example per table, in the house form the compliant TAPPs use
# (quoted tokens, joined with '; '). Both members must be declared by that table.
COMPOSITE = {
    "SEM_TAPP":             "BSE Imaging; EDS Point Analysis",
    "SEM_Composition_TAPP": "EDS Point Analysis; EDS Mapping",
    "SEM_Imaging_TAPP":     "SE Imaging; BSE Imaging",
    "SEM_FIBSEM_TAPP":      "TEM Sample Preparation; 3D Tomography",
}


def header_mode(h: str) -> str:
    """The mode token a literature column header ends with, minus its instrument parenthetical."""
    return re.sub(r"\s*\(.*$", "", h.replace("\n", " | ").split("|")[-1].strip()).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    renames = []
    for rel in SEM:
        path = os.path.join(root, rel)
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
        hdr = [h.replace("﻿", "") for h in rows[0]]
        sent = next(i for i, h in enumerate(hdr) if SENTINEL in h)
        modes = hdr[FIRST_MODE_COL:sent]
        stem = re.sub(r"_v\d+\.csv$", "", os.path.basename(rel))
        print(f"\n{os.path.basename(rel)}   ({len(modes)} modes declared)")

        # --- C: drop literature columns whose mode this table does not declare -------
        drop = [i for i in range(sent + 1, len(hdr)) if header_mode(hdr[i]) not in modes]
        if drop:
            dropped = {}
            for i in drop:
                dropped[header_mode(hdr[i])] = dropped.get(header_mode(hdr[i]), 0) + 1
            print(f"   C  drop {len(drop)} foreign literature column(s): {dropped}")
            keep = [i for i in range(len(hdr)) if i not in set(drop)]
            rows = [[r[i] if i < len(r) else "" for i in keep] for r in rows]
            hdr = rows[0]
            sent = next(i for i, h in enumerate(hdr) if SENTINEL in h)
        else:
            print("   C  no foreign columns")

        # --- B: Analytical Mode publication cells := the mode named in their header ---
        am = next(r for r in rows[1:] if r and r[COL_ITEM].strip() == "Analytical Mode")
        fixed = 0
        for i in range(sent + 1, len(hdr)):
            want = header_mode(hdr[i])
            if i < len(am) and am[i].strip() != want:
                am[i] = want
                fixed += 1
        print(f"   B  {fixed} publication cell(s) set from their column header")

        # --- A: Column F := this table's mode headers, Rule 3 --------------------------
        newf = " | ".join(f"'{m}'" for m in modes) + f" | '{COMPOSITE[stem]}'"
        if am[COL_EXAMPLE] != newf:
            print(f"   A  Column F rewritten to mirror the {len(modes)} mode headers")
            am[COL_EXAMPLE] = newf
        if fixed or drop or am[COL_EXAMPLE] == newf:
            am[COL_UPDATE] = DATE

        m = int(re.search(r"_v(\d+)\.csv$", rel).group(1)) + 1
        newrel = re.sub(r"_v\d+\.csv$", f"_v{m}.csv", rel)
        renames.append((rel, newrel))
        print(f"   ->  {os.path.basename(newrel)}")
        if args.apply:
            with open(os.path.join(root, newrel), "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{len(renames)} TAPP(s) changed")
    if not args.apply:
        print("(dry run — pass --apply to write)")
        return

    reg_path = os.path.join(root, "composed_tapps.json")
    with open(reg_path, encoding="utf-8") as fh:
        reg = json.load(fh)
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

    cv = os.path.join(root, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
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

    sup = os.path.join(root, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for old, _ in renames:
        oldp = os.path.join(root, old)
        shutil.move(oldp, os.path.join(sup, os.path.basename(oldp)))
        oldx = oldp[:-4] + ".xlsx"
        if os.path.exists(oldx):
            shutil.move(oldx, os.path.join(sup, os.path.basename(oldx)))
    print(f"  retired {len(renames)} CSV(s) + xlsx to Superseded TAPPs/{DATE}/")

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
