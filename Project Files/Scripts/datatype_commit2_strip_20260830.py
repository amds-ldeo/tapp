#!/usr/bin/env python3
"""Data Type reclassification, commit 2 of 3 — the coupled commit.

`Other: specify` leaves the vocabulary. Under the two-type scheme it is wrong in both
places: on a `Controlled list` it contradicts the type (the type says closed, the option
says otherwise, and nothing could see the contradiction -- that is how `Technique` drifted
open in 13 of 16 TAPPs unnoticed); on a `Controlled list / Text` it is the WRONG PROMPT,
not merely redundant, because a compound wants a term PLUS qualification, not "pick
something else". The user-facing guidance moves to a Data Type table on the generated xlsx
Legends sheet -- stated once where people read it, instead of 226 inline repetitions that
can drift out of sync with the type.

MUST land with the validate_tapp.py inversion: CONTROLLED_LIST_REQUIRED (line 514) demands
`Other: specify` on a plain `Controlled list` today, so stripping alone would generate
~226 WARN on a clean baseline.

HELD: `Technique`'s 13 cells. Closing a list that is known incomplete is precisely what
produced amds-ldeo/tapp#3 -- three TAPPs' lists still omit their own technique. It closes
in commit 3, after Rule 1 settles the cross-TAPP technique vocabulary.

Also here, because both fields are being CLOSED in this commit and their Column F is
incoherent with a closed type:
  * `Laser Beam Energy Profile` drops `Not stated` as an allowed VALUE -- absence is what
    an empty cell means, not a member of the domain.
  * `Triple Scanning Mode` moves `Y | N` -> `Yes | No`, matching the ex-Boolean fields.
"""
import csv, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-08-30"
HOLD = {"Technique"}                       # Rule 1 — commit 3
TO_CLOSED = {"Laser Beam Energy Profile", "X-ray Tube Anode Material"}
CLOSED = "Controlled list"

def strip_other(ex: str) -> str:
    parts = [p.strip() for p in ex.split("|")]
    kept = [p for p in parts if p.strip().strip("'\"").lower() != "other: specify"]
    return " | ".join(kept)

def fix_members(item: str, ex: str) -> str:
    if item == "Laser Beam Energy Profile":
        ex = " | ".join(p.strip() for p in ex.split("|")
                        if p.strip().strip("'\"").lower() != "not stated")
    if item == "Triple Scanning Mode":
        ex = re.sub(r"(?<![A-Za-z])Y(?![A-Za-z])", "Yes", ex, count=1)
        ex = re.sub(r"(?<![A-Za-z])N(?![A-Za-z/])", "No", ex, count=1)
    return ex

def latest_tables():
    out, seen = [], {}
    for p in sorted(ROOT.glob("*/*_v*.csv")):
        if any(x in p.parts for x in ("Archive", "Superseded TAPPs", "Current TAPPs")): continue
        m = re.fullmatch(r"(.+)_v(\d+)", p.stem)
        if not m: continue
        base, ver = m.group(1), int(m.group(2))
        if ver > seen.get((p.parent, base), -1):
            seen[(p.parent, base)] = ver
    for (folder, base), ver in seen.items(): out.append((folder, base, ver))
    return sorted(out, key=lambda x: x[1])

def main():
    dry = "--apply" not in sys.argv
    tot = {"strip": 0, "retype": 0, "members": 0, "held": 0}
    for folder, base, ver in latest_tables():
        src = folder / f"{base}_v{ver}.csv"
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        iA, iE = hdr.index("Metadata Item"), hdr.index("Data Type")
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        hits = []
        for r in rows[1:]:
            if len(r) <= iU: continue
            item, dt, ex = r[iA], r[iE].strip(), r[iF]
            changed = False
            if item in TO_CLOSED and dt == "Controlled list / Text":
                r[iE] = CLOSED; dt = CLOSED; changed = True
                tot["retype"] += 1; hits.append(("retype -> Controlled list", item))
            if item in HOLD:
                if "Other: specify" in ex: tot["held"] += 1
                continue
            if dt.startswith("Controlled list"):
                new = fix_members(item, ex)
                if new != ex: tot["members"] += 1; hits.append(("members", item))
                if "Other: specify" in new:
                    new = strip_other(new); tot["strip"] += 1; hits.append(("strip", item))
                if new != ex: r[iF] = new; changed = True
            if changed: r[iU] = STAMP
        if not hits: continue
        print(f"{base}_v{ver} -> v{ver+1}   " +
              ", ".join(f"{k}×{sum(1 for a,_ in hits if a==k)}"
                        for k in ("strip","retype","members")
                        if any(a==k for a,_ in hits)))
        for a, i in hits:
            if a != "strip": print(f"     {a:26s} {i}")
        if not dry:
            dst = folder / f"{base}_v{ver+1}.csv"
            shutil.copyfile(src, dst)
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(rows)
    print(f"\n{'DRY RUN — ' if dry else ''}strip {tot['strip']} | retype {tot['retype']} | "
          f"member-fix {tot['members']} | HELD (Technique) {tot['held']}")
    return 0

sys.exit(main())
