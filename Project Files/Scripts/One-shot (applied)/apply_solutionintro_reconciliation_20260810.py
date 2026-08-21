#!/usr/bin/env python3
"""
Apply the SolutionIntroduction Column B reconciliation.

Reads the adopted text from
`SolutionIntroduction_Reconciliation_WORKSHEET.csv` — the worksheet is the
decision record and therefore the source of truth — and writes it into
`Module_SolutionIntroduction.csv`. Column B is module-owned (6.4), so this is a
module edit; the three consuming TAPPs are updated by recomposition, not by
editing them.

Also promotes the module from `1-provisional` to `1`. The provisional marker
existed for exactly one reason: 15 of 16 descriptions had been selected by
default rather than decided. That is no longer true, so the marker goes and the
manifest's reconciliation note is rewritten to record what was decided instead
of why it could not be.

Rows whose Status is NO DECISION NEEDED (3, byte-identical across all sources)
carry an Adopted description too; they are written as well, which is a no-op and
is verified as such.

Run with --apply; default is a dry run.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
APPLY = "--apply" in sys.argv
MODDIR = ROOT / "Claude Skills for TAPP" / "modules"
MODCSV = MODDIR / "Module_SolutionIntroduction.csv"
MODJSON = MODDIR / "Module_SolutionIntroduction.json"
WS = ROOT / "SolutionIntroduction_Reconciliation_WORKSHEET.csv"
DECISIONS = ROOT / "SolutionIntroduction_Reconciliation_Decisions.csv"

NEW_RECONCILIATION = (
    "Reconciled 2026-08-10. Tiers and data types were identical across all three source TAPPs; "
    "only descriptions diverged, in 13 of 16 fields. Three were byte-identical and needed no "
    "decision; `Isotope Dilution Spike` had been decided on evidence at extraction; the remaining "
    "12 were decided by reading, recorded field by field in "
    "SolutionIntroduction_Reconciliation_Decisions.csv.\n\n"
    "Outcome: 5 adopted the Solution MC-ICP-MS variant, 3 adopted Q/SF, 4 were synthesized. MC won "
    "often not because its text was longest but because its authors wrote trade-offs, which is the "
    "highest-value description content.\n\n"
    "Governing distinction: naming an ANALYSER ('prior to MC-ICP-MS analysis') disqualifies text "
    "from a module consumed by three TAPPs; naming a PURPOSE ('for isotope-ratio work') does not, "
    "being a conditional that is true for any consumer doing that work. Several MC variants carried "
    "the module's best content wrapped in analyser-naming and were adopted with the wrapper removed.\n\n"
    "Two rows went against the 2-of-3 majority. `Nebulizer Type`: SF and MC both said the nebulizer "
    "affects 'uptake rate', which collides with the adjacent `Sample Uptake Rate` field; Q's "
    "'sample introduction efficiency' was adopted on the boundary criterion. `Digestion Vessel Type` "
    "went the other way, adopting the SF/MC pair for its concrete consequence clause.\n\n"
    "The earlier finding stands and is why this was done by reading: the Rule 6.10 criteria are "
    "sound as criteria but are NOT automatable by keyword matching. Only the disqualifiers automate."
)


def main():
    ws = list(csv.DictReader(open(WS, encoding="utf-8-sig")))
    adopted = {r["Field"]: r["Adopted description"].strip()
               for r in ws if r.get("Adopted description", "").strip()}
    decided = {r["Field"] for r in ws if r["Status"].startswith("DECIDE")}

    rows = list(csv.reader(open(MODCSV, encoding="utf-8-sig")))
    changed, noop, missing = [], [], []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        f = r[0].strip()
        if f not in adopted:
            missing.append(f)
            continue
        if r[1].strip() == adopted[f]:
            noop.append(f)
        else:
            changed.append((f, r[1], adopted[f]))
            r[1] = adopted[f]

    print(f"{'APPLY' if APPLY else 'DRY RUN'} — SolutionIntroduction Column B reconciliation\n")
    print(f"  changed : {len(changed)}")
    print(f"  no-op   : {len(noop)}  (already equal — expected for the identical rows)")
    if missing:
        print(f"  MISSING adopted text: {missing}")
    print()
    for f, before, after in changed:
        mark = "*" if f in decided else " "
        print(f"  {mark} {f}")
        print(f"      was: {before[:104]}")
        print(f"      now: {after[:104]}")
    print()

    if not APPLY:
        print("(dry run — nothing written; re-run with --apply)")
        return

    with open(MODCSV, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)

    man = json.loads(MODJSON.read_text(encoding="utf-8"))
    man["version"] = "1"
    man["reconciliation"] = NEW_RECONCILIATION
    MODJSON.write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"module version: 1-provisional -> {man['version']}")

    # The worksheet becomes the permanent decision record.
    ws_rows = list(csv.DictReader(open(WS, encoding="utf-8-sig")))
    keep = ["Field", "Status", "Winner", "Attention", "Rationale", "Adopted description",
            "Q (Solution Q v6)", "SF (Solution SF v6)", "MC (Solution MC v4)"]
    with open(DECISIONS, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=keep, extrasaction="ignore")
        w.writeheader()
        w.writerows(ws_rows)
    print(f"wrote {DECISIONS.name}")


if __name__ == "__main__":
    main()
