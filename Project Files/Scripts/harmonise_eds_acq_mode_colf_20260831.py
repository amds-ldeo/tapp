#!/usr/bin/env python3
"""`EDS Acquisition Mode` — harmonise the shared core, keep the technique-specific members,
and reclassify the entry PRINCIPLED (2026-08-31). 7.8.11 backlog.

    [2] SEM, SEM_Composition  Point / spot | Line scan | Map | Automated mineralogy |
                              Multiple (specify) | N/A | None
    [1] EPMA                  'Point' | 'Linescan' | 'Map' | N/A | None
    [1] TEM                   Point analysis | Line scan | Spectrum image (map) |
                              Simultaneous EDS+EELS | N/A | None

THE FIRST BACKLOG ENTRY THAT DOES NOT FULLY HARMONISE, and the reason is worth stating: two of
the members name capabilities the other techniques do not have. `Simultaneous EDS+EELS` is
meaningless outside TEM -- SEM and EPMA have no electron energy-loss spectrometer -- and
`Automated mineralogy` (QEMSCAN, TIMA) is an SEM platform. A uniform list would offer every
EPMA user a mode their instrument cannot perform. That is the `ICP-MS Type` situation: scoping,
not drift.

So the divergence is split. The SHARED CORE was drift and is harmonised; the technique-specific
members stay, and the entry moves from BACKLOG to PRINCIPLED rather than being deleted -- the
first to leave the backlog that way. The test applied: a member is principled if it names a
capability the technique does not have.

Three fixes in the core, all evidence-led against 27 attested cells:

  * `Point` -- one spelling for `Point / spot`, `'Point'` and `Point analysis`. The literature
    uses both words (`Spot analysis`, `Point spectra (spot analysis)`, `point analysis`), so
    Column B glosses the synonym rather than the member carrying a slash that reads like a
    separator.
  * `Line scan` over `'Linescan'` -- 2 of 3 tables and the attested form.
  * `Map` AND `Spectrum image` as SEPARATE members. This is not a naming choice: they are
    different acquisitions. A map may retain element intensities only; a spectrum image retains
    a full spectrum per pixel and can be requantified afterwards. The literature reports both --
    `Element mapping`, `EDS mapping` against `Spectrum image (map)` x5,
    `Spectrum image (hyperspectral map)` -- and every table offered only one of them, so the
    distinction could not be recorded anywhere.

`Multiple (specify)` is dropped from the SEM tables. Composite acquisitions are attested
(`Point / spot; Map`, `Line scan; Spectrum image (map)`) and the `; ` join convention already
sanctioned for `Analytical Mode` under Rule 3 expresses them without a catch-all member --
the same swap made for `CL Acquisition Mode`.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
ITEM = "EDS Acquisition Mode"
CORE = "Point | Line scan | Map | Spectrum image"
TARGET = {
 "EPMA_TAPP":            f"{CORE} | N/A | None",
 "SEM_TAPP":             f"{CORE} | Automated mineralogy | N/A | None",
 "SEM_Composition_TAPP": f"{CORE} | Automated mineralogy | N/A | None",
 "TEM_TAPP":             f"{CORE} | Simultaneous EDS+EELS | N/A | None",
}
B_ADD = (" 'Point' covers what the literature also calls spot or point-spectrum analysis. "
         "'Map' and 'Spectrum image' are distinct acquisitions, not synonyms: a map may retain "
         "element intensities alone, whereas a spectrum image retains a full spectrum at every "
         "pixel and can be requantified afterwards — record which was acquired. Where more than "
         "one mode was used, join them with '; ' rather than looking for a combined member.")

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
            if base not in TARGET:
                print(f"  ABORT: {base} carries {ITEM} but has no target list defined"); return 1
            if r[iF].strip() != TARGET[base]:
                print(f"  {base:24s} v{ver} -> v{ver+1}\n      was: {r[iF]}\n      now: {TARGET[base]}")
                r[iF] = TARGET[base]; hit = True; tot += 1
            if B_ADD.strip() not in r[iB]:
                r[iB] = r[iB].rstrip() + B_ADD; hit = True
            if hit: r[iU] = STAMP
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} Column F cells (+ Column B on each)")
    return 0

sys.exit(main())
