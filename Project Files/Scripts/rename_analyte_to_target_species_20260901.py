#!/usr/bin/env python3
"""Rename `Analyte` -> `Target Species` and the Rule 7 key `analyte` -> `target species`.

Field name and key are renamed TOGETHER: splitting them would recreate the
`Reported Variables and Units` / `reported property` drift.

Composition cannot express a field rename (compose matches rows by name, so a renamed module
field is ADDED while the old row survives), so Column A is renamed in the new version BEFORE
composing. Literature-assessment cells are NOT touched: they are extraction records, the same
treatment the retired "Analyte-specific:" label got.
"""
import csv, json, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-01"
OLD_STAMP, NEW_STAMP = "Source: Analyte module", "Source: Target Species module"

FIELD = {
    "Analyte": "Target Species",
    "Per-Analyte Calibration Strategy": "Calibration Strategy per Target Species",
    "Analyte Estimation Method": "Target Species Estimation Method",
    "Technique per Analyte": "Technique per Target Species",
    "EPMA Technique per Analyte": "EPMA Technique per Target Species",
}


def rn(s):
    if not s:
        return s
    s = s.replace("Per-Analyte Calibration Strategy", "Calibration Strategy per Target Species")
    s = s.replace("Analyte-Specific", "Target-Species-Specific").replace("Analyte-specific", "Target-species-specific")
    s = s.replace("analyte-specific", "target-species-specific")
    s = s.replace("Per-Analyte", "Per-Target-Species").replace("per-analyte", "per-target-species")
    s = re.sub(r"\bAnalytes\b", "Target Species", s)
    s = re.sub(r"\banalytes\b", "target species", s)
    s = re.sub(r"\bAnalyte\b", "Target Species", s)
    s = re.sub(r"\banalyte\b", "target species", s)
    return s


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
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
    print("  %d TAPP(s): %s -> +1" % (len(plan), os.path.basename(plan[0][1])))
    if not apply:
        for e, rel, new in plan:
            print("    %-38s -> %s" % (os.path.basename(rel), os.path.basename(new)))
        print("(dry run — pass --apply to write)")
        return

    for e, rel, new in plan:
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, new)
        shutil.copy2(src, dst)
        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        hdr = rows[0]
        sent = hdr.index("Literature Assessment") if "Literature Assessment" in hdr else len(hdr)
        iu = hdr.index("Last Update")
        touched = set()
        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            before = list(r)
            if r[0] in FIELD:
                r[0] = FIELD[r[0]]
            # A..sentinel only — literature columns are extraction records, left alone
            for j in range(1, min(sent, len(r))):
                if j == 6:                      # Column G: provenance stamp, handled below
                    continue
                if re.search(r"analyte", r[j], re.I):
                    r[j] = rn(r[j])
            if len(r) > 6 and r[6].strip() == OLD_STAMP:
                r[6] = NEW_STAMP
            if r != before:
                touched.add(r[0])
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)

        p = subprocess.run([sys.executable, COMPOSE, "--source", dst] + flags(e["modules"])
                           + ["--out", dst], cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (new, p.stdout[-1500:], p.stderr[-600:]))

        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        for r in rows[1:]:
            if r and r[0].strip() in touched:
                while len(r) <= iu:
                    r.append("")
                r[iu] = DATE
        if any(r and re.search(r"\bAnalyte\b", r[0]) for r in rows):
            raise SystemExit("%s: a field named Analyte survived" % new)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  %-38s %d row(s) touched" % (os.path.basename(new), len(touched)))

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    mods = {}
    for j in sorted(os.listdir(os.path.join(ROOT, "Claude Skills for TAPP", "modules"))):
        if j.endswith(".json"):
            d = json.load(open(os.path.join(ROOT, "Claude Skills for TAPP", "modules", j), encoding="utf-8"))
            mods[d["module"]] = d["version"]
    for e, rel, new in plan:
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
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
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:90])


if __name__ == "__main__":
    main("--apply" in sys.argv)
