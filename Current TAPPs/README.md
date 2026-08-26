# Current TAPPs

**This folder is a generated mirror. Do not edit anything in it.**

It holds the **latest version of every TAPP** in the library — the CSV (source of truth) and the
xlsx (colour-coded, with a Legends sheet explaining the tier vocabulary and the `Keyed By` keys).
Flat, one version each, refreshed on every version bump under Rule 12.

Share this whole folder with anyone who needs the current TAPPs. It is self-contained and carries no
superseded versions, so there is nothing to sift.

| | |
|---|---|
| TAPPs | 16 |
| Files | 32 (16 CSV + 16 xlsx) |
| As of | 2026-08-26 |

## Where to look for more

| For | Go to |
|---|---|
| Earlier versions of a TAPP | the technique folder in the library root (`EPMA/`, `SEM/`, …) — it keeps every version |
| The specification behind the columns | `Claude Skills for TAPP/references/conventions.md` |
| Why a specific field is the way it is | `Claude Skills for TAPP/references/precedents.md` |
| Which modules a TAPP is composed from | `composed_tapps.json` at the library root |

## Reading a TAPP

Columns A–I are: Metadata Item · Description · Procedure-Level Tier · Analysis-Level Tier · Data Type
· Example / Allowed Content · Comments · Last Update · **Keyed By**. After those come one column per
analytical mode, a sentinel column headed `Literature Assessment`, and then one column per procedure
extracted from the literature.

`Keyed By` states what a field's value repeats over — `(none)` for a scalar, or a key such as
`analyte`, `channel`, `reported property`, `sampling unit`. The xlsx Legends sheet lists the keys used
in that particular TAPP.

## Contents

- `EPMA_TAPP_v30.csv`
- `LA-MC-ICPMS_TAPP_v32.csv`
- `LA-MC-ICPMS_UPb_TAPP_v32.csv`
- `LA-Q-ICP-MS_TAPP_v35.csv`
- `LA-Q-ICP-MS_UPb_TAPP_v35.csv`
- `LA-SF-ICP-MS_TAPP_v34.csv`
- `LA-SF-ICP-MS_UPb_TAPP_v35.csv`
- `Lab-XCT_TAPP_v23.csv`
- `SEM_Composition_TAPP_v28.csv`
- `SEM_FIBSEM_TAPP_v17.csv`
- `SEM_Imaging_TAPP_v17.csv`
- `SEM_TAPP_v28.csv`
- `Solution_MC-ICP-MS_TAPP_v36.csv`
- `Solution_Q-ICP-MS_TAPP_v40.csv`
- `Solution_SF-ICP-MS_TAPP_v38.csv`
- `TEM_TAPP_v25.csv`
