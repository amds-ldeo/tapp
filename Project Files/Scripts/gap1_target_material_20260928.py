#!/usr/bin/env python3
"""Gap 1 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md, EPMA part.

    python3 "Project Files/Scripts/gap1_target_material_20260928.py" [--apply]

PROBLEM. EPMA's five beam fields were keyed `sample > sampling unit`, which projects (7.3.3) to one
value per procedure, while published procedures state beam conditions per phase. No procedure in the
15 EPMA literature columns states a beam condition per analysis point, so the per-point key was
finer than anything attested and the per-phase axis had no key.

AGREED DESIGN (2026-09-28), with the point/map split decided the same day:
  1. Module_Core v10: `Target Material` Keyed By `(none)` -> `defines: target material`, in all 16
     TAPPs. Exempt from 7.4c: the field states the procedure's scope for discovery in its own
     right, and only the electron-beam TAPPs key fields by it.
  2. EPMA point-analysis beam fields -> keyed `target material`, and flagged for point modes only
     (YNYN): Beam Mode, Beam Current, Beam Diameter, Beam Damage Minimization, plus Beam Raster
     Dimensions (already YNYN).
  3. EPMA mapping twins, mapping modes only (NYNY), keyed per map (`sample > sampling unit`):
     Mapping Beam Mode, Mapping Beam Current, Mapping Beam Diameter. A map scans every material
     at one set of conditions. Liu+2016 attests the need: olivine at 20 nA for points and 200 nA
     for the olivine megacryst maps, which one per-material value cannot hold. This follows the
     Peak Counting Time / Dwell Time per Pixel pattern; a `mode` key is forbidden (7.2).
  4. EPMA new session field `Target Material of Sampling Unit` (point modes), keyed
     `sample > sampling unit`, C=N/A, D=Basic: which Target Material entry each analysis point
     belongs to. It links a point to its conditions.
  5. Literature cells: the map conditions in the four columns that report maps (Liu+2016_UT,
     Frank+2023, Broussard+2026, Neuman+2025) move to the mapping twins. The point fields become
     N/A in the Neuman+2025 column, a mapping-only procedure; its 2 nA BSE mosaic is already recorded
     under Pre-Analysis Imaging and Screening. Other columns get N/A in the mapping twins, because
     those are point-analysis procedures. The new link field is left blank: it has not been assessed.

SEM and SEM_Composition carry the same beam fields and keep `sample > sampling unit` until their
literature columns are checked. The divergence is registered in KEYED_BY_TECHNIQUE_DEPENDENT.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-28"
TM      = "Target Material"
POINT   = ["Beam Mode", "Beam Current", "Beam Diameter", "Beam Raster Dimensions", "Beam Damage Minimization"]

DECISION = (
    "2026-09-28 v10. `Target Material` Keyed By `(none)` -> `defines: target material` (gap 1 of "
    "analysis/Pending_Gaps_2026-09-24_Reference_Example.md). EPMA keys its point-analysis beam conditions "
    "per target material: the literature states them per phase, never per analysis point. Exempt from "
    "7.4c in TAPPs with no consumer: the field states the procedure's scope for discovery in its own right. "
    "Data type unchanged (Controlled list / Text, open), so a procedure may name a finer entry where its "
    "conditions need one (Pang+2016 treats plagioclase apart from olivine and pyroxene).")

# New EPMA rows: name -> (description, C, D, data type, example, key, modes, purpose)
LINK = "Target Material of Sampling Unit"
NEW_LINK = (LINK,
    "The entry in Target Material that the sampling unit belongs to, which links the unit to the "
    "point-analysis conditions registered for that material.",
    "N/A", "Basic", "Text (free)",
    "e.g., 'Silicate mineral' for points P1-01–P1-12; 'Phosphate' for points P3-01–P3-06",
    "sample > sampling unit", "YNYN",
    "Without it a consumer cannot tell which of the conditions registered per target material a given "
    "analysis point was acquired under.")
MAP_ROWS = [
    ("Mapping Beam Mode",
     "Whether the electron beam was focused or defocused to a stated diameter during X-ray mapping. How "
     "the beam or stage moves across the mapped area is recorded by Stage Scan vs. Beam Scan and Step "
     "Size / Pixel Size.",
     "Basic", "Read-Only", "Controlled list / Text", "Focused | Defocused | N/A | None",
     "sample > sampling unit", "NYNY", ""),
    ("Mapping Beam Current",
     "Probe current in nanoamperes (nA) used during X-ray mapping.",
     "Basic", "Editable", "Numeric (nA)", "e.g., 50 | 100 | 200",
     "sample > sampling unit", "NYNY", ""),
    ("Mapping Beam Diameter",
     "Diameter of the electron beam in micrometres during X-ray mapping. 0 indicates a fully focused beam.",
     "Basic", "Editable", "Numeric (µm) / Text", "e.g., 0 (focused) | 1 | 10",
     "sample > sampling unit", "NYNY", ""),
]

# Literature refiling, by column-label prefix. field -> {column prefix: new value}
POINT_EDITS = {
    "Beam Mode":     {"Frank+2023": "Focused (point analysis)",
                      "Neuman+2025": "N/A — mapping-only procedure; map conditions under Mapping Beam Mode"},
    "Beam Current":  {"Liu+2016_UT": "20 nA (olivine, pyroxene, Fe-Ti-Cr oxides); 10 nA (maskelynite, phosphate, sulfide, glass)",
                      "Neuman+2025": "N/A — mapping-only procedure; map current under Mapping Beam Current; the 2 nA BSE mosaic is recorded under Pre-Analysis Imaging and Screening"},
    "Beam Diameter": {"Neuman+2025": "N/A — mapping-only procedure; map beam under Mapping Beam Diameter"},
    "Beam Damage Minimization": {"Neuman+2025": "N/A"},
}
MAP_CELLS = {
    "Mapping Beam Mode":     {"Liu+2016_UT": "N", "Frank+2023": "N", "Broussard+2026": "N",
                              "Neuman+2025": "Fixed 10 µm beam (stated 'a fixed 10 um electron beam')"},
    "Mapping Beam Current":  {"Liu+2016_UT": "200 nA (olivine megacryst Kα maps)", "Frank+2023": "N",
                              "Broussard+2026": "N", "Neuman+2025": "100 nA probe current (stage maps)"},
    "Mapping Beam Diameter": {"Liu+2016_UT": "N", "Frank+2023": "N", "Broussard+2026": "N",
                              "Neuman+2025": "10 µm (fixed)"},
}
POINT_OLD = {  # premise: the cells being rewritten still hold what was read on 2026-09-28
    ("Beam Current", "Liu+2016_UT"): "200 nA (olivine megacryst Ka maps)",
    ("Beam Current", "Neuman+2025"): "100 nA probe current (stage maps)",
    ("Beam Mode", "Neuman+2025"): "Fixed 10 um beam",
    ("Beam Mode", "Frank+2023"): "mapping beam mode N",
    ("Beam Diameter", "Neuman+2025"): "10 um (fixed)",
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


def epma_edit(rr):
    """Apply the EPMA-only changes to a composed EPMA table in place."""
    h = rr[0]
    iI, iU, iP = h.index("Keyed By"), h.index("Last Update"), h.index("Purpose")
    iS = h.index("Literature Assessment")
    modes = list(range(iP + 1, iS))
    assert [h[i] for i in modes] == ["EDS Point Analysis", "EDS Mapping", "WDS Point Analysis", "WDS Mapping"], h[iP+1:iS]
    lit = {i: h[i].replace("\n", " ").split("|")[0].strip() for i in range(iS + 1, len(h)) if h[i].strip()}

    def col(prefix):
        m = [i for i, lab in lit.items() if lab == prefix]
        assert len(m) == 1, (prefix, m)
        return m[0]

    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for (f, c), frag in POINT_OLD.items():
        assert frag in by[f][col(c)], "PREMISE: %s / %s no longer holds %r" % (f, c, frag)
    for f in POINT:
        r = by[f]
        r[iI] = "target material"
        for k, i in enumerate(modes):
            r[i] = "YNYN"[k]
        r[iU] = DATE
        for c, v in POINT_EDITS.get(f, {}).items():
            r[col(c)] = v

    def make(spec, cells):
        name, desc, c, d, dt, ex, key, mflags, purpose = spec
        r = [""] * len(h)
        r[0], r[1], r[2], r[3], r[4], r[5] = name, desc, c, d, dt, ex
        r[6] = ""; r[iU] = DATE; r[iI] = key; r[iP] = purpose
        for k, i in enumerate(modes):
            r[i] = mflags[k]
        for i, lab in lit.items():
            r[i] = cells.get(lab, "N/A") if cells is not None else ""
        return r

    out = []
    for r in rr:
        out.append(r)
        n = r[0].strip() if r else ""
        if n == "Sampling Unit Name":
            out.append(make(NEW_LINK, None))            # not yet assessed: blank
        if n == "Beam Damage Minimization":
            for spec in MAP_ROWS:
                out.append(make(spec, MAP_CELLS[spec[0]]))
    return out


def main(apply=False):
    mcsv = os.path.join(MODULES, "Module_Core.csv")
    mrows = rows_of(mcsv)
    hdr = mrows[0]; iI = hdr.index("Keyed By"); iU = hdr.index("Last Update"); iE = hdr.index("Data Type")
    tm = next(r for r in mrows if r and r[0] == TM)
    if tm[iI] != "(none)":
        raise SystemExit("PREMISE: Module_Core %s keyed %r" % (TM, tm[iI]))
    if tm[iE].startswith(("Integer", "Numeric")):
        raise SystemExit("PREMISE: a definer must be text-typed (7.4a); %s is %s" % (TM, tm[iE]))

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        rel = e["tapp"]
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), rel)
        plan.append((e, rel, new))
        print("  %-40s -> %-30s%s" % (os.path.basename(rel), os.path.basename(new),
                                       "  + beam re-key, 4 new fields, lit refiling" if "EPMA_TAPP" in rel else ""))
    mj = os.path.join(MODULES, "Module_Core.json")
    d = json.load(io.open(mj, encoding="utf-8"))
    newver = str(int(d["version"]) + 1)
    print("\n  Module_Core v%s -> v%s: %s -> defines: target material; %d consumers"
          % (d["version"], newver, TM, len(plan)))
    epma = next(rel for _, rel, _ in plan if "EPMA_TAPP" in rel)
    test = epma_edit(rows_of(os.path.join(ROOT, epma)))
    print("  EPMA dry edit: %d -> %d rows" % (len(rows_of(os.path.join(ROOT, epma))), len(test)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    tm[iI] = "defines: target material"; tm[iU] = DATE
    write(mcsv, mrows)
    d["version"] = newver; d["decisions"].append(DECISION)
    with io.open(mj, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h = rr[0]; jU = h.index("Last Update"); jI = h.index("Keyed By")
        for r in rr[1:]:
            if r and r[0].strip() == TM:
                if r[jI] != "defines: target material":
                    raise SystemExit("%s: composition did not carry the new key" % new)
                r[jU] = DATE
        if "EPMA_TAPP" in rel:
            rr = epma_edit(rr)
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f):
                dst = os.path.join(sup, os.path.basename(f))
                if os.path.exists(dst):
                    raise SystemExit("PREMISE: %s already parked" % dst)
                shutil.move(f, dst)
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  composed %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "Core":
                    m["version"] = newver
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)          # skips: the folder README exists (gaps 5/6) and is extended by hand
    return 0


sys.exit(main("--apply" in sys.argv))
