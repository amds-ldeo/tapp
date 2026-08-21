#!/usr/bin/env python3
"""Validate every Column I key against the literature assessment extractions.

Generalises the Detection Limit finding. An extracted cell is evidence about a field's *shape*: if
15 EPMA procedures all state one accelerating voltage, the field is scalar; if they all state a
value per element, it is analyte-keyed. Where the observed shape and the declared key disagree, one
of them is wrong.

Method
------
For each keyed content row in each TAPP, classify the shape of every non-empty extraction, then
compare the aggregate against the declared key:

  OVER-DECLARED   key names a repeat axis but every extraction is scalar
  UNDER-DECLARED  key is (none) but extractions enumerate
  AXIS-MISMATCH   key names axis A, extractions enumerate axis B
  CONSISTENT      observed shape matches the declaration
  NO-EVIDENCE     fewer than MIN_EVIDENCE extractions with content

Detectors are deliberately conservative: a shape is only claimed when the signal is unambiguous, so
the residue is NO-EVIDENCE rather than a wrong guess. Output is ranked by how much evidence backs
the disagreement, because a field contradicted by 30 procedures is a different proposition from one
contradicted by 2. Every finding is then hand-adjudicated — the detectors locate candidates, they
do not decide.
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

OUT = os.path.join(ROOT, "Claude Skills for TAPP", "analysis",
                   "Audit_ColI_vs_LitAssess_2026-08-12.csv")
MIN_EVIDENCE = 3          # extractions with real content needed before judging a field

ELEMENTS = set("""H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn
Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Sm Eu Gd Tb
Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Th U""".split())

# Element symbols that are also ordinary English words or unit tokens. Only counted when
# unambiguously adjacent to a number, never from a bare list.
AMBIGUOUS = {"In", "As", "At", "No", "I", "K", "S", "P", "C", "N", "O", "V", "Y", "W", "U", "B",
             "F", "He", "Be", "Ne", "Ar", "Sc", "Br", "Te", "Ba", "La", "Pr", "Sn", "Er"}

NOT_STATED = re.compile(r"^\s*(N|N/?A|n/?a|-|—|not stated|not reported|not specified)\s*[\(\.]?", re.I)

# ---- shape detectors -------------------------------------------------------------------
ISOTOPE_RE = re.compile(r"(?:\b|[⁰¹²³⁴⁵⁶⁷⁸⁹]|\^?\d{1,3})\s*(?:[⁰¹²³⁴⁵⁶⁷⁸⁹]{1,3})?\s*"
                        r"(?:\d{1,3})([A-Z][a-z]?)\b")
# Case-SENSITIVE, and Greek letters or spelled-out alpha/beta only. With re.I and a bare
# `K[a1b]|L[a1b]` this matched "Imaging" as ('I','ma') and "Planet" as ('P','la'), which produced
# a 120-evidence phantom `channel` finding on Coupled Technique(s) in the first run.
XRAY_LINE_RE = re.compile(r"\b([A-Z][a-z]?)[- ]?(?:K|L|M)(?:α|β|γ|alpha|beta)\d?\b")
CRYSTAL_RE = re.compile(r"\b(LIF|LiF|PET|TAP|LDE\d?|PC\d|LPET|LTAP|LLIF)\b")
CUP_RE = re.compile(r"\b(L[1-5]|H[1-5]|Ax|IC\d)\b")
STEP_RE = re.compile(r"\b(step \d|stage \d|first|second|third)\b.*\b(step|stage|column)\b", re.I)
RM_RE = re.compile(r"\b(NIST|SRM|BHVO|BCR|BIR|GSD|GSE|GOR|ATHO|StHs|T1-G|KL2|ML3|NKT|"
                   r"Plesovice|Ple[sš]ovice|91500|GJ-?1|Temora|Zircon|IRMM|Durango|Kakanui|"
                   r"San Carlos|JB-?\d|AGV|GSP|W-?2|DTS|reference material|RM)\b", re.I)
MINERAL_RE = re.compile(r"\b(olivine|pyroxene|plagioclase|feldspar|maskelynite|chromite|spinel|"
                        r"merrillite|apatite|phosphate|sulfide|metal|kamacite|taenite|glass|"
                        r"melt|matrix|chondrule|CAI|zircon|monazite|ilmenite|magnetite)\b", re.I)
PERUNIT_RE = re.compile(r"\b(per|each|every)\s+(spot|analysis|analyses|grain|point|pixel|line|"
                        r"aliquot|phase|acquisition|replicate|session|map|scan)\b", re.I)


def element_hits(text):
    """(valued, listed) sets of distinct element symbols.

    The distinction matters for UNDER-DECLARED. A bare list of elements is a field *holding a
    list*, which 7.4c says is `(none)`, not a keyed field — `Target Material` listing mineral
    types is not keyed by mineral. Only element symbols carrying their own value are evidence
    that the field repeats over analyte.
    """
    valued, listed = set(), set()
    for m in re.finditer(r"\b([A-Z][a-z]?)\s*[:=]?\s*(?:<|~|≈)?\s*\d", text):
        if m.group(1) in ELEMENTS:
            valued.add(m.group(1))
    for run in re.findall(r"(?:\b[A-Z][a-z]?\b\s*[,;]\s*){2,}\b[A-Z][a-z]?\b", text):
        toks = [t.strip() for t in re.split(r"[,;]", run) if t.strip()]
        if len(toks) >= 3 and all(t in ELEMENTS for t in toks):
            listed |= set(toks)
    return valued, listed


# Fields where a cardinality key is meaningless by construction: identifiers, narrative, dates,
# funding, software, coupling, and fields that hold a type list rather than a keyed table (7.4c).
# Excluded so the audit reports shape disagreements about measurement content, not phantom keys on
# a grant acknowledgement. Module_Group1's fields are added programmatically.
EXCLUDE_FIELDS = {
    "Additional Notes", "Target Material", "Target Feature(s)", "Sample Name",
    "Sample Persistent Identifier", "Sample Description", "Analytical Mode",
    "Coupled Technique(s)", "Coupling Description", "Coupled Procedure DOI",
    "Coupled Dataset or Publication Reference", "Acquisition Software",
    "Data Reduction Software", "Sample Preparation Method", "Technique",
    "Reported Variables and Units", "Sampling Unit", "Analyte", "Interfering Elements",
}


# Findings adjudicated 2026-08-12 and deliberately NOT changed. Keyed by (field, verdict) with the
# reason. Re-runs list these separately instead of presenting them as new, so a later Phase 3 pass
# sees only genuinely new disagreements. Rationale for each is in precedents.md under
# "Validating keys against the literature assessment".
ADJUDICATED = {
    ("Primary Calibration Standard Name", "AXIS-MISMATCH"):
        "CONSISTENT — a field that NAMES standards always looks standard-shaped to the detector. "
        "Key set to analyte in LA-SF 2026-08-12 because Navarro et al. 2024 assigns standards to "
        "analyte groups; 6 of 7 use one joint set, which is that axis with one member.",
    ("Isobaric Interference Corrections Applied", "UNDER-DECLARED"):
        "KEEP (none) — Solution extractions are Boolean answers with the affected masses as "
        "parenthetical detail ('Y (204Hg on 204Pb corrected using 202Hg monitor)'). The value is "
        "Y/N; the per-mass detail belongs to Interfering Species and Interference Correction "
        "Method, which keep channel.",
    ("Beam Current", "OVER-DECLARED"):
        "KEEP sampling unit — 2 of 13 procedures publish per-phase currents, so the axis is "
        "attested in reported data even though 10 are scalar.",
    ("Blank / Background Correction Method", "UNDER-DECLARED"):
        "KEEP (none) — 'measured before each ablation' is a schedule, not a cardinality. The "
        "field holds one method.",
    ("Elemental Fractionation Correction", "UNDER-DECLARED"):
        "KEEP (none) — reference materials are mentioned because the correction uses them, not "
        "because the field repeats over them.",
    ("Spike / Outlier Filtering Approach", "UNDER-DECLARED"):
        "KEEP (none) — element names are rejection criteria, not per-analyte values.",
    ("Detection Limit", "AXIS-MISMATCH"):
        "CONSISTENT in EPMA — per-element values are covered by the analyte/reported-property "
        "isomorphism precedent (2026-08-12).",
    ("Monitored Isotopes", "AXIS-MISMATCH"):
        "CONSISTENT — the per-analyte grouping is implicit in isotope notation ('47Ti, 49Ti, "
        "93Nb'); the detector cannot see it.",
    ("Within-Session Analytical Precision and Assessment Method", "OVER-DECLARED"):
        "KEEP standard x reported property — every Solution extraction references reference "
        "materials; the RM detector needs 2 NAMED RMs in one cell and scores 'USGS/GSJ RMs' as "
        "scalar. Detector precision failure.",
    ("Analytical Accuracy and Assessment Method", "OVER-DECLARED"):
        "KEEP standard x reported property — same detector failure; accuracy is assessed against "
        "RMs in all 9 extractions.",
    ("EPMA Technique per Analyte", "OVER-DECLARED"):
        "KEEP analyte — the per-analyte assignment is the field's entire purpose; the surveyed "
        "procedures happen to use one technique throughout.",
    ("Per-Analyte Calibration Strategy", "OVER-DECLARED"):
        "KEEP analyte — as above.",
    ("Mass Resolution per Analyte", "AXIS-MISMATCH"):
        "KEEP analyte — SF procedures assign one resolution mode per element; papers name the "
        "masses because that is how they label the analytes. 4 extractions, 1 TAPP.",
    ("Peak Counting Time", "OVER-DECLARED"):
        "KEEP analyte — 3 of 4 extractions are 'not stated'; insufficient evidence either way.",
    ("Interference Correction Method", "OVER-DECLARED"):
        "KEEP channel — the correction applies per interfered-upon mass; 3 extractions only.",
    ("EDS Live Time per Point or Pixel", "UNDER-DECLARED"):
        "KEEP (none) — 'per point' is the unit of the live time, and the flagged procedures are "
        "N/A for EDS.",
    ("Beam Damage Minimization", "UNDER-DECLARED"):
        "APPLIED 2026-08-12 -> sampling unit.",
    ("Minimum Resolvable Feature Size", "OVER-DECLARED"):
        "DEFERRED — 5 scalar extractions, but Lab-XCT multi-volume scanning may exercise the "
        "per-sub-volume axis.",
    ("Image Processing Methods Applied", "UNDER-DECLARED"):
        "KEEP (none) — holds a processing chain description, not a per-channel table.",
    ("Analytical Sub-mode", "UNDER-DECLARED"):
        "KEEP (none) — enumerates sub-modes as a controlled list; nothing is keyed by it (7.4c).",
}


def classify(text):
    """Return a set of shape tags observed in one extracted cell."""
    t = (text or "").strip()
    if not t or NOT_STATED.match(t):
        return set()
    tags = set()
    valued, listed = element_hits(t)
    isos = {m.group(1) for m in ISOTOPE_RE.finditer(t) if m.group(1) in ELEMENTS}
    lines = XRAY_LINE_RE.findall(t)

    if len(isos) >= 2 or len(CUP_RE.findall(t)) >= 2:
        tags.add("channel")
    if len(lines) >= 2 or len(set(CRYSTAL_RE.findall(t))) >= 2:
        tags.add("channel")
    if len(valued) >= 3:
        tags.add("analyte")
        tags.add("analyte:valued")
    elif len(listed) >= 3:
        tags.add("analyte")
    if len(set(MINERAL_RE.findall(t))) >= 2 or PERUNIT_RE.search(t):
        tags.add("sampling unit")
    if len(set(x.lower() for x in RM_RE.findall(t))) >= 2:
        tags.add("standard")
    if STEP_RE.search(t):
        tags.add("preparation step")
    if not tags:
        # scalar only if it is short and holds at most one numeric quantity
        nums = re.findall(r"\d+(?:\.\d+)?", t)
        tags.add("scalar" if len(t) <= 90 and len(nums) <= 2 else "unclear")
    return tags


def declared_axes(decl):
    kind, domains, keys = V.parse_keyed_by(decl)
    return kind, set(domains), set(keys)


def main():
    g1 = os.path.join(ROOT, "Claude Skills for TAPP", "modules", "Module_Group1.csv")
    if os.path.exists(g1):
        for row in csv.reader(open(g1, newline="", encoding="utf-8-sig")):
            if row and row[0].strip():
                EXCLUDE_FIELDS.add(row[0].strip())
    findings = []
    for path in V.discover(ROOT):
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        hdr = rows[0]
        if "Literature Assessment" not in hdr:
            continue
        s = hdr.index("Literature Assessment")
        litcols = list(range(s + 1, len(hdr)))
        if not litcols:
            continue
        name = os.path.basename(path)

        for n, r in enumerate(rows[1:], start=2):
            if not r or not r[0].strip() or len(r) <= 8 or not r[8].strip():
                continue
            if r[0].strip() in EXCLUDE_FIELDS:
                continue
            decl = r[8].strip()
            kind, domains, keys = declared_axes(decl)
            cells = [r[i].strip() for i in litcols if i < len(r) and r[i].strip()]
            shapes = [classify(c) for c in cells]
            shapes = [x for x in shapes if x]
            if len(shapes) < MIN_EVIDENCE:
                continue

            tally = Counter()
            for sh in shapes:
                for tag in sh:
                    tally[tag] += 1
            n_ev = len(shapes)
            n_scalar = tally["scalar"]
            observed = {k for k, v in tally.items()
                        if k not in ("scalar", "unclear", "analyte:valued")
                        and v >= max(2, 0.34 * n_ev)}
            # value-bearing enumeration only, for the UNDER-DECLARED direction
            observed_valued = {k for k in observed
                               if k != "analyte" or tally["analyte:valued"] >= max(2, 0.34 * n_ev)}

            # A definer's extraction IS the list of members, so enumeration is expected and
            # carries no information about a second key. Only judge definers on their `per` key.
            judge_keys = keys if kind != "defines" else set()
            if kind == "defines" and not keys:
                continue

            verdict = None
            if judge_keys and not observed and n_scalar >= max(2, 0.6 * n_ev):
                verdict = "OVER-DECLARED"
            elif not judge_keys and kind == "none" and observed_valued:
                verdict = "UNDER-DECLARED"
            elif judge_keys and observed and not (observed & judge_keys):
                verdict = "AXIS-MISMATCH"
            elif judge_keys and len(judge_keys) > 1 and observed and len(observed & judge_keys) == 1:
                verdict = "OVER-DECLARED (one axis unsupported)"
            if not verdict:
                continue

            findings.append(dict(
                TAPP=name, Row=n, Field=r[0].strip(), Declared_I=decl, Verdict=verdict,
                N_evidence=n_ev, N_scalar=n_scalar,
                Observed=" + ".join(sorted(observed)) or "scalar",
                Tally="; ".join(f"{k}={v}" for k, v in tally.most_common()),
                Sample=" || ".join(c[:110] for c in cells[:3])))

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["TAPP", "Row", "Field", "Declared_I", "Verdict",
                                          "Disposition", "N_evidence", "N_scalar", "Observed",
                                          "Tally", "Sample"])
        w.writeheader()
        for x in sorted(findings, key=lambda d: (-d["N_evidence"], d["Field"])):
            x = dict(x, Disposition=ADJUDICATED.get(
                (x["Field"], x["Verdict"].split(" (")[0]), "NEW — needs adjudication"))
            w.writerow(x)

    fresh = [x for x in findings
             if (x["Field"], x["Verdict"].split(" (")[0]) not in ADJUDICATED]
    settled = [x for x in findings if x not in fresh]

    print(f"{len(findings)} finding(s) -> {OUT}")
    print(f"  {len(fresh)} NEW (need adjudication) · {len(settled)} already adjudicated "
          f"2026-08-12\n")
    if not fresh:
        print("  No new key/literature disagreements.\n")
    byv = Counter(x["Verdict"] for x in fresh)
    for k, v in byv.most_common():
        print(f"  NEW  {k:32s} {v}")

    # Group by field name: a field flagged in many TAPPs is one decision, not many.
    print("\nNEW findings by field name (strongest evidence first):")
    byf = defaultdict(list)
    for x in fresh:
        byf[(x["Field"], x["Verdict"], x["Declared_I"])].append(x)
    for (fld, verdict, decl), xs in sorted(byf.items(), key=lambda kv: -sum(
            y["N_evidence"] for y in kv[1]))[:30]:
        tapps = ", ".join(sorted({y["TAPP"].replace("_TAPP", "").replace(".csv", "")
                                  for y in xs}))
        print(f"  {sum(y['N_evidence'] for y in xs):4d} ev  {fld[:38]:40s} "
              f"I={decl[:26]:28s} {verdict[:14]:16s} obs={xs[0]['Observed'][:22]:24s} [{tapps[:60]}]")

    print("\nAlready adjudicated (listed so re-runs do not re-raise them):")
    for (fld, verdict), why in sorted(ADJUDICATED.items()):
        n = sum(x["N_evidence"] for x in settled
                if x["Field"] == fld and x["Verdict"].split(" (")[0] == verdict)
        mark = f"{n:4d} ev" if n else "   --  "
        print(f"  {mark}  {fld[:44]:46s} {why[:88]}")


if __name__ == "__main__":
    main()
