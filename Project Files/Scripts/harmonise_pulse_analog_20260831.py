#!/usr/bin/env python3
"""`Pulse/Analog Detector Nonlinearity Correction` — 7.8.11 backlog (2026-08-31).

Three Column F variants across six TAPPs, and reading them shows the members are not a
vocabulary at all -- they are SENTENCES, each variant pre-writing different specific
procedures as list members:

    [4] LA        Not applicable (instrument uses pulse counting only) |
                  Applied: describe method and elements affected |
                  Not applied (crossover threshold not reached for any element) |
                  Not applied (known bias accepted) | N/A | None
    [1] Sol Q     Applied: cross-calibration factor measured per session and applied at
                  crossover threshold | Not applied (all signals in pulse-counting mode) |
                  Not applicable (pulse-counting only) | N/A | None
    [1] Sol SF    Applied: SEM-to-analog and analog-to-Faraday cross-calibration factors
                  measured per session | Applied: SEM-to-analog cross-calibration factor
                  applied | Not applied (all signals in pulse-counting mode) | N/A | None

THE GRAIN IS WRONG, the same defect as `Sample Mounting Method`: there the list enumerated
specific vessels, here it enumerates specific correction procedures, and both domains are
unbounded. The literature confirms it -- all 15 attested cells begin `Applied:` and continue
with detail (`triple mode detection at 65% duty cycle`, `SEM-to-analog cross-calibration
performed daily`, `dual detector mode (30 ms / 10 ms dwell alternation)`), and NOT ONE matches
any of those elaborate members. The lists were pre-writing the `/ Text` half.

The real axis is three-valued, and two of the three states are already the conventional
values every controlled list carries:

    Applied   a correction was made -- the text says how
    None      a crossover exists on this instrument and no correction was applied -- why
    N/A       no pulse-to-analog crossover exists (pulse-counting-only detector)

So `Not applied` is dropped: it collides with `None`, exactly as `Not applicable (instrument
uses pulse counting only)` collides with `N/A` -- the same collision fixed in `Guard Electrode`
on 2026-08-30. Keeping both halves of a collision means whichever a curator picks, the other
becomes noise.

Column B is harmonised too, from three variants to one. It absorbs the Solution SF text (the
only one covering triple-mode Faraday instruments) and adds the three-state definition, so the
distinction between `None` and `N/A` is stated where someone choosing a value will read it --
the same "the description is what sent them there" fix as B8 and B9.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-31"
ITEM = "Pulse/Analog Detector Nonlinearity Correction"
NEW_F = "Applied | N/A | None"
NEW_B = ("Whether a correction was applied for nonlinear detector response at the transition "
         "between pulse-counting and analog (and Faraday, for triple-mode instruments) "
         "detection modes. Cross-calibration factors between detector modes must be confirmed, "
         "typically measured each session. Record 'Applied' and describe the method, the "
         "detector modes involved and the analytes affected; 'None' where a crossover exists "
         "on this instrument but no correction was made, giving the reason; and 'N/A' where the "
         "detector is pulse-counting only and no crossover exists.")

def main():
    dry = "--apply" not in sys.argv
    seen = {}
    for p in sorted(ROOT.glob("*/*_TAPP_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get(base, (-1, None))[0]: seen[base] = (ver, p)
    nf = nb = 0
    for base, (ver, src) in sorted(seen.items()):
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iB = hdr.index("Metadata Item"), hdr.index("Description")
        iE, iF = hdr.index("Data Type"), hdr.index("Example / Allowed Content")
        iU = hdr.index("Last Update")
        hit = False
        for r in rows[1:]:
            if len(r) <= iU or r[iA] != ITEM: continue
            if r[iE].strip() != "Controlled list / Text":
                print(f"  ABORT: {base} type is '{r[iE]}'"); return 1
            if r[iF].strip() != NEW_F:
                print(f"  {base:24s} v{ver} -> v{ver+1}\n      F was: {r[iF][:104]}")
                r[iF] = NEW_F; nf += 1; hit = True
            if r[iB].strip() != NEW_B:
                r[iB] = NEW_B; nb += 1; hit = True
            if hit: r[iU] = STAMP
        if hit and not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n  F now: {NEW_F}\n\n{'DRY RUN — ' if dry else ''}Column F: {nf}   Column B: {nb}")
    return 0

sys.exit(main())
