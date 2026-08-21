#!/usr/bin/env python3
"""Dissolve Module_ReportingCore into TargetSelection, CalibrationFactor, Blank, Aggregation.

No TAPP file changes and no version bumps: all 52 module x consumer pairs report --check MATCH,
because the dissolution moves fields between modules and changes no definition.

  --dry (default) / --apply
"""
import argparse, csv, json, os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
REG = os.path.join(ROOT, "composed_tapps.json")
MREG = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
ARCH = os.path.join(ROOT, "Archive", "Superseded Modules")
DATE, OLD = "2026-08-14", "ReportingCore"
NEW = ["TargetSelection", "CalibrationFactor", "Blank", "Aggregation"]


def module_fields(name):
    p = os.path.join(MODDIR, f"Module_{name}.csv")
    return {r[0].strip() for r in list(csv.reader(open(p, encoding="utf-8-sig")))[1:]
            if r and r[0].strip() and ((len(r) > 2 and r[2].strip()) or (len(r) > 3 and r[3].strip()))}


def tapp_fields(rel):
    p = os.path.join(ROOT, rel)
    out = set()
    for r in list(csv.reader(open(p, encoding="utf-8-sig")))[1:]:
        if r and r[0].strip() and ((len(r) > 2 and r[2].strip()) or (len(r) > 3 and r[3].strip())):
            out.add(r[0].strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); apply = a.apply and not a.dry

    reg = json.load(open(REG, encoding="utf-8"))
    mf = {n: module_fields(n) for n in NEW}

    # ---- guard: the four must partition ReportingCore's fields exactly ----
    old_fields = module_fields(OLD)
    union = set().union(*mf.values())
    if union != old_fields:
        sys.exit(f"FATAL: field sets differ.\n  only in {OLD}: {sorted(old_fields - union)}\n"
                 f"  only in successors: {sorted(union - old_fields)}")
    overlap = [(x, y) for i, x in enumerate(NEW) for y in NEW[i + 1:] if mf[x] & mf[y]]
    if overlap:
        sys.exit(f"FATAL: successor modules overlap: {overlap}")
    print(f"guard OK — the four partition {OLD}'s {len(old_fields)} fields exactly, no overlap")

    # ---- work out each consumer's new module set from actual field presence ----
    plan, pairs = {}, 0
    for e in reg["composed"]:
        if not any(m["name"] == OLD for m in e["modules"]):
            continue
        have = tapp_fields(e["tapp"])
        sel = [n for n in NEW if mf[n] <= have]
        partial = [n for n in NEW if (mf[n] & have) and not mf[n] <= have]
        if partial:
            sys.exit(f"FATAL: {os.path.basename(e['tapp'])} holds part of {partial} — "
                     f"a successor module is not all-or-nothing there")
        plan[e["tapp"]] = sel
        pairs += len(sel)

    print(f"\n{len(plan)} consumer(s); {OLD} x{len(plan)} -> {pairs} successor pair(s)")
    for t, sel in sorted(plan.items()):
        print(f"  {os.path.basename(t)[:-4]:34s} {', '.join(sel) if sel else '(none)'}")

    # ---- guard: --check MATCH for every new pair ----
    bad = []
    for t, sel in plan.items():
        for n in sel:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "Claude Skills for TAPP",
                                                             "scripts", "compose_tapp.py"),
                                "--source", t, "--module", n, "--check"],
                               capture_output=True, text=True, cwd=ROOT)
            if r.returncode != 0:
                bad.append((os.path.basename(t), n))
    if bad:
        sys.exit(f"FATAL: {len(bad)} pair(s) do not MATCH: {bad[:5]}")
    print(f"guard OK — all {pairs} successor pairs --check MATCH; dissolution is pure bookkeeping")

    # ---- composed_tapps.json ----
    for e in reg["composed"]:
        if e["tapp"] not in plan:
            continue
        keep = [m for m in e["modules"] if m["name"] != OLD]
        at = next((i for i, m in enumerate(e["modules"]) if m["name"] == OLD), len(keep))
        ins = [{"name": n, "version": "1"} for n in plan[e["tapp"]]]
        e["modules"] = keep[:at] + ins + keep[at:]
    reg["generated"] = DATE

    # ---- requires: UPb / ArAr name ReportingCore ----
    req_updates = []
    for f in sorted(os.listdir(MODDIR)):
        if not f.endswith(".json") or f == f"Module_{OLD}.json":
            continue
        p = os.path.join(MODDIR, f)
        man = json.load(open(p, encoding="utf-8"))
        if OLD in (man.get("requires") or []):
            man["requires"] = [x for x in man["requires"] if x != OLD] + NEW
            req_updates.append((p, man, man["module"]))
    for _, _, name in req_updates:
        print(f"  requires: {name} -> {OLD} replaced by the four successors")

    # ---- module register ----
    rows = list(csv.reader(open(MREG, newline="", encoding="utf-8-sig")))
    hdr = rows[0]
    out = [hdr]
    for r in rows[1:]:
        if r and r[0].strip() == OLD:
            r[hdr.index("Consumers")] = "0 TAPP(s)"
            r[hdr.index("Status")] = f"retired {DATE} — dissolved into {', '.join(NEW)}"
        out.append(r)
    for n in NEW:
        man = json.load(open(os.path.join(MODDIR, f"Module_{n}.json"), encoding="utf-8"))
        nf = sum(len(b["fields"]) for b in man["blocks"])
        nc = sum(1 for sel in plan.values() if n in sel)
        out.append([n, "2", man["title"], str(nf), str(len(man["blocks"])), "1",
                    f"{nc} TAPP(s)", "active"])
    out[1:] = sorted(out[1:], key=lambda r: r[0].lower())

    moves = [(os.path.join(MODDIR, f"Module_{OLD}{e}"), os.path.join(ARCH, f"Module_{OLD}{e}"))
             for e in (".csv", ".json")]
    for s, d in moves:
        print(f"  archive: {os.path.relpath(s, ROOT)} -> {os.path.relpath(d, ROOT)}")

    if not apply:
        print("\n(dry run — pass --apply to write)")
        return

    with open(REG, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for p, man, _ in req_updates:
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(man, fh, indent=4, ensure_ascii=False); fh.write("\n")
    with open(MREG, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(out)
    os.makedirs(ARCH, exist_ok=True)
    for s, d in moves:
        if os.path.exists(s):
            shutil.move(s, d)
    with open(os.path.join(ARCH, "README.md"), "a", encoding="utf-8") as fh:
        fh.write(f"- `Module_{OLD}` — retired {DATE}, dissolved into {', '.join(NEW)}. It was the "
                 f"only conditional module and the only one that was not all-or-nothing: 9 of 16 "
                 f"consumers held all six fields, and its five blocks had four different consumer "
                 f"footprints. Field definitions were carried over unchanged.\n")
    print("\nwritten.")


if __name__ == "__main__":
    main()
