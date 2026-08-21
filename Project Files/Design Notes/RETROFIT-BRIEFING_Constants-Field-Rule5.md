# Briefing: retrofit "Constants and Reference Values Used" as a mandatory cross-TAPP field (Rule 5)

**How to use this file:** paste this whole document as your first message in a new Claude Code session
in this project. It is written to be self-contained — it does not assume you have any memory of the
conversation that produced it. Read it fully before making any edits.

---

## 1. What happened and why you're here

While building a standalone test TAPP (`LA-ICP-MS Geochronology (Horstwood Test)/LA-ICPMS_Geochron_Horstwood_TAPP_v5.csv`)
from Horstwood et al. (2016)'s community LA-ICP-MS U-Th-Pb geochronology reporting standard, we found that
Table 3 (the paper's metadata template) never asks for the physical constants used in data reduction —
even though Table 4 (the paper's *data* template) has a footnote stating "Decay constants of Jaffey et al.
(1971) used." That's exactly the kind of thing that needs to be traceable: decay constants and standard
isotope ratios get revised over time (concrete example: the ²³⁸U/²³⁵U ratio was long assumed to be a
constant 137.88 per Steiger & Jäger 1977, until Hiess et al. (2012) showed it actually varies in nature —
many labs now use 137.818 or sample-specific values instead). A reported age or ratio can only be correctly
reinterpreted against a future revision of a constant if the constant originally used is documented.

We added a new field for this to the Horstwood test TAPP (Group 5, see spec below) and the user decided
it should become a **mandatory field in every TAPP** in this project, not just geochronology ones — the
field is written generically enough to apply to any technique whose data reduction depends on a citable,
potentially-revisable constant. This mirrors how "Analytical Mode" (Rule 3 in `references/conventions.md`)
is mandatory in every TAPP regardless of whether the technique has multiple modes.

**Your job:** make this official — add it as a new numbered rule in `references/conventions.md`, document
it in `references/precedents.md`, and retrofit it into every current TAPP.

---

## 2. Read this before touching any files

**Start here, in order:**
1. Invoke the `tapp` skill (or read directly): `Claude Skills for TAPP/references/conventions.md`,
   `references/workflow.md`, `references/precedents.md`. Per the skill's own instructions, these must be
   read before writing any TAPP content — this is a retrofit, but the same rule applies.
2. Read `TAPP_Planning_Table.csv` (project root) and search `TAPP_Development_Log.md` for any topic you're
   about to touch, rather than reading either end-to-end.

**Critical trap — read this twice:** `LA-ICP-MS/LA-ICPMS_TAPP_v13.csv` and
`LA-Q:SF-ICP-MS/LA-Q:SF-ICPMS_TAPP_v4.1.csv` are **the same TAPP lineage**, not two separate TAPPs, despite
living in differently-named folders. The `LA-ICP-MS` folder is a **stale, frozen branch** — it received no
real development after a rename to "LA-Q/SF-ICP-MS" partway through the project's history, and its `v13`
is just `v12`'s content plus an unrelated terminology-only pass, not organic growth. **The current,
actively-maintained file for this technique is `LA-Q:SF-ICPMS_TAPP_v4.1.csv`.** Do not edit, cite, or count
`LA-ICPMS_TAPP_v13.csv` as current — if your file inventory lists both as separate TAPPs, it's wrong, merge
them into one. Full detail, if you want it: memory file `reference_la_icpms_lineage.md`. This has already
caused one real mistake in a prior session (a comparison workbook had to be rebuilt after being run against
the wrong file) — don't repeat it.

**Verify, don't trust, the file inventory below.** Versions move on. Before editing anything, run
`find` to confirm actual current versions:
```bash
find "/Users/ruolin/Documents/Astromat/TAPPs" -iname "*_TAPP_v*.csv" | grep -v "Pre-VIM3"
```
Best-known inventory as of this writing (11 distinct TAPPs — verify this count, not 12):
EPMA, LA-Q/SF-ICP-MS (the file above, NOT the stale LA-ICP-MS branch), SEM, SEM_Composition, SEM_Imaging,
SEM_FIBSEM, Solution MC-ICP-MS, Solution Q-ICP-MS, Solution SF-ICP-MS, TEM, Lab-XCT.

---

## 3. Open question to resolve FIRST, before retrofitting anything

Some existing TAPPs cover techniques with no plausible citable-constant dependency in their data reduction
(e.g. pure imaging/morphology sub-TAPPs like SEM_Imaging, or Lab-XCT). Two options:

- **(a) Fully universal** (recommended, matches Rule 3's own "even single-mode techniques get Analytical
  Mode" precedent): add the field to literally every TAPP, description explicitly says to record "None" or
  "Not applicable" when no such constants exist. Field presence itself is informative — distinguishes
  "deliberately none" from "nobody asked."
- **(b) Scoped**: only add to TAPPs where a technique-appropriate reviewer agrees it's plausibly relevant
  (geochronology-adjacent, isotope-ratio, quantitative-composition techniques), skip pure-imaging TAPPs.

The user's original phrasing ("make this field mandatory for other TAPPs as well") leaned universal, but
this wasn't explicitly pinned down. **Confirm with the user which approach before doing the retrofit** —
it changes which TAPPs are in scope. Default to (a) if you can't get a quick answer; it's the more
conservative, more consistent-with-existing-precedent choice, and an unneeded field is lower cost than a
missing one.

---

## 4. Field specification

```
Metadata Item:          Constants and Reference Values Used
Group:                  5. Data Processing (last field in the group, immediately before the
                         blank separator row preceding Group 6)
Procedure-Level Tier:   Basic
Analysis-Level Tier:    Editable
Data Type:              Text (free)
Description:            Physical constants and reference values used in data reduction to
                         calculate the final reported quantity (e.g., decay constants for age
                         calculation, standard isotope ratios, or other citable reference values
                         used in a correction or calculation), together with their source.
                         Distinct from Reference Material Information / Secondary Reference
                         Materials (Group 6), which document accepted values for specific
                         calibration/validation materials rather than universal physical
                         constants. Record "None" if no citable, revisable physical constants
                         feed into this procedure's data reduction.
Example/Allowed Content: e.g., "λ238U = 1.55125×10⁻¹⁰ yr⁻¹, λ235U = 9.8485×10⁻¹⁰ yr⁻¹ (Jaffey et
                         al. 1971); 238U/235U = 137.818 (Hiess et al. 2012)" | "None"
```

**Why C=Basic:** mandatory declaration, mirroring Analytical Mode (Rule 3) — even techniques with no
constant-dependent calculation should explicitly state "None" rather than silently omitting the field, so
the field's universal presence is itself informative.

**Why D=Editable:** the constants in use are embedded in whatever data-reduction software/method is
current; if community-recommended values are revised between procedure registration and a later analysis
session, documenting the update shouldn't require registering a whole new procedure — same logic as
`Data Processing Software(s)` (D=Editable, Rule 1).

---

## 5. Draft text to add to `references/conventions.md`

Add as a new rule after the existing Rule 4 (Propagation obligation), in the "Cross-TAPP Consistency Rules"
section. Check the current rule numbering first — if a Rule 5 already exists (someone else may have added
one), renumber this to fit; don't overwrite.

```markdown
### Rule 5 — "Constants and Reference Values Used" field is mandatory in Group 5 of every TAPP

Every TAPP must include a **"Constants and Reference Values Used"** field as the last field in Group 5
(Data Processing), regardless of whether the technique's data reduction depends on citable physical
constants.

**Canonical definition:**
- Field name: `Constants and Reference Values Used`
- Procedure-Level Tier: Basic
- Analysis-Level Tier: Editable
- Data Type: Text (free)
- Placement: last field in Group 5, immediately before the blank separator row preceding Group 6
- Description: "Physical constants and reference values used in data reduction to calculate the final
  reported quantity (e.g., decay constants for age calculation, standard isotope ratios, or other citable
  reference values used in a correction or calculation), together with their source. Distinct from
  Reference Material Information / Secondary Reference Materials (Group 6), which document accepted values
  for specific calibration/validation materials rather than universal physical constants. Record 'None' if
  no citable, revisable physical constants feed into this procedure's data reduction."

**Purpose:** traceability of any reported quantity that depends on external, periodically-revised physical
constants. A reported value can only be correctly reinterpreted against a future revision of such a
constant if the constant originally used is documented. Most consequential for geochronology (decay
constants; the ²³⁸U/²³⁵U ratio, revised by Hiess et al. 2012 after decades of assumed-constant 137.88) but
written generally, since any technique's data reduction could in principle depend on a citable constant.

**Why C=Basic:** mandatory declaration, mirroring Rule 3's Analytical Mode — the field's universal presence
is itself informative, distinguishing "deliberately none" from "not asked."

**Why D=Editable:** the constants in use are embedded in the data-reduction method; documenting a revision
between procedure registration and a later session shouldn't require a new procedure (same logic as the
Group 3 software fields, D=Editable).

**Retrofitting to existing TAPPs (as of [FILL IN DATE]):** [list which TAPPs were touched and their new
version numbers here as you complete them]
```

---

## 6. Draft text to add to `references/precedents.md`

Add under a "Group 5: Data Processing" heading (create one if it doesn't exist yet), following the
"Decision → Reasoning → Generalization" format used throughout that file:

```markdown
### "Constants and Reference Values Used" as a mandatory Group 5 field — purpose and distinction from Reference Material Information

**Context:** Identified while building a test TAPP for LA-ICP-MS U-Th-Pb Geochronology (derived from
Horstwood et al. 2016's community reporting standard), motivated directly by a footnote in the paper's own
Table 4 ("Decay constants of Jaffey et al. (1971) used") — information the paper's own Table 3 metadata
template never captured as a structured item, despite feeding directly into every reported age.

**Decision:** Mandatory field in Group 5 of every TAPP (Rule 5), C=Basic, D=Editable, Text (free). Record
"None" when not applicable.

**Reasoning:** Community-recommended values for physical constants used in data reduction — decay
constants, standard isotope ratios — are periodically revised. The ²³⁸U/²³⁵U ratio is a concrete precedent:
long assumed constant at 137.88 (Steiger & Jäger 1977), then shown by Hiess et al. (2012) to vary in
nature, prompting many labs to adopt 137.818 or sample-specific values instead. A reported age computed
under the old value cannot be correctly reinterpreted against the new one unless the original value used is
documented. This is distinct from Reference Material Information (Group 6), which documents accepted
values of *specific materials* (e.g., zircon 91500's isotopic composition) rather than *universal physical
constants* that apply regardless of which material was run.

**Generalization:** Most consequential for geochronology and any isotope-dilution-dependent technique
(⁴⁰Ar/³⁹Ar, Sm-Nd, Rb-Sr all have analogous decay-constant-revision histories), but written generally since
data reduction in any technique could in principle depend on a citable, revisable constant.
```

---

## 7. Per-TAPP retrofit template

Use a targeted patch script per TAPP (per `conventions.md`'s own patch-script convention — don't
regenerate whole files from scratch). Template:

```python
import csv

INPUT = "path/to/Technique_TAPP_vN.csv"
OUTPUT = "path/to/Technique_TAPP_v(N+1).csv"  # integer bump: field addition = major structural revision
DATE = "YYYY-MM-DD"  # today

with open(INPUT, newline='', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

header = rows[0]
n_cols = len(header)

NEW_ROW = [""] * n_cols
NEW_ROW[header.index("Metadata Item")] = "Constants and Reference Values Used"
NEW_ROW[header.index("Description")] = ("Physical constants and reference values used in data reduction "
    "to calculate the final reported quantity (e.g., decay constants for age calculation, standard "
    "isotope ratios, or other citable reference values used in a correction or calculation), together "
    "with their source. Distinct from Reference Material Information / Secondary Reference Materials "
    "(Group 6), which document accepted values for specific calibration/validation materials rather than "
    "universal physical constants. Record \"None\" if no citable, revisable physical constants feed into "
    "this procedure's data reduction.")
NEW_ROW[header.index("Procedure-Level Tier")] = "Basic"
NEW_ROW[header.index("Analysis-Level Tier")] = "Editable"
NEW_ROW[header.index("Data Type")] = "Text (free)"
NEW_ROW[header.index("Example/Allowed Content")] = ("e.g., \"lambda238U = 1.55125e-10 yr-1 (Jaffey et al. "
    "1971)\" | \"None\"")  # adapt per technique; use the technique's actual relevant example if it has one
NEW_ROW[header.index("Comments")] = "Source: In-house TAPP rule — Rule 5 (mandatory in all TAPPs)"
NEW_ROW[header.index("Last Update")] = DATE
# If this TAPP has mode-flag columns (between "Last Update" and the "Literature Assessment" sentinel),
# set them all to "Y" -- this field is general, not mode-restricted.
if "Literature Assessment" in header:
    sent_idx = header.index("Literature Assessment")
    last_update_idx = header.index("Last Update")
    for i in range(last_update_idx + 1, sent_idx):
        NEW_ROW[i] = "Y"

# Insert as the last field in Group 5, i.e. immediately before the blank row that precedes
# the "6. Quality Control & Uncertainty" group header. Find that boundary:
group6_idx = next(i for i, r in enumerate(rows) if r and r[0].strip().startswith("6."))
insert_at = group6_idx - 1  # the blank separator row right before Group 6
assert rows[insert_at][0] == "", f"expected blank row at {insert_at}, got {rows[insert_at]}"

new_rows = rows[:insert_at] + [NEW_ROW] + rows[insert_at:]

with open(OUTPUT, "w", newline='', encoding='utf-8-sig') as f:
    csv.writer(f).writerows(new_rows)

print(f"Inserted at row {insert_at}, {len(rows)} -> {len(new_rows)} rows")
```

**After running the patch, for each TAPP:**
1. Verify: no duplicate field names, all tier values valid (`Basic`/`Advanced`/`N/A` for C;
   `Read-Only`/`Editable`/`Basic`/`Advanced` for D), row count increased by exactly 1.
2. Regenerate the xlsx: `python3 "Claude Skills for TAPP/scripts/tapp_to_xlsx.py" "<new CSV>"`.
3. Add a dated entry to that TAPP's section in `TAPP_Development_Log.md` documenting the version bump and
   why (point at Rule 5). **Do this even if it feels like overhead** — a prior session in this project
   nearly reverted two intentional design decisions because a cross-TAPP check wasn't cross-referenced
   against existing dev-log entries; don't create the same trap for someone checking this field later.

---

## 8. Scope check before you start

Per Rule 4 (propagation obligation), once this becomes a Rule it must land in every TAPP in the same
revision cycle, not deferred piecemeal. Don't leave some TAPPs updated and others not without explicitly
flagging the gap in the dev log if you have to stop partway through.

## 9. Final checklist

- [ ] Resolved the universal-vs-scoped question (Section 3) with the user
- [ ] Verified actual current TAPP inventory via `find` (not the list in Section 2)
- [ ] `references/conventions.md` updated with the new rule (correct number)
- [ ] `references/precedents.md` updated
- [ ] Every in-scope TAPP CSV patched, version-bumped, xlsx regenerated
- [ ] Dev log entries added per TAPP touched
- [ ] Did NOT touch the stale `LA-ICPMS_TAPP_v13.csv` — only `LA-Q:SF-ICPMS_TAPP_v4.1.csv`
- [ ] `TAPP_Planning_Table.csv` checked for anything else this might affect
