---
name: tapp-skill-installation-sync
description: "How to sync the TAPP skill install path from the project copy — no auto-sync; the install is fully populated as of 2026-09-10; cmp -s per file, copy only what differs, re-verify"
metadata: 
  node_type: memory
  type: project
---

The TAPP skill has two SKILL.md copies: the authoritative one at `Claude Skills for TAPP/SKILL.md` in the project folder, and an installation-path copy the Skill tool actually loads from (see [[reference_skill_paths]] for the full install path and the related missing-references-files issue). These two copies do NOT auto-sync — editing the project copy alone leaves the installation copy stale until someone manually re-copies it.

**Superseded 2026-09-10 — the install is now fully populated.** This note used to say `tapp` "has only ever had the single SKILL.md file there — its references/scripts were never installed at all". That is no longer true. A file-by-file sweep on 2026-09-10 found **all 83 project files present** in the install path, none missing and none extra, so some earlier pass copied the whole tree. Only **2 of 83 had drifted** — `SKILL.md` and `analysis/Audit_ColI_vs_LitAssess.csv`, both edited earlier the same session — and after copying those two, all 83 verified byte-identical. There is still no evidence of any automatic re-sync mechanism; the drift was from that session's own edits.

**The procedure that works** (and is cheap enough to run every time): walk the project tree, `cmp -s` each file against its install counterpart, copy only the ones that differ, then re-walk and confirm identical / 0 differs / 0 missing. Also check for files present in the install but absent from the project — there were none, but an orphan there would be served to the Skill tool with nothing to compare it against.

**What happened:** during the VIM3 terminology migration, both SKILL.md copies were edited directly and confirmed to carry the new terminology — but a diff done in the same pass found the installation copy had older, pre-existing drift unrelated to VIM3, flagged in [[project_tapp_vim3_terminology]] as an unresolved follow-up. That follow-up was completed later the same day: full-file diff, then the installation copy was overwritten with the project copy's content, verified byte-identical afterward.

**Actual divergences found (the original flag undersold/misattributed some of these — corrected here):**
- Sentinel column convention (header exactly `Literature Assessment`, empty data rows, marks the mode-flag/lit-assessment boundary) — present in the project copy's column-structure table and prose, entirely absent from the installation copy.
- Group 1 must end with the four standard coupling fields, in order, right after Procedure Reference(s) — present only in the project copy's Key Structural Invariants.
- **D=N/A validity rule — a real rule change, not just wording, and not in the original flag list.** The project copy states flatly "D=N/A is not a valid analysis-level tier" (every field must carry Read-Only/Editable/Basic/Advanced at analysis level). The installation copy instead had an older, looser rule — "C=N/A and D=N/A cannot both be set for the same field" — which permits D=N/A whenever C is not also N/A. Anyone relying on the stale installation copy would have validated fields against the wrong rule.
- Common Mistake #1 (procedure-target-vs-measured-value split): the project copy adds an exception carve-out for session-tunable parameters (flow rate, fluence, spot size) that correctly stay a single D=Editable field — the installation copy lacked this nuance and could prompt an unwarranted split.
- Common Mistake #4 — **the original flag had the attribution backwards.** The project copy's actual #4 is "Using 'Default'/'Target'/'Achieved'/'Typical' in field names" (with Target Material / Target Feature(s) carved out as exceptions). The installation copy's stale #4 was the older, narrower "Omitting the split between Target Analyte and Analyte" — a specific case the broader naming rule later superseded.
- Minor wording-only diffs: the CSV tier-label parenthetical (~line 70) and one clarifying parenthetical "(C=N/A)" added to the Read-Only invariant bullet.

**How to apply:** there is no automatic sync — anything edited in the project copy must be re-copied to the installation, or the Skill tool silently serves stale content.

**Scope is the whole skill directory, not just SKILL.md.** The 2026-08-11 Rule 7 work changed `references/conventions.md`, `references/precedents.md`, `references/field-review.md`, `references/workflow.md`, all three `scripts/*.py`, and all sixteen `modules/*` files. Syncing SKILL.md alone would have left the validator, the composer and every module definition stale.

Installation path (contains session-specific UUIDs; may change if the app resets local-agent-mode-sessions state):
`~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/d4f0b039-8813-4a14-99a0-266e4a807c1c/097232b4-a4f8-49f0-b0a0-82a888967776/skills/tapp/`

Verify rather than assume — `cmp -s` each project file against its installation counterpart. A one-file drift is easy to create and invisible until a rule fires wrongly. See [[project_tapp_keyed_by_rule7]].
