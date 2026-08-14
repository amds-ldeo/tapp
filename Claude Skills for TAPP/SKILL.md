---
name: tapp
description: Use this skill whenever developing a Technique-Aligned Procedure Profile (TAPP) for any analytical technique used in geochemistry, cosmochemistry, or related earth and planetary sciences. Triggers include: creating a new TAPP from scratch for any technique (EPMA, SIMS, ICP-MS solution, noble gas MS, geochronology, Raman spectroscopy, X-ray diffraction, imagery analysis, physical property measurement, etc.), extending or revising an existing TAPP, assessing a TAPP against literature, designing the tier system or mode-applicability flags for a TAPP, or discussing the procedure-vs-analysis distinction for any metadata field. Also use when the user asks about the metadata infrastructure for EarthChem, Astromat, or SESAR, or mentions "TAPP", "procedure registration", or "method metadata". Always use this skill before generating any TAPP content — do not rely on memory of prior TAPP decisions.
---

# TAPP Development Skill

A TAPP (Technique-Aligned Procedure Profile) is a structured metadata framework that documents an analytical technique at two levels: the **procedure** (the standing set of guidelines that specifies how the technique is applied, registerable with a DOI) and the **analysis** (the specific execution of that procedure — what actually happened in a given session, on a given sample, on a given date). TAPPs are the primary deliverable for the Astromat/EarthChem method metadata infrastructure.

See `references/conventions.md` for the precise vocabulary: Technique / Method / Procedure / Analysis.

## Quick Reference

| What you need | Where to look |
|---|---|
| Full workflow with phase details | `references/workflow.md` |
| Field-by-field review checklist | `references/field-review.md` |
| Controlled vocabulary and conventions | `references/conventions.md` |
| Precedent decisions from LA-ICP-MS TAPP | `references/precedents.md` |
| Shared field blocks (modules) | `references/conventions.md` Rule 6, and `modules/` |

| Script | What it does |
|---|---|
| `scripts/validate_tapp.py` | lints every TAPP against the structural invariants and cross-TAPP rules; run before any version bump |
| `scripts/compose_tapp.py` | builds a TAPP from a source file plus one or more modules |
| `scripts/tapp_to_xlsx.py` | exports a TAPP CSV to a formatted xlsx |
| `scripts/audit_keys_vs_literature.py` | validates every Column I key against the literature assessment extractions; run during Phase 3 (Rule 7.12) |
| `Project Files/Scripts/sync_current_tapps.py` | refreshes `Current TAPPs/`, the shareable flat mirror of the latest CSV + xlsx for every TAPP (Rule 12); run after any version bump |

**Always read `references/conventions.md` before writing any TAPP content.** It defines the tier vocabulary, group structure, mode flags, naming conventions, and the CSV/xlsx file management workflow that must be consistent across all TAPPs.

For a new TAPP, read `references/workflow.md` first to orient, then proceed phase by phase.

---

## Overview: The Five-Phase Workflow

```
Phase 0 — Technique Scoping        (human-led, AI-assisted)
    ↓
Phase 1 — Preliminary TAPP         (AI-led)
    ↓
Phase 2 — Structured Field Review  (human-in-the-loop)
    ↓
Phase 3 — Literature Assessment    (AI-led, human-validated)
    ↓
Phase 4 — Post-Assessment Revision (human-in-the-loop)
    ↓
  Final TAPP (vN)
```

Each phase has defined inputs, outputs, and decision criteria. Phases 2 and 4 are iterative — they may loop back. The loop between Phase 3 and Phase 2 is expected and healthy: literature assessment frequently surfaces fields that need revision.

---

## Starting a New TAPP

Before generating any content, confirm the following with the user:

1. **Technique name and scope**: What is the technique, and what related techniques does it exclude? (e.g., "LA-ICP-MS" excludes solution ICP-MS and MC-ICP-MS, which get separate TAPPs)
2. **Sub-modes**: Are there distinct analytical modes that require separate mode-applicability flag columns? How many modes, and what are they called? Or should variants be separate TAPPs?
3. **Inputs for Phase 1**: Two types are useful and may be provided together:
   - *Seed papers*: 2–4 methodologically authoritative references (method papers, best-practice papers, data reduction papers)
   - *Existing procedure templates*: community procedure templates or checklists from instrument manufacturers, professional societies, or other TAPPs — these drive structural decisions and suggest field vocabulary
4. **Reference TAPP**: Which existing TAPP should be used as the structural template? Default to LA-ICP-MS unless the technique is substantially different.

Do not proceed to Phase 1 until these items are confirmed. Premature field generation before the mode/scope question is resolved causes expensive retroactive revision.

---

## Deliverable Format and File Management

TAPPs are maintained as **CSV files** during development and revision, and exported as **formatted xlsx files** for sharing with stakeholders and community review.

### CSV (development format)
- One CSV per TAPP, named `[Technique]_TAPP_v[N].csv`
- All editing, patching, and version control is done on the CSV
- Human-readable in any text editor; diffable between versions; no library overhead
- No color formatting — tier values are represented by their text labels (Basic, Advanced, Read-Only, Editable, N/A for procedure level; Read-Only, Editable, Basic, Advanced for analysis level)

### xlsx (shareable format)
- Generated from the CSV using a Python export script (`scripts/tapp_to_xlsx.py`)
- Color coding applied automatically during export per the tier vocabulary in `references/conventions.md`
- Never edit the xlsx directly — it is a generated artifact, not the source of truth
- Named `[Technique]_TAPP_v[N].xlsx`

### `Current TAPPs/` — the shareable mirror (Rule 12)
A flat folder at the library root holding the **latest CSV + xlsx for every TAPP**, and nothing else.
It exists so the whole folder can be handed to another developer as a unit. **Every version bump must
refresh it** — `bump_and_stamp_20260812.py` does so automatically, and `validate_tapp.py` reports a
stale mirror at WARN (`rule12-*`). It is a copy, never an editing target: edit the TAPP in its
technique folder and re-sync. The folder is excluded from `discover()` by name; Rule 12.1 explains why
that exclusion is load-bearing rather than cosmetic.

### Targeted patch scripts
For small changes to an existing TAPP (updating a description, changing a tier assignment, adding a field), write a targeted Python patch script rather than regenerating from scratch. A patch script modifies specific rows/columns by coordinate and saves the updated CSV. This is faster and makes the change set explicit and auditable.

Always dry-run a patch first, verify that only the intended columns changed, then re-run `scripts/validate_tapp.py` and regenerate the affected xlsx.

### Modules (composed field blocks)
Fields shared by more than one TAPP live in `modules/` as a CSV plus a JSON manifest, and are **composed** into consuming TAPPs by `scripts/compose_tapp.py` rather than copied into each one. The module owns field names, descriptions, tiers and data types; the consuming TAPP owns examples, comments, dates and mode flags.

**See Rule 6 in `references/conventions.md` before creating or changing a module.** It defines the admission test — a field must both recur across TAPPs *and* not already exist elsewhere in the library — along with column ownership, placement, conditional block selection, and the verification steps a new module must pass.

A composed TAPP is a generated artifact. Never edit one directly; edit the module or the source and recompose.

### Column structure

| Col | Content | Notes |
|---|---|---|
| A | Metadata Item | Field name |
| B | Description | Full description |
| C | Procedure-Level Tier | Basic / Advanced / N/A |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced |
| E | Data Type | Controlled vocabulary — see conventions |
| F | Example / Allowed Content | Examples or controlled list values |
| G | Comments | Short field-level qualifiers that are neither mode nor cardinality — instrument variant, signal/detector, conditional notes |
| H | Last Update | YYYY-MM-DD |
| I | Keyed By | What the field's value repeats over — see Rule 7. Never blank; `(none)` for a scalar |
| J … J+n | Mode flag columns | One column per mode defined in Phase 0; labels set in Phase 0 |
| J+n+1 | Sentinel column | Header must be exactly `Literature Assessment`; all data rows empty; marks the mode/lit boundary |
| J+n+2 … | Literature assessment columns | One column per procedure extracted from papers; added in Phase 3 |

The number of mode flag columns is determined in Phase 0 and varies by technique. A sentinel column with the header `Literature Assessment` (all data rows empty) follows the last mode flag column and marks the boundary. Literature assessment columns begin immediately after the sentinel. There is no fixed column letter for either boundary — both depend on the number of modes defined.

---

## Key Structural Invariants

These must hold in every TAPP. Violations indicate a design error.

- **Every field has exactly one Procedure-Level Tier value and one Analysis-Level Tier value.** Never leave these blank for content rows.
- **Group 1 must end with the four standard coupling fields** (Coupled Technique(s), Coupling Description, Coupled Procedure DOI, Coupled Dataset or Publication Reference), in that order, immediately after Procedure Reference(s). See `references/conventions.md` for default tier assignments and rationale.
- **D=N/A is not a valid analysis-level tier.** Every field must carry a meaningful analysis-level assignment: Read-Only, Editable, Basic, or Advanced. Fields that are only relevant at procedure level are assigned D=Read-Only (the value is imported from the procedure and cannot be changed at analysis time).
- **Read-Only fields at analysis level must correspond to Basic or Advanced fields at procedure level.** A field cannot be Read-Only if the procedure never specifies it (C=N/A).
- **Editable fields at analysis level must also be Basic or Advanced at procedure level.** Editable means "imported from procedure, adjustable within procedure-defined bounds."
- **Basic at analysis level (D=Basic) means mandatory user input at analysis time.** It is appropriate when the value cannot be known until the analysis is performed.
- **Mode flags are Y or N only.** N/A is not valid in mode flag columns — use N for "not applicable to this mode."
- **The analysis record is the session, not one sample** (Rule 13, added 2026-08-12). A session may cover many samples, each with its own identity and possibly its own preparation. `Sample Name` (`defines: sample`), `Sample Persistent Identifier` (`sample`) and `Session Identifier` (`(none)`) are mandatory in every TAPP. Ask of every field whether it is per **session**, per **sample**, or per **sampling unit within a sample** — "analysis-level" is two levels, and Column I is what separates them.

---

## Common Mistakes to Avoid

These errors are most likely to appear in a preliminary TAPP:

1. **Confusing procedure target with measured value when a split is warranted.** When a procedure specifies an acceptance *criterion* (threshold, pass/fail gate) and the analysis records an *actual measured result* against that criterion, split into two fields — one procedure-level (the criterion), one analysis-level (the measured value). See `references/precedents.md` for the Oxide Production example. Do not confuse this with session-tunable parameters (flow rates, fluence, spot size), where a single field with D=Editable is correct: the procedure registers the target value and the analyst may adjust within allowed bounds.

2. **Setting the signal integration window as procedure-level.** The integration window is selected during data reduction by applying the Signal Integration Interval Method to the actual signal — it is analysis-level. The *method* for selecting the window is procedure-level; the resulting *window or time* is analysis-level.

3. **Assigning Read-Only to a field that is routinely session-tuned.** Parameters adjusted during daily tuning (background settings, flow rates) should be Editable, not Read-Only.

4. **Using "Default", "Target", "Achieved", or "Typical" in field names.** Field names should be level-neutral; the tier columns (C and D) encode whether a value is a procedure target or an analysis-level measurement. Use the description (Column B) to clarify that the procedure registers a target or typical value. Exceptions: "Target Material" and "Target Feature(s)" are retained because "Target" here means the material/feature *type* the procedure is designed to analyze, not a value that is later achieved — these have no analysis-level counterpart and no ambiguity.

5. **Recording how many values a field holds in the Comments column.** Cardinality is declared in Column I (`Keyed By`) under Rule 7, never in Comments. Ask what the field's value repeats over and declare that key: `(none)`, `sample`, `sampling unit`, `reported property`, `channel`, `analyte`, or one of the secondary keys. Do not reach for `analyte` by default — it applies to fewer than half the fields that once carried the `Analyte-Specific` label, and it is absent entirely from techniques with no chemical species (Lab-XCT, Raman, fission track). The Comments column carries only qualifiers that are neither mode nor cardinality; mode applicability belongs in the mode flag columns.

   **Nor in the description.** Cardinality stated in Column B is the same mistake one column over, and harder to spot because it reads as ordinary prose. A field that *enumerates* a domain can also *repeat over* one — `Monitored Isotopes` is `defines: channel per analyte` (Rule 7.3.1) — so when a field declares `defines: X`, ask whether it also repeats over something before moving on. Where a description names a key, either Column I should carry it or the sentence should go.

6. **Using "Method" when referring to the registered procedure object.** Use "Procedure" for the registerable object. "Method" is reserved for assessment methods, calculation methods, and sub-procedures. See `references/conventions.md` for the full vocabulary.

---

## Reading Order for a New TAPP

1. Read `references/conventions.md` — mandatory before writing anything
2. Read `references/workflow.md` — full phase-by-phase guidance
3. As needed during Phase 2: read `references/field-review.md`
4. As needed for precedent: read `references/precedents.md`
