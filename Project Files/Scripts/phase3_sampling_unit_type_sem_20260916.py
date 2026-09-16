#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Type` — batch 3: the SEM family (70 cells, 4 TAPPs).

    python3 "Project Files/Scripts/phase3_sampling_unit_type_sem_20260916.py" [--apply]

Same source rule and cell grammar as batches 1-2. SEM carries 35 procedure columns; SEM_Composition
(9), SEM_FIBSEM (8) and SEM_Imaging (18) carry subsets under identical headers, so one value per
procedure fills all four TAPPs and shared columns stay byte-identical.

WHAT THE TYPE IS, FOR SEM. The procedure's own product decides it, and the four products differ:
  * imaging (SE, BSE) reports the imaged field — a region of interest on a section, or the section;
  * EDS point analysis reports a point inside a phase or grain;
  * mapping (EDS, CL) reports the mapped area, read for the phases it resolves;
  * FIB sample preparation reports the section it produces, cut out of a named particle or grain;
  * 3D tomography reports the serial-sectioned volume.

Barnes 2025's BSE and two FIB columns describe procedures the paper does not contain — as their own
`Additional Notes` record — so those three cells are N, exactly as in the `Sampling Unit Name` pass.
Unlike that pass, Zega 2025's laboratory cells are NOT N here: a passage can state what kind of unit
it worked on without naming it, and each of these does.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Type"
FILES = ["SEM/SEM_TAPP_v69.csv", "SEM/SEM_Composition_TAPP_v68.csv", "SEM/SEM_FIBSEM_TAPP_v35.csv",
         "SEM/SEM_Imaging_TAPP_v34.csv"]

GENGE = ("the NG-1 section, with settings given per phase (\"12 kV for metals and 10 kV for silicates and "
         "oxides, beam current at 10 nA for metals and 5 nA for silicates and oxides\", p.2)")
IZAWA_SECTION = "\"polished thin sections\" of Tagish Lake (p.2)"
LIU_COAL = "the polished coal blocks \"#1\" and \"#2\" (Table 1, p.2)"
PASC = ("the \"NWA 7317 slab\", a \"small fragment of about 10 × 6 mm\" embedded in epoxy and polished "
        "(pp.3–4)")
BARNES_NONE = "N — this procedure is not described in the paper (see Additional Notes)"

VALUES = [
    (("Garvie et al. 2008", "| SE Imaging"),
     "Grain (individual carbonaceous nanoglobule) — \"low voltage scanning electron microscopy (SEM) was used to "
     "characterize the globule forms and external structures\" (p.1) of globules on an Al-SEM stub (p.2)"),
    (("Garvie et al. 2008", "TEM Sample Preparation"),
     "Grain (individual nanoglobule) > Sub-volume (FIB cross-section) — \"The internal structure of the globules was "
     "investigated after sectioning by focused ion beam (FIB) milling\" (p.1)"),
    (("Genge et al. 2025", "BSE Imaging"),
     "Whole sample (the NG-1 section) > Phase — BSE imaging was used \"to determine the composition and structure of "
     "the Al-Cu alloy phases and associated minerals\" in " + GENGE),
    (("Genge et al. 2025", "EDS Point Analysis"),
     "Phase > Analysis point — \"quantitative EDS analyses\" of the alloy phases and associated minerals in " + GENGE),
    (("Genge et al. 2025", "EBSD"),
     "Phase > Grain — \"Electron back-scatter diffraction (EBSD) analyses were operated at 20 kV and 6 nA in focused "
     "beam mode\", the beam \"several nanometers in diameter\" with \"~30 nm\" resolution for diffracted electrons, "
     "run for \"Structural information\" on the alloy phases (p.2)"),
    (("Gucsik et al. 2013", "CL Mapping"),
     "Grain > Region of interest (core and rim) — CL was measured on \"seven representative grains (designated as B-1 "
     "through B-7)\" (p.2); \"CL spectra of red luminescent forsterite grains\" are reported against their cores, which "
     "\"show CL blue luminescence\" (p.1)"),
    (("Gucsik et al. 2013", "EDS Point Analysis"),
     "Grain > Analysis point — \"Semiquantitative analyses\" on the same \"seven representative grains (designated as "
     "B-1 through B-7)\" of a Kaba thin section (p.2)"),
    (("Izawa et al. 2010", "CL Mapping"),
     "Whole sample (polished thin section) > Region of interest — \"colour SEM-CL analysis of polished thin sections\" "
     "(p.1), reported as CL zoning within named textural components, \"relict CAI spinel, in chondrule and AOA "
     "forsterite, and in calcite nodules\" (p.1)"),
    (("Izawa et al. 2010", "BSE Imaging (Leo 440)"),
     "Whole sample (polished thin section) > Phase — \"Backscattered electron images and EDX element maps of the "
     "Tagish Lake sections were acquired with the Leo 440 SEM\", providing \"graphical representations of elemental "
     "distribution\" (p.3)"),
    (("Izawa et al. 2010", "EDS Mapping (Leo 440)"),
     "Whole sample (polished thin section) > Phase — \"full spectral imaging, recording all X-rays collected from each "
     "pixel location\" over " + IZAWA_SECTION + ", read as elemental distribution (p.3)"),
    (("Izawa et al. 2010", "BSE Imaging (Leo 1540"),
     "Region of interest — \"High-resolution BSE imaging ... carried out with the Leo 1540 FIB/SEM CrossBeam field "
     "emission SEM\" (p.3), used for \"higher resolution SEM-BSE mapping to document smaller scale relationships\" "
     "within " + IZAWA_SECTION),
    (("Izawa et al. 2010", "EDS Point Analysis (Leo 1540"),
     "Phase > Analysis point — \"High-resolution BSE imaging and EDX spot analysis were carried out with the Leo 1540 "
     "FIB/SEM CrossBeam field emission SEM\" (p.3)"),
    (("Liu et al. 2017", "3D Tomography"),
     "Sub-volume (FIB-SEM serial-sectioning volume) > Phase (pore types) — the volume supports \"a three dimensional "
     "(3D) pore network model, which was further used to characterize the pore connectivity\" (p.1), with pores "
     "classified as coalification-related and mineral-related (p.1); the model \"only focuses on the coal sample #1\" "
     "(p.8)"),
    (("Liu et al. 2017", "| SE Imaging (ESEM Quanta 250)"),
     "Whole sample (polished coal block) > Phase (pore types) — \"Electron microscopy observations further revealed "
     "there are coalification-related pores and mineral-related pores in the high-rank coal\" (p.1), imaged on "
     + LIU_COAL),
    (("Liu et al. 2017", "| SE Imaging (FESEM SUPRA 55)"),
     "Whole sample (polished coal block) > Phase (pore types) — higher-resolution imaging of the same pore types "
     "(p.1) on " + LIU_COAL),
    (("Ma et al. 2017", "BSE Imaging"),
     "Whole sample (section 126A) > Phase — the SEM was used \"to characterize chemical compositions and structures of "
     "minerals in section 126A\" (p.1); the metal assemblages are shown as whole-section context (Fig. 2, p.3)"),
    (("Ma et al. 2017", "EBSD"),
     "Grain (single crystal) — one pattern per crystal, \"EBSD patterns of (a) the type hollisterite crystal, indexed "
     "with the C2/m Fe3Al structure\" (Fig. 3, p.3), each returning that crystal's cell parameters (p.3)"),
    (("Pascucci et al. 2026", "BSE Imaging"),
     "Whole sample (polished slab) > Phase — BSE images \"were used at high vacuum mode at 20.00 kV accelerating "
     "voltage\" (p.3) on " + PASC),
    (("Pascucci et al. 2026", "EDS Point Analysis"),
     "Phase > Analysis point — \"semi-quantitative analyses with virtual standards present within the INCA software\" "
     "(p.3), to \"determine its elemental composition\" for " + PASC),
    (("Pascucci et al. 2026", "EDS Mapping"),
     "Whole sample (polished slab) > Phase — elemental mapping of " + PASC + ", acquired on \"almost the same portion "
     "of the VIS-IR SPIM images\" (p.4) so the two datasets can be compared pixel for pixel"),
    (("Pascucci et al. 2026", "| SE Imaging"),
     "Whole sample (polished slab) > Region of interest — \"Secondary electrons were used to construct images enlarged "
     "up to ×200,000 and resolved up to 5 nm\" (p.3) on " + PASC),
    (("Zhou et al. 2017", "3D Tomography"),
     "Sub-volume (FIB-SEM serial-sectioning volume) > Phase (pore types) — \"an area within the coal sample was "
     "selected for FIB-SEM tomography\" on \"cuboidal-shaped 0.5 × 1 × 1 cm3 coal samples\", and \"~800 SEM images of "
     "FIB slices were obtained\" at a \"pixel-size of 14.8 × 14.8 nm\" (pp.3–4)"),
    (("Zega et al. 2025", "BSE Imaging (JEOL 7600F"),
     "Region of interest — \"Characterization of regions of interest was performed at an accelerating voltage of 15 kV "
     "using both secondary electron (SE) and low-angle backscattered electron imaging modes\", on a particle "
     "\"attached to an Al cylinder SEM mount\" (p.9)"),
    (("Zega et al. 2025", "EDS Point Analysis (JEOL 7600F"),
     "Region of interest > Analysis point — \"The Oxford AZtec 'Point & ID' programme was used for the acquisition of "
     "images and point spectra\" (p.9)"),
    (("Zega et al. 2025", "| SE Imaging (Hitachi S-4800"),
     "Whole sample (polished section) > Region of interest — \"SE and BSE images were acquired using a Hitachi S-4800 "
     "SEM\" on \"Polished sections\" (p.9); the imaged fields are not labelled"),
    (("Zega et al. 2025", "BSE Imaging (Hitachi S-4800"),
     "Whole sample (polished section) > Region of interest — \"SE and BSE images were acquired using a Hitachi S-4800 "
     "SEM\" on \"Polished sections\" (p.9); the imaged fields are not labelled"),
    (("Zega et al. 2025", "EDS Mapping (Hitachi S-4800"),
     "Whole sample (particle) > Phase — \"The compositional heterogeneity of the particles was assessed through EDS "
     "mapping\" (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G3"),
     "Grain (Bennu particle) > Sub-volume (FIB section) — \"All sections were extracted from varied regions of matrix "
     "within the particles\" (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Helios G4 UX"),
     "Grain (Bennu particle) > Sub-volume (FIB section) — \"Bennu particles were placed on PELCO carbon conductive "
     "tabs\" for extraction (p.9)"),
    (("Zega et al. 2025", "TEM Sample Preparation (Quanta3D600"),
     "Grain (Bennu particle) > Sub-volume (FIB section) — \"FIB sections were prepared from particles dispersed on "
     "conductive carbon dots on Al SEM pin mounts\" (p.10)"),
    (("Zega et al. 2025", "CL Mapping"),
     "Whole sample (particle thin section) > Region of interest — panchromatic and monochromatic CL imaging of \"Bennu "
     "particle thin sections\", the emitting volume reaching \"up to 230 nm below the bombarded sample surface and "
     "around to 200 nm sideways\" (p.9)"),
    (("Barnes et al. 2025", "EDS Mapping (JEOL 7600F"),
     "Grain (presolar grain) > Phase — EDS was used on grains first found by NanoSIMS raster imaging of "
     "\"aggregate QL material pressed onto a gold (Au) foil mount\": \"Two O-rich presolar grains were also analysed "
     "by SEM-EDS to further constrain the phase and to confirm the phase identifications\" (pp.10–11)"),
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
