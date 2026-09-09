#!/usr/bin/env python3
"""
harmonise_analytical_mode_colf_20260909.py
-------------------------------------------
Rule 3 conformance for `Analytical Mode` Column F, library-wide.

WHAT WAS WRONG, AND WHAT WAS NOT.
The trigger was a report that Column F wrapped every value in literal single quotes
in EPMA and LA-MC-ICP-MS, unlike other controlled lists. That framing was wrong and
is corrected here, because the correction is the reason for the change:

  Of the 16 TAPPs, 13 quote their Analytical Mode values and 3 do not. The split is
  not arbitrary — it is EXACT. All 13 quoted TAPPs list at least one composite
  `A; B` member; all 3 unquoted TAPPs (the Solution family) list none. The quoting
  was a deliberate device to bracket the composite entries so the `;` inside them
  would not read as a second separator.

The real non-conformance is the composite entries themselves. Rule 3:

    Allowed values: exactly the mode flag column labels defined in Phase 0 for that
    TAPP ... For multi-mode procedures: list all applicable modes separated by
    semicolons

Semicolon-joining is the COMBINING RULE, not a vocabulary member. Listing
`'Spot; Transect'` promotes a rule into a fifth member of a closed list. Once the
composites go, the quoting has nothing left to bracket and goes with them.

Nothing is lost: a multi-mode procedure still records `Spot; Transect` in the cell,
by the documented rule, exactly as before.

VERIFIED BEFORE WRITING — atomic members vs the TAPP's own mode flag headers:
  12 of 16 match the mode flag column labels exactly, as a set and in order.
  EPMA_v63 matches as a SET but not in order (flags run EDS Point, EDS Mapping, WDS
    Point, WDS Mapping; Column F runs WDS Point, EDS Point, WDS Mapping, EDS Mapping).
    Order is NOT changed here — it is set-identical, cosmetic, and was not part of
    the approved change. Reported instead.
  The 3 Solution TAPPs have ZERO mode flag columns, so Rule 3's vocabulary clause has
    no labels to bind them to; they fall under its single-mode clause. They carry no
    quotes and no composites, so they are UNTOUCHED.

SCOPE: 13 TAPPs, one cell each. Column F is consumer-owned on Module_Core
(`consumer_columns: ['F','G','H']`), so this is a TAPP-level edit with no module
change and no recomposition — the same route harmonise_beam_mode_colf_20260830.py took.

Column H IS stamped, unlike the literature re-extraction on 2026-09-09: changing which
values a controlled list admits is a substantive edit to the field.

New CSVs are written utf-8-sig. Every library CSV carries a BOM except
LA-MC-ICPMS_TAPP_v71.csv, written without one earlier today by
patch_lamcicpms_zhang2022_reextract_20260909.py; superseding it here restores the norm.
"""

import csv, json, os, re, shutil, subprocess, sys

ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEM  = "Analytical Mode"
STAMP = "2026-09-09"
SKIP  = {"Solution_MC-ICP-MS", "Solution_Q-ICP-MS", "Solution_SF-ICP-MS"}
XLSX  = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")


def newF(raw):
    """Strip the bracketing quotes and drop composite members. Order preserved."""
    parts = [p.strip() for p in raw.split("|")]
    out = []
    for p in parts:
        if len(p) > 1 and p[0] == p[-1] == "'":
            p = p[1:-1].strip()
        if ";" in p:            # a combining-rule expression, not a member
            continue
        out.append(p)
    return " | ".join(out)


def main(apply=False):
    reg  = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        rel  = e["tapp"]
        base = re.match(r"(.+)_v(\d+)\.csv$", os.path.basename(rel))
        stem, ver = base.group(1), int(base.group(2))
        if stem.replace("_TAPP", "") in SKIP:
            continue
        src  = os.path.join(ROOT, rel)
        rows = list(csv.reader(open(src, newline="", encoding="utf-8-sig")))
        hdr  = rows[0]
        iF, iU = hdr.index("Example / Allowed Content"), hdr.index("Last Update")
        s = hdr.index("Literature Assessment")
        flags = [c.strip() for c in hdr[10:s]]

        row = next((r for r in rows[1:] if r and r[0].strip() == ITEM), None)
        if row is None:
            print("  ABORT: %s has no %s row" % (stem, ITEM)); return 1
        cur = row[iF].strip()
        nxt = newF(cur)
        if cur == nxt:
            print("  skip %-28s already conformant" % stem); continue

        atomic = nxt.split(" | ")
        if sorted(atomic) != sorted(flags):
            print("  ABORT: %s atomic members do not match its mode flags\n"
                  "     flags : %s\n     atomic: %s" % (stem, flags, atomic)); return 1
        if sorted(atomic) != sorted(x.strip().strip("'") for x in cur.split("|")
                                    if ";" not in x):
            print("  ABORT: %s member set changed unexpectedly" % stem); return 1

        newrel = rel.replace("_v%d.csv" % ver, "_v%d.csv" % (ver + 1))
        plan.append((e, rel, newrel, rows, row, iF, iU, cur, nxt, stem, ver))
        print("  %-28s v%d -> v%d" % (stem, ver, ver + 1))
        print("      was: %s" % cur)
        print("      now: %s" % nxt)

    print("\n  %d TAPP(s) to change; %d skipped as already conformant (Solution family)"
          % (len(plan), len(SKIP)))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", STAMP)
    os.makedirs(sup, exist_ok=True)
    for e, rel, newrel, rows, row, iF, iU, cur, nxt, stem, ver in plan:
        while len(row) <= iU: row.append("")
        row[iF], row[iU] = nxt, STAMP
        dst = os.path.join(ROOT, newrel)
        with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        p = subprocess.run([sys.executable, XLSX, newrel], cwd=ROOT,
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("xlsx failed for %s\n%s" % (newrel, p.stderr[-600:]))
        e["tapp"] = newrel
        print("  wrote %s" % os.path.basename(newrel))

    reg["generated"] = STAMP
    with open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced" % len(plan))

    s = os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py")
    p = subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print(p.stdout.strip()[-300:])
    return 0


sys.exit(main("--apply" in sys.argv))
