#!/usr/bin/env python3
"""Phase 3 for `Pre-Analysis Imaging and Screening` — batch 4: TEM (21 cells), completing the field.

    python3 "Project Files/Scripts/phase3_pre_analysis_imaging_tem_20260916.py" [--apply]

Same source rule and boundary as batches 1-3. With this batch the field is complete, and with it the
last of the four fields that were blank on all 131 in-situ columns.

TEM ALWAYS HAS A PRIOR STEP, because the specimen has to be made: something must be imaged to decide
where to cut. Most of these papers say so — SEM/FIB imaging of the target grain (Chaves 2023, Cymes
2023, Matsumoto 2021), an optical microscope search across 25 glass beads (Zeng 2024), SEM/EDS phase
identification in the polished section (Dobrica 2022), CL imaging of zoning (Seifert 2026), regions
of interest picked in the SEM (Thompson 2020). Where the paper does not describe that step, the cell
is N and says what it describes instead.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Pre-Analysis Imaging and Screening"
REL = "TEM/TEM_TAPP_v57.csv"

MATS = ("FE-SEM imaging of the soil grains before sectioning — grains were coated with 3 nm of osmium and observed "
        "\"using a field-emission (FE) scanning electron microscope (JSM-7001F) at Kyushu University\", with "
        "\"Secondary high-resolution electron imaging ... at a low accelerating voltage of 2.0 kV under high vacuum\" "
        "and EDX \"used to determine the mineral phases on the grain\" (p.2); the section was then cut where the iron "
        "sulfides are exposed (p.3)")
SEIFERT = ("SEM EDS mapping and CL imaging at JSC — apatite grains \"were identified via EDS mapping and point "
           "analysis\", then \"CL images were obtained for each apatite grain to search for zoning or internal "
           "structures not resolvable in EDS maps\" (p.2); the FIB cut was placed across two grains chosen for that "
           "zoning, with the transect \"indicated by the dashed white line\" on the BSE image and the CL image shown "
           "\"before preparation of the FIB section\" (Fig. 5, p.9)")
CYMES = ("FIB-SEM imaging of the dispersed soil grains — \"The soil grains were dispersed onto a carbon-tape substrate "
         "adhered to an Al pin-stub and coated with ~80 nm of amorphous carbon for focused ion beam (FIB)-scanning "
         "electron microscope (SEM) analysis. An individual grain ~10 lm in size was identified and prepared with an "
         "FEI Helios G3 Dual Beam FIB-SEM\" (p.3); the SE image acquired during preparation shows the section site "
         "(Fig. 1, p.3)")
ZEGA_LAB = ("N — this laboratory's passage describes its instrument and conditions only; the imaging that precedes the "
            "sectioning is reported for the SEM and FIB laboratories (p.9)")

CELLS = {
 "Chaves2023":
  "FIB-SEM imaging of the irradiated pellets — \"To analyze the surface morphology and texture of the magnetite "
  "samples after laser or ion irradiation and to prepare electron transparent samples suitable for TEM, we used a "
  "Thermo Scientific Helios G4 UX DualBeam FIB-SEM at Purdue University. We compared textural differences between the "
  "irradiated and unirradiated areas\" (p.3), and the grains large enough to section were chosen from those images",
 "Zega2025|HF5000": ZEGA_LAB,
 "Zega2025|TitanX": ZEGA_LAB,
 "Zega2025|Talos":
  "N — this laboratory crushed its material onto a grid (\"TEM samples were prepared by crushing the grain\", p.10); "
  "no imaging or screening precedes that step",
 "Zega2025|2500SE": ZEGA_LAB,
 "Matsumoto2021|Tecnai": MATS,
 "Matsumoto2021|JEM-3200FSK": MATS,
 "Matsumoto2021|ARM200F": MATS,
 "KellerBerger2014":
  "N — the particles were embedded and ultramicrotomed directly (\"Both particles were embedded in low-viscosity epoxy "
  "and thin sections (approximately 60-nm thick) were prepared using ultramicrotomy\", p.2); no prior imaging or "
  "screening is described",
 "Zeng2024":
  "Optical microscopy across the bead population, then SEM — \"Twenty-five micrometric-sized glass beads (~50 to 400 "
  "μm in diameter) were chosen from these soil samples\", and \"A micrometeorite impact crater was observed on the "
  "surface of one of these 25 glass beads (CE5C0600YJFM00304) using an optical microscope. This glass bead was then "
  "placed onto conductive glue, coated with gold and then characterized by various in situ analytical techniques, "
  "including scanning electron microscopy (SEM), focused ion beam (FIB) imaging and TEM\" (p.5); BSE and SE images "
  "were collected on the FEI Scios before the foil was cut (p.6)",
 "Dobrica2022|Titan G2":
  "SEM/EDS identification in the polished section — the sections were cut at phases \"identified in the polished "
  "section by SEM/EDS\", avoiding \"the regions that were the least damaged by the ion microprobe measurements "
  "performed during previous studies\" (p.3); BSE micrographs show the external and polished surfaces and the "
  "extraction sites as white rectangles (Fig. 1, p.3)",
 "Dobrica2022|TitanX":
  "SEM/EDS identification in the polished section — the same four sections, cut at carbonates and other secondary "
  "phases \"identified in the polished section by SEM/EDS\" (p.3), of which the carbonate-bearing ones carry this "
  "laboratory's maps (Fig. 5, p.7)",
 "Singerling2025":
  "N — the particle was crushed onto a grid and the fine particles taken as they came: \"We did not use any specific "
  "parameters in selecting which particles to investigate (i.e., they were selected arbitrarily)\" (p.2)",
 "Thompson2020":
  "SEM survey on the FIB-SEM, used to pick the section sites — \"We investigated the surface morphology and "
  "composition of irradiated regions of the 1 and 5 lasered samples using the FEI Quanta 3D focused ion beam scanning "
  "electron microscope (FIB-SEM) at JSC. We identified regions of interest in the SEM for further investigation in the "
  "TEM\" (p.4); reflectance, FTIR and Mössbauer spectra were also collected on the same chips before sectioning "
  "(pp.3–4)",
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE": SEIFERT,
 "Seifert2026|HF5000": SEIFERT,
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos":
  "BSE imaging and FIB site selection — \"Back-scattered electron image of CE5C0400YJFM00505-G1. The green rectangle "
  "indicates the FIB site\" (Fig. 1 caption, p.3), and the same for grain G2 (Fig. 3, p.4); the foils were then "
  "characterized in sequence by FE-STEM, scanning Auger nanoprobe and TEM-EELS (p.2)",
 "Mo2022|HF5000":
  "The earlier analyses on the same foil — \"The same FIB foil extracted from CE5C0400YJFM00505-G1 for the AES "
  "analysis was also analyzed using TEM-EELS\" (p.5), the foil having been sited from the BSE image (Fig. 1, p.3)",
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
    print("  %s: %d cells -> %s (%d N)" % (os.path.basename(REL), len(m), os.path.basename(new),
                                           sum(1 for v in CELLS.values() if v.startswith("N "))))
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
