---
name: TAPP Skill Reference File Locations
description: Where the TAPP skill's files live — the project folder is the source of truth, the Claude install path is a copy that is now fully populated
metadata:
  type: reference
---
The TAPP skill exists in two places. **The project folder is the source of truth; always read and edit there.**

- Authoritative: `Claude Skills for TAPP/` — `SKILL.md`, `references/` (conventions, workflow, field-review, lit_assessment, precedents), `scripts/` (validate_tapp, compose_tapp, tapp_to_xlsx, audit_keys_vs_literature), `modules/`, `analysis/`, `tapp_files/`.
- Install copy the Skill tool loads from: see [[project_tapp_skill_sync]] for the path and the sync procedure.

**Corrected 2026-09-10.** This note previously said the references and scripts were "NOT present in the Claude app support skill directory (only SKILL.md is there)". That was true when written and is no longer: a verified sweep on 2026-09-10 found **all 83 files present** in the install path, and after syncing two drifted files, byte-identical. Do not repeat the old claim.

Note that many `Project Files/Scripts/*.py` helpers (`sync_current_tapps.py`, `check_field_ownership.py`, `superseded_readme.py`, the dated patch scripts) live in the project only and are *not* part of the skill directory at all — they are invoked by path, not through the skill.
