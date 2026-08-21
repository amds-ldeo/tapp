# Superseded TAPPs — retired 2026-08-10

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## `LA-ICP-MS (stale branch)/`

The `LA-ICP-MS` and `LA-Q_SF-ICP-MS` folders were never two TAPPs. They are **one continuous
lineage** under two folder names, and the split was an artifact of renaming the technique from
"LA-ICP-MS" to "LA-Q/SF-ICP-MS" partway through development.

The branches were kept in exact parallel sync through two rounds — `LA-ICPMS_TAPP_v11` and
`LA-Q_SF-ICPMS_TAPP_v1` have a 100% identical field set, as do `v12` and `v2`. **After that sync
point only `LA-Q_SF-ICP-MS` received real development.** `v13` is `v12`'s content plus the mechanical
VIM3 terminology pass (2026-07-24) and the Group 1 composition (2026-08-08). No organic development
happened between v12 and v13.

The problem was that `LA-ICPMS_TAPP_v13.csv` *looked* current — highest version number in its folder,
recent timestamp — while being frozen. That had already caused one real error: a comparison workbook
built against the wrong file and rebuilt. Archiving it removes the trap.

**Superseded by:** `LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv`

### Verification performed before retirement

All **95 fields** in v13 checked against LA-Q/SF-ICP-MS v5 (125 fields). **Zero uncovered.**

A name-only diff initially reported three uncovered fields. All three dissolved on reading the
descriptions — the same failure mode recorded in the 2026-08-08 entry ("name similarity is not
evidence of field identity"), here running in the opposite direction:

| v13 field | Status in LA-Q/SF v5 |
|---|---|
| `Auxiliary and Cool Gas Flow Rates` | Covered by **two** fields — `Coolant (Plasma) Gas Flow Rate` and `Auxiliary Gas Flow Rate`. v13's compound field is the inferior form. |
| `Spectrometer Dwell Time` | Renamed to `Dwell Time per Mass`. **Byte-identical description**, identical C/D tiers. |
| `Drift Monitor Frequency` | Covered by `Calibration Standard Measurement Frequency`, which explicitly defines the bracketing interval used to monitor and correct instrument drift. |

### Literature assessment — read this before assuming nothing was lost

Unlike the 2026-08-08 retirements, **this TAPP carried literature assessment content**: 16 columns,
1,436 filled cells, against LA-Q/SF v5's 13 columns. Thirteen correspond one-to-one.

The **three extra columns (89 filled cells each, 267 total) survive only in the archived
`LA-ICPMS_TAPP_v13.csv` in this folder.** They were dropped from LA-Q/SF deliberately and correctly —
each covers an instrument outside a Q/SF TAPP's scope — and each maps to a TAPP in the planning
table:

| Archived column | Instrument | Destination |
|---|---|---|
| Chernonozhkin et al. 2024 (JAAS 39), micrometeorites | LA-ICP-ToF-MS | Row **7b** — planned, not built |
| Masuda et al. 2024 (M&PS 59), Allende CAIs | TQ (iCAP TQ, KED mode) | Row **7c** — planned, not built; the planning table already names this paper as its seed |
| Zhang et al. 2022 (At. Spectrosc. 43), lunar meteorite Rb-Sr | fs-LA-MC-ICP-MS | Row **7a** — **exists** at v1 with **zero** literature assessment columns |

The third is the live one. `LA-MC-ICPMS_TAPP_v1` used this exact paper for its Phase 0 coverage
audit and has no Phase 3 content at all, so this column is directly usable extraction for the
outstanding LA-MC-ICP-MS Phase 3 — a field-name-matched transfer, not a column copy, since the two
TAPPs' field sets differ. **Not performed here**, to avoid folding a Phase 3 step into a retirement.

## What deliberately did NOT move

`LA-ICP-MS/Validation Papers/` and the loose method PDFs **stay in `LA-ICP-MS/`**. Two reasons:

1. `paper_registry.csv` records `LA-ICP-MS/Validation Papers` as the location of **10 papers**.
2. Those papers are the Phase 3 sources for the **live** LA-Q/SF-ICP-MS TAPP, which has no papers
   folder of its own. Archiving them would file the current TAPP's provenance under "superseded".

`LA-ICP-MS/` is therefore retained as a source-paper folder and carries its own README saying so.
