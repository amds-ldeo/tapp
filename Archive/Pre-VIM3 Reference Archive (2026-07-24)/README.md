# Pre-VIM3 Reference Archive (2026-07-24)

These are frozen, byte-for-byte snapshots (plus one prepended "archived/outdated" banner or marker
row each) of every living reference document, template, and script as they stood **immediately
before** the VIM3 (BIPM/JCGM 200:2012) terminology migration on 2026-07-24.

**Why this exists:** unlike versioned TAPP CSVs (`[Technique]_TAPP_v[N].csv`), these files are edited
in place and carry no version number of their own. This archive is the "before" record for that
edit, kept so the terminology change is auditable later.

**What changed, in one line:** "Protocol" (the registerable, DOI-bearing object) was renamed to
"Procedure"; the old "Procedure" (the analysis-level execution) was formally renamed to "Measurement"
per VIM3, but the working/user-facing label in TAPP stays "Analysis" — see `conventions.md`'s
Vocabulary table (current version) for the full definitions and VIM3 citations.

**Do not edit these files, and do not use them as a template or reference for current TAPP work.**
The current, authoritative versions live at their original paths in the TAPPs project.

## Contents

- `conventions_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/references/conventions.md` as it stood before the VIM3 migration
- `workflow_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/references/workflow.md` as it stood before the VIM3 migration
- `field-review_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/references/field-review.md` as it stood before the VIM3 migration
- `precedents_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/references/precedents.md` as it stood before the VIM3 migration
- `lit_assessment_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/references/lit_assessment.md` as it stood before the VIM3 migration
- `SKILL_PRE-VIM3_2026-07-24.md` — snapshot of `Claude Skills for TAPP/SKILL.md` as it stood before the VIM3 migration
- `Template TAPP Group 1_PRE-VIM3_2026-07-24.csv` — snapshot of `Claude Skills for TAPP/tapp_files/Template TAPP Group 1.csv` as it stood before the VIM3 migration
- `tapp_to_xlsx_PRE-VIM3_2026-07-24.py` — snapshot of `Claude Skills for TAPP/scripts/tapp_to_xlsx.py` as it stood before the VIM3 migration
- `TAPP_Development_Log_PRE-VIM3_2026-07-24.md` — snapshot of `TAPP_Development_Log.md` as it stood before the VIM3 migration
- `TAPP_Planning_Table_PRE-VIM3_2026-07-24.csv` — snapshot of `TAPP_Planning_Table.csv` as it stood before the VIM3 migration

## Not archived here

- The 12 current-version TAPP CSVs/xlsx (EPMA, LA-ICP-MS, LA-Q/SF-ICP-MS, SEM x4, Solution MC/Q/SF-ICP-MS,
  TEM, XCT) are not duplicated in this folder — they already carry their own version-numbered filenames
  (e.g. `EPMA_TAPP_v7.csv`), which remain on disk unchanged as the pre-migration record. The migration
  created new integer-bumped versions (v7 -> v8, etc.) alongside them.
- The installation copy of `SKILL.md` (Claude skill-installation path, outside this project folder) was
  identical to the project copy archived here at the time of archiving, so it was not separately duplicated.
