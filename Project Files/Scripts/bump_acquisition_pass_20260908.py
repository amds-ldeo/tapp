#!/usr/bin/env python3
"""Execute the acquisition-pass proposal: recompose and bump every consumer of the four edited modules.

Applies the three TAPP-owned re-keys to the NEW version before composing, so published copies stay as
published. Modules already edited: LaserAblation v11, ICPMS v12, SolutionIntroduction v8, MCICPMS v8.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-08"
EDITED = {"LaserAblation", "ICPMS", "SolutionIntroduction", "MCICPMS"}
TAPP_OWNED = {"Mass Resolution Assignment", "Number of Scans per Replicate",
              "Pulse/Analog Detector Nonlinearity Correction"}
OLD_NAME, NEW_NAME = "Multi-Run Sequential Analysis Design", "Inter-Pass Data Dependency"


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
        if not (EDITED & {m["name"] for m in e["modules"]}):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("  %d consumer(s)" % len(plan))
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    for e, rel, new in plan:
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, new)
        shutil.copy2(src, dst)
        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        iu = rows[0].index("Last Update")
        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            if r[0] == OLD_NAME:                 # rename before composing: compose matches by name
                r[0] = NEW_NAME
            if r[0] in TAPP_OWNED:
                r[8] = "acquisition pass"; r[iu] = DATE
        with open(dst, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

        p = subprocess.run([sys.executable, COMPOSE, "--source", dst] + flags(e["modules"])
                           + ["--out", dst], cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (new, p.stdout[-1500:], p.stderr[-600:]))
        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        touched = [r for r in rows[1:] if r and len(r) > 8 and r[8] and "acquisition pass" in r[8]]
        for r in touched:
            while len(r) <= iu:
                r.append("")
            r[iu] = DATE
        if any(r and r[0] == OLD_NAME for r in rows):
            raise SystemExit("%s: old field name survived" % new)
        with open(dst, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
        print("  %-38s %2d row(s) keyed acquisition pass" % (os.path.basename(new), len(touched)))

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    mods = {}
    for j in sorted(os.listdir(os.path.join(ROOT, "Claude Skills for TAPP", "modules"))):
        if j.endswith(".json"):
            d = json.load(open(os.path.join(ROOT, "Claude Skills for TAPP", "modules", j), encoding="utf-8"))
            mods[d["module"]] = d["version"]
    for e, rel, new in plan:
        o = os.path.join(ROOT, rel)
        for f in (o, o[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] in mods:
                m["version"] = mods[m["name"]]
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced, module versions synced" % len(plan))
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:80])


if __name__ == "__main__":
    main("--apply" in sys.argv)
