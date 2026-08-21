> **⚠️ ARCHIVED — PRE-VIM3 SNAPSHOT (2026-07-24)**
> This file reflects TAPP terminology *before* alignment with BIPM VIM3 (JCGM 200:2012): "Protocol" = the
> registerable, DOI-bearing object; "Procedure"/"Analysis" = the analysis-level execution. Kept for
> historical record only — **do not use for current TAPP work.** Current version lives at the original
> path in the TAPPs project (same filename, without this suffix).
>
> See the "Aligning TAPP Vocabulary with VIM3" migration plan for the full rationale.

---

---
name: tapp
description: Use this skill whenever developing a Technique-Aligned Protocol Profile (TAPP) for any analytical technique used in geochemistry, cosmochemistry, or related earth and planetary sciences. Triggers include: creating a new TAPP from scratch for any technique (EPMA, SIMS, ICP-MS solution, noble gas MS, geochronology, Raman spectroscopy, X-ray diffraction, imagery analysis, physical property measurement, etc.), extending or revising an existing TAPP, assessing a TAPP against literature, designing the tier system or mode-applicability flags for a TAPP, or discussing the protocol-vs-analysis distinction for any metadata field. Also use when the user asks about the metadata infrastructure for EarthChem, Astromat, or SESAR, or mentions "TAPP", "protocol registration", or "method metadata". Always use this skill before generating any TAPP content — do not rely on memory of prior TAPP decisions.
---

# TAPP Development Skill

A TAPP (Technique-Aligned Protocol Profile) is a structured metadata framework that documents an analytical technique at two levels: the **protocol** (the standing set of guidelines that specifies how the technique is applied, registerable with a DOI) and the **analysis** (the specific execution of that protocol — what actually happened in a given session, on a given sample, on a given date). TAPPs are the primary deliverable for the Astromat/EarthChem method metadata infrastructure.

See `references/conventions.md` for the precise vocabulary: Technique / Method / Protocol / Procedure / Analysis.

## Quick Reference

| What you need | Where to look |
|---|---|
| Full workflow with phase details | `references/workflow.md` |
| Field-by-field review checklist | `references/field-review.md` |
| Controlled vocabulary and conventions | `references/conventions.md` |
| Precedent decisions from LA-ICP-MS TAPP | `references/precedents.md` |

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
   - *Existing protocol templates*: community protocol templates or checklists from instrument manufacturers, professional societies, or other TAPPs — these drive structural decisions and suggest field vocabulary
4. **Reference TAPP**: Which existing TAPP should be used as the structural template? Default to LA-ICP-MS unless the technique is substantially different.

Do not proceed to Phase 1 until these items are confirmed. Premature field generation before the mode/scope question is resolved causes expensive retroactive revision.

---

## Deliverable Format and File Management

TAPPs are maintained as **CSV files** during development and revision, and exported as **formatted xlsx files** for sharing with stakeholders and community review.

### CSV (development format)
- One CSV per TAPP, named `[Technique]_TAPP_v[N].csv`
- All editing, patching, and version control is done on the CSV
- Human-readable in any text editor; diffable between versions; no library overhead
- No color formatting — tier values are represented by their text labels (Basic, Advanced, Read-Only, Editable, N/A for protocol level; Read-Only, Editable, Basic, Advanced for analysis level)

### xlsx (shareable format)
- Generated from the CSV using a Python export script (`scripts/tapp_to_xlsx.py`)
- Color coding applied automatically during export per the tier vocabulary in `references/conventions.md`
- Never edit the xlsx directly — it is a generated artifact, not the source of truth
- Named `[Technique]_TAPP_v[N].xlsx`

### Targeted patch scripts
For small changes to an existing TAPP (updating a description, changing a tier assignment, adding a field), write a targeted Python patch script rather than regenerating from scratch. A patch script modifies specific rows/columns by coordinate and saves the updated CSV. This is faster and makes the change set explicit and auditable.

### Column structure

| Col | Content | Notes |
|---|---|---|
| A | Metadata Item | Field name |
| B | Description | Full description |
| C | Protocol-Level Tier | Basic / Advanced / N/A |
| D | Analysis-Level Tier | Read-Only / Editable / Basic / Advanced |
| E | Data Type | Controlled vocabulary — see conventions |
| F | Example / Allowed Content | Examples or controlled list values |
| G | Last update date | YYYY-MM-DD |
| H … H+n | Mode flag columns | One column per mode defined in Phase 0; labels set in Phase 0 |
| H+n+1 | Sentinel column | Header must be exactly `Literature Assessment`; all data rows empty; marks the mode/lit boundary |
| H+n+2 … | Literature assessment columns | One column per protocol extracted from papers; added in Phase 3 |

The number of mode flag columns is determined in Phase 0 and varies by technique. A sentinel column with the header `Literature Assessment` (all data rows empty) follows the last mode flag column and marks the boundary. Literature assessment columns begin immediately after the sentinel. There is no fixed column letter for either boundary — both depend on the number of modes defined.

---

## Key Structural Invariants

These must hold in every TAPP. Violations indicate a design error.

- **Every field has exactly one Protocol-Level Tier value and one Analysis-Level Tier value.** Never leave these blank for content rows.
- **Group 1 must end with the four standard coupling fields** (Coupled Technique(s), Coupling Description, Coupled Protocol DOI, Coupled Dataset or Publication Reference), in that order, immediately after Protocol Reference(s). See `references/conventions.md` for default tier assignments and rationale.
- **D=N/A is not a valid analysis-level tier.** Every field must carry a meaningful analysis-level assignment: Read-Only, Editable, Basic, or Advanced. Fields that are only relevant at protocol level are assigned D=Read-Only (the value is imported from the protocol and cannot be changed at analysis time).
- **Read-Only fields at analysis level must correspond to Basic or Advanced fields at protocol level.** A field cannot be Read-Only if the protocol never specifies it (C=N/A).
- **Editable fields at analysis level must also be Basic or Advanced at protocol level.** Editable means "imported from protocol, adjustable within protocol-defined bounds."
- **Basic at analysis level (D=Basic) means mandatory user input at analysis time.** It is appropriate when the value cannot be known until the analysis is performed.
- **Mode flags are Y or N only.** N/A is not valid in mode flag columns — use N for "not applicable to this mode."

---

## Common Mistakes to Avoid

These errors are most likely to appear in a preliminary TAPP:

1. **Confusing protocol target with measured value when a split is warranted.** When a protocol specifies an acceptance *criterion* (threshold, pass/fail gate) and the analysis records an *actual measured result* against that criterion, split into two fields — one protocol-level (the criterion), one analysis-level (the measured value). See `references/precedents.md` for the Oxide Production example. Do not confuse this with session-tunable parameters (flow rates, fluence, spot size), where a single field with D=Editable is correct: the protocol registers the target value and the analyst may adjust within allowed bounds.

2. **Setting the signal integration window as protocol-level.** The integration window is selected during data reduction by applying the Signal Integration Interval Method to the actual signal — it is analysis-level. The *method* for selecting the window is protocol-level; the resulting *window or time* is analysis-level.

3. **Assigning Read-Only to a field that is routinely session-tuned.** Parameters adjusted during daily tuning (background settings, flow rates) should be Editable, not Read-Only.

4. **Using "Default", "Target", "Achieved", or "Typical" in field names.** Field names should be level-neutral; the tier columns (C and D) encode whether a value is a protocol target or an analysis-level measurement. Use the description (Column B) to clarify that the protocol registers a target or typical value. Exceptions: "Target Material" and "Target Feature(s)" are retained because "Target" here means the material/feature *type* the protocol is designed to analyze, not a value that is later achieved — these have no analysis-level counterpart and no ambiguity.

5. **Using "Element-Specific" instead of "Analyte-Specific".** The correct term is Analyte-Specific to remain technique-agnostic across all TAPP types.

6. **Using "Method" when referring to the registered protocol object.** Use "Protocol" for the registerable object. "Method" is reserved for assessment methods, calculation methods, and sub-procedures. See `references/conventions.md` for the full vocabulary.

---

## Reading Order for a New TAPP

1. Read `references/conventions.md` — mandatory before writing anything
2. Read `references/workflow.md` — full phase-by-phase guidance
3. As needed during Phase 2: read `references/field-review.md`
4. As needed for precedent: read `references/precedents.md`
