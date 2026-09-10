#!/usr/bin/env python3
"""Fill the Why / Verification sections of the seven backfilled superseded READMEs.

`superseded_readme.py --all` generated the derived half. This supplies the half that
needs judgement, for the seven folders that were parked before the step existed.

EVERY claim below is sourced, and the sources are named in the text so a reader can
check them: the dated entries in `Project Files/Design Notes/TAPP_Development_Log.md`,
the dated commit subjects in git, and the dated patch scripts in
`Project Files/Scripts/`. Where a date has no dev-log entry the commits carry it, and
where it has no commits (2026-08-12 predates the repository's first commit, 2026-08-14)
the dev-log entry and a contemporaneous lint report carry it.

WHAT IS NOT CLAIMED. These READMEs are reconstructions written on 2026-09-10, not
contemporaneous records, and each says so in place. In particular no per-date
`validate_tapp.py` result is asserted for a date whose output was not recorded — only
2026-08-12 has a contemporaneous lint report. Inventing a clean bill of health for a
past date would be worse than leaving the section thin.
"""

import io, os, re, sys

STAMP = "2026-09-10"

RECON = ("> **Reconstructed %s.** This folder was parked before bump scripts wrote a README, so "
         "the\n> notes below were assembled afterwards from the dated entries in "
         "`../../Project Files/Design Notes/TAPP_Development_Log.md`, the dated commit subjects in "
         "git, and the\n> dated patch scripts in `../../Project Files/Scripts/`. It is not a "
         "contemporaneous record.\n" % STAMP)

WHY = {
"2026-08-12": """The Rule 13 session/sample restructure, the `analyte` settlement, and the folder
reorganisation — the largest single-day change in the library's history to that point. Recorded in
full in the development log under *"Rule 13, the `analyte` settlement, and a schema-facing sweep"*.

- **Rule 13** — the analysis record is the **session**, not one sample. `sample` entered the key
  vocabulary as an anchor; `Sample Name` became `defines: sample`, `Sample Persistent Identifier`
  became `sample`, and a new `Session Identifier` was composed into all 16 TAPPs. 17 rows nested to
  `sample > sampling unit`, and `A > B x C` was specified in Rule 7.3 for `Counting Statistics Error`.
- **`analyte` settled** as the chemical species determined, never the isotope — eight contradicting
  descriptions corrected. Nine electron-beam setup fields moved from `analyte` to `channel` on Jia et
  al. 2022, and `WDS Spectrometer Channel` became `defines: channel per analyte`. Rule 7.3.1 was
  amended so the parent key is optional per row, interference monitors being channels with no analyte.
- **Four new validator checks**, two of which found real pre-existing problems: `Module_MCICPMS` at v3
  against a register claiming v4, and a regenerated xlsx byte-identical in size but not content.

Applied by `survey_colB_colI_20260812.py`, `build_colI_survey_findings_20260812.py`,
`triage_colB_uniformity_20260812.py`, `bump_and_stamp_20260812.py` and `recompose_all_20260812.py`.

`fix_paths_after_reorg_20260812.py` ran the same day and is why this folder is
`Superseded TAPPs/2026-08-12/` rather than the root-level `Superseded TAPPs (2026-08-12)/` that the
three earlier retirement folders were originally created as.""",

"2026-08-24": """Four independent conformance fixes, one per commit:

- **`Fix SEM Analytical Mode vocabulary and foreign columns`** — `fix_sem_analytical_mode_20260824.py`
- **`Fix Detection Limit typing across 13 TAPPs`** — `fix_detection_limit_20260824.py`, closing
  `amds-ldeo/tapp#1`
- **`Track A: header canon, um->µm, stale open-item cleanup`** — `trackA_conformance_20260824.py`
- **`Add Column E cross-TAPP uniformity check (Rule 7.8.10)`** — the check itself, with
  `triage_colE_uniformity_20260824.py` triaging what it found

The Detection Limit and SEM fixes are the two that bumped TAPP versions.""",

"2026-08-25": """`Module_ICPMS` v1, and the start of the Description/Purpose split.

- **`Module_ICPMS` v1 extracted** — 13 of 39 candidate fields admitted, **26 deferred by evidence**
  rather than assumed; the development log entry records the admission test. Composed into the 9
  ICP-MS TAPPs by `apply_module_icpms_20260825.py`.
- **Description/Purpose split, Step 1** — Column J (`Purpose`) added by
  `add_purpose_column_20260825.py`, and the Purpose sentences moved out of Column B descriptions by
  `apply_step1_purpose_20260825.py` and `apply_step1_icpms_slice_20260825.py`. Move only, no rewording.
- **Step 2 rewriting** began with `apply_step2_rewrite_20260825.py`; versions bumped by
  `bump_after_step2_20260825.py`.""",

"2026-08-26": """The Description/Purpose split carried through the ICP-MS family, plus a Column E
evidence pass — eleven commits, the busiest day in the record. The largest items:

- **`Split Description/Purpose: column J added, Step 1 applied to all modules`** and
  **`Step 2: rewrite the 48 flagged items; add Purpose overlay to modules`**
- **`Step 1 for the 26 ICP-MS TAPP-owned fields; convergence claim retracted`** — the retraction is
  the notable part: an earlier claim that the descriptions had converged did not survive checking
- **`Item 3: merge 26 ICP-MS descriptions; Module_ICPMS 13 -> 38 fields`** —
  `apply_icpms_merges_20260826.py`, taking up the 26 fields deferred on 2026-08-25
- **`Resolve 8 Column E divergences on evidence; register 1 as a name collision`** —
  `fix_colE_divergences_20260826.py`
- **`Map Area stays Numeric + unit — do not pin a unit with no evidence`** — a deliberate
  non-change, kept in the record so it is not reopened
- **`Sample Preparation Method -> Controlled list / Text`**, and
  **`Retire Internal Standard Approach from Solution; move to Module_LaserAblation`**""",

"2026-08-27": """`Module_CompositionQC`, the non-ICP-MS half of the Description/Purpose split, and the
completion of `Module_ICPMS` — 172 versions parked, the largest single day in this folder tree.

- **`Module_CompositionQC v1: the 12-TAPP quantitative-composition layer`** —
  `build_compositionqc_20260827.py`, bumped by `bump_for_compositionqc_20260827.py`
- **`Apply Step 1 of the Description/Purpose split to the 7 non-ICP-MS TAPPs`** and
  **`Step 2 for the 7 non-ICP-MS TAPPs: 91 flags acted on, 26 resolved as no change`** —
  the `step1_routes_*`, `apply_step1_*`, `step2_edits_*` and `apply_step2_*` scripts of that date
- **`Move Analysis Sequence into Module_ICPMS; module complete at 39 fields`** —
  `add_analysis_sequence_to_module_20260827.py`, closing the module opened on 2026-08-25
- **`Correct W5.3: the Dwell Time case is a scope leak, not a Column I defect`** — a correction to
  the working note, not to a TAPP
- Field-level items: `add_elnes_field_20260827.py`, `fix_eels_energy_resolution_20260827.py`,
  `rename_detector_type_20260827.py`, `rename_interference_20260827.py`,
  `universalise_spm_20260827.py`, `extend_laserablation_20260827.py`""",

"2026-09-01": """The `analyte` → `target species` rename, a Lab-XCT Phase 3 gap, and eight audit
findings adjudicated. Three dev-log entries cover the day.

- **`Target Selection Criteria` → `Sampling Unit Selection Criteria`, 13 TAPPs** —
  `bump_samplingunitselection_20260901.py`. The same log entry records the register being found
  drifting.
- **`analyte` → `target species` renamed library-wide** by
  `rename_analyte_to_target_species_20260901.py`, executing the vocabulary settled on 2026-08-12.
- **Lab-XCT: the VOI is not the sampling unit** — a shaped Phase 3 extraction gap closed by
  `patch_labxct_extraction_20260901.py`.
- **Eight audit findings adjudicated** — seven detector artefacts and one real re-key, and the
  session that produced the **unfalsifiability rule** later cited by the `acquisition pass` decision.
- `bump_for_module_20260901.py` was written this day, superseding the 2026-08-27 bump script, which
  had left every `tapp` path in `composed_tapps.json` naming the file it had just moved here. That is
  the mechanism behind the six stale registry entries found the same day, and why
  `register-stale-tapp-path` is now an ERROR.""",

"2026-09-08": """`acquisition pass` minted, the `Digestion Step` retype and its Phase 3 backfill, and
a reference-file reconciliation — 22 commits.

- **`Mint acquisition pass: 15 consumers, 9 ICP-MS TAPPs, 92 rows`** —
  `bump_acquisition_pass_20260908.py`. The key had been retired on 2026-08-11 for want of a consumer
  and was reinstated when a survey found 69 pass-structured cells across 4 TAPPs. **EPMA and SEM were
  deliberately deferred**, and `Record the named falsifier for the EPMA/SEM acquisition-pass deferral`
  is the commit that wrote down what would reverse that.
- **`Number of Digestion Steps` → `Digestion Step`, Integer → Text (free)** —
  `retype_digestion_step_20260908.py`, then `phase3_digestion_step_20260908.py` and
  `reextract_digestion_step_20260908.py` filled it from the sources, **falsifying 6 neighbouring
  cells** in the process.
- **`Reconcile the reference files with four days of passes; the schema spec was wrong`** — the spec
  handed to the schema developer had drifted materially. `Generate the schema spec's counts; refuse a
  stale block at save time` is the fix that made it structural: `tapp-save.sh` now refuses a save
  whose generated counts are stale.
- **`Backfill the development log: nine entries, 2026-08-28 to 2026-09-08`** — which is why the
  entries for this date exist at all.
- Three commits record **corrected reasoning** rather than changed files: `Resolve the SEM 7.4c snag
  — it dissolves, and it was my error`, `Settle the scalar-summary pattern: both KEEP, and the test I
  proposed was wrong`, and `4A rewritten: the definer ENUMERATES passes`.""",
}

VERIF = {
"2026-08-12": """A contemporaneous lint report survives for this date:
`../../Project Files/Reports/TAPP_Lint_Report_2026-08-12.csv`. It is the last of four such reports
(2026-08-07, -08, -11, -12); the practice of saving dated lint output stopped after this one, so no
later folder in this tree has an equivalent.

Four validator checks were **added** on this date, so the library was not being measured against a
fixed ruleset across the day. Two of the four found real pre-existing defects, both fixed the same
day.""",
"2026-08-24": """Not recorded. `Add Column E cross-TAPP uniformity check (Rule 7.8.10)` means the
validator itself changed on this date, so no single before/after result would characterise it.""",
"2026-08-25": """Not recorded.""",
"2026-08-26": """Not recorded. `Step 1 for the 26 ICP-MS TAPP-owned fields; convergence claim
retracted` shows a claim about this day's work being checked and withdrawn, which is the closest
thing in the record to a verification trail.""",
"2026-08-27": """Not recorded. `Correct W5.3: the Dwell Time case is a scope leak, not a Column I
defect` is a same-day correction to the day's own working note.""",
"2026-09-01": """Not recorded as a validator run, but this is the date `register-stale-tapp-path`
became an ERROR after six stale registry entries were found — a verification gap being closed rather
than a verification being reported.""",
"2026-09-08": """Not recorded as a validator run. Two structural gates were added on this date
instead: generated counts in the schema spec, and `tapp-save.sh` refusing a save that would commit
them stale.""",
}

TAIL = ("\n---\n\nNo per-date `validate_tapp.py` output is asserted where none was recorded — see "
        "the Verification\nsection. The library validates 0 ERROR / 0 WARN as of %s, which says "
        "nothing about its\nstate on the date this folder was parked.\n" % STAMP)


def main(apply=False):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    n = 0
    for date in sorted(WHY):
        p = os.path.join(root, "Superseded TAPPs", date, "README.md")
        if not os.path.exists(p):
            print("  !! no README at %s — run superseded_readme.py --all first" % date); return 1
        s = io.open(p, encoding="utf-8").read()
        if "TODO" not in s:
            print("  skip %s — already filled" % date); continue

        # Deterministic rather than pattern-matched per block: drop the skeleton notice,
        # then truncate at "## Why" and rebuild the two prose sections from scratch.
        lines, out, skipping = s.split("\n"), [], False
        for ln in lines:
            if ln.startswith("> **TODO — skeleton."):
                skipping = True
                out.append(RECON.rstrip("\n"))
                continue
            if skipping:
                if ln.startswith(">"):
                    continue
                skipping = False
            out.append(ln)
        s = "\n".join(out)
        head = s.split("## Why", 1)[0].rstrip("\n")
        s = (head + "\n\n## Why\n\n" + WHY[date].strip()
             + "\n\n## Verification\n\n" + VERIF[date].strip() + "\n" + TAIL)
        if "TODO" in s:
            print("  !! %s still has TODO after fill — pattern mismatch" % date); return 1
        if apply:
            io.open(p, "w", encoding="utf-8").write(s)
        print("  %s %s (%d chars)" % ("filled" if apply else "would fill", date, len(s)))
        n += 1
    print("\n  %d folder(s)%s" % (n, "" if apply else "  (dry run — pass --apply)"))
    return 0


sys.exit(main("--apply" in sys.argv))
