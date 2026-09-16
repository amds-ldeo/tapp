#!/usr/bin/env python3
"""Phase 3 for `Sampling Unit Type` — batch 4: TEM (21 cells), completing the field.

    python3 "Project Files/Scripts/phase3_sampling_unit_type_tem_20260916.py" [--apply]

Same source rule and cell grammar as batches 1-3. With this batch every `Sampling Unit Type`
literature cell in the library is filled: 131 in this pass, on top of the Solution and Lab-XCT
columns that were done when those TAPPs were built.

WHAT THE TYPE IS, FOR TEM. Almost always the electron-transparent specimen, with the level below it
named: the FIB section is the unit, and the paper reports phases, grains or regions inside it. Two
departures, both stated by their papers — Keller & Berger 2014 ultramicrotomes whole particles and
reports spectrum images of individual grains, and Singerling 2025 crushes a particle onto a grid and
reports grains. Xing 2023 is a review with no original analyses, so it is N.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-09-16"
FIELD = "Sampling Unit Type"
REL = "TEM/TEM_TAPP_v55.csv"

ZEGA = ("Sub-volume (FIB section) > Phase — the reported data are phases within a section, \"STEM-HAADF ... images of "
        "FIB sections extracted from OREX-803095-100 and OREX-803096-100\" showing \"the coarse- and fine-grained "
        "sheet silicates\" (Fig. 2 caption, p.3)")
SEIFERT = ("Sub-volume (FIB section) > Grain (apatite) — one section, \"OREX-803173-100\", carrying \"Ap. #1 and Ap. #2\" "
           "(Fig. 5 caption, p.9); compositions are tabulated per grain (Table 2, p.11)")
CYMES = ("Sub-volume (FIB section) > Grain (pyroxene) — one section carrying the grains \"1pyx\" and \"2pyx\" (p.3); "
         "\"Both EELS and EDS data were acquired as spectrum images (SI), in which a spectrum is acquired at each pixel "
         "in a given image\" (p.3)")

CELLS = {
 "Chaves2023":
  "Sub-volume (FIB section) > Region of interest (altered rim) — \"We analyzed the FIB sections using different imaging "
  "modes\" and \"collected EDS maps and profiles using a probe size of <1 nm\" (p.3); the reported profiles run across "
  "the rim and \"The underlying unaltered magnetite\" (p.7)",
 "Zega2025|HF5000": ZEGA,
 "Zega2025|TitanX": ZEGA,
 "Zega2025|Talos":
  "Grain > Phase — this laboratory did not work on a section: \"TEM samples were prepared by crushing the grain, "
  "dropping ethanol onto the resulting powder and touching a TEM copper mesh grid ... to the suspension\" (p.10), and "
  "the reported data are the phases in that material (p.3)",
 "Zega2025|2500SE": ZEGA,
 "Matsumoto2021|Tecnai":
  "Sub-volume (FIB section) > Region of interest — one section, \"11_5A_1\" (p.3); imaging is reported for named "
  "features within it, \"three (one short (1) and two long (2,3)) iron whiskers on the space-exposed surface of iron "
  "sulfides\" and the space-weathered rim beneath them (pp.3–4)",
 "Matsumoto2021|JEM-3200FSK":
  "Phase > Analysis point — \"TEM observations and quantitative EDX analysis\" of the iron sulfides in the section, "
  "quantified with \"the Cliff–Lorimer thin film approximation\" against troilite and terrestrial standards (p.3)",
 "Matsumoto2021|ARM200F":
  "Sub-volume (FIB section) > Phase — \"STEM-EDS mapping and high-resolution STEM imaging\" of the same section (p.3), "
  "read for the sulfide, metallic iron and pyroxene phases it contains (p.3)",
 "KellerBerger2014":
  "Grain > Region of interest (spectrum image) — the JEOL 2500SE \"was used to measure chemical compositions using EDX "
  "as well as to acquire quantitative elemental maps (spectrum images) of individual grains. Spectrum images contain a "
  "high-count EDX spectrum in each pixel\" (p.3), in ultramicrotome thin sections of two particles (p.2)",
 "Zeng2024":
  "Sub-volume (FIB slice) > Region of interest — one slice \"about 15 μm, 10 μm and 90–100 nm\" in size (p.6); results "
  "are reported for two regions of the impact crater rim, labelled \"Area 1\" and \"Area 2\" (Figs 1–2, p.2)",
 "Dobrica2022|Titan G2":
  "Sub-volume (FIB section) > Phase — \"Four FIB sections\" (p.2), each \"studied using a variety of TEM techniques, "
  "including scanning transmission electron microscopy (STEM) imaging, nanodiffraction, and energy-dispersive X-ray "
  "spectroscopy (EDS)\", with \"Crystalline phases ... identified by electron nanodiffraction and EDS measurements\" "
  "(p.2)",
 "Dobrica2022|TitanX":
  "Sub-volume (FIB section) > Region of interest — \"The elemental compositions of carbonates reported here were "
  "extracted from EDS mapping over areas of 5–10 nm (at the Molecular Foundry)\" (p.2), within the carbonate-bearing "
  "sections UH-001 and UH-002 (Fig. 5, p.7)",
 "Singerling2025":
  "Grain > Phase — the particle was crushed onto a grid, and \"28 fine particles\" were investigated \"within which we "
  "identified four Na,Ca carbonates: grains 4, 11 ..., 22, and 27\" (p.2); compositions come \"from TEM EDS analyses\" "
  "per grain (Table 1, p.2)",
 "Thompson2020":
  "Sub-volume (FIB section) > Phase — four sections cut from the lasered chips (p.4); EDX maps are collected \"for each "
  "sample using the 2 nm probe\" with \"The size of the EDX map areas ... optimized to prevent oversampling\" (p.4), and "
  "read for the melt layer, vesicles and Fe-Ni-S nanoparticles within it (p.6)",
 "Xing2023": "N — review article; it reports no original analyses",
 "Seifert2026|2500SE": SEIFERT,
 "Seifert2026|HF5000": SEIFERT,
 "Cymes2023|JEM-2200FS": CYMES,
 "Cymes2023|Nion": CYMES,
 "Mo2022|Talos":
  "Grain > Sub-volume (FIB foil) — one foil per lunar soil grain, \"CE5C0400YJFM00505-G1\" and \"-G2\" (Figs 1, 3, "
  "pp.3–4); \"The nanoscale composition and structure of the FIB foils were characterized using an FEI Talos F200X "
  "FE-STEM\" (p.2)",
 "Mo2022|HF5000":
  "Grain > Sub-volume (FIB foil) — \"The same FIB foil extracted from CE5C0400YJFM00505-G1 for the AES analysis was "
  "also analyzed using TEM-EELS\", reported as \"TEM-EELS point and line analysis results\" (p.5)",
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
