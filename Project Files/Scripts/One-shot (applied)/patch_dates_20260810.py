#!/usr/bin/env python3
"""
Date cleanup, 2026-08-10.

Two distinct problems, fixed differently.

(A) date-format, 22 rows, EPMA only. `5/11/26` -> `2026-05-11`.
    Disambiguated, not assumed: EPMA's other dates cluster at 2026-05-13 (32
    rows), so M/D/YY puts this two days earlier. The D/M/YY reading would be
    2026-11-05 — a future date, today being 2026-08-10. Only one reading is
    possible.

(B) date-missing, 98 rows across LA-Q/SF v5 and its U-Pb variant. These were
    never initialised — v4.1 had exactly the same 49 empty, and 0 were lost
    between v4.1 and v5, so this is not a composition bug.

    conventions.md defines column H as "the date of the most recent substantive
    edit to each row". So rather than stamping one blanket date, each field's
    date is COMPUTED by walking the development lineage in chronological order
    and finding the last version in which that row's substantive content —
    description, procedure tier, analysis tier, data type — actually changed.
    A field that has not been touched since May gets its May date, not today's.

    The lineage (mtime = version date; maxH <= mtime in every file, so mtime is
    the safe proxy for when the version was produced):

      v6 05-06, v7 05-07, v8 05-13, v9 05-13, v10 05-14, v11 05-14,
      LA-Q/SF v1 05-22, v2 06-01, v3 06-17, v4 07-24, v4.1 07-28, v5 08-08

    LA-ICPMS v12/v13 are excluded: they are the stale parallel branch, and their
    content duplicates LA-Q/SF v1/v2 which already precede them.

NOT touched: LA-MC-ICPMS_TAPP_v1.csv and LA-MC-ICPMS_UPb_TAPP_v1.csv (96
date-missing findings). A separate session is currently rewriting those files to
v2 to add literature assessment columns. Editing them concurrently would clobber
that work. They inherit the same empties from LA-Q/SF v5 and should get the same
treatment afterwards.

Run with --apply; default is a dry run.
"""
import csv
import datetime
import os
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv

ARCH = ROOT / "Superseded TAPPs (2026-08-10)" / "LA-ICP-MS (stale branch)"

# Chronological development line. Stale-branch v12/v13 deliberately omitted.
LINEAGE = [
    ARCH / "LA-ICPMS_TAPP_v6.csv",
    ARCH / "LA-ICPMS_TAPP_v7.csv",
    ARCH / "LA-ICPMS_TAPP_v8.csv",
    ARCH / "LA-ICPMS_TAPP_v9.csv",
    ARCH / "LA-ICPMS_TAPP_v10.csv",
    ARCH / "LA-ICPMS_TAPP_v11.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v1.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v2.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v3.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v4.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v4.1.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v5.csv",
]

TARGETS = [
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_TAPP_v5.csv",
    ROOT / "LA-Q_SF-ICP-MS" / "LA-Q_SF-ICPMS_UPb_TAPP_v5.csv",
]

EPMA = ROOT / "EPMA" / "EPMA_TAPP_v9.csv"


def is_group_header(name):
    return name and name[0].isdigit() and "." in name[:3]


def read(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    return rows[0], rows[1:]


def signatures(path):
    """field name -> (description, C tier, D tier, data type)"""
    hdr, body = read(path)
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
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def build_last_change_map():
    """field -> date of last substantive content change across the lineage."""
    last = {}
    prev = {}
    for p in LINEAGE:
        d = version_date(p)
        sig = signatures(p)
        for name, s in sig.items():
            if name not in prev or prev[name] != s:
                last[name] = d
        prev = sig
    return last


def fix_epma():
    hdr, body = read(EPMA)
    H = hdr.index("Last Update")
    n = 0
    for r in body:
        if len(r) > H and r[H].strip() == "5/11/26":
            r[H] = "2026-05-11"
            n += 1
    if APPLY and n:
        with open(EPMA, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows([hdr] + body)
    return n


def fix_missing(path, lastmap):
    hdr, body = read(path)
    H = hdr.index("Last Update")
    filled, unknown = [], []
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
            filled.append((name, d))
        else:
            unknown.append(name)
    if APPLY and filled:
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows([hdr] + body)
    return filled, unknown


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — date cleanup 2026-08-10\n")

    print("(A) EPMA date-format")
    print(f"    5/11/26 -> 2026-05-11 on {fix_epma()} rows\n")

    lastmap = build_last_change_map()
    print(f"(B) date-missing — computed last-substantive-change for "
          f"{len(lastmap)} fields across {len(LINEAGE)} lineage versions\n")

    import collections
    for t in TARGETS:
        filled, unknown = fix_missing(t, lastmap)
        print(f"  {t.name}: filled {len(filled)}, unresolved {len(unknown)}")
        dist = collections.Counter(d for _, d in filled)
        for d, c in sorted(dist.items()):
            print(f"      {d}  x{c}")
        if unknown:
            print(f"      UNRESOLVED (no lineage record): {unknown}")
        print()

    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
