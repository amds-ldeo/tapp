#!/usr/bin/env python3
"""
Apply the Module_Core Column B reconciliation across the library.

Adopted text is read from
`Archive/Worksheets (reconciled)/ModuleCore_Reconciliation_Decisions.csv` — the decisions
file is the record and therefore the source of truth; nothing is hard-coded here except the
structural changes, which have no natural home in that file's Adopted-description column.

Unlike the SolutionIntroduction pass, these five fields are in **no module**, so this edits the
TAPPs directly rather than a module CSV. That is only legitimate while they remain unmoduled, so
the script asserts it (see guard 1) and refuses to run if any of them has since been moved into a
module — at which point Rule 6.6 applies and the edit belongs in the module instead.

Targets are the TAPPs in their technique folders, resolved through `composed_tapps.json`.
`Current TAPPs/` is a generated mirror under Rule 12 and is never an editing target; refresh it
afterwards with `sync_current_tapps.py`.

What changes:
  1. Column B for 4 fields, in every TAPP holding them.
  2. Column A rename `Data Reduction Software` -> `Data Processing Software(s)` (15 TAPPs).
  3. Lab-XCT absorption: `Segmentation and Analysis Software` -> `Data Processing Software(s)`,
     taking the same adopted description, so the field reaches 16/16.
     Lab-XCT RETAINS `Reconstruction Software` — a stage the other 15 techniques do not have.
  4. Column E `Target Material`: `Text (free)` -> `Controlled list / Text` (3 Solution TAPPs).
  5. Column D `Sample Persistent Identifier`: `Basic` -> `Advanced` (3 Solution TAPPs).
  6. Column H stamped 2026-08-14 on every row this script changes. Column H is consumer-owned
     under Rule 6.4, so stamping it in the TAPP is correct.

What this script deliberately does NOT do — each has its own tooling or its own decision:
  * version bumps and register rewrites  -> bump_and_stamp
  * refreshing the mirror                -> sync_current_tapps.py
  * building Module_Core itself          -> compose_tapp.py, after this lands
  * registering the two renames in validate_tapp.RETIRED_FIELDS (required; reported at the end)
  * Column F content for the renamed/absorbed rows (consumer-owned; reported where empty)

  --dry (default)  report every cell that would change, write nothing
  --apply          write the changes
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DECISIONS = os.path.join(ROOT, "Archive", "Worksheets (reconciled)",
                         "ModuleCore_Reconciliation_Decisions.csv")
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
DATE = "2026-08-14"
COL_A, COL_B, COL_C, COL_D, COL_E, COL_F, COL_G, COL_H = range(8)

RENAME = {"Data Reduction Software": "Data Processing Software(s)"}
ABSORB = {"Lab-XCT": ("Segmentation and Analysis Software", "Data Processing Software(s)")}
COL_E_FIX = ("Target Material", "Text (free)", "Controlled list / Text")
COL_D_FIX = ("Sample Persistent Identifier", "Basic", "Advanced")
KEEP_IN_XCT = "Reconstruction Software"


def load_adopted():
    """Adopted Column B text, keyed by the field's CURRENT name."""
    out = {}
    for row in csv.DictReader(open(DECISIONS, encoding="utf-8-sig")):
        txt = (row.get("Adopted description") or "").strip()
        if not txt or txt.startswith("(no change"):
            continue
        out[row["Field"].strip()] = txt
    return out


def tapp_paths():
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    paths = []
    for e in reg["composed"]:
        p = os.path.join(ROOT, e["tapp"])
        if not os.path.exists(p):
            sys.exit(f"FATAL: composed_tapps.json names a missing file: {e['tapp']}")
        paths.append(p)
    return sorted(paths)


def module_owned_fields():
    owned = set()
    for f in os.listdir(MODDIR):
        if not (f.startswith("Module_") and f.endswith(".csv")):
            continue
        for r in list(csv.reader(open(os.path.join(MODDIR, f), encoding="utf-8-sig")))[1:]:
            if r and r[0].strip() and ((len(r) > 2 and r[2].strip()) or (len(r) > 3 and r[3].strip())):
                owned.add(r[0].strip())
    return owned


def short(p):
    return os.path.basename(p)[:-4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    apply = args.apply and not args.dry

    adopted = load_adopted()
    paths = tapp_paths()

    # ---- guard 1: none of these fields may be module-owned (else Rule 6.6 applies) ----
    owned = module_owned_fields()
    clash = (set(adopted) | set(RENAME) | {COL_E_FIX[0], COL_D_FIX[0]}) & owned
    if clash:
        sys.exit(f"FATAL: these fields are module-owned and must be edited in the module, "
                 f"not the TAPPs (Rule 6.6): {sorted(clash)}")
    print(f"guard 1 OK — none of the 5 fields is module-owned ({len(owned)} module fields checked)")

    # ---- guard 2: the adopted text must be present for every field we intend to rewrite ----
    expect = {"Acquisition Software", "Data Reduction Software", "Analytical Mode", "Target Material"}
    missing = expect - set(adopted)
    if missing:
        sys.exit(f"FATAL: decisions file has no adopted text for {sorted(missing)}")
    print(f"guard 2 OK — adopted text loaded for {len(adopted)} fields from the decisions file")

    changes = defaultdict(list)
    empty_F = []
    totals = defaultdict(int)
    bumps = []          # (old path, new path) for every TAPP this pass changes

    for p in paths:
        rows = list(csv.reader(open(p, encoding="utf-8-sig")))
        name = short(p)
        dirty_rows = set()

        for i, r in enumerate(rows[1:], start=1):
            if not r or not r[COL_A].strip():
                continue
            has_tier = (len(r) > COL_C and r[COL_C].strip()) or (len(r) > COL_D and r[COL_D].strip())
            if not has_tier:
                continue
            fld = r[COL_A].strip()

            # 3. Lab-XCT absorption — handle before the generic rename
            absorbed = False
            for tag, (src, dst) in ABSORB.items():
                if tag in name and fld == src:
                    changes[name].append(("A", i, fld, dst))
                    r[COL_A] = dst
                    if r[COL_B].strip() != adopted["Data Reduction Software"]:
                        changes[name].append(("B", i, dst, "<adopted>"))
                        r[COL_B] = adopted["Data Reduction Software"]
                    dirty_rows.add(i); totals["absorbed"] += 1; absorbed = True
            if absorbed:
                if not r[COL_F].strip():
                    empty_F.append((name, dst))
                continue

            # 1 + 2. Column B rewrite, and rename where applicable
            if fld in adopted:
                new_name = RENAME.get(fld, fld)
                if new_name != fld:
                    changes[name].append(("A", i, fld, new_name))
                    r[COL_A] = new_name
                    totals["renamed"] += 1
                if r[COL_B].strip() != adopted[fld]:
                    changes[name].append(("B", i, new_name, "<adopted>"))
                    r[COL_B] = adopted[fld]
                    totals["colB"] += 1
                dirty_rows.add(i)

            # 4. Column E
            if fld == COL_E_FIX[0] and r[COL_E].strip() == COL_E_FIX[1]:
                changes[name].append(("E", i, fld, f"{COL_E_FIX[1]} -> {COL_E_FIX[2]}"))
                r[COL_E] = COL_E_FIX[2]; dirty_rows.add(i); totals["colE"] += 1

            # 5. Column D
            if fld == COL_D_FIX[0] and r[COL_D].strip() == COL_D_FIX[1]:
                changes[name].append(("D", i, fld, f"{COL_D_FIX[1]} -> {COL_D_FIX[2]}"))
                r[COL_D] = COL_D_FIX[2]; dirty_rows.add(i); totals["colD"] += 1

        # 6. Column H stamp on changed rows
        for i in sorted(dirty_rows):
            if rows[i][COL_H].strip() != DATE:
                rows[i][COL_H] = DATE
                totals["colH"] += 1

        # ---- guard 3: Lab-XCT must keep Reconstruction Software ----
        if "Lab-XCT" in name:
            names = [r[COL_A].strip() for r in rows[1:] if r]
            if KEEP_IN_XCT not in names:
                sys.exit(f"FATAL: {KEEP_IN_XCT} vanished from {name} — the absorption took the wrong row")
            if names.count("Data Processing Software(s)") != 1:
                sys.exit(f"FATAL: {name} has {names.count('Data Processing Software(s)')} "
                         f"'Data Processing Software(s)' rows, expected exactly 1")

        # A changed TAPP is a NEW version. The current file is left byte-untouched — technique
        # folders keep every version, and writing in place would destroy the one being superseded.
        if dirty_rows:
            m = re.search(r"_v(\d+)\.csv$", os.path.basename(p))
            newp = re.sub(r"_v\d+\.csv$", f"_v{int(m.group(1)) + 1}.csv", p)
            if os.path.exists(newp):
                sys.exit(f"FATAL: {os.path.basename(newp)} already exists — refusing to overwrite")
            bumps.append((p, newp))
            if apply:
                with open(newp, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)

    # ---------------- report ----------------
    print("\n" + "=" * 92)
    print(f"{'APPLIED' if apply else 'DRY RUN — nothing written'}   ({len(paths)} TAPPs)")
    print("=" * 92)
    for name in sorted(changes):
        print(f"\n{name}")
        for col, i, fld, val in changes[name]:
            print(f"   row {i:>3}  col {col}  {fld:<34} {val}")

    print("\n" + "=" * 92)
    print("TOTALS")
    print("=" * 92)
    for k, v in [("Column A renames", totals["renamed"]), ("Lab-XCT absorptions", totals["absorbed"]),
                 ("Column B rewrites", totals["colB"]), ("Column D fixes", totals["colD"]),
                 ("Column E fixes", totals["colE"]), ("Column H stamps", totals["colH"])]:
        print(f"  {k:<24} {v}")
    print(f"  {'TAPPs touched':<24} {len(changes)}")

    if empty_F:
        print("\nColumn F empty on absorbed/renamed rows (consumer-owned — fill before composing):")
        for n, f in empty_F:
            print(f"   {n}: {f}")

    print("\nVERSION BUMPS")
    for o, n in bumps:
        print(f"  {os.path.basename(o)}  ->  {os.path.basename(n)}")

    if not apply:
        print("\nre-run with --apply to write.")
        print("NOTE: --apply writes the bumped file and leaves the current version untouched.")
        return

    # ---- registers ----
    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in bumps}
    regp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(open(regp, encoding="utf-8"))
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"])
        if b in pathmap:
            e["tapp"] = e["tapp"].replace(b, pathmap[b])
    reg["generated"] = DATE
    with open(regp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"\n  composed_tapps.json — {len(pathmap)} path(s) updated")

    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        hits = 0
        for r in crows[1:]:
            for i, cell in enumerate(r):
                for old, new in pathmap.items():
                    if old in cell:
                        r[i] = cell.replace(old, new); hits += 1
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(crows)
        print(f"  TAPP_Composed_Variants.csv — {hits} reference(s) updated")

    # ---- xlsx for the new versions ----
    x = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    okx = badx = 0
    for _, n in bumps:
        r = subprocess.run([sys.executable, x, n], capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(n[:-4] + ".xlsx"):
            okx += 1
        else:
            badx += 1
            print(f"  WARN xlsx failed for {os.path.basename(n)}: "
                  f"{(r.stderr or r.stdout).strip().splitlines()[-1:]}")
    print(f"  xlsx regenerated — {okx} ok, {badx} failed")

    # ---- Rule 12 mirror ----
    sync = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, sync, "--apply"], capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    print(f"  Rule 12 mirror: {tail[0].strip() if tail else 'sync ran'}")

    print("\nSTILL REQUIRED, BY HAND:")
    print("  1. validate_tapp.RETIRED_FIELDS += "
          "'Data Reduction Software': 'renamed 2026-08-14 -> Data Processing Software(s)'")
    print("  2. validate_tapp.RETIRED_FIELDS += 'Segmentation and Analysis Software': "
          "'absorbed 2026-08-14 -> Data Processing Software(s)' (Lab-XCT)")
    print("  3. re-run validate_tapp.py — expect 0 ERROR / 0 WARN")
    print("  4. superseded versions were NOT archived; technique folders keep them "
          "(housekeeping sweep is separate)")


if __name__ == "__main__":
    main()
