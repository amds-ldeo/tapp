#!/usr/bin/env python3
"""`Dwell Time per Pixel` — put units in Column F where the type demands them (2026-08-30).

The field is `Numeric + unit` in all six tables that carry it, but EPMA and TEM still hold
the unit-free numerals from before they joined that family: TEM was harmonised from
`Numeric (ms)` on 2026-08-27, EPMA joined earlier, and neither retype carried Column F.
The four SEM tables already show the correct quoted, unit-bearing form.

`Numeric + unit` is right and Column F is the defect. Across the six tables there are only
FIVE attested cells, and 5 of 5 carry a unit, spanning 8 us to 0.5 s — a factor of ~62,000,
which is precisely why no single unit can be pinned:

    EPMA  ~0.5 s per step (olivine megacryst Ka maps)
    TEM   8 us  |  50 us  |  50 us/pixel  |  50 us (kept short to prevent beam damage)

The new examples are authored from those attested values and each technique's real range.
The old bare numerals are NOT reconstructed — their intended unit is unknowable, and
guessing is the defect being fixed. Column F is technique-appropriate allowed content and
legitimately differs between EPMA (ms-s, mapping) and TEM (us-ms, STEM), so these are NOT
harmonised to the SEM string; only the house form (quoted, unit-bearing) is shared.
"""
import csv, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP, ITEM = "2026-08-30", "Dwell Time per Pixel"

NEW = {"EPMA_TAPP": "e.g., '10 ms' | '100 ms' | '0.5 s'",
       "TEM_TAPP":  "e.g., '8 µs' | '50 µs' | '1 ms'"}
BUMPS = [("EPMA", "EPMA_TAPP", 42), ("TEM", "TEM_TAPP", 36)]

def main():
    dry = "--apply" not in sys.argv
    n = 0
    for folder, base, ver in BUMPS:
        src = ROOT / folder / f"{base}_v{ver}.csv"
        dst = ROOT / folder / f"{base}_v{ver+1}.csv"
        if not src.exists():
            print(f"  MISSING {src}"); return 1
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        done = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if r[iE].strip() != "Numeric + unit":
                print(f"  !! {base}: type is '{r[iE]}', expected 'Numeric + unit' — skipped")
                continue
            print(f"{base}_v{ver} -> v{ver+1}\n     was: {r[iF]}\n     now: {NEW[base]}")
            r[iF] = NEW[base]; r[iU] = STAMP; done = True; n += 1
        if not done:
            print(f"  !! {base}: '{ITEM}' row not found or not updated"); return 1
        if not dry:
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{n} cell(s)")
    return 0

sys.exit(main())
