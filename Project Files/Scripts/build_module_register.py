#!/usr/bin/env python3
"""Generate TAPP_Module_Register.csv from the module manifests and composed_tapps.json.

Every column except Status is derived: Layer and Title and Version come from the manifest, Fields
and Blocks from the module CSV and manifest, Consumers from the composition register. Maintaining
derived facts by hand is what produced the two silent version drifts recorded in Rule 6.13, and the
register's own `register-stale-*` lint findings exist only because nothing generated it.

**Retired modules are preserved.** A module that has been archived out of `modules/` has no manifest
to regenerate from, so its row is carried through untouched — that row IS the retirement record and
regenerating it away would erase why the module is gone.

  --check (default)  report whether the file on disk is what would be generated; exit 1 if not
  --apply            write it
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
REG = os.path.join(ROOT, "composed_tapps.json")
OUT = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
HDR = ["Module", "Layer", "Title", "Fields", "Blocks", "Version", "Consumers", "Status"]


def module_field_count(name):
    """Named, non-group-header rows in the module CSV.

    This is what the Fields column has always meant, and what README section 9 publishes. For the two
    Layer 3 modules it therefore includes overlay rows — ArAr introduces 4 fields and overlays 12,
    UPb introduces 3 and overlays 12 — because a Layer 3 module's job is as much the overlay as the
    insertion. Counting only introduced fields would silently redefine a published number.
    """
    p = os.path.join(MODDIR, f"Module_{name}.csv")
    n = 0
    for r in list(csv.reader(open(p, encoding="utf-8-sig")))[1:]:
        a = r[0].strip() if r else ""
        if not a or re.match(r"^\d+\.\s", a):
            continue
        n += 1
    return n


def build():
    reg = json.load(open(REG, encoding="utf-8"))
    consumers = {}
    for e in reg.get("composed", []):
        for m in e.get("modules", []):
            consumers[m["name"]] = consumers.get(m["name"], 0) + 1

    rows = []
    live = set()
    for p in sorted(glob.glob(os.path.join(MODDIR, "Module_*.json"))):
        man = json.load(open(p, encoding="utf-8"))
        name = man["module"]
        live.add(name)
        n_consumers = consumers.get(name, 0)
        blocks = man.get("blocks")
        n_blocks = len(blocks) if blocks is not None else 1
        rows.append([
            name,
            str(man.get("layer", "")),
            man.get("title", ""),
            str(module_field_count(name)),
            str(n_blocks),
            str(man.get("version", "")),
            f"{n_consumers} TAPP(s)",
            "active",
        ])

    # Retired modules: no manifest left, so carry their existing row through unchanged.
    carried = []
    if os.path.exists(OUT):
        for r in list(csv.reader(open(OUT, newline="", encoding="utf-8-sig")))[1:]:
            if r and r[0].strip() and r[0].strip() not in live:
                carried.append(r)
    rows += carried
    rows.sort(key=lambda r: r[0].lower())
    return [HDR] + rows, sorted(live), carried


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    want, live, carried = build()
    have = list(csv.reader(open(OUT, newline="", encoding="utf-8-sig"))) if os.path.exists(OUT) else []

    print(f"{len(live)} live module(s); {len(carried)} retired row(s) carried through")
    for r in want[1:]:
        tag = "" if r[0] in live else "   (retired — carried)"
        print(f"  {r[0]:22s} L{r[1]}  {r[3]:>2} field(s)  {r[4]} block(s)  v{r[5]:<3} {r[6]:<12}{tag}")

    if want == have:
        print("\nregister is up to date")
        return 0

    print("\nregister DIFFERS from what would be generated:")
    hi = {r[0]: r for r in have[1:] if r}
    wi = {r[0]: r for r in want[1:]}
    for k in sorted(set(hi) | set(wi)):
        if k not in hi:
            print(f"  + {k}")
        elif k not in wi:
            print(f"  - {k}")
        elif hi[k] != wi[k]:
            for col, o, n in zip(HDR, hi[k], wi[k]):
                if o != n:
                    print(f"  ~ {k}.{col}: {o!r} -> {n!r}")

    if a.apply:
        with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(want)
        print("\nwritten.")
        return 0
    print("\n(check only — pass --apply to write)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
