#!/usr/bin/env python3
"""Rename Lab-XCT `Detector Type` -> `X-ray Detector Type`.

Clears the two COLE_NAME_VARIANT_TRIAGED entries against SEM's `BSE Detector Type` and
`SE Detector Type`. The field is TAPP-owned (no module), appears in no other TAPP, and is
cross-referenced nowhere, so the rename touches exactly one cell and changes no meaning.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
DATE = "2026-08-27"
OLD, NEW = "Detector Type", "X-ray Detector Type"

def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    entry = next(e for e in reg["composed"] if "Lab-XCT" in e["tapp"])
    rel = entry["tapp"]
    rows = list(csv.reader(open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
    hdr = rows[0]; upd = hdr.index("Last Update")
    n = 0
    for r in rows[1:]:
        if r and r[0].strip() == OLD:
            r[0] = NEW
            while len(r) <= upd: r.append("")
            r[upd] = DATE
            n += 1
    if n != 1:
        raise SystemExit("expected exactly one '%s' row, found %d" % (OLD, n))
    newrel = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
    print("  %s -> %s  (1 row renamed)" % (os.path.basename(rel), os.path.basename(newrel)))
    if not apply:
        print("(dry run — pass --apply to write)"); return

    with open(os.path.join(ROOT, newrel), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    entry["tapp"] = newrel
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")

    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        ob, nb = os.path.basename(rel), os.path.basename(newrel)
        for r in crows[1:]:
            for i, c in enumerate(r):
                if ob in c: r[i] = c.replace(ob, nb)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh: csv.writer(fh).writerows(crows)

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    old = os.path.join(ROOT, rel)
    shutil.move(old, os.path.join(sup, os.path.basename(old)))
    x = old[:-4] + ".xlsx"
    if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))

    gen = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    r = subprocess.run([sys.executable, gen, newrel], cwd=ROOT, capture_output=True, text=True)
    print("  xlsx:", (r.stdout.strip().splitlines() or ["(none)"])[-1][:80], r.stderr[:200])
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (r.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__ == "__main__":
    main("--apply" in sys.argv)
