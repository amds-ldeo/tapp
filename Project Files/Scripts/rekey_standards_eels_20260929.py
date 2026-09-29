#!/usr/bin/env python3
"""Primary calibration standards keyed per target material; EELS detection limit per reported property (2026-09-29).

    python3 "Project Files/Scripts/rekey_standards_eels_20260929.py" [--apply]

1. `Primary Calibration Standard Name`: `target species` -> `target material x target species`, in
   Module_CompositionQC (v5 -> v6), so in all 12 consumers. The EPMA keyed-notation pilot found
   McCoy+2025_UA stating standards per phase AND element: for Mg, Fo92 olivine and rhodonite for the
   Mg,Na phosphate, dolomite for the carbonates. A target-species key cannot hold that. The module
   owns Column I (Rule 6.5), so the key cannot change in EPMA/SEM/SEM_Composition alone. The user
   chose the module-wide re-key, on the module's own 2026-08-27 reasoning under 7.3.2: declare the
   finest attested key unconditionally; a procedure with one standard set writes `all [ ... ]`.
   No ICP-MS literature cell states per-material standards today.

2. `EELS Detection Limit` (TEM, TAPP-owned): `monitored property` -> `reported property`. A detection
   limit is a value of the measured quantity (VIM), stated in concentration units; the library's
   only literature value is "~10 ppm for transition metals and lanthanides" (Xing+2023). This matches
   `EDS Detection Limit` and `Detection Limit`. The description said "for target edges"; it now says
   what the key says.

3. EPMA literature cells (the only TAPP in the keyed-notation enforced set): each stated standards
   cell becomes two-level. Where the paper does not vary standards by phase: `all [ ... ]`, with the
   entries unchanged. McCoy+2025_UA gets its per-phase statement, transcribed as printed ("rhodonite
   (Mg)" included).
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import keyed_cells as K

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-29"
PCS, NEWKEY = "Primary Calibration Standard Name", "target material x target species"
EELS = "EELS Detection Limit"
EELS_DESC = ("Estimated detection limit or minimum detectable concentration, under this procedure, of each "
             "quantity determined by EELS. Record 'N/A' where EELS is not listed in Spectroscopic Detector(s).")
MCCOY_UA = ("\"Mg,Na phosphate\" [F, P, Ca: fluorapatite; Si: Fo92 olivine; Mg: Fo92 olivine, rhodonite; "
            "Fe: fayalite; Al: anorthite; S: baryte; K: potassium feldspar; Cl: scapolite]; carbonate [Na: albite; "
            "Si: Fo92 olivine; Mg: dolomite; Ca: calcite; Mn: Mn carbonate; P: apatite; S: baryte; Fe: fayalite]"
            " — 'The standards used for Mg,Na phosphate were fluorapatite (F, P, Ca), Fo92 olivine (Si, Mg), "
            "rhodonite (Mg), fayalite (Fe), anorthite (Al), baryte (S), potassium feldspar (K) and scapolite (Cl). "
            "For carbonates, the standards used were albite (Na), Fo92 olivine (Si), dolomite (Mg), calcite (Ca), "
            "Mn carbonate (Mn), apatite (P), baryte (S) and fayalite (Fe)' (p.7); rhodonite is printed against Mg")
DECISION = ("2026-09-29 v6. `Primary Calibration Standard Name` Keyed By `target species` -> `target material x "
            "target species` in all 12 consumers. McCoy+2025_UA (EPMA) states standards per phase and element, "
            "which a target-species key cannot hold; the module owns Column I, so the re-key is module-wide, on "
            "the 2026-08-27 reasoning under 7.3.2. A procedure with one standard set writes `all [ ... ]` "
            "(conventions 7.3.4).")


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


def epma_cells(rr, report):
    h = rr[0]; s = h.index("Literature Assessment")
    r = next(x for x in rr if x and x[0].strip() == PCS)
    for j in range(s + 1, len(h)):
        lab = h[j].replace("\n", " ").split("|")[0].strip()
        v = r[j]
        if lab == "McCoy+2025_UA":
            new = MCCOY_UA
        elif K.is_marker(v) or v.lstrip().startswith("all ["):
            continue
        else:
            struct, comment = K.split_commentary(v)
            new = "all [%s]" % struct + (" — " + comment if comment else "")
        if new != v:
            report.append((lab, v, new)); r[j] = new
    return rr


def main(apply=False):
    mcsv = os.path.join(MODULES, "Module_CompositionQC.csv")
    mrows = rows_of(mcsv); mh = mrows[0]; iI, iU = mh.index("Keyed By"), mh.index("Last Update")
    mr = next(r for r in mrows if r and r[0] == PCS)
    if mr[iI] != "target species":
        raise SystemExit("PREMISE: Module_CompositionQC %s keyed %r" % (PCS, mr[iI]))
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        mods = {m["name"] for m in e["modules"]}
        stem = os.path.basename(e["tapp"]).rsplit("_TAPP_v", 1)[0]
        if "CompositionQC" in mods or stem == "TEM":
            new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
            plan.append((e, stem, new))
    if len(plan) != 13:
        raise SystemExit("PREMISE: expected 12 CompositionQC consumers + TEM, found %d" % len(plan))
    tem = rows_of(os.path.join(ROOT, next(e["tapp"] for e, s, _ in plan if s == "TEM")))
    er = next(r for r in tem if r and r[0] == EELS)
    if er[tem[0].index("Keyed By")] != "monitored property":
        raise SystemExit("PREMISE: TEM %s keyed %r" % (EELS, er[tem[0].index("Keyed By")]))
    report = []
    epma_cells(rows_of(os.path.join(ROOT, next(e["tapp"] for e, s, _ in plan if s == "EPMA"))), report)
    print("  Module_CompositionQC: %s -> %s; %d TAPPs to bump" % ("target species", NEWKEY, len(plan)))
    print("  TEM: %s -> reported property" % EELS)
    for lab, old, new in report:
        print("  EPMA [%s]\n      was: %s\n      now: %s" % (lab, old[:110], new[:110]))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    mr[iI] = NEWKEY; mr[iU] = DATE; write(mcsv, mrows)
    jp = os.path.join(MODULES, "Module_CompositionQC.json")
    d = json.load(io.open(jp, encoding="utf-8")); d["version"] = newver = str(int(d["version"]) + 1)
    d.setdefault("decisions", []).append(DECISION)
    with io.open(jp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, stem, new in plan:
        rel = e["tapp"]; np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_); h = rr[0]; jI, jU = h.index("Keyed By"), h.index("Last Update")
        for r in rr[1:]:
            if r and r[0].strip() == PCS:
                if r[jI] != NEWKEY:
                    raise SystemExit("%s: composition did not carry the new key" % new)
                r[jU] = DATE
            if stem == "TEM" and r and r[0].strip() == EELS:
                r[jI], r[1], r[jU] = "reported property", EELS_DESC, DATE
        if stem == "EPMA":
            rr = epma_cells(rr, [])
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            dst = os.path.join(sup, os.path.basename(f))
            if os.path.exists(dst):
                raise SystemExit("PREMISE: %s already parked" % dst)
            shutil.move(f, dst)
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
        for m in e["modules"]:
            if m["name"] == "CompositionQC":
                m["version"] = newver
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
