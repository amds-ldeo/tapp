#!/usr/bin/env python3
"""`Chromatographic Separation Applied` — 7.8.11 backlog (2026-08-31).

    [2] Solution Q, SF   Anion exchange resin (HCl) | Cation exchange resin | AG1-X8 (HBr) |
                         None | N/A
    [1] Solution MC      Anion exchange resin AG1-X8 (HCl) | Cation exchange resin AG50W-X8 |
                         TRU resin | UTEVA resin | AG-MP-1 (HBr) | Thiol resin |
                         Multi-step: specify | None | N/A

THE STARKEST GRAIN FAILURE IN THE BACKLOG. 24 attested cells, **24 of them distinct** —
a distinctness ratio of 1.00, and not one is a bare list member. Every positive answer is a
full column-chemistry protocol:

    Yes — AG1-X8 anion (1 ml) for Fe, then AG50-X12 cation (1 ml) twice for Cr and Mg
    Yes — five steps: AG50W-X8 cation, a second cation column, AG1-X8 anion in 2 M HF for Ti...
    Yes — U/TEVA, TODGA, then two-step FPLC on Ln-Spec resin (70 cm x 1.6 mm, 1.4 ml of 25-50 um)
    None (direct analysis of digested solution)

The lists enumerate RESINS, and that domain is unbounded — the literature alone supplies
AG1-X8, AG50-X8, AG50W-X8, AG50 X12, AG-MP-1, DGA, LN/Ln-Spec, TODGA, U/TEVA, Eichrom and
thiol resins, in stacks of two to five columns with their own volumes, mesh sizes, molarities
and yields. `Multi-step: specify` was the MC table conceding the point one member at a time.

Same defect as `Pulse/Analog Detector Nonlinearity Correction` and `Sample Mounting Method`:
the list is pitched below the level at which the domain closes. The field name and Column B
both ask a WHETHER question — "Whether chromatographic separation ... was performed ... Record
resin type and elution matrix conditions if applied" — so the answer is a state plus the
chemistry, and the `/ Text` half is where the chemistry belongs.

    ->  Yes | N/A | None

`No` is not added: it would collide with `None`, which is the attested negative
(`None (direct analysis of digested solution)`) and is already required on every controlled
list. Column B needs no change; it already asks for the resin and elution conditions and
already defines `None`.

`Yes` rather than `Applied` because 24 of 24 cells say `Yes —`, and because the field's
name-siblings `Spectral Interference Corrections Applied` and `X-ray Line Overlap Corrections
Applied` both use the `Yes — <detail>` form. NOTE this differs from
`Pulse/Analog Detector Nonlinearity Correction`, set to `Applied | N/A | None` earlier today
on ITS attested wording (`Applied:`). Both follow their own evidence, which is the rule this
backlog has used throughout — but the two forms sit oddly together and reconciling them is
worth a decision. Flagged, not settled here.

Column F is overlay on `Module_SolutionIntroduction`, so the TAPP values are authoritative and
this is a TAPP edit; the module's empty seed is filled at the same time so a newly composed
consumer inherits the list rather than a blank.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
ITEM = "Chromatographic Separation Applied"
NEW_F = "Yes | N/A | None"

def main():
    dry = "--apply" not in sys.argv
    # module seed
    m = ROOT / "Claude Skills for TAPP" / "modules" / "Module_SolutionIntroduction.csv"
    rows = list(csv.reader(open(m, encoding="utf-8-sig")))
    h = rows[0]; iA, iF = h.index("Metadata Item"), h.index("Example / Allowed Content")
    for r in rows[1:]:
        if len(r) > iF and r[iA] == ITEM and r[iF].strip() != NEW_F:
            print(f"  module seed F: {r[iF]!r} -> {NEW_F!r}")
            if not dry:
                r[iF] = NEW_F
                with open(m, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        mm = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not mm: continue
        base, ver = mm.group(1), int(mm.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    tot = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iF = hdr.index("Metadata Item"), hdr.index("Example / Allowed Content")
        iU = hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM or r[iF].strip() == NEW_F: continue
            print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {r[iF]}")
            r[iF], r[iU] = NEW_F, STAMP; hit = True; tot += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  now: {NEW_F}\n\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
