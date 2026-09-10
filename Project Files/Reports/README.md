# Reports

Generated outputs and correspondence. Nothing here is a TAPP, and nothing here is a source of truth
— the TAPPs live in the technique folders, mirrored in `Current TAPPs/`.

## ⚠ The `*_Mockup.html` files are MOCKUPS

**They are illustrations of what a procedure-registration webform built from a TAPP could look like.
They are not a system, and they are not a record of anything.**

Concretely, what they are not:

- **Not a working form.** There is no backend, no account, no submission and no storage. Every control
  is live enough to demonstrate the interaction, and nothing you type is saved anywhere. Reloading the
  page discards it.
- **Not registered procedures.** The values they open with are *literature extractions* — the
  contents of one procedure column of one TAPP, which is our reading of a published methods section.
  A registered procedure is a different object, with a DOI and an author who registered it. None of
  these is one.
- **Not authored or endorsed by the laboratories or authors named in them.** Ma et al. 2017,
  Neuman et al. 2025 and Zhang et al. 2022 published methods; they did not fill in these forms and
  have not reviewed them. The laboratory and author names shown are part of the extracted content.
- **Not a specification.** The field set, tiers, data types and controlled lists are read out of a
  TAPP at build time, so the TAPP is the specification and the page is one rendering of it. Where
  the two disagree, the TAPP is right. For the schema hand-off, use
  `README_TAPP_for_Schema_Generation.md` at the library root.

Each page carries the same warning on its face — a `Mockup · example content` badge beside the title
and a footer stating that the values are not a registered procedure.

### What they are for

Showing, to someone who has not read a TAPP, what registering a procedure would actually involve —
how many fields, which are mandatory, and above all how `Keyed By` (Column I) changes the shape of an
input. A field keyed by `(none)` is one box; a field keyed by `channel` or `target species` is a
repeating table over a domain that some *other* field has to establish first. That is hard to convey
in a spreadsheet and immediate on a form.

### They go stale on a version bump

| Mockup | Built from | Column | Mode shown |
|---|---|---|---|
| `EPMA_Procedure_Registration_Mockup.html` | `EPMA_TAPP_v68.csv` | 30 — Neuman et al. 2025 | WDS Mapping |
| `EPMA_Point_Analysis_Mockup.html` | `EPMA_TAPP_v68.csv` | 19 — Ma et al. 2017 | WDS Point Analysis |
| `LA-MC-ICP-MS_Spot_Mockup.html` | `LA-MC-ICPMS_TAPP_v74.csv` | 14 — Zhang et al. 2022 | Spot |

A mockup is a snapshot of the TAPP it was built from. Bump that TAPP and the page is out of date
until it is rebuilt — the version it was built from is printed in its own masthead, so check there
before trusting a page you did not just generate. Nothing validates this automatically; there is no
`rule12`-style staleness check for mockups.

The one non-obvious caveat: `LA-MC-ICP-MS_Spot_Mockup.html` is set to **Spot** mode, but the library's
only LA-MC-ICP-MS literature assessment is a **Transect** procedure. Fields that do not apply to Spot
are flagged on the page rather than silently carried, but the prefilled content is a transect
procedure's.

### Rebuilding

```
cd "Project Files/Reports" && python3 build_form.py cfg.json
```

Runnable from any working directory — it resolves the library root, its two templates and its
output paths from its own file location. It did not on 2026-09-09 before being committed: the
library root was hardcoded to one machine's home directory and the templates were opened relative
to the cwd, so it worked only when run from this folder. Fixed for the same reason
`check_field_ownership.py` exists.

`build_form.py` reads `cfg.json` — which TAPP, which literature column, which mode, plus any
per-member value overrides — and renders each page from `_head.html` (styles) and `_body.html`
(markup and the render logic). Adding a fourth mockup for another TAPP is a `cfg.json` entry, not new
code. `build_form.py` resolves TAPPs through `Current TAPPs/`, so it always sees the latest version.

Known limitation: domain members are parsed out of free-text Column F and literature cells by
splitting on `;` and `,`, which is approximate. `Natural clinopyroxenes NHB-9 and YY12-01` reads as
one standard rather than two, and a long `Acquisition Pass` value can split across two chips. The
TAPP is unaffected — this is the page's parser, not the data.

## The other files

| File | What it is |
|---|---|
| `TAPP_Lint_Report_*.csv` | dated `validate_tapp.py --csv` output, kept as a record of what the library looked like on that date. Four consecutive reports were saved 2026-08-07 to -08-12, then the practice lapsed until 2026-09-10. One row per finding; the console collapses repeated checks but the CSV does not. A report is a snapshot, never a substitute for re-running the validator. |
| `UPSTREAM_RESPONSE_*.md` | correspondence with the schema developer. Records what was asked and what was answered — see `Claude Skills for TAPP/analysis/` for the reconciliation behind them. |
