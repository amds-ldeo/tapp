#!/usr/bin/env python3
"""
patch_lamcicpms_zhang2022_litassess_20260810.py
-----------------------------------------------
Phase 3 (start) for LA-MC-ICP-MS: transfer the Zhang et al. 2022
(At. Spectrosc. 43) literature assessment column out of the retired
LA-ICP-MS stale branch and into the LA-MC-ICP-MS TAPP.

  source : Superseded TAPPs (2026-08-10)/LA-ICP-MS (stale branch)/LA-ICPMS_TAPP_v13.csv
           column index 22 — "Zhang et al. 2022 / (At. Spectrosc. 43) / Lunar meteorite
           silicates / (Rb-Sr geochronology) / Line scan (transect) / fs-LA-MC-ICP-MS /
           China Univ. of Geosciences"  — 89 filled cells
  target : LA-MC-ICP-MS/LA-MC-ICPMS_TAPP_v1.csv  ->  LA-MC-ICPMS_TAPP_v2.csv

This is a FIELD-NAME-MATCHED TRANSFER, not a column copy. v13 (107 fields) and
LA-MC-ICPMS v1 (132 fields) have different field sets. Every source cell is matched
by Metadata Item name; cells with no name match are routed explicitly by the RENAMED /
SPLIT tables below, or reported as unplaced. Nothing is dropped silently.

Verification performed before writing this patch (per the recorded lesson that a
name-only diff over-reports matches in both directions):

  * All 85 name-matched fields had their Column B descriptions compared.
    83 are byte-identical. The 2 that differ are compatible refinements in v1:
      - Ablation Cell Type : v1 adds internal volume / washout rationale
      - RF Power           : v1 relaxes "fixed, cannot be changed" to a registered
                             target the analyst may fine-adjust (D=Editable)
    Neither changes what the Zhang value means. Both transfer unchanged.

  * The 4 source cells with no name match were checked against v1 descriptions and
    against Table 1 of the source PDF (LA-MC-ICP-MS/Seed Papers/Zhang et al 2022 -
    in situ Rb-Sr LA-MC-ICP-MS.pdf, read in this session):
      - "Auxiliary and Cool Gas Flow Rates" -> SPLIT. v13 held one field for both
        gases; v1 holds two. Table 1 p.2 lists them as two separate rows
        ("Cool gas flow 16.0 L min-1", "Auxiliary gas flow 0.80 L min-1"), so the
        split is how the source itself states them.
      - "Drift Monitor Frequency" -> "Calibration Standard Measurement Frequency".
        Same concept, renamed: v1's description states it "defines the bracketing
        interval between calibration standard ablations used to monitor and correct
        for instrumental drift".
      - "Spectrometer Dwell Time" -> "Integration Time per Cycle". NOT the same
        concept in the abstract — v13's field is per-mass dwell on a sequential
        analyser — but the recorded Zhang value is literally "0.524 s integration
        time per cycle", which is Table 1's "Integration Time (s) 0.524 s" row and
        is exactly what v1's simultaneous-collection field asks for.
      - "Pulse/Analog Detector Nonlinearity Correction" -> NO DESTINATION. v1 has no
        such field, and its "Ion Counter Dead Time" description explicitly states it
        is distinct from this one, so it is not a substitute. The value was
        "N/A (MC-ICP-MS ... no pulse/analog transition)" — i.e. the field does not
        apply to this technique at all, which is why the LA-MC-ICP-MS TAPP omits it.
        Reported, not transferred.

  * Direction-2 over-report checked: the source "Analyte" cell is a valid name AND
    description match and transfers verbatim, but its content is the paper's Table 1
    "Cup-configuration" row. v1 has a dedicated "Collector Configuration" field that
    this content would also populate. NOT filled here — that is re-extraction, not
    transfer. Reported as an immediate Phase 3 follow-up.

Group header rows receive 'N' in the new column per references/lit_assessment.md
("Group header rows: use N in all procedure columns"). The source column left them
blank; this is a deliberate normalisation to the documented convention and to the
dominant library practice (EPMA, SEM, TEM, Solution Q/SF all use N).

Blank separator rows stay blank. Column H (Last Update) is NOT touched: adding an
assessment column is not a substantive edit to any field definition.
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

SRC = os.path.join(
    ROOT,
    "Superseded TAPPs (2026-08-10)",
    "LA-ICP-MS (stale branch)",
    "LA-ICPMS_TAPP_v13.csv",
)
SRC_COL = 22

DST_IN = os.path.join(ROOT, "LA-MC-ICP-MS", "LA-MC-ICPMS_TAPP_v1.csv")
DST_OUT = os.path.join(ROOT, "LA-MC-ICP-MS", "LA-MC-ICPMS_TAPP_v2.csv")

SENTINEL = "Literature Assessment"

# source field name -> destination field name (concept match, different name)
RENAMED = {
    "Drift Monitor Frequency": "Calibration Standard Measurement Frequency",
    "Spectrometer Dwell Time": "Integration Time per Cycle",
}

# source field name -> {destination field name: value} (one source field, two dest fields)
SPLIT = {
    "Auxiliary and Cool Gas Flow Rates": {
        "Coolant (Plasma) Gas Flow Rate": "Cool gas: 16.0 l min⁻¹ Ar",
        "Auxiliary Gas Flow Rate": "Auxiliary: 0.80 l min⁻¹ Ar",
    }
}

# source field names deliberately not transferred (no destination exists)
NO_DESTINATION = {"Pulse/Analog Detector Nonlinearity Correction"}


def is_group_header(name):
    return name.strip()[:2] in ("1.", "2.", "3.", "4.", "5.", "6.")


def main():
    dry = "--dry-run" in sys.argv

    with open(SRC, newline="", encoding="utf-8-sig") as f:
        src_rows = list(csv.reader(f))
    with open(DST_IN, newline="", encoding="utf-8-sig") as f:
        dst_rows = list(csv.reader(f))

    header_text = src_rows[0][SRC_COL]

    # --- harvest source column, keyed by Metadata Item -------------------------
    src_vals = {}
    for r in src_rows[1:]:
        name = r[0].strip()
        val = r[SRC_COL].strip() if len(r) > SRC_COL else ""
        if name and val:
            src_vals[name] = val
    print(f"source column      : {header_text.splitlines()[0]} ...")
    print(f"source filled cells: {len(src_vals)}")
    assert len(src_vals) == 89, f"expected 89 filled source cells, found {len(src_vals)}"

    # --- destination structure -------------------------------------------------
    dst_header = dst_rows[0]
    assert SENTINEL in dst_header, "destination has no sentinel column"
    sent_idx = dst_header.index(SENTINEL)
    n_lit = len(dst_header) - sent_idx - 1
    print(f"destination        : {os.path.basename(DST_IN)}")
    print(f"sentinel at index  : {sent_idx}  (existing lit assessment columns: {n_lit})")
    assert n_lit == 0, f"expected 0 existing lit columns, found {n_lit}"

    dst_names = [r[0].strip() for r in dst_rows[1:]]
    dst_index = {n: i + 1 for i, n in enumerate(dst_names) if n}

    # --- build the new column --------------------------------------------------
    new_col = [""] * len(dst_rows)
    new_col[0] = header_text

    direct, renamed_done, split_done, unplaced = [], [], [], []

    for name, val in src_vals.items():
        if name in NO_DESTINATION:
            unplaced.append((name, val, "field does not exist in LA-MC-ICP-MS"))
            continue
        if name in SPLIT:
            for dname, dval in SPLIT[name].items():
                if dname not in dst_index:
                    unplaced.append((name, val, f"split target '{dname}' missing"))
                    break
                new_col[dst_index[dname]] = dval
                split_done.append((name, dname, dval))
            continue
        dname = RENAMED.get(name, name)
        if dname not in dst_index:
            unplaced.append((name, val, f"no destination field '{dname}'"))
            continue
        new_col[dst_index[dname]] = val
        (renamed_done if name in RENAMED else direct).append((name, dname, val))

    filled = sum(1 for i, v in enumerate(new_col) if i > 0 and v)

    # group header rows get N per lit_assessment.md
    gh = 0
    for i, r in enumerate(dst_rows[1:], 1):
        if is_group_header(r[0]):
            assert not new_col[i], f"group header row {i} already carries a value"
            new_col[i] = "N"
            gh += 1

    # --- report ----------------------------------------------------------------
    print()
    print("=" * 90)
    print(f"DIRECT name matches transferred : {len(direct)}")
    print(f"RENAMED (concept match)         : {len(renamed_done)}")
    for s, d, v in renamed_done:
        print(f"    '{s}'  ->  '{d}'")
        print(f"        {v[:100]}")
    print(f"SPLIT (1 source -> 2 dest)      : {len(split_done)}")
    for s, d, v in split_done:
        print(f"    '{s}'  ->  '{d}' = {v}")
    print(f"UNPLACED (reported, not dropped): {len(unplaced)}")
    for s, v, why in unplaced:
        print(f"    '{s}' — {why}")
        print(f"        value was: {v}")
    print(f"Group header rows set to 'N'    : {gh}")

    consumed = len(direct) + len(renamed_done) + len(SPLIT) + len(unplaced)
    print()
    print(f"source cells accounted for : {consumed} / 89")
    print(f"destination cells filled   : {filled} (+ {gh} group-header 'N')")
    assert consumed == 89, "source cell accounting does not balance"
    assert filled == 85 + 2 + 2, f"expected 89 destination cells, got {filled}"

    # v1 fields left empty by this transfer
    empty = [
        n
        for i, n in enumerate(dst_names, 1)
        if n and not is_group_header(n) and not new_col[i]
    ]
    print()
    print(f"LA-MC-ICP-MS fields with no Zhang value ({len(empty)}) — left blank:")
    for n in empty:
        print(f"    - {n}")

    if dry:
        print("\n[dry run] nothing written")
        return

    # --- write -----------------------------------------------------------------
    out = []
    for i, r in enumerate(dst_rows):
        r = list(r) + [""] * (len(dst_header) - len(r))
        out.append(r + [new_col[i]])

    widths = {len(r) for r in out}
    assert widths == {len(dst_header) + 1}, f"ragged rows: {widths}"

    with open(DST_OUT, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(out)
    print(f"\nwrote {DST_OUT}  ({len(out)} rows x {len(out[0])} cols)")


if __name__ == "__main__":
    main()
