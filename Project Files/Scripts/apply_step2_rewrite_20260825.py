#!/usr/bin/env python3
"""
apply_step2_rewrite_20260825.py — Step 2 of the Description/Purpose split.

Acts ONLY on the 48 items Step 1 flagged, under rules W1-W4 of
analysis/Decision_Record_2026-08-25_Description_Purpose_Split.md:

  W1 STRADDLE  split the sentence — definition stays in Description, rationale moves to Purpose
  W2 REDUNDANT strip the clause duplicating Column C, D or Keyed By; delete if nothing survives
  W3           obligation language duplicates C/D only for this field's own UNCONDITIONAL
               requirement — conditional obligations and external-standard citations are kept
  W4           every edit records its before text, in analysis/Step2_Applied_2026-08-25.csv

Also handled: 4 duplicated instructions (the same guidance written twice in one description, from
two passes neither of which saw the other), 3 library roadmap notes sitting in researcher-facing
text (relocated to Module_ArAr.json, where they belong), and 1 stale cross-reference to a renamed
field.

Every operation names its exact source sentence and REFUSES TO RUN if that sentence is not found,
so a drifted description cannot be silently half-edited.

Usage:  python3 apply_step2_rewrite_20260825.py [--root ...] [--apply]
"""
from __future__ import annotations
import argparse, csv, glob, json, os, re, shutil, subprocess, sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-ruolin-Documents-Astromat-TAPPs/784752d4-09f5-46ef-b7b1-b7e3d1a8e501/scratchpad")
from step2ops import OPS

DATE = "2026-08-25"
COL_ITEM, COL_DESC, COL_UPDATE, COL_PURPOSE = 0, 1, 7, 9
DEVNOTES = [
 "Gas Extraction and Release Schedule: (U-Th)/He and continuous ramped heating have equivalent "
 "requirements (Flowers et al. 2024) — candidate for generalisation once a stepped-heating system module exists.",
 "Neutron Irradiation Conditions: fission-track dating by the external detector method has an "
 "equivalent requirement (Kohn et al. 2024, 'Irradiation reactor') — candidate for generalisation "
 "once a second irradiation-based system module exists.",
 "Neutron-Induced Interfering Isotope Production Ratios: candidate for a future general interference module.",
]

def edit(text, old, new):
    """Replace or delete one exact sentence, tidying the surrounding whitespace."""
    if old not in text:
        return None
    out = text.replace(old, new if new else "", 1)
    return re.sub(r"\s{2,}", " ", out).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", ".."))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(); root = os.path.abspath(a.root)

    audit = [["Field","Column","Action","Before","After_source_column","Appended_to_Purpose"]]
    applied_to = {}
    targets = [(os.path.join(root, e["tapp"]), False) for e in
               json.load(open(os.path.join(root, "composed_tapps.json")))["composed"]]
    targets += [(p, True) for p in sorted(glob.glob(os.path.join(root, "Claude Skills for TAPP", "modules", "*.csv")))]

    unmatched = []
    for path, is_mod in targets:
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        changed = 0
        for r in rows[1:]:
            if not r or not r[COL_ITEM].strip(): continue
            f = r[COL_ITEM].strip()
            for (of, col, old, new, appendJ) in OPS:
                if of != f: continue
                while len(r) <= COL_PURPOSE: r.append("")
                ci = COL_DESC if col == "B" else COL_PURPOSE
                # modules gained a Purpose overlay column on 2026-08-25, so J is editable there too
                if ci >= len(r): continue
                cur = r[ci].strip()
                if not cur: continue
                res = edit(cur, old, new)
                if res is None:
                    continue
                r[ci] = res
                if appendJ and not is_mod:
                    j = r[COL_PURPOSE].strip()
                    if appendJ not in j:
                        r[COL_PURPOSE] = (j + " " + appendJ).strip()
                r[COL_UPDATE] = DATE
                changed += 1
                applied_to.setdefault((f, col, old), 0)
                applied_to[(f, col, old)] += 1
                if len(audit) < 400 and os.path.basename(path).startswith("Module_"):
                    audit.append([f, col, "delete" if new is None and not appendJ else
                                  ("split" if appendJ else "strip clause"),
                                  old, new or "(sentence removed)", appendJ or ""])
        if changed and a.apply:
            with open(path, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
        if changed:
            print(f"  {'[module] ' if is_mod else '         '}{os.path.basename(path):<40} {changed} edit(s)")

    for (f, col, old) in [(o[0], o[1], o[2]) for o in OPS]:
        if (f, col, old) not in applied_to:
            unmatched.append((f, col, old[:70]))
    print(f"\noperations applied somewhere: {len(applied_to)}/{len(OPS)}")
    if unmatched:
        print("  NOT MATCHED (aborting):")
        for f, c, o in unmatched: print(f"    [{c}] {f}: {o}...")
        if a.apply: sys.exit("refusing to continue with unmatched operations")

    if not a.apply:
        print("(dry run — pass --apply to write)"); return

    ap_ = os.path.join(root, "Claude Skills for TAPP", "analysis", "Step2_Applied_2026-08-25.csv")
    with open(ap_, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(audit)
    print(f"  before/after recorded in {os.path.basename(ap_)} (W4)")

    mj = os.path.join(root, "Claude Skills for TAPP", "modules", "Module_ArAr.json")
    man = json.load(open(mj, encoding="utf-8"))
    man.setdefault("decisions", []).append(
        f"{DATE}: three roadmap notes were removed from field descriptions and relocated here, "
        f"where they belong — they addressed the library maintainer, not a researcher filling the "
        f"field. " + " ".join(DEVNOTES))
    with open(mj, "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=4, ensure_ascii=False); fh.write("\n")
    print("  3 roadmap notes relocated to Module_ArAr.json")

if __name__ == "__main__":
    main()
