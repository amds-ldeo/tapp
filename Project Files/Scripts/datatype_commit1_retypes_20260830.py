#!/usr/bin/env python3
"""Data Type reclassification, commit 1 of 3 — retypes only, no validator behaviour change.

Safe to land ahead of the strip because nothing the validator checks today changes:
`CONTROLLED_LIST_REQUIRED` (validate_tapp.py:514) already exempts compounds from the
`Other: specify` requirement (line 762), so moving a field from `Controlled list` to
`Controlled list / Text` relaxes rather than tightens. Every field below retypes across
ALL TAPPs carrying it, so `cole-divergence` stays clean.

`Boolean` is retired here: of 4 attested cells across its 3 fields, only 1 was a bare
Yes/No. Their Column F is rewritten to the attested form, following the
`Spectral Interference Corrections Applied` precedent (precedents.md, 2026-08-27), where
Column F -- not the type -- was the cell that did not match the data.

NOT DONE HERE: the ~213-cell `Other: specify` strip and the two `/ Text` -> `Controlled
list` retypes. Those must land with the validator inversion or they generate ~226 WARN.
`Technique` is held for Rule 1.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"

TO_TEXT = [
 "Plasma Thermal Mode", "Sample Form / Analytical Substrate",
 "Collision/Reaction Cell (CRC) Configuration", "Beam Mode", "Analyte Estimation Method",
 "WDS Dead Time Correction", "Chromatographic Separation Applied", "Desolvation System",
 "Analytical Sub-mode", "Diffraction Camera Length Calibration Method",
 "EELS Background Subtraction Method", "Specimen Thickness Determination Method",
 "Matrix Correction Method",
]
FROM_BOOL = {
 "Halogen Correction on Oxygen":
   "e.g., 'Yes — F and Cl substitution in apatite; O calculated as 1-F-Cl=OH' | 'No' | N/A | None",
 "Flat Field Correction":
   "e.g., 'Yes — flat-field applied; residual Poisson noise from flat-fielding noted' | "
   "'No — flux normalization not applied' | N/A | None",
 "X-ray Line Overlap Corrections Applied":
   "Yes — specify the overlapping lines and the correction method | No | N/A | None",
}
NEW = "Controlled list / Text"

def latest(folder: Path, base: str):
    vs = sorted(int(m.group(1)) for p in folder.glob(f"{base}_v*.csv")
                if (m := re.fullmatch(rf"{re.escape(base)}_v(\d+)", p.stem)))
    return vs[-1] if vs else None

def main():
    dry = "--apply" not in sys.argv
    tables = []
    for csvp in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in csvp.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")):
            continue
        m = re.fullmatch(r"(.+)_v(\d+)", csvp.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver != latest(csvp.parent, base): continue
        tables.append((csvp.parent, base, ver))

    total = 0
    for folder, base, ver in tables:
        src = folder / f"{base}_v{ver}.csv"
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hits = []
        for r in rows[1:]:
            if len(r) <= iU: continue
            item, dt = r[iA], r[iE].strip()
            if item in TO_TEXT and dt == "Controlled list":
                r[iE], r[iU] = NEW, STAMP; hits.append((item, "Controlled list -> / Text", None))
            elif item in FROM_BOOL and dt == "Boolean":
                oldF = r[iF]
                r[iE], r[iF], r[iU] = NEW, FROM_BOOL[item], STAMP
                hits.append((item, "Boolean -> / Text", oldF))
        if not hits: continue
        print(f"{base}_v{ver} -> v{ver+1}  ({len(hits)} cell(s))")
        for item, what, oldF in hits:
            print(f"     {what:26s} {item}")
            if oldF is not None:
                print(f"        Column F: {oldF}  ->  {FROM_BOOL[item][:74]}")
        total += len(hits)
        if not dry:
            dst = folder / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{total} cells")
    return 0

sys.exit(main())
