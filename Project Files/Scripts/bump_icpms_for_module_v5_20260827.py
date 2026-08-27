#!/usr/bin/env python3
"""Recompose and bump the 9 ICP-MS TAPPs after Module_ICPMS v4 -> v5 (Analysis Sequence added).

The only cell composition changes in each TAPP is the Column G provenance stamp
`Source: ICP-MS module` on the `Analysis Sequence` row -- verified by `recompose_all --check`
before this ran, which reported "1 cell(s) would change" for each of the nine and MATCH for the
seven non-ICP-MS TAPPs. All six module-owned columns already held the module's values.

`Last Update` is stamped to the pass date on that row, following the precedent set when
Module_ICPMS v1 took over its original 13 byte-identical fields (Torch Depth still carries
2026-08-25, the v1 extraction date).

Composition writes straight to the NEW version path, so the superseded copy is the file as it was
published. compose_tapp.record_composition carries each composed_tapps.json entry forward.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
DATE = "2026-08-27"
FIELD = "Analysis Sequence"

def module_flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out

def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    targets = [e for e in reg["composed"] if "ICP" in os.path.basename(e["tapp"])]
    if len(targets) != 9: raise SystemExit("expected 9 ICP-MS TAPPs, found %d" % len(targets))
    plan = []
    for e in targets:
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-34s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    if not apply:
        print("(dry run — pass --apply to write)"); return

    for e, rel, new in plan:
        cmd = ([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
               + module_flags(e["modules"]) + ["--out", os.path.join(ROOT, new)])
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed for %s:\n%s\n%s" % (rel, p.stdout[-1500:], p.stderr[-800:]))
        # Stamp Last Update on the row that just became module-owned.
        np_ = os.path.join(ROOT, new)
        rows = list(csv.reader(open(np_, newline="", encoding="utf-8-sig")))
        h = rows[0]; ui = h.index("Last Update"); ci = h.index("Comments")
        row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
        while len(row) <= max(ui, ci): row.append("")
        if row[ci].strip() != "Source: ICP-MS module":
            raise SystemExit("%s: provenance stamp missing after composition (got %r)" % (new, row[ci]))
        row[ui] = DATE
        with open(np_, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  composed %s" % os.path.basename(new))

    pm = {os.path.basename(o): os.path.basename(n) for _, o, n in plan}
    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in crows[1:]:
            for i, c in enumerate(r):
                for o, n in pm.items():
                    if o in c: r[i] = c.replace(o, n)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh: csv.writer(fh).writerows(crows)

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    gen = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, rel, new in plan:
        old = os.path.join(ROOT, rel)
        if os.path.exists(old): shutil.move(old, os.path.join(sup, os.path.basename(old)))
        x = old[:-4] + ".xlsx"
        if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
        subprocess.run([sys.executable, gen, new], cwd=ROOT, capture_output=True, text=True)

    r = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    r["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(r, fh, indent=2, ensure_ascii=False); fh.write("\n")
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])

if __name__ == "__main__":
    main("--apply" in sys.argv)
