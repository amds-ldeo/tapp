#!/usr/bin/env python3
"""
build_la_mc_icpms_20260808.py

Builds LA-MC-ICP-MS by the composition route (workflow.md, "Choosing a Route").

Base
----
LA-Q/SF-ICP-MS v5, which already carries Group1 + LaserAblation + ReportingCore plus the
generic ICP-MS content. Starting from Solution MC-ICP-MS instead would mean stripping the
whole solution-introduction chain (digestion, desolvation, chromatography, nebuliser) and
adding the laser front end back; starting here means swapping one analyser for another.

Steps
-----
1. strip LA-Q/SF's literature assessment columns — those are its Phase 3 papers, not this
   TAPP's; the sentinel column is kept so the structure stays valid
2. remove the fields specific to a SEQUENTIAL analyser (see below)
3. compose Module_MCICPMS, which supplies the multi-collector analyser
4. reset the Column F values that are technique-specific declarations

Sequential-analyser fields removed
----------------------------------
    E-scan Range                                  electrostatic scanning, single-collector SF
    Triple Scanning Mode                          SF acquisition strategy
    Signal Collection Mode                        peak hopping vs scanning; the MC equivalent
                                                  is static/dynamic, held in Collector Configuration
    Dwell Time per Mass                           sequential; MC uses Integration Time per Cycle
    Total Integration Time per Output Data Point  its own description says "applies to
                                                  sequential (Q/SF) acquisition"
    Pulse/Analog Detector Nonlinearity Correction P/A cross-calibration; the MC equivalent is
                                                  Faraday Cup Gain Calibration Method

Deliberately RETAINED
---------------------
    Mass Resolution Setting / Mass Resolution per Analyte — modern MC instruments (Neptune,
        Nu Plasma 3D) have entrance slits for pseudo-high resolution
    Collision/reaction cell fields — present on Nu Sapphire and Neoma MS/MS
    Ion Counter Dead Time — MC instruments carry ion counters alongside Faradays

Residue — NOT established, and NOT written by this script
---------------------------------------------------------
The coverage audit above is empirical. What LA-MC-ICP-MS needs BEYOND its composed modules is
not: no source in this project addresses it. The planning table note for #7a attributes this
technique's distinctiveness to Faraday cup configuration, mass bias correction and isotope-ratio
workflows — all of which Module_MCICPMS already supplies — so the residue may be small or empty.

One plausible gap, reasoned from the field descriptions rather than from any source: Solution
MC-ICP-MS's Baseline Measurement Approach describes on-peak-zero by beam deflection or by
aspirating an acid blank, and an acid blank cannot be aspirated during laser ablation. Whether
that and related transient-signal issues warrant fields is a Phase 0/Phase 3 question, not a
composition question. Seed paper identified in the planning table: Zhang 2022 (in situ Rb-Sr),
not yet read.

This script produces a starting point, not a finished profile.
"""

from __future__ import annotations

import csv
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "LA-Q_SF-ICP-MS", "LA-Q_SF-ICPMS_TAPP_v5.csv")
OUTDIR = os.path.join(ROOT, "LA-MC-ICP-MS")
OUT = os.path.join(OUTDIR, "LA-MC-ICPMS_TAPP_v1.csv")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
TODAY = datetime.date.today().isoformat()
SENTINEL = "Literature Assessment"

DROP = [
    "E-scan Range",
    "Triple Scanning Mode",
    "Signal Collection Mode",
    "Dwell Time per Mass",
    "Total Integration Time per Output Data Point",
    "Pulse/Analog Detector Nonlinearity Correction",
]

# Column F declarations that must not be inherited verbatim from the Q/SF parent.
RESET_F = {
    "Technique": "LA-MC-ICP-MS | Other: specify | N/A | None",
    "ICP-MS Type": "Multi-collector (MC-ICP-MS) | Multi-collector with collision/reaction cell "
                   "(e.g. Nu Sapphire, Thermo Neoma MS/MS) | Other: specify | N/A | None",
    "Analytical Mode": "'Spot' | 'Transect' | 'Mapping' | 'Spot; Transect' | 'Spot; Mapping'",
}


def main():
    dry = "--dry-run" in sys.argv
    with open(SRC, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    sent = next(i for i, h in enumerate(rows[0]) if h.strip() == SENTINEL)
    lit_dropped = len(rows[0]) - sent - 1
    rows = [r[:sent + 1] for r in rows]

    before = len(rows)
    kept, removed = [], []
    for r in rows:
        if r and r[0].strip() in DROP:
            removed.append(r[0].strip())
            continue
        kept.append(r)
    rows = kept

    reset = []
    for r in rows[1:]:
        name = r[0].strip() if r else ""
        if name in RESET_F and r[5] != RESET_F[name]:
            reset.append((name, r[5][:44], RESET_F[name][:44]))
            r[5] = RESET_F[name]
            r[7] = TODAY

    print(f"base   : {os.path.relpath(SRC, ROOT)}  ({before} rows)")
    print(f"  dropped {lit_dropped} literature assessment column(s) — LA-Q/SF's Phase 3 papers")
    print(f"  removed {len(removed)} sequential-analyser field(s):")
    for x in removed:
        print(f"      - {x}")
    missing = [d for d in DROP if d not in removed]
    if missing:
        print(f"  !! not found (check the base): {missing}")
        return 2
    print(f"  reset {len(reset)} technique declaration(s) in Column F:")
    for n, o, x in reset:
        print(f"      {n}: {o!r} -> {x!r}")

    if dry:
        print("\nDry run — nothing written.")
        return 0

    os.makedirs(OUTDIR, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}  ({len(rows)} rows)")

    r = subprocess.run([sys.executable, COMPOSE, "--source", OUT,
                        "--module", "MCICPMS", "--out", OUT],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
