#!/usr/bin/env python3
"""Which module, if any, owns a field — and which of its columns (Rule 6).

    python3 "Project Files/Scripts/check_field_ownership.py" "Beam Mode" "Torch Type"

WHY THIS EXISTS AS A SCRIPT. The one-liner it replaces caused a Rule 6 violation on
2026-08-30 and again on 2026-08-31:

    for j in glob.glob('Claude Skills for TAPP/modules/*.json'):
        ...
        if field in fields: print('MODULE', ...); break
    else: print('TAPP-owned')

Run from a subdirectory the RELATIVE glob matches nothing, the loop body never executes, and
control falls to `else` — printing a confident "TAPP-owned" that means only "I looked in the
wrong place". `Primary Calibration Standard Name` was edited directly in 12 TAPPs on that
answer; it is owned by Module_CompositionQC.

So: the module directory is resolved from THIS FILE's location, never the working directory,
and finding no modules is a hard error rather than a silent negative.
"""
import json, sys
from pathlib import Path

MD = Path(__file__).resolve().parents[2] / "Claude Skills for TAPP" / "modules"

def main(fields):
    mods = sorted(MD.glob("*.json"))
    if not mods:
        print(f"ERROR: no module manifests under {MD}", file=sys.stderr)
        return 2
    owners = {}
    for j in mods:
        d = json.loads(j.read_text())
        fl = set()
        for b in d.get("blocks", []):
            fl.update(b.get("fields", []))
        for f in fl:
            owners[f] = (j.stem.replace("Module_", ""), sorted(d.get("owned_columns", [])),
                         sorted(d.get("overlay_columns", []) or []))
    rc = 0
    for f in fields:
        if f in owners:
            mod, owned, overlay = owners[f]
            print(f"  {f}\n      MODULE {mod} — owns {owned}, overlay {overlay}")
            print(f"      -> edit the module CSV, bump its JSON version, recompose consumers.")
            rc = 1
        else:
            print(f"  {f}\n      TAPP-owned (checked {len(mods)} modules) — edit the TAPP CSVs directly.")
    return rc

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
