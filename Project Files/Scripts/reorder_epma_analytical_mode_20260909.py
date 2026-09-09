#!/usr/bin/env python3
"""
reorder_epma_analytical_mode_20260909.py
-----------------------------------------
Follow-up to harmonise_analytical_mode_colf_20260909.py: put EPMA's Analytical Mode
Column F members into mode flag column order.

Rule 3: "Allowed values: exactly the mode flag column labels defined in Phase 0 for
that TAPP". After the harmonisation, 12 of the 13 flag-bearing TAPPs list their
members in flag order. EPMA is the last one out:

    flags : EDS Point Analysis | EDS Mapping | WDS Point Analysis | WDS Mapping
    col F : WDS Point Analysis | EDS Point Analysis | WDS Mapping | EDS Mapping

Set-identical, so this changes no vocabulary — only the order in which the same four
members are written. Held back from the 2026-09-09 harmonisation because reordering
was not part of the change that was reviewed there; requested separately afterwards.

The new order is READ FROM THE HEADER, not hardcoded, so the file cannot drift from
its own mode flag columns. The script asserts the set is unchanged before writing.

EPMA_TAPP_v64.csv -> v65. Column H stamped, consistent with the harmonisation:
Column F order is part of the field's registered allowed content.
"""

import csv, json, os, shutil, subprocess, sys

ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL   = "EPMA/EPMA_TAPP_v64.csv"
NEW   = "EPMA/EPMA_TAPP_v65.csv"
ITEM  = "Analytical Mode"
STAMP = "2026-09-09"
XLSX  = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")


def main(apply=False):
    src  = os.path.join(ROOT, REL)
    rows = list(csv.reader(open(src, newline="", encoding="utf-8-sig")))
    hdr  = rows[0]
    iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
    flags  = [c.strip() for c in hdr[10:hdr.index("Literature Assessment")]]

    row = next(r for r in rows[1:] if r and r[0].strip() == ITEM)
    cur = [p.strip() for p in row[iF].split("|")]
    if sorted(cur) != sorted(flags):
        print("  ABORT: member set does not match mode flags\n     flags: %s\n     colF : %s"
              % (flags, cur)); return 1
    if cur == flags:
        print("  already in flag order — nothing to do"); return 0

    nxt = " | ".join(flags)              # the header IS the order
    print("  EPMA_TAPP v64 -> v65")
    print("      was: %s" % " | ".join(cur))
    print("      now: %s" % nxt)
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    row[iF], row[iU] = nxt, STAMP
    dst = os.path.join(ROOT, NEW)
    with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)

    sup = os.path.join(ROOT, "Superseded TAPPs", STAMP)
    os.makedirs(sup, exist_ok=True)
    for f in (src, src[:-4] + ".xlsx"):
        if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
    p = subprocess.run([sys.executable, XLSX, NEW], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit("xlsx failed\n%s" % p.stderr[-600:])

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(open(rp, encoding="utf-8"))
    n = 0
    for e in reg["composed"]:
        if e["tapp"] == REL: e["tapp"] = NEW; n += 1
    reg["generated"] = STAMP
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  wrote %s; registry advanced (%d)" % (os.path.basename(NEW), n))

    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print(p.stdout.strip()[-200:])
    return 0


sys.exit(main("--apply" in sys.argv))
