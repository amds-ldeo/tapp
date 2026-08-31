#!/usr/bin/env python3
"""Harmonise `WDS Dead Time Correction` Column F; 7.8.11 backlog (2026-08-31).

    [2] SEM, SEM_Composition
        Default constant (manufacturer) | Adjusted constant | High-precision (Probe for EPMA) |
        Logarithmic | Unknown | N/A | None
    [1] EPMA
        Default constant 3 us (Cameca) | Adjusted constant (Cameca) | Default constant (JEOL) |
        Adjusted constant (JEOL) | High-precision (Probe for EPMA) | Logarithmic |
        Super-precision | Unknown | N/A | None

ZERO attested cells across all three tables -- the literature reports this essentially never
(44 explicit not-stated). So there is no evidence to adjudicate from and this is a design call,
stated as such rather than dressed up as a finding.

THE MAJORITY FORM WINS ON STRUCTURE, and this is the first backlog entry where the harmonised
list is SHORTER than one of its variants. EPMA's four constant-members are a CROSS-PRODUCT of
two axes -- {default, adjusted} x {Cameca, JEOL} -- and the vendor axis is not this field's to
carry: `Instrument Manufacturer` already records it, as a Controlled list discovery facet.
This is the same defect as `FESEM` in `Instrument Variant` and the `fs-` prefix in `Technique`
-- a value from a neighbouring field folded into these members -- and the same defect as
`FIB-SEM dual-beam + VP`, a combinatorial member that cannot survive its axes being separated.
`Default constant 3 us (Cameca)` compounds it by baking a VALUE into a member name.

Nothing is lost. The field is `Controlled list / Text`, so a procedure that needs to say
`Default constant (manufacturer) - 3 us, Cameca` says exactly that, and Column B now instructs
it. What goes is the cross-product, not a distinction the field owns.

`Super-precision` is genuine and additive -- it is the top of the Probe for EPMA dead-time
hierarchy (constant -> logarithmic -> high-precision -> super-precision) and the SEM tables
simply lacked it. It gains the `(Probe for EPMA)` qualifier its sibling already carries.
Members are ordered by that hierarchy rather than alphabetically.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
ITEM = "WDS Dead Time Correction"
TARGET = ("Default constant (manufacturer) | Adjusted constant | Logarithmic | "
          "High-precision (Probe for EPMA) | Super-precision (Probe for EPMA) | "
          "Unknown | N/A | None")
B_ADD = (" Record the algorithm here and any instrument-specific constant alongside it — "
         "'Default constant (manufacturer) — 3 µs, Cameca'. The instrument vendor itself is "
         "recorded by Instrument Manufacturer, not by this field's allowed values.")
EXPECT = {
 ("Default constant (manufacturer) | Adjusted constant | High-precision (Probe for EPMA) | "
  "Logarithmic | Unknown | N/A | None"),
 ("Default constant 3 us (Cameca) | Adjusted constant (Cameca) | Default constant (JEOL) | "
  "Adjusted constant (JEOL) | High-precision (Probe for EPMA) | Logarithmic | Super-precision | "
  "Unknown | N/A | None"),
}

def main():
    dry = "--apply" not in sys.argv
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    tot = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            cur = r[iF].strip()
            if cur != TARGET:
                if cur not in EXPECT:
                    print(f"  ABORT: {base} Column F is not a known variant:\n     {cur}"); return 1
                print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {cur}")
                r[iF] = TARGET; hit = True; tot += 1
            if B_ADD.strip() not in r[iB]:
                r[iB] = r[iB].rstrip() + B_ADD; hit = True
            if hit: r[iU] = STAMP
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  now: {TARGET}\n\n{'DRY RUN — ' if dry else ''}{tot} Column F cells (+ Column B on each)")
    return 0

sys.exit(main())
