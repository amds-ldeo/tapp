#!/usr/bin/env python3
"""
Reconcile `Mass Cycles per Replicate` (Solution Q) with `Number of Scans per Replicate` (Solution SF).

The simplest of the reconciliations: identical C=Basic, D=Read-Only, E=Integer, Keyed By (none), and
descriptions that differ by one parenthesis —
  Q   "Number of complete mass scans (sweeps) accumulated per analytical replicate."
  SF  "Number of complete mass scans accumulated per analytical replicate."
The extractions are the same shape on both sides: "250 sweeps per replicate", "48 scans per 30 s
acquisition", "2000 sweeps per set x 30 sets", "LR: 15 passes x 3 runs".

NAME `Number of Scans per Replicate` survives, for two reasons beyond the coin-toss of one TAPP each:

  1. **"Cycles" means something else in this library, and the difference is physical.**
     `Number of Cycles per Block` (LA-MC, LA-MC_UPb, Solution MC) defines a cycle as "a single set of
     SIMULTANEOUS Faraday cup readings". A scan is a SEQUENTIAL traversal of the monitored masses by a
     scanning analyser. Simultaneous multi-collection and sequential scanning are different
     acquisition physics, so reserving "cycle" for the first and "scan" for the second keeps a real
     distinction rather than an accidental one. Naming the merged field "Mass Cycles" would have
     collided with it.
  2. It matches the library's established "Number of X per Y" form — `Number of Blocks per
     Measurement`, `Number of Cycles per Block`, `Number of Replicates`, `Number of Digestion Steps`.

NO CROSS-REFERENCE between this field and `Number of Cycles per Block`: their footprints are
DISJOINT (Solution Q/SF against the three MC TAPPs), so naming either in the other's description
would point every reader at a field they do not have. Following the rule recorded earlier today, the
boundary is stated generically instead — "distinct from a cycle in simultaneous multi-collection".

NOT extended to the LA TAPPs. They have no scans-per-replicate field and no paper in the LA corpus
states one; laser ablation acquires a continuous transient, where the equivalent information is
carried by `Ablation Duration per Spot` and `Total Integration Time per Output Data Point`. Rule 6.10:
do not provision without instances.
"""
import csv, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
DATE = "2026-08-17"
OLD, NEW = "Mass Cycles per Replicate", "Number of Scans per Replicate"

NEW_B = ("Number of complete mass scans accumulated per analytical replicate. A scan — also called a "
         "sweep or a pass — is one complete traversal of the monitored masses by a sequentially "
         "scanning analyser, so the scan count multiplied by the per-mass dwell time gives the total "
         "integration time per replicate. Distinct from a cycle in simultaneous multi-collection, "
         "which is one readout of all detectors at once rather than a traversal of masses.")
NEW_F = "20 | 40 | 100 | 250 | 2000"

JOBS = [
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v33.csv",  "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v34.csv"),
 ("Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v31.csv","Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v32.csv"),
]

for src, dst in JOBS:
    rows = list(csv.reader(open(os.path.join(ROOT, src), encoding='utf-8-sig')))
    hit = [r for r in rows[1:] if r and r[0] in (OLD, NEW)]
    assert len(hit) == 1, f"{src}: {len(hit)} rows"
    r = hit[0]
    was = r[0]
    assert (r[2], r[3], r[4], r[8]) == ("Basic", "Read-Only", "Integer", "(none)"), \
        f"{src}: unexpected {(r[2], r[3], r[4], r[8])}"
    r[0], r[1], r[5], r[7] = NEW, NEW_B, NEW_F, DATE
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} '{was}' -> '{NEW}'")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
