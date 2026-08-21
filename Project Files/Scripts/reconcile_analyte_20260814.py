#!/usr/bin/env python3
"""Reconcile the `Analyte` description across its 13 holders, ahead of Module_Analyte.

Module_Analyte could not be built: the field had 4 description variants, and the build script's
uniformity guard refused. Same discipline as Module_Core — reconcile first, so the module ships at
v1 and composition stays a no-op that means something.

Adopted text = V1 (8 TAPPs) minus its closing cross-reference to `Monitored Isotopes`, which is
absent from 5 of the 13 holders (EPMA, SEM_Composition, SEM, TEM, Solution MC-ICP-MS) and so would
dangle in a module-owned description (Rule 6.4). Nothing is lost: `Monitored Isotopes` already states
the boundary from its own side — "The analyte list is given by the Analyte field and is never
inferred from the element symbols appearing here."

Two smaller generalisations: "elements were excluded" -> "species were excluded", and "each element
in this list" -> "each entry in this list", since an analyte may be a valence species or a compound.

  --dry (default) / --apply
"""
import argparse, csv, glob, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REG = os.path.join(ROOT, "composed_tapps.json")
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
DATE, FIELD = "2026-08-14", "Analyte"
COL_A, COL_B, COL_C, COL_D, COL_H = 0, 1, 2, 3, 7

ADOPTED = ("The chemical species this procedure is designed to determine, recorded at whatever "
           "resolution the chemistry is resolved — element(s) for this technique; valence species "
           "where a procedure resolves oxidation state; compounds where it resolves molecules. "
           "Isotopes are not analytes: isotopes of an element are the same chemical species. The "
           "procedure registers the full analyte suite; at analysis level the analyst records the "
           "specific subset actually measured in the session, which may be narrower if species were "
           "excluded due to interferences or scope reduction. Fields whose Keyed By column declares "
           "'analyte' apply individually to each entry in this list.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); apply = a.apply and not a.dry

    # guard: the field must still be in no module (else Rule 6.6 — edit the module instead)
    for p in glob.glob(os.path.join(MODDIR, "Module_*.csv")):
        for r in list(csv.reader(open(p, encoding="utf-8-sig")))[1:]:
            if r and r[0].strip() == FIELD:
                sys.exit(f"FATAL: {FIELD} is owned by {os.path.basename(p)} — edit the module, "
                         f"not the TAPPs (Rule 6.6)")
    print(f"guard OK — {FIELD} is in no module; direct TAPP edit is correct")

    reg = json.load(open(REG, encoding="utf-8"))
    bumps, changed = [], 0
    for e in reg["composed"]:
        p = os.path.join(ROOT, e["tapp"])
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        hit = None
        for i, r in enumerate(rows[1:], start=1):
            if r and r[COL_A].strip() == FIELD and \
               ((len(r) > COL_C and r[COL_C].strip()) or (len(r) > COL_D and r[COL_D].strip())):
                hit = i
        if hit is None:
            continue
        row = rows[hit]
        if " ".join(row[COL_B].split()) == ADOPTED:
            print(f"  {os.path.basename(p)[:-4]:34s} already adopted — skipped")
            continue
        row[COL_B] = ADOPTED
        row[COL_H] = DATE
        changed += 1
        m = re.search(r"_v(\d+)\.csv$", os.path.basename(p))
        newp = re.sub(r"_v\d+\.csv$", f"_v{int(m.group(1)) + 1}.csv", p)
        if os.path.exists(newp):
            sys.exit(f"FATAL: {os.path.basename(newp)} exists — refusing to overwrite")
        bumps.append((p, newp))
        print(f"  {os.path.basename(p)[:-4]:34s} row {hit:>3}  ->  {os.path.basename(newp)[:-4]}")
        if apply:
            with open(newp, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)

    print(f"\n{changed} TAPP(s) change Column B; {len(bumps)} version bump(s)")
    if not apply:
        print("(dry run — pass --apply to write)")
        return

    pathmap = {os.path.basename(o): os.path.basename(n) for o, n in bumps}
    for e in reg["composed"]:
        b = os.path.basename(e["tapp"])
        if b in pathmap:
            e["tapp"] = e["tapp"].replace(b, pathmap[b])
    reg["generated"] = DATE
    with open(REG, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print(f"  composed_tapps.json — {len(pathmap)} path(s) updated")

    cv = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Composed_Variants.csv")
    if os.path.exists(cv):
        crows = list(csv.reader(open(cv, newline="", encoding="utf-8-sig")))
        for r in crows[1:]:
            for i, cell in enumerate(r):
                for old, new in pathmap.items():
                    if old in cell:
                        r[i] = cell.replace(old, new)
        with open(cv, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(crows)
        print("  TAPP_Composed_Variants.csv updated")

    x = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    ok = bad = 0
    for _, n in bumps:
        r = subprocess.run([sys.executable, x, n], capture_output=True, text=True)
        ok, bad = (ok + 1, bad) if r.returncode == 0 else (ok, bad + 1)
    print(f"  xlsx regenerated — {ok} ok, {bad} failed")

    sync = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, sync, "--apply"], capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    print(f"  Rule 12 mirror: {tail[0].strip() if tail else 'sync ran'}")
    print("\nNEXT: run add_analyte_module_20260814.py --apply (its uniformity guard should now pass)")


if __name__ == "__main__":
    main()
