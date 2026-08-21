#!/usr/bin/env python3
"""Extend Rule 6.11 `source_comment` from 3 modules to all 12, so every module-supplied field
names its module in Column G.

Rule 6.11 previously declared source_comment only on Geochronology, UPb and ArAr, and recorded a
deliberate decision NOT to label the general modules because "labelling them would be noise". That
decision was made when there were 8 modules, 3 of them geochronology-specific, and Column G had just
been cleared. With 12 modules supplying 45% of all content rows, a reader of a composed TAPP can no
longer tell what came from where, which is the situation the label exists to fix. Superseded
deliberately, not by oversight.

Mechanism is unchanged and already safe: `stamp_source_comment` only ever fills an EMPTY Column G
cell, so consumer annotation always wins and recomposition stays idempotent. Fields a Layer 3 module
merely OVERLAYS keep their owner's label — the label names the owner, not the overlayer.

  --dry (default) / --apply
"""
import argparse, csv, glob, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
REG = os.path.join(ROOT, "composed_tapps.json")
DATE = "2026-08-14"
COL_G = 6

LABEL = {
    "Core": "Source: Core module",
    "TargetSelection": "Source: Target Selection module",
    "CalibrationFactor": "Source: Calibration Factor module",
    "Blank": "Source: Blank module",
    "Aggregation": "Source: Aggregation module",
    "Analyte": "Source: Analyte module",
    "LaserAblation": "Source: Laser Ablation module",
    "MCICPMS": "Source: MC-ICP-MS module",
    "SolutionIntroduction": "Source: Solution Introduction module",
}


def module_flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(); apply = a.apply and not a.dry

    # ---- 1. declare source_comment on the modules that lack it ----
    todo = []
    for p in sorted(glob.glob(os.path.join(MODDIR, "Module_*.json"))):
        man = json.load(open(p, encoding="utf-8"))
        name = man["module"]
        if man.get("source_comment"):
            print(f"  {name:22s} already labelled: {man['source_comment']!r}")
            continue
        if name not in LABEL:
            sys.exit(f"FATAL: no label defined for module {name}")
        todo.append((p, man, LABEL[name]))
        print(f"  {name:22s} -> {LABEL[name]!r}")

    if apply:
        for p, man, label in todo:
            out = {}
            for k, v in man.items():
                out[k] = v
                if k == "mode_flag_default":
                    out["source_comment"] = label
            if "source_comment" not in out:
                out["source_comment"] = label
            out.setdefault("decisions", []).append(
                f"{DATE}: source_comment declared. Rule 6.11 originally withheld the label from the "
                f"general modules as noise; with 12 modules supplying most of the library, naming the "
                f"source of every field is what makes a composed TAPP readable. Documentation only — "
                f"no structural meaning, not schema content.")
            json.dump(out, open(p, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
            open(p, "a", encoding="utf-8").write("\n")
        print(f"\n{len(todo)} manifest(s) updated")

    # ---- 2. recompose every TAPP into a bumped version ----
    reg = json.load(open(REG, encoding="utf-8"))
    plan = [(e["tapp"], e["modules"]) for e in reg["composed"]]
    print(f"\nrecomposing {len(plan)} TAPP(s)")
    changed = 0
    for tapp, mods in plan:
        src = os.path.join(ROOT, tapp)
        m = re.search(r"_v(\d+)\.csv$", os.path.basename(src))
        dst = re.sub(r"_v\d+\.csv$", f"_v{int(m.group(1)) + 1}.csv", src)
        if os.path.exists(dst):
            sys.exit(f"FATAL: {os.path.basename(dst)} already exists")
        if not apply:
            print(f"  {os.path.basename(src)[:-4]:34s} -> {os.path.basename(dst)[:-4]}"
                  f"   ({len(mods)} modules)")
            continue
        r = subprocess.run([sys.executable, COMPOSE, "--source", src, "--out", dst]
                           + module_flags(mods), capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            sys.exit(f"FATAL: composing {os.path.basename(src)} failed:\n{r.stdout}\n{r.stderr}")

        # ---- guard: Column G must be the ONLY column that changed ----
        before = list(csv.reader(open(src, newline="", encoding="utf-8-sig")))
        after = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        if len(before) != len(after):
            sys.exit(f"FATAL: {os.path.basename(dst)} row count moved "
                     f"{len(before)} -> {len(after)}")
        bad, g = [], 0
        for i, (b, aft) in enumerate(zip(before, after)):
            for j in range(max(len(b), len(aft))):
                ov = b[j] if j < len(b) else ""
                nv = aft[j] if j < len(aft) else ""
                if ov == nv:
                    continue
                if j == COL_G:
                    g += 1
                else:
                    bad.append((i + 1, j, ov[:40], nv[:40]))
        if bad:
            sys.exit(f"FATAL: {os.path.basename(dst)} changed columns other than G: {bad[:5]}")
        changed += g
        print(f"  {os.path.basename(src)[:-4]:34s} -> {os.path.basename(dst)[:-4]}"
              f"   {g:3d} Column G cell(s) stamped")

    if not apply:
        print("\n(dry run — pass --apply to write)")
        return
    print(f"\n{changed} Column G cells stamped across {len(plan)} TAPPs")

    # ---- 3. xlsx + mirror ----
    reg = json.load(open(REG, encoding="utf-8"))   # compose_tapp.py rewrote the paths
    x = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
    ok = bad = 0
    for e in reg["composed"]:
        r = subprocess.run([sys.executable, x, os.path.join(ROOT, e["tapp"])],
                           capture_output=True, text=True)
        ok, bad = (ok + 1, bad) if r.returncode == 0 else (ok, bad + 1)
    print(f"  xlsx regenerated — {ok} ok, {bad} failed")
    sync = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    r = subprocess.run([sys.executable, sync, "--apply"], capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    print(f"  Rule 12 mirror: {tail[0].strip() if tail else 'sync ran'}")


if __name__ == "__main__":
    main()
