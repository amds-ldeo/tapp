#!/usr/bin/env python3
"""Gap 1 of analysis/Pending_Gaps_2026-09-24_Reference_Example.md, SEM part.

    python3 "Project Files/Scripts/gap1_sem_target_material_20260928.py" [--apply]

EPMA was done earlier the same day (gap1_target_material_20260928.py): point-analysis beam fields
keyed `target material`, mapping twins keyed per map, and a link field. This script brings the four
SEM TAPPs into line. All fields touched are TAPP-owned (check_field_ownership.py, 15 modules).

EVIDENCE (read 2026-09-28; the SEM literature cells alone could not decide it). Beam Mode, Beam
Diameter, Beam Raster Dimensions and Beam Damage Minimization were added after the SEM v1 literature
pass and are blank in all 35 SEM and 9 SEM_Composition columns. Beam Current holds one value per
column everywhere. The SEM key `sample > sampling unit` had been justified on 2026-08-11 by Liu+2016,
an EPMA paper. Reading the SEM sections of the source papers:
  * per analysis point: no procedure;
  * per material: Ferus+2020 (TESCAN SEM with EDS+WDS, a seed paper): 0.090 um beam, "for glass
    and feldspar, the beam diameter was increased to 5 um";
  * points vs maps: Barnes+2025 Hokkaido JSM-7000F EDS ("~2 nA and ~1 nA ... for the X-ray mapping
    and quantitative analysis, respectively"), Ferus+2020 (20 nA points, 2-10 nA maps),
    Pascucci+2026 (30 um aperture spots, 60 um aperture maps);
  * imaging current varies per image, not per material: Garvie+2008 (70 fA at 500 V, 1.4 pA at
    1 kV, 98 pA at 5 kV).

CHANGE (decided 2026-09-28: SEM_Composition follows EPMA; option (a) for SEM Beam Current;
propagate fully to SEM_Imaging and SEM_FIBSEM under Rule 4):
  * Beam Mode, Beam Current, Beam Diameter, Beam Raster Dimensions, Beam Damage Minimization ->
    keyed `target material`, flagged for point modes only (EDS/WDS Point; CL Point too for Beam
    Current, which is the only one of the five that CL carries).
  * Mapping Beam Mode and Mapping Beam Diameter (new, EDS/WDS Mapping) and Mapping Beam Current
    (new; every mode that scans an area: X-ray and CL maps, EBSD, SE/BSE images, FIB-SEM work),
    keyed per map or image (`sample > sampling unit`).
  * Target Material of Sampling Unit (new, point modes), C=N/A D=Basic, keyed `sample > sampling unit`.
  * SEM_Imaging: Beam Current keeps CL Point only; its other modes move to Mapping Beam Current.
  * SEM_FIBSEM: Beam Current (both modes scan) is renamed Mapping Beam Current.
  * Literature: assessed Beam Current values in scanning-mode columns move to Mapping Beam Current,
    and Beam Current becomes N/A there; point columns get N/A in Mapping Beam Current. Zega+2025's
    Helios G3 value "0.8 to 2.5 nA (thinning)" is a Ga+ ion current, already under Coarse Milling
    Conditions, so the electron-beam cell becomes N. Fields never assessed stay blank for the
    literature pass that follows.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-28"
TM_KEY  = "target material"
UNIT    = "sample > sampling unit"

POINT_X = {"EDS Point Analysis", "WDS Point Analysis"}
POINT_ALL = POINT_X | {"CL Point Analysis"}
MAP_X = {"EDS Mapping", "WDS Mapping"}
SCAN = {"SE Imaging", "BSE Imaging", "EDS Mapping", "WDS Mapping", "CL Mapping", "EBSD",
        "TEM Sample Preparation", "3D Tomography"}

# field -> set of modes flagged Y after the change (modes absent from a TAPP are ignored)
POINT_FLAGS = {"Beam Mode": POINT_X, "Beam Diameter": POINT_X, "Beam Raster Dimensions": POINT_X,
               "Beam Damage Minimization": POINT_X, "Beam Current": POINT_ALL}

BC_DESC = ("Electron beam probe current for point analysis. For sub-nA values use decimal notation "
           "(e.g., 0.4 nA). The current used while the beam scans an area, for a map or an image, is "
           "recorded under Mapping Beam Current.")
BC_PURPOSE = ("Higher current improves signal-to-noise in point analysis but may increase beam damage "
              "and reduce spatial resolution.")
BD_DESC = ("Nominal electron beam diameter (spot size) at the sample surface for point analysis, in "
           "nanometres or micrometres, as set by the condenser aperture and working distance. The beam "
           "used for mapping is recorded under Mapping Beam Diameter.")

LINK = ("Target Material of Sampling Unit",
        "The entry in Target Material that the sampling unit belongs to, which links the unit to the "
        "point-analysis conditions registered for that material.",
        "N/A", "Basic", "Text (free)",
        "e.g., 'Silicate mineral' for points P1-01–P1-12; 'Phosphate' for points P3-01–P3-06",
        UNIT, POINT_ALL,
        "Without it a consumer cannot tell which of the conditions registered per target material a given "
        "analysis point was acquired under.")
MBM = ("Mapping Beam Mode",
       "Whether the electron beam was focused or defocused to a stated diameter during X-ray mapping. How "
       "the beam or stage moves across the mapped area is recorded by Stage Scan vs. Beam Scan and Step "
       "Size / Pixel Size.",
       "Basic", "Read-Only", "Controlled list / Text", "Focused | Defocused | N/A | None",
       UNIT, MAP_X, "")
MBD = ("Mapping Beam Diameter",
       "Diameter of the electron beam in micrometres during X-ray mapping. 0 indicates a fully focused beam.",
       "Basic", "Editable", "Numeric (µm) / Text", "e.g., 0 (focused) | 1 | 10",
       UNIT, MAP_X, "")
MBC_X = ("Mapping Beam Current",                      # SEM_Composition: EPMA's wording (Rule 2)
         "Probe current in nanoamperes (nA) used during X-ray mapping.",
         "Basic", "Editable", "Numeric (nA)", "e.g., 50 | 100 | 200",
         UNIT, MAP_X, "")
MBC_SCAN = ("Mapping Beam Current",                   # SEM, SEM_Imaging, SEM_FIBSEM
            "Electron beam probe current used while the beam scans an area: an X-ray or CL map, an EBSD "
            "map, or an SE or BSE image, including images taken during FIB-SEM work. For sub-nA values use "
            "decimal notation (e.g., 0.4 nA). Ion-beam currents used for milling belong in the milling "
            "condition fields.",
            "Basic", "Editable", "Numeric (nA)", "e.g., 0.07 | 0.4 | 2 | 6",
            UNIT, SCAN,
            "Sets the signal-to-noise and the electron dose delivered to every pixel of a map or image.")

ION_FIX = {"0.8 to 2.5 nA (thinning)":
           "N (the 2.5 to 0.8 nA stated for thinning are Ga+ ion currents, recorded under Coarse Milling "
           "Conditions)"}

# stem -> what the TAPP gets
PLAN = {
    "SEM":             {"point": True,  "twins": [MBM, MBC_SCAN, MBD], "link": True},
    "SEM_Composition": {"point": True,  "twins": [MBM, MBC_X, MBD],    "link": True},
    "SEM_Imaging":     {"point": False, "twins": [MBC_SCAN],           "link": True},
    "SEM_FIBSEM":      {"point": False, "twins": [],                   "link": False, "rename": True},
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


def col_mode(label):
    """Mode named in a literature-column label: its last '|' segment, before the instrument '('."""
    return label.replace("\n", " ").split("|")[-1].split("(")[0].strip()


def edit(stem, rr, report):
    spec = PLAN[stem]
    h = rr[0]
    iI, iU, iP, iS = h.index("Keyed By"), h.index("Last Update"), h.index("Purpose"), h.index("Literature Assessment")
    modes = {h[i]: i for i in range(iP + 1, iS)}
    lit = {i: h[i] for i in range(iS + 1, len(h)) if h[i].strip()}
    lmode = {i: col_mode(lab) for i, lab in lit.items()}
    for i, m in lmode.items():
        assert m in modes, "PREMISE: %s column %d names mode %r, not a mode column" % (stem, i, m)
    by = {r[0].strip(): r for r in rr[1:] if r and r[0].strip()}
    for new in ("Mapping Beam Mode", "Mapping Beam Current", "Mapping Beam Diameter", LINK[0]):
        assert new not in by, "PREMISE: %s already has %s" % (stem, new)
    bc = by["Beam Current"]
    assert bc[iI] in (UNIT, "(none)"), "PREMISE: %s Beam Current keyed %r" % (stem, bc[iI])

    def setflags(r, on):
        for m, i in modes.items():
            r[i] = "Y" if m in on else "N"

    # literature values of Beam Current, taken before anything is rewritten
    moved = {}
    for i in lit:
        v = bc[i]
        moved[i] = ION_FIX.get(v, v)

    if spec.get("rename"):                              # SEM_FIBSEM: every mode scans
        assert all(m in SCAN for m in modes), modes
        bc[0], bc[1], bc[iI], bc[iU], bc[iP] = MBC_SCAN[0], MBC_SCAN[1], UNIT, DATE, MBC_SCAN[8]
        bc[5] = MBC_SCAN[5]
        for i in lit:
            if moved[i] != bc[i]:
                report.append("%s col %d: %r -> %r" % (stem, i - iS, bc[i], moved[i]))
            bc[i] = moved[i]
        return rr

    for f, on in POINT_FLAGS.items():
        r = by.get(f)
        if r is None:
            continue
        if f != "Beam Current":
            assert spec["point"], (stem, f)
            assert r[iI] == UNIT, "PREMISE: %s %s keyed %r" % (stem, f, r[iI])
        r[iI] = TM_KEY; r[iU] = DATE
        setflags(r, on)
    bc[1], bc[iP] = BC_DESC, BC_PURPOSE
    if "Beam Diameter" in by:
        by["Beam Diameter"][1] = BD_DESC
    # Beam Current literature: point columns keep theirs; scanning columns go N/A (value moves)
    for i in lit:
        if lmode[i] not in POINT_ALL:
            bc[i] = "N/A"

    def make(t, cells):
        name, desc, c, d, dt, ex, key, on, purpose = t
        r = [""] * len(h)
        r[0], r[1], r[2], r[3], r[4], r[5] = name, desc, c, d, dt, ex
        r[iU] = DATE; r[iI] = key; r[iP] = purpose
        setflags(r, on)
        for i in lit:
            r[i] = cells(i)
        return r

    def mbc_cell(i):
        return moved[i] if lmode[i] in SCAN else "N/A"

    out = []
    anchor = "Beam Damage Minimization" if spec["point"] else "Beam Current"
    for r in rr:
        out.append(r)
        n = r[0].strip() if r else ""
        if n == "Sampling Unit Name" and spec["link"]:
            out.append(make(LINK, lambda i: ""))          # not yet assessed
        if n == anchor:
            for t in spec["twins"]:
                if t[0] == "Mapping Beam Current":
                    out.append(make(t, mbc_cell))
                else:
                    out.append(make(t, lambda i: ""))     # not yet assessed
    for i in lit:
        if lmode[i] in SCAN and moved[i] not in ("", "N", "N/A"):
            report.append("%s col %d [%s]: Beam Current -> Mapping Beam Current: %r"
                          % (stem, i - iS, lmode[i], moved[i]))
    return out


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_TAPP_v", 1)[0]
        if stem not in PLAN:
            continue
        new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
        plan.append((e, stem, new))
    if len(plan) != 4:
        raise SystemExit("PREMISE: expected 4 SEM TAPPs, found %d" % len(plan))
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    for e, stem, new in plan:
        rel = e["tapp"]
        for f in (rel, rel[:-4] + ".xlsx"):
            if os.path.exists(os.path.join(sup, os.path.basename(f))):
                raise SystemExit("PREMISE: %s already parked" % f)
        report = []
        before = rows_of(os.path.join(ROOT, rel))
        after = edit(stem, [list(r) for r in before], report)
        print("  %-32s -> %-28s %d -> %d rows" % (os.path.basename(rel), os.path.basename(new), len(before), len(after)))
        for line in report:
            print("      " + line)
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    os.makedirs(sup, exist_ok=True)
    for e, stem, new in plan:
        rel = e["tapp"]; np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = edit(stem, rows_of(np_), [])
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        print("  wrote %s" % os.path.basename(new))

    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    news = {os.path.basename(n).rsplit("_v", 1)[0]: n for _, _, n in plan}
    for e in reg["composed"]:
        s = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if s in news:
            e["tapp"] = news[s]
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)          # skips: this date's README exists and is extended by hand
    return 0


sys.exit(main("--apply" in sys.argv))
