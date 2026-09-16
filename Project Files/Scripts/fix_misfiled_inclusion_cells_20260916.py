#!/usr/bin/env python3
"""Refile the four `Analysis Inclusion and Rejection Criteria` cells that the amds-ldeo/tapp#4
definition made wrong (LA-MC v83, Solution MC v84, Solution Q v87).

    python3 "Project Files/Scripts/fix_misfiled_inclusion_cells_20260916.py" [--apply]

Module_Aggregation v4 (2026-09-15, commit 3818c79) defined the field's level: an *individual result*
is the value of the reported quantity obtained from one acquisition, and the boundary with signal
filtering is drawn by BASIS — signal-based discards during data reduction belong to
`Spike / Outlier Filtering Approach`, result-based selection belongs here. Four cells were flagged in
the issue reply as misfiled under that definition; this refiles them. Two shapes:

  * WRONG LEVEL, right field family. Zhang 2022 and Pringle & Moynier 2017 record discards made
    *inside* an acquisition (cycles, individual ratios). Both are already recorded verbatim in
    `Spike / Outlier Filtering Approach`, so the content is not lost — it is removed from here and
    the cell keeps only what is genuinely result-level.
  * NOT AGGREGATION AT ALL. Makishima 2011 excludes a MASS from serving a target species; Lopez
    Garcia 2026 excludes two ELEMENTS from the reported results. Neither selects among individual
    results, so each moves to the field that does govern it — `Monitored Masses` and
    `Reported Variables and Units` respectively — and the vacated cell states where it went.

Nothing is deleted without a destination: every moved sentence is written into its new field in the
same run, and the script refuses if a destination has changed since this was written.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"

ZHANG_NEW = (
    "Run level, on the results rather than the signal: runs with stable signals go to the Normal group, runs with "
    "large ⁸⁷Rb/⁸⁶Sr variation to the SUIA group (NWA 10597: 36 Normal, 6 SUIA; NWA 6950: 94 "
    "Normal, 21 SUIA). For NWA 6950 only data with initial ⁸⁷Sr/⁸⁶Sr of 0.7025-0.7035 were kept, "
    "those at 0.7072-0.7076 being from glasses and pyroxenes in or around black veins and interpreted as "
    "later-altered (p.8). The cycle-level discards and the two technical criteria (⁸⁷Rb/⁸⁶Sr > 1; "
    "⁸⁸Sr < 0.2 V) act inside an acquisition and are recorded under Spike / Outlier Filtering Approach")
PRINGLE_NEW = (
    "N — no result-level rule is stated. Reported values are \"averages of repeated measurements of each sample "
    "when multiple analyses were possible\", with no criterion for admitting or rejecting a measurement; the "
    "\"any ratio outside 2σ was discarded\" rule acts within a measurement and is recorded under Spike / Outlier "
    "Filtering Approach")
MAKISHIMA_NEW = (
    "Partially -- n = 5 (evaporation test), n = 4 (dissolution blanks), \"an average of eight sessions\" for "
    "detection limits. No acceptance or rejection rule for individual results is stated. The 113Cd decision is a "
    "mass-selection decision, not an aggregation one, and is recorded under Monitored Masses")
MAKISHIMA_MASSES = (
    "95Mo, 111Cd, 113Cd, 115In, 118Sn, 149Sm, 205Tl, 209Bi (Table 1). Cd is determined on 111Cd only: \"113Cd was "
    "not used for Cd determination, because the correction of 113In was far larger than the MoO correction\"")
LOPEZ_NEW = (
    "N — no rule for admitting or rejecting individual results is stated. The exclusion of Ta and W is a "
    "decision about which elements are reported, not about which results enter an aggregate, and is recorded under "
    "Reported Variables and Units")
LOPEZ_REPORTED = (
    "Elemental abundances, CI-normalised ratios. Ta and W were measured but are not reported: \"Although the "
    "abundances of Ta and W were measured, the data for these elements were excluded from the results due to high "
    "blank contributions (>30%) during the ICP-MS analysis\"")

INCL = "Analysis Inclusion and Rejection Criteria"
# (relative path, column-key prefix, field, expected-current-prefix, new value)
EDITS = [
    ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v82.csv", "Zhang et al. 2022 (At. Spectro", INCL,
     "Cycle level: the cycles at the beginning", ZHANG_NEW),
    ("Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v83.csv", "Pringle+Moynier2017", INCL,
     "\"any ratio outside 2", PRINGLE_NEW),
    ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v86.csv", "Makishima+etal2011", INCL,
     "Partially -- n = 5 (evaporation test)", MAKISHIMA_NEW),
    ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v86.csv", "Makishima+etal2011", "Monitored Masses",
     "95Mo, 111Cd, 113Cd", MAKISHIMA_MASSES),
    ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v86.csv", "LopezGarcia+etal2026", INCL,
     "Explicit rule and outcome:", LOPEZ_NEW),
    ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v86.csv", "LopezGarcia+etal2026", "Reported Variables and Units",
     "Elemental abundances, CI-normalised ratios", LOPEZ_REPORTED),
]


def col(header, key):
    k = " ".join(key.split()).lower()
    hits = [i for i, h in enumerate(header) if " ".join(h.split()).lower().startswith(k)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    by_file = {}
    for rel, key, field, expect, new in EDITS:
        by_file.setdefault(rel, []).append((key, field, expect, new))
    plan = []
    for rel, edits in by_file.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            raise SystemExit("missing %s — has it been bumped since this script was written?" % rel)
        rows = list(csv.reader(io.open(path, newline="", encoding="utf-8-sig")))
        h = rows[0]
        for key, field, expect, new in edits:
            i = col(h, key)
            row = next(r for r in rows if r and r[0].strip() == field)
            cur = row[i].strip()
            if not cur.startswith(expect):
                raise SystemExit("REFUSING: %s / %s / %s starts %r, expected %r"
                                 % (rel, key[:20], field, cur[:60], expect[:40]))
            row[i] = new
            print("  %-34s %-28s %-42s rewritten" % (os.path.basename(rel)[:34], key[:28], field[:42]))
        new_rel = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new_rel, rows))
    print("\n  %d cells in %d TAPPs" % (len(EDITS), len(plan)))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for rel, new_rel, rows in plan:
        with io.open(os.path.join(ROOT, new_rel), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new_rel)], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        next(e for e in reg["composed"] if e["tapp"] == rel)["tapp"] = new_rel
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
