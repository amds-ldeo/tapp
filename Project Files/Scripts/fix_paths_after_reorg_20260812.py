#!/usr/bin/env python3
"""Repair path references broken by the 2026-08-12 folder reorganisation.

The move itself verified that scripts still RUN. It did not check that documentation and registers
still POINT at the right places — this does. Sources found by grepping every text file in the tree
for each of the 78 moved basenames (see MOVE_MANIFEST_2026-08-12.csv).

Deliberately NOT touched, because their old paths are correct history:
  Project Files/MOVE_MANIFEST_2026-08-12.csv      records from -> to by design
  Project Files/Design Notes/PLAN_Folder_…md      describes the old -> new mapping
  Project Files/Design Notes/TAPP_Development_Log.md   dated log; gets a forward note only
  Project Files/Design Notes/{DRAFT_Rule7…,RETROFIT-BRIEFING…}.md   historical design docs
  Claude Skills for TAPP/analysis/MC-ICP-MS_Technology_Update_2026-07-29.txt   historical note
  Claude Skills for TAPP/scripts/validate_tapp.py   a history comment, plus `unpacked_tapp`
                                                    in _excluded(), which is still the folder's name

One fix here is NOT caused by the move: `precedents.md` cited
`analysis/Audit_ColI_vs_LitAssess_2026-08-12.csv`, but that file was renamed to
`Audit_ColI_vs_LitAssess.csv` when the audit was promoted into the skill as a standing tool. Stale
since then; corrected now.

Dry-run by default. Pass --apply to write.
"""
import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))

PFS = "Project Files/Scripts"
PFR = "Project Files/Registers & Planning"
PFD = "Project Files/Design Notes"
ONE = "Project Files/Scripts/One-shot (applied)"
ARCW = "Archive/Worksheets (reconciled)"

# (file, old, new)
FIXES = [
    # ---- skill analysis README: relative paths from analysis/ to the scripts
    ("Claude Skills for TAPP/analysis/README.md",
     "`../../survey_colB_colI_20260812.py` and `../../build_colI_survey_findings_20260812.py`.",
     f"`../../{PFS}/survey_colB_colI_20260812.py` and\n"
     f"`../../{PFS}/build_colI_survey_findings_20260812.py`."),
    ("Claude Skills for TAPP/analysis/README.md",
     "Built by `../../triage_colB_uniformity_20260812.py`; harmonisation applied by "
     "`../../patch_colB_harmonise_20260812.py`.",
     f"Built by `../../{PFS}/triage_colB_uniformity_20260812.py`; harmonisation applied by "
     f"`../../{ONE}/patch_colB_harmonise_20260812.py`."),

    # ---- lit_assessment.md: an absolute path and a "at the TAPPs root" claim
    ("Claude Skills for TAPP/references/lit_assessment.md",
     "`paper_registry.csv` lives at `/Users/ruolin/Documents/Astromat/TAPPs/paper_registry.csv`.",
     "`paper_registry.csv` lives at "
     "`/Users/ruolin/Documents/Astromat/TAPPs/Project Files/Registers & Planning/"
     "paper_registry.csv`."),
    ("Claude Skills for TAPP/references/lit_assessment.md",
     "The registry is maintained by `generate_paper_registry.py` at the TAPPs root.",
     f"The registry is maintained by `generate_paper_registry.py` in `{PFS}/`."),
    # the planning table is a CSV, not an xlsx — wrong extension predates the move
    ("Claude Skills for TAPP/references/lit_assessment.md",
     'Technique columns use the **exact "Proposed TAPP Name"** from `TAPP_Planning_Table.xlsx`.',
     'Technique columns use the **exact "Proposed TAPP Name"** from '
     f'`{PFR}/TAPP_Planning_Table.csv`.'),
    ("Claude Skills for TAPP/references/lit_assessment.md",
     "If a technique used in a paper does not appear in `TAPP_Planning_Table.xlsx`",
     f"If a technique used in a paper does not appear in `{PFR}/TAPP_Planning_Table.csv`"),
    ("Claude Skills for TAPP/references/lit_assessment.md",
     'Always look up the exact "Proposed TAPP Name" in `TAPP_Planning_Table.xlsx` before adding a '
     'column.',
     'Always look up the exact "Proposed TAPP Name" in '
     f'`{PFR}/TAPP_Planning_Table.csv` before adding a column.'),

    # ---- workflow.md: "in the project root" is no longer true
    ("Claude Skills for TAPP/references/workflow.md",
     "**Always read `TAPP_Planning_Table.csv` (in the project root) before beginning Phase 0",
     f"**Always read `{PFR}/TAPP_Planning_Table.csv` before beginning Phase 0"),
    ("Claude Skills for TAPP/references/workflow.md",
     "**Search `TAPP_Development_Log.md` for the specific topic",
     f"**Search `{PFD}/TAPP_Development_Log.md` for the specific topic"),

    # ---- conventions.md: locate the registers and archived worksheets
    ("Claude Skills for TAPP/references/conventions.md",
     "`TAPP_Module_Register.csv` is the current register.",
     f"`{PFR}/TAPP_Module_Register.csv` is the current register."),
    ("Claude Skills for TAPP/references/conventions.md",
     "The Group 1 pass produced `Group1_Reconciliation_Decisions.csv`",
     f"The Group 1 pass produced `{ARCW}/Group1_Reconciliation_Decisions.csv`"),
    ("Claude Skills for TAPP/references/conventions.md",
     "`SolutionIntroduction_Reconciliation_Decisions.csv`, and Column F is complete",
     f"`{ARCW}/SolutionIntroduction_Reconciliation_Decisions.csv`, and Column F is complete"),
    ("Claude Skills for TAPP/references/conventions.md",
     "harmonised (`patch_colB_harmonise_20260812.py`, 71 rows across all 16 TAPPs).",
     f"harmonised (`{ONE}/patch_colB_harmonise_20260812.py`, 71 rows across all 16 TAPPs)."),

    # ---- precedents.md: stale filename, predates the move
    ("Claude Skills for TAPP/references/precedents.md",
     "in `analysis/Audit_ColI_vs_LitAssess_2026-08-12.csv`.",
     "in `analysis/Audit_ColI_vs_LitAssess.csv`."),
    ("Claude Skills for TAPP/references/precedents.md",
     "A full lint (`TAPP_Lint_Report_2026-08-11.csv`)",
     "A full lint (`Project Files/Reports/TAPP_Lint_Report_2026-08-11.csv`)"),

    # ---- module manifest: locate the archived evidence it cites
    ("Claude Skills for TAPP/modules/Module_SolutionIntroduction.json",
     "recorded field by field in SolutionIntroduction_Reconciliation_Decisions.csv.",
     f"recorded field by field in {ARCW}/SolutionIntroduction_Reconciliation_Decisions.csv."),

    # ---- root README file inventory
    ("README_TAPP_for_Schema_Generation.md",
     "| `TAPP_Development_Log.md` | Dated change history |",
     f"| `{PFD}/TAPP_Development_Log.md` | Dated change history |"),

    # ---- consolidated superseded folders: these paths WERE valid before the move
    ("LA-ICP-MS/README.md",
     "`Superseded TAPPs (2026-08-10)/LA-ICP-MS (stale branch)/`",
     "`Superseded TAPPs/2026-08-10/LA-ICP-MS (stale branch)/`"),
]

# Plain string replacements applied to every occurrence in the named file.
GLOBAL_FIXES = [
    ("composed_tapps.json", "Superseded TAPPs (2026-08-08)/", "Superseded TAPPs/2026-08-08/"),
    ("composed_tapps.json", "Superseded TAPPs (2026-08-10)/", "Superseded TAPPs/2026-08-10/"),
    ("composed_tapps.json", "Superseded TAPPs (2026-08-11)/", "Superseded TAPPs/2026-08-11/"),
    ("Project Files/Registers & Planning/TAPP_Planning_Table.csv",
     "Superseded TAPPs (2026-08-10)/", "Superseded TAPPs/2026-08-10/"),
]

LOG_NOTE = """> **Layout note, 2026-08-12.** The repository was reorganised on this date: loose root files moved
> into `Project Files/` (`Scripts/`, `Registers & Planning/`, `Reports/`, `Design Notes/`,
> `Presentations & Figures/`, `Reference/`), the four dated superseded folders were consolidated under
> `Superseded TAPPs/`, and working files moved to `Archive/`. **Paths written in dated entries below
> were correct when written and have not been rewritten.** For current locations see
> `Project Files/Design Notes/PLAN_Folder_Reorganisation_2026-08-12.md`.

"""
LOG = "Project Files/Design Notes/TAPP_Development_Log.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    applied, failed = [], []
    edits = {}
    for path, old, new in FIXES:
        p = os.path.join(ROOT, path)
        if not os.path.exists(p):
            failed.append(f"missing file: {path}")
            continue
        txt = edits.get(path) or open(p, encoding="utf-8").read()
        if old not in txt:
            failed.append(f"{path}: pattern not found -> {old[:66]!r}")
            continue
        edits[path] = txt.replace(old, new, 1)
        applied.append((path, old[:64], "exact"))

    for path, old, new in GLOBAL_FIXES:
        p = os.path.join(ROOT, path)
        if not os.path.exists(p):
            failed.append(f"missing file: {path}")
            continue
        txt = edits.get(path) or open(p, encoding="utf-8-sig").read()
        n = txt.count(old)
        if not n:
            failed.append(f"{path}: pattern not found -> {old!r}")
            continue
        edits[path] = txt.replace(old, new)
        applied.append((path, old, f"{n}x global"))

    # forward note at the top of the development log (does not rewrite history)
    p = os.path.join(ROOT, LOG)
    logtxt = open(p, encoding="utf-8").read()
    if "Layout note, 2026-08-12" not in logtxt:
        lines = logtxt.split("\n")
        ins = 1 if lines and lines[0].startswith("#") else 0
        edits[LOG] = "\n".join(lines[:ins] + ["", LOG_NOTE.rstrip()] + lines[ins:])
        applied.append((LOG, "insert forward layout note", "prepend"))

    for path, what, how in applied:
        print(f"  {'APPLY' if args.apply else 'DRY':5s} [{how:11s}] {path}")
        print(f"          {what}")
    if failed:
        print("\nFAILURES (nothing written):")
        for f in failed:
            print("  " + f)
        sys.exit(1)

    if args.apply:
        for path, txt in edits.items():
            enc = "utf-8-sig" if path.endswith(".csv") else "utf-8"
            open(os.path.join(ROOT, path), "w", encoding=enc).write(txt)
        print(f"\nwrote {len(edits)} file(s)")
    else:
        print(f"\n{len(applied)} fix(es) across {len(edits)} file(s) "
              f"(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
