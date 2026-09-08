#!/usr/bin/env python3
"""Fix the `Sequence` description, which denies applicability to X-ray mapping.

The cell read: "Order in which spectrometer assignments are acquired during point analysis. Not
applicable to X-ray mapping, where all assigned spectrometers collect simultaneously at each pixel."

Neuman et al. 2025 (extracted into EPMA v62 on 2026-09-08) IS X-ray mapping and DOES acquire in two
passes: "Two passes were used to collect X-ray intensities for Mg, Al, Fe, Ca, and Ti in pass 1, and
Na, Si, Mn, K, and Cr in pass 2." Both halves of the old sentence are true separately — within one pass
the fixed spectrometers do collect simultaneously at each pixel — but ten elements on five fixed
spectrometers requires the map to be run twice. The description asserted a non-applicability the
evidence disproves.

`Sequence` is TAPP-owned (check_field_ownership.py: "TAPP-owned (checked 14 modules)") and its
description is byte-identical in all three carriers, so all three are updated together to keep Column B
uniform under Rule 7.8.9. Column I is NOT touched: re-keying `Sequence` to `acquisition pass` belongs
to the acquisition-pass proposal, not to a description fix.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-08"

OLD = ("Order in which spectrometer assignments are acquired during point analysis. Not applicable to "
       "X-ray mapping, where all assigned spectrometers collect simultaneously at each pixel.")
NEW = ("Order in which spectrometer assignments are acquired, and — where the element suite exceeds the "
       "number of spectrometers — the passes the acquisition is divided into. Within a single pass all "
       "assigned spectrometers collect simultaneously, including at every pixel in X-ray mapping; a "
       "suite larger than the spectrometer count therefore requires the acquisition to be run more than "
       "once, each pass covering a different subset of elements.")

TARGETS = ["EPMA/EPMA_TAPP_v62.csv", "SEM/SEM_TAPP_v60.csv", "SEM/SEM_Composition_TAPP_v59.csv"]


def main(apply=False):
    plan = [(t, re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), t)) for t in TARGETS]
    for a, b in plan:
        print("  %-38s -> %s" % (os.path.basename(a), os.path.basename(b)))
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    for old, new in plan:
        src, dst = os.path.join(ROOT, old), os.path.join(ROOT, new)
        shutil.copy2(src, dst)
        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        iu = rows[0].index("Last Update")
        n = 0
        for r in rows[1:]:
            if r and r[0].strip() == "Sequence":
                if r[1].strip() != OLD:
                    raise SystemExit("%s: unexpected description %r" % (new, r[1][:80]))
                r[1] = NEW
                r[iu] = DATE
                n += 1
        if n != 1:
            raise SystemExit("%s: expected 1 Sequence row, found %d" % (new, n))
        with open(dst, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
        print("  updated", os.path.basename(new))

    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    m = dict(plan)
    for e in reg["composed"]:
        if e["tapp"] in m:
            e["tapp"] = m[e["tapp"]]
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for old, new in plan:
        o = os.path.join(ROOT, old)
        for f in (o, o[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
    print("  registry: %d path(s) advanced" % len(plan))
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])


if __name__ == "__main__":
    main("--apply" in sys.argv)
