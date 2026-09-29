#!/usr/bin/env python3
"""SEM TAPPs: convert the remaining structured literature cells to the keyed-value notation (2026-09-29).

    python3 "Project Files/Scripts/sem_keyed_notation_20260929.py" [--apply] [--show]

Conventions 7.3.4, as the EPMA pilot applied it. SEM's structured cells are 32 Target Material and 32
Reported Variables definer cells, plus eight keyed value cells; the other keyed fields were written in the
notation by the 2026-09-29 passes, or are markers. After this pass every structured cell in the four SEM
TAPPs parses and names only definer members, so they join `KEYED_NOTATION_ENFORCED`.

  * Definer cells become a member list, then ` — ` and the original cell as commentary, so every
    transcribed quote survives. Target Material names the materials the procedure analyses, not the
    sample (EPMA's convention); the sample description moves into the commentary.
  * Value cells become `all: value` with their source quote.
  * The variants carry SEM's columns under the same labels; each cell is written where the variant holds
    the same old value, and the script stops if a variant's cell differs.

Corrected on the way (re-read against the papers):
  * Pascucci+2026 Target Species read "Mg, Si, Fe, Ni, S, Na, Ca, Al", which is not in the paper: it is
    Barnes+2025's CRPG list. The EDS map's elements are "O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni"; the spot
    analyses name none.
  * Pascucci+2026 EDS Mapping Reported Variables described the EMPA-WDS maps ("Si, Fe, Ca, Al, and S" at
    3 μm). The SEM-EDS maps are the INCA pixel maps and the Cameo+ energy-colour map.
  * Izawa+2010 BSE Imaging (Leo 440) Reported Variables described the EDX X-ray maps, which are the EDS
    Mapping column's.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "
TAPPS = ["SEM_TAPP_v", "SEM_Composition_TAPP_v", "SEM_Imaging_TAPP_v", "SEM_FIBSEM_TAPP_v"]

# SEM column number -> member list, for the two definers. The original cell follows as commentary.
TARGET_MATERIAL = {
  1: "carbonaceous nanoglobules", 2: "carbonaceous nanoglobules",
  3: "micrometeorite", 4: "Al-Cu alloy phases; associated minerals", 5: "Al-Cu alloy phases",
  6: "forsterite", 7: "constituent minerals",
  8: "carbonaceous chondrite", 9: "carbonaceous chondrite", 10: "carbonaceous chondrite",
  11: "carbonaceous chondrite", 12: "carbonaceous chondrite",
  13: "anthracite; lean coal", 14: "anthracite; lean coal", 15: "anthracite; lean coal",
  16: "hollisterite; kryachkoite; stolperite; khatyrkite; icosahedrite",
  17: "hollisterite; kryachkoite; stolperite; khatyrkite; icosahedrite",
  18: "carbonaceous chondrite", 19: "carbonaceous chondrite", 20: "carbonaceous chondrite", 21: "carbonaceous chondrite",
  22: "subbituminous coal; high-volatile bituminous coal",
  23: "Bennu particles", 24: "Bennu particles", 25: "Bennu particles", 26: "Bennu particles", 27: "Bennu particles",
  28: "fine-grained matrix", 29: "Bennu particles", 30: "Bennu particles", 31: "olivine; carbonate",
  32: "O-rich presolar grains",
}
REPORTED = {
  1: "globule morphology (nominal); globule size (µm); surface structure (nominal)",
  2: "internal structure of the sectioned globules (nominal)",
  3: "texture (nominal); phase distribution (nominal); grain size (µm); modal abundance (vol%)",
  4: "phase composition (normalised); fayalite content (Fa); phase identification (nominal)",
  5: "crystal structure (nominal); crystal orientation (nominal); cell constants (Å)",
  6: "CL emission bands (nm); CL colour (nominal); CL zoning (nominal)",
  7: "mineral composition; forsterite content (Fo)",
  8: "CL colour (nominal); CL zoning (nominal)",
  10: "elemental distribution (counts per pixel); phase identification (nominal)",
  11: "textural relationships (nominal)",
  12: "elemental composition of the analysed phases; phase identification (nominal)",
  13: "pore volume percent by pore class (vol%); pore width (nm); pore type (nominal); pore connectivity (nominal)",
  14: "pore type (nominal); pore morphology (nominal); pore size (nm)",
  15: "pore type (nominal); pore morphology (nominal); pore size (nm)",
  16: "textural relationships (nominal); phase assemblage (nominal); grain size (µm)",
  17: "crystal structure identification (nominal); unit-cell parameters (Å, Å3); mean angular deviation (degrees)",
  18: "texture (nominal); phase distribution (nominal)",
  19: "atomic proportions of the constituent elements (%); phase identification (nominal)",
  21: "surface topography (nominal); texture (nominal)",
  22: "pore-space volume (voxels); pore diameter (nm); pore connectivity (nominal); pore type (nominal); throat size (nm); throat length (µm)",
  23: "particle texture (nominal); phase occurrence (nominal); grain size (µm)",
  24: "phase composition (At%); phase identification (nominal)",
  25: "surface morphology (nominal); texture (nominal)",
  26: "phase distribution (nominal); texture (nominal); grain size (µm)",
  27: "element maps; phase identification (nominal)",
  28: "electron-transparent section (nominal); section thickness (nm)",
  29: "electron-transparent section (nominal)", 30: "electron-transparent section (nominal)",
  31: "panchromatic CL images; monochromatic CL images; hyperspectral CL; luminescence zoning (nominal)",
  32: "elemental composition of the presolar grains; phase assignment (nominal: silicate vs oxide)",
}
# Cells replaced outright: (field, SEM column) -> new value
REPLACE = {
  ("Reported Variables and Units", 9): ("textural relationships (nominal)" + D + "'Backscattered electron (BSE) imaging and elemental X-ray "
      "mapping provide graphical representations of elemental distribution' (p.3); the Leo 440's X-ray maps are recorded under the "
      "EDS Mapping column"),
  ("Reported Variables and Units", 20): ("element maps (pixel by pixel); Cameo+ energy-colour map (nominal); mineral phase map (nominal)" + D +
      "INCA gives 'a map on a pixel-by-pixel basis of the main elements (O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni) so to derive the "
      "distribution of each mineral phase'; the SEM-EDS area is '10.5 × 4.0 mm wide'. The 'Si, Fe, Ca, Al, and S' maps at 3 μm "
      "resolution are the EMPA-WDS mapping's, a different procedure"),
  ("Target Species", 19): "N" + D + "no element set is stated for the SEM-EDS spot analyses; the list 'Mg, Si, Fe, Ni, S, Na, Ca, Al' formerly here is not in the paper",
  ("Target Species", 20): ("O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni" + D + "'a map on a pixel-by-pixel basis of the main elements (O, Si, "
      "Mg, Fe, Al, P, Cr, Ca, Na, S, Ni)'; the list 'Mg, Si, Fe, Ni, S, Na, Ca, Al' formerly here is not in the paper"),
  ("Beam Current", 7): "all: 2.0 nA" + D + "'The accelerating voltage was 15 kV and the beam current was 2.0 nA, with a focused beam' (p.2)",
  ("Beam Current", 24): "all: ~900 pA" + D + "'EDS spectra were acquired at 15 kV ... with an incident beam current of ~900 pA' (p.9)",
  ("Detection Limit", 10): "all: 0.5 wt%" + D + "'with a detection limit of 0.5 wt% for most elements' (p.3), a capability of the Quartz XOne system",
  ("Primary Calibration Standard Name", 4): "all [all: Oxford factory internal standards]" + D + "'an XPP correction procedure calibrated with Oxford factory internal standards' (p.2)",
  ("Target Species Estimation Method", 19): "all: virtual standards preloaded within the Oxford INCA Energy software" + D + "'semi-quantitative analyses with virtual standards present within the INCA software' (p.3)",
  ("Target Species Estimation Method", 20): "all: virtual standards preloaded within the Oxford INCA Energy software" + D + "'semi-quantitative analyses with virtual standards present within the INCA software' (p.3)",
}


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def labels(h):
    s = h.index("Literature Assessment")
    return {" ".join(h[j].split()): j for j in range(s + 1, len(h)) if h[j].strip()}


def plan_from_sem(sem):
    """(field, label) -> (old, new), built from the SEM TAPP."""
    h = sem[0]; s = h.index("Literature Assessment")
    cols = [j for j in range(s + 1, len(h)) if h[j].strip()]
    if len(cols) != 32:
        raise SystemExit("PREMISE: SEM has %d literature columns, expected 32" % len(cols))
    by = {r[0].strip(): r for r in sem[1:] if r and r[0].strip()}
    out = {}
    for n, j in enumerate(cols, 1):
        lab = " ".join(h[j].split())
        for f, table in (("Target Material", TARGET_MATERIAL), ("Reported Variables and Units", REPORTED)):
            if n in table:
                old = by[f][j]
                if not old.strip() or old.strip() in ("N", "N/A"):
                    raise SystemExit("PREMISE: [%d] %s is %r" % (n, f, old))
                out[(f, lab)] = (old, table[n] + D + old)
        for (f, c), v in REPLACE.items():
            if c == n:
                out[(f, lab)] = (by[f][j], v)
    return out


def edit(rr, plan, report):
    lab = labels(rr[0]); by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for (f, l), (old, new) in plan.items():
        if f not in by or l not in lab:
            continue
        j = lab[l]; cur = by[f][j]
        if cur == new:
            continue
        if cur != old:
            raise SystemExit("PREMISE: [%s] %s holds %r, not SEM's %r" % (l[:60], f, cur[:60], old[:60]))
        report.append((l, f, cur, new)); by[f][j] = new
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    ents = [next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(p)) for p in TAPPS]
    plan = plan_from_sem(rows_of(os.path.join(ROOT, ents[0]["tapp"])))
    todo = []
    for e in ents:
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        report = []
        edit(rows_of(os.path.join(ROOT, rel)), plan, report)
        print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
        if "--show" in sys.argv:
            for l, f, old, v in report:
                print("    [%s] %s\n        now: %s" % (l[:60], f, v[:170]))
        todo.append((e, rel, new))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for e, rel, new in todo:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), plan, []))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed\n%s" % q.stderr[-700:])
        rp = os.path.join(ROOT, "composed_tapps.json")
        reg = json.load(io.open(rp, encoding="utf-8"))
        for x in reg["composed"]:
            if x["tapp"] == rel:
                x["tapp"] = new
        with io.open(rp, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
