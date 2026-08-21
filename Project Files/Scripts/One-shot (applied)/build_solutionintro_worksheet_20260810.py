#!/usr/bin/env python3
"""
Build the SolutionIntroduction reconciliation worksheet.

`Module_SolutionIntroduction` is version `1-provisional`: its descriptions were
taken from Solution Q-ICP-MS by default after an attempt to choose between the
three source variants by keyword proxy failed (14 of 16 scored identically).
Only `Isotope Dilution Spike` was decided on evidence.

The three source variants survive in the PRE-composition versions, since
composition overwrote columns A-E in the live files:

    Q  -> Solution Q-ICP-MS/Solution_Q-ICP-MS_TAPP_v6.csv   (v7 is composed)
    SF -> Solution SF-ICP-MS/Solution_SF-ICP-MS_TAPP_v6.csv (v7 is composed)
    MC -> Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v4.csv (v5 is composed)

All 16 fields are present in all three, so nothing is lost.

Output mirrors `Group1_Reconciliation_Decisions.csv` — the established shape for
a reconciliation record — with the three candidate texts added so the choice can
be made by reading rather than by guessing.

Rows where all three variants are byte-identical are pre-resolved: there is
nothing to decide. Rows where two of three agree are marked, because that
reduces a three-way read to a two-way one.
"""
import csv
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
MODCSV = ROOT / "Claude Skills for TAPP" / "modules" / "Module_SolutionIntroduction.csv"
OUT = ROOT / "SolutionIntroduction_Reconciliation_WORKSHEET.csv"

SOURCES = {
    "Q": ROOT / "Solution Q-ICP-MS" / "Solution_Q-ICP-MS_TAPP_v6.csv",
    "SF": ROOT / "Solution SF-ICP-MS" / "Solution_SF-ICP-MS_TAPP_v6.csv",
    "MC": ROOT / "Solution MC-ICP-MS" / "Solution_MC-ICP-MS_TAPP_v4.csv",
}

# Decided on evidence during extraction; carried over rather than re-asked.
ALREADY_DECIDED = {
    "Isotope Dilution Spike": (
        "MC",
        "MC adds when the spike must be introduced and why — genuine instruction "
        "content the other two lack.",
    )
}


def descriptions(path):
    out = {}
    for r in csv.reader(open(path, encoding="utf-8-sig")):
        if r and r[0].strip():
            out[r[0].strip()] = (r[1] if len(r) > 1 else "").strip()
    return out


def main():
    module = descriptions(MODCSV)
    fields = [r[0].strip() for r in csv.reader(open(MODCSV, encoding="utf-8-sig"))][1:]
    fields = [f for f in fields if f]
    src = {k: descriptions(p) for k, p in SOURCES.items()}

    rows = []
    counts = {"identical": 0, "two-way": 0, "three-way": 0, "pre-decided": 0}
    for f in fields:
        q, sf, mc = src["Q"].get(f, ""), src["SF"].get(f, ""), src["MC"].get(f, "")
        variants = {q, sf, mc}
        # which source does the module text currently match?
        cur = [k for k, v in (("Q", q), ("SF", sf), ("MC", mc)) if v == module.get(f, "")]
        cur = "/".join(cur) if cur else "(none - edited)"

        if f in ALREADY_DECIDED:
            winner, rationale = ALREADY_DECIDED[f]
            status = "PRE-DECIDED (evidence)"
            adopted = {"Q": q, "SF": sf, "MC": mc}[winner]
            counts["pre-decided"] += 1
        elif len(variants) == 1:
            winner, rationale = "all identical", "No divergence - nothing to decide."
            status = "NO DECISION NEEDED"
            adopted = q
            counts["identical"] += 1
        else:
            winner = rationale = adopted = ""
            if len(variants) == 2:
                pair = ("Q=SF" if q == sf else "Q=MC" if q == mc else "SF=MC")
                status = f"DECIDE (2 variants; {pair})"
                counts["two-way"] += 1
            else:
                status = "DECIDE (3 variants)"
                counts["three-way"] += 1

        rows.append({
            "Field": f,
            "Status": status,
            "Module text currently from": cur,
            "Winner": winner,
            "Rationale": rationale,
            "Adopted description": adopted,
            "Q (Solution Q v6)": q,
            "SF (Solution SF v6)": sf,
            "MC (Solution MC v4)": mc,
        })

    cols = ["Field", "Status", "Module text currently from", "Winner", "Rationale",
            "Adopted description", "Q (Solution Q v6)", "SF (Solution SF v6)",
            "MC (Solution MC v4)"]
    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT.relative_to(ROOT)}  ({len(rows)} fields)\n")
    for k, v in counts.items():
        print(f"  {k:12s} {v}")
    print()
    decisions = counts["two-way"] + counts["three-way"]
    print(f"  ACTUAL DECISIONS REQUIRED: {decisions}")
    print()
    for r in rows:
        if r["Status"].startswith("DECIDE"):
            print(f"   {r['Field'][:44]:44s} {r['Status']}")


if __name__ == "__main__":
    main()
