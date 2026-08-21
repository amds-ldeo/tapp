> **⚠️ ARCHIVED — PRE-VIM3 SNAPSHOT (2026-07-24)**
> This file reflects TAPP terminology *before* alignment with BIPM VIM3 (JCGM 200:2012): "Protocol" = the
> registerable, DOI-bearing object; "Procedure"/"Analysis" = the analysis-level execution. Kept for
> historical record only — **do not use for current TAPP work.** Current version lives at the original
> path in the TAPPs project (same filename, without this suffix).
>
> See the "Aligning TAPP Vocabulary with VIM3" migration plan for the full rationale.

---

# Literature Assessment Skill

**Trigger:** Read this file at the start of any Phase 3 literature assessment task — whenever you are asked to extract protocol metadata from one or more papers into a TAPP assessment column.

---

## Non-Negotiable Rules

These rules override everything else. They exist because past extractions were corrupted by relying on session summaries rather than source documents.

### Inference Rule
**Only record values that are directly stated in the paper.** If a value is logically implied by other stated values but not written explicitly, record `N`. Do not complete the mental step from stated facts to implied values.

Examples of prohibited inferences:
- Paper says "JEOL JXA-8200" → do NOT infer "LaB6 electron source" (not stated)
- Paper says "Cameca SX100" → do NOT infer "WDS (all analytes)" unless WDS is written
- Paper says "Probe for EPMA" → do NOT infer matrix correction algorithm (unless stated separately)
- Standard assignment for element X → analyte X is confirmed; crystal, line, and spectrometer are NOT unless stated

### Source Rule
**Every value you record must be traceable to a specific sentence, table cell, or figure caption in the source document read in the current session.** If you have not read the source document directly, read it before filling any column. Session summaries, prior session notes, and common knowledge about instrument types are not valid sources.

### N vs. N/A
| Value | Use when |
|-------|----------|
| `N` | The field is applicable to this protocol but the value is not directly stated in the paper |
| `N/A` | The concept genuinely does not apply to this protocol (e.g., EDS acquisition time for a WDS-only instrument; halogen correction for a protocol measuring no halogens) |

Never leave a cell blank. Blank is ambiguous.

---

## PDF Reading Procedure

Since `pdfplumber` is required (the `Read` tool requires `poppler` which may not be installed), use this approach:

```python
import pdfplumber

with pdfplumber.open('path/to/paper.pdf') as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for i, pg in enumerate(pdf.pages):
        txt = pg.extract_text()
        if txt:
            print(f"--- PAGE {i+1} ---")
            print(txt)
```

**Steps before extracting any field:**

1. **Full page count** — know how many pages the PDF has.
2. **Grep for EPMA terms** across all pages to locate the methods section:
   ```python
   keywords = ['electron microprobe', 'epma', 'microprobe', 'probe for', 'jeol', 'cameca',
               'accelerat', 'kv', 'wds', 'eds', 'wavelength', 'standard', 'calibrat',
               'detection', 'background', 'matrix correct', 'citzaf', 'pap', 'zaf',
               'carbon coat', 'polished', 'thin section', 'peak count', 'x-ray map']
   ```
3. **Read the full methods section page by page** — do not rely on grep matches alone. Read each methods page in full to capture context.
4. **Check data tables explicitly** — detection limits, interference corrections, and analyte lists are often in tables or supplementary material, not the main text. Scan table captions for EPMA-relevant content.
5. **Re-read source sentences before writing** — do not rely on notes from step 2/3 without re-reading.

---

## Standalone Draft CSV Format

For each pair of papers (or batch), create a standalone draft CSV **before** touching the main TAPP CSV. This allows the user to review and approve before incorporation.

**File naming:** `lit_assessment_draft_[Author1Year]_[Author2Year].csv`

**Header row:**
```
Metadata Item, [Author+Year | Instrument | Lab], [Author+Year | Instrument | Lab], ...
```

**Column 1 (Metadata Item):** Exactly match the field names in the TAPP (Column A). Include group header rows (`1. Protocol Identification`, etc.) and blank separator rows.

**Group header rows:** Use `N` in all protocol columns (consistent with TAPP convention).

**Blank separator rows:** Leave all columns blank/empty.

**Source citations in cells:** When a value is directly stated, include a bracketed citation to the source sentence (e.g., `[F3]` or `[B2]`) using the source key defined in the script docstring. These citations are for review purposes; they are stripped when incorporating into the main TAPP.

---

## Protocol Separation Decisions

A single paper may require **multiple columns** if:
- Different instruments were used for different analyses in the same paper
- Different labs are described with separate conditions
- Different analytical modes are used with different conditions (e.g., distinct settings for silicates vs. phosphates)

Give each column a header identifying: Author+Year | Instrument Model | Lab.

**One column per instrument** is the default when two instruments are used in the same paper, even if conditions are partially shared.

---

## Field-by-Field Extraction Notes

### Instrument fields
- State the instrument exactly as written: `"JEOL JXA-8200 electron microprobe"` → Instrument Model = `JXA-8200 (stated as "JEOL JXA-8200 electron microprobe")`
- If the paper uses a non-standard model name (e.g., "JEOL 8200" without "JXA" prefix), note that in the value.
- WDS vs. EDS: Record `N` for EPMA Technique per Analyte unless the paper explicitly uses the term "WDS," "wavelength-dispersive," "EDS," or "energy-dispersive" in the context of which analytes were measured.

### Standards
- Record the full standard list exactly as stated if given. If the paper says only "natural and synthetic minerals" without naming them, record that phrasing + `(specific names NR)`.
- For analyte-specific standards (e.g., F-phlogopite for F), note the association: `synthetic F-phlogopite (for F, LDE1 crystal)`.

### Background methods
- MAN (mean atomic number) background: off-peak counting time and positions = `N/A` (no off-peak counting is performed).
- Two-point off-peak: record time and positions separately if stated.
- Polynomial fit on reference phases: record as a background method variant; off-peak positions = `N/A`.

### Matrix correction
- Only record what is explicitly named: `PAP`, `XPP`, `CITZAF`, `ZAF`, `Bence-Albee`, etc.
- `Probe for EPMA` alone does NOT imply a specific matrix correction — the software supports multiple. Record `N` unless the correction is named.
- CITZAF is specific to Armstrong 1995 and is NOT the same as PAP. The Caltech GPS Analytical Facility (Chi Ma) uses CITZAF, not PAP.

### Analytes
- If an explicit analyte list appears in methods: record it.
- If analytes can be reconstructed from standards assignments (e.g., "Kakanui kaersutite for Si, Al, Ti..."): record the reconstructed list, noting the source.
- If only results tables or individual element mentions exist without a formal methods-section list: record `N`, with a note in Additional Notes about what elements appeared in results.

### X-ray lines
- X-ray lines are often NOT stated even when analytes are. Do not infer Kα for light elements, Lα for heavy elements, etc. — record `N` unless stated.
- Diffracting crystal is a separate field: record it separately from the X-ray line.

### Detection limits
- Record exactly as stated, including the qualifier ("typically," "approximately") and the unit.
- If given as a range over groups of elements (e.g., "0.03–0.04 wt% for Al₂O₃, K₂O, CaO"), record the range plus the element list.
- If not stated, record `N`.

### Mapping conditions
- Mapping conditions (step size, dwell time, beam current during mapping, map area) are frequently absent even when mapping is done. Record what is stated; use `N` for each unstated parameter.
- Stage scan vs. beam scan: if the paper says "stage mapping," record `Stage scan`. If it says "beam scan" or "rastered beam," record `Beam scan`. Otherwise `N`.
- Mapping software (CalcImage, XMapTools, etc.) goes in Data Reduction Software.

---

## Workflow Steps

1. **Read the full TAPP CSV** (or at minimum Group 3–6 fields) to have the complete field list.
2. **Read each paper from PDF** using pdfplumber — full methods section + any data tables — before writing any extraction.
3. **Write the standalone draft CSV** with N/N/A conventions and source citations.
4. **Present the draft** to the user for review.
5. **After user approval**, update the main TAPP CSV by either:
   - Running a targeted patch script to update individual columns
   - Also correcting column headers if the instrument was misidentified in the initial extraction
6. **Update `paper_registry.csv`** in the same session — see rules below.

---

---

## Paper Registry Rules

`paper_registry.csv` lives at `/Users/ruolin/Documents/Astromat/TAPPs/paper_registry.csv`.
It tracks every paper that has been assessed for any TAPP, recording which analytical techniques
appear in each paper and how well documented each technique's protocol is.

### When to update

Update the registry **in the same session** as the literature assessment — not retroactively.
Every value in the registry must be traceable to a specific sentence or section read directly
from the source PDF in the current session. Session summaries and inference are not valid sources.

### Schema

Fixed columns: `Citation Key | DOI | PDF Filename | File Location`

Technique columns use the **exact "Proposed TAPP Name"** from `TAPP_Planning_Table.xlsx`.
Only add a technique column if that technique appears in at least one registered paper.
Do not invent column names — look up the planning table first.

### Cell values

Use **bare labels only** — no explanatory notes, dashes, or qualifiers after the label.

| Value | Use when |
|-------|----------|
| `Detailed` | Paper has a dedicated method description with enough detail (instrument model + conditions, standards, software, etc.) that it could usefully inform a future TAPP assessment for that technique |
| `Brief` | Technique is mentioned (possibly with instrument name or facility) but no protocol parameters are given; not useful as a TAPP source on its own |
| `N` | Technique not used in this paper (including cases where it is mentioned only as future work) |

Never leave a cell blank. Never write "Coupled only", "Detailed — …", "Brief — …", or "N — …" — the label must stand alone.

### How to assign Detailed vs. Brief

Read the actual methods section (or supplementary methods) for each coupled technique before assigning a label. Do **not** infer from:
- The journal impact factor or paper length
- Whether the technique appears as a headline result
- Common knowledge about what protocols usually contain

Minimum criteria for **Detailed**: instrument model stated + at least one of (beam/laser conditions, standards, software, count times, acquisition parameters).

**Brief** if only: technique name + possibly instrument model or facility, with no operating conditions.

### Flagging unlisted techniques

If a technique used in a paper does not appear in `TAPP_Planning_Table.xlsx`, record it in the `N — <note>` format in the closest matching column (or add a temporary "Other" note) and flag it to the user immediately so the planning table can be updated.

### File location

The registry is maintained by `generate_paper_registry.py` at the TAPPs root. When adding a new paper:
1. Add a new dict entry to `papers` in that script with all 18 fields filled.
2. Run the script to regenerate the CSV.
3. Spot-check the output CSV.

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Recording PAP for Caltech GPS Chi Ma protocols | Chi Ma's Caltech lab uses CITZAF (Armstrong 1995), not PAP. This is confirmed in Ma et al. 2017/2018. Check every Ma/Caltech extraction. |
| Recording Probe for EPMA as implying PAP | Probe for EPMA supports multiple matrix corrections. Never infer PAP from software name alone. |
| Inferring WDS from instrument model | "JEOL JXA-8200" or "Cameca SX100" → WDS only if the paper says so. |
| Using session summary values | Session summaries have been wrong (wrong instrument model, wrong matrix correction, missing detection limits). Re-read the source PDF every time. |
| Missing values in tables | Detection limits, interference corrections, and calibration standards are frequently in tables, not prose. Always scan table captions. |
| Misidentifying instrument model from summary | Frank 2023 uses Cameca SX100, not JEOL JXA-8530F. Broussard 2026 uses JEOL JXA-8200, not JXA-8230. Read the paper. |
| Treating "Not reported" as a valid cell value | Use `N` for "applicable but not stated." Never write the string "Not reported." |
| Labelling all coupled techniques as "Brief" without reading them | Read each coupled technique's methods section before assigning Detailed or Brief to the registry. |
| Updating the registry from session summary instead of source PDF | The registry must be filled from values read in the current session. If the PDF was not read in this session, re-read before filling. |
| Using a technique column name not in the planning table | Always look up the exact "Proposed TAPP Name" in `TAPP_Planning_Table.xlsx` before adding a column. |
| Writing "Detailed — note" or "N — reason" in the registry | Cell values must be bare labels only: `Detailed`, `Brief`, or `N`. No dashes, notes, or qualifiers. |

---

## Post-Extraction Checklist

Before delivering the draft CSV, verify:

- [ ] Every cell contains either a value, `N`, or `N/A` — no blanks
- [ ] Every stated value traces to a specific source sentence (documented in script docstring or inline citation)
- [ ] No values were inferred from instrument type, software name, or common practice
- [ ] Table content was explicitly checked, not just prose
- [ ] Group header rows contain `N` in all protocol columns
- [ ] Blank separator rows are blank
- [ ] Column headers follow the format: `Author+Year | Instrument | Lab`
- [ ] `paper_registry.csv` updated in this session with Detailed/Brief/N labels drawn from direct PDF reading (not from session summary)
