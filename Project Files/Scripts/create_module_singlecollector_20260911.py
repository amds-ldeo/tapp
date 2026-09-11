#!/usr/bin/env python3
"""Create Module_SingleCollector (v1); take Detector Configuration out of the two LA-MC TAPPs.

    python3 "Project Files/Scripts/create_module_singlecollector_20260911.py" [--apply]

WHY. amds-ldeo/tapp#6 group A counted `Detector Configuration` (8 copies) and `Pulse/Analog Detector
Nonlinearity Correction` (6) among the fields still duplicated rather than composed. Reading all 14
Solution MC papers on 2026-09-11 settled what the first one is:

  * In the multi-collector TAPPs it duplicates Module_MCICPMS's `Faraday Cup Array Configuration`.
    Every Solution MC paper that describes its detectors does so in that field's terms, and for
    Zhang 2022, the one assessed LA-MC procedure, the two cells held the same content. Its only
    multi-collector option, "Multi-collector array (Faraday cups, with or without ion counters)",
    says nothing the technique's name does not. So it is REMOVED from LA-MC and LA-MC U-Pb, and the
    option leaves its Column F.
  * In the six single-collector TAPPs (LA-Q, LA-Q U-Pb, LA-SF, LA-SF U-Pb, Solution Q, Solution SF)
    it sits beside `Pulse/Analog Detector Nonlinearity Correction`, which has exactly that footprint.

THE MODULE. Rule 6.10: six consumers; 2 fields x 6 = 12 placements (floor 10); a real component —
the detection system of a single-collector analyser, the counterpart of Module_MCICPMS's Faraday
array. Rule 6.15: the footprint is a subset of Module_ICPMS's, which nominates absorption, but the
subject test refuses it — Module_ICPMS is defined as what every ICP-MS shares "independent of … the
analyser", and these are the analyser's detector. Module_MCICPMS passed the same test on the same
ground. Recorded in the manifest as `sub_module_test`.

VALUES. `Pulse/Analog` already agreed in all six in A–E and I: a zero-content transfer.
`Detector Configuration` had three descriptions (LA, Solution Q, Solution SF), harmonised here to
one single-collector text that names the Group 5 field instead of pointing at "Group 5". Tiers,
data types and keys unchanged.

`Ion Counter Dead Time` is NOT included, although its six `(none)` copies are exactly this footprint:
its three MC copies are keyed `monitored property`, and no field in the library is yet defined by
two modules — the tooling has no check for that case. It stays TAPP-owned, as decided 2026-09-10.

SIDE EFFECTS OF COMPOSITION, all by design: Column G gains the module's source comment where empty;
the overlay DEFAULT in Column J fills the four LA TAPPs' empty Purpose cells on both fields and
changes no existing Purpose. Column F is consumer-owned, so the option removal is applied here
directly, identically in all six.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-11"
NAME    = "SingleCollector"
DET     = "Detector Configuration"
PA      = "Pulse/Analog Detector Nonlinearity Correction"
SINGLE  = ("LA-Q-ICP-MS_TAPP", "LA-Q-ICP-MS_UPb_TAPP", "LA-SF-ICP-MS_TAPP", "LA-SF-ICP-MS_UPb_TAPP",
           "Solution_Q-ICP-MS_TAPP", "Solution_SF-ICP-MS_TAPP")
MULTI   = ("LA-MC-ICPMS_TAPP", "LA-MC-ICPMS_UPb_TAPP")
MC_OPTION = "Multi-collector array (Faraday cups, with or without ion counters)"
DET_F   = ("Single SEM, pulse counting only | Single SEM, dual mode (pulse counting + analog) | "
           "Single SEM, triple mode (pulse counting + analog + Faraday) | N/A | None")

HEADER = ["Metadata Item", "Description", "Procedure-Level Tier", "Analysis-Level Tier", "Data Type",
          "Example / Allowed Content", "Comments", "Last Update", "Keyed By", "Purpose"]
MODULE_ROWS = [
    [DET,
     "Type(s) of detector(s) installed in the mass spectrometer and the detection mode(s) used: "
     "pulse counting, analog and, on some sector-field instruments, Faraday. The cross-calibration "
     "between detector modes is recorded in Pulse/Analog Detector Nonlinearity Correction (Group 5).",
     "Basic", "Read-Only", "Controlled list / Text", DET_F, "", DATE, "(none)",
     "Single-collector instruments use one detector, usually a secondary electron multiplier run in "
     "pulse-counting and analog modes; some sector-field instruments (e.g., Thermo Element XR) add a "
     "Faraday cup for the highest signals."],
    [PA, None, "Advanced", "Editable", "Controlled list / Text", "Applied | N/A | None", "", DATE,
     "acquisition pass",
     "Accurate cross-calibration is critical for target species spanning a wide concentration range "
     "in the same session."],
]

MANIFEST = {
    "module": NAME,
    "title": "Single-Collector ICP-MS Detector",
    "layer": 2,
    "version": "1",
    "source_of_truth": "modules/Module_%s.csv" % NAME,
    "owned_columns": ["A", "B", "C", "D", "E", "I"],
    "overlay_columns": ["F", "J"],
    "mode_flag_default": "Y",
    "source_comment": "Source: single-collector ICP-MS module",
    "conditional": False,
    "blocks": [
        {"name": "sc_hardware", "target_group": "3. Instrument & Software",
         "placement": "append_to_group", "fields": [DET]},
        {"name": "sc_reduction", "target_group": "5. Data Processing", "placement": "insert_before",
         "anchor_field": "Constants and Reference Values Used", "fields": [PA]},
    ],
    "consumed_by": ["LA-Q-ICP-MS", "LA-Q-ICP-MS U-Pb", "LA-SF-ICP-MS", "LA-SF-ICP-MS U-Pb",
                    "Solution Q-ICP-MS", "Solution SF-ICP-MS"],
    "notes": ("The detection system of a single-collector ICP-MS analyser (quadrupole or "
              "single-collector sector field): which detector and detection modes are installed, and "
              "the cross-calibration between those modes. The counterpart of Module_MCICPMS's Faraday "
              "array; the two footprints are disjoint and together make up Module_ICPMS's."),
    "extraction": ("Extracted 2026-09-11 under Rule 6.10 from the six single-collector ICP-MS TAPPs. "
                   "Six consumers; 2 fields x 6 = 12 placements (floor 10); coherent as the "
                   "single-collector analyser's detection system. Pulse/Analog Detector Nonlinearity "
                   "Correction already agreed in all six in A-E and I. Detector Configuration had three "
                   "descriptions (LA, Solution Q, Solution SF), harmonised to one single-collector text. "
                   "Raised by amds-ldeo/tapp#6, group A."),
    "sub_module_test": ("Run 2026-09-11 under Rule 6.15. Footprint: the 6 single-collector ICP-MS "
                        "TAPPs. ICPMS (9): proposed is a subset, so prong 1 nominates absorption; prong "
                        "2 refuses it - ICPMS is defined as what every ICP-MS shares 'independent of ... "
                        "the analyser', and these fields are the analyser's detector. MCICPMS (the 3 "
                        "multi-collector TAPPs): disjoint - the complement within ICPMS - and it passed "
                        "the same subject test on the same ground. CollisionCell (6: LA-Q, LA-Q U-Pb, "
                        "LA-MC, LA-MC U-Pb, Solution Q, Solution MC): overlapping, neither contained. "
                        "LaserAblation (6 LA) and SolutionIntroduction (3 Solution): overlapping, neither "
                        "contained, and a different subject (the front end, not the analyser). No "
                        "IDENTICAL footprint; proceed."),
    "decisions": [
        ("2026-09-11 v1. Created. Detector Configuration removed from LA-MC and LA-MC U-Pb in the same "
         "pass: there it duplicated Module_MCICPMS's Faraday Cup Array Configuration (for Zhang 2022, "
         "the one assessed procedure, both cells held the same content), and all 14 Solution MC papers "
         "describe their detectors in that field's terms. The 'Multi-collector array' option left "
         "Detector Configuration's Column F for the same reason. Ion Counter Dead Time deliberately "
         "NOT included although its six (none)-keyed copies are exactly this footprint: its three MC "
         "copies are keyed monitored property, and no field in the library is yet defined by two "
         "modules; the tooling has no check for that case. It stays TAPP-owned, as decided 2026-09-10 "
         "(c5632e0)."),
    ],
    "tier_provenance": ("Tier values (Columns C and D) in this module are the library's current best "
                        "answer and are PROVISIONAL: how hard a field should be pushed at procedure "
                        "registration and at analysis time is a governance question for community "
                        "review, not a technical one settled here. They are module-owned so that a "
                        "review decision lands in one place and reaches every consumer on "
                        "recomposition — not because the values are considered final."),
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


def bumped(rel):
    return re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan, pa_descs = [], set()
    for e in reg["composed"]:
        base = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        rows = rows_of(os.path.join(ROOT, e["tapp"]))
        have = {r[0].strip(): r for r in rows[1:] if r and r[0].strip() in (DET, PA)}
        role = "single" if base in SINGLE else "multi" if base in MULTI else None
        if role is None:
            if have:
                raise SystemExit("PREMISE: %s carries %s but is in neither set" % (base, sorted(have)))
            continue
        if role == "single" and sorted(have) != sorted([DET, PA]):
            raise SystemExit("PREMISE: %s lacks one of the two fields" % base)
        if role == "multi" and sorted(have) != [DET]:
            raise SystemExit("PREMISE: %s should carry Detector Configuration only" % base)
        if role == "single":
            for name, r in have.items():
                m = next(x for x in MODULE_ROWS if x[0] == name)
                for i in (2, 3, 4, 8):
                    if r[i] != m[i]:
                        raise SystemExit("PREMISE: %s %s col %d is %r, not %r" % (base, name, i, r[i], m[i]))
                if MC_OPTION not in r[5] and name == DET:
                    raise SystemExit("PREMISE: %s Detector Configuration F lacks the MC option" % base)
            pa_descs.add(have[PA][1])
        if role == "multi":
            far = next((r for r in rows[1:] if r and r[0].strip() == "Faraday Cup Array Configuration"), None)
            if far is None:
                raise SystemExit("PREMISE: %s has no Faraday Cup Array Configuration" % base)
        plan.append((e, role, base))
        print("  %-8s %-34s -> %s" % (role, os.path.basename(e["tapp"]), os.path.basename(bumped(e["tapp"]))))
    if len(pa_descs) != 1:
        raise SystemExit("PREMISE: Pulse/Analog descriptions differ across the six (%d variants)" % len(pa_descs))
    MODULE_ROWS[1][1] = pa_descs.pop()          # a zero-content transfer: take the agreed text
    if len(plan) != 8 or sum(1 for p in plan if p[1] == "single") != 6:
        raise SystemExit("PREMISE: expected 6 single-collector and 2 multi-collector TAPPs")
    if os.path.exists(os.path.join(MODULES, "Module_%s.json" % NAME)):
        raise SystemExit("PREMISE: Module_%s already exists" % NAME)
    print("\n  Module_%s v1: %d fields x 6 consumers = 12 placements" % (NAME, len(MODULE_ROWS)))
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- 1. the module -----------------------------------------------------------
    write(os.path.join(MODULES, "Module_%s.csv" % NAME), [HEADER] + MODULE_ROWS)
    with io.open(os.path.join(MODULES, "Module_%s.json" % NAME), "w", encoding="utf-8") as fh:
        json.dump(MANIFEST, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  Module_%s written" % NAME)

    # --- 2. the TAPPs --------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    news = {}
    for e, role, base in plan:
        rel, new = e["tapp"], bumped(e["tapp"])
        np_ = os.path.join(ROOT, new)
        if role == "single":
            mods = e["modules"] + [{"name": NAME, "version": "1"}]
            q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                               + flags(mods) + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
            if q.returncode != 0:
                raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
            rr = rows_of(np_); h = rr[0]; iF, iU = h.index("Example / Allowed Content"), h.index("Last Update")
            got = [r for r in rr[1:] if r and r[0].strip() in (DET, PA)]
            if sorted(r[0] for r in got) != sorted([DET, PA]):
                raise SystemExit("%s: expected one row of each field" % new)
            for r in got:
                r[iU] = DATE
                if r[0].strip() == DET:
                    r[iF] = DET_F                     # consumer-owned: the MC option leaves
            write(np_, rr)
        else:
            rr = rows_of(os.path.join(ROOT, rel))
            keep = [r for r in rr if not (r and r[0].strip() == DET)]
            if len(keep) != len(rr) - 1:
                raise SystemExit("%s: expected to remove exactly one row" % rel)
            write(np_, keep)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        news[base] = (new, role)
        print("  %-8s %s" % (role, os.path.basename(new)))

    # --- 3. the registry: re-read, because compose_tapp --out records compositions itself ----
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_v", 1)[0]
        if stem not in news:
            continue
        new, role = news[stem]
        e["tapp"] = new
        if role == "single":
            e["modules"] = [m for m in e["modules"] if m["name"] != NAME] + [{"name": NAME, "version": "1"}]
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
