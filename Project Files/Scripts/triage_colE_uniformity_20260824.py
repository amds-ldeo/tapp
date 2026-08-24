#!/usr/bin/env python3
"""
triage_colE_uniformity_20260824.py — evidence generator for the Column E (Data Type)
uniformity register, conventions.md 7.8.10.

Column E is the only content column with no cross-TAPP consistency check: A (name), B
(description), C/D (tiers) and I (Keyed By) all have one, E has none. This script produces
the triage table that freezes the divergences present on 2026-08-24 so the new check ships
at 0 WARN and catches new drift, exactly as Triage_ColB_Uniformity_2026-08-12.csv did for
Column B.

Two tables are written:
  Triage_ColE_Uniformity_2026-08-24.csv       divergence across IDENTICAL field names
  Triage_ColE_NameVariants_2026-08-24.csv     divergence across name VARIANTS (suffix test)

Usage:  python3 triage_colE_uniformity_20260824.py [--root /path/to/TAPPs]
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
from collections import defaultdict

COL_ITEM, COL_TYPE, COL_KEYEDBY = 0, 4, 8

# Clusters assigned by inspection of which TAPPs hold which variant. A cluster is an
# authorship boundary, not a verdict: it says where the divergence came from, not whether
# it is justified.
LA = {"LA-MC-ICPMS", "LA-Q-ICP-MS", "LA-SF-ICP-MS"}
SOLUTION = {"Solution_MC-ICP-MS", "Solution_Q-ICP-MS", "Solution_SF-ICP-MS"}
ELECTRON = {"EPMA", "SEM", "SEM_Composition", "SEM_Imaging", "SEM_FIBSEM"}


def stem(fname: str) -> str:
    return re.sub(r"_TAPP_v\d+\.csv$|\.csv$", "", os.path.basename(fname))


def family(s: str) -> str:
    s = s.replace("_UPb", "")
    if s in LA:
        return "LA"
    if s in SOLUTION:
        return "Solution"
    if s in ELECTRON:
        return "electron-beam"
    return s


def cluster_of(variants: dict[str, list[str]]) -> str:
    """Name the authorship boundary the divergence tracks, or '' if it tracks none."""
    fams = {v: {family(s) for s in tapps} for v, tapps in variants.items()}
    allf = set().union(*fams.values())
    if allf <= {"LA", "Solution"} and len(allf) == 2:
        # every variant must sit on one side or the other for the boundary to be clean
        if all(len(f) == 1 for f in fams.values()):
            return "LA/Solution"
        return "LA/Solution (imperfect)"
    if allf <= {"electron-beam"}:
        return "EPMA/SEM"
    return ""


def collect(root: str):
    types: dict[str, list[tuple[str, str]]] = defaultdict(list)
    keys: dict[str, set[str]] = defaultdict(set)
    for p in sorted(glob.glob(os.path.join(root, "Current TAPPs", "*.csv"))):
        with open(p, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.reader(fh))
        for row in rows[1:]:
            if len(row) <= COL_TYPE or not row[COL_ITEM].strip():
                continue
            name = row[COL_ITEM].strip()
            if row[COL_TYPE].strip():
                types[name].append((stem(p), row[COL_TYPE].strip()))
            if len(row) > COL_KEYEDBY and row[COL_KEYEDBY].strip():
                keys[name].add(row[COL_KEYEDBY].strip())
    return types, keys


def words(s: str) -> list[str]:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    out_dir = os.path.join(root, "Claude Skills for TAPP", "analysis")

    types, keys = collect(root)

    # ---- Table 1: identical field names -----------------------------------
    rows = []
    for name, entries in sorted(types.items()):
        variants = defaultdict(list)
        for tapp, dt in entries:
            variants[dt].append(tapp)
        if len(variants) <= 1 or len(entries) <= 1:
            continue
        cl = cluster_of(variants)
        rows.append({
            "Field": name,
            "N_TAPPs": len(entries),
            "N_variants": len(variants),
            "Cluster": cl or "(none)",
            "Verdict": "LINEAGE" if cl else "OPEN",
            "Keyed_By": " | ".join(sorted(keys.get(name, {"(blank)"}))),
            "Variants": " || ".join(
                f"{dt} [{', '.join(sorted(t))}]" for dt, t in sorted(variants.items())
            ),
        })
    rows.sort(key=lambda r: (-r["N_TAPPs"], r["Field"]))
    p1 = os.path.join(out_dir, "Triage_ColE_Uniformity_2026-08-24.csv")
    with open(p1, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{p1}: {len(rows)} divergences "
          f"({sum(1 for r in rows if r['Verdict'] == 'LINEAGE')} LINEAGE, "
          f"{sum(1 for r in rows if r['Verdict'] == 'OPEN')} OPEN)")

    # ---- Table 2: name variants (two-word suffix containment, as Rule 7.8.7) ----
    tsets = {n: {dt for _, dt in e} for n, e in types.items()}
    vrows = []
    for short in sorted(tsets):
        ws = words(short)
        if len(ws) < 2:
            continue
        for long in sorted(tsets):
            wl = words(long)
            if long == short or len(wl) <= len(ws) or wl[-len(ws):] != ws:
                continue
            if tsets[short] == tsets[long]:
                continue
            vrows.append({
                "Base_field": short,
                "Variant_field": long,
                "Base_types": " | ".join(sorted(tsets[short])),
                "Variant_types": " | ".join(sorted(tsets[long])),
                "Keys_agree": "yes" if keys.get(short) == keys.get(long) else "no",
                "Seen_by_key_check": "yes" if keys.get(short) != keys.get(long) else "no",
            })
    p2 = os.path.join(out_dir, "Triage_ColE_NameVariants_2026-08-24.csv")
    with open(p2, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(vrows[0]))
        w.writeheader()
        w.writerows(vrows)
    new = sum(1 for r in vrows if r["Seen_by_key_check"] == "no")
    print(f"{p2}: {len(vrows)} pairs ({new} invisible to the 7.8.7 key companion — keys agree, "
          f"types differ)")


if __name__ == "__main__":
    main()
