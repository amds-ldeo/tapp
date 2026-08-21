#!/usr/bin/env python3
"""
Harmonise the `Collision/Reaction Cell (CRC) Configuration` allowed values, and migrate the
Solution Q extractions that used `None` to mean "no cell gas".

Three different vocabularies were in circulation across the 6 TAPPs holding the field:

  LA-Q, LA-Q_UPb, LA-MC, LA-MC_UPb  STD | KED | DRC | ICP-MS/MS | N/A | None | Other
                                    -> has ICP-MS/MS, but no `Not installed`
  Solution MC                       Not installed | STD | KED | DRC | N/A | None | Other
  Solution Q                        None (STD mode) | KED (He) | DRC (NH3) | KED+DRC |
                                    Not installed | N/A | Other
                                    -> no ICP-MS/MS, and `None` overloaded to mean "no gas"

Two defects, both consequential for the 2026-08-14 decision that a triple-quadrupole instrument
registers under the Q-ICP-MS TAPP:

1. **Solution Q could not record tandem operation at all** — it had no `ICP-MS/MS` value. That is
   the field the decision relies on to carry the distinction between an 8900 run as a single quad
   and one run in MS/MS mode.
2. **Solution Q overloaded `None`.** Conventions require every Controlled list to offer `None`
   meaning "no such thing"; Solution Q used `None (STD mode)` to mean "cell present, no gas". Its
   own extractions show the confusion: three cells read `None (STD mode; ...)` for procedures whose
   instruments demonstrably have a cell — Lu et al. 2007 states "Our instrument has a collision cell
   with octapoles, but collision gases were not introduced into the cell", which is STD, not None.

Resolution — two lists, split on analyser family rather than forced identical, since Column F is
consumer-owned and legitimately technique-specific (Rule 6.4):

  Q family   Not installed | STD | KED | DRC | KED+DRC | ICP-MS/MS | N/A | None | Other: specify
  MC family  Not installed | STD | KED | DRC | N/A | None | Other: specify

`ICP-MS/MS (triple-quadrupole mode)` is REMOVED from the two LA-MC TAPPs: a multi-collector has no
second quadrupole, so the value invited an answer that cannot be true. `Not installed` is ADDED to
the four LA TAPPs, which lacked it — that is the value distinguishing "no cell hardware" from "cell
present, no gas", and it is what makes an `N` in a literature column mean "not reported" rather than
being confused with either.

Column B is deliberately untouched: it already carries 4 registered variants across the 6 TAPPs, and
editing it would create new Rule 7.8.9 divergence for no gain.
"""
import csv, os, re, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
APPLY = "--apply" in sys.argv
FIELD = "Collision/Reaction Cell (CRC) Configuration"
DATE = "2026-08-14"

Q_LIST = ("Not installed | STD (standard mode, no gas) | KED (kinetic energy discrimination, He gas) | "
          "DRC (dynamic reaction cell, reactive gas) | KED+DRC | ICP-MS/MS (triple-quadrupole mode) | "
          "N/A | None | Other: specify")
MC_LIST = ("Not installed | STD (standard mode, no gas) | KED (kinetic energy discrimination, He gas) | "
           "DRC (dynamic reaction cell, reactive gas) | N/A | None | Other: specify")

JOBS = [
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v20.csv",             "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v21.csv",             Q_LIST),
 ("LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v21.csv",         "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v22.csv",         Q_LIST),
 ("Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v24.csv", "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v25.csv", Q_LIST),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v18.csv",            "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v19.csv",            MC_LIST),
 ("LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v18.csv",        "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v19.csv",        MC_LIST),
]

# Solution Q extraction cells that used `None` for "cell present, no gas".
MIGRATE = re.compile(r'^None \(STD mode([;)])')

for src, dst, lst in JOBS:
    p = os.path.join(ROOT, src)
    if not os.path.exists(p):
        print(f"SKIP (not found) {src}")
        continue
    rows = list(csv.reader(open(p, encoding='utf-8-sig')))
    hdr = rows[0]
    si = hdr.index('Literature Assessment') if 'Literature Assessment' in hdr else len(hdr)
    changed_f = migrated = 0
    for r in rows[1:]:
        if not r or r[0] != FIELD:
            continue
        if r[5] != lst:
            r[5] = lst
            r[7] = DATE
            changed_f += 1
        for k in range(si + 1, len(r)):
            if MIGRATE.match(r[k] or ''):
                r[k] = MIGRATE.sub(r'STD (standard mode, no gas\1', r[k])
                migrated += 1
    print(f"{'WROTE' if APPLY else 'DRY '} {os.path.basename(dst):36} "
          f"Column F {'rewritten' if changed_f else 'unchanged'}, {migrated} extraction cells migrated")
    if APPLY:
        with open(os.path.join(ROOT, dst), "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

if not APPLY:
    print("\ndry run — rerun with --apply")
