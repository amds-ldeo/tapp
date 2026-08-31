#!/usr/bin/env python3
"""Column F completion for four closed electron-beam Controlled lists (2026-08-30).

Step (a) of the Data Type two-type reclassification. Four lists were incomplete against
their own attested literature, three of them from the SAME defect: the list enumerates at a
finer grain than papers report, so a correct coarse answer has nowhere to go. `Electron
Source` showed it plainest -- 14 cells read `Other: FEG (type not specified in paper)`
because the list demands Cold vs Schottky and the paper said only "FEG".

EPMA already carried the coarse member the others lacked (`Field Emission (FEG)`), so this
is largely harmonisation, not invention.

NOT DONE HERE, deliberately: `Other: specify` is KEPT. These fields are still typed
`Controlled list`, and validate_tapp.py:514 requires that option on a plain Controlled list.
Stripping it belongs in the coordinated ~226-cell commit that also changes the validator.

`Technique` is deferred -- its gaps are real but are a Rule 1 cross-TAPP vocabulary matter.
"""
import csv, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"

NEW = {
 "Electron Source":
   "Cold-FEG | Schottky FEG (X-FEG) | Schottky FEG (standard) | "
   "Field emission gun (FEG) — subtype not specified | LaB6 / CeB6 | Tungsten (W) | "
   "Other: specify | Unknown | N/A | None",
 "BSE Detector Type":
   "Solid-state diode (single) | Solid-state diode (segmented, composition mode) | "
   "Solid-state diode (segmented, topography mode) | "
   "Solid-state diode (segmented, mode not specified) | "
   "Solid-state diode (type not specified) | In-lens BSE | YAG scintillator | "
   "Other: specify | N/A | None",
 "X-ray Background Correction Method":
   "2-point off-peak linear | 2-point off-peak exponential | 2-point off-peak polynomial | "
   "2-point off-peak (interpolation not specified) | 1-point high with slope factor | "
   "1-point low with slope factor | Mean Atomic Number (MAN) | EDS background fit | "
   "Top-hat filter | Other: specify | N/A | None",
 "CL Acquisition Mode":
   "Panchromatic | Monochromatic imaging | Spectral point | Hyperspectral map | "
   "Multi-channel pseudo-color | Other: specify | N/A | None",
}

BUMPS = [("EPMA", "EPMA_TAPP", 41), ("SEM", "SEM_TAPP", 40),
         ("SEM", "SEM_Composition_TAPP", 39), ("SEM", "SEM_FIBSEM_TAPP", 23),
         ("SEM", "SEM_Imaging_TAPP", 22), ("TEM", "TEM_TAPP", 35)]

def main():
    dry = "--apply" not in sys.argv
    total = 0
    for folder, base, ver in BUMPS:
        src = ROOT / folder / f"{base}_v{ver}.csv"
        dst = ROOT / folder / f"{base}_v{ver+1}.csv"
        if not src.exists():
            print(f"  MISSING {src}"); return 1
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        hits = []
        for r in rows[1:]:
            if len(r) <= iU or r[iA] not in NEW: continue
            if r[iE].strip() != "Controlled list":
                print(f"  !! {base}: {r[iA]} is '{r[iE]}', expected 'Controlled list' — skipped")
                continue
            if r[iF] == NEW[r[iA]]:
                continue
            hits.append((r[iA], r[iF]))
            r[iF] = NEW[r[iA]]
            r[iU] = STAMP
        print(f"{base}_v{ver} -> v{ver+1}: {len(hits)} cell(s)")
        for name, old in hits:
            print(f"     {name}\n       was: {old[:96]}")
        total += len(hits)
        if not dry:
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{total} cells across {len(BUMPS)} TAPPs")
    return 0

sys.exit(main())
