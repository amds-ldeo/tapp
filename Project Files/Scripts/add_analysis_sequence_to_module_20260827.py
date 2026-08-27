#!/usr/bin/env python3
"""Move `Analysis Sequence` into Module_ICPMS (38 -> 39 fields), completing the 26.

It was the one field of the 26 ICP-MS-specific descriptions left out on 2026-08-26, because its
Analysis-Level Tier split Editable (6 LA) / Read-Only (3 Solution) and precedents.md recorded that
divergence as knowingly unresolved. The manifest's own decision log says so: "it is not this
module's to settle." That divergence was settled on 2026-08-27 (D -> Editable across all nine,
decided by the shared Column B), so the blocker is discharged.

**This changes no TAPP content.** All six module-owned columns (A, B, C, D, E, I) are already
byte-identical across the nine consumers, so composition updates them in place to the values they
already hold. Column F -- where the nine carry four different lineage-specific example sets -- is an
overlay column and is left alone. The change converts nine hand-maintained copies into one owned
definition, exactly as Module_ICPMS v1 did for its original 13 fields.

Placement: the `session` block, whose target group is `4. Measurement Information` -- where the
field already sits in all nine TAPPs.
"""
import csv, json, os, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs"
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
DATE = "2026-08-27"
FIELD = "Analysis Sequence"

ROW = {
    "Metadata Item": FIELD,
    "Description": ("The repeating order in which calibration or bracketing standards, "
                    "quality-control and secondary reference materials, blanks and unknowns are "
                    "interleaved within a measurement session. Adjustments must maintain the "
                    "bracketing strategy defined in the procedure."),
    "Procedure-Level Tier": "Basic",
    "Analysis-Level Tier": "Editable",
    "Data Type": "Text (free)",
    # Column F is an overlay and is lineage-specific in all nine consumers (LA bracketing counts,
    # SSB and double-spike for Solution MC, matrix-matched bracketing for Solution SF). The module
    # carries a front-end-neutral default rather than promoting one lineage's examples.
    "Example / Allowed Content": ("e.g., '1 primary standard / 1 QC / 10 unknowns' | "
                                  "'Standard bracketing every 5 samples' | "
                                  "'Calibration block at session start, standard after every 3 samples'"),
    "Comments": "",
    "Last Update": DATE,
    "Keyed By": "(none)",
    # Empty, as in all nine consumers: Step 1 of the Description/Purpose split routed every
    # sentence of this field to Description.
    "Purpose": "",
}

def main(apply=False):
    csvp = os.path.join(MODDIR, "Module_ICPMS.csv")
    jsonp = os.path.join(MODDIR, "Module_ICPMS.json")
    rows = list(csv.reader(open(csvp, newline="", encoding="utf-8-sig")))
    h = rows[0]
    if any(r and r[0].strip() == FIELD for r in rows[1:]):
        raise SystemExit("%s is already in Module_ICPMS" % FIELD)
    missing = [c for c in ROW if c not in h]
    if missing: raise SystemExit("module CSV lacks column(s): %s" % missing)

    # Verify against the live consumers before writing: every owned column must already agree.
    OWNED = ["Metadata Item", "Description", "Procedure-Level Tier",
             "Analysis-Level Tier", "Data Type", "Keyed By"]
    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    consumers = [e["tapp"] for e in reg["composed"] if "ICP" in os.path.basename(e["tapp"])]
    if len(consumers) != 9: raise SystemExit("expected 9 ICP-MS consumers, found %d" % len(consumers))
    for p in consumers:
        crows = list(csv.reader(open(os.path.join(ROOT, p), newline="", encoding="utf-8-sig")))
        ch = crows[0]
        cr = next((x for x in crows[1:] if x and x[0].strip() == FIELD), None)
        if cr is None: raise SystemExit("%s has no %s row" % (p, FIELD))
        for c in OWNED:
            got = (cr[ch.index(c)].strip() if len(cr) > ch.index(c) else "")
            if got != ROW[c]:
                raise SystemExit("%s: %s differs from the module row it would adopt:\n  TAPP:   %r\n  module: %r"
                                 % (os.path.basename(p), c, got[:120], ROW[c][:120]))
    print("  verified: all 6 owned columns already identical across all 9 consumers")

    newrow = [ROW.get(c, "") for c in h]
    rows.append(newrow)

    man = json.load(open(jsonp, encoding="utf-8"))
    sess = next(b for b in man["blocks"] if b["name"] == "session")
    if FIELD in sess["fields"]: raise SystemExit("already in the session block")
    sess["fields"].append(FIELD)
    old_v = man["version"]; man["version"] = str(int(old_v) + 1)
    man["decisions"].append(
        "2026-08-27: extended to 39 fields — `Analysis Sequence` moved in, completing the 26 and "
        "with them the full 39-field ICP-MS-specific set identified at extraction. The 2026-08-26 "
        "entry above deferred it because its D-tier split Editable/Read-Only on the LA/Solution "
        "line and precedents.md recorded that divergence as knowingly unresolved. It was resolved "
        "on 2026-08-27 to D=Editable across all nine, decided not by majority but by the field's "
        "own text: the 2026-08-26 description merge had made Column B identical across all nine, "
        "and the shared wording — 'Adjustments must maintain the bracketing strategy defined in "
        "the procedure' — presupposes that the analyst may adjust, which is what D=Editable means. "
        "Adding it here changes NO TAPP content: all six owned columns were already byte-identical "
        "across the nine, so composition rewrites them to the values they already hold, and the "
        "four lineage-specific Column F example sets are untouched because F is an overlay column. "
        "Generalise: a merge pass that harmonises Column B can settle a tier divergence that was "
        "left open for want of evidence, and so unblock an extraction that was waiting on it — "
        "re-check a module's deferred list after any description merge.")
    print("  Module_ICPMS: %d -> %d fields, manifest v%s -> v%s"
          % (len(rows) - 2, len(rows) - 1, old_v, man["version"]))
    if not apply:
        print("(dry run — pass --apply to write)"); return

    with open(csvp, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    with open(jsonp, "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=4, ensure_ascii=False); fh.write("\n")
    print("  written")

if __name__ == "__main__":
    main("--apply" in sys.argv)
