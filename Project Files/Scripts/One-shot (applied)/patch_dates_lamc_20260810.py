#!/usr/bin/env python3
"""
Date cleanup, part 2: the two LA-MC-ICP-MS files (96 `date-missing` findings).

Deferred from `patch_dates_20260810.py` while a separate session rewrote these
files to add literature assessment columns. That work has landed, so they are
finished here using the same method.

The method is unchanged: column H is "the date of the most recent substantive
edit to each row", so each date is COMPUTED by walking a chronological chain of
versions and finding the last one in which a row's description, both tiers, or
data type actually changed. Nothing is blanket-stamped.

What differs is the chain. LA-MC carries fields the LA-Q/SF lineage never had —
the `MCICPMS`, `Geochronology` and `UPb` module blocks — so walking only the
LA-Q/SF lineage would leave those unresolved. The chain is extended along the
real derivation path recorded in `composed_tapps.json`:

    LA-MC-ICPMS_TAPP_v2      <- LA-MC-ICPMS_TAPP_v1 <- LA-Q_SF-ICPMS_TAPP_v5
    LA-MC-ICPMS_UPb_TAPP_v1  <- LA-MC-ICPMS_TAPP_v1 <- LA-Q_SF-ICPMS_TAPP_v5

so a field inherited unchanged from LA-Q/SF keeps its original May/June/July
date; a field introduced by module composition resolves to 2026-08-08 when
LA-MC v1 was built; and anything genuinely new or changed in v2 resolves to
2026-08-10.

Note LA-MC-ICPMS_TAPP_v1.csv is retained on disk and is load-bearing here as a
chain link, even though v2 supersedes it.

Run with --apply; default is a dry run.
"""
import collections
import csv
import datetime
import os
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
ARCH = ROOT / "Superseded TAPPs (2026-08-10)" / "LA-ICP-MS (stale branch)"
LAQSF = ROOT / "LA-Q_SF-ICP-MS"
LAMC = ROOT / "LA-MC-ICP-MS"

# Shared ancestry, identical to part 1.
BASE = [
    ARCH / "LA-ICPMS_TAPP_v6.csv",
    ARCH / "LA-ICPMS_TAPP_v7.csv",
    ARCH / "LA-ICPMS_TAPP_v8.csv",
    ARCH / "LA-ICPMS_TAPP_v9.csv",
    ARCH / "LA-ICPMS_TAPP_v10.csv",
    ARCH / "LA-ICPMS_TAPP_v11.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v1.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v2.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v3.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v4.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v4.1.csv",
    LAQSF / "LA-Q_SF-ICPMS_TAPP_v5.csv",
]

CHAINS = {
    LAMC / "LA-MC-ICPMS_TAPP_v2.csv":
        BASE + [LAMC / "LA-MC-ICPMS_TAPP_v1.csv", LAMC / "LA-MC-ICPMS_TAPP_v2.csv"],
    LAMC / "LA-MC-ICPMS_UPb_TAPP_v1.csv":
        BASE + [LAMC / "LA-MC-ICPMS_TAPP_v1.csv", LAMC / "LA-MC-ICPMS_UPb_TAPP_v1.csv"],
}

# Version dates are PINNED rather than read from filesystem mtime.
#
# Part 1 could safely use mtime because none of its chain had been touched. That
# is no longer true: today's own patches (dates, group-header flags, the Column F
# fill) rewrote LA-Q_SF v5 and both LA-MC files, pushing their mtimes to
# 2026-08-10. Reading mtime now would date every field that last changed at one
# of those links to today — silently converting "composed on 08-08" into "edited
# today", which is exactly the fabricated provenance this method exists to avoid.
#
# The values below are the dates captured in the lineage survey BEFORE any of
# today's edits, plus the build dates recorded in composed_tapps.json.
PINNED = {
    "LA-ICPMS_TAPP_v6.csv": "2026-05-06",
    "LA-ICPMS_TAPP_v7.csv": "2026-05-07",
    "LA-ICPMS_TAPP_v8.csv": "2026-05-13",
    "LA-ICPMS_TAPP_v9.csv": "2026-05-13",
    "LA-ICPMS_TAPP_v10.csv": "2026-05-14",
    "LA-ICPMS_TAPP_v11.csv": "2026-05-14",
    "LA-Q_SF-ICPMS_TAPP_v1.csv": "2026-05-22",
    "LA-Q_SF-ICPMS_TAPP_v2.csv": "2026-06-01",
    "LA-Q_SF-ICPMS_TAPP_v3.csv": "2026-06-17",
    "LA-Q_SF-ICPMS_TAPP_v4.csv": "2026-07-24",
    "LA-Q_SF-ICPMS_TAPP_v4.1.csv": "2026-07-28",
    "LA-Q_SF-ICPMS_TAPP_v5.csv": "2026-08-08",
    "LA-MC-ICPMS_TAPP_v1.csv": "2026-08-08",      # composed, per composed_tapps.json
    "LA-MC-ICPMS_UPb_TAPP_v1.csv": "2026-08-08",  # composed, per composed_tapps.json
    "LA-MC-ICPMS_TAPP_v2.csv": "2026-08-10",      # literature assessment transfer
}


def is_group_header(name):
    return bool(name) and name[0].isdigit() and "." in name[:3]


def read(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    return rows[0], rows[1:]


def signatures(path):
    _, body = read(path)
    sig = {}
    for r in body:
        if not r or not r[0].strip():
            continue
        n = r[0].strip()
        if is_group_header(n):
            continue
        sig[n] = tuple((r[i].strip() if len(r) > i else "") for i in (1, 2, 3, 4))
    return sig


def version_date(path):
    try:
        return PINNED[path.name]
    except KeyError:
        raise SystemExit(
            f"refusing to guess a version date for {path.name} — add it to PINNED. "
            f"mtime is unreliable here because today's patches rewrote several "
            f"chain links.")


def last_change_map(chain):
    last, prev = {}, {}
    for p in chain:
        d = version_date(p)
        sig = signatures(p)
        for name, s in sig.items():
            if name not in prev or prev[name] != s:
                last[name] = d
        prev = sig
    return last


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — date cleanup part 2 (LA-MC-ICP-MS)\n")
    for target, chain in CHAINS.items():
        missing = [p for p in chain if not p.exists()]
        if missing:
            print(f"  ABORT {target.name}: missing chain link(s) {[m.name for m in missing]}")
            continue
        lastmap = last_change_map(chain)
        hdr, body = read(target)
        H = hdr.index("Last Update")
        filled, unresolved = [], []
        for r in body:
            if not r or not r[0].strip():
                continue
            name = r[0].strip()
            if is_group_header(name):
                continue
            while len(r) <= H:
                r.append("")
            if r[H].strip():
                continue
            d = lastmap.get(name)
            if d:
                r[H] = d
                filled.append(d)
            else:
                unresolved.append(name)
        if APPLY and filled:
            with open(target, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows([hdr] + body)
        print(f"  {target.name}  (chain of {len(chain)})")
        print(f"      filled {len(filled)}, unresolved {len(unresolved)}")
        for d, c in sorted(collections.Counter(filled).items()):
            print(f"        {d}  x{c}")
        if unresolved:
            print(f"        UNRESOLVED: {unresolved}")
        print()
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
