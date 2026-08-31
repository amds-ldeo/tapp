#!/usr/bin/env python3
"""Remove two off-scope paper columns from the Lab-XCT TAPP (2026-08-30).

Found via the `Technique` Column F adjudication: two of Lab-XCT's assessed papers declare a
technique that is not Lab XCT.

    Charles et al. 2018  (MAPS, 10.1111/maps.13038)   Technique = 'Medical CT'
    Treiman et al. 2022  (MAPS, 10.1111/maps.13904)   Technique = 'NXCT'   (neutron CT)

Both are separate techniques with their own folders at the repo root (`Medical CT/`, `NCT/`).
Assessing them inside Lab-XCT inflates that TAPP's evidence base with procedures it does not
describe, and it was `Technique` -- the one field that names the technique -- that caught it.

37 non-empty cells per column. Two fields drop to ZERO attestation as a result:
`CT Number Calibration` (`Controlled list / Text`, classified on that single cell) and
`VOI Selection Criteria` (`Text (free)`). Both survive as no-evidence fields.

The paper registry is GENERATED from the TAPPs, so it is regenerated rather than hand-edited.
The PDFs themselves are untracked and stay where they are.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DROP = ("Charles et al. 2018", "Treiman et al. 2022")

def main():
    dry = "--apply" not in sys.argv
    folder = ROOT / "XCT"
    vs = sorted(int(m.group(1)) for p in folder.glob("Lab-XCT_TAPP_v*.csv")
                if (m := re.fullmatch(r"Lab-XCT_TAPP_v(\d+)", p.stem)))
    if not vs:
        print("no Lab-XCT tables found"); return 1
    ver = vs[-1]
    src = folder / f"Lab-XCT_TAPP_v{ver}.csv"
    rows = list(csv.reader(open(src, encoding="utf-8-sig")))
    hdr = rows[0]
    sent = hdr.index("Literature Assessment")
    idx = [i for i, h in enumerate(hdr) if i > sent and any(d in h for d in DROP)]
    if len(idx) != 2:
        print(f"ABORT: expected 2 columns to drop, found {len(idx)}"); return 1
    for i in idx:
        filled = sum(1 for r in rows[1:] if len(r) > i and r[i].strip() not in ("", "N", "Y", "-"))
        print(f"  dropping col {i}: {hdr[i].splitlines()[0][:60]}  ({filled} non-empty cells)")
    keep = [i for i in range(len(hdr)) if i not in idx]
    out = [[r[i] if i < len(r) else "" for i in keep] for r in rows]
    print(f"\n  columns {len(hdr)} -> {len(out[0])}   rows {len(out)}")
    if not dry:
        dst = folder / f"Lab-XCT_TAPP_v{ver+1}.csv"
        shutil.copyfile(src, dst)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(out)
        print(f"  wrote {dst.name}")
    print(f"\n{'DRY RUN — ' if dry else ''}Lab-XCT_TAPP_v{ver} -> v{ver+1}")
    return 0

sys.exit(main())
