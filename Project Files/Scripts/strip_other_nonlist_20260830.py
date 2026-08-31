#!/usr/bin/env python3
"""Strip `Other: specify` from the non-controlled-list cells commit 2 left behind (2026-08-30).

Commit 2 retired `Other: specify` from the vocabulary but swept only cells typed
`Controlled list` / `Controlled list / Text`, because that is where the option contradicted
the type. 137 cells across 43 fields typed `Text (free)` or `Numeric (L/min)` kept it, where
it is simply meaningless: free text already admits any answer, and a numeric field's Column F
is illustrative.

READING THE CELLS FIRST TURNED UP SOMETHING WORTH RECORDING. All 43 fields write Column F as a
MEMBER LIST -- pipe-separated values ending `N/A | None | Other: specify`, the controlled-list
convention exactly -- and NONE uses the `e.g.,` prefix that marks an illustrative list. So
`Other: specify` never appeared on a genuine example list; it appeared wherever someone wrote
an enumeration and typed the field `Text (free)`.

That splits the 43 two ways, and this script does NOT resolve it:
  * genuine taxonomies, arguably mis-typed -- `Torch Type` (Standard quartz | High-matrix |
    Low-volume), `Nebulizer Type`, `Digestion Acid(s)`, `Digestion Vessel Type`,
    `Sampler and Skimmer Cone Material`
  * genuine examples that merely lack the `e.g.,` prefix -- `Interfering Species`
    ("54Cr+ on 54Fe+"), `Within-Session Analytical Precision`, `Faraday Cup Array
    Configuration`, `Monitored Masses`
Deciding which is which is a typing pass, flagged separately. Stripping is correct under
either reading, and forecloses nothing.

`N/A | None` are KEPT. They are meaningful values on any type -- the field does not apply, or
it applies and nothing was used -- and only `Other: specify` left the vocabulary.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"

def strip_other(ex):
    return " | ".join(p.strip() for p in ex.split("|")
                      if p.strip().strip("'\"").lower() != "other: specify")

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
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        n = 0
        for r in rows[1:]:
            if len(r) <= iU: continue
            if r[iE].strip().startswith("Controlled list"): continue   # commit 2 owned these
            if "Other: specify" not in r[iF]: continue
            r[iF] = strip_other(r[iF]); r[iU] = STAMP; n += 1
        if not n: continue
        print(f"  {base:26s} v{ver} -> v{ver+1}   {n} cell(s)")
        tot += n
        if not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
