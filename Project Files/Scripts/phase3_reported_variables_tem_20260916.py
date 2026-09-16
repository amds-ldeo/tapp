#!/usr/bin/env python3
"""Phase 3 for `Reported Variables and Units` — batch 4: TEM (21 cells), completing the field.

    python3 "Project Files/Scripts/phase3_reported_variables_tem_20260916.py" [--apply]

Same rule as batches 1-3, and with this batch the field is complete: 131 cells, three of the four
in-situ corpora plus TEM.

WHAT A TEM PROCEDURE REPORTS is rarely one kind of thing. A single column usually carries three at
once: a composition (at% from EDS), a structure (d-spacings in Å or nm, indexed phases from SAED),
and a microstructure that has no unit at all (rim thickness in nm, but "amorphous", "poorly
ordered", "nanocrystalline" as nominal states). The cells record all three, because the field asks
for every reported variable and a consumer reading only the composition would miss what these papers
are actually for.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Reported Variables and Units"
REL = "TEM/TEM_TAPP_v58.csv"

ZEGA = ("Phase identifications and their structures from HRTEM and SAED (nominal, with d-spacings in nm — serpentine "
        "0.7 nm and saponite 1.0 nm, Fig. 3, p.4); phase compositions from STEM-EDS, plotted as atomic proportions "
        "(At%: Mg, Fe, Si+Al for the sheet silicates, Fig. 4, p.4); sulfide polytypes (nominal, e.g. pyrrhotite 4C, "
        "5C; Fig. 5, p.5); Fe3+/ΣFe from Fe L2,3 XANES mapping (Fig. 4, p.4)")
SEIFERT = ("Apatite compositions by STEM EDS as oxide concentrations (wt%: F, Cl, SiO2, P2O5, CaO, MnO, Fe2O3, with "
           "totals; Table 2, p.11); crystallinity and orientation from zone-axis SAED patterns (nominal, p.12); "
           "textural relationships between apatite and phyllosilicate (nominal, Figs 6–7, pp.10–12)")
CYMES = ("Iron oxidation states and their distribution from EELS spectrum imaging (nominal: \"the presence and "
         "heterogeneous distribution of Fe0, Fe2+, and Fe3+ in the exsolved pyroxene\", p.1); nanophase iron particle "
         "size and abundance (nm, compared between augite and pigeonite lamellae, p.1); lamellar and rim "
         "microstructure from BF/EF-TEM and SAED, with lamellae \"20–35 nm wide\" (p.4)")

CELLS = {
 "Chaves2023":
  "Fe and O concentrations across the altered rim (at%, from quantitative EDS maps and line profiles quantified by "
  "the Cliff-Lorimer method, p.3); rim thickness (nm — \"a ~50 nm rim on the magnetite surface\", p.9); d-spacings "
  "from HRTEM (Å: \"2.9 Å, 2.5 Å, and 1.6 Å\", p.9); and the defect microstructure as a nominal property "
  "(\"elongated defects\" in a crystalline rim, p.9)",
 "Zega2025|HF5000": ZEGA,
 "Zega2025|TitanX":
  "Elemental distributions from STEM/EDS maps acquired over minutes to hours and combined in Python (p.10), reported "
  "as phase compositions in atomic proportions (At%) and as the phases resolved from them (nominal, Fig. 4, p.4)",
 "Zega2025|Talos":
  "Phase identifications from TEM images and SAED patterns of the crushed material (nominal); compositions from "
  "STEM-HAADF and EDS with four windowless detectors, reported as atomic proportions (At%, p.10)",
 "Zega2025|2500SE": ZEGA,
 "Matsumoto2021|Tecnai":
  "Space-weathered rim structure and thickness (nm) and solar-flare track densities, from BF/DF-TEM, ADF-STEM and "
  "SAED (p.3); iron whisker morphology and crystallography (nominal, with lengths in nm, Figs 3–4, pp.3–7)",
 "Matsumoto2021|JEM-3200FSK":
  "Quantitative compositions of the iron sulfides by EDX, calculated with \"the Cliff–Lorimer thin film "
  "approximation\" against troilite and terrestrial standards (p.3); pyroxene composition reported as end-members "
  "(En8-14Wo8-21Fs66-85, p.5)",
 "Matsumoto2021|ARM200F":
  "Elemental distributions from STEM-EDX mapping and high-resolution STEM images (p.3), reported as the phases and "
  "their spatial relations — metallic iron, iron sulfides and pyroxene (nominal, Fig. 9, p.11)",
 "KellerBerger2014":
  "Quantitative elemental maps as spectrum images, \"enabling the determination of quantitative element abundances in "
  "addition to displaying the spatial distribution of major and minor elements\" (p.3); rim thickness (nm — \"a "
  "continuous approximately 50-nm thick, structurally disordered rim\", p.4); rim structure and the presence or "
  "absence of npFe and solar-flare tracks (nominal, with an upper limit of <10^9 cm-2 on track density, p.4)",
 "Zeng2024":
  "Phase identifications of the Ti-oxide deposits from FFT of BF-TEM images and their unit-cell parameters (Å and "
  "Å3, with space groups — rutile, trigonal Ti2O \"P3̅m1; a = 2.983 Å ... V = 37.01 Å3\", p.2); grain sizes (nm: "
  "rutile 2–15 nm, Ti2O 10–300 nm, p.2); compositions from TEM-EDS as atomic percentages (\"O (66.17 at% by atomic "
  "percentage) and Ti (33.83 at%)\", p.2)",
 "Dobrica2022|Titan G2":
  "Crystalline phase identifications from electron nanodiffraction with EDS (nominal, p.2); carbonate microstructure "
  "and the textural relations of the FIB sections (nominal, Figs 1–2, pp.3–5)",
 "Dobrica2022|TitanX":
  "Carbonate compositions from EDS hyperspectral maps, normalised to 100% and reported as oxide mole percentages on "
  "the MgCO3-CaCO3-(Fe + Mn)CO3 ternary (mole%, Fig. 5, p.7) — with the ranges also given in wt% (\"2.9–8.1 wt.% MnO, "
  "2.5–6.0 wt.% FeO\", p.5); the EDS detection limit is stated (p.2)",
 "Singerling2025":
  "Na,Ca carbonate compositions from TEM EDS, reported as atomic percentages and as changes in them over time "
  "(at%: \"+9.4 at.% C, +5.6 at.% F, +4.1 at.% Ca, +3.5 at.% Cl, –19 at.% O, and –4.8 at.% Na\" for grain 11, p.3); "
  "grain dimensions (nm: shortest axes 140–860 nm, longest 640–2360 nm, p.2); grain area and the areal fraction the "
  "carbonates represent (µm2, p.2); phase identifications from SAED (nominal)",
 "Thompson2020":
  "Microstructure and composition of the space-weathered rims — EDX element maps quantified for \"major and minor "
  "elements for each sample using the 2 nm probe\" (p.4); melt-layer thickness (nm: \"variably thick (100–500 nm) "
  "glassy material\", p.6); nanoparticle sizes and compositions (nm, \"ranging in size from 5 to 50 nm but typically "
  "<10 nm\", with Fe-Ni-S compositions, p.6); vesicle and melt textures (nominal)",
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE": SEIFERT,
 "Seifert2026|HF5000": SEIFERT,
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos":
  "Nanoscale composition and structure of the FIB foils from STEM with EDS (p.2), reported as elemental maps "
  "(notably Fe) and the phases resolved from them (nominal), with lattice spacings from FFT identifying olivine in a "
  "glass matrix containing np-Fe0 (Fig. 1, p.3)",
 "Mo2022|HF5000":
  "Iron oxidation state from TEM-EELS, acquired in DualEELS mode with 0.5–0.7 eV energy resolution at the zero-loss "
  "peak (p.3) and reported as Fe L3,2 spectra for point and line analyses against standard references (Figs 4–5, "
  "p.5); the derived output is the Fe0/Fe2+/Fe3+ assignment per point (nominal)",
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
    missing = [" ".join(h[i].split())[:60] for i in lit if i not in m]
    if missing:
        raise SystemExit("unmatched columns %s" % missing)
    for i, v in m.items():
        if row[i].strip():
            raise SystemExit("REFUSING: %s already holds %r" % (h[i][:40], row[i][:60]))
        row[i] = v
    new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), REL)
    print("  %s: %d cells -> %s" % (os.path.basename(REL), len(m), os.path.basename(new)))
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
