#!/usr/bin/env python3
"""Survey Column B descriptions against Column I (Keyed By) across the whole TAPP library.

Three axes:
  A  Cardinality language in Column B — does the description state a key?
     Classified against the declared Column I value:
       REDUNDANT   description states exactly the key already declared in I
       EXTRA       description states a key absent from I  (the Monitored Isotopes class)
       CONFLICT    description states a key that contradicts I
  B  Every `defines: K` row, enumerated exhaustively for hand adjudication:
     is the definer itself keyed by something?
  C  Multi-key language in non-definer rows — a second key hiding behind a single declared key.

Read-only. Writes two CSVs plus a console summary.
"""
import csv
import os
import re
import sys
from collections import defaultdict, Counter

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # library root: this script lives in "Project Files/Scripts/"
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import validate_tapp as V  # noqa: E402

OUT_DIR = os.path.join(ROOT, "Claude Skills for TAPP", "analysis")

# ---------------------------------------------------------------- key vocabulary
# Noun -> key. Ordered longest-first at match time so "reference material" beats "material".
NOUN_TO_KEY = {
    # analyte
    "analyte": "analyte", "analytes": "analyte",
    "element": "analyte", "elements": "analyte", "elemental": "analyte",
    "chemical species": "analyte", "oxide": "analyte", "oxides": "analyte",
    # channel
    "isotope": "channel", "isotopes": "channel", "isotopic": "channel",
    "mass": "channel", "masses": "channel", "m/z": "channel",
    "channel": "channel", "channels": "channel",
    "cup": "channel", "cups": "channel", "collector": "channel", "collectors": "channel",
    "detector": "channel", "detectors": "channel",
    "spectrometer": "channel", "spectrometers": "channel",
    "crystal": "channel", "crystals": "channel",
    "x-ray line": "channel", "x-ray lines": "channel", "line": "channel", "lines": "channel",
    "edge": "channel", "edges": "channel",
    "wavenumber": "channel", "bin": "channel", "bins": "channel",
    "peak position": "channel",
    # reported property
    "reported variable": "reported property", "reported variables": "reported property",
    "reported quantity": "reported property", "reported quantities": "reported property",
    "reported property": "reported property", "reported properties": "reported property",
    "reported value": "reported property", "reported values": "reported property",
    "ratio": "reported property", "ratios": "reported property",
    "date": "reported property", "dates": "reported property",
    "age": "reported property", "ages": "reported property",
    "quantity": "reported property", "quantities": "reported property",
    "variable": "reported property", "variables": "reported property",
    "output": "reported property", "outputs": "reported property",
    "isotope ratio": "reported property", "isotope ratios": "reported property",
    "delta value": "reported property", "delta values": "reported property",
    # sampling unit
    "spot": "sampling unit", "spots": "sampling unit",
    "grain": "sampling unit", "grains": "sampling unit",
    "analysis point": "sampling unit", "analysis points": "sampling unit",
    "point": "sampling unit", "points": "sampling unit",
    "aliquot": "sampling unit", "aliquots": "sampling unit",
    "phase": "sampling unit", "phases": "sampling unit",
    "track": "sampling unit", "tracks": "sampling unit",
    "sub-volume": "sampling unit", "sub-volumes": "sampling unit",
    "region of interest": "sampling unit", "regions of interest": "sampling unit",
    "replicate": "sampling unit", "replicates": "sampling unit",
    "sampling unit": "sampling unit", "sampling units": "sampling unit",
    "analysis": "sampling unit", "analyses": "sampling unit",
    "transect": "sampling unit", "map": "sampling unit",
    # standard
    "standard": "standard", "standards": "standard",
    "reference material": "standard", "reference materials": "standard",
    "calibrant": "standard", "calibrants": "standard",
    "calibration standard": "standard", "calibration standards": "standard",
    # preparation step
    "step": "preparation step", "steps": "preparation step",
    "stage": "preparation step", "stages": "preparation step",
    "column": "preparation step", "columns": "preparation step",
    # model component
    "component": "model component", "components": "model component",
    "doublet": "model component", "sextet": "model component",
    "fitted peak": "model component", "fitted peaks": "model component",
}
NOUNS_BY_LEN = sorted(NOUN_TO_KEY, key=len, reverse=True)

VALID_KEYS = {"analyte", "channel", "reported property", "sampling unit",
              "standard", "preparation step", "model component",
              "conversion", "acquisition pass"}

# Cardinality trigger constructions. Group 1 = the noun phrase that follows.
TRIGGERS = [
    (r"\bper[- ]([a-z/\- ]{3,30})", "per X"),
    (r"\bfor each ([a-z/\- ]{3,30})", "for each X"),
    (r"\bone (?:value |row |entry )?(?:per|for each) ([a-z/\- ]{3,30})", "one per X"),
    (r"\beach ([a-z/\- ]{3,30})", "each X"),
    (r"\bseparately for ([a-z/\- ]{3,30})", "separately for X"),
    (r"\bindividually for ([a-z/\- ]{3,30})", "individually for X"),
    (r"\blisted (?:for|by) ([a-z/\- ]{3,30})", "listed by X"),
    (r"\bacross ([a-z/\- ]{3,30})", "across X"),
]
# "<noun>-specific" — the demoted Rule 7 label and its relatives
SPECIFIC_RE = re.compile(r"\b([a-z][a-z\- ]{2,25}?)[- ]specific\b", re.I)


def noun_to_key(phrase):
    """Map a captured noun phrase to a key, longest noun first. None if no key noun present."""
    p = phrase.lower().strip()
    for noun in NOUNS_BY_LEN:
        if re.search(r"\b" + re.escape(noun) + r"\b", p):
            return NOUN_TO_KEY[noun], noun
    return None, None


def keys_in_declared(decl):
    """The set of keys a Column I value is *keyed by* (excludes the defines: domain)."""
    d = decl.strip()
    if not d or d == "(none)":
        return set(), None
    m = re.match(r"^defines:\s*(.+)$", d)
    if m:
        # under the current grammar a definer declares no key of its own
        return set(), m.group(1).strip()
    m = re.match(r"^pair:\s*(.+)$", d)
    if m:
        return {m.group(1).strip()}, None
    parts = re.split(r"\s+x\s+|\s*>\s*", d)
    return {p.strip() for p in parts if p.strip()}, None


def scan_description(text):
    """All (key, noun, trigger, snippet) cardinality signals in a description."""
    hits = []
    low = text.lower()
    for pat, label in TRIGGERS:
        for m in re.finditer(pat, low):
            key, noun = noun_to_key(m.group(1))
            if key:
                s = max(0, m.start() - 30)
                hits.append((key, noun, label, text[s:min(len(text), m.end() + 20)].strip()))
    for m in SPECIFIC_RE.finditer(text):
        key, noun = noun_to_key(m.group(1))
        if key:
            s = max(0, m.start() - 30)
            hits.append((key, noun, "X-specific", text[s:min(len(text), m.end() + 20)].strip()))
    # dedupe on (key, trigger)
    seen, out = set(), []
    for h in hits:
        if (h[0], h[2]) not in seen:
            seen.add((h[0], h[2]))
            out.append(h)
    return out


def main():
    tapps = V.discover(ROOT)
    axis_a, axis_b, axis_c = [], [], []
    definer_names = defaultdict(list)
    stats = Counter()

    for path in tapps:
        name = os.path.basename(path)
        rows = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
        hdr = rows[0]
        iI = hdr.index("Keyed By")
        for n, r in enumerate(rows[1:], start=2):
            if not r or not r[0].strip():
                continue
            if len(r) <= iI:
                continue
            item, desc = r[0].strip(), (r[1] if len(r) > 1 else "").strip()
            dtype = (r[4] if len(r) > 4 else "").strip()
            example = (r[5] if len(r) > 5 else "").strip()
            decl = r[iI].strip()
            if not decl:
                continue          # group headers / separators
            stats["rows"] += 1
            declared_keys, defines_dom = keys_in_declared(decl)

            # ---- Axis B: every definer row, for hand adjudication
            if defines_dom:
                definer_names[item].append((name, n, decl, desc, dtype, example))

            # ---- Axis A: description language vs declaration
            for key, noun, trig, snip in scan_description(desc):
                if key in declared_keys:
                    verdict = "REDUNDANT"
                elif defines_dom and key == defines_dom:
                    verdict = "REDUNDANT"
                elif not declared_keys and not defines_dom:
                    verdict = "EXTRA"      # declared (none) but description states a key
                elif defines_dom:
                    verdict = "EXTRA"      # definer whose description states a further key
                else:
                    verdict = "CONFLICT"   # keyed by something else than description says
                stats[verdict] += 1
                axis_a.append(dict(
                    TAPP=name, Row=n, Field=item, Declared_I=decl, Verdict=verdict,
                    Description_key=key, Trigger=trig, Matched_noun=noun, Snippet=snip,
                    Description=desc))

            # ---- Axis C: two or more distinct keys implied, only one declared
            impl = {h[0] for h in scan_description(desc)}
            if len(impl) >= 2 and not defines_dom:
                undeclared = impl - declared_keys
                if undeclared:
                    axis_c.append(dict(
                        TAPP=name, Row=n, Field=item, Declared_I=decl,
                        Implied_keys=" + ".join(sorted(impl)),
                        Undeclared=" + ".join(sorted(undeclared)), Description=desc))

    # ------------------------------------------------------------------ write Axis A
    os.makedirs(OUT_DIR, exist_ok=True)
    pa = os.path.join(OUT_DIR, "Survey_ColB_vs_ColI_AxisA_2026-08-12.csv")
    with open(pa, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["TAPP", "Row", "Field", "Declared_I", "Verdict",
                                          "Description_key", "Trigger", "Matched_noun",
                                          "Snippet", "Description"])
        w.writeheader()
        order = {"EXTRA": 0, "CONFLICT": 1, "REDUNDANT": 2}
        for row in sorted(axis_a, key=lambda x: (order[x["Verdict"]], x["Field"], x["TAPP"])):
            w.writerow(row)

    # ------------------------------------------------------------------ write Axis B
    pb = os.path.join(OUT_DIR, "Survey_ColB_vs_ColI_AxisB_definers_2026-08-12.csv")
    with open(pb, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Field", "Defines", "N_TAPPs", "TAPPs", "Declared_I_variants",
                    "Data_Type", "Description", "Example"])
        for item in sorted(definer_names):
            occ = definer_names[item]
            variants = sorted({o[2] for o in occ})
            doms = sorted({re.sub(r"^defines:\s*", "", v) for v in variants})
            w.writerow([item, " / ".join(doms), len(occ),
                        "; ".join(f"{o[0]}:{o[1]}" for o in occ),
                        " | ".join(variants), occ[0][4], occ[0][3], occ[0][5]])

    # ------------------------------------------------------------------ console summary
    print(f"TAPPs surveyed          : {len(tapps)}")
    print(f"Content rows with a key : {stats['rows']}")
    print()
    print("AXIS A — cardinality language in Column B")
    for v in ("EXTRA", "CONFLICT", "REDUNDANT"):
        print(f"  {v:10s} {stats[v]:4d}")
    print(f"  -> {pa}")
    print()
    print(f"AXIS B — definer rows: {sum(len(v) for v in definer_names.values())} "
          f"across {len(definer_names)} distinct field names")
    print(f"  -> {pb}")
    print()
    print(f"AXIS C — rows implying >=2 keys with one declared: {len(axis_c)}")
    for r in axis_c[:40]:
        print(f"  {r['TAPP']:32s} r{r['Row']:<4} {r['Field'][:42]:44s} "
              f"I={r['Declared_I']:26s} implied={r['Implied_keys']}")


if __name__ == "__main__":
    main()
