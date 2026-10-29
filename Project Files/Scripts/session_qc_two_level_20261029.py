#!/usr/bin/env python3
"""Rule 14.1 amendment: session-level statistics hold the value achieved in the session record.

    python3 "Project Files/Scripts/session_qc_two_level_20261029.py" [--apply]

FINDINGS. analysis/Rule14_Amendment_Session_QC_2026-10-29.md (fourth draft; RD accepted all six
decisions 2026-10-29). The dataset records measurements. A statistic that describes a session as a
whole (precision and accuracy on reference materials, detection limits, blank levels, long-term
precision) is recorded twice in the TAPP: the procedure holds the method and the expected value,
the session record the value achieved. Per-measurement statistics stay dataset-only (the
2026-10-27 sweep stands). Where the dataset includes the reference-material analyses, they are the
primary record and the session value must agree with them (14.5). Each level is stated in Column B
under the fixed lead-ins `For the procedure:` / `For the session:` (14.6).

CHANGE. No field renamed, no key changed. One tier: Procedural Blank Level C N/A -> Advanced.
  * Module_ICPMS — Within-Session Precision, Analytical Accuracy (overlap sentence), Between-Session
    Precision (no dataset sentence: no single dataset holds its analyses).
  * Module_CompositionQC — Detection Limit: "procedure-typical or session-specific" becomes the
    two-level sentences; its per-analysis dataset sentence is kept.
  * Module_Blank — Procedural Blank Level: two-level sentences; C -> Advanced; Purpose default
    reworded, since no blank criterion field exists. Module_UPb's overlay Purpose follows it.
    Consumers' Purpose is consumer-owned, so it is rewritten in each source.
  * TAPP-owned — Analytical Precision and Analytical Accuracy (EPMA, SEM, SEM_Composition); EDS and
    EELS Detection Limit (TEM).
The overlap sentence is written as ONE sentence (a semicolon, not a full stop), so 14.2's "one
sentence beginning `In the dataset:`" holds and the sentence collector takes it whole.
Literature cells are not re-read: all ~125 positive cells were read for the proposal's third draft
and hold methods, typical values or pointers to session tables, which the two-level fields accept.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-10-29"
WS  = "Within-Session Analytical Precision and Assessment Method"
AAM = "Analytical Accuracy and Assessment Method"
BS  = "Between-Session (Long-Term) Analytical Precision and Assessment Method"
DL, BL = "Detection Limit", "Procedural Blank Level"
AP, AA = "Analytical Precision", "Analytical Accuracy"
EDL, ELL = "EDS Detection Limit", "EELS Detection Limit"

OVERLAP = ("In the dataset: report the analyses of each secondary reference material, where they are included; "
           "the session value summarises them and must agree with them.")
WS_B = ("Precision of repeated measurements of a reference material within a single analytical session, and the "
        "method used to assess it. The assessment method specifies the reference material or standard measured, "
        "the number of replicates n, and the statistic reported (1s RSD, 2s RSD, 2SD, 2SE, 95% CI). For the "
        "procedure: the assessment method and the expected within-session precision. For the session: the "
        "precision achieved in this session, assessed by that method. Distinct from the internal precision of a "
        "single measurement, which derives from counting statistics over the cycles of that measurement rather "
        "than from repeated analyses. " + OVERLAP)
AAM_B = ("Offset between measured and accepted values for secondary reference materials, and the method used to "
         "assess it. Specify the reference material and the source of its accepted values, the number of analyses, "
         "and the quantities assessed. Express the offset in the form appropriate to what the procedure reports: "
         "percent relative bias for concentrations, or deviation in delta or ratio units for isotopic quantities. "
         "For the procedure: the assessment method, the accepted-value source and the expected offset. For the "
         "session: the offset found in this session, with any systematic bias and its likely cause. " + OVERLAP)
BS_B = ("Precision of measurements across multiple analytical sessions over weeks to months — long-term or "
        "intermediate precision — and the method used to assess it. Specify the reference material, the number of "
        "measurements and sessions, the time span covered, and the statistic reported. For the procedure: the "
        "assessment method and the long-term precision on record when the procedure is registered. For the "
        "session: the long-term precision as it stands at this session, including this session's results where "
        "they contribute.")
DL_B = ("Detection limit, one per reported concentration variable (one per target species, these being the same "
        "set), with its units. For the procedure: the typical detection limits. For the session: the limits "
        "achieved in this session, where they are determined for the session as a whole (for example, from the "
        "blanks of the run). The calculation method is recorded separately in Detection Limit Method. Record "
        "'N/A' where the procedure reports no concentrations. In the dataset: report the detection limit of each "
        "analysis, where the procedure computes one.")
BL_B = ("The level of the analytical blank and, where the reported quantity is a ratio, its composition, since a "
        "blank subtracted from a ratio biases the result unless its own composition is known. For the procedure: "
        "the typical or maximum blank expected. For the session: the blank measured in this session. Companion to "
        "the blank correction method.")
BL_J_OLD = ("Follows the criterion-versus-measurement split the library applies wherever a procedure sets a "
            "threshold and an analysis reports a value against it.")
BL_J = ("A blank that is large relative to the sample, or of unknown composition, biases every result it is "
        "subtracted from.")
AP_OLD = ("Precision of repeated measurements on the same or equivalent reference material, expressed as 1-sigma "
          "relative standard deviation (%). State whether the repeats were made within one session "
          "(repeatability) or across sessions (intermediate precision, in ISO 5725 terms). Include reference "
          "material name, number of analyses (n), and the measured value.")
AP_B = ("Precision of repeated measurements on the same or equivalent reference material, expressed as 1-sigma "
        "relative standard deviation (%). State whether the repeats were made within one session (repeatability) "
        "or across sessions (intermediate precision, in ISO 5725 terms), the reference material name and the "
        "number of analyses (n). For the procedure: the expected precision. For the session: the precision "
        "achieved in this session. " + OVERLAP)
AA_OLD = ("Offset between measured and accepted reference values for secondary standards, expressed as percent "
          "relative bias. Include reference material, reference value source, and the measured value.")
AA_B = ("Offset between measured and accepted reference values for secondary standards, expressed as percent "
        "relative bias, with the reference material and the source of its reference value. For the procedure: "
        "the expected offset. For the session: the offset found in this session. " + OVERLAP)
EDL_OLD = ("Estimated detection limits by EDS under this procedure's conditions, one per reported concentration "
           "variable (one per target species, these being the same set). Record 'N/A' where EDS is not listed in "
           "Spectroscopic Detector(s).")
EDL_B = ("Detection limits by EDS, one per reported concentration variable (one per target species, these being "
         "the same set). For the procedure: the estimated limits under this procedure's conditions. For the "
         "session: the limits achieved in this session, or 'Not determined'. Record 'N/A' where EDS is not listed "
         "in Spectroscopic Detector(s).")
ELL_OLD = ("Estimated detection limit or minimum detectable concentration, under this procedure, of each quantity "
           "determined by EELS. Record 'N/A' where EELS is not listed in Spectroscopic Detector(s).")
ELL_B = ("Detection limit or minimum detectable concentration of each quantity determined by EELS. For the "
         "procedure: the estimated limit under this procedure's conditions. For the session: the limit achieved "
         "in this session, or 'Not determined'. Record 'N/A' where EELS is not listed in Spectroscopic "
         "Detector(s).")
OWNED = {AP: (AP_OLD, AP_B), AA: (AA_OLD, AA_B), EDL: (EDL_OLD, EDL_B), ELL: (ELL_OLD, ELL_B)}
CHANGED = {WS, AAM, BS, DL, BL, AP, AA, EDL, ELL}
DECISION = {
    "ICPMS": ("2026-10-29 v{v}. Rule 14.1 amendment (analysis/Rule14_Amendment_Session_QC_2026-10-29.md). "
              "Within-Session Precision, Analytical Accuracy and Between-Session Precision state both levels under "
              "the 14.6 lead-ins: the procedure holds the method and the expected value, the session the value "
              "achieved. Within-Session and Accuracy end with the 14.5 overlap sentence; Between-Session has none, "
              "since no single dataset holds the analyses it is computed from. Tiers unchanged."),
    "CompositionQC": ("2026-10-29 v{v}. Rule 14.1 amendment. Detection Limit: 'state whether procedure-typical or "
                      "session-specific' becomes the 14.6 two-level sentences; the per-analysis dataset sentence "
                      "is kept. Tiers unchanged."),
    "Blank": ("2026-10-29 v{v}. Rule 14.1 amendment. Procedural Blank Level C N/A -> Advanced, so a procedure can "
              "register its expected blank; Column B states both levels under the 14.6 lead-ins. The Purpose "
              "default no longer cites a criterion-versus-measurement split: no blank criterion field exists, its "
              "companion Blank / Background Correction Method being a method. No overlap sentence: a blank is a "
              "measurement on neither a sample nor a reference material."),
    "UPb": ("2026-10-29 v{v}. Overlay Purpose for Procedural Blank Level follows Module_Blank v{blank}."),
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


def main(apply=False):
    mods = {m: os.path.join(MODULES, "Module_%s.csv" % m) for m in DECISION}
    M = {m: rows_of(p) for m, p in mods.items()}
    by = {m: {r[0]: r for r in rs[1:] if r} for m, rs in M.items()}
    h = M["ICPMS"][0]
    iB, iC, iU, iJ = (h.index(c) for c in ("Description", "Procedure-Level Tier", "Last Update", "Purpose"))
    for m, f in (("ICPMS", WS), ("ICPMS", AAM), ("ICPMS", BS), ("CompositionQC", DL), ("Blank", BL)):
        assert "For the procedure:" not in by[m][f][iB], "PREMISE: %s already done" % f
    assert by["Blank"][BL][iC] == "N/A" and by["Blank"][BL][iJ] == BL_J_OLD, "PREMISE: blank row"
    assert by["UPb"][BL][iJ] == BL_J_OLD, "PREMISE: UPb blank overlay"
    vers = {m: json.load(io.open(p[:-4] + ".json", encoding="utf-8"))["version"] for m, p in mods.items()}

    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    plan = []
    for e in reg["composed"]:
        src = rows_of(os.path.join(ROOT, e["tapp"]))
        hh = src[0]; sB = hh.index("Description")
        names = {r[0].strip(): r for r in src[1:] if r}
        owned = [f for f in OWNED if f in names]
        for f in owned:
            assert names[f][sB] == OWNED[f][0], "PREMISE: %s %s" % (e["tapp"], f)
        if BL in names:
            assert names[BL][hh.index("Purpose")] == BL_J_OLD, "PREMISE: %s blank Purpose" % e["tapp"]
        if any(m["name"] in DECISION for m in e["modules"]) or owned:
            new = re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])
            plan.append((e, e["tapp"], new))
            print("  %-36s -> %-36s %s" % (os.path.basename(e["tapp"]), os.path.basename(new),
                  ",".join(sorted(m["name"] for m in e["modules"] if m["name"] in DECISION) + owned)))
    print("\n  modules %s; %d consumers" % (", ".join("%s v%s->v%d" % (m, v, int(v) + 1) for m, v in vers.items()),
                                          len(plan)))
    assert len(plan) == 13, "expected 13 TAPPs, found %d" % len(plan)
    if not apply:
        print("\n(dry run — pass --apply to write)"); return 0

    # --- modules ----------------------------------------------------------------------------
    for m, f, b in (("ICPMS", WS, WS_B), ("ICPMS", AAM, AAM_B), ("ICPMS", BS, BS_B),
                    ("CompositionQC", DL, DL_B), ("Blank", BL, BL_B)):
        r = by[m][f]; r[iB], r[iU] = b, DATE
    r = by["Blank"][BL]; r[iC], r[iJ] = "Advanced", BL_J
    r = by["UPb"][BL]; r[iJ], r[iU] = BL_J, DATE
    newver = {m: str(int(v) + 1) for m, v in vers.items()}
    for m, p in mods.items():
        write(p, M[m])
        jp = p[:-4] + ".json"; d = json.load(io.open(jp, encoding="utf-8"))
        d["version"] = newver[m]
        d["decisions"].append(DECISION[m].format(v=newver[m], blank=newver["Blank"]))
        with io.open(jp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=4 if m == "Blank" else 2, ensure_ascii=False); fh.write("\n")

    # --- consumers ----------------------------------------------------------------------------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, rel, new in plan:
        np_ = os.path.join(ROOT, new)
        src = rows_of(os.path.join(ROOT, rel)); hh = src[0]
        sB, sJ, sU = hh.index("Description"), hh.index("Purpose"), hh.index("Last Update")
        for x in src[1:]:
            n = x[0].strip() if x else ""
            if n in OWNED:
                x[sB] = OWNED[n][1]
            if n == BL:
                x[sJ] = BL_J            # consumer-owned overlay: the module default fills only blanks
        write(np_, src)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        rr = rows_of(np_)
        for x in rr[1:]:
            n = x[0].strip() if x else ""
            if n in CHANGED:
                x[sU] = DATE
                assert x[sB].count("For the procedure:") == 1 and x[sB].count("For the session:") == 1, (new, n)
            if n == BL:
                assert x[hh.index("Procedure-Level Tier")] == "Advanced" and x[sJ] == BL_J, new
        write(np_, rr)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
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
                if m["name"] in newver:
                    m["version"] = newver[m["name"]]
    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
