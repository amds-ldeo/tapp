#!/usr/bin/env python3
"""SEM TAPPs: assess the never-assessed literature fields (2026-09-29).

    python3 "Project Files/Scripts/sem_never_assessed_fields_20260929.py" [--apply] [--show]

Tasks 2 and 3 of the 2026-09-28 gaps plan, for the four SEM TAPPs (SEM, SEM_Composition, SEM_Imaging,
SEM_FIBSEM). Gap 1 left these fields blank in every SEM column: the link field, the four point beam
fields, the two mapping twins, the detection method per element, and the Aggregation fields. Five other
fields had never been assessed either (Drift Correction, Stage Scan vs. Beam Scan, Map Area, Calibration
Factor, Procedural Blank Level, Constants); they are assessed in the same pass, with the paper open.

The variant TAPPs' columns are the same procedures as SEM's, under the same labels, so each procedure is
read once and its cells are written to every TAPP that carries the field and the column. Only blank
cells are filled: a field flagged N for a column's mode becomes `N/A`, a stated value is transcribed in
the keyed-value notation (conventions 7.3.4), and anything else is `N`.

Read from the papers:
  * Gucsik+2013 is the only SEM point procedure that states a beam mode ("with a focused beam").
  * Pascucci+2026 states a 10.5 × 4.0 mm SEM-EDS map area, and apertures (30 and 60 µm) rather than beam
    diameters; running SEM-EDS after the SPIM measurements is its stated damage measure.
  * Zhou+2017 is the only SEM procedure with combined results: mean pore diameter and mean throat size
    per sample, and mean throat length per throat-size class (Table 5).
  * No SEM procedure states drift correction, stage or beam scanning, a calibration factor or a constant.
  * Every averaged composition in Izawa+2010, Ma+2017, Genge+2025 and Pascucci+2026 is from EPMA, not SEM.

Corrected on the way (Monitored Elements):
  * Pascucci+2026 EDS Mapping said no element set is given for the SEM-EDS work. The INCA maps are
    "a map on a pixel-by-pixel basis of the main elements (O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni)".
  * Barnes+2025 EDS Mapping quoted "multi-element EDS mapping (Mg, Si, Fe, Ni, S, Na, Ca and Al)". That
    sentence is CRPG's JEOL JSM-6510 work on other samples; the JSC SEM-EDS of the two presolar grains
    names no elements.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
D = " — "
TAPPS = ["SEM_TAPP_v", "SEM_Composition_TAPP_v", "SEM_Imaging_TAPP_v", "SEM_FIBSEM_TAPP_v"]
PREP = "N" + D + "a sample-preparation procedure produces sections, not results to combine"

# field -> {matcher: value}. Matchers, most specific first:
#   "Author|text"  every column whose label contains both;
#   "mode:<Mode>"  every column of that analytical mode;
#   "*"            every other column.
# Only blank cells are written, except the (field, matcher) pairs in OVERWRITE_OK.
EDITS = {
  "Target Material of Sampling Unit": {"*": "N"},
  "Beam Mode": {
    "Gucsik|EDS Point": "all: Focused" + D + "'The accelerating voltage was 15 kV and the beam current was 2.0 nA, with a focused beam' (p.2)",
    "*": "N"},
  "Beam Diameter": {
    "Genge|EDS Point": "N" + D + "the '0.1 μm beam diameter' (p.2) is the EPMA's, not the SEM's",
    "Pascucci|EDS Point": "N" + D + "a 30 μm aperture is stated (p.3), not a beam diameter",
    "*": "N"},
  "Beam Raster Dimensions": {"*": "N"},
  "Beam Damage Minimization": {
    "Genge|EDS Point": "N" + D + "10 kV was chosen 'to reduce the excitation volume and increase spatial resolution' (p.2), not to limit beam damage",
    "Pascucci|EDS Point": "all: SEM-EDS run only after the SPIM reflectance measurements" + D + "'This was done only after the SPIM reflectance acquisitions to try to avoid charging effects and by also reducing thermal damage' (p.3)",
    "*": "N"},
  "Mapping Beam Mode": {"*": "N"},
  "Mapping Beam Diameter": {
    "Pascucci|EDS Mapping": "N" + D + "a 60 μm aperture is stated (p.3), not a beam diameter",
    "*": "N"},
  "Drift Correction": {"*": "N"},
  "Stage Scan vs. Beam Scan": {"*": "N"},
  "X-ray Detection Method per Monitored Element": {"*": "all: EDS"},
  "Map Area": {
    "Pascucci|EDS Mapping": "10.5 × 4.0 mm" + D + "'The area acquired by the SEM-EDS instrument is 10.5 × 4.0 mm wide and it is composed of nine mosaicked images (magnification 138×)'",
    "*": "N"},
  "Calibration Factor and Determination Method": {
    "Genge|EDS Point": "N" + D + "quantified with 'an XPP correction procedure calibrated with Oxford factory internal standards' (p.2); no factor is stated",
    "Pascucci|EDS": "N" + D + "standardless: 'semi-quantitative analyses with virtual standards present within the INCA software' (p.3)",
    "*": "N"},
  "Procedural Blank Level": {"*": "N/A" + D + "no chemical separation, so there is no procedural blank"},
  "Combination Method": {
    "mode:TEM Sample Preparation": PREP,
    "Zhou|3D Tomography": ("pore diameter, throat size: average over the pores or throats of each sample; throat length: average per "
                           "throat-size class in each sample" + D + "'average diameters of 18.409 and 14.452 μm', 'average sizes of "
                           "74.36 and 67.64 nm' (Conclusions); Table 5 'Average length (μm)'"),
    "*": "N"},
  "Combined Results": {
    "mode:TEM Sample Preparation": PREP,
    "Zhou|3D Tomography": ("SC pore diameter; HBC pore diameter; SC throat size (516 throats); HBC throat size (715 throats); "
                           "SC throat length per size class; HBC throat length per size class" + D + "Conclusions and Table 5; "
                           "the number of pores averaged is not stated"),
    "*": "N"},
  "Goodness-of-Fit or Dispersion Statistic": {"mode:TEM Sample Preparation": PREP, "*": "N"},
  "Other Statistics": {"mode:TEM Sample Preparation": PREP, "*": "N"},
  "Constants and Reference Values Used": {"*": "N"},
  "Monitored Elements": {
    "Pascucci|EDS Mapping": ("O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni" + D + "the SEM-EDS maps give 'a map on a pixel-by-pixel basis "
                             "of the main elements (O, Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni)', and the Cameo+ energy threshold covers "
                             "'Si, Mg, Fe, Al, P, Cr, Ca, Na, S, Ni, Ti'. The 'Si, Fe, Ca, Al, and S' list belongs to the EMPA-WDS "
                             "mapping, a different procedure"),
    "Barnes|EDS Mapping": ("N" + D + "no element set is named for the JSC SEM-EDS of the two presolar grains (p.2, p.11, Extended Data "
                           "Fig. 8). The 'multi-element EDS mapping (Mg, Si, Fe, Ni, S, Na, Ca and Al) of the different grains' (p.11) "
                           "is the CRPG JEOL JSM-6510 work on other samples")},
}
OVERWRITE_OK = {("Monitored Elements", "Pascucci|EDS Mapping"), ("Monitored Elements", "Barnes|EDS Mapping")}


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


def mode_of(label):
    return label.split("|")[2].split("(")[0].strip()


def pick(spec, label):
    """(matcher, value) for a column, most specific matcher first."""
    for k, v in spec.items():
        if "|" in k and all(p in label for p in k.split("|")):
            return k, v
    for k, v in spec.items():
        if k.startswith("mode:") and mode_of(label) == k[5:]:
            return k, v
    return ("*", spec["*"]) if "*" in spec else (None, None)


def edit(rr, report):
    h = rr[0]; s = h.index("Literature Assessment")
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for f, spec in EDITS.items():
        if f not in by:
            continue
        r = by[f]
        for j in range(s + 1, len(h)):
            label = " ".join(h[j].split())
            if not label.strip():
                continue
            mode = mode_of(label)
            if mode not in h[:s]:
                raise SystemExit("PREMISE: mode %r of column %r is not a mode column" % (mode, label))
            k, v = pick(spec, label)
            if k is None:
                continue
            old = r[j]
            if r[h.index(mode)].strip() == "N" and (f, k) not in OVERWRITE_OK:
                v = "N/A"
            if old.strip():
                if (f, k) not in OVERWRITE_OK:
                    continue
            elif (f, k) in OVERWRITE_OK:
                raise SystemExit("PREMISE: [%s] %s was expected to hold the cell being corrected" % (label, f))
            if old != v:
                report.append((label, f, old, v)); r[j] = v
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for pre in TAPPS:
        e = next(x for x in reg["composed"] if os.path.basename(x["tapp"]).startswith(pre))
        rel = e["tapp"]; new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        report = []
        edit(rows_of(os.path.join(ROOT, rel)), report)
        print("  %s -> %s: %d cells" % (os.path.basename(rel), os.path.basename(new), len(report)))
        if "--show" in sys.argv:
            for c, f, old, v in report:
                if v != "N/A":
                    print("    [%s] %s\n        was: %s\n        now: %s" % (c[:70], f, old[:90], v[:160]))
        plan.append((e, rel, new))
    if not apply:
        print("\n(dry run — pass --apply to write; --show lists every change except N/A)"); return 0
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed\n%s\n%s" % (q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), []))
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
