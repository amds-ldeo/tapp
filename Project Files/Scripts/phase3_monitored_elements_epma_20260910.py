#!/usr/bin/env python3
"""Phase 3 for `Monitored Elements` in EPMA — all 15 procedure columns.

The field was created on 2026-09-10 by restructure_monitored_property_20260910.py, after
those columns had been assessed, so its cells went in blank. This fills them.

SOURCE RULE. Every value was read from the source PDF in the session that wrote this script
and carries its page. Twelve papers cover the fifteen columns — Liu et al. 2016, McCoy et al.
2025 and Barnes et al. 2025 each supply two, on different instruments. Neuman et al. 2025 is
in `XCT/Literature Assessment/`, the rest in `EPMA/`.

NOTHING IS DERIVED FROM A NEIGHBOURING CELL. `X-ray Line`, `Target Species` and `Primary
Calibration Standard Name` already hold overlapping content for several of these procedures.
Those are our own earlier readings, not evidence. Every value here traces to a sentence.

FOUR CELLS GET `N`, each for its own stated reason — the corpus is thinner on this than the
X-ray-line attestation rate alone suggested:
  * Pang et al. 2016  — "Natural and synthetic standards were used" (p.7) without naming them;
                         the analysed elements are in Supplementary Table 4, not in the PDF.
  * Broussard et al. 2026 — describes EPMA stage mapping and its calibration (p.3) but names
                         no element.
  * Zega et al. 2025  — "Well-characterized natural and synthetic materials were used as
                         standards" (p.9); no element list.
  * Barnes et al. 2025, NHM London — gives beam conditions and a detection limit for
                         "transition metals" (p.13) but no element list.

TWO CELLS RECORD A PASS STRUCTURE, which is what `acquisition pass` was minted for and is
worth noting for the EPMA/SEM deferral recorded in conventions.md: Neuman collects Mg, Al,
Fe, Ca, Ti in pass 1 and Na, Si, Mn, K, Cr in pass 2; Barnes at CRPG uses two *sessions* with
different element sets. Neither is acted on here — this pass fills a field, it does not re-key.
"""

import csv, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REL  = "EPMA/EPMA_TAPP_v67.csv"
NEW  = "EPMA/EPMA_TAPP_v68.csv"
FIELD = "Monitored Elements"

V = {
"Ma+2015":
  "Si, Al, Ca, Na, Fe, Mg, Mn, Ti, Cr, K — all determined; no monitor-only element. "
  "\"Standards for analysis were anorthite (SiKα, AlKα, CaKα); albite (NaKα); fayalite (FeKα); "
  "forsterite (MgKα); Mn2SiO4 (MnKα); TiO2 (TiKα); Cr2O3 (CrKα); and microcline (KKα)\" (p.3)",
"Hu+2020":
  "Si, Mg, Fe, Na, Al, Ca, Mn, K, Ti, Cr — all determined. \"The EPMA standards were natural and "
  "synthetic minerals: natural kaersutite for Si, Mg and Fe, jadeite for Na and Al, bustamite for Ca "
  "and Mn, and K-feldspar for K, synthetic rutile for Ti and Cr2O3 for Cr\". Cr also carries the "
  "interference correction — \"X-ray interference of the Kα line of Mn by the Kβ line of Cr was "
  "corrected\" — but is itself determined, so it is not an orphan",
"Liu+2016_UT":
  "Ca, Al, Fe, Mg — \"elemental X-ray maps (Ca Kα, Al Kα, Fe Kα, and Mg Kα) of four sections were "
  "obtained using a Cameca SX100 electron microprobe (EMP) at the University of Tennessee\" (p.3). "
  "A separate Caltech map set of two olivine megacrysts adds Fe, P, Al, Ca and Cr (p.4) but was "
  "collected on the other instrument, which this TAPP records as its own procedure column",
"Liu+2016_Cal":
  "Si, Ti, Al, Mg, Ca, Fe, Mn, Cr, Ni, Na, K, P — all determined. \"Detection limits are typically "
  "<0.03 wt% for SiO2, TiO2, Al2O3, MgO, and CaO; <0.05–0.1 wt% for FeO, MnO, Cr2O3, NiO, Na2O, K2O, "
  "and P2O5\" (p.4)",
"Ma+2017":
  "Si, Al, K, Ca, Na, Fe, Mg, Ti, Cr, Mn — all determined. \"Standards for analysis were Asbestos "
  "microcline (SiKa, AlKa, KKa), synthetic anorthite (CaKa), Amelia albite (NaKa), synthetic fayalite "
  "(FeKa), synthetic forsterite (MgKa), synthetic TiO2 (TiKa), synthetic Cr2O3 (CrKa), and synthetic "
  "Mn-olivine (MnKa)\", with detection limits quoted for the same ten (p.2)",
"Frank+2023":
  "Si, Al, Ti, K, Na, Fe, Mg, Ca, S, Mn, Cr, Ni, P, V — all determined. \"Standards were Kakanui "
  "kaersutite for silicon, aluminum, titanium, potassium, sodium, iron, magnesium, and calcium, Canyon "
  "Diablo troilite for sulfur, rhodonite for manganese, chromium metal for chromium, nickel metal for "
  "nickel, apatite for phosphorus, and vanadium metal for vanadium\" (pp.3–4)",
"Broussard+2026":
  "N — the paper describes quantitative EPMA stage mapping and its calibration against Smithsonian "
  "Microbeam secondary standards (p.3) but names no element",
"Seifert+2026":
  "P, F, Cl, Ca, Mn, Fe, Na, Mg, Si, S — all determined. \"A total of 14 analyses were performed at "
  "15 kV, 20 nA, using a 2 μm probe size, and included the elements P, F, Cl, Ca, Mn, Fe, Na, Mg, Si, "
  "and S\" (p.3)",
"Pang+2016":
  "N — \"Natural and synthetic standards were used\" (p.7) without naming them; the analysed elements "
  "are given in Supplementary Table 4, which is not in the archived PDF",
"McCoy+2025_SI":
  "Fe, Mn, Mg, Ca — all determined. \"Carbonate analyses were run at 15 kV and 10 nA, with an "
  "analytical spot size of 5 µm. Fe and Mn were analysed using a LIFL crystal, Mg using a TAPL crystal "
  "and Ca using a PETL crystal\" (p.7)",
"McCoy+2025_UA":
  "F, P, Ca, Si, Mg, Fe, Al, S, K, Cl (Mg,Na phosphate) and Na, Si, Mg, Ca, Mn (carbonates) — all "
  "determined. \"The standards used for Mg,Na phosphate were fluorapatite (F, P, Ca), Fo92 olivine "
  "(Si, Mg), rhodonite (Mg), fayalite (Fe), anorthite (Al), baryte (S), potassium feldspar (K) and "
  "scapolite (Cl). For carbonates, the standards used were albite (Na), Fo92 olivine (Si), dolomite "
  "(Mg), calcite (Ca), Mn...\" (p.7)",
"Zega+2025":
  "N — \"Well-characterized natural and synthetic materials were used as standards\" (p.9); the paper "
  "gives beam conditions and count times for silicates, sulfides, oxides, phosphates and carbonates "
  "but names no element",
"Barnes+2025 | JEOL JXA-8230":
  "Session 1: Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe, Si. Session 2: Na, K, Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe, "
  "Si. All determined. \"We used two different settings to determine the chemical compositions of "
  "minerals: (1) Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe and Si (session 1) and (2) Na, K, Al, Ti, Ca, Cr, Mn, "
  "Ni, Mg, Fe and Si (session 2)\" (p.11)",
"Barnes+2025 | Cameca SX100":
  "N — the paper gives beam conditions and a detection limit for transition metals of about 250 ppm "
  "for the NHM London instrument (p.13) but names no element",
"Neuman+2025":
  "Pass 1: Mg, Al, Fe, Ca, Ti. Pass 2: Na, Si, Mn, K, Cr. All determined. \"Two passes were used to "
  "collect X-ray intensities for Mg, Al, Fe, Ca, and Ti in pass 1, and Na, Si, Mn, K, and Cr in "
  "pass 2\" (p.6)",
}


def main(apply=False):
    src = os.path.join(ROOT, REL)
    rows = list(csv.reader(io.open(src, newline="", encoding="utf-8-sig")))
    h = rows[0]; s = h.index("Literature Assessment")
    lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
    m = {}
    for i in lit:
        hs = " ".join(h[i].split())
        hits = [k for k in V if all(p.strip().lower() in hs.lower() for p in k.split("|"))]
        if len(hits) != 1:
            print("  !! %d match(es) for %s" % (len(hits), hs[:60])); return 1
        m[i] = V[hits[0]]
    row = next(r for r in rows[1:] if r and r[0].strip() == FIELD)
    while len(row) < len(h): row.append("")
    for i in sorted(m):
        if row[i].strip():
            print("  !! %s already filled — refusing" % h[i][:40]); return 1
        row[i] = m[i]
        print("  %-46s %s" % (" ".join(h[i].split())[:46], m[i][:64]))
    print("\n  %d of %d columns filled; blanks left: %d"
          % (len(m), len(lit), sum(1 for i in lit if not row[i].strip())))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0
    with io.open(os.path.join(ROOT, NEW), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    print("  wrote %s" % NEW)
    return 0


sys.exit(main("--apply" in sys.argv))
