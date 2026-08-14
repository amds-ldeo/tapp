#!/usr/bin/env python3
"""Rule 12 — refresh `Current TAPPs/`, the shareable flat mirror of the latest TAPPs.

The mirror holds the latest CSV **and** xlsx for every TAPP, flat, with no versions but the current
one. It exists so the whole folder can be handed to another developer as a unit. That is also why a
stale mirror is worse than no mirror: a recipient has no way to tell that what they were given is out
of date. `validate_tapp.py` therefore reports any drift at WARN (`rule12-*`).

Run after any change that creates a TAPP or bumps a version. `bump_and_stamp_20260812.py` calls it
automatically; run it by hand after anything that bumps versions some other way.

  (default)  report what would change
  --apply    write

The mirror is a COPY, never an editing target. It is excluded from `discover()` by name
(`CURRENT_DIR` in validate_tapp.py) — without that exclusion a copy accidentally bumped inside the
mirror would out-rank the real file and become what the linter validates, while `compose_tapp.py`
went on using the technique-folder path from composed_tapps.json.
"""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

MIRROR = os.path.join(ROOT, V.CURRENT_DIR)
TAPP_FILE_RE = re.compile(r"_TAPP_v\d+(\.\d+)?\.(csv|xlsx)$")

README = """# Current TAPPs

**This folder is a generated mirror. Do not edit anything in it.**

It holds the **latest version of every TAPP** in the library — the CSV (source of truth) and the
xlsx (colour-coded, with a Legends sheet explaining the tier vocabulary and the `Keyed By` keys).
Flat, one version each, refreshed on every version bump under Rule 12.

Share this whole folder with anyone who needs the current TAPPs. It is self-contained and carries no
superseded versions, so there is nothing to sift.

| | |
|---|---|
| TAPPs | {n} |
| Files | {files} ({n} CSV + {nx} xlsx) |
| As of | {date} |

## Where to look for more

| For | Go to |
|---|---|
| Earlier versions of a TAPP | the technique folder in the library root (`EPMA/`, `SEM/`, …) — it keeps every version |
| The specification behind the columns | `Claude Skills for TAPP/references/conventions.md` |
| Why a specific field is the way it is | `Claude Skills for TAPP/references/precedents.md` |
| Which modules a TAPP is composed from | `composed_tapps.json` at the library root |

## Reading a TAPP

Columns A–I are: Metadata Item · Description · Procedure-Level Tier · Analysis-Level Tier · Data Type
· Example / Allowed Content · Comments · Last Update · **Keyed By**. After those come one column per
analytical mode, a sentinel column headed `Literature Assessment`, and then one column per procedure
extracted from the literature.

`Keyed By` states what a field's value repeats over — `(none)` for a scalar, or a key such as
`analyte`, `channel`, `reported property`, `sampling unit`. The xlsx Legends sheet lists the keys used
in that particular TAPP.

## Contents

{listing}
"""


def wanted():
    """{filename: source path} — latest CSV + xlsx for every discovered TAPP."""
    out = {}
    for t in V.discover(ROOT):
        for ext in ("csv", "xlsx"):
            src = t[:-4] + "." + ext
            if os.path.exists(src):
                out[os.path.basename(src)] = src
            elif ext == "csv":
                print(f"  WARN source CSV missing?! {t}")
    return out


def digest(path):
    """Content hash, not file size.

    Size was the original test and it silently missed changes. Confirmed 2026-08-12: a
    regenerated LA-MC-ICPMS_UPb xlsx and its mirror copy were both exactly 42785 bytes with
    different content, so the sync reported 15 files to copy instead of 16 and the stale one
    had to be found by hand. openpyxl output is especially prone to this — rewriting the same
    workbook with a small text change often lands on an identical size. A stale mirror is the
    failure Rule 12.1 calls worse than no mirror, because the recipient cannot tell.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    exp = wanted()
    have = ({f for f in os.listdir(MIRROR)
             if os.path.isfile(os.path.join(MIRROR, f)) and TAPP_FILE_RE.search(f)}
            if os.path.isdir(MIRROR) else set())

    to_copy = [n for n, src in sorted(exp.items())
               if not os.path.exists(os.path.join(MIRROR, n))
               or digest(os.path.join(MIRROR, n)) != digest(src)]
    to_remove = sorted(have - set(exp))

    for n in to_remove:
        # name the version it is being replaced by, where there is one
        stem, ext = n.rsplit("_v", 1)[0], n.rsplit(".", 1)[1]
        repl = [e for e in exp if e.rsplit("_v", 1)[0] == stem and e.endswith("." + ext)]
        why = f"superseded by {repl[0]}" if repl else "no longer a current TAPP"
        print(f"  {'REMOVE' if args.apply else 'would remove':14s} {n:44s} ({why})")
    for n in to_copy:
        print(f"  {'COPY  ' if args.apply else 'would copy  ':14s} {n}")

    n_csv = sum(1 for k in exp if k.endswith(".csv"))
    n_xlsx = sum(1 for k in exp if k.endswith(".xlsx"))
    print(f"\n{len(exp)} file(s) in the mirror when synced "
          f"({n_csv} CSV + {n_xlsx} xlsx for {n_csv} TAPPs)")
    print(f"  {len(to_copy)} to copy, {len(to_remove)} to remove")

    if not args.apply:
        print("(dry run — pass --apply to write)")
        return

    os.makedirs(MIRROR, exist_ok=True)
    for n in to_remove:
        os.remove(os.path.join(MIRROR, n))
    for n in to_copy:
        shutil.copy2(exp[n], os.path.join(MIRROR, n))

    listing = "\n".join(
        f"- `{n}`" for n in sorted(k for k in exp if k.endswith(".csv")))
    open(os.path.join(MIRROR, "README.md"), "w", encoding="utf-8").write(
        README.format(n=n_csv, nx=n_xlsx, files=len(exp),
                      date=datetime.date.today().isoformat(), listing=listing))
    print(f"synced -> {MIRROR}")


if __name__ == "__main__":
    main()
