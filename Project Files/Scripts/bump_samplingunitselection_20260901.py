#!/usr/bin/env python3
"""Release the SamplingUnitSelection rename: recompose, bump and publish all 13 consumers.

Modelled on bump_for_module_20260827.py, with two differences that this pass forced:

1. **A field RENAME cannot be expressed by composition.** compose_tapp matches module rows to TAPP
   rows by field name, so a renamed module field is ADDED while the old row survives — both rows end
   up in the TAPP and the consumer-owned Column F of the old row is orphaned. Column A is therefore
   renamed in the new version BEFORE composing it.

2. **The registry paths are updated.** bump_for_module_20260827.py set only `generated` and left
   every `tapp` path naming the file it had just moved into Superseded TAPPs/. That is the mechanism
   behind the six stale entries found on 2026-09-01: compose_tapp writes to the recorded path, so the
   next pass edits a superseded copy and reports MATCH. validate_tapp now catches it
   (`register-stale-tapp-path`, ERROR); this script no longer causes it.

Column G is repaired explicitly for the same reason 2 exists: stamp_source_comment only ever fills an
EMPTY Column G, so a module rename leaves `Source: <old> module` behind and recomposition reports MATCH.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-01"
MODULE = "SamplingUnitSelection"
OLD_FIELD, NEW_FIELD = "Target Selection Criteria", "Sampling Unit Selection Criteria"
OLD_STAMP, NEW_STAMP = "Source: Target Selection module", "Source: Sampling Unit Selection module"
FIELDS = {NEW_FIELD, "Pre-Analysis Imaging and Screening"}


def flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == MODULE for m in e["modules"]):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-36s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("  %d consumer(s)" % len(plan))
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    for e, rel, new in plan:
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, new)
        shutil.copy2(src, dst)

        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        hit = [r for r in rows if r and r[0].strip() == OLD_FIELD]
        if len(hit) != 1:
            raise SystemExit("%s: expected 1 '%s' row, found %d" % (new, OLD_FIELD, len(hit)))
        hit[0][0] = NEW_FIELD
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)

        p = subprocess.run([sys.executable, COMPOSE, "--source", dst] + flags(e["modules"])
                           + ["--out", dst], cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (new, p.stdout[-1200:], p.stderr[-600:]))

        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        h = rows[0]; iu = h.index("Last Update"); ic = h.index("Comments"); n = 0
        for r in rows[1:]:
            if not r or r[0].strip() not in FIELDS:
                continue
            while len(r) <= max(iu, ic):
                r.append("")
            if r[ic].strip() == OLD_STAMP:
                r[ic] = NEW_STAMP
            if r[ic].strip() != NEW_STAMP:
                raise SystemExit("%s: %s stamp is %r" % (new, r[0], r[ic]))
            r[iu] = DATE; n += 1
        if n != len(FIELDS):
            raise SystemExit("%s: stamped %d of %d" % (new, n, len(FIELDS)))
        if any(r and r[0].strip() == OLD_FIELD for r in rows):
            raise SystemExit("%s: old field name survived composition" % new)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  composed %s (%d rows stamped)" % (os.path.basename(new), n))

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        e["tapp"] = new                      # <-- the line bump_for_module_20260827.py was missing
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced, generated=%s" % (len(plan), DATE))

    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:90])


if __name__ == "__main__":
    main("--apply" in sys.argv)
