#!/usr/bin/env python3
"""Build the adjudicated findings table for the Column B / Column I survey (2026-08-12).

Input  : the raw Axis A/B/C sweeps from survey_colB_colI_20260812.py, plus hand adjudication
         recorded in FINDINGS below.
Output : Claude Skills for TAPP/analysis/Survey_ColI_Findings_2026-08-12.csv

Each finding carries the evidence quote it rests on, so the table can be checked against the
TAPPs without re-running the sweep. Occurrence counts are recomputed from the library at build
time rather than typed in, so they cannot drift from the files.
"""
import csv
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # library root: this script lives in "Project Files/Scripts/"
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

OUT = os.path.join(ROOT, "Claude Skills for TAPP", "analysis",
                   "Survey_ColI_Findings_2026-08-12.csv")

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")

# Class, Field, Declared_I_filter, Diagnosis, Evidence, Proposed_action, Desc_regex
# Declared_I_filter = only count rows whose Column I matches this (None = all rows)
# Desc_regex        = only count rows whose Column B matches this (None = no text narrowing)
FINDINGS = [
    # ---- Class 1: definer that is itself keyed. Needs notation that does not yet exist.
    ("1 — definer carrying a second key", "Monitored Isotopes", "defines: channel",
     "Defines the channel domain, but the enumeration is organised per analyte. Column I states "
     "only the definer role; the analyte key is stated in Column B and nowhere machine-readable.",
     "'Specific isotope(s) monitored per analyte element in this procedure...' + 'Analyte-specific field.'",
     "Column I -> definer-with-key form, domain=channel, key=analyte. Delete the trailing "
     "'Analyte-specific field.' sentence, which the key now carries.", r"analyte[- ]specific"),
    ("1 — definer carrying a second key", "EELS Edges", "defines: channel",
     "Defines the channel domain; edges are named by element symbol, so the enumeration is "
     "organised per analyte. Same shape as Monitored Isotopes, reached independently in TEM.",
     "'Ionization edge(s) acquired by EELS, specified by element symbol and edge label (e.g., Fe "
     "L2,3; O K)... the EELS-specific counterpart to the Analyte field'",
     "Column I -> definer-with-key form, domain=channel, key=analyte. No Column B change needed; "
     "the description is accurate.", None),
    ("1 — definer carrying a second key", "Secondary Reference Materials", "defines: standard",
     "Defines the standard domain, but each entry carries per-analyte assessed values, so the "
     "field body is a table keyed by analyte within standard. Not in the technique-dependent "
     "register, so whichever key is chosen applies to all 12 TAPPs.",
     "'Include material name, assessed elements, number of analyses (n), and measured vs. "
     "accepted values.'",
     "Column I -> definer-with-key form, domain=standard, key=analyte (or reported property — "
     "decide against Analytical Precision, which is already standard x reported property).", r"assessed elements"),
    ("1 — definer carrying a second key", "Collector Configuration", "defines: channel",
     "Defines the channel domain, but multi-dynamic procedures register several configurations "
     "with a cycling sequence, so the definition repeats over a pass/magnet-step axis. That key "
     "('acquisition pass') was retired 2026-08-11 under 7.4b/c for want of a user — this is a user.",
     "'For static multi-collection procedures, one configuration applies throughout... For "
     "multi-dynamic procedures, list all configurations and the cycling sequence.'",
     "Decide whether multi-dynamic cycling is a key or free text. If a key, un-retire "
     "'acquisition pass' with this field as its user. MODULE-OWNED (Module_MCICPMS).", r"multi-dynamic"),

    # ---- Class 2: definer whose domain nests in itself.
    ("2 — definer with a self-nesting domain", "Sampling Unit", "defines: sampling unit",
     "Rule 9's mandatory field describes a two-level domain in prose. Rule 7.3 has 'A > B' for "
     "containment between two different keys, but no form for a definer that enumerates a domain "
     "nested within itself.",
     "'Where units nest (e.g. confined tracks within grains), state both levels.'",
     "Decide whether nesting is expressible in Column I (e.g. a nested-domain form) or stays "
     "prose-only. Affects all 16 TAPPs; fission track is the live case.", r"nest"),

    # ---- Class 3: conditionally keyed.
    ("3 — conditionally keyed", "Integration Time per Cycle", "(none)",
     "Declared scalar, but the description says it becomes channel-keyed under a stated "
     "condition. Rule 7 has no notation for a key that is present only conditionally, so the "
     "declaration takes the narrower reading and the wider one survives only in prose.",
     "'Analyte-specific when different isotope channels use different integration schemes.'",
     "Choose a policy: declare the finest key unconditionally (over-declares for simple "
     "procedures), or add a conditional-key notation. MODULE-OWNED (Module_MCICPMS).", r"analyte[- ]specific"),
    ("3 — conditionally keyed", "Dwell Time per Mass", "channel",
     "Same shape one level up: declared channel, description adds an optional analyte "
     "dimension. Whether channel already subsumes it depends on the procedure.",
     "'May differ per analyte if analyte-specific dwell times are programmed.'",
     "Resolve with the Class 3 policy. If channel is judged sufficient, delete the sentence.", r"analyte[- ]specific"),

    # ---- Class 4: stale cross-reference to a retired mechanism.
    ("4 — stale cross-reference", "Analyte", "defines: analyte",
     "Description directs the reader to a Comments-column label that Rule 7 retired. In all 5 "
     "TAPPs carrying this sentence the Comments column is empty on every row, so the instruction "
     "cannot be followed. Survives because Rule 7.6 cleaned Column G and never swept Column B.",
     "'Fields below flagged as Analyte-Specific in the Comments column apply individually to "
     "each element in this list.'",
     "Replace the sentence with a pointer to Column I, or delete it — Column I now carries the "
     "information for every field.", r"Comments column"),

    # ---- Class 5: bare assertion duplicating Column I (delete prose; I is correct).
    ("5 — prose duplicates Column I", "Mass Resolution per Analyte", "analyte",
     "Trailing 'Analyte-specific field.' restates the declared key verbatim.",
     "'...recorded in Mass Resolution Setting (Group 3). Analyte-specific field.'",
     "Delete the trailing sentence. Column I is correct.", r"analyte[- ]specific"),
    ("5 — prose duplicates Column I", "Monitored Isotopes", "analyte",
     "In the two MC TAPPs the field is analyte-keyed (the cup array defines the channel, per "
     "7.4b) and the trailing sentence restates that key verbatim.",
     "'...including any interference-monitor masses. Analyte-specific field.'",
     "Delete the trailing sentence. Column I is correct.", r"analyte[- ]specific"),
    ("5 — prose duplicates Column I", "Per-Analyte Calibration Strategy", "analyte",
     "'list analyte-specific strategies as needed' restates the declared key.",
     "'Free text; list analyte-specific strategies as needed.'",
     "Optional cleanup — reads as drafting guidance rather than a cardinality claim.", r"analyte[- ]specific"),

    # ---- Class 6: prose names a key that contradicts Column I.
    ("6 — prose contradicts Column I", "Interfering Species", "channel",
     "Column I says channel, which is right: an interference is on a mass, not on an element. "
     "The trailing 'Analyte-specific.' names the wrong key.",
     "'List of isobaric or polyatomic species mathematically corrected in data reduction. "
     "Analyte-specific.'",
     "Delete the trailing sentence. Column I is correct.", r"Analyte-specific\."),
    ("6 — prose contradicts Column I", "Interference Correction Method", "channel",
     "As above — the correction is per interfered-upon mass.",
     "'...the tailing factor is measured using a pure standard. Analyte-specific.'",
     "Delete the trailing sentence. Column I is correct.", r"Analyte-specific\."),
    ("6 — prose contradicts Column I", "Isobaric Interference Corrections Applied", "channel",
     "The Solution MC row ends 'Analyte-specific.' while the 6 LA rows say 'Analyte-specific "
     "detail is captured in Interfering Species and Interference Correction Method' — a "
     "legitimate cross-reference. Only the bare assertion is at fault.",
     "'...abundance sensitivity tailing of 238U onto 236U and 235U. Analyte-specific.'",
     "Delete the trailing sentence on the Solution MC row only; keep the LA cross-reference.", r"Analyte-specific\.\s*$"),
    ("6 — prose contradicts Column I", "Isotope Ratio Reported", "reported property",
     "A reported ratio is itself the reported property; 'Analyte-specific.' names a coarser key.",
     "'Report all ratio pairs routinely calculated and reported. Analyte-specific.'",
     "Delete the trailing sentence. Column I is correct.", r"Analyte-specific\."),
    ("6 — prose contradicts Column I", "delta or epsilon Value Reference Standard",
     "reported property",
     "Genuinely unresolved, unlike the rest of Class 6. The zero-delta anchor is chosen per "
     "element system (IRMM-014 for Fe), which argues analyte or standard, not reported property.",
     "'...the certified or consensus isotope ratio used for normalization. Analyte-specific.'",
     "Adjudicate the key. Do not delete the sentence until the key is settled.", r"Analyte-specific\."),
    ("6 — prose contradicts Column I", "Detection Limit", None,
     "The description names a different key from Column I in all 12 TAPPs that carry the field, "
     "in both register variants: where I = reported property the prose says 'for each analyte'; "
     "where I = sampling unit x reported property the prose says 'for each measured isotope... "
     "per isotope or element group' (channel). Rule 7.3 uses this very field as its worked "
     "example of the defines/keyed-by distinction, so the mismatch is conspicuous.",
     "'Elemental detection limits for each analyte.' / 'Session detection limit for each "
     "measured isotope... Report the value(s) and units per isotope or element group.'",
     "Decide whether the analyte and reported-property domains are isomorphic for "
     "concentration-reporting procedures (one concentration variable per element). If so, record "
     "it as a precedent — it recurs across the library. Then align the prose to Column I.", r"each analyte|each measured isotope"),
    ("6 — prose contradicts Column I", "Detection Limit Method", "reported property",
     "Same mismatch, inherited from the field it documents.",
     "'Method used to calculate detection limits for each analyte.'",
     "Align with the Detection Limit decision.", r"each analyte"),

    # ---- Class 7: declared scalar, prose implies a key.
    ("7 — declared (none), prose implies a key", "Calibration Factor and Determination Method",
     "(none)",
     "Declared scalar in 14 TAPPs, but the description distinguishes itself from a field that is "
     "explicitly per-analyte and says it holds 'the resulting factor itself' — one factor per "
     "analyte. Highest-leverage row in the survey: MODULE-OWNED in Module_ReportingCore, which "
     "has 16 consumers.",
     "'Distinct from... Per-Analyte Calibration Strategy, which states which approach applies to "
     "which analyte: this field records the resulting factor itself.'",
     "Adjudicate: analyte, reported property, or genuinely scalar. MODULE-OWNED — fix in "
     "Module_ReportingCore and recompose, never in the TAPPs (Rule 6.6).", r"which analyte"),

    # ---- Class 8: definer by count, not by enumeration.
    ("8 — definer by count", "Number of Digestion Steps", "defines: preparation step",
     "Satisfies 7.4a by stating how many steps exist rather than listing them — the domain is "
     "ordinal 1..N. Legitimate, but it is the only definer in the library of this shape and the "
     "rule text does not acknowledge that a count can enumerate a domain.",
     "Data Type = Integer; 'Total number of distinct acid digestion steps required...'",
     "No change to the file. Note in Rule 7.4a that an ordinal count enumerates its domain. "
     "MODULE-OWNED (Module_SolutionIntroduction).", None),
]

# Field names whose 'per X' is a rate, normalisation or schedule rather than a key.
# Recorded so a future sweep does not re-raise them.
FALSE_POSITIVES = [
    ("Ablation Duration per Spot", "'per spot' is the unit of the duration, not a key"),
    ("Signal Integration Time", "'per analysis' expresses a rate"),
    ("EDS Live Time per Point or Pixel", "'per point' is the unit of the live time"),
    ("Dwell Time per Pixel", "'per pixel' is the unit; the analyte key it does carry is already declared"),
    ("Total Integration Time per Output Data Point", "'per data point' is the unit"),
    ("Number of Blocks per Measurement", "a count, and 'per measurement' is its unit"),
    ("Mass Cycles per Replicate", "a count; 'per replicate' is its unit"),
    ("Number of Scans per Replicate", "a count; 'per replicate' is its unit"),
    ("Number of Replicates", "a scalar count"),
    ("Number of Projections", "a scalar count"),
    ("Background Count Time", "'before each ablation' / 'once per raster line' is a schedule, not a cardinality"),
    ("Mass Resolution Setting", "correctly delegates the per-analyte case to Mass Resolution per Analyte"),
    ("Additional Notes", "'session-specific' is not a key"),
    ("Technique per Analyte", "declared analyte, correct; 'line overlap' is prose, not a second key"),
    ("Stage Scan vs. Beam Scan", "'across' is spatial, not distributive"),
    ("Total Scan Duration", "'across the scan' is spatial"),
    ("Signal Integration Interval Method", "'for each ablation' is a schedule"),
    ("Pre-Ablation Surface Treatment", "'each spot' is a schedule"),
    ("EBSD Phase List", "holds a list; no field is keyed by it (7.4c)"),
]


def module_owner(field):
    owners = []
    for fn in sorted(os.listdir(MODULES)):
        if not fn.endswith(".csv"):
            continue
        for r in csv.reader(open(os.path.join(MODULES, fn), newline="", encoding="utf-8-sig")):
            if r and r[0].strip() == field:
                owners.append(fn.replace("Module_", "").replace(".csv", ""))
                break
    return ",".join(owners)


def occurrences(field, decl_filter, desc_regex=None):
    """Rows matching this field, optionally narrowed by Column I value and by Column B text.

    desc_regex narrows a prose finding to the rows that actually carry the offending text —
    without it, a field present in 13 TAPPs would be reported as 13 affected rows when only
    5 carry the sentence at issue.
    """
    hits = []
    rx = re.compile(desc_regex, re.I) if desc_regex else None
    for p in V.discover(ROOT):
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        iI = rows[0].index("Keyed By")
        for n, r in enumerate(rows[1:], start=2):
            if not r or len(r) <= iI or r[0].strip() != field:
                continue
            if decl_filter is not None and r[iI].strip() != decl_filter:
                continue
            if rx and not rx.search(r[1] if len(r) > 1 else ""):
                continue
            hits.append((os.path.basename(p), n, r[iI].strip()))
    return hits


def main():
    rows_out = []
    for cls, field, declf, diagnosis, evidence, action, descrx in FINDINGS:
        occ = occurrences(field, declf, descrx)
        mod = module_owner(field)
        rows_out.append(dict(
            Class=cls, Field=field,
            Declared_Keyed_By=declf if declf else " / ".join(sorted({o[2] for o in occ})),
            N_rows=len(occ),
            TAPPs="; ".join(f"{o[0].replace('_TAPP','').replace('.csv','')}:{o[1]}" for o in occ),
            Owner=f"MODULE:{mod}" if mod else "TAPP-owned",
            Diagnosis=diagnosis, Evidence_from_Column_B=evidence, Proposed_action=action))

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Class", "Field", "Declared_Keyed_By", "N_rows",
                                          "Owner", "TAPPs", "Diagnosis",
                                          "Evidence_from_Column_B", "Proposed_action"])
        w.writeheader()
        for r in sorted(rows_out, key=lambda x: (x["Class"], -x["N_rows"])):
            w.writerow(r)
        w.writerow({})
        w.writerow({"Class": "9 — adjudicated false positive",
                    "Diagnosis": "'per X' in a field name or description denoting a rate, unit, "
                                 "count or schedule rather than a cardinality key. Recorded so a "
                                 "future sweep does not re-raise them.",
                    "Proposed_action": "No change."})
        for field, why in FALSE_POSITIVES:
            occ = occurrences(field, None)
            w.writerow({"Class": "9 — adjudicated false positive", "Field": field,
                        "Declared_Keyed_By": " / ".join(sorted({o[2] for o in occ})),
                        "N_rows": len(occ),
                        "Owner": f"MODULE:{module_owner(field)}" if module_owner(field) else "TAPP-owned",
                        "Diagnosis": why, "Proposed_action": "No change."})

    actionable = sum(r["N_rows"] for r in rows_out)
    print(f"{len(rows_out)} findings across {len(set(r['Class'] for r in rows_out))} classes, "
          f"{actionable} affected rows")
    print(f"{len(FALSE_POSITIVES)} field names adjudicated as false positives")
    print(f"-> {OUT}")
    print()
    for r in sorted(rows_out, key=lambda x: (x["Class"], -x["N_rows"])):
        print(f"  {r['Class'][:34]:36s} {r['Field'][:42]:44s} n={r['N_rows']:<3} {r['Owner']}")


if __name__ == "__main__":
    main()
