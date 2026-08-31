#!/usr/bin/env python3
"""B3 — Rule 7 keys for two fields whose values repeat but declared `(none)` (2026-08-30).

Three fields were flagged during the Data Type pass for showing per-analyte or per-phase
assignment in their attested cells while carrying `Keyed By: (none)`. Reading them against
their SIBLING CLUSTERS settles two and rules the third out.

`X-ray Background Correction Method` -> `channel`   (EPMA, SEM, SEM_Composition)
    Its whole cluster is already `channel`: `Peak Counting Time`, `Background Counting Time`,
    and decisively `Background Position(s)`, plus `X-ray Line` and `Diffracting Crystal`. The
    background POSITIONS are keyed per channel; the METHOD that interpolates between those
    positions cannot be on a coarser axis. It was the odd one out. The attested cell
    `Mean Atomic Number (MAN) (most analytes); polynomial fit ... (for F, LDE1 crystal)` names
    an element and its crystal -- a channel.

`Beam Mode` -> `sample > sampling unit`             (EPMA, SEM, SEM_Composition)
    Matches `Beam Current` and `Beam Damage Minimization` exactly, the two beam fields already
    keyed. Six of 13 attested cells assign per mineral phase --
    `Focused (olivine, pyroxene, Fe-Ti-Cr oxides); Defocused 5-10 um (maskelynite, phosphate,
    sulfide, glass)` -- and `sampling unit` is the key whose domain covers phases.

`Desolvation System` -> NOT KEYED, left `(none)`.   (3 Solution TAPPs)
    Two reasons. Its entire sample-introduction cluster is scalar -- Torch Type, Nebulizer
    Type, Spray Chamber Type, Cone Material, Nebulizer Gas Flow, Plasma Thermal Mode all
    `(none)` -- so keying it alone would make one hardware field repeat inside a block that
    does not. And its attested variation runs across THREE different axes, not one: per
    analyte (`Apex HF (Cr); Apex Omega (Mg)`), per resolution mode (`Apex for HR-mode dry
    plasma; none for MR-mode wet plasma`) and per session (`used ... in different sessions`).
    The honest axis is `acquisition pass` -- you physically change the introduction path and
    analytes follow whichever pass measured them -- but NO Solution TAPP declares a
    `defines: acquisition pass` field, so Rule 7.4a cannot be satisfied without first adding
    one. That is a modelling decision, not a key edit. Flagged, not done.

Rule 7.4a verified before the fact: all three electron-beam TAPPs declare `sampling unit` and
`defines: channel per analyte` (`WDS Spectrometer Channel`). Neither field is module-owned.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
KEYS = {"X-ray Background Correction Method": "channel",
        "Beam Mode": "sample > sampling unit"}

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
        iA, iK, iU = hdr.index("Metadata Item"), hdr.index("Keyed By"), hdr.index("Last Update")
        present = {r[iA] for r in rows[1:] if len(r) > iA}
        hits = []
        for r in rows[1:]:
            if len(r) <= iU or r[iA] not in KEYS: continue
            want = KEYS[r[iA]]
            if r[iK].strip() == want: continue
            if r[iK].strip() != "(none)":
                print(f"  ABORT: {base} {r[iA]} is '{r[iK]}', expected '(none)'"); return 1
            # Rule 7.4a — the key's domain must be enumerated somewhere in this TAPP
            root = want.split(">")[-1].strip()
            if not any(len(x) > iK and "defines" in x[iK] and root in x[iK] for x in rows[1:]):
                print(f"  ABORT: {base} has no `defines: {root}` field (Rule 7.4a)"); return 1
            hits.append((r[iA], r[iK].strip(), want))
            r[iK], r[iU] = want, STAMP
        if not hits: continue
        print(f"  {base:24s} v{ver} -> v{ver+1}")
        for it, o, n in hits: print(f"       {it[:44]:44s} {o} -> {n}")
        tot += len(hits)
        if not dry:
            dst = src.parent / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
