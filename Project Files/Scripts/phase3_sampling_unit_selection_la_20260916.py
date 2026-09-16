#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Selection Criteria` — batch 2: the laser-ablation family (26 cells).

    python3 "Project Files/Scripts/phase3_sampling_unit_selection_la_20260916.py" [--apply]

Same source rule and the same line between this field and `Sampling Unit Type` as batch 1: a stated
rule or reason is recorded; a bare list of what was measured is not.

LA PAPERS STATE THIS FIELD FAR MORE OFTEN THAN EPMA PAPERS DO, and the reason is the technique. The
laser destroys what it samples and cannot be re-run on the same spot, so where to put it is a
decision the method section has to defend: spots picked off prior images (Nakanishi 2022,
Mittlefehldt 2024), maps placed against a μXRF survey (Chernonozhkin 2021), a grid covering a fused
glass (Liu 2024), a raster chosen over spots for representative sampling of exsolution banding
(Zhang 2022, Navarro 2024).

The one cell already filled (Wu 2023, in LA-Q only) is left alone; LA-MC is not touched.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Selection Criteria"

NAKANISHI = ("Picked off prior electron images — \"Based on the secondary electron images taken by EPMA, we "
             "selected analytical spots for LA-ICP-MS and sampling spots for micro-milling\" (p.4); the grains "
             "themselves are sorted by setting into interior, margin and isolated metal (p.1)")
LIU2024 = ("Coverage — \"Nine spot analyses ... were arranged in a grid pattern to cover the entire glass\" "
           "(p.5), the grid being the test of whether the fused disc is homogeneous")
LIU2025_GL = ("N — the paper states the beam diameter used for glasses (\"40 μm beam diameter for glasses\", p.4) "
              "but no rule for choosing where in a run product to ablate")
LIU2025_SU = ("Size — \"20 μm for sulfides, selecting grain sizes larger than 20 µm for the latter\" (p.4), so a "
              "sulfide grain is analysed only if it is wider than the beam")
LIU2016 = ("N — spots are screened after the fact, not before: \"The time-lapse plots of each spot were examined, "
           "and only the plateau region was used to quantify the trace element abundances\" (p.4). That is a "
           "rejection rule (see `Analysis Inclusion and Rejection Criteria`), not a rule for choosing units")
BZHANG = ("Representativeness of the exsolution banding — the raster \"yielded more representative sampling of the "
          "kamacite-taenite banding\", and where it \"failed to yield useful Ge abundances for Klamath Falls ... To "
          "obtain more precise Ge, a set of five 150 μm spots were analyzed ... on five of the irons\" (p.4)")
CHERN_MAP = ("Position relative to the metal-olivine rim, sited on a prior μXRF survey — \"The locations for "
             "LA-ICP-MS mapping were selected to be close to the metal-olivine rims of large olivine crystals with "
             "the laser beam rastering from the olivine rim in the direction of the olivine core\", at locations "
             "\"indicated on the larger μXRF maps as black rectangles\" (p.4)")
CHERN_LINE = ("Position relative to the metal-olivine rim — the line scans run \"from the olivine rim in the "
              "direction of the olivine core\" on large olivine crystals sited from the μXRF maps (p.4); the "
              "surface is pre-ablated before each analysis (p.3)")
CHERN_PH = ("Mineral identity, from the μXRF survey — phosphates are located as \"thin elongate inclusions in the "
            "kamacite-taenite metal matrix (e.g., μXRF map of Imilac at Fig. 1)\", the identification resting \"on "
            "the intensities of the Kα lines of the constituent major elements (Fe, Mg, Ni, Cr, S, Ca and P)\" (p.4)")
MITTLE = ("Freedom from inclusions, checked by SEM beforehand — the grains were \"low in inclusions, [but] were not "
          "devoid of them\", so \"The grains were first imaged using a scanning electron microscope (SEM) to locate "
          "regions for analysis. Regions containing surface inclusions were avoided for analysis\" (p.5)")
NAVARRO_SP = ("Phase targeting, as the stated alternative to rastering — \"depending on the specific objectives, "
              "spot sampling at specific phases may also fulfill the analytical requirements\", against the problem "
              "that irons have an \"inherent natural inhomogeneity, a result of their lamellar exsolution patterns\" "
              "(p.2)")
NAVARRO_MAP = ("Representativeness, and phase diversity — \"the approach of rastering large areas may improve "
               "representative sampling compared with spot analysis\" (p.2), and the mapping is \"conducted within "
               "regions featuring diverse phases of the Augusto Pestana meteorite\" (p.1)")

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
 "LA-Q-ICP-MS/LA-Q-ICP-MS_TAPP_v84.csv": dict(LAQ),
 "LA-Q-ICP-MS/LA-Q-ICP-MS_UPb_TAPP_v84.csv": dict(LAQ),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_TAPP_v81.csv": dict(LASF),
 "LA-SF-ICP-MS/LA-SF-ICP-MS_UPb_TAPP_v82.csv": dict(LASF),
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
