# Superseded TAPPs — 2026-10-01

Retained for reference and provenance. **Do not develop against these, and do not register
procedures using them.** Folders beginning `Superseded` are excluded from `validate_tapp.py`
discovery.

## What was superseded, and by what

| Superseded | Successor |
|---|---|
| `EPMA_TAPP_v87` | `v88` |
| `SEM_Composition_TAPP_v82` | `v83` |
| `SEM_TAPP_v84` | `v85` |

3 version(s), 6 file(s) (CSV + xlsx).

## Why

**Counting times keyed per target material.** `Peak Counting Time` and `Background Counting Time` were
re-keyed from `monitored property` to `target material x monitored property`. The fields are TAPP-owned,
and the re-key applies to EPMA, SEM and SEM_Composition alike (Rule 2).

Zega+2025 sets its counting times per phase, with no element named:
- silicates, sulfides and oxides: 20 s peak and 10 s on each background;
- phosphates: 20 s and 10 s;
- carbonates: 10 s and 5 s.

The times change with the phase, as the beam current and diameter do, "to minimize possible beam damage
effects". Gap 1 (2026-09-28) keyed the beam conditions per target material, but held the counting times
"until a second procedure attests them". The user decided on 2026-10-01 to re-key them now.

Only a procedure that analyses several materials *and* states its counting times can test a material axis.
Ma+2017, Frank+2023 and Barnes+2025 state times, but one set for all materials. Zega is the one test, and
it attests the axis. The 2026-09-29 standards re-key was decided on one paper (McCoy+2025_UA) in the same
way.

**Cells.** Five stated EPMA cells became two-level:
- Ma+2017 (peak and background), Frank+2023 and Barnes+2025: `all [ ... ]`, with their entries unchanged.
- Zega+2025: its per-phase statement, which until now was `N` with the times in commentary. For example
  `silicates, sulfides, oxides [all: 20 s]; phosphates [all: 20 s]; carbonates [all: 10 s]`. The inner
  `all` is used because the paper names no element.

SEM and SEM_Composition have no stated cells; only their key changed.

Applied by `Project Files/Scripts/rekey_counting_time_20261001.py`. The EPMA form mockups (`cfg.json`, the
Reports README) and the five review workbooks were rebuilt at v88, and the v87 workbooks were removed.

## Verification

- Simulated before applying. The validator's per-TAPP and cross-TAPP checks on the simulated v88, v85
  and v83 reported no ERROR or WARN.
- After applying: `compose_tapp.py --check` 16 of 16 match; `validate_tapp.py` 0 ERROR, 0 WARN, once the
  EPMA reports were rebuilt; `audit_keys_vs_literature.py` 0 NEW.
- The six non-marker cells parse two-level, and Zega's four stated times sit under their phases.
- The Ma+2017 mockup still prefills `Peak Counting Time` as `20 s` under the new key.
- The 2026-09-29 EPMA round-trip scorer predates two-level cells, and its facts assume the old key. It
  was left unchanged as a dated record of v84–v86.
- Changed: Column I and Last Update of two fields in three TAPPs, and five EPMA literature cells. No
  description, tier, data type or Column F changed.
