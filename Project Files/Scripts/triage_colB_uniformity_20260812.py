#!/usr/bin/env python3
"""Triage the Column B divergences across shared field names (Rule 6.4 / 7.8.7 counterpart).

Of 252 field names appearing in more than one TAPP, 89 carry substantively divergent descriptions and
NONE of them are module-owned — `compose_tapp.py --check` guarantees uniformity where a module owns
the row, and nothing looks anywhere else. Column I has a cross-TAPP check (7.8.7, implemented
2026-08-12); Column B has none.

A naive uniformity check would be wrong, because some divergence is legitimate: a description that
names the technique's own physics SHOULD differ between EPMA and Lab-XCT. So this triages first,
following the same drift / principled / bug scheme that `analysis/Test4_Tier_Difference_Triage.csv`
used for tier divergences.

  SUPERSET    one variant contains the others' content and adds more — harmonise to the fullest
  PARAPHRASE  same content, different words; no technique-specific material — drift, harmonise
  PRINCIPLED  variants encode genuinely technique-specific content — legitimate, register
  MIXED       some variants technique-specific, others merely shorter — needs the full text

Ranked by breadth: a field in 16 TAPPs is a bigger decision than one in 2.
"""
import csv
import difflib
import glob
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # library root: this script lives in "Project Files/Scripts/"
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

OUT = os.path.join(ROOT, "Claude Skills for TAPP", "analysis",
                   "Triage_ColB_Uniformity_2026-08-12.csv")

# Words that make a description legitimately technique-specific: instrument classes, signal types,
# and technique-bound physics. A variant containing markers the others lack is encoding real
# technique content, not drifting.
TECH_MARKERS = re.compile(r"""\b(
 EPMA|WDS|EDS|EBSD|CL|SEM|FIB|FIB-SEM|TEM|STEM|EELS|4D-STEM|EFTEM|
 XCT|CT|tomograph\w*|radiograph\w*|projection|voxel|beam.hardening|ring.artefact|ring.artifact|
 LA|laser|ablation|fluence|downhole|aerosol|
 ICP-MS|quadrupole|sector.field|multi.collector|multicollector|Faraday|collector|cup|
 plasma|nebuli[sz]er|desolvat\w*|spray.chamber|torch|
 X-ray.tube|anode|spectrometer|crystal|LIF|PET|TAP|LDE|
 takeoff.angle|overvoltage|ZAF|phi.rho.z|matrix.correction|
 mass.bias|isotope.dilution|double.spike|delta|epsilon|
 Raman|XRD|Rietveld|M[oö]ssbauer|fission.track|luminescence|OSL|
 digestion|column.chemistry|chromatograph\w*|aliquot|
 monochromator|aperture|convergence.angle|camera.length|diffraction
)\b""", re.I | re.X)

STOP = set("""a an the of to in for and or is are be been with by on at as that this it its from
which may can where when if not no than then also such other more most one two each per within
between into using used use record recorded records state stated states specify specified give
given e g eg i e ie etc value values field procedure analysis analyst level""".split())


def tokens(t):
    return {w for w in re.findall(r"[a-z][a-z\-]{2,}", t.lower()) if w not in STOP}


TRUNCATED = re.compile(r"[,;:]\s*$|\(\s*[^)]*$")


def classify(variants):
    """variants: {normalised description: [tapp names]} -> (verdict, note)

    The first cut of this classifier called any field PRINCIPLED when one variant carried a
    technique term the others lacked. That over-classified badly: `Sample Name`'s four variants
    are one sentence with a local noun swapped ("sample mount", "TEM section"), which is drift,
    not principled divergence. So technique markers are STRIPPED before comparing content — a
    field is only PRINCIPLED when what remains after removing them still differs.
    """
    texts = list(variants)
    marks = {t: set(m.group(0).lower() for m in TECH_MARKERS.finditer(t)) for t in texts}
    toks = {t: tokens(t) for t in texts}
    # content words with technique vocabulary removed, so a swapped noun does not read as substance
    bare = {t: {w for w in toks[t]
                if not any(w in m or m in w for m in marks[t])
                and not TECH_MARKERS.fullmatch(w)}
            for t in texts}

    # BUG — a variant is truncated or a stub while its siblings are full sentences
    longest_len = max(len(t) for t in texts)
    broken = [t for t in texts if TRUNCATED.search(t) or (len(t) < 45 and longest_len > 110)]
    if broken:
        return "BUG", (f"{len(broken)} variant(s) truncated or stub: "
                       + " / ".join(f"…{b[-42:]!r}" for b in broken[:2]))

    # SUPERSET — one text's content covers every other's and is materially longer
    longest = max(texts, key=len)
    others = [t for t in texts if t is not longest]
    if others and all(not (toks[o] - toks[longest]) for o in others) \
            and len(longest) >= 1.25 * max(len(o) for o in others):
        return "SUPERSET", f"fullest variant covers all others ({len(longest)} chars)"

    pairs = [(a, b) for i, a in enumerate(texts) for b in texts[i + 1:]]
    jac = [len(bare[a] & bare[b]) / max(1, len(bare[a] | bare[b])) for a, b in pairs]
    lo, hi = (min(jac), max(jac)) if jac else (0, 0)

    all_marks = set().union(*marks.values()) if marks else set()
    shared_marks = set.intersection(*marks.values()) if marks else set()
    distinctive = all_marks - shared_marks

    # PRINCIPLED — technique terms differ AND the surrounding content differs too
    if distinctive and lo < 0.40:
        return "PRINCIPLED", (f"technique terms differ ({', '.join(sorted(distinctive)[:5])}) and "
                              f"non-technique content also differs ({lo:.2f}–{hi:.2f})")
    # DRIFT — same content, only a technique noun or the phrasing swapped
    if distinctive:
        return "DRIFT", (f"same content ({lo:.2f}–{hi:.2f}) once technique terms are set aside "
                         f"({', '.join(sorted(distinctive)[:5])})")
    if lo >= 0.45:
        return "PARAPHRASE", f"content-word overlap {lo:.2f}–{hi:.2f}, no technique terms"
    return "MIXED", f"content-word overlap {lo:.2f}–{hi:.2f}"


def main():
    modf = set()
    for f in glob.glob(os.path.join(ROOT, "Claude Skills for TAPP", "modules", "*.csv")):
        for r in csv.reader(open(f, newline="", encoding="utf-8-sig")):
            if r and r[0].strip():
                modf.add(r[0].strip())

    desc = defaultdict(lambda: defaultdict(list))
    for p in V.discover(ROOT):
        rows = list(csv.reader(open(p, newline="", encoding="utf-8-sig")))
        iI = rows[0].index("Keyed By")
        for r in rows[1:]:
            if not r or len(r) <= iI or not r[0].strip() or not r[iI].strip():
                continue
            key = re.sub(r"\s+", " ", (r[1] or "").strip())
            desc[r[0].strip()][key].append(
                os.path.basename(p).replace("_TAPP", "").replace(".csv", ""))

    rows_out = []
    for fld, variants in desc.items():
        n_tapp = sum(len(v) for v in variants.values())
        if n_tapp < 2 or len(variants) < 2:
            continue
        vs = list(variants)
        worst = min(difflib.SequenceMatcher(None, a, b).ratio()
                    for i, a in enumerate(vs) for b in vs[i + 1:])
        if worst >= 0.90:
            continue                      # trivial rewording, not in scope
        verdict, note = classify(variants)
        rows_out.append(dict(
            Field=fld, N_TAPPs=n_tapp, N_variants=len(variants),
            Worst_similarity=f"{worst:.2f}", Verdict=verdict, Basis=note,
            Owner="MODULE" if fld in modf else "TAPP-owned",
            Variants=" ||| ".join(f"[{','.join(sorted(variants[v]))}] {v}" for v in
                                  sorted(variants, key=lambda x: -len(x)))))

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Field", "N_TAPPs", "N_variants", "Worst_similarity",
                                          "Verdict", "Basis", "Owner", "Variants"])
        w.writeheader()
        order = {"BUG": 0, "SUPERSET": 1, "DRIFT": 2, "PARAPHRASE": 3, "MIXED": 4, "PRINCIPLED": 5}
        for r in sorted(rows_out, key=lambda d: (order[d["Verdict"]], -d["N_TAPPs"])):
            w.writerow(r)

    from collections import Counter
    c = Counter(r["Verdict"] for r in rows_out)
    print(f"{len(rows_out)} substantively divergent field names -> {OUT}\n")
    for k in ("BUG", "SUPERSET", "DRIFT", "PARAPHRASE", "MIXED", "PRINCIPLED"):
        n = c[k]
        breadth = sum(r["N_TAPPs"] for r in rows_out if r["Verdict"] == k)
        print(f"  {k:11s} {n:3d} field names, {breadth:4d} TAPP-rows")
    print()
    for k in ("BUG", "SUPERSET", "DRIFT", "PARAPHRASE", "MIXED", "PRINCIPLED"):
        sel = sorted([r for r in rows_out if r["Verdict"] == k],
                     key=lambda d: -d["N_TAPPs"])
        if not sel:
            continue
        print(f"--- {k} ---")
        for r in sel[:14]:
            print(f"  {r['N_TAPPs']:3d} TAPPs  {r['N_variants']}v  sim={r['Worst_similarity']}  "
                  f"{r['Field'][:44]:46s} {r['Basis'][:58]}")
        if len(sel) > 14:
            print(f"  … +{len(sel) - 14} more")
        print()


if __name__ == "__main__":
    main()
