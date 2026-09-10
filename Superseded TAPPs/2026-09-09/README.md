# Superseded TAPPs — 2026-09-09

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

**This is a routine version-bump folder, not a retirement.** It differs in kind from the
`2026-08-08`, `2026-08-10` and `2026-08-11` folders, which record structural retirements — a TAPP
decomposed into modules, a stale branch archived, a TAPP split in two. Nothing was retired here.
Every file below is an ordinary previous version of a TAPP that is still live under a higher version
number, and every field in it survives in its successor.

## What was superseded, and by what

| Superseded | Successor | Caused by |
|---|---|---|
| `LA-MC-ICPMS_TAPP_v70` | `v72` | change 1 |
| `LA-MC-ICPMS_TAPP_v71` | `v72` | change 2 |
| `EPMA_TAPP_v63` | `v65` | change 2 |
| `EPMA_TAPP_v64` | `v65` | change 3 |
| `LA-MC-ICPMS_UPb_TAPP_v70` | `v71` | change 2 |
| `LA-Q-ICP-MS_TAPP_v73` | `v74` | change 2 |
| `LA-Q-ICP-MS_UPb_TAPP_v73` | `v74` | change 2 |
| `LA-SF-ICP-MS_TAPP_v70` | `v71` | change 2 |
| `LA-SF-ICP-MS_UPb_TAPP_v71` | `v72` | change 2 |
| `Lab-XCT_TAPP_v38` | `v39` | change 2 |
| `SEM_Composition_TAPP_v60` | `v61` | change 2 |
| `SEM_FIBSEM_TAPP_v31` | `v32` | change 2 |
| `SEM_Imaging_TAPP_v30` | `v31` | change 2 |
| `SEM_TAPP_v61` | `v62` | change 2 |
| `TEM_TAPP_v49` | `v50` | change 2 |

15 versions, 30 files (CSV + xlsx). Two TAPPs appear twice because two changes landed on the same
day: LA-MC-ICP-MS was bumped by changes 1 and 2, EPMA by changes 2 and 3.

## The three changes

**1. LA-MC-ICP-MS v70 → v71 — Zhang et al. 2022 re-extracted.**
`patch_lamcicpms_zhang2022_reextract_20260909.py`. The `Target Species` cell held Table 1's
Cup-configuration row — a follow-up that `patch_lamcicpms_zhang2022_litassess_20260810.py` recorded
in its own docstring and deferred, and which the 2026-09-01 `Analyte` → `Target Species` rename then
made harder to see. `Target Species` is now `Rb, Sr`; `Collector Configuration` holds the cup map
with the Kr/Er/Yb interference monitors marked as orphan `channel` members (Rule 7.3.1). The same
pass resolved all 53 blank cells in that column to a value, `N` or `N/A` — 26 substantive, 14 `N`,
12 `N/A` — `references/lit_assessment.md` forbidding blanks. Column 14 only; Column H untouched,
re-extracting literature not being an edit to a field definition.

**2. `Analytical Mode` Column F, 13 TAPPs — Rule 3 conformance.**
`harmonise_analytical_mode_colf_20260909.py`. Composite `A; B` entries dropped, and the single
quotes that bracketed them with them. Rule 3 makes semicolon-joining the **combining rule**, not a
vocabulary member, so `'Spot; Transect'` had promoted a rule into a fifth member of a closed list.
The quoting was deliberate rather than a defect — all 13 quoted TAPPs carried a composite and all 3
unquoted ones (the Solution family) carried none — which is why it went with the composites and not
on its own. Members verified against each TAPP's own mode flag headers before writing. The three
Solution TAPPs are untouched: they have no mode flag columns, so Rule 3's vocabulary clause has no
labels to bind them to. Column H stamped — changing which values a controlled list admits is a
substantive edit to the field.

**3. EPMA v64 → v65 — `Analytical Mode` members reordered.**
`reorder_epma_analytical_mode_20260909.py`. Into mode flag column order, read from the header rather
than hardcoded. Set-identical, so no vocabulary changed. EPMA was the last flag-bearing TAPP out of
order after change 2.

## Verification

`validate_tapp.py` reports **0 ERROR, 0 WARN** after all three, with the same 39 INFO items as
before — all pre-existing registered divergences. `audit_keys_vs_literature.py` reports **0 new**
key/literature disagreements (Rule 7.12). `composed_tapps.json` and
`Project Files/Registers & Planning/TAPP_Composed_Variants.csv` were advanced to the new paths;
leaving either stale is an ERROR (`register-stale-tapp-path`, `doc-stale-version-ref`). The Rule 12
mirror was re-synced.

No field was added, removed or renamed on 2026-09-09, and no tier, data type or `Keyed By` value
changed. Only Column F (changes 2 and 3), one literature column (change 1) and Column H were touched.

## A note on `LA-MC-ICPMS_TAPP_v70`

It was parked here later than the rest. `patch_lamcicpms_zhang2022_reextract_20260909.py` wrote v71
but did not move its predecessor, unlike `bump_for_module_*` and the `harmonise_*` scripts, which
park the superseded pair as they go. v70 therefore sat loose in the untracked `LA-MC-ICP-MS/` working
folder — outside the repository, and out of step with v66–v69, all of which are parked under their
own dates. Moved here once noticed, so the day's set is complete.

That same patch left one other trace: `LA-MC-ICPMS_TAPP_v71.csv` in this folder is the only CSV in
the library written without a UTF-8 BOM, the script having used plain `utf-8`. v70, written by an
earlier script, carries it. The norm was restored when v71 was superseded, and all 16 current TAPPs
carry the BOM.
