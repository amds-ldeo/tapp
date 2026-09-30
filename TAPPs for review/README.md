# TAPPs for review

The reviewer-facing workbooks: the TAPPs rendered for domain experts to read and comment on. Each
workbook has a preamble sheet explaining the tiers and how to review, one row per field in plain
language with its structure in the procedure and the session record, drop-down review columns, and
a traceability sheet mapping each row back to the TAPP's `Keyed By`.

**Only the latest version is kept.** The workbooks are generated, never edited by hand. The generator
writes here and deletes any workbook of another version, so every file in this folder matches the
live TAPP in `Current TAPPs/`. Earlier versions are in git history.

| Workbooks | Generator |
|---|---|
| EPMA — one combined workbook and one per analytical mode (EDS Point Analysis, EDS Mapping, WDS Point Analysis, WDS Mapping) | `Project Files/Reports/make_review_workbook.py` — set `VERSION` and run it after an EPMA bump |

A reviewer's completed copy should be saved under a new name or kept outside this folder, since
regenerating overwrites these files.
