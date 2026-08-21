#!/usr/bin/env python3
"""
Retire the stale LA-ICP-MS branch (LA-ICPMS_TAPP_v1..v13).

The LA-ICP-MS folder and LA-Q_SF-ICP-MS folder are ONE lineage. The branches
synced at v11/v12; only LA-Q/SF received development after that. v13 is v12
plus the mechanical VIM3 pass plus the 2026-08-08 Group 1 composition.

What moves: TAPP artifacts only.
What STAYS: `Validation Papers/` and the loose method PDFs. paper_registry.csv
points 10 papers at `LA-ICP-MS/Validation Papers`, and those papers are the
Phase 3 sources for the LIVE LA-Q/SF-ICP-MS TAPP, which has no papers folder of
its own. Moving them would archive the live TAPP's provenance and break the
registry. The folder is therefore kept, demoted to a source-paper folder.

Run with --apply to execute; default is a dry run.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
SRC = ROOT / "LA-ICP-MS"
DEST = ROOT / "Superseded TAPPs (2026-08-10)" / "LA-ICP-MS (stale branch)"

APPLY = "--apply" in sys.argv

# TAPP artifacts to archive. Papers and Validation Papers/ deliberately excluded.
MOVE_SUFFIXES = (".csv", ".xlsx", ".py")
KEEP_NAMES = set()  # nothing csv/xlsx/py is kept in LA-ICP-MS


def plan_moves():
    moves = []
    for p in sorted(SRC.iterdir()):
        if p.is_dir():
            continue  # Validation Papers/ stays
        if p.name.startswith("."):
            continue
        if p.suffix.lower() == ".pdf":
            continue  # method PDFs stay (referenced by paper_registry.csv)
        if p.suffix.lower() in MOVE_SUFFIXES and p.name not in KEEP_NAMES:
            moves.append(p)
    return moves


def main():
    moves = plan_moves()
    stays = [p for p in sorted(SRC.iterdir())
             if p.is_dir() or p.suffix.lower() == ".pdf"]

    print(f"{'APPLY' if APPLY else 'DRY RUN'} — retire stale LA-ICP-MS branch")
    print(f"\ndest: {DEST}")
    print(f"\nMOVE ({len(moves)}):")
    for p in moves:
        print(f"   {p.name}")
    print(f"\nSTAY in LA-ICP-MS/ ({len(stays)}):")
    for p in stays:
        kind = "dir" if p.is_dir() else "pdf"
        print(f"   [{kind}] {p.name}")

    if not APPLY:
        print("\n(dry run — nothing moved; re-run with --apply)")
        return

    DEST.mkdir(parents=True, exist_ok=True)
    for p in moves:
        shutil.move(str(p), str(DEST / p.name))
    print(f"\nmoved {len(moves)} files")

    # --- composed_tapps.json: v13 moves from composed[] to retired[] ---
    ctp = ROOT / "composed_tapps.json"
    data = json.loads(ctp.read_text(encoding="utf-8"))
    before = len(data["composed"])
    entry = next((c for c in data["composed"]
                  if c["tapp"] == "LA-ICP-MS/LA-ICPMS_TAPP_v13.csv"), None)
    if entry:
        data["composed"] = [c for c in data["composed"]
                            if c["tapp"] != "LA-ICP-MS/LA-ICPMS_TAPP_v13.csv"]
        data.setdefault("retired", []).append({
            "tapp": "LA-ICP-MS/LA-ICPMS_TAPP_v13.csv",
            "retired": "2026-08-10",
            "moved_to": "Superseded TAPPs (2026-08-10)/LA-ICP-MS (stale branch)/",
            "superseded_by": ["LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv"],
            "verification": (
                "All 95 fields checked against LA-Q/SF-ICP-MS v5 (125 fields); 0 uncovered. "
                "Three fields flagged by a name-only diff resolved on reading: "
                "'Auxiliary and Cool Gas Flow Rates' is covered by the two separate fields "
                "'Coolant (Plasma) Gas Flow Rate' + 'Auxiliary Gas Flow Rate'; "
                "'Spectrometer Dwell Time' is a rename of 'Dwell Time per Mass' "
                "(byte-identical description, identical tiers); "
                "'Drift Monitor Frequency' is covered by "
                "'Calibration Standard Measurement Frequency'."
            ),
            "literature_assessment": (
                "v13 carried 16 literature assessment columns (1436 filled cells) against "
                "LA-Q/SF v5's 13. The 3 extra columns (89 filled cells each) are out of scope "
                "for a Q/SF TAPP and are retained in the archived file: "
                "Chernonozhkin et al. 2024 (LA-ICP-ToF-MS) -> planning table row 7b; "
                "Masuda et al. 2024 -> row 7c (LA-ICP-TQ-MS, already names this as its seed paper); "
                "Zhang et al. 2022 At. Spectrosc. 43 (fs-LA-MC-ICP-MS) -> row 7a LA-MC-ICP-MS, "
                "which EXISTS at v1 with zero literature assessment columns. That third column is "
                "directly usable Phase 3 material for LA-MC-ICP-MS and is the reason this "
                "retirement is not a pure archive."
            ),
        })
        ctp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        print(f"composed_tapps.json: composed {before} -> {len(data['composed'])}, "
              f"retired {len(data['retired'])}")
    else:
        print("composed_tapps.json: v13 entry NOT found (already retired?)")


if __name__ == "__main__":
    main()
