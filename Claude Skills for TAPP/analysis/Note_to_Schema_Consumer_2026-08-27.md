# Follow-up note for amds-ldeo/tapp issues #1 and #3 — DRAFT, NOT SENT

**Status: unsent.** This is a draft for the maintainer to post (or not). It supersedes the
`issue1_reply.md` / `issue3_reply.md` drafts in the 2026-08-25 scratchpad, which are stale: they
quote *34 attested Detection Limit cells* where `precedents.md` now records 42, and they were
written before the Column E uniformity pass moved six more cells.

## What the reporter needs to know

Both issues are closed. The reporter sized their consumer-side work against a
**`Numeric + unit` cell count of 35**, measured before our fix. That number is stale, and it is
stale in the direction that costs them: the count is now **42**, not 35.

### The count, measured from git rather than inferred

| Point in history | `Numeric + unit` | `Numeric + unit / Text` | Total |
|---|---|---|---|
| `2517677~1` — before the Detection Limit fix | 23 | 12 | **35** |
| `2517677` — immediately after it | 23 | 22 | **45** |
| `HEAD` (2026-08-27) | 19 | 23 | **42** |

**45 was correct when it was first written down and is no longer correct.** Between that commit
and today, six cells left the family and three joined:

*Left* — `Beam Diameter`, `Beam Raster Dimensions` and `Step Size / Pixel Size` in both `SEM` and
`SEM_Composition`, retyped to `Numeric (µm) / Text` and `Numeric pair (µm x µm)` so that the three
electron-beam tables agree with EPMA. This was the Column E uniformity pass, not a reversal of the
#1 fix.

*Joined* — EPMA's `Dwell Time per Pixel` and `Map Area`, and TEM's `EELS Detection Limit`.

So the direction of travel is unchanged and the reporter's original point stands: consolidating the
duplicated parameters into one shared definition is now worth more than it was when they measured,
because the family it collapses is larger. The exact figure to plan against is **42**, made up of
19 cells typed `Numeric + unit` and 23 typed `Numeric + unit / Text`.

### Why the two forms are still distinct

`Numeric + unit` requires `schema:unitText`; `Numeric + unit / Text` requires it on the numeric
branch but admits a text alternative, because 10 of the 42 attested literature cells behind these
fields are ranges or qualitative statements. Collapsing the two forms into one would re-introduce
the over-tightening that #1 existed to undo. They should stay two shapes.

## Housekeeping worth mentioning

Issue #1 was auto-closed twice by a commit keyword rather than by a decision to close. If the
reporter is still watching the thread, saying so directly is better than leaving it to look like
the report was dismissed.
