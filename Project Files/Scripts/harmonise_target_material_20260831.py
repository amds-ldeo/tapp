#!/usr/bin/env python3
"""`Target Material` — harmonise the in-situ family, leave the bulk family, PRINCIPLED
(2026-08-31). The last 7.8.11 backlog entry.

Seven variants across 16 TAPPs at 0.09 overlap, the lowest in the library — but they split on
TWO AXES, and only one of the splits is drift.

PRINCIPLED: in-situ targets a PHASE WITHIN a specimen; bulk targets the SPECIMEN.
    LA, SEM, EPMA, TEM   Silicate mineral | Oxide | Sulfide | Carbonate | Phosphate ...
    Solution x3          Basalt | Chondrite | Peridotite | Seawater | Synthetic solution ...
    Lab-XCT              Chondrite meteorite | Lunar sample | Drill core | Sediment core ...
A Solution ICP-MS procedure does not target olivine; it digests a basalt. A uniform list would
offer the electron-beam tables `Seawater`. Same test as `Sample Preparation Method`. The bulk
tables are NOT touched.

DRIFT, inside the in-situ family, and the LA list carries all of it:
  * LA enumerates NAMED MINERALS (`Feldspar | Pyroxene | Olivine`) where SEM, EPMA and TEM
    enumerate CLASSES (`Silicate mineral`). Named minerals are unbounded — LA's list has no
    spinel, amphibole, garnet, zircon or apatite, all of which its own papers analyse. The
    grain lesson from `Sample Mounting Method`: enumerate classes, let `/ Text` carry the
    species.
  * `Iron meteorite` is a SPECIMEN type in a phase list — the bulk axis leaking in. All six of
    its attested cells write `Iron meteorite metal (kamacite + taenite)`: the material is metal,
    the specimen is the meteorite. Same defect as `FESEM` in `Instrument Variant`.
  * Three concepts worded three ways: `Native metal` vs `Metal alloy`; `Glass` vs
    `Silicate glass`; `Whole rock` vs `Whole rock / polished section` (the preparation half of
    which `Sample Preparation Method` owns).
  * `Organic matter / IOM` vs `Organic matter` — IOM is a species, so it belongs in `/ Text`.

THE LA CELLS CONFIRM ALL OF IT. Of 13 distinct LA values, NOT ONE is a bare member: every one
reads `<specimen> <phase> (<specifics>)` — `Pallasite olivine ([Mg,Fe]2SiO4)`,
`Martian meteorite (Tissint) phosphate: sodium-merrillite`. And four of LA's thirteen members
— `Feldspar`, `Native metal`, `Whole rock`, `Melt inclusion` — have ZERO attested cells.
`Melt inclusion` and `Fluid inclusion` are kept anyway: they are genuine LA-ICP-MS targets and
a real phase distinction, absent from this paper set rather than from the technique.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
ITEM = "Target Material"
CORE = "Silicate mineral | Silicate glass | Oxide | Sulfide | Carbonate | Phosphate | Metal or alloy"
TARGET = {
 "EPMA_TAPP":            f"{CORE} | N/A | None",
 "TEM_TAPP":             f"{CORE} | Organic matter | Amorphous phase | Nanoparticle | N/A | None",
 "SEM_TAPP":             f"{CORE} | Organic matter | Regolith | Porous material | Whole rock | N/A | None",
 "SEM_Composition_TAPP": f"{CORE} | Organic matter | Regolith | Porous material | Whole rock | N/A | None",
 "SEM_FIBSEM_TAPP":      f"{CORE} | Organic matter | Regolith | Porous material | Whole rock | N/A | None",
 "SEM_Imaging_TAPP":     f"{CORE} | Organic matter | Regolith | Porous material | Whole rock | N/A | None",
}
for la in ("LA-MC-ICPMS_TAPP", "LA-MC-ICPMS_UPb_TAPP", "LA-Q-ICP-MS_TAPP",
           "LA-Q-ICP-MS_UPb_TAPP", "LA-SF-ICP-MS_TAPP", "LA-SF-ICP-MS_UPb_TAPP"):
    TARGET[la] = f"{CORE} | Fluid inclusion | Melt inclusion | Whole rock | N/A | None"
UNTOUCHED = {"Solution_Q-ICP-MS_TAPP", "Solution_SF-ICP-MS_TAPP", "Solution_MC-ICP-MS_TAPP",
             "Lab-XCT_TAPP"}

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
        iA, iF, iU = hdr.index("Metadata Item"), hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if base in UNTOUCHED:
                print(f"  {base:24s} bulk axis — left unchanged"); continue
            if base not in TARGET:
                print(f"  ABORT: {base} carries {ITEM} but has no target defined"); return 1
            if r[iF].strip() == TARGET[base]: continue
            print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {r[iF][:120]}")
            r[iF], r[iU] = TARGET[base], STAMP; hit = True; tot += 1
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  in-situ core: {CORE}\n\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
