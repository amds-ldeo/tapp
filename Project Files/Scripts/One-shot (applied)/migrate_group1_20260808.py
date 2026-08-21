#!/usr/bin/env python3
"""
migrate_group1_20260808.py

Migrates Group 1 in all production TAPPs from copied content to composed content.

After this runs, Group 1 in every TAPP is a build output of
`Claude Skills for TAPP/modules/Module_Group1.csv`. Per Rule 6.6 those rows must
no longer be hand-edited: edit the module and recompose.

What changes
------------
Per TAPP, Group 1 only:
  B Description        <- module (the reconciled text)
  C/D Tiers            <- module (corrects the Funding Source outlier in 3 TAPPs)
  E Data Type          <- module
  field order          <- module order
  sentinel column      <- cleared on data rows, N on the group header

What is preserved
-----------------
  A Metadata Item, F Example, G Comments, H Last Update, mode flags,
  and every literature assessment column — matched by field name.
  Groups 2-6 are untouched and are verified byte-identical after composition.

Verification performed per file, before anything is written
----------------------------------------------------------
  1. row count unchanged
  2. column count unchanged on every row
  3. Groups 2-6 byte-identical
  4. changed columns confined to {B, C, D, E, sentinel}
  5. Group 1 field set unchanged (composition refuses to drop fields anyway)
A file failing any check is skipped and reported; the rest still proceed.

Version policy
--------------
No version bump. The migration changes how Group 1 content is maintained, not what
any procedure means: descriptions are reconciled to the best existing text in the
library, and the one tier correction restores the documented template value.

Usage
-----
    python3 migrate_group1_20260808.py --dry-run
    python3 migrate_group1_20260808.py
"""

from __future__ import annotations

import csv
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
MODULE_CSV = os.path.join(ROOT, "Claude Skills for TAPP", "modules", "Module_Group1.csv")
MANIFEST = os.path.join(ROOT, "composed_tapps.json")
BACKUP = os.path.join(ROOT, ".migration_backup_group1_20260808")

COL_ITEM = 0
SENTINEL = "Literature Assessment"


def find_tapps():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {"unpacked_tapp", "Pre-VIM3 Reference Archive (2026-07-24)"}
                       and not d.startswith(".")]
        for fn in filenames:
            if re.search(r"_TAPP_v\d+(\.\d+)?\.csv$", fn):
                out.append(os.path.join(dirpath, fn))
    latest = {}
    for p in out:
        key = os.path.basename(p).rsplit("_v", 1)[0]
        ver = float(re.search(r"_v(\d+(?:\.\d+)?)\.csv$", p).group(1))
        if key not in latest or ver > latest[key][0]:
            latest[key] = (ver, p)
    return [v[1] for v in sorted(latest.values(), key=lambda x: x[1])]


def read(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def group2_onward(rows):
    """Slice from the '2. Samples' header to end — must be identical after composition."""
    for i, r in enumerate(rows):
        if r and r[COL_ITEM].strip().startswith("2. "):
            return rows[i:]
    return None


def group1_fields(rows):
    out, inside = [], False
    for r in rows[1:]:
        a = r[COL_ITEM].strip() if r else ""
        if not a:
            continue
        if re.match(r"^1\.\s", a):
            inside = True
            continue
        if re.match(r"^\d+\.\s", a):
            break
        if inside:
            out.append(a)
    return out


def verify(before, after, sentinel_idx):
    """Return list of problems; empty means the composition is safe to write."""
    problems = []
    if len(before) != len(after):
        problems.append(f"row count {len(before)} -> {len(after)}")
        return problems
    for i, (a, b) in enumerate(zip(before, after)):
        if len(a) != len(b):
            problems.append(f"column count changed on row {i+1}")
            return problems
    if group2_onward(before) != group2_onward(after):
        problems.append("Groups 2-6 are not byte-identical")
    if set(group1_fields(before)) != set(group1_fields(after)):
        problems.append("Group 1 field set changed")

    allowed = {1, 2, 3, 4} | ({sentinel_idx} if sentinel_idx is not None else set())
    # Field order changes, so compare Group 1 by field name rather than by row.
    def idx(rows):
        return {r[COL_ITEM].strip(): r for r in rows[1:]
                if r and r[COL_ITEM].strip() and not re.match(r"^\d+\.\s", r[COL_ITEM].strip())}
    A, B = idx(before), idx(after)
    for name in A.keys() & B.keys():
        for i, (x, y) in enumerate(zip(A[name], B[name])):
            if x != y and i not in allowed:
                problems.append(f"out-of-scope change in column {i} of {name!r}")
    return problems


def main():
    dry = "--dry-run" in sys.argv
    tapps = find_tapps()
    print(f"{len(tapps)} TAPPs found\n")

    if not dry:
        os.makedirs(BACKUP, exist_ok=True)

    ok, skipped, records = [], [], []
    for p in tapps:
        rel = os.path.relpath(p, ROOT)
        name = os.path.basename(p)
        tmp = os.path.join(BACKUP if not dry else "/tmp", name + ".composed")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)

        r = subprocess.run([sys.executable, COMPOSE, "--source", p,
                            "--module", "Group1", "--out", tmp],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            skipped.append((rel, f"compose failed: {r.stdout.strip()[-200:]}"))
            continue

        before, after = read(p), read(tmp)
        sidx = next((i for i, h in enumerate(before[0]) if h.strip() == SENTINEL), None)
        problems = verify(before, after, sidx)
        if problems:
            skipped.append((rel, "; ".join(problems)))
            continue

        # Count semantic changes by field name, not by row position — Group 1 is
        # reordered to module order, so a positional count would report every
        # shifted cell as changed.
        def by_name(rows):
            return {r[COL_ITEM].strip(): r for r in rows[1:]
                    if r and r[COL_ITEM].strip()
                    and not re.match(r"^\d+\.\s", r[COL_ITEM].strip())}
        A, B = by_name(before), by_name(after)
        changed = sum(1 for n in A.keys() & B.keys()
                      for x, y in zip(A[n], B[n]) if x != y)
        reordered = [r[COL_ITEM].strip() for r in before[1:]] != \
                    [r[COL_ITEM].strip() for r in after[1:]]
        ok.append((rel, changed, reordered))
        if not dry:
            shutil.copy2(p, os.path.join(BACKUP, name))
            shutil.move(tmp, p)
            records.append({"tapp": rel, "modules": [{"name": "Group1", "version": "1"}]})
        else:
            os.remove(tmp)

    print("MIGRATED" if not dry else "WOULD MIGRATE")
    for rel, n, reord in ok:
        print(f"   {n:>4} cells{'  +reordered' if reord else '             '}   {rel}")
    if skipped:
        print("\nSKIPPED (verification failed — file left unchanged)")
        for rel, why in skipped:
            print(f"   {rel}\n      {why}")

    if not dry and records:
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump({
                "generated": datetime.date.today().isoformat(),
                "note": ("TAPPs whose listed groups are composed build outputs. Per Rule 6.6 the "
                         "composed rows must not be hand-edited — edit the module and recompose "
                         "with scripts/compose_tapp.py. Verify with --check."),
                "composed": sorted(records, key=lambda x: x["tapp"]),
            }, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\nprovenance written to {os.path.relpath(MANIFEST, ROOT)}")
        print(f"backups in {os.path.relpath(BACKUP, ROOT)}/")

    print(f"\n{'=' * 76}")
    print(f"  {len(ok)} migrated, {len(skipped)} skipped, "
          f"{sum(n for _, n, _ in ok)} cells total")
    print("=" * 76)
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
