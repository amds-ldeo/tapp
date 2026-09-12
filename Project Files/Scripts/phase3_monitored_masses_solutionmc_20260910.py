#!/usr/bin/env python3
"""Phase 3 for `Monitored Masses` in Solution MC-ICP-MS — all 14 procedure columns.

The field was added on 2026-09-10 by restructure_monitored_property_20260910.py, after those
columns had been assessed, so its cells went in blank. This fills them.

SOURCE RULE. Every value below was read from the source PDF in the session that wrote this
script, and carries its page. Ten papers are in `Solution MC-ICP-MS/literature assessment/`;
Broussard et al. 2026 and Barnes et al. 2025 are in `EPMA/`, both covering several techniques.

WHAT WAS NOT DONE. No value is derived from the neighbouring `Collector Configuration` or
`Target Species` cell, even where that cell plainly contains the masses. Those cells are our
own earlier reading, not evidence, and copying one field into another is the folded-in-neighbour
defect repaired on 2026-09-09. Where the source does not state the masses, the cell gets `N`.

THREE CELLS GET `N`, each for a different reason:
  * Hu et al. 2022 — the paper says "The cup configurations used for isotopic analyses of the
    REEs are provided in table S2" (p.9). That supplementary table is not in the archived PDF.
  * Nowell et al. 2008, Nu Plasma — the paper describes only "two-sequence static
    multi-collection" for that instrument and gives no mass list.
  * (The Neptune column of the same paper IS filled, from the Re/W correction discussion and
    the naming of the L3 detector, with the limits of that reading stated in the cell.)
"""

import csv, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v73.csv"
NEW  = "Solution MC-ICP-MS/Solution_MC-ICP-MS_TAPP_v74.csv"
FIELD = "Monitored Masses"

V = {
"Budde+etal2016":
  "⁹²Mo, ⁹⁴Mo, ⁹⁵Mo, ⁹⁶Mo, ⁹⁷Mo, ⁹⁸Mo, ¹⁰⁰Mo (Mo); "
  "⁹¹Zr, ⁹⁹Ru (interference monitors, no target species) — \"Isobaric interferences of Zr "
  "and Ru on Mo masses were corrected by monitoring 91Zr and 99Ru\" (p.2); mass bias normalised to "
  "98Mo/96Mo and ε⁹²/⁹⁴/⁹⁵/⁹⁷/¹⁰⁰Mo reported (pp.2–3)",
"Craddock+etal2008":
  "³²S (L3), ³³S (C), ³⁴S (H3) — Table 1 \"Cup configuration\", p.3. All three serve the "
  "single target species S",
"Hopp+etal2021":
  "⁵⁴Fe, ⁵⁶Fe, ⁵⁷Fe, ⁵⁸Fe (Fe); ⁵³Cr, ⁶⁰Ni (interference monitors, no target species) — "
  "\"Ion beams of 54Fe+, 56Fe+, 57Fe+, and 58Fe+ were analyzed in static mode on Faraday collectors... "
  "Possible isobaric interferences from 54Cr+ and 58Ni+ were measured simultaneously by monitoring "
  "53Cr+ and 60Ni+\" (p.6)",
"Hu+etal2022":
  "N — the paper states \"The cup configurations used for isotopic analyses of the REEs are provided "
  "in table S2\" (p.9); that supplementary table is not in the archived PDF",
"IbanezMejia+Tissot2020":
  "Masses 90, 91, 92, 93, 94, 95, 96 and 98 — \"Masses 90, 91, 92, 93, 94, 95, 96, and 98 were measured "
  "in static mode at 0.5 amu spacing in the Nu Plasma II collector block, allowing direct monitoring of "
  "all Zr isotopes and Mo interferences (masses 95 and 98)\" (p.11). 95 and 98 carry the Mo monitors and "
  "serve no target species",
"Nie+Dauphas2019":
  "⁸⁵Rb, ⁸⁷Rb (Rb); ⁸⁸Sr (interference monitor, no target species) — \"Rubidium-85 and -87 were "
  "measured on L2 and axial (A) Faraday collectors, respectively\", and the ⁸⁷Sr contribution \"was "
  "corrected for by monitoring 88Sr\" (p.8)",
"Nowell+etal2008 | Neptune":
  "¹⁸⁴Os, ¹⁸⁶Os, ¹⁸⁷Os, ¹⁸⁸Os, ¹⁸⁹Os, ¹⁹⁰Os, ¹⁹²Os (Os); ¹⁸⁵Re and ¹⁸²W/¹⁸⁴W/¹⁸⁶W "
  "(interference monitors, no target species) — the Os masses are those whose ratios to ¹⁸⁸Os the paper "
  "measures and reports; the Re and W monitors are named throughout the interference-correction "
  "discussion (§3.6, pp.12–18), and the L3 detector is named as carrying ¹⁸⁴Os (p.26). The paper gives "
  "no single cup-configuration table",
"Nowell+etal2008 | Nu Plasma":
  "N — the paper describes the Nu Plasma acquisition only as two-sequence static multi-collection and "
  "gives no mass list or cup configuration for that instrument",
"Pringle+Moynier2017":
  "⁸⁴Sr (L2), ⁸⁵Rb (L1), ⁸⁶Sr (C), ⁸⁷Rb + ⁸⁷Sr (H1), ⁸⁸Sr (H2) — Table 2, p.3. ⁸⁵Rb and ⁸⁷Rb serve "
  "the target species Rb; the Sr masses are interference monitors with no target species, ⁸⁸Sr being the "
  "one used to correct ⁸⁷Sr on ⁸⁷Rb",
"Schönbächler+etal2025":
  "⁹⁰Zr, ⁹¹Zr, ⁹²Zr, ⁹⁴Zr, ⁹⁶Zr (Zr); ⁹⁵Mo, ⁹⁹Ru, ¹⁰¹Ru (interference monitors, no target species) — "
  "\"Faraday cups with 10¹¹ Ω amplifiers were used to collect Zr masses 90Zr to 96Zr and 95Mo, whereas "
  "10¹² Ω amplifiers were applied for the collection of 99Ru and 101Ru\" (p.6)",
"vanKooten+etal2026":
  "²⁴Mg, ²⁵Mg, ²⁶Mg (Mg) — \"The isotopes 24Mg, 25Mg and 26Mg were analysed using 10¹¹ Ω resistors\" "
  "(p.8)",
"Broussard+etal2026":
  "³⁹K, ⁴¹K (K) — δ⁴¹K is defined from the ⁴¹K/³⁹K ratio (p.4). ⁴⁰Ar¹H⁺ is named as the interference on "
  "⁴¹K⁺ (p.4) but is not itself a monitored mass",
"Barnes+etal2025 | Neptune Plus | WUSTL":
  "³⁹K, ⁴¹K (K); ⁶³Cu, ⁶⁵Cu (Cu); ⁶⁴Zn, ⁶⁶Zn (Zn) — the three delta values are defined from the "
  "⁴¹K/³⁹K, ⁶⁵Cu/⁶³Cu and ⁶⁶Zn/⁶⁴Zn ratios (p.7)",
"Barnes+etal2025 | Neptune Plus | ETH":
  "\"all five Ti isotopes\" — ⁴⁶Ti, ⁴⁷Ti, ⁴⁸Ti, ⁴⁹Ti, ⁵⁰Ti (Ti); ⁴⁴Ca, ⁴⁵Sc, ⁵¹V, ⁵²Cr, ⁵³Cr "
  "(interference monitors, no target species) — \"Titanium isotopes were collected in two cup "
  "configurations. First, all five Ti isotopes as well as 44Ca, 45Sc, 51V, 52Cr and 53Cr were collected "
  "in one line using Faraday cups\" (p.8)",
}


def pick(header):
    """Map each literature column to its value by matching the header text."""
    out = {}
    for i, h in enumerate(header):
        hs = " ".join(h.split())
        for k, v in V.items():
            parts = [p.strip() for p in k.split("|")]
            if all(p.lower() in hs.lower() for p in parts):
                if i in out:
                    raise SystemExit("column %d matched twice" % i)
                out[i] = v
    return out


def main(apply=False):
    src = os.path.join(ROOT, REL)
    rows = list(csv.reader(io.open(src, newline="", encoding="utf-8-sig")))
    h = rows[0]
    s = h.index("Literature Assessment")
    lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
    m = pick(h)
    m = {i: v for i, v in m.items() if i in lit}
    missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
    if missing:
        print("  !! unmatched columns:"); [print("     ", x) for x in missing]; return 1
    row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
    while len(row) < len(h): row.append("")
    filled = 0
    for i, v in sorted(m.items()):
        if row[i].strip():
            print("  !! %s already has a value — refusing" % h[i][:40]); return 1
        row[i] = v; filled += 1
        print("  %-44s %s" % (" ".join(h[i].split())[:44], v[:72]))
    print("\n  %d of %d columns filled; blanks left: %d"
          % (filled, len(lit), sum(1 for i in lit if not row[i].strip())))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0
    with io.open(os.path.join(ROOT, NEW), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    print("  wrote %s" % NEW)
    return 0


sys.exit(main("--apply" in sys.argv))
