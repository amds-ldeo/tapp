# Superseded TAPPs — 2026-09-10

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.


## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v65` | `v67` |
| `EPMA_TAPP_v66` | `v67` |
| `LA-MC-ICPMS_TAPP_v72` | `v74` |
| `LA-MC-ICPMS_TAPP_v73` | `v74` |
| `LA-MC-ICPMS_UPb_TAPP_v71` | `v73` |
| `LA-MC-ICPMS_UPb_TAPP_v72` | `v73` |
| `LA-Q-ICP-MS_TAPP_v74` | `v75` |
| `LA-Q-ICP-MS_UPb_TAPP_v74` | `v75` |
| `LA-SF-ICP-MS_TAPP_v71` | `v72` |
| `LA-SF-ICP-MS_UPb_TAPP_v72` | `v73` |
| `SEM_Composition_TAPP_v61` | `v63` |
| `SEM_Composition_TAPP_v62` | `v63` |
| `SEM_TAPP_v62` | `v64` |
| `SEM_TAPP_v63` | `v64` |
| `Solution_MC-ICP-MS_TAPP_v71` | `v73` |
| `Solution_MC-ICP-MS_TAPP_v72` | `v73` |
| `Solution_Q-ICP-MS_TAPP_v77` | `v78` |
| `Solution_SF-ICP-MS_TAPP_v73` | `v74` |
| `TEM_TAPP_v50` | `v51` |

19 version(s), 38 file(s) (CSV + xlsx).

## Why

Two passes on the same day, both executing
`../../Project Files/Design Notes/Proposal_Monitored_Property_2026-09-10.md`. Several TAPPs appear
twice because both passes touched them.

**Pass 1 — the key rename.** `retrofit_monitored_property_20260910.py`. Every field keyed `channel`
moved to `monitored property`, and every `defines: channel per target species` to
`defines: monitored property per target species` — 29 fields, 126 cells, 13 TAPPs. No field in the
library is keyed `channel` now; the key stays in the vocabulary for the swept-axis techniques not yet
built (Rule 7.2, third note). Column I is module-owned for 13 of the 29 fields, so those were edited
in the module and recomposed rather than hand-edited (Rule 6.6): Module_CollisionCell v4→v5,
Module_ICPMS v12→v13, Module_MCICPMS v8→v9. A cell-level diff showed **exactly two columns changed —
`Keyed By` (126) and `Last Update` (126)** — with no row counts altered. A pure rename: every value
changed name, none changed shape.

**Pass 2 — §4, the definer moves to the measurand list.**
`restructure_monitored_property_20260910.py`, 6 TAPPs, Module_MCICPMS v9→v10.

- `Collector Configuration` stopped being the definer and became an attribute keyed
  `monitored property` — which collector each monitored mass was assigned to.
- `Monitored Masses` became the definer in all nine ICP-MS TAPPs, promoted from `target species` in
  the two LA-MC TAPPs and **added to Solution MC-ICP-MS**, which had lacked it entirely.
- `WDS Spectrometer Channel` likewise stopped being the definer, and **`Monitored Elements`** — a new
  field — took that role in EPMA, SEM and SEM_Composition.

**This dissolved a registered divergence rather than adding one.** `Monitored Masses` had been the
definer in the six single-collector TAPPs but a plain `target species` consumer in LA-MC, and the
register recorded why: *"defines … where there is no collector array; target species where the cup
array defines the channel."* With the mass list as definer everywhere, that entry has no cause. It is
marked **dormant** in `KEYED_BY_TECHNIQUE_DEPENDENT`, not deleted — the treatment
`Secondary Reference Materials` already has. `validate_tapp.py` INFO consequently fell from 39 to 38.

**`Monitored Elements` is TAPP-owned, not a module field.** All four of its siblings —
`WDS Spectrometer Channel`, `X-ray Line`, `Diffracting Crystal`, `WDS PHA Setting` — are TAPP-owned;
the WDS block was never modularised, and admitting one member to a module while the rest stayed
behind would split the block across two ownership regimes for no gain. Its Columns A–E and I are
byte-identical in all three TAPPs, verified, so the cross-TAPP uniformity checks stay quiet.

## Verification

`validate_tapp.py` **0 ERROR / 0 WARN**, INFO 39 → 38 (the dissolved divergence).
`audit_keys_vs_literature.py` **0 NEW**. `compose_tapp.py --check` **MATCH on all 9** recomposed TAPPs
in pass 1. Every one of the 13 TAPPs that uses `monitored property` now has **exactly one definer** —
`Monitored Masses` in the nine ICP-MS, `Monitored Elements` in the three electron-beam, `EELS Edges`
in TEM — which is the uniform shape the restructure existed to produce. Pass 2's diff: 4 rows added,
4 `Keyed By` cells changed.

Generated artefacts refreshed in both passes: `composed_tapps.json`, `TAPP_Module_Register.csv`,
`README_TAPP_for_Schema_Generation.md`, the Rule 12 mirror, and the three webform mockups.

## Outstanding

**Phase 3 for the two new fields.** Their literature cells are **blank, deliberately** — 15 EPMA
procedures for `Monitored Elements`, 8 for `Monitored Masses` in Solution MC-ICP-MS. Blank is the
honest value here: `lit_assessment.md` forbids blanks in *a column being assessed*, and this is the
other case — a field added after those columns were assessed, where blank means "not yet assessed
against this source" and `N` would misreport it as "assessed, not stated". Deriving the values from
the neighbouring `Target Species` or `X-ray Line` cells is specifically NOT the way to fill them; that
is the folded-in-neighbour defect repaired on 2026-09-09.

**`Ion Counter Dead Time` stays uniform**, not `(none)` in the six single-collector TAPPs. It is
Module_ICPMS-owned and Rule 6.5 forbids a module expressing two Column I values, so the fix needs the
field taken out of the module first. Zero attestations in the corpus, so nothing decides it today.
