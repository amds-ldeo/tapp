#!/usr/bin/env python3
"""Phase 3 for `Reported Variables and Units` — batch 3: the SEM family (70 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_reported_variables_sem_20260916.py" [--apply]

Same rule as batches 1-2: the field is a definer, so each cell enumerates every reported variable
with its unit, derived quantities included.

THE SEM FAMILY IS WHERE THE FIELD'S "nominal property" CLAUSE EARNS ITS PLACE. Half of these
procedures report no magnitude at all: an imaging procedure reports a morphology, a phase
identification, a texture. The description says to record the variable and mark it as nominal, so
these cells read e.g. "Globule morphology and internal structure (nominal)". That is a real value,
not an N — the procedure does report something, it simply has no unit.

Barnes 2025's three absent procedures stay N, as in every pass on this corpus.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Reported Variables and Units"
FILES = ["SEM/SEM_TAPP_v72.csv", "SEM/SEM_Composition_TAPP_v71.csv", "SEM/SEM_FIBSEM_TAPP_v38.csv",
         "SEM/SEM_Imaging_TAPP_v37.csv"]

GUCSIK_CL = ("Cathodoluminescence emission bands, reported by wavelength (nm) and colour — \"two broad emission bands "
             "at approximately 630 nm (impurity center of divalent Mn ions) in the red region and above 700 nm "
             "(trivalent Cr ions) in the red–IR region\", with grain cores giving \"a characteristic broad band "
             "emission at 400 nm\" (p.1); the CL colour and its spatial zoning are nominal properties")
IZAWA_CL = ("Cathodoluminescence colour and zoning (nominal), recorded through four spectral channels — \"red "
            "(600–850 nm, including near-infrared from 700–850 nm), green (500…\", detected \"in the range 300–850 "
            "nm\" (p.3); the reported result is CL zoning in relict CAI spinel, chondrule and AOA forsterite and "
            "calcite nodules (p.1)")
IZAWA_MAP = ("Elemental distribution as X-ray maps (counts per pixel, \"full spectral imaging, recording all X-rays "
             "collected from each pixel location\", p.3) and the phase identifications read from them (nominal); "
             "BSE images give the accompanying textural relationships (nominal)")
LIU_PORE = ("Pore volume percent by pore class (vol%: macropores, mesopores, micropores — \"Volume percent of pores of "
            "these high-rank coals are dominated by mesopores of approximately 10–50 nm in width\", p.1); pore width "
            "(nm); pore type and connectivity (nominal: coalification-related vs mineral-related, \"mesopore-dominated "
            "pore network\", p.1)")
PASC_COMP = ("Atomic proportions of the constituent elements (%), from which \"mineral phases were determined from "
             "atomic proportions in percentages (%) of constituent elements and compared to the atomic proportions of "
             "constituent elements in stoichiometric proportions\" (p.4); the phase identification is the nominal "
             "output")
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"),
     "Globule morphology, size and surface structure (nominal, with sizes in µm) — the imaging is used \"to "
     "characterize the globule forms and external structures\" (p.1)"),
    (("Garvie et al. 2008", "TEM Sample Preparation"),
     "Internal structure of the sectioned globules (nominal) — \"The FIB-SEM analysis shows that the globules range "
     "from solid to hollow. Some hollow globules show a central open core, with adjoining smaller cores\" (p.1)"),
    (("Genge et al. 2025", "BSE Imaging"),
     "Texture and phase distribution (nominal), with grain sizes in µm and a modal estimate by area — e.g. \"subhedral "
     "crystals of Fe-bearing olivine (Fa11–25, 37 vol %), up to 10.8 µm in size\" (p.2)"),
    (("Genge et al. 2025", "EDS Point Analysis"),
     "Phase compositions as normalised analyses, with the olivine reported by fayalite content (Fa11–25) and "
     "\"Phase identification ... determined using normalised analyses, since the stoichiometry provides an adequate "
     "confirmation of analysis quality\" (p.2); phase identification is the nominal output"),
    (("Genge et al. 2025", "EBSD"),
     "Crystal structure and orientation of the alloy phases (nominal), acquired for \"Structural information\" at 20 kV "
     "and 6 nA with ~30 nm spatial resolution for the diffracted electrons (p.2)"),
    (("Gucsik et al. 2013", "CL Mapping"), GUCSIK_CL),
    (("Gucsik et al. 2013", "EDS Point Analysis"),
     "Mineral compositions of the seven analysed grains, reported for the olivine as forsterite content "
     "(\"Fo: 99.2–99.7\", p.1), with WDS X-ray distribution maps alongside; detection limits are stated per element "
     "(\"ranged between 0.03 (light element…\", p.2)"),
    (("Izawa et al. 2010", "CL Mapping"), IZAWA_CL),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"), IZAWA_MAP),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"), IZAWA_MAP),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"),
     "Textural relationships at higher resolution (nominal) — the stage is \"higher resolution SEM-BSE mapping to "
     "establish spatial context for textural variation\" (p.2), reporting mineralogy and texture rather than a "
     "magnitude"),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"),
     "Elemental compositions of the analysed phases, used with the μXRD and CL data for phase identification "
     "(nominal); the EDX system detects \"all elements from C to U, with a detection limit of 0.5 wt% for most "
     "elements\" (p.3)"),
    (("Liu et al. 2017", "3D Tomography"),
     LIU_PORE + "; the 3D pore-network model reports pore connectivity for coal sample #1 (p.8)"),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"),
     "Pore type and morphology (nominal: \"secondary gas pores in organic matter and shrinkage-induced pores around "
     "quartz and clay minerals\", \"dissolution-created pores and intercrystalline pores\", p.1), with pore sizes in nm"),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"),
     "Pore type and morphology at higher resolution (nominal), with pore sizes in nm — \"the shrinkage-induced pores "
     "are mainly mesopores\" (p.1)"),
    (("Ma et al. 2017", "BSE Imaging"),
     "Textural relationships and phase assemblage (nominal) — the imaging documents the metal assemblage in which the "
     "new minerals occur, with grain sizes in µm (Fig. 2, p.3)"),
    (("Ma et al. 2017", "EBSD"),
     "Crystal structure identification with unit-cell parameters (Å and Å3) and the fit quality as mean angular "
     "deviation (degrees) — e.g. \"with a mean angular deviation of 0.30°~0.45°, revealing the cell parameters: "
     "a = 15.60 Å, b = 7.94 Å, c = 12.51 Å\" and cell volume (p.3)"),
    (("Pascucci et al. 2026", "BSE Imaging"),
     "Textures and phase distribution across the slab (nominal), imaged at 20.00 kV and mosaicked into 10 BSE images "
     "covering the SPIM area (p.3)"),
    (("Pascucci et al. 2026", "EDS Point Analysis"), PASC_COMP),
    (("Pascucci et al. 2026", "EDS Mapping"),
     "Elemental maps for \"Si, Fe, Ca, Al, and S elements, since these five are sufficient to discriminate all mineral "
     "phases present in the sample\" at 3 μm resolution (p.6); the mineral map derived from them is the nominal "
     "output"),
    (("Pascucci et al. 2026", "| SE Imaging"),
     "Surface topography and texture (nominal), imaged \"enlarged up to ×200,000 and resolved up to 5 nm\" (p.3)"),
    (("Zhou et al. 2017", "3D Tomography"),
     "Pore-space volume as voxel counts (\"total voxel numbers of 28,944 and 83,866\", p.1); pore diameter (nm, with "
     "both samples predominantly showing closed-pore diameters of 10–50 nm, p.1); pore connectivity and pore "
     "type (nominal), from ~800 serial FIB slices at 14.8 × 14.8 nm pixel size (pp.3–4)"),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"),
     "Particle textures and phase occurrences (nominal), with grain sizes in µm — angular, hummocky and other particle "
     "types imaged for the regions of interest (Fig. 1, p.2)"),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"),
     "Phase compositions from point spectra, reported with the EMPA data as atomic proportions (At%: Fe + Co, S, Ni for "
     "the sulfides, Fig. 1, p.2); phase identification is the nominal output"),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"),
     "Particle surface morphology and texture (nominal) — pitted sulfide surfaces and particle shapes (p.2)"),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"),
     "Phase distribution and texture within the polished sections (nominal), with grain sizes in µm (Fig. 1, p.2)"),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"),
     "Elemental maps used to assess \"The compositional heterogeneity of the particles\" (p.9); the phases resolved "
     "from them are the nominal output"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"),
     "Electron-transparent sections ~100 nm thick (\"final thinning at 5 kV until the sections were ~100 nm thick\", "
     "p.10) — the reported product is the section itself and its location within the particle (nominal)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"),
     "Electron-transparent sections for TEM analysis — the reported product is the section and its provenance "
     "(nominal); no measured variable is reported by this procedure (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"),
     "Electron-transparent sections for TEM analysis — the reported product is the section and its provenance "
     "(nominal); no measured variable is reported by this procedure (p.10)"),
    (("Zega et al. 2025", "CL Mapping"),
     "Panchromatic and monochromatic CL images, and hyperspectral CL, collected at 5 keV with 1–4 nA (p.9); the "
     "reported result is luminescence zoning within carbonate grains, e.g. \"a core-shell texture, with Fe–Mn-rich "
     "magnesite (M) non-luminescent crystals forming the core\" (Fig. 6, p.6) — nominal"),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"),
     "Elemental composition of the two presolar grains, used \"to further constrain the phase and to confirm the phase "
     "identifications made based on the NanoSIMS data\" (p.11); the reported output is the phase assignment (nominal: "
     "silicate vs oxide)"),
    (("Barnes et al. 2025", "BSE Imaging (FEI Quanta"), BARNES_NONE),
    (("Barnes et al. 2025", "TEM Sample Preparation (FEI Helios G4"), BARNES_NONE),
    (("Barnes et al. 2025", "TEM Sample Preparation (FEI Helios 660"), BARNES_NONE),
]


def value_for(header):
    hs = " ".join(header.split())
    hits = [v for parts, v in VALUES if all(p in hs for p in parts)]
    if len(hits) != 1:
        raise SystemExit("header %r matched %d value entries" % (hs[:90], len(hits)))
    return hits[0]


def main(apply=False):
    plan, used = [], set()
    for rel in FILES:
        rows = list(csv.reader(io.open(os.path.join(ROOT, rel), newline="", encoding="utf-8-sig")))
        h = rows[0]; s = h.index("Literature Assessment")
        row = next(r for r in rows if r and r[0].strip() == FIELD)
        n = 0
        for i in range(s + 1, len(h)):
            if not h[i].strip():
                continue
            if row[i].strip():
                raise SystemExit("REFUSING: %s %s already holds %r" % (rel, h[i][:40], row[i][:60]))
            row[i] = value_for(h[i]); used.add(" ".join(h[i].split())); n += 1
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((rel, new, rows, n))
        print("  %-32s %2d cells -> %s" % (os.path.basename(rel), n, os.path.basename(new)))
    print("\n  %d cells in %d TAPPs; %d distinct procedure columns" % (sum(p[3] for p in plan), len(plan), len(used)))
    if len(used) != len(VALUES):
        raise SystemExit("PREMISE: %d value entries but %d distinct columns" % (len(VALUES), len(used)))
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
