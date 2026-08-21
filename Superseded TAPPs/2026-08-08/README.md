# Superseded TAPPs — retired 2026-08-08

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** They are excluded from `validate_tapp.py` discovery.

## What was retired, and why

Both folders held LA-ICP-MS U-Th-Pb geochronology as a standalone TAPP. That framing turned out
to be the problem rather than the solution: they used **instrument columns** (Q-ICP-MS /
SF-ICP-MS / MC-ICP-MS) where every other TAPP uses analytical mode columns, because they were
trying to be an instrument TAPP and a dating-system TAPP at once.

Geochronology is not a technique. It is a **reported-quantity class** produced by applying a
dating system to an instrument. So the content was decomposed:

| Original content | Where it lives now |
|---|---|
| Q/SF instrument content | `LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_TAPP_v5.csv` |
| MC instrument content (13 fields) | `Module_MCICPMS`, consumed by `LA-MC-ICP-MS` and `Solution MC-ICP-MS` |
| Laser front end (18 fields) | `Module_LaserAblation` |
| Cross-system geochronology fields (6) | `Module_Geochronology` |
| U-Pb-specific fields and examples | `Module_UPb` |
| Fields general to all techniques (6) | `Module_ReportingCore` |
| 8 generic LA-ICP-MS fields the geochronology TAPP had and LA-Q/SF lacked | harvested into `LA-Q_SF-ICP-MS` (2026-08-08) |

The equivalent registerable profiles are now:

- `LA-Q_SF-ICP-MS/LA-Q_SF-ICPMS_UPb_TAPP_v5.csv` — LA-Q/SF-ICP-MS × Geochronology × U-Pb
- `LA-MC-ICP-MS/LA-MC-ICPMS_UPb_TAPP_v1.csv` — LA-MC-ICP-MS × Geochronology × U-Pb

## Verification performed before retirement

All **124 fields** in each TAPP were checked against the two composed U-Pb variants, allowing for
fields renamed during harvest and harmonisation. **Zero uncovered.** Neither TAPP carried any
literature assessment columns, so no Phase 3 extraction was lost.

## Folders

**`LA-ICP-MS Geochronology (General)/`** — the production attempt, v1–v2. Superseded by the two
composed variants above.

**`LA-ICP-MS Geochronology (Horstwood Test)/`** — the comparison exercise that started this work,
v1–v8, derived from Horstwood et al. (2016). Also holds the experiment report, the
Horstwood-vs-LA-Q/SF comparison, and the experimental per-instrument sub-TAPPs. Historically the
origin of the "Constants and Reference Values Used" field, now Rule 5.

Analysis artifacts derived from these TAPPs, and still cited by the conventions, were moved to
`../Claude Skills for TAPP/analysis/` rather than archived here.
