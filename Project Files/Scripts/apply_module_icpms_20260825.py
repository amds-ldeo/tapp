#!/usr/bin/env python3
"""
apply_module_icpms_20260825.py — compose Module_ICPMS v1 into the 9 ICP-MS TAPPs.

The module was extracted from the 13 fields whose Columns B/C/D/E/I are already byte-identical
across all nine consumers, so composition changes NO field content. The only cell that moves is
Comments, which gains the Rule 6.11 provenance label `Source: ICP-MS module` on those 13 rows.
That is the point of v1: nine hand-maintained copies become one owned definition, and
`compose_tapp.py --check` starts reporting MATCH instead of a standing DIFFERS.

Usage:  python3 apply_module_icpms_20260825.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, json, os, re, shutil, subprocess, sys

DATE = "2026-08-25"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    compose = os.path.join(root, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
    reg_path = os.path.join(root, "composed_tapps.json")
    with open(reg_path, encoding="utf-8") as fh:
        reg = json.load(fh)

    targets = sorted(e["tapp"] for e in reg["composed"] if "ICP" in e["tapp"])
    renames = []
    for rel in targets:
        newrel = re.sub(r"_v(\d+)\.csv$", lambda m: f"_v{int(m.group(1))+1}.csv", rel)
        renames.append((rel, newrel))
        print(f"  {os.path.basename(rel)}  ->  {os.path.basename(newrel)}")
        if a.apply:
            r = subprocess.run([sys.executable, compose, "--source", rel, "--module", "ICPMS",
                                "--out", newrel], cwd=root, capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"compose failed for {rel}: {r.stderr.strip()[:300]}")

    print(f"\n{len(renames)} TAPP(s)")
    if not a.apply:
        print("(dry run — pass --apply to write)")
        return

    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in renames}
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"])
        if b not in pathmap:
            continue
        e["tapp"] = e["tapp"].replace(b, pathmap[b])
        if not any(m["name"] == "ICPMS" for m in e["modules"]):
            e["modules"].append({"name": "ICPMS", "version": "1"})
    reg["generated"] = DATE
    with open(reg_path, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"  composed_tapps.json: {len(pathmap)} path(s) + ICPMS v1 recorded on each")

    cv = os.path.join(root, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        rows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in rows[1:]:
            for i, cell in enumerate(r):
                for old, new in pathmap.items():
                    if old in cell:
                        r[i] = cell.replace(old, new)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  TAPP_Composed_Variants.csv updated")

    sup = os.path.join(root, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for old, _ in renames:
        p = os.path.join(root, old)
        shutil.move(p, os.path.join(sup, os.path.basename(p)))
        x = p[:-4] + ".xlsx"
        if os.path.exists(x):
            shutil.move(x, os.path.join(sup, os.path.basename(x)))
    print(f"  retired {len(renames)} CSV(s) + xlsx to Superseded TAPPs/{DATE}/")

    gen = os.path.join(root, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, new in renames:
        r = subprocess.run([sys.executable, gen, new], cwd=root, capture_output=True, text=True)
        if r.returncode:
            print(f"  WARN xlsx failed {new}: {r.stderr.strip()[:140]}")
    print(f"  regenerated {len(renames)} xlsx")

    for script, label in [("build_module_register.py", "module register"),
                          ("sync_current_tapps.py", "Rule 12 mirror")]:
        p = os.path.join(root, "Project Files", "Scripts", script)
        if not os.path.exists(p):
            p = os.path.join(root, "Claude Skills for TAPP", "scripts", script)
        if os.path.exists(p):
            r = subprocess.run([sys.executable, p, "--apply"], cwd=root, capture_output=True, text=True)
            tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
            print(f"  {label}: {tail[0].strip()[:80] if tail else 'ran'}")

if __name__ == "__main__":
    main()
