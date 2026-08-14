# Field Review Checklist

This file contains the complete decision criteria for Phase 2 (Structured Field Review), organized as a per-field checklist with heuristics and worked mini-examples for each question.

Use this file during Phase 2 when you need specific guidance on a particular decision type.

---

## The Four Questions: Decision Trees

### Q1 — Ontological: Procedure or Analysis?

```
Is the value determined BEFORE the session begins?
    ├── YES → Procedure-level
    │         └── Is it also recorded per-analysis? → Both levels (consider split)
    └── NO
         ├── Determined BY the instrument during acquisition → Analysis-level, D=Basic
         ├── Determined BY the analyst during data reduction → Analysis-level, D=Basic
         └── Can only be known IN RETROSPECT (e.g., precision, accuracy, LOD) → Analysis-level, D=Basic
```

**The hardest cases are "both levels."** The distinguishing sign is: does the procedure-level version capture a *target* or *constraint*, while the analysis-level version captures the *actual measured result*? If so, split them. The procedure-level field documents what was intended; the analysis-level field documents what actually occurred.

Examples of both-level fields that should be split:
- Oxide production threshold (procedure: acceptance criterion) vs. oxide production measured (analysis: actual ratio) — split because these are different *types* of information (criterion vs. measurement)

Examples of both-level fields that should NOT be split (use D=Editable instead):
- Analyte (procedure: range of isotopes the procedure is designed to measure; analysis: specific isotopes measured in this session, which may be a subset) — same type of information at different stages; D=Editable captures that the analyst may narrow the set
- Laser fluence (procedure: target value; analysis: as-run value) — same quantity; D=Editable is correct

- RF power: the procedure specifies it; the analysis uses the same value. Read-Only at analysis level is the correct representation, not a split.
- Spot geometry: the procedure registers the typical geometry; the analyst may use a different size for different phases. D=Editable captures this without splitting.

---

### Q2 — Mode Applicability: Which modes?

*For each analytical mode defined in Phase 0, does this field apply (Y) or not (N)?*

Evaluate the field against each mode independently. The number of modes varies by technique — this question is answered once per mode, not just for three fixed modes.

**General patterns for any number of modes:**

| Pattern | Meaning | Action |
|---|---|---|
| All Y — same meaning | Universal, mode-invariant | No description note needed |
| All Y — different meaning | Universal, mode-dependent semantics | Keep one field; describe each mode's interpretation explicitly |
| Some Y, some N | Mode-restricted | Set N for excluded modes; note in field name if restriction is fundamental |
| One Y only | Single-mode field | Note restriction in field name: e.g., "X (Mode-Name Only)" |

**The key distinction: "not applicable" vs. "not typically done"**

Set N only when the concept does not meaningfully exist for that mode — when a user filling out the TAPP for that mode would have nothing to report because the concept is irrelevant to how the technique works in that mode.

Set Y (with a description note) when the concept exists but is rarely practiced in that mode. This preserves the ability to document absence as a deliberate choice, rather than leaving the field ambiguous.

Examples across technique families:

| Field | Mode A (e.g., point/spot) | Mode B (e.g., line scan) | Mode C (e.g., 2D map) |
|---|---|---|---|
| Per-analysis acquisition duration | Y — fixed per procedure | N — determined by line length (analysis-level) | N — determined by map area (analysis-level) |
| Spatial step or scan speed | N/A (stationary) | Y — procedure-level | Y — procedure-level |
| Line/raster spacing | N — concept does not exist | N — single line only | Y — mandatory for map design |
| Background measurement interval | Y — pre-acquisition blank per analysis | Y — pre-line blank | Y — per-session or per-line blank (different implementation; describe both) |
| Calibration bracketing frequency | Y | Y | Y — but implementation differs for long map sessions |

For fields with mode-dependent semantics (all Y but different meaning), the description must explicitly address each mode. Do not write a generic description and leave mode-specific behavior implicit.

---

### Q3 — Granularity: One or Two Fields?

The split-or-merge decision follows a consistent pattern. Ask:

1. **Do the two components have different tier assignments?**
   - Same tier at both levels → merge (capture both in description)
   - Different tiers → split (they serve different procedure/analysis purposes)

2. **Would users legitimately search or filter on each component independently?**
   - Yes → split (each is a distinct piece of information)
   - No → merge (they are always used together)

3. **Is one component almost always blank?**
   - Yes → do not split (creates a mostly-empty field)

**Canonical split pattern — threshold vs. value:**
The most common split in analytical chemistry TAPPs. A procedure specifies a threshold or acceptance criterion (e.g., "ThO⁺/Th⁺ must be <0.5%"). The analysis records the actual measured value (e.g., "ThO⁺/Th⁺ = 0.3%"). These have different tiers (procedure: Basic, Read-Only at analysis; measured: N/A procedure, Basic analysis) and serve different purposes (quality gating vs. reporting).

Fields that commonly follow this pattern:
- Oxide production threshold (procedure) / Oxide production measured (analysis)
- Mass bias correction factor target (procedure) / Mass bias factor as-run (analysis) [where applicable]
- Instrumental blank threshold (procedure) / Procedural blank measured (analysis) [solution ICP-MS]

**Scope fields with D=Editable:**
A procedure defines the *scope* of what it is designed to measure (e.g., the analyte suite). An analysis may measure a subset of that scope. Use a single field with D=Editable: the procedure registers the intended scope; the analyst confirms or narrows it at analysis time. Do not split into separate procedure-scope and analysis-execution fields.

- Analyte (C=Basic, D=Editable): procedure registers the full isotope suite; analyst may record a subset actually measured
- Target material (procedure) / Sample name (analysis) [different concepts entirely — already separate fields in Group 2]

---

### Q4 — Tier Assignment Decision Table

#### Procedure-Level Tier (Column C)

| Use Basic when... | Use Advanced when... | Use N/A when... |
|---|---|---|
| The procedure is under-specified without this field | The field is best practice but not strictly required | This field can only be known at analysis time |
| A reproducibility expert would always expect this documented | Thorough labs include it; others may not | The concept does not exist at procedure level |
| Absence of this value creates ambiguity about what was measured or how | It contributes to completeness, not minimum specification | |

**Borderline Basic vs. Advanced — ask:** "If a researcher tried to reproduce this method without this field, would they be unable to get comparable results?" If yes → Basic. If they would probably get comparable results but with some uncertainty → Advanced.

#### Analysis-Level Tier (Column D)

D=N/A is not a valid analysis-level tier. Every field must carry one of: Read-Only, Editable, Basic, Advanced.

| Use Read-Only when... | Use Editable when... | Use Basic when... | Use Advanced when... |
|---|---|---|---|
| Changing the value would mean running a different procedure | The value is a procedure target but is legitimately adjusted during daily tuning | The analyst must provide this value (it comes from the analysis, not the procedure) | The value is useful but not required for a credible analysis record |
| The value is a fundamental invariant of the method design | Minor updates (e.g., software version) do not constitute a different procedure | The value cannot be predicted from the procedure alone | Literature shows it is rarely reported, suggesting it is not a community norm |
| The field is relevant only at procedure level and does not vary per analysis | | | |

**Read-Only vs. Editable: the daily tuning test.** If a value is routinely verified or adjusted during instrument startup and tuning before each session, it is Editable, not Read-Only. Examples of Editable: flow rates tuned to maintain stable plasma or background conditions; background measurement duration adjusted based on signal stability; software version updated without changing the procedure. Examples of Read-Only: instrument manufacturer and model (cannot change without a new procedure); excitation source wavelength or beam energy (hardware property); internal standard or calibration approach (changing this changes the data reduction fundamentally).

**Basic vs. Advanced at analysis level: the community norm test.** If the majority of published papers in the relevant literature report this value, it should be Basic. If it is best practice but uncommonly reported, Advanced. This judgment should be revisited after Phase 3 with actual data. During Phase 2, assign a provisional tier and flag it for Phase 3 validation.

---

## Tier Combination Reference

Valid tier combinations and their meanings:

| C (Procedure) | D (Analysis) | Meaning |
|---|---|---|
| Basic | Read-Only | Core procedure parameter; always the same in every analysis following this procedure. Also used for administrative procedure-only fields (e.g., funding for procedure development) that are displayed read-only in the analysis record. |
| Basic | Editable | Core procedure parameter with a defined target; analyst may tune within allowed range. The procedure registers the typical or target value; the analyst confirms or adjusts it. |
| Advanced | Read-Only | Optional procedure parameter; if specified, always the same in every analysis |
| Advanced | Editable | Optional procedure parameter with a target; analyst may tune if specified |
| N/A | Basic | Analysis-only field; mandatory per-analysis input (analyst provides from the analysis itself) |
| N/A | Advanced | Analysis-only field; optional per-analysis input |
| Advanced | Basic | Field is optional at procedure level (may be void when procedure is registered) but mandatory when reporting any analysis. Use when a value cannot be characterized until the procedure has been applied to real samples, yet must be documented for every data submission. Examples: detection limits, precision, accuracy — these require accumulated session data to characterize properly, so they are not required for procedure registration, but are non-negotiable for credible analytical data. See Detection Limit entry in `references/precedents.md`. |
| Basic | Basic | Field exists at procedure level AND requires fresh analyst input at analysis level. Rare — only when the analysis value is genuinely independent of the procedure specification. |
| N/A | Read-Only | **Invalid.** Read-Only means imported from procedure. If C=N/A, there is nothing to import. |
| N/A | Editable | **Invalid.** Same reason — nothing to import from procedure. |
| Basic | N/A | **Invalid.** D=N/A is not a permitted analysis-level tier. Use D=Read-Only for fields that are procedure-only. |
| Advanced | N/A | **Invalid.** Same reason. Use D=Read-Only. |

---

## Naming Conventions Quick Reference

See `references/conventions.md` for the full vocabulary. Key naming rules for field review:

- **Do not use** "Default", "Target", "Achieved", "Typical", or "Actual" as prefixes/suffixes that encode which level a value belongs to. Field names are level-neutral; use Column B to clarify that the procedure registers a target or typical value: "Laser Fluence (Energy Density)", "Carrier Gas and Flow Rate", "Voxel Size"
- **Exception**: "Target Material" and "Target Feature(s)" retain "Target" because it means *the type of material or feature the procedure is designed to analyze*, not a value with an achieved counterpart
- Use **"(Measured)"** or a separate field name for analysis-level values corresponding to procedure-level *acceptance criteria* (thresholds, pass/fail gates) only: "Oxide Production" (measured) vs. "Oxide Production Method and Threshold" (criterion). This is distinct from session-tunable parameters, which use D=Editable.
- Use **"Procedure"** rather than **"Method"** when referring to the overall registered procedure object: "Procedure DOI", "Procedure Name", "Funding Source for Procedure Development"
- Declare cardinality in **Column I (`Keyed By`)**, never in Comments — see Rule 7 in `conventions.md`. Ask what the field's value repeats over: `(none)`, `analyte`, `channel`, `reported property`, `sampling unit`, or a secondary key. The superseded label "Analyte-Specific" named only one of these, and not the most common one
- **If the field declares `defines: X`, ask a second question: does it also repeat over something?** A definer can carry a parent key — `Monitored Isotopes` enumerates the masses (`channel`) but does so *per analyte element*, so it is `defines: channel per analyte` (Rule 7.3.1). Four of the library's eight definers turned out to be of this shape, and two of them said so only through their example values ("Fe L2,3; O K" — an edge named per element), never in cardinality language. **Read Column B and Column F against Column I, not Column I alone**
- **Mine Column B for information that belongs in a structured column, then delete it from the prose.** A description asserting a key that Column I does not carry is the defect the 2026-08-12 survey was built to find; a description restating a key Column I already carries is redundant text to remove. Neither is visible from Column I alone
- Use **"(Mode Only)"** suffix in field names when a field is restricted to a single mode: "Raster Line Spacing (Mapping Only)"
