"""Two approved issues in one bump (2026-11-25): Lab-XCT gains two fields (#13), map grids get one shape (#15).

amds-ldeo/tapp#13 — SMR, 2026-11-25: "the xct analysis is good too ... Go ahead and implement". The reply
of 2026-11-23 mapped 11 of his 15 ADA keys onto existing Lab-XCT fields and proposed two new ones:
  - `Detector Gain` (Group 3, Advanced / Advanced, Adjustable, `Numeric + unit / Text`): his `imageGain`
    and the low-coverage `detectorGain` (`0.25 pF`) are one setting in detector-dependent units.
  - `Reconstructed Volume Dimensions` (Group 5, N/A / Advanced, Not carried over, `Text (free)`): the
    volume in voxels, X x Y x slices, covering `numberOfSlices` and `sliceDimensions`.
Their 14 literature cells were read from the papers in `XCT/Literature Assessment/` on 2026-11-25, not
inferred: gain is stated only in the JSC scan record (`Gain (dB): 12.0`); volume dimensions in Glavin
et al. 2023 (2000 x 2000 x 2000), Richard et al. 2019 sample A (885 x 885 x 999) and the Strathclyde
setup (2000 x 2000 x 2000, stated once for both Sample B scans); the JSC record gives slices only.

amds-ldeo/tapp#15 — SMR, 2026-11-25: "this should work, lets implement". The three confirmed points:
  1. Grid pairs stay one `Numeric pair` field each, with the order stated: X (along a scan line)
     first, Y (lines) second. Stated in every grid pair: Map Dimensions, STEM Scan Dimensions, Beam
     Raster Dimensions, Step Size / Pixel Size and Map Area.
  2. `Step Size / Pixel Size` (`Numeric (µm) / Text`) and `Map Area` (`Numeric + unit`) are retyped to
     `Numeric pair (µm x µm)`. A square grid is recorded as two equal values; the total-area form
     (`0.2 mm²`) is dropped, being the product of the pair. Map Area was left unpinned on 2026-08-26
     for want of any attested value; SMR's VNMIR records (691.2 x 1209.6 = 256 x 2.7 by 448 x 2.7) and
     Pascucci et al. 2026 (10.5 x 4.0 mm) are the evidence it waited for.
  3. SEM and SEM_Composition `EDS Map Dimensions` is renamed `Map Dimensions`, EPMA's name. The SEM
     tables map WDS as well as EDS (their Step Size says so), so the description says "X-ray map".
Literature cells are untouched: each is a paper's attestation, and every attested step or area there
already reads as one value or a width x height.

All edited fields are TAPP-owned (check_field_ownership.py, 2026-11-25). Column H is stamped on every
changed row. Recomposed (must be identical), parked, xlsx, register, mirror and schema counts refreshed,
Superseded README skeleton written. Run without --apply for a dry run.
"""

import csv, io, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton  # noqa: E402

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-11-25"
A, B, E, F = 0, 1, 4, 5          # Metadata Item, Description, Data Type, Example
PAIR_UM = "Numeric pair (µm x µm)"
PIX = "X is the number of pixels along a scan line, Y the number of lines"
STEP = "X is the step along a scan line, Y the step between lines"

RASTER_OLD = ("Dimensions of the small area over which the beam is rastered at a single analysis point, reported "
              "as width × height in µm.")
RASTER_NEW = ("Dimensions of the small area over which the beam is rastered at a single analysis point, reported "
              "as width × height in µm, X (along a scan line) first.")
AREA_OLD_B = ("Physical extent of the mapped region, given either as width × height in µm or as a total area in µm² "
              "or mm², and equal to (map width in pixels × step size) × (map height in pixels × step size). "
              "Complements the map's pixel-grid dimensions by recording the physical scale of the mapped region.")
AREA_NEW_B = ("Physical extent of the mapped region, given as width × height in µm, X (along a scan line) first, and "
              "equal to (map width in pixels × X step) × (map height in pixels × Y step). Complements the map's "
              "pixel-grid dimensions by recording the physical scale of the mapped region. A total area in µm² or "
              "mm² is not recorded: it is the product of the two values.")
SEM_STEP_OLD_B = ("Centre-to-centre distance between adjacent measurement points (WDS mapping) or pixels (EDS mapping) "
                  "in µm.")
SEM_STEP_NEW_B = ("Centre-to-centre distance between adjacent measurement points (WDS mapping) or pixels (EDS mapping) "
                  "in µm, given as X × Y: %s. A square grid is recorded with both values equal (e.g., 2.5 x 2.5)."
                  % STEP)
SEM_STEP_F = ("e.g., '0.5 µm' | '1 µm' | '2.5 µm' | '10 µm (automated mineralogy)'",
              "e.g., 0.5 x 0.5 | 1 x 1 | 2.5 x 2.5 | 10 x 10 (automated mineralogy)")
EDS_DIM_B = ("Number of pixels in the EDS map in the X and Y directions. Based on the area of interest and selected "
             "pixel size.",
             "Number of pixels in the X-ray map (EDS or WDS), given as X × Y: %s. Based on the area of interest and "
             "selected pixel size." % PIX)


def sem_edits(area_f_old):
    return {
        "Beam Raster Dimensions": {B: ("prefix", RASTER_OLD, RASTER_NEW)},
        "Step Size / Pixel Size": {B: (SEM_STEP_OLD_B, SEM_STEP_NEW_B), E: ("Numeric (µm) / Text", PAIR_UM),
                                   F: SEM_STEP_F},
        "EDS Map Dimensions": {A: ("EDS Map Dimensions", "Map Dimensions"), B: EDS_DIM_B},
        "Map Area": {B: (AREA_OLD_B, AREA_NEW_B), E: ("Numeric + unit", PAIR_UM),
                     F: (area_f_old, "e.g., 500 x 400 | 1000 x 500 | 10500 x 4000")},
    }


EDITS = {
    "EPMA": {
        "Beam Raster Dimensions": {B: ("prefix", RASTER_OLD, RASTER_NEW)},
        "Step Size / Pixel Size": {
            B: ("Distance between adjacent measurement points in the X-ray map in micrometers, defining the spatial "
                "resolution. Report both X and Y step if they differ.",
                "Distance between adjacent measurement points in the X-ray map in micrometers, defining the spatial "
                "resolution, given as X × Y: %s. A square grid is recorded with both values equal (e.g., 2 x 2)."
                % STEP),
            E: ("Numeric (µm) / Text", PAIR_UM),
            F: ("e.g., 0.5 | 1 | 2 | 5 | 10; or '1 um (X) x 2 um (Y)'", "e.g., 0.5 x 0.5 | 1 x 1 | 2 x 2 | 1 x 2")},
        "Map Dimensions": {
            B: ("Number of pixels in the X-ray map in the X and Y directions. Based on the area of interest and "
                "selected step size.",
                "Number of pixels in the X-ray map, given as X × Y: %s. Based on the area of interest and selected "
                "step size." % PIX)},
        "Map Area": {B: (AREA_OLD_B, AREA_NEW_B), E: ("Numeric + unit", PAIR_UM),
                     F: ("e.g., '100 × 100 µm' | '500 × 300 µm' | '1000 × 500 µm' | '0.2 mm²'",
                         "e.g., 100 x 100 | 500 x 300 | 1000 x 500")}},
    "SEM": sem_edits("e.g., '500 × 400 µm' | '0.2 mm²'"),
    "SEM_Composition": sem_edits("e.g., '500 × 400 µm' | '0.2 mm²'"),
    "TEM": {
        "STEM Scan Dimensions": {
            B: ("Number of pixels in the STEM scan frame (X × Y pixels). Also governs STEM-EDS and STEM-EELS "
                "acquisition where those detectors are used.",
                "Number of pixels in the STEM scan frame, given as X × Y: %s. Also governs STEM-EDS and STEM-EELS "
                "acquisition where those detectors are used." % PIX)}},
}

# ---- #13: two new Lab-XCT rows. Literature cells keyed by the column's leading number.
GAIN = {
    "after": "Detector Pixel Size",
    "A": "Detector Gain",
    "B": ("Gain setting of the X-ray detector during acquisition, recorded with its unit as the acquisition "
          "software reports it. The unit depends on the detector: flat-panel and CCD detectors usually report a "
          "gain in dB or as a factor, integrating detectors a capacitance setting in pF, and some software only a "
          "named preset."),
    "C": "Advanced", "D": "Advanced", "E": "Numeric + unit / Text",
    "F": "e.g., 12.0 dB | 0.25 pF",
    "I": "(none)",
    "J": ("Raises the signal of each projection without lengthening the exposure, at the cost of amplified noise; "
          "with exposure time, it sets the grey-level range of the projections."),
    "K": "Adjustable",
    "lit": {14: "12.0 dB — scan record, 'Gain (dB): 12.0'"},
}
VOLUME = {
    "after": "Output Bit Depth",
    "A": "Reconstructed Volume Dimensions",
    "B": ("Size of the reconstructed volume in voxels, given as X × Y × number of slices, the slices running along "
          "the rotation axis. For a stitched multi-volume scan, the size of the stitched volume. Its physical "
          "extent is these dimensions times the Voxel Size."),
    "C": "N/A", "D": "Advanced", "E": "Text (free)",
    "F": "e.g., 2000 × 2000 × 2000 | 885 × 885 × 999 | 1024 × 1024 × 1450",
    "I": "(none)",
    "J": "With the voxel size, gives the physical extent of the volume and the number of slices a dataset holds.",
    "K": "Not carried over",
    "lit": {14: "N — slices only: 'Total slices: 928'; X × Y not stated",
            21: "2000 × 2000 × 2000 voxels — 'reconstructed into a 2000 × 2000 × 2000 voxel 3-D volume'",
            23: "885 × 885 × 999 voxels — 'elementary image volume'",
            24: "2000 × 2000 × 2000 voxels — stated once for the Strathclyde setup, both Sample B scans",
            25: "2000 × 2000 × 2000 voxels — stated once for the Strathclyde setup, both Sample B scans"},
}
LIT_EXPECT = {14: "Eckley", 21: "Glavin", 23: "Richard", 24: "Richard", 25: "Richard"}
COLS = dict(zip("ABCDEFGHIJK", range(11)))


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


def apply_edits(rows, stem, edits):
    n = 0
    by = {r[0]: r for r in rows[1:] if r and r[0]}
    assert set(edits) <= set(by), (stem, set(edits) - set(by))
    for field, cells in edits.items():
        r = by[field]
        for col, spec in cells.items():
            if spec[0] == "prefix":
                _, old, new = spec
                assert r[col].startswith(old), (stem, field, col, r[col][:120])
                r[col] = new + r[col][len(old):]
            else:
                old, new = spec
                assert r[col] == old, (stem, field, col, r[col])
                r[col] = new
            n += 1
        r[7] = DATE
    return n


def new_row(h, spec, sentinel):
    r = [""] * len(h)
    for k in "ABCDEFIJK":
        r[COLS[k]] = spec[k]
    r[7] = DATE
    for j in range(11, sentinel):
        r[j] = "Y"
    for j in range(sentinel + 1, len(h)):
        r[j] = spec["lit"].get(j, "N")
        if j in spec["lit"]:
            assert LIT_EXPECT[j] in h[j], (j, h[j][:40])
    return r


def insert_xct(rows):
    h = rows[0]
    s = h.index("Literature Assessment")
    assert h[11:s] == ["Single-volume", "Multi-volume stitching"] and len(h) - s - 1 == 14, h[11:s]
    names = [r[0] for r in rows]
    for spec in (GAIN, VOLUME):
        assert spec["A"] not in names, spec["A"]
        i = names.index(spec["after"])
        rows.insert(i + 1, new_row(h, spec, s))
        names = [r[0] for r in rows]
    return rows


def main(apply=False):
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    plan, cells = [], 0
    for e in reg["composed"]:
        rel = e["tapp"]
        stem = os.path.basename(rel).rsplit("_TAPP_v", 1)[0]
        if stem not in EDITS and stem != "Lab-XCT":
            continue
        rows = rows_of(os.path.join(ROOT, rel))
        if stem == "Lab-XCT":
            rows = insert_xct(rows)
            print("  %-16s +2 rows (Detector Gain, Reconstructed Volume Dimensions)" % stem)
        else:
            k = apply_edits(rows, stem, EDITS[stem])
            cells += k
            print("  %-16s %d cells in %d fields" % (stem, k, len(EDITS[stem])))
        s, v = rel[:-4].rsplit("_v", 1)
        plan.append((e, rel, "%s_v%d.csv" % (s, int(v) + 1), rows))
    assert len(plan) == 5 and cells == 27, (len(plan), cells)
    if not apply:
        for e, rel, new, _ in plan:
            print("  %-44s -> %s" % (os.path.basename(rel), os.path.basename(new)))
        print("dry run")
        return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new, rows in plan:
        np_ = os.path.join(ROOT, new)
        write(np_, rows)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-2000:], q.stderr[-800:]))
        if rows_of(np_) != rows:
            raise SystemExit("composition changed %s beyond the edit" % new)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        e["tapp"] = new
        print("  composed %s" % os.path.basename(new))

    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
