---
name: project-tapp-folder-layout
description: "TAPPs folder layout after the 2026-08-12 reorganisation — where things live now, and the three path constraints that make some folders unmovable"
metadata: 
  node_type: memory
  type: project
---

**Reorganised 2026-08-12.** Root went from 73 loose files to **2**, and 34 directories to **31**.
Nothing was deleted. Manifest of every move: `Project Files/MOVE_MANIFEST_2026-08-12.csv` (the move
script takes `--revert MANIFEST`). Plan: `Project Files/Design Notes/PLAN_Folder_Reorganisation_2026-08-12.md`.

## Where things are now

| Path | Contents |
|---|---|
| *root* | only `README_TAPP_for_Schema_Generation.md` and `composed_tapps.json` |
| `Claude Skills for TAPP/` | the skill — `references/`, `scripts/`, `modules/`, `analysis/`, `SKILL.md` |
| 10 live technique folders | EPMA, SEM, TEM, XCT, LA-MC/Q/SF-ICP-MS, Solution MC/Q/SF-ICP-MS |
| 17 technique folders, no TAPP yet | Ar-Ar, Fission Track, INAA, IRMS, LA-ICP-MS, Luminescence, Medical CT, Mossbauer, NCT, Raman, Re-Os, SIMS, SR-XCT, TIMS, ToF-SIMS, U-Th:He, XRD — **kept at root by author decision** |
| `Project Files/Registers & Planning/` | TAPP_Planning_Table, TAPP_Module_Register, TAPP_Composed_Variants, paper_registry |
| `Project Files/Scripts/` | 6 live scripts (see below) |
| `Project Files/Scripts/One-shot (applied)/` | 37 applied patch/build scripts + README |
| `Project Files/Reports/` | dated `TAPP_Lint_Report_*.csv` |
| `Project Files/Design Notes/` | TAPP_Development_Log.md, DRAFT_Rule7, RETROFIT-BRIEFING, the reorg plan |
| `Project Files/Presentations & Figures/`, `Project Files/Reference/` | decks, figures, VIM3 xlsx, template, ada stats |
| `Superseded TAPPs/{2026-08-08,-08-10,-08-11,-08-12}/` | 4 dated folders consolidated under one parent |
| `Archive/` | `Worksheets (reconciled)/`, `Pre-VIM3 Reference Archive (2026-07-24)/`, `.migration_backup_group1_20260808/`, `unpacked_tapp/` |
| `Current TAPPs/` | **Rule 12 mirror** (added 2026-08-12) — flat, latest CSV + xlsx for every TAPP (32 files) + generated README. The folder to hand to another developer |

**Live scripts** in `Project Files/Scripts/`: `recompose_all_20260812.py` (recompose/`--check` all 16
from `composed_tapps.json`), `survey_colB_colI_20260812.py`, `build_colI_survey_findings_20260812.py`,
`triage_colB_uniformity_20260812.py`, `bump_and_stamp_20260812.py`, `generate_paper_registry.py`.

## ⚠ Three constraints — do not move these

1. **`Claude Skills for TAPP/` must stay a DIRECT child of the root.** `scripts/compose_tapp.py` and
   `scripts/audit_keys_vs_literature.py` derive the library root by walking **up two levels from
   `scripts/`**. Nesting the skill folder deeper breaks both silently.
2. **Do not rename `Claude Skills for TAPP`.** 16 archived scripts hardcode the literal string. The
   name is load-bearing even though the two skill scripts derive it from `__file__`.
3. **The 10 live technique folders must stay at root.** `composed_tapps.json` holds 16 root-relative
   TAPP paths resolved at runtime by `recompose_all_20260812.py`.

## Rule 12 — the `Current TAPPs/` mirror

**Every TAPP creation or version bump copies the new CSV + xlsx into `Current TAPPs/`, replacing the
version it supersedes.** Technique folders keep every version; the mirror keeps exactly one. Purpose:
hand the whole folder over as a unit. That is also why a *stale* mirror is worse than none — the
recipient cannot tell.

- Refresh: `Project Files/Scripts/sync_current_tapps.py --apply` (dry-run by default)
- Automatic: `bump_and_stamp_20260812.py` calls it at the end of every bump
- Check: `validate_tapp.py` → `check_current_tapps`, **WARN** — `rule12-{missing-folder,stale,absent,extra,differs}`
- It is a COPY, never an editing target.

**⚠ The mirror MUST stay excluded from `discover()`** (`CURRENT_DIR` in `validate_tapp.py`). Verified by
construction before building it: without the exclusion every TAPP is found twice and, for equal
versions, which path is authoritative depends on `os.walk` order. Worse — **a copy accidentally bumped
inside the mirror out-ranks the real file and becomes what the linter validates**, while
`compose_tapp.py` keeps using the technique-folder path from `composed_tapps.json`. The two then
silently disagree about which file is live.

## ⚠ The silent-failure trap

`validate_tapp.py`'s `_excluded()` is **pattern-based**: it skips any directory starting with
`superseded`, containing `archive`, named `unpacked_tapp`, or starting with `.`. That is why
consolidating the superseded folders and creating `Archive/` cost nothing. **But a live TAPP placed in
any folder whose name contains "archive" disappears from `validate_tapp.py`, `compose --check` and the
audits with NO error** — it simply stops being discovered. Always assert the TAPP count is still 16
after moving anything.

## Path conventions after the move

- Live scripts resolve `ROOT` **two levels up** from themselves. New scripts placed in
  `Project Files/Scripts/` must do the same.
- The **37 one-shot scripts were deliberately NOT path-corrected** — rewriting applied history would
  falsify the audit trail. They fail on import from their new location rather than operating on the
  wrong directory. To re-run one, copy it to the library root first.
- Verification after any structural change:
  `validate_tapp.py --root .` (expect **16 TAPPs, 0 ERROR / 0 WARN / 85 INFO**) · `Project Files/Scripts/sync_current_tapps.py` (expect **0 to copy, 0 to remove**) ·
  `Project Files/Scripts/recompose_all_20260812.py --check` (**16 MATCH**) ·
  `Claude Skills for TAPP/scripts/audit_keys_vs_literature.py` (**0 NEW**).

**Path references repaired after the move (2026-08-12).** The move verified that scripts *run*; a
second pass verified that documentation still *points* correctly — they are different checks and the
first does not imply the second. 23 fixes across 11 files: `analysis/README.md` relative script paths,
an absolute path and two "at the TAPPs root" claims in `lit_assessment.md`, a "(in the project root)"
claim in `workflow.md`, register/worksheet locations in `conventions.md`, the root README's file
inventory, `LA-ICP-MS/README.md`, and **9 consolidated-superseded paths inside `composed_tapps.json`
plus 3 in `TAPP_Planning_Table.csv`** — those had been valid before the move and were broken by it.
Script: `Project Files/Scripts/fix_paths_after_reorg_20260812.py`.

Two stale references found that **predate** the move and were fixed in passing: `precedents.md` cited
`analysis/Audit_ColI_vs_LitAssess_2026-08-12.csv` (renamed to `Audit_ColI_vs_LitAssess.csv` when the
audit became a standing tool), and `lit_assessment.md` cited `TAPP_Planning_Table.xlsx` when the live
register is the `.csv`.

**Historical files deliberately NOT rewritten:** `MOVE_MANIFEST`, the reorg plan,
`TAPP_Development_Log.md` (given a forward layout note at the top instead), `DRAFT_Rule7`,
`RETROFIT-BRIEFING`, and the MC-ICP-MS technology note. Their old paths were correct when written.

**`composed_tapps.json` — 3 of the 4 "stale paths" were never stale.** In the **`retired`** list,
`tapp` is the TAPP's **HISTORICAL** path (its identity while live) and `moved_to` gives the current
location; `tapp` is deliberately unresolvable and **must not be rewritten**. An `os.path.exists` test
is the wrong test for that field — applying it produced three phantom findings. This convention is now
stated in the file's own `note`. Everywhere else (`composed[].tapp`, `derived_from`) paths are current
and resolvable.

Only **1** was a real defect, fixed 2026-08-12: `LA-MC-ICPMS_TAPP_v10`'s
`derived_from: LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v6.csv` cited the pre-split TAPP by its old live path
while the LA-Q and LA-SF entries cited the *same file* by its archived path — an internal
inconsistency, now aligned. All composed paths resolve; all retired entries locate via `moved_to`.

**Two register gaps left alone deliberately** (documentation content, not paths): the LA-Q_SF-ICP-MS
split of 2026-08-11 has **no `retired` entry**, though the other three retirements do — reconstructing
its `superseded_by`/`verification` from memory risked being wrong. And `LA-MC-ICP-MS/` still holds live
copies of `LA-MC-ICPMS_TAPP_v1/v2.csv` and `_UPb_TAPP_v1/v2.csv` that were never moved to
`Superseded TAPPs/`; the `derived_from` pointing at v1 resolves because of that.

**Left alone deliberately:** `.DS_Store` (hidden, Finder regenerates it); the 4 stale `tapp` paths in
`composed_tapps.json` pointing at retired folders (documentation only, not resolved at runtime); which
of the three near-identical decks is current.

See [[project_tapp_module_architecture]], [[reference_skill_paths]], [[project_tapp_colB_colI_survey]].
