#!/usr/bin/env python3
"""Gap 4 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md.

    python3 "Project Files/Scripts/gap4_detection_method_20260928.py" [--apply]

PROBLEM. In a combined WDS+EDS point analysis the detector is chosen element by element (Ni by WDS,
Fe by EDS), and the WDS-only fields — crystal, spectrometer, detector, PHA, counting times — are keyed
by monitored element. The field recording the choice was keyed by target species, which is the wrong
grain for the fields it gates. It also cannot record the method for an element monitored only to
correct an interference (Zn in the reference example serves no target species).

CHANGE. In EPMA, SEM and SEM_Composition (TAPP-owned; Rules 2 and 4 require the same WDS/EDS field to
match across them and to change in one pass):
  * `EPMA Technique per Target Species` (EPMA) and `Technique per Target Species` (SEM,
    SEM_Composition) -> one name, `X-ray Detection Method per Monitored Element`. This also retires a
    Rule 1 name variant, and the new name no longer collides with the Group 1 `Technique` field.
  * Keyed By `target species` -> `monitored property` (defined by `Monitored Elements` in all three).
  * One shared description, which defines the two methods.
  * Unchanged in each TAPP: tiers, data type, allowed values, mode flags, literature cells.

The gap record said this field existed in EPMA only. That was wrong: SEM and SEM_Composition carry it
under the shorter name, which is why they are included here.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-28"
OLD     = {"EPMA": "EPMA Technique per Target Species",
           "SEM": "Technique per Target Species",
           "SEM_Composition": "Technique per Target Species"}
NEW     = "X-ray Detection Method per Monitored Element"
DESC    = ("The X-ray detection method used to measure the monitored element: wavelength-dispersive "
           "(WDS), in which a crystal spectrometer separates the X-rays by wavelength and a proportional "
           "counter counts them, or energy-dispersive (EDS), in which a solid-state detector sorts every "
           "photon by energy at once. Applies where a procedure uses both.")


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


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_TAPP_v", 1)[0]
        if stem not in OLD:
            continue
        rows = rows_of(os.path.join(ROOT, e["tapp"]))
        h = rows[0]
        hit = [r for r in rows[1:] if r and r[0].strip() == OLD[stem]]
        if len(hit) != 1 or hit[0][h.index("Keyed By")] != "target species":
            raise SystemExit("PREMISE: %s has no single %r keyed target species" % (stem, OLD[stem]))
        if not any(r and r[0].strip() == "Monitored Elements"
                   and r[h.index("Keyed By")].startswith("defines: monitored property") for r in rows[1:]):
            raise SystemExit("PREMISE: %s has no Monitored Elements definer (7.4a)" % stem)
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
        plan.append((e, stem, new))
        print("  %-30s -> %-26s %r -> %r" % (os.path.basename(e["tapp"]), os.path.basename(new), OLD[stem], NEW))
    if len(plan) != 3:
        raise SystemExit("PREMISE: expected 3 TAPPs, found %d" % len(plan))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, stem, new in plan:
        rel = e["tapp"]; np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h = rr[0]
        jI, jU = h.index("Keyed By"), h.index("Last Update")
        for r in rr[1:]:
            if r and r[0].strip() == OLD[stem]:
                r[0], r[1], r[jI], r[jU] = NEW, DESC, "monitored property", DATE
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  wrote %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        s = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if s in news:
            e["tapp"] = news[s]
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)          # skips: this date's README exists and is extended by hand
    return 0


sys.exit(main("--apply" in sys.argv))
