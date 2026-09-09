#!/usr/bin/env python3
"""Settle `Number of Digestion Steps`: rename to `Digestion Step` and re-type Integer -> Text (free).

The defect: it is the library's ONLY definer typed as a scalar number (95 of 98 definer rows are
`Text (free)` or `Controlled list / Text`). Rule 7.4c asks a definer to enumerate the members of its
key's domain so consumers have rows to attach values to. An Integer cannot: "3" says there are three
steps, not which is which, so `Digestion Acid(s)`, `Digestion Temperature` and `Digestion Duration`
have no member to hang a value on.

Modelled on bump_samplingunitselection_20260901.py because this is a field RENAME: compose matches
rows by field name, so Column A is renamed in the new version BEFORE composing. Column F is an
OVERLAY column, consumer-owned after first composition, so it is rewritten in each consumer too --
composing alone would leave 'e.g., 1 | 2 | 3' behind. The module name is unchanged, so no Column G
repair is needed.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
SKILL = os.path.join(ROOT, "Claude Skills for TAPP")
COMPOSE = os.path.join(SKILL, "scripts", "compose_tapp.py")
XLSX = os.path.join(SKILL, "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-08"
MODULE = "SolutionIntroduction"
OLD_FIELD, NEW_FIELD = "Number of Digestion Steps", "Digestion Step"

NEW_B = (
    "Each distinct acid digestion step applied to dissolve the sample, listed in the order performed "
    "and named by its attack. A step is distinct when its acid mixture, vessel, temperature or duration "
    "differs from the one before; an evaporation or dry-down that carries no attack of its own is part "
    "of the step it follows, and an identical attack repeated on the residue is a repeat of that step "
    "rather than a new one. Enumerating the steps is what allows Digestion Acid(s), Digestion "
    "Temperature and Digestion Duration to be recorded per step. Record N/A where the sample is "
    "introduced without acid digestion."
)
NEW_F = ("e.g., '1: HF-HNO3, Parr bomb | 2: aqua regia reflux of the residue' | "
         "'1: HF-HNO3-HClO4 | 2: HNO3-HCl | 3: HNO3-H2O2' | 'Single step' | 'N/A (no acid digestion)'")
NEW_J = ("Naming each step is what lets acid, temperature and duration be read per step; a bare count "
         "cannot say which conditions belong to which attack, and cannot settle whether a repeated "
         "attack or an intervening evaporation counts.")
FIELDS = {NEW_FIELD}


def flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def edit_module():
    p = os.path.join(SKILL, "modules", "Module_%s.csv" % MODULE)
    rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
    h = rows[0]
    iB, iE, iF, iH, iJ = (h.index(x) for x in
                          ("Description", "Data Type", "Example / Allowed Content", "Last Update", "Purpose"))
    hit = 0
    for r in rows[1:]:
        if r and r[0].strip() == OLD_FIELD:
            while len(r) <= max(iB, iE, iF, iH, iJ):
                r.append("")
            assert r[iE].strip() == "Integer", r[iE]
            r[0] = NEW_FIELD
            r[iB] = NEW_B
            r[iE] = "Text (free)"
            r[iF] = NEW_F
            r[iH] = DATE
            r[iJ] = NEW_J
            hit += 1
    assert hit == 1, hit
    with open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)

    jp = os.path.join(SKILL, "modules", "Module_%s.json" % MODULE)
    j = json.load(open(jp, encoding="utf-8"))
    assert j["version"] == "8", j["version"]
    j["version"] = "9"
    for b in j["blocks"]:
        b["fields"] = [NEW_FIELD if f == OLD_FIELD else f for f in b["fields"]]
    j["decisions"].append(
        "2026-09-08 v9. `Number of Digestion Steps` -> `Digestion Step`, Data Type Integer -> Text "
        "(free); Column I unchanged at `defines: preparation step`. It was the library's only definer "
        "typed as a scalar number, against 95 definer rows typed `Text (free)` or `Controlled list / "
        "Text`. 7.4a's `An ordinal count enumerates its domain` carve-out, written for this one field, "
        "was retired at the same time: its own literature falsifies it -- 6 of 9 assessed cells carry "
        "the step names beside or instead of the count, 2 carry no number at all, and Hu & Gao 2008 "
        "reads `2` beside `five steps explicitly numbered`. Column B now defines a step by what the "
        "consumers distinguish, which settles that grain question. Kept `Digestion` rather than "
        "`Preparation Step` because all three consumers are `Digestion X` and could not describe a "
        "non-digestion member.")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(j, fh, indent=4, ensure_ascii=False); fh.write("\n")
    return j["version"]


def main(apply=False):
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        if not any(m["name"] == MODULE for m in e["modules"]):
            continue
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-34s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    if not apply:
        print("  (dry run -- pass --apply to write)")
        return

    mver = edit_module()
    print("  module Module_%s -> v%s" % (MODULE, mver))

    for e, rel, new in plan:
        src, dst = os.path.join(ROOT, rel), os.path.join(ROOT, new)
        # 1. rename Column A and rewrite the consumer-owned overlay cells BEFORE composing
        rows = list(csv.reader(open(src, newline="", encoding="utf-8-sig")))
        h = rows[0]
        iF, iJ = h.index("Example / Allowed Content"), h.index("Purpose")
        hit = 0
        for r in rows[1:]:
            if r and r[0].strip() == OLD_FIELD:
                while len(r) <= iJ:
                    r.append("")
                r[0] = NEW_FIELD; r[iF] = NEW_F; r[iJ] = NEW_J; hit += 1
        assert hit == 1, (rel, hit)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        # 2. compose in place over the renamed copy
        p = subprocess.run([sys.executable, COMPOSE, "--source", dst] + flags(e["modules"])
                           + ["--out", dst], cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, p.stdout[-1500:], p.stderr[-600:]))
        # 3. stamp Last Update on the row the module owns
        rows = list(csv.reader(open(dst, newline="", encoding="utf-8-sig")))
        h = rows[0]; iu = h.index("Last Update"); n = 0
        for r in rows[1:]:
            if r and r[0].strip() in FIELDS:
                while len(r) <= iu:
                    r.append("")
                r[iu] = DATE; n += 1
        assert n == len(FIELDS), (new, n)
        assert not any(r and r[0].strip() == OLD_FIELD for r in rows[1:]), "old row survived " + new
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print("  composed %s" % os.path.basename(new))

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT,
                       capture_output=True, text=True)
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] == MODULE:
                m["version"] = mver
    reg["generated"] = DATE
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced" % len(plan))
    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:90])


if __name__ == "__main__":
    main("--apply" in sys.argv)
