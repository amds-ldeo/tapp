#!/usr/bin/env python3
"""Stamp Last Update on rows changed by the 2026-08-12 pass, then bump every changed TAPP.

The changed-row list comes from Survey_ColI_Findings_2026-08-12.csv, which recorded TAPP:row for
every finding while the library was still in its pre-edit state, plus the two follow-on edits made
after that file was built. Row numbers are stable because no row was added or removed.

Column H (Last Update) is consumer-owned under Rule 6.4, so stamping it in the TAPP is correct even
on module-owned rows — recomposition will not revert it.

Classes deliberately excluded: class 2 (Sampling Unit nesting, deferred), class 8 (Number of
Digestion Steps, no file change), class 9 (adjudicated false positives).

  --dry    report what would change
  --apply  stamp, bump versions, and rewrite the registers
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # library root: this script lives in "Project Files/Scripts/"
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

DATE = "2026-08-12"
COL_H = 7
FINDINGS = os.path.join(ROOT, "Claude Skills for TAPP", "analysis",
                        "Survey_ColI_Findings_2026-08-12.csv")
EXCLUDE_CLASS_PREFIX = ("2 ", "8 ", "9 ")

# Edits made after the findings CSV was built: the Isobaric Interference Corrections Applied
# cross-reference reword in the 6 LA TAPPs.
EXTRA_FIELDS = {"Isobaric Interference Corrections Applied"}

# Module versions bumped by this pass (Rule 6 — a module content change is a module version).
MODULE_BUMPS = {"ReportingCore": ("3", "4"), "MCICPMS": ("3", "4")}


def changed_rows():
    """{tapp basename: {row numbers}} from the findings table."""
    out = {}
    for r in csv.DictReader(open(FINDINGS, encoding="utf-8-sig")):
        cls = (r.get("Class") or "").strip()
        if not cls or cls.startswith(EXCLUDE_CLASS_PREFIX):
            continue
        for tok in (r.get("TAPPs") or "").split(";"):
            tok = tok.strip()
            if not tok or ":" not in tok:
                continue
            stem, _, row = tok.rpartition(":")
            if not row.isdigit():
                continue
            out.setdefault(stem.strip(), set()).add(int(row))
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # Findings records stems like 'LA-Q-ICP-MS_v11' (the _TAPP and .csv stripped at build time).
    by_stem = changed_rows()
    renames, total_stamped = [], 0

    for path in V.discover(ROOT):
        base = os.path.basename(path)
        stem = base.replace("_TAPP", "").replace(".csv", "")
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        want = set(by_stem.get(stem, set()))
        for n, r in enumerate(rows[1:], start=2):
            if r and r[0].strip() in EXTRA_FIELDS:
                want.add(n)
        if not want:
            continue

        stamped = []
        for n in sorted(want):
            if n - 1 >= len(rows) or not rows[n - 1] or len(rows[n - 1]) <= COL_H:
                print(f"  WARN {base}: row {n} out of range or short — skipped")
                continue
            row = rows[n - 1]
            if row[COL_H].strip() != DATE:
                row[COL_H] = DATE
                stamped.append((n, row[0].strip()))
        total_stamped += len(stamped)

        m = re.search(r"_v(\d+)\.csv$", base)
        newver = int(m.group(1)) + 1
        newbase = re.sub(r"_v\d+\.csv$", f"_v{newver}.csv", base)
        newpath = os.path.join(os.path.dirname(path), newbase)
        renames.append((path, newpath, len(stamped)))

        print(f"  {base}  ->  {newbase}   ({len(stamped)} row(s) stamped)")
        for n, f in stamped[:4]:
            print(f"        r{n} {f}")
        if len(stamped) > 4:
            print(f"        … +{len(stamped) - 4} more")

        if args.apply:
            with open(newpath, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{len(renames)} TAPP(s) bumped, {total_stamped} row(s) stamped {DATE}")

    if not args.apply:
        print("(dry run — pass --apply to write)")
        return

    # Registers: composed_tapps.json paths, module versions, and the module register.
    reg_path = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(open(reg_path))
    pathmap = {os.path.basename(o): os.path.basename(n) for o, n, _ in renames}
    for entry in reg["composed"]:
        b = os.path.basename(entry["tapp"])
        if b in pathmap:
            entry["tapp"] = entry["tapp"].replace(b, pathmap[b])
        for mod in entry["modules"]:
            if mod["name"] in MODULE_BUMPS and mod.get("version") == MODULE_BUMPS[mod["name"]][0]:
                mod["version"] = MODULE_BUMPS[mod["name"]][1]
    reg["generated"] = DATE
    with open(reg_path, "w") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"  updated composed_tapps.json ({len(pathmap)} path(s), module versions bumped)")

    mr = os.path.join(ROOT, "Project Files", "Registers & Planning",
                      "TAPP_Module_Register.csv")
    mrows = list(csv.reader(open(mr, newline="", encoding="utf-8-sig")))
    vi = mrows[0].index("Version")
    for r in mrows[1:]:
        if r and r[0].strip() in MODULE_BUMPS and r[vi].strip() == MODULE_BUMPS[r[0].strip()][0]:
            r[vi] = MODULE_BUMPS[r[0].strip()][1]
            print(f"  module register: {r[0]} -> v{r[vi]}")
    with open(mr, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(mrows)

    cv = os.path.join(ROOT, "Project Files", "Registers & Planning",
                      "TAPP_Composed_Variants.csv")
    crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
    for r in crows[1:]:
        for i, cell in enumerate(r):
            for old, new in pathmap.items():
                if old in cell:
                    r[i] = cell.replace(old, new)
    with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(crows)
    print("  updated TAPP_Composed_Variants.csv")

    # Retire the superseded CSVs and their xlsx into a dated folder.
    sup = os.path.join(ROOT, f"Superseded TAPPs ({DATE})")
    os.makedirs(sup, exist_ok=True)
    for old, _, _ in renames:
        shutil.move(old, os.path.join(sup, os.path.basename(old)))
        oldx = old[:-4] + ".xlsx"
        if os.path.exists(oldx):
            shutil.move(oldx, os.path.join(sup, os.path.basename(oldx)))
    print(f"  moved {len(renames)} superseded CSV(s) + xlsx to {os.path.basename(sup)}/")

    # Rule 12 — a version bump invalidates the shareable mirror, so refresh it in the same pass.
    # Doing it here rather than leaving it to the operator is the point: `validate_tapp.py` reports a
    # stale mirror at WARN, and the whole reason for the folder is that it can be handed over as-is.
    sync = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    if os.path.exists(sync):
        import subprocess
        r = subprocess.run([sys.executable, sync, "--apply"], capture_output=True, text=True)
        tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] 
        print(f"  Rule 12 mirror: {tail[0].strip() if tail else 'sync ran'}")
        if r.returncode:
            print(f"  WARN mirror sync failed: {r.stderr.strip().splitlines()[-1:]}")
    else:
        print("  WARN sync_current_tapps.py not found — refresh 'Current TAPPs/' manually (Rule 12)")


if __name__ == "__main__":
    main()
