---
name: reference-la-icpms-lineage
description: The LA-ICP-MS lineage — stale branch archived 2026-08-10, then LA-Q/SF-ICP-MS split into separate LA-Q-ICP-MS and LA-SF-ICP-MS TAPPs on 2026-08-11
metadata: 
  node_type: memory
  type: reference
---

`LA-ICP-MS/` and `LA-Q_SF-ICP-MS/` were **one continuous development lineage**, not two TAPPs. The split was an artifact of renaming the technique mid-development. The branches synced at v11/v12 (100% identical field sets in both rounds); only `LA-Q_SF-ICP-MS` was developed afterwards.

**Two archival events, both resolved:**

1. **2026-08-10** — the stale branch (`LA-ICPMS_TAPP_v1..v13`, 31 files) was archived to `Superseded TAPPs (2026-08-10)/LA-ICP-MS (stale branch)/`. Verified first: 95 fields, 0 uncovered against LA-Q/SF v5. Lint 477 → 395.

2. **2026-08-11 — LA-Q/SF was SPLIT INTO TWO TAPPs.** `LA-Q_SF-ICP-MS/` no longer exists as a live folder; it is archived at `Superseded TAPPs (2026-08-11)/LA-Q_SF-ICP-MS (split into Q and SF)/` with a README holding the field-level split record. **Current live files:**
   - `LA-Q-ICP-MS/` and `LA-SF-ICP-MS/`, each holding a base TAPP and a U-Pb variant. The split created
     v7; both families were at **v9** by the end of 2026-08-11 after the Rule 7 retrofit and two rounds of
     tier reconciliation. Always check with `ls` — versions moved several times in one day.

   Rationale: the solution family already had separate Q and SF TAPPs, so the combined LA TAPP was the outlier. Naming uses `ICP-MS` not `ICPMS`, matching the solution TAPPs; versioning continued the v6 lineage at v7 rather than restarting. Planning-table numbering is now 7 = LA-Q, 7a = LA-SF, 7b = LA-MC, 7c = LA-ToF, 7d = LA-TQ. **The library is now 16 TAPPs.**

Always verify the latest version with `ls`/`find` rather than trusting any memory snapshot, including this one.

**`LA-ICP-MS/` still exists and must not be deleted or renamed.** It holds only `Validation Papers/` and loose method PDFs, plus a README. `paper_registry.csv` records the literal path `LA-ICP-MS/Validation Papers` for **10 papers**, and those are Phase 3 sources for the live LA-Q and LA-SF TAPPs. SF-specific seed papers moved to `LA-SF-ICP-MS/Seed Papers/` during the split.

**Three literature assessment columns survive only in the archived `v13`** (89 filled cells each), covering instruments out of scope for Q/SF: planning-table rows 7c (Chernonozhkin 2024, ToF), 7d (Masuda 2024, TQ) and **7b (Zhang et al. 2022 At. Spectrosc. 43, LA-MC-ICP-MS)** — note these row numbers shifted in the 2026-08-11 renumber. See [[project_tapp_module_architecture]] and [[project_tapp_keyed_by_rule7]].

**How to apply:** "LA-ICP-MS" or "LA-Q/SF-ICP-MS" no longer resolves to a single live TAPP — ask which instrument, or check both `LA-Q-ICP-MS/` and `LA-SF-ICP-MS/`. Treat `LA-ICP-MS/` as a papers folder only.
