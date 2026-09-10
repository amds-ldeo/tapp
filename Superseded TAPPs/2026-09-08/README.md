# Superseded TAPPs — 2026-09-08

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

> **Reconstructed 2026-09-10.** This folder was parked before bump scripts wrote a README,
> so the notes below were assembled afterwards from the dated entries in
> `../../Project Files/Design Notes/TAPP_Development_Log.md`, the dated commit subjects in
> git, and the dated patch scripts in `../../Project Files/Scripts/`. It is not a
> contemporaneous record.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v61` | `v65` |
| `EPMA_TAPP_v62` | `v65` |
| `LA-MC-ICPMS_TAPP_v69` | `v72` |
| `LA-MC-ICPMS_UPb_TAPP_v69` | `v71` |
| `LA-Q-ICP-MS_TAPP_v72` | `v74` |
| `LA-Q-ICP-MS_UPb_TAPP_v72` | `v74` |
| `LA-SF-ICP-MS_TAPP_v69` | `v71` |
| `LA-SF-ICP-MS_UPb_TAPP_v70` | `v72` |
| `SEM_Composition_TAPP_v59` | `v61` |
| `SEM_TAPP_v60` | `v62` |
| `Solution_MC-ICP-MS_TAPP_v68` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v69` | `v71` |
| `Solution_MC-ICP-MS_TAPP_v70` | `v71` |
| `Solution_Q-ICP-MS_TAPP_v74` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v75` | `v77` |
| `Solution_Q-ICP-MS_TAPP_v76` | `v77` |
| `Solution_SF-ICP-MS_TAPP_v70` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v71` | `v73` |
| `Solution_SF-ICP-MS_TAPP_v72` | `v73` |

19 version(s), 38 file(s) (CSV + xlsx).

## Why

`acquisition pass` minted, the `Digestion Step` retype and its Phase 3 backfill, and
a reference-file reconciliation — 22 commits.

- **`Mint acquisition pass: 15 consumers, 9 ICP-MS TAPPs, 92 rows`** —
  `bump_acquisition_pass_20260908.py`. The key had been retired on 2026-08-11 for want of a consumer
  and was reinstated when a survey found 69 pass-structured cells across 4 TAPPs. **EPMA and SEM were
  deliberately deferred**, and `Record the named falsifier for the EPMA/SEM acquisition-pass deferral`
  is the commit that wrote down what would reverse that.
- **`Number of Digestion Steps` → `Digestion Step`, Integer → Text (free)** —
  `retype_digestion_step_20260908.py`, then `phase3_digestion_step_20260908.py` and
  `reextract_digestion_step_20260908.py` filled it from the sources, **falsifying 6 neighbouring
  cells** in the process.
- **`Reconcile the reference files with four days of passes; the schema spec was wrong`** — the spec
  handed to the schema developer had drifted materially. `Generate the schema spec's counts; refuse a
  stale block at save time` is the fix that made it structural: `tapp-save.sh` now refuses a save
  whose generated counts are stale.
- **`Backfill the development log: nine entries, 2026-08-28 to 2026-09-08`** — which is why the
  entries for this date exist at all.
- Three commits record **corrected reasoning** rather than changed files: `Resolve the SEM 7.4c snag
  — it dissolves, and it was my error`, `Settle the scalar-summary pattern: both KEEP, and the test I
  proposed was wrong`, and `4A rewritten: the definer ENUMERATES passes`.

## Verification

Not recorded as a validator run. Two structural gates were added on this date
instead: generated counts in the schema spec, and `tapp-save.sh` refusing a save that would commit
them stale.

---

No per-date `validate_tapp.py` output is asserted where none was recorded — see the Verification
section. The library validates 0 ERROR / 0 WARN as of 2026-09-10, which says nothing about its
state on the date this folder was parked.
