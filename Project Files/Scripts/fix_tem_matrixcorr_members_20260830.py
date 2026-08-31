#!/usr/bin/env python3
"""Remove two standards-mode members from TEM's `Matrix Correction Method` (2026-08-30).

Follows directly from B8. The field asks which ALGORITHM corrects for matrix effects; two of
its TEM members answer a different question -- where the calibration came from:

    Cliff-Lorimer (k-factor)            algorithm
    zeta-factor                         algorithm
    Absorption-corrected Cliff-Lorimer  algorithm
    Standardless                        <- k-factor SOURCE, not an algorithm
    Direct comparison to reference spectra   <- calibration approach, not an algorithm

Standardless quantification still applies a matrix correction; what makes it standardless is
that the k-factors come from a vendor library or theoretical cross-sections rather than
measured standards. The two axes are orthogonal, and mixing them means a procedure that is
both absorption-corrected AND standardless cannot state both.

TEM ALREADY HAS THE RIGHT HOME and it is already explicit -- `EDS Calibration Standard(s)`
carries `'Cliff-Lorimer k-factors from ThermoFisher Velox manufacturer database (no external
standard)'` and `'None (standardless analysis, relative compositions only)'` among its own
examples. So unlike B8, no description fix is needed there; only a cross-reference from this
field, so the next reader is not left guessing.

Column F change is TEM-ONLY (EPMA/SEM carry XPP/PAP/ZAF instead). That divergence is already
registered PRINCIPLED in COLF_DIVERGENCE_TRIAGED, so no new finding. The Column B sentence is
applied to ALL FOUR consumers and written technique-neutrally -- EPMA/SEM's calibration home is
`Primary Calibration Standard Name`, TEM's is `EDS Calibration Standard(s)` -- because Column B
is uniform across the four and splitting it would trip `colb-divergence`.

Five of TEM's seven attested cells name Cliff-Lorimer and match a surviving member. The other
two are standards-mode answers (`Brown-Powell ionization cross-section model`, `mostly
semiquantitative; standard-based quantification`); the `/ Text` half still admits them and
Column B now points at where they belong. Their cells are NOT moved -- that is the evidence
zone.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Matrix Correction Method"
DROP = {"standardless", "direct comparison to reference spectra"}
B_ADD = (" Where the k-factors or calibration constants themselves came from — measured "
         "standards, a vendor library, or theoretical cross-sections — is a separate question "
         "answered by this technique's calibration-standard field, not here; a procedure may "
         "be both absorption-corrected and standardless.")

def main():
    dry = "--apply" not in sys.argv
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    nb = nf = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if B_ADD.strip() not in r[iB]:
                r[iB] = r[iB].rstrip() + B_ADD; nb += 1; hit = True
            parts = [x.strip() for x in r[iF].split("|")]
            kept = [x for x in parts if x.lower().strip("'\"") not in DROP]
            if len(kept) != len(parts):
                print(f"  {base}: dropping {[x for x in parts if x not in kept]}")
                r[iF] = " | ".join(kept); nf += 1; hit = True
            if hit: r[iU] = STAMP
        if hit:
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            if not dry:
                dst = src.parent / f"{base}_v{ver+1}.csv"
                shutil.copyfile(src, dst)
                with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}Column B: {nb} cells   Column F: {nf} cell(s)")
    return 0

sys.exit(main())
