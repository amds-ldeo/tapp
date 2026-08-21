#!/usr/bin/env python3
"""
Column F reconciliation worksheet for the three Solution ICP-MS TAPPs.

Column F is CONSUMER-owned (Rule 6.4), so divergence there is legitimate by
design — it is where a technique-specific instantiation of an abstract module
field lives. The question is therefore not "are these different?" but "is each
difference *earned*?"

Each field is classified against one test:

    Does the content depend on the mass analyser?

  * ANALYSER-DEPENDENT -> divergence is earned; keep it. Double-spike
    compositions, desolvating nebulisers and separation-resin suites genuinely
    differ between a quadrupole trace-element procedure and a multi-collector
    isotope-ratio one.

  * ANALYSER-INDEPENDENT -> divergence is drift. Digestion vessels and acids do
    not know what detector is downstream. Proposed resolution is the union of
    the three lists, so no lab's real practice is dropped.

  * GAP -> empty in all three. Rule 6.4: "a module row is not complete until its
    consumer supplies Column F." These need content written, not chosen.

Source is the LIVE composed files, since composition preserves Column F.

Output is a worksheet, not an edit. Nothing is written to any TAPP.
"""
import csv
from pathlib import Path

ROOT = Path("/Users/ruolin/Documents/Astromat/TAPPs")
MODCSV = ROOT / "Claude Skills for TAPP" / "modules" / "Module_SolutionIntroduction.csv"
OUT = ROOT / "SolutionIntroduction_ColumnF_WORKSHEET.csv"

LIVE = {
    "Q": ROOT / "Solution Q-ICP-MS" / "Solution_Q-ICP-MS_TAPP_v7.csv",
    "SF": ROOT / "Solution SF-ICP-MS" / "Solution_SF-ICP-MS_TAPP_v7.csv",
    "MC": ROOT / "Solution MC-ICP-MS" / "Solution_MC-ICP-MS_TAPP_v5.csv",
}

# Classification. The reason is stated per field so the call can be challenged.
ANALYSER_DEPENDENT = {
    "Isotope Dilution Spike":
        "MC lists double spikes (IRMM-3636, Sn/Fe) because double-spiking is an "
        "MC-ICP-MS mass-bias technique. Q/SF single-element spikes serve a different purpose.",
    "Chromatographic Separation Applied":
        "MC needs quantitative element separation (TRU, UTEVA, AG-MP-1, thiol) for "
        "isotope-ratio work; Q/SF trace-element runs frequently skip separation entirely.",
    "Nebulizer Type":
        "MC routinely runs self-aspirating low-flow and Apex-HF nebulisers; the "
        "introduction chain differs with the measurement goal.",
    "Spray Chamber Type and Cooling Temperature":
        "Follows the nebuliser choice — MC's SIS and downstream-of-Aridus arrangements "
        "have no Q/SF counterpart.",
    "Final Solution Matrix":
        "PARTLY earned: MC genuinely runs lower acid strengths. But MC states molarity "
        "(0.3 M HNO3) where Q/SF state percent — a NOTATION difference that is drift. "
        "Recommend harmonising units, keeping the values.",
}

ANALYSER_INDEPENDENT = {
    "Digestion Vessel Type":
        "Vessels do not depend on the detector. MC alone lists 'TFE/TFM bomb'.",
    "Digestion Acid(s)":
        "Acids do not depend on the detector. MC adds HF-HNO3-HClO4 and drops Aqua regia.",
    "Desolvation System":
        "Same 4-5 instruments in different order, with spelling drift "
        "('Apex IR' vs 'Apex-IR').",
    "Nebulizer Gas Flow Rate":
        "0.8-1.1 / 0.8-1.0 / 0.85-1.05 L/min. No instrument reason for three different "
        "ceilings; arbitrary near-identical ranges.",
    "Wash Time Between Samples":
        "Q and SF empty, MC populated. Not a divergence — a gap in two of three.",
}


def colf(path):
    out = {}
    for r in csv.reader(open(path, encoding="utf-8-sig")):
        if r and r[0].strip():
            out[r[0].strip()] = (r[5] if len(r) > 5 else "").strip()
    return out


def union(vals):
    seen = []
    for v in vals:
        for opt in [o.strip() for o in v.split("|") if o.strip()]:
            if opt not in seen:
                seen.append(opt)
    tail = [o for o in seen if o in ("N/A", "None", "Other: specify")]
    head = [o for o in seen if o not in ("N/A", "None", "Other: specify")]
    return " | ".join(head + tail)


def main():
    fields = [r[0].strip() for r in csv.reader(open(MODCSV, encoding="utf-8-sig"))][1:]
    fields = [f for f in fields if f]
    F = {k: colf(p) for k, p in LIVE.items()}

    rows, counts = [], {"keep (earned)": 0, "harmonise (drift)": 0,
                        "write (gap)": 0, "already identical": 0}
    for f in fields:
        vals = [F[k].get(f, "") for k in ("Q", "SF", "MC")]
        distinct = len(set(vals))
        allempty = not any(vals)

        if allempty:
            disp, why, proposed = "WRITE (gap)", (
                "Empty in all three. Rule 6.4: a module row is not complete until the "
                "consumer supplies Column F."), ""
            counts["write (gap)"] += 1
        elif f in ANALYSER_INDEPENDENT:
            disp, why = "HARMONISE (drift)", ANALYSER_INDEPENDENT[f]
            proposed = union(vals)
            counts["harmonise (drift)"] += 1
        elif f in ANALYSER_DEPENDENT:
            disp, why, proposed = "KEEP (earned)", ANALYSER_DEPENDENT[f], ""
            counts["keep (earned)"] += 1
        elif distinct == 1:
            disp, why, proposed = "OK (identical)", "Already consistent.", vals[0]
            counts["already identical"] += 1
        else:
            disp, why, proposed = "REVIEW", "Unclassified.", ""

        rows.append({
            "Field": f, "Disposition": disp, "Why": why,
            "Proposed unified value": proposed, "Agree? (y/n)": "", "Notes": "",
            "Q (live v7)": vals[0], "SF (live v7)": vals[1], "MC (live v5)": vals[2],
        })

    cols = ["Field", "Disposition", "Why", "Proposed unified value", "Agree? (y/n)",
            "Notes", "Q (live v7)", "SF (live v7)", "MC (live v5)"]
    with open(OUT, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT.name}  ({len(rows)} fields)\n")
    for k, v in counts.items():
        print(f"  {k:20s} {v}")
    print()
    for r in rows:
        if r["Disposition"].startswith(("HARMONISE", "WRITE")):
            print(f"  {r['Disposition'][:18]:18s} {r['Field']}")


if __name__ == "__main__":
    main()
