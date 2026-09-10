---
name: project-tapp-vim3-terminology
description: "TAPP core vocabulary migrated from in-house definitions to BIPM VIM3 (JCGM 200:2012) definitions — Protocol became Procedure, old Procedure became Measurement (Analysis kept as working label). Executed 2026-07-24."
metadata: 
  node_type: memory
  type: project
---

The user is realigning TAPP's four core terms (Technique, Method, Protocol, Procedure) with VIM3 (International Vocabulary of Metrology, 3rd ed., BIPM/JCGM 200:2012), on advice from geoscience experts consulted on techniques and analysis. Source file: `Measurement Term Definitions VIM3.xlsx` in the TAPPs project root.

**Why:** VIM3 gives the definitions external authority and should make TAPP easier to introduce to the community, versus bespoke in-house definitions.

**The mapping (confirmed by the user):**
- **Technique** — term kept, definition swapped to VIM3 "measurement principle" (§2.4). No cascading changes.
- **Method** — term kept, definition text refined to VIM3 "measurement method" (§2.5) wording. No field-level renames follow from this.
- **Protocol → Procedure** — the old "Protocol" (registerable, DOI-bearing, protocol-level/Column-C object) is renamed to "Procedure," VIM3's "measurement procedure" (§2.6). This is the term the user explicitly said should no longer appear in TAPP work.
- **Old Procedure → Measurement** — the old "Procedure" (analysis-level execution, what actually happened in a session) is renamed to "Measurement," VIM3 §2.1 — but **only as the formal/definitional anchor**. Per the user's explicit choice (asked via AskUserQuestion 2026-07-24), the TAPP-facing working label stays **"Analysis"** — Column D header remains "Analysis-Level Tier," unchanged. "Measurement" appears only in the vocabulary definitions table, mirroring how "Technique" already stays the working label for "measurement principle." This choice avoids a same-document collision with Group 4's existing (unrelated) name "Measurement Information."
- **TAPP acronym**: "Technique-Aligned Protocol Profiles" → **"Technique-Aligned Procedure Profiles."** Acronym unchanged.

**Key mechanical hazard flagged:** Protocol→Procedure and old-Procedure→Measurement are a *rotation*, not two independent renames — a naive two-pass find/replace would double-convert. Neutralized by the "keep Analysis" decision above, since "Procedure" is only ever being occupied, never vacated.

**Status: executed 2026-07-24.** All skill reference docs (`conventions.md`, `workflow.md`, `field-review.md`, `precedents.md`, `lit_assessment.md`, both `SKILL.md` copies, `Template TAPP Group 1.csv`, `tapp_to_xlsx.py`) now use the new terminology (Procedure = registerable object, Column C = "Procedure-Level Tier", Group 1 = "Procedure Identification", Column D unchanged = "Analysis-Level Tier"). See [[reference_skill_paths]] for where these files live. Both `SKILL.md` copies were edited directly (installation copy confirmed writable) — but note they were independently found to have PRE-EXISTING content drift unrelated to this migration (installation copy missing the sentinel-column convention and a couple other rules); flagged as a separate follow-up task. **Resolved later the same day** — see [[project_tapp_skill_sync]] for the full divergence list (including a real D=N/A rule change beyond what was initially flagged) and the reconciliation.

All 12 current-version TAPP CSVs were migrated to new integer-bumped versions and their xlsx regenerated: EPMA v7→v8, LA-ICP-MS v12→v13, LA-Q/SF-ICP-MS v3→v4, SEM v4→v5, SEM_Composition v4→v5, SEM_Imaging v4→v5, SEM_FIBSEM v4→v5, Solution MC-ICP-MS v2→v3, Solution Q-ICP-MS v5→v6, Solution SF-ICP-MS v5→v6, TEM v7→v8, Lab-XCT v8→v9. Prior versions (v1…v(n−1) for each) were left completely untouched on disk, per the scope boundary agreed in planning. Literature-assessment columns (verbatim/paraphrased paper extractions) were also left untouched by design, everywhere.

**CORRECTION (2026-07-29, verified in a later session):** "LA-ICP-MS v12→v13" and "LA-Q/SF-ICP-MS v3→v4" above are NOT two separate TAPPs — they are the same lineage under two folder names, and the "LA-ICP-MS" branch is stale/frozen post-v12 (this VIM3 pass's own v12→v13 bump was the last thing that branch ever received; no organic development happened there after the rename to "LA-Q/SF-ICP-MS"). So the true count is 11 distinct TAPPs, not 12, and the "current" file for that technique is `LA-Q:SF-ICPMS_TAPP_v4.1.csv`, not `LA-ICPMS_TAPP_v13.csv`. Full detail in [[reference_la_icpms_lineage]]. This also means the VIM3 terminology pass itself only reached the LA-ICP-MS/LA-Q-SF-ICP-MS technique via the (already-then-stale) LA-ICP-MS branch's v13 AND separately via v4→v4.1's own later description-only patch (2026-07-28) — worth double-checking VIM3 terminology actually landed correctly in the file that matters (v4.1) if this ever becomes relevant again.

**Pre-migration snapshots** of every hand-edited reference/living doc (the ones without their own version numbers) are archived at `Pre-VIM3 Reference Archive (2026-07-24)/` in the TAPPs project root, each with an explicit "archived/outdated" banner — done at the user's request before any edits were made, so old terminology stays fully recoverable.

`TAPP_Development_Log.md` was handled specially: only "Part I — Cross-TAPP Conventions" (the living reference section) was updated to match `conventions.md`; every dated per-TAPP entry in Parts II–IX was left byte-for-byte untouched (historical record, not rewritten). A banner was added at the top of the file explaining the change, stating that `conventions.md` wins on any conflict with old entries, and recommending searching the log for a topic rather than reading it wholesale — the same "search, don't read end-to-end" instruction was also added to `workflow.md`'s "Before Consulting the Dev Log" section, to reduce the risk of old terminology leaking into future AI-drafted TAPP content. A new dated entry was appended recording the full migration.

**Known live follow-up (not yet acted on):** Solution Q-ICP-MS and Solution SF-ICP-MS both have a pending Open Question in the dev log (Chromatographic Separation Applied — split into Y/N + "Procedure"?) proposing a candidate field literally named "Procedure." Whoever resumes Phase 4 on either of those TAPPs should name it something else (e.g., "Chromatographic Separation Method") to avoid colliding with the new formal term — deliberately left as-is in the dev log itself (historical entry) but called out in the new 2026-07-24 entry.

Full assessment + implementation plan was written up as an artifact: "Aligning TAPP Vocabulary with VIM3" (published 2026-07-24, before execution).
