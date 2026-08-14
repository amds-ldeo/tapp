#!/usr/bin/env python3
"""
Split `Uncertainty Level and Propagation` into two fields, across 7 TAPPs.

    Uncertainty Level            C=Basic     D=Read-Only   (NEW)
    Uncertainty Propagation Method  C=Advanced  D=Editable  (renamed back)

WHY THIS DOES NOT REVERSE THE PRECEDENT.

`precedents.md` carries "Uncertainty Propagation Method — Advanced/Editable
rather than Basic/Read-Only". Its reasoning is entirely about the PROPAGATION
framework: "many labs use informal uncertainty estimates without a formally
specified propagation framework", so mandating one at Basic would exclude
legitimate procedures or generate boilerplate.

That reasoning is sound and is preserved untouched on the propagation half.

It never covered the LEVEL, because when the precedent was written the field was
named `Uncertainty Propagation Method` — propagation only. The level component
was merged in by the 2026-08-08 rename to `Uncertainty Level and Propagation`,
which introduced a concept the precedent had never considered and inherited its
Advanced tier by accident rather than by argument. The split restores the
precedent's scope rather than overturning it, and the propagation half takes its
original name back so the precedent applies to it by name again.

WHY THE LEVEL IS BASIC.
`analysis/Test5_Geochronology_Module_CrossSystem.csv` row 3 records "Uncertainty
Level Convention" as REQUIRED in 6 of 6 independent community dating standards,
with recommended tiers C=Basic / D=Read-Only, and its status as "PARTIAL -
folded into geochron Uncertainty Level and Propagation". Unlike a propagation
framework, every lab that reports an uncertainty has a level convention — there
is no "informal" case to exclude. D=Read-Only is correct here and does not hit
the precedent's void-import trap, which applies only when C=Advanced: a C=Basic
field always carries a procedure value for the analysis to inherit.

The old description's own closing sentence — "A reported uncertainty is not
interpretable without BOTH HALVES" — states that this was two fields.

PLACEMENT. `Uncertainty Level` is inserted immediately BEFORE the propagation
field, which sits well inside Group 5 in all 7 TAPPs, so Rule 5's requirement
that `Constants and Reference Values Used` remain last in Group 5 is unaffected.

LITERATURE ASSESSMENT CELLS on the new row are left EMPTY. The existing
extractions sit on the propagation row where they were made. Several visibly
contain level information ("2SE of individual spot measurements reported"), so a
Phase 3 re-pass could populate the new row — but copying them wholesale would
fabricate extraction that was never performed against this field.

VERSION BUMP. Adding a field is a major structural revision under Version and
Date Tracking, so all 7 TAPPs take an integer bump. Old versions stay in place.

Run with --apply; default is a dry run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
TODAY = "2026-08-10"
OLD_NAME = "Uncertainty Level and Propagation"
NEW_LEVEL = "Uncertainty Level"
NEW_PROP = "Uncertainty Propagation Method"

LEVEL_DESC = (
    "The convention at which reported uncertainties are quoted — 1-sigma, 2-sigma, or a 95% "
    "confidence interval — and whether a measured spread is reported as a standard error or a "
    "standard deviation. A reported uncertainty is not interpretable without it: the same numeric "
    "value means different things at 1-sigma and at 95% confidence. State the convention applying "
    "to all values reported under this procedure, and state each separately where different "
    "reported quantities use different conventions. Distinct from Uncertainty Propagation Method, "
    "which addresses how component uncertainties are combined rather than how the result is quoted."
)
LEVEL_TYPE = "Controlled list / Text"
# Compound: conventions require N/A | None but NOT "Other: specify",
# because the "/ Text" component already permits an unlisted answer.
LEVEL_EXAMPLE = (
    "2σ (95% confidence) | 1σ (68% confidence) | 95% confidence interval | "
    "2 standard errors (2SE) | 1 standard deviation (1SD) | N/A | None"
)

PROP_DESC = (
    "The approach used to propagate analytical uncertainty through the data reduction chain to the "
    "final reported value. State which sources are included in the propagation: counting "
    "statistics, calibration standard uncertainty, internal standard uncertainty, drift correction, "
    "and any systematic contributions. Distinct from Uncertainty Level, which states the convention "
    "at which the resulting uncertainty is quoted."
)

# current path -> new path (integer bump; old files remain)
BUMPS = {
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv": "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v6.csv",
    "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_UPb_TAPP_v5.csv": "LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_UPb_TAPP_v6.csv",
    "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v2.csv": "LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v3.csv",
    "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v1.csv": "LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v2.csv",
    "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v7.csv": "Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v8.csv",
    "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v7.csv": "Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v8.csv",
    "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v5.csv": "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v6.csv",
}

COL_ITEM, COL_DESC, COL_C, COL_D, COL_TYPE, COL_EXAMPLE, COL_COMMENT, COL_UPDATE = range(8)
SENTINEL = "Literature Assessment"


def main():
    print(f"{'APPLY' if APPLY else 'DRY RUN'} — split Uncertainty Level / Propagation\n")
    for src_rel, dst_rel in BUMPS.items():
        src, dst = ROOT / src_rel, ROOT / dst_rel
        rows = list(csv.reader(open(src, encoding="utf-8-sig")))
        hdr = rows[0]
        width = len(hdr)
        sent = hdr.index(SENTINEL) if SENTINEL in hdr else None

        out, done = [hdr], False
        for r in rows[1:]:
            if r and r[COL_ITEM].strip() == OLD_NAME:
                # new level row, structurally cloned so mode flags line up
                lvl = [""] * width
                lvl[COL_ITEM] = NEW_LEVEL
                lvl[COL_DESC] = LEVEL_DESC
                lvl[COL_C], lvl[COL_D] = "Basic", "Read-Only"
                lvl[COL_TYPE] = LEVEL_TYPE
                lvl[COL_EXAMPLE] = LEVEL_EXAMPLE
                lvl[COL_UPDATE] = TODAY
                if sent is not None:
                    for c in range(COL_UPDATE + 1, sent):      # mode flags
                        lvl[c] = r[c] if len(r) > c else ""
                    lvl[sent] = ""                              # sentinel stays empty
                    # literature assessment cells deliberately left empty
                out.append(lvl)

                # renamed propagation row, tiers untouched
                pr = list(r) + [""] * (width - len(r))
                pr[COL_ITEM] = NEW_PROP
                pr[COL_DESC] = PROP_DESC
                pr[COL_UPDATE] = TODAY
                out.append(pr)
                done = True
            else:
                out.append(r)

        status = "OK" if done else "*** FIELD NOT FOUND ***"
        print(f"  {src.name}  ->  {dst.name}   [{status}]")
        print(f"      rows {len(rows)} -> {len(out)}   width {width}")
        if APPLY and done:
            with open(dst, "w", newline="", encoding="utf-8-sig") as fh:
                csv.writer(fh).writerows(out)
            print(f"      written")
    print()
    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")


if __name__ == "__main__":
    main()
