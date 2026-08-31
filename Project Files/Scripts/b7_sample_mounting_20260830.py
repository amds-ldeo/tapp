#!/usr/bin/env python3
"""B7 — rebuild `Sample Mounting Method`'s vocabulary from the literature (2026-08-30).

Flagged during the Data Type pass as the clearest case of a vocabulary that was invented
rather than observed: of the attested cells, five of six name a vessel the list does not
contain.

    was:  Free-standing on stage pin | Mounted in plastic straw | Mounted in glass capillary |
          Mounted with wax | Mounted in modeling clay | Placed on flat quartz window |
          Wrapped in PTFE tape | Free-standing without holder | N/A | None

    attested:  Mounted in pipette tips
               Plexiglass tube (vertical); triple-sealed Teflon bag
               Custom PVC tube
               Triple-bagged in Teflon, wrapped in cylinder, placed in 1-cm plastic straw
               Glass vial placed in scanner
               Polystyrene support

THE DEFECT IS THE GRAIN, NOT THE MEMBERS. The old list enumerates SPECIFIC VESSELS -- straw,
capillary, quartz window, PTFE tape, wax, clay -- and that domain is unbounded: any container
can hold a sample, and the literature duly supplies pipette tips, plexiglass tubes, PVC tubes,
glass vials and polystyrene. No amount of extending fixes it. Enumerating HOLDER CLASSES does,
and the `/ Text` half already exists to carry the specific vessel. This is the mirror of the
`Electron Source` fix: there the list was too FINE for what papers report and needed a coarse
member; here it is too SPECIFIC and needs a coarser axis throughout.

Two of the six cells also show a pattern the old list had no concept of -- CONTAINMENT PLUS A
SEALING LAYER (`triple-sealed Teflon bag` inside a plexiglass tube; `triple-bagged in Teflon`
then inside a straw), which is contamination control for planetary material. Column B gains a
sentence asking for both layers rather than forcing a choice between them.

Not module-owned; Lab-XCT only.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
ITEM = "Sample Mounting Method"

NEW_F = ("Free-standing on stage pin | Free-standing without holder | Tube or vial | "
         "Glass capillary | Sealed bag or wrap | Embedded or adhered | "
         "On a flat support or substrate | Fixed to the stage or gantry | N/A | None")
NEW_B = ("Method used to mount or hold the sample on the instrument rotation stage. Mounting "
         "material should transmit X-rays at the selected voltage without dominating beam "
         "attenuation. Report the holder CLASS from the list and name the specific vessel or "
         "material alongside it — 'Tube or vial — 1 cm plastic straw', not 'Tube or vial'. "
         "Where the sample is sealed or bagged inside a further holder for contamination "
         "control, record both layers. Report any adhesive, support material and alignment "
         "aids used.")

def main():
    dry = "--apply" not in sys.argv
    folder = next((d for d in ROOT.iterdir() if d.is_dir() and d.name == "XCT"), None)
    if folder is None:
        print("ABORT: no XCT folder"); return 1
    vs = sorted(int(m.group(1)) for p in folder.glob("Lab-XCT_TAPP_v*.csv")
                if (m := re.fullmatch(r"Lab-XCT_TAPP_v(\d+)", p.stem)))
    if not vs:
        print("ABORT: no Lab-XCT tables"); return 1
    ver = vs[-1]
    src = folder / f"Lab-XCT_TAPP_v{ver}.csv"
    rows = list(csv.reader(open(src, encoding="utf-8-sig")))
    hdr = rows[0]
    iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
    iE, iF = hdr.index("Data Type"), hdr.index("Example / Allowed Content")
    iU = hdr.index("Last Update")
    hit = 0
    for r in rows[1:]:
        if len(r) <= iU or r[iA] != ITEM: continue
        if r[iE].strip() != "Controlled list / Text":
            print(f"ABORT: type is '{r[iE]}', expected 'Controlled list / Text'"); return 1
        print(f"Lab-XCT_TAPP_v{ver} -> v{ver+1}")
        print(f"  F was: {r[iF]}")
        print(f"  F now: {NEW_F}")
        print(f"  B gains the holder-class instruction and the two-layer sentence")
        r[iF], r[iB], r[iU] = NEW_F, NEW_B, STAMP
        hit += 1
    if hit != 1:
        print(f"ABORT: expected 1 '{ITEM}' row, found {hit}"); return 1
    if not dry:
        dst = folder / f"Lab-XCT_TAPP_v{ver+1}.csv"
        shutil.copyfile(src, dst)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        print(f"  wrote {dst.name}")
    print(f"\n{'DRY RUN — ' if dry else ''}1 field rebuilt")
    return 0

sys.exit(main())
