# Plan — TAPPs folder reorganisation

**Status: REVISED WITH YOUR DECISIONS. FOR FINAL APPROVAL. Nothing has been moved.**
Date: 2026-08-12

| | Before | After |
|---|---|---|
| Loose files at root | **73** | **2** (+ `.DS_Store`, hidden) |
| Directories at root | 34 | **31** |
| Files deleted | — | **0** |

### Your decisions, applied throughout

1. **Nothing is deleted.** The two files I had proposed removing are moved instead (§3.7).
2. **The 17 technique folders with no TAPP yet stay at the root.** No `Techniques (planned)/`.
3. **`composed_tapps.json` stays at the root.** No edit to `recompose_all_20260812.py`'s register path.
4. **The six admin folders are grouped under one `Project Files/` parent** rather than sitting flat at
   root. This is what takes directories down to 31 instead of up to 36.

---

## 1. Read this first — three things are load-bearing

Some paths here are resolved at runtime. Moving the wrong thing breaks tooling *silently* rather than
erroring, so these constrain the plan.

### 1.1 `Claude Skills for TAPP/` must stay a direct child of the root

`compose_tapp.py` derives the library root by walking **up two levels from `scripts/`**:

```python
HERE      = os.path.dirname(os.path.abspath(__file__))   # …/Claude Skills for TAPP/scripts
SKILL_DIR = os.path.dirname(HERE)                        # …/Claude Skills for TAPP
ROOT      = os.path.dirname(SKILL_DIR)                   # …/TAPPs      ← the library root
```

`scripts/audit_keys_vs_literature.py` does the same. **Nesting the skill folder deeper breaks both.**
It does not move, and it keeps its exact name — 16 root scripts hardcode the literal string
`"Claude Skills for TAPP"`.

### 1.2 The 10 live technique folders must stay at the root

`composed_tapps.json` holds **16 root-relative TAPP paths** (`EPMA/EPMA_TAPP_v16.csv`,
`Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v16.csv`, …) resolved at runtime by
`recompose_all_20260812.py`. They stay where they are.

### 1.3 Directory exclusion is pattern-based — a convenience and a trap

`validate_tapp.py`'s `_excluded()` skips any directory that starts with `superseded`, contains
`archive`, is named `unpacked_tapp`, or starts with `.`. So consolidating the four dated superseded
folders under one `Superseded TAPPs/` parent and creating `Archive/` costs nothing — the exclusions
keep working automatically, including for everything nested inside.

> ⚠ **The trap:** never put a live TAPP in a folder whose name contains "archive" or starts with
> "superseded". It disappears from `validate_tapp.py`, `compose --check` and the audits **with no
> error at all** — the file simply stops being discovered. This is the main risk in the whole move,
> and §6 verifies against it by asserting the TAPP count is still 16.

---

## 2. Final structure

```
TAPPs/
├── README_TAPP_for_Schema_Generation.md        ← entry point
├── composed_tapps.json                          ← stays at root (your decision)
├── .claude/                                     ← Claude Code config, untouched
│
├── Claude Skills for TAPP/                      ← UNCHANGED, name and depth (§1.1)
│
├── EPMA/  SEM/  TEM/  XCT/                                  ┐
├── LA-MC-ICP-MS/  LA-Q-ICP-MS/  LA-SF-ICP-MS/               │ 10 live TAPP folders
├── Solution MC-ICP-MS/  Solution Q-ICP-MS/  Solution SF-ICP-MS/  ┘ UNCHANGED (§1.2)
│
├── Ar-Ar Geochronology/   Fission Track Dating/   INAA/   IRMS/     ┐
├── LA-ICP-MS/   Luminescence Dating/   Medical CT/   Mossbauer/     │ 17 folders with
├── NCT/   Raman/   Re-Os Geochronology/   SIMS/   SR-XCT/           │ no TAPP yet —
├── TIMS/   ToF-SIMS/   U-Th:He Geochronology/   XRD/                ┘ stay at root
│
├── Project Files/                               ← NEW parent for all admin material
│   ├── Registers & Planning/       4 files
│   ├── Scripts/                    6 live scripts
│   │   └── One-shot (applied)/    35 scripts
│   ├── Reports/                    4 files
│   ├── Design Notes/               3 files
│   ├── Presentations & Figures/    6 files
│   └── Reference/                  3 files
│
├── Superseded TAPPs/                            ← 4 dated folders consolidated under one parent
│   ├── 2026-08-08/   2026-08-10/   2026-08-11/   2026-08-12/
│
└── Archive/                                     ← NEW
    ├── Worksheets (reconciled)/    9 files
    ├── Pre-VIM3 Reference Archive (2026-07-24)/     ← moved in whole
    ├── .migration_backup_group1_20260808/           ← moved in whole, name unchanged
    └── unpacked_tapp/                               ← moved in whole
```

**Root ends up at 31 directories** — 27 technique folders plus `Claude Skills for TAPP/`,
`Project Files/`, `Superseded TAPPs/`, `Archive/` — **and 2 loose files.**

---

## 3. Destinations, file by file

### 3.1 Stays at root (2 files)

| File | Why |
|---|---|
| `README_TAPP_for_Schema_Generation.md` | Entry point — the first thing a reader should find |
| `composed_tapps.json` | Your decision; also avoids editing `recompose_all_20260812.py` |

### 3.2 `Project Files/Registers & Planning/` (4)

`TAPP_Planning_Table.csv` · `TAPP_Module_Register.csv` · `TAPP_Composed_Variants.csv` ·
`paper_registry.csv`

Live, hand-maintained registers. Two of them are **written** by `bump_and_stamp_20260812.py` → needs
a path update (§4).

### 3.3 `Project Files/Scripts/` (6 live)

| Script | What it does |
|---|---|
| `recompose_all_20260812.py` | Recomposes or `--check`s all 16 TAPPs from `composed_tapps.json` |
| `survey_colB_colI_20260812.py` | Column B vs Column I sweep |
| `build_colI_survey_findings_20260812.py` | Builds the adjudicated findings table |
| `triage_colB_uniformity_20260812.py` | Column B uniformity triage (Rule 7.8.9) |
| `bump_and_stamp_20260812.py` | Stamps Last Update, bumps versions, updates registers |
| `generate_paper_registry.py` | Builds `paper_registry.csv` |

### 3.4 `Project Files/Scripts/One-shot (applied)/` (35)

Every `patch_*`, `build_*`, `migrate_*`, `apply_*`, `retire_*`, `draft_*` script whose change is
already applied and version-bumped. **Kept, not deleted** — they are the audit trail for how the
library reached its current state, and several are cited in `precedents.md`.

One special case: **`audit_colI_vs_litassess_20260812.py` is superseded** by
`Claude Skills for TAPP/scripts/audit_keys_vs_literature.py`, the same tool promoted into the skill as
a standing Phase 3 step (Rule 7.12). The root copy goes here; the skill copy is the one to run. A
README in the folder will say so.

### 3.5 `Project Files/Reports/` (4)

`TAPP_Lint_Report_2026-08-07 / -08-08 / -08-11 / -08-12.csv`

### 3.6 `Project Files/Design Notes/` (3)

`TAPP_Development_Log.md` (186 KB running log) · `DRAFT_Rule7_KeyedBy_2026-08-11.md` ·
`RETROFIT-BRIEFING_Constants-Field-Rule5.md`

### 3.7 `Project Files/Presentations & Figures/` (6)

`TAPP for Better Metadata Reporting and Curation.pptx` · `… copy.pptx` · `… _revised.pptx` ·
`Definition Example.png` · `TAPP Development Workflow.png` ·
**`~$TAPP for Better Metadata Reporting and Curation_revised.pptx`**

That last one is an orphaned PowerPoint lock file (165 bytes). Per your instruction it is **moved, not
deleted** — it travels with the deck it belongs to. All three deck copies move as-is; I have not
assumed which is current.

### 3.8 `Project Files/Reference/` (3)

`Measurement Term Definitions VIM3.xlsx` · `TAPP template v1.xlsx` · `ada_stats_technique.rtf`

### 3.9 `Archive/Worksheets (reconciled)/` (9)

Working files whose decisions are already applied to the TAPPs and recorded in `precedents.md` /
`conventions.md`:

`Group1_Reconciliation_Decisions.csv` · `RepeatKey_Audit_Test1-4_2026-08-10.csv` ·
`SolutionIntroduction_ColumnF_WORKSHEET.{csv,xlsx}` ·
`SolutionIntroduction_Reconciliation_{Decisions.csv,WORKSHEET.csv,WORKSHEET.xlsx}` ·
`TAPP_Planning_Table (outdated).xlsx` · `TAPP_Planning_Table_PRE-RESTRUCTURE_2026-08-08.csv`

⚠ `RepeatKey_Audit_Test1-4_2026-08-10.csv` is **cited as evidence** in the Rule 7 record. Archived,
never deleted.

### 3.10 Whole folders moved into `Archive/` (3)

| Folder | Note |
|---|---|
| `Pre-VIM3 Reference Archive (2026-07-24)/` | 11 files. Already auto-excluded by name; still is |
| `.migration_backup_group1_20260808/` | 14 old TAPP CSVs from the Aug 8 migration. **Name unchanged**, so it stays hidden and stays excluded |
| `unpacked_tapp/` | An unzipped `.pptx` (`[Content_Types].xml`, `ppt/`, `docProps/`). Moved, not deleted |

### 3.11 Left exactly where it is (1)

`.DS_Store` — hidden Finder metadata that macOS regenerates on its own. Moving it accomplishes
nothing and it contributes nothing to the clutter you see. Not deleted, not moved.

---

## 4. Script edits this requires

Contained, and all in scripts I wrote:

**a) The 6 live scripts now sit two levels below the root**, so their `ROOT` must climb two levels.
They currently do:

```python
ROOT = os.path.dirname(os.path.abspath(__file__))          # was: the library root
```

which after the move resolves to `Project Files/Scripts/`. Fix, one line each:

```python
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
```

**b) `bump_and_stamp_20260812.py`** writes `TAPP_Module_Register.csv` and
`TAPP_Composed_Variants.csv` → repoint to `Project Files/Registers & Planning/`.

**c) The 35 one-shot scripts are NOT edited.** Rewriting already-applied history would falsify the
audit trail. Their `ROOT` will be wrong if anyone re-runs them from their new location, but the
failure is safe and immediate — they import `validate_tapp` from a path that no longer exists and
error on import rather than operating on the wrong directory. The folder README will state that they
assume the library root and are kept for reference only.

**d) Nothing in `Claude Skills for TAPP/` changes**, so the skill install sync is unaffected.

---

## 5. Not doing (out of scope for "only re-organise")

- **The 4 stale `tapp` paths in `composed_tapps.json`** pointing at retired folders
  (`LA-ICP-MS/LA-ICPMS_TAPP_v13.csv` and the two LA-ICP-MS Geochronology entries). They are
  documentation, not resolved at runtime, so they are harmless — but worth a separate cleanup.
- **Deciding which of the three deck copies is current.** All three move together untouched.
- **The 17-field MIXED Column B backlog** from the previous session. Unrelated to this move.

---

## 6. Verification after the move

| Risk | Check |
|---|---|
| A live TAPP landed in an auto-excluded folder (§1.3) | `validate_tapp.py` must still report **16 TAPP files** |
| A moved register broke a live script | `recompose_all_20260812.py --check` → **16 MATCH** |
| Lint state regressed | **0 ERROR / 0 WARN / 85 INFO**, unchanged |
| Key audit regressed | `audit_keys_vs_literature.py` → **0 NEW** |
| A file went missing | Manifest count: **73 files relocated, 0 deleted**; total file count under `TAPPs/` unchanged |

```bash
python3 "Claude Skills for TAPP/scripts/validate_tapp.py" --root . --severity WARN
python3 "Project Files/Scripts/recompose_all_20260812.py" --check
python3 "Claude Skills for TAPP/scripts/audit_keys_vs_literature.py"
```

## 7. How I would execute it

A single script with `--dry-run` (default) and `--apply`, in the same discipline as the patch
scripts:

1. Count every file under `TAPPs/` before the move, and record it.
2. Create the new directories.
3. `mv` each file/folder per the manifest above — **never overwrite**; abort if a destination exists.
4. Write `MOVE_MANIFEST_2026-08-12.csv` (every `from → to` pair) into `Project Files/`, so the whole
   move is reversible from a printed record.
5. Apply the §4 script edits.
6. Re-count files, assert the total is unchanged and that 0 were deleted.
7. Run the §6 verification and report.

**All questions are resolved — say go and I will dry-run it first, then apply.**
