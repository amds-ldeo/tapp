#!/usr/bin/env python3
"""Phase 3 for `Reported Variables and Units` — batch 2: the laser-ablation family (26 cells).

    python3 "Project Files/Scripts/phase3_reported_variables_la_20260916.py" [--apply]

Same rule as batch 1: the field is a definer, so each cell enumerates every variable the procedure
reports with its unit, derived quantities included.

WHAT AN LA PROCEDURE REPORTS is an element list and a unit, and the units are not interchangeable —
this corpus alone uses µg g-1, mg g-1, g/100 g, ppm, ppb and atomic % side by side, sometimes within
one table (Navarro 2024 reports As in µg g-1 and Fe in g/100 g). Each cell takes the unit from the
paper's own table header rather than normalising, because the unit is part of what the field records.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Reported Variables and Units"

NAKANISHI = ("Highly siderophile element abundances in metal (ppm: Ru, Rh, Pd, Re, Os, Ir, Pt, Au — e.g. \"Ir "
             "abundance ranging from 1.08 to 2.53 ppm\", p.5), with major element abundances from EPMA alongside; "
             "HSE/Ir ratios; and the Re/Os abundance ratio that feeds the reported 187Re/188Os, \"determined by the "
             "mean Re/Os abundance ratios for each of the 1–3 analytical spots measured by LA-ICP-MS\" (Table 3, p.8)")
LIU2024 = ("Trace element concentrations per element, reported as \"Mean\" with a \"95% CI\" for each sample (Table 2, "
           "p.8: Sc, V, Cr, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Ba, the REE La-Lu, Hf, Ta, Th, U), against SN-ICP-MS "
           "for the same materials; relative standard deviations are reported as the precision measure (p.9)")
LIU2025_GL = ("Au and Cu contents of the quenched silicate melt (ppm), with S content and H2O content of the starting "
              "material tabulated per run (Table 1, p.3); the derived quantity the paper reports from them is the "
              "sulfide/melt partition coefficient DAu (dimensionless, p.2)")
LIU2025_SU = ("Au and Cu contents of the quenched sulfide (ppm) per run (Table 1, p.3), which with the coexisting "
              "glass give the reported sulfide/melt partition coefficient DAu (dimensionless, p.2)")
LIU2016 = ("Trace element abundances per phase (ppm, with REE at ppb level — \"8 ppb La, 23 ppb Yb, and 6 ppb Lu\", "
           "\"Nickel contents in olivines decrease from 910 ppm at Mg# = ~80 to 234 ppm\", p.7), reported as means "
           "with 1σ and n (table p.9); limits of detection are reported per element (Table 3, p.9). Silicate and "
           "oxide abundances are normalised to 100 wt% oxide total; phosphate to EMP CaO (p.4)")
BZHANG = ("Abundances of 23 elements in metal, with mixed units in one table — P, Fe, Co and Ni in mg/g, and V, "
          "Cr, Mn, Cu, Ga, Ge, As, Mo, Ru, Rh, Pd, Sn, Sb, W, Re, Os, Ir, Pt, Au in µg/g (Table 3, p.4). Values are "
          "reported as raster averages, with spot averages in Appendix 2; for Ge, Sb, Re, Os and Ir the reported "
          "value is \"calculated from the mean of the spot average ... and the raster average\" (p.4)")
CHERN_MAP = ("Two-dimensional concentration maps per element (µg/g) for the mapped olivine crystals, held as \"2D "
             "concentration matrices of all target elements\" (p.5); the paper also reports the fayalite content "
             "\"(fayalite, Fa # = FeO/(FeO + MgO) ∙ 100, atomic %)\" from the μXRF data alongside (Table 1, p.5), and "
             "principal-component scores derived from seven normalised maps (p.6)")
CHERN_LINE = ("Major and trace element concentrations along the scan (µg/g), reported as profiles from olivine rim to "
              "core and as tabulated compositions (Table 1, p.5); Fa# \"(fayalite, Fa # = FeO/(FeO + MgO) ∙ 100, "
              "atomic %)\" is reported with them (p.5)")
CHERN_PH = ("Trace element concentrations in the phosphate grains (µg/g), reported per named grain with the mineral "
            "identified as stanfieldite or merrillite (nominal) and each single parallel measurement listed "
            "(Table 2, p.10)")
MITTLE = ("Trace element concentrations in pallasite olivine (µg/g), reported as average analyses per sample with "
          "dispersion, the measured nuclides being \"25Mg, 27Al, 31P, 43Ca, 44Ca, 45Sc, 47Ti, 49Ti, 51V\" and "
          "others (p.5); P2O5 content is estimated where P was not in the protocol (\"the P2O5 content was probably "
          "~1.5 wt%\", p.3)")
NAVARRO_SP = ("Elemental mass fractions in metal, with units mixed by magnitude — As, Au, Co, Cu, Ga, Ge, Ir, Pd, Ru "
              "and others in µg g-1, Fe and Ni in g/100 g (Table 5, p.12) — reported with 2 sdm; the derived output "
              "is the meteorite's chemical classification (nominal, Table 1, p.2)")
NAVARRO_MAP = ("Elemental mass fractions per phase, obtained by integrating 176 kamacite points over 211,060 µm2 and "
               "1,173 plessite points over 1,712,297 µm2 — As, Au, Co, Cu, Ga, Ge, Ir, Pd, Ru in µg g-1 and Fe, Ni in g/100 g, "
               "each with 2 sdm and the integrated area and point count (Table 5, p.12); phase identification from "
               "the maps (nominal)")

LAQ = {"Nakanishi": NAKANISHI, "Liu et al. 2024": LIU2024,
       "Liu et al. 2025 (GCA 393) Experimental silicate glass": LIU2025_GL,
       "Liu et al. 2025 (GCA 393) Experimental sulfide": LIU2025_SU,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Silicates": LIU2016,
       "Liu et al. 2016 (M&PS 51) Tissint martian meteorite Phosphate": LIU2016}
LASF = {"Zhang et al. 2022 (GCA 323)": BZHANG,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Raster": CHERN_MAP,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite olivine Line": CHERN_LINE,
        "Chernonozhkin et al. 2021 (Chem Geol 562) Pallasite phosphate": CHERN_PH,
        "Mittlefehldt": MITTLE,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Spot": NAVARRO_SP,
        "Navarro et al. 2024 (ACS ESC 8) Iron meteorites Raster": NAVARRO_MAP}

CELLS = {
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v86.csv": dict(LAQ),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v86.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v83.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v84.csv": dict(LASF),
}


def col(header, key):
    k = " ".join(key.split()).lower()
    hits = [i for i, h in enumerate(header) if " ".join(h.split()).lower().startswith(k)]
    if len(hits) != 1:
        raise SystemExit("column key %r matched %d columns" % (key, len(hits)))
    return hits[0]


def main(apply=False):
    plan = []
    for rel, cells in CELLS.items():
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        lit = [i for i in range(s + 1, len(h)) if h[i].strip()]
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        m = {col(h, k): v for k, v in cells.items()}
        if len(m) != len(cells):
            raise SystemExit("%s: two keys matched one column" % rel)
        unhandled = [" ".join(h[i].split())[:60] for i in lit if i not in m and not row[i].strip()]
        if unhandled:
            raise SystemExit("%s: blank columns with no value: %s" % (rel, unhandled))
        for i, v in m.items():
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = v
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, len(m)))
        print("  %-40s %2d cells -> %s" % (os.path.basename(rel), len(m), os.path.basename(new)))
    print("\n  %d cells in %d TAPPs" % (sum(p[3] for p in plan), len(plan)))
    if not apply:
        print("(dry run — pass --apply to write)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for rel, new, rows, _ in plan:
        with io.open(os.path.join(ROOT, new), "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        subprocess.run([sys.executable, XLSX, os.path.join(ROOT, new)], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        next(e for e in reg["composed"] if e["tapp"] == rel)["tapp"] = new
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),
                        "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  written; parked; registry advanced; mirror:", (p.stdout.strip().splitlines() or ["synced"])[-1][:70])
    return 0


sys.exit(main("--apply" in sys.argv))
