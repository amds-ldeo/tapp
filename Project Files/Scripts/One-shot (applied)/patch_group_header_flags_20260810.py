#!/usr/bin/env python3
"""
Group-header mode-flag and sentinel cells: empty -> N.

conventions.md, "Section header mode flags":
    Group header rows must have N in all mode flag columns to prevent them from
    appearing in mode-filtered views.

The sentinel column follows the same rule for headers. Note the asymmetry, which
is why this patch touches header rows ONLY: in the sentinel column, group headers
must be N but DATA rows must be empty. Writing N onto data rows is a separate
existing finding (`sentinel-stray-N`, 4 occurrences in the SEM family) and must
not be made worse here.

Cosmetic by the linter's own assessment — an empty flag is not Y, so headers
already stay out of mode-filtered views. This aligns the files with the stated
convention so the checks stop firing.

SKIPPED: LA-MC-ICPMS_TAPP_v2.csv and LA-MC-ICPMS_UPb_TAPP_v1.csv (40 findings).
A separate session has been rewriting those files and may still be active.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
SENTINEL = "Literature Assessment"

# Originally skipped the two LA-MC-ICP-MS files while a separate session was
# rewriting them. That work has landed (v2, 2026-08-10 13:21) and the folder has
# been stable since, so the skip list is now empty and this script was re-run to
# cover them. Idempotent: it only ever fills cells that are empty.
SKIP: set = set()


def is_group_header(name):
    return bool(name) and name[0].isdigit() and "." in name[:3]


CHECKS = {"mode-flag-group-header", "sentinel-group-header"}


def find_targets():
    """Exactly the live files that actually carry these two findings.

    Derived from a fresh lint report rather than a glob: a glob picks up
    `.migration_backup_*`, the archived branch, and every historical vN in each
    folder — 44 files instead of the 12 that need touching.
    """
    import subprocess
    import tempfile
    rep = Path(tempfile.mkdtemp()) / "lint.csv"
    subprocess.run(
        [sys.executable,
         str(ROOT / "Claude Skills for TAPP" / "scripts" / "validate_tapp.py"),
         "--csv", str(rep)],
        capture_output=True, text=True, cwd=str(ROOT))
    names = set()
    with open(rep, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["Check"] in CHECKS:
                names.add(row["TAPP"])
    names -= SKIP

    paths = []
    for p in ROOT.rglob("*.csv"):
        rel = str(p.relative_to(ROOT)).lower()
        if rel.startswith(".") or "superseded" in rel or "archive" in rel:
            continue
        if p.name in names:
            paths.append(p)
    return sorted(set(paths))


def process(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    hdr = rows[0]
    if SENTINEL not in hdr:
        return None
    sent = hdr.index(SENTINEL)
    try:
        H = hdr.index("Last Update")
    except ValueError:
        return None
    # mode flag columns sit between Last Update and the sentinel
    mode_cols = list(range(H + 1, sent))
    cols = mode_cols + [sent]

    changed = 0
    headers_seen = 0
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        if not is_group_header(r[0].strip()):
            continue
        headers_seen += 1
        while len(r) <= sent:
            r.append("")
        for c in cols:
            if not r[c].strip():
                r[c] = "N"
                changed += 1

    if APPLY and changed:
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
    return headers_seen, len(mode_cols), changed


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — group-header flag cells empty -> N\n")
    total = 0
    for p in find_targets():
        res = process(p)
        if not res:
            continue
        headers, nmodes, changed = res
        if changed:
            print(f"  {p.relative_to(ROOT)}")
            print(f"      headers={headers}  mode cols={nmodes}  cells set={changed}")
            total += changed
    print(f"\ntotal cells set: {total}")
    print(f"skipped (other session active): {sorted(SKIP)}")
    if not APPLY:
        print("\n(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
