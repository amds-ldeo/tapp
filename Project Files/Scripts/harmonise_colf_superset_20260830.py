#!/usr/bin/env python3
"""Two more 7.8.11 backlog entries, both pure missing-member cases (2026-08-30).

After `Plasma Thermal Mode` turned out to be a missing member rather than the verbosity its
triage note claimed, I measured the remaining 12 for that shape instead of trusting the notes:
in how many is one variant a strict SUPERSET of every other? Three. Those are lossless to fix
-- the shorter lists gain members, none is removed -- and two of the three hold up on reading.

`Diffracting Crystal`  (EPMA superset; SEM, SEM_Composition short by PETJ, LTAP, ADP)
    My triage note guessed this "may be PRINCIPLED -- crystal availability is instrument-
    dependent". It is not. Column F is the vocabulary for the TECHNIQUE, not for one lab's
    spectrometer, and SEM-WDS uses the same crystal families as EPMA. The SEM tables were
    simply shorter.

`Stage Scan vs. Beam Scan`  (EPMA superset; SEM, SEM_Composition short by `Combined stage and
    beam scan` and `Unknown`, and quoting their members)
    A stage+beam combination is not an EPMA-only capability. The quoting is dropped with it.

NOT DONE -- `Collision/Reaction Cell (CRC) Configuration` is NOT the clean superset it appeared
to be. The Q tables carry two members the MC tables lack:
  * `KED+DRC` is a genuine combined mode and applies to any cell instrument -- additive.
  * `ICP-MS/MS (triple-quadrupole mode)` is NOT: a Nu Sapphire or Thermo Neoma MS/MS has a
    pre-cell mass filter and a multi-collector array, not a triple quadrupole, so copying that
    wording into the MC tables would state something false. MC MS/MS is attested in the MC
    tables' own `ICP-MS Type` list but in no MC literature cell, so the correctly-worded member
    would be authored on no evidence.
That needs a decision, not a sweep, and is left on the backlog.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
TARGETS = {
 "Diffracting Crystal":
   ("LIF | LLIF | LIFL | LIFH | PET | LPET | PETL | PETH | PETJ | TAP | TAPL | TAPH | LTAP | "
    "LDE1 | LDE2 | LDE3 | RAP | KAP | ADP | Unknown | N/A | None"),
 "Stage Scan vs. Beam Scan":
   "Stage scan | Beam scan | Combined stage and beam scan | Unknown | N/A | None",
}

def members(ex):
    return {re.sub(r"\s+", " ", v.strip().strip("'\"")).lower() for v in ex.split("|") if v.strip().strip("'\"")}

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
        hit = []
        for r in rows[1:]:
            if len(r) <= iU or r[iA] not in TARGETS: continue
            want = TARGETS[r[iA]]
            if r[iF].strip() == want: continue
            lost = members(r[iF]) - members(want)
            if lost:
                print(f"  ABORT: {base} {r[iA]} would LOSE members {sorted(lost)} — not additive")
                return 1
            gained = sorted(members(want) - members(r[iF]))
            hit.append((r[iA], gained))
            r[iF], r[iU] = want, STAMP; tot += 1
        if hit:
            print(f"  {base:24s} v{ver} -> v{ver+1}")
            for it, g in hit: print(f"       {it[:38]:38s} + {g}")
            if not dry:
                dst = src.parent / f"{base}_v{ver+1}.csv"
                shutil.copyfile(src, dst)
                with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                    csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}{tot} cells")
    return 0

sys.exit(main())
