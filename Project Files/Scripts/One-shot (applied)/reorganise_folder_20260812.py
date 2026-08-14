#!/usr/bin/env python3
"""Execute the TAPPs folder reorganisation per PLAN_Folder_Reorganisation_2026-08-12.md.

Nothing is deleted. Every move is recorded in a manifest so the whole operation is reversible from a
printed record. Destinations are enumerated by exact filename rather than derived by heuristic, so a
file cannot land somewhere unintended.

  --dry-run   (default) print the manifest and every check, touch nothing
  --apply     create directories, move, write the manifest, patch the script paths
  --revert M  undo a previous run using its manifest CSV

Safety
------
* Aborts before moving anything if any destination already exists.
* Aborts if the pre-move file census cannot be reproduced afterwards.
* Never overwrites; never deletes.
"""
import argparse
import csv
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SELF = os.path.basename(os.path.abspath(__file__))

PF = "Project Files"
ARCH = "Archive"
SUP = "Superseded TAPPs"

STAY = {"README_TAPP_for_Schema_Generation.md", "composed_tapps.json", ".DS_Store", SELF}

REGISTERS = ["TAPP_Planning_Table.csv", "TAPP_Module_Register.csv",
             "TAPP_Composed_Variants.csv", "paper_registry.csv"]

LIVE_SCRIPTS = ["recompose_all_20260812.py", "survey_colB_colI_20260812.py",
                "build_colI_survey_findings_20260812.py", "triage_colB_uniformity_20260812.py",
                "bump_and_stamp_20260812.py", "generate_paper_registry.py"]

REPORTS = [f"TAPP_Lint_Report_2026-08-{d}.csv" for d in ("07", "08", "11", "12")]

DESIGN = ["TAPP_Development_Log.md", "DRAFT_Rule7_KeyedBy_2026-08-11.md",
          "RETROFIT-BRIEFING_Constants-Field-Rule5.md",
          "PLAN_Folder_Reorganisation_2026-08-12.md"]

PRESENT = ["TAPP for Better Metadata Reporting and Curation.pptx",
           "TAPP for Better Metadata Reporting and Curation copy.pptx",
           "TAPP for Better Metadata Reporting and Curation_revised.pptx",
           "~$TAPP for Better Metadata Reporting and Curation_revised.pptx",
           "Definition Example.png", "TAPP Development Workflow.png"]

REFERENCE = ["Measurement Term Definitions VIM3.xlsx", "TAPP template v1.xlsx",
             "ada_stats_technique.rtf"]

WORKSHEETS = ["Group1_Reconciliation_Decisions.csv", "RepeatKey_Audit_Test1-4_2026-08-10.csv",
              "SolutionIntroduction_ColumnF_WORKSHEET.csv",
              "SolutionIntroduction_ColumnF_WORKSHEET.xlsx",
              "SolutionIntroduction_Reconciliation_Decisions.csv",
              "SolutionIntroduction_Reconciliation_WORKSHEET.csv",
              "SolutionIntroduction_Reconciliation_WORKSHEET.xlsx",
              "TAPP_Planning_Table (outdated).xlsx",
              "TAPP_Planning_Table_PRE-RESTRUCTURE_2026-08-08.csv"]

# whole directories moved intact
DIR_MOVES = [
    ("Superseded TAPPs (2026-08-08)", f"{SUP}/2026-08-08"),
    ("Superseded TAPPs (2026-08-10)", f"{SUP}/2026-08-10"),
    ("Superseded TAPPs (2026-08-11)", f"{SUP}/2026-08-11"),
    ("Superseded TAPPs (2026-08-12)", f"{SUP}/2026-08-12"),
    ("Pre-VIM3 Reference Archive (2026-07-24)", f"{ARCH}/Pre-VIM3 Reference Archive (2026-07-24)"),
    (".migration_backup_group1_20260808", f"{ARCH}/.migration_backup_group1_20260808"),
    ("unpacked_tapp", f"{ARCH}/unpacked_tapp"),
]

NEW_DIRS = [PF, f"{PF}/Registers & Planning", f"{PF}/Scripts",
            f"{PF}/Scripts/One-shot (applied)", f"{PF}/Reports", f"{PF}/Design Notes",
            f"{PF}/Presentations & Figures", f"{PF}/Reference",
            SUP, ARCH, f"{ARCH}/Worksheets (reconciled)"]

# ---- path fixes: the 6 live scripts move two levels down -------------------------------
OLD_ROOT = "ROOT = os.path.dirname(os.path.abspath(__file__))"
NEW_ROOT = ('ROOT = os.path.abspath(os.path.join(\n'
            '    os.path.dirname(os.path.abspath(__file__)), "..", ".."))'
            '   # library root: this script lives in "Project Files/Scripts/"')

EDITS = [
    # (relative path after the move, old substring, new substring, required?)
    (f"{PF}/Scripts/bump_and_stamp_20260812.py",
     'mr = os.path.join(ROOT, "TAPP_Module_Register.csv")',
     'mr = os.path.join(ROOT, "Project Files", "Registers & Planning",\n'
     '                      "TAPP_Module_Register.csv")', True),
    (f"{PF}/Scripts/bump_and_stamp_20260812.py",
     'cv = os.path.join(ROOT, "TAPP_Composed_Variants.csv")',
     'cv = os.path.join(ROOT, "Project Files", "Registers & Planning",\n'
     '                      "TAPP_Composed_Variants.csv")', True),
    (f"{PF}/Scripts/generate_paper_registry.py",
     "OUT = os.path.join(os.path.dirname(__file__), 'paper_registry.csv')",
     "OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',\n"
     "                   'Project Files', 'Registers & Planning', 'paper_registry.csv')", True),
]

ONESHOT_README = """# One-shot scripts (already applied)

Every script here made a change that is already applied to the TAPPs and version-bumped. They are
kept as the audit trail for how the library reached its current state — several are cited in
`Claude Skills for TAPP/references/precedents.md`.

**They are deliberately NOT path-corrected for this folder.** Rewriting already-applied history would
falsify the audit trail. Each computes its library root as its own directory, which is no longer
correct here, so re-running one from this location fails immediately on import rather than operating on
the wrong directory. If you ever need to re-run one, copy it to the library root first.

`audit_colI_vs_litassess_20260812.py` is superseded by
`Claude Skills for TAPP/scripts/audit_keys_vs_literature.py` — the same tool promoted into the skill as
a standing Phase 3 step (Rule 7.12). Run the skill copy, not this one.
"""


def census(root):
    """Every file under root, as paths relative to root. Excludes nothing."""
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            out.add(os.path.relpath(os.path.join(dirpath, fn), root))
    return out


def build_manifest():
    moves = []
    for fn in REGISTERS:
        moves.append((fn, f"{PF}/Registers & Planning/{fn}"))
    for fn in LIVE_SCRIPTS:
        moves.append((fn, f"{PF}/Scripts/{fn}"))
    for fn in REPORTS:
        moves.append((fn, f"{PF}/Reports/{fn}"))
    for fn in DESIGN:
        moves.append((fn, f"{PF}/Design Notes/{fn}"))
    for fn in PRESENT:
        moves.append((fn, f"{PF}/Presentations & Figures/{fn}"))
    for fn in REFERENCE:
        moves.append((fn, f"{PF}/Reference/{fn}"))
    for fn in WORKSHEETS:
        moves.append((fn, f"{ARCH}/Worksheets (reconciled)/{fn}"))

    named = {m[0] for m in moves} | STAY
    # every remaining .py at root is a one-shot
    oneshot = sorted(f for f in os.listdir(ROOT)
                     if f.endswith(".py") and f not in named
                     and os.path.isfile(os.path.join(ROOT, f)))
    for fn in oneshot:
        moves.append((fn, f"{PF}/Scripts/One-shot (applied)/{fn}"))
    return moves, oneshot


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--revert", metavar="MANIFEST")
    args = ap.parse_args()

    if args.revert:
        rows = list(csv.DictReader(open(args.revert, encoding="utf-8-sig")))
        n = 0
        for r in reversed(rows):
            src = os.path.join(ROOT, r["to"])
            dst = os.path.join(ROOT, r["from"])
            if os.path.exists(src) and not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst) or ROOT, exist_ok=True)
                shutil.move(src, dst)
                n += 1
        print(f"reverted {n} of {len(rows)} entries")
        return

    before = census(ROOT)
    moves, oneshot = build_manifest()
    dirmoves = [(s, d) for s, d in DIR_MOVES if os.path.exists(os.path.join(ROOT, s))]

    # ---- preflight
    problems = []
    for s, _ in moves:
        if not os.path.isfile(os.path.join(ROOT, s)):
            problems.append(f"source missing: {s}")
    for _, d in moves + dirmoves:
        if os.path.exists(os.path.join(ROOT, d)):
            problems.append(f"destination already exists: {d}")
    leftover = [f for f in os.listdir(ROOT)
                if os.path.isfile(os.path.join(ROOT, f))
                and f not in STAY and f not in {m[0] for m in moves}]
    if leftover:
        problems.append(f"unclassified root file(s), refusing to guess: {leftover}")

    print(f"{len(moves)} file move(s) + {len(dirmoves)} directory move(s)")
    print(f"  {len(oneshot)} one-shot scripts detected")
    print(f"  staying at root: {sorted(STAY - {SELF})}")
    print()
    from collections import Counter
    for dest, n in sorted(Counter(os.path.dirname(d) for _, d in moves).items()):
        print(f"  {n:3d} -> {dest}/")
    for s, d in dirmoves:
        print(f"   dir  {s}  ->  {d}")

    if problems:
        print("\nPREFLIGHT FAILED — nothing moved:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("\npreflight OK")

    if not args.apply:
        print("(dry run — pass --apply to execute)")
        return

    # ---- execute
    for d in NEW_DIRS:
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    done = []
    for s, d in moves + dirmoves:
        shutil.move(os.path.join(ROOT, s), os.path.join(ROOT, d))
        done.append((s, d))

    man = os.path.join(ROOT, PF, "MOVE_MANIFEST_2026-08-12.csv")
    with open(man, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["from", "to"])
        w.writerows(done)
    with open(os.path.join(ROOT, PF, "Scripts", "One-shot (applied)", "README.md"),
              "w", encoding="utf-8") as f:
        f.write(ONESHOT_README)

    # ---- path fixes
    fixed = 0
    for rel in [f"{PF}/Scripts/{s}" for s in LIVE_SCRIPTS]:
        p = os.path.join(ROOT, rel)
        t = open(p, encoding="utf-8").read()
        if OLD_ROOT in t:
            open(p, "w", encoding="utf-8").write(t.replace(OLD_ROOT, NEW_ROOT, 1))
            fixed += 1
    for rel, old, new, required in EDITS:
        p = os.path.join(ROOT, rel)
        t = open(p, encoding="utf-8").read()
        if old in t:
            open(p, "w", encoding="utf-8").write(t.replace(old, new, 1))
            fixed += 1
        elif required:
            print(f"  WARN edit target not found in {rel}: {old[:60]!r}")
    print(f"\nmoved {len(done)} item(s); {fixed} path fix(es) applied")
    print(f"manifest: {man}")

    # ---- census: nothing lost, nothing deleted
    after = census(ROOT)
    created = {os.path.relpath(man, ROOT),
               f"{PF}/Scripts/One-shot (applied)/README.md"}
    lost = before - after - set()
    # a moved file changes its relative path, so compare by basename multiset instead
    from collections import Counter as C
    b, a = C(os.path.basename(x) for x in before), C(os.path.basename(x) for x in after)
    missing = {k: b[k] - a[k] for k in b if b[k] > a[k]}
    print(f"\nfiles before: {len(before)}   after: {len(after)}   "
          f"(expected +{len(created)} for manifest + README)")
    if missing:
        print(f"  MISSING: {missing}")
        sys.exit(1)
    print("  census OK — no file lost, none deleted")


if __name__ == "__main__":
    main()
