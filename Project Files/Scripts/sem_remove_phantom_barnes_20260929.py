#!/usr/bin/env python3
"""SEM TAPPs: remove three literature columns that describe no procedure in their paper (2026-09-29).

    python3 "Project Files/Scripts/sem_remove_phantom_barnes_20260929.py" [--apply]

Three Barnes+2025 columns record procedures the paper does not contain, as their own Additional Notes say:
  * BSE Imaging (FEI Quanta 3D DualBeam + Helios DualBeam, NASA JSC): the paper's BSE mosaics were made on
    a Hitachi TM4000plus at the University of Arizona, and no JSC BSE imaging is described.
  * TEM Sample Preparation (FEI Helios G4 DualBeam, NASA JSC) and (FEI Helios 660 G3, NASA JSC): the paper
    has no TEM work and no FIB preparation. That preparation is in the companion paper, Zega+2025, which
    has its own columns.
Every field in them reads `N` or `N/A` apart from identification cells copied from the paper's other
work. They are removed from SEM, SEM_Imaging and SEM_FIBSEM (SEM_Composition does not carry them).
Barnes+2025's JSC SEM-EDS mapping column stays: the paper describes that work (p.11, Extended Data Fig. 8).
The user decided the removal on 2026-09-29.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
PHANTOM = [
  "Barnes et al. 2025 | Bennu asteroid particles (OSIRIS-REx) | BSE Imaging (FEI Quanta 3D DualBeam + Helios DualBeam, NASA JSC)",
  "Barnes et al. 2025 | Bennu asteroid particles (OSIRIS-REx) | TEM Sample Preparation (FEI Helios G4 DualBeam, NASA JSC)",
  "Barnes et al. 2025 | Bennu asteroid particles (OSIRIS-REx) | TEM Sample Preparation (FEI Helios 660 G3, NASA JSC)",
]
TAPPS = {"SEM_TAPP_v": 3, "SEM_Imaging_TAPP_v": 1, "SEM_FIBSEM_TAPP_v": 2}


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def edit(rr, expect):
    h = rr[0]; s = h.index("Literature Assessment")
    drop = [j for j in range(s + 1, len(h)) if " ".join(h[j].split()) in PHANTOM]
    if len(drop) != expect:
        raise SystemExit("PREMISE: expected %d phantom columns, found %d" % (expect, len(drop)))
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for j in drop:
        rv = by["Reported Variables and Units"][j]
        if "not described in the paper" not in rv:
            raise SystemExit("PREMISE: %r does not say it is undescribed: %r" % (h[j], rv[:80]))
    keep = [j for j in range(max(len(r) for r in rr)) if j not in drop]
    return [[r[j] for j in keep if j < len(r)] for r in rr], len(drop)


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for pre, n in TAPPS.items():
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(pre))
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        rr, k = edit(rows_of(os.path.join(ROOT, rel)), n)
        s = rr[0].index("Literature Assessment")
        print("  %s -> %s: %d columns removed, %d literature columns left" % (os.path.basename(rel), os.path.basename(new),
                                                                              k, len(rr[0]) - s - 1))
        plan.append((e, rel, new, n))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for e, rel, new, n in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), n)[0])
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
        rp = os.path.join(ROOT, "composed_tapps.json")
        reg = json.load(io.open(rp, encoding="utf-8"))
        for x in reg["composed"]:
            if x["tapp"] == rel:
                x["tapp"] = new
        with io.open(rp, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
