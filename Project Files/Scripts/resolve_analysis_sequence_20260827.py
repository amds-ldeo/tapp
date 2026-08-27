#!/usr/bin/env python3
"""Resolve the `Analysis Sequence` D-tier divergence: Solution D=Read-Only -> D=Editable.

The divergence was recorded as knowingly unresolved on 2026-08-08, when the three Solution tables
still carried their own wording (inherited from `Sample Sequence Design`). The 2026-08-26 merge of
the 26 ICP-MS descriptions made Column B identical across all nine TAPPs, and that shared text says:

    "Adjustments must maintain the bracketing strategy defined in the procedure."

A sentence that constrains how the analyst may adjust presupposes that the analyst may adjust, which
is the definition of D=Editable. So the shared description now contradicts D=Read-Only, and the
question the 2026-08-08 entry left open is answered by the field's own text rather than by majority.

The field is TAPP-owned (not in Module_ICPMS), so this edits the three tables directly; no
recomposition is involved.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
DATE = "2026-08-27"
FIELD = "Analysis Sequence"

def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    targets = [e for e in reg["composed"] if os.path.basename(e["tapp"]).startswith("Solution_")]
    if len(targets) != 3: raise SystemExit("expected 3 Solution TAPPs, found %d" % len(targets))
    renames = []
    for e in targets:
        rel = e["tapp"]
        rows = list(csv.reader(open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; di = h.index("Analysis-Level Tier"); ui = h.index("Last Update")
        row = next((r for r in rows[1:] if r and r[0].strip() == FIELD), None)
        if row is None: raise SystemExit("no %s row in %s" % (FIELD, rel))
        if row[di].strip() != "Read-Only":
            raise SystemExit("%s: expected D=Read-Only, found %r" % (rel, row[di]))
        row[di] = "Editable"
        while len(row) <= ui: row.append("")
        row[ui] = DATE
        newrel = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        print("  %-34s D=Read-Only -> Editable   -> %s" % (os.path.basename(rel), os.path.basename(newrel)))
        renames.append((e, rel, newrel, rows))
    if not apply:
        print("(dry run — pass --apply to write)"); return

    for e, rel, newrel, rows in renames:
        with open(os.path.join(ROOT, newrel), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        e["tapp"] = newrel
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")

    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        pm = {os.path.basename(o): os.path.basename(n) for _, o, n, _ in renames}
        for r in crows[1:]:
            for i, c in enumerate(r):
                for o, n in pm.items():
                    if o in c: r[i] = c.replace(o, n)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh: csv.writer(fh).writerows(crows)

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    gen = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, rel, newrel, _ in renames:
        old = os.path.join(ROOT, rel); shutil.move(old, os.path.join(sup, os.path.basename(old)))
        x = old[:-4] + ".xlsx"
        if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
        subprocess.run([sys.executable, gen, newrel], cwd=ROOT, capture_output=True, text=True)
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (r.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__ == "__main__":
    main("--apply" in sys.argv)
