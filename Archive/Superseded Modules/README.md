# Superseded modules

Modules retired from `Claude Skills for TAPP/modules/`. Kept for provenance; **not live** and never composed. A TAPP version composed from one of these records it in `composed_tapps.json` under the name it had at the time.

- `Module_Group1` — retired 2026-08-14, superseded by `Module_Core`, which holds its 18 fields plus the 10 universals that belonged to no module. Retired rather than extended because Group1 used `replace_group` on Group 1, and the new fields sit in Groups 2-6.
- `Module_ReportingCore` — retired 2026-08-14, dissolved into TargetSelection, CalibrationFactor, Blank, Aggregation. It was the only conditional module and the only one that was not all-or-nothing: 9 of 16 consumers held all six fields, and its five blocks had four different consumer footprints. Field definitions were carried over unchanged.
