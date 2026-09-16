#!/usr/bin/env python3
"""Phase 3 for `Reported Variables and Units` — batch 1: EPMA (14 cells).

    python3 "Project Files/Scripts/phase3_reported_variables_epma_20260916.py" [--apply]

The field is a DEFINER (Column I `defines: reported property`), so each cell enumerates the axis:
every variable the procedure reports, with its unit, including intermediate quantities reported
alongside final ones. Nominal properties are recorded with their variable and no unit.

WHAT AN EPMA PROCEDURE REPORTS, and the distinction that matters here: the oxide concentrations are
the measurement, but almost every paper also publishes quantities DERIVED from them — cations per
formula unit, end-member components, modal or areal abundances. The description asks for both, so
each cell lists the oxide suite from the paper's own table and then the derived quantities.

Where the analyses live in a supplement that is not in the archived PDF (Pang 2016, Barnes 2025
CRPG), the cell records the variables the paper states in text and says where the values are.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Reported Variables and Units"
REL = "EPMA/EPMA_TAPP_v75.csv"

CELLS = {
 "Ma+2015":
  "Oxide concentrations (wt%: SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, K2O) with totals and one "
  "standard deviation of the mean; cations per formula unit on 6 oxygens, with \"Sum cations\" (Table 1, p.5); "
  "Ca-Eskola component (mol%: \"42–60 mol% of the Ca-Eskola\" component, p.1); anorthite content of the precursor "
  "plagioclase (An58–69, p.1)",
 "Hu+2020":
  "Oxide concentrations (wt%: SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, K2O) for maskelynite, melt "
  "inclusion glasses, silica glasses, coesite aggregates and mesostasis (p.2); detection limits are given per oxide "
  "(0.01–0.06 wt%, p.2)",
 "Liu+2016_UT":
  "Modal-area fraction per mineral (vol%), computed as \"The number of pixels attributed to each mineral ... divided "
  "by the total number of pixels in the whole section\" (p.3) and reported as modal abundances, e.g. pyroxenes "
  "51–60 vol%, olivine 22–26 vol%, maskelynite 14–17 vol% (Table 1, p.4)",
 "Liu+2016_Cal":
  "Oxide concentrations (wt%: SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, NiO, P2O5, K2O, plus V2O3, La2O3 "
  "and Ce2O3 for the oxides and merrillite) \"of selected minerals\" (Table 2, p.6); derived ratio and end-member "
  "quantities used in the text (Mg#, En-Fs-Wo); glass compositions reported as means with 1σ (Table 3, p.9)",
 "Ma+2017":
  "Oxide concentrations (wt%: SiO2, TiO2, Al2O3, FeO, CaO, Na2O, K2O) with totals and one standard deviation of the "
  "mean; cations per formula unit; empirical formulae for liebermannite, lingunite and maskelynite (Table 1, p.3); "
  "calculated density (g cm-3) from the composition and cell volume (p.4)",
 "Frank+2023":
  "Oxide concentrations (wt%: SiO2, TiO2, Al2O3, Cr2O3, FeO, MnO, MgO, CaO, Na2O, K2O, P2O5, NiO) with totals "
  "(Table 1, p.6); åkermanite content of the melilite (Åk14–31, with minor Åk32–36, p.5)",
 "Broussard+2026":
  "Element concentrations in the carbonates (wt%: Fe, Mn — \"Dolomite contains 2.0 ± 0.4 wt% Fe and 3.0 ± 0.9 wt% Mn "
  "(n = 37)\", p.5); phase abundance as areal fraction of the section (areal%, e.g. sulfides \"2.3 areal%\", p.6); "
  "phase identifications from the X-ray maps (nominal)",
 "Seifert+2026":
  "Oxide concentrations in apatite (wt%: F, Cl, Na2O, MgO, SiO2, SO3, P2O5, CaO, MnO, FeO) with totals, per named "
  "grain (Table 1, p.7); the STEM EDS counterpart table reports the same suite as Fe2O3 (Table 2, p.11)",
 "Pang+2016":
  "Pyroxene end-member compositions (mol%: En, Fs, Wo — \"orthopyroxene (En33.2±0.5Fs64.5±0.6Wo2.3±0.5; based on 12 "
  "analyses)\", p.2); Ca-Eskola component (mol%: \"41 ± 8 mol% on average; based on 13 analyses\", p.4); empirical "
  "formulae for the high-pressure phases (p.4). The oxide analyses are in Supplementary Tables 1–4, not in the "
  "archived PDF",
 "McCoy+2025_SI":
  "Carbonate end-member composition (mol%: MgCO3, FeCO3, MnCO3 — calcite is \"near-end member composition (4 mol.% "
  "or less MgCO3 and FeCO3; 0.1 mol.% or less MnCO3)\", p.2); phase identifications (nominal)",
 "McCoy+2025_UA":
  "Phosphate and carbonate compositions, reported by phase rather than per point (p.2); phase identifications "
  "(nominal). The quantitative analyses are in the paper's supplementary tables, not in the archived PDF",
 "Zega+2025":
  "Sulfide composition as atomic proportions (At%: Fe + Co, S, Ni, plotted against stoichiometric sulfides — "
  "pyrrhotite compositions \"close to Fe7S8 (the 4C polytype)\", Fig. 1, p.2); modal abundance of carbonates, "
  "sulfides and magnetite (%, \"0.4–3.4%, ~3–8% and ~3–5%\", p.2) from the EMPA phase maps; phase identifications "
  "(nominal)",
 "Barnes+2025 | CRPG":
  "Mineral compositions from quantitative WDS/EDS analyses, with the element suites set per session — \"(1) Al, Ti, "
  "Ca, Cr, Mn, Ni, Mg, Fe and Si (session 1) and (2) Na, K, Al, Ti, Ca, Cr, Mn, Ni, Mg, Fe and Si (session 2)\" "
  "(p.11); the values are \"compiled in Supplementary Table 14\" (p.11), not in the archived PDF",
 "Barnes+2025 | NHM":
  "\"Major and minor element abundances\" of olivine and pyroxene (p.13), with \"Typical detection limits for "
  "transition metals were around 250 ppm\" (p.13); the derived quantity used in the paper is the olivine Mg# "
  "(\"the Mg# of olivine grains is >83\", p.13)",
}


def col(header, key):
    parts = [p.strip().lower() for p in key.split("|")]
    hits = [i for i, h in enumerate(header) if all(p in " ".join(h.split()).lower() for p in parts)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    rows = list(csv.reader(io.open(os.path.join(ROOT, REL), newline="", encoding="utf-8-sig")))
    h = rows[0]; s = h.index("Literature Assessment")
    lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
    row = next(r for r in rows if r and r[0].strip() == FIELD)
    m = {col(h, k): v for k, v in CELLS.items()}
    if len(m) != len(CELLS):
        raise SystemExit("two keys matched one column")
    unhandled = [" ".join(h[i].split())[:60] for i in lit if i not in m and not row[i].strip()]
    if unhandled:
        raise SystemExit("blank columns with no value: %s" % unhandled)
    for i, v in m.items():
        if row[i].strip():
            raise SystemExit("REFUSING: %s already holds %r" % (h[i][:40], row[i][:60]))
        row[i] = v
    kept = [" ".join(h[i].split())[:40] for i in lit if i not in m]
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), REL)
    print("  %s: %d cells -> %s" % (os.path.basename(REL), len(m), os.path.basename(new)))
    print("  already filled, left alone: %s" % (kept or "none"))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0
    with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)
    subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT, check=True, capture_output=True, text=True)
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    old = os.path.join(ROOT, REL)
    for f in (old, old[:-4] + ".xlsx"):
        if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    next(e for e in reg["composed"] if e["tapp"] == REL)["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
