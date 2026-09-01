#!/usr/bin/env python3
"""Recompose and bump every consumer of a module, stamping Last Update on the rows it owns.

  python3 bump_for_module_20260901.py <ModuleName> [--apply]

Supersedes bump_for_module_20260827.py, which set only `generated` and left every `tapp` path in
composed_tapps.json naming the file it had just moved into Superseded TAPPs/. That is the mechanism
behind the six stale registry entries found on 2026-09-01: compose_tapp writes to the recorded path,
so the next pass edits a superseded copy and reports MATCH. validate_tapp now catches it
(`register-stale-tapp-path`, ERROR). COPY THIS SCRIPT, NOT THE 2026-08-27 ONE.

Composes to the NEW version path so each superseded copy is the file as it was published. Does NOT
handle a field RENAME — compose matches rows by field name, so a renamed module field is ADDED while
the old row survives; see bump_samplingunitselection_20260901.py for that case.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-01"


def flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def main(module, apply=False):
    mrows = list(csv.reader(open(os.path.join(
        ROOT, "Claude Skills for TAPP", "modules", "Module_%s.csv" % module),
        newline="", encoding="utf-8-sig")))
    FIELDS = {r[0].strip() for r in mrows[1:] if r and r[0].strip()}
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == module for m in e["modules"]):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-36s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("  %d consumer(s), %d module field(s)" % (len(plan), len(FIELDS)))
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    for e, rel, new in plan:
        p = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", os.path.join(ROOT, new)],
                           cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, p.stdout[-1200:], p.stderr[-600:]))
        np_ = os.path.join(ROOT, new)
        rows = list(csv.reader(open(np_, newline="", encoding="utf-8-sig")))
        h = rows[0]; iu = h.index("Last Update"); n = 0
        for r in rows[1:]:
            if r and r[0].strip() in FIELDS:
                while len(r) <= iu:
                    r.append("")
                r[iu] = DATE; n += 1
        if n != len(FIELDS):
            raise SystemExit("%s: stamped %d of %d" % (new, n, len(FIELDS)))
        with open(np_, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  composed %s (%d row(s) stamped)" % (os.path.basename(new), n))

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        e["tapp"] = new                      # the line bump_for_module_20260827.py was missing
    # and advance the module's recorded version, or validate_tapp reports module-version-drift
    mver = json.load(open(os.path.join(
        ROOT, "Claude Skills for TAPP", "modules", "Module_%s.json" % module),
        encoding="utf-8"))["version"]
    for e, _, _ in plan:
        for m in e["modules"]:
            if m["name"] == module:
                m["version"] = mver
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced" % len(plan))
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:90])


if __name__ == "__main__":
    main(sys.argv[1], "--apply" in sys.argv)
