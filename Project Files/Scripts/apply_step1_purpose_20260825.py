#!/usr/bin/env python3
"""
apply_step1_purpose_20260825.py — execute Step 1 of the Description/Purpose split (modules).

MOVE ONLY. Every sentence keeps its exact text; sentences are assigned to Column B (Description)
or Column J (Purpose) per the routing in
analysis/Step1_Routing_ALL_MODULES_2026-08-25.csv, decided under rules M1-M6 of
analysis/Decision_Record_2026-08-25_Description_Purpose_Split.md. Nothing is reworded and nothing
is deleted; the 48 items needing edits are flagged there for Step 2 and are untouched here.

Ownership. Modules own Column B, so the module CSV keeps only the Description sentences. Purpose is
CONSUMER-owned, so the Purpose sentences are written into each consuming TAPP's Column J. All
consumers start from identical Purpose text because the module description they came from was
uniform; they are free to diverge afterwards, which is the point of making J consumer-owned.

Verification built in: the script refuses to write if the Description and Purpose halves of any
field do not reconstruct the original word count.

Usage:  python3 apply_step1_purpose_20260825.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re, shutil, subprocess, sys

DATE = "2026-08-25"
COL_ITEM, COL_DESC, COL_UPDATE, COL_PURPOSE = 0, 1, 7, 9


def load_map(root):
    p = os.path.join(root, "Claude Skills for TAPP", "analysis",
                     "Step1_Routing_ALL_MODULES_2026-08-25.csv")
    from collections import defaultdict
    acc = defaultdict(list)
    with open(p, newline="", encoding="utf-8-sig") as fh:
        for mod, f, i, route, rule, flag, reason, text in list(csv.reader(fh))[1:]:
            acc[f].append((int(i), route, text))
    out = {}
    for f, ss in acc.items():
        ss.sort()
        seen, uniq = set(), []
        for i, r, t in ss:                      # same field can appear via two modules
            if (i, t) in seen: continue
            seen.add((i, t)); uniq.append((i, r, t))
        d = " ".join(t for _, r, t in uniq if r == "D")
        p_ = " ".join(t for _, r, t in uniq if r == "P")
        orig = " ".join(t for _, _, t in uniq)
        assert len((d + " " + p_).split()) == len(orig.split()), f
        out[f] = (d, p_)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(); root = os.path.abspath(a.root)
    M = load_map(root)
    print(f"routing map: {len(M)} fields, {sum(1 for d,p in M.values() if p)} with a Purpose\n")

    # ---- modules: Column B keeps Description only -------------------------
    bumped = {}
    for mp in sorted(glob.glob(os.path.join(root, "Claude Skills for TAPP", "modules", "*.csv"))):
        name = os.path.basename(mp).replace("Module_", "").replace(".csv", "")
        rows = list(csv.reader(open(mp, newline="", encoding="utf-8-sig")))
        n = 0
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip() or not r[COL_DESC].strip(): continue
            f = r[COL_ITEM].strip()
            if f in M and r[COL_DESC].strip() != M[f][0]:
                r[COL_DESC] = M[f][0]; r[COL_UPDATE] = DATE; n += 1
        if n:
            jp = mp[:-4] + ".json"
            man = json.load(open(jp, encoding="utf-8"))
            old = man.get("version", "1"); new = str(int(old) + 1)
            bumped[name] = (old, new)
            print(f"  [module] {name:<22} {n} description(s) trimmed   v{old} -> v{new}")
            if a.apply:
                with open(mp, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
                man["version"] = new
                man.setdefault("decisions", []).append(
                    f"{DATE}: Step 1 of the Description/Purpose split. Column B keeps the "
                    f"Description sentences; the Purpose sentences moved to consumer-owned Column J. "
                    f"Move only — no text reworded or deleted. Routing and rules in "
                    f"analysis/Step1_Routing_ALL_MODULES_2026-08-25.csv.")
                with open(jp, "w", encoding="utf-8") as fh:
                    json.dump(man, fh, indent=4, ensure_ascii=False); fh.write("\n")

    # ---- TAPPs: B = Description, J = Purpose ------------------------------
    reg_path = os.path.join(root, "composed_tapps.json")
    reg = json.load(open(reg_path, encoding="utf-8"))
    renames = []
    for e in sorted(reg["composed"], key=lambda x: x["tapp"]):
        rel = e["tapp"]; path = os.path.join(root, rel)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        nb = npu = 0
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip(): continue
            f = r[COL_ITEM].strip()
            if f not in M: continue
            while len(r) <= COL_PURPOSE: r.append("")
            d, p_ = M[f]
            if r[COL_DESC].strip() != d: r[COL_DESC] = d; nb += 1
            if p_ and r[COL_PURPOSE].strip() != p_: r[COL_PURPOSE] = p_; npu += 1
            if nb or npu: r[COL_UPDATE] = DATE
        if not (nb or npu): continue
        base = os.path.basename(rel)
        newrel = re.sub(r"_v(\d+)\.csv$", lambda m: f"_v{int(m.group(1))+1}.csv", rel)
        renames.append((rel, newrel))
        print(f"  {base:<38} B:{nb:>3}  J:{npu:>3}  -> {os.path.basename(newrel)}")
        if a.apply:
            with open(os.path.join(root, newrel), "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{len(bumped)} module(s) bumped, {len(renames)} TAPP(s) bumped")
    if not a.apply:
        print("(dry run — pass --apply to write)"); return

    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in renames}
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"])
        if b in pathmap: e["tapp"] = e["tapp"].replace(b, pathmap[b])
        for mod in e["modules"]:
            if mod["name"] in bumped and mod.get("version") == bumped[mod["name"]][0]:
                mod["version"] = bumped[mod["name"]][1]
    reg["generated"] = DATE
    with open(reg_path, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"  composed_tapps.json updated ({len(pathmap)} paths, {len(bumped)} module versions)")

    mr = os.path.join(root, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
    if os.path.exists(mr):
        mrows = list(csv.reader(open(mr, newline="", encoding="utf-8-sig")))
        vi = mrows[0].index("Version") if "Version" in mrows[0] else None
        if vi is not None:
            for r in mrows[1:]:
                if r and r[0].strip() in bumped and r[vi].strip() == bumped[r[0].strip()][0]:
                    r[vi] = bumped[r[0].strip()][1]
            with open(mr, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(mrows)
            print("  TAPP_Module_Register.csv updated")

    cv = os.path.join(root, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in crows[1:]:
            for i, cell in enumerate(r):
                for old, new in pathmap.items():
                    if old in cell: r[i] = cell.replace(old, new)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(crows)
        print("  TAPP_Composed_Variants.csv updated")

    sup = os.path.join(root, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for old, _ in renames:
        p = os.path.join(root, old); shutil.move(p, os.path.join(sup, os.path.basename(p)))
        x = p[:-4] + ".xlsx"
        if os.path.exists(x): shutil.move(x, os.path.join(sup, os.path.basename(x)))
    print(f"  retired {len(renames)} CSV(s) + xlsx to Superseded TAPPs/{DATE}/")

    gen = os.path.join(root, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    for _, new in renames:
        r = subprocess.run([sys.executable, gen, new], cwd=root, capture_output=True, text=True)
        if r.returncode: print(f"  WARN xlsx {new}: {r.stderr.strip()[:120]}")
    print(f"  regenerated {len(renames)} xlsx")
    for s in ["build_module_register.py", "sync_current_tapps.py"]:
        for d in ["Project Files/Scripts", "Claude Skills for TAPP/scripts"]:
            p = os.path.join(root, d, s)
            if os.path.exists(p):
                r = subprocess.run([sys.executable, p, "--apply"], cwd=root, capture_output=True, text=True)
                tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
                print(f"  {s}: {tail[0].strip()[:70] if tail else 'ran'}")
                break

if __name__ == "__main__":
    main()
