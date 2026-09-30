#!/usr/bin/env python3
"""Retire `Sample Form / Analytical Substrate` from Module_LaserAblation (v11 -> v12) and the six LA TAPPs.

    python3 "Project Files/Scripts/retire_sample_form_20260930.py" [--apply]

WHY. The field duplicates Module_Core's `Sample Preparation Method` and fails Rule 6.1's specificity
test. Core asks for "the form in which the sample is presented to the instrument"; this field asked for
"the physical form of the material as it enters the ablation cell" — the same question, restated for
one technique. Rule 6.4 point 3 puts per-technique specificity in Column F, not in a second field.

How it happened. In LA-ICP-MS v13 the two were complementary: `Sample Form` was the controlled-list
FORM, and `Sample Preparation Method` was free-text STEPS at C=Advanced. On 2026-08-27 Core redefined
`Sample Preparation Method` as "the form ... and the preparation that brought it to that form", a
controlled list at C=Basic, which absorbed this field's job. The same day
`extend_laserablation_20260827.py` moved this field into the module as a zero-content transfer, and
the 6.1 test was never run against the redefined Core field.

EVIDENCE. 15 distinct literature columns (LA-Q 7, LA-SF 7, LA-MC 1; the U-Pb variants repeat their
parents' columns). In none does this field hold attested content that is absent from
`Sample Preparation Method` or from the field that owns it (`Ablation Cell Type`,
`Pre-Ablation Surface Treatment`, `Fusion Flux and Dilution Ratio`). 8 restate it, 2 lose content
(Zhang 2022 SF drops "and thin sections"; Navarro mapping drops the Nital etch), and 4 contradict it
(Liu 2016 x2 assert "polished" where the prep extraction reads "not described"; Navarro spot borrows
the mapping column's etch; Wu 2023 is N against a filled cell). It was also keyed `(none)`
against Core's `sample`, which flattened Zhang 2022's mixed-route procedure to one form. The
fusion-vs-in-situ distinction it could have been narrowed to is already carried twice: by
`Sample Preparation Method`'s values (Fused bead vs sections and mounts) and by
`Fusion Flux and Dilution Ratio` ('Not applicable (in situ)').

WHAT THIS DOES (user decision, 2026-09-30):
  1. Module_LaserAblation: the row leaves the CSV and the `la_sample` block; version 11 -> 12.
  2. Six LA TAPPs bumped. Composition does not delete a row the module stops defining (the blocks
     path, Rule 6.9), so the row is dropped here after composing.
  3. `Sample Preparation Method` Column F (consumer-owned) in the six LA TAPPs gains the two pellet
     values from the retired field's list. `Liquid` is dropped: never attested, and not a routine
     ablation substrate. `Li-borate fused glass disc` is already `Fused bead`.
  4. LA-Q v94, Wu+2023: `Sample Preparation Method` held the samples' provenance ("Megacrysts and
     single crystals; XN02 megacrysts from the Datas alluvial deposits"), not a preparation. The
     paper (JAAS 38, 1285) gives only the origin of each sample in §2.1 and credits sample
     preparation in the acknowledgements without describing it, so the cell is `N`.
No literature content is moved: every retired cell is either already in `Sample Preparation Method`
or in the neighbouring field that owns it, or it is an inference (Liu 2016).
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-30"
SFS     = "Sample Form / Analytical Substrate"
SPM     = "Sample Preparation Method"
LA      = ("LA-Q-ICP-MS_TAPP", "LA-Q-ICP-MS_UPb_TAPP", "LA-SF-ICP-MS_TAPP", "LA-SF-ICP-MS_UPb_TAPP",
           "LA-MC-ICPMS_TAPP", "LA-MC-ICPMS_UPb_TAPP")
OLD_F   = ("Polished thin section | Polished thick section | Polished block or epoxy mount | Grain mount | "
           "Fused bead | Experimental capsule section | Etched or chemically treated surface | N/A | None")
NEW_F   = ("Polished thin section | Polished thick section | Polished block or epoxy mount | Grain mount | "
           "Fused bead | Pressed powder pellet | Nano-particulate pressed pellet | Experimental capsule section | "
           "Etched or chemically treated surface | N/A | None")
WU_HEAD = "Wu+etal2023"
WU_OLD  = "Megacrysts and single crystals; XN02 megacrysts from the Datas alluvial deposits, SE Brazil"
WU_NEW  = ("N (not described; §2.1 gives only the origin of the megacrysts and single crystals, and the "
           "acknowledgements credit sample preparation without stating a method)")
DECISION = (
    "2026-09-30 v12. `Sample Form / Analytical Substrate` RETIRED (29 -> 28 fields). It duplicated "
    "Module_Core's `Sample Preparation Method` and failed Rule 6.1's specificity test: 'the form as it "
    "enters the ablation cell' is Core's 'the form in which the sample is presented to the instrument', "
    "restated for one technique. The two were complementary in LA-ICP-MS v13 (form vs free-text steps); "
    "Core's 2026-08-27 redefinition absorbed this field's job the same day this module took it over. In "
    "15 distinct literature columns it held no attested content absent from Sample Preparation Method "
    "or a neighbouring owner field; 4 cells contradicted it and 2 lost content. Its key, (none), also "
    "disagreed with Core's `sample`. Narrowing to fusion vs in situ was rejected: that distinction is "
    "carried by Sample Preparation Method's values and by Fusion Flux and Dilution Ratio. The two pellet "
    "values moved to Sample Preparation Method's Column F in the six LA TAPPs; 'Liquid' was dropped. See "
    "precedents.md, 2026-09-30.")


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


def bumped(rel):
    return re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)


def edit(rr, base):
    """Drop the retired row, extend SPM's Column F, fix the Wu cell. Returns (rows, report)."""
    h = rr[0]
    iF, iU = h.index("Example / Allowed Content"), h.index("Last Update")
    keep = [r for r in rr if not (r and r[0].strip() == SFS)]
    if len(keep) != len(rr) - 1:
        raise SystemExit("PREMISE: %s should carry exactly one %s row" % (base, SFS))
    spm = [r for r in keep if r and r[0].strip() == SPM]
    if len(spm) != 1 or spm[0][iF] != OLD_F:
        raise SystemExit("PREMISE: %s SPM Column F is not the expected LA list" % base)
    spm = spm[0]
    spm[iF] = NEW_F
    spm[iU] = DATE
    wu = [j for j, x in enumerate(h) if x.startswith(WU_HEAD)]
    report = "row dropped, SPM F extended"
    if base == "LA-Q-ICP-MS_TAPP":
        if len(wu) != 1 or spm[wu[0]] != WU_OLD:
            raise SystemExit("PREMISE: LA-Q Wu+2023 SPM cell is not the expected text")
        spm[wu[0]] = WU_NEW
        report += ", Wu+2023 cell -> N"
    elif wu:
        raise SystemExit("PREMISE: %s unexpectedly has a Wu+2023 column" % base)
    return keep, report


def main(apply=False):
    # --- premises: the module ------------------------------------------------------------
    mcsv = os.path.join(MODULES, "Module_LaserAblation.csv")
    mjs  = os.path.join(MODULES, "Module_LaserAblation.json")
    mrows = rows_of(mcsv)
    man = json.load(io.open(mjs, encoding="utf-8"))
    if man["version"] != "11":
        raise SystemExit("PREMISE: Module_LaserAblation is v%s, not v11" % man["version"])
    blk = next(b for b in man["blocks"] if b["name"] == "la_sample")
    if SFS not in blk["fields"] or sum(1 for r in mrows if r and r[0] == SFS) != 1:
        raise SystemExit("PREMISE: %s not defined once in Module_LaserAblation" % SFS)
    nfields = sum(len(b["fields"]) for b in man["blocks"])
    if nfields != 29:
        raise SystemExit("PREMISE: expected 29 module fields, found %d" % nfields)

    # --- premises: the TAPPs ---------------------------------------------------------------
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        base = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        has = any(r and r[0].strip() == SFS for r in rows_of(os.path.join(ROOT, e["tapp"])))
        if has != (base in LA):
            raise SystemExit("PREMISE: %s %s the field" % (base, "carries" if has else "lacks"))
        if base in LA:
            _, rep = edit(rows_of(os.path.join(ROOT, e["tapp"])), base)
            plan.append((e, base))
            print("  %-32s -> %-32s %s" % (os.path.basename(e["tapp"]), os.path.basename(bumped(e["tapp"])), rep))
    if len(plan) != 6:
        raise SystemExit("PREMISE: expected 6 LA TAPPs, found %d" % len(plan))
    print("\n  Module_LaserAblation v11 -> v12, 29 -> 28 fields")
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- 1. the module -------------------------------------------------------------------------
    write(mcsv, [r for r in mrows if not (r and r[0] == SFS)])
    blk["fields"] = [f for f in blk["fields"] if f != SFS]
    man["version"] = "12"
    man["decisions"].append(DECISION)
    with io.open(mjs, "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  Module_LaserAblation v12 written")

    # --- 2. the TAPPs --------------------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    news = {}
    for e, base in plan:
        rel, new = e["tapp"], bumped(e["tapp"])
        np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr, _ = edit(rows_of(np_), base)
        write(np_, rr)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        news[base] = new
        print("  %s" % os.path.basename(new))

    # --- 3. the registry: re-read, because compose_tapp --out records compositions itself ----------
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem in news:
            e["tapp"] = news[stem]
            for m in e["modules"]:
                if m["name"] == "LaserAblation":
                    m["version"] = "12"
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
