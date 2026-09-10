# Superseded TAPPs — 2026-09-10

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.


## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v65` | `v66` |
| `LA-MC-ICPMS_TAPP_v72` | `v73` |
| `LA-MC-ICPMS_UPb_TAPP_v71` | `v72` |
| `LA-Q-ICP-MS_TAPP_v74` | `v75` |
| `LA-Q-ICP-MS_UPb_TAPP_v74` | `v75` |
| `LA-SF-ICP-MS_TAPP_v71` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v72` | `v73` |
| `SEM_Composition_TAPP_v61` | `v62` |
| `SEM_TAPP_v62` | `v63` |
| `Solution_MC-ICP-MS_TAPP_v71` | `v72` |
| `Solution_Q-ICP-MS_TAPP_v77` | `v78` |
| `Solution_SF-ICP-MS_TAPP_v73` | `v74` |
| `TEM_TAPP_v50` | `v51` |

13 version(s), 26 file(s) (CSV + xlsx).

## Why

The `monitored property` retrofit — `retrofit_monitored_property_20260910.py`, executing the
`monitored property` half of `../../Project Files/Design Notes/Proposal_Monitored_Property_2026-09-10.md`
(whose §10 withdrew the `detector` half the same day, for want of a single attested consumer).

Every field keyed `channel` moved to `monitored property`, and every
`defines: channel per target species` to `defines: monitored property per target species` — 29 fields,
126 cells, 13 TAPPs. No field in the library is now keyed `channel`; the key stays in the vocabulary
for the swept-axis techniques not yet built (Rule 7.2, third note, 2026-09-10).

Column I is module-owned for 13 of the 29 fields, so those were edited in the module and recomposed
rather than hand-edited (Rule 6.6): **Module_CollisionCell v4→v5** (5 fields), **Module_ICPMS v12→v13**
(4), **Module_MCICPMS v8→v9** (4). Nine TAPPs were recomposed; four — EPMA, SEM, SEM_Composition, TEM
— carry only TAPP-owned affected fields and were bumped without recomposition.

**Deliberately not done in this pass**, both recorded in the script's docstring: `Ion Counter Dead
Time` stays uniform rather than becoming `(none)` in the six single-collector TAPPs, because the field
is Module_ICPMS-owned and Rule 6.5 forbids a module expressing two Column I values; and the §4
restructure (demoting `Collector Configuration` and `WDS Spectrometer Channel` to attributes,
promoting `Monitored Masses` to definer) is untouched, since it needs two new fields and a Rule 6
admission decision. The four definers keep their `per target species` parent, so the mass-to-element
binding is preserved exactly.

## Verification

`validate_tapp.py` **0 ERROR / 0 WARN / 39 INFO** — the same 39 pre-existing registered divergences as
before the retrofit. `audit_keys_vs_literature.py` **0 NEW**; its axis detector had been updated the
same day to report `monitored property` and `detector` separately instead of one conflated `channel`
tag, so the re-key raises no artifacts. `compose_tapp.py --check` reports **MATCH on all 9** recomposed
TAPPs.

A cell-level diff of every TAPP against its predecessor shows **exactly two columns changed — `Keyed
By` (126 cells) and `Last Update` (126)** — and no row counts altered. This was a pure key rename: every
Column I value changed name, none changed shape.

Four generated artefacts were refreshed in the same pass, each of which the validator would otherwise
have failed the save on: `composed_tapps.json`, `TAPP_Module_Register.csv`,
`README_TAPP_for_Schema_Generation.md` (its counts are generated and `tapp-save.sh` refuses a stale
block), and the Rule 12 mirror.
